"""Tests for scripts/check.py: the --soft policy of the quality gate (B-CI, ADR-0005) and the
resolution of the lint-imports console script (AF-05).

No real step (ruff, mypy, import-linter, pytest...) is ever executed here: the only subprocess
is the stand-in command that the gate runs when lint-imports is missing.
"""

from __future__ import annotations

import importlib
import io
import subprocess
import sys
import sysconfig
from pathlib import Path
from unittest.mock import create_autospec

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
check = importlib.import_module("check")

RUFF = check.STEP_KEYS["ruff"]
MYPY = check.STEP_KEYS["mypy"]
TESTS = check.STEP_KEYS["tests"]


class TestParseSoft:
    @pytest.mark.parametrize("text", ["", "   ", ",", " , "])
    def test_empty_input_tolerates_nothing(self, text: str) -> None:
        assert check.parse_soft(text) == set()

    def test_list_maps_keys_to_step_names(self) -> None:
        assert check.parse_soft("format,ruff,mypy") == {
            check.STEP_KEYS["format"],
            RUFF,
            MYPY,
        }

    def test_whitespace_and_duplicates_are_ignored(self) -> None:
        assert check.parse_soft(" ruff , mypy,ruff ") == {RUFF, MYPY}

    def test_every_documented_key_is_accepted(self) -> None:
        keys = ["format", "ruff", "mypy", "imports", "docs", "tests"]
        assert list(check.STEP_KEYS) == keys
        assert len(check.parse_soft(",".join(keys))) == len(keys)

    def test_unknown_key_raises_and_names_the_offender(self) -> None:
        with pytest.raises(ValueError, match="mpyy"):
            check.parse_soft("ruff,mpyy")

    def test_step_name_is_not_a_valid_key(self) -> None:
        # Keys are the short fixed ones; the printed step names are not an alias.
        with pytest.raises(ValueError):
            check.parse_soft("ruff check")


class TestVerdict:
    def test_all_green_returns_zero_and_no_tolerated(self) -> None:
        assert check.verdict({RUFF: True, MYPY: True}, set()) == (0, [])

    def test_red_without_soft_blocks(self) -> None:
        assert check.verdict({RUFF: False, MYPY: True}, set()) == (1, [])

    def test_red_only_in_soft_passes_and_is_listed(self) -> None:
        results = {RUFF: False, MYPY: False, TESTS: True}
        assert check.verdict(results, {RUFF, MYPY}) == (0, [RUFF, MYPY])

    def test_red_outside_soft_blocks_even_if_another_red_is_tolerated(self) -> None:
        results = {RUFF: False, MYPY: True, TESTS: False}
        code, tolerated = check.verdict(results, {RUFF})
        assert code == 1
        assert tolerated == [RUFF]

    def test_soft_step_that_passes_is_not_reported_as_tolerated(self) -> None:
        assert check.verdict({RUFF: True, MYPY: False}, {RUFF, MYPY}) == (0, [MYPY])

    def test_tolerated_keeps_execution_order(self) -> None:
        results = {MYPY: False, RUFF: False}
        assert check.verdict(results, {RUFF, MYPY})[1] == [MYPY, RUFF]


class TestSoftArg:
    def test_absent_returns_none(self) -> None:
        assert check._soft_arg(["--fix", "--no-tests"]) is None

    def test_space_form(self) -> None:
        assert check._soft_arg(["--soft", "ruff,mypy", "--fix"]) == "ruff,mypy"

    def test_equals_form(self) -> None:
        assert check._soft_arg(["--soft=ruff,mypy"]) == "ruff,mypy"

    @pytest.mark.parametrize("argv", [["--soft"], ["--soft", "--fix"]])
    def test_missing_value_raises(self, argv: list[str]) -> None:
        with pytest.raises(ValueError):
            check._soft_arg(argv)


class TestImportHasNoSideEffects:
    def test_import_keeps_cwd_and_streams(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        fake_out = create_autospec(io.TextIOWrapper, instance=True)
        fake_err = create_autospec(io.TextIOWrapper, instance=True)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "stdout", fake_out)
        monkeypatch.setattr(sys, "stderr", fake_err)

        importlib.reload(check)

        assert Path.cwd() == tmp_path
        fake_out.reconfigure.assert_not_called()
        fake_err.reconfigure.assert_not_called()


class TestMainRejectsBadSoft:
    """main() validates --soft before running any step, so these never spawn a process."""

    def test_main_pins_cwd_to_repo_root(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert check.main(["--soft", "nope"]) == 2
        assert Path.cwd() == check.REPO_ROOT

    def test_unknown_key_exits_2_with_message_on_stderr(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert check.main(["--soft", "nope"]) == 2
        captured = capsys.readouterr()
        assert "nope" in captured.err
        assert captured.out == ""

    def test_missing_value_exits_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check.main(["--soft"]) == 2
        assert capsys.readouterr().out == ""


class TestLintImportsResolution:
    """The import-linter step runs the interpreter's own console script, or fails loudly."""

    BIN = Path("/fake/bin")

    def test_step_resolves_from_scripts_dir_regardless_of_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        with_path = dict(check.steps(no_tests=True))["import-linter"]
        # A PATH without the venv: the scenario of AF-05 (venv invoked by path, not activated).
        monkeypatch.setenv("PATH", str(tmp_path))
        without_path = dict(check.steps(no_tests=True))["import-linter"]

        assert "importlinter.cli" not in without_path
        assert without_path[1:2] != ["-m"]
        assert without_path == with_path
        assert without_path == check._lint_imports_cmd(Path(sysconfig.get_path("scripts")))

    @pytest.mark.parametrize("name", ["lint-imports.exe", "lint-imports"], ids=["windows", "posix"])
    def test_finds_console_script_in_scripts_dir(self, name: str) -> None:
        assert check.find_lint_imports(self.BIN, lambda p: p == self.BIN / name) == self.BIN / name

    def test_looks_only_inside_the_scripts_dir(self) -> None:
        seen: list[Path] = []

        def is_file(path: Path) -> bool:
            seen.append(path)
            return False

        assert check.find_lint_imports(self.BIN, is_file) is None
        assert seen == [self.BIN / "lint-imports.exe", self.BIN / "lint-imports"]

    def test_found_tool_is_invoked_directly(self) -> None:
        cmd = check._lint_imports_cmd(self.BIN, lambda p: p.name == "lint-imports")
        assert cmd == [str(self.BIN / "lint-imports")]

    def test_missing_tool_yields_failing_command_with_install_hint(self, tmp_path: Path) -> None:
        cmd = check._lint_imports_cmd(tmp_path)

        assert cmd[:2] == [check.PY, "-c"]
        assert "importlinter.cli" not in " ".join(cmd)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert result.stdout == ""
        assert str(tmp_path) in result.stderr
        assert "-m pip install -e .[dev]" in result.stderr

    def test_missing_tool_makes_the_gate_step_red(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        assert check.run("import-linter", check._lint_imports_cmd(tmp_path)) is False
        assert str(tmp_path) in capfd.readouterr().err

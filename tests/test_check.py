"""Tests for scripts/check.py: the --soft policy of the quality gate (B-CI, ADR-0005), how the
import-linter step is built (AF-05, AF-12) and how a step that cannot start is reported (AF-13).

No real step (ruff, mypy, import-linter, pytest...) checks anything here. The only subprocesses
are the stand-in command for a missing import-linter, the entry point under ``-S``, which fails
at import before checking anything, and trivial ``-c`` commands for run() and main().
"""

from __future__ import annotations

import importlib
import io
import subprocess
import sys
from importlib.metadata import entry_points
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


class TestLintImportsStep:
    """The import-linter step runs the tool's entry point in this interpreter, or fails loudly."""

    def test_step_is_the_entry_point_regardless_of_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        with_path = dict(check.steps(no_tests=True))["import-linter"]
        # A PATH without the venv: the scenario of AF-05 (venv invoked by path, not activated).
        monkeypatch.setenv("PATH", str(tmp_path))
        without_path = dict(check.steps(no_tests=True))["import-linter"]

        assert without_path == [check.PY, "-c", check.LINT_IMPORTS_CODE]
        assert "importlinter.cli" in without_path[2]
        assert without_path == with_path

    def test_code_calls_the_registered_console_script(self) -> None:
        (script,) = entry_points(group="console_scripts", name="lint-imports")

        assert (
            f"from {script.module} import {script.attr}; {script.attr}()" == check.LINT_IMPORTS_CODE
        )

    def test_missing_package_yields_failing_command_with_install_hint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        asked: list[str] = []

        def no_spec(name: str) -> None:
            asked.append(name)
            return None

        monkeypatch.setattr(check, "find_spec", no_spec)

        cmd = check._lint_imports_cmd()

        assert asked == ["importlinter"]
        assert cmd[:2] == [check.PY, "-c"]
        assert check.LINT_IMPORTS_CODE not in cmd
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert result.stdout == ""
        assert check.PY in result.stderr
        assert "-m pip install -e .[dev]" in result.stderr

    def test_missing_package_makes_the_gate_step_red(
        self, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(check, "find_spec", lambda name: None)
        cmd = dict(check.steps(no_tests=True))["import-linter"]

        assert check.run("import-linter", cmd) is False
        assert "-m pip install -e .[dev]" in capfd.readouterr().err

    def test_entry_point_without_the_package_on_sys_path_is_red(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        cmd = check._lint_imports_cmd()
        # -S skips site-packages: importable when the command is built, not when it runs.
        no_site = [cmd[0], "-S", *cmd[1:]]

        assert "importlinter.cli" in cmd[2]
        assert check.run("import-linter", no_site) is False
        err = capfd.readouterr().err
        assert "ModuleNotFoundError" in err
        assert "importlinter" in err


class TestRunReportsUnstartableStep:
    """A step whose command cannot start is a red step, not a crash of the gate (AF-13)."""

    def test_unstartable_command_is_a_red_step(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        missing = tmp_path / "no-such-tool"

        assert check.run("x", [str(missing)]) is False
        out, err = capfd.readouterr()
        assert any(
            line.startswith("--- x: ") and "(FileNotFoundError)" in line
            for line in out.splitlines()
        )
        assert str(missing) in err

    def test_main_runs_later_steps_and_prints_summary(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # main() pins the cwd to the repo root; chdir through monkeypatch so it is restored.
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            check,
            "steps",
            lambda no_tests: [
                ("unstartable", [str(tmp_path / "no-such-tool")]),
                ("after", [check.PY, "-c", "pass"]),
            ],
        )

        assert check.main([]) == 1
        out = capfd.readouterr().out
        assert "=== after ===" in out
        assert "✘ unstartable" in out
        assert "✔ after" in out

    def test_command_that_runs_and_fails_reports_its_exit_code(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        assert check.run("x", [check.PY, "-c", "import sys; sys.exit(3)"]) is False
        assert "(exit 3)" in capfd.readouterr().out

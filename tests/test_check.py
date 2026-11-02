"""Tests for scripts/check.py: the --soft policy of the quality gate (B-CI, ADR-0005).

Only the pure functions are exercised; no step (ruff, mypy, pytest...) is ever executed here.
"""

from __future__ import annotations

import importlib
import io
import sys
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

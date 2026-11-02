"""Tests for scripts/check_docs.py (docs coherence gate, ADR-0008)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
check_docs = importlib.import_module("check_docs")

_DEFAULT_FILES = {
    "docs/PLAN.md": (
        "# Plan\n\n## 2b. Bloques\n\n| Bloque | Qué |\n|---|---|\n"
        "| `B-FUTURO` | Lo que sale |\n| `B-HIGIENE` | Limpieza |\n\n## 3. Cronograma\n\n"
        "| Día | Qué |\n|---|---|\n| Lun 2 | algo |\n"
    ),
    "docs/CONTEXT.md": (
        "# Context\n\n## 2. Entrega\n\n| Hito | Fecha |\n|---|---|\n"
        "| **Deadline** | **11 de enero de 2027** |\n"
    ),
    "docs/backlog.md": (
        "# Backlog\n\n| ID | Título | Decisión |\n|---|---|---|\n"
        "| BE-01 | algo | **Entra · `B-HIGIENE`** |\n"
    ),
    "docs/sesiones/README.md": (
        "# Sesiones\n\n| Comando | Qué |\n|---|---|\n| `/foo` | hace foo |\n"
    ),
    ".claude/commands/foo.md": "foo\n",
}


def make_repo(tmp_path: Path, files: dict[str, str] | None = None) -> Path:
    """Write a minimal valid docs tree under tmp_path; `files` overrides or adds paths."""
    merged = {**_DEFAULT_FILES, **(files or {})}
    for rel, content in merged.items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return tmp_path


def test_unknown_flag_exits_2() -> None:
    with pytest.raises(SystemExit) as exc:
        check_docs.main(["--inexistente"])
    assert exc.value.code == 2
    with pytest.raises(SystemExit) as exc:
        check_docs.main(["--copias"])
    assert exc.value.code == 2


def test_sections_numbers_and_bounds() -> None:
    text = "## 0. A\nx\n## 2. B\n## 2b. C\n### sub\ny\n## 3. D\nz\nw"
    secs = check_docs.sections(text)
    assert [s.num for s in secs] == ["0", "2", "2b", "3"]
    sec_2b = secs[2]
    assert sec_2b.start <= 5 <= sec_2b.end  # the "### sub" line (5) belongs to 2b
    assert secs[-1].end == len(text.splitlines())


def test_lines_outside_and_inside_section_3(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/PLAN.md": "a\n## 2. X\nb\n## 3. Y\nc\nd\n## 4. Z\ne\n"})
    inside = check_docs.lines_inside(root, "docs/PLAN.md", {"3"})
    outside = check_docs.lines_outside(root, "docs/PLAN.md", {"3"})
    assert [n for n, _ in inside] == [4, 5, 6]
    assert [n for n, _ in outside] == [1, 2, 3, 7, 8]
    assert dict(inside)[5] == "c"


_CITATIONS = [
    "(CONTEXT §2)",
    "(PLAN §3)",
    "(backlog BE-01)",
    "(ADR-0008)",
    "(AGENTS §5)",
    "(README de sesiones)",
    "(bitácora 2026-10-29)",
    "(docs/deuda/AF-01/)",
]


@pytest.mark.parametrize("backticks", [False, True])
@pytest.mark.parametrize("cite", _CITATIONS)
def test_strip_citations(cite: str, backticks: bool) -> None:
    wrapped = f"`{cite}`" if backticks else cite
    assert check_docs.strip_citations(f"dato {wrapped} fin") == "dato  fin"


@pytest.mark.parametrize("text", ["dato (ver arriba) fin", "dato (bitácora ayer) fin"])
def test_strip_citations_keeps_non_citations(text: str) -> None:
    assert check_docs.strip_citations(text) == text


def test_rule_commands_both_directions(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path,
        {
            ".claude/commands/orphan.md": "x\n",
            "docs/sesiones/README.md": "| `/foo` | a |\n| `/bar` | b |\n",
        },
    )
    errors: list[str] = []
    check_docs.rule_commands(root, errors)
    assert len(errors) == 2
    assert all("R1" in e for e in errors)
    assert any("orphan" in e for e in errors)
    assert any("bar" in e for e in errors)


def test_main_on_fixture_root_is_green(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    assert check_docs.main(["--root", str(root)]) == 0


def test_main_on_fixture_with_error_returns_1(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {".claude/commands/orphan.md": "x\n"})
    assert check_docs.main(["--root", str(root)]) == 1


def test_estado_accepts_root(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/deuda/X/plan.md": "plan\n"})
    assert check_docs.main(["--estado", "--root", str(root)]) == 0


def test_repo_is_green() -> None:
    assert check_docs.main(["--root", str(ROOT)]) == 0

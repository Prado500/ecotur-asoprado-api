"""Tests for scripts/check_docs.py (docs coherence gate, ADR-0008)."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from unittest.mock import call, create_autospec

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


def _run(rule: Callable[[Path, list[str]], None], root: Path) -> list[str]:
    errors: list[str] = []
    rule(root, errors)
    return errors


# --- R2: schedule dates outside PLAN §3 ------------------------------------------------------

# Old CONTEXT §8 of 31 oct (`git show 2647ea3:docs/CONTEXT.md`, lines 238 and 253).
_OLD_CONTEXT_8 = (
    "# Context\n\n"
    "## 8. Próximo paso (sáb 31 oct, cierre)\n\n"
    "2. Lun 2 → vie 6: la semana fechada en PLAN §3 (`B-FORMATO`+`B-CI` → `B-HIGIENE` 1 m → "
    "`B-S1` → `B-TESTS` → cierre de\n"
)


@pytest.mark.parametrize(
    ("files", "locations"),
    [
        (
            {"docs/backlog.md": "# Backlog\n\nCorte el jueves 29 a las 18:00\n"},
            ["docs/backlog.md:3:"],
        ),
        ({"docs/CONTEXT.md": _OLD_CONTEXT_8}, ["docs/CONTEXT.md:3:", "docs/CONTEXT.md:5:"]),
        ({"docs/sesiones/x.md": "# X\nEl día 11 se cierra.\n"}, ["docs/sesiones/x.md:2:"]),
        ({"docs/PLAN.md": "# Plan\n\n| Lun 2 | fuera de la sección 3 |\n"}, ["docs/PLAN.md:3:"]),
    ],
    ids=["backlog-weekday", "context-old-section-8", "sesiones-dia", "plan-outside-3"],
)
def test_r2_flags_schedule_dates(
    tmp_path: Path, files: dict[str, str], locations: list[str]
) -> None:
    errors = _run(check_docs.rule_no_schedule_days, make_repo(tmp_path, files))
    assert len(errors) == len(locations)
    assert all(": R2: " in e for e in errors)
    for loc in locations:
        assert any(e.startswith(loc) for e in errors)


@pytest.mark.parametrize(
    "line",
    [
        "Capacidad: sáb 7 h o menos, dom descanso.",
        "Tope: 15 de diciembre.",
        "Medido el 24 oct, e4fd14d.",
        "reunión lun 17:00–18:00",
        "(bitácora 2026-10-29)",
        "`(bitácora 2026-10-29)` y nada más",
        "dom 90 % de avance",
        "sáb 7 horas o menos",
        "Dom 4 m de trabajo",
    ],
)
def test_r2_accepts_non_schedule_lines(tmp_path: Path, line: str) -> None:
    root = make_repo(tmp_path, {"docs/CONTEXT.md": f"# Context\n\n{line}\n"})
    assert _run(check_docs.rule_no_schedule_days, root) == []


def test_r2_accepts_weekday_rows_inside_plan_section_3(tmp_path: Path) -> None:
    root = make_repo(tmp_path)  # default PLAN has `| Lun 2 | algo |` under `## 3.`
    assert _run(check_docs.rule_no_schedule_days, root) == []


# --- R3: blocks, now also in docs/sesiones -------------------------------------------------


def test_r3_flags_undefined_block_in_sesiones(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/sesiones/mentor.md": "# Mentor\nVer `B-INEXISTENTE`.\n"})
    errors = _run(check_docs.rule_blocks, root)
    assert len(errors) == 1
    assert errors[0].startswith("docs/sesiones/mentor.md:2: R3: ")
    assert "B-INEXISTENTE" in errors[0]


def test_r3_accepts_defined_block_in_sesiones(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/sesiones/mentor.md": "# Mentor\nVer `B-HIGIENE`.\n"})
    assert _run(check_docs.rule_blocks, root) == []


# --- R4: one block, one qualifier without blocks or vocabulary ----------------------------


def _backlog_with_decision(cell: str) -> dict[str, str]:
    return {
        "docs/backlog.md": (
            f"# Backlog\n\n| ID | Título | Decisión |\n|---|---|---|\n| BE-99 | algo | {cell} |\n"
        )
    }


@pytest.mark.parametrize(
    "cell",
    [
        "**Entra · `B-ORDEN` (backend) y `B-FE-RESERVAS` (cliente)**",  # BE-08, 30 oct
        "**Decidir en `B-HIGIENE` (verificar lo que existe; luego `B-FUTURO`)**",  # BE-09, 31 oct
        "**Entra · `B-PAGOS` (mitigación en `B-FE-LISTA`)**",
        "**Entra · `B-X` (a) (b)**",
        "**Hecho**",
        "**Hecho (ADR-0003; re-verificación en `B-TESTS`)**",
        "Entra · `B-X`",
        "**Entra · `B-X` (Sale)**",
        "**Entra · `B-X` (Hecho parcialmente)**",
    ],
)
def test_r4_rejects_decisions_outside_vocabulary(tmp_path: Path, cell: str) -> None:
    errors = _run(check_docs.rule_decisions, make_repo(tmp_path, _backlog_with_decision(cell)))
    assert len(errors) == 1
    assert errors[0].startswith("docs/backlog.md:5: R4: ")


@pytest.mark.parametrize(
    "cell",
    [
        "**Entra · `B-RESERVAS` (mínimo)**",
        "**Entra · `B-FE-LISTA` (parcial: solo la señal visual)**",
        "**Entra · `B-PAGOS` (solo ADR; código si cabe)**",
        "**Sale → `B-FUTURO`**",
        "**Sale → `B-FUTURO` (con nota legal)**",
        "**Entra · `B-HIGIENE` (`detalle`→`detail`)**",
        "**Hecho (PR #61, 27 oct; ADR-0006)**",
        "**Decidir en `B-HIGIENE`**",
    ],
)
def test_r4_accepts_vocabulary(tmp_path: Path, cell: str) -> None:
    root = make_repo(tmp_path, _backlog_with_decision(cell))
    assert _run(check_docs.rule_decisions, root) == []


def test_r4_decision_re_rejects_two_blocks() -> None:
    cell = "**Entra · `B-ORDEN` (backend) y `B-FE-RESERVAS` (cliente)**"
    assert check_docs.DECISION_RE.match(cell) is None


# --- R5: delivery date equals CONTEXT §2 and carries its citation -------------------------

# Row AF-01 of docs/backlog.md on 1 nov, copied verbatim: trigger and dates > 40 chars apart.
_BACKLOG_AF01_ROW = (
    "| AF-01 | ADR-0008 y addendum (29–30 oct); hallazgo del 31 oct | Reglas de ADR-0008 en "
    "`scripts/check_docs.py`: días fuera de PLAN §3 (también dentro de PLAN); fecha de entrega en "
    "PLAN igual a CONTEXT §2; bloque citado existe en §2b; encabezado de versión según ADR-0007; "
    "fila de PLAN §3 cerrada sin marca; `--copias` lista citas por dueño; copia de hecho duro sin "
    "cita como hallazgo; la columna Decisión nombra exactamente un bloque y nada más (hoy "
    "`DECISION_RE` deja pasar cualquier cola, por eso BE-08 estuvo en dos bloques) | Media | "
    "**Entra · `B-CHECK-DOCS`** | Casos de prueba para la regla de la Decisión: FE-05 "
    "(`parcial`), BE-18 (`mínimo`) y BE-14 (`Sale` con mitigación en otro bloque); se decide con "
    "el script delante si se admite un calificador cerrado entre paréntesis. Especificación a dos "
    "manos antes de Claude Code. |"
)


@pytest.mark.parametrize(
    ("rel", "line", "mismatch"),
    [
        ("docs/PLAN.md", "Fecha de entrega del 7 de noviembre.", True),
        ("docs/backlog.md", "La entrega el 11 ene.", False),
        ("docs/PLAN.md", "- **Lun 11 nov — entrega en línea** `(CONTEXT §2)`.", True),
        ("docs/sesiones/x.md", "entrega el 11 de enero de 2026 (CONTEXT §2)", True),
    ],
    ids=["other-date", "no-citation", "date-before-trigger", "other-year"],
)
def test_r5_flags_wrong_or_uncited_delivery_date(
    tmp_path: Path, rel: str, line: str, mismatch: bool
) -> None:
    root = make_repo(tmp_path, {rel: f"# Doc\n\n{line}\n"})
    errors = _run(check_docs.rule_deadline, root)
    assert len(errors) == 1
    assert errors[0].startswith(f"{rel}:3: R5: ")
    assert ("≠" in errors[0]) is mismatch


@pytest.mark.parametrize(
    "line",
    [
        "- **Lun 11 ene — entrega en línea** `(CONTEXT §2)`. El domingo anterior es margen.",
        "| `B-TESIS` | Capítulos; integración con María Paula; entrega | El documento |",
        "`B-TESIS` 22); **colchón 1** más el domingo anterior a la entrega. Orden: `B-QA` →",
        "corte de código el 18 dic y entrega el 11 ene `(CONTEXT §2)`",
        "entrega 2027-01-11 (CONTEXT §2)",
        _BACKLOG_AF01_ROW,
    ],
    ids=["plan-milestone", "no-date", "colchon-1", "nearest-date", "iso", "backlog-af01-row"],
)
def test_r5_accepts_matching_cited_or_unevaluated_lines(tmp_path: Path, line: str) -> None:
    root = make_repo(tmp_path, {"docs/PLAN.md": f"# Plan\n\n{line}\n"})
    assert _run(check_docs.rule_deadline, root) == []


def test_r5_reports_unreadable_deadline_once(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path,
        {
            "docs/CONTEXT.md": "# Context\n\n## 2. Entrega\n\nSin fila.\n",
            "docs/PLAN.md": "# Plan\n\nentrega el 7 de noviembre\n",
        },
    )
    errors = _run(check_docs.rule_deadline, root)
    assert len(errors) == 1
    assert errors[0].startswith("docs/CONTEXT.md")
    assert ": R5: " in errors[0]


# --- main wires R1-R5 ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("files", "rule_id"),
    [
        ({"docs/sesiones/x.md": "El día 11.\n"}, "R2"),
        ({"docs/sesiones/x.md": "`B-INEXISTENTE`\n"}, "R3"),
        (_backlog_with_decision("**Entra · `B-HIGIENE` (a) (b)**"), "R4"),
        ({"docs/sesiones/x.md": "entrega el 7 de noviembre\n"}, "R5"),
    ],
)
def test_main_fails_on_each_new_rule(
    tmp_path: Path, files: dict[str, str], rule_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert check_docs.main(["--root", str(make_repo(tmp_path, files))]) == 1
    out = capsys.readouterr().out
    assert out.count(f": {rule_id}: ") == 1
    others = {"R1", "R2", "R3", "R4", "R5"} - {rule_id}
    assert not any(f": {r}: " in out for r in others)


# --- informative commands: mutually exclusive, never part of the blocking pass ------------


@pytest.mark.parametrize(
    "argv",
    [
        ["--estado", "--huerfanas"],
        ["--copias", "--estado"],
        ["--huerfanas", "--copias", "X"],
        ["--cierre", "--estado"],
        ["--huerfanas", "--cierre"],
    ],
)
def test_informative_flags_are_mutually_exclusive(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        check_docs.main(argv)
    assert exc.value.code == 2


# --- R8: --copias lists fixed-form citations per owner ------------------------------------

_CITATIONS_REPO = {
    "docs/backlog.md": "# Backlog\n\nHito (CONTEXT §2).\n",
    "docs/sesiones/x.md": "# X\nVer `(PLAN §3)`.\nY (ADR-0008).\n",
}


def _location_and_citation(entry: str) -> str:
    return entry.split(' "', 1)[0]


def test_copias_lists_all_and_filters(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_repo(tmp_path, _CITATIONS_REPO)
    everything = check_docs.list_citations(root, "")
    assert [_location_and_citation(e) for e in everything] == [
        "docs/backlog.md:3: (CONTEXT §2):",
        "docs/sesiones/x.md:2: (PLAN §3):",
        "docs/sesiones/x.md:3: (ADR-0008):",
    ]
    filtered = check_docs.list_citations(root, "CONTEXT §2")
    assert [_location_and_citation(e) for e in filtered] == ["docs/backlog.md:3: (CONTEXT §2):"]

    assert check_docs.main(["--copias", "--root", str(root)]) == 0
    assert capsys.readouterr().out.splitlines() == everything
    assert check_docs.main(["--copias", "CONTEXT §2", "--root", str(root)]) == 0
    assert capsys.readouterr().out.splitlines() == filtered


def test_copias_lists_every_citation_of_a_line_in_order(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/sesiones/x.md": "a (ADR-0008) b `(backlog BE-01)` c\n"})
    entries = check_docs.list_citations(root, "")
    assert [_location_and_citation(e) for e in entries] == [
        "docs/sesiones/x.md:1: (ADR-0008):",
        "docs/sesiones/x.md:1: (backlog BE-01):",
    ]


def test_copias_ignores_out_of_scope(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {**_CITATIONS_REPO, "docs/adr/x.md": "Dato (CONTEXT §2).\n"})
    entries = check_docs.list_citations(root, "")
    assert len(entries) == 3
    assert not any(e.startswith("docs/adr/") for e in entries)


def test_copias_with_unknown_owner_lists_nothing(tmp_path: Path) -> None:
    root = make_repo(tmp_path, _CITATIONS_REPO)
    assert check_docs.list_citations(root, "AGENTS") == []


# --- R9: --huerfanas lists candidate hard facts without a citation ------------------------


def test_huerfanas_reports_uncited_fact_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(
        tmp_path,
        {
            "docs/sesiones/x.md": (
                "# X\ncobertura 93 %\n93 % (PLAN §6)\n**Versión 1.0 — 1 nov 2026.**\n"
            ),
            "docs/PLAN.md": _DEFAULT_FILES["docs/PLAN.md"] + "\n## 6. Métricas\n\n93 %\n",
            "docs/adr/x.md": "cobertura 93 %\n",
        },
    )
    orphans = check_docs.list_orphans(root)
    assert len(orphans) == 1
    assert orphans[0].startswith("docs/sesiones/x.md:2: ")
    assert '"93 %"' in orphans[0]

    assert check_docs.main(["--huerfanas", "--root", str(root)]) == 0
    assert capsys.readouterr().out.splitlines() == orphans


@pytest.mark.parametrize(
    ("line", "fragment"),
    [
        ("Medido el 24 oct.", "24 oct"),
        ("Suite de 219 tests.", "219 tests"),
        ("Capacidad de 7 h.", "7 h"),
        ("Bloque de 1 m.", "1 m"),
        ("Avance 90 %, luego 4 m.", "90 %"),
    ],
)
def test_huerfanas_patterns_report_first_fragment(tmp_path: Path, line: str, fragment: str) -> None:
    root = make_repo(tmp_path, {"docs/backlog.md": f"# Backlog\n\n{line}\n"})
    orphans = check_docs.list_orphans(root)
    assert len(orphans) == 1
    assert orphans[0].startswith("docs/backlog.md:3: ")
    assert f'"{fragment}"' in orphans[0]


@pytest.mark.parametrize(
    ("rel", "num"),
    [
        ("docs/CONTEXT.md", "0"),
        ("docs/CONTEXT.md", "2"),
        ("docs/CONTEXT.md", "4"),
        ("docs/CONTEXT.md", "6"),
        ("docs/PLAN.md", "3"),
        ("docs/PLAN.md", "6"),
        ("docs/PLAN.md", "7"),
    ],
)
def test_huerfanas_skips_owner_sections(tmp_path: Path, rel: str, num: str) -> None:
    content = f"# Doc\n\n## {num}. Dueño\n\ncobertura 93 %\n\n## 9. Otra\n\nnada\n"
    root = make_repo(tmp_path, {rel: content})
    assert check_docs.list_orphans(root) == []


def test_huerfanas_reports_non_owner_section(tmp_path: Path) -> None:
    content = "# Doc\n\n## 2. Dueño\n\n93 %\n\n## 8. Próximo paso\n\ncobertura 93 %\n"
    root = make_repo(tmp_path, {"docs/CONTEXT.md": content})
    orphans = check_docs.list_orphans(root)
    assert len(orphans) == 1
    assert orphans[0].startswith("docs/CONTEXT.md:9: ")


# --- --estado: progress.json parsed as JSON ------------------------------------------------


def _progress(target: str | None, statuses: list[str]) -> str:
    phases = {f"Fase_{chr(65 + i)}": {"status": s, "commit": None} for i, s in enumerate(statuses)}
    return json.dumps({"current_target": target, "phases": phases})


def _estado_line(root: Path, item: str, capsys: pytest.CaptureFixture[str]) -> str:
    assert check_docs.main(["--estado", "--root", str(root)]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith(f"{item}:")]
    assert len(lines) == 1
    return lines[0]


def test_estado_all_completed_and_null_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rel = "docs/deuda/X/progress.json"
    root = make_repo(tmp_path, {rel: _progress(None, ["completed", "completed"])})
    assert check_docs.read_progress(root / rel) == check_docs.Progress("done", None)
    line = _estado_line(root, "X", capsys)
    assert "?" not in line
    assert check_docs.STATE_DONE in line
    assert check_docs.STATE_UNREADABLE not in line


def test_estado_in_progress(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rel = "docs/deuda/X/progress.json"
    root = make_repo(tmp_path, {rel: _progress("Fase_B", ["completed", "pending"])})
    assert check_docs.read_progress(root / rel) == check_docs.Progress("running", "Fase_B")
    line = _estado_line(root, "X", capsys)
    assert "Fase_B" in line
    assert check_docs.STATE_RUNNING.format(target="Fase_B") in line


def test_estado_non_utf8_progress_is_unreadable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(tmp_path)
    path = root / "docs/deuda/X/progress.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"current_target": "\xff"}')
    assert check_docs.read_progress(path) == check_docs.Progress("unreadable", None)
    line = _estado_line(root, "X", capsys)
    assert check_docs.STATE_UNREADABLE in line
    assert check_docs.STATE_DONE not in line


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (_progress(None, ["completed", "pending"]), ("running", None)),
        (_progress(None, []), ("running", None)),
        (_progress("Fase_A", ["completed"]), ("running", "Fase_A")),
        ("{not json", ("unreadable", None)),
        ("[1, 2]", ("unreadable", None)),
    ],
    ids=["null-target-unfinished", "null-target-no-phases", "target-set", "invalid", "not-object"],
)
def test_read_progress_edges(
    tmp_path: Path, content: str, expected: tuple[str, str | None]
) -> None:
    path = tmp_path / "progress.json"
    path.write_text(content, encoding="utf-8")
    assert check_docs.read_progress(path) == check_docs.Progress(*expected)


def test_estado_on_real_repo_be01(capsys: pytest.CaptureFixture[str]) -> None:
    progress = ROOT / "docs/deuda/BE-01/progress.json"
    assert check_docs.read_progress(progress) == check_docs.Progress("done", None)
    line = _estado_line(ROOT, "BE-01", capsys)
    assert "?" not in line
    assert check_docs.STATE_DONE in line
    assert check_docs.STATE_UNREADABLE not in line


# --- git helpers: real functions over a mocked process boundary (no process is spawned) ---


def _completed(returncode: int, stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (_completed(0, "2026-11-01\n"), date(2026, 11, 1)),
        (_completed(128, ""), None),
        (_completed(0, ""), None),
        (FileNotFoundError(), None),
    ],
    ids=["committed", "not-a-repo", "no-history", "git-missing"],
)
def test_git_last_commit_date(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: subprocess.CompletedProcess[str] | Exception,
    expected: date | None,
) -> None:
    run = create_autospec(subprocess.run, return_value=outcome)
    if isinstance(outcome, Exception):
        run.side_effect = outcome
    monkeypatch.setattr(subprocess, "run", run)
    assert check_docs.git_last_commit_date(tmp_path, "docs/PLAN.md") == expected
    run.assert_called_once_with(
        ["git", "log", "-1", "--format=%cs", "--", "docs/PLAN.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (_completed(0, " M docs/PLAN.md\n"), True),
        (_completed(0, ""), False),
        (_completed(128, ""), None),
        (FileNotFoundError(), None),
    ],
    ids=["modified", "clean", "not-a-repo", "git-missing"],
)
def test_git_is_dirty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: subprocess.CompletedProcess[str] | Exception,
    expected: bool | None,
) -> None:
    run = create_autospec(subprocess.run, return_value=outcome)
    if isinstance(outcome, Exception):
        run.side_effect = outcome
    monkeypatch.setattr(subprocess, "run", run)
    assert check_docs.git_is_dirty(tmp_path, "docs/PLAN.md") is expected
    run.assert_called_once_with(
        ["git", "status", "--porcelain", "--", "docs/PLAN.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


# --- R6 (--cierre): version line never older than the file's last commit (ADR-0007) -------

_BEFORE_ADR_0007 = date(2026, 10, 27)  # last commit of every file a test does not target


def _version_line(day_month_year: str) -> str:
    return f"> **Versión 2.0 — {day_month_year}.** Cambios de esta versión: x."


def _plan_with_version(day_month_year: str) -> str:
    return _DEFAULT_FILES["docs/PLAN.md"].replace(
        "# Plan\n\n", f"# Plan\n\n{_version_line(day_month_year)}\n\n", 1
    )


def _run_r6(
    root: Path, target: str, last: date | None, dirty: bool | None
) -> tuple[list[str], list[str]]:
    def last_commit_date(_root: Path, rel: str) -> date | None:
        return last if rel == target else _BEFORE_ADR_0007

    def is_dirty(_root: Path, rel: str) -> bool | None:
        return dirty if rel == target else False

    errors: list[str] = []
    warnings: list[str] = []
    check_docs.rule_version_header(
        root, errors, warnings, last_commit_date=last_commit_date, is_dirty=is_dirty
    )
    return errors, warnings


@pytest.mark.parametrize("dirty", [False, True])
def test_r6_flags_header_older_than_last_commit(tmp_path: Path, dirty: bool) -> None:
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_with_version("31 oct 2026")})
    errors, warnings = _run_r6(root, "docs/PLAN.md", date(2026, 11, 1), dirty)
    assert len(errors) == 1
    assert errors[0].startswith("docs/PLAN.md:3: R6: ")
    assert "2026-10-31" in errors[0]
    assert "2026-11-01" in errors[0]
    assert len(warnings) == int(dirty)
    for warning in warnings:
        assert warning.startswith("docs/PLAN.md: R6: ")
        assert check_docs.WARN_DIRTY in warning


@pytest.mark.parametrize(
    ("version", "last"),
    [(None, date(2026, 10, 31)), ("31 nov 2026", date(2026, 11, 1))],
    ids=["unversioned-after-adr-0007", "impossible-header-date"],
)
def test_r6_flags_file_without_valid_version_line(
    tmp_path: Path, version: str | None, last: date
) -> None:
    rel = "docs/sesiones/mentor.md"
    header = f"{_version_line(version)}\n\n" if version else ""
    root = make_repo(tmp_path, {rel: f"# Mentor\n\n{header}Prompt.\n"})
    errors, warnings = _run_r6(root, rel, last, False)
    assert len(errors) == 1
    assert errors[0].startswith(f"{rel}: R6: ")
    assert warnings == []


@pytest.mark.parametrize(
    ("version", "last", "dirty", "warning"),
    [
        ("1 nov 2026", date(2026, 11, 1), False, None),
        ("1 nov 2026", date(2026, 11, 1), True, "WARN_DIRTY"),
        ("1 nov 2026", date(2026, 10, 31), False, None),
        (None, date(2026, 10, 27), False, None),
        (None, date(2026, 10, 28), False, None),
        ("31 oct 2026", None, None, "WARN_UNVERIFIABLE"),
    ],
    ids=[
        "same-day",
        "same-day-dirty",
        "header-newer",
        "unversioned-before-adr-0007",
        "unversioned-on-adr-0007-day",
        "git-unavailable",
    ],
)
def test_r6_accepts_current_header_and_warns_without_failing(
    tmp_path: Path, version: str | None, last: date | None, dirty: bool | None, warning: str | None
) -> None:
    rel = "docs/sesiones/mentor.md"
    header = f"{_version_line(version)}\n\n" if version else ""
    root = make_repo(tmp_path, {rel: f"# Mentor\n\n{header}Prompt.\n"})
    errors, warnings = _run_r6(root, rel, last, dirty)
    assert errors == []
    if warning is None:
        assert warnings == []
    else:
        assert len(warnings) == 1
        assert warnings[0].startswith(f"{rel}: R6: ")
        assert getattr(check_docs, warning) in warnings[0]


def test_r6_asks_git_about_every_scope_file(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"docs/sesiones/mentor.md": "# Mentor\n"})
    last_commit_date = create_autospec(
        check_docs.git_last_commit_date, return_value=_BEFORE_ADR_0007
    )
    is_dirty = create_autospec(check_docs.git_is_dirty, return_value=False)
    errors: list[str] = []
    warnings: list[str] = []
    check_docs.rule_version_header(
        root, errors, warnings, last_commit_date=last_commit_date, is_dirty=is_dirty
    )
    expected = [call(root, rel) for rel in check_docs.scope_files(root)]
    assert len(expected) == 5  # CONTEXT, PLAN, backlog, sesiones/README and sesiones/mentor
    assert last_commit_date.call_args_list == expected
    assert is_dirty.call_args_list == expected
    assert errors == []
    assert warnings == []


# --- R7 (--cierre): rows of PLAN §3 dated before today carry a closing mark ---------------

# PLAN §3 tables of 1 nov, copied verbatim (`docs/PLAN.md`, lines 94-104 and 117-124).
_PLAN_CLOSED_DAYS_TABLE = (
    "| Día | Bloques planeados | Cierre |\n"
    "|---|---|---|\n"
    "| Vie 23 oct | Aprobación del plan, backlog, CONTEXT/PLAN; tooling y línea base "
    "| ✔ 23 |\n"
    "| Sáb 24 | Flujo agéntico v1; `B-BE01` | ◐ 24 |\n"
    "| Dom 25 | (media jornada) PR docs+tooling, ADR-0004, `/deuda-verificar BE-01` |"
    " ◐ 25 |\n"
    "| Lun 26 | `B-BE01`, `B-FORMATO`, `B-CI`, `B-HIGIENE` | ✘ 26 |\n"
    "| Mar 27 | `B-BE01`; `B-FORMATO`, `B-CI`, `B-S1` | ◐ 27 |\n"
    "| Mié 28 | `B-S1`, `B-TESTS`, `B-RESERVAS` (esquema) | ✘ 28 |\n"
    "| Jue 29 | `B-RESERVAS`, `B-PAGOS` | ✘ 29 |\n"
    "| Vie 30 | `B-PAGOS`, `B-ORDEN` | ✘ 30 |\n"
    "| Sáb 31 | PLAN 2.0; `B-CHECK-DOCS` | ◐ 31 |\n"
)

_PLAN_BOGOTA_TABLE = (
    "| Día | Mañana | Tarde | Cierre |\n"
    "|---|---|---|---|\n"
    "| Dom 1 nov | **Comodín (fuera del presupuesto):** `B-CHECK-DOCS m1`: especifica"
    "ción a dos manos, implementación por Claude Code, `/pr` | — | |\n"
    "| Lun 2 | `B-FORMATO`+`B-CI` m1 (dos PR propios). A primera hora: mensaje a Marí"
    "a Paula para fijar la reunión | `B-HIGIENE m1` (tope: 1 m; lo que no quepa → dec"
    "isión nueva en backlog hoy). **Hito: reunión con María Paula, 17:00–18:00, dentr"
    "o de esta media jornada**; si ella no puede, mar 3 a la misma hora (come una hor"
    "a de `B-S1 m2`); sus filas se escriben al cierre de ese día (PLAN 2.1) | |\n"
    "| Mar 3 | `B-S1 m1` | `B-S1 m2` | |\n"
    "| Mié 4 | `B-TESTS m1` | `B-TESTS m2` | |\n"
    "| Jue 5 | `B-TESTS m3` | `B-TESTS m4`: cierre; compuerta medida (verde → ADR-000"
    "5 superado). Si no cierra, el cierre de hoy lo declara deslizado y mueve la fila"
    "; no se arrastra en silencio | |\n"
    "| Vie 6 | **Colchón (1 m):** si no se gastó, `B-HIGIENE m2` devuelto | Cierre de"
    " Bogotá: PR `develop` → `staging` `[señal]`; dump de la base de staging para `B-"
    "RESERVAS m2`; preparar mudanza. **Fechar la semana siguiente (Prado)** | |\n"
)

_TABLE_HEAD = "| Día | Mañana | Cierre |\n|---|---|---|\n"


def _plan_section_3(tables: str, year: int = 2026) -> str:
    return (
        f"# Plan\n\n{_version_line(f'31 oct {year}')}\n\n## 2b. Bloques\n\n"
        "| Bloque | Qué |\n|---|---|\n| `B-FUTURO` | Lo que sale |\n| `B-HIGIENE` | Limpieza |\n\n"
        f"## 3. Cronograma\n\n{tables}\n## 4. Después\n\nnada\n"
    )


def _run_r7(root: Path, today: date) -> list[str]:
    errors: list[str] = []
    check_docs.rule_closed_days_marked(root, errors, today=lambda: today)
    return errors


@pytest.mark.parametrize(
    ("tables", "today", "row"),
    [
        (
            _TABLE_HEAD + "| Dom 1 nov | comodín | ✔ 1 |\n| Lun 2 | algo | |\n| Mar 3 | hoy | |\n",
            date(2026, 11, 3),
            "| Lun 2 | algo | |",
        ),
        (
            _TABLE_HEAD + "| Jue 31 dic | x | ✔ 31 |\n| Sáb 2 ene | y | |\n",
            date(2027, 1, 5),
            "| Sáb 2 ene | y | |",
        ),
        (
            _TABLE_HEAD
            + "| Jue 31 dic | x | ✔ 31 |\n| Vie 1 ene | y | ✔ 1 |\n\n### Otra\n\n"
            + _TABLE_HEAD
            + "| Lun 2 nov | z | |\n",
            date(2026, 11, 3),
            "| Lun 2 nov | z | |",
        ),
        (_TABLE_HEAD + "| Lun 2 nov | z |\n", date(2026, 11, 3), "| Lun 2 nov | z |"),
    ],
    ids=["past-row-unmarked", "year-by-monotony", "year-resets-per-table", "missing-cierre-cell"],
)
def test_r7_flags_closed_row_without_mark(
    tmp_path: Path, tables: str, today: date, row: str
) -> None:
    content = _plan_section_3(tables)
    root = make_repo(tmp_path, {"docs/PLAN.md": content})
    errors = _run_r7(root, today)
    assert len(errors) == 1
    assert errors[0].startswith(f"docs/PLAN.md:{content.splitlines().index(row) + 1}: R7: ")


@pytest.mark.parametrize(
    ("mark", "flagged"),
    [
        ("✔ 2", False),
        ("◐ 2", False),
        ("✘ 2", False),
        ("", True),
        ("—", True),
        ("✔", True),
        ("✔ 2 (bitácora)", True),
    ],
)
def test_r7_closing_mark_shape(tmp_path: Path, mark: str, flagged: bool) -> None:
    tables = _TABLE_HEAD + f"| Lun 2 nov | algo | {mark} |\n"
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_section_3(tables)})
    assert len(_run_r7(root, date(2026, 11, 3))) == int(flagged)


@pytest.mark.parametrize(
    ("tables", "today"),
    [
        (_PLAN_BOGOTA_TABLE, date(2026, 11, 1)),
        (_PLAN_CLOSED_DAYS_TABLE, date(2026, 11, 1)),
        (_TABLE_HEAD + "| Jue 31 dic | x | ✔ 31 |\n| Sáb 2 ene | y | ✔ 2 |\n", date(2026, 12, 31)),
        (_TABLE_HEAD + "| Jue 31 dic | x | ✔ 31 |\n| Sáb 2 ene | y | |\n", date(2026, 12, 31)),
        (_TABLE_HEAD + "| (se fecha el vie 6) | | |\n", date(2027, 6, 1)),
        (
            _TABLE_HEAD
            + "| Vie 30 oct | x | ✔ 30 |\n\n### Otra\n\n"
            + _TABLE_HEAD
            + "| Lun 2 | y | |\n",
            date(2026, 11, 3),
        ),
        ("| Día | Qué |\n|---|---|\n| Lun 2 nov | algo |\n", date(2027, 6, 1)),
    ],
    ids=[
        "bogota-table-today",
        "closed-days-table-today",
        "year-jump-marked",
        "year-jump-future-row",
        "unscheduled-row",
        "month-resets-per-table",
        "no-cierre-column",
    ],
)
def test_r7_accepts_marked_future_or_undated_rows(tmp_path: Path, tables: str, today: date) -> None:
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_section_3(tables)})
    assert _run_r7(root, today) == []


def test_r7_ignores_tables_outside_section_3(tmp_path: Path) -> None:
    content = _plan_section_3("nada\n").replace(
        "## 4. Después\n\nnada\n", "## 4. Después\n\n" + _TABLE_HEAD + "| Lun 2 nov | x | |\n"
    )
    root = make_repo(tmp_path, {"docs/PLAN.md": content})
    assert _run_r7(root, date(2027, 6, 1)) == []


def test_r7_without_plan_version_reports_once(tmp_path: Path) -> None:
    content = _plan_section_3(_TABLE_HEAD + "| Lun 2 nov | x | |\n| Mar 3 | y | |\n")
    content = content.replace(_version_line("31 oct 2026"), "Sin versión.")
    root = make_repo(tmp_path, {"docs/PLAN.md": content})
    errors = _run_r7(root, date(2027, 6, 1))
    assert len(errors) == 1
    assert errors[0].startswith("docs/PLAN.md: R7: ")


# --- --cierre wires R6-R7; the default pass never runs git nor reads the clock -------------


def test_default_pass_runs_no_git_and_no_closing_rules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = create_autospec(subprocess.run)
    monkeypatch.setattr(subprocess, "run", run)
    tables = _TABLE_HEAD + "| Lun 2 nov | algo | |\n"
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_section_3(tables, year=2025)})
    assert check_docs.main(["--root", str(root)]) == 0
    run.assert_not_called()
    out = capsys.readouterr().out
    assert ": R6: " not in out
    assert ": R7: " not in out


def test_cierre_flag_fails_on_unmarked_closed_day_and_keeps_warnings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = create_autospec(subprocess.run, side_effect=FileNotFoundError)
    monkeypatch.setattr(subprocess, "run", run)
    tables = _TABLE_HEAD + "| Lun 2 nov | algo | |\n"
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_section_3(tables, year=2025)})
    assert check_docs.main(["--cierre", "--root", str(root)]) == 1
    out = capsys.readouterr().out
    scope = check_docs.scope_files(root)
    assert out.count(": R7: ") == 1
    assert out.count(f": R6: {check_docs.WARN_UNVERIFIABLE}") == len(scope)
    assert run.call_count == 2 * len(scope)
    run.assert_any_call(
        ["git", "log", "-1", "--format=%cs", "--", "docs/PLAN.md"],
        cwd=root,
        capture_output=True,
        text=True,
    )


def test_cierre_flag_runs_r6_r7(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Real git on a directory that is not a repository; the ceiling keeps git from finding a
    # repository above tmp_path. Never run against the real repo: it would depend on the tree.
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    root = make_repo(tmp_path, {"docs/PLAN.md": _plan_with_version("31 oct 2026")})
    assert check_docs.main(["--cierre", "--root", str(root)]) == 0
    out = capsys.readouterr().out
    unverifiable = [ln for ln in out.splitlines() if check_docs.WARN_UNVERIFIABLE in ln]
    assert len(unverifiable) == len(check_docs.scope_files(root))
    assert ": R7: " not in out

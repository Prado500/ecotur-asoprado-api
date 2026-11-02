"""Tests for scripts/check_docs.py (docs coherence gate, ADR-0008)."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
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
        "4 m, 90 %, 7 horas",
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

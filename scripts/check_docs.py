"""Compuerta de documentación: el flujo y el plan no pueden desincronizarse en silencio.

Alcance (ADR-0008 punto 7): `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/backlog.md` y
`docs/sesiones/*.md`. Las citas de forma fija (ADR-0008 punto 3) se quitan de la línea antes de
evaluar R2 y R5.

Reglas bloqueantes (todas deterministas, todas con exit code):
  R1. Cada comando de `.claude/commands/*.md` aparece en la tabla de comandos de
      `docs/sesiones/README.md`, y cada comando de esa tabla existe como archivo.
  R2. Ninguna fecha de cronograma ("día N" o día de la semana + número) fuera de PLAN §3: los días
      viven solo ahí (CONTEXT §0). PLAN se evalúa fuera de su sección 3; el resto, entero.
  R3. Todo bloque `B-XXX` citado en el alcance existe en la tabla de bloques de PLAN §2b.
  R4. La columna "Decisión" del backlog usa solo el vocabulario cerrado: Entra · B-x /
      Sale → B-FUTURO / Decidir en B-x, con un calificador opcional entre paréntesis sin bloques
      ni vocabulario dentro, o Hecho (referencia). El estado intermedio se deriva con `--estado`.
  R5. La fecha de entrega más cercana (±40 caracteres) a "entrega", "deadline" o "fecha límite"
      en PLAN, backlog y sesiones es la de CONTEXT §2 y la línea lleva la cita `(CONTEXT §2)`.

Uso:
  python scripts/check_docs.py              reglas bloqueantes (exit 1 si hay errores)
  python scripts/check_docs.py --estado     vista derivada del estado de cada ítem
  python scripts/check_docs.py --root RUTA  raíz del repo (por defecto, la de este script)

Lo invoca también scripts/check.py como paso "docs". Un flag desconocido termina con exit 2.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def read(root: Path, rel: str) -> str:
    """Read a repo-relative text file as UTF-8.

    Args:
        root: Repository root (injected so rules can run against fixtures).
        rel: Path relative to ``root``.

    Returns:
        The file content.
    """
    return (root / rel).read_text(encoding="utf-8")


class Section(NamedTuple):
    """A level-2 heading of a markdown file and its 1-based inclusive line bounds."""

    num: str
    title: str
    start: int
    end: int


_SECTION_RE = re.compile(r"^## (\d+[a-z]?)\. (.*)$")


def sections(text: str) -> list[Section]:
    """Split a document into its ``## N.`` sections.

    ``###`` headings belong to the preceding ``##``. ``end`` is the line before the next ``##``
    heading, or the last line of the document.

    Args:
        text: Markdown content.

    Returns:
        Sections in document order.
    """
    lines = text.splitlines()
    found: list[tuple[str, str, int]] = []
    for n, line in enumerate(lines, 1):
        m = _SECTION_RE.match(line)
        if m:
            found.append((m.group(1), m.group(2), n))
    result: list[Section] = []
    for i, (num, title, start) in enumerate(found):
        end = found[i + 1][2] - 1 if i + 1 < len(found) else len(lines)
        result.append(Section(num, title, start, end))
    return result


def _split_by_sections(
    root: Path, rel: str, nums: set[str]
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    text = read(root, rel)
    chosen = [s for s in sections(text) if s.num in nums]
    inside: list[tuple[int, str]] = []
    outside: list[tuple[int, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        target = inside if any(s.start <= n <= s.end for s in chosen) else outside
        target.append((n, line))
    return inside, outside


def lines_inside(root: Path, rel: str, nums: set[str]) -> list[tuple[int, str]]:
    """Return ``(line number, line)`` pairs that fall inside the given sections."""
    return _split_by_sections(root, rel, nums)[0]


def lines_outside(root: Path, rel: str, nums: set[str]) -> list[tuple[int, str]]:
    """Return ``(line number, line)`` pairs that fall outside the given sections."""
    return _split_by_sections(root, rel, nums)[1]


CITATION_RE = re.compile(
    r"`?\((?:CONTEXT §\d+[a-z]?|PLAN §\d+[a-z]?|backlog (?:[A-Z]+-\d+|[A-Z]\d+)|ADR-\d{4}"
    r"|AGENTS §\d+[a-z]?|README de sesiones|bitácora \d{4}-\d{2}-\d{2}"
    r"|docs/deuda/(?:[A-Z]+-\d+|[A-Z]\d+)/)\)`?"
)


def strip_citations(line: str) -> str:
    """Remove fixed-form citations (ADR-0008 point 3), with or without backticks."""
    return CITATION_RE.sub("", line)


def scope_files(root: Path) -> list[str]:
    """Return the living documents every content rule reads (ADR-0008 point 7).

    ``docs/bitacora``, ``docs/adr`` and ``docs/deuda`` are dated, immutable records and stay out.

    Args:
        root: Repository root.

    Returns:
        Repo-relative POSIX paths: CONTEXT, PLAN, backlog, then ``docs/sesiones/*.md`` sorted.
    """
    sesiones = sorted(p.relative_to(root).as_posix() for p in (root / "docs/sesiones").glob("*.md"))
    return ["docs/CONTEXT.md", "docs/PLAN.md", "docs/backlog.md", *sesiones]


def numbered_lines(root: Path, rel: str) -> list[tuple[int, str]]:
    """Return every ``(line number, line)`` pair of a file, 1-based."""
    return list(enumerate(read(root, rel).splitlines(), 1))


def _error(rel: str, n: int, rule: str, message: str, line: str) -> str:
    return f'{rel}:{n}: {rule}: {message} — "{line[:80]}"'


def rule_commands(root: Path, errors: list[str]) -> None:
    """R1: commands on disk and in the README table must match in both directions."""
    readme = read(root, "docs/sesiones/README.md")
    on_disk = {p.stem for p in (root / ".claude/commands").glob("*.md")}
    in_readme = set(re.findall(r"^\| `/([a-z-]+)", readme, flags=re.M))
    for c in sorted(on_disk - in_readme):
        errors.append(
            f"R1: comando `/{c}` existe en .claude/commands/ pero no está en la tabla de "
            "docs/sesiones/README.md"
        )
    for c in sorted(in_readme - on_disk):
        errors.append(
            f"R1: la tabla de docs/sesiones/README.md menciona `/{c}` pero no existe "
            f".claude/commands/{c}.md"
        )


SCHEDULE_DAY_RE = re.compile(
    r"\b(?:d[ií]a|lun(?:es)?|mar(?:tes)?|mi[eé](?:rcoles)?|jue(?:ves)?|vie(?:rnes)?"
    r"|s[aá]b(?:ado)?|dom(?:ingo)?)\.?\s+\d{1,2}\b(?![:\d])(?!\s*(?:h(?:oras?)?|m|%)(?!\w))",
    re.IGNORECASE,
)
"""Schedule date: "día N" or a weekday plus a number; clock times and units are not dates."""


def rule_no_schedule_days(root: Path, errors: list[str]) -> None:
    """R2: no schedule date outside PLAN §3 (CONTEXT §0: days live only there).

    Headings are included (ADR-0008 point 1: a hard fact never goes in a title). Citations are
    stripped first, so ``(bitácora 2026-10-29)`` is not a date.

    Args:
        root: Repository root.
        errors: Accumulator; one entry per offending line.
    """
    for rel in scope_files(root):
        lines = (
            lines_outside(root, rel, {"3"}) if rel == "docs/PLAN.md" else numbered_lines(root, rel)
        )
        for n, line in lines:
            if SCHEDULE_DAY_RE.search(strip_citations(line)):
                errors.append(_error(rel, n, "R2", "fecha de cronograma fuera de PLAN §3", line))


def rule_blocks(root: Path, errors: list[str]) -> None:
    """R3: every ``B-X`` block mentioned in the scope files is defined in PLAN §2b."""
    plan = read(root, "docs/PLAN.md")
    defined = set(re.findall(r"^\| `(B-[A-Z0-9-]+)` \|", plan, flags=re.M))
    for rel in scope_files(root):
        for n, line in numbered_lines(root, rel):
            for b in sorted(set(re.findall(r"B-[A-Z0-9-]+", line))):
                if b not in defined:
                    message = f"bloque `{b}` no está definido en docs/PLAN.md §2b"
                    errors.append(_error(rel, n, "R3", message, line))


_QUAL = r"\((?:(?!B-[A-Z0-9-]+)(?!\b(?:Entra|Sale|Decidir|Hecho)\b)[^()])*\)"
"""One parenthesized qualifier: no block, no vocabulary word, no nested parentheses."""

DECISION_RE = re.compile(
    r"^\*\*(?:(?:Entra · `B-[A-Z0-9-]+`|Sale → `B-FUTURO`|Decidir en `B-[A-Z0-9-]+`)"
    r"(?: " + _QUAL + r")?|Hecho " + _QUAL + r")\*\*$"
)
"""Closed vocabulary of the backlog "Decisión" cell: exactly one block, nothing else."""


def rule_decisions(root: Path, errors: list[str]) -> None:
    """R4: validate the backlog "Decisión" column against the closed vocabulary.

    Exactly one block and at most one qualifier without blocks inside (``DECISION_RE``). Rows
    are split with `" | "`: no cell is assumed to contain an inner ` | `.

    Args:
        root: Repository root.
        errors: Accumulator; one entry per offending cell.
    """
    dec_idx = None
    for n, line in enumerate(read(root, "docs/backlog.md").splitlines(), 1):
        if line.startswith("| ") and "Decisión" in [
            c.strip() for c in line.strip().strip("|").split("|")
        ]:
            hdr = [c.strip() for c in line.strip().strip("|").split("|")]
            dec_idx = hdr.index("Decisión")
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("| ") or dec_idx is None:
            dec_idx = dec_idx if line.startswith("|") else None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) <= dec_idx:
            continue
        if not DECISION_RE.match(cells[dec_idx]):
            message = "decisión fuera del vocabulario (un bloque, un calificador sin bloques)"
            errors.append(_error("docs/backlog.md", n, "R4", message, cells[dec_idx]))


DATE_RE = re.compile(
    r"\b(\d{1,2})(?: de)? (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[a-z]*\b"
    r"(?:(?: de)? (\d{4}))?|\b(\d{4})-(\d{2})-(\d{2})\b"
)
"""A written date ("11 de enero de 2027", "11 ene") or an ISO date."""

TRIGGER_RE = re.compile(r"\b(?:entrega|deadline|fecha l[ií]mite)\b", re.IGNORECASE)
_MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
_WINDOW = 40


class DayMonth(NamedTuple):
    """A date reduced to what R5 compares: day, three-letter month and optional year."""

    day: int
    month: str
    year: int | None


def _day_month(m: re.Match[str]) -> DayMonth:
    if m.group(4):
        month = int(m.group(5))
        name = _MONTHS[month - 1] if 1 <= month <= 12 else ""
        return DayMonth(int(m.group(6)), name, int(m.group(4)))
    year = m.group(3)
    return DayMonth(int(m.group(1)), m.group(2), int(year) if year else None)


def _same_date(found: DayMonth, deadline: DayMonth) -> bool:
    if (found.day, found.month) != (deadline.day, deadline.month):
        return False
    return found.year is None or deadline.year is None or found.year == deadline.year


def _nearest_date(dates: list[re.Match[str]], trigger: re.Match[str]) -> re.Match[str] | None:
    """Date whose start is closest to the trigger span, within ±40 characters of it."""

    def distance(d: re.Match[str]) -> int:
        return max(trigger.start() - d.start(), d.start() - trigger.end(), 0)

    near = [d for d in dates if distance(d) <= _WINDOW]
    return min(near, key=distance) if near else None


def read_deadline(root: Path) -> tuple[DayMonth | None, int | None]:
    """Read the deadline from its owner, the ``| **Deadline** |`` row of CONTEXT §2.

    Args:
        root: Repository root.

    Returns:
        ``(deadline, line number)``; the deadline is ``None`` if the row or its date is missing,
        and the line number is ``None`` if the row is missing.
    """
    for n, line in numbered_lines(root, "docs/CONTEXT.md"):
        if line.startswith("| **Deadline** |"):
            m = DATE_RE.search(strip_citations(line))
            return (_day_month(m) if m else None), n
    return None, None


def rule_deadline(root: Path, errors: list[str]) -> None:
    """R5: a delivery date outside CONTEXT equals the CONTEXT §2 deadline and cites it.

    For each trigger ("entrega", "deadline", "fecha límite") the evaluated date is the one whose
    start is nearest to the trigger, within ±40 characters on either side; with no date in that
    window the trigger is not evaluated. A wrong date takes precedence over a missing citation.

    Args:
        root: Repository root.
        errors: Accumulator; an unreadable deadline is a single error and stops the rule.
    """
    deadline, row = read_deadline(root)
    if deadline is None:
        where = "docs/CONTEXT.md" if row is None else f"docs/CONTEXT.md:{row}"
        errors.append(f"{where}: R5: deadline no legible en CONTEXT §2")
        return
    for rel in scope_files(root):
        if rel == "docs/CONTEXT.md":
            continue
        for n, line in numbered_lines(root, rel):
            clean = strip_citations(line)
            dates = list(DATE_RE.finditer(clean))
            if not dates:
                continue
            for trigger in TRIGGER_RE.finditer(clean):
                date_match = _nearest_date(dates, trigger)
                if date_match is None:
                    continue
                if not _same_date(_day_month(date_match), deadline):
                    message = f'fecha de entrega "{date_match.group(0)}" ≠ deadline de CONTEXT §2'
                    errors.append(_error(rel, n, "R5", message, line))
                elif "(CONTEXT §2)" not in line:
                    message = "fecha de entrega sin cita (CONTEXT §2)"
                    errors.append(_error(rel, n, "R5", message, line))


def estado(root: Path) -> int:
    """Derived (never stored) view of each in-progress item, according to its folder."""
    base = root / "docs/deuda"
    if not base.exists():
        print("docs/deuda/ no existe: ningún ítem en curso.")
        return 0
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        parts = []
        if (d / "verificacion.md").exists():
            parts.append("verificado")
        if (d / "plan.md").exists():
            parts.append("planeado")
        prog = d / "progress.json"
        if prog.exists():
            m = re.search(r'"current_target"\s*:\s*"([^"]+)"', prog.read_text(encoding="utf-8"))
            parts.append(f"en ejecución (objetivo: {m.group(1) if m else '?'})")
        handoffs = sorted(p.stem.split("-", 1)[1] for p in d.glob("handoff-*.md"))
        if handoffs:
            parts.append("handoffs: " + ", ".join(handoffs))
        gaps = d / "gaps.md"
        if gaps.exists():
            txt = gaps.read_text(encoding="utf-8")
            parts.append(
                "última auditoría: " + ("PASS" if "PASS" in txt.splitlines()[-1] else "con gaps")
            )
        print(f"{d.name}: " + (" → ".join(parts) if parts else "carpeta vacía"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser; unknown flags make argparse exit with code 2."""
    parser = argparse.ArgumentParser(
        prog="check_docs.py", description="Compuerta de coherencia de la documentación."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio")
    parser.add_argument("--estado", action="store_true", help="estado derivado de cada ítem")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the blocking rules R1-R5, or ``--estado``.

    Args:
        argv: Arguments without the program name; ``None`` reads ``sys.argv``.

    Returns:
        Exit code: 0 coherent, 1 desynchronized. Invalid arguments exit 2 (argparse).
    """
    args = build_parser().parse_args(argv)
    root: Path = args.root
    if args.estado:
        return estado(root)
    errors: list[str] = []
    for rule in (
        rule_commands,
        rule_no_schedule_days,
        rule_blocks,
        rule_decisions,
        rule_deadline,
    ):
        rule(root, errors)
    if errors:
        print("Documentación desincronizada:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, "
        "R4 decisiones, R5 deadline)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

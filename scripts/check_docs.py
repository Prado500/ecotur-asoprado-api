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

Comandos informativos (exit 0 siempre; excluyentes entre sí y con la pasada bloqueante):
  R8. `--copias [DUEÑO]`: cada cita de forma fija del alcance, por archivo y línea; con DUEÑO, solo
      las citas cuyo interior empieza por ese texto (`CONTEXT §2`, `ADR-0008`, `backlog`).
  R9. `--huerfanas`: candidatos a hecho duro (fecha, `N %`, `N tests`, `N h`, `N m`) en líneas sin
      ninguna cita, fuera de las secciones dueñas (CONTEXT §0, §2, §4, §6; PLAN §3, §6, §7) y de
      las líneas de versión. Ruidoso por diseño: lo revisa la sesión que cierra.
  `--estado`: vista derivada de cada ítem de `docs/deuda/`; `progress.json` se lee como JSON y
      `gaps.md` por la línea de veredicto de su último bloque `## Auditoría Fase`.

Reglas de cierre (solo con `--cierre`: dependen de git y de la fecha de hoy, así que la compuerta
por defecto no las corre y sigue siendo determinista, ADR-0001):
  R6. La línea de versión (ADR-0007) de cada archivo del alcance no es anterior a su último commit;
      un archivo sin línea de versión es error solo si su último commit es posterior al 28 oct
      2026. Cambios sin commitear o git no disponible son avisos, nunca error.
  R7. Toda fila de PLAN §3 con fecha anterior a hoy lleva en `Cierre` la marca `[✔◐✘] N`. El mes
      se hereda dentro de cada tabla y el año sube cuando el mes retrocede.

Uso:
  python scripts/check_docs.py                  reglas bloqueantes (exit 1 si hay errores)
  python scripts/check_docs.py --cierre         además R6 y R7 (ritual de cierre)
  python scripts/check_docs.py --estado         vista derivada del estado de cada ítem
  python scripts/check_docs.py --copias [DUEÑO] citas de forma fija por dueño
  python scripts/check_docs.py --huerfanas      candidatos a hecho duro sin cita
  python scripts/check_docs.py --root RUTA      raíz del repo (por defecto, la de este script)

Lo invoca también scripts/check.py como paso "docs". Un flag desconocido termina con exit 2.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Literal, NamedTuple

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
    session_prompts = sorted(
        p.relative_to(root).as_posix() for p in (root / "docs/sesiones").glob("*.md")
    )
    return ["docs/CONTEXT.md", "docs/PLAN.md", "docs/backlog.md", *session_prompts]


def numbered_lines(root: Path, rel: str) -> list[tuple[int, str]]:
    """Return every line of a file with its number.

    Args:
        root: Repository root.
        rel: Path relative to ``root``.

    Returns:
        ``(line number, line)`` pairs in file order, numbered from 1.
    """
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


def list_citations(root: Path, prefix: str) -> list[str]:
    """R8: list every fixed-form citation of the scope files, optionally filtered by owner.

    This is the mechanism of the closing ritual (ADR-0008 point 6): when an owner changes, every
    line that cites it is reviewed.

    Args:
        root: Repository root.
        prefix: Owner filter matched against the citation interior (no backticks or
            parentheses); ``""`` lists everything.

    Returns:
        ``file:line: (citation): "text"`` entries ordered by file, line and position.
    """
    entries: list[str] = []
    for rel in scope_files(root):
        for n, line in numbered_lines(root, rel):
            for m in CITATION_RE.finditer(line):
                citation = m.group(0).strip("`")
                if citation[1:-1].startswith(prefix):
                    entries.append(f'{rel}:{n}: {citation}: "{line[:80]}"')
    return entries


_ORPHAN_RES = (
    DATE_RE,
    re.compile(r"\b\d{1,3} %"),
    re.compile(r"\b\d+ tests\b"),
    re.compile(r"\b\d+ h\b"),
    re.compile(r"\b\d+ m\b"),
)
"""Shapes of a hard fact: a date, a percentage, a test count, hours, half-days."""

_OWNER_SECTIONS = {"docs/CONTEXT.md": {"0", "2", "4", "6"}, "docs/PLAN.md": {"3", "6", "7"}}
"""Sections that own hard facts (CONTEXT §0 is the fact-to-owner map): never orphans."""


def list_orphans(root: Path) -> list[str]:
    """R9: list candidate hard facts written on a line without any citation.

    Informative and noisy by design (ADR-0008 addendum, point 3): it never fails the gate.

    Args:
        root: Repository root.

    Returns:
        One ``file:line: … "fragment" — "line"`` entry per offending line, with the first
        fragment of the line, ordered by file and line.
    """
    entries: list[str] = []
    for rel in scope_files(root):
        owned = _OWNER_SECTIONS.get(rel)
        lines = lines_outside(root, rel, owned) if owned else numbered_lines(root, rel)
        for n, line in lines:
            if "**Versión " in line or CITATION_RE.search(line):
                continue
            clean = strip_citations(line)
            found = [m for pattern in _ORPHAN_RES if (m := pattern.search(clean))]
            if found:
                first = min(found, key=lambda m: m.start()).group(0)
                entries.append(
                    f'{rel}:{n}: candidato a hecho duro sin cita: "{first}" — "{line[:80]}"'
                )
    return entries


class Progress(NamedTuple):
    """What ``--estado`` derives from a ``progress.json``."""

    state: Literal["done", "running", "unreadable"]
    target: str | None


def read_progress(path: Path) -> Progress:
    """Parse a ``progress.json`` into its derived state.

    An item is ``done`` when ``current_target`` is null and it has phases, all ``completed``
    (executed, pending PR or merged); any other readable object is ``running``.

    Args:
        path: Path of the ``progress.json`` file.

    Returns:
        The state and, when it is a string, the current target.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:  # JSONDecodeError and UnicodeDecodeError (a file that is not UTF-8)
        return Progress("unreadable", None)
    if not isinstance(data, dict):
        return Progress("unreadable", None)
    raw_target = data.get("current_target")
    phases = data.get("phases")
    if (
        raw_target is None
        and isinstance(phases, dict)
        and phases
        and all(isinstance(p, dict) and p.get("status") == "completed" for p in phases.values())
    ):
        return Progress("done", None)
    return Progress("running", raw_target if isinstance(raw_target, str) else None)


STATE_DONE = "ejecutado (todas las fases); pendiente de PR o mezclado"
STATE_RUNNING = "en ejecución (objetivo: {target})"
STATE_UNREADABLE = "progress.json ilegible"
"""What ``--estado`` prints for each ``Progress.state``; ``{target}`` is ``?`` when unknown."""

AUDIT_BLOCK_RE = re.compile(r"^## Auditoría Fase ")
"""Heading of an audit block: ``handoff-auditor`` adds one per audit to the item's ``gaps.md``."""

VERDICT_RE = re.compile(
    r"^(?:- )?(?:\*\*)?Veredicto(?: Fase [^:*]+)?:(?:\*\*)? (?:\*\*)?(PASS|GAPS)\b"
)
"""Verdict line, anchored at its start: a finding that merely mentions a verdict is not one."""

AuditVerdict = Literal["pass", "gaps", "no_verdict", "unreadable"]

STATE_AUDIT = "última auditoría: {verdict}"
AUDIT_LABELS: dict[AuditVerdict, str] = {
    "pass": "PASS",
    "gaps": "con gaps",
    "no_verdict": "sin veredicto",
    "unreadable": "ilegible",
}
"""What ``--estado`` prints for each ``AuditVerdict``."""


def read_last_audit(path: Path) -> AuditVerdict:
    """Read the verdict of the last audit block of a ``gaps.md``.

    Only the first verdict line of the last ``## Auditoría Fase`` block counts: findings are never
    read, so a mention of ``[BLOQUEANTE]`` or of an old ``PASS`` cannot change the result.

    Args:
        path: Path of the ``gaps.md`` file.

    Returns:
        ``pass`` or ``gaps`` from the verdict line; ``no_verdict`` if the file has no block or its
        last block has no verdict line; ``unreadable`` if it is blank or cannot be read as UTF-8.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError, ValueError:  # ValueError covers UnicodeDecodeError
        return "unreadable"
    if not text.strip():
        return "unreadable"
    lines = text.splitlines()
    starts = [n for n, line in enumerate(lines) if AUDIT_BLOCK_RE.match(line)]
    if not starts:
        return "no_verdict"
    for line in lines[starts[-1] + 1 :]:
        m = VERDICT_RE.match(line)
        if m:
            return "pass" if m.group(1) == "PASS" else "gaps"
    return "no_verdict"


def estado(root: Path) -> int:
    """Print the derived (never stored) state of each item of ``docs/deuda/``.

    The state comes from the files the item's folder has (verification, plan, progress, handoffs,
    audit), so it cannot drift from them.

    Args:
        root: Repository root.

    Returns:
        0: the view is informative and an unreadable ``gaps.md`` is reported, never raised. The one
        declared exception: if the operating system prevents reading a ``progress.json`` (no
        permission, locked), the view ends with a traceback and exit 1.
    """
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
            progress = read_progress(prog)
            if progress.state == "done":
                parts.append(STATE_DONE)
            elif progress.state == "unreadable":
                parts.append(STATE_UNREADABLE)
            else:
                parts.append(STATE_RUNNING.format(target=progress.target or "?"))
        handoffs = sorted(p.stem.split("-", 1)[1] for p in d.glob("handoff-*.md"))
        if handoffs:
            parts.append("handoffs: " + ", ".join(handoffs))
        gaps = d / "gaps.md"
        if gaps.exists():
            parts.append(STATE_AUDIT.format(verdict=AUDIT_LABELS[read_last_audit(gaps)]))
        print(f"{d.name}: " + (" → ".join(parts) if parts else "carpeta vacía"))
    return 0


def git_last_commit_date(root: Path, rel: str) -> date | None:
    """Return the date of the last commit that touched a file (``git log -1 --format=%cs``).

    Args:
        root: Repository root; git runs there.
        rel: Path relative to ``root``.

    Returns:
        The committer date, or ``None`` if git is missing, fails (not a repository) or the file
        has no history (untracked, shallow clone).
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    out = result.stdout.strip()
    if result.returncode != 0 or not out:
        return None
    return date.fromisoformat(out)


def git_is_dirty(root: Path, rel: str) -> bool | None:
    """Tell whether a file has uncommitted changes (``git status --porcelain``).

    Args:
        root: Repository root; git runs there.
        rel: Path relative to ``root``.

    Returns:
        ``True`` with changes, ``False`` without them, ``None`` if git is missing or fails.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", rel],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


VERSION_RE = re.compile(
    r"^> \*\*Versión (\d+)\.(\d+) — (\d{1,2}) (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)"
    r" (\d{4})\.\*\*"
)
"""Version line of a living document (ADR-0007 point 3): ``> **Versión X.Y — D mmm AAAA.**``."""

ADR_0007_START = date(2026, 10, 28)
"""ADR-0007 point 5: a file last committed on or before this day may lack a version line."""

WARN_DIRTY = "cambios sin commitear: la versión se sube en el cierre"
WARN_UNVERIFIABLE = "no verificable (git no disponible o archivo sin historia)"
"""R6 warnings: printed under ``Avisos:``, they never change the exit code."""


class VersionLine(NamedTuple):
    """The version line of a file: its date, its 1-based line number and its text."""

    when: date
    n: int
    line: str


def read_version(root: Path, rel: str) -> VersionLine | None:
    """Find the version line of a file (ADR-0007 point 3).

    Args:
        root: Repository root.
        rel: Path relative to ``root``.

    Returns:
        The first line matching ``VERSION_RE``, or ``None`` if there is none or its date does not
        exist (``31 nov``): an impossible date is not a valid version line.
    """
    for n, line in numbered_lines(root, rel):
        m = VERSION_RE.match(line)
        if m:
            try:
                when = date(int(m.group(5)), _MONTHS.index(m.group(4)) + 1, int(m.group(3)))
            except ValueError:
                return None
            return VersionLine(when, n, line)
    return None


def rule_version_header(
    root: Path,
    errors: list[str],
    warnings: list[str],
    *,
    last_commit_date: Callable[[Path, str], date | None] = git_last_commit_date,
    is_dirty: Callable[[Path, str], bool | None] = git_is_dirty,
) -> None:
    """R6 (``--cierre``): no version line of the scope files predates its file's last commit.

    A file without a version line is an error only if its last commit is after
    ``ADR_0007_START`` (ADR-0007 point 5). Uncommitted changes and an unavailable git are
    warnings, never errors: the version goes up once a day, at closing time, and a shallow clone
    must not turn red.

    Args:
        root: Repository root.
        errors: Accumulator for blocking findings.
        warnings: Accumulator for findings that never change the exit code.
        last_commit_date: Injected git query (tests pass a fake; nothing spawns a process).
        is_dirty: Injected git query for uncommitted changes.
    """
    for rel in scope_files(root):
        last = last_commit_date(root, rel)
        if is_dirty(root, rel):
            warnings.append(f"{rel}: R6: {WARN_DIRTY}")
        if last is None:
            warnings.append(f"{rel}: R6: {WARN_UNVERIFIABLE}")
            continue
        version = read_version(root, rel)
        if version is None:
            if last > ADR_0007_START:
                errors.append(f"{rel}: R6: sin línea de versión (ADR-0007)")
        elif version.when < last:
            message = f"encabezado de versión ({version.when}) anterior al último commit ({last})"
            errors.append(_error(rel, version.n, "R6", message, version.line))


DAY_CELL_RE = re.compile(
    r"^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom) (\d{1,2})"
    r"(?: (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic))?"
)
"""First cell of a PLAN §3 row: weekday, day and, when the row names it, the month."""

CLOSE_MARK_RE = re.compile(r"^[✔◐✘] \d{1,2}$")
"""``Cierre`` cell of a closed day: done, partial or nothing done, plus its log's day number."""


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _dated_rows(lines: list[tuple[int, str]], start_year: int) -> list[tuple[int, str, date, str]]:
    """Rows of the tables that have a ``Cierre`` column, with their date and ``Cierre`` cell.

    The first line of each table is its header and resets month and year: the month is inherited
    from the last row that names it, and the year starts at ``start_year`` and goes up when the
    month goes back. Rows without a date (``(se fecha …)``, separator) or before any month is
    named are skipped, and so is an impossible date.
    """
    rows: list[tuple[int, str, date, str]] = []
    close_idx: int | None = None
    month: int | None = None
    year = start_year
    in_table = False
    for n, line in lines:
        if not line.startswith("|"):
            in_table = False
            continue
        cells = _cells(line)
        if not in_table:
            in_table = True
            close_idx = cells.index("Cierre") if "Cierre" in cells else None
            month, year = None, start_year
            continue
        m = DAY_CELL_RE.match(cells[0])
        if close_idx is None or m is None:
            continue
        if m.group(3):
            named = _MONTHS.index(m.group(3)) + 1
            if month is not None and named < month:
                year += 1
            month = named
        if month is None:
            continue
        try:
            day = date(year, month, int(m.group(2)))
        except ValueError:
            continue
        rows.append((n, line, day, cells[close_idx] if close_idx < len(cells) else ""))
    return rows


def rule_closed_days_marked(
    root: Path, errors: list[str], *, today: Callable[[], date] = date.today
) -> None:
    """R7 (``--cierre``): every PLAN §3 row dated before today carries its closing mark.

    The mark is ``[✔◐✘] N`` in the ``Cierre`` column (ADR-0008 point 6); today's row needs none
    yet. The year of the first row is the year of PLAN's version line.

    Args:
        root: Repository root.
        errors: Accumulator; a PLAN without a version line is a single error and stops the rule.
        today: Injected clock (tests pass a fixed date).
    """
    rel = "docs/PLAN.md"
    version = read_version(root, rel)
    if version is None:
        errors.append(f"{rel}: R7: sin línea de versión: el año de PLAN §3 no se puede inferir")
        return
    now = today()
    for n, line, day, close in _dated_rows(lines_inside(root, rel, {"3"}), version.when.year):
        if day < now and not CLOSE_MARK_RE.match(close):
            errors.append(_error(rel, n, "R7", "fila de PLAN §3 cerrada sin marca en Cierre", line))


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser.

    Unknown flags, and more than one mode at once (``--cierre`` or an informative command), make
    argparse exit with code 2.

    Returns:
        The parser.
    """
    parser = argparse.ArgumentParser(
        prog="check_docs.py", description="Compuerta de coherencia de la documentación."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--cierre",
        action="store_true",
        dest="closing",
        help="además R6 versión y R7 cierres (usa git y la fecha de hoy)",
    )
    mode.add_argument("--estado", action="store_true", help="estado derivado de cada ítem")
    mode.add_argument(
        "--copias",
        nargs="?",
        const="",
        default=None,
        dest="citation_owner",
        metavar="DUEÑO",
        help="citas de forma fija, opcionalmente solo las de un dueño",
    )
    mode.add_argument(
        "--huerfanas",
        action="store_true",
        dest="orphans",
        help="candidatos a hecho duro sin cita",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the blocking rules R1-R5 (plus R6-R7 with ``--cierre``) or one informative command.

    Args:
        argv: Arguments without the program name; ``None`` reads ``sys.argv``.

    Returns:
        Exit code: 0 coherent or informative command, 1 desynchronized. Invalid arguments exit
        2 (argparse).
    """
    args = build_parser().parse_args(argv)
    root: Path = args.root
    if args.estado:
        return estado(root)
    if args.citation_owner is not None:
        for entry in list_citations(root, args.citation_owner):
            print(entry)
        return 0
    if args.orphans:
        for entry in list_orphans(root):
            print(entry)
        return 0
    errors: list[str] = []
    warnings: list[str] = []
    for rule in (
        rule_commands,
        rule_no_schedule_days,
        rule_blocks,
        rule_decisions,
        rule_deadline,
    ):
        rule(root, errors)
    if args.closing:
        rule_version_header(root, errors, warnings)
        rule_closed_days_marked(root, errors)
    if warnings:
        print("Avisos:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("Documentación desincronizada:")
        for e in errors:
            print(f"  - {e}")
        return 1
    rules = "R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline"
    if args.closing:
        rules += " + cierre: R6 versión, R7 cierres"
    print(f"Documentación coherente (reglas: {rules}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

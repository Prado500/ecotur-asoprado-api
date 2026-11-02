"""Compuerta de documentación: el flujo y el plan no pueden desincronizarse en silencio.

Reglas (todas deterministas, todas con exit code):
  1. Cada comando de `.claude/commands/*.md` aparece en la tabla de comandos de
     `docs/sesiones/README.md`, y cada comando de esa tabla existe como archivo.
  2. `docs/backlog.md` y `docs/CONTEXT.md` no mencionan días del cronograma ("día N"): los días
     viven solo en `docs/PLAN.md` §3 (CONTEXT §0).
  3. Todo bloque `B-XXX` referenciado en backlog, CONTEXT o PLAN existe en la tabla de bloques de
     PLAN §2b.
  4. La columna "Decisión" del backlog usa solo el vocabulario cerrado: Entra · B-x /
     Sale → B-FUTURO / Decidir en B-x / Hecho (…). El estado intermedio no se escribe: se deriva
     con `--estado`.

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


def rule_no_days(root: Path, errors: list[str]) -> None:
    """R2: backlog and CONTEXT do not mention schedule days ("día N")."""
    for p in ("docs/backlog.md", "docs/CONTEXT.md"):
        for n, line in enumerate(read(root, p).splitlines(), 1):
            if re.search(r"\bdías? [0-9]", line):
                errors.append(
                    f'{p}:{n}: R2: día del cronograma fuera de docs/PLAN.md §3 — "{line[:80]}"'
                )


def rule_blocks(root: Path, errors: list[str]) -> None:
    """R3: every ``B-X`` block mentioned is defined in the PLAN §2b table."""
    plan = read(root, "docs/PLAN.md")
    defined = set(re.findall(r"^\| `(B-[A-Z0-9-]+)` \|", plan, flags=re.M))
    for p in ("docs/backlog.md", "docs/CONTEXT.md", "docs/PLAN.md"):
        for n, line in enumerate(read(root, p).splitlines(), 1):
            for b in set(re.findall(r"B-[A-Z0-9-]+", line)):
                if b not in defined:
                    errors.append(
                        f"{p}:{n}: R3: bloque `{b}` no está definido en docs/PLAN.md §2b "
                        f'— "{line[:80]}"'
                    )


DECISION_RE = re.compile(
    r"^\*\*(Entra · `B-[A-Z0-9-]+`|Sale → `B-FUTURO`|Decidir en `B-[A-Z0-9-]+`|Hecho \().*\*\*$"
)


def rule_decisions(root: Path, errors: list[str]) -> None:
    """R4: validate the backlog "Decisión" column against the closed vocabulary.

    Rows are split with `" | "`: no cell is assumed to contain an inner ` | `.
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
            errors.append(
                f'docs/backlog.md:{n}: R4: decisión fuera del vocabulario — "{cells[dec_idx][:80]}"'
            )


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
    """Run the blocking rules, or ``--estado``.

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
    for rule in (rule_commands, rule_no_days, rule_blocks, rule_decisions):
        rule(root, errors)
    if errors:
        print("Documentación desincronizada:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Documentación coherente (reglas: R1 comandos, R2 días, R3 bloques, R4 decisiones).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

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

Uso: python scripts/check_docs.py   (lo invoca también scripts/check.py como paso "docs")
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def read(p: str) -> str:
    return Path(p).read_text(encoding="utf-8")


def rule_commands(errors: list[str]) -> None:
    readme = read("docs/sesiones/README.md")
    on_disk = {p.stem for p in Path(".claude/commands").glob("*.md")}
    in_readme = set(re.findall(r"^\| `/([a-z-]+)", readme, flags=re.M))
    for c in sorted(on_disk - in_readme):
        errors.append(
            f"comando `/{c}` existe en .claude/commands/ pero no está en la tabla de "
            "docs/sesiones/README.md"
        )
    for c in sorted(in_readme - on_disk):
        errors.append(
            f"la tabla de docs/sesiones/README.md menciona `/{c}` pero no existe "
            f".claude/commands/{c}.md"
        )


def rule_no_days(errors: list[str]) -> None:
    for p in ("docs/backlog.md", "docs/CONTEXT.md"):
        for n, line in enumerate(read(p).splitlines(), 1):
            if re.search(r"\bdías? [0-9]", line):
                errors.append(
                    f"{p}:{n}: menciona un día del cronograma; los días viven solo en "
                    "docs/PLAN.md §3"
                )


def rule_blocks(errors: list[str]) -> None:
    plan = read("docs/PLAN.md")
    defined = set(re.findall(r"^\| `(B-[A-Z0-9-]+)` \|", plan, flags=re.M))
    for p in ("docs/backlog.md", "docs/CONTEXT.md", "docs/PLAN.md"):
        for n, line in enumerate(read(p).splitlines(), 1):
            for b in set(re.findall(r"B-[A-Z0-9-]+", line)):
                if b not in defined:
                    errors.append(f"{p}:{n}: bloque `{b}` no está definido en docs/PLAN.md §2b")


DECISION_RE = re.compile(
    r"^\*\*(Entra · `B-[A-Z0-9-]+`|Sale → `B-FUTURO`|Decidir en `B-[A-Z0-9-]+`|Hecho \().*\*\*$"
)


def rule_decisions(errors: list[str]) -> None:
    """Valida la columna "Decisión" del backlog contra el vocabulario cerrado.

    Las filas se parten con `split(" | ")`: se asume que ninguna celda contiene ` | ` interno.
    """
    dec_idx = None
    for n, line in enumerate(read("docs/backlog.md").splitlines(), 1):
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
                f"docs/backlog.md:{n}: decisión fuera del vocabulario: {cells[dec_idx][:70]}"
            )


def estado() -> int:
    """Vista derivada (nunca almacenada) del estado de cada ítem en curso, según su carpeta."""
    base = Path("docs/deuda")
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


def main() -> int:
    if "--estado" in sys.argv:
        return estado()
    errors: list[str] = []
    for rule in (rule_commands, rule_no_days, rule_blocks, rule_decisions):
        rule(errors)
    if errors:
        print("Documentación desincronizada:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "Documentación coherente: comandos ↔ README, sin días fuera del cronograma, "
        "bloques definidos, decisiones en vocabulario."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

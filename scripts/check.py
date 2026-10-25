"""Compuerta de calidad del backend (ADR-0001): lo que debe pasar siempre, falla con exit code.

Uso:
    python scripts/check.py            # compuerta completa
    python scripts/check.py --fix      # primero formatea y autocorrige con ruff, luego la compuerta
    python scripts/check.py --no-tests # todo menos pytest (útil mientras se edita)

Es deliberadamente tool-neutral: la invocan los hooks de Claude Code, el CI de Azure y cualquier
agente (OpenCode incluido) por instrucción. Un solo lugar define qué significa "código aceptable".
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PY = sys.executable
REPO_ROOT = Path(__file__).resolve().parent.parent

# En Windows, al redirigir la salida a un fichero la consola usa cp1252 y los símbolos del RESUMEN
# rompen con UnicodeEncodeError. Forzamos UTF-8 (con reemplazo) para que la compuerta nunca falle por
# su propia salida.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# La compuerta siempre se evalúa desde la raíz del repo, sin importar desde dónde se invoque:
# ruff/mypy/import-linter/pytest leen pyproject.toml y buscan app/ y tests/ relativos a ella.
os.chdir(REPO_ROOT)


def _lint_imports_cmd() -> list[str]:
    exe = shutil.which("lint-imports")
    if exe:
        return [exe]
    # Fallback: módulo del paquete (por si el venv no tiene el script en PATH).
    return [PY, "-m", "importlinter.cli", "lint_imports"]


def steps(no_tests: bool) -> list[tuple[str, list[str]]]:
    s: list[tuple[str, list[str]]] = [
        ("ruff format --check", [PY, "-m", "ruff", "format", "--check", "."]),
        ("ruff check", [PY, "-m", "ruff", "check", "."]),
        ("mypy", [PY, "-m", "mypy"]),
        ("import-linter", _lint_imports_cmd()),
    ]
    if not no_tests:
        s.append(
            (
                "pytest + cobertura",
                [PY, "-m", "pytest", "-q", "--cov=app", "--cov-report=term-missing:skip-covered"],
            )
        )
    return s


def run(name: str, cmd: list[str]) -> bool:
    print(f"\n=== {name} ===", flush=True)
    t0 = time.perf_counter()
    code = subprocess.call(cmd)
    dt = time.perf_counter() - t0
    print(f"--- {name}: {'OK' if code == 0 else f'FALLA (exit {code})'} en {dt:.1f}s", flush=True)
    return code == 0


def main(argv: list[str]) -> int:
    fix = "--fix" in argv
    no_tests = "--no-tests" in argv
    print(f"Raíz del repo: {REPO_ROOT} · Python {sys.version.split()[0]}", flush=True)
    if fix:
        subprocess.call([PY, "-m", "ruff", "format", "."])
        subprocess.call([PY, "-m", "ruff", "check", "--fix", "."])
    results = {name: run(name, cmd) for name, cmd in steps(no_tests)}
    print("\n=== RESUMEN ===")
    for name, ok in results.items():
        print(f"  {'✔' if ok else '✘'} {name}")
    failed = [n for n, ok in results.items() if not ok]
    if failed:
        print(f"\nCompuerta NO superada: {', '.join(failed)}")
        return 1
    print("\nCompuerta superada.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

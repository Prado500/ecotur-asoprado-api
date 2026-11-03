"""Compuerta de calidad del backend (ADR-0001): lo que debe pasar siempre, falla con exit code.

Uso:
    python scripts/check.py            # compuerta completa
    python scripts/check.py --fix      # primero formatea y autocorrige con ruff, luego la compuerta
    python scripts/check.py --no-tests # todo menos pytest (útil mientras se edita)
    python scripts/check.py --soft ruff,mypy  # corre todo; esos pasos en rojo no bloquean (exit 0)

Claves de --soft: format, ruff, mypy, imports, docs, tests. Es una excepción de la INVOCACIÓN
(p. ej. el YAML del CI), no del valor por defecto: sin --soft la compuerta es estricta.
Clave desconocida → exit 2.

Es deliberadamente tool-neutral: la invocan los hooks de Claude Code, el CI de Azure y cualquier
agente (OpenCode incluido) por instrucción. Un solo lugar define qué significa "código aceptable".
"""

from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
import time
from collections.abc import Callable
from pathlib import Path

PY = sys.executable
REPO_ROOT = Path(__file__).resolve().parent.parent


def _prepare_process() -> None:
    """Pin the process to the repo root and make its output streams UTF-8.

    Called from ``main()`` only: importing this module must not change the cwd or the streams of
    the importing process (tests, tools).
    """
    # En Windows, al redirigir la salida a un fichero la consola usa cp1252 y los símbolos del
    # RESUMEN rompen con UnicodeEncodeError. Forzamos UTF-8 (con reemplazo) para que la compuerta
    # nunca falle por su propia salida.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    # La compuerta siempre se evalúa desde la raíz del repo, sin importar desde dónde se invoque:
    # ruff/mypy/import-linter/pytest leen pyproject.toml y buscan app/ y tests/ relativos a ella.
    os.chdir(REPO_ROOT)


# Console script names of import-linter: a Windows install has the .exe, a POSIX one the bare name.
LINT_IMPORTS_NAMES: tuple[str, ...] = ("lint-imports.exe", "lint-imports")


def find_lint_imports(
    scripts_dir: Path, is_file: Callable[[Path], bool] = Path.is_file
) -> Path | None:
    """Return the lint-imports console script installed in ``scripts_dir``, or None.

    Pure on purpose (the existence check is injected) so both platform names can be unit
    tested on any OS. Only ``scripts_dir`` is searched, never the PATH: the contracts must be
    checked by the import-linter of the interpreter that runs the gate (backlog AF-05).

    Args:
        scripts_dir: Where pip installs the running interpreter's console scripts
            (``sysconfig.get_path("scripts")``: ``venv/Scripts`` on Windows, ``bin`` on POSIX).
        is_file: Existence check; ``Path.is_file`` outside tests.

    Returns:
        The first path of ``LINT_IMPORTS_NAMES`` that exists in ``scripts_dir``, or None.
    """
    for name in LINT_IMPORTS_NAMES:
        candidate = scripts_dir / name
        if is_file(candidate):
            return candidate
    return None


def _lint_imports_cmd(
    scripts_dir: Path, is_file: Callable[[Path], bool] = Path.is_file
) -> list[str]:
    """Build the import-linter step: the console script, or a stand-in that fails loudly.

    There is no module fallback: the package's cli module only defines the click command, so
    running it exits 0 having checked nothing. When the script is missing, the stand-in
    prints what to install and exits 1, so ``run()`` marks the step red with the same
    exit-code rule as every other step.

    Args:
        scripts_dir: Directory searched by ``find_lint_imports``.
        is_file: Existence check; ``Path.is_file`` outside tests.

    Returns:
        The command to run for the import-linter step.
    """
    exe = find_lint_imports(scripts_dir, is_file)
    if exe is not None:
        return [str(exe)]
    hint = (
        f"lint-imports not found in {scripts_dir}; install the dev extras in this interpreter: "
        f"{PY} -m pip install -e .[dev]"
    )
    return [PY, "-c", f"import sys; sys.exit({hint!r})"]


def steps(no_tests: bool) -> list[tuple[str, list[str]]]:
    s: list[tuple[str, list[str]]] = [
        ("ruff format --check", [PY, "-m", "ruff", "format", "--check", "."]),
        ("ruff check", [PY, "-m", "ruff", "check", "."]),
        ("mypy", [PY, "-m", "mypy"]),
        ("import-linter", _lint_imports_cmd(Path(sysconfig.get_path("scripts")))),
        ("docs (coherencia)", [PY, "scripts/check_docs.py"]),
    ]
    if not no_tests:
        s.append(
            (
                "pytest + cobertura",
                [PY, "-m", "pytest", "-q", "--cov=app", "--cov-report=term-missing:skip-covered"],
            )
        )
    return s


# Short, stable keys accepted by --soft, mapped to the step names printed in the summary.
STEP_KEYS: dict[str, str] = {
    "format": "ruff format --check",
    "ruff": "ruff check",
    "mypy": "mypy",
    "imports": "import-linter",
    "docs": "docs (coherencia)",
    "tests": "pytest + cobertura",
}


def parse_soft(text: str) -> set[str]:
    """Translate the value of ``--soft`` into the set of step names it tolerates.

    Pure on purpose (no subprocess, no I/O) so the gate's policy can be unit tested.

    Args:
        text: Comma-separated step keys (see ``STEP_KEYS``); may be empty.

    Returns:
        The step names (as printed in the summary) the caller may leave red.

    Raises:
        ValueError: If any key is not in ``STEP_KEYS``; the message lists the offenders.
    """
    keys = [k.strip() for k in text.split(",") if k.strip()]
    unknown = [k for k in keys if k not in STEP_KEYS]
    if unknown:
        raise ValueError(f"unknown --soft key(s): {', '.join(unknown)}")
    return {STEP_KEYS[k] for k in keys}


def verdict(results: dict[str, bool], soft: set[str]) -> tuple[int, list[str]]:
    """Decide the gate's exit code from the step results.

    Every step has already run; this only decides which reds block.

    Args:
        results: Step name -> passed, in execution order.
        soft: Step names allowed to fail without blocking (from ``parse_soft``).

    Returns:
        ``(exit_code, tolerated_red)``: exit code is 1 if any failed step is not in ``soft``,
        else 0; ``tolerated_red`` lists the failed steps that were tolerated, in execution order.
    """
    failed = [name for name, ok in results.items() if not ok]
    tolerated = [name for name in failed if name in soft]
    blocking = [name for name in failed if name not in soft]
    return (1 if blocking else 0), tolerated


def _soft_arg(argv: list[str]) -> str | None:
    """Return the raw value of ``--soft`` (``--soft a,b`` or ``--soft=a,b``), or None if absent.

    Raises:
        ValueError: If ``--soft`` is given without a value.
    """
    for i, arg in enumerate(argv):
        if arg.startswith("--soft="):
            return arg.removeprefix("--soft=")
        if arg == "--soft":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("--soft requires a comma-separated list of step keys")
            return argv[i + 1]
    return None


def run(name: str, cmd: list[str]) -> bool:
    print(f"\n=== {name} ===", flush=True)
    t0 = time.perf_counter()
    code = subprocess.call(cmd)
    dt = time.perf_counter() - t0
    print(f"--- {name}: {'OK' if code == 0 else f'FALLA (exit {code})'} en {dt:.1f}s", flush=True)
    return code == 0


def main(argv: list[str]) -> int:
    _prepare_process()
    fix = "--fix" in argv
    no_tests = "--no-tests" in argv
    try:
        raw_soft = _soft_arg(argv)
        soft = parse_soft(raw_soft) if raw_soft is not None else set()
    except ValueError as exc:
        # Validate before running anything: a typo must not silently tolerate (or hide) a step.
        print(f"check.py: {exc}. Valid keys: {', '.join(STEP_KEYS)}", file=sys.stderr)
        return 2
    print(f"Raíz del repo: {REPO_ROOT} · Python {sys.version.split()[0]}", flush=True)
    if fix:
        subprocess.call([PY, "-m", "ruff", "format", "."])
        subprocess.call([PY, "-m", "ruff", "check", "--fix", "."])
    results = {name: run(name, cmd) for name, cmd in steps(no_tests)}
    code, tolerated = verdict(results, soft)
    print("\n=== RESUMEN ===")
    for name, ok in results.items():
        print(f"  {'✔' if ok else '✘'} {name}{' (soft)' if name in tolerated else ''}")
    if code:
        blocking = [n for n, ok in results.items() if not ok and n not in tolerated]
        print(f"\nCompuerta NO superada: {', '.join(blocking)}")
        return code
    if tolerated:
        print(f"\nCompuerta superada; tolerados en rojo: {', '.join(tolerated)}")
    else:
        print("\nCompuerta superada.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

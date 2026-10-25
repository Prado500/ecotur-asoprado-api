"""Hook PostToolUse: formatea y autocorrige con ruff el archivo .py recién editado.

Claude Code envía por stdin un JSON con `tool_input.file_path`. Si el archivo es Python:
  1. `ruff format <archivo>`  (determinista: el formato nunca se discute)
  2. `ruff check --fix <archivo>`
Si tras el autofix quedan errores, salimos con código 2 y los errores en stderr: Claude Code se los
muestra al agente como feedback y debe corregirlos antes de continuar. Cualquier otro fallo del hook
sale con 0 para no bloquear el trabajo por un problema del propio hook.
"""

from __future__ import annotations

import json
import subprocess
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(".py"):
        return 0
    py = sys.executable
    subprocess.run([py, "-m", "ruff", "format", path], capture_output=True, text=True)
    fix = subprocess.run([py, "-m", "ruff", "check", "--fix", path], capture_output=True, text=True)
    if fix.returncode == 0:
        return 0
    sys.stderr.write(f"ruff sigue reportando errores en {path} tras el autofix:\n{fix.stdout}{fix.stderr}")
    return 2


if __name__ == "__main__":
    sys.exit(main())

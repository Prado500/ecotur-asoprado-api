## Auditoría Fase A — 2026-11-09

**Veredicto Fase A: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase A — La "ejecución inestable" de la duda 1 del handoff no es un test inestable. Es un fallo determinista del paso import-linter cuando el stdout de la compuerta es el dispositivo `NUL` de Windows (`> /dev/null` en Git Bash). El spinner de rich que usa import-linter (`venv/Lib/site-packages/importlinter/application/use_cases.py:127`, `_get_spinner` l.231) detecta una consola heredada, escribe con cp1252 y lanza `UnicodeEncodeError`. El subproceso sale con 1 y la compuerta da exit 1. `check.py` reconfigura a UTF-8 solo sus propios streams (`scripts/check.py:40-41`), y el subproceso no lo hereda. No es una regresión de la fase: el lanzador de pip falla igual. Ningún archivo del repo invoca la compuerta con salida a `NUL`. Destino: backlog/Residuales (p. ej., `PYTHONIOENCODING=utf-8` en el entorno de los pasos, o documentar que no se redirige a `/dev/null` en Windows). Fuera del alcance de AF-12 — evidencia: `check.py --soft ruff,mypy > /dev/null 2>&1` → exit 1 en 3 de 3; `> /dev/null` solo stdout → exit 1 en 2 de 2, con la traza `rich/_win32_console.py:402 … cp1252.py:19 … UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-2` dentro de `<string>, line 1 … lint_imports_command()`; la misma orden a fichero → exit 0 en 6 de 6 (`546 passed`, `Compuerta superada; tolerados en rojo: ruff check, mypy`); a tubería (`| cat > /dev/null`) → exit 0. Sin cambios de la fase: `venv/Scripts/lint-imports.exe > /dev/null` → exit 1 y `> fichero` → exit 0; el entry point con `-c` da los mismos dos resultados. `git grep -E 'check\.py[^|]*(>\s*/dev/null|>\s*NUL)'` → vacío.

Puntos juzgados sin hallazgo:

- **Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, exit 1, con RESUMEN): `✔ ruff format --check`,
  `✘ ruff check` (`Found 8 errors.`, los 8 I001 en `app/` de la línea base), `✘ mypy` (`Found 9 errors in 5 files (checked 53
  source files)`), `✔ import-linter` (`Contracts: 4 kept, 0 broken.`), `✔ docs (coherencia)`, `✔ pytest + cobertura`
  (`546 passed, 5 warnings`, `TOTAL 943 23 138 19 96.11%`), `Compuerta NO superada: ruff check, mypy`. Coincide con
  el criterio de aceptación (`plan.md:235-240`) y con la línea base (`verificacion.md:117,123,146-149`): cobertura igual,
  contratos iguales, ruff/mypy sin aumento. 548 → 546 es la baja prevista y aceptada (`plan.md:76`, E0.2).
- **Archivos tocados:** `ruff check scripts/check.py tests/test_check.py` → `All checks passed!`; `ruff format --check` →
  `2 files already formatted`; `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
- **Commit `6ee6923`:** el mensaje es idéntico al de `plan.md:250-278` (`diff` del bloque del plan frente a
  `git log -1 --format=%B`: solo cambia el salto de línea final que añade git). Toca solo `scripts/check.py` y `tests/test_check.py`
  (`git show --stat`; paso 8 de la Verificación final: `git diff --stat 9d2b589 -- . ':(exclude)docs'` → los mismos 2 archivos).
  `run()` no cambia: el diff no tiene ningún hunk en `scripts/check.py:170-176`, y `subprocess.call(cmd)` sigue sin `try`
  (`:173`). Están todos los cambios exactos: importaciones (`:22-23`), `LINT_IMPORTS_CODE` y `_lint_imports_cmd()` con el
  texto literal del plan (`:48-80`), `steps()` con docstring y `("import-linter", _lint_imports_cmd()),` (`:77-90`). En los tests:
  docstring del módulo, `entry_points` en lugar de `sysconfig` y `TestLintImportsStep` con los 5 casos (`tests/test_check.py:141-205`).
- **Desviación 1 (SIM300) confirmada como forzada y equivalente.** La forma del plan, pasada por ruff con la configuración del
  repo, da `SIM300 [*] Yoda condition detected` (exit 1). La igualdad es simétrica, y MA3 la hace caer
  (`tests/test_check.py:159-161`).
- **Desviación 2 (Smart App Control ya no bloquea):** sin la reproducción "antes rojo / después verde", la evidencia de que
  la fase resuelve el incidente es estructural. Basta: (a) paso 4 de la Verificación final → `True` (todo paso empieza por
  `PY`); (b) test 1 congela `[PY, "-c", LINT_IMPORTS_CODE]` con y sin PATH; (c) experimento del auditor: con
  `venv/Scripts/lint-imports.exe` renombrado temporalmente, `check.py --no-tests --soft ruff,mypy` → `Contracts: 4 kept, 0 broken.`,
  `--- import-linter: OK`, exit 0. La compuerta ya no depende del lanzador, ni bloqueado ni ausente. El binario se restauró
  (`sha256sum -c` OK). Consecuencia para B: MB3 probablemente no reproducirá `WinError 4551`. El plan ya lo prevé (`plan.md:364`).
- **Mutaciones repetidas por el auditor** (helper `mut` del plan): MA1 → `3 failed, 26 passed` (tests 1, 3, 5); MA2 →
  `2 failed, 27 passed` (3, 4); MA3 → `1 failed, 28 passed` (2); MA5 → `2 failed, 27 passed` (1, 4). MA4 (contrato roto real,
  sin venv en PATH) → `Los servicios no conocen el transporte HTTP BROKEN`, `Contracts: 3 kept, 1 broken.`,
  `--- import-linter: FALLA (exit 1)`, `exit 1`. Restauración byte a byte: `sha256sum -c` OK en `scripts/check.py` y
  `app/services/user_service.py`, y `git status --short` vacío.
- **Verificación final, pasos aplicables tras A:** paso 1 vacío; paso 2 vacío y `tests/test_check.py:2`; paso 3
  `2/2 · 2/3 · 2/2 · 2/2` como espera el plan.
- **`progress.json`:** JSON válido; `Fase_A` `completed` con `6ee6923` (hash real, `git show --stat` lo confirma);
  `current_target` `Fase_B`; `last_handoff` presente; `edit_rules` intacto. El registro va en commit aparte (`13a060d`), que toca
  solo `progress.json` y `handoff-Fase_A.md`.
- **Árbol:** `git status --short` limpio al empezar y al terminar la auditoría (salvo este `gaps.md`).
- **AGENTS:** docstrings Google en `_lint_imports_cmd` y `steps()`. Ninguna aserción sobre texto en español. Los tests no
  usan `Mock`: `find_spec` se sustituye con funciones puras vía `monkeypatch`, así que `spec=` no aplica. `check.py` está fuera
  de las capas de `import-linter`.

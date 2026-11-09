# Handoff — AF-12 · Fase B: un paso que no arranca sale en rojo y la compuerta sigue (AF-13)

- **Commit de la fase:** `5cbdec1` — `fix(check): mark a step that cannot start red instead of aborting`. El mensaje es
  idéntico al del plan: `diff` de `plan.md:377-398` frente a `git log -1 --format=%B` → sin diferencias.
- **Rama / base:** `item/af-12`; `git fetch origin` OK; `origin/develop` = `merge-base HEAD origin/develop` = `bb03f46`
  (= `Base develop` de `verificacion.md:103`).
- **Fecha:** 2026-11-09.

## Archivos tocados

```
$ git show --stat 5cbdec1
 scripts/check.py    | 27 ++++++++++++++++++++++++---
 tests/test_check.py | 51 +++++++++++++++++++++++++++++++++++++++++++++++----
 2 files changed, 71 insertions(+), 7 deletions(-)
```

- `scripts/check.py`: `run()` con el texto literal del plan (`plan.md:286-313`): docstring Google, `try/except OSError`
  alrededor de `subprocess.call`, aviso `check.py: cannot start <cmd[0]>: <exc>` en stderr, paso `FALLA (<tipo>)` y `False`.
  En la rama `else`, `OK` o `FALLA (exit N)` como antes. No se toca nada más: ni `--fix`, ni `steps()`, ni `main()`.
- `tests/test_check.py`: el docstring del módulo del plan (`plan.md:318-324`) y la clase `TestRunReportsUnstartableStep` (tests 6,
  7 y 8 del plan), después de `TestLintImportsStep`, con el docstring del plan.

## Arranque (antes de tocar nada)

`git status --short` vacío. `current_target` = `Fase_B`. `./venv/Scripts/python.exe scripts/check.py` → exit 1, con RESUMEN:
`Found 8 errors.` · `Found 9 errors in 5 files (checked 53 source files)` · `Contracts: 4 kept, 0 broken.` ·
`546 passed, 5 warnings` · `TOTAL 943 23 138 19 96.11%` · `Compuerta NO superada: ruff check, mypy`. Coincide con la línea base
de la fase A (auditada en `gaps.md`).

## TDD

- **RED** (tests 6-8 y docstring escritos antes de tocar `check.py`): `2 failed, 30 passed in 1.22s`, como el plan.
  - `test_unstartable_command_is_a_red_step` y `test_main_runs_later_steps_and_prints_summary`:
    `FileNotFoundError: [WinError 2] The system cannot find the file specified` (sale de `subprocess.call`).
  - `test_command_that_runs_and_fails_reports_its_exit_code`: pasa antes y después (test de guarda).
- **GREEN:** `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `32 passed in 0.80s`.

## Mutaciones (helper `mut` del plan; restauración verificada con `sha256sum -c` tras cada una)

| Mutante | Resultado | Esperado | Tests que fallan |
|---|---|---|---|
| MB1 `except ValueError as exc:` | `2 failed, 30 passed` | 2 (6, 7) | `test_unstartable_command_is_a_red_step`, `test_main_runs_later_steps_and_prints_summary` |
| MB2 `else "FALLA"` | `1 failed, 31 passed` | 1 (8) | `test_command_that_runs_and_fails_reports_its_exit_code` |

`sha256sum -c` → `scripts/check.py: OK` tras MB1, MB2, MB3 y la variante de MB3.

**MB3 (el incidente real): no reproduce `WinError 4551`.** Smart App Control ya no bloquea `venv/Scripts/lint-imports.exe` en esta
máquina (ya lo anotaron el handoff y la auditoría de A). El guion del plan, tal cual, corre el lanzador y sale en verde:

```
=== import-linter ===
...
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s

=== docs (coherencia) ===
...
--- docs (coherencia): OK en 0.1s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)

Compuerta NO superada: ruff check, mypy
exit 1
```

Como prevé `plan.md:364`, la evidencia son los tests 6 y 7 (y MB1). **Evidencia complementaria** (fuera del guion del plan, no
commiteada): el mismo guion de MB3, pero con el paso apuntando a `lint-imports-absent.exe`, que no existe. Así se ejercita el mismo
camino `OSError` con la compuerta real de extremo a extremo:

```
=== import-linter ===
check.py: cannot start C:\projects\ecotur-asoprado\venv\Scripts\lint-imports-absent.exe: [WinError 2] The system cannot find the file specified
--- import-linter: FALLA (FileNotFoundError) en 0.0s

=== docs (coherencia) ===
Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).
--- docs (coherencia): OK en 0.1s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✘ import-linter
  ✔ docs (coherencia)

Compuerta NO superada: ruff check, mypy, import-linter
exit 1
```

En los dos casos, `git status --short scripts/` mostró ` M scripts/check.py` porque se corrieron antes del commit de la fase:
es el cambio de la propia fase. `sha256sum -c` confirma que el archivo volvió byte a byte a la versión de la fase.

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` (salida a fichero del scratchpad, no a `/dev/null`) → **exit 1, con RESUMEN**:

```
--- ruff format --check: OK en 0.1s
Found 8 errors.
--- ruff check: FALLA (exit 1) en 0.1s
Found 9 errors in 5 files (checked 53 source files)
--- mypy: FALLA (exit 1) en 0.5s
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
--- docs (coherencia): OK en 0.1s
TOTAL                                        943     23    138     19  96.11%
549 passed, 5 warnings in 18.47s
--- pytest + cobertura: OK en 21.1s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

- pytest: **549 passed, 0 failed** (546 + 3, como el plan). Cobertura: **96.11 %** (= línea base).
- Contratos: **4 KEPT, 0 BROKEN** (= línea base).
- ruff: 8 · mypy: 9 en 5 archivos (= línea base; deuda A4/BE-32, no tocada).
- Archivos tocados: `ruff check scripts/check.py tests/test_check.py` → `All checks passed!`; `ruff format --check` →
  `2 files already formatted`; `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
- `./venv/Scripts/python.exe scripts/check.py --soft ruff,mypy` → exit 0, `549 passed, 5 warnings`,
  `Compuerta superada; tolerados en rojo: ruff check, mypy`.

## Verificación final (pasos que puede correr el ejecutor)

- Paso 1: vacío. Paso 2: vacío y `tests/test_check.py:2`.
- Paso 3: `check.py:2 test_check.py:2` · `check.py:2 test_check.py:3` · `check.py:2 test_check.py:2` · `check.py:2 test_check.py:2`
  (= lo esperado).
- Paso 4: `True`.
- Paso 8 (`git diff --stat 9d2b589 -- . ':(exclude)docs'`): `AGENTS.md | 6`, `scripts/check.py | 96`, `tests/test_check.py | 123`.
  `AGENTS.md` entra por el commit de documentos de David (`3e47d99`, el único commit que toca `AGENTS.md` desde `9d2b589`),
  que E0.6 adelantó antes de esta fase. El paso 8 del plan se escribió con ese commit al final. Ninguna fase tocó `AGENTS.md`.
- Paso 9: `32 passed`, `Found 8 errors.`, `Found 9 errors in 5 files`. Pasos 10 y 11: ver Compuerta de salida.
- Paso 12: vacío (el commit de David ya está en la rama).
- Pasos 5, 6 y 7: no cambian con B (son del mecanismo de A); no los repetí.

## Desviaciones del plan

1. **MB3 no reproduce el bloqueo** (SAC ya no bloquea el lanzador). Queda anotada, como prevé `plan.md:364`. Añadí una variante con
   un lanzador inexistente como evidencia complementaria; no cambia nada commiteado.
2. **Paso 8 de la Verificación final** muestra `AGENTS.md` por el momento del commit de David (E0.6). No es un cambio de esta fase.
3. **`progress.json`:** `current_target` pasa a `null` porque no hay fase siguiente; es la convención de los otros 12 ítems
   cerrados en `docs/deuda/`.

## Residuales

- Los del plan (`plan.md:462-473`) no cambian: `--fix` sigue sin capturar `OSError` (AF-14 sugerida, E0.4), el docstring de uso con
  `python` a secas, `ruff.exe` vía `python -m ruff` y la mezcla de idiomas en la salida (la línea nueva en stderr está en inglés).
- El OPCIONAL de `gaps.md` (import-linter con stdout a `NUL` en Windows, cp1252) sigue igual y fuera de alcance. Por eso las
  compuertas de esta sesión se guardaron en un fichero o se pasaron por tubería, nunca a `/dev/null`.

## Dudas

Ninguna abierta.

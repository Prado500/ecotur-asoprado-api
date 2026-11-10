# Handoff — AF-12 · Fase A: import-linter por su entry point, o paso en rojo con el hint

- **Commit de la fase:** `6ee6923` — `fix(check): run import-linter via its entry point, not pip's launcher` (mensaje exacto
  del plan).
- **Rama / base:** `item/af-12`; `git fetch origin` OK; `origin/develop` = `merge-base HEAD origin/develop` = `bb03f46`
  (= `Base develop` de `verificacion.md`).
- **Fecha:** 2026-11-09.

## Archivos tocados

```
$ git show --stat 6ee6923
 scripts/check.py    | 69 ++++++++++++++++----------------------------
 tests/test_check.py | 82 +++++++++++++++++++++++++++++++----------------------
 2 files changed, 73 insertions(+), 78 deletions(-)
```

- `scripts/check.py`: fuera `import sysconfig` y `from collections.abc import Callable`; entra
  `from importlib.util import find_spec`. `LINT_IMPORTS_NAMES`, `find_lint_imports` y el `_lint_imports_cmd(scripts_dir, is_file)`
  de AF-05 se sustituyen por `LINT_IMPORTS_CODE` y `_lint_imports_cmd() -> list[str]`, con el texto literal del plan. En `steps()`
  queda `("import-linter", _lint_imports_cmd()),` y la función recibe el docstring del plan. `run()` no se toca (fase B).
- `tests/test_check.py`: docstring del módulo del plan; fuera `import sysconfig`, entra
  `from importlib.metadata import entry_points`; `TestLintImportsResolution` (7 casos) pasa a ser `TestLintImportsStep` (5 casos 1-5 del plan).

## Arranque (antes de tocar nada)

`./venv/Scripts/python.exe scripts/check.py` → exit 1, **terminó con RESUMEN**:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

`Found 8 errors.` · `Found 9 errors in 5 files (checked 53 source files)` · `Contracts: 4 kept, 0 broken.` ·
`548 passed, 5 warnings` · `TOTAL 943 23 138 19 96.11%`.

**Diferencia con la verificación:** el 9 nov por la mañana la compuerta abortaba con `OSError [WinError 4551]`. En esta sesión,
`venv/Scripts/lint-imports.exe --help` → exit 0: Smart App Control ya no bloquea el lanzador desde esta shell (lo midió así el
ejecutor, causa no investigada). Los números son iguales a la medición complementaria de la verificación (548 · 96.11 % ·
4 kept · ruff 8 · mypy 9), no peores, así que no hay motivo para detenerse. Efecto para la fase B: probablemente MB3 no reproduzca
el bloqueo. El plan ya lo prevé (l.364): se anota y los tests 6 y 7 son la evidencia.

## TDD

- **RED** (los 5 tests escritos antes de tocar `check.py`): `5 failed, 24 passed in 0.73s`, como el plan.
  - 1 y 2: `AttributeError: module 'check' has no attribute 'LINT_IMPORTS_CODE'`.
  - 3 y 4: `AttributeError: <module 'check' …> has no attribute 'find_spec'`.
  - 5: `TypeError: _lint_imports_cmd() missing 1 required positional argument: 'scripts_dir'`.
- **GREEN:** `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `29 passed in 0.62s`.

## Mutaciones (helper `mut` del plan; última línea de cada una y tests que caen)

| Mutante | Resultado | Esperado | Tests que fallan |
|---|---|---|---|
| MA1 `find_spec("import_linter")` | `3 failed, 26 passed` | 3 (1, 3, 5) | `test_step_is_the_entry_point_regardless_of_path`, `test_missing_package_yields_failing_command_with_install_hint`, `test_entry_point_without_the_package_on_sys_path_is_red` |
| MA2 `if True:` | `2 failed, 27 passed` | 2 (3, 4) | `…_yields_failing_command_with_install_hint`, `test_missing_package_makes_the_gate_step_red` |
| MA3 grupo click `import_linter()` | `1 failed, 28 passed` | 1 (2) | `test_code_calls_the_registered_console_script` |
| MA5 `[PY, "-c", "pass"]` | `2 failed, 27 passed` | 2 (1, 4) | `test_step_is_the_entry_point_regardless_of_path`, `test_missing_package_makes_the_gate_step_red` |

Tras cada una: `git diff --stat` igual al de la fase (69/82 líneas) y `scripts/check.py` sin `\r` (restaurado byte a byte desde el
`.bak`).

**MA4** (contrato roto real, `env -u VIRTUAL_ENV PATH="$NOVENV_PATH" … --no-tests --soft format,ruff,mypy`):

```
Capas: api -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP BROKEN
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 3 kept, 1 broken.
…
app.services is not allowed to import fastapi:

-   app.services.user_service -> fastapi (l.430)


--- import-linter: FALLA (exit 1) en 0.2s
exit 1
```

`git status --short app/` después: vacío.

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` → **exit 1, con RESUMEN**:

```
--- ruff format --check: OK en 0.1s
Found 8 errors.
--- ruff check: FALLA (exit 1) en 0.1s
Found 9 errors in 5 files (checked 53 source files)
--- mypy: FALLA (exit 1) en 0.7s
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
--- docs (coherencia): OK en 0.1s
TOTAL                                        943     23    138     19  96.11%
546 passed, 5 warnings in 17.92s
--- pytest + cobertura: OK en 20.5s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

- pytest: **546 passed, 0 failed** (548 − 2, como prevé el plan). Cobertura: **96.11 %** (= línea base).
- Contratos: **4 KEPT, 0 BROKEN** (= línea base).
- ruff: 8 (todos I001, en `app/`: `api/dependencies.py`, `api/routers/audit.py`, `core/email.py`, `db/database.py`,
  `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`, `services/user_service.py`) = línea base.
  mypy: 9 en 5 archivos = línea base. Deuda A4/BE-32, no tocada.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
  `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
- `./venv/Scripts/python.exe scripts/check.py --soft ruff,mypy` → exit 0,
  `Compuerta superada; tolerados en rojo: ruff check, mypy` (546 passed). Ver la duda 1.

## Evidencia adicional (pasos de la Verificación final aplicables tras A)

- Paso 1 (`lint-imports\.exe|LINT_IMPORTS_NAMES|find_lint_imports|sysconfig` en `scripts tests`): vacío.
- Paso 2: `"importlinter\.cli" not in` vacío; `"importlinter\.cli" in` → `tests/test_check.py:2`.
- Paso 4 (todos los pasos empiezan por `PY`): `True`.
- Paso 5 (intérprete sin dev extras): `C:/Python314/python.exe scripts/check.py --no-tests` →
  `importlinter is not importable by C:\Python314\python.exe; install the dev extras in this interpreter: C:\Python314\python.exe -m pip install -e .[dev]`
  y `--- import-linter: FALLA (exit 1) en 0.0s`.
- Paso 8 (`git diff --stat 9d2b589 -- . ':(exclude)docs'`): solo `scripts/check.py` y `tests/test_check.py`.

## Desviaciones del plan

1. **Test 2, orden de los operandos.** El plan dicta `assert check.LINT_IMPORTS_CODE == f"…"`. El hook de ruff
   (`ruff check --fix`, regla SIM300 "Yoda condition": trata `LINT_IMPORTS_CODE`, en mayúsculas, como constante) lo reescribió
   como `assert (f"from {script.module} import {script.attr}; {script.attr}()" == check.LINT_IMPORTS_CODE)`. La comparación es
   la misma (MA3 lo confirma). No lo revierto: la forma del plan no pasaría `ruff check`.
2. Sin más desviaciones. Durante la edición, el hook borró `from importlib.metadata import entry_points` (F401: la primera
   edición añadía la importación antes que su uso) y se volvió a añadir. El commit la incluye.

## Residuales

- Los del plan (l.462-473) no cambian. La fase A no añade ninguno.
- Smart App Control ya no bloquea `lint-imports.exe` en esta sesión (ver Arranque). Esto no invalida AF-12: el lanzador sigue
  siendo un binario por máquina sin firma. Pero MB3 de la fase B seguramente quede "anotada" en lugar de reproducida.

## Dudas

1. **Una ejecución de `scripts/check.py --soft ruff,mypy` sin explicar.** La primera vez, con la salida a `/dev/null`, dio
   `exit 1`. Después repetí la misma orden cuatro veces seguidas, guardando la salida, y las cuatro dieron `exit 0`, con
   `546 passed` y `Compuerta superada; tolerados en rojo: ruff check, mypy`. No guardé la salida de la primera, así que no
   puedo decir qué paso falló. No volvió a ocurrir. Si el auditor lo ve otra vez, conviene mirar si hay algún test inestable
   en la suite. Los tests de esta fase son deterministas: subprocesos `-c`/`-S` y nada de red ni de reloj.

# Handoff AF-05 · Fase A — lint-imports desde el directorio de scripts del intérprete, o paso en rojo

- **Fecha:** 2026-11-03 · **Rama:** `item/af-05` · **Commit de la fase:** `bd9b8c7`
  (`fix(check): run lint-imports from the scripts dir or fail the step`, mensaje literal del plan + trailer)
- **Base develop:** `217e58f` (`git fetch origin` OK; `origin/develop` = `merge-base HEAD origin/develop` = `217e58f`).
- **Intérprete:** `./venv/Scripts/python.exe` (Python 3.14.3) en toda la sesión.

## Archivos tocados

```
 scripts/check.py    | 64 ++++++++++++++++++++++++++++++++++++++++++++++-------
 tests/test_check.py | 62 +++++++++++++++++++++++++++++++++++++++++++++++++--
 2 files changed, 116 insertions(+), 10 deletions(-)
```

- `scripts/check.py`: sale `import shutil`; entran `import sysconfig` y `from collections.abc import Callable`.
  `LINT_IMPORTS_NAMES = ("lint-imports.exe", "lint-imports")`, `find_lint_imports(scripts_dir, is_file)` y
  `_lint_imports_cmd(scripts_dir, is_file)` con las firmas y el `-c sys.exit(...)` del plan. En `steps()`:
  `("import-linter", _lint_imports_cmd(Path(sysconfig.get_path("scripts")))),`. `ruff format` partió las dos firmas en
  tres líneas; la línea de `steps()` quedó en una. Nada más del archivo cambia (`run()`, `main()`, `verdict`, etc.).
- `tests/test_check.py`: docstring del módulo (política `--soft` + resolución de lint-imports; el único subproceso es
  el sustituto), `import subprocess`, `import sysconfig` y `class TestLintImportsResolution` (`BIN = Path("/fake/bin")`)
  con los 6 tests / 7 casos y los nombres exactos del plan (enmienda 4).

## RED → GREEN

RED (tests escritos, `scripts/check.py` aún sin tocar):

```
E       AssertionError: assert 'importlinter.cli' not in ['C:\\projects\\ecotur-asoprado\\venv\\Scripts\\python.exe', '-m', 'importlinter.cli', 'lint_imports']
E       AttributeError: module 'check' has no attribute 'find_lint_imports'
E       AttributeError: module 'check' has no attribute 'find_lint_imports'
E       AttributeError: module 'check' has no attribute 'find_lint_imports'
E       TypeError: _lint_imports_cmd() takes 0 positional arguments but 2 were given
E       TypeError: _lint_imports_cmd() takes 0 positional arguments but 1 was given
E       TypeError: _lint_imports_cmd() takes 0 positional arguments but 1 was given
FAILED tests/test_check.py::TestLintImportsResolution::test_step_resolves_from_scripts_dir_regardless_of_path
FAILED tests/test_check.py::TestLintImportsResolution::test_finds_console_script_in_scripts_dir[windows]
FAILED tests/test_check.py::TestLintImportsResolution::test_finds_console_script_in_scripts_dir[posix]
FAILED tests/test_check.py::TestLintImportsResolution::test_looks_only_inside_the_scripts_dir
FAILED tests/test_check.py::TestLintImportsResolution::test_found_tool_is_invoked_directly
FAILED tests/test_check.py::TestLintImportsResolution::test_missing_tool_yields_failing_command_with_install_hint
FAILED tests/test_check.py::TestLintImportsResolution::test_missing_tool_makes_the_gate_step_red
7 failed, 24 passed in 0.73s
```

El test 1 falla por aserción con el no-op `[PY, '-m', 'importlinter.cli', 'lint_imports']`, como predice el plan.

GREEN: `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `31 passed in 0.50s`.

## Mutaciones (sobre la punta de la fase, por Bash, restauradas)

```
== MA1   ("lint-imports.exe",)
FAILED ...::test_finds_console_script_in_scripts_dir[posix]
FAILED ...::test_looks_only_inside_the_scripts_dir
FAILED ...::test_found_tool_is_invoked_directly
3 failed, 28 passed in 0.69s
== MA2   vuelve el fallback -m importlinter.cli
FAILED ...::test_missing_tool_yields_failing_command_with_install_hint
FAILED ...::test_missing_tool_makes_the_gate_step_red
2 failed, 29 passed in 0.68s
== MA3   _lint_imports_cmd(Path.cwd())
FAILED ...::test_step_resolves_from_scripts_dir_regardless_of_path
1 failed, 30 passed in 0.61s
== restore
scripts/check.py: OK          (sha256sum -c contra el hash previo)
```

MA4 (`import fastapi` añadido a `app/services/user_service.py`; compuerta `--no-tests` con `env -u VIRTUAL_ENV` y un
`PATH` sin el venv, comprobado: 0 entradas `ecotur` en `NOVENV_PATH`):

```
Los servicios no conocen el transporte HTTP BROKEN
Contracts: 3 kept, 1 broken.
app.services is not allowed to import fastapi:
-   app.services.user_service -> fastapi (l.424)
--- import-linter: FALLA (exit 1) en 0.2s
exit 1
```

Restauración: `sha256sum` antes y después = `dd99df12a252393dbdc3d5515c6898416cf647867b4bbfcd44a7f1c895e83722`;
`git hash-object` = `git rev-parse HEAD:app/services/user_service.py` = `6f709fc8…`; `git status --short app/` vacío.

## Criterios de aceptación

- Compuerta **sin el venv en el PATH** (`env -u VIRTUAL_ENV PATH="$NOVENV_PATH" … --no-tests`): 4 contratos `KEPT`,
  `Contracts: 4 kept, 0 broken.` y `--- import-linter: OK en 0.2s` (antes del cambio: OK vacío).
- Intérprete sin la herramienta (`C:/Python314/python.exe scripts/check.py --no-tests`):
  ```
  === import-linter ===
  lint-imports not found in C:\Python314\Scripts; install the dev extras in this interpreter: C:\Python314\python.exe -m pip install -e .[dev]
  --- import-linter: FALLA (exit 1) en 0.0s
  ```
- Trinquete en los dos archivos: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already
  formatted`; `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
  Totales: `Found 60 errors.` (ruff) y `Found 10 errors in 5 files (checked 35 source files)` (mypy).

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1 por deuda heredada)

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

| Métrica | Línea base (verificación) | Arranque de esta fase | Tras la fase | Plan exige |
|---|---|---|---|---|
| pytest | 369 passed | 369 passed | **376 passed**, 0 failed | 376 passed |
| Cobertura | 94.81 % | 94.81 % | **94.81 %** | ≥ 94.81 % |
| ruff format | 52 already formatted | igual | 52 already formatted | OK |
| ruff check (total) | Found 60 errors. | 60 | **Found 60 errors.** | 60 |
| mypy (total) | 10 errors in 5 files | 10 | **Found 10 errors in 5 files** | 10 |
| import-linter | Contracts: 4 kept, 0 broken. | igual | **Contracts: 4 kept, 0 broken.** | 4 kept |

## Verificación final del plan (greps)

- 1: `grep importlinter\.cli|shutil\.which` en `scripts/check.py` y en `scripts app alembic .claude .azure-pipelines
  pyproject.toml` → vacío · vacío.
- 2: `sysconfig.get_path("scripts")` → **2 líneas**, no 1: la 109 (`steps()`) y la 64, que es el docstring de
  `find_lint_imports` copiado tal cual del plan (``(``sysconfig.get_path("scripts")``: ``venv/Scripts`` …)``).
  Discrepancia del propio plan entre su bloque de código y su grep esperado; no es un defecto. `Path(PY).parent` /
  `Path(sys.executable).parent` → vacío; `shutil` → vacío.
- 3: solo `scripts/check.py` (nombres, funciones, mensaje y `steps()`), `tests/test_check.py` (con `importlinter.cli`
  solo en aserciones negativas) y `pyproject.toml` (`[tool.importlinter]`). Además salen dos `.pyc` de `__pycache__`
  (ignorados por git).
- 6: `git diff 217e58f --stat` muestra, además de `scripts/check.py`, `tests/test_check.py` y `docs/deuda/AF-05/`,
  `docs/backlog.md` (commit `490d40c`, anterior al plan) y `docs/bitacora/2026-11-03.md` (commit `490d40c` + cambios
  sin commitear de David). Ninguno es de esta fase; la bitácora no se tocó ni se añadió a ningún commit.

## Residuales y dudas

1. **Grep 2 del plan:** espera 1 línea y da 2 por el docstring que el propio plan fija. El auditor puede ajustar la
   expectativa; cambiar el docstring no aporta nada.
2. **Hook de ruff (AF-06):** el hook con el ruff del `PATH` quitó los imports `subprocess`/`sysconfig` por F401 mientras
   aún no se usaban (edición en pasos). Se repusieron y después se pasó `./venv/Scripts/python.exe -m ruff format` y
   `ruff check --fix` sobre los dos archivos: `2 files left unchanged` / `All checks passed!`.
3. **Docstring de `_lint_imports_cmd`:** lleva además `Args`/`Returns` (Google Style, AGENTS §4); la redacción era
   orientativa en el plan y no contiene `importlinter.cli`.
4. **Pendiente de David:** MD1 (log del CI del PR de `item/af-05`: los 4 contratos y `Contracts: 4 kept, 0 broken.`
   bajo `=== import-linter ===`). Siguiente paso de agente: `/auditar AF-05 Fase_A`.
5. Residuales 1-3 del plan sin cambios (run() solo confía en el exit code; mitigación caducada en documentos;
   salida bilingüe de `check.py`).

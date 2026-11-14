# Handoff — BE-34 · Fase A (BE-47: `TEST_ENVIRONMENT` cubre todo `Settings`)

- Commit de la fase: `d873b49` — `test(config): require a test value for every Settings field (BE-47)` (mensaje exacto
  del plan).
- Rama: `item/be-34`, sobre `c0e9096` (plan aprobado entero: E0, E1, E2, E3).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas: ninguna cambia la fase A (E0, E2 y E3 la dejan "como está escrita").

## Ritual de arranque

- `git status --short`: limpio. HEAD `c0e9096`. `current_target` = `Fase_A`. Sin `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), idéntica a la línea base de la verificación (fila Base del plan):
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `638 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`.

## Archivos tocados (el único de la fase)

`git show --stat --format= d873b49`:

```
 tests/test_config.py | 9 +++++++++
 1 file changed, 9 insertions(+)
```

`git show --numstat --format= d873b49` → `9	0	tests/test_config.py` (criterio de aceptación).

Resumen del diff, todo dictado por el plan:

1. `import runpy` como primera línea de los imports de la biblioteca estándar, antes de
   `from collections.abc import Callable`.
2. `ROOT_CONFTEST = Path(__file__).resolve().parents[1] / "conftest.py"` justo tras `ENV_EXAMPLE = …`, sin línea en blanco.
3. Al final, con dos líneas en blanco antes, `test_test_environment_fixes_every_setting` con el texto exacto del plan.

`conftest.py`, `REQUIRED`/`OPTIONAL_DEFAULTS` y la clase nueva (fase C): sin tocar.

`git grep -n 'TEST_ENVIRONMENT' -- tests | wc -l` → `1` (criterio de aceptación).

## Tests (RED → GREEN)

- **RED** (procedimiento del plan, en el árbol de trabajo, antes del commit): borrada la línea
  `    "CORS_ORIGINS": "http://localhost:3000",` de `conftest.py` y ejecutado
  `./venv/Scripts/python.exe -m pytest tests/test_config.py -q -p no:cacheprovider -rf`:

  ```
  FAILED tests/test_config.py::test_test_environment_fixes_every_setting - Asse...
  1 failed, 23 passed in 0.54s
  ```

  `conftest.py` restaurado desde una copia en el scratchpad (no con git); `git status --short` tras restaurar:
  ` M tests/test_config.py` (solo el archivo de la fase).
- **GREEN**: `tests/test_config.py` → `24 passed in 0.34s`.

## Mutante MA (procedimiento común, sobre `git archive` del commit `d873b49`)

Directorio nuevo en el scratchpad (`mutant_MA`), edición exacta de la tabla (borrar la línea de `CORS_ORIGINS` de
`conftest.py`; `grep -c CORS_ORIGINS` → `0`), suite sin `test_check*`:

```
FAILED tests/test_config.py::test_test_environment_fixes_every_setting - Asse...
1 failed, 349 passed, 8 warnings in 11.68s
```

Igual a la tabla (`1 failed, 349 passed`). Muerto. Copia limpia del mismo commit, sin mutante (otro directorio nuevo,
`copy_A_clean`): `350 passed, 8 warnings in 11.21s` (columna "Suite de la copia" de la fila A).

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` → **exit 0**.

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `639 passed, 8 warnings in 17.01s` (0 failed).
- Cobertura: `TOTAL 965 19 136 16 96.82%` (= línea base).
- ruff format: `61 files already formatted` · ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.`
- docs: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- Sobre el archivo tocado: `ruff check` → `All checks passed!`; `ruff format --check` → `1 file already formatted`;
  `mypy tests/test_config.py` → `Success: no issues found in 1 source file`.

Coincide con la fila A de la tabla de la compuerta (639 · 96,82 % (965) · 61 files · 56 source files · 350).

## Checklist `test-sanitizer` (solo checklist)

Test nuevo de borde sin mocks ni fábricas (lee un dato estático del `conftest.py` de la raíz); aserción sobre conjuntos
de claves, sin texto en español; docstring con la categoría ("Edge case"). Ningún test existente reescrito.

## Residuales y dudas

- Incidencia de proceso, sin efecto en el resultado: el hook de `ruff --fix` borró `import runpy` (F401) al aplicar la
  primera edición, antes de que existiera el test que lo usa; se volvió a añadir en la misma línea dictada. El diff
  final es el del plan (`9 0`).
- `runpy.run_path` ejecuta también el `os.environ.update(TEST_ENVIRONMENT)` del `conftest.py` de la raíz; reescribe las
  mismas claves con los mismos valores, así que no altera el entorno de la suite. Leído, no es hallazgo.
- Sin desviaciones respecto del plan.

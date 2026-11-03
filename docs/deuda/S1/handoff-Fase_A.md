# Handoff S1 Fase A

Commit: `a30795a test(models): freeze the ORM schema before the Mapped migration`
Base develop re-comprobada: `origin/develop` = merge-base = HEAD = `b421268` (fetch correcto).

## Archivos tocados
- `tests/test_models_schema.py` (nuevo). Nada en `app/`: las mutaciones se restauraron (`git status` sin cambios en `app/`).

## Diff (`git show --stat HEAD`)
```
 tests/test_models_schema.py | 158 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 158 insertions(+)
```

## Tests
`./venv/Scripts/python.exe -m pytest -q tests/test_models_schema.py` -> `7 passed in 0.10s` (verdes sobre los modelos actuales, por diseño).
`ruff check tests/test_models_schema.py` -> `All checks passed!`; `mypy tests/test_models_schema.py | grep '^tests'` -> vacío.

## Mutaciones (ultima línea de pytest de cada una)
- MA1: `1 failed, 6 passed in 0.27s`
- MA2: `2 failed, 5 passed in 0.23s`
- MA3: `1 failed, 6 passed in 0.21s`
- MA4: `1 failed, 6 passed in 0.22s`

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`)
```
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff format --check, ruff check, mypy
```
- pytest: `367 passed, 5 warnings in 16.63s` (línea base 360)
- Cobertura: `TOTAL 934 34 136 22 94.77%` (línea base 94.77 %)
- ruff check: `Found 82 errors.` (línea base 82) · mypy: `Found 44 errors in 12 files (checked 35 source files)` (línea base 44)
- `./venv/Scripts/lint-imports.exe` -> `Contracts: 4 kept, 0 broken.`

## Residuales
1. `ruff format --check` falla (1 file would be reformatted): es `docs/deuda/S1/plan.md` (sin commitear), cuyos bloques ```python el ruff 0.17.2 del venv quiere reformatear (líneas de más de 100 columnas en el plan). No es código; la línea base de la verificación decía ✔ porque `plan.md` aún no existía. Antes de mi cambio ya fallaba igual (148 files already formatted + 1). El archivo `plan.md` no es mío y no lo toqué. Decisión de David: dejar o reformatear los bloques; en cuanto `plan.md` se commitee, la compuerta local queda con este rojo hasta que se resuelva.
2. `docs/bitacora/2026-11-03.md`, `docs/deuda/S1/plan.md` y `verificacion.md` siguen sin commitear (no son de la fase); en este commit docs solo entran `progress.json` y este handoff.

## Dudas
Ninguna bloqueante. Fase B requiere M0 de David (`alembic current` y `alembic check`, salida a la bitácora).

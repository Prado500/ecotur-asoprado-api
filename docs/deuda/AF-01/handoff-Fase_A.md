# Handoff AF-01 Fase A

Commit: `8d51302` refactor(flow): make check_docs.py testable with --root and reject unknown flags
Base develop: `2647ea3` (origin/develop y merge-base coinciden; fetch hecho).

## Archivos tocados
```
 pyproject.toml           |   2 +-
 scripts/check_docs.py    | 178 +++++++++++++++++++++++++++++++++++++----------
 tests/test_check_docs.py | 129 ++++++++++++++++++++++++++++++++++
 3 files changed, 273 insertions(+), 36 deletions(-)
```

## Compuerta (antes = despues, salvo tests)
```
=== RESUMEN ===
  x ruff format --check   (27 files would be reformatted)
  x ruff check            (Found 362 errors)
  x mypy                  (Found 44 errors in 12 files, checked 34 source files)
  v import-linter
  v docs (coherencia)
  v pytest + cobertura
```
pytest: 171 passed (145 + 26 nuevos); cobertura TOTAL 93 %.
ruff y mypy sobre `scripts/check_docs.py` y `tests/test_check_docs.py`: 0 errores. Los totales no subieron.
RED verificado: 26 failed antes de implementar; 26 passed despues.
Verificado: `check_docs.py` exit 0; `--copias` exit 2 con uso; sin `os.chdir`.

## Residuales / notas
- El plan lista "8 tests"; hay 26 casos por parametrizacion (8 formas de cita x con/sin backticks, etc.) mas un test extra `test_main_on_fixture_with_error_returns_1`.
- Formato de error unificado ya aplicado a R1-R4 (`archivo:linea: R#: ...`), sin cambiar la deteccion.
- `progress.json` se reserializo con `json.dump` (el arreglo `allowed_statuses` quedo multilinea); sin cambio semantico.
- Los fixtures autouse de conftest no causaron problemas (tests en 0.3 s).

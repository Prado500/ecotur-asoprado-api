# Handoff BE-01 Fase B

Commit de código: `867e56c` (fix(storage): raise domain errors and copy blobs synchronously). Base develop `8bf9815` vigente (origin/develop y merge-base coinciden).

## Archivos tocados
app/core/exceptions.py, app/main.py, app/core/storage.py, tests/test_domain_error_handler.py, tests/test_storage.py.

```
 app/core/exceptions.py             | 115 +++++++++++++--------
 app/core/storage.py                | 142 +++++++++++++++++++-------
 app/main.py                        |  69 ++++++++-----
 tests/test_domain_error_handler.py |  16 ++-
 tests/test_storage.py              | 203 ++++++++++++++++++++++++++++++++++---
 5 files changed, 423 insertions(+), 122 deletions(-)
```

## Línea base (antes) -> después
- pytest: 116 passed -> 135 passed. Cobertura total 89 % -> 93 %; `app/core/storage.py` 28 % -> 100 %.
- import-linter: 3 kept / 1 broken -> `Contracts: 4 kept, 0 broken.`
- ruff total: 473 -> 416. mypy total: 44 -> 44 (los 5 archivos de la fase: 0 errores, ruff 0 y format OK).
- RED verificado: `ImportError: cannot import name 'InvalidImageUrlError'` en la colección de test_storage y test_domain_error_handler antes de implementar.

## Salida literal de la compuerta (RESUMEN)
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
(Los tres ✘ son deuda heredada fuera de los archivos de la fase.) `135 passed, 1 warning in 10.95s`, `TOTAL 927 52 130 25 93%`.

## Notas
- gaps.md no contenía bloqueantes para la fase B; se implementó la fase completa.
- Para pasar mypy a 0 en `test_domain_error_handler.py` se sustituyó `None` por un `Request({"type": "http"})` en las 4 llamadas al handler (sin cambio de comportamiento).
- Los docstrings de exceptions.py y main.py se reescribieron a resumen de una línea (D205) y se partieron strings largos (E501), sin cambio semántico ni de `detail`.
- Se ejecutó con el árbol sucio de archivos de `.claude/`, `AGENTS.md`, `CLAUDE.md` y `gaps.md` sin commitear, ajenos a la fase (no se tocaron ni se añadieron).
- Co-Authored-By usa `Claude Sonnet 5.5` (modelo ejecutor).

## Residuales
- `print()` (A6), `str(e)` en detail (SEC3), `os.getenv` (A4): intactos por plan.
- Hasta la fase C el servicio sigue envolviendo en `image_uploader` (415 sale como 503).

# Handoff BE-01 Fase C (c5fc0b7)

Commit: `fix(services): classify image urls on create and surface domain errors` (coautor: Claude Sonnet 5.5).
Entorno: compuerta ejecutada con `venv/Scripts` en PATH. Base develop `8bf9815` vigente (origen == merge-base).

## Archivos tocados
- app/services/tourist_services_service.py (create_tourist_package: `is_temporal_url` -> `InvalidImageUrlError`; docstring; image_uploader sin try/except; import de `StorageUnavailableError` retirado)
- tests/conftest.py (mock con `is_temporal_url`/`is_permanent_url` por prefijo)
- tests/test_services.py (6 tests nuevos + outage con `StorageUnavailableError`)

`git diff -w --stat HEAD~1`: servicio 192, conftest 31, test_services 233 (335 ins / 121 del). El ruido restante es
`ruff format` + fixes mecanicos (UP006, D212, D202, UP035, UP017, I001, W292) para dejar ruff en 0 en los 3
archivos; esto toca por formato cuerpos de otros metodos del servicio (update_package_details incluido) sin cambiar logica.
Los E501 se resolvieron a mano recortando docstrings/comentarios y partiendo dos literales (el texto de `detail` se conserva).

## RED
Antes de implementar: 3 failed, 16 passed en test_services.py (foreign URL, permanent URL, 415 -> 503).
Los otros nuevos pasaban por el comportamiento previo; el outage test pasaba con la nueva excepcion al seguir envuelta.
Tras implementar: 141 passed.

## Compuerta (RESUMEN literal)
```
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura
Compuerta NO superada: ruff format --check, ruff check, mypy
```
- pytest: 141 passed (135 base + 6). Cobertura total 93 % (base 93 %).
- import-linter: `Contracts: 4 kept, 0 broken.`
- ruff total: 416 -> 362 (baja). mypy total: 44 = 44.
- Archivos tocados: `ruff check` -> All checks passed; `ruff format --check` -> 3 files already formatted.
- `grep "except Exception" app/services/tourist_services_service.py` -> vacio.

## mypy del servicio (decision 6): mismo conjunto de 10 errores, solo desplazan lineas
Antes (l.): 55,116,122,155,156,161,193,194,200,324 -> Despues: 74,128,136,165,166,173,206,207,215,331.
Codigos identicos en orden: arg-type, assignment, arg-type, assignment, assignment, arg-type, assignment, assignment, arg-type, arg-type.
tests/conftest.py y tests/test_services.py: mypy mantiene sus 2 errores heredados (no-any-return conftest, index test_services); ninguno nuevo.

## Residuales / dudas
- Ruff/mypy globales siguen en rojo por deuda heredada (no tocada).
- Los tests usan el prefijo CDN fijo del mock; `storage_double` y `admin_headers` son fixtures locales de test_services.py (el plan pide `persist_user`+`make_auth_headers`, usados).
- Fase D debe ser consciente de que `update_package_details` sigue con el `in` por substring (no tocado).

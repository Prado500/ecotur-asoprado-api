# Handoff BE-01 Fase D

Commit: 4295334 `fix(services): apply the same image url rule when updating a package`.
gaps.md: sin [BLOQUEANTE] para esta fase. Alcance extra del plan (c7cdecf): create clasifica todas las URLs antes de promover.
Base develop 8bf9815 = origin/develop = merge-base (fetch OK).

## Archivos
- app/services/tourist_services_service.py: create valida todas con `is_temporal_url` antes de cualquier promocion; update clasifica (temporal/permanente/otra -> InvalidImageUrlError) antes de borrar o copiar; closure `resolve_url` usa `is_temporal_url`; sin `temporal_container_name in`; import `HttpUrl` ya inutil retirado; docstring Raises.
- tests/test_services.py: wasabisys -> URL permanente propia; 4 tests nuevos (PUT ajena x2 parametrizado sin efectos, PUT feliz permanente+temporal, POST 2 temporales + 1 ajena -> 400 sin promover).

## git diff --stat
 app/services/tourist_services_service.py | 60 ++++++++++++--------
 tests/test_services.py                   | 94 +++++++++++++++++++++++++++++++-
 2 files changed, 128 insertions(+), 26 deletions(-)

## Compuerta (literal)
```
=== RESUMEN ===
  x ruff format --check
  x ruff check
  x mypy
  ok import-linter
  ok docs (coherencia)
  ok pytest + cobertura
Found 362 errors.  (base 362)
Found 44 errors in 12 files  (base 44)
Contracts: 4 kept, 0 broken.
TOTAL 927 52 134 25 93%
145 passed, 1 warning
```
RED previo: 4 failed / 19 passed. Ruff 0 en los 2 archivos tocados. mypy del servicio: los mismos 10 errores Column[...] (lineas 74,128,136,165,166,173,206,207,215 y 331->343 por desplazamiento).

## Residuales
Rojo global de ruff/mypy es deuda heredada de archivos no tocados. Blobs compartidos entre paquetes: ver Residuales del plan.

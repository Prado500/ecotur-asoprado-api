# Verificación — BE-01: `storage.py` lanza `HTTPException` (500 al crear paquete con URLs inválidas) y rompe el contrato de capas

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A, fila BE-01; relacionados: §A2 filas A7 y P1, ADR-0003 "Hipótesis para BE-01")
**Fecha:** 2026-10-25

> Nota sobre la fuente: el backlog cita "B1 (txt)" como origen. El tag `B1` del informe
> `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` es **otro defecto** (`_verify_admin`
> inexistente en `TouristServicesService`, ya resuelto) y no describe BE-01. La descripción válida
> de BE-01 es únicamente la fila del backlog; el informe solo aporta A7 y SEC2 como vecinos.

## Qué describe el ítem
Crear un paquete (`POST /servicios/`) con URLs de blobs inexistentes o ajenas al CDN devuelve **500**.
El backlog lo localiza en `app/core/storage.py:138` (`HTTPException(500, "Fallo al consolidar…")`),
más un 415 (l.60) y otro 500 (l.86). Por esa importación transitiva `services → core/storage → fastapi`
el contrato de `import-linter` "Los servicios no conocen el transporte HTTP" está BROKEN. La fila
incluye A7 (copia sin esperar antes de borrar el origen) y, como fase A, P1 (imports muertos en
`core/security.py`, segunda causa del mismo contrato roto).

## Evidencia en el código
- `app/core/storage.py:5` — `from fastapi import HTTPException, status` (único import de FastAPI fuera de `app/api` y `app/main.py` que se usa de verdad).
- `app/core/storage.py:55-56` — docstring de `upload_image` documenta `Raises: HTTPException: 415 … or 500`.
- `app/core/storage.py:59-63` — `if not image.content_type.startswith("image/"): raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, …)`.
- `app/core/storage.py:85-89` — `except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fallo al comunicar con Azure CDN: {str(e)}")` (interpola `str(e)`: también SEC3).
- `app/core/storage.py:111-138` — `promote_to_permanent` envuelve todo en `try/except Exception`; `:134-138` → `print(...)` + `raise HTTPException(status_code=500, detail="Fallo al consolidar las imágenes en el CDN.")`. **Este es el 500 de BE-01**: resuelve la "hipótesis para BE-01" del ADR-0003 a favor de la segunda opción (es el `HTTPException(500)` admitido como residuo, no una excepción de dominio sin registrar).
- `app/core/storage.py:114` — `blob_name = temp_url.split("/")[-1]`: no se valida que la URL pertenezca al CDN ni al contenedor temporal; cualquier URL llega a `start_copy_from_url`.
- `app/core/storage.py:126` + `:129` — `await dest_blob.start_copy_from_url(temp_url)` seguido de `await source_blob.delete_blob()` sin consultar `copy_status` ni `requires_sync` (A7, misma zona).
- `app/services/tourist_services_service.py:6` — `from app.core.storage import AzureStorageClient, StagedImage` (arista que `import-linter` reporta: `app.services.tourist_services_service -> app.core.storage (l.6)`, `app.core.storage -> fastapi (l.5)`).
- `app/services/tourist_services_service.py:42-43` — `create_tourist_package` llama `promote_to_permanent(str(url))` para **toda** URL del payload sin comprobar el contenedor temporal. Una URL ajena al CDN o un blob inexistente cae directo al `HTTPException(500)` de `storage.py:138`. No hay try/except en este camino.
- `app/services/tourist_services_service.py:301-302` — en cambio `update_package_details` sí comprueba `if self.storage_client.temporal_container_name in str(url)` antes de promover: comportamiento asimétrico entre crear y actualizar.
- `app/services/tourist_services_service.py:231-238` — `image_uploader`: `except Exception as e: raise StorageUnavailableError(...)`. `HTTPException` hereda de `Exception`, así que el 415 de `storage.py:60` se degrada a **503** al pasar por el endpoint (ver "Rincones").
- `app/main.py:108-117` — `_DOMAIN_ERROR_STATUS`: contiene `StorageUnavailableError → 503`; **no existe** ninguna excepción de dominio para "tipo de archivo no soportado" ni para "URL/blob de imagen inválido". `app/core/exceptions.py:185-205` confirma que `StorageUnavailableError` es la única excepción de almacenamiento.
- `app/core/security.py:6-10` — `from fastapi import HTTPException`, `from starlette import status`, `from app.models import User`, `from app.models.user import UserRole`: los 4 imports muertos de P1 (`ruff` los marca como `F401 ×4`). Son la segunda causa del contrato roto: `app.services.user_service -> app.core.security (l.16)`, `app.core.security -> fastapi (l.6)` / `-> starlette (l.7)`.
- `tests/test_storage.py:4` y `:18-21` — el único test de `storage.py` importa `HTTPException` y afirma `exc_info.value.status_code == 415`: congela el acoplamiento y hay que reescribirlo.
- `tests/conftest.py:79` — `mock_client = MagicMock()` sin `spec` para el storage; `:90-93` simula `promote_to_permanent` como `url.replace("temp-ecotur-images", "ecotur-images")`, siempre exitoso. Ningún test ejercita un fallo de promoción, ni una URL ajena, ni la creación de paquete con URL inválida.
- `tests/test_domain_error_handler.py:25-37` — parametrize con las 8 excepciones actuales; es donde deben registrarse las nuevas.

## Ficheros afectados (mapa completo)
- `app/core/storage.py` — origen de la deuda: import de FastAPI (l.5), tres `raise HTTPException` (l.60, l.86, l.138), docstring l.55-56, copia asíncrona sin espera (l.126/129), `print` (l.105, l.135), `str(e)` en `detail` (l.88).
- `app/core/security.py` — 4 imports muertos (l.6-10) que rompen el mismo contrato (P1, fase A según backlog).
- `app/core/exceptions.py` — faltan las excepciones de dominio nuevas (tipo de archivo no soportado; URL/blob de imagen inválido).
- `app/main.py` — `_DOMAIN_ERROR_STATUS` (l.108-117) debe registrar las nuevas (415 y 422 según backlog); si no, fallback a 500 (l.137).
- `app/services/tourist_services_service.py` — l.42-43 (promoción sin validar contenedor), l.231-238 (`except Exception` que absorbe la 415), l.301-302 (comprobación que crear no tiene).
- `tests/test_storage.py` — afirma sobre `HTTPException` (l.4, l.18-21).
- `tests/test_domain_error_handler.py` — parametrize de la tabla (l.25-37).
- `tests/conftest.py` — mock del storage sin `spec` (l.79) y promoción siempre exitosa (l.90-93).
- `tests/test_services.py` — tests de `upload-images` (l.199-222, 503) y de reconciliación con promoción (l.283-335) que el cambio no debe romper; falta test de `POST /servicios/` con URL ajena/inexistente.
- `pyproject.toml` — contrato `[[tool.importlinter.contracts]] "Los servicios no conocen el transporte HTTP"` (l.116-120) es la verificación final: debe pasar a 4 KEPT.
- `docs/adr/0003-manejo-de-errores-agnostico-al-transporte.md` — l.64-66 declara el `HTTPException` de `storage.py` como "residuo vigente" y l.74-76 la hipótesis; BE-01 contradice ese residuo (supersede o nota, no edición del ADR aceptado).

## Rincones no mencionados por la fuente
1. **El 415 nunca llega al cliente.** `tourist_services_service.py:235-236` convierte cualquier `Exception` —incluida la `HTTPException(415)` de `storage.py:60`— en `StorageUnavailableError` → **503**. Solo existe el test unitario `tests/test_storage.py` (que llama a `upload_image` directamente); no hay ningún test por endpoint que suba un archivo no-imagen (grep `octet-stream|text/plain|415` en `tests/` → solo `test_storage.py`). El backlog asume "`UnsupportedMediaTypeError` → 415" como si hoy funcionara.
2. **Asimetría crear/actualizar:** `create_tourist_package` (l.43) promueve toda URL; `update_package_details` (l.301) solo las del contenedor temporal. Con una URL permanente del propio CDN, crear también intenta promover (`start_copy_from_url` desde el contenedor permanente y luego `delete_blob` en el temporal, que no existe → 500).
3. `start_copy_from_url(temp_url)` acepta cualquier URL pública (l.126): sin una lista blanca de host/contenedor, el servidor copiaría contenido arbitrario de Internet al CDN. Es consecuencia directa de "URL ajena al CDN" y conviene cerrarla en la misma excepción de dominio (422).
4. `import-linter` reporta **dos** rutas rotas del mismo contrato (`storage` y `security`); corregir solo `storage.py` dejaría el contrato BROKEN. P1 es condición necesaria para "4 KEPT".
5. `scripts/check.py:73` imprime `✔/✘` y falla con `UnicodeEncodeError` (cp1252) cuando la salida se redirige a fichero en Windows; corriendo con `PYTHONIOENCODING=utf-8` funciona. No es BE-01; reportado para que un humano lo lleve al backlog.
6. Residuos que viven en el mismo bloque y que el plan **no** debe arreglar "de paso" (tienen ítem propio): `print()` en l.105/135 (A6), `str(e)` en `detail` l.88 (SEC3), `os.getenv` l.35-37 (A4), SVG/tamaño (SEC2), `mock_client = MagicMock()` sin spec (§9).

## Patrones de detección (copiables)
```bash
# 1. Acoplamiento HTTP fuera de la capa de transporte (debe quedar vacío salvo app/main.py)
grep -rn "HTTPException\|from fastapi\|from starlette" app --include=*.py | grep -v "^app/api/\|^app/main.py"
# 2. Las tres lanzadas concretas de storage.py (deben desaparecer)
grep -n "raise HTTPException" app/core/storage.py
# 3. Tests que afirman sobre HTTPException (deben migrar a excepciones de dominio)
grep -rn "HTTPException" tests alembic scripts --include=*.py
# 4. A7: copia sin espera antes de borrar el origen
grep -n "start_copy_from_url\|copy_status\|requires_sync\|delete_blob" app/core/storage.py
# 5. P1: imports muertos de core/security
ruff check app/core/security.py --select F401
# 6. Promoción sin comprobar el contenedor temporal (crear vs actualizar)
grep -n "promote_to_permanent\|temporal_container_name in" app/services/tourist_services_service.py
# 7. Registro en la tabla del handler (ADR-0003)
grep -n "Error: status\." app/main.py
# 8. Verificación final del contrato de capas (esperado: "Contracts: 4 kept, 0 broken.")
lint-imports
```

## Línea base (python scripts/check.py)
Comando ejecutado (dos veces; la primera redirigida a fichero rompió en el RESUMEN por cp1252, ver rincón 5):
```
python scripts/check.py
PYTHONIOENCODING=utf-8 python scripts/check.py
```
Bloque RESUMEN literal:
```
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✘ import-linter
  ✔ pytest + cobertura

Compuerta NO superada: ruff format --check, ruff check, mypy, import-linter
EXIT=1
```
**La compuerta ya falla antes de tocar nada** (4 de 5 pasos en rojo; es el estado conocido del día 1).
Detalle por paso:
- `ruff format --check`: múltiples ficheros sin formatear (entre ellos `app/core/storage.py`, `app/core/security.py`, `app/services/tourist_services_service.py`).
- `ruff check`: `Found 488 errors. [*] 263 fixable with --fix`. En los ficheros de BE-01: `storage.py` 18 (E501×6, D212×5, B904×2, D200×2, D205, W292, I001); `security.py` 16 (D212×4, **F401×4**, UP017×3, E501×2, W292, D415, I001); `tourist_services_service.py` 37; `tests/test_storage.py` 0.
- `mypy`: `Found 44 errors in 12 files (checked 33 source files)`. En ficheros de BE-01: `security.py:72,92` (`SECRET_KEY: str | None`), `tourist_services_service.py` ×10 (todos `Column[...]` vs tipo nativo → S1, no BE-01). `storage.py`: 0.
- `import-linter`: `Analyzed 50 files, 131 dependencies.` — `Contracts: 3 kept, 1 broken.` Roto: "Los servicios no conocen el transporte HTTP" por `tourist_services_service -> core.storage (l.6) -> fastapi (l.5)` y `user_service -> core.security (l.16) -> fastapi (l.6) / starlette (l.7)`.
- `pytest`: **116 passed, 1 warning in 8.70s** (warning: `HTTP_422_UNPROCESSABLE_ENTITY` deprecado, S5).
- Cobertura total: **89 %** (`TOTAL 908 stmts, 88 miss, 122 branch, 26 partial`). `app/core/storage.py`: **28 %** (missing 35-42, 66-86, 95-105, 111-138). `tourist_services_service.py`: 93 %.

## Conclusión para el planificador
- **Resolver:** (1) `storage.py` deja de importar FastAPI: 415 → `UnsupportedMediaTypeError`, 500 de `upload_image` → `StorageUnavailableError` (ya existe, `exceptions.py:185`), fallo de promoción/URL ajena/blob inexistente → excepción de dominio nueva → 422; registrar las nuevas en `_DOMAIN_ERROR_STATUS` y en el parametrize de `test_domain_error_handler.py`. (2) `create_tourist_package` debe validar que la URL pertenece al contenedor temporal del CDN **antes** de promover (misma regla que `update_package_details:301`), y el `except Exception` de `image_uploader` (l.235) debe dejar pasar las excepciones de dominio para que el 415 llegue como 415. (3) A7: copia síncrona (`requires_sync=True`) o espera de `copy_status` antes de `delete_blob`. (4) Fase A = P1: borrar `security.py:6-10`; sin eso el contrato sigue BROKEN. (5) Tests: endpoint `POST /servicios/` con URL ajena → 422 y con fallo de promoción → código acordado; `upload-images` con `application/octet-stream` → 415; unitarios de `storage.py` con `BlobServiceClient` mockeado con `autospec` para subir del 28 %; reescribir `tests/test_storage.py`.
- **No tocar:** `print`/`str(e)`/`os.getenv`/SVG (A6, SEC3, A4, SEC2 tienen su día); el estilo `Column` que mypy marca en el servicio (S1); el ADR-0003 aceptado (si se retira el "residuo declarado", se añade nota o ADR que lo supersede, no edición).
- **Riesgos:** `HTTPException` hereda de `Exception`, así que cualquier `except Exception` intermedio seguirá absorbiendo excepciones de dominio — hay que excluirlas explícitamente (`except DomainError: raise`). `create_autospec(AzureStorageClient)` en `test_services.py:205` seguirá válido solo si la firma pública no cambia. La compuerta parte en rojo (ruff/mypy/import-linter): el criterio de aceptación realista es "import-linter 4 KEPT, pytest verde, cobertura ≥ 89 %, y ruff/mypy sin errores **nuevos** en los ficheros tocados", no "compuerta verde" global.

## Re-verificación — 2026-10-27

**Veredicto:** confirmada (sin cambios respecto a 2026-10-25). La deuda persiste íntegra.

- Base develop: `8bf9815` (tras `git fetch origin`; merge-base HEAD == origin/develop).
- Grep global repetido: `app/core/storage.py:5` (import fastapi), `:60`, `:86`, `:138` (`raise HTTPException`); `app/core/security.py:6-7` (fastapi/starlette); `tourist_services_service.py:43` promueve sin validar contenedor, `:301` sí valida. Sin ficheros nuevos afectados.
- Comando: `PYTHONIOENCODING=utf-8 python scripts/check.py` (EXIT=1)

```
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✘ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff format --check, ruff check, mypy, import-linter
```
- pytest: 116 passed, 1 warning. Cobertura total 89 % (`storage.py` 28 %).
- ruff check: Found 489 errors (antes 488). mypy: 44 errors en 12 ficheros. import-linter: 3 kept, 1 broken.
- Cambio vs. anterior: aparece el paso "docs (coherencia)" (OK) y ruff +1 error (en `scripts/`, ajeno a BE-01). La compuerta ya falla antes de tocar nada.
- La conclusión para el planificador de la verificación inicial sigue vigente.

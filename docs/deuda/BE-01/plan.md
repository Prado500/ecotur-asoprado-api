# PLAN — BE-01: Sacar `HTTPException` de `storage.py`, validar las URLs de imagen y esperar la copia antes de borrar

> Fuente: `docs/deuda/BE-01/verificacion.md` (confirmada 2026-10-25; re-verificada 2026-10-27 contra develop `8bf9815`).
> Estado: **aprobado por David el 2026-10-27** con seis decisiones (ver "Objetivo y decisiones bloqueadas").
> Cambios respecto al borrador: `InvalidImageUrlError` → **400** (no 422); trinquete mypy por conjunto de errores;
> `requires_sync=True` confirmado contra el portal de Azure; fase D aprobada; coautoría del commit = modelo ejecutor real.
> Incluye P1 (fase A) y A7 (fase B), como manda `docs/backlog.md` y el bloque `B-BE01` de `PLAN.md` §2b.

## Resumen para aprobación

Hoy `POST /servicios/` responde **500** cuando una URL de imagen es ajena al CDN o apunta a un blob que no
existe, porque `app/core/storage.py` envuelve todo fallo en `HTTPException(500)`. Ese mismo `import fastapi`
(y cuatro imports muertos en `app/core/security.py`) rompen el contrato de capas de `import-linter`.
El plan, en cuatro fases pequeñas: (A) borrar los imports muertos de `security.py`; (B) `storage.py` deja de
conocer HTTP: lanza excepciones de dominio (`UnsupportedMediaTypeError` → 415, `InvalidImageUrlError` → 400,
`StorageUnavailableError` → 503), rechaza cualquier URL que no sea un blob del contenedor temporal de la
cuenta propia, copia con `requires_sync=True` y comprueba `copy_status` **antes** de borrar el origen (A7),
con una suite unitaria que sube `storage.py` del 28 % de cobertura; (C) el servicio exige que las imágenes de
un paquete nuevo vengan del contenedor temporal y deja de tragarse las excepciones de dominio (hoy el 415
sale como 503); (D) `PUT /servicios/{id}` aplica la misma regla que crear (hoy acepta cualquier URL externa).
**Riesgo principal (cerrado):** `requires_sync=True` exige que el blob origen sea legible desde Azure; David
verificó en el portal que `temp-ecotur-images` y `ecotur-images` están en nivel de acceso **Blob** (lectura
anónima de blobs), así que la premisa se cumple. El sondeo de `copy_status` queda solo como alternativa
documentada en el ADR-0006. **Cambio de contrato visible:** la fase D convierte en 400 lo que hoy es 200 (URL
externa en PUT); aprobada, se mantiene como última fase y es recortable si no cabe hoy. **Por qué 400 y no 422:**
contrato con el cliente Flutter: el 422 actual de este endpoint tiene forma `{"detalle": [...]}` que el cliente
parsea como lista, mientras que el 400 con `{"detail": str}` ya lo recibe (misma lógica que ADR-0003 con
`AlreadyExistsError`). **No se toca:** `print()` (A6), `str(e)` en `detail` (SEC3), `os.getenv` (A4),
SVG/tamaño (SEC2), el `MagicMock` sin spec de `conftest.py` (§9), el estilo `Column` que mypy marca en el
servicio (S1), ni el ADR-0003 (el ADR-0006, aceptado, lo supersede parcialmente; David lo mueve a `docs/adr/`
en un commit antes del PR, cuando la sección de evidencia tenga los números reales).

## Objetivo y decisiones bloqueadas

Objetivo: que ninguna ruta `app.services → … → fastapi/starlette` exista (`lint-imports` → 4 KEPT) y que
crear un paquete con URLs inválidas responda 400/503 según la causa, nunca 500, sin perder blobs por una
copia inacabada.

1. Los códigos HTTP viven solo en `_DOMAIN_ERROR_STATUS` (ADR-0003). Nuevas entradas: `UnsupportedMediaTypeError`
   → `status.HTTP_415_UNSUPPORTED_MEDIA_TYPE`; `InvalidImageUrlError` → `status.HTTP_400_BAD_REQUEST`.
   **400, no 422 (decisión de David, 2026-10-27):** el 422 actual de `/servicios/` tiene forma `{"detalle": [...]}`
   (handler de `RequestValidationError`, `main.py:85-88`) que el cliente Flutter parsea como lista; el 400 con
   `{"detail": str}` ya lo recibe este endpoint (`BusinessRuleViolationError`, 11 imágenes). Misma lógica que
   ADR-0003 con `AlreadyExistsError` (400 en vez de 409 para no romper el cliente). Se mantiene la excepción
   propia `InvalidImageUrlError` (no se reutiliza `BusinessRuleViolationError`) para poder remapearla a 422 cuando
   P2 unifique la forma (ver Residuales).
2. El adaptador `AzureStorageClient` lanza **excepciones de dominio** (`app/core/exceptions.py`), nunca
   `HTTPException`. Esto retira el "residuo declarado" del ADR-0003 → borrador de ADR-0006 adjunto.
3. `promote_to_permanent` solo acepta URLs cuyo prefijo exacto sea `<container_client.url>/` del contenedor
   temporal de la cuenta propia (el `in` por substring de hoy admite `https://evil.example/temp-ecotur-images/x.jpg`).
   Blob origen inexistente (`exists()` → `False`) → `InvalidImageUrlError`. Fallo del SDK (`azure.core.exceptions.AzureError`)
   → `StorageUnavailableError`. Copia con `requires_sync=True`; si `copy_status != "success"` → `StorageUnavailableError`
   y **no** se borra el origen.
4. Regla de negocio (servicio): al **crear**, toda imagen debe ser un blob temporal (se promueve); cualquier otra
   URL → `InvalidImageUrlError`. Al **actualizar** (fase D): temporal → se promueve; permanente propia → se conserva;
   otra → `InvalidImageUrlError`, decidido antes de borrar o copiar nada.
5. El `try/except Exception` de `image_uploader` se elimina: el adaptador ya traduce sus fallos; el servicio no
   vuelve a envolverlos (un punto de traducción por frontera).
6. Trinquete (ADR-0005) aplicado a los archivos tocados: ruff **0** en cada uno (el hook formatea; lo no
   autocorregible se arregla a mano en la misma fase); mypy **0** salvo dos excepciones declaradas aquí porque
   dependen de otros ítems: `security.py` (2 errores `SECRET_KEY: str | None`, A4) y
   `tourist_services_service.py` (10 errores `Column[...]`, S1). Criterio para esos dos: **≤ línea base, medido
   como el mismo conjunto de errores (mismas líneas y mismos códigos de mypy), no solo el mismo conteo.** El
   ejecutor pega en el handoff la salida literal de `mypy <archivo>` antes y después; el auditor compara línea a
   línea: un error nuevo con el mismo conteo (uno que desaparece y otro que aparece) es BLOQUEANTE.
7. Mensajes `detail` existentes se conservan letra a letra (incluido `{str(e)}` de `upload_image`, SEC3).
8. Coautoría de los commits: la línea `Co-Authored-By` de cada mensaje lleva el nombre del **modelo que realmente
   ejecuta la fase** (p. ej. `Claude Sonnet 4.5 <noreply@anthropic.com>`), nunca un nombre fijo. En los bloques de
   commit de abajo figura el marcador `<MODELO EJECUTOR>`; el ejecutor lo sustituye por su propio nombre de modelo
   y deja el resto del mensaje letra a letra.

## Análisis del redactor

**Qué se cambia y por qué.** Dos rutas rompen el contrato "Los servicios no conocen el transporte HTTP":
`user_service → core.security → fastapi/starlette` (imports muertos, P1) y `tourist_services_service →
core.storage → fastapi` (uso real: tres `raise HTTPException`). La primera se cierra borrando líneas; la
segunda exige que el adaptador hable el idioma del dominio. Elegir excepciones de dominio en el adaptador (y no
una excepción "de infraestructura" que el servicio traduzca) evita una segunda tabla de traducción y es lo que
`StorageUnavailableError` ya insinúa en su docstring. El 500 concreto de BE-01 (`storage.py:138`) desaparece al
distinguir tres causas: URL no admitida/blob inexistente (400, culpa del cliente), fallo de Azure (503) y copia
no terminada (503, sin borrar el origen: A7).

**Orden y dependencias.** A es independiente y la más pequeña; sin A, el contrato sigue BROKEN aunque B esté
perfecta. B crea las excepciones, las registra y reescribe el adaptador; con solo B, el síntoma de BE-01 ya
pasa de 500 a 400 (crear no tiene `try/except`), pero el 415 sigue saliendo como 503. C depende de B
(`is_temporal_url`, nuevas excepciones) y hace explícita la regla de crear. D depende de C y es la única que
cambia un contrato visible (PUT con URL externa: 200 → 400); por eso va al final y se puede recortar sin
afectar a las anteriores (aprobada el 2026-10-27; recortable si no cabe hoy).

**Tests que congelan comportamiento relacionado.** `tests/test_storage.py` (415 vía `HTTPException`: se
reescribe entera). `tests/test_domain_error_handler.py:25-37` (tabla de 8: se amplía a 10).
`tests/test_services.py:199-222` (`upload_image` lanza `Exception` genérica → 503: con la decisión 5 el mock
debe lanzar `StorageUnavailableError`, la excepción documentada del adaptador). `tests/test_services.py:282-326`
(reconciliación en PUT: URL permanente intacta, temporales promovidas; debe seguir verde en C y en D).
`tests/test_services.py:136-163` (PUT con `https://s3.wasabisys.com/ejemplo.jpg` → 200: es el único test que
congela "URL externa aceptada"; D lo cambia a una URL permanente propia). `tests/test_audit.py:26-57` (POST con
URL temporal → 201: camino feliz de crear, no cambia). El mock global de `conftest.py:79-93` no tiene `spec`:
sin definir `is_temporal_url`/`is_permanent_url` devolvería `MagicMock` (verdadero) y haría pasar la nueva regla
por accidente; C le añade dos lambdas por prefijo.

**Riesgos.** (1) `requires_sync=True`: Azure exige que el origen sea legible por URL. Confirmado: David verificó
en el portal de Azure que `temp-ecotur-images` y `ecotur-images` están en nivel de acceso **Blob**. La copia
asíncrona con sondeo de `copy_status` (`get_blob_properties` antes de `delete_blob`) queda solo como alternativa
documentada en el ADR-0006, no como plan B operativo. (2) El hook de
Claude Code reformatea cada `.py` tocado: los diffs llevarán ruido mecánico; el auditor revisa la lógica con
`git diff -w`. (3) `InvalidImageUrlError` responde 400 `{"detail": str}` (forma única que el cliente Flutter ya
maneja) en vez del 422 semánticamente más preciso; cuando P2 unifique la forma del 422 se remapea (Residuales).
(4) `create_autospec(AzureStorageClient, instance=True)` de `test_services.py:205` sigue válido: no cambia
ninguna firma pública, solo se añaden `is_temporal_url` e `is_permanent_url`.

**Qué NO se toca.** `delete_image` (salvo cobertura), `__init__` de `AzureStorageClient` (`os.getenv`, A4),
`print()` (A6), `str(e)` (SEC3), SVG/tamaño (SEC2), `MagicMock()` sin spec (§9), modelos `Column` (S1),
`HTTP_422_UNPROCESSABLE_ENTITY` de `main.py:86` (S5), `app/core/email.py` (importa `fastapi_mail`, no `fastapi`).

## Regla de alcance

**Sí:** `app/core/security.py`, `app/core/storage.py`, `app/core/exceptions.py`, `app/main.py` (solo imports y
tabla), `app/services/tourist_services_service.py` (solo `create_tourist_package`, `image_uploader` y, en D,
`update_package_details`), `tests/test_storage.py`, `tests/test_domain_error_handler.py`, `tests/conftest.py`
(solo el mock de storage), `tests/test_services.py`. **No:** ningún otro archivo de `app/`, ningún ADR aceptado,
`.claude/`, `scripts/`, `AGENTS.md`, migraciones (no hay cambio de esquema).

## Fases

### Fase A — Borrar los imports muertos de `core/security.py` (P1) (la más pequeña)
- Archivos: `app/core/security.py`.
- Cambios exactos: eliminar l.6-10 (`from fastapi import HTTPException`, `from starlette import status`,
  `from app.models import User`, `from app.models.user import UserRole`). Dejar el archivo con ruff a cero: el hook
  aplica `format`/`--fix` (I001, D212, UP017, W292); a mano, D415 (l.21: terminar el resumen con punto) y E501 (l.26,
  l.40: partir las líneas del docstring). Sin cambios de lógica.
- Tests (RED primero): no existe prueba pytest capaz de detectar un import muerto; el RED es de herramientas y se
  pega literal en el handoff: `ruff check app/core/security.py --select F401` → 4 errores (RED) → 0 (GREEN);
  `lint-imports` → antes lista dos rutas rotas, después solo `tourist_services_service -> core.storage -> fastapi`.
- Criterio de aceptación: `ruff check app/core/security.py` → "All checks passed"; `mypy app/core/security.py` → los
  **mismos 2 errores** de la línea base (mismas líneas y códigos, `SECRET_KEY`, decisión 6; salida literal antes y
  después en el handoff); `lint-imports` → "3 kept, 1 broken" con **una sola** ruta
  (`storage`); pytest 116 passed; cobertura ≥ 89 %.
- Fuera de alcance de esta fase: `SECRET_KEY: str | None` (A4); cualquier otro archivo.
- Commit:
  ```
  refactor(core): drop unused HTTP and model imports from security

  app/core/security.py imported HTTPException, starlette.status, User and
  UserRole without using them (ruff F401 x4). Because app.services.user_service
  imports this module, the transitive edge services -> core.security -> fastapi
  is one of the two routes that break the import-linter contract "Los servicios
  no conocen el transporte HTTP" (backlog P1, phase A of BE-01).

  - app/core/security.py: remove the four dead imports; the automatic
    ruff format/--fix pass and two manual docstring wraps leave the file with
    zero ruff findings. The two mypy findings on SECRET_KEY (str | None) belong
    to configuration (backlog A4) and are left untouched on purpose.

  Behavior is unchanged: no symbol used by the module was removed.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — `storage.py` lanza excepciones de dominio, valida la URL y espera la copia (BE-01 + A7)
- Archivos: `app/core/exceptions.py`, `app/main.py`, `app/core/storage.py`, `tests/test_domain_error_handler.py`,
  `tests/test_storage.py`.
- Cambios exactos:
  - `exceptions.py`: añadir `UnsupportedMediaTypeError(DomainError)` y `InvalidImageUrlError(DomainError)` con el
    mismo patrón (`__init__(self, detail: str)`, docstring Google Style que nombra el código HTTP al que se mapea).
    Ruff a cero: reescribir en una línea el resumen de los 8 docstrings con D205 y partir la línea E501 (sin cambios
    semánticos).
  - `main.py`: importar ambas; añadir a `_DOMAIN_ERROR_STATUS` `UnsupportedMediaTypeError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE`
    e `InvalidImageUrlError: status.HTTP_400_BAD_REQUEST` (decisión 1). Nada más en `main.py` salvo lo que ruff exija
    (D205/D212/E501/I001/W292 del archivo).
  - `storage.py`: quitar `from fastapi import HTTPException, status`; importar `AzureError` de `azure.core.exceptions`
    y las tres excepciones de dominio. `upload_image`: MIME no imagen → `UnsupportedMediaTypeError` (mismo `detail`);
    `except AzureError as e` → `raise StorageUnavailableError(detail=<texto actual>) from e`. Nuevos métodos públicos
    `is_temporal_url(url: str) -> bool` e `is_permanent_url(url: str) -> bool` (prefijo exacto
    `f"{self.blob_service_client.get_container_client(<nombre>).url}/"`, resto no vacío y sin `/` ni `?`).
    `promote_to_permanent`: si no `is_temporal_url` → `InvalidImageUrlError`; `if not await source_blob.exists()` →
    `InvalidImageUrlError`; `props = await dest_blob.start_copy_from_url(temp_url, requires_sync=True)`;
    `if props.get("copy_status") != "success"` → `StorageUnavailableError` (sin borrar); después `delete_blob()` y
    `return dest_blob.url`; `except AzureError as e` → `StorageUnavailableError(...) from e` (el `print` de l.135 se
    conserva dentro del `except`, A6). Docstrings `Raises:` actualizados. `delete_image` y `__init__` intactos.
  - `test_domain_error_handler.py`: dos entradas nuevas en el parametrize: `(UnsupportedMediaTypeError("mime"), 415)`,
    `(InvalidImageUrlError("url"), 400)`.
  - `test_storage.py`: reescribir. Fixture `storage_client` con `monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", ...)`
    y `patch.object(storage_module, "BlobServiceClient", autospec=True)` cuyo `from_connection_string.return_value` es
    `create_autospec(BlobServiceClient, instance=True)` con `get_container_client` → `create_autospec(ContainerClient,
    instance=True)` (fijando `.url` por contenedor) y `get_blob_client` → `create_autospec(BlobClient, instance=True)`
    (`create_autospec` genera `AsyncMock` para `upload_blob`, `exists`, `start_copy_from_url`, `delete_blob`; verificado).
- Tests (RED primero), todos con `pytest.raises(<excepción de dominio>)`:
  1. `__init__` sin `AZURE_STORAGE_CONNECTION_STRING` → `ValueError`.
  2. `upload_image` con `application/octet-stream` → `UnsupportedMediaTypeError`; `upload_blob.assert_not_awaited()`.
  3. `upload_image` feliz → devuelve `blob_client.url`; `upload_blob.assert_awaited_once()` con `overwrite=True` y
     `content_settings.content_type == "image/jpeg"`; nombre `<uuid>.<extensión original>`.
  4. `upload_image` con `ServiceRequestError` del SDK → `StorageUnavailableError` (y `__cause__` es la del SDK).
  5. `is_temporal_url`/`is_permanent_url` parametrizados: temporal propia (T/F), permanente propia (F/T),
     `https://evil.example/temp-ecotur-images/x.jpg` (F/F), ruta anidada y con `?` (F/F), URL sin nombre de blob (F/F).
  6. `promote_to_permanent` con URL ajena → `InvalidImageUrlError`; `start_copy_from_url` y `delete_blob` no esperados.
  7. `promote_to_permanent` con blob inexistente (`exists` → `False`) → `InvalidImageUrlError`; sin copia ni borrado.
  8. `promote_to_permanent` feliz → `start_copy_from_url.assert_awaited_once_with(url, requires_sync=True)`;
     `copy_status="success"` → `delete_blob.assert_awaited_once()`; devuelve la URL del destino.
  9. `promote_to_permanent` con `copy_status="pending"` → `StorageUnavailableError`; `delete_blob.assert_not_awaited()` (A7).
  10. `promote_to_permanent` con `HttpResponseError` en la copia → `StorageUnavailableError`; `delete_blob.assert_not_awaited()`.
  11. `delete_image` feliz (`delete_blob` esperado una vez) y con fallo del SDK (no propaga).
- Criterio de aceptación: `grep -n "HTTPException\|from fastapi" app/core/storage.py` → vacío; `lint-imports` → "4 kept,
  0 broken"; cobertura de `app/core/storage.py` ≥ 90 % (línea base 28 %) y total ≥ 89 %; ruff y mypy a **0** en los 5
  archivos; pytest verde (116 + los nuevos); `test_domain_error_handler` con 10 entradas.
- Fuera de alcance de esta fase: el servicio (el 415 sigue llegando como 503 hasta C), `print`, `str(e)`, `os.getenv`, SVG.
- Commit:
  ```
  fix(storage): raise domain errors and copy blobs synchronously

  Creating a package with a blob URL foreign to the CDN or pointing to a blob
  that no longer exists answered 500 because promote_to_permanent wrapped every
  failure in HTTPException(500). The same module raised HTTPException(415) and
  HTTPException(500) from upload_image, which made app/core/storage.py the
  second route breaking the import-linter contract "Los servicios no conocen el
  transporte HTTP" (BE-01). The copy also deleted the source blob without
  waiting for the copy to finish (A7).

  - app/core/exceptions.py: add UnsupportedMediaTypeError and
    InvalidImageUrlError as DomainError subtypes.
  - app/main.py: register them in _DOMAIN_ERROR_STATUS (415 and 400) so the
    global handler translates them (ADR-0003); without the entry the fallback
    would degrade them to 500. 400 instead of 422 on purpose: the 422 this
    endpoint already emits has the {"detalle": [...]} shape the Flutter client
    parses as a list, while 400 with {"detail": str} is a shape it already
    handles here (same reasoning ADR-0003 applied to AlreadyExistsError).
  - app/core/storage.py: drop the fastapi import; upload_image raises
    UnsupportedMediaTypeError / StorageUnavailableError; promote_to_permanent
    only accepts blobs of this account's temporal container
    (InvalidImageUrlError otherwise, also when the blob does not exist), copies
    with requires_sync=True, checks copy_status before deleting the source and
    maps Azure SDK failures to StorageUnavailableError. is_temporal_url and
    is_permanent_url expose the URL classification to the service layer.
  - tests/test_domain_error_handler.py: the parametrize covers both entries.
  - tests/test_storage.py: unit suite over an autospecced BlobServiceClient
    freezing the MIME gate, the URL whitelist, the synchronous copy and the
    error translation.

  print() and str(e) inside detail stay as they are: they belong to A6 and SEC3.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — Crear exige blobs temporales y el servicio deja pasar las excepciones de dominio
- Archivos: `app/services/tourist_services_service.py`, `tests/conftest.py`, `tests/test_services.py`.
- Cambios exactos:
  - `create_tourist_package` (l.42-49): antes de promover cada URL, `if not self.storage_client.is_temporal_url(raw): raise
    InvalidImageUrlError(detail="…")` (texto nuevo en español que indique que la imagen debe subirse primero por
    `/servicios/upload-images/`); el resto del bucle igual. Docstring Google Style (hoy no tiene) con `Raises:`.
  - `image_uploader` (l.231-238): eliminar el `try/except Exception`; el bucle queda sin envoltorio; docstring `Raises:`
    pasa a listar `BusinessRuleViolationError`, `UnsupportedMediaTypeError`, `StorageUnavailableError`.
  - Importar `InvalidImageUrlError` (y dejar de importar `StorageUnavailableError` si queda sin uso). Ruff a cero en el
    archivo (E501 ×11 a mano; el resto lo arregla el hook). mypy: los mismos 10 errores de la línea base (mismas
    líneas y códigos, decisión 6).
  - `conftest.py` (l.79-93): añadir al mock
    `mock_client.is_temporal_url = lambda url: url.startswith("https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/")`
    y el equivalente para `is_permanent_url` con `/ecotur-images/`. Sigue siendo `MagicMock()` (§9 no es de este ítem).
  - `test_services.py`: los tests nuevos usan `persist_user(role=UserRole.admin)` + `make_auth_headers` de `conftest.py`
    (AGENTS §5), no la fixture local `admin_token`. Ruff a cero en el archivo.
- Tests (RED primero), por endpoint, con `create_autospec(AzureStorageClient, instance=True)` inyectado vía
  `app.dependency_overrides[get_storage_client]`:
  1. `POST /servicios/` con `https://evil.example/temp-ecotur-images/x.jpg` → 400, `{"detail": str}`;
     `promote_to_permanent.assert_not_awaited()`; `select(TouristService)` vacío; `select(AuditLog)` vacío.
  2. `POST /servicios/` con URL permanente propia → 400 (regla de crear); sin promoción ni filas.
  3. `POST /servicios/` con `promote_to_permanent.side_effect = InvalidImageUrlError("missing")` (blob inexistente)
     → 400; sin filas.
  4. `POST /servicios/` con `promote_to_permanent.side_effect = StorageUnavailableError("copy")` → 503; sin filas.
  5. `POST /servicios/` feliz explícito: URL temporal → 201; `promote_to_permanent.assert_awaited_once_with(url)`;
     `images[0].image_url` igual a la URL devuelta por el mock e `is_primary` verdadero.
  6. `POST /servicios/upload-images/` con `upload_image.side_effect = UnsupportedMediaTypeError("mime")` → **415**,
     `{"detail": str}`; `upload_image.assert_awaited_once()` con un `StagedImage` de `content_type="application/octet-stream"`.
  7. Modificar `test_upload_images_storage_outage_returns_503` (l.199-222): `side_effect=StorageUnavailableError("cdn outage")`;
     el resto de aserciones intactas.
- Criterio de aceptación: los 7 casos en verde; `grep -n "except Exception" app/services/tourist_services_service.py` →
  vacío; `test_audit_trail_creation_and_retrieval` y `test_update_package_concurrent_reconciliation` siguen verdes;
  ruff 0 en los 3 archivos; mypy del servicio: mismo conjunto de 10 errores que la línea base (salida literal antes
  y después en el handoff); cobertura total ≥ 89 %.
- Fuera de alcance de esta fase: `update_package_details` (fase D); convertir el mock global a `create_autospec` (§9);
  la fixture local `admin_token` de `test_services.py` (§9).
- Commit:
  ```
  fix(services): classify image urls on create and surface domain errors

  create_tourist_package promoted every URL of the payload, so a foreign URL
  or a permanent CDN URL reached the storage adapter and failed there, while
  update_package_details already told temporal URLs apart. image_uploader
  caught every Exception and re-raised StorageUnavailableError, which turned
  the adapter's 415 into a 503 and hid it from the client.

  - app/services/tourist_services_service.py: a new package only accepts
    temporal blobs (is_temporal_url) and raises InvalidImageUrlError for
    anything else before touching the CDN; image_uploader no longer wraps
    adapter failures because the adapter already raises domain errors
    (ADR-0003: one translation point per boundary).
  - tests/conftest.py: the shared storage mock answers is_temporal_url and
    is_permanent_url by URL prefix instead of a truthy MagicMock.
  - tests/test_services.py: endpoint tests for POST /servicios/ with a foreign
    URL (400), a permanent URL (400), a missing temporal blob (400), a
    promotion outage (503) and the explicit happy path (201); upload-images
    with a non-image now answers 415; the outage test raises the adapter's
    documented exception instead of a bare Exception.

  update_package_details is intentionally untouched here (next phase).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase D — `PUT /servicios/{id}` aplica la misma regla de URLs (aprobada 2026-10-27; recortable si no cabe hoy)
- Archivos: `app/services/tourist_services_service.py`, `tests/test_services.py`.
- Cambios exactos: en `create_tourist_package`: separar en dos bucles: primero clasificar todas las URLs
  (cualquiera no temporal → InvalidImageUrlError), después promover; ninguna promoción antes de validar todas.
  en `update_package_details`, antes del paso 2.2 (borrado en CDN), clasificar todas las URLs:
  si alguna no es ni temporal ni permanente propia → `InvalidImageUrlError` (nada se borra ni se copia). Sustituir la
  closure `resolve_url` (l.300-304, `in` por substring) por `is_temporal_url` → promover / `is_permanent_url` →
  conservar. Docstring `Raises:` actualizado.
- Tests (RED primero):
  1. `PUT` con una URL ajena entre las imágenes → 400; `delete_image.assert_not_awaited()`;
     `promote_to_permanent.assert_not_awaited()`; las imágenes del paquete en BD no cambian; sin fila de auditoría.
  2. `PUT` con `https://evil.example/temp-ecotur-images/x.jpg` (pasaría el `in` de hoy) → 400.
  3. `test_update_package_details` (l.136-163): la URL `https://s3.wasabisys.com/ejemplo.jpg` pasa a
     `https://ecoturasopradocdn2026.blob.core.windows.net/ecotur-images/ejemplo.jpg`; aserciones intactas.
  4. `test_update_package_concurrent_reconciliation` intacto y verde (congela temporal → promovida, permanente → intacta).
  5. `POST /servicios/` con dos URLs temporales válidas y una ajena → 400; promote_to_permanent.assert_not_awaited(); sin filas
- Criterio de aceptación: `grep -n "temporal_container_name in" app/services/tourist_services_service.py` → vacío; los
  4 casos verdes; ruff 0 y mypy con el mismo conjunto de 10 errores en el servicio (decisión 6); cobertura ≥ 89 %.
- Fuera de alcance de esta fase: blobs compartidos entre paquetes (ver Residuales); cualquier cambio en `delete_image`.
- Commit:
  ```
  fix(services): apply the same image url rule when updating a package

  update_package_details accepted any non-temporal URL verbatim through a
  substring check on the container name, while create_tourist_package now
  rejects URLs foreign to the CDN with 400. The inconsistency let an admin
  store hotlinked images through PUT but not through POST, and the substring
  check let a foreign host that merely contains the container name in its
  path reach start_copy_from_url.

  - app/services/tourist_services_service.py: every URL is classified
    (temporal -> promote, permanent -> keep, otherwise InvalidImageUrlError)
    before any CDN deletion or promotion runs, so a rejected payload leaves
    blobs and rows untouched; the resolve_url closure is removed.
  - tests/test_services.py: test_update_package_details uses a permanent CDN
    URL instead of a third-party host; new tests freeze the 400 on a foreign
    URL (no delete_image, no promote, no audit row) and keep the
    reconciliation test unchanged.

  Visible contract change: PUT /servicios/{id} answers 400 instead of 200 for
  image URLs outside the CDN. Approved with the BE-01 plan.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final
```bash
# 1. Acoplamiento HTTP fuera del transporte → solo debe quedar app/core/email.py:3 (fastapi_mail, falso positivo textual)
grep -rn "HTTPException\|from fastapi\|from starlette" app --include=*.py | grep -v "^app/api/\|^app/main.py"
# 2 y 3. Ninguna lanzada ni aserción sobre HTTPException fuera de app/api → ambos vacíos
grep -n "raise HTTPException" app/core/storage.py
grep -rn "HTTPException" tests alembic scripts --include=*.py
# 4. A7: requires_sync=True y copy_status aparecen ANTES de delete_blob en promote_to_permanent
grep -n "start_copy_from_url\|copy_status\|requires_sync\|delete_blob" app/core/storage.py
# 5. P1 → "All checks passed!"
ruff check app/core/security.py --select F401
# 6. Sin substring check; promote solo bajo is_temporal_url → ninguna línea con "temporal_container_name in"
grep -n "promote_to_permanent\|temporal_container_name in\|is_temporal_url\|is_permanent_url" app/services/tourist_services_service.py
# 7. Tabla del handler con 10 entradas (415 y 400 incluidas)
grep -n "Error: status\." app/main.py
# 8. Contrato de capas
lint-imports            # esperado: "Contracts: 4 kept, 0 broken."
# 9. Compuerta completa (ADR-0005: pytest verde, cobertura ≥ 89 %, storage.py ≥ 90 %, totales ruff/mypy ≤ 489/44)
PYTHONIOENCODING=utf-8 python scripts/check.py
pytest tests/test_storage.py tests/test_services.py tests/test_domain_error_handler.py -q
```

## Residuales
- **SEC3** — `storage.py` `upload_image`: `detail=f"Fallo al comunicar con Azure CDN: {str(e)}"` se conserva letra a letra
  (filtra el error interno). Destino: ya en `B-HIGIENE` (fila SEC3); sin fila nueva.
- **A6** — `print()` en `delete_image` y en el `except` de `promote_to_permanent`. Ya en `B-HIGIENE`; sin fila nueva.
- **A4** — `security.py` mypy ×2 (`SECRET_KEY: str | None` a `jwt.encode`) y `os.getenv` en `storage.__init__`. Ya en `B-PAGOS`.
- **S1** — 10 errores mypy `Column[...]` en `tourist_services_service.py`. Ya en `B-S1`.
- **§9** — `conftest.py:79` `MagicMock()` sin spec; fixture local `admin_token` en `test_services.py:24-48` construye el
  usuario a mano. Ya en `B-TESTS`.
- **Nuevo (sugerencia de fila)** — `BE-nn | plan BE-01 | InvalidImageUrlError responde 400 en vez de 422 por
  contrato con el cliente Flutter (el 422 de Pydantic tiene forma {"detalle": [...]}, main.py:85-88; el 400 de
  dominio {"detail": str}). | Baja | Decidir en B-HIGIENE (junto a P2) | Remapear InvalidImageUrlError a 422 en
  _DOMAIN_ERROR_STATUS cuando P2 unifique la forma del 422; actualizar el parametrize del handler y los tests de
  servicios; sin cambios en el servicio ni en el adaptador.`
- **Nuevo (sugerencia de fila)** — `BE-nn | plan BE-01 | Blobs compartidos: PUT acepta una URL permanente de otro paquete;
  al quitarla después, delete_image borra el blob y rompe la imagen del otro paquete. | Media | Decidir en B-HIGIENE |
  Rechazar en PUT las URLs permanentes que no pertenezcan ya al paquete, o no borrar blobs referenciados por otros.`
- Rincón 5 de la verificación (cp1252 en `check.py`) quedó resuelto en `cdb086b`; no requiere fila.

## Referencias
- Context7 no estaba disponible en esta sesión (`mcp__context7__resolve-library-id` → "No such tool available"); cada
  API se confirmó contra el código fuente del paquete instalado en `venv/`.
- azure-storage-blob · 12.30.1 · `azure.storage.blob.aio.BlobClient.start_copy_from_url(source_url, **kwargs)`: kwarg
  `requires_sync: bool` ("Set requires_sync to True to force the copy to be synchronous"); devuelve dict con `copy_status`
  (`"success"` si fue síncrona, `"pending"` si no) · `BlobClient.exists() -> bool` · `BlobClient.delete_blob()` ·
  `ContainerClient.url` (property) · https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.aio.blobclient ·
  REST subyacente: https://learn.microsoft.com/rest/api/storageservices/copy-blob-from-url
- azure-core (dependencia de la anterior) · `azure.core.exceptions.AzureError` es la base de `HttpResponseError`,
  `ResourceNotFoundError` y `ServiceRequestError` (verificado por `__mro__`) ·
  https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions
- Starlette · 1.6.0 · `starlette.status.HTTP_400_BAD_REQUEST` y `HTTP_415_UNSUPPORTED_MEDIA_TYPE` (ya usados en
  `main.py` / `storage.py`); el `HTTP_422_UNPROCESSABLE_ENTITY` deprecado de `main.py:86` es S5 y no se toca ·
  https://www.starlette.io/
- Python 3.14 stdlib · `unittest.mock.create_autospec` produce `AsyncMock` para corrutinas (verificado sobre
  `BlobClient.start_copy_from_url`) · https://docs.python.org/3/library/unittest.mock.html#unittest.mock.create_autospec
- FastAPI 0.141.1 / Pydantic 2.13.5: el plan no introduce ninguna API nueva de estas librerías.
- Decisión no trivial → `docs/deuda/BE-01/adr-0006-borrador-adaptador-lanza-errores-de-dominio.md`, **aceptado por
  David el 2026-10-27** (con 400 en vez de 422). Permanece en esta carpeta; David lo mueve a `docs/adr/` en un commit
  propio antes del PR, cuando la sección de evidencia tenga los números reales (ojo: el ADR de pagos también espera
  "el siguiente número libre"). El ejecutor y el auditor **no** lo mueven.

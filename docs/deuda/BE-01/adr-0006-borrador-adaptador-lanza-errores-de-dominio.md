# ADR-0006 (BORRADOR) — El adaptador de almacenamiento lanza excepciones de dominio; política de URLs de imagen y copia síncrona

- **Estado:** **aceptado por David el 2026-10-27** (propuesto por el plan de BE-01 el mismo día), con un cambio
  respecto al borrador inicial: `InvalidImageUrlError` → **400**, no 422 (ver Decisión 2 y Alternativas).
  Permanece en `docs/deuda/BE-01/` hasta que David lo mueva, en un commit propio antes del PR, a
  `docs/adr/0006-adaptador-de-almacenamiento-lanza-errores-de-dominio.md` con la sección de evidencia rellenada
  con los números reales; tomará el siguiente número libre (comprobar que el ADR de pagos no lo haya ocupado
  antes). Ni el ejecutor ni el auditor lo mueven.
- **Supersede parcialmente:** ADR-0003, apartado "Residuos declarados (vigentes)", primer punto
  (`app/core/storage.py` conserva `HTTPException` 415/500). El resto de ADR-0003 sigue vigente.
- **Relación:** ADR-0003 (handler global y tabla `_DOMAIN_ERROR_STATUS`), ADR-0005 (trinquete), backlog BE-01, A7, P1.

## Contexto

ADR-0003 sacó `HTTPException` de los servicios y admitió como residuo que el adaptador de Azure
(`app/core/storage.py`) siguiera lanzando `HTTPException` 415/500 "por ser infraestructura". La verificación de
BE-01 (2026-10-25, re-verificada 2026-10-27) mostró tres consecuencias de ese residuo:

1. `app.services.tourist_services_service → app.core.storage → fastapi` rompe el contrato de `import-linter`
   "Los servicios no conocen el transporte HTTP" (la otra ruta, `core.security`, son imports muertos: P1).
2. `promote_to_permanent` envuelve en `HTTPException(500)` tres situaciones distintas: URL ajena al CDN, blob
   inexistente y fallo real de Azure. El cliente recibe 500 por un error que es suyo (400) y no distingue la
   caída del CDN (503).
3. El `except Exception` del servicio (`image_uploader`) convierte el 415 del adaptador en 503, de modo que el
   415 nunca llega al cliente. La "hipótesis para BE-01" de ADR-0003 se resolvió a favor de "es el
   `HTTPException(500)` admitido como residuo".

Además, `start_copy_from_url(temp_url)` acepta cualquier URL (el servicio comprueba el contenedor con `in`
por substring) y borra el origen sin esperar la copia (A7).

## Decisión

1. **El adaptador habla el idioma del dominio.** `AzureStorageClient` lanza subclases de `DomainError`
   definidas en `app/core/exceptions.py`: `UnsupportedMediaTypeError` (MIME no imagen), `InvalidImageUrlError`
   (URL fuera del contenedor temporal propio o blob inexistente) y `StorageUnavailableError` (cualquier
   `azure.core.exceptions.AzureError` o copia no completada). Nunca `HTTPException`. Los servicios **no**
   vuelven a envolver estos fallos: un único punto de traducción por frontera (infra → dominio en el
   adaptador; dominio → HTTP en `app/main.py`).
2. **Tabla del handler (ADR-0003):** `UnsupportedMediaTypeError → 415`, `InvalidImageUrlError → 400`
   (`status.HTTP_400_BAD_REQUEST`), `StorageUnavailableError → 503` (ya existía). **400 y no 422 por contrato
   con el cliente Flutter:** el 422 que hoy emite `/servicios/` (handler de `RequestValidationError`,
   `main.py:85-88`) tiene forma `{"detalle": [...]}` y el cliente la parsea como lista; el 400 con
   `{"detail": str}` ya lo recibe este endpoint (`BusinessRuleViolationError`). Es la misma lógica con la que
   ADR-0003 mantuvo `AlreadyExistsError` en 400 en vez de 409. Se conserva la excepción propia
   `InvalidImageUrlError` (no se reutiliza `BusinessRuleViolationError`) para que el remapeo a 422 sea un cambio
   de una línea en la tabla cuando P2 unifique la forma del 422.
3. **Lista blanca de URLs.** `promote_to_permanent` solo copia blobs cuyo URL empiece exactamente por
   `<url del contenedor temporal de la cuenta>/`; el servicio decide la política por operación: al crear, toda
   imagen debe ser temporal; al actualizar, temporal → se promueve, permanente propia → se conserva, otra → 400.
   Nada externo al CDN entra en un paquete.
4. **Copia síncrona antes de borrar (A7).** `start_copy_from_url(url, requires_sync=True)`; se borra el origen
   solo si `copy_status == "success"`; en cualquier otro caso se lanza `StorageUnavailableError` y el blob
   temporal sobrevive. Premisa verificada por David en el portal de Azure (2026-10-27): los contenedores
   `temp-ecotur-images` y `ecotur-images` están en nivel de acceso **Blob** (lectura anónima de blobs), por lo
   que el origen es legible por URL desde el servicio de copia.

## Consecuencias

- Positivas: `lint-imports` → 4 KEPT por construcción; los códigos HTTP siguen en un único sitio; el cliente
  distingue su error (400) de la caída del CDN (503) con una forma de respuesta que ya maneja; cierra la copia
  de contenido arbitrario de Internet al CDN; sin pérdida de imágenes por copia inacabada.
- Negativas / aceptadas: `app/core/storage.py` importa `app/core/exceptions.py` (mismo paquete `core`; no viola
  ningún contrato). Un error de programación no derivado de `AzureError` ya no se disfraza de 503: sale como 500
  real, que es lo correcto. Una URL semánticamente inválida responde 400 y no el 422 más preciso: deuda
  residual anotada en el backlog (remapear `InvalidImageUrlError` a 422 cuando P2 unifique la forma del 422).
  `requires_sync=True` depende del nivel de acceso Blob de los contenedores (verificado); si ese nivel cambiara
  (p. ej. a privado con SAS), la alternativa documentada es copia asíncrona + sondeo de `copy_status` con
  `get_blob_properties` antes de `delete_blob` (ver Alternativas).
- Contrato visible: `PUT /servicios/{id}` pasa de 200 a 400 cuando alguna URL es externa al CDN (fase D del plan;
  aprobada por David el 2026-10-27, recortable si no cabe en el día sin afectar a las fases anteriores).

## Alternativas consideradas

- **Excepciones "de infraestructura" propias del adaptador que el servicio traduce a dominio.** Descartada:
  añade una segunda tabla de traducción y un `try/except` por llamada en cada servicio; `StorageUnavailableError`
  ya era de facto la excepción del adaptador.
- **Mantener el `except Exception` del servicio y añadir `except DomainError: raise`.** Descartada: parchea el
  síntoma (415 tragado) sin quitar la causa (doble traducción); ante un jurado es difícil de justificar.
- **Validar la URL solo en el servicio.** Descartada: el adaptador es quien llama a `start_copy_from_url`; la
  guarda contra copiar URLs arbitrarias debe vivir donde se hace la copia (defensa en profundidad), y la
  política por operación (crear vs actualizar) donde vive la regla de negocio.
- **Sondear `copy_status` en vez de `requires_sync`.** Descartada hoy: más código (bucle + espera) para blobs
  de pocos MB que la copia síncrona resuelve en una llamada, y la premisa de lectura por URL está verificada.
  Queda documentada como la alternativa a aplicar si el nivel de acceso de los contenedores deja de ser Blob.
- **422 (`HTTP_422_UNPROCESSABLE_CONTENT`) en lugar de 400 para la URL inválida.** Era la opción del backlog y
  del borrador inicial, y es la semánticamente más precisa. Descartada por David (2026-10-27) por contrato con el
  cliente Flutter: el 422 que ya emite este endpoint tiene forma `{"detalle": [...]}` parseada como lista, y un
  422 con `{"detail": str}` rompería ese parseo; el 400 con `{"detail": str}` es una forma que el cliente ya
  recibe aquí. Misma lógica que ADR-0003 con `AlreadyExistsError` (400 en vez de 409). El remapeo a 422 queda
  como residual del backlog, condicionado a que P2 unifique la forma del 422.
- **Reutilizar `BusinessRuleViolationError` (400) en lugar de una excepción propia.** Descartada: perdería el
  punto de remapeo a 422 y mezclaría "URL fuera de la lista blanca" con reglas de negocio ajenas (11 imágenes).

## Evidencia (a completar por el ejecutor/auditor)

- `lint-imports` → "Contracts: 4 kept, 0 broken." · `grep -rn "HTTPException" app/core tests` → vacío.
- Cobertura de `app/core/storage.py` ≥ 90 % (línea base 28 %). Suite completa en verde.

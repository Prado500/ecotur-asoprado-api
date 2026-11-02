# ADR-0003 — Manejo de errores agnóstico al transporte: excepciones de dominio + un handler global

- **Estado:** aceptado (retroactivo). El primer punto de "Residuos declarados" (`storage.py` conserva `HTTPException`)
  está **superado por ADR-0006** (27 oct 2026); el resto sigue vigente.
- **Fecha de la decisión:** 2026-10-10 · **Fecha de registro en este formato:** 2026-10-24
- **Ubicación en el repo:** `docs/adr/0003-manejo-de-errores-agnostico-al-transporte.md`
- **Origen:** `ADR_NOTE.md` (flujo agéntico v0), reescrito al formato de la casa sin cambiar
  ninguna decisión. Plan de contexto: `docs/archive/planes/plan-consolidado-servicios.md`
  (fases A, B, C, D). Commits: `e581c6a` (A), `cf115a0` (B), `9cd96c0` (C), `aab1d3a` (D).

## Decisión (resumen)

Los servicios (`app/services/`) lanzan **exclusivamente excepciones de dominio**, subclases de
`DomainError` (`app/core/exceptions.py`), con un único `detail: str` y **sin código HTTP**. Un
**único handler global** en `app/main.py` (`domain_error_handler` + tabla `_DOMAIN_ERROR_STATUS`)
traduce cada tipo a su respuesta HTTP. Los códigos HTTP viven en un solo lugar.

## Contexto

La capa de servicios mezclaba reglas de negocio con semántica de transporte: importaba
`HTTPException`, `status` y `UploadFile` de FastAPI. Eso acoplaba el dominio al framework y
dispersaba las decisiones HTTP (códigos, headers, payloads) por toda la capa de negocio. Es la
violación más visible de Clean Architecture ante un jurado: la capa interna conoce la externa.

## Decisión (detalle)

### Mapeo en el adaptador (`app/main.py`)
| Excepción de dominio | HTTP |
|---|---|
| `AuthorizationError` | 403 |
| `NotFoundError` | 404 |
| `AlreadyExistsError` | 400 (ver consecuencias: migración a 409 diferida) |
| `InvalidCredentialsError` | 401 |
| `AccountNotActiveError` | 403 |
| `InvalidVerificationTokenError` | 400 |
| `BusinessRuleViolationError` | 400 |
| `StorageUnavailableError` | 503 |

Todas responden `{"detail": exc.detail}` preservando los mensajes existentes letra a letra: el
contrato visible para el cliente no cambió.

### 401 con `WWW-Authenticate`
`InvalidCredentialsError` mapea a 401 y el handler adjunta `WWW-Authenticate: Bearer` (RFC 7235:
una respuesta 401 debe anunciar el esquema de autenticación). Se implementa de forma genérica:
si el código mapeado es 401, se adjunta el header; sin lógica por excepción.

### Fallback: 500 para subtipos desconocidos
`_DOMAIN_ERROR_STATUS.get(type(exc), 500)`: una subclase de `DomainError` sin entrada en la tabla
degrada a 500 con su `detail`, en lugar de un stack trace no manejado. **Regla operativa que se
desprende:** toda excepción de dominio nueva debe registrarse en la tabla en el mismo PR que la
crea; un test parametrizado sobre la tabla lo hace cumplir.

### Contrato neutro de upload
Misma filosofía aplicada a datos: `BackgroundTasks` (fase B) y `UploadFile` (fase C) salieron de
los servicios. El transporte decide **cuándo** se agenda el correo y **cómo** se bufferea el
multipart; el servicio recibe `RegistrationResult` / `List[StagedImage]` (`NamedTuple` en
`app/core/storage.py`).

## Consecuencias

- **Positivas:** `grep -R "from fastapi import" app/services/` → cero resultados (verificado por
  David el 23 oct); los códigos HTTP se deciden en un solo sitio; la taxonomía futura falla de
  forma segura. Desde el 24 oct, `import-linter` hará cumplir la regla con exit code
  (`app.services` no puede importar `fastapi`), para que no dependa de la memoria de nadie.
- **Residuos declarados (vigentes):**
  - `app/core/storage.py` conserva `HTTPException` (415/500): es infraestructura (cliente Azure),
    no servicio; el check de MIME 415 es guarda de seguridad del transporte de bytes.
  - `AlreadyExistsError` → 400 hoy; 409 es semánticamente correcto. Migración diferida para no
    alterar el contrato del cliente → **backlog BE-23** (decidir si entra en esta entrega: toca
    el manejo de errores en Flutter).
  - Handlers preexistentes intactos: `RequestValidationError` → 422, `IntegrityError` → 409.
- **Relación con ADR-0002:** `DateAlreadyReserved` (reservas) nacerá del `IntegrityError` del
  índice único parcial. Debe **registrarse en `_DOMAIN_ERROR_STATUS` → 409**; si se olvida, el
  fallback la degradará a 500.
- **Hipótesis para BE-01** (500 "Fallo al consolidar las imágenes en el CDN"): o es una
  excepción de dominio no registrada (fallback 500) o es el `HTTPException(500)` que este ADR
  admite en `storage.py`. Se verifica el día 2 al pasar BE-01 por el flujo.

## Alternativas consideradas

- **Un handler por excepción:** descartado. Multiplica superficie y duplica lógica; una tabla +
  un handler genérico es la opción de menor superficie y mayor previsibilidad para el MVP.
- **Mantener `HTTPException` en servicios "por velocidad":** descartado. Los handlers globales ya
  existen; la velocidad no se gana y el acoplamiento se paga en cada test.

## Evidencia

- `pytest`: 116 passed (suite completa en verde al cierre de la fase C).
- 10 tests nuevos (fase C) + suites de A y B congelan el comportamiento: 415 unitario en storage,
  400 con 11 imágenes, 503 con contrato `StagedImage`, 404 antes que 403, parametrize del handler
  con 8 entradas.
- `grep -R "from fastapi import" app/services/` → 0.

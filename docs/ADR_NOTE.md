# ADR_NOTE — Transport-Agnostic Error Handling Strategy

**Status:** Accepted
**Date:** 2026-10-10
**Context plan:** `docs/plan-consolidado-servicios.md` (Fases A, B, C, D)
**Commits:** `e581c6a` (A), `cf115a0` (B), `9cd96c0` (C)

---

## Contexto y trade-off

La capa de servicios (`app/services/`) mezclaba reglas de negocio con semántica
de transporte: importaba `HTTPException`, `status` y `UploadFile` de FastAPI, lo
que acoplaba el dominio al framework y dispersaba las decisiones HTTP (códigos,
headers, payloads) por toda la capa de negocio.

**Decisión:** aplicar un flujo de errores transport-agnostic:

1. **Servicios**: lanzan exclusivamente excepciones de dominio
   (`app/core/exceptions.py`), todas subclases de `DomainError`, que cargan un
   único `detail: str` legible y **ningún** código HTTP.
2. **Adaptador**: un único handler global en `app/main.py`
   (`domain_error_handler` + tabla `_DOMAIN_ERROR_STATUS`) traduce cada tipo a
   su respuesta HTTP. Los códigos HTTP viven en un solo lugar.

El trade-off asumido (per AGENTS.md): se sacrifica el handler "uno por
excepción" a favor de una tabla DRY con un handler genérico. Es la opción de
menor superficie y mayor previsibilidad para el MVP.

## Mapeo en el adaptador (`app/main.py`)

| Excepción de dominio | HTTP |
|---|---|
| `AuthorizationError` | 403 |
| `NotFoundError` | 404 |
| `AlreadyExistsError` | 400 |
| `InvalidCredentialsError` | 401 |
| `AccountNotActiveError` | 403 |
| `InvalidVerificationTokenError` | 400 |
| `BusinessRuleViolationError` | 400 |
| `StorageUnavailableError` | 503 |

Todos responden `{"detail": exc.detail}` preservando los mensajes existentes
letra a letra: el contrato visible para el cliente no cambió en ningún caso.

## Caso especial: 401 con `WWW-Authenticate`

`InvalidCredentialsError` mapea a 401 y el handler adjunta
`WWW-Authenticate: Bearer` por RFC 7235 (la respuesta 401 debe anunciar el
esquema de autenticación). Se implementa de forma genérica en el handler: si el
código mapeado es 401, se adjunta el header — sin lógica por excepción.

## Fallback: 500 para subtipos desconocidos

`_DOMAIN_ERROR_STATUS.get(type(exc), 500)`: una subclase de `DomainError` sin
entrada en la tabla degrada a 500 con su `detail`, en lugar de producir un
stack trace no manejado. Garantiza que toda la taxonomía futura falle de forma
segura hasta que se registre su código.

## Residuos documentados

- **`app/core/storage.py` conserva `HTTPException` (415/500)**: es capa de
  infraestructura (cliente Azure), no servicio. El check de MIME 415 vive ahí
  por ser guarda de seguridad del transporte de bytes. La simetría exigida
  (cero `from fastapi import` en `app/services/`) se cumple al 100%: `grep`
  arroja **cero** resultados.
- **Migración 409 diferida**: `AlreadyExistsError` mapea a 400 hoy. Migrar
  duplicados a 409 (más correcto semánticamente) es trabajo futuro explícito,
  fuera del alcance de este plan, para no alterar el contrato HTTP actual.
- Los handlers preexistentes (`RequestValidationError` → 422, `IntegrityError`
  → 409) no se tocaron.

## Contrato neutro de upload (coherencia con BackgroundTasks)

Misma filosofía aplicada a datos: `BackgroundTasks` (Fase B) y `UploadFile`
(Fase C) salieron de los servicios. El transporte decide **cuándo** se agenda
el correo y **cómo** se bufferea el multipart; el servicio recibe
`RegistrationResult` / `List[StagedImage]` (NamedTuple en `app/core/storage.py`).

## Verificación

- `pytest`: 116 passed (suite completa en verde).
- `grep -R "from fastapi import" app/services/`: cero resultados.
- 10 tests nuevos (Fase C) + suites de A y B congelan el comportamiento:
  415 unitario en storage, 400 con 11 imágenes, 503 con contrato `StagedImage`
  bien formado, 404 antes que 403, y el parametrize del handler con 8 entradas.

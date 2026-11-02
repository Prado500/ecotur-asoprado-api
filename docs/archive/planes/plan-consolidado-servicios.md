# PLAN CONSOLIDADO DEFINITIVO — "Capa de servicios transport-agnostic"

**Objetivo:** eliminar de `app/services/` toda lógica de autorización dispersa y todo acoplamiento a semántica HTTP, con excepciones de dominio traducidas por un único handler en la capa de adaptadores.

**Decisiones bloqueadas:** (1) duplicados pasarán a 409 como trabajo futuro documentado — *no* en este plan; (2) taxonomía de excepciones aprobada; (3) `BackgroundTasks` se mueve al router (el transporte decide CUÁNDO); (4) un solo handler DRY con tabla de mapeo; (5) secuencia A→B→C, suite verde entre fases, commits atómicos.

**Regla de alcance:** simetría exigida = cero `from fastapi import ...` en `app/services/`. `app/core/` (storage) y `app/api/` (dependencies, routers) son capas de infraestructura/adaptadores y pueden conservar `HTTPException` — esto se documentará en el ADR_NOTE.

---

## 0. Taxonomía de excepciones (`app/core/exceptions.py`)

Base común `DomainError(Exception)` con atributo `detail: str` (patrón ya existente en `AuthorizationError`). Todas las nuevas heredan de ella. **Los códigos HTTP NO viven aquí**: viven en `main.py`.

| Excepción | Lugar de uso | Código mapeado |
|---|---|---|
| `AuthorizationError` (existente, refactorizada para heredar de `DomainError`) | Política | 403 |
| `NotFoundError` | user (404s), tourist (paquete inexistente) | 404 |
| `AlreadyExistsError` | user (duplicados) | **400** (hoy; 409 será la migración futura) |
| `InvalidCredentialsError` | user (login) | 401 + header especial |
| `AccountNotActiveError` | user (login cuenta no verificada) | 403 |
| `InvalidVerificationTokenError` | user (token inválido/expirado/scope malo) | 400 |
| `BusinessRuleViolationError` | tourist (límite de imágenes, no está en papelera) | 400 |
| `StorageUnavailableError` | tourist (fallo CDN) | 503 |

**Handler en `main.py` (Fase B):** se sustituye el `authorization_error_handler` actual por UN handler genérico de `DomainError` + tabla `_DOMAIN_ERROR_STATUS: dict[type, int]`:

- Caso especial documentado y testeado: si el código es 401, adjuntar `WWW-Authenticate: Bearer`.
- Fallback documentado y testeado: subclase sin entrada en la tabla → 500.
- Los handlers existentes (`RequestValidationError` → 422, `IntegrityError` → 409) no se tocan.

---

## Fase A — `audit_service` (la más pequeña)

**Archivos:**

1. `app/services/user_access_policy.py`: añadir `assert_is_admin_plus(actor: User) -> None` — lanza `AuthorizationError` con el mensaje EXACTO actual: `"Privilegios insuficientes para visualizar la auditoría del sistema."`. Docstring Google Style. Nombre genérico (regla de tier administrativo, reutilizable).
2. `app/services/audit_service.py`: constructor recibe `user_access_policy`; `retrieve_audit_history` sustituye el bloque L64-68 por `self.user_access_policy.assert_is_admin_plus(current_user)`; eliminar `from fastapi import HTTPException, status` y el import de `UserRole` (queda huérfano). Resultado: **cero imports FastAPI, cero comparaciones de rol**.
3. `app/api/dependencies.py`: `get_audit_service(audit_repo=..., user_access_policy=Depends(get_user_access_policy))`. `get_user_service` y `get_service_service` no cambian (reciben `AuditService` ya construido).
4. `app/api/routers/audit.py`: `router = APIRouter(dependencies=[Depends(get_current_admin_user)])` (gate a nivel router, NO en la firma); el endpoint conserva `usuario_actual: User = Depends(get_current_user)` SOLO como identidad para la política (FastAPI cachea la dependencia: una sola evaluación por request). Docstring actualizado explicando defensa en profundidad.

**Tests (RED primero, per test-sanitizer):**

- Política: happy `assert_is_admin_plus` superadmin ✓ y admin ✓; unhappy: tourist lanza `AuthorizationError`; edge: dos usuarios idénticos en todo salvo el rol (la regla depende SOLO del rol); edge: usuario con rol válido y datos degenerados (cédula vacía) sigue permitido (el método no inspecciona nada más).
- Servicio (repo `autospec=True`): tourist → `AuthorizationError` y `get_all_audit_logs` NUNCA se llama; admin → repo llamado exactamente una vez con los args correctos (`assert_called_once_with`).
- Integración: turista → 403 (test existente intacto y verde); admin → 200 (nuevo); sin token → 401 (nuevo, prueba el gate del router).
- GREEN: implementar; suite completa verde.

---

## Fase B — `user_service` (la grande)

### 1. `BackgroundTasks` → transporte (decisión 3)

- El servicio deja de recibir `background_tasks` y `base_url`; `register_tourist(self, user_data)` retorna `RegistrationResult = NamedTuple("RegistrationResult", [("user", User), ("verification_token", str)])` (definido en el propio módulo de servicio).
- El router `registrar_turista` ya recibe `BackgroundTasks`: desempaca el resultado, hace `background_tasks.add_task(send_verification_email, email_to=..., first_name=..., token=..., base_url=frontend_url)` y retorna `result.user` (el `response_model=UserResponse` no cambia). El import de `send_verification_email` pasa al router. La lógica del token (`create_verification_token`) se queda en el servicio: el negocio decide QUÉ, el transporte CUÁNDO.
- **Test existente que DEBE actualizarse (RED):** `tests/test_auth.py` usa `patch("app.services.user_service.send_verification_email")` — el patch path pasa a `"app.api.routers.user.send_verification_email"`. La aserción `mock_send_email.assert_called_once()` se conserva.

### 2. Conversión de excepciones (mensajes letra a letra preservados)

| Sitio actual | Nueva excepción |
|---|---|
| `register_tourist` duplicado (400) | `AlreadyExistsError` |
| `verify_email_account`: scope/None, expirado, corrupto (400) | `InvalidVerificationTokenError` (3 mensajes distintos, mismo tipo) |
| `verify_email_account`: usuario no encontrado (404) | `NotFoundError` |
| `authenticate_user`: credenciales malas (401) | `InvalidCredentialsError` |
| `authenticate_user`: cuenta inactiva (403) | `AccountNotActiveError` |
| `delete`/`update`/`recover`: objetivo inexistente (404) | `NotFoundError` (se mantiene el orden 404 → política → mutación) |
| `create_administrative_account`: duplicado (400) | `AlreadyExistsError` |

- Al final: `user_service.py` sin imports de FastAPI (`BackgroundTasks`, `HTTPException`, `status` fuera). `jwt`, `core.security`, `core.exceptions` permanecen.

### 3. Handler unificado en `main.py`

Implementar el handler + tabla de la sección 0 (con las 6 entradas de esta fase) y reemplazar `authorization_error_handler`. `AuthorizationError` se refactoriza para heredar de `DomainError` (su handler individual desaparece; la tabla lo absorbe).

**Tests (RED primero):**

- Handler (unitarios): cada tipo de la tabla → su código; `InvalidCredentialsError` → 401 CON header `WWW-Authenticate`; subclase desconocida → 500; `detail` presente en el JSON.
- Servicio: ordenamiento — actor sin rango sobre objetivo INEXISTENTE → `NotFoundError` (no `AuthorizationError`).
- Integración: login malo → 401 con header; duplicado → 400; token inválido → 400; 404 antes de 403 en `patch`/`delete` sobre cédula inexistente; el flujo feliz de registro sigue enviando el correo (mock en el router) y retornando 201.
- Suites existentes intactas y verdes.

---

## Fase C — `tourist_services_service`

### 1. `UploadFile` → contrato neutro (coherencia con la decisión de BackgroundTasks)

- En `app/core/storage.py` (infraestructura): definir `StagedImage = NamedTuple("StagedImage", [("filename", str), ("content_type", str), ("content", bytes)])` y cambiar `upload_image(self, image: StagedImage)` usando `image.content` en vez de `file.read()` (sin `.close()`; ya son bytes). El resto de storage.py (HTTPException 415/500) **se queda igual**: es capa de infraestructura.
- En `routers/service.py` (`upload_images`): leer cada `UploadFile` → construir `StagedImage` → cerrar el archivo. El parsing multipart vive en transporte.
- En el servicio: `image_uploader(self, images_files: List[StagedImage])`; su `try/except Exception` pasa a lanzar `StorageUnavailableError` (mismo mensaje actual, incluye el detalle del error). El catch sigue capturando el `HTTPException(500)` interno de storage y lo traduce a 503 — comportamiento actual preservado.

### 2. Conversión de excepciones

| Sitio actual | Nueva excepción |
|---|---|
| Límite de 10 imágenes (3 sitios: create, uploader, update — 400) | `BusinessRuleViolationError` (mensaje preservado) |
| Paquete no encontrado (toggle, soft_delete, update — 404) | `NotFoundError` |
| Recuperar paquete no eliminado (400) | `BusinessRuleViolationError` |
| Fallo CDN (503) | `StorageUnavailableError` |

- Al final: `tourist_services_service.py` sin `HTTPException`, `status` ni `UploadFile`.

**Tests (RED primero):**

- 400 con 11 imágenes en el endpoint de upload (no existe hoy; el de update sí).
- 415 con MIME no-imagen (congela el check que vive en storage).
- 503: mock `upload_image` (`spec=AzureStorageClient`) lanzando excepción → la respuesta es 503 y el mock fue llamado con un `StagedImage` bien formado.
- 404 en toggle/delete/update sobre ID inexistente (unhappy paths inexistentes hoy).
- Verdes sin tocar: los tests felices de update/upload/deactivate/recover.

---

## Fase D — Verificación, documentación y entrega

1. `pytest` completo en verde tras cada fase (nunca commitear en rojo).
2. Grep de verificación: `from fastapi import` en `app/services/` = **cero resultados**.
3. **ADR_NOTE** (per AGENTS.md): estrategia de errores de dominio + mapeo en adaptador; caso especial 401; fallback 500; residuos documentados (`storage.py` conserva HTTPException por ser infraestructura); migración 409 diferida (enlace al prompt de abajo).
4. Commits atómicos:
   - A: `refactor(audit): centralize audit authorization in access policy and router gate`
   - B: `refactor(user): replace transport coupling with domain errors and move email scheduling to router`
   - C: `refactor(tourist): replace transport coupling with domain errors and neutral upload contract`
   - D: `docs(adr): record transport-agnostic error handling strategy`
5. PR description (título imperativo + Por qué / Organización A-B-C / Cómo se probó / Residuales / Referencias) y **squash merge** con mensaje redactado nuevo (validado con Conventional Commits: el mantenedor redacta el mensaje del merge, no se recicla el último commit message).

**Riesgos controlados:** el único cambio de contrato interno visible para el cliente es ninguno (todos los códigos/mensajes se preservan); el único test existente que se edita es el patch path del mock de correo; el orden 404→403 queda congelado por tests nuevos.

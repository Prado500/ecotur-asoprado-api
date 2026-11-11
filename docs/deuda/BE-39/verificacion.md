# Verificación — BE-39: ningún test HTTP depende del guard de rol

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A, fila `BE-39`, l.83; origen `docs/deuda/A2/verificacion.md`, mutantes M1–M7) + ADR-0012 (punto 4 de la decisión y addendum del 6 nov)
**Fecha:** 2026-11-11

## Qué describe el ítem

Con el guard admin sin comprobar el rol (M7), sin guard en `/servicios` (M1–M3), con `/usuarios` admin bajo
`get_current_user` (M6) o sin guard en `/auditoria` (M4), la suite sigue en verde: ninguna de las 14 rutas con guard
admin tiene un test HTTP que caiga si el guard desaparece. El único test HTTP de turista contra guard admin
(`tests/test_audit.py`, `GET /auditoria/`) queda tapado por el re-chequeo de `audit_service.py:65`. El trabajo: un test de
rechazo por ruta protegida (14 admin + 3 de usuario): sin token → 401 con `WWW-Authenticate`, rol inferior → 403, con
estructura del JSON y sin texto, en RED frente a M1–M7.

## Evidencia en el código

### El guard que nadie vigila

- `app/api/dependencies.py:143` — `async def get_current_admin_user(current_user: User = Depends(get_current_user))`;
  la comprobación de rol está en l.156: `if current_user.role not in [UserRole.admin, UserRole.superadmin]:` → 403
  `Privilegios insuficientes.` sin cabecera `WWW-Authenticate` (l.157-159).
- `app/api/dependencies.py:89-140` — `get_current_user`; 401 con `headers={"WWW-Authenticate": "Bearer"}` (l.112-116,
  l.125-130). Sin token, el 401 lo da `oauth2_scheme` (l.19, `OAuth2PasswordBearer`).
- Guards de router (las 14 rutas admin cuelgan de uno de estos tres):
  - `app/api/routers/user.py:37` — `admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])`
  - `app/api/routers/service.py:24` — ídem para `/servicios` admin.
  - `app/api/routers/audit.py:8` — `router = APIRouter(dependencies=[Depends(get_current_admin_user)])`
- Identidad en el handler (segunda capa del mismo guard, por eso M1 sola no cae ni aunque hubiera tests):
  `app/api/routers/service.py:89,146,170,191,212,234` (`= Depends(get_current_admin_user)`); `app/api/routers/user.py:21`
  (`AdminDep`), usado en l.182, 201, 220, 243.
- Guard de usuario: `app/api/routers/user.py:36` (`self_service_router = APIRouter(dependencies=[Depends(get_current_user)])`)
  y `UserDep` (l.20) en los tres handlers (l.117, 131, 153).

### Las 17 rutas protegidas (medido sobre `app.routes`, 26 rutas en total incluidas `/docs`, `/redoc`, `/openapi.json`)

| # | Ruta | Declarada en | Guard |
|---|---|---|---|
| 1 | `GET /usuarios/` | `app/api/routers/user.py:180` | admin (router + `AdminDep`) |
| 2 | `GET /usuarios/admin/eliminados` | `app/api/routers/user.py:199` | admin (router + `AdminDep`) |
| 3 | `PATCH /usuarios/{cedula}/recuperar` | `app/api/routers/user.py:218` | admin (router + `AdminDep`) |
| 4 | `POST /usuarios/admin` | `app/api/routers/user.py:240` | admin (router + `AdminDep`) + política de superadmin |
| 5 | `POST /servicios/upload-images/` | `app/api/routers/service.py:50` | admin (router) |
| 6 | `POST /servicios/` | `app/api/routers/service.py:86` | admin (router + handler) |
| 7 | `GET /servicios/admin/inactivos` | `app/api/routers/service.py:110` | admin (router) |
| 8 | `GET /servicios/admin/eliminados` | `app/api/routers/service.py:126` | admin (router) |
| 9 | `PUT /servicios/{service_id}` | `app/api/routers/service.py:142` | admin (router + handler) |
| 10 | `PATCH /servicios/{service_id}/activar` | `app/api/routers/service.py:166` | admin (router + handler) |
| 11 | `PATCH /servicios/{service_id}/desactivar` | `app/api/routers/service.py:187` | admin (router + handler) |
| 12 | `DELETE /servicios/{service_id}` | `app/api/routers/service.py:208` | admin (router + handler) |
| 13 | `PATCH /servicios/{service_id}/recuperar` | `app/api/routers/service.py:230` | admin (router + handler) |
| 14 | `GET /auditoria/` | `app/api/routers/audit.py:11` | admin (router) + re-chequeo `audit_service.py:65` |
| 15 | `GET /usuarios/mi-perfil` | `app/api/routers/user.py:116` | user (router + `UserDep`) |
| 16 | `DELETE /usuarios/{cedula}` | `app/api/routers/user.py:129` | user (router + `UserDep`) |
| 17 | `PATCH /usuarios/{cedula}` | `app/api/routers/user.py:149` | user (router + `UserDep`) |

Respuestas medidas hoy sin mutar (sonda HTTP en copia desechable): las 17 dan **401** anónimo con
`www-authenticate: Bearer` y cuerpo `{"detail"}`; las 14 admin dan **403** a un turista, cuerpo `dict`, sin
`www-authenticate`. Las 3 de usuario no tienen "rol inferior": un turista pasa el guard (mi-perfil 200; `DELETE`/`PATCH`
de una cédula inexistente 404/422).

### Lo que la suite comprueba hoy de esas rutas (inventario completo de `tests/`)

- **Rechazo por rol en ruta admin — 1 test:** `tests/test_audit.py:50` `test_audit_trail_forbidden_for_tourist`
  (petición l.56, `assert response.status_code == 403` l.58, `isinstance(... ["detail"], str)` l.59). Sin aserción de
  `set(body)` ni de ausencia de `www-authenticate`.
- **Rechazo sin token en ruta admin — 1 test:** `tests/test_audit.py:140` `test_audit_trail_requires_authentication`
  (petición l.142, `== 401` l.144, `"detail" in response.json()` l.145). Sin aserción de `WWW-Authenticate`.
- **Las otras 13 rutas admin:** 0 tests de turista, 0 tests anónimos. Todas las peticiones a ellas usan un admin o un
  superadmin: `tests/test_services.py` (fixture `admin_headers`, l.35-37; `grep "UserRole\.tourist|status_code == 40[13]"`
  → 0 líneas), `tests/test_auth.py:309,326,343,367,398,430`, `tests/test_user_response.py:97,118`.
- **Los 403 de `/usuarios/admin` y `/usuarios/{cedula}/recuperar` que sí existen son de la política, no del guard:**
  actor admin en `tests/test_auth.py:357-376` (recuperar un superadmin, `assert_can_recover`) y `tests/test_auth.py:379-407`
  (provisión, `assert_can_provision_admin`, M8 de A2).
- **Rutas de usuario, sin token — 0 tests.** Los 401 de `GET /usuarios/mi-perfil` (`PROTECTED_ROUTE`,
  `tests/test_token_failure_paths.py:32`) llevan siempre un `Authorization` (token caducado, corrupto, sin `sub`, de otra
  clave…; l.102-247): prueban `get_current_user`, no la ausencia de token. `DELETE`/`PATCH /usuarios/{cedula}` solo
  tienen 403 de la política (jerarquía, BE-02; `tests/test_auth.py:230,251,294`, `tests/test_user_access_policy.py:348…845`).
- `tests/` no importa `get_current_admin_user`, `AdminDep` ni `oauth2_scheme` (0 coincidencias); `alembic/` tampoco.
- La cobertura no lo revela: `app/api/dependencies.py` está entre los "26 files skipped due to complete coverage".

### Mutantes re-ejecutados hoy (copia `git archive HEAD` en el scratchpad; `app/` del repo intacto)

Suite sin `tests/test_check.py` ni `tests/test_check_docs.py` (no importan `app`). Línea base de la copia:
**290 passed** (el backlog decía 259: la suite creció con BE-32 y A4).

| Mutante | Edición (copiable) | Resultado |
|---|---|---|
| M1 | `service.py:24` → `admin_router = APIRouter()` | **290 passed** |
| M2 | `service.py`: las 7 `Depends(get_current_admin_user)` → `Depends(get_current_user)` | **290 passed** |
| M3 | M1 + los 6 handlers de `service.py` a `get_current_user` | **290 passed** |
| M4 | `audit.py:8` → `router = APIRouter()` | **290 passed** |
| M5 | borrar `audit_service.py:65` (`assert_is_admin_plus`) | 1 failed: `TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called` (unitario) |
| M4+M5 | ambos | 2 failed: el anterior y `test_audit_trail_forbidden_for_tourist` |
| M6 | `user.py:21,37`: `Depends(get_current_admin_user)` → `Depends(get_current_user)` | **290 passed** |
| M7 | `dependencies.py:156` → `if False:` | **290 passed** |

Bajo M7, sonda HTTP con token de turista: **200** en `GET /usuarios/`, `GET /usuarios/admin/eliminados`,
`GET /servicios/admin/inactivos`, `GET /servicios/admin/eliminados` (cuerpo lista); 404 en `PATCH /usuarios/{c}/recuperar`,
`activar`, `desactivar`, `DELETE /servicios/{id}`; 422 en `POST /usuarios/admin`, `POST /servicios/`,
`POST /servicios/upload-images/`, `PUT /servicios/{id}` (cuerpo vacío); 400 en `PATCH /servicios/{id}/recuperar`; **403
solo en `/auditoria/`** (por el re-chequeo). Anónimo: 401 en las 17, con o sin M7. Coincide con lo medido en A2.

## Ficheros afectados (mapa completo)

- `app/api/dependencies.py` — el guard (l.143-160, predicado l.156) y el 401 (l.19, 112-130); objeto de los mutantes, no
  del cambio.
- `app/api/routers/user.py` — 4 rutas admin (l.180, 199, 218, 240) y 3 de usuario (l.116, 129, 149); guards l.20-21, 36-37.
- `app/api/routers/service.py` — 9 rutas admin (l.50-249), guard l.24.
- `app/api/routers/audit.py` — 1 ruta admin (l.11), guard l.8.
- `app/services/audit_service.py:65` — re-chequeo que tapa M4 y M7 en `/auditoria/` (lo quita BE-40, no BE-39).
- `app/services/user_access_policy.py:109` — `assert_can_provision_admin`: rechaza a todo no-superadmin con cuerpo válido;
  tapa M7 en `POST /usuarios/admin` si el test manda cuerpo válido.
- `tests/test_audit.py` — los únicos dos tests de rechazo de guard (l.50, l.140); estructura y cabecera incompletas.
- `tests/test_services.py` — 0 rechazos por rol o sesión en 9 rutas admin.
- `tests/test_auth.py`, `tests/test_user_response.py` — peticiones a rutas admin solo con admin/superadmin.
- `tests/test_token_failure_paths.py` — 401 de token inválido en `mi-perfil`; ningún "sin token".
- `tests/conftest.py` — fábricas disponibles: `persist_user` (l.249), `make_auth_headers` (l.233), `make_token` (l.207),
  `client` (l.70).

## Rincones no mencionados por la fuente

1. **Dos rutas donde un test de turista bien intencionado no mata a M7, por enmascaramiento:**
   - `GET /auditoria/`: guard (403 `HTTPException`) y re-chequeo (403 `AuthorizationError` vía handler global) responden
     igual en código, cuerpo (`{"detail": str}`) y cabeceras (sin `www-authenticate`, congelado en
     `tests/test_domain_error_handler.py:62-67`). Sin afirmar sobre texto, **M4 es equivalente por HTTP mientras exista
     `audit_service.py:65`**; solo cae junto con M5 o tras BE-40. El ítem lo sabe (addendum de ADR-0012), pero el
     criterio "en RED frente a M1–M7" no puede cumplirse para M4 en BE-39 y hay que declararlo.
   - `POST /usuarios/admin`: bajo M7, un turista con cuerpo **válido** recibe 403 de `assert_can_provision_admin`
     (`user_access_policy.py:109`); solo con cuerpo vacío/inválido recibe 422. Un test de 403 con cuerpo válido sobrevive
     a M7; con `{}` lo mata (pero ese 403-antes-de-422 cambia de origen cuando BE-40 ponga el guard de superadmin).
2. **En las 3 rutas de usuario el guard de router es redundante con `UserDep`** (`user.py:36` frente a l.117, 131, 153):
   quitar `dependencies=[...]` de `self_service_router` es un mutante equivalente. M1–M7 no tocan estas rutas; el plan
   tiene que definir su propio mutante (p. ej., `oauth2_scheme` con `auto_error=False` + `get_current_user` que devuelva
   un usuario fijo sin token) o declarar que el test de 401 sin token vigila `oauth2_scheme`/`get_current_user`, no el
   router.
3. **Doble capa en `/servicios` y `/usuarios` admin:** M1 sola dejaría intactos los 6 handlers de `service.py` con
   `Depends(get_current_admin_user)` (y los 4 de `user.py` con `AdminDep`); solo las rutas sin identidad en el handler
   (`service.py:50,110,126`) quedarían abiertas. Un test por ruta mata M1 en esas tres y M7 en todas.
4. Las cifras del backlog están desplazadas: `259 passed` → hoy 290 en la copia (579 en la compuerta completa);
   `tests/test_audit.py:49` → el test empieza en l.50 (aserción l.58).

## Patrones de detección (copiables)

```bash
# Rechazos por rol o sesión en /servicios (0 líneas hoy; debe ser > 0 al cerrar)
grep -rnE "UserRole\.tourist|status_code == 40[13]" tests/test_services.py
# Todas las aserciones 401/403 de la suite (30 líneas hoy; solo tests/test_audit.py:58,144 son de un guard de rol/sesión de ruta admin)
grep -rnE "status_code == 40[13]" tests --include=*.py
# Peticiones sin cabeceras a rutas protegidas (1 línea hoy: tests/test_audit.py:142)
grep -rnE "client\.(get|post|put|patch|delete)\(\"/(auditoria|usuarios|servicios)/[^\"]*\"\)" tests --include=*.py
# Guards e identidad (15 líneas hoy en app/)
grep -rn "get_current_admin_user" app --include=*.py
# Re-chequeo que enmascara M4/M7 en /auditoria (1 línea hoy; lo quita BE-40)
grep -rn "assert_is_admin_plus(current_user)" app --include=*.py
```

Mutantes: la tabla de la sección "Mutantes re-ejecutados hoy" da la edición exacta de cada uno (cadena original →
sustituta) para repetirlos sobre una copia `git archive HEAD`, con
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`
desde la raíz de la copia (se comprobó que `app` se importa de la copia, no del repo).

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)

- Base develop: `3ca990a` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop`)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (salida redirigida a un fichero del scratchpad; exit 0)
- La compuerta **pasa** antes de tocar nada.

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura
Compuerta superada.
```

- **ruff format:** 60 files already formatted.
- **ruff check:** All checks passed! (0 errores).
- **mypy:** Success: no issues found in 55 source files (0 errores).
- **import-linter:** Contracts: 4 kept, 0 broken.
  - Capas: api -> services -> repositories -> models KEPT
  - Los servicios no conocen el transporte HTTP KEPT
  - Los repositorios solo conocen SQLAlchemy y los modelos KEPT
  - Los modelos y los schemas no dependen de capas superiores KEPT
- **docs:** Documentación coherente (R1–R5).
- **pytest:** 579 passed, 0 failed, 5 warnings in 21.22s.
- **cobertura:** Total coverage: 96.29% (piso exigido 92.0%).

## Conclusión para el planificador

- **Debe resolver:** un test HTTP de rechazo por cada una de las 17 rutas de la tabla: anónimo → 401 con
  `www-authenticate: Bearer` y `set(body) == {"detail"}`; en las 14 admin, turista → 403 con `{"detail"}` y sin
  `www-authenticate`. Sin afirmar texto. Tests en RED primero frente a M1, M2, M3, M6, M7 (re-ejecutados con la tabla de
  arriba); conviene parametrizar por ruta (método, path, cuerpo) para no duplicar 17 tests casi iguales. Dominios: los
  tests se reparten entre `tests/test_services.py`, `tests/test_auth.py`/`tests/test_audit.py` o un archivo nuevo por
  router; respetar ≤ 5 archivos por fase.
- **Declarar en el plan, no "arreglar":** M4 no puede caer por HTTP mientras exista `audit_service.py:65` (cae con M4+M5;
  se cierra en BE-40); en `POST /usuarios/admin` el test de turista debe ir con cuerpo vacío/inválido o la política tapa
  a M7; en las 3 rutas de usuario el guard de router es redundante con `UserDep` y M1–M7 no las tocan: elegir y escribir
  el mutante que el 401 sin token debe matar.
- **No debe tocar:** `app/` (BE-39 es solo tests; el re-chequeo de auditoría, el guard de superadmin, `AdminDep`/`UserDep`
  y los comentarios son BE-40); el `scope` del token (BE-42); las reglas de dato de la política (`B-GHOST-ADMIN`); el
  campo `code` en errores (P2).
- **Riesgos:** los tests de turista con cuerpo vacío fijan hoy "403 antes de 422", que BE-40 conserva (guard de
  superadmin) pero con otro origen; los tests con IDs inexistentes (`/servicios/1`) dependen de que el guard corra antes
  del 404 del servicio (cierto hoy, medido). La compuerta está en verde: la cobertura no puede bajar del 96,29 %.

## Adenda — decisiones de David antes de planear (11 nov 2026, 10:48, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir. David aprobó las cinco a las 10:48 ("te doy el sí 5 a las 5").

1. **Veredicto aceptado: confirmada. Línea base aceptada:** `3ca990a`, compuerta en verde sin `--soft` (579 passed ·
   96,29 % · ruff 0 · mypy 0 · 4 kept). Desde hoy el CI no tolera nada (PR #89): el criterio de cada fase es la compuerta
   completa en verde, sin trinquete (ADR-0005 superado).
2. **M4 no se exige en BE-39.** En `GET /auditoria/` el guard (`audit.py:8`) y el re-chequeo (`audit_service.py:65`)
   responden el mismo 403, con el mismo cuerpo y sin `www-authenticate`; sin afirmar sobre texto (AGENTS §5) ningún test
   HTTP los distingue. **Criterio de aceptación de BE-39: tests en RED frente a M1, M2, M3, M6, M7 y M4+M5**, con las
   ediciones exactas de la tabla "Mutantes re-ejecutados hoy". M4 sola pasa a la Verificación final de BE-40 (que quita el
   re-chequeo); el plan lo declara en Residuales y la sesión Mentor anota la fila BE-40 en el cierre.
3. **`POST /usuarios/admin`: el test de turista envía cuerpo `{}`.** Con cuerpo válido, `assert_can_provision_admin`
   (`user_access_policy.py:109`) da 403 aunque el guard no compruebe el rol, y el test sobrevive a M7; con `{}`, bajo M7
   la respuesta es 422 y el test cae. El caso sigue valiendo tras BE-40 (el guard de superadmin también corre antes de
   validar el cuerpo).
4. **Mutante de los 401 sin token: M9, compuesto, en `app/api/dependencies.py`.** M1–M7 no tocan las tres rutas de
   usuario, y en casi todas las rutas la identidad se pide dos veces (router y handler), así que quitar el guard del
   router no deja pasar a un anónimo. M9 = `oauth2_scheme` con `auto_error=False` (l.19) **más** `get_current_user`
   devolviendo un usuario fijo cuando no llega token. Los diecisiete tests de 401 deben caer bajo M9. **Dato leído, no
   ejecutado, que el planificador mide con sonda antes de dictar M9:** `auto_error=False` solo sería un mutante
   equivalente, porque `jwt.decode(None, …)` lanza `DecodeError` (`venv/Lib/site-packages/jwt/api_jws.py:298-299`), que es
   `InvalidTokenError`, y `dependencies.py:131-132` la convierte en el mismo 401 con `WWW-Authenticate`. Si la sonda
   muestra otra cosa, el plan lo dice y propone el mutante mínimo que deje pasar a un anónimo.
5. **Un solo archivo nuevo, `tests/test_route_guards.py`, con una tabla de las 17 rutas** (método, ruta, cuerpo, tipo de
   guard: admin o usuario) y tests parametrizados sobre ella: anónimo → 401, `www-authenticate: Bearer`,
   `set(body) == {"detail"}` (las 17); turista → 403, `set(body) == {"detail"}`, sin `www-authenticate` (las 14 admin).
   Sin texto. Usuarios y cabeceras con las fábricas de `tests/conftest.py` (`persist_user`, `make_auth_headers`). **Los
   dos tests de `tests/test_audit.py` (l.50 `test_audit_trail_forbidden_for_tourist`, l.140
   `test_audit_trail_requires_authentication`) se borran en la misma fase que los sustituye**: la tabla cubre
   `/auditoria/` con aserciones más estrictas; el plan declara el cambio de conteo y comprueba que M4+M5 sigue cayendo
   con los tests nuevos.
6. **Test de inventario.** Un test recorre `app.routes` y falla si una ruta (método + path) no está ni en la tabla de
   protegidas ni en una lista explícita de públicas (las 5 de la aplicación y las de documentación de FastAPI). Es el
   patrón de `_DOMAIN_ERROR_STATUS` (ADR-0003) y de `tests/test_models_registry.py` (ADR-0010): convierte el punto 4 de
   ADR-0012 en algo con exit code, antes de que `B-RESERVAS` añada rutas. Con mutante propio: una ruta nueva sin
   entrada → el test cae; una entrada de la tabla que ya no existe en `app.routes` → el test cae.
7. **Alcance.** BE-39 no toca `app/` (los mutantes se aplican sobre copia desechable y se restauran). Fuera: el
   re-chequeo de auditoría, el guard de superadmin, `AdminDep`/`UserDep` y los comentarios (BE-40); el `scope` del token
   (BE-42); las reglas de dato (`B-GHOST-ADMIN`). Rol inferior = turista (`UserRole.tourist`).

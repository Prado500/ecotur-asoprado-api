# Verificación — BE-40: aplicar la frontera de autorización de ADR-0012 (re-chequeo de auditoría, guard de superadmin, identidad única)

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-40, sección B, línea 86; origen: verificación de A2, 6 nov) + ADR-0012 (Decisión 1, 3 y 5; Consecuencias) + notas R1/R2 de `docs/deuda/BE-39/plan.md:714-720`
**Fecha:** 2026-11-12

## Qué describe el ítem
Dos rutas no cumplen la frontera de ADR-0012 ("el rol se decide en el guard, el dato en la política, ninguna regla dos
veces"): `GET /auditoria/` comprueba el rol en el guard del router y otra vez en `AuditService` vía `assert_is_admin_plus`;
`POST /usuarios/admin` aplica una regla de solo rol (superadmin) dentro de la política, sin guard de superadmin. Además:
comentarios que se contradicen sobre la frontera, el predicado "es admin+" escrito dos veces y tres formas distintas de
inyectar la identidad bajo guard admin. Las cinco partes persisten hoy; solo han derivado algunos números de línea.

## Evidencia en el código

**1. Re-chequeo de rol en auditoría (regla comprobada dos veces)**
- `app/api/routers/audit.py:8` — guard de router: `router = APIRouter(dependencies=[Depends(get_current_admin_user)])`
- `app/services/audit_service.py:65` — re-chequeo: `self.user_access_policy.assert_is_admin_plus(current_user)`
- `app/services/audit_service.py:6,12,14` — import y `__init__(self, audit_repo, user_access_policy)`: la política se
  inyecta solo para ese re-chequeo (`log_transaction`, :16-36, no la usa).
- `app/services/audit_service.py:46-50,62-63` — docstring: "enforcing Role-Based Access Control… Raises AuthorizationError".
- `app/api/dependencies.py:40-44` — `get_audit_service` inyecta `get_user_access_policy` y construye
  `AuditService(audit_repo, user_access_policy)` (el backlog dice `:44-48`; deriva por los cambios de A4).
- `app/services/user_access_policy.py:115-133` — `assert_is_admin_plus`, regla de solo rol; `:130`
  `if actor.role not in [UserRole.admin, UserRole.superadmin]:`. Único llamador en `app/`: `audit_service.py:65`.

**2. Regla de solo rol en la política para `POST /usuarios/admin`, sin guard de superadmin**
- `app/api/routers/user.py:240-261` — `crear_administrador` cuelga de `admin_router` (`:37`, guard admin) e inyecta `AdminDep`;
  no hay guard de superadmin en ningún sitio (grep `superadmin_user|get_current_superadmin|SuperadminDep`: 0 resultados).
- `app/services/user_access_policy.py:98-113` — `assert_can_provision_admin`; `:109` `if actor.role != UserRole.superadmin:`.
- `app/services/user_service.py:396` — `self.user_access_policy.assert_can_provision_admin(current_user)`.

**3. Comentarios contradictorios sobre la frontera**
- `app/api/routers/user.py:23-33` — "Services … never duplicate the transport-level authorization frontier".
- `app/api/routers/audit.py:28-31` — "Defense in depth: … the service layer re-asserts the same administrative rule"
  (contradice a `user.py:31-32` y a ADR-0012, Alternativa 1 rechazada).
- `app/api/routers/user.py:248-249` — "The admin-tier dependency gates transport access, while UserService enforces the
  stricter superadmin-only hierarchical rule".
- `app/services/user_service.py:378-382` — "The superadmin-only guard below is an intentional hierarchical business rule,
  not a duplicate of the transport frontier" (a ADR-0012 punto 1: es regla de solo rol, va en el guard).
- `app/services/audit_service.py:46-50` — "Authorization is delegated to the UserAccessPolicy administrative-tier rule".

**4. Predicado "es admin+" escrito dos veces**
- `app/api/dependencies.py:156` — guard: `if current_user.role not in [UserRole.admin, UserRole.superadmin]:` (el backlog
  y D1 dicen `:132`; deriva por A4).
- `app/services/user_access_policy.py:130` — mismo predicado en `assert_is_admin_plus`.
- `app/services/user_access_policy.py:93` — variante (`target.role in [UserRole.admin, UserRole.superadmin]`), pero es regla
  de dato (depende del objetivo) en `assert_can_recover`: legítima según ADR-0012 punto 2; no es duplicado.

**5. Tres formas de inyectar la identidad bajo guard admin**
- `app/api/routers/user.py:20-21` — alias `UserDep` / `AdminDep` (forma que fija ADR-0012 punto 5); usados en
  `user.py:117,131,153` (`UserDep`) y `:182,201,220,243` (`AdminDep`).
- `app/api/routers/service.py:89,146,170,191,212,234` — `usuario_actual: User = Depends(get_current_admin_user)` repetido
  en 6 handlers (no usa los alias; `service.py` no los importa).
- `app/api/routers/audit.py:24` — `usuario_actual: User = Depends(get_current_user)` bajo un router de guard admin (el
  handler pide la identidad de nivel "user" y solo la usa para el re-chequeo de :65 del servicio).

**Tests que fijan hoy el comportamiento a retirar**
- `tests/test_audit.py:55-99` — `TestAuditServiceAuthorization`: `:63-64` construye `AuditService(..., user_access_policy=
  UserAccessPolicy())`; `:66-75` turista → `AuthorizationError` desde el servicio; `:77-99` admin → repo llamado (el backlog
  cita `:66-111`; deriva). Import en `:6` (`AuthorizationError`) y `:11` (`UserAccessPolicy`).
- `tests/test_user_access_policy.py:260-278` — `TestAssertCanProvisionAdmin` (3 tests); `:281-312` `TestAssertIsAdminPlus`
  (5 tests).
- `tests/test_user_service.py:357-366` — `test_create_administrative_account_rejects_non_superadmin` (admin →
  `AuthorizationError` del servicio, repo no tocado).
- `tests/test_auth.py:379-408` — `test_admin_provisioning_admin_returns_403_without_row` (admin con cuerpo **válido** → 403,
  sin fila nueva). Con guard de superadmin sigue dando 403 (lo daría el guard); el test no cambia de verde.
- `tests/test_route_guards.py:30` — `guard: Literal["admin", "user"]`; `:24` docstring; `:34-35` comentario "A valid body to
  POST /usuarios/admin gets 403 from the provisioning policy and hides the guard"; `:42`
  `ProtectedRoute("POST", "/usuarios/admin", "admin", _EMPTY_BODY)`; `:58` `ADMIN_ROUTES` filtra `guard == "admin"`;
  `:52` `ProtectedRoute("GET", "/auditoria/", "admin")`; `:146-161` `test_admin_route_rejects_tourist`.

**M4 sola (nota R1 de BE-39).** Con `audit.py:8` → `APIRouter()` la suite sigue verde porque `audit_service.py:65` responde
el mismo 403 (evidencia de BE-39: `docs/deuda/BE-39/plan.md:714-717`, estado C bajo M4 = `320 passed`). Hoy no se
re-ejecutó: la copia desechable requería `rm -rf`, denegado por permisos. El re-chequeo que la enmascara sigue intacto
(`audit_service.py:65`), así que no hay motivo para que el resultado haya cambiado.

## Ficheros afectados (mapa completo)
- `app/services/audit_service.py` — re-chequeo `:65`, política en `__init__` (:6, :12, :14), docstring :46-50/:62-63.
- `app/api/dependencies.py` — `get_audit_service` inyecta la política (:40-44); guard admin con el predicado (:143-160);
  aquí iría el guard de superadmin (no existe).
- `app/services/user_access_policy.py` — `assert_can_provision_admin` (:98-113) y `assert_is_admin_plus` (:115-133), reglas
  de solo rol.
- `app/services/user_service.py` — llamada `:396` y docstring `:378-393` que justifica la regla en el servicio.
- `app/api/routers/user.py` — `crear_administrador` bajo guard admin (:240-261), comentario de frontera (:23-33), docstring
  :248-249.
- `app/api/routers/audit.py` — identidad con `get_current_user` (:24), docstring "defense in depth" (:28-31).
- `app/api/routers/service.py` — 6 inyecciones `Depends(get_current_admin_user)` en vez de `AdminDep` (:89, :146, :170,
  :191, :212, :234); import en :3 y :5.
- `tests/test_audit.py` — `TestAuditServiceAuthorization` (:55-99) fija el re-chequeo.
- `tests/test_user_access_policy.py` — `TestAssertCanProvisionAdmin` (:260-278), `TestAssertIsAdminPlus` (:281-312).
- `tests/test_user_service.py` — `test_create_administrative_account_rejects_non_superadmin` (:357-366).
- `tests/test_route_guards.py` — `Literal` (:30), comentario (:34-35), fila de provisión (:42), filtro `ADMIN_ROUTES` (:58).
- `tests/test_auth.py` — `:379-408` (sigue válido; cambia la capa que da el 403).

## Rincones no mencionados por la fuente
- `app/services/user_service.py:378-382` — docstring que defiende explícitamente la regla de solo rol en el servicio
  ("not a duplicate of the transport frontier"); es el cuarto comentario contradictorio, no citado en la fila.
- `app/api/routers/user.py:248-249` — docstring de `crear_administrador` con la misma tesis; tampoco citado.
- `tests/test_user_service.py:357-366` y `tests/test_user_access_policy.py:260-312` — 9 tests unitarios que fijan las dos
  reglas a retirar; la fila solo cita `tests/test_audit.py`.
- `tests/test_route_guards.py:58` — `ADMIN_ROUTES` se construye con `guard == "admin"`: si la fila de provisión pasa a
  `"superadmin"` (nota R2), sale de `ADMIN_ROUTES` y pierde el caso "turista → 403" salvo que el filtro la incluya.
- `app/api/routers/audit.py:24` — tras quitar el re-chequeo, el handler ya no necesita la identidad (como
  `service.py:111,127`, que no la inyectan); la tercera "forma" puede desaparecer en vez de convertirse a `AdminDep`.
- Derivas de línea respecto de la fila: `dependencies.py:44-48` → `:40-44`; `dependencies.py:132` → `:156` (también en la
  fila D1, `docs/backlog.md:114`); `tests/test_audit.py:66-111` → `:55-99`.
- `alembic/`: ninguna ocurrencia (el ítem no toca esquema).

## Patrones de detección (copiables)
```bash
# Reglas de solo rol en la política y sus llamadores (objetivo: 0 en app/ y tests/)
grep -rn "assert_is_admin_plus\|assert_can_provision_admin" app tests

# Política inyectada en el servicio de auditoría (objetivo: 0)
grep -n "user_access_policy\|UserAccessPolicy" app/services/audit_service.py
grep -n -A5 "def get_audit_service" app/api/dependencies.py

# Predicados de rol en app/ (objetivo: "es admin+" solo en dependencies.py; superadmin solo en su guard y en :66 de la política)
grep -rnE "role (not )?in \[|role ?[!=]= ?UserRole" app

# Formas de inyectar identidad en routers (objetivo: solo APIRouter(dependencies=…) y los alias UserDep/AdminDep)
grep -rnE "Depends\(get_current_(admin_)?user\)" app/api/routers

# Guard de superadmin (objetivo: >= 1 en dependencies.py y su uso en POST /usuarios/admin)
grep -rniE "superadmin_user|SuperadminDep" app tests

# Comentarios de frontera contradictorios (objetivo: 0)
grep -rniE "defen[cs]e in depth|re-asserts|not a duplicate of the transport|gates transport access" app

# Fila de provisión en el inventario de guards
grep -n '"/usuarios/admin"' tests/test_route_guards.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `41ff01d` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` == `git rev-parse
  origin/develop` == `41ff01d35a33e3bc412a07fec4452011f3278f31`; `item/be-40` sin commits propios).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (salida 0).

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
- pytest: `622 passed, 8 warnings in 22.81s` (0 failed).
- Cobertura total: `96.47%` (`Required test coverage of 92.0% reached. Total coverage: 96.47%`).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas api -> services -> repositories -> models KEPT; Los servicios no
  conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los modelos y los schemas
  no dependen de capas superiores KEPT).
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
- Resolver las cinco partes de ADR-0012 en `app/`: retirar `assert_is_admin_plus` y la política de `AuditService`/
  `get_audit_service`; crear un guard de superadmin en `dependencies.py`, aplicarlo a `POST /usuarios/admin` y retirar
  `assert_can_provision_admin` (política + `user_service.py:396`); `AdminDep`/`UserDep` como única forma en
  `service.py` (6 handlers) y `audit.py:24` (o quitar la identidad si el handler ya no la usa); reescribir los 5 comentarios.
- Tests RED primero: en `test_route_guards.py`, la fila de provisión pasa a `guard="superadmin"` (ampliar el `Literal`, ajustar
  el filtro de `:58` para no perder el caso turista y el comentario de `:34-35`) y un caso "admin → 403" con cuerpo `{}`, que
  hoy falla (da 422). La Verificación final ejecuta M4 sola (`audit.py:8` → `APIRouter()`): debe caer
  `test_admin_route_rejects_tourist[GET /auditoria/]`.
- Borrar o reescribir los tests que fijan las reglas retiradas (`test_audit.py:55-99`, `test_user_access_policy.py:260-312`,
  `test_user_service.py:357-366`) sin bajar la cobertura (96.47%) ni la regla de AGENTS §5 (2 de fallo y 2 de borde).
- NO tocar: reglas de dato de la política (`assert_can_delete`, `assert_can_update` incl. `:66`, `assert_can_recover` incl.
  `:93`, `can_see`), `B-GHOST-ADMIN` (BE-34..BE-38), el `scope` del token (BE-42; también toca `dependencies.py`, conviene
  secuenciar), D6/S3.
- Riesgo: cambio de contrato declarado (admin con cuerpo inválido en `POST /usuarios/admin`: 422 → 403); confirmarlo con el
  cliente Flutter antes de fusionar. Repartir en fases de ≤ 5 archivos: hay 7 de `app/` y 5 de `tests/` implicados.

## Adenda — decisiones de David antes de planear (12 nov 2026, 10:30, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base aceptada:** `41ff01d`,
compuerta completa en verde (622 passed · 96,47 % · ruff 0 · mypy 0 en 56 archivos · 4 kept); el criterio de cada fase es
la compuerta completa en verde (ADR-0005 superado). Contraste de la sesión Mentor contra el código, sin correcciones de
hecho: `audit.py:8,24,37`, `audit_service.py:40,65`, `dependencies.py:40-44,156`, `user_access_policy.py:109,130`,
`user_service.py:396`, `user.py:20-21,36-37,240-243`, los seis `Depends(get_current_admin_user)` de `service.py` y
`tests/test_route_guards.py:30,42,58`. David aprobó los cinco puntos a las 10:30 ("sí, de acuerdo con los 5 puntos").

1. **Un guard de superadmin reemplaza al guard admin en `POST /usuarios/admin`; no se suma a él** (David, 10:21: "ese debe
   reemplazar al guard admin en esta ruta de post… va de la mano con el punto 3 del ADR-0012"). Consecuencia medida:
   `crear_administrador` cuelga hoy de `admin_router` (`user.py:240`), cuyo guard se aplica a todas sus rutas
   (`user.py:37`); para que el rol se compruebe una sola vez la ruta sale de ese router. Forma coherente con lo que ya
   existe: `get_current_superadmin_user` en `app/api/dependencies.py`, construido sobre `get_current_user` (no sobre el
   guard admin); un `superadmin_router` con ese guard y un alias `SuperadminDep` junto a `UserDep`/`AdminDep`
   (`user.py:20-21`); el router nuevo se incluye en `user.py:264-267` (si falta, el test de inventario cae: compara por
   igualdad, `tests/test_route_guards.py:127-131`). Método y ruta no cambian (contrato con el cliente).
   `assert_can_provision_admin` (`user_access_policy.py:98-113`) y su llamada (`user_service.py:396`) se retiran. Cambio de
   contrato declarado en ADR-0012: un admin con cuerpo inválido pasa de 422 a 403; con cuerpo válido sigue en 403
   (`tests/test_auth.py:379-408`), ahora desde el guard. El planificador dicta y mide el mutante del guard nuevo
   (guard de superadmin sustituido por el de admin → debe caer el caso "admin → 403").
2. **`retrieve_audit_history` deja de recibir `current_user`** (`audit_service.py:40`, `audit.py:24,37`): al retirar el
   re-chequeo de `audit_service.py:65` es un parámetro que nadie lee. Con él salen la política de `AuditService.__init__`
   y de `get_audit_service` (`dependencies.py:40-44`) y `assert_is_admin_plus` (`user_access_policy.py:115-133`, único
   llamador: la l.65). **`log_transaction` y `performed_by` (`audit_service.py:16-36`) no se tocan:** el registro de quién
   hizo qué queda igual; lo que sale es la identidad de quien *consulta* el historial, que solo servía para repetir la
   comprobación de rol. La tercera "forma" de inyectar identidad (`audit.py:24`) desaparece en vez de pasar a `AdminDep`.
3. **M4 sola no se re-ejecutó hoy y se acepta como evidencia estructural:** `git diff a0578ae HEAD -- app tests alembic
   conftest.py` es vacío (medido por la sesión Mentor a las 09:14), así que vale la medición del auditor de BE-39 sobre el
   estado final (`docs/deuda/BE-39/gaps.md`, fase E: M4 sola sin rojo). La Verificación final de BE-40 sí la ejecuta
   (`audit.py:8` → `APIRouter()`): debe caer `tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]`.
   Si el auditor tampoco puede crear o borrar la copia desechable (`rm -rf` denegado al verificador), lo reporta como
   bloqueo; no da el mutante por medido.
4. **`AGENTS.md:48` enumera los guards como `"admin"` o `"user"`:** al ampliar el `Literal` con `"superadmin"` la viñeta
   queda desactualizada. La corrige David en un commit de documentos antes de `/pr` (los agentes no editan AGENTS).
5. **La fila de provisión no pierde su caso "turista → 403".** `ADMIN_ROUTES` filtra `guard == "admin"`
   (`tests/test_route_guards.py:58`): al pasar la fila a `guard="superadmin"` el planificador decide cómo conserva el caso
   de turista con cuerpo `{}` (adenda de BE-39, punto 3) y añade el caso "admin → 403" con cuerpo `{}`, que hoy da 422
   (RED). El docstring de `:24` y el comentario de `:34-35` se actualizan.

**Fuera de BE-40, anotado para que no se haga de paso:** hoy un admin ve el mismo historial que un superadmin (la consulta
de `audit_service.py:67-69` no filtra por quién pregunta), mientras `user_access_policy.py:147` le oculta los superadmins
en el listado de usuarios. Si David quiere una regla ahí, depende del dato, va en la política (ADR-0012, punto 2) y recibe
fila propia; pregunta abierta en la bitácora `2026-11-12`. **Pendiente antes del merge, sin respuesta aún:** confirmar en
el cliente Flutter el cambio 422 → 403 (ADR-0012, Consecuencias).

# PLAN — BE-40: Aplicar la frontera de ADR-0012 en auditoría, provisión de administradores e inyección de identidad

> Fuente: `docs/deuda/BE-40/verificacion.md` (confirmada; adenda de cinco decisiones de David, 12 nov, 10:30).
> Base: `3798db4` (`41ff01d` más cuatro commits de documentación; `app/`, `tests/`, `alembic/` y `conftest.py` sin cambios,
> `git diff --name-only 41ff01d HEAD -- app tests alembic conftest.py` vacío). Estado: **aprobado por David el 12 nov 2026
> con E0 (11:22): cuatro fases, A → D; P1–P5 resueltas y dos correcciones de dictado en "Enmiendas aprobadas", al final.**
> **E1 (12:38) añade la fase E** (opcional de la auditoría de D); A–D ejecutadas y auditadas PASS. **Fase E aprobada con E2 (12:57).**
> Las cifras de este plan (tests, cobertura, mutantes y conteos de grep) se midieron el 12 nov sobre copias desechables
> con el texto exacto que dicta.

## Resumen para aprobación

En cuatro fases se aplica ADR-0012 donde la verificación midió que no se cumple: el rol lo decide el guard y nada lo
repite. (A) `UserDep` y `AdminDep` pasan a `app/api/dependencies.py`, y los seis handlers de `service.py` que escribían
`Depends(get_current_admin_user)` a mano usan `AdminDep`. No cambia el comportamiento. (B) `GET /auditoria/` deja de
comprobar el rol dos veces: `AuditService` pierde la política y `retrieve_audit_history` pierde `current_user`. El mutante
M4 (quitar el guard del router) pasa a tumbar 2 tests; hoy no tumba ninguno. (C) Un guard nuevo,
`get_current_superadmin_user`, **sustituye** al guard admin en `POST /usuarios/admin` mediante un `superadmin_router`.
(D) Se retiran `assert_can_provision_admin` y `assert_is_admin_plus` de la política y los 9 tests que las fijaban (8 de
la política y 1 del servicio). La suite pasa de 622 a 618 tests y la cobertura de 96,47 % a 96,81 %, porque un test HTTP
nuevo de los filtros de auditoría (fase B) compensa el código cubierto que se borra.
**Riesgo principal:** el contrato cambia en la fase C. Un admin que envía un cuerpo inválido a `POST /usuarios/admin` recibe
403 donde hoy recibe 422, porque el guard responde antes de que se valide el cuerpo. Hay que confirmarlo con el cliente
Flutter antes de fusionar (ADR-0012, Consecuencias).
**No se toca:** las reglas de dato de la política (`assert_can_delete`, `assert_can_update` con su l.66, `assert_can_recover`
con su l.93, `can_see`), `B-GHOST-ADMIN`, el `scope` del token (BE-42), D6/S3 (las demás `= Depends(` siguen igual),
`log_transaction`/`performed_by`, `tests/test_auth.py`, `alembic/`. **No hace falta ADR nuevo:** ADR-0012 ya decide el
guard de superadmin (punto 1), la regla de no comprobar dos veces (punto 3), la forma única de inyectar la identidad
(punto 5) y el cambio 422 → 403 (Consecuencias).

## Objetivo y decisiones bloqueadas

Objetivo: cada regla de solo rol se decide en un único guard HTTP, y quitar o debilitar ese guard pone la suite en rojo.
Esto incluye `GET /auditoria/` y `POST /usuarios/admin`.

1. **El guard de superadmin sustituye al guard admin en `POST /usuarios/admin`; no se suma a él** (adenda, punto 1).
   `get_current_superadmin_user` se apoya en `get_current_user`. La ruta pasa a un `superadmin_router` con ese guard y se
   incluye en `router`. El método, la ruta y el cuerpo no cambian.
2. **Los alias viven en `app/api/dependencies.py`**: `UserDep`, `AdminDep` y `SuperadminDep`, juntos y debajo de los
   guards que nombran. Es la única forma de que `service.py` los use sin importar otro router. Es "cómo" se cumple
   ADR-0012 punto 5, no "qué" (ver Decisiones abiertas, P1).
3. **`retrieve_audit_history` no recibe `current_user`** (adenda, punto 2). El handler de auditoría deja de inyectar la
   identidad; no pasa a `AdminDep`.
4. **La fila de provisión conserva su caso "turista → 403"** (adenda, punto 5). `ADMIN_ROUTES` pasa a filtrar
   `guard in ("admin", "superadmin")`. Un `SUPERADMIN_ROUTES` nuevo alimenta el caso "admin con `{}` → 403".
5. **Mutantes en la verificación final**: M4 (adenda, punto 3) y MS1–MS3 (el guard de superadmin). Se aplican siempre en
   copias desechables.
6. **Compuerta** `./venv/Scripts/python.exe scripts/check.py` completa y en verde en cada fase. La cobertura nunca queda
   por debajo de 96,47 %.

## Análisis del redactor

**Qué cambia y por qué.** Hay cinco desviaciones de ADR-0012, y todas tienen la misma causa: comprobar el rol fuera del
guard o escribir la identidad de varias formas. Las dos comprobaciones duplicadas, auditoría y provisión, se tapan
mutuamente con su guard. M4 sobrevive hoy porque el re-chequeo de `audit_service.py:65` da el mismo 403. Con el guard de
superadmin pasaría lo mismo si `assert_can_provision_admin` se quedara: medido, MS1 tumba 1 test en el estado C y 2 en
el D. Por eso la fase D existe, aunque no cambie ninguna respuesta HTTP.

**Orden y dependencias.** A → B → C → D.
- A va primera porque C necesita que los alias ya estén en `dependencies.py` para añadir `SuperadminDep` a su lado.
- B es independiente de A y C. Va antes que D porque D borra `assert_is_admin_plus`, y su único llamador lo retira B.
- D depende de B (llamador de `assert_is_admin_plus`) y de C. Sin el guard de superadmin, quitar
  `assert_can_provision_admin` dejaría a un admin provisionar cuentas, y `tests/test_auth.py:379-408` caería.
- `dependencies.py` se toca en A, B y C, siempre en bloques distintos.

**Tests que congelan comportamiento.**
- `tests/test_route_guards.py` (17 sin token → 401, 14 turista → 403): es la red de A, B y C.
- `tests/test_services.py`: si un handler perdiera el alias, FastAPI leería `usuario_actual` como cuerpo y las seis
  mutaciones de paquetes darían 422.
- `tests/test_auth.py:379-408` (admin con cuerpo válido → 403, sin fila) y `:411-…` (superadmin → 201): siguen verdes en
  todas las fases sin tocarlos. Cambia la capa que da el 403.
- `tests/test_audit.py:14,107` (superadmin y admin leen el historial): sin cambios.

**Tests que se retiran y qué los sustituye** (regla de AGENTS §5: 2 de fallo y 2 de borde):
- Los 2 de `TestAuditServiceAuthorization` los sustituyen 4 unitarios de delegación (feliz, dos bordes, fallo de BD) y un
  test HTTP de los dos filtros.
- Los 8 de la política no tienen sustituto en la política. Su regla pasa al guard, y allí la vigilan los casos turista,
  admin y sin token de `test_route_guards.py` y el 403 de `test_auth.py:379`.
- El de `test_user_service.py:357` lo sustituye un fallo de BD en la búsqueda de duplicados. Así la provisión sigue
  teniendo dos caminos de fallo en el servicio.

**Cobertura.** Borrar código cubierto baja el porcentaje: sin compensación, el estado final quedaría en 96,44 % (medido), por
debajo de la base. Lo compensa la fase B con el test HTTP de filtros, que cubre `audit_repository.py:35,37`, hoy sin cubrir (2 sentencias y 2
ramas). Medido por fase: A 96,47 % · B 96,82 % · C 96,84 % · D 96,81 %.

**Riesgos.**
1. El contrato 422 → 403 (fase C), declarado en ADR-0012. Pendiente de confirmar con Flutter antes del merge (adenda).
2. En A, cuatro handlers de `service.py` tienen `usuario_actual` después de `service_service = Depends(...)`. Con
   `AdminDep`, que no lleva valor por defecto, ese orden es un `SyntaxError`. Por eso la fase A dicta el orden nuevo.
3. Orden de rutas: `POST /usuarios/admin` coincide en ruta con `PATCH`/`DELETE /{cedula}`, pero solo de forma parcial,
   porque el método no coincide. Starlette sigue buscando hasta el `POST` del `superadmin_router`, aunque esté incluido
   el último (medido: 626 passed en C).
4. BE-42 también toca `dependencies.py` (`get_current_user`). Secuencia: BE-40 se fusiona antes de que empiece BE-42. El
   guard nuevo se apoya en `get_current_user`, así que heredará gratis la comprobación de `scope`.

**Qué NO se toca.** Reglas de dato (`user_access_policy.py:20-96,135-147`), `get_user_access_policy` (lo sigue usando
`get_user_service`), `log_transaction`, `B-GHOST-ADMIN`, BE-42, D6/S3 (los `= Depends(get_*_service)` no son identidad),
`AGENTS.md` (lo actualiza David), el filtro por rol del historial de auditoría (pregunta abierta, ver Residuales).

## Regla de alcance

- **Sí:** los 7 archivos de `app/` y 4 de los 5 de `tests/` del mapa de la verificación, con el texto exacto de cada fase.
- **No:** `tests/test_auth.py` (sigue válido sin cambios), `alembic/`, ningún `conftest.py`, `app/main.py`, schemas,
  repositorios y modelos. Tampoco docstrings ni comentarios fuera de los que dicta cada fase, ni los nombres de handler en
  español (P2).
- Un hallazgo nuevo va a Residuales, nunca "de paso".

## Fases

**Procedimiento de mutantes (común; el de BE-39 sin borrar nada).** (1) Crear un directorio nuevo y vacío en el
scratchpad. No se reutiliza ni se borra (`rm -rf` está denegado). (2) Ejecutar
`git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>`. (3) Copiar encima, desde el árbol de trabajo, los
archivos que la fase modifica. (4) Aplicar la edición del mutante. (5) Desde `<dir>`, ejecutar
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
En el handoff se pegan la última línea y los `FAILED`.

| Mutante | Archivo | Edición exacta (original → sustituto) |
|---|---|---|
| M4 | `app/api/routers/audit.py` | `router = APIRouter(dependencies=[Depends(get_current_admin_user)])` → `router = APIRouter()` |
| MS1 | `app/api/dependencies.py` | en `get_current_superadmin_user`: `if current_user.role != UserRole.superadmin:` → `if current_user.role not in [UserRole.admin, UserRole.superadmin]:` |
| MS2 | `app/api/routers/user.py` | `Depends(get_current_superadmin_user)])` → `Depends(get_current_admin_user)])` en `superadmin_router`, y `usuario_actual: SuperadminDep,` → `usuario_actual: AdminDep,` |
| MS3 | `app/api/dependencies.py` | en `get_current_superadmin_user`: `if current_user.role != UserRole.superadmin:` → `if False:` |
| ML1 | `app/services/user_service.py` | l.75, en `register_tourist`: `cedula=user_data.cedula` → `cedula=user_data.email`. La l.395 tiene la misma cadena: se edita por número de línea, `sed -i '75s/cedula=user_data.cedula/cedula=user_data.email/'` (fase E) |
| ML2 | `app/services/user_service.py` | l.395, en `create_administrative_account`: la misma edición, `sed -i '395s/cedula=user_data.cedula/cedula=user_data.email/'` (fase E) |

Compuerta esperada al cerrar cada fase: exit 0, `Compuerta superada.`, `61 files already formatted`,
`All checks passed!`, `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.` y `8 warnings`.

| Fin de | pytest | Cobertura | Suite de la copia (sin `test_check*`) |
|---|---|---|---|
| Base | 622 passed | 96,47 % | 333 passed |
| A | 622 passed | 96,47 % | 333 passed |
| B | 625 passed | 96,82 % | 336 passed |
| C | 626 passed | 96,84 % | 337 passed |
| D | 618 passed | 96,81 % | 329 passed |
| E | 618 passed | 96,81 % | 329 passed |

Al usar cada mensaje de commit, el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra.

### Fase A — Una sola forma de inyectar la identidad bajo guard admin (la más pequeña)

- **Archivos (3):** `app/api/dependencies.py`, `app/api/routers/user.py`, `app/api/routers/service.py`.
- **Cambios exactos:**
  1. `dependencies.py`: añadir `from typing import Annotated` y una línea en blanco antes de `import jwt`. Al final del
     archivo, tras `get_current_admin_user`, añadir dos líneas en blanco y este bloque:
     ```python
     # --- IDENTITY ALIASES (ADR-0012, point 5) ---
     # The single way a handler receives the caller under a guard: the alias names the guard, so
     # the signature says with which right the route acts.

     UserDep = Annotated[User, Depends(get_current_user)]
     AdminDep = Annotated[User, Depends(get_current_admin_user)]
     ```
  2. `user.py`: borrar `from typing import Annotated` (l.1 y su línea en blanco), `from app.models.user import User` (l.8)
     y el bloque `DEPENDENCY TYPE ALIASES` con los dos alias (l.13-22). El import de `app.api.dependencies` queda así
     (ruff lo parte):
     ```python
     from app.api.dependencies import (
         AdminDep,
         UserDep,
         get_current_admin_user,
         get_current_user,
         get_user_service,
     )
     ```
  3. `service.py`: el import pasa a `from app.api.dependencies import AdminDep, get_current_admin_user, get_service_service`.
     Se borra `from app.models.user import User`. En los seis handlers, `usuario_actual: User = Depends(get_current_admin_user),`
     pasa a `usuario_actual: AdminDep,`:
     - En `crear_paquete` y `modificar_paquete` la línea se queda donde está.
     - En `activar_paquete`, `desactivar_paquete`, `borrar_paquete_logico` y `recuperar_paquete` sube justo antes de
       `service_service: …`, y en sus docstrings la línea `usuario_actual (User): …` sube también antes de
       `service_service (TouristServicesService): …`.
     - El comentario de segmentación (l.15-21) no cambia.
- **Tests (RED primero):** no hay RED posible. Es un refactor sin cambio de comportamiento: FastAPI resuelve la misma
  dependencia, una vez por petición. La red la forman los 622 tests de la base, sobre todo `tests/test_route_guards.py` y
  `tests/test_services.py`: un handler sin alias trataría `usuario_actual` como cuerpo y daría 422. No se añade ningún
  test.
- **Criterio de aceptación:** compuerta como la fila A (622 passed, 96,47 %). `grep -rn "usuario_actual: User = " app --include=*.py | wc -l` → `0`;
  `grep -rnE "^(UserDep|AdminDep) = " app --include=*.py` → 2 líneas, ambas en `app/api/dependencies.py`.
- **Fuera de alcance:** `audit.py` (fase B), el guard de superadmin (C), los `= Depends(get_service_service)` (D6/S3),
  `get_current_admin_user` como guard de router.
- **Commit:**
  ```
  refactor(api): inject the admin identity through AdminDep only

  ADR-0012 (point 5) fixes one way to receive the caller under a guard,
  so a signature says with which right the route acts. The six package
  mutations in service.py still spelled it out by hand with
  Depends(get_current_admin_user): the aliases lived in user.py, and a
  router does not import another router (BE-40).

  - app/api/dependencies.py: UserDep and AdminDep move here, below the
    guards they name.
  - app/api/routers/user.py: imports the aliases; drops the Annotated
    and User imports it no longer needs.
  - app/api/routers/service.py: the six handlers take
    usuario_actual: AdminDep, placed before the defaulted service
    parameter, and their Args sections follow that order.

  No behaviour changes: FastAPI resolves the same dependency once per
  request, and every route answers as before.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — `GET /auditoria/`: el guard del router decide solo

- **Archivos (4):** `app/services/audit_service.py`, `app/api/dependencies.py`, `app/api/routers/audit.py`, `tests/test_audit.py`.
- **Cambios exactos:**
  1. `audit_service.py`:
     - Borrar `from app.models.user import User` y `from app.services.user_access_policy import UserAccessPolicy`.
     - El constructor pasa a `def __init__(self, audit_repo: AuditRepository) -> None:`, con solo `self.audit_repo = audit_repo`.
     - En `retrieve_audit_history`, borrar el parámetro `current_user: User,`, su línea de Args, la sección `Raises:` entera y
       la línea `self.user_access_policy.assert_is_admin_plus(current_user)` con la línea en blanco que la sigue.
     - El resumen y el primer párrafo del docstring quedan así:
       ```
       Retrieves one page of the global audit history, newest first.

       Who may read it is decided before this call, by the admin guard of the audit
       router (ADR-0012, point 1); the service applies no role rule of its own.
       ```
     - `log_transaction` no cambia.
  2. `dependencies.py`, `get_audit_service`: borrar el parámetro `user_access_policy: …`; el cuerpo pasa a
     `return AuditService(audit_repo)`.
  3. `audit.py`:
     - El import pasa a `from app.api.dependencies import get_audit_service, get_current_admin_user`.
     - Borrar `from app.models.user import User`, el parámetro `usuario_actual: User = Depends(get_current_user),` y el
       argumento `current_user=usuario_actual,`.
     - Las ocho primeras líneas del cuerpo del docstring (de "Defense in depth" a "pagination and prevent…") se sustituyen
       por este texto:
       ```
       The router-level admin guard is the only role check on this route
       (ADR-0012, point 3); the handler needs no identity, so it injects none.
       Utilizes limit/offset parameters to establish cursor-less pagination and
       prevent RAM exhaustion on large datasets. Exposes explicit Query Params to
       avoid frontend Over-fetching.
       ```
  4. `tests/test_audit.py`:
     - Imports: borrar `AuthorizationError` y `UserAccessPolicy`; añadir `from sqlalchemy.exc import SQLAlchemyError` tras
       `import pytest`.
     - Sustituir la clase `TestAuditServiceAuthorization` (l.55-99) por `TestAuditServiceHistory`. Docstring de la clase:
       `"""Freezes the history read: a pure delegation to the repository, with no role rule."""`. Conserva el fixture
       `audit_repo` (autospec) y construye `AuditService(audit_repo)`.
     - Al final del archivo, añadir el test HTTP de filtros.
- **Tests (RED primero):**
  - `TestAuditServiceHistory` tiene cuatro tests:
    - `test_forwards_page_and_filters_to_repository_once` (feliz): `limit=5, offset=10, entity_name="User", entity_id="1"`,
      con `assert_called_once_with` de esos cuatro valores; devuelve la lista del repo.
    - `test_uses_first_page_of_twenty_without_filters_by_default` (borde): sin argumentos,
      `assert_called_once_with(limit=20, offset=0, entity_name=None, entity_id=None)`.
    - `test_returns_empty_list_when_repository_has_no_rows` (borde): repo `[]`, `entity_name="Ghost"`, resultado `== []`.
    - `test_propagates_repository_failure` (fallo de BD): `side_effect = SQLAlchemyError("database unavailable")`,
      `pytest.raises(SQLAlchemyError)` y la misma llamada única por defecto.
  - `test_audit_history_filters_by_entity_name_and_id` (HTTP): un admin persiste tres logs con `AuditRepository(db_session)`,
    `("User","1")`, `("User","2")` y `("TouristService","2")`, todos con `performed_by=admin.cedula`. Después hace
    `client.get("/auditoria/", params={"entity_name": "User", "entity_id": "2"}, headers=make_auth_headers(admin))`.
    Espera `200`, `len(logs) == 1`, `logs[0]["entity_name"] == "User"` y `logs[0]["entity_id"] == "2"`. Docstring:
    `"""Both query filters reach the query: only the log matching name and id comes back."""`.
  - RED medido, con solo el archivo de tests nuevo sobre el estado A: `4 failed, 3 passed` en `tests/test_audit.py`. Los
    cuatro unitarios fallan con `TypeError`, porque el constructor aún exige la política. El test HTTP está verde desde el
    principio: es cobertura y borde, no RED.
  - Mutante M4 antes de B (estado A): `333 passed`, sin rojo. Después de B: `2 failed, 334 passed`.
    `test_protected_route_rejects_request_without_token[GET /auditoria/]` y `test_admin_route_rejects_tourist[GET /auditoria/]`.
- **Criterio de aceptación:** compuerta como la fila B (625 passed, 96,82 %) y M4 con el resultado de arriba.
  `grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py` → `0`.
- **Fuera de alcance:** borrar `assert_is_admin_plus` de la política (fase D: aquí queda sin llamadores, todavía con sus
  tests), `log_transaction`, filtrar el historial por rol (Residuales R2), `audit_repository.py`.
- **Commit:**
  ```
  refactor(audit): let the router guard alone decide who reads the trail

  GET /auditoria/ checked the role twice: in the router guard and again
  in AuditService through UserAccessPolicy.assert_is_admin_plus. Each
  check hid the other from the tests, so removing the guard (mutant M4)
  left the suite green (ADR-0012, point 3; BE-39, R1).

  - app/services/audit_service.py: no policy in __init__ and no
    current_user in retrieve_audit_history, whose only reader was the
    re-check.
  - app/api/dependencies.py: get_audit_service builds the service
    without the policy.
  - app/api/routers/audit.py: the handler injects no identity, and its
    docstring names the guard as the only role check.
  - tests/test_audit.py: the service tests pin the delegation to the
    repository (page, filters, defaults, empty result, failure); an
    HTTP test pins both query filters.

  log_transaction and performed_by do not change. M4 now fails two
  tests. assert_is_admin_plus has no caller left; a later commit of
  BE-40 removes it.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — Guard de superadmin para `POST /usuarios/admin`

- **Archivos (3):** `app/api/dependencies.py`, `app/api/routers/user.py`, `tests/test_route_guards.py`.
- **Cambios exactos:**
  1. `dependencies.py`: entre `get_current_admin_user` y el bloque de alias, añadir lo siguiente (dos líneas en blanco
     antes y después):
     ```python
     async def get_current_superadmin_user(current_user: User = Depends(get_current_user)) -> User:
         """Lets only superadmins through: the role guard of superadmin-only routes.

         Built on get_current_user, not on the admin guard, so the superadmin rule is checked
         once and on its own (ADR-0012, points 1 and 3). As a route dependency it runs before
         body validation: any other role gets 403 whatever the body.

         Args:
             current_user (User): The active user resolved from the JWT session.

         Returns:
             User: The same user, once known to be a superadmin.

         Raises:
             HTTPException: 403 Forbidden if the user's role is not 'superadmin'.
         """
         if current_user.role != UserRole.superadmin:
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN, detail="Privilegios insuficientes."
             )
         return current_user
     ```
     Tras `AdminDep = …`, añadir `SuperadminDep = Annotated[User, Depends(get_current_superadmin_user)]`.
  2. `user.py`:
     - En el import de `app.api.dependencies`, añadir `SuperadminDep,` tras `AdminDep,` y `get_current_superadmin_user,` tras
       `get_current_admin_user,`.
     - El bloque de comentario `ROUTER SEGMENTATION` queda así:
       ```python
       # -------------------------------------------------------------------
       # ROUTER SEGMENTATION (RBAC at the transport boundary, ADR-0012)
       # Each router's guard decides the role, once:
       #   - public_router: no auth dependency (registration, login, verification).
       #   - self_service_router: requires an authenticated session; handlers inject
       #     the user only when the service needs the identity (audit, ABAC).
       #   - admin_router: requires admin/superadmin privileges; handlers inject the
       #     user only when the service needs the identity.
       #   - superadmin_router: requires superadmin privileges (provisioning of
       #     administrative accounts).
       # Services keep the rules that depend on the data (hierarchical ABAC, data
       # scoping) and never check the caller's role again.
       # -------------------------------------------------------------------
       ```
     - Tras `admin_router = …`, añadir
       `superadmin_router = APIRouter(dependencies=[Depends(get_current_superadmin_user)])`.
     - Antes de `crear_administrador`, añadir un encabezado de sección `# SUPERADMIN ENDPOINTS (superadmin only)`, con el
       mismo formato de tres líneas que `# ADMIN ENDPOINTS`, seguido de dos líneas en blanco.
     - El decorador pasa a
       `@superadmin_router.post("/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)` y el parámetro
       a `usuario_actual: SuperadminDep,`.
     - El párrafo del docstring de `crear_administrador` pasa a:
       ```
       Only a superadmin reaches this handler: the superadmin_router guard decides
       the role before the body is validated, so an admin gets 403 whatever the
       body (ADR-0012, Consequences).
       ```
       y su línea de Args a `usuario_actual (User): Authenticated superadmin executing the operation.`
     - Al final del archivo, añadir `router.include_router(superadmin_router)`.
  3. `tests/test_route_guards.py`:
     - Docstring de `ProtectedRoute`, l.24:
       `guard: "superadmin" for get_current_superadmin_user, "admin" for` y, en la línea siguiente con 12 espacios,
       `get_current_admin_user, "user" for get_current_user.`
     - `guard: Literal["superadmin", "admin", "user"]`.
     - Las dos líneas de comentario de `:34-35` pasan a una sola:
       `# Empty on purpose: past a guard, body validation would answer 422 instead of the guard's 403.`
     - Fila: `ProtectedRoute("POST", "/usuarios/admin", "superadmin", _EMPTY_BODY),`.
     - `ADMIN_ROUTES` pasa a ser lo siguiente:
       ```python
       # Every route a tourist may not enter: the admin ones and the superadmin ones.
       ADMIN_ROUTES: tuple[ProtectedRoute, ...] = tuple(
           r for r in PROTECTED_ROUTES if r.guard in ("admin", "superadmin")
       )

       SUPERADMIN_ROUTES: tuple[ProtectedRoute, ...] = tuple(
           r for r in PROTECTED_ROUTES if r.guard == "superadmin"
       )
       ```
     - Tras `test_admin_route_rejects_tourist`, añadir `test_superadmin_route_rejects_admin`, parametrizado sobre
       `SUPERADMIN_ROUTES` con `ids=_route_id`. Su docstring es
       `"""An admin's valid token gets 403 from every superadmin route, before body validation."""`. Usa
       `admin = await persist_user(role=UserRole.admin)`, la misma petición que el test de turista con
       `make_auth_headers(admin)` y las mismas cinco aserciones (`403`, sin `www-authenticate`, `set(body) == {"detail"}` y
       `detail` de tipo `str`).
- **Tests (RED primero):**
  - RED medido, con solo `tests/test_route_guards.py` sobre el estado B: `1 failed, 45 passed`.
    `test_superadmin_route_rejects_admin[POST /usuarios/admin]` falla con `assert 422 == 403`: hoy el admin pasa el guard
    y responde la validación del cuerpo.
  - `test_admin_route_rejects_tourist[POST /usuarios/admin]` sigue en la lista (14 casos).
  - Mutantes sobre el estado C:
    - MS1: `1 failed, 336 passed` (`test_superadmin_route_rejects_admin[POST /usuarios/admin]`).
    - MS2: el mismo `1 failed, 336 passed`.
    - MS3: `2 failed, 335 passed` (más `test_admin_route_rejects_tourist[POST /usuarios/admin]`).
    - Que MS1 tumbe 1 y no 2 es lo esperado: `assert_can_provision_admin` todavía tapa `tests/test_auth.py:379` (fase D).
- **Criterio de aceptación:**
  - Compuerta como la fila C (626 passed, 96,84 %) y mutantes con los resultados de arriba.
  - `tests/test_auth.py` sin cambios y verde.
  - `grep -cE '^    ProtectedRoute\(".*", "superadmin"' tests/test_route_guards.py` → `1`.
- **Fuera de alcance:**
  - Borrar `assert_can_provision_admin` (fase D).
  - Cambiar el método, la ruta o el schema de la provisión.
  - Un caso "superadmin pasa el guard" en la tabla: ya lo cubre `tests/test_auth.py` con el 201.
  - `AGENTS.md:48` (lo corrige David, adenda punto 4).
- **Commit:**
  ```
  feat(auth)!: guard POST /usuarios/admin with a superadmin dependency

  Provisioning an administrative account depends only on the caller's
  role, yet the route sat under the admin guard while the superadmin
  rule lived in UserAccessPolicy (ADR-0012, point 1). The new guard
  replaces the admin guard on this route instead of adding to it.

  - app/api/dependencies.py: get_current_superadmin_user, built on
    get_current_user, and the SuperadminDep alias.
  - app/api/routers/user.py: superadmin_router carries that guard; the
    route moves to it with the same method, path and body; the router
    comments state the frontier as ADR-0012 does.
  - tests/test_route_guards.py: the row takes guard "superadmin" and
    keeps its tourist case; a new case sends an admin with an empty
    body and expects 403.

  BREAKING CHANGE: an admin token on POST /usuarios/admin with an
  invalid body now gets 403 instead of 422, because the guard answers
  before body validation. With a valid body it was and stays 403.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase D — La política sin reglas de solo rol

- **Archivos (4):** `app/services/user_access_policy.py`, `app/services/user_service.py`,
  `tests/test_user_access_policy.py`, `tests/test_user_service.py`.
- **Cambios exactos:**
  1. `user_access_policy.py`:
     - Borrar `assert_can_provision_admin` y `assert_is_admin_plus` (l.98-134, con sus líneas en blanco).
     - En el docstring de la clase, la frase `layer remains transport-agnostic.` pasa a:
       ```
       layer remains transport-agnostic. Rules that depend only on the actor's role
       are decided by the HTTP guards, not here (ADR-0012, point 1).
       ```
  2. `user_service.py`, `create_administrative_account`:
     - Borrar la línea `self.user_access_policy.assert_can_provision_admin(current_user)` y la línea en blanco que la
       sigue, así como la línea `AuthorizationError: 403 Forbidden if the requester is not a superadmin.` de `Raises:`.
     - El primer párrafo del docstring (l.378-382) pasa a:
       ```
       The caller is a superadmin: the route's guard decided it (ADR-0012,
       point 1), so the service checks no role. The account is created
       instantly without requiring email verification.
       ```
     - La línea de Args de `current_user` pasa a
       `current_user (User): The authenticated superadmin executing the creation;` y, en la línea siguiente con 16
       espacios, `recorded as the author of the audit entry.`
  3. `tests/test_user_access_policy.py`: borrar las clases `TestAssertCanProvisionAdmin` y `TestAssertIsAdminPlus`
     (l.260-314, 8 tests).
  4. `tests/test_user_service.py`:
     - En el import de `app.core.exceptions`, borrar `AuthorizationError,`. Añadir
       `from sqlalchemy.exc import SQLAlchemyError` tras `import pytest`.
     - Sustituir `test_create_administrative_account_rejects_non_superadmin` (l.357-366) por
       `test_create_administrative_account_lookup_failure_writes_nothing(user_repo, audit_service, user_service, make_user)`.
       Su docstring es `"""Unhappy path: a failing duplicate lookup aborts before the audit entry and the insert."""`.
       El test pone `user_repo.get_user_by_email_or_cedula.side_effect = SQLAlchemyError("database unavailable")`, llama a
       `create_administrative_account(_admin_payload(), make_user(role=UserRole.superadmin))` dentro de
       `pytest.raises(SQLAlchemyError)` y comprueba `audit_service.log_transaction.assert_not_awaited()` y
       `user_repo.create_user.assert_not_awaited()`.
- **Tests (RED primero):**
  - El RED de esta fase es un mutante, como M4 en B. Antes de tocar nada, MS1 sobre el estado C da `1 failed`:
    `tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row` sigue verde porque lo tapa la política.
    Después de D, MS1 da `2 failed, 327 passed`: ese test cae también.
  - MS2: `2 failed, 327 passed`. MS3: `3 failed, 326 passed`. M4: `2 failed, 327 passed`.
  - El test nuevo de `test_user_service.py` está verde antes y después: sustituye al retirado para mantener dos caminos de
    fallo (duplicado y BD).
- **Criterio de aceptación:**
  - Compuerta como la fila D (618 passed, 96,81 %) y mutantes con los resultados de arriba.
  - `grep -rn "assert_is_admin_plus\|assert_can_provision_admin" app tests --include=*.py | wc -l` → `0`.
- **Fuera de alcance:**
  - `assert_can_delete`, `assert_can_update` (incluida la l.66), `assert_can_recover` (incluida la l.93) y `can_see`.
  - El orden auditoría-antes-que-inserción de `create_administrative_account` (backlog A3).
  - `B-GHOST-ADMIN`.
- **Commit:**
  ```
  refactor(policy): drop the role-only rules the guards now decide

  assert_can_provision_admin and assert_is_admin_plus inspect nothing
  but the actor's role, which the superadmin and admin guards now
  decide. Keeping them would check each rule twice and hide the guards
  from the HTTP tests, as the re-check on /auditoria/ did (ADR-0012,
  point 3).

  - app/services/user_access_policy.py: both methods go; the class
    docstring says role-only rules belong to the guards.
  - app/services/user_service.py: create_administrative_account no
    longer calls the policy, and its docstring stops defending that
    check.
  - tests/test_user_access_policy.py: the eight tests of the two
    methods go.
  - tests/test_user_service.py: the non-superadmin rejection test
    gives way to a lookup failure test, so provisioning keeps two
    unhappy paths in the service.

  The data-dependent rules (delete, update, recover, can_see) do not
  change. With the superadmin guard weakened to the admin rule, the
  HTTP test of an admin provisioning with a valid body now fails as
  well.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase E — La búsqueda de duplicados, afirmada con sus argumentos (E1)

- **Archivos (1):** `tests/test_user_service.py`. Dominio: tests del servicio de usuarios. `app/` no se toca.
- **Cambios exactos:** cuatro tests ganan el mismo bloque de tres líneas, con la forma de `:113-115` (en una sola línea
  pasaría de 100 columnas). Los valores salen del payload de cada test: `_tourist_payload()` (`:35-46`) y
  `_admin_payload()` (`:49-62`).
  ```python
      user_repo.get_user_by_email_or_cedula.assert_awaited_once_with(
          email="<email>", cedula="<cedula>"
      )
  ```
  1. `test_register_tourist_duplicate_raises_already_exists` (`:125`): `email="turista@example.com", cedula="1005911792"`,
     justo antes de `user_repo.create_user.assert_not_called()` (`:132`).
  2. `test_create_administrative_account_provisions_admin` (`:320`): `email="newadmin@test.com", cedula="5555555555"`,
     justo antes de `user_repo.create_user.assert_awaited_once_with(created_user)` (`:333`).
  3. `test_create_administrative_account_duplicate_raises_already_exists` (`:343`): los valores de admin, justo antes de
     `user_repo.create_user.assert_not_awaited()` (`:354`).
  4. `test_create_administrative_account_lookup_failure_writes_nothing` (`:357`): los valores de admin, justo antes de
     `audit_service.log_transaction.assert_not_awaited()` (`:368`).
  - Nada más cambia: nombres, docstrings, imports y demás aserciones quedan igual. Diff: 12 líneas añadidas, 0 borradas.
- **Tests (RED primero):**
  - No hay RED contra el código actual: las cuatro aserciones afirman lo que el servicio ya hace. El RED es un mutante,
    como M4 en B y MS1 en D (ML1 y ML2 en la tabla de mutantes). Medido el 12 nov en copias desechables de `4ce8db3`
    (`app/` y `tests/` iguales a `09ec81b`):

    | Mutante | Antes de E (estado D) | Después de E |
    |---|---|---|
    | Control | `329 passed` | `329 passed` |
    | ML1 | `1 failed, 328 passed` (`test_register_tourist_returns_registration_result`) | `2 failed, 327 passed` (más `test_register_tourist_duplicate_raises_already_exists`) |
    | ML2 | `329 passed`: sobrevive a toda la suite | `3 failed, 326 passed` (`test_create_administrative_account_provisions_admin`, `…_duplicate_raises_already_exists` y `…_lookup_failure_writes_nothing`) |

  - ML2 confirma el dato de E1.4: hoy ningún test vigila los argumentos de la búsqueda de
    `create_administrative_account` (`user_service.py:394-396`).
  - M4, MS1, MS2 y MS3 re-medidos sobre el estado E: los mismos `2`, `2`, `2` y `3 failed` del estado D.
- **Criterio de aceptación:**
  - Compuerta como la fila E (618 passed, 96,81 %). El número de tests no cambia y la cobertura tampoco: `--cov=app` no
    mide `tests/` (medido: `TOTAL 961 19 136 16 96.81%`).
  - ML1 y ML2 con los resultados de la columna "Después de E".
  - `grep -c "get_user_by_email_or_cedula.assert_awaited_once_with" tests/test_user_service.py` → `5`.
  - `git diff --numstat 09ec81b HEAD -- app tests alembic conftest.py` → una sola línea: `12	0	tests/test_user_service.py`
    (separada por tabuladores).
- **Fuera de alcance:**
  - `app/`.
  - `test_register_tourist_returns_registration_result`, que ya afirma la búsqueda (`:113`).
  - Los demás mocks del archivo sin aserción de argumentos y los de otros archivos (Residuales, R5).
  - Renombrar, reordenar o reescribir tests.
- **Commit:**
  ```
  test(doubles): assert the duplicate lookup with its arguments

  Only one of the five tests that stub get_user_by_email_or_cedula in
  test_user_service.py checked how it was called. A lookup with a wrong
  cedula in create_administrative_account left the whole suite green
  (mutant ML2): no test pinned the arguments of that call, and AGENTS 5
  asks for mock calls with their arguments (BE-40, E1).

  The tourist duplicate test and the three provisioning tests (happy
  path, duplicate, lookup failure) now assert one awaited lookup with
  the email and cedula of their payload.

  No production code changes. Mutant ML2 now fails three tests, and
  ML1 (the same change in register_tourist) fails two instead of one.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Se ejecuta desde la raíz del repo, tras la fase D. Las cifras cuentan el texto literal que dicta este plan (docstrings,
comentarios y nombres de tests incluidos) y se midieron sobre la copia del estado D.

```bash
# 1. Archivos tocados: exactamente 11 (7 de app/, 4 de tests/); alembic/ y conftest.py, ninguno
git diff --name-only 41ff01d HEAD -- app tests alembic conftest.py | wc -l                 # 11
git diff --name-only 41ff01d HEAD -- alembic conftest.py tests/conftest.py tests/test_auth.py | wc -l   # 0
# 2. Reglas de solo rol fuera de la política: 0
grep -rn "assert_is_admin_plus\|assert_can_provision_admin" app tests --include=*.py | wc -l   # 0
# 3. Política fuera del servicio de auditoría: 0 y 0
grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py     # 0
grep -A3 "def get_audit_service" app/api/dependencies.py | grep -c "user_access_policy"       # 0
# 4. Predicados de rol en app/: 6 (dependencies.py 2: admin+ y superadmin; política 4: l.66, 74, 93, can_see)
grep -rnE "role (not )?in \[|role ?[!=]= ?UserRole" app --include=*.py | wc -l               # 6
grep -cE "role (not )?in \[|role ?[!=]= ?UserRole" app/api/dependencies.py                    # 2
# 5. Identidad en routers: 4 Depends(get_current_(admin_)user) y todos en APIRouter(dependencies=…); 13 con alias; 0 a mano
grep -rnE "Depends\(get_current_(admin_)?user\)" app/api/routers --include=*.py | wc -l       # 4
grep -rnE "Depends\(get_current_(admin_)?user\)" app/api/routers --include=*.py | grep -vc "APIRouter(dependencies="   # 0
grep -rnE "usuario_actual: (UserDep|AdminDep|SuperadminDep)" app/api/routers --include=*.py | wc -l   # 13
grep -rn "usuario_actual: User = \|= Depends(get_current" app/api/routers --include=*.py | wc -l      # 0
grep -rnE "^(UserDep|AdminDep|SuperadminDep) = " app --include=*.py | wc -l                  # 3 (todas en dependencies.py)
# 6. Guard de superadmin: 7 líneas (dependencies.py 2, user.py 4, test_route_guards.py 1)
grep -rniE "superadmin_user|SuperadminDep" app tests --include=*.py | wc -l                  # 7
# 7. Comentarios de frontera contradictorios: 0
grep -rniE "defen[cs]e in depth|re-asserts|not a duplicate of the transport|gates transport access" app --include=*.py | wc -l   # 0
# 8. Inventario: 17 filas; 1 superadmin (la de provisión), 13 admin, 3 user; cabecera afirmada 3 veces
grep -n '"/usuarios/admin"' tests/test_route_guards.py    # 42:    ProtectedRoute("POST", "/usuarios/admin", "superadmin", _EMPTY_BODY),
grep -c '^    ProtectedRoute("' tests/test_route_guards.py                                   # 17
grep -cE '^    ProtectedRoute\(".*", "superadmin"' tests/test_route_guards.py                 # 1
grep -cE '^    ProtectedRoute\(".*", "admin"' tests/test_route_guards.py                      # 13
grep -c "www-authenticate" tests/test_route_guards.py                                         # 3
# 9. AuthorizationError ya no se importa donde se retiraron sus tests: 0 y 0
grep -c "AuthorizationError" tests/test_audit.py tests/test_user_service.py
# 10. Casos de la tabla: 46 (1 inventario + 17 sin token + 14 turista + 1 admin en superadmin + 3 usuario + 1 higiene + 9 públicas)
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider        # 46 passed
# 11. Compuerta: exit 0; 618 passed; 96,81 % (≥ 96,47 %); 61 files; mypy 56 source files; 4 kept; 8 warnings
./venv/Scripts/python.exe scripts/check.py
```

12. Mutantes sobre la copia del estado final (procedimiento común): M4 `2 failed, 327 passed`
    (`test_protected_route_rejects_request_without_token[GET /auditoria/]` y `test_admin_route_rejects_tourist[GET /auditoria/]`),
    MS1 `2 failed, 327 passed` (`test_superadmin_route_rejects_admin[POST /usuarios/admin]` y
    `tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row`), MS2 `2 failed, 327 passed` (los mismos),
    MS3 `3 failed, 326 passed` (los de MS1 más `test_admin_route_rejects_tourist[POST /usuarios/admin]`). Si el auditor no
    puede crear la copia, lo declara como bloqueo y no da el mutante por medido (adenda, punto 3).

13. Fase E, tras su commit. Los pasos 1-12 no cambian: `tests/test_user_service.py` ya está entre los 11 archivos del
    paso 1, y los mutantes del paso 12 dan lo mismo sobre el estado E (medido).

    ```bash
    git diff --numstat 09ec81b HEAD -- app tests alembic conftest.py                         # 12	0	tests/test_user_service.py
    grep -c "get_user_by_email_or_cedula.assert_awaited_once_with" tests/test_user_service.py  # 5
    grep -c 'email="newadmin@test.com", cedula="5555555555"' tests/test_user_service.py        # 3
    grep -c 'email="turista@example.com", cedula="1005911792"' tests/test_user_service.py      # 2
    ```

14. Mutantes de la fase E sobre la copia del estado final (procedimiento común): ML1 `2 failed, 327 passed`
    (`test_register_tourist_returns_registration_result` y `test_register_tourist_duplicate_raises_already_exists`), ML2
    `3 failed, 326 passed` (`test_create_administrative_account_provisions_admin`,
    `test_create_administrative_account_duplicate_raises_already_exists` y
    `test_create_administrative_account_lookup_failure_writes_nothing`). Antes de mirar el resultado, un
    `sed -n '75p;395p' app/services/user_service.py` sobre la copia confirma que solo cambió la línea del mutante.

## Residuales

- **R1: el autor de las seis mutaciones de paquetes no lo fija ningún test.** `performed_by` solo se comprueba en
  `tests/test_user_service.py:117,334`. En `tests/test_services.py` no hay ninguna aserción sobre `log_transaction` ni
  sobre `performed_by` (grep: 0). Un handler que pasara otra identidad al servicio seguiría en verde. Destino: fila nueva
  en `B-TESTS`. *Texto sugerido:* "Ningún test fija `performed_by` de crear, modificar, activar, desactivar, borrar y
  recuperar paquete; un test HTTP por mutación que lea el `AuditLog` y compare con la cédula del admin".
- **R2: qué puede leer un admin del historial de auditoría.** Ya está anotado (verificación, adenda: "Fuera de BE-40";
  `docs/CONTEXT.md:318`). Si se decide una regla, depende del dato y va en la política, con fila propia. BE-40 no la toca.
- **R3: `AGENTS.md:48`.** La viñeta del inventario enumera los guards `"admin"` o `"user"`. Hay que añadir `"superadmin"`
  y decir que una ruta de superadmin entra en `ADMIN_ROUTES` (caso turista) y en `SUPERADMIN_ROUTES` (caso admin). Lo
  hace David en un commit de documentos antes de `/pr` (adenda, punto 4).
- **R4: cierre en el backlog.** La fila D1 (`docs/backlog.md:114`) cita "`user_access_policy.py:130` por el re-chequeo de
  auditoría, que BE-40 retira". Al cerrar, la sesión Mentor anota que se retiró (fase B y D). La nota de BE-42 debe
  recoger que `get_current_superadmin_user` se apoya en `get_current_user` y que `PROTECTED_ROUTES` ya trae la fila
  `"superadmin"`.

- **R5: más mocks sin argumentos en `tests/test_user_service.py`** (visto al redactar la fase E; leído, no medido con
  mutantes). `get_user_by_cedula` se configura en `:144, 157, 172, 183` y `get_non_deleted_user_by_email` en
  `:200, 217, 230, 241`, y ningún test afirma con qué argumentos se llamaron. `activate_user` en
  `test_verify_email_missing_user_raises_not_found` (`:307`) tampoco. E1.4 los deja fuera. Destino sugerido: fila nueva
  en `B-TESTS-2`, junto a BE-48. *Texto sugerido:* "En `test_user_service.py`, afirmar los argumentos de
  `get_user_by_cedula`, `get_non_deleted_user_by_email` y `activate_user` donde se configuran; medir antes con un mutante
  por llamada del servicio".

## Referencias

- FastAPI · 0.135.1 · alias `Annotated[..., Depends(...)]` compartido entre rutas ·
  https://fastapi.tiangolo.com/tutorial/dependencies/#share-annotated-dependencies
- FastAPI · 0.135.1 · el guard del router y el alias del handler son la misma dependencia, y FastAPI la ejecuta una sola
  vez por petición · https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/#using-the-same-dependency-multiple-times
- FastAPI · 0.135.1 · las dependencias del router se ejecutan antes que las de la ruta y que los parámetros
  (https://fastapi.tiangolo.com/tutorial/bigger-applications/). En la fuente instalada, `fastapi/dependencies/utils.py:625-709`
  resuelve las sub-dependencias antes de validar ruta, query y cuerpo. Por eso el guard responde 403 antes del 422.

## Decisiones abiertas para David

> **Cerradas el 12 nov a las 11:22: ver E0 en "Enmiendas aprobadas".** Ninguna espera respuesta.

- **P1: dónde viven los alias.** La adenda dice "`SuperadminDep` junto a `UserDep`/`AdminDep` (`user.py:20-21`)". El plan
  los lleva los tres a `app/api/dependencies.py`, porque `service.py` no puede usarlos sin importar otro router. Siguen
  juntos. Alternativa: dejarlos en `user.py` y duplicar `AdminDep` en `service.py`, lo que va contra el punto 5 de
  ADR-0012. Sin ADR en ningún caso: es el "cómo" del punto 5 (ADR-0009, punto 2). Si quieres dejarlo escrito, es un
  addendum tuyo a ADR-0012.
- **P2: `feat(auth)!` y `BREAKING CHANGE` en la fase C.** El plan marca la ruptura porque el código de estado cambia para
  un caso que hoy existe (admin con cuerpo inválido). La alternativa es `refactor(auth):` sin `!`, si consideras que
  ningún cliente real lo ve (Flutter solo muestra esa pantalla al superadmin).
- **P3: confirmar con Flutter el 422 → 403 antes del merge.** Viene de la adenda y sigue sin respuesta. No bloquea las
  fases; bloquea el PR.
- **P4: los dos tests que no retiran nada.** El test HTTP de filtros (fase B) y el de fallo de BD en la provisión (fase D)
  no salen de la verificación. El primero sostiene la cobertura: sin él, el estado final quedaría en 96,44 % (medido). El
  segundo mantiene dos caminos de fallo en el servicio (AGENTS §5). Si prefieres no añadirlos, la cobertura final
  baja a menos de la línea base.
- **P5: el nombre `ADMIN_ROUTES`.** Se conserva, con el filtro ampliado y un comentario, para no tocar el test de turista.
  La alternativa es renombrarlo (p. ej. `TOURIST_FORBIDDEN_ROUTES`), con más diff y la misma cifra.

## Enmiendas aprobadas

### E0 — 12 nov 2026, 11:22 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «ok, sí a las cuatro y, con relación al hallazgo de las pruebas, mándalo al backlog y a un bloque
B-TEST-2 que por ahora no entra al cronograma, por ahora lo consideraré trabajo futuro».

**Plan aprobado: fases A → B → C → D como están escritas, con las dos correcciones de dictado de abajo.** La tabla de
compuerta, los mutantes, los commits y las cifras no cambian. Si un punto de arriba y E0 difieren, rige E0.

1. **Corrección a la fase A, criterio de aceptación.** Donde dice
   `grep -rn "usuario_actual: User = " app --include=*.py | wc -l` → `0`, léase:
   `grep -n "usuario_actual: User = " app/api/routers/service.py app/api/routers/user.py | wc -l` → `0`.
   Razón (medida por la sesión Mentor sobre `3798db4`): al terminar la fase A queda una coincidencia en `app/`,
   `app/api/routers/audit.py:24`, que la propia fase A deja fuera de alcance y que retira la fase B. El comando original
   daría `1` con la fase bien ejecutada. El segundo grep del criterio (`^(UserDep|AdminDep) = ` → 2 líneas en
   `app/api/dependencies.py`) no cambia. La comprobación sobre todo `app/` vale desde el final de la fase B (paso 5 de la
   Verificación final).
2. **Corrección a la fase B, punto 3, docstring de `obtener_historial_auditoria`.** Donde dice "Las ocho primeras líneas
   del cuerpo del docstring (de "Defense in depth" a "pagination and prevent…")", léase: **el párrafo entero del cuerpo,
   `app/api/routers/audit.py:28-34`, siete líneas, desde `Defense in depth: the router-level dependency…` hasta
   `Query Params to avoid frontend Over-fetching.` inclusive**. El texto de sustitución (cinco líneas) ya termina en
   `avoid frontend Over-fetching.`; si la l.34 se conservara, esa frase quedaría repetida. La línea de resumen (l.26) y la
   línea en blanco (l.27) no cambian. Comprobación añadida al criterio de la fase B:
   `grep -c "Over-fetching" app/api/routers/audit.py` → `1`.
3. **P1: sí.** Los tres alias (`UserDep`, `AdminDep`, `SuperadminDep`) viven en `app/api/dependencies.py`. Afina el punto 1
   de la adenda, que los situaba en `user.py:20-21`: `service.py` no puede importarlos de otro router. Sin ADR ni addendum.
4. **P2: `feat(auth)!` con `BREAKING CHANGE`**, como dicta el plan. El código de estado cambia para un caso que la API
   admite hoy; que el cliente no lo alcance se explica en la descripción del PR.
5. **P3: resuelto antes del plan** (David, 12 nov, 10:43; bitácora `2026-11-12`): la evidencia del 5 nov basta para el
   cambio 422 → 403; no se revisa el cliente Flutter antes del merge y se declara en el PR. Las frases "Hay que confirmarlo
   con el cliente Flutter antes de fusionar" (Resumen) y "Pendiente de confirmar con Flutter antes del merge" (Riesgos, 1)
   quedan superadas; no bloquea el PR.
6. **P4: sí a los dos tests** (HTTP de filtros en la fase B; fallo de BD en la búsqueda de duplicados en la fase D).
7. **P5: `ADMIN_ROUTES` conserva el nombre**, con el filtro ampliado y el comentario que dicta la fase C.
8. **R1 tiene destino:** fila **BE-48** en `docs/backlog.md`, bloque **`B-TESTS-2`** (nuevo, sin fechar; PLAN §2b; David
   lo nombró "B-TEST-2" a las 11:22 y fijó `B-TESTS-2` a las 11:29), no `B-TESTS`, que está cerrado. Precisión de la
   sesión Mentor al texto de R1: `performed_by` se comprueba también en
   `tests/test_user_access_policy.py:647,675,711`; lo que no tiene ninguna aserción es `tests/test_services.py`.
   Ninguna fase de BE-40 lo toca.

`progress.json` no cambia (`current_target: Fase_A`).

### E1 — 12 nov 2026, 12:38 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «nos vamos por la opción A (fase E) para solucionar el hueco del opcional».

**Origen:** opcional de la auditoría de la fase D (`docs/deuda/BE-40/gaps.md`, bloque "Auditoría Fase D"): el test
sustituto `test_create_administrative_account_lookup_failure_writes_nothing` (`tests/test_user_service.py:357-369`), que
este plan dictó, comprueba que no hubo escrituras pero no con qué argumentos se llamó a la búsqueda que falla. AGENTS §5
pide llamadas a mocks con argumentos. Es un defecto del artefacto del propio ítem: se corrige dentro del ítem, con una
fase nueva (regla de David del 11 nov; precedentes: E0 y E2 de BE-39).

**Fase E nueva. Las fases A–D, sus commits, sus cifras y sus auditorías no cambian.**

1. **Alcance: un archivo, `tests/test_user_service.py`** (los tests exactos, en el punto 4). Se añade la aserción de la llamada a
   `user_repo.get_user_by_email_or_cedula` con sus dos argumentos por nombre (`email`, `cedula`), una sola vez. Los valores
   salen de `_admin_payload()` (`tests/test_user_service.py:49-62`: `cedula="5555555555"`, `email="newadmin@test.com"`); la
   llamada del servicio es `app/services/user_service.py`, `create_administrative_account`,
   `get_user_by_email_or_cedula(email=user_data.email, cedula=user_data.cedula)`. `app/` no se toca.
2. **El planificador dicta el texto exacto de la aserción y lo mide** (regla "medir antes de dictar"): compuerta
   completa, y un mutante en la copia desechable que demuestre que la aserción vigila (la llamada del servicio con un
   argumento cambiado: sin la aserción la suite queda en verde; con ella, cae este test). Declara cuántos tests caen y
   cuáles. El número de tests no cambia (618); si la cobertura cambia, lo dice.
3. **El planificador recalcula solo lo que depende de E1:** sección "Fase E" con el formato de las demás (archivos,
   cambio exacto, RED o mutante, criterio de aceptación, fuera de alcance, commit), fila E en la tabla de compuerta,
   fila del mutante nuevo en la tabla de mutantes, pasos de la Verificación final que cambien, y `progress.json` con
   `Fase_E` (`pending`) y `current_target: "Fase_E"`. No reescribe nada de A–D.
4. **Alcance ampliado por David (12:40: «sí, la fase E arregla todos los huecos homólogos»).** Medido por la sesión
   Mentor sobre `ed3047a`: cinco tests de `tests/test_user_service.py` configuran `get_user_by_email_or_cedula` y solo uno
   afirma sus argumentos (`test_register_tourist_returns_registration_result`, `:92`, aserción en `:113`). La fase E
   añade la misma aserción (una llamada, `email` y `cedula` por nombre, con los valores del payload de cada test) a los
   otros cuatro:
   - `test_register_tourist_duplicate_raises_already_exists` (`:125`), sobre `user_service.py:74`;
   - `test_create_administrative_account_provisions_admin` (`:320`), sobre `user_service.py:394`;
   - `test_create_administrative_account_duplicate_raises_already_exists` (`:343`), ídem;
   - `test_create_administrative_account_lookup_failure_writes_nothing` (`:357`), ídem (el del opcional).
   Dato que motiva el alcance: hoy ningún test de ese archivo afirma los argumentos de la búsqueda de
   `create_administrative_account` (`user_service.py:394`). Es un dato leído, no ejecutado: si un mutante ahí sobrevive a
   toda la suite lo mide el planificador, con un mutante por cada llamada del servicio (`:74` y `:394`), y declara qué
   tests caen antes y después. Sigue siendo un solo archivo y ningún
   cambio en `app/`. **Fuera de alcance:** cualquier otro mock sin argumentos de ese archivo o de otros; si el
   planificador ve más, van a Residuales.
5. **Cómo se invoca:** mensaje directo al subagente `plan-redactor` ("lee E1 en `docs/deuda/BE-40/plan.md` y escribe la
   fase E"), no `/deuda-planear`, que redacta el plan desde la verificación y podría reescribir fases ya ejecutadas (nota
   de BE-39 en AF-09).

### E2 — 12 nov 2026, 12:57 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «se aprueba (tienes el "aprobado") y creo que hemos descubierto un hueco más hondo de lo que
pensábamos. Se va a su propia fila en el backlog, junto a B-TESTS-2».

1. **Fase E aprobada como está escrita** (sección "Fase E", filas ML1 y ML2, fila E de la compuerta, pasos 13 y 14 de la
   Verificación final). Contraste de la sesión Mentor contra el código, sin correcciones: las cuatro inserciones caen en
   `tests/test_user_service.py:132`, `:333`, `:354` y `:368`; los valores coinciden con `_tourist_payload()` y
   `_admin_payload()`; el bloque de tres líneas es el de `:113-115` y en una línea mediría 114 y 116 columnas;
   `app/services/user_service.py:75` y `:395` contienen la cadena que editan ML1 y ML2. Las cifras las repite el auditor.
2. **R5 tiene destino:** fila **BE-49** en `docs/backlog.md`, bloque `B-TESTS-2` (PLAN §2b), junto a BE-48. Ninguna fase de
   BE-40 lo toca.

`progress.json` no cambia (`current_target: Fase_E`, escrito por el planificador).

# PLAN — BE-39: Dar a cada ruta protegida un test HTTP de rechazo que caiga si su guard desaparece

> Fuente: `docs/deuda/BE-39/verificacion.md` (confirmada, con adenda de siete decisiones de David del 11 nov, 10:48).
> Base: `9ecc176` (`3ca990a` + un commit de documentación, la verificación; `app/` y `tests/` idénticos). Estado:
> **aprobado con E0 y E1 (11 nov, 12:32 y 12:55): cuatro fases, A → D**. Todas las cifras de este plan se midieron hoy
> sobre copias desechables con el contenido exacto que dicta.

## Resumen para aprobación

En cuatro fases, todas en `tests/` y sin tocar `app/`, el plan crea `tests/test_route_guards.py` con una tabla de las 17
rutas protegidas y cuatro tests sobre ella. (A) Un test de inventario compara la tabla y la lista de rutas públicas con
`app.routes`, de modo que una ruta nueva sin entrada hace caer la suite. (B) Las 17 rutas, sin token, responden 401 con
`WWW-Authenticate: Bearer`. (C) Las 14 rutas admin responden 403 a un turista, sin esa cabecera. (D) Las 3 rutas de
usuario dejan pasar a un turista y responde el handler (200, 404, 404), así que una ruta admin etiquetada `"user"` por
error cae (E0). Ningún test lee texto. Los dos tests de `tests/test_audit.py` que cubrían `/auditoria/` se borran en la
fase que los sustituye. La suite pasa de 579 a 612 tests y la cobertura queda en 96,29 % (medido). Cada test nuevo se
midió en rojo frente a su mutante: M1, M2, M3, M6, M7, M4+M5, M9 (sin token), M10 y M11 (inventario), M12 y M14
(etiqueta y guard de usuario); M13, el recíproco de M12, lo mata la fase C.
**Riesgo principal:** M4 sola sigue sin matarse. En `/auditoria/` el re-chequeo de `audit_service.py:65` responde el mismo
403 que el guard, y así seguirá hasta BE-40. Está declarado (adenda, decisión 2) y pasa a la verificación final de BE-40.
Por la misma razón, M7 tumba 13 de las 14 rutas admin, no 14.
**No se toca:** `app/`, `alembic/`, ningún `conftest.py`, `tests/test_services.py`, el re-chequeo de auditoría, el guard de
superadmin, `AdminDep`/`UserDep` (BE-40), el `scope` del token (BE-42), las reglas de dato (`B-GHOST-ADMIN`). Sin ADR.

## Objetivo y decisiones bloqueadas

Objetivo: que quitar o debilitar el guard de cualquier ruta protegida ponga la suite en rojo (ADR-0012, punto 4) y que
una ruta nueva no pueda nacer sin decidir si es pública o protegida.

1. **Solo tests.** `app/` no cambia. Los mutantes se aplican en copias desechables y nunca en el árbol de trabajo (adenda 7).
2. **Un archivo nuevo, `tests/test_route_guards.py`** (adenda 5). Contiene la tabla `PROTECTED_ROUTES` (método, plantilla de
   ruta tal como la declara `app.routes`, guard, cuerpo), `PUBLIC_ROUTES` y tres tests: uno de inventario y dos
   parametrizados. Usuarios y tokens salen de `persist_user` y `make_auth_headers`.
3. **Aserciones fijas.** Sin token: `401`, `headers["www-authenticate"] == "Bearer"`, `set(body) == {"detail"}` y `detail` de
   tipo `str`. Turista en una ruta admin: `403`, sin `www-authenticate` y el mismo cuerpo. No se lee ningún texto (AGENTS §5).
4. **Cuerpo `{}`** en las cinco rutas que declaran cuerpo. En `POST /usuarios/admin` es obligatorio (adenda 3); en las otras
   cuatro da igual, y se usa `{}` por uniformidad. Los parámetros de ruta no nombran ninguna fila (`cedula="0000000000"`,
   `service_id="999"`).
5. **Criterio de mutantes (adenda 2).** Se exige rojo frente a M1, M2, M3, M6, M7, M4+M5, M9, M10 y M11. M4 sola no se exige:
   va a Residuales. M9a (`auto_error=False` sin más) es un mutante equivalente, medido aquí.
6. **M9 (adenda 4)**, en `app/api/dependencies.py`: `auto_error=False` y, además, `get_current_user` devuelve un turista
   fijo cuando no llega token (edición exacta abajo). Tiene que tumbar los 17 tests de 401, y los tumba.
7. **Inventario (adenda 6).** `_declared_routes() == protected | PUBLIC_ROUTES`. `PUBLIC_ROUTES` recoge las 5 rutas públicas
   de la aplicación y las 4 de documentación de FastAPI. HEAD se excluye porque Starlette lo añade a todo GET.
8. **Los dos tests de `tests/test_audit.py` se borran en la fase que los sustituye:** `test_audit_trail_requires_authentication`
   en la B y `test_audit_trail_forbidden_for_tourist` en la C.
9. **Compuerta:** `./venv/Scripts/python.exe scripts/check.py` completa, en verde y sin `--soft` en cada fase (adenda 1).
   Cobertura ≥ 96,29 %.

## Análisis del redactor

**Qué cambia y por qué.** Hoy solo `GET /auditoria/` tiene tests de rechazo, y además flojos. La tabla convierte "una ruta
protegida, un test de rechazo" en datos. Los tests parametrizados recorren esos datos, y el inventario impide que los datos
se queden atrás cuando el código crece (`B-RESERVAS` añadirá rutas). Es el mismo patrón que `_DOMAIN_ERROR_STATUS`
(ADR-0003) y `tests/test_models_registry.py` (ADR-0010).

**Orden y dependencias.** A → B → C, sobre el mismo archivo. A crea la tabla, que B y C consumen. B y C son independientes
en contenido, pero B va antes porque es la que añade `import pytest`, `_PATH_PARAMS`, `_url` y `_route_id`, que C reutiliza.
Se separan porque cada una mata a una familia de mutantes distinta (M9 frente a M1–M7). Así cada handoff y cada auditoría
contrastan un solo criterio.

**Lo que se midió (sonda sobre copia `git archive`, suite sin `test_check*.py`).**
- *M9a es equivalente*: con `auto_error=False` a secas, sale `307 passed` en el estado B y `320 passed` en el C.
  `jwt.decode(None, …)` lanza `DecodeError` (`venv/Lib/site-packages/jwt/api_jws.py:298-299`) y `dependencies.py:131-132`
  la convierte en el mismo 401. Se confirma lo que la adenda había leído sin ejecutar. Por eso M9 necesita la segunda
  edición. El usuario fijo es un turista. Con él, ninguna de las 17 responde 401 y caen los 17 casos (`17 failed`, medido).
- *M1 tumba 6, no 3*: sin guard de router, `upload-images`, `admin/inactivos` y `admin/eliminados` se quedan sin ninguna
  identidad, así que caen también sus casos anónimos. Los otros 6 handlers conservan `Depends(get_current_admin_user)`:
  esa es la doble capa (rincón 3 de la verificación), y M3 la cubre.
- *M7 tumba 13*: en `/auditoria/` el re-chequeo responde el mismo 403. Ese caso cae con M4+M5 (2 failed: el test unitario
  que ya existía y el caso nuevo).
- *Cobertura*: 96,29 % en los tres estados. Los tests borrados de `tests/test_audit.py` no cubren ninguna línea que los
  nuevos no cubran.

**Qué congela comportamiento relacionado.** `tests/test_token_failure_paths.py` congela los 401 con token inválido.
`tests/test_domain_error_handler.py:62-67` fija que el 403 de dominio va sin `www-authenticate`, y eso es lo que hace
indistinguibles el guard y el re-chequeo. `tests/test_auth.py:357-407` congela los 403 de la política (no del guard) en
`recuperar` y `admin`. Nada de eso se toca.

**Estado de la base de datos.** Los tests de rechazo no comprueban que no haya mutación de estado (AGENTS §5), porque no
puede haberla por construcción: las cédulas y los IDs no existen y los cuerpos son `{}`. Lo que se prueba es que el guard
responde antes que la validación y que la búsqueda. Lo midió la verificación y lo confirma la sonda: bajo M7, la misma
petición da 200, 404, 422 o 400.

**Riesgos.**
1. *"403 antes de 422" queda congelado.* Es lo que se busca: el guard corre antes que la validación del cuerpo. BE-40 lo
   conserva en `POST /usuarios/admin`, aunque con otro guard.
2. *Las plantillas de ruta son contrato con el test.* Renombrar un parámetro (`{cedula}`) obliga a tocar la tabla. Es
   deseable: el inventario falla y avisa.
3. *Restos en el scratchpad.* El directorio de pruebas es compartido entre sesiones. Al planear apareció
   `base/tests/test_probe_guard.py`, una sonda de la verificación que inflaba en +1 todas las cuentas. Cada copia se
   extrae en un **directorio nuevo y vacío**. Además, `rm -rf` está denegado.

**Discrepancias con la verificación (leídas o medidas, no cambian el alcance).**
- Patrón 1 (`tests/test_services.py`): la verificación dice que debe ser > 0 al cerrar. Con la decisión 5 de la adenda los
  tests viven en un archivo nuevo, así que sigue en **0**. Su equivalente es el patrón sobre `tests/test_route_guards.py` (Verificación final, 7).
- Patrón 3 (peticiones sin cabeceras): da **4** líneas hoy, no 1. Las otras tres son a rutas públicas
  (`tests/test_auth.py:109`, `tests/test_services.py:648`, `:668`). Al cerrar quedan **3**.

## Regla de alcance

- **Sí:** `tests/test_route_guards.py` (nuevo) y el borrado de dos tests de `tests/test_audit.py`.
- **No:** ninguna línea de `app/`, `alembic/`, `conftest.py` (raíz o `tests/`) ni del resto de `tests/`. Tampoco: renombrar o
  reordenar los demás tests de `tests/test_audit.py`; el comentario de cabecera "INTEGRATION TESTS (router-level gate)"; el
  texto de los `detail`; `docs/backlog.md`, `docs/CONTEXT.md`, `AGENTS.md` (cierre o PR humano).

## Fases

**Procedimiento de mutantes (común).** Se hace antes del commit de la fase y por cada mutante: (1) un directorio nuevo y
vacío en el scratchpad; (2) `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>`; (3) copiar encima, desde el
árbol de trabajo, los archivos de `tests/` que la fase modifica; (4) aplicar la edición de la tabla; (5) desde `<dir>`,
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
Hay que pegar en el handoff la última línea y los `FAILED`.

| Mutante | Archivo de la copia | Edición exacta (original → sustituto) |
|---|---|---|
| M1 | `app/api/routers/service.py` | `admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])` → `admin_router = APIRouter()` |
| M2 | `app/api/routers/service.py` | `import get_current_admin_user, get_service_service` → `import get_current_admin_user, get_current_user, get_service_service`; las 7 `Depends(get_current_admin_user)` → `Depends(get_current_user)` |
| M3 | `app/api/routers/service.py` | M1 + la edición de import de M2 + las 6 `Depends(get_current_admin_user)` restantes → `Depends(get_current_user)` |
| M4 | `app/api/routers/audit.py` | `router = APIRouter(dependencies=[Depends(get_current_admin_user)])` → `router = APIRouter()` |
| M5 | `app/services/audit_service.py` | borrar la línea `        self.user_access_policy.assert_is_admin_plus(current_user)` |
| M6 | `app/api/routers/user.py` | las 2 `Depends(get_current_admin_user)` (l.21, l.37) → `Depends(get_current_user)` |
| M7 | `app/api/dependencies.py` | `if current_user.role not in [UserRole.admin, UserRole.superadmin]:` → `if False:` |
| M9a | `app/api/dependencies.py` | `OAuth2PasswordBearer(tokenUrl="usuarios/login")` → `OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=False)` |
| M9 | `app/api/dependencies.py` | M9a + `import jwt` → `from datetime import UTC, datetime` + línea en blanco + `import jwt` + el bloque de abajo, justo antes de `    credentials_exception = HTTPException(` |
| M10 | `app/main.py` | añadir al final: `@app.get("/ping")` / `async def ping():` / `    return {}` |
| M11 | `app/api/routers/service.py` | borrar la línea `@admin_router.get("/admin/inactivos", response_model=list[ServiceListResponse])` |

Bloque de M9 (cuatro espacios de sangría, dentro de `get_current_user`):
```python
    if token is None:
        return User(
            id=0,
            cedula="0000000001",
            email="anonymous@test.com",
            first_name="Anonymous",
            last_name="Caller",
            password_hash="x",
            role=UserRole.tourist,
            data_consent=True,
            is_active=True,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

```

Compuerta esperada al cerrar cada fase (exit 0, `Compuerta superada.`; ruff check `All checks passed!`; 4 kept; docs ✔):

| Fin de | `ruff format --check` | mypy | pytest | Cobertura | Suite de la copia (sin `test_check*`) |
|---|---|---|---|---|---|
| Base | 60 files | `Success: no issues found in 55 source files` | 579 passed | 96,29 % | 290 passed |
| A | 61 files | `… in 56 source files` | **580 passed** | 96,29 % | 291 passed |
| B | 61 files | 56 | **596 passed** | 96,29 % | 307 passed |
| C | 61 files | 56 | **609 passed** | 96,29 % | 320 passed |
| D | 61 files | 56 | **612 passed** | 96,29 % | 323 passed |

Al usar cada mensaje de commit, el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra.

### Fase A — Inventario: toda ruta es protegida o pública (la más pequeña)
- **Archivos:** `tests/test_route_guards.py` (nuevo).
- **Cambios exactos:** el archivo, entero:
  ```python
  """Route guard tests (ADR-0012, decision 4; BE-39).

  PROTECTED_ROUTES lists every protected route as app.routes declares it (method and path template),
  with the guard that protects it; PUBLIC_ROUTES lists every other route. The inventory test keeps
  both tables equal to app.routes, so a route added without an entry, or an entry whose route is
  gone, fails the suite.
  """

  from typing import Any, Literal, NamedTuple

  from starlette.routing import Route

  from app.main import app


  class ProtectedRoute(NamedTuple):
      """A protected route, keyed as app.routes declares it, with the guard that protects it.

      Attributes:
          method: HTTP method, upper case.
          path: Path template as declared in app.routes (e.g. "/servicios/{service_id}").
          guard: "admin" for get_current_admin_user, "user" for get_current_user.
          body: JSON body sent with the request; None sends no body.
      """

      method: str
      path: str
      guard: Literal["admin", "user"]
      body: dict[str, Any] | None = None


  # Empty on purpose: if a guard let a tourist through, body validation would answer 422, not 403.
  # A valid body to POST /usuarios/admin gets 403 from the provisioning policy and hides the guard.
  _EMPTY_BODY: dict[str, Any] = {}

  PROTECTED_ROUTES: tuple[ProtectedRoute, ...] = (
      ProtectedRoute("GET", "/usuarios/", "admin"),
      ProtectedRoute("GET", "/usuarios/admin/eliminados", "admin"),
      ProtectedRoute("PATCH", "/usuarios/{cedula}/recuperar", "admin"),
      ProtectedRoute("POST", "/usuarios/admin", "admin", _EMPTY_BODY),
      ProtectedRoute("POST", "/servicios/upload-images/", "admin", _EMPTY_BODY),
      ProtectedRoute("POST", "/servicios/", "admin", _EMPTY_BODY),
      ProtectedRoute("GET", "/servicios/admin/inactivos", "admin"),
      ProtectedRoute("GET", "/servicios/admin/eliminados", "admin"),
      ProtectedRoute("PUT", "/servicios/{service_id}", "admin", _EMPTY_BODY),
      ProtectedRoute("PATCH", "/servicios/{service_id}/activar", "admin"),
      ProtectedRoute("PATCH", "/servicios/{service_id}/desactivar", "admin"),
      ProtectedRoute("DELETE", "/servicios/{service_id}", "admin"),
      ProtectedRoute("PATCH", "/servicios/{service_id}/recuperar", "admin"),
      ProtectedRoute("GET", "/auditoria/", "admin"),
      ProtectedRoute("GET", "/usuarios/mi-perfil", "user"),
      ProtectedRoute("DELETE", "/usuarios/{cedula}", "user"),
      ProtectedRoute("PATCH", "/usuarios/{cedula}", "user", _EMPTY_BODY),
  )

  PUBLIC_ROUTES: frozenset[tuple[str, str]] = frozenset(
      {
          ("POST", "/usuarios/registro"),
          ("GET", "/usuarios/verificar-email"),
          ("POST", "/usuarios/login"),
          ("GET", "/servicios/"),
          ("GET", "/"),
          ("GET", "/openapi.json"),
          ("GET", "/docs"),
          ("GET", "/docs/oauth2-redirect"),
          ("GET", "/redoc"),
      }
  )


  def _declared_routes() -> set[tuple[str, str]]:
      """Collect (method, path template) for every route of the app.

      HEAD is left out: Starlette adds it to every GET route, it is not a route of its own.

      Returns:
          The set of (method, path) pairs declared in app.routes.
      """
      declared: set[tuple[str, str]] = set()
      for route in app.routes:
          assert isinstance(route, Route), f"unexpected route type: {route!r}"
          declared |= {(method, route.path) for method in (route.methods or set()) - {"HEAD"}}
      return declared


  def test_every_route_is_listed_as_protected_or_public() -> None:
      """A route in neither table, or an entry with no route behind it, fails here."""
      protected = {(route.method, route.path) for route in PROTECTED_ROUTES}

      assert _declared_routes() == protected | PUBLIC_ROUTES
  ```
- **Tests (RED primero):** con el procedimiento común, copiando `tests/test_route_guards.py`. M10 da `1 failed, 290 passed`
  (`test_every_route_is_listed_as_protected_or_public`). M11 da `2 failed, 289 passed` (el inventario y
  `tests/test_services.py::test_inactive_column_returns_off_rule_package`). Sin mutante, `291 passed`.
- **Criterio de aceptación:** las tres cifras anteriores, `pytest tests/test_route_guards.py -q` → `1 passed` y la fila A
  de la compuerta.
- **Fuera de alcance de esta fase:** los tests de rechazo; `tests/test_audit.py`.
- **Commit:**
  ```text
  test(guards): list every route as protected or public and pin the list

  ADR-0012 (decision 4) asks for a rejection test on every protected
  route, but nothing flags a route that was added without one.
  tests/test_route_guards.py now holds the table of the 17 protected
  routes (method, path template, guard, body) and the set of public
  ones, and one test asserts that together they equal app.routes. A
  route added without an entry fails the suite, and so does an entry
  whose route is gone.

  Same registry pattern as _DOMAIN_ERROR_STATUS (ADR-0003) and
  tests/test_models_registry.py (ADR-0010). The rejection tests that
  read the table come in the next two commits (BE-39).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — Sin token: 401 con `WWW-Authenticate: Bearer` en las 17
- **Archivos:** `tests/test_route_guards.py`, `tests/test_audit.py`.
- **Cambios exactos:**
  - `tests/test_route_guards.py`, tres inserciones: `import pytest` entre la línea en blanco tras `from typing …` y
    `from starlette.routing import Route`. Entre el cierre de `PUBLIC_ROUTES` y `def _declared_routes()`:
    ```python

    # Path parameters that name no stored row: the guard must answer before any lookup could.
    _PATH_PARAMS: dict[str, str] = {"cedula": "0000000000", "service_id": "999"}


    def _url(route: ProtectedRoute) -> str:
        """Fill the route's path template with _PATH_PARAMS."""
        return route.path.format(**_PATH_PARAMS)


    def _route_id(route: ProtectedRoute) -> str:
        """Name a parametrized case after its route, e.g. "PUT /servicios/{service_id}"."""
        return f"{route.method} {route.path}"
    ```
    Y al final del archivo:
    ```python


    @pytest.mark.parametrize("route", PROTECTED_ROUTES, ids=_route_id)
    async def test_protected_route_rejects_request_without_token(client, route: ProtectedRoute) -> None:
        """Without a token, every protected route answers 401 with the Bearer challenge."""
        response = await client.request(route.method, _url(route), json=route.body)

        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        body = response.json()
        assert set(body) == {"detail"}
        assert isinstance(body["detail"], str)
    ```
  - `tests/test_audit.py`: borrar `test_audit_trail_requires_authentication` (`:140-145`) y las dos líneas en blanco que la
    preceden. El archivo termina en `assert logs[0]["action"] == "CREATE"`.
- **Tests (RED primero):** procedimiento común, copiando los dos archivos. M9 da `17 failed, 290 passed`: los 17 casos de
  `test_protected_route_rejects_request_without_token` y ninguno más. M9a da `307 passed`; es equivalente y se pega como
  evidencia de que no basta. Sin mutante, `307 passed`.
- **Criterio de aceptación:** las cifras anteriores, `pytest tests/test_route_guards.py -q` → `18 passed`, `grep -rn
  "test_audit_trail_requires_authentication" tests --include=*.py` → 0 líneas, y la fila B de la compuerta.
- **Fuera de alcance de esta fase:** los tests de turista y `test_audit_trail_forbidden_for_tourist` (fase C).
- **Commit:**
  ```text
  test(guards): reject requests without a token on all 17 protected routes

  Only GET /auditoria/ had a test without a token, and it did not check
  the Bearer challenge. One parametrized test now asks every route of
  the table for a 401 with "WWW-Authenticate: Bearer" and a body that
  holds only "detail", without reading its text.

  - tests/test_route_guards.py: the test, the path parameters it fills
    in and the case ids.
  - tests/test_audit.py: drop test_audit_trail_requires_authentication;
    the GET /auditoria/ case of the new test covers it, with stricter
    assertions.

  Mutant M9 (a request without a token resolved to a fixed tourist)
  fails all 17 cases. auto_error=False alone is an equivalent mutant:
  jwt.decode(None) raises DecodeError and get_current_user answers the
  same 401 (BE-39).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — Turista: 403 sin `WWW-Authenticate` en las 14 admin
- **Archivos:** `tests/test_route_guards.py`, `tests/test_audit.py`.
- **Cambios exactos:**
  - `tests/test_route_guards.py`, tres inserciones: `from app.models.user import UserRole` tras `from app.main import app`.
    Entre el cierre de `PROTECTED_ROUTES` y `PUBLIC_ROUTES`, con una línea en blanco a cada lado:
    `ADMIN_ROUTES: tuple[ProtectedRoute, ...] = tuple(r for r in PROTECTED_ROUTES if r.guard == "admin")`. Y al final:
    ```python


    @pytest.mark.parametrize("route", ADMIN_ROUTES, ids=_route_id)
    async def test_admin_route_rejects_tourist(
        client, persist_user, make_auth_headers, route: ProtectedRoute
    ) -> None:
        """A tourist's valid token gets 403 from every admin route, without a Bearer challenge."""
        tourist = await persist_user(role=UserRole.tourist)

        response = await client.request(
            route.method, _url(route), json=route.body, headers=make_auth_headers(tourist)
        )

        assert response.status_code == 403
        assert "www-authenticate" not in response.headers
        body = response.json()
        assert set(body) == {"detail"}
        assert isinstance(body["detail"], str)
    ```
  - `tests/test_audit.py`: borrar `test_audit_trail_forbidden_for_tourist` (`:50-59`) y las dos líneas en blanco que la
    siguen. El bloque `# ===…` de "UNIT TESTS" queda a dos líneas en blanco del test anterior.
- **Tests (RED primero):** procedimiento común, copiando los dos archivos. Las cifras están en la tabla siguiente; los
  `FAILED` son siempre casos `test_admin_route_rejects_tourist[...]`, salvo los indicados.

  | M1 | M2 | M3 | M4 | M5 | M4+M5 | M6 | M7 |
  |---|---|---|---|---|---|---|---|
  | 6 failed, 314 passed (3 de turista + 3 anónimos: `upload-images`, `admin/inactivos`, `admin/eliminados`) | 9 failed, 311 passed (las 9 de `/servicios`) | 12 failed, 308 passed (9 de turista + los 3 anónimos de M1) | **320 passed (declarado, Residual R1)** | 1 failed, 319 passed (el unitario `TestAuditServiceAuthorization::test_tourist_raises_…`, que ya existía) | 2 failed, 318 passed (el unitario + `[GET /auditoria/]`) | 4 failed, 316 passed (las 4 de `/usuarios`) | 13 failed, 307 passed (todas salvo `[GET /auditoria/]`) |

  Sin mutante, `320 passed`.
- **Criterio de aceptación:** la tabla anterior, `pytest tests/test_route_guards.py -q` → `32 passed`, `grep -rn
  "test_audit_trail_forbidden_for_tourist" tests --include=*.py` → 0 líneas, y la fila C de la compuerta.
- **Fuera de alcance de esta fase:** M4 sola (BE-40); un caso "admin → 403" para `POST /usuarios/admin` (no hay guard de
  superadmin hasta BE-40).
- **Commit:**
  ```text
  test(guards): reject a tourist on all 14 admin routes

  With the role check gone from get_current_admin_user (M7), or the
  admin guard gone from /servicios (M1-M3) or /usuarios (M6), the suite
  stayed green: no test sent a tourist to 13 of the 14 admin routes.
  One parametrized test now asks every admin route of the table for a
  403 to a tourist's token, with a body that holds only "detail" and
  no Bearer challenge.

  - tests/test_route_guards.py: the test and ADMIN_ROUTES.
  - tests/test_audit.py: drop test_audit_trail_forbidden_for_tourist;
    the GET /auditoria/ case of the new test replaces it, with stricter
    assertions.

  M1, M2, M3, M6, M7 and M4+M5 now fail tests. M4 alone does not: the
  re-check in audit_service answers the same 403 until BE-40 removes
  it (BE-39).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase D — La etiqueta `"user"` se comprueba: un turista pasa el guard de las 3 rutas de usuario (E0, punto 3)
- **Archivos:** `tests/test_route_guards.py`.
- **Cambios exactos:** dos inserciones. Tras la línea `ADMIN_ROUTES: …` de la fase C, una línea en blanco y:
  ```python
  USER_ROUTES: tuple[ProtectedRoute, ...] = tuple(r for r in PROTECTED_ROUTES if r.guard == "user")

  # What each user route answers a tourist once its guard lets them through, with _PATH_PARAMS and
  # the table's body: the tourist's own profile, and 404 for a cedula that names no account.
  _TOURIST_PAST_USER_GUARD: dict[tuple[str, str], int] = {
      ("GET", "/usuarios/mi-perfil"): 200,
      ("DELETE", "/usuarios/{cedula}"): 404,
      ("PATCH", "/usuarios/{cedula}"): 404,
  }
  ```
  Y al final del archivo:
  ```python


  @pytest.mark.parametrize("route", USER_ROUTES, ids=_route_id)
  async def test_user_route_lets_tourist_through(
      client, persist_user, make_auth_headers, route: ProtectedRoute
  ) -> None:
      """A tourist's valid token passes the guard of every user route, so the handler answers.

      An admin route labeled "user" by mistake answers 403 here, not its handler's code.
      """
      tourist = await persist_user(role=UserRole.tourist)

      response = await client.request(
          route.method, _url(route), json=route.body, headers=make_auth_headers(tourist)
      )

      assert response.status_code == _TOURIST_PAST_USER_GUARD.get((route.method, route.path))
  ```
- **Por qué el código exacto y no "ni 401 ni 403"** (E0, punto 3, dato medido hoy con una sonda sobre copia nueva): con
  `_PATH_PARAMS` y el cuerpo de la tabla, un turista recibe `200` en `GET /usuarios/mi-perfil`, `404` en
  `DELETE /usuarios/{cedula}` y `404` en `PATCH /usuarios/{cedula}`. Con el cuerpo `{}` de la tabla, el PATCH da 404, no el
  422 que la verificación anotó para "404/422". El código exacto descarta además un 5xx que "ni 401 ni 403" dejaría pasar.
  Los dos 404 dependen de que la existencia se compruebe antes que la política, y eso ya lo congelan
  `tests/test_user_access_policy.py::test_delete_nonexistent_cedula_returns_404_before_403` y
  `::test_patch_nonexistent_cedula_returns_404_before_403`. Con `.get(...)`, una ruta sin entrada da `None`: una ruta
  `"user"` nueva falla hasta que se anota su código, y una ruta admin mal etiquetada falla con `403 == None`.
- **Tests (RED primero):** procedimiento común, copiando `tests/test_route_guards.py` (y `tests/test_audit.py` tal como
  queda tras la fase C). Mutantes propios:

  | Mutante | Archivo de la copia | Edición exacta (original → sustituto) | Resultado |
  |---|---|---|---|
  | M12 | `tests/test_route_guards.py` | `    ProtectedRoute("GET", "/usuarios/", "admin"),` → `    ProtectedRoute("GET", "/usuarios/", "user"),` | 1 failed, 322 passed: `test_user_route_lets_tourist_through[GET /usuarios/]` |
  | M13 (recíproco, declarado) | `tests/test_route_guards.py` | `    ProtectedRoute("GET", "/usuarios/mi-perfil", "user"),` → `    ProtectedRoute("GET", "/usuarios/mi-perfil", "admin"),` | 1 failed, 322 passed: `test_admin_route_rejects_tourist[GET /usuarios/mi-perfil]` (lo mata la fase C, no esta) |
  | M14 | `app/api/routers/user.py` | `self_service_router = APIRouter(dependencies=[Depends(get_current_user)])` → `self_service_router = APIRouter(dependencies=[Depends(get_current_admin_user)])` | 18 failed, 305 passed: los 3 casos nuevos y 15 tests que ya existían (`tests/test_auth.py` 2, `tests/test_token_failure_paths.py` 1, `tests/test_user_access_policy.py` 2, `tests/test_user_response.py` 10) |

  Sin mutante, `323 passed`.
- **Criterio de aceptación:** las cifras anteriores, `pytest tests/test_route_guards.py -q` → `35 passed`, y la fila D de la
  compuerta.
- **Fuera de alcance de esta fase:** `ProtectedRoute` y la tabla (aprobadas en A); aserciones sobre el cuerpo de las
  respuestas de usuario (ya las congelan `tests/test_auth.py` y `tests/test_user_response.py`); `tests/test_audit.py`.
- **Commit:**
  ```text
  test(guards): check the "user" label by letting a tourist through

  The inventory test proves that every route sits in a table, not that
  its guard label is right. An admin route labeled "user" by mistake
  would drop out of ADMIN_ROUTES, lose its tourist case, and nothing
  would notice. One parametrized test now sends a tourist to each
  "user" route and expects the handler's own code (200 for the
  profile, 404 for a cedula that names no account), so a mislabeled
  admin route answers 403 and fails.

  The opposite mistake, a user route labeled "admin", already fails
  test_admin_route_rejects_tourist. Requested by E0 of the BE-39 plan.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz del repo, tras la fase D. Las cifras cuentan el texto literal que dicta este plan (docstrings y comentarios
de `tests/test_route_guards.py` incluidos).

```bash
# 1. Ni app/ ni alembic/ ni ningún conftest cambian (0 líneas)
git diff --name-only 9ecc176 HEAD -- app alembic conftest.py tests/conftest.py
# 2. En tests/ cambian exactamente estos dos archivos: tests/test_audit.py y tests/test_route_guards.py
git diff --name-only 9ecc176 HEAD -- tests
# 3. 17 filas en la tabla; 14 admin; 3 user
grep -c '^    ProtectedRoute("' tests/test_route_guards.py
grep -cE '^    ProtectedRoute\(".*", "admin"' tests/test_route_guards.py
grep -cE '^    ProtectedRoute\(".*", "user"' tests/test_route_guards.py
# 4. 35 casos (1 inventario + 17 sin token + 14 turista en admin + 3 turista en usuario), todos verdes
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider      # 35 passed
# 5. La cabecera se afirma dos veces (presente en 401, ausente en 403): 2
grep -c "www-authenticate" tests/test_route_guards.py
# 6. Aserciones 401/403 en toda la suite: 30 (30 − test_audit.py:58,144 + 2 nuevas); 0 en test_audit.py
grep -rnE "status_code == 40[13]" tests --include=*.py | wc -l
grep -cE "status_code == 40[13]" tests/test_audit.py
# 7. Patrón 1 de la verificación: 0 en test_services.py (decisión 5); 4 en el archivo nuevo
grep -rnE "UserRole\.tourist|status_code == 40[13]" tests/test_services.py | wc -l
grep -nE "UserRole\.tourist|status_code == 40[13]" tests/test_route_guards.py | wc -l
# 8. Patrón 3: 3 líneas, todas a rutas públicas (test_auth.py:109, test_services.py:648, :668)
grep -rnE "client\.(get|post|put|patch|delete)\(\"/(auditoria|usuarios|servicios)/[^\"]*\"\)" tests --include=*.py
# 9. Los dos tests sustituidos ya no existen: 0
grep -rn "test_audit_trail_forbidden_for_tourist\|test_audit_trail_requires_authentication" tests --include=*.py | wc -l
# 10. app/ intacto: 15 y 1, como en la línea base
grep -rn "get_current_admin_user" app --include=*.py | wc -l
grep -rn "assert_is_admin_plus(current_user)" app --include=*.py | wc -l
# 11. Compuerta: exit 0, 612 passed, cobertura ≥ 96,29 %, 61 files formatted, mypy 56 source files, 4 kept
./venv/Scripts/python.exe scripts/check.py
```

12. Mutantes sobre la copia del estado final (procedimiento común): M1 6/317, M2 9/314, M3 12/311, M4+M5 2/321, M6 4/319,
    M7 13/310, M9 17/306, M10 1/322, M11 4/319 (los 4 de M11: el inventario, los dos casos de `admin/inactivos` y
    `test_inactive_column_returns_off_rule_package`), M12 1/322 (`test_user_route_lets_tourist_through[GET /usuarios/]`),
    M13 1/322 (`test_admin_route_rejects_tourist[GET /usuarios/mi-perfil]`), M14 18/305. Sin rojo: M4 323 (R1) y M9a 323
    (equivalente).

## Enmiendas aprobadas

### E0 — 11 nov 2026, 12:32 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «sobre la fase D, va porque va. tiene mi visto bueno […] dicho eso, sí a todo». Y a las 12:25,
sobre el límite que motiva la fase D: «no anotarlo al cierre, dejarlo corregido de una vez […] un ítem saldado no debería
dejar 3 más por saldar a menos que no sea buena idea corregir sus hallazgos emergentes».

**Plan aprobado: fases A → B → C como están escritas, más una fase D nueva.** La tabla de compuerta, los mutantes, los
commits y las cifras de A, B y C no cambian.

1. **P2:** tres fases (A, B, C) como propone el plan; no se funden B y C.
2. **P1:** sí, la regla va a AGENTS §3 ("una ruta nueva se registra en `PROTECTED_ROUTES`, con su guard, o en
   `PUBLIC_ROUTES` de `tests/test_route_guards.py`; si no, el test de inventario falla"). La escribe David en un commit
   de documentos propio, después de la última auditoría y antes de `/pr`. Ninguna fase edita `AGENTS.md`. R4 queda
   resuelto así.
3. **Fase D nueva: la etiqueta `guard` de la tabla se comprueba.** Límite hallado por la sesión Mentor al revisar el
   plan: el inventario comprueba que cada ruta esté en una tabla, no que su etiqueta sea la correcta. Una ruta admin
   anotada por error como `"user"` no entra en `ADMIN_ROUTES`, se queda sin su caso de 403 y ningún test lo nota.
   **Lo que la fase D debe conseguir (el planificador dicta el código y lo mide; lo de abajo es el requisito, no el
   dictado):** un test parametrizado sobre las rutas con `guard == "user"` (hoy 3): un turista con token válido
   (`persist_user`, `make_auth_headers`) **no** recibe 401 ni 403. Si una ruta admin lleva la etiqueta `"user"`, el
   turista recibe 403 y el test cae. Es comportamiento por HTTP, no inspección de dependencias (AGENTS §5). Solo
   `tests/test_route_guards.py`; sin tocar `app/`.
   - **Dato a medir antes de dictar** (la verificación lo midió con un turista: `mi-perfil` 200; `DELETE`/`PATCH` de una
     cédula inexistente 404/422): qué responde hoy cada una de las tres con `_PATH_PARAMS` y el cuerpo de la tabla. Si
     el plan puede afirmar el código exacto por ruta sin leer texto, mejor que "ni 401 ni 403"; lo decide el
     planificador con la medición.
   - **Mutante propio (sobre la tabla, en la copia):** cambiar la etiqueta de una ruta admin a `"user"` (p. ej.
     `GET /usuarios/`) → el test nuevo cae en ese caso. Y el recíproco que ya cubre la fase C: una ruta de usuario
     etiquetada `"admin"` → cae `test_admin_route_rejects_tourist` en ese caso; el plan lo mide y lo declara.
4. **Lo que el planificador recalcula con esta enmienda, y nada más:** la sección de la fase D (archivos, cambios
   exactos, RED con su mutante, criterio de aceptación, commit); la fila D de la tabla de compuerta; los pasos de la
   Verificación final que cambian de cifra (casos de `tests/test_route_guards.py`, total de la suite, patrones que
   cuenten líneas del archivo) y el paso 12 con el mutante nuevo; `progress.json` con `Fase_D` (`current_target` sigue
   en `Fase_A`); el Resumen para aprobación, si su cifra final cambia.
5. **Residuales tras E0:** R1 (M4 sola) y R2 (`guard="superadmin"`) son notas para BE-40, que ya tiene fila; R3 es una
   nota para BE-42. Ninguno crea fila nueva. R4 resuelto por el punto 2.

### E1 — 11 nov 2026, 12:55 (David, sesión Mentor)

Texto literal de David: «sí, ve y deja el plan listo para implementar».

**Fase D aprobada como la escribió el planificador** (E0, punto 3): `USER_ROUTES`, `_TOURIST_PAST_USER_GUARD` con el
código exacto por ruta (200, 404, 404) y `test_user_route_lets_tourist_through`; mutantes M12, M13 y M14; meta 612 passed.
Sin cambios en A, B y C. Límite aceptado: la fase D afirma solo el código de estado; los cuerpos de esas respuestas ya
los congelan `tests/test_auth.py` y `tests/test_user_response.py`. `current_target` sigue en `Fase_A`.

## Residuales

- **R1 — M4 sola sobrevive hasta BE-40** (adenda, decisión 2). Evidencia: el estado C bajo M4 da `320 passed`, porque el
  re-chequeo de `app/services/audit_service.py:65` responde el mismo 403. Destino: fila BE-40. *Sugerencia de texto:* "La
  verificación final de BE-40 incluye M4 (`audit.py:8` → `APIRouter()`): debe caer
  `tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]`". Lo anota la sesión Mentor en el cierre.
- **R2 — El guard de superadmin de BE-40 amplía la tabla.** Cuando `POST /usuarios/admin` tenga guard de superadmin, la fila
  pasa a `guard="superadmin"` (amplía el `Literal`) y necesita un caso "admin → 403". Hoy no puede escribirse: el 403 de un
  admin lo da la política (M8 de A2). Destino: plan de BE-40.
- **R3 — BE-42 (scope) y estos tests.** Los tokens salen de `make_auth_headers` → `make_token`. Cuando BE-42 exija
  `scope=access`, basta con actualizar `make_token`. Esta tabla le sirve a BE-42 para su caso "token de verificación como
  bearer → 401" en las 17 rutas, si su plan lo quiere. Destino: plan de BE-42.
- **R4 — La regla, escrita.** "Una ruta nueva se registra en `PROTECTED_ROUTES` o `PUBLIC_ROUTES` de
  `tests/test_route_guards.py`" es una regla para el código futuro, del tipo de `_DOMAIN_ERROR_STATUS` en AGENTS §3. Este plan
  no edita `AGENTS.md`. Destino: PR humano (decisión abierta P1).

## Referencias

- pytest · 9.0.2 · `parametrize(ids=callable)` llama a la función con cada valor y usa lo que devuelve como id ·
  https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-parametrize
- httpx · 0.28.1 · `AsyncClient.request(method, url, json=…, headers=…)`; `.get`/`.delete` no admiten `json`, `.request` sí ·
  https://www.python-httpx.org/async/ · https://www.python-httpx.org/compatibility/
- Starlette · 1.3.1 · `Route.methods` añade `HEAD` a todo `GET` (fuente instalada `starlette/routing.py:229-234`) ·
  https://www.starlette.io/routing/
- FastAPI · 0.135.1 · `OAuth2PasswordBearer(auto_error=False)` devuelve `None` sin cabecera (fuente `fastapi/security/oauth2.py:536-543`) ·
  https://fastapi.tiangolo.com/reference/security/#fastapi.security.OAuth2PasswordBearer
- PyJWT · 2.12.1 · `jwt.decode(None, …)` → `DecodeError` (`jwt/api_jws.py:298-299`), subclase de `InvalidTokenError` ·
  https://pyjwt.readthedocs.io/en/stable/api.html

## Decisiones abiertas para David

- **P1 — ¿Regla en AGENTS?** Propuesta: una línea en AGENTS §3, en PR humano al cerrar, como la de ADR-0013: "Una ruta nueva
  se registra en `PROTECTED_ROUTES` (con su guard) o en `PUBLIC_ROUTES` de `tests/test_route_guards.py`; si no, el inventario
  falla". La alternativa es confiar en el mensaje del test que falla. Sin ADR en ningún caso: el inventario solo hace cumplir
  el punto 4 de ADR-0012, no decide nada nuevo.
- **P2 — Tres fases o dos.** El plan separa B (M9) y C (M1–M7) para que cada auditoría contraste una sola familia de mutantes.
  Fundirlas en una deja 2 fases y 2 commits, con la misma cifra final (609).

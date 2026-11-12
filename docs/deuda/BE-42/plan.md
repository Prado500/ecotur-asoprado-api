# PLAN — BE-42: Exigir el `scope` de acceso en `get_current_user`

> Fuente: `docs/deuda/BE-42/verificacion.md` (confirmada; adenda de cuatro decisiones de David, 12 nov, 15:21, `9028ead`).
> Base: `e116c3a` (`app/`, `tests/`, `alembic/` y `conftest.py` iguales a `deb0b1e`: `git diff --name-only deb0b1e e116c3a --
> app tests alembic conftest.py` vacío). Estado: **aprobado por David el 12 nov 2026 con E0 (16:37): tres fases, A → C; P1–P5 resueltas en "Enmiendas aprobadas", al final.** Las cifras de este plan (tests, cobertura,
> mutantes y conteos de grep) se midieron el 12 nov sobre copias desechables de `e116c3a` en el scratchpad, con el texto
> exacto que dicta el plan.

## Resumen para aprobación

En tres fases, `get_current_user` deja de aceptar como sesión un token que no sea de acceso. (A) El valor
`"email_verification"`, hoy escrito dos veces, pasa a una constante `EMAIL_VERIFICATION_SCOPE`; no cambia ningún
comportamiento. (B) `create_access_token` firma siempre `scope="access"` (`ACCESS_TOKEN_SCOPE`), aunque el llamador pida
otro. Los tests se ajustan a ese cambio: `make_token` pierde `extra_claims`, una fábrica nueva `sign_claims` firma los
tokens que la app nunca emite y el login comprueba el `scope`. (C) `get_current_user` exige ese `scope` y responde con el
mismo 401 de hoy. Un token de verificación de un superadmin activo recibe 401 en las 17 rutas protegidas; hoy pasa la
autenticación en todas. La suite pasa de 618 a 638 tests y la cobertura de 96,81 % a 96,82 %.
**Riesgo principal:** al desplegar, los tokens de acceso vivos no llevan `scope` y reciben 401. Afecta a quien tenga una
sesión abierta en ese momento, como máximo 30 minutos, y se declara como `BREAKING CHANGE` en el commit de la fase C y
en el PR. **No se toca:** los guards de admin y superadmin, los alias, los routers, la política, la lógica de
`verify_email_account` (solo cambia el literal por la constante), el carácter de un solo uso del enlace (BE-50) ni
`activate_user`. **No hace falta ADR nuevo:** el patrón ya existe en `verify_email_account` y BE-42 lo aplica en el otro
sentido (ver "Decisión sobre el ADR").

## Objetivo y decisiones bloqueadas

Objetivo: solo un token de acceso abre una ruta protegida. Un token de verificación de correo, firmado con la misma
clave, o un token sin `scope`, recibe el 401 de un token inválido. Quitar esa comprobación pone la suite en rojo.

1. **El `scope` lo pone `create_access_token`, siempre** (adenda, punto 1). Se escribe en el `update` final, después de
   copiar `data`, así que sustituye a cualquier `scope` que traiga el llamador.
2. **`get_current_user` responde con la misma `credentials_exception`**: 401, `WWW-Authenticate: Bearer` y el mismo
   `detail` que un token corrupto (adenda, punto 1). La condición sigue la forma de `verify_email_account`:
   `if email is None or scope != ACCESS_TOKEN_SCOPE:`.
3. **Dos constantes en `app/core/security.py`:** `ACCESS_TOKEN_SCOPE = "access"` y
   `EMAIL_VERIFICATION_SCOPE = "email_verification"`. Las usan los dos emisores y los dos verificadores. Los valores no
   cambian (adenda, punto 2).
4. **Regla de los tests: la constante para construir, el literal para afirmar.** Un test que construye un token usa la
   constante, porque así construye lo que la app llama así. Un test que afirma lo que la app emite compara con el
   literal (`"access"`, `"email_verification"`), porque fija el valor que viaja en tokens y enlaces ya emitidos. Medido:
   los mutantes MEV y MAV, que cambian el valor de la constante, tumban esos tests.
5. **Tests de rechazo de la adenda (punto 3):** 17 casos "token de verificación de un superadmin activo → 401" sobre
   `PROTECTED_ROUTES`; "token sin `scope` → 401"; `scope` en los claims del login (dos tests). Los mutantes MSC y MA se
   miden y se declaran.
6. **BE-42 no toca** los docstrings de un solo uso (`app/core/security.py:84`, `app/services/user_service.py:37`) ni
   `activate_user` (adenda, punto 4; BE-50).
7. **Compuerta** `./venv/Scripts/python.exe scripts/check.py` completa y en verde al cerrar cada fase. La cobertura nunca
   baja de 96,81 %.

## Análisis del redactor

**Qué cambia y por qué.** La protección es asimétrica: `verify_email_account` (`user_service.py:137`) rechaza un token de
acceso, pero `get_current_user` (`dependencies.py:120-123`) solo lee `sub`. Medido en la copia: con el token de
verificación de un superadmin activo, las 17 rutas responden 200, 400, 404 o 422, y ninguna 401. En las tres rutas de
usuario el impacto es real hoy, con el enlace del correo de un turista: `GET /usuarios/mi-perfil` responde 200. El
arreglo copia el patrón que ya existe en `verify_email_account`. El emisor fija su `scope` y el lector exige el suyo.

**Orden y dependencias: A → B → C.**
- A es la más pequeña (2 archivos) y no cambia comportamiento: deja la constante a la que B añade la segunda.
- B va antes que C. Si `get_current_user` exigiera el `scope` antes de que los tokens lo llevasen, todo token de
  `make_token` daría 401. Medido con MA sobre el estado final: 102 tests caen. Entre B y C los tokens llevan un claim que
  nadie lee todavía, así que ninguna respuesta HTTP cambia.
- C usa `sign_claims`, que crea B.
- `app/core/security.py` se toca en A y en B, en bloques distintos.

**Consecuencias del punto 1 de la adenda, resueltas y medidas.**
- `test_verify_email_expired_token_…` (`tests/test_user_service.py:280-293`): con el `scope` impuesto, `make_token` ya no
  sabe fabricar un token de verificación caducado. Lo fabrica `sign_claims`, una fábrica nueva de `tests/conftest.py`
  (AGENTS §5: fábricas centralizadas, sin tokens a mano en cada test) que firma los claims tal cual con la clave de la
  app. No se amplía la API de producción: `create_verification_token` no recibe una duración solo para un test. El test
  añade `assert type(exc_info.value.__cause__) is jwt.ExpiredSignatureError`, la forma que ya usa
  `tests/test_token_failure_paths.py:265`. Así demuestra que el rechazo viene de la caducidad, y no de la firma ni del
  `scope`.
- `test_verify_email_wrong_scope_…` (`:296-307`): `extra_claims={"scope": "access"}` sobra. Pasa a
  `make_token(make_user(...))`, que es el token de login real, y el test fija "un token de login no es un enlace". El
  mutante MV, que quita el chequeo de `scope` de `verify_email_account`, lo tumba en la base, en A, en B y en C.
- `make_token` pierde `extra_claims`. Sus dos únicos usos eran los dos tests anteriores; mantener un parámetro sin uso
  sería generalidad especulativa (AGENTS §3). El docstring deja de prometer que puede sobrescribir un `scope` (decisión
  P2).
- **Rincón 2, demostrado y no supuesto.** Los tres tests de `tests/test_token_failure_paths.py:136-166` no cambian. Con
  la opción (a), sus tokens llevan `scope` y llegan a la rama que nombran. Medido sobre el estado final:
  - MSUB (quitar el chequeo de `sub`) tumba `test_token_without_subject_returns_401`: `TokenData(email=None)` lanza.
  - MU (no rechazar al usuario inexistente) tumba `test_corrupt_token_gets_the_same_detail_as_an_unknown_user` y
    `test_token_for_unknown_user_returns_401`, y también `…_soft_deleted_active_user_…`.
  - Contrafactual: con MA (el `scope` puesto fuera de `create_access_token`, es decir, la opción (b)), MA+MSUB y MA+MU dan
    `102 failed` y esos tres tests **siguen en verde**. Es el "test theater" que la opción (a) evita.

**Tests que congelan comportamiento.**
- `tests/test_route_guards.py`: 46 casos, todos con `make_auth_headers`. Siguen verdes en B y C porque sus tokens llevan
  el `scope` desde B.
- `tests/test_token_failure_paths.py`: 18 tests, incluidos `_resign`, que conserva el `scope` del token original, y los
  4 tokens firmados con `create_access_token(data=…)`.
- `tests/test_auth.py:91-114`: verificación de correo por HTTP.
- `tests/test_user_service.py:107-111`: `scope` del registro, con literal.

**Tests nuevos más allá de la adenda (decisión P4).**
- `test_verify_email_rejects_access_token_whose_data_names_the_verification_scope` (B) fija que el `scope` se
  **impone**. Sin él, el mutante MD (`data.get("scope", ACCESS_TOKEN_SCOPE)`) sobrevive a toda la suite.
- `test_verification_token_gets_the_same_detail_as_a_corrupt_token` (C) fija que el cliente no distingue qué falló
  (adenda, punto 1).

**Riesgos.**
1. Despliegue: los tokens vivos reciben 401 durante 30 minutos como máximo (adenda, punto 5). El cliente Flutter no
   maneja el 401 (FE-01) y verá lo mismo que con una sesión vencida.
2. Que `sign_claims` fabrique tokens inválidos por otra razón y produzca "test theater". Lo cubren dos cosas: MSC tumba
   `test_access_token_without_scope_returns_401` (ese token, sin la comprobación de `scope`, abre la ruta: medido) y la
   aserción de `__cause__` en el test de caducidad.
3. Orden de imports: ruff (isort, `order-by-type`) pone las constantes antes que las funciones. El plan dicta ese orden.

**Qué NO se toca.** `get_current_admin_user`, `get_current_superadmin_user` y los alias (`dependencies.py:144-193`):
heredan el arreglo. Tampoco se tocan los routers, `UserAccessPolicy`, la lógica de `verify_email_account`,
`activate_user` y `user_repository.py`, los docstrings de un solo uso (BE-50), `TokenData`, `app/core/config.py` (no hay
ajuste nuevo), los 4 tokens de `create_access_token(data=…)` ni `_expired_token`/`_resign` de
`tests/test_token_failure_paths.py`, `alembic/`, `AGENTS.md` ni los documentos vivos (los cierra la sesión Mentor).

**Decisión sobre el ADR: no hace falta uno nuevo.**
- No hay patrón nuevo: el par "emisor fija `scope`, lector lo exige" ya existe en `create_verification_token` y
  `verify_email_account`. BE-42 lo completa en el otro sentido, como leyó la sesión Mentor.
- No hay módulo nuevo.
- El contrato HTTP no cambia: los códigos, el cuerpo y la cabecera de un token inválido son los de hoy. El único efecto
  visible es la invalidación única de los tokens vivos al desplegar. Es un efecto del despliegue, no una decisión que
  perdure, y se declara en el `BREAKING CHANGE` y en el PR (adenda, punto 5).
- ADR-0012 no cambia: los guards siguen decidiendo el rol y la política el dato.
- ADR-0003 no aplica: `get_current_user` está en la capa HTTP y ya lanza `HTTPException`.
- Alternativa descartada sin ADR: los scopes OAuth2 de FastAPI (`Security`/`SecurityScopes`). Sirven para permisos
  dentro de un token de acceso, no para distinguir tipos de token, y obligarían a tocar guards y routers.

## Regla de alcance

- **Sí:** 3 archivos de `app/` (`core/security.py`, `api/dependencies.py`, `services/user_service.py`) y 5 de `tests/`
  (`conftest.py`, `test_auth.py`, `test_user_service.py`, `test_route_guards.py`, `test_token_failure_paths.py`), con el
  texto exacto de cada fase.
- **No:** cualquier otro archivo, docstring o comentario fuera de los que dicta cada fase, y los nombres de handler en
  español (P2 del backlog).
- Un hallazgo nuevo va a Residuales, nunca "de paso".

## Fases

**Procedimiento de mutantes (común, el de BE-40).**
1. Crear en el scratchpad un directorio nuevo y vacío. No se reutiliza ni se borra (`rm -rf` está denegado).
2. Ejecutar `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>`, después del commit de la fase.
3. Aplicar la edición del mutante: una sola línea, con la cadena exacta de la tabla.
4. Desde `<dir>`, ejecutar
   `C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
5. Pegar en el handoff la última línea y los `FAILED`.

| Mutante | Archivo | Edición exacta (original → sustituto) |
|---|---|---|
| MSC | `app/api/dependencies.py` | `        if email is None or scope != ACCESS_TOKEN_SCOPE:` → `        if email is None:` |
| MSUB | `app/api/dependencies.py` | `        if email is None or scope != ACCESS_TOKEN_SCOPE:` → `        if scope != ACCESS_TOKEN_SCOPE:` |
| MU | `app/api/dependencies.py` | `    if user is None or not user.is_active:` → `    if user is not None and not user.is_active:` |
| MA | `app/core/security.py` | `    to_encode.update({"scope": ACCESS_TOKEN_SCOPE, "exp": expire})` → `    to_encode.update({"exp": expire})` |
| MD | `app/core/security.py` | la misma línea → `    to_encode.update({"scope": data.get("scope", ACCESS_TOKEN_SCOPE), "exp": expire})` |
| MV | `app/services/user_service.py` | `        if email is None or scope != EMAIL_VERIFICATION_SCOPE:` → `        if email is None:` (en la base: `!= "email_verification":`) |
| MEV | `app/core/security.py` | `EMAIL_VERIFICATION_SCOPE = "email_verification"` → `EMAIL_VERIFICATION_SCOPE = "verification"` |
| MAV | `app/core/security.py` | `ACCESS_TOKEN_SCOPE = "access"` → `ACCESS_TOKEN_SCOPE = "bearer"` |

Al cerrar cada fase, la compuerta debe dar: exit 0, `Compuerta superada.`, `61 files already formatted`,
`All checks passed!`, `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.` y `8 warnings`.

| Fin de | pytest | Cobertura (`TOTAL` stmts) | Suite de la copia (sin `test_check*`) |
|---|---|---|---|
| Base | 618 passed | 96,81 % (961) | 329 passed |
| A | 618 passed | 96,81 % (962) | 329 passed |
| B | 619 passed | 96,82 % (963) | 330 passed |
| C | 638 passed | 96,82 % (965) | 349 passed |

Al usar cada mensaje de commit, el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra.

### Fase A — Una constante para el `scope` de verificación (la más pequeña)

- **Archivos (2):** `app/core/security.py`, `app/services/user_service.py`. Dominio: tokens (auth).
- **Cambios exactos:**
  1. `security.py`: entre el bloque `"""` / `    TOKEN FACTORY` / `"""` (l.45-47) y `def create_access_token`, insertar
     estas tres líneas. El resultado queda así: el `"""` de cierre, una línea en blanco, las tres líneas, dos líneas en
     blanco y `def create_access_token`.
     ```python
     # Value of the scope claim of each token kind. The values travel in tokens already issued:
     # changing one invalidates them.
     EMAIL_VERIFICATION_SCOPE = "email_verification"
     ```
     En `create_verification_token` (l.99):
     `to_encode = {"sub": email, "scope": EMAIL_VERIFICATION_SCOPE, "exp": expire}`.
  2. `user_service.py`: en el import de `app.core.security`, añadir `    EMAIL_VERIFICATION_SCOPE,` como **primer**
     nombre, antes de `create_access_token,`. En `verify_email_account` (l.137):
     `if email is None or scope != EMAIL_VERIFICATION_SCOPE:`. Nada más cambia en el método.
- **Tests (RED primero):** no hay RED posible: es un refactor sin cambio de comportamiento, y no se añade ningún test.
  Lo vigilan los tests existentes y dos mutantes medidos:
  - MV en la base (forma literal) da `1 failed, 328 passed`
    (`test_verify_email_wrong_scope_raises_invalid_verification_token`). Tras A, MV da el mismo `1 failed, 328 passed`.
  - MEV tras A da `1 failed, 328 passed` (`test_register_tourist_returns_registration_result`, que afirma el literal en
    `tests/test_user_service.py:111`).
- **Criterio de aceptación:**
  - Compuerta como la fila A (618 passed, 96,81 %) y MV y MEV con los resultados de arriba.
  - `git show --numstat --format= <sha de A>` da `5	1	app/core/security.py` y `2	1	app/services/user_service.py`.
  - `git grep -n '"email_verification"' -- app | wc -l` → `1`.
- **Fuera de alcance:** `ACCESS_TOKEN_SCOPE` (fase B), `create_access_token`, `get_current_user`, los tests y los
  docstrings de un solo uso (BE-50).
- **Commit:**
  ```
  refactor(auth): name the email verification scope in one constant

  The scope value "email_verification" was written twice, in two
  layers that must agree: create_verification_token signs it and
  verify_email_account checks it (BE-42, addendum point 2).

  - app/core/security.py: EMAIL_VERIFICATION_SCOPE, next to the token
    factories; create_verification_token signs it.
  - app/services/user_service.py: verify_email_account compares the
    claim against it; nothing else in the method changes.

  The value does not change: it travels in verification links already
  sent, and the registration test still asserts the literal.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — Todo token de acceso lleva `scope=access`

- **Archivos (4):** `app/core/security.py`, `tests/conftest.py`, `tests/test_auth.py`, `tests/test_user_service.py`.
  Dominio: tokens (auth).
- **Cambios exactos:**
  1. `security.py`:
     - Entre la segunda línea de comentario y `EMAIL_VERIFICATION_SCOPE = …`, añadir `ACCESS_TOKEN_SCOPE = "access"`.
     - En el docstring de `create_access_token`, entre el párrafo que acaba en `…of the application settings.` y
       `Args:`, añadir este párrafo con una línea en blanco detrás:
       ```
           The scope claim is always ACCESS_TOKEN_SCOPE, over any scope in data: no caller
           chooses it, as create_verification_token fixes its own.
       ```
     - La línea de Args pasa a
       `        data (dict): Claims to sign; copied, never mutated. A scope in it is replaced.`
     - `to_encode.update({"exp": expire})` (l.74) pasa a
       `to_encode.update({"scope": ACCESS_TOKEN_SCOPE, "exp": expire})`.
  2. `tests/conftest.py`:
     - Imports: `from datetime import UTC, datetime, timedelta`; `import jwt` antes de `import pytest`;
       `from app.core.config import get_settings` antes de `from app.core.security import create_access_token`.
     - En el docstring de `make_token`, las líneas `the user's email and role as claims; expires_delta overrides the`
       … `so a test can add or override one (e.g. a scope) without signing by hand.` pasan a:
       ```
               the user's email and role as claims, plus the access scope that
               create_access_token always sets; expires_delta overrides the
               default lifespan, and a negative one yields an already expired token.
               A token with another scope, or with none, comes from sign_claims.
       ```
     - La función interna pasa a
       `    def _make_token(user: User, *, expires_delta: timedelta | None = None) -> str:`, con su línea `claims: …`
       y su `return …` actuales. Se borra `claims.update(extra_claims or {})`.
     - Entre `make_token` y `make_auth_headers`, con dos líneas en blanco antes y después, añadir:
       ```python
       @pytest.fixture
       def sign_claims():
           """
           Centralized factory that signs the given claims as they are, with the app's key.

           For the tokens the producers of app/core/security.py never sign: an access
           token with no scope, as they were signed before BE-42, or an expired
           verification token. Only exp is added; every other claim is the caller's.

           Returns:
               Callable[..., str]: Factory taking the claims and a keyword-only
               expires_delta (negative for an already expired token) and producing
               a JWT signed with the settings' key and algorithm.
           """

           def _sign_claims(claims: dict[str, Any], *, expires_delta: timedelta) -> str:
               settings = get_settings()
               payload = {**claims, "exp": datetime.now(UTC) + expires_delta}
               return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)

           return _sign_claims
       ```
  3. `tests/test_auth.py`: en `test_login_active_user_returns_bearer_token`, tras `assert claims["role"] == "tourist"`,
     añadir `    assert claims["scope"] == "access"`.
  4. `tests/test_user_service.py`:
     - El import de `app.core.security` pasa a la forma partida con `EMAIL_VERIFICATION_SCOPE,`, `create_access_token,`,
       `create_verification_token,` y `get_password_hash,`, en ese orden.
     - En `test_authenticate_active_user_returns_bearer_token`, tras `assert claims["role"] == user.role.value`, añadir
       `    assert claims["scope"] == "access"`.
     - `test_verify_email_expired_token_raises_invalid_verification_token`:
       - Fixtures: `user_repo, user_service, sign_claims`.
       - Docstring:
         `"""Unhappy path: an expired verification token is rejected before any activation attempt."""`.
       - Token:
         ```python
             expired_token = sign_claims(
                 {"sub": "turista@example.com", "scope": EMAIL_VERIFICATION_SCOPE},
                 expires_delta=timedelta(minutes=-1),
             )
         ```
       - `with pytest.raises(InvalidVerificationTokenError) as exc_info:`.
       - Antes de `user_repo.activate_user.assert_not_awaited()`, añadir
         `    assert type(exc_info.value.__cause__) is jwt.ExpiredSignatureError`.
     - `test_verify_email_wrong_scope_raises_invalid_verification_token`:
       - Docstring:
         `"""Edge case: an access token, valid in every other way, is not a verification link."""`.
       - Token: `    wrong_scope_token = make_token(make_user(email="turista@example.com"))`.
     - Antes de `test_verify_email_missing_user_raises_not_found`, añadir:
       ```python
       async def test_verify_email_rejects_access_token_whose_data_names_the_verification_scope(
           user_repo, user_service
       ):
           """Edge case: create_access_token replaces a scope in its data, so no caller forges a link."""
           forged_token = create_access_token(
               data={"sub": "turista@example.com", "scope": EMAIL_VERIFICATION_SCOPE}
           )

           with pytest.raises(InvalidVerificationTokenError):
               await user_service.verify_email_account(forged_token)

           user_repo.activate_user.assert_not_awaited()
       ```
- **Tests (RED primero):**
  - Se escriben primero los cambios de los tres archivos de tests. Después se ejecuta
    `./venv/Scripts/python.exe -m pytest tests/test_auth.py tests/test_user_service.py -q -p no:cacheprovider -rf`
    **antes** de tocar `security.py`. Medido: `3 failed, 37 passed`.
    - `test_login_active_user_returns_bearer_token` (`KeyError: 'scope'`).
    - `test_authenticate_active_user_returns_bearer_token` (`KeyError: 'scope'`).
    - `test_verify_email_rejects_access_token_whose_data_names_the_verification_scope` (`DID NOT RAISE`).
  - Los dos tests reescritos (caducado y `scope` equivocado) están verdes antes y después.
  - Mutantes tras B:
    - MA: `3 failed, 327 passed` (los tres de arriba).
    - MD: `1 failed, 329 passed` (el de `…_data_names_the_verification_scope`).
    - MV: `2 failed, 328 passed` (`…_wrong_scope_…` y `…_data_names_the_verification_scope`).
- **Criterio de aceptación:**
  - Compuerta como la fila B (619 passed, 96,82 %) y mutantes con los resultados de arriba.
  - `git show --numstat --format= <sha de B>` da `6	2	app/core/security.py`, `30	11	tests/conftest.py`,
    `1	0	tests/test_auth.py` y `29	11	tests/test_user_service.py`.
  - `git grep -n "extra_claims" -- app tests | wc -l` → `0`.
- **Fuera de alcance:** `get_current_user` (fase C), `test_route_guards.py` y `test_token_failure_paths.py` (fase C),
  los 4 tokens de `create_access_token(data=…)` de `test_token_failure_paths.py`, `make_auth_headers` y
  `tests/test_user_service.py:107-111`, que ya afirma el literal.
- **Commit:**
  ```
  feat(auth): sign every access token with the access scope

  Access and verification tokens share the signing key, and only the
  verification token said what it was for. create_access_token now sets
  scope=access over anything its data carries, as create_verification_token
  fixes its own, so no caller chooses the scope of an access token
  (BE-42, addendum point 1). Nothing reads the claim yet: the next commit
  makes get_current_user require it.

  - app/core/security.py: ACCESS_TOKEN_SCOPE beside the verification
    scope; create_access_token sets it.
  - tests/conftest.py: make_token drops extra_claims, whose only use was
    choosing a scope; sign_claims signs claims as given, for the tokens
    the app never issues (no scope, expired verification).
  - tests/test_auth.py, tests/test_user_service.py: login claims include
    the access scope; the expired verification token comes from
    sign_claims and is rejected for its expiry; the wrong-scope test sends
    a plain access token; a new test shows that asking for the
    verification scope in data still yields no verification link.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — `get_current_user` exige el `scope` de acceso

- **Archivos (3):** `app/api/dependencies.py`, `tests/test_route_guards.py`, `tests/test_token_failure_paths.py`.
  Dominio: tokens (auth).
- **Cambios exactos:**
  1. `dependencies.py`:
     - Tras `from app.core.config import Settings, get_settings`, añadir
       `from app.core.security import ACCESS_TOKEN_SCOPE`.
     - En el docstring de `get_current_user`, entre el párrafo que acaba en `…overrides get_settings is honoured.` y
       `Args:`, añadir este párrafo con una línea en blanco detrás:
       ```
           Only an access token is a bearer: the scope claim must be ACCESS_TOKEN_SCOPE. An email
           verification token, signed with the same key, or a token with no scope gets the same 401
           as a corrupt one, as verify_email_account refuses an access token.
       ```
     - En `Raises:`, la línea `            subject, or names no active user.` pasa a
       `            subject, is not an access token, or names no active user.`.
     - `if email is None:` (l.122) pasa a dos líneas:
       ```python
               scope: str | None = payload.get("scope")
               if email is None or scope != ACCESS_TOKEN_SCOPE:
       ```
     - `credentials_exception`, los dos `except`, la búsqueda del usuario y todo lo que hay desde
       `get_current_admin_user` no cambian.
  2. `tests/test_route_guards.py`:
     - Antes de `from app.main import app`, añadir `from app.core.security import create_verification_token`.
     - Entre `test_protected_route_rejects_request_without_token` y el `@pytest.mark.parametrize` de
       `test_admin_route_rejects_tourist`, añadir:
       ```python
       @pytest.mark.parametrize("route", PROTECTED_ROUTES, ids=_route_id)
       async def test_protected_route_rejects_verification_token_as_bearer(
           client, persist_user, route: ProtectedRoute
       ) -> None:
           """An email verification token gets 401 from every protected route, Bearer challenge included.

           It belongs to an active superadmin, who passes every role guard: only the token's scope
           can stop the request (BE-42).
           """
           superadmin = await persist_user(role=UserRole.superadmin)
           token = create_verification_token(superadmin.email)

           response = await client.request(
               route.method, _url(route), json=route.body, headers={"Authorization": f"Bearer {token}"}
           )

           assert response.status_code == 401
           assert response.headers["www-authenticate"] == "Bearer"
           body = response.json()
           assert set(body) == {"detail"}
           assert isinstance(body["detail"], str)
       ```
  3. `tests/test_token_failure_paths.py`:
     - Tras `MakeToken = Callable[..., str]`, añadir `SignClaims = Callable[..., str]`.
     - Entre `test_token_for_unknown_user_returns_401` y `test_token_for_inactive_user_returns_401`, añadir:
       ```python
       async def test_access_token_without_scope_returns_401(
           client: AsyncClient, persist_user: PersistUser, sign_claims: SignClaims
       ) -> None:
           """Unhappy path: a token like those signed before BE-42, with no scope, opens nothing.

           Same subject, role and lifespan as a login token, for an active user: only the missing
           scope stands between it and the route.
           """
           user = await persist_user()
           token = sign_claims(
               {"sub": user.email, "role": user.role.value}, expires_delta=timedelta(minutes=30)
           )

           response = await client.get(PROTECTED_ROUTE, headers=_bearer(token))

           _assert_bearer_401(response)


       async def test_verification_token_gets_the_same_detail_as_a_corrupt_token(
           client: AsyncClient, persist_user: PersistUser
       ) -> None:
           """Edge case: a verification token is answered like a corrupt one, text unread."""
           user = await persist_user()

           verification = await client.get(
               PROTECTED_ROUTE, headers=_bearer(create_verification_token(user.email))
           )
           corrupt = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))

           _assert_bearer_401(verification)
           assert verification.json()["detail"] == corrupt.json()["detail"]
       ```
- **Tests (RED primero):**
  - Se escriben primero los dos archivos de tests. Después se ejecuta
    `./venv/Scripts/python.exe -m pytest tests/test_route_guards.py tests/test_token_failure_paths.py -q -p no:cacheprovider -rf`
    **antes** de tocar `dependencies.py`. Medido: `19 failed, 64 passed`.
  - Los 17 casos de `test_protected_route_rejects_verification_token_as_bearer` responden así:
    - 200 (6): `GET /usuarios/`, `GET /usuarios/admin/eliminados`, `GET /servicios/admin/inactivos`,
      `GET /servicios/admin/eliminados`, `GET /auditoria/` y `GET /usuarios/mi-perfil`.
    - 404 (7): `PATCH /usuarios/{cedula}/recuperar`, `PUT /servicios/{service_id}`, `PATCH …/activar`,
      `PATCH …/desactivar`, `DELETE /servicios/{service_id}`, `DELETE /usuarios/{cedula}` y `PATCH /usuarios/{cedula}`.
    - 422 (3): `POST /usuarios/admin`, `POST /servicios/upload-images/` y `POST /servicios/`.
    - 400 (1): `PATCH /servicios/{service_id}/recuperar`.
  - Los otros dos fallos son `test_access_token_without_scope_returns_401` y
    `test_verification_token_gets_the_same_detail_as_a_corrupt_token`, los dos con `assert 200 == 401`.
  - Mutantes tras C:
    - MSC: `19 failed, 330 passed`. Caen los 17 casos de la tabla y los dos tests nuevos de `test_token_failure_paths.py`;
      es el "deben caer los dos primeros grupos" de la adenda.
    - MSUB: `1 failed, 348 passed` (`test_token_without_subject_returns_401`).
    - MU: `3 failed, 346 passed` (`test_corrupt_token_gets_the_same_detail_as_an_unknown_user`,
      `test_token_for_unknown_user_returns_401` y `test_token_for_soft_deleted_active_user_returns_401`).
    - MA: `102 failed, 247 passed`. Por archivo: `test_services.py` 29, `test_user_access_policy.py` 24,
      `test_route_guards.py` 18 (14 de turista, 1 de admin en la ruta de superadmin y 3 de usuario), `test_auth.py` 13,
      `test_user_response.py` 12, `test_audit.py` 3, `test_user_service.py` 2 y `test_token_failure_paths.py` 1.
    - MA+MSUB y MA+MU: `102 failed, 247 passed`, con los tres tests del rincón 2 en verde. Es el contrafactual del
      análisis.
    - MD: `1 failed, 348 passed`. MV: `2 failed, 347 passed`. MEV: `1 failed, 348 passed`.
    - MAV: `2 failed, 347 passed` (los dos tests de claims del login).
- **Criterio de aceptación:**
  - Compuerta como la fila C (638 passed, 96,82 %) y mutantes con los resultados de arriba.
  - `git show --numstat --format= <sha de C>` da `8	2	app/api/dependencies.py`, `24	0	tests/test_route_guards.py` y
    `34	0	tests/test_token_failure_paths.py`: ningún test existente cambia.
  - `./venv/Scripts/python.exe -m pytest tests/test_route_guards.py --collect-only -q -p no:cacheprovider` →
    `63 tests collected`.
- **Fuera de alcance:**
  - `get_current_admin_user`, `get_current_superadmin_user`, los alias, los routers y la política.
  - Distinguir en el `detail` un `scope` equivocado (adenda, punto 1).
  - Añadir filas a `PROTECTED_ROUTES` o a `PUBLIC_ROUTES`: no hay rutas nuevas.
  - `verify_email_account`, BE-50 y `TokenData.role` (Residuales).
- **Commit:**
  ```
  fix(auth)!: accept only access tokens as bearer

  get_current_user read the subject and never the scope, so an email
  verification token, signed with the same key and sent in a link, was a
  15-minute session for its account once active, with no password: enough
  to read the profile, change the email or delete the account.
  verify_email_account already refused access tokens; this closes the
  other direction (BE-42).

  - app/api/dependencies.py: get_current_user requires ACCESS_TOKEN_SCOPE
    and answers any other scope, or none, with the same 401 and Bearer
    challenge as a corrupt token. The admin and superadmin guards build on
    it and inherit the check unchanged.
  - tests/test_route_guards.py: an active superadmin's verification token
    gets 401 from all 17 protected routes.
  - tests/test_token_failure_paths.py: a token without scope gets 401, and
    a verification token gets the same detail as a corrupt one.

  BREAKING CHANGE: access tokens issued before this version carry no
  scope and get 401 from the moment it is deployed, even if unexpired.
  Whoever holds one signs in again; none is left 30 minutes after the
  deploy (access_token_expire_minutes).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Se ejecuta desde la raíz del repo, después de la fase C. Las cifras incluyen el texto literal que dicta este plan
(docstrings, comentarios y nombres de tests) y se midieron sobre la copia del estado C. Entre paréntesis va el valor de
hoy, cuando difiere.

```bash
# 1. Archivos tocados: 8 (3 de app/, 5 de tests/), con estas cifras exactas
git diff --numstat e116c3a HEAD -- app tests alembic conftest.py
#   8	2	app/api/dependencies.py
#   11	3	app/core/security.py
#   2	1	app/services/user_service.py
#   30	11	tests/conftest.py
#   1	0	tests/test_auth.py
#   24	0	tests/test_route_guards.py
#   34	0	tests/test_token_failure_paths.py
#   29	11	tests/test_user_service.py
# 2. Lo que no se toca: 0, 0 y 0
git diff --name-only e116c3a HEAD -- app/api/routers app/services/user_access_policy.py app/repositories app/schemas app/models app/core/config.py alembic conftest.py | wc -l   # 0
git diff e116c3a HEAD -- app/api/dependencies.py | grep -cE "^[-+].*(get_current_admin_user|get_current_superadmin_user|Dep = )"   # 0
git diff e116c3a HEAD -- app | grep -c "single-use"                                            # 0
# 3. Patrones de la verificación
git grep -c "scope" -- app/api/dependencies.py                                                 # app/api/dependencies.py:4 (hoy sin salida)
git grep -n -E "jwt\.decode\(" -- app | wc -l                                                  # 2
git grep -n -E "jwt\.encode\(" -- app | wc -l                                                  # 2
git grep -n -E "create_access_token\(|create_verification_token\(" -- app tests | wc -l        # 16 (hoy 13)
git grep -n -E '"scope"|scope=' -- app | wc -l                                                 # 4 (hoy 2)
git grep -n -E "create_access_token\(data=" -- tests | wc -l                                   # 5 (hoy 5; ver Residuales R1)
git grep -n -E "_bearer\(create_verification|verification.*bearer|bearer.*verification" -- tests | wc -l   # 3 (hoy 0)
git grep -n -E "Depends\(get_current_user\)" -- app/api/dependencies.py | wc -l                # 3
git grep -c 'ProtectedRoute("' -- tests/test_route_guards.py                                   # tests/test_route_guards.py:17
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py --collect-only -q -p no:cacheprovider   # 63 tests collected (hoy 46)
# 4. Constantes y literales en app/
git grep -n '"email_verification"' -- app | wc -l                                              # 1 (hoy 2)
git grep -n '"access"' -- app | wc -l                                                          # 1 (hoy 0)
git grep -n "ACCESS_TOKEN_SCOPE" -- app | wc -l                                                # 6
git grep -n "EMAIL_VERIFICATION_SCOPE" -- app tests | wc -l                                    # 7
# 5. Fábricas y aserciones
git grep -n "extra_claims" -- app tests | wc -l                                                # 0 (hoy 5)
git grep -n "sign_claims" -- tests | wc -l                                                     # 8
git grep -n 'claims\["scope"\] == "access"' -- tests | wc -l                                   # 2
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py tests/test_token_failure_paths.py -q -p no:cacheprovider   # 83 passed
# 6. Compuerta: exit 0; 638 passed; 96,82 % (≥ 96,81 %); 61 files; mypy 56 source files; 4 kept; 8 warnings
./venv/Scripts/python.exe scripts/check.py
```

7. Mutantes sobre la copia del estado final (procedimiento común), con los resultados de la fase C: MSC `19 failed`,
   MSUB `1`, MU `3`, MA `102`, MD `1`, MV `2`, MEV `1`, MAV `2`, y MA+MSUB y MA+MU `102` con los tres tests del rincón 2
   en verde. Si el auditor no puede crear la copia, lo declara como bloqueo y no da el mutante por medido.

## Residuales

- **R1: cita imprecisa en la verificación, sin deuda.** El patrón 6 (`create_access_token\(data=` en `tests`) dice "hoy:
  `test_token_failure_paths.py:44,140,150,162`". Hoy da 5 líneas, porque `tests/conftest.py:227` también coincide. La
  Verificación final usa el 5. Destino: ninguno; se apunta para el auditor.
- **R2: `TokenData.role` sin uso** (rincón 8 de la verificación; `app/schemas/token.py:23`). `get_current_user` solo
  pasa `email`. Destino sugerido: ninguno, salvo que David quiera una fila `Sale → B-FUTURO`. *Texto sugerido:*
  "`TokenData.role` no lo lee nadie: quitarlo, o usarlo si algún día el rol del token decide algo".
- **R3: BE-50 ya tiene fila** (`docs/backlog.md:97`, `Sale → B-FUTURO`). BE-42 no la toca: el enlace sigue siendo
  reutilizable durante 15 minutos, pero desde la fase C ya no abre una sesión.
- **R4: cierre de documentos (sesión Mentor, tras el merge).**
  - `docs/backlog.md`: BE-42 pasa a `Hecho (PR #N)`.
  - `PLAN.md` §2b: cierra `B-GUARD-TESTS` m2.
  - En el PR se declaran el `BREAKING CHANGE` de la fase C y los 30 minutos (adenda, punto 5).
  - Opcional: AGENTS §5 nombra como fábricas `make_user` y `auth_headers`; `sign_claims` se añade solo si David lo quiere.

## Referencias

- PyJWT · 2.12.1 (instalada; Context7 `/jpadilla/pyjwt`) · `jwt.decode` valida `exp` por dentro y lanza
  `ExpiredSignatureError` antes de que el código lea ningún claim. `jwt.encode` acepta `exp` como `datetime` UTC y lo
  convierte a entero. `exp` no es obligatorio salvo con `options={"require": …}`. Esto sostiene `sign_claims` y la
  aserción de `__cause__` · https://pyjwt.readthedocs.io/en/stable/usage.html#expiration-time-claim-exp
- FastAPI · 0.135.1 · los scopes OAuth2 (`Security`, `SecurityScopes`) son la alternativa descartada en "Decisión sobre
  el ADR" · https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/

## Decisiones abiertas para David

> **Cerradas el 12 nov a las 16:37: ver E0 en "Enmiendas aprobadas".** Ninguna espera respuesta.

- **P1: `fix(auth)!` con `BREAKING CHANGE` en la fase C.** El plan marca la ruptura porque un token que el servidor
  aceptaba ayer recibe 401 tras desplegar (adenda, punto 5). Precedente: BE-40 P2. La alternativa es `fix(auth):` sin
  `!` y declararlo solo en el PR, porque el efecto dura 30 minutos.
- **P2: quitar `extra_claims` de `make_token`.** La adenda pide corregir el docstring; el plan quita además el parámetro,
  que se queda sin usos. Alternativa: conservarlo y que el docstring diga que no puede cambiar el `scope`. Es un
  parámetro sin llamadores (AGENTS §3, YAGNI).
- **P3: `sign_claims` como fábrica de `tests/conftest.py`.** Hay dos alternativas:
  - `jwt.encode` a mano en cada uno de los dos tests (AGENTS §5 lo prohíbe).
  - Para el token caducado, sustituir `get_settings` con `verification_token_expire_minutes` negativo. Acopla el test al
    punto donde `security.py` lee la configuración y no sirve para el token sin `scope`.
- **P4: dos tests que la adenda no lista**: el del `scope` impuesto (fase B; sin él, MD sobrevive) y el del `detail`
  idéntico (fase C; fija "el cliente no distingue"). Si prefieres no añadirlos, la suite final queda en 636 y MD
  sobrevive.
- **P5: sin ADR nuevo** (ver "Decisión sobre el ADR"). Si quieres dejar escrito que el claim `scope` distingue los tipos
  de token, es un addendum tuyo a ADR-0012 (ADR-0009), no un ADR del planificador.

## Enmiendas aprobadas

### E0 — 12 nov 2026, 16:37 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «ok, sí a las 5».

**Plan aprobado: fases A → B → C como están escritas.** La tabla de compuerta, los mutantes, los commits y las cifras no
cambian. Contraste de la sesión Mentor contra el código, sin correcciones de dictado: existen las anclas que el plan usa
(`app/core/security.py:45-47` y `:74`, el import partido de `app/services/user_service.py:13-18`, el docstring de
`get_current_user`, los imports de `tests/conftest.py`, los helpers de `tests/test_token_failure_paths.py`); ningún
bloque de Python dictado pasa de 100 columnas (medido); las cuentas cuadran (618 → 619 → 638; 46 + 17 = 63 casos en
`tests/test_route_guards.py`). Las cifras de tests, cobertura y mutantes las repite el auditor.

1. **P1: `fix(auth)!` con `BREAKING CHANGE`** en la fase C, como dicta el plan (precedente: BE-40, E0.4).
2. **P2: `make_token` pierde `extra_claims`**, que se queda sin llamadores. Afina el punto 1 de la adenda, que solo pedía
   corregir el docstring.
3. **P3: `sign_claims` es una fábrica de `tests/conftest.py`.**
4. **P4: sí a los dos tests que la adenda no listaba** (el del `scope` impuesto, fase B, que mata a MD; el del `detail`
   idéntico al de un token corrupto, fase C).
5. **P5: sin ADR nuevo ni addendum.**

Precisión al encabezado del plan: la adenda de la verificación tiene cinco puntos, no cuatro (el quinto es el efecto
que el PR declara, que el plan recoge como `BREAKING CHANGE`). Pendiente fuera del plan, de David, antes de `/pr`: si
AGENTS §5 nombra `sign_claims` y corrige `auth_headers` por `make_auth_headers` (Residuales, R4).

`progress.json` no cambia (`current_target: Fase_A`).

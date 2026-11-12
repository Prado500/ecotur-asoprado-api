# Verificación — BE-42: `get_current_user` no comprueba el `scope` del token

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-42, l.89, con las notas de BE-39 R3 y BE-40 R4) + opcional 2 de la
auditoría de la fase D de A4 (`docs/deuda/A4/gaps.md:125`; destino fijado en `docs/deuda/A4/plan.md:652-653`)
**Fecha:** 2026-11-12

## Qué describe el ítem
`get_current_user` decodifica el JWT y solo lee `sub`; no mira `scope`. Un token de verificación de correo
(`scope=email_verification`, 15 min, viaja en un enlace) firmado con la misma clave se acepta como bearer del usuario
en cuanto la cuenta está activa, sin contraseña. Meta: los tokens de acceso llevan `scope=access` y `get_current_user`
lo exige; test "token de verificación como bearer → 401" con mutante; declarar que los tokens de acceso emitidos antes
del despliegue (30 min) dejan de valer. La auditoría de A4 lo puso en `dependencies.py:106-110`; con BE-40 el bloque
está ahora en `:119-123`.

## Evidencia en el código
Emisión (los dos únicos `jwt.encode` de `app/`):
- `app/core/security.py:50` — `def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:`;
  firma lo que recibe y solo añade `exp` (`:74` `to_encode.update({"exp": expire})`). **No añade `scope`.**
- `app/core/security.py:83-99` — `create_verification_token(email)`:
  `to_encode = {"sub": email, "scope": "email_verification", "exp": expire}`; dura
  `verification_token_expire_minutes` (`app/core/config.py:51`, `= 15`). Misma clave y algoritmo (`:101-103`).
- `app/services/user_service.py:171-173` — único emisor de acceso en `app/`: `authenticate_user` firma
  `{"sub": user.email, "role": user.role.value}` con `create_access_token(data=token_payload)`. Sin `scope`.
- `app/services/user_service.py:104` — único emisor de verificación en `app/`: `register_tourist`.
  Solo los turistas reciben token de verificación (el alta de admin no llama a `create_verification_token`).

Decodificación (los dos únicos `jwt.decode` de `app/`):
- `app/api/dependencies.py:120-123` — la deuda:
  `payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])` ·
  `email: str | None = payload.get("sub")` · `if email is None: raise credentials_exception`. No hay `scope` en el
  archivo (`git grep -n -c "scope" -- app/api/dependencies.py` → sin salida, exit 1).
- `app/services/user_service.py:124,135-137` — el otro extremo sí está protegido:
  `scope: str | None = payload.get("scope")` · `if email is None or scope != "email_verification":`. Un token de
  acceso no sirve para verificar; uno de verificación sí sirve como acceso. La protección es asimétrica.

Guards que heredan la deuda (todos dependen de `get_current_user`):
- `app/api/dependencies.py:144` — `get_current_admin_user(current_user: User = Depends(get_current_user))`.
- `app/api/dependencies.py:164` — `get_current_superadmin_user(current_user: User = Depends(get_current_user))`
  (BE-40). Se monta sobre `get_current_user`, no sobre el guard de admin: **hereda el chequeo de `scope` sin
  tocarse** en cuanto `get_current_user` lo haga. Confirma la nota de BE-40.
- `app/api/dependencies.py:191-193` — `UserDep`, `AdminDep`, `SuperadminDep` (`Annotated[User, Depends(...)]`).
- Montaje de los guards en routers: `app/api/routers/user.py:33-35` (`self_service_router`, `admin_router`,
  `superadmin_router`), `app/api/routers/service.py:23` (`admin_router`), `app/api/routers/audit.py:7`.

Rutas afectadas (`tests/test_route_guards.py:38-56`, `PROTECTED_ROUTES`): **17**. 1 `superadmin`
(`POST /usuarios/admin`), 13 `admin`, 3 `user` (`GET /usuarios/mi-perfil`, `DELETE /usuarios/{cedula}`,
`PATCH /usuarios/{cedula}`). `pytest tests/test_route_guards.py --collect-only -q` → **46 tests collected**
(17 sin token, 14 turista en ruta de admin/superadmin, 1 admin en ruta de superadmin, 3 turista en ruta de usuario,
9 públicas, 2 de inventario). Coincide con la nota de BE-40.

Impacto real hoy: como solo los turistas reciben token de verificación, el abuso práctico son las 3 rutas `user`: con el
enlace del correo se lee el perfil, se hace soft-delete de la propia cuenta (`app/api/routers/user.py:127-144`) o se
cambia el correo y el nombre (`:147-170`; `UserUpdate.email`, `app/schemas/user.py:160`) durante 15 min, sin
contraseña. En las rutas de admin/superadmin un turista recibe 403 del guard de rol. Un token de verificación firmado
para el correo de un admin (solo posible en tests, con `create_verification_token(admin.email)`) pasaría hoy también
esos guards.

Factories y emisores en tests:
- `tests/conftest.py:207-229` — `make_token(user, *, expires_delta=None, extra_claims=None)`: firma
  `{"sub": user.email, "role": user.role.value}` + `extra_claims` con `create_access_token` (`:227`). Sin `scope`.
- `tests/conftest.py:233-245` — `make_auth_headers(user)` → `Bearer {make_token(user)}`. Todas las peticiones
  autenticadas de la suite pasan por aquí (test_audit, test_auth, test_route_guards, test_services,
  test_token_failure_paths, test_user_access_policy, test_user_response).
- `tests/test_token_failure_paths.py:44` — `_expired_token()` → `create_access_token(data={"sub": "ghost@test.com"}, expires_delta=timedelta(minutes=-1))`.
- `tests/test_token_failure_paths.py:140` — `create_access_token(data={"sub": "ghost@test.com"})` (usuario desconocido).
- `tests/test_token_failure_paths.py:150` — `create_access_token(data={"role": "tourist"})` (sin `sub`).
- `tests/test_token_failure_paths.py:162` — `create_access_token(data={"sub": "ghost@test.com"})` (usuario desconocido).
- `tests/test_token_failure_paths.py:57-61` — `_resign(token, key)`: re-firma los claims de un token real
  (`:198`, `:212`, `:233`); conserva el `scope` que tenga el token original.
- `tests/test_user_service.py:284-288` — `make_token(..., expires_delta=timedelta(minutes=-1), extra_claims={"scope": "email_verification"})`.
- `tests/test_user_service.py:300-302` — `make_token(..., extra_claims={"scope": "access"})` (test de scope equivocado
  en verificación; ya usa el valor que la meta propone).
- Verificación en tests: `tests/test_auth.py:94`, `tests/test_token_failure_paths.py:212`,
  `tests/test_user_service.py:262,315` (`create_verification_token`).

Aserciones sobre claims emitidos (las rompería o ampliaría el cambio):
- `tests/test_auth.py:131-135` — login: `claims["sub"]`, `claims["role"]`; no compara el conjunto de claims.
- `tests/test_user_service.py:211-215` — `authenticate_user`: `claims["sub"]`, `claims["role"]`; idem.
- `tests/test_user_service.py:107-111` — registro: `claims["scope"] == "email_verification"`.

No existe hoy ningún test "token de verificación como bearer": `git grep -n -E "_bearer\(create_verification|verification.*bearer" -- tests` → sin salida.

## Ficheros afectados (mapa completo)
- `app/api/dependencies.py` — `get_current_user` (`:90-141`) decodifica sin comprobar `scope`; los guards
  `get_current_admin_user` (`:144`) y `get_current_superadmin_user` (`:164`) y los alias (`:191-193`) lo heredan.
- `app/core/security.py` — `create_access_token` (`:50-80`) no pone `scope`; `create_verification_token` (`:83-105`)
  pone `scope="email_verification"` con la misma clave.
- `app/services/user_service.py` — emisor de acceso (`:171-173`, sin `scope`) y verificador del token de correo
  (`:124-137`, el único que mira `scope`); emisor de verificación (`:104`).
- `tests/conftest.py` — `make_token` (`:207-229`) y `make_auth_headers` (`:233-245`): toda la autenticación de la suite.
- `tests/test_token_failure_paths.py` — 4 tokens firmados a mano con `create_access_token` sin `scope`
  (`:44`, `:140`, `:150`, `:162`); hogar natural del caso "verificación como bearer → 401" (ya tiene `_bearer` y
  `_assert_bearer_401`).
- `tests/test_route_guards.py` — `PROTECTED_ROUTES` (17 rutas) para el caso parametrizado sobre todas las rutas, si el
  plan lo quiere (nota R3 de BE-39).
- `tests/test_auth.py`, `tests/test_user_service.py` — aserciones sobre claims del token de login (`:131-135`;
  `:211-215`) y tokens con `scope` explícito (`tests/test_user_service.py:284-288`, `:300-302`).
- (sin cambio previsto) `app/api/routers/user.py`, `app/api/routers/service.py`, `app/api/routers/audit.py` — montan
  los guards; heredan el arreglo sin tocarse.

## Rincones no mencionados por la fuente
1. **Protección asimétrica.** `verify_email_account` (`app/services/user_service.py:137`) ya rechaza un token de acceso
   (`scope != "email_verification"`); el hueco es solo en la dirección verificación → acceso. El patrón a imitar está
   en el propio repo.
2. **Tres tests de `test_token_failure_paths.py` pueden quedar en "test theater" según dónde se ponga `scope=access`.**
   `:136-145` (corrupto = desconocido), `:148-154` (sin `sub`) y `:157-166` (usuario desconocido) firman con
   `create_access_token` sin `scope`. Si el `scope` se añade en `authenticate_user` y no en `create_access_token`,
   esos tres siguen dando 401, pero por el `scope` ausente y no por la rama que nombran (desconocido, sin `sub`). Pasan
   en verde sin probar lo que dicen. Pasa lo mismo con `_expired_token` (`:44`) solo si el chequeo de `scope` corre antes
   que la verificación de `exp`; con PyJWT no ocurre (`exp` se valida dentro de `jwt.decode`).
3. **`make_token(extra_claims=...)` y un `scope` forzado.** Si `create_access_token` impone `scope="access"` con
   `update` *después* de `data`, sobrescribe el `extra_claims={"scope": "email_verification"}` de
   `tests/test_user_service.py:287`. El test sigue en verde (lo tumba `exp`), pero deja de construir lo que dice. Con
   `setdefault`, o si el `scope` lo pone la fábrica, el `extra_claims` se respeta.
4. **El literal `"email_verification"` está repetido** en `app/core/security.py:99` y en
   `app/services/user_service.py:137`. `"access"` sería un tercer literal en dos sitios más (emisor y `get_current_user`).
   No es deuda nueva; es un riesgo de deriva que el plan decide si asume.
5. **El token de verificación no es de un solo uso,** aunque lo diga `app/core/security.py:84` ("single-use") y
   `app/services/user_service.py:37`: `activate_user` (`app/repositories/user_repository.py:33-44`) solo pone
   `is_active = True`, así que el mismo enlace vuelve a funcionar durante sus 15 min. Además viaja en la query string
   (`app/core/email.py:41`, `?token=`). Queda fuera de BE-42; si interesa, va al backlog como fila aparte.
6. **Severidad distinta en las fuentes:** la auditoría de A4 la propuso "Baja" (`docs/deuda/A4/gaps.md:125`, "el
   portador es el dueño del correo"); la fila del backlog dice "Media". Manda la fila. Este informe no cambia la
   severidad.
7. **Cita desfasada:** la auditoría de A4 la sitúa en `dependencies.py:106-110`. Tras BE-40 el bloque está en
   `app/api/dependencies.py:119-123`.
8. **`TokenData.role`** (`app/schemas/token.py:23`) existe, pero `get_current_user` no lo usa (`:125` solo pasa
   `email`). No afecta a BE-42; solo se apunta.

## Patrones de detección (copiables)
```bash
# 1. La deuda: get_current_user no menciona scope (hoy: sin salida, exit 1; tras el arreglo: ≥ 1 línea)
git grep -n "scope" -- app/api/dependencies.py

# 2. Todos los puntos que decodifican tokens (hoy: 2 — dependencies.py:120, user_service.py:124)
git grep -n -E "jwt\.decode\(" -- app

# 3. Todos los puntos que firman tokens (hoy: 2 — security.py:76, security.py:101)
git grep -n -E "jwt\.encode\(" -- app

# 4. Emisores de acceso y de verificación en app/ y tests/
git grep -n -E "create_access_token\(|create_verification_token\(" -- app tests

# 5. Claims de scope en app/ (hoy: security.py:99, user_service.py:135; tras el arreglo deben aparecer el emisor de acceso y get_current_user)
git grep -n -E "\"scope\"|scope=" -- app

# 6. Tokens firmados a mano en tests sin pasar por make_token (hoy: test_token_failure_paths.py:44,140,150,162)
git grep -n -E "create_access_token\(data=" -- tests

# 7. Caso de rechazo pedido por la fila (hoy: sin salida)
git grep -n -E "_bearer\(create_verification|verification.*bearer|bearer.*verification" -- tests

# 8. Guards montados sobre get_current_user (hoy: dependencies.py:144,164,191)
git grep -n -E "Depends\(get_current_user\)" -- app/api/dependencies.py

# 9. Inventario de rutas protegidas (hoy: 17 filas; 46 tests)
git grep -n -c "ProtectedRoute(\"" -- tests/test_route_guards.py
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py --collect-only -q
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `deb0b1e` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `deb0b1e0e5c5aaf05960814fd1f10ef40d9559c7`; HEAD `item/be-42` = `d7f97f4`, solo
  documentación sobre esa base)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (exit 0). Python 3.14.3.

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
- pytest: `618 passed, 8 warnings in 20.89s` (0 failed). Los warnings son `StarletteDeprecationWarning` de
  `HTTP_422_UNPROCESSABLE_ENTITY`, ajenos al ítem.
- Cobertura: `TOTAL 961 19 136 16 96.81%` · `Required test coverage of 92.0% reached. Total coverage: 96.81%`.
- ruff format: `61 files already formatted` · ruff check: `All checks passed!` (0 errores).
- mypy: `Success: no issues found in 56 source files` (0 errores).
- import-linter: `Contracts: 4 kept, 0 broken.` Los cuatro, KEPT: Capas api -> services -> repositories -> models ·
  Los servicios no conocen el transporte HTTP · Los repositorios solo conocen SQLAlchemy y los modelos · Los modelos y
  los schemas no dependen de capas superiores.
- docs: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- La compuerta está en verde antes de tocar nada.

## Conclusión para el planificador
El plan debe hacer que **todo** token de acceso lleve `scope="access"` y que `get_current_user`
(`app/api/dependencies.py:120-123`) devuelva 401 (`credentials_exception`, con Bearer challenge) si el `scope` no es
`"access"`. Hay que decidir y justificar dónde se pone el claim. En `create_access_token` cubre `authenticate_user`,
`make_token` y los 4 tokens a mano de `tests/test_token_failure_paths.py` (`:44,140,150,162`), pero hay que respetar
el `extra_claims` (rincón 3). En `authenticate_user` + `make_token`, esos 4 tests pasan a probar la rama del `scope`
y no la que nombran (rincón 2). En los dos casos, mutante: quitar el chequeo de `scope` debe tumbar el test
"verificación como bearer → 401". Ese test necesita una cuenta activa, porque hoy da 200 en `GET /usuarios/mi-perfil`.
Si se parametriza sobre `PROTECTED_ROUTES` (17 rutas), en las de admin/superadmin el token de verificación debe ser
de un admin/superadmin; con un turista daría 403 antes y después del arreglo.
No tocar: `get_current_admin_user` ni `get_current_superadmin_user` (heredan el arreglo), los routers, la política,
`verify_email_account` (ya correcta) ni el carácter "un solo uso" del token de verificación (rincón 5; fuera de alcance).
Riesgos: los tokens de acceso vivos al desplegar dejan de valer (máx. 30 min, `access_token_expire_minutes`): hay que
declararlo en el PR. Las aserciones de claims de login (`tests/test_auth.py:131-135`,
`tests/test_user_service.py:211-215`) deben comprobar además `claims["scope"] == "access"`. Previsión: un dominio
(auth), ≤ 5 archivos (`security.py` o `user_service.py`, `dependencies.py`, `conftest.py`,
`test_token_failure_paths.py`, opcionalmente `test_route_guards.py` o `test_auth.py`).

## Adenda — decisiones de David antes de planear (12 nov 2026, 15:21, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base aceptada:** `deb0b1e`,
compuerta completa en verde (618 passed · 96,81 % · ruff 0 · mypy 0 en 56 archivos · 4 kept). Severidad: Media, la de
la fila (rincón 6). Contraste de la sesión Mentor contra el código, sin correcciones de hecho: `security.py:50-80,99`,
`dependencies.py:120-123`, `user_service.py:124-137,171-173`, `tests/conftest.py:207-229`,
`tests/test_token_failure_paths.py:44,57-61,136-166`, `tests/test_user_service.py:280-288`. David aprobó los cuatro puntos
a las 15:21 ("sí a las 4").

1. **El `scope` lo pone `create_access_token`, siempre** (opción (a) de la conclusión; David: "sí a a"). La función
   impone `scope` de acceso sobre lo que traiga `data`: ningún llamador elige el `scope` de un token de acceso, igual
   que `create_verification_token` fija el suyo. `get_current_user` lo exige y, si no coincide, responde con la misma
   `credentials_exception` de hoy (401, `WWW-Authenticate: Bearer`, mismo `detail`): el cliente no distingue qué falló.
   Consecuencias que el plan resuelve y mide:
   - `tests/test_user_service.py:280-288` (`test_verify_email_expired_token_…`) fabrica hoy su token con
     `make_token(..., extra_claims={"scope": "email_verification"})`. Con el `scope` impuesto, ese token pasaría a ser uno
     de acceso caducado y el test seguiría en verde (lo rechaza `exp` antes de mirar el `scope`, `user_service.py:124-127`)
     sin construir lo que su nombre dice. El planificador dicta otra forma de construir un token de verificación
     caducado y la justifica (sin ampliar la API de producción solo para un test, salvo que lo argumente).
   - `tests/test_user_service.py:300-302` (`extra_claims={"scope": "access"}`) queda redundante: el plan dice qué hace con él.
   - El docstring de `make_token` (`tests/conftest.py:215-216`) promete que `extra_claims` puede sobrescribir un `scope`;
     deja de ser cierto y se corrige.
   - Los tres tests de `tests/test_token_failure_paths.py:136-166` siguen probando la rama que nombran (rincón 2): con
     (a) sus tokens llevan `scope` y llegan a la comprobación de `sub` y a la búsqueda del usuario. El plan lo demuestra
     (mutante o medición), no lo supone.
2. **Constantes, no literales** (rincón 4; David: "vámonos por las constantes"). Dos constantes en
   `app/core/security.py` para los dos valores de `scope`, usadas por los dos emisores (`create_access_token`,
   `create_verification_token`) y por los dos verificadores (`get_current_user`, `app/api/dependencies.py`; y
   `verify_email_account`, `app/services/user_service.py:137`, que cambia una línea sin cambiar su comportamiento). Los
   nombres los elige el planificador. Los valores no cambian: `"email_verification"` ya viaja en enlaces emitidos.
3. **Tests de rechazo** (David: "los apruebo"):
   - **Token de verificación como bearer → 401, parametrizado sobre las 17 filas de `PROTECTED_ROUTES`**
     (`tests/test_route_guards.py`), con el token de verificación de un **superadmin activo**: pasa todos los guards de
     rol, así que hoy ninguna ruta responde 401 y el RED se mide ruta por ruta. Una ruta futura cuyo guard no pase por
     `get_current_user` caería aquí.
   - **Token de acceso sin `scope` → 401.** Es el efecto declarado del punto 5, fijado por un test. Como
     `create_access_token` siempre lo pondrá, ese token se firma de otra forma (el planificador la dicta).
   - **Claims del login:** `tests/test_auth.py:131-135` y `tests/test_user_service.py:211-215` comprueban además el
     `scope` de acceso.
   - **Mutantes mínimos:** quitar la comprobación de `scope` de `get_current_user` (deben caer los dos primeros grupos);
     quitar el `scope` de `create_access_token` (el plan declara cuántos tests caen).
4. **El rincón 5 recibe fila, fuera de BE-42:** **BE-50**, `Sale → B-FUTURO`, detrás de SEC3 en el orden de prioridad de ese
   bloque (PLAN §2b). El enlace de verificación no es de un solo uso aunque lo digan `app/core/security.py:84` y
   `app/services/user_service.py:37`: el segundo clic responde otra vez 200. Razón de David: tras BE-42 el token ya no
   sirve de acceso y repetir el clic es inofensivo; es experiencia de usuario, y si un jurado se registra el día de la
   sustentación conviene que lo que vea esté cubierto; si no da el tiempo, se sustenta. **BE-42 no toca esos dos
   docstrings ni `activate_user`.**
5. **Efecto que el PR declara:** un token de acceso emitido por la versión anterior no lleva `scope`; desde el momento
   en que se despliega la versión nueva, `get_current_user` lo rechaza con 401 aunque no haya caducado. Afecta solo a
   quien tenga una sesión abierta en ese momento, que vuelve a iniciar sesión, y el efecto desaparece solo: un token de
   acceso dura 30 min (`access_token_expire_minutes`), así que media hora después del despliegue ya no queda ninguno de
   los viejos. El cliente Flutter no maneja el 401 (FE-01, sin redirección al login): verá lo mismo que hoy con una
   sesión vencida.

**No se toca** (de la conclusión, sin cambios): `get_current_admin_user`, `get_current_superadmin_user`, los alias, los
routers, la política. **ADR:** lo decide el planificador en su paso 6; lectura de la sesión Mentor: el patrón ya existe en
`verify_email_account` y BE-42 lo completa en el otro sentido.

# Verificación — BE-50: el enlace de verificación de correo no es de un solo uso

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-50, §B; nace del rincón 5 de `docs/deuda/BE-42/verificacion.md:119-122`;
medida en la re-verificación de BE-38, sonda V4, `docs/deuda/BE-38/verificacion.md:346`, y decisión 14, `:539-544`)
**Fecha:** 2026-11-19

## Qué describe el ítem
Siete comentarios y docstrings llaman "single-use" al token de verificación, pero `verify_email_account` no impide su
reutilización: durante los 15 min de vida del token, un segundo clic vuelve a responder 200 "Cuenta verificada
exitosamente", y el mismo enlace reactiva una cuenta que un admin desactivó (V4). La causa de fondo es de datos: el
único estado es `is_active`, y `false` significa a la vez "pendiente de verificar", "desactivada por un admin" y
"recuperada de la papelera, pendiente de aprobación". El token viaja en la query string.

## Evidencia en el código
Las líneas que cita la fila (`security.py:84`, `user_service.py:37`, `user_repository.py:33-44` con `activate_user`)
son anteriores a `2ef12e7` (BE-38); la fila ya lo advierte. Medidas hoy sobre `c478e38`:

- `app/core/security.py:92` — `"""Generates a single-use JWT token for user email validation purposes.` El token solo
  lleva `sub`, `scope` y `exp` (`:107`, `{"sub": email, "scope": EMAIL_VERIFICATION_SCOPE, "exp": expire}`): no hay
  identificador de token (`jti`) ni nada que se pueda marcar como usado.
- `app/core/config.py:51` — `verification_token_expire_minutes: int = 15`: ventana de reutilización.
- `app/services/user_service.py:109` — `verify_email_account`. Tras validar firma y `scope` (`:131-143`):
  - `:145` — `user = await self.user_repo.get_non_deleted_user_by_email(email)`: busca por correo, solo excluye borradas.
  - `:150` — `changes = changed_fields(user, {"is_active": True})`: si ya está activa, `changes` es vacío y no muta
    ni audita (BE-38); si está inactiva por cualquier motivo, la activa (`:151-160`, `save_user` + fila `UPDATE`).
  - `:162-165` — devuelve siempre `{"success": True, "message": "Cuenta verificada exitosamente. Ya puede iniciar
    sesión."}`, haya cambiado algo o no.
- `app/repositories/user_repository.py:43-46` — `get_non_deleted_user_by_email`: `User.email == email,
  User.deleted_at.is_(None)`; no distingue por qué la cuenta está inactiva.
- `app/models/user.py:51` — `is_active: Mapped[bool] = mapped_column(default=False)`; junto con `deleted_at` (`:55`)
  es todo el estado de la cuenta. No existe marca de correo verificado (`grep` de `verified|email_verified` en
  `app/models` y `alembic/versions`: 0 resultados).
- `app/core/email.py:41` — `verification_link = f"{base_url}/usuarios/verificar-email?token={token}"`: token en la
  query string.
- `app/api/routers/user.py:83-92` — `GET /usuarios/verificar-email`, ruta pública; delega en el servicio.
- Docstrings "single-use" (7, todos en `app/`):
  `app/api/routers/user.py:86`, `app/core/security.py:92`, `app/services/user_service.py:32`, `:38`, `:70`, `:104`,
  `:117`.

**Medido hoy** (sondas en el scratchpad, fuera del repo, con las fábricas de `tests/conftest.py`; no forman parte de la
suite):

| Sonda | Secuencia | Resultado |
|---|---|---|
| P1 | cuenta inactiva → enlace → mismo enlace | 200 → **200**, mismo cuerpo `{"success": true, "message": "Cuenta verificada…"}`; 1 sola fila de auditoría |
| P2 (V4) | enlace → admin `PATCH {"is_active": false}` → mismo enlace | 200 → 200 → **200**; `is_active` final **`True`** |
| P3 | cuenta inactiva → admin `DELETE` → admin `PATCH /recuperar` (queda `is_active=False`, `deleted_at=None`) → enlace | 200 → 200 → **200**; `is_active` final **`True`**, `deleted_at` `None` |
| P4 | turista `PATCH /usuarios/{su cédula}` con `{"is_active": true}` | **403** (la política se lo prohíbe) |
| P5b | admin desactiva a un turista activo → el turista hace login con su contraseña | **403**, `detail` "Debe verificar su cuenta. Revise su correo electrónico." |

Los tests de la suite ya congelan P1 y P2 como comportamiento esperado (ver "Ficheros afectados").

## Ficheros afectados (mapa completo)
- `app/services/user_service.py` — `verify_email_account` (`:109-165`): la regla que falta; el mensaje fijo de éxito
  (`:162-165`); cinco docstrings "single-use" (`:32`, `:38`, `:70`, `:104`, `:117`); el mensaje de login de una
  cuenta inactiva (`:185-186`) y la recuperación que deja la cuenta inactiva "por seguridad" (`:357-361`, `:384-385`),
  ambos afectados por la misma ambigüedad de `is_active`.
- `app/core/security.py` — `create_verification_token` (`:91-113`): docstring "single-use" (`:92`); claims sin `jti`.
- `app/api/routers/user.py` — `verificar_cuenta` (`:83-92`): docstring "Single-use" (`:86`).
- `app/repositories/user_repository.py` — `get_non_deleted_user_by_email` (`:43-46`): única consulta de la activación.
- `app/models/user.py` — `:51` (`is_active`) y `:55` (`deleted_at`): no hay dato que distinga "pendiente de verificar"
  de "desactivada"; cerrar V4 exige un dato nuevo (fila del backlog), y por tanto `alembic/versions/` (cabeza actual
  `b51f3c9e2a64`).
- `app/core/email.py:41` — token en query string (dato de la fila; no es en sí el defecto).
- `app/core/config.py:51` — 15 min de vida del token.
- `tests/test_auth.py:112-125` — `test_be38_verify_email_on_active_account_returns_200_without_audit_row`: congela
  "cuenta activa + enlace → 200, `success: true`".
- `tests/test_auth.py:147-171` — `test_be38_verify_email_after_admin_deactivation_writes_an_audit_row`: congela V4
  (`verified.status_code == 200`, `is_active is True`); su docstring (`:152`) dice "That the link can do it at all is
  BE-50".
- `tests/test_user_service.py:286-301` — `test_verify_email_on_active_account_writes_nothing`: congela
  `result["success"] is True` para una cuenta ya activa.
- `tests/test_auth.py:92-109`, `:128-144`, `:174-180`; `tests/test_user_service.py:263-283`, `:304-364`;
  `tests/test_email_case.py:198-210`; `tests/test_token_failure_paths.py:308-327` — resto de tests del enlace; no
  congelan el defecto, pero un cambio de datos (columna nueva) o de fábrica (`make_user`/`persist_user` en
  `tests/conftest.py:168-206`, `:268`) los toca.
- `tests/test_route_guards.py:81`, `:96` — la ruta está en `PUBLIC_ROUTES` con 422 sin `token`; no cambia salvo que
  cambie la firma de la ruta.
- `docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md:37-39` (punto 5) y `:71-72` (alternativa 4 rechazada) —
  restricción: la activación por correo es un `UPDATE` de `is_active` con la cuenta como autora; no hay acción `VERIFY`.

## Rincones no mencionados por la fuente
1. **Siete docstrings "single-use", no dos.** La fila cita `security.py` y `user_service.py:37`; hay además
   `user_service.py:32`, `:70`, `:104`, `:117` y `app/api/routers/user.py:86`.
2. **La recuperación de la papelera también se salta con el enlace (P3, medido).** `recover_user_account` deja la
   cuenta inactiva "requiring explicit administrative approval" (`user_service.py:357-359`, `:385`; mensaje
   "Se encuentra inactivo por seguridad.", `:401`), pero un enlace aún vigente la activa sin aprobación (200,
   `is_active=True`). Misma causa que V4; ocurre en el primer uso del enlace si registro, borrado y recuperación caben
   en 15 min.
3. **El enlace salta la política de acceso.** `UserAccessPolicy.assert_can_update` prohíbe a un turista tocar
   `is_active` (`app/services/user_access_policy.py:105-109`; P4: 403), pero el enlace lo hace por otra puerta (P2).
   No es un defecto de la política: es la misma ambigüedad de datos.
4. **El login de una cuenta desactivada por un admin le pide verificar el correo (P5b, medido).**
   `authenticate_user` lanza `AccountNotActiveError("Debe verificar su cuenta. Revise su correo electrónico.")`
   (`user_service.py:185-186`) para todo `is_active=False`; su docstring (`:178`) lo describe como "Account pending
   email verification". Con un enlace vigente en el buzón, el mensaje empuja justo a V4. Comparte causa; cambiarlo es
   decisión de producto (texto que ve el usuario).
5. **Tres tests congelan el comportamiento actual** (`tests/test_auth.py:112-125`, `:147-171`;
   `tests/test_user_service.py:286-301`): cualquier corrección los hace caer y debe reescribirlos, no borrarlos.
6. **Otras cuentas que nacen con `is_active=False` sin pasar por el enlace:** el alta administrativa
   (`user_service.py:444`, `UserCreateByAdmin.is_active = False` por defecto en `app/schemas/user.py:132`) no emite
   token (solo `register_tourist`, `:105`, llama a `create_verification_token`), así que hoy no es alcanzable por el
   enlace. Pero si el arreglo añade una marca de "correo verificado", el plan debe decidir su valor para cuentas
   administrativas, para el superadmin del bootstrap (`app/services/superadmin_bootstrap.py:62`) y el relleno de las
   filas existentes en la migración: una fila inactiva y no borrada hoy no dice si está pendiente o desactivada.
7. **No hay ruta para pedir otro enlace** (dato C6 de BE-38, confirmado: `grep -rn -i "resend\|reenviar" app` sin
   resultados en rutas). Si el enlace pasa a ser de un solo uso, un usuario que pierde la respuesta del primer clic no
   tiene forma de obtener otro; el mensaje de token expirado (`user_service.py:132`) ya dice "Por favor solicite
   uno nuevo" sin que exista dónde.

## Patrones de detección (copiables)
```bash
# 1. Docstrings que prometen "single-use" (hoy: 7 en app/; tras el arreglo: 0 o ciertos)
grep -rn -i "single-use" app tests --include=*.py

# 2. La regla que falta: la activación decide solo por el valor actual de is_active (hoy: user_service.py:150)
grep -n 'changed_fields(user, {"is_active": True})' app/services/user_service.py

# 3. Respuesta fija de éxito del enlace (hoy: 1, user_service.py:164)
grep -rn "Cuenta verificada exitosamente" app --include=*.py

# 4. Dato que distinga "pendiente de verificar" (hoy: 0 en modelos y migraciones)
grep -rn -i -E "verified|email_verified|verification_sent|jti" app/models alembic/versions app/core/security.py

# 5. Tests que congelan el defecto (hoy: test_auth.py:112, :147; test_user_service.py:286)
grep -n -E "def test_be38_verify_email_on_active_account|def test_be38_verify_email_after_admin_deactivation|def test_verify_email_on_active_account_writes_nothing" tests/test_auth.py tests/test_user_service.py

# 6. Mención explícita de BE-50 en tests (hoy: test_auth.py:152)
grep -rn "BE-50" app tests alembic --include=*.py

# 7. Todos los tests que golpean el enlace (hoy: test_auth.py, test_email.py, test_email_case.py)
grep -rln "verificar-email?token=" tests --include=*.py

# 8. Escritores de is_active (puertas por las que una cuenta queda inactiva o activa)
grep -rn "is_active = \|is_active=" app --include=*.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `c478e38` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `c478e3876d00bd315014780f925d4e419ede3f05`; precondición cumplida).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (desde `C:\projects\ecotur-asoprado`, Python 3.14.3).

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
- Código de salida: 0. La compuerta pasa antes de tocar nada.
- ruff format: `71 files already formatted`. ruff check: `All checks passed!` (0 errores).
- mypy: `Success: no issues found in 66 source files` (0 errores).
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas `api | cli -> services -> repositories -> models` KEPT; Los
  servicios no conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los
  modelos y los schemas no dependen de capas superiores KEPT).
- docs: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- pytest: `797 passed, 25 warnings in 34.51s` (0 failed).
- Cobertura total: `98.69%` (`Required test coverage of 92.0% reached.`).

## Conclusión para el planificador
Confirmada y algo más ancha que la fila: el defecto de fondo es que `is_active=False` tiene tres significados
(pendiente, desactivada por admin, recuperada sin aprobar) y el enlace los activa todos (P1, P2, P3 medidos). El plan
debe primero obtener de David la decisión de producto que la fila deja abierta (qué ve el usuario en el segundo clic:
rechazo o "ya verificada") y elegir el dato nuevo (marca de correo verificado o enlace de un solo uso, con `jti`
almacenado); la marca cierra V4 y P3, el solo-uso por sí solo no cierra P3 si cae en el primer uso. Ese dato es un
cambio de esquema: modelo en estilo S1, migración Alembic con relleno decidido para filas existentes (activas →
verificadas; inactivas no borradas son ambiguas) y valor para cuentas administrativas y bootstrap. Debe respetar
ADR-0021 punto 5 (la activación sigue siendo `UPDATE` de `is_active`, sin acción `VERIFY`; un rechazo no deja fila),
reescribir los tres tests que congelan el defecto y corregir los siete docstrings. Fuera de alcance salvo decisión
expresa: ruta de reenvío del enlace (rincón 7), texto del login de una cuenta desactivada (rincón 4), sacar el token de
la query string, y la atomicidad save/auditoría (A3).

## Adenda — decisiones de David antes de planear (19 nov 2026, 11:24, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador toma estas decisiones como dadas; lo demás (fases, tests,
commits, nombres) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base
aceptada:** `c478e38`, compuerta completa en verde (797 passed · 98,69 % · ruff 0 · mypy 0 en 66 archivos · 4 kept).

Contraste de la sesión Mentor contra el código de `f6ec752`, sin correcciones de hecho: las siete menciones de
"single-use"; `app/services/user_service.py:109-165`, `:185-186`, `:357-361` y `:384-385`;
`app/services/user_access_policy.py:105-109`; `tests/test_auth.py:112`, `:147` y `:152`;
`tests/test_user_service.py:286`. Las sondas P1 a P5b no se repitieron. **Una precisión a la conclusión:** "la marca
cierra V4 y P3" depende de la regla que se elija; con la que David decide abajo, P3 no se cierra porque deja de ser un
defecto (decisión 3).

### Decisiones (David, 10:34, 10:45, 11:03, 11:14 y 11:24)

1. **Mecanismo: una marca de correo verificado en la cuenta, que solo llena el enlace** (opción A de las tres que
   comparó la sesión Mentor; `docs/aprendizaje/fichas/BE-50.md`). Es un dato nuevo en `users`: vacío hasta que el
   enlace se usa con éxito, y lleno para siempre desde entonces. Ningún acto de un administrador lo llena ni lo vacía.
   Nombre y tipo los fija el plan; la sesión Mentor sugiere un instante con zona (`Mapped[datetime | None]`,
   ADR-0010), que además dice cuándo.
2. **Regla del enlace**, con el token válido (firma, `scope` y caducidad, como hoy):
   - cuenta borrada → 404, sin cambios (como desde BE-38);
   - marca vacía → se llena la marca y, si la cuenta está inactiva, pasa a activa; 200 con el mensaje de hoy;
   - marca llena → no cambia nada, no deja fila de auditoría y responde **200 con "Su correo ya fue verificado."**
     (texto de David; no promete que se pueda iniciar sesión, porque la cuenta puede estar desactivada).
   El enlace queda de un solo efecto por el estado de la cuenta, no por consumir el token: el token sigue sin `jti` y
   no se guarda.
3. **El enlace completa el alta de quien nunca la completó, pase lo que pase entre medias.** Dos casos que David
   decide expresamente:
   - **P3 es comportamiento deseado.** Una cuenta que nunca usó su enlace, borrada y recuperada por un administrador,
     se activa con el enlace si aún está vigente: quien se estaba registrando termina su registro. Es una excepción
     declarada a "toda cuenta recuperada espera la aprobación de un administrador"
     (`app/services/user_service.py:357-359`); el plan corrige ese docstring. Para frenar un registro pendiente, el
     administrador borra la cuenta y no la recupera.
   - **Un administrador que activa a mano a un turista no llena la marca.** Si después lo desactiva y el turista usa
     su enlace vigente, el enlace lo activa: el enlace no había muerto (solo muere al usarse o al caducar). Confirmado
     por David a las 11:24.
4. **Después del enlace, `is_active` es solo del administrador.** V4 (P2) queda cerrado: una cuenta con la marca llena
   que un administrador desactiva no vuelve a activarse con el enlace. **Riesgo que David acepta y declara:** si el
   administrador desactiva la cuenta justo después de la verificación, el turista vio la pantalla de éxito y no puede
   entrar; el login le dirá además "Debe verificar su cuenta" `(backlog BE-56)`. Es un tema para las sesiones de
   usabilidad y para el manual de usuario.
5. **Opciones descartadas.** B (el enlace solo anota el correo verificado y entrar exige las dos cosas): es el modelo
   de la industria, pero obliga a cambiar el registro y lo que el kanban del cliente llama "por activar"; queda como
   fila nueva `(backlog BE-62)`. C (un acto del administrador mata el enlace): descartada por David porque la cuenta
   podría quedar activa sin que nadie haya probado que el correo existe.
6. **La migración no inventa verificaciones.** La columna nace vacía en todas las filas, también en las activas: una
   cuenta activa hoy pudo activarla un administrador. No hace falta contar filas por entorno ni hay precondición de
   datos: un enlace vive 15 min (`app/core/config.py:51`), así que los únicos enlaces que la marca vacía deja vivos
   son los emitidos en los 15 min anteriores al despliegue. Las cuentas administrativas y el superadmin del bootstrap
   no reciben enlace: su marca queda vacía.
7. **Auditoría: ADR-0021, punto 5, no cambia, y la marca no se audita.** La fila sigue siendo un `UPDATE` de
   `is_active` con la cuenta como autora, y existe solo cuando el enlace cambia `is_active`. Secuencia que David
   describe (11:24): el administrador activa a mano → fila del administrador; lo desactiva → fila; el turista usa su
   enlace y queda activo → fila del turista. **Si el turista usa su enlace cuando el administrador ya lo tenía
   activo, la marca se llena y no queda fila** (David: "de momento tiene sentido"); cuándo se verificó lo dice la
   propia marca. La sesión Mentor había propuesto auditar la marca; David decidió que no.
8. **Los siete docstrings "single-use" pasan a decir lo que el código hace.** Los tres tests que congelan el defecto
   se reescriben, no se borran; cada caso de las decisiones 2 a 4 tiene su test, y los mutantes se miden en copias
   `git archive` (E1 de BE-38).
9. **ADR-0022, que dicta el plan.** Declara que la opción elegida es una simplificación frente al modelo de dos
   hechos separados y por qué (decisión 5). Fuentes que la sesión Mentor consultó el 19 nov **solo en extractos de
   búsqueda, no en la página entera**; el planificador las lee antes de citarlas (regla del 14 nov): OWASP ASVS 4,
   2.3.1 (códigos de activación aleatorios y de vida corta; versión anotada en
   `https://owasp-aasvs4.readthedocs.io/en/latest/2.3.1.html`); OWASP, Forgot Password Cheat Sheet (tokens de un solo
   uso y con caducidad; trata de la recuperación de contraseña, se aplica por analogía); Devise, módulo Confirmable
   (`https://rubydoc.info/gems/devise/Devise/Models/Confirmable`: `confirmed_at` en columna propia; `confirm` no
   vuelve a confirmar; el acceso exige además estar confirmado, que es la opción B).
10. **Entorno.** El ítem toca `app/models/` y `alembic/`: David corre `alembic check` contra su PostgreSQL local antes
    y después de la fase que toque el modelo (ADR-0010, punto 7) y lo tiene encendido antes de planear. Si un agente
    necesita medir en PostgreSQL, usa un contenedor desechable sin secretos. Los pasos que el plan asigne a David van
    en sintaxis de `cmd`.
11. **No cambia en este ítem:** los DTO de salida y el contrato con el cliente (la marca no se expone), la firma de
    la ruta, los claims del token, el token en la query string, el texto del login de una cuenta inactiva
    `(backlog BE-56)`, la falta de una ruta de reenvío (rincón 7), que es el ítem siguiente del bloque `(backlog BE-64)`, y A3.
12. **El enlace del correo abre el cliente, no la API.** `app/api/routers/user.py:66-75` arma el enlace con
    `frontend_url`; la pantalla del cliente tiene un botón, y ese botón es el que llama a
    `GET /usuarios/verificar-email` (lo segundo es palabra de David, 11:14: la sesión Mentor no ve el repositorio del
    cliente). Un escáner de correo que abra el enlace carga esa pantalla y no verifica nada. **Corrige a la sesión
    Mentor,** que había escrito aquí lo contrario al leer la ruta del enlace como si fuera la de la API (tienen el
    mismo camino). El plan no cambia esa pantalla; si el texto nuevo del segundo clic necesita algo del cliente, lo
    dice como residual.
13. **Filas nuevas:** `(backlog BE-62)` y `(backlog BE-63)` (un administrador puede activar a un turista que nunca
    verificó su correo; David, 11:03: no es algo que un jurado vaya a ver, va a `B-FUTURO`), con las severidades confirmadas por David, y `(backlog BE-64)`, el reenvío del enlace, que entra en el
    bloque como su último ítem (David, 11:24). La viñeta de AGENTS §3,
    después de la última auditoría, la commitea David.

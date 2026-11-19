# Verificación — BE-64: no hay forma de pedir otro enlace de verificación

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-64, l.119; origen: rincón 7 de `docs/deuda/BE-50/verificacion.md`, l.107-110, y
dato C6 de `docs/deuda/BE-38/verificacion.md`, l.466). No referencia tag del informe de auditoría.
**Fecha:** 2026-11-19

## Qué describe el ítem
El enlace de verificación caduca a los 15 min y no existe ninguna ruta (ni comando) que emita otro. El mensaje de
token expirado pide "solicite uno nuevo" sin que haya dónde, y repetir el registro da 400 porque el correo y la cédula
ya existen. La cuenta queda inactiva hasta que un administrador la active a mano (BE-63).

## Evidencia en el código
- `app/core/config.py:51` — `verification_token_expire_minutes: int = 15`.
- `app/core/security.py:91-109` — `create_verification_token(email)`: `exp = now + verification_token_expire_minutes`,
  claims `{"sub", "scope": EMAIL_VERIFICATION_SCOPE, "exp"}`; sin `jti`, no se guarda.
- `app/services/user_service.py:106` — **única** llamada a `create_verification_token` en `app/`, dentro de
  `register_tourist`.
- `app/api/routers/user.py:43-78` — `POST /usuarios/registro`: **único** sitio que programa `send_verification_email`
  (`background_tasks.add_task(send_verification_email, ...)`, l.70-76).
- `app/services/user_service.py:138-142` — `except jwt.ExpiredSignatureError` →
  `InvalidVerificationTokenError("El enlace de verificación ha expirado. Por favor solicite uno nuevo.")` (400,
  `app/main.py:127`). La fila cita `:132`; hoy está en `:141`.
- `app/services/user_service.py:76-80` — `register_tourist` rechaza con `AlreadyExistsError("Este usuario ya se
  encuentra registrado.")` (400, `app/main.py:124`) si existe correo **o** cédula. La fila cita `:75`; hoy `:80`.
- `app/repositories/user_repository.py:17-21` — `get_user_by_email_or_cedula` no filtra `deleted_at`: también una
  cuenta borrada bloquea el re-registro.
- `app/services/user_service.py:198-199` — login de cuenta inactiva: `AccountNotActiveError("Debe verificar su cuenta.
  Revise su correo electrónico.")` (403): remite al correo, cuyo enlace ya caducó.
- `app/api/routers/user.py:43, 81, 98` — las tres rutas públicas de usuarios: `/registro`, `/verificar-email`,
  `/login`. Ninguna emite un enlace nuevo. Rutas de usuarios protegidas: l.117, 130, 151, 182, 201, 220, 247; ninguna
  emite enlace.
- `tests/test_route_guards.py:78-89` — `PUBLIC_ROUTES` confirma el inventario: no hay ruta de reenvío.
- `app/cli/` — sin comando que emita enlace (el grep de `create_verification_token` no lo encuentra).
- Sin limitador de peticiones: `grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml
  constraints.txt` → 0 resultados (dato para el punto (c) de la fila).
- `app/models/user.py:40-58` — `users` no tiene columna de "último envío"; la única marca es `email_verified_at`
  (l.58).

## Ficheros afectados (mapa completo)
- `app/api/routers/user.py` — no hay ruta de reenvío; la ruta nueva iría en `public_router` (l.32) y reutilizaría el
  patrón de `BackgroundTasks` de `/registro` (l.70-76).
- `app/services/user_service.py` — `register_tourist` es el único emisor del token (l.106); el texto de l.141 promete
  un reenvío que no existe; la regla de "a quién se le emite" viviría aquí.
- `app/core/security.py` — `create_verification_token` (l.91), reutilizable tal cual.
- `app/core/config.py` — `verification_token_expire_minutes` (l.51); una variable nueva (p. ej. intervalo mínimo
  entre envíos) exige campo, línea en `.env.example` y valor en `conftest.py` raíz (ADR-0013).
- `app/repositories/user_repository.py` — `get_non_deleted_user_by_email` (l.43) ya existe para la búsqueda.
- `app/models/user.py` + `alembic/versions/` — solo si se guarda la hora del último envío (punto (c)).
- `tests/test_route_guards.py` — toda ruta nueva entra en `PUBLIC_ROUTES` (l.78) y `_ANONYMOUS_ON_PUBLIC_ROUTE`
  (l.94), o la suite falla (ADR-0012).
- `tests/conftest.py:156` — el doble de `send_verification_email` parchea `app.api.routers.user.send_verification_email`;
  la ruta nueva en el mismo router lo reutiliza.

## Rincones no mencionados por la fuente
1. **"Marca vacía y no borrada" (punto (b) de la fila) no basta como criterio: alcanza cuentas que no son turistas
   pendientes.** La migración `e50a7c3d9b12` deja `email_verified_at` NULL en **todas** las filas previas
   (`alembic/versions/e50a7c3d9b12_users_email_verified_at.py:22,30`; ADR-0022 punto 7), y solo
   `verify_email_account` la llena (`user_service.py:163`). Por tanto tienen la marca vacía, para siempre:
   - toda cuenta administrativa creada por `create_administrative_account` (`user_service.py:448-460`, con
     `is_active=user_data.is_active`, por defecto `False` en `app/schemas/user.py:132`) y el superadmin del bootstrap
     (`app/services/superadmin_bootstrap.py:62`);
   - todo turista anterior a la migración, incluidos los que verificaron y luego un admin desactivó.
   Como el enlace con marca vacía pone `is_active = True` (`user_service.py:162-164`), una ruta de reenvío con solo ese
   criterio permitiría que (i) un admin desactivado por un superadmin se reactive solo (choca con ADR-0017: "la baja de
   un admin la decide un superadmin"), (ii) una cuenta administrativa creada inactiva se active sin el superadmin, y
   (iii) un turista anterior a BE-50 desactivado por un admin se reactive cuando quiera (lo que ADR-0022 punto 5
   cierra). Hoy no es alcanzable solo porque el token original caducó; el reenvío lo vuelve alcanzable sin límite de
   tiempo. El punto (d) de la fila solo contempla el caso de la decisión 3 de BE-50. Leído, no probado con sonda.
2. **El registro ya revela si un correo o cédula existe** (`user_service.py:79-80`, 400 con texto distinto al 201).
   La exigencia (a) de que la ruta nueva no revele la existencia del correo es correcta pero no cierra la enumeración
   por sí sola; tampoco lo cubre SEC3 (l.156 del backlog, que habla de `str(e)` y del tiempo del login). Además, la
   ruta nueva puede filtrar por tiempo si solo las cuentas existentes generan token y programan correo (mismo patrón que
   SEC3 en el login).
3. **El login de una cuenta pendiente remite al correo** (`user_service.py:199`) cuyo enlace pudo caducar: el punto
   de entrada natural del reenvío en el cliente. Relacionado con BE-56 (texto del login), no con esta fila.

## Patrones de detección (copiables)
```bash
# 1. Emisores del token de verificación (hoy: 1 en app/, user_service.py:106; tras el arreglo: 2 o un helper común)
grep -rn "create_verification_token(" app --include=*.py
# 2. Sitios que programan el correo de verificación (hoy: 1, routers/user.py:71)
grep -rn "send_verification_email," app --include=*.py
# 3. Rutas de reenvío (hoy: 0 en app/; tras el arreglo: la ruta nueva)
grep -rn -i "resend\|reenv" app --include=*.py
# 4. Inventario de rutas públicas (hoy: registro, verificar-email, login en /usuarios)
grep -n "@public_router\." app/api/routers/user.py
grep -n -A 14 "^PUBLIC_ROUTES" tests/test_route_guards.py
# 5. Mensaje que promete el reenvío
grep -rn "solicite uno nuevo" app --include=*.py
# 6. Escritores de email_verified_at (hoy: solo user_service.py:163) y filas que nacen con la marca vacía
grep -rn "email_verified_at" app alembic --include=*.py
grep -rn "is_active=" app/services --include=*.py
# 7. Limitador de peticiones (hoy: 0)
grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml constraints.txt
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `b6a80ba` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop`; la rama `item/be-64` lleva encima solo commits de docs: `8600df0`, `cc043c9`).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (sin `--soft`; salida 0).

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
- pytest: `806 passed, 25 warnings in 35.22s` (0 failed).
- Cobertura total: `98.70%` (umbral 92,0 %).
- ruff format: `72 files already formatted`; ruff check: `All checks passed!` (0 errores).
- mypy: `Success: no issues found in 67 source files` (0 errores).
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas api | cli -> services -> repositories -> models KEPT; Los
  servicios no conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los
  modelos y los schemas no dependen de capas superiores KEPT).
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
Hay que añadir una ruta pública de reenvío en `public_router` que reutilice `create_verification_token` y el patrón de
`BackgroundTasks` de `/registro`, con respuesta idéntica exista o no la cuenta, y registrarla en `PUBLIC_ROUTES` y
`_ANONYMOUS_ON_PUBLIC_ROUTE`. El criterio de emisión no puede ser solo "marca vacía y no borrada": como mínimo
`role == tourist`, y el plan debe decidir (con David, por adenda) qué hacer con los turistas anteriores a la migración
que un admin desactivó, porque tienen la marca vacía y el reenvío los dejaría reactivarse (ADR-0022 punto 5; para
cuentas administrativas, ADR-0017). El tiempo mínimo entre envíos (punto (c)) exige columna nueva y migración Alembic, o
dejarlo fuera explícitamente; no hay limitador en la app. No tocar: la regla del enlace de ADR-0022 (`verify_email_account`),
el texto del login (BE-56), la activación manual (BE-63), la enumeración del registro y del login (SEC3), ni el cliente
Flutter si se cierra solo con backend (fila `FE-nn` ese día). Cambiar el texto de `user_service.py:141` es contrato visible:
solo si la decisión lo pide.

## Adenda — decisiones de David antes de planear (19 nov 2026, 17:44, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador toma estas decisiones como dadas; lo demás (fases, tests,
commits, nombres) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base aceptada:** `b6a80ba`, compuerta completa en verde
(806 passed · 98,70 % · ruff 0 · mypy 0 en 67 archivos · 4 kept).

Contraste de la sesión Mentor contra el código de `7789998`, sin correcciones de hecho sobre el código:
`app/services/user_service.py:80`, `:106`, `:141`, `:159-164`, `:199` y `:450-460`; `app/schemas/user.py:132`;
`app/models/user.py:51-58`. No se midió nada con sonda: el rincón 1 sigue "leído, no probado". **Una corrección de
cita:** las líneas 65 y 129 de este archivo atribuyen "la baja de un admin la decide un superadmin" a ADR-0017; esa
regla es de ADR-0019 (ADR-0017 trata solo de superadmins). Donde esta verificación dice ADR-0017 para una cuenta de
admin, léase ADR-0019.

### Decisiones

1. **Decidido (David, 17:23 y 17:44): a quién se le reenvía.** A una cuenta de **turista**, **no borrada** y con
   `email_verified_at` **vacía**, **esté activa o inactiva**. Las cuentas administrativas quedan fuera siempre, tengan
   la marca como la tengan: su alta y su baja las decide un superadmin (ADR-0019; ADR-0022, punto 7: no reciben
   enlace). **No se exige `is_active` en falso:** la sesión Mentor lo propuso y lo retiró (17:36). Un turista que un
   administrador activó a mano sin haber verificado `(backlog BE-63)` puede pedir el enlace; al usarlo solo se llena la
   marca (`user_service.py:162-164`: `is_active` ya era verdadero, no cambia nada más ni deja fila). Es la única vía
   para que esa cuenta llegue a tener su correo probado, que es lo que exigiría el modelo de dos hechos
   `(backlog BE-62)`. Razones de David (17:44, sus palabras): "está bloqueado o se puede bloquear desde el FE", y "si
   un admin activa un usuario es porque tiene la potestad jerárquica de poder hacerlo"; si no logra que inicie sesión,
   los administradores "no tienen total control" sobre los turistas que gestionan.
2. **Decidido (David, 17:23): riesgo aceptado, opción A.** Un turista anterior a la migración `e50a7c3d9b12` que
   verificó su correo y que un administrador desactivó después tiene la marca vacía y es indistinguible, por sus
   columnas, de uno que nunca usó su enlace: con el reenvío puede pedir un enlace y reactivarse (rincón 1, caso iii).
   David lo acepta porque ningún entorno tiene usuarios reales (palabra de David; la sesión Mentor no ve esas bases) y
   porque el modelo de dos hechos lo cierra de raíz cuando se haga `(backlog BE-62)`: allí el enlace deja de escribir
   `is_active`. Descartada la opción B (reenviar solo a cuentas con la hora de último envío llena): deja sin reenvío a
   todo turista pendiente anterior al despliegue, que es a quien el ítem quiere ayudar. **Dato:** en la base local de
   David, `SELECT count(*) FROM users WHERE role = 'tourist' AND is_active = false AND deleted_at IS NULL AND
   email_verified_at IS NULL;` dio **6** (captura de las 17:15); cuántas de las seis tocó un administrador no se
   midió. Purgar o no las bases antes de promover lo decide David en la puesta en `staging`.
3. **Decidido (David, 17:13 y 17:31): tiempo mínimo entre envíos, 60 segundos, sin tope total.** Entre dos envíos a
   la misma cuenta pasan al menos 60 s; no hay máximo de enlaces, porque un tope volvería a dejar la cuenta sin
   salida. El valor es un campo de `Settings` con 60 por defecto (ADR-0013: campo, línea en `.env.example` y valor
   en el `conftest.py` de la raíz). Pide guardar cuándo salió el último envío: **columna nueva en `users`** y su
   migración (nombres, del planificador; estilo de ADR-0010). Varios enlaces vigentes a la vez no son un riesgo: el
   primero que se usa llena la marca y los demás no cambian nada (ADR-0022). **Por qué 60 s:** ver "Fuentes".
4. **Decidido (David, 17:31): el registro cuenta como envío.** `POST /usuarios/registro` llena la misma columna, de
   modo que quien acaba de registrarse no puede pedir otro enlace hasta pasado el primer minuto.
5. **Decidido (David, 17:26 y 17:28): la ruta responde siempre lo mismo.** 200 con la misma forma que la
   verificación (`{"success": true, "message": …}`) y el mismo texto, exista o no la cuenta, esté verificada, sea
   administrativa, esté borrada o no haya pasado el tiempo mínimo. Texto, con la redacción de David ("le acabamos de
   enviar"): **"Si su correo tiene una cuenta pendiente de verificación, le acabamos de enviar un nuevo enlace. Revise
   su bandeja de entrada y la carpeta de correo no deseado. Si ya pidió uno hace poco, espere un minuto antes de
   intentarlo de nuevo."** Un cuerpo inválido (correo mal formado) sigue siendo 422: no revela nada de ninguna cuenta.
   El correo de entrada usa `LowercaseEmail` (ADR-0016). El texto del enlace caducado (`user_service.py:141`) no cambia.
6. **Decidido (David, 17:36): el reenvío no deja fila de auditoría**, "porque no es información relevante para el
   negocio". La marca de correo tampoco se audita (ADR-0022, punto 6) y la hora del último envío es un dato
   operativo. Descartada: una fila por reenvío, que llenaría el historial con cada clic.
7. **Decidido (David, 17:44): la diferencia de tiempo de respuesta se declara, no se cierra.** Rincón 2: solo una
   cuenta elegible genera token, escribe la columna y programa el correo, así que su respuesta puede tardar algo más.
   El correo ya sale en segundo plano (`BackgroundTasks`), lo que quita la mayor parte. Va como residual junto a
   `(backlog SEC3)`, que ya recoge el mismo patrón en el login; el registro sigue revelando si un correo o una cédula
   existen (`user_service.py:79-80`) y esta fila no lo toca: cerrar aquí lo que el registro dice abiertamente no
   protege nada.
8. **Decidido (David, 17:44): dos peticiones simultáneas pueden enviar dos correos, y se declara.** Sin bloqueo de
   fila, las dos leen la columna antes de que ninguna la escriba. David: "para un MVP en realidad es inofensivo y muy
   justificable". Mismo trato que los dos clics simultáneos de ADR-0022 (A3). No se añade bloqueo.
9. **Decidido (David, 17:36 y 17:44): alcance solo backend.** El ítem se cierra con la ruta, sus reglas y sus tests,
   sin tocar el cliente Flutter. La parte del cliente (el punto de entrada al reenvío, natural en la pantalla del
   enlace caducado y en el login de una cuenta pendiente) recibe su fila `FE-nn` y es lo primero que se hace cuando se
   toque el frontend, como David dijo a las 11:33. Hasta entonces el turista no puede pedir el enlace desde la
   aplicación.
10. **Fuera, sin cambios:** la regla del enlace (`verify_email_account`, ADR-0022); el texto del login
    `(backlog BE-56)`; la activación a mano `(backlog BE-63)`; el modelo de dos hechos `(backlog BE-62)`.

### Avisos para planear y ejecutar

- **El plan toca `app/models/user.py` y `alembic/`** (decisión 3). El PostgreSQL local de David está encendido
  (17:13). Los pasos de `alembic` contra la base local, antes y después de la fase que toque el modelo, los corre
  David desde `cmd`, no un agente (ADR-0010, punto 7).
- La migración escrita a mano la reescribe el hook de formato `(backlog AF-18)`: el ejecutor la restaura y lo declara,
  como en BE-50.
- Si Windows bloquea `_rustgrimp`, el ítem lleva una enmienda como la E1 de BE-50 `(backlog AF-17)`.
- Ruta nueva: en `PUBLIC_ROUTES` y `_ANONYMOUS_ON_PUBLIC_ROUTE` de `tests/test_route_guards.py` (ADR-0012, punto 4).
- La decisión pide ADR (ruta pública nueva, columna nueva, riesgo aceptado): el siguiente número libre es 0023.

### Fuentes (para el valor de 60 s)

Buscadas por la sesión Mentor el 19 nov (búsqueda web; extractos, no las páginas enteras). **Si el ADR las cita, el
planificador las lee antes** (regla del 14 nov: ninguna fuente externa se cita de memoria).

- Supabase Auth, "Rate limits" (`https://supabase.com/docs/guides/auth/rate-limits`): la petición de confirmación de
  registro se limita por la última petición del usuario, con una ventana por defecto de 60 segundos, configurable; lo
  mismo para el restablecimiento de contraseña y los enlaces mágicos. Es el valor por defecto de un producto de uso
  amplio, no una norma.
- OWASP, Forgot Password Cheat Sheet (`https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html`):
  pide protección contra envíos automatizados excesivos, por ejemplo límite por cuenta; no da ninguna cifra. Trata de
  la recuperación de contraseña: aplica por analogía.
- Ninguna fuente hallada fija 60 s como estándar: se elige por ser el valor por defecto documentado de Supabase y
  porque es mucho menor que la vida del enlace (15 min, `app/core/config.py:51`).

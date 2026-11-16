# Verificación — BE-36: superadmin recuperado por un par queda inactivo sin vuelta atrás

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-36, l.86) + rincón 3 de `docs/deuda/BE-02/verificacion.md` (l.89-91);
contexto: ADR-0017 (l.44) y adenda de `docs/deuda/BE-35/verificacion.md` ("Fuera de alcance, sin cambio", l.223-227)
**Fecha:** 2026-11-16

## Qué describe el ítem
Un superadmin recupera a otro superadmin de la papelera (`PATCH /usuarios/{cedula}/recuperar` → 200), la recuperación
fuerza `is_active=False`, y el `PATCH {"is_active": true}` entre pares da 403 por la regla jerárquica. El par queda sin
borrar pero inactivo y, sin SQL directo, no vuelve a entrar. La fila pide decidir: o la recuperación entre superadmins
reactiva, o la política permite `is_active` entre pares; y un test de ida y vuelta (recuperar → entrar).

## Evidencia en el código
Números de línea de la fila desfasados por BE-02 y BE-35; los actuales:

- `app/services/user_service.py:357-358` — la recuperación pone `target_user.deleted_at = None` y
  `target_user.is_active = False` para cualquier rol, sin excepción (la fila cita l.349).
- `app/services/user_service.py:332-334` — el docstring lo declara intencional: "forced into an inactive state
  (is_active=False) by default, requiring explicit administrative approval". Para un superadmin recuperado esa
  aprobación no existe en la aplicación.
- `app/services/user_service.py:374` — mensaje al cliente: `"Usuario recuperado. Se encuentra inactivo por seguridad."`
- `app/services/user_access_policy.py:110` — `assert_can_recover` solo rechaza a un admin que recupera admin o
  superadmin; un superadmin recupera a otro superadmin (la fila cita l.82).
- `app/services/user_access_policy.py:71` — `if not is_self_update and self._ROLE_RANK[actor.role] <= self._ROLE_RANK[target.role]`:
  entre pares 403 para cualquier clave, `is_active` incluida (la fila cita l.55).
- `app/services/user_access_policy.py:90-95` — la guarda de ADR-0017 sobre `is_active` es solo de auto-edición y solo
  para `False`; no cambia nada entre pares.
- `app/api/dependencies.py:144` — `if user is None or not user.is_active`: el recuperado recibe 401 con cualquier token.
- `app/services/user_service.py:169-170` — en el login, una cuenta inactiva lanza `AccountNotActiveError` ("Debe verificar
  su cuenta…"), 403 (`app/main.py:126`).
- `app/repositories/user_repository.py:54-64` — `activate_user(email)` es la única otra escritura de `is_active = True`
  sobre una cuenta existente; solo la llama `verify_email_account` (`user_service.py:141`) con un token de verificación,
  que solo emite el registro de turistas (`user_service.py:105`). No hay reenvío: no es una vía para el superadmin.
- `app/services/superadmin_bootstrap.py:26-27, 42-51` — el comando de operador no reactiva ni recupera: con otro
  superadmin activo no hace nada, y la cédula o el correo del recuperado ya existentes lo detienen.

**Medición por HTTP (16 nov, sonda en el scratchpad, pila real de la suite: `client`, `persist_user`,
`make_auth_headers`; nada en `tests/`).** Superadmin A activo; superadmin B sembrado borrado (`is_active=False`,
`deleted_at` puesto, como lo deja `soft_delete_user`):

```
A PATCH B (aún borrado) {"is_active": true}   -> 403
A PATCH /usuarios/B/recuperar                   -> 200  (B: deleted_at None, is_active False)
A PATCH B {"is_active": true}                   -> 403  (B sigue is_active False)
B POST /usuarios/login (contraseña correcta)    -> 403
B GET /usuarios/mi-perfil (token firmado)       -> 401
B PATCH B {"is_active": true} (token firmado)   -> 401
count_active_superadmins()                      -> 1   (solo A)
auditoría                                       -> una fila RECOVER sobre B
```

Controles (mismo mecanismo, otros roles, sin bloqueo): superadmin recupera admin → activa → login del admin:
200 · 200 · 200. Admin recupera turista → activa → login del turista: 200 · 200 · 200. El bloqueo es exclusivo del
caso superadmin → superadmin.

**Cómo llega hoy un superadmin a la papelera (efecto de BE-35 / ADR-0017), medido en la misma sonda:**

```
A DELETE A (propio)                  -> 403
A DELETE B (par)                     -> 403
admin DELETE A                       -> 403
A PATCH A {"is_active": false}       -> 403
A PATCH B {"is_active": false}       -> 403
```

Desde la aplicación ya no hay ninguna vía para que un superadmin quede borrado: la única escritura de `deleted_at`
sobre usuarios es `user_repository.py:83`, alcanzable solo por `delete_user_account`, que la política cierra para
cualquier superadmin objetivo. La precondición del ítem solo se da con SQL directo del operador (la baja que ADR-0017
y BE-55 dejan como único camino) o con filas borradas antes del merge de BE-35 (`09f529b`). La base de producción no
se midió.

## Ficheros afectados (mapa completo)
- `app/services/user_service.py` — `recover_user_account` (l.329-375): fuerza `is_active=False` (l.358), docstring
  (l.332-334) y mensaje (l.374) que prometen una aprobación posterior.
- `app/services/user_access_policy.py` — `assert_can_update` l.71 (403 entre pares, también para `is_active: true`);
  `assert_can_recover` l.97-113 (permite superadmin → superadmin); docstring de clase l.10-17 y de `assert_can_update`
  l.51-58 si cambia la regla entre pares.
- `app/api/routers/user.py` — docstring de `recuperar_usuario` (l.221-224); el contrato de la ruta no cambia en
  ninguna de las dos opciones.
- `tests/test_user_access_policy.py` — l.281-285 (`test_superadmin_can_recover_superadmin`, la política lo permite);
  l.162-167 (`test_superadmin_cannot_update_peer_superadmin`, con `first_name`; la opción "is_active entre pares" no debe
  ponerlo en rojo: solo se abre esa clave). No hay test HTTP de superadmin → superadmin en la recuperación.
- `tests/test_auth.py` — l.334-355 (`test_admin_recovers_tourist_as_inactive`) congela que la recuperación deja
  inactivo a un turista; l.358-377 (admin → superadmin, 403). Ninguna opción de la fila debe romperlos.
- `tests/test_user_service.py` — l.178-200, solo los 404 de la recuperación; no afectados.

## Rincones no mencionados por la fuente
1. **La precondición ya no se produce desde la aplicación (ADR-0017).** Ver arriba: el bloqueo está intacto, pero para
   llegar a él un operador tiene que haber borrado a un superadmin por SQL (o ser una fila anterior a BE-35). Quien lo
   borró por SQL puede restaurarlo por SQL; la ruta de recuperación es la que hoy lo deja a medias.
2. **El mensaje de login engaña al recuperado.** Un superadmin recuperado que intenta entrar recibe 403 con
   `AccountNotActiveError` ("Debe verificar su cuenta. Revise su correo…", `user_service.py:170`), pero nunca recibirá
   ese correo: no hay reenvío de verificación. Texto de usuario final; no se afirma sobre él, solo se constata la causa.
3. **El comando de operador tampoco sirve de salida** (`superadmin_bootstrap.py:26-27`): mientras A esté activo devuelve
   `None`; si no lo estuviera, la cédula/correo de B lo detendría con exit 1. Es coherente con ADR-0015, no deuda nueva.
4. **Fuera de alcance, no medido:** `update_user_account` lee el objetivo con `include_deleted=True`
   (`user_service.py:274`), de modo que un actor de rango superior puede editar una cuenta que sigue en la papelera.
   Entre superadmins lo cierra l.71 (medido: 403); para admin/turista no se midió. Si interesa, es fila nueva del backlog.
5. **Relación con la regla de AGENTS §3 (ADR-0017).** Ninguna de las dos opciones de la fila desactiva, borra ni degrada
   a un superadmin, así que no dispara por sí misma la exigencia de ADR que supersede a ADR-0017. Pero la opción
   "la política permite `is_active` entre pares", si lee la clave y no el valor, sí permitiría desactivar a un par: eso
   cae de lleno en la regla y exige ADR. Y en cualquier variante cambia la frase "entre pares nadie modifica a nadie"
   que recoge AGENTS §3 (l.59-60), y la "regla entre pares" en la que se apoya ADR-0017 (l.33).

## Patrones de detección (copiables)

```bash
# 1. La recuperación fuerza la cuenta a inactiva (hoy: user_service.py:358)
git grep -n -E "target_user\.is_active = False" -- app

# 2. Única escritura de is_active = True sobre una cuenta existente (hoy: user_repository.py:63, solo vía verificación de correo)
git grep -n -E "\.is_active = True" -- app

# 3. Regla jerárquica entre pares que bloquea el PATCH de reactivación (hoy: user_access_policy.py:71)
git grep -n -E "not is_self_update and self\._ROLE_RANK" -- app

# 4. Quién puede recuperar a quién (hoy: user_access_policy.py:97 y :110; user_service.py:354)
git grep -n -E "assert_can_recover|recover_user_account" -- app

# 5. Únicas escrituras de deleted_at sobre usuarios (precondición; hoy: user_repository.py:83 y user_service.py:357)
git grep -n -E "deleted_at\s*=[^=]" -- app/repositories/user_repository.py app/services/user_service.py

# 6. Tests que tocan la recuperación de usuarios (hoy: test_auth.py:334, :358; test_user_access_policy.py:266-299; test_user_service.py:178, :189)
git grep -n -E "recuperar|recover" -- tests/test_auth.py tests/test_user_access_policy.py tests/test_user_service.py
```

Comprobación de cierre por HTTP (la que debe convertirse en el test de ida y vuelta): superadmin A activo, superadmin B
sembrado con `deleted_at` y `is_active=False` → `PATCH /usuarios/{B}/recuperar` → (opción elegida) → `POST
/usuarios/login` con las credenciales de B → 200. Hoy da 403 en el login y 403 en el `PATCH {"is_active": true}`.

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `09f529b` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop` = `09f529bb…`; HEAD de `item/be-36` = `09f529b`, árbol limpio)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Python 3.14.3), exit 0

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

- pytest: `707 passed, 8 warnings in 31.32s` (0 failed)
- Cobertura total: `97.65%` (mínimo exigido 92.0%)
- ruff format: `68 files already formatted` · ruff check: `All checks passed!` (0 errores)
- mypy: `Success: no issues found in 63 source files` (0 errores)
- import-linter: `Contracts: 4 kept, 0 broken.`
- La compuerta no falla antes de tocar nada.

## Conclusión para el planificador
El mecanismo de la fila está intacto y medido por HTTP: recuperar a un superadmin lo deja `is_active=False`
(`user_service.py:358`) y el par no puede reactivarlo (`user_access_policy.py:71`, 403); login 403, token 401. El plan
resuelve solo el caso superadmin → superadmin, con la opción que decida David, y lo prueba con un test HTTP de ida y
vuelta (recuperar → entrar con 200) más sus fallos y bordes (admin → superadmin sigue 403; superadmin → admin y
admin → turista siguen dejando la cuenta inactiva salvo decisión en contra). No tocar: la recuperación de turistas
(`test_auth.py:334` la congela) ni la de admins, las guardas de ADR-0017 (l.47-48 y l.90-95), `activate_user`, el bootstrap
(ADR-0015), BE-37, BE-38, BE-55 ni A3 (`save_user` hace `commit()`). Riesgo: la opción "is_active entre pares" abre la
regla entre pares que AGENTS §3 describe y ADR-0017 da por supuesta ("entre pares nadie modifica a nadie"); si deja pasar `false` choca con
ADR-0017 y exige ADR que la supersede. La opción "la recuperación reactiva" solo toca el servicio y no baja el número
de superadmins, pero convierte la recuperación en reactivación inmediata sin segundo paso: dejarlo escrito (docstring y,
si David lo pide, ADR). Con ADR-0017 la precondición solo nace de SQL directo o de filas anteriores a BE-35; eso puede
bajar la severidad, no el veredicto.

## Adenda — decisiones de David antes de planear (16 nov 2026, 12:22, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador toma estas decisiones como dadas; lo demás (fases, tests,
commits, nombres) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base
aceptada:** `09f529b`, compuerta completa en verde (707 passed · 97,65 % · ruff 0 · mypy 0 en 63 archivos · 4 kept).
Severidad: Media, la de la fila (el rincón 1 la habría bajado; el hecho de abajo la sostiene).

Contraste de la sesión Mentor contra el código, sin correcciones de hecho: `user_access_policy.py:66-72, 97-113`,
`user_service.py:329-375, 392-420`, `user_repository.py:54-64`, `schemas/user.py:128-130`.

### Un hecho que la verificación no trae: la otra puerta al mismo callejón (leído, no ejecutado)

`app/schemas/user.py:130` declara `is_active: bool = False` en `UserCreateByAdmin`, el schema de `POST /usuarios/admin`,
y `create_administrative_account` crea la cuenta con `is_active=user_data.is_active` (`user_service.py:416`, en el `User(...)` de esa
función). Si un superadmin provisiona a otro superadmin sin enviar `is_active`, la cuenta nace inactiva; el `PATCH
{"is_active": true}` del creador da 403 por la misma l.71, y el nuevo no puede entrar. Es el mismo fondo que la fila
(**un superadmin inactivo no tiene a nadie por encima que lo active**) por una puerta que, a diferencia de la
recuperación, sigue abierta desde la aplicación tras ADR-0017. La sesión Mentor lo leyó; no pudo ejecutarlo.

### Decisiones (David, "sí a las 6")

1. **Regla: un superadmin puede reactivar a otro superadmin, y nada más.** Excepción única a la regla entre pares de
   `assert_can_update` (l.71): actor superadmin, objetivo superadmin, y el conjunto de cambios es **exactamente**
   `{"is_active": true}`. Cualquier otra clave entre pares, sola o acompañando a `is_active`, sigue dando 403; `false`
   sigue dando 403 (ADR-0017 no se toca: la excepción no baja el número de superadmins). No se abre entre admins.
   De las dos opciones de la fila es la segunda, acotada por valor; la primera ("la recuperación reactiva") se descarta
   porque no cubre la puerta de la provisión.
2. **La recuperación no cambia:** sigue dejando inactiva la cuenta para cualquier rol, en dos pasos (recuperar; después
   activar). `tests/test_auth.py:334` no se toca. El test de ida y vuelta de la fila es: recuperar → el par reactiva →
   el recuperado entra (login 200).
3. **El planificador mide primero la puerta de la provisión con una sonda** (superadmin A crea superadmin B por
   `POST /usuarios/admin` sin `is_active` → estado de B; A `PATCH {"is_active": true}` sobre B; login de B), antes de
   dictar. Si se reproduce, entra en los tests del ítem como segundo camino (provisionar → reactivar → entrar). Si no se
   reproduce, lo dice y el ítem se queda con la puerta de la papelera. El valor por defecto `False` del schema **no se
   cambia** en este ítem.
4. **ADR-0018, corto, dictado por el planificador:** la excepción a la jerarquía, por qué se acota a esa clave y a ese
   valor, y la consecuencia que David acepta: si un operador desactiva por SQL a un superadmin (la baja de ADR-0017),
   otro superadmin puede reactivarlo desde la aplicación; una baja que deba ser definitiva no puede consistir solo en
   `is_active = false` (dato para BE-55). Debe decir cómo queda la premisa de ADR-0017 ("entre pares nadie modifica a
   nadie"): sigue siendo cierta para desactivar, borrar y degradar.
5. **AGENTS §3:** la viñeta "Superadmins (ADR-0017)" pasa a decir que entre pares nadie modifica a nadie **salvo que un
   superadmin reactiva a otro (ADR-0018)**. La edita David antes de `/pr`; el plan no toca `AGENTS.md`.
6. **Fuera de alcance, con fila nueva cada uno:** el mensaje de login que remite al correo de verificación a una cuenta
   inactiva que nunca lo recibirá (rincón 2) → **BE-56**; la edición de cuentas que siguen en la papelera (rincón 4,
   sin medir) → **BE-57**. David: "una cuenta inactiva no debería poderse editar".

### Lo que el plan debe vigilar con tests (bordes de la excepción)

Entre superadmins: `{"is_active": true}` → 200; `{"is_active": false}` → 403; `{"is_active": true, "first_name": …}` →
403 sin mutación; `{"first_name": …}` → 403 (`tests/test_user_access_policy.py:162-167` sigue en verde);
`{"role": …}` → 403. Entre admins: `{"is_active": true}` → 403. Superadmin sobre un superadmin **aún en la papelera**:
decidirlo y medirlo (hoy 403; el objetivo se lee con `include_deleted=True`, `user_service.py:274`): recomendación de
la sesión Mentor, que siga en 403, para que reactivar no sea una forma de saltarse la recuperación ni su auditoría.

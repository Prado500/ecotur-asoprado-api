# Verificación — BE-58: un admin puede borrarse o desactivarse a sí mismo

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-58, l.109; celda de `B-GHOST-ADMIN` en `docs/PLAN.md:100`) + E1.3 de
`docs/deuda/BE-36/plan.md` (l.882-885) + bitácora `docs/bitacora/2026-11-16.md` (l.211-221, decisiones de David de las
15:35 y 15:38); contexto: ADR-0017, ADR-0018, ADR-0009 y la viñeta "Superadmins" de `AGENTS.md:59-62`
**Fecha:** 2026-11-16

## Qué describe el ítem
Un admin puede sacarse a sí mismo de la plataforma por las dos vías de autoservicio que ADR-0017 cerró solo para
superadmins: `DELETE /usuarios/{su cédula}` y `PATCH /usuarios/{su cédula}` con `{"is_active": false}`. David decidió
(16 nov, 15:35) que solo un superadmin decide la baja de una cuenta administrativa; los turistas conservan el borrado
de su propia cuenta. La fila pide un ADR nuevo que extienda ADR-0017 e invertir los dos tests de BE-35 que congelan
hoy lo contrario.

## Evidencia en el código
Política (`app/services/user_access_policy.py`, HEAD `6b168e1`):

- `:40` — `is_self_deletion = actor.cedula == target.cedula`; `:43` — el 403 jerárquico solo salta si **no** es auto-borrado
  y el actor no supera en rango al objetivo: todo auto-borrado pasa esta guarda.
- `:49-50` — `if is_self_deletion and actor.role == UserRole.superadmin:` → la única excepción al auto-borrado es de
  superadmins (ADR-0017). Un admin la atraviesa.
- `:73` y `:83-90` — `is_self_update` exime de la regla de rango a toda auto-edición.
- `:100-104` — `if "is_active" in update_dict and actor.role == UserRole.tourist:` → la clave `is_active` solo se
  prohíbe a turistas (sobre sí o sobre otros); un admin puede enviarla.
- `:106-111` — `is_self_update and actor.role == UserRole.superadmin and update_dict.get("is_active") is False` → la
  guarda de auto-desactivación es solo de superadmins y lee el valor (`True` pasa, `None` no la dispara).
- Docstrings que describen la regla actual: `:10-16` ("an actor may update or delete their own account … a superadmin
  never deletes or deactivates it"), `:27-29`, `:36-38`, `:55-62`.

Servicio y rutas:

- `app/services/user_service.py:206` — `self.user_access_policy.assert_can_delete(current_user, soft_deleted_user)`;
  `:209` — `soft_delete_user`; `:212-217` — fila de auditoría `SOFT_DELETE` con `performed_by` del propio admin.
- `app/services/user_service.py:286` — `assert_can_update(...)`; `:289-290` — `setattr` de cada clave enviada, después de
  la política (un 403 no muta nada).
- `app/repositories/user_repository.py:83-84` — el borrado lógico pone `deleted_at` y `is_active = False`.
- `app/api/routers/user.py:127` — `@self_service_router.delete("/{cedula}")` y `:148` — `@self_service_router.patch("/{cedula}")`:
  las dos rutas están bajo el guard de "usuario autenticado" (`:33`), no de admin; la regla solo puede vivir en la política.
- `app/api/dependencies.py:144` — `if user is None or not user.is_active: raise credentials_exception`: desde el 200, el
  token del admin recibe 401.
- `app/schemas/user.py:181` — `is_active: bool | None = None` en `UserUpdate`: `null` llega a la política (BE-37).
- Docstrings con la regla actual: `app/api/routers/user.py:132-135`, `app/services/user_service.py:179-183, 194-195, 205,
  253-259`.

Tests que congelan hoy el comportamiento contrario (medido, ver "Sonda"):

- `tests/test_user_access_policy.py:71-74` — `test_be35_admin_self_delete_is_still_allowed`: `policy.assert_can_delete(admin, admin)` sin excepción.
- `tests/test_user_access_policy.py:255-258` — `test_be35_admin_self_deactivation_is_still_allowed`: `policy.assert_can_update(admin, admin, {"is_active": False})` sin excepción.
- **No hay ningún otro.** Con la regla de BE-58 inyectada por monkeypatch en la política (solo admin, solo auto-borrado y
  auto-`is_active` `False`), la suite entera da `2 failed, 724 passed` y los dos fallos son exactamente estos. No existe
  ningún test HTTP de un admin que se borre o se desactive a sí mismo: ni a favor ni en contra.

Tests que protegen lo que **no** debe cambiar (medido con una regla demasiado amplia, auto-borrado prohibido a todos):

- `tests/test_auth.py:168` — `test_self_soft_delete_keeps_row_and_blocks_login` (turista se borra a sí mismo → 200).
  La fila cita `:167`; el `def` está en la l.168.
- `tests/test_user_access_policy.py:41-44` — `test_self_delete_tourist_is_allowed`.
- Con esa regla amplia: `4 failed, 722 passed` (los dos de arriba más los dos de BE-35).
- `tests/test_user_access_policy.py:513` — `test_b2_admin_self_update_without_role_returns_200`: un admin edita su perfil
  (`first_name`) → 200; la regla no debe tocarlo.

### Sonda (pila real de la suite, fuera de `tests/`)
Scripts en el scratchpad de la sesión (`probe_be58.py`, `probe_be58_email.py`, `be58_rule_plugin.py`,
`be58_overbroad_plugin.py`), ejecutados con
`./venv/Scripts/python.exe -m pytest -c pyproject.toml --rootdir . -p conftest -p tests.conftest <ruta> -s --no-cov`.
Salida literal, código actual:

```
P1 admin self PATCH is_active false -> 200 is_active: False deleted_at: None audits: [('UPDATE', '1000000000', '1000000000', {'is_active': False})]
P1 same token GET mi-perfil -> 401
P1 login -> 403
P1 superadmin reactivates -> 200 | login after -> 200
P2 admin self DELETE -> 200 is_active: False deleted_at set: True audits: [('SOFT_DELETE', '1000000002', '1000000002', None)]
P2 same token GET mi-perfil -> 401 | login -> 401
P2 another admin recovers -> 403
P2 superadmin recover -> 200 | reactivate -> 200 | login -> 200
P3 admin self PATCH {'is_active': True} -> 200 is_active: True first_name: John
P3 admin self PATCH {'is_active': None} -> 409 is_active: True first_name: John
P3 admin self PATCH {'is_active': False, 'first_name': 'Changed'} -> 200 is_active: False first_name: Changed
P4 admin reactivates peer admin -> 403
P4 tourist self PATCH is_active false -> 403 | tourist self DELETE -> 200
P4 superadmin deactivates admin -> 200 | deletes admin -> 200
P5 admin self email change -> 200 | old token -> 401 | login with new email -> 200
```

Lectura: las dos vías dan 200 y dejan auditoría con el propio admin como autor; su token muere (401) y el login da 403
(desactivado: `AccountNotActiveError`, `app/main.py:126`) o 401 (borrado: `get_non_deleted_user_by_email` no lo
encuentra). Otro admin no puede rescatarlo (reactivar 403 por la regla entre pares, recuperar 403 por
`assert_can_recover`, `user_access_policy.py:126`); un superadmin sí, desde la aplicación (200 · 200 · 200), como
anticipaba la nota del Mentor en la fila. Un `PATCH` que mezcla `is_active: false` con otro campo muta los dos.

Misma sonda con la regla inyectada por monkeypatch (solo para medir; no es una propuesta de implementación): P1 y P2 →
403 sin mutación ni auditoría y el token sigue vivo (200); P3 mixto → 403 y `first_name` intacto; `{"is_active": true}`
→ 200; `null` → 409 (sin cambio); turista y superadmin sobre admin, sin cambio.

## Ficheros afectados (mapa completo)
- `app/services/user_access_policy.py` — donde vive la regla: `assert_can_delete` (`:40-50`) y `assert_can_update`
  (`:73-111`) solo exceptúan al superadmin; docstrings de clase y métodos describen la regla vigente.
- `app/services/user_service.py` — docstrings de `delete_user_account` (`:179-195`), comentario `:205` y docstring de
  `update_user_account` (`:253-259`) que enumeran las guardas; la lógica no cambia (delega en la política).
- `app/api/routers/user.py` — docstring de `eliminar_usuario` (`:132-135`) que nombra la excepción de superadmin.
- `tests/test_user_access_policy.py` — los dos tests que congelan lo contrario (`:71-74`, `:255-258`); sección B sin
  casos HTTP de admin sobre sí mismo para las dos vías.
- `docs/adr/` — ADR nuevo (la fila lo exige; ADR-0017 `:41-42` dice "Turistas y admins no cambian").
- `AGENTS.md:59-62` — la viñeta "Superadmins" solo nombra superadmins; si la regla se extiende, la viñeta (o una nueva) la
  edita David, no un agente.

## Rincones no mencionados por la fuente
1. **Ningún test HTTP cubre hoy a un admin que se borra o se desactiva a sí mismo.** Solo los dos unitarios de la
   política. Los casos de superadmin tienen su gemelo HTTP (`tests/test_user_access_policy.py:839-978`); los de admin no.
2. **`{"is_active": null}` sobre uno mismo da 409, no 403** (P3; `app/schemas/user.py:181` + NOT NULL de la base). Si la
   guarda nueva lee el valor como la de ADR-0017 (`is False`), `null` no la dispara y sigue siendo BE-37; el mutante
   "tratar `None` como desactivación" sobreviviría igual que M6 de BE-35 (fila BE-37).
3. **Un `PATCH` mixto (`is_active: false` + campo de perfil) hoy muta los dos** (P3). La política corre antes de
   `setattr` (`user_service.py:286-290`), así que una guarda en la política rechaza la petición entera; conviene que un
   test lo congele (el molde existe para superadmin en B2/BE-02).
4. **Docstrings** de la política, el servicio y el router dicen literalmente que "an actor may update or delete their own
   account" con la sola excepción del superadmin (citas arriba): quedan falsos si cambia la regla.
5. **Cambiar el propio correo también deja muerto el token** (P5: 200 → 401 con el token viejo), porque `sub` es el
   correo; no es una baja (el login con el correo nuevo da 200) y no está en el alcance de la fila. Se anota para que el
   plan no lo confunda con BE-58.
6. Cifra de la fila: el test del turista está en `tests/test_auth.py:168`, no `:167`.

## Patrones de detección (copiables)
```bash
# Guardas de auto-borrado y auto-desactivación: hoy solo superadmin
git grep -n "is_self_deletion and actor.role\|is_self_update$\|update_dict.get(\"is_active\") is False" -- app/services/user_access_policy.py
# Tests que congelan el comportamiento contrario (deben desaparecer o invertirse)
git grep -n "test_be35_admin_self_delete_is_still_allowed\|test_be35_admin_self_deactivation_is_still_allowed" -- tests
# Tests que protegen el borrado propio del turista (deben seguir en verde)
git grep -n "test_self_soft_delete_keeps_row_and_blocks_login\|test_self_delete_tourist_is_allowed" -- tests
# Docstrings que describen la regla vigente
git grep -n "own account" -- app
# Casos HTTP de admin que se borra o se desactiva a sí mismo (hoy: ninguno)
git grep -n "async def test_.*_admin_self_\(delet\|deactiv\)" -- tests
# Referencias a ADR-0017 en código, tests y reglas
git grep -n "ADR-0017" -- app tests AGENTS.md
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `6b168e1` (`git fetch origin` sin errores; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `6b168e1b424a79d7894b05f9cc992e709863f230`; árbol limpio)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (salida 0)

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

- pytest: `726 passed, 8 warnings in 32.38s` (0 failed)
- Cobertura total: `TOTAL 1039 15 152 13 97.65%` (`Required test coverage of 92.0% reached. Total coverage: 97.65%`);
  `app/services/user_access_policy.py` al 100 % (entre los 30 archivos omitidos por cobertura completa)
- ruff: `68 files already formatted` · `All checks passed!` (0)
- mypy: `Success: no issues found in 63 source files` (0)
- import-linter: `Contracts: 4 kept, 0 broken.`
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
El plan debe cerrar las dos vías para el rol admin en `UserAccessPolicy` (auto-borrado en `assert_can_delete`,
auto-`is_active` `false` en `assert_can_update`), con 403 `AuthorizationError` y sin mutación ni auditoría, e invertir
`test_be35_admin_self_delete_is_still_allowed` y `test_be35_admin_self_deactivation_is_still_allowed` (son los dos
únicos que caen, medido); faltan casos HTTP de admin sobre sí mismo (las dos vías, el `PATCH` mixto, `{"is_active": true}`
→ 200, token vivo tras el rechazo). **No debe tocar:** el borrado propio del turista (`tests/test_auth.py:168`,
`test_user_access_policy.py:41`), la edición de perfil propia del admin (`:513`), lo que un superadmin hace sobre un admin
(200 · 200, y el rescate 200 · 200 · 200), ADR-0018, BE-37 (`null` → 409) ni BE-38. El ADR va antes que el código y
tiene que resolver su relación con ADR-0017, cuya consecuencia "Turistas y admins no cambian" (`:42`) contradice; los
docstrings de política, servicio y router cambian con la regla. Riesgo: una guarda escrita sobre "no superadmin" en vez
de "admin" alcanzaría al turista; los dos tests de turista la detectan (medido: `4 failed`).

## Adenda — decisiones de David antes de planear (16 nov 2026, 18:02, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador toma estas decisiones como dadas; lo demás (fases, tests,
commits, nombres) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base
aceptada:** `6b168e1`, compuerta completa en verde (726 passed · 97,65 % · ruff 0 · mypy 0 en 63 archivos · 4 kept).
Severidad: Media, la de la fila.

Contraste de la sesión Mentor contra el código, sin correcciones de hecho más allá de la que el cuerpo ya trae (el test
del turista está en `tests/test_auth.py:168`): `user_access_policy.py:40-50, 98-111`,
`tests/test_user_access_policy.py:71-74, 255-258`, `docs/adr/0017-…:41-42`.

### Decisiones (David, "sí a las 6")

1. **A quién alcanza: a todo actor que no sea turista.** La guarda se escribe sobre "el actor no es turista", no sobre
   "es admin o superadmin": un rol que se añada mañana queda bloqueado hasta que alguien decida abrirlo. La regla de
   David es "solo el superadmin decide cuándo se da de baja una cuenta administrativa". Los turistas conservan el
   borrado de su propia cuenta (`tests/test_auth.py:168`, `tests/test_user_access_policy.py:41-44`) y siguen sin poder
   tocar su `is_active` (guarda de `:100-104`, sin cambio).
2. **Una sola guarda por vía.** Las dos guardas de ADR-0017 (`:49-50` auto-borrado; `:106-111` auto-desactivación) se
   amplían; no se añade una segunda para el admin. La de `is_active` sigue leyendo el valor: `false` → 403, `true`
   pasa, `null` sigue siendo BE-37 (el mutante "tratar `None` como desactivación" seguirá vivo y declarado, como M6 de
   BE-35). 403 con `AuthorizationError`; sin excepción nueva; la política sigue pura, síncrona y con la misma firma.
3. **Texto de los dos avisos (usuario final; lo decide David, los tests no afirman sobre él):**
   `"Una cuenta administrativa no puede eliminarse a sí misma. Solicítelo a un superadministrador."` y
   `"Una cuenta administrativa no puede desactivarse a sí misma. Solicítelo a un superadministrador."`. Sustituyen a
   los dos textos de BE-35 ("Un superadministrador no puede…"). El planificador mide las columnas antes de dictarlos.
4. **ADR-0019, dictado por el planificador, supersede parcialmente a ADR-0017:** solo la consecuencia "Turistas y
   admins no cambian" (`0017:42`) y el alcance "superadmin" de sus dos guardas; el resto de ADR-0017 (el número de
   superadmins no baja desde la aplicación; coste de la baja por SQL; BE-55) sigue vigente, y ADR-0018 no se toca.
   Precedente de forma: ADR-0006 respecto de ADR-0003. La línea "Estado" de ADR-0017 anota la supersesión parcial
   (única edición admitida en un ADR aceptado). El ADR declara la razón que sostiene la regla (quién decide la baja de
   una cuenta administrativa) y **no** la de "quedan varados hasta que alguien entre a la base": la sonda P1 y P2 del
   cuerpo mide que un superadmin rescata a un admin desde la aplicación (200 · 200 · 200).
5. **Tests HTTP de un admin sobre sí mismo** (hoy no hay ninguno; rincón 1): `DELETE` propio → 403 sin mutación ni
   auditoría; `PATCH {"is_active": false}` propio → 403 sin mutación ni auditoría; `PATCH` mixto
   (`is_active: false` más un campo de perfil) → 403 y ningún campo cambia (rincón 3); `{"is_active": true}` propio →
   200; tras un rechazo, el mismo token sigue sirviendo (`GET /usuarios/mi-perfil` → 200); y lo que no debe cambiar: un
   superadmin sigue desactivando y borrando a un admin (200 · 200), y un admin sigue editando su perfil
   (`tests/test_user_access_policy.py:513`). Los dos tests de BE-35 que congelan lo contrario (`:71-74`, `:255-258`) se
   invierten. Los mutantes M1 y M5 de BE-35, que morían gracias a esos dos tests, se vuelven a definir y a medir.
6. **Fuera de alcance:** el rincón 5 (cambiar el propio correo deja muerto el token porque el token lleva el correo;
   no es una baja) recibe **nota en la fila FE-01**, no fila nueva. `AGENTS.md` no lo toca el plan: la viñeta de §3 la
   edita David después de la última auditoría y antes de `/pr`. BE-37, BE-38, BE-55, BE-56, BE-57: sin cambio.

# PLAN — BE-02: Impedir que un superadmin cambie su propio rol

> Fuente: `docs/deuda/BE-02/verificacion.md` (confirmada, con adenda, commit `dbdcbf5`). Base develop: `c6422ed`.
> Estado: **aprobado por David el 5 nov 2026, con enmiendas (decisiones 1, 2 y 4; residuales 1, 2 y 5).**

## Resumen para aprobación

Hoy un superadmin puede enviar `PATCH /usuarios/{su cédula}` con `{"role":"tourist"}`: responde 200, pierde el rango
con efecto inmediato y, si era el único, nadie puede restaurarlo sin SQL directo. En una sola fase, el plan añade una
guarda en `UserAccessPolicy.assert_can_update`: si el actor se edita a sí mismo y el payload trae la clave `role`, 403.
Solo cambia la respuesta del superadmin: turista y admin ya reciben 403, y el superadmin sigue cambiando roles ajenos y
su propio perfil. Corrige los tres docstrings que prometen lo contrario y añade 19 casos de test (10 en rojo antes de
la guarda). **Bloqueo por clave, decidido por David** (decisión 1). **Trinquete con excepción, aprobado por David**
(decisión 2): ADR-0005 pide cero errores en archivos tocados y estos dos archivos heredan 15 de ruff y 3 de mypy de
BE-33 y A4; el plan exige no añadir ninguno, no limpiarlos.
**Riesgo principal:** creer que esto garantiza que siempre quede un superadmin: `is_active:false` y la auto-eliminación
siguen abiertas (BE-35). **No se toca:** esquema, `UserUpdate`, router, guardas existentes, BE-34 a BE-38 ni el backlog. Sin ADR.

## Objetivo y decisiones bloqueadas

Objetivo: que ninguna cuenta pueda enviar la clave `role` sobre sí misma, superadmin incluido, sin alterar ningún otro
resultado de la política.

1. **Bloqueo por clave (decisión de David: adenda de `verificacion.md`, punto 2, commit `dbdcbf5`).** El payload de una
   auto-edición con la clave `role` da 403, aunque el valor sea el rol actual. Coherente con `user_access_policy.py:60` y
   con `test_b2_admin_self_role_noop_returns_403`, que no se toca. La variante por valor queda descartada.
2. **Trinquete con excepción, aprobado por David; forma de BE-01 (decisión 6 de su plan).** ADR-0005 dice
   "cero errores de `ruff` y `mypy` en los archivos tocados"; los rituales de `fase-ejecutor` y `handoff-auditor`
   también, y el auditor lo marca BLOQUEANTE. La adenda (punto 6) y la conclusión de la verificación lo leen como "solo
   no añadir". Para este plan, y **prevaleciendo sobre esos rituales**:
   - `app/services/user_access_policy.py`: exactamente los errores de la línea base menos la D205 de l.40 (9 → **8**:
     D205 ×5, E501 ×3). Dueño: BE-33.
   - `app/services/user_service.py`: el mismo conjunto de errores en las mismas líneas: ruff **6** (I001 l.1, E501 l.46,
     217 y 337, B904 l.126 y 130), mypy **3** (l.124, 132, 133). Dueños: A4 y BE-33.
   - `tests/test_user_access_policy.py`: ruff **0**, como hoy.
   - Totales: ruff **53**, mypy **10**. Igual conteo con otro error distinto es BLOQUEANTE.
3. La guarda nueva va **después** de la de l.60: turista y admin conservan su `detail` actual letra a letra.
4. **`user_service.py` se edita con Edit normal (enmienda de David).** `unfixable = ["I001"]` ya está en
   `[tool.ruff.lint]` de `pyproject.toml` (commit `a120cae`, anterior a esta fase y fuera de su diff): I001 se sigue
   reportando, pero el hook de edición ya no reordena los imports. Medido el 5 nov: `ruff check --fix --diff` no propone
   cambios en los tres archivos de la fase. El motivo sigue vigente: reordenarlos cambia el orden de carga y
   `import app.services.user_service` como primer import deja `SECRET_KEY` en `None` (de A4). Sigue sin usarse
   `scripts/check.py --fix`. El hook sale con código 2 al editar la política (8 errores) y `user_service.py` (6): son los
   de la decisión 2 y **no se corrigen**.
5. Compuerta y herramientas siempre con `./venv/Scripts/python.exe`, nunca `python` a secas (AGENTS §6). Este punto
   prevalece sobre el `python …` literal de los rituales.

## Análisis del redactor

**Qué y por qué.** Contrastado en el código: la guarda de jerarquía (l.55) se salta en auto-edición y la de rol (l.60)
solo mira el rango del actor; `user_service.py:279` aplica el payload sin más filtros. La combinación superadmin + sí
mismo + `role` no la detiene nada. Basta una condición, y `is_self_update` ya existe (l.53).

**Docstrings: los tres declaran la paridad sin excepción.** `user_access_policy.py:10-12` ("may always act on their
own"), `:39-42` ("self-update parity", y limita la guarda de rol a "non-superadmins"; el patrón 5 de la verificación no
lo detecta, por eso la verificación final lo amplía) y `user_service.py:247-251` ("self-updates are always permitted").
No se tocan `user_access_policy.py:20` ni `user_service.py:178,201`, que hablan de borrado y siguen siendo ciertos, ni
el docstring del router (`routers/user.py:154-157`), que no promete paridad.

**Orden.** Una sola fase: regla y docstrings deben cambiar en el mismo commit o el código queda mintiendo; son 3 archivos
de 1 dominio.

**Tests que congelan comportamiento relacionado; ninguno cambia.** `test_b2_admin_self_role_noop_returns_403` (por
clave, admin); `test_tourist_self_role_escalation_…` en `test_auth.py`; `test_superadmin_can_mutate_role`;
`test_superadmin_cannot_update_peer_superadmin`; `test_superadmin_self_delete_is_allowed` (rincón 2, sigue abierto). El
plan **no** congela `{"is_active": false}` sobre sí mismo, para no estorbar a BE-35.

**¿ADR? No.** No hay patrón ni módulo nuevo: misma política, misma excepción, mismo 403 ya presente en esta ruta. La
"self parity" no es una decisión registrada: no aparece en `docs/adr/` ni en `AGENTS.md`, solo en esos docstrings, así
que no hay principio que superseder. El cambio 200 → 403 es el defecto que pide la fila del backlog, no un contrato
nuevo, y en la copia local del cliente ningún `PATCH` envía `role`. La decisión queda trazada en la adenda, este plan y
los tests. Pasaría a requerir ADR la regla "siempre queda un superadmin" (BE-35), que no es de este plan.

**Riesgos.** (a) Leer esto como garantía de gobernanza: ver el resumen. (b) Efecto colateral por clave: `{"role": null}`
sobre sí mismo pasa de 409 a 403; sobre un tercero sigue en 409 (medido). No es arreglar BE-37: es consecuencia directa
de la regla. (c) Si cae un test existente, el cambio tocó algo más: medido, los 396 siguen en verde.

**Sonda de este plan** (copia desechable de `HEAD` fuera del repo, con variables de entorno ficticias): línea base
reproducida (396, 94.81 %); con los tests sin la guarda, `10 failed, 405 passed`; con todo, `415 passed`, 94.82 %, ruff
53, mypy 10, 4 KEPT, formato limpio.

## Regla de alcance

**Sí:** la guarda, los tres docstrings y sus tests. **No:** rincones BE-34 (bootstrap), BE-35 (`is_active:false` y
auto-eliminación), BE-36 (superadmin recuperado sin activación), BE-37 (`{"role": null}` da 409), BE-38 (auditoría de
claves enviadas); `app/schemas/user.py`; `app/api/`; `alembic/`; los errores heredados de la decisión 2; `docs/backlog.md`.

## Fases

**Precondición:** `plan.md` y `progress.json` commiteados; el ritual de arranque de `fase-ejecutor` se detiene con el
árbol sucio.

### Fase A — Guarda de auto-edición de rol, docstrings y tests

- **Archivos (3):** `tests/test_user_access_policy.py`, `app/services/user_access_policy.py`,
  `app/services/user_service.py`.
- **Cambios exactos:**
  1. Política, tras el bloque de l.60-63 y antes del de `is_active`:
     ```python
     if is_self_update and "role" in update_dict:
         raise AuthorizationError("Violación de jerarquía: No puede modificar su propio rol.")
     ```
  2. Docstring de clase, sustituye las l.10-12 por:
     ```text
     All guarded mutations follow a hierarchical dominance invariant over role
     ranks: an actor may act on their own account, while third-party operations
     require a strictly higher rank. One exception: nobody changes their own
     role, superadmins included.
     ```
  3. Docstring de `assert_can_update`, sustituye las l.40-42 por (retira la D205 de l.40):
     ```text
     """Enforces the invariants of a partial update on a user account.

     The target must be the actor's own account or one of strictly lower rank.
     Fail-safe guards then reject the role key for non-superadmins and on any
     self-update, and the is_active key for tourists. The role guards read the
     key, not its value: resending the current role is rejected too.
     ```
  4. `user_service.py`, con Edit normal (decisión 4); sustituye las l.248-251 por:
     ```text
     account deletion: an actor may edit their own account, while third-party
     updates require the actor's role rank to be strictly greater than the
     target's role rank. Fail-safe invariants additionally block the role key
     for non-superadmins and on any self-update, and is_active for tourists.
     ```
- **Tests (RED primero).** Todos con prefijo `test_be02_`: 19 casos, 10 funciones. Fábricas de `conftest.py`, sin texto
  en español. Unitarios (síncronos) al final de `TestAssertCanUpdate`; HTTP en un bloque nuevo antes del de B3, con el
  comentario `# --- BE-02 regression: nobody changes their own role, superadmin included ---`. HTTP según ADR-0011:
  `refresh` tras la petición.

  | Test | Entrada | Esperado | Antes de la guarda |
  |---|---|---|---|
  | `test_be02_nobody_can_send_own_role` (parametrizado `actor_role` × `new_role`, `list(UserRole)`, 9 casos) | `assert_can_update(actor, actor, {"role": new_role.value})` | `AuthorizationError` | 3 rojos (superadmin), 6 verdes |
  | `test_be02_superadmin_self_update_with_role_none_is_rejected` | `(superadmin, superadmin, {"role": None})` | `AuthorizationError` | rojo |
  | `test_be02_self_role_guard_identifies_the_actor_by_cedula` | `(superadmin, twin, {"role": "tourist"})`, dos instancias con la misma cédula | `AuthorizationError` | rojo |
  | `test_be02_superadmin_self_update_profile_fields_is_allowed` | `(superadmin, superadmin, {"first_name": "Updated"})` | no lanza | verde |
  | `test_be02_superadmin_self_role_change_returns_403_without_mutation` (`new_role`: `tourist`, `admin`) | PATCH propio `{"role": new_role}` | 403; `set(body) == {"detail"}`; `detail` es `str`; rol intacto; `AuditLog` vacío | 2 rojos |
  | `test_be02_superadmin_self_role_noop_returns_403` | PATCH propio `{"role": "superadmin"}` | 403; `{"detail"}`; rol intacto; `AuditLog` vacío | rojo |
  | `test_be02_superadmin_self_role_with_profile_fields_mutates_nothing` | PATCH propio `{"role": "tourist", "first_name": "Changed"}` | 403; `{"detail"}`; `first_name == "John"`; rol intacto | rojo |
  | `test_be02_superadmin_keeps_powers_after_rejected_self_demotion` | PATCH propio `{"role": "tourist"}` y, con el mismo token, a un turista `{"role": "admin"}` | 403 y luego 200; `role == "admin"` en cuerpo y en BD | rojo |
  | `test_be02_superadmin_self_profile_update_returns_200` | PATCH propio `{"first_name": "Changed"}` | 200; `first_name` y `cedula` en cuerpo; BD cambiada; rol intacto; 1 fila de auditoría: `UPDATE`, `performed_by` el actor, `changes == {"first_name": "Changed"}` | verde |
  | `test_be02_superadmin_changes_third_party_role_returns_200` | PATCH a un admin ajeno `{"role": "tourist"}` | 200; `role` y `cedula` en cuerpo; BD `tourist`; 1 fila: `entity_id` el destino, `performed_by` el actor, `changes == {"role": "tourist"}` | verde |

  RED demostrado en el handoff: `10 failed, 9 passed` con `-k be02`, los 10 rojos exactamente los de la tabla.
- **Criterio de aceptación:** `-k be02` da `19 passed`; suite `415 passed`; cobertura ≥ 94.81 %; import-linter 4 KEPT;
  trinquete de la decisión 2 cumplido; `git diff --numstat` de la fase da `12 5` en la política, `3 3` en `user_service.py`
  y 0 borradas en los tests. La compuerta sigue en **exit 1** (`Compuerta NO superada: ruff check, mypy`): ese rojo
  heredado no bloquea esta fase (ADR-0005). No se exige verde. Salida literal en el handoff.
- **Fuera de alcance de esta fase:** todo lo de "Regla de alcance"; renombrar o reordenar tests existentes; sus D205 y E501
  vecinas; el texto de los `detail` existentes.
- **Commit** (el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra):
  ```text
  fix(access-policy): block self role changes for superadmins too

  A superadmin could PATCH their own role and lose the rank at once; with a
  single superadmin nobody could restore it short of direct SQL. The hierarchy
  guard skips self-updates and the role guard only reads the actor's rank, so
  this was the one actor and target combination still open.

  - user_access_policy.py: add the self-update guard on the role key, after the
    non-superadmin guard so the other actors keep their current answer; rewrite
    the two docstrings that promised self-update parity without this exception.
  - user_service.py: same correction in the update_user_account docstring only.
  - test_user_access_policy.py: 19 cases, 10 of them red before the guard.

  The guard reads the key, not the value, like the existing one: resending the
  current role is rejected too. This does not keep a superadmin on the platform:
  self-deactivation and self-deletion stay open (BE-35).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Expectativas medidas sobre la copia desechable con el texto literal de este plan (equivalentes de grep y numstat; los
pasos de la compuerta, uno a uno). Se ejecutan desde la raíz, en Git Bash.

```bash
# V1. Ningún docstring declara la paridad sin excepción: 0 coincidencias (exit 1)
git grep -n -E 'self-updates are always permitted|may always act on their own|self-operation parity|self-update parity|role mutations for non-superadmins' -- app

# V2. Guardas: 4 líneas, todas en user_access_policy.py (la cuarta, la guarda nueva)
git grep -n -E '"role" in update_dict|is_self_update' -- app

# V3. Sigue habiendo un único punto de mutación: 1 línea, user_service.py:279
git grep -n -E 'setattr\(target_user' -- app

# V4. El hueco de test se cerró: 2 líneas
git grep -n -E 'assert_can_update\(superadmin, *superadmin' -- tests

# V5. Tests nuevos: 10 funciones y 19 casos
git grep -c -E 'def test_be02_' -- tests/test_user_access_policy.py
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -q -k be02

# V6. Los tests congelados siguen: 2
git grep -c -E 'def test_b2_admin_self_role_noop_returns_403|def test_superadmin_self_delete_is_allowed' -- tests/test_user_access_policy.py

# V7. Solo 3 archivos en app, tests y alembic; policy 12/5, service 3/3, tests N/0 (sin esquema, schemas ni router)
git diff --name-only c6422ed HEAD -- app tests alembic
git diff --numstat c6422ed HEAD -- app/services/user_access_policy.py app/services/user_service.py tests/test_user_access_policy.py

# V8. Trinquete por archivo (decisión 2): 8, 6 y "All checks passed!"; total 53
./venv/Scripts/python.exe -m ruff check app/services/user_access_policy.py --statistics
./venv/Scripts/python.exe -m ruff check app/services/user_service.py --statistics
./venv/Scripts/python.exe -m ruff check tests/test_user_access_policy.py
./venv/Scripts/python.exe -m ruff check .

# V9. mypy: "Found 10 errors in 5 files"; 3 en user_service.py (l.124, 132, 133), 0 en la política
./venv/Scripts/python.exe -m mypy

# V10. Compuerta: exit 1 solo por ruff check y mypy; 415 passed; cobertura >= 94.81 %; 4 KEPT
./venv/Scripts/python.exe scripts/check.py
```

## Enmiendas aprobadas

- **E1 (5 nov 2026, 19:00, tras la auditoría de la fase A; texto de David: "tú corrige el test").** Opcional 3 de
  `gaps.md`: `test_be02_self_role_guard_identifies_the_actor_by_cedula` no fija lo que su nombre promete (con `actor is
  target` o comparación por email, el gemelo cae en la guarda de jerarquía y lanza la misma excepción). Retoque de test,
  sin tocar `app/`: se añade `test_be02_twin_by_cedula_with_profile_fields_is_self_update` (gemelo con la cédula del
  actor y `{"first_name": …}` **no** lanza), que mata M14 y M15. Opcional 2 (orden de las guardas) va a BE-32 por
  decisión de David; opcional 1 (`current_target` → `null`) lo hace David a mano al cerrar el ítem.

## Residuales

1. **Texto de ADR-0005 frente a su aplicación.** El ADR y los dos rituales piden cero en archivos tocados; la verificación
   dice "solo no añadir"; BE-01 y A9 ya usaron excepciones declaradas. Decisión de David: sin addendum a ADR-0005; el ADR
   caduca al quedar verde (BE-33 + A4).
2. **Retirar `unfixable I001` al cerrar A4** (decisión 4).
3. **BE-37:** tras este plan el caso propio de `{"role": null}` da 403; el de un tercero sigue en 409 (medido). Al verificar
   BE-37 hay que medir sobre un tercero. Sugerencia para David, sin editar el backlog.
4. **Rincones 1-5:** ya tienen fila (BE-34 a BE-38, `B-GHOST-ADMIN`); no hacen falta filas nuevas.
5. **Otro builder de `PATCH` en el frontend:** David responde de memoria que ninguna otra pantalla envía `role` en un
   `PATCH`; no verificado contra el frontend. No condiciona la Fase A.

## Referencias

No aplica: el plan no usa ninguna API de librería nueva ni con aviso de deprecación (solo `pytest.mark.parametrize` y los
fixtures existentes), por lo que no se consultó Context7. Internas: ADR-0003, ADR-0005, ADR-0009, ADR-0011;
`docs/deuda/BE-01/plan.md` (decisión 6).

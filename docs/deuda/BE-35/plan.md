# PLAN — BE-35: Impedir que un superadmin se borre o se desactive a sí mismo

> Fuente: `docs/deuda/BE-35/verificacion.md` (confirmada; adenda de David, 16 nov 2026, 10:31, que **cambia la regla de
> la fila**). Base: `300e294` (HEAD de `item/be-35`; `app/` y `tests/` idénticos a `87b9905`, la línea base de la
> verificación: 691 passed, 97,63 %, ruff 0, mypy 0 en 63 archivos, 4 kept).
> **Estado: aprobado por David con E0 (16 nov 2026, 10:51).** `Aprobado: 16 nov 2026`
> (esa es la `<FECHA>` del ADR de la fase A). Enmiendas al final, en "Enmiendas aprobadas".
> Las cifras de este plan (tests, RED, conteos de grep) están **calculadas** sobre el código de `300e294` y el texto que
> el plan dicta, no medidas en una copia: el redactor no ejecutó código en esta sesión. El ejecutor las confirma; si una
> no cuadra, se detiene y lo anota en el handoff, sin "arreglar" código para que cuadre.

## Resumen para aprobación

Dos fases. (A) Escribe ADR-0017: ningún superadmin se borra ni se desactiva a sí mismo, haya uno o varios; como entre
pares ya no se puede (403 medido), el número de superadmins no baja nunca desde la aplicación. (B) Aplica la regla en
`UserAccessPolicy`: `assert_can_delete` rechaza el auto-borrado de un superadmin y `assert_can_update` rechaza
`is_active` a `false` sobre sí mismo (lee el **valor**: `{"is_active": true}` sigue pasando). Corrige los docstrings que
describen la "paridad de auto-borrado", cambia el test que la congela y añade 16 tests (691 → 707).
**Riesgo principal:** coste de producto aceptado por David: una cuenta de superadmin ya no se puede retirar desde la
aplicación (baja = SQL directo del operador, sin auditoría, hasta BE-55). Segundo: dos rutas pasan de 200 a 403 para un
superadmin sobre sí mismo; no se ha comprobado que el cliente Flutter no ofrezca esas acciones (residual R1).
**No se toca:** `count_active_superadmins`, `app/core/exceptions.py`, `app/main.py` (`_DOMAIN_ERROR_STATUS`), guards,
rutas, `tests/test_route_guards.py`, BE-36, BE-37, BE-38, A3.

**Decisiones que este plan toma de la adenda y que quedan pendientes de aprobación al aprobarlo** (la adenda las fijó
antes de planear; el plan no las da por cerradas en silencio, las recomienda con su trade-off):

1. **Código de respuesta — pendiente de aprobación. Recomendado: 403 con `AuthorizationError`** (adenda, punto 2).
   La fila pedía 409 porque su regla dependía de un conteo ("eres el último"); con la regla nueva el rechazo no depende
   del estado, es una prohibición sobre la propia cuenta, el mismo molde que "nadie cambia su propio rol" (BE-02, 403).
   Trade-off: 409 exigiría una `DomainError` nueva y su entrada en `_DOMAIN_ERROR_STATUS` (AGENTS §3); 400 con
   `BusinessRuleViolationError` mezclaría una regla de autorización con una de negocio. Coste del 403: el cliente solo
   distingue este rechazo de otros 403 por el `detail`.
2. **Dónde se cruza el conteo con la política — pendiente de aprobación. Recomendado: no se cruza; no hay conteo**
   (adenda, punto 4). La política sigue pura, síncrona y con la misma firma; el servicio no llama a
   `count_active_superadmins`, que sigue siendo solo del bootstrap. Trade-off: se pierde que un superadmin se retire a sí
   mismo cuando hay varios. Ganancia: sin I/O en la política, sin `return_value` nuevo en los mocks `autospec` de
   `tests/test_user_service.py:70-73` (rincón 7 sin objeto), y sin carrera.
3. **ADR — pendiente de aprobación. Recomendado: sí, ADR-0017** (adenda, punto 5; `docs/deuda/BE-02/plan.md:72` lo
   anunciaba). Es un trade-off contra producto (nadie puede retirar a un superadmin desde la app) y descarta una
   alternativa medida (conteo bajo bloqueo). Texto dictado en la fase A.
4. **Carrera entre contar y escribir — pendiente de aprobación. Recomendado: desaparece por construcción** (adenda,
   punto 4). Sin conteo, dos peticiones simultáneas reciben el mismo 403. No hay límite que declarar en la suite (BE-31
   no interviene). El conteo bajo `SELECT … FOR UPDATE` (sonda de la adenda) queda como dato para BE-55, que reabre el
   problema si la baja la hace otro superadmin.

## Objetivo y decisiones bloqueadas

Que ninguna petición de la aplicación pueda reducir el número de superadmins activos: se cierran las dos vías medidas de
autoservicio (auto-`DELETE` y auto-`PATCH {"is_active": false}`), las únicas que quedaban (sonda de la verificación).

1. Regla: ningún superadmin borra ni desactiva su propia cuenta, haya uno o varios. Sin conteo.
2. Respuesta: 403 con `AuthorizationError` existente. Orden 404 → 403. El rechazo no muta estado ni escribe auditoría.
3. La guarda de `is_active` lee el valor `False`, no la presencia de la clave; `true` propio pasa; `null` es BE-37.
4. `UserAccessPolicy` no cambia de firma ni recibe repositorio. El servicio no cambia de lógica.
5. "Sí mismo" = misma `cedula` (como BE-02), no misma instancia ni mismo correo.
6. ADR-0017 antes del código que lo cita.
7. Admins y turistas no cambian: un admin puede seguir borrándose o desactivándose a sí mismo (un superadmin lo recupera).

## Análisis del redactor

**Qué se cambia y por qué.** Contrastado en `300e294`: `user_access_policy.py:34-41` deja pasar todo auto-borrado;
`:60-79` no tiene guarda sobre el valor de `is_active` salvo la de turistas por clave (`:75`); `user_service.py:205-208`
y `:281-285` aplican lo que la política deje pasar. Se añaden dos guardas a la política y nada más en la lógica. Es una
regla que depende del dato (el objetivo es el propio actor), así que va en la política y no en un guard (ADR-0012,
punto 2), y lanza la excepción que el handler ya traduce a 403 (ADR-0003).

**Código que dicta la fase B** (dentro de `user_access_policy.py`):
- En `assert_can_delete`, tras el `raise` de `:37-41`:
  ```python
          if is_self_deletion and actor.role == UserRole.superadmin:
              raise AuthorizationError("Un superadministrador no puede eliminar su propia cuenta.")
  ```
- En `assert_can_update`, tras la guarda de turistas (`:75-79`), como última guarda:
  ```python
          if (
              is_self_update
              and actor.role == UserRole.superadmin
              and update_dict.get("is_active") is False
          ):
              raise AuthorizationError("Un superadministrador no puede desactivar su propia cuenta.")
  ```
  `update_dict` sale de `model_dump(mode="json", exclude_unset=True)` (`user_service.py:278`), así que llega el `bool` ya
  validado: `"false"` del JSON llega como `False` (modo laxo de pydantic; ver Referencias).

**Orden y dependencias.** A (ADR, 1 archivo) va primero porque los docstrings de B citan ADR-0017. B depende de A y de
nada más. Regla, docstrings y tests van en un solo commit, como en BE-02 (`docs/deuda/BE-02/plan.md:60-61`): separar el
código de sus docstrings dejaría un commit en que el código miente.

**Tests que congelan comportamiento relacionado.** Cambia uno: `test_superadmin_self_delete_is_allowed`
(`tests/test_user_access_policy.py:57-60`), que pasa a esperar el rechazo. Siguen en verde sin tocarlos (comprobado
leyéndolos): `test_self_delete_tourist_is_allowed` (`:40`), `test_superadmin_cannot_delete_peer_superadmin` (`:83`),
`test_admin_can_mutate_is_active` (`:111`, admin → turista), `test_tourist_cannot_mutate_is_active` (`:137`),
`test_superadmin_cannot_update_peer_superadmin` (`:149`), los BE-02 (`:165-221`, `:481-621`), los B3 (`:630-738`),
`test_service_authorization_error_propagates_to_403_through_global_handler` (`:772`, turista con servicio simulado),
`tests/test_auth.py:167` (auto-borrado de un turista) y `:239` (turista, `{"is_active": False}` → 403). Ningún test de
`tests/test_user_service.py` llega a la política con un superadmin (cortan en el 404, `:148-175`). Ninguna ruta cambia:
`tests/test_route_guards.py` no se toca.

**Corrección a la verificación.** El docstring del router citado en `:133-134` sí está ahí (`app/api/routers/user.py:133-134`,
"on self-deletion or …"); la adenda no lo había comprobado.

**Riesgos.** (a) El coste de producto (resumen). (b) Contrato: 200 → 403 en dos casos; cliente sin verificar (R1).
(c) El caso `"coerced-false"` depende de que pydantic 2.12.5 convierta `"false"` en `False` en modo laxo; si da 422, el
ejecutor se detiene y lo anota (no toca `app/` para forzarlo). (d) Mutante M6 (abajo) sobrevive a propósito: es BE-37.

**Mutantes que la fase B debe matar** (para el auditor; sobre una copia, no en el repo):
M1 quitar `and actor.role == UserRole.superadmin` del borrado → muere por `test_be35_admin_self_delete_is_still_allowed` y
`test_self_delete_tourist_is_allowed`. M2 `actor is target` en vez de `is_self_deletion` en la guarda nueva de borrado →
`test_be35_self_delete_guard_identifies_the_actor_by_cedula`. M3 `"is_active" in update_dict` en vez del valor →
`test_be35_superadmin_self_update_with_is_active_true_is_allowed` y su gemelo HTTP. M4 quitar `is_self_update` de la guarda
nueva → `test_be35_superadmin_can_deactivate_lower_rank_account` y su gemelo HTTP. M5 quitar la condición de rol de la
guarda nueva → `test_be35_admin_self_deactivation_is_still_allowed`. M7 `actor is target` en la guarda nueva de
`is_active` → `test_be35_self_deactivation_guard_identifies_the_actor_by_cedula`. M8 y M9 (quitar cada guarda entera) → los
RED de su vía. **M6 `not update_dict.get("is_active", True)`** (trata `None` como desactivación) **sobrevive**: ningún test
congela `{"is_active": null}`, porque hacerlo congelaría el 409 de BE-37. Declarado, no es hueco.

**Qué NO se toca.** `UserRepository` (ni el docstring de `count_active_superadmins`, que sigue siendo cierto),
`superadmin_bootstrap.py`, `app/core/exceptions.py`, `app/main.py`, `app/api/dependencies.py`, `app/schemas/`, la lógica de
`user_service.py`, `tests/test_user_service.py`, `tests/test_auth.py`, `tests/test_route_guards.py`, `assert_can_recover`.

## Regla de alcance

**Sí:** ADR-0017; dos guardas en `UserAccessPolicy`; docstrings y el comentario de paso que describen la paridad de
auto-borrado en `user_access_policy.py`, `user_service.py` y `routers/user.py` (patrón 4 de la verificación); el test de
`:57-60` y los tests nuevos en `tests/test_user_access_policy.py`.
**No:** conteo de superadmins en cualquier capa; excepción nueva o entrada en `_DOMAIN_ERROR_STATUS`; validar `None`
explícito (BE-37); auditoría de no-ops (BE-38); recuperación entre pares (BE-36); `commit()` en repositorios (A3); guards,
rutas e inventario de rutas; reglas de auto-borrado o auto-desactivación de admins y turistas; un mecanismo de baja de
superadmins (BE-55); `docs/backlog.md`, `docs/CONTEXT.md` y `AGENTS.md` (los actualiza la sesión Mentor al cierre).

## Fases

### Fase A — ADR-0017 (la más pequeña)

- **Archivos (1):** `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md` (nuevo). Dominio: decisiones (docs).
- **Cambios exactos:** crear el archivo con este texto; `<FECHA>` es la de la línea `Aprobado:` de la cabecera de este plan.
  ```markdown
  # ADR-0017 — Ningún superadmin se borra ni se desactiva a sí mismo: el número de superadmins no baja desde la aplicación

  - **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-35)
  - **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 10:31)
  - **Ubicación en el repo:** `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md`
  - **Origen:** backlog BE-35; `docs/deuda/BE-35/verificacion.md` (veredicto y adenda); `docs/deuda/BE-35/plan.md`. El plan
    de BE-02 (`docs/deuda/BE-02/plan.md:72`) anunció que esta regla requeriría ADR. Relación: ADR-0012 (una regla que
    depende del dato va en la política), ADR-0003 (`AuthorizationError` → 403), ADR-0015 (primer superadmin y
    `count_active_superadmins`), BE-55 (baja de un superadmin sin SQL directo).

  ## Contexto

  Un superadmin podía sacarse a sí mismo de la plataforma por dos vías de autoservicio: `DELETE /usuarios/{su cédula}` y
  `PATCH /usuarios/{su cédula}` con `{"is_active": false}`. Las dos daban 200 y la petición siguiente, 401
  (`get_current_user` rechaza a quien está borrado o inactivo). Si era el único, la plataforma se quedaba sin superadmin.
  Medido el 16 nov (sonda de la verificación): un superadmin no puede desactivar ni borrar a otro (403 y 403), y el cambio
  del propio rol lo cerró BE-02. Esas dos vías eran las únicas por las que bajaba el número de superadmins activos.

  La fila del backlog proponía "siempre queda al menos un superadmin activo": contar antes de borrar o desactivar y
  responder 409 al último.

  ## Decisión

  1. **Ningún superadmin borra ni desactiva su propia cuenta, haya uno o varios.** `UserAccessPolicy.assert_can_delete`
     rechaza que un superadmin borre su cuenta; `assert_can_update` rechaza que ponga su `is_active` a `false`. "Su
     cuenta" es la de su misma cédula.
  2. **La guarda de `is_active` lee el valor, no la clave:** `{"is_active": true}` sobre uno mismo sigue pasando.
  3. **403 con `AuthorizationError`,** el molde de "nadie cambia su propio rol" (BE-02). Sin excepción nueva ni entrada
     nueva en `_DOMAIN_ERROR_STATUS`. Orden: 404 → 403. El rechazo no muta estado ni escribe auditoría.
  4. **Sin conteo y sin bloqueo.** La política sigue pura y síncrona, con la misma firma. `count_active_superadmins`
     sigue siendo solo del primer superadmin (ADR-0015).

  Con el punto 1 y la regla entre pares, el número de superadmins no baja nunca desde la aplicación: no hay "último" que
  detectar, y dos peticiones simultáneas reciben el mismo rechazo.

  ## Consecuencias

  - **Coste aceptado (David, 16 nov):** una cuenta de superadmin no se puede retirar desde la aplicación. Antes solo
    podía hacerlo su dueño; ahora, nadie. Si cambia el gerente o una cuenta se ve comprometida, la baja es SQL directo
    del operador, que no escribe auditoría, hasta que exista el mecanismo de BE-55.
  - Cambio de contrato solo para un superadmin sobre sí mismo: `DELETE /usuarios/{cedula}` y `PATCH /usuarios/{cedula}`
    con `is_active` a `false` pasan de 200 a 403. Turistas y admins no cambian.
  - `{"is_active": null}` no lo trata esta regla (BE-37).
  - BE-36 sigue abierta: el caso "A se desactiva y B no puede reactivarlo" deja de poder producirse, pero la
    recuperación entre pares que deja la cuenta inactiva sigue ahí.
  - Si BE-55 deja que un superadmin dé de baja a otro, vuelve el problema de contar bajo concurrencia (alternativa 2).

  ## Alternativas consideradas

  1. **La regla de la fila, contando con `SELECT count(*)`.** Rechazada: con dos superadmins que se retiran a la vez,
     cada petición cuenta 2 y las dos pasan; quedan 0 (sonda de la adenda, abajo). Ningún `CHECK` puede contar filas.
  2. **La regla de la fila, contando bajo bloqueo (`SELECT id … FOR UPDATE` sobre los superadmins activos).** Cierra la
     carrera en PostgreSQL. Descartada porque la regla del punto 1 no necesita contar; además, la política dejaría de ser
     pura (el conteo vive en `UserRepository`) y la suite no lo vería: SQLite ignora `FOR UPDATE` (BE-31). Queda como dato
     para BE-55.
  3. **409 con una `DomainError` nueva.** Descartada: con la regla del punto 1 el rechazo no depende del estado de la
     plataforma; es una prohibición sobre la propia cuenta, como el rol propio de BE-02, que ya es 403.
  4. **No hacer nada.** Rechazada: el único superadmin deja la plataforma sin superadmin con una petición.

  ## Evidencia

  - Verificación (16 nov, pila real de la suite): único superadmin, `PATCH` propio `{"is_active": false}` → 200 y 401
    después; `DELETE` propio → 200 y 401 después; `count_active_superadmins()` = 0 en ambos. Entre dos superadmins: 403 y
    403.
  - Sonda de la sesión Mentor (16 nov; PostgreSQL 16.15 propio, réplica mínima de `users`, psycopg2, `READ COMMITTED`;
    dos superadmins A y B que se borran a la vez, cada uno en su transacción):
    `plain count [('A', 'counted 2 -> deleted'), ('B', 'counted 2 -> deleted')] | active superadmins left: 0` y
    `FOR UPDATE [('A', 'counted 2 -> deleted'), ('B', 'counted 1 -> rejected')] | active superadmins left: 1`. Límites:
    SQL directo, no el repositorio ni asyncpg; no es una base de Azure.
  - Tests y mutantes de la regla: `docs/deuda/BE-35/plan.md`, fase B.
  ```
- **Tests (RED primero):** no aplica (solo documentación). Comprobación sustituta: `scripts/check.py --no-tests` en verde
  (`check_docs` no escanea `docs/adr`, pero la compuerta debe seguir igual) y `git diff --stat` = 1 archivo nuevo.
- **Criterio de aceptación:** el archivo existe con el texto dictado y `<FECHA>` sustituida; `git grep -c 'ADR-0017' --
  docs/adr` = `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md:1`; compuerta completa en verde con 691 passed.
- **Fuera de alcance de esta fase:** cualquier archivo de `app/` o `tests/`; `AGENTS.md`, `docs/CONTEXT.md`,
  `docs/backlog.md`.
- **Commit:**
  ```
  docs(adr): add ADR-0017, superadmins never remove their own account

  A superadmin could delete or deactivate their own account and, if it
  was the only one, leave the platform without a superadmin (BE-35).
  The backlog row proposed counting active superadmins and answering
  409 for the last one; a probe on PostgreSQL showed that a plain count
  lets two simultaneous removals leave zero, and only a row lock
  closes the race.

  The ADR records David's decision before the code that cites it
  lands: no superadmin deletes or deactivates their own account,
  answered with 403 through the existing AuthorizationError. Peers
  already cannot remove each other, so the number of superadmins never
  drops from the application and there is no last one to detect. It
  declares the cost (retiring a superadmin is direct SQL until BE-55)
  and the rejected paths: counting with or without a lock, a 409 with
  a new domain error, and doing nothing.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Las dos guardas en `UserAccessPolicy`, sus docstrings y sus tests

- **Archivos (4):** `app/services/user_access_policy.py`, `app/services/user_service.py` (solo docstrings y un
  comentario), `app/api/routers/user.py` (solo un docstring), `tests/test_user_access_policy.py`. Dominio: autorización
  sobre cuentas de usuario.
- **Cambios exactos en `app/`** (las dos guardas, en "Análisis del redactor"; los textos, aquí):
  - `user_access_policy.py`, docstring de la clase, sustituir las líneas `:10-13` por:
    ```
        All guarded mutations follow a hierarchical dominance invariant over role
        ranks: an actor may update or delete their own account, while third-party
        operations require a strictly higher rank. Two exceptions on one's own
        account: nobody changes their own role, and a superadmin never deletes or
        deactivates it, so the number of superadmins never drops (ADR-0017).
    ```
  - `assert_can_delete`: tras `:24` añadir, separado por línea en blanco,
    `A superadmin never deletes their own account (ADR-0017).`; y el `Raises:` (`:31-32`) pasa a:
    ```
                AuthorizationError: When the actor neither deletes their own
                    account nor outranks the target, or when a superadmin deletes
                    their own account.
    ```
  - `assert_can_update`, docstring `:47-49` pasa a:
    ```
            Fail-safe guards then reject the role key for non-superadmins and on any
            self-update, the is_active key for tourists, and is_active set to false
            by a superadmin on their own account (ADR-0017). The role guards read the
            key, not its value: resending the current role is rejected too. The last
            guard reads the value: is_active true on one's own account passes.
    ```
  - `user_service.py`, docstring de `delete_user_account` `:180-183` pasa a:
    ```
            Authorization follows a pure hierarchical invariant: the action is
            allowed when the actor deletes their own account or when the actor's
            role rank is strictly greater than the target's role rank. A superadmin
            never deletes their own account (ADR-0017).
    ```
    Su `Raises` `:194` pasa a `AuthorizationError: 403 Forbidden if the hierarchical invariant fails` + línea siguiente
    `or a superadmin deletes their own account.` (sangría de continuación). Comentario `:204` pasa a
    `# 2. ABAC Hierarchical Invariant: own account OR strictly higher rank; see ADR-0017`.
  - `user_service.py`, docstring de `update_user_account` `:256-257` pasa a:
    ```
            target's role rank. Fail-safe invariants additionally block the role key
            for non-superadmins and on any self-update, is_active for tourists, and
            is_active set to false by a superadmin on their own account (ADR-0017).
    ```
  - `routers/user.py`, docstring del `DELETE` `:133-134` pasa a:
    ```
        Hierarchical ABAC is delegated to UserService: the action is allowed only
        on the actor's own account or when the actor's role strictly outranks the
        target's, and never on a superadmin's own account (ADR-0017).
    ```
- **Tests (RED primero)** — en `tests/test_user_access_policy.py`, escritos y ejecutados **antes** de tocar `app/`:
  - Docstrings de clase (texto de E0; una línea cada uno, 95 y 94 columnas con su sangría de cuatro espacios):
    `TestAssertCanDelete` (`:38`) →
    `"""Freezes the deletion invariant: own account or higher rank, never a superadmin's own."""`;
    `TestAssertCanUpdate` (`:92`) →
    `"""Freezes update invariants: hierarchy, role and is_active fail-safes, ADR-0017 guard."""`.
  - Unitarios en `TestAssertCanDelete` (`make_user`, `policy`; `pytest.raises(AuthorizationError)` donde dice "lanza"):
    U1 **sustituye** a `test_superadmin_self_delete_is_allowed` (`:57-60`): `test_be35_superadmin_self_delete_is_rejected`
    — `assert_can_delete(superadmin, superadmin)` lanza. U2 `test_be35_self_delete_guard_identifies_the_actor_by_cedula` —
    `twin = make_user(role=UserRole.superadmin, cedula=superadmin.cedula)`; `assert_can_delete(superadmin, twin)` lanza.
    U3 `test_be35_admin_self_delete_is_still_allowed` — `assert_can_delete(admin, admin)` no lanza.
  - Unitarios en `TestAssertCanUpdate`: U4 `test_be35_superadmin_self_deactivation_is_rejected` —
    `(superadmin, superadmin, {"is_active": False})` lanza. U5
    `test_be35_superadmin_self_update_with_is_active_true_is_allowed` — `{"is_active": True}` no lanza. U6
    `test_be35_self_deactivation_guard_identifies_the_actor_by_cedula` — gemelo por cédula, `{"is_active": False}` lanza.
    U7 `test_be35_admin_self_deactivation_is_still_allowed` — `(admin, admin, {"is_active": False})` no lanza. U8
    `test_be35_superadmin_can_deactivate_lower_rank_account` — `(superadmin, admin, {"is_active": False})` no lanza.
  - HTTP, sección nueva al final del bloque B (tras `:738`, antes de `# C. GLOBAL EXCEPTION HANDLER TESTS`), con la
    cabecera `# --- BE-35 regression: a superadmin never deletes or deactivates their own account ---`. Fixtures `client`,
    `db_session`, `persist_user`, `make_auth_headers`; `refresh` tras cada petición (ADR-0011). La forma de cada llamada
    está fijada porque la cuenta el patrón 7 de la verificación final:
    - H1 `test_be35_sole_superadmin_self_delete_returns_403_without_mutation` — `client.delete(f"/usuarios/{superadmin.cedula}",
      headers=…)`: 403; `set(body) == {"detail"}`; `isinstance(body["detail"], str)`; `deleted_at is None`;
      `is_active is True`; `select(AuditLog)` → `[]`.
    - H2 `test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active` — persiste además `peer`
      superadmin; mismo `DELETE`: 403, `{"detail"}`; el actor sigue con `deleted_at is None` e `is_active is True`;
      `peer.is_active is True`.
    - H3 `test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation`, `@pytest.mark.parametrize("payload",
      [{"is_active": False}, {"is_active": "false"}, {"is_active": False, "first_name": "Changed"}], ids=["false",
      "coerced-false", "with-profile-fields"])`, llamada `client.patch(…, json=payload, headers=…)`: 403;
      `{"detail"}` y `str`; `is_active is True`; `first_name == "John"`; auditoría `[]`.
    - H4 `test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active` — un segundo superadmin
      persistido; `client.patch(f"/usuarios/{superadmin.cedula}", json={"is_active": False}, headers=…)`: 403,
      `{"detail"}`; `is_active is True`.
    - H5 `test_be35_superadmin_keeps_access_after_rejected_self_removal` — mismo `headers` para las tres: `DELETE` propio
      → 403; `client.patch(f"/usuarios/{superadmin.cedula}", json={"is_active": False}, headers=headers)` → 403;
      `client.get("/usuarios/mi-perfil", headers=headers)` → 200 con `body["cedula"] == superadmin.cedula`,
      `body["role"] == "superadmin"`, `body["is_active"] is True`.
    - H6 `test_be35_superadmin_self_update_with_is_active_true_returns_200` — `json={"is_active": True}` sobre sí mismo:
      200; `body["cedula"]`, `body["is_active"] is True`; tras `refresh`, `is_active is True`. **Sin** aserción sobre la
      auditoría (hoy registra la clave aunque no cambie: BE-38, no se congela).
    - H7 `test_be35_superadmin_deactivates_lower_rank_account_returns_200` — superadmin sobre un admin,
      `client.patch(f"/usuarios/{admin.cedula}", json={"is_active": False}, headers=…)`: 200; `body["cedula"] ==
      admin.cedula`, `body["is_active"] is False`; tras `refresh`, `admin.is_active is False`; una fila de auditoría con
      `action == AuditAction.UPDATE`, `entity_id == admin.cedula`, `performed_by == superadmin.cedula`,
      `changes == {"is_active": False}`.
  - **RED esperado** (antes de tocar `app/`): `./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be35 -q`
    → `11 failed, 6 passed`. Fallan U1, U2, U4, U6, H1, H2, H3 (×3), H4, H5. Pasan ya U3, U5, U7, U8, H6, H7: son los
    bordes que impiden que la regla bloquee de más (mueren con M1, M3, M4, M5). Si `coerced-false` falla con 422 en vez
    de 200, detenerse (riesgo c).
- **Criterio de aceptación:** `-k be35` → `17 passed`; suite completa `707 passed` (691 − 1 sustituido + 17); compuerta
  `./venv/Scripts/python.exe scripts/check.py` con salida 0, ruff 0, mypy 0, 4 kept y cobertura ≥ 97,63 %
  (`user_access_policy.py` sigue al 100 %); los comandos 1–9 de la verificación final dan lo esperado; mutantes M1–M5,
  M7–M9 muertos y M6 vivo, anotados en el handoff.
- **Fuera de alcance de esta fase:** lógica de `user_service.py`; `count_active_superadmins` y su docstring;
  `exceptions.py`, `main.py`, `dependencies.py`, schemas; `tests/test_user_service.py`, `tests/test_auth.py`,
  `tests/test_route_guards.py`; `{"is_active": null}` (BE-37); auditoría de no-ops (BE-38); admins y turistas.
- **Commit:**
  ```
  fix(access-policy): block superadmin self-deletion and self-deactivation

  A superadmin could delete their own account or PATCH their own
  is_active to false and get 200; the next request was 401 and, if it
  was the only one, the platform was left without a superadmin
  (BE-35, measured). Peers already cannot remove each other (403), so
  these two self-service paths were the only ways the number of
  superadmins could drop. David chose to close both whatever the
  number of superadmins, instead of counting the last one (ADR-0017).

  - app/services/user_access_policy.py: assert_can_delete rejects a
    superadmin deleting their own account; assert_can_update rejects
    is_active set to false on their own account. The second guard
    reads the value, not the key, so is_active true still passes.
    Both raise AuthorizationError (403), the mold of the BE-02
    self-role rule: no new exception and no count, so the policy
    stays pure and two simultaneous requests get the same answer.
  - app/services/user_service.py, app/api/routers/user.py: docstrings
    and one step comment stop describing self-deletion parity as the
    rule and cite ADR-0017. No logic change.
  - tests/test_user_access_policy.py: the unit test that froze the
    superadmin self-deletion as allowed now expects the rejection.
    New unit and HTTP cases cover both paths with one superadmin and
    with two, a coerced "false", mixed profile fields, access kept
    after the rejection, and the boundaries that must keep passing:
    is_active true on oneself, admin self-service and a superadmin
    deactivating an admin.

  {"is_active": null} is BE-37 and is left as is. Retiring a superadmin
  is now a database operation until BE-55.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase B. Los conteos incluyen el texto que dicta este plan (código, docstrings,
comentarios, nombres de tests). Patrones 1–6 = los de la verificación, recalculados.

```bash
# 1. Patrón 1: guardas de borrado y de is_active por clave → 4 líneas, todas en app/services/user_access_policy.py
#    (is_self_deletion: asignación, guarda de jerarquía, guarda nueva; "is_active" in update_dict: guarda de turistas)
git grep -n -E 'is_self_deletion|"is_active" in update_dict' -- app

# 2. La guarda nueva lee el valor → 1 línea, en app/services/user_access_policy.py
git grep -n -F 'update_dict.get("is_active") is False' -- app

# 3. Patrón 2: consumidores del conteo → las mismas 2 líneas de la base (user_repository.py def; superadmin_bootstrap.py:42)
git grep -n 'count_active_superadmins' -- app

# 4. Patrón 3: el test que congelaba el auto-borrado → 0 líneas (exit 1)
git grep -n 'test_superadmin_self_delete_is_allowed' -- tests

# 5. Patrón 4 ampliado: paridad de auto-borrado en docstrings y comentarios → 0 líneas (exit 1)
git grep -n -i -E 'self-deletion|act on their own account|parity' -- app

# 6. Patrón 5: respuestas 409 → 1 línea, app/main.py (IntegrityError); ninguna nueva
git grep -n 'HTTP_409' -- app

# 7. Patrón 6: tests HTTP que envían is_active=False literal → 4 líneas: tests/test_auth.py (1)
#    y tests/test_user_access_policy.py (3: H4, H5, H7; H3 usa json=payload)
git grep -n -E 'json=\{"is_active": False\}' -- tests

# 8. Citas de la decisión en app/ → 7 líneas: user_access_policy.py (3: clase, assert_can_delete, assert_can_update),
#    user_service.py (3: docstring de delete, comentario de paso, docstring de update), routers/user.py (1)
git grep -n 'ADR-0017' -- app

# 9. Mensajes nuevos → 2 líneas, ambas en app/services/user_access_policy.py
git grep -n -F 'superadministrador no puede' -- app

# 10. Sin excepción nueva ni cambios fuera del alcance → salida vacía
git diff --stat 300e294 HEAD -- app/core app/main.py app/repositories app/schemas app/api/dependencies.py tests/test_user_service.py tests/test_route_guards.py tests/test_auth.py

# 11. Tests del ítem → 15 funciones nuevas o renombradas; 17 casos en verde
git grep -c 'def test_be35_' -- tests/test_user_access_policy.py      # → tests/test_user_access_policy.py:15
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be35 -q   # → 17 passed

# 12. Compuerta completa → salida 0; 707 passed; cobertura ≥ 97,63 %; ruff 0; mypy 0; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

- **R1 — Cliente Flutter sin verificar.** Dos casos pasan de 200 a 403 (superadmin que se borra o se desactiva). Nadie ha
  comprobado si alguna pantalla del cliente los ofrece a un superadmin. Evidencia: ninguna en el repo backend. Destino:
  nota en la fila BE-35 al cierre (sesión Mentor), como la nota de BE-02 sobre `role`.
- **R2 — Mutante M6 vivo (`None` tratado como desactivación).** Indistinguible hasta que BE-37 impida que `None` llegue
  a la política. Destino: nota en la fila BE-37 ("al cerrar BE-37, M6 de BE-35 deja de ser alcanzable").
- **R3 — La baja por SQL directo no tiene procedimiento escrito ni auditoría.** ADR-0017 lo declara como coste. Destino:
  nota en la fila BE-55 (el mecanismo debe auditar la baja y comprobar que queda al menos un superadmin, contando bajo
  bloqueo si la hace otro superadmin).
- **R4 — Reglas que dejan la sesión Mentor al cierre.** Si David lo quiere, una línea en AGENTS §3 junto a "nadie cambia
  su propio rol" y la entrada en `docs/CONTEXT.md` con ADR-0017. Fila sugerida: ninguna (es el ritual de cierre).

## Referencias

- pydantic · 2.12.5 (`constraints.txt`) · conversión laxa de `str` a `bool` (caso `coerced-false` de H3):
  https://docs.pydantic.dev/2.12/concepts/conversion_table/ — **pendiente de consulta**: Context7 falló al conectar en
  esta sesión (timeout); la afirmación sale del conocimiento del redactor y la confirma el RED de la fase B (riesgo c).
- No hay otra API de librería nueva: las guardas usan `dict.get` y la excepción del dominio; los tests, fixtures existentes.

## Enmiendas aprobadas

### E0 — 16 nov 2026, 10:51 (David: "si, apruebo"; revisión de la sesión Mentor)

1. **Plan aprobado, dos fases, y ADR-0017 aceptado.** Las cuatro "decisiones pendientes de aprobación" del resumen (403
   con `AuthorizationError`; sin conteo; ADR-0017; la carrera desaparece por construcción) quedan aprobadas como se
   recomiendan: son las de la adenda de la verificación (10:31).
2. **Corrección de dictado, ya aplicada en la fase B (sección Tests).** El plan dictaba dos docstrings de clase para
   `tests/test_user_access_policy.py` que, con su sangría, miden 104 y 120 columnas (medido con el intérprete), y decía
   que "ruff format los parte si pasan de 100". No los parte: `ruff format` no reescribe cadenas ni docstrings, y
   `pyproject.toml` tiene `line-length = 100` con `select = ["E", …]` (E501) y solo ignora `D` en `tests/**`; la
   compuerta habría salido en rojo. Texto vigente, una línea cada uno (95 y 94 columnas):
   `"""Freezes the deletion invariant: own account or higher rank, never a superadmin's own."""` y
   `"""Freezes update invariants: hierarchy, role and is_active fail-safes, ADR-0017 guard."""`.
   Ningún conteo de la Verificación final cambia.
3. **Riesgo (c) cerrado por medición de la sesión Mentor** (pydantic 2.12.5, modelo mínimo con `is_active: bool | None`):
   `"false"`, `False`, `0`, `"0"`, `"no"` y `"False"` dan `{'is_active': False}` tras
   `model_dump(mode="json", exclude_unset=True)`; `None` da `{'is_active': None}`. El caso `coerced-false` de H3 se
   comporta como el plan supone. La referencia de pydantic "pendiente de consulta" queda cubierta por esta medición, no
   por la lectura de la documentación.
4. **Dato leído, no ejecutado:** `app/models/user.py:51` declara `is_active: Mapped[bool]` (sin `None`), así que
   `{"is_active": null}` no es una tercera vía de desactivación: choca con la base (BE-37). M6 sigue declarado vivo.
5. **Recalculado por la sesión Mentor, coincide con el plan:** 15 funciones `test_be35_` y 17 casos; 691 − 1 + 17 = 707;
   RED `11 failed, 6 passed`; conteos de los comandos 1, 5, 7, 8 y 9 de la Verificación final; anclas de
   `user_access_policy.py`, `user_service.py`, `routers/user.py` y `tests/test_user_access_policy.py`; las dos líneas
   `raise` dictadas miden 97 y 99 columnas. Las cifras de la suite y los mutantes los mide el ejecutor y los repite el
   auditor (el plan no las midió).
6. **R1 sigue abierto:** David no ha dicho aún si el cliente Flutter ofrece a un superadmin borrar o desactivar su
   propia cuenta. No bloquea ninguna fase.

# PLAN — BE-36: Permitir que un superadmin reactive a otro superadmin, y nada más

> Fuente: `docs/deuda/BE-36/verificacion.md` (confirmada; adenda de David, 16 nov 2026, 12:22, que fija la regla).
> Base: `62b9702` (HEAD de `item/be-36`; `app/` y `tests/` idénticos a `09f529b`, la línea base de la verificación:
> 707 passed, 97,65 %, ruff 0, mypy 0 en 63 archivos, 4 kept).
> **Estado: aprobado por David con E0 (16 nov 2026, 13:03).** `Aprobado: 16 nov 2026` (esa fecha es la `<FECHA>` del ADR
> de la fase A). Enmiendas al final, en "Enmiendas aprobadas".
> **Qué midió el redactor y qué no** (todo fuera del repo, en el scratchpad de la sesión; `git status` sin cambios propios):
> (1) la sonda de la provisión que pide la adenda (punto 3; salida literal en "Análisis"); (2) los 18 casos dictados
> contra el código de `62b9702`: `3 failed, 15 passed` (el RED de la fase B); (3) los mismos 18 casos con la política
> dictada sustituida por `monkeypatch`: `18 passed`; (4) la suite completa de `tests/` con esa sustitución: `707 passed`;
> (5) una copia de `app/` y `tests/` con todo lo que dicta la fase B: ruff format y ruff check limpios, mypy limpio,
> `725` tests recogidos y en verde salvo los 13 de `tests/test_check_docs.py` que leen `docs/` (la copia no lo tenía);
> (6) los mutantes N1–N6 de la fase B. **No medido:** la compuerta completa ni la cobertura; las mide el ejecutor. Si una
> cifra no cuadra, el ejecutor se detiene y lo anota en el handoff, sin "arreglar" código para que cuadre.

## Resumen para aprobación

Dos fases. (A) Escribe ADR-0018: entre pares nadie modifica a nadie, **salvo que un superadmin reactiva a otro**; la
excepción se acota a la clave `is_active` con valor `true`, sola, y a un objetivo fuera de la papelera. (B) Aplica la
regla en `UserAccessPolicy.assert_can_update` (una condición más en la guarda de jerarquía), ajusta dos docstrings de
`user_service.py` y añade 18 casos en `tests/test_user_access_policy.py` (707 → 725), entre ellos los dos caminos de
ida y vuelta medidos: recuperar → el par reactiva → el recuperado entra, y provisionar sin `is_active` → el par
reactiva → el nuevo entra. **La sonda de la provisión reprodujo la segunda puerta** (201 con `is_active` false, 403 al
reactivar, 403 al entrar).
**Riesgo principal:** coste aceptado por David en la adenda: una baja de superadmin hecha por SQL con solo
`is_active = false` deja de ser definitiva, porque otro superadmin la deshace desde la aplicación (dato para BE-55).
Segundo: un `PATCH` pasa de 403 a 200 (superadmin sobre superadmin con `{"is_active": true}`); no se ha comprobado
que el cliente Flutter lo ofrezca (residual R1).
**No se toca:** la recuperación (`recover_user_account` sigue dejando inactiva cualquier cuenta; `tests/test_auth.py`
intacto), el valor por defecto `False` de `UserCreateByAdmin.is_active`, las guardas de ADR-0017, ADR-0017,
`AGENTS.md` (la viñeta la edita David antes de `/pr`), excepciones, `_DOMAIN_ERROR_STATUS`, rutas, guards, BE-37,
BE-38, BE-55, BE-56, BE-57, A3.

**Decisiones que este plan toma y que quedan pendientes de aprobación al aprobarlo:**

1. **Superadmin sobre un superadmin aún en la papelera — pendiente. Recomendado: 403, como hoy** (recomendación de la
   sesión Mentor; la adenda no lo cierra). La condición `target.deleted_at is None` lo fija y dos tests lo congelan
   (medido hoy: 403). Trade-off: sin ella, un `PATCH {"is_active": true}` sobre una cuenta borrada daría 200 y la
   dejaría activa **y** borrada, saltándose la recuperación y su fila `RECOVER`; con ella, recuperar un superadmin
   sigue siendo dos pasos y dos filas de auditoría.
2. **Reactivar a un par que ya está activo — pendiente. Recomendado: 200, sin condición sobre el estado actual.** La
   excepción no mira `target.is_active`. Trade-off: un no-op escribe una fila `UPDATE` (es BE-38, que ya lo trata para
   todos los campos); exigir `is_active is False` añadiría una rama y un 403 que no protege nada.
3. **ADR-0018 — pendiente. Recomendado: sí, con el texto de la fase A** (adenda, punto 4). Complementa ADR-0017, no lo
   supersede: la excepción no desactiva, borra ni degrada (AGENTS §3, viñeta "Superadmins").
4. **Dónde viven los tests — pendiente. Recomendado: todos en `tests/test_user_access_policy.py`,** también los dos de
   ida y vuelta con login, junto a los de BE-02 y BE-35. Trade-off: `tests/test_auth.py` agrupa hoy recuperación y
   login, pero la adenda (punto 2) pide no tocar su l.334, y un solo archivo de tests deja la fase en tres archivos.

## Objetivo y decisiones bloqueadas

Que un superadmin inactivo, llegue por la papelera o por la provisión, tenga a alguien que lo active desde la
aplicación, sin abrir ninguna vía para desactivar, borrar, degradar ni editar a un superadmin.

1. Excepción única a la regla entre pares de `assert_can_update` (l.71): actor superadmin, objetivo superadmin fuera de
   la papelera, y el conjunto de cambios es **exactamente** `{"is_active": True}` (claves `{"is_active"}` y valor
   `is True`). Cualquier otra clave, sola o junto a `is_active`, y cualquier otro valor (`False`, `None`) → 403.
2. Entre admins no se abre nada; un admin sobre un superadmin sigue en 403.
3. La recuperación no cambia: deja inactiva la cuenta de cualquier rol (dos pasos: recuperar; después activar).
4. `UserCreateByAdmin.is_active` sigue con `False` por defecto.
5. Respuesta: 403 con `AuthorizationError` existente; sin excepción nueva. La política sigue pura, síncrona, con la misma
   firma.
6. ADR-0018 antes del código que lo cita. ADR-0017 no se edita. `AGENTS.md` no lo toca el plan (adenda, punto 5).

## Análisis del redactor

**Contraste con el código (`62b9702`).** Todo lo que la verificación cita sigue en su sitio: `user_access_policy.py:71`
(403 entre pares para cualquier clave), `:90-95` (guarda de ADR-0017, solo auto-edición y solo `False`), `:110`
(`assert_can_recover` deja a un superadmin recuperar a otro); `user_service.py:274` (el objetivo del `PATCH` se lee
con `include_deleted=True`), `:280` (`model_dump(mode="json", exclude_unset=True)`: llega un `bool` validado),
`:357-358` (la recuperación pone `deleted_at = None` e `is_active = False`), `:416` (la provisión copia
`user_data.is_active`); `schemas/user.py:130` (`is_active: bool = False`).

**Sonda de la provisión (adenda, punto 3).** Pila real de la suite (`client`, `persist_user`, `make_auth_headers`,
`db_session`), archivo en el scratchpad, ejecutado con
`./venv/Scripts/python.exe -m pytest -c pyproject.toml --rootdir . -p conftest -p tests.conftest <ruta>` desde la raíz.
Salida literal:

```
A POST /usuarios/admin (role=superadmin, sin is_active) -> 201 body.is_active=False
B en BD: role=superadmin is_active=False deleted_at=None
B POST /usuarios/login (antes del PATCH) -> 403
A PATCH B {'is_active': true} -> 403
B en BD tras PATCH: is_active=False
B POST /usuarios/login (tras el PATCH) -> 403
B GET /usuarios/mi-perfil (token firmado) -> 401
auditoria: [('CREATE', '777777', {'role': 'superadmin'})]
control: A POST admin sin is_active -> 201 is_active=False
control: A PATCH admin {'is_active': true} -> 200
control: login admin -> 200
papelera: A PATCH C (aun borrado) {'is_active': true} -> 403
```

Se reproduce: la provisión es una segunda puerta al mismo callejón y **sigue abierta desde la aplicación** tras
ADR-0017 (la papelera, no: un superadmin solo llega a ella por SQL). Entra en los tests como segundo camino (H2).

**Qué se cambia y por qué.** Una condición nombrada antes de la guarda de jerarquía, que la deja pasar solo en el caso
de la excepción. Es una regla que depende del dato (rol del objetivo, `deleted_at`, contenido del cambio), así que va
en la política (ADR-0012, punto 2). Va **dentro** de la guarda de `:71`, no como `return` temprano: las guardas
siguientes (`role`, turistas, ADR-0017) siguen ejecutándose, y una guarda que se añada mañana también. La condición
`target.role == UserRole.superadmin` es redundante en lógica (con actor superadmin, `:71` solo dispara si el objetivo
también lo es) y se deja por legibilidad: es el mutante equivalente N3, declarado.

Código que dicta la fase B (sustituye `user_access_policy.py:69-71`, sin tocar el `raise` de `:72-74`):

```python
        is_self_update = actor.cedula == target.cedula
        # ADR-0018: a superadmin may reactivate a peer outside the recycle bin, nothing else.
        is_peer_reactivation = (
            actor.role == UserRole.superadmin
            and target.role == UserRole.superadmin
            and target.deleted_at is None
            and set(update_dict) == {"is_active"}
            and update_dict["is_active"] is True
        )

        if (
            not is_self_update
            and not is_peer_reactivation
            and self._ROLE_RANK[actor.role] <= self._ROLE_RANK[target.role]
        ):
```

`ruff format` lo deja tal cual (medido en la copia); el comentario mide 93 columnas.

**Orden y dependencias.** A (ADR, 1 archivo) primero, porque los docstrings de B citan ADR-0018. B depende solo de A.
Regla, docstrings y tests en un commit, como en BE-02 y BE-35: separar el código de sus docstrings dejaría un commit en
que el código miente.

**Tests que congelan comportamiento relacionado** (leídos; con la política dictada, `707 passed` medido). Siguen en
verde sin tocarlos: `test_superadmin_cannot_update_peer_superadmin` (`tests/test_user_access_policy.py:162-167`,
`first_name` entre pares), `test_admin_cannot_update_superadmin` (`:130`), `test_superadmin_can_recover_superadmin`
(`:281`), los BE-35 (`:236-263`, `:781-951`), `tests/test_auth.py:334` (recuperación de turista, inactivo) y `:358`
(admin → superadmin, 403), `:412` (provisión de admin con `is_active: true`). `tests/test_user_service.py` usa la
política con `autospec`: no la ejecuta. Ninguna ruta cambia: `tests/test_route_guards.py` no se toca.

**Mutantes de la regla** (medidos en el scratchpad con los 18 casos dictados; el auditor los repite sobre una copia):
N1 quitar `and not is_peer_reactivation` → mueren U1, H1, H2. N2 quitar `actor.role == UserRole.superadmin` → muere U6.
N4 quitar `target.deleted_at is None` → mueren U4, H5. N5 quitar `set(update_dict) == {"is_active"}` → mueren U3
(`with-profile-field`, `with-role`, `role-only`, `empty`) y H3 (×3). N6 quitar `update_dict["is_active"] is True` →
mueren U2, U3 `null`, H4. **N3 quitar `target.role == UserRole.superadmin` sobrevive: es equivalente** (ver arriba).

**Riesgos.** (a) El coste de producto aceptado (resumen; ADR-0018). (b) Contrato: un caso 403 → 200; cliente sin
verificar (R1). (c) Las líneas dictadas cerca del límite (hasta 99 columnas en tests) están medidas con el intérprete,
no a ojo (lección de la E0 de BE-35); si `ruff check` da E501, el ejecutor se detiene.

**Qué NO se toca.** `recover_user_account` (lógica y mensaje), `assert_can_recover`, `assert_can_delete`, las guardas de
`:76-95`, `app/schemas/`, `app/core/`, `app/main.py`, `app/api/` (el contrato de `recuperar_usuario` no cambia y el
docstring del `PATCH` no describe la jerarquía), `app/repositories/` (`activate_user`, A3), `superadmin_bootstrap.py`,
`tests/test_auth.py`, `tests/test_user_service.py`, `tests/test_route_guards.py`, `tests/conftest.py`.

## Regla de alcance

**Sí:** ADR-0018; la excepción en la guarda de jerarquía de `assert_can_update`; los docstrings que describen la regla
entre pares en `user_access_policy.py` (clase y `assert_can_update`) y en `user_service.py` (`update_user_account` y
`recover_user_account`); los tests nuevos en `tests/test_user_access_policy.py`.
**No:** que la recuperación reactive; el valor por defecto de `is_active` en la provisión; cualquier otra clave entre
pares; reglas entre admins; `{"is_active": null}` en general (BE-37); auditoría de no-ops (BE-38); baja de superadmins
(BE-55); el mensaje del login de una cuenta inactiva (BE-56); la edición de cuentas en la papelera para rangos inferiores
(BE-57); `AGENTS.md`, `docs/CONTEXT.md`, `docs/backlog.md` (los actualizan David y la sesión Mentor al cierre).

## Fases

### Fase A — ADR-0018 (la más pequeña)

- **Archivos (1):** `docs/adr/0018-un-superadmin-reactiva-a-otro.md` (nuevo). Dominio: decisiones (docs).
- **Cambios exactos:** crear el archivo con este texto; `<FECHA>` es la de la línea `Aprobado:` de la cabecera de este
  plan.

  ```markdown
  # ADR-0018 — Un superadmin puede reactivar a otro superadmin, y nada más

  - **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-36)
  - **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 12:22)
  - **Ubicación en el repo:** `docs/adr/0018-un-superadmin-reactiva-a-otro.md`
  - **Origen:** backlog BE-36; `docs/deuda/BE-36/verificacion.md` (veredicto y adenda); `docs/deuda/BE-36/plan.md`.
    Relación: ADR-0017 (lo complementa, no lo supersede: ver Consecuencias), ADR-0012 (una regla que depende del dato
    va en la política), ADR-0003 (`AuthorizationError` → 403), ADR-0009 (no es un addendum de ADR-0017: abre un caso
    que ese ADR no trataba), BE-55 (baja de un superadmin sin SQL directo).

  ## Contexto

  Entre pares nadie modifica a nadie: `UserAccessPolicy.assert_can_update` responde 403 cuando el objetivo no tiene un
  rango estrictamente menor que el del actor, sea cual sea el cambio. Nadie está por encima de un superadmin, así que
  un superadmin inactivo no tiene a nadie que lo active. Dos puertas llevan a ese estado, medidas el 16 nov con la pila
  real de la suite:

  1. **Recuperación.** `PATCH /usuarios/{cédula}/recuperar` deja la cuenta de cualquier rol con `is_active = false`, a la
     espera de que alguien la active; entre superadmins esa activación da 403, y el recuperado recibe 403 al entrar.
     Desde ADR-0017 un superadmin solo llega a la papelera por SQL directo o si ya estaba en ella.
  2. **Provisión.** `POST /usuarios/admin` con `role = superadmin` y sin `is_active` crea la cuenta inactiva (el schema
     lo pone a `false` por defecto); el `PATCH {"is_active": true}` de su creador da 403 y el nuevo no puede entrar.
     Esta puerta sigue abierta desde la aplicación.

  ## Decisión

  1. **Excepción única a la regla entre pares:** un superadmin puede actualizar a otro superadmin cuando el conjunto de
     cambios es exactamente `{"is_active": true}`. Cualquier otra clave, sola o junto a `is_active`, y cualquier otro
     valor (`false`, `null`) siguen dando 403. Entre admins no se abre nada.
  2. **La excepción lee la clave y el valor.** Si leyera solo la clave, dejaría que un superadmin desactivase a otro,
     que es lo que ADR-0017 cierra.
  3. **El objetivo no puede estar en la papelera.** Reactivar no sustituye a la recuperación ni a su fila de auditoría:
     un superadmin borrado se recupera primero y se reactiva después.
  4. **Nada más cambia:** la recuperación sigue dejando inactiva la cuenta de cualquier rol, el valor por defecto de
     `is_active` en la provisión sigue en `false`, la respuesta sigue siendo 403 con `AuthorizationError` y la política
     sigue pura, síncrona y con la misma firma.

  ## Consecuencias

  - **Coste aceptado (David, 16 nov):** si un operador da de baja a un superadmin por SQL poniendo solo
    `is_active = false` (la baja que deja ADR-0017), otro superadmin puede reactivarlo desde la aplicación. Una baja que
    deba ser definitiva no puede consistir solo en `is_active = false`: dato para BE-55.
  - **La premisa de ADR-0017 sigue en pie.** "Entre pares nadie modifica a nadie" pasa a ser "entre pares nadie
    modifica a nadie, salvo que un superadmin reactiva a otro". Para desactivar, borrar y degradar sigue siendo cierta:
    el número de superadmins activos no baja desde la aplicación; la excepción solo puede subirlo.
  - Cambio de contrato: `PATCH /usuarios/{cédula}` con `{"is_active": true}` de un superadmin sobre otro que no está en
    la papelera pasa de 403 a 200 y escribe una fila de auditoría `UPDATE`. Ninguna otra petición cambia.
  - Reactivar a un par que ya está activo también da 200 y escribe la fila aunque nada cambie (BE-38).
  - La viñeta "Superadmins" de AGENTS §3 recoge la excepción; la edita David.

  ## Alternativas consideradas

  1. **Que la recuperación reactive cuando actor y objetivo son superadmins.** Descartada: no cubre la puerta de la
     provisión, y haría de la recuperación una reactivación inmediata solo para un rol.
  2. **Permitir la clave `is_active` entre pares, con cualquier valor.** Rechazada: dejaría a un superadmin desactivar a
     otro, que ADR-0017 cierra; exigiría superseder ese ADR.
  3. **Poner a `true` el valor por defecto de `is_active` en la provisión.** Fuera de este ADR por decisión de David:
     solo cierra la segunda puerta y cambia lo que hoy recibe quien provisiona a un admin.
  4. **No hacer nada.** Rechazada: un superadmin provisionado sin `is_active` no puede entrar nunca, y nadie lo arregla
     sin SQL.

  ## Evidencia

  - Verificación (16 nov, pila real de la suite): recuperar a un par → 200 con `is_active` false; `PATCH
    {"is_active": true}` del par → 403; login del recuperado → 403. Superadmin → admin y admin → turista, mismo
    mecanismo: 200 · 200 · 200.
  - Sonda del planificador (16 nov, pila real de la suite, fuera de `tests/`): el superadmin A crea al superadmin B sin
    `is_active` → 201, B inactivo; login de B → 403; `PATCH {"is_active": true}` de A sobre B → 403; login de B → 403.
    Un admin provisionado igual: 201 · 200 · 200. Superadmin aún en la papelera, `PATCH {"is_active": true}` → 403.
  - Tests y mutantes de la regla: `docs/deuda/BE-36/plan.md`, fase B.
  ```

- **Tests (RED primero):** no aplica (solo documentación). Comprobación sustituta: `./venv/Scripts/python.exe
  scripts/check.py --no-tests` en verde (`check_docs` no escanea `docs/adr`) y `git diff --stat` = 1 archivo nuevo.
- **Criterio de aceptación:** el archivo existe con el texto dictado y `<FECHA>` sustituida; `git grep -l 'ADR-0018' --
  docs/adr` = solo `docs/adr/0018-un-superadmin-reactiva-a-otro.md`; `git diff --stat 62b9702 HEAD --
  docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md` vacío; compuerta completa en verde con 707 passed.
- **Fuera de alcance de esta fase:** cualquier archivo de `app/` o `tests/`; ADR-0017; `AGENTS.md`,
  `docs/CONTEXT.md`, `docs/backlog.md`.
- **Commit:**
  ```
  docs(adr): add ADR-0018, a superadmin may reactivate a peer superadmin

  Between peers nobody modifies anybody, and nobody outranks a
  superadmin, so an inactive superadmin has nobody who can activate it
  (BE-36). Two doors lead there: the recycle bin, whose recovery leaves
  every account inactive, and provisioning, where POST /usuarios/admin
  without is_active creates the account inactive. Both were measured
  through the real HTTP stack: the peer's PATCH {"is_active": true}
  gets 403 and the account can never log in.

  The ADR records David's decision before the code that cites it
  lands: the only exception to the peer rule is a superadmin sending
  exactly {"is_active": true} to another superadmin outside the
  recycle bin. ADR-0017 stands, since peers still cannot deactivate,
  delete or demote each other. It declares the accepted cost: an
  operator's SQL removal that only sets is_active to false can now be
  undone from the application, which BE-55 has to take into account.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — La excepción en `UserAccessPolicy`, sus docstrings y sus tests

- **Archivos (3):** `app/services/user_access_policy.py`, `app/services/user_service.py` (solo docstrings),
  `tests/test_user_access_policy.py`. Dominio: autorización sobre cuentas de usuario.
- **Cambios exactos en `app/`** (el código, en "Análisis del redactor"; los textos, aquí):
  - `user_access_policy.py`, docstring de la clase: tras la l.14 (`deactivates it, so the number of superadmins never
    drops (ADR-0017).`), que pasa a terminar en `(ADR-0017). One`, añadir dos líneas; el bloque `:10-14` queda:
    ```
        All guarded mutations follow a hierarchical dominance invariant over role
        ranks: an actor may update or delete their own account, while third-party
        operations require a strictly higher rank. Two exceptions on one's own
        account: nobody changes their own role, and a superadmin never deletes or
        deactivates it, so the number of superadmins never drops (ADR-0017). One
        exception between peers: a superadmin may reactivate another superadmin
        outside the recycle bin, sending is_active true and nothing else (ADR-0018).
    ```
  - `assert_can_update`, docstring: la l.53 pasa a tres líneas (el resto del párrafo, `:54-58`, no cambia):
    ```
            The target must be the actor's own account or one of strictly lower rank,
            except a peer superadmin outside the recycle bin when a superadmin sends
            is_active true and nothing else (ADR-0018).
    ```
  - `assert_can_update`, código: el bloque dictado sustituye `:69-71`.
  - `user_service.py`, docstring de `update_user_account`: tras la l.259, añadir:
    ```
            One exception to the rank rule: a superadmin may reactivate another
            superadmin outside the recycle bin, sending is_active true and nothing
            else (ADR-0018).
    ```
  - `user_service.py`, docstring de `recover_user_account`: tras la l.334, añadir:
    ```
            For a recovered superadmin, that approval is another superadmin sending
            is_active true (ADR-0018).
    ```
- **Tests (RED primero)** — en `tests/test_user_access_policy.py`, escritos y ejecutados **antes** de tocar `app/`. Texto
  literal en el Anexo (medido con ruff y con el intérprete); aquí, qué prueba cada uno:
  - Imports: `from app.core.security import get_password_hash` tras la l.18; la l.21 pasa a
    `from app.models.user import User, UserRole`.
  - Unitarios, al final de `TestAssertCanUpdate` (tras la l.263), con `make_user` y `policy`:
    U1 `test_be36_superadmin_can_reactivate_peer_superadmin` — superadmin → superadmin inactivo, `{"is_active": True}`
    no lanza. U2 `test_be36_peer_superadmin_deactivation_is_rejected` — `{"is_active": False}` lanza. U3
    `test_be36_peer_superadmin_update_other_than_reactivation_is_rejected`, parametrizado ×5 (`with-profile-field`,
    `with-role`, `role-only`, `null`, `empty`) — lanza. U4 `test_be36_superadmin_cannot_reactivate_peer_in_recycle_bin`
    — objetivo con `deleted_at`, lanza. U5 `test_be36_admin_cannot_reactivate_peer_admin` — lanza. U6
    `test_be36_admin_cannot_reactivate_superadmin` — lanza.
  - HTTP, sección nueva al final del bloque B (tras la l.951, antes de `# C. GLOBAL EXCEPTION HANDLER TESTS`), cabecera
    `# --- BE-36 regression: a superadmin reactivates a peer superadmin, and nothing else ---` y constante
    `BE36_PASSWORD = "Password123"`. Fixtures `client`, `db_session`, `persist_user`, `make_auth_headers`; `refresh`
    tras las peticiones (ADR-0011):
    H1 `test_be36_recovered_superadmin_reactivated_by_peer_can_log_in` — **ida y vuelta de la fila**: recuperar → 200;
    login → 403 (la recuperación no cambia); `PATCH {"is_active": true}` del par → 200 (`cedula`, `role`, `is_active`);
    login → 200 con `{"access_token", "token_type"}`; `deleted_at is None`, `is_active is True`; auditoría exacta
    `[RECOVER, UPDATE {"is_active": True}]`, ambas con `performed_by` del par.
    H2 `test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in` — **puerta de la provisión**:
    `POST /usuarios/admin` sin `is_active` → 201 con `is_active` false; login → 403; `PATCH` → 200; login → 200;
    fila releída con `select`; auditoría exacta `[CREATE {"role": "superadmin"}, UPDATE {"is_active": True}]`.
    H3 `test_be36_peer_superadmin_update_other_than_reactivation_returns_403`, ×3 (`with-profile-field`,
    `profile-only`, `role-only`) — 403, `{"detail"}` y `str`; sin mutación (`is_active`, `first_name`, `role`);
    auditoría `[]`. H4 `test_be36_peer_superadmin_deactivation_still_returns_403` — par activo, `{"is_active": False}`
    → 403; sigue activo; auditoría `[]`. H5 `test_be36_peer_still_in_recycle_bin_reactivation_returns_403` — 403;
    sigue inactivo y en la papelera; auditoría `[]` (decisión pendiente 1). H6
    `test_be36_admin_reactivating_peer_admin_returns_403` — 403; sigue inactivo; auditoría `[]`.
  - **RED esperado** (medido contra `62b9702`):
    `./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be36 -q` → `3 failed, 15 passed`. Fallan
    U1, H1 y H2. Pasan ya los 15 bordes que impiden que la excepción deje pasar de más (mueren con N2, N4, N5, N6).
- **Criterio de aceptación:** `-k be36` → `18 passed`; suite completa `725 passed` (707 + 18); compuerta
  `./venv/Scripts/python.exe scripts/check.py` con salida 0, ruff 0, mypy 0, 4 kept y cobertura ≥ 97,65 %
  (`user_access_policy.py` sigue al 100 %); los comandos 1–12 de la verificación final dan lo esperado; mutantes N1,
  N2, N4, N5 y N6 muertos y N3 vivo (equivalente), anotados en el handoff.
- **Fuera de alcance de esta fase:** lógica de `user_service.py` (`recover_user_account` y
  `create_administrative_account` incluidas); `assert_can_recover`, `assert_can_delete` y las guardas `:76-95`;
  schemas, `exceptions.py`, `main.py`, `app/api/`; `tests/test_auth.py`, `tests/test_user_service.py`,
  `tests/test_route_guards.py`; `{"is_active": null}` fuera del par de superadmins (BE-37); auditoría de no-ops (BE-38);
  BE-56; BE-57.
- **Commit:**
  ```
  fix(access-policy): let a superadmin reactivate a peer superadmin

  A superadmin recovered from the recycle bin, or provisioned without
  is_active, stays inactive for good: the hierarchy guard of
  assert_can_update rejects any change between peers with 403, and
  nobody outranks a superadmin (BE-36, both doors measured). David
  chose one narrow exception over making the recovery reactivate,
  because the recovery path does not cover provisioning (ADR-0018).

  - app/services/user_access_policy.py: the hierarchy guard lets a
    superadmin through on another superadmin only when the change set
    is exactly {"is_active": true} and the target is not in the
    recycle bin. It reads keys and value, so false, null or any extra
    key still get 403 and ADR-0017 holds. Same exception, same 403,
    same pure signature.
  - app/services/user_service.py: the update and recovery docstrings
    name the exception and who approves a recovered superadmin. No
    logic change: the recovery still leaves every account inactive.
  - tests/test_user_access_policy.py: unit and HTTP cases for the
    round trip of the row (recover, the peer reactivates, the
    recovered one logs in) and for the provisioning door, plus the
    boundaries that stay 403: deactivation, extra keys, role, an empty
    or null change, a peer still in the recycle bin, admin on admin
    and admin on superadmin.

  The schema default of is_active stays false. The login message of
  an inactive account is BE-56; editing accounts in the recycle bin
  is BE-57.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase B. Los conteos incluyen el texto que dicta este plan (código, docstrings,
comentarios, nombres y docstrings de tests) y están medidos con `grep` sobre una copia de `app/` y `tests/` con la fase
B aplicada. Patrones 1–6 = los de la verificación, recalculados.

```bash
# 1. Patrón 1: la recuperación sigue forzando la cuenta a inactiva → 1 línea, app/services/user_service.py
git grep -n -E "target_user\.is_active = False" -- app

# 2. Patrón 2: única escritura de is_active = True → 1 línea, app/repositories/user_repository.py (sin cambio)
git grep -n -E "\.is_active = True" -- app

# 3. Patrón 3: la guarda de jerarquía ya no es de una línea → 0 líneas (exit 1)
git grep -n -E "not is_self_update and self\._ROLE_RANK" -- app

# 4. La excepción y su uso en la guarda → 2 líneas, ambas en app/services/user_access_policy.py
git grep -n -F "is_peer_reactivation" -- app

# 5. La excepción lee claves y valor → 1 línea cada comando, en app/services/user_access_policy.py
git grep -n -F 'set(update_dict) == {"is_active"}' -- app
git grep -n -F 'update_dict["is_active"] is True' -- app

# 6. Patrón 4: quién recupera a quién → las mismas 4 líneas de la base (router, política, servicio ×2)
git grep -n -E "assert_can_recover|recover_user_account" -- app

# 7. Patrón 5: escrituras de deleted_at sobre usuarios → las mismas 2 líneas (user_repository.py, user_service.py)
git grep -n -E "deleted_at\s*=[^=]" -- app/repositories/user_repository.py app/services/user_service.py

# 8. Patrón 6: tests que tocan la recuperación → 27 líneas (22 de la base + 5 de H1 y H5)
git grep -n -E "recuperar|recover" -- tests/test_auth.py tests/test_user_access_policy.py tests/test_user_service.py | wc -l

# 9. Citas de la decisión → app: 5 líneas (user_access_policy.py 3: clase, docstring, comentario;
#    user_service.py 2); tests: 0 (exit 1); docs/adr: solo el archivo 0018; ADR-0017 en app sigue en 7 líneas
git grep -n 'ADR-0018' -- app
git grep -n 'ADR-0018' -- tests
git grep -l 'ADR-0018' -- docs/adr
git grep -n 'ADR-0017' -- app | wc -l

# 10. El valor por defecto de la provisión no cambia → 1 línea, app/schemas/user.py:130
git grep -n 'is_active: bool = False' -- app/schemas/user.py

# 11. Nada fuera del alcance → salida vacía
git diff --stat 62b9702 HEAD -- app/schemas app/core app/main.py app/repositories app/api app/models app/cli tests/test_auth.py tests/test_user_service.py tests/test_route_guards.py tests/conftest.py conftest.py AGENTS.md docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md

# 12. Tests del ítem → 12 funciones; 18 casos en verde
git grep -c 'def test_be36_' -- tests/test_user_access_policy.py      # → tests/test_user_access_policy.py:12
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be36 -q   # → 18 passed

# 13. Compuerta completa → salida 0; 725 passed; cobertura ≥ 97,65 %; ruff 0; mypy 0; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

- **R1 — Cliente Flutter sin verificar.** `PATCH {"is_active": true}` de un superadmin sobre otro pasa de 403 a 200, y la
  provisión de un superadmin sin `is_active` ahora tiene arreglo. Nadie ha comprobado si alguna pantalla ofrece activar
  a un superadmin, ni si la de provisión envía `is_active`. Evidencia: ninguna en el repo backend. Destino: nota en la
  fila BE-36 al cierre (sesión Mentor), como la de BE-35.
- **R2 — Reglas y estado que se actualizan al cierre.** La viñeta "Superadmins (ADR-0017)" de AGENTS §3 (adenda,
  punto 5, la edita David antes de `/pr`) y la entrada de ADR-0018 en `docs/CONTEXT.md`. ADR-0017 dice en sus
  Consecuencias "BE-36 sigue abierta"; no se edita (ADR aceptado): ADR-0018 lo cita en su Origen. Fila sugerida:
  ninguna (ritual de cierre).
- **R3 — Dato para BE-55.** Con ADR-0018, una baja por SQL que solo pone `is_active = false` es reversible desde la
  aplicación. Destino: nota en la fila BE-55 ("una baja definitiva no puede ser solo `is_active = false`").
- BE-56 y BE-57 (adenda, punto 6) **ya tienen fila** en `docs/backlog.md` (l.107 y l.108, del commit `62b9702`): este
  plan no crea ninguna.

## Referencias

- Ninguna API de librería nueva: la excepción usa `set()`, comparación de conjuntos y la excepción del dominio; los
  tests, fixtures existentes y `pytest.mark.parametrize`, ya usados en el mismo archivo. No hizo falta Context7 (además,
  falló al conectar en esta sesión). El comportamiento que el plan da por supuesto de pydantic (`model_dump` entrega
  `bool`) quedó medido en la E0 de BE-35 (`docs/deuda/BE-35/plan.md`, "Enmiendas aprobadas", punto 3).

## Anexo — texto literal de los tests de la fase B

Unitarios, al final de `TestAssertCanUpdate` (tras la l.263, separados por una línea en blanco):

```python
    def test_be36_superadmin_can_reactivate_peer_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_peer_superadmin_deactivation_is_rejected(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": False})

    @pytest.mark.parametrize(
        "update_dict",
        [
            {"is_active": True, "first_name": "Changed"},
            {"is_active": True, "role": "superadmin"},
            {"role": "admin"},
            {"is_active": None},
            {},
        ],
        ids=["with-profile-field", "with-role", "role-only", "null", "empty"],
    )
    def test_be36_peer_superadmin_update_other_than_reactivation_is_rejected(
        self, policy, make_user, update_dict
    ):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, update_dict)

    def test_be36_superadmin_cannot_reactivate_peer_in_recycle_bin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC))

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_admin_cannot_reactivate_peer_admin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.admin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_admin_cannot_reactivate_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})
```

HTTP, tras la l.951 (dos líneas en blanco antes de la cabecera y dos después del último test, antes de
`# ==========================================` de la sección C):

```python
# --- BE-36 regression: a superadmin reactivates a peer superadmin, and nothing else ---

BE36_PASSWORD = "Password123"


async def test_be36_recovered_superadmin_reactivated_by_peer_can_log_in(
    client, db_session, persist_user, make_auth_headers
):
    """Round trip of the row: recover, the peer reactivates, the recovered one logs in."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(
        role=UserRole.superadmin,
        is_active=False,
        deleted_at=datetime.now(UTC),
        password_hash=get_password_hash(BE36_PASSWORD),
    )
    headers = make_auth_headers(superadmin)
    credentials = {"email": peer.email, "password": BE36_PASSWORD}

    recovered = await client.patch(f"/usuarios/{peer.cedula}/recuperar", headers=headers)
    login_before = await client.post("/usuarios/login", json=credentials)
    reactivated = await client.patch(
        f"/usuarios/{peer.cedula}", json={"is_active": True}, headers=headers
    )
    login_after = await client.post("/usuarios/login", json=credentials)

    assert recovered.status_code == 200
    assert login_before.status_code == 403
    assert reactivated.status_code == 200
    body = reactivated.json()
    assert body["cedula"] == peer.cedula
    assert body["role"] == "superadmin"
    assert body["is_active"] is True
    assert login_after.status_code == 200
    assert set(login_after.json()) == {"access_token", "token_type"}

    await db_session.refresh(peer)
    assert peer.deleted_at is None
    assert peer.is_active is True
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (AuditAction.RECOVER, peer.cedula, superadmin.cedula, None),
        (AuditAction.UPDATE, peer.cedula, superadmin.cedula, {"is_active": True}),
    ]


async def test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in(
    client, db_session, persist_user, make_auth_headers
):
    """Second door: a superadmin created without is_active is born inactive; a peer fixes it."""
    superadmin = await persist_user(role=UserRole.superadmin)
    headers = make_auth_headers(superadmin)
    payload = {
        "cedula": "777777",
        "email": "newsuper@test.com",
        "first_name": "Nuevo",
        "last_name": "Super",
        "phone": "3000000000",
        "password": BE36_PASSWORD,
        "role": "superadmin",
        "data_consent": True,
    }
    credentials = {"email": payload["email"], "password": BE36_PASSWORD}

    created = await client.post("/usuarios/admin", json=payload, headers=headers)
    login_before = await client.post("/usuarios/login", json=credentials)
    reactivated = await client.patch("/usuarios/777777", json={"is_active": True}, headers=headers)
    login_after = await client.post("/usuarios/login", json=credentials)

    assert created.status_code == 201
    assert created.json()["is_active"] is False
    assert login_before.status_code == 403
    assert reactivated.status_code == 200
    assert reactivated.json()["is_active"] is True
    assert login_after.status_code == 200
    assert set(login_after.json()) == {"access_token", "token_type"}

    provisioned = (
        await db_session.execute(select(User).where(User.cedula == "777777"))
    ).scalar_one()
    assert provisioned.role == UserRole.superadmin
    assert provisioned.is_active is True
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (AuditAction.CREATE, "777777", superadmin.cedula, {"role": "superadmin"}),
        (AuditAction.UPDATE, "777777", superadmin.cedula, {"is_active": True}),
    ]


@pytest.mark.parametrize(
    "payload",
    [{"is_active": True, "first_name": "Changed"}, {"first_name": "Changed"}, {"role": "admin"}],
    ids=["with-profile-field", "profile-only", "role-only"],
)
async def test_be36_peer_superadmin_update_other_than_reactivation_returns_403(
    client, db_session, persist_user, make_auth_headers, payload
):
    """Any other key, alone or next to is_active true, is still 403; nothing is written."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}", json=payload, headers=make_auth_headers(superadmin)
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(peer)
    assert peer.is_active is False
    assert peer.first_name == "John"
    assert peer.role == UserRole.superadmin
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_peer_superadmin_deactivation_still_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The exception reads the value: is_active false on a peer is still 403 (ADR-0017)."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": False},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is True
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_peer_still_in_recycle_bin_reactivation_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Reactivation does not skip the recovery: a peer still in the recycle bin stays 403."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(
        role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC)
    )

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is False
    assert peer.deleted_at is not None
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_admin_reactivating_peer_admin_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The exception is only between superadmins: an admin reactivating a peer admin gets 403."""
    admin = await persist_user(role=UserRole.admin)
    peer = await persist_user(role=UserRole.admin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is False
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []
```

Líneas más largas que dicta el Anexo, medidas con el intérprete: 99 columnas (`target = make_user(…deleted_at=…)` de
U4 y `reactivated = await client.patch("/usuarios/777777", …)` de H2) y 97 (docstring de H6 y lista de H3). Ninguna
pasa de 100. Las unitarias no llevan docstring (`tests/**` ignora `D`, como las de BE-35 en la misma clase).

## Enmiendas aprobadas

### E0 — 16 nov 2026, 13:03 (David: "apruebo"; revisión de la sesión Mentor)

1. **Plan aprobado, dos fases, y ADR-0018 aceptado.** Las cuatro decisiones pendientes del resumen quedan aprobadas como
   se recomiendan: (1) un superadmin aún en la papelera no se reactiva, 403; (2) reactivar a un par ya activo da 200,
   sin condición sobre el estado actual; (3) ADR-0018 con el texto de la fase A; (4) todos los tests en
   `tests/test_user_access_policy.py`.
2. **Sin correcciones de dictado.** Contraste de la sesión Mentor contra el código de `62b9702`: anclas
   `user_access_policy.py:14, :53, :69-71`, `user_service.py:259, :334`, `tests/test_user_access_policy.py:18, :21,
   :263, :951`; imports ya presentes en el archivo de tests (`datetime`/`UTC` l.10, `select` l.14, `AuditAction` y
   `AuditLog` l.20); los bordes que pedía la adenda están todos como test. Lógica del bloque dictado leída: la
   comparación de conjuntos precede al acceso por clave, y la excepción va dentro de la guarda de jerarquía, así que
   las guardas siguientes siguen ejecutándose. Las cifras (RED, 725, mutantes) las midió el planificador en una copia;
   la compuerta y la cobertura las mide el ejecutor y las repite el auditor.
3. **Orden que el plan impone a David:** la viñeta de AGENTS §3 (adenda, punto 5) se commitea **después** de la
   auditoría de la fase B y antes de `/pr`. El comando 11 de la Verificación final exige que `AGENTS.md` no haya
   cambiado desde `62b9702`; un commit anterior lo pondría en rojo sin que el ítem haya hecho nada mal.
4. **R1, respuesta parcial de David (de memoria, sin evidencia en este repositorio):** en el cliente Flutter todo
   usuario que se crea va por defecto a "por activar", una columna del kanban que ven admins y superadmins al crear
   usuarios. Si es así, la provisión sin `is_active` es el camino normal del cliente y no un descuido: la segunda
   puerta de ADR-0018 se abre cada vez que se crea un superadmin, y pasar una tarjeta de superadmin de "por activar" a
   activo es el `PATCH` que hoy da 403 y que este ítem pasa a 200. Queda por comprobar en el cliente qué cuerpo envía
   ese movimiento (la excepción exige exactamente `{"is_active": true}`): nota en la fila BE-36 al cierre.

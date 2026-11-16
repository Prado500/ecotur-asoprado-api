# PLAN — BE-58: Impedir que una cuenta administrativa se borre o se desactive a sí misma

> Fuente: `docs/deuda/BE-58/verificacion.md` (confirmada; adenda de David, 16 nov 2026, 18:02, que fija las decisiones).
> Base: `2cc8f73` (HEAD de `item/be-58`; `app/`, `tests/`, `conftest.py` y `pyproject.toml` idénticos a `6b168e1`, la
> línea base de la verificación: 726 passed, 97,65 %, ruff 0, mypy 0 en 63 archivos, 4 kept).
> **Estado: aprobado por David con E0 (16 nov 2026, 18:50).** `Aprobado: 16 nov 2026` (esa es la `<FECHA>` de la fase
> A: ADR-0019 y línea "Estado" de ADR-0017). Enmiendas al final, en "Enmiendas aprobadas".
> **Qué midió el redactor** (todo fuera del repo, en el scratchpad de la sesión; `git status` del repo sin cambios
> propios fuera de `docs/deuda/BE-58/`): (1) los 7 casos be58 dictados contra el código de `2cc8f73`, con el comando de
> la casa desde la raíz y en una copia `git archive` de `2cc8f73` con solo el archivo de tests cambiado (RED); (2) una
> copia `git archive` de `2cc8f73` con **todo** lo que dicta la fase B: compuerta `scripts/check.py` completa, exit 0
> (GREEN, cifras abajo); (3) 17 mutantes de la política sobre esa copia, suite completa cada uno; (4) la longitud de cada
> línea dictada, con el intérprete; (5) los conteos de la Verificación final, con `grep` sobre una copia con las fases A
> y B aplicadas. Si una cifra no cuadra, el ejecutor se detiene y lo anota en el handoff, sin "arreglar" código para que
> cuadre.

## Resumen para aprobación

Dos fases. (A) Escribe ADR-0019: ninguna cuenta administrativa (la de todo rol que no sea turista) se borra ni se
desactiva a sí misma, porque solo un superadmin decide cuándo se da de baja una cuenta administrativa; supersede
parcialmente a ADR-0017 (el alcance "superadmin" de sus dos guardas y la consecuencia "Turistas y admins no cambian") y
anota esa supersesión en la línea "Estado" de ADR-0017. (B) Amplía las dos guardas de ADR-0017 en `UserAccessPolicy` de
`actor.role == UserRole.superadmin` a `actor.role != UserRole.tourist`, cambia sus dos avisos por los textos de David,
corrige los docstrings de política, servicio y router, invierte los dos tests de BE-35 que congelaban lo contrario y
añade 5 casos HTTP (726 → 731, medido en copia con la compuerta completa).
**Riesgo principal:** cambio de contrato; para un admin sobre sí mismo, `DELETE` y `PATCH {"is_active": false}` pasan
de 200 a 403 (el cliente ya muestra el `detail` de un 403). Segundo: el aviso nuevo también lo recibe un superadmin, y
para él "Solicítelo a un superadministrador" no tiene salida desde la aplicación (decisión pendiente 2).
**No se toca:** el borrado propio del turista ni su 403 al enviar `is_active`, lo que un superadmin hace sobre un admin,
ADR-0018, `AGENTS.md` (la viñeta la edita David tras la última auditoría y antes de `/pr`), excepciones,
`_DOMAIN_ERROR_STATUS`, rutas, guards, `tests/test_route_guards.py`, BE-37, BE-38, BE-55, BE-56, BE-57.

**Decisiones que la adenda no cierra y que quedan pendientes de aprobación al aprobar el plan:**

1. **"Lo que no debe cambiar" (adenda, punto 5) — pendiente. Recomendado: no duplicar tests; ya existen y se miden.**
   Un superadmin desactiva a un admin → 200 (`test_be35_superadmin_deactivates_lower_rank_account_returns_200`), lo
   borra → 200 (`test_b3_superadmin_deletes_third_party_account[admin]`), un admin edita su perfil → 200
   (`test_b2_admin_self_update_without_role_returns_200`, l.513), un turista se borra → 200
   (`tests/test_auth.py:168`; unitario `:41`) y no envía `is_active` → 403 (`tests/test_auth.py:240`). Los seis pasan
   con la regla dictada (medido). Trade-off: un gemelo be58 de cada uno no mataría ningún mutante más.
2. **Texto del aviso para un superadmin — pendiente. Recomendado: aceptarlo tal cual** (adenda, puntos 2 y 3: una
   guarda por vía y los dos textos sustituyen a los de BE-35). Un superadmin que intente borrarse o desactivarse leerá
   "Solicítelo a un superadministrador", pero ningún par puede darle de baja (ADR-0017; BE-55). Alternativa: elegir el
   texto según el rol dentro de la misma guarda (una rama más y un tercer texto que David tendría que dictar).
3. **Texto de ADR-0019 y de la línea "Estado" de ADR-0017 — pendiente. Recomendado: los de la fase A.**
4. **Alcance de los tests nuevos — pendiente. Recomendado: los 2 unitarios invertidos (renombrados `be58`) y 5 casos
   HTTP; sin gemelo por cédula ni `"false"` en texto para el admin.** La guarda es la misma que la del superadmin; el
   gemelo por cédula de BE-35 ya mata `actor is target` en las dos vías (M2, M7) y la conversión de `"false"` está medida
   en la E0 de BE-35 y congelada por su H3.

## Objetivo y decisiones bloqueadas

Que ninguna cuenta que no sea de turista pueda darse de baja a sí misma por la aplicación: la baja de un admin la decide
un superadmin. Las dos vías medidas (auto-`DELETE` y auto-`PATCH {"is_active": false}`) se cierran con las guardas que ya
existen.

1. La condición de las dos guardas es "el actor no es turista" (`actor.role != UserRole.tourist`), no "es admin o
   superadmin" (adenda, punto 1).
2. Una sola guarda por vía: se amplían las de ADR-0017 (`user_access_policy.py:49-50` y `:106-111`); no se añade otra.
3. La guarda de `is_active` sigue leyendo el valor: `false` → 403, `true` pasa, `null` es BE-37 (M6 vivo, declarado).
4. 403 con `AuthorizationError`; sin excepción nueva ni entrada en `_DOMAIN_ERROR_STATUS`; política pura, síncrona, misma
   firma. El rechazo no muta estado ni escribe auditoría (la política corre antes de `setattr`, `user_service.py:286-290`).
5. Textos de los avisos, letra a letra (David): `"Una cuenta administrativa no puede eliminarse a sí misma. Solicítelo a
   un superadministrador."` y `"Una cuenta administrativa no puede desactivarse a sí misma. Solicítelo a un
   superadministrador."`. Los tests no afirman sobre ellos.
6. ADR-0019 antes del código que lo cita; ADR-0017 solo cambia su línea "Estado"; ADR-0018 no se toca.
7. Los turistas no cambian: borran su cuenta (200) y no envían `is_active` (403).

## Análisis del redactor

**Contraste con el código (`2cc8f73`).** Todo lo que la verificación cita sigue en su sitio: `user_access_policy.py:40`
(`is_self_deletion` por cédula), `:43` (el 403 jerárquico no salta en un auto-borrado), `:49-50` (guarda de auto-borrado
solo para superadmin), `:73` (`is_self_update`), `:100-104` (la clave `is_active` prohibida a turistas), `:106-111`
(guarda de auto-desactivación solo para superadmin, por valor); `user_service.py:206` y `:286` (la política antes de
mutar y de auditar); docstrings `user_access_policy.py:10-16, 29, 36-38, 58-62`, `user_service.py:180-183, 194-195, 205,
256-259` y `routers/user.py:133-135`. Tests que congelan lo contrario: `tests/test_user_access_policy.py:71-74` y
`:255-258` (los únicos, medido por la verificación y repetido aquí: RED de la copia `6 failed, 725 passed`, todos be58).

**Qué se cambia y por qué.** Dos condiciones, una por guarda, y sus textos. Es una regla que depende del dato (el
objetivo es el propio actor), así que va en la política (ADR-0012, punto 2), y lanza la excepción que el handler ya
traduce a 403 (ADR-0003). Código que dicta la fase B (dentro de `user_access_policy.py`):

- `:49-50` pasa a:
  ```python
          if is_self_deletion and actor.role != UserRole.tourist:
              raise AuthorizationError(
                  "Una cuenta administrativa no puede eliminarse a sí misma. "
                  "Solicítelo a un superadministrador."
              )
  ```
- `:108` pasa a `            and actor.role != UserRole.tourist` y `:111` pasa a:
  ```python
              raise AuthorizationError(
                  "Una cuenta administrativa no puede desactivarse a sí misma. "
                  "Solicítelo a un superadministrador."
              )
  ```

**Columnas de los avisos (medidas con el intérprete, UTF-8).** Los textos miden 93 y 95 caracteres; en una línea,
`raise AuthorizationError("…")` mediría 133 y 135 columnas, y el literal solo dentro de paréntesis, 111 y 113: los tres
pasan de 100 (E501). Forma dictada: concatenación implícita de dos literales entre los paréntesis de la llamada, partida
tras `a sí misma. ` (el espacio final queda en el primer literal, así que la cadena resultante es la de David letra a
letra). Líneas: 76 (`"…eliminarse a sí misma. "`), 78 (`"…desactivarse a sí misma. "`) y 53
(`"Solicítelo a un superadministrador."`), con 16 espacios de sangría. `ruff format --check` deja las dos llamadas tal
cual y `ruff check` no da E501 (medido en la copia).

**Mutantes M1 y M5 de BE-35, redefinidos.** En BE-35, M1 (quitar la condición de rol de la guarda de borrado) moría por
`test_be35_admin_self_delete_is_still_allowed` y M5 (quitar la de la guarda de `is_active`) por
`test_be35_admin_self_deactivation_is_still_allowed`; esos dos tests se invierten. Con la regla nueva:
**M1** = quitar `and actor.role != UserRole.tourist` de la guarda de borrado → muere por los dos tests del turista
(`tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login`,
`TestAssertCanDelete::test_self_delete_tourist_is_allowed`). **M5** = quitar esa condición de la guarda de `is_active` →
**sobrevive y es equivalente**: un turista que envía `is_active` cae antes en la guarda de `:100-104`, así que la
condición no cambia ninguna respuesta mientras esa guarda vaya antes. Se conserva por la decisión 1: la guarda dice a quién
alcanza la regla en vez de depender del orden de las guardas. La regresión que de
verdad debe morir es volver a "solo superadmin" (**R1**, **R5**): la matan los tests be58.

**Tabla de mutantes** (copia de `2cc8f73` con la fase B; suite completa por mutante; salida literal en "Mediciones"):

| Id | Vía | Mutación (sobre el código dictado) | Suite | Lo matan |
|---|---|---|---|---|
| R1 | borrado | `actor.role == UserRole.superadmin` (volver a BE-35) | 3 failed | U1, H1, H3 (be58) |
| M1 | borrado | quitar `and actor.role != UserRole.tourist` | 2 failed | `test_self_delete_tourist_is_allowed`, `tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login` |
| SD | borrado | `actor.role != UserRole.superadmin` ("no superadmin") | 7 failed | los dos del turista + 5 be35 de superadmin (U1, U2, H1, H2, H5 de BE-35) |
| AD | borrado | `actor.role == UserRole.admin` ("admin") | 5 failed | 5 be35 de superadmin (U1, U2, H1, H2, H5 de BE-35) |
| ASD | borrado | `actor.role in (UserRole.admin, UserRole.superadmin)` | **731 passed (vive)** | ninguno: equivalente con los tres roles de hoy (decisión 1: un rol nuevo) |
| M2 | borrado | `actor is target` en vez de `is_self_deletion` | 1 failed | `test_be35_self_delete_guard_identifies_the_actor_by_cedula` |
| M8 | borrado | quitar la guarda entera (`if False:`) | 8 failed | U1, H1, H3 (be58) + 5 be35 de superadmin |
| R5 | `is_active` | `and actor.role == UserRole.superadmin` (volver a BE-35) | 4 failed | U2, H2 ×2, H3 (be58) |
| M5 | `is_active` | quitar `and actor.role != UserRole.tourist` | **731 passed (vive)** | ninguno: equivalente, la guarda de `:100-104` corta antes al turista |
| SU | `is_active` | `and actor.role != UserRole.superadmin` ("no superadmin") | 7 failed | 7 be35 de superadmin (U4, U6, H3 ×3, H4, H5 de BE-35); ningún test del turista |
| AU | `is_active` | `and actor.role == UserRole.admin` ("admin") | 7 failed | los mismos 7 be35 que SU |
| ASU | `is_active` | `and actor.role in (UserRole.admin, UserRole.superadmin)` | **731 passed (vive)** | ninguno: equivalente hoy, como ASD |
| M3 | `is_active` | `and "is_active" in update_dict` (clave en vez de valor) | 3 failed | H4 (be58), U5 y H6 de BE-35 |
| M4 | `is_active` | quitar `is_self_update` | 3 failed | `test_admin_can_mutate_is_active`, U8 y H7 de BE-35 |
| M6 | `is_active` | `and not update_dict.get("is_active", True)` (`None` como desactivación) | **731 passed (vive)** | ninguno, a propósito: BE-37 |
| M7 | `is_active` | `actor is target` en vez de `is_self_update` | 1 failed | `test_be35_self_deactivation_guard_identifies_the_actor_by_cedula` |
| M9 | `is_active` | quitar la guarda entera (`False and …`) | 11 failed | U2, H2 ×2, H3 (be58) + 7 be35 de superadmin |

Nombres be35 de la tabla (U/H de BE-35, `docs/deuda/BE-35/plan.md`, fase B): U1 `test_be35_superadmin_self_delete_is_rejected`,
U2 `test_be35_self_delete_guard_identifies_the_actor_by_cedula`, U4 `test_be35_superadmin_self_deactivation_is_rejected`,
U5 `test_be35_superadmin_self_update_with_is_active_true_is_allowed`, U6
`test_be35_self_deactivation_guard_identifies_the_actor_by_cedula`, U8 `test_be35_superadmin_can_deactivate_lower_rank_account`,
H1 `…sole_superadmin_self_delete…`, H2 `…self_delete_returns_403_with_another_superadmin_active`, H3
`…sole_superadmin_self_deactivation…` (×3), H4 `…self_deactivation_returns_403_with_another_superadmin_active`, H5
`…superadmin_keeps_access_after_rejected_self_removal`, H6 `…superadmin_self_update_with_is_active_true_returns_200`, H7
`…superadmin_deactivates_lower_rank_account_returns_200`. Lectura: el mutante "no superadmin" en la vía de `is_active`
(SU) **no** lo detecta ningún test del turista (el turista ya cae en `:100-104`); lo matan los be35 de superadmin. En la
vía de borrado (SD) lo matan las dos familias. "Admin" (AD, AU) lo matan los be35 de superadmin. "Admin o superadmin"
(ASD, ASU) es equivalente hoy: la decisión 1 lo descarta por roles futuros, no porque un test lo distinga.

**Orden y dependencias.** A (ADR, 2 archivos) primero, porque los docstrings y dos tests de B citan ADR-0019. B depende
solo de A. Regla, docstrings y tests en un commit, como en BE-02, BE-35 y BE-36: separar el código de sus docstrings
dejaría un commit en que el código miente.

**Tests que congelan comportamiento relacionado** (todos en verde con la regla dictada; medido): turista se borra
(`tests/test_auth.py:168`, `tests/test_user_access_policy.py:41`), turista y `is_active` (`tests/test_auth.py:240`,
`tests/test_user_access_policy.py:151`), admin edita su perfil (`:513`), superadmin sobre admin (`:727` con `[admin]`,
`:980`), los be35 de superadmin sobre sí mismo (unitarios `:58`, `:64`, `:237`, `:243`, `:248`; HTTP `:839-978`: congelan
que la guarda ampliada sigue alcanzando al superadmin) y `:260` (superadmin sobre admin), los be36 (`:266-319`,
`:1014-1221`). `tests/test_user_service.py` usa la política con
`autospec`: no la ejecuta. Ninguna ruta cambia: `tests/test_route_guards.py` no se toca.

**Riesgos.** (a) Contrato: dos respuestas 200 → 403 para un admin sobre sí mismo; el cliente ya muestra el `detail` de un
403 (fila BE-58). (b) El aviso para un superadmin (decisión pendiente 2). (c) M5, ASD y ASU sobreviven por construcción
(equivalentes, tabla); M6 sobrevive a propósito (BE-37). (d) Las líneas dictadas más largas (96 columnas, docstring de H3;
90, comentario de `user_service.py:205`) están medidas con el intérprete y con `ruff check`; si da E501, el ejecutor se
detiene.

**Qué NO se toca.** `assert_can_recover`, `can_see`, la guarda de jerarquía y `is_peer_reactivation` (ADR-0018), las
guardas de `role` y la de turistas (`:92-104`), la lógica de `user_service.py`, `app/core/`, `app/main.py`,
`app/schemas/`, `app/repositories/`, `app/api/dependencies.py`, `tests/test_auth.py`, `tests/test_user_service.py`,
`tests/test_route_guards.py`, `tests/conftest.py`, `conftest.py`, ADR-0018, `AGENTS.md`.

## Regla de alcance

**Sí:** ADR-0019; la línea "Estado" de ADR-0017; la condición de rol y el texto de las dos guardas de ADR-0017; los
docstrings y el comentario de paso que describen el auto-borrado en `user_access_policy.py`, `user_service.py` y
`routers/user.py`; el docstring de `TestAssertCanDelete`, los dos tests invertidos y la sección HTTP be58 en
`tests/test_user_access_policy.py`.
**No:** guarda nueva o excepción nueva; `{"is_active": null}` (BE-37); auditoría de no-ops (BE-38); baja de superadmins
(BE-55); mensaje del login inactivo (BE-56); edición en la papelera (BE-57); el token que muere al cambiar el propio
correo (rincón 5: nota en FE-01, ya presente en `2cc8f73`); `AGENTS.md`, `docs/CONTEXT.md`, `docs/backlog.md` (los
actualizan David y la sesión Mentor al cierre).

## Fases

| Fase | Qué | Archivos | Suite tras la fase | Commit |
|---|---|---|---|---|
| A | ADR-0019 y línea "Estado" de ADR-0017 | 2 (`docs/adr/`) | 726 passed · 97,65 % (sin cambios en código) | — |
| B | Dos guardas ampliadas, textos, docstrings, 2 tests invertidos y 5 casos HTTP | 4 | 731 passed · 97,65 % (medido en copia) | — |

### Fase A — ADR-0019 y la supersesión parcial de ADR-0017 (la más pequeña)

- **Archivos (2):** `docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md` (nuevo) y
  `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md` (solo la línea "Estado"). Dominio: decisiones (docs).
- **Cambios exactos:**
  - Crear ADR-0019 con este texto (71 líneas; la más larga, 120 columnas; `<FECHA>` = la de la línea de aprobación).
    Los cuatro espacios que abren cada línea de los dos bloques de esta fase son la sangría de la lista del plan, no
    parte del archivo:

    ```markdown
    # ADR-0019 — Ninguna cuenta administrativa se borra ni se desactiva a sí misma: su baja la decide un superadmin

    - **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-58)
    - **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 18:02)
    - **Ubicación en el repo:** `docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md`
    - **Supersede parcialmente:** ADR-0017, en dos puntos: el alcance "superadmin" de las dos guardas de su decisión 1 y
      su consecuencia "Turistas y admins no cambian". El resto de ADR-0017 sigue vigente (el número de superadmins no baja
      desde la aplicación; la baja de un superadmin es SQL directo hasta BE-55; las alternativas descartadas). ADR-0018 no
      cambia.
    - **Origen:** backlog BE-58; `docs/deuda/BE-58/verificacion.md` (veredicto y adenda); `docs/deuda/BE-58/plan.md`.
      Relación: ADR-0009 (un addendum no puede ampliar el alcance de una decisión: esto es un ADR nuevo), ADR-0006 respecto
      de ADR-0003 (precedente de supersesión parcial), ADR-0012 (una regla que depende del dato va en la política),
      ADR-0003 (`AuthorizationError` → 403).

    ## Contexto

    ADR-0017 cerró dos vías de autoservicio solo para superadmins, `DELETE /usuarios/{su cédula}` y
    `PATCH /usuarios/{su cédula}` con `{"is_active": false}`, y dejó escrito "Turistas y admins no cambian". Un admin seguía
    pudiendo usarlas: medido el 16 nov con la pila real de la suite, las dos dan 200, escriben una fila de auditoría con el
    propio admin como autor y la petición siguiente recibe 401. David lo vio también en el cliente: un admin se desactiva
    desde su tarjeta del kanban y su sesión queda muerta. La cuenta no se pierde: un superadmin la reactiva o la recupera
    desde la aplicación (200 · 200 · 200); otro admin no puede (403).

    ## Decisión

    1. **Ninguna cuenta administrativa borra ni desactiva su propia cuenta.** Cuenta administrativa es la de todo rol que no
       sea turista. Las dos guardas de ADR-0017 (`UserAccessPolicy.assert_can_delete` y `assert_can_update`) pasan de "el
       actor es superadmin" a "el actor no es turista". Una sola guarda por vía: no se añade otra. "Su cuenta" sigue siendo
       la de su misma cédula.
    2. **La condición se escribe sobre "no es turista", no sobre "es admin o superadmin".** Hoy dicen lo mismo; un rol que
       se añada mañana queda bloqueado hasta que alguien decida abrirlo.
    3. **Los turistas no cambian:** conservan el borrado de su propia cuenta y siguen sin poder enviar `is_active`.
    4. **Lo demás de ADR-0017 se mantiene:** la guarda de `is_active` lee el valor (`false` → 403, `true` pasa, `null`
       es BE-37); 403 con `AuthorizationError`, sin excepción nueva; el rechazo no muta estado ni escribe auditoría; la
       política sigue pura, síncrona y con la misma firma.

    La razón es de gobierno: **solo un superadmin decide cuándo se da de baja una cuenta administrativa** (David, 16 nov).
    Un funcionario no debe poder interrumpir la operación retirando la cuenta que el gerente tenía prevista para su
    reemplazo. No la sostiene que la cuenta "quede varada hasta que alguien entre a la base": la verificación midió que un
    superadmin rescata a un admin desde la aplicación.

    ## Consecuencias

    - Cambio de contrato solo para un admin sobre sí mismo: `DELETE /usuarios/{cédula}` y `PATCH /usuarios/{cédula}` con
      `is_active` a `false` pasan de 200 a 403, y un `PATCH` que mezcla `is_active: false` con otros campos se rechaza
      entero. `{"is_active": true}` sobre uno mismo sigue dando 200. Turistas y superadmins no cambian de código.
    - La baja de un admin la da un superadmin desde la aplicación (borrar o desactivar a un rango inferior, sin cambio). La
      de un superadmin sigue como la deja ADR-0017: SQL directo hasta BE-55.
    - Los dos avisos dejan de nombrar al superadministrador como sujeto y piden la baja a un superadministrador. Un
      superadmin recibe el mismo texto, aunque ningún par puede darle de baja desde la aplicación (ADR-0017; BE-55).
    - La viñeta "Superadmins" de AGENTS §3 recoge la ampliación; la edita David.
    - Cambiar el propio correo también deja muerto el token en uso (el token lleva el correo), pero no es una baja: queda
      fuera de esta regla (FE-01).

    ## Alternativas consideradas

    1. **Una guarda nueva solo para admins, junto a las de ADR-0017.** Descartada: dos guardas por vía con el mismo efecto,
       y un rol nuevo obligaría a acordarse de una tercera.
    2. **Escribir la condición sobre "admin o superadmin".** Descartada: equivale hoy, pero un rol nuevo quedaría abierto
       por omisión.
    3. **Un addendum a ADR-0017.** Descartado: amplía el alcance de su decisión e invierte una consecuencia escrita, que
       ADR-0009 (punto 3) reserva a un ADR nuevo.
    4. **No hacer nada, porque un superadmin rescata la cuenta.** Rechazada: la cuestión no es si la cuenta se recupera,
       sino quién decide su baja.

    ## Evidencia

    - Verificación (16 nov, pila real de la suite): admin, `PATCH` propio `{"is_active": false}` → 200, el mismo token →
      401, login → 403; `DELETE` propio → 200, el mismo token → 401, login → 401. Otro admin no lo rescata (403); un
      superadmin sí (200 · 200 · 200). Con la regla inyectada: 403 sin mutación ni auditoría, y el token sigue sirviendo.
    - Tests y mutantes de la regla: `docs/deuda/BE-58/plan.md`, fase B.
    ```

  - En ADR-0017, la l.3 (`- **Estado:** aceptado (David, 16 nov 2026, al aprobar el plan de BE-35)`) pasa a estas tres
    líneas (112, 116 y 35 columnas con `<FECHA>` = `16 nov 2026`); nada más cambia en ese archivo:

    ```markdown
    - **Estado:** aceptado (David, 16 nov 2026, al aprobar el plan de BE-35). **Superado parcialmente por ADR-0019**
      (<FECHA>): el alcance "superadmin" de las dos guardas de la decisión 1 y la consecuencia "Turistas y admins no
      cambian"; el resto sigue vigente.
    ```

- **Tests (RED primero):** no aplica (solo documentación). Comprobación sustituta: `./venv/Scripts/python.exe
  scripts/check.py --no-tests` en verde (`check_docs` no escanea `docs/adr`, `scripts/check_docs.py:157`).
- **Criterio de aceptación:** el ADR-0019 existe con el texto dictado y `<FECHA>` sustituida en él y en ADR-0017;
  `git diff --numstat 2cc8f73 HEAD -- docs/adr` = `71 0` para el 0019 y `3 1` para el 0017, y nada más;
  `git grep -l 'ADR-0019' -- docs/adr` = esos dos archivos; `git diff --stat 2cc8f73 HEAD --
  docs/adr/0018-un-superadmin-reactiva-a-otro.md` vacío; compuerta completa en verde con 726 passed.
- **Fuera de alcance de esta fase:** `app/`, `tests/`; ADR-0018; cualquier otra línea de ADR-0017; `AGENTS.md`,
  `docs/CONTEXT.md`, `docs/backlog.md`.
- **Commit:**
  ```
  docs(adr): add ADR-0019, no administrative account removes itself

  ADR-0017 closed self-deletion and self-deactivation for superadmins
  only and wrote that admins do not change. An admin could still
  DELETE their own account or PATCH their own is_active to false and
  get 200, with an audit row signed by themselves and a dead session
  (BE-58, measured). A superadmin can rescue that account from the
  application, so the account is not lost; the question is who
  decides when an administrative account leaves.

  The ADR records David's answer before the code that cites it lands:
  only a superadmin does. The two ADR-0017 guards widen from "the
  actor is a superadmin" to "the actor is not a tourist", so a role
  added later stays blocked until someone opens it, and tourists keep
  deleting their own account. ADR-0017 is superseded only in that
  scope and in its "tourists and admins do not change" consequence;
  its status line says so, the only edit an accepted ADR admits. An
  addendum could not do this: it would widen the decision (ADR-0009).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Las dos guardas ampliadas, sus textos, sus docstrings y sus tests

- **Archivos (4):** `app/services/user_access_policy.py`, `app/services/user_service.py` (solo docstrings y un
  comentario), `app/api/routers/user.py` (solo un docstring), `tests/test_user_access_policy.py`. Dominio: autorización
  sobre cuentas de usuario. `git diff --numstat` esperado: 22/14, 6/5, 2/2 y 110/5 (medido en la copia).
- **Cambios exactos en `app/`** (las guardas, en "Análisis del redactor"; los textos, aquí; anclas de `2cc8f73`):
  - `user_access_policy.py`, docstring de la clase, `:13-16` pasan a (el resto, `:10-12` y `:17-19`, no cambia):
    ```
        account: nobody changes their own role, and no actor other than a tourist
        deletes or deactivates it (ADR-0017, ADR-0019), so the number of superadmins
        never drops and only a superadmin retires an admin account. One exception
        between peers: a superadmin may reactivate another superadmin outside the
        recycle bin, sending is_active true and nothing else (ADR-0018).
    ```
  - `assert_can_delete`, docstring: `:29` pasa a
    `        No actor other than a tourist deletes their own account (ADR-0017, ADR-0019).` (85 columnas), y `:37-38` a:
    ```
                account nor outranks the target, or when an actor other than
                a tourist deletes their own account.
    ```
  - `assert_can_update`, docstring: `:60-62` pasan a:
    ```
            on their own account by any other actor (ADR-0017, ADR-0019). The role
            guards read the key, not its value: resending the current role is
            rejected too. The last guard reads the value: is_active true on one's own
            account passes.
    ```
  - `user_service.py`, `delete_user_account`: `:182-183` pasan a:
    ```
            role rank is strictly greater than the target's role rank. No actor
            other than a tourist deletes their own account (ADR-0017, ADR-0019).
    ```
    `:195` pasa a `                or an actor other than a tourist deletes their own account.`; el comentario `:205`
    pasa a `        # 2. ABAC Hierarchical Invariant: higher rank OR a tourist's own account; ADR-0019` (90 columnas).
  - `user_service.py`, `update_user_account`: `:259` pasa a dos líneas:
    ```
            is_active set to false on their own account by any other actor
            (ADR-0017, ADR-0019).
    ```
  - `routers/user.py`, docstring de `eliminar_usuario`: `:134-135` pasan a (75 y 70 columnas):
    ```
        when the actor's role strictly outranks the target's, or on a tourist's
        own account; no other account deletes itself (ADR-0017, ADR-0019).
    ```
- **Tests (RED primero)** — en `tests/test_user_access_policy.py`, escritos y ejecutados **antes** de tocar `app/`.
  Texto literal en el Anexo. Fixtures de `tests/conftest.py` (`make_user`, `persist_user`, `make_auth_headers`);
  `persist_user` confirma antes de la petición y `refresh` relee después (ADR-0011); se afirma sobre código, forma del
  cuerpo, estado y auditoría, nunca sobre el texto en español.
  - `:39`, docstring de `TestAssertCanDelete` →
    `    """Freezes the deletion invariant: higher rank, or own account only for a tourist."""` (89 columnas; el de BE-35,
    "never a superadmin's own", deja de describir la regla).
  - U1 **sustituye** a `test_be35_admin_self_delete_is_still_allowed` (`:71-74`):
    `test_be58_admin_self_delete_is_rejected` — `assert_can_delete(admin, admin)` lanza.
  - U2 **sustituye** a `test_be35_admin_self_deactivation_is_still_allowed` (`:255-258`):
    `test_be58_admin_self_deactivation_is_rejected` — `assert_can_update(admin, admin, {"is_active": False})` lanza.
  - HTTP, sección nueva al final del bloque B (tras la l.1221, última de
    `test_be36_superadmin_reactivating_active_peer_returns_200`; antes de `# ==========================================`
    de la sección C, l.1224), cabecera
    `# --- BE-58 regression: an administrative account never deletes or deactivates itself ---`:
    H1 `test_be58_admin_self_delete_returns_403_without_mutation` — `DELETE` propio → 403, `{"detail"}` y `str`;
    `deleted_at is None`, `is_active is True`; auditoría `[]`.
    H2 `test_be58_admin_self_deactivation_returns_403_without_mutation`, ×2 (`false`, `with-profile-field`: el `PATCH`
    mixto del rincón 3) — 403, `{"detail"}` y `str`; `is_active is True`, `first_name == "John"`, `deleted_at is None`;
    auditoría `[]`.
    H3 `test_be58_admin_keeps_access_after_rejected_self_removal` — mismo token: `DELETE` → 403, `PATCH
    {"is_active": false}` → 403, `GET /usuarios/mi-perfil` → 200 con `cedula`, `role == "admin"`, `is_active is True`.
    H4 `test_be58_admin_self_update_with_is_active_true_returns_200` — 200, `cedula`, `is_active is True`; tras
    `refresh`, activo. **Sin** aserción sobre la auditoría (registra la clave aunque no cambie: BE-38).
  - **RED esperado** (medido contra `2cc8f73`):
    `./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be58 -q` → `6 failed, 1 passed`. Fallan U1,
    U2, H1, H2 (×2) y H3. Pasa ya H4: es el borde que impide que la guarda lea la clave en vez del valor (mata M3, junto a dos be35).
- **Criterio de aceptación:** `-k be58` → `7 passed`; `-k be35` → `15 passed` (17 − 2 renombrados); `-k be36` →
  `19 passed`; compuerta `./venv/Scripts/python.exe scripts/check.py` con salida 0, ruff 0, mypy 0 en 63, 4 kept,
  `731 passed` (726 + 5) y cobertura ≥ 97,65 % (`user_access_policy.py` al 100 %); comandos 1–14 de la Verificación
  final como se esperan; mutantes de la tabla con el resultado declarado (muertos y vivos), anotados en el handoff.
- **Fuera de alcance de esta fase:** lógica de `user_service.py`; `assert_can_recover`, `can_see`,
  `is_peer_reactivation` y las guardas `:83-104`; `exceptions.py`, `main.py`, schemas, `dependencies.py`;
  `tests/test_auth.py`, `tests/test_user_service.py`, `tests/test_route_guards.py`, `tests/conftest.py`; el docstring de
  `TestAssertCanUpdate` (`:106`, "ADR-0017 guard": sigue nombrando la guarda que se amplía); la cabecera y los tests be35
  de superadmin; `{"is_active": null}` (BE-37); auditoría de no-ops (BE-38); ADRs; `AGENTS.md`.
- **Commit:**
  ```
  fix(access-policy): block admin self-deletion and self-deactivation

  An admin could delete their own account or PATCH their own is_active
  to false and get 200, with an audit row signed by themselves and a
  dead session from the next request on (BE-58, measured). Only a
  superadmin decides when an administrative account leaves
  (ADR-0019).

  - app/services/user_access_policy.py: the two ADR-0017 guards now
    fire for any actor that is not a tourist instead of only for a
    superadmin, so a role added later is blocked by default. One
    guard per path; the is_active guard still reads the value, so
    true passes and null stays BE-37. Same AuthorizationError (403),
    no new exception, same pure signature. The two messages are
    David's neutral texts and replace the BE-35 ones.
  - app/services/user_service.py, app/api/routers/user.py: docstrings
    and one step comment stop saying that any actor may delete their
    own account and cite ADR-0019. No logic change.
  - tests/test_user_access_policy.py: the two BE-35 unit tests that
    froze admin self-deletion and self-deactivation as allowed now
    expect the rejection. New HTTP cases cover an admin deleting or
    deactivating itself, alone and mixed with a profile field, with
    no mutation and no audit row; the same token still working after
    the rejection; and is_active true on oneself still returning 200.

  Tourists keep deleting their own account and a superadmin still
  deactivates and deletes an admin: tests that already freeze both
  stay green.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase B. Los conteos incluyen el texto que dicta este plan (código, docstrings,
comentarios, nombres y docstrings de tests, ADR) y están medidos con `grep` sobre una copia de `2cc8f73` con las fases A
y B aplicadas. Patrones 1–6 = los de la verificación, recalculados.

```bash
# 1. Las dos guardas, escritas sobre "no turista" → 2 líneas, app/services/user_access_policy.py:50 y :113
git grep -n -F 'actor.role != UserRole.tourist' -- app

# 2. Patrón 1 → 4 líneas en app/services/user_access_policy.py: :50 (guarda de borrado), :89 y :112 (is_self_update),
#    :114 (la guarda lee el valor)
git grep -n "is_self_deletion and actor.role\|is_self_update$\|update_dict.get(\"is_active\") is False" -- app/services/user_access_policy.py

# 3. Las guardas ya no nombran al superadmin → app/services/user_access_policy.py:6 (base: 8; quedan _ROLE_RANK,
#    is_peer_reactivation ×2, la guarda de role, assert_can_recover y can_see)
git grep -c -F 'UserRole.superadmin' -- app/services/user_access_policy.py

# 4. Patrón 2: los tests que congelaban lo contrario → 0 líneas (exit 1)
git grep -n "test_be35_admin_self_delete_is_still_allowed\|test_be35_admin_self_deactivation_is_still_allowed" -- tests

# 5. Patrón 3: el borrado propio del turista sigue protegido → 2 líneas (tests/test_auth.py:168,
#    tests/test_user_access_policy.py:41)
git grep -n "test_self_soft_delete_keeps_row_and_blocks_login\|test_self_delete_tourist_is_allowed" -- tests

# 6. Patrón 4: "own account" en app/ → 13 líneas (base: 15): routers/user.py 1, user_access_policy.py 6,
#    user_service.py 6
git grep -n "own account" -- app

# 7. Patrón 5: casos HTTP de admin que se borra o se desactiva → 2 líneas (H1 y H2 de tests/test_user_access_policy.py)
git grep -n "async def test_.*_admin_self_\(delet\|deactiv\)" -- tests

# 8. Patrón 6: ADR-0017 en código, tests y reglas → 10 líneas (base: 11): app 6, tests 2, AGENTS.md 2 (sin cambio)
git grep -n "ADR-0017" -- app tests AGENTS.md

# 9. Citas de ADR-0019 → app: 7 líneas (user_access_policy.py 3, user_service.py 3, routers/user.py 1); tests: 2
#    (docstrings de H1 y H2); docs/adr: los archivos 0017 y 0019
git grep -n "ADR-0019" -- app
git grep -n "ADR-0019" -- tests
git grep -l "ADR-0019" -- docs/adr

# 10. Avisos → 2 líneas en app/services/user_access_policy.py (:52 y :117); los de BE-35, 0 líneas (exit 1)
git grep -n -F "Una cuenta administrativa no puede" -- app
git grep -n -F "Un superadministrador no puede" -- app

# 11. Nada fuera del alcance → salida vacía
git diff --stat 2cc8f73 HEAD -- app/core app/main.py app/repositories app/schemas app/models app/cli app/api/dependencies.py tests/test_auth.py tests/test_user_service.py tests/test_route_guards.py tests/conftest.py conftest.py AGENTS.md docs/adr/0018-un-superadmin-reactiva-a-otro.md

# 12. ADR-0017: solo su línea "Estado" → "3	1	docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md"
git diff --numstat 2cc8f73 HEAD -- docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md

# 13. Tests del ítem → 6 funciones be58, 13 be35 (base: 15); 7, 15 y 19 casos en verde
git grep -c "def test_be58_" -- tests/test_user_access_policy.py      # → tests/test_user_access_policy.py:6
git grep -c "def test_be35_" -- tests/test_user_access_policy.py      # → tests/test_user_access_policy.py:13
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be58 -q   # → 7 passed
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be35 -q   # → 15 passed
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be36 -q   # → 19 passed

# 14. Compuerta completa → salida 0; 731 passed; cobertura ≥ 97,65 %; ruff 0; mypy 0 en 63; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

- **R1 — Aviso sin salida para un superadmin.** Con una guarda por vía, el superadmin que intenta borrarse o
  desactivarse recibe "Solicítelo a un superadministrador", y ningún par puede hacerlo desde la aplicación (ADR-0017).
  Evidencia: `user_access_policy.py` dictado (un texto por guarda) y `:83-90` (403 entre pares). Destino: decisión
  pendiente 2; si David lo acepta, nota en la fila BE-55 ("el aviso de BE-58 remite a un superadministrador").
- **R2 — Reglas y estado que se actualizan al cierre.** La viñeta "Superadmins (ADR-0017, ADR-0018)" de AGENTS §3
  (`AGENTS.md:59-62`) solo nombra superadmins; la amplía David después de la auditoría de la fase B y antes de `/pr`
  (adenda, punto 6): el comando 11 exige `AGENTS.md` sin cambio desde `2cc8f73`, así que un commit anterior lo pondría
  en rojo sin que el ítem haya hecho nada mal. La entrada de ADR-0019 en `docs/CONTEXT.md`, la sesión Mentor. Fila
  sugerida: ninguna (ritual de cierre).
- **R3 — Rincón 5 (el token muere al cambiar el propio correo).** La nota que pide la adenda (punto 6) **ya está** en la
  fila FE-01 de `docs/backlog.md` en `2cc8f73` ("Otro caso, medido por la verificación de BE-58 (16 nov, sonda P5)");
  este plan no la escribe ni crea fila.
- **R4 — M6 sigue vivo (`None` tratado como desactivación).** Como en BE-35: BE-37. Sin fila nueva (la nota de BE-37 ya
  lo cubre desde BE-35).

## Referencias

- Ninguna API de librería nueva: la regla usa una comparación de enum y la excepción del dominio; la partición del
  aviso usa la concatenación implícita de literales adyacentes de Python (referencia del lenguaje,
  https://docs.python.org/3.14/reference/lexical_analysis.html#string-literal-concatenation), comprobada en la copia
  (`ruff format --check` y la suite en verde). Los tests usan fixtures existentes y `pytest.mark.parametrize`, ya usados
  en el mismo archivo. Context7 falló al conectar en esta sesión y no hizo falta. La conversión de `"false"` a `False`
  por pydantic 2.12.5 está medida en la E0 de BE-35 (`docs/deuda/BE-35/plan.md`, "Enmiendas aprobadas", punto 3).

## Mediciones (literales; scratchpad de la sesión, nunca en el repo)

**(1) RED con el comando de la casa, desde la raíz del repo** (los 7 casos be58 en un archivo del scratchpad, contra el
código de `2cc8f73`):
`./venv/Scripts/python.exe -m pytest -c pyproject.toml --rootdir . -p conftest -p tests.conftest -p no:cacheprovider --no-cov -q -rA <scratchpad>/probe/test_be58_probe.py`

```
PASSED ::test_be58_admin_self_update_with_is_active_true_returns_200
FAILED ::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected - Faile...
FAILED ::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
FAILED ::test_be58_admin_self_delete_returns_403_without_mutation - assert 20...
FAILED ::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
FAILED ::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
FAILED ::test_be58_admin_keeps_access_after_rejected_self_removal - assert 20...
6 failed, 1 passed in 1.27s
```

**(2) RED en una copia `git archive` de `2cc8f73` con solo `tests/test_user_access_policy.py` como dicta la fase B:**
`-k be58` → `6 failed, 1 passed, 100 deselected in 0.81s` (los mismos seis); suite completa →
`6 failed, 725 passed, 8 warnings in 33.59s`, y los seis fallos son exactamente los be58 de arriba. Nada más cae.

**(3) GREEN: copia de `2cc8f73` con todo lo que dicta la fase B**, `scripts/check.py` completo, exit 0:

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1039     15    152     13  97.65%
30 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 97.65%
731 passed, 8 warnings in 32.71s
Compuerta superada.
```

`user_access_policy.py` no aparece en la tabla de cobertura: está entre los 30 al 100 %. En otra copia con las fases A y
B (ADR-0019 y la línea "Estado" de ADR-0017 incluidos): `scripts/check.py --no-tests` → `Compuerta superada.`; suite
completa → `731 passed, 8 warnings in 30.06s`; `-k be58` → `7 passed, 100 deselected`; `-k be35` → `15 passed,
92 deselected`; `-k be36` → `19 passed, 88 deselected`. Los seis tests de "lo que no cambia" (decisión pendiente 1),
uno a uno: `6 passed`.

**(4) Mutantes**, suite completa sobre la copia GREEN, uno por ejecución, restaurando después (salida literal del
script; ids de la tabla del Análisis):

```
== R1: 3 failed, 728 passed, 8 warnings in 31.77s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== M1: 2 failed, 729 passed, 8 warnings in 31.73s
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_self_delete_tourist_is_allowed
== SD: 7 failed, 724 passed, 8 warnings in 32.04s
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_self_delete_tourist_is_allowed
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== AD: 5 failed, 726 passed, 8 warnings in 30.95s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== ASD: 731 passed, 8 warnings in 32.11s
== M2: 1 failed, 730 passed, 8 warnings in 31.44s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
== M8: 8 failed, 723 passed, 8 warnings in 31.47s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== R5: 4 failed, 727 passed, 8 warnings in 32.00s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== M5: 731 passed, 8 warnings in 32.26s
== SU: 7 failed, 724 passed, 8 warnings in 31.97s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== AU: 7 failed, 724 passed, 8 warnings in 31.43s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== ASU: 731 passed, 8 warnings in 31.06s
== M3: 3 failed, 728 passed, 8 warnings in 32.02s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_update_with_is_active_true_is_allowed
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_update_with_is_active_true_returns_200
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_update_with_is_active_true_returns_200
== M4: 3 failed, 728 passed, 8 warnings in 31.42s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_admin_can_mutate_is_active
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_can_deactivate_lower_rank_account
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
== M6: 731 passed, 8 warnings in 30.01s
== M7: 1 failed, 730 passed, 8 warnings in 33.15s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
== M9: 11 failed, 720 passed, 8 warnings in 30.76s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
```

**(5) Columnas** (intérprete, lectura UTF-8). Avisos: 93 y 95 caracteres; en una línea, 133 y 135 columnas con el
`raise`, 111 y 113 como literal suelto con 16 espacios: no caben. Forma dictada: 76 + 53 y 78 + 53. Líneas añadidas más
largas por archivo: `user_access_policy.py` 85, `user_service.py` 90, `routers/user.py` 75, tests 96. ADR-0019: 120;
"Estado" de ADR-0017: 112, 116 (con la fecha) y 35. Mensajes de commit: ≤ 70 columnas.

## Anexo — texto literal de los tests de la fase B

Docstring de `TestAssertCanDelete` (l.39):

```python
    """Freezes the deletion invariant: higher rank, or own account only for a tourist."""
```

U1, sustituye a `:71-74` (dentro de `TestAssertCanDelete`):

```python
    def test_be58_admin_self_delete_is_rejected(self, policy, make_user):
        admin = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(admin, admin)
```

U2, sustituye a `:255-258` (dentro de `TestAssertCanUpdate`):

```python
    def test_be58_admin_self_deactivation_is_rejected(self, policy, make_user):
        admin = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(admin, admin, {"is_active": False})
```

HTTP, tras la l.1221 (dos líneas en blanco antes de la cabecera y dos después del último test, antes de
`# ==========================================` de la sección C):

```python
# --- BE-58 regression: an administrative account never deletes or deactivates itself ---


async def test_be58_admin_self_delete_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin DELETEing their own account gets 403; nothing is written (ADR-0019)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.delete(
        f"/usuarios/{admin.cedula}",
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(admin)
    assert admin.deleted_at is None
    assert admin.is_active is True
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


@pytest.mark.parametrize(
    "payload",
    [{"is_active": False}, {"is_active": False, "first_name": "Changed"}],
    ids=["false", "with-profile-field"],
)
async def test_be58_admin_self_deactivation_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers, payload
):
    """An admin PATCHing their own is_active to false gets 403; no field changes (ADR-0019)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json=payload,
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(admin)
    assert admin.is_active is True
    assert admin.first_name == "John"
    assert admin.deleted_at is None
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be58_admin_keeps_access_after_rejected_self_removal(
    client, db_session, persist_user, make_auth_headers
):
    """After both self-removals are rejected, the admin's same token still reads its profile."""
    admin = await persist_user(role=UserRole.admin)
    headers = make_auth_headers(admin)

    deleted = await client.delete(f"/usuarios/{admin.cedula}", headers=headers)
    deactivated = await client.patch(
        f"/usuarios/{admin.cedula}", json={"is_active": False}, headers=headers
    )
    profile = await client.get("/usuarios/mi-perfil", headers=headers)

    assert deleted.status_code == 403
    assert deactivated.status_code == 403
    assert profile.status_code == 200
    body = profile.json()
    assert body["cedula"] == admin.cedula
    assert body["role"] == "admin"
    assert body["is_active"] is True

    await db_session.refresh(admin)
    assert admin.deleted_at is None
    assert admin.is_active is True


async def test_be58_admin_self_update_with_is_active_true_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """The guard reads the value: is_active true on an admin's own account still succeeds."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == admin.cedula
    assert body["is_active"] is True

    await db_session.refresh(admin)
    assert admin.is_active is True
```

Líneas más largas que dicta el Anexo, medidas con el intérprete: 96 columnas (docstring de H3), 95 (docstring de H2), 93
(docstring de H4) y 89 (cabecera de la sección y docstring de `TestAssertCanDelete`). Ninguna pasa de 100. Sin imports
nuevos: `pytest`, `select`, `AuthorizationError`, `AuditLog` y `UserRole` ya están importados (l.13, 14, 18, 21, 22).

## Enmiendas aprobadas

### E0 — 16 nov 2026, 18:50 (David: "apruebo con a"; revisión de la sesión Mentor)

1. **Plan aprobado, dos fases, y ADR-0019 aceptado** con el texto de la fase A, incluida la línea "Estado" de ADR-0017.
2. **Decisión pendiente 2, el aviso que recibe un superadmin: opción (a), se acepta tal cual.** Hay dos avisos, uno por
   vía (eliminar y desactivar), y cada uno es el mismo para admin y superadmin: `"Una cuenta administrativa no puede
   eliminarse a sí misma. Solicítelo a un superadministrador."` y su par con "desactivarse". Para un superadmin la
   segunda frase no tiene salida desde la aplicación (ADR-0017; BE-55): se acepta, lo declara ADR-0019 y queda nota en
   la fila BE-55. **Error de la sesión Mentor, declarado:** el texto lo propuso ella a las 17:52 sin ver ese caso; lo
   vio el planificador. Opciones descartadas hoy: (b) quitar la segunda frase; (c) un texto por rol dentro de la misma
   guarda (una rama que ningún test puede vigilar, porque no se afirma sobre texto en español).
3. **Decisiones pendientes 1, 3 y 4, aprobadas como se recomiendan:** no se duplican los tests de "lo que no debe
   cambiar" (existen seis y pasan con la regla, medido); texto del ADR y de la línea "Estado"; dos unitarios invertidos
   y cinco casos HTTP, sin gemelo por cédula ni `"false"` en texto para el admin.
4. **Sin correcciones de dictado.** Contraste de la sesión Mentor contra `2cc8f73`: anclas
   `user_access_policy.py:13-16, :29, :49-50, :106-111` y `tests/test_user_access_policy.py:39, :71-74, :255-258,
   :1221, :1224`; la condición `actor.role != UserRole.tourist` en las dos vías; cuentas (726 + 5 = 731; `-k be35` de
   17 a 15). Las cifras de la copia, las columnas y los 17 mutantes los midió el planificador; el ejecutor los repite y
   el auditor también.
5. **Orden para David:** la viñeta de AGENTS §3 se commitea después de la auditoría de la fase B y antes de `/pr`.

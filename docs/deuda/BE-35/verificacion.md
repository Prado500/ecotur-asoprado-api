# Verificación — BE-35: el último superadmin puede dejar la plataforma sin superadmin

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-35, l.85) + rincón 2 de `docs/deuda/BE-02/verificacion.md` (l.83-88)
**Fecha:** 2026-11-16

## Qué describe el ítem
Dos vías por las que el único superadmin activo se saca a sí mismo y la plataforma queda sin superadmin:
`PATCH /usuarios/{su cédula}` con `{"is_active": false}` (200 y 401 en la siguiente petición) y
`DELETE /usuarios/{su cédula}` (200 y 401 después). La política de acceso no cuenta superadmins activos antes de
desactivar o borrar, y un test unitario congela el auto-borrado del superadmin como comportamiento deseado. Regla
propuesta: "siempre queda al menos un superadmin activo", 409 si es el último.

## Evidencia en el código
Los números de línea de la fila (l.65, l.31-34) son de la medición del 5 nov; hoy son otros. Los de abajo son los
actuales (`87b9905`).

- `app/services/user_access_policy.py:34-37` — `assert_can_delete` admite el auto-borrado de cualquier rol, superadmin
  incluido; no hay conteo:
  `is_self_deletion = actor.cedula == target.cedula` … `if not is_self_deletion and not actor_outranks_target: raise`
- `app/services/user_access_policy.py:75` — la única guarda sobre `is_active` excluye a turistas, nada más:
  `if "is_active" in update_dict and actor.role == UserRole.tourist:`
- `app/services/user_access_policy.py:60-62` — la auto-edición (`is_self_update`) salta la regla de jerarquía, así que
  un superadmin puede tocar su propio `is_active`.
- `app/services/user_access_policy.py:10-13` y `:24` — los docstrings de la clase y de `assert_can_delete` describen la
  paridad de auto-borrado como regla ("an actor may act on their own account").
- `app/services/user_service.py:205` y `:208` — `delete_user_account` llama a la política y luego a
  `soft_delete_user` sin ninguna comprobación de "último superadmin". Docstring `:180-183` y comentario `:204`
  ("self-deletion parity OR strictly higher rank").
- `app/services/user_service.py:281` y `:284-285` — `update_user_account` llama a la política y aplica
  `setattr(target_user, key, value)`, incluido `is_active=False` sobre sí mismo. Docstring `:254-257`.
- `app/repositories/user_repository.py:83-84` — `soft_delete_user` pone `deleted_at` y `is_active = False`.
- `app/api/dependencies.py:142-145` — `get_current_user` rechaza (401) a quien está borrado o inactivo; por eso la
  petición siguiente da 401 y no hay vuelta atrás desde la aplicación.
- `app/api/routers/user.py:126` (`DELETE /{cedula}`) y `:146` (`PATCH /{cedula}`) — ambas en `self_service_router`
  (guard `user`); docstring `:133-134` del DELETE habla de "self-deletion".
- `app/repositories/user_repository.py:23-41` — `count_active_superadmins` existe (BE-34, R6): cuenta
  `role == superadmin`, `is_active` y `deleted_at IS NULL`. Hoy solo lo usa `app/services/superadmin_bootstrap.py:42`.
- `tests/test_user_access_policy.py:57-60` — `test_superadmin_self_delete_is_allowed` congela
  `policy.assert_can_delete(superadmin, superadmin)` sin excepción.
- `app/main.py:121-132` — `_DOMAIN_ERROR_STATUS` no tiene ninguna excepción que mapee a 409;
  `app/core/exceptions.py` no define una de conflicto (`BusinessRuleViolationError`, l.150, mapea a 400). El único 409
  de la app es el handler de `IntegrityError` (`app/main.py:100-107`), que no es de dominio.

**Medición (sonda HTTP en el scratchpad, sin tocar el repo; pila real, `client` + `persist_user` de la suite):**

| Sonda | Resultado |
|---|---|
| Único superadmin, `PATCH` propio `{"is_active": false}` → `GET /usuarios/mi-perfil` con el mismo token | `200` → `401`; `is_active=False`; `count_active_superadmins()=0` |
| Único superadmin, `DELETE` propio → `GET /usuarios/mi-perfil` | `200` → `401`; `is_active=False`, `deleted_at` puesto; conteo `0` |
| Dos superadmins: A hace `PATCH {"is_active": false}` y `DELETE` sobre B | `403` y `403` (jerarquía, l.62 y l.37) |

Conclusión de la sonda: las dos únicas vías por las que baja el número de superadmins activos son las dos de la fila,
y las dos son autoservicio. Un superadmin no puede desactivar ni borrar a un par.

## Ficheros afectados (mapa completo)
- `app/services/user_access_policy.py` — las dos guardas sin la regla (l.34-37 borrado, l.75 `is_active`) y los
  docstrings que describen la paridad de auto-borrado (l.10-13, l.24, l.46-49).
- `app/services/user_service.py` — `delete_user_account` (l.177-224) y `update_user_account` (l.248-297): los dos
  puntos donde la regla tiene que tener el conteo a mano (la política es pura, sin repositorio); docstrings l.180-183,
  l.254-257 y comentario l.204.
- `app/repositories/user_repository.py` — `count_active_superadmins` (l.23-41), ya existente; su docstring (l.26) solo
  nombra al bootstrap como consumidor.
- `app/core/exceptions.py` + `app/main.py` (`_DOMAIN_ERROR_STATUS`, l.121-132) — si la respuesta es 409, falta la
  excepción de dominio y su registro (AGENTS §3: en el mismo PR o el fallback da 500).
- `tests/test_user_access_policy.py` — l.57-60 congela el auto-borrado del superadmin como deseado; no hay test HTTP
  de auto-desactivación ni de auto-borrado de un superadmin.
- `app/api/routers/user.py` — solo docstring del DELETE (l.133-134); la ruta no cambia.

## Rincones no mencionados por la fuente
1. **Línea de la fila desactualizada.** La fila cita `user_access_policy.py:65` y `assert_can_delete, l.31-34`; hoy son
   l.75 y l.34-37 (BE-02 añadió la guarda de rol propio y docstrings). El fondo no cambia.
2. **No existe excepción para 409.** La fila pide 409; el mapa de dominio actual solo tiene 400/401/403/404/415/503.
   La regla necesita una `DomainError` nueva registrada en `_DOMAIN_ERROR_STATUS`, o aceptar 400 con
   `BusinessRuleViolationError`. Es decisión de contrato.
3. **La política es pura y no puede contar.** `UserAccessPolicy` no recibe repositorio (constructor sin dependencias,
   `user_access_policy.py:7-19`); el conteo vive en `UserRepository`. Quien decide dónde se cruza el dato (el servicio
   pasa el conteo a la política, o el servicio aplica la regla) es el planificador; AGENTS §3 pone las reglas que
   dependen del dato en `UserAccessPolicy`.
4. **Carrera entre comprobar y escribir.** Con dos superadmins activos que se borran o desactivan a la vez, cada
   petición puede contar 2 y las dos pasan: queda 0. La suite no lo puede reproducir (`StaticPool`, una conexión,
   AGENTS §5; aislamiento real en BE-31). No hay restricción en BD que lo impida (un CHECK no puede contar filas).
5. **`{"is_active": true}` propio y `{"is_active": null}`.** El primero es un no-op legítimo y no debe bloquearse: la
   regla tiene que leer el **valor**, a diferencia de la guarda de `role`, que lee la clave (l.67, l.72). El segundo es
   BE-37 (NOT NULL → 409 genérico), no de este ítem.
6. **Test de `test_auth.py:167-185`** (`test_self_soft_delete_keeps_row_and_blocks_login`) borra a un turista
   (`persist_user` crea turistas por defecto, `tests/conftest.py:185`); no lo afecta la regla.
7. **Mock con `autospec` en `tests/test_user_service.py:70-73`.** Si el servicio llama a `count_active_superadmins`,
   los tests unitarios que llegan a la política con un superadmin necesitarán `return_value` explícito; los actuales
   (`:148-175`) cortan antes, en el 404.

## Patrones de detección (copiables)
```bash
# 1. Guardas de borrado y de is_active en la política (hoy: l.34, l.37, l.75)
git grep -n -E 'is_self_deletion|"is_active" in update_dict' -- app

# 2. Consumidores del conteo de superadmins activos (hoy: repo l.23 y superadmin_bootstrap.py:42; tras BE-35, también la regla)
git grep -n 'count_active_superadmins' -- app

# 3. El test que congela el auto-borrado del superadmin como deseado (hoy: l.57-60)
git grep -n 'test_superadmin_self_delete_is_allowed' -- tests

# 4. Docstrings y comentarios que describen la paridad de auto-borrado
git grep -n -i -E 'self-deletion|act on their own account' -- app

# 5. Respuestas 409 (hoy: solo app/main.py:107, handler de IntegrityError; ninguna DomainError mapea a 409)
git grep -n 'HTTP_409' -- app

# 6. Tests HTTP que envían is_active=False (hoy: solo tests/test_auth.py:248, un turista sobre sí mismo -> 403;
#    ninguno de un superadmin)
git grep -n -E 'json=\{"is_active": False\}' -- tests
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `87b9905` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop`; HEAD = origin/develop, árbol limpio)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Python 3.14.3), salida 0.

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

- pytest: `691 passed, 8 warnings in 29.51s` (0 failed)
- Cobertura total: `97.63%` (mínimo exigido 92.0%). `user_access_policy.py` 100 % (omitido por cobertura completa),
  `user_service.py` 99.16 % (rama `288->297`), `user_repository.py` 97.14 % (l.80).
- ruff format: `68 files already formatted` · ruff check: `All checks passed!` (0) · mypy:
  `Success: no issues found in 63 source files` (0)
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas `api | cli -> services -> repositories -> models` KEPT; Los
  servicios no conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los modelos
  y los schemas no dependen de capas superiores KEPT)
- La compuerta no falla antes de tocar nada.

## Conclusión para el planificador
Resolver las dos vías medidas: auto-`DELETE` y auto-`PATCH {"is_active": false}` del último superadmin activo deben
fallar sin mutar estado ni escribir auditoría, reutilizando `UserRepository.count_active_superadmins`; la regla lee el
valor (`False`), no la clave, para no bloquear `{"is_active": true}`. Hay que cambiar
`test_superadmin_self_delete_is_allowed` (l.57-60) y añadir tests HTTP de ambas vías (último → rechazo; con un segundo
superadmin activo → 200). Decisiones previas que el plan debe fijar: el código (409 con `DomainError` nueva registrada
en `_DOMAIN_ERROR_STATUS`, o 400 con `BusinessRuleViolationError`), dónde se cruza el conteo con la política pura, y si
lleva ADR (el plan de BE-02, l.72, dejó escrito que esta regla "pasaría a requerir ADR"). No tocar: BE-36
(recuperar entre pares), BE-37 (`None` explícito), BE-38 (auditoría), A3 (`commit()` en repositorio), guards ni rutas.
Riesgo: la carrera entre contar y escribir (rincón 4) no se cierra con un conteo en Python ni se puede probar en la
suite; el plan debe declararla como límite aceptado o tratarla aparte.

## Adenda — decisiones de David antes de planear (16 nov 2026, 10:31, sesión Mentor)

Resuelve lo que la conclusión deja abierto y **cambia la regla que la fila proponía**. El planificador toma estas
decisiones como dadas; lo demás (fases, tests, commits, nombres) es suyo. Regla del verificador: no reescribir, añadir.
**Veredicto aceptado: confirmada. Línea base aceptada:** `87b9905`, compuerta completa en verde (691 passed · 97,63 % ·
ruff 0 · mypy 0 en 63 archivos · 4 kept). Severidad: Alta, la de la fila.

Contraste de la sesión Mentor contra el código: `user_access_policy.py:1-79`, `user_service.py:177-297`,
`user_repository.py:23-41,70-87`, `dependencies.py:142-145`, `main.py:100-132`, `core/exceptions.py` (clases),
`tests/test_user_access_policy.py:57-60`, `tests/test_user_service.py:70-73`. **Una corrección de hecho:** el cuerpo cita
`app/api/routers/user.py:126` y `:146` como las rutas; esas líneas están en blanco y los decoradores son `:127`
(`@self_service_router.delete`) y `:147` (`@self_service_router.patch`). El docstring citado como `:133-134` no se
comprobó. El fondo no cambia.

Tres hechos que la verificación no trae (leídos por la sesión Mentor):
- **La tercera vía ya está cerrada.** Un superadmin también dejaría de serlo cambiando su rol; lo bloquea BE-02
  (`user_access_policy.py:72-73`) y lo vigilan `tests/test_user_access_policy.py:481`, `:504`, `:525` y `:545`. Este
  ítem no la reabre.
- **Ningún test HTTP actual depende del auto-borrado ni de la auto-desactivación de un superadmin.** Los ocho
  `client.delete` de `tests/test_user_access_policy.py` (l.288-783) borran a terceros o esperan 403/404; el único
  `{"is_active": False}` de la suite es de un turista (`tests/test_auth.py:248`). De lo existente solo cambia el test
  unitario de la l.57-60.
- **Por la sonda del cuerpo (fila 3 de la tabla), las dos vías de autoservicio son las únicas** por las que baja el
  número de superadmins activos: entre pares, 403 y 403.

### Decisiones (David, "sí a las 7"; son seis puntos y un encargo, el del punto 6)

1. **Regla: ningún superadmin puede borrarse ni desactivarse a sí mismo, haya uno o haya varios.** Sustituye a la
   regla de la fila ("siempre queda al menos un superadmin activo", con conteo y 409 si es el último). Razón de David:
   es la que más sentido le hace. Consecuencia que la sostiene: como entre pares ya no se puede (sonda), si se
   prohíben las dos vías de autoservicio el número de superadmins **no baja nunca desde la aplicación**, así que no
   puede llegar a cero. No hay "último" que detectar.
2. **Respuesta: 403 con `AuthorizationError`**, el mismo molde que "nadie cambia su propio rol" de BE-02
   (`user_access_policy.py:72-73`). No se crea excepción nueva ni entrada en `_DOMAIN_ERROR_STATUS`; el rincón 2 del
   cuerpo (409) queda sin objeto. Orden: 404 → 403. El rechazo no muta estado ni escribe auditoría, y el superadmin
   rechazado sigue pudiendo operar en la petición siguiente (test, como el de la l.545).
3. **La guarda de `is_active` lee el valor, no la clave:** se rechaza `is_active` a `False` sobre uno mismo;
   `{"is_active": true}` propio sigue pasando (rincón 5 del cuerpo). `{"is_active": null}` es BE-37 y no se toca.
4. **Sin conteo y sin bloqueo.** La política sigue pura y síncrona y no cambia de firma: decide con `actor`, `target` y
   `update_dict`, que ya recibe. El servicio no llama a `count_active_superadmins`, que queda solo para el bootstrap
   (rincones 3 y 7 del cuerpo, sin objeto). **La carrera del rincón 4 desaparece por construcción:** dos peticiones
   simultáneas reciben el mismo rechazo.
5. **ADR-0017, corto, dictado por el planificador:** el número de superadmins no baja desde la aplicación; la baja de
   un superadmin es operación de base de datos hasta que exista el mecanismo del punto 6. Debe declarar el coste
   (abajo) y la alternativa descartada (conteo bajo bloqueo). El plan de BE-02 (`docs/deuda/BE-02/plan.md:72`) ya
   anunciaba que esta regla requeriría ADR.
6. **Fila nueva, BE-55, `Sale → B-FUTURO`:** un mecanismo para dar de baja a un superadmin sin SQL directo. Encargo
   expreso de David, con dos ideas suyas anotadas en la fila.

### Coste aceptado

Una cuenta de superadmin no se puede retirar desde la aplicación: hoy solo podía hacerlo su dueño; con esta regla,
nadie. Si cambia el gerente o una cuenta se ve comprometida, la baja es SQL directo del operador hasta BE-55. David lo
acepta y lo declara.

### Alternativa medida y descartada (queda como dato para BE-55)

La regla de la fila con el conteo bajo bloqueo de filas. Sonda de la sesión Mentor (16 nov, PostgreSQL 16.15 propio,
réplica mínima de `users`, psycopg2, `READ COMMITTED`; dos superadmins A y B que se borran a la vez, cada uno en su
transacción). Salida literal:

```
plain count [('A', 'counted 2 -> deleted'), ('B', 'counted 2 -> deleted')] | active superadmins left: 0
FOR UPDATE [('A', 'counted 2 -> deleted'), ('B', 'counted 1 -> rejected')] | active superadmins left: 1
```

Con `SELECT count(*)` la carrera del rincón 4 es real; con `SELECT id … FOR UPDATE` sobre los superadmins activos se
cierra. Límites: SQL directo, no el repositorio ni asyncpg; no es una base de Azure; SQLite ignora `FOR UPDATE`, así
que la suite no lo vería. Descartada porque la regla del punto 1 no necesita contar.

### Fuera de alcance, sin cambio

BE-36 (recuperar y reactivar entre pares; con la regla del punto 1 el caso "A se desactiva y B no puede reactivarlo"
deja de poder producirse, pero la recuperación que deja inactiva la cuenta sigue ahí y se verifica aparte), BE-37,
BE-38, A3, guards y rutas. Docstrings y comentarios que describen la paridad de auto-borrado (patrón 4 del cuerpo): sí
entran, se corrigen con la regla.

# Verificación — BE-02: un superadmin puede auto-degradarse de rol

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (sección A, fila BE-02, línea 34). El informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` no aplica: la fila cita "B1 (txt)", un archivo de notas de David que no está en el repo ni en `C:\projects\INSUMOS-ecotur-asoprado` por nombre. El hallazgo B1 del informe es otro (`_verify_admin`) (bitácora 2026-11-05, l.59). El vecino del informe es B2 (`admin` que se auto-asigna `superadmin`, l.268), ya corregido. `auto-degrad` y `self-demot` no aparecen en el informe.
**Fecha:** 2026-11-05

## Qué describe el ítem
Título: "Superadmin puede auto-degradarse de rol" (Alta). Resolución que propone la fila: nadie cambia su propio
rol; solo un superadmin cambia roles ajenos; test explícito. Lleva además una decisión de producto pendiente: la
política bloquea la **clave** `role`, no su valor (`user_access_policy.py:60`), y hay que verificar si el formulario
de perfil del cliente Flutter envía `role`.

## Evidencia en el código

**El defecto, con sus tres piezas:**
- `app/services/user_access_policy.py:53-55` — `is_self_update = actor.cedula == target.cedula`; la guarda de jerarquía
  solo corre con `not is_self_update`. Una auto-edición nunca la evalúa.
- `app/services/user_access_policy.py:60` — `if "role" in update_dict and actor.role != UserRole.superadmin:`. Mira el
  rol del actor, no si el destino es él mismo. Un superadmin la pasa siempre.
- `app/services/user_service.py:278-279` — `setattr(target_user, key, value)` aplica el payload sin más filtros. Es el
  único punto de `app/` que muta `role` de una cuenta existente; `user_service.py:88` y `:409` solo fijan el rol al crear.
- `app/schemas/user.py:174` — `role: UserRole | None = None` en `UserUpdate`: el PATCH admite la clave.
- `app/api/routers/user.py:36,147` — el `PATCH /usuarios/{cedula}` cuelga de `self_service_router`; lo alcanza cualquier
  sesión autenticada.

**La regla "self parity" está declarada a propósito en docstrings:**
- `app/services/user_access_policy.py:10-12` — "an actor may always act on their own account".
- `app/services/user_service.py:247-251` — "self-updates are always permitted".

**Comprobación en tiempo de ejecución** (sondas desechables fuera del repo, app real con los fixtures de
`tests/conftest.py`, SQLite; sin tocar código):

| Petición (actor → destino) | Resultado |
|---|---|
| superadmin → sí mismo, `{"role":"tourist"}` | **200**, BD `tourist`, auditoría `UPDATE {'role':'tourist'}` |
| superadmin → sí mismo, `{"role":"admin"}` | **200**, BD `admin`, auditoría `UPDATE {'role':'admin'}` |
| superadmin → sí mismo, `{"role":"superadmin"}` (sin cambio) | 200, BD igual, auditoría registra `{'role':'superadmin'}` aunque nada cambió |
| único superadmin tras degradarse: cambiar rol ajeno / `GET /usuarios/` / restaurar su rol | **403 / 403 / 403** (efecto inmediato con el mismo token: `app/api/dependencies.py:108` relee el usuario de BD) |
| superadmin → admin ajeno, `{"role":"tourist"}` | 200, BD `tourist` (legítimo) |
| superadmin → superadmin par, `{"role":"admin"}` | 403, BD sin cambio |

**Lo que de la resolución propuesta ya se cumple (no es deuda):**
- Turista y admin no pueden cambiar su propio rol: l.60, con tests HTTP en `tests/test_auth.py:204-218` y
  `tests/test_user_access_policy.py:437-537`.
- Solo un superadmin cambia roles ajenos: l.60, con `tests/test_user_access_policy.py:130-135,398-431`. Un superadmin
  no toca a un par: l.55, `tests/test_user_access_policy.py:149-154`.
- Lo único que persiste es el caso **actor superadmin + destino él mismo + clave `role`**.

**Hueco de tests:** ninguno ejercita ese caso. `test_superadmin_can_mutate_role` (`tests/test_user_access_policy.py:105-109`)
usa un destino turista distinto. Revisé el actor de todos los `client.patch` a `/usuarios/{cedula}` en `tests/`
(`test_auth.py`, `test_user_access_policy.py`, `test_user_response.py`): ninguno es un superadmin sobre sí mismo. Por eso
la suite está en verde con la deuda viva. Ningún test congela el comportamiento defectuoso.

**La nota de la clave `role` y el cliente Flutter** (lectura en `C:\projects\ecotur-asoprado-frontend_MVP_1\ecotur_app`,
`develop` en `543598c`, 21 sep; lo único sin commitear son 7 archivos generados de plugins; **puede no ser el último
estado del frontend**, la bitácora del 5 nov, l.131, menciona cambios de María):
- `lib/view_models/admin_user_form_viewmodel.dart:54-61` — `_buildUpdatePayload()` envía solo `first_name`, `last_name`,
  `phone`, `email`.
- `lib/view_models/admin_kanban_viewmodel.dart:132,135` — los únicos otros `updateUser`, con `{'is_active': …}`.
- `lib/view_models/admin_user_form_viewmodel.dart:72` — `"role"` solo está en el payload de **creación**.
- En esa copia, **ninguna llamada a `PATCH /usuarios/{cedula}` envía `role`**, y el cliente tampoco tiene pantalla para
  cambiar un rol existente. Coincide con la evidencia preliminar de David (bitácora 2026-11-05, l.123-127) y responde a su
  pendiente: no hay otro builder en esa copia. El 403 por clave no muerde a este cliente.
- `tests/test_user_access_policy.py:501-517` (`test_b2_admin_self_role_noop_returns_403`) congela el bloqueo por clave
  para el admin (auditoría de BE-15, `docs/deuda/BE-15/gaps.md:452-457`).

## Ficheros afectados (mapa completo)
- `app/services/user_access_policy.py:10-12,39-42,53-63` — la regla que falta y los docstrings que declaran lo contrario.
- `app/services/user_service.py:247-251` — docstring "self-updates are always permitted". `:272-279` es el flujo que
  aplica el cambio.
- `tests/test_user_access_policy.py:91-161,434-537` — falta la clase de equivalencia del superadmin, unitaria y HTTP.
- Sin cambio esperado, pero parte del camino: `app/schemas/user.py:174`, `app/api/routers/user.py:147-170`.
- `alembic/`: sin relación. No hay CHECK ni trigger sobre el rol, ni hace falta para esta regla: "el actor es el destino"
  no se puede expresar en la BD.

## Rincones no mencionados por la fuente

Fuera del alcance literal de BE-02. Decide David si entran; ninguno se debe arreglar "de paso".

1. **Consecuencia de gobernanza: no hay vuelta atrás dentro del producto.** Un único superadmin degradado deja el sistema
   sin nadie que provisione administradores (`user_access_policy.py:97`) ni cambie roles (l.60). `app/`, `alembic/` y
   `scripts/` no tienen seed ni bootstrap de superadmin (patrón 6): solo se recupera con SQL directo.
2. **Otras dos vías al mismo bloqueo, que la regla de BE-02 no cierra.** Medidas: un superadmin que se envía
   `{"is_active": false}` recibe 200 y su siguiente petición da 401 (l.65 solo excluye turistas). Un único superadmin que
   se elimina (`DELETE /usuarios/{su cédula}`) recibe 200 y su siguiente petición da 401 (`assert_can_delete`, l.31-34,
   con paridad; el test `test_superadmin_self_delete_is_allowed` en `tests/test_user_access_policy.py:57` lo congela como
   deseado). La regla "nadie cambia su propio rol" no protege de ninguna de las dos. "Que siempre quede un superadmin" es
   otra regla, que nadie ha pedido.
3. **Superadmin recuperado sin activación posible.** Medido: un superadmin recupera a un par (200; `assert_can_recover`,
   l.82), la recuperación fuerza `is_active=False` (`user_service.py:349`), y el PATCH `{"is_active": true}` da 403 por
   l.55 entre pares. El par queda sin borrar pero inactivo; sin SQL no vuelve a entrar.
4. **`{"role": null}` de un superadmin da 409, no 422.** Medido: `UserUpdate` admite `None` (`schemas/user.py:174`),
   `exclude_unset` conserva la clave (`user_service.py:272`), l.60 la deja pasar y la restricción NOT NULL
   (`alembic/versions/a0f621304d75_*.py:44`) cae en el handler genérico de `app/main.py:101-108`. El admin recibe 403. El
   molde de campos opcionales con `None` es común a `is_active` (`schemas/user.py:175`) y demás; no medí esos.
5. **La auditoría registra claves enviadas, no cambios.** Medido con `{"role":"superadmin"}` sin cambio
   (`user_service.py:282-289`).

## Patrones de detección (copiables)

```bash
# 1. Las guardas: paridad de auto-edición y filtro por rol del actor
git grep -n -E '"role" in update_dict|is_self_update' -- app
# Hoy: user_access_policy.py:53, :55, :60

# 2. Único punto de mutación del rol de una cuenta existente
git grep -n -E 'setattr\(target_user' -- app
# Hoy: user_service.py:279

# 3. Campo role en los DTOs (entrada de update: l.174)
git grep -n -E '^\s+role: UserRole( \| None = None)?$' -- app/schemas/user.py

# 4. Hueco de test: unitario con superadmin sobre sí mismo (hoy 0 coincidencias, exit 1)
git grep -n -E 'assert_can_update\(superadmin, *superadmin' -- tests

# 5. Docstrings que declaran la paridad sin excepción
git grep -n -E 'self-updates are always permitted|may always act on their own' -- app
# Hoy: user_access_policy.py:11, user_service.py:248

# 6. Bootstrap de superadmin (hoy 0 coincidencias, exit 1)
git grep -n -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts
```

**Prueba de comportamiento:** ningún grep demuestra esto; lo demuestra este test. Hoy responde 200 y degrada.

```python
async def test_probe(client, db_session, persist_user, make_auth_headers):
    sa = await persist_user(role=UserRole.superadmin)
    r = await client.patch(
        f"/usuarios/{sa.cedula}", json={"role": "tourist"}, headers=make_auth_headers(sa)
    )
    await db_session.refresh(sa)
    print(r.status_code, sa.role)  # hoy: 200 UserRole.tourist
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `c6422ed`. `git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop` = `c6422ed`; precondición cumplida. Rama `item/be-02`, árbol limpio.
- Comando: `./venv/Scripts/python.exe scripts/check.py` (exit 1). **La compuerta ya falla antes de tocar nada**, por
  deuda heredada (ADR-0005), no por BE-02.

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

- pytest: `396 passed, 5 warnings in 19.24s` (0 failed).
- Cobertura total: **94.81 %** (`TOTAL 942 34 136 22 94.81%`; piso 92.0 %). `app/services/user_access_policy.py` entre
  los 22 archivos al 100 %; `app/services/user_service.py` 99.15 % (`282->291`).
- ruff format: `53 files already formatted`. ruff check: `Found 54 errors.` mypy: `Found 10 errors in 5 files (checked
  35 source files)`.
- Contratos: `Contracts: 4 kept, 0 broken.`
  - Capas: api -> services -> repositories -> models KEPT
  - Los servicios no conocen el transporte HTTP KEPT
  - Los repositorios solo conocen SQLAlchemy y los modelos KEPT
  - Los modelos y los schemas no dependen de capas superiores KEPT
- De esos 54 de ruff, 9 están en `app/services/user_access_policy.py` (D205 y E501; líneas 20, 36, 40, 67, 71, 88, 99,
  103, 122). De los 10 de mypy, ninguno en ese archivo; 3 en `app/services/user_service.py` (`:124`, `:132`, `:133`).

## Conclusión para el planificador
- **Resolver:** el caso único **actor superadmin + destino él mismo + clave `role`** en `UserAccessPolicy.assert_can_update`,
  con tests RED unitarios y HTTP (200 hoy) y los dos docstrings que declaran paridad sin excepción. Es una fase pequeña.
- **Decisión para David antes de aprobar el plan:** bloquear por **clave** (como l.60 hoy: `{"role":"superadmin"}` sin
  cambio da 403) o por **valor** (reenviar el rol actual pasa). La clave es coherente con `test_b2_admin_self_role_noop_returns_403`, que no
  habría que tocar; el valor obliga a ajustarlo y a decidir el caso del admin. El cliente Flutter no envía `role` en ningún
  PATCH (copia local de `543598c`, a confirmar contra el estado actual), así que hoy ninguna de las dos rompe al cliente.
  La nota pendiente del backlog puede cerrarse con esto.
- **No tocar:** las guardas de admin y turista ni la de pares, que ya cumplen y tienen tests y mutantes (BE-15 fase E); el
  schema `UserUpdate`; `alembic/`, porque la regla no requiere esquema. Tampoco el residual de ruff del archivo: esas 9
  líneas son de BE-33; si el plan reescribe el docstring de l.39-42, la D205 de l.40 puede cambiar, y el trinquete (ADR-0005) solo exige no añadir.
- **Riesgo principal:** creer que esto garantiza "siempre queda un superadmin". No lo garantiza: `is_active:false` y
  auto-eliminación siguen dejando el sistema sin superadmin, y el test de `test_user_access_policy.py:57` congela la
  segunda como deseada. Si David quiere esa garantía, es otra regla y otra fila (rincones 1-3), no alcance de BE-02.
- **Riesgo de cierre:** medido con un parche en memoria de la regla por clave (actor = destino + clave `role` → 403;
  sin tocar el repo): la suite da `396 passed`, y las tres sondas de auto-edición de rol del superadmin pasan a 403. Si en
  la implementación cae algún test existente, el cambio tocó algo más que este caso.

## Adenda — decisiones de David antes de planear (5 nov 2026, 17:40, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo.

1. **Veredicto aceptado: confirmada.** Planear.
2. **Bloqueo por clave.** Si el payload de una auto-edición (`actor == objetivo`) trae `role`, 403 para cualquier actor,
   superadmin incluido. Coherente con la l.60 y con `test_b2_admin_self_role_noop_returns_403`, que no se toca. La regla
   "solo un superadmin cambia roles ajenos" (l.60) no cambia. Lo que queda igual para los tres roles: perfil propio sí
   (`PATCH` de autoservicio: `first_name`, `last_name`, `phone`, `email`); rol propio nunca. Razón de producto: degradar
   un superadmin a turista no tiene sentido y nadie lo pidió; crear usuarios con rol es otro camino (`POST
   /usuarios/admin`, `user_service.py:88` y `:409`) y no lo toca esta regla. Evidencia del cliente Flutter (5 nov):
   `_buildUpdatePayload()` no envía `role`; solo viaja al crear, desde la pantalla de superadmin.
3. **Los cinco rincones fuera de alcance no se arreglan de paso.** Ya tienen fila en `docs/backlog.md` (v1.15): BE-34
   (bootstrap de superadmin), BE-35 (siempre queda un superadmin activo), BE-36 (recuperar sin reactivar), BE-37
   (`{"role": null}` → 409), BE-38 (auditoría registra claves, no cambios), todas `Entra · B-GHOST-ADMIN`, bloque nuevo
   en PLAN §2b (v2.5), por fechar en §3. El plan los cita si le sirve; no los toca. Nada de esto es "de paso": son casos
   de sustentación (un jurado no debe poder dejar la plataforma sin administrador).
4. **Docstrings: los tres sitios** que lista el mapa de ficheros (`app/services/user_access_policy.py:10-12` y `:39-42`,
   `app/services/user_service.py:247-251`), no "los dos" de la conclusión.
5. **Hash de base.** `c6422ed` es correcto: merge de PR #79 (bitácora del día), sobre `7f64175` (merge de PR #78,
   cierre de BE-15). CONTEXT §8 no cita `7f64175`; la bitácora `2026-11-05` sí, en "Siguiente", y el cierre de hoy lo
   corrige (append-only). La línea base queda como se midió.
6. **ADR-0005.** Si al reescribir el docstring de l.39-42 cambia la D205 de l.40, no se añade ninguna violación y el
   total de ruff no sube. El resto de errores de esas líneas es BE-33 (`Entra · B-TESTS`), no de este plan.

# Gaps — BE-40

## Auditoría Fase A — 2026-11-12
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, sobre `3eec1b9`):

- Árbol: `git status --short` limpio antes y después de la compuerta (este `gaps.md` es el único archivo nuevo).
- `progress.json`: `Fase_A` `completed` con `commit: "a138a9e"`; `git show --stat a138a9e` confirma el commit real
  (3 archivos: `app/api/dependencies.py`, `app/api/routers/service.py`, `app/api/routers/user.py`; 28+/26-).
  `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` sin cambios (diff de `3eec1b9`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`;
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `622 passed, 8 warnings` · `Total coverage: 96.47%`. Igual a la línea base de
  `verificacion.md:151-155` y a la fila A del plan.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
  `mypy` → `Success: no issues found in 3 source files`.
- Mensaje de commit: idéntico, línea a línea, al bloque "Commit" de la fase A (`plan.md:180-199`) con
  `<MODELO EJECUTOR>` sustituido (diff vacío).
- Cambios exactos: (1) `dependencies.py:1-2` `from typing import Annotated` + línea en blanco; `:165-170` bloque
  `IDENTITY ALIASES` literal tras `get_current_admin_user`. (2) `user.py`: fuera `Annotated`, `User` y el bloque
  `DEPENDENCY TYPE ALIASES`; import partido `:3-9` en la forma dictada. (3) `service.py:3` import dictado, fuera
  `from app.models.user import User`; los seis handlers con `usuario_actual: AdminDep,` (`:88,145,168,189,210,232`); los
  cuatro reordenados antes de `service_service` con su línea de Args subida; comentario de segmentación `:14-20` intacto.
- Tests: la fase no exige RED ni tests nuevos; ningún test tocado.
- Criterio de aceptación (corregido por E0.1):
  `grep -n "usuario_actual: User = " app/api/routers/service.py app/api/routers/user.py | wc -l` → `0`;
  `grep -rnE "^(UserDep|AdminDep) = " app --include=*.py` → 2 líneas, `app/api/dependencies.py:169-170`.
  El grep original sobre `app/` da 1 (`app/api/routers/audit.py:24`), lo que E0.1 prevé y retira la fase B.
- AGENTS.md: capas respetadas (`service.py` ya no importa de `user.py`; 4 contratos KEPT); sin excepciones de dominio
  nuevas; código y comentarios en inglés.

## Auditoría Fase B — 2026-11-12
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, sobre `cd475ee`):

- Árbol: `git status --short` limpio antes y después de la compuerta y de los mutantes (este bloque de `gaps.md` es el
  único cambio).
- `progress.json`: JSON válido; `Fase_B` `completed` con `commit: "0739e24"`; `git show --stat 0739e24` confirma el commit
  real (4 archivos: `app/api/dependencies.py`, `app/api/routers/audit.py`, `app/services/audit_service.py`,
  `tests/test_audit.py`; 77+/50-). `current_target` = `Fase_C`; `last_handoff` presente; `edit_rules` sin cambios
  (diff de `cd475ee`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`;
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `625 passed, 8 warnings` · `Total coverage: 96.82%`. Igual a la fila B del plan y al
  handoff; por encima de la línea base de `verificacion.md:151-152` (622 passed, 96,47 %).
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` (los 3 de `app/`) → `Success: no issues found in 3 source files`.
- Archivos de la fase: `git diff --name-only c8f3784 0739e24` = exactamente los 4 de `plan.md:204`.
- Mensaje de commit: idéntico, línea a línea, al bloque "Commit" de la fase B (`plan.md:266-288`) con
  `<MODELO EJECUTOR>` sustituido (diff vacío).
- Cambios exactos: (1) `audit_service.py`: fuera los imports de `User` y `UserAccessPolicy`; `__init__` con solo
  `audit_repo` y `-> None`; `retrieve_audit_history` sin `current_user`, sin su Args, sin `Raises:` y sin la llamada a
  `assert_is_admin_plus`; resumen y primer párrafo literales del plan; `log_transaction` intacto. (2) `dependencies.py:42-45`
  `get_audit_service` sin la política, `return AuditService(audit_repo)`; `get_user_access_policy` sigue en uso por
  `get_user_service` (`:51`). (3) `audit.py:3` import dictado, fuera `User`, el parámetro y el argumento; docstring
  `:23-31` según E0.2 (párrafo entero sustituido, resumen y línea en blanco intactos). (4) `tests/test_audit.py`: imports
  dictados (`:5` `SQLAlchemyError` tras `import pytest`); clase `TestAuditServiceHistory` con el docstring del plan,
  fixture autospec y `AuditService(audit_repo)`; test HTTP de filtros al final (`:143`) con el docstring del plan.
- Tests: los 4 unitarios (`tests/test_audit.py:62,84,94,105`) y el HTTP (`:143`) existen con los nombres del plan y pasan.
  RED re-medido en copia desechable (estado `c8f3784` + `tests/test_audit.py` nuevo): `4 failed, 3 passed`, los cuatro con
  `TypeError: AuditService.__init__() missing 1 required positional argument: 'user_access_policy'`. Coincide con
  `plan.md:255-257` y con el handoff.
- Mutante M4 re-medido en copias desechables (procedimiento común): estado A → `333 passed` (sobrevive); estado B →
  `2 failed, 334 passed` con `test_protected_route_rejects_request_without_token[GET /auditoria/]` y
  `test_admin_route_rejects_tourist[GET /auditoria/]`. Copia de B sin mutante: `336 passed` (fila B, columna copia).
  Coincide con `plan.md:258-259`.
- Criterio de aceptación (con E0): `grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py`
  → `0`; `grep -c "Over-fetching" app/api/routers/audit.py` → `1` (E0.2); `grep -rn "usuario_actual: User = " app
  --include=*.py | wc -l` → `0` (E0.1, vale desde B); `grep -A3 "def get_audit_service" app/api/dependencies.py | grep -c
  "user_access_policy"` → `0`.
- Precisiones declaradas por el ejecutor, valoradas sin hallazgo: (a) los 4 unitarios sin docstring propio: el plan no lo
  dicta y su regla de alcance (`plan.md:103-104`) prohíbe docstrings fuera de los dictados; la clase lo lleva. (b) el
  `assert_called_once_with(limit=20, offset=0, entity_name="Ghost", entity_id=None)` extra en
  `test_returns_empty_list_when_repository_has_no_rows` (`tests/test_audit.py:101-103`): lo exige AGENTS §5 (llamadas a
  mocks con argumentos), no cambia el nombre, el número de tests ni las cifras.
- AGENTS.md: capas respetadas (4 contratos KEPT); sin excepciones de dominio nuevas; mock con
  `create_autospec(..., instance=True)`; usuarios y cabeceras por fábricas; el test HTTP cumple ADR-0011 (el repositorio
  confirma con `commit()` antes de la petición, `audit_repository.py:16`); aserciones sobre código y estructura, ninguna
  sobre texto en español. `assert_is_admin_plus` queda sin llamadores en `app/` con sus tests
  (`tests/test_user_access_policy.py:287-312`), como prevé el plan (fase D).

## Auditoría Fase C — 2026-11-12
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, sobre `cc17660`):

- Árbol: `git status --short` limpio antes y después de la compuerta y de los mutantes (este bloque de `gaps.md` es el
  único cambio).
- `progress.json`: JSON válido; `Fase_C` `completed` con `commit: "349a329"`; `git show --stat 349a329` confirma el commit
  real (3 archivos: `app/api/dependencies.py` 24+/0-, `app/api/routers/user.py` 21+/9-, `tests/test_route_guards.py`
  31+/6-). `current_target` = `Fase_D`; `last_handoff` presente; `edit_rules` sin cambios (diff `189dd45..cc17660`).
  `cc17660` solo toca `handoff-Fase_C.md` y `progress.json`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`;
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `626 passed, 8 warnings` · `Total coverage: 96.84%` (`TOTAL 968 19 140 16 96.84%`).
  Igual a la fila C del plan y al handoff; por encima de la línea base de `verificacion.md` (622 passed, 96,47 %).
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
  `mypy` (los 3) → `Success: no issues found in 3 source files`.
- Archivos de la fase: `git diff --name-only 189dd45 349a329` = exactamente los 3 de la fase C del plan. Fuera de alcance
  intacto: `tests/test_auth.py` sin diff desde `189dd45`; `assert_can_provision_admin` (`app/services/user_access_policy.py:98`,
  llamada en `app/services/user_service.py:396`) y `assert_is_admin_plus` (`user_access_policy.py:115`) siguen en su sitio
  para la fase D.
- Finales de línea: 0 líneas con CR en los 3 archivos, tanto en `HEAD` como en el árbol; `git ls-files --eol` →
  `i/lf w/lf` en los 3; `git diff --ignore-cr-at-eol --stat 189dd45 349a329 -- tests/test_route_guards.py` da las mismas
  31+/6- que el diff normal, así que el commit no lleva cambios espurios de fin de línea; el diff no contiene ningún `\r`.
- Mensaje de commit: idéntico, línea a línea, al bloque "Commit" de la fase C del plan, con `<MODELO EJECUTOR>` sustituido
  (diff vacío); incluye `feat(auth)!` y el footer `BREAKING CHANGE` (E0.4).
- Cambios exactos: (1) `dependencies.py:164-185` `get_current_superadmin_user` literal (firma, docstring, `!=
  UserRole.superadmin` → 403), entre `get_current_admin_user` y el bloque de alias, con dos líneas en blanco antes y
  después; `:193` `SuperadminDep` tras `AdminDep` (E0.3). (2) `user.py`: import con `SuperadminDep,` tras `AdminDep,` y
  `get_current_superadmin_user,` tras `get_current_admin_user,`; bloque `ROUTER SEGMENTATION` literal;
  `superadmin_router` tras `admin_router`; encabezado `:238-240` con el mismo formato que `# ADMIN ENDPOINTS` (`:173-175`)
  y dos líneas en blanco; decorador y `usuario_actual: SuperadminDep,`; párrafo y línea de Args del docstring literales;
  `router.include_router(superadmin_router)` al final (`:272`). Método, ruta y schema sin cambios. (3)
  `tests/test_route_guards.py`: docstring de `ProtectedRoute` en dos líneas, `Literal["superadmin", "admin", "user"]`,
  comentario de `_EMPTY_BODY` en una línea, fila `"superadmin"`, `ADMIN_ROUTES` con el comentario y el filtro dictados
  (E0.7, conserva el nombre), `SUPERADMIN_ROUTES`, y `test_superadmin_route_rejects_admin` tras el test de turista con el
  docstring dictado, `persist_user(role=UserRole.admin)`, `make_auth_headers(admin)` y las mismas aserciones que el caso
  turista.
- E0: ninguna corrección de dictado afecta a la fase C; E0.3, E0.4 y E0.7 se cumplen como arriba; E0.5 deja el contrato
  422 → 403 declarado para el PR, sin bloquear.
- Tests: RED re-medido en copia desechable (`189dd45` + `tests/test_route_guards.py` de `349a329`):
  `1 failed, 45 passed`, `assert 422 == 403` en `test_superadmin_route_rejects_admin[POST /usuarios/admin]`. Coincide con
  el plan y el handoff. La colección da `46 tests collected` con `test_admin_route_rejects_tourist[POST /usuarios/admin]`,
  `test_protected_route_rejects_request_without_token[POST /usuarios/admin]` y el caso nuevo; `test_route_guards.py` +
  `test_auth.py` → `66 passed`.
- Mutantes re-medidos en copias desechables (procedimiento común, `git archive HEAD`): control `337 passed` (fila C,
  columna copia); MS1 → `1 failed, 336 passed` (`test_superadmin_route_rejects_admin[POST /usuarios/admin]`); MS2 → el
  mismo `1 failed, 336 passed`; MS3 → `2 failed, 335 passed` (más `test_admin_route_rejects_tourist[POST /usuarios/admin]`).
  Coinciden con el plan y el handoff.
- Criterio de aceptación: `grep -cE '^    ProtectedRoute\(".*", "superadmin"' tests/test_route_guards.py` → `1`;
  `tests/test_auth.py` sin cambios y verde.
- AGENTS.md: capas respetadas (4 contratos KEPT); el guard nuevo vive en la capa HTTP (`HTTPException` en
  `dependencies.py`, no en un servicio), así que no hace falta excepción de dominio; la ruta ya estaba en el inventario de
  `tests/test_route_guards.py` (ADR-0012, punto 4) y cambia de guard; usuarios y cabeceras por fábricas, sin mocks;
  aserciones sobre código, cabecera y estructura, ninguna sobre texto en español; código y comentarios en inglés.

## Auditoría Fase D — 2026-11-12
**Veredicto Fase D: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase D — El test sustituto no afirma los argumentos de la búsqueda que falla. AGENTS §5 pide llamadas a mocks con argumentos; aquí solo se comprueba que las dos escrituras no ocurrieron. Una línea más lo cerraría: `user_repo.get_user_by_email_or_cedula.assert_awaited_once_with(email=…, cedula=…)`. El plan dicta el test tal como está, y el test del duplicado (`:343-354`) tiene el mismo hueco, así que no es una desviación. Va como sugerencia para `B-TESTS-2`. Evidencia: `tests/test_user_service.py:357-369`.

Evidencia (auditor, contexto fresco, sobre `7d66cfc`):
- Árbol: `git status --short` vacío. `git log` muestra `09ec81b` (fase) y `7d66cfc` (registro) sobre `b0de901` (PASS de C).
- `progress.json`:
  - `Fase_D` está `completed` con `commit: "09ec81b"`, y `git show --stat 09ec81b` lo confirma: 4 archivos, 16+/108−.
  - `last_handoff` apunta a `handoff-Fase_D.md` y `edit_rules` no cambia.
  - `current_target: null` es coherente con el sistema. `scripts/check_docs.py:473-480` solo da un ítem por `done` si `current_target` es `null` y todas sus fases están `completed`. Los 15 `progress.json` de `docs/deuda/` tienen `null`. `check_docs.py --estado` da para BE-40: "ejecutado (todas las fases); pendiente de PR o mezclado … última auditoría: PASS" (antes de este bloque).
  - El plan no fija el valor final. E0 solo fija el valor que tenía al aprobarse (`Fase_A`).
  - `last_handoff` habla de "8 tests" y `description` de "9 tests". Las dos cifras son coherentes: se borran 8 tests de la política y 1 del servicio se sustituye.
- Compuerta: `./venv/Scripts/python.exe scripts/check.py` sale con 0. Resultados:
  - `618 passed, 8 warnings`, `Total coverage: 96.81%` (`TOTAL 961 19 136 16 96.81%`).
  - `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files` y `Contracts: 4 kept, 0 broken.`
  - Cifras iguales a la fila D del plan y al handoff. La cobertura no baja de la línea base de `verificacion.md:151-152` (622 / 96,47 %).
  - Ruff y mypy sobre los 4 archivos de la fase: `All checks passed!` y `Success: no issues found in 4 source files`.
- Commit frente al plan:
  - El mensaje es idéntico al del plan, con `<MODELO EJECUTOR>` sustituido (comparado con `diff`).
  - Toca exactamente los 4 archivos de la fase.
  - (1) `user_access_policy.py`: se borran `assert_can_provision_admin` y `assert_is_admin_plus`, y el docstring de la clase queda literal (`:15-16`). El diff no toca `assert_can_delete`, `assert_can_update`, `assert_can_recover` ni `can_see`.
  - (2) `user_service.py`: desaparecen la llamada y la línea `AuthorizationError` de `Raises:`. El párrafo (`:379-381`) y la línea de Args en dos líneas quedan literales.
  - (3) `test_user_access_policy.py`: se borran `TestAssertCanProvisionAdmin` (3 tests) y `TestAssertIsAdminPlus` (5 tests).
  - (4) `test_user_service.py`: el import queda como dicta el plan y el test sustituto tiene el nombre, la firma, el docstring, el `side_effect`, el actor superadmin, el `pytest.raises` y las dos aserciones `assert_not_awaited` dictadas.
- E0: ninguna corrección de dictado toca la fase D. E0.6 (el test de fallo de BD) se cumple. E0.8 (R1 → BE-48, `B-TESTS-2`) consta en `docs/backlog.md:95`.
- AGENTS §5 en el test sustituto:
  - Los mocks son los fixtures `create_autospec(…, instance=True)` (`:66-74`) y el actor sale de `make_user`. No hay texto en español.
  - La provisión conserva dos caminos de fallo en el servicio: duplicado (`:343`) y fallo de BD (`:357`), más el camino feliz (`:320`).
  - No hacen falta excepciones de dominio nuevas, porque la fase solo borra código.
- Verificación final, pasos 1-10: re-ejecutados uno a uno. Salen 11 / 0 · 0 · 0 / 0 · 6 / 2 · 4 / 0 / 13 / 0 / 3 (todos en `dependencies.py:191-193`) · 7 · 0 · `42:` / 17 / 1 / 13 / 3 · 0 y 0 · `46 passed`. Todo cuadra.
  - Nota: los predicados de la política están ahora en `:67, 75, 94, 111`. El comentario del paso 4 del plan cita l.66, 74 y 93, porque el docstring de la clase gana una línea. La cifra es la misma.
- Paso 11: es la compuerta de arriba.
- Paso 12: mutantes re-medidos en copias desechables nuevas (`git archive`, edición comprobada con `grep`):
  - RED en el estado C (`b0de901`), MS1: `1 failed, 336 passed` (`test_superadmin_route_rejects_admin[POST /usuarios/admin]`).
  - Estado D, control: `329 passed`.
  - MS1: `2 failed, 327 passed` (más `tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row`).
  - MS2: `2 failed, 327 passed` (los mismos).
  - MS3: `3 failed, 326 passed` (más `test_admin_route_rejects_tourist[POST /usuarios/admin]`).
  - M4: `2 failed, 327 passed` (`…without_token[GET /auditoria/]` y `test_admin_route_rejects_tourist[GET /auditoria/]`).
  - Todos coinciden con el plan y con el handoff.
- `tests/test_auth.py`, `alembic/` y los `conftest.py` siguen intactos desde `41ff01d` (paso 1, segunda línea: 0).

Cierre del ítem: las cuatro fases tienen PASS y la Verificación final cuadra (pasos 1-12). Quedan pendientes los residuales que no son de ningún ejecutor:
- R1 hecho (BE-48 en `B-TESTS-2`, `docs/backlog.md:95`).
- R2 anotado fuera de BE-40 (`docs/CONTEXT.md`).
- R3 pendiente: `AGENTS.md:48` sigue diciendo `"admin"` o `"user"`. Lo hace David antes de `/pr`.
- R4 pendiente: la fila D1 (`docs/backlog.md:115`) aún cita `user_access_policy.py:130`. Faltan la nota en BE-42 y el estado de la fila BE-40. Lo hace la sesión Mentor al cerrar.
- P3/E0.5: el cambio 422 → 403 se declara en el PR y no lo bloquea.

## Auditoría Fase E — 2026-11-12
**Veredicto Fase E: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. El OPCIONAL de la auditoría de la fase D (el test sustituto no afirmaba los argumentos de la búsqueda que falla, `tests/test_user_service.py:357-369` en `09ec81b`) queda **RESUELTO (`9ff32a9`)**: `test_create_administrative_account_lookup_failure_writes_nothing` afirma ahora `get_user_by_email_or_cedula.assert_awaited_once_with(email="newadmin@test.com", cedula="5555555555")` (`tests/test_user_service.py:377-379`). El mismo hueco del test del duplicado, que aquel opcional citaba, también queda cerrado (`:360-362`). El bloque de D no se edita.

Evidencia (auditor, contexto fresco, sobre `d141d4e`):
- Árbol: `git status --short` vacío. `git log` muestra `9ff32a9` (fase) y `d141d4e` (registro) sobre `54a4551`. La aprobación es `d49bc9a` (E2). `git diff --name-only 54a4551 HEAD` da `handoff-Fase_E.md`, `progress.json` y `tests/test_user_service.py`.
- `progress.json`:
  - Es JSON válido.
  - `Fase_E` está `completed` con `commit: "9ff32a9"`, y `git show --stat 9ff32a9` lo confirma: 1 archivo, 12+/0−.
  - `current_target` pasa de `"Fase_E"` a `null`: es la última fase, y se aplica el mismo criterio que en la auditoría de D (`check_docs.py:473-480`).
  - `last_handoff` apunta a `handoff-Fase_E.md`. `edit_rules` y las fases A–D no cambian: el diff de `d141d4e` solo toca `current_target`, `Fase_E.status`, `Fase_E.commit` y `last_handoff`.
  - `check_docs.py --estado` da `BE-40: … ejecutado (todas las fases); pendiente de PR o mezclado … última auditoría: PASS`.
- Compuerta: `./venv/Scripts/python.exe scripts/check.py` sale con 0. Resultados:
  - `618 passed, 8 warnings` y `TOTAL 961 19 136 16 96.81%`.
  - `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.` y `Compuerta superada.`
  - Cifras iguales a la fila E del plan y al handoff. La línea base es 622 / 96,47 % (`verificacion.md:151-152`), así que la cobertura no baja.
  - Archivo de la fase: `ruff check`: `All checks passed!`. `mypy`: `Success: no issues found in 1 source file`. `ruff format --check`: `1 file already formatted`. Ninguna línea pasa de 100 columnas.
- Commit frente al plan:
  - El mensaje es idéntico al del plan (`plan.md:554-571`), con `<MODELO EJECUTOR>` sustituido. Se comparó con `diff`.
  - Toca solo `tests/test_user_service.py`, y `app/` no aparece.
  - Las cuatro inserciones van en el sitio que dicta el plan y no se borra ninguna línea:
    - `test_register_tourist_duplicate_raises_already_exists`: antes de `create_user.assert_not_called()`.
    - `…_provisions_admin`: antes de `create_user.assert_awaited_once_with(created_user)`.
    - `…_duplicate_raises_already_exists`: antes de `create_user.assert_not_awaited()`.
    - `…_lookup_failure_writes_nothing`: antes de `audit_service.log_transaction.assert_not_awaited()`.
  - Los bloques de tres líneas tienen la forma de `:113-115`.
- Valores frente al payload:
  - El test turista usa `_tourist_payload()` (`:35-46`: `cedula="1005911792"`, `email="turista@example.com"`) y afirma esos valores.
  - Los tres tests de provisión usan `_admin_payload()` (`:49-62`: `cedula="5555555555"`, `email="newadmin@test.com"`) y afirman esos valores.
  - Ningún test pasa `overrides`.
- R5 no se toca. En `git diff 54a4551 HEAD -- tests/test_user_service.py` hay 0 líneas `+`/`-` con `get_user_by_cedula`, `get_non_deleted_user_by_email` o `activate_user`.
- E0, E1 y E2: E1 define la fase, con 4 tests y 1 archivo, y se cumple. E2.1 la aprueba sin correcciones de dictado, así que manda el cuerpo de la sección "Fase E". E2.2 lleva R5 a BE-49, que consta en `docs/backlog.md:96`. Ninguna corrección de E0 toca la fase E.
- Verificación final:
  - Paso 13: `git diff --numstat 09ec81b HEAD -- app tests alembic conftest.py` da `12<TAB>0<TAB>tests/test_user_service.py`, una sola línea (comprobado con `cat -A`). Los greps dan `5`, `3` y `2`.
  - Pasos 1-10, re-ejecutados sobre el estado E: 11 / 0 · 0 · 0 / 0 · 6 / 2 · 4 / 0 / 13 / 0 / 3 · 7 · 0 · `42:` / 17 / 1 / 13 / 3 · `test_audit.py:0` / `test_user_service.py:0` · `46 passed`. Todo cuadra.
  - Paso 11: es la compuerta de arriba.
- Mutantes (pasos 12 y 14):
  - Procedimiento común: una copia nueva de `git archive` por medición, en el scratchpad.
  - En ML1 y ML2, `sed -n '75p;395p'` confirma que solo cambia la línea del mutante. `diff --strip-trailing-cr` contra `git show <rev>:<archivo>` da un único hunk en cada mutante.
  - Resultados:

    | Mutante | Copia | Resultado | Tests que caen |
    |---|---|---|---|
    | Control | E | `329 passed` | — |
    | ML1 | D (`54a4551`) | `1 failed, 328 passed` | `test_register_tourist_returns_registration_result` |
    | ML2 | D (`54a4551`) | `329 passed` | ninguno: sobrevive (RED de la fase) |
    | ML1 | E | `2 failed, 327 passed` | el de D más `test_register_tourist_duplicate_raises_already_exists` |
    | ML2 | E | `3 failed, 326 passed` | `…_provisions_admin`, `…_duplicate_raises_already_exists`, `…_lookup_failure_writes_nothing` |
    | M4 | E | `2 failed, 327 passed` | `…without_token[GET /auditoria/]`, `test_admin_route_rejects_tourist[GET /auditoria/]` |
    | MS1 | E | `2 failed, 327 passed` | `test_superadmin_route_rejects_admin[POST /usuarios/admin]`, `test_auth.py::test_admin_provisioning_admin_returns_403_without_row` |
    | MS2 | E | `2 failed, 327 passed` | los mismos que MS1 |
    | MS3 | E | `3 failed, 326 passed` | los de MS1 más `test_admin_route_rejects_tourist[POST /usuarios/admin]` |

  - Todo coincide con el plan (tabla de la fase E, pasos 12 y 14) y con el handoff.
- Las dos rarezas que anotó el ejecutor no son hallazgos:
  - `app/api/__init__.py` difiere solo en el fin de línea. El índice tiene LF y la copia de trabajo CRLF (`git ls-files --eol`: `i/lf w/crlf attr/text=auto eol=lf`). `.gitattributes` lo normaliza, así que `git status` sale limpio. El archivo no cambia desde `d822671` y BE-40 no lo toca. No afecta a ninguna medición.
  - MS1 y MS2 dan 9 warnings y MS3 10, frente a 8. Re-medido: los extra son `StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY'` en `test_admin_route_rejects_tourist[POST /usuarios/admin]` y `test_superadmin_route_rejects_admin[POST /usuarios/admin]`. Con el guard mutado, la petición llega a la validación del cuerpo y responde 422, que es el síntoma del mutante. En la copia de control y en la compuerta hay 8.

Cierre del ítem: las cinco fases tienen PASS y la Verificación final cuadra (pasos 1-14). Según el plan, el código del ítem está listo para PR. Antes de `/pr` falta un paso que no es de ningún ejecutor:
- R1 hecho (BE-48, `docs/backlog.md:95`).
- R2 fuera de BE-40 (`docs/CONTEXT.md`).
- R3 pendiente y previo a `/pr`. `AGENTS.md:48` sigue diciendo `(`"admin"` o `"user"`)`. Lo hace David en un commit de documentos (adenda, punto 4).
- R4 pendiente, al cerrar. La fila D1 (`docs/backlog.md:116`) sigue citando `user_access_policy.py:130`. La fila BE-40 (`:86`) no está cerrada y BE-42 (`:89`) no tiene la nota del guard de superadmin. Lo hace la sesión Mentor.
- R5 hecho (BE-49, `docs/backlog.md:96`, E2.2).
- P3/E0.5: el cambio 422 → 403 se declara en el PR y no lo bloquea.

# Handoff — BE-40 · Fase D (la política sin reglas de solo rol)

- Commit de la fase: `09ec81b` — `refactor(policy): drop the role-only rules the guards now decide`
- Rama: `item/be-40`, sobre `b0de901` (auditoría PASS de la fase C).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_D`. `gaps.md` de la fase C: PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `41ff01d`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `41ff01d`; `Base develop` de `verificacion.md` = `41ff01d`.
- Compuerta antes de tocar nada (exit 0), igual a la fila C del plan: `626 passed, 8 warnings in 18.43s` ·
  `Total coverage: 96.84%` · `61 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · `Compuerta superada.`

## Archivos tocados (los 4 de la fase)

`git show --stat 09ec81b`:

```
 app/services/user_access_policy.py | 40 ++-------------------------
 app/services/user_service.py       | 12 +++------
 tests/test_user_access_policy.py   | 55 --------------------------------------
 tests/test_user_service.py         | 17 +++++++-----
 4 files changed, 16 insertions(+), 108 deletions(-)
```

Resumen del diff, con el texto que dicta el plan (E0 no corrige nada de la fase D):

1. `app/services/user_access_policy.py`: se borran `assert_can_provision_admin` y `assert_is_admin_plus` (l.98-134). El
   docstring de la clase añade `Rules that depend only on the actor's role / are decided by the HTTP guards, not here
   (ADR-0012, point 1).` tras `layer remains transport-agnostic.`. `assert_can_delete`, `assert_can_update`,
   `assert_can_recover` y `can_see` no cambian (el diff no las toca).
2. `app/services/user_service.py`, `create_administrative_account`: se borran la llamada
   `self.user_access_policy.assert_can_provision_admin(current_user)` con su línea en blanco y la línea
   `AuthorizationError: …` de `Raises:`. El primer párrafo del docstring y la línea de Args de `current_user` quedan con
   el texto dictado (dos líneas, la segunda con 16 espacios).
3. `tests/test_user_access_policy.py`: se borran `TestAssertCanProvisionAdmin` (3 tests) y `TestAssertIsAdminPlus`
   (5 tests), l.260-314. Quedan 4 clases (`TestAssertCanDelete`, `TestAssertCanUpdate`, `TestAssertCanRecover`, `TestCanSee`).
4. `tests/test_user_service.py`: fuera `AuthorizationError` del import de `app.core.exceptions` (lo retiró el autofix de
   ruff del hook al quedar sin uso, que es el cambio que dicta el plan); `from sqlalchemy.exc import SQLAlchemyError` tras
   `import pytest`. `test_create_administrative_account_rejects_non_superadmin` se sustituye por
   `test_create_administrative_account_lookup_failure_writes_nothing(user_repo, audit_service, user_service, make_user)`:
   `get_user_by_email_or_cedula.side_effect = SQLAlchemyError("database unavailable")`, llamada con
   `make_user(role=UserRole.superadmin)` dentro de `pytest.raises(SQLAlchemyError)`,
   `audit_service.log_transaction.assert_not_awaited()` y `user_repo.create_user.assert_not_awaited()`.

## Tests (RED primero)

El RED de esta fase es un mutante. Copia desechable `beD_ms1_stateC` (scratchpad, `git archive HEAD` sobre `b0de901`,
sin archivos de la fase), MS1 aplicado (`role != UserRole.superadmin` → `role not in [UserRole.admin, UserRole.superadmin]`
en `get_current_superadmin_user`), antes de tocar nada:

```
FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
1 failed, 336 passed, 9 warnings in 15.23s
```

`tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row` sigue verde: lo tapa `assert_can_provision_admin`.

Test nuevo de `test_user_service.py`, escrito antes del código y verde sobre el estado C (como dicta el plan; sustituye al
retirado, no es RED): `tests/test_user_service.py tests/test_user_access_policy.py` → `86 passed in 3.73s`.

Checklist de `test-sanitizer` (solo los estándares): los mocks son los fixtures `create_autospec(..., instance=True)` del
archivo; el actor sale de la fábrica `make_user`; aserción sobre el tipo de excepción y sobre las dos escrituras no
ejecutadas (`assert_not_awaited`); nada de texto en español. No hizo falta ningún cambio.

## Mutantes sobre el estado D (procedimiento común)

Una copia nueva por mutante en el scratchpad (`beD_stateD_<m>`), con `git archive HEAD` (`b0de901`) y los 4 archivos de
la fase copiados encima desde el árbol de trabajo; cada edición se comprobó con `grep` en su copia. Comando:
`…/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

- Control (sin mutar, `beD_stateD_none`): `329 passed, 8 warnings in 14.20s` (fila D: 329).
- MS1:
  ```
  FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  2 failed, 327 passed, 9 warnings in 15.32s
  ```
- MS2 (`superadmin_router` con `Depends(get_current_admin_user)` y `usuario_actual: AdminDep`):
  ```
  FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  2 failed, 327 passed, 9 warnings in 14.85s
  ```
- MS3 (`if current_user.role != UserRole.superadmin:` → `if False:`):
  ```
  FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
  FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /usuarios/admin]
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  3 failed, 326 passed, 10 warnings in 14.67s
  ```
- M4 (`router = APIRouter(dependencies=[Depends(get_current_admin_user)])` → `router = APIRouter()` en `audit.py`):
  ```
  FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /auditoria/]
  FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]
  2 failed, 327 passed, 8 warnings in 15.19s
  ```

Los cuatro coinciden con el plan (fase D y Verificación final, punto 12). MS1 pasa de 1 a 2: `test_auth.py:379` ya no
está tapado.

## Criterio de aceptación y Verificación final (pasos 1-10, tras el commit)

```
git diff --name-only 41ff01d HEAD -- app tests alembic conftest.py | wc -l                       11
git diff --name-only 41ff01d HEAD -- alembic conftest.py tests/conftest.py tests/test_auth.py | wc -l   0
grep -rn "assert_is_admin_plus\|assert_can_provision_admin" app tests --include=*.py | wc -l     0
grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py       0
grep -A3 "def get_audit_service" app/api/dependencies.py | grep -c "user_access_policy"         0
grep -rnE "role (not )?in \[|role ?[!=]= ?UserRole" app --include=*.py | wc -l                 6
grep -cE "role (not )?in \[|role ?[!=]= ?UserRole" app/api/dependencies.py                      2
grep -rnE "Depends\(get_current_(admin_)?user\)" app/api/routers --include=*.py | wc -l         4
  … | grep -vc "APIRouter(dependencies="                                                        0
grep -rnE "usuario_actual: (UserDep|AdminDep|SuperadminDep)" app/api/routers … | wc -l          13
grep -rn "usuario_actual: User = \|= Depends(get_current" app/api/routers … | wc -l             0
grep -rnE "^(UserDep|AdminDep|SuperadminDep) = " app --include=*.py | wc -l                    3
grep -rniE "superadmin_user|SuperadminDep" app tests --include=*.py | wc -l                    7
grep -rniE "defen[cs]e in depth|re-asserts|not a duplicate of the transport|gates transport access" app … | wc -l   0
grep -n '"/usuarios/admin"' tests/test_route_guards.py   42:    ProtectedRoute("POST", "/usuarios/admin", "superadmin", _EMPTY_BODY),
grep -c '^    ProtectedRoute("' tests/test_route_guards.py                                     17
grep -cE '^    ProtectedRoute\(".*", "superadmin"' tests/test_route_guards.py                   1
grep -cE '^    ProtectedRoute\(".*", "admin"' tests/test_route_guards.py                        13
grep -c "www-authenticate" tests/test_route_guards.py                                           3
grep -c "AuthorizationError" tests/test_audit.py tests/test_user_service.py    tests/test_audit.py:0 tests/test_user_service.py:0
./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider          46 passed, 3 warnings in 0.83s
```

Todas las cifras coinciden con las esperadas. El paso 11 es la compuerta de abajo; el 12, los mutantes de arriba.

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` → exit 0. Bloque RESUMEN literal:

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

- pytest: `618 passed, 8 warnings in 24.82s` (0 failed). Cobertura: `Total coverage: 96.81%`
  (`TOTAL 961 19 136 16 96.81%`). Línea base del ítem: 622 / 96,47 %; fila D del plan: 618 / 96,81 %. Coincide.
  626 − 8 tests de la política = 618 (el de `test_user_service.py` se sustituye 1 a 1).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.`
- Archivos tocados: `python -m ruff check` (los 4) → `All checks passed!`; `python -m mypy` (los 4) →
  `Success: no issues found in 4 source files`.

## Residuales y dudas

- Sin desviaciones respecto al plan ni a E0. `tests/test_auth.py` y las reglas de dato de la política, sin tocar.
- Para el cierre del ítem siguen abiertos R1 (BE-48, `B-TESTS-2`, según E0 punto 8), R2 (filtro por rol del historial),
  R3 (`AGENTS.md:48`, lo hace David antes de `/pr`) y R4 (anotar en la fila D1 del backlog y en la nota de BE-42).
- `progress.json` queda con `current_target: null` (convención de los 14 ítems cerrados): el plan no tiene fase posterior a D.

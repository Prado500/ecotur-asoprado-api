# Handoff — BE-40 · Fase B (`GET /auditoria/`: el guard del router decide solo)

- Commit de la fase: `0739e24` — `refactor(audit): let the router guard alone decide who reads the trail`
- Rama: `item/be-40`, sobre `c8f3784` (auditoría PASS de la fase A).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_B`. `gaps.md` de la fase A: PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `41ff01d`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `41ff01d`; `Base develop` de `verificacion.md` = `41ff01d`.
- Compuerta antes de tocar nada (exit 0), igual a la fila A del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `622 passed, 8 warnings` · `Total coverage: 96.47%`.

## Archivos tocados (los 4 de la fase)

`git show --stat 0739e24`:

```
 app/api/dependencies.py       |  3 +-
 app/api/routers/audit.py      | 17 +++------
 app/services/audit_service.py | 19 ++--------
 tests/test_audit.py           | 88 ++++++++++++++++++++++++++++++++-----------
 4 files changed, 77 insertions(+), 50 deletions(-)
```

Resumen del diff, todo dictado por el plan (con E0.2):

1. `app/services/audit_service.py`: fuera `from app.models.user import User` y
   `from app.services.user_access_policy import UserAccessPolicy`. `__init__(self, audit_repo: AuditRepository) -> None`
   con solo `self.audit_repo = audit_repo`. `retrieve_audit_history` sin `current_user`, sin su línea de Args, sin
   `Raises:` y sin la llamada `assert_is_admin_plus` (ni la línea en blanco siguiente). Resumen y primer párrafo del
   docstring con el texto literal del plan. `log_transaction` sin cambios.
2. `app/api/dependencies.py`: `get_audit_service` sin el parámetro `user_access_policy`; `return AuditService(audit_repo)`.
   `UserAccessPolicy`/`get_user_access_policy` siguen importados y usados por `get_user_service`.
3. `app/api/routers/audit.py`: import `get_audit_service, get_current_admin_user`; fuera `from app.models.user import User`,
   el parámetro `usuario_actual` y el argumento `current_user=usuario_actual`. **E0.2:** se sustituyó el párrafo entero
   del cuerpo del docstring (antiguas l.28-34, siete líneas, de `Defense in depth…` a `…Over-fetching.`) por las cinco
   líneas dictadas; la línea de resumen y la línea en blanco no cambian.
4. `tests/test_audit.py`: fuera los imports `AuthorizationError` y `UserAccessPolicy` (los retiró el hook de ruff al quedar
   sin uso); `from sqlalchemy.exc import SQLAlchemyError` tras `import pytest`. `TestAuditServiceAuthorization` →
   `TestAuditServiceHistory` (docstring del plan, fixture `audit_repo` con `create_autospec(..., instance=True)`,
   `AuditService(audit_repo)`), con los cuatro tests dictados. Al final, `test_audit_history_filters_by_entity_name_and_id`.

## Tests (RED primero)

RED con solo `tests/test_audit.py` nuevo sobre el estado A
(`./venv/Scripts/python.exe -m pytest tests/test_audit.py -q -p no:cacheprovider -rf`):

```
E       TypeError: AuditService.__init__() missing 1 required positional argument: 'user_access_policy'
FAILED tests/test_audit.py::TestAuditServiceHistory::test_forwards_page_and_filters_to_repository_once
FAILED tests/test_audit.py::TestAuditServiceHistory::test_uses_first_page_of_twenty_without_filters_by_default
FAILED tests/test_audit.py::TestAuditServiceHistory::test_returns_empty_list_when_repository_has_no_rows
FAILED tests/test_audit.py::TestAuditServiceHistory::test_propagates_repository_failure
4 failed, 3 passed in 0.34s
```

El test HTTP de filtros estuvo verde desde el principio (cobertura y borde, como dice el plan). GREEN tras el código:
`7 passed in 0.14s`.

Checklist `test-sanitizer` (solo estándares): mock del repositorio con `create_autospec(AuditRepository, instance=True)`;
usuarios y cabeceras por `persist_user`/`make_auth_headers`; nombres y variables en inglés; ninguna aserción sobre texto en
español. Sin cambios adicionales.

## Mutante M4 (procedimiento común)

Edición: `app/api/routers/audit.py`, `router = APIRouter(dependencies=[Depends(get_current_admin_user)])` →
`router = APIRouter()`. Copias nuevas en el scratchpad (`git archive HEAD | tar -x`, más los 4 archivos de la fase en la
copia de B). Comando: `…/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

- Antes de B (estado A, copia de `c8f3784`): `333 passed, 8 warnings in 11.31s` (sin rojo: M4 sobrevive).
- Después de B:

```
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /auditoria/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]
2 failed, 334 passed, 8 warnings in 12.02s
```

Coincide con el plan.

## Criterio de aceptación

```
$ grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py
0
$ grep -c "Over-fetching" app/api/routers/audit.py          # E0.2
1
$ grep -rn "usuario_actual: User = " app --include=*.py | wc -l   # E0.1: vale desde el final de B
0
$ grep -A3 "def get_audit_service" app/api/dependencies.py | grep -c "user_access_policy"
0
```

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

- pytest: `625 passed, 8 warnings in 17.88s` (0 failed). Cobertura: `Total coverage: 96.82%` (base 96,47 %; fila B del
  plan 96,82 %). `app\repositories\audit_repository.py` sale de la tabla de faltantes (l.35 y 37 ya cubiertas).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Archivos tocados: `python -m ruff check` → `All checks passed!`; `python -m mypy` (los 3 de `app/`) →
  `Success: no issues found in 3 source files`.

## Residuales y dudas

- `UserAccessPolicy.assert_is_admin_plus` queda sin llamadores en `app/`, con sus tests en
  `tests/test_user_access_policy.py:287-312`; lo retira la fase D, como dicta el plan.
- Desviaciones del plan o de E0: ninguna. Dos precisiones: los cuatro tests unitarios no llevan docstring propio (el
  plan no lo dicta; la clase sí lo lleva), y `test_returns_empty_list_when_repository_has_no_rows` añade, además de
  `result == []`, `assert_called_once_with(limit=20, offset=0, entity_name="Ghost", entity_id=None)` (AGENTS §5:
  aserción sobre la llamada al mock; no cambia cifras).

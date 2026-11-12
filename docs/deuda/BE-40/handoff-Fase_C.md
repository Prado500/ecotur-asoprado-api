# Handoff — BE-40 · Fase C (guard de superadmin para `POST /usuarios/admin`)

- Commit de la fase: `349a329` — `feat(auth)!: guard POST /usuarios/admin with a superadmin dependency`
- Rama: `item/be-40`, sobre `189dd45` (auditoría PASS de la fase B).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_C`. `gaps.md` de la fase B: PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `41ff01d`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `41ff01d`; `Base develop` de `verificacion.md` = `41ff01d`.
- Compuerta antes de tocar nada (exit 0), igual a la fila B del plan: `625 passed, 8 warnings` ·
  `Total coverage: 96.82%`, con el RESUMEN entero en verde (`Compuerta superada.`).

## Archivos tocados (los 3 de la fase)

`git show --stat 349a329`:

```
 app/api/dependencies.py    | 24 ++++++++++++++++++++++++
 app/api/routers/user.py    | 30 +++++++++++++++++++++---------
 tests/test_route_guards.py | 37 +++++++++++++++++++++++++++++++------
 3 files changed, 76 insertions(+), 15 deletions(-)
```

Resumen del diff, todo con el texto que dicta el plan (E0 no corrige nada de la fase C):

1. `app/api/dependencies.py`: `get_current_superadmin_user(current_user: User = Depends(get_current_user)) -> User`
   entre `get_current_admin_user` y el bloque de alias, con el docstring dictado y `role != UserRole.superadmin` → 403
   `HTTPException`. `SuperadminDep = Annotated[User, Depends(get_current_superadmin_user)]` tras `AdminDep`.
2. `app/api/routers/user.py`: import con `SuperadminDep` y `get_current_superadmin_user`; el bloque `ROUTER SEGMENTATION`
   queda con el texto dictado; `superadmin_router = APIRouter(dependencies=[Depends(get_current_superadmin_user)])`; el
   encabezado `# SUPERADMIN ENDPOINTS (superadmin only)`; `@superadmin_router.post("/admin", …)` con
   `usuario_actual: SuperadminDep`. El párrafo y la línea de Args del docstring de `crear_administrador` quedan con el
   texto dictado, y `router.include_router(superadmin_router)` va al final. Método, ruta y schema sin cambios.
3. `tests/test_route_guards.py`: el docstring de `ProtectedRoute` queda en dos líneas, el `Literal["superadmin", "admin", "user"]`,
   el comentario de `_EMPTY_BODY` en una sola línea y la fila `ProtectedRoute("POST", "/usuarios/admin", "superadmin", _EMPTY_BODY)`.
   `ADMIN_ROUTES` filtra `guard in ("admin", "superadmin")` y lleva el comentario dictado. Se añaden `SUPERADMIN_ROUTES` y,
   tras el test de turista, `test_superadmin_route_rejects_admin`, con las mismas aserciones que el caso del turista.

## Tests (RED primero)

RED con solo `tests/test_route_guards.py` nuevo sobre el estado B
(`./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider`):

```
>       assert response.status_code == 403
E       assert 422 == 403
FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
1 failed, 45 passed, 4 warnings in 1.09s
```

GREEN tras el código: `tests/test_route_guards.py` + `tests/test_auth.py` → `66 passed`.

**Caso turista → 403 de la fila de provisión, conservado** (E0 y adenda, punto 5). La colección sigue mostrando
`test_admin_route_rejects_tourist[POST /usuarios/admin]` (`-k admin_route_rejects_tourist` → `14 passed`), junto a
`test_protected_route_rejects_request_without_token[POST /usuarios/admin]` y al nuevo
`test_superadmin_route_rejects_admin[POST /usuarios/admin]`; en total se recogen `46 tests collected`.

Checklist de `test-sanitizer` (solo los estándares): el admin y su cabecera salen de las fábricas `persist_user` y
`make_auth_headers`, sin mocks. Las aserciones cubren código, ausencia de `www-authenticate`, estructura (`{"detail"}`) y
tipo, y ninguna afirma sobre texto en español. No hizo falta ningún cambio.

## Mutantes MS1/MS2/MS3 (procedimiento común)

Hay una copia nueva por mutante en el scratchpad (`be40_C_<m>`), hecha con `git archive HEAD | tar -x` y los 3 archivos
de la fase copiados encima. Además hay una copia de control sin mutar, `be40_C_C0`. Comando:
`…/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

- Control (sin mutar): `337 passed, 8 warnings in 11.96s`.
- MS1 (`role != UserRole.superadmin` → `role not in [UserRole.admin, UserRole.superadmin]`):
  ```
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  1 failed, 336 passed, 9 warnings in 12.37s
  ```
- MS2 (`superadmin_router` con `Depends(get_current_admin_user)` y `usuario_actual: AdminDep`):
  ```
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  1 failed, 336 passed, 9 warnings in 12.01s
  ```
- MS3 (`if current_user.role != UserRole.superadmin:` → `if False:`):
  ```
  FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /usuarios/admin]
  FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
  2 failed, 335 passed, 10 warnings in 15.06s
  ```

Los tres coinciden con el plan. Que MS1 tumbe 1 y no 2 es lo esperado:
`tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row` sigue tapado por `assert_can_provision_admin`
hasta la fase D.

## Criterio de aceptación

```
$ grep -cE '^    ProtectedRoute\(".*", "superadmin"' tests/test_route_guards.py
1
$ git diff --name-only HEAD -- tests/test_auth.py | wc -l      # antes del commit; test_auth.py sin cambios
0
$ ./venv/Scripts/python.exe -m pytest tests/test_auth.py -q -p no:cacheprovider
20 passed in 2.83s
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

- pytest: `626 passed, 8 warnings in 25.00s` (0 failed). Cobertura: `Total coverage: 96.84%` (base 96,47 %; fila C del
  plan 96,84 %). `TOTAL 968 19 140 16 96.84%`.
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Archivos tocados: `python -m ruff check` → `All checks passed!`; `python -m mypy` (los 3) →
  `Success: no issues found in 3 source files`.

## Residuales y dudas

- `assert_can_provision_admin` sigue en la política y en `create_administrative_account`, y tapa
  `tests/test_auth.py:379` frente a MS1. Lo retira la fase D, como dicta el plan.
- No hay desviaciones respecto al plan ni a E0. Una nota de proceso: el primer volcado de `tests/test_route_guards.py`
  salió con CRLF (lo escribió `Path.write_text` en Windows) y se normalizó a LF justo después de medir el RED (mismo texto, solo cambian los finales de línea). El commit no
  cambia ningún final de línea: el diff son 31 líneas añadidas y 6 borradas.

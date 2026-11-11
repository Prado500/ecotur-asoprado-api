# Handoff — BE-39 · Fase C (turista: 403 sin `WWW-Authenticate` en las 14 admin)

- **Commit de la fase:** `f980041` — `test(guards): reject a tourist on all 14 admin routes`
- **Ejecutor:** fase-ejecutor (Claude Opus 5.5), 11 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `HEAD` = `fb109e7` (`gaps.md` con la auditoría de B: PASS, 0 bloqueantes, 0 opcionales).
- `current_target` = `Fase_C`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `3ca990a`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `3ca990a`. Ambos iguales a `Base develop` de
  `verificacion.md`.
- Compuerta antes de tocar nada: exit 0, `61 files already formatted`, `All checks passed!`,
  `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.`, `Total coverage: 96.29%`,
  `596 passed, 5 warnings in 15.20s`. Es la fila B del plan: la fase B no dejó nada roto.

## Archivos tocados

- `tests/test_route_guards.py`: las tres inserciones del plan (`from app.models.user import UserRole` tras
  `from app.main import app`; `ADMIN_ROUTES` entre `PROTECTED_ROUTES` y `PUBLIC_ROUTES`, con una línea en blanco a cada
  lado; `test_admin_route_rejects_tourist` al final). El `git diff` del commit contiene exactamente esas líneas y nada más.
- `tests/test_audit.py`: borrado `test_audit_trail_forbidden_for_tourist` (antes `:50-59`) y las dos líneas en blanco que
  lo seguían. El bloque `# ===…` de "UNIT TESTS" queda a dos líneas en blanco de `test_audit_trail_creation_and_retrieval`.
  `UserRole` sigue en uso en ese archivo (el superadmin del primer test), así que su import no cambia.
- Fin de línea: `git ls-files --eol` → `i/lf w/lf` en los dos.

`git show --stat f980041`:

```text
 tests/test_audit.py        | 12 ------------
 tests/test_route_guards.py | 21 +++++++++++++++++++++
 2 files changed, 21 insertions(+), 12 deletions(-)
```

Incidencia de proceso (sin efecto en el resultado): apliqué el import de `UserRole` en una edición aparte, antes de la del
test. El hook `ruff_on_edit` corrió `ruff check --fix` sobre el archivo en ese estado intermedio y quitó el import por no
usado (F401). Lo volví a añadir después de insertar el test. El diff final es el del plan.

## Mutantes (procedimiento común del plan)

Cada copia va en un directorio nuevo y vacío del scratchpad (`fcx_NOMUT`, `fcx_M1`, `fcx_M2`, `fcx_M3`, `fcx_M4`, `fcx_M5`,
`fcx_M4M5`, `fcx_M6`, `fcx_M7`; comprobé antes que ninguno existía). Se extrajo con
`git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>` (HEAD = `fb109e7`) y encima se copiaron
`tests/test_route_guards.py` y `tests/test_audit.py` desde el árbol de trabajo. `find <dir> -name 'test_*probe*'` → 0 en
las nueve. Las ediciones se aplicaron con un script que vive aparte (`fcx_tools/mutate.py`) y exige el número exacto de
coincidencias de cada sustitución (1, salvo las 7 `Depends(get_current_admin_user)` de M2, las 6 de M3 y las 2 de M6).
`diff -r -q --strip-trailing-cr <copia>/app app` solo muestra el archivo mutado de cada copia (además de los
`__pycache__` del árbol), y los dos tests de cada copia son idénticos a los del árbol. Líneas cambiadas frente a
`HEAD`: M1 1, M2 8, M3 8, M4 1, M5 1 (borrada), M6 2, M7 1. Comando, desde cada `<dir>`:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

| Estado | Resultado (literal) | Esperado por el plan |
|---|---|---|
| Sin mutante | `320 passed, 5 warnings in 10.03s` | 320 passed |
| M1 | `6 failed, 314 passed, 7 warnings in 10.02s` | 6 failed, 314 passed |
| M2 | `9 failed, 311 passed, 7 warnings in 10.88s` | 9 failed, 311 passed |
| M3 | `12 failed, 308 passed, 8 warnings in 10.55s` | 12 failed, 308 passed |
| M4 | `320 passed, 5 warnings in 10.55s` | 320 passed (declarado, R1) |
| M5 | `1 failed, 319 passed, 5 warnings in 11.30s` | 1 failed, 319 passed |
| M4+M5 | `2 failed, 318 passed, 5 warnings in 10.94s` | 2 failed, 318 passed |
| M6 | `4 failed, 316 passed, 6 warnings in 10.75s` | 4 failed, 316 passed |
| M7 | `13 failed, 307 passed, 8 warnings in 11.01s` | 13 failed, 307 passed |

Los warnings de más en M1, M2, M3, M6 y M7 salen de los caminos que el mutante abre (los handlers llegan a ejecutarse); no
son de la suite sin mutante, que da `5 warnings` igual que la compuerta.

`FAILED` literales (sin el sufijo ` - <mensaje>`):

```text
== M1
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/eliminados]
== M2
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PUT /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/activar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/desactivar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[DELETE /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/recuperar]
== M3
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PUT /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/activar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/desactivar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[DELETE /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/recuperar]
== M4
(ninguno)
== M5
FAILED tests/test_audit.py::TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called
== M4M5
FAILED tests/test_audit.py::TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]
== M6
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /usuarios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /usuarios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /usuarios/{cedula}/recuperar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /usuarios/admin]
== M7
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /usuarios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /usuarios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /usuarios/{cedula}/recuperar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /usuarios/admin]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /servicios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PUT /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/activar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/desactivar]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[DELETE /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[PATCH /servicios/{service_id}/recuperar]
```

M7 tumba las 13 rutas admin salvo `[GET /auditoria/]`, y M4+M5 tumba ese caso, como dice el plan.

## Criterio de aceptación

- Tabla de mutantes: las nueve cifras coinciden con el plan (arriba).
- `./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider` → `32 passed in 0.49s`.
- `grep -rn "test_audit_trail_forbidden_for_tourist" tests --include=*.py | wc -l` → `0`.
- `python -m ruff check tests/test_route_guards.py tests/test_audit.py` → `All checks passed!`;
  `ruff format --check` → `2 files already formatted`; `python -m mypy` sobre los dos → `Success: no issues found in 2 source files`.
- Fila C de la compuerta, abajo.

## Compuerta al cerrar (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```text
61 files already formatted
All checks passed!
Success: no issues found in 56 source files
Contracts: 4 kept, 0 broken.
Required test coverage of 92.0% reached. Total coverage: 96.29%
609 passed, 5 warnings in 17.61s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Ratchet: pytest 596 → 609 (+14 casos nuevos, −1 test borrado); cobertura 96,29 % = línea base; contratos 4 kept = línea
base; ruff y mypy sin errores en total ni en lo tocado.

## test-sanitizer (solo checklist)

Sin mocks; usuario y token salen de `persist_user` y `make_auth_headers`; nombres en inglés; se afirma sobre la clave
`detail`, su tipo, el código y la ausencia de cabecera, nunca sobre texto. No se reescribió ningún test.

## Residuales y dudas

- **R1 (declarado en el plan):** M4 sola sigue en `320 passed`; el re-chequeo de `app/services/audit_service.py:65` responde
  el mismo 403. Destino: BE-40.
- Sin dudas. Ninguna desviación de contenido respecto del plan; solo la incidencia de proceso del hook, descrita arriba.

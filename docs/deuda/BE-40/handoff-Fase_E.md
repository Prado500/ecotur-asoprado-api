# Handoff — BE-40 · Fase E (la búsqueda de duplicados, afirmada con sus argumentos)

- Commit de la fase: `9ff32a9` — `test(doubles): assert the duplicate lookup with its arguments`
- Rama: `item/be-40`, sobre `54a4551` (fase E aprobada con E2 en `d49bc9a`).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_E`. `gaps.md`: A–D PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `41ff01d`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `41ff01d`; `Base develop` de `verificacion.md` = `41ff01d`.
- Compuerta antes de tocar nada (exit 0), igual a la fila D del plan: `618 passed, 8 warnings in 17.00s` ·
  `TOTAL 961 19 136 16 96.81%` · `61 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · `Compuerta superada.`

## Qué aplica de E2

E2.1 aprueba la fase E tal como está escrita (sección "Fase E", filas ML1 y ML2, fila E de la compuerta, pasos 13 y 14)
sin correcciones: se ejecutó el texto del cuerpo del plan sin desviaciones. E2.2 (R5 → BE-49 en el backlog) no toca
ninguna fase: no se hizo nada con R5.

## Archivos tocados (el único de la fase)

`git show --stat 9ff32a9`:

```
 tests/test_user_service.py | 12 ++++++++++++
 1 file changed, 12 insertions(+)
```

Cuatro bloques de tres líneas idénticos al de `:113-115`, con los valores del payload de cada test:

1. `test_register_tourist_duplicate_raises_already_exists`: `email="turista@example.com", cedula="1005911792"`, antes de
   `user_repo.create_user.assert_not_called()`.
2. `test_create_administrative_account_provisions_admin`: `email="newadmin@test.com", cedula="5555555555"`, antes de
   `user_repo.create_user.assert_awaited_once_with(created_user)`.
3. `test_create_administrative_account_duplicate_raises_already_exists`: valores de admin, antes de
   `user_repo.create_user.assert_not_awaited()`.
4. `test_create_administrative_account_lookup_failure_writes_nothing`: valores de admin, antes de
   `audit_service.log_transaction.assert_not_awaited()`.

Nada más cambia (nombres, docstrings, imports, otras aserciones). `app/` sin tocar.

## RED (mutantes, procedimiento común, copias desechables del scratchpad)

Una copia nueva por medición (`git archive HEAD | tar -x`); en las de "después" se copió encima
`tests/test_user_service.py` del árbol de trabajo. Cada mutante se comprobó con `sed -n '75p;395p'` y con
`diff -r --strip-trailing-cr` contra `app/` del árbol de trabajo: solo cambia la línea del mutante.

| Mutante | Antes de E (estado D) | Después de E |
|---|---|---|
| Control | `329 passed, 8 warnings` | `329 passed, 8 warnings` |
| ML1 (`user_service.py:75`) | `1 failed, 328 passed` | `2 failed, 327 passed` |
| ML2 (`user_service.py:395`) | `329 passed` (sobrevive) | `3 failed, 326 passed` |

```
== pre_ml1
FAILED tests/test_user_service.py::test_register_tourist_returns_registration_result
1 failed, 328 passed, 8 warnings in 15.37s
== pre_ml2
329 passed, 8 warnings in 15.07s
== post_ml1
FAILED tests/test_user_service.py::test_register_tourist_returns_registration_result
FAILED tests/test_user_service.py::test_register_tourist_duplicate_raises_already_exists
2 failed, 327 passed, 8 warnings in 12.46s
== post_ml2
FAILED tests/test_user_service.py::test_create_administrative_account_provisions_admin
FAILED tests/test_user_service.py::test_create_administrative_account_duplicate_raises_already_exists
FAILED tests/test_user_service.py::test_create_administrative_account_lookup_failure_writes_nothing
3 failed, 326 passed, 8 warnings in 11.86s
```

Resto de mutantes re-medidos sobre el estado E (iguales al estado D):

```
== post_m4
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /auditoria/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /auditoria/]
2 failed, 327 passed, 8 warnings in 11.23s
== post_ms1
FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
2 failed, 327 passed, 9 warnings in 11.56s
== post_ms2
FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
2 failed, 327 passed, 9 warnings in 12.01s
== post_ms3
FAILED tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[POST /usuarios/admin]
FAILED tests/test_route_guards.py::test_superadmin_route_rejects_admin[POST /usuarios/admin]
3 failed, 326 passed, 10 warnings in 11.94s
```

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py`, exit 0:

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

- `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.`
- `TOTAL 961 19 136 16 96.81%` · `Required test coverage of 92.0% reached. Total coverage: 96.81%` ·
  `618 passed, 8 warnings in 22.30s`. Igual a la fila E del plan (618 passed, 96,81 %).
- Archivo tocado: `ruff check tests/test_user_service.py` → `All checks passed!`; `mypy tests/test_user_service.py` →
  `Success: no issues found in 1 source file`.

## Verificación final

- Paso 13: `git diff --numstat 09ec81b HEAD -- app tests alembic conftest.py` → `12	0	tests/test_user_service.py`;
  `grep -c "get_user_by_email_or_cedula.assert_awaited_once_with"` → `5`; `newadmin…5555555555` → `3`;
  `turista…1005911792` → `2`.
- Paso 14: ML1 `2 failed, 327 passed`, ML2 `3 failed, 326 passed`, con los tests de la tabla (ver arriba).
- Pasos 1-10 repetidos sobre el estado E, sin cambios: `11`, `0`, `0`, `0`, `0`, `6`, `2`, `4`, `0`, `13`, `0`, `3`, `7`, `0`,
  `42:    ProtectedRoute("POST", "/usuarios/admin", "superadmin", _EMPTY_BODY),`, `17`, `1`, `13`, `3`,
  `tests/test_audit.py:0` / `tests/test_user_service.py:0`, `46 passed`. Paso 11: la compuerta de arriba. Paso 12: M4,
  MS1, MS2 y MS3 de arriba.

## Residuales y dudas

- Ninguna desviación del plan. R5 sigue fuera (BE-49, E2.2).
- Nota menor: la diferencia de `app/api/__init__.py` entre `git archive` y el árbol de trabajo es solo de fin de línea
  (desaparece con `--strip-trailing-cr`); no afecta a ninguna medición.
- Los warnings de MS1–MS3 (9 y 10 en vez de 8) solo aparecen en las copias mutadas.
- E es la última fase: `current_target` pasa a `null`.

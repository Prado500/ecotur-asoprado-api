# Handoff — BE-15 Fase E: regresiones de B2 y B3 por HTTP

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `84ad522`
  (`test(access-policy): freeze B2 self-promotion and B3 third-party delete`; cuerpo idéntico al bloque del plan,
  comprobado con `diff` sobre `git log -1 --format=%B` sin el trailer → `MSG IDENTICAL`)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` vacío; HEAD `e9904f9`; `current_target` = `Fase_E`. Compuerta de arranque igual a
  la fila D: 381 passed, 94.81 %, 4 KEPT, ruff 56 (tests/ 3), mypy 10.

## Archivos tocados

Solo el que el plan asigna a la fase E (`git show --stat 84ad522`):

```
 tests/test_user_access_policy.py | 227 ++++++++++++++++++++++++++++++++++++++-
 1 file changed, 225 insertions(+), 2 deletions(-)
```

- Las dos docstrings E501 se acortan al texto literal del plan: l.347 → `"""Admin provisioning an admin account yields
  403 and persists nothing."""`; l.395 → `"""Admin promoting a tourist to superadmin yields 403 with no mutation."""`.
- Imports añadidos: `from datetime import UTC, datetime` y `from app.models.audit import AuditAction, AuditLog`. El
  `from sqlalchemy.future import select` de l.13 no se toca (fuera de alcance).
- Los 10 tests nuevos van al final de la sección B (integración), antes de la sección C, en dos sub-bloques
  comentados (`B2 regression` / `B3 regression`). Sin fábricas nuevas; `conftest.py`, `app/` intactos.
  Finales de línea: `git ls-files --eol` → `i/lf w/lf`.

## Tests añadidos (10 definiciones, 11 casos)

`grep -cE "^async def test_b[23]_" tests/test_user_access_policy.py` → `10`. Todos con `persist_user` +
`make_auth_headers`; estado por `db_session.refresh`; auditoría por `select(AuditLog)`.

| # | Test | Petición | Afirma |
|---|---|---|---|
| 1 | `test_b2_admin_self_promotion_to_superadmin_returns_403_without_mutation` | PATCH propia cédula `{"role": "superadmin"}` | 403; `set(body) == {"detail"}`, `detail` str; `refresh` → `role == admin`; `AuditLog` vacío |
| 2 | `test_b2_admin_self_demotion_to_tourist_returns_403` | `{"role": "tourist"}` | 403; `set(body) == {"detail"}`; rol sigue `admin` |
| 3 | `test_b2_admin_self_update_without_role_returns_200` | `{"first_name": "Changed"}` | 200; `body["first_name"] == "Changed"`, `body["cedula"] == admin.cedula`; `refresh` → `first_name == "Changed"`, `role == admin` |
| 4 | `test_b2_admin_self_role_noop_returns_403` | `{"role": "admin"}` | 403; `set(body) == {"detail"}`; rol sigue `admin` (se bloquea la clave, no el valor) |
| 5 | `test_b2_admin_self_promotion_with_profile_fields_mutates_nothing` | `{"role": "superadmin", "first_name": "Changed"}` | 403; `set(body) == {"detail"}`; `first_name == "John"` y `role == admin` |
| 6 | `test_b3_superadmin_deletes_third_party_account[admin]` / `[tourist]` | DELETE de un tercero | 200; `set(body) == {"success", "message"}`, `success is True`, `message` str; `refresh` → `deleted_at is not None`, `is_active is False`; una sola fila `AuditLog` con `entity_id == target.cedula`, `action == AuditAction.SOFT_DELETE`, `performed_by == superadmin.cedula` |
| 7 | `test_b3_superadmin_deleting_peer_superadmin_returns_403_without_mutation` | DELETE de otro superadmin | 403; `set(body) == {"detail"}`; `deleted_at is None`, `is_active is True` |
| 8 | `test_b3_admin_deleting_peer_admin_returns_403_without_mutation` | admin borra a otro admin | 403; `set(body) == {"detail"}`; `deleted_at is None`, `is_active is True` |
| 9 | `test_b3_superadmin_deleting_already_deleted_account_returns_404` | objetivo con `deleted_at=datetime.now(UTC), is_active=False` | 404; `set(body) == {"detail"}`, `detail` str; `AuditLog` vacío |
| 10 | `test_b3_superadmin_deleting_missing_cedula_returns_404` | `/usuarios/9999999999` | 404; `set(body) == {"detail"}`, `detail` str |

Ninguna aserción sobre texto en español. La parametrización de 6 usa `ids=["admin", "tourist"]`.

## RED sustituido por prueba de sensibilidad con mutantes (sin editar `app/`)

Plugin en el scratchpad, fuera del repo:
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\b26168e9-94c0-4f60-87ec-a1857cacccf0\scratchpad\e_be15_mutants.py`.
Un fixture `autouse` que, con `monkeypatch.setattr` sobre la clase, sustituye `UserAccessPolicy.assert_can_update`
por una función que no hace nada y `UserAccessPolicy.assert_can_delete` por una que lanza `AuthorizationError()`.

Comando: `PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -p e_be15_mutants -p no:cacheprovider
tests/test_user_access_policy.py -k "b2_ or b3_" -q -rpf --tb=no`. Salida literal:

```
FF.FFFF....                                                              [100%]
=========================== short test summary info ===========================
PASSED tests/test_user_access_policy.py::test_b2_admin_self_update_without_role_returns_200
PASSED tests/test_user_access_policy.py::test_b3_superadmin_deleting_peer_superadmin_returns_403_without_mutation
PASSED tests/test_user_access_policy.py::test_b3_admin_deleting_peer_admin_returns_403_without_mutation
PASSED tests/test_user_access_policy.py::test_b3_superadmin_deleting_already_deleted_account_returns_404
PASSED tests/test_user_access_policy.py::test_b3_superadmin_deleting_missing_cedula_returns_404
FAILED tests/test_user_access_policy.py::test_b2_admin_self_promotion_to_superadmin_returns_403_without_mutation
FAILED tests/test_user_access_policy.py::test_b2_admin_self_demotion_to_tourist_returns_403
FAILED tests/test_user_access_policy.py::test_b2_admin_self_role_noop_returns_403
FAILED tests/test_user_access_policy.py::test_b2_admin_self_promotion_with_profile_fields_mutates_nothing
FAILED tests/test_user_access_policy.py::test_b3_superadmin_deletes_third_party_account[admin]
FAILED tests/test_user_access_policy.py::test_b3_superadmin_deletes_third_party_account[tourist]
6 failed, 5 passed, 46 deselected in 0.23s
```

Exactamente lo que exige el plan: fallan 1, 2, 4, 5 y los dos casos de 6; pasan 3, 7, 8, 9 y 10. Sin el plugin:
`11 passed, 46 deselected in 0.23s`. `git hash-object app/services/user_access_policy.py` antes y después de la
corrida: `eea566b2a738caaeda2d5472937a5c839867b98c` (sin cambio).

## Salvaguarda E (decisión bloqueada 9)

Antes del commit, salida literal:

```
$ test "$(git hash-object app/services/user_access_policy.py)" = "$(git rev-parse HEAD:app/services/user_access_policy.py)" && echo IGUAL
IGUAL
$ git status --short app/
(vacío)
```

Repetida tras el commit `84ad522`: `IGUAL` y `git status --short app/` vacío.

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Bloque RESUMEN literal:

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

Cifras literales de la misma corrida:

```
Found 54 errors.
Found 10 errors in 5 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        942     34    136     22  94.81%
Required test coverage of 92.0% reached. Total coverage: 94.81%
392 passed, 5 warnings in 13.55s
```

| | Fila "Fase E" del plan | Real |
|---|---|---|
| pytest passed | 392 | 392 |
| ruff total | 54 | 54 |
| ruff en `tests/` | 1 | 1 (`tests\test_user_service.py:3:1` I001, heredado) |
| mypy | 10 | 10 (todos en `app/`) |
| cobertura | ≥ 94.81 % | 94.81 % |
| import-linter | 4 KEPT | 4 kept, 0 broken |

Archivo tocado: `ruff check tests/test_user_access_policy.py` → `All checks passed!`; `ruff format --check` →
`1 file already formatted`; `mypy tests/test_user_access_policy.py` → 0 errores en `tests/` (los 10 que imprime
son los heredados de `app/` que sigue por import). El rojo de ruff y mypy es la deuda heredada de la línea base
(ADR-0005); ninguno de sus errores está en código de esta fase.

## Checklist `test-sanitizer` ("Ecotur Enterprise Test Standards")

1. Mocks: la fase no añade ninguno. 2. Preparación: solo `persist_user` y `make_auth_headers`. 3. Nombres,
variables y docstrings en inglés. 4. Contrato `{"detail": ...}` (nunca `"detalle"`). 5. Bordes ABAC: auto-promoción,
auto-degradación, rol sin cambio, rol mezclado con perfil, pares del mismo rango, 404 antes de 403.

## Desviaciones y dudas

- **Nombre del plugin:** el plan dice `be15_mutants.py`; usé `e_be15_mutants.py` (y `-p e_be15_mutants`) porque el
  scratchpad es compartido y el lanzador pidió un prefijo propio. El contenido es el que describe el plan.
- **Aserciones por encima del mínimo del plan** (todas se cumplen con el código real y no cambian el resultado
  `6 failed, 5 passed`, porque los casos que fallan con el mutante fallan ya en el código HTTP): `isinstance(detail,
  str)` en 1, 9 y 10; `set(body) == {"detail"}` en 2, 4, 5, 7 y 8; rol sin cambio en 4; `is_active is True` en 7 y
  8; `body["cedula"]` en 3; `isinstance(message, str)` en 6. Razón: AGENTS §5 (código HTTP **y** estructura **y**
  estado). El `AuditLog` vacío de 1 y 9 no es desviación: lo pide el plan.
- `-rpf --tb=no` en la corrida de mutantes solo para listar qué pasa y qué falla; la cifra es la misma que con `-q`
  a secas (comprobado: `6 failed, 5 passed, 46 deselected in 0.45s`).
- Sin dudas abiertas.

## Residuales

- Los de la tabla del plan siguen igual (I001 de `test_user_service.py:3`, `sqlalchemy.future` en
  `test_user_access_policy.py:13` y `test_services.py:14`, 10 aserciones de mock sin argumentos, duplicados HTTP
  entre `test_auth.py` y `test_user_access_policy.py`).
- Ruff (53 en `app/`) y mypy (10 en `app/`): heredados, no tocados.

# Handoff — BE-15 Fase D-bis: las cuatro aserciones conservadas de `test_auth.py`, a la decisión 4 (enmienda E3)

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `c8743ed`
  (`test(auth): raise four kept RBAC assertions to the decision 4 form`; cuerpo idéntico al bloque del plan,
  comprobado con `diff` sobre `git log -1 --format=%B` sin el trailer → `MSG IDENTICAL`)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` vacío; HEAD `f9b850c`; `current_target` = `Fase_D_bis`.
  `git diff --stat 9e2700f HEAD -- tests/test_auth.py` → vacío (las líneas del plan siguen valiendo).
  Compuerta de arranque igual a la fila E: 392 passed, 94.81 %, 4 KEPT, ruff 54 (tests/ 1), mypy 10.

## Archivos tocados

Solo el que el plan asigna a la fase (`git show --stat c8743ed`):

```
 tests/test_auth.py | 24 ++++++++++++++++++++----
 1 file changed, 20 insertions(+), 4 deletions(-)
```

Antes del commit: `git diff --stat HEAD` → solo `tests/test_auth.py`; `git status --short app/` → vacío.
Finales de línea: `git ls-files --eol tests/test_auth.py` → `i/lf w/lf`. Sin imports nuevos (`select`, `User` y
`UserRole` ya estaban), sin cambios de nombre ni de docstring, 0 tests nuevos.

## Los cuatro cambios (líneas de HEAD `9e2700f`)

| # | Test | Antes | Después |
|---|---|---|---|
| 1 | `test_tourist_self_role_escalation_returns_403_without_mutation` (l.213) | `assert "detail" in response.json()` | `body = response.json()`; `set(body) == {"detail"}`; `isinstance(body["detail"], str)` |
| 2 | `test_tourist_self_is_active_change_returns_403_without_mutation` (l.232) | igual que 1 | igual que 1 |
| 3 | `test_admin_recovers_tourist_as_inactive` (l.324-325) | 200 y `response.json()["success"] is True` | 200; `body = response.json()`; `{"success", "message"} <= set(body)`; `body["success"] is True`; `isinstance(body["message"], str)`. No se afirman `cc`/`correo`/`nombre`/`apellido` (P2, E3) |
| 4 | `test_superadmin_provisions_admin_account` (l.404-408) | solo la respuesta | recibe `db_session`; se conservan las 3 aserciones de respuesta y se añade el bloque literal del plan: `select(User).where(User.cedula == "555555")` → `scalar_one()` → `refresh` → `role == UserRole.admin`, `is_active is True`, `deleted_at is None` |

La firma del test 4 pasó a 3 líneas por `ruff format` (100 columnas); es el único efecto del hook.

## RED: mutación de auditoría (sin editar `app/` ni el repo)

Plugin `C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\b26168e9-94c0-4f60-87ec-a1857cacccf0\scratchpad\dbis_mutants.py`,
copia literal del bloque del plan (el hook de formato lo reformateó al guardarlo: solo espacios y saltos de línea).
Comando por mutante:
`DBIS_MUTANT=<m> PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -rf -p no:cacheprovider -p
dbis_mutants tests/test_auth.py -k "tourist_self_role_escalation or tourist_self_is_active_change or
admin_recovers_tourist or superadmin_provisions_admin"`, filtrado a las líneas `FAILED` y de resumen.

**Antes de editar** (`git hash-object tests/test_auth.py` = `0a33509a646a723ad8d4089fd9b4019e1e349843`), salida literal:

```
=== DBIS_MUTANT=(vacio)
4 passed, 15 deselected in 0.28s
=== DBIS_MUTANT=extra_key_403
4 passed, 15 deselected in 0.28s
=== DBIS_MUTANT=detail_not_str_403
4 passed, 15 deselected in 0.28s
=== DBIS_MUTANT=recover_no_message
4 passed, 15 deselected in 0.29s
=== DBIS_MUTANT=recover_message_not_str
4 passed, 15 deselected in 0.29s
=== DBIS_MUTANT=row_role
4 passed, 15 deselected in 0.29s
=== DBIS_MUTANT=row_is_active
4 passed, 15 deselected in 0.30s
=== DBIS_MUTANT=row_deleted_at
4 passed, 15 deselected in 0.29s
```

**Después de editar**, salida literal:

```
=== DBIS_MUTANT=(vacio)
4 passed, 15 deselected in 0.34s
=== DBIS_MUTANT=extra_key_403
FAILED tests/test_auth.py::test_tourist_self_role_escalation_returns_403_without_mutation
FAILED tests/test_auth.py::test_tourist_self_is_active_change_returns_403_without_mutation
2 failed, 2 passed, 15 deselected in 0.50s
=== DBIS_MUTANT=detail_not_str_403
FAILED tests/test_auth.py::test_tourist_self_role_escalation_returns_403_without_mutation
FAILED tests/test_auth.py::test_tourist_self_is_active_change_returns_403_without_mutation
2 failed, 2 passed, 15 deselected in 0.54s
=== DBIS_MUTANT=recover_no_message
FAILED tests/test_auth.py::test_admin_recovers_tourist_as_inactive - Assertio...
1 failed, 3 passed, 15 deselected in 0.42s
=== DBIS_MUTANT=recover_message_not_str
FAILED tests/test_auth.py::test_admin_recovers_tourist_as_inactive - assert F...
1 failed, 3 passed, 15 deselected in 0.46s
=== DBIS_MUTANT=row_role
FAILED tests/test_auth.py::test_superadmin_provisions_admin_account - Asserti...
1 failed, 3 passed, 15 deselected in 0.44s
=== DBIS_MUTANT=row_is_active
FAILED tests/test_auth.py::test_superadmin_provisions_admin_account - assert ...
1 failed, 3 passed, 15 deselected in 0.47s
=== DBIS_MUTANT=row_deleted_at
FAILED tests/test_auth.py::test_superadmin_provisions_admin_account - assert ...
1 failed, 3 passed, 15 deselected in 0.49s
```

Aserción que cae en cada mutante (misma corrida con `--tb=line`, salida literal):

```
=== extra_key_403
C:\projects\ecotur-asoprado\tests\test_auth.py:214: AssertionError: assert {'code', 'detail'} == {'detail'}
C:\projects\ecotur-asoprado\tests\test_auth.py:235: AssertionError: assert {'code', 'detail'} == {'detail'}
=== detail_not_str_403
C:\projects\ecotur-asoprado\tests\test_auth.py:215: AssertionError: assert False
C:\projects\ecotur-asoprado\tests\test_auth.py:236: AssertionError: assert False
=== recover_no_message
C:\projects\ecotur-asoprado\tests\test_auth.py:330: AssertionError: assert {'message', 'success'} <= {'apellido', ...e', 'success'}
=== recover_message_not_str
C:\projects\ecotur-asoprado\tests\test_auth.py:332: assert False
=== row_role
C:\projects\ecotur-asoprado\tests\test_auth.py:423: AssertionError: assert <UserRole.tourist: 'tourist'> == <UserRole.admin: 'admin'>
=== row_is_active
C:\projects\ecotur-asoprado\tests\test_auth.py:424: assert False is True
=== row_deleted_at
C:\projects\ecotur-asoprado\tests\test_auth.py:425: assert datetime.datetime(2026, 11, 4, 23, 25, 48, 527530) is None
```

| `DBIS_MUTANT` | Antes | Después | Test que cae (línea nueva) | Plan |
|---|---|---|---|---|
| (vacío) | `4 passed` | `4 passed` | — | igual |
| `extra_key_403` | `4 passed` | `2 failed, 2 passed` | 1 y 2 (`set(body)`, l.214 / l.235) | igual |
| `detail_not_str_403` | `4 passed` | `2 failed, 2 passed` | 1 y 2 (`isinstance`, l.215 / l.236) | igual |
| `recover_no_message` | `4 passed` | `1 failed, 3 passed` | 3 (forma, l.330) | igual |
| `recover_message_not_str` | `4 passed` | `1 failed, 3 passed` | 3 (`message` str, l.332) | igual |
| `row_role` | `4 passed` | `1 failed, 3 passed` | 4 (`role`, l.423) | igual |
| `row_is_active` | `4 passed` | `1 failed, 3 passed` | 4 (`is_active`, l.424) | igual |
| `row_deleted_at` | `4 passed` | `1 failed, 3 passed` | 4 (`deleted_at`, l.425) | igual |

Tras las corridas, `git status --short` solo mostraba `tests/test_auth.py` (la edición de la fase); `app/` vacío.

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
Required test coverage of 92.0% reached. Total coverage: 94.81%
392 passed, 5 warnings in 14.80s
```

| | Fila "Fase D-bis" del plan | Real |
|---|---|---|
| pytest passed | 392 | 392 |
| ruff total | 54 | 54 |
| ruff en `tests/` | 1 | 1 (`Found 1 error.`, el I001 heredado de `test_user_service.py:3`) |
| ruff en `tests/test_auth.py` | 0 | `All checks passed!`; `ruff format --check` → `1 file already formatted` |
| mypy | 10 | 10 (todos en `app/`) |
| cobertura | ≥ 94.81 % | 94.81 % |
| import-linter | 4 KEPT | 4 kept, 0 broken |

`mypy tests/test_auth.py` → `Found 3 errors in 2 files`, los tres en `app/db/database.py:11` y
`app/core/security.py:71,87` (heredados, seguidos por import; `tests/` no está en `files` de mypy). 0 en el test.

Criterio de aceptación, salida literal de los greps:

```
grep -c 'assert "detail" in response.json()' tests/test_auth.py            → 0
grep -c 'set(body) == {"detail"}' tests/test_auth.py                       → 9
grep -c '{"success", "message"} <= set(body)' tests/test_auth.py           → 1
grep -c 'select(User).where(User.cedula == "555555")' tests/test_auth.py   → 1
pytest --collect-only -q tests/test_auth.py | tail -1                      → 19 tests collected in 0.01s
```

Los nombres de test no cambian: en `git diff` solo aparece la línea `def` de `test_superadmin_provisions_admin_account`,
reformateada por el parámetro nuevo, con el mismo nombre.

## Checklist `test-sanitizer` ("Ecotur Enterprise Test Standards")

1. Mocks: la fase no añade ninguno. 2. Preparación: sin cambios, siguen `persist_user` y `make_auth_headers`.
3. Aserciones de código HTTP, estructura (`set(body)`), tipo y estado en BD (`refresh`); nada sobre texto en español.
4. Contrato `{"detail": ...}`. 5. La relectura con `select` + `refresh` sirve con la sesión compartida y con la de F.

## Desviaciones y dudas

- **`-rf` y filtro de salida:** las corridas de mutantes usan `-rf` (lo pide el plan) y se filtran con
  `grep -E "^(FAILED|ERROR)|passed|failed|error"` para pegar solo el resumen. La cifra es la de pytest sin tocar.
- **Corrida extra con `--tb=line`** (después de editar) para dejar constancia de la aserción concreta que cae; no
  la pide el plan.
- **Plugin reformateado por el hook** al guardarlo en el scratchpad: el contenido lógico es el del plan.
- Sin dudas abiertas.

## Residuales

- Los de la tabla del plan siguen igual (I001 de `test_user_service.py:3`, `sqlalchemy.future` en
  `test_user_access_policy.py:13` y `test_services.py:14`, 10 aserciones de mock sin argumentos, duplicados HTTP
  entre `test_auth.py` y `test_user_access_policy.py`, claves en español de la recuperación → P2).
- Ruff (53 en `app/`) y mypy (10 en `app/`): heredados, no tocados.

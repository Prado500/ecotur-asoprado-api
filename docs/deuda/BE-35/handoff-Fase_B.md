# Handoff — BE-35 · Fase B (dos guardas en `UserAccessPolicy`, docstrings y tests)

- Commit de la fase: `84eef92` — `fix(access-policy): block superadmin self-deletion and self-deactivation` (mensaje
  exacto del plan, trailer `Co-Authored-By` incluido; `diff` del bloque "Commit" de la fase B, plan l. 349-380 sin la
  sangría, contra `git log -1 --format=%B 84eef92`: solo difiere la línea en blanco final que añade `%B`).
- Rama: `item/be-35`, sobre `474d075` (auditoría de la fase A, PASS).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E0.2 (docstrings de clase de los tests, 95 y 94 columnas, aplicados tal cual), E0.3 (riesgo c
  cerrado; confirmado aquí por el RED, abajo), E0.4 (M6 vivo), E0.5 (cifras recalculadas; aquí medidas).

## Ritual de arranque

- `git status --short`: limpio. HEAD `474d075`. `current_target` = `Fase_B`. `gaps.md` existe: Fase A PASS, sin
  bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `87b9905`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `87b9905`; `Base develop` de `verificacion.md` = `87b9905`.
- Compuerta antes de tocar nada (exit 0), igual a la línea base:
  `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `691 passed, 8 warnings in 27.63s` · `TOTAL 1034 15 148 13 97.63%`.

## Archivos tocados (los cuatro de la fase)

`git show --stat --format= 84eef92`:

```
 app/api/routers/user.py            |   3 +-
 app/services/user_access_policy.py |  28 ++++-
 app/services/user_service.py       |  16 +--
 tests/test_user_access_policy.py   | 223 ++++++++++++++++++++++++++++++++++++-
 4 files changed, 252 insertions(+), 18 deletions(-)
```

`git show --numstat --format= 84eef92`: `2 1 routers/user.py` · `22 6 user_access_policy.py` · `9 7 user_service.py` ·
`219 4 tests/test_user_access_policy.py`. En `user_service.py` y `routers/user.py` solo cambian docstrings y el
comentario de paso 2 (lógica intacta). Las dos guardas y los textos de `app/` son los dictados en el plan.

## RED (tests escritos y ejecutados antes de tocar `app/`)

`./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be35 -q -p no:cacheprovider`:

```
FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
11 failed, 6 passed, 66 deselected in 0.88s
```

Coincide con el plan: fallan U1, U2, U4, U6, H1, H2, H3 (x3), H4, H5; pasan U3, U5, U7, U8, H6, H7. Los unitarios fallan
con `Failed: DID NOT RAISE <class 'app.core.exceptions.AuthorizationError'>`. Riesgo (c): `coerced-false` falla con
`assert 200 == 403` (200, no 422): pydantic convierte `"false"` en `False`, como dice E0.3.

## GREEN

Mismo comando tras las guardas: `17 passed, 66 deselected in 0.31s`.

## Compuerta completa tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1038     15    152     13  97.65%
Required test coverage of 92.0% reached. Total coverage: 97.65%
707 passed, 8 warnings in 27.32s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest 691 → 707 (691 − 1 sustituido + 17), como el plan. Cobertura 97,63 % → 97,65 % (≥ línea base).
  `user_access_policy.py` no aparece en la tabla de faltantes (`30 files skipped due to complete coverage`): sigue al 100 %.
- Sobre los cuatro archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already
  formatted`; `mypy` → `Success: no issues found in 4 source files`.
- Totales ruff 0 / mypy 0 (63 archivos) / 4 kept: iguales a la línea base.

## Verificación final del plan (comandos 1–11, salida medida)

1. `is_self_deletion|"is_active" in update_dict` → 4 líneas, todas en `user_access_policy.py` (:38, :41, :47, :84). OK.
2. `update_dict.get("is_active") is False` → 1 línea (`user_access_policy.py:93`). OK.
3. `count_active_superadmins` → 2 líneas (`user_repository.py:23`, `superadmin_bootstrap.py:42`). OK.
4. `test_superadmin_self_delete_is_allowed` → 0 líneas, exit 1. OK.
5. `self-deletion|act on their own account|parity` en `app` → 0 líneas, exit 1. OK.
6. `HTTP_409` → 1 línea (`app/main.py:107`). OK.
7. `json=\{"is_active": False\}` en `tests` → 4 líneas: `test_auth.py:248` y `test_user_access_policy.py:867, :887, :934`
   (H4, H5, H7). OK.
8. `ADR-0017` en `app` → 7 líneas: `routers/user.py:135`; `user_access_policy.py:14, :27, :56`; `user_service.py:183,
   :205, :259`. OK.
9. `superadministrador no puede` → 2 líneas (`user_access_policy.py:48, :95`). OK.
10. `git diff --stat 300e294 HEAD -- app/core app/main.py app/repositories app/schemas app/api/dependencies.py
    tests/test_user_service.py tests/test_route_guards.py tests/test_auth.py` → salida vacía. OK.
11. `git grep -c 'def test_be35_'` → `tests/test_user_access_policy.py:15`; `-k be35` → `17 passed`. OK.
12. Compuerta: arriba.

## Mutantes (sobre una copia de `app/`, `tests/`, `conftest.py` y `pyproject.toml` en el scratchpad, no en el repo)

Se comprobó antes que la copia importa su propio `app/` (`m.__file__` dentro de la copia). Cada mutante corre
`tests/test_user_access_policy.py` completo; M6, la suite entera.

| Mutante | Resultado | Lo matan |
|---|---|---|
| M1 sin rol en la guarda de borrado | muerto (2 failed) | `test_self_delete_tourist_is_allowed`, `test_be35_admin_self_delete_is_still_allowed` |
| M2 `actor is target` en borrado | muerto (1) | `test_be35_self_delete_guard_identifies_the_actor_by_cedula` |
| M3 `"is_active" in update_dict` | muerto (2) | U5 `..._is_active_true_is_allowed` y H6 `..._is_active_true_returns_200` |
| M4 sin `is_self_update` | muerto (2) | U8 `..._can_deactivate_lower_rank_account` y H7 `..._deactivates_lower_rank_account_returns_200` |
| M5 sin rol en la guarda de `is_active` | muerto (1) | U7 `test_be35_admin_self_deactivation_is_still_allowed` |
| M6 `not update_dict.get("is_active", True)` | **vivo** (declarado) | ninguno |
| M7 `actor is target` en `is_active` | muerto (1) | U6 `..._self_deactivation_guard_identifies_the_actor_by_cedula` |
| M8 sin guarda de borrado | muerto (5) | U1, U2, H1, H2, H5 |
| M9 sin guarda de `is_active` | muerto (7) | U4, U6, H3 (x3), H4, H5 |

M6: la primera pasada con `tests` completo dio `2 errors` de colección (`test_check.py` y `test_check_docs.py` importan
`scripts/`, ausente en la copia), no un fallo real. Repetida con esos dos módulos excluidos: control sin mutar
`5 failed, 411 passed, 8 warnings, 2 errors` y M6 `5 failed, 411 passed, 8 warnings, 2 errors`; resultado idéntico
(los 5 fallos y 2 errores salen de `.env.example` y `alembic/`, que tampoco están en la copia: `test_config.py` x4,
`test_token_failure_paths.py` x1, `test_email_case.py` x2 errores). M6 sobrevive, como declara el plan (R2, BE-37).

## Checklist `test-sanitizer` (solo "Ecotur Enterprise Test Standards")

1. Mocks: ninguno nuevo. 2. Fábricas: `make_user`, `persist_user`, `make_auth_headers`; ningún usuario ni token a mano.
3. Nombres y variables en inglés. 4. Contrato: `set(body) == {"detail"}` e `isinstance(body["detail"], str)`; ninguna
aserción sobre texto en español. 5. ABAC: rechazo con uno y con dos superadmins, gemelo por cédula, `"false"`
convertido, campos de perfil mezclados, acceso conservado y bordes que deben seguir pasando. `refresh` tras cada
petición (ADR-0011). No se reescribió ningún test que ya cumpliera.

## Desviaciones respecto al plan

Ninguna en código, textos, cifras ni conteos. Detalles de forma, dentro de lo que el plan deja libre:
- H2 hace `refresh` también de `peer` antes de afirmar `peer.is_active is True` (ADR-0011, regla 2).
- H5 añade, tras las tres peticiones, `refresh` del actor y `deleted_at is None` / `is_active is True`.

## Residuales

- R1 (cliente Flutter sin verificar), R2 (M6 vivo, medido arriba), R3 (baja por SQL sin procedimiento ni auditoría) y
  R4 (AGENTS/CONTEXT al cierre): los del plan, sin cambios. Destino: sesión Mentor al cierre.
- Ninguno nuevo. No se tocó ningún archivo fuera de los cuatro de la fase.

# Handoff — BE-15 Fase B: `test_services.py` y `test_audit.py` sobre las fábricas centrales

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `fc06d1e`
  (`test(fixtures): move services and audit setup to central factories`, mensaje exacto del plan)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` solo mostraba `?? docs/deuda/BE-15/gaps.md` (auditoría de la fase A, la commitea
  David; no se tocó ni se añadió a ningún commit). `current_target` = `Fase_B`.

## Archivos tocados

Solo los dos que el plan asigna a la fase B (`git show --stat fc06d1e`):

```
 tests/test_audit.py    |  52 +++++++------------------
 tests/test_services.py | 104 +++++++++++++++++--------------------------------
 2 files changed, 48 insertions(+), 108 deletions(-)
```

- `tests/test_services.py`: borrados `admin_token` y `auth_headers`. `admin_headers` (`persist_user` +
  `make_auth_headers`, sin cambios en su cuerpo) se movió al bloque "TEST FIXTURES" (ahora l.33-38). Los 13 tests
  (`test_deactivate_and_activate_package` … `test_update_package_concurrent_reconciliation`) reciben y usan
  `admin_headers`. Fuera los imports sin uso: `create_access_token`, `get_password_hash` y `User` (se queda
  `UserRole`).
- `tests/test_audit.py`: borrado `superadmin_token`. `test_audit_trail_creation_and_retrieval(client, persist_user,
  make_auth_headers)` crea `superadmin = await persist_user(role=UserRole.superadmin)` y `headers =
  make_auth_headers(superadmin)`. `test_audit_trail_forbidden_for_tourist(client, persist_user, make_auth_headers)`
  crea `tourist = await persist_user(role=UserRole.tourist)`, usa `make_auth_headers(tourist)` y además del 403
  comprueba `isinstance(response.json()["detail"], str)`. Fuera `User`, `get_password_hash` y
  `create_access_token`; `ruff check --fix` corrigió el I001 de la l.1 (orden de imports).
- No se creó ninguna fábrica nueva.

## Red de seguridad: `--collect-only` idéntico (refactor sin RED)

`./venv/Scripts/python.exe -m pytest --collect-only -q -p no:cacheprovider tests/test_services.py tests/test_audit.py`

- Antes (HEAD `68cf40c`): `42 tests collected in 0.02s`
- Después: `42 tests collected in 0.07s`
- `diff` de las dos listas de IDs → sin salida, exit 0. `sha256` de las líneas con `::` en ambas:
  `325d3bda95f3af090dae831f492518ae614bebd339da4de3b320fea63bcfcb1c` (igual antes y después).

Lista de IDs (igual antes y después):

```
tests/test_services.py::test_deactivate_and_activate_package
tests/test_services.py::test_soft_delete_and_recover
tests/test_services.py::test_update_package_details
tests/test_services.py::test_upload_images_staging_endpoint
tests/test_services.py::test_upload_images_ceiling_limit_rejection
tests/test_services.py::test_upload_images_storage_outage_returns_503
tests/test_services.py::test_toggle_nonexistent_package_returns_404
tests/test_services.py::test_soft_delete_nonexistent_package_returns_404
tests/test_services.py::test_update_nonexistent_package_returns_404
tests/test_services.py::test_recover_package_not_in_trash_returns_400
tests/test_services.py::test_recover_nonexistent_package_returns_400
tests/test_services.py::test_update_package_image_ceiling_limit_rejection
tests/test_services.py::test_update_package_concurrent_reconciliation
tests/test_services.py::test_create_package_rejects_foreign_url
tests/test_services.py::test_create_package_rejects_permanent_url
tests/test_services.py::test_create_package_missing_temporal_blob_returns_400
tests/test_services.py::test_create_package_promotion_outage_returns_503
tests/test_services.py::test_create_package_promotes_temporal_url
tests/test_services.py::test_upload_images_non_image_returns_415
tests/test_services.py::test_update_package_rejects_foreign_url_without_side_effects[https://evil.example/temp-ecotur-images/x.jpg]
tests/test_services.py::test_update_package_rejects_foreign_url_without_side_effects[https://s3.wasabisys.com/ejemplo.jpg]
tests/test_services.py::test_update_package_keeps_permanent_and_promotes_temporal
tests/test_services.py::test_create_package_validates_all_urls_before_promoting
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[short_name]
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_name]
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[price_below_floor]
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[capacity_over_cap]
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_description]
tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[mixed_case_name]
tests/test_services.py::test_public_catalog_survives_one_off_rule_package
tests/test_services.py::test_inactive_column_returns_off_rule_package
tests/test_services.py::test_deleted_column_returns_off_rule_package
tests/test_services.py::test_update_on_off_rule_package_returns_200_with_persisted_change
tests/test_services.py::test_create_still_rejects_short_name
tests/test_services.py::test_update_still_rejects_capacity_over_limit
tests/test_services.py::test_create_still_title_cases_name
tests/test_audit.py::test_audit_trail_creation_and_retrieval
tests/test_audit.py::test_audit_trail_forbidden_for_tourist
tests/test_audit.py::TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called
tests/test_audit.py::TestAuditServiceAuthorization::test_admin_calls_repo_exactly_once_with_expected_args
tests/test_audit.py::test_audit_trail_accessible_for_admin
tests/test_audit.py::test_audit_trail_requires_authentication
```

Ejecución de los dos archivos tras el cambio: `42 passed, 3 warnings in 0.84s` (36 + 6).

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

| Medida | Línea base (antes de tocar, HEAD `68cf40c`) | Tras la fase B | Fila "Fase B" del plan |
|---|---|---|---|
| pytest | `380 passed, 5 warnings in 20.97s` | `380 passed, 5 warnings in 16.99s` | 380 |
| Cobertura | `TOTAL 942 34 136 22 94.81%` | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % |
| import-linter | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT |
| ruff total | `Found 60 errors.` | `Found 59 errors.` | 59 |
| ruff en `tests/` | `Found 7 errors.` | `Found 6 errors.` | 6 |
| mypy | `Found 10 errors in 5 files (checked 35 source files)` | igual | 10 |

Criterios propios de la fase:

- `ruff check tests/test_services.py tests/test_audit.py` → `All checks passed!`
- `ruff format --check` de los dos → `2 files already formatted`
- En los dos archivos: `User(` → 0, `create_access_token(` → 0, `f"Bearer {` → 0,
  `def (admin_token|auth_headers|superadmin_token)\(` → 0 (cada uno).
- Los 6 errores de ruff que quedan en `tests/`: `test_auth.py:1`, `:50`, `:162` (fase C),
  `test_user_access_policy.py:347`, `:395` (fase E) y `test_user_service.py:3` (residual del plan).

## Residuales

- `mypy` sobre los dos archivos tocados (la compuerta solo mide `app/`) da 2 errores en ellos, heredados y en
  líneas que esta fase no cambia: `tests/test_services.py:157` (`Value of type "object" is not indexable`; es la
  antigua l.183, ya anotada en el handoff A y en el OPCIONAL de `gaps.md`, desplazada 26 líneas) y
  `tests/test_audit.py:72` (`Returning Any from function declared to return "AuditRepository"`, el fixture
  `audit_repo`; antigua l.98, idéntica en `HEAD~1`). No se tocan: mismo destino que el OPCIONAL de la fase A
  (entrada de `tests/` en el alcance de mypy).
- Fuera de alcance según el plan y sin tocar: comentario en español de `test_audit.py` (ahora l.21), `from
  sqlalchemy.future` de `test_services.py:14`, aserciones sobre `"detalle"`, `assert_awaited_once()` sin argumentos.

## Desviaciones y dudas

- Ninguna desviación del plan. La edición se hizo con un script en el scratchpad; al escribir, Python en Windows
  convirtió `test_services.py` a CRLF y se devolvió a LF antes del commit (el diff final solo contiene los cambios
  de la fase; `.gitattributes` fija `eol=lf`).
- `test-sanitizer` aplicado como checklist: preparación solo con `persist_user`/`make_auth_headers`; el 403 afirma
  código y tipo de `detail`, sin texto en español; ningún test reescrito más allá de lo que pide el plan.

# Handoff — BE-38 · Fase B (calcular lo que cambió; `PATCH /usuarios/{cedula}`)

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `dc7195d`.
- Plan: `docs/deuda/BE-38/plan.md`, fase B y Anexo B; aprobado con E0 (la fase B no depende de la opción de precio).

## Ritual de arranque

- `git status --short`: limpio. HEAD `1079a46`. `current_target` = `Fase_B`.
- Vigencia de la línea base: `git fetch origin` correcto (exit 0). `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0, todos los pasos con ✔): `TOTAL 1047 10 150 8 98.50%` ·
  `759 passed, 25 warnings`. Igual al GREEN de la fase A (línea base 757 · 98,49 % + fase A); no peor.

## Archivos tocados (5, los del plan)

- `app/services/audit_service.py`: `_JSON_VALUE: TypeAdapter[Any]`, funciones de módulo `audit_value` y
  `changed_fields` (docstrings Google, ADR-0021).
- `app/services/user_service.py`: import de `changed_fields`; en `update_user_account`, tras `assert_can_update` (sin
  cambios, sigue recibiendo el `update_dict` completo) y antes del bucle `setattr`, `changes = changed_fields(target_user,
  update_data.model_dump(exclude_unset=True))`; `if update_dict:` → `if changes:` y `changes=changes`; pasos renumerados
  (3 → 5); dos líneas de docstring.
- `tests/test_user_update_audit.py` (nuevo): texto literal del Anexo B.
- `tests/test_user_access_policy.py`: los 8 tests reescritos del Anexo B.
- `tests/test_user_update_null.py`: `test_be37_null_on_phone_still_clears_it` con `{"old", "new"}`.

Aplicado desde el diff literal del Anexo B (`git apply --check` limpio; primero solo `tests/*`, luego `app/*`) y el
archivo nuevo copiado tal cual del anexo. `git diff --numstat` antes del commit: `44 0`, `10 5`, `152 0`, `22 6`,
`1 1` (el plan dicta exactamente esos).

`git show --stat --format= dc7195d`:

```
 app/services/audit_service.py    |  44 ++++++++++++
 app/services/user_service.py     |  15 ++--
 tests/test_user_access_policy.py |  28 ++++++--
 tests/test_user_update_audit.py  | 152 +++++++++++++++++++++++++++++++++++++++
 tests/test_user_update_null.py   |   2 +-
 5 files changed, 229 insertions(+), 12 deletions(-)
```

## RED (solo los tests, suite completa, `pytest -q -rf`)

```
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_profile_update_returns_200
FAILED tests/test_user_access_policy.py::test_be02_superadmin_changes_third_party_role_returns_200
FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_update_with_is_active_true_returns_200
FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
FAILED tests/test_user_access_policy.py::test_be58_admin_self_update_with_is_active_true_returns_200
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[role-same]
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[first-name-same]
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[first-name-normalized]
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[phone-null-already-null]
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[is-active-same]
FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[four-keys-same]
FAILED tests/test_user_update_audit.py::test_be38_email_in_another_case_is_unchanged
FAILED tests/test_user_update_audit.py::test_be38_partial_change_audits_only_the_changed_field
FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
18 failed, 751 passed, 25 warnings in 46.13s
```

Plan: `18 failed, 751 passed` (8 de `test_user_update_audit.py` con las dos guardas en verde, 8 de
`test_user_access_policy.py`, 2 de `test_user_update_null.py`). Coincide.

## GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1055     10    150      7  98.59%
769 passed, 25 warnings in 35.16s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `769 passed` (plan: 769). Cobertura: 98,59 % (plan: 98,59 %; ≥ 98,50 % de la fase A y 98,49 % de la base).
  Avisos: 25, como la base. Formato: 71 archivos; mypy: 66 (plan: 71 y 66 desde B).
- Sobre los archivos tocados: `ruff format --check` → `5 files already formatted`; `ruff check` → `All checks passed!`;
  `mypy` → `Success: no issues found in 5 source files`.
- Contratos: 4 kept, 0 broken (= línea base).

## Mutantes M1 y M3u (copia `git archive dc7195d` en el scratchpad, nunca en el repo; suite completa; restaurada: `769 passed`)

M1 — `changes` antes de la política y la política solo con las claves que cambian:

```
FAILED tests/test_user_access_policy.py::test_b2_admin_self_role_noop_returns_403
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_noop_returns_403
FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
FAILED tests/test_user_update_audit.py::test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403
FAILED tests/test_user_update_audit.py::test_be38_admin_self_role_with_unchanged_value_returns_403
5 failed, 764 passed, 25 warnings in 37.10s
```

Muere. Misma lista de 5 que el plan ("Mediciones", 4).

M3u — `changed_fields` después del bucle `setattr`:

```
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_profile_update_returns_200
FAILED tests/test_user_access_policy.py::test_be02_superadmin_changes_third_party_role_returns_200
FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
FAILED tests/test_user_update_audit.py::test_be38_partial_change_audits_only_the_changed_field
FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
8 failed, 761 passed, 25 warnings in 41.73s
```

Muere. El plan mide 9 sobre la copia final; el noveno es
`tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row` (V4), que nace en la fase C.
Las 8 restantes son exactamente las del plan. No es desviación.

## Checklist `test-sanitizer` (solo estándares; sin reescrituras)

Sin mocks; fábricas centrales (`persist_user`, `make_auth_headers`); nombres y aserciones en inglés; clave `detail`
(solo `isinstance(..., str)`, ningún texto en español); guardas ABAC (las dos de M1). Cada caso afirma código, cuerpo,
estado refrescado (`db_session.refresh`) y filas de `AuditLog`. Nada que corregir.

## Residuales y dudas

- Ninguna desviación del plan. Ningún archivo fuera de la fase.
- Observación menor, sin acción: `_audit_rows` existe ahora en `tests/test_user_update_audit.py` y en
  `tests/test_user_update_null.py` (y D añade otra en `tests/test_services.py`); lo dicta el plan y es un helper de consulta,
  no de preparación, así que no choca con la regla de fábricas de AGENTS §5.

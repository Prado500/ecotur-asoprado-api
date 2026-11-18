# Handoff — BE-38 · Fase C (la activación por correo deja fila y no alcanza a cuentas borradas)

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `2ef12e7`.
- Plan: `docs/deuda/BE-38/plan.md`, fase C y Anexo C; aprobado con E0 (la fase C no depende de la opción de precio;
  E0.3 aprueba la excepción a AGENTS §5: dobles `autospec` de `UserRepository` en `tests/test_user_service.py`).

## Ritual de arranque

- `git status --short`: limpio. HEAD `a25879f`. `current_target` = `Fase_C`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0, todos los pasos con ✔): `TOTAL 1055 10 150 7 98.59%` ·
  `769 passed, 25 warnings`. Igual al GREEN de la fase B; no peor.

## Archivos tocados (4, los del plan)

- `app/services/user_service.py`: en `verify_email_account`, `get_non_deleted_user_by_email` sustituye a
  `activate_user`; `NotFoundError` si es `None`; `changes = changed_fields(user, {"is_active": True})` y, si hay cambio,
  `user.is_active = True`, `save_user(user)` y `log_transaction(UPDATE, entity_id=user.cedula,
  performed_by=user.cedula, changes=changes)`; docstring ampliada (tres líneas y el `Raises`).
- `app/repositories/user_repository.py`: se borra `activate_user` (sin llamadores).
- `tests/test_user_service.py`: `test_verify_email_activates_account` reescrito; nuevo
  `test_verify_email_on_active_account_writes_nothing`; `test_verify_email_missing_user_raises_not_found` con
  `return_value = None` y tres afirmaciones de llamadas; las cuatro `activate_user.assert_not_awaited()` →
  `get_non_deleted_user_by_email.assert_not_awaited()`.
- `tests/test_auth.py`: import de `AuditAction, AuditLog`; `test_verify_email_endpoint_activates_account` afirma la
  fila; nuevos `test_be38_verify_email_on_active_account_returns_200_without_audit_row` (V3),
  `test_be38_verify_email_on_deleted_account_returns_404_without_mutation` (V5) y
  `test_be38_verify_email_after_admin_deactivation_writes_an_audit_row` (V4).

Aplicado desde el diff literal del Anexo C (`git apply --check` limpio; primero `--include='tests/*'`, luego
`--include='app/*'`). `git diff --numstat` antes del commit: `0 13`, `19 3`, `67 0`, `43 11` (el plan dicta
`19 3`, `0 13`, `43 11`, `67 0`: idénticos).

`git show --stat --format= 2ef12e7`:

```
 app/repositories/user_repository.py | 13 -------
 app/services/user_service.py        | 22 ++++++++++--
 tests/test_auth.py                  | 67 +++++++++++++++++++++++++++++++++++++
 tests/test_user_service.py          | 54 ++++++++++++++++++++++++------
 4 files changed, 129 insertions(+), 27 deletions(-)
```

## RED (solo los tests, suite completa, `pytest -q -rf`)

```
FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account - Ass...
FAILED tests/test_auth.py::test_be38_verify_email_on_deleted_account_returns_404_without_mutation
FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
FAILED tests/test_user_service.py::test_verify_email_activates_account - asse...
FAILED tests/test_user_service.py::test_verify_email_on_active_account_writes_nothing
FAILED tests/test_user_service.py::test_verify_email_missing_user_raises_not_found
6 failed, 767 passed, 25 warnings in 34.74s
```

Plan: `6 failed, 767 passed` (3 unitarios y 3 HTTP; V3 y los cuatro de token, verdes). Coincide caso por caso.

## GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1051     10    150      7  98.58%
773 passed, 25 warnings in 35.91s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `773 passed` (plan: 773). Cobertura: 98,58 % (plan: 98,58 %; ≥ 98,49 % de la línea base de la verificación).
  Baja una centésima frente a la fase B (98,59 %) porque se borran las 13 líneas de `activate_user`, que estaban
  cubiertas (`Stmts` 1055 → 1051); el plan lo midió así. Avisos: 25, como la base.
- Sobre los archivos tocados: `ruff format --check` → `4 files already formatted`; `ruff check` → `All checks passed!`;
  `mypy` → `Success: no issues found in 4 source files`.
- Contratos: 4 kept, 0 broken (= línea base).
- Comando 3 del plan (parte de esta fase): `git grep -n "activate_user" -- app tests` → sin salida, exit 1.

## Mutantes M5, M11 y M12 (copia `git archive 2ef12e7` en el scratchpad, nunca en el repo; suite completa; restaurada)

```
== M5   (get_non_deleted_user_by_email sin deleted_at.is_(None))
    FAILED tests/test_auth.py::test_be38_verify_email_on_deleted_account_returns_404_without_mutation
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
    3 failed, 770 passed, 25 warnings in 34.38s
== M11  (la activación guarda y audita siempre: if changes: -> if True:)
    FAILED tests/test_auth.py::test_be38_verify_email_on_active_account_returns_200_without_audit_row
    FAILED tests/test_user_service.py::test_verify_email_on_active_account_writes_nothing
    2 failed, 771 passed, 25 warnings in 41.04s
== M12  (performed_by=email en la activación)
    FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_service.py::test_verify_email_activates_account
    3 failed, 770 passed, 25 warnings in 39.66s
```

Los tres mueren, con exactamente los casos del plan ("Mediciones", 4: M5 3, M11 2, M12 3). Las cifras de casos fallidos
coinciden con las de la copia final A–G (allí `… 790/794 passed` solo porque la suite final es mayor). Tras cada
mutante el archivo se restauró; comparado con `git show HEAD:<archivo>` difiere solo en el fin de línea CRLF de la
copia.

## Checklist `test-sanitizer` (solo estándares; sin reescrituras)

Dobles `autospec` de `UserRepository` y `AuditService` solo en `tests/test_user_service.py` (excepción aprobada, E0.3);
fábricas centrales (`make_user`, `persist_user`, `make_auth_headers`); `assert_awaited_once_with` con todos los
argumentos y `assert_not_awaited` en los caminos que no escriben; el 404 se afirma por código y estructura
(`set(body) == {"detail"}`, `isinstance(..., str)`), sin texto en español; estado refrescado (`db_session.refresh`)
y filas de `AuditLog` en los HTTP. Nada que corregir.

## Residuales y dudas

- Ninguna desviación del plan. Ningún archivo fuera de la fase.
- R4 del plan sigue vigente: BE-49 cita el doble de `activate_user`, que tras esta fase no existe (destino: nota en la
  fila BE-49, E0.6; no se toca el backlog en esta fase).

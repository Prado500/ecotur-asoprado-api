# Handoff — BE-38 · Fase A (alta administrativa: crear primero, auditar después)

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `9d89f8e`.
- Plan: `docs/deuda/BE-38/plan.md`, fase A y Anexo A; aprobado con E0 (la fase A no depende de la opción de precio).

## Ritual de arranque

- `git status --short`: limpio. HEAD `964f15e`. `current_target` = `Fase_A`.
- Vigencia de la línea base: `git fetch origin` correcto (exit 0). `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0): `70 files already formatted` · ruff `All checks passed!` · mypy
  `Success: no issues found in 65 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1046 10 150 8 98.49%` · `757 passed, 25 warnings`. Igual a la línea base de la verificación.

## Archivos tocados (2, los del plan)

- `app/services/user_service.py`: en `create_administrative_account`, `saved_user = await
  self.user_repo.create_user(new_user)` antes de `log_transaction`, que pasa a `entity_id=saved_user.cedula`;
  `return saved_user`; una frase de docstring (ADR-0021).
- `tests/test_user_service.py`: import de `IntegrityError` y `OperationalError`;
  `test_create_administrative_account_provisions_admin` con `create_user.side_effect = lambda user: user` y
  `assert result is created_user`; nuevo `test_create_administrative_account_insert_failure_writes_no_audit_row`
  (ids `race-on-unique-index`, `database-failure`).

`git show --stat --format= 9d89f8e`:

```
 app/services/user_service.py |  9 ++++++---
 tests/test_user_service.py   | 41 +++++++++++++++++++++++++++++++++++++++--
 2 files changed, 45 insertions(+), 5 deletions(-)
```

`git diff --numstat` antes del commit: `6 3 app/services/user_service.py` y `39 2 tests/test_user_service.py` (el plan
dicta `6 3` y `39 2`). El diff coincide línea por línea con el Anexo A.

## RED (solo los tests, suite completa)

```
FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]
FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[database-failure]
2 failed, 757 passed, 25 warnings in 32.85s
```

Plan: `2 failed, 757 passed`, fallan exactamente los dos ids. Coincide.

## GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
70 files already formatted
All checks passed!
Success: no issues found in 65 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1047     10    150      8  98.50%
759 passed, 25 warnings in 33.56s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `759 passed` (plan: 759). Cobertura: 98,50 % (plan: 98,50 %; línea base 98,49 %). Avisos: 25, como la base.
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `mypy` → `Success: no issues found in 2 source files`.
- Contratos: 4 kept, 0 broken (= línea base).

## Mutante M4 (copia de los archivos versionados en el scratchpad, nunca en el repo)

`log_transaction` con `entity_id=user_data.cedula` movido antes de `create_user`:

```
FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]
FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[database-failure]
2 failed, 757 passed, 25 warnings in 33.33s
```

Muere, como predice el plan ("los dos ids del test de A").

## Checklist test-sanitizer

Dobles `autospec` de `UserRepository` (fixtures existentes; excepción a AGENTS §5 declarada en el plan y aprobada en E0,
punto 3); aserciones sobre llamadas con argumentos (`assert_awaited_once_with`, `assert_not_awaited`) y sobre el tipo de
la excepción; ningún texto en español afirmado; docstrings presentes. Nada que reescribir.

## Residuales y dudas

- Incidencia de proceso, sin efecto en el resultado: el hook de `ruff --fix` borró el import nuevo de `IntegrityError` y
  `OperationalError` tras la primera edición (aún no se usaban); se repuso después de añadir el test. El diff final es el
  del Anexo A.
- Ninguna desviación respecto del plan. A3 (fila de auditoría que falla tras el alta) sigue fuera, como declara el plan.

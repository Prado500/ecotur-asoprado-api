# Gaps — BE-38

## Auditoría Fase A — 2026-11-18
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (contexto fresco; el relato del handoff no se tomó como evidencia):

- Árbol: `git status --short` vacío antes y después de la compuerta. HEAD `9cdc9d1` (progress + handoff), padre
  `9d89f8e` (fase A), padre `964f15e`.
- Commit `9d89f8e`: `git show --stat` → `app/services/user_service.py | 9 ++++++---`, `tests/test_user_service.py | 41
  +++…--`, `2 files changed, 45 insertions(+), 5 deletions(-)`; solo los dos archivos de la fase (plan: +45 −5,
  numstat `6 3` y `39 2`). Mensaje (`git log -1 --format=%B 9d89f8e`) idéntico al dictado en "Fase A → Commit",
  incluida la línea `Co-Authored-By`.
- Diff contra el plan: `git show --format= 9d89f8e` sin las líneas `diff --git`/`index`, comparado con `diff` contra
  `plan.md` líneas 1039–1135 (Anexo A): sin diferencias (exit 0). Todos los puntos de "Cambios exactos" están:
  `create_user` antes de `log_transaction`, `entity_id=saved_user.cedula`, `return saved_user`, frase de docstring,
  imports `IntegrityError`/`OperationalError`, `side_effect = lambda user: user` y `assert result is created_user`.
- Tests (RED primero): `test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]` y
  `[database-failure]` existen y pasan. RED reproducido por el auditor en una copia `git archive 9d89f8e` (scratchpad)
  con `app/services/user_service.py` de `964f15e`: `2 failed, 20 passed` en `tests/test_user_service.py`; fallan
  exactamente los dos ids.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `70 files already formatted` · ruff
  `All checks passed!` · mypy `Success: no issues found in 65 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1047 10 150 8 98.50%` · `759 passed, 25 warnings`. Línea base (`verificacion.md`): 757 passed · 98,49 % ·
  ruff 0 · mypy 0 en 65 · 4 kept. Criterio de aceptación (759 passed, 98,50 %) cumplido; la cobertura sube.
- Archivos tocados: `ruff check` → `All checks passed!`; `mypy` → `Success: no issues found in 2 source files`.
- `progress.json`: JSON válido; `Fase_A` `completed` con `9d89f8e` (hash real); `current_target` `Fase_B`;
  `last_handoff` presente; `edit_rules` sin cambio (`git diff 964f15e 9cdc9d1 -- docs/deuda/BE-38/progress.json`
  solo toca `current_target`, `status`, `commit` y `last_handoff`).
- AGENTS: dobles `create_autospec(…, instance=True)` (`tests/test_user_service.py:73`, `:79`), excepción a §5 declarada
  en el plan y aprobada en E0, punto 3; aserciones sobre llamadas con argumentos y tipo de excepción; ningún texto en
  español afirmado; docstrings en inglés. Sin excepciones de dominio nuevas, sin capas cruzadas (4 kept).
- No es la última fase: la "Verificación final" no aplica.

## Auditoría Fase B — 2026-11-18
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (contexto fresco; el relato del handoff no se tomó como evidencia):

- Árbol: `git status --short` vacío antes y después de la compuerta. HEAD `486e1af` (progress + handoff-B, solo
  `docs/deuda/BE-38/`), padre `dc7195d` (fase B), padre `1079a46`.
- Commit `dc7195d`: `git show --stat` → `app/services/audit_service.py | 44`, `app/services/user_service.py | 15`,
  `tests/test_user_access_policy.py | 28`, `tests/test_user_update_audit.py | 152`, `tests/test_user_update_null.py | 2`,
  `5 files changed, 229 insertions(+), 12 deletions(-)`: los cinco archivos de la fase y ninguno más (plan: +229 −12).
  Mensaje (`git log -1 --format=%B dc7195d`) comparado con `diff` contra `plan.md` l.299–319: idéntico (solo difiere el
  salto de línea final que añade `%B`), incluidos `BREAKING CHANGE:` y `Co-Authored-By`.
- Diff contra el plan: las líneas `+`/`-` de `git show --format= dc7195d` sobre los cuatro archivos modificados,
  comparadas con `diff` contra el Anexo B (`plan.md` l.1144–1348): sin diferencias (exit 0); el archivo completo, sin
  filtrar, también idéntico. `git show dc7195d:tests/test_user_update_audit.py` contra `plan.md` l.1354–1505: idéntico.
  Todos los puntos de "Cambios exactos" están: `_JSON_VALUE: TypeAdapter[Any]`, `audit_value` y `changed_fields` como
  funciones de módulo con docstring Google y ADR-0021; `assert_can_update` sigue recibiendo `update_dict`
  (`app/services/user_service.py:289`); `changes = changed_fields(target_user, update_data.model_dump(exclude_unset=True))`
  antes del bucle `setattr` (:292); `if changes:` y `changes=changes` (:299–305); pasos 3 → 5; dos líneas de docstring.
- Tests (RED primero): los 10 casos nuevos de `tests/test_user_update_audit.py` y los 10 reescritos existen y pasan. RED
  reproducido por el auditor en una copia `git archive dc7195d` (scratchpad) con `audit_service.py` y `user_service.py`
  de `1079a46`: `18 failed, 751 passed, 25 warnings`; la lista de FAILED coincide línea a línea con "Mediciones", 1
  (8 de la política, 8 de `test_user_update_audit.py` con las dos guardas en verde, 2 de `test_user_update_null.py`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `71 files already formatted` · ruff
  `All checks passed!` · mypy `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1055 10 150 7 98.59%` · `769 passed, 25 warnings`. Línea base (`verificacion.md`): 757 passed · 98,49 % · ruff 0
  · mypy 0 en 65 · 4 kept; fase A: 759 · 98,50 %. Criterio de aceptación (769 passed, 98,59 %) cumplido; la cobertura
  sube; avisos 25, como la base.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `5 files already formatted`; `mypy` →
  `Success: no issues found in 5 source files`.
- Mutantes del criterio, re-ejecutados por el auditor en copias `git archive dc7195d` (suite completa):
  M1 (cálculo antes de la política y política solo con las claves que cambian) → `5 failed, 764 passed`, los cinco del
  plan ("Mediciones", 4). M3u (`changed_fields` después del bucle `setattr`) → `8 failed, 761 passed`: los 5 de la
  política, `test_be38_partial_change_audits_only_the_changed_field` y `test_be37_null_on_phone_still_clears_it` ×2.
- M3u con 8 y no 9: **no es desviación.** La tabla de mutantes del plan (l.185–186) se midió sobre las "copias finales"
  A–G, y su noveno test es `tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row`
  (`plan.md` l.883, l.893), que la fase C crea (`plan.md` l.336, Anexo C l.1743); `git grep` de ese nombre en
  `dc7195d -- tests` sale vacío (exit 1). El criterio de la fase B (l.295) exige que M3u muera, sin cifra; muere, y los
  8 restantes son exactamente los de la lista del plan.
- Regla de grep (`git grep -n -E "changed_fields\(|if changes:|log_transaction\(" -- app`): las coincidencias son código
  (definición en `audit_service.py:28`, llamada y guarda en `user_service.py:292`, `:299`); ninguna en docstring o
  comentario.
- `progress.json`: JSON válido; `Fase_B` `completed` con `dc7195d` (hash real); `current_target` `Fase_C`;
  `last_handoff` presente; `edit_rules` sin cambio (`git diff 1079a46 486e1af -- docs/deuda/BE-38/progress.json` solo
  toca `current_target`, `status`, `commit` y `last_handoff`).
- AGENTS: sin mocks en los tests nuevos; fábricas centrales (`persist_user`, `make_auth_headers`); cada caso afirma
  código, cuerpo, estado tras `db_session.refresh` y filas de `AuditLog`; `detail` solo con `isinstance(..., str)`, ningún
  texto en español afirmado; docstrings e identificadores en inglés. Sin excepciones de dominio nuevas; `pydantic` ya en
  `pyproject.toml`; capas intactas (4 kept).
- No es la última fase: la "Verificación final" no aplica.

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

## Auditoría Fase C — 2026-11-18
**Veredicto Fase C: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase C — La fila BE-50 de `docs/backlog.md` sigue describiendo `activate_user`
(`app/repositories/user_repository.py:33-44`) como el mecanismo vigente; tras `2ef12e7` el método no existe y la
activación pasa por `get_non_deleted_user_by_email` + `save_user`, sin tocar cuentas borradas. E0.6 solo da destino a
R4 (BE-49), y BE-49 ya lleva su nota (`docs/backlog.md:104`, "Nota de BE-38 … residual R4", commiteada en `39fa95b`).
El plan deja `docs/backlog.md` fuera de alcance, así que no bloquea; destino sugerido: una nota en la fila BE-50, igual
que la de R4, cuando David cierre BE-38 (su `/deuda-verificar` la volvería a medir de todos modos). Evidencia:
`git grep -n "activate_user"` → `docs/backlog.md:105`.

Evidencia de lo comprobado (contexto fresco; el relato del handoff no se tomó como evidencia):

- Árbol: `git status --short` vacío antes de auditar. HEAD `49a3b46` (progress + handoff-C, solo `docs/deuda/BE-38/`:
  `git diff --stat 2ef12e7 49a3b46` → `handoff-C.md`, `progress.json`), padre `2ef12e7` (fase C), padre `a25879f`.
- Commit `2ef12e7`: `git show --stat` → `app/repositories/user_repository.py | 13 -------`,
  `app/services/user_service.py | 22 ++++++++++--`, `tests/test_auth.py | 67 +++`, `tests/test_user_service.py | 54 +++…--`,
  `4 files changed, 129 insertions(+), 27 deletions(-)`; `git diff --numstat a25879f 2ef12e7` → `0 13`, `19 3`, `67 0`,
  `43 11`: los cuatro archivos de la fase y el numstat dictado. Mensaje (`git show -s --format=%B 2ef12e7`) comparado con
  `diff` contra `plan.md` l.344–359: idéntico, incluida la línea `Co-Authored-By`.
- Diff contra el plan: las líneas `+`/`-` de `git diff a25879f 2ef12e7` (156), ordenadas, comparadas con `diff` contra
  las del Anexo C (`plan.md` l.1514–1770, 156): sin diferencias. Todos los puntos de "Cambios exactos" están:
  `get_non_deleted_user_by_email`, `NotFoundError` si `None`, `changed_fields(user, {"is_active": True})`, guarda
  `if changes:` (`app/services/user_service.py:151`), `save_user` y `log_transaction(UPDATE, entity_id=user.cedula,
  performed_by=user.cedula, changes=changes)` (:152–160), docstring ampliada y `Raises` reescrito;
  `UserRepository.activate_user` borrado.
- Tests (RED primero): los 7 tests de la fase existen y pasan (`test_verify_email_activates_account`,
  `test_verify_email_on_active_account_writes_nothing`, `test_verify_email_missing_user_raises_not_found`, las cuatro
  `get_non_deleted_user_by_email.assert_not_awaited()`; en `test_auth.py`, la fila de
  `test_verify_email_endpoint_activates_account` y los tres `test_be38_verify_email_*`). RED reproducido por el auditor
  en una copia `git archive 2ef12e7` (scratchpad) con `user_service.py` y `user_repository.py` de `a25879f`, suite
  completa: `6 failed, 767 passed, 25 warnings`; fallan exactamente los 3 unitarios y los 3 HTTP del plan; V3 y los
  cuatro de token, verdes.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `71 files already formatted` · ruff
  `All checks passed!` · mypy `Success: no issues found in 66 source files` · 4 contratos KEPT · `TOTAL 1051 10 150 7
  98.58%` · `773 passed, 25 warnings`. Línea base (`verificacion.md`): 757 passed · 98,49 % · ruff 0 · mypy 0 en 65 ·
  4 kept. Criterio de aceptación (773 passed, 98,58 %) cumplido. La cobertura baja una centésima frente a la fase B
  (98,59 %) al borrar 13 líneas cubiertas (`Stmts` 1055 → 1051): sigue por encima de la línea base y es la cifra que el
  plan midió; no es hallazgo. Avisos 25, como la base.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`; `mypy` →
  `Success: no issues found in 4 source files`.
- Mutantes del criterio, re-ejecutados por el auditor en copias `git archive 2ef12e7` (suite completa; `diff` contra
  `git show 2ef12e7:<archivo>` confirma una sola línea mutada en cada una):
  M5 (`user_repository.py:44` sin `User.deleted_at.is_(None)`) → `3 failed, 770 passed`
  (`test_be38_verify_email_on_deleted_account_returns_404_without_mutation`, `test_self_soft_delete_keeps_row_and_blocks_login`,
  `test_token_for_soft_deleted_active_user_returns_401`); M11 (`user_service.py:151` `if changes:` → `if True:`) →
  `2 failed, 771 passed` (V3 HTTP y unitario); M12 (`user_service.py:158` `performed_by=user.email`) → `3 failed,
  770 passed` (V1 HTTP y unitario, V4). Los tres mueren con los casos de "Mediciones", 4.
- Comando 3 del plan, parte de esta fase: `git grep -n "activate_user" -- app tests` → sin salida (exit 1).
  Grep en todo el repo (versionado y no versionado, sin `venv` ni cachés): `activate_user` solo aparece en `docs/`.
  Clasificación: `docs/backlog.md:104` (BE-49) es la nota de R4 ya escrita (E0.6 cumplido); `docs/backlog.md:105`
  (BE-50), el opcional de arriba; el resto (`docs/archive/auditorias/…html`, `docs/bitacora/2026-11-12.md`,
  `2026-11-18.md`, y los `plan.md`/`verificacion.md`/`handoff`/`gaps.md` de BE-32, BE-33, BE-34, BE-36, BE-38, BE-40 y
  BE-42) son registros históricos de lo que había cuando se escribieron: no se tocan.
- `progress.json`: JSON válido; `Fase_C` `completed` con `2ef12e7` (hash real); `current_target` `Fase_D`;
  `last_handoff` presente; `edit_rules` sin cambio (`git diff a25879f 49a3b46 -- docs/deuda/BE-38/progress.json` solo
  toca `current_target`, `status`, `commit` y `last_handoff`).
- AGENTS: dobles `autospec` de `UserRepository`/`AuditService` solo en `tests/test_user_service.py` (excepción a §5
  aprobada en E0, punto 3), con `assert_awaited_once_with` de todos los argumentos y `assert_not_awaited` en los caminos
  que no escriben; los HTTP usan fábricas centrales (`persist_user`, `make_auth_headers`), refrescan el estado y leen
  las filas de `AuditLog`; el 404 se afirma por código y estructura (`set(body) == {"detail"}`, `isinstance(…, str)`),
  sin texto en español. Docstrings en inglés. Sin excepciones de dominio nuevas (`NotFoundError` ya registrada); el
  servicio no importa FastAPI; el repositorio pierde un `commit()` (A3 mejora); capas intactas (4 kept).
- No es la última fase: la "Verificación final" no aplica.

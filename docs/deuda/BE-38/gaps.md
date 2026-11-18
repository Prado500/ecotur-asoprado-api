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

## Auditoría Fase D — 2026-11-18
**Veredicto Fase D: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase D — El ejecutor corrió los seis mutantes sobre el árbol de trabajo del repo (con los cambios de la
fase aún sin commitear) y restauró los archivos a mano; las fases A–C los corrieron en copias del scratchpad. No hay
regla que lo prohíba: el "nunca en el repo" del plan (`plan.md` l.12) describe cómo midió el redactor, y l.185–186 solo
pide que "el ejecutor de cada fase repite los suyos sobre su fase", sin decir dónde. Tampoco quedó ningún resto (abajo:
blobs idénticos al Anexo D, árbol limpio). Se registra porque el riesgo es real y la compuerta no lo detecta: un
mutante que la suite no mata y que se queda sin restaurar entra en el commit con la compuerta en verde. M2 es ese caso
desde la fase E (vive con la opción (b), E0.2). Además M2 mutó `app/services/audit_service.py`, que no es de esta fase.
Para las fases E–G se recomienda volver a las copias (`git archive` en el scratchpad). Evidencia: `handoff-D.md`
l.118–120; `ls --full-time app/services/audit_service.py` → `15:35:25`, posterior a `71c4b6f` (15:29:32) y anterior a
`53ea731` (15:41:17), con contenido idéntico a ambos (`git diff --quiet 71c4b6f 53ea731 -- app/services/audit_service.py`
→ 0).

Evidencia de lo comprobado (contexto fresco; el relato del handoff no se tomó como evidencia):

- Árbol: `git status --short` vacío antes de auditar, después de la compuerta y después de los mutantes. HEAD `b081999`
  (progress + handoff-D; `git diff --stat 53ea731 b081999` → solo `handoff-D.md` y `progress.json`), padre `53ea731`
  (fase D), padre `71c4b6f`. `git status --short --ignored` sin `.orig`, `.bak`, `.rej` ni copias en `app/` o `tests/`;
  `scripts/.coverage` y `scripts/.mypy_cache` son del 24 oct, anteriores a la fase.
- Sin restos de mutantes: el Anexo D (`plan.md` l.1779–2170) se aplica limpio con `git apply` sobre una copia
  `git archive 71c4b6f` (scratchpad). Los cuatro archivos dan el mismo md5 en la copia + Anexo, en `53ea731` y en el
  árbol de trabajo: `tourist_services_service.py` `ddb3af2b…`, `models/service.py` `c1fbe508…`, `test_services.py`
  `fc78c975…`, `test_models_schema.py` `fc83cc3a…`. `git diff --stat 53ea731 HEAD -- app tests` vacío.
- Commit `53ea731`: `git diff --numstat 71c4b6f 53ea731` → `5 1` `app/models/service.py`, `27 16`
  `tourist_services_service.py`, `8 0` `test_models_schema.py`, `225 2` `test_services.py`: son los cuatro archivos y el
  numstat que dicta el plan (l.363–364), +265 −19. El mensaje (`git show -s --format=%B`), comparado con `diff` contra
  `plan.md` l.390–410, es idéntico salvo el salto de línea final que añade `%B`. Incluye `BREAKING CHANGE:` y
  `Co-Authored-By`.
- Cambios exactos, todos presentes: import de `changed_fields`. En `update_package_details`,
  `changes = changed_fields(service, update_dict)` (:289) antes del bucle `setattr` (:290–291) y `old_urls` antes de
  `images.clear()`; paso 2.8 `if definitive_urls != old_urls:` (:345–346); `if changes:` / `changes=changes`;
  `payload_changes` desaparece. En `toggle_package_status`, primero `estado` y luego la mutación, `save_service` y la
  auditoría dentro de `if service.is_available != is_available:` (:132). Docstrings de los dos métodos con ADR-0021
  (:112, :263). `order_by=lambda: ServiceImage.id` (`app/models/service.py:52`) con dos líneas de docstring (:29–30).
  Test de precio: `{"old": "50000.00", "new": "60000"}` tal cual (E0.2: lo reescribe E(b)).
- Tests (RED primero): los 16 casos de la fase y las dos guardas de estado existen y pasan. RED reproducido por el
  auditor en una copia `git archive 53ea731` con `tourist_services_service.py` y `models/service.py` de `71c4b6f`, suite
  completa: `16 failed, 773 passed, 25 warnings`. La lista de FAILED coincide con la de "Mediciones", 1 y con la del
  handoff; las dos `test_be38_status_route_with_change_audits_the_action` pasan.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `71 files already formatted` · ruff
  `All checks passed!` · mypy `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1055 10 154 6 98.68%` · `789 passed, 25 warnings`. Línea base (`verificacion.md`): 757 passed · 98,49 % ·
  ruff 0 · mypy 0 en 65 · 4 kept. Fase C: 773 · 98,58 %. Criterio de aceptación (789 passed, 98,68 %) cumplido. 25
  avisos, como la base. La línea sin cubrir `tourist_services_service.py:297` es el `raise` de más de 10 imágenes, ya
  existente (antes `:293`).
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`; `mypy` →
  `Success: no issues found in 4 source files`.
- Mutantes del criterio, re-ejecutados por el auditor en seis copias `git archive 53ea731` (scratchpad, nunca en el
  repo; suite completa; un script exige una sola coincidencia y `diff` contra `git show 53ea731:<archivo>` confirma una
  sola línea mutada; `app` se importa de la copia, comprobado):
  M2 (`audit_service.py:47` en forma JSON) → `1 failed, 788 passed` (`[price-same-value]`);
  M3p (`changed_fields` después del bucle `setattr`) → `3 failed, 786 passed`
  (`test_be37_null_on_description_still_clears_it`, `…partial_package_change…`, `…price_change…`);
  M6 (`:132` → `if True:`) → `2 failed, 787 passed` (estado sin cambio ×2);
  M7 (`"new": raw_urls`) → `1 failed, 788 passed` (`test_be38_image_change_audits_the_stored_urls`);
  M9 (`set(definitive_urls) != set(old_urls)`) → `1 failed, 788 passed` (`…reordered_image_list…`);
  M10 (sin `order_by`) → `1 failed, 788 passed` (`test_service_images_load_in_stored_order`).
  Mueren los seis, con los mismos casos que "Mediciones", 4 y que el handoff. M2 da la cifra de la copia de la fase D
  (`plan.md` l.976).
- Verificación final, comandos que ya aplican: 3 sin salida (exit 1); 5 → `tourist_services_service.py:1`,
  `user_service.py:2`; 10 → `app/models/service.py:52`, como el plan. 4 → `tourist_services_service.py:289` y 6 →
  `:132`, donde el plan cita `:293` y `:136`. **No es desviación:** el plan mide sobre la copia final (l.524–526).
  Después de D, el único anexo que toca ese archivo es el F (E(b) toca `app/schemas/service.py` y
  `tests/test_services.py`; G, `app/models/audit.py` y el ADR), y sus hunks `@@ -30,7 +30,9 @@` y
  `@@ -67,12 +69,14 @@` añaden 4 líneas netas, todas por encima de `:112` (el de `-8,7 +8,7` suma 0). 289+4=293 y
  132+4=136. Las demás citas del plan cuadran igual: comando 2, `:288` → `:292`; comando 13, `:112`/`:263` →
  `:116`/`:267`.
- `progress.json`: JSON válido; `Fase_D` `completed` con `53ea731` (hash real, `git cat-file -t` → `commit`);
  `current_target` `Fase_E`; `last_handoff` presente; `edit_rules` sin cambio (`git diff 71c4b6f b081999 --
  docs/deuda/BE-38/progress.json` solo toca `current_target`, `status`, `commit` y `last_handoff`).
- AGENTS: los tests HTTP usan las fixtures centrales (`client`, `db_session`, `admin_headers`, `storage_double` y
  `classifying_storage`, dobles del CDN que ya existían). Preparan con `commit()` y releen con `db_session.refresh`
  (ADR-0011). Afirman el código, la estructura del cuerpo, el estado, las filas de `AuditLog` y las llamadas al CDN
  (`assert_awaited_once_with`, `assert_not_awaited`). No afirman ningún texto en español: el mensaje de estado solo se
  comprueba por sus claves. Docstrings en inglés. No hay excepciones de dominio nuevas; el servicio no importa FastAPI;
  las capas siguen intactas (4 kept). R1 es un cambio solo de ORM; el `alembic check` contra PostgreSQL queda para David
  después de esta auditoría (E0.4) y no cuenta para el veredicto.
- No es la última fase: la "Verificación final" completa no aplica.

## Auditoría Fase E — 2026-11-18
**Veredicto Fase E: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase E — Ningún test guarda la regla del tercer decimal en el alta (`ServiceBase`/`ServiceCreate`, `POST
/servicios/`): `test_be38_schema_keeps_rejecting_a_third_decimal` solo valida `ServiceUpdate`. El commit dice que los
dos DTO siguen dando 422 con un tercer decimal, y hoy es cierto, pero si alguien pierde `decimal_places=2` en
`ServiceBase` o pasa su validador a `mode="before"`, `POST` redondearía en silencio con la suite en verde. El plan se
cumple al pie de la letra: M13 es "el validador" en singular, y la cifra medida (`1 failed`, l.206/l.968) es la de
`ServiceUpdate`. Antes de E el hueco ya existía (ningún test enviaba un tercer decimal a `POST`). Destino sugerido:
backlog o fase F/G si David lo decide; no se toca en E. Evidencia (copias `git archive 1d9752e` del scratchpad, suite
completa): M13base, el `format_base_price` de `ServiceBase` con `mode="before"` y
`return v if v is None else Decimal(str(v)).quantize(_CENTS)` → `796 passed` (vive); M13dpbase, sin
`decimal_places=2` en `ServiceBase.base_price` (`app/schemas/service.py:36`) → `796 passed` (vive).

Evidencia de lo comprobado (contexto fresco; el relato del handoff no se tomó como evidencia):

- Árbol: `git status --short` vacío antes de auditar, después de la compuerta y después de los mutantes. HEAD `d6f880f`
  (padre `1d9752e`; `git diff --stat 584b40f d6f880f` → los dos archivos de la fase más `handoff-E.md` y
  `progress.json`); `1d9752e` tiene como padre `584b40f`. `git diff --quiet HEAD -- app tests` → 0, y
  `git diff --stat 1d9752e HEAD -- app tests` vacío: no quedó ningún resto de mutantes.
- `progress.json`: JSON válido; `Fase_E` `completed` con `1d9752e` (`git cat-file -t` → `commit`); `current_target`
  `Fase_F`; `last_handoff` presente; `edit_rules` sin cambio (`git diff 584b40f d6f880f -- progress.json` solo toca
  `current_target`, `status`, `commit` y `last_handoff`).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `71 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1064 10 154 6 98.69%` ·
  `796 passed, 25 warnings`. Coincide con la cifra (b) del plan (796 · 98,69 %, E0.2) y con el handoff. Supera la línea
  base de la verificación (757 · 98,49 % · ruff 0 · mypy 0 · 4 kept) y la fase D (98,68 %). Sobre los dos archivos
  tocados: `ruff check` → `All checks passed!`, `ruff format --check` → `2 files already formatted`, `mypy` → `Success:
  no issues found in 2 source files`.
- Plan contra commit: el mensaje de `1d9752e` es idéntico byte a byte al "Commit (b)" del plan (`diff` sin salida). El
  `numstat` es `15 0` (`app/schemas/service.py`) y `66 1` (`tests/test_services.py`), como dice la tabla de fases. Las 82
  líneas `+`/`-` del diff `584b40f..1d9752e` son idénticas a las del Anexo E(b) (`diff` sin salida). Solo cambian esos dos
  archivos. Anexo E(a) no ejecutado: `git diff --stat 6cae238 1d9752e -- app/repositories/service_repository.py` vacío
  (E0.2). Comando 15 de la Verificación final, con `service_repository.py` añadido: vacío. Comando 11: `:11 :61 :147`, como
  el plan con (b). Comando 14: `test_services.py:11` (12 tras F, que añade `test_be61_…`).
- Línea reescrita (punto 4): `test_be38_price_change_audits_old_and_new_values`, `"new": "60000"` → `"new": "60000.00"`
  (hunk `@@ -1028,7 +1030,7 @@`). Fuera del Anexo E(b), `tests/test_services.py` no cambia: dos imports, esa línea y la
  sección nueva, y nada más.
- Mutantes (E1: una copia `git archive 1d9752e | tar -x` por mutante en el scratchpad, aplicada con un script de
  reemplazo exacto con recuento comprobado. `diff -ru` contra una copia prístina muestra solo la línea o el bloque
  mutado. Suite completa con el Python del venv por ruta y cwd = la copia; los tracebacks de la sonda de import citan
  `…\scratchpad\audE\M2\app\…`, así que la copia importa su propio código):
  - M8b (sin el validador de `ServiceBase`) → `2 failed, 794 passed`: `create_answers…[integer]` y `[one-decimal]`. El
    plan da `3 failed`, pero lo mide sobre la copia final (l.938). El tercero, `test_create_package_promotes_temporal_url`,
    en `1d9752e` solo afirma `len(audits) == 1` (`tests/test_services.py:473-474`). La fila `CREATE` sigue siendo
    `package_data.model_dump` hasta F (Anexo F), y el criterio de F lo reconoce ("M8b con (b), por la fila"). Coincide
    con el handoff; no es desviación.
  - M8c (sin el validador de `ServiceUpdate`) → `3 failed, 793 passed`: precio auditado de D y `update_answers…[integer]`
    y `[one-decimal]`, los mismos casos que el plan.
  - M13 del ejecutor (`ServiceUpdate` con `mode="before"` y `return v if v is None else Decimal(str(v)).quantize(_CENTS)`)
    → `1 failed, 795 passed`: `test_be38_schema_keeps_rejecting_a_third_decimal` con `DID NOT RAISE ValidationError`.
    Representa bien el fallo que el plan describe: redondea `"50000.555"` antes de `decimal_places` y el 422 desaparece.
    La guarda de `None` evita que choque con la nulabilidad del DTO. Contraste: M13lit, solo `mode="before"` con el
    cuerpo intacto, que es la lectura más literal, → `7 failed, 789 passed`, todos por `AttributeError` ('int', 'float',
    'str' y 'NoneType' sin `quantize`), uno de ellos el test de `null` de BE-37. Muere por un fallo, no por redondear, así
    que no representa el defecto. Variante alternativa natural, M13dp (sin `decimal_places=2` en `ServiceUpdate`) →
    `1 failed, 795 passed`, mismo test, `DID NOT RAISE`. M13both (las dos en `before`) → `1 failed`. Las variantes de
    `ServiceBase` viven (ver el opcional).
  - M2 (`audit_service.py:47` → `audit_value(getattr(entity, field)) != audit_value(value)`) → `796 passed`: vive, como
    esperan E0.2, el riesgo 4 y R7. No es hallazgo.
- AGENTS: ningún DTO de salida cambia (A9: `ServiceResponse` hereda de `BaseModel`). No hay excepciones de dominio nuevas.
  Las capas siguen intactas (4 kept). Los tests HTTP usan las fixtures centrales (`client`, `db_session`, `admin_headers`,
  `storage_double`), preparan con `commit()` y releen con `refresh`/`get` (ADR-0011). Afirman código, campo, lista de
  `GET` y valor guardado. El borde del tercer decimal afirma `loc`, no texto. Nada en español en las aserciones;
  docstrings en inglés.
- No es la última fase: la "Verificación final" completa no aplica.

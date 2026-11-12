# Gaps — BE-40

## Auditoría Fase A — 2026-11-12
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, sobre `3eec1b9`):

- Árbol: `git status --short` limpio antes y después de la compuerta (este `gaps.md` es el único archivo nuevo).
- `progress.json`: `Fase_A` `completed` con `commit: "a138a9e"`; `git show --stat a138a9e` confirma el commit real
  (3 archivos: `app/api/dependencies.py`, `app/api/routers/service.py`, `app/api/routers/user.py`; 28+/26-).
  `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` sin cambios (diff de `3eec1b9`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`;
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `622 passed, 8 warnings` · `Total coverage: 96.47%`. Igual a la línea base de
  `verificacion.md:151-155` y a la fila A del plan.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
  `mypy` → `Success: no issues found in 3 source files`.
- Mensaje de commit: idéntico, línea a línea, al bloque "Commit" de la fase A (`plan.md:180-199`) con
  `<MODELO EJECUTOR>` sustituido (diff vacío).
- Cambios exactos: (1) `dependencies.py:1-2` `from typing import Annotated` + línea en blanco; `:165-170` bloque
  `IDENTITY ALIASES` literal tras `get_current_admin_user`. (2) `user.py`: fuera `Annotated`, `User` y el bloque
  `DEPENDENCY TYPE ALIASES`; import partido `:3-9` en la forma dictada. (3) `service.py:3` import dictado, fuera
  `from app.models.user import User`; los seis handlers con `usuario_actual: AdminDep,` (`:88,145,168,189,210,232`); los
  cuatro reordenados antes de `service_service` con su línea de Args subida; comentario de segmentación `:14-20` intacto.
- Tests: la fase no exige RED ni tests nuevos; ningún test tocado.
- Criterio de aceptación (corregido por E0.1):
  `grep -n "usuario_actual: User = " app/api/routers/service.py app/api/routers/user.py | wc -l` → `0`;
  `grep -rnE "^(UserDep|AdminDep) = " app --include=*.py` → 2 líneas, `app/api/dependencies.py:169-170`.
  El grep original sobre `app/` da 1 (`app/api/routers/audit.py:24`), lo que E0.1 prevé y retira la fase B.
- AGENTS.md: capas respetadas (`service.py` ya no importa de `user.py`; 4 contratos KEPT); sin excepciones de dominio
  nuevas; código y comentarios en inglés.

## Auditoría Fase B — 2026-11-12
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, sobre `cd475ee`):

- Árbol: `git status --short` limpio antes y después de la compuerta y de los mutantes (este bloque de `gaps.md` es el
  único cambio).
- `progress.json`: JSON válido; `Fase_B` `completed` con `commit: "0739e24"`; `git show --stat 0739e24` confirma el commit
  real (4 archivos: `app/api/dependencies.py`, `app/api/routers/audit.py`, `app/services/audit_service.py`,
  `tests/test_audit.py`; 77+/50-). `current_target` = `Fase_C`; `last_handoff` presente; `edit_rules` sin cambios
  (diff de `cd475ee`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`;
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `625 passed, 8 warnings` · `Total coverage: 96.82%`. Igual a la fila B del plan y al
  handoff; por encima de la línea base de `verificacion.md:151-152` (622 passed, 96,47 %).
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` (los 3 de `app/`) → `Success: no issues found in 3 source files`.
- Archivos de la fase: `git diff --name-only c8f3784 0739e24` = exactamente los 4 de `plan.md:204`.
- Mensaje de commit: idéntico, línea a línea, al bloque "Commit" de la fase B (`plan.md:266-288`) con
  `<MODELO EJECUTOR>` sustituido (diff vacío).
- Cambios exactos: (1) `audit_service.py`: fuera los imports de `User` y `UserAccessPolicy`; `__init__` con solo
  `audit_repo` y `-> None`; `retrieve_audit_history` sin `current_user`, sin su Args, sin `Raises:` y sin la llamada a
  `assert_is_admin_plus`; resumen y primer párrafo literales del plan; `log_transaction` intacto. (2) `dependencies.py:42-45`
  `get_audit_service` sin la política, `return AuditService(audit_repo)`; `get_user_access_policy` sigue en uso por
  `get_user_service` (`:51`). (3) `audit.py:3` import dictado, fuera `User`, el parámetro y el argumento; docstring
  `:23-31` según E0.2 (párrafo entero sustituido, resumen y línea en blanco intactos). (4) `tests/test_audit.py`: imports
  dictados (`:5` `SQLAlchemyError` tras `import pytest`); clase `TestAuditServiceHistory` con el docstring del plan,
  fixture autospec y `AuditService(audit_repo)`; test HTTP de filtros al final (`:143`) con el docstring del plan.
- Tests: los 4 unitarios (`tests/test_audit.py:62,84,94,105`) y el HTTP (`:143`) existen con los nombres del plan y pasan.
  RED re-medido en copia desechable (estado `c8f3784` + `tests/test_audit.py` nuevo): `4 failed, 3 passed`, los cuatro con
  `TypeError: AuditService.__init__() missing 1 required positional argument: 'user_access_policy'`. Coincide con
  `plan.md:255-257` y con el handoff.
- Mutante M4 re-medido en copias desechables (procedimiento común): estado A → `333 passed` (sobrevive); estado B →
  `2 failed, 334 passed` con `test_protected_route_rejects_request_without_token[GET /auditoria/]` y
  `test_admin_route_rejects_tourist[GET /auditoria/]`. Copia de B sin mutante: `336 passed` (fila B, columna copia).
  Coincide con `plan.md:258-259`.
- Criterio de aceptación (con E0): `grep -cE "user_access_policy|UserAccessPolicy|current_user" app/services/audit_service.py`
  → `0`; `grep -c "Over-fetching" app/api/routers/audit.py` → `1` (E0.2); `grep -rn "usuario_actual: User = " app
  --include=*.py | wc -l` → `0` (E0.1, vale desde B); `grep -A3 "def get_audit_service" app/api/dependencies.py | grep -c
  "user_access_policy"` → `0`.
- Precisiones declaradas por el ejecutor, valoradas sin hallazgo: (a) los 4 unitarios sin docstring propio: el plan no lo
  dicta y su regla de alcance (`plan.md:103-104`) prohíbe docstrings fuera de los dictados; la clase lo lleva. (b) el
  `assert_called_once_with(limit=20, offset=0, entity_name="Ghost", entity_id=None)` extra en
  `test_returns_empty_list_when_repository_has_no_rows` (`tests/test_audit.py:101-103`): lo exige AGENTS §5 (llamadas a
  mocks con argumentos), no cambia el nombre, el número de tests ni las cifras.
- AGENTS.md: capas respetadas (4 contratos KEPT); sin excepciones de dominio nuevas; mock con
  `create_autospec(..., instance=True)`; usuarios y cabeceras por fábricas; el test HTTP cumple ADR-0011 (el repositorio
  confirma con `commit()` antes de la petición, `audit_repository.py:16`); aserciones sobre código y estructura, ninguna
  sobre texto en español. `assert_is_admin_plus` queda sin llamadores en `app/` con sus tests
  (`tests/test_user_access_policy.py:287-312`), como prevé el plan (fase D).

## Auditoría Fase A — 2026-11-07

**Veredicto Fase A: PASS (0 bloqueantes, 2 opcionales).**

[OPCIONAL] — Fase A — El RED de herramienta del plan está mal contado: `grep -cE "^tests.test_fixtures_contract"` da `3` antes, no `2`, porque mypy añade una línea `note:` en `:59` que empieza por la misma ruta. Los errores son 2, como dice el plan (`:59 [call-arg]`, `:61 [attr-defined]`), y el `0` de después coincide. Es una imprecisión del comando del plan, no de la fase: el criterio de aceptación (2 errores → 0; `mypy tests` 16 → 14) se cumple. Para los RED de herramienta de las fases siguientes conviene filtrar con `error:` — evidencia: mypy sobre la copia de `bcc7c8c:tests/test_fixtures_contract.py` en el scratchpad da `:59: error: ... [call-arg]`, `:59: note: "send_verification_email" defined in "app.core.email"`, `:61: error: ... [attr-defined]` (3 líneas con el patrón); `plan.md:165-167`; `handoff-Fase_A.md`, "Desviaciones y dudas".
[OPCIONAL] — Fase A — Aviso de Git CRLF→LF en `progress.json`: es informativo y no exige ninguna acción. El blob commiteado está en LF (0 CR, 49 LF) y la copia de trabajo, en CRLF (49 CR) porque el editor la escribió así. `.gitattributes` (`* text=auto eol=lf`) normaliza al hacer `git add`, por eso `git status` sale limpio y el repositorio no lleva ningún CR. El JSON es válido — evidencia: `git ls-files --eol docs/deuda/BE-32/progress.json` → `i/lf w/crlf attr/text=auto eol=lf`; recuento de bytes de `git show HEAD:docs/deuda/BE-32/progress.json` → `CR 0, LF 49`; `json.load` correcto.

Puntos juzgados sin hallazgo:

- **Commit aparte `e51784e` (handoff y `progress.json`):** el protocolo lo exige así. `.claude/agents/fase-ejecutor.md:62-63`
  pide `git add docs/deuda/<ID>/progress.json docs/deuda/<ID>/handoff-<fase>.md` y
  `git commit -m "docs(progress): record <ID> <fase> completion"`. El mensaje coincide letra a letra, y el commit toca solo
  esos 2 archivos (`2 files changed, 128 insertions(+), 4 deletions(-)`). Hay precedente en `23af07b` (AF-02 Fase_B).
- **Commit de la fase `e7c814d`:** el mensaje es idéntico al de `plan.md:173-185` (`diff` vacío, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`).
  Toca solo `tests/test_fixtures_contract.py` (`1 file changed, 4 insertions(+), 3 deletions(-)`). El cuerpo coincide con
  los "Cambios exactos" (`double: Any = ...`, `assert double is mock_send_email`, `await double(recipient="x")`,
  `double.assert_not_called()`), y la docstring y la firma no cambian.
- **`progress.json`:** `Fase_A` está `completed` con `e7c814d`, un commit real. `current_target` = `Fase_B`, `last_handoff`
  existe, `edit_rules` no cambia respecto a `bcb7271` y quedan 8 fases.
- **RED reproducido:** `mypy tests` en HEAD da `Found 14 errors in 8 files (checked 18 source files)` y 0 líneas de
  `test_fixtures_contract`. Los 9 de `tests/` que quedan son los 5 de BE-32 de la fase B (`test_audit.py:72`,
  `test_user_service.py:65`, `:71`, `test_services.py:157`, `conftest.py:239`) y los 4 de A4 (`test_user_service.py:103`,
  `:197`, `:274`, `:292`). `pytest tests/test_fixtures_contract.py -q` da `9 passed`.
- **Compuerta (fila A):** `57 files already formatted` · ruff `Found 9 errors.` (8 I001 `:1:1` de `app/` +
  `tests\test_user_service.py:3:1`) · mypy `Found 5 errors in 4 files (checked 35 source files)` (`app\db\database.py:11`,
  `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`) ·
  `Contracts: 4 kept, 0 broken.` · `547 passed, 5 warnings` · `96.11%`. Coincide con la línea base
  (`verificacion.md:241-252`) y con el handoff. El rojo es exactamente el heredado (ADR-0005, decisión 5 del plan).
- **Archivo tocado:** `ruff check` → `All checks passed!`; `ruff format --check` → `1 file already formatted`; mypy no
  reporta ninguna línea del archivo.

## Auditoría Fase B — 2026-11-07

**Veredicto Fase B: PASS (0 bloqueantes, 2 opcionales).**

[OPCIONAL] — Fase B — Los "Cambios exactos" del plan no bastaban para cumplir P3 y el criterio `ruff check tests/` → `All checks passed!`. El ejecutor sacó `UserRole as SchemaUserRole` del bloque parentizado a su propia sentencia, en una línea (`tests/test_user_service.py:27`). Era necesario: con la configuración del repo, isort no combina imports con alias y los separa en otra sentencia. La edición es admisible sin enmienda. Es la mínima que exige un criterio de aceptación explícito del plan (P3 y E0, "P3 → sí"). Queda en el mismo bloque de imports que P3 asigna a la fase B, no cambia ninguna cifra y conserva A4 en 104/198/275/293, así que las tablas de B y D siguen valiendo. Además, se declaró en el handoff. Es una imprecisión del plan, no de la fase — evidencia: en una copia de `ddddb9d` en el scratchpad, con solo los cambios literales del plan (datetime ordenado, `typing.Any`, `-> Any`), `ruff check tests/test_user_service.py` da `tests\test_user_service.py:3:1: I001 ... Found 1 error.`. El `--isolated --select I --diff` propone `+from app.schemas.user import (\n     UserRole as SchemaUserRole,`. En esa copia, `diff` contra `d8848db:tests/test_user_service.py` solo difiere en la línea del alias. `pyproject.toml:72` `unfixable = ["I001"]` (por eso `--diff` no propone nada con la configuración del repo). En HEAD, `ruff check tests/` → `All checks passed!` y `ruff format --check` sobre los 4 `.py` tocados → `4 files already formatted`.
[OPCIONAL] — Fase B — El cuerpo del commit describe el diff de forma incompleta. «sort the datetime import (the only I001 in tests/)» no menciona la separación del alias, que también hizo falta para eliminar ese I001. El mensaje es el que dicta el plan letra a letra, y apartarse de él habría sido un bloqueante, así que no se corrige en el commit: la traza queda en `handoff-Fase_B.md` ("Desviaciones y dudas") y en `last_handoff` de `progress.json` («I001 also needed the alias import split»). Lo demás del cuerpo sí es fiel: pyproject, conftest, test_services, `-> Any` y «mypy goes from 5 to 9» — evidencia: `diff` entre `plan.md:209-227` (con `<MODELO EJECUTOR>` → `Claude Opus 5.5`) y `git log -1 --format=%B d8848db` → idénticos; el `git show d8848db -- tests/test_user_service.py` incluye `-    UserRole as SchemaUserRole,` / `+from app.schemas.user import UserRole as SchemaUserRole`.

Puntos juzgados sin hallazgo:

- **Fixtures `-> Any` (`user_repo`, `audit_service`, `audit_repo`):** es lo que dicta el plan, letra a letra (`plan.md:196-199`:
  `def audit_repo(self) -> Any:`, `def user_repo() -> Any:`, `def audit_service() -> Any:`). También cumple la adenda 3
  (`verificacion.md:290`, «anotan el retorno de `create_autospec`»): `create_autospec` devuelve `Any`, y anotarlo así
  quita el `no-any-return` sin mentir sobre el tipo. Es la forma que ya usa el repo (`tests/test_token_failure_paths.py:58`,
  `def user_repo() -> Any:`). Los dobles siguen siendo `create_autospec(..., instance=True)`: el diff solo toca las
  anotaciones y ninguna aserción.
- **Commit `d8848db`:** el mensaje es idéntico al del plan. Toca exactamente los 5 archivos de la fase
  (`5 files changed, 11 insertions(+), 8 deletions(-)`: `pyproject.toml`, `conftest.py`, `test_audit.py`,
  `test_services.py`, `test_user_service.py`). Todos los puntos de "Cambios exactos" están en el diff: `pyproject.toml:94`
  con `"tests"`, `conftest.py:235` `user: User = ...`, `typing.Any` en `test_services.py` entre `decimal` y
  `unittest.mock` con `update_payload: dict[str, Any]` (`:139`), `typing.Any` en `test_audit.py:1` con `audit_repo -> Any`,
  y `datetime` ordenado, `Any` en la línea 4 y los dos fixtures en `test_user_service.py`.
- **RED reproducido (solo `pyproject.toml` cambiado):** copia de `ddddb9d` con el `pyproject.toml` de `d8848db`, en el
  scratchpad: `Found 14 errors in 8 files (checked 53 source files)`. Son los 5 de `app/`, los 4 de A4
  (`test_user_service.py:103,197,274,292`) y los 5 de BE-32 (`test_audit.py:72`, `test_user_service.py:65,71`,
  `test_services.py:157`, `conftest.py:239`). Coincide con el plan y con el handoff.
- **Compuerta (fila B), reejecutada en HEAD `338bc40`, exit 1:** `57 files already formatted` · ruff `Found 8 errors.`
  (solo los 8 I001 `:1:1` de `app/`: `api/dependencies.py`, `api/routers/audit.py`, `core/email.py`, `db/database.py`,
  `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`, `services/user_service.py`) · mypy
  `Found 9 errors in 5 files (checked 53 source files)` (`app\db\database.py:11`, `app\core\security.py:71`, `:87`,
  `app\services\user_service.py:124`, `app\api\dependencies.py:95`, `tests\test_user_service.py:104`, `:198`, `:275`,
  `:293`) · `Contracts: 4 kept, 0 broken.` · `547 passed, 5 warnings` · `96.11%`. Las 4 líneas de `tests/` son las de
  `SECRET_KEY` (`grep -n SECRET_KEY`: 104 y 198 `jwt.decode`, 275 y 293 `SECRET_KEY,`), es decir, el conjunto de A4
  identificado por contenido, en las líneas de la tabla de la decisión 5 (P2). Ruff baja de 9 a 8 y mypy sube de 5 a 9
  y el aumento de mypy es exactamente ese conjunto (excepción a ADR-0005). El rojo no bloquea.
- **Archivos tocados:** `ruff check` sobre los 5 → `All checks passed!`. Con `mypy` sobre los 4 `.py`, ninguna línea de
  `conftest.py`, `test_services.py` ni `test_audit.py`; en `test_user_service.py` solo salen los 4 de A4.
- **`progress.json`:** `Fase_B` está `completed` con `d8848db`, un commit real. `current_target` = `Fase_C`,
  `last_handoff` existe y `edit_rules` no cambia respecto a `bcb7271`. Quedan 8 fases y el JSON es válido. El commit
  `338bc40` toca solo `handoff-Fase_B.md` y `progress.json`, con el mensaje del protocolo. Árbol limpio.
- **Handoff:** pega el RED, el RESUMEN y las cifras de la compuerta, que coinciden con las de esta auditoría (salvo el
  tiempo de pytest). La nota del hook (F401 borra `from typing import Any` si se añade antes que su uso) es informativa.

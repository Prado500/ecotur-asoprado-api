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

## Auditoría Fase C — 2026-11-07

**Veredicto Fase C: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase C — El RED de los ids está mal contado en el plan. `grep -cE "year-by-monotony|year-resets-per-table|year-jump" tests/test_check_docs.py` da `3` antes, no `2` («2 líneas, 4 ids»). Los 4 ids viven en 3 líneas, y el propio plan cita `:1039` y `:1089-1090`, que son 3. Es una imprecisión del comando del plan, como la de la fase A, no un fallo de la fase: el objetivo (`0`) y los 4 renombrados coinciden, y el ejecutor lo declaró en el handoff — evidencia: `git show 5979b07^:tests/test_check_docs.py | grep -nE "year-by-monotony|year-resets-per-table|year-jump"` → `1039:` (dos ids), `1089:`, `1090:`; en HEAD el mismo `grep -cE` da `0`; `plan.md:237-239,250`; `verificacion.md` («ids de `test_check_docs.py` … → `:1039,1089-1090`»); `handoff-Fase_C.md`, "Desviaciones y dudas" 1.

Puntos juzgados sin hallazgo:

- **Lista `ids=` de `test_r7_flags_closed_row_without_mark` en una línea por elemento (`+8 −3`):** es admisible. El plan dice
  que «el corte de línea es el que deje `ruff format` (100 columnas)» (`plan.md:148-149`). En una sola línea, la lista con
  los nombres nuevos mide 110 columnas, así que `ruff format` la abre con coma final. `ruff format --check tests/` →
  `18 files already formatted`. El contenido de la lista es el del plan: mismos 4 ids y en el mismo orden.
- **Nombres de los ids:** son los 4 que dicta el plan, letra a letra (`plan.md:237-239`). Describen bien cada caso según
  `_date_near` (`scripts/check_docs.py:757`, «year that leaves it nearest to `anchor`»), con la versión del plan del test el
  31 oct 2026:
  `year-nearest-to-version` (2 ene sin marca, hoy 5 ene 2027: el año más cercano a la versión es 2027, la fila es pasada
  y R7 la marca); `year-nearest-in-each-table` (tras una tabla que cruza a enero, el `2 nov` de la tabla siguiente vuelve
  a 2026; el año no se arrastra entre tablas); `new-year-rows-marked` (31 dic y 2 ene marcados, aceptados);
  `new-year-row-in-future` (2 ene sin marca, hoy 31 dic 2026: la fila es de 2027, futura, aceptada). `--collect-only`
  lista los 4 ids nuevos; `pytest tests/test_check_docs.py -q` → `257 passed`, igual que antes (handoff).
- **`tests\conftest.py:85 override_get_db` sigue en el patrón AST de `Yields:`:** el plan lo excluye a propósito; no es un
  residuo. Fase C, "Fuera de alcance": «`override_get_db` (función anidada)» (`plan.md:253-254`). Patrón 7 de la
  verificación: «Queda fuera `override_get_db` (`conftest.py:76`), que es una función anidada y no un fixture público».
  La adenda 3 (`verificacion.md:291`) pide `Yields:` en `conftest.py:34`, `:89` y `test_email.py:43`, además de los dos
  de la fila (`:51`, `:62`), y no en `:76`. La verificación final del plan (`plan.md:643-645`) espera exactamente esa
  línea como única salida: `tests\conftest.py:86 override_get_db`. La 85 de hoy (76 + 9 de los tres `Yields:` de encima)
  pasa a 86 con el `from datetime import timedelta` de la fase G (`plan.md:76-77,451`). El AST da hoy
  `tests\conftest.py:85 override_get_db` y `tests\test_email.py:43 send_message`, que es de la fase H. Las 4 líneas que
  pide el criterio de aceptación (34, 51, 62, 89) ya no salen.
- **Comentario en `test_audit.py:22`, no en `:21`:** el plan lo cita como «`:21` en la base», y en `fd144ad` está en la 21.
  La fase B añadió `from typing import Any` en la línea 1, así que en `5979b07^` el comentario estaba en la 22. El diff lo
  cambia por el texto dictado, letra a letra. El patrón 5 de la verificación final da `0`.
- **Commit `5979b07`:** el mensaje es idéntico al de `plan.md:257-272`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`. El
  `diff` solo difiere en el salto final que añade `git log --format=%B`. Toca exactamente los 5 archivos de la fase
  (`5 files changed, 23 insertions(+), 6 deletions(-)`). Todos los "Cambios exactos" están en el diff:
  `from sqlalchemy import select` en `test_services.py:15` y `test_user_access_policy.py:14`; el comentario; los 4 ids; y
  los 4 `Yields:` con línea en blanco, 3 líneas cada uno y el texto del plan letra a letra. No cambia ninguna aserción.
  `git diff --stat fd144ad -- app/` sale vacío.
- **RED → 0:** `grep -rn "sqlalchemy.future" tests/` → `0`; patrón 5 (comentario en español) → `0`; ids → `0`.
- **Compuerta (fila C), reejecutada en HEAD `755fa3e`, exit 1:** `57 files already formatted` · ruff `Found 8 errors.`
  (solo los 8 I001 `:1:1` de `app/`) · mypy `Found 9 errors in 5 files (checked 53 source files)` (`app\db\database.py:11`,
  `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`,
  `tests\test_user_service.py:104`, `:198`, `:275`, `:293`) · `Contracts: 4 kept, 0 broken.` · `547 passed, 5 warnings` ·
  `96.11%`. Las 4 líneas de `tests/` son las de `SECRET_KEY` (104 y 198 en `jwt.decode`, 275 y 293 en `SECRET_KEY,`): el
  conjunto de A4, sin moverse, porque la fase no toca ese archivo. Coincide con la fila C, con la línea base y con el
  handoff, salvo el tiempo de pytest.
- **Archivos tocados:** `ruff check` sobre los 5 → `All checks passed!`. `mypy` sobre los 5 solo imprime los 5 de `app/` que
  sigue por las importaciones (A4), ninguno en `tests\`.
- **`progress.json`:** `Fase_C` está `completed` con `5979b07`, un commit real. `current_target` = `Fase_D`, `last_handoff`
  existe y declara la desviación del RED, y `edit_rules` no cambia respecto a `bcb7271`. Quedan 8 fases y el JSON es
  válido. El commit `755fa3e` toca solo `handoff-Fase_C.md` y `progress.json`, con el mensaje del protocolo. Árbol limpio.

## Auditoría Fase D — 2026-11-07

**Veredicto Fase D: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase D — El criterio de aceptación del plan pide 0 en el patrón 1, pero el propio plan deja fuera la línea que queda. `grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ --include=*.py` da `1` (`tests/test_email.py:99: send_message.assert_awaited_once()`), no `0`. La base tiene 11 (`git grep … fd144ad -- tests/`: 10 en los 4 archivos de la fase más `test_email.py:99`). El plan saca esa línea del alcance de D («`test_email.py:99` (fase H)»), el commit que dicta dice «Ten assertions», y la "Verificación final" pone el 0 tras H, donde E0 punto 4 cambia `:99`. Por tanto, el error es del criterio del plan, no de la fase. Ninguna de las 10 aserciones de la fase sigue sin argumentos, y el ejecutor lo dejó declarado — evidencia: `plan.md:315-318`, `plan.md:323`, `plan.md:623-624`, `plan.md:737-744`; `handoff-Fase_D.md`, "Desviaciones y dudas" 1. El patrón 1b da `0`, como pide el plan.

Puntos juzgados sin hallazgo:

- **Líneas +1 (`:122→:123`, `:219→:220`, `:486→:487`, `test_audit.py:87→:88`):** no hay desviación. El plan escribe
  «Cambios exactos (líneas de la base)» (`plan.md:277`), y en `fd144ad` cada línea citada tiene el contenido citado:
  `test_user_service.py:122` `assert_not_awaited()`, `test_services.py:219` y `:486` `upload_image.assert_awaited_once()`,
  `test_audit.py:87` `assert_not_awaited()`. En `eb68510` (antes de D) las mismas líneas están en la +1, por el
  `from typing import Any` de la fase B en esos tres archivos. `test_storage.py` (92/159/189/198) no se movió porque B no
  lo tocó. El diff cambia exactamente esas líneas.
- **Tabla de mutantes, reproducida entera** en una copia desechable (`git archive 8eb71d4 app tests pyproject.toml` en
  el scratchpad, con variables de entorno ficticias). `app.__file__` apuntaba a la copia. Script
  `scratchpad/mut_run.py`: cada mutante se aplica con un `assert` sobre el texto original y luego se restaura. "Antes" =
  los 4 archivos de `eb68510`, "después" = los de `8eb71d4`. Sin mutar: `73 passed` en los dos casos. Resultados:
  MU1 `19 passed` → `1 failed, 18 passed` (`test_register_tourist_returns_registration_result`); MU2 `19 passed` →
  `1 failed, 18 passed` (`test_create_administrative_account_provisions_admin`); MS1 `18 passed` → `1 failed, 17 passed`
  (`test_promote_happy_path_copies_synchronously_then_deletes`); MS2 `18 passed` → `2 failed, 16 passed`
  (`test_delete_image_deletes_blob_by_name`, `test_delete_image_swallows_sdk_failure`); MR1 `1 failed, 35 passed` (503)
  → `2 failed, 34 passed` (503 y `test_upload_images_non_image_returns_415`). Coincide fila a fila con el plan
  (`plan.md:307-313`) y con el handoff. Después, `git status --short` sale vacío y `git diff --quiet -- app` sale con 0.
- **Los tres `delete_blob.assert_awaited_once_with()` vacíos:** son los que dicta el plan (`plan.md:303`). No son vacuos,
  porque `_with()` exige que la llamada no lleve argumentos y `app/core/storage.py:154` y `:202` llaman a
  `delete_blob()` sin ellos. Matan MS1 y MS2 (medido arriba). El doble es `create_autospec(BlobServiceClient, …)`
  (`tests/test_storage.py:59`), así que el mutante con `delete_snapshots=` respeta la firma y solo falla la aserción.
- **`test_services.py`:** conserva `staged = ….call_args.args[0]` + `isinstance(staged, StagedImage)` y borra las
  aserciones campo a campo (3 en el 503, 1 en el 415), como dicta `plan.md:291-295` («se quedan :220-221 … se borran
  :222-224»; «se quedan :487-488 y se borra :489»). El `StagedImage(...)` posicional sigue el orden de campos de la
  `NamedTuple` (`filename`, `content_type`, `content`; `app/core/storage.py:16`, `app/api/routers/service.py:75-78`).
  Las capturas por posición que quedan (`:223`, `:489`) son las de los Residuales del plan; allí se citan como `220,487`
  (líneas de antes de D) y el handoff ya da las nuevas.
- **`create_user.assert_awaited_once_with(created_user)` con `created_user = call_args.args[0]`**
  (`test_user_service.py:330,335`): compara el argumento consigo mismo, así que solo fija que hubo una llamada y con un
  único argumento posicional. Es el texto que dicta el plan (`plan.md:288`). Lo que importa son los campos (`:331-333`)
  y `log_transaction`. No es un hallazgo.
- **`ContentSettings(content_type="image/jpeg")`:** compara por igualdad real, ni tautológica ni frágil. En la versión
  instalada (azure-storage-blob 12.30.0), `DictMixin.__eq__` devuelve `isinstance(other, self.__class__) and
  self.__dict__ == other.__dict__`. Medido: `== ContentSettings(content_type="image/jpeg")` → `True`;
  `== …("image/png")` → `False`; `== …("image/jpeg", cache_control="x")` → `False`. `__dict__` contiene los 6 campos
  (`content_type`, `content_encoding`, `content_language`, `content_md5`, `content_disposition`, `cache_control`), así
  que la aserción también falla si `storage.py:127` empieza a rellenar otro campo. No es frágil: los dos lados salen del
  mismo constructor de la misma versión.
- **Edición de `test_storage.py` con `sed`, sin hook:** los 4 archivos tocados están limpios.
  `ruff format --check` → `4 files already formatted`; `ruff check` → `All checks passed!`;
  `git diff --check 8eb71d4^ 8eb71d4` → sin salida; `git ls-files --eol` → `i/lf w/lf` en los 4. `mypy` sobre los 4 →
  `Found 9 errors in 5 files (checked 4 source files)`, todos de A4 (los 5 de `app/` entran por los imports).
- **Conjunto de A4 por contenido y línea (decisión 5, E0-P2):** `tests\test_user_service.py:105`
  `jwt.decode(result.verification_token, SECRET_KEY, …)`, `:203` `jwt.decode(result.access_token, SECRET_KEY, …)`,
  `:280` y `:298` `SECRET_KEY,`. Son las líneas de la columna «Tras D» (`plan.md:40-45`). Ni sobra ni falta un error.
- **Commit `8eb71d4`:** el mensaje es idéntico a `plan.md:321-339`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`. Solo
  difiere el salto final de `git log --format=%B`. Toca exactamente los 4 archivos de la fase
  (`4 files changed, 29 insertions(+), 20 deletions(-)`); `app/` y `pyproject.toml` no cambian. Están todos los
  "Cambios exactos": `AuditAction` entre `app.core.security` y `app.models.user`; `create_user` y `log_transaction` con
  argumentos en los dos tests, con coma final y `changes={"role": "admin"}`; el `assert_not_awaited` redundante borrado
  en `test_user_service.py` y en `test_audit.py`; `ContentSettings` entre `azure.core.exceptions` y
  `azure.storage.blob.aio`; `upload_blob` con la forma dictada; los 3 `delete_blob`.
- **Compuerta (fila D), reejecutada en HEAD `872e0ae`, exit 1:** `57 files already formatted` · ruff `Found 8 errors.`
  (solo los 8 I001 `:1:1` de `app/`) · mypy `Found 9 errors in 5 files (checked 53 source files)` ·
  `Contracts: 4 kept, 0 broken.` · docs coherentes · `547 passed, 5 warnings` · `TOTAL 943 23 138 19 96.11%`. Coincide
  con la fila D, con la línea base (cobertura 96.11 %) y con lo que pegó el ejecutor, salvo el tiempo de pytest.
- **`progress.json`:** `Fase_D` está `completed` con `8eb71d4`, un commit real. `current_target` = `Fase_E`,
  `last_handoff` existe y declara la desviación del patrón 1, y `edit_rules` no cambia. El JSON es válido. El commit
  `872e0ae` toca solo `handoff-Fase_D.md` y `progress.json`. Árbol limpio.
- **AGENTS §5:** los dobles siguen con autospec. Ninguna aserción nueva lee texto en español: los valores (`"1005911792"`,
  `"5555555555"`, nombres de fichero, MIME) son entradas del propio test. No es la última fase, así que no toca la
  "Verificación final".

## Auditoría Fase E — 2026-11-07

**Veredicto Fase E: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase E — La tabla de G1 del handoff y el `last_handoff` de `progress.json` no miden el estado commiteado, sino uno intermedio: los tests de `a861358` (el archivo, con las 3 copias, tiene 77 casos; la suite, 547) más el test nuevo copiado encima. De ahí sale «después» `1 failed, 77 passed` / `1 failed, 547 passed` (78 y 548 casos), y no 75 y 545. La salida literal del handoff sí lo dice («después, suite (copia con el test nuevo y aún con las 3 copias HTTP)»), pero la cabecera de la tabla y `last_handoff` lo presentan sin esa salvedad. No afecta al criterio de aceptación: el plan no da cifras para G1, solo «sin el test nuevo, el archivo y la suite pasan enteros; con él, `1 failed` (el test nuevo) y el resto passed» (`plan.md:373-375`). Medir con las copias aún presentes muestra además que ninguna de ellas mataba G1. Re-medido sobre `11f2f17` en una copia desechable, con resultado conforme al plan: sin mutar, `75 passed` / `545 passed, 5 warnings`; G1 sin el test nuevo (`--deselect`), `74 passed, 1 deselected` / `544 passed, 1 deselected, 5 warnings`; G1 con él, `1 failed, 74 passed` / `1 failed, 544 passed, 5 warnings`, y el único FAILED es `TestAssertCanUpdate::test_role_guard_for_non_superadmins_runs_before_the_self_role_guard` (`tests\test_user_access_policy.py:220`, la aserción `==`) — evidencia: `handoff-Fase_E.md`, «RED: mutante G1» (tabla y salida literal); `progress.json` `last_handoff`; la re-medición de esta auditoría (`git archive 11f2f17 | tar -x` en el scratchpad).

Puntos juzgados sin hallazgo:

- **Las tres copias borradas** son exactamente las de la adenda 4 y de `plan.md:33-34,348-349`. En `a861358` (y en `fd144ad`)
  están en `test_user_access_policy.py:314` (`test_patch_hierarchy_violation_returns_403_detail`), `:384`
  (`test_admin_cannot_provision_admin_account_403_and_no_db_mutation`) y `:412` (`test_admin_update_tourist_persists_mutation`).
  El diff borra esas tres funciones enteras y nada más de la sección HTTP. Comparación con sus pares de `test_auth.py`:
  - Patch a superadmin. La copia afirmaba `403`, `"detail" in json()` y `first_name == "John"` (un literal).
    `test_admin_patching_superadmin_returns_403_without_mutation` (`test_auth.py:262`) afirma `403`,
    `set(body) == {"detail"}`, `isinstance(detail, str)`, `refresh` y `first_name == original_first_name`. El par es más
    fuerte.
  - Admin que da de alta a un admin. La copia afirmaba `403`, `"detail" in` y una sola fila, la del admin.
    `test_admin_provisioning_admin_returns_403_without_row` (`:361`) ya afirmaba `set(body) == {"detail"}` y `isinstance`,
    y ahora hereda `len(users) == 1` y `users[0].cedula == admin.cedula`. Queda más fuerte que la copia.
  - Admin que corrige el email de un turista. La copia afirmaba `200`, el email en el cuerpo, `refresh` y el email
    persistido. `test_admin_updates_tourist_email_and_persists_it` (`:242`) afirma lo mismo, así que la fuerza es igual.
  Los tres pares recorren las mismas rutas y el mismo camino de `app/`, y la cobertura no se mueve (ver abajo).
- **Aserción heredada (`test_auth.py:388-390`).** Sustituye `select(func.count()).select_from(User)` +
  `scalar_one() == 1` por las tres líneas dictadas en `plan.md:345-347`, iguales a las de la copia
  (`a861358:tests/test_user_access_policy.py:407-409`). `func` sigue usándose en `test_auth.py:67` y `select` en `:47`,
  `:67`, `:388` y `:421`, así que `from sqlalchemy import func, select` (`:6`) no cambia. En `test_user_access_policy.py`,
  `User` queda sin uso y el import pasa a `from app.models.user import UserRole`, como dicta el plan. El hook lo quitó
  (F401), y el handoff lo declara. `select` sigue usándose ahí (`:448` y siguientes, sobre `AuditLog`).
- **Test G1** (`test_user_access_policy.py:201-221`, al final de `TestAssertCanUpdate`, justo antes de
  `class TestAssertCanRecover`). Docstring y cuerpo son literales a `plan.md:353-371`. Lo único que cambia es la firma, que
  `ruff format` parte en tres líneas, como el plan permite. Mata el mutante sin leer texto: compara `.detail` con
  `.detail` (`==` entre «admin, su propio rol» y «admin, rol de otro»; `!=` contra «superadmin, su propio rol»). Con G1, el
  primer caso cae en la guarda de auto-rol y falla el `==` (`:220`). La re-medición lo confirma. Que falle prueba también
  que `make_user` da cédulas distintas a `admin` y `tourist`: si fueran iguales, los dos casos serían auto-update y el
  mutante sobreviviría.
- **Mutante aplicado** (`scratchpad/tools/mutate_g1.py`): `assert` por contenido de que `:66` es la guarda
  `actor.role != UserRole.superadmin` y `:71` la de `is_self_update and "role"`. Después intercambia `:66-69` y `:71-72`.
  `app.services.user_access_policy.__file__` resolvía a la copia. Después: `git status --short` vacío y
  `git diff --quiet -- app` con exit 0 en el repo.
- **Cobertura y `app/`.** Compuerta reejecutada: `TOTAL 943 23 138 19 96.11%`, igual que la línea base y que la fila D
  (`a861358`, con las copias). Como los totales de líneas y ramas sin cubrir son idénticos, borrar las copias no
  descubrió nada. `git diff --stat fd144ad -- app/` sale vacío (0 líneas de diff), así que la fase F será la primera en
  tocar `app/`.
- **Compuerta (fila E), reejecutada en HEAD `0ba3050`, exit 1:** `57 files already formatted` · ruff `Found 8 errors.`
  (solo los 8 I001 `:1:1` de `app\`: `api\dependencies.py`, `api\routers\audit.py`, `core\email.py`, `db\database.py`,
  `repositories\user_repository.py`, `schemas\audit.py`, `services\audit_service.py`, `services\user_service.py`) ·
  mypy `Found 9 errors in 5 files (checked 53 source files)`, con los 5 de `app/` y `tests\test_user_service.py:105`,
  `:203`, `:280` y `:298` (el conjunto de A4 de la decisión 5 y E0-P2, ni uno más) · `Contracts: 4 kept, 0 broken.` ·
  docs coherentes · `545 passed, 5 warnings` · cobertura 96.11 %. Coincide con la fila E (`plan.md:143`) y con lo que
  pegó el ejecutor, salvo el tiempo de pytest. En los archivos tocados: `ruff check` da `All checks passed!` y
  `ruff format --check` da `2 files already formatted`. mypy sobre los dos da
  `Found 5 errors in 4 files (checked 2 source files)`: todos de `app/`, que entra por import, y ninguno en los archivos
  tocados. `git diff --check` no da salida.
- **Criterio de aceptación** (`plan.md:376-380`): 547 − 3 + 1 = 545. Los greps del criterio dan: copias en la política,
  `0`; pares en `test_auth.py`, `3`; cédula heredada, `tests/test_auth.py:1` y `tests/test_user_access_policy.py:0`;
  patrón 8 (G1), `1`.
- **Commit `11f2f17`:** el mensaje es idéntico a `plan.md:384-399`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`. Solo
  difiere el salto final de `git log --format=%B`. Toca exactamente los 2 archivos de la fase
  (`2 files changed, 26 insertions(+), 71 deletions(-)`).
- **`progress.json`:** `Fase_E` está `completed` con `11f2f17`, un commit real. `current_target` = `Fase_F`, existe
  `last_handoff`, `edit_rules` no cambia y el JSON es válido. El commit `0ba3050` toca solo `handoff-Fase_E.md` y
  `progress.json`. El árbol está limpio.
- **AGENTS §5:** el test nuevo usa `make_user` y `policy`, no usa mocks, está en inglés y con docstring, y no lee texto en
  español. No es la última fase, así que no toca la "Verificación final".

## Auditoría Fase F — 2026-11-07

**Veredicto Fase F: PASS (0 bloqueantes, 3 opcionales).**

[OPCIONAL] — Fase F — El criterio de aceptación pide que «el `git diff` de `app/` se limita a esas 2 líneas de docstring» (`plan.md:426`), y el patrón 10 de la verificación final espera `1 file changed, 2 insertions(+)` (`plan.md:663`). El diff real tiene **3** líneas, y el corte a 3 era necesario. El texto dictado (173 caracteres) no cabe en 2 líneas con sangrías de 12 y 16 a 100 columnas: con el corte del plan, la segunda línea mide 103 (E501, que está activo: `pyproject.toml:60,66`), y ningún corte por espacio deja las dos líneas en ≤ 100 (prueba exhaustiva de todos los cortes: 0 válidos). El contenido es el dictado letra a letra: unido, el texto de `service_repository.py:89-91` es `==` al de `plan.md:416-417`. Aplica la regla general del plan: «los bloques de código dictan el contenido exacto; el corte de línea es el que deje `ruff format` (100 columnas)» (`plan.md:148-149`). En rigor el corte no lo impone `ruff format`, que no rehace docstrings, sino E501 de `ruff check`, pero el espíritu de la regla es ese. Es un error de medida del plan, no una desviación del ejecutor, y no exige enmienda para dar PASS a F. Para que la auditoría de H no lo lea como un apartamiento, el patrón 10 debe leerse `1 file changed, 3 insertions(+)`; David decide si lo deja escrito como E2 o como nota de cierre. El ejecutor lo declaró en «Desviaciones y dudas», punto 1. Una errata menor del handoff: el texto mide 173 caracteres, no 174; la conclusión no cambia — evidencia: `git diff --stat fd144ad -- app/` → `1 file changed, 3 insertions(+)`; anchos de `service_repository.py:89-91` = 97/94/24; el corte del plan da 97/103.

[OPCIONAL] — Fase F — `assert saved.deleted_at == deleted_at.replace(tzinfo=None)` (`tests/test_service_repository.py:96`) es correcta hoy, pero solo en SQLite. La columna es `DateTime(timezone=True)` (`app/models/service.py:45`). En Postgres con asyncpg, un `timestamptz` vuelve como `datetime` *aware* (`2026-01-15 12:00+00:00`), y en Python `==` entre un *aware* y un *naive* devuelve `False` sin lanzar excepción. Con BE-31 (suite sobre Postgres) el test fallaría aunque `save_service` fuera correcto. No es un hallazgo contra la fase: el plan dicta esa aserción y ese comentario letra a letra (`plan.md:411-412`), la suite corre solo en SQLite (ADR-0011) y el comentario `# SQLite returns the column without its time zone.` deja la dependencia a la vista. Destino: nota en la fila BE-31. Alternativa portable, que también mata M10: `assert saved.deleted_at is not None` seguido de `assert saved.deleted_at.replace(tzinfo=saved.deleted_at.tzinfo or UTC) == deleted_at`. Con SQLite, al *naive* se le pone UTC, que es lo que se guardó. Con Postgres, el *aware* se deja como está y se comparan instantes — evidencia: `tests/test_service_repository.py:95-96`; `app/models/service.py:45`; `docs/backlog.md:69` (BE-31).

[OPCIONAL] — Fase F — El docstring nuevo de `test_save_service_commits_pending_changes_and_returns_the_row` («…and the row returned is this id's of two.», `tests/test_service_repository.py:51`) es el dictado letra a letra (`plan.md:407`), pero se lee mal. «this id's» es un posesivo elíptico sin sustantivo y «of two» queda colgando: se entiende solo si ya se sabe que hay una fila vecina. Una redacción más clara sería «…and of the two rows, the one returned has this id.». Cambiarlo ahora sería apartarse del plan, así que queda para el cierre o para quien retoque el archivo — evidencia: `tests/test_service_repository.py:51`; `plan.md:407`.

Puntos juzgados sin hallazgo:

- **`app/` en todo el ítem (decisión 7).** `git diff fd144ad -- app/` contiene solo el hunk `@@ -86,6 +86,9 @@` de
  `app/repositories/service_repository.py`: tres líneas `+` dentro de `Raises:`, tras `NoResultFound`, y ninguna línea de
  código. `grep -c "StaleDataError" app/repositories/service_repository.py` = `1` (patrón 9b-B).
- **Tests literales al plan.** Cada cadena dictada aparece tal cual: la vecina
  `await _persist(db_session, _package(name="Paquete Vecino De Prueba"))` 2 veces (las dos pruebas que devuelven fila,
  después de `package`); los 3 docstrings, el comentario de SQLite y la aserción exacta, 1 vez cada uno. El test de
  borrado físico solo cambia de docstring. Las vecinas usan las fábricas locales `_package`/`_persist`; no hay dobles
  nuevos. Nada en español salvo el dato de la vecina, que no se afirma.
- **M5 y M10 se matan sin leer texto.** M5 muere por la excepción `MultipleResultsFound` de `scalar_one()` (tipo, no
  mensaje). M10 muere por la igualdad de `datetime`. Ninguna aserción lee un `detail` ni un texto en español.
- **Tabla de mutantes re-medida sobre `8b2cfe2`.** Copia `git archive 8b2cfe2 | tar -x` en el scratchpad (`cmp` idéntico
  con `8b2cfe2:` para los 2 archivos de la fase). Mutantes por contenido dentro de `save_service`; restauración byte a byte
  comprobada con `assert`; el árbol de trabajo no se tocó. Coincide con el handoff cifra a cifra:
  - archivo, después: sin mutar `5 passed`; M5 `2 failed, 3 passed` (`…commits_pending_changes_and_returns_the_row` y
    `…returns_a_soft_deleted_row`); M10 `1 failed, 4 passed` (`…returns_a_soft_deleted_row`).
  - suite, después: `545 passed, 5 warnings`; M5 `2 failed, 543 passed, 5 warnings`; M10 `4 failed, 541 passed, 5 warnings`.
  - antes (copia de `2af510a`): archivo `5 passed` sin mutar, con M5 y con M10, igual que la columna «Antes» del plan;
    suite: M5 `545 passed`, M10 `3 failed, 542 passed, 5 warnings`.
  - **M10 ya lo detectaba la suite antes de la fase**, con 3 tests de `test_services.py`:
    `test_deactivate_and_activate_package`, `test_soft_delete_and_recover` y
    `test_update_package_concurrent_reconciliation`. La fase añade que el archivo del repositorio lo detecta por sí
    mismo. Lo declara el handoff (punto 2).
  - Las cifras de M5 y M10 son las del estado commiteado (545 casos). Desaparece la salvedad del opcional de la fase E.
- **Compuerta (fila F), reejecutada en HEAD `3607798`, exit 1.** `57 files already formatted`; ruff `Found 8 errors.`,
  solo los 8 I001 `:1:1` de `app\` (`api\dependencies.py`, `api\routers\audit.py`, `core\email.py`, `db\database.py`,
  `repositories\user_repository.py`, `schemas\audit.py`, `services\audit_service.py`, `services\user_service.py`), sin
  `service_repository.py`. mypy `Found 9 errors in 5 files (checked 53 source files)`: `app\db\database.py:11`,
  `app\core\security.py:71` y `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95` y
  `tests\test_user_service.py:105`, `:203`, `:280` y `:298`, los 4 `[arg-type]` `str | None` de `SECRET_KEY`. Es el
  conjunto de A4, ni uno más. Además: `Contracts: 4 kept, 0 broken.`, docs coherentes, `545 passed, 5 warnings`,
  `TOTAL 943 23 138 19 96.11%` (igual que la línea base). Coincide con la fila F (`plan.md:144`) y con lo que pegó el
  ejecutor. En los archivos tocados: `ruff check` da `All checks passed!` y `ruff format --check` da
  `2 files already formatted`. mypy da 1 error, `app\db\database.py:11` (A4, entra por import), y ninguno en ellos.
  `git diff --check 2af510a 8b2cfe2` no da salida.
- **Commit `8b2cfe2`.** El mensaje es idéntico a `plan.md:431-445`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`. Toca
  exactamente los 2 archivos de la fase (`2 files changed, 10 insertions(+), 4 deletions(-)`).
- **`progress.json`.** `Fase_F` está `completed` con `8b2cfe2`, un commit real. `current_target` = `Fase_G`, el
  `last_handoff` es nuevo y declara las 3 líneas, `edit_rules` no cambia y el JSON es válido. `3607798` toca solo
  `handoff-Fase_F.md` y `progress.json`. El árbol está limpio.
- No es la última fase: la «Verificación final» completa queda para H. Los patrones 9b-B (`1`) y 10 (`3 insertions`,
  ver el primer opcional) se adelantaron aquí.

## Auditoría Fase G — 2026-11-07

**Veredicto Fase G: PASS (0 bloqueantes, 2 opcionales).**

[OPCIONAL] — Fase G — La cifra de suite de D17 en la tabla del plan (`suite: 1 failed`) parte de una premisa falsa: D17 ya moría en la suite antes de la fase, por el camino del login. La tabla define sus cifras **por archivo**: el encabezado dice «el archivo tiene 11 casos antes y 14 después», y todas las celdas «Antes» son `11 passed`, la cuenta del archivo. Solo D17 (y U8) añaden una nota de suite. Las celdas de archivo coinciden todas. La nota de suite de D17 sale de `docs/deuda/BE-33/gaps.md:144` («`432 passed`»), pero `test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login` (`bf22982`, ancestro de `948f539`) ya lo detectaba en el login: `tests/test_auth.py:167-168`, porque con D17 `authenticate_user` encuentra la fila borrada y responde `AccountNotActiveError`, no 401. Lo que la fase añade es la detección por `get_current_user`, que ningún otro test cubre. El mensaje de commit dictado («a lookup that ignored deleted_at survived») solo es exacto para ese camino. Ni el ejecutor ni la implementación se apartaron del plan, y el ejecutor lo declaró (handoff, «Desviaciones y dudas» 1). No es bloqueante. Destino: nota de cierre (enmienda o Residuales), corrigiendo también la cifra de BE-33 — evidencia: re-medido en el scratchpad (`git archive` de `b070f55` y `dd88bf8`): D17 antes, archivo `11 passed`, suite `1 failed, 544 passed` (`test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login`); después, archivo `1 failed, 13 passed`, suite `2 failed, 546 passed` (ese test y `test_token_for_soft_deleted_active_user_returns_401`); `plan.md:501,508`.
[OPCIONAL] — Fase G — El docstring de `_bearer` («Builds the Authorization header for a token the factories cannot produce.», `tests/test_token_failure_paths.py:45`) ha quedado obsoleto. `test_expired_token_on_protected_route_returns_401` le pasa ahora un token de la fábrica `make_token` (`:93`). El plan no dicta ese docstring, así que cambiarlo en esta fase habría sido apartarse del alcance. El ejecutor lo declaró (handoff, punto 3). Destino: cierre, o la próxima fase que toque el archivo. Una redacción posible: «Builds the Authorization header for any raw token string.» — evidencia: `tests/test_token_failure_paths.py:45,93`.

Puntos juzgados sin hallazgo:

- **Los 3 tests nuevos son el texto dictado.** `test_corrupt_token_gets_the_same_detail_as_an_unknown_user` (`:114-123`) es el bloque
  de `plan.md:468-478` letra a letra. Cumple la adenda 2 (`verificacion.md:284-288`): está junto al de `:93-98` (hoy
  `test_expired_and_corrupt_tokens_get_distinct_details`, `:106-111`, que se conserva), usa
  `create_access_token(data={"sub": "ghost@test.com"})` y compara las dos respuestas con `==`.
  `test_token_for_soft_deleted_active_user_returns_401` (`:158-166`) tiene la firma, el docstring, el
  `persist_user(deleted_at=datetime(2026, 1, 15, 12, 0, tzinfo=UTC))` y el `_assert_bearer_401` dictados, y va tras el de
  usuario inactivo. `test_verify_email_expired_and_corrupt_tokens_get_distinct_errors` (`:203-212`) es `plan.md:490-500`
  letra a letra. Ninguna aserción lee texto en español: `==`/`!=` entre `json()["detail"]` o entre `.detail` de dos
  excepciones, más el contrato estructural de `_assert_bearer_401` (401, `WWW-Authenticate`, `set(body) == {"detail"}`,
  `isinstance(..., str)`). El archivo tiene `14 tests collected`.
- **Cuentas vecinas (D11).** `await persist_user()` está antes de `user = await persist_user()` en el test de token válido
  (`:77`) y antes de la petición en el de usuario desconocido (`:139`), que recibe `persist_user: PersistUser`, como dictan
  `plan.md:463,479-480`. `persist_user` llama a `make_user`, y este saca `cedula` y `email` de un contador global
  (`_USER_FACTORY_COUNTER = itertools.count()`, `tests/conftest.py:162,187-190`): sin argumentos, cada usuario es único y no
  choca con `ghost@test.com`. D11 en el archivo: `2 failed, 12 passed` (los dos tests), igual que la tabla.
- **`make_token` (P5).** `_make_token(user: User, *, expires_delta: timedelta | None = None) -> str` y la llamada con
  `expires_delta=expires_delta` son exactamente lo de `plan.md:451-456`. No hay claims libres. `from datetime import timedelta`
  está tras `import itertools`. El elemento `Returns:` es el texto dictado. `make_auth_headers` sigue llamando a
  `make_token(user)`. `grep -c "expires_delta" tests/conftest.py` = `3`; `grep -c "make_token(user, expires_delta="` = `1`.
- **El borrado de `:166` y el docstring recortado.** Los dicta `plan.md:486-487`, y el docstring nuevo es el dictado. La
  garantía queda en `tests/test_user_service.py:287` (`activate_user.assert_not_awaited()` en
  `test_verify_email_expired_token_raises_invalid_verification_token`) y, para el corrupto, en `:267`. El plan cita
  `:281` (`plan.md:85`), que es la línea de la base de BE-33. Las fases B y D movieron 6 líneas, igual que A4 pasó de 274 a 280.
  La forma de U8 que aplicó el ejecutor (activar con el `sub` del token, en la rama `ExpiredSignatureError`, antes del
  `raise`) es la de BE-33: `docs/deuda/BE-33/gaps.md:146` la describe en el caso `expired`. Re-medido: antes, archivo
  `1 failed, 10 passed` (`…chains_the_jwt_error_as_cause[expired]`) y suite `2 failed, 543 passed`; después, archivo
  `14 passed` y suite `1 failed, 547 passed` (`test_user_service.py::test_verify_email_expired_token_raises_invalid_verification_token`).
  Coincide con la fila U8 del plan.
- **Ni `_expired_token()` sin parámetros ni `_user_service` son refactors de paso.** Los dicta `plan.md:459-462`: el
  primero, sin parámetro y con el docstring dictado; el segundo, con el `UserService(...)` de la antigua `:156-160`, usado por
  los dos tests que el plan nombra. El docstring de una línea de `_user_service` no estaba dictado, pero AGENTS §4 lo exige
  y sigue la forma de los demás helpers del archivo. Tampoco son de paso `MakeToken` ni la importación
  `UTC, datetime, timedelta` (`plan.md:458`).
- **Tabla de mutantes re-medida.** Dos copias desechables en el scratchpad, `git archive b070f55` y `git archive dd88bf8`
  (el `diff --stat` entre sus `tests/` es exactamente los 2 archivos de la fase), con `app` resuelto a cada copia. Mutantes
  aplicados por contenido (1 coincidencia exigida), restaurados byte a byte y comprobados con `assert`. El árbol de trabajo
  no se tocó. `-p no:cacheprovider --no-cov`, variables de entorno ficticias.
  - antes (`b070f55`): sin mutar, `11 passed` / `545 passed`. D2, U6 y U7: `11 passed` / `545 passed`. D17: `11 passed` /
    `1 failed, 544 passed` (`test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login`). D11: `11 passed` /
    `1 failed, 544 passed` (`test_auth.py::test_admin_directory_hides_superadmins`).
  - después (`dd88bf8`): sin mutar, `14 passed` / `548 passed`. D2: `1 failed, 13 passed` / `1 failed, 547 passed`
    (`corrupt_token_gets_the_same_detail_as_an_unknown_user`). U6 y U7: `1 failed, 13 passed` / `1 failed, 547 passed`
    (`verify_email_expired_and_corrupt_tokens_get_distinct_errors`). D17: `1 failed, 13 passed` / `2 failed, 546 passed`.
    D11: `2 failed, 12 passed` / `3 failed, 545 passed`.
  - Coincide cifra a cifra con el handoff (`handoff-Fase_G.md:96-173`). Las celdas de archivo coinciden con la tabla del plan.
    La única nota de suite que no coincide es la de D17 (primer opcional). La tabla no da cifra de suite para D11. BE-33
    medía `11 failed` en la suite; hoy son 1 antes y 3 después. Lo que la tabla pide se cumple: el archivo lo mata por sí mismo.
- **Compuerta (fila G), reejecutada en HEAD `ed47aef`, exit 1.** `57 files already formatted`. ruff: `Found 8 errors.`,
  solo los 8 I001 `:1:1` de `app\` (`api\dependencies.py`, `api\routers\audit.py`, `core\email.py`, `db\database.py`,
  `repositories\user_repository.py`, `schemas\audit.py`, `services\audit_service.py`, `services\user_service.py`). mypy:
  `Found 9 errors in 5 files (checked 53 source files)`. Son `app\db\database.py:11`, `app\core\security.py:71` y `:87`,
  `app\services\user_service.py:124`, `app\api\dependencies.py:95` y `tests\test_user_service.py:105`, `:203`, `:280`,
  `:298`. Los cuatro de tests son `[arg-type]` `str | None`, y su contenido es `jwt.decode(result.verification_token, SECRET_KEY, …)`,
  `jwt.decode(result.access_token, SECRET_KEY, …)`, `SECRET_KEY,` y `SECRET_KEY,`: el conjunto de A4, ni uno más. Además:
  `Contracts: 4 kept, 0 broken.`, docs coherentes, `548 passed, 5 warnings`, `TOTAL 943 23 138 19 96.11%` (= línea base).
  En los archivos tocados, `ruff check` da `All checks passed!`, y mypy no da ningún error en ellos (los 5 que salen son de
  `app/` y entran por import). `git diff --check b070f55 dd88bf8` no da salida.
- **Commit `dd88bf8`.** El mensaje es idéntico a `plan.md:519-538`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5` (`diff`
  vacío salvo el salto final de `%B`). Toca exactamente los 2 archivos de la fase (`2 files changed, 68 insertions(+),
  18 deletions(-)`). `app/` no cambia: `git diff --stat fd144ad -- app/` sigue en `1 file changed, 3 insertions(+)` (E2).
  `override_get_db` sigue en `tests/conftest.py:86`. E1 se respetó: ninguna importación perdida (F401) y ruff está limpio.
- **`progress.json`.** `Fase_G` está `completed` con `dd88bf8`, un commit real. `current_target` = `Fase_H`. El `last_handoff`
  es nuevo y declara la desviación de D17. `edit_rules` no cambia y el JSON es válido. `ed47aef` toca solo
  `handoff-Fase_G.md` y `progress.json`. El árbol está limpio.
- No es la última fase: la «Verificación final» completa queda para H. Se adelantaron los patrones 1b (`0`), 9b-C
  (`1`, `1`, `3`) y 9c (`3`, `1`, `2`). El patrón 1 da `1` (`tests/test_email.py:99`), que es de la fase H.

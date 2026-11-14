# Gaps — BE-34

## Auditoría Fase A — 2026-11-14
**Veredicto Fase A: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase A — Proceso, no código: el hook de `ruff check --fix` (`.claude/settings.json`) borró `import runpy` (F401) porque el import se escribió en una edición anterior a la del test que lo usa. El ejecutor lo volvió a añadir y el diff final es el dictado (`9 0`), así que no afecta a la fase A. Riesgo para C, D y E, que dictan imports nuevos (`SecretStr`, `func`, `UserRole`, `UserCreateByAdmin`): conviene escribir cada import en la misma edición que su primer uso, o comprobarlo con `git show --numstat` antes del commit, como hizo A — evidencia: `docs/deuda/BE-34/handoff-Fase_A.md`, sección "Residuales y dudas", viñeta 1.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `0147a71`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `d873b49` existe (`git show --stat`: `tests/test_config.py | 9 +++++++++`, 1 file changed), su padre es `c0e9096`
  y `git diff --name-only c0e9096 d873b49` → solo `tests/test_config.py`. El mensaje coincide byte a byte con el bloque
  "Commit" de la fase A, incluido el trailer `Co-Authored-By`.
- Segundo commit `0147a71` (`docs(progress): record BE-34 Fase_A completion`): solo `docs/deuda/BE-34/handoff-Fase_A.md` y
  `progress.json`. Se ajusta al protocolo: es el paso 6 de `.claude/agents/fase-ejecutor.md` (l. 62-63, mensaje
  `docs(progress): record <ID> <fase> completion`), y así se hizo en BE-39, BE-40, BE-42 y A4. No es hallazgo.
- `progress.json`: `Fase_A` `completed` con `commit: "d873b49"` (hash real); `current_target: "Fase_B"`; `last_handoff`
  presente; `edit_rules` y `allowed_statuses` intactos; las fases B–G, sin tocar (diff de `0147a71`: 8 líneas, solo esos
  campos). JSON válido.
- Cambios exactos (diff de `d873b49`): (1) `import runpy` antes de `from collections.abc import Callable`; (2)
  `ROOT_CONFTEST = …` justo tras `ENV_EXAMPLE = …`, sin línea en blanco; (3) `test_test_environment_fixes_every_setting` al
  final, con dos líneas en blanco antes, texto idéntico al dictado. Los tres están, nada más cambia.
- Criterio de aceptación: `git show --numstat --format= d873b49` → `9	0	tests/test_config.py`;
  `git grep -n 'TEST_ENVIRONMENT' -- tests | wc -l` → `1` (`tests/test_config.py:226`). UTF-8/ASCII, LF (0 `\r`).
- Fuera de alcance respetado: `conftest.py`, `REQUIRED`/`OPTIONAL_DEFAULTS` y `app/` no aparecen en el diff.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs coherente ·
  `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`. Igual a la fila A del plan y a lo que pegó el ejecutor. Frente a
  la línea base de `verificacion.md` (l. 127-131: 638 passed, 96.82 %, 61 files, 56 source files, 4 kept): +1 test, cobertura
  igual, 0 errores de ruff y mypy.
- Archivo tocado: `ruff check tests/test_config.py` → `All checks passed!`; `ruff format --check` → `1 file already formatted`;
  `mypy tests/test_config.py` → `Success: no issues found in 1 source file`.
- Mutante MA repetido por el auditor (copias nuevas de `git archive`, procedimiento común del plan):
  - sobre `d873b49`, sin la línea `CORS_ORIGINS`: `FAILED tests/test_config.py::test_test_environment_fixes_every_setting` ·
    `1 failed, 349 passed, 8 warnings` (= tabla);
  - sobre `c0e9096` con el mismo mutante: `349 passed, 8 warnings` (el hueco de BE-47 era real);
  - copia limpia de `d873b49`: `350 passed, 8 warnings` (= columna "Suite de la copia" de la fila A).
- AGENTS §5: el test nuevo no usa mocks ni fábricas, la aserción es sobre un conjunto de claves (sin texto en español) y el
  docstring dice su categoría ("Edge case"). Está anotado (`-> None`). Su único efecto lateral, que `runpy` repite
  `os.environ.update(TEST_ENVIRONMENT)` con los mismos valores, ya lo midió el plan (Análisis) y es inocuo.
- No es la última fase: la "Verificación final" del plan no aplica todavía.

## Auditoría Fase B — 2026-11-14
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `29b61b8`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `b08491b` existe, su padre es `4b2230a`; `git show --numstat --format= b08491b` →
  `76	0	docs/adr/0015-bootstrap-del-primer-superadmin.md` (1 file changed, solo el ADR). El mensaje (`git cat-file commit`)
  coincide byte a byte con el bloque "Commit" de la fase B, trailer `Co-Authored-By` incluido.
- Segundo commit `29b61b8` (`docs(progress): record BE-34 Fase_B completion`): solo `handoff-Fase_B.md` y `progress.json`
  (paso 6 de `fase-ejecutor`, como en la fase A). No es hallazgo.
- Texto del ADR contra el dictado: script del auditor que extrae el bloque ```` ```markdown ```` de la fase B de
  `plan.md` en `b08491b` (plan sin cambios desde `4b2230a`: `git diff 4b2230a HEAD -- docs/deuda/BE-34/plan.md` vacío),
  quita los dos espacios de sangría y sustituye `<FECHA>` por `13 nov 2026` (E0) → `IDENTICAL: True`, 76 líneas en ambos.
  Sin BOM, sin `\r`, termina en un único `\n`. La Evidencia cita `de 638 a 675 tests` (E0.3, E2 punto 1); R9 queda
  resuelto como preveía E2. La línea "Estado" lleva `13 nov 2026`, no `<FECHA>`.
- `progress.json` (diff de `29b61b8`): `Fase_B` `completed`, `commit: "b08491b"` (hash real); `current_target`
  `Fase_B` → `Fase_C`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos; las demás fases sin tocar.
  JSON válido.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` ·
  `docs (coherencia): OK` · `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`. Igual a la fila B del plan, a lo
  que pegó el ejecutor y, frente a la línea base de `verificacion.md` (l. 127-131: 638 · 96.82 % · 61 · 56 · 4 kept), sin
  retroceso. Ningún `.py` tocado: ruff y mypy por archivo no aplican.
- Suite de la copia (directorio nuevo, `git archive b08491b`, sin `test_check*`): `350 passed, 8 warnings` (= fila B).
- Fuera de alcance respetado: `AGENTS.md`, `docs/CONTEXT.md`, el manual técnico y ADR-0013 no aparecen en el diff.
- AGENTS §7: el ADR sigue el formato Nygard (Contexto, Decisión, Consecuencias, Alternativas consideradas, Evidencia).
- No es la última fase: la "Verificación final" del plan no aplica todavía.

## Auditoría Fase C — 2026-11-14
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `9c0eae7`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `f83a511` existe, su padre es `846efe0`; `git show --numstat --format= f83a511` →
  `11	0	.env.example` · `24	1	app/core/config.py` · `93	0	tests/test_config.py` (= criterio de aceptación).
  `git diff --name-only 846efe0 HEAD` → esos tres más `handoff-Fase_C.md` y `progress.json`. El mensaje
  (`git cat-file commit`, comparado en Python con las l. 483-501 de `plan.md` sin la sangría) → `IDENTICAL`, trailer incluido.
- Segundo commit `9c0eae7` (`docs(progress): record BE-34 Fase_C completion`): solo `handoff-Fase_C.md` y `progress.json`
  (paso 6 de `fase-ejecutor`, como en A y B). No es hallazgo.
- Enmiendas: E0–E3 no cambian la fase C (E0 aprueba A–D "como están escritas"; E2 y E3 tocan F y G). Rige el cuerpo.
- Cambios exactos contra el diff: (1) `from pydantic import Field, SecretStr`; la clase `SuperadminBootstrapSettings(DatabaseSettings)`
  entre el final de `Settings` (`return self.mail_from or self.mail_username`) y `@lru_cache`, docstring y cinco campos
  idénticos al dictado (`superadmin_password: SecretStr`); (2) bloque `SUPERADMIN_*` de `.env.example` tras
  `CORS_ORIGINS=…` con una línea en blanco, texto idéntico; (3) en `tests/test_config.py`, el import de
  `SuperadminBootstrapSettings` tras `Settings,`, `from app.schemas.user import UserCreateByAdmin, UserRole`,
  `BOOTSTRAP_VALUES`, `_set_bootstrap` entre `_set_required` y `_clear`, y los 6 tests (11 casos con el parametrizado) al
  final, texto idéntico. Nada más cambia.
- Archivos en UTF-8 sin BOM, LF (blob de `f83a511`: 0 `\r` en los tres, medido en Python), con `\n` final.
- Fuera de alcance respetado: `git diff 846efe0 f83a511 -- conftest.py tests/conftest.py alembic app/api app/main.py
  pyproject.toml app/schemas app/models` → vacío; `Settings`, `REQUIRED` y `OPTIONAL_DEFAULTS` sin cambios.
  `python -c "…print(len(S.model_fields), len(B.model_fields))"` → `15 6` (= plan).
- `progress.json` (diff de `9c0eae7`): `Fase_C` `completed`, `commit: "f83a511"` (hash real); `current_target`
  `Fase_C` → `Fase_D`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos; las demás fases sin tocar.
  JSON válido.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` ·
  `docs (coherencia): OK` · `650 passed, 8 warnings` · `TOTAL 966 18 136 15 97.01%`. Igual a la fila C del plan y a lo que
  pegó el ejecutor. Frente a la línea base de `verificacion.md` (638 · 96.82 % · 61 · 56 · 4 kept) y a la fase B
  (639 · 96.82 %): +11 tests, cobertura sube, 0 errores de ruff y mypy.
- Archivos tocados: `ruff check app/core/config.py tests/test_config.py` → `All checks passed!`; `ruff format --check` →
  `2 files already formatted`; `mypy` → `Success: no issues found in 2 source files`.
- Mutantes repetidos por el auditor (directorios nuevos `scratchpad/audit_C_*`, `git archive f83a511`, comando común del
  plan, sin `test_check*`):
  - copia limpia: `361 passed, 8 warnings` (= columna "Suite de la copia" de la fila C);
  - MC1 (`SecretStr` → `str`): `FAILED test_bootstrap_settings_need_no_web_app_secret` ·
    `FAILED test_bootstrap_password_never_shows_in_repr` · `FAILED test_env_example_password_is_not_a_usable_credential` ·
    `3 failed, 358 passed` (= tabla);
  - MC2 (`(DatabaseSettings)` → `(Settings)`): `FAILED test_bootstrap_settings_need_no_web_app_secret` ·
    `1 failed, 360 passed` (= tabla);
  - MC3 (`.env.example`, contraseña → `Superadmin2026`): `FAILED test_env_example_password_is_not_a_usable_credential` ·
    `1 failed, 360 passed` (= tabla).
  - Sonda adicional del auditor sobre la observación del handoff (MC1 no tumba `test_bootstrap_validation_errors_do_not_echo_values`):
    con `hide_input_in_errors=False` en `DatabaseSettings` (l. 34) ese test sí cae (`2 failed, 33 passed` en
    `tests/test_config.py`, junto a `test_validation_errors_do_not_echo_values`). El test protege algo real; no es teatro.
- AGENTS §5 y `test-sanitizer`: sin mocks; sin fábricas de usuario o token que centralizar (son valores de configuración);
  aserciones sobre tipos y `loc` de errores, conjuntos de campos y valores centinela propios, nunca sobre texto en español
  (`Nombre`/`Apellido` de `.env.example` son datos, no aserciones); nombres y docstrings en inglés, cada docstring con su
  categoría (1 camino feliz; 2 de fallo, 6 + 1 casos; 3 de borde); anotados.
- No es la última fase: la "Verificación final" del plan no aplica todavía.

## Auditoría Fase D — 2026-11-14
**Veredicto Fase D: PASS (0 bloqueantes, 0 opcionales).**

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `c1cefc0`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `e9d010c` existe, su padre es `a5cd7b5`; `git diff --name-only a5cd7b5 e9d010c` → solo los cuatro
  archivos de la fase. `git show --numstat --format= e9d010c` → `22 1 app/repositories/user_repository.py` ·
  `74 0 app/services/superadmin_bootstrap.py` · `159 0 tests/test_superadmin_bootstrap.py` ·
  `41 0 tests/test_user_repository.py` (= criterio de aceptación). El mensaje coincide byte a byte con el bloque "Commit"
  de la fase D (l. 831-850 de `plan.md` sin sangría, `diff` vacío), trailer incluido.
- Segundo commit `c1cefc0` (`docs(progress): record BE-34 Fase_D completion`): solo `handoff-Fase_D.md` y `progress.json`.
- `progress.json` (diff de `c1cefc0`): `Fase_D` `completed`, `commit: "e9d010c"` (hash real); `current_target`
  `Fase_D` → `Fase_E`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos; E, F y G sin tocar. JSON válido
  (`python -m json.tool`).
- Enmiendas: E0 aprueba A–D "como están escritas" (y acepta `"source": "bootstrap"`, E0.2); E2/E3 tocan F y G. Rige el
  cuerpo de la fase D.
- Cambios exactos contra el diff, comparados por script (bloques dictados sin la sangría de 5 espacios frente a
  `git show e9d010c:<archivo>`): `app/services/superadmin_bootstrap.py` (l. 535-608) `IDENTICAL`;
  `tests/test_user_repository.py` (l. 612-652) `IDENTICAL`; `tests/test_superadmin_bootstrap.py` (l. 657-815)
  `IDENTICAL`; el método `count_active_superadmins` (l. 513-531) está contenido literalmente en `user_repository.py`, entre
  `get_user_by_email_or_cedula` y `get_non_deleted_user_by_email`; `from sqlalchemy import func` antes de
  `from sqlalchemy.ext.asyncio import AsyncSession` y `from app.models.user import User, UserRole`. Nada más cambia.
- Codificación: los cuatro blobs de `e9d010c` en UTF-8 sin BOM, 0 bytes `\r`, `\n` final (medido en Python).
- Fuera de alcance respetado: `git diff --stat a5cd7b5 e9d010c -- conftest.py tests/conftest.py alembic app/api app/main.py
  pyproject.toml app/core app/models app/schemas app/services/user_service.py app/services/user_access_policy.py` → vacío.
  `create_user` y su `commit()` (A3) sin cambios.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `64 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 59 source files` · `Contracts: 4 kept, 0 broken.` · docs coherente ·
  `667 passed, 8 warnings` · `TOTAL 988 18 140 15 97.07%` (`superadmin_bootstrap.py` al 100 %, no aparece por
  `skip_covered`; las líneas sin cubrir de `user_repository.py`, 61 y 80, son previas y ajenas al método nuevo). Igual a la
  fila D del plan y a lo que pegó el ejecutor. Frente a la línea base de `verificacion.md` (638 · 96.82 % · 61 · 56 · 4
  kept) y a la fase C (650 · 97.01 %): +17 tests, cobertura sube, 0 errores de ruff y mypy.
- Archivos tocados: `ruff format --check` (los 4) → `4 files already formatted`; `ruff check` → `All checks passed!`;
  `mypy` → `Success: no issues found in 4 source files`.
- Hook de ruff no disparado (handoff, "Cómo se escribió"): sobre una copia `git archive e9d010c` se aplicó lo mismo que hace
  `.claude/hooks/ruff_on_edit.py` (`ruff format <f>` + `ruff check --fix <f>`) a los cuatro archivos → `4 files left
  unchanged` · `All checks passed!`, y `cmp` contra los blobs de `e9d010c` → idénticos los cuatro. El estado commiteado es
  el que habría dejado el hook, y la compuerta cubre lo mismo (`ruff format --check` y `ruff check`). No es hallazgo.
- Mutantes repetidos por el auditor (directorios nuevos `scratchpad/auditD/mut_*`, `git archive e9d010c`, comando común del
  plan, sin `test_check*`; cada edición exige una sola aparición del original):
  - copia limpia: `378 passed, 8 warnings` (= columna "Suite de la copia" de la fila D);
  - MD1 (borrar `User.is_active.is_(True),`): `2 failed, 376 passed` — `test_bootstrap_creates_when_no_superadmin_can_sign_in[inactive]`,
    `test_count_active_superadmins_skips_those_who_cannot_sign_in[inactive]` (= tabla);
  - MD2 (borrar `User.deleted_at.is_(None),`): `1 failed, 377 passed` — `…skips_those_who_cannot_sign_in[deleted-but-active-flag]` (= tabla);
  - MD3 (borrar `User.role == UserRole.superadmin,`): `3 failed, 375 passed` — `…never_takes_over_an_existing_account[active-tourist-cedula|email]`,
    `test_count_active_superadmins_counts_each_active_one` (= tabla);
  - MD4 (`> 0:` → `> 1:`): `2 failed, 376 passed` — `…writes_nothing_when_an_active_superadmin_exists`, `…second_run_writes_nothing` (= tabla);
  - MD5 (`if existing_user:` → `if False:`): `6 failed, 372 passed` — los 6 casos de `…never_takes_over_an_existing_account` (= tabla);
  - MD6 (`role=UserRole.superadmin,` → `role=credentials.role,`): `1 failed, 377 passed` — `…always_creates_an_active_superadmin` (= tabla);
  - MD7 (`is_active=True,` → `is_active=credentials.is_active,`): `1 failed, 377 passed` — `…always_creates_an_active_superadmin` (= tabla).
- AGENTS §3: `app/services/superadmin_bootstrap.py` no importa `fastapi` ni `starlette` (grep vacío) y no hace `commit()`;
  el método nuevo del repositorio solo hace `execute` + `scalar_one` (sin `commit`). `AlreadyExistsError` ya existe
  (`app/core/exceptions.py:67`) y está registrada (`app/main.py:124`, 400). Su texto en español es `detail` para el usuario
  final (AGENTS §4 c). No hay excepción nueva.
- AGENTS §5 y `test-sanitizer`: sin mocks (repositorios reales sobre la base de prueba); usuarios previos con la fábrica
  `persist_user` (sin `User(` a mano en los tests); las credenciales del bootstrap son un DTO de entrada, no un usuario de
  fábrica. Aserciones estrictas sobre filas, roles, banderas, `deleted_at`, hash verificable, conteos de `User` y `AuditLog`
  y el `changes` de la auditoría; ninguna sobre texto en español (0 caracteres acentuados en los dos archivos de test).
  ADR-0011: no hay petición HTTP (el núcleo se llama con `db_session`); `persist_user` confirma antes, y los objetos ya
  cargados se releen con `refresh` después (`account` en la matriz de toma, `created` en el caso de rol/estado ignorados).
  Categorías: 2 caminos felices; fallo: cuenta existente (6 casos), superadmin activo existente, inactivos/borrados no
  cuentan (3); borde: base vacía, segunda corrida, superadmins que no pueden entrar (2), credenciales con rol/estado ajenos.
- No es la última fase: la "Verificación final" del plan no aplica todavía.

## Auditoría Fase E — 2026-11-14
**Veredicto Fase E: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase E — `test_command_fails_when_the_email_belongs_to_another_account` crea el turista con `insert(User).values(...)` y `password_hash="hash"`, no con la fábrica (AGENTS §5: "prohibido construir usuarios a mano"). Está justificado: `persist_user` está atado a `db_session` (`tests/conftest.py:268-282`, `StaticPool` en memoria) y el comando abre su propio motor sobre la base de archivo de `tmp_path`, así que la fábrica no puede escribir donde lee el comando. Lo dicta el plan aprobado (l. 1100-1114) y lo declara el handoff ("test-sanitizer"), pero no lo explica ni el plan en "Por qué cada truco del test" ni un comentario del test. `make_user`, que no está atado a una sesión, podría construir la entidad con una sesión sobre la URL del archivo. No afecta a la corrección; si David lo quiere, va al backlog — tests/test_bootstrap_superadmin_command.py:100-114 — RESUELTO (5ec73d2, fase H por E4/E5; auditoría de H más abajo)

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `74ac1d8`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `2bf29e5` existe y su padre es `1beb91d`. `git diff --name-only 1beb91d 2bf29e5` → solo los cuatro
  archivos de la fase. `git show --numstat --format= 2bf29e5` → `1 0 app/cli/__init__.py` ·
  `114 0 app/cli/bootstrap_superadmin.py` · `2 2 pyproject.toml` · `208 0 tests/test_bootstrap_superadmin_command.py`
  (= criterio de aceptación). El mensaje (`git log -1 --format=%B`) coincide byte a byte con el bloque "Commit" de la fase
  E (l. 1217-1240 de `plan.md` sin la sangría), trailer incluido.
- Segundo commit `74ac1d8` (`docs(progress): record BE-34 Fase_E completion`, padre `2bf29e5`): solo `handoff-Fase_E.md`
  y `progress.json`.
- `progress.json` (diff de `74ac1d8`): `Fase_E` `completed`, `commit: "2bf29e5"` (hash real); `current_target`
  `Fase_E` → `Fase_F`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos; la descripción de `Fase_E` no
  cambia; F y G sin tocar. JSON válido.
- Enmiendas: E0.3 añade a E el test del proceso hijo y ME6; su "Aplicación" fija 675 · 97,37 % · 1031 · 8 tests · 386;
  E2 punto 1 aprueba A–E "tal como están escritas". El cuerpo de la fase E ya incorpora E0.3; no hay diferencia que dirimir.
- Cambios exactos contra el diff, comparados por script (bloques dictados sin la sangría de 5 espacios frente a
  `git show 2bf29e5:<archivo>`): `app/cli/bootstrap_superadmin.py` (l. 866-979, 4442 bytes) `IDENTICAL`;
  `tests/test_bootstrap_superadmin_command.py` (l. 983-1190, 7279 bytes) `IDENTICAL`; `app/cli/__init__.py` igual a la
  línea dictada más `\n`. `pyproject.toml`: exactamente los dos cambios del punto 2 (`name = "Capas: api | cli -> ..."` y
  `"app.api | app.cli",`). Los tres `.py` en UTF-8 sin BOM y sin `\r`.
- Hook de ruff no disparado (handoff, "Cómo se escribió"): sobre una copia `git archive 2bf29e5` se aplicó lo mismo que
  `.claude/hooks/ruff_on_edit.py` (`ruff format <f>` + `ruff check --fix <f>`) a los tres `.py` → `3 files left
  unchanged` · `All checks passed!`, y `cmp` contra los blobs de `2bf29e5` → idénticos los tres. No es hallazgo.
- Archivos tocados en el repo: `ruff check` (los tres `.py` y `pyproject.toml`) → `All checks passed!`; `mypy` (los tres)
  → `Success: no issues found in 3 source files`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `67 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 62 source files` ·
  `Capas: api | cli -> services -> repositories -> models KEPT` · `Contracts: 4 kept, 0 broken.` · docs coherente ·
  `675 passed, 8 warnings` · `TOTAL 1031 17 148 14 97.37%`. `coverage report --include='app/cli/*'` con los datos de esa
  corrida → `TOTAL 43 0 8 0 100.00%` (`1 empty file skipped`, el `__init__.py`). Igual a la fila E del plan y a lo que
  pegó el ejecutor. Frente a la línea base de `verificacion.md` (638 · 96,82 % · 61 · 56 · 4 kept) y a la fase D (667 ·
  97,07 %): +8 tests, la cobertura sube, 0 errores de ruff y mypy.
- Mutantes repetidos por el auditor (directorios nuevos `scratchpad/auditE/mut_*`, `git archive 2bf29e5`, comando común
  del plan, sin `test_check*`; cada edición exige una sola aparición del original y se comprobó con `git diff --no-index`):
  - copia limpia: `386 passed, 8 warnings` (= columna "Suite de la copia" de la fila E);
  - ME1 (borrar las dos líneas de `superadmin_{field}`): `2 failed, 384 passed` — `…naming_only_the_variable[weak-password]`
    y `[short-cedula]` (= tabla);
  - ME2 (`return 1` → `return 0` en la rama de `AlreadyExistsError`, l. 104; `diff` contra el blob: solo `104c104`):
    `1 failed, 385 passed` — `test_command_fails_when_the_email_belongs_to_another_account` (= tabla). Confirma la
    repetición que declaró el ejecutor tras su ancla fallida;
  - ME3 (añadir `{credentials.password}` al `print` de éxito): `3 failed, 383 passed` — `…creates_the_superadmin_without_writing_secrets`,
    `…second_run_exits_zero_and_writes_nothing`, `…runs_without_the_web_app_secrets` (= tabla);
  - ME4 (`echo=True` en el motor del comando): `1 failed, 385 passed` — `…creates_the_superadmin_without_writing_secrets` (= tabla);
  - ME5 (`sys.exit(main())` → `main()`): `1 failed, 385 passed` — `…runs_as_a_module_and_exits_with_the_code_of_main` (= tabla);
  - ME6 (`import app.core.email  # noqa: F401` en el núcleo): `1 failed, 385 passed` — solo
    `test_command_runs_without_the_web_app_secrets` (= tabla);
  - MK1 (`import app.cli  # noqa: F401` antes del primer `from app.` del núcleo), entry point de import-linter en la copia
    → exit 1, `Capas: api | cli -> ... BROKEN`, `Contracts: 3 kept, 1 broken.`,
    `app.services.superadmin_bootstrap -> app.cli (l.8)` (= tabla).
- ADR-0015 y ADR-0013: el comando lee la configuración solo con `SuperadminBootstrapSettings()` de `app/core/config.py`;
  `git grep -E 'getenv|load_dotenv|os\.environ|fastapi|starlette|get_settings|commit\(' -- app/cli` → vacío. No construye
  `Settings` (lo prueba el test del proceso hijo, y ME6 lo demuestra). Motor propio sin `echo`, con `dispose()` en
  `finally`. No imprime ningún secreto: la contraseña sale de `SecretStr` solo para `UserCreateByAdmin`; los errores van
  como `VARIABLE: tipo` con `errors(include_input=False, include_url=False)`; `UserCreateByAdmin` no tiene
  `model_validator`, así que todo `loc` tiene al menos un elemento y `_report` no puede caer en `IndexError`. El éxito
  imprime el correo (no es secreto; lo dicta el plan). R8 (`IntegrityError` con parámetros si dos operadores corren el
  comando a la vez) sigue declarado, sin arreglo.
- AGENTS §3 y §4: `app.cli` es un adaptador hermano de `app.api` en el contrato; no hay excepción de dominio nueva
  (`AlreadyExistsError` ya está registrada); identificadores, docstrings y comentarios en inglés; los textos en español
  son salida para el operador (§4 c). Fuera de alcance respetado: `Dockerfile`, `cd-pipeline.yml`, `app/db/database.py` y
  `AGENTS.md` sin cambios.
- AGENTS §5 y `test-sanitizer`: sin mocks (comando real sobre una base de archivo propia); aserciones sobre código de
  salida, filas (cédula, rol, `is_active`), hash verificado con `verify_password`, conteos de `users` y `audit_logs`, y
  ausencia de contraseña y hash en stdout, stderr y `caplog`; la única igualdad de texto es `VARIABLE: tipo`
  (identificadores) o la cadena vacía; nada en español en las aserciones. Categorías: 1 camino feliz; fallo: correo tomado
  y 3 configuraciones inválidas; borde: segunda corrida, `python -m` y proceso hijo sin secretos. La fábrica: ver el
  opcional.
- Verificación final, pasos 1-8 (los que valen tras E; F y G siguen `pending`, así que no es la última fase):
  1. `git grep ... 'seed|create_superuser|create_superadmin'` → sin salida, exit 1.
  2. Patrón 2 → las 8 líneas exactas (`.env.example:6` · `app/cli/bootstrap_superadmin.py:19` · `app/core/config.py:12` ·
     `app/repositories/user_repository.py:1` · `app/services/superadmin_bootstrap.py:3` ·
     `tests/test_bootstrap_superadmin_command.py:16` · `tests/test_config.py:41` · `tests/test_superadmin_bootstrap.py:11`),
     109 en total.
  3. Patrón 3 → 4 líneas: `app/cli/bootstrap_superadmin.py:90`, `app/services/superadmin_bootstrap.py:60`,
     `app/services/user_service.py:88` y `:412`.
  4. Patrón 4 → `dependencies.py:199`, `routers/user.py:35`, `user_access_policy.py:67` y `:72`.
  5. `TEST_ENVIRONMENT` → 1 línea, `tests/test_config.py:243`.
  6. `git diff --stat 4f10660 -- <lo que no se toca>` → vacío.
  7. `git diff --name-only 4f10660 -- app tests pyproject.toml .env.example docs/adr` → 12 archivos, los de la Regla de
     alcance.
  8. `15 6`.
  (El paso 9 es la compuerta de arriba.)

## Auditoría Fase F — 2026-11-14
**Veredicto Fase F: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `2570c03`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `4eba2d2` existe; `git cat-file -p 4eba2d2` → `parent a631612c51d05a0a1ec43caf4acbc0aecf9647f2`.
  `git show --numstat --format= 4eba2d2` → `87	0	docs/adr/0016-correo-en-minusculas.md` (1 file changed, solo el ADR;
  = criterio de aceptación). `git diff --stat a631612 2570c03` → el ADR, `handoff-Fase_F.md` y `progress.json`, nada más.
- Mensaje del commit, byte a byte: cuerpo de `git cat-file commit 4eba2d2` (todo lo que sigue a la primera línea vacía)
  frente a las l. 1458-1476 de `plan.md` sin los dos espacios de sangría → `cmp` idéntico, 0 `\r`, 0 espacios finales,
  termina en un único `\n` tras el trailer `Co-Authored-By`. No hay diferencia real en el objeto commit: la "línea en
  blanco final" que cita el handoff es solo el separador que añade `git log --format=%B` al mostrarlo.
- Texto del ADR, carácter a carácter: l. 1362-1448 de `plan.md` sin la sangría de dos espacios y con `<FECHA>` →
  `14 nov 2026` (E3, punto 1) frente a `git show 4eba2d2:docs/adr/0016-correo-en-minusculas.md` → `cmp` idéntico, 87
  líneas en ambos (incluye las dos líneas de E3, punto 2, en "Consecuencias": criterio `87 0`). UTF-8 sin `\r`, 0
  espacios finales, `\n` final. La línea "Estado" lleva `14 nov 2026`, no `<FECHA>`.
- Coherencia del ADR con E2, E3 y la fase G:
  - Nombres: `LowercaseEmail = Annotated[EmailStr, AfterValidator(str.lower)]` en `app/schemas/user.py` sobre `UserBase`,
    `UserLogin` y `UserUpdate` (= G, cambio 1); `CHECK (email = lower(email))` con nombre `ck_users_email_lowercase`
    en el modelo `User` y en la migración `b51f3c9e2a64` (= G, cambios 2 y 3; E2, punto 3.2). `ix_users_email` existe
    (`alembic/versions/a0f621304d75_init_esquema_inicial_limpio.py:51`) y sigue dando la unicidad (E2, punto 5). La
    revisión base de G, `2cc4b57c136c`, es la cabeza actual (ningún otro archivo de `alembic/versions` la cita como padre).
  - Las tres consultas que el ADR dice exactas siguen así: `app/repositories/user_repository.py:18`, `:44` y `:56` (= E3).
  - Ventana de mantenimiento: Q1 = Q2 = 0 en `develop`, `staging` y `main` (13 nov, 17:40) y API apagada el 14 nov
    (= E2, puntos 3.4, 3.7 y 4). Sin migración de datos y precondición de cada despliegue (= E2, punto 3.4).
  - Tokens que comparan exacto (decisión 6) = E3, punto 3 y el test que G dicta para el 404.
  - Desviaciones de OWASP declaradas: la parte local sensible a mayúsculas (primera viñeta de Consecuencias), el pliegue
    por defecto (segunda, añadida por E3, punto 2) y "Store both" (alternativa 3) = E3, punto 2 (opción a). Las citas en
    inglés las comprobó la sesión Mentor contra la página (E3, punto 2); el enlace está en Referencias del plan
    (l. 2040-2042), como exige E2, punto 3.7. RFC 5321 no se cita (l. 2043).
  - Alternativas que E2, punto 3.7 exige con su razón: `lower(email)` en consultas con índice funcional (alternativa 1) y
    normalizar sin `CHECK` (alternativa 2), presentes.
  - Evidencia: `rOOT@Test.com` y `ÁNGEL@Test.com` son los valores de G (l. 1590, l. 1286); 675 → 691 tests y 97,37 % →
    97,63 % (= fila G); límite de SQLite y de `alembic check` declarados (= R12, E2 punto 3.8).
  - Relaciones citadas existen: ADR-0002, ADR-0009 (addenda), ADR-0010 punto 7 (`alembic check`, l. 31-32), backlog A9,
    D5 y BE-51.
  - Formato Nygard (AGENTS §7): Estado, Contexto, Decisión, Consecuencias, Alternativas consideradas, Evidencia.
- `progress.json` (diff de `2570c03`, 4 líneas cambiadas): `current_target` `Fase_F` → `Fase_G`; `Fase_F.status`
  `pending` → `completed`; `Fase_F.commit` `null` → `"4eba2d2"` (hash real); `last_handoff` reescrito. Nada más: la
  descripción de `Fase_F`, las fases A–E y G, `allowed_statuses` (misma línea, mismo formato en línea) y `edit_rules`
  intactos. JSON válido, 0 `\r`, mismo final (`\n}\n`) que en `a631612`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `67 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 62 source files` · `Contracts: 4 kept, 0 broken.` ·
  `docs (coherencia): OK` · `675 passed, 8 warnings` · `TOTAL 1031 17 148 14 97.37%`. Igual a la fila F del plan y a lo
  que pegó el ejecutor. Frente a la línea base de `verificacion.md` (638 · 96,82 % · 61 · 56 · 4 kept) y a la fase E
  (675 · 97,37 %): sin retroceso. Ningún `.py` tocado: ruff y mypy por archivo no aplican.
- Suite de la copia (directorio nuevo `scratchpad/auditF_copy_4eba2d2`, `git archive 4eba2d2`, comando común del plan,
  sin `test_check*`): `386 passed, 8 warnings` (= fila F).
- Fuera de alcance respetado: el código de G, ADR-0015, `AGENTS.md`, `docs/CONTEXT.md` y `docs/backlog.md` no aparecen en
  el diff. Nada de la fase H (E4).
- No es la última fase (G pendiente; H por escribir): la "Verificación final" del plan no aplica todavía.

## Auditoría Fase G — 2026-11-14
**Veredicto Fase G: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `bf4ae56`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `9c9edd2` existe, `parent 06c8929acb4dac7e5001397f1fdac9a004797e1f` (`git cat-file commit`).
  `git diff --name-only 06c8929 9c9edd2` → los 5 archivos de G y nada más; ninguno de A–E.
  `git show --numstat --format= 9c9edd2` → `35 0` migración · `4 1 app/models/user.py` · `10 4 app/schemas/user.py` ·
  `299 0 tests/test_email_case.py` · `0 2 tests/test_user_response.py` (= criterio de aceptación).
- Mensaje, byte a byte: cuerpo de `git cat-file commit 9c9edd2` frente a l. 1882-1905 de `plan.md` sin la sangría de dos
  espacios → `diff` vacío (incluye el trailer `Co-Authored-By`).
- Código, byte a byte (copias en el scratchpad de la auditoría):
  - Migración: l. 1513-1547 del plan sin los 5 espacios de sangría (0 líneas no vacías sin ella) frente a
    `git show 9c9edd2:alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py` → `cmp` idéntico, 35 líneas,
    0 `\r`.
  - `tests/test_email_case.py`: l. 1553-1851 → `cmp` idéntico, 299 líneas, 0 `\r`.
  - `app/schemas/user.py`, `app/models/user.py` y `tests/test_user_response.py`: reconstruidos aplicando a la versión de
    `06c8929` cada sustitución dictada (cada ancla aparece una sola vez) → iguales a los de `9c9edd2` (`True` ×3), LF.
- Hook simulado sobre copias de los cuatro `.py` fuera de `alembic/`: `ruff format` → `4 files left unchanged`;
  `ruff check --fix` → `All checks passed!`; `cmp` con el original → idénticos los cuatro. En el repo,
  `ruff check` / `ruff format --check` / `mypy` de esos cuatro → `All checks passed!` · `4 files already formatted` ·
  `Success: no issues found in 4 source files`.
- Migración fuera de ruff y mypy, igual que las existentes: `pyproject.toml:61` `extend-exclude = ["alembic/versions", …]`
  y `[tool.mypy] files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]` (`:90`). `ruff check
  --force-exclude` sobre ella → sin archivos. Forzada junto a `2cc4b57c136c`, las dos dan los avisos de la plantilla
  `script.py.mako` (`UP007`, `UP035`, `I001`; `E501` solo en la existente). El estilo es el que dicta el plan.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `68 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `691 passed, 8 warnings` · `TOTAL 1034 15 148 13 97.63%` · `Compuerta superada.` = fila G y = handoff. Frente a la
  línea base (638 · 96,82 % · 61 · 56 · 4 kept) y a F (675 · 97,37 %): sin retroceso. Los 8 warnings son los mismos
  `StarletteDeprecationWarning` de siempre (`test_route_guards` ×3, `test_services` ×3, `test_user_response` ×2);
  ninguno de `test_email_case.py`, que con `-W error` da `17 passed`.
- Mutantes (directorio nuevo por copia, `git archive HEAD`, comando común sin `test_check*`): limpia `402 passed`;
  MG1 `11 failed, 391 passed`; MG2 `5 failed, 397 passed`; MG3 `3 failed, 399 passed`; MG4 `3 failed, 399 passed`; MG5
  `1 failed, 399 passed, 2 errors` (errores en `pre_migration_db`: `ValueError: No such constraint:
  'ck_users_email_lowercase'`); MG6 `1 failed, 401 passed` (`test_migration_stops_on_an_email_with_an_uppercase_letter`);
  MG7 `2 failed, 400 passed` (los dos de la migración); MG8 `1 failed, 401 passed` (solo
  `test_verification_token_in_another_case_is_rejected`). Las ocho cifras = tabla del plan; los `FAILED` = handoff.
- Base de la suite sin restos: sonda en una copia aparte, un test que corre tras `tests/test_email_case.py` y lista las
  tablas de `engine_test` → `TABLES []`, sin `_alembic_tmp_users` (`18 passed`). `pre_migration_db` usa
  `create_engine("sqlite://")` propio y lo cierra con `engine.dispose()`.
- AGENTS §5 / test-sanitizer / ADR-0011: usuarios por `persist_user`/`make_user` (en la base propia, `_add` con
  `make_user`); único doble, `mock_send_email` (`autospec=True`, `tests/conftest.py:156`), afirmado con
  `assert_called_once_with(...)` y `assert_not_called()`; aserciones sobre código HTTP, claves `{"detail"}`, filas,
  claims del JWT y restricción por nombre (`match=CHECK_NAME`); ningún texto humano en español (`ÁNGEL@Test.com` es un
  dato). Commit antes: todo lo previo va por `persist_user`. Refresh después: `refresh(user)`/`refresh(tourist)` antes de
  leer atributos; `_emails` lee columnas con un `select` nuevo, no instancias del mapa de identidad.
- AGENTS §3: `CheckConstraint` con nombre explícito y texto SQL (`app/models/user.py:38`); DDL compilado para PostgreSQL y
  SQLite → `CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email))`; ningún `naming_convention` en `Base` lo
  altera. No hay columnas nuevas (S1 no cambia). Un solo punto de normalización: `git grep LowercaseEmail -- app` → 4
  líneas en `app/schemas/user.py`; ningún `field_validator` de correo ni `.lower()` nuevo (D5 no crece). A9:
  `UserResponse(BaseModel)` sigue con `email: str` (`app/schemas/user.py:147`) y `app/schemas/token.py:22` con
  `email: str`; ningún DTO de salida usa `LowercaseEmail` ni hereda de `UserBase` (los `response_model` de
  `app/api/routers/user.py` son `UserResponse` y `TokenResponse`). Correcto: la salida devuelve lo guardado tal cual. La
  migración tiene `upgrade` y `downgrade`, ambos con `batch_alter_table`.
- Verificación final, pasos 10-18 (repetidos): 10 sin salida, exit 1 · 11 `user_repository.py:18`, `:44`, `:56` · 12
  `:22`, `:39`, `:134`, `:166` · 13 migración `:2`, `app/models/user.py:1`, `app/schemas/user.py:1`,
  `tests/test_email_case.py:2` · 14 `b51f3c9e2a64 (head)` · 15 `ALTER TABLE users ADD CONSTRAINT
  ck_users_email_lowercase CHECK (email = lower(email));` entre `BEGIN;`/`COMMIT;` (downgrade: `ALTER TABLE users DROP
  CONSTRAINT ck_users_email_lowercase;`) · 16 desde `2bf29e5` → 6 archivos (ADR-0016 y los 5 de G) · 17 9 líneas, 114
  coincidencias (las 8 del paso 2 más `tests/test_email_case.py:5`) · 18 la compuerta de arriba. También 1 (exit 1), 3
  (4 líneas), 4 (las 4 de la base), 5 (1 línea), 6 tras G (solo los 3 archivos que el plan anuncia,
  `49 insertions(+), 5 deletions(-)`), 7 tras G (17 archivos) y 8 (`15 6`): todos = plan. Paso 19 (David, PostgreSQL
  local, antes de `/pr`): no lo ejecuta la auditoría; pendiente.
- `progress.json` (diff de `bf4ae56`): `Fase_G` `pending`/`null` → `completed`/`"9c9edd2"` (hash real); `last_handoff`
  reescrito; `current_target` `Fase_G` → `Fase_H`. Descripciones, fases A–F, `allowed_statuses` y `edit_rules` intactos;
  JSON válido, 0 `\r`. `Fase_H` aún no es clave de `phases`, y no es hallazgo: `edit_rules` da `current_target` a la
  sesión que ejecuta; `fase-ejecutor` (paso 4) lo manda a la "siguiente fase", y E4 fija que la siguiente es H; E4.6 hace
  que el planificador añada `Fase_H` (`pending`) "sin tocar `current_target`", así que el valor queda bien en cuanto
  exista la clave. `null` sería falso: `check_docs --estado` leería el ítem como "ejecutado (todas las fases)" con H
  pendiente; hoy dice `en ejecución (objetivo: Fase_H)`, y es cierto. `/implementar BE-34 H` no puede arrancar antes de E5.
- Verificación final completa: cumplida para A–G (pasos 1-18), salvo el paso 19, que es de David. Lo que depende de H
  queda abierto: el paso nuevo que dicte H (ningún usuario hecho a mano en `tests/test_bootstrap_superadmin_command.py`),
  la fila H de la compuerta y volver a contar los pasos 2/17 y 7, porque H vuelve a tocar ese archivo, que el patrón 2
  cuenta (16 coincidencias hoy).
- Fuera de alcance respetado: `app/repositories/`, `app/services/`, `tests/test_models_schema.py`,
  `tests/test_user_repository.py`, `tests/test_bootstrap_superadmin_command.py` (E4/H) y los demás archivos de A–E no
  aparecen en el diff.

## Auditoría Fase H — 2026-11-14
**Veredicto Fase H: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. El opcional de la auditoría de la fase E queda RESUELTO (5ec73d2): marcado en su línea, sin borrarlo.

Evidencia (re-ejecutada por el auditor, contexto fresco; copias propias en el scratchpad, el árbol del repo no se tocó):
- Árbol y rama: `git status --short` vacío; `item/be-34`, HEAD `fe1a005` sobre `5ec73d2` sobre `0dd6770`.
  `git show --numstat --format= 5ec73d2` → `18	18	tests/test_bootstrap_superadmin_command.py` (único archivo).
  `fe1a005` toca solo `docs/deuda/BE-34/handoff-Fase_H.md` y `progress.json`.
- Mensaje: `git cat-file commit 5ec73d2` = bloque "Commit" de la fase H (plan l. 1997-2013): asunto, dos párrafos y
  trailer `Co-Authored-By`, línea por línea.
- Byte a byte: un script aplica los tres cambios dictados (imports; `_add` con su docstring sobre `persist_user` entre
  `_execute` y `_count`; firma con `make_user: Callable[..., User]` y las 15 líneas del `insert` → la llamada con
  `cedula="2000000002"` y `email="root@test.com"`) al archivo de `0dd6770`, cada ancla con una sola aparición, y
  `cmp` contra el de `5ec73d2` → idénticos. 0 `\r`. `assert completed.returncode == 0, completed.stderr` aparece una
  sola vez (l. 203), igual que en la base: el `assert` duplicado del ejecutor no llegó al commit; `Callable` importado
  en l. 13 y usado en l. 129.
- Hook simulado: copia del archivo commiteado, `ruff format` + `ruff check --fix` con `--config pyproject.toml` →
  `1 file left unchanged` · `All checks passed!`; `cmp` con el commiteado → idéntico.
- E4.4 (aserciones): el archivo en `2bf29e5` y en `0dd6770` es el mismo (`cmp`); las 25 líneas con `assert` de la base y
  de H son idénticas en orden y texto (`diff` vacío). El test conserva `main() == 1`, `[("2000000002",
  UserRole.tourist)]`, `AuditLog == 0`, `output.out == ""` y `PASSWORD not in output.err`. `make_user` da
  `role=UserRole.tourist`, `is_active=True` y `data_consent=True` por defecto (`tests/conftest.py:183-203`).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1034 15 148 13 97.63%` ·
  `691 passed, 8 warnings in 20.36s` · `Compuerta superada.` = fila H del plan y = fila G (ratchet: tests, cobertura,
  contratos, ruff y mypy sin cambio). Los 8 warnings, de los mismos tests que en G (`test_route_guards` ×3,
  `test_services` ×3, `test_user_response` ×2). Sobre el archivo: `ruff check` limpio, `ruff format --check`
  `1 file already formatted`, `mypy` `Success: no issues found in 1 source file`, `pytest` `8 passed in 1.93s`.
- Mutantes (procedimiento común, `git archive` en directorios nuevos; suite sin `test_check*`). Sin mutante: base
  (`0dd6770`) y H (`5ec73d2`) → `402 passed, 8 warnings`. ME2 → `1 failed, 401 passed`; MD5 → `8 failed, 394 passed`;
  MH1 → `1 failed, 401 passed`; MH2 → `1 failed, 401 passed`; MH3 → `7 failed, 395 passed`, en las dos copias; las
  listas de `FAILED` más la última línea (sin tiempos), idénticas base/H con `cmp` en los cinco, y las mismas que
  "Aplicación de E4". ME2, MH1 y MH2 tumban solo `test_command_fails_when_the_email_belongs_to_another_account`.
  MHT1 (sin `await session.commit()` en `_add`) → `1 failed, 401 passed`, solo ese test. MHT2 (sin
  `await engine.dispose()`) → sobrevive, `402 passed, 8 warnings`; `-X dev` sobre el archivo → `1` `ResourceWarning`;
  sin mutante, copia H → `0`, copia base → `0`. = tabla del plan (l. 175-179) y fe de erratas de E5.5.
- AGENTS §5 / test-sanitizer / ADR-0011: el turista sale de `make_user` (fábrica central); no hay mocks; ningún
  `insert(User)` ni `User(` a mano en los tests de A–E (paso 20); ninguna aserción sobre texto en español (`PASSWORD`
  es la constante del archivo). El test no usa `client` ni `db_session`: escribe con `_add` (commit en su propia sesión,
  antes de `main()`) y lee con `_execute` (motor nuevo, `select` de columnas), así que no hay instancia del mapa de
  identidad que refrescar. La frase de E4.3 está en el docstring de `_add`. Motor cerrado con `dispose()`, como
  `_create_schema` y `_execute`.
- `progress.json` (diff `0dd6770..fe1a005`): `Fase_H` `pending`/`null` → `completed`/`"5ec73d2"`; `last_handoff`
  reescrito; `current_target` `"Fase_H"` → `null`. Descripciones, fases A–G, `allowed_statuses` y `edit_rules` intactos;
  JSON válido. Las ocho fases `completed` con hash real (`git log -1` de `d873b49`, `b08491b`, `f83a511`, `e9d010c`,
  `2bf29e5`, `4eba2d2`, `9c9edd2`, `5ec73d2` → el asunto de cada fase). `null` es coherente: `edit_rules` da
  `current_target` a la sesión que ejecuta, no hay fase siguiente, y los otros 16 ítems cerrados de `docs/deuda/`
  tienen `current_target` `null`. `scripts/check_docs.py --estado` →
  `BE-34: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, …,
  Fase_H → última auditoría: PASS`.
- Verificación final (última fase), repetida: 1 → sin salida, exit 1 · 2/17 → 9 líneas (`.env.example:6`,
  `app/cli/bootstrap_superadmin.py:19`, `app/core/config.py:12`, `app/repositories/user_repository.py:1`,
  `app/services/superadmin_bootstrap.py:3`, `tests/test_bootstrap_superadmin_command.py:16`, `tests/test_config.py:41`,
  `tests/test_email_case.py:5`, `tests/test_superadmin_bootstrap.py:11`), 114 · 3 → 4 líneas
  (`bootstrap_superadmin.py:90`, `superadmin_bootstrap.py:60`, `user_service.py:88`, `:412`) · 4 →
  `dependencies.py:199`, `routers/user.py:35`, `user_access_policy.py:67`, `:72` · 5 → `tests/test_config.py:243` ·
  6 → los 3 archivos de G, `49 insertions(+), 5 deletions(-)` · 7 → 17 archivos · 8 → `15 6` · 9/18 → la compuerta de
  arriba · 10 → exit 1 · 11 → `:18`, `:44`, `:56` · 12 → `app/schemas/user.py:22`, `:39`, `:134`, `:166` · 13 →
  migración `:2`, `app/models/user.py:1`, `app/schemas/user.py:1`, `tests/test_email_case.py:2` · 14 →
  `b51f3c9e2a64 (head)` · 15 → contiene `ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email =
  lower(email));` · 16 (desde `2bf29e5`) → 7 archivos (los 6 de F y G más `tests/test_bootstrap_superadmin_command.py`)
  · 20 → sin salida, exit 1 · 21 → `:129` y `:132` · 22 → `1 file changed, 18 insertions(+), 18 deletions(-)` · 23 →
  `0` (con MHT2, `1`). Todos = plan.
- Paso 19 (de David; el auditor no lo ejecuta): consta en `docs/bitacora/2026-11-14.md`, sección "Paso 19 de la
  Verificación final" (commit `4a8508f`): 19a se detuvo primero (`CheckViolationError` por una fila de prueba local con
  mayúsculas, corregida solo en la base local) y después aplicó `Running upgrade 2cc4b57c136c -> b51f3c9e2a64`; 19b
  `No new upgrade operations detected.`; 19c `ck_users_email_lowercase · CHECK (((email)::text = lower((email)::text)))`.
  PostgreSQL 15 local (asyncpg), no Azure. Es la salida que pegó David, transcrita por la sesión Mentor.
- Verificación final completa: cumplida (1-18 y 20-23 por el auditor; 19 con constancia en la bitácora).
- Pendiente antes de `/pr` según el plan (no son hallazgos de H): R1 cerrado por `8412e19` (AGENTS §3, l. 53-58,
  comandos de operador y correo en minúsculas); R2 saldado por F y G; R10 retirado. Quedan: R5 (`docs/CONTEXT.md` sin
  ADR-0015/ADR-0016 ni `app/cli/`, cierre del ítem), R4 (manual técnico), R6 (nota en BE-35), R12 (declararlo en el PR),
  R9 (si David prefiere B intacta), R3/R13 ya con fila (BE-52, BE-54), R7 y R11 sin fila salvo petición. Q1 se repite
  antes de promover a `staging` y a `main` (plan l. 1370); la primera ejecución en Azure es el CD de `develop` con Q1 = 0.

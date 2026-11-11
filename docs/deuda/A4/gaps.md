# Gaps — A4

## Auditoría Fase A — 2026-11-10
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`):

- Árbol: `git status --short` limpio. `git diff --name-only db2be61 HEAD` → `docs/deuda/A4/handoff-Fase_A.md`,
  `docs/deuda/A4/progress.json`, `tests/test_token_failure_paths.py`. `git show --stat 21ee9fc` → solo
  `tests/test_token_failure_paths.py` (69+, 1-), el único archivo de la fase.
- Commit `21ee9fc`: asunto idéntico al del plan (`test(auth): pin JWT signature checks on both decode paths (A4)`);
  el cuerpo trae el porqué (CONTEXT 8.1), qué fija cada test, M1/M2 con conteos y el límite del tercer test.
- Diff contra "Cambios exactos": imports `Path`, `dotenv_values`, `AsyncSession`, `create_verification_token`;
  `VERIFY_ROUTE`, `FOREIGN_KEY`, `ENV_EXAMPLE` tras `PROTECTED_ROUTE`; `_resign` y `_env_example_jwt_key` literales,
  junto a `_bearer`; los tres tests con nombre, firma, docstring y aserciones del plan (401 vía `_assert_bearer_401`;
  400 + `set(body) == {"detail"}` + `detail` str + `refresh` + `is_active is False`). Ni `make_token`, ni otros
  tests, ni `app/` tocados.
- `progress.json`: `Fase_A` `completed` con `21ee9fc` (hash real), `current_target` = `Fase_B`, `last_handoff`
  presente, `edit_rules` intacto, JSON válido.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): `57 files already formatted` ·
  `Found 8 errors.` (los 8 I001 heredados de `app/`) · `Found 9 errors in 5 files (checked 53 source files)` ·
  `Contracts: 4 kept, 0 broken.` · `552 passed, 5 warnings` · `TOTAL … 96.11%`. Fila A de la tabla exacta;
  cobertura = línea base (96.11 %).
- Archivo tocado: `ruff check` → `All checks passed!`; `ruff format --check` → `1 file already formatted`;
  `mypy tests/test_token_failure_paths.py` → 5 errores, todos en `app/` (heredados), 0 en el test.
- Mutantes re-medidos en copias `git archive 21ee9fc` del scratchpad, sin `.env`, con el env del plan
  (`-k signed_with`): sin mutante `3 passed, 14 deselected`; M1 (`app/api/dependencies.py:95`) `2 failed, 1 passed`
  (fallan los dos de token de acceso); M2 (`app/services/user_service.py:124`) `1 failed, 2 passed` (falla el de
  verificación). Coinciden con el plan y con el handoff.
- Verificación final #9 (estado tras A): 3 líneas, `tests/test_token_failure_paths.py:57`, `:189`, `:202`.
- AGENTS §5: usuarios y tokens por fábricas (`persist_user`, `make_token`), sin mocks nuevos, refresh tras la
  petición (ADR-0011), ninguna aserción sobre texto en español.

## Auditoría Fase B — 2026-11-10
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`):

- Árbol: `git status --short` limpio al empezar. `git diff --name-status 7f46c5e HEAD` → `A app/core/config.py`,
  `A conftest.py`, `A tests/test_config.py`, `A docs/deuda/A4/handoff-Fase_B.md`, `M docs/deuda/A4/progress.json`.
  `git show --stat 43d28f5` → solo los 3 archivos de la fase (325+).
- Commit `43d28f5`: asunto idéntico al del plan (`feat(config): add validated Settings and a .env-free test env (A4)`);
  el cuerpo trae el porqué (15 lecturas sin validar, `.env` por efecto lateral, suite atada a `.env`), un bullet por
  archivo, las sondas (a)–(d), `DatabaseSettings` por el CD (P1, ADR-0013), consumidores en C–G y el trailer.
- `progress.json`: JSON válido; `Fase_B` `completed` con `43d28f5` (hash real); `current_target` = `Fase_C`;
  `last_handoff` presente; `edit_rules` intacto (el diff `7f46c5e..HEAD` solo cambia status, commit, target y handoff).
- Diff contra "Cambios exactos": `conftest.py` idéntico al bloque del plan (`diff` vacío). `app/core/config.py` igual
  palabra por palabra (`diff` por palabras vacío); solo cambia el corte de línea de 3 líneas de docstring que, sin la
  sangría del plan, miden 102, 105 y 101 columnas (`line-length = 100`, `E` seleccionado). Desviación 1 aceptable: la
  exige la regla "archivos tocados con 0 errores". P3 presente (`config.py:34`, `hide_input_in_errors=True`);
  `extra="ignore"` (`:33`); `ENV_FILE` por la ruta del módulo (`:17`).
- `tests/test_config.py`: 21 casos (5+5+1+1+1+1+1+1+2+1+1+1) con los nombres y aserciones del plan; entorno solo por
  `monkeypatch.setenv/delenv` (`git grep "os\.environ|getenv" -- tests/test_config.py` → 0). Desviación 2 (caso 8,
  `:171`, `{e["loc"]} == {(name,) for name in others}`) aceptable: endurece la aserción dictada sin quitarla
  (AGENTS §5). Desviación 3 (caso 9, `:175`, `Callable[[], DatabaseSettings]`) aceptable: el plan no dicta la anotación,
  es correcta para ambos getters (mypy limpio) y mantiene la Verificación final #4 en 3 líneas, todas en
  `app/core/config.py` (`:13`, `:20`, `:30`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): `60 files already formatted` ·
  `Found 8 errors.` (los 8 I001 heredados: `dependencies.py`, `routers/audit.py`, `email.py`, `database.py`,
  `user_repository.py`, `schemas/audit.py`, `audit_service.py`, `user_service.py`) ·
  `Found 9 errors in 5 files (checked 55 source files)` (los 9 `[arg-type]` heredados) · `Contracts: 4 kept, 0 broken.` ·
  `573 passed, 5 warnings` · `TOTAL … 96.23%`. Fila B exacta; cobertura ≥ 96.11 %.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
  `mypy app/core/config.py tests/test_config.py conftest.py` → `Success: no issues found in 3 source files`.
- Mutantes re-medidos en copias `git archive 43d28f5` del scratchpad, sin `.env`, sin las 5 obligatorias: sin mutante
  (`-k "echo_values or unknown_keys"`) `2 passed, 19 deselected`; M9 (línea `hide_input_in_errors=True,` borrada)
  `-k echo_values` → `1 failed, 20 deselected`; M10 (`:33` `extra="forbid",`) `-k unknown_keys` →
  `1 failed, 20 deselected`. Coinciden con el plan y el handoff.
- Suite sin `.env` (criterio de B), copia `git archive 43d28f5`, `test ! -e .env`, `env -u` de las 5 obligatorias:
  `573 passed, 5 warnings`. P5 (orden de carga): en esa copia, `pytest tests/test_auth.py` → `19 passed`; desde
  `tests/`, `pytest test_auth.py test_config.py` → `40 passed`; con el `conftest.py` raíz borrado →
  `ArgumentError: Expected string or URL object, got None` (el mismo error de colección de `55345a1`).
- P3 con sonda propia (`env -i`, sin `JWT_SECRET_KEY`, `Settings(_env_file=None)`): `ValidationError`; el texto
  contiene `jwt_secret_key` y `Field required`, y no contiene `a@test.com` ni `UseDevelopmentStorage`.
- Verificación final, estado tras B: #2 → 1 línea (`conftest.py:28`); #4 → 3 líneas en `config.py`; #9 → las 3 líneas
  de la fase A (`tests/test_token_failure_paths.py:57`, `:189`, `:202`).
- AGENTS: sin mocks; sin usuarios ni tokens a mano; inglés; docstrings Google en lo público; aserciones sobre
  `type`/`loc` de pydantic, valores e identidad, ninguna sobre texto en español. Ninguna excepción de dominio nueva.

## Auditoría Fase C — 2026-11-10
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia:

- Árbol: `git status --short` limpio. `git diff --stat 41a457a..HEAD` → solo `tests/conftest.py`, `tests/test_auth.py`,
  `tests/test_user_service.py` (commit `cbf439c`, 38+/30-) y `docs/deuda/A4/handoff-Fase_C.md`,
  `docs/deuda/A4/progress.json` (commit `429b17c`). Nada en `app/`.
- Commit `cbf439c`: asunto idéntico al del plan (`test(auth): drop JWT constant imports; sign tokens with make_token (A4)`);
  cuerpo con el porqué (D borra las constantes), un bullet por archivo, M3/M4 y el trailer.
- `progress.json`: JSON válido; `Fase_C` `completed` con `cbf439c` (hash real, `git show --stat` lo confirma);
  `current_target` = `Fase_D`; `last_handoff` presente; `edit_rules` idéntico al de `41a457a`.
- Diff contra "Cambios exactos": `make_token` con `extra_claims: dict[str, Any] | None = None` keyword-only, mezclado con
  `update` sobre `{"sub", "role"}` y documentado en el docstring (`tests/conftest.py:219-227`), `from typing import Any`;
  `test_user_service.py` importa solo `create_verification_token, get_password_hash` + `get_settings`, los dos decodes con
  `settings.jwt_secret_key`/`[settings.algorithm]`, los dos `jwt.encode` sustituidos por las llamadas a `make_token`
  dictadas y sus tests reciben `make_user, make_token`; `from datetime import timedelta`. `test_auth.py`: fuera
  `ALGORITHM, SECRET_KEY` y `assert SECRET_KEY is not None`; decode con `get_settings()`. Todo presente, nada de más.
- Punto a juzgar (token de scope equivocado con `role` y 30 min en vez de 5): aceptable, no debilita el test.
  `verify_email_account` (`app/services/user_service.py:123-138`) solo mira firma, `exp`, `sub` y `scope`; ignora `role`.
  El token tiene firma válida, `exp` futuro (30 min o 5, da igual: no caduca durante el test) y `sub` presente, así que
  el único motivo posible del `InvalidVerificationTokenError` es `scope`; M4 (quitar el chequeo de scope) lo mata
  (`1 failed`). El claim `role` además lo acerca a un token de acceso real. `make_token(extra_claims=...)` se ajusta a lo
  dictado (tipo, keyword-only, mezcla "sobre" la base, docstring).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): `60 files already formatted` ·
  `Found 8 errors.` (los 8 I001 heredados en `app/`: `dependencies.py`, `routers/audit.py`, `email.py`, `database.py`,
  `user_repository.py`, `schemas/audit.py`, `audit_service.py`, `user_service.py`) ·
  `Found 5 errors in 4 files (checked 55 source files)` (`database.py:11`, `security.py:71,87`, `user_service.py:124`,
  `dependencies.py:95`; desaparecen los 4 de `tests/test_user_service.py`) · `Contracts: 4 kept, 0 broken.` ·
  `573 passed, 5 warnings` · `TOTAL … 96.23%`. Fila C exacta; cobertura = B (96.23 %) ≥ base (96.11 %).
- Archivos tocados: `ruff check` → `All checks passed!`; `mypy tests/conftest.py tests/test_user_service.py
  tests/test_auth.py` → ninguna línea `tests…` (los 5 errores que informa son de `app/`, seguidos por import).
- Criterio: `git grep -n -E "\bSECRET_KEY\b|import .*\bALGORITHM\b|ALGORITHM,$" -- tests` → sin salida (exit 1).
- Mutantes re-medidos en copias `git archive HEAD` del scratchpad, sin `.env`: sin mutante
  (`-k "expired_token or wrong_scope"`) `2 passed, 17 deselected`; M3 (`124: … options={"verify_exp": False})`)
  `-k expired_token` → `1 failed, 18 deselected`; M4 (`137: if email is None:`) `-k wrong_scope` →
  `1 failed, 18 deselected`. Coinciden con el plan y el handoff.
- AGENTS: sin mocks nuevos; tokens por la fábrica de `conftest.py`, ninguno a mano; inglés; ninguna aserción sobre
  texto en español; ninguna excepción de dominio nueva. E0 no afecta a C. La Verificación final #6 aún encuentra
  `tests/test_main.py:3,49` (`DEFAULT_CORS_ORIGINS`), que el plan asigna a la fase F: no es hallazgo de C.

## Auditoría Fase D — 2026-11-10
**Veredicto Fase D: PASS (0 bloqueantes, 2 opcionales).**

[OPCIONAL] — Fase D — Tras el `ruff --fix` de I001, los comentarios `# Repository injection` y `# Service injection` ya no encabezan los bloques que describen: el primero queda entre `service_repository` y `user_repository`, el segundo tras `audit_service`, `tourist_services_service` y `user_access_policy`. No afecta a la corrección. El plan dicta solo el `--fix` y la fase G declara fuera de alcance "el resto de `dependencies.py`", así que el ejecutor hizo bien en no tocarlos. Destino: residual del PR o fila de backlog (retirarlos o dejar uno solo sobre el bloque `app.*`) — app/api/dependencies.py:13,20
[OPCIONAL] — Fase D — Ya existía antes de esta fase y no forma parte del alcance de A4: `get_current_user` no comprueba `scope`, así que un token de verificación (`scope=email_verification`, `sub`=correo, 15 min) se acepta como bearer de un usuario activo. D no lo debilita: `git show d528748:app/api/dependencies.py | grep scope` → sin salida. Riesgo bajo, porque el portador es el dueño del correo. Destino: `docs/backlog.md` (seguridad, Baja) — app/api/dependencies.py:106-110

Evidencia:

- Árbol: `git status --short` limpio. `git diff --stat d528748..HEAD` → los 4 archivos de la fase (`e4602cf`, 75+/32-)
  más `docs/deuda/A4/handoff-Fase_D.md` y `docs/deuda/A4/progress.json` (`1b43c2b`). Nada fuera de la fase.
- Commit `e4602cf`: asunto idéntico al del plan (`refactor(auth): sign and verify JWTs with the injected Settings (A4)`).
  El cuerpo da el porqué, un bullet por archivo, la compuerta y los mutantes, y termina en el trailer.
- `progress.json`: JSON válido; `Fase_D` `completed` con `e4602cf` (hash real, `git show --stat` lo confirma);
  `current_target` = `Fase_E`; `last_handoff` presente; `edit_rules` sin cambios en el diff de `1b43c2b`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1), fila D exacta:
  `60 files already formatted` · ruff `Found 6 errors.`, los 6 I001 heredados (`routers/audit.py`, `email.py`,
  `database.py`, `user_repository.py`, `schemas/audit.py`, `audit_service.py`), asignados a E e I · mypy
  `Found 1 error in 1 file (checked 55 source files)` en `app\db\database.py:11` (fase E) ·
  `Contracts: 4 kept, 0 broken.` · `574 passed, 5 warnings` · `TOTAL … 96.23%`, igual que C y ≥ 96.11 % de la base.
- Archivos tocados: `ruff check` sobre los 4 → `All checks passed!`. `mypy` sobre los 4 → solo `database.py:11`,
  que entra por el import y no es de esta fase. Han desaparecido `security.py:71,87`, `dependencies.py:95` y `user_service.py:124`.
- Diff contra "Cambios exactos". `security.py`: sin `import os` ni las 4 constantes; `get_settings()` en las dos
  funciones; docstrings con Args/Returns. `dependencies.py`: el import pasa a ser `Settings, get_settings`;
  `settings: Settings = Depends(get_settings)` es el tercer parámetro; decode con `settings.jwt_secret_key` y
  `[settings.algorithm]`; docstring con Args/Returns/Raises; I001 resuelto. `user_service.py`: pierde `SECRET_KEY, ALGORITHM`;
  `settings = get_settings()` antes del `try`; I001 resuelto. Test: importa `get_settings` y `app`; test nuevo con el
  nombre, las fábricas y el docstring dictados. Todo está presente y no hay nada de más.
- Punto 1 (arquitectura): `git grep -n -E "os\.getenv|getenv\(|environ"` sobre los 3 archivos de `app/` → sin salida.
  `security.py` y `user_service.py` no importan `fastapi` ni `starlette`; `dependencies.py`, que es capa HTTP, sí, y recibe
  `Settings` por `Depends`. import-linter: 4 kept.
- Punto 2 (seguridad): las dos rutas siguen fijando la lista de algoritmos (`algorithms=[settings.algorithm]`,
  dependencies.py:107, user_service.py:124), sin `options`, así que la verificación de firma y de `exp` sigue por defecto.
  `sub` sigue comprobándose en dependencies.py:109 y `sub`+`scope` en user_service.py:136. `alg=none` tampoco se cuela:
  PyJWT rechaza `none` con clave no vacía, y `jwt_secret_key` es `min_length=1`. El origen del algoritmo es el mismo que
  antes (variable de entorno con default `HS256`); ahora además pasa por la validación de `Settings`.
- Punto 3b: la única llamada directa a `get_current_user` del repo (`git grep -n "get_current_user("`) está en
  tests/test_token_failure_paths.py:262 y pasa `settings=get_settings()`. El handoff dice `:263`, una línea de
  desfase que no cambia nada.
- Punto 3c: `git ls-files --eol` → `i/lf w/lf attr/text=auto eol=lf` en los 4 archivos.
- Mutantes re-medidos en copias `git archive e4602cf` del scratchpad, sin `.env`, una por mutante. Sin mutante
  (`-k "signed_with or injected_settings"`) → `4 passed, 14 deselected`. M1' (`107: … options={"verify_signature":
  False, "verify_exp": True})`, `-k signed_with`) → `2 failed, 1 passed, 15 deselected`. M2' (`124: …` igual) →
  `1 failed, 2 passed, 15 deselected`. M5 (`107: jwt.decode(token, get_settings().jwt_secret_key, …`,
  `-k injected_settings`) → `1 failed, 17 deselected`. Coinciden con el plan y con el handoff.
- AGENTS: el test nuevo usa las fábricas (`persist_user`, `make_auth_headers`), no tiene mocks, y el override lo limpia
  `dependency_overrides.clear()` (tests/conftest.py:96). Afirma código, cabecera y estructura con `_assert_bearer_401`,
  sin texto en español. No hay excepciones de dominio nuevas. El texto no dictado no nombra variables de entorno en
  mayúsculas en `app/` y no usa "another/other key" ni "forged" en `tests/`. E0 no afecta a D.

## Auditoría Fase E — 2026-11-10
**Veredicto Fase E: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia:

- Árbol: `git status --short` limpio al empezar. `git diff --name-only 6104d15 HEAD` → los 4 archivos de la fase
  (`59d75b7`, 50+/32-: `alembic/env.py`, `app/core/email.py`, `app/db/database.py`, `tests/test_email.py`) más
  `docs/deuda/A4/handoff-Fase_E.md` y `docs/deuda/A4/progress.json` (`18662f2`). Nada fuera de la fase.
  `git diff --stat 55345a1 HEAD -- .azure-pipelines` → vacío: `cd-pipeline.yml` intacto (E0.1).
- Commit `59d75b7`: el asunto es idéntico al del plan (`refactor(config): engine, migrations and SMTP client read Settings (A4)`).
  El cuerpo declara el cambio de remitente (`tu_correo@gmail.com` → `MAIL_USERNAME` sin `MAIL_FROM`) y explica por qué
  el CD sigue intacto (`DatabaseSettings`, P1/E0). Termina en el trailer.
- `progress.json`: JSON válido. `Fase_E` está en `completed` con `59d75b7` (hash real, `git show --stat` lo confirma);
  `current_target` = `Fase_F`; `last_handoff` presente. El diff de `18662f2` no toca `edit_rules`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1), fila E exacta:
  `60 files already formatted` · ruff `Found 4 errors.`, los 4 I001 que el plan deja para I (`routers/audit.py`,
  `user_repository.py`, `schemas/audit.py`, `audit_service.py`) · mypy `Success: no issues found in 55 source files` ·
  `Contracts: 4 kept, 0 broken.` · `575 passed, 5 warnings` · `TOTAL 971 23 138 19 96.21%` ·
  `Compuerta NO superada: ruff check`. Coincide con lo que pegó el ejecutor.
- Cobertura: 96.21 % ≥ 96.11 % (umbral del plan, `plan.md:128`). La explicación del ejecutor cuadra con la tabla:
  en D era `975 23 138 19 96.23%` (`handoff-Fase_D.md:133`); `Miss`, `Branch` y `BrPart` no cambian, y `Stmts`
  baja en 4. `database.py` pierde 4 sentencias y gana 1 (−3). `email.py` pierde 4 (`import os`, `dotenv`,
  `load_dotenv()`, `conf`) y gana 3 (import, `def _smtp_config`, `return`) (−1). `alembic/` no se mide
  (`source = ["app"]`). Ninguna línea nueva queda sin cubrir: `email.py` está entre los 25 archivos con cobertura
  completa, y en `database.py` solo faltan `31-35` (cuerpo de `get_db`, que la suite sustituye; ADR-0011), que ya
  faltaban antes.
- Archivos tocados: `ruff check` de los 4 → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` sobre `email.py`, `database.py` y `test_email.py` → `Success: no issues found in 3 source files`; sobre
  `alembic/env.py`, que no está en `mypy.files` → `Success: no issues found in 1 source file`.
- Diff frente a "Cambios exactos". `database.py`: sin `os`, `dotenv`, `load_dotenv()` ni `DATABASE_URL`; usa
  `get_database_settings().database_url`; `echo=True` y su comentario siguen igual (A5); I001 resuelto.
  `alembic/env.py`: sin `os`, `dotenv`, `load_dotenv()`, `database_url` ni `raise ValueError`; el comentario dictado
  aparece literal y le sigue `set_main_option(..., get_database_settings().database_url)`. `email.py`: los imports
  dictados; `_smtp_config(settings: Settings) -> ConnectionConfig` con docstring Google (Args/Returns), los 5 campos de
  `settings`, `mail_sender` incluido, y los 5 fijos sin cambios; `fast_mail = FastMail(_smtp_config(get_settings()))`;
  I001 resuelto. Plantilla y `send_verification_email` sin tocar. Test: nombre y tupla de 5 campos dictados.
- P1 (E0): `database.py` y `alembic/env.py` llaman a `get_database_settings()`, no a `get_settings()`. Sonda re-medida
  en exportaciones `git archive` de `55345a1` y `HEAD` en el scratchpad, sin `.env` (`test ! -e .env`) y con los 15
  campos quitados del entorno (`env -u …`). Con solo `DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db"`,
  `-m alembic upgrade head --sql` → `base: exit=0 lines=116` y `head: exit=0 lines=116`; `cmp` → idénticos. Sin
  `DATABASE_URL` en `HEAD` → `exit=1`; stderr `1 validation error for DatabaseSettings` / `database_url` /
  `Field required [type=missing]` (2 apariciones de `database_url`; ninguna de `postgresql` ni de valores). No se
  ejecutó nada contra una base real.
- M6, en una copia `git archive HEAD` sin `.env`. El `sed` del plan deja `25:        MAIL_FROM=settings.mail_username,`;
  `tests/test_email.py -k configured_from_settings` → `1 failed, 6 deselected`
  (`FAILED tests/test_email.py::test_smtp_client_is_configured_from_settings`). En otra copia, sin mutante →
  `1 passed, 6 deselected`. La caracterización que dicta el plan ("pasa antes y después") se cumple: en una copia de
  `6104d15` (código con `os.getenv("MAIL_FROM", "tu_correo@gmail.com")`) con el `tests/test_email.py` de `59d75b7`,
  `tests/test_email.py` → `7 passed`.
- Punto 3: `git grep -n -E "getenv|load_dotenv|os\.environ" -- app/db alembic app/core/email.py` → sin salida (exit 1).
  `echo=True` sigue en `database.py:7`; `sqlalchemy.future` sigue en los 3 repositorios (S2). `app/services` no importa
  `fastapi` ni `starlette`; import-linter: 4 kept.
- Punto 4: `git ls-files --eol` → `i/lf w/lf attr/text=auto eol=lf` en los 4 archivos.
- Verificación final, en lo que esta fase cambia: #3 → 1 línea (`tests/test_token_failure_paths.py:16`; la segunda
  llega con H). #7 en `app tests` → 0. #5 → 4 líneas, todas en `app/main.py` (`:170,189,196,200`); `:196` y `:200` las
  retira F, y ya no aparece `DATABASE_URL`.
- AGENTS: el test nuevo no usa mocks ni fábricas de usuario (no los necesita) y afirma sobre valores de configuración,
  sin texto en español. No hay excepciones de dominio nuevas. El texto no dictado (docstring de `_smtp_config`) no
  nombra variables de entorno en mayúsculas. El límite E0.7 (arranque local desde `.env` entre E y G) está aceptado:
  no es hallazgo.

## Auditoría Fase F — 2026-11-10
**Veredicto Fase F: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia:

- Árbol: `git status --short` limpio al empezar. `git diff --name-only feabea0 HEAD` → los 4 archivos de la fase
  (`311b19e`, 45+/19-: `app/api/routers/user.py`, `app/main.py`, `tests/test_auth.py`, `tests/test_main.py`) más
  `docs/deuda/A4/handoff-Fase_F.md` y `docs/deuda/A4/progress.json` (`973aa77`). Nada fuera de la fase.
- Commit `311b19e`: el asunto es idéntico al del plan (`refactor(api): CORS origins and frontend URL come from Settings (A4)`).
  El cuerpo explica el porqué (las dos últimas lecturas `os.getenv` de la capa HTTP), lleva un bullet por archivo, el
  RED y M7. Termina en el trailer.
- `progress.json`: JSON válido. `Fase_F` está en `completed` con `311b19e` (hash real, `git show --stat` lo confirma);
  `current_target` = `Fase_G`; `last_handoff` presente. El diff de `973aa77` no toca `edit_rules`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1), fila F exacta:
  `60 files already formatted` · ruff `Found 4 errors.`, los 4 I001 que el plan deja para I (`routers/audit.py`,
  `user_repository.py`, `schemas/audit.py`, `audit_service.py`) · mypy `Success: no issues found in 55 source files` ·
  `Contracts: 4 kept, 0 broken.` · `576 passed, 5 warnings` · `TOTAL 969 23 138 19 96.21%` ·
  `Compuerta NO superada: ruff check`. Coincide con lo que pegó el ejecutor.
- Cobertura: 96.21 % ≥ 96.11 % (umbral del plan, `plan.md:128`), igual que en E. `Stmts` baja de 971 a 969 y
  `Miss`/`Branch`/`BrPart` no cambian. `app\main.py` `57 6 18 5 85.33%`, `Miss` `61, 72, 76, 79, 82, 106`: las mismas
  ramas de handlers que en E, desplazadas una línea por el `import os` borrado. `routers/user.py` y `core/config.py`
  no aparecen en el informe (cobertura completa).
- Archivos tocados: `ruff check` de los 4 → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` → `Success: no issues found in 4 source files`; `git ls-files --eol` → `i/lf w/lf attr/text=auto eol=lf` en
  los 4.
- Diff frente a "Cambios exactos". `main.py`: sin `import os`, `DEFAULT_CORS_ORIGINS`, el comentario de tres líneas
  ni `CORS_ORIGINS`; importa `get_settings`; el comentario dictado aparece literal sobre `app.add_middleware`, con
  `allow_origins=parse_cors_origins(get_settings().cors_origins),`. `parse_cors_origins` no cambia, y
  `allow_credentials=False`, `allow_methods=["*"]` y `allow_headers=["*"]` siguen igual con sus comentarios (SEC1). El
  comportamiento de CORS es el mismo: misma función, mismo valor por defecto (`Settings.cors_origins` =
  `http://localhost:3000`), y sigue fallando al importar si hay comodín. `routers/user.py`: sin `import os`; importa
  `Settings, get_settings`; `registrar_turista` tiene `settings: Settings = Depends(get_settings)` como último
  parámetro, con su línea `Args`, y `frontend_url = settings.frontend_url.rstrip("/")`. Ruta `/registro`,
  `response_model`, `status_code` y textos sin cambios. El router solo orquesta: recibe, delega en `UserService` y
  encola el correo. `test_main.py`: los imports dictados; el helper `_allowed_origins()` toma el único `Middleware`
  con `cls is CORSMiddleware`; `:49` usa `Settings.model_fields["cors_origins"].default`; el resto usa
  `_allowed_origins()`; `test_configured_cors_origins_have_no_wildcard` añade la igualdad dictada. `test_auth.py`:
  `from app.main import app` y el test con el nombre, el override y el `assert_called_once_with` dictados.
- RED: con el código de `feabea0`, el `base_url` era `http://localhost:3000`, el valor de `os.getenv` que el override
  de `get_settings` no alcanza. El RED de ejecución lo pegó el ejecutor (`handoff-Fase_F.md:57-62`); es coherente con el
  diff y con M7.
- M7, en una copia `git archive 311b19e` del scratchpad sin `.env` (`test ! -e .env`). El `sed` del plan deja
  `68:    frontend_url = settings.frontend_url`; `tests/test_auth.py -k frontend_url` → `1 failed, 19 deselected`
  (`FAILED tests/test_auth.py::test_register_builds_the_verification_link_from_frontend_url`, `Actual: … base_url='https://front.example/'`).
  En otra copia, sin mutante (`68:    frontend_url = settings.frontend_url.rstrip("/")`) → `1 passed, 19 deselected`.
- Suite exportada sin `.env` y con `env -u` de las 5 obligatorias → `576 passed, 5 warnings`.
- Criterios y Verificación final. `git grep -n "DEFAULT_CORS_ORIGINS" -- app tests` → sin salida. #5 → 2 líneas, su
  valor final: `app/main.py:168` (docstring de `parse_cors_origins`) y `app/main.py:187` (su `ValueError`). #6 → sin
  salida. #1 → 3 líneas, todas en `app/core/storage.py:42-44` (fase G). #9 sigue en 3 líneas. `git grep -n -E "import os|getenv" -- app/main.py app/api/routers/user.py` → sin salida.
- Desviación declarada (a), `assert isinstance(origins, list)` en `_allowed_origins()`: aceptable. Starlette tipa
  `Middleware.kwargs` con valores `object`, y la aserción estrecha el tipo sin `cast` ni `type: ignore`. No oculta
  nada: si el middleware recibiera otra cosa que una lista, el helper fallaría en voz alta, que es más estricto que un
  `cast`. Hace redundante el `assert isinstance(_allowed_origins(), list)` que sigue en el test, pero esa línea viene
  del test original y el plan no la quita. No es hallazgo.
- Desviación declarada (b), `# === CORS ===` en `app/main.py:164` seguido de dos líneas en blanco: no es hallazgo.
  `ruff format` lo acepta, deja las dos líneas que PEP 8 pide antes de una función de nivel superior, la cabecera sigue
  encabezando la sección y no afecta a la corrección ni a ningún requisito del plan. Tocarla saldría de lo dictado.
- AGENTS: el router recibe la configuración por `Depends` (§3, decisión 2 del plan); `app/services` no importa
  `fastapi` ni `starlette`; import-linter: 4 kept. El test nuevo afirma sobre el código HTTP y sobre la llamada al
  mock con todos sus argumentos (`mock_send_email`, doble global de `tests/conftest.py`), sin texto en español. Su
  override de `get_settings` lo limpia el `dependency_overrides.clear()` del fixture `client`. No hay excepciones de
  dominio nuevas. El texto no dictado (docstring de `_allowed_origins`, línea `Args` de `settings`) no nombra variables
  de entorno en mayúsculas. El límite E0.7 (Azure sigue con `os.getenv` hasta G) está aceptado: no es hallazgo.

## Auditoría Fase G — 2026-11-10
**Veredicto Fase G: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia:

- Árbol y commits: `git status --short` limpio. `714e05a` (`refactor(storage): build the Azure adapter from injected
  Settings (A4)`, mensaje idéntico al del plan, con `Co-Authored-By`) toca solo `app/api/dependencies.py`,
  `app/core/storage.py` y `tests/test_storage.py` (71+/23-), los tres archivos de la fase. `35c263c` solo
  `handoff-Fase_G.md` y `progress.json`. `progress.json`: `Fase_G` `completed` con `714e05a` (real, `git show --stat`),
  `current_target` `Fase_H`, `last_handoff` presente, `edit_rules` intacto (diff de `35c263c`).
- Compuerta re-ejecutada (exit 1), igual a la fila G y a lo que pegó el ejecutor: `60 files already formatted` ·
  `Found 4 errors.` (los 4 I001 de la fase I: `routers/audit.py`, `user_repository.py`, `schemas/audit.py`,
  `audit_service.py`) · `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 968 22 138 19 96.29%` (≥ 96.11 %, `plan.md:128`; sube desde 96.21 % de F) · `577 passed, 5 warnings` ·
  `Compuerta NO superada: ruff check`. Archivos de la fase: `ruff check` → `All checks passed!`; `ruff format --check`
  → `3 files already formatted`; `mypy` → `Success: no issues found in 3 source files`.
- Cambios exactos: `storage.py` sin `import os`; `__init__(self, connection_string: str, container_name: str,
  temporal_container_name: str) -> None` con docstring `Args`/`Raises`, guarda los tres valores y conserva el
  `ValueError` antes de `BlobServiceClient.from_connection_string` (mismo orden). El diff de `storage.py` es un único
  hunk en `__init__`: `upload_image`, `delete_image` y la promoción no cambian (E0: Azure solo cambia de dónde lee).
  `dependencies.py:58-75`: `get_storage_client(settings: Settings = Depends(get_settings))` con los tres argumentos
  nombrados del plan y docstring Google. `tests/test_storage.py`: fixture `doubles` sin `monkeypatch`, valores
  explícitos; `test_init_without_connection_string_raises` con `connection_string=""`; test nuevo
  `test_get_storage_client_builds_the_adapter_from_settings` con `patch.object(..., autospec=True)`,
  `assert_called_once_with("UseDevelopmentStorage=true")` y la tupla `("perm-c", "temp-c")`, como dicta el plan.
  Única instanciación de producción: `dependencies.py:71` (`git grep "AzureStorageClient("`).
- E1: `git grep -n -E "# (Repository|Service) injection" -- app/api/dependencies.py` → sin salida (exit 1). El diff
  borra exactamente 4 líneas del bloque de imports (dos comentarios y la línea en blanco que precede a cada uno); ningún
  import se mueve ni cambia. `# --- DEPENDENCY FACTORY (Inversion of Control) ---` intacto (`:21`). Fuera de E1 y de
  `get_storage_client`, `dependencies.py` no cambia: `get_current_user` (BE-42, `scope`) no aparece en el diff.
- Criterio de G: `git grep -n -E "getenv|setenv|delenv" -- app/core/storage.py tests/test_storage.py` → sin salida.
- M8 repetido en copia `git archive 714e05a` sin `.env` (scratchpad `tmp.VSzo3b1J3c`): `grep` muestra `:73` y `:74`
  con `azure_temporal_container_name`; `-k from_settings` → `AssertionError: assert ('temp-c', 'temp-c') == ('perm-c',
  'temp-c')`, `1 failed, 18 deselected`. Control (`tmp.UL2qe9K2Ut`) → `1 passed, 18 deselected`. Misma copia de
  control, `env -u` de las 5 obligatorias → `577 passed, 5 warnings`.
- Verificación final parcial: #1 → sin salida (valor final ya alcanzado); #3 → 1 línea (la de `test_config.py` llega
  en H); #5 → 2 líneas, `app/main.py:168` y `:187`; #9 → 3 líneas. `git ls-files --eol` de los 3 archivos →
  `i/lf w/lf`.
- AGENTS: la capa HTTP recibe la configuración por `Depends(get_settings)` (§3, decisión 2 del plan); el adaptador
  no lee entorno; import-linter 4 kept. El único doble nuevo usa `autospec=True` (§5); el test afirma sobre la
  llamada al mock con argumentos y sobre el estado del adaptador, sin texto en español. Sin excepciones de dominio
  nuevas. Los dobles globales de `tests/conftest.py:135` (`lambda: mock_client`) siguen valiendo: FastAPI resuelve el
  override sin la dependencia `settings`, y `test_fixtures_contract.py` y `test_services.py` pasan.
- Desviación declarada, texto del `ValueError` (`app/core/storage.py:61-63`): aceptable, no es hallazgo. El plan
  (`plan.md:502-503`) dicta "conserva el `ValueError` si la cadena está vacía", no su mensaje. El texto viejo
  ("… missing in environment variables") pasó a ser falso, porque el adaptador ya no lee el entorno. `git grep` del
  texto viejo y del nuevo: ningún test ni documento depende de él (solo el handoff lo cita), y
  `test_init_without_connection_string_raises` afirma solo el tipo. No llega al usuario final (AGENTS §4 c): no hay
  handler de `ValueError` en `app/main.py` (solo `RequestValidationError`, `IntegrityError` y `DomainError`), así que
  un fallo produciría el 500 genérico de Starlette sin el mensaje. Además, con `Settings` (`min_length=1`), la rama no
  se alcanza por `get_storage_client`. El texto nuevo no nombra variables en mayúsculas en `app/` ("Texto no
  dictado") y no altera los conteos de la Verificación final.

## Auditoría Fase H — 2026-11-10
**Veredicto Fase H: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia, medida por el auditor (no copiada del handoff):

- Árbol: `git status --short` vacío al empezar. HEAD `8a06b91` (progreso) sobre `c2ffea8` (fase) sobre `8d1afcb`.
- `progress.json` (`git diff 8d1afcb 8a06b91`): `Fase_H` pasa a `completed` con `c2ffea8` (`git show --stat` lo
  confirma); `current_target` `Fase_H` → `Fase_I`; `last_handoff` reescrito; `edit_rules` y `allowed_statuses` intactos;
  JSON válido.
- Commit `c2ffea8`: mensaje exacto del plan (`plan.md:550`), cuerpo con el porqué y `Co-Authored-By`. Archivos:
  `.azure-pipelines/ci-pipeline.yml`, `.env.example`, `tests/test_config.py` (40+/8-), los tres de `plan.md:526`.
  `git diff 8d1afcb HEAD --stat -- .azure-pipelines/cd-pipeline.yml` vacío (E0/P1).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1) = fila H (`plan.md:140`): `60 files already
  formatted` · ruff `Found 4 errors.` (los I001 de `audit.py`, `user_repository.py`, `schemas/audit.py`,
  `audit_service.py`, de la fase I) · `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` ·
  `579 passed, 5 warnings` · `TOTAL 968 22 138 19 96.29%` (≥ 96.11 %, `plan.md:128`; igual que G: la fase no toca
  `app/`) · `Compuerta NO superada: ruff check`. Archivo tocado: `ruff check`, `ruff format --check` y `mypy` de
  `tests/test_config.py` limpios.
- Cambios exactos, `.env.example`: `:20-22` → `HS256`, `30`, `15`; `:19` intacta. Bloque Email con las 5 claves y el
  comentario dictados, tras el bloque JWT. `AZURE_TEMPORAL_CONTAINER_NAME=temp-ecotur-images` en `:39`, justo tras
  `AZURE_CONTAINER_NAME` (`:38`) **dentro del bloque Azure** (`cat -A`): en el diff parece seguir a `MAIL_SERVER` solo
  porque el hunk muestra como contexto el encabezado Azure entre las dos zonas añadidas. Bloque Frontend antes de CORS.
  Sin secretos: solo placeholders (`cuenta_smtp@example.com`, `DIGITAR_CONTRASEÑA_DE_APLICACION`) y valores por defecto
  públicos; `JWT_SECRET_KEY` es la línea previa, que el tercer test de A ya fija como no aceptada.
- 15 campos: `dotenv_values(".env.example")` devuelve las 15 claves de `Settings` más las 5 `POSTGRES_*`. Carácter `Ñ`:
  `dotenv_values` lee en `utf-8` por defecto (firma: `encoding='utf-8'`) y `Settings` usa `env_file_encoding="utf-8"`;
  medido con locale `cp1252`, `utf8_mode 0`: `mail_password == "DIGITAR_CONTRASEÑA_DE_APLICACION"` → `True` en las
  dos lecturas. Precedente: `POSTGRES_PASSWORD=DIGITAR_CONTRASEÑA_PRIVADA` (`:5`) ya estaba en la línea base.
- CI (E0/P4): el bloque `env:` (5 líneas) desaparece entero; `yaml.safe_load` → 3 pasos (`task`, `script`, `script`),
  `variables` con `pythonVersion` y `group: VG-ECOTUR-DEV`, el último paso sin `env`. Comentario dictado
  (`plan.md:536`) en `:29`, sobre `- script:`. **El comentario es cierto:** en una copia `git archive HEAD` sin `.env`
  (scratchpad `auditH_head`), con `env -i` (solo `PATH`, `SYSTEMROOT`, `TEMP`, `TMP`, `USERPROFILE`), `pytest` →
  `579 passed`, y el comando literal del CI (`scripts/check.py --soft format,ruff,mypy`) → `Compuerta superada;
  tolerados en rojo: ruff check`, exit 0. Ningún paso de la compuerta necesita una variable del CI.
- Tests: los dos dictados, con el nombre, la firma y la aserción del plan (`plan.md:540-545`). RED repetido en copia
  `git archive 8d1afcb` + `tests/test_config.py` de `c2ffea8` (`auditH_red`): `int_parsing` ×2 + `missing` ×2 y 7
  claves sobrantes (`MAIL_*` ×5, `AZURE_TEMPORAL_CONTAINER_NAME`, `FRONTEND_URL`) → `2 failed`. No dependen de `.env`:
  el primero pasa `_env_file=ENV_EXAMPLE` y borra los 15 campos con `_clear` (`monkeypatch.delenv`, se restaura al
  salir); el segundo solo lee `.env.example`. `Settings(_env_file=…)` no escribe en `os.environ` y ninguno toca la
  caché de `get_settings`: sin fuga entre tests. Sin aserciones sobre texto en español.
- Criterios: `^\s+env:` en `ci-pipeline.yml` → 0; `tu_correo@gmail.com` → 0; Verificación final #1 → 0; #2 → 1
  (`conftest.py:28`); #3 → 2 (`tests/test_config.py:13`, `tests/test_token_failure_paths.py:16`); #8 `--soft` → 2.
  Suite exportada con `env -u` de las 5 obligatorias → `579 passed`. `git ls-files --eol` de los 3 archivos →
  `i/lf w/lf`.
- Desviaciones declaradas, aceptables (no son hallazgo): (a) los separadores `# ====` y la línea en blanco única siguen
  el estilo de todos los bloques del archivo; el plan dicta el texto del encabezado y no su marco, y no alteran claves
  ni conteos. (b) Que `ci-pipeline.yml` acabe en `\n` es consecuencia de borrar las últimas líneas (la base no tenía
  salto final) y es lo correcto en POSIX; YAML válido.
- MD de la fase (David, en el PR): el log del paso "Compuerta de calidad (scripts/check.py)" del CI sin `env:`.
  Pendiente; la medición local con `env -i` lo anticipa.
- AGENTS: sin código de `app/`, sin excepciones de dominio, sin dobles; tests en inglés con docstring.

## Auditoría Fase I — 2026-11-10
**Veredicto Fase I: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos en la fase ni en el cierre del ítem. Evidencia, medida por el auditor (no copiada del handoff):

- Árbol: `git status --short` vacío al empezar. HEAD `3298a91` (progreso) sobre `c122cb1` (fase) sobre `88425c4`.
- `progress.json` (`git show 3298a91`): `Fase_I` pasa a `completed` con `c122cb1`; `current_target` `Fase_I` → `null`
  (convención de cierre: los 13 `docs/deuda/*/progress.json` del repo lo tienen en `null`); `last_handoff` reescrito;
  `edit_rules` idéntico en las 10 versiones del archivo (`md5sum` único); JSON válido, 9 fases `completed`. Hashes de
  A–I (`21ee9fc`, `43d28f5`, `cbf439c`, `e4602cf`, `59d75b7`, `311b19e`, `714e05a`, `c2ffea8`, `c122cb1`) reales
  (`git log -1`) y cada asunto coincide letra por letra con el "Commit:" de su fase en `plan.md`.
- Commit `c122cb1`: mensaje exacto del plan (`plan.md:562`), cuerpo con el porqué y `Co-Authored-By`. Archivos: los 5
  de `plan.md:553-554` (10+/11-), ningún otro.
- Cambios exactos: `pyproject.toml` pierde solo las 3 líneas de comentario y `unfixable = ["I001"]`. Los 4 archivos de
  `app/` cambian solo líneas del bloque de imports. **Reproducido:** en una copia `git archive 88425c4`
  (scratchpad `audI_ruff`), borrar esas 4 líneas da un `pyproject.toml` idéntico al de `c122cb1`, y el comando literal
  del plan (`ruff check --select I001 --fix <4 archivos>`) → `Found 4 errors (4 fixed, 0 remaining).`, con los 4
  archivos idénticos (`diff`) a los de `c122cb1`. `from sqlalchemy.future import select` sigue en
  `app/repositories/user_repository.py:4` (S2). Archivos tocados: `ruff check` → `All checks passed!`; `mypy` →
  `Success: no issues found in 4 source files`.
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, sin `--soft`, exit 0) = fila I (`plan.md:141`):
  `60 files already formatted` · `All checks passed!` · `Success: no issues found in 55 source files` ·
  `Contracts: 4 kept, 0 broken.` · `579 passed, 5 warnings` · `TOTAL 968 22 138 19 96.29%` (≥ 96.11 %,
  `plan.md:128`; igual que H) · `Compuerta superada.` Coincide con el handoff.
- Verificación final (`plan.md:564-605`), sobre `3298a91` (= `c122cb1` en código):
  #1 → 0 · #2 → 1 (`conftest.py:28`) · #3 → 2 (`tests/test_config.py:13`, `tests/test_token_failure_paths.py:16`) ·
  #4 → 3 (`app/core/config.py:13,20,30`) · #5 → 2 (`app/main.py:168,187`) · #6 → 0 · #7 → 0 · #8 → `unfixable` 0,
  `env:` 0, `--soft` 2 (`ci-pipeline.yml:28,31`) · #9 → 3 (`tests/test_token_failure_paths.py:59,191,204`) ·
  #10 → `All checks passed!` y `Success: no issues found in 55 source files` · #11 → bloque anterior.
  En copias `git archive` sin `.env` (`test ! -e .env` en las dos; scratchpad `audI_head` = `HEAD`, `audI_base` =
  `55345a1`): #12 `env -u` de las 5 obligatorias → `579 passed, 5 warnings` · #13 `env -i` con las 5 → exit 0 en `HEAD`
  y en `55345a1` · #14 sin `JWT_SECRET_KEY` → `HEAD` exit 1, stderr `jwt_secret_key` 1, `Field required` 1,
  `a@test.com` 0 (`55345a1`: exit 0, como dice el plan) · #15 solo `DATABASE_URL` → exit 0 y 116 líneas en las dos,
  `cmp` idénticos; sin `DATABASE_URL` en `HEAD` → exit 1, `database_url` en stderr. Todo coincide con el handoff.
- Cierre del ítem: `git diff --stat 55345a1 HEAD` → 40 archivos. Código y configuración: exactamente los de la Regla de
  alcance (`plan.md:118-123`): `app/core/config.py`, `conftest.py`, `tests/test_config.py`, los 8 consumidores,
  `alembic/env.py`, los 7 tests existentes, `.env.example`, `ci-pipeline.yml` (solo el bloque `env:` y el comentario
  dictado), `pyproject.toml` (solo `unfixable`) y los 4 I001. El resto es documentación del flujo: ADR-0013
  (`db2be61`, con el plan), bitácora del 10 nov (`7f46c5e`, `e6feb08`), `docs/deuda/A4/*`. Sin diff desde `8cea834` en
  `cd-pipeline.yml`, `Dockerfile`, `docker-compose.yml`, `docs/CONTEXT.md`, `docs/PLAN.md`; `docs/backlog.md` solo
  cambia en `8cea834..55345a1` (verificación, antes de la base). `git grep -E "getenv|load_dotenv|os\.environ" -- app
  alembic` → 0. Fuera de `docs/`, ninguna mención de `unfixable`, `load_dotenv` ni `os.getenv`.
- Opcionales previos con destino: los dos de la fase D. El 1 lo resolvió E1 en la fase G
  (`git grep -n -E "# (Repository|Service) injection" -- app/api/dependencies.py` → 0); el 2 queda fuera de A4 como
  BE-42 por decisión de David (E1, `plan.md:652-653`). A–C y E–H, sin opcionales.
- AGENTS: la fase solo reordena imports; sin código nuevo, sin excepciones de dominio, sin tests nuevos.
- Pendiente humano antes del PR (no es hallazgo): (1) MD de H/P4: el log del paso "Compuerta de calidad
  (scripts/check.py)" del CI del PR, sin `env:`. (2) E0.8 y E1: las filas del backlog (residuales 1–4 y 6 del plan,
  longitud mínima de `jwt_secret_key`, BE-42) las escribe la sesión Mentor; hoy `git grep -n "BE-42" -- docs/backlog.md`
  no da nada. La fila A4 (`docs/backlog.md:98`) sigue en `Entra · B-PAGOS`. (3) La descripción del PR declara el límite
  de E0.7 (commits de E y F con `.env` local). (4) Residuales 5 y 7 → CI duro (`--soft` sale tras medir `develop`).

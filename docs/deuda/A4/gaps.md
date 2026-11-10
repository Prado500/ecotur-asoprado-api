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

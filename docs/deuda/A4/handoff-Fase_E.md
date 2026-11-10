# Handoff — A4 · Fase E (motor, migraciones y cliente SMTP desde `Settings`)

- Commit de la fase: `59d75b7` — `refactor(config): engine, migrations and SMTP client read Settings (A4)`
- Rama: `item/a4`, sobre `6104d15` (enmienda E1 commiteada por David).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.
- Enmiendas aplicables: E0 (P1 aceptada: motor y migraciones con `DatabaseSettings` vía `get_database_settings()`;
  P2: esta fase ordena los I001 de `database.py` y `email.py`). E1 no afecta a E.

## Ritual de arranque

- `git status --short`: limpio. HEAD `6104d15`. `current_target` = `Fase_E`. `gaps.md`: A, B, C, D en PASS, sin
  bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila D: `60 files already formatted` · ruff `Found 6 errors.` ·
  mypy `Found 1 error in 1 file (checked 55 source files)` (`app\db\database.py:11 … [arg-type]`) ·
  `Contracts: 4 kept, 0 broken.` · `574 passed, 5 warnings` · `TOTAL 975 23 138 19 96.23%` ·
  `Compuerta NO superada: ruff check, mypy`.

## Archivos tocados

`app/db/database.py`, `alembic/env.py`, `app/core/email.py`, `tests/test_email.py`. Ningún otro.

`git show --stat 59d75b7`:

```
 alembic/env.py      | 11 +++--------
 app/core/email.py   | 46 +++++++++++++++++++++++++++++-----------------
 app/db/database.py  | 10 +++-------
 tests/test_email.py | 15 +++++++++++++++
 4 files changed, 50 insertions(+), 32 deletions(-)
```

Resumen del diff:

- `app/db/database.py`: fuera `import os`, `from dotenv import load_dotenv`, `load_dotenv()` y `DATABASE_URL`;
  `from app.core.config import get_database_settings`; `create_async_engine(get_database_settings().database_url,
  echo=True)` con el comentario de `echo=True` intacto (A5). I001 aplicado con
  `ruff check --select I001 --fixable I001 --fix`.
- `alembic/env.py`: fuera `import os`, `dotenv`, `load_dotenv()`, `database_url` y el `raise ValueError`;
  `from app.core.config import get_database_settings`; tras `config = context.config`, el comentario dictado
  `# Same source as the app (ADR-0013): validated settings; only the database URL is required.` y
  `config.set_main_option("sqlalchemy.url", get_database_settings().database_url)`.
- `app/core/email.py`: fuera `import os`, `dotenv`, `load_dotenv()` y `conf`. Imports
  `from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType`, `from pydantic import EmailStr`,
  `from app.core.config import Settings, get_settings`. Función `_smtp_config(settings: Settings) -> ConnectionConfig`
  (docstring Google con `Args`/`Returns`) con los mismos argumentos que `conf`, salvo `MAIL_USERNAME=settings.mail_username`,
  `MAIL_PASSWORD=settings.mail_password`, `MAIL_FROM=settings.mail_sender`, `MAIL_PORT=settings.mail_port`,
  `MAIL_SERVER=settings.mail_server`; `fast_mail = FastMail(_smtp_config(get_settings()))`. I001 aplicado (mismo
  comando). La plantilla HTML y `send_verification_email` sin cambios.
- `tests/test_email.py`: import `from app.core.config import get_settings`; test nuevo
  `test_smtp_client_is_configured_from_settings` (tupla de 5 campos de `email_module.fast_mail.config` frente a
  `mail_username`, `mail_password`, `mail_sender`, `mail_port`, `mail_server`).

## Tests (RED primero)

- Test nuevo, de caracterización (el plan lo declara así: pasa antes y después). Escrito antes de tocar `app/`:
  `tests/test_email.py` → `7 passed in 0.24s`. Su RED es el mutante M6 (abajo).
- RED de herramienta, antes del cambio (literal):
  ```
  app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
  Found 1 error in 1 file (checked 1 source file)
  ```
  y `git grep -n -E "getenv|load_dotenv" -- app/db alembic app/core/email.py` → 13 líneas
  (`alembic/env.py:5,14,20`, `app/core/email.py:4,6,12-16`, `app/db/database.py:2,6,7`).
- Después: el mismo `git grep` → 0 líneas (exit 1); mypy de los 4 archivos tocados →
  `Success: no issues found in 4 source files`; `ruff check` de los 4 → `All checks passed!`; `ruff format` →
  `4 files left unchanged`.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

```
60 files already formatted
...
Found 4 errors.
--- ruff check: FALLA (exit 1) en 0.1s

=== mypy ===
Success: no issues found in 55 source files
--- mypy: OK en 0.9s
...
Contracts: 4 kept, 0 broken.
...
TOTAL                                        971     23    138     19  96.21%

25 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 96.21%
575 passed, 5 warnings in 19.26s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check
```

Los 4 I001 restantes son los que el plan deja para la fase I: `app\api\routers\audit.py:1:1`,
`app\repositories\user_repository.py:1:1`, `app\schemas\audit.py:1:1`, `app\services\audit_service.py:1:1`.

| | ruff check | mypy | pytest | cobertura | format | contratos |
|---|---|---|---|---|---|---|
| Esperado (fila E) | 4 | `Success: no issues found in 55 source files` | 575 | ≥ 96.11 % (base, plan) | 60 | 4 kept |
| Real | 4 | `Success: no issues found in 55 source files` | 575 passed | 96.21 % | 60 | 4 kept |

**Cobertura 96.21 % < 96.23 % de la fase D (desviación declarada, no del plan).** El plan fija `cobertura ≥ 96.11 %`
en todas las filas y la línea base de `verificacion.md` es 96.11 %; se cumple. La bajada frente a D es aritmética:
`Stmts` 975 → 971 (se borran sentencias cubiertas: `import os`, `dotenv`, `load_dotenv()`, `DATABASE_URL`, `conf`) y
`Miss` sigue en 23, `Branch` 138, `BrPart` 19. Ninguna línea nueva queda sin cubrir: en `app\db\database.py` los 4
`Miss` son el cuerpo de `get_db` (`35-39` antes, `31-35` ahora), que la suite sustituye por su override (ADR-0011).
Subirla exigiría tests de `get_db`, fuera del alcance de la fase.

## Mutante M6 (copia `git archive HEAD` de `59d75b7` en el scratchpad, sin `.env`)

```
$ sed -i 's/MAIL_FROM=settings.mail_sender/MAIL_FROM=settings.mail_username/' app/core/email.py
$ grep -n "MAIL_FROM=" app/core/email.py
25:        MAIL_FROM=settings.mail_username,
$ python -m pytest -q -p no:cacheprovider tests/test_email.py -k configured_from_settings
E         At index 2 diff: 'smtp-account@test.com' != 'sender@test.com'
FAILED tests/test_email.py::test_smtp_client_is_configured_from_settings - As...
1 failed, 6 deselected in 0.27s
```

Esperado: `1 failed`. Coincide. Control sin mutante en otra copia de `HEAD`: `1 passed, 6 deselected in 0.04s`.

## Migraciones como el CD (criterio de aceptación de E)

Exportaciones `git archive` de `55345a1` y de `HEAD` (`59d75b7`) en el scratchpad, ambas sin `.env`
(`test ! -e .env`), comando del plan con `env -u JWT_SECRET_KEY -u MAIL_USERNAME -u MAIL_PASSWORD
-u AZURE_STORAGE_CONNECTION_STRING DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db" … -m alembic upgrade head --sql > out.sql`:

```
alembic_base_e: exit=0 lines=116
alembic_head_e: exit=0 lines=116
cmp: identical
```

Sin `DATABASE_URL` en `HEAD` (`env -u DATABASE_URL -u …`): `exit=1`; la salida de error contiene `database_url`
(2 apariciones):

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for DatabaseSettings
database_url
  Field required [type=missing]
```

Nada se ejecutó contra una base real ni en el árbol de trabajo. `cd-pipeline.yml` no se tocó.

## Comprobaciones de la Verificación final que esta fase mueve

- `git grep -n -E "load_dotenv|from dotenv" -- app alembic tests` → 1 línea (`tests/test_token_failure_paths.py:16`,
  `dotenv_values`); la segunda llega con la fase H.
- `git grep -n "tu_correo@gmail.com" -- app` → 0.
- Constantes (#5) en `app`/`alembic`: quedan las 4 líneas de `app/main.py` (`:170`, `:189`, `:196`, `:200`); `:196` y
  `:200` las retira la fase F. `DATABASE_URL` ya no aparece.

## Residuales y dudas

- Desviación: cobertura 96.21 % frente al 96.23 % de D (arriba). Cumple el criterio del plan.
- Límite aceptado en E0.7 (no es hallazgo): en este commit, la app arrancada en local desde `.env` ya no carga
  `.env` en el entorno del proceso, así que `CORS_ORIGINS`, `FRONTEND_URL` y `AZURE_*` toman sus valores por defecto o
  fallan hasta F y G.
- Incidencia de herramienta, sin efecto en el commit: la primera escritura por script en Windows dejó CRLF en
  tres archivos; se normalizaron a LF antes de `git add` (los originales eran LF; `grep -c $'\r'` → 0).

# Handoff — A4 · Fase I (fuera `unfixable`; I001 en los 4 archivos restantes)

- Commit de la fase: `c122cb1` — `style(imports): drop unfixable I001 and sort the last four blocks (A4)`
- Rama: `item/a4`, sobre `88425c4` (auditoría de H en PASS). Última fase del plan.
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.
- Enmiendas aplicables: E0/P2 (I001 repartido: D y E ya ordenaron `dependencies.py`, `user_service.py`, `database.py`
  y `email.py`; I quita `unfixable` y ordena los 4 bloques restantes).

## Ritual de arranque

- `git status --short`: limpio. HEAD `88425c4`. `current_target` = `Fase_I`. `gaps.md`: A–H en PASS, sin bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila H: `60 files already formatted` · ruff `Found 4 errors.` (I001
  en `app\api\routers\audit.py`, `app\repositories\user_repository.py`, `app\schemas\audit.py`,
  `app\services\audit_service.py`) · mypy `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` ·
  `579 passed, 5 warnings in 14.20s` · `TOTAL 968 22 138 19 96.29%` · `Compuerta NO superada: ruff check`.

## Archivos tocados

`pyproject.toml`, `app/api/routers/audit.py`, `app/repositories/user_repository.py`, `app/schemas/audit.py`,
`app/services/audit_service.py`. Ningún otro. `.env` no se leyó en ningún momento.

`git show --stat c122cb1`:

```
 app/api/routers/audit.py            | 4 ++--
 app/repositories/user_repository.py | 3 ++-
 app/schemas/audit.py                | 6 ++++--
 app/services/audit_service.py       | 4 ++--
 pyproject.toml                      | 4 ----
 5 files changed, 10 insertions(+), 11 deletions(-)
```

Resumen del diff:

- `pyproject.toml`: borradas `:69-72` (3 líneas de comentario sobre el orden de carga y `unfixable = ["I001"]`). Nada más.
- Los 4 archivos de `app/`: solo lo que hace `ruff check --select I001 --fix` (comando literal del plan, ya sin
  `--fixable` porque `unfixable` ha desaparecido): reordenar nombres y líneas de import y separar grupos
  stdlib / terceros / `app.*` con línea en blanco. Ninguna línea fuera del bloque de imports. En
  `user_repository.py` solo cambia `datetime, UTC` → `UTC, datetime` y una línea en blanco; `from sqlalchemy.future
  import select` sigue (S2, fuera de alcance).
- Finales de línea: `git ls-files --eol` de los 5 archivos → `i/lf w/lf attr/text=auto eol=lf`.

## Tests (RED primero)

RED de herramienta, antes del cambio
(`ruff check --select I001 --fixable I001 --diff <4 archivos>`, exit 1): `Would fix 4 errors.` con el mismo diff que
luego aplicó el `--fix`. Después: `ruff check --select I001 --fix <4 archivos>` → `Found 4 errors (4 fixed, 0 remaining).`
Sobre los archivos tocados: `ruff check` → `All checks passed!`; `mypy <4 archivos>` →
`Success: no issues found in 4 source files`.

La prueba de que el orden de imports ya no decide nada (adenda 12, E0/P2) es la suite: `579 passed` antes (fila H) y
después (fila I), también en la copia exportada sin `.env` (punto 12). Ningún test nuevo ni tocado (el plan no dicta
ninguno); checklist `test-sanitizer` sin aplicación.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
60 files already formatted
All checks passed!
Success: no issues found in 55 source files
Contracts: 4 kept, 0 broken.
TOTAL                                        968     22    138     19  96.29%
579 passed, 5 warnings in 14.16s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

| | ruff check | mypy | pytest | cobertura | format | contratos | Resumen |
|---|---|---|---|---|---|---|---|
| Esperado (fila I) | 0 (`All checks passed!`) | `Success: no issues found in 55 source files` | 579 | ≥ 96.11 % | 60 | 4 kept | `Compuerta superada.` |
| Real | `All checks passed!` | `Success: no issues found in 55 source files` | 579 passed | 96.29 % | 60 | 4 kept | `Compuerta superada.` (exit 0) |

Sin `--soft`. Cobertura sin cambios (`TOTAL 968 22`): la fase solo reordena imports.

## Verificación final (plan, sobre `c122cb1`)

Salida literal; `(exit 1)` de `git grep` = 0 líneas.

```
### 1
(exit 1)
### 2
conftest.py:28:os.environ.update(TEST_ENVIRONMENT)
### 3
tests/test_config.py:13:from dotenv import dotenv_values
tests/test_token_failure_paths.py:16:from dotenv import dotenv_values
### 4
app/core/config.py:13:from pydantic_settings import BaseSettings, SettingsConfigDict
app/core/config.py:20:class DatabaseSettings(BaseSettings):
app/core/config.py:30:    model_config = SettingsConfigDict(
### 5
app/main.py:168:    """Parse the comma-separated ``CORS_ORIGINS`` value into an explicit allow-list.
app/main.py:187:        raise ValueError("CORS_ORIGINS must list explicit origins; wildcards are not allowed")
### 6
(exit 1)
### 7
(exit 1)
### 8 unfixable
(exit 1)
### 8 env del CI
(exit 1)
### 8 --soft
.azure-pipelines/ci-pipeline.yml:28:  # --soft: ruff/mypy do not block until the global gate is green (B-TESTS m4, ADR-0005). Remove it then.
.azure-pipelines/ci-pipeline.yml:31:      python scripts/check.py --soft format,ruff,mypy
### 9
tests/test_token_failure_paths.py:59:    claims = jwt.decode(token, options={"verify_signature": False})
tests/test_token_failure_paths.py:191:async def test_access_token_signed_with_another_key_returns_401(
tests/test_token_failure_paths.py:204:async def test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive(
### 10
All checks passed!
Success: no issues found in 55 source files
```

| # | Esperado | Real |
|---|---|---|
| 1 | 0 líneas | 0 |
| 2 | 1 línea, `conftest.py:…:os.environ.update(TEST_ENVIRONMENT)` | 1 (`conftest.py:28`) |
| 3 | 2 líneas `from dotenv import dotenv_values` | 2 (`test_config.py:13`, `test_token_failure_paths.py:16`) |
| 4 | 3 líneas en `app/core/config.py` | 3 (`:13`, `:20`, `:30`) |
| 5 | 2 líneas en `app/main.py` (docstring y `ValueError` de `parse_cors_origins`) | 2 (`:168`, `:187`) |
| 6 | 0 | 0 |
| 7 | 0 | 0 |
| 8 | unfixable 0 · env 0 · `--soft` 2 | 0 · 0 · 2 |
| 9 | 3 líneas en `test_token_failure_paths.py` | 3 (`:59`, `:191`, `:204`) |
| 10 | `All checks passed!` · `Success: no issues found in 55 source files` | igual |
| 11 | exit 0, `Compuerta superada.`, 60 formatted, 4 kept, 579 passed, ≥ 96.11 % | igual (bloque de arriba; 96.29 %) |
| 12 | 579 passed | `579 passed, 5 warnings in 14.36s` |
| 13 | exit 0 (también sobre `55345a1`) | exit 0 · `55345a1`: exit 0 |
| 14 | exit 1; stderr con `jwt_secret_key` y `Field required`, sin `a@test.com` | exit 1; 1 · 1 · 0 (`55345a1`: exit 0, como dice el plan) |
| 15 | exit 0 y salida idéntica a `55345a1` | exit 0 en las dos, 116 líneas, `cmp` idénticos |

Puntos 12–15, en copias `git archive` (`test ! -e .env` correcto en las dos):
HEAD en
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\d5752b8a-a1fb-4650-a57d-6b3899de76c6\scratchpad\finalI.Ztcx`,
`55345a1` en
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\d5752b8a-a1fb-4650-a57d-6b3899de76c6\scratchpad\base55.qFuz`.

```
### 12   (env -u de las 5 obligatorias; pytest -q -p no:cacheprovider)
579 passed, 5 warnings in 14.36s
### 13   (env -i con las 5 obligatorias; python -c "import app.main")
(exit 0)
### 14   (env -i sin JWT_SECRET_KEY)
(exit 1)
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
jwt_secret_key
  Field required [type=missing]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
jwt_secret_key: 1  Field required: 1  a@test.com: 0
### 15   (env -u de las 4 no-BD; DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db; alembic upgrade head --sql)
base55.qFuz: exit 0 lines 116
finalI.Ztcx: exit 0 lines 116
cmp: idénticos
### 15b  (HEAD sin DATABASE_URL, criterio de E)
(exit 1)
database_url en stderr: 2
```

## Residuales y dudas

- Ninguna desviación del plan. `current_target` queda en `null` (convención de los demás `progress.json` del repo al
  cerrar un ítem).
- **MD de H pendiente (David, en el PR):** el paso "Compuerta de calidad (scripts/check.py)" del CI pasa sin el bloque
  `env:`. Con la compuerta local ya en verde completo, el `--soft` del CI (`ci-pipeline.yml:28,31`) ya no oculta nada;
  quitarlo sigue fuera de alcance (CI duro, CONTEXT §8.2).
- Residuales 1–7 del plan sin cambios; sus filas en `docs/backlog.md` las escribe la sesión Mentor (E0.8).

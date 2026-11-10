# Handoff — A4 · Fase F (CORS y URL del frontend desde `Settings`)

- Commit de la fase: `311b19e` — `refactor(api): CORS origins and frontend URL come from Settings (A4)`
- Rama: `item/a4`, sobre `feabea0` (auditoría de E en PASS).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.
- Enmiendas aplicables: E0 (el límite E0.7 de arranque local entre E y G está aceptado, no es hallazgo). E1 solo
  afecta a G.

## Ritual de arranque

- `git status --short`: limpio. HEAD `feabea0`. `current_target` = `Fase_F`. `gaps.md`: A–E en PASS, sin bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila E: `60 files already formatted` · ruff `Found 4 errors.` ·
  mypy `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` · `575 passed, 5 warnings` ·
  `TOTAL 971 23 138 19 96.21%` · `Compuerta NO superada: ruff check`.

## Archivos tocados

`app/main.py`, `app/api/routers/user.py`, `tests/test_main.py`, `tests/test_auth.py`. Ningún otro.

`git show --stat 311b19e`:

```
 app/api/routers/user.py |  6 ++++--
 app/main.py             | 12 +++---------
 tests/test_auth.py      | 17 +++++++++++++++++
 tests/test_main.py      | 29 +++++++++++++++++++++--------
 4 files changed, 45 insertions(+), 19 deletions(-)
```

Resumen del diff:

- `app/main.py`: fuera `import os`, `DEFAULT_CORS_ORIGINS`, el comentario de `:193-195` y `CORS_ORIGINS`;
  `from app.core.config import get_settings`. Sobre `app.add_middleware`, el comentario dictado
  `# Allowed origins come from Settings.cors_origins (ADR-0013); wildcards are rejected at startup.`;
  `allow_origins=parse_cors_origins(get_settings().cors_origins),`. `parse_cors_origins`, `allow_credentials`,
  `allow_methods` y `allow_headers` sin cambios (SEC1).
- `app/api/routers/user.py`: fuera `import os`; `from app.core.config import Settings, get_settings`.
  `registrar_turista` gana `settings: Settings = Depends(get_settings)` como último parámetro, con su línea `Args`
  (`settings (Settings): Injected configuration; frontend_url is the base of the emailed link.`);
  `frontend_url = settings.frontend_url.rstrip("/")`. Ruta, `response_model` y textos sin cambios.
- `tests/test_main.py`: imports `from fastapi.middleware.cors import CORSMiddleware`,
  `from app.core.config import Settings, get_settings`, `from app.main import app, parse_cors_origins`. Helper
  `_allowed_origins() -> list[str]`: desempaqueta el único `Middleware` de `app.user_middleware` con
  `cls is CORSMiddleware` y devuelve `kwargs["allow_origins"]`. `test_default_cors_origins_is_local_frontend` usa
  `parse_cors_origins(Settings.model_fields["cors_origins"].default)`; los demás usos de `CORS_ORIGINS` pasan a
  `_allowed_origins()`; `test_configured_cors_origins_have_no_wildcard` añade
  `_allowed_origins() == parse_cors_origins(get_settings().cors_origins)`.
- `tests/test_auth.py`: `from app.main import app`; test nuevo
  `test_register_builds_the_verification_link_from_frontend_url(client, mock_send_email)`.

## Tests (RED primero)

Test nuevo escrito antes de tocar `app/`. RED literal (`tests/test_auth.py -k frontend_url`):

```
E           Expected: send_verification_email(email_to='turista@example.com', first_name='Juan', token=<ANY>, base_url='https://front.example')
E             Actual: send_verification_email(email_to='turista@example.com', first_name='Juan', token='eyJ…', base_url='http://localhost:3000')
FAILED tests/test_auth.py::test_register_builds_the_verification_link_from_frontend_url
1 failed, 19 deselected in 0.40s
```

Tras el cambio: `tests/test_main.py tests/test_auth.py` → `37 passed`; `mypy` de los 4 archivos →
`Success: no issues found in 4 source files`; `ruff check` → `All checks passed!`; `ruff format --check` →
`4 files already formatted`.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

```
60 files already formatted
...
Found 4 errors.
...
Success: no issues found in 55 source files
...
Contracts: 4 kept, 0 broken.
...
TOTAL                                        969     23    138     19  96.21%
576 passed, 5 warnings in 14.35s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check
```

Los 4 I001 son los de la fase I: `app\api\routers\audit.py:1:1`, `app\repositories\user_repository.py:1:1`,
`app\schemas\audit.py:1:1`, `app\services\audit_service.py:1:1`.

| | ruff check | mypy | pytest | cobertura | format | contratos |
|---|---|---|---|---|---|---|
| Esperado (fila F) | 4 | `Success: no issues found in 55 source files` | 576 | ≥ 96.11 % | 60 | 4 kept |
| Real | 4 | `Success: no issues found in 55 source files` | 576 passed | 96.21 % | 60 | 4 kept |

Cobertura igual a E (96.21 %). `app\main.py`: `59 6 18 5 85.71%` → `57 6 18 5 85.33%`; los 6 `Miss` son los mismos
(ramas de handlers de excepciones, `61, 72, 76, 79, 82, 106`, antes `62, 73, …, 107`, desplazadas una línea); el
porcentaje del archivo baja solo porque se borraron 2 sentencias cubiertas.

## Mutante M7 (copia `git archive HEAD` de `311b19e` en el scratchpad, sin `.env`)

```
$ sed -i 's/settings.frontend_url.rstrip("\/")/settings.frontend_url/' app/api/routers/user.py
$ grep -n "frontend_url = " app/api/routers/user.py
68:    frontend_url = settings.frontend_url
$ python -m pytest -q -p no:cacheprovider tests/test_auth.py -k frontend_url
E             Actual: send_verification_email(email_to='turista@example.com', first_name='Juan', token=<jwt>, base_url='https://front.example/')
FAILED tests/test_auth.py::test_register_builds_the_verification_link_from_frontend_url
1 failed, 19 deselected in 0.50s
```

Esperado: `1 failed`. Coincide. Control sin mutante en otra copia de `HEAD`: `1 passed, 19 deselected in 0.23s`.

## Criterios de aceptación y Verificación final

- `git grep -n "DEFAULT_CORS_ORIGINS" -- app tests` → 0 líneas (exit 1).
- #5 → 2 líneas, ya su valor final: `app/main.py:168` (docstring de `parse_cors_origins`) y `app/main.py:187` (su
  `ValueError`).
- #6 → 0 líneas.
- #1 → quedan 3 líneas, todas en `app/core/storage.py:42-44` (fase G).
- `app/services` no importa `fastapi` ni `starlette`; import-linter 4 kept.
- Suite exportada (`git archive HEAD`, sin `.env`, `env -u` de las 5 obligatorias) → `576 passed, 5 warnings`.
- `git ls-files --eol` de los 4 archivos → `i/lf w/lf attr/text=auto eol=lf`.

## Residuales y dudas

- Desviación menor, de tipado: el helper `_allowed_origins()` incluye `assert isinstance(origins, list)` antes del
  `return`. mypy tipa `Middleware.kwargs` con valores `object` (`tests\test_main.py:18: error: Incompatible return value
  type (got "object", expected "list[str]")`); la aserción estrecha el tipo sin `cast` ni `type: ignore` y no cambia
  lo que prueba el test.
- Queda en `app/main.py:164` la cabecera `# === CORS ===` seguida de las dos líneas en blanco que antes separaban
  `DEFAULT_CORS_ORIGINS` de `parse_cors_origins`; `ruff format` la acepta. No se tocó para no salir de lo dictado.
- El override de `get_settings` del test nuevo lo limpia el `app.dependency_overrides.clear()` del fixture `client`.
- Límite E0.7 (aceptado, no es hallazgo): hasta G, el adaptador de Azure sigue leyendo `os.getenv`.

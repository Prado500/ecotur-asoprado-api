# Handoff — A4 · Fase B (módulo de configuración y entorno de la suite)

- Commit de la fase: `43d28f5` — `feat(config): add validated Settings and a .env-free test env (A4)`
- Rama: `item/a4`, sobre `7f46c5e` (bitácora tras la auditoría PASS de la fase A).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_B`. `gaps.md`: Fase A PASS, sin hallazgos para B.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila A: `57 files already formatted` · ruff `Found 8 errors.` ·
  mypy `Found 9 errors in 5 files (checked 53 source files)` · `Contracts: 4 kept, 0 broken.` ·
  `552 passed, 5 warnings` · `TOTAL … 96.11%`.

## Archivos tocados

- `app/core/config.py` (nuevo), `conftest.py` (nuevo, raíz), `tests/test_config.py` (nuevo). Ningún otro.

`git show --stat 43d28f5`:

```
 app/core/config.py   |  99 ++++++++++++++++++++++++++
 conftest.py          |  28 ++++++++
 tests/test_config.py | 198 +++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 325 insertions(+)
```

Resumen del diff:

- `app/core/config.py`: el código del plan, literal (imports, `ENV_FILE`, `DatabaseSettings` con `extra="ignore"` y
  `hide_input_in_errors=True`, `Settings` con los 15 campos, `mail_sender`, `get_settings` y `get_database_settings`
  con `@lru_cache`). **Única diferencia:** dos docstrings dictados superaban las 100 columnas (E501: líneas 3 y 4 del
  docstring del módulo, 102 y 105 columnas; la línea `Kept apart…` de `DatabaseSettings`, 101). Se re-envolvieron con
  las mismas palabras; ningún término cambia. En el plan el bloque va sangrado 2 espacios, lo que ocultaba el desborde.
- `conftest.py` (raíz): literal del plan (15 variables, `os.environ.update(TEST_ENVIRONMENT)`).
- `tests/test_config.py`: 21 casos con los nombres y aserciones del plan. Constantes `REQUIRED`, `OPTIONAL_DEFAULTS`
  (10 opcionales, `mail_from: None`), `ALL_FIELDS` y `VALID_REQUIRED`; helpers `_set_required` y `_clear`, que solo
  usan `monkeypatch.setenv`/`delenv` con `name.upper()`. Todos construyen `Settings(_env_file=None)` salvo los casos 6
  y 7 (archivo propio en `tmp_path`) y 9 y 11 (getters). Añadido sobre el plan, sin cambiar lo dictado: el caso 8
  además comprueba que el `ValidationError` de `Settings` nombra exactamente los cuatro campos obligatorios que faltan
  (aserción más estricta, AGENTS §5).

## Tests (RED primero)

RED antes del módulo, literal:

```
tests\test_config.py:16: in <module>
    from app.core.config import (
E   ModuleNotFoundError: No module named 'app.core.config'
ERROR tests/test_config.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.22s
```

GREEN en el árbol: `21 passed in 0.35s`.

## Mutantes (copia `git archive HEAD` de `43d28f5` en el scratchpad, una por mutante, sin `.env`)

Salida literal:

```
== Sin mutante
no .env
2 passed, 19 deselected in 0.07s
== M9
33:        extra="ignore",
1 failed, 20 deselected in 0.26s
== M10
33:        extra="forbid",
1 failed, 20 deselected in 0.28s
```

(El `grep -n -E "hide_input|extra="` de M9 muestra que la línea `hide_input_in_errors=True,` desapareció.)
Esperado por el plan: M9 `-k echo_values` → `1 failed`; M10 `-k unknown_keys` → `1 failed`. Coincide.

## Suite sin `.env` (criterio de aceptación)

`X=$(mktemp -d …) && git archive HEAD | tar -x -C "$X" && test ! -e "$X/.env" && cd "$X" && env -u DATABASE_URL -u
JWT_SECRET_KEY -u MAIL_USERNAME -u MAIL_PASSWORD -u AZURE_STORAGE_CONNECTION_STRING …/venv/Scripts/python.exe -m pytest
-q -p no:cacheprovider` (copia en el scratchpad en vez de `/tmp`):

```
no .env in /c/Users/dalde/AppData/Local/Temp/claude/…/scratchpad/tmp.M7vR8U3Azq
573 passed, 5 warnings in 19.41s
```

Esperado: `573 passed`. Coincide.

**Comprobación de David, pendiente** (el agente no la corre):
`./venv/Scripts/python.exe -c "from app.core.config import get_settings; get_settings(); print('ok')"` → `ok`.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Bloque RESUMEN literal:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Conteos literales:

```
60 files already formatted
Found 8 errors.
Found 9 errors in 5 files (checked 55 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        975     23    138     19  96.23%
Required test coverage of 92.0% reached. Total coverage: 96.23%
573 passed, 5 warnings in 19.72s
```

Fila B de la tabla del plan: ruff 8 · mypy `Found 9 errors in 5 files (checked 55 source files)` · 573 passed ·
format 60 · mismo resumen. **Exacta.** Cobertura 96.23 % ≥ 96.11 %.

Los 8 errores de ruff son los mismos I001 heredados que antes de la fase (`diff` de las ubicaciones antes/después sin
diferencias): `dependencies.py`, `routers/audit.py`, `email.py`, `database.py`, `user_repository.py`,
`schemas/audit.py`, `audit_service.py`, `user_service.py`. Los 9 de mypy son los `[arg-type]` heredados.

Archivos tocados: `ruff check tests/test_config.py app/core/config.py conftest.py` → `All checks passed!`;
`ruff format --check` → `3 files already formatted`; `mypy app/core/config.py tests/test_config.py` →
`Success: no issues found in 2 source files` (`conftest.py` de la raíz no está en `mypy.files`: residual 7 del plan).

Greps de la Verificación final, estado tras B: #4 → 3 líneas, todas en `app/core/config.py` (`:13`, `:20`, `:30`);
#9 → las mismas 3 líneas de la fase A (`tests/test_config.py` no añade ninguna); `tests/test_config.py` no lee ni
escribe `os.environ`.

## test-sanitizer (checklist)

Sin mocks; no se construyen usuarios ni tokens; nombres e identificadores en inglés; aserciones sobre tipos de error
de pydantic (`type`, `loc`), valores y identidad de objetos; ninguna sobre texto en español. Sin cambios a pruebas
existentes.

## Residuales y dudas

- Desviación menor declarada arriba: re-envoltura de dos docstrings dictados por E501. Sin cambio de texto.
- El hook de ruff, tras escribir `tests/test_config.py` antes de existir el módulo, marcó I001 porque clasificaba
  `app.core.config` como tercero; desapareció al crear el módulo. En una primera versión el test importaba
  `BaseSettings` para anotar el parámetro del caso 9: rompía el conteo #4 de la Verificación final (pydantic-settings
  solo en `config.py`), así que la anotación pasó a `Callable[[], DatabaseSettings]` y el hook quitó el import.
- Ninguno nuevo para el backlog.

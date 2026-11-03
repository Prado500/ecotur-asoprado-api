# Handoff S1 Fase C

Commit: `8ba10c0 refactor(alembic): import the whole app.models registry in env.py`
Base develop re-comprobada: `git fetch origin` correcto; `origin/develop` = merge-base(HEAD, origin/develop) = `b421268`
(= `Base develop` de `verificacion.md`). Arranque con árbol limpio en `07804ff`; gaps de A y B sin [BLOQUEANTE].

## Archivos tocados
- `alembic/env.py` (solo la cabecera, l.1-18), `app/models/__init__.py`, `tests/test_models_registry.py` (nuevo). Nada más.

## Diff (`git show --stat HEAD` del commit de la fase)
```
 alembic/env.py                | 14 +++++--------
 app/models/__init__.py        | 12 +++++++++--
 tests/test_models_registry.py | 48 +++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 63 insertions(+), 11 deletions(-)
```

## RED -> GREEN (`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_models_registry.py`)
- Antes de tocar `__init__.py`:
  ```
  E       AttributeError: module 'app.models' has no attribute '__all__'. Did you mean: '__file__'?
  tests\test_models_registry.py:38: AttributeError
  E       AttributeError: module 'app.models' has no attribute '__all__'. Did you mean: '__file__'?
  tests\test_models_registry.py:38: AttributeError
  2 failed in 0.18s
  ```
- Después: `tests/test_models_registry.py tests/test_models_schema.py` -> `9 passed in 0.10s`.

## Mutaciones (última línea de pytest sobre `tests/test_models_registry.py`)
- MC1 `__init__.py` sin `"AuditLog", ` en `__all__`: `2 failed in 0.16s`
- MC2 `app/models/zz_probe.py` con `Probe(Base)` creado por Bash (heredoc) y borrado con `rm` (también su `.pyc`):
  `2 failed in 0.16s`
- Tras restaurar: `2 passed in 0.03s`; `git status --short` solo mostraba los 3 archivos de la fase.

## Smoke offline de `env.py` (sin BD)
`DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" ./venv/Scripts/python.exe -m alembic upgrade head --sql`
antes y después: `exit 0` las dos veces (116 líneas); `diff s1_offline_antes.sql s1_offline_despues.sql` -> vacío
(`diff exit 0`). Los `.sql` se escribieron en el scratchpad de la sesión en lugar de `/tmp` (regla del entorno).

## Criterios del plan
- `grep -cE "^import app\.models\b" alembic/env.py` -> `1`
- `grep -nE "from app\.models\.\w+ import" alembic/env.py` -> vacío
- `grep -rn "B-S1 replaces it" alembic app` -> vacío
- `./venv/Scripts/python.exe -m ruff check alembic/env.py app/models/__init__.py tests/test_models_registry.py` ->
  `All checks passed!` (antes, `ruff format` y `ruff check --fix` del venv: `3 files left unchanged`)
- `./venv/Scripts/python.exe -m mypy app/models alembic/env.py tests/test_models_registry.py 2>&1 | grep -E
  '^(app[/\\]models|alembic|tests)[/\\]'` -> vacío (la única línea es `app\db\database.py:11`, A4)
- `git diff b421268 --stat -- alembic/versions/ app/db/ app/services/ app/repositories/ app/api/ app/schemas/
  tests/conftest.py scripts/` -> vacío

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`)
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
| Métrica | Arranque (HEAD `07804ff`) | Después (`8ba10c0`) | Plan | Línea base verificación |
|---|---|---|---|---|
| pytest | `367 passed, 5 warnings in 19.11s` | `369 passed, 5 warnings in 18.97s` | 369 | 360 |
| cobertura | `TOTAL 941 34 136 22 94.80%` | `TOTAL 942 34 136 22 94.81%` | ≥ 94.77 % | 94.77 % |
| ruff check | `Found 76 errors.` | `Found 60 errors.` | 60 | 82 |
| mypy | `Found 10 errors in 5 files (checked 35 source files)` | `Found 10 errors in 5 files (checked 35 source files)` | 10 | 44 |
| lint-imports (`./venv/Scripts/lint-imports.exe`) | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
| ruff format | `51 files already formatted` | `52 files already formatted` | — | — |

mypy: las 10 líneas son exactamente la lista del plan (`database.py:11`, `security.py:71/:87`,
`service_repository.py:83`, `user_service.py:124/:132/:133`, `dependencies.py:92/:93/:108`).

## Notas
- `env.py`: el orden de imports lo dejó ruff (`import app.models` y `from alembic import context` en el bloque
  first-party); `load_dotenv()` queda justo después del bloque. El resto del archivo no cambió.
- test-sanitizer (solo checklist): sin mocks, sin construcción de usuarios/tokens, nombres y aserciones en inglés, sin
  texto humano en español; nada que corregir.
- `current_target` -> `cierre` (precedente A9/SEC1): S1 no tiene más fases.

## Residuales
- Sin nuevos. Los del plan (1-7) siguen abiertos.

## Dudas
Ninguna bloqueante. Siguiente: M1 de David (`alembic current` y `alembic check`; la salida de `check` debe ser idéntica a
la de M0, `No new upgrade operations detected.`).

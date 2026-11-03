# Handoff S1 Fase B

Commit: `0e833c0 refactor(models): declare columns with Mapped and mapped_column`
Base develop re-comprobada: `git fetch origin` correcto; `origin/develop` = merge-base(HEAD, origin/develop) = `b421268`
(= `Base develop` de `verificacion.md`).
Precondición humana M0: cumplida (`docs/bitacora/2026-11-03.md`, sección "M0 del plan de S1": `alembic current` =
`2cc4b57c136c (head)`, `alembic check` = `No new upgrade operations detected.`).

## Archivos tocados
- `app/models/user.py`, `app/models/service.py`, `app/models/audit.py`. Nada más (`docs/bitacora/2026-11-03.md` tiene
  cambios sin commitear de David; no se tocó ni entró en ningún commit).

## Diff (`git show --stat HEAD` del commit de la fase)
```
 app/models/audit.py   | 25 ++++++++++++--------
 app/models/service.py | 63 +++++++++++++++++++++++++++++++++++----------------
 app/models/user.py    | 36 +++++++++++++++++------------
 3 files changed, 81 insertions(+), 43 deletions(-)
```

## Rojo de herramientas (antes de editar) -> después
- `grep -rnE "\bColumn\(" app --include=*.py | wc -l`: `33` -> `0`
- `./venv/Scripts/python.exe -m mypy 2>&1 | grep -cE "Column\[|Need type annotation"`: `34` -> `0`
- `from sqlalchemy import … Column`: 0 · `relationship(` sin anotar: 0 · `nullable=` en `app/models`: 0
- `= mapped_column(`: 33 · `: Mapped[`: 35 · `Enum(…, name="user_role|servicecategory|audit_action_enum")`: 3
- `git diff HEAD -- tests/test_models_schema.py`: vacío; `pytest tests/test_models_schema.py` -> `7 passed in 0.07s`
- `git diff b421268 --stat -- alembic/versions/ app/db/ app/services/ app/repositories/ app/api/ app/schemas/ tests/conftest.py scripts/`: vacío

## mypy (`./venv/Scripts/python.exe -m mypy`)
`Found 10 errors in 5 files (checked 35 source files)`, exactamente la lista del plan: `app\db\database.py:11`,
`app\core\security.py:71`, `:87`, `app\repositories\service_repository.py:83`, `app\services\user_service.py:124`,
`:132`, `:133`, `app\api\dependencies.py:92`, `:93`, `:108`. Ninguna línea fuera de la lista (decisión 6 no aplica).
`./venv/Scripts/python.exe -m mypy app/models 2>&1 | grep -E '^app[/\\]models[/\\]'` -> vacío.

## Mutaciones (última línea de pytest sobre `tests/test_models_schema.py`)
- M1 `user.py` nulabilidad `created_at`: `1 failed, 6 passed in 0.28s`
- M2 `user.py` `Enum(UserRole)` sin `name=`: `2 failed, 5 passed in 0.27s`
- M3 `service.py` `images: Mapped[ServiceImage]`: `1 failed, 6 passed in 0.23s`
- M4 `service.py` sin `ondelete="CASCADE"`: `1 failed, 6 passed in 0.23s`
- M5 `audit.py` `JSON()` sin variante: `1 failed, 6 passed in 0.21s`
- M6 `service.py` `Numeric()`: `1 failed, 6 passed in 0.23s`
- M7 `service.py` `name="service_category"`: `2 failed, 5 passed in 0.23s`

Tras restaurar: `git status --short` solo muestra los 3 modelos (y la bitácora de David); `7 passed in 0.10s`.

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
| Métrica | Arranque (HEAD `61cc853`) | Después (`0e833c0`) | Plan |
|---|---|---|---|
| pytest | `367 passed, 5 warnings` | `367 passed, 5 warnings in 17.50s` | 367 |
| cobertura | `94.77%` | `TOTAL 941 34 136 22 94.80%` | ≥ 94.77 % |
| ruff check | `Found 82 errors.` | `Found 76 errors.` | 76 |
| mypy | `Found 44 errors in 12 files` | `Found 10 errors in 5 files (checked 35 source files)` | 10 en 5 |
| lint-imports (`./venv/Scripts/lint-imports.exe`) | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT |
| ruff format | `51 files already formatted` | `51 files already formatted` | — |

Archivos tocados: `./venv/Scripts/python.exe -m ruff check app/models/user.py app/models/service.py app/models/audit.py`
-> `All checks passed!`; mypy filtrado por `app/models` -> vacío.

## Notas
- El hook formateó con el ruff del sistema; después se corrió `./venv/Scripts/python.exe -m ruff format` y
  `ruff check --fix` sobre los 3 archivos (`3 files left unchanged`, `All checks passed!`).
- Docstrings nuevos (Google Style, una línea + cuerpo) en `ServiceCategory`, `TouristService` (cascada ORM y FK
  `ON DELETE CASCADE`) y `ServiceImage`. Los existentes y los cuatro comentarios de `audit.py` se conservan literales
  (incluido `# "User" o "TouristService"`, residual 7).
- test-sanitizer: la fase no añade ni modifica tests; nada que revisar.

## Residuales
- Sin nuevos. Los del plan (1-7) siguen abiertos; mypy restante = A4 (9) + `service_repository.py:83` (residual 6).

## Dudas
Ninguna bloqueante. Siguiente: Fase C; tras ella, M1 de David (`alembic check` debe repetir la salida de M0).

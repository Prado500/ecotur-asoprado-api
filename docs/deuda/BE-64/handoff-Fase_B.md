# Handoff — BE-64 · Fase B (columna `users.verification_sent_at` y migración `a64d0c2e7f15`)

- **Commit de la fase:** `f22ce02` — `feat(users): add the verification_sent_at column, empty in every row` (mensaje
  exacto del plan, fase B, `plan.md:251-267`, extraído con `sed` sin reescribirlo).
- **Rama:** `item/be-64`. HEAD al arrancar: `c84f12e` (árbol limpio). **Base develop:** `b6a80ba` (`git fetch origin`
  correcto; `git rev-parse --short origin/develop` y `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `b6a80ba`, igual a `verificacion.md`).
- **Requisito previo (E1, punto 3, momento 1):** la salida de David está en `docs/bitacora/2026-11-27.md`
  (`alembic current` → `e50a7c3d9b12 (head)`; `alembic check` → `No new upgrade operations detected.`). No la corrí yo.
- **Compuerta:** `./venv/Scripts/python.exe scripts/check.py`, sin `--soft`. Windows no bloqueó `_rustgrimp`: E0,
  punto 3, no aplicó.

## Archivos tocados (4, los del plan)
- `app/models/user.py`: 3 líneas tras `email_verified_at` (comentario de 2 líneas y la columna
  `Mapped[datetime | None] = mapped_column(DateTime(timezone=True))`).
- `alembic/versions/a64d0c2e7f15_users_verification_sent_at.py` (nuevo): texto del Anexo B.
- `tests/test_models_schema.py`: una fila en `EXPECTED["users"]`.
- `tests/test_migration_verification_sent_at.py` (nuevo): texto del Anexo B.

Igualdad con el Anexo B, comprobada por hash de blob: los cuatro blobs del commit (`git rev-parse HEAD:<archivo>`) son
`2aba32d` (migración), `48cd9d8` (modelo), `33d83c4` (test de migración) y `f26f634` (test de esquema), los mismos de
las líneas `index` del Anexo B. El contenido es el del Anexo byte a byte.

## Diff (`git show --stat f22ce02`)
```
 .../a64d0c2e7f15_users_verification_sent_at.py     | 38 +++++++++
 app/models/user.py                                 |  3 +
 tests/test_migration_verification_sent_at.py       | 94 ++++++++++++++++++++++
 tests/test_models_schema.py                        |  1 +
 4 files changed, 136 insertions(+)
```

## Compuerta de arranque (antes de tocar nada)
Exit 0. `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` ·
`Contracts: 4 kept, 0 broken.` · `806 passed, 25 warnings in 32.89s` · `TOTAL 1071 10 156 6 98.70%` ·
`Compuerta superada.` Igual a la línea base de `verificacion.md`.

## RED (solo los dos archivos de test, sin `app/` ni `alembic/`)
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`, literal:
```
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\projects\\ecotur-asoprado\\alembic\\versions\\a64d0c2e7f15_users_verification_sent_at.py'
<frozen runpy>:254: FileNotFoundError
E       AssertionError: assert {'cedula': Fr...ey=None), ...} == {'cedula': Fr...ey=None), ...}
tests\test_models_schema.py:129: AssertionError
FAILED tests/test_models_schema.py::test_table_columns_match_the_frozen_schema[users]
ERROR tests/test_migration_verification_sent_at.py::test_migration_adds_the_column_empty_in_every_row
ERROR tests/test_migration_verification_sent_at.py::test_migration_downgrade_drops_only_its_column_and_keeps_the_rows
1 failed, 805 passed, 25 warnings, 2 errors in 33.88s
```
Es el esperado del plan: `1 failed, 805 passed, 2 errors`.

## Compuerta de salida (literal)
Exit 0. Líneas por paso:
```
73 files already formatted
--- ruff format --check: OK en 0.1s
All checks passed!
--- ruff check: OK en 0.1s
Success: no issues found in 68 source files
--- mypy: OK en 2.6s
Analyzed 56 files, 148 dependencies.
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
--- docs (coherencia): OK en 0.1s
TOTAL                                       1072     10    156      6  98.70%
808 passed, 25 warnings in 33.38s
--- pytest + cobertura: OK en 36.4s
```

Bloque RESUMEN, literal:
```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```
- pytest: `808 passed, 25 warnings` (0 failed). Plan: `808 passed`. ✔
- Cobertura: `98.70%` (línea base 98,70 %; no baja). ✔
- mypy: 0 errores en 68 archivos (plan: 68). ✔
- ruff: 0 errores; `73 files` formateados. ✔
- import-linter: `4 kept, 0 broken` (línea base 4). ✔

## Ruff y mypy sobre los archivos tocados
- `python -m ruff check app/models/user.py tests/test_models_schema.py tests/test_migration_verification_sent_at.py`
  → `All checks passed!`.
- `python -m ruff check --force-exclude <los cuatro>` → `All checks passed!` (la migración está en
  `extend-exclude = ["alembic/versions", …]`, `pyproject.toml:61`).
- Nombrando la migración sin `--force-exclude`, ruff salta la exclusión y da `Found 5 errors.` (UP035, I001, 3×UP007:
  `typing.Sequence`/`Union` y el orden `alembic` antes de `sqlalchemy`). Es el texto que fija el Anexo B `(backlog
  AF-18)`; la migración anterior `e50a7c3d9b12_users_email_verified_at.py` da los mismos `Found 5 errors.`. No se tocó.
- `python -m mypy <los cuatro>` → `Success: no issues found in 4 source files`.

## SQL fuera de línea (criterio de aceptación)
`DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db ./venv/Scripts/python.exe -m alembic upgrade
e50a7c3d9b12:a64d0c2e7f15 --sql`, exit 0, literal:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Generating static SQL
INFO  [alembic.runtime.migration] Will assume transactional DDL.
BEGIN;

INFO  [alembic.runtime.migration] Running upgrade e50a7c3d9b12 -> a64d0c2e7f15, users: verification_sent_at, when the last verification link was issued (BE-64)
-- Running upgrade e50a7c3d9b12 -> a64d0c2e7f15

ALTER TABLE users ADD COLUMN verification_sent_at TIMESTAMP WITH TIME ZONE;

UPDATE alembic_version SET version_num='a64d0c2e7f15' WHERE alembic_version.version_num = 'e50a7c3d9b12';

COMMIT;
```
`grep -c "UPDATE users"` → `0`. `python -m alembic heads` → `a64d0c2e7f15 (head)`.

## Mutantes MB1–MB5 (cada uno en su copia, suite completa)
Copias `git archive HEAD` (HEAD `c84f12e`) + los cuatro archivos de la fase, en `be64B1-MB1` … `be64B1-MB5` del
scratchpad; intérprete del venv por ruta, cwd = la copia; `import app; app.__file__` →
`…\scratchpad\be64B1-MBn\app\__init__.py` en las cinco. Mutante aplicado por reemplazo exacto (ancla única).

| # | Mutante | Resultado literal | Lo matan |
|---|---|---|---|
| MB1 | `op.execute("UPDATE users SET verification_sent_at = CURRENT_TIMESTAMP")` tras el batch | `1 failed, 807 passed` | `test_migration_adds_the_column_empty_in_every_row` |
| MB2 | `downgrade()` → `pass` | `2 failed, 806 passed` | los dos de `test_migration_verification_sent_at.py` |
| MB3 | modelo `Mapped[datetime]` (NOT NULL) | `194 failed, 550 passed, 4 warnings, 64 errors` (258) | `test_table_columns_match_the_frozen_schema[users]`, los 2 de migración (ERROR) y 255 más |
| MB4 | modelo `DateTime()` sin zona | `1 failed, 807 passed` | `test_table_columns_match_the_frozen_schema[users]` |
| MB5 | `downgrade()` borra también `email_verified_at` | `1 failed, 807 passed` | `test_migration_downgrade_drops_only_its_column_and_keeps_the_rows` |

5 muertos, 0 vivos; coinciden con la tabla del Análisis del plan, MB3 incluido (258 en total).

## Skill `test-sanitizer` (solo checklist, "Ecotur Enterprise Test Standards")
Sobre `tests/test_migration_verification_sent_at.py` y la fila de `tests/test_models_schema.py`: (1) sin mocks, no
aplica; (2) las tres cuentas salen de `make_user`, sin usuarios a mano; (3) nombres y variables en inglés; (4) sin
contrato JSON, no aplica; (5) sin ABAC, no aplica. Ninguna aserción sobre texto en español. No se reescribió nada.

## Incidencias y desviaciones
- **La migración se escribió con un heredoc de Bash, no con la herramienta Write**, para que el hook de formato
  `(backlog AF-18)` no la reescribiera; así no hubo nada que restaurar (riesgo 5 del plan). Su blob es `2aba32d`, el
  del Anexo B.
- **El SQL fuera de línea se corrió en el árbol de trabajo**, que sí tiene `.env` (la copia del plan no lo tenía).
  `DATABASE_URL` de la orden tiene prioridad sobre el archivo y `--sql` no conecta; no leí el `.env`. La salida es la
  que da el plan.
- `rm -rf` está denegado por permisos: las copias de mutantes se crearon en carpetas nuevas (`be64B1-…`).
- Ninguna otra desviación. No se tocó `plan.md`, `verificacion.md` ni ningún archivo fuera de los cuatro de la fase.

## Residuales
Ninguno nuevo.

## Siguiente paso (de David, no de un agente; E1, punto 3, momento 2)
Después de `/auditar BE-64 B` y **antes de `/implementar BE-64 D`** (la fase C puede correr entre medias), en `cmd`
desde `C:\projects\ecotur-asoprado`, con salida literal a la bitácora:
1. `venv\Scripts\python.exe -m alembic upgrade head` → `Running upgrade e50a7c3d9b12 -> a64d0c2e7f15`.
2. `venv\Scripts\python.exe -m alembic check` → `No new upgrade operations detected.` (si lista operaciones, el ítem
   se detiene).
3. `venv\Scripts\python.exe -m alembic downgrade -1` → `Running downgrade a64d0c2e7f15 -> e50a7c3d9b12`.
4. `venv\Scripts\python.exe -m alembic upgrade head`.
5. En su cliente SQL: `SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name =
   'users' AND column_name = 'verification_sent_at';` → `verification_sent_at | timestamp with time zone | YES`.
6. `SELECT count(*) FROM users WHERE verification_sent_at IS NOT NULL;` → `0`.

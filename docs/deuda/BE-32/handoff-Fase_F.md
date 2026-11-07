# Handoff — BE-32 Fase_F: `save_service`, su fila entre dos, su `deleted_at` y su `Raises:`

**Commit de la fase:** `8b2cfe2` (`test(service-repo): pin save_service to its own row and deletion date`). El mensaje
es el del plan letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:**
`/implementar BE-32 Fase_G`.

## Arranque

- Árbol limpio, HEAD `2af510a`, `current_target` = `Fase_F`.
- Línea base: `git fetch origin` correcto; `origin/develop` = `fd144ad` y `merge-base HEAD origin/develop` = `fd144ad`,
  iguales a `Base develop` de `verificacion.md`.
- Compuerta antes de tocar nada (exit 1): igual a la fila E. `57 files already formatted`; ruff `Found 8 errors.` (los
  8 I001 `app\...:1:1`); mypy `Found 9 errors in 5 files (checked 53 source files)` (A4 en
  `tests\test_user_service.py:105,203,280,298`); `Contracts: 4 kept, 0 broken.`; `545 passed, 5 warnings`;
  `TOTAL 943 23 138 19 96.11%`.

## Archivos tocados

`git show --stat 8b2cfe2`:

```text
 app/repositories/service_repository.py |  3 +++
 tests/test_service_repository.py       | 11 +++++++----
 2 files changed, 10 insertions(+), 4 deletions(-)
```

- `tests/test_service_repository.py`: vecina `_package(name="Paquete Vecino De Prueba")` persistida tras `package` en
  `test_save_service_commits_pending_changes_and_returns_the_row` y en `test_save_service_returns_a_soft_deleted_row`;
  en este último, `assert saved.deleted_at == deleted_at.replace(tzinfo=None)` precedido de
  `# SQLite returns the column without its time zone.`; los tres docstrings dictados por el plan.
- `app/repositories/service_repository.py`: solo el elemento `StaleDataError` de `Raises:`, tras `NoResultFound`.

`git show 8b2cfe2 -- app/` (solo la parte del diff):

```text
@@ -86,6 +86,9 @@ class ServiceRepository:
         Raises:
             NoResultFound: The row is gone. It was just committed and nothing deletes rows
                 physically, so this is a broken invariant, not a business case.
+            StaleDataError: The commit flushed a pending change to a row that another session had
+                already deleted (the UPDATE matched no row): the same broken invariant, caught
+                earlier.
         """
         await self.db.commit()
         stmt = (
```

`grep -c "StaleDataError" app/repositories/service_repository.py` = `1`.

## RED: mutantes M5 y M10 en copia desechable

Copia fuera del árbol: `git archive HEAD | tar -x` (HEAD `2af510a`) en el scratchpad de la sesión, con los 2 archivos
modificados de la fase copiados encima **antes del commit**. `git diff --name-only` listaba exactamente esos 2 y `cmp`
dio idénticos byte a byte, así que la copia era el árbol que se commiteó. Tras el commit, el test de la copia es igual
byte a byte a `8b2cfe2:tests/test_service_repository.py`. El `service_repository.py` de la copia es igual a
`8b2cfe2:app/repositories/service_repository.py` salvo los fines de línea: el `write_text` del `finally` lo restauró con
CRLF, después de medir. Variables de entorno ficticias (`JWT_SECRET_KEY`, `ALGORITHM`, `*_EXPIRE_MINUTES`,
`DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`, `CORS_ORIGINS`, `FRONTEND_URL`) y el Python del
`venv/`; `app` resolvía a la copia. Un script localiza `save_service` por contenido y aplica:

- **M5:** borra la línea `.where(TouristService.id == service.id)` del `select` de `save_service` (`:94` en la base,
  `:97` tras el docstring nuevo).
- **M10:** inserta `service.deleted_at = datetime(2000, 1, 1, tzinfo=UTC)` antes del `await self.db.commit()` de
  `save_service`, y `from datetime import UTC, datetime` al principio del archivo.

Corre pytest con `--no-cov` y restaura el archivo en un `finally`. El repo nunca llevó un mutante: `git status --short`
solo listaba los 2 archivos de la fase.

| Mutante | Antes (archivo; tests de HEAD `2af510a`) | Después (archivo; estado commiteado `8b2cfe2`) | Antes (suite; `2af510a`) | Después (suite; `8b2cfe2`) |
|---|---|---|---|---|
| sin mutante | `5 passed` | `5 passed` | `545 passed, 5 warnings` | `545 passed, 5 warnings` |
| M5 | `5 passed` | `2 failed, 3 passed` (commits y soft-deleted: `MultipleResultsFound`) | `545 passed, 5 warnings` | `2 failed, 543 passed, 5 warnings` |
| M10 | `5 passed` | `1 failed, 4 passed` (soft-deleted) | `3 failed, 542 passed, 5 warnings` | `4 failed, 541 passed, 5 warnings` |

Las columnas de archivo coinciden con la tabla del plan. Salida literal del script (líneas de resumen):

```text
# despues, archivo (estado final de la fase)
unmutated:
    5 passed in 0.13s
M5:
    FAILED tests/test_service_repository.py::test_save_service_commits_pending_changes_and_returns_the_row
    FAILED tests/test_service_repository.py::test_save_service_returns_a_soft_deleted_row
    2 failed, 3 passed in 0.28s
M10:
    FAILED tests/test_service_repository.py::test_save_service_returns_a_soft_deleted_row
    1 failed, 4 passed in 0.24s
# antes, archivo (tests de HEAD 2af510a)
unmutated:
    5 passed in 0.11s
M5:
    5 passed in 0.10s
M10:
    5 passed in 0.10s
# antes, suite (tests de HEAD 2af510a)
unmutated:
    545 passed, 5 warnings in 19.93s
M5:
    545 passed, 5 warnings in 20.11s
M10:
    FAILED tests/test_services.py::test_deactivate_and_activate_package - assert ...
    FAILED tests/test_services.py::test_soft_delete_and_recover - assert datetime...
    FAILED tests/test_services.py::test_update_package_concurrent_reconciliation
    3 failed, 542 passed, 5 warnings in 21.25s
# despues, suite (estado final de la fase)
unmutated:
    545 passed, 5 warnings in 20.84s
M5:
    FAILED tests/test_service_repository.py::test_save_service_commits_pending_changes_and_returns_the_row
    FAILED tests/test_service_repository.py::test_save_service_returns_a_soft_deleted_row
    2 failed, 543 passed, 5 warnings in 20.80s
M10:
    FAILED tests/test_service_repository.py::test_save_service_returns_a_soft_deleted_row
    FAILED tests/test_services.py::test_deactivate_and_activate_package - assert ...
    FAILED tests/test_services.py::test_soft_delete_and_recover - assert datetime...
    FAILED tests/test_services.py::test_update_package_concurrent_reconciliation
    4 failed, 541 passed, 5 warnings in 20.47s
```

Causa de cada fallo, impresa por una variante del script sobre el estado final:
`sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when exactly one was required` (las 2 de M5) y
`assert datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc) == datetime.datetime(2026, 1, 15, 12, 0)`
(M10).

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

- `ruff format --check`: `57 files already formatted`.
- `ruff check`: `Found 8 errors.`. Las 8 son I001 `:1:1` en `app\api\dependencies.py`, `app\api\routers\audit.py`,
  `app\core\email.py`, `app\db\database.py`, `app\repositories\user_repository.py`, `app\schemas\audit.py`,
  `app\services\audit_service.py` y `app\services\user_service.py`. `service_repository.py` no está entre ellas; solo
  aparece como línea de import dentro del fragmento del I001 de `dependencies.py`, igual que antes de la fase.
- mypy: `Found 9 errors in 5 files (checked 53 source files)`: `app\db\database.py:11`, `app\core\security.py:71`,
  `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95` y `tests\test_user_service.py:105`, `:203`,
  `:280`, `:298`, los 4 `[arg-type]` `str | None` de `SECRET_KEY`. Es el conjunto de A4.
- import-linter: `Contracts: 4 kept, 0 broken.`
- pytest: `545 passed, 5 warnings in 20.66s`.
- Cobertura: `TOTAL 943 23 138 19 96.11%` (antes: 96.11 %).

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Archivos tocados: `ruff check` dice `All checks passed!` y `ruff format --check` dice `2 files already formatted`.
`mypy app/repositories/service_repository.py tests/test_service_repository.py` da 0 errores en esos dos archivos. Solo
informa de `app\db\database.py:11` (A4), que entra al seguir los imports.

Checklist de `test-sanitizer` (Enterprise Test Standards): no hay dobles nuevos; la vecina usa las fábricas locales
`_package`/`_persist`; nombres, comentario y docstrings en inglés; ninguna aserción lee texto en español (el nombre de
la vecina es un dato, no una aserción). No hubo que reescribir nada.

## Desviaciones y dudas

1. **El `Raises:` ocupa 3 líneas, no 2.** El texto dictado, con el corte del plan, deja la segunda línea en 103
   columnas. El hook devolvió `E501 Line too long (103 > 100)` en `service_repository.py:90`. Con sangrías de 12 y 16,
   el texto (174 caracteres) no cabe en dos líneas de 100 columnas, donde caben 172. Apliqué la regla del plan: "los
   bloques de código dictan el contenido exacto; el corte de línea es el que deje `ruff format` (100 columnas)". El
   contenido es letra a letra el dictado. La primera línea queda igual que en el plan, y la segunda se corta en el
   último espacio antes de la columna 100, así que `earlier.` pasa a una tercera línea. Consecuencias: el criterio
   "el `git diff` de `app/` se limita a esas 2 líneas de docstring" se cumple en espíritu (solo el docstring) pero son
   **3 líneas**. Y el patrón 10 de la verificación final dará
   `1 file changed, 3 insertions(+)`, no `2 insertions(+)`. El auditor y la verificación final deben leer 3.
2. **M10 ya lo detectaba la suite antes de la fase** (3 tests de `test_services.py`). La tabla del plan es por archivo
   y su columna "Antes" (`5 passed`) coincide. Lo que la fase añade es que el propio archivo del repositorio lo detecta.
3. En la copia, el `service_repository.py` restaurado quedó con CRLF por el `write_text` del script en Windows. Pasó
   después de medir y no afecta a ninguna cifra.

## Residuales

- Sin cambios respecto al plan: ningún test provoca el `StaleDataError` que ahora documenta el `Raises:`
  (Residuales del plan, nota en BE-31).

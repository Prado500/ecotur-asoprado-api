# Handoff — BE-15 Fase A: el doble global de almacenamiento con la firma de `AzureStorageClient`

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `9484b04`
  (`test(conftest): give the global storage double the adapter's autospec`, mensaje exacto del plan)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.

## Archivos tocados

Solo los tres que el plan asigna a la fase A:

```
 tests/conftest.py               | 34 +++++++++++++++++--------------
 tests/test_fixtures_contract.py | 44 +++++++++++++++++++++++++++++++++++++++++
 tests/test_services.py          |  4 ++--
 3 files changed, 65 insertions(+), 17 deletions(-)
```

- `tests/conftest.py`, en `override_azure_storage_client`: `mock_client = create_autospec(AzureStorageClient,
  instance=True)`; `upload_image.return_value` (la misma URL temporal), `delete_image.return_value = None`,
  `promote_to_permanent.side_effect = mock_promote`, `is_temporal_url` / `is_permanent_url` como `.side_effect =
  lambda url: ...` con los mismos prefijos. Borradas las asignaciones de `container_name` y `temporal_container_name`.
  La docstring ya no habla de "environment variables": explica que el doble lleva la firma del adaptador. Imports:
  fuera `AsyncMock` y `MagicMock` (los quitó el hook al quedar sin uso); dentro `create_autospec` y `from
  app.core.storage import AzureStorageClient`.
- `tests/test_services.py:234`: `failing_client.upload_image.side_effect = StorageUnavailableError("cdn outage")`;
  `AsyncMock` fuera del import de la l.11.
- `tests/test_fixtures_contract.py` (nuevo): docstring de módulo del plan y 4 tests a nivel de módulo; todos
  obtienen el doble con `app.dependency_overrides[get_storage_client]()`.

## RED → GREEN

RED, con el `conftest.py` original (`pytest -p no:cacheprovider tests/test_fixtures_contract.py -q`):

```
FAILED tests/test_fixtures_contract.py::test_storage_double_is_specced_on_the_adapter
FAILED tests/test_fixtures_contract.py::test_storage_double_rejects_unknown_attribute
FAILED tests/test_fixtures_contract.py::test_storage_double_rejects_a_call_off_the_adapter_signature
3 failed, 1 passed in 0.38s
```

El tercero falló con `Failed: DID NOT RAISE <class 'TypeError'>`, como prevé el plan. El cuarto
(`test_storage_double_mirrors_the_cdn_url_rules`) pasa antes y después.

GREEN, tras el cambio (`tests/test_fixtures_contract.py tests/test_services.py`): `40 passed, 3 warnings in 3.55s`
(4 de contrato + los 36 de `test_services.py`).

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

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

| Medida | Línea base (antes de tocar) | Tras la fase A | Fila "Fase A" del plan |
|---|---|---|---|
| pytest | `376 passed, 5 warnings` | `380 passed, 5 warnings in 19.76s` | 380 |
| Cobertura | `TOTAL 942 34 136 22 94.81%` | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % |
| import-linter | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT |
| ruff total | `Found 60 errors.` | `Found 60 errors.` | 60 |
| ruff en `tests/` | `Found 7 errors.` | `Found 7 errors.` | 7 |
| mypy | `Found 10 errors in 5 files (checked 35 source files)` | igual | 10 |

Criterios propios de la fase:

- `ruff check tests/conftest.py tests/test_services.py tests/test_fixtures_contract.py` → `All checks passed!`
- `ruff format --check` de los tres → `3 files already formatted`
- `grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py | wc -l` → `0`
- Los 36 tests de `test_services.py` siguen pasando.

## Residuales

- `mypy` sobre los archivos de test tocados (la compuerta solo mide `app/`) da 2 errores en `tests/`, heredados:
  `tests/test_services.py:183` (`Value of type "object" is not indexable`) y `tests/conftest.py:210`
  (`Returning Any from function declared to return "User"`, en `persist_user._persist`). Comprobado sobre
  `HEAD~1` (copia en el scratchpad): los mismos dos errores (`conftest.py:206` allí; la línea se desplazó 4 por el
  diff). Ninguno cae en las líneas que cambia esta fase; no se tocan.
- Los 7 errores de ruff de `tests/` siguen fuera de los tres archivos de la fase (los reparten las fases B, C y E,
  más el I001 de `test_user_service.py`).

## Desviaciones y dudas

- Ninguna desviación del plan. Los imports `AsyncMock`/`MagicMock` los eliminó el hook de ruff
  (`ruff check --fix`) al quedar sin uso, en lugar de una edición manual; el resultado es el que pide el plan.
- `test-sanitizer` aplicado como checklist: el doble es `create_autospec`; los tests nuevos afirman tipos,
  ausencia de atributo, `TypeError` y `assert_awaited_once_with(TEMP)`; ningún texto en español; sin clases.

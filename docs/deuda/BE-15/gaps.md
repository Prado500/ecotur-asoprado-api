# GAPS — BE-15

Un solo archivo por ID. Cada auditoría añade su bloque; los bloqueantes corregidos se marcan `RESUELTO (<hash>)` y
no se borran.

## Auditoría Fase A — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 1 opcional).
- **Auditado:** `9484b04` (fase) y `68cf40c` (registro en `progress.json` y handoff). Base de la fase: `987e568`.
- **Árbol:** `git status --short` vacío antes y después de la auditoría.

### Evidencia

- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1, rojo heredado previsto por la
  decisión 8 del plan):

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

  | Medida | Línea base (`verificacion.md`) | Auditoría | Fila "Fase A" del plan | Handoff |
  |---|---|---|---|---|
  | pytest | 376 passed | `380 passed, 5 warnings in 19.90s` | 380 | 380 |
  | Cobertura | 94.81 % | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | 4 kept | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | 60 | `Found 60 errors.` | 60 | 60 |
  | ruff en `tests/` | 7 | `Found 7 errors.` (test_audit 1, test_auth 3, test_user_access_policy 2, test_user_service 1) | 7 | 7 |
  | mypy | 10 | `Found 10 errors in 5 files (checked 35 source files)` | 10 | 10 |
  | ruff format | OK | `53 files already formatted` | OK | OK |

- Archivos tocados: `ruff check tests/conftest.py tests/test_services.py tests/test_fixtures_contract.py` →
  `All checks passed!`; `ruff format --check` de los tres → `3 files already formatted`.
- `git show --stat 9484b04` → exactamente `tests/conftest.py`, `tests/test_fixtures_contract.py` (nuevo),
  `tests/test_services.py`. `git diff --stat 987e568..HEAD -- app/ AGENTS.md CLAUDE.md pyproject.toml scripts/
  .azure-pipelines/ .claude/` → vacío.
- Mensaje de commit: el cuerpo de `9484b04` (sin el trailer `Co-Authored-By`) es idéntico byte a byte al bloque
  "Commit" de la fase A en `plan.md:199-213` (`diff` → sin diferencias).
- Cambios exactos, todos presentes en el diff: `create_autospec(AzureStorageClient, instance=True)`
  (`tests/conftest.py:85`); `upload_image.return_value` con la misma URL (`:88-90`); `delete_image.return_value =
  None` (`:91`); `promote_to_permanent.side_effect = mock_promote` (`:97`); `is_temporal_url`/`is_permanent_url`
  como `.side_effect` con los mismos prefijos (`:101-106`); asignaciones de `container_name` borradas
  (`grep -rn container_name tests/` → solo `.pyc`); docstring sin "environment variables" (`:77-83`); imports
  `create_autospec` y `AzureStorageClient` (`:2`, `:12`), sin `AsyncMock`/`MagicMock`. `tests/test_services.py:234`
  usa `failing_client.upload_image.side_effect = StorageUnavailableError("cdn outage")` y la l.11 ya no importa
  `AsyncMock`. `tests/test_fixtures_contract.py`: docstring de módulo literal del plan y los 4 tests a nivel de
  módulo con los nombres del plan, todos vía `app.dependency_overrides[get_storage_client]()`.
- RED reproducido por el auditor con el `conftest.py` de `987e568` cargado como plugin (`pytest --noconftest -p
  be15_base_conftest tests/test_fixtures_contract.py`): `3 failed, 1 passed`; fallan los tests 1-3 (el 3 con
  `Failed: DID NOT RAISE <class 'TypeError'>`), pasa el 4. GREEN: `tests/test_fixtures_contract.py
  tests/test_services.py` → `40 passed`; `test_services.py` sigue con `36 tests collected`.
- Criterio de aceptación: `grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py | wc -l`
  → `0`.
- `progress.json`: JSON válido; `Fase_A` = `completed` con `commit` `9484b04` (real); `current_target` = `Fase_B`;
  `last_handoff` presente; `edit_rules` y `approval` sin cambios respecto a `987e568` (el diff solo toca esos cuatro
  campos).
- AGENTS §5: el doble y el de `test_services.py:233` son `create_autospec`; el test 4 verifica el mock con
  `assert_awaited_once_with(TEMP)`; ninguna aserción sobre texto en español; docstrings en inglés; sin clases.

### Hallazgos

- [OPCIONAL] — Fase A — `mypy` sobre los archivos de test tocados da 2 errores: `tests/test_services.py:183`
  (`Value of type "object" is not indexable [index]`) y `tests/conftest.py:210` (`Returning Any from function
  declared to return "User" [no-any-return]`). ADR-0005 (`docs/adr/0005-trinquete-de-calidad-contra-la-linea-base.md:13`)
  pide 0 errores de mypy en los archivos tocados, pero `tests/` está fuera del alcance configurado de mypy
  (`pyproject.toml:90`, `files = ["app", ...]`), ninguno cae en las líneas del diff y los dos ya estaban en `987e568`
  (comprobado por el auditor sobre `git show 987e568:tests/...`: `test_services.py:183` y `conftest.py:206`). No los
  introduce la fase y el plan aprobado fija mypy = 10 en el alcance de la compuerta. Destino: residual, junto con la
  entrada de `tests/` en el alcance de mypy (PLAN día 4-5), no se exige corrección en BE-15.

# Handoff — A4 · Fase G (Adaptador de Azure construido desde `Settings` inyectado)

- Commit de la fase: `714e05a` — `refactor(storage): build the Azure adapter from injected Settings (A4)`
- Rama: `item/a4`, sobre `e6feb08` (bitácora tras la auditoría de F en PASS).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.
- Enmiendas aplicables: E0 (Azure no cambia de comportamiento, solo de dónde lee su configuración) y **E1** (borrar
  `# Repository injection` y `# Service injection` de `app/api/dependencies.py`).

## Ritual de arranque

- `git status --short`: limpio. HEAD `e6feb08`. `current_target` = `Fase_G`. `gaps.md`: A–F en PASS, sin bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila F: `60 files already formatted` · ruff `Found 4 errors.` ·
  mypy `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` · `576 passed, 5 warnings` ·
  `TOTAL 969 23 138 19 96.21%` · `Compuerta NO superada: ruff check`.

## Archivos tocados

`app/core/storage.py`, `app/api/dependencies.py`, `tests/test_storage.py`. Ningún otro.

`git show --stat 714e05a`:

```
 app/api/dependencies.py | 24 ++++++++++++++++++------
 app/core/storage.py     | 30 ++++++++++++++++++++++--------
 tests/test_storage.py   | 40 +++++++++++++++++++++++++++++++---------
 3 files changed, 71 insertions(+), 23 deletions(-)
```

Resumen del diff:

- `app/core/storage.py`: fuera `import os`. `__init__(self, connection_string: str, container_name: str,
  temporal_container_name: str) -> None` guarda los tres valores, conserva el `ValueError` si la cadena está vacía (antes
  de llamar a `BlobServiceClient.from_connection_string`, mismo orden que antes) y lleva docstring con `Args`/`Raises`.
  Los métodos del adaptador no cambian.
- `app/api/dependencies.py`: `get_storage_client(settings: Settings = Depends(get_settings)) -> AzureStorageClient`
  devuelve `AzureStorageClient(connection_string=settings.azure_storage_connection_string,
  container_name=settings.azure_container_name, temporal_container_name=settings.azure_temporal_container_name)`, con
  docstring Google (`Args`/`Returns`). **E1:** borradas las líneas `# Repository injection` y `# Service injection` y la
  línea en blanco que precedía a cada una; los imports `app.*` quedan contiguos, sin reordenar ni cambiar ninguno.
  `# --- DEPENDENCY FACTORY (Inversion of Control) ---` intacto (`:21`).
- `tests/test_storage.py`: imports `from app.api.dependencies import get_storage_client` y
  `from app.core.config import get_settings`. El fixture `doubles` ya no recibe `monkeypatch` ni usa `setenv`; construye
  el cliente con `connection_string="UseDevelopmentStorage=true", container_name="ecotur-images",
  temporal_container_name="temp-ecotur-images"`. `test_init_without_connection_string_raises` pasa `connection_string=""`
  (sin `delenv`). Test nuevo `test_get_storage_client_builds_the_adapter_from_settings` según el plan
  (`patch.object(storage_module, "BlobServiceClient", autospec=True)`).

## Tests (RED primero)

Cambios de tests escritos antes de tocar `app/`. RED literal (`tests/test_storage.py`):

```
E           TypeError: get_storage_client() takes 0 positional arguments but 1 was given
FAILED tests/test_storage.py::test_init_without_connection_string_raises - Ty...
FAILED tests/test_storage.py::test_get_storage_client_builds_the_adapter_from_settings
ERROR tests/test_storage.py::test_upload_image_rejects_non_image_content_type
...
2 failed, 17 errors in 1.85s
```

(Los 17 `ERROR` son el fixture `doubles` con `TypeError` al pasar argumentos al `__init__` viejo.)

Tras el cambio: `tests/test_storage.py tests/test_services.py tests/test_fixtures_contract.py` → `64 passed`;
`ruff check` de los 3 archivos → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
`mypy` de los 3 → `Success: no issues found in 3 source files`.

Checklist `test-sanitizer` (Enterprise Test Standards): el único doble nuevo (`BlobServiceClient`) usa `autospec=True`;
nombres en inglés; ninguna aserción sobre texto en español; sin preparación duplicada que deba ir a `conftest.py`.

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
TOTAL                                        968     22    138     19  96.29%
577 passed, 5 warnings in 18.96s

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
| Esperado (fila G) | 4 | `Success: no issues found in 55 source files` | 577 | ≥ 96.11 % | 60 | 4 kept |
| Real | 4 | `Success: no issues found in 55 source files` | 577 passed | 96.29 % | 60 | 4 kept |

Cobertura 96.21 % → 96.29 %: `TOTAL` pasa de `969 23` a `968 22`. `app/api/dependencies.py` deja de tener líneas sin
cubrir (el cuerpo de `get_storage_client` solo se ejecutaba con el override de los tests; ahora lo ejecuta el test
nuevo) y queda entre los 26 archivos con cobertura completa, igual que `app/core/storage.py`.

## Mutante M8 (copia `git archive HEAD` de `714e05a` en el scratchpad, sin `.env`)

```
$ sed -i 's/ container_name=settings.azure_container_name,/ container_name=settings.azure_temporal_container_name,/' app/api/dependencies.py
$ grep -n "container_name=settings" app/api/dependencies.py
73:        container_name=settings.azure_temporal_container_name,
74:        temporal_container_name=settings.azure_temporal_container_name,
$ python -m pytest -q -p no:cacheprovider tests/test_storage.py -k from_settings
E       AssertionError: assert ('temp-c', 'temp-c') == ('perm-c', 'temp-c')
FAILED tests/test_storage.py::test_get_storage_client_builds_the_adapter_from_settings
1 failed, 18 deselected in 0.26s
```

Esperado: `1 failed`. Coincide. Control sin mutante en otra copia de `HEAD`: `1 passed, 18 deselected in 0.05s`.
Copias: `C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\d5752b8a-a1fb-4650-a57d-6b3899de76c6\scratchpad\tmp.U239JU2s8N`
(mutante) y `...\scratchpad\tmp.pbHqKOfUf4` (control).

## Criterios de aceptación y Verificación final

- `git grep -n -E "getenv|setenv|delenv" -- app/core/storage.py tests/test_storage.py` → 0 líneas (exit 1).
- **E1:** `git grep -n -E "# (Repository|Service) injection" -- app/api/dependencies.py` → 0 líneas (exit 1);
  `ruff check` y `ruff format --check` del archivo limpios.
- Verificación final #1 (`os\.getenv|os\.environ|getenv\(|environ\[|environ\.get` en `app alembic tests scripts`) →
  **0 líneas** (exit 1): ya su valor final.
- #5 → 2 líneas, sin cambios: `app/main.py:168` y `app/main.py:187`.
- `app/services` no importa `fastapi` ni `starlette`; import-linter 4 kept.
- Suite exportada (`git archive HEAD`, sin `.env`, `env -u` de las 5 obligatorias) → `577 passed, 5 warnings in 19.13s`.
- `git ls-files --eol` de los 3 archivos → `i/lf w/lf attr/text=auto eol=lf`.

## Residuales y dudas

- Texto no dictado: el mensaje del `ValueError` pasa de `"AZURE_STORAGE_CONNECTION_STRING is missing in environment
  variables."` a `"connection_string must be a non-empty Azure Storage connection string."`. El plan dicta conservar el
  `ValueError`, no su texto; el viejo hablaba de variables de entorno que el adaptador ya no lee y nombraba una variable
  en mayúsculas en `app/` (regla "Texto no dictado"). Es un mensaje de desarrollador, no de usuario final, y ningún test
  afirma sobre él. Con `Settings` (`min_length=1`) la rama solo se alcanza construyendo el adaptador a mano.
- `tests/conftest.py` (dobles globales de `get_storage_client`) no se tocó: los overrides son `lambda: mock_client` sin
  argumentos y FastAPI los sigue aceptando; `tests/test_fixtures_contract.py` y `tests/test_services.py` en verde.
- BE-42 (`get_current_user` sin `scope`) fuera de A4: no tocado.

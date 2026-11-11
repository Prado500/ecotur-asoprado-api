# Handoff — A4 · Fase H (`.env.example` completo y válido; CI sin `env:`)

- Commit de la fase: `c2ffea8` — `chore(config): complete .env.example; drop the CI gate's env block (A4)`
- Rama: `item/a4`, sobre `8d1afcb` (auditoría de G en PASS, E1 aplicada).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.
- Enmiendas aplicables: E0/P4 (el bloque `env:` del paso de la compuerta se elimina entero, también
  `MAIL_USERNAME`/`MAIL_PASSWORD`); E0/P1 (`cd-pipeline.yml` no se toca).

## Ritual de arranque

- `git status --short`: limpio. HEAD `8d1afcb`. `current_target` = `Fase_H`. `gaps.md`: A–G en PASS, sin bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila G: `60 files already formatted` · ruff `Found 4 errors.` ·
  mypy `Success: no issues found in 55 source files` · `Contracts: 4 kept, 0 broken.` · `577 passed, 5 warnings` ·
  `TOTAL 968 22 138 19 96.29%` · `Compuerta NO superada: ruff check`.

## Archivos tocados

`.env.example`, `.azure-pipelines/ci-pipeline.yml`, `tests/test_config.py`. Ningún otro (`cd-pipeline.yml` intacto).
`.env` no se leyó en ningún momento.

`git show --stat c2ffea8`:

```
 .azure-pipelines/ci-pipeline.yml |  6 +-----
 .env.example                     | 21 ++++++++++++++++++---
 tests/test_config.py             | 21 +++++++++++++++++++++
 3 files changed, 40 insertions(+), 8 deletions(-)
```

Resumen del diff:

- `.env.example`: `:20-22` → `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `VERIFICATION_TOKEN_EXPIRE_MINUTES=15`;
  `:19` (`JWT_SECRET_KEY`) intacta. Tras el bloque JWT, bloque `# Email (SMTP account that sends the verification email)`
  con `MAIL_USERNAME=cuenta_smtp@example.com`, `MAIL_PASSWORD=DIGITAR_CONTRASEÑA_DE_APLICACION`,
  `# Optional: when missing, the sender is MAIL_USERNAME.`, `MAIL_FROM=cuenta_smtp@example.com`, `MAIL_PORT=465`,
  `MAIL_SERVER=smtp.gmail.com`. `AZURE_TEMPORAL_CONTAINER_NAME=temp-ecotur-images` tras `AZURE_CONTAINER_NAME`. Bloque
  `# Frontend (base URL of the links sent by email)` con `FRONTEND_URL=http://localhost:3000` antes del de CORS. Solo
  placeholders y valores por defecto públicos.
- `.azure-pipelines/ci-pipeline.yml`: borradas `:32-36` (`env:` y sus 4 variables). Tras el comentario `--soft` (`:28`)
  y sobre `- script:` va `# No env block: the suite fixes its own configuration in conftest.py (ADR-0013).`
  `--soft`, `variables: group` y el resto del YAML, intactos.
- `tests/test_config.py`: `from dotenv import dotenv_values`;
  `ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"` (tras `ALL_FIELDS`); dos tests nuevos al final:
  `test_env_example_is_a_valid_configuration(monkeypatch)` (borra los 15 campos del entorno con `_clear`, construye
  `Settings(_env_file=ENV_EXAMPLE)` y afirma `(algorithm, access_token_expire_minutes,
  verification_token_expire_minutes) == ("HS256", 30, 15)`) y `test_env_example_documents_every_setting`
  (`{n.upper() for n in Settings.model_fields} <= set(dotenv_values(ENV_EXAMPLE))`).

## Tests (RED primero)

Los dos tests se escribieron antes de tocar `.env.example`. RED literal
(`pytest -q -p no:cacheprovider tests/test_config.py -k env_example`):

```
E       pydantic_core._pydantic_core.ValidationError: 4 validation errors for Settings
E       access_token_expire_minutes
E         Input should be a valid integer, unable to parse string as an integer [type=int_parsing]
E       verification_token_expire_minutes
E         Input should be a valid integer, unable to parse string as an integer [type=int_parsing]
E       mail_username
E         Field required [type=missing]
E       mail_password
E         Field required [type=missing]
E       AssertionError: assert {'ACCESS_TOKE...ORIGINS', ...} <= {'ACCESS_TOKE...ASE_URL', ...}
E         Extra items in the left set:
E         'MAIL_PORT'
E         'MAIL_SERVER'
E         'FRONTEND_URL'
E         'MAIL_USERNAME'
E         'MAIL_FROM'
E         'AZURE_TEMPORAL_CONTAINER_NAME'
E         'MAIL_PASSWORD'
FAILED tests/test_config.py::test_env_example_is_a_valid_configuration - pyda...
FAILED tests/test_config.py::test_env_example_documents_every_setting - Asser...
2 failed, 21 deselected in 0.21s
```

(Líneas `For further information visit …` omitidas.) Coincide con el plan: `ValidationError` (`mail_username` ausente,
`int_parsing`) y 7 claves faltantes. Tras el cambio: `tests/test_config.py` → `23 passed in 0.31s`; `ruff check` →
`All checks passed!`; `ruff format --check` → `1 file already formatted`; `mypy tests/test_config.py` →
`Success: no issues found in 1 source file`.

Checklist `test-sanitizer` (Enterprise Test Standards): sin dobles; nombres, docstrings y aserciones en inglés; ninguna
aserción sobre texto en español (se afirma sobre tipos, valores por defecto y conjuntos de claves); el entorno se arma
solo con `monkeypatch` (helper `_clear` existente) y no depende del `.env` local (el primer test borra los 15 campos y
lee solo `.env.example`; el segundo no lee el entorno). Ningún test previo reescrito.

## Validez del YAML

`yaml.safe_load` (PyYAML 6.0.3, del `venv`) sobre `.azure-pipelines/ci-pipeline.yml` tras el cambio:

```
{"script": "python scripts/check.py --soft format,ruff,mypy\n", "displayName": "Compuerta de calidad (scripts/check.py)"}
[['task', 'displayName', 'inputs'], ['script', 'displayName'], ['script', 'displayName']]
[{'name': 'pythonVersion', 'value': '3.14'}, {'group': 'VG-ECOTUR-DEV'}]
```

El último paso ya no tiene clave `env`; los tres pasos y `variables` se conservan.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

```
60 files already formatted
 --> app\api\routers\audit.py:1:1
 --> app\repositories\user_repository.py:1:1
 --> app\schemas\audit.py:1:1
 --> app\services\audit_service.py:1:1
Found 4 errors.
Success: no issues found in 55 source files
Contracts: 4 kept, 0 broken.
TOTAL                                        968     22    138     19  96.29%
579 passed, 5 warnings in 14.20s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check
```

Los 4 errores de ruff son los I001 de la fase I.

| | ruff check | mypy | pytest | cobertura | format | contratos |
|---|---|---|---|---|---|---|
| Esperado (fila H) | 4 | `Success: no issues found in 55 source files` | 579 | ≥ 96.11 % | 60 | 4 kept |
| Real | 4 | `Success: no issues found in 55 source files` | 579 passed | 96.29 % | 60 | 4 kept |

Cobertura sin cambios (`TOTAL 968 22`): la fase no toca `app/`.

## Mutantes y sondas

El plan no dicta mutantes para H; el RED de los dos tests es el cambio de `.env.example` de la propia fase (arriba).

## Criterios de aceptación y Verificación final

- `git grep -n -E "^\s+env:" -- .azure-pipelines/ci-pipeline.yml` → 0 líneas (exit 1).
- `git grep -n "tu_correo@gmail.com" -- app tests .env.example` → 0 líneas (exit 1).
- `git grep -n -- "--soft" -- .azure-pipelines` → 2 líneas (`ci-pipeline.yml:28` y `:31`), como espera la Verificación
  final #8.
- Verificación final #1 → 0 líneas (exit 1). #3 → 2 líneas, ambas `from dotenv import dotenv_values`:
  `tests/test_config.py:13` y `tests/test_token_failure_paths.py:16` (su valor final).
- `cd-pipeline.yml`: sin cambios en el commit (`git diff HEAD~1 --stat -- .azure-pipelines/cd-pipeline.yml` vacío).
- Suite exportada (`git archive HEAD` de `c2ffea8` en
  `C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\d5752b8a-a1fb-4650-a57d-6b3899de76c6\scratchpad\tmp.VEIHEMk5gY`,
  `test ! -e .env` correcto, `env -u` de las 5 obligatorias) → `579 passed, 5 warnings in 14.15s`.
- `git ls-files --eol` de los 3 archivos → `i/lf w/lf attr/text=auto eol=lf`.
- **MD (David, en el PR):** el paso "Compuerta de calidad (scripts/check.py)" del CI pasa sin el bloque `env:`. Pendiente.

## Residuales y dudas

- Formato de los dos bloques nuevos de `.env.example`: el plan dicta el texto de su encabezado (`# Email (…)`,
  `# Frontend (…)`); se enmarcaron con las líneas `# ====…` que usan todos los bloques del archivo, para no romper su
  estilo. Además, las dos líneas en blanco que había tras el bloque JWT quedan en una, como entre los demás bloques.
- `ci-pipeline.yml` no terminaba en salto de línea (`\ No newline at end of file`); tras borrar `:32-36` el archivo
  termina en `\n` tras el `displayName`.
- Residual 5 del plan (`variables: - group: VG-ECOTUR-DEV`, ya sin uso en la compuerta) y residual 6
  (`AZURE_STORAGE_CONNECTION_STRING=Endpoint=sb://...` con formato de Service Bus): no tocados, fuera de alcance.

# Handoff — BE-34 · Fase C (`SuperadminBootstrapSettings` y su bloque en `.env.example`)

- Commit de la fase: `f83a511` — `feat(config): read the first superadmin credentials in a class of their own` (mensaje
  exacto del plan, trailer `Co-Authored-By` incluido; `diff` contra las l. 483-501 de `plan.md` sin la sangría →
  `IDENTICAL`).
- Rama: `item/be-34`, sobre `846efe0` (plan aprobado entero: E0, E1, E2, E3).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: ninguna cambia la fase C (E0, E2 punto 1 y E3: "las fases A → E quedan aprobadas tal como están
  escritas").

## Ritual de arranque

- `git status --short`: limpio. HEAD `846efe0`. `current_target` = `Fase_C`. `gaps.md`: A y B PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila B del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`.

## Archivos tocados (los tres de la fase)

`git show --stat --format= f83a511`:

```
 .env.example         | 11 +++++++++
 app/core/config.py   | 25 +++++++++++++++++-
 tests/test_config.py | 93 ++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 128 insertions(+), 1 deletion(-)
```

`git show --numstat --format= f83a511` (criterio de aceptación: `11 0`, `24 1`, `93 0`):

```
11	0	.env.example
24	1	app/core/config.py
93	0	tests/test_config.py
```

Cómo se escribió (aviso del auditor de A sobre el hook F401): cada archivo se editó en una sola escritura con un script
de Python que sustituye anclas únicas (`assert s.count(old) == 1`), así cada import nuevo (`SecretStr`,
`SuperadminBootstrapSettings`, `UserCreateByAdmin, UserRole`) entró en la misma escritura que su primer uso. Los tres
archivos quedan en UTF-8 con LF (`grep -c $'\r'` → 0 en los tres).

## TDD

1. Tests primero (`tests/test_config.py`, texto dictado) →
   `./venv/Scripts/python.exe -m pytest tests/test_config.py -q -p no:cacheprovider -rf`:
   `ImportError: cannot import name 'SuperadminBootstrapSettings' from 'app.core.config'` ·
   `1 error during collection` (= plan).
2. Con `config.py` hecho y `.env.example` sin tocar: `2 failed, 33 passed`
   (`test_env_example_documents_every_bootstrap_variable`, `test_env_example_password_is_not_a_usable_credential`) (= plan).
3. Con `.env.example`: `35 passed` (= plan).

`./venv/Scripts/python.exe -c "from app.core.config import Settings as S, SuperadminBootstrapSettings as B; print(len(S.model_fields), len(B.model_fields))"`
→ `15 6` (= plan).

## Compuerta al cerrar (exit 0)

Archivos tocados: `ruff check app/core/config.py tests/test_config.py` → `All checks passed!`;
`ruff format --check` → `2 files already formatted`; `mypy app/core/config.py tests/test_config.py` →
`Success: no issues found in 2 source files`.

`./venv/Scripts/python.exe scripts/check.py` → exit 0:

```
61 files already formatted
All checks passed!
Success: no issues found in 56 source files
Contracts: 4 kept, 0 broken.
TOTAL                                        966     18    136     15  97.01%
650 passed, 8 warnings in 17.69s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Igual a la fila C del plan (650 passed · 97,01 % (966) · 61 files · 56 source files). Ratchet frente a B: +11 tests,
cobertura 96,82 % → 97,01 %, 4 kept, 0 errores de ruff y mypy.

## Mutantes (procedimiento común: copia nueva de `git archive HEAD` sobre `f83a511`, un directorio por mutante)

Comando en cada copia: `C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

- Copia limpia: `361 passed, 8 warnings` (= columna "Suite de la copia" de la fila C).
- MC1 (`superadmin_password: SecretStr` → `str`):
  ```
  FAILED tests/test_config.py::test_bootstrap_settings_need_no_web_app_secret
  FAILED tests/test_config.py::test_bootstrap_password_never_shows_in_repr - as...
  FAILED tests/test_config.py::test_env_example_password_is_not_a_usable_credential
  3 failed, 358 passed, 8 warnings in 11.80s
  ```
- MC2 (`(DatabaseSettings)` → `(Settings)`):
  ```
  FAILED tests/test_config.py::test_bootstrap_settings_need_no_web_app_secret
  1 failed, 360 passed, 8 warnings in 12.24s
  ```
- MC3 (`.env.example`, `SUPERADMIN_PASSWORD=DIGITAR_CONTRASEÑA_PRIVADA` → `SUPERADMIN_PASSWORD=Superadmin2026`):
  ```
  FAILED tests/test_config.py::test_env_example_password_is_not_a_usable_credential
  1 failed, 360 passed, 8 warnings in 12.54s
  ```

Los tres = tabla del plan. Directorios: `scratchpad/mut_C_{clean,MC1,MC2,MC3}` (no se borran).

## Fuera de alcance respetado

`git diff --stat 846efe0 f83a511 -- conftest.py tests/conftest.py alembic app/api app/main.py pyproject.toml` → vacío.
`Settings`, `REQUIRED` y `OPTIONAL_DEFAULTS` sin cambios (siguen 15 campos).

## test-sanitizer (checklist)

Tests dictados por el plan, sin reescribir: sin mocks; sin aserciones sobre texto en español (tipos y `loc` de errores,
conjuntos de campos, valores de prueba propios); cada docstring nombra su categoría (1 camino feliz, 2 de fallo con 6+1
casos, 3 de borde); anotados.

## Residuales y dudas

- Ninguno nuevo. Observación sin acción: `test_bootstrap_validation_errors_do_not_echo_values` no lo tumba MC1, porque
  `hide_input_in_errors=True` (heredado de `DatabaseSettings`) ya oculta los valores; el plan no lo cuenta entre los
  que MC1 tumba y la cifra medida coincide.

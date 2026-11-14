# Handoff — BE-34 · Fase E (comando `python -m app.cli.bootstrap_superadmin` y `app.cli` en el contrato de capas)

- Commit de la fase: `2bf29e5` — `feat(cli): add python -m app.cli.bootstrap_superadmin for operators` (mensaje exacto
  del plan, trailer `Co-Authored-By` incluido; `git cat-file commit HEAD` sin cabeceras contra las l. 1217-1240 de
  `plan.md` sin la sangría → `IDENTICAL`).
- Rama: `item/be-34`, sobre `1beb91d` (plan aprobado entero: E0, E1, E2, E3).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: E0.3 (test `test_command_runs_without_the_web_app_secrets` y mutante ME6) y su "Aplicación"
  (cifras de E: 675 tests, 97,37 %, 1031 stmts, 8 tests en el archivo, `numstat` 208). E2 punto 1: "las fases A → E
  quedan aprobadas tal como están escritas". El cuerpo de la fase E en `plan.md` ya incorpora E0.3; no hay diferencia
  entre cuerpo y enmiendas para esta fase.

## Ritual de arranque

- `git status --short`: limpio. HEAD `1beb91d`. `current_target` = `Fase_E`. `gaps.md`: A–D PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila D del plan:
  `64 files already formatted` · `All checks passed!` · `Success: no issues found in 59 source files` ·
  `Contracts: 4 kept, 0 broken.` · `667 passed, 8 warnings` · `TOTAL 988 18 140 15 97.07%`.

## Archivos tocados (los cuatro de la fase)

`git show --stat --format= 2bf29e5` (última línea): `4 files changed, 325 insertions(+), 2 deletions(-)`.

`git show --numstat --format= 2bf29e5` (criterio de aceptación: `1 0`, `114 0`, `2 2`, `208 0`):

```
1	0	app/cli/__init__.py
114	0	app/cli/bootstrap_superadmin.py
2	2	pyproject.toml
208	0	tests/test_bootstrap_superadmin_command.py
```

Cómo se escribió (aviso del hook F401): los dos archivos de Python dictados se extrajeron de `plan.md` por rango de
líneas con un script (l. 866-979 → el módulo, l. 983-1190 → el test), quitando la sangría de 5 espacios y escribiendo
bytes UTF-8 con LF; el hook no corre (no es Edit/Write), así que ningún import se perdió. `app/cli/__init__.py` con
`printf` (una línea). `pyproject.toml` con un script que exige una sola aparición de cada ancla (`assert count == 1`).
`ruff format --check`, `ruff check` y `mypy` se pasaron a mano sobre los tres `.py`. Los cuatro archivos: 0 bytes `\r`.

## TDD

1. Primero `tests/test_bootstrap_superadmin_command.py` →
   `./venv/Scripts/python.exe -m pytest tests/test_bootstrap_superadmin_command.py -q -p no:cacheprovider --tb=line`:
   ```
   E   ModuleNotFoundError: No module named 'app.cli'
   ERROR tests/test_bootstrap_superadmin_command.py
   !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
   1 error in 0.20s
   ```
   (= plan).
2. Con `app/cli/__init__.py`, `app/cli/bootstrap_superadmin.py` y el contrato: `8 passed in 2.22s` (= plan).

## Compuerta al cerrar (exit 0)

Archivos tocados (`app/cli/__init__.py`, `app/cli/bootstrap_superadmin.py`, `tests/test_bootstrap_superadmin_command.py`):
`ruff format --check` → `3 files already formatted`; `ruff check` → `All checks passed!`; `mypy` →
`Success: no issues found in 3 source files`.

`./venv/Scripts/python.exe scripts/check.py` → exit 0:

```
67 files already formatted
All checks passed!
Success: no issues found in 62 source files
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT
Contracts: 4 kept, 0 broken.
TOTAL                                       1031     17    148     14  97.37%
675 passed, 8 warnings in 20.84s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Igual a la fila E del plan (675 passed · 97,37 % (1031) · 67 files · 62 source files · 8 warnings). El módulo no
aparece en el informe porque está entre los `30 files skipped due to complete coverage`; con los datos de esa misma
corrida, `python -m coverage report --include='app/cli/*'` →
`app\cli\bootstrap_superadmin.py      43      0      8      0  100.00%` (y `1 empty file skipped`, el `__init__.py`).
Ratchet frente a D: +8 tests, cobertura 97,07 % → 97,37 %, 4 kept, 0 errores de ruff y mypy.

## Mutantes (procedimiento común: copia nueva de `git archive HEAD` sobre `2bf29e5`, un directorio por mutante)

Comando en cada copia: `C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
Cada edición se aplicó con un script que exige una sola aparición del texto original.

- Copia limpia: `386 passed, 8 warnings in 14.43s` (= columna "Suite de la copia" de la fila E).
- ME1 (borrar las dos líneas `if field not in SuperadminBootstrapSettings.model_fields:` / `field = f"superadmin_{field}"`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_rejects_bad_configuration_naming_only_the_variable[weak-password]
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_rejects_bad_configuration_naming_only_the_variable[short-cedula]
  2 failed, 384 passed, 8 warnings in 14.48s
  ```
- ME2 (el `return 1` tras el `print` de `AlreadyExistsError` → `return 0`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
  1 failed, 385 passed, 8 warnings in 14.41s
  ```
  Nota: el primer intento (`mut_E_ME2`) no aplicó la edición (mi ancla tenía 4 espacios de más; el script falló con
  `AssertionError: ('ME2', 0)` y esa copia corrió sin mutar: `386 passed`). Se corrigió el ancla y se repitió en un
  directorio nuevo, `mut_E_ME2_c` (`git diff --no-index --stat` contra el original: `1 insertion(+), 1 deletion(-)`).
  `mut_E_ME2_b` quedó creado y sin mutar por un fallo de escape del script; no se usó.
- ME3 (`{created.email}")` → `{created.email} {credentials.password}")`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_creates_the_superadmin_without_writing_secrets
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_second_run_exits_zero_and_writes_nothing
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_runs_without_the_web_app_secrets
  3 failed, 383 passed, 8 warnings in 14.70s
  ```
- ME4 (`create_async_engine(database_url)` → `create_async_engine(database_url, echo=True)`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_creates_the_superadmin_without_writing_secrets
  1 failed, 385 passed, 8 warnings in 14.38s
  ```
- ME5 (`    sys.exit(main())` → `    main()`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_runs_as_a_module_and_exits_with_the_code_of_main
  1 failed, 385 passed, 8 warnings in 14.70s
  ```
- ME6 (`import app.core.email  # noqa: F401` antes de `from app.core.exceptions import AlreadyExistsError` en
  `app/services/superadmin_bootstrap.py`):
  ```
  FAILED tests/test_bootstrap_superadmin_command.py::test_command_runs_without_the_web_app_secrets
  1 failed, 385 passed, 8 warnings in 14.53s
  ```
- MK1 (`import app.cli  # noqa: F401` antes del primer `from app.` de `app/services/superadmin_bootstrap.py`), con
  `python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"` en la copia → exit 1:
  ```
  Capas: api | cli -> services -> repositories -> models BROKEN
  Los servicios no conocen el transporte HTTP KEPT
  Los repositorios solo conocen SQLAlchemy y los modelos KEPT
  Los modelos y los schemas no dependen de capas superiores KEPT
  Contracts: 3 kept, 1 broken.
  app.services is not allowed to import app.cli:
  - app.services.superadmin_bootstrap -> app.cli (l.8)
  ```

Los siete = tabla del plan. Directorios (no se borran), en el scratchpad de la sesión:
`mut_E_clean`, `mut_E_ME1`, `mut_E_ME2_c`, `mut_E_ME3`, `mut_E_ME4`, `mut_E_ME5`, `mut_E_ME6`, `mut_E_MK1`.

## Criterio de aceptación

| Criterio | Medido |
|---|---|
| Compuerta como la fila E | exit 0 · 675 passed · 97,37 % (1031) · 67 files · 62 source files · 4 kept · 8 warnings |
| `app\cli\bootstrap_superadmin.py` al 100 % | `43 0 8 0 100.00%` |
| `numstat` `1 0` / `114 0` / `2 2` / `208 0` | idéntico (arriba) |
| `Capas: api \| cli -> services -> repositories -> models KEPT` | sí (salida de la compuerta) |
| ME1–ME6 y MK1 con los resultados de la tabla | sí (2, 1, 3, 1, 1, 1 failed; MK1 `3 kept, 1 broken`) |

Verificación final, pasos 1-8 (pasos que valen tras E), ejecutados:
1. `git grep -n -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts` → sin salida, exit 1.
2. Patrón 2 → las 8 líneas exactas: `.env.example:6` · `app/cli/bootstrap_superadmin.py:19` · `app/core/config.py:12` ·
   `app/repositories/user_repository.py:1` · `app/services/superadmin_bootstrap.py:3` ·
   `tests/test_bootstrap_superadmin_command.py:16` · `tests/test_config.py:41` · `tests/test_superadmin_bootstrap.py:11`
   (109 en total).
3. Patrón 3 → 4 líneas: `app/cli/bootstrap_superadmin.py:90`, `app/services/superadmin_bootstrap.py:60`,
   `app/services/user_service.py:88`, `:412`.
4. Patrón 4 → `dependencies.py:199`, `routers/user.py:35`, `user_access_policy.py:67`, `:72`.
5. `TEST_ENVIRONMENT` → 1 línea, `tests/test_config.py:243`.
6. `git diff --stat 4f10660 -- <lo que no se toca>` → vacío.
7. `git diff --name-only 4f10660 -- app tests pyproject.toml .env.example docs/adr` → exactamente 12 archivos.
8. `15 6`.
9. Compuerta: la de arriba.

## Fuera de alcance respetado

`Dockerfile`, `cd-pipeline.yml`, `app/db/database.py`, el manual técnico (R4) y `AGENTS.md` (R1) sin cambios (paso 6
vacío). Ningún archivo de A–D ni de F–G tocado: el commit solo lista los cuatro de la fase.

## test-sanitizer (checklist)

Tests dictados por el plan, sin reescribir. Sin mocks: base de archivo propia en `tmp_path` y el comando real.
Aserciones sobre código de salida, filas (cédula, rol, `is_active`, hash verificado), conteos de `users` y `audit_logs`,
y salida en stdout/stderr/`caplog` por ausencia de la contraseña y del hash; la única comparación exacta de texto de
salida es `VARIABLE: tipo` (identificadores, no texto en español). Nombres en inglés. Desviación consciente del punto
"fábricas" de AGENTS §5, dictada por el plan: el turista de `test_command_fails_when_the_email_belongs_to_another_account`
se inserta con `insert(User).values(...)`, porque el comando usa su propia base de archivo y `persist_user` escribe en
la base de la sesión del test (no en la del comando). No se cambia.

## Residuales y dudas

- Ninguno nuevo. R8 (E0.6: `IntegrityError` no capturado con los parámetros del `INSERT` si dos operadores corren el
  comando a la vez) sigue declarado, sin arreglo, como dicta el plan.
- Para el auditor: el hook de `ruff` corrió sobre el script de mutantes del scratchpad (fuera del repo) al editarlo con
  Edit; no afecta a ningún archivo del repositorio.

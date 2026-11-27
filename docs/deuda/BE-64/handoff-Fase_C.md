# Handoff — BE-64 · Fase C (variable `VERIFICATION_RESEND_INTERVAL_SECONDS`)

- **Commit de la fase:** `a218a65` — `feat(config): add the minimum wait between two verification links` (mensaje
  exacto del plan, fase C, `plan.md:284-299`, extraído con `sed` sin reescribirlo; `git log -1 --format=%B` coincide
  con él línea a línea).
- **Rama:** `item/be-64`. HEAD al arrancar: `a3c0e90` (árbol limpio). **Base develop:** `b6a80ba` (`git fetch origin`
  correcto; `git rev-parse --short origin/develop` y `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `b6a80ba`, igual a `verificacion.md`).
- **Compuerta:** `./venv/Scripts/python.exe scripts/check.py`, sin `--soft`. Windows no bloqueó `_rustgrimp`: E0,
  punto 3, no aplicó.

## Archivos tocados (4, los del plan)
- `app/core/config.py`: comentario y campo `verification_resend_interval_seconds: int = 60` tras
  `verification_token_expire_minutes`.
- `.env.example`: comentario y `VERIFICATION_RESEND_INTERVAL_SECONDS=60` tras `VERIFICATION_TOKEN_EXPIRE_MINUTES=15`.
- `conftest.py` (raíz): `"VERIFICATION_RESEND_INTERVAL_SECONDS": "60"` en `TEST_ENVIRONMENT`.
- `tests/test_config.py`: la entrada en `OPTIONAL_DEFAULTS`, el cuarto valor de
  `test_env_example_is_a_valid_configuration` y dos tests nuevos
  (`test_verification_resend_interval_is_read_in_seconds`, `test_verification_resend_interval_rejects_a_non_integer`).

Igualdad con el Anexo C, comprobada por hash de blob: los cuatro blobs del commit (`git rev-parse HEAD:<archivo>`) son
`4000dc2` (`.env.example`), `35cd82a` (`config.py`), `7a65482` (`conftest.py`) y `de1c8ab` (`test_config.py`), los de
las líneas `index` del Anexo C; y `git diff -U2` sin las líneas `index`, comparado con `diff` contra el Anexo, sale
idéntico. El hook de formato no cambió nada (`ruff format --check` sobre los tres `.py`: `3 files already formatted`).

## Diff (`git show --stat a218a65`)
```
 .env.example         |  2 ++
 app/core/config.py   |  2 ++
 conftest.py          |  1 +
 tests/test_config.py | 29 ++++++++++++++++++++++++++++-
 4 files changed, 33 insertions(+), 1 deletion(-)
```

## Compuerta de arranque (antes de tocar nada)
Exit 0. `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Contracts: 4 kept, 0 broken.` · `808 passed, 25 warnings in 31.20s` · `TOTAL 1072 10 156 6 98.70%` ·
`Compuerta superada.` Igual al estado de salida de la fase B.

## RED (`tests/test_config.py` y `conftest.py` raíz, sin `app/` ni `.env.example`)
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`, literal (líneas `E`, `FAILED` y conteo):
```
E       AssertionError: assert {'access_toke...origins', ...} == {'access_toke...origins', ...}
E         Extra items in the right set:
E         'verification_resend_interval_seconds'
E                   AttributeError: 'Settings' object has no attribute 'verification_resend_interval_seconds'
E       Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
E                   AttributeError: 'Settings' object has no attribute 'verification_resend_interval_seconds'
FAILED tests/test_config.py::test_optional_variables_keep_their_current_defaults
FAILED tests/test_config.py::test_verification_resend_interval_is_read_in_seconds
FAILED tests/test_config.py::test_verification_resend_interval_rejects_a_non_integer
FAILED tests/test_config.py::test_env_example_is_a_valid_configuration - Attr...
4 failed, 806 passed, 25 warnings in 32.31s
```
Es el esperado del plan: `4 failed, 806 passed`, con las cuatro causas de la tabla "Qué se midió".

## Compuerta de salida (literal)
Exit 0. Líneas por paso:
```
73 files already formatted
--- ruff format --check: OK en 0.1s
All checks passed!
--- ruff check: OK en 0.1s
Success: no issues found in 68 source files
--- mypy: OK en 0.9s
Analyzed 56 files, 148 dependencies.
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
--- docs (coherencia): OK en 0.1s
TOTAL                                       1073     10    156      6  98.70%
810 passed, 25 warnings in 32.21s
--- pytest + cobertura: OK en 35.2s
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
- pytest: `810 passed, 25 warnings` (0 failed). Plan: `810 passed`. ✔
- Cobertura: `98.70%` (línea base 98,70 %; no baja). ✔
- mypy: 0 errores en 68 archivos. ✔
- ruff: 0 errores; `73 files` formateados (los cuatro archivos ya existían). ✔
- import-linter: `4 kept, 0 broken` (línea base 4). ✔

## Ruff y mypy sobre los archivos tocados
- `python -m ruff check app/core/config.py conftest.py tests/test_config.py` → `All checks passed!`.
- `python -m ruff format --check <los tres>` → `3 files already formatted`.
- `python -m mypy <los tres>` → `Success: no issues found in 3 source files`.
- `.env.example` no es Python: fuera de ruff y mypy; lo cubren `test_env_example_documents_every_setting` y
  `test_env_example_is_a_valid_configuration`.

## Mutantes MC1–MC4 (cada uno en su copia, suite completa)
Copias `git archive HEAD` (HEAD `a3c0e90`) + los cuatro archivos de la fase, en `be64C1-MC1` … `be64C1-MC4` del
scratchpad; intérprete del venv por ruta, cwd = la copia; `import app; app.__file__` →
`…\scratchpad\be64C1-MCn\app\__init__.py` en las cuatro. Mutante aplicado por reemplazo exacto (ancla única). Las copias
no tienen `.env`.

| # | Mutante | Resultado literal | Lo mata |
|---|---|---|---|
| MC1 | `verification_resend_interval_seconds: int = 30` | `1 failed, 809 passed` | `test_optional_variables_keep_their_current_defaults` |
| MC2 | `.env.example` con `=61` | `1 failed, 809 passed` | `test_env_example_is_a_valid_configuration` |
| MC3 | `.env.example` sin la línea `VERIFICATION_RESEND_INTERVAL_SECONDS=60` | `1 failed, 809 passed` | `test_env_example_documents_every_setting` |
| MC4 | `conftest.py` raíz sin la entrada | `1 failed, 809 passed` | `test_test_environment_fixes_every_setting` |

4 muertos, 0 vivos; coinciden con la tabla del Análisis del plan.

## Skill `test-sanitizer` (solo checklist, "Ecotur Enterprise Test Standards")
Sobre los cambios de `tests/test_config.py`: (1) sin mocks, no aplica; (2) el entorno se prepara con los helpers ya
existentes del módulo (`_set_required`, `_clear`) y `monkeypatch`, sin duplicar preparación; (3) nombres, docstrings y
variables en inglés; (4) la aserción del error compara `(type, loc)` de pydantic, sin texto humano; (5) sin ABAC, no
aplica. Ninguna aserción sobre texto en español. No se reescribió nada.

## Incidencias y desviaciones
- Ninguna desviación del plan. No se tocó `plan.md`, `verificacion.md` ni ningún archivo fuera de los cuatro de la fase.
- No leí `.env`. La suite no lo lee (el `conftest.py` raíz fija todas las variables), y
  `test_env_example_is_a_valid_configuration` carga `.env.example`.
- `rm -rf` está denegado por permisos: las copias de mutantes quedan en carpetas nuevas del scratchpad (`be64C1-…`).

## Residuales
Ninguno nuevo. Sigue vigente R5 del plan: la variable acepta 0 o negativos (validar rango no lo pide la adenda).

## Siguiente paso
- `/auditar BE-64 C`.
- El requisito previo de la fase D (E1, punto 3, momento 2: cuatro comandos de `alembic` y dos consultas) ya está en
  `docs/bitacora/2026-11-27.md` ("BE-64: momento 2 de E1 … (10:37–10:38)", commit `a3c0e90`); no lo corrí yo.
- Después, `/implementar BE-64 D`.

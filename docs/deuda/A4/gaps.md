# Gaps — A4

## Auditoría Fase A — 2026-11-10
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`):

- Árbol: `git status --short` limpio. `git diff --name-only db2be61 HEAD` → `docs/deuda/A4/handoff-Fase_A.md`,
  `docs/deuda/A4/progress.json`, `tests/test_token_failure_paths.py`. `git show --stat 21ee9fc` → solo
  `tests/test_token_failure_paths.py` (69+, 1-), el único archivo de la fase.
- Commit `21ee9fc`: asunto idéntico al del plan (`test(auth): pin JWT signature checks on both decode paths (A4)`);
  el cuerpo trae el porqué (CONTEXT 8.1), qué fija cada test, M1/M2 con conteos y el límite del tercer test.
- Diff contra "Cambios exactos": imports `Path`, `dotenv_values`, `AsyncSession`, `create_verification_token`;
  `VERIFY_ROUTE`, `FOREIGN_KEY`, `ENV_EXAMPLE` tras `PROTECTED_ROUTE`; `_resign` y `_env_example_jwt_key` literales,
  junto a `_bearer`; los tres tests con nombre, firma, docstring y aserciones del plan (401 vía `_assert_bearer_401`;
  400 + `set(body) == {"detail"}` + `detail` str + `refresh` + `is_active is False`). Ni `make_token`, ni otros
  tests, ni `app/` tocados.
- `progress.json`: `Fase_A` `completed` con `21ee9fc` (hash real), `current_target` = `Fase_B`, `last_handoff`
  presente, `edit_rules` intacto, JSON válido.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): `57 files already formatted` ·
  `Found 8 errors.` (los 8 I001 heredados de `app/`) · `Found 9 errors in 5 files (checked 53 source files)` ·
  `Contracts: 4 kept, 0 broken.` · `552 passed, 5 warnings` · `TOTAL … 96.11%`. Fila A de la tabla exacta;
  cobertura = línea base (96.11 %).
- Archivo tocado: `ruff check` → `All checks passed!`; `ruff format --check` → `1 file already formatted`;
  `mypy tests/test_token_failure_paths.py` → 5 errores, todos en `app/` (heredados), 0 en el test.
- Mutantes re-medidos en copias `git archive 21ee9fc` del scratchpad, sin `.env`, con el env del plan
  (`-k signed_with`): sin mutante `3 passed, 14 deselected`; M1 (`app/api/dependencies.py:95`) `2 failed, 1 passed`
  (fallan los dos de token de acceso); M2 (`app/services/user_service.py:124`) `1 failed, 2 passed` (falla el de
  verificación). Coinciden con el plan y con el handoff.
- Verificación final #9 (estado tras A): 3 líneas, `tests/test_token_failure_paths.py:57`, `:189`, `:202`.
- AGENTS §5: usuarios y tokens por fábricas (`persist_user`, `make_token`), sin mocks nuevos, refresh tras la
  petición (ADR-0011), ninguna aserción sobre texto en español.

## Auditoría Fase B — 2026-11-10
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`):

- Árbol: `git status --short` limpio al empezar. `git diff --name-status 7f46c5e HEAD` → `A app/core/config.py`,
  `A conftest.py`, `A tests/test_config.py`, `A docs/deuda/A4/handoff-Fase_B.md`, `M docs/deuda/A4/progress.json`.
  `git show --stat 43d28f5` → solo los 3 archivos de la fase (325+).
- Commit `43d28f5`: asunto idéntico al del plan (`feat(config): add validated Settings and a .env-free test env (A4)`);
  el cuerpo trae el porqué (15 lecturas sin validar, `.env` por efecto lateral, suite atada a `.env`), un bullet por
  archivo, las sondas (a)–(d), `DatabaseSettings` por el CD (P1, ADR-0013), consumidores en C–G y el trailer.
- `progress.json`: JSON válido; `Fase_B` `completed` con `43d28f5` (hash real); `current_target` = `Fase_C`;
  `last_handoff` presente; `edit_rules` intacto (el diff `7f46c5e..HEAD` solo cambia status, commit, target y handoff).
- Diff contra "Cambios exactos": `conftest.py` idéntico al bloque del plan (`diff` vacío). `app/core/config.py` igual
  palabra por palabra (`diff` por palabras vacío); solo cambia el corte de línea de 3 líneas de docstring que, sin la
  sangría del plan, miden 102, 105 y 101 columnas (`line-length = 100`, `E` seleccionado). Desviación 1 aceptable: la
  exige la regla "archivos tocados con 0 errores". P3 presente (`config.py:34`, `hide_input_in_errors=True`);
  `extra="ignore"` (`:33`); `ENV_FILE` por la ruta del módulo (`:17`).
- `tests/test_config.py`: 21 casos (5+5+1+1+1+1+1+1+2+1+1+1) con los nombres y aserciones del plan; entorno solo por
  `monkeypatch.setenv/delenv` (`git grep "os\.environ|getenv" -- tests/test_config.py` → 0). Desviación 2 (caso 8,
  `:171`, `{e["loc"]} == {(name,) for name in others}`) aceptable: endurece la aserción dictada sin quitarla
  (AGENTS §5). Desviación 3 (caso 9, `:175`, `Callable[[], DatabaseSettings]`) aceptable: el plan no dicta la anotación,
  es correcta para ambos getters (mypy limpio) y mantiene la Verificación final #4 en 3 líneas, todas en
  `app/core/config.py` (`:13`, `:20`, `:30`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): `60 files already formatted` ·
  `Found 8 errors.` (los 8 I001 heredados: `dependencies.py`, `routers/audit.py`, `email.py`, `database.py`,
  `user_repository.py`, `schemas/audit.py`, `audit_service.py`, `user_service.py`) ·
  `Found 9 errors in 5 files (checked 55 source files)` (los 9 `[arg-type]` heredados) · `Contracts: 4 kept, 0 broken.` ·
  `573 passed, 5 warnings` · `TOTAL … 96.23%`. Fila B exacta; cobertura ≥ 96.11 %.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already formatted`;
  `mypy app/core/config.py tests/test_config.py conftest.py` → `Success: no issues found in 3 source files`.
- Mutantes re-medidos en copias `git archive 43d28f5` del scratchpad, sin `.env`, sin las 5 obligatorias: sin mutante
  (`-k "echo_values or unknown_keys"`) `2 passed, 19 deselected`; M9 (línea `hide_input_in_errors=True,` borrada)
  `-k echo_values` → `1 failed, 20 deselected`; M10 (`:33` `extra="forbid",`) `-k unknown_keys` →
  `1 failed, 20 deselected`. Coinciden con el plan y el handoff.
- Suite sin `.env` (criterio de B), copia `git archive 43d28f5`, `test ! -e .env`, `env -u` de las 5 obligatorias:
  `573 passed, 5 warnings`. P5 (orden de carga): en esa copia, `pytest tests/test_auth.py` → `19 passed`; desde
  `tests/`, `pytest test_auth.py test_config.py` → `40 passed`; con el `conftest.py` raíz borrado →
  `ArgumentError: Expected string or URL object, got None` (el mismo error de colección de `55345a1`).
- P3 con sonda propia (`env -i`, sin `JWT_SECRET_KEY`, `Settings(_env_file=None)`): `ValidationError`; el texto
  contiene `jwt_secret_key` y `Field required`, y no contiene `a@test.com` ni `UseDevelopmentStorage`.
- Verificación final, estado tras B: #2 → 1 línea (`conftest.py:28`); #4 → 3 líneas en `config.py`; #9 → las 3 líneas
  de la fase A (`tests/test_token_failure_paths.py:57`, `:189`, `:202`).
- AGENTS: sin mocks; sin usuarios ni tokens a mano; inglés; docstrings Google en lo público; aserciones sobre
  `type`/`loc` de pydantic, valores e identidad, ninguna sobre texto en español. Ninguna excepción de dominio nueva.

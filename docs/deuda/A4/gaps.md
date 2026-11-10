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

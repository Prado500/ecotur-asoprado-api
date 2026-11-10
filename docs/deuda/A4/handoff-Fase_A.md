# Handoff — A4 · Fase A (tests de firma JWT en las dos rutas de `jwt.decode`)

- Commit de la fase: `21ee9fc` — `test(auth): pin JWT signature checks on both decode paths (A4)`
- Rama: `item/a4`, sobre `db2be61` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_A`. Sin `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), idéntica a la línea base de la verificación:
  `57 files already formatted` · ruff `Found 8 errors.` · mypy `Found 9 errors in 5 files (checked 53 source files)` ·
  `Contracts: 4 kept, 0 broken.` · `549 passed, 5 warnings` · `TOTAL … 96.11%`.

## Archivos tocados

- `tests/test_token_failure_paths.py` (único archivo de la fase).

`git show --stat 21ee9fc`:

```
 tests/test_token_failure_paths.py | 70 ++++++++++++++++++++++++++++++++++++++-
 1 file changed, 69 insertions(+), 1 deletion(-)
```

Resumen del diff, todo dictado por el plan: imports `Path`, `dotenv_values`, `AsyncSession` y
`create_verification_token`; constantes `VERIFY_ROUTE`, `FOREIGN_KEY`, `ENV_EXAMPLE` tras `PROTECTED_ROUTE`; helpers
`_resign` y `_env_example_jwt_key` junto a `_bearer` (código literal del plan); tres tests nuevos tras
`test_token_for_soft_deleted_active_user_returns_401` (al final de los casos HTTP, antes de las llamadas directas):

1. `test_access_token_signed_with_another_key_returns_401`
2. `test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive`
3. `test_access_token_signed_with_the_env_example_key_returns_401`

Docstrings literales del plan. Ningún otro test del archivo, ni `make_token`, ni `app/` tocados.

## Tests (caracterización; su RED es el mutante)

Sin mutante, en el árbol: `3 passed, 14 deselected` (`-k signed_with`). El tercer test pasa en local: la clave JWT del
entorno local no es la de `.env.example` (no se leyó `.env`; se dedujo del resultado del test).

## Mutantes (copia `git archive HEAD` de `21ee9fc` en el scratchpad, una por mutante, sin `.env`; env del plan)

Salida literal:

```
=== none ===
3 passed, 14 deselected in 0.08s
=== M1 ===
95:        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False, "verify_exp": True})
FAILED tests/test_token_failure_paths.py::test_access_token_signed_with_another_key_returns_401
FAILED tests/test_token_failure_paths.py::test_access_token_signed_with_the_env_example_key_returns_401
2 failed, 1 passed, 14 deselected in 0.37s
=== M2 ===
124:            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False, "verify_exp": True})
FAILED tests/test_token_failure_paths.py::test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive
1 failed, 2 passed, 14 deselected in 0.33s
```

Esperado por el plan: M1 `2 failed, 1 passed`; M2 `1 failed, 2 passed`; sin mutante `3 passed`. Coincide.
Antes del commit se hizo la misma medición sobre `git archive db2be61` con el archivo de test superpuesto, con
resultados idénticos, para que el cuerpo del commit llevara conteos medidos.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

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

Conteos literales:

```
57 files already formatted
Found 8 errors.
Found 9 errors in 5 files (checked 53 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
552 passed, 5 warnings in 18.78s
```

Fila A de la tabla del plan: ruff 8 · mypy 9 (53 archivos) · 552 passed · format 57 · mismo resumen. **Exacta.**
Cobertura 96.11 % = línea base.

Archivo tocado: `ruff check tests/test_token_failure_paths.py` → `All checks passed!`; `ruff format --check` →
`1 file already formatted`; `mypy tests/test_token_failure_paths.py` → 0 errores en el archivo (los 5 que informa son
de `app/` importado, parte de los 9 heredados de la línea base).

Verificación final #9 del plan, estado tras A (3 líneas, las que el plan cuenta):

```
tests/test_token_failure_paths.py:57:    claims = jwt.decode(token, options={"verify_signature": False})
tests/test_token_failure_paths.py:189:async def test_access_token_signed_with_another_key_returns_401(
tests/test_token_failure_paths.py:202:async def test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive(
```

## test-sanitizer (checklist)

Sin mocks nuevos; usuarios y tokens por fábricas (`persist_user`, `make_token`); nombres en inglés; aserciones sobre
código HTTP, cabecera `WWW-Authenticate`, estructura `{"detail"}` y tipo, y mutación de estado (`is_active` tras
`refresh`, ADR-0011); ninguna sobre texto en español. Sin cambios a pruebas existentes.

## Residuales y dudas

- Ninguno nuevo. Los 8 ruff (I001) y 9 mypy son la deuda heredada que A4 salda en D, E e I.
- El hook de edición quitó por F401 los imports añadidos antes de que tuvieran uso; se volvieron a poner tras escribir
  los tests. Sin efecto en el resultado.

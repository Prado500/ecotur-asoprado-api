# Handoff — A4 · Fase C (los tests dejan de importar las constantes JWT)

- Commit de la fase: `cbf439c` — `test(auth): drop JWT constant imports; sign tokens with make_token (A4)`
- Rama: `item/a4`, sobre `41a457a` (auditoría PASS de la fase B).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_C`. `gaps.md`: fases A y B en PASS, nada para C.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila B: `60 files already formatted` · ruff `Found 8 errors.` ·
  mypy `Found 9 errors in 5 files (checked 55 source files)` (4 de ellos en `tests/test_user_service.py:105,203,280,298`) ·
  `Contracts: 4 kept, 0 broken.` · `573 passed, 5 warnings` · `TOTAL … 96.23%`.

## Archivos tocados

- `tests/conftest.py`, `tests/test_user_service.py`, `tests/test_auth.py`. Ningún otro; nada en `app/`.

`git show --stat cbf439c`:

```
 tests/conftest.py          | 16 ++++++++++++----
 tests/test_auth.py         |  9 +++++----
 tests/test_user_service.py | 43 +++++++++++++++++++++----------------------
 3 files changed, 38 insertions(+), 30 deletions(-)
```

Resumen del diff:

- `tests/conftest.py`: `from typing import Any`. `make_token` gana `extra_claims: dict[str, Any] | None = None`
  (keyword-only), que se mezcla con `update` sobre `{"sub": user.email, "role": user.role.value}`; el docstring lo
  documenta. `expires_delta` sin cambios.
- `tests/test_user_service.py`: el import de `app.core.security` queda en `create_verification_token, get_password_hash`;
  se añade `from app.core.config import get_settings`; `from datetime import UTC, datetime, timedelta` pasa a
  `from datetime import timedelta`. Los dos `jwt.decode` (registro y login) hacen `settings = get_settings()` y decodifican
  con `settings.jwt_secret_key` / `[settings.algorithm]`. Los dos `jwt.encode` a mano pasan a
  `make_token(make_user(email="turista@example.com"), expires_delta=timedelta(minutes=-1), extra_claims={"scope": "email_verification"})`
  y `make_token(make_user(email="turista@example.com"), extra_claims={"scope": "access"})`; sus tests reciben
  `make_user, make_token`.
- `tests/test_auth.py`: el import de `app.core.security` pierde `ALGORITHM, SECRET_KEY`; se añade
  `from app.core.config import get_settings`; el `decode` del login usa `settings = get_settings()`;
  `assert SECRET_KEY is not None` desaparece.

## Tests (RED primero)

RED de herramienta, antes de tocar nada (compuerta de arranque, literal):

```
tests\test_user_service.py:105: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | ... | str | bytes"  [arg-type]
tests\test_user_service.py:203: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | ... | str | bytes"  [arg-type]
tests\test_user_service.py:280: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | ... | str | bytes"  [arg-type]
tests\test_user_service.py:298: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | ... | str | bytes"  [arg-type]
Found 9 errors in 5 files (checked 55 source files)
```

(Tipos de clave abreviados con `...` aquí; la salida completa está en la compuerta de la fase B.) Después: 0 errores en
`tests/` (`mypy tests/conftest.py tests/test_user_service.py tests/test_auth.py | grep -c "^tests"` → `0`); los 5 que
quedan son de `app/`, de las fases D y E. GREEN de los dos archivos de tests: `38 passed in 4.42s`.

## Mutantes (copia `git archive HEAD` de `cbf439c` en el scratchpad, una por mutante, sin `.env`)

Salida literal (línea mutada con `grep -n`, después `pytest -q -p no:cacheprovider tests/test_user_service.py -k …`):

```
== Sin mutante
no .env
124:            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
137:        if email is None or scope != "email_verification":
2 passed, 17 deselected in 0.08s
== M3
no .env
124:            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
1 failed, 18 deselected in 0.32s
== M4
no .env
137:        if email is None:
1 failed, 18 deselected in 0.29s
```

Esperado por el plan: M3 `-k expired_token` → `1 failed`; M4 `-k wrong_scope` → `1 failed`. Coincide.

## Criterio de aceptación

- `git grep -n -E "\bSECRET_KEY\b|import .*\bALGORITHM\b|ALGORITHM,$" -- tests` → sin salida (exit 1). Esperado 0. Coincide.
- Fila C de la tabla: ruff 8 · `Found 5 errors in 4 files (checked 55 source files)` · 573 passed · 60 formatted ·
  4 kept · mismo resumen. Coincide (abajo).

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Extractos literales:

```
60 files already formatted
Found 8 errors.
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; ...  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; ...  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; ...  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; ...  [arg-type]
Found 5 errors in 4 files (checked 55 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        975     23    138     19  96.23%
Required test coverage of 92.0% reached. Total coverage: 96.23%
573 passed, 5 warnings in 17.22s
```

Bloque RESUMEN, literal:

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

| | ruff check | mypy | pytest | cobertura | format | contratos |
|---|---|---|---|---|---|---|
| Esperado (fila C) | 8 | 5 en 4 (55) | 573 | ≥ 96.23 % (B) y ≥ 96.11 % (base) | 60 | 4 kept |
| Real | 8 | 5 en 4 (55) | 573 passed | 96.23 % | 60 | 4 kept |

`ruff check` y `ruff format --check` sobre los tres archivos tocados: `All checks passed!` / `3 files already formatted`.
Los 8 I001 son los heredados de la línea base (ninguno en archivos de esta fase).

## Residuales y dudas

- Ninguno nuevo. Los 5 errores de mypy y los 8 de ruff son los que el plan asigna a D, E e I.
- Nota menor: el token de "scope equivocado" lleva ahora también el claim `role` (lo pone `make_token`) y caduca a los
  30 minutos por defecto en vez de 5; ninguna de las dos cosas afecta a lo que prueba (el `scope`), y M4 lo confirma.
- Checklist `test-sanitizer`: sin mocks nuevos; fábricas de `conftest.py` en lugar de tokens a mano; ninguna aserción
  sobre texto en español. No se reescribió ningún otro test.

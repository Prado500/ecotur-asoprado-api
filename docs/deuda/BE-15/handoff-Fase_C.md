# Handoff — BE-15 Fase C: `test_auth.py` (registro, login, auto-borrado) y un único `mock_send_email`

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `bf22982`
  (`test(auth): assert codes, not Spanish text, in registration and login`; cuerpo idéntico al bloque del plan,
  comprobado con `diff` sobre `git log -1 --format=%B` sin el trailer)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` vacío; HEAD `818027a`; `current_target` = `Fase_C`.

## Archivos tocados

Solo los cuatro que el plan asigna a la fase C (`git show --stat bf22982`):

```
 tests/conftest.py               |  15 ++-
 tests/test_auth.py              | 221 ++++++++++++++++++++--------------------
 tests/test_fixtures_contract.py |  13 +++
 tests/test_user_response.py     |   9 +-
 4 files changed, 136 insertions(+), 122 deletions(-)
```

- `tests/conftest.py` (D2): fixture `mock_send_email` con `@pytest.fixture(autouse=True)` en la línea anterior a
  `def mock_send_email():` (l.115-116), `patch("app.api.routers.user.send_verification_email", autospec=True)`,
  docstring en inglés. Import: `from unittest.mock import create_autospec, patch`.
- `tests/test_user_response.py`: borrado el fixture local; el import queda `from unittest.mock import ANY`.
- `tests/test_auth.py`, solo l.1-175 de `818027a` (todos los hunks de `git diff -U0` empiezan en las l.1-172 del
  original; la sección RBAC, desde el banner de l.177, no cambia): fuera el fixture local y `patch`; `from
  sqlalchemy.future import select` → `from sqlalchemy import func, select`; imports `jwt`, `ANY`, `ALGORITHM` y
  `SECRET_KEY`; constante `PASSWORD = USER_PAYLOAD["password"]`; `pytest` deja de importarse (ya no se usa en el
  archivo). Los 8 tests reescritos:

| Antes | Después |
|---|---|
| `test_registro_usuario_exitoso` | `test_register_tourist_returns_201_and_schedules_verification_email` |
| `test_registro_usuario_duplicado` | `test_register_duplicate_returns_400_without_second_row` |
| `test_verificacion_email_exitosa` | `test_verify_email_endpoint_activates_account` |
| `test_verificacion_email_token_invalido` | `test_verify_email_invalid_token_returns_400` |
| `test_login_exitoso` | `test_login_active_user_returns_bearer_token` |
| `test_login_usuario_inactivo` | `test_login_inactive_user_returns_403_without_token` |
| `test_login_credenciales_invalidas` | `test_login_wrong_password_returns_401_with_bearer_challenge` (D3) |
| `test_borrado_logico_usuario` | `test_self_soft_delete_keeps_row_and_blocks_login` |

- `tests/test_fixtures_contract.py`: +1 test, `test_email_dispatch_double_is_autouse_and_autospecced`.

Aserciones según la tabla del plan. Registro: las de l.36-43, `mock_send_email.assert_called_once_with(email_to=
USER_PAYLOAD["email"], first_name="Juan", token=ANY, base_url=ANY)` y la fila por cédula (`is_active is False`,
`role == UserRole.tourist`). Duplicado: 400, `set(body) == {"detail"}`, `detail` str, `count(User) == 1` y correo
una sola vez con los mismos argumentos. Verificación: `persist_user(is_active=False)` +
`create_verification_token(user.email)`, 200, `{"success", "message"}`, `refresh` → activo. Token inválido: 400 y
forma. Login: `{"access_token", "token_type"}`, `bearer`, `jwt.decode` con `sub == user.email` y `role ==
"tourist"`. Inactivo: 403 y forma. Contraseña incorrecta (cuenta activa con hash real, `"wrongPassword1"`): 401,
`www-authenticate == "Bearer"`, `{"detail"}`. Auto-borrado con `make_auth_headers(user)`: 200, `{"success",
"message"}`, `message` str; `refresh` → `deleted_at` no nulo e inactivo; el login posterior da 401.

## RED → GREEN

Test nuevo escrito con el `conftest.py` de `818027a`:
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_fixtures_contract.py`

```
E       fixture 'mock_send_email' not found
...
ERROR tests/test_fixtures_contract.py::test_email_dispatch_double_is_autouse_and_autospecced
4 passed, 1 error in 0.09s
```

Tras el fixture en `conftest.py` y el borrado de la copia de `test_user_response.py`:
`tests/test_fixtures_contract.py tests/test_user_response.py` → `19 passed, 2 warnings in 0.54s`. Los 8 tests de
`test_auth.py` no tienen RED (refactor y endurecimiento): `tests/test_auth.py` → `19 passed in 3.33s`;
`--collect-only` → `19 tests collected`.

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

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

| Medida | Línea base (antes de tocar, HEAD `818027a`) | Tras la fase C | Fila "Fase C" del plan |
|---|---|---|---|
| pytest | `380 passed, 5 warnings` | `381 passed, 5 warnings in 11.91s` | 381 |
| Cobertura | `TOTAL 942 34 136 22 94.81%` | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % |
| import-linter | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT |
| ruff total | `Found 59 errors.` | `Found 56 errors.` | 56 |
| ruff en `tests/` | `Found 6 errors.` | `Found 3 errors.` | 3 |
| mypy | `Found 10 errors in 5 files (checked 35 source files)` | igual | 10 |
| ruff format | OK | `53 files already formatted` | OK |

Criterios propios de la fase:

- `ruff check` de los cuatro archivos → `All checks passed!`; `ruff format --check` → `4 files already formatted`.
- `grep -rnE "def mock_send_email\(" tests/ --include=*.py` → `tests/conftest.py:116:def mock_send_email():` (1).
- `grep -B1 -E "^def mock_send_email\(" tests/conftest.py | grep -c "@pytest.fixture(autouse=True)"` → 1.
- `test_auth.py` l.1-175: `\["(detail|message)"\] ==|\.lower\(\)` → 0. En el archivo: `sqlalchemy.future` → 0;
  `def test_login_wrong_password_returns_401_with_bearer_challenge(` → 1; `noexiste@example.com` → 0.
- `tests/test_fixtures_contract.py`: 5 tests (A 4 + C 1). `patch(` sin autospec en `tests/` → 0; `MagicMock(` y
  afines → 0.
- Los 3 errores de ruff que quedan en `tests/`: `test_user_access_policy.py:347` y `:395` (fase E) y
  `test_user_service.py:3` (residual del plan).
- Finales de línea: `git ls-files --eol` de los cuatro → `i/lf w/lf`.

## Residuales

- `mypy` sobre los cuatro archivos tocados (la compuerta solo mide `app/`): queda 1 error, heredado y fuera del
  diff, `tests/conftest.py:223` (`Returning Any from function declared to return "User"`, `persist_user`; es la
  antigua l.210, el OPCIONAL de la fase A). Antes de la fase esos cuatro archivos daban 2 (`conftest.py:210` y
  `test_auth.py:67`, `create_verification_token(USER_PAYLOAD["email"])` con tipo `object`); el segundo desaparece.
- Las dos aserciones en español que siguen en `test_auth.py` (l.558 y l.602, `.lower()` sobre `detail`) están en la
  sección RBAC: fase D.

## Desviaciones y dudas

Tres añadidos menores, todos para que los archivos tocados no sumen errores de mypy nuevos (ADR-0005). Ninguno
cambia lo que afirma un test:

1. `USER_PAYLOAD: dict[str, Any]` en `test_auth.py`. Sin la anotación, mypy infiere `dict[str, object]` y
   `get_password_hash(PASSWORD)` daba 4 errores `arg-type`. Se mantiene literal `PASSWORD = USER_PAYLOAD["password"]`.
2. `assert SECRET_KEY is not None` antes de `jwt.decode` en `test_login_active_user_returns_bearer_token`.
   `SECRET_KEY` es `str | None` en `app/core/security.py:7`, el mismo origen que los `arg-type` heredados de `app/`.
   Deja explícita la precondición de que el entorno de pruebas define la clave.
3. `mock_send_email: MagicMock` en la firma del test de contrato (`from unittest.mock import MagicMock`, solo como
   tipo; no hay ningún `MagicMock(`). Sin anotación, mypy estrecha el fixture al tipo de `send_verification_email`
   tras el `is` y da `call-arg` y `attr-defined`. El import del router va a nivel de módulo (`from app.api.routers
   import user as user_router`), no dentro del test como lo escribe el plan.

- `first_name="Juan"` va literal, como en la tabla del plan: es un dato, no prosa.
- `test-sanitizer` aplicado como checklist: dobles con `autospec=True`; preparación con `persist_user` y
  `make_auth_headers`; nombres y variables en inglés; aserciones sobre `{"detail"}` y tipos, nunca texto; nada
  reescrito fuera de lo que pide el plan.

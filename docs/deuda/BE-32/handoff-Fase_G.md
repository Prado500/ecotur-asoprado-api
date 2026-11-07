# Handoff — BE-32 Fase_G: fallos de token, respuestas iguales y distintas, usuario borrado y `make_token` con caducidad

Commit de la fase: `dd88bf8` (`test(tokens): pin token error details and soft-deleted user rejection`), mensaje
letra a letra el del plan, con `<MODELO EJECUTOR>` = `Claude Opus 5.5`. Ejecutor: Claude Opus 5.5 (`fase-ejecutor`).

## Arranque

- `git status --short`: vacío. HEAD `b070f55`. `progress.json`: `current_target` = `Fase_G`.
- Base develop (`verificacion.md:223`): `fd144ad`. `git fetch origin` correcto; `git rev-parse --short origin/develop`
  = `fd144ad`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `57 files already formatted`; ruff `Found 8 errors.` (8 I001 `app\`); mypy
  `Found 9 errors in 5 files (checked 53 source files)`; `Contracts: 4 kept, 0 broken.`; `545 passed, 5 warnings`;
  `TOTAL 943 23 138 19 96.11%`. Es la fila F de la tabla: la fase F no dejó nada roto.

## Archivos tocados

```text
 tests/conftest.py                 | 12 ++++---
 tests/test_token_failure_paths.py | 74 +++++++++++++++++++++++++++++++--------
 2 files changed, 68 insertions(+), 18 deletions(-)
```

- `tests/conftest.py`: `from datetime import timedelta` tras `import itertools`.
  `_make_token(user: User, *, expires_delta: timedelta | None = None) -> str` pasa `expires_delta` a
  `create_access_token`. El `Returns:` cambia a `Callable[..., str]` con el texto dictado, en 3 líneas. Sin claims
  libres (P5). `make_auth_headers` sigue llamando a `make_token(user)`. Con `expires_delta=None`,
  `create_access_token` va por la rama de la duración por defecto (`app/core/security.py:64-67`), así que el token es
  el mismo que antes. `tests/test_fixtures_contract.py` pasa.
- `tests/test_token_failure_paths.py`:
  - Imports: `from datetime import UTC, datetime, timedelta` y el alias `MakeToken = Callable[..., str]`.
  - `_expired_token()` ya no recibe parámetro. Lleva `"ghost@test.com"` fijo y el docstring dictado.
  - Helper nuevo `_user_service(user_repo)`, con el `UserService(...)` que antes estaba en `:156-160`.
  - `test_valid_token_...`: crea una vecina (`await persist_user()`) antes que `user` (D11).
  - `test_expired_token_...`: ahora recibe `make_token: MakeToken` y llama a
    `make_token(user, expires_delta=timedelta(minutes=-1))`.
  - Nuevo `test_corrupt_token_gets_the_same_detail_as_an_unknown_user`, justo después del de `:93-98`, que se queda.
    Es el bloque dictado (D2).
  - `test_token_for_unknown_user_...`: recibe `persist_user` y crea una vecina antes de la petición (D11).
  - Nuevo `test_token_for_soft_deleted_active_user_returns_401`, después del de usuario inactivo (D17).
  - `test_verify_email_chains_...`: usa `_user_service`; se borra `user_repo.activate_user.assert_not_called()` (la
    antigua `:166`). El docstring es el dictado.
  - Nuevo al final: `test_verify_email_expired_and_corrupt_tokens_get_distinct_errors`, el bloque dictado (U6/U7).
  - El archivo pasa de 11 a 14 casos: `pytest --collect-only` → `14 tests collected`.

Orden de edición (E1): en `conftest.py` escribí primero la firma que usa `timedelta` y después su import. Entre las dos
ediciones el hook devolvió `F821 Undefined name timedelta`, como se esperaba, y no borró nada. `test_token_failure_paths.py`
lo reescribí en una sola escritura, con cada import nuevo junto a la línea que lo usa.

Criterios del plan:

```text
grep -c "expired\.value\.detail != corrupt\.value\.detail" tests/test_token_failure_paths.py        -> 1
grep -c 'assert corrupt.json()\["detail"\] == unknown.json()\["detail"\]' tests/test_token_failure_paths.py -> 1
grep -c "expires_delta" tests/conftest.py                                                       -> 3 (212, 216, 218)
grep -c "make_token(user, expires_delta=" tests/test_token_failure_paths.py                     -> 1
grep -rnE "persist_user\([^)]*deleted_at" tests/ --include=*.py | wc -l                         -> 3
    (test_auth.py:306, test_token_failure_paths.py:162, test_user_response.py:116)
grep -rnE -A1 "\.assert_not_called\(\)" tests/ --include=*.py | grep -cE "assert_not_awaited"    -> 0
sed -n 86p tests/conftest.py                                                -> "    async def override_get_db():"
git diff -- app/ | wc -l                                                                        -> 0
```

El patrón 1 (`\.assert_(called|awaited)(_once)?\(\)`) da 1, `tests/test_email.py:99`. Es de la fase H, como ya anotó la
auditoría de D.

## RED: mutantes en copia desechable

Hay dos copias fuera del árbol, en el scratchpad de la sesión, las dos sacadas con `git archive b070f55 | tar -x`:

- **antes**: el árbol de `b070f55` sin cambios (tests previos a la fase, 545 en la suite).
- **después**: `b070f55` con los 2 archivos de la fase copiados encima antes del commit. `git diff --name-only` listaba
  exactamente esos 2 y `cmp` dio idénticos. Tras el commit, `git show dd88bf8:<archivo> | cmp - <copia>` también da
  idénticos para los dos. La copia "después" es, por tanto, el árbol commiteado `dd88bf8` (548 en la suite).

El script localiza cada mutante por contenido (exige exactamente 1 coincidencia), lo aplica y corre
`pytest -q --no-cov -p no:cacheprovider` sobre `tests/test_token_failure_paths.py` y sobre `tests`. Después restaura el
archivo byte a byte en un `finally` y lo comprueba con `assert`. Usa variables de entorno ficticias (`JWT_SECRET_KEY`,
`ALGORITHM=HS256`, `*_EXPIRE_MINUTES`, `DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`,
`CORS_ORIGINS`, `FRONTEND_URL`) y el Python del `venv/`. `app` resolvía a la copia en los dos casos (lo imprime el
script). El repo nunca llevó un mutante.

Definición de cada mutante:

- **D2**: en `get_current_user` se cambian los cuerpos de las ramas. `except jwt.ExpiredSignatureError` (`:101`) lanza
  `credentials_exception from err`, y `except jwt.InvalidTokenError` (`:107`) lanza el `HTTPException` de sesión
  expirada `from err`.
- **U6**: el texto de `user_service.py:127` (expirado) se sustituye por el de `:131` (corrupto).
- **U7**: en `verify_email_account`, el bloque `except jwt.InvalidTokenError` pasa delante de `except jwt.ExpiredSignatureError`.
- **D17**: `user_repository.py:22` sin `User.deleted_at.is_(None)`.
- **D11**: `user_repository.py:22` sin `User.email == email`.
- **D1**: se intercambian los dos textos de `dependencies.py`.
- **U1**: se intercambian los dos textos de `user_service.py`.
- **U8**: en la rama `except jwt.ExpiredSignatureError` de `verify_email_account`, antes del `raise`, se añade
  `await self.user_repo.activate_user(jwt.decode(token, options={"verify_signature": False})["sub"])`.

| Mutante | Antes, archivo (`b070f55`, 11 casos) | Después, archivo (`dd88bf8`, 14 casos) | Antes, suite (`b070f55`) | Después, suite (`dd88bf8`) |
|---|---|---|---|---|
| sin mutante | `11 passed` | `14 passed` | `545 passed, 5 warnings` | `548 passed, 5 warnings` |
| D2 | `11 passed` | `1 failed, 13 passed` (`corrupt_token_gets_the_same_detail_as_an_unknown_user`) | `545 passed` | `1 failed, 547 passed` (el mismo) |
| U6 | `11 passed` | `1 failed, 13 passed` (`verify_email_expired_and_corrupt_tokens_get_distinct_errors`) | `545 passed` | `1 failed, 547 passed` (el mismo) |
| U7 | `11 passed` | `1 failed, 13 passed` (el mismo) | `545 passed` | `1 failed, 547 passed` (el mismo) |
| D17 | `11 passed` | `1 failed, 13 passed` (`soft_deleted_active_user_returns_401`) | `1 failed, 544 passed` (`test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login`) | `2 failed, 546 passed` (ese y el nuevo) |
| D11 | `11 passed` | `2 failed, 12 passed` (`valid_token` y `unknown_user`) | `1 failed, 544 passed` (`test_auth.py::test_admin_directory_hides_superadmins`) | `3 failed, 545 passed` (ese y los 2 del archivo) |
| D1 | `11 passed` | `14 passed` (vivo: Residuales) | `545 passed` | `548 passed` |
| U1 | `11 passed` | `14 passed` (vivo: Residuales) | `545 passed` | `548 passed` |
| U8 | `1 failed, 10 passed` (`verify_email_chains_...[expired]`, la `:166`) | `14 passed` | `2 failed, 543 passed` (`:166` y `test_user_service.py::test_verify_email_expired_token_raises_invalid_verification_token`) | `1 failed, 547 passed` (`test_user_service.py::test_verify_email_expired_token_...`) |

Salida literal del script, estado **antes** (`b070f55`):

```text
none | file: 11 passed in 0.21s
none | suite: 545 passed, 5 warnings in 18.44s
D2 | file: 11 passed in 0.20s
D2 | suite: 545 passed, 5 warnings in 18.95s
U6 | file: 11 passed in 0.18s
U6 | suite: 545 passed, 5 warnings in 19.20s
U7 | file: 11 passed in 0.21s
U7 | suite: 545 passed, 5 warnings in 18.90s
D17 | file: 11 passed in 0.21s
D17 | suite: 1 failed, 544 passed, 5 warnings in 19.61s
      FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
D11 | file: 11 passed in 0.21s
D11 | suite: 1 failed, 544 passed, 5 warnings in 19.69s
      FAILED tests/test_auth.py::test_admin_directory_hides_superadmins - assert 40...
D1 | file: 11 passed in 0.20s
D1 | suite: 545 passed, 5 warnings in 18.95s
U1 | file: 11 passed in 0.24s
U1 | suite: 545 passed, 5 warnings in 19.00s
U8 | file: 1 failed, 10 passed in 0.35s
      FAILED tests/test_token_failure_paths.py::test_verify_email_chains_the_jwt_error_as_cause[expired]
U8 | suite: 2 failed, 543 passed, 5 warnings in 19.47s
      FAILED tests/test_token_failure_paths.py::test_verify_email_chains_the_jwt_error_as_cause[expired]
      FAILED tests/test_user_service.py::test_verify_email_expired_token_raises_invalid_verification_token
all mutants restored byte for byte
```

Salida literal del script, estado **después** (árbol commiteado `dd88bf8`):

```text
none | file: 14 passed in 0.25s
none | suite: 548 passed, 5 warnings in 18.85s
D2 | file: 1 failed, 13 passed in 0.43s
      FAILED tests/test_token_failure_paths.py::test_corrupt_token_gets_the_same_detail_as_an_unknown_user
D2 | suite: 1 failed, 547 passed, 5 warnings in 18.93s
      FAILED tests/test_token_failure_paths.py::test_corrupt_token_gets_the_same_detail_as_an_unknown_user
U6 | file: 1 failed, 13 passed in 0.42s
      FAILED tests/test_token_failure_paths.py::test_verify_email_expired_and_corrupt_tokens_get_distinct_errors
U6 | suite: 1 failed, 547 passed, 5 warnings in 19.18s
      FAILED tests/test_token_failure_paths.py::test_verify_email_expired_and_corrupt_tokens_get_distinct_errors
U7 | file: 1 failed, 13 passed in 0.39s
      FAILED tests/test_token_failure_paths.py::test_verify_email_expired_and_corrupt_tokens_get_distinct_errors
U7 | suite: 1 failed, 547 passed, 5 warnings in 19.19s
      FAILED tests/test_token_failure_paths.py::test_verify_email_expired_and_corrupt_tokens_get_distinct_errors
D17 | file: 1 failed, 13 passed in 0.41s
      FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
D17 | suite: 2 failed, 546 passed, 5 warnings in 19.67s
      FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
      FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
D11 | file: 2 failed, 12 passed in 0.41s
      FAILED tests/test_token_failure_paths.py::test_valid_token_on_protected_route_returns_the_user
      FAILED tests/test_token_failure_paths.py::test_token_for_unknown_user_returns_401
D11 | suite: 3 failed, 545 passed, 5 warnings in 19.23s
      FAILED tests/test_auth.py::test_admin_directory_hides_superadmins - assert 40...
      FAILED tests/test_token_failure_paths.py::test_valid_token_on_protected_route_returns_the_user
      FAILED tests/test_token_failure_paths.py::test_token_for_unknown_user_returns_401
D1 | file: 14 passed in 0.30s
D1 | suite: 548 passed, 5 warnings in 19.53s
U1 | file: 14 passed in 0.27s
U1 | suite: 548 passed, 5 warnings in 19.09s
U8 | file: 14 passed in 0.25s
U8 | suite: 1 failed, 547 passed, 5 warnings in 19.41s
      FAILED tests/test_user_service.py::test_verify_email_expired_token_raises_invalid_verification_token
all mutants restored byte for byte
```

Las columnas de archivo coinciden fila a fila con la tabla del plan.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Medida sobre el árbol de trabajo con los 2 archivos de la fase, que es el contenido de `dd88bf8`.

- `ruff format --check`: `57 files already formatted`.
- `ruff check`: `Found 8 errors.`. Las 8 son I001 `:1:1` en `app\api\dependencies.py`, `app\api\routers\audit.py`,
  `app\core\email.py`, `app\db\database.py`, `app\repositories\user_repository.py`, `app\schemas\audit.py`,
  `app\services\audit_service.py` y `app\services\user_service.py`. Ninguna está en `tests\`.
- mypy: `Found 9 errors in 5 files (checked 53 source files)`. Son `app\db\database.py:11`, `app\core\security.py:71`,
  `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95` y `tests\test_user_service.py:105`, `:203`,
  `:280`, `:298`. Los cuatro de tests son los `[arg-type]` `str | None` de `SECRET_KEY`. Es el conjunto de A4.
- import-linter: `Contracts: 4 kept, 0 broken.`
- pytest: `548 passed, 5 warnings in 19.33s` (545 + 3).
- Cobertura: `TOTAL 943 23 138 19 96.11%` (antes: 96.11 %).

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Archivos tocados:

- `ruff check tests/conftest.py tests/test_token_failure_paths.py` → `All checks passed!`.
- `ruff format --check` sobre los mismos → `2 files already formatted`.
- `mypy tests/conftest.py tests/test_token_failure_paths.py` → 0 líneas `error:` en esos dos archivos. El total,
  `Found 5 errors in 4 files (checked 2 source files)`, son los 5 de `app/` (A4), que entran al seguir los imports.

Checklist de `test-sanitizer` (Enterprise Test Standards): no hay dobles nuevos. `user_repo` y el `AuditService` de
`_user_service` siguen con `create_autospec`. El token caducado de la ruta protegida ya sale de la fábrica `make_token`
y no se construye a mano. Nombres y docstrings están en inglés. Se afirma sobre `{"detail"}`, el código 401 y
`WWW-Authenticate`. Los mensajes se comparan con `==`/`!=` entre sí y nunca se leen. No hubo que reescribir ningún test
que ya cumpliera.

## Desviaciones y dudas

1. **D17 y D11 ya morían en la suite antes de la fase.** El plan solo da una cifra de suite, para D17
   (`suite: 1 failed`), y supone que hoy sobrevive (`BE-33/gaps.md:145`: `432 passed`). En `b070f55`, D17 da
   `1 failed, 544 passed` por `test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login`. Tras la fase da
   **`2 failed, 546 passed`**, no `1 failed`. D11 también da `1 failed` antes (`test_auth.py::test_admin_directory_hides_superadmins`;
   BE-33 medía `11 failed`) y `3 failed` después. Las columnas de archivo, que son las que la tabla define, coinciden
   todas. Lo que la fase añade es que el camino del token (`get_current_user`) detecta D17 por sí mismo: el test de
   `test_auth.py` no llega por ese camino, porque el usuario borrado por la ruta normal también queda `is_active=False`.
   No lo traté como bloqueante, porque la compuerta coincide en todas sus cifras y el archivo mata lo que el plan pide.
   El auditor decide.
2. **Forma concreta de U8.** El plan dice "activar antes de lanzar", sin código. Lo apliqué solo en la rama de
   expiración, que es la que cubría la `:166`. Así reproduce la medición de BE-33: la suite lo sigue detectando
   (`1 failed`) por `test_user_service.py::test_verify_email_expired_token_raises_invalid_verification_token`, que es la
   línea de `assert_not_awaited` de ese test, hoy en `:287`. El plan la citaba como `:281`, en la base de BE-33.
3. **El docstring de `_bearer` se queda viejo.** Dice "for a token the factories cannot produce", y ahora
   `test_expired_token_...` le pasa un token de `make_token`. El plan no lo toca y no lo cambié. Lo dejo como opcional
   para el auditor.
4. El docstring de `_user_service` (`"""Builds the real UserService over the given repository double."""`) no estaba
   dictado; el plan solo pedía el helper. Es de una línea, como los demás helpers privados del archivo.

## Residuales

- D1 y U1 siguen vivos (`14 passed` / `548 passed`), como prevé el plan. Ya están en los Residuales del plan.
- Los tres `create_access_token(data={"sub": ...})` sin `User` detrás siguen en el archivo: dos con
  `"ghost@test.com"` (D2 y usuario desconocido) y uno sin `sub`. Están fuera de alcance por el plan.

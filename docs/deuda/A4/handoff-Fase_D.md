# Handoff — A4 · Fase D (la app firma y verifica JWT con `Settings`)

- Commit de la fase: `e4602cf` — `refactor(auth): sign and verify JWTs with the injected Settings (A4)`
- Rama: `item/a4`, sobre `d528748` (auditoría PASS de la fase C).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 10 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_D`. `gaps.md`: fases A, B y C en PASS, nada para D.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `8cea834`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `8cea834`; `Base develop` de `verificacion.md` = `8cea834`.
- Compuerta antes de tocar nada (exit 1), igual a la fila C: `60 files already formatted` · ruff `Found 8 errors.` ·
  mypy `Found 5 errors in 4 files (checked 55 source files)` (`database.py:11`, `security.py:71,87`,
  `user_service.py:124`, `dependencies.py:95`) · `Contracts: 4 kept, 0 broken.` · `573 passed, 5 warnings` ·
  `TOTAL … 96.23%`.

## Archivos tocados

- `app/core/security.py`, `app/api/dependencies.py`, `app/services/user_service.py`, `tests/test_token_failure_paths.py`.
  Ningún otro.

`git show --stat e4602cf`:

```
 app/api/dependencies.py           | 34 +++++++++++++++++++++++-----------
 app/core/security.py              | 38 +++++++++++++++++++++++++++-----------
 app/services/user_service.py      | 18 +++++++++---------
 tests/test_token_failure_paths.py | 17 ++++++++++++++++-
 4 files changed, 75 insertions(+), 32 deletions(-)
```

Resumen del diff:

- `app/core/security.py`: fuera `import os` y las 4 constantes; `from app.core.config import get_settings`.
  `create_access_token` y `create_verification_token` hacen `settings = get_settings()` y usan
  `settings.access_token_expire_minutes` / `settings.verification_token_expire_minutes` / `settings.jwt_secret_key` /
  `settings.algorithm`. Docstrings con `Args`/`Returns`.
- `app/api/dependencies.py`: el import `from app.core.security import SECRET_KEY, ALGORITHM` se sustituye por
  `from app.core.config import Settings, get_settings`. `get_current_user` gana
  `settings: Settings = Depends(get_settings)` (tercer parámetro) y decodifica con
  `jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])`. Docstring con `Args`/`Returns`/`Raises`.
  I001 aplicado con `ruff check --select I001 --fixable I001 --fix`.
- `app/services/user_service.py`: el import de `app.core.security` pierde `SECRET_KEY, ALGORITHM`; se añade
  `from app.core.config import get_settings`. `verify_email_account` hace `settings = get_settings()` antes del `try`.
  I001 aplicado con el mismo comando. El servicio sigue sin importar FastAPI/Starlette (4 contratos kept).
- `tests/test_token_failure_paths.py`: imports `from app.core.config import get_settings` y `from app.main import app`;
  la llamada directa a `get_current_user` del test parametrizado (`:179` en el plan, que contaba líneas de la base;
  `:263` hoy) pasa `settings=get_settings()`; test nuevo `test_protected_route_verifies_with_the_injected_settings`
  con el docstring dictado.

## Tests (RED primero)

RED del test nuevo, escrito antes de tocar `app/` (literal):

```
>       assert response.status_code == 401
E       assert 200 == 401
E        +  where 200 = <Response [200 OK]>.status_code

tests\test_token_failure_paths.py:73: AssertionError
FAILED tests/test_token_failure_paths.py::test_protected_route_verifies_with_the_injected_settings
1 failed, 17 deselected in 0.19s
```

Esperado por el plan: 200 antes de D (el override no llega a `SECRET_KEY`). Coincide. GREEN tras el cambio:
`tests/test_token_failure_paths.py` → `18 passed in 0.32s`.

RED de herramienta: mypy `security.py:71,87`, `dependencies.py:95`, `user_service.py:124` (compuerta de arranque,
arriba) → 0. `mypy` sobre los 4 archivos tocados tras el cambio:

```
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
Found 1 error in 1 file (checked 4 source files)
```

(el único error lo arrastra el import de `app.db.database`, archivo de la fase E). `ruff check` sobre los 4 archivos:
`All checks passed!`; `ruff format --check`: `4 files already formatted`.

## Mutantes (copia `git archive HEAD` de `e4602cf` en el scratchpad, una por mutante, sin `.env`)

Salida literal (línea mutada con `grep -n "jwt.decode"`, después
`pytest -q -p no:cacheprovider tests/test_token_failure_paths.py -k …`):

```
== none
no .env
107:        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
4 passed, 14 deselected in 0.10s
== none_svc
no .env
124:            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
3 passed, 15 deselected in 0.11s
== M1p
no .env
107:        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm], options={"verify_signature": False, "verify_exp": True})
2 failed, 1 passed, 15 deselected in 0.34s
== M2p
no .env
124:            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm], options={"verify_signature": False, "verify_exp": True})
1 failed, 2 passed, 15 deselected in 0.32s
== M5
no .env
107:        payload = jwt.decode(token, get_settings().jwt_secret_key, algorithms=[settings.algorithm])
1 failed, 17 deselected in 0.28s
```

(`none` con `-k "signed_with or injected_settings"`; `none_svc` con `-k signed_with`; M1'/M2' con `-k signed_with`;
M5 con `-k injected_settings`.) Esperado por el plan: M1' `2 failed, 1 passed`; M2' `1 failed, 2 passed`; M5
`1 failed`. Coincide.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Extractos literales:

```
60 files already formatted
I001 Import block is un-sorted or un-formatted
 --> app\api\routers\audit.py:1:1
I001 Import block is un-sorted or un-formatted
 --> app\core\email.py:1:1
I001 Import block is un-sorted or un-formatted
 --> app\db\database.py:1:1
I001 Import block is un-sorted or un-formatted
 --> app\repositories\user_repository.py:1:1
I001 Import block is un-sorted or un-formatted
 --> app\schemas\audit.py:1:1
I001 Import block is un-sorted or un-formatted
 --> app\services\audit_service.py:1:1
Found 6 errors.
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
Found 1 error in 1 file (checked 55 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        975     23    138     19  96.23%
Required test coverage of 92.0% reached. Total coverage: 96.23%
574 passed, 5 warnings in 19.62s
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
| Esperado (fila D) | 6 | 1 en 1 (55), `database.py:11` | 574 | ≥ 96.23 % (C) y ≥ 96.11 % (base) | 60 | 4 kept |
| Real | 6 | 1 en 1 (55), `database.py:11` | 574 passed | 96.23 % | 60 | 4 kept |

Los 6 I001 restantes son los que el plan asigna a E (`database.py`, `email.py`) y a I (los otros 4).

## Residuales y dudas

- **Comentarios desplazados por el I001 de `dependencies.py` (OPCIONAL, no tocado).** El orden de ruff deja
  `# Repository injection` sobre `from app.repositories.user_repository …` (precedido ya de `service_repository`) y
  `# Service injection` sobre `from app.services.user_service …`, después de `audit_service`, `tourist_services_service`
  y `user_access_policy`. Ya no describen los bloques. El plan dicta solo el `ruff --fix`, así que no los moví ni
  borré; pueden retirarse cuando alguien toque ese bloque (p. ej. la fase G, si el plan lo permite).
- **Finales de línea:** una edición intermedia con `Path.write_text` dejó `security.py` en CRLF en el árbol; se
  normalizó a LF antes del commit (`git ls-files --eol` → `w/lf` en los 4 archivos). El commit no contiene cambios de
  EOL.
- Referencia de línea del plan (`:179`) desfasada respecto al archivo actual (`:263`) porque las fases A y C añadieron
  código encima; el cambio aplicado es el que el plan describe (única llamada directa a `get_current_user`).
- Checklist `test-sanitizer`: el test nuevo no usa mocks; usa las fábricas `persist_user` y `make_auth_headers`; el
  override de `get_settings` lo limpia el `dependency_overrides.clear()` del fixture `client`; afirma código 401,
  cabecera `WWW-Authenticate` y estructura del JSON (`_assert_bearer_401`), sin texto en español. No se reescribió
  ningún otro test.

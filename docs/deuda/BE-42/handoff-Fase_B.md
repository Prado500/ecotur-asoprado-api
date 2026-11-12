# Handoff — BE-42 · Fase B (todo token de acceso lleva `scope=access`)

- Commit de la fase: `20429bf` — `feat(auth): sign every access token with the access scope`
- Rama: `item/be-42`, sobre `53268ba` (auditoría PASS de la fase A).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.
- Enmiendas aplicadas: E0 (P2 `make_token` sin `extra_claims`; P3 `sign_claims` en `tests/conftest.py`; P4 test del
  `scope` impuesto, que mata a MD).

## Ritual de arranque

- `git status --short`: limpio. HEAD `53268ba`. `current_target` = `Fase_B`. `gaps.md`: fase A PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `deb0b1e`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `deb0b1e`; `Base develop` de `verificacion.md` = `deb0b1e`.
- Compuerta antes de tocar nada (exit 0), igual a la fila A: `61 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · `618 passed, 8 warnings` ·
  `TOTAL 962 19 136 16 96.81%`.

## Archivos tocados (los 4 de la fase)

`git show --stat 20429bf`:

```
 app/core/security.py       |  8 ++++++--
 tests/conftest.py          | 41 ++++++++++++++++++++++++++++++-----------
 tests/test_auth.py         |  1 +
 tests/test_user_service.py | 40 +++++++++++++++++++++++++++++-----------
 4 files changed, 66 insertions(+), 24 deletions(-)
```

Resumen del diff, todo dictado por el plan:

1. `app/core/security.py`: `ACCESS_TOKEN_SCOPE = "access"` entre el comentario y `EMAIL_VERIFICATION_SCOPE`; párrafo
   nuevo en el docstring de `create_access_token` y línea de Args `… A scope in it is replaced.`;
   `to_encode.update({"scope": ACCESS_TOKEN_SCOPE, "exp": expire})`.
2. `tests/conftest.py`: imports (`UTC, datetime, timedelta`; `import jwt`; `get_settings`); `make_token` sin
   `extra_claims` (firma de una línea, docstring nuevo); fixture `sign_claims` entre `make_token` y `make_auth_headers`.
3. `tests/test_auth.py`: `assert claims["scope"] == "access"` en `test_login_active_user_returns_bearer_token`.
4. `tests/test_user_service.py`: import partido (`EMAIL_VERIFICATION_SCOPE`, `create_access_token`,
   `create_verification_token`, `get_password_hash`); `scope` en los claims de `authenticate_user`; test de caducidad con
   `sign_claims` y `assert type(exc_info.value.__cause__) is jwt.ExpiredSignatureError`; test de `scope` equivocado con
   `make_token(make_user(email="turista@example.com"))`; test nuevo
   `test_verify_email_rejects_access_token_whose_data_names_the_verification_scope`.

No se tocaron `app/api/dependencies.py`, `tests/test_route_guards.py`, `tests/test_token_failure_paths.py`, los
docstrings de un solo uso ni `activate_user`.

## RED (tests escritos antes de tocar `security.py`)

`git diff --stat app/` vacío en ese momento.
`./venv/Scripts/python.exe -m pytest tests/test_auth.py tests/test_user_service.py -q -p no:cacheprovider -rf`:

```
E       KeyError: 'scope'
tests\test_auth.py:136: KeyError
E       KeyError: 'scope'
tests\test_user_service.py:221: KeyError
E       Failed: DID NOT RAISE <class 'app.core.exceptions.InvalidVerificationTokenError'>
FAILED tests/test_auth.py::test_login_active_user_returns_bearer_token - KeyE...
FAILED tests/test_user_service.py::test_authenticate_active_user_returns_bearer_token
FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
3 failed, 37 passed in 4.39s
```

GREEN tras `security.py`: `40 passed in 4.06s`. Los dos tests reescritos (caducado y `scope` equivocado) estuvieron
verdes antes y después.

Checklist `test-sanitizer` (solo "Ecotur Enterprise Test Standards"): `user_repo` sigue siendo el mock con autospec
existente; los tokens salen de fábricas de `conftest.py` (`make_token`, `sign_claims`) o de la API de producción; nombres
en inglés; ninguna aserción sobre texto en español. No se reescribió ningún test fuera de lo dictado.

## Mutantes (procedimiento común; directorios nuevos bajo
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\9323b4d2-0c40-448b-8044-1c871b545639\scratchpad\be42b`,
`git archive HEAD` tras el commit)

Cada edición se comprobó con `sed -n` y `diff -r` contra la copia sin mutante (una sola línea cambiada en cada una):

- MA (`sed -n 82p app/core/security.py` → `    to_encode.update({"exp": expire})`):
  ```
  FAILED tests/test_auth.py::test_login_active_user_returns_bearer_token - KeyE...
  FAILED tests/test_user_service.py::test_authenticate_active_user_returns_bearer_token
  FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
  3 failed, 327 passed, 8 warnings in 13.39s
  ```
- MD (`sed -n 82p` → `    to_encode.update({"scope": data.get("scope", ACCESS_TOKEN_SCOPE), "exp": expire})`):
  ```
  FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
  1 failed, 329 passed, 8 warnings in 13.86s
  ```
- MV (`sed -n 138p app/services/user_service.py` → `        if email is None:`):
  ```
  FAILED tests/test_user_service.py::test_verify_email_wrong_scope_raises_invalid_verification_token
  FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
  2 failed, 328 passed, 8 warnings in 13.44s
  ```
- Copia sin mutante: `330 passed, 8 warnings in 12.44s`, como la fila B.

Los tres coinciden con el plan.

## Criterio de aceptación

```
$ git show --numstat --format= 20429bf
6	2	app/core/security.py
30	11	tests/conftest.py
1	0	tests/test_auth.py
29	11	tests/test_user_service.py
$ git grep -n "extra_claims" -- app tests | wc -l
0
```

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` → exit 0. Bloque RESUMEN literal:

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

- pytest: `619 passed, 8 warnings in 15.41s` (0 failed). Cobertura: `TOTAL 963 19 136 16 96.82%` ·
  `Total coverage: 96.82%` (≥ 96,81 % de la base).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Sobre los cuatro archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already
  formatted`; `mypy` → `Success: no issues found in 4 source files`.
- Coincide con la fila B del plan (619 passed, 96,82 %, 963 stmts).

## Residuales y dudas

- Ninguno nuevo. Sin desviaciones del plan ni de E0.

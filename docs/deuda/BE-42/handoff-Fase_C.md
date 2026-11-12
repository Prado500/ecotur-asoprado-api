# Handoff — BE-42 · Fase C (`get_current_user` exige el `scope` de acceso)

- Commit de la fase: `717fc73` — `fix(auth)!: accept only access tokens as bearer` (con el footer `BREAKING CHANGE`
  exacto del plan; E0, P1).
- Rama: `item/be-42`, sobre `48e782e` (auditoría PASS de la fase B).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.
- Enmiendas aplicadas: E0 (P1 `fix(auth)!` + `BREAKING CHANGE`; P4 test del `detail` idéntico al de un token corrupto).

## Ritual de arranque

- `git status --short`: limpio. HEAD `48e782e`. `current_target` = `Fase_C`. `gaps.md`: fases A y B PASS, sin BLOQUEANTE.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `deb0b1e`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `deb0b1e`; `Base develop` de `verificacion.md` = `deb0b1e`.
- Compuerta antes de tocar nada (exit 0), igual a la fila B: `61 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · `619 passed, 8 warnings` ·
  `TOTAL 963 19 136 16 96.82%`.

## Archivos tocados (los 3 de la fase)

`git show --stat 717fc73`:

```
 app/api/dependencies.py           | 10 ++++++++--
 tests/test_route_guards.py        | 24 ++++++++++++++++++++++++
 tests/test_token_failure_paths.py | 34 ++++++++++++++++++++++++++++++++++
 3 files changed, 66 insertions(+), 2 deletions(-)
```

Resumen del diff, todo dictado por el plan:

1. `app/api/dependencies.py`: `from app.core.security import ACCESS_TOKEN_SCOPE` tras el import de `config`; párrafo
   nuevo en el docstring de `get_current_user` ("Only an access token is a bearer: …"); `Raises:` dice
   `subject, is not an access token, or names no active user.`; `scope: str | None = payload.get("scope")` y
   `if email is None or scope != ACCESS_TOKEN_SCOPE:`. `credentials_exception`, los dos `except`, la búsqueda del usuario
   y todo desde `get_current_admin_user` sin cambios.
2. `tests/test_route_guards.py`: import de `create_verification_token`; test parametrizado nuevo
   `test_protected_route_rejects_verification_token_as_bearer` (17 casos, superadmin activo) entre
   `test_protected_route_rejects_request_without_token` y `test_admin_route_rejects_tourist`.
3. `tests/test_token_failure_paths.py`: alias `SignClaims`; `test_access_token_without_scope_returns_401` y
   `test_verification_token_gets_the_same_detail_as_a_corrupt_token` entre `test_token_for_unknown_user_returns_401` y
   `test_token_for_inactive_user_returns_401`.

Ningún test existente cambia (solo inserciones en los dos archivos de tests). No se tocaron los guards de admin y
superadmin, los alias, los routers, la política, `security.py`, `conftest.py`, los tests de la fase B, los docstrings de
un solo uso ni `activate_user`.

Nota de proceso: el hook `ruff --fix` borró el import de `create_verification_token` tras la primera edición (aún sin
uso) y señaló F821 en `SignClaims` y `ACCESS_TOKEN_SCOPE` mientras las ediciones iban por partes; se repusieron. El texto
final es el del plan, como prueba el numstat.

## RED (tests escritos antes de tocar `dependencies.py`)

`git diff --stat app/` vacío en ese momento.
`./venv/Scripts/python.exe -m pytest tests/test_route_guards.py tests/test_token_failure_paths.py -q -p no:cacheprovider -rf`
→ `19 failed, 64 passed, 6 warnings in 1.52s`. Código que devuelve hoy cada ruta con el token de verificación de un
superadmin activo (`--tb=line`, `assert <código> == 401`):

| Código | Rutas |
|---|---|
| 200 (6) | `GET /usuarios/`, `GET /usuarios/admin/eliminados`, `GET /servicios/admin/inactivos`, `GET /servicios/admin/eliminados`, `GET /auditoria/`, `GET /usuarios/mi-perfil` |
| 404 (7) | `PATCH /usuarios/{cedula}/recuperar`, `PUT /servicios/{service_id}`, `PATCH /servicios/{service_id}/activar`, `PATCH /servicios/{service_id}/desactivar`, `DELETE /servicios/{service_id}`, `DELETE /usuarios/{cedula}`, `PATCH /usuarios/{cedula}` |
| 422 (3) | `POST /usuarios/admin`, `POST /servicios/upload-images/`, `POST /servicios/` |
| 400 (1) | `PATCH /servicios/{service_id}/recuperar` |

Los otros dos fallos, ambos `assert 200 == 401` (`tests/test_token_failure_paths.py:74`, en `_assert_bearer_401`):

```
FAILED tests/test_token_failure_paths.py::test_access_token_without_scope_returns_401
FAILED tests/test_token_failure_paths.py::test_verification_token_gets_the_same_detail_as_a_corrupt_token
19 failed, 64 passed, 6 warnings in 1.52s
```

Coincide con el plan. GREEN tras `dependencies.py`: `83 passed, 3 warnings in 2.52s`.

Checklist `test-sanitizer` (solo "Ecotur Enterprise Test Standards"): sin mocks nuevos; los tokens salen de la API de
producción (`create_verification_token`) o de la fábrica `sign_claims` de `conftest.py`; usuarios con `persist_user`;
nombres en inglés; las aserciones van sobre código, cabecera y estructura (`{"detail"}`) y la igualdad de `detail` entre
dos respuestas, nunca sobre texto en español. No se reescribió ningún test.

## Mutantes (procedimiento común; un directorio nuevo por mutante bajo
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\9323b4d2-0c40-448b-8044-1c871b545639\scratchpad\be42c`,
`git archive HEAD` tras el commit `717fc73`)

Cada edición se comprobó con `sed -n <línea>p` en la copia, y con `diff -r` contra la copia sin mutante (`BASE`): una
sola línea cambiada en cada mutante y dos en los dobles.

| Mutante | Línea mutada (`sed -n`) | Resultado | Plan |
|---|---|---|---|
| (sin mutante) | — | `349 passed` | 349 passed |
| MSC | `dependencies.py:128` → `        if email is None:` | `19 failed, 330 passed` | 19 / 330 |
| MSUB | `dependencies.py:128` → `        if scope != ACCESS_TOKEN_SCOPE:` | `1 failed, 348 passed` | 1 / 348 |
| MU | `dependencies.py:144` → `    if user is not None and not user.is_active:` | `3 failed, 346 passed` | 3 / 346 |
| MA | `security.py:82` → `    to_encode.update({"exp": expire})` | `102 failed, 247 passed` | 102 / 247 |
| MA+MSUB | `security.py:82` y `dependencies.py:128` como arriba | `102 failed, 247 passed` | 102 / 247 |
| MA+MU | `security.py:82` y `dependencies.py:144` como arriba | `102 failed, 247 passed` | 102 / 247 |
| MD | `security.py:82` → `    to_encode.update({"scope": data.get("scope", ACCESS_TOKEN_SCOPE), "exp": expire})` | `1 failed, 348 passed` | 1 / 348 |
| MV | `user_service.py:138` → `        if email is None:` | `2 failed, 347 passed` | 2 / 347 |
| MEV | `security.py:52` → `EMAIL_VERIFICATION_SCOPE = "verification"` | `1 failed, 348 passed` | 1 / 348 |
| MAV | `security.py:51` → `ACCESS_TOKEN_SCOPE = "bearer"` | `2 failed, 347 passed` | 2 / 347 |

`FAILED` literales:

- MSC: los 17 `test_protected_route_rejects_verification_token_as_bearer[...]` (las mismas 17 rutas del RED) y
  ```
  FAILED tests/test_token_failure_paths.py::test_access_token_without_scope_returns_401
  FAILED tests/test_token_failure_paths.py::test_verification_token_gets_the_same_detail_as_a_corrupt_token
  19 failed, 330 passed, 11 warnings in 14.40s
  ```
- MSUB:
  ```
  FAILED tests/test_token_failure_paths.py::test_token_without_subject_returns_401
  1 failed, 348 passed, 8 warnings in 14.05s
  ```
- MU:
  ```
  FAILED tests/test_token_failure_paths.py::test_corrupt_token_gets_the_same_detail_as_an_unknown_user
  FAILED tests/test_token_failure_paths.py::test_token_for_unknown_user_returns_401
  FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
  3 failed, 346 passed, 8 warnings in 13.93s
  ```
- MA: `102 failed, 247 passed, 4 warnings in 14.20s`. Por archivo: `test_services.py` 29, `test_user_access_policy.py` 24,
  `test_route_guards.py` 18 (14 `test_admin_route_rejects_tourist`, 1 `test_superadmin_route_rejects_admin`, 3
  `test_user_route_lets_tourist_through`), `test_auth.py` 13, `test_user_response.py` 12, `test_audit.py` 3,
  `test_user_service.py` 2 (`test_authenticate_active_user_returns_bearer_token`,
  `test_verify_email_rejects_access_token_whose_data_names_the_verification_scope`) y `test_token_failure_paths.py` 1
  (`test_valid_token_on_protected_route_returns_the_user`). Igual al desglose del plan.
- MA+MSUB: `102 failed, 247 passed, 4 warnings in 13.91s`; MA+MU: `102 failed, 247 passed, 4 warnings in 14.02s`. Mismo
  desglose por archivo que MA. Los tres tests del rincón 2 (`test_token_without_subject_returns_401`,
  `test_corrupt_token_gets_the_same_detail_as_an_unknown_user`, `test_token_for_unknown_user_returns_401`) no aparecen
  en ningún `FAILED`: siguen en verde, que es el contrafactual del análisis.
- MD:
  ```
  FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
  1 failed, 348 passed, 8 warnings in 13.47s
  ```
- MV:
  ```
  FAILED tests/test_user_service.py::test_verify_email_wrong_scope_raises_invalid_verification_token
  FAILED tests/test_user_service.py::test_verify_email_rejects_access_token_whose_data_names_the_verification_scope
  2 failed, 347 passed, 8 warnings in 13.54s
  ```
- MEV:
  ```
  FAILED tests/test_user_service.py::test_register_tourist_returns_registration_result
  1 failed, 348 passed, 8 warnings in 14.07s
  ```
- MAV:
  ```
  FAILED tests/test_auth.py::test_login_active_user_returns_bearer_token - Asse...
  FAILED tests/test_user_service.py::test_authenticate_active_user_returns_bearer_token
  2 failed, 347 passed, 8 warnings in 14.36s
  ```

Todos coinciden con el plan.

## Criterio de aceptación

```
$ git show --numstat --format= 717fc73
8	2	app/api/dependencies.py
24	0	tests/test_route_guards.py
34	0	tests/test_token_failure_paths.py
$ ./venv/Scripts/python.exe -m pytest tests/test_route_guards.py --collect-only -q -p no:cacheprovider
63 tests collected in 0.02s
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

- pytest: `638 passed, 8 warnings in 24.03s` (0 failed). Cobertura: `TOTAL 965 19 136 16 96.82%` ·
  `Total coverage: 96.82%`.
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Sobre los tres archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already
  formatted`; `mypy` → `Success: no issues found in 3 source files`.
- Fila C del plan: 638 passed, 96,82 %, 965 stmts → coincide. Línea base: 618 passed, 96,81 % → +20 tests, +0,01 pp.

## Verificación final (plan, sección "Verificación final"; C es la última fase)

Salida literal, en el orden del plan:

```
# 1
8	2	app/api/dependencies.py
11	3	app/core/security.py
2	1	app/services/user_service.py
30	11	tests/conftest.py
1	0	tests/test_auth.py
24	0	tests/test_route_guards.py
34	0	tests/test_token_failure_paths.py
29	11	tests/test_user_service.py
# 2
0
0
0
# 3
app/api/dependencies.py:4
2
2
16
4
5
3
3
tests/test_route_guards.py:17
63 tests collected in 0.02s
# 4
1
1
6
7
# 5
0
8
2
83 passed, 3 warnings in 1.45s
```

- Puntos 1 a 5: todas las cifras coinciden con las esperadas por el plan.
- Punto 6 (compuerta): exit 0; 638 passed; 96,82 % (≥ 96,81 %); 61 files; mypy 56 source files; 4 kept; 8 warnings.
  Se corrió sobre el árbol que luego se commiteó tal cual (`git status` solo mostraba los tres archivos de la fase).
- Punto 7 (mutantes sobre la copia del estado final): ver la tabla de arriba; todos coinciden.

## Residuales y dudas

- Ninguno nuevo. Sin desviaciones del plan ni de E0.
- Siguen vigentes los residuales del plan para la sesión Mentor: R1 (cita de 5 líneas, sin deuda), R2 (`TokenData.role`
  sin uso), R3 (BE-50 ya tiene fila) y R4 (cierre de documentos tras el merge; el PR declara el `BREAKING CHANGE` y los 30
  minutos; si AGENTS §5 nombra `sign_claims` y corrige `auth_headers` por `make_auth_headers`, decisión de David).

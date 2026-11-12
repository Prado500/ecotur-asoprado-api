# Handoff — BE-42 · Fase A (una constante para el `scope` de verificación)

- Commit de la fase: `db6bc51` — `refactor(auth): name the email verification scope in one constant`
- Rama: `item/be-42`, sobre `fed1f7c` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. HEAD `fed1f7c`. `current_target` = `Fase_A`. Sin `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `deb0b1e`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `deb0b1e`; `Base develop` de `verificacion.md` = `deb0b1e`.
- Compuerta antes de tocar nada (exit 0), idéntica a la línea base de la verificación:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `618 passed, 8 warnings` · `TOTAL 961 19 136 16 96.81%`.

## Archivos tocados (los 2 de la fase)

`git show --stat db6bc51`:

```
 app/core/security.py         | 6 +++++-
 app/services/user_service.py | 3 ++-
 2 files changed, 7 insertions(+), 2 deletions(-)
```

Resumen del diff, todo dictado por el plan:

1. `app/core/security.py`: tras el bloque `"""` / `    TOKEN FACTORY` / `"""`, una línea en blanco, las dos líneas de
   comentario y `EMAIL_VERIFICATION_SCOPE = "email_verification"`, dos líneas en blanco y `def create_access_token`.
   En `create_verification_token`: `to_encode = {"sub": email, "scope": EMAIL_VERIFICATION_SCOPE, "exp": expire}`.
2. `app/services/user_service.py`: `EMAIL_VERIFICATION_SCOPE,` como primer nombre del import partido de
   `app.core.security`; en `verify_email_account`, `if email is None or scope != EMAIL_VERIFICATION_SCOPE:`. Nada más
   cambia en el método.

No se tocaron `create_access_token`, `ACCESS_TOKEN_SCOPE`, los docstrings de un solo uso ni `activate_user`.

## Tests

Sin RED posible (refactor sin cambio de comportamiento, como dicta el plan). No se añadió ni modificó ningún test.
Checklist `test-sanitizer`: no aplica, no se tocó ningún test.

## Mutantes (procedimiento común; un directorio nuevo del scratchpad por mutante, `git archive`)

Cada edición se comprobó con `sed -n` en la copia antes de correr la suite.

- MV en la base (`fed1f7c`, forma literal; `sed -n 137p` → `        if email is None:`):
  ```
  FAILED tests/test_user_service.py::test_verify_email_wrong_scope_raises_invalid_verification_token
  1 failed, 328 passed, 8 warnings in 10.28s
  ```
- MV tras A (`db6bc51`; `sed -n 138p app/services/user_service.py` → `        if email is None:`):
  ```
  FAILED tests/test_user_service.py::test_verify_email_wrong_scope_raises_invalid_verification_token
  1 failed, 328 passed, 8 warnings in 13.91s
  ```
- MEV tras A (`db6bc51`; `sed -n 51p app/core/security.py` → `EMAIL_VERIFICATION_SCOPE = "verification"`):
  ```
  FAILED tests/test_user_service.py::test_register_tourist_returns_registration_result
  1 failed, 328 passed, 8 warnings in 12.36s
  ```
- Copia sin mutante (`db6bc51`): `329 passed, 8 warnings in 10.16s`, como la fila A.

Los tres coinciden con el plan.

## Criterio de aceptación

```
$ git show --numstat --format= db6bc51
5	1	app/core/security.py
2	1	app/services/user_service.py
$ git grep -n '"email_verification"' -- app | wc -l
1
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

- pytest: `618 passed, 8 warnings in 21.24s` (0 failed). Cobertura: `TOTAL 962 19 136 16 96.81%` ·
  `Total coverage: 96.81%` (= base).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Sobre los dos archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already
  formatted`; `mypy` → `Success: no issues found in 2 source files`.
- Coincide con la fila A del plan (618 passed, 96,81 %, 962 stmts).

## Residuales y dudas

- Ninguno nuevo. El hook de ruff (`F401` autofix) eliminó el import `EMAIL_VERIFICATION_SCOPE` de `user_service.py`
  porque se añadió antes que su uso, y reportó `F821` al editar la comparación; se volvió a añadir el import y el estado
  final está limpio (diff `2	1`, como dicta el plan).
- Sin desviaciones del plan ni de E0.

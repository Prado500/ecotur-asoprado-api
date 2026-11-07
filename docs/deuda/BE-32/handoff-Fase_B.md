# Handoff — BE-32 Fase_B: `tests/` entra en mypy, con los otros 5 errores de BE-32 en 0

**Commit de la fase:** `d8848db` (`chore(mypy): check tests/ in the gate and clear the suite's own errors`). El mensaje es
el del plan letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:**
`/implementar BE-32 Fase_C`.

## Archivos tocados

`git show --stat d8848db`:

```text
 pyproject.toml             | 2 +-
 tests/conftest.py          | 2 +-
 tests/test_audit.py        | 3 ++-
 tests/test_services.py     | 3 ++-
 tests/test_user_service.py | 9 +++++----
 5 files changed, 11 insertions(+), 8 deletions(-)
```

- `pyproject.toml:94` → `files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]`.
- `tests/conftest.py:235` → `user: User = make_user(**overrides)`.
- `tests/test_services.py`: `from typing import Any` entre `decimal` y `unittest.mock`; `:139` →
  `update_payload: dict[str, Any] = {`.
- `tests/test_audit.py`: `from typing import Any` antes de `unittest.mock` (línea 1); `audit_repo(self) -> Any:`.
- `tests/test_user_service.py`: `:3` → `from datetime import UTC, datetime, timedelta`; nueva línea 4 `from typing import
  Any`; `user_repo() -> Any:` y `audit_service() -> Any:`; y **`UserRole as SchemaUserRole` sale del bloque
  parentizado a su propia sentencia** `from app.schemas.user import UserRole as SchemaUserRole` (ver Desviaciones).

## Ritual de arranque

- Árbol limpio en `item/be-32`, HEAD en `ddddb9d`. `current_target` = `Fase_B`. `gaps.md` de la fase A: PASS, sin
  bloqueantes.
- `git fetch origin` correcto. `origin/develop` = `fd144ad`; `merge-base HEAD origin/develop` = `fd144ad`; `Base develop`
  de `verificacion.md` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `547 passed, 5 warnings`, 96.11 %, ruff `Found 9 errors.`, mypy `Found 5 errors
  in 4 files (checked 35 source files)`, `Contracts: 4 kept, 0 broken.`, `57 files already formatted`. Coincide con la
  fila A.

## RED (de herramienta): solo `pyproject.toml` cambiado

`./venv/Scripts/python.exe scripts/check.py` (exit 1), líneas `error:` de mypy (filtradas por `error:`, opcional de la
auditoría A; `grep -cE " error: "` = 14):

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_audit.py:72: error: Returning Any from function declared to return "AuditRepository"  [no-any-return]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:65: error: Returning Any from function declared to return "UserRepository"  [no-any-return]
tests\test_user_service.py:71: error: Returning Any from function declared to return "AuditService"  [no-any-return]
tests\test_user_service.py:103: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:197: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:274: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:292: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_services.py:157: error: Value of type "object" is not indexable  [index]
tests\conftest.py:239: error: Returning Any from function declared to return "User"  [no-any-return]
Found 14 errors in 8 files (checked 53 source files)
```

Coincide con el plan: 5 de `app/`, los 4 de A4 en `:103,197,274,292` y los 5 de BE-32.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

La corrí sobre el árbol editado justo antes del commit; solo estaban modificados los 5 archivos de la fase.

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

```text
57 files already formatted
Found 8 errors.
Found 9 errors in 5 files (checked 53 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
547 passed, 5 warnings in 22.31s
```

mypy, los 9 (`error:`), el conjunto exacto de A4:

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:104: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:198: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:275: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:293: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
```

Las 4 de `tests/` por contenido (`grep -n "SECRET_KEY" tests/test_user_service.py`):

```text
104:    claims = jwt.decode(result.verification_token, SECRET_KEY, algorithms=[ALGORITHM])
198:    claims = jwt.decode(result.access_token, SECRET_KEY, algorithms=[ALGORITHM])
275:        SECRET_KEY,
293:        SECRET_KEY,
```

Ruff (`ruff check . --output-format=concise`): solo los 8 I001 `:1:1` de `app/` (`dependencies.py`, `routers/audit.py`,
`core/email.py`, `db/database.py`, `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`,
`services/user_service.py`). `./venv/Scripts/python.exe -m ruff check tests/` → `All checks passed!`.

| Métrica | Fila A | Fase_B | Criterio (fila B) |
|---|---|---|---|
| pytest | 547 passed | 547 passed | 547 passed |
| Cobertura | 96.11 % | 96.11 % | ≥ 96.11 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 9 | 8 | 8 (solo `app/`) |
| mypy | 5 en 4 archivos, 35 fuentes | 9 en 5 archivos, 53 fuentes | 9 en 5, 53; tests en 104/198/275/293 |

Archivos tocados: `ruff check` sobre los 5 → `All checks passed!`. `mypy tests/conftest.py tests/test_services.py
tests/test_audit.py` → `Found 5 errors in 4 files (checked 3 source files)`, ninguno en esos archivos (son los de `app/`,
por imports). `mypy tests/test_user_service.py` → los 5 de `app/` y los 4 de A4 del archivo (excepción de la decisión 5).

## Checklist `test-sanitizer`

Solo cambian anotaciones de tipo e importaciones; ningún test cambia lo que afirma. Los fixtures siguen devolviendo
dobles `create_autospec(..., instance=True)`; `-> Any` solo quita el `no-any-return`. Nada que corregir.

## Residuales

- Rojo heredado de A4: ruff 8 (I001 de `app/`) y mypy 9 (5 de `app/` y 4 `SECRET_KEY` de `test_user_service.py`). No se
  tocó.

## Desviaciones y dudas

- **I001 de `test_user_service.py:3`: el cambio exacto del plan no bastaba.** Con solo `UTC, datetime, timedelta` y
  `typing.Any`, ruff seguía dando `I001` en `:3:1`. La base tenía dos causas, no una. La segunda es que la configuración
  de isort no combina alias (`combine-as-imports` desactivado por defecto), así que `UserRole as SchemaUserRole` debe ir en
  su propia sentencia. Prueba en una copia en el scratchpad (`ruff check --isolated --line-length 100 --select I
  --config "lint.isort.known-first-party=['app']" --diff`) sobre `HEAD:tests/test_user_service.py`:
  ```diff
  -from datetime import datetime, timedelta, UTC
  +from datetime import UTC, datetime, timedelta
  ...
       UserLogin,
  +    UserUpdate,
  +)
  +from app.schemas.user import (
       UserRole as SchemaUserRole,
  -    UserUpdate,
   )
  ```
  Escribí la sentencia del alias **en una línea** (`from app.schemas.user import UserRole as SchemaUserRole`). Ruff la
  acepta (`All checks passed!`) y así el bloque conserva sus 7 líneas, de modo que las líneas de A4 quedan exactamente
  en 104/198/275/293, como dice la tabla. La forma parentizada que propone ruff habría movido A4 una línea más (105/…)
  y habría roto la tabla de B y la de D. Es la única edición fuera de la lista literal; no cambia ninguna cifra del plan
  y cumple P3 y el criterio `ruff check tests/` → `All checks passed!`. El cuerpo del commit dice «sort the datetime
  import (the only I001 in tests/)», tal como lo dicta el plan; no menciona el alias.
- **Hook de ruff y F401:** al añadir `from typing import Any` antes de usarlo, el hook (`ruff check --fix`) lo borró
  por F401. Lo reañadí cuando los usos ya existían. El resultado es el mismo, pero conviene saberlo para las fases C–H:
  primero el uso y luego la importación.
- `Base develop` vigente (`fetch` correcto); sin otras desviaciones.

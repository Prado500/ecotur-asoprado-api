# Handoff — BE-33 Fase_C: autenticación y cuentas: causa de errores JWT, tipado y textos

**Commit de la fase:** `0c076b4` (`fix(auth): chain JWT errors as causes and correct token typing`), mensaje letra a letra
del plan con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:** `/implementar BE-33 Fase_D`.

## Archivos tocados

`git show --stat --format= 0c076b4` y `git show --numstat --format= 0c076b4`:

```text
 app/api/dependencies.py            |  28 ++++---
 app/schemas/token.py               |   5 +-
 app/services/user_access_policy.py |  32 ++++---
 app/services/user_service.py       |  24 ++++--
 tests/test_token_failure_paths.py  | 166 +++++++++++++++++++++++++++++++++++++
 5 files changed, 219 insertions(+), 36 deletions(-)
16	12	app/api/dependencies.py
3	2	app/schemas/token.py
19	13	app/services/user_access_policy.py
15	9	app/services/user_service.py
166	0	tests/test_token_failure_paths.py
```

## Ritual de arranque

- Árbol limpio, rama `item/be-33`, HEAD `064821d`. `current_target` = `Fase_C`. `gaps.md` sin hallazgos [BLOQUEANTE].
- `git fetch origin` sin error. `origin/develop` = `bab25c2`; `merge-base HEAD origin/develop` = `bab25c2`; `Base develop`
  de `verificacion.md` = `bab25c2`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 1), igual al cierre de la fase B:

```text
55 files already formatted
Found 41 errors.
Found 9 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
421 passed, 5 warnings in 16.23s
```

## RED

`./venv/Scripts/python.exe -m pytest tests/test_token_failure_paths.py -q --no-cov`, con el test escrito y `app/` sin tocar:

```text
.......FFFF                                                              [100%]
E       AssertionError: assert <class 'NoneType'> is <class 'jwt.exceptions.ExpiredSignatureError'>
E       AssertionError: assert <class 'NoneType'> is <class 'jwt.exceptions.DecodeError'>
E       AssertionError: assert <class 'NoneType'> is <class 'jwt.exceptions.ExpiredSignatureError'>
E       AssertionError: assert <class 'NoneType'> is <class 'jwt.exceptions.DecodeError'>
FAILED tests/test_token_failure_paths.py::test_get_current_user_chains_the_jwt_error_as_cause[expired]
FAILED tests/test_token_failure_paths.py::test_get_current_user_chains_the_jwt_error_as_cause[corrupt]
FAILED tests/test_token_failure_paths.py::test_verify_email_chains_the_jwt_error_as_cause[expired]
FAILED tests/test_token_failure_paths.py::test_verify_email_chains_the_jwt_error_as_cause[corrupt]
4 failed, 7 passed in 0.39s
```

Los cuatro fallan en la aserción de `__cause__`, que es lo que añade `from err`, no por un error de preparación. Los 7 HTTP
pasan antes y después: son de caracterización (decisión 7).

## GREEN

El mismo comando, tras el cambio:

```text
...........                                                              [100%]
11 passed in 0.23s
```

## Mutaciones

Todas sobre `app/api/dependencies.py`, restaurando desde la copia y comprobando el hash tras cada una.

**M1, la del plan** (`sed -i 's/HTTP_401_UNAUTHORIZED/HTTP_403_FORBIDDEN/'`):

```text
FAILED tests/test_token_failure_paths.py::test_expired_token_on_protected_route_returns_401
FAILED tests/test_token_failure_paths.py::test_corrupt_token_on_protected_route_returns_401
FAILED tests/test_token_failure_paths.py::test_token_without_subject_returns_401
FAILED tests/test_token_failure_paths.py::test_token_for_unknown_user_returns_401
FAILED tests/test_token_failure_paths.py::test_token_for_inactive_user_returns_401
FAILED tests/test_token_failure_paths.py::test_get_current_user_chains_the_jwt_error_as_cause[expired]
FAILED tests/test_token_failure_paths.py::test_get_current_user_chains_the_jwt_error_as_cause[corrupt]
7 failed, 4 passed in 0.61s
```

**M2, extra** (la rama de token vencido responde con el `detail` genérico). M1 no ejercita `distinct_details`, así que su no
vacuidad quedaba sin demostrar:

```text
FAILED tests/test_token_failure_paths.py::test_expired_and_corrupt_tokens_get_distinct_details
1 failed, 10 passed in 0.45s
```

**M3, extra** (los dos `detail` intercambiados entre ramas; `grep` confirmó que la mutación se aplicó):

```text
11 passed in 0.19s
```

**M3 sobrevive.** Ver "Residuales".

Restauración, igual tras M1, M2 y M3, y `numstat` del archivo de nuevo en `16 12`:

```text
f77aa10d3ffe1424ace4129617745bf49d067b94ea04e69f8170b381f3aa0fb8 *app/api/dependencies.py
```

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Corrida sobre el commit `0c076b4`, con el árbol limpio:

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
56 files already formatted
Found 20 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
app\api\dependencies.py                       53      1      6      0  98.31%   63
TOTAL                                        943     27    138     19  95.74%
432 passed, 5 warnings in 12.64s
```

`ruff check . --statistics` (corrido sobre el árbol de trabajo justo antes del commit, con el mismo contenido):

```text
9	I001	unsorted-imports
8	E501	line-too-long
3	W293	blank-line-with-whitespace
Found 20 errors.
```

`mypy` (ídem). Son exactamente los 5 de A4 que V4 espera, con `dependencies.py:92` ya en `:95`:

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
Found 5 errors in 4 files (checked 35 source files)
```

| Métrica | Fase_B | Fase_C | Criterio |
|---|---|---|---|
| pytest | 421 passed | 432 passed | 432 passed |
| Cobertura | 94.82 % | 95.74 % | ≥ 94.82 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 41 | 20 | 20 |
| mypy total | 9 en 4 archivos | 5 en 4 archivos | 5 |
| Missing de `dependencies.py` | `63, 95, 98-105, 111` | `63` | `63` |

## Conjuntos por archivo (decisión 2)

`ruff check <los 5> --output-format=concise` sobre `0c076b4`:

```text
app\api\dependencies.py:1:1: I001 Import block is un-sorted or un-formatted
app\services\user_service.py:1:1: I001 Import block is un-sorted or un-formatted
Found 2 errors.
```

`ruff format --check <los 5>`: `5 files already formatted`. `mypy tests/test_token_failure_paths.py | grep -c '^tests'`: `0`.

| Archivo | Ruff después | Mypy después | Decisión 2 |
|---|---|---|---|
| `app/api/dependencies.py` | I001 l.1 | l.95 (`str \| None`) | cumple |
| `app/schemas/token.py` | 0 | 0 | cumple |
| `app/services/user_service.py` | I001 l.1 | l.124 | cumple |
| `app/services/user_access_policy.py` | 0 | 0 | cumple |
| `tests/test_token_failure_paths.py` (nuevo) | 0 | 0 líneas `^tests` | cumple |

## Criterios restantes

V5: la primera búsqueda da 0 líneas; la segunda, 3 (1 en `dependencies.py`, 2 en `user_service.py`):

```text
app/api/dependencies.py:96:        email: str | None = payload.get("sub")
app/services/user_service.py:134:        email: str | None = payload.get("sub")
app/services/user_service.py:135:        scope: str | None = payload.get("scope")
```

V7: 4 con `from err` y 4 con `as err`:

```text
app/api/dependencies.py:106:        ) from err
app/api/dependencies.py:108:        raise credentials_exception from err
app/services/user_service.py:128:            ) from err
app/services/user_service.py:132:            ) from err
app/api/dependencies.py:101:    except jwt.ExpiredSignatureError as err:
app/api/dependencies.py:107:    except jwt.InvalidTokenError as err:
app/services/user_service.py:125:        except jwt.ExpiredSignatureError as err:
app/services/user_service.py:129:        except jwt.InvalidTokenError as err:
```

V8, los dos de esta fase: `usuario` en `dependencies.py` y `email: str | None` en `token.py`, 0 líneas. Silenciadores, los 4
UP042 de siempre:

```text
app/models/audit.py:13:class AuditAction(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/models/service.py:12:class ServiceCategory(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/models/user.py:11:class UserRole(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/schemas/user.py:7:class UserRole(str, Enum):  # noqa: UP042 (backlog D2)
```

V9, script literal del plan sobre `0c076b4`. `code=same` en `user_access_policy.py` y `strings=exact` en los cuatro archivos
de la fase: ningún texto de usuario cambió. Los `changed` son los de las decisiones 4, 5, 6 y 9; `email.py` sigue en
`exact` porque es de la fase D:

```text
app/api/dependencies.py                      code=changed  strings=exact
app/core/email.py                            code=same     strings=exact
app/db/database.py                           code=same     strings=exact
app/repositories/audit_repository.py         code=same     strings=exact
app/repositories/service_repository.py       code=changed  strings=exact
app/repositories/user_repository.py          code=same     strings=exact
app/schemas/audit.py                         code=same     strings=exact
app/schemas/token.py                         code=changed  strings=exact
app/services/user_access_policy.py           code=same     strings=exact
app/services/user_service.py                 code=changed  strings=exact
```

## Checklist `test-sanitizer`

Aplicado solo como checklist (estándares 1-5 del skill):

1. Mocks: `create_autospec(..., instance=True)` en `UserRepository` y `AuditService`.
2. Fixtures DRY: usa `persist_user`, `make_auth_headers` y `client` de `conftest.py`. Los tokens sin usuario o con caducidad
   pasan por `create_access_token`, porque `make_token` no admite claims (análisis, punto 6; residual 4 del plan).
3. Inglés: nombres, docstrings y aserciones. Ninguna aserción lee texto en español: `distinct_details` compara dos `detail`
   sin leerlos.
4. Contratos de datos: `_assert_bearer_401` fija código, `WWW-Authenticate` y `set(body) == {"detail"}`.
5. ABAC: no aplica, esta fase no cambia reglas de acceso. Los textos de `user_access_policy.py` no cambian (V9).

## Residuales

- **`test_expired_and_corrupt_tokens_get_distinct_details` no demuestra todo lo que dice la tabla del plan.** La columna
  "Cubre" dice "ramas no intercambiadas", pero M3 (los dos `detail` intercambiados) sobrevive en este archivo: el test
  demuestra que los dos textos son distintos (M2 lo mata), no cuál corresponde a cada rama. Detectar el cruce obliga a leer
  el texto, y AGENTS §5 lo prohíbe, o a exponer un código de error en la respuesta, que es un cambio de contrato fuera de
  esta fase. No se añadió ninguna aserción. Solo se corrió este archivo contra M3, no la suite completa.
- Rojo heredado de la compuerta: ruff 20 y mypy 5. Son la fase D y A4; sin tocar.
- El hook de edición salió con código 2 en las ediciones de `dependencies.py`, `user_service.py` y `user_access_policy.py`:
  listaba I001 (esperado, decisión 2) y los errores de las ediciones aún pendientes. Estado final: la tabla de arriba.
- `/openapi.json` no se midió en esta fase. El plan (análisis, punto 3) espera solo el cambio de `description` de
  `TokenResponse`, medido en la sonda y aceptado en E0.

## Desviaciones y dudas

Sin desviaciones en `app/`: los cambios son los textos del plan y el `numstat` coincide en los cuatro archivos. En lo que
el plan deja al ejecutor o no precisa:

- **Helpers locales `_expired_token`, `_corrupt_token` y `_bearer`.** El plan pide tokens "construidos dentro del test". Los
  helpers se llaman durante el test, no al importar, y evitan repetirlos en los casos parametrizados; ninguno usa
  `SECRET_KEY`.
- **`AuditService` también va con autospec.** El plan solo nombra el doble de `UserRepository`, pero el constructor de
  `UserService` exige un `AuditService`; la política es la real.
- **`test_expired_token_on_protected_route_returns_401` usa un usuario persistido y activo,** de modo que solo la caducidad
  separa ese token de un 200.
- **`distinct_details` no afirma el código HTTP,** a propósito: con él, M1 daría `8 failed, 3 passed` y no el `7 failed,
  4 passed` que dicta el plan.
- **Dos mutaciones que el plan no pedía** (M2 y M3), restauradas igual que M1.

Incidencias durante la ejecución, ninguna en el contenido del commit:

- **Edición paralela de David.** Con la fase en curso aparecieron sin commitear `docs/deuda/BE-33/plan.md` (enmienda E2),
  `docs/bitacora/2026-11-06.md` y `docs/aprendizaje/fichas/BE-33.md`; después entraron como `9c3cd3c`, `88b47e4` y
  `7f8a103`. Al arrancar el árbol estaba limpio, así que no se activó la parada del ritual. Se leyó el diff: E2 no cambia
  la fase C ("no a la fase C, cuyos totales están dictados"). No se tocaron ni se añadieron al commit.
- **Sobrescribí un archivo del scratchpad compartido.** Escribí el script V9 en `scratchpad/v9.py` sin comprobar antes si
  existía, y existía desde las 10:46:56 (fecha de creación de NTFS). Su contenido anterior no es recuperable y no lo
  restauré por suposición. El actual es el script literal del plan e iguala, salvo fin de línea, a `audit-be33-b/v9.py`;
  nada en `docs/` lo referencia. Fuera del repo. El resto de los temporales está en el subdirectorio nuevo
  `scratchpad/fase-c-be33-ejecutor/`.

# Handoff — BE-33 Fase_D: correo de verificación y cadena de `database.py`

**Commit de la fase:** `c60ad12` (`style(email): wrap the verification HTML at its existing spaces`), mensaje letra a letra
del plan con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:** `/auditar BE-33 Fase_D`. Última fase
del plan.

## Archivos tocados

`git show --stat --format= c60ad12` y `git show --numstat --format= c60ad12`:

```text
 app/core/email.py   |  52 +++++++++++++++++-----
 app/db/database.py  |   2 +-
 tests/test_email.py | 126 ++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 169 insertions(+), 11 deletions(-)
42	10	app/core/email.py
1	1	app/db/database.py
126	0	tests/test_email.py
```

## Ritual de arranque

- Árbol limpio, rama `item/be-33`, HEAD `0f9e178`. `current_target` = `Fase_D`. `gaps.md` sin hallazgos [BLOQUEANTE].
- `git fetch origin` sin error. `origin/develop` = `bab25c2`; `merge-base HEAD origin/develop` = `bab25c2`; `Base develop`
  de `verificacion.md` = `bab25c2`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 1), igual al cierre de la fase C:

```text
56 files already formatted
Found 20 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
app\core\email.py                             12      4      0      0  66.67%   29-82
TOTAL                                        943     27    138     19  95.74%
432 passed, 5 warnings in 11.91s
```

## Tests de caracterización

`./venv/Scripts/python.exe -m pytest tests/test_email.py -q --no-cov`. No hay RED: el plan los define como caracterización.

**Antes de editar** (`git status --short` mostraba solo `?? tests/test_email.py`; `app/` sin tocar):

```text
......                                                                   [100%]
6 passed in 0.15s
```

**W293**, con el comando exacto del plan, primer cambio en `app/`:

```text
Found 3 errors (3 fixed, 0 remaining).
```

**Después de editar** (W293 y las sustituciones de `email.py`):

```text
......                                                                   [100%]
6 passed in 0.12s
```

## Mutación controlada

Copia de `email.py` al temporal; `<a href="{verification_link}"` → `<a href="#"`; test; restauración desde la copia.

```text
88:                    <a href="#" class="btn"
E       assert 1 == 2
FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
1 failed, 5 passed in 0.25s
```

Restauración: mismo SHA-256 antes y después, el mismo que `git show c60ad12:app/core/email.py`. Tras restaurar, `numstat`
`42 10` y `6 passed`.

```text
before: dec6009865e14501550ca4f83549c0f7e1eef410f6471dbe745b537fa769037d *-
after:  dec6009865e14501550ca4f83549c0f7e1eef410f6471dbe745b537fa769037d *-
RESTORED_IDENTICAL
88:                    <a href="{verification_link}" class="btn"
```

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Corrida sobre el commit `c60ad12`, con el árbol limpio:

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
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
app\api\dependencies.py                       53      1      6      0  98.31%   63
TOTAL                                        943     23    138     19  96.11%
438 passed, 5 warnings in 12.58s
```

`email.py` no aparece en la tabla porque la compuerta usa `term-missing:skip-covered`. Medido aparte con
`pytest tests/test_email.py --cov=app.core.email --cov-report=term-missing`:

```text
app\core\email.py      12      0      0      0  100.00%
```

| Métrica | Fase_C | Fase_D | Criterio |
|---|---|---|---|
| pytest | 432 passed | 438 passed | 438 passed |
| Cobertura | 95.74 % | 96.11 % | ≥ 94.82 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 20 | 9 | 9 |
| mypy total | 5 en 4 archivos | 5 en 4 archivos | 5 |
| Missing de `email.py` | `29-82` | ninguno (100 %) | 100 % |
| Formato | 56 | 57 | 57 (E1) |

## Conjuntos por archivo (decisión 2)

`ruff check app/core/email.py app/db/database.py tests/test_email.py --output-format=concise`:

```text
app\core\email.py:1:1: I001 Import block is un-sorted or un-formatted
app\db\database.py:1:1: I001 Import block is un-sorted or un-formatted
Found 2 errors.
```

`ruff format --check` de los tres: `3 files already formatted`. `mypy tests/test_email.py | grep -c '^tests'`: `0`.

| Archivo | Ruff después | Mypy después | Decisión 2 |
|---|---|---|---|
| `app/core/email.py` | I001 l.1 | 0 | cumple |
| `app/db/database.py` | I001 l.1 | l.11 | cumple |
| `tests/test_email.py` (nuevo) | 0 | 0 líneas `^tests` | cumple |

## Verificación final, sobre `c60ad12`

V1, `All checks passed!`. V2, los 9 I001:

```text
app\api\dependencies.py:1:1: I001 Import block is un-sorted or un-formatted
app\api\routers\audit.py:1:1: I001 Import block is un-sorted or un-formatted
app\core\email.py:1:1: I001 Import block is un-sorted or un-formatted
app\db\database.py:1:1: I001 Import block is un-sorted or un-formatted
app\repositories\user_repository.py:1:1: I001 Import block is un-sorted or un-formatted
app\schemas\audit.py:1:1: I001 Import block is un-sorted or un-formatted
app\services\audit_service.py:1:1: I001 Import block is un-sorted or un-formatted
app\services\user_service.py:1:1: I001 Import block is un-sorted or un-formatted
tests\test_user_service.py:3:1: I001 Import block is un-sorted or un-formatted
Found 9 errors.
```

V3, 0 líneas. V4, las 5 de A4 y el total esperado:

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
Found 5 errors in 4 files (checked 35 source files)
```

V5, 0 líneas y 3 líneas; V6, 1 `first()` y 2 `scalar_one()`; V7, 4 y 4:

```text
app/api/dependencies.py:96:        email: str | None = payload.get("sub")
app/services/user_service.py:134:        email: str | None = payload.get("sub")
app/services/user_service.py:135:        scope: str | None = payload.get("scope")
app/repositories/service_repository.py:75:        return result.scalars().first()
app/repositories/service_repository.py:26:        return result.scalar_one()
app/repositories/service_repository.py:97:        return result.scalar_one()
app/api/dependencies.py:106:        ) from err
app/api/dependencies.py:108:        raise credentials_exception from err
app/services/user_service.py:128:            ) from err
app/services/user_service.py:132:            ) from err
app/api/dependencies.py:101:    except jwt.ExpiredSignatureError as err:
app/api/dependencies.py:107:    except jwt.InvalidTokenError as err:
app/services/user_service.py:125:        except jwt.ExpiredSignatureError as err:
app/services/user_service.py:129:        except jwt.InvalidTokenError as err:
```

V8, 0, 0, 0, y los 4 UP042:

```text
app/models/audit.py:13:class AuditAction(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/models/service.py:12:class ServiceCategory(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/models/user.py:11:class UserRole(str, enum.Enum):  # noqa: UP042 (backlog D2)
app/schemas/user.py:7:class UserRole(str, Enum):  # noqa: UP042 (backlog D2)
```

V9, script extraído de `plan.md` por programa. Coincide con la tabla esperada del plan:

```text
app/api/dependencies.py                      code=changed  strings=exact
app/core/email.py                            code=same     strings=whitespace-only
app/db/database.py                           code=same     strings=exact
app/repositories/audit_repository.py         code=same     strings=exact
app/repositories/service_repository.py       code=changed  strings=exact
app/repositories/user_repository.py          code=same     strings=exact
app/schemas/audit.py                         code=same     strings=exact
app/schemas/token.py                         code=changed  strings=exact
app/services/user_access_policy.py           code=same     strings=exact
app/services/user_service.py                 code=changed  strings=exact
```

V10, 13 archivos y `numstat` de `app/` igual a los criterios de cada fase:

```text
app/api/dependencies.py
app/core/email.py
app/db/database.py
app/repositories/audit_repository.py
app/repositories/service_repository.py
app/repositories/user_repository.py
app/schemas/audit.py
app/schemas/token.py
app/services/user_access_policy.py
app/services/user_service.py
tests/test_email.py
tests/test_service_repository.py
tests/test_token_failure_paths.py
16	12	app/api/dependencies.py
42	10	app/core/email.py
1	1	app/db/database.py
3	2	app/repositories/audit_repository.py
23	9	app/repositories/service_repository.py
3	2	app/repositories/user_repository.py
2	6	app/schemas/audit.py
3	2	app/schemas/token.py
19	13	app/services/user_access_policy.py
15	9	app/services/user_service.py
```

V11, 6, 5 y 9 funciones; 0 líneas `^tests` en mypy:

```text
tests/test_email.py:6
tests/test_service_repository.py:5
tests/test_token_failure_paths.py:9
22 passed in 0.37s
```

V12: la compuerta de arriba. Exit 1 solo por `ruff check` y `mypy`.

## Checklist `test-sanitizer`

Aplicado solo como checklist (estándares 1-5 del skill):

1. Mocks: `patch.object(email_module.fast_mail, "send_message", autospec=True)`; solo se dobla SMTP.
2. Fixtures DRY: el archivo no crea usuarios ni tokens; el fixture `send_message` y los helpers son locales al módulo.
3. Inglés: nombres, docstrings y aserciones. `"María José"` es la entrada del test, no texto de la aplicación. Ninguna
   aserción lee texto en español del correo.
4. Contratos de datos: destinatarios, `subtype`, `href`, `class` y `style` del `<a>`, y número de llaves.
5. ABAC: no aplica.

## Residuales

- **Revisión visual del correo: pendiente de David antes de `/pr` (E0, punto 3).** Ningún agente la hizo. `tests/test_email.py`
  demuestra estructura y V9 que el cuerpo solo difiere en espacios; nada aquí lo pintó en un navegador o cliente de correo.
- **Rojo restante de la compuerta:** ruff 9 (8 I001 en `app/`, de A4, y `tests/test_user_service.py:3`, de BE-32) y mypy 5
  (A4). Sin tocar. BE-33 cierra con la compuerta en rojo, como dice el plan.
- **Límites de los tests, ninguno contra la tabla del plan:**
  - `assert_awaited_once_with(message)` compara contra el mismo objeto capturado de la llamada. Fija que hubo un solo `await`
    con un solo argumento posicional; el contenido lo fijan las demás aserciones.
  - `isinstance(message.subject, str)` ya lo garantiza Pydantic; la que actúa es la de no vacío.
  - Solo se midió la mutación del plan. La fijación del segundo enlace (texto plano) se apoya en `count == 2`; no se corrió
    una mutación sobre él.
- El hook de edición salió con código 2 en las cinco ediciones de `email.py`: listaba I001 (esperado, decisión 2) y las E501
  aún pendientes. La última listaba solo I001.
- Los residuales 2 a 6 del plan siguen a cargo del cierre de David.

## Desviaciones y dudas

Sin desviaciones en `app/`: los textos son los del plan y el `numstat` coincide. En lo que el plan deja al ejecutor o no
precisa:

- **Helpers locales `_AnchorCollector` y `_send_and_capture`,** además del que estrecha el cuerpo (`_body_of`), y fixture
  `send_message`. El plan pide `html.parser` y un helper de estrechamiento, sin fijar nombres.
- **`current_target` queda en `Auditoria`,** no en `null`: el plan no tiene más fases, y es el valor que usaron BE-02, BE-15 y
  AF-05 tras su última fase. `null` marca el ítem como hecho en `check_docs.py --estado`, y aún falta la auditoría de esta fase.
- **Comandos de V3, V4 y V11 con cambios de forma:** V3 con `grep -c`, V4 con la salida de mypy en un archivo intermedio y el
  pytest de V11 con `--no-cov`. El filtro es el mismo.
- **La compuerta se corrió también antes del commit,** con los mismos conteos que la de arriba.
- **Temporales:** todos en `scratchpad/fase-d-be33-ejecutor/`, creado tras comprobar que no existía. Nada en la raíz del
  scratchpad.

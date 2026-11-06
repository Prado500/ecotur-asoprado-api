# Handoff — BE-33 Fase_B: `save_service` falla donde se rompe la invariante

**Commit de la fase:** `b9a8907` (`fix(service-repository): raise when save_service finds no row`), mensaje letra a letra
del plan con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:** `/implementar BE-33 Fase_C`.

## Archivos tocados

`git show --stat --format= b9a8907` y `git show --numstat --format= b9a8907`:

```text
 app/repositories/service_repository.py |  32 +++++++---
 tests/test_service_repository.py       | 107 +++++++++++++++++++++++++++++++++
 2 files changed, 130 insertions(+), 9 deletions(-)
23	9	app/repositories/service_repository.py
107	0	tests/test_service_repository.py
```

## Ritual de arranque

- Árbol limpio, rama `item/be-33`, HEAD `dd1ecc0`. `current_target` = `Fase_B`. `gaps.md` sin hallazgos [BLOQUEANTE].
- `git fetch origin` sin error. `origin/develop` = `bab25c2`; `merge-base HEAD origin/develop` = `bab25c2`; `Base develop`
  de `verificacion.md` = `bab25c2`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 1):

```text
54 files already formatted
Found 49 errors.
Found 10 errors in 5 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
416 passed, 5 warnings in 16.91s
```

Igual a la salida de la fase A. Los 54 archivos (frente a los 53 de `verificacion.md`) son los que explica la enmienda E1.

## RED

`./venv/Scripts/python.exe -m pytest tests/test_service_repository.py -q --no-cov`, con el test escrito y
`service_repository.py` sin tocar:

```text
.FF..                                                                    [100%]
E       Failed: DID NOT RAISE <class 'sqlalchemy.exc.NoResultFound'>
tests\test_service_repository.py:67: Failed
E       Failed: DID NOT RAISE <class 'sqlalchemy.exc.NoResultFound'>
tests\test_service_repository.py:79: Failed
FAILED tests/test_service_repository.py::test_save_service_raises_when_the_row_never_existed
FAILED tests/test_service_repository.py::test_save_service_raises_when_the_row_was_physically_deleted
2 failed, 3 passed in 0.47s
```

Los dos fallan por la razón que corrige la fase, no por un error de preparación.

## GREEN

El mismo comando, tras el cambio:

```text
.....                                                                    [100%]
5 passed in 0.09s
```

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Corrida sobre el árbol con los dos archivos de la fase, justo antes del commit; el commit contiene exactamente ese
contenido (solo esos dos archivos figuraban en `git status --short`).

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
55 files already formatted
Found 41 errors.
Found 9 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
421 passed, 5 warnings in 16.96s
```

`ruff check . --statistics`:

```text
17	E501	line-too-long
 9	I001	unsorted-imports
 7	D205	missing-blank-line-after-summary
 4	B904	raise-without-from-inside-except
 3	W293	blank-line-with-whitespace
 1	D415	missing-terminal-punctuation
Found 41 errors.
```

`mypy`:

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:132: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\services\user_service.py:133: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\api\dependencies.py:92: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:93: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\api\dependencies.py:108: error: Argument 1 to "get_non_deleted_user_by_email" of "UserRepository" has incompatible type "str | None"; expected "str"  [arg-type]
Found 9 errors in 4 files (checked 35 source files)
```

| Métrica | Fase_A | Fase_B | Criterio |
|---|---|---|---|
| pytest | 416 passed | 421 passed | 421 passed |
| Cobertura | 94.82 % | 94.82 % | ≥ 94.82 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 49 | 41 | 41 |
| mypy total | 10 en 5 archivos | 9 en 4 archivos | 9 |

## Conjuntos por archivo (decisión 2)

`ruff check <los 2> --output-format=concise` y `ruff format --check <los 2>`, después:

```text
All checks passed!
2 files already formatted
```

`mypy <los 2>`: ninguna línea de `service_repository.py` ni de `tests`. Queda una, de un archivo que esta fase no toca y al
que llega siguiendo imports (frontera con A4):

```text
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
Found 1 error in 1 file (checked 2 source files)
```

| Archivo | Ruff antes | Ruff después | Mypy antes → después |
|---|---|---|---|
| `app/repositories/service_repository.py` | D415 l.15, 28, 38, 48, 75; D205 l.60; E501 l.18, 60 | 0 | l.83 → 0 |
| `tests/test_service_repository.py` (nuevo) | — | 0 | 0 líneas `^tests` |

## Criterios restantes

V6 (`git grep` sobre `service_repository.py`), un `first()` legítimo y dos `scalar_one()`:

```text
app/repositories/service_repository.py:75:        return result.scalars().first()
app/repositories/service_repository.py:26:        return result.scalar_one()
app/repositories/service_repository.py:97:        return result.scalar_one()
```

`is_active` en ese archivo: `0` (`grep -c`). `numstat` del archivo: `23 9`.

V9, script literal del plan. El único `changed` es el de esta fase (decisión 4); los que faltan son de las fases C y D:

```text
app/api/dependencies.py                      code=same     strings=exact
app/core/email.py                            code=same     strings=exact
app/db/database.py                           code=same     strings=exact
app/repositories/audit_repository.py         code=same     strings=exact
app/repositories/service_repository.py       code=changed  strings=exact
app/repositories/user_repository.py          code=same     strings=exact
app/schemas/audit.py                         code=same     strings=exact
app/schemas/token.py                         code=same     strings=exact
app/services/user_access_policy.py           code=same     strings=exact
app/services/user_service.py                 code=same     strings=exact
```

## Checklist `test-sanitizer`

Aplicado solo como checklist (estándares 1-5 del skill):

1. Mocks: no hay; repositorio y sesión reales.
2. Fixtures DRY: `repo` y los helpers locales `_package` y `_persist`. No se construyen usuarios ni tokens.
3. Inglés: nombres, docstrings y aserciones. El valor `"Paquete De Prueba Automatizada"` es un dato, copiado de
   `_persist_package` como pide el plan, y ninguna aserción lo lee.
4. Contratos de datos: no aplica, no hay respuesta HTTP.
5. ABAC: no aplica, no hay política de acceso en esta capa.

## Residuales

- Rojo heredado de la compuerta: ruff 41 y mypy 9. Son las fases C y D y A4; sin tocar.
- El hook de edición salió con código 2 en cinco de las siete ediciones de `service_repository.py`: en cada una, los errores
  listados eran los de las ediciones aún pendientes. El estado final es `All checks passed!`. No se usó `--unsafe-fixes`.
- Los `commit()` de `create_service` y `save_service` siguen (A3), como `== True` y `sqlalchemy.future`, fuera de alcance.

## Desviaciones y dudas

Sin desviaciones en `app/`: los ocho cambios son los textos del plan. Dos añadidos en lo que el plan deja al ejecutor:

- **Helper local `_persist`, además de `_package`.** Hace `commit` y un `refresh` limitado a columnas, de modo que `images`
  queda sin cargar. Si se cargase, `test_save_service_returns_the_row_with_its_images_loaded` pasaría aunque `save_service`
  no cargase nada. Vive en el archivo de test nuevo; no toca `conftest.py`.
- **Mutación que el plan no pedía en esta fase,** para comprobar que ese test no es vacuo: copia de `service_repository.py`
  al temporal, quitar el `selectinload` de `save_service`, ejecutar y restaurar desde la copia. El `numstat` volvió a
  `23 9` y el test a `5 passed`:

  ```text
  venv\Lib\site-packages\sqlalchemy\util\_concurrency_py3k.py:123: MissingGreenlet
  FAILED tests/test_service_repository.py::test_save_service_returns_the_row_with_its_images_loaded
  1 failed, 4 passed in 0.56s
  ```

El test de fila con borrado lógico afirma `deleted_at is not None`, no el valor exacto: es lo que pide la tabla del plan.

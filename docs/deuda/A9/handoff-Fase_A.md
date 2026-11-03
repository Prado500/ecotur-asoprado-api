# Handoff — A9 · Fase A (`UserResponse` describe el usuario guardado)

- **Fecha:** 2026-11-02 · **Rama:** `bloque/b-higiene` · **Ejecutor:** `fase-ejecutor` (Claude Opus 5.5)
- **Commits:** `4f70b0e` (A1, `style`) · `c369e3f` (A2, `fix`). Mensajes exactos del plan + trailer `Co-Authored-By`.

## Ritual de arranque

- `git status --short` vacío; `git log` con punta en `83bfd6a` (plan aprobado).
- `current_target` = `Fase_A`. No había `gaps.md`.
- Línea base: `git fetch origin` OK (refrescado). `git rev-parse --short origin/develop` = `7c6d606`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7c6d606`. Ambos iguales a `Base develop`.
- Compuerta de arranque (`venv/Scripts/python.exe scripts/check.py`): 333 passed, 92.76 %, `ruff check` 97,
  mypy 44 (12 archivos), import-linter 4 KEPT / 0 BROKEN, `142 files already formatted`. Idéntica a la verificación.

## Archivos tocados

| Commit | Archivo | Qué |
|---|---|---|
| A1 `4f70b0e` | `app/schemas/user.py` | I001 (lo aplicó el hook), `# noqa: UP042 (backlog D2)` en `UserRole`, 4 `description` repartidas con concatenación implícita, comentario de `format_title_case` en dos líneas, 3 docstrings con línea de resumen + línea en blanco + cuerpo |
| A2 `c369e3f` | `app/schemas/user.py` | `class UserResponse(BaseModel)` con docstring y los 9 campos planos del plan, `model_config = {"from_attributes": True}` intacto |
| A2 `c369e3f` | `tests/test_user_response.py` (nuevo) | 7 funciones, 14 casos |

```
$ git show --stat --format= 4f70b0e
 app/schemas/user.py | 48 ++++++++++++++++++++++++++++++++++++------------
 1 file changed, 36 insertions(+), 12 deletions(-)

$ git show --stat --format= c369e3f
 app/schemas/user.py         |  14 ++-
 tests/test_user_response.py | 207 ++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 220 insertions(+), 1 deletion(-)
```

## Neutralidad del commit `style` (A1)

- `ruff check app/schemas/user.py` → `All checks passed!` (antes: 11). `ruff format --check` → `1 file already formatted`.
- `diff openapi-0.json openapi-1.json` → vacío (rc=0); `git diff --no-index --stat` → vacío.
- `pytest -q` tras A1 → `333 passed, 1 warning in 12.06s` (igual que la línea base).

## RED (tests sobre A1, antes del cambio de A2)

```
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[hyphen]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[apostrophe]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_surname]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[66_chars]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[landline]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[11_digit_cedula]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[dotless_domain]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_domain]
FAILED tests/test_user_response.py::test_user_directory_survives_one_off_rule_record
FAILED tests/test_user_response.py::test_deleted_directory_returns_stored_names_verbatim
FAILED tests/test_user_response.py::test_patch_on_off_rule_record_returns_200_with_persisted_change
11 failed, 3 passed, 2 warnings in 1.93s
```

Motivos (extracto literal): seis casos de 1 y los tests 2, 3 y 4 lanzan
`fastapi.exceptions.ResponseValidationError` (`venv\Lib\site-packages\fastapi\routing.py:296`), p. ej.
`{'type': 'string_pattern_mismatch', 'loc': ('response', 'first_name'), ... 'input': 'Jean-Luc', ...}`.
Los dos casos de reescritura fallan por aserción:

```
E       AssertionError: assert 'Mcdonald' == 'McDonald'
E       AssertionError: assert 'Ana@example.com' == 'Ana@EXAMPLE.COM'
```

Los 3 que pasan son 5, 6 y 7 (congelan la entrada), tal como prevé el plan.

## GREEN (tras A2)

```
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[hyphen] PASSED [  7%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[apostrophe] PASSED [ 14%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_surname] PASSED [ 21%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[66_chars] PASSED [ 28%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[landline] PASSED [ 35%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[11_digit_cedula] PASSED [ 42%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[dotless_domain] PASSED [ 50%]
tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_domain] PASSED [ 57%]
tests/test_user_response.py::test_user_directory_survives_one_off_rule_record PASSED [ 64%]
tests/test_user_response.py::test_deleted_directory_returns_stored_names_verbatim PASSED [ 71%]
tests/test_user_response.py::test_patch_on_off_rule_record_returns_200_with_persisted_change PASSED [ 78%]
tests/test_user_response.py::test_registration_still_rejects_hyphenated_name PASSED [ 85%]
tests/test_user_response.py::test_registration_still_title_cases_names PASSED [ 92%]
tests/test_user_response.py::test_patch_still_rejects_hyphenated_name PASSED [100%]
======================= 14 passed, 2 warnings in 0.45s ========================
```

## Compuerta de salida (`venv/Scripts/python.exe scripts/check.py`, sobre `c369e3f`)

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

| Métrica | Línea base | Salida | Criterio |
|---|---|---|---|
| pytest | 333 passed, 0 failed | `347 passed, 3 warnings in 13.02s` | 347 ✔ |
| Cobertura total | 92.76 % | `Total coverage: 93.05%` | ≥ 92.76 ✔ |
| `app/schemas/user.py` cobertura | 84.85 % | 85.07 % | — |
| ruff format | 142 formatted | `143 files already formatted` | ✔ |
| `ruff check` total | 97 | `Found 86 errors.` | ≤ 86 ✔ |
| mypy total | 44 | `Found 44 errors in 12 files (checked 35 source files)` | ≤ 44 ✔ |
| import-linter | 4 KEPT | `Contracts: 4 kept, 0 broken.` | ✔ |

- `ruff check app/schemas/user.py tests/test_user_response.py` → `All checks passed!`;
  `ruff format --check` → `2 files already formatted`.
- `mypy app/schemas/user.py tests/test_user_response.py` → 0 líneas en esos dos archivos. Los 4 errores que imprime
  son de módulos importados no tocados (`app/db/database.py:11`, `app/models/service.py:21`, `app/models/user.py:40`,
  `app/models/audit.py:36`): deuda heredada, ya dentro de los 44.
- Los 2 warnings nuevos son el S5 conocido (`HTTP_422_UNPROCESSABLE_ENTITY` deprecado) disparado por los dos tests
  de 422 de esta fase; no es regresión.

## OpenAPI

- `diff openapi-0 openapi-1` → vacío.
- `git diff --no-index --stat openapi-1.json openapi-2.json` → `1 file changed, 1 insertion(+), 16 deletions(-)`.
- Componentes cambiados entre 1 y 2 (comparación programática de `components.schemas`): solo `['UserResponse']`; el
  resto del documento es idéntico; `required` de `UserResponse` sin cambio. Diff literal:

```
651a652
>     "description": "Serialized view of a stored user account.\n\nDeclared on BaseModel on purpose: an output DTO describes what is stored and never\nre-applies the input rules of UserBase (patterns, lengths, EmailStr, title-case),\nso a row that predates or bypasses them is still readable (backlog A9).",
654,657d654
<       "description": "Cédula de ciudadanía. Solo puede contener números del 0 al 9, y su longitud debe ser entre 6 y 10 dígitos",
<       "maxLength": 10,
<       "minLength": 6,
<       "pattern": "^\\d{6,10}$",
667,668d663
<       "description": "Correo electrónico debe ser válido",
<       "format": "email",
673,676d667
<       "description": "Nombres. Máximo 65 caracteres incluyendo un espacio en blanco entre nombres. (solo puede digitar letras, tíldes y un espacio entre palabras; todo nombre debe empezar con una letra)",
<       "maxLength": 65,
<       "minLength": 2,
<       "pattern": "^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
689,692d679
<       "description": "Apellidos. Máximo 65 caracteres incluyendo un espacio en blanco entre apellidos. (solo puede digitar letras, tíldes y un espacio entre palabras; todo apellido debe empezar con una letra)",
<       "maxLength": 65,
<       "minLength": 2,
<       "pattern": "^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
699d685
<         "pattern": "^3\\d{9}$",
706d691
<       "description": "Número de celular (debe tener 10 dígitos y comenzar por el número tres (3) )",
```

## Introspección

```
UserResponse BaseModel {} {} <class 'str'>
['cedula', 'email', 'first_name', 'last_name', 'phone', 'id', 'role', 'is_active', 'created_at']
True        # == list(UserBase.model_fields) + ['id', 'role', 'is_active', 'created_at'] (orden de antes)
{'from_attributes': True}
```

## Desviaciones y notas para el auditor

1. **Recuento 4b de la Verificación final: 23 frente a 22 en `7c6d606`.** La línea de más es el docstring de
   `UserResponse` del propio plan (`re-applies the input rules of UserBase (patterns, lengths, EmailStr, title-case),`),
   que contiene la palabra `EmailStr`. La otra diferencia del `diff` de líneas es solo el reorden I001 del import. No ha
   desaparecido ninguna regla de entrada.
2. **Grep 3 de la Verificación final (`git diff 7c6d606 --stat -- app/api/routers/ app/main.py app/models/ alembic/`)
   no sale vacío:** muestra `app/main.py | 41 +++---`. Viene de `9ce0379 fix(cors)` (SEC1, ya en la rama antes del plan),
   no de A9. `git diff 83bfd6a HEAD --stat` solo contiene `app/schemas/user.py` y `tests/test_user_response.py`.
   El auditor debería medir ese grep contra `83bfd6a` o filtrar el commit de SEC1.
3. **Docstrings de A1:** las líneas de resumen nuevas son paráfrasis cortas; el texto original sigue completo en el
   cuerpo. Los docstrings de validadores no salen en el OpenAPI (diff 0-1 vacío).
4. **Test 7:** se afirma `[e["raw_field"] for e in body["detalle"]] == ["first_name"]` (lista completa), algo más
   estricto que el `raw_field == "first_name"` del plan.
5. **Helper `_count_users(db_session: AsyncSession)`** (privado del módulo de tests) para afirmar "no queda ningún
   `User`" en el test 5; la anotación evita un `no-any-return` de mypy en el archivo nuevo.
6. **`test-sanitizer` (solo checklist):** mock de correo con `autospec=True` ✔; usuarios solo vía `persist_user` y
   cabeceras con `make_auth_headers` ✔; nombres y variables en inglés ✔; aserciones sobre códigos, claves, valores
   guardados y BD, nunca sobre texto en español ✔. El punto 4 del skill (`"detail"` en vez de `"detalle"`) no aplica:
   el handler actual responde `"detalle"` (`app/main.py`, deuda P2) y el plan lo fija así (Riesgo 3).

## Residuales

- Los ya listados en el plan (patrón de nombres, handler de `ResponseValidationError`, regla no determinista, S6 con el
  dict en `UserResponse`, `noqa: UP042` ligado a D2, BD más laxa que los formularios). Nada nuevo en código.
- Mutaciones M1-M3 no ejecutadas: son del auditor.

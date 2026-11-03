# Handoff — A9 · Fase B (`ServiceListResponse` y `ServiceDetailResponse` describen el paquete guardado)

- **Fecha:** 2026-11-02 · **Rama:** `bloque/b-higiene` · **Ejecutor:** `fase-ejecutor` (Claude Opus 5.5)
- **Commits:** `87e1942` (B1, `style`) · `f59f75e` (B2, `fix`). Mensajes exactos del plan + trailer `Co-Authored-By`.

## Ritual de arranque

- `git status --short` vacío; `git log` con punta en `f7520dd` (Fase A auditada, PASS).
- `current_target` = `Fase_B`. `gaps.md` sin bloqueantes; sus 4 opcionales no se tocan en esta fase.
- Línea base: `git fetch origin` OK (refrescado). `git rev-parse --short origin/develop` = `7c6d606`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7c6d606`. Ambos iguales a `Base develop`.
- Compuerta de arranque (`venv/Scripts/python.exe scripts/check.py`): 347 passed, 93.05 %, `ruff check` 86,
  mypy 44 (12 archivos), import-linter 4 KEPT / 0 BROKEN, `145 files already formatted`. Igual al cierre de la Fase A.

## Archivos tocados

| Commit | Archivo | Qué |
|---|---|---|
| B1 `87e1942` | `app/schemas/service.py` | I001 (lo aplicó el hook), docstring de `format_service_name` con resumen terminado en punto + línea en blanco + cuerpo, `description` de `image_urls` repartida con concatenación implícita. `default=[]` (S7) sin tocar |
| B2 `f59f75e` | `app/schemas/service.py` | `ServiceListResponse(BaseModel)` y `ServiceDetailResponse(BaseModel)` con docstring y los campos planos del plan, `ConfigDict(from_attributes=True)` intacto |
| B2 `f59f75e` | `tests/test_services.py` | imports `datetime`/`Decimal`; sección `# === A9: ... ===` al final: `LIST_RESPONSE_KEYS` (8), `DETAIL_RESPONSE_KEYS` (10), `_persist_package`, 8 funciones, 13 casos |

```
$ git show --stat --format= 87e1942
 app/schemas/service.py | 11 ++++++++---
 1 file changed, 8 insertions(+), 3 deletions(-)

$ git show --stat --format= f59f75e
 app/schemas/service.py |  28 +++++++-
 tests/test_services.py | 191 +++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 217 insertions(+), 2 deletions(-)
```

## Neutralidad del commit `style` (B1)

- `ruff check app/schemas/service.py` → `All checks passed!` (antes: 4). `ruff format --check` → `1 file already formatted`.
- `diff openapi-0.json openapi-1.json` → vacío (rc=0); `git diff --no-index --stat` → vacío.
- `pytest -q` tras B1 → `347 passed, 3 warnings in 17.34s` (igual que la línea base).

## RED (tests sobre B1, antes del cambio de B2)

```
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[short_name]
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_name]
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[price_below_floor]
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[capacity_over_cap]
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_description]
FAILED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[mixed_case_name]
FAILED tests/test_services.py::test_public_catalog_survives_one_off_rule_package
FAILED tests/test_services.py::test_inactive_column_returns_off_rule_package
FAILED tests/test_services.py::test_deleted_column_returns_off_rule_package
FAILED tests/test_services.py::test_update_on_off_rule_package_returns_200_with_persisted_change
PASSED tests/test_services.py::test_create_still_rejects_short_name
PASSED tests/test_services.py::test_update_still_rejects_capacity_over_limit
PASSED tests/test_services.py::test_create_still_title_cases_name
10 failed, 3 passed, 23 deselected, 2 warnings in 0.29s
```

Motivos (`--tb=line`): 9 de los 10 fallos son
`fastapi.exceptions.ResponseValidationError: 1 validation error:` (`fastapi/routing.py:296`). El décimo es
`mixed_case_name`: `AssertionError: assert 'Ruta Cafetera Delacruz' == 'Ruta Cafetera DeLaCruz'`
(`tests/test_services.py:692`). Coincide con lo que predice el plan: en el caso 1 hay 5 RVE y una aserción;
2, 3, 4 y 5 dan RVE; 6, 7 y 8 están en verde y congelan la entrada.

## GREEN (tras B2)

```
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[short_name]
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_name]
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[price_below_floor]
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[capacity_over_cap]
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[long_description]
PASSED tests/test_services.py::test_public_catalog_returns_stored_package_verbatim[mixed_case_name]
PASSED tests/test_services.py::test_public_catalog_survives_one_off_rule_package
PASSED tests/test_services.py::test_inactive_column_returns_off_rule_package
PASSED tests/test_services.py::test_deleted_column_returns_off_rule_package
PASSED tests/test_services.py::test_update_on_off_rule_package_returns_200_with_persisted_change
PASSED tests/test_services.py::test_create_still_rejects_short_name
PASSED tests/test_services.py::test_update_still_rejects_capacity_over_limit
PASSED tests/test_services.py::test_create_still_title_cases_name
13 passed, 23 deselected, 2 warnings in 0.26s
```

`pytest tests/test_services.py -q` → `36 passed, 3 warnings in 3.52s` (23 anteriores + 13).

## Compuerta de salida (`venv/Scripts/python.exe scripts/check.py`, árbol idéntico a `f59f75e`)

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

| Métrica | Inicio de la Fase B | Fin de la Fase B | Criterio del plan |
|---|---|---|---|
| pytest | 347 passed | **360 passed**, 0 failed (`360 passed, 5 warnings in 18.24s`) | 360 |
| Cobertura | 93.05 % | **94.77 %** (`TOTAL 934 34 136 22 94.77%`) | ≥ 92.76 % |
| `ruff check .` | 86 | **82** (`Found 82 errors.`) | ≤ 82 |
| mypy | 44 (12 archivos) | **44** (`Found 44 errors in 12 files (checked 35 source files)`) | ≤ 44 |
| import-linter | 4 KEPT | **4 KEPT, 0 broken** | 4 KEPT |
| `ruff format --check` | 145 OK | 145 OK | OK |

- `ruff check app/schemas/service.py tests/test_services.py` → `All checks passed!`.
- En la salida de la compuerta, la única línea de `app/schemas/service.py` es la de cobertura (`51 1 2 1 96.23% 120`);
  no tiene ningún error de ruff ni de mypy.

## OpenAPI

`git diff --no-index --stat openapi-1.json openapi-2.json` → `1 file changed, 4 insertions(+), 18 deletions(-)`.
Comprobado por programa: los componentes que cambian son `['ServiceDetailResponse', 'ServiceListResponse']`;
el resto del documento es igual (`True`), y en los dos componentes la lista `required` y el orden de las
propiedades no cambian (`True`/`True`). Diff literal (`diff openapi-1.json openapi-2.json`):

```
181a182
>     "description": "Serialized detail view of a stored tourist package, including its timestamps.\n\nSame rationale as ServiceListResponse: no input rules on output (backlog A9).",
184,185c185
<       "description": "Precio base en COP. No puede ser inferior a $40,000",
<       "pattern": "^(?!^[-+.]*$)[+-]?0*(?:\\d{0,8}|(?=[\\d.]{1,11}0*$)\\d{0,8}\\.\\d{0,2}0*$)",
---
>       "pattern": "^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$",
213d212
<         "maxLength": 1000,
240,242d238
<       "description": "Capacidad máxima de turistas",
<       "exclusiveMinimum": 0.0,
<       "maximum": 30.0,
247,249d242
<       "description": "Nombre del paquete (mínimo 20 caracteres, máximo 65)",
<       "maxLength": 65,
<       "minLength": 20,
304a298
>     "description": "Serialized catalog view of a stored tourist package.\n\nDeclared on BaseModel on purpose: it describes what is stored and never re-applies\nthe input rules of ServiceBase (length, price floor, capacity cap, title-case), so\none off-rule package cannot take the public catalog down (backlog A9).",
307,308c301
<       "description": "Precio base en COP. No puede ser inferior a $40,000",
<       "pattern": "^(?!^[-+.]*$)[+-]?0*(?:\\d{0,8}|(?=[\\d.]{1,11}0*$)\\d{0,8}\\.\\d{0,2}0*$)",
---
>       "pattern": "^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$",
319d311
<         "maxLength": 1000,
346,348d337
<       "description": "Capacidad máxima de turistas",
<       "exclusiveMinimum": 0.0,
<       "maximum": 30.0,
353,355d341
<       "description": "Nombre del paquete (mínimo 20 caracteres, máximo 65)",
<       "maxLength": 65,
<       "minLength": 20,
```

## Verificación final (pasos que dependen de la Fase B; retoque 3)

```
--1  grep -rnE "class \w+Response\(\w+Base\)" app/schemas/
app/schemas/audit.py:25:class AuditLogResponse(AuditLogBase):
--2  grep -nE "class (UserResponse|ServiceListResponse|ServiceDetailResponse)\(" app/schemas/*.py
app/schemas/service.py:65:class ServiceListResponse(BaseModel):
app/schemas/service.py:84:class ServiceDetailResponse(BaseModel):
app/schemas/user.py:132:class UserResponse(BaseModel):
--3  grep -rnE "response_model=(list\[)?(UserResponse|ServiceListResponse|ServiceDetailResponse)" app/api/routers/ | wc -l
11
     git diff 83bfd6a --stat -- app/api/routers/ app/main.py app/models/ alembic/
(vacío)
--4  introspección
UserResponse BaseModel {} {} <class 'str'>
ServiceListResponse BaseModel {} {} None
ServiceDetailResponse BaseModel {} {} None
--4b grep -cE "pattern=|min_length=|max_length=|ge=|le=|gt=|EmailStr" app/schemas/user.py app/schemas/service.py
app/schemas/user.py:23
app/schemas/service.py:12
     git show ba75d89:app/schemas/user.py | grep -cE "…"     → 23
     git show 83bfd6a:app/schemas/service.py | grep -cE "…"  → 12
--5  grep -rn "ResponseValidation" app/
(vacío)
--6  grep -rnE "Jean-Luc|O'Brien|Tour corto|DeLaCruz" tests/   (sin contar .pyc)
      7 tests/test_services.py
     11 tests/test_user_response.py
--7  grep -n "default=\[\]" app/schemas/service.py
56:        default=[],
--alcance  git diff ba75d89 HEAD --stat   (sobre f59f75e, antes del commit de docs)
 app/schemas/service.py |  39 ++++++++--
 docs/deuda/A9/gaps.md  |  80 +++++++++++++++++++++
 docs/deuda/A9/plan.md  |  14 ++++
 tests/test_services.py | 191 +++++++++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 319 insertions(+), 5 deletions(-)
```

- Paso 4b: `service.py` da el mismo recuento que en `83bfd6a` (12 = 12), así que no hay líneas de más que
  justificar. `user.py` da el mismo que en `ba75d89` (23 = 23).
- Alcance: solo `app/schemas/service.py`, `tests/test_services.py` y `docs/deuda/A9/` (`gaps.md` y `plan.md` vienen de
  `f7520dd`, el commit de la auditoría de la Fase A). Este commit de docs añade `progress.json` y `handoff-Fase_B.md`.

## Desviaciones y notas para el auditor

1. **S7 cambia de línea, no de contenido.** El plan dice que `default=[]` "sigue en l.54", pero ahora está en la **l.56**.
   El I001 de B1 añade dos líneas al bloque de imports (el import de `pydantic` baja debajo de la stdlib, separado
   por una línea en blanco). El contenido de `Field(default=[], max_length=10, …)` no cambia.
2. **El `pattern` del `Decimal` no desaparece del OpenAPI: lo sustituye el genérico.** Al quitar
   `max_digits`/`decimal_places`, Pydantic emite el patrón genérico de `Decimal` (`^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$`)
   en vez del acotado. El tipo sigue siendo el mismo. `ge=40000` ya no salía en el componente antes de B2, así que no
   aparece en el diff.
3. **El hook borró los imports nuevos de los tests en la primera edición.** Añadí `from datetime …` y `from decimal …`
   antes que los tests que los usan. `ruff check --fix` los quitó (F401) y los volví a poner después de añadir la
   sección. El resultado final coincide con el plan.
4. **`current_target` = `"cierre"`.** Es la última fase del plan. Seguí el precedente de `docs/deuda/SEC1/progress.json`.
   El cierre (o el auditor) lo pasa a `null` cuando A9 quede cerrado.
5. Además de lo que pide el plan, en el caso 1 afirmo que la lista tiene un único elemento (`len(body) == 1`) y que
   `item["id"] == package.id`. En el 3, en el 4 y en el 8 compruebo también el `id`. La comprobación del 8 en la BD usa
   `db_session.get(TouristService, body["id"])`.
6. No ejecuté las mutaciones M1-M3: son para el auditor.

## Residuales

- **mypy fuera de la compuerta en `tests/test_services.py:183`** (`Value of type "object" is not indexable [index]`).
  Sale solo al correr `mypy` directamente sobre el archivo de tests; la compuerta no lo ve porque
  `[tool.mypy] files` solo cubre `app` y `scripts`. El error ya existía en la l.181 de `87e1942`
  (`test_update_package_details`, `update_payload["image_urls"][0]`), comprobado con mypy sobre esa versión. Las
  líneas nuevas de la Fase B no le añaden ningún error. No lo arreglo porque está fuera de alcance.
- Los demás residuales del plan (patrón de nombres, handler de `ResponseValidationError`, regla no determinista, S7,
  S6, D2 y esquema de BD laxo) siguen igual y van al cierre.

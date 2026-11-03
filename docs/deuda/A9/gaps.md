# Gaps — A9

## Auditoría Fase A — 2026-11-02

Compuerta re-ejecutada sobre `ba75d89` con `venv/Scripts/python.exe scripts/check.py`: ruff format ✔ (144 files: ruff
también formatea los `.md`, por eso +1 frente a los 143 del handoff, que es el propio handoff), ruff check ✘ `Found 86
errors.`, mypy ✘ `Found 44 errors in 12 files (checked 35 source files)`, import-linter ✔ (`Contracts: 4 kept, 0
broken.`, con `venv/Scripts/lint-imports.exe --no-cache`), docs ✔, pytest ✔ `347 passed, 3 warnings`, cobertura `Total
coverage: 93.05%`. Frente a la línea base (333 · 92.76 % · ruff 97 · mypy 44 · 4 KEPT): +14 tests, cobertura sube, ruff
baja 11 (97 − 11 = 86, criterio ≤ 86), mypy igual. Coincide con lo que pegó el ejecutor. Archivos de la fase:
`ruff check app/schemas/user.py tests/test_user_response.py` → `All checks passed!`; `ruff format --check` → `2 files
already formatted`; `mypy` global sin ninguna línea de `app/schemas/` ni del test nuevo.

Mutaciones del plan (sobre la punta, aplicadas con un script del scratchpad, `tests/test_user_response.py`, archivo
restaurado byte a byte desde copia, sha256 `ee65bc9c…` antes y después; `git status --short` y `git diff` vacíos al final):
- M1, `UserResponse` vuelve a la declaración previa (`class UserResponse(UserBase)` sin campos redeclarados) →
  `11 failed, 3 passed`: los 8 casos de 1, más 2, 3 y 4. Seis por `ResponseValidationError` y dos por aserción
  (`'Mcdonald' == 'McDonald'`, `'Ana@example.com' == 'Ana@EXAMPLE.COM'`). **Muerta.**
- M1 literal (solo cambia la base a `UserBase` y se mantienen los campos planos) → `2 failed, 12 passed`: `[mixed_case_surname]`
  (`'Mcdonald'`) y `[66_chars]` (`'Aaaa…'`), por el `format_title_case` heredado. **Muerta.**
- M2, `email: EmailStr` en `UserResponse` → `2 failed, 12 passed`: `[dotless_domain]` (`ResponseValidationError`,
  `value_error` en `('response', 'email')`) y `[mixed_case_domain]` (`'Ana@example.com' == 'Ana@EXAMPLE.COM'`). **Muerta.**
- M3, quitar `format_title_case` de `UserBase` → `1 failed, 13 passed`: `test_registration_still_title_cases_names`
  (`'jUAN' == 'Juan'`). **Muerta.**

Hallazgos:
- [OPCIONAL] — Fase A (defecto del plan, no de la fase) — El grep 3 de la Verificación final compara contra `7c6d606`,
  pero los commits de SEC1 (`9ce0379 fix(cors)`) entraron en la rama antes del plan (`83bfd6a`), así que `app/main.py |
  41` aparece sin que A9 lo toque. Medido contra `83bfd6a`, `git diff 83bfd6a --stat -- app/api/routers/ app/main.py
  app/models/ alembic/` sale vacío. En el cierre de Fase B se debe medir contra `83bfd6a`. — `git log --oneline
  7c6d606..HEAD -- app/main.py` → solo `9ce0379`
- [OPCIONAL] — Fase A (defecto del plan) — El recuento 4b da `app/schemas/user.py:23` frente a `22` en `7c6d606`. La línea
  de más es el docstring de `UserResponse`, que el propio plan dicta (`re-applies the input rules of UserBase (patterns,
  lengths, EmailStr, title-case),`). La otra diferencia es el reorden I001 del import. No ha desaparecido ninguna regla:
  `model_json_schema()`, validadores y `model_config` de `UserBase`, `UserCreate`, `UserCreateByAdmin`, `UserUpdate` y
  `UserLogin` son idénticos entre `83bfd6a` y la punta. Solo cambia `UserResponse`. — diff de las líneas que casan
  el patrón entre `7c6d606:app/schemas/user.py` y la punta; comparación de esquemas en el scratchpad del auditor
- [OPCIONAL] — Fase A (hueco del plan) — Ningún test fija que la salida ya **no recorta** (adenda punto 3, decisión 2
  "no recorta"). Un mutante que añadiera `str_strip_whitespace` al `model_config` de `UserResponse` pasaría los 14
  casos. El plan no pedía ese caso, así que la fase cumple. Si se quiere fijar, basta un caso más en el test 1 (por ejemplo
  `first_name=" Ana "`). — `tests/test_user_response.py:58-80`
- [OPCIONAL] — Fase A — `_count_users` es un helper privado del módulo de tests que el plan no listaba. Sirve para
  afirmar "no queda ningún `User` en la BD" del test 5, que el plan sí exige. No tiene docstring, pero AGENTS §4 lo pide
  solo para funciones públicas. Aceptable. — `tests/test_user_response.py:50-52`

Juicio de las notas del ejecutor:
1. 4b 23 frente a 22: confirmado. Es el docstring del plan y no falta ninguna regla (ver arriba).
2. Grep 3: es un defecto del plan, no de la fase (ver arriba). `git diff 83bfd6a HEAD --stat` solo contiene
   `app/schemas/user.py`, `tests/test_user_response.py` y los documentos de `docs/deuda/A9/`.
3. `_count_users`: aceptable (ver arriba).
4. Clave `"detalle"`: es estructura del JSON (`app/main.py:96`, `content={"detalle": ...}`), no texto humano. El plan la
   fija en el Riesgo 3 (deuda P2). Se afirma sobre `raw_field`, que es un nombre de campo. No vulnera AGENTS §5. El test 7
   afirma la lista completa `== ["first_name"]`, más estricto que el plan.

Sin bloqueantes. Verificado:
- Árbol limpio: `git status --short` vacío antes y después de la auditoría.
- `progress.json`: JSON válido; `Fase_A` `completed` con `"4f70b0e c369e3f"` (los dos son commits reales en
  `bloque/b-higiene`); `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` sin cambios (diff
  `83bfd6a..ba75d89`).
- Mensajes de commit: A1 y A2 idénticos al plan línea a línea (`diff` del cuerpo frente a `plan.md:221-239` y
  `:243-271`). Solo se añade el trailer `Co-Authored-By`, que el ritual permite.
- `4f70b0e` toca solo `app/schemas/user.py`. `c369e3f` toca solo `app/schemas/user.py`, en el único bloque de
  `UserResponse` (13+/1−), y `tests/test_user_response.py`, así que contiene solo A9. No se tocan `app/schemas/service.py`,
  `tests/test_services.py`, routers, `app/main.py`, modelos, `alembic/`, `tests/conftest.py` ni `tests/test_auth.py`
  en `83bfd6a..ba75d89`.
- Neutralidad del commit `style`, regenerada por el auditor: `app.openapi()` con `user.py` de `83bfd6a` y de `4f70b0e`
  da `diff` vacío; la suite (sin el test nuevo) da `333 passed, 1 warning` con las dos versiones. Entre `4f70b0e` y la
  punta solo cambia `components.schemas.UserResponse`; el resto del documento es idéntico, y `required`, propiedades y
  tipos no cambian.
- Cambios exactos de A1: `noqa: UP042 (backlog D2)`, descripciones de l.26/36/43/66 con concatenación implícita y el
  mismo texto (lo prueba el OpenAPI idéntico), comentario en dos líneas y tres docstrings con resumen, línea en blanco y
  cuerpo. Los de A2: los 9 campos, su orden, sus tipos, `phone=None` y `model_config = {"from_attributes": True}`, como en
  el plan. Introspección: `UserResponse BaseModel {} {} <class 'str'>`; el orden de los campos es igual a
  `UserBase + [id, role, is_active, created_at]`.
- Tests: 7 funciones y 14 casos con los nombres exactos del plan, todos en verde. El RED que reproduce M1 coincide con el
  previsto. Usuarios sembrados solo con `persist_user` y cabeceras con `make_auth_headers` (fábricas de `conftest.py`).
  Mock de correo con `autospec=True`, más `assert_not_called` y `assert_called_once_with(email_to=..., first_name="Juan",
  token=ANY, base_url=ANY)`. Se afirma código HTTP, claves, valores guardados y estado de la BD tras `refresh`/`select`.
  Ninguna aserción sobre texto en español: `"Pérez"` es un dato guardado, no un mensaje.
- Ninguna excepción de dominio nueva. Capas intactas (4 KEPT).

## Auditoría Fase B — 2026-11-02

**Veredicto: PASS (0 bloqueantes, 4 opcionales).**

Compuerta re-ejecutada sobre `99593c1` con `venv/Scripts/python.exe scripts/check.py`, árbol limpio: ruff format ✔
(`146 files already formatted`: +1 frente al handoff porque cuenta el propio handoff), ruff check ✘ `Found 82 errors.`,
mypy ✘ `Found 44 errors in 12 files (checked 35 source files)`, import-linter ✔ (`Contracts: 4 kept, 0 broken.`, con
`venv/Scripts/lint-imports.exe --no-cache`), docs ✔, pytest ✔ `360 passed, 5 warnings in 18.53s`, cobertura `Total
coverage: 94.77%`. Frente a la línea base de la fase (347 · 93.05 % · ruff 86 · mypy 44 · 4 KEPT): +13 tests, la
cobertura sube, ruff baja 4 (86 − 4 = 82, criterio ≤ 82) y mypy queda igual. Coincide con lo que pegó el ejecutor.
Archivos de la fase: `ruff check app/schemas/service.py tests/test_services.py` → `All checks passed!`;
`ruff format --check` → `2 files already formatted`; `mypy` global sin ninguna línea de `app/schemas/`.

Mutaciones del plan, sobre la punta y solo con los 13 casos de la sección A9 de `tests/test_services.py` (`-k` con las 8
funciones). Cada mutante se generó con un script del scratchpad. `app/schemas/service.py` se restauró desde una copia
y el sha256 `37594fee…` se comprobó tras cada una. `tests/test_services.py` (`3ba2f60a…`) no se tocó:
- M1, las dos clases vuelven a la declaración de `87e1942` (`(ServiceBase)` sin campos redeclarados) → `10 failed, 3
  passed`: los 6 casos de 1, más 2, 3, 4 y 5. Nueve fallan por `ResponseValidationError` (`fastapi/routing.py:296`) y
  `[mixed_case_name]` por aserción (`'Ruta Cafetera Delacruz' == 'Ruta Cafetera DeLaCruz'`, `tests/test_services.py:692`).
  6, 7 y 8 siguen en verde. **Muerta.**
- M1 literal (solo cambia la base a `ServiceBase` en las dos clases; se mantienen los campos planos) → `4 failed, 9
  passed`: `[short_name]` (`'Tour Corto'`), `[long_name]` (`'Paquete Aaaa…'`), `[mixed_case_name]` y el test 5
  (`'Tour Corto' == 'Tour corto'`, l.752), por el `format_service_name` heredado. **Muerta.**
- M2, solo `ServiceListResponse` vuelve a la declaración de `87e1942` → `8 failed, 5 passed`: los 6 casos de 1, más 2 y
  3. **No** fallan 4 (`/admin/eliminados`, `ServiceDetailResponse`) ni 5 (PUT, `ServiceDetailResponse`). Coincide con lo
  que predice el plan. **Muerta.**
- M2 literal (solo cambia la base de `ServiceListResponse`) → `3 failed, 10 passed`: `[short_name]`, `[long_name]` y
  `[mixed_case_name]`. **Muerta.**
- M3, quitar `format_service_name` de `ServiceBase` → `1 failed, 12 passed`: `test_create_still_title_cases_name`
  (`'ruta cafetera del magdalena' == 'Ruta Cafetera Del Magdalena'`, l.796). **Muerta.**
- Punta restaurada → `13 passed, 23 deselected`. `git status --short` y `git diff` vacíos después de cada mutación.

Hallazgos:
- [OPCIONAL] — Fase B (hueco del plan, el mismo que en la Fase A) — Ningún test fija que la salida de paquetes ya **no
  recorta** (decisión 2, "no recorta"). `ServiceBase` tiene `str_strip_whitespace=True`, y un mutante del auditor (M4)
  que añade `str_strip_whitespace=True` al `ConfigDict` de las dos respuestas pasa los 13 casos (`13 passed, 23
  deselected`). El plan no pedía ese caso, así que la fase cumple. Si se quiere fijar, basta un caso más en el test 1
  (por ejemplo `name=" Paquete De Prueba Automatizada "`). — `tests/test_services.py:658-692`; mutante en el scratchpad
  del auditor
- [OPCIONAL] — Fase B (defecto del plan) — El Riesgo 1 dice que los componentes de respuesta pierden "el `pattern` del
  `Decimal`". En realidad Pydantic lo sustituye por el patrón genérico de `Decimal`
  (`^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$`) al quitar `max_digits`/`decimal_places`, y `ge=40000` no aparecía antes en esos
  componentes. El tipo, `required`, `default`, `title` y el orden de las propiedades no cambian. La nota 2 del ejecutor
  es correcta. El cierre debe describir así el cambio del OpenAPI. — `diff openapi-1 openapi-2` regenerado por el
  auditor (líneas 184-185 y 307-308)
- [OPCIONAL] — Fase B (defecto del plan) — El criterio `grep -n "default=\[\]" app/schemas/service.py → sigue en l.54`
  y el Residual "S7 en `app/schemas/service.py:53-54`" se quedaron viejos: ahora es `56:        default=[],` (y
  `Field(` en l.55). El I001 de B1 añade dos líneas al bloque de imports. El contenido no cambia: en el diff de
  `87e1942`, `default=[]` y `max_length=10` aparecen como líneas de contexto. El cierre debe citar l.55-56 cuando anote
  S7 en el backlog. — `git show 87e1942 -- app/schemas/service.py`, grep 7
- [OPCIONAL] — Fase B (residual, preexistente) — `mypy tests/test_services.py` da `tests\test_services.py:183: error:
  Value of type "object" is not indexable [index]`. Ya existía antes de la fase: el mismo archivo en `f7520dd` da el
  mismo error en la l.181 (las dos líneas de diferencia son los imports nuevos), con el mismo total (`Found 45 errors in
  13 files`). Está fuera de la compuerta (`pyproject.toml:90`, `files = ["app", "scripts/…"]`). Va a Residuales o al
  backlog, no es gap. — mypy sobre `git show f7520dd:tests/test_services.py` en el scratchpad

Juicio de las notas del ejecutor:
1. S7 de l.54 a l.56: confirmado; es un desplazamiento y no un cambio (ver hallazgo 3).
2. `pattern` genérico de `Decimal`: confirmado; el defecto es del texto del plan, no de la fase (ver hallazgo 2).
3. Imports de `datetime`/`Decimal` borrados por el hook y vueltos a añadir: no se ve en el resultado, que coincide con
   el plan (`tests/test_services.py:9-10`, ordenados por isort, `ruff check` limpio). No es un hallazgo.
4. `current_target: "cierre"`: aceptado. Sigue el precedente de `docs/deuda/SEC1/progress.json:3`, y `edit_rules`
   permite que la sesión ejecutora lo cambie. Lo pasa a `null` el cierre.
5. Aserciones extra (`len(body) == 1` e `item["id"] == package.id` en 1; `id` en 3, 4 y 8; `db_session.get` en 8): son
   más estrictas que el plan y no contradicen ningún punto. Aceptadas.
6. mypy `tests/test_services.py:183 [index]`: preexistente (ver hallazgo 4). Residual.

Sin bloqueantes. Verificado:
- Árbol limpio: `git status --short` vacío antes de la auditoría; al terminar solo cambia este `gaps.md`.
- `progress.json`: JSON válido; `Fase_B` `completed` con `"87e1942 f59f75e"` (los dos son `commit` en
  `bloque/b-higiene`); `current_target` = `cierre`; `last_handoff` presente y coherente con las cifras re-ejecutadas;
  `edit_rules` sin cambios (`git diff 83bfd6a HEAD`, línea de contexto).
- Mensajes de commit: B1 y B2 idénticos al plan línea a línea (`diff` del cuerpo, sin el trailer, frente a
  `plan.md:377-392` y `:396-419`: vacío). Solo se añade el trailer `Co-Authored-By`, que el ritual permite.
- Alcance: `87e1942` toca solo `app/schemas/service.py` (8+/3−). `f59f75e` toca solo `app/schemas/service.py`, en los
  dos bloques `*Response` (26+/2−), y `tests/test_services.py` (2 imports más la sección final, 191 líneas añadidas,
  0 borradas), así que contiene solo A9. `99593c1` toca solo `docs/deuda/A9/`. `git diff ba75d89 HEAD --stat`:
  `app/schemas/service.py`, `tests/test_services.py` y `docs/deuda/A9/{gaps,handoff-Fase_B,plan,progress}`. En
  `f7520dd..99593c1` no cambian `app/schemas/user.py`, `tests/test_user_response.py`, `app/api/`, `app/models/`,
  `app/main.py`, `alembic/`, `tests/conftest.py` ni `tests/test_auth.py` (`git diff --name-only`: vacío).
- Neutralidad del commit `style`, regenerada por el auditor (se cambiaron los archivos en el árbol y se restauraron por
  sha256): `app.openapi()` con `service.py` de `f7520dd` y de `87e1942` da `diff` vacío. La suite, con
  `tests/test_services.py` de `f7520dd`, da `347 passed, 3 warnings` con las dos versiones. Entre `87e1942` y la punta
  solo cambian `components.schemas.ServiceListResponse` y `ServiceDetailResponse`; `paths` y el resto de componentes
  son idénticos, y `required` y el orden de las propiedades no cambian.
- Cambios exactos de B1: I001, el docstring de `format_service_name` (resumen con punto, línea en blanco y cuerpo) y la
  `description` de `image_urls` con concatenación implícita y el mismo texto (lo prueba el OpenAPI idéntico).
  `default=[]` intacto. Los de B2: los campos, el orden, los tipos, los defaults (`None`, `ServiceCategory.otro`,
  `False`, `[]`) y `ConfigDict(from_attributes=True)` de las dos clases, como en el plan. Sondeo del auditor: para un
  paquete válido, `model_dump_json()` de las clases de `87e1942` y de la punta es idéntico byte a byte. El orden y los
  defaults de `model_fields` son iguales. `model_json_schema()`, validadores y `model_config` de `ServiceBase`,
  `ServiceCreate`, `ServiceUpdate`, `ServiceImageResponse` y `ServiceImageOutput` son idénticos entre `87e1942` y la punta.
- Tests: 8 funciones y 13 casos con los nombres exactos del plan, todos en verde. El RED que reproduce M1 coincide con
  el del handoff. Los paquetes se siembran vía ORM con `_persist_package` (helper que dicta el plan) y el admin con la
  fixture `admin_headers` (`persist_user` + `make_auth_headers`). `storage_double` usa `create_autospec(...,
  instance=True)` y se comprueba con `assert_not_awaited`/`assert_awaited_once_with(TEMP_URL)`. Se afirma el código HTTP,
  las claves, los valores guardados y el estado de la BD (`refresh`, `db_session.get`, `_assert_nothing_persisted`).
  Ninguna aserción sobre texto humano en español: `"Tour corto"` y `"Ruta Cafetera Del Magdalena"` son datos guardados,
  y `"detalle"`/`raw_field` son estructura (Riesgo 3, deuda P2). Los 2 warnings nuevos
  (`HTTP_422_UNPROCESSABLE_ENTITY`) los emite `app/main.py:95` en los dos tests 422 nuevos; ya están en el backlog como S5.
- Ninguna excepción de dominio nueva. Capas intactas (4 KEPT).

Verificación final (última fase; retoque 3 para los pasos 3 y 4b), ejecutada por el auditor sobre `99593c1`:
```
--1  app/schemas/audit.py:25:class AuditLogResponse(AuditLogBase):      (AuditLogBase sin Field ni validadores)
--2  app/schemas/service.py:65:class ServiceListResponse(BaseModel):
     app/schemas/service.py:84:class ServiceDetailResponse(BaseModel):
     app/schemas/user.py:132:class UserResponse(BaseModel):
--3  11 ; git diff 83bfd6a --stat -- app/api/routers/ app/main.py app/models/ alembic/ → (vacío)
--4  UserResponse BaseModel {} {} <class 'str'>
     ServiceListResponse BaseModel {} {} None
     ServiceDetailResponse BaseModel {} {} None
--4b app/schemas/user.py:23 · app/schemas/service.py:12 ; ba75d89:user.py → 23 ; 83bfd6a:service.py → 12
--5  grep -rn "ResponseValidation" app/ → (vacío)
--6  7 tests/test_services.py · 11 tests/test_user_response.py
--7  56:        default=[],
--8  ruff check (4 archivos) → All checks passed! ; ruff check . → Found 82 errors.
     mypy → Found 44 errors in 12 files (checked 35 source files), sin líneas de app/schemas
     pytest tests/test_user_response.py tests/test_services.py → 50 passed, 5 warnings
     scripts/check.py → 360 passed, Total coverage: 94.77%, 4 kept / 0 broken
```
Todo sale como espera el plan, salvo la línea de S7 (l.56 y no l.54; hallazgo 3). A9 queda listo para el cierre.

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

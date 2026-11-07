# Handoff — BE-32 · Fase I (E3, corregida por E4)

- **Commit de la fase:** `21e0142` `test(email): pin the single SMTP attempt and tighten two docstrings`
- **Ejecutor:** Claude Opus 5.5 (`fase-ejecutor`), 7 nov 2026.
- **Contrato:** `plan.md` → E3 / `### Fase I`, con E4 (puntos 1–3) donde choca con E3.

## Ritual de arranque

- `git status --short`: limpio. HEAD `ad9a7ce`. `current_target` = `Fase_I`, `Fase_I` = `pending`.
- Vigencia de la línea base: `Base develop` = `fd144ad` (`verificacion.md:223`). `git fetch origin` correcto;
  `git rev-parse --short origin/develop` = `fd144ad`; `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `fd144ad`. Vigente.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 1): ruff 8 (todos `app\...:1:1`
  I001), mypy `Found 9 errors in 5 files (checked 53 source files)`, `Contracts: 4 kept, 0 broken.`, `548 passed, 5
  warnings`, `TOTAL 943 23 138 19 96.11%`. Igual a la fila H: nada peor que la verificación.

## Archivos tocados

- `tests/test_email.py` (commit de la fase).
- `docs/deuda/BE-32/progress.json` y este handoff (commit de progreso).

`git show --stat 21e0142`:

```text
 tests/test_email.py | 7 +++----
 1 file changed, 3 insertions(+), 4 deletions(-)
```

Diff del commit (completo):

```diff
@@ -28,7 +28,7 @@ VERIFICATION_LINK = f"{BASE_URL}/usuarios/verificar-email?token={TOKEN}"
 class _BodyCollector(HTMLParser):
-    """Collects every <a> tag's attributes and each visible text node with its tag."""
+    """Collects each <a> tag's attributes and every text node with its tag, <style> included."""
@@ -91,9 +91,7 @@
 async def test_body_carries_the_link_in_the_button_and_as_plain_text(send_message: Any) -> None:
-    """The link is the button's href and, once, visible text in a styled <p>; the button
-    has text.
-    """
+    """The link is the button's href and, once, visible text in a styled <p>; button has text."""
@@ -125,6 +123,7 @@ async def test_smtp_failure_propagates(send_message: Any) -> None:
     assert exc_info.value is error
+    assert send_message.await_count == 1
     call = send_message.await_args
```

## Columnas medidas (`len()` de la línea, con el Python del venv)

| Línea (tras el cambio) | Contenido | Columnas |
|---|---|---|
| `:31` | docstring de `_BodyCollector` (texto de E4) | **96** |
| `:94` | docstring de `test_body_carries_...` (texto de E3) | **97** |
| `:126` | `assert send_message.await_count == 1` | 40 |

Ninguna línea del archivo pasa de 100 columnas (búsqueda `len(l) > 100`: vacía).

## RED de D205 (E4 punto 2)

`./venv/Scripts/python.exe -m ruff check --isolated --select D205,D415 --line-length 100 tests/test_email.py`

Antes (`ad9a7ce`), exit 1:

```text
D205 1 blank line required between summary line and description
  --> tests\test_email.py:94:5
   |
93 |   async def test_body_carries_the_link_in_the_button_and_as_plain_text(send_message: Any) -> None:
94 | /     """The link is the button's href and, once, visible text in a styled <p>; the button
95 | |     has text.
96 | |     """
   | |_______^
97 |       body = _body_of(await _send_and_capture(send_message))
   |
help: Insert single blank line

Found 1 error.
```

Después (árbol = `21e0142`), exit 0:

```text
All checks passed!
```

## RED: mutantes R1 y D8 en copia desechable

Dos copias fuera del árbol, en el scratchpad de la sesión, sacadas con `git archive HEAD | tar -x` con HEAD = `ad9a7ce`:

- **antes** (`ad9a7ce`, 548 tests): sin cambios. `cmp` de `tests/test_email.py` y `app/core/email.py` contra el árbol:
  idénticos.
- **después** (`ad9a7ce` + `tests/test_email.py` de la fase = árbol de `21e0142`, 548 tests): `cmp` contra el árbol de
  trabajo idéntico y `git diff --name-only` listaba solo `tests/test_email.py`. Tras el commit,
  `git show 21e0142:tests/test_email.py | cmp - <copia>` también da idéntico.

Método: un script (en un directorio aparte de las copias) localiza `    await fast_mail.send_message(message)\n` en
`app/core/email.py` de la copia (exige 1 coincidencia), aplica el mutante, corre
`python -m pytest <objetivo> -q --no-cov -p no:cacheprovider` con cwd en la copia sobre `tests/test_email.py` y sobre
`tests`, y restaura el archivo byte a byte en un `finally` con `assert`. Variables de entorno ficticias (`JWT_SECRET_KEY`,
`ALGORITHM=HS256`, `*_EXPIRE_MINUTES`, `DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`,
`CORS_ORIGINS`, `FRONTEND_URL`) y el Python del `venv/`. El script afirma que `app.core.email` resuelve a la copia
(lo imprime: `...\scratchpad\copy_before\app\core\email.py` y `...\copy_after\app\core\email.py`). Al final, `cmp` de
`app/core/email.py` de cada copia contra el repo: idéntico. El repo nunca llevó un mutante.

Mutantes:

- **R1** (E3 + E4 punto 3): la línea pasa a
  `from fastapi_mail.errors import ConnectionErrors` / `try: await fast_mail.send_message(message)` /
  `except ConnectionErrors: await fast_mail.send_message(message)`. El segundo intento vuelve a fallar con el mismo
  `side_effect`.
- **D8**: `await fast_mail.send_message(message.model_copy(update={"subject": "x"}))`.
- **CTRL** (control, no es del plan): `return None` en lugar del envío. Debe morir en los dos estados; prueba que pytest
  importa el `email.py` de la copia y no el del repo (el venv tiene una instalación editable).

| Mutante | Antes, archivo (`ad9a7ce`) | Después, archivo (`21e0142`) | Antes, suite (`ad9a7ce`) | Después, suite (`21e0142`) |
|---|---|---|---|---|
| sin mutante | `6 passed` | `6 passed` | `548 passed, 5 warnings` | `548 passed, 5 warnings` |
| R1 | `6 passed` | `1 failed, 5 passed` (`test_smtp_failure_propagates - assert 2 == 1`) | `548 passed, 5 warnings` | `1 failed, 547 passed, 5 warnings` (el mismo) |
| D8 | `6 passed` | `6 passed` (vivo, E0) | `548 passed, 5 warnings` | `548 passed, 5 warnings` |
| CTRL | `5 failed, 1 passed` | `5 failed, 1 passed` | `5 failed, 543 passed` | `5 failed, 543 passed` |

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Bloque RESUMEN literal:

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

Cifras de cada paso:

| Paso | Salida | Esperado (fila H / E3) |
|---|---|---|
| ruff format --check | `57 files already formatted` | igual |
| ruff check | `Found 8 errors.`: I001 en `app\api\dependencies.py`, `app\api\routers\audit.py`, `app\core\email.py`, `app\db\database.py`, `app\repositories\user_repository.py`, `app\schemas\audit.py`, `app\services\audit_service.py`, `app\services\user_service.py`, todos `:1:1`; ninguna línea `tests\` | 8, solo `app/` |
| mypy | `Found 9 errors in 5 files (checked 53 source files)`: `app\db\database.py:11`, `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`, `tests\test_user_service.py:105`, `:203`, `:280`, `:298` | conjunto de A4 |
| import-linter | `Contracts: 4 kept, 0 broken.` | 4 kept |
| docs | `Documentación coherente (...)` | OK |
| pytest | `548 passed, 5 warnings` (los 5 `StarletteDeprecationWarning` de siempre) | 548 passed |
| cobertura | `TOTAL 943 23 138 19 96.11%` | ≥ 96.11 % |

Identidad de A4 en `tests/test_user_service.py` (todas `SECRET_KEY`): `:105` `jwt.decode(result.verification_token,
SECRET_KEY, ...)`, `:203` `jwt.decode(result.access_token, SECRET_KEY, ...)`, `:280` `SECRET_KEY,`, `:298`
`SECRET_KEY,`.

Archivo tocado: `./venv/Scripts/python.exe -m ruff check tests/test_email.py` → `All checks passed!`;
`./venv/Scripts/python.exe -m mypy tests/test_email.py` → `Success: no issues found in 1 source file`.

## Verificación final completa (sobre el árbol de `21e0142`)

| Patrón | Esperado | Obtenido |
|---|---|---|
| 1. `assert_*()` sin argumentos | 0 | `0` |
| 1b. pares `not_called` + `not_awaited` | 0 | `0` |
| 2. copias en `test_user_access_policy.py` | 0 | `0` |
| 2. tests en `test_auth.py` | 3 | `3` |
| 2. cédula heredada (`test_auth.py` / política) | 1 y 0 | `tests/test_auth.py:1 tests/test_user_access_policy.py:0` |
| 3. `ruff check tests/` | `All checks passed!` | `All checks passed!` |
| 3. I001 en el repo | 8 | `8` |
| 4. `sqlalchemy.future` en tests | 0 | `0` |
| 5. comentario en español | 0 | `0` |
| 6. `files = ` en `pyproject.toml` | `94:files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]` | idéntico |
| 6. mypy | `Found 9 errors in 5 files (checked 53 source files)` | idéntico |
| 7. generadores sin `Yields:` | `tests\conftest.py:86 override_get_db` | idéntico |
| 8. orden de guardas | 1 | `1` |
| 9b-B. `StaleDataError` | 1 | `1` |
| 9b-C. `expired != corrupt` | 1 | `1` |
| 9b-C. D2 `corrupt == unknown` | 1 | `1` |
| 9b-C. `persist_user(... deleted_at` | 3 | `3` |
| 9b-D. `isinstance(message.subject, str)` / `await_args.args[0]` | 0 | `0` |
| 9c. `expires_delta` en `conftest.py` | 3 | `3` |
| 9c. `make_token(user, expires_delta=` | 1 | `1` |
| 9c. `jwt.encode` en tests | 2 | `2` |
| 9d. ids de la regla vieja | 0 | `0` |
| 10. `git diff --stat fd144ad -- app/` | `1 file changed, 3 insertions(+)` (E2) | ` 1 file changed, 3 insertions(+)` |
| 11. compuerta | exit 1 por ruff check y mypy; 4 kept; 548; ≥ 96.11 % | ver arriba |
| Fase I: `grep -c "await_count == 1" tests/test_email.py` | 1 | `1` |

## test-sanitizer (solo checklist)

El doble de `send_message` sigue con `autospec=True`; no hay preparación duplicada; todo en inglés; la aserción nueva
compara un entero, no texto en español. No se reescribió ninguna otra prueba.

## Residuales

Ninguno nuevo. D8 sigue vivo por decisión (E0; fila ya en Residuales por E3).

## Desviaciones y dudas

- Ninguna desviación de E3/E4. Se usó el texto de `_BodyCollector` de E4 (96 columnas), no el de E3 (101).
- Método: el primer intento de comprobar la resolución de `app.core.email` en la copia usó `python -I`, que quita el
  cwd de `sys.path`, e imprimió la ruta del repo (instalación editable en el venv). Lo corregí sin `-I` (como
  resuelve `python -m pytest`, más `pythonpath = "."` de la copia), añadí un `assert` de resolución y el mutante de
  control CTRL, y repetí la medición "antes". Las cifras de la tabla son de esa segunda corrida. Las de la primera
  corrida coincidían (R1 y D8: `6 passed` / `548 passed`).
- La medición de E4 ("sobre el árbol de trabajo, por confirmar sobre el commit") queda confirmada sobre `21e0142`.

# Handoff — BE-32 Fase_H: correo, enlace visible, regla del botón y el mensaje que se envía (con E0)

Commit de la fase: `91af6e8` (`test(email): pin visible link, button rule and the message actually sent`). El mensaje
es el del plan con los dos cambios de E0 punto 7: el párrafo de `built_messages` se sustituye por el de la captura por
posición o por palabra clave, y la última línea queda «Only SMTP is doubled; no assertion reads Spanish text.». El título
no cambia y `<MODELO EJECUTOR>` = `Claude Opus 5.5`. Ejecutor: Claude Opus 5.5 (`fase-ejecutor`). Es la última fase del
plan: `current_target` pasa a `null`.

## Arranque

- `git status --short`: vacío. HEAD `e89a2b0`. `progress.json`: `current_target` = `Fase_H`.
- Base develop (`verificacion.md:223`, la única registrada): `fd144ad`. `git fetch origin` correcto;
  `git rev-parse --short origin/develop` = `fd144ad`; `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `57 files already formatted`; ruff `Found 8 errors.` (8 I001 `app\`); mypy
  `Found 9 errors in 5 files (checked 53 source files)`; `Contracts: 4 kept, 0 broken.`; `548 passed, 5 warnings`;
  `TOTAL 943 23 138 19 96.11%`. Coincide con la fila G de la tabla: la fase G no dejó nada roto.

## Archivos tocados

```text
 tests/test_email.py | 55 ++++++++++++++++++++++++++++++++++++++++++-----------
 1 file changed, 44 insertions(+), 11 deletions(-)
```

`tests/test_email.py`, aplicando E0 (puntos 1–5) sobre el texto original de H:

- `import re`, escrito en la misma escritura que su uso (E1). El hook no borró nada.
- `_AnchorCollector` → `_BodyCollector`. Conserva `anchors` y añade
  `texts: list[tuple[str, dict[str, str | None], str]]` y la etiqueta abierta `_open`. `handle_starttag` guarda
  `(tag, dict(attrs))` como etiqueta abierta y, si es un `<a>`, añade el mismo diccionario a `anchors`.
  `handle_endtag` pone `_open` a `None`. `handle_data` añade `(tag, attrs, data.strip())` solo si hay una etiqueta
  abierta y el texto no está en blanco. Cada método lleva un docstring de una línea.
- `send_message`: el docstring gana `Yields:` / `The autospecced stand-in for FastMail.send_message.`.
- **Sin fixture `built_messages` y sin `patch.object(email_module, "MessageSchema", ...)`** (E0 punto 1). Solo se dobla
  SMTP.
- `_send_and_capture(send_message, first_name=FIRST_NAME)` sigue recibiendo `send_message`. Su cuerpo es el de E0
  punto 2: `call = send_message.await_args` y
  `message: MessageSchema = call.args[0] if call.args else call.kwargs["message"]` (D4). El docstring no cambia.
- `test_dispatches_one_html_message_to_the_recipient`: conserva `send_message.assert_awaited_once_with(message)` y se
  borra `assert isinstance(message.subject, str)`. El docstring no cambia (E0 punto 3).
- `test_body_carries_...`: tras las aserciones del ancla añade
  `assert len([t for tag, _, t in parser.texts if tag == "a"]) == 1` (L14). Después,
  `link_texts = [(tag, attrs) for tag, attrs, text in parser.texts if text == VERIFICATION_LINK]` y
  `assert [tag for tag, _ in link_texts] == ["p"]` (L2–L5). Por último, `p_style = link_texts[0][1].get("style")`, que
  no es `None` y que, normalizado con `" ".join(p_style.split())`, vale
  `"font-size: 12px; color: #006875; word-break: break-all;"` (L17). El docstring es el dictado, partido en dos líneas
  (ver "Desviaciones", punto 1).
- `test_smtp_failure_propagates`: `send_message.assert_awaited_once()` (la `:99` de la base) se sustituye por las tres
  líneas de E0 punto 4: la lectura del mensaje y `assert [recipient.email for recipient in message.recipients] == [RECIPIENT]`.
- `test_body_renders_...` y `test_css_braces_...` siguen recibiendo `send_message` (E0 punto 5). `test_css_braces_...`
  añade `assert re.search(r"\{\s*\}", body) is None` (C10) y `assert re.search(r"\.btn\s*\{", body) is not None` (L15),
  con el docstring dictado.

Ninguna aserción lee texto en español. Se comparan valores que el test suministra (`RECIPIENT`, `VERIFICATION_LINK`),
nombres de etiqueta, CSS, recuentos y la identidad del objeto capturado. El texto del botón se cuenta, pero no se lee.

## RED: mutantes en copia desechable

Hay dos copias fuera del árbol, en el scratchpad de la sesión, las dos sacadas con `git archive HEAD | tar -x` sobre
`e89a2b0`:

- **antes**: el árbol de `e89a2b0` sin cambios (6 tests en el archivo, 548 en la suite).
- **después**: `e89a2b0` con `tests/test_email.py` de la fase copiado encima. `cmp` contra el árbol de trabajo dio
  idéntico, y `git diff --name-only` listaba solo ese archivo. Tras el commit,
  `git show 91af6e8:tests/test_email.py | cmp - <copia>` también da idéntico. La copia "después" es, por tanto, el
  árbol commiteado `91af6e8` (548 en la suite).

El script localiza cada mutante por contenido en `app/core/email.py` (exige exactamente 1 coincidencia), lo aplica y
corre `pytest -q --no-cov -p no:cacheprovider` sobre `tests/test_email.py` y sobre `tests`. Después restaura el archivo
byte a byte en un `finally` y lo comprueba con `assert`. Al final, `cmp` de `app/core/email.py` de las dos copias contra
el repo da idéntico. Usa variables de entorno ficticias (`JWT_SECRET_KEY`, `ALGORITHM=HS256`, `*_EXPIRE_MINUTES`,
`DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`, `CORS_ORIGINS`, `FRONTEND_URL`) y el Python del
`venv/`. `app.core.email` resolvía a la copia en los dos casos (lo imprime el script). El repo nunca llevó un mutante.

Definición de cada mutante (sobre `app/core/email.py`):

- **L4**: el `{verification_link}` del `<p>` de las l.94-95 pasa a `<!-- {verification_link} -->`.
- **L5**: ese `<p>` queda vacío, con `data-link="{verification_link}"`.
- **L14**: `...text-decoration: none;"></a>`, el botón sin texto (l.90).
- **L15**: `.btn {{` → `.button {{` (l.57).
- **L17**: `<p>{verification_link}</p>`, sin `style` (l.94-95).
- **C10**: el cuerpo de `.btn` (l.57-65) vaciado: `.btn {{ }}`.
- **D8**: `await fast_mail.send_message(message.model_copy(update={"subject": "x"}))`.
- **D4**: `await fast_mail.send_message(message=message)`.
- **L2**: el segundo enlace se quita (`<p style=...></p>`).
- **L3**: el segundo enlace se cambia por `{base_url}`.

| Mutante | Antes, archivo (`e89a2b0`, 6 tests) | Después, archivo (`91af6e8`, 6 tests) | Antes, suite (`e89a2b0`) | Después, suite (`91af6e8`) |
|---|---|---|---|---|
| sin mutante | `6 passed` | `6 passed` | `548 passed, 5 warnings` | `548 passed, 5 warnings` |
| L4 | `6 passed` | `1 failed, 5 passed` (body) | `548 passed` | `1 failed, 547 passed` (body) |
| L5 | `6 passed` | `1 failed, 5 passed` (body) | `548 passed` | `1 failed, 547 passed` (body) |
| L14 | `6 passed` | `1 failed, 5 passed` (body) | `548 passed` | `1 failed, 547 passed` (body) |
| L15 | `6 passed` | `1 failed, 5 passed` (css) | `548 passed` | `1 failed, 547 passed` (css) |
| L17 | `6 passed` | `1 failed, 5 passed` (body) | `548 passed` | `1 failed, 547 passed` (body) |
| C10 | `6 passed` | `1 failed, 5 passed` (css) | `548 passed` | `1 failed, 547 passed` (css) |
| D8 | `6 passed` | `6 passed` (vivo: Residuales, E0) | `548 passed` | `548 passed` |
| D4 | `4 failed, 2 passed` (`IndexError`) | `6 passed` (falsa alarma retirada) | `4 failed, 544 passed` | `548 passed` |
| L2 | `1 failed, 5 passed` (body) | `1 failed, 5 passed` (body) | `1 failed, 547 passed` | `1 failed, 547 passed` |
| L3 | `1 failed, 5 passed` (body) | `1 failed, 5 passed` (body) | `1 failed, 547 passed` | `1 failed, 547 passed` |

"body" = `test_body_carries_the_link_in_the_button_and_as_plain_text`; "css" = `test_css_braces_are_rendered_unescaped`.
Las columnas de archivo coinciden fila a fila con la tabla del plan, con la fila D8 corregida por E0 punto 6.

Salida literal del script, estado **antes** (`e89a2b0`):

```text
app.core.email resolves to: C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\596cc4d4-19c0-40a7-9188-e570531e5537\scratchpad\before\app\core\email.py
none | file: 6 passed in 0.09s
none | suite: 548 passed, 5 warnings in 18.26s
L4 | file: 6 passed in 0.11s
L4 | suite: 548 passed, 5 warnings in 19.41s
L5 | file: 6 passed in 0.12s
L5 | suite: 548 passed, 5 warnings in 19.09s
L14 | file: 6 passed in 0.10s
L14 | suite: 548 passed, 5 warnings in 19.24s
L15 | file: 6 passed in 0.10s
L15 | suite: 548 passed, 5 warnings in 19.74s
L17 | file: 6 passed in 0.10s
L17 | suite: 548 passed, 5 warnings in 19.66s
C10 | file: 6 passed in 0.11s
C10 | suite: 548 passed, 5 warnings in 18.40s
D8 | file: 6 passed in 0.09s
D8 | suite: 548 passed, 5 warnings in 19.07s
D4 | file: 4 failed, 2 passed in 0.25s
      FAILED tests/test_email.py::test_dispatches_one_html_message_to_the_recipient
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
      FAILED tests/test_email.py::test_body_renders_a_compound_first_name_verbatim
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - IndexErr...
D4 | suite: 4 failed, 544 passed, 5 warnings in 19.27s
      FAILED tests/test_email.py::test_dispatches_one_html_message_to_the_recipient
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
      FAILED tests/test_email.py::test_body_renders_a_compound_first_name_verbatim
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - IndexErr...
L2 | file: 1 failed, 5 passed in 0.24s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L2 | suite: 1 failed, 547 passed, 5 warnings in 19.10s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L3 | file: 1 failed, 5 passed in 0.35s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L3 | suite: 1 failed, 547 passed, 5 warnings in 19.79s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
all mutants restored byte for byte
before exit 0
```

Salida literal del script, estado **después** (árbol commiteado `91af6e8`):

```text
app.core.email resolves to: C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\596cc4d4-19c0-40a7-9188-e570531e5537\scratchpad\after\app\core\email.py
none | file: 6 passed in 0.13s
none | suite: 548 passed, 5 warnings in 19.45s
L4 | file: 1 failed, 5 passed in 0.24s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L4 | suite: 1 failed, 547 passed, 5 warnings in 19.79s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L5 | file: 1 failed, 5 passed in 0.23s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L5 | suite: 1 failed, 547 passed, 5 warnings in 19.40s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L14 | file: 1 failed, 5 passed in 0.24s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L14 | suite: 1 failed, 547 passed, 5 warnings in 18.74s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L15 | file: 1 failed, 5 passed in 0.27s
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - assert N...
L15 | suite: 1 failed, 547 passed, 5 warnings in 19.18s
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - assert N...
L17 | file: 1 failed, 5 passed in 0.23s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L17 | suite: 1 failed, 547 passed, 5 warnings in 19.63s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
C10 | file: 1 failed, 5 passed in 0.27s
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - assert <...
C10 | suite: 1 failed, 547 passed, 5 warnings in 20.16s
      FAILED tests/test_email.py::test_css_braces_are_rendered_unescaped - assert <...
D8 | file: 6 passed in 0.11s
D8 | suite: 548 passed, 5 warnings in 19.36s
D4 | file: 6 passed in 0.12s
D4 | suite: 548 passed, 5 warnings in 19.36s
L2 | file: 1 failed, 5 passed in 0.27s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L2 | suite: 1 failed, 547 passed, 5 warnings in 19.30s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L3 | file: 1 failed, 5 passed in 0.25s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
L3 | suite: 1 failed, 547 passed, 5 warnings in 19.08s
      FAILED tests/test_email.py::test_body_carries_the_link_in_the_button_and_as_plain_text
all mutants restored byte for byte
after exit 0
```

Un primer intento del estado "antes" se cortó en D4 con `UnicodeDecodeError` al leer la salida de pytest, que la
consola escribió en cp1252. El `finally` restauró la copia (`cmp` contra el repo: idéntico). Añadí
`PYTHONIOENCODING=utf-8` y `errors="replace"` y repetí la medición entera, que es la que se pega arriba. Las filas que
el primer intento sí llegó a medir (none–D8) dieron las mismas cifras.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Medida sobre el árbol de trabajo con `tests/test_email.py` de la fase, que es el contenido de `91af6e8`.

- `ruff format --check`: `57 files already formatted`.
- `ruff check`: `Found 8 errors.`. Las 8 son I001 `:1:1` en `app\api\dependencies.py`, `app\api\routers\audit.py`,
  `app\core\email.py`, `app\db\database.py`, `app\repositories\user_repository.py`, `app\schemas\audit.py`,
  `app\services\audit_service.py` y `app\services\user_service.py`. Ninguna está en `tests\`.
- mypy: `Found 9 errors in 5 files (checked 53 source files)`. Son `app\db\database.py:11`, `app\core\security.py:71`,
  `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95` y `tests\test_user_service.py:105`, `:203`,
  `:280`, `:298`. Los cuatro de tests son los `[arg-type]` `str | None` de `SECRET_KEY` (`jwt.decode(..., SECRET_KEY,
  ...)` en 105 y 203; `SECRET_KEY,` de `jwt.encode` en 280 y 298). Es el conjunto de A4.
- import-linter: `Contracts: 4 kept, 0 broken.`
- pytest: `548 passed, 5 warnings in 19.18s`. Los 5 avisos son `StarletteDeprecationWarning`
  (`HTTP_422_UNPROCESSABLE_ENTITY`), los mismos 5 tests que antes, y no hay ningún otro aviso.
- Cobertura: `TOTAL 943 23 138 19 96.11%` (antes: 96.11 %).

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

Archivo tocado:

- `ruff check tests/test_email.py` → `All checks passed!`.
- `ruff format --check tests/test_email.py` → `1 file already formatted`.
- `mypy tests/test_email.py` → `Success: no issues found in 1 source file`.

Criterio de aceptación de H: `grep -cE "isinstance\(message\.subject, str\)|await_args\.args\[0\]" tests/test_email.py`
→ `0`. Siguen los 5 `StarletteDeprecationWarning`. El patrón 7 lista una sola línea, `tests\conftest.py:86 override_get_db`.

Checklist de `test-sanitizer` (Enterprise Test Standards): el único doble es `send_message`, con `autospec=True`, que es
infraestructura externa (SMTP). No se construyen usuarios ni tokens. Nombres, docstrings y comentarios están en inglés.
No se afirma sobre texto en español. No hubo que reescribir ningún test que ya cumpliera. Una nota: la lectura
`call.args[0] if call.args else call.kwargs["message"]` aparece dos veces, en `_send_and_capture` y en
`test_smtp_failure_propagates`. Así lo dictan E0 puntos 2 y 4. El segundo no puede usar el helper, porque la llamada
lanza antes de devolver.

## Verificación final (todas las fases, sobre el árbol `91af6e8`)

| # | Patrón | Esperado | Obtenido |
|---|---|---|---|
| 1 | `grep -rnE "\.assert_(called\|awaited)(_once)?\(\)" tests/ --include=*.py \| wc -l` | 0 | `0` |
| 1b | `grep -rnE -A1 "\.assert_not_called\(\)" tests/ ... \| grep -cE "assert_not_awaited"` | 0 | `0` |
| 2 | copias en `test_user_access_policy.py` | 0 | `0` |
| 2 | los tres en `test_auth.py` | 3 | `3` |
| 2 | `assert users\[0\].cedula == admin.cedula` en `test_auth.py` / `test_user_access_policy.py` | 1 y 0 | `tests/test_auth.py:1`, `tests/test_user_access_policy.py:0` |
| 3 | `ruff check tests/` | `All checks passed!` | `All checks passed!` |
| 3 | `ruff check . --output-format=concise \| grep -c "I001"` | 8, todas `app\...:1:1` | `8`, todas `app\...:1:1: I001` |
| 4 | `sqlalchemy.future` en `tests/` | 0 | `0` |
| 5 | comentario en español | 0 | `0` |
| 6 | `grep -n "^files = " pyproject.toml` | `94:files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]` | `94:files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]` |
| 6 | `mypy` | `Found 9 errors in 5 files (checked 53 source files)`, conjunto de A4 | `Found 9 errors in 5 files (checked 53 source files)`: `app\db\database.py:11`, `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`, `tests\test_user_service.py:105`, `:203`, `:280`, `:298` |
| 7 | generadores sin `Yields:` (AST) | `tests\conftest.py:86 override_get_db` | `tests\conftest.py:86 override_get_db` |
| 8 | `def test_role_guard_for_non_superadmins_runs_before_the_self_role_guard` | 1 | `1` |
| 9b-B | `StaleDataError` en `service_repository.py` | 1 | `1` |
| 9b-C | `expired\.value\.detail != corrupt\.value\.detail` | 1 | `1` |
| 9b-C | `assert corrupt.json()["detail"] == unknown.json()["detail"]` | 1 | `1` |
| 9b-C | `persist_user\([^)]*deleted_at` | 3 | `3` (`test_auth.py:306`, `test_token_failure_paths.py:162`, `test_user_response.py:116`) |
| 9b-D | `isinstance\(message\.subject, str\)\|await_args\.args\[0\]` en `test_email.py` | 0 | `0` |
| 9c | `expires_delta` en `conftest.py` | 3 | `3` |
| 9c | `make_token(user, expires_delta=` | 1 | `1` |
| 9c | `jwt.encode` en `tests/` | 2 (`test_user_service.py:274`, `:292`) | `2` (`tests/test_user_service.py:274`, `:292`) |
| 9d | ids de la regla vieja | 0 | `0` |
| 10 | `git diff --stat fd144ad -- app/` | `1 file changed, 3 insertions(+)` (E2) | `app/repositories/service_repository.py \| 3 +++` / `1 file changed, 3 insertions(+)` |
| 11 | compuerta | exit 1 por ruff check y mypy; 4 kept; 548 passed; cobertura ≥ 96.11 % | exit 1 (`ruff check, mypy`); `4 kept, 0 broken`; `548 passed`; `96.11%` |

Todas las cifras coinciden. El patrón 1 llega a 0 en esta fase, como anotó la auditoría de D.

## Desviaciones y dudas

1. **El docstring dictado de `test_body_carries_...` no cabe en 100 columnas.** En una línea ocupa 101 (E501). Lo
   partí sin cambiar ninguna palabra: `"""The link is the button's href and, once, visible text in a styled <p>; the
   button` / `has text.` / `"""`. `ruff format` no parte docstrings, así que no había un "corte que deje ruff format".
   Es el mismo tipo de ajuste que E2 registró para la fase F.
2. **El primer párrafo del commit sigue nombrando D8.** E0 punto 7 cambia solo dos cosas, el párrafo de
   `built_messages` y la última línea, y apliqué exactamente esas dos. Pero el primer párrafo sigue enumerando «and a
   copy of the message sent instead of the one built» entre los correos rotos que los tests dejaban pasar, y el título
   dice «and the message actually sent». Tras E0, D8 sigue vivo. La frase describe correctamente lo que los tests de
   antes dejaban pasar, pero un lector puede entender que este commit lo arregla. No me aparté de E0. El auditor decide
   si es un opcional.
3. `p_style` se lee con `.get("style")` en lugar de `["style"]`. Así un `<p>` sin `style` (L17) falla en la aserción
   `is not None` y no con un `KeyError`. El plan no dicta la forma de la lectura.
4. El docstring de `_send_and_capture` no cambia. Sigue siendo cierto («returns the message it handed to the SMTP
   client») y el plan no lo dicta.

## Residuales

- **D8** (enviar una copia del mensaje con otro asunto) sigue vivo: matarlo exige suplantar la clase `MessageSchema`
  dentro de `email.py`; declarado inmatable por E0, como D1 y U1. Medido: `6 passed` antes y después, en el archivo y en
  la suite (548). Es la fila dictada por E0 punto 9.
- `send_message.assert_awaited_once_with(message)` en `test_dispatches_...` es tautológico frente a D8, como declara E0
  punto 3: compara lo enviado consigo mismo. Se mantiene porque fija una sola llamada con ese objeto.
- Ocultar el `<p>` con una regla CSS de clase sigue sin detectarse, como prevén los Residuales del plan (revisión
  visual del correo).
- Para el cierre del ítem: los Residuales del plan y las notas de E2 (BE-31, A4, AF-08 y el docstring «this id's of
  two») siguen pendientes. No son de esta fase.

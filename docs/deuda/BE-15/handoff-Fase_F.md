# Handoff — BE-15 Fase F: una sesión por petición para la app (más la enmienda E2)

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commits:**
  - `22d9a22` `test(conftest): give each request its own session, apart from the test's`
  - `2c8e3d5` `docs(adr): add ADR-0011, the app and the test use separate sessions`

  Cuerpos idénticos a los bloques del plan: `diff` de `git log -1 --format=%B` sin el trailer contra el bloque
  extraído del plan → `22d9a22 MSG IDENTICAL`, `2c8e3d5 MSG IDENTICAL`.
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` vacío; HEAD `70b0f2e`; `current_target` = `Fase_F`. Compuerta de arranque igual
  a la fila D-bis: 392 passed, 94.81 %, 4 KEPT, ruff 54 (tests/ 1), mypy 10.
- F se ejecutó completa, así que F-mínima no se ejecuta (excluyentes, decisión 6). En `progress.json`, `Fase_F_min`
  queda `completed` con el hash de test de F (`22d9a22`), como dicta su descripción.

## Archivos tocados

Solo los tres que el plan asigna a la fase. No se usó el hueco de dos archivos de test más.

```
$ git show --stat 22d9a22
 tests/conftest.py               | 26 +++++++++++++++----
 tests/test_fixtures_contract.py | 55 +++++++++++++++++++++++++++++++++++++++--
 2 files changed, 74 insertions(+), 7 deletions(-)

$ git show --stat 2c8e3d5
 ...011-sesion-de-la-app-distinta-de-la-del-test.md | 47 ++++++++++++++++++++++
 1 file changed, 47 insertions(+)
```

Finales de línea: `git ls-files --eol` → `i/lf w/lf` en los tres archivos y en `progress.json`.

## Cambios

- `tests/conftest.py`:
  - `client` ya no recibe `db_session`. `override_get_db` hace `async with TestingSessionLocal() as session:
    yield session`.
  - La docstring de `client` enuncia las dos reglas (commit antes de la petición, `persist_user` ya lo hace; refresh
    después) y cita ADR-0011. La de `db_session` dice que es la sesión del test y que la app nunca la recibe.
  - E2: la docstring de `mock_send_email` recibe `Yields:` con `The autospecced stand-in for
    send_verification_email.`. Nada más cambia en ese fixture.
- `tests/test_fixtures_contract.py`:
  - Fuera `from unittest.mock import MagicMock`. Dentro `from typing import Any` y `from app.core.email import
    send_verification_email as real_send_verification_email`.
  - Imports que necesitan los tests de sesión: `from sqlalchemy import func, select`, `get_db` y `User`.
  - `mock_send_email: MagicMock` pasa a `mock_send_email: Any`.
  - 4 tests nuevos: `test_email_dispatch_is_patched_without_requesting_the_fixture` (síncrono, sin parámetros),
    `test_each_request_gets_its_own_session`, `test_app_flush_without_commit_is_invisible_to_the_test` y
    `test_app_commit_is_visible_to_the_test`.
  - Los tres de sesión reciben `client` (instala el override) y `db_session`. Obtienen el generador con
    `app.dependency_overrides[get_db]()`, `anext` y lo cierran con `aclose()`.
- `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`: copia byte a byte del borrador con los dos cambios
  del plan. `diff` borrador → ADR:

  ```
  1,5c1
  < # ADR-0011 — La app y el test usan sesiones distintas en la suite (borrador)
  <
  < > Borrador de la fase F de BE-15. La fase F lo copia a `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`
  < > con dos cambios: borra este bloque de cita y quita " (borrador)" del título. Si la fase F se recorta, el borrador se
  < > queda aquí y no se copia.
  ---
  > # ADR-0011 — La app y el test usan sesiones distintas en la suite
  ```

  El borrador se queda en `docs/deuda/BE-15/` como registro.

## RED → GREEN (tests 1 y 2)

Los tests se escribieron primero, con el `conftest.py` de HEAD `70b0f2e`:

```
E       assert <sqlalchemy.ext.asyncio.session.AsyncSession object at 0x00000197E8699940> is not <sqlalchemy.ext.asyncio.session.AsyncSession object at 0x00000197E8699940>
E       assert 1 == 0
FAILED tests/test_fixtures_contract.py::test_each_request_gets_its_own_session
FAILED tests/test_fixtures_contract.py::test_app_flush_without_commit_is_invisible_to_the_test
2 failed, 7 passed in 0.24s
```

Fallan exactamente el 1 (la sesión de la petición es `db_session`) y el 2 (el `flush` sin `commit` se ve: 1 fila).
El 3 y el 4 pasan, como prevé el plan. Tras el cambio en `conftest.py`: `9 passed in 0.14s`. La suite completa da
`396 passed`.

## Tests rotos por la sesión por petición

**Ninguno.** Con el override nuevo, la suite completa dio `396 passed, 5 warnings` a la primera. Eso incluye los
tests añadidos desde el ensayo en seco: C, D, E y D-bis. No hizo falta añadir `refresh` en ningún archivo. Los
mutantes de fila de D-bis siguen dando sus cifras con la sesión nueva (punto 6c).

## Test 4 (E2): mutación de auditoría sin editar el repo

- `H=ffc3e713e7a13c2f3226ff057a4ac885482c5724` (`git hash-object tests/conftest.py` tras las ediciones).
- Plugin: `C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\b26168e9-94c0-4f60-87ec-a1857cacccf0\scratchpad\f_be15_no_autouse.py`.
  Es una copia de ese `conftest.py` con una sola sustitución, `@pytest.fixture(autouse=True)\ndef mock_send_email():`
  por `@pytest.fixture\ndef mock_send_email():`. `diff` contra el repo: `128c128 < @pytest.fixture(autouse=True)
  --- > @pytest.fixture`.
- El nombre lleva el prefijo `f_` en lugar de `be15_no_autouse` porque el scratchpad es compartido (instrucción del
  orquestador).

```
$ PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --noconftest -p f_be15_no_autouse tests/test_fixtures_contract.py -rf
FAILED tests/test_fixtures_contract.py::test_email_dispatch_is_patched_without_requesting_the_fixture
1 failed, 8 passed in 0.24s
$ ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_fixtures_contract.py
9 passed in 0.12s
```

## Salvaguarda

Antes del commit:

```
$ test "$(git hash-object tests/conftest.py)" = "$H" && echo IGUAL
IGUAL
$ grep -B1 -E "^def mock_send_email\(" tests/conftest.py | grep -c "@pytest.fixture(autouse=True)"
1
```

Tras el commit `22d9a22`:

```
$ test "$(git hash-object tests/conftest.py)" = "$(git rev-parse HEAD:tests/conftest.py)" && echo IGUAL
IGUAL
```

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, tras los dos commits; exit 1 por la deuda heredada)

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

```
53 files already formatted
Found 54 errors.
Found 10 errors in 5 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
--- docs (coherencia): OK en 0.1s
TOTAL                                        942     34    136     22  94.81%
Required test coverage of 92.0% reached. Total coverage: 94.81%
396 passed, 5 warnings in 11.16s
```

La fila "Fase F" sale exacta: 396 passed; ruff 54 en total (`ruff check tests/` → `Found 1 error.`, el I001
heredado de `test_user_service.py:3`); mypy 10; cobertura 94.81 %; 4 KEPT. En los archivos tocados,
`ruff check tests/conftest.py tests/test_fixtures_contract.py` → `All checks passed!` y `ruff format --check` →
`2 files already formatted`.

## Verificación final (completa: F es la última fase)

La ejecuté con la rama tras los dos commits de F. El script está en
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\b26168e9-94c0-4f60-87ec-a1857cacccf0\scratchpad\f_verif.sh`.
El punto 4b usa `f_be15_no_autouse` y el 6c, `dbis_mutants.py` del scratchpad. Salida literal:

```
# 1
0
# 2
0
tests/conftest.py:140:    with patch("app.api.routers.user.send_verification_email", autospec=True) as mock:
# 3
0
0
0
0
# 4
tests/conftest.py:129:def mock_send_email():
1
# 4b
1
0
1
1
1 failed, 8 passed in 0.26s
IGUAL
# 5
0
tests/test_services.py:718:    assert body["name"] == "Tour corto"
tests/test_services.py:722:    assert package.name == "Tour corto"
# 6
0
0
# 6b
1
0
19 tests collected in 0.01s
# 6c
0
9
1
1
extra_key_403: 2 failed, 2 passed, 15 deselected in 0.40s
detail_not_str_403: 2 failed, 2 passed, 15 deselected in 0.40s
recover_no_message: 1 failed, 3 passed, 15 deselected in 0.40s
recover_message_not_str: 1 failed, 3 passed, 15 deselected in 0.40s
row_role: 1 failed, 3 passed, 15 deselected in 0.41s
row_is_active: 1 failed, 3 passed, 15 deselected in 0.40s
row_deleted_at: 1 failed, 3 passed, 15 deselected in 0.41s
# 7
10
# 8
10
# 9
9
# 10
0
2
# 11
1
0
0
1
# 12
Found 1 error.
Found 54 errors.
# 13
# 13 end
# 14
IGUAL
```

El punto 15 es la compuerta de arriba. Todas las cifras coinciden con las que espera el plan. El 13 sale vacío entre
sus marcas: `app/`, la configuración, el CI y las reglas de agentes no se tocaron desde `7877829`.

## Residuales y hallazgos

1. **mypy sobre `test_fixtures_contract.py` invocado a mano.** El protocolo pide `python -m mypy <archivos
   tocados>`. `tests/` no entra en el alcance de mypy (`pyproject.toml`, `files = ["app", ...]`), así que el total
   de la compuerta sigue en 10. Aun así, `./venv/Scripts/python.exe -m mypy tests/conftest.py
   tests/test_fixtures_contract.py` da 3 errores en `tests/`:
   ```
   tests\test_fixtures_contract.py:59: error: Unexpected keyword argument "recipient" for "send_verification_email"  [call-arg]
   tests\test_fixtures_contract.py:61: error: "Callable[[str, str, str, str], Coroutine[Any, Any, Any]]" has no attribute "assert_not_called"  [attr-defined]
   tests\conftest.py:239: error: Returning Any from function declared to return "User"  [no-any-return]
   ```
   - Los dos de `test_fixtures_contract.py` vienen de la anotación `Any` que dicta E2. Tras `assert
     user_router.send_verification_email is mock_send_email` (l.56), mypy estrecha el `Any` al tipo de la función
     real. La llamada de l.59 tiene la firma mal a propósito (el test espera `TypeError`).
   - Con la anotación `MagicMock` de HEAD `70b0f2e`, ese archivo daba 0 errores. Lo comprobé con una copia temporal
     en `tests/_f_head_probe.py`, que borré enseguida y nunca entró en ningún commit; `git status` quedó limpio.
   - `conftest.py:239` es `persist_user`, preexistente y fuera de lo que toca la fase.
   - No lo cambié: el plan dicta `Any` literalmente, y la decisión 8 mide mypy por el total de la compuerta.
   - Si se quiere mypy limpio en `tests/` el día que entre en su alcance, la salida sería un `cast` o una variable
     tipada después de la aserción de identidad. Es una decisión para David o para el auditor.
2. Siguen los residuales del plan, sin cambios: 10 aserciones de mock sin argumentos, el I001 de
   `test_user_service.py:3`, `sqlalchemy.future` en `test_services.py` y `test_user_access_policy.py`, los tests
   HTTP duplicados, el comentario en español de `test_audit.py:37` y las claves en español de la recuperación (P2).
3. Llevar las dos reglas de ADR-0011 a AGENTS §5 queda para **David**, en un PR al cierre de BE-15. Ninguna fase
   edita `AGENTS.md`.

## Desviaciones declaradas

- El plugin de la mutación se llama `f_be15_no_autouse.py` y no `be15_no_autouse.py`, por el scratchpad compartido.
  El contenido es el que dicta el plan.
- `current_target` pasa a `"Auditoria"`, porque no queda ninguna fase. Sigo el precedente de
  `docs/deuda/AF-05/progress.json`; la siguiente etapa es `/auditar BE-15 F`.
- Los tests de sesión importan `func`, `select`, `get_db` y `User` además de lo que el plan lista para E2. Los
  tests 1 a 3 los necesitan tal como el plan los describe.
- Una copia temporal dentro de `tests/` para medir mypy en la versión de HEAD (residual 1). La borré enseguida y
  nunca se añadió a git.

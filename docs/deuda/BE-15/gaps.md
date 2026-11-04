# GAPS — BE-15

Un solo archivo por ID. Cada auditoría añade su bloque; los bloqueantes corregidos se marcan `RESUELTO (<hash>)` y
no se borran.

## Auditoría Fase A — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 1 opcional).
- **Auditado:** `9484b04` (fase) y `68cf40c` (registro en `progress.json` y handoff). Base de la fase: `987e568`.
- **Árbol:** `git status --short` vacío antes y después de la auditoría.

### Evidencia

- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1, rojo heredado previsto por la
  decisión 8 del plan):

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

  | Medida | Línea base (`verificacion.md`) | Auditoría | Fila "Fase A" del plan | Handoff |
  |---|---|---|---|---|
  | pytest | 376 passed | `380 passed, 5 warnings in 19.90s` | 380 | 380 |
  | Cobertura | 94.81 % | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | 4 kept | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | 60 | `Found 60 errors.` | 60 | 60 |
  | ruff en `tests/` | 7 | `Found 7 errors.` (test_audit 1, test_auth 3, test_user_access_policy 2, test_user_service 1) | 7 | 7 |
  | mypy | 10 | `Found 10 errors in 5 files (checked 35 source files)` | 10 | 10 |
  | ruff format | OK | `53 files already formatted` | OK | OK |

- Archivos tocados: `ruff check tests/conftest.py tests/test_services.py tests/test_fixtures_contract.py` →
  `All checks passed!`; `ruff format --check` de los tres → `3 files already formatted`.
- `git show --stat 9484b04` → exactamente `tests/conftest.py`, `tests/test_fixtures_contract.py` (nuevo),
  `tests/test_services.py`. `git diff --stat 987e568..HEAD -- app/ AGENTS.md CLAUDE.md pyproject.toml scripts/
  .azure-pipelines/ .claude/` → vacío.
- Mensaje de commit: el cuerpo de `9484b04` (sin el trailer `Co-Authored-By`) es idéntico byte a byte al bloque
  "Commit" de la fase A en `plan.md:199-213` (`diff` → sin diferencias).
- Cambios exactos, todos presentes en el diff: `create_autospec(AzureStorageClient, instance=True)`
  (`tests/conftest.py:85`); `upload_image.return_value` con la misma URL (`:88-90`); `delete_image.return_value =
  None` (`:91`); `promote_to_permanent.side_effect = mock_promote` (`:97`); `is_temporal_url`/`is_permanent_url`
  como `.side_effect` con los mismos prefijos (`:101-106`); asignaciones de `container_name` borradas
  (`grep -rn container_name tests/` → solo `.pyc`); docstring sin "environment variables" (`:77-83`); imports
  `create_autospec` y `AzureStorageClient` (`:2`, `:12`), sin `AsyncMock`/`MagicMock`. `tests/test_services.py:234`
  usa `failing_client.upload_image.side_effect = StorageUnavailableError("cdn outage")` y la l.11 ya no importa
  `AsyncMock`. `tests/test_fixtures_contract.py`: docstring de módulo literal del plan y los 4 tests a nivel de
  módulo con los nombres del plan, todos vía `app.dependency_overrides[get_storage_client]()`.
- RED reproducido por el auditor con el `conftest.py` de `987e568` cargado como plugin (`pytest --noconftest -p
  be15_base_conftest tests/test_fixtures_contract.py`): `3 failed, 1 passed`; fallan los tests 1-3 (el 3 con
  `Failed: DID NOT RAISE <class 'TypeError'>`), pasa el 4. GREEN: `tests/test_fixtures_contract.py
  tests/test_services.py` → `40 passed`; `test_services.py` sigue con `36 tests collected`.
- Criterio de aceptación: `grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py | wc -l`
  → `0`.
- `progress.json`: JSON válido; `Fase_A` = `completed` con `commit` `9484b04` (real); `current_target` = `Fase_B`;
  `last_handoff` presente; `edit_rules` y `approval` sin cambios respecto a `987e568` (el diff solo toca esos cuatro
  campos).
- AGENTS §5: el doble y el de `test_services.py:233` son `create_autospec`; el test 4 verifica el mock con
  `assert_awaited_once_with(TEMP)`; ninguna aserción sobre texto en español; docstrings en inglés; sin clases.

### Hallazgos

- [OPCIONAL] — Fase A — `mypy` sobre los archivos de test tocados da 2 errores: `tests/test_services.py:183`
  (`Value of type "object" is not indexable [index]`) y `tests/conftest.py:210` (`Returning Any from function
  declared to return "User" [no-any-return]`). ADR-0005 (`docs/adr/0005-trinquete-de-calidad-contra-la-linea-base.md:13`)
  pide 0 errores de mypy en los archivos tocados, pero `tests/` está fuera del alcance configurado de mypy
  (`pyproject.toml:90`, `files = ["app", ...]`), ninguno cae en las líneas del diff y los dos ya estaban en `987e568`
  (comprobado por el auditor sobre `git show 987e568:tests/...`: `test_services.py:183` y `conftest.py:206`). No los
  introduce la fase y el plan aprobado fija mypy = 10 en el alcance de la compuerta. Destino: residual, junto con la
  entrada de `tests/` en el alcance de mypy (PLAN día 4-5), no se exige corrección en BE-15.

## Auditoría Fase B — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 1 opcional).
- **Auditado:** `fc06d1e` (fase) y `9b69358` (registro en `progress.json` y handoff). Base de la fase: `68cf40c`.
  `35e2627` (gaps de la fase A, commit de David) solo toca `docs/deuda/BE-15/gaps.md`.
- **Árbol:** `git status --short` vacío antes de la auditoría.
- **Bloqueantes anteriores:** ninguno (la fase A cerró en PASS).

### Evidencia

- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1, rojo heredado previsto por la
  decisión 8 del plan):

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

  | Medida | Línea base (`verificacion.md`) | Auditoría | Fila "Fase B" del plan (`plan.md:68`) | Handoff |
  |---|---|---|---|---|
  | pytest | 376 passed | `380 passed, 5 warnings in 16.56s` | 380 | 380 |
  | Cobertura | 94.81 % | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | 4 kept | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | 60 | `Found 59 errors.` | 59 | 59 |
  | ruff en `tests/` | 7 | `Found 6 errors.` (test_auth 1/50/162, test_user_access_policy 347/395, test_user_service 3) | 6 | 6 |
  | mypy | 10 | `Found 10 errors in 5 files (checked 35 source files)` | 10 | 10 |
  | ruff format | OK | `53 files already formatted` | OK | OK |

- Archivos tocados: `ruff check tests/test_services.py tests/test_audit.py` → `All checks passed!`;
  `ruff format --check` de los dos → `2 files already formatted`. Los dos archivos solos: `42 passed`.
- `git show --stat fc06d1e` → exactamente `tests/test_audit.py` y `tests/test_services.py`. `git diff --stat
  68cf40c fc06d1e -- app/ AGENTS.md CLAUDE.md pyproject.toml scripts/ .azure-pipelines/ .claude/
  tests/conftest.py` → vacío. `git diff --name-only 68cf40c HEAD` → solo esos dos tests más `gaps.md`,
  `handoff-Fase_B.md` y `progress.json`.
- Mensaje de commit: el cuerpo de `fc06d1e` (sin el trailer `Co-Authored-By`) es idéntico byte a byte al bloque
  "Commit" de la fase B (`plan.md:238-252`; `diff` → sin diferencias).
- Fin de línea: `git cat-file blob` de los dos archivos en `68cf40c` y en `fc06d1e` → 0 bytes `\r`; working tree → 0;
  `git ls-files --eol` → `i/lf w/lf eol=lf`; `git diff --ignore-cr-at-eol --stat 68cf40c fc06d1e` igual al `--stat`
  normal (48+/108-). La conversión CRLF→LF que menciona el handoff no dejó rastro en el commit.
- Collect-only reproducido por el auditor: `git archive 68cf40c` y `git archive fc06d1e` extraídos al scratchpad,
  `pytest --collect-only -q -p no:cacheprovider tests/test_services.py tests/test_audit.py` con el `venv` del repo
  (con variables de entorno ficticias de `DATABASE_URL`/`JWT_*`/`MAIL_*`, porque el archivo no lleva `.env`; la
  colección no conecta). Antes `42 tests collected`, después `42 tests collected` (36 + 6); `diff` de las listas de
  IDs → sin diferencias; también idénticas a la colección del working tree. sha256 de las tres listas:
  `325d3bda95f3af090dae831f492518ae614bebd339da4de3b320fea63bcfcb1c`, el mismo del handoff.
- Cambios exactos, todos presentes: `admin_token` y `auth_headers` borrados; `admin_headers` movido sin cambios al
  bloque "TEST FIXTURES" (`tests/test_services.py:33-38`); los 13 tests (`deactivate_and_activate` …
  `update_package_concurrent_reconciliation`) reciben y usan `admin_headers`; imports `create_access_token`,
  `get_password_hash` y `User` fuera (`tests/test_services.py:22-26`). `superadmin_token` borrado;
  `test_audit_trail_creation_and_retrieval(client, persist_user, make_auth_headers)` con `persist_user(role=
  UserRole.superadmin)` + `make_auth_headers` (`tests/test_audit.py:13-19`);
  `test_audit_trail_forbidden_for_tourist` con `persist_user(role=UserRole.tourist)` y la aserción nueva
  `isinstance(response.json()["detail"], str)` (`tests/test_audit.py:49-58`); I001 corregido (imports ordenados,
  `tests/test_audit.py:1-11`).
- Criterio de aceptación: en los dos archivos `User\(` → 0, `create_access_token\(` → 0, `f"Bearer \{` → 0,
  `def (admin_token|auth_headers|superadmin_token)\(` → 0.
- Sin fábricas nuevas: `tests/conftest.py` no cambia en la fase; se usan `persist_user` (`conftest.py:196`) y
  `make_auth_headers` (`conftest.py:180`), que ya existían; `admin_headers` es el fixture local combinador que la
  decisión 2 del plan (`plan.md:35-37`) admite.
- Aserciones (AGENTS §5): el diff no borra ninguna línea `assert`; añade una (`tests/test_audit.py:58`). Conteo de
  `assert`/`.assert_*` en `68cf40c` → `fc06d1e`: `test_services.py` 124 → 124, `test_audit.py` 17 → 18. En los 13
  tests de services solo cambia el nombre del fixture de cabeceras; ninguna aserción sobre texto en español.
- `progress.json`: JSON válido; `Fase_B` = `completed` con `commit` `fc06d1e` (real, `git cat-file -t` → `commit`);
  `current_target` = `Fase_C`; `last_handoff` presente; el diff de `9b69358` solo toca esos cuatro campos
  (`edit_rules` y `approval` intactos).

### Hallazgos

- [OPCIONAL] — Fase B — `mypy tests/test_services.py tests/test_audit.py` da 2 errores en los archivos tocados:
  `tests/test_services.py:157` (`Value of type "object" is not indexable [index]`) y `tests/test_audit.py:72`
  (`Returning Any from function declared to return "AuditRepository" [no-any-return]`). Mismo criterio que el
  OPCIONAL de la fase A: `tests/` está fuera de `[tool.mypy] files` (`pyproject.toml:90`), ninguna de las dos líneas
  está en el diff (`git blame`: `53ca672`, 29 jul, y `e581c6a`, 10 oct) y los dos ya estaban en `68cf40c` (mypy del
  auditor sobre el árbol extraído: `test_services.py:183` y `test_audit.py:98`, mismo mensaje, desplazados 26 líneas).
  Destino: residual con la entrada de `tests/` en el alcance de mypy (PLAN día 4-5); no se exige corrección en BE-15.

## Auditoría Fase C — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 3 opcionales).
- **Auditado:** `bf22982` (fase) y `ec474e5` (registro en `progress.json` y handoff). Base de la fase: `818027a`.
- **Árbol:** `git status --short` vacío antes y después de la auditoría (RED y mutantes con plugins en el
  scratchpad, `--noconftest -p no:cacheprovider`; en el repo solo se escribió este archivo).
- **Bloqueantes anteriores:** ninguno (A y B cerraron en PASS).

### Evidencia

- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 1, rojo heredado previsto por la
  decisión 8 del plan):

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

  | Medida | Línea base (`verificacion.md`) | Auditoría | Fila "Fase C" del plan (`plan.md:69`) | Handoff |
  |---|---|---|---|---|
  | pytest | 376 passed | `381 passed, 5 warnings in 12.04s` | 381 | 381 |
  | Cobertura | 94.81 % | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | 4 kept | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | 60 | `Found 56 errors.` | 56 | 56 |
  | ruff en `tests/` | 7 | `Found 3 errors.` (test_user_access_policy 347/395, test_user_service 3) | 3 | 3 |
  | mypy | 10 | `Found 10 errors in 5 files (checked 35 source files)` (todos en `app/`) | 10 | 10 |
  | ruff format | OK | `53 files already formatted` | OK | OK |

- Archivos tocados: `ruff check` de los cuatro → `All checks passed!` (en `818027a` daban 3: `test_auth.py:1`, `:50`
  y `:162`); `ruff format --check` → `4 files already formatted`. `mypy` de los cuatro (fuera del alcance de la
  compuerta), medido por el auditor sobre `git archive 818027a`: antes 2 errores en `tests/` (`test_auth.py:67`,
  `conftest.py:210`); ahora 1 (`conftest.py:223`, el mismo `no-any-return` heredado del OPCIONAL de la fase A, fuera
  del diff).
- `git show --stat bf22982` → exactamente `tests/conftest.py`, `tests/test_auth.py`,
  `tests/test_fixtures_contract.py` y `tests/test_user_response.py`. `ec474e5` → solo `handoff-Fase_C.md` y
  `progress.json`. `git diff --stat 818027a ec474e5 -- app/ AGENTS.md CLAUDE.md pyproject.toml scripts/
  .azure-pipelines/ .claude/` → vacío.
- Fin de línea: `git ls-files --eol` de los cuatro → `i/lf w/lf attr/text=auto eol=lf`.
- Mensaje de commit: el cuerpo de `bf22982` sin el trailer es idéntico al bloque "Commit" de la fase C
  (`plan.md:292-309`; `diff` → sin diferencias).
- Alcance de `test_auth.py`: todos los hunks de `git diff -U0 818027a bf22982 -- tests/test_auth.py` empiezan en las
  l.1-172 del original (el último es `@@ -172,3 +168,2 @@`). `diff` entre `git show 818027a:tests/test_auth.py | tail
  -n +177` y `git show bf22982:tests/test_auth.py | tail -n +172` → idéntico: la sección RBAC (fase D) no cambia.
- Cambios exactos: fixture `mock_send_email` con `@pytest.fixture(autouse=True)` en la línea anterior a `def
  mock_send_email():` (`tests/conftest.py:115-116`), `patch(..., autospec=True)` y docstring (`:117-125`), import
  `patch` (`:2`). `tests/test_user_response.py`: fixture local borrado e import `ANY` solo (`:12`).
  `tests/test_auth.py`: fixture local y `patch` fuera; `from sqlalchemy import func, select` (`:6`); `jwt`, `ANY`,
  `ALGORITHM` y `SECRET_KEY` (`:3-14`); `PASSWORD = USER_PAYLOAD["password"]` (`:26`); los 8 nombres del plan (`:29`,
  `:54`, `:76`, `:92`, `:102`, `:121`, `:135`, `:150`).
- Criterio de aceptación: `grep -rnE "def mock_send_email\(" tests/` → 1 (`tests/conftest.py:116`); `grep -B1 …
  | grep -c "@pytest.fixture(autouse=True)"` → 1; en `test_auth.py` l.1-171 `["detail"|"message"] ==`, `.lower()` e
  `in response.json()["detail"]` → 0; `sqlalchemy.future` → 0; `noexiste@example.com` → 0; `test_auth.py` →
  `19 tests collected`; `patch(` sin autospec en `tests/` → 0; `MagicMock(` y afines → 0;
  `test_fixtures_contract.py` → 5 tests (A 4 + C 1).
- RED reproducido por el auditor con el `conftest.py` de `818027a` como plugin (`PYTHONPATH=<scratchpad> pytest -q
  -p no:cacheprovider --noconftest -p be15_old_conftest tests/test_fixtures_contract.py`): `E fixture
  'mock_send_email' not found` · `4 passed, 1 error`. GREEN: `test_fixtures_contract.py test_auth.py
  test_user_response.py` → `38 passed`.
- Sensibilidad del test de contrato (mutantes del `conftest.py` actual, cargados como plugin): sin `autospec=True` →
  `1 failed, 4 passed` (lo detecta); sin `autouse=True` → `5 passed` (no lo detecta; ver hallazgo 1).
- Aserción a aserción (l.1-175 de `818027a` → l.1-170 de `bf22982`; líneas `assert`/`mock.assert_*`: 29 → 43):
  - Registro: se conservan las 7 de l.36-43; `assert_called_once()` → `assert_called_once_with(email_to=…,
    first_name="Juan", token=ANY, base_url=ANY)`, que coincide con la firma real (`app/core/email.py:27`) y con la
    llamada del router (`app/api/routers/user.py:71-75`); + fila por cédula con `is_active is False` y
    `role == UserRole.tourist`.
  - Duplicado: texto (l.58) → `set(body) == {"detail"}` + `str`; + primer POST 201, `count(User) == 1` y correo una
    sola vez con argumentos.
  - Verificación: se conservan el 200 y `success`; + `set(body)`; estado vía `refresh(user)` (antes, re-`select`).
  - Token inválido: `"inválido" in ….lower()` (l.85) → forma `{"detail"}` + `str`.
  - Login: se conservan el 200 y `bearer`; `"access_token" in data` → `set(body)` exacto; + claims `sub` y `role`.
  - Inactivo: texto (l.122) → forma; `set(body) == {"detail"}` prueba además que no hay token.
  - Credenciales: texto (l.131) → forma + `www-authenticate == "Bearer"`; el correo inexistente (D3) sigue cubierto
    por HTTP en `tests/test_user_service.py:363-372` (`ghost@example.com`, 401 y cabecera).
  - Auto-borrado: texto (l.160-163) → `message` de tipo `str` + `set(body)`; se conservan `deleted_at`,
    `is_active` y el 401 posterior. `deleted_user is not None` (l.168) queda implícito: `refresh(user)` (`:164`)
    lanza `InvalidRequestError` si la fila desaparece.

  Ninguna aserción de comportamiento se pierde sin sustituto, y ninguna afirma texto en español (`"Juan"` es un dato
  del payload).
- Desviaciones del ejecutor: (1) `USER_PAYLOAD: dict[str, Any]` (`tests/test_auth.py:17`): aceptable, solo es un
  tipo. (2) `assert SECRET_KEY is not None` (`:115`): aceptable; es el estrechamiento de tipo idiomático en pytest,
  no afirma comportamiento ni texto y no puede ocultar nada (el login ya firmó el token con esa clave).
  `typing.cast` sería equivalente y sin coste en ejecución; no se exige. (3a) import del router a nivel de módulo
  (`tests/test_fixtures_contract.py:8`): aceptable, porque importa el módulo y el atributo se resuelve al ejecutar el
  test, así que el `is` ve el parche. (3b) anotación `mock_send_email: MagicMock` (`:50`): OPCIONAL, ver hallazgo 2.
- `progress.json`: JSON válido; `Fase_C` = `completed` con `commit` `bf22982` (real); `current_target` = `Fase_D`;
  `last_handoff` presente; el diff de `ec474e5` solo toca esos cuatro campos (`edit_rules` y `approval` intactos).
- AGENTS §5: doble con `autospec=True`; preparación con `persist_user`/`make_auth_headers`; código HTTP + forma +
  estado (`refresh`, `count`) + mock con argumentos donde interviene el correo; nombres y docstrings en inglés.

### Hallazgos

- [OPCIONAL] — Fase C — `test_email_dispatch_double_is_autouse_and_autospecced` no congela la mitad "autouse" de su
  nombre: al pedir el fixture por parámetro, el parche se activa aunque el fixture no sea `autouse`. Un mutante con
  `@pytest.fixture` sin `autouse=True` da `5 passed` en `tests/test_fixtures_contract.py` y `381 passed` en toda la
  suite. Hoy solo lo vigila el grep 4 de "Verificación final" (`plan.md:502`). Evidencia:
  `tests/test_fixtures_contract.py:50-57`, `tests/conftest.py:115`. El test es el que dicta el plan
  (`plan.md:280-283`). Para congelarlo bastaría un test que no pida el fixture y compruebe que
  `user_router.send_verification_email` no es la función de `app.core.email`. Destino: residual, o la fase F, que ya
  toca ese archivo.
- [OPCIONAL] — Fase C — la anotación `mock_send_email: MagicMock` es inexacta. `patch(autospec=True)` sobre una
  función devuelve una `function` con atributos de mock (`type(m)` → `<class 'function'>`, `isinstance(m,
  MagicMock)` → `False`). No afecta a la ejecución y silencia mypy, pero describe mal el objeto; `Any` sería más
  honesta. Evidencia: `tests/test_fixtures_contract.py:3`, `:50`.
- [OPCIONAL] — Fase C — a la docstring del fixture nuevo le falta la sección `Yields:` (AGENTS §4, Google Style); los
  fixtures vecinos sí llevan `Returns:`. Evidencia: `tests/conftest.py:117-124` frente a `tests/conftest.py:144-148`.
- Sigue abierto, sin cambios, lo de la fase A: el `no-any-return` de `persist_user` se desplazó a
  `tests/conftest.py:223`. No es un hallazgo nuevo.

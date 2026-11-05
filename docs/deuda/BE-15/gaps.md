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

## Auditoría Fase D — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 2 opcionales).
- **Auditado:** `ee9d54b` (fase) y `e1e7df3` (registro en `progress.json` y handoff). Base de la fase: `c699ac6`.
- **Árbol:** `git status --short` vacío antes de la auditoría; HEAD `e1e7df3`, rama `bloque/b-tests`.
- **Bloqueantes anteriores:** ninguno (A, B y C cerraron en PASS).

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

  | Medida | Auditor | Fila "Fase D" | Handoff |
  |---|---|---|---|
  | pytest | `381 passed, 5 warnings in 14.07s` | 381 | 381 |
  | Cobertura | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | `Found 56 errors.` | 56 | 56 |
  | ruff en `tests/` | `Found 3 errors.` | 3 | 3 |
  | mypy | `Found 10 errors in 5 files (checked 35 source files)` (todos en `app/`) | 10 | 10 |

  `ruff check tests/test_auth.py` → `All checks passed!`; `ruff format --check tests/test_auth.py` → `1 file already
  formatted`; `mypy tests/test_auth.py` → 3 errores, los tres en `app/` (`database.py:11`, `security.py:71,87`), 0 en
  el archivo. `git ls-files --eol tests/test_auth.py` → `i/lf w/lf`; 0 `\r` en el blob de `ee9d54b`.
- Commit: `git show --stat ee9d54b` → solo `tests/test_auth.py` (111+/353−). Mensaje (sin el trailer) contra el bloque
  de `plan.md:391-401` con `diff` → idéntico. `e1e7df3` solo toca `handoff-Fase_D.md` y `progress.json`.
- Alcance: hunks de `git diff -U0 c699ac6 ee9d54b -- tests/test_auth.py` → `@@ -11 +10,0 @@` (retirada de
  `create_access_token,`, asignada a D por `plan.md:382`) y, después, desde `@@ -177,…` (primer `def` RBAC); las l.1-171
  de la fase C no cambian salvo ese import. `git diff --stat c699ac6..e1e7df3 -- app/ pyproject.toml scripts/
  .azure-pipelines/ .claude/ AGENTS.md CLAUDE.md tests/conftest.py` → vacío; lo mismo desde `7877829`.
- Red de seguridad (refactor sin RED), reproducida por el auditor: los blobs de `c699ac6` y `ee9d54b` de
  `tests/test_auth.py` extraídos al scratchpad (`audD_before/`, `audD_after/`) y recogidos con `pytest --collect-only
  -q --noconftest` → `19 tests collected` en ambos; `diff` de los nombres: l.1-8 idénticas (fase C), l.9-19 cambian
  1:1 y en el mismo orden que la tabla de `plan.md:368-380`. En el repo: `19 tests collected`.
- Criterio de aceptación sobre `tests/test_auth.py`: `User(` 0; `create_access_token` 0; `f"Bearer {` 0;
  `get_password_hash("pass")` 0; regex de nombres en español (punto 6 de la Verificación final) 0; regex de
  aserciones de texto (punto 5) 0; `jerarqu|superusuario|Violaci` 0; `^async def test_` 19.
- `progress.json`: JSON válido; `Fase_D` = `completed`, `commit` `ee9d54b` (real); `current_target` = `Fase_E`;
  `last_handoff` actualizado; el diff de `e1e7df3` solo toca esos cuatro campos (`edit_rules`, `approval` y las demás
  fases intactos).
- Aserción a aserción (`c699ac6` l.177-657 → `ee9d54b` l.176-408): 1, 2, 3, 8 y 11 conservan todas sus aserciones; 4
  añade `refresh` + `email` en BD; 5, 9 y 10 cambian el texto en español por `set(body) == {"detail"}` + `str` + no
  mutación (`first_name`, `deleted_at`, `count == 1`), que antes no se comprobaba; 6 y 7 pasan de `in`/`not in` a
  igualdad exacta de cédulas, que implica las anteriores (cada cédula tiene un rol fijo y solo existen las filas que
  crea el test: `setup_database` es `autouse` y crea/borra las tablas por test, `tests/conftest.py:33-47`; ningún otro
  fixture `autouse` crea usuarios). En 7 la lista tiene un solo elemento, así que el orden no importa; 6 usa conjunto.
  Ninguna aserción de comportamiento desaparece sin sustituto.
- Sensibilidad de los tres 403 (plugins en el scratchpad, `-p`, sin editar `app/`; `git status` limpio después):
  - `audD_noop_policy` (`assert_can_update`, `assert_can_recover` y `assert_can_provision_admin` sin efecto) → los 3
    tests 403 de `test_auth.py`: `3 failed`.
  - `audD_wrong_reason` (los tres métodos lanzan `AccountNotActiveError`, que también es 403, `app/main.py:127`) → los
    3 tests 403 de `test_auth.py`: `3 passed` (no lo distinguen); los unitarios
    `test_admin_cannot_update_superadmin`, `test_admin_cannot_recover_superadmin` y `test_admin_cannot_provision_admin`
    (`tests/test_user_access_policy.py:115-210`): `3 failed` (sí lo distinguen, por tipo).
- Observaciones de la sesión principal: la 2 (los tres tests que registraban por HTTP probaban la edición de perfil,
  no el alta; el alta y la activación siguen por HTTP en `tests/test_auth.py:28`, `:53`, `:75`, `:120`), la 3 (igualdad
  exacta: dictada por `plan.md:375-376` y determinista) y la 4 (`isinstance` en 9 y 10: forma de la decisión 4;
  `original_first_name`: equivale al literal `"John"` de `tests/conftest.py:162` y no depende de él; docstrings de una
  línea en inglés sin AAA: misma convención que la fase C auditada y que `test_user_access_policy.py`, los tests no son
  API pública) no dan hallazgo.

### Hallazgos

- [OPCIONAL] — Fase D — La afirmación de `plan.md:164-166` y del handoff ("la distinción … la congelan por tipo
  `tests/test_user_access_policy.py:115-216`") es imprecisa: todas las ramas de la política lanzan el mismo
  `AuthorizationError` (`app/services/user_access_policy.py:35,56,61,66,83,98,117`) y esos tests solo hacen
  `pytest.raises(AuthorizationError)`. Lo que sí congelan es el tipo frente a otro `DomainError` en la capa de política
  (mutante `audD_wrong_reason`: 3 unitarios en rojo). Para los tres escenarios HTTP hoy solo hay un `raise` alcanzable
  (el admin pasa `get_current_admin_user`, `app/api/dependencies.py:128-131`; un actor inactivo da 401, `:110-111`), así
  que no hay "403 por la razón equivocada" posible sin cambiar `app/`. Lo que se pierde: un cambio en el servicio o el
  router que devolviera otro 403 (p. ej. `AccountNotActiveError`) antes de llegar a la política pasaría los tres tests
  HTTP (`tests/test_auth.py:272-278`, `:345-351`, `:376-382`; mutante: `3 passed`), y la aserción de texto antigua lo
  habría detectado. Es el coste aceptado de AGENTS §5 (sin texto en español); además, la aserción antigua del PATCH
  tampoco separaba la rama de jerarquía de la de rol (los dos mensajes contienen "Violación de jerarquía", `:57`, `:62`).
  Destino: backlog (si se quiere cerrar: un código de error estable en el cuerpo, que es cambio de contrato y pide ADR,
  o subclases de `AuthorizationError` registradas en `_DOMAIN_ERROR_STATUS`).
- [OPCIONAL] — Fase D — Los tests que la tabla marca "—" conservan aserciones por debajo de la decisión 4 y de AGENTS §5:
  `"detail" in response.json()` en vez de `set(body) == {"detail"}` (`tests/test_auth.py:213`, `:232`); sin
  `set(body)` en la recuperación (`:324-325`); sin comprobar en BD la fila del admin creado (`:404-408`). No es
  bloqueante: el plan dicta "se conservan" (`plan.md:370-372`, `:377`, `:380`). Destino: residual del bloque o
  backlog, junto a las aserciones de mock sin argumentos.

## Auditoría Fase E — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 1 opcional).
- **Auditado:** `84ad522` (fase) y `9e2700f` (registro en `progress.json` y handoff). Base de la fase: `e9904f9`.
- **Árbol:** `git status --short` vacío antes y después de la auditoría; HEAD `9e2700f`, rama `bloque/b-tests`.
- **Bloqueantes anteriores:** ninguno (A, B, C y D cerraron en PASS).

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

  | Medida | Auditor | Fila "Fase E" | Handoff |
  |---|---|---|---|
  | pytest | `392 passed, 5 warnings in 14.41s` | 392 | 392 |
  | Cobertura | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | `Found 54 errors.` | 54 | 54 |
  | ruff en `tests/` | `Found 1 error.` (`tests\test_user_service.py:3:1`, I001 heredado) | 1 | 1 |
  | mypy | `Found 10 errors in 5 files (checked 35 source files)` (todos en `app/`) | 10 | 10 |

  `ruff check tests/test_user_access_policy.py` → `All checks passed!`; `ruff format --check` → `1 file already
  formatted`; `mypy tests/test_user_access_policy.py` → los 10 heredados de `app/`, 0 en `tests/`. `git ls-files --eol`
  del test, el handoff, `progress.json` y `gaps.md` → `i/lf w/lf`; 0 `\r` en el blob de `84ad522`.
- Commit: `git show --stat 84ad522` → solo `tests/test_user_access_policy.py` (225+/2−). Mensaje sin el trailer contra
  `plan.md:451-464` con `diff` → idéntico. `9e2700f` solo toca `handoff-Fase_E.md` y `progress.json`.
- Alcance: `git diff --stat 7877829..HEAD -- app/ pyproject.toml scripts/ .azure-pipelines/ .claude/ AGENTS.md
  CLAUDE.md` → vacío; `git diff --stat e9904f9..HEAD` → los tres archivos citados, ni `tests/conftest.py` ni
  `tests/test_auth.py`. `git log 7877829..HEAD -- app/services/user_access_policy.py` → vacío.
- Salvaguarda E (decisión 9), re-ejecutada: `test "$(git hash-object app/services/user_access_policy.py)" = "$(git
  rev-parse HEAD:app/services/user_access_policy.py)" && echo IGUAL` → `IGUAL`; `git status --short app/` → vacío.
  Hash `eea566b2a738caaeda2d5472937a5c839867b98c` antes y después de todas las corridas de mutantes.
- Cambios exactos: docstrings de l.349 y l.397 con el texto literal de `plan.md:409-410`; `sqlalchemy.future` de l.13
  intacto; imports `datetime`/`UTC` y `AuditAction`/`AuditLog`. `grep -cE "^async def test_b[23]_"` → `10`; 11 casos.
  Los 10 tests (`tests/test_user_access_policy.py:437-653`) tienen el nombre, la petición y todas las aserciones que
  dicta `plan.md:411-431`; usan solo `persist_user`/`make_auth_headers`, `refresh` y `select(AuditLog)`; ningún mock;
  ninguna aserción sobre texto en español (los docstrings y `"Changed"` son inglés).
- Sensibilidad (plugins en el scratchpad, cargados con `-p`, sin editar `app/`):
  - `e_be15_mutants.py` del ejecutor: coincide con `plan.md:433-436` (fixture `autouse` con `monkeypatch.setattr` sobre
    la clase; `assert_can_update` → `return None`; `assert_can_delete` → `raise AuthorizationError()`). Resultado:
    `6 failed, 5 passed, 46 deselected`; fallan 1, 2, 4, 5 y `[admin]`/`[tourist]` de 6; pasan 3, 7, 8, 9, 10. Sin
    plugin: `11 passed, 46 deselected`.
  - `audE_b2_only` (solo `assert_can_update`, con la guarda de rol saltada en auto-edición, la forma previa del bug B2;
    jerarquía e `is_active` reales; `assert_can_delete` real) → `4 failed, 7 passed`: los cuatro B2 de 403, ningún B3.
  - `audE_b3_only` (solo `assert_can_delete`: niega todo borrado de un tercero, la forma previa de B3) →
    `2 failed, 9 passed`: los dos casos de 6, ningún B2.
  - `audE_b3_allow_all` (`assert_can_delete` sin efecto) → `2 failed, 9 passed`: 7 y 8 (los 403 entre pares).
  - `audE_b2_value_based` (la guarda de rol compara el valor con el rol actual en vez de la clave) → `1 failed,
    10 passed`: solo `test_b2_admin_self_role_noop_returns_403`.
- `progress.json`: JSON válido; `Fase_E` = `completed`, `commit` `84ad522` (real); `current_target` = `Fase_F`;
  `last_handoff` actualizado; el diff de `9e2700f` solo toca esos cuatro campos (`edit_rules`, `approval` y las demás
  fases intactos).
- Observación de la sesión principal (no-op de rol): el test 4 lo dicta el plan (`plan.md:417-418`: "Lo que se bloquea
  es la clave, no el valor") y coincide con la política real (`app/services/user_access_policy.py:60`, `"role" in
  update_dict and actor.role != UserRole.superadmin`, sobre un `update_dict` con `exclude_unset=True`,
  `app/services/user_service.py:272`). Es la guarda fail-safe que corrige B2 y la verificación ya la describe
  (`verificacion.md:98-99`). No es decisión del ejecutor. Ver opcional 1.
- Desviaciones declaradas: nombre `e_be15_mutants` (scratchpad compartido; contenido igual al del plan); aserciones
  extra (`isinstance`, `set(body)`, `is_active`, `body["cedula"]`), dentro de la decisión 4 y AGENTS §5, sin cambio en
  el resultado de mutantes; `ids=["admin", "tourist"]`, que solo da nombre a los casos que pide el plan; `-rpf --tb=no`,
  que no cambia la cifra. Ninguna da hallazgo.
- Enmienda E3 / D-bis (`docs/bitacora/2026-11-04.md:210-213`): no está en `plan.md` ni en `progress.json`. El
  `current_target: Fase_F` es correcto según el plan vigente. No hay conflicto mientras E3 no se registre. Al
  registrarla, la enmienda debe añadir la entrada `Fase_D_bis` a `progress.json`, como E2 hizo con `Fase_F_min`, y
  decidir el `current_target`, porque la bitácora deja abierto el orden ("luego D-bis o F").

### Hallazgos

- [OPCIONAL] — Fase E — `test_b2_admin_self_role_noop_returns_403` (`tests/test_user_access_policy.py:501-517`) congela
  una decisión de producto: un admin que reenvía su rol actual (`{"role": "admin"}`) recibe 403. Lo dicta el plan
  (`plan.md:417-418`) y coincide con `app/services/user_access_policy.py:60`. Es el único test que separa una guarda
  por clave de una por valor (mutante `audE_b2_value_based`: `1 failed, 10 passed`). Consecuencia: un cliente que
  envíe el formulario de perfil completo, con `role` incluido, recibirá 403 en la auto-edición de un admin. Es
  defendible como fail-safe, pero si producto quiere aceptar el rol sin cambio, ese cambio va en la política con su
  propio ítem (junto a BE-02), y este test se ajusta a conciencia. Sin acción en BE-15.

## Auditoría Fase D-bis — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 2 opcionales).
- **Auditado:** `c8743ed` (fase) y `0e81c7d` (registro en `progress.json` y handoff). Base de la fase: `f9b850c`;
  enmienda E3 registrada en `a164b7d` (`plan.md` y `progress.json`, sesión principal).
- **Árbol:** `git status --short` vacío antes y después de la auditoría; HEAD `0e81c7d`, rama `bloque/b-tests`.
- **Bloqueantes anteriores:** ninguno (A–E cerraron en PASS). El opcional 2 de la fase D (aserciones conservadas de
  `tests/test_auth.py:213`, `:232`, `:324-325`, `:404-408`) queda atendido por `c8743ed`.

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

  | Medida | Auditor | Fila "Fase D-bis" | Handoff |
  |---|---|---|---|
  | pytest | `392 passed, 5 warnings in 11.09s` | 392 | 392 |
  | Cobertura | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | `Found 54 errors.` | 54 | 54 |
  | ruff en `tests/` | `Found 1 error.` (`tests\test_user_service.py:3:1: I001`, heredado) | 1 | 1 |
  | mypy | `Found 10 errors in 5 files (checked 35 source files)` (todos en `app/`) | 10 | 10 |

  `ruff check tests/test_auth.py` → `All checks passed!`; `ruff format --check tests/test_auth.py` → `1 file already
  formatted`; `mypy tests/test_auth.py` → 3 errores, los tres en `app/` (`database.py:11`, `security.py:71,87`), 0 en
  el archivo. `git ls-files --eol` → `i/lf w/lf` en `tests/test_auth.py`, `progress.json` y `handoff-Fase_D_bis.md`.
- Commit: `git show --stat c8743ed` → solo `tests/test_auth.py` (20+/4−). Mensaje (sin el trailer) contra el bloque de
  `plan.md:611-627` con `diff` → idéntico. `0e81c7d` solo toca `handoff-Fase_D_bis.md` y `progress.json`. `git diff
  --stat f9b850c HEAD -- app/ tests/conftest.py AGENTS.md CLAUDE.md pyproject.toml scripts/ .azure-pipelines/ .claude/
  .github/` → vacío.
- Cambios exactos (`plan.md:503-520`) contra el diff: 1 → `tests/test_auth.py:213-215`; 2 → `:234-236`; 3 →
  `:329-332` (sin `cc`/`correo`/`nombre`/`apellido`); 4 → firma con `db_session` (`:392-394`, reformateada por `ruff
  format`) y el bloque literal del plan en `:420-425`. Las tres aserciones de respuesta del test 4 se conservan
  (`:415-418`). Imports: `diff` de las líneas `from|import` entre `f9b850c` y HEAD → idénticas. Nombres: `diff` de los
  `def test_` → idénticos, 19.
- Criterio de aceptación: `grep -c 'assert "detail" in response.json()'` → 0 (era 2 en `f9b850c`); `grep -c 'set(body)
  == {"detail"}'` → 9 (era 7); `{"success", "message"} <= set(body)` → 1; `select(User).where(User.cedula ==
  "555555")` → 1.
- `progress.json`: JSON válido; `Fase_D_bis` = `completed`, `commit` `c8743ed` (real); `current_target` = `Fase_F`;
  `last_handoff` actualizado; el diff de `0e81c7d` solo toca esos cuatro campos (`edit_rules`, `approval` y las
  demás fases intactos).
- Mutación de auditoría reproducida con un plugin propio (`audDbis_mutants.py` en el scratchpad, lógica literal de
  `plan.md:525-582` más un contador de disparos y dos mutantes de sondeo). "Antes": `tests/test_auth.py` de `f9b850c`
  (hash `0a33509…`, igual al del handoff) junto a una copia de `tests/conftest.py` (hash igual a HEAD) en el
  scratchpad, con `-c pyproject.toml --rootdir .` desde el repo (el árbol de `git archive` no arranca sin `.env`, A4).
  "Después": el repo en HEAD. Sin editar `app/` ni el repo.

  | `DBIS_MUTANT` | Disparos | Antes (`f9b850c`) | Después (HEAD) | Línea que cae |
  |---|---|---|---|---|
  | (vacío) | 0 | `4 passed` | `4 passed` | — |
  | `extra_key_403` | 2 | `4 passed` | `2 failed, 2 passed` | `:214` y `:235` (`set(body)`) |
  | `detail_not_str_403` | 2 | `4 passed` | `2 failed, 2 passed` | `:215` y `:236` (`isinstance`) |
  | `recover_no_message` | 1 | `4 passed` | `1 failed, 3 passed` | `:330` (subconjunto) |
  | `recover_message_not_str` | 1 | `4 passed` | `1 failed, 3 passed` | `:332` (`message` str) |
  | `row_role` | 1 | `4 passed` | `1 failed, 3 passed` | `:423` |
  | `row_is_active` | 1 | `4 passed` | `1 failed, 3 passed` | `:424` |
  | `row_deleted_at` | 1 | `4 passed` | `1 failed, 3 passed` | `:425` |
  | `recover_success_false` (control, auditor) | 1 | `1 failed, 3 passed` | `1 failed, 3 passed` | `:325` / `:331` |
  | `recover_drop_cc` (sondeo, auditor) | 1 | `4 passed` | `4 passed` | — (ver opcional 1) |

  Con `-rf`, el test que cae es siempre el previsto: `test_tourist_self_role_escalation_returns_403_without_mutation`
  y `test_tourist_self_is_active_change_returns_403_without_mutation` (403), `test_admin_recovers_tourist_as_inactive`
  (recuperación), `test_superadmin_provisions_admin_account` (fila). Coincide con `plan.md:590-599` y con el handoff.
- Sondeo del `refresh` del test 4: con `tests/test_auth.py` de HEAD sin la línea `await db_session.refresh(created)`
  (copia en el scratchpad), los tres mutantes de fila siguen dando `1 failed`. Ver opcional 2.
- Diseño de E3 (escrito por la sesión principal, no por el `plan-redactor`):
  - (a) El subconjunto es coherente: la decisión 4 fija la forma del cuerpo; E3 dice "comprueban la forma del cuerpo
    en la recuperación" sin exigir igualdad; el fuera de alcance de D (`plan.md:421-422`) y de D-bis (`:607`) prohíbe
    afirmar las claves en español. La igualdad exacta habría contradicho a D. Deja pasar dos regresiones: que
    desaparezca o se renombre `cc`/`correo`/`nombre`/`apellido` (sondeo `recover_drop_cc`: `4 passed`) y que se añada
    una clave (por ejemplo, un dato sensible: la ruta no tiene `response_model`, `app/api/routers/user.py:216`, y el
    dict se arma a mano, `app/services/user_service.py:359-366`). Ver opcional 1.
  - (b) `isinstance(body["detail"], str)` es aceptable: es una de las formas que nombra la decisión 4 (`plan.md:47-48`),
    E3 pide "elevar a la decisión 4", los 7 casos de C y D ya la llevan junto a `set(body)` (`tests/test_auth.py:65`,
    `:98`, `:131`, `:146`, `:279`, `:355`, `:386`) y el mutante `detail_not_str_403` demuestra que no es redundante con
    `set(body)`.
  - (c) El mutante de fila modela un estado persistido distinto del devuelto (una escritura posterior en la misma
    petición, un valor por defecto de la base o una respuesta construida desde la entrada). Es realista, aunque menos
    frecuente que "no persiste" (que `scalar_one()` también detecta). Tras F sigue siendo válido: la sesión por petición
    sale de `TestingSessionLocal` (`expire_on_commit=False`, `tests/conftest.py:24-27`; `plan.md:57-58`), así que la
    respuesta sigue diciendo admin, y el `select` de la sesión del test lee la fila confirmada.
  - (d) No hay mutante tautológico: cada uno aísla una sola aserción (líneas distintas de la tabla) y el contador de
    disparos confirma que todos se activan antes y después. El plugin del plan no cuenta disparos, así que "Antes = `4
    passed`" no distingue por sí solo entre "sobrevive" y "no se activa"; la columna "Después", con el mismo plugin y
    los mismos flujos, cierra ese hueco. Los greps miden recuentos, no posiciones; el diff confirma las posiciones. La
    explicación de `plan.md:583-585` es inexacta (opcional 2).

### Hallazgos

- [OPCIONAL] — Fase D-bis — El subconjunto `{"success", "message"} <= set(body)` (`tests/test_auth.py:330`) no detecta
  que se pierda o se renombre una clave de datos de la recuperación ni que aparezca una clave extra (sondeo
  `recover_drop_cc`: `4 passed` en HEAD). Es el trade-off consciente de E3 (`plan.md:138-142`). El vínculo con P2 solo
  existe en el residual del plan (`plan.md:859`): la fila P2 del backlog (`docs/backlog.md:93`) no menciona `cc`,
  `correo`, `nombre` ni `apellido`. Destino: cuando los residuales del bloque pasen al backlog, la nota de P2 debe decir
  que, al renombrar esas claves, este test pasa a `set(body) == {...}` exacto. Sin acción en D-bis.
- [OPCIONAL] — Fase D-bis — `plan.md:583-585` afirma que, con los mutantes de fila, "solo la relectura con `refresh` lo
  ve". El sondeo lo desmiente: sin `await db_session.refresh(created)` (`tests/test_auth.py:422`) los tres mutantes de
  fila siguen dando `1 failed`. El `select` ya trae la fila de la base, probablemente porque el objeto de la app sale
  del mapa de identidad (débil) al terminar la petición. El `refresh` es defensivo (ADR-0011, "refresh después"),
  inocuo y válido antes y después de F, pero hoy no es lo que hace caer el test. Sin acción en el código; la ficha o
  la bitácora pueden corregir la explicación.

## Auditoría Fase F — 2026-11-04

- **Veredicto:** PASS (0 bloqueantes, 5 opcionales). F es la última fase: el juicio de cierre de BE-15 va al final.
- **Auditado:** `22d9a22` (test), `2c8e3d5` (ADR) y `2a1ee41` (`progress.json` y handoff). Base de la fase: `70b0f2e`
  (`git rev-parse 22d9a22^`). Base develop: `7877829`.
- **Árbol:** `git status --short` vacío antes y después de la auditoría; HEAD `2a1ee41`, rama `bloque/b-tests`. RED,
  mutantes y sondeos de mypy con plugins y copias en el scratchpad (prefijo `audF_`); en el repo solo se escribió
  este archivo.
- **Bloqueantes anteriores:** ninguno (A–E y D-bis cerraron en PASS). Los opcionales 1, 2 y 3 de la fase C (autouse sin
  vigilar, anotación `MagicMock`, falta de `Yields:`) quedan atendidos por `22d9a22` (enmienda E2).

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

  | Medida | Línea base (`verificacion.md`) | Auditor | Fila "Fase F" (`plan.md:80`) | Handoff |
  |---|---|---|---|---|
  | pytest | 376 passed | `396 passed, 5 warnings in 11.45s` | 396 | 396 |
  | Cobertura | 94.81 % | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % | 94.81 % |
  | import-linter | 4 kept | `Contracts: 4 kept, 0 broken.` | 4 KEPT | 4 KEPT |
  | ruff total | 60 | `Found 54 errors.` | 54 | 54 |
  | ruff en `tests/` | 7 | `Found 1 error.` (I001 heredado de `tests/test_user_service.py:3`) | 1 | 1 |
  | mypy | 10 | `Found 10 errors in 5 files (checked 35 source files)` (todos en `app/`) | 10 | 10 |
  | ruff format | OK | `53 files already formatted` | OK | OK |

  Archivos tocados: `ruff check tests/conftest.py tests/test_fixtures_contract.py` → `All checks passed!`; `ruff
  format --check` → `2 files already formatted`. `git ls-files --eol` → `i/lf w/lf` en los tres archivos de la fase,
  `progress.json` y `handoff-Fase_F.md`.
- Commits: `git show --stat` → `22d9a22` = `tests/conftest.py` + `tests/test_fixtures_contract.py`; `2c8e3d5` = solo
  el ADR; `2a1ee41` = solo `handoff-Fase_F.md` y `progress.json`. No se usó el hueco de dos archivos de test más.
  Mensajes sin el trailer contra `plan.md:693-715` y `:718-726` con `diff` → idénticos los dos.
- Cambios exactos contra el diff: `client()` sin `db_session` y override con `async with TestingSessionLocal() as
  session: yield session` (`tests/conftest.py:62-78`); docstring de `client` con las dos reglas y la cita a ADR-0011
  (`:63-74`); docstring de `db_session` ("the test's own … The app never receives this session", `:52-56`); `Yields:`
  con el texto literal en `mock_send_email` (`:137-138`), sin otro cambio en el fixture. `test_fixtures_contract.py`:
  fuera `MagicMock`, dentro `Any` (`:3`) y `real_send_verification_email` (`:10`); `mock_send_email: Any` (`:54`); los
  4 tests con los nombres del plan (`:64`, `:69`, `:83`, `:96`), los tres de sesión con `client` + `db_session`,
  `app.dependency_overrides[get_db]()`, `anext` y `aclose()`; el 4, síncrono, sin parámetros y con la docstring
  literal.
- (1) RED reproducido por el auditor: `tests/conftest.py` de `70b0f2e` como plugin (`PYTHONPATH=<scratchpad> pytest -q
  -p no:cacheprovider --noconftest -p audF_old_conftest tests/test_fixtures_contract.py -rf`) → `2 failed, 7 passed`;
  caen exactamente `test_each_request_gets_its_own_session` y
  `test_app_flush_without_commit_is_invisible_to_the_test`. Con el `conftest.py` de HEAD → `9 passed`.
- (2) Mutación E2 reproducida con un plugin propio (`audF_no_autouse.py`: el `conftest.py` de HEAD con una sola línea
  cambiada, `diff --strip-trailing-cr` → `128c128 < @pytest.fixture(autouse=True) --- > @pytest.fixture`; idéntico
  al `f_be15_no_autouse.py` del ejecutor) → `1 failed, 8 passed`; cae solo
  `test_email_dispatch_is_patched_without_requesting_the_fixture`. `git hash-object tests/conftest.py` =
  `ffc3e71…` antes y después = `HEAD:tests/conftest.py` → `IGUAL`.
- (3) Verificación final (`plan.md:784-848`) re-ejecutada entera con plugins propios (`audF_no_autouse`,
  `audF_dbis_mutants` extraído de `plan.md:526-581`); cada cifra coincide con la que dicta el plan y con el handoff:
  1 → `0`; 2 → `0` y `tests/conftest.py:140`; 3 → `0 0 0 0`; 4 → `tests/conftest.py:129:def mock_send_email():` y `1`;
  4b → `1 0 1 1`, `1 failed, 8 passed`, `IGUAL`; 5 → `0` y las dos líneas "Tour corto" (`tests/test_services.py:718`,
  `:722`); 6 → `0 0`; 6b → `1 0` y `19 tests collected`; 6c → `0 9 1 1`; mutantes de D-bis con la sesión nueva: vacío
  `4 passed`, `extra_key_403` y `detail_not_str_403` `2 failed, 2 passed` (los dos 403), `recover_no_message` y
  `recover_message_not_str` `1 failed, 3 passed` (recuperación), `row_role`, `row_is_active` y `row_deleted_at` `1
  failed, 3 passed` (`test_superadmin_provisions_admin_account`); 7 → `10`; 8 → `10`; 9 → `9`; 10 → `0` y `2`; 11 →
  `1 0 0 1`; 12 → `Found 1 error.` y `Found 54 errors.`; 13 → vacío; 14 → `IGUAL`; 15 → la compuerta de arriba.
- Sondeo del auditor, el commit olvidado de A3 (el motivo de (4)): plugin `audF_forgot_commit.py` que hace que
  `UserRepository.create_user` haga `flush()` sin `commit()`. Suite completa con HEAD → `1 failed, 395 passed` (cae
  `test_superadmin_provisions_admin_account`, la relectura que añadió D-bis); con el `conftest.py` de `70b0f2e` → `2
  failed, 394 passed` (solo los dos contratos de sesión, que con ese conftest fallan siempre): la sesión compartida lo
  ocultaba y la sesión por petición lo detecta. El registro no cae porque `log_transaction` confirma después de
  `create_user` (`app/services/user_service.py:94-101`), así que ahí no hay commit olvidado.
- ADR-0011: `diff docs/deuda/BE-15/adr-0011-borrador.md docs/adr/0011-…md` → solo `1,5c1` (título sin " (borrador)";
  fuera la línea en blanco y las tres líneas `>`); el resto, byte a byte. Contenido frente a D1 (`plan.md:219-224`):
  decisión (sesión por petición, aparte de la del test), límite aceptado con los tres puntos (conexión compartida por
  `StaticPool`; aislamiento de sesión, no de transacción; commit olvidado detectado al cerrar la sesión de la app),
  las dos reglas en "Consecuencias" y las tres alternativas (sesión compartida, conexiones separadas, PostgreSQL →
  BE-31). Formato: contexto, decisión, consecuencias y alternativas presentes; falta "Evidencia" (opcional 2).
- `progress.json`: JSON válido; `Fase_F` = `completed`, `commit` `"22d9a22 2c8e3d5"` (los dos reales, formato
  `"<test> <docs>"` que dicta `plan.md:691`); `Fase_F_min` = `completed` con `22d9a22`, que es lo que dice su
  descripción ("if Fase_F is completed, mark this completed with Fase_F's test commit hash"), y es necesario para que
  `read_progress` (`scripts/check_docs.py:451-478`) pueda dar el ítem por ejecutado. `current_target` = `"Auditoria"`:
  precedente real en `docs/deuda/AF-05/progress.json:3`. `last_handoff` actualizado. El diff de `2a1ee41` solo toca
  esos campos de las dos fases, `current_target` y `last_handoff`; `edit_rules` y `approval` intactos.
  `check_docs.py --estado` → `BE-15: … en ejecución (objetivo: Auditoria) → handoffs: … Fase_F → …` (ver opcional 4).
- Fuera de alcance intacto: `git diff --stat 7877829..HEAD -- app/ pyproject.toml scripts/ .azure-pipelines/ .claude/
  AGENTS.md CLAUDE.md` → vacío; `git status --short -- app/ AGENTS.md CLAUDE.md` → vacío.
- Desviaciones declaradas: (a) plugin `f_be15_no_autouse.py` en vez de `be15_no_autouse.py`: aceptable, mismo
  contenido (`diff` contra el del auditor → idéntico salvo fin de línea). (b) imports `func`, `select`, `get_db` y
  `User` no listados: aceptable, los tests 1-3 tal como los describe `plan.md:657-664` no se pueden escribir sin ellos;
  0 errores de ruff. (c) copia temporal `tests/_f_head_probe.py`: no está en el árbol (`ls tests/`) ni en ningún commit
  (`git log --all -- tests/_f_head_probe.py` → vacío). Aceptable; nota de proceso: el sondeo cabe en el scratchpad
  (`mypy --cache-dir <scratchpad> <copia>`, como hizo esta auditoría) sin crear nada dentro de `tests/`.
- AGENTS §5 en los 4 tests: sin mocks nuevos; aserciones sobre identidad, recuento y filas (`[row.email for row in
  rows] == [user.email]`, más estricto que "una fila"); nada de texto en español; docstrings en inglés. El test 3 es el
  borde que impide un aislamiento excesivo (un commit sí llega); el 2 es el fallo que (4) quería detectar.

### Hallazgos

- [OPCIONAL] — Fase F — mypy sobre el archivo tocado pasa de 0 a 2 errores: `tests/test_fixtures_contract.py:59`
  (`Unexpected keyword argument "recipient" for "send_verification_email" [call-arg]`) y `:61` (`… has no attribute
  "assert_not_called" [attr-defined]`). Causa: tras `assert user_router.send_verification_email is mock_send_email`
  (`:56`) mypy estrecha el `Any` de E2 al tipo de la función real. La copia de `70b0f2e` da 0 errores en el archivo
  (sondeo del auditor). No bloquea: `tests/` está fuera de `[tool.mypy] files` (`pyproject.toml:90`), la decisión 8 mide
  mypy por el total de la compuerta (sigue en 10) y la anotación es el texto literal de E2; es el mismo criterio de los
  opcionales de A y B. Pero, a diferencia de aquellos, este error lo introduce la fase. El opcional 2 de la fase C
  propuso `Any` sin prever el estrechamiento. Arreglo mínimo, probado en una copia (0 errores en el archivo): tras el
  `is`, `double: Any = user_router.send_verification_email` y usar `double` en `:59` y `:61`. Sin import nuevo. También
  vale `double = cast(Any, mock_send_email)`. Invertir los operandos del `is` no lo arregla. Destino: el próximo PR que
  toque el archivo, como tarde cuando `tests/` entre en mypy (PLAN día 4-5).
- [OPCIONAL] — Fase F — ADR-0011 no tiene sección "Evidencia" (AGENTS §7 la nombra en el formato Nygard). No es
  bloqueante: D1 pidió un ADR "corto" y enumeró su contenido sin evidencia (`plan.md:219-222`), y 5 de los 10 ADR
  aceptados tampoco la tienen (0002, 0005, 0007, 0008, 0009). La evidencia existe: el RED de esta fase (`2 failed, 7
  passed` → `9 passed`), el ensayo en seco del plan (`1 failed, 375 passed`, `plan.md:168-174`) y el sondeo del commit
  olvidado de esta auditoría. Destino: si David la quiere en el ADR, un addendum (ADR-0009, "corregir una omisión"); el
  ADR aceptado no se edita.
- [OPCIONAL] — Fase F — las docstrings reescritas de `client` y `db_session` (`tests/conftest.py:52-56`, `:63-74`) no
  tienen sección `Yields:` (AGENTS §4). Es el mismo defecto que el opcional 3 de la fase C para `mock_send_email`, que
  esta fase corrige; el plan dictó su contenido, no su formato. Destino: el próximo PR que toque `conftest.py`.
- [OPCIONAL] — Fase F — `current_target: "Auditoria"` es válido por el precedente de AF-05, pero `check_docs.py
  --estado` mantiene BE-15 "en ejecución". Los ítems cerrados (`docs/deuda/BE-01/progress.json:3`,
  `docs/deuda/AF-01/progress.json:3`) tienen `null` y salen como "ejecutado (todas las fases); pendiente de PR o
  mezclado". Destino: al cerrar el ítem tras esta auditoría, `current_target` pasa a `null`. Lo decide David, porque
  `edit_rules` reserva ese campo a la sesión que ejecuta una fase.
- [OPCIONAL] — Fase F — ADR-0011 no figura en la tabla de decisiones de `docs/CONTEXT.md` (§6; la fila de ADR-0010
  está en `:234`). Fuera del alcance del plan (`plan.md:233-235`). Destino: el PR de cierre de David, junto a las reglas
  de AGENTS §5.

### Juicio de cierre de BE-15

- Sub-hallazgos de `verificacion.md` (l.8-13):
  - (1) mocks sin spec: **cerrado**. Verificación final 1 → 0 y 2 → 0; un solo `patch`, con autospec
    (`tests/conftest.py:140`).
  - (2) preparación a mano: **cerrado**. Puntos 3 → 0/0/0/0 y 4 → un solo `mock_send_email`.
  - (3) texto en español: **cerrado**. Puntos 5 y 6 → 0; 6c → 9 formas `{"detail"}`.
  - (4) sesión compartida: **cerrado**. Punto 10 → 0/2; RED de F reproducido; el commit olvidado ahora se detecta (sondeo
    de arriba); ADR-0011.
  - (6) B2/B3: **cerrado**. Punto 8 → 10 definiciones (11 casos), sensibilidad por mutantes en E.
  - (5) ya estaba corregido al verificar.
- Residuales del plan (`plan.md:851-861`), sin cambios:
  - 10 aserciones de mock sin argumentos (punto 7). Destino: backlog, `B-TESTS m3`.
  - I001 de `tests/test_user_service.py:3`. Destino: el próximo cambio que toque el archivo.
  - `sqlalchemy.future` en `tests/test_services.py:14` y `tests/test_user_access_policy.py:13`. Destino: S2.
  - Tests HTTP duplicados entre `test_auth.py` y `test_user_access_policy.py`. Destino: backlog, prioridad baja.
  - Comentario en español en `tests/test_audit.py:37`. Destino: el próximo PR que toque el archivo.
  - Claves en español de la recuperación (`cc`, `correo`, `nombre`, `apellido`). Destino: P2.
- Opcionales acumulados A–F y su destino:
  - A y B (mypy en tests heredado: `no-any-return` de `persist_user`, hoy en `tests/conftest.py:239`; `[index]` de
    `test_services.py`; `no-any-return` de `test_audit.py`): con la entrada de `tests/` en mypy (PLAN día 4-5).
  - C 1-3: atendidos en `22d9a22`.
  - D 1 (403 sin distinguir la causa): backlog. Para cerrarlo hace falta un código de error estable con ADR, o
    subclases de `AuthorizationError` registradas.
  - D 2: atendido en `c8743ed`.
  - E 1 (403 con el mismo rol): solo si producto lo cambia, junto a BE-02.
  - D-bis 1 (subconjunto en la recuperación): una nota en la fila P2 del backlog.
  - D-bis 2: corregido en `70b0f2e`.
  - F 1-5: arriba.
- Tarea pendiente de **David**: llevar a AGENTS §5, por PR, las dos reglas de ADR-0011 ("commit antes de la petición",
  "refresh después"), y con ellas la fila de ADR-0011 en CONTEXT §6 y `current_target: null` en `progress.json`.
  Ninguna fase lo hace (decisión 7).
- Veredicto de cierre: BE-15 queda cumplido en lo que el plan exige; el ítem está listo para el PR del bloque: PASS

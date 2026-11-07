# Verificación — BE-32: residuales de la suite (BE-15 + acumulado del 5 y 6 nov)

**Veredicto:** confirmada
**Fuente del ítem:** `docs/backlog.md:70` (fila BE-32, con la nota del 5 nov y la lista acumulada del 6 nov). Origen:
`docs/deuda/BE-15/gaps.md:716-725` (juicio de cierre), `docs/deuda/BE-15/plan.md:851-861` (residuales),
`docs/deuda/BE-33/gaps.md:66-69,142,144-146,251-255` (opcionales de las fases B, C y D) y `docs/bitacora/2026-11-06.md`
(decisiones de David de las 09:15, 11:35, 12:14 y 13:00). No es un tag de auditoría: no aplica el informe HTML.
**Fecha:** 2026-11-07

## Qué describe el ítem
Es una bolsa de residuales de la suite que no cumplen AGENTS §4/§5 y que BE-15 y BE-33 dejaron fuera de su alcance:
aserciones de mock sin argumentos, tests HTTP duplicados, un I001 en `tests/`, `sqlalchemy.future` en tests, un
comentario en español, errores de mypy en `tests/` con `tests/` fuera de `mypy.files`, y `Yields:` que falta en los
fixtures `client` y `db_session`. Se le suman la nota del 5 nov (orden de las guardas de `assert_can_update`) y la lista
del 6 nov: la decisión (a) de meter `tests/` en mypy, los opcionales (b) de BE-33 B/C/D, (c) `make_token` y (d) ids
viejos de `test_check_docs.py`. Todos los subpuntos siguen presentes en el código. Varias líneas se han movido desde que
se escribió la fila y hay ocurrencias que la fila no cuenta (se detallan abajo).

## Evidencia en el código

### 1. Aserciones de mock sin argumentos: hay **11**, no 10
`grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ app/` (0 en `app/`):
- `tests/test_services.py:219` — `failing_client.upload_image.assert_awaited_once()`. La fila decía `:245`. Las líneas
  220-223 sí inspeccionan `call_args.args[0]` (`StagedImage`, filename, content_type, content).
- `tests/test_services.py:486` — `storage_double.upload_image.assert_awaited_once()`. La fila decía `:520`. Las líneas
  487-489 inspeccionan `call_args` (tipo y content_type).
- `tests/test_storage.py:92` — `doubles.source_blob.upload_blob.assert_awaited_once()`. Las líneas 93-95 inspeccionan
  `await_args` (args y `overwrite`), pero no `content_settings`.
- `tests/test_storage.py:159` — `doubles.source_blob.delete_blob.assert_awaited_once()`. No comprueba argumentos.
- `tests/test_storage.py:189` — `doubles.dest_blob.delete_blob.assert_awaited_once()`. No comprueba argumentos.
- `tests/test_storage.py:198` — `doubles.dest_blob.delete_blob.assert_awaited_once()`. No comprueba argumentos.
- `tests/test_user_service.py:110` — `user_repo.create_user.assert_awaited_once()`. El argumento sí se comprueba por
  identidad en `:98` (`result.user is user_repo.create_user.call_args.args[0]`).
- `tests/test_user_service.py:111` — `audit_service.log_transaction.assert_awaited_once()`. No comprueba argumentos.
- `tests/test_user_service.py:328` — `user_repo.create_user.assert_awaited_once()`. El argumento se lee en `:324`
  (`created_user = user_repo.create_user.call_args.args[0]`).
- `tests/test_user_service.py:329` — `audit_service.log_transaction.assert_awaited_once()`. No comprueba argumentos.
- **`tests/test_email.py:99`** — `send_message.assert_awaited_once()`, en `test_smtp_failure_propagates`. Es **nuevo**:
  lo introdujo la fase D de BE-33 y no está en el conteo de la fila. No comprueba argumentos.

### 2. Tests HTTP duplicados entre `test_auth.py` y `test_user_access_policy.py`: hay **3 pares**
- Un admin hace PATCH sobre un superadmin y recibe 403 sin mutación: `tests/test_auth.py:262`
  (`test_admin_patching_superadmin_returns_403_without_mutation`) y `tests/test_user_access_policy.py:314`
  (`test_patch_hierarchy_violation_returns_403_detail`). Mismo payload `{"first_name": "Hacked"}`.
- Un admin crea un admin y recibe 403 sin fila nueva: `tests/test_auth.py:361`
  (`test_admin_provisioning_admin_returns_403_without_row`) y `tests/test_user_access_policy.py:384`
  (`test_admin_cannot_provision_admin_account_403_and_no_db_mutation`).
- **Tercer par, que la fuente no cita:** un admin corrige el email de un turista y el cambio se persiste:
  `tests/test_auth.py:242` (`test_admin_updates_tourist_email_and_persists_it`) y `tests/test_user_access_policy.py:412`
  (`test_admin_update_tourist_persists_mutation`). Tienen la misma estructura (200, email en la respuesta, `refresh`, email
  en la BD).
- Las aserciones de las dos copias no son iguales. Las de `test_auth.py` son más estrictas en el cuerpo
  (`set(body) == {"detail"}` + `isinstance(..., str)`). Las de `test_user_access_policy.py` solo comprueban
  `"detail" in response.json()` (`:328`, `:404`), pero en el caso de provisión verifican la cédula de la única fila (`:408-409`).

### 3. I001 en `tests/test_user_service.py:3`
- `tests/test_user_service.py:3` — `from datetime import datetime, timedelta, UTC` (ruff:
  `tests\test_user_service.py:3:1: I001 Import block is un-sorted or un-formatted`). Es el único I001 fuera de `app/`.

### 4. `sqlalchemy.future` en tests (S2)
- `tests/test_services.py:14` — `from sqlalchemy.future import select`
- `tests/test_user_access_policy.py:14` — `from sqlalchemy.future import select`. La fuente dice `:13`; la línea se movió.

### 5. Comentario en español en `tests/test_audit.py`
- `tests/test_audit.py:21` — `# 1. Sustituimos el multipart/form-data por un JSON puro que cumple con ServiceCreate`.
  La fila lo sitúa en `:37`. Hoy `:37` está vacía y `:38` dice `# 2. Retrieve Audit History`, en inglés. Es el único
  comentario en español de `tests/`; los textos en español de `test_check_docs.py` son datos de fixtures, no comentarios.

### 6. mypy en `tests/`: `tests/` fuera de `mypy.files`, y hay **11** errores, no 6
- `pyproject.toml:94` — `files = ["app", "scripts/check_docs.py", "scripts/check.py"]` (sin `tests`).
- `./venv/Scripts/python.exe -m mypy tests --cache-dir <scratchpad>` da `Found 16 errors in 9 files (checked 18 source
  files)`. De ellos, 5 están en `app/` (los de A4) y **11 en `tests/`**:
  - `tests/conftest.py:239` — `no-any-return` (`persist_user` devuelve `Any` como `User`). Es de la fila (2+2+2).
  - `tests/test_services.py:157` — `[index]`: `Value of type "object" is not indexable`. Es de la fila.
  - `tests/test_audit.py:72` — `no-any-return`: `create_autospec` devuelto como `AuditRepository`. Es de la fila.
  - `tests/test_fixtures_contract.py:59` — `[call-arg]`: `Unexpected keyword argument "recipient"`. Es de la fila
    (fase F de BE-15).
  - `tests/test_fixtures_contract.py:61` — `[attr-defined]`: `has no attribute "assert_not_called"`. Es de la fila
    (fase F de BE-15).
  - `tests/test_user_service.py:65` y `:71` — `no-any-return` (`create_autospec` devuelto como `UserRepository` y
    `AuditService`). La fila no los cuenta: son el mismo patrón que `test_audit.py:72`.
  - `tests/test_user_service.py:103`, `:197`, `:274`, `:292` — `[arg-type]` `str | None` (`SECRET_KEY`). Según la decisión
    (a) del 6 nov, **son de A4**: se declaran como conjunto de A4 en la excepción al trinquete y BE-32 no los corrige.
- Balance: BE-32 es dueño de **7** errores de mypy en `tests/` y A4 de 4. Si `tests/` entra en `mypy.files`, la
  compuerta pasa de 5 a 16 errores, y al cerrar BE-32 se queda en 9 (5 en `app/` y 4 en `tests/`, todos de A4).

### 7. `Yields:` ausente en los fixtures generadores
- `tests/conftest.py:51-56` — docstring de `db_session` sin `Yields:` (`yield session` en `:58`). Es de la fila.
- `tests/conftest.py:62-74` — docstring de `client` sin `Yields:` (`yield ac` en `:83`). Es de la fila.
- Generadores que la fila no cita: `tests/conftest.py:34` (`setup_database`, yield en `:44`), `tests/conftest.py:89`
  (`override_azure_storage_client`, yield en `:123`) y `tests/test_email.py:43` (`send_message`, yield en `:46`). Ninguno
  tiene `Yields:`. El único fixture generador que sí lo tiene es `mock_send_email` (`tests/conftest.py:137`). Queda fuera
  `override_get_db` (`conftest.py:76`), que es una función anidada y no un fixture público.

### 8. Nota del 5 nov: orden de las guardas de `assert_can_update` sin congelar
- `app/services/user_access_policy.py:65-72`. La fila dice `:64-70`; el bloque se movió. El orden es: jerarquía (`:61`),
  `role` por un no superadmin (`:65`), `role` en una actualización propia (`:70`) e `is_active` por un turista (`:73`).
- `grep -rnE '\["detail"\] *!= *[a-z_]+\.json\(\)' tests/` solo devuelve `tests/test_token_failure_paths.py:98`
  (expirado frente a corrupto), que no tiene relación con esto. Ningún test compara el `detail` de las dos peticiones
  (admin con `role` frente a superadmin con su propio `role`).

### 9. Lista acumulada del 6 nov
- **(a)** Decisión de meter `tests/` en mypy: ver el punto 6. El conteo real es 11 (7 de BE-32 y 4 de A4).
- **(b) BE-33, fase B** (`tests/test_service_repository.py`):
  - `:48-107` — los cinco tests corren con 0 o 1 filas, así que ninguno distingue "la fila de este `id`" de "la única
    fila". El `WHERE` está en `app/repositories/service_repository.py:94`
    (`.where(TouristService.id == service.id)`).
  - `:59` y `:92` — `assert saved.id == package.id`, que es cierto por el mapa de identidad.
  - `:93` — `assert saved.deleted_at is not None`, sin fijar el valor (`:87` fija `datetime(2026, 1, 15, 12, 0,
    tzinfo=UTC)`).
  - `:74` — el docstring dice "A row removed behind the entity's back", pero el `delete()` de `:76` corre en la misma
    sesión.
  - `app/repositories/service_repository.py:86-88` — `Raises:` solo documenta `NoResultFound`: falta `StaleDataError`.
    **Toca `app/`**, aunque es solo un docstring.
- **(b) BE-33, fase C:**
  - `app/services/user_service.py:125-132` — `verify_email_account` lanza `InvalidVerificationTokenError` con dos mensajes.
    Ningún test los distingue: `grep -rnE "str\((expired|corrupt)" tests/` da 0. `tests/test_token_failure_paths.py:152-166`
    solo comprueba `__cause__`.
  - `app/api/dependencies.py:111` (`get_non_deleted_user_by_email`) y `app/repositories/user_repository.py:22`
    (`User.deleted_at.is_(None)`): ningún test presenta un token de un usuario con `deleted_at` puesto e
    `is_active=True`. Los dos `persist_user(..., deleted_at=...)` de la suite (`tests/test_auth.py:306`,
    `tests/test_user_response.py:116`) llevan `is_active=False`.
  - `tests/test_token_failure_paths.py:63-72` y `:110-116` — los docstrings ("the active user it names", "a valid token
    whose subject has no account") se prueban con 1 y con 0 usuarios.
  - `tests/test_token_failure_paths.py:166` — `user_repo.activate_user.assert_not_called()`, redundante en el caso
    `expired` (`_expired_token` está en `:33-35`, sin `scope`).
- **(b) BE-33, fase D** (`tests/test_email.py`):
  - `:77` — `body.count(VERIFICATION_LINK) == 2`: no prueba que la segunda aparición sea texto visible.
  - `:84`, `:87`, `:125` — nada fija el selector `.btn` del CSS, el texto del `<a>` ni el `style` del `<p>`
    (`app/core/email.py:57,90,94`, según la auditoría).
  - `:68` — `assert isinstance(message.subject, str)` es vacua.
  - `:66` — `send_message.assert_awaited_once_with(message)` compara el argumento con el mismo objeto capturado en `:52`.
  - `:52` — `_send_and_capture` lee `send_message.await_args.args[0]`, así que depende de que el mensaje se pase por
    posición.
- **(c)** `tests/conftest.py:192-205` — `make_token` solo acepta `user`
  (`create_access_token(data={"sub": user.email, "role": user.role.value})`): no admite claims extra ni caducidad. Los
  tokens a medida se construyen a mano con `jwt.encode(..., SECRET_KEY, ...)` en `tests/test_user_service.py:268` y
  `:286`, y con `create_access_token` directo en `tests/test_token_failure_paths.py:35,103,112`.
- **(d)** `tests/test_check_docs.py:1039` — `ids=[..., "year-by-monotony", "year-resets-per-table", ...]`, y
  `tests/test_check_docs.py:1089-1090` — `"year-jump-marked"`, `"year-jump-future-row"`. La regla actual infiere el año
  "más cercano" (`scripts/check_docs.py:758-775`, `_date_near`), no por monotonía. AF-02 los citaba en `:834` y
  `:881-885`; se han movido.

## Ficheros afectados (mapa completo)
- `pyproject.toml` — `:94`, `mypy.files` sin `tests` (punto 6).
- `tests/conftest.py` — `:239` (mypy); `:51-56`, `:62-74` (`Yields:` en la fila); `:34`, `:89` (`Yields:` no citado);
  `:192-205` (`make_token`, punto c).
- `tests/test_user_service.py` — `:3` (I001); `:65`, `:71` (mypy, de BE-32); `:103,197,274,292` (mypy, **de A4**);
  `:110,111,328,329` (aserciones sin argumentos); `:268,286` (`jwt.encode` a mano, relacionado con c).
- `tests/test_services.py` — `:14` (`sqlalchemy.future`); `:157` (mypy); `:219`, `:486` (aserciones sin argumentos).
- `tests/test_user_access_policy.py` — `:14` (`sqlalchemy.future`); `:314`, `:384`, `:412` (copias de tests HTTP).
- `tests/test_auth.py` — `:242`, `:262`, `:361` (la otra mitad de cada par duplicado).
- `tests/test_audit.py` — `:21` (comentario en español); `:72` (mypy).
- `tests/test_storage.py` — `:92`, `:159`, `:189`, `:198` (aserciones sin argumentos).
- `tests/test_fixtures_contract.py` — `:59`, `:61` (mypy).
- `tests/test_email.py` — `:43` (`Yields:`); `:52`, `:66`, `:68`, `:77`, `:84`, `:87`, `:99`, `:125` (fase D de BE-33 y
  aserción sin argumentos).
- `tests/test_service_repository.py` — `:48-107`, `:59`, `:74`, `:92`, `:93` (fase B de BE-33).
- `tests/test_token_failure_paths.py` — `:63-72`, `:110-116`, `:166` (fase C de BE-33); aquí iría el test de `deleted_at`.
- `tests/test_check_docs.py` — `:1039`, `:1089-1090` (ids, punto d).
- `app/repositories/service_repository.py` — `:86-88`, `Raises:` sin `StaleDataError`. Es el **único cambio en `app/`**, y
  es solo un docstring.
- Referencia sin cambio previsto: `app/services/user_access_policy.py:65-72` (las guardas que se quieren congelar),
  `app/services/user_service.py:125-132`, `app/api/dependencies.py:111` y `app/core/email.py:57,90,94` (código bajo test).

## Rincones no mencionados por la fuente
1. Una aserción sin argumentos más (11 en total): `tests/test_email.py:99`, introducida por la fase D de BE-33.
2. Un tercer par de tests HTTP duplicados: `tests/test_auth.py:242` y `tests/test_user_access_policy.py:412`.
3. Dos errores de mypy de BE-32 que la fila no cuenta: `tests/test_user_service.py:65,71` (`no-any-return` de
   `create_autospec`, el mismo patrón que `test_audit.py:72`).
4. Tres fixtures generadores sin `Yields:` además de `client` y `db_session`: `tests/conftest.py:34` (`setup_database`),
   `tests/conftest.py:89` (`override_azure_storage_client`) y `tests/test_email.py:43` (`send_message`).
5. Pares redundantes `assert_not_called()` + `assert_not_awaited()` sobre el mismo `AsyncMock`, del mismo tipo que el
   opcional 6 de la fase C: `tests/test_user_service.py:121-122` y `tests/test_audit.py:86-87`.
6. Líneas que se han movido respecto a la fila: comentario en español `:37` → `:21`; `test_services.py` `:245,520` →
   `:219,486`; `test_user_access_policy.py:13` → `:14`; guardas `:64-70` → `:65-72`; ids de `test_check_docs.py`
   `:834,881-885` → `:1039,1089-1090`.
7. **Fuera de BE-32, con otro dueño.** No son omisiones; se anotan para que el plan no los absorba:
   - `sqlalchemy.future` en `app/repositories/audit_repository.py:2`, `service_repository.py:2` y
     `user_repository.py:3` pertenece a S2 (`B-FUTURO`, `docs/backlog.md:107`).
   - Que ningún test rechace un token firmado con otra clave (`docs/deuda/BE-33/gaps.md:143`) es una **precondición de
     A4** por decisión de David (12:14 del 6 nov), no de BE-32.
8. **Hace falta una decisión.** `docs/deuda/BE-33/gaps.md:141` sugiere llevar a BE-32 el test candidato contra D2
  (exigir que el `detail` de un token corrupto sea igual al de un usuario desconocido, en `get_current_user`). La fila
  BE-32 no lo recoge, y la bitácora del 6 nov solo registra E3 para ese opcional. David decide si entra.

## Patrones de detección (copiables)
```bash
# 1. Aserciones de mock sin argumentos (hoy 11; la meta la fija el plan)
grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ --include=*.py
# 1b. not_called y not_awaited redundantes sobre el mismo mock (rincón 5)
grep -rnE -A1 "\.assert_not_called\(\)" tests/ --include=*.py | grep -E "assert_not_awaited"
# 2. Copias HTTP (3 pares): nombres de los tests
grep -nE "def test_(admin_patching_superadmin|admin_provisioning_admin|admin_updates_tourist_email)" tests/test_auth.py
grep -nE "def test_(patch_hierarchy_violation|admin_cannot_provision_admin_account|admin_update_tourist_persists)" tests/test_user_access_policy.py
# 3. I001 en tests (hoy 1)
./venv/Scripts/ruff.exe check --output-format=concise tests/
# 4. sqlalchemy.future en tests (hoy 2)
grep -rn "sqlalchemy.future" tests/ --include=*.py
# 5. Comentario en español en tests (hoy 1)
grep -rnE "^\s*#.*\b(Sustituimos|Creamos|Verificamos|Comprobamos|Probamos|Usamos|Simulamos|Validamos)\b" tests/ --include=*.py
# 6. mypy en tests (hoy 11 en tests/; 4 de ellos son de A4: test_user_service.py:103,197,274,292)
grep -n "^files = " pyproject.toml
./venv/Scripts/python.exe -m mypy tests --cache-dir "$TMPDIR/mypycache" 2>&1 | grep -E "^tests" | grep -c "error:"
# 7. Fixtures generadores sin Yields: (hoy 6: conftest 34, 51, 62, 89 y test_email 43; más override_get_db anidado)
./venv/Scripts/python.exe -I -c "import ast,pathlib;[print(f'{p}:{n.lineno} {n.name}') for p in sorted(pathlib.Path('tests').glob('*.py')) for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(isinstance(x,ast.Yield) for x in ast.walk(n)) and 'Yields:' not in (ast.get_docstring(n) or '')]"
# 8. Orden de las guardas: ¿hay algún test que compare dos detail? (hoy solo test_token_failure_paths.py:98)
grep -rnE '\["detail"\] *!= *[a-z_]+\.json\(\)' tests/ --include=*.py
# 9b-B. Raises sin StaleDataError (hoy 0)
grep -n "StaleDataError" app/repositories/service_repository.py
# 9b-C. Mensajes de verify_email_account sin distinguir (hoy 0)
grep -rnE "str\((expired|corrupt)" tests/ --include=*.py
# 9b-C. Usuario con deleted_at y activo presentado con token (hoy 0 con is_active=True)
grep -rnE "persist_user\([^)]*deleted_at" tests/ --include=*.py
# 9c. make_token sin claims ni caducidad
grep -n -A12 "def make_token" tests/conftest.py
grep -rn "jwt.encode" tests/ --include=*.py
# 9d. Ids de la regla vieja del año (hoy 3 líneas)
grep -nE "year-by-monotony|year-resets-per-table|year-jump" tests/test_check_docs.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `fd144ad` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `fd144adbfe5a888a1196dce6c8c6dc721dbc6efe`; rama `item/be-32` limpia).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (desde `C:\projects\ecotur-asoprado`; Python 3.14.3).
- **La compuerta ya estaba en rojo antes de tocar nada.** El rojo es el heredado: A4 y el I001 de BE-32.

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

- `ruff format --check`: `57 files already formatted`.
- `ruff check`: `Found 9 errors.` Son 8 I001 en `app/` (`api/dependencies.py`, `api/routers/audit.py`, `core/email.py`,
  `db/database.py`, `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`,
  `services/user_service.py`, todos `:1:1`, de A4) y 1 en `tests\test_user_service.py:3:1` (BE-32).
- `mypy`: `Found 5 errors in 4 files (checked 35 source files)`. Todos son `str | None` de A4: `app\db\database.py:11`,
  `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`. `tests/` no se mide.
- `import-linter`: `Contracts: 4 kept, 0 broken.` (Capas KEPT · Los servicios no conocen el transporte HTTP KEPT · Los
  repositorios solo conocen SQLAlchemy y los modelos KEPT · Los modelos y los schemas no dependen de capas superiores KEPT).
- `docs (coherencia)`: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- pytest: `547 passed, 5 warnings in 22.30s` (0 failed). Los 5 avisos son `StarletteDeprecationWarning`
  `HTTP_422_UNPROCESSABLE_ENTITY`.
- Cobertura: `TOTAL 943 23 138 19 96.11%`, `Required test coverage of 92.0% reached. Total coverage: 96.11%`.
- Medición adicional, fuera de la compuerta: `mypy tests` da `Found 16 errors in 9 files (checked 18 source files)`, que
  son 5 en `app/` (A4) y 11 en `tests/` (7 de BE-32 y 4 de A4).

## Conclusión para el planificador
- Hay que resolver el ítem en todos sus subpuntos (la decisión del 6 nov fue "BE-32 completo"). Son unos 30 hallazgos
  repartidos por 14 archivos de `tests/`, más `pyproject.toml` y un docstring de `app/repositories/service_repository.py`.
  Con el límite de ≤ 5 archivos y 1 dominio por fase, salen al menos 4 fases. Una agrupación natural:
  (i) mypy, metiendo `tests/` en `mypy.files`, con los 7 errores y `Yields:`;
  (ii) higiene: I001, `sqlalchemy.future`, comentario e ids;
  (iii) aserciones de mock y copias HTTP;
  (iv) opcionales de BE-33 por archivo (`test_service_repository.py`, `test_token_failure_paths.py`, `test_email.py`),
  más `make_token` y la guarda de `assert_can_update`.
- No debe tocar: los 8 I001 ni los 5 `str | None` de `app/`; los 4 `str | None` de `tests/test_user_service.py:103,197,274,292`,
  que se declaran conjunto de A4 en la excepción al trinquete de ADR-0005; el `sqlalchemy.future` de `app/` (S2); los tests
  de firma con otra clave (precondición de A4); ningún cambio de comportamiento en `app/` aparte del docstring `Raises`.
- Riesgo 1: con `tests/` en `mypy.files`, la compuerta pasa de 5 a 16 errores en cuanto entra el cambio. Al cerrar BE-32
  debe quedar en 9 exactos (5 + 4, todos de A4); la fase que lo active tiene que dejar los 7 de BE-32 en 0 en el mismo commit.
- Riesgo 2: consolidar las 3 copias HTTP baja el número de tests (547). Hay que justificarlo y comprobar que la cobertura
  (96.11 %) no baja y que en la copia que se queda se conservan las aserciones más estrictas de cada par (`set(body) ==
  {"detail"}` de `test_auth.py`; cédula de la única fila de `test_user_access_policy.py:408-409`).
- Riesgo 3: algunos opcionales piden matar mutantes concretos (D2, U6/U7, M5, M10, L2-L5, L14/L15/L17, C10, D8). El plan
  debe fijar qué mutante mata cada test y no afirmar sobre texto en español (AGENTS §5): para distinguir mensajes, se
  comparan con `!=` / `==`. El candidato D2 (rincón 8) necesita una decisión de David antes de planear.

## Adenda — decisiones de David antes de planear (7 nov 2026, 10:24, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir.

1. **Veredicto aceptado: confirmada. Alcance: BE-32 completo**, como se decidió el 6 nov (09:15 y 09:41): los nueve
   puntos de la fila, la nota del 5 nov y la lista acumulada (a)–(d), más los rincones 1–5 y 8 de esta verificación.
   Nada de lo que tiene otro dueño (rincón 7) entra.
2. **Rincón 8, entra:** un test nuevo en `tests/test_token_failure_paths.py`, junto al de `:93-98`, que compara la
   respuesta de un token corrupto con la de un token válido de un correo sin cuenta
   (`create_access_token(data={"sub": "ghost@test.com"})`, como `:111`) y afirma `corrupt.json()["detail"] ==
   unknown.json()["detail"]`. Mata el mutante D2 de `docs/deuda/BE-33/gaps.md:141` (intercambio de las ramas `except`
   de `app/api/dependencies.py:101` y `:107`); el de `:93-98` se conserva. No afirma sobre texto: compara dos respuestas.
3. **Rincones 1–5, entran todos**, como ediciones a tests existentes: `tests/test_email.py:99` pasa a
   `assert_awaited_once_with(...)`; `tests/test_user_service.py:65,71` anotan el retorno de `create_autospec`;
   `Yields:` en `tests/conftest.py:34`, `:89` y `tests/test_email.py:43`; una línea borrada en cada par redundante
   (`tests/test_user_service.py:121-122`, `tests/test_audit.py:86-87`: un `AsyncMock` no llamado tampoco fue esperado).
   El tercer par duplicado es el punto 4.
4. **Copias HTTP: se borran las tres de `tests/test_user_access_policy.py` (`:314`, `:384`, `:412`) y se quedan las de
   `tests/test_auth.py` (`:262`, `:361`, `:242`)**, que son las más estrictas en el cuerpo (`set(body) == {"detail"}`).
   Antes de borrar `test_user_access_policy.py:384`, su aserción de `:406-409` (`len(users) == 1` y
   `users[0].cedula == admin.cedula`) se copia a `tests/test_auth.py:361`. La suite pasa de 547 a 544 tests; el plan lo
   declara y el ejecutor mide la cobertura antes y después (no puede bajar: las líneas de `app/` ejercitadas son las
   mismas).
5. **Excepción al trinquete de ADR-0005, conjunto exacto de A4.** `tests/` entra en `mypy.files` (`pyproject.toml:94`,
   opción b del 6 nov) y la fase que lo haga deja los 7 errores de BE-32 (`tests/conftest.py:239`,
   `tests/test_services.py:157`, `tests/test_audit.py:72`, `tests/test_fixtures_contract.py:59,61`,
   `tests/test_user_service.py:65,71`) en 0 **en el mismo commit**. Lo que queda en rojo al cerrar BE-32 es de A4 y es
   exactamente: mypy 9 = {`app/db/database.py:11`, `app/core/security.py:71`, `:87`, `app/services/user_service.py:124`,
   `app/api/dependencies.py:95`, `tests/test_user_service.py:103`, `:197`, `:274`, `:292`}; ruff 8 = los 8 I001 de `app/`
   (`api/dependencies.py`, `api/routers/audit.py`, `core/email.py`, `db/database.py`, `repositories/user_repository.py`,
   `schemas/audit.py`, `services/audit_service.py`, `services/user_service.py`, todos `:1:1`). El auditor compara contra
   este conjunto, no contra los totales 9 y 5 de la línea base. **Compuerta esperada al cerrar: ruff 8 · mypy 9 · 4 kept
   · 544 tests · cobertura ≥ 96,11 %.** Ni una línea más en rojo.
6. **Mutantes:** por cada opcional de la lista (b) que pida matar un mutante (D2, U6/U7, D17, L2–L5, L14/L15/L17, C10,
   D8 de `docs/deuda/BE-33/gaps.md`), el plan nombra el mutante y el test que lo mata, con el `failed/passed` esperado;
   mensajes distintos se fijan con `!=`/`==` entre respuestas, nunca leyendo el texto (AGENTS §5).
7. **`app/` no cambia de comportamiento:** el único cambio permitido en `app/` es el docstring `Raises:` de
   `app/repositories/service_repository.py:86-88` (`StaleDataError`). Si el plan cree necesitar otro, se detiene y lo
   dice.
8. **Fuera de BE-32, con dueño (rincón 7), sin discusión:** `sqlalchemy.future` de `app/repositories/*` (S2); tests de
   firma con otra clave (precondición de A4). **Para el cierre, no para el plan:** la laguna que señala el verificador
   (un opcional "→ BE-32" en `gaps.md` que nadie llevó a la fila: el D2) se anota en la fila AF-08 del backlog.

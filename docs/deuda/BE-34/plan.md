# PLAN — BE-34: Crear el primer superadmin con un comando manual e idempotente

> Fuente: `docs/deuda/BE-34/verificacion.md` (confirmada; adenda de ocho decisiones de David, 13 nov, 16:28).
> Base: `4f10660` (HEAD de `item/be-34` = `5db7641`: `git diff --name-only 4f10660 5db7641 -- app tests alembic conftest.py
> pyproject.toml .env.example` vacío). Estado: **aprobado por David, completo: fases A → E con E0 (13 nov 2026, 17:26) y E2 (14 nov 2026, 09:08); fases F y G (BE-51), reescritas por E2, con E3 (14 nov 2026, 10:54). Siete fases, A → G. Detalle en "Enmiendas aprobadas", al final.** Las cifras de este plan (tests,
> cobertura, mutantes, `numstat` y conteos de grep) se midieron el 13 nov sobre copias desechables de `4f10660` en el
> scratchpad, con el texto exacto que dicta el plan.

## Resumen para aprobación

En cinco fases, un operador podrá crear el primer superadmin con `python -m app.cli.bootstrap_superadmin`. (A) Salda
BE-47: un test exige que `TEST_ENVIRONMENT` tenga una clave por cada campo de `Settings`. (B) Escribe ADR-0015 con las
decisiones de la adenda. (C) Añade `SuperadminBootstrapSettings`, clase hermana de `Settings` con las cinco credenciales
(contraseña `SecretStr`), y su bloque en `.env.example`. La contraseña de ejemplo no pasa la validación. (D) Añade
`UserRepository.count_active_superadmins` y el núcleo `bootstrap_superadmin`. El núcleo no escribe nada si existe un
superadmin activo y no borrado. Si la cédula o el correo ya están en cualquier fila, falla sin promover a nadie. Si no,
crea un superadmin activo y lo audita como autor de su propia alta. (E) Añade el comando: valida con
`UserCreateByAdmin`, abre su propio motor sin `echo`, no imprime nunca la contraseña y sale con 0 o 1. `app.cli` entra
en el contrato de capas. La suite pasa de 638 a 675 tests y la cobertura de 96,82 % a 97,37 %.
**Riesgo principal:** filtrar la contraseña, por el texto de un `ValidationError` (medido: lo incluye) o por el `echo`
del motor (el hash). Los tests de C y E lo impiden, y cuatro mutantes lo demuestran. **No se toca:** `Settings` (sigue
con 15 campos), guards, routers, rutas, la política (BE-35..BE-38), `create_user` (A3), `app/db/database.py` (A5),
`alembic/`, `Dockerfile`, `docker-compose.yml` ni `cd-pipeline.yml`.

**Fases F y G (BE-51; reescritas por E2, no se ejecutan sin E3):** un correo es una sola cuenta y se guarda en una sola
forma, en minúsculas. (F) Escribe ADR-0016. (G) Los tres schemas que reciben un correo usan el tipo `LowercaseEmail`, que
lo pasa a minúsculas, y una restricción `CHECK (email = lower(email))` (modelo y migración `b51f3c9e2a64`) hace que la
base rechace cualquier otra grafía. La unicidad la sigue dando `ix_users_email`. Las consultas no cambian y ningún dato se
reescribe, porque ningún correo guardado tiene mayúsculas (Q1 = 0). La suite pasa a 691 tests y la cobertura a 97,63 %.
**Riesgo:** una fila con mayúsculas detiene la migración y el despliegue; por eso G espera Q1 = 0 en `develop`. La guía
de OWASP recomienda guardar también el correo tal como se escribió; el plan guarda solo la forma en minúsculas y lo
declara (decisión 2 de E3).

## Objetivo y decisiones bloqueadas

Objetivo: una base sin superadmin activo (instalación nueva o pérdida del último) se recupera sin SQL directo. Hace falta
un comando que el operador corre una vez por entorno, idempotente, que nunca convierte una cuenta existente en
superadmin.

1. **Lógica en `app/`** (adenda, punto 1). El núcleo es `app/services/superadmin_bootstrap.py::bootstrap_superadmin`. El
   punto de entrada es `app/cli/bootstrap_superadmin.py`, en el paquete nuevo `app.cli`. Nada en `scripts/`.
2. **Comando manual** `python -m app.cli.bootstrap_superadmin` (punto 2). No es ruta HTTP, no corre en `lifespan` ni es
   paso del CD. El uso está en el docstring del módulo.
3. **`SuperadminBootstrapSettings(DatabaseSettings)`** en `app/core/config.py` (punto 3). Cinco campos obligatorios sin
   valor por defecto: `superadmin_cedula`, `superadmin_email`, `superadmin_first_name`, `superadmin_last_name` y
   `superadmin_password: SecretStr`. Variables: `SUPERADMIN_*`. `Settings` no gana campos.
4. **"Ya existe" = superadmin con `is_active` y `deleted_at IS NULL`** (punto 4). Si existe: no se escribe nada y el
   comando sale con 0. Si la cédula o el correo están en cualquier fila: `AlreadyExistsError`, no se escribe nada y sale
   con 1. Si todos están inactivos o borrados: se crea uno.
5. **Auditoría** (punto 5): `CREATE`, `entity_id` y `performed_by` = cédula nueva,
   `changes={"role": "superadmin", "source": "bootstrap"}` (`source` es la marca propuesta). Primero el alta, después la
   auditoría, como en `register_tourist`.
6. **Validación con `UserCreateByAdmin`** (punto 6). El núcleo fija `role=superadmin`, `is_active=True` y
   `data_consent=True` sin mirar el DTO. Los errores se imprimen como `VARIABLE: tipo`, con
   `errors(include_input=False)`.
7. **ADR-0015** (punto 7), fase B, antes del código que lo cita.
8. **BE-47 es la fase A** (punto 8). La clase nueva no entra en `TEST_ENVIRONMENT` (ver Análisis).
9. **Compuerta** `./venv/Scripts/python.exe scripts/check.py` en verde al cerrar cada fase. La cobertura nunca baja de
   96,82 %.

## Análisis del redactor

**Qué cambia y por qué.** Las dos vías para tener un superadmin exigen ya uno: el guard de `dependencies.py:186` y la
política de `user_access_policy.py:67`. La adenda fija el diseño. Este plan elige nombres y capas, y mide los riesgos
de fuga antes de dictar código.

**Medido con sonda, y lo que cambia en el plan.**
- `str(ValidationError)` de `UserCreateByAdmin` con `password="DIGITAR_CONTRASEÑA_PRIVADA"` contiene la contraseña (`True`).
  `errors(include_input=False, include_url=False)` da `[(('password',), 'value_error')]` sin ella. Por eso el comando
  imprime solo `loc` y `type`.
- `SecretStr` sale como `'**********'` en `repr` y en `model_dump()`. ADR-0013 aplazó `SecretStr` porque obligaba a tocar
  a cada consumidor de `Settings`. Aquí hay un solo consumidor y una sola llamada a `get_secret_value()`.
- `from conftest import TEST_ENVIRONMENT` en un test resuelve a `tests/conftest.py` (`ImportError`; mypy, `attr-defined`).
  El test de BE-47 lee el `conftest.py` de la raíz con `runpy.run_path`. Al ejecutarlo repite
  `os.environ.update(TEST_ENVIRONMENT)` con los mismos valores, y eso es inocuo.
- Mutante de `echo=True` en el motor del comando: con `capsys` sobrevive, porque el manejador de SQLAlchemy ya existe
  desde `app/db/database.py` y escribe en el stdout original. Con `caplog` muere, y el test de E afirma sobre
  `caplog.text`.
- Con `"app.api | app.cli"`, un `import app.cli` dentro de `app/services/` da `3 kept, 1 broken` (exit 1). Sin esa línea
  da `4 kept`. Lo mismo ocurre con un `import app.api` dentro de `app/cli/`.

**Orden y dependencias: A → B → C → D → E.** A no depende de nada (1 archivo, 9 líneas). B documenta las decisiones que
C, D y E citan como `ADR-0015`. E importa la clase de C y el núcleo de D. D no depende de C: el núcleo recibe un
`UserCreateByAdmin`, no la configuración.

**¿Necesita la clase nueva una vigilancia como la de BE-47? No en `TEST_ENVIRONMENT`.** BE-47 protege `Settings`, que la
app construye implícitamente al importar (`get_settings()` con caché). `SuperadminBootstrapSettings` solo la construyen
el comando y sus tests: los de C con `_env_file=None`, y los de E con las seis variables puestas en el entorno del
proceso, que gana al `.env` (ADR-0013, punto 3). La vigilancia equivalente sí entra en C: cada campo está en
`.env.example`, cada campo es obligatorio (6 casos `missing`) y el conjunto de campos es exacto.
`REQUIRED`/`OPTIONAL_DEFAULTS` no cambian: la igualdad de `tests/test_config.py:105` hace que añadir un campo a
`Settings` ponga la suite en rojo. Eso congela el punto 3 de la adenda.

**Tests que congelan comportamiento relacionado (no cambian).** `tests/test_config.py:105` (los 15 campos de `Settings`)
y `:219` (`.env.example`). `tests/test_route_guards.py` (no hay ruta nueva). Los tests de `create_administrative_account`
y `register_tourist` en `tests/test_user_service.py`. `tests/test_models_registry.py` (no hay modelo nuevo).

**Riesgos y su cobertura.**
1. Contraseña débil o la de ejemplo: la valida `UserCreateByAdmin` y la prueban el test de `.env.example` (C) y el caso
   `weak-password` (E).
2. Fuga de la contraseña o del hash: `SecretStr` (MC1), solo `loc`/`type` (ME1) y motor sin `echo` (ME4). Los tests
   afirman sobre stdout, stderr y `caplog`.
3. Escalada: 6 casos de choque (cédula o correo × turista activo, admin inactivo, superadmin borrado) y el mutante MD5
   los tumba todos.
4. Idempotencia: hay tests de segunda corrida en D y en E.
5. Carrera entre dos ejecuciones simultáneas: el índice único rechaza la segunda con `IntegrityError`. Se acepta en
   ADR-0015 porque es un comando manual.
6. A3: `create_user` y `create_audit_log` hacen `commit()` por separado. Se acepta, como en las demás altas.

**Qué NO se toca.** `Settings`, `get_settings`, `get_database_settings`. `app/api/` y `app/main.py`.
`user_service.py` y `user_access_policy.py`. `app/models/` y `app/schemas/`. `app/db/database.py` (el `echo` es de A5).
`alembic/`, `Dockerfile`, `docker-compose.yml`, `.azure-pipelines/`, `scripts/`. Los dos `conftest.py`. `AGENTS.md` y los
documentos vivos (los cierra la sesión Mentor).

## Regla de alcance

- **Sí:** 12 archivos con el texto exacto de cada fase. En `app/`: `cli/__init__.py`, `cli/bootstrap_superadmin.py`,
  `core/config.py`, `repositories/user_repository.py` y `services/superadmin_bootstrap.py`. En la raíz: `pyproject.toml`
  y `.env.example`. En `docs/`: `adr/0015-bootstrap-del-primer-superadmin.md`. En `tests/`: `test_config.py`,
  `test_user_repository.py`, `test_superadmin_bootstrap.py` y `test_bootstrap_superadmin_command.py`.
- **Fases F y G (E1, E2):** 6 archivos más, 18 en total. F: `docs/adr/0016-correo-en-minusculas.md`. G:
  `app/schemas/user.py`, `app/models/user.py`, `alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py`,
  `tests/test_user_response.py` y `tests/test_email_case.py`. G no vuelve sobre ningún archivo de A–E. La exclusión de
  `app/schemas/`, `app/models/` y `alembic/` deja de valer solo para G.
- **No:** cualquier otro archivo, docstring o comentario. Un hallazgo nuevo va a Residuales, nunca "de paso".

## Fases

**Procedimiento de mutantes (común, el de BE-42).**
1. Crear en el scratchpad un directorio nuevo y vacío. No se reutiliza ni se borra.
2. Ejecutar `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>` después del commit de la fase.
3. Aplicar la edición exacta de la tabla.
4. Desde `<dir>`, ejecutar `C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
5. Pegar en el handoff la última línea y los `FAILED`.

| Mutante | Archivo | Edición exacta (original → sustituto) | Resultado medido |
|---|---|---|---|
| MA | `conftest.py` | borrar la línea `    "CORS_ORIGINS": "http://localhost:3000",` | `1 failed, 349 passed` |
| MC1 | `app/core/config.py` | `    superadmin_password: SecretStr` → `    superadmin_password: str` | `3 failed, 358 passed` |
| MC2 | `app/core/config.py` | `class SuperadminBootstrapSettings(DatabaseSettings):` → `class SuperadminBootstrapSettings(Settings):` | `1 failed, 360 passed` |
| MC3 | `.env.example` | `SUPERADMIN_PASSWORD=DIGITAR_CONTRASEÑA_PRIVADA` → `SUPERADMIN_PASSWORD=Superadmin2026` | `1 failed, 360 passed` |
| MD1 | `app/repositories/user_repository.py` | borrar `                User.is_active.is_(True),` | `2 failed, 376 passed` |
| MD2 | ídem | borrar `                User.deleted_at.is_(None),` | `1 failed, 377 passed` |
| MD3 | ídem | borrar `                User.role == UserRole.superadmin,` | `3 failed, 375 passed` |
| MD4 | `app/services/superadmin_bootstrap.py` | `count_active_superadmins() > 0:` → `count_active_superadmins() > 1:` | `2 failed, 376 passed` |
| MD5 | ídem | `    if existing_user:` → `    if False:` | `6 failed, 372 passed` |
| MD6 | ídem | `        role=UserRole.superadmin,` → `        role=credentials.role,` | `1 failed, 377 passed` |
| MD7 | ídem | `        is_active=True,` → `        is_active=credentials.is_active,` | `1 failed, 377 passed` |
| ME1 | `app/cli/bootstrap_superadmin.py` | borrar las dos líneas `        if field not in SuperadminBootstrapSettings.model_fields:` / `            field = f"superadmin_{field}"` | `2 failed, 384 passed` |
| ME2 | ídem | el `return 1` tras el `print` de `AlreadyExistsError` → `return 0` | `1 failed, 385 passed` |
| ME3 | ídem | `{created.email}")` → `{created.email} {credentials.password}")` | `3 failed, 383 passed` |
| ME4 | ídem | `    engine = create_async_engine(database_url)` → `    engine = create_async_engine(database_url, echo=True)` | `1 failed, 385 passed` |
| ME5 | ídem | `    sys.exit(main())` → `    main()` | `1 failed, 385 passed` |
| ME6 | `app/services/superadmin_bootstrap.py` | añadir `import app.core.email  # noqa: F401` antes de `from app.core.exceptions import AlreadyExistsError` | `1 failed, 385 passed` (solo `test_command_runs_without_the_web_app_secrets`) |
| MK1 | `app/services/superadmin_bootstrap.py` | añadir `import app.cli  # noqa: F401` antes del primer `from app.` | import-linter `3 kept, 1 broken` (exit 1) |
| MG1 | `app/schemas/user.py` | `AfterValidator(str.lower)]` → `AfterValidator(str.strip)]` | `11 failed, 391 passed` |
| MG2 | ídem | en `UserBase`, `    email: LowercaseEmail = Field(` → `    email: EmailStr = Field(` | `5 failed, 397 passed` |
| MG3 | ídem | en `UserLogin`, `    email: LowercaseEmail` → `    email: EmailStr` | `3 failed, 399 passed` |
| MG4 | ídem | en `UserUpdate`, `    email: LowercaseEmail \| None = Field(` → `    email: EmailStr \| None = Field(` | `3 failed, 399 passed` |
| MG5 | `app/models/user.py` | borrar la línea `    __table_args__ = (CheckConstraint("email = lower(email)", name="ck_users_email_lowercase"),)` | `1 failed, 399 passed, 2 errors` (los errores: el `downgrade()` del fixture de la migración no encuentra la restricción) |
| MG6 | `alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py` | `'email = lower(email)')` → `'email = email')` | `1 failed, 401 passed` |
| MG7 | ídem | `        batch_op.drop_constraint('ck_users_email_lowercase', type_='check')` → `        pass` | `2 failed, 400 passed` |
| MG8 | `app/repositories/user_repository.py` | en `activate_user`, `select(User).where(User.email == email)` → `select(User).where(func.lower(User.email) == func.lower(email))` | `1 failed, 401 passed` (solo `test_verification_token_in_another_case_is_rejected`) |

Al cerrar cada fase, la compuerta debe dar exit 0, `Compuerta superada.`, `All checks passed!`,
`Contracts: 4 kept, 0 broken.` y `8 warnings`, y además:

| Fin de | pytest | Cobertura (`TOTAL` stmts) | ruff format | mypy | Suite de la copia (sin `test_check*`) |
|---|---|---|---|---|---|
| Base | 638 passed | 96,82 % (965) | 61 files | 56 source files | 349 passed |
| A | 639 passed | 96,82 % (965) | 61 files | 56 source files | 350 passed |
| B | 639 passed | 96,82 % (965) | 61 files | 56 source files | 350 passed |
| C | 650 passed | 97,01 % (966) | 61 files | 56 source files | 361 passed |
| D | 667 passed | 97,07 % (988) | 64 files | 59 source files | 378 passed |
| E | 675 passed | 97,37 % (1031) | 67 files | 62 source files | 386 passed |
| F | 675 passed | 97,37 % (1031) | 67 files | 62 source files | 386 passed |
| G | 691 passed | 97,63 % (1034) | 68 files | 63 source files | 402 passed |

Todo archivo nuevo o editado se guarda en UTF-8 con fin de línea LF.

### Fase A — BE-47: `TEST_ENVIRONMENT` cubre todo `Settings` (la más pequeña)

- **Archivos (1):** `tests/test_config.py`. Dominio: configuración (tests).
- **Cambios exactos:**
  1. `import runpy` como primera línea del bloque de imports de la biblioteca estándar, antes de
     `from collections.abc import Callable`.
  2. Tras la línea `ENV_EXAMPLE = …`, sin línea en blanco entre ambas:
     `ROOT_CONFTEST = Path(__file__).resolve().parents[1] / "conftest.py"`.
  3. Al final del archivo, con dos líneas en blanco antes:
     ```python
     def test_test_environment_fixes_every_setting() -> None:
         """Edge case: the root conftest.py gives every Settings field a test value (ADR-0013, 6)."""
         test_environment = runpy.run_path(str(ROOT_CONFTEST))["TEST_ENVIRONMENT"]

         assert {n.upper() for n in Settings.model_fields} <= set(test_environment)
     ```
- **Tests (RED primero):** en la base el test pasa, porque las 15 claves están (verificación, l.55). El RED se demuestra
  con el mutante MA antes del commit: se borra la clave `CORS_ORIGINS` de `conftest.py` y se ejecuta
  `./venv/Scripts/python.exe -m pytest tests/test_config.py -q -p no:cacheprovider -rf`. Medido: `1 failed`
  (`test_test_environment_fixes_every_setting`). Después se restaura `conftest.py` y no se commitea. Sin el test nuevo,
  ese mismo mutante deja la suite de la copia en verde (`349 passed`): es el hueco de BE-47.
- **Criterio de aceptación:** compuerta como la fila A. MA con el resultado de la tabla. `git show --numstat --format=
  <sha A>` da `9	0	tests/test_config.py`. `git grep -n 'TEST_ENVIRONMENT' -- tests | wc -l` → `1`.
- **Fuera de alcance:** `conftest.py` (no cambia), la clase nueva (fase C), `REQUIRED`/`OPTIONAL_DEFAULTS`.
- **Commit:**
  ```
  test(config): require a test value for every Settings field (BE-47)

  The root conftest.py fixes every setting before the app is imported
  (ADR-0013, point 6), but nothing checked that it keeps doing so. An
  optional field added to Settings without a key in TEST_ENVIRONMENT
  left the suite green and, in it, took the value of the .env file of
  whoever ran it: removing CORS_ORIGINS from TEST_ENVIRONMENT kept all
  349 tests of an exported copy green.

  The new test reads TEST_ENVIRONMENT from the root conftest.py with
  runpy.run_path: "from conftest import" resolves to tests/conftest.py.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — ADR-0015

- **Archivos (1):** `docs/adr/0015-bootstrap-del-primer-superadmin.md` (nuevo). Dominio: decisiones (docs).
- **Cambios exactos:** crear el archivo con este texto. `<FECHA>` es la fecha de aprobación que la sesión Mentor anote en
  la línea "Estado" de este plan; si no figura, la fase se detiene.
  ```markdown
  # ADR-0015 — Primer superadmin: comando manual `python -m app.cli.bootstrap_superadmin`, credenciales fuera de `Settings`

  - **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-34)
  - **Propuesta:** Claude, `plan-redactor` (13 nov 2026), sobre la adenda de David a la verificación (13 nov, 16:28)
  - **Ubicación en el repo:** `docs/adr/0015-bootstrap-del-primer-superadmin.md`
  - **Origen:** backlog BE-34; `docs/deuda/BE-34/verificacion.md` (veredicto y adenda de ocho puntos);
    `docs/deuda/BE-34/plan.md`. Relación: ADR-0013 (añade una clase hermana de `Settings`), ADR-0012 (el comando no pasa
    por guards ni política), ADR-0003 (reutiliza `AlreadyExistsError`).

  ## Contexto

  Las dos vías de producto para tener un superadmin exigen ya uno: `POST /usuarios/admin` (guard
  `get_current_superadmin_user`) y el cambio de rol por `PATCH` (`UserAccessPolicy`). Ni `app/`, ni `alembic/`, ni `scripts/`
  crean uno. Tras `alembic upgrade head`, lo único que corre el CD, la tabla `users` está vacía, y si se pierde el último
  superadmin solo se recupera con SQL directo. La aplicación no tiene cambio de contraseña: la contraseña con que nazca el
  superadmin es la definitiva. El CD solo pasa `DATABASE_URL` al contenedor de migraciones, y el motor de la app escribe
  cada sentencia con sus parámetros (`echo=True`, backlog A5).

  ## Decisión

  1. **Lógica en `app/`, en dos piezas.** El núcleo, `bootstrap_superadmin` (`app/services/superadmin_bootstrap.py`),
     recibe credenciales ya validadas y los repositorios. El punto de entrada, `app/cli/bootstrap_superadmin.py` (paquete
     nuevo `app.cli`), lee la configuración, valida, abre su motor y traduce el resultado a código de salida. Nada en
     `scripts/`. `app.cli` entra en el contrato de capas como hermano independiente de `app.api` (`"app.api | app.cli"`).
  2. **Invocación manual, una vez por entorno**, con la imagen que despliega el CD:
     `docker run --rm -e DATABASE_URL=… -e SUPERADMIN_CEDULA=… -e SUPERADMIN_EMAIL=… -e SUPERADMIN_FIRST_NAME=…
     -e SUPERADMIN_LAST_NAME=… -e SUPERADMIN_PASSWORD=… <imagen> python -m app.cli.bootstrap_superadmin`. No es ruta HTTP,
     no corre en `lifespan` ni al arrancar y no es paso del CD.
  3. **Credenciales en `SuperadminBootstrapSettings(DatabaseSettings)`** (`app/core/config.py`), hermana de `Settings` y
     construida solo por el comando. Tiene cinco campos obligatorios; la contraseña es `SecretStr`. `Settings` sigue con 15
     campos. `.env.example` las documenta con una contraseña de ejemplo que no pasa la validación.
  4. **"Ya existe" = al menos un superadmin activo y no borrado** (`UserRepository.count_active_superadmins`). Si existe, no
     se escribe nada y el comando sale con 0. Si la cédula o el correo están en cualquier fila (cualquier rol o estado):
     `AlreadyExistsError`, no se escribe nada y sale con 1. El comando no promueve, no reactiva ni recupera cuentas.
  5. **Validación con `UserCreateByAdmin`**, sin repetir reglas. El núcleo fija `role=superadmin`, `is_active=True` y
     `data_consent=True` aunque las credenciales digan otra cosa.
  6. **Auditoría:** `CREATE` sobre `User`, con `entity_id` y `performed_by` = la cédula del nuevo superadmin (no hay actor,
     como en `register_tourist`) y `changes={"role": "superadmin", "source": "bootstrap"}`.
  7. **Nada secreto en la salida.** Los errores se imprimen como `VARIABLE: tipo` con `errors(include_input=False)`, y el
     comando usa un motor propio con `echo` apagado.

  ## Consecuencias

  - Hay que correr el comando una vez por entorno. El modo de uso vive en el docstring del módulo; el manual técnico lo
    recoge en su bloque `(PLAN §2b)`.
  - La contraseña viaja solo en el entorno de ese `docker run`, no en los grupos de variables ni en la Web App. Es la
    definitiva hasta que exista el cambio de contraseña.
  - Alta y auditoría son dos `commit()` (A3). Si falla la auditoría, el superadmin queda sin su entrada. Se acepta.
  - Dos ejecuciones simultáneas sobre una base vacía: el índice único rechaza la segunda con `IntegrityError`. Se acepta
    porque es un comando manual.
  - El comando crea su propio motor, como `alembic/env.py`. `app/db/database.py` no cambia.
  - Hay un segundo adaptador, `app.cli`, junto al HTTP; AGENTS §3 describe hoy solo el flujo Router → Servicio.

  ## Alternativas consideradas

  1. **Paso en `cd-pipeline.yml`.** Guardaría una contraseña que no se puede cambiar en los tres grupos de variables, al
     alcance del log del pipeline. Descartada por David.
  2. **`lifespan` de la app.** Correría en cada arranque y obligaría a la Web App a guardar la contraseña.
  3. **Ruta HTTP de "setup".** Una ruta pública que crea un superadmin es una puerta de escalada para quien llegue primero.
  4. **Campos en `Settings`.** La Web App pediría una contraseña que no usa, y el comando exigiría los secretos de JWT,
     correo y Azure (el caso de Alembic, ADR-0013, punto 5).
  5. **Migración de datos.** Los secretos no van en `alembic/`, y una migración corre una vez en la historia del esquema,
     no "si no hay superadmin".
  6. **Script en `scripts/`.** Quedaría fuera de mypy, de la cobertura (`source = ["app"]`) y de import-linter
     (`root_package = "app"`).

  ## Evidencia

  - Sonda del plan (13 nov, pydantic 2.12.5): `str(ValidationError)` de `UserCreateByAdmin` contiene la contraseña.
    `errors(include_input=False, include_url=False)` da `[(('password',), 'value_error')]`. `SecretStr` sale como
    `'**********'`.
  - Copia de `4f10660` con el texto del plan: de 638 a 675 tests y de 96,82 % a 97,37 %. Con `"app.api | app.cli"`, un
    import de `app.cli` desde `app.services` da `3 kept, 1 broken`. El mutante `echo=True` en el motor del comando lo
    tumba un test.
  - Documentación: pydantic-settings, SQLAlchemy asyncio e import-linter (layers), enlaces en
    `docs/deuda/BE-34/plan.md`, sección Referencias.
  ```
- **Tests (RED primero):** no aplica (documento). Lo vigila la compuerta (`check_docs` no lo evalúa; no cambia ninguna
  cifra).
- **Criterio de aceptación:** compuerta como la fila B. `git show --stat --format= <sha B>` lista solo el ADR. La línea
  "Estado" lleva una fecha real, no `<FECHA>`.
- **Fuera de alcance:** `AGENTS.md`, `docs/CONTEXT.md` y el manual técnico (Residuales R1 y R4), ADR-0013 (no se edita;
  este ADR lo complementa).
- **Commit:**
  ```
  docs(adr): add ADR-0015, the first superadmin comes from a manual command

  Both product paths to a superadmin already require one, and nothing
  in app/, alembic/ or scripts/ creates the first (BE-34). The ADR
  records David's eight decisions on how to close that gap before the
  code that cites it lands: a python -m command in a new app.cli
  package, credentials in a sibling of Settings, "exists" meaning an
  active non-deleted superadmin, no takeover of existing accounts, and
  no secret in the output.

  It also lists the rejected paths (CD step, lifespan, setup route,
  Settings fields, data migration, scripts/) and their reasons.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase C — `SuperadminBootstrapSettings` y su bloque en `.env.example`

- **Archivos (3):** `app/core/config.py`, `.env.example`, `tests/test_config.py`. Dominio: configuración.
- **Cambios exactos:**
  1. `config.py`: `from pydantic import Field` → `from pydantic import Field, SecretStr`. Entre el final de `Settings`
     (`return self.mail_from or self.mail_username`) y `@lru_cache` / `def get_settings`, con dos líneas en blanco a cada
     lado:
     ```python
     class SuperadminBootstrapSettings(DatabaseSettings):
         """Credentials of the first superadmin, read only by the bootstrap command (ADR-0015).

         A sibling of Settings, not a part of it: the web app never asks for nor keeps the
         superadmin password, and the command runs with the database URL and these five variables
         alone, as the migrations do. This class only reads them: the account rules (cedula, names,
         password strength) belong to UserCreateByAdmin and are not repeated here.

         Attributes:
             superadmin_cedula: Cedula of the account to create. Required.
             superadmin_email: Email of the account to create. Required.
             superadmin_first_name: First name(s). Required.
             superadmin_last_name: Last name(s). Required.
             superadmin_password: Initial password; SecretStr keeps it out of repr and logs. Required.
         """

         superadmin_cedula: str
         superadmin_email: str
         superadmin_first_name: str
         superadmin_last_name: str
         superadmin_password: SecretStr
     ```
  2. `.env.example`: al final, tras `CORS_ORIGINS=http://localhost:3000`, una línea en blanco y:
     ```
     # ==========================================
     # First superadmin (read only by: python -m app.cli.bootstrap_superadmin; ADR-0015)
     # ==========================================
     # The web app never reads these. Run the command once per environment. This example password
     # is rejected on purpose: set one with 8+ characters, an upper case, a lower case and a digit.
     SUPERADMIN_CEDULA=1000000000
     SUPERADMIN_EMAIL=superadmin@example.com
     SUPERADMIN_FIRST_NAME=Nombre
     SUPERADMIN_LAST_NAME=Apellido
     SUPERADMIN_PASSWORD=DIGITAR_CONTRASEÑA_PRIVADA
     ```
  3. `tests/test_config.py`:
     - En el import de `app.core.config`, `    SuperadminBootstrapSettings,` tras `    Settings,`. Tras el cierre `)`
       de ese import: `from app.schemas.user import UserCreateByAdmin, UserRole`.
     - Tras el cierre de `VALID_REQUIRED`, con una línea en blanco antes:
       ```python
       BOOTSTRAP_VALUES = {
           "database_url": "sqlite+aiosqlite:///:memory:",
           "superadmin_cedula": "900000001",
           "superadmin_email": "root@test.com",
           "superadmin_first_name": "Ana",
           "superadmin_last_name": "Diaz",
           "superadmin_password": "Bootstrap-sentinel-1",
       }
       ```
     - Entre `_set_required` y `_clear`:
       ```python
       def _set_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
           """Gives every bootstrap credential, and the database URL, a valid value."""
           for name, value in BOOTSTRAP_VALUES.items():
               monkeypatch.setenv(name.upper(), value)
       ```
     - Al final del archivo, tras el test de la fase A:
       ```python
       @pytest.mark.parametrize("field", tuple(BOOTSTRAP_VALUES))
       def test_missing_bootstrap_variable_fails_naming_it(
           monkeypatch: pytest.MonkeyPatch, field: str
       ) -> None:
           """Unhappy path: the bootstrap command needs every credential; a missing one is named."""
           _set_bootstrap(monkeypatch)
           monkeypatch.delenv(field.upper())

           with pytest.raises(ValidationError) as exc_info:
               SuperadminBootstrapSettings(_env_file=None)

           assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [("missing", (field,))]


       def test_bootstrap_settings_need_no_web_app_secret(monkeypatch: pytest.MonkeyPatch) -> None:
           """Happy path: the command runs without the JWT, mail and storage secrets of the web app."""
           _clear(monkeypatch, REQUIRED)
           _set_bootstrap(monkeypatch)

           settings = SuperadminBootstrapSettings(_env_file=None)

           assert set(SuperadminBootstrapSettings.model_fields) == set(BOOTSTRAP_VALUES)
           assert settings.superadmin_cedula == "900000001"
           assert settings.superadmin_password.get_secret_value() == "Bootstrap-sentinel-1"


       def test_bootstrap_password_never_shows_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
           """Edge case: printing or logging the settings object never reveals the password."""
           _set_bootstrap(monkeypatch)

           settings = SuperadminBootstrapSettings(_env_file=None)

           assert "Bootstrap-sentinel-1" not in repr(settings)
           assert "Bootstrap-sentinel-1" not in str(settings.model_dump())


       def test_bootstrap_validation_errors_do_not_echo_values(monkeypatch: pytest.MonkeyPatch) -> None:
           """Unhappy path: a missing credential fails without printing the password already read."""
           _set_bootstrap(monkeypatch)
           monkeypatch.delenv("SUPERADMIN_EMAIL")

           with pytest.raises(ValidationError) as exc_info:
               SuperadminBootstrapSettings(_env_file=None)

           assert "Bootstrap-sentinel-1" not in str(exc_info.value)


       def test_env_example_documents_every_bootstrap_variable() -> None:
           """Edge case: every SuperadminBootstrapSettings field has its upper-case key in .env.example."""
           assert {n.upper() for n in SuperadminBootstrapSettings.model_fields} <= set(
               dotenv_values(ENV_EXAMPLE)
           )


       def test_env_example_password_is_not_a_usable_credential(monkeypatch: pytest.MonkeyPatch) -> None:
           """Edge case: the example password, copied as is, fails the account rules (ADR-0015)."""
           _clear(monkeypatch, tuple(BOOTSTRAP_VALUES))
           settings = SuperadminBootstrapSettings(_env_file=ENV_EXAMPLE)

           with pytest.raises(ValidationError) as exc_info:
               UserCreateByAdmin(
                   cedula=settings.superadmin_cedula,
                   email=settings.superadmin_email,
                   first_name=settings.superadmin_first_name,
                   last_name=settings.superadmin_last_name,
                   password=settings.superadmin_password.get_secret_value(),
                   data_consent=True,
                   role=UserRole.superadmin,
                   is_active=True,
               )

           assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [
               ("value_error", ("password",))
           ]
       ```
- **Tests (RED primero):** se escriben primero los tests y se ejecuta
  `./venv/Scripts/python.exe -m pytest tests/test_config.py -q -p no:cacheprovider -rf`. Medido:
  `ImportError: cannot import name 'SuperadminBootstrapSettings'` (`1 error during collection`). Con `config.py` hecho y
  `.env.example` todavía sin tocar: `2 failed, 33 passed`
  (`test_env_example_documents_every_bootstrap_variable` y `test_env_example_password_is_not_a_usable_credential`). Al
  final: `35 passed`. Mutantes MC1, MC2 y MC3 con los resultados de la tabla.
- **Criterio de aceptación:** compuerta como la fila C. `git show --numstat --format= <sha C>` da `11	0	.env.example`,
  `24	1	app/core/config.py` y `93	0	tests/test_config.py`.
  `./venv/Scripts/python.exe -c "from app.core.config import Settings as S, SuperadminBootstrapSettings as B; print(len(S.model_fields), len(B.model_fields))"`
  → `15 6`.
- **Fuera de alcance:** `Settings`, `REQUIRED`, `OPTIONAL_DEFAULTS`, `conftest.py` (ver Análisis), el núcleo y el comando.
- **Commit:**
  ```
  feat(config): read the first superadmin credentials in a class of their own

  The bootstrap command needs five credentials that the web app must
  never ask for nor keep (BE-34, ADR-0015). SuperadminBootstrapSettings
  extends DatabaseSettings, as a sibling of Settings: the command runs
  with DATABASE_URL and the SUPERADMIN_* variables alone, as the
  migrations do, and Settings keeps its 15 fields.

  - app/core/config.py: the new class; the password is a SecretStr, so
    a repr or a dump of the settings never shows it. The account rules
    stay in UserCreateByAdmin and are not repeated here.
  - .env.example: the five variables, with an example password that
    the account rules reject, so a copied .env is not a usable account.
  - tests/test_config.py: every variable is required and named when
    missing, no web app secret is needed, the password never shows in
    repr or in a validation error, and .env.example documents the five
    with a password that fails validation.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase D — Conteo de superadmins activos y núcleo `bootstrap_superadmin`

- **Archivos (4):** `app/repositories/user_repository.py`, `app/services/superadmin_bootstrap.py` (nuevo),
  `tests/test_user_repository.py` (nuevo), `tests/test_superadmin_bootstrap.py` (nuevo). Dominio: usuarios.
- **Cambios exactos:**
  1. `user_repository.py`: `from sqlalchemy import func` antes de `from sqlalchemy.ext.asyncio import AsyncSession`.
     `from app.models.user import User` → `from app.models.user import User, UserRole`. Entre
     `get_user_by_email_or_cedula` y `get_non_deleted_user_by_email`:
     ```python
         async def count_active_superadmins(self) -> int:
             """Counts the superadmins that can still sign in: active and not soft-deleted.

             The bootstrap command (BE-34) creates a superadmin only when this count is zero.

             Returns:
                 int: Number of rows with role superadmin, is_active true and no deleted_at.
             """
             stmt = (
                 select(func.count())
                 .select_from(User)
                 .where(
                     User.role == UserRole.superadmin,
                     User.is_active.is_(True),
                     User.deleted_at.is_(None),
                 )
             )
             result = await self.db.execute(stmt)
             return result.scalar_one()
     ```
  2. `app/services/superadmin_bootstrap.py`:
     ```python
     """Creation of the first superadmin of an empty platform (BE-34, ADR-0015).

     No HTTP route can create the first superadmin: provisioning and role changes already require
     one. This service is called by the bootstrap command (app/cli/bootstrap_superadmin.py), run by
     an operator, never by the web app.
     """

     from app.core.exceptions import AlreadyExistsError
     from app.core.security import get_password_hash
     from app.models.audit import AuditAction
     from app.models.user import User, UserRole
     from app.repositories.user_repository import UserRepository
     from app.schemas.user import UserCreateByAdmin
     from app.services.audit_service import AuditService


     async def bootstrap_superadmin(
         credentials: UserCreateByAdmin,
         user_repo: UserRepository,
         audit_service: AuditService,
     ) -> User | None:
         """Creates an active superadmin when none can sign in; otherwise writes nothing.

         Idempotent: while an active, non-deleted superadmin exists, every call returns None. The
         account is always an active superadmin, whatever role or is_active the credentials carry.
         It never promotes, reactivates or recovers an existing account: a cedula or email already
         in any row (any role, active, inactive or deleted) stops it, so it is no escalation path.
         There is no authenticated actor, so the new superadmin is recorded as the author of its
         own creation, as a tourist is in register_tourist.

         Args:
             credentials (UserCreateByAdmin): Account data, already validated by the account rules.
             user_repo (UserRepository): Data access for users.
             audit_service (AuditService): Records the creation.

         Returns:
             User | None: The new superadmin, or None when an active one already exists.

         Raises:
             AlreadyExistsError: When the cedula or email already belongs to an account.
         """
         if await user_repo.count_active_superadmins() > 0:
             return None

         existing_user = await user_repo.get_user_by_email_or_cedula(
             email=credentials.email, cedula=credentials.cedula
         )
         if existing_user:
             raise AlreadyExistsError(
                 "La cédula o el correo del superadministrador ya pertenecen a una cuenta."
             )

         new_user = User(
             cedula=credentials.cedula,
             email=credentials.email,
             first_name=credentials.first_name,
             last_name=credentials.last_name,
             phone=credentials.phone,
             password_hash=get_password_hash(credentials.password),
             role=UserRole.superadmin,
             data_consent=True,
             is_active=True,
         )
         saved_user = await user_repo.create_user(new_user)

         await audit_service.log_transaction(
             entity_name="User",
             entity_id=saved_user.cedula,
             action=AuditAction.CREATE,
             performed_by=saved_user.cedula,
             changes={"role": UserRole.superadmin.value, "source": "bootstrap"},
         )

         return saved_user
     ```
  3. `tests/test_user_repository.py`:
     ```python
     """Tests for UserRepository.count_active_superadmins: which superadmins can sign in."""

     from datetime import UTC, datetime

     import pytest

     from app.models.user import UserRole
     from app.repositories.user_repository import UserRepository


     async def test_count_active_superadmins_counts_each_active_one(db_session, persist_user):
         """Happy path: every active, non-deleted superadmin is counted, and only those."""
         await persist_user(role=UserRole.superadmin)
         await persist_user(role=UserRole.superadmin)
         await persist_user(role=UserRole.admin)
         await persist_user(role=UserRole.tourist)

         assert await UserRepository(db_session).count_active_superadmins() == 2


     async def test_count_active_superadmins_on_empty_database_is_zero(db_session):
         """Edge case: with no users at all, the count is zero, not None."""
         assert await UserRepository(db_session).count_active_superadmins() == 0


     @pytest.mark.parametrize(
         "overrides",
         [
             {"is_active": False},
             {"is_active": False, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)},
             {"is_active": True, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)},
         ],
         ids=["inactive", "soft-deleted", "deleted-but-active-flag"],
     )
     async def test_count_active_superadmins_skips_those_who_cannot_sign_in(
         db_session, persist_user, overrides
     ):
         """Unhappy path: an inactive or soft-deleted superadmin does not count."""
         await persist_user(role=UserRole.superadmin, **overrides)

         assert await UserRepository(db_session).count_active_superadmins() == 0
     ```
  4. `tests/test_superadmin_bootstrap.py`. Las cédulas `900000001`/`900000002` quedan fuera del rango de `make_user`
     (`1000000000 + n`): así ningún `-k` las hace chocar con una fila de la fábrica.
     ```python
     """Tests for bootstrap_superadmin: the first superadmin of an empty platform (BE-34, ADR-0015).

     Real repositories over the test database: what matters is which rows exist afterwards.
     """

     from datetime import UTC, datetime

     import pytest
     from sqlalchemy import func, select

     from app.core.exceptions import AlreadyExistsError
     from app.core.security import verify_password
     from app.models.audit import AuditAction, AuditLog
     from app.models.user import User, UserRole
     from app.repositories.audit_repository import AuditRepository
     from app.repositories.user_repository import UserRepository
     from app.schemas.user import UserCreateByAdmin
     from app.schemas.user import UserRole as SchemaUserRole
     from app.services.audit_service import AuditService
     from app.services.superadmin_bootstrap import bootstrap_superadmin

     PASSWORD = "Bootstrap2026x"


     def _credentials(**overrides) -> UserCreateByAdmin:
         values = dict(
             cedula="900000001",
             email="root@test.com",
             first_name="Ana",
             last_name="Diaz",
             password=PASSWORD,
             data_consent=True,
             role=SchemaUserRole.superadmin,
             is_active=True,
         )
         values.update(overrides)
         return UserCreateByAdmin(**values)


     async def _run(db_session, credentials: UserCreateByAdmin) -> User | None:
         return await bootstrap_superadmin(
             credentials,
             UserRepository(db_session),
             AuditService(AuditRepository(db_session)),
         )


     async def _count(db_session, model: type[User] | type[AuditLog]) -> int:
         return int(await db_session.scalar(select(func.count()).select_from(model)))


     async def test_bootstrap_creates_an_active_superadmin_on_an_empty_database(db_session):
         """Happy path: with no users, it creates the superadmin and audits it as its own author."""
         created = await _run(db_session, _credentials())

         assert created is not None
         user = await db_session.scalar(select(User))
         assert (user.cedula, user.email, user.first_name, user.last_name) == (
             "900000001",
             "root@test.com",
             "Ana",
             "Diaz",
         )
         assert (user.role, user.is_active, user.data_consent, user.deleted_at) == (
             UserRole.superadmin,
             True,
             True,
             None,
         )
         assert verify_password(PASSWORD, user.password_hash)
         log = await db_session.scalar(select(AuditLog))
         assert (log.entity_name, log.entity_id, log.action, log.performed_by, log.changes) == (
             "User",
             "900000001",
             AuditAction.CREATE,
             "900000001",
             {"role": "superadmin", "source": "bootstrap"},
         )


     async def test_bootstrap_writes_nothing_when_an_active_superadmin_exists(db_session, persist_user):
         """Unhappy path: an active superadmin already exists, so nothing is created or audited."""
         await persist_user(role=UserRole.superadmin)

         assert await _run(db_session, _credentials()) is None

         assert await _count(db_session, User) == 1
         assert await _count(db_session, AuditLog) == 0


     async def test_bootstrap_second_run_writes_nothing(db_session):
         """Edge case: idempotent; the second run finds the first superadmin and stops."""
         await _run(db_session, _credentials())

         assert await _run(db_session, _credentials(cedula="900000002", email="b@test.com")) is None

         assert await _count(db_session, User) == 1
         assert await _count(db_session, AuditLog) == 1


     @pytest.mark.parametrize("shared", ["cedula", "email"])
     @pytest.mark.parametrize(
         "existing",
         [
             {"role": UserRole.tourist, "is_active": True},
             {"role": UserRole.admin, "is_active": False},
             {
                 "role": UserRole.superadmin,
                 "is_active": False,
                 "deleted_at": datetime(2026, 1, 1, tzinfo=UTC),
             },
         ],
         ids=["active-tourist", "inactive-admin", "deleted-superadmin"],
     )
     async def test_bootstrap_never_takes_over_an_existing_account(
         db_session, persist_user, shared, existing
     ):
         """Unhappy path: a cedula or email already in any row fails; nothing is promoted or written."""
         account = await persist_user(**existing)
         credentials = _credentials(**{shared: getattr(account, shared)})

         with pytest.raises(AlreadyExistsError):
             await _run(db_session, credentials)

         await db_session.refresh(account)
         assert (account.role, account.is_active, account.deleted_at is None) == (
             existing["role"],
             existing["is_active"],
             "deleted_at" not in existing,
         )
         assert await _count(db_session, User) == 1
         assert await _count(db_session, AuditLog) == 0


     @pytest.mark.parametrize(
         "overrides",
         [{"is_active": False}, {"is_active": False, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)}],
         ids=["inactive", "soft-deleted"],
     )
     async def test_bootstrap_creates_when_no_superadmin_can_sign_in(
         db_session, persist_user, overrides
     ):
         """Edge case: superadmins that are inactive or deleted do not count; a new one is created."""
         await persist_user(role=UserRole.superadmin, **overrides)

         created = await _run(db_session, _credentials())

         assert created is not None
         assert (created.role, created.is_active) == (UserRole.superadmin, True)
         assert await _count(db_session, User) == 2


     async def test_bootstrap_always_creates_an_active_superadmin(db_session):
         """Edge case: the role and is_active of the credentials are ignored, not trusted."""
         created = await _run(db_session, _credentials(role=SchemaUserRole.admin, is_active=False))

         assert created is not None
         await db_session.refresh(created)
         assert (created.role, created.is_active) == (UserRole.superadmin, True)
     ```
- **Tests (RED primero):**
  1. Primero `tests/test_user_repository.py` y luego
     `./venv/Scripts/python.exe -m pytest tests/test_user_repository.py -q -p no:cacheprovider -rf --tb=no`. Medido:
     `5 failed` (`AttributeError`, el método no existe).
  2. Después el método, y luego `tests/test_superadmin_bootstrap.py` antes del servicio. Medido:
     `ModuleNotFoundError: No module named 'app.services.superadmin_bootstrap'`.
  3. Al final: `17 passed` entre los dos archivos. Mutantes MD1 a MD7 con los resultados de la tabla.
- **Criterio de aceptación:** compuerta como la fila D. `git show --numstat --format= <sha D>` da
  `22	1	app/repositories/user_repository.py`, `74	0	app/services/superadmin_bootstrap.py`,
  `159	0	tests/test_superadmin_bootstrap.py` y `41	0	tests/test_user_repository.py`.
- **Fuera de alcance:** `create_user` y su `commit()` (A3), `UserService` y la política, el comando (fase E). La regla de
  BE-35 no se implementa; el conteo solo queda disponible para ella (R6).
- **Commit:**
  ```
  feat(users): create the first superadmin only when no active one exists

  Provisioning and role changes both require a superadmin, so a
  database without one could only be fixed with raw SQL (BE-34). The
  bootstrap core creates one, and only when it is safe (ADR-0015):

  - app/repositories/user_repository.py: count_active_superadmins
    counts superadmins that can sign in (active, not soft-deleted).
  - app/services/superadmin_bootstrap.py: bootstrap_superadmin writes
    nothing while that count is not zero; refuses a cedula or email
    already in any row, whatever its role or state, so it never
    promotes, reactivates or recovers an account; always creates an
    active superadmin, whatever the credentials say; and audits the
    creation with the new cedula as its author and source=bootstrap.
  - tests: the count over every role and state, and the five cases of
    the addendum plus the takeover matrix, on real repositories.

  create_user still commits on its own (A3); reusing it is accepted.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase E — Comando `python -m app.cli.bootstrap_superadmin`

- **Archivos (4):** `app/cli/__init__.py` (nuevo), `app/cli/bootstrap_superadmin.py` (nuevo), `pyproject.toml`,
  `tests/test_bootstrap_superadmin_command.py` (nuevo). Dominio: comando de operador.
- **Cambios exactos:**
  1. `app/cli/__init__.py`, una línea:
     `"""Commands an operator runs by hand with python -m, outside the web app (ADR-0015)."""`
  2. `pyproject.toml`, en el contrato de capas:
     - `name = "Capas: api -> services -> repositories -> models"` →
       `name = "Capas: api | cli -> services -> repositories -> models"`.
     - `    "app.api",` → `    "app.api | app.cli",`.
  3. `app/cli/bootstrap_superadmin.py`:
     ```python
     """Creates the first superadmin when no active one exists (BE-34, ADR-0015).

     Run by an operator, once per environment, with the image the CD deploys, as the CD runs the
     migrations; never at startup, never over HTTP:

         docker run --rm -e DATABASE_URL=... -e SUPERADMIN_CEDULA=... -e SUPERADMIN_EMAIL=...
             -e SUPERADMIN_FIRST_NAME=... -e SUPERADMIN_LAST_NAME=... -e SUPERADMIN_PASSWORD=...
             <image> python -m app.cli.bootstrap_superadmin

     Locally: ./venv/Scripts/python.exe -m app.cli.bootstrap_superadmin, with the six variables in
     .env or in the environment. Exit code 0: created, or an active superadmin already exists (nothing
     written). Exit code 1: a variable is missing or breaks the account rules, or the cedula or email
     already belongs to an account (nothing written). The password is never printed.
     """

     import asyncio
     import sys

     from pydantic import ValidationError
     from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

     from app.core.config import SuperadminBootstrapSettings
     from app.core.exceptions import AlreadyExistsError
     from app.models.user import User
     from app.repositories.audit_repository import AuditRepository
     from app.repositories.user_repository import UserRepository
     from app.schemas.user import UserCreateByAdmin, UserRole
     from app.services.audit_service import AuditService
     from app.services.superadmin_bootstrap import bootstrap_superadmin


     async def _bootstrap(database_url: str, credentials: UserCreateByAdmin) -> User | None:
         """Runs the bootstrap in one session over an engine of its own, disposed at the end.

         The engine is not the web app's (app/db/database.py, echo=True): with echo off, the INSERT
         parameters (email, cedula, password hash) are not written to the output.

         Args:
             database_url (str): SQLAlchemy async URL of the target database.
             credentials (UserCreateByAdmin): Validated account data.

         Returns:
             User | None: The new superadmin, or None when an active one already exists.

         Raises:
             AlreadyExistsError: When the cedula or email already belongs to an account.
         """
         engine = create_async_engine(database_url)
         try:
             session_factory = async_sessionmaker(engine, expire_on_commit=False)
             async with session_factory() as session:
                 return await bootstrap_superadmin(
                     credentials,
                     UserRepository(session),
                     AuditService(AuditRepository(session)),
                 )
         finally:
             await engine.dispose()


     def _report(error: ValidationError) -> None:
         """Prints each failing variable and its error type to stderr, never its value.

         Args:
             error (ValidationError): From SuperadminBootstrapSettings or UserCreateByAdmin; an
                 account field (password, cedula...) is reported by its variable name.
         """
         for detail in error.errors(include_input=False, include_url=False):
             field = str(detail["loc"][0])
             if field not in SuperadminBootstrapSettings.model_fields:
                 field = f"superadmin_{field}"
             print(f"{field.upper()}: {detail['type']}", file=sys.stderr)


     def main() -> int:
         """Reads and validates the credentials, then creates the superadmin if none is active.

         Returns:
             int: The exit code: 0 created or already present; 1 on error, with nothing written.
         """
         try:
             settings = SuperadminBootstrapSettings()
             credentials = UserCreateByAdmin(
                 cedula=settings.superadmin_cedula,
                 email=settings.superadmin_email,
                 first_name=settings.superadmin_first_name,
                 last_name=settings.superadmin_last_name,
                 password=settings.superadmin_password.get_secret_value(),
                 data_consent=True,
                 role=UserRole.superadmin,
                 is_active=True,
             )
         except ValidationError as error:
             _report(error)
             return 1

         try:
             created = asyncio.run(_bootstrap(settings.database_url, credentials))
         except AlreadyExistsError:
             print(
                 "SUPERADMIN_CEDULA o SUPERADMIN_EMAIL ya pertenecen a una cuenta; no se escribió nada.",
                 file=sys.stderr,
             )
             return 1

         if created is None:
             print("Ya existe un superadministrador activo; no se escribió nada.")
         else:
             print(f"Superadministrador creado: {created.email}")
         return 0


     if __name__ == "__main__":
         sys.exit(main())
     ```
  4. `tests/test_bootstrap_superadmin_command.py`:
     ```python
     """Tests for the bootstrap command, python -m app.cli.bootstrap_superadmin (BE-34, ADR-0015).

     The command opens its own engine from DATABASE_URL, so each test points it at a file database
     of its own, with the schema already created. Every variable is set in the process environment,
     which beats any developer .env file (ADR-0013, point 3).
     """

     import asyncio
     import os
     import runpy
     import subprocess
     import sys
     from pathlib import Path
     from typing import Any

     import pytest
     from sqlalchemy import func, insert, select
     from sqlalchemy.ext.asyncio import create_async_engine

     from app.cli.bootstrap_superadmin import main
     from app.core.security import verify_password
     from app.db.database import Base
     from app.models.audit import AuditLog
     from app.models.user import User, UserRole

     PASSWORD = "Bootstrap-sentinel-7"

     VALID_VARIABLES = {
         "SUPERADMIN_CEDULA": "900000001",
         "SUPERADMIN_EMAIL": "root@test.com",
         "SUPERADMIN_FIRST_NAME": "Ana",
         "SUPERADMIN_LAST_NAME": "Diaz",
         "SUPERADMIN_PASSWORD": PASSWORD,
     }

     # The required secrets of Settings: the web app needs them, the command must not (ADR-0015).
     WEB_APP_SECRETS = (
         "JWT_SECRET_KEY",
         "MAIL_USERNAME",
         "MAIL_PASSWORD",
         "AZURE_STORAGE_CONNECTION_STRING",
     )

     REPO_ROOT = Path(__file__).resolve().parents[1]


     async def _create_schema(url: str) -> None:
         """Creates every table in the database at url."""
         engine = create_async_engine(url)
         async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
         await engine.dispose()


     async def _execute(url: str, statement: Any) -> list[Any]:
         """Runs one statement on an engine of its own, commits, and returns its rows, if any."""
         engine = create_async_engine(url)
         async with engine.begin() as conn:
             result = await conn.execute(statement)
             rows = list(result.all()) if result.returns_rows else []
         await engine.dispose()
         return rows


     def _count(url: str, model: type[User] | type[AuditLog]) -> int:
         return int(asyncio.run(_execute(url, select(func.count()).select_from(model)))[0][0])


     @pytest.fixture
     def database_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
         """A file database with the schema created, and the command's six variables set."""
         url = f"sqlite+aiosqlite:///{tmp_path / 'bootstrap.db'}"
         asyncio.run(_create_schema(url))
         monkeypatch.setenv("DATABASE_URL", url)
         for name, value in VALID_VARIABLES.items():
             monkeypatch.setenv(name, value)
         return url


     def test_command_creates_the_superadmin_without_writing_secrets(
         database_url: str, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
     ) -> None:
         """Happy path: exit 0, one active superadmin, one audit entry; no password or hash shown."""
         assert main() == 0

         users = asyncio.run(
             _execute(database_url, select(User.cedula, User.role, User.is_active, User.password_hash))
         )
         assert [(u.cedula, u.role, u.is_active) for u in users] == [
             ("900000001", UserRole.superadmin, True)
         ]
         assert verify_password(PASSWORD, users[0].password_hash)
         assert _count(database_url, AuditLog) == 1
         output = capsys.readouterr()
         assert output.err == ""
         assert PASSWORD not in output.out
         assert users[0].password_hash not in output.out + caplog.text


     def test_command_second_run_exits_zero_and_writes_nothing(
         database_url: str, capsys: pytest.CaptureFixture[str]
     ) -> None:
         """Edge case: an operator may run it twice; the second run changes nothing."""
         assert main() == 0

         assert main() == 0

         assert (_count(database_url, User), _count(database_url, AuditLog)) == (1, 1)
         output = capsys.readouterr()
         assert output.err == ""
         assert PASSWORD not in output.out


     def test_command_fails_when_the_email_belongs_to_another_account(
         database_url: str, capsys: pytest.CaptureFixture[str]
     ) -> None:
         """Unhappy path: exit 1 with nothing written; the tourist keeps its role."""
         asyncio.run(
             _execute(
                 database_url,
                 insert(User).values(
                     cedula="2000000002",
                     email="root@test.com",
                     password_hash="hash",
                     first_name="Luis",
                     last_name="Rojas",
                     role=UserRole.tourist,
                     data_consent=True,
                     is_active=True,
                 ),
             )
         )

         assert main() == 1

         users = asyncio.run(_execute(database_url, select(User.cedula, User.role)))
         assert [(u.cedula, u.role) for u in users] == [("2000000002", UserRole.tourist)]
         assert _count(database_url, AuditLog) == 0
         output = capsys.readouterr()
         assert output.out == ""
         assert PASSWORD not in output.err


     @pytest.mark.parametrize(
         ("variable", "value", "expected_err"),
         [
             ("SUPERADMIN_PASSWORD", "sinmayuscula1", "SUPERADMIN_PASSWORD: value_error\n"),
             ("SUPERADMIN_CEDULA", "12AB", "SUPERADMIN_CEDULA: string_too_short\n"),
             ("DATABASE_URL", "", "DATABASE_URL: string_too_short\n"),
         ],
         ids=["weak-password", "short-cedula", "empty-database-url"],
     )
     def test_command_rejects_bad_configuration_naming_only_the_variable(
         database_url: str,
         monkeypatch: pytest.MonkeyPatch,
         capsys: pytest.CaptureFixture[str],
         variable: str,
         value: str,
         expected_err: str,
     ) -> None:
         """Unhappy path: exit 1 before any write; stderr names the variable, never a value."""
         monkeypatch.setenv(variable, value)

         assert main() == 1

         assert _count(database_url, User) == 0
         assert capsys.readouterr() == ("", expected_err)


     def test_command_runs_as_a_module_and_exits_with_the_code_of_main(
         database_url: str, monkeypatch: pytest.MonkeyPatch
     ) -> None:
         """Edge case: python -m app.cli.bootstrap_superadmin exits with what main returns."""
         monkeypatch.setenv("SUPERADMIN_PASSWORD", "sinmayuscula1")
         monkeypatch.delitem(sys.modules, "app.cli.bootstrap_superadmin")

         with pytest.raises(SystemExit) as exc_info:
             runpy.run_module("app.cli.bootstrap_superadmin", run_name="__main__")

         assert exc_info.value.code == 1
         assert _count(database_url, User) == 0


     def test_command_runs_without_the_web_app_secrets(database_url: str) -> None:
         """Edge case: run as a child process with the web app secrets empty, it still creates it.

         The suite's environment carries every secret (root conftest.py), so a test that calls main()
         cannot see an import that builds Settings. Empty values beat any .env file (ADR-0013, point
         3) and fail Field(min_length=1): if the command built Settings, the child would exit 1.
         """
         env = os.environ | dict.fromkeys(WEB_APP_SECRETS, "")

         completed = subprocess.run(
             [sys.executable, "-m", "app.cli.bootstrap_superadmin"],
             cwd=REPO_ROOT,
             env=env,
             capture_output=True,
             text=True,
             timeout=60,
             check=False,
         )

         assert completed.returncode == 0, completed.stderr
         users = asyncio.run(_execute(database_url, select(User.cedula, User.role, User.is_active)))
         assert [(u.cedula, u.role, u.is_active) for u in users] == [
             ("900000001", UserRole.superadmin, True)
         ]
         assert PASSWORD not in completed.stdout + completed.stderr
     ```
- **Tests (RED primero):** primero el archivo de tests, y luego
  `./venv/Scripts/python.exe -m pytest tests/test_bootstrap_superadmin_command.py -q -p no:cacheprovider --tb=line`.
  Medido: `ModuleNotFoundError: No module named 'app.cli'`. Al final: `8 passed`. Mutantes ME1 a ME6 y MK1 con los
  resultados de la tabla (MK1 se mide con
  `./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"` en la copia).
  Por qué cada truco del test:
  - Base de archivo en `tmp_path`: el comando abre su propio motor, y `:memory:` le daría una base vacía sin tablas.
  - `delitem` antes de `runpy`: evita el `RuntimeWarning` de reejecutar un módulo ya importado, así que los warnings
    siguen en 8.
  - `caplog`: es el único canal donde se ve el `echo` (ME4).
  - Proceso hijo con los cuatro secretos de `Settings` a cadena vacía (E0.3). La suite trae todos los secretos
    (`conftest.py` de la raíz), así que un `main()` dentro de ella no ve un import que construya `Settings`. La cadena
    vacía gana al `.env` (ADR-0013, punto 3) y no pasa `Field(min_length=1)`. Medido con ME6: el hijo sale con 1
    (`4 validation errors for Settings`, `string_too_short`) y cae solo este test. Si el hijo hereda el entorno sin
    vaciarlos, ME6 sobrevive (`8 passed`). `cwd=REPO_ROOT` hace que `-m` importe el `app/` de este árbol y no el de la
    instalación editable del venv. La cobertura no mide al hijo: sigue en 97,37 %.
- **Criterio de aceptación:** compuerta como la fila E, con `app\cli\bootstrap_superadmin.py` al 100 % en el informe de
  cobertura. `git show --numstat --format= <sha E>` da `1	0	app/cli/__init__.py`,
  `114	0	app/cli/bootstrap_superadmin.py`, `2	2	pyproject.toml` y
  `208	0	tests/test_bootstrap_superadmin_command.py`. Salida de import-linter:
  `Capas: api | cli -> services -> repositories -> models KEPT`.
- **Fuera de alcance:** `Dockerfile` (la imagen ya copia `app/` e instala el paquete), `cd-pipeline.yml`,
  `app/db/database.py`, el manual técnico (R4) y `AGENTS.md` (R1).
- **Commit:**
  ```
  feat(cli): add python -m app.cli.bootstrap_superadmin for operators

  The bootstrap core needs an entry point that an operator runs once
  per environment, as the CD runs the migrations, and that never runs
  at startup, over HTTP or as a CD step (BE-34, ADR-0015).

  - app/cli/bootstrap_superadmin.py: reads SuperadminBootstrapSettings,
    validates through UserCreateByAdmin, runs the core on an engine of
    its own and exits 0 (created or already present) or 1 (bad
    variable or taken cedula/email, nothing written). Validation errors
    print only "VARIABLE: type": str(ValidationError) includes the
    input, the password among it. The engine has echo off: the app's
    engine (echo=True) would write the INSERT with the password hash.
  - app/cli/__init__.py: the new package of operator commands.
  - pyproject.toml: app.cli joins the layers contract as an independent
    sibling of app.api, so services cannot import it and the two
    adapters cannot import each other.
  - tests: create, second run, taken email, three bad variables, the
    python -m path, and a child process with the web app secrets
    empty, so an import that builds Settings fails here and not in the
    docker run. Each runs on a file database of its own; no password
    in stdout or stderr and no hash in stdout or the log.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fases F y G — BE-51: un correo es una sola cuenta, guardado siempre en minúsculas (E1, E2)

**Reescritas por E2 (14 nov 2026). No se ejecutan hasta que David las apruebe (E3).** El mecanismo es el de E2, punto 3:
el correo se pasa a minúsculas al entrar por los schemas, una restricción `CHECK` en la base lo garantiza y la unicidad
la sigue dando `ix_users_email`. Siguen partidas (E2, punto 2): **F** = ADR-0016 (dominio documentación) y **G** = el
código (5 archivos, dominio usuarios). Orden A → … → E → F → G. **G no toca ningún archivo de A–E** (la versión del
13 nov editaba `user_repository.py` y `tests/test_user_repository.py`); depende de D solo porque un test suyo llama a
`bootstrap_superadmin`. Las cifras de F y G se midieron el 14 nov sobre copias de `HEAD` con los 12 archivos de A–E; la
compuerta de esa copia da la fila E exacta (`675 passed`, `97.37%`, `1031` stmts, `67 files`, `62 source files`).

**Medición (E2, punto 3.6), sobre la copia con A–E.** Cada punto dice qué se hace con lo medido.
- **Correos con mayúsculas en los tests.** El grep de E2,
  `grep -rnE '"[^" ]*[A-Z][^" ]*@[^" ]*"' tests conftest.py`, da una sola línea:
  `tests/test_user_response.py:61:        ("email", "Ana@EXAMPLE.COM"),`. Con comillas simples, 0. Con cualquier token `x@y`
  que lleve mayúsculas, la misma línea. Las fábricas generan `user{n}@test.com` (`tests/conftest.py:193`). Con el modelo
  y los schemas de G, y ese test sin tocar: `1 failed, 385 passed`. Solo cae
  `test_my_profile_returns_stored_values_verbatim[mixed_case_domain]`, con
  `CHECK constraint failed: ck_users_email_lowercase`. **Qué se hace:** G borra ese caso (el par y su id, 2 líneas). La
  base ya no puede guardar ese valor, así que el caso deja de describir un dato posible. A9 sigue cubriendo el correo con
  `dotless_domain`.
- **Un token de verificación cuyo `sub` difiere en mayúsculas.** `activate_user` compara exacto
  (`user_repository.py:56` tras D) y `verify_email_account` responde `NotFoundError` (`user_service.py:141-144`): 404 y
  la cuenta sigue inactiva. **Qué se hace:** un test fija el rechazo (`test_verification_token_in_another_case_is_rejected`).
  El mutante MG8, que compara `lower()` en `activate_user`, lo tumba, y solo a él.
- **Un `PATCH` que solo cambia las mayúsculas del propio correo.** Llega en minúsculas, así que es el mismo valor: 200 y
  el correo no cambia. **Qué se hace:** lo fija `test_patch_changing_only_the_case_keeps_the_email`. Como todo `PATCH`
  con campos, deja una entrada `UPDATE` en la auditoría (`user_service.py:288-295`). Es comportamiento previo, sin cambio.
- **`lower()` en SQLite, en PostgreSQL y en Python.** Sonda P2, sobre SQLite: `lower('ÁNGEL@x.com')` da `'Ángel@x.com'`.
  Con la restricción, SQLite rechaza `Root@test.com` insertado sin schema, pero acepta `Ángel@x.com`. **Qué se hace:**
  se declara en ADR-0016 y en R12, y no se cubre: cubrirlo exige PostgreSQL en la suite (BE-31). Por los schemas no
  llega, porque `str.lower()` pliega Unicode (tabla siguiente).
- **`EmailStr` admite la parte local no ASCII y no la toca; solo pasa el dominio a minúsculas.** Sonda P1 (pydantic
  2.12.5, email-validator 2.3.0):

  | Entrada | `EmailStr` | `LowercaseEmail` |
  |---|---|---|
  | `Root@Test.COM` | `Root@test.com` | `root@test.com` |
  | `ÁNGEL@X.com` | `ÁNGEL@x.com` | `ángel@x.com` |
  | `Straße@x.com` | `Straße@x.com` | `straße@x.com` |
  | `İSTANBUL@x.com` | `İSTANBUL@x.com` | `i̇stanbul@x.com` (`i` + U+0307: `str.lower()` alarga la cadena) |
  | `  Root@test.com  ` | `Root@test.com` | `root@test.com` |

  `LowercaseEmail` es idempotente en los cinco casos (`v == v.lower()`). **Qué se hace:** un test fija
  `ÁNGEL@Test.com` → `ángel@test.com`.
- **Vías que escriben un correo** (`git grep -n -E '\bUser\(|setattr' -- app` y los usos de los schemas): las altas
  (`user_service.py:81` y `:405`; tras D, también `superadmin_bootstrap.py`) toman el correo de `UserCreate` o
  `UserCreateByAdmin`, y el `PATCH` (`user_service.py:285`) lo toma de `UserUpdate`. Ninguna escribe un correo sin pasar
  por los tres schemas. Hoy no se pasa ningún correo a minúsculas:
  `git grep -n -i -E 'lower\(|ilike|casefold|func\.lower|citext|collat' -- app alembic tests conftest.py scripts` da solo
  `schemas/user.py:100` (`c.islower()`) y `tests/test_main.py:78,107` (cabeceras). Ninguna restricción `CHECK` en el
  repo: `git grep -n -i -E 'CheckConstraint|create_check_constraint|ck_users' -- . ':!docs'` sale vacío. Esta es la
  primera.
- **Alembic.** Cabeza actual: `2cc4b57c136c (head)`. `alembic/env.py` no usa `render_as_batch`. Ninguna FK apunta a
  `users` (`git grep -n ForeignKey -- app/models` → solo `service.py:58`), así que reconstruir la tabla en SQLite no
  arrastra dependencias. Sonda P2b: `op.create_check_constraint` sin modo batch, sobre SQLite, da `NotImplementedError:
  No support for ALTER of constraints in SQLite dialect`. Por eso la migración usa `batch_alter_table`.
- **La migración en un SQLite propio** (sonda P2, el texto exacto del paso 3). `downgrade` deja 0 restricciones.
  `upgrade` sobre filas en minúsculas da
  `[{'sqltext': 'email = lower(email)', 'name': 'ck_users_email_lowercase'}]`, conserva las filas y conserva los
  índices únicos `ix_users_cedula` y `ix_users_email`. `upgrade` con una fila `Juan@test.com` lanza `IntegrityError`
  (`CHECK constraint failed: ck_users_email_lowercase`), y `users` queda sin restricción y con su fila. **Pero queda la
  tabla `_alembic_tmp_users`**: tras el fallo la conexión está fuera de transacción (`in_transaction()` → `False`) y el
  `CREATE TABLE` del batch no se deshace. Por eso los dos tests de la migración
  usan un motor propio y no la base compartida de la suite. En PostgreSQL es una sola sentencia (SQL de abajo) y la
  sesión Mentor midió 0 restricciones tras el fallo.
- **`compare_metadata`**, con el modelo con la restricción frente a una base sin ella, da `[]`. Alembic no compara
  restricciones `CHECK`: su documentación las pone entre lo que autogenerate "can't currently, but will eventually
  detect" (Referencias). **Qué se hace (E2, punto 3.8):** `alembic check` no prueba que la restricción exista, así que el
  paso 19 de la Verificación final la busca en `pg_constraint`.
- **DDL del modelo**, compilado para PostgreSQL y para SQLite: `CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email))`.
- **SQL fuera de línea para PostgreSQL** (`alembic upgrade 2cc4b57c136c:b51f3c9e2a64 --sql`, sin base), literal:
  ```
  BEGIN;

  -- Running upgrade 2cc4b57c136c -> b51f3c9e2a64

  ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email));

  UPDATE alembic_version SET version_num='b51f3c9e2a64' WHERE alembic_version.version_num = '2cc4b57c136c';

  COMMIT;
  ```
  El `downgrade` (`alembic downgrade b51f3c9e2a64:2cc4b57c136c --sql`) da
  `ALTER TABLE users DROP CONSTRAINT ck_users_email_lowercase;` en el mismo marco.

**Mecanismo y por qué así.**
- **Un solo punto de normalización (E2, punto 3.1):** el tipo
  `LowercaseEmail = Annotated[EmailStr, AfterValidator(str.lower)]` en `app/schemas/user.py`, que usan los tres campos.
  Es un tipo, no tres `field_validator`, así que no suma copias a D5. `AfterValidator` corre después de `EmailStr`: pliega
  lo que `EmailStr` ya validó y normalizó (dominio y espacios de los extremos; la sonda P1 lo mide en un modelo sin
  `str_strip_whitespace`). Es el patrón
  de pydantic para validadores reutilizables (Referencias). `UserCreateByAdmin` lo hereda de `UserBase`; el comando de E
  valida con él, así que `SUPERADMIN_EMAIL` también llega en minúsculas.
- **La restricción (E2, punto 3.2):** el texto SQL `"email = lower(email)"`, el mismo en el modelo y en la migración. La
  sonda Mentor usó la expresión `email == func.lower(email)`. Aquí se dicta el texto: compila igual en los dos dialectos
  (medido arriba) y se lee igual en los dos archivos (paso 13 de la Verificación final).
- **La migración** usa `batch_alter_table`. En PostgreSQL emite un `ALTER TABLE` (SQL de arriba); en SQLite reconstruye
  la tabla. Así la suite ejecuta `upgrade()` y `downgrade()` del archivo real (E2, punto 3.5).
- **Las consultas no cambian (E2, punto 3.3):** lo que llega y lo guardado ya están en minúsculas, y `ix_users_email`
  sostiene la unicidad. Un `PATCH` hacia el correo de otra cuenta, escrito como sea, recibe el 409 del handler de
  `IntegrityError` (R11).

**Precondición de G (E2, punto 3.4).** David corre Q1 en `develop`, `staging` y `main`:
```sql
-- Q1: correos guardados con alguna mayúscula (debe dar 0)
SELECT count(*) AS mixed_case FROM users WHERE email <> lower(email);
```
Resultado: 0 en las tres (David, 13 nov, 17:40). Repetida el 14 nov a las 09:20: `count = 0`, pero la captura no muestra
contra qué base (bitácora `2026-11-14`; decisión 6 de E3). Q2 (colisiones) ya no hace falta: con Q1 = 0 todo correo
guardado está en minúsculas, y dos iguales ya los rechazaría `ix_users_email`. G no se ejecuta si Q1 deja de dar 0 en
`develop`. Q1 se repite antes de promover a `staging` y a `main`.

### Fase F — ADR-0016

- **Archivos (1):** `docs/adr/0016-correo-en-minusculas.md` (nuevo). Dominio: decisiones (docs).
- **Cambios exactos:** crear el archivo con este texto. `<FECHA>` es la fecha de E3 que la sesión Mentor anote en este
  plan (E2, punto 6); si no figura, la fase se detiene. Las frases en inglés entre comillas son de la guía de OWASP,
  leída el 14 nov (Referencias); la de "Store both" une en una línea los dos puntos de una lista.
  ```markdown
  # ADR-0016 — Un correo, una sola forma: se guarda en minúsculas y la base lo exige

  - **Estado:** aceptado (David, <FECHA>, al aprobar las fases F y G del plan de BE-34)
  - **Propuesta:** Claude, `plan-redactor` (14 nov 2026), sobre las enmiendas E1 (13 nov, 17:29) y E2 (14 nov, 09:08) de
    David al plan de BE-34
  - **Ubicación en el repo:** `docs/adr/0016-correo-en-minusculas.md`
  - **Origen:** backlog BE-51 (residual R2 del plan de BE-34); `docs/deuda/BE-34/plan.md`, fases F y G. Relación: ADR-0002
    (la invariante vive también en la base), ADR-0010 (punto 7: `alembic check`), ADR-0009 (no es un addendum de ADR-0015:
    alcanza el registro y el login de todos los usuarios), backlog A9 (lo guardado se devuelve tal cual) y D5 (validadores
    repetidos).

  ## Contexto

  `EmailStr` solo pasa a minúsculas el dominio: `Root@Test.COM` llega como `Root@test.com` a `UserCreate`, `UserLogin` y
  `UserUpdate`. Las tres consultas por correo de `UserRepository` comparan exacto, y el índice único `ix_users_email`
  también. Medido el 13 nov sobre una copia con las fases A–E de BE-34: un segundo registro con `root@test.com` junto a
  `Root@test.com` da 201 y deja dos cuentas; la provisión y el bootstrap también crean la segunda; el login con
  `root@test.com` da 401; un `PATCH` a `ROOT@test.com` da 200; un enlace de verificación con `root@test.com` da 404.

  Datos reales: 0 correos con alguna mayúscula y 0 colisiones en `develop`, `staging` y `main` (David, 13 nov, 17:40). David
  declaró la API apagada el 14 nov: es la ventana de mantenimiento en la que entra este cambio.

  ## Decisión

  1. **Un correo es una sola cuenta y se guarda en una sola forma: minúsculas, parte local y dominio.** Vale para el
     registro, la provisión, el bootstrap, el login, la verificación de correo y el cambio de correo por `PATCH`.
  2. **Se normaliza al entrar, en un solo punto:** el tipo `LowercaseEmail` (`Annotated[EmailStr, AfterValidator(str.lower)]`,
     en `app/schemas/user.py`), que usan `UserBase`, `UserLogin` y `UserUpdate`. El servicio recibe el correo ya en
     minúsculas, y las consultas de `UserRepository` siguen comparando exacto.
  3. **La base lo exige:** `CHECK (email = lower(email))`, con nombre `ck_users_email_lowercase`, declarada en el modelo
     `User` y creada por la migración `b51f3c9e2a64`. Un correo con mayúsculas escrito por una vía que no pase por un schema
     lo rechaza la base (ADR-0002).
  4. **La unicidad la sigue dando `ix_users_email`.** No hay índice nuevo.
  5. **Sin migración de datos.** Precondición de cada despliegue que lleve `b51f3c9e2a64`: 0 correos con mayúsculas en esa
     base (`SELECT count(*) FROM users WHERE email <> lower(email);`). Si una fila tiene mayúsculas, PostgreSQL se niega a
     crear la restricción, la migración se detiene sin cambiar nada y el CD no despliega la imagen.
  6. **Los tokens comparan exacto.** La app firma el correo guardado, que ya está en minúsculas; un token con otra grafía
     no encuentra cuenta. Los tokens emitidos antes del cambio siguen valiendo, porque ningún correo guardado tenía
     mayúsculas.

  ## Consecuencias

  - `UserResponse` devuelve la forma en minúsculas, y el correo de verificación va a esa forma, no a la que escribió el
    usuario. La guía de OWASP sobre correos dice que la parte local es "technically case-sensitive under SMTP, though many
    providers do not enforce this in practice": un buzón que dependiera de las mayúsculas no recibiría ese correo. Se acepta.
  - La misma guía desaconseja plegar la parte local por defecto y lo admite solo cuando el sistema controla ese
    comportamiento y no crea riesgo de colisión ni de cuenta equivocada. Aquí se pliega siempre: segunda desviación, aceptada.
  - `lower()` de SQLite solo pliega ASCII; el de PostgreSQL y `str.lower()` de Python pliegan también el resto de Unicode.
    `EmailStr` admite una parte local no ASCII, y `LowercaseEmail` la pliega en Python, así que por un schema no llega
    ninguna mayúscula. Lo que la suite no ve: en SQLite, la restricción acepta `Ángel@x.com` escrito sin schema; PostgreSQL
    lo rechaza.
  - `alembic check` no compara restricciones `CHECK` (Alembic las lista entre lo que autogenerate aún no detecta; medido:
    `compare_metadata` da `[]` con la restricción ausente de la base). Su presencia en PostgreSQL se comprueba en
    `pg_constraint`.
  - La migración usa `batch_alter_table`: en PostgreSQL emite un `ALTER TABLE … ADD CONSTRAINT`; en SQLite, que no puede
    añadir una restricción a una tabla existente, reconstruye la tabla. Así la suite la ejecuta.
  - Toda vía nueva que escriba un correo usa `LowercaseEmail`; si no, la base la rechaza.

  ## Alternativas consideradas

  1. **Comparar `lower(email)` en las consultas, con un índice único sobre `lower(email)`, sin normalizar lo guardado**
     (propuesta del 13 nov, no aprobada en E2). Guarda grafías distintas del mismo correo y deja la forma del dato sin
     fijar: cada consulta nueva tendría que recordar comparar sin mayúsculas. David prefiere una sola forma en la base.
  2. **Normalizar en los schemas, sin restricción en la base.** La regla dependería solo del código: una escritura que no
     pase por un schema guardaría mayúsculas sin que nada lo impida.
  3. **Guardar el correo como se escribió y, aparte, su forma canónica** (lo que recomienda la guía de OWASP: "Store both:
     Original input (for display and communication); Canonical form (for comparison according to your policy)"). Una
     columna más, sincronizada en cada escritura, para una forma original que hoy nada usa. Se aparta de la guía a
     sabiendas; si un día hace falta, es un cambio de esquema aparte.
  4. **Tipo `citext` de PostgreSQL.** Exige la extensión en las tres bases de Azure y no existe en SQLite, así que la suite
     dejaría de probar la invariante.
  5. **Migración de datos que pase a minúsculas lo guardado.** No hace falta: ningún correo guardado tiene mayúsculas.
  6. **No hacer nada.** Una persona podría tener dos cuentas, y escribir su correo con otras mayúsculas le impediría entrar.

  ## Evidencia

  - Sondas del plan (14 nov; pydantic 2.12.5, email-validator 2.3.0, SQLAlchemy 2.0.48, Alembic 1.18.4): `LowercaseEmail`
    da `root@test.com` para `rOOT@Test.com` y `ángel@test.com` para `ÁNGEL@Test.com`; en SQLite, `lower('ÁNGEL@x.com')` da
    `Ángel@x.com`; la migración sube, baja y se detiene con una fila en mayúsculas.
  - SQL fuera de línea para PostgreSQL: `ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email =
    lower(email));` entre `BEGIN;` y `COMMIT;`.
  - Sesión Mentor (14 nov), sobre una réplica mínima de `users` en PostgreSQL 16.15: un correo con mayúsculas da
    `CheckViolation`; un segundo correo igual, `UniqueViolation`; crear la restricción con una fila en mayúsculas ya
    guardada da `CheckViolation` y deja 0 restricciones.
  - Copia con las fases A–G: de 675 a 691 tests y de 97,37 % a 97,63 %. Ocho mutantes, los ocho muertos.
  - Documentación: OWASP (Email Validation and Verification Cheat Sheet), pydantic (`AfterValidator`), SQLAlchemy
    (`CheckConstraint`) y Alembic (modo batch, autogenerate), enlaces en `docs/deuda/BE-34/plan.md`, sección Referencias.
  ```
- **Tests (RED primero):** no aplica (documento). `check_docs` no lee `docs/adr` (`scripts/check_docs.py:157`). Medido:
  la compuerta, con el ADR sobre la copia con A–E, da la fila F.
- **Criterio de aceptación:** compuerta como la fila F. `git show --numstat --format= <sha F>` da
  `87	0	docs/adr/0016-correo-en-minusculas.md`. La línea "Estado" lleva una fecha real, no `<FECHA>`.
- **Fuera de alcance:** el código (fase G), ADR-0015 (no se edita), `AGENTS.md`, `docs/CONTEXT.md` y la fila BE-51 (cierre
  de la sesión Mentor).
- **Commit:**
  ```
  docs(adr): add ADR-0016, every email is stored in lowercase

  EmailStr lowers only the domain, and every lookup and the unique
  index compare emails exactly, so Root@test.com and root@test.com
  can be two accounts and a user who types another case cannot sign
  in (BE-51). David chose to close it inside BE-34 (amendments E1
  and E2).

  The ADR records how before the code that cites it lands: one
  lowercasing type for the three schemas that take an email, a CHECK
  constraint so the database refuses any other spelling, the existing
  unique index for uniqueness, and no data migration, because no
  stored email has an uppercase letter. It states where it departs
  from the OWASP email cheat sheet (only the lowercase form is stored)
  and lists the rejected paths: lower() in queries with a functional
  index, lowercasing without a CHECK, storing both forms, citext, a
  data migration, and nothing.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase G — Correo en minúsculas al entrar, restricción `CHECK` y su migración

- **Archivos (5):** `app/schemas/user.py`, `app/models/user.py`,
  `alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py` (nuevo), `tests/test_user_response.py`,
  `tests/test_email_case.py` (nuevo). Dominio: usuarios. La exclusión de `app/schemas/`, `app/models/` y `alembic/` de la
  Regla de alcance deja de valer solo para esta fase (E1, punto 5; E2, punto 3.1).
- **Cambios exactos:**
  1. `app/schemas/user.py`:
     - Tras `from enum import Enum`, la línea `from typing import Annotated`.
     - `from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator` →
       `from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, field_validator`.
     - Entre la clase `UserRole` y `class UserBase(BaseModel):`, con dos líneas en blanco a cada lado:
       ```python
       # Every email enters lowercased, local part included (BE-51, ADR-0016). EmailStr lowers only
       # the domain; the database refuses any other spelling (CHECK ck_users_email_lowercase).
       LowercaseEmail = Annotated[EmailStr, AfterValidator(str.lower)]
       ```
     - En `UserBase`: `    email: EmailStr = Field(..., description="Correo electrónico debe ser válido")` →
       `    email: LowercaseEmail = Field(..., description="Correo electrónico debe ser válido")`.
     - En `UserLogin`: `    email: EmailStr` → `    email: LowercaseEmail`.
     - En `UserUpdate`: `    email: EmailStr | None = Field(None, description="Correo electrónico válido")` →
       `    email: LowercaseEmail | None = Field(None, description="Correo electrónico válido")`.
  2. `app/models/user.py`: `from sqlalchemy import DateTime, Enum, String` →
     `from sqlalchemy import CheckConstraint, DateTime, Enum, String`. Justo después de `    __tablename__ = "users"`, sin
     línea en blanco entre medias (la que ya sigue separa las columnas):
     ```python
         # Every stored email is lowercase (BE-51, ADR-0016): the schemas lower what comes in, and
         # the database refuses any other spelling, whatever path writes it.
         __table_args__ = (CheckConstraint("email = lower(email)", name="ck_users_email_lowercase"),)
     ```
  3. `alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py`, escrito a mano (el id y la fecha son los del
     plan, no los de `alembic revision`), con el estilo de la plantilla `script.py.mako` (`alembic/versions` está fuera
     de ruff y de mypy):
     ```python
     """users: every email stored in lowercase (BE-51)

     Revision ID: b51f3c9e2a64
     Revises: 2cc4b57c136c
     Create Date: 2026-11-14 10:00:00.000000

     """
     from typing import Sequence, Union

     from alembic import op


     # revision identifiers, used by Alembic.
     revision: str = 'b51f3c9e2a64'
     down_revision: Union[str, Sequence[str], None] = '2cc4b57c136c'
     branch_labels: Union[str, Sequence[str], None] = None
     depends_on: Union[str, Sequence[str], None] = None


     def upgrade() -> None:
         """Adds CHECK (email = lower(email)) to users: every stored email is lowercase (ADR-0016).

         No row is rewritten. If one already holds an uppercase letter, the database refuses the
         constraint and the migration stops without changing anything, so the CD does not deploy.
         batch_alter_table emits a plain ALTER TABLE on PostgreSQL and rebuilds the table on SQLite,
         which cannot add a constraint in place; the suite runs this function on SQLite.
         """
         with op.batch_alter_table('users') as batch_op:
             batch_op.create_check_constraint('ck_users_email_lowercase', 'email = lower(email)')


     def downgrade() -> None:
         """Drops the CHECK; ix_users_email still keeps each email unique."""
         with op.batch_alter_table('users') as batch_op:
             batch_op.drop_constraint('ck_users_email_lowercase', type_='check')
     ```
  4. `tests/test_user_response.py`: en el `parametrize` de `test_my_profile_returns_stored_values_verbatim`, borrar la
     línea `        ("email", "Ana@EXAMPLE.COM"),` y la línea `        "mixed_case_domain",`. Nada más cambia.
  5. `tests/test_email_case.py`:
     ```python
     """Tests for BE-51: every email is stored in lowercase, so one email is one account (ADR-0016).

     The schemas lower each email that comes in (LowercaseEmail), the CHECK ck_users_email_lowercase
     refuses an uppercase letter written by any other path, and the unique index ix_users_email keeps
     one account per email. One test per path that reads or writes an email (registration,
     provisioning, bootstrap, login, email verification and the change by PATCH), and the migration
     that adds the CHECK, run on a database of its own.
     """

     import runpy
     from collections.abc import Callable, Iterator
     from pathlib import Path
     from unittest.mock import ANY

     import jwt
     import pytest
     from alembic.migration import MigrationContext
     from alembic.operations import Operations
     from sqlalchemy import Connection, create_engine, func, inspect, select
     from sqlalchemy.exc import IntegrityError
     from sqlalchemy.orm import Session

     from app.core.config import get_settings
     from app.core.exceptions import AlreadyExistsError
     from app.core.security import create_verification_token, get_password_hash
     from app.db.database import Base
     from app.models.audit import AuditLog
     from app.models.user import User, UserRole
     from app.repositories.audit_repository import AuditRepository
     from app.repositories.user_repository import UserRepository
     from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserUpdate
     from app.schemas.user import UserRole as SchemaUserRole
     from app.services.audit_service import AuditService
     from app.services.superadmin_bootstrap import bootstrap_superadmin

     PASSWORD = "Password123"
     STORED = "root@test.com"
     TYPED = "rOOT@Test.com"
     CHECK_NAME = "ck_users_email_lowercase"

     REGISTRATION = {
         "cedula": "1005911792",
         "email": TYPED,
         "first_name": "Juan",
         "last_name": "Perez",
         "password": PASSWORD,
         "data_consent": True,
     }

     MIGRATION = (
         Path(__file__).resolve().parents[1]
         / "alembic"
         / "versions"
         / "b51f3c9e2a64_users_email_stored_in_lowercase.py"
     )


     async def _emails(db_session) -> list[str]:
         return list(await db_session.scalars(select(User.email).order_by(User.id)))


     def _migrate(connection: Connection, step: str) -> None:
         """Runs upgrade() or downgrade() of the BE-51 migration, with its own op, on this connection."""
         migration = runpy.run_path(str(MIGRATION))
         with Operations.context(MigrationContext.configure(connection)):
             migration[step]()


     def _checks(connection: Connection) -> list[str | None]:
         return [check["name"] for check in inspect(connection).get_check_constraints("users")]


     def _add(connection: Connection, user: User) -> None:
         with Session(connection) as session:
             session.add(user)
             session.commit()


     @pytest.fixture
     def pre_migration_db() -> Iterator[Connection]:
         """A SQLite database of its own, on the schema before b51f3c9e2a64 (its downgrade applied).

         The suite's shared database is left alone: on SQLite a failed batch leaves its temporary
         table behind, and the next test would find it.
         """
         engine = create_engine("sqlite://")
         with engine.connect() as connection:
             Base.metadata.create_all(connection)
             _migrate(connection, "downgrade")
             connection.commit()
             yield connection
         engine.dispose()


     @pytest.mark.parametrize(
         "build",
         [
             lambda: UserCreate(**REGISTRATION),
             lambda: UserLogin(email=TYPED, password=PASSWORD),
             lambda: UserUpdate(email=TYPED),
         ],
         ids=["UserBase", "UserLogin", "UserUpdate"],
     )
     def test_every_email_input_arrives_lowercased(
         build: Callable[[], UserCreate | UserLogin | UserUpdate],
     ) -> None:
         """Happy path: the three schemas that take an email hand it over lowercased, local part too."""
         assert build().email == STORED


     def test_a_non_ascii_local_part_is_lowercased_too() -> None:
         """Edge case: EmailStr admits a non-ASCII local part, and Python lowers it as Unicode."""
         assert UserLogin(email="ÁNGEL@Test.com", password=PASSWORD).email == "ángel@test.com"


     def test_a_patch_with_a_null_email_keeps_it_null() -> None:
         """Edge case: the optional email of UserUpdate accepts None and does not lower it."""
         update = UserUpdate(email=None, phone="3001234567")

         assert update.email is None
         assert update.model_dump(exclude_unset=True) == {"email": None, "phone": "3001234567"}


     async def test_registration_stores_the_email_in_lowercase(client, db_session, mock_send_email):
         """Happy path: 201; the row, the response and the verification email carry it lowercased."""
         response = await client.post("/usuarios/registro", json=REGISTRATION)

         assert response.status_code == 201
         assert response.json()["email"] == STORED
         assert await _emails(db_session) == [STORED]
         mock_send_email.assert_called_once_with(
             email_to=STORED, first_name="Juan", token=ANY, base_url=ANY
         )


     async def test_registration_rejects_an_email_taken_in_another_case(
         client, db_session, persist_user, mock_send_email
     ):
         """Unhappy path: 400, no second row and no verification email."""
         await persist_user(email=STORED)

         response = await client.post("/usuarios/registro", json=REGISTRATION)

         assert response.status_code == 400
         assert set(response.json()) == {"detail"}
         assert await _emails(db_session) == [STORED]
         mock_send_email.assert_not_called()


     async def test_provisioning_rejects_an_email_taken_in_another_case(
         client, db_session, persist_user, make_auth_headers
     ):
         """Unhappy path: a superadmin cannot provision a second account for the same email."""
         superadmin = await persist_user(role=UserRole.superadmin)
         await persist_user(email=STORED)
         payload = {**REGISTRATION, "cedula": "555555", "role": "admin", "is_active": True}

         response = await client.post(
             "/usuarios/admin", json=payload, headers=make_auth_headers(superadmin)
         )

         assert response.status_code == 400
         assert set(response.json()) == {"detail"}
         assert await _emails(db_session) == [superadmin.email, STORED]


     async def test_bootstrap_rejects_an_email_taken_in_another_case(db_session, persist_user):
         """Unhappy path: SUPERADMIN_EMAIL in another case stops the bootstrap; nothing is written."""
         await persist_user(email=STORED)
         credentials = UserCreateByAdmin(
             **{**REGISTRATION, "cedula": "900000001"}, role=SchemaUserRole.superadmin, is_active=True
         )

         with pytest.raises(AlreadyExistsError):
             await bootstrap_superadmin(
                 credentials, UserRepository(db_session), AuditService(AuditRepository(db_session))
             )

         assert await _emails(db_session) == [STORED]
         assert await db_session.scalar(select(func.count()).select_from(AuditLog)) == 0


     async def test_login_accepts_the_email_typed_in_another_case(client, persist_user):
         """Happy path: 200, and the token carries the stored, lowercase email."""
         user = await persist_user(email=STORED, password_hash=get_password_hash(PASSWORD))

         response = await client.post("/usuarios/login", json={"email": TYPED, "password": PASSWORD})

         assert response.status_code == 200
         settings = get_settings()
         claims = jwt.decode(
             response.json()["access_token"], settings.jwt_secret_key, algorithms=[settings.algorithm]
         )
         assert claims["sub"] == user.email == STORED


     async def test_verification_token_in_another_case_is_rejected(client, db_session, persist_user):
         """Edge case: the app signs only the stored email, so a subject in another case finds none."""
         user = await persist_user(email=STORED, is_active=False)
         token = create_verification_token(TYPED)

         response = await client.get(f"/usuarios/verificar-email?token={token}")

         assert response.status_code == 404
         assert set(response.json()) == {"detail"}
         await db_session.refresh(user)
         assert user.is_active is False


     async def test_patch_stores_a_new_email_in_lowercase(
         client, db_session, persist_user, make_auth_headers
     ):
         """Happy path: 200; the response and the row carry the new email lowercased."""
         user = await persist_user()

         response = await client.patch(
             f"/usuarios/{user.cedula}", json={"email": TYPED}, headers=make_auth_headers(user)
         )

         assert response.status_code == 200
         assert response.json()["email"] == STORED
         await db_session.refresh(user)
         assert user.email == STORED


     async def test_patch_cannot_take_an_email_in_another_case(
         client, db_session, persist_user, make_auth_headers
     ):
         """Unhappy path: 409 from the unique index ix_users_email; the target keeps its email."""
         admin = await persist_user(role=UserRole.admin)
         await persist_user(email=STORED)
         tourist = await persist_user()
         original_email = tourist.email

         response = await client.patch(
             f"/usuarios/{tourist.cedula}", json={"email": TYPED}, headers=make_auth_headers(admin)
         )

         assert response.status_code == 409
         assert set(response.json()) == {"detail"}
         await db_session.refresh(tourist)
         assert tourist.email == original_email


     async def test_patch_changing_only_the_case_keeps_the_email(
         client, db_session, persist_user, make_auth_headers
     ):
         """Edge case: its own email in another case is the same value once lowercased."""
         user = await persist_user(email=STORED)

         response = await client.patch(
             f"/usuarios/{user.cedula}", json={"email": TYPED}, headers=make_auth_headers(user)
         )

         assert response.status_code == 200
         assert response.json()["email"] == STORED
         await db_session.refresh(user)
         assert user.email == STORED


     async def test_database_rejects_an_email_with_an_uppercase_letter(db_session, make_user):
         """Unhappy path: a row written without a schema still meets the CHECK (ADR-0002)."""
         db_session.add(make_user(email="Root@test.com"))

         with pytest.raises(IntegrityError, match=CHECK_NAME):
             await db_session.commit()

         await db_session.rollback()
         assert await _emails(db_session) == []


     def test_migration_adds_the_check_and_its_downgrade_drops_it(pre_migration_db, make_user):
         """Happy path: upgrade keeps rows and unique indexes and adds the CHECK; downgrade drops it."""
         _add(pre_migration_db, make_user(email=STORED))
         assert _checks(pre_migration_db) == []

         _migrate(pre_migration_db, "upgrade")

         assert _checks(pre_migration_db) == [CHECK_NAME]
         assert list(pre_migration_db.scalars(select(User.email))) == [STORED]
         indexes = inspect(pre_migration_db).get_indexes("users")
         assert {index["name"] for index in indexes if index["unique"]} == {
             "ix_users_cedula",
             "ix_users_email",
         }
         _migrate(pre_migration_db, "downgrade")
         assert _checks(pre_migration_db) == []


     def test_migration_stops_on_an_email_with_an_uppercase_letter(pre_migration_db, make_user):
         """Unhappy path: one uppercase row stops the upgrade; row and table stay as they were."""
         _add(pre_migration_db, make_user(email="Juan@test.com"))

         with pytest.raises(IntegrityError, match=CHECK_NAME):
             _migrate(pre_migration_db, "upgrade")

         pre_migration_db.rollback()
         assert _checks(pre_migration_db) == []
         assert list(pre_migration_db.scalars(select(User.email))) == ["Juan@test.com"]
     ```
- **Tests (RED primero):**
  1. Primero los tests (pasos 4 y 5) y luego
     `./venv/Scripts/python.exe -m pytest tests/test_email_case.py tests/test_user_response.py -q -p no:cacheprovider -rf --tb=no`.
     Medido: `13 failed, 15 passed, 2 warnings, 2 errors`. Los 2 errores son los tests de la migración: su archivo aún no
     existe. Pasan los 13 de `test_user_response.py`, `test_a_patch_with_a_null_email_keeps_it_null` y
     `test_verification_token_in_another_case_is_rejected`; estos dos fijan comportamiento que G no cambia.
  2. Después los schemas (paso 1). Medido: `1 failed, 27 passed, 2 warnings, 2 errors`. Solo falta
     `test_database_rejects_an_email_with_an_uppercase_letter`.
  3. Al final, el modelo y la migración (pasos 2 y 3): `30 passed, 2 warnings`. Mutantes MG1 a MG8 con los resultados de
     la tabla.
  Por qué cada truco del test:
  - Variante `rOOT@Test.com`: cambia la parte local, que `EmailStr` deja como llega; el dominio ya lo pliega `EmailStr`.
  - `pre_migration_db`: un SQLite propio, creado con el modelo y llevado al esquema previo con el `downgrade()` de la
    propia migración. Así el fallo de `upgrade()` no deja `_alembic_tmp_users` en la base compartida.
  - `Operations.context(MigrationContext.configure(connection))`: ejecuta `upgrade()` y `downgrade()` del archivo real,
    con su `op`, sobre la conexión del test.
  - `match=CHECK_NAME`: distingue el rechazo de la restricción del de `ix_users_email`, que también es `IntegrityError`.
  - `_add` usa `make_user` y una `Session` sobre la conexión propia (AGENTS §5: nada de usuarios a mano).
- **Criterio de aceptación:** compuerta como la fila G. `git show --numstat --format= <sha G>` da
  `35	0	alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py`, `4	1	app/models/user.py`,
  `10	4	app/schemas/user.py`, `299	0	tests/test_email_case.py` y `0	2	tests/test_user_response.py`. Pasos 10 a 18 de la
  Verificación final con su salida esperada. El paso 19 es de David, antes de `/pr`.
- **Fuera de alcance:** `app/repositories/` (las consultas siguen comparando exacto); `app/services/` (reciben el correo
  ya en minúsculas); `ix_users_email` (se queda, E2, punto 5); `tests/test_models_schema.py` (congela columnas, y las
  columnas no cambian); `tests/test_user_repository.py` y los demás archivos de A–E; los datos de las tres bases; el texto
  del handler de `IntegrityError`; el `PATCH` que no comprueba el correo antes de guardar (R11); la longitud del correo
  (R13).
- **Commit:**
  ```
  fix(users): store every email in lowercase, enforced by the database

  Registration, provisioning, the bootstrap, login and the email change
  by PATCH kept the local part as typed, and every lookup compared it
  exactly, so Root@test.com and root@test.com could be two accounts and
  a user who typed another case could not sign in (BE-51, ADR-0016).

  - app/schemas/user.py: LowercaseEmail, EmailStr followed by
    str.lower, is the email type of UserBase, UserLogin and UserUpdate:
    one type, not three validators.
  - app/models/user.py and migration b51f3c9e2a64: CHECK (email =
    lower(email)) named ck_users_email_lowercase, so a write that skips
    the schemas is refused. batch_alter_table emits a plain ALTER TABLE
    on PostgreSQL and lets the suite run the migration on SQLite.
  - Lookups still compare exactly, and ix_users_email still keeps one
    account per email: what comes in and what is stored are lowercase.
  - No row is rewritten: no stored email has an uppercase letter. If
    one does, the migration stops and changes nothing.
  - tests: the six paths with a case variant, the database refusing an
    uppercase email, and the migration upgrading, downgrading and
    stopping. The A9 case that stored Ana@EXAMPLE.COM goes: the
    database can no longer hold it.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase E. Los conteos incluyen el texto que dicta este plan (docstrings, comentarios de
`.env.example`, nombres de tests).

```bash
# 1. Patrón 1 de la verificación: sigue en 0 (el nombre es "bootstrap", que mide el patrón 2) → exit 1
git grep -n -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts

# 2. Patrón 2 por archivo → exactamente estas 8 líneas (109 coincidencias en total):
#    .env.example:6 · app/cli/bootstrap_superadmin.py:19 · app/core/config.py:12 · app/repositories/user_repository.py:1
#    app/services/superadmin_bootstrap.py:3 · tests/test_bootstrap_superadmin_command.py:16 · tests/test_config.py:41
#    tests/test_superadmin_bootstrap.py:11
git grep -c -i -E 'bootstrap|first_superadmin|initial_admin|superadmin_(email|password|cedula|first_name|last_name)' -- app alembic scripts tests conftest.py .env.example Dockerfile docker-compose.yml .azure-pipelines

# 3. Patrón 3 → 4 líneas: user_service.py:88 (turista), :412 (bajo guard), superadmin_bootstrap.py y bootstrap_superadmin.py
#    (ambas role=UserRole.superadmin)
git grep -n -E 'role=(UserRole\.|user_data\.role)' -- app

# 4. Patrón 4 → las mismas 4 líneas de la base (dependencies.py:199, routers/user.py:35, user_access_policy.py:67, :72)
git grep -n -E '"role" in update_dict|get_current_superadmin_user\)' -- app

# 5. Patrón 5 (BE-47) → 1 línea, en tests/test_config.py
git grep -n 'TEST_ENVIRONMENT' -- tests

# 6. Lo que no se toca → salida vacía
git diff --stat 4f10660 -- app/api app/main.py app/db app/models app/schemas app/services/user_service.py app/services/user_access_policy.py alembic scripts conftest.py tests/conftest.py tests/test_route_guards.py Dockerfile docker-compose.yml .azure-pipelines

# 7. Lo que sí → exactamente 12 archivos
git diff --name-only 4f10660 -- app tests pyproject.toml .env.example docs/adr

# 8. Settings sigue en 15 campos; la clase nueva tiene 6 → "15 6"
./venv/Scripts/python.exe -c "from app.core.config import Settings as S, SuperadminBootstrapSettings as B; print(len(S.model_fields), len(B.model_fields))"

# 9. Compuerta → exit 0; 675 passed, 8 warnings; TOTAL 1031 stmts, 97.37 %; 67 files; 62 source files; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

Tras la fase G (E1, E2), desde la raíz. Los pasos 1 a 9 valen tras E. Tras G cambian el 2 (ver el 17), el 6 (lista
`app/models/user.py`, `app/schemas/user.py` y la migración `b51f3c9e2a64`), el 7 (17 archivos: los 12 de A–E, ADR-0016
y cuatro de G; la migración está en `alembic/`, fuera de ese pathspec) y el 9 (ver el 18). Los conteos incluyen el texto
que dicta este plan (comentarios, docstrings y nombres de tests).

```bash
# 10. Ningún resto del mecanismo del 13 nov ni comparación sin mayúsculas → exit 1
git grep -n -E 'func\.lower|_same_email|ix_users_email_lower|ilike|casefold' -- app alembic tests

# 11. Las consultas siguen comparando exacto → 3 líneas: app/repositories/user_repository.py:18, :44 y :56
git grep -n 'User\.email ==' -- app

# 12. Un solo punto de normalización → 4 líneas, todas en app/schemas/user.py: :22 (la definición), :39 (UserBase),
#     :134 (UserLogin) y :166 (UserUpdate)
git grep -n 'LowercaseEmail' -- app

# 13. Nombre de la restricción → alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py:2 ·
#     app/models/user.py:1 · app/schemas/user.py:1 · tests/test_email_case.py:2
git grep -c 'ck_users_email_lowercase' -- app alembic tests

# 14. Una sola cabeza de Alembic → "b51f3c9e2a64 (head)"
DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db ./venv/Scripts/python.exe -m alembic heads

# 15. SQL de PostgreSQL sin base → contiene
#     "ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email));"
DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db ./venv/Scripts/python.exe -m alembic upgrade 2cc4b57c136c:b51f3c9e2a64 --sql

# 16. Archivos de F y G → exactamente 6 (el ADR, los 2 nuevos de G y los 3 que G edita)
git diff --name-only <sha E> -- app tests alembic docs/adr

# 17. Patrón 2 de BE-34 tras G → 9 líneas (114 coincidencias): las 8 del paso 2 más tests/test_email_case.py:5
git grep -c -i -E 'bootstrap|first_superadmin|initial_admin|superadmin_(email|password|cedula|first_name|last_name)' -- app alembic scripts tests conftest.py .env.example Dockerfile docker-compose.yml .azure-pipelines

# 18. Compuerta → exit 0; 691 passed, 8 warnings; TOTAL 1034 stmts, 97.63 %; 68 files; 63 source files; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

Paso 19, **de David, antes de `/pr`** (E2, punto 3.8; ADR-0010, punto 7), contra su PostgreSQL local y con la salida
literal en la bitácora:

```bash
# 19a. → la salida incluye "Running upgrade 2cc4b57c136c -> b51f3c9e2a64"
DATABASE_URL=<PostgreSQL local> ./venv/Scripts/python.exe -m alembic upgrade head

# 19b. → "No new upgrade operations detected." No prueba la restricción: Alembic no compara CHECK
#      (medido: compare_metadata → [] con la restricción ausente)
DATABASE_URL=<PostgreSQL local> ./venv/Scripts/python.exe -m alembic check

# 19c. En su cliente SQL, sobre esa base → 1 fila: ck_users_email_lowercase · CHECK (((email)::text = lower((email)::text)))
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'ck_users_email_lowercase';
```

La forma de 19c es la que midió la sesión Mentor (PostgreSQL 16.15) con la expresión equivalente; aquí no se midió. Si la
base local tiene un correo con mayúsculas, 19a se detiene: es lo esperado, y Q1 dice cuál. Si 19b lista operaciones,
van a la bitácora y a Residuales; no se corrigen de paso.

## Residuales

| # | Hallazgo (evidencia) | Destino sugerido |
|---|---|---|
| R1 | AGENTS §3 describe solo el flujo Router → Servicio. `app.cli` es un segundo adaptador (ADR-0015). | Que David añada en AGENTS una línea "comandos de operador en `app/cli/`, ADR-0015", en un PR propio (AGENTS no lo edita un agente). |
| R2 | La parte local del correo conservaba mayúsculas. Sonda: `UserCreate(email='Root@Test.COM').email` → `'Root@test.com'`. La unicidad y las tres consultas por correo comparan exacto, así que `Root@test.com` y `root@test.com` son dos cuentas, también en el registro de turistas. No es escalada: el bootstrap crea una fila nueva. | **Se salda en este ítem (E1, E2):** fila BE-51 (`Entra · B-GHOST-ADMIN`), fases F y G, con el mecanismo de E2. |
| R3 | No existe cambio de contraseña (adenda): la del superadmin es definitiva. BE-11 solo cubre la recuperación (Sale). | Fila nueva de feature (cambio de contraseña autenticado), si David la quiere. |
| R4 | El manual técnico debe recoger el comando (adenda, punto 2). | Bloque del manual `(PLAN §2b)`, sesión Mentor. |
| R5 | `docs/CONTEXT.md` no menciona ADR-0015 ni `app/cli/`. | Cierre del ítem, sesión Mentor. |
| R6 | BE-35 ("siempre queda al menos un superadmin activo") puede reutilizar `UserRepository.count_active_superadmins`. | Nota en la fila BE-35. |
| R7 | import-linter no prohíbe `fastapi`/`starlette` en `app.cli`: el contrato de capas solo fija la dirección. | Opcional; sin fila salvo que David lo pida. |
| R9 | E0.3 cambió la cifra que ADR-0015 cita (674 → 675 tests). La fase B no está commiteada, así que se corrigió esa cifra en su texto dictado, como prevé E0.3; nada más de B cambia. | Si David prefiere B intacta, se devuelve la cifra a 674 y este residual pasa al PR. |
| R10 | **Retirado por E2 (punto 5).** `ix_users_email` no es redundante: es el índice que sostiene la unicidad. | — |
| R11 | `update_user_account` no comprueba el correo antes de guardar (`user_service.py:285,297`): un `PATCH` con el correo de otra cuenta, escrito como sea, recibe el 409 genérico del handler de `IntegrityError` (`app/main.py:100-114`), no un `AlreadyExistsError`. Ya pasaba antes de G. Tras G lo fija `test_patch_cannot_take_an_email_in_another_case`, el primer test que pasa por ese handler (medido: `app/main.py:106` deja de faltar en la cobertura). | Sin fila salvo que David la pida. |
| R12 | Lo que queda sin ejecutar en PostgreSQL (BE-31). La suite y las sondas del planificador corren sobre SQLite; la migración de G solo se vio aquí como SQL fuera de línea. La sesión Mentor ejecutó la restricción en un PostgreSQL 16.15 propio (réplica mínima, psycopg2), y el paso 19 la ejecuta en el PostgreSQL local de David; ninguno es una base de Azure. Lo que SQLite no deja ver: su `lower()` solo pliega ASCII (`Ángel@x.com` pasa la restricción en SQLite y no en PostgreSQL; por los schemas no llega, porque Python pliega Unicode), y un `batch` fallido deja `_alembic_tmp_users` (en PostgreSQL es un solo `ALTER TABLE`). `alembic check` no compara `CHECK`. Si `str.lower()` y el `lower()` de una base de Azure difirieran en algún carácter Unicode, esa base rechazaría el correo con 409; no medido. | Declararlo en el PR. La primera ejecución en Azure es el CD de `develop`, con Q1 = 0. |
| R13 | `EmailStr` admite correos más largos que la columna: uno de 196 caracteres pasa `UserLogin` (sonda), y `users.email` es `String(150)` (`app/models/user.py:39`). SQLite no aplica la longitud, así que la suite no lo ve. En PostgreSQL el `INSERT` fallaría con un error de datos que no es `IntegrityError`, y ningún handler lo traduce (leído, no ejecutado). Previo a BE-51. | Fila Baja nueva si David la quiere (`max_length` en `LowercaseEmail` o en la columna). Fuera de BE-34. |

## Referencias

- pydantic-settings · 2.13.1 (instalada) · `SecretStr` en `BaseSettings`: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- pydantic · 2.12.5 · `ValidationError.errors(include_input=…, include_url=…)`: https://github.com/pydantic/pydantic/blob/v2.12.5/docs/errors/errors.md ;
  tipos secretos: https://docs.pydantic.dev/2.12/api/types/#pydantic.types.SecretStr
- SQLAlchemy · 2.0.48 · `create_async_engine`, `async_sessionmaker(expire_on_commit=False)`, `await engine.dispose()`
  en un script: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- import-linter · 2.15 · capas con hermanos independientes (`"a | b"`):
  https://github.com/seddonym/import-linter/blob/v2.15/docs/contract_types/layers.md
- Python · 3.14 · `runpy.run_path` / `runpy.run_module`: https://docs.python.org/3/library/runpy.html
- Python · 3.14 · `subprocess.run(env=…, cwd=…, timeout=…)` (E0.3): https://docs.python.org/3/library/subprocess.html#subprocess.run
- pydantic · 2.12.5 · validador reutilizable `Annotated[T, AfterValidator(f)]` (G, `LowercaseEmail`):
  https://github.com/pydantic/pydantic/blob/v2.12.5/docs/concepts/validators.md
- SQLAlchemy · 2.0.48 · `CheckConstraint` con nombre en `__table_args__` (G; medido:
  `CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email))` en PostgreSQL y en SQLite):
  https://docs.sqlalchemy.org/en/20/core/constraints.html#check-constraint
- Alembic · 1.18.4 · `batch_alter_table` y las restricciones `CHECK` con nombre ("Including CHECK constraints"):
  https://github.com/sqlalchemy/alembic/blob/rel_1_18_4/docs/build/batch.rst ; autogenerate no detecta `CHECK` ("can't
  currently, but will eventually detect"): https://github.com/sqlalchemy/alembic/blob/rel_1_18_4/docs/build/autogenerate.rst ;
  `Operations.context` y `MigrationContext.configure` fuera de `env.py` (tests de G):
  https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.migration.MigrationContext.configure
- OWASP Cheat Sheet Series · `master`, leída el 14 nov 2026 por Context7 · Email Validation and Verification Cheat Sheet,
  secciones "Case Sensitivity" y "Email Canonicalization" (ADR-0016):
  https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Email_Validation_and_Verification_Cheat_Sheet.md
- RFC 5321: no se leyó, así que ADR-0016 no lo cita (E2, punto 3.7).

## Enmiendas aprobadas

### E0 — 13 nov 2026, 17:26 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «si a todo. lo unico, es que R2 se resuelve de una vez. R3 si merece irse al futuro; es un feaure
de reestablecimiento de contraseñas que practicamente casi que por excelencia se espera en un mvp con login propio».

**Plan aprobado: fases A → B → C → D como están escritas; la fase E, con el añadido del punto 3.** Fecha de aprobación
para la línea "Estado" de ADR-0015 (fase B): **13 nov 2026**. Si un punto de arriba y E0 difieren, rige E0. Contraste de
la sesión Mentor contra el código, sin correcciones de dictado: existen las anclas que el plan usa
(`tests/test_config.py:9,47,49-55,58,64` y su última función; `app/core/config.py:12,73,76`; los imports de
`app/repositories/user_repository.py:1-7`); ningún bloque de Python dictado pasa de 100 columnas (medido); las cuentas
cuadran (638 → 639 → 650 → 667 → 674; 1 + 11 + 17 + 7 tests; 9 líneas en la fase A); `UserRole` existe en
`app/models/user.py:11`, `make_user` acepta `is_active` y `deleted_at` (`tests/conftest.py:183-188`) y
`[tool.setuptools.packages.find]` ya incluye `app*` (`pyproject.toml:50-52`). Las cifras de tests, cobertura y mutantes
las repite el auditor.

1. **ADR-0015 aceptado** con el texto que dicta la fase B.
2. **La marca `"source": "bootstrap"` en `changes` se acepta** (punto 5 de la adenda, propuesta del planificador).
3. **Añadido a la fase E: un test que ejecuta el comando en un proceso hijo sin los secretos de la web app.** Hueco medido
   por la sesión Mentor: el docstring de `SuperadminBootstrapSettings` y ADR-0015 afirman que el comando corre con
   `DATABASE_URL` y las cinco `SUPERADMIN_*` solas. Hoy es cierto por lectura: solo dos módulos construyen `Settings` al
   importarse (`app/core/email.py:36`, `app/main.py:194`) y el comando no importa ninguno (`app/core/security.py:74,104`
   lo llama dentro de funciones que el comando no usa). Pero los siete tests de la fase E llaman a `main()` dentro de
   la suite, cuyo entorno ya trae todos los secretos (`conftest.py` de la raíz): si un cambio futuro hiciera que el
   núcleo o el comando importaran un módulo que construye `Settings` al importarse (hoy `app.core.email`, que solo
   importa `app/api/routers/user.py:13`; o uno nuevo que llame a `get_settings()` a nivel de módulo), la suite seguiría
   en verde y el comando fallaría en el `docker run` real. `app.services.user_service` no es ese caso: llama a
   `get_settings()` dentro de una función (`:123`). Lo que se pide
   al planificador (invocado con mensaje directo, antes de `/implementar BE-34 E`; las fases A–D no cambian):
   - un test en `tests/test_bootstrap_superadmin_command.py` que lance `python -m app.cli.bootstrap_superadmin` con
     `subprocess` y el intérprete de la suite, sobre una base de archivo propia, con las seis variables del comando y
     con `JWT_SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD` y `AZURE_STORAGE_CONNECTION_STRING` **puestas a cadena
     vacía** en el entorno del hijo, y afirme código de salida 0 y un superadmin activo en la base. La cadena vacía es
     lo que lo hace determinista: el entorno del proceso gana al `.env` de quien corre la suite (ADR-0013, punto 3) y
     `Field(min_length=1)` hace fallar cualquier construcción de `Settings`. **Esto está razonado, no medido** (la VM de
     la sesión Mentor no puede ejecutar el venv): el planificador lo mide con sonda antes de dictar y, si el mecanismo no
     se comporta así, propone otro que vigile la misma propiedad y lo dice;
   - su mutante: un `import app.core.email` (o equivalente) en `app/services/superadmin_bootstrap.py` debe tumbar el
     test nuevo y solo ese (o los que el planificador mida);
   - recalcular lo que dependa: tabla de mutantes, fila E de la compuerta, `numstat` y conteos de la fase E, cuerpo del
     commit de E, Verificación final (pasos 2 y 9), la cifra del Resumen y la descripción de `Fase_E` en `progress.json`
     (sin tocar `current_target` ni las demás fases). El texto de ADR-0015 (fase B) cita "de 638 a 674 tests": si la
     fase B ya está commiteada cuando cambie la cifra, el ADR no se edita; el planificador lo declara en Residuales.
4. **R2 no es residual: David decide resolverlo ya** («R2 se resuelve de una vez»). Queda **fuera de las fases A–E**, que
   no tocan `app/schemas/` ni las consultas por correo. La forma (ítem propio en el mismo bloque, con su verificación, o
   fase nueva de este ítem) la confirma David; hasta entonces ningún ejecutor hace nada sobre R2. Dato de alcance medido
   por la sesión Mentor: tres entradas de correo (`app/schemas/user.py:33,128,160`), tres consultas con comparación
   exacta (`app/repositories/user_repository.py:17,23,35`), el índice único `ix_users_email`
   (`alembic/versions/a0f621304d75_*.py:51`) y los correos ya guardados en las tres bases.
5. **R3 (cambio de contraseña) recibe fila en `B-FUTURO`**, escrita por la sesión Mentor en el cierre. No lo cubre el
   derivado de BE-11 (recuperación por correo, `Sale`).
6. **Residual que añade la sesión Mentor, R8, sin arreglo:** si dos operadores corren el comando a la vez, el segundo
   recibe un `IntegrityError` no capturado cuyo texto incluye los parámetros del `INSERT` (correo, cédula y hash bcrypt,
   no la contraseña). Leído, no ejecutado. Se declara en el PR; `hide_parameters=True` en el motor del comando lo
   cerraría si David lo pide.
7. **Pendiente fuera del plan, de David, antes de `/pr`:** la línea de AGENTS §3 sobre `app/cli/` (R1), con texto de la
   sesión Mentor. R4, R5 y R6: cierre del ítem. R7: sin acción.

`progress.json` no cambia (`current_target: Fase_A`).

### E1 — 13 nov 2026, 17:29 (David, sesión Mentor; regla del retoque)

Texto literal de David: «pues mira, haremos esto: se resuelve en la fase H del plan y recie su item en el backlog y entra
aa este bloque. si de por si hoy el dia no nos va a alcanzar para mucho, pues que almenos los cabos sueltos que podamos
atar sin que deje de hacer sentido hacerlo, atemoslos».

**R2 se salda dentro de este ítem, como fase nueva, y recibe fila propia: BE-51, `Entra · B-GHOST-ADMIN`** (fila hija,
AGENTS §8: una carpeta, un PR). Confirma el punto 4 de E0. La fase se llama **F** (la letra que sigue a E; David dijo
"H"). La sesión Mentor recomendó ítem propio con su verificación, porque R2 toca el registro y el login de todos los
usuarios y la verificación de BE-34 no lo midió; David eligió la fase. **Por eso la fase F empieza midiendo:** el
planificador hace para R2 lo que habría hecho un verificador (grep global, sondas) antes de dictar nada.

Qué debe cumplir la fase F (el cómo lo propone y lo mide el planificador):

1. **Objetivo:** dos correos que solo difieren en mayúsculas no pueden ser dos cuentas, y una cuenta entra con su correo
   escrito con cualquier combinación de mayúsculas. Vale para el registro de turistas, la provisión de administradores,
   el bootstrap, el login, la verificación de correo y el cambio de correo por `PATCH`.
2. **Mapa mínimo que el planificador completa con grep global:** entradas de correo en `app/schemas/user.py:33` (`UserBase`),
   `:128` (`UserLogin`) y `:160` (`UserUpdate`); comparaciones exactas en `app/repositories/user_repository.py:17,23,35`;
   el correo que viaja en el token de verificación (`app/core/security.py`, `create_verification_token`); el índice único
   `ix_users_email` (`alembic/versions/a0f621304d75_*.py:51`); 0 usos de `lower()`/`ilike` sobre correos en `app/`
   (medido por la sesión Mentor).
3. **Condición que no se negocia: ninguna cuenta existente deja de poder entrar.** Si la solución normaliza a minúsculas
   en la entrada, una fila guardada como `Root@test.com` ya no coincidiría con lo que escribe su dueño: el plan dice
   cómo lo evita (migración de datos de Alembic con detección de colisiones, comparación insensible en las consultas con
   índice funcional, u otra) y por qué. Todo cambio de esquema o de datos va por Alembic (AGENTS §2).
4. **Datos reales que el planificador no puede ver:** cuántos correos con mayúsculas y cuántas colisiones hay en las
   bases de `develop`, `staging` y `main`. David corre dos consultas y pega el resultado antes de aprobar la fase
   (bitácora `2026-11-13`); el plan no las supone.
5. **Alcance y forma:** si no cabe en ≤ 5 archivos y un dominio, el planificador la parte (F, G) y lo dice; tests RED
   primero y mutantes, como las demás fases; si hay decisión no trivial, ADR o addendum. **La fase F no se ejecuta hasta
   que David la apruebe (E2).** Las fases A–E no cambian por E1; "No se toca `app/schemas/`" de la Regla de alcance deja
   de valer solo para la fase F.
6. **Si al medir resulta que no tiene sentido hacerlo aquí** (por ejemplo, colisiones reales en una base que exijan una
   decisión de producto), el planificador se detiene y lo dice; David lo previó en su texto ("sin que deje de hacer
   sentido").

`progress.json`: el planificador añade `Fase_F` (`pending`) cuando escriba la fase, sin tocar `current_target` ni las
fases existentes.

### Aplicación de E0.3 y E1 (plan-redactor, 13 nov 2026, por mensaje directo; las fases A–D no cambian)

- **E0.3, medido en una copia de A–E en el scratchpad.** El test nuevo es `test_command_runs_without_the_web_app_secrets`.
  Ejecuta `python -m app.cli.bootstrap_superadmin` con `subprocess`, `sys.executable` y `cwd=REPO_ROOT`, con las seis
  variables del comando y los cuatro secretos de `Settings` a `""`. El mecanismo razonado por la sesión Mentor se
  comporta como se razonó. Sobre E pasa (`8 passed` en el archivo). Con ME6 (`import app.core.email` en el núcleo) el hijo
  sale con 1, `4 validation errors for Settings` (`string_too_short`): `1 failed, 385 passed`, y solo cae él. Si el hijo
  hereda el entorno sin vaciar los secretos, ME6 sobrevive (`8 passed`), y por eso la cadena vacía es necesaria.
  Recalculado: filas ME1 a ME5 de la tabla de mutantes (la suite de la copia pasa de 385 a 386; ME3 tumba también el test
  nuevo: 3 failed), fila ME6, fila E de la compuerta (675 · 97,37 % · 1031 sin cambio: la cobertura no mide al hijo ·
  386), `numstat` del test (169 → 208), "Tests (RED primero)" y "Por qué" de E, cuerpo del commit de E, pasos 2 y 9 de
  la Verificación final, cifra del Resumen, la cifra de ADR-0015 en el texto de la fase B (R9) y la descripción de
  `Fase_E` en `progress.json`.
- **E1.** BE-51 se midió con grep global y sondas (sección de las fases F y G). Cabe en 5 archivos de código y un
  dominio, más el ADR, así que se parte en F (ADR-0016) y G (código). En `progress.json` entran `Fase_F` y `Fase_G`,
  `pending`, sin tocar `current_target` ni las fases existentes. Ocho mutantes, los ocho muertos.

### E2 — 14 nov 2026, 09:08 (David, sesión Mentor; regla del retoque)

Texto literal de David (09:04): «mmm, pero sabes que? no te parece que las fuentes de autoridad recomiendan mejor garantizar
que en la bd si o si un correo del tipo XcOrRReo@... se guarde como @xcorreo? o sea yo entiendo que por temas de que si
alguien se registrase en este momento seria un problema si lo hace con mayuculas, pero prefiero argumentar que se
estableció una ventana de mantenimiento segura bajo la cual, y tras verificar 0 correos en mayusculas, se estableció el
mecanismo que normaliza a minusculas cada correo, porque lo que propones permite entradas irregulares a la bd y el codigo
de la api es el que compararía con lower, pero desde la realidad práctica te digo que no hay necesidad de hacer eso porque
se que hay 0% de probabilidades que un usuario se geistre hoy dado que tengo apagada la api». Y (09:08): «ok 1.) va la
restricción check en la base. 2.) no. reescritura de F y G ya. 3. te aurotizp».

Responde a las siete "Decisiones pendientes de David (E2)". Si un punto de arriba y E2 difieren, rige E2.

1. **E0.3 aceptado como se midió:** el test `test_command_runs_without_the_web_app_secrets`, ME6 y las cifras
   recalculadas, incluida la cifra 675 en el texto dictado de ADR-0015 (fase B). **Las fases A → E quedan aprobadas tal
   como están escritas y no cambian por E2.**
2. **BE-51 sigue partido en dos fases, F (ADR-0016) y G (código).**
3. **Mecanismo: NO se aprueba el de la pasada del 13 nov** (comparar `lower(email)` con índice único funcional, sin
   normalizar lo guardado). **David decide: todo correo se guarda en minúsculas, y la base lo garantiza.** El planificador
   reescribe F y G con esto (el cómo lo propone y lo mide él; lo que sigue es lo que debe cumplir):
   1. **Normalización al entrar.** Todo correo que entra por un schema llega al servicio completo en minúsculas (parte
      local y dominio). Vale para las tres entradas: `app/schemas/user.py:33` (`UserBase`), `:128` (`UserLogin`) y `:160`
      (`UserUpdate`). Un solo punto de normalización que las tres reutilicen: no se añade otra copia de validador (el
      backlog ya tiene D5 por eso). Es el mismo trato que `format_title_case` da a los nombres (`app/schemas/user.py:64-74`).
      La exclusión de `app/schemas/` de la Regla de alcance deja de valer para la fase G.
   2. **Garantía en la base (decisión 1 de David, 09:08):** una restricción `CHECK (email = lower(email))` sobre `users`,
      con nombre explícito, declarada en el modelo `User` y creada por una migración de Alembic (AGENTS §2; ADR-0002: la
      invariante vive también en la base). Un correo con mayúsculas escrito por cualquier vía que no pase por el schema
      lo rechaza la base.
   3. **La unicidad la sostiene el índice que ya existe, `ix_users_email`.** No se crean `ix_users_email_lower` ni
      `_same_email`; las tres consultas de `app/repositories/user_repository.py` siguen comparando exacto, porque lo que
      llega y lo guardado ya están en minúsculas.
   4. **Sin migración de datos.** Precondición: Q1 (correos con alguna mayúscula) = 0 en la base, antes de cada
      despliegue que lleve la migración. Si una fila tiene mayúsculas, la migración se detiene sin cambiar nada y el CD
      no despliega. G no se ejecuta si Q1 deja de dar 0 en `develop`. David declara la API apagada hoy (ventana de
      mantenimiento); Q1 se repite antes de promover a `staging` y a `main`.
   5. **Tests (RED primero) y mutantes**, como las demás fases: las seis rutas que leen o escriben un correo (registro,
      provisión, bootstrap, login, verificación de correo, cambio por `PATCH`) con una variante en mayúsculas de la parte
      local; que lo guardado queda en minúsculas; que la base rechaza un correo con mayúsculas insertado sin pasar por
      el schema; y la migración (sube, baja, y se detiene con una fila en mayúsculas).
   6. **Lo que el planificador debe medir antes de dictar, y decir qué hace con ello:**
      - `tests/test_user_response.py:61` usa `Ana@EXAMPLE.COM` (A9: lo guardado se devuelve tal cual). Si ese test, u
        otro, guarda en la base un correo con mayúsculas, la restricción lo tumba. Grep global de correos con mayúsculas
        en `tests/` y `conftest.py`.
      - Un token de verificación cuyo `sub` difiere en mayúsculas de lo guardado: la app nunca lo emite (lleva el correo
        guardado). Decir si queda sin test o con uno que fije el rechazo.
      - Un `PATCH` que solo cambia mayúsculas del propio correo: tras normalizar es el mismo valor.
      - `lower()` de SQLite solo pliega ASCII; el de PostgreSQL y `str.lower()` de Python pliegan Unicode. Medido por la
        sesión Mentor el 14 nov: SQLite `lower('ÁNGEL@X.com')` → `Ángel@x.com`; PostgreSQL 16.15 y Python → `ángel@x.com`.
        La suite no ve esa diferencia en la restricción; se declara (junto a R12) o se cubre.
      - Si `EmailStr` admite parte local no ASCII, y qué devuelve.
   7. **ADR-0016 se reescribe** con esta decisión. En "Alternativas consideradas" entra la descartada el 14 nov
      (`lower(email)` en consultas e índice funcional) con su razón verdadera: guarda grafías distintas del mismo correo
      y deja la forma del dato sin fijar; David prefiere una sola forma en la base. La alternativa "normalizar sin
      restricción en la base" se descarta porque la regla dependería solo del código. El ADR recoge la ventana de
      mantenimiento (0 correos con mayúsculas en `develop`, `staging` y `main`, medido por David el 13 nov a las 17:40; API
      apagada el 14 nov). **Ninguna fuente externa se cita de memoria:** si el ADR cita OWASP o el RFC 5321, el
      planificador las lee antes y enlaza lo leído en Referencias.
   8. **ADR-0010, punto 7** (un cambio de modelos se prueba con `alembic check`): la Verificación final conserva el SQL
      fuera de línea para PostgreSQL y añade un paso **de David, antes de `/pr`**, contra su PostgreSQL local:
      `alembic upgrade head` y `alembic check`, con la salida literal en la bitácora. Si Alembic no compara restricciones
      `CHECK` en `autogenerate`, se declara.
   9. **Evidencia de la sesión Mentor (14 nov), con sus límites.** En un PostgreSQL 16.15 propio, con SQLAlchemy 2.0.48 y
      Alembic 1.18.4, sobre una réplica mínima de `users` (`id`, `cedula`, `email`; psycopg2, no asyncpg; no es una base
      de Azure): `CheckConstraint(email == func.lower(email), name=…)` en el modelo crea
      `CHECK (((email)::text = lower((email)::text)))`; `Root@test.com` → `CheckViolation`; un segundo `root@test.com` →
      `UniqueViolation`; `op.create_check_constraint` con una fila `Juan@test.com` ya guardada → `CheckViolation` y 0
      restricciones después; `compare_metadata` → `[]`. Script y salida en la bitácora `2026-11-14`. El nombre de la
      restricción y la forma exacta son del planificador; esto no sustituye sus mediciones ni las del auditor.
4. **Datos reales:** Q1 = 0 y Q2 = 0 filas en `develop`, `staging` y `main` (David, 13 nov, 17:40; bitácora `2026-11-13`).
   Con el mecanismo nuevo la consulta que decide es Q1 (punto 3.4).
5. **`ix_users_email` se queda** y deja de ser redundante: es el índice que sostiene la unicidad. R10 desaparece.
6. **Fecha de aceptación de ADR-0016:** la de la aprobación de las fases reescritas (E3). Si E3 se da hoy, 14 nov 2026.
7. **Límite de PostgreSQL (R12): aceptado, reducido** por el punto 3.8 (paso local de David antes de `/pr`) y el 3.9. El
   planificador reescribe R12 con lo que quede sin ejecutar en PostgreSQL.

**Qué recalcula el planificador** (invocado con mensaje directo, antes de `/implementar BE-34 A`, por decisión 2 de David
a las 09:08: «reescritura de F y G ya»): la sección "Fases F y G", la fase F y la fase G enteras; las filas MG de la tabla
de mutantes; las filas F y G de la tabla de la compuerta; la Regla de alcance (archivos de F y G); los pasos 10 a 18 de la
Verificación final; el párrafo de F y G del Resumen; los residuales R2, R10, R11 y R12; Referencias; los mensajes de
commit de F y G; y las descripciones de `Fase_F` y `Fase_G` en `progress.json`, sin tocar `current_target` ni las fases A–E.
Si al medir algo de las fases A–E resultara afectado, se detiene y lo dice. **Las fases F y G reescritas no se ejecutan
hasta que David las apruebe (E3).**

`progress.json`: sin cambios por E2 (`current_target: Fase_A`).

### Aplicación de E2 (plan-redactor, 14 nov 2026, por mensaje directo; las fases A–E no cambian)

- **Medido antes de dictar (E2, punto 3.6)**, sobre copias de `HEAD` (`8391e88`) con los 12 archivos de A–E; la compuerta
  de esa copia da la fila E exacta. Cada resultado, y qué se hace con él, está en la sección "Fases F y G". Lo que pesa:
  el único test que guarda un correo con mayúsculas es `mixed_case_domain` (G lo borra); un token con otra grafía da 404
  (G lo fija con un test); `alembic check` no compara `CHECK` (paso 19c); en SQLite un `batch` fallido deja
  `_alembic_tmp_users` (los tests de la migración usan un motor propio).
- **Fuente externa leída (E2, punto 3.7):** la guía de OWASP sobre correos, por Context7. No respalda del todo la
  premisa de David de las 09:04. Dice que la parte local es técnicamente sensible a mayúsculas, que solo se pliegue
  cuando el sistema controla ese comportamiento y no crea riesgo de colisión ni de cuenta equivocada, y que se guarden el
  original y la forma canónica. ADR-0016 cita lo leído y declara la desviación (decisión 2 de E3). El RFC 5321 no se leyó
  y no se cita.
- **Recalculado:** la sección "Fases F y G", las fases F y G enteras, las filas MG1 a MG8, las filas F y G de la
  compuerta, la Regla de alcance, los pasos 10 a 18 de la Verificación final (más el 19, de David), el párrafo de F y G
  del Resumen, R2, R10, R11 y R12 (más R13, nuevo), Referencias, los dos mensajes de commit y las descripciones de
  `Fase_F` y `Fase_G` en `progress.json` (`current_target` y las fases A–E, sin tocar).
- **Efecto sobre A–E: ninguno, medido.** G no toca ningún archivo de A–E. Los tests de C, D y E usan correos en
  minúsculas (`root@test.com`, `superadmin@example.com`), así que pasarlos a minúsculas no cambia ninguna aserción. La
  copia con A–G pasa entera sin tocar un test de A–E. Lo que ADR-0015 (fase B) afirma sigue siendo cierto. Las cifras de
  A–E no cambian.
- **Cifras nuevas:** de 675 a 691 tests (17 nuevos, 1 borrado); de 97,37 % a 97,63 % (de 1031 a 1034 stmts); de 386 a
  402 en la suite de la copia; ocho mutantes, los ocho muertos.

### E3 — 14 nov 2026, 10:54 (David, sesión Mentor; regla del retoque)

Texto literal de David: «Diosss. ok. por tiempo, esta bién. apruebo todo tal y como lo propones pero que nazca fila en el
backlog de trabajo futuro para revertir el plan o al mecanismo del 13 de noviembre; una app que busca ser usada por muchos
debería poder responder a cualquier buzonera, idependientemente si las buoneras son case sensitive o no (quisiera saber si
gmail, yahoo, y las principales buzoneras son o no case sensitive; si si, entonces aunque no es lo que quiero decido la c;
que tal que un jurado tengta un correo raro y preciso tenga problema?). 2. si, la consulta fue a las 9:20 con apicerrada,
todo sigue igual y fue sobre develop. 3.) si condicionado" a lo que te dije de revisar si las principales buzoneras con
case sensitive o no».

Responde a las siete "Decisiones pendientes de David (E3)". **Las fases F y G quedan aprobadas; con E0 y E2, el plan
entero (A → G) está aprobado.** Si un punto de arriba y E3 difieren, rige E3. Contraste de la sesión Mentor contra el
código, sin correcciones de dictado: las fases A–E son idénticas a las de `0fb8680` (comparadas como texto); las anclas de
G existen (`app/schemas/user.py:33,128,160` → `:39`, `:134`, `:166` con las 6 líneas que G añade antes; `LowercaseEmail`
en `:22`); los `numstat` de `app/schemas/user.py` (`10 4`) y `app/models/user.py` (`4 1`) cuadran contados a mano; las
tres consultas quedan en `user_repository.py:18`, `:44` y `:56` tras D; el caso que G borra existe
(`tests/test_user_response.py:61` y su id); el test del registro afirma los argumentos con que el router agenda el correo
(`app/api/routers/user.py:70-76`). Las cifras de tests, cobertura y mutantes las repite el auditor.

1. **F y G aprobadas como quedaron escritas, con el añadido del punto 2.** Fecha de aceptación para la línea "Estado" de
   ADR-0016 (fase F): **14 nov 2026**.
2. **Desviación de la guía de OWASP: opción (a), aceptarla y declararla**, con dos precisiones.
   - **Condición de David, comprobada.** David eligió (a) solo si los proveedores principales no distinguen mayúsculas en
     la parte local; si las distinguieran, elegía (c). La sesión Mentor lo buscó el 14 nov: las fuentes consultadas
     coinciden en que Gmail, Outlook, Yahoo e iCloud entregan al mismo buzón con cualquier combinación de mayúsculas.
     **Límite:** son fuentes secundarias (guías de proveedores de envío de correo), no la documentación de Google,
     Microsoft o Yahoo. La condición se da por cumplida con ese límite declarado.
     **Fuente primaria leída después, a petición de David (10:56):** la ayuda de Google Workspace, "Name guidelines for
     users & groups" (https://support.google.com/a/answer/9193374), dice que un nombre de usuario debe ir en minúsculas y
     que las mayúsculas escritas al crearlo se convierten a minúsculas. Vale para cuentas administradas de Google; para
     Gmail personal, Microsoft y Yahoo no se halló una página oficial que lo afirme (solo respuestas de foros).
   - **Las citas de OWASP del ADR, comprobadas por la sesión Mentor** abriendo la página de Referencias el 14 nov: existen
     y dicen lo que el ADR les atribuye.
   - **Añadido al texto dictado de ADR-0016 (ya aplicado en la fase F de este plan):** dos líneas en "Consecuencias", tras
     la viñeta que cita a OWASP, que declaran la segunda desviación (la guía desaconseja plegar la parte local por
     defecto). El texto dictado pasa de 85 a 87 líneas (contadas) y el criterio de aceptación de F, de `85 0` a `87 0`.
     Nada más de F cambia.
   - **Fila nueva, BE-53, `Sale → B-FUTURO`:** guardar el correo como lo escribió el usuario y comparar por su forma
     canónica (el mecanismo del 13 nov, o una columna para el original). El texto del mecanismo del 13 nov está en
     `git show 0fb8680:docs/deuda/BE-34/plan.md`, fases F y G.
3. **Token de verificación con otra grafía:** el test que fija el 404 se queda.
4. **El caso `mixed_case_domain` de A9 se borra.**
5. **La migración va en modo batch**, probada sobre un SQLite propio.
6. **Q1 del 14 nov, 09:20: fue sobre `develop`, con la API apagada** (palabra de David, 10:54); `count = 0`. La
   precondición de G se cumple. Se repite antes de promover a `staging` y a `main`.
7. **R13 recibe fila, BE-54, Baja, `Sale → B-FUTURO`**, fuera de BE-34.

`progress.json`: sin cambios por E3 (`current_target: Fase_A`).

## Decisiones pendientes de David (E2)

**Respondidas por David el 14 nov 2026 (09:08): ver E2, en "Enmiendas aprobadas".** La lista se conserva como se
escribió el 13 nov; la decisión 3 no se aprobó y las fases F y G se reescriben.

1. **E0.3 tal como se midió:** el test, ME6 y las cifras recalculadas. Incluye una sola cifra cambiada en el texto
   dictado de la fase B (ADR-0015: 674 → 675), porque B no está commiteada. ¿Se acepta, o B queda intacta con 674 y R9 va
   al PR?
2. **Partir BE-51 en dos fases, F (ADR-0016) y G (código),** en lugar de la única fase F de E1. Motivo: ≤ 5 archivos y un
   dominio por fase.
3. **Mecanismo:** comparar `lower(email)` en la base, con un índice único funcional, sin reescribir ningún correo
   guardado (ADR-0016), frente a pasar a minúsculas y reescribir las filas. ¿Se aprueba?
4. **Datos reales (E1, punto 4):** resultado de Q1 y Q2 en `develop`, `staging` y `main`. G solo se ejecuta si Q2 da 0
   filas en las tres; con una colisión, G se detiene (E1, punto 6).
5. **`ix_users_email` se queda**, aunque tras G sea redundante (R10). ¿Se queda, o quiere fila para retirarlo?
6. **Fecha de aceptación de ADR-0016** para su línea "Estado": la de E2.
7. **Límite aceptado o no:** la migración de G no se ejecuta en PostgreSQL antes del CD de `develop`; solo se ve su SQL
   fuera de línea (R12, BE-31).

## Decisiones pendientes de David (E3)

**Respondidas por David el 14 nov 2026 (10:54): ver E3, en "Enmiendas aprobadas".** La lista se conserva como la escribió
el planificador.

1. **Aprobar F y G como quedan:** el tipo `LowercaseEmail`, la restricción `ck_users_email_lowercase` como texto SQL, la
   migración `b51f3c9e2a64` en modo batch, los 17 tests y el ADR con el nombre `0016-correo-en-minusculas.md` (fecha de
   "Estado": la de E3, E2 punto 6). Opciones: aprobar, o pedir cambios. **Recomendación: aprobar.** Trade-off: G toca el
   registro y el login de todos los usuarios; lo cubren 17 tests y ocho mutantes, pero sobre SQLite (R12).
2. **Desviación de la guía de OWASP: se guarda solo la forma en minúsculas.** Opciones: (a) aceptarla y declararla, como
   dicta ADR-0016; (b) guardar además el correo tal como se escribió (columna nueva y migración: otra fase u otro ítem);
   (c) volver al mecanismo del 13 nov, que tampoco guarda las dos formas. **Recomendación: (a).** Hoy nada usa la forma
   original. El riesgo, un proveedor que distinga mayúsculas en la parte local, es raro, y su efecto es que el correo de
   verificación no llega a ese buzón. Trade-off: la premisa de las 09:04 ("las fuentes de autoridad recomiendan...") no es
   lo que dice OWASP, y el ADR lo dice.
3. **Token de verificación con otra grafía:** un test fija el 404 (lo que dicta G), o queda sin test. **Recomendación:
   el test.** Cuesta uno, y MG8 muestra que vigila que nadie vuelva a comparar con `lower()` en las consultas. Trade-off:
   congela un comportamiento que la app no ejercita, porque nunca firma esa grafía.
4. **El caso `mixed_case_domain` de A9:** borrarlo (lo que dicta G) o sustituirlo por otro correo fuera de regla que la
   base sí acepte. **Recomendación: borrarlo.** `dotless_domain` ya cubre el correo en A9, y la base ya no puede guardar
   el valor del caso borrado.
5. **La migración en modo batch, probada sobre un SQLite propio** (lo que dicta G), o `op.create_check_constraint` directo
   sin test de la migración en la suite. **Recomendación: batch.** E2 (punto 3.5) pide probar la migración, y en
   PostgreSQL emite el mismo `ALTER TABLE`. Trade-off: en SQLite reconstruye la tabla, y un fallo deja
   `_alembic_tmp_users`; por eso el motor propio.
6. **Q1 del 14 nov (09:20) sin base identificada.** G exige Q1 = 0 en `develop`. Opciones: David confirma que esa captura
   es de `develop`, o repite Q1 en `develop` con el nombre de la base visible. **Recomendación: repetirla**, antes de
   `/implementar BE-34 G`. Trade-off: un minuto, frente a apoyar la precondición en una captura ambigua.
7. **R13 (`EmailStr` acepta un correo de 196 caracteres; la columna es `String(150)`):** fila Baja nueva o nada. **Recomendación: fila Baja,
   fuera de BE-34.** Es previo a BE-51 y no lo cambia G.

# PLAN — BE-34: Crear el primer superadmin con un comando manual e idempotente

> Fuente: `docs/deuda/BE-34/verificacion.md` (confirmada; adenda de ocho decisiones de David, 13 nov, 16:28).
> Base: `4f10660` (HEAD de `item/be-34` = `5db7641`: `git diff --name-only 4f10660 5db7641 -- app tests alembic conftest.py
> pyproject.toml .env.example` vacío). Estado: **aprobado por David el 13 nov 2026 con E0 (17:26): cinco fases, A → E; la fase E recibe un test más antes de ejecutarse (E0.3); E1 (17:29) añade una fase F, por escribir y aprobar, para BE-51; detalle en "Enmiendas aprobadas", al final.** Las cifras de este plan (tests,
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
en el contrato de capas. La suite pasa de 638 a 674 tests y la cobertura de 96,82 % a 97,37 %.
**Riesgo principal:** filtrar la contraseña, por el texto de un `ValidationError` (medido: lo incluye) o por el `echo`
del motor (el hash). Los tests de C y E lo impiden, y cuatro mutantes lo demuestran. **No se toca:** `Settings` (sigue
con 15 campos), guards, routers, rutas, la política (BE-35..BE-38), `create_user` (A3), `app/db/database.py` (A5),
`alembic/`, `Dockerfile`, `docker-compose.yml` ni `cd-pipeline.yml`.

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
| ME1 | `app/cli/bootstrap_superadmin.py` | borrar las dos líneas `        if field not in SuperadminBootstrapSettings.model_fields:` / `            field = f"superadmin_{field}"` | `2 failed, 383 passed` |
| ME2 | ídem | el `return 1` tras el `print` de `AlreadyExistsError` → `return 0` | `1 failed, 384 passed` |
| ME3 | ídem | `{created.email}")` → `{created.email} {credentials.password}")` | `2 failed, 383 passed` |
| ME4 | ídem | `    engine = create_async_engine(database_url)` → `    engine = create_async_engine(database_url, echo=True)` | `1 failed, 384 passed` |
| ME5 | ídem | `    sys.exit(main())` → `    main()` | `1 failed, 384 passed` |
| MK1 | `app/services/superadmin_bootstrap.py` | añadir `import app.cli  # noqa: F401` antes del primer `from app.` | import-linter `3 kept, 1 broken` (exit 1) |

Al cerrar cada fase, la compuerta debe dar exit 0, `Compuerta superada.`, `All checks passed!`,
`Contracts: 4 kept, 0 broken.` y `8 warnings`, y además:

| Fin de | pytest | Cobertura (`TOTAL` stmts) | ruff format | mypy | Suite de la copia (sin `test_check*`) |
|---|---|---|---|---|---|
| Base | 638 passed | 96,82 % (965) | 61 files | 56 source files | 349 passed |
| A | 639 passed | 96,82 % (965) | 61 files | 56 source files | 350 passed |
| B | 639 passed | 96,82 % (965) | 61 files | 56 source files | 350 passed |
| C | 650 passed | 97,01 % (966) | 61 files | 56 source files | 361 passed |
| D | 667 passed | 97,07 % (988) | 64 files | 59 source files | 378 passed |
| E | 674 passed | 97,37 % (1031) | 67 files | 62 source files | 385 passed |

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
  - Copia de `4f10660` con el texto del plan: de 638 a 674 tests y de 96,82 % a 97,37 %. Con `"app.api | app.cli"`, un
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
     import runpy
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
     ```
- **Tests (RED primero):** primero el archivo de tests, y luego
  `./venv/Scripts/python.exe -m pytest tests/test_bootstrap_superadmin_command.py -q -p no:cacheprovider --tb=line`.
  Medido: `ModuleNotFoundError: No module named 'app.cli'`. Al final: `7 passed`. Mutantes ME1 a ME5 y MK1 con los
  resultados de la tabla (MK1 se mide con
  `./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"` en la copia).
  Por qué cada truco del test:
  - Base de archivo en `tmp_path`: el comando abre su propio motor, y `:memory:` le daría una base vacía sin tablas.
  - `delitem` antes de `runpy`: evita el `RuntimeWarning` de reejecutar un módulo ya importado, así que los warnings
    siguen en 8.
  - `caplog`: es el único canal donde se ve el `echo` (ME4).
- **Criterio de aceptación:** compuerta como la fila E, con `app\cli\bootstrap_superadmin.py` al 100 % en el informe de
  cobertura. `git show --numstat --format= <sha E>` da `1	0	app/cli/__init__.py`,
  `114	0	app/cli/bootstrap_superadmin.py`, `2	2	pyproject.toml` y
  `169	0	tests/test_bootstrap_superadmin_command.py`. Salida de import-linter:
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
  - tests: create, second run, taken email, three bad variables and the
    python -m path, each on a file database of its own; no password in
    stdout or stderr and no hash in stdout or the log.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase E. Los conteos incluyen el texto que dicta este plan (docstrings, comentarios de
`.env.example`, nombres de tests).

```bash
# 1. Patrón 1 de la verificación: sigue en 0 (el nombre es "bootstrap", que mide el patrón 2) → exit 1
git grep -n -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts

# 2. Patrón 2 por archivo → exactamente estas 8 líneas (108 coincidencias en total):
#    .env.example:6 · app/cli/bootstrap_superadmin.py:19 · app/core/config.py:12 · app/repositories/user_repository.py:1
#    app/services/superadmin_bootstrap.py:3 · tests/test_bootstrap_superadmin_command.py:15 · tests/test_config.py:41
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

# 9. Compuerta → exit 0; 674 passed, 8 warnings; TOTAL 1031 stmts, 97.37 %; 67 files; 62 source files; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

| # | Hallazgo (evidencia) | Destino sugerido |
|---|---|---|
| R1 | AGENTS §3 describe solo el flujo Router → Servicio. `app.cli` es un segundo adaptador (ADR-0015). | Que David añada en AGENTS una línea "comandos de operador en `app/cli/`, ADR-0015", en un PR propio (AGENTS no lo edita un agente). |
| R2 | La parte local del correo conserva mayúsculas. Sonda: `UserCreate(email='Root@Test.COM').email` → `'Root@test.com'`. La unicidad y `get_user_by_email_or_cedula` comparan exacto, así que `Root@test.com` y `root@test.com` son dos cuentas, también en el registro de turistas. No es escalada: el bootstrap crea una fila nueva. | Fila nueva `BE-51` (Baja): "unicidad de correo sensible a mayúsculas en la parte local", decidir si se normaliza. |
| R3 | No existe cambio de contraseña (adenda): la del superadmin es definitiva. BE-11 solo cubre la recuperación (Sale). | Fila nueva de feature (cambio de contraseña autenticado), si David la quiere. |
| R4 | El manual técnico debe recoger el comando (adenda, punto 2). | Bloque del manual `(PLAN §2b)`, sesión Mentor. |
| R5 | `docs/CONTEXT.md` no menciona ADR-0015 ni `app/cli/`. | Cierre del ítem, sesión Mentor. |
| R6 | BE-35 ("siempre queda al menos un superadmin activo") puede reutilizar `UserRepository.count_active_superadmins`. | Nota en la fila BE-35. |
| R7 | import-linter no prohíbe `fastapi`/`starlette` en `app.cli`: el contrato de capas solo fija la dirección. | Opcional; sin fila salvo que David lo pida. |

## Referencias

- pydantic-settings · 2.13.1 (instalada) · `SecretStr` en `BaseSettings`: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- pydantic · 2.12.5 · `ValidationError.errors(include_input=…, include_url=…)`: https://github.com/pydantic/pydantic/blob/v2.12.5/docs/errors/errors.md ;
  tipos secretos: https://docs.pydantic.dev/2.12/api/types/#pydantic.types.SecretStr
- SQLAlchemy · 2.0.48 · `create_async_engine`, `async_sessionmaker(expire_on_commit=False)`, `await engine.dispose()`
  en un script: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- import-linter · 2.15 · capas con hermanos independientes (`"a | b"`):
  https://github.com/seddonym/import-linter/blob/v2.15/docs/contract_types/layers.md
- Python · 3.14 · `runpy.run_path` / `runpy.run_module`: https://docs.python.org/3/library/runpy.html

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

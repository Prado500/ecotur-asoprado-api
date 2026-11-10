# PLAN — A4: Centralizar la configuración en un `Settings` validado al arrancar

> Fuente: `docs/deuda/A4/verificacion.md` (confirmada; adenda de 13 puntos del 10 nov, que manda sobre el cuerpo).
> Base: `55345a1` (`item/a4`, sobre `8cea834` = `origin/develop`). Decisión de diseño: **ADR-0013** (propuesto,
> `docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md`; se acepta al aprobar este plan).
> Estado: **aprobado por David el 10 nov 2026 con E0** (P1–P6 aceptadas como se proponen; ver "Enmiendas aprobadas").

## Resumen para aprobación

Nueve fases llevan las 16 lecturas de `os.getenv` (15 en `app/`, 1 en `alembic/`) y las 3 de `load_dotenv()` a un solo
módulo, `app/core/config.py`: un `Settings` de pydantic-settings (ya instalado) con `get_settings()` en caché. La app
no arranca si falta una de las cinco variables obligatorias, y el error nombra el campo sin imprimir valores. La capa
HTTP recibe la configuración por `Depends(get_settings)`; el resto, por llamada directa. Antes de tocar `jwt.decode`,
la fase A fija tres tests de firma con mutante. Al cerrar: ruff 0 · mypy 0 · 4 kept · 579 tests, compuerta en verde, y
la suite pasa sin `.env` ni variables del CI. **Riesgo principal:** el CD migra con solo `DATABASE_URL`, y la adenda 9 al
pie de la letra lo rompería; el plan propone `DatabaseSettings` (P1). **No se toca:** `echo=True` y el ciclo de vida del
motor (A5), `sqlalchemy.future` (S2), `--soft`, Azure, los textos de usuario, `docs/backlog.md` y `docs/CONTEXT.md`.

## Objetivo y decisiones bloqueadas

Objetivo: que toda la configuración se lea en un solo sitio, validada al arrancar, sin depender del orden de imports ni
de `.env` en la suite. Al cerrar, la compuerta queda en verde completo sin `--soft` local.

1. **Obligatorias, no vacías, sin valor por defecto (adenda 4):** `DATABASE_URL`, `JWT_SECRET_KEY`, `MAIL_USERNAME`,
   `MAIL_PASSWORD`, `AZURE_STORAGE_CONNECTION_STRING`. El resto conserva su valor por defecto actual. `MAIL_FROM` es
   opcional, y sin ella el remitente es `MAIL_USERNAME` (propiedad `Settings.mail_sender`). `tu_correo@gmail.com` sale
   del código. Ninguna fase vuelve obligatoria otra variable (adenda 5): **el merge no exige cambios en Azure.**
2. **Acceso (adenda 8):** `Depends(get_settings)` en `get_current_user`, `get_storage_client` y `registrar_turista`.
   Llamada directa a `get_settings()` en `security.py`, `user_service.py`, `email.py` y `main.py`. `database.py` y
   `alembic/env.py` llaman a `get_database_settings()` (P1).
3. **Mecanismo de lectura (adenda 10, medido con sonda):** `env_file` absoluto (raíz del repo, por la ruta del módulo) +
   `extra="ignore"` + `hide_input_in_errors=True`. Sin `load_dotenv()` en ningún sitio.
4. **Suite sin `.env` (adenda 7):** un `conftest.py` en la raíz fija los 15 campos en el entorno del proceso antes de
   que `tests/conftest.py` importe la app. El bloque `env:` del CI se elimina entero (adenda 6, opción "ninguno").
5. **Fase A = tests de firma (adenda 3)**, con los mutantes M1/M2 medidos en una copia exportada (`git archive`), nunca
   en el árbol. Se repiten en la fase D sobre las líneas nuevas.
6. **Compuerta y trinquete (ADR-0005):** siempre `./venv/Scripts/python.exe scripts/check.py`. Cada fase debe dar
   exactamente su fila de la tabla de compuerta. Un error de más o de menos es BLOQUEANTE. Los archivos tocados quedan
   con 0 errores.
7. **Commits:** el cuerpo termina en `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; el ejecutor pone su
   modelo real si es otro. Solo `git add` de los archivos de la fase.

## Análisis del redactor

**Qué cambia y por qué.** La configuración se lee en tres momentos: al importar (`security.py`, `database.py`,
`email.py`, `main.py`), por instancia (`storage.py`) y por petición (`routers/user.py:66`). Todo pasa a `get_settings()`,
validado una vez. Las constantes de módulo (`SECRET_KEY`, `ALGORITHM`, `DATABASE_URL`, `CORS_ORIGINS`,
`DEFAULT_CORS_ORIGINS`, `conf`) desaparecen. Sus consumidores reciben `Settings`.

**Sondas (adenda 10; `.env` temporal propio en el scratchpad, nunca el real).**
(a) Con el `extra` por defecto de `BaseSettings`, las `POSTGRES_*` del archivo dan 5 errores `extra_forbidden`; con
`extra="ignore"` se toleran. (b) `DATABASE_URL=…${POSTGRES_USER}…` se expande igual con `env_file` que con
`load_dotenv()`. Por eso se elige el mecanismo (1). (c) Una variable del entorno del proceso gana a la del archivo.
(d) **Hallazgo nuevo:** sin `hide_input_in_errors`, el error de un campo ausente imprime en `input_value` los valores ya
leídos. En Azure, un arranque fallido escribiría secretos en el log. Se añade la opción (P3).

**P1: migraciones del CD (riesgo principal).** `cd-pipeline.yml:62,91,120` ejecuta
`docker run --rm -e DATABASE_URL=… alembic upgrade head`. La imagen no trae `.env`, que está en `.gitignore`.
`alembic/env.py:10,12` importa `app.models` → `app.db.database`, que crea el motor al importar. Si `database.py` llamara
al `Settings` completo, el CD fallaría al migrar por falta de `JWT_SECRET_KEY`, `MAIL_*` y `AZURE_*`. Eso choca con la
adenda 5: el merge no debe exigir cambios en Azure. Medido sobre `55345a1` en una exportación sin `.env`:
`alembic upgrade head --sql` con solo `DATABASE_URL` → exit 0, 116 líneas. **Propuesta:** `DatabaseSettings` (solo
`database_url`), de la que hereda `Settings`. Mismo módulo, misma fuente, y las migraciones siguen necesitando solo la
URL. Alternativa: adenda 9 literal + `-e` de cuatro secretos en los tres `docker run`. Exige que los grupos
`VG-ECOTUR-*` los tengan, cosa que no consta.

**Orden y dependencias.**
- A va primero (adenda 3): tests de firma antes de tocar `jwt.decode`.
- B crea `config.py` y el entorno de la suite. Todo lo demás depende de B. Desde B la suite ya no depende de `.env`:
  el código viejo lee el entorno del proceso y `load_dotenv()` no lo sobrescribe (`override=False`).
- C (tests) antes que D (app): C deja de importar `SECRET_KEY`/`ALGORITHM` en los tests. Así D puede borrar las
  constantes sin romper la suite, y ninguna fase supera los 5 archivos.
- E, F y G dependen solo de B y no se tocan entre sí. G va después de D porque los dos editan `dependencies.py`.
- H va después de B (amplía `tests/test_config.py`). I va la última.
- **I001 (P2):** cada fase que reescribe el bloque de imports de un archivo con I001 lo ordena con ruff: D ordena
  `dependencies.py` y `user_service.py`, E ordena `database.py` y `email.py`. I quita `unfixable` y ordena los 4
  restantes, que nunca dependieron del orden. Antes, el orden importaba porque `security.py` leía el entorno al
  importar; desde D ya no lo hace, y la suite en verde tras cada fase es la prueba.

**Qué congela comportamiento relacionado.** `tests/test_token_failure_paths.py` congela las ramas de `jwt.decode`
(caducado, corrupto, sin `sub`, usuario inactivo). `tests/test_main.py` congela CORS. `tests/test_email.py` congela el
cuerpo del correo y parchea `fast_mail.send_message`, que sigue siendo un objeto de módulo. `tests/test_storage.py`
congela el adaptador. `tests/test_fixtures_contract.py` congela los dobles globales, y nada en este plan los cambia.

**Cambios de comportamiento declarados.** (1) Sin `MAIL_FROM`, el remitente es `MAIL_USERNAME` en vez de
`tu_correo@gmail.com`. Gmail ya mostraba la cuenta (adenda 4). (2) Si falta `AZURE_STORAGE_CONNECTION_STRING` o
`JWT_SECRET_KEY`, la app falla al arrancar y no en la primera petición. (3) Los valores vacíos se rechazan.
(4) `FRONTEND_URL` y `AZURE_*` se leen una vez por proceso. Azure reinicia la app al cambiar su configuración.

**Riesgos.** (1) P1. (2) Un `.env` local sin alguna de las cinco obligatorias impide arrancar `uvicorn` en local.
David lo comprueba tras B con un comando que imprime solo nombres de campos (criterio de B). (3) Hasta B, el tercer test
de A depende de la clave local: si el `.env` de David usa la de `.env.example`, falla. Eso es justo lo que el test
detecta: el ejecutor se detiene y avisa. (4) Quitar el `env:` del CI se demuestra en local con la exportación sin
variables. La prueba final es el log del CI del PR, que revisa David. (5) Si alguien añade un campo a `Settings` y no lo
añade a `conftest.py`, su `.env` se cuela en la suite. Lo detecta el test
`test_suite_settings_come_from_the_test_environment_not_from_dotenv`.

**Qué NO se toca.** `echo=True` y su comentario en español (A5); el ciclo de vida del motor (A5);
`sqlalchemy.future` de `user_repository.py` más allá del I001 (S2); `--soft` y `variables: group` del CI (CI duro);
`cd-pipeline.yml` (con P1 aceptado); `docker-compose.yml` y `Dockerfile` (Residuales); `parse_cors_origins` y su
contrato; los textos de usuario; `docs/backlog.md`, `docs/CONTEXT.md`, `docs/PLAN.md` y la bitácora.

**Preguntas para David.**
- **P1 (bloquea E).** `DatabaseSettings` para motor y migraciones (recomendado) o adenda 9 literal + cambio del CD.
- **P2.** I001 repartido (D, E, I) en lugar de todo en la última fase. La adenda 12 lo pide al final. El cambio evita
  reescribir dos veces el mismo bloque de imports y una décima fase.
- **P3.** `hide_input_in_errors=True` no está en la adenda. Sin él, un arranque fallido imprime secretos (sonda d).
- **P4.** El bloque `env:` del CI se elimina entero, también `MAIL_USERNAME`/`MAIL_PASSWORD` reales del grupo de
  variables. La suite ya no los necesita y deja de recibir credenciales reales. Confirmar en el log del CI del PR.
- **P5.** `conftest.py` nuevo en la raíz del repo, frente a escribir en el entorno al principio de `tests/conftest.py`
  (eso exigiría `# noqa: E402` en sus 9 imports). Medido con pytest 9.0.2: la raíz se carga antes, también con
  `pytest tests/x.py` y desde `tests/`.
- **P6.** El tercer test lee la clave de `.env.example` con `dotenv_values`, no con un literal: si alguien cambia la
  clave del ejemplo, el test la sigue. Coste: `python-dotenv` se importa en dos archivos de tests.

## Regla de alcance

- **Sí:** `app/core/config.py` (nuevo), `conftest.py` (nuevo, raíz), `tests/test_config.py` (nuevo); los 8 consumidores
  de `app/` (`security.py`, `email.py`, `storage.py`, `database.py`, `main.py`, `dependencies.py`, `user_service.py`,
  `routers/user.py`); `alembic/env.py`; 7 archivos de tests existentes (`test_token_failure_paths.py`, `conftest.py`,
  `test_user_service.py`, `test_auth.py`, `test_main.py`, `test_email.py`, `test_storage.py`); `.env.example`;
  `ci-pipeline.yml` (solo el bloque `env:`); `pyproject.toml` (solo `unfixable`); el I001 de 4 archivos que no leen
  configuración.
- **No:** ninguna otra línea de esos archivos fuera de lo dictado; nada de la lista "Qué NO se toca".

## Fases

**Tabla de compuerta esperada.** Docs ✔ y `Contracts: 4 kept, 0 broken.` en todas las filas; cobertura ≥ 96.11 %.

| Fin de | ruff check | mypy | pytest | format | Resumen |
|---|---|---|---|---|---|
| Base | 8 (I001) | `Found 9 errors in 5 files (checked 53 source files)` | 549 passed | 57 | NO superada: ruff check, mypy |
| A | 8 | igual | **552** | 57 | igual |
| B | 8 | `Found 9 errors in 5 files (checked 55 source files)` | **573** | 60 | igual |
| C | 8 | `Found 5 errors in 4 files (checked 55 source files)` | 573 | 60 | igual |
| D | **6** | `Found 1 error in 1 file (checked 55 source files)` (`database.py:11`) | **574** | 60 | igual |
| E | **4** | `Success: no issues found in 55 source files` | **575** | 60 | NO superada: ruff check |
| F | 4 | Success | **576** | 60 | igual |
| G | 4 | Success | **577** | 60 | igual |
| H | 4 | Success | **579** | 60 | igual |
| I | **0** (`All checks passed!`) | Success | 579 | 60 | `Compuerta superada.` |

**Mutantes (procedimiento común).** Se miden en una copia de `HEAD` tras el commit de la fase, nunca en el árbol:
`M=$(mktemp -d) && git -C /c/projects/ecotur-asoprado archive HEAD | tar -x -C "$M" && cd "$M"`, después el `sed` de
la fase, `grep -n` para mostrar la línea mutada y
`/c/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider <selección>`. Una copia por
mutante. La salida literal va al handoff y el auditor la repite. **Antes de B**, la copia no tiene `conftest.py` en la
raíz: el `pytest` se lanza con `env DATABASE_URL="sqlite+aiosqlite:///:memory:"
JWT_SECRET_KEY="mutant-run-jwt-key-not-for-any-real-use-0001" MAIL_USERNAME="smtp-account@test.com"
MAIL_PASSWORD="x"` (valores del estilo del CI; nunca se lee `.env`).

**I001 de un archivo concreto:** `./venv/Scripts/python.exe -m ruff check --select I001 --fixable I001 --fix <archivo>`
(`--fixable` gana a `unfixable`, medido con ruff 0.17.2). Solo sobre archivos de la fase. En los que arrastran I001
desde la línea base, solo si la fase lo dicta (D: `dependencies.py`, `user_service.py`; E: `database.py`,
`email.py`). En los demás, para ordenar los imports que la fase añade.

**Texto no dictado.** Los docstrings y comentarios que el plan no dicta palabra por palabra no nombran variables de
entorno en mayúsculas en `app/` ni en `alembic/` (usan el nombre del campo), y en `tests/` no dicen "another key",
"other key" ni "forged". Si no, los conteos 5 y 9 de la Verificación final dejan de cuadrar.

### Fase A — Tests de firma JWT en las dos rutas de `jwt.decode` (la más pequeña)
- Archivos: `tests/test_token_failure_paths.py`.
- Cambios exactos: imports `from pathlib import Path`, `from dotenv import dotenv_values`,
  `from sqlalchemy.ext.asyncio import AsyncSession`; el import de `app.core.security` añade `create_verification_token`.
  Después de `PROTECTED_ROUTE`:
  ```python
  VERIFY_ROUTE = "/usuarios/verificar-email"
  FOREIGN_KEY = "foreign-signing-key-known-only-to-these-tests"
  ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"
  ```
  Dos helpers junto a `_bearer`:
  ```python
  def _resign(token: str, key: str) -> str:
      """Signs a genuine token's claims again with the given key, keeping its algorithm."""
      claims = jwt.decode(token, options={"verify_signature": False})
      algorithm = jwt.get_unverified_header(token)["alg"]
      return jwt.encode(claims, key, algorithm=algorithm)


  def _env_example_jwt_key() -> str:
      """Reads the JWT key that .env.example ships, the one a developer may copy as is."""
      key = dotenv_values(ENV_EXAMPLE)["JWT_SECRET_KEY"]
      assert key
      return key
  ```
- Tests (RED primero). Son de caracterización: pasan con el código actual. Su RED es el mutante.
  1. `test_access_token_signed_with_another_key_returns_401(client, persist_user, make_token)`, docstring
     `"""Unhappy path: a token re-signed with a foreign key is rejected for an active user."""`: usuario activo
     persistido; `GET PROTECTED_ROUTE` con `_bearer(_resign(make_token(user), FOREIGN_KEY))` → `_assert_bearer_401`.
  2. `test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive(client, db_session,
     persist_user)`, docstring `"""Unhappy path: a re-signed verification token is rejected and activates nothing."""`:
     `persist_user(is_active=False)`; `GET VERIFY_ROUTE` con
     `params={"token": _resign(create_verification_token(user.email), FOREIGN_KEY)}` → 400, `set(body) == {"detail"}`,
     `detail` es `str`; `await db_session.refresh(user)`; `user.is_active is False`.
  3. `test_access_token_signed_with_the_env_example_key_returns_401(client, persist_user, make_token)`: como el 1, con
     `_env_example_jwt_key()`. Docstring, que declara el límite (el CI, `ci-pipeline.yml:34`, y producción usan otras
     claves): `"""Edge case: the key that .env.example ships signs nothing this app accepts.` + línea en blanco +
     `Protects whoever copies the example as their .env; CI and production use their own keys."""`.
  - **M1** (`sed -i '95s/algorithms=\[ALGORITHM\])/algorithms=[ALGORITHM], options={"verify_signature": False, "verify_exp": True})/' app/api/dependencies.py`):
    `-k signed_with` → `2 failed, 1 passed`. **M2** (el mismo `sed` en la línea `124` de
    `app/services/user_service.py`) → `1 failed, 2 passed`. Sin mutante, `3 passed`. `verify_exp` explícito porque
    PyJWT 2.12.1 lo apaga junto con la firma (`jwt/api_jwt.py:79-87`) y el mutante debe quitar solo la firma.
- Criterio de aceptación: la fila A de la tabla; M1 y M2 con los conteos exactos. Si el test 3 falla en la compuerta
  local (la clave del `.env` local es la del ejemplo), el ejecutor se detiene y avisa a David sin leer `.env`.
- Fuera de alcance: `app/`; `make_token`; cualquier otro test del archivo.
- Commit: `test(auth): pin JWT signature checks on both decode paths (A4)`. Cuerpo: por qué (precondición de A4: la
  suite no detectaba una firma sin verificar; CONTEXT §8.1), qué fija cada test, M1/M2 con sus conteos, límite del
  tercer test.

### Fase B — Módulo de configuración y entorno de la suite
- Archivos: `app/core/config.py` (nuevo), `conftest.py` (nuevo, raíz), `tests/test_config.py` (nuevo).
- Cambios exactos, `app/core/config.py`:
  ```python
  """Application settings, read once from the process environment and the repository .env file.

  Every configuration value of the app lives here (ADR-0013). Values are validated when first read, so a
  missing or malformed variable stops the app at startup with an error that names the field. The HTTP layer
  injects them with ``Depends(get_settings)``; code with no request calls ``get_settings()`` directly.
  """

  from functools import lru_cache
  from pathlib import Path

  from pydantic import Field
  from pydantic_settings import BaseSettings, SettingsConfigDict

  # Repository-root .env, located by this file and not by the working directory. Optional:
  # process environment variables take priority over it.
  ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


  class DatabaseSettings(BaseSettings):
      """Settings the database layer needs, and the only ones database migrations need.

      Kept apart so that ``alembic upgrade`` runs with the database URL alone, as the CD pipeline does.

      Attributes:
          database_url: SQLAlchemy async URL. Required, non-empty.
      """

      model_config = SettingsConfigDict(
          env_file=ENV_FILE,
          env_file_encoding="utf-8",
          extra="ignore",
          hide_input_in_errors=True,
      )

      database_url: str = Field(min_length=1)


  class Settings(DatabaseSettings):
      """Whole application configuration: one field per environment variable, named in upper case.

      Required (no default, non-empty): jwt_secret_key, mail_username, mail_password,
      azure_storage_connection_string and the inherited database_url. The rest keep the defaults
      the app had before this module existed.
      """

      jwt_secret_key: str = Field(min_length=1)
      algorithm: str = "HS256"
      access_token_expire_minutes: int = 30
      verification_token_expire_minutes: int = 15

      mail_username: str = Field(min_length=1)
      mail_password: str = Field(min_length=1)
      mail_from: str | None = None
      mail_port: int = 465
      mail_server: str = "smtp.gmail.com"

      azure_storage_connection_string: str = Field(min_length=1)
      azure_container_name: str = "ecotur-images"
      azure_temporal_container_name: str = "temp-ecotur-images"

      frontend_url: str = "http://localhost:3000"
      cors_origins: str = "http://localhost:3000"

      @property
      def mail_sender(self) -> str:
          """Sender address: mail_from when set, otherwise the SMTP account (mail_username).

          Returns:
              str: The address the verification email is sent from.
          """
          return self.mail_from or self.mail_username


  @lru_cache
  def get_settings() -> Settings:
      """Builds the application settings once and returns the same instance afterwards.

      Returns:
          Settings: The validated configuration.

      Raises:
          pydantic.ValidationError: When a required variable is missing or a value is malformed.
      """
      return Settings()


  @lru_cache
  def get_database_settings() -> DatabaseSettings:
      """Builds the database settings once; used by the engine and by Alembic.

      Returns:
          DatabaseSettings: The validated database configuration.

      Raises:
          pydantic.ValidationError: When the database URL is missing or empty.
      """
      return DatabaseSettings()
  ```
  `conftest.py` (raíz):
  ```python
  """Suite-wide test configuration, loaded by pytest before tests/conftest.py imports the app.

  The app reads its settings once (app/core/config.py, ADR-0013). Every setting is fixed here, before
  anything imports the app, so the suite never depends on a developer's .env file or on CI variables:
  process environment variables take priority over the .env file.
  """

  import os

  TEST_ENVIRONMENT = {
      "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
      "JWT_SECRET_KEY": "test-only-jwt-secret-key-not-for-production",
      "ALGORITHM": "HS256",
      "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
      "VERIFICATION_TOKEN_EXPIRE_MINUTES": "15",
      "MAIL_USERNAME": "smtp-account@test.com",
      "MAIL_PASSWORD": "test-mail-password",
      "MAIL_FROM": "sender@test.com",
      "MAIL_PORT": "465",
      "MAIL_SERVER": "smtp.test.com",
      "AZURE_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true",
      "AZURE_CONTAINER_NAME": "ecotur-images",
      "AZURE_TEMPORAL_CONTAINER_NAME": "temp-ecotur-images",
      "FRONTEND_URL": "http://localhost:3000",
      "CORS_ORIGINS": "http://localhost:3000",
  }

  os.environ.update(TEST_ENVIRONMENT)
  ```
- Tests (RED primero, `tests/test_config.py`; RED = `ModuleNotFoundError: app.core.config` antes del módulo).
  Constantes `REQUIRED` (los 5 campos, en minúscula) y `OPTIONAL_DEFAULTS` (dict de los 10 opcionales con sus valores
  de arriba, `mail_from: None`). Cada test arma el entorno solo con `monkeypatch.setenv`/`delenv` (`name.upper()`; nunca `os.environ`) y
  construye `Settings(_env_file=None)`, salvo los que dicen otra cosa. 21 casos:
  1. `test_missing_required_variable_fails_naming_it` [×5, `REQUIRED`]:
     `[(e["type"], e["loc"]) for e in exc_info.value.errors()] == [("missing", (field,))]`.
  2. `test_empty_required_variable_is_rejected` [×5]: `== [("string_too_short", (field,))]`.
  3. `test_optional_variables_keep_their_current_defaults`: `set(Settings.model_fields) == set(REQUIRED) |
     set(OPTIONAL_DEFAULTS)`; sin los 10 opcionales, `{n: getattr(s, n) for n in OPTIONAL_DEFAULTS} == OPTIONAL_DEFAULTS`.
  4. `test_mail_sender_defaults_to_mail_username`: sin `MAIL_FROM` y con `MAIL_USERNAME=account@test.com` →
     `mail_sender == "account@test.com"`.
  5. `test_mail_sender_is_mail_from_when_set`: `MAIL_FROM=sender@test.com` → `mail_sender == "sender@test.com"`.
  6. `test_env_file_ignores_unknown_keys_and_expands_references(tmp_path, monkeypatch)`: archivo con `POSTGRES_USER=u`,
     `POSTGRES_PASSWORD=p`, `POSTGRES_HOST=h`, `POSTGRES_PORT=5432`, `POSTGRES_DB=d` y
     `DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}`;
     `delenv("DATABASE_URL")`; `Settings(_env_file=path).database_url == "postgresql+asyncpg://u:p@h:5432/d"`.
  7. `test_process_environment_beats_env_file(tmp_path, monkeypatch)`: archivo `JWT_SECRET_KEY=from-file-key`, entorno
     `from-process-key` → gana el entorno.
  8. `test_database_settings_need_only_the_database_url`: sin las otras cuatro obligatorias,
     `DatabaseSettings(_env_file=None).database_url` vale la URL fijada, y `Settings(_env_file=None)` lanza `ValidationError`.
  9. `test_settings_getters_are_cached` [×2: `get_settings`, `get_database_settings`]: `getter() is getter()`.
  10. `test_env_file_is_the_repository_root_dotenv`: `ENV_FILE == Path(__file__).resolve().parents[1] / ".env"`.
  11. `test_suite_settings_come_from_the_test_environment_not_from_dotenv`: `get_settings() == Settings(_env_file=None)`.
  12. `test_validation_errors_do_not_echo_values`: se borran los 15 campos del entorno y se fija
      `JWT_SECRET_KEY=leak-sentinel-value`; con `pytest.raises(ValidationError)`, `"leak-sentinel-value" not in str(exc)`.
  - **M9** (`sed -i '/hide_input_in_errors=True,/d' app/core/config.py`): `-k echo_values` → `1 failed`.
    **M10** (`sed -i 's/extra="ignore",/extra="forbid",/' app/core/config.py`): `-k unknown_keys` → `1 failed`.
- Criterio de aceptación: la fila B; M9 y M10. **Suite sin `.env`:** tras el commit,
  `X=$(mktemp -d) && git archive HEAD | tar -x -C "$X" && test ! -e "$X/.env" && cd "$X" && env -u DATABASE_URL -u JWT_SECRET_KEY -u MAIL_USERNAME -u MAIL_PASSWORD -u AZURE_STORAGE_CONNECTION_STRING /c/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`
  → `573 passed`. Sobre `55345a1` daba error de colección (`ArgumentError … got None`). **Comprobación de David** (no la
  corre el agente; no imprime valores):
  `./venv/Scripts/python.exe -c "from app.core.config import get_settings; get_settings(); print('ok')"` → `ok`. Si
  falla, el error lista los campos que faltan, sin valores (`hide_input_in_errors`).
- Fuera de alcance: ningún consumidor (siguen con `os.getenv` hasta su fase); `pyproject.toml`; ADR-0013 (se commitea
  con el plan).
- Commit: `feat(config): add validated Settings and a .env-free test env (A4)`. Cuerpo: por qué (15 lecturas
  sin validar, `.env` cargado por efecto lateral, suite atada a `.env`), un bullet por archivo, las sondas (a)–(d),
  `DatabaseSettings` por el CD (P1), que los consumidores migran en C–G.

### Fase C — Los tests dejan de importar las constantes JWT
- Archivos: `tests/conftest.py`, `tests/test_user_service.py`, `tests/test_auth.py`.
- Cambios exactos:
  - `tests/conftest.py`: `make_token` gana `extra_claims: dict[str, Any] | None = None` (keyword-only), que se mezcla
    sobre `{"sub": user.email, "role": user.role.value}`. El docstring lo documenta. `from typing import Any`.
  - `tests/test_user_service.py`: `:18` importa solo `create_verification_token, get_password_hash`; se añade
    `from app.core.config import get_settings`. En `:105` y `:203`, `settings = get_settings()` y
    `jwt.decode(..., settings.jwt_secret_key, algorithms=[settings.algorithm])`. Los dos `jwt.encode` a mano
    (`:274-282`, `:292-300`) pasan a `make_token(make_user(email="turista@example.com"),
    expires_delta=timedelta(minutes=-1), extra_claims={"scope": "email_verification"})` y
    `make_token(make_user(email="turista@example.com"), extra_claims={"scope": "access"})`. Sus tests reciben
    `make_user, make_token`. `from datetime import timedelta` (el hook quita `UTC`, `datetime` si quedan sin uso).
  - `tests/test_auth.py`: el import de `app.core.security` pierde `ALGORITHM, SECRET_KEY`; se añade
    `from app.core.config import get_settings`. En `:114-115`, `settings = get_settings()` y el `decode` con sus
    campos. `assert SECRET_KEY is not None` desaparece.
- Tests (RED primero): RED de herramienta, los 4 `[arg-type]` de `tests/test_user_service.py:105,203,280,298` →
  0. Los tests migrados conservan su fuerza: **M3** (`sed -i '124s/algorithms=\[ALGORITHM\])/algorithms=[ALGORITHM], options={"verify_exp": False})/' app/services/user_service.py`)
  con `tests/test_user_service.py -k expired_token` → `1 failed`; **M4**
  (`sed -i 's/if email is None or scope != "email_verification":/if email is None:/' app/services/user_service.py`)
  con `-k wrong_scope` → `1 failed`.
- Criterio de aceptación: la fila C; M3 y M4;
  `git grep -n -E "\bSECRET_KEY\b|import .*\bALGORITHM\b|ALGORITHM,$" -- tests` → 0.
- Fuera de alcance: `app/`; otros usos de `make_token`.
- Commit: `test(auth): drop JWT constant imports; sign tokens with make_token (A4)`.

### Fase D — La app firma y verifica JWT con `Settings`
- Archivos: `app/core/security.py`, `app/api/dependencies.py`, `app/services/user_service.py`,
  `tests/test_token_failure_paths.py`.
- Cambios exactos:
  - `security.py`: fuera `import os` y las 4 constantes (`:7-10`); `from app.core.config import get_settings`.
    `create_access_token` y `create_verification_token` hacen `settings = get_settings()` y usan
    `settings.access_token_expire_minutes` / `verification_token_expire_minutes` / `jwt_secret_key` / `algorithm`.
    Docstrings con `Args`/`Returns`.
  - `dependencies.py`: el import de `app.core.security` se sustituye por `from app.core.config import Settings,
    get_settings`. `get_current_user` gana `settings: Settings = Depends(get_settings)` (tercer parámetro) y decodifica
    con `jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])`. Docstring con
    `Args`/`Returns`/`Raises`. I001 aplicado.
  - `user_service.py`: el import de `app.core.security` pierde `SECRET_KEY, ALGORITHM`; se añade
    `from app.core.config import get_settings`. `verify_email_account` hace `settings = get_settings()` antes del `try`.
    I001 aplicado.
  - `tests/test_token_failure_paths.py`: `:179` pasa `settings=get_settings()`. Se importan `get_settings` y
    `from app.main import app`. Test nuevo (abajo).
- Tests (RED primero): `test_protected_route_verifies_with_the_injected_settings(client, persist_user,
  make_auth_headers)`, docstring
  `"""Edge case: get_current_user verifies with the Settings it is given, not a module copy."""`: `rotated = get_settings().model_copy(update={"jwt_secret_key": FOREIGN_KEY})`;
  `app.dependency_overrides[get_settings] = lambda: rotated` (lo limpia el `clear()` del fixture `client`); token de
  `make_auth_headers(user)` → `_assert_bearer_401`. RED antes de D: 200, porque el override no llega a `SECRET_KEY`.
  Además, RED de herramienta: mypy `security.py:71,87`, `dependencies.py:95`, `user_service.py:124` → 0.
  - **M1'** (`sed -i 's/algorithms=\[settings.algorithm\])/algorithms=[settings.algorithm], options={"verify_signature": False, "verify_exp": True})/' app/api/dependencies.py`)
    con `tests/test_token_failure_paths.py -k signed_with` → `2 failed, 1 passed`; **M2'** (mismo `sed` sobre
    `app/services/user_service.py`) → `1 failed, 2 passed`; **M5**
    (`sed -i 's/jwt.decode(token, settings.jwt_secret_key/jwt.decode(token, get_settings().jwt_secret_key/' app/api/dependencies.py`)
    con `-k injected_settings` → `1 failed`.
- Criterio de aceptación: la fila D (ruff 6: desaparecen los I001 de `dependencies.py` y `user_service.py`); M1', M2', M5.
- Fuera de alcance: `get_storage_client` (G); `UserService.__init__`; el resto de `dependencies.py`.
- Commit: `refactor(auth): sign and verify JWTs with the injected Settings (A4)`.

### Fase E — Motor, migraciones y cliente SMTP desde `Settings` (requiere P1)
- Archivos: `app/db/database.py`, `alembic/env.py`, `app/core/email.py`, `tests/test_email.py`.
- Cambios exactos:
  - `database.py`: fuera `import os`, `dotenv`, `load_dotenv()` y `DATABASE_URL`;
    `from app.core.config import get_database_settings`; `create_async_engine(get_database_settings().database_url,
    echo=True)` con su comentario intacto (A5). I001 aplicado.
  - `alembic/env.py`: fuera `import os`, `dotenv`, `load_dotenv()`, `database_url` y el `raise ValueError`;
    `from app.core.config import get_database_settings`; tras `config = context.config`:
    `# Same source as the app (ADR-0013): validated settings; only the database URL is required.` y
    `config.set_main_option("sqlalchemy.url", get_database_settings().database_url)`.
  - `email.py`: fuera `import os`, `dotenv`, `load_dotenv()` y `conf`. Imports:
    `from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType`, `from pydantic import EmailStr`,
    `from app.core.config import Settings, get_settings`. Función `_smtp_config(settings: Settings) -> ConnectionConfig`
    (docstring Google) con los mismos argumentos de hoy, salvo `MAIL_USERNAME=settings.mail_username`,
    `MAIL_PASSWORD=settings.mail_password`, `MAIL_FROM=settings.mail_sender`, `MAIL_PORT=settings.mail_port` y
    `MAIL_SERVER=settings.mail_server`; `fast_mail = FastMail(_smtp_config(get_settings()))`. I001 aplicado.
- Tests (RED primero): RED de herramienta: mypy `database.py:11` → 0; `git grep -n -E "getenv|load_dotenv" -- app/db
  alembic app/core/email.py` → 0. Test nuevo en `tests/test_email.py`, de caracterización (pasa antes y después):
  `test_smtp_client_is_configured_from_settings`: `(config.MAIL_USERNAME, config.MAIL_PASSWORD.get_secret_value(),
  config.MAIL_FROM, config.MAIL_PORT, config.MAIL_SERVER) == (s.mail_username, s.mail_password, s.mail_sender,
  s.mail_port, s.mail_server)`, con `config = email_module.fast_mail.config`. **M6**
  (`sed -i 's/MAIL_FROM=settings.mail_sender/MAIL_FROM=settings.mail_username/' app/core/email.py`) →
  `-k configured_from_settings` → `1 failed` (el entorno de prueba distingue remitente y cuenta).
- Criterio de aceptación: la fila E. **Migraciones como el CD:** en exportaciones de `55345a1` y de `HEAD`,
  `env -u JWT_SECRET_KEY -u MAIL_USERNAME -u MAIL_PASSWORD -u AZURE_STORAGE_CONNECTION_STRING DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db" /c/projects/ecotur-asoprado/venv/Scripts/python.exe -m alembic upgrade head --sql > out.sql`
  → exit 0 en las dos y `cmp` de los dos `out.sql` sin diferencias. Sin `DATABASE_URL` en `HEAD` → exit ≠ 0 y la
  salida de error contiene `database_url`.
- Fuera de alcance: `echo=True`; la plantilla HTML; `send_verification_email`.
- Commit: `refactor(config): engine, migrations and SMTP client read Settings (A4)`. El cuerpo declara el
  cambio de remitente (`tu_correo@gmail.com` → `MAIL_USERNAME` si falta `MAIL_FROM`) y por qué el CD sigue intacto.

### Fase F — CORS y URL del frontend desde `Settings`
- Archivos: `app/main.py`, `app/api/routers/user.py`, `tests/test_main.py`, `tests/test_auth.py`.
- Cambios exactos:
  - `main.py`: fuera `import os`, `DEFAULT_CORS_ORIGINS`, el comentario `:193-195` y `CORS_ORIGINS`;
    `from app.core.config import get_settings`. El comentario sobre `app.add_middleware` pasa a ser
    `# Allowed origins come from Settings.cors_origins (ADR-0013); wildcards are rejected at startup.` y el argumento
    a `allow_origins=parse_cors_origins(get_settings().cors_origins),`. `parse_cors_origins` no cambia.
  - `routers/user.py`: fuera `import os`; `from app.core.config import Settings, get_settings`. `registrar_turista`
    gana `settings: Settings = Depends(get_settings)` (último parámetro, con línea `Args`);
    `frontend_url = settings.frontend_url.rstrip("/")`.
  - `tests/test_main.py`: el import pasa a `from fastapi.middleware.cors import CORSMiddleware`,
    `from app.core.config import Settings, get_settings` y `from app.main import app, parse_cors_origins`. Helper
    `_allowed_origins() -> list[str]`, que devuelve `kwargs["allow_origins"]` del `Middleware` de `app.user_middleware`
    cuyo `cls is CORSMiddleware`. Las líneas `:49,53-55,59,71,80` usan
    `parse_cors_origins(Settings.model_fields["cors_origins"].default)` (`:49`) y `_allowed_origins()` (resto).
    `test_configured_cors_origins_have_no_wildcard` añade
    `_allowed_origins() == parse_cors_origins(get_settings().cors_origins)`.
- Tests (RED primero): `tests/test_auth.py::test_register_builds_the_verification_link_from_frontend_url(client,
  mock_send_email)`: override de `get_settings` con
  `get_settings().model_copy(update={"frontend_url": "https://front.example/"})`; registro → 201 y
  `mock_send_email.assert_called_once_with(email_to=USER_PAYLOAD["email"], first_name="Juan", token=ANY,
  base_url="https://front.example")`. RED antes de F: `base_url` es `http://localhost:3000`. Se añade
  `from app.main import app`. **M7** (`sed -i 's/settings.frontend_url.rstrip("\/")/settings.frontend_url/' app/api/routers/user.py`)
  → `-k frontend_url` → `1 failed`.
- Criterio de aceptación: la fila F; `git grep -n "DEFAULT_CORS_ORIGINS" -- app tests` → 0.
- Fuera de alcance: el resto de handlers; la lista de métodos y cabeceras de CORS (SEC1).
- Commit: `refactor(api): CORS origins and frontend URL come from Settings (A4)`.

### Fase G — Adaptador de Azure construido desde `Settings` inyectado
- Archivos: `app/core/storage.py`, `app/api/dependencies.py`, `tests/test_storage.py`.
- Cambios exactos:
  - `storage.py`: fuera `import os`; `__init__(self, connection_string: str, container_name: str,
    temporal_container_name: str) -> None`, que guarda los tres valores y conserva el `ValueError` si la cadena está
    vacía. Docstring con `Args`/`Raises`.
  - `dependencies.py`: `get_storage_client(settings: Settings = Depends(get_settings)) -> AzureStorageClient`, que
    devuelve `AzureStorageClient(connection_string=settings.azure_storage_connection_string,
    container_name=settings.azure_container_name,
    temporal_container_name=settings.azure_temporal_container_name)`. Docstring Google.
  - `tests/test_storage.py`: el fixture `doubles` deja de usar `monkeypatch.setenv` y construye el cliente con
    `connection_string="UseDevelopmentStorage=true", container_name="ecotur-images",
    temporal_container_name="temp-ecotur-images"`. Prueba lo mismo, con los valores explícitos (adenda 2).
    `test_init_without_connection_string_raises` pasa `connection_string=""` (sin `delenv`).
- Tests (RED primero): `test_get_storage_client_builds_the_adapter_from_settings`: con `BlobServiceClient` parcheado
  (`patch.object(storage_module, "BlobServiceClient", autospec=True)`) y
  `settings = get_settings().model_copy(update={"azure_storage_connection_string": "UseDevelopmentStorage=true",
  "azure_container_name": "perm-c", "azure_temporal_container_name": "temp-c"})`:
  `cls.from_connection_string.assert_called_once_with("UseDevelopmentStorage=true")` y
  `(client.container_name, client.temporal_container_name) == ("perm-c", "temp-c")`. RED antes de G: `TypeError`
  (`get_storage_client()` no recibe `settings`). **M8**
  (`sed -i 's/ container_name=settings.azure_container_name,/ container_name=settings.azure_temporal_container_name,/' app/api/dependencies.py`)
  con `tests/test_storage.py -k from_settings` → `1 failed`.
- Criterio de aceptación: la fila G; `git grep -n -E "getenv|setenv|delenv" -- app/core/storage.py tests/test_storage.py` → 0.
- Fuera de alcance: los métodos del adaptador; los dobles de `tests/conftest.py`.
- Commit: `refactor(storage): build the Azure adapter from injected Settings (A4)`.

### Fase H — `.env.example` completo y válido; CI sin `env:`
- Archivos: `.env.example`, `.azure-pipelines/ci-pipeline.yml`, `tests/test_config.py`.
- Cambios exactos:
  - `.env.example`: `:20-22` → `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`,
    `VERIFICATION_TOKEN_EXPIRE_MINUTES=15` (`:19` intacta). Tras el bloque JWT, un bloque
    `# Email (SMTP account that sends the verification email)` con `MAIL_USERNAME=cuenta_smtp@example.com`,
    `MAIL_PASSWORD=DIGITAR_CONTRASEÑA_DE_APLICACION`, `# Optional: when missing, the sender is MAIL_USERNAME.`,
    `MAIL_FROM=cuenta_smtp@example.com`, `MAIL_PORT=465`, `MAIL_SERVER=smtp.gmail.com`.
    `AZURE_TEMPORAL_CONTAINER_NAME=temp-ecotur-images` tras `AZURE_CONTAINER_NAME`. Un bloque
    `# Frontend (base URL of the links sent by email)` con `FRONTEND_URL=http://localhost:3000` antes del de CORS.
  - `ci-pipeline.yml`: se borran `:32-36` (`env:` y sus 4 variables). Sobre `- script:` (tras el comentario `:28`) va
    `# No env block: the suite fixes its own configuration in conftest.py (ADR-0013).`
  - `tests/test_config.py`: `from dotenv import dotenv_values`;
    `ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"`; dos tests nuevos (abajo).
- Tests (RED primero, los dos fallan antes del cambio de `.env.example`):
  1. `test_env_example_is_a_valid_configuration(monkeypatch)`: se borran del entorno los 15 campos;
     `Settings(_env_file=ENV_EXAMPLE)` no lanza, y
     `(algorithm, access_token_expire_minutes, verification_token_expire_minutes) == ("HS256", 30, 15)`. Antes:
     `ValidationError` (`mail_username` ausente, `int_parsing`).
  2. `test_env_example_documents_every_setting`:
     `{n.upper() for n in Settings.model_fields} <= set(dotenv_values(ENV_EXAMPLE))`. Antes faltan 7 claves.
- Criterio de aceptación: la fila H; `git grep -n -E "^\s+env:" -- .azure-pipelines/ci-pipeline.yml` → 0;
  `git grep -n "tu_correo@gmail.com" -- app tests .env.example` → 0; la suite exportada sin `.env` ni variables →
  `579 passed`. **MD (David, en el PR):** el paso "Compuerta de calidad" del CI pasa sin el bloque `env:`.
- Fuera de alcance: `--soft`, `variables: group` y el resto del YAML; `cd-pipeline.yml`; claves `POSTGRES_*`.
- Commit: `chore(config): complete .env.example; drop the CI gate's env block (A4)`.

### Fase I — Fuera `unfixable`; I001 en los 4 archivos restantes
- Archivos: `pyproject.toml`, `app/api/routers/audit.py`, `app/repositories/user_repository.py`, `app/schemas/audit.py`,
  `app/services/audit_service.py`.
- Cambios exactos: se borran `pyproject.toml:69-72` (3 líneas de comentario y `unfixable = ["I001"]`). Después,
  `./venv/Scripts/python.exe -m ruff check --select I001 --fix app/api/routers/audit.py app/repositories/user_repository.py app/schemas/audit.py app/services/audit_service.py`.
  No se cambia nada más en esos archivos.
- Tests (RED primero): RED de herramienta, los 4 I001 → 0. La suite en verde antes (fila H) y después (fila I) es la
  prueba de que el orden de imports ya no decide nada (adenda 12).
- Criterio de aceptación: la fila I. `Compuerta superada.`, exit 0, sin `--soft`.
- Fuera de alcance: cualquier otra regla de ruff; `sqlalchemy.future` (S2).
- Commit: `style(imports): drop unfixable I001 and sort the last four blocks (A4)`.

## Verificación final

Desde la raíz del repo, sobre el último commit. Los conteos incluyen el texto que este plan dicta.

```bash
# 1. Lecturas de entorno fuera del módulo de configuración → 0 líneas
git grep -n -E "os\.getenv|os\.environ|getenv\(|environ\[|environ\.get" -- app alembic tests scripts
# 2. Única escritura de entorno de la suite → 1 línea: conftest.py:…:os.environ.update(TEST_ENVIRONMENT)
git grep -n -E "os\.environ|getenv" -- conftest.py
# 3. dotenv → 2 líneas, ambas "from dotenv import dotenv_values": tests/test_config.py y tests/test_token_failure_paths.py
git grep -n -E "load_dotenv|from dotenv" -- app alembic tests
# 4. pydantic-settings → 3 líneas, todas en app/core/config.py (import, class DatabaseSettings, model_config)
git grep -n -E "BaseSettings|pydantic_settings|SettingsConfigDict" -- app tests alembic
# 5. Constantes de configuración en app/alembic → 2 líneas, ambas en app/main.py: docstring de parse_cors_origins
#    ("``CORS_ORIGINS`` value") y su ValueError ("CORS_ORIGINS must list explicit origins")
git grep -n -E "\bSECRET_KEY\b|\bALGORITHM\b|ACCESS_TOKEN_EXPIRE_MINUTES|VERIFICATION_TOKEN_EXPIRE_MINUTES|\bDATABASE_URL\b|\bCORS_ORIGINS\b" -- app alembic
# 6. Constantes importadas por los tests → 0
git grep -n -E "\bSECRET_KEY\b|DEFAULT_CORS_ORIGINS|import .*\b(ALGORITHM|CORS_ORIGINS)\b" -- tests
# 7. Default de correo heredado → 0
git grep -n "tu_correo@gmail.com" -- app tests .env.example
# 8. unfixable → 0; env del CI → 0; --soft sigue (fuera de alcance) → 2
git grep -n "unfixable" -- pyproject.toml
git grep -n -E "^\s+env:" -- .azure-pipelines/ci-pipeline.yml
git grep -n -- "--soft" -- .azure-pipelines
# 9. Tests de firma → 3 líneas en tests/test_token_failure_paths.py: el decode de _resign ("verify_signature")
#    y las dos definiciones "..._signed_with_another_key_..."
git grep -n -i -E "verify_signature|wrong.?key|other.?key|forged|InvalidSignature" -- tests
# 10. Herramientas → "All checks passed!" · "Success: no issues found in 55 source files"
./venv/Scripts/python.exe -m ruff check .
./venv/Scripts/python.exe -m mypy
# 11. Compuerta → exit 0, "Compuerta superada.", 60 files already formatted, Contracts: 4 kept, 0 broken.,
#     579 passed, cobertura >= 96.11 %
./venv/Scripts/python.exe scripts/check.py
# 12. Suite sin .env ni variables → 579 passed
X=$(mktemp -d) && git archive HEAD | tar -x -C "$X" && test ! -e "$X/.env" && cd "$X" && env -u DATABASE_URL -u JWT_SECRET_KEY -u MAIL_USERNAME -u MAIL_PASSWORD -u AZURE_STORAGE_CONNECTION_STRING /c/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
# 13. En esa misma copia: la app arranca con las cinco obligatorias y nada más → exit 0 (también sobre 55345a1)
env -i PATH="$PATH" SYSTEMROOT="$SYSTEMROOT" DATABASE_URL="sqlite+aiosqlite:///:memory:" JWT_SECRET_KEY="k-0123456789-0123456789-0123456789" MAIL_USERNAME="a@test.com" MAIL_PASSWORD="x" AZURE_STORAGE_CONNECTION_STRING="UseDevelopmentStorage=true" /c/projects/ecotur-asoprado/venv/Scripts/python.exe -c "import app.main"
# 14. ... y sin JWT_SECRET_KEY no arranca → exit 1; stderr contiene "jwt_secret_key" y "Field required", y no "a@test.com"
#     (sobre 55345a1 el mismo comando daba exit 0: el fallo salía en la primera petición; medido el 10 nov)
env -i PATH="$PATH" SYSTEMROOT="$SYSTEMROOT" DATABASE_URL="sqlite+aiosqlite:///:memory:" MAIL_USERNAME="a@test.com" MAIL_PASSWORD="x" AZURE_STORAGE_CONNECTION_STRING="UseDevelopmentStorage=true" /c/projects/ecotur-asoprado/venv/Scripts/python.exe -c "import app.main"
# 15. Migraciones como el CD (solo DATABASE_URL) → exit 0 y salida idéntica a la de 55345a1 (ver criterio de E)
```

## Enmiendas aprobadas

### E0 — 10 nov 2026, 12:12 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «p1-p6 si como propone el plan; la reorganizacion que propones me parece que solo afecta si
alguien por alguna razon quisiera usar la app en ese commit […] creo que no merece la pena […] se declara en el pr».

**Plan aprobado con las nueve fases A → I en el orden escrito.** Tabla de compuerta, mutantes, Verificación final y
`progress.json` sin cambios.

1. **P1:** sí, `DatabaseSettings` para el motor y las migraciones. Sustituye al punto 9 de la adenda de
   `verificacion.md` ("`alembic/env.py` usa el mismo `Settings`"), que la sesión Mentor escribió sin leer
   `.azure-pipelines/cd-pipeline.yml:62,91,120`. `cd-pipeline.yml` no se toca.
2. **P2:** sí, I001 repartido en D, E e I. Ajusta el punto 12 de la adenda (pedía todo en la última fase); la prueba que
   pedía se conserva: suite en verde antes y después de cada ordenamiento.
3. **P3:** sí, `hide_input_in_errors=True`.
4. **P4:** sí, el bloque `env:` del CI se elimina entero. David revisa el log del CI del PR (MD de la fase H).
5. **P5:** sí, `conftest.py` nuevo en la raíz.
6. **P6:** sí, el tercer test lee la clave de `.env.example` con `dotenv_values`.
7. **Orden E → F → G, sin cambios, con un límite que la descripción del PR declara.** La fase E retira los
   `load_dotenv()` de `app/db/database.py:6` y `app/core/email.py:6`, que son los que hoy llevan `.env` al entorno del
   proceso; `app/main.py:196`, `app/api/routers/user.py:66` y `app/core/storage.py:42-46` siguen con `os.getenv` hasta
   F y G. En los commits de E y de F, la app arrancada en local desde `.env` toma los valores por defecto de
   `CORS_ORIGINS` y `FRONTEND_URL` y el adaptador de Azure lanza `ValueError`; la suite no lo ve (el `conftest.py` de la
   raíz fija el entorno) y en Azure y en el CI no ocurre (no hay `.env`). El estado tras G es correcto. El Mentor
   propuso ejecutar D → F → G → E; David lo descartó: nadie ejecuta la app en esos dos commits y el reorden obligaba a
   recalcular la tabla y `progress.json`. **Ningún ejecutor ni auditor lo trata como hallazgo:** está aceptado aquí.
8. **Residuales que reciben fila en el cierre de hoy** (los escribe la sesión Mentor en `docs/backlog.md`, no este
   ítem): 1 y 2 (sin `.dockerignore`; `docker-compose.yml` con cuatro variables); 3, 4 y 6 como dice el plan; y uno
   nuevo: longitud mínima de `jwt_secret_key` (`Field(min_length=1)` acepta una clave de un carácter; exigir 32
   condiciona el arranque a las claves de las tres Web Apps, sin medir).

## Residuales

1. **Sin `.dockerignore`.** `Dockerfile:8,15` (`COPY . .`) mete el `.env` local en las imágenes construidas en local; el
   CD construye desde el checkout, sin `.env`. Destino: fila nueva, seguridad, `B-FUTURO` o la puesta en `staging`.
2. **`docker-compose.yml:9-13`** solo pasa `DATABASE_URL`, `JWT_SECRET_KEY`, `ALGORITHM` y
   `ACCESS_TOKEN_EXPIRE_MINUTES`. Tras A4, `docker compose up` arranca solo gracias al `.env` copiado (residual 1).
   Destino: misma fila.
3. **`SecretStr`** para `jwt_secret_key`, `mail_password`, `azure_storage_connection_string` y `database_url`, para que
   un `repr` no muestre secretos. Destino: `B-FUTURO`, Baja (ADR-0013, alternativa 4).
4. **El correo dice "Este enlace expirará en 15 minutos."** (`app/core/email.py:96`), pero la caducidad es configurable
   (`verification_token_expire_minutes`). Destino: fila nueva, Baja.
5. **`variables: - group: VG-ECOTUR-DEV`** (`ci-pipeline.yml:16`) ya no lo usa la compuerta tras H. Destino: CI duro
   (CONTEXT §8.2).
6. **`AZURE_STORAGE_CONNECTION_STRING=Endpoint=sb://...`** en `.env.example:28` tiene formato de Service Bus, no de
   Storage. Destino: Baja, junto al residual 4.
7. **`conftest.py` de la raíz fuera de `mypy.files`** (`pyproject.toml:94`). Es un dict sin funciones. Destino: CI duro,
   si se quiere.

## Referencias

- pydantic-settings · 2.13.1 · https://docs.pydantic.dev/latest/concepts/pydantic_settings/#dotenv-env-support (Context7
  `/pydantic/pydantic-settings`: el entorno gana al `.env`; `_env_file=None`; con `extra`, las claves sobrantes del
  dotenv llegan al modelo). Comportamiento con `extra` y `${VAR}` medido con sonda.
- FastAPI · 0.135.1 · https://fastapi.tiangolo.com/advanced/settings/ (Context7 `/websites/fastapi_tiangolo`:
  `@lru_cache` en `get_settings`, `Depends(get_settings)`, `app.dependency_overrides[get_settings]` en tests).
- pydantic · 2.12.5 · https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.hide_input_in_errors
  (medido con sonda: sin la opción, `input_value` muestra lo leído).
- PyJWT · 2.12.1 · https://pyjwt.readthedocs.io/en/stable/api.html (con `verify_signature: False`, las demás
  verificaciones se apagan salvo que se pidan; leído en `venv/Lib/site-packages/jwt/api_jwt.py:79-87`).
- pytest · 9.0.2 · https://docs.pytest.org/en/stable/how-to/writing_plugins.html#plugin-discovery-order-at-tool-startup
  (`conftest.py` de la raíz antes que el de `tests/`, medido con sonda en tres formas de invocar).
- ruff · 0.17.2 · https://docs.astral.sh/ruff/settings/#lint_unfixable (`--fixable I001` gana a `unfixable`, medido
  con `--diff`).
- Starlette · 1.3.1 · `Middleware.cls`/`.kwargs` leído en `venv/Lib/site-packages/starlette/middleware/__init__.py:21-25`.
- fastapi-mail · 1.6.5 · `FastMail.config` leído en `venv/Lib/site-packages/fastapi_mail/fastmail.py:50-51`.

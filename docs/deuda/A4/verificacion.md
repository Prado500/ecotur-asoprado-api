# Verificación — A4: configuración dispersa, `pydantic-settings` sin usar

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A2, fila A4, l.98) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` (sección A4, l.490)
**Fecha:** 2026-11-10

## Qué describe el ítem
La configuración se lee con `os.getenv` repartido por módulos, al importar, sin validación de arranque;
`pydantic-settings` está declarado e instalado pero no se usa. Consecuencias citadas: `SECRET_KEY` puede ser
`None` y el fallo sale tarde (PyJWT en la primera petición); `email.py` arrastra `"tu_correo@gmail.com"` a
producción; el orden de imports decide si `.env` está cargado, por eso I001 es `unfixable` hasta cerrar A4.
La fila añade: precondición de tests de caracterización de firma JWT, `Settings` sin default para
`JWT_SECRET_KEY`, migrar los `jwt.encode` a mano de `tests/test_user_service.py` y retirar `unfixable = ["I001"]`.

Cifras de las fuentes vs. hoy: la fila dice **14** `os.getenv` (medido el 25 oct); el informe dice **15 en 6
módulos contando `alembic/env.py` y sin `main.py`**. Hoy hay **15 en `app/` (6 archivos) + 1 en `alembic/` = 16**.
La llamada nueva es `app/main.py:196` (`CORS_ORIGINS`, SEC1, `9ce0379`).

## Evidencia en el código

### Lecturas de entorno (`os.getenv`): 15 en `app/` + 1 en `alembic/`
- `app/core/security.py:7` — `SECRET_KEY = os.getenv("JWT_SECRET_KEY")` (sin default, sin validación: `str | None`)
- `app/core/security.py:8` — `ALGORITHM = os.getenv("ALGORITHM", "HS256")`
- `app/core/security.py:9` — `ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))`
- `app/core/security.py:10` — `VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", "15"))`
- `app/core/email.py:12` — `MAIL_USERNAME=os.getenv("MAIL_USERNAME")` (sin default)
- `app/core/email.py:13` — `MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")` (sin default)
- `app/core/email.py:14` — `MAIL_FROM=os.getenv("MAIL_FROM", "tu_correo@gmail.com")` (el default que cita el informe; este lo ubicaba en `:15`)
- `app/core/email.py:15` — `MAIL_PORT=int(os.getenv("MAIL_PORT", 465))`
- `app/core/email.py:16` — `MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com")`
- `app/core/storage.py:42` — `os.getenv("AZURE_STORAGE_CONNECTION_STRING")` (en `__init__`, por instancia; valida en `:48-49`)
- `app/core/storage.py:43` — `os.getenv("AZURE_CONTAINER_NAME", "ecotur-images")`
- `app/core/storage.py:44-46` — `os.getenv("AZURE_TEMPORAL_CONTAINER_NAME", "temp-ecotur-images")`
- `app/db/database.py:7` — `DATABASE_URL = os.getenv("DATABASE_URL")` (sin default; se pasa a `create_async_engine` en `:11`)
- `app/api/routers/user.py:66` — `frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")` (lectura de entorno **dentro de un router**, por petición; el informe la ubicaba en `:20`)
- `app/main.py:196` — `CORS_ORIGINS: list[str] = parse_cors_origins(os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS))`
- `app/main.py:193-195` — comentario que documenta la dependencia: "Read at import time with os.getenv … `.env` is already loaded here: app.db.database loads it on import and is imported transitively"
- `alembic/env.py:20` — `database_url = os.getenv("DATABASE_URL")`; valida y falla rápido en `:21-22`

### `load_dotenv()`: 3 llamadas (igual que el informe)
- `app/db/database.py:2,6` — `from dotenv import load_dotenv` / `load_dotenv()`
- `app/core/email.py:4,6` — ídem
- `alembic/env.py:5,14` — ídem
- `app/core/security.py` y `app/core/storage.py` **no** llaman a `load_dotenv()`: dependen de que otro módulo lo haya hecho antes.

### `import os` asociado: 7 archivos
- `app/api/routers/user.py:1`, `app/core/email.py:1`, `app/core/security.py:1`, `app/core/storage.py:1`,
  `app/db/database.py:1`, `app/main.py:1`, `alembic/env.py:2`.

### `pydantic-settings`: declarado, instalado, sin uso
- `pyproject.toml:19` — `"pydantic-settings",` (también `pyproject.toml:23` `"python-dotenv"`)
- Instalado en el venv: `pydantic-settings 2.13.1`, `python-dotenv 1.2.2`.
- `BaseSettings | pydantic_settings | SettingsConfigDict | get_settings` en `app/ tests/ alembic/ scripts/` → **0**.

### Dependencia del orden de imports (motivo del `unfixable`)
- `pyproject.toml:69-72` — comentario + `unfixable = ["I001"]` ("Se retira al cerrar A4").
- `app/api/dependencies.py:6-11` — importa `app.db.database` (`:7`, que ejecuta `load_dotenv()`) **antes** que
  `app.core.security` (`:11`, que lee `JWT_SECRET_KEY` al importar). Ordenar con isort colocaría `app.core.*`
  antes de `app.db.*`.

### Consumidores de las constantes de módulo (lo que el cambio a `Settings` arrastra)
- `app/core/security.py:67,71,83,87` — usan `ACCESS_TOKEN_EXPIRE_MINUTES`, `SECRET_KEY`, `ALGORITHM`, `VERIFICATION_TOKEN_EXPIRE_MINUTES`.
- `app/api/dependencies.py:11` (import) y `:95` — `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`.
- `app/services/user_service.py:16-23` (import de `SECRET_KEY`, `ALGORITHM`) y `:124` — `jwt.decode(token, SECRET_KEY, …)`.
- `app/db/database.py:11` — `create_async_engine(DATABASE_URL, echo=True)` (el `echo=True` es A5, no A4).
- `app/main.py:166,196,200` — `DEFAULT_CORS_ORIGINS`, `CORS_ORIGINS`, `allow_origins=CORS_ORIGINS`.
- `app/core/email.py:11-24` — `conf = ConnectionConfig(...)` y `fast_mail = FastMail(conf)` construidos al importar.
- `tests/test_auth.py:8-13` (import de `ALGORITHM`, `SECRET_KEY`), `:114` `assert SECRET_KEY is not None`, `:115` `jwt.decode(..., SECRET_KEY, ...)`.
- `tests/test_user_service.py:18` (import), `:105` y `:203` `jwt.decode(..., SECRET_KEY, ...)`, `:280` y `:298` `jwt.encode(..., SECRET_KEY, algorithm=ALGORITHM)` a mano (no usan `make_token`).
- `tests/test_main.py:3,49,53-55,59,71,80` — importan y afirman sobre `CORS_ORIGINS` / `DEFAULT_CORS_ORIGINS` de módulo.
- `tests/test_email.py:65` — `patch.object(email_module.fast_mail, "send_message", autospec=True)` (parchea el singleton de módulo).

### Medición en la compuerta (rojo atribuido a A4)
- ruff: 8 × I001 — `app/api/dependencies.py:1`, `app/api/routers/audit.py:1`, `app/core/email.py:1`,
  `app/db/database.py:1`, `app/repositories/user_repository.py:1`, `app/schemas/audit.py:1`,
  `app/services/audit_service.py:1`, `app/services/user_service.py:1`.
- mypy: 9 × `str | None` — `app/db/database.py:11`, `app/core/security.py:71,87`, `app/services/user_service.py:124`,
  `app/api/dependencies.py:95`, `tests/test_user_service.py:105,203,280,298`.

### Precondición de la fila (tests de firma JWT): no existe todavía
- `git grep -i -E "verify_signature|wrong.key|another.key|forged|InvalidSignature"` en `tests/` y `app/` → 0
  resultados relevantes. Ningún test firma un token con otra clave contra `dependencies.py:95` ni contra
  `user_service.py:124`; tampoco hay test que firme con la clave de `.env.example` (`.env.example:19`).
- `tests/conftest.py:206-219` — `make_token(user, *, expires_delta=None)` delega en `create_access_token`; no
  admite clave alternativa ni claims (residual ya anotado en BE-32 (c)).

## Ficheros afectados (mapa completo)
- `app/core/security.py` — 4 `os.getenv` al importar; `SECRET_KEY` sin default ni validación; origen de 2 errores mypy.
- `app/core/email.py` — 5 `os.getenv` + `load_dotenv()`; default `"tu_correo@gmail.com"`; `ConnectionConfig` al importar; I001.
- `app/core/storage.py` — 3 `os.getenv` en `AzureStorageClient.__init__` (valida la cadena de conexión).
- `app/db/database.py` — 1 `os.getenv` + `load_dotenv()` (el que hoy carga `.env` para todos); mypy `:11`; I001.
- `app/api/routers/user.py` — 1 `os.getenv` (`FRONTEND_URL`) en el cuerpo de un handler.
- `app/main.py` — 1 `os.getenv` (`CORS_ORIGINS`) y comentario que remite a A4.
- `app/api/dependencies.py` — consume `SECRET_KEY`/`ALGORITHM`; orden de imports sensible; mypy `:95`; I001.
- `app/services/user_service.py` — consume `SECRET_KEY`/`ALGORITHM`; mypy `:124`; I001.
- `app/api/routers/audit.py`, `app/repositories/user_repository.py`, `app/schemas/audit.py`,
  `app/services/audit_service.py` — solo I001 (asignado a A4 por la regla `unfixable`; no leen entorno).
- `alembic/env.py` — 1 `os.getenv` + `load_dotenv()`; ya valida y falla rápido.
- `pyproject.toml` — `pydantic-settings` declarado (`:19`); `unfixable = ["I001"]` (`:72`).
- `.env.example` — plantilla incompleta e inválida para varias claves (ver rincones).
- `.azure-pipelines/ci-pipeline.yml` — `--soft format,ruff,mypy` (`:30`) y `env:` con `DATABASE_URL`, `JWT_SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`.
- `tests/test_auth.py`, `tests/test_user_service.py`, `tests/test_main.py`, `tests/test_email.py` — importan/parchean constantes de módulo.

## Rincones no mencionados por la fuente
1. **`app/main.py:196` (`CORS_ORIGINS`)** — la llamada 15.ª de `app/`; ni la fila (14) ni el informe (que no
   lista `main.py`) la cuentan. Total real: 15 en `app/` + 1 en `alembic/` = 16.
2. **`tests/test_auth.py:9-10,114-115`** — también importa `SECRET_KEY`/`ALGORITHM` y hace `jwt.decode`; la fila
   A4 solo nombra `tests/test_user_service.py:105,203,280,298`. No sale en mypy porque `:114` hace `assert SECRET_KEY is not None`.
3. **`.env.example` incompleto respecto al código:** define 13 claves (`POSTGRES_*` ×5, `DATABASE_URL`, 4 de JWT,
   `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME`, `CORS_ORIGINS`) y **no** define `MAIL_USERNAME`,
   `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_PORT`, `MAIL_SERVER`, `FRONTEND_URL` ni `AZURE_TEMPORAL_CONTAINER_NAME`.
   `fastapi_mail.ConnectionConfig` (`venv/Lib/site-packages/fastapi_mail/config.py:9-17`) es a su vez un
   `Settings` de pydantic con `MAIL_USERNAME: str`, `MAIL_PASSWORD: SecretStr`, `MAIL_FROM: EmailStr`;
   `email.py:12-13` le pasa `None` explícito si faltan. Por lectura (no ejecutado): un entorno montado solo con
   `.env.example` fallaría al importar `app.core.email`, es decir, al importar la app.
4. **`.env.example:20-22` con valores no válidos como ejemplo:** `ALGORITHM=x`,
   `ACCESS_TOKEN_EXPIRE_MINUTES=tiempo_en_minutos`, `VERIFICATION_TOKEN_EXPIRE_MINUTES=tiempo_en_minutos`.
   Copiados literalmente, `security.py:9-10` lanza `ValueError` en `int(...)` al importar. Y `.env.example:19`
   trae una clave JWT con aspecto real (`ecotur_secreto_super_seguro_2026`), la que la fila pide rechazar con test.
5. **La suite depende de `.env` o del `env:` del CI:** `tests/conftest.py` no fija variables (0 `setenv` sobre
   configuración en `tests/`); importa `app.db.database` (`conftest.py:14`), que llama
   `create_async_engine(DATABASE_URL)` al importar (`database.py:11`), aunque los tests usen su propio engine
   SQLite (`conftest.py:18-23`). El CI inyecta `DATABASE_URL`, `JWT_SECRET_KEY` y `MAIL_*`
   (`ci-pipeline.yml`, bloque `env:` del paso de la compuerta); en local los aporta `.env`.
6. **`storage.py` y `alembic/env.py` sí validan** (`storage.py:48-49`, `alembic/env.py:21-22`), como dice el
   informe; `security.py`, `database.py` y `email.py` no.

## Patrones de detección (copiables)
```bash
# lecturas de entorno (meta: 0 fuera del módulo de configuración)
git grep -n -E "os\.getenv|os\.environ|getenv\(|environ\[|environ\.get" -- app alembic tests scripts
# load_dotenv repartido (meta: 0 en app/; alembic según decida el plan)
git grep -n -E "load_dotenv|from dotenv" -- app alembic tests
# uso de pydantic-settings (meta: ≥ 1 en app/)
git grep -n -E "BaseSettings|pydantic_settings|SettingsConfigDict" -- app tests alembic
# consumidores de constantes de módulo de configuración
git grep -n -E "\bSECRET_KEY\b|\bALGORITHM\b|ACCESS_TOKEN_EXPIRE_MINUTES|VERIFICATION_TOKEN_EXPIRE_MINUTES|\bDATABASE_URL\b|\bCORS_ORIGINS\b" -- app tests alembic
# default de correo heredado
git grep -n "tu_correo@gmail.com" -- app tests .env.example
# regla I001 y --soft (meta: desaparecen al cerrar)
git grep -n -E "unfixable" -- pyproject.toml
git grep -n -- "--soft" -- .azure-pipelines
# rojo de la compuerta atribuido a A4
./venv/Scripts/python.exe -m ruff check app tests --select I001
./venv/Scripts/python.exe -m mypy
# precondición: tests de firma con otra clave (meta: ≥ 2, uno por ruta de jwt.decode)
git grep -n -i -E "verify_signature|wrong.?key|other.?key|forged|InvalidSignature" -- tests
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `8cea834` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop` = `8cea8341…`; rama `item/a4`, árbol limpio)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Python 3.14.3) → exit 1

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

- ruff format: `57 files already formatted` (OK).
- ruff check: `Found 8 errors.` — los 8 son I001 (lista arriba).
- mypy: `Found 9 errors in 5 files (checked 53 source files)` — los 9 son `str | None` de configuración (lista arriba).
- import-linter: `Contracts: 4 kept, 0 broken.` (4 KEPT, 0 BROKEN).
- docs: `Documentación coherente` (OK).
- pytest: `549 passed, 5 warnings in 19.28s` (0 failed); cobertura total **96.11 %** (mínimo 92.0 %).
- **La compuerta ya falla antes de tocar nada**, y todo su rojo (8 ruff + 9 mypy) corresponde al conjunto de A4.

## Conclusión para el planificador
El plan debe centralizar las 15 lecturas de `app/` en un único `Settings` (`pydantic-settings`, ya instalado)
validado al arrancar, con `JWT_SECRET_KEY` y `DATABASE_URL` obligatorios (sin default), y migrar a él los
consumidores listados (`security.py`, `dependencies.py:95`, `user_service.py:124`, `database.py`, `email.py`,
`storage.py`, `routers/user.py:66`, `main.py:196`) y los tests que importan constantes (`test_auth.py`,
`test_user_service.py`, `test_main.py`, `test_email.py`). Antes de tocar `jwt.decode`, la precondición de la
fila: dos tests de caracterización con clave ajena (401 en `dependencies.py`, error de dominio/400 en
`user_service.py`) más el de la clave de `.env.example`. Al final: retirar `unfixable` y aplicar I001 (8),
dejar mypy en 0, migrar `test_user_service.py:280,298` a `make_token` o equivalente, y completar/corregir
`.env.example` (`MAIL_*`, `FRONTEND_URL`, `AZURE_TEMPORAL_CONTAINER_NAME`, valores de `:20-22`).
No tocar: `echo=True` y ciclo de vida del engine (A5), `sqlalchemy.future` de `user_repository.py` más allá
del I001 (S2), quitar `--soft` del YAML (CI duro, decisión aparte). Riesgos: el orden de carga (que `.env` se
lea una sola vez y antes de cualquier constante), que la suite pase a depender de que `.env`/CI definan
variables que hoy tienen default (decidir si el conftest fija valores de test), `alembic/env.py` (decidir si
usa el mismo `Settings` o se deja, ya valida) y `tests/test_email.py:65`, que parchea el `fast_mail` de módulo.
Son ≥ 12 archivos: necesita varias fases de ≤ 5.

## Adenda — decisiones de David antes de planear (10 nov 2026, 10:42 y 11:03, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir.

1. **Veredicto aceptado: confirmada. Línea base aceptada:** sobre `8cea834` (= `origin/develop`), 549 passed · 96,11 % ·
   ruff 8 (I001) · mypy 9 (`str | None`) · `Contracts: 4 kept, 0 broken.` · `check_docs` 0. **Meta del ítem: compuerta en
   verde completa (ruff 0 · mypy 0 · 4 kept), sin `--soft` local.** Hasta la última fase rige el trinquete de ADR-0005
   (los totales no crecen; cero errores nuevos en lo tocado).
2. **Fe de erratas del rincón 5:** "0 `setenv` sobre configuración en `tests/`" es falso. `tests/test_storage.py:55-57`
   hace `monkeypatch.setenv` de `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME` y
   `AZURE_TEMPORAL_CONTAINER_NAME`, y funciona porque `app/core/storage.py:42-46` lee el entorno en `__init__`, por
   instancia. Con la configuración leída una sola vez, ese `setenv` llega tarde: el plan dice cómo queda ese test (y
   cualquier otro que cambie configuración) sin perder lo que prueba.
3. **Los dos tests de firma son la fase A del plan** (CONTEXT §8.1; fila A4), no se escriben a mano: token firmado con
   otra clave → 401 por `app/api/dependencies.py:95` y 400 por `app/services/user_service.py:124`, cada uno con el
   mutante `verify_signature=False` en copia, medido por el ejecutor y repetido por el auditor. Tercer test: token
   firmado con la clave literal de `.env.example:19` → 401. **Límite que el plan declara:** el CI usa una clave fija
   distinta (`.azure-pipelines/ci-pipeline.yml:34`), así que ese test protege a quien copie el ejemplo en local, no a
   producción.
4. **Campos obligatorios, sin valor por defecto** (David: "que falle ruidoso en lugar de cargar valores por defecto
   que inducen a fallos silenciosos"): `JWT_SECRET_KEY`, `DATABASE_URL`, `MAIL_USERNAME`, `MAIL_PASSWORD` y
   `AZURE_STORAGE_CONNECTION_STRING`. Si falta uno, la app no arranca y el error nombra la variable. **Conservan su
   valor por defecto actual:** `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `VERIFICATION_TOKEN_EXPIRE_MINUTES`,
   `MAIL_PORT`, `MAIL_SERVER`, `AZURE_CONTAINER_NAME`, `AZURE_TEMPORAL_CONTAINER_NAME`, `FRONTEND_URL`, `CORS_ORIGINS`.
   **`MAIL_FROM` es opcional y, si no está definida, vale `MAIL_USERNAME`** (David, 11:03). El valor
   `"tu_correo@gmail.com"` (`app/core/email.py:14`) desaparece del código. Razón, con evidencia de David: un correo de
   verificación real (27 jul 2026, enviado por un entorno desplegado que no define `MAIL_FROM`) muestra como remitente
   la cuenta de `MAIL_USERNAME`, no el valor por defecto: el SMTP de Gmail pone la cuenta autenticada. Hacerla
   obligatoria exigiría añadir en tres Web Apps una variable que hoy no cambia lo que ve el destinatario; derivarla
   quita el valor basura sin tocar Azure, y el día que haya dominio propio basta con definirla. Si `MAIL_USERNAME` no
   es una dirección válida y `MAIL_FROM` falta, la app no arranca (validación de `fastapi_mail`), que es lo deseado.
5. **Inventario de las tres Web Apps (capturas de David del portal, 10 nov, solo nombres):** `develop`, `staging` y
   `main` definen las mismas diez variables de la aplicación: `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`,
   `AZURE_CONTAINER_NAME`, `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_TEMPORAL_CONTAINER_NAME`, `DATABASE_URL`,
   `FRONTEND_URL`, `JWT_SECRET_KEY`, `MAIL_PASSWORD`, `MAIL_USERNAME` (más las de plataforma `DOCKER_*` y `WEBSITES_*`).
   **No definen** `MAIL_FROM`, `MAIL_PORT`, `MAIL_SERVER`, `VERIFICATION_TOKEN_EXPIRE_MINUTES` ni `CORS_ORIGINS`. Las
   cinco obligatorias del punto 4 existen en las tres: **el merge de A4 no exige ningún cambio en Azure.** Es la
   condición que el plan debe conservar: ninguna fase convierte en obligatoria una variable fuera de esas cinco.
   `CORS_ORIGINS` sigue siendo la puesta en `staging` `(PLAN §3)`, no este ítem.
6. **El bloque `env:` del CI entra en el alcance** (`ci-pipeline.yml:32-36`; hoy `DATABASE_URL`, `JWT_SECRET_KEY`,
   `MAIL_USERNAME`, `MAIL_PASSWORD`): falta `AZURE_STORAGE_CONNECTION_STRING`, que pasa a obligatoria; se añade un
   valor ficticio, o ninguno si el punto 7 hace que la suite no lo necesite; el plan elige y lo justifica.
   **`--soft` (`ci-pipeline.yml:30`) no se toca en este ítem:** es el CI duro, después del merge.
7. **La suite deja de depender de `.env`** `(PLAN §2b, celda de B-TESTS)`. Criterio de aceptación: la suite pasa en
   verde sin `.env` presente y sin las variables del `env:` del CI que no sean imprescindibles. El plan dice cómo se
   mide **sin leer ni copiar `.env`** (AGENTS §2).
8. **Acceso a la configuración: `get_settings()` cacheado, e inyección por `Depends` donde hay petición.** Un módulo de
   configuración en `app/core/` (sin importar FastAPI: lo usan `core`, `db` y servicios) con la clase `Settings` y
   `get_settings()` con caché. En la capa HTTP se inyecta con `Depends(get_settings)` en la fábrica que ya existe
   (`app/api/dependencies.py`: `get_current_user` `:95`, `get_storage_client` `:62`) y en `app/api/routers/user.py:66`.
   Donde no hay petición (`app/db/database.py:11`, `app/main.py:196-204`, `app/core/email.py:11-24`,
   `app/core/security.py:67-87`) se llama a `get_settings()` directamente. Ningún `os.getenv` ni constante de módulo de
   configuración queda fuera de ese módulo. El plan cita la página de FastAPI sobre settings en Referencias y dice
   cómo limpian la caché los tests que cambian configuración.
9. **`alembic/env.py` usa el mismo `Settings`** (ya importa `app.db.database`, `:12`). Coste aceptado: correr
   migraciones exige la configuración completa, no solo `DATABASE_URL`.
10. **A medir por el planificador con sonda, no por lectura** (pydantic-settings 2.13.1, con un `.env` temporal propio,
    nunca el real): (a) el `.env` de David tiene `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`,
    `POSTGRES_PORT` (las usa `docker-compose.yml:11,26-28`), claves que `Settings` no declara: qué hace `Settings` con
    claves de más en el archivo y qué configuración las tolera; (b) su `DATABASE_URL` se compone con `${POSTGRES_USER}`…
    como `.env.example:14`: si la lectura del archivo por `Settings` expande esas referencias igual que `load_dotenv()`
    hoy. **Dos mecanismos posibles; el `.env` de David no cambia en ninguno:** (1) `Settings` lee el archivo
    (`env_file`); (2) una única llamada a `load_dotenv()` en el módulo de configuración, antes de construir `Settings`,
    y `Settings` lee solo el entorno del proceso (es lo que hoy hace `app/db/database.py:6`, movido a un solo sitio).
    Si (a) o (b) falla con (1), el plan usa (2) y lo justifica. En Azure y en el CI no hay `.env`: las variables llegan
    por el entorno del proceso con cualquiera de los dos.
11. **`.env.example` completo y válido:** las siete claves que faltan (`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`,
    `MAIL_PORT`, `MAIL_SERVER`, `FRONTEND_URL`, `AZURE_TEMPORAL_CONTAINER_NAME`) y valores de ejemplo válidos en `:20-22`
    (rincones 3 y 4). La clave de `:19` se queda: es la que el tercer test del punto 3 rechaza.
12. **Resto de CONTEXT §8.1:** los dos `jwt.encode` a mano de `tests/test_user_service.py:280,298` migran a `make_token`
    (`tests/conftest.py:206-219`; si hace falta ampliar su firma, el plan lo dice); `tests/test_auth.py:10,114-115` entra
    en el mismo conjunto (rincón 2). `CORS_ORIGINS` conserva su nombre (contrato con `.env.example` y con las Web Apps).
    Última fase: `unfixable = ["I001"]` fuera de `pyproject.toml:72` e I001 aplicado, con la suite en verde antes y
    después (es la prueba de que el orden de imports ya no decide nada).
13. **Fuera de alcance:** `echo=True` y el ciclo de vida del engine (A5); `sqlalchemy.future` (S2); retirar `--soft`;
    `CORS_ORIGINS` en Azure; que `develop` y `staging` compartan el mismo `JWT_SECRET_KEY` (dato de David, 10 nov:
    ninguna Web App usa la clave de `.env.example`; la rotación es operación, se anota en el cierre).

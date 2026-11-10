# ADR-0013 — Configuración centralizada: un `Settings` de pydantic-settings, leído una vez y validado al arrancar

- **Estado:** aceptado (David, 10 nov 2026, al aprobar el plan de A4 con E0)- **Propuesta:** Claude, `plan-redactor` (10 nov 2026)
- **Ubicación en el repo:** `docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md`
- **Origen:** backlog A4; `docs/deuda/A4/verificacion.md` (veredicto y adenda de David, 10 nov); `docs/deuda/A4/plan.md`

## Contexto

La configuración se leía con `os.getenv` en 15 sitios de `app/` (6 archivos) y uno de `alembic/`, casi todos al importar
el módulo, sin validación. `.env` se cargaba con `load_dotenv()` en tres módulos, y `app/core/security.py` leía
`JWT_SECRET_KEY` sin cargarlo: funcionaba solo si otro módulo se importaba antes. Por eso ruff no puede ordenar imports
(`unfixable = ["I001"]`). `JWT_SECRET_KEY` ausente era `None` y el fallo salía en la primera petición; `MAIL_FROM` tenía
un valor por defecto de plantilla (`tu_correo@gmail.com`); la suite fallaba al importar si no había `.env` ni variables
del CI. `pydantic-settings` estaba declarado e instalado, pero no se usaba.

## Decisión

1. **Un único módulo, `app/core/config.py`** (sin FastAPI), con `Settings` (un campo por variable de entorno) y
   `get_settings()` con `functools.lru_cache`. Ningún otro módulo lee el entorno ni guarda constantes de configuración.
2. **Obligatorias sin valor por defecto y no vacías:** `DATABASE_URL`, `JWT_SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`
   y `AZURE_STORAGE_CONNECTION_STRING`. Si falta una, la app no arranca y el error nombra el campo. Las demás conservan
   el valor por defecto que tenían. `MAIL_FROM` es opcional y, si falta, el remitente es `MAIL_USERNAME`.
3. **Fuentes:** el entorno del proceso y, si existe, el `.env` de la raíz del repositorio, ubicado por la ruta del
   módulo y no por el directorio de trabajo. El entorno del proceso gana. `extra="ignore"` tolera las claves del `.env`
   que la app no declara (`POSTGRES_*`, de `docker-compose.yml`); las referencias `${VAR}` se expanden como antes.
   `hide_input_in_errors=True` evita que un error de arranque imprima valores (secretos) en el log.
4. **Acceso:** en la capa HTTP, `Depends(get_settings)` (`get_current_user`, `get_storage_client`, el registro de
   turistas). Donde no hay petición (motor de BD, cliente SMTP, fábrica de tokens, servicio de usuarios, CORS) se llama a
   `get_settings()` directamente.
5. **Migraciones:** `DatabaseSettings` (solo `database_url`), de la que hereda `Settings`, con su propio
   `get_database_settings()`. La usan `app/db/database.py` y `alembic/env.py`. Así `alembic upgrade head` sigue
   funcionando con `DATABASE_URL` sola, como lo ejecuta el CD (`docker run -e DATABASE_URL=… alembic upgrade head`).
6. **Suite:** un `conftest.py` en la raíz, que pytest carga antes que `tests/conftest.py`, fija en el entorno del
   proceso un valor de prueba para cada campo. La suite no depende de `.env` ni de las variables del CI.

## Consecuencias

- Una variable obligatoria que falte o que tenga un valor inválido detiene el arranque, no la primera petición. En
  local, el `.env` debe definir las cinco obligatorias. Las tres Web Apps ya las definen.
- Los valores se leen una vez por proceso. `FRONTEND_URL` y las de Azure Storage, que antes se releían en cada petición,
  ahora exigen reiniciar la app (Azure la reinicia al cambiar la configuración).
- Cómo cambia la configuración un test: (a) para probar `Settings`, se construye `Settings(_env_file=None)` con
  `monkeypatch.setenv`/`delenv`; (b) para probar un consumidor HTTP, se usa
  `app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(update={...})`, y el fixture `client`
  limpia el override; (c) un consumidor sin petición recibe `Settings` como argumento en su test. Ningún test cambia el
  entorno de un lector directo. Si alguno lo necesitara, llamaría a `get_settings.cache_clear()` antes y después.
- El orden de los imports ya no decide qué configuración se carga: `unfixable = ["I001"]` desaparece.

## Alternativas consideradas

1. **`load_dotenv()` una sola vez en el módulo de configuración y `Settings` solo del entorno.** Es equivalente. Se
   descarta porque, con `extra="ignore"`, `env_file` tolera las claves de más y expande `${VAR}`, medido con sonda sobre
   pydantic-settings 2.13.1. Así basta un mecanismo en lugar de dos.
2. **Un solo `Settings` también para Alembic** (adenda 9 al pie de la letra). Se descarta: `alembic/env.py` importa
   `app.models` → `app.db.database`, que crea el motor al importar, y el paso de migraciones del CD pasaría a exigir
   cuatro secretos que hoy no recibe. Habría que cambiar el pipeline y los grupos de variables.
3. **Inyectar `Settings` en el constructor de `UserService`.** Es más puro, pero cambia la firma que construyen decenas
   de tests. El servicio llama a `get_settings()`, igual que el resto de código sin petición.
4. **`SecretStr` para los secretos.** Se aplaza (Residuales del plan): obliga a llamar a `get_secret_value()` en cada
   consumidor, y el riesgo que cubre en los logs ya lo cubre `hide_input_in_errors`.

## Evidencia

- Sonda del 10 nov (pydantic-settings 2.13.1, `.env` temporal propio, nunca el real): con el `extra` por defecto,
  5 errores `extra_forbidden` por `POSTGRES_*`; con `extra="ignore"`, `DATABASE_URL=${POSTGRES_USER}…` se expande
  igual que con `load_dotenv()`; el entorno del proceso gana al archivo. Sin `hide_input_in_errors`, el error de un
  campo ausente imprime los valores leídos en `input_value`.
- Suite exportada con `git archive` sin `.env` y sin variables del CI, sobre `55345a1`: falla al recoger los tests
  (`sqlalchemy.exc.ArgumentError: Expected string or URL object, got None`).
- `alembic upgrade head --sql` con solo `DATABASE_URL`, sobre la misma exportación: exit 0 (116 líneas de SQL).
- Documentación: FastAPI, "Settings and Environment Variables"; pydantic-settings, "Dotenv (.env) support". Enlaces
  en `docs/deuda/A4/plan.md`, sección Referencias.

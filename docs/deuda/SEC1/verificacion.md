# Verificación — SEC1: CORS `*` con credenciales

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A2, fila SEC1, línea 89) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` (línea 983)
**Fecha:** 2026-11-02

## Qué describe el ítem
`CORSMiddleware` se registra con `allow_origins=["*"]` y `allow_credentials=True`. Starlette resuelve esa
combinación reflejando el `Origin` del solicitante, así que cualquier sitio web puede hacer peticiones con
credenciales y leer la respuesta. El informe lo acota: hoy la auth va por cabecera `Bearer`, no por cookie,
pero deja de estarlo si se añaden cookies. Los orígenes deben venir de configuración y enumerarse.
Backlog: Alta · XS · entra en `B-HIGIENE`; métrica "**1** `allow_origins=["*"]`".

## Evidencia en el código
- `app/main.py:163-169` — único registro de CORS:
  `app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])`
- `app/main.py:3` — `from fastapi.middleware.cors import CORSMiddleware` (único import).
- `app/api/dependencies.py:23` — `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")`: la auth es
  por cabecera Bearer. Grep de `set_cookie|Cookie` en `app/`, `tests/`, `alembic/`: 0 resultados. El impacto
  actual es el acotado que describe el informe (sin cookies).
- El informe ubica la deuda en `app/main.py:93-99`; hoy está en `:163-169` (el fichero creció). Misma deuda.
- No existe ninguna configuración de orígenes: `.env.example` no tiene variable CORS (solo `POSTGRES_*`,
  `DATABASE_URL`, JWT, Azure). No hay `Settings`/`BaseSettings` en el código; `pydantic-settings` está en
  `pyproject.toml:19` pero no se importa en ningún `.py`. El proyecto lee la config con `os.getenv` +
  `load_dotenv()` disperso (`app/db/database.py:6-7`, `app/core/security.py:7-10`, `app/core/email.py:12-16`,
  `app/core/storage.py:42-44`, `app/api/routers/user.py:66`).
- `app/api/routers/user.py:66` — `os.getenv("FRONTEND_URL", "http://localhost:3000")` es lo más parecido a un
  origen configurado, pero se usa para el enlace del correo. En el `.env` local (no copiado aquí) el valor
  incluye ruta/fragmento (`.../#`), por lo que NO sirve tal cual como origen CORS (un origen es esquema+host+puerto).
- Tests: ninguno prueba CORS. `tests/test_main.py` solo tiene `test_read_root`. Grep de
  `access-control|Origin|cors` en `tests/`: 0 coincidencias (las coincidencias de `allowed` en `test_user_access_policy.py` son
  falsos positivos de un grep amplio). El cliente de prueba (`tests/conftest.py:57-68`) usa
  `AsyncClient(transport=ASGITransport(app=app))`, o sea ejercita el `app` real con su middleware.

## Ficheros afectados (mapa completo)
- `app/main.py` — línea 163-169: el middleware con `*` + credenciales (único sitio de la deuda).
- `.env.example` — no declara variable de orígenes; habrá que documentarla (no es deuda por sí misma, es consecuencia de la corrección).
- `tests/test_main.py` — hogar natural para los tests de CORS (hoy 1 test).
- `app/api/routers/user.py:66` — NO es deuda; solo se señala porque lee `FRONTEND_URL` y puede confundirse con un origen.

## Rincones no mencionados por la fuente
- `allow_methods=["*"]` y `allow_headers=["*"]` (`app/main.py:167-168`) también son comodines; el informe solo cita
  `allow_origins`. No son la vulnerabilidad (con orígenes explícitos el riesgo cae), pero quedan abiertos.
- Con `allow_origins` explícitos, `allow_credentials=True` deja de ser reflejo universal. Con Bearer no es
  imprescindible; es decisión del planificador mantenerlo o ponerlo a `False`.
- `app.add_middleware` fija los argumentos al importar `app.main`: la lectura de la variable debe hacerse en ese
  momento (import time), lo que condiciona cómo se testea (ver conclusión).
- Fuera del repo (frontend Flutter): el origen real de desarrollo/producción no consta en el backend; hay que
  preguntarlo a David. Flutter móvil/escritorio no usa CORS; solo Flutter web.

## Patrones de detección (copiables)
```
grep -rnE "allow_origins|allow_credentials|CORSMiddleware" app tests alembic --include=*.py
grep -rnE "allow_origins=\[\"\*\"\]" app tests alembic --include=*.py      # esperado hoy: 1; objetivo: 0
grep -rnE "allow_(methods|headers)=\[\"\*\"\]" app --include=*.py          # esperado hoy: 2
grep -rniE "set_cookie|Cookie" app tests alembic --include=*.py            # esperado: 0 (auth solo Bearer)
```
(Con Grep/ripgrep en Windows el mismo patrón sirve: `allow_origins=\["\*"\]`.)

## Línea base (python scripts/check.py)
- Base develop: `7c6d606` (`git fetch origin` OK; `merge-base HEAD origin/develop` == `rev-parse origin/develop` == `7c6d606405157c56872166df2506a3f35b611fd0`; rama `bloque/b-higiene`).
- Comando: `venv/Scripts/python.exe scripts/check.py` desde la raíz del repo. Nota: `python` a secas (Python 3.14 del
  sistema) no tiene las dependencias (sin `jwt`, `mypy`, `importlinter`) y falla por entorno, no por código; hay que
  usar el intérprete del `venv/` del repo.
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
- pytest: `317 passed, 1 warning in 17.87s` (0 failed). Cobertura total: **92.68%** (mínimo exigido 92.0%).
- ruff check: **Found 98 errors** (19 fixables con `--fix`). ruff format --check: OK.
- mypy: **Found 44 errors in 12 files** (checked 35 source files).
- import-linter: **4 kept, 0 broken** (Capas; servicios sin HTTP; repositorios solo SQLAlchemy/modelos; modelos/schemas sin capas superiores).
- **La compuerta ya falla antes de tocar nada** (ruff check y mypy) por deuda previa, no por SEC1. Los bloques
  de ruff/mypy relevantes a `app/main.py`: la bitácora del 2-nov (l.316) registra que `app/main.py` pasa ruff
  limpio sin I001; no se re-midió por separado. El ejecutor debe comparar contra estos totales (98 / 44), no
  contra cero.

## Conclusión para el planificador
- Resolver: sustituir `allow_origins=["*"]` (`app/main.py:165`) por una lista explícita leída de configuración
  (variable de entorno nueva, p. ej. lista separada por comas, documentada en `.env.example`, con un valor por
  defecto seguro para desarrollo local y SIN comodín). Decidir además si se acotan `allow_methods`/`allow_headers`
  y si `allow_credentials` se mantiene (auth es Bearer).
- Decisión abierta para David: los orígenes reales (dev/prod, Flutter web). No inventarlos. Y no reutilizar
  `FRONTEND_URL` tal cual (puede traer ruta/fragmento y su semántica es el enlace del correo).
- Tests (RED primero) en `tests/test_main.py`: origen permitido recibe `access-control-allow-origin` con ese
  origen; origen no permitido NO lo recibe (ni reflejado); preflight OPTIONS; con `*` prohibido. Como los
  argumentos se fijan al importar `app.main`, probar con una función que construya la lista (parseo testeable
  de forma pura) o con un helper de fábrica, no recargando módulos.
- NO tocar: `app/api/routers/user.py:66`, la auth Bearer, ni la deuda de ruff/mypy preexistente (98/44) ni
  I001 de otros ficheros (otros ítems de `B-HIGIENE`). No introducir `pydantic-settings`/`Settings` en este
  ítem si implica migrar el resto de la config (alcance XS; se dispararía a otro ítem).
- Riesgo: un origen mal escrito rompe el frontend web sin que ningún test del backend lo detecte; coordinar con el cliente.

## Adenda — decisiones de David antes de planear (2 nov 2026, sesión Mentor)

Resuelve las "decisiones abiertas" de la conclusión. El planificador las toma como dadas; lo demás (fases, tests,
commits) es suyo.

1. **`allow_credentials=False`.** En CORS, "credenciales" son cookies, HTTP auth y certificados de cliente; la
   cabecera `Authorization: Bearer` que pone el cliente no lo es (solo exige preflight). No hay cookies en el repo.
   La autenticación no cambia. Si el ADR de BE-12 eligiera refresh token en cookie, vuelve a `True` con orígenes
   explícitos.
2. **`allow_methods` y `allow_headers` quedan en `*`: fuera de alcance.** Con lista blanca de orígenes solo afectan a
   los sitios permitidos; acotarlos puede romper el cliente sin que ningún test del backend lo detecte. Residual de
   SEC1 con nombre en el backlog al cierre.
3. **Lectura de configuración:** variable nueva `CORS_ORIGINS` (lista separada por comas), leída con `os.getenv` en
   `app/main.py` con comentario `(backlog A4)`. Sin módulo nuevo ni `pydantic-settings`: eso es A4. Parser puro,
   testeable por import, que recorta, descarta vacíos y **rechaza `*` con `ValueError` al arrancar**. No derivar de
   `FRONTEND_URL` (otro propósito: enlace del correo; su valor local trae ruta y fragmento).
4. **Orígenes reales.** Flutter móvil (emulador con `10.0.2.2` o físico) y Postman no envían `Origin`: el
   middleware los deja pasar sin mirarlos (`starlette/middleware/cors.py:86-88`, Starlette 1.3.1); CORS solo aplica a
   Flutter **web**. Local: David fija `--web-port=3000` en la run configuration de IntelliJ; valor por defecto de
   desarrollo y `.env.example`: `http://localhost:3000` (elegido sobre `allow_origin_regex`: una variable menos y
   nada que no deba llegar a producción). Cada API de Azure recibe **solo su propio frontend** en `CORS_ORIGINS`
   (Azure Static Web Apps; la variable va junto a la `FRONTEND_URL` que ya tiene cada Web App for Containers):
   - `develop`: `https://nice-tree-0c72d630f.7.azurestaticapps.net`
   - `staging`: `https://kind-dune-011dee50f.7.azurestaticapps.net`
   - `main`: `https://wonderful-tree-0c5f28e0f.7.azurestaticapps.net`
   Las URLs de Azure no van en el código ni en `.env.example`; van en la configuración de cada Web App.
5. **Riesgo fuera del alcance de los tests:** sin `CORS_ORIGINS` en una Web App, la API arranca con el default local
   y el PWA de ese entorno deja de funcionar, visiblemente. Lo pone David en las tres Web Apps antes del PR a
   `staging`; la descripción del PR lo recuerda.
6. **Criterio de aceptación para todos los planes de `B-HIGIENE`:** I001 tolerado en archivos tocados hasta A4
   (bitácora 2026-11-02: el hook y `check.py --fix` no deben reordenar imports mientras `security.py` lea el entorno
   al importar). `app/main.py` hoy no tiene I001 pendiente.

# PLAN — SEC1: Sustituir el comodín de CORS por una lista blanca configurada y retirar las credenciales

- **Fecha:** 2026-11-02 · **Fuente:** `verificacion.md` (confirmada, con adenda de decisiones de David del 2 nov) ·
  **Rama:** `bloque/b-higiene`
- **Base develop:** `7c6d606` (la de la verificación; el ejecutor la re-comprueba en su ritual de arranque)

## Resumen para aprobación

Hoy `app/main.py:163-169` registra `CORSMiddleware` con `allow_origins=["*"]` y `allow_credentials=True`; Starlette
resuelve esa pareja reflejando el `Origin` de quien llama, así que cualquier sitio web puede invocar la API con
credenciales y leer la respuesta. Se cambia por una lista explícita leída de una variable nueva `CORS_ORIGINS` (separada
por comas, default `http://localhost:3000`), parseada por una función pura `parse_cors_origins` en el propio `app/main.py`
que recorta, descarta vacíos y rechaza cualquier comodín con `ValueError` al arrancar; `allow_credentials` pasa a `False`
(la auth es `Authorization: Bearer`, que no es una credencial CORS). Una sola fase, tres archivos (`app/main.py`,
`tests/test_main.py`, `.env.example`), un commit `fix(cors)`. Riesgo principal: no es de código sino de despliegue; sin
`CORS_ORIGINS` en una Web App la API arranca con el default local y el PWA de ese entorno deja de funcionar; lo gestiona
David antes del PR a `staging` y la descripción del PR lo recuerda. NO se tocan `allow_methods`/`allow_headers` (quedan
en `*`, residual con nombre), ni `FRONTEND_URL`, ni la auth, ni se introduce `pydantic-settings` ni módulo nuevo (eso es A4).
No hace falta ADR nuevo.

## Objetivo y decisiones bloqueadas

Que ningún origen no enumerado reciba `Access-Control-Allow-Origin` y que la API nunca anuncie credenciales CORS, con la
lista de orígenes fuera del código y un arranque que falla ruidosamente ante un comodín.

1. `allow_credentials=False` (adenda, decisión 1). Si BE-12 eligiera refresh token en cookie, vuelve a `True` con orígenes
   explícitos; eso es otro ítem.
2. `allow_methods=["*"]` y `allow_headers=["*"]` **no se tocan** (decisión 2). Residual con nombre en el backlog al cierre.
3. Variable `CORS_ORIGINS`, lista separada por comas, leída con `os.getenv` en `app/main.py` con comentario `(backlog A4)`.
   Sin módulo nuevo, sin `pydantic-settings`, sin `load_dotenv()` nuevo. Parser puro e importable que recorta, descarta
   vacíos y rechaza `*` con `ValueError` al arrancar. No se deriva de `FRONTEND_URL` (decisión 3).
4. Default en código y en `.env.example`: `http://localhost:3000`. Las URLs de Azure Static Web Apps no entran ni en el
   código ni en `.env.example` (decisión 4).
5. El despliegue (variable en las tres Web Apps for Containers) lo hace David; el PR lo recuerda (decisión 5).
6. Criterio de aceptación de `B-HIGIENE` (decisión 6): pytest verde, cobertura ≥ 92.68 %, totales de ruff ≤ 98 y de mypy ≤ 44
   (hoy la compuerta ya falla por deuda previa), 0 errores de ruff/mypy en los archivos tocados, I001 tolerado en archivos
   tocados (no aplica: `app/main.py` no tiene I001 y `tests/test_main.py` no tiene imports hoy).
7. Compuerta y tests con `venv/Scripts/python.exe`, nunca con el Python del sistema (verificación, línea base).

## Análisis del redactor

**Qué se cambia y por qué.** Verificado hoy contra el código: `app/main.py:163-169` es el único registro de
`CORSMiddleware` (único import en `:3`); no existe ninguna variable de orígenes en `.env.example`; ningún test toca CORS
(`tests/test_main.py` tiene solo `test_read_root`); la auth es Bearer (`app/api/dependencies.py:23`) y no hay cookies en
`app/`, `tests/` ni `alembic/`. En el código fuente instalado de Starlette 1.3.1 (`venv/Lib/site-packages/starlette/middleware/cors.py`)
el comportamiento que el plan explota es exacto: (a) sin cabecera `Origin` el middleware no interviene (`__call__`:
`if origin is None: await self.app(...)`), que es el camino de Postman y de Flutter móvil; (b) `is_allowed_origin` compara
por igualdad de cadena (`origin in self.allow_origins`): una barra final o una ruta en la lista hacen que el origen nunca
case; (c) en respuestas normales, con `allow_origins` explícitos y `allow_credentials=False`, el origen se devuelve solo si
está en la lista (`send()`: rama `elif not self.allow_all_origins and self.is_allowed_origin(origin)`), añadiendo
`Vary: Origin`; si no está, no se añade ninguna cabecera CORS y la petición se sirve igual (el navegador es quien bloquea);
(d) el preflight (`OPTIONS` + `Access-Control-Request-Method`) responde `200` con el origen cuando está permitido y `400`
(`Disallowed CORS origin`) cuando no; (e) `Access-Control-Allow-Credentials: true` solo se emite si `allow_credentials=True`,
tanto en preflight como en respuestas normales. Con la combinación actual (`*` + `True`), la rama
`if self.allow_all_origins and self.allow_credentials: self.allow_explicit_origin(headers, origin)` refleja cualquier
origen: esa línea es la vulnerabilidad.

**Por qué el parser vive en `app/main.py` y se lee al importar.** `app.add_middleware` fija los argumentos cuando se
importa `app.main`, y `tests/conftest.py:13` importa ese `app` real (`ASGITransport(app=app)`), así que los tests de
integración ejercitan la configuración vigente en el proceso de pytest (en CI y en local sin `.env` que la cambie:
`http://localhost:3000`); no se recargan módulos. El valor de la variable se lee en el cuerpo del módulo, **después** del
bloque de imports: `app.main:7` importa `app.api.routers`, que importa `app.api.dependencies`, que importa
`app.db.database`, donde vive `load_dotenv()` (`app/db/database.py:6`). Por eso `.env` ya está cargado cuando se evalúa
`os.getenv("CORS_ORIGINS", ...)`, sea cual sea el orden interno del bloque de imports de `main.py` (robusto frente a I001).
No se añade un `load_dotenv()` nuevo: la bitácora del 2 nov descarta esparcir ese olor; A4 lo resuelve de raíz.

**Qué congela qué.** Hoy nada congela CORS. Los tests nuevos congelan: (1) el contrato del parser (recorte, vacíos,
comodín → `ValueError`); (2) que la lista efectiva del proceso no contiene `*` (la métrica del backlog, "**1**
`allow_origins=["*"]`", pasa a 0 y un test la vigila); (3) origen permitido → eco + `Vary` y **sin**
`access-control-allow-credentials` (decisión 1 congelada); (4) origen desconocido → sin cabeceras CORS en respuesta normal y
`400` en preflight; (5) sin `Origin` → sin cabeceras CORS (Postman y móvil siguen igual). `test_read_root` sigue
congelando el health check. Para no depender del `.env` local, los tests de integración toman el origen permitido de la
constante `CORS_ORIGINS` exportada por `app.main` (y afirman como precondición que el origen "malo" no está en ella), en
lugar de escribir `http://localhost:3000` a mano; el default se congela aparte mediante `DEFAULT_CORS_ORIGINS`.

**Orden y dependencias.** Una sola fase: parser, cableado, `.env.example` y tests son un único cambio atómico (`fix`). Se
descartó partir en "parser" y "cableado": la primera mitad dejaría una función sin uso en un commit y un segundo ciclo
ejecutor + auditor por tres líneas. Con una fase, la fase A es trivialmente la más pequeña.

**Riesgos.** (1) Despliegue: sin `CORS_ORIGINS` en una Web App el PWA de ese entorno se rompe visiblemente; es de David
(decisión 5) y no lo detecta ningún test del backend. (2) Un origen mal escrito (barra final, ruta, `http` por `https`)
nunca casa por la comparación exacta de Starlette; el parser **no** lo valida (no está en las decisiones; ver Residuales).
(3) Si el cliente Flutter web enviara peticiones con `withCredentials: true`, el navegador bloquearía las respuestas al no
venir `Access-Control-Allow-Credentials`; el repo del frontend no está aquí, así que es una comprobación para David (ver
Residuales). (4) `tests/test_main.py:3` tiene hoy un `E501` (docstring de 103 columnas): el hook `ruff_on_edit.py` corre
`ruff check --fix` sobre el archivo editado y devolverá ese error al ejecutor porque no es autocorregible; la fase lo
corrige (archivo tocado → 0 errores, ADR-0005) y el total de ruff baja de 98 a 97. (5) `app/main.py` entra en `mypy.files`;
hoy no aporta errores: la función nueva va completamente anotada para que siga así. (6) `.env` local: si David tuviera
`CORS_ORIGINS` definido ahí con otro valor, los tests siguen pasando (leen la constante), salvo que el valor sea vacío
(`CORS_ORIGINS[0]` fallaría); el handoff lo anota si ocurre.

**Qué NO se toca.** `app/api/routers/user.py:66` (`FRONTEND_URL`), `app/api/dependencies.py`, la auth, `allow_methods`,
`allow_headers`, `docker-compose.yml`, `.azure-pipelines/`, `pyproject.toml`, `tests/conftest.py`, la deuda de ruff/mypy de
otros archivos, y los documentos vivos (backlog, CONTEXT, PLAN): los actualiza la sesión de cierre.

## Regla de alcance

- **Sí:** `app/main.py` (parser, constantes, los cinco argumentos del middleware), `tests/test_main.py` (tests nuevos y el
  docstring de `test_read_root`), `.env.example` (una sección nueva con `CORS_ORIGINS`).
- **No:** todo lo demás. Hallazgos nuevos → sección Residuales → `docs/backlog.md` en el cierre.

## Fases

### Fase A — Lista blanca `CORS_ORIGINS` sin credenciales, con parser puro y tests (única fase, la más pequeña)

- **Archivos:** `app/main.py`, `tests/test_main.py`, `.env.example`.
- **Cambios exactos:**
  - `app/main.py`: añadir `import os` como primer import (bloque stdlib, antes de `fastapi`). Justo antes del
    `app.add_middleware(...)` actual (hoy `:163`), bajo un banner `# === CORS ===` en el estilo del archivo:
    ```python
    DEFAULT_CORS_ORIGINS = "http://localhost:3000"


    def parse_cors_origins(raw: str) -> list[str]:
        """Parse the comma-separated ``CORS_ORIGINS`` value into an explicit allow-list.

        Pure on purpose so the startup contract can be unit tested without reloading
        the module: entries are trimmed, empty entries are dropped and any wildcard is
        rejected, because Starlette would either reflect every origin (``"*"``) or
        never match it (``"https://*.example"``).

        Args:
            raw: The raw environment value, e.g. ``"https://a.example, https://b.example"``.

        Returns:
            The list of allowed origins, in the order given, possibly empty.

        Raises:
            ValueError: If any entry contains ``"*"``.
        """
        origins = [entry.strip() for entry in raw.split(",")]
        origins = [origin for origin in origins if origin]
        if any("*" in origin for origin in origins):
            raise ValueError("CORS_ORIGINS must list explicit origins; wildcards are not allowed")
        return origins


    # Read at import time with os.getenv, like the rest of the configuration (backlog A4
    # centralizes settings). `.env` is already loaded here: app.db.database calls
    # load_dotenv() and is imported transitively through app.api.routers above.
    CORS_ORIGINS: list[str] = parse_cors_origins(os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS))
    ```
    y el middleware pasa a:
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,  # Bearer tokens are not CORS credentials; no cookies in this API.
        allow_methods=["*"],  # Open on purpose: only trusted origins get this far (backlog SEC1).
        allow_headers=["*"],
    )
    ```
    El texto del `ValueError` y de los comentarios es orientativo; la firma, los nombres `DEFAULT_CORS_ORIGINS`,
    `parse_cors_origins`, `CORS_ORIGINS`, el comentario `(backlog A4)` y los cinco argumentos del middleware son exactos.
    Nada más cambia en `app/main.py` (ni `load_dotenv()`, ni handlers, ni routers).
  - `.env.example`: nueva sección al final, con el mismo formato de banner que las existentes:
    ```
    # ==========================================
    # CORS (browser clients only; mobile and Postman send no Origin)
    # ==========================================
    # Comma-separated list of exact origins (scheme://host[:port], no path, no trailing slash).
    # Wildcards are rejected at startup. Each deployment sets only its own frontend here.
    CORS_ORIGINS=http://localhost:3000
    ```
  - `tests/test_main.py`: cabecera `import pytest` y `from app.main import CORS_ORIGINS, DEFAULT_CORS_ORIGINS, parse_cors_origins`;
    el docstring de `test_read_root` se reparte en dos líneas de ≤ 100 columnas (mismo contenido; corrige el `E501`
    preexistente). Constante local `UNKNOWN_ORIGIN = "https://evil.example"`. Todos los tests de integración usan la
    fixture `client` existente; las cabeceras se leen con `response.headers.get(...)` (httpx es case-insensitive).
- **Tests (RED primero)** (nombres exactos; aserciones sobre códigos, cabeceras y estructura, nunca sobre texto humano):
  1. `test_parse_cors_origins_single_origin`: `"http://localhost:3000"` → `["http://localhost:3000"]`.
  2. `test_parse_cors_origins_trims_and_drops_empties`: `" https://a.example , ,https://b.example, "` →
     `["https://a.example", "https://b.example"]`.
  3. `test_parse_cors_origins_empty_value_is_empty_list` (parametrizado `""`, `",,"`, `"  "`) → `[]`.
  4. `test_parse_cors_origins_rejects_wildcard` (parametrizado `"*"`, `" * "`, `"https://a.example,*"`,
     `"https://*.azurestaticapps.net"`) → `pytest.raises(ValueError)`.
  5. `test_default_cors_origins_is_local_frontend`: `parse_cors_origins(DEFAULT_CORS_ORIGINS) == ["http://localhost:3000"]`.
  6. `test_configured_cors_origins_have_no_wildcard`: `CORS_ORIGINS` es `list`, no vacía, y ningún elemento contiene `"*"`.
  7. `test_cors_allowed_origin_is_echoed_without_credentials`: `GET /` con `Origin: CORS_ORIGINS[0]` → `200`;
     `access-control-allow-origin == CORS_ORIGINS[0]`; `"origin"` en `vary.lower()`; `access-control-allow-credentials`
     **ausente**; el JSON del cuerpo es el mismo que en `test_read_root`.
  8. `test_cors_unknown_origin_gets_no_cors_headers`: precondición `UNKNOWN_ORIGIN not in CORS_ORIGINS`; `GET /` con
     `Origin: UNKNOWN_ORIGIN` → `200` (la petición se sirve; el navegador bloquea) y `access-control-allow-origin` ausente.
  9. `test_cors_preflight_allowed_origin`: `OPTIONS /` con `Origin: CORS_ORIGINS[0]`, `Access-Control-Request-Method: POST`,
     `Access-Control-Request-Headers: authorization, content-type` → `200`; `access-control-allow-origin == CORS_ORIGINS[0]`;
     `"POST"` en `access-control-allow-methods`; `"authorization"` en `access-control-allow-headers.lower()`;
     `access-control-allow-credentials` ausente.
  10. `test_cors_preflight_unknown_origin_is_rejected`: `OPTIONS /` con `Origin: UNKNOWN_ORIGIN` y
      `Access-Control-Request-Method: GET` → `400` y `access-control-allow-origin` ausente.
  11. `test_request_without_origin_bypasses_cors`: `GET /` sin `Origin` → `200` y `access-control-allow-origin` ausente.

  RED esperado sobre `7c6d606`: 1–6 fallan por `ImportError`; 7 y 9 fallan porque hoy llega
  `access-control-allow-credentials: true`; 8 falla porque hoy el origen desconocido se refleja; 10 falla porque hoy el
  preflight responde `200`. El 11 está verde hoy y después: congela el camino de Postman/móvil (borde documentado, no RED).
- **Criterio de aceptación:**
  - `venv/Scripts/python.exe -m pytest tests/test_main.py -q` → 17 passed (12 funciones; 17 casos con las parametrizaciones de los tests 3 y 4); suite completa 317 + 16 = 333 passed, 0 failed.
  - `venv/Scripts/python.exe -m ruff check app/main.py tests/test_main.py` → 0 errores (incluido el `E501` que había);
    `venv/Scripts/python.exe -m ruff format --check app/main.py tests/test_main.py` → OK; total de `ruff check .` ≤ 97.
  - `venv/Scripts/python.exe -m mypy` → ninguna línea de `app/main.py` en la salida; total ≤ 44.
  - `scripts/check.py`: import-linter 4 kept; docs ✔; cobertura ≥ 92.68 %.
  - `grep -rnE 'allow_origins=\["\*"\]' app tests alembic --include=*.py` → vacío; `grep -rn "allow_credentials=True" app --include=*.py` → vacío;
    `grep -n "CORS_ORIGINS" .env.example` → 1 línea; `grep -rn "load_dotenv" app/main.py` → vacío.
  - Arranque con comodín falla: en Git Bash, `CORS_ORIGINS="*" venv/Scripts/python.exe -c "import app.main"` termina con
    `ValueError` (en PowerShell: `$env:CORS_ORIGINS='*'; venv/Scripts/python.exe -c "import app.main"`). Requiere el
    `.env` local para que `app.db.database` importe; el ejecutor pega el traceback resumido en el handoff.
- **Fuera de alcance de esta fase:** `allow_methods`/`allow_headers`; validar la forma del origen (ruta, barra final,
  esquema); `docker-compose.yml`; `FRONTEND_URL`; cualquier `Settings`; anotar los handlers de `app/main.py` que no
  tienen tipo de retorno; actualizar backlog/CONTEXT/PLAN.
- **Commit:**
  ```
  fix(cors): allow only configured origins and stop sending credentials

  CORSMiddleware was registered with allow_origins=["*"] and
  allow_credentials=True. Starlette resolves that pair by reflecting the
  request's Origin, so any website could call the API with credentials
  and read the response (backlog SEC1). Auth is Bearer-only today, so the
  exposure was latent; it stops being latent the day a cookie appears.

  - app/main.py: `parse_cors_origins` (pure, importable) splits the
    comma-separated CORS_ORIGINS, trims, drops empties and refuses any
    wildcard with ValueError at startup; the middleware receives that
    list with allow_credentials=False (Authorization: Bearer is not a
    CORS credential). Read with os.getenv at import time like the rest
    of the config until backlog A4 centralizes settings. allow_methods
    and allow_headers stay "*" on purpose: behind an origin allow-list
    they only apply to trusted sites (SEC1 residual).
  - .env.example: CORS_ORIGINS documented with the local default
    http://localhost:3000; per-environment values live in each Web App.
  - tests/test_main.py: parser cases (trim, empties, wildcard) and the
    middleware through the real app: allowed origin echoed with Vary and
    without a credentials header, unknown origin gets no CORS headers,
    preflight 200/400, requests without Origin untouched. The root test
    docstring is re-wrapped to clear a pre-existing E501.

  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  ```

## Verificación final

```bash
# Patrones de la verificación (esperado: 0 · 0 · 2 sin cambio · 0)
grep -rnE 'allow_origins=\["\*"\]' app tests alembic --include=*.py
grep -rnE 'allow_credentials=True' app tests alembic --include=*.py
grep -rnE 'allow_(methods|headers)=\["\*"\]' app --include=*.py
grep -rniE 'set_cookie|Cookie' app tests alembic --include=*.py
# Inventario de la corrección (esperado: CORSMiddleware solo en app/main.py; parser y constante presentes y testeados)
grep -rnE 'allow_origins|allow_credentials|CORSMiddleware|CORS_ORIGINS|parse_cors_origins' app tests --include=*.py
grep -n 'CORS_ORIGINS' .env.example                       # esperado: 1 línea, valor http://localhost:3000
grep -rn 'azurestaticapps' app .env.example               # esperado: vacío (URLs de Azure fuera del código)
grep -rnE 'pydantic_settings|BaseSettings' app --include=*.py   # esperado: vacío (sin Settings en este ítem)
grep -n 'load_dotenv' app/main.py                         # esperado: vacío
# Arranque con comodín (esperado: ValueError; en PowerShell usar $env:CORS_ORIGINS='*')
CORS_ORIGINS="*" venv/Scripts/python.exe -c "import app.main"; echo "exit $?"
# Trinquete (ADR-0005) sobre los archivos tocados y totales
venv/Scripts/python.exe -m ruff check app/main.py tests/test_main.py
venv/Scripts/python.exe -m ruff check . | tail -1         # esperado: Found 97 errors (o menos)
venv/Scripts/python.exe -m mypy | grep -E 'app[\\/]main\.py|^Found'   # esperado: solo "Found 44 errors" (o menos)
venv/Scripts/python.exe -m pytest tests/test_main.py -q   # esperado: 17 passed
# Compuerta completa (línea base: pytest 317 ✔ · 92.68 % · ruff ✘ 98 · mypy ✘ 44 · import-linter 4 kept · docs ✔)
venv/Scripts/python.exe scripts/check.py
```

## Residuales

- **`allow_methods=["*"]` y `allow_headers=["*"]`** (`app/main.py`, 2 ocurrencias; decisión 2 de la adenda). Con lista
  blanca de orígenes solo afectan a sitios de confianza; acotarlos puede romper el cliente sin que lo detecte el backend.
  Fila sugerida para `docs/backlog.md` §A (la decisión la fija David; vocabulario de R4):
  `| SEC1-R | CORS: \`allow_methods\`/\`allow_headers\` en \`*\` tras la lista blanca de SEC1 | **2** \`allow_(methods|headers)=["*"]\` | Baja | XS | **Sale → \`B-FUTURO\`** |`
- **`docker-compose.yml:10-14`** enumera `environment:` explícito y no pasa `CORS_ORIGINS` (tampoco `FRONTEND_URL`, correo ni
  Azure): el contenedor local arranca con el default `http://localhost:3000`, que es el valor correcto en local, pero la
  variable no es configurable desde `.env` por compose. Añadir `CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}` cuando
  se toque el compose (manual técnico de despliegue, entregable de CONTEXT §3).
- **Manual técnico de despliegue:** debe listar `CORS_ORIGINS` por entorno junto a `FRONTEND_URL` de cada Web App; la
  verificación lo deja en la adenda (decisión 4), pero el manual es el dueño natural.
- **Frontend Flutter web (fuera de este repo):** confirmar que el cliente HTTP no usa `withCredentials: true` (en
  `package:http` `BrowserClient` y en `dio` el default es `false`). Si lo usara, el navegador bloquearía las respuestas al
  faltar `Access-Control-Allow-Credentials`. Comprobación de David antes del PR a `staging`; una línea en la descripción del PR.
- **Validación de forma del origen** (opcional, no está en las decisiones): Starlette compara por igualdad, así que
  `https://host/` o `https://host/#` en `CORS_ORIGINS` nunca casan y el fallo es silencioso. Rechazar entradas con ruta,
  barra final o sin esquema sería una rama más en `parse_cors_origins` y un test parametrizado. Si David lo quiere, cabe en
  esta misma fase (sumar al punto 4 de los tests); si no, queda aquí con destino `B-FUTURO` o al cerrar A4.
- **Preexistente en `app/main.py`, no SEC1:** los tres handlers de excepciones no declaran tipo de retorno (mypy no lo
  exige hoy con `check_untyped_defs`); el handler de 422 responde con clave `"detalle"` (ya es P2 en el backlog).

## Referencias

- **Context7** (`/kludex/starlette`, `docs/middleware.md`, consultado por la sesión orquestadora el 2 nov 2026): confirma
  que los parámetros por defecto son restrictivos; que un preflight es cualquier `OPTIONS` con `Origin` y
  `Access-Control-Request-Method` y responde `200` o `400`; que una petición simple con `Origin` se sirve igual y solo se le
  añaden las cabeceras CORS que correspondan; y que `allow_credentials` es para cookies y es incompatible con `["*"]`
  (release notes: "Return explicit origin in CORS response when credentials are allowed", PR #3137, que es exactamente el
  reflejo que SEC1 elimina). El detalle línea a línea se leyó del código fuente **instalado** en el `venv`, fuente exacta
  para la versión en uso:
  `venv/Lib/site-packages/starlette/middleware/cors.py` (Starlette **1.3.1**): `__call__` (sin `Origin` → pasa sin tocar;
  `OPTIONS` + `access-control-request-method` → `preflight_response`), `is_allowed_origin` (`origin in self.allow_origins`,
  igualdad exacta), `send` (eco del origen + `Vary: Origin` solo si está en la lista; reflejo universal solo con `*` +
  credenciales), `preflight_response` (`400` con `Disallowed CORS origin` si no está permitido; `Access-Control-Allow-Headers`
  espeja lo pedido cuando `allow_headers` es `*`), `Access-Control-Allow-Credentials: true` solo si `allow_credentials=True`.
- Starlette · 1.3.1 · `CORSMiddleware` · https://www.starlette.io/middleware/#corsmiddleware
- FastAPI · 0.135.1 · tutorial de CORS (`allow_origins` explícitos; con `["*"]` no se deben permitir credenciales) ·
  https://fastapi.tiangolo.com/tutorial/cors/
- httpx · 0.28.1 · `ASGITransport` (ya usado por `tests/conftest.py:68`; cabeceras de respuesta case-insensitive) ·
  https://www.python-httpx.org/advanced/transports/#asgitransport
- `os.getenv` · Python 3.14 · https://docs.python.org/3.14/library/os.html#os.getenv

**ADR propuesto:** ninguno. Es la corrección de una configuración insegura, no un patrón, módulo ni contrato nuevo; las
cuatro decisiones XS (credenciales a `False`, métodos/cabeceras fuera, `os.getenv` + parser en `main.py`, default local)
están registradas con fecha y autor en la adenda de `verificacion.md`, y la lectura de configuración al importar es deuda ya
nombrada (A4), no una decisión de este ítem. Si BE-12 mueve el refresh token a cookie, ese ADR será el que revise
`allow_credentials`, no este plan.
- **Variable definida pero vacía (nota del cierre de la fase, David, 2 nov):** el plan devuelve `[]` (fail-closed) y así
  se implementó en `9ce0379`. David había aprobado a las 15:58 "vacío → `ValueError`" en la sesión Mentor, pero el retoque
  no se escribió en este archivo antes de `/implementar`, y el ejecutor lee el disco. Se acepta `[]` hoy; "configuración
  inválida = la API no arranca" para toda la configuración pasa a A4, donde `Settings` la valida junta
  (bitácora 2026-11-02).

# Verificación — BE-15: suite de tests no conforme a AGENTS §5 (diagnóstico §9 de la auditoría)

**Veredicto:** parcial
**Fuente del ítem:** docs/backlog.md §A (fila BE-15, l.45) + §A2 (fila §9, l.98) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html`, sección "Resiliencia de la suite de pruebas" y fichas B2/B3/B4; fase 6 del plan de remediación
**Fecha:** 2026-11-04

## Qué describe el ítem
Seis defectos de la suite: (1) mocks sin `spec`; (2) preparación de usuarios/tokens duplicada a mano en vez de
fábricas de `conftest.py`; (3) aserciones sobre texto en español; (4) la sesión de prueba es la misma que recibe
la app (≠ `get_db`, que crea una por petición); (5) sin cobertura ni linters; (6) sin tests para B2 (admin se
auto-asigna superadmin), B3 (superadmin borra a un tercero) y B4 (DELETE de cédula inexistente → 404).

Estado por sub-hallazgo: **(1) persiste · (2) persiste (parcialmente migrado) · (3) persiste · (4) persiste ·
(5) corregido · (6) B4 cubierto, B3 cubierto solo en unidad, B2 sin test del escenario exacto.**

## Evidencia en el código

### (1) Mocks sin `spec` — PERSISTE
- `tests/conftest.py:81` — `mock_client = MagicMock()` en el fixture `autouse` `override_azure_storage_client`
  (l.74–108): sustituye a `AzureStorageClient` en **todos** los tests. Es exactamente el `conftest.py:76` del informe.
- `tests/conftest.py:88`, `:91`, `:97` — `AsyncMock(...)` sin `spec` colgados de ese mock (`upload_image`,
  `delete_image`, `promote_to_permanent`); `:101–102` atributos lambda (`is_temporal_url`, `is_permanent_url`).
  Un método renombrado en el adaptador real no rompe ningún test que use este doble.
- `tests/test_auth.py:28` — `patch("app.api.routers.user.send_verification_email")` **sin** `autospec=True`
  (el mismo patch en `tests/test_user_response.py:46` sí lo lleva).
- `tests/test_services.py:234` — `failing_client.upload_image = AsyncMock(side_effect=...)` reemplaza un método de
  un `create_autospec(AzureStorageClient, instance=True)` (l.233) por un `AsyncMock` sin firma: pierde la
  comprobación de firma que daba el autospec. Menor.
- Contrapunto (ya conforme): `create_autospec` en `tests/test_audit.py:98`, `tests/test_services.py:233,397`,
  `tests/test_storage.py:24,31,58,61`, `tests/test_user_access_policy.py:471`, `tests/test_user_service.py:65,71`,
  `tests/test_user_response.py:46` (`autospec=True`), `tests/test_check.py:104–105`, `tests/test_check_docs.py:596,625,738,741,919,933`.

### (2) Setup duplicado — PERSISTE (las fábricas existen; la migración está a medias)
- Fábricas centrales ya presentes: `tests/conftest.py:119` `make_user`, `:159` `make_token`, `:175`
  `make_auth_headers`, `:191` `persist_user`.
- `tests/test_auth.py` — **16** `User(` a mano (l.279, 292, 326, 336, 369, 379, 389, 425, 435, 446, 483, 493, 530,
  540, 573, 617), **11** `create_access_token(` a mano (l.194, 228, 257, 305, 349, 403, 461, 508, 555, 586, 630),
  cabeceras `Bearer` a mano (l.149, 195, 229, 258, 312, 355, 406, 465, 512, 560, 604, 648) y 4
  `get_password_hash("pass")` (l.284, 297, 331, 341). Ningún test de este archivo usa las fábricas.
- `tests/test_audit.py:13–28` — fixture local `superadmin_token` con `User(` (l.15), `get_password_hash` (l.20),
  `create_access_token` (l.27) y `Bearer` (l.28); `:69`, `:81`, `:83` repiten lo mismo dentro de un test.
- `tests/test_services.py:34–64` — fixtures locales `admin_token` (`User(` l.46, `get_password_hash` l.51,
  `create_access_token` l.58) y `auth_headers` (l.62–64), usados por **13** tests (l.100, 128, 157, 191, 210, 227,
  253, 261, 269, 279, 287, 295, 318). El mismo archivo ya tiene `admin_headers` sobre las fábricas centrales
  (l.404–409): dos mecanismos paralelos en un archivo.
- Fixture `mock_send_email` duplicado: `tests/test_auth.py:22–29` y `tests/test_user_response.py:43–47`
  (uno con autospec, otro sin él).

### (3) Aserciones sobre texto en español — PERSISTE (8, todas en `tests/test_auth.py`)
- `tests/test_auth.py:58` — `assert response.json()["detail"] == "Este usuario ya se encuentra registrado."`
- `tests/test_auth.py:85` — `assert "inválido" in response.json()["detail"].lower()`
- `tests/test_auth.py:122` — `assert "verificar su cuenta" in response.json()["detail"]`
- `tests/test_auth.py:131` — `assert response.json()["detail"] == "Revise su correo y contraseña"`
- `tests/test_auth.py:160–163` — `response_data["message"] == f"La cuenta vinculada a {target_email}, con C.C. ... ha sido eliminada exitosamente."`
- `tests/test_auth.py:360` — `assert "Violación de jerarquía" in response.json()["detail"]`
- `tests/test_auth.py:565` — `assert "jerarquía" in response.json()["detail"].lower()`
- `tests/test_auth.py:609` — `assert "superusuario" in response.json()["detail"].lower()`
- Nota: la línea base del 24 oct ("`detail ==` **4**", backlog l.98) solo contaba igualdades; las de subcadena
  (`in ...["detail"]`) y la de `["message"]` no entraban. El total real hoy es 8.
- No cuentan (verificado): `tests/test_services.py:433,453,469,485,519,570,609` y
  `tests/test_user_access_policy.py:462` afirman `isinstance(..., str)` (estructura);
  `tests/test_user_response.py:180,184` y `tests/test_services.py:752,756` comparan **datos** ("Pérez",
  "Tour corto"), no mensajes; `tests/test_check_docs.py` afirma códigos de regla (`R1`, `: R5: `), no prosa.

### (4) Sesión de prueba ≠ `get_db` — PERSISTE
- `tests/conftest.py:49–53` — `db_session` abre **una** sesión de `TestingSessionLocal`.
- `tests/conftest.py:56–71` — `client` sobreescribe `get_db` con `override_get_db()` que hace `yield db_session`
  (l.63–66): la app y el test comparten la misma sesión durante todo el test.
- `app/db/database.py:33–39` — `get_db()` real abre una sesión nueva por petición (`async with AsyncSessionLocal()`).
- Dependientes del comportamiento actual (llamadas directas a `db_session.refresh/execute/get/commit/add`):
  `tests/test_auth.py` 33, `tests/test_services.py` 23, `tests/test_user_access_policy.py` 6,
  `tests/test_audit.py` 4, `tests/test_user_response.py` 4, `tests/conftest.py` 3 (`persist_user`, l.203–205).

### (5) Sin cobertura ni linters — CORREGIDO
- `pyproject.toml:40` `pytest-cov>=6.0`; `:38–41` ruff, mypy, import-linter en `dev`.
- `pyproject.toml:58–98` configuración de ruff y mypy; `:100–132` cuatro contratos de import-linter;
  `:134–143` coverage con `branch = true` y `fail_under = 92`.
- `scripts/check.py` une los seis pasos; `.azure-pipelines/ci-pipeline.yml` lo ejecuta en cada PR a
  develop/staging/main, **pero con `--soft format,ruff,mypy`** (l.27–29): ruff y mypy no bloquean el CI. Su
  retirada es entregable de `B-TESTS m4` (PLAN §2b, l.59), no de este sub-hallazgo.

### (6) Huecos B2/B3/B4 — PARCIAL
El código de producción ya está corregido (`app/services/user_access_policy.py:53–63`;
`app/services/user_service.py:193–202` comprueba existencia antes que permisos). Lo que se mide aquí es si hay
test que lo congele:
- **B4 — cubierto.** `tests/test_user_access_policy.py:329–341` (`DELETE /usuarios/9999999999` → 404 + clave
  `detail`, HTTP real) y `tests/test_user_service.py:130–140` (unidad: `NotFoundError` y
  `soft_delete_user.assert_not_awaited()`). El actor es turista, no admin como en el informe; el orden
  404-antes-que-403 es el mismo camino.
- **B3 — cubierto solo en unidad.** `tests/test_user_access_policy.py:49–53` (`assert_can_delete(superadmin, admin)`
  no lanza) y `:55–58` (auto-borrado). **No existe** test HTTP ni de servicio en el que un superadmin borre la
  cuenta de un tercero y se compruebe 200 + `deleted_at` en BD: los únicos `client.delete("/usuarios/...")` son
  `tests/test_auth.py:154` (turista se borra a sí mismo), `tests/test_user_access_policy.py:301` (admin→superadmin,
  403), `:335` (inexistente, 404) y `:476` (servicio falso).
- **B2 — sin test del escenario exacto.** El bug era la ruta de auto-edición (`actor == target`, rol admin,
  `{"role": "superadmin"}`). Tests existentes: `tests/test_user_access_policy.py:128–132` (admin → **turista**,
  unidad), `:392–409` y `:412–429` (admin → **turista**, HTTP), `:141–145` y `:122–126` (auto-escalada de
  **turista**). Ninguno usa un admin sobre su propia cédula. La regla actual (`user_access_policy.py:60`, "role en el
  payload y actor ≠ superadmin → 403") lo bloquea con independencia del objetivo, así que la cobertura indirecta
  existe; lo que falta es el test de regresión que nombra el bug.

## Ficheros afectados (mapa completo)
- `tests/conftest.py` — (1) `MagicMock()` sin spec l.81 y AsyncMocks l.88/91/97; (4) `override_get_db` comparte sesión l.56–71.
- `tests/test_auth.py` — (1) patch sin autospec l.28; (2) 16 `User(`, 11 tokens, 12 cabeceras a mano; (3) las 8 aserciones en español; 3 de los 7 errores de ruff de la suite (l.1, 50, 162; ver línea base).
- `tests/test_audit.py` — (2) fixture local `superadmin_token` l.13–28 y construcción manual l.69–83.
- `tests/test_services.py` — (1) `AsyncMock` sobre autospec l.234; (2) fixtures locales `admin_token`/`auth_headers` l.34–64 usados por 13 tests, en paralelo a `admin_headers` l.404.
- `tests/test_user_response.py` — (2) `mock_send_email` duplicado l.43–47.
- `tests/test_user_access_policy.py` — (6) destino natural de los tests de B2 (admin auto-edición) y B3 (superadmin borra a tercero, HTTP + estado).
- `tests/test_user_service.py` — (6) alternativa de nivel servicio para B3 (`delete_user_account` con superadmin → `soft_delete_user` llamado con argumentos).
- `app/db/database.py` — (4) solo referencia: `get_db` real l.33–39 (no se modifica para cerrar el ítem).
- `pyproject.toml`, `scripts/check.py`, `.azure-pipelines/ci-pipeline.yml` — (5) ya conformes; el `--soft` del CI es de `B-TESTS m4`.

## Rincones no mencionados por la fuente
- **Aserciones de mock sin argumentos** (AGENTS §5 exige `assert_called_once_with`): `tests/test_auth.py:46`,
  `tests/test_user_service.py:110,111,328,329`, `tests/test_storage.py:159,189,198` sin inspección posterior de
  argumentos. `tests/test_services.py:245,520` y `tests/test_storage.py:92` sí inspeccionan `call_args`/`await_args`
  después (no son deuda).
- **Nombres de test en español** (AGENTS §4): los 19 `test_` de `tests/test_auth.py` (l.32–612, p. ej.
  `test_registro_usuario_exitoso`, `test_borrado_logico_usuario`).
- **Aserciones que congelan la clave `"detalle"`** (deuda P2): `tests/test_services.py:767,782`,
  `tests/test_user_response.py:166,205`. No son texto en español, pero romperán cuando P2 unifique a `detail`.
- **`sqlalchemy.future`** (S2) en `tests/test_auth.py:5`.
- **Dependencia del entorno**: `tests/conftest.py:13` importa `app.main`, que arrastra `app/db/database.py:6`
  (`load_dotenv()`) y `app/core/security.py:7` (`JWT_SECRET_KEY` de `os.getenv`); el conftest no fija esas
  variables. Es el "la suite deja de depender de `.env`" de `B-TESTS m1` (PLAN l.59); su raíz es A4.
- **Errores de ruff dentro de la suite** (de la línea base, ver abajo): `tests/test_audit.py:1` I001,
  `tests/test_auth.py:1` I001, `:50` E501, `:162` E501 (es la propia aserción en español del punto 3),
  `tests/test_user_access_policy.py:347,395` E501, `tests/test_user_service.py:3` I001.

## Patrones de detección (copiables)
```bash
# (1) mocks sin spec (constructores sueltos y patch sin autospec)
grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py
grep -rnE "patch(\.object)?\(" tests/ --include=*.py | grep -v "autospec"
# (2) setup duplicado fuera de conftest
grep -rnE "\bUser\(" tests/ --include=*.py | grep -v "tests/conftest.py"
grep -rnE "create_access_token\(" tests/ --include=*.py | grep -v "tests/conftest.py"
grep -rnE "f\"Bearer \{" tests/ --include=*.py | grep -v "tests/conftest.py"
grep -rnE "def mock_send_email|def admin_token|def auth_headers|def superadmin_token" tests/ --include=*.py
# (3) aserciones sobre texto en español
grep -rnE "\[\"(detail|message)\"\]( ==|\.lower\(\))|in response\.json\(\)\[\"detail\"\]" tests/ --include=*.py
grep -rnE "== f?\"[A-ZÁÉÍÓÚ][a-záéíóúñ]+ [a-záéíóúñ]+" tests/ --include=*.py
# (4) sesión compartida test/app
grep -nE "def override_get_db|yield db_session" tests/conftest.py
# (6) huecos: admin sobre su propia cédula con role; superadmin borrando a un tercero por HTTP
grep -rnE "json=\{\"role\"" -B4 tests/ --include=*.py
grep -rnE "client\.delete\(" -B6 tests/ --include=*.py | grep -E "superadmin|client\.delete"
# adyacente: aserciones de mock sin argumentos
grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ --include=*.py
```

## Línea base (python scripts/check.py)
- Base develop: `7877829` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `78778296f39e…`). La rama actual es `bloque/b-tests` (HEAD `6697602`), dos
  commits sobre develop que solo tocan `docs/bitacora/2026-11-04.md` y `docs/deuda/BE-07/verificacion.md`.
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Python 3.14.3).

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
- **La compuerta ya falla antes de tocar nada** (exit 1), igual que en la verificación previa de BE-07.
- ruff format: `52 files already formatted`.
- ruff check: `Found 60 errors.` (`[*] 11 fixable with --fix`). Por regla: E501 23, D205 13, I001 11, D415 6,
  B904 4, W293 3. **7 caen en archivos de BE-15:** `tests/test_audit.py:1` I001, `tests/test_auth.py:1` I001,
  `tests/test_auth.py:50` E501, `tests/test_auth.py:162` E501, `tests/test_user_access_policy.py:347` E501,
  `tests/test_user_access_policy.py:395` E501, `tests/test_user_service.py:3` I001. Resto: `app/core/email.py` 11,
  `app/services/user_access_policy.py` 9, `app/repositories/service_repository.py` 8, `app/api/dependencies.py` 7,
  `app/services/user_service.py` 6, `app/schemas/audit.py` 3, `app/db/database.py` 2,
  `app/repositories/user_repository.py` 2, `app/schemas/token.py` 2, `app/api/routers/audit.py` 1,
  `app/repositories/audit_repository.py` 1, `app/services/audit_service.py` 1.
- mypy: `Found 10 errors in 5 files (checked 35 source files)` — `app/db/database.py:11`,
  `app/repositories/service_repository.py:83`, `app/core/security.py:71,87`, `app/services/user_service.py:124,132,133`,
  `app/api/dependencies.py:92,93,108`. **Ninguno en `tests/`** (mypy no analiza `tests/`: `pyproject.toml:90`).
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- docs (coherencia): OK.
- pytest: `376 passed, 5 warnings in 19.39s` (0 failed). Los 5 warnings son `StarletteDeprecationWarning`
  de `HTTP_422_UNPROCESSABLE_ENTITY` (S5).
- Cobertura total: `TOTAL 942 34 136 22 94.81%` — `Required test coverage of 92.0% reached. Total coverage: 94.81%`.
- Cobertura de los módulos de producción que ejercen B2/B3/B4 (los archivos del ítem son tests, fuera de
  `source = ["app"]`): `app/services/user_access_policy.py` 100 % (entre los 22 omitidos por cobertura completa),
  `app/services/user_service.py` 99.15 % (falta rama `282->291`), `app/api/dependencies.py` 84.75 %
  (faltan 63, 95, 98-105, 111).

## Conclusión para el planificador
El plan debe cerrar cuatro sub-hallazgos que siguen vivos: (1) dar `spec`/`autospec` al doble global de
`tests/conftest.py:81` y al patch de `tests/test_auth.py:28`; (2) migrar `test_auth.py`, `test_audit.py` y el par
`admin_token`/`auth_headers` de `test_services.py` a las fábricas que **ya existen** en `conftest.py` (no crear
fábricas nuevas) y unificar `mock_send_email`; (3) sustituir las 8 aserciones en español de `test_auth.py` por
código + estructura; (4) dar a la app una sesión distinta de la del test; y (6) añadir el test de regresión de B2
(admin, propia cédula, `role=superadmin` → 403 sin mutación) y el de B3 por HTTP (superadmin borra a un tercero →
200 + `deleted_at`). No toca código de `app/` (los bugs B2–B4 ya están corregidos), ni el `--soft` del CI ni la
clave `"detalle"` (P2), ni la carga de entorno (A4). Riesgo principal: el punto (4) cambia la semántica de ~70
llamadas directas a `db_session` repartidas en 5 archivos (lecturas tras `commit` de la app, `refresh`); conviene
aislarlo en su propia fase, después de migrar las fábricas, y medir que siguen 376 passed y cobertura ≥ 94.81 %.
Los 7 errores de ruff en tests caerán solos al reescribir esas líneas; los 53 de `app/` y los 10 de mypy no son de
este ítem.

## Adenda — decisiones de David antes de planear (4 nov 2026, 10:12, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Dato de infraestructura que la conclusión no subraya y que pesa en el punto 4: la suite corre sobre SQLite con
`StaticPool` (una sola conexión; `create_all`/`drop_all` por test), `tests/conftest.py:19-28`.

1. **Orden de fases y qué cabe en cada media jornada (PLAN §2b, `B-TESTS`).** `m1`: (1) `spec`/`autospec` en el doble
   global de `conftest.py:81` y en el `patch` de `test_auth.py:28` · (2) migrar `test_auth.py`, `test_audit.py` y el par
   `admin_token`/`auth_headers` de `test_services.py` a las fábricas que **ya existen** en `conftest.py` (no se crean
   fábricas nuevas), y unificar `mock_send_email` · (3) las 8 aserciones en español de `test_auth.py` por código +
   estructura. `m2`: (6) tests de regresión de B2 (admin, propia cédula, `role=superadmin` → 403 sin mutación) y B3
   (superadmin borra a un tercero por HTTP → 200 + `deleted_at`) · (4) sesión de la app distinta de la del test,
   **última fase y recortable**: si no cabe en `m2`, el cierre del día la declara deslizada; no se arrastra en silencio.
   Cada fase respeta ≤ 5 archivos y termina en 376 passed (más los nuevos) y cobertura ≥ 94.81 %.
2. **"La suite deja de depender de `.env`" sale del alcance.** Es A4 (`B-PAGOS`): `security.py` lee el entorno al
   importar; un parche solo para tests sería una segunda ruta de configuración. La celda `B-TESTS m1` de PLAN §2b se
   corrige en el cierre del 4 nov.
3. **Alcance adyacente, por archivo tocado, declarado aquí para que no sea scope creep:** los 19 nombres de tests en
   español de `test_auth.py` se renombran en la fase que reescribe ese archivo (AGENTS §4); `from sqlalchemy.future`
   de `test_auth.py:5` pasa a `from sqlalchemy import select` en esa misma fase (S2 sigue en `B-FUTURO` para `app/`);
   las aserciones de mock sin argumentos se convierten en `assert_called_once_with` solo donde la fase ya reescribe
   la línea; el resto queda como residual con conteo en `gaps.md`. **No se toca:** la clave `"detalle"` (P2), el
   `--soft` del CI (`m4`), `app/` (B2–B4 ya están corregidos), `.claude/` (David).
4. **Punto (4), por qué y cómo.** Con la misma sesión, un `commit()` olvidado en la app es invisible para el test (el
   `flush` ya se ve en la misma sesión). Hoy no muerde porque los repositorios hacen `commit()` (A3); cuando
   `B-RESERVAS` traiga `add()`/`flush()` sin `commit()`, la suite debe poder detectar que nadie confirmó. Con
   `StaticPool`, una segunda `TestingSessionLocal()` para la app comparte conexión con la del test, así que el cambio
   en `conftest.py` es pequeño; el coste real son las lecturas directas con `db_session` tras un commit de la app
   (`expire_on_commit=False` → objetos viejos): se resuelven con `refresh`/re-consulta, archivo por archivo, midiendo
   376 passed en cada paso. El plan dice cuántas llamadas hay por archivo (la conclusión estima ~70 en 5 archivos).
5. **Fuera de BE-15, con fila propia (BE-31, cierre del 4 nov):** SQLite ignora `postgresql_where`, así que el índice
   único parcial de ADR-0002 no sería ejercitado por esta suite tal cual; la decisión de diseño va a `B-RESERVAS m1`
   (`sqlite_where` espejo en el `Index`), no a este ítem.

# PLAN — BE-15: Poner la suite en regla con AGENTS §5 (dobles con firma, fábricas, aserciones por estructura, sesión propia de la app y regresiones B2/B3)

- **Fecha:** 2026-11-04 · **Fuente:** `verificacion.md` (veredicto parcial; la adenda de David, puntos 1 a 5, manda
  sobre la conclusión) · **Rama:** `bloque/b-tests` · **Base develop:** `7877829` (la de la verificación; el ejecutor
  la vuelve a comprobar al arrancar)
- **Aprobación:** David, 2026-11-04. Aprobado con enmiendas: D1, D2 y D3 = sí, y salvaguarda de la fase E (ver
  "Decisiones de David"). Enmienda E2 (4 nov, 12:25), tras la auditoría PASS de la fase C: test de contrato del
  `autouse` de `mock_send_email` en F y fase F-mínima si F se recorta (ver "Enmiendas aprobadas"). Enmienda E3 (4 nov,
  17:28), tras la auditoría PASS de la fase D: fase D-bis, entre E y F, que eleva a la decisión 4 las cuatro
  aserciones conservadas de `test_auth.py` (ver "Enmiendas aprobadas").

## Resumen para aprobación

Se cierran los cinco sub-hallazgos vivos de BE-15. Se toca solo `tests/` y, en la fase F, un ADR.
(1) El doble global de Azure y el del correo pasan a tener la firma real (`create_autospec`, `autospec=True`).
(2) `test_auth.py`, `test_audit.py` y `test_services.py` dejan de construir usuarios, tokens y cabeceras a mano y usan
las fábricas que ya existen en `conftest.py`; `mock_send_email` queda en un solo sitio.
(3) Las 8 aserciones sobre texto en español pasan a código HTTP, claves del JSON y estado en BD, y los 19 tests de
`test_auth.py` pasan a tener nombre en inglés.
(6) Se añaden las regresiones de B2 (un admin se asciende a sí mismo → 403, sin mutación) y de B3 por HTTP (un
superadmin borra a un tercero → 200, `deleted_at` y fila de auditoría).
(4) La app recibe una sesión propia en cada petición.
Son siete fases: A–D en `m1` y E, D-bis y F en `m2`; F es recortable. D-bis (enmienda E3) eleva a la decisión 4
las cuatro aserciones que D conservó en `test_auth.py`, sin tests nuevos. Si F se recorta, una fase F-mínima
conserva el test que vigila el `autouse` del correo (enmienda E2). El riesgo principal es (4). Un ensayo en seco, hecho sin
tocar el repo, dio 1 fallo de 376, y es un test que la fase C ya reescribe; por eso F se queda en `conftest.py`, 3
tests y el ADR. No se toca `app/`, el `--soft` del CI, la clave `"detalle"` (P2), la carga de `.env` (A4), BE-02 ni
BE-31, y tampoco se edita `AGENTS.md`: David llevará a AGENTS §5, en un PR al cierre, las dos reglas que enuncia
ADR-0011. Aprobado por David el 4 nov 2026 con enmiendas (D1–D3 = sí y salvaguarda en la fase E).

## Objetivo y decisiones bloqueadas

Que cada test de la suite cumpla AGENTS §5: dobles con firma, preparación con las fábricas centrales, aserciones sobre
códigos y estructura y no sobre prosa, y una sesión de la app distinta de la del test. Además, B2 y B3 quedan
congelados por HTTP.

1. **Solo tests y documentación.** Ninguna fase modifica `app/`, `.azure-pipelines/`, `pyproject.toml`, `scripts/`,
   `.claude/`, `AGENTS.md` ni `CLAUDE.md`. `git diff --stat <base>..HEAD` sobre esas rutas debe salir vacío al
   final.
2. **No se crean fábricas nuevas** (adenda, punto 1). Se usan `make_user`, `make_token`, `make_auth_headers` y
   `persist_user` (`tests/conftest.py:119-208`). Se admite un fixture local que solo combina fábricas, como el
   `admin_headers` que ya existe en `tests/test_services.py:404-409`.
3. **Dobles.** El doble global de almacenamiento es `create_autospec(AzureStorageClient, instance=True)`. El correo
   se sustituye con `patch("app.api.routers.user.send_verification_email", autospec=True)` en un único fixture
   `autouse` de `tests/conftest.py`. No queda en `tests/` ningún `MagicMock(`, `AsyncMock(` ni `patch(` sin
   autospec.
4. **Forma de las aserciones:** código HTTP, `set(body) == {...}`, `isinstance(body["detail"], str)` o
   `isinstance(body["message"], str)`, estado en BD (`refresh`) y mocks verificados con `assert_called_once_with`.
   Nunca texto humano.
5. **Alcance adyacente** (adenda, punto 3): se renombran los 19 tests de `test_auth.py`; `from sqlalchemy.future`
   pasa a `from sqlalchemy` solo en `test_auth.py`; `assert_called_once_with` se aplica solo en `test_auth.py:46`.
   Las otras 10 aserciones de mock sin argumentos quedan como residual.
6. **Orden:** A → B → C → D (`m1`), E → D-bis → F (`m2`). D-bis (enmienda E3) va después de E y antes de F, y no
   es recortable. F va la última y es recortable: si no cabe en `m2`, el cierre del
   día la declara deslizada (adenda, punto 1). En ese caso se ejecuta F-mínima antes del PR del bloque (enmienda
   E2); F y F-mínima son excluyentes.
7. **Sesión (fase F):** el override abre una sesión de `TestingSessionLocal` por petición, sobre el mismo engine con
   `StaticPool` (adenda, punto 4). ADR-0011 (D1) enuncia las dos reglas: "commit antes de la petición" y "refresh
   después". Este plan **no edita `AGENTS.md`**; llevar las reglas a AGENTS §5 es tarea de David, en un PR al
   cierre.
8. **Compuerta "verde" en este ítem** (ADR-0005, trinquete). `./venv/Scripts/python.exe scripts/check.py` sale con
   exit 1 en la línea base por ruff (53 errores en `app/`) y mypy (10, todos en `app/`). Una fase se acepta si:
   pytest pasa con el número de la tabla; la cobertura es ≥ 94.81 %; import-linter da 4 KEPT; docs da OK; `ruff
   format` da OK; **cada archivo tocado tiene 0 errores de ruff**; el total de ruff es **igual** al de la tabla; mypy
   sigue en 10.
9. **Salvaguarda de la fase E** (enmienda de David). La prueba de mutantes no edita `app/`. Antes del commit de E,
   `git hash-object app/services/user_access_policy.py` tiene que ser igual a `git rev-parse
   HEAD:app/services/user_access_policy.py`. Si algún método llegara a editar ese archivo, se restaura byte a byte
   antes de seguir.

| Al cerrar | pytest (passed) | ruff total | ruff en `tests/` | mypy |
|---|---|---|---|---|
| Línea base | 376 | 60 | 7 | 10 |
| Fase A | 380 | 60 | 7 | 10 |
| Fase B | 380 | 59 | 6 | 10 |
| Fase C | 381 | 56 | 3 | 10 |
| Fase D | 381 | 56 | 3 | 10 |
| Fase E | 392 | 54 | 1 | 10 |
| Fase D-bis (enmienda E3) | 392 | 54 | 1 | 10 |
| Fase F | 396 | 54 | 1 | 10 |
| Fase F-mínima (solo si F se recorta) | 393 | 54 | 1 | 10 |

## Enmiendas aprobadas

- **E1, 4 nov 2026: aprobación del plan.** D1, D2 y D3 = sí, más la salvaguarda de la fase E. Siguen registradas donde
  estaban: en "Decisiones de David (resueltas el 4 nov 2026)", en el Análisis del redactor y en la decisión
  bloqueada 9. No se mueven.
- **E2, 4 nov 2026, 12:25: el test que vigila el `autouse` de `mock_send_email`.** David la aprobó tras la auditoría
  PASS de la fase C (`gaps.md`, fase C, opcionales 1 a 3). Texto literal:

  > "La fase F añade un test de contrato en tests/test_fixtures_contract.py que no pide el fixture mock_send_email por
  > parámetro y afirma que app.api.routers.user.send_verification_email no es la función real (es decir, que el
  > parche autouse está activo sin pedirlo). Razón: el test actual (l.50-57) pide el fixture por parámetro y pasa
  > aunque se quite autouse=True (el auditor lo verificó: 381 passed sin él); D2 se eligió para que un test que olvide
  > el fixture no envíe un correo real, y hoy ningún test lo vigila.
  > En el mismo cambio de F: la anotación de mock_send_email en test_fixtures_contract.py:50 pasa de MagicMock a Any
  > (patch(autospec=True) sobre una función devuelve una función), y el docstring del fixture mock_send_email en
  > tests/conftest.py recibe su sección Yields: (AGENTS §4).
  > Conteos: la fase F cierra con 396 tests (antes 395); la tabla de fases, la Verificación final de F y el RED
  > esperado de F se actualizan; el nuevo test empieza en verde (el autouse ya existe), así que su prueba es una
  > mutación de auditoría: quitar autouse=True del fixture debe hacerlo fallar, y se restaura.
  > Si F se recorta, estos tres puntos no se recortan con ella: pasan a una fase F-mínima (un archivo de tests más la
  > línea del docstring en conftest.py, sin el cambio de sesión ni ADR-0011), con su propio mensaje de commit, que se
  > ejecuta antes del PR del bloque."

  Cómo queda aplicada. Todo lo comprobé en HEAD `ec474e5`.
  - **Test nuevo.** El test actual está en `tests/test_fixtures_contract.py:50-57` y el fixture en
    `tests/conftest.py:115-125` (`@pytest.fixture(autouse=True)` en l.115). La función real es
    `send_verification_email` (`app/core/email.py:27`). El router la importa con `from app.core.email import
    send_verification_email` (`app/api/routers/user.py:7`). El fixture parchea solo el nombre del router
    (`patch("app.api.routers.user.send_verification_email", ...)`) y nunca `app.core.email`, así que un `from
    app.core.email import send_verification_email as real_send_verification_email` a nivel de módulo siempre
    obtiene la función real, sin activar ni esquivar el parche.
  - **Imports.** `MagicMock` solo se usa en la anotación de l.50 (import en l.3). Al pasar a `Any`, el import queda
    sin uso: se quita, se añade `from typing import Any` y el hook reordena los imports. El archivo sigue con 0
    errores de ruff y los totales no cambian (54 en total, 1 en `tests/`). `tests/` no entra en mypy
    (`pyproject.toml:90`): sigue en 10.
  - **Sondeo.** Lo hice en el scratchpad, sin tocar el repo; `git hash-object tests/conftest.py` no cambió. El test
    nuevo, junto a los 5 de `test_fixtures_contract.py`, da `6 passed` con el `conftest.py` actual cargado como
    plugin. Con un mutante sin `autouse=True` da `1 failed, 5 passed`, y el que falla es solo el test nuevo.
  - **Conteos.** F pasa de 395 a 396. F-mínima: 381 (C) + 0 (D) + 11 (E) + 1 = 393, que coincide con la fila
    E (392) + 1.
  - Se recalculan la fila F de la tabla, el RED y el criterio de F, el commit de F, la fase F-mínima nueva y los
    puntos 4b, 9 y 15 de la Verificación final, y su nota de cabecera. No cambia ninguna otra decisión.
- **E3, 4 nov 2026, 17:28: fase D-bis, las cuatro aserciones conservadas de `test_auth.py` a la decisión 4.** David
  la aprobó tras la auditoría PASS de la fase D (`gaps.md`, fase D, opcional 2). Texto literal:

  > "Añádela a 'Enmiendas aprobadas' y crea la fase D-bis, a ejecutar después de E y antes de F: un archivo,
  > tests/test_auth.py; eleva a la decisión 4 las cuatro aserciones de los tests conservados: :213 y :232 →
  > set(body) == {"detail"}; :324-325 comprueban la forma del cuerpo en la recuperación; :404-408 comprueban en la
  > base de datos la fila del admin creado. 0 tests nuevos (392 al cerrar, tras E), ruff y mypy sin cambio, su
  > mensaje de commit, y su RED: cada aserción nueva debe fallar contra una respuesta o fila manipulada (mutación de
  > auditoría sin editar app/). Recalcula la tabla y la Verificación final; no toques nada más; no implementes."

  Cómo queda aplicada. Todo comprobado en HEAD `9e2700f`.
  - **Líneas.** `tests/test_auth.py:213` y `:232` hacen `assert "detail" in response.json()`; `:324-325`, solo 200 y
    `success is True`; `:404-408`, solo la respuesta del alta. Las líneas son las de HEAD `9e2700f`.
  - **Forma de la recuperación.** La respuesta es `{"success", "cc", "correo", "nombre", "apellido", "message"}`
    (`app/services/user_service.py:359-366`). La fase D dejó fuera de alcance afirmar las claves en español, que
    son contrato con el cliente y van con P2 (residual de este plan). Por eso la forma se comprueba sobre la parte
    estable: `{"success", "message"} <= set(body)`, `success is True` y `message` de tipo str (decisión 4). La
    igualdad exacta congelaría `cc`, `correo`, `nombre` y `apellido`.
  - **Fila del admin.** El test lee la fila con `select` + `refresh` (ADR-0011: "refresh después"), así que sirve
    igual con la sesión compartida de hoy que con la sesión por petición de F.
  - **Sondeo** (scratchpad, sin tocar el repo; `git hash-object tests/test_auth.py` no cambió). Con los cuatro tests
    reescritos en un archivo de sondeo y el plugin de mutantes de la fase D-bis, cada mutante sobrevive a las
    aserciones actuales (`4 passed`) y tumba solo su test con las nuevas (2 o 1 failed; tabla en la fase D-bis).
  - **Conteos.** 0 tests nuevos: D-bis cierra en 392. F sigue en 396 y F-mínima en 393 (381 + D 0 + E 11 + D-bis 0
    + 1). Ruff 54 (1 en `tests/`) y mypy 10 no cambian: no hay imports nuevos (`select`, `User` y `UserRole` ya
    están en `test_auth.py`).
  - Se recalculan el resumen, la decisión 6, la tabla, la fase D-bis nueva, el conteo de F-mínima y el punto 6c de
    la Verificación final. No cambia ninguna otra decisión ni ninguna fase ya ejecutada.


## Análisis del redactor

**Comprobado hoy en el código (HEAD `dc09398`).** Siguen tal como las describe la verificación: `tests/conftest.py:81`
(`MagicMock()`), `:88`, `:91` y `:97` (`AsyncMock`), `:101-102` (lambdas), `:56-71` (`override_get_db` hace `yield
db_session`); `tests/test_auth.py:28` (`patch` sin autospec); los 16 `User(`, 11 `create_access_token(`, 12
`f"Bearer {` y 4 `get_password_hash("pass")` de `test_auth.py`; las 8 aserciones en español (l.58, 85, 122, 131,
160-163, 360, 565, 609); `tests/test_audit.py:13-28` y `:69-83`; `tests/test_services.py:34-64`, que usan 13 tests;
`:234`; y `mock_send_email` duplicado (`test_auth.py:22-29`, `test_user_response.py:43-47`). La línea base de los
patrones de detección coincide: `User(` fuera de conftest = 19 (audit 2, auth 16, services 1); tokens = 14; `Bearer`
= 15; mocks sin argumentos = 11; ruff = `Found 60 errors.`. Nadie lee `container_name` ni `temporal_container_name`
del doble: `grep -rn container_name tests/ app/` solo los encuentra en `tests/conftest.py:84-85` y dentro de
`app/core/storage.py`. Por eso la fase A los quita.

**Ensayo en seco de (4)** (scratchpad; no se modificó ningún archivo del repo y `git status` siguió limpio). Copié
`tests/conftest.py` a un plugin con un único cambio: el override hace `async with TestingSessionLocal() as session:
yield session`. Lo ejecuté con `pytest --noconftest -p <plugin>` y el resultado fue `1 failed, 375 passed`. El único
fallo es `test_auth.py::test_borrado_logico_usuario` (l.166-169): relee con `select` un `User` que ya tenía en el
mapa de identidad y ve `deleted_at = None`. La estimación de "~70 llamadas en riesgo" se queda en un test, que la
fase C reescribe con `refresh`. Por eso F no necesita tocar otros tests. Si al ejecutarla aparece algún fallo, la
fase tiene hueco para dos archivos más (ver F).

**Sondeos de API** (con el intérprete del proyecto: Python 3.14.3, SQLAlchemy 2.0.48, aiosqlite 0.22.1).
(a) `create_autospec(cls, instance=True)` convierte los métodos `async` en `AsyncMock` con firma. Una llamada con
firma incorrecta lanza `TypeError` al llamar; un atributo inexistente lanza `AttributeError`; `isinstance(doble, cls)`
es `True`; `side_effect` acepta una función normal o una corrutina.
(b) `patch(..., autospec=True)` sobre una función `async` no lanza el `TypeError` al llamar, sino **al hacer
`await`**, y en ese caso no registra la llamada. Un `patch` sin autospec acepta cualquier argumento.
(c) Con `StaticPool`, dos sesiones comparten conexión. Un re-`select` devuelve el objeto viejo y `refresh` devuelve
el nuevo. El `flush()` sin `commit()` de la app desaparece al cerrarse su sesión. El `flush()` sin `commit()` del
test **también** desaparece al cerrarse la sesión de la app, por el `rollback` que hace el pool al recibir la
conexión. De ahí sale la convención "commit antes de la petición".

**Orden y dependencias.** A no depende de nadie y crea `tests/test_fixtures_contract.py`; C y F le añaden tests. B es
independiente de A, pero va después para que `test_services.py` se toque en dos commits pequeños y se puedan leer.
C → D: las dos reescriben `test_auth.py` por secciones (l.1-175 y l.177-657). C deja el archivo con 0 errores de ruff
porque los tres errores (l.1, 50 y 162) caen en su sección. C → F: C reescribe con `refresh` el único test que
rompería F. E es independiente de todas; va en `m2` por la adenda. D-bis (enmienda E3) depende de D, porque toca
tests que D reescribió, y va antes de F para que F se mida sobre la suite final de `test_auth.py`.

**Qué congela qué.** Los 4 tests nuevos de A congelan el contrato del doble de almacenamiento: tiene firma y reproduce
las reglas de URL del CDN. Los tests de `test_services.py` que usan el doble global (l.191-250 y 295-367) siguen
cubriendo su comportamiento. En B y D no cambia el comportamiento: la red son los mismos tests, que deben seguir
pasando (36 en `test_services.py`, 6 en `test_audit.py`, 19 en `test_auth.py`). Las aserciones de texto que se quitan
en C y D no pierden su poder de distinguir errores, porque la distinción entre `AccountNotActiveError`,
`InvalidCredentialsError`, `AlreadyExistsError` y `AuthorizationError` ya la congelan por tipo
`tests/test_user_service.py:114-122` y `:202-233` y `tests/test_user_access_policy.py:115-216`. Los tests HTTP
afirman el código, la forma `{"detail": str}` y la **ausencia de mutación**. Los 11 casos de E congelan B2 y B3 en la
capa HTTP. Su RED es imposible sin tocar `app/` (los bugs ya están corregidos), así que se sustituye por una prueba de
sensibilidad con mutantes cargados como plugin, sin editar `app/`. La salvaguarda de la decisión 9 lo comprueba por
hash. Los 3 tests de F congelan la sesión por petición.

**Riesgos.** (1) F cambia la semántica de la suite. Mitigación: el ensayo en seco, C antes que F, el ADR y la
docstring de `client`. (2) C y D son diffs grandes sobre un solo archivo; se mitiga partiéndolos por secciones y
manteniendo el número de tests. (3) Un `mock_send_email` `autouse` global parchea el correo en **todos** los tests;
es inocuo, porque solo sustituye un nombre en `app.api.routers.user`, y además evita SMTP real en tests futuros (D2).
(4) `tests/test_services.py:223` recupera el doble global con `app.dependency_overrides[get_storage_client]()` y
llama a `assert_not_awaited()`; con autospec sigue funcionando (sondeo a).

**Qué NO se toca.** `app/` (B2–B4 ya están corregidos, `user_access_policy.py:53-63`); el `--soft` del CI (`B-TESTS
m4`); la clave `"detalle"` (`test_services.py:767,782`, `test_user_response.py:166,205`, P2); `load_dotenv` y
`JWT_SECRET_KEY` (A4, adenda punto 2); la auto-degradación del superadmin (BE-02); `sqlite_where` (BE-31); `from
sqlalchemy.future` fuera de `test_auth.py` (S2).

**Decisiones de David (resueltas el 4 nov 2026).**
- **D1 = sí: ADR-0011, corto.** Contiene la decisión (una sesión por petición, aparte de la del test), el límite
  aceptado (la conexión es compartida por `StaticPool`; el aislamiento es de sesión, no de transacción; el commit
  olvidado se detecta al cerrarse la sesión de la app) y las alternativas (sesión compartida, conexiones separadas,
  Postgres → BE-31). El ADR enuncia las dos reglas. El borrador está en `docs/deuda/BE-15/adr-0011-borrador.md` y la
  fase F lo copia a `docs/adr/`. **AGENTS.md no se edita en este plan:** David lleva las reglas a AGENTS §5 por PR
  al cierre.
- **D2 = sí:** un `mock_send_email` `autouse` en `tests/conftest.py`, con `autospec=True`.
- **D3 = sí:** en C, `test_login_credenciales_invalidas` pasa a "contraseña incorrecta de una cuenta activa"
  (`test_login_wrong_password_returns_401_with_bearer_challenge`). El correo inexistente ya está por HTTP en
  `test_user_service.py:363-372`.
- **Salvaguarda E:** decisión bloqueada 9.

## Regla de alcance

- **Sí:** `tests/conftest.py`, `tests/test_auth.py`, `tests/test_audit.py`, `tests/test_services.py`,
  `tests/test_user_response.py`, `tests/test_user_access_policy.py`, `tests/test_fixtures_contract.py` (nuevo) y
  `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`. Dentro de cada archivo tocado, los errores
  de ruff hasta dejarlo en 0. En F, hasta dos archivos de test más si se rompen por la sesión, y solo para añadir
  `refresh`.
- **No:** todo lo listado en "Qué NO se toca"; `AGENTS.md` y `CLAUDE.md` (las reglas de ADR-0011 las lleva David a
  AGENTS §5 por PR al cierre); `tests/test_user_service.py` (su I001 queda como residual); las 10
  aserciones de mock sin argumentos fuera de `test_auth.py`; comentarios en español fuera de las líneas que se
  reescriben; los tests duplicados entre `test_auth.py` y `test_user_access_policy.py` (se migran, no se borran: el
  conteo no baja).

## Fases

### Fase A — El doble global de almacenamiento con la firma de `AzureStorageClient` (la más pequeña)
- **Archivos:** `tests/conftest.py`, `tests/test_services.py`, `tests/test_fixtures_contract.py` (nuevo).
- **Cambios exactos:**
  - `conftest.py`, en `override_azure_storage_client`: `mock_client = create_autospec(AzureStorageClient,
    instance=True)`. Se conservan los valores: `upload_image.return_value` = la misma URL temporal;
    `delete_image.return_value = None`; `promote_to_permanent.side_effect = mock_promote`; `is_temporal_url` e
    `is_permanent_url` como `.side_effect = lambda url: ...` con los mismos prefijos. Se borran las dos asignaciones
    de `container_name` y `temporal_container_name` (no las lee nadie). La docstring deja de hablar de "environment
    variables" y explica que el doble lleva la firma del adaptador. Imports: fuera `AsyncMock` y `MagicMock`; dentro
    `create_autospec` y `from app.core.storage import AzureStorageClient`.
  - `test_services.py:234`: `failing_client.upload_image.side_effect = StorageUnavailableError("cdn outage")`. Se
    quita `AsyncMock` del import de la l.11.
  - `test_fixtures_contract.py` (nuevo): una docstring de módulo en inglés ("Contract tests for the shared doubles and
    sessions of tests/conftest.py.") y 4 tests a nivel de módulo, sin clases. Todos obtienen el doble con
    `app.dependency_overrides[get_storage_client]()`.
- **Tests (RED primero):** se escriben con el `conftest.py` actual y se comprueba que los 3 primeros fallan.
  1. `test_storage_double_is_specced_on_the_adapter`: `isinstance(double, AzureStorageClient)`. RED, porque un
     `MagicMock` no es instancia del adaptador.
  2. `test_storage_double_rejects_unknown_attribute`: `assert not hasattr(double, "upload_images")`. RED, porque
     `MagicMock` crea cualquier atributo.
  3. `test_storage_double_rejects_a_call_off_the_adapter_signature`, `async`: `with pytest.raises(TypeError): await
     double.upload_image()`. RED, porque el `AsyncMock` actual no tiene firma.
  4. `test_storage_double_mirrors_the_cdn_url_rules`, `async`: con `TEMP = ".../temp-ecotur-images/a.jpg"` y `PERM =
     ".../ecotur-images/a.jpg"` (prefijo `https://ecoturasopradocdn2026.blob.core.windows.net/`), comprueba que
     `await double.promote_to_permanent(TEMP) == PERM`, `double.is_temporal_url(TEMP) is True`,
     `double.is_permanent_url(TEMP) is False`, `double.is_permanent_url(PERM) is True` y
     `double.promote_to_permanent.assert_awaited_once_with(TEMP)`. Pasa antes y después: congela el comportamiento
     que la reescritura no puede cambiar.
- **Criterio de aceptación:** compuerta según la decisión 8 con la fila "Fase A" (380 passed; ruff 60; 0 en los
  tres archivos). `grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py | wc -l` → 0.
  Los 36 tests de `test_services.py` siguen pasando.
- **Fuera de alcance:** el `patch` de `test_auth.py:28` (se elimina en C); el decorador `@pytest_asyncio.fixture` de
  un fixture síncrono; el fixture `storage_double` de `test_services.py:391-401`, que ya es autospec.
- **Commit:**
  ```
  test(conftest): give the global storage double the adapter's autospec

  The autouse override in tests/conftest.py replaced AzureStorageClient
  with a bare MagicMock and unspecced AsyncMocks, so renaming or
  re-signing an adapter method broke no test (AGENTS 5, BE-15 point 1).

  - tests/conftest.py: the double is create_autospec(AzureStorageClient,
    instance=True); same return values and URL rules as before, set as
    return_value/side_effect. The container-name attributes are gone:
    nothing read them.
  - tests/test_services.py: the 503 test sets side_effect on the
    autospecced method instead of swapping it for an unspecced AsyncMock.
  - tests/test_fixtures_contract.py: new; freezes that the double is an
    adapter instance, rejects unknown attributes and wrong signatures,
    and keeps the CDN URL rules.
  ```

### Fase B — `test_services.py` y `test_audit.py` sobre las fábricas centrales
- **Archivos:** `tests/test_services.py`, `tests/test_audit.py`.
- **Cambios exactos:**
  - `test_services.py`: se borran los fixtures `admin_token` (l.34-58) y `auth_headers` (l.61-64). El fixture
    `admin_headers` (l.404-409) se mueve al bloque "TEST FIXTURES". En los 13 tests (l.100, 128, 157, 191, 210, 227,
    253, 261, 269, 279, 287, 295, 318) el parámetro y el uso `auth_headers` pasan a `admin_headers`. Se quitan los
    imports que quedan sin uso (`create_access_token`, `get_password_hash`, `User`).
  - `test_audit.py`: se borra el fixture `superadmin_token` (l.13-28). En `test_audit_trail_creation_and_retrieval`,
    los parámetros pasan a ser `client, persist_user, make_auth_headers`; el test crea `superadmin = await
    persist_user(role=UserRole.superadmin)` y `headers = make_auth_headers(superadmin)`. En
    `test_audit_trail_forbidden_for_tourist`, el test crea `tourist = await persist_user(role=UserRole.tourist)` y
    usa `make_auth_headers(tourist)`; además de comprobar el 403, comprueba `isinstance(response.json()["detail"],
    str)`. Se quitan los imports sin uso. El hook corrige el I001 de la l.1.
- **Tests (RED primero):** no aplica, porque es un refactor de la preparación sin cambio de comportamiento. La red de
  seguridad: `./venv/Scripts/python.exe -m pytest --collect-only -q tests/test_services.py tests/test_audit.py`
  antes y después tiene que dar la misma lista de IDs (36 + 6) y todos los tests tienen que pasar.
- **Criterio de aceptación:** fila "Fase B" (380 passed; ruff 59; 0 en los dos archivos). En estos dos archivos:
  `User(`, `create_access_token(`, `f"Bearer {` → 0, y `def (admin_token|auth_headers|superadmin_token)\(` → 0.
- **Fuera de alcance:** el comentario en español de `test_audit.py:37`; `from sqlalchemy.future` de
  `test_services.py:14`; las aserciones sobre `"detalle"` (l.767, 782); `assert_awaited_once()` de l.245 y 520.
- **Commit:**
  ```
  test(fixtures): move services and audit setup to central factories

  tests/test_services.py kept a local admin_token/auth_headers pair that
  built a User, hashed a password and signed a token by hand, next to an
  admin_headers fixture already built on the conftest factories: two
  mechanisms in one file. tests/test_audit.py did the same for a
  superadmin and a tourist (AGENTS 5, BE-15 point 2).

  - tests/test_services.py: the 13 tests that used auth_headers now use
    admin_headers (persist_user + make_auth_headers); the local pair is
    removed.
  - tests/test_audit.py: superadmin and tourist come from persist_user
    and make_auth_headers; the forbidden case also checks the detail type.

  Same test IDs before and after; no behaviour change.
  ```

### Fase C — `test_auth.py`, sección de registro, login y auto-borrado, más un único `mock_send_email`
- **Archivos:** `tests/conftest.py`, `tests/test_user_response.py`, `tests/test_auth.py` (l.1-175),
  `tests/test_fixtures_contract.py`.
- **Cambios exactos:**
  - `conftest.py` (D2): se añade el fixture `mock_send_email`, con `@pytest.fixture(autouse=True)` en la línea
    inmediatamente anterior a `def mock_send_email():`. Hace `with
    patch("app.api.routers.user.send_verification_email", autospec=True) as mock: yield mock` y lleva docstring.
    Import: `patch`.
  - `test_user_response.py`: se borra el fixture local (l.43-47) y `patch` del import de la l.12 (se queda `ANY`).
  - `test_auth.py`: se borra el fixture local (l.21-29) y el import de `patch`; `from sqlalchemy.future import select`
    pasa a `from sqlalchemy import func, select`. Se añaden la constante `PASSWORD = USER_PAYLOAD["password"]` y los
    imports `jwt`, `ANY` y `ALGORITHM, SECRET_KEY`. Los 8 tests se reescriben así:

  | Antes | Después | Preparación → aserciones |
  |---|---|---|
  | `test_registro_usuario_exitoso` | `test_register_tourist_returns_201_and_schedules_verification_email` | POST registro → se conservan las aserciones de l.36-43; `mock_send_email.assert_called_once_with(email_to=USER_PAYLOAD["email"], first_name="Juan", token=ANY, base_url=ANY)`; fila por cédula con `is_active is False` y `role == UserRole.tourist` |
  | `test_registro_usuario_duplicado` | `test_register_duplicate_returns_400_without_second_row` | 2 POST → el segundo devuelve 400, `set(body) == {"detail"}` y `detail` de tipo str; `count(User) == 1`; el correo se envía una sola vez (`assert_called_once_with`, los mismos argumentos) |
  | `test_verificacion_email_exitosa` | `test_verify_email_endpoint_activates_account` | `persist_user(is_active=False)`, token con `create_verification_token(user.email)` → 200, `set(body) == {"success", "message"}`, `success is True`; `refresh(user)` → `is_active is True` |
  | `test_verificacion_email_token_invalido` | `test_verify_email_invalid_token_returns_400` | → 400, `set(body) == {"detail"}`, `detail` de tipo str |
  | `test_login_exitoso` | `test_login_active_user_returns_bearer_token` | `persist_user(password_hash=get_password_hash(PASSWORD), is_active=True)` → 200, `set(body) == {"access_token", "token_type"}`, `token_type == "bearer"`; claims con `jwt.decode`: `sub == user.email`, `role == "tourist"` |
  | `test_login_usuario_inactivo` | `test_login_inactive_user_returns_403_without_token` | igual, con `is_active=False` → 403, `set(body) == {"detail"}`, `detail` de tipo str |
  | `test_login_credenciales_invalidas` | `test_login_wrong_password_returns_401_with_bearer_challenge` | cuenta activa con hash real, contraseña `"wrongPassword1"` → 401, cabecera `www-authenticate == "Bearer"`, `set(body) == {"detail"}` (D3) |
  | `test_borrado_logico_usuario` | `test_self_soft_delete_keeps_row_and_blocks_login` | cuenta activa con hash real, `make_auth_headers(user)` → DELETE propio: 200, `set(body) == {"success", "message"}`, `success is True`, `message` de tipo str; `refresh(user)` → `deleted_at is not None`, `is_active is False`; el login posterior da 401 |

  - `test_fixtures_contract.py`: se le añade 1 test.
- **Tests (RED primero):** `test_email_dispatch_double_is_autouse_and_autospecced(mock_send_email)`, `async`.
  Comprueba `from app.api.routers import user as user_router; assert user_router.send_verification_email is
  mock_send_email`, después `with pytest.raises(TypeError): await mock_send_email(recipient="x")` y por último
  `mock_send_email.assert_not_called()`. Es RED antes del cambio en conftest: `fixture 'mock_send_email' not found`.
  Los 8 tests reescritos no tienen RED (refactor y endurecimiento): deben pasar con el número de tests intacto (19 en
  `test_auth.py`).
- **Criterio de aceptación:** fila "Fase C" (381 passed; ruff 56; 0 en los cuatro archivos). `grep -rnE
  "def mock_send_email\(" tests/ --include=*.py` → 1 (conftest). En `test_auth.py`, l.1-175: ninguna aserción sobre
  `["detail"] ==`, `.lower()` ni `["message"] ==`; 0 `sqlalchemy.future`; los 8 nombres nuevos.
- **Fuera de alcance:** los 11 tests de l.177-657 (fase D); el `"detalle"` de `test_user_response.py:166,205`.
- **Commit:**
  ```
  test(auth): assert codes, not Spanish text, in registration and login

  The registration, verification, login and self-deletion tests in
  tests/test_auth.py compared Spanish user-facing messages (five of the
  eight BE-15 point 3 assertions), built and activated users by hand
  through the test session, and patched the email dispatch without a
  spec in a fixture duplicated in tests/test_user_response.py.

  - tests/conftest.py: one autouse mock_send_email, autospecced on
    send_verification_email.
  - tests/test_user_response.py: drops its local copy.
  - tests/test_auth.py: eight tests renamed to English; arrange through
    persist_user; assertions on status, JSON keys, detail/message type,
    DB state (refresh) and email-call arguments; sqlalchemy.future ->
    sqlalchemy. The invalid-credentials case now covers a wrong password
    (unknown email is already covered over HTTP in test_user_service).
  - tests/test_fixtures_contract.py: freezes that the email double is
    autouse and autospecced.
  ```

### Fase D — `test_auth.py`, sección RBAC y gestión de usuarios, sobre las fábricas
- **Archivos:** `tests/test_auth.py` (l.177-657).
- **Cambios exactos:** en los 11 tests, `User(...)`, `add`/`add_all`/`commit` y `create_access_token` +
  `f"Bearer {..}"` pasan a `persist_user(role=..., is_active=..., deleted_at=...)` + `make_auth_headers(actor)`. Los
  tres tests que registraban por HTTP y activaban a mano (l.182, 216, 245) usan `persist_user(role=UserRole.tourist)`.
  Toda relectura posterior a la petición se hace con `await db_session.refresh(obj)`. Cambios de nombre y de
  aserciones:

  | Antes | Después | Aserciones que cambian |
  |---|---|---|
  | `test_actualizacion_perfil_self_service_exitoso` | `test_tourist_self_update_persists_profile_change` | — (se conservan) |
  | `test_actualizacion_perfil_escalacion_rol_rechazada` | `test_tourist_self_role_escalation_returns_403_without_mutation` | — |
  | `test_actualizacion_perfil_mutacion_estado_rechazada` | `test_tourist_self_is_active_change_returns_403_without_mutation` | — |
  | `test_actualizacion_usuario_helpdesk_exitoso` | `test_admin_updates_tourist_email_and_persists_it` | + `refresh(tourist)`, `tourist.email == "correo_corregido@asoprado.com"` |
  | `test_actualizacion_usuario_violacion_jerarquia` | `test_admin_patching_superadmin_returns_403_without_mutation` | l.360 → `set(body) == {"detail"}`, `detail` de tipo str; `refresh(superadmin)`, `first_name` sin cambios |
  | `test_listar_usuarios_visibilidad_jerarquica` | `test_admin_directory_hides_superadmins` | `{u["cedula"] for u in body} == {tourist.cedula, admin.cedula}` |
  | `test_listar_usuarios_eliminados_visibilidad` | `test_admin_deleted_directory_hides_deleted_superadmins` | `[u["cedula"] for u in body] == [deleted_tourist.cedula]` |
  | `test_recuperar_usuario_exitoso` | `test_admin_recovers_tourist_as_inactive` | — |
  | `test_recuperar_usuario_violacion_jerarquia` | `test_admin_recovering_superadmin_returns_403_without_mutation` | l.565 → `set(body) == {"detail"}`; `refresh(superadmin)`, `deleted_at is not None` |
  | `test_crear_administrador_violacion_jerarquia` | `test_admin_provisioning_admin_returns_403_without_row` | l.609 → `set(body) == {"detail"}`; `count(User) == 1` |
  | `test_crear_administrador_exitoso` | `test_superadmin_provisions_admin_account` | — |

  Se quitan los imports sin uso (`create_access_token` y los que queden).
- **Tests (RED primero):** no aplica: es un refactor de la preparación y un endurecimiento de aserciones sobre
  comportamiento existente. La red: 19 tests en `test_auth.py` antes y después, todos en verde.
- **Criterio de aceptación:** fila "Fase D" (381 passed; ruff 56; `test_auth.py` en 0). En `test_auth.py`: `User(`,
  `create_access_token(`, `f"Bearer {`, `get_password_hash("pass")` → 0, y ningún `def test_` con nombre en español.
- **Fuera de alcance:** borrar los duplicados de `test_user_access_policy.py:274-291` y `:344-369` (residual); las
  claves en español de la respuesta de recuperación (`cc`, `correo`, `nombre`, `apellido`): no se afirman.
- **Commit:**
  ```
  test(auth): build RBAC management tests with the central factories

  The eleven RBAC tests of tests/test_auth.py created users with
  hand-written User(...) rows, hashed passwords and signed tokens one by
  one, and three of them still asserted Spanish detail text (BE-15
  points 2 and 3).

  Users now come from persist_user and headers from make_auth_headers;
  every read after a request goes through refresh; the three 403 cases
  assert the detail shape plus no mutation; directory tests compare the
  exact cedula sets. Tests renamed to English (AGENTS 4). Same count.
  ```

### Fase E — Regresiones de B2 y B3 por HTTP
- **Archivos:** `tests/test_user_access_policy.py`.
- **Cambios exactos:** en la sección B (integración) se añaden 10 tests, que dan 11 casos con la parametrización.
  Todos usan `persist_user` y `make_auth_headers`, y comprueban el estado con `refresh` y, si aplica, con
  `select(AuditLog)`. Para que el archivo quede en 0 errores de ruff, las docstrings de l.347 y l.395 se acortan a
  `"""Admin provisioning an admin account yields 403 and persists nothing."""` y `"""Admin promoting a tourist to
  superadmin yields 403 with no mutation."""`. No se toca el import `sqlalchemy.future` de l.13.
  - **B2** (PATCH sobre la propia cédula de un admin):
    1. `test_b2_admin_self_promotion_to_superadmin_returns_403_without_mutation`: con `{"role": "superadmin"}` →
       403, `set(body) == {"detail"}`; `refresh(admin)` → `role == UserRole.admin`; `select(AuditLog)` vacío.
    2. `test_b2_admin_self_demotion_to_tourist_returns_403`: con `{"role": "tourist"}` → 403; el rol no cambia.
    3. `test_b2_admin_self_update_without_role_returns_200`: con `{"first_name": "Changed"}` → 200,
       `body["first_name"] == "Changed"`; tras `refresh`, `first_name == "Changed"` y `role == UserRole.admin`.
    4. `test_b2_admin_self_role_noop_returns_403`: con `{"role": "admin"}` → 403. Lo que se bloquea es la clave, no el
       valor.
    5. `test_b2_admin_self_promotion_with_profile_fields_mutates_nothing`: con `{"role": "superadmin", "first_name":
       "Changed"}` → 403; `first_name` y `role` siguen como antes.
  - **B3** (DELETE):
    6. `test_b3_superadmin_deletes_third_party_account`, parametrizado con `target_role` ∈ {`admin`, `tourist`} → 200,
       `set(body) == {"success", "message"}`, `success is True`; `refresh(target)` → `deleted_at is not None`,
       `is_active is False`; una sola fila `AuditLog` con `entity_id == target.cedula`, `action ==
       AuditAction.SOFT_DELETE` y `performed_by == superadmin.cedula`.
    7. `test_b3_superadmin_deleting_peer_superadmin_returns_403_without_mutation`: 403; `deleted_at is None`.
    8. `test_b3_admin_deleting_peer_admin_returns_403_without_mutation`: 403; `deleted_at is None`.
    9. `test_b3_superadmin_deleting_already_deleted_account_returns_404`: el objetivo se crea con
       `deleted_at=datetime.now(UTC), is_active=False` → 404, `set(body) == {"detail"}`; no hay `AuditLog`.
    10. `test_b3_superadmin_deleting_missing_cedula_returns_404`: `/usuarios/9999999999` → 404, `set(body) ==
        {"detail"}`.
- **Tests (RED primero):** no se puede tener RED sin tocar `app/`, porque los bugs ya están corregidos. En su lugar
  se hace una **prueba de sensibilidad con mutantes**, que va al handoff. En el scratchpad se crea `be15_mutants.py`
  con un fixture `autouse` que, mediante `monkeypatch`, sustituye `UserAccessPolicy.assert_can_update` por una
  función que no hace nada y `UserAccessPolicy.assert_can_delete` por una que lanza
  `AuthorizationError()`. Se ejecuta `PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -p be15_mutants
  -p no:cacheprovider tests/test_user_access_policy.py -k "b2_ or b3_" -q` y el resultado esperado es **`6 failed, 5
  passed`**: fallan 1, 2, 4, 5 y los dos casos de 6; pasan 3, 7, 8, 9 y 10. Sin el plugin: 11 passed. El plugin
  vive fuera del repo y no edita `app/`. Si se usara cualquier otro método que editara
  `app/services/user_access_policy.py`, el archivo se restaura byte a byte (decisión 9) antes de seguir.
- **Criterio de aceptación:** fila "Fase E" (392 passed; ruff 54; `test_user_access_policy.py` en 0). `grep -cE
  "^async def test_b[23]_" tests/test_user_access_policy.py` → 10. La prueba de sensibilidad da exactamente `6
  failed, 5 passed`. **Paso obligatorio antes del commit**, con su salida literal en el handoff:
  `test "$(git hash-object app/services/user_access_policy.py)" = "$(git rev-parse
  HEAD:app/services/user_access_policy.py)" && echo IGUAL` → `IGUAL`, y `git status --short app/` → vacío. Si no
  da `IGUAL`, no se hace el commit.
- **Fuera de alcance:** cambiar la política (BE-02: un superadmin que cambia su propio rol); tests de B4 (ya
  cubierto); `sqlalchemy.future` en l.13.
- **Commit:**
  ```
  test(access-policy): freeze B2 self-promotion and B3 third-party delete

  The audit's B2 (an admin promoting their own account to superadmin) and
  B3 (a superadmin unable to delete someone else's account) were fixed in
  app/services/user_access_policy.py, but no test named either scenario:
  B2 was covered only for admin -> tourist targets and B3 only at unit
  level (BE-15 point 6).

  Five B2 cases PATCH the admin's own cedula (role up, down, unchanged,
  mixed with profile fields, and a role-free update that must pass); six
  B3 cases DELETE over HTTP (superadmin on an admin and a tourist with
  deleted_at and an audit row naming the actor, peer 403s, 404 for a
  deleted or missing cedula). A mutant run that disables the two policy
  checks turns exactly the six expected cases red.
  ```

### Fase D-bis — Las cuatro aserciones conservadas de `test_auth.py`, a la decisión 4 (enmienda E3)
- **Archivos:** `tests/test_auth.py` (solo los cuatro tests de abajo).
- **Cambios exactos** (líneas de HEAD `9e2700f`):
  1. `test_tourist_self_role_escalation_returns_403_without_mutation`, l.213: `assert "detail" in response.json()`
     pasa a `body = response.json()`, `assert set(body) == {"detail"}` y `assert isinstance(body["detail"], str)`.
  2. `test_tourist_self_is_active_change_returns_403_without_mutation`, l.232: el mismo cambio.
  3. `test_admin_recovers_tourist_as_inactive`, l.324-325: tras `assert response.status_code == 200`, `body =
     response.json()`, `assert {"success", "message"} <= set(body)`, `assert body["success"] is True` y `assert
     isinstance(body["message"], str)`. No se afirman `cc`, `correo`, `nombre` ni `apellido` (P2; ver E3).
  4. `test_superadmin_provisions_admin_account`, l.404-408: recibe además `db_session`; se conservan las tres
     aserciones sobre la respuesta y se añaden:
     ```python
     result = await db_session.execute(select(User).where(User.cedula == "555555"))
     created = result.scalar_one()
     await db_session.refresh(created)
     assert created.role == UserRole.admin
     assert created.is_active is True
     assert created.deleted_at is None
     ```
  Nada más cambia en el archivo: ni nombres, ni docstrings, ni imports, ni los otros 15 tests.
- **Tests (RED primero):** 0 tests nuevos. El RED es una **mutación de auditoría que no edita `app/` ni el repo**:
  cada mutante manipula una respuesta o una fila, sobrevive a las aserciones actuales y tumba la nueva. Plugin
  `dbis_mutants.py` en el scratchpad (el prefijo `dbis_` evita choques en el scratchpad compartido), con el mutante
  elegido por la variable `DBIS_MUTANT`:
  ```python
  import os
  from datetime import UTC, datetime

  import httpx
  import pytest
  from sqlalchemy import update

  from app.models.user import User, UserRole
  from app.repositories.user_repository import UserRepository

  MUTANT = os.environ.get("DBIS_MUTANT", "")
  ROW_VALUES = {
      "row_role": {"role": UserRole.tourist},
      "row_is_active": {"is_active": False},
      "row_deleted_at": {"deleted_at": datetime.now(UTC)},
  }

  def _rebuild(response, body):
      headers = {k: v for k, v in response.headers.items()
                 if k.lower() not in ("content-length", "content-encoding")}
      return httpx.Response(response.status_code, headers=headers, json=body, request=response.request)

  @pytest.fixture(autouse=True)
  def _dbis_mutant(monkeypatch):
      if MUTANT in ("extra_key_403", "detail_not_str_403", "recover_no_message", "recover_message_not_str"):
          real_send = httpx.AsyncClient.send

          async def send(self, request, **kwargs):
              response = await real_send(self, request, **kwargs)
              recover = request.url.path.endswith("/recuperar") and response.status_code == 200
              if MUTANT == "extra_key_403" and response.status_code == 403:
                  return _rebuild(response, {**response.json(), "code": "x"})
              if MUTANT == "detail_not_str_403" and response.status_code == 403:
                  return _rebuild(response, {"detail": {"msg": response.json()["detail"]}})
              if MUTANT == "recover_no_message" and recover:
                  body = response.json()
                  body.pop("message")
                  return _rebuild(response, body)
              if MUTANT == "recover_message_not_str" and recover:
                  return _rebuild(response, {**response.json(), "message": None})
              return response

          monkeypatch.setattr(httpx.AsyncClient, "send", send)
      elif MUTANT in ROW_VALUES:
          real_create = UserRepository.create_user

          async def create_user(self, user):
              created = await real_create(self, user)
              await self.db.execute(
                  update(User).where(User.cedula == user.cedula).values(**ROW_VALUES[MUTANT])
                  .execution_options(synchronize_session=False)
              )
              await self.db.commit()
              return created

          monkeypatch.setattr(UserRepository, "create_user", create_user)
  ```
  Los mutantes de fila cambian la fila con `synchronize_session=False`. Como `expire_on_commit=False`, el objeto en
  memoria (y por tanto la respuesta) sigue diciendo admin, activo y sin borrar; solo la relectura con `refresh` lo
  ve. Comando, por cada mutante:
  `DBIS_MUTANT=<m> PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -p
  dbis_mutants tests/test_auth.py -k "tourist_self_role_escalation or tourist_self_is_active_change or
  admin_recovers_tourist or superadmin_provisions_admin"`.

  | `DBIS_MUTANT` | Antes de editar (RED: el hueco) | Después de editar | Test que cae |
  |---|---|---|---|
  | (vacío) | `4 passed` | `4 passed` | — |
  | `extra_key_403` | `4 passed` | `2 failed, 2 passed` | 1 y 2 (`set(body)`) |
  | `detail_not_str_403` | `4 passed` | `2 failed, 2 passed` | 1 y 2 (`isinstance`) |
  | `recover_no_message` | `4 passed` | `1 failed, 3 passed` | 3 (forma) |
  | `recover_message_not_str` | `4 passed` | `1 failed, 3 passed` | 3 (`message` str) |
  | `row_role` | `4 passed` | `1 failed, 3 passed` | 4 (`role`) |
  | `row_is_active` | `4 passed` | `1 failed, 3 passed` | 4 (`is_active`) |
  | `row_deleted_at` | `4 passed` | `1 failed, 3 passed` | 4 (`deleted_at`) |

  Las dos columnas, con su salida literal y `-rf` para nombrar el test que cae, van al handoff.
- **Criterio de aceptación:** fila "Fase D-bis" (392 passed; ruff 54, 1 en `tests/`; `test_auth.py` en 0; mypy 10;
  cobertura ≥ 94.81 %; 4 KEPT). `test_auth.py` sigue con 19 tests y los mismos nombres. `grep -c 'assert "detail" in
  response.json()' tests/test_auth.py` → 0; `grep -c 'set(body) == {"detail"}' tests/test_auth.py` → 9 (7 de C y D,
  más 2). La tabla de mutantes da exactamente esas cifras. Antes del commit: `git diff --stat HEAD` solo muestra
  `tests/test_auth.py`, y `git status --short app/` sale vacío.
- **Fuera de alcance:** afirmar las claves en español de la recuperación (P2); la distinción entre causas de 403
  (opcional 1 de la fase D, backlog); cualquier otro test de `test_auth.py`; `app/`.
- **Commit:**
  ```
  test(auth): raise four kept RBAC assertions to the decision 4 form

  Phase D kept four assertions of tests/test_auth.py as they were, and
  its audit (optional 2) found them weaker than the plan's decision 4:
  two 403 cases only checked that "detail" was a key, the recovery case
  did not check the body shape, and the admin provisioning case never
  looked at the database.

  - The two tourist self-update 403s assert set(body) == {"detail"} and
    a str detail.
  - Recovery asserts success and a str message, without freezing the
    Spanish data keys (P2).
  - Provisioning reads the new row back with refresh and asserts role
    admin, active and not deleted.

  Same count. Response and row mutants that the old assertions let pass
  now turn exactly the targeted test red.
  ```

### Fase F — Una sesión por petición para la app (recortable)
- **Archivos:** `tests/conftest.py`, `tests/test_fixtures_contract.py`,
  `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`. Hueco para 2 archivos de test más, solo
  para añadir `refresh` si algún test se rompe. Si se rompen 3 o más, la fase se detiene en `partial` y se informa.
- **Cambios exactos:**
  - `conftest.py`, fixture `client`: deja de recibir `db_session`; el override pasa a ser `async def
    override_get_db(): async with TestingSessionLocal() as session: yield session`. La docstring de `client` enuncia
    las dos convenciones (confirmar con `commit()` lo preparado antes de la petición; hacer `refresh` de los objetos
    ya cargados después) y cita ADR-0011. La docstring de `db_session` dice que es la sesión del test y que la app
    nunca la recibe.
  - `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`: copia literal de
    `docs/deuda/BE-15/adr-0011-borrador.md` con dos cambios: se borra el bloque de cita inicial (las líneas que
    empiezan por `>` y la línea en blanco que les sigue) y se quita " (borrador)" del título. El estado ya es "aceptado". El borrador se queda en esta
    carpeta como registro.
  - `test_fixtures_contract.py`: se le añaden 3 tests `async` que reciben `client` (instala el override) y
    `db_session`. Cada uno obtiene el generador con `app.dependency_overrides[get_db]()` y lo cierra con
    `aclose()`.
  - `test_fixtures_contract.py` (enmienda E2):
    - se añade un cuarto test, `test_email_dispatch_is_patched_without_requesting_the_fixture()`, sin parámetros;
    - en l.50, `mock_send_email: MagicMock` pasa a `mock_send_email: Any`;
    - fuera `from unittest.mock import MagicMock` y dentro `from typing import Any` y
      `from app.core.email import send_verification_email as real_send_verification_email`.
  - `conftest.py` (enmienda E2): la docstring de `mock_send_email` (l.117-123) recibe una sección
    `Yields:` con la línea `The autospecced stand-in for send_verification_email.`. Nada más cambia en el fixture.
- **Tests (RED primero):** se escriben con el `conftest.py` actual y se comprueba que los dos primeros fallan.
  1. `test_each_request_gets_its_own_session`: dos generadores, `anext` en cada uno; se comprueba
     `first_session is not db_session` y `second_session is not first_session`. RED, porque hoy los dos son
     `db_session`.
  2. `test_app_flush_without_commit_is_invisible_to_the_test(make_user)`: la sesión de la app hace `add(make_user())`
     y `flush()`, luego `aclose()`; `select(func.count()).select_from(User)` en `db_session` → 0. RED, porque hoy
     da 1.
  3. `test_app_commit_is_visible_to_the_test(make_user)`: lo mismo con `commit()`; `select(User).where(User.cedula
     == user.cedula)` en `db_session` → una fila con `email == user.email`. Pasa antes y después.
  4. `test_email_dispatch_is_patched_without_requesting_the_fixture()` (enmienda E2), síncrono y sin parámetros.
     Docstring: "The autouse email double is active in a test that does not request it." Comprueba `assert
     user_router.send_verification_email is not real_send_verification_email`. **Empieza en verde**, porque el
     `autouse` ya existe (fase C), así que no tiene RED. Su prueba es una **mutación de auditoría que no edita el
     repo**:
     - se guarda `H=$(git hash-object tests/conftest.py)` después de las ediciones de la fase;
     - se copia ese `conftest.py` al scratchpad como `be15_no_autouse.py`, cambiando solo
       `@pytest.fixture(autouse=True)\ndef mock_send_email():` por `@pytest.fixture\ndef mock_send_email():`;
     - se ejecuta `PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --noconftest
       -p be15_no_autouse tests/test_fixtures_contract.py` → **`1 failed, 8 passed`**. Falla solo el test 4; los 4
       de A, el de C y los 3 de sesión pasan;
     - sin el plugin, el mismo archivo da `9 passed`.

     Si algún método llegara a editar `tests/conftest.py` en el sitio, antes se guarda una copia y después se
     restaura byte a byte.
- **Criterio de aceptación:** fila "Fase F" (396 passed; ruff 54; 0 en los archivos tocados). `grep -c "yield
  db_session" tests/conftest.py` → 0; `grep -cE "async with TestingSessionLocal\(\) as session" tests/conftest.py` →
  2. Cobertura ≥ 94.81 %. Mutación de auditoría del test 4: exactamente `1 failed, 8 passed`. **Salvaguarda
  antes del commit**, con su salida literal en el handoff: `test "$(git hash-object tests/conftest.py)" = "$H" &&
  echo IGUAL` → `IGUAL` (el mutante no tocó el archivo de la fase), y `grep -B1 -E "^def mock_send_email\("
  tests/conftest.py | grep -c "@pytest.fixture(autouse=True)"` → 1. Tras el commit: `test "$(git hash-object
  tests/conftest.py)" = "$(git rev-parse HEAD:tests/conftest.py)" && echo IGUAL` → `IGUAL`. Si no da `IGUAL`, no
  se hace el commit.
- **Fuera de alcance:** cambiar `StaticPool`, el motor o `expire_on_commit`; PostgreSQL de pruebas; `sqlite_where`
  (BE-31); `app/db/database.py`; **`AGENTS.md`** (llevar las dos reglas a AGENTS §5 es tarea de David, por PR al
  cierre).
- **Commits** (dos; `progress.json` guarda `"<test> <docs>"`):
  ```
  test(conftest): give each request its own session, apart from the test's

  The client fixture overrode get_db with the test's own db_session, so
  the app and the test shared one session for the whole test, unlike
  get_db, which opens one per request. A write the app flushed but never
  committed was still visible to the test. Today the repositories commit
  themselves, so nothing slipped through, but A3 moves commits out of
  the repositories and the suite must catch a forgotten one (BE-15
  point 4).

  - tests/conftest.py: the override opens a TestingSessionLocal session
    per request; client no longer depends on db_session. Its docstring
    states the two rules: commit arrange data before calling the client,
    refresh held objects afterwards.
  - tests/test_fixtures_contract.py: freezes one session per request, an
    uncommitted app flush invisible to the test, a commit visible. One
    more test does not request mock_send_email and asserts that the
    router's send_verification_email is not the real app.core.email
    function, so dropping autouse=True (D2) now fails the suite; the
    fixture parameter is annotated Any, since patch(autospec=True) on a
    function returns a function, and the unused MagicMock import goes.
  - tests/conftest.py: the mock_send_email docstring gets its Yields
    section (AGENTS 4).
  ```
  ```
  docs(adr): add ADR-0011, the app and the test use separate sessions

  Records the BE-15 phase F decision: one app session per request, apart
  from the test's. Accepted limit: StaticPool shares one connection, so
  isolation is per session, not per transaction, and a forgotten commit
  shows up when the app session closes. It states the two rules every
  test follows (commit before the request, refresh after); David moves
  them into AGENTS 5 in a PR at closing. Alternatives: shared session,
  separate connections, a PostgreSQL test database (decided in BE-31).
  ```

### Fase F-mínima — El test que vigila el `autouse` del correo (solo si F se recorta; enmienda E2)
- **Cuándo:** solo si F se recorta. Se ejecuta antes del PR del bloque. F y F-mínima son excluyentes: si F se
  ejecuta, F-mínima no se ejecuta, porque su contenido va dentro de F.
- **Archivos:** `tests/test_fixtures_contract.py` y `tests/conftest.py` (solo la docstring de `mock_send_email`). Sin
  el cambio de sesión y sin ADR-0011.
- **Cambios exactos:** los dos puntos "(enmienda E2)" de "Cambios exactos" de la fase F, idénticos:
  - test `test_email_dispatch_is_patched_without_requesting_the_fixture()` sin parámetros;
  - anotación `Any` en l.50;
  - fuera el import de `MagicMock`; dentro `Any` y `real_send_verification_email`;
  - sección `Yields:` en la docstring del fixture.
- **Tests (RED primero):** el test nuevo empieza en verde y no tiene RED. Su prueba es la mutación de auditoría
  descrita en el test 4 de la fase F, igual en todo salvo la cifra: con `be15_no_autouse`,
  `tests/test_fixtures_contract.py` da **`1 failed, 5 passed`** (falla solo el test nuevo; pasan los 4 de A y el de
  C). Sin el plugin: `6 passed`.
- **Criterio de aceptación** (trinquete ADR-0005):
  - fila "Fase F-mínima": 393 passed (381 + D 0 + E 11 + D-bis 0 + 1); ruff total 54; 1 en `tests/` (el I001 heredado de
    `test_user_service.py:3`); 0 en los dos archivos tocados; mypy 10; cobertura ≥ 94.81 %; import-linter 4 KEPT;
    docs OK; `ruff format` OK;
  - `grep -cE "^(async )?def test_" tests/test_fixtures_contract.py` → 6;
  - `grep -c "MagicMock" tests/test_fixtures_contract.py` → 0;
  - `git diff -- tests/conftest.py`, antes del commit: solo líneas añadidas (`+`), todas dentro de la docstring de
    `mock_send_email`;
  - mutación: `1 failed, 5 passed`;
  - salvaguarda antes del commit: `test "$(git hash-object tests/conftest.py)" = "$H" && echo IGUAL` → `IGUAL`, y
    el grep de `autouse=True` → 1.
- **Fuera de alcance:** todo lo demás de F (sesión por petición, sus 3 tests, ADR-0011), que queda deslizado según
  la decisión 6.
- **Commit:**
  ```
  test(conftest): freeze that the email double is active without asking

  D2 made mock_send_email autouse so that a test which forgets the fixture
  cannot send a real verification email. The phase C contract test
  requests the fixture by name, so it kept passing with autouse=True
  removed (audit of phase C: 381 passed): nothing guarded D2.

  - tests/test_fixtures_contract.py: a new test that does not request the
    fixture asserts that app.api.routers.user.send_verification_email is
    not the real app.core.email function. The mock_send_email parameter
    is annotated Any, since patch(autospec=True) on a function returns a
    function, and the unused MagicMock import goes.
  - tests/conftest.py: the mock_send_email docstring gets its Yields
    section (AGENTS 4).

  A conftest mutant without autouse=True turns exactly the new test red.
  ```

## Verificación final

Se ejecuta desde la raíz del repo, con la rama tras la fase F. Si F se recorta, se ejecuta F-mínima y valen las
cifras de su fila (393 passed): los puntos 10 y 11 no se aplican, el 9 da 6 y el mutante del 4b da `1 failed, 5
passed`. Cada cifra cuenta también el texto que dicta este plan (nombres de test, docstrings, literales y el ADR).
Ninguno de esos textos contiene `MagicMock(`, `User(`, `f"Bearer {`, `noexiste@example.com` ni una frase en español
entre comillas en `tests/`.

```bash
# 1. Mocks sin spec → 0
grep -rnE "\b(MagicMock|AsyncMock|Mock|NonCallableMock)\(" tests/ --include=*.py | wc -l
# 2. patch sin autospec (excluye client.patch) → 0; y el único patch del correo, en conftest → 1 línea (tests/conftest.py)
grep -rnE "(^|[^.])\bpatch(\.object)?\(" tests/ --include=*.py | grep -v "autospec=True" | wc -l
grep -rnE "(^|[^.])\bpatch\(\"app\.api\.routers\.user\.send_verification_email\", autospec=True\)" tests/ --include=*.py
# 3. Preparación a mano fuera de conftest → 0, 0, 0, 0
grep -rnE "\bUser\(" tests/ --include=*.py | grep -v "tests/conftest.py" | wc -l
grep -rnE "create_access_token\(" tests/ --include=*.py | grep -v "tests/conftest.py" | wc -l
grep -rnE "f\"Bearer \{" tests/ --include=*.py | grep -v "tests/conftest.py" | wc -l
grep -rnE "get_password_hash\(\"pass\"\)" tests/ --include=*.py | wc -l
# 4. D2: fixtures duplicados → 1 línea (tests/conftest.py: mock_send_email); está declarado autouse → 1
grep -rnE "def (mock_send_email|admin_token|auth_headers|superadmin_token)\(" tests/ --include=*.py
grep -B1 -E "^def mock_send_email\(" tests/conftest.py | grep -c "@pytest.fixture(autouse=True)"
# 4b. E2: test sin parámetros que vigila el autouse → 1; MagicMock fuera del archivo → 0; anotación Any → 1; Yields en la docstring → 1
grep -c "def test_email_dispatch_is_patched_without_requesting_the_fixture()" tests/test_fixtures_contract.py
grep -c "MagicMock" tests/test_fixtures_contract.py
grep -c "mock_send_email: Any" tests/test_fixtures_contract.py
grep -A12 -E "^def mock_send_email\(" tests/conftest.py | grep -c "Yields:"
#     mutante sin autouse=True (plugin be15_no_autouse en el scratchpad, ver fase F, test 4) → "1 failed, 8 passed" (F-mínima: "1 failed, 5 passed")
PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --noconftest -p be15_no_autouse tests/test_fixtures_contract.py
#     conftest.py commiteado tal cual, sin restos del mutante → IGUAL
test "$(git hash-object tests/conftest.py)" = "$(git rev-parse HEAD:tests/conftest.py)" && echo IGUAL
# 5. Aserciones sobre texto → 0; frase entre comillas → 2 líneas, ambas en tests/test_services.py con "Tour corto" (dato)
grep -rnE "\[\"(detail|message)\"\]( ==|\.lower\(\))|in response\.json\(\)\[\"detail\"\]" tests/ --include=*.py | wc -l
grep -rnE "== f?\"[A-ZÁÉÍÓÚ][a-záéíóúñ]+ [a-záéíóúñ]+" tests/ --include=*.py
# 6. Nombres en español y sqlalchemy.future en test_auth.py → 0, 0
grep -nE "def test_\w*(registro|verificacion|usuario|actualizacion|listar|recuperar|crear|borrado|exitos|jerarquia)" tests/test_auth.py | wc -l
grep -c "sqlalchemy.future" tests/test_auth.py
# 6b. D3: el caso de credenciales inválidas es contraseña incorrecta → 1; el correo inexistente salió de test_auth.py → 0; test_auth.py sigue con 19 tests
grep -c "def test_login_wrong_password_returns_401_with_bearer_challenge(" tests/test_auth.py
grep -c "noexiste@example.com" tests/test_auth.py
./venv/Scripts/python.exe -m pytest --collect-only -q -p no:cacheprovider tests/test_auth.py | tail -1   # "19 tests collected"
# 6c. E3 (D-bis): "detail" in response.json() en test_auth.py → 0; set(body) == {"detail"} → 9; forma de la recuperación → 1; relectura de la fila del admin creado → 1
grep -c 'assert "detail" in response.json()' tests/test_auth.py
grep -c 'set(body) == {"detail"}' tests/test_auth.py
grep -c '{"success", "message"} <= set(body)' tests/test_auth.py
grep -c 'select(User).where(User.cedula == "555555")' tests/test_auth.py
#     mutantes de D-bis (plugin dbis_mutants en el scratchpad, ver fase D-bis) → columna "Después de editar" de su tabla
for m in extra_key_403 detail_not_str_403 recover_no_message recover_message_not_str row_role row_is_active row_deleted_at; do DBIS_MUTANT=$m PYTHONPATH=<scratchpad> ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -p dbis_mutants tests/test_auth.py -k "tourist_self_role_escalation or tourist_self_is_active_change or admin_recovers_tourist or superadmin_provisions_admin" | tail -1; done
# 7. Aserciones de mock sin argumentos → 10 (residual: services 245/520, storage 92/159/189/198, user_service 110/111/328/329)
grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ --include=*.py | wc -l
# 8. Regresiones B2/B3 → 10 definiciones
grep -cE "^async def test_b[23]_" tests/test_user_access_policy.py
# 9. Tests de contrato de los fixtures → 9 (A 4 + C 1 + F 3 + E2 1; con F-mínima: 6)
grep -cE "^(async )?def test_" tests/test_fixtures_contract.py
# 10. Sesión por petición → 0 y 2
grep -c "yield db_session" tests/conftest.py
grep -cE "async with TestingSessionLocal\(\) as session" tests/conftest.py
# 11. D1: ADR-0011 en docs/adr → 1; sin el bloque de borrador → 0 y 0; estado aceptado → 1
ls docs/adr/ | grep -c "^0011-sesion-de-la-app-distinta-de-la-del-test\.md$"
grep -c "^>" docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md
grep -c "borrador" docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md
grep -c "^- \*\*Estado:\*\* aceptado$" docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md
# 12. Ruff: en tests/ solo queda el I001 de test_user_service.py → "Found 1 error."; total → "Found 54 errors."
./venv/Scripts/python.exe -m ruff check tests/ 2>&1 | grep -E "^Found"
./venv/Scripts/python.exe -m ruff check . 2>&1 | grep -E "^Found"
# 13. Fuera de alcance intacto: app/, configuración, CI, reglas de agentes → salida vacía
git diff --stat 7877829..HEAD -- app/ pyproject.toml scripts/ .azure-pipelines/ .claude/ AGENTS.md CLAUDE.md
git status --short -- app/ AGENTS.md CLAUDE.md
# 14. Salvaguarda E (obligatoria antes del commit de E y otra vez aquí) → IGUAL
test "$(git hash-object app/services/user_access_policy.py)" = "$(git rev-parse HEAD:app/services/user_access_policy.py)" && echo IGUAL
# 15. Compuerta: ruff ✘ (54, en app/ y test_user_service) y mypy ✘ (10), heredados; el resto ✔;
#     pytest "396 passed" (393 con F-mínima); cobertura ≥ 94.81 %; "Contracts: 4 kept, 0 broken."
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

| Hallazgo | Evidencia | Destino sugerido |
|---|---|---|
| Aserciones de mock sin argumentos (10) | `tests/test_services.py:245,520` (sí inspeccionan `call_args` después), `tests/test_storage.py:92,159,189,198`, `tests/test_user_service.py:110,111,328,329` | `gaps.md` de BE-15 con el conteo (adenda, punto 3). Fila sugerida para el backlog: "Suite: `assert_*_once()` sin argumentos donde AGENTS §5 pide `_with`" · Baja · `B-TESTS m3` si sobra tiempo |
| I001 de `tests/test_user_service.py:3` | Línea base de ruff | Con el próximo cambio que toque ese archivo (el hook lo corrige solo) |
| `from sqlalchemy.future` en tests | `tests/test_services.py:14`, `tests/test_user_access_policy.py:13` | S2 (`B-FUTURO`), junto con `app/` |
| Tests HTTP duplicados | `test_auth.py` (admin → superadmin con PATCH; admin crea admin) frente a `test_user_access_policy.py:274-291` y `:344-369` | Backlog, Baja: consolidar cuando se pueda bajar el conteo con justificación |
| Comentario en español | `tests/test_audit.py:37` | Trivial; con el próximo PR que toque el archivo (AGENTS §4) |
| Las reglas "commit antes de la petición" y "refresh después" de ADR-0011 no están en AGENTS §5 | Enmienda D1 de David (4 nov 2026). Este plan no edita `AGENTS.md` | **David**, PR al cierre de BE-15. No lo hace ninguna fase |
| La respuesta de recuperación de usuario usa claves en español (`cc`, `correo`, `nombre`, `apellido`) | `app/services/user_service.py:359-366` | Junto a P2 (`B-FUTURO`): es contrato con el cliente Flutter |

## Referencias

En esta sesión no había herramienta Context7. Cada API se comprobó con un sondeo local sobre las versiones instaladas
en `venv/` (scripts en el scratchpad de la sesión, fuera del repo) y se enlaza su documentación oficial:

- `unittest.mock` (`create_autospec`, `patch(autospec=True)` con funciones `async`) · Python 3.14.3 ·
  https://docs.python.org/3.14/library/unittest.mock.html#autospeccing
- SQLAlchemy `StaticPool`, reset on return · 2.0.48 · https://docs.sqlalchemy.org/en/20/core/pooling.html#reset-on-return
- SQLAlchemy `AsyncSession.refresh`, mapa de identidad, `populate_existing` · 2.0.48 ·
  https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#refreshing-expiring
- FastAPI `dependency_overrides` · 0.135.1 · https://fastapi.tiangolo.com/advanced/testing-dependencies/
- httpx `ASGITransport` · 0.28.1 · https://www.python-httpx.org/advanced/transports/#asgi-transport
- pytest-asyncio `asyncio_mode = "auto"`, ámbito de bucle por función · 1.3.0 ·
  https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html
- ADR-0005 (trinquete), ADR-0003 (forma `{"detail": str}`), ADR-0011 (aprobado el 4 nov 2026; borrador en
  `docs/deuda/BE-15/adr-0011-borrador.md`, que la fase F copia a `docs/adr/`)

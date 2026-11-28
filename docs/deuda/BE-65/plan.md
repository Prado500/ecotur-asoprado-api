# PLAN — BE-65: Declarar el schema de salida de siete rutas y que el router arme su respuesta

> Fuente: `docs/deuda/BE-65/verificacion.md` (confirmada; adenda de David del 27 nov, decisiones 1–10, que este plan
> toma como dadas, y dos precisiones de David al pedir el plan: los textos pasan al router letra por letra y el cuerpo
> de las siete rutas no cambia, byte a byte). Base: HEAD `9e1cfe7` de `item/be-65`; encima de `0911898` solo hay
> commits de docs, y la línea base se volvió a medir (abajo). **Estado: pendiente de aprobación.** ADR propuesto:
> ADR-0024 (Anexo A), que escribe la fase A; este plan no lo crea en `docs/adr/`.

## Qué se midió y qué no

Todo en copias `git archive HEAD` (`9e1cfe7`) en el scratchpad de la sesión, una carpeta por corrida y una por
mutante, nunca sobre el árbol de trabajo. Intérprete: `C:/projects/ecotur-asoprado/venv/Scripts/python.exe` por ruta
(CPython 3.14.3, Windows), con cwd = la copia; comprobado `import app; app.__file__` →
`…\scratchpad\base\app\__init__.py`, y `scripts/check.py` imprime `Raíz del repo: …\scratchpad\<copia>`. El código y
los tests de los Anexos B y C se aplicaron con scripts de reemplazo exacto (cada ancla una vez); los Anexos son el
`diff -u` entre copias consecutivas y ya salen formateados (`ruff format --check` en verde sin tocar nada).

| Corrida | Comando | Resultado literal |
|---|---|---|
| Línea base (copia limpia) | `scripts/check.py` | exit 0 · `75 files already formatted` · `All checks passed!` · `Success: no issues found in 70 source files` · `Contracts: 4 kept, 0 broken.` · `845 passed, 29 warnings` · `TOTAL 1098 10 160 6 98.73%` · `Compuerta superada.` |
| Cuerpos antes (golden master) | un test de scratch, fuera de la suite y del plan | 10 respuestas guardadas byte a byte (estado, `content-type`, `content-length`, cuerpo): `verificar-email` primer y segundo clic, `DELETE /usuarios/{cedula}`, `PATCH /usuarios/{cedula}/recuperar`, `activar` y `desactivar` con y sin cambio, `DELETE /servicios/{id}`, `PATCH /servicios/{id}/recuperar` |
| B RED (solo tests de B) | `pytest -q` | `11 failed, 845 passed`: 6 con `AttributeError: module 'app.api.routers.service' has no attribute 'PACKAGE_…_MESSAGE'`, 4 con `assert {} == {'$ref': '#/c...sageResponse'}` (el OpenAPI publica un schema vacío) y 1 con `KeyError: 'ServiceMessageResponse'` |
| B GREEN | `scripts/check.py` | exit 0 · `75 files` · `All checks passed!` · mypy `70 source files` · `Analyzed 57 files, 152 dependencies.` · `4 kept` · `856 passed, 29 warnings` · `TOTAL 1105 10 160 6 98.74%` · `Compuerta superada.` |
| C RED (tests de C sobre B) | `pytest -q` | `14 failed, 852 passed`: 4 con `AttributeError: module 'app.api.routers.user' has no attribute …` (`EMAIL_VERIFIED_MESSAGE` ×2, `ACCOUNT_DELETED_MESSAGE`, `ACCOUNT_RECOVERED_MESSAGE`), 3 con `assert {} == {'$ref': …}`, 1 con `KeyError: 'UserRecoveryResponse'` y 6 unitarios con `AssertionError: assert {'message': …, 'success': True} is True` / `is False` / `is <app.models.user.User …>` (el servicio aún devuelve el `dict`) |
| **C GREEN = estado final** | `scripts/check.py` | exit 0 · `75 files already formatted` · `All checks passed!` · `Success: no issues found in 70 source files` · `Analyzed 57 files, 152 dependencies.` · `Contracts: 4 kept, 0 broken.` · `866 passed, 29 warnings` · `TOTAL 1114 10 160 6 98.74%` · `Compuerta superada.` |
| Cuerpos después | el mismo test de scratch sobre la copia final; `cmp` | **idénticos byte a byte, 10 de 10** (`cmp` sin salida) |
| OpenAPI antes y después | `diff` de `/openapi.json` | cambian solo las siete rutas (su `200` pasa de `"schema": {}` a un `$ref`, y su `description`, que es el docstring) y entran dos componentes, `ServiceMessageResponse` y `UserRecoveryResponse` |
| Mutantes | `pytest -q` completo, cada uno en su copia del estado final | 24 mutantes: **20 muertos**; 4 vivos declarados, 2 de texto (MB8, MC13: los mata el comando 6 de la verificación final, medido) y 2 equivalentes (MB9, MC14: el cuerpo que sale no cambia) (tabla en el Análisis) |
| Alternativa de alias (D1) | copia final + `serialization_alias` en `UserRecoveryResponse` | cuerpos idénticos byte a byte (10 de 10); `12 passed` (tests `be65` de `test_auth.py` y el golden master); `mypy` de los dos archivos: `Success`. Con las claves del alias en el `dict` del router: `ResponseValidationError: 4 validation errors` |
| Anexos aplicables | copias limpias nuevas; `git apply` del Anexo B y luego del C, enteros y partidos (`--include='tests/*'` y luego `--exclude='tests/*'`) | partidos reproducen `11 failed, 845 passed`, `14 failed, 852 passed` y `866 passed`; enteros, `--check` limpio en los dos y el resultado es la copia final en los 9 archivos (`diff --strip-trailing-cr`). Fuera de un repo, `git apply` escribió CRLF; en el repo, `.gitattributes` fija `eol=lf` |
| Verificación final | comandos 1–6 y 9 sobre la copia final | los valores que se dan abajo; 7, 8 y 10 usan `git` y se midieron con `diff -rq` y `diff -u` entre la copia base y la final (9 archivos cambiados) |

**No medido, y por qué:** (1) la fase A: el ADR no se escribió en las copias; `docs/adr` queda fuera de `check_docs`
(`scripts/check_docs.py:157`), así que no mueve la compuerta. (2) Los comandos con `git` de la verificación final (las
copias no tienen `.git`); el alcance se midió con `diff -rq`. (3) La skill `test-sanitizer`. (4) El cliente Flutter: las
siete acciones las prueba David contra el backend de la rama (adenda, avisos). (5) PostgreSQL: no hace falta, no se
tocan `app/models/` ni `alembic/` (adenda, avisos). (6) El cuerpo byte a byte con solo la fase B aplicada (se midió el
estado final; B pasó su compuerta). (7) La alternativa de alias, sin compuerta completa ni mutantes. (8) El bloqueo de
`_rustgrimp` `(backlog AF-17)`: no se dio, import-linter evaluó `4 kept` en todas las corridas.

## Resumen para aprobación

Tres fases. (A) ADR-0024 por escrito antes del código: un servicio devuelve un dato del dominio o nada, y el router
arma la respuesta y declara su schema. (B) Las cuatro rutas de paquetes: `toggle_package_status`, `soft_delete_package`
y `recover_package` pasan a devolver `None`; el router arma el cuerpo con cuatro textos constantes y declara
`MessageResponse` (activar, desactivar) o el nuevo `ServiceMessageResponse` (`success`, `message`, `UID`). (C) Las tres
rutas de usuario: `verify_email_account` devuelve `bool` (`True` si este enlace verificó el correo),
`delete_user_account` y `recover_user_account` devuelven el `User`; el router arma los cuerpos con cuatro textos
constantes y declara `MessageResponse` o el nuevo `UserRecoveryResponse` (`success`, `cc`, `correo`, `nombre`,
`apellido`, `message`). Medido: el cuerpo de las siete rutas sale igual byte a byte (10 respuestas), el OpenAPI cambia
solo en ellas, y la compuerta pasa en cada fase (845 → 856 → 866 tests; 98,73 % → 98,74 %). Riesgo principal: la suite
no detecta una letra cambiada en un texto (AGENTS §5 prohíbe afirmar sobre texto en español); lo detecta el comando 6
de la verificación final. No se toca: `GET /`, `image_uploader`, el texto del borrado (BE-66), los nombres de las
claves (P2), `tests/test_route_guards.py`, la auditoría, A3 ni el cliente.

## Objetivo y decisiones bloqueadas

Las siete rutas declaran `response_model` con un schema por forma y ningún servicio arma un `dict` de respuesta, un
`success` ni un texto de éxito. El cliente recibe exactamente los mismos bytes que hoy.

1. **Mismo cuerpo** (adenda 1 y precisión de David): mismas claves, mismos valores, mismo orden y los textos letra por
   letra. Lo prueban los tests de cuerpo exacto (`list(body.items()) == [...]`) y, para la letra, el comando 6.
2. **El servicio devuelve un dato o nada** (adenda 2): `verify_email_account → bool`, `delete_user_account → User`,
   `recover_user_account → User`, `toggle_package_status`, `soft_delete_package` y `recover_package → None`.
3. **El router arma y declara** (adenda 3): textos como constantes de módulo del router, junto a
   `RESEND_VERIFICATION_MESSAGE`; el del borrado es una plantilla `str.format` con `{email}` y `{cedula}`. El handler
   devuelve un `dict` y anota `-> dict[str, …]`, como la ruta de BE-64; `response_model` manda.
4. **Schemas:** `MessageResponse` para la forma 1, sin tocar `app/schemas/message.py`; `ServiceMessageResponse` en
   `app/schemas/service.py`, hereda de `MessageResponse` (DTO de salida) y añade `UID: int`, así que el orden es
   `success`, `message`, `UID`; `UserRecoveryResponse` en `app/schemas/user.py`, sobre `BaseModel`, con el orden
   `success`, `cc`, `correo`, `nombre`, `apellido`, `message`. Sin validadores ni herencia de un DTO de entrada (A9).
5. **`verify_email_account` dice el caso, no el texto** (adenda 4): `True` cuando este enlace verificó, `False` cuando
   ya estaba verificado. La regla del enlace (ADR-0022) y la auditoría (ADR-0021) no cambian.
6. **Tests primero** (adenda 5); los tests HTTP que ya existen no se editan y siguen en verde.
7. **ADR-0024 en la fase A** (adenda 6); la viñeta de AGENTS §3 va en el Anexo D y la commitea David tras la última
   auditoría.
8. **Los campos se llaman como las claves** (`UID`, `cc`, `correo`, `nombre`, `apellido`), sin alias: decisión del
   redactor, pendiente de que David la confirme (D1 del informe; alternativa medida arriba).

## Análisis del redactor

**Qué cambia y por qué.** Las seis funciones dejan de escribir la respuesta HTTP: quitan su `return {…}` y devuelven lo
que el router necesita para armarla, y nada más. Paquetes: el router ya conoce `service_id` (ruta) y si activa o
desactiva (cada ruta es una), así que el servicio devuelve `None`; el `f"…{estado}…"` se parte en dos constantes, una
por ruta, con el mismo texto resultante (medido). Usuarios: el mensaje del borrado necesita el correo de la cuenta
borrada, que el router no tiene, y la recuperación necesita cédula, correo y nombres, así que ambas devuelven el `User`;
la verificación necesita saber cuál de dos casos ocurrió, así que devuelve `bool`. La cédula del mensaje del borrado
sale del parámetro de la ruta, el mismo valor que hoy usa el servicio (`target_cedula`). La sesión no expira atributos
al confirmar (`expire_on_commit=False`, `app/db/database.py:17`), y el servicio ya leía esos atributos después del
mismo `commit`, así que leerlos en el router no cambia nada.

**Orden de fases y dependencias.** A → B → C. B y C no comparten archivos; solo citan ADR-0024 en comentarios y
docstrings, por eso van después de A. B va antes porque es más pequeña y no reescribe tests. Las cifras de C se
midieron sobre B.

**Qué tests congelan qué (no se editan y siguen en verde).** `tests/test_auth.py:92-111` (primer clic) y `:209-232`
(segundo clic, mensaje distinto); `:366-385` (borrado propio, claves `success` y `message`); `:532-552`
(recuperación, subconjunto); `tests/test_services.py:77-127` (activar, desactivar, borrar y recuperar) y `:1079-1121`
(BE-38, con y sin cambio); `tests/test_route_guards.py` (las siete rutas en el inventario);
`tests/test_user_access_policy.py:1378-1395` (autospec de `UserService` con `side_effect`); los caminos de fallo
unitarios de borrado y recuperación (`tests/test_user_service.py:161-210`) y de la verificación (`:361-420`,
`tests/test_token_failure_paths.py:308-327`); `tests/test_verification_resend.py:249-261`, que ya fija el componente
`MessageResponse` que B y C reutilizan. **Se reescriben** (adenda 5) los cuatro unitarios de la verificación que
afirman sobre el `dict`: `tests/test_user_service.py:278-358`, incluido `:342-358`, que la adenda no contaba
(`first["success"]`, `set(first)`, `second["message"] != first["message"]`).

**Mutantes (todos medidos; cada uno en su copia del estado final, suite completa).**

| # | Mutante (archivo de producción) | Resultado · lo matan |
|---|---|---|
| MB1 | `activar` responde `PACKAGE_DEACTIVATED_MESSAGE` | muerto (2): `test_be65_status_route_answers_only_success_and_its_message[activate-inactive]`, `[activate-active]` |
| MB2 | `recuperar` responde `PACKAGE_DELETED_MESSAGE` | muerto (1): `test_be65_recover_answers_its_message_and_the_package_id` |
| MB3 | `DELETE /servicios/{id}` sin `response_model` | muerto (1): `test_be65_package_route_declares_its_response_schema[delete]` |
| MB4 | `desactivar` sin `response_model` | muerto (1): `…_declares_its_response_schema[deactivate]` |
| MB5 | `UID: int \| None = None` | muerto (1): `test_be65_service_message_response_documents_three_required_keys_in_order` |
| MB6 | `ServiceMessageResponse(BaseModel)` con el orden `UID`, `success`, `message` | muerto (3): `…_soft_delete_answers_…`, `…_recover_answers_…`, `…_documents_three_required_keys_in_order` |
| MB7 | `ServiceMessageResponse` gana `detail: str \| None = None` | muerto (3): los mismos tres de MB6 |
| MB8 | `"…(Eliminado logicamente)."` (sin tilde) | **vivo** en la suite (AGENTS §5); el comando 6 da `0 0 0 0` para ese texto |
| MB9 | `"UID": str(service_id)` | **vivo, equivalente**: Pydantic lo convierte a entero y el cuerpo no cambia |
| MC1 | el router invierte el `bool` de la verificación | muerto (2): `test_be65_verify_link_answers_one_message_per_case[registered-tourist]`, `[activated-by-an-admin]` |
| MC2 | el servicio devuelve `True` con la marca llena | muerto (6): `test_link_used_again_after_admin_deactivation_keeps_the_account_inactive`, `test_second_click_on_the_link_changes_nothing_and_answers_another_message`, los 2 de MC1, `test_verify_email_with_the_mark_filled_changes_nothing`, `test_verify_email_second_use_reports_the_email_as_already_verified` |
| MC3 | el mensaje del borrado usa `usuario_actual.email` | muerto (1): `test_be65_delete_answers_with_the_deleted_account_in_the_message` |
| MC4 | `format(email=cedula, cedula=deleted.email)` | muerto (1): el mismo de MC3 |
| MC5 | `nombre` ↔ `apellido` en el `dict` del router | muerto (1): `test_be65_recover_answers_the_account_keys_in_their_order` |
| MC6 | `UserRecoveryResponse` con `message` en segundo lugar | muerto (2): `…_recover_answers_the_account_keys_in_their_order`, `test_be65_user_recovery_response_documents_six_required_keys_in_order` |
| MC7 | `PATCH /usuarios/{cedula}/recuperar` sin `response_model` | muerto (2): `test_be65_user_route_declares_its_response_schema[recover]`, `…_documents_six_required_keys_in_order` (el componente desaparece) |
| MC8 | `verificar-email` sin `response_model` | muerto (1): `…_declares_its_response_schema[verify]` |
| MC9 | `DELETE /usuarios/{cedula}` sin `response_model` | muerto (1): `…_declares_its_response_schema[delete]` |
| MC10 | `cc: int` | muerto (2): `…_recover_answers_…`, `…_documents_six_required_keys_in_order` |
| MC11 | `delete_user_account` devuelve `current_user` | muerto (2): `…_delete_answers_with_the_deleted_account_in_the_message`, `test_delete_returns_the_soft_deleted_account` |
| MC12 | `recover_user_account` devuelve `current_user` | muerto (2): `…_recover_answers_the_account_keys_in_their_order`, `test_recover_returns_the_recovered_account` |
| MC13 | `"Su correo ya fue verificado"` (sin punto) | **vivo** en la suite (AGENTS §5); el comando 6 da `0 0 0 0` para ese texto |
| MC14 | el router añade `"telefono": recovered.phone` | **vivo, equivalente**: `response_model` descarta la clave y el cuerpo no cambia |
| MC15 | el router no envía `message` en la recuperación | muerto (5): `test_link_finishes_the_registration_of_a_recovered_account`, `test_link_does_not_activate_a_recovered_account_that_was_verified`, `test_admin_recovers_tourist_as_inactive`, `…_recover_answers_the_account_keys_in_their_order`, `test_be36_recovered_superadmin_reactivated_by_peer_can_log_in` (500 por `ResponseValidationError`) |

Muertos 20 de 24. Vivos: MB8 y MC13 (texto: los mata el comando 6, medido sobre sus copias) y MB9 y MC14
(equivalentes: el cuerpo que sale es el mismo).

**Riesgos.** (1) Texto: MB8 y MC13 sobreviven a la suite por diseño (AGENTS §5); el comando 6 los mata, contando cada
texto literal en `app/`. (2) Filtrado: una clave que el router añada y el schema no tenga se descarta sin aviso (MC14,
equivalente); una que el schema pida y el `dict` no traiga es un 500 (MC15, muerto). (3) Coerción: `"UID":
str(service_id)` sale como entero, porque Pydantic convierte en modo laxo (MB9, equivalente). (4) El orden del cuerpo es
el del schema, no el del `dict`: los tests lo fijan con `list(body.items())`. (5) El OpenAPI publica el docstring del
handler como `description`: las líneas `Returns:` que cambian se ven allí (medido, inocuo). (6) `_rustgrimp`
`(backlog AF-17)`: si Windows lo bloquea, la fase lo declara en su handoff como en E0 de BE-64.

**Qué NO se toca:** `app/schemas/message.py`, `app/main.py` (`GET /`, decisión 7), `image_uploader` (decisión 9), el
texto del borrado (BE-66, decisión 8), las claves y los textos (P2), `tests/test_route_guards.py`, `tests/conftest.py`,
los tests HTTP existentes, `app/models/`, `alembic/`, los repositorios (A3), dónde se escribe la auditoría (ADR-0021),
los textos de error de los servicios, `AGENTS.md`, `docs/backlog.md`, `docs/CONTEXT.md` y el cliente Flutter.

## Regla de alcance

**Sí:** ADR-0024; dos schemas de salida nuevos; el retorno de seis funciones de servicio; `response_model`, retorno
anotado y cuerpo armado en siete handlers, con ocho textos constantes; los tests nuevos y los cuatro unitarios
reescritos. **No:** todo lo de la lista anterior. Un hallazgo nuevo va a Residuales del handoff, nunca al código.

## Fases

### Fase A — ADR-0024: el servicio devuelve datos y el router arma la respuesta (la más pequeña)
- **Archivos (1):** `docs/adr/0024-el-servicio-devuelve-datos-y-el-router-arma-la-respuesta.md` (nuevo).
- **Cambios exactos:** el texto del Anexo A, literal, con `<FECHA DE APROBACIÓN>` sustituido por la fecha de
  aprobación del plan.
- **Tests (RED primero):** no aplica (solo documentación). La compuerta debe dar las cifras de la línea base.
- **Criterio de aceptación:** el archivo existe y es el Anexo A más la fecha; `grep -c "<FECHA DE APROBACIÓN>"` sobre
  él → `0`; compuerta exit 0 con `845 passed` y `98.73%`.
- **Fuera de alcance de esta fase:** código, tests, `AGENTS.md` (la viñeta es del Anexo D y la commitea David).
- **Commit:**
  ```
  docs(adr): add ADR-0024, services return data and routers build the answer

  Six service functions built the HTTP answer themselves: a dict with
  success and the text the user reads, which seven routes returned with
  no response_model, so nothing limited its keys and the OpenAPI showed
  an empty schema (BE-65).

  ADR-0024 records David's decisions before any code: a service returns
  a domain value or nothing, never a response dict, success or a text
  for the user; the router builds the body, declares its output schema
  and keeps each text as a constant, moved letter by letter. It lists
  the six functions and what each returns, and what stays out: error
  texts, image_uploader and GET /.
  ```

### Fase B — Rutas de paquetes: el router arma la respuesta y declara su schema
- **Archivos (4):** `app/schemas/service.py`, `app/services/tourist_services_service.py`, `app/api/routers/service.py`,
  `tests/test_services.py`.
- **Cambios exactos:** Anexo B, literal. `ServiceMessageResponse(MessageResponse)` con `UID: int`; las tres funciones
  `-> None`, sin `estado` ni `return {…}` y sin `Returns:` en el docstring; en el router, el import de
  `MessageResponse` y `ServiceMessageResponse`, las constantes `PACKAGE_ACTIVATED_MESSAGE`,
  `PACKAGE_DEACTIVATED_MESSAGE`, `PACKAGE_DELETED_MESSAGE` y `PACKAGE_RECOVERED_MESSAGE`, y en los cuatro handlers
  `response_model`, `-> dict[str, bool | str]` o `-> dict[str, bool | str | int]`, la llamada al servicio sin `return` y
  el `return` del cuerpo.
- **Tests (RED primero):** el bloque de tests del Anexo B y el import `from app.api.routers import service as
  service_router`, antes de tocar `app/`: `test_be65_status_route_answers_only_success_and_its_message` (4 casos:
  activar y desactivar, con y sin cambio), `test_be65_soft_delete_answers_its_message_and_the_package_id`,
  `test_be65_recover_answers_its_message_and_the_package_id`, `test_be65_package_route_declares_its_response_schema`
  (4 rutas) y `test_be65_service_message_response_documents_three_required_keys_in_order`. RED esperado:
  `11 failed, 845 passed` con los motivos de la tabla de mediciones. Forma medida de aplicarlo: copiar el bloque del
  Anexo B a un archivo fuera del repo, `git apply --include='tests/*' <archivo>` (RED) y luego
  `git apply --exclude='tests/*' <archivo>` (GREEN).
- **Criterio de aceptación:** compuerta exit 0 con `856 passed`, cobertura ≥ 98,74 %, mypy `70 source files`,
  `4 kept`; MB1–MB7 muertos. Medido sobre la copia de B: `grep -hA1 -E "^@[a-z_]*router\.(get|post|put|patch|delete)\("
  app/api/routers/service.py | grep -c response_model` → `10` (de 10 decoradores); `grep -nE "\) -> dict:"
  app/services/tourist_services_service.py` → solo `image_uploader`; `grep -cE '"success": True'
  app/services/tourist_services_service.py` → `0`.
- **Fuera de alcance de esta fase:** las rutas de usuario, `app/schemas/message.py`, `image_uploader`, los tests ya
  existentes de `tests/test_services.py`.
- **Commit:**
  ```
  refactor(services): build the package answers in the router, with schemas

  The four package routes that change a state returned the dict the
  service built, with no response_model: nothing limited its keys and
  the OpenAPI showed an empty schema (BE-65, ADR-0024).

  - app/schemas/service.py: ServiceMessageResponse extends
    MessageResponse with UID, so its keys keep the order success,
    message, UID.
  - app/services/tourist_services_service.py: toggle_package_status,
    soft_delete_package and recover_package return None; the audit rows
    stay where they were.
  - app/api/routers/service.py: the four texts, moved letter by letter,
    are constants; each handler builds its body and declares
    MessageResponse (activar, desactivar) or ServiceMessageResponse
    (delete, recuperar).
  - tests/test_services.py: the exact body of each route, key order
    included, and its schema in /openapi.json.

  The client gets the same bytes: measured on every route before and
  after.
  ```

### Fase C — Rutas de usuario: el router arma la respuesta y declara su schema
- **Archivos (5):** `app/schemas/user.py`, `app/services/user_service.py`, `app/api/routers/user.py`,
  `tests/test_auth.py`, `tests/test_user_service.py`.
- **Cambios exactos:** Anexo C, literal. `UserRecoveryResponse(BaseModel)` con seis campos en el orden del cuerpo;
  `verify_email_account -> bool` (`return False` con la marca llena, `return True` al final), `delete_user_account ->
  User` (`return soft_deleted_user`), `recover_user_account -> User` (`return target_user`), con sus `Returns:`; en el
  router, el import de `UserRecoveryResponse`, las constantes `EMAIL_VERIFIED_MESSAGE`,
  `EMAIL_ALREADY_VERIFIED_MESSAGE`, `ACCOUNT_DELETED_MESSAGE` y `ACCOUNT_RECOVERED_MESSAGE` tras
  `RESEND_VERIFICATION_MESSAGE`, y en los tres handlers `response_model`, `-> dict[str, bool | str]` y el cuerpo armado.
- **Tests (RED primero):** el Anexo C de `tests/test_auth.py` (imports `pytest` y `user_router`;
  `test_be65_verify_link_answers_one_message_per_case` con 2 casos, `test_be65_delete_answers_with_the_deleted_account_in_the_message`,
  `test_be65_recover_answers_the_account_keys_in_their_order`, `test_be65_user_route_declares_its_response_schema` con
  3 rutas y `test_be65_user_recovery_response_documents_six_required_keys_in_order`) y de
  `tests/test_user_service.py` (los cuatro unitarios de la verificación pasan a `result is True` / `is False`, el
  último renombrado `test_verify_email_second_use_reports_the_email_as_already_verified`; nuevos
  `test_delete_returns_the_soft_deleted_account` y `test_recover_returns_the_recovered_account`), antes de tocar `app/`.
  RED esperado: `14 failed, 852 passed` con los motivos de la tabla de mediciones. Se aplica como el Anexo B:
  `--include='tests/*'` y luego `--exclude='tests/*'`.
- **Criterio de aceptación:** compuerta exit 0 con `866 passed`, cobertura ≥ 98,74 %, mypy `70 source files`,
  `4 kept`; MC1–MC12 y MC15 muertos; verificación final 1–10 con los valores de abajo.
- **Fuera de alcance de esta fase:** las rutas de paquetes, `POST /usuarios/reenviar-verificacion` y su texto, el
  texto del borrado (BE-66), la regla del enlace (ADR-0022), los tests HTTP ya existentes de `tests/test_auth.py`.
- **Commit:**
  ```
  refactor(users): build the account answers in the router, with schemas

  Three user routes returned the dict the service built, with no
  response_model: the recovery even sent cc, correo, nombre and
  apellido that no schema listed and no test checked (BE-65,
  ADR-0024).

  - app/schemas/user.py: UserRecoveryResponse, on BaseModel with no
    validators, keeps the six keys and their order.
  - app/services/user_service.py: verify_email_account returns True
    when this link verified the email and False when it already was;
    delete_user_account and recover_user_account return the account.
    The link rule (ADR-0022) and the audit rows do not change.
  - app/api/routers/user.py: the four texts, moved letter by letter,
    are constants (the deletion one a template with the email and the
    cedula); each handler builds its body and declares MessageResponse
    or UserRecoveryResponse.
  - tests/test_auth.py: the exact body of each route, key order
    included, and its schema in /openapi.json.
  - tests/test_user_service.py: the verification tests assert on the
    returned bool; the deletion and the recovery return the account.

  The client gets the same bytes: measured on every route before and
  after.
  ```

## Verificación final

Desde la raíz del repo, en Git Bash, sobre el HEAD de la rama tras la fase C. `--include='*.py'` evita contar los
`.pyc` de `__pycache__`. Los valores salen de la copia final medida, e incluyen el texto que dictan los Anexos.

```bash
# 1. Las 22 rutas de los routers declaran response_model (en la línea del decorador o en la siguiente) → 22 y 22
cat app/api/routers/*.py | grep -cE "^@[a-z_]*router\.(get|post|put|patch|delete)\("
grep -hA1 -E "^@[a-z_]*router\.(get|post|put|patch|delete)\(" app/api/routers/*.py | grep -c "response_model"

# 2. Patrón de la verificación: solo quedan los 4 decoradores multilínea (service.py:58; user.py:105, 128, 198),
#    y los 4 llevan response_model en su línea siguiente (ver 1)
grep -nE "^@[a-z_]*router\.(get|post|put|patch|delete)\(" app/api/routers/*.py | grep -v response_model

# 3. GET / queda fuera (decisión 7) → 1 línea: 205:@app.get("/", tags=["Health Check"])
grep -nE "^@app\.(get|post|put|patch|delete)\(" app/main.py | grep -v response_model

# 4. Ningún servicio arma la respuesta → 1 (image_uploader, decisión 9) y 0
grep -nE "\) -> dict:" app/services/*.py
grep -rnE --include='*.py' '"success": True' app/services | wc -l

# 5. Las claves de las formas 2 y 3 → 6 en app/, las 6 en app/api/routers; 0 en app/services; 16 en tests/
grep -rnE --include='*.py' "\"UID\"|\"cc\"|\"correo\"|\"nombre\"|\"apellido\"" app/ | wc -l
grep -rnE --include='*.py' "\"UID\"|\"cc\"|\"correo\"|\"nombre\"|\"apellido\"" app/api/routers | wc -l
grep -rnE --include='*.py' "\"UID\"|\"cc\"|\"correo\"|\"nombre\"|\"apellido\"" app/services | wc -l
grep -rnE --include='*.py' "\"UID\"|\"cc\"|\"correo\"|\"nombre\"|\"apellido\"" tests/ | wc -l

# 6. Cada texto, letra por letra, una sola vez en app/ y en un router; 0 en app/services y 0 en tests/
for t in "El paquete ha sido activado exitosamente." "El paquete ha sido desactivado exitosamente." \
  "Paquete movido a la papelera (Eliminado lógicamente)." \
  "Paquete recuperado. Se encuentra en la sección 'Por Activar'." \
  "Cuenta verificada exitosamente. Ya puede iniciar sesión." "Su correo ya fue verificado." \
  "La cuenta vinculada a {email}, con C.C. {cedula} ha sido eliminada exitosamente." \
  "Usuario recuperado. Se encuentra inactivo por seguridad."; do
  echo "$(grep -rF --include='*.py' "$t" app | wc -l) $(grep -rF --include='*.py' "$t" app/api/routers | wc -l) $(grep -rF --include='*.py' "$t" app/services | wc -l) $(grep -rF --include='*.py' "$t" tests | wc -l)"
done   # → ocho líneas "1 1 0 0"

# 7. Lo que no se toca → sin salida
git diff 9e1cfe7..HEAD --stat -- app/main.py app/schemas/message.py app/models alembic app/repositories \
  tests/test_route_guards.py tests/conftest.py

# 8. Los tests HTTP existentes no se editan → 0 líneas borradas en cada archivo
git diff 9e1cfe7..HEAD -- tests/test_auth.py | grep -c "^-[^-]"
git diff 9e1cfe7..HEAD -- tests/test_services.py | grep -c "^-[^-]"

# 9. Compuerta completa → exit 0 · 75 files · mypy 70 · 4 kept · 866 passed · TOTAL … 98.74 %
./venv/Scripts/python.exe scripts/check.py

# 10. Alcance → 10 archivos: los 9 de los Anexos B y C y el ADR-0024
git diff 9e1cfe7..HEAD --stat -- app tests docs/adr
```

Medido sobre la copia final: 1 → `22` y `22` (base: `22` y `15`); 2 → 4 líneas; 3 → 1 línea; 4 → 1 línea y `0`
(base: 7 líneas y `7`); 5 → `6`, `6`, `0`, `16` (base: `6`, `0`, `6`, `0`); 6 → ocho veces `1 1 0 0`; 9 → los valores
de la fila C GREEN; 10 → 9 archivos con `diff -rq` (el ADR no se escribió en la copia). 7 y 8 no se midieron con `git`;
`diff -rq` confirma que ningún archivo de 7 cambió, y `diff -u` da 0 líneas borradas en `tests/test_auth.py` y
`tests/test_services.py` (10 en `tests/test_user_service.py`, las de los cuatro unitarios reescritos).

## Residuales

| # | Hallazgo (fuera de alcance) | Evidencia | Destino sugerido |
|---|---|---|---|
| R1 | Los textos que lee el usuario quedan repartidos: los de éxito en los routers, los de error (`detail`) en los servicios. | ADR-0024, decisión 5 y consecuencias; `app/services/*.py` (`raise …Error("…")`) | Ninguna fila nueva: es parte de `(backlog P2)` (campo `code` estable). Decide David. |
| R2 | Una letra cambiada en un texto sobrevive a la suite (MB8, MC13). | AGENTS §5; tabla de mutantes | Nota en `(backlog P2)`, junto a los mutantes D1 y U1 que ya anota: mismo trabajo. |
| R3 | La fila P2 cita `app/services/user_service.py:359-366` y `tests/test_auth.py:330` para las claves en español; tras BE-65 viven en `UserRecoveryResponse` (`app/schemas/user.py`) y `app/api/routers/user.py`, y la igualdad exacta ya existe (`test_be65_recover_answers_the_account_keys_in_their_order`). | `docs/backlog.md`, fila P2 | Actualizar la nota de P2 al cerrar BE-65 (David). |
| R4 | `test_admin_recovers_tourist_as_inactive` mantiene su aserción de subconjunto (`<=`), ahora más débil que el test nuevo; `test_self_soft_delete_keeps_row_and_blocks_login` repite la petición del test nuevo de borrado con otro actor. | `tests/test_auth.py:532-552`, `:366-385` | Ninguna: la adenda 5 deja los tests HTTP sin editar. Si `test-sanitizer` lo marca, va al handoff. |
| R5 | FE-19 no cambia con BE-65: las claves y los textos son los mismos, ahora documentados en el OpenAPI. | Fila FE-19; comparación byte a byte | Ninguno. |

## Referencias

- FastAPI 0.135.1 (`constraints.txt:29`) · `response_model` manda sobre la anotación de retorno y valida, filtra y
  documenta la salida · https://fastapi.tiangolo.com/tutorial/response-model/ (leído en Context7,
  `/websites/fastapi_tiangolo`; sin índice para 0.135.1, se sirvió la documentación vigente).
- Pydantic 2.12.5 (`constraints.txt:56`) · el orden de los campos se conserva al serializar y en el JSON Schema;
  `serialization_alias` para la alternativa D1 ·
  https://github.com/pydantic/pydantic/blob/v2.12.5/docs/concepts/models.md y
  https://github.com/pydantic/pydantic/blob/v2.12.5/docs/concepts/alias.md (leído en Context7, `/pydantic/pydantic`,
  v2.12.5).
- Las fuentes de la adenda (borrador IETF de health check, OWASP API3:2023) sostienen las decisiones 7 y 8, que dejan
  cosas fuera; ADR-0024 no las cita y este plan no las releyó.

## Anexo A — texto de ADR-0024

Literal; la fase A sustituye `<FECHA DE APROBACIÓN>` y nada más.

````markdown
# ADR-0024 — El servicio devuelve datos del dominio y el router arma la respuesta

- **Estado:** aceptado (David, <FECHA DE APROBACIÓN>, al aprobar el plan de BE-65)
- **Propuesta:** Claude, `plan-redactor` (27 nov 2026), sobre la adenda de David a la verificación (27 nov, 17:27 a
  17:48)
- **Ubicación en el repo:** `docs/adr/0024-el-servicio-devuelve-datos-y-el-router-arma-la-respuesta.md`
- **Origen:** backlog BE-65; `docs/deuda/BE-65/verificacion.md` (veredicto, rincones 1 a 5 y adenda);
  `docs/deuda/BE-65/plan.md`. Relación: ADR-0003 (el servicio no conoce el transporte; los errores ya salen como
  excepciones de dominio), ADR-0015 (`app.cli` es un segundo adaptador que no quiere un `dict` pensado para HTTP),
  ADR-0023 (crea `MessageResponse`; su servicio ya devuelve `VerificationResend | None` y el router arma el cuerpo),
  ADR-0022 (la regla del enlace no cambia), ADR-0021 (la auditoría sigue donde está).

## Contexto

Siete rutas no declaraban `response_model` y devolvían el `dict` que armaba el servicio: `{"success": True,
"message": …}`, a veces con claves de más (`UID`; `cc`, `correo`, `nombre`, `apellido`). Sin schema, nada limitaba
qué claves salían y el OpenAPI las publicaba con un schema vacío. Seis funciones de servicio escribían así `success` y
el texto que lee el usuario, que son forma de una respuesta HTTP, aunque ADR-0003 ya saca el transporte de los
servicios para los errores. Un segundo adaptador, como los comandos de `app/cli/` (ADR-0015), recibiría un `dict`
pensado para la API. BE-64 ya había hecho lo contrario en su ruta: el servicio devuelve un dato y el router arma el
cuerpo con un texto constante.

## Decisión

1. **Un servicio devuelve un dato del dominio o nada:** una entidad (`User`), un `NamedTuple` (`RegistrationResult`,
   `VerificationResend`), un `bool` cuando el resultado es uno de dos casos, o `None`. Nunca un `dict` de respuesta,
   ni `success`, ni un texto para el usuario final. Un fallo sigue siendo una excepción de dominio (ADR-0003), así que
   ningún router escribe `success: False`.
2. **El router arma el cuerpo y declara su `response_model`:** un schema de salida en `app/schemas/`, sobre
   `BaseModel` o sobre otro DTO de salida, sin validadores y sin heredar de un DTO de entrada (backlog A9). El handler
   anota el retorno con el tipo que devuelve (`dict[str, …]`, como la ruta de ADR-0023); `response_model` manda en la
   validación, el filtrado y la documentación.
3. **Los textos de éxito son constantes del módulo del router**, como `RESEND_VERIFICATION_MESSAGE`; el que lleva
   datos es una plantilla con `str.format`. Se mueven sin cambiar una letra, y `success` sigue siendo `True`
   constante, porque es contrato con el cliente.
4. **Aplicación inmediata (BE-65):**

   | Función | Antes | Después | Ruta y schema |
   |---|---|---|---|
   | `verify_email_account` | `dict` | `bool`: `True` si este enlace verificó el correo | `GET /usuarios/verificar-email` · `MessageResponse` |
   | `delete_user_account` | `dict` | `User` borrado | `DELETE /usuarios/{cedula}` · `MessageResponse` |
   | `recover_user_account` | `dict` | `User` recuperado | `PATCH /usuarios/{cedula}/recuperar` · `UserRecoveryResponse` |
   | `toggle_package_status` | `dict` | `None` | `PATCH /servicios/{id}/activar` y `…/desactivar` · `MessageResponse` |
   | `soft_delete_package` | `dict` | `None` | `DELETE /servicios/{id}` · `ServiceMessageResponse` |
   | `recover_package` | `dict` | `None` | `PATCH /servicios/{id}/recuperar` · `ServiceMessageResponse` |

   El código nuevo nace así.
5. **Fuera de esta decisión:** los textos de error (`detail` de las excepciones de dominio) siguen en los servicios,
   como manda ADR-0003; `image_uploader` sigue devolviendo `{"image_urls": […]}`, que lleva solo el dato y cuya ruta
   ya declara `ServiceImageOutput` (decisión 9 de la adenda); `GET /` de `app/main.py` no declara schema (decisión 7).

## Consecuencias

- El OpenAPI documenta las siete respuestas y `response_model` deja salir solo las claves del schema. El cuerpo que
  recibe el cliente no cambia: medido byte a byte en las siete rutas (`docs/deuda/BE-65/plan.md`).
- Los servicios se prueban sobre datos (`result is True`, `result is target`) y no sobre un `dict`.
- Los textos que lee el usuario quedan repartidos: los de éxito en los routers, los de error en los servicios. Unificar
  dónde viven es trabajo de `(backlog P2)` (campo `code` estable), no de esta decisión.
- Los campos de `UserRecoveryResponse` y `ServiceMessageResponse` se llaman como las claves que ya recibe el cliente
  (`cc`, `correo`, `nombre`, `apellido`, `UID`): son contrato con el cliente, como las rutas en español que exceptúa
  AGENTS §4 (b), y renombrarlas es `(backlog P2)`.
- El orden de los campos del schema es el orden de las claves en el cuerpo; el orden del `dict` que arma el router no
  cuenta.
- Una clave que el router añada y el schema no tenga se descarta sin aviso; una que el schema pida y el `dict` no
  traiga es un 500. Por eso los tests fijan el cuerpo exacto de cada ruta.
- Una letra cambiada en un texto no la detecta la suite, que no afirma sobre texto en español (AGENTS §5); la detecta
  la verificación final del plan, que busca cada texto literal.

## Alternativas consideradas

1. **Solo `response_model`, y el servicio sigue armando el `dict`** (recomendación de la sesión Mentor). Rechazada por
   David: el servicio seguiría escribiendo la respuesta HTTP.
2. **El servicio construye el schema de salida** (`MessageResponse(...)`). El contrato de capas lo permite. Rechazada:
   el texto y `success` seguirían en el servicio.
3. **Un `Enum` de resultado para `verify_email_account`.** Rechazado por YAGNI: hay dos casos y un `bool` con su
   docstring basta; un tercer caso lo cambiaría.
4. **Nombres en inglés con `serialization_alias`** (`cedula: str = Field(serialization_alias="cc")`). Medido en una
   copia: el cuerpo sale igual byte a byte y el OpenAPI publica las claves del alias. No elegido: el `dict` del router
   tendría que usar el nombre del campo y no el de la clave (con la clave, FastAPI lanza `ResponseValidationError`: medido, un 500), y el
   cambio de nombres es de `(backlog P2)`.
5. **Los textos en un módulo compartido** (`app/api/messages.py`). Rechazado: cada texto lo usa una sola ruta y el
   precedente de ADR-0023 lo deja en su router.

## Evidencia

- Verificación (27 nov): las siete rutas, las seis funciones y las tres formas, leídas en el código y con `grep`
  global; adenda con las decisiones 1 a 10.
- Plan: RED y GREEN de cada fase, compuerta completa, comparación byte a byte de las siete respuestas antes y después
  y mutantes, medidos en copias del repositorio (`docs/deuda/BE-65/plan.md`).
- FastAPI, "Response Model - Return Type" (https://fastapi.tiangolo.com/tutorial/response-model/): si una operación
  declara a la vez un tipo de retorno y `response_model`, manda `response_model`, que valida, filtra y documenta la
  salida. Leído en Context7 (`/websites/fastapi_tiangolo`, documentación vigente; FastAPI instalada 0.135.1).
- Pydantic 2.12.5, "Models · Field ordering" (https://github.com/pydantic/pydantic/blob/v2.12.5/docs/concepts/models.md): el orden
  de los campos se conserva al serializar y en el JSON Schema. Leído en Context7 (`/pydantic/pydantic`, v2.12.5).
````

## Anexo B — fase B (`diff -u` entre la copia base y la de B GREEN)

Cuatro archivos. Ya formateado; el ejecutor lo aplica tal cual.

```diff
--- a/app/schemas/service.py
+++ b/app/schemas/service.py
@@ -5,6 +5,7 @@
 from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
 
 from app.models.service import ServiceCategory
+from app.schemas.message import MessageResponse
 from app.schemas.partial_update import NoExplicitNull
 
 # Scale of tourist_services.base_price, NUMERIC(10, 2): every price is written with two decimals.
@@ -145,3 +146,17 @@
     def format_base_price(cls, v: Decimal) -> Decimal:
         """Writes the price with the two decimals of its column: 50000 becomes 50000.00."""
         return v.quantize(_CENTS)
+
+
+class ServiceMessageResponse(MessageResponse):
+    """Body of the routes that move a package to or from the recycle bin (BE-65).
+
+    Extends MessageResponse, another output DTO, never an input one (backlog A9). The keys
+    keep their current names and order, so the body the client reads does not change; UID
+    is renamed only by backlog P2.
+
+    Attributes:
+        UID: Identifier of the package the route acted on.
+    """
+
+    UID: int
--- a/app/services/tourist_services_service.py
+++ b/app/services/tourist_services_service.py
@@ -108,7 +108,7 @@
 
     async def toggle_package_status(
         self, service_id: int, is_available: bool, current_user: User
-    ) -> dict:
+    ) -> None:
         """Mutates the public availability state of a specific non-soft-deleted package.
 
         Transitions a package between the 'Por Activar' and 'Activos' columns.
@@ -120,9 +120,6 @@
             is_available (bool): Target availability (True for active, False for inactive).
             current_user (User): The administrator executing the mutation.
 
-        Returns:
-            dict: A standardized JSON response confirming the state change.
-
         Raises:
             NotFoundError: If the package does not exist or is deleted.
         """
@@ -131,8 +128,6 @@
         if not service:
             raise NotFoundError(detail="Paquete no encontrado.")
 
-        estado = "activado" if is_available else "desactivado"
-
         if service.is_available != is_available:
             service.is_available = is_available
             await self.service_repo.save_service(service)
@@ -145,9 +140,7 @@
                 performed_by=current_user.cedula,
             )
 
-        return {"success": True, "message": f"El paquete ha sido {estado} exitosamente."}
-
-    async def soft_delete_package(self, service_id: int, current_user: User) -> dict:
+    async def soft_delete_package(self, service_id: int, current_user: User) -> None:
         """Executes a soft deletion on a package to preserve its financial historical footprint.
 
         Transitions the package to the 'Eliminados' column by stamping the UTC timestamp
@@ -157,9 +150,6 @@
             service_id (int): The unique identifier of the package to delete.
             current_user (User): The administrator executing the deletion.
 
-        Returns:
-            dict: Standardized confirmation message.
-
         Raises:
             NotFoundError: If the package is already deleted or doesn't exist.
         """
@@ -179,13 +169,8 @@
             action=AuditAction.SOFT_DELETE,
             performed_by=current_user.cedula,
         )
-        return {
-            "success": True,
-            "message": "Paquete movido a la papelera (Eliminado lógicamente).",
-            "UID": service_id,
-        }
 
-    async def recover_package(self, service_id: int, current_user: User) -> dict:
+    async def recover_package(self, service_id: int, current_user: User) -> None:
         """Restores a soft-deleted package back to the operational workflow.
 
         As a business rule, recovered packages strictly transition to the 'Por Activar'
@@ -195,9 +180,6 @@
             service_id (int): The unique identifier of the deleted package.
             current_user (User): The administrator performing the recovery.
 
-        Returns:
-            dict: Standardized confirmation message.
-
         Raises:
             BusinessRuleViolationError: If the package was not actually deleted.
         """
@@ -222,12 +204,6 @@
             performed_by=current_user.cedula,
         )
 
-        return {
-            "success": True,
-            "message": "Paquete recuperado. Se encuentra en la sección 'Por Activar'.",
-            "UID": service_id,
-        }
-
     async def image_uploader(self, images_files: list[StagedImage]) -> dict:
         """Uploads images asynchronously to the Azure CDN.
 
--- a/app/api/routers/service.py
+++ b/app/api/routers/service.py
@@ -2,11 +2,13 @@
 
 from app.api.dependencies import AdminDep, get_current_admin_user, get_service_service
 from app.core.storage import StagedImage
+from app.schemas.message import MessageResponse
 from app.schemas.service import (
     ServiceCreate,
     ServiceDetailResponse,
     ServiceImageOutput,
     ServiceListResponse,
+    ServiceMessageResponse,
     ServiceUpdate,
 )
 from app.services.tourist_services_service import TouristServicesService
@@ -22,6 +24,13 @@
 public_router = APIRouter()
 admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])
 
+# Texts the end user reads after a change of state: the router builds the answer and the
+# service returns no text (ADR-0024).
+PACKAGE_ACTIVATED_MESSAGE = "El paquete ha sido activado exitosamente."
+PACKAGE_DEACTIVATED_MESSAGE = "El paquete ha sido desactivado exitosamente."
+PACKAGE_DELETED_MESSAGE = "Paquete movido a la papelera (Eliminado lógicamente)."
+PACKAGE_RECOVERED_MESSAGE = "Paquete recuperado. Se encuentra en la sección 'Por Activar'."
+
 
 # -------------------------------------------------------------------
 # PUBLIC ENDPOINTS
@@ -162,12 +171,12 @@
     return await service_service.update_package_details(service_id, update_payload, usuario_actual)
 
 
-@admin_router.patch("/{service_id}/activar")
+@admin_router.patch("/{service_id}/activar", response_model=MessageResponse)
 async def activar_paquete(
     service_id: int,
     usuario_actual: AdminDep,
     service_service: TouristServicesService = Depends(get_service_service),
-):
+) -> dict[str, bool | str]:
     """Protected Endpoint: Triggers a state mutation transitioning a package to active.
 
     The package will immediately become visible in the public tourist catalog.
@@ -178,17 +187,18 @@
         service_service (TouristServicesService): Injected business-logic service.
 
     Returns:
-        dict: Standardized JSON response confirming the state change.
+        dict: Success flag and the message to show, also when the package was already active.
     """
-    return await service_service.toggle_package_status(service_id, True, usuario_actual)
+    await service_service.toggle_package_status(service_id, True, usuario_actual)
+    return {"success": True, "message": PACKAGE_ACTIVATED_MESSAGE}
 
 
-@admin_router.patch("/{service_id}/desactivar")
+@admin_router.patch("/{service_id}/desactivar", response_model=MessageResponse)
 async def desactivar_paquete(
     service_id: int,
     usuario_actual: AdminDep,
     service_service: TouristServicesService = Depends(get_service_service),
-):
+) -> dict[str, bool | str]:
     """Protected Endpoint: Triggers a state mutation transitioning a package to inactive.
 
     The package is un-published from the public catalog but remains structurally intact.
@@ -199,17 +209,18 @@
         service_service (TouristServicesService): Injected business-logic service.
 
     Returns:
-        dict: Standardized JSON response confirming the state change.
+        dict: Success flag and the message to show, also when the package was already inactive.
     """
-    return await service_service.toggle_package_status(service_id, False, usuario_actual)
+    await service_service.toggle_package_status(service_id, False, usuario_actual)
+    return {"success": True, "message": PACKAGE_DEACTIVATED_MESSAGE}
 
 
-@admin_router.delete("/{service_id}")
+@admin_router.delete("/{service_id}", response_model=ServiceMessageResponse)
 async def borrar_paquete_logico(
     service_id: int,
     usuario_actual: AdminDep,
     service_service: TouristServicesService = Depends(get_service_service),
-):
+) -> dict[str, bool | str | int]:
     """Protected Endpoint: Performs a logical deletion (Soft Delete) on the target package.
 
     This fulfills the referential integrity constraints avoiding hard deletions.
@@ -221,17 +232,18 @@
         service_service (TouristServicesService): Injected business-logic service.
 
     Returns:
-        dict: Standardized confirmation message.
+        dict: Success flag, the message to show and the package identifier (UID).
     """
-    return await service_service.soft_delete_package(service_id, usuario_actual)
+    await service_service.soft_delete_package(service_id, usuario_actual)
+    return {"success": True, "message": PACKAGE_DELETED_MESSAGE, "UID": service_id}
 
 
-@admin_router.patch("/{service_id}/recuperar")
+@admin_router.patch("/{service_id}/recuperar", response_model=ServiceMessageResponse)
 async def recuperar_paquete(
     service_id: int,
     usuario_actual: AdminDep,
     service_service: TouristServicesService = Depends(get_service_service),
-):
+) -> dict[str, bool | str | int]:
     """Protected Endpoint: Recovers a soft-deleted package.
 
     Resets the deletion timestamp and forces the package state to inactive
@@ -243,9 +255,10 @@
         service_service (TouristServicesService): Injected business-logic service.
 
     Returns:
-        dict: Standardized confirmation message.
+        dict: Success flag, the message to show and the package identifier (UID).
     """
-    return await service_service.recover_package(service_id, usuario_actual)
+    await service_service.recover_package(service_id, usuario_actual)
+    return {"success": True, "message": PACKAGE_RECOVERED_MESSAGE, "UID": service_id}
 
 
 router = APIRouter()
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -16,6 +16,7 @@
 from sqlalchemy import select
 
 from app.api.dependencies import get_storage_client
+from app.api.routers import service as service_router
 from app.core.exceptions import (
     InvalidImageUrlError,
     StorageUnavailableError,
@@ -1221,3 +1222,102 @@
     changes = audits[0].changes
     assert changes is not None
     assert changes["image_urls"] == [PERMANENT_URL, second_permanent]
+
+
+# === BE-65: each package route answers its schema, built by the router (ADR-0024) ===
+
+
+@pytest.mark.parametrize(
+    ("route", "is_available", "message"),
+    [
+        pytest.param("activar", False, "PACKAGE_ACTIVATED_MESSAGE", id="activate-inactive"),
+        pytest.param("activar", True, "PACKAGE_ACTIVATED_MESSAGE", id="activate-active"),
+        pytest.param("desactivar", True, "PACKAGE_DEACTIVATED_MESSAGE", id="deactivate-active"),
+        pytest.param("desactivar", False, "PACKAGE_DEACTIVATED_MESSAGE", id="deactivate-inactive"),
+    ],
+)
+async def test_be65_status_route_answers_only_success_and_its_message(
+    client, db_session, admin_headers, route, is_available, message
+):
+    """Happy path and edge case: with or without a change, the body is the route's own message."""
+    package = await _persist_package(db_session, is_available=is_available)
+
+    response = await client.patch(f"/servicios/{package.id}/{route}", headers=admin_headers)
+
+    assert response.status_code == 200
+    assert list(response.json().items()) == [
+        ("success", True),
+        ("message", getattr(service_router, message)),
+    ]
+
+
+async def test_be65_soft_delete_answers_its_message_and_the_package_id(
+    client, db_session, admin_headers
+):
+    """Happy path: the body is success, the route's message and UID, in that order, no more."""
+    package = await _persist_package(db_session)
+    package_id = package.id
+
+    response = await client.delete(f"/servicios/{package_id}", headers=admin_headers)
+
+    assert response.status_code == 200
+    assert list(response.json().items()) == [
+        ("success", True),
+        ("message", service_router.PACKAGE_DELETED_MESSAGE),
+        ("UID", package_id),
+    ]
+    await db_session.refresh(package)
+    assert package.deleted_at is not None
+
+
+async def test_be65_recover_answers_its_message_and_the_package_id(
+    client, db_session, admin_headers
+):
+    """Happy path: the body is success, the route's message and UID, in that order, no more."""
+    package = await _persist_package(db_session, is_available=False, deleted_at=datetime.now(UTC))
+    package_id = package.id
+
+    response = await client.patch(f"/servicios/{package_id}/recuperar", headers=admin_headers)
+
+    assert response.status_code == 200
+    assert list(response.json().items()) == [
+        ("success", True),
+        ("message", service_router.PACKAGE_RECOVERED_MESSAGE),
+        ("UID", package_id),
+    ]
+    await db_session.refresh(package)
+    assert package.deleted_at is None
+
+
+@pytest.mark.parametrize(
+    ("method", "path", "schema_name"),
+    [
+        pytest.param("patch", "/servicios/{service_id}/activar", "MessageResponse", id="activate"),
+        pytest.param(
+            "patch", "/servicios/{service_id}/desactivar", "MessageResponse", id="deactivate"
+        ),
+        pytest.param("delete", "/servicios/{service_id}", "ServiceMessageResponse", id="delete"),
+        pytest.param(
+            "patch", "/servicios/{service_id}/recuperar", "ServiceMessageResponse", id="recover"
+        ),
+    ],
+)
+async def test_be65_package_route_declares_its_response_schema(client, method, path, schema_name):
+    """Edge case: the 200 answer of each route points to its schema in the OpenAPI."""
+    spec = (await client.get("/openapi.json")).json()
+
+    answer = spec["paths"][path][method]["responses"]["200"]["content"]["application/json"]
+    assert answer["schema"] == {"$ref": f"#/components/schemas/{schema_name}"}
+
+
+async def test_be65_service_message_response_documents_three_required_keys_in_order(client):
+    """Edge case: the schema lists success, message and UID, in the body's order, all required."""
+    spec = (await client.get("/openapi.json")).json()
+
+    schema = spec["components"]["schemas"]["ServiceMessageResponse"]
+    assert [(name, field.get("type")) for name, field in schema["properties"].items()] == [
+        ("success", "boolean"),
+        ("message", "string"),
+        ("UID", "integer"),
+    ]
+    assert sorted(schema["required"]) == ["UID", "message", "success"]
```

## Anexo C — fase C (`diff -u` entre la copia de B GREEN y la final)

Cinco archivos. Ya formateado; el ejecutor lo aplica tal cual.

```diff
--- a/app/schemas/user.py
+++ b/app/schemas/user.py
@@ -201,3 +201,28 @@
         """Silently applies title casing if the field is present in the payload."""
         clean = " ".join(v.split())
         return clean.title()
+
+
+class UserRecoveryResponse(BaseModel):
+    """Body of PATCH /usuarios/{cedula}/recuperar (BE-65).
+
+    Declared on BaseModel with no validators, never on an input DTO (backlog A9): the email
+    and names come from the database and are not checked again. The keys keep their current
+    names and order, message last, so the body the client reads does not change; the Spanish
+    keys are renamed only by backlog P2.
+
+    Attributes:
+        success: Whether the request was handled.
+        cc: Cedula of the recovered account.
+        correo: Its email.
+        nombre: Its first name.
+        apellido: Its last name.
+        message: Text for the end user.
+    """
+
+    success: bool
+    cc: str
+    correo: str
+    nombre: str
+    apellido: str
+    message: str
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -125,7 +125,7 @@
 
         return RegistrationResult(user=saved_user, verification_token=token)
 
-    async def verify_email_account(self, token: str) -> dict:
+    async def verify_email_account(self, token: str) -> bool:
         """Decodes the verification token and verifies the account's email, once.
 
         The link has one effect per account, not per token: the token is never stored and
@@ -143,8 +143,8 @@
             token (str): Email-verification JWT issued during registration.
 
         Returns:
-            dict: Confirmation payload with a success flag and the message to show,
-                which is another one once the email was already verified.
+            bool: True when this link verified the email; False when it was already
+                verified and nothing changed. The router words each case (ADR-0024).
 
         Raises:
             InvalidVerificationTokenError: Token corrupted, expired or
@@ -175,7 +175,7 @@
             raise NotFoundError("Usuario no encontrado.")
 
         if user.email_verified_at is not None:
-            return {"success": True, "message": "Su correo ya fue verificado."}
+            return False
 
         changes = changed_fields(user, {"is_active": True})
         user.email_verified_at = datetime.now(UTC)
@@ -190,10 +190,7 @@
                 changes=changes,
             )
 
-        return {
-            "success": True,
-            "message": "Cuenta verificada exitosamente. Ya puede iniciar sesión.",
-        }
+        return True
 
     async def resend_verification_link(self, email: str) -> VerificationResend | None:
         """Issues a new email-verification link when the account may receive one now.
@@ -251,7 +248,7 @@
         generated_token = create_access_token(data=token_payload)
         return TokenResponse(access_token=generated_token, token_type="bearer")
 
-    async def delete_user_account(self, target_cedula: str, current_user: User) -> dict:
+    async def delete_user_account(self, target_cedula: str, current_user: User) -> User:
         """Orchestrates the soft deletion of a user account enforcing hierarchical ABAC.
 
         Authorization follows a pure hierarchical invariant: the action is
@@ -264,7 +261,7 @@
             current_user (User): The authenticated user attempting the deletion.
 
         Returns:
-            dict: Standardized confirmation payload.
+            User: The account just soft-deleted; the router words the confirmation (ADR-0024).
 
         Raises:
             NotFoundError: 404 Not Found if the target doesn't exist.
@@ -293,13 +290,7 @@
             performed_by=current_user.cedula,
         )
 
-        return {
-            "success": True,
-            "message": (
-                f"La cuenta vinculada a {soft_deleted_user.email}, con C.C. {target_cedula} "
-                "ha sido eliminada exitosamente."
-            ),
-        }
+        return soft_deleted_user
 
     async def get_all_registered_users(self, current_user: User) -> list[User]:
         """Retrieves the user directory enforcing hierarchical visibility rules.
@@ -412,7 +403,7 @@
 
         return deleted_users
 
-    async def recover_user_account(self, target_cedula: str, current_user: User) -> dict:
+    async def recover_user_account(self, target_cedula: str, current_user: User) -> User:
         """Restores a soft-deleted user account enforcing RBAC precedence.
 
         Recovered accounts are structurally restored but forced into an inactive
@@ -428,7 +419,7 @@
             current_user (User): The authenticated administrator.
 
         Returns:
-            dict: Standardized confirmation payload.
+            User: The recovered account, inactive; the router builds the answer (ADR-0024).
 
         Raises:
             NotFoundError: 404 Not Found if the user is not in the recycle bin.
@@ -455,14 +446,7 @@
             performed_by=current_user.cedula,
         )
 
-        return {
-            "success": True,
-            "cc": target_user.cedula,
-            "correo": target_user.email,
-            "nombre": target_user.first_name,
-            "apellido": target_user.last_name,
-            "message": "Usuario recuperado. Se encuentra inactivo por seguridad.",
-        }
+        return target_user
 
     async def create_administrative_account(
         self, user_data: UserCreateByAdmin, current_user: User
--- a/app/api/routers/user.py
+++ b/app/api/routers/user.py
@@ -17,6 +17,7 @@
     UserCreate,
     UserCreateByAdmin,
     UserLogin,
+    UserRecoveryResponse,
     UserResponse,
     UserUpdate,
     VerificationResendRequest,
@@ -46,6 +47,13 @@
     "enlace. Revise su bandeja de entrada y la carpeta de correo no deseado. Si ya pidió uno "
     "hace poco, espere un minuto antes de intentarlo de nuevo."
 )
+# Texts the end user reads: the service returns what happened and the router words it (ADR-0024).
+EMAIL_VERIFIED_MESSAGE = "Cuenta verificada exitosamente. Ya puede iniciar sesión."
+EMAIL_ALREADY_VERIFIED_MESSAGE = "Su correo ya fue verificado."
+ACCOUNT_DELETED_MESSAGE = (
+    "La cuenta vinculada a {email}, con C.C. {cedula} ha sido eliminada exitosamente."
+)
+ACCOUNT_RECOVERED_MESSAGE = "Usuario recuperado. Se encuentra inactivo por seguridad."
 self_service_router = APIRouter(dependencies=[Depends(get_current_user)])
 admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])
 superadmin_router = APIRouter(dependencies=[Depends(get_current_superadmin_user)])
@@ -94,8 +102,12 @@
     return result.user
 
 
-@public_router.get("/verificar-email", status_code=status.HTTP_200_OK)
-async def verificar_cuenta(token: str, user_service: UserService = Depends(get_user_service)):
+@public_router.get(
+    "/verificar-email", response_model=MessageResponse, status_code=status.HTTP_200_OK
+)
+async def verificar_cuenta(
+    token: str, user_service: UserService = Depends(get_user_service)
+) -> dict[str, bool | str]:
     """Public endpoint: verifies the account's email with the emailed token.
 
     The first use fills the account's verification mark and activates the account if it
@@ -106,9 +118,11 @@
         user_service (UserService): Injected business-logic service.
 
     Returns:
-        dict: Success flag and the message to show.
+        dict: Success flag and the message to show, another one once the email was verified.
     """
-    return await user_service.verify_email_account(token)
+    verified_now = await user_service.verify_email_account(token)
+    message = EMAIL_VERIFIED_MESSAGE if verified_now else EMAIL_ALREADY_VERIFIED_MESSAGE
+    return {"success": True, "message": message}
 
 
 @public_router.post(
@@ -181,10 +195,12 @@
     return usuario_actual
 
 
-@self_service_router.delete("/{cedula}", status_code=status.HTTP_200_OK)
+@self_service_router.delete(
+    "/{cedula}", response_model=MessageResponse, status_code=status.HTTP_200_OK
+)
 async def eliminar_usuario(
     cedula: str, usuario_actual: UserDep, user_service: UserService = Depends(get_user_service)
-):
+) -> dict[str, bool | str]:
     """Protected endpoint: Performs a soft-delete on a target user account.
 
     Hierarchical ABAC is delegated to UserService: the action is allowed only
@@ -197,9 +213,15 @@
         user_service (UserService): Injected business-logic service.
 
     Returns:
-        dict: Standardized JSON confirmation payload.
+        dict: Success flag and the message to show, with the account's email and cedula.
     """
-    return await user_service.delete_user_account(target_cedula=cedula, current_user=usuario_actual)
+    deleted = await user_service.delete_user_account(
+        target_cedula=cedula, current_user=usuario_actual
+    )
+    return {
+        "success": True,
+        "message": ACCOUNT_DELETED_MESSAGE.format(email=deleted.email, cedula=cedula),
+    }
 
 
 @self_service_router.patch("/{cedula}", response_model=UserResponse)
@@ -271,10 +293,10 @@
     return await user_service.get_deleted_users(usuario_actual)
 
 
-@admin_router.patch("/{cedula}/recuperar")
+@admin_router.patch("/{cedula}/recuperar", response_model=UserRecoveryResponse)
 async def recuperar_usuario(
     cedula: str, usuario_actual: AdminDep, user_service: UserService = Depends(get_user_service)
-):
+) -> dict[str, bool | str]:
     """Protected endpoint: Recovers a soft-deleted user account.
 
     Delegates RBAC precedence rules to UserService to prevent standard admins
@@ -286,11 +308,19 @@
         user_service (UserService): Injected business-logic service.
 
     Returns:
-        dict: Standardized JSON confirmation payload.
+        dict: Success flag, the recovered account's cedula, email and names, and the message.
     """
-    return await user_service.recover_user_account(
+    recovered = await user_service.recover_user_account(
         target_cedula=cedula, current_user=usuario_actual
     )
+    return {
+        "success": True,
+        "cc": recovered.cedula,
+        "correo": recovered.email,
+        "nombre": recovered.first_name,
+        "apellido": recovered.last_name,
+        "message": ACCOUNT_RECOVERED_MESSAGE,
+    }
 
 
 # -------------------------------------------------------------------
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -3,8 +3,10 @@
 from unittest.mock import ANY
 
 import jwt
+import pytest
 from sqlalchemy import func, select
 
+from app.api.routers import user as user_router
 from app.core.config import get_settings
 from app.core.security import (
     create_verification_token,
@@ -641,3 +643,118 @@
     assert created.role == UserRole.admin
     assert created.is_active is True
     assert created.deleted_at is None
+
+
+# ==========================================
+# BE-65: EACH USER ROUTE ANSWERS ITS SCHEMA, BUILT BY THE ROUTER (ADR-0024)
+# ==========================================
+
+
+@pytest.mark.parametrize(
+    "is_active",
+    [
+        pytest.param(False, id="registered-tourist"),
+        pytest.param(True, id="activated-by-an-admin"),
+    ],
+)
+async def test_be65_verify_link_answers_one_message_per_case(client, persist_user, is_active):
+    """Happy path and edge case: the first click verifies and says so; the second says done."""
+    user = await persist_user(is_active=is_active)
+    url = f"/usuarios/verificar-email?token={create_verification_token(user.email)}"
+
+    first = await client.get(url)
+    second = await client.get(url)
+
+    assert first.status_code == second.status_code == 200
+    assert list(first.json().items()) == [
+        ("success", True),
+        ("message", user_router.EMAIL_VERIFIED_MESSAGE),
+    ]
+    assert list(second.json().items()) == [
+        ("success", True),
+        ("message", user_router.EMAIL_ALREADY_VERIFIED_MESSAGE),
+    ]
+
+
+async def test_be65_delete_answers_with_the_deleted_account_in_the_message(
+    client, persist_user, make_auth_headers
+):
+    """Happy path: an admin deletes a tourist; the message names the tourist, not the admin."""
+    admin = await persist_user(role=UserRole.admin)
+    tourist = await persist_user(role=UserRole.tourist, is_active=True)
+    expected = user_router.ACCOUNT_DELETED_MESSAGE.format(
+        email=tourist.email, cedula=tourist.cedula
+    )
+
+    response = await client.delete(f"/usuarios/{tourist.cedula}", headers=make_auth_headers(admin))
+
+    assert response.status_code == 200
+    assert list(response.json().items()) == [("success", True), ("message", expected)]
+
+
+async def test_be65_recover_answers_the_account_keys_in_their_order(
+    client, persist_user, make_auth_headers
+):
+    """Happy path: the body keeps cc, correo, nombre and apellido of the recovered account."""
+    admin = await persist_user(role=UserRole.admin)
+    tourist = await persist_user(
+        role=UserRole.tourist,
+        first_name="Ana",
+        last_name="Gómez",
+        is_active=False,
+        deleted_at=datetime.now(UTC),
+    )
+    expected = [
+        ("success", True),
+        ("cc", tourist.cedula),
+        ("correo", tourist.email),
+        ("nombre", "Ana"),
+        ("apellido", "Gómez"),
+        ("message", user_router.ACCOUNT_RECOVERED_MESSAGE),
+    ]
+
+    response = await client.patch(
+        f"/usuarios/{tourist.cedula}/recuperar", headers=make_auth_headers(admin)
+    )
+
+    assert response.status_code == 200
+    assert list(response.json().items()) == expected
+
+
+@pytest.mark.parametrize(
+    ("method", "path", "schema_name"),
+    [
+        pytest.param("get", "/usuarios/verificar-email", "MessageResponse", id="verify"),
+        pytest.param("delete", "/usuarios/{cedula}", "MessageResponse", id="delete"),
+        pytest.param("patch", "/usuarios/{cedula}/recuperar", "UserRecoveryResponse", id="recover"),
+    ],
+)
+async def test_be65_user_route_declares_its_response_schema(client, method, path, schema_name):
+    """Edge case: the 200 answer of each route points to its schema in the OpenAPI."""
+    spec = (await client.get("/openapi.json")).json()
+
+    answer = spec["paths"][path][method]["responses"]["200"]["content"]["application/json"]
+    assert answer["schema"] == {"$ref": f"#/components/schemas/{schema_name}"}
+
+
+async def test_be65_user_recovery_response_documents_six_required_keys_in_order(client):
+    """Edge case: the schema lists the six keys in the body's order, all required strings."""
+    spec = (await client.get("/openapi.json")).json()
+
+    schema = spec["components"]["schemas"]["UserRecoveryResponse"]
+    assert [(name, field.get("type")) for name, field in schema["properties"].items()] == [
+        ("success", "boolean"),
+        ("cc", "string"),
+        ("correo", "string"),
+        ("nombre", "string"),
+        ("apellido", "string"),
+        ("message", "string"),
+    ]
+    assert sorted(schema["required"]) == [
+        "apellido",
+        "cc",
+        "correo",
+        "message",
+        "nombre",
+        "success",
+    ]
--- a/tests/test_user_service.py
+++ b/tests/test_user_service.py
@@ -210,6 +210,33 @@
         )
 
 
+async def test_delete_returns_the_soft_deleted_account(user_repo, user_service, make_user):
+    """Happy path: the service returns the deleted account, whose email the router words."""
+    target = make_user(role=UserRole.tourist)
+    user_repo.get_user_by_cedula.return_value = target
+    actor = make_user(role=UserRole.admin)
+
+    result = await user_service.delete_user_account(target_cedula=target.cedula, current_user=actor)
+
+    assert result is target
+    user_repo.soft_delete_user.assert_awaited_once_with(target.cedula)
+
+
+async def test_recover_returns_the_recovered_account(user_repo, user_service, make_user):
+    """Happy path: the service returns the recovered account, inactive and out of the bin."""
+    target = make_user(role=UserRole.tourist, is_active=True, deleted_at=datetime.now(UTC))
+    user_repo.get_user_by_cedula.return_value = target
+
+    result = await user_service.recover_user_account(
+        target_cedula=target.cedula, current_user=make_user(role=UserRole.admin)
+    )
+
+    assert result is target
+    assert target.deleted_at is None
+    assert target.is_active is False
+    user_repo.save_user.assert_awaited_once_with(target)
+
+
 # ==========================================
 # AUTHENTICATION
 # ==========================================
@@ -285,8 +312,7 @@
         create_verification_token("turista@example.com")
     )
 
-    assert result["success"] is True
-    assert "message" in result
+    assert result is True
     assert user.is_active is True
     verified_at = user.email_verified_at
     assert verified_at is not None
@@ -313,7 +339,7 @@
         create_verification_token("turista@example.com")
     )
 
-    assert result["success"] is True
+    assert result is True
     assert user.is_active is True
     assert user.email_verified_at is not None
     user_repo.get_non_deleted_user_by_email.assert_awaited_once_with("turista@example.com")
@@ -332,17 +358,17 @@
         create_verification_token("turista@example.com")
     )
 
-    assert result["success"] is True
+    assert result is False
     assert user.is_active is False
     assert user.email_verified_at == VERIFIED_AT
     user_repo.save_user.assert_not_awaited()
     audit_service.log_transaction.assert_not_awaited()
 
 
-async def test_verify_email_second_use_answers_another_message(
+async def test_verify_email_second_use_reports_the_email_as_already_verified(
     user_repo, audit_service, user_service, make_user
 ):
-    """Edge case: a second use succeeds, writes nothing more and does not repeat the message."""
+    """Edge case: a second use succeeds, writes nothing more and reports no new verification."""
     user = make_user(email="turista@example.com", is_active=False)
     user_repo.get_non_deleted_user_by_email.return_value = user
     token = create_verification_token("turista@example.com")
@@ -350,10 +376,8 @@
     first = await user_service.verify_email_account(token)
     second = await user_service.verify_email_account(token)
 
-    assert first["success"] is True
-    assert second["success"] is True
-    assert set(first) == set(second) == {"success", "message"}
-    assert second["message"] != first["message"]
+    assert first is True
+    assert second is False
     user_repo.save_user.assert_awaited_once_with(user)
     audit_service.log_transaction.assert_awaited_once()
 
```

## Anexo D — viñeta propuesta para AGENTS §3 (la commitea David tras la última auditoría)

Va después de la viñeta "**Servicios** contienen reglas de negocio puras…":

```markdown
- **El router arma la respuesta (ADR-0024):** un servicio devuelve un dato del dominio (una entidad, un `NamedTuple`,
  un `bool`) o nada; nunca un `dict` de respuesta, un `success` ni un texto para el usuario. El router arma el cuerpo,
  declara su `response_model` y guarda cada texto de éxito como constante de su módulo. Los textos de error siguen en
  las excepciones de dominio (ADR-0003).
```

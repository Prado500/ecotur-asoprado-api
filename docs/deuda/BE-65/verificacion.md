# Verificación — BE-65: siete rutas sin `response_model` que devuelven un `dict`

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-65, línea 121; residual R3 de `docs/deuda/BE-64/plan.md`)
**Fecha:** 2026-11-27

## Qué describe el ítem
Siete rutas no declaran `response_model` y devuelven el `dict` que arma el servicio, contra AGENTS §3 (un router
devuelve schemas Pydantic). No todas tienen la misma forma: unas dan `{"success", "message"}` y otras añaden
claves (`UID`; `cc`, `correo`, `nombre`, `apellido`). Sin schema nada limita qué claves salen ni las documenta en el
OpenAPI. La fila pide un schema por forma, reutilizando `MessageResponse` (BE-64), sin renombrar las claves en
español (son de P2) y medir qué claves lee el cliente Flutter.

## Evidencia en el código
Las siete rutas existen y siguen sin `response_model`. Las líneas de `user.py` se movieron por BE-64 (la fila cita
`:81`, `:130`, `:220`); las de `service.py` coinciden. Las de `user_service.py` también se movieron (la fila cita
`:410-417`).

Rutas (decorador sin `response_model`, función sin anotación de retorno, `return` del `dict` del servicio):
- `app/api/routers/user.py:97` — `@public_router.get("/verificar-email", status_code=status.HTTP_200_OK)`;
  `:111` `return await user_service.verify_email_account(token)`.
- `app/api/routers/user.py:184` — `@self_service_router.delete("/{cedula}", status_code=status.HTTP_200_OK)`;
  `:202` `return await user_service.delete_user_account(...)`.
- `app/api/routers/user.py:274` — `@admin_router.patch("/{cedula}/recuperar")`; `:291-293`
  `return await user_service.recover_user_account(...)`.
- `app/api/routers/service.py:165` — `@admin_router.patch("/{service_id}/activar")`; `:183`
  `return await service_service.toggle_package_status(service_id, True, usuario_actual)`.
- `app/api/routers/service.py:186` — `@admin_router.patch("/{service_id}/desactivar")`; `:204`
  `toggle_package_status(service_id, False, usuario_actual)`.
- `app/api/routers/service.py:207` — `@admin_router.delete("/{service_id}")`; `:226`
  `return await service_service.soft_delete_package(service_id, usuario_actual)`.
- `app/api/routers/service.py:229` — `@admin_router.patch("/{service_id}/recuperar")`; `:248`
  `return await service_service.recover_package(service_id, usuario_actual)`.

Formas que arma el servicio (todas con firma `-> dict` sin parámetros de tipo):
- Forma 1, `{"success", "message"}` (coincide con `MessageResponse`, `app/schemas/message.py:4-15`):
  - `app/services/user_service.py:128` `verify_email_account(...) -> dict`; dos salidas con la misma forma:
    `:178` `{"success": True, "message": "Su correo ya fue verificado."}` y `:193-196`.
  - `app/services/user_service.py:254` `delete_user_account(...) -> dict`; `:296-302`.
  - `app/services/tourist_services_service.py:109-111` `toggle_package_status(...) -> dict`; `:148`
    `{"success": True, "message": f"El paquete ha sido {estado} exitosamente."}` (sirve a `activar` y `desactivar`).
- Forma 2, `{"success", "message", "UID"}` (`UID` es `int`, el `service_id`):
  - `app/services/tourist_services_service.py:150` `soft_delete_package(...) -> dict`; `:182-186`.
  - `app/services/tourist_services_service.py:188` `recover_package(...) -> dict`; `:225-229`.
- Forma 3, `{"success", "cc", "correo", "nombre", "apellido", "message"}` (todas `str` salvo `success`):
  - `app/services/user_service.py:415` `recover_user_account(...) -> dict`; `:458-465`.

Referencia ya resuelta (no es deuda): `app/api/routers/user.py:114-149`, `POST /usuarios/reenviar-verificacion` con
`response_model=MessageResponse` y `-> dict[str, bool | str]`; su test de OpenAPI es
`tests/test_verification_resend.py:249-261` (`test_route_declares_its_response_schema`).

Lo que afirman hoy los tests sobre esos cuerpos:
- `tests/test_auth.py:101` (`verificar-email`), `:222` (dos verificaciones) — `set(body) == {"success", "message"}`.
- `tests/test_auth.py:376` (`DELETE /usuarios/{cedula}`) — `set(body) == {"success", "message"}`.
- `tests/test_services.py:1095` (`activar`/`desactivar` sin cambio) — `set(response.json()) == {"success", "message"}`;
  `:1117` solo `["success"] is True`.
- `tests/test_auth.py:547` (`PATCH /usuarios/{cedula}/recuperar`) — `{"success", "message"} <= set(body)`: subconjunto;
  ningún test afirma `cc`, `correo`, `nombre` ni `apellido`.
- `tests/test_services.py:114-115` (`DELETE /servicios/{id}`) y `:123-126` (`PATCH .../recuperar`) — solo
  `status_code == 200`; ningún test afirma la clave `UID` ni la forma del cuerpo.
- `grep` de `"UID"`, `"cc"`, `"correo"`, `"nombre"`, `"apellido"` en `tests/`: cero coincidencias.
- `tests/test_route_guards.py:42, 49-52, 81, 97` — las siete rutas están en el inventario; BE-65 no lo toca.

Cliente Flutter (fuera de este repo; leído en `C:\projects\ecotur-asoprado-frontend_MVP_1\ecotur_app`, commit
`543598c`), solo para medir el riesgo de contrato:
- `lib/abstractions/api_client.dart:134-136` — ante un 2xx devuelve `{'success': true, 'data': decodedData}`: las
  claves del backend quedan dentro de `data`, y `success`/`message` que leen las vistas son del envoltorio del cliente.
- Las siete rutas se llaman en `lib/services/auth_service.dart:27`, `lib/services/user_service.dart:97, 104`,
  `lib/services/catalog_service.dart:87, 92, 97, 102`, y su resultado se lee en
  `lib/view_models/admin_kanban_viewmodel.dart:110-114, 145-149` y `lib/view_models/verification_viewmodel.dart:30-34`:
  solo `result['success']` y `result['message']`, nunca `result['data']`.
- `grep` de `['UID']`, `['cc']`, `['correo']`, `['nombre']`, `['apellido']` en `lib/`: cero coincidencias.
- Consecuencia: el cliente no lee hoy ninguna clave del cuerpo de estas rutas; un `response_model` que conserve las
  claves actuales no le cambia nada, y ni siquiera filtrar las claves extra lo rompería. (Efecto lateral observado, no
  de este ítem: en un 2xx `result['message']` es `null`, así que el aviso de éxito del kanban de paquetes sale vacío;
  es del cliente, no del backend.)

## Ficheros afectados (mapa completo)
- `app/api/routers/user.py` — tres rutas sin `response_model` (`:97`, `:184`, `:274`); ya importa `MessageResponse`
  (`:14`).
- `app/api/routers/service.py` — cuatro rutas sin `response_model` (`:165`, `:186`, `:207`, `:229`); hoy no importa
  ningún schema de mensaje.
- `app/schemas/message.py` — `MessageResponse` (forma 1); lugar natural de los schemas de las formas 2 y 3 si se
  decide que no son específicos de un dominio (o `app/schemas/service.py` / `app/schemas/user.py` si lo son).
- `app/services/user_service.py` — `:128`, `:254`, `:415` devuelven `dict` sin tipar (`:178`, `:193-196`,
  `:296-302`, `:458-465`).
- `app/services/tourist_services_service.py` — `:111`, `:150`, `:188` devuelven `dict` sin tipar (`:148`,
  `:182-186`, `:225-229`).
- `tests/test_auth.py`, `tests/test_services.py` — los tests que hoy miden (o no miden) esos cuerpos; donde
  entrarían los tests de forma y de OpenAPI.

## Rincones no mencionados por la fuente
1. **Una octava ruta sin `response_model`:** `app/main.py:205-207`, `GET /` (health check),
   `return {"status": "ok", "message": "Ecotur-ASOPRADO API (v0.2.0) está en línea"}`. Tiene otra forma
   (`status`, `message`) y vive en `app/main.py`, que es de `(backlog S5)`. La fila cuenta siete y no la menciona;
   queda a decisión de David si entra aquí o se anota aparte.
2. **Los servicios tipan `-> dict` sin parámetros** en las seis funciones citadas: mypy pasa porque `dict` desnudo es
   `dict[Any, Any]`. Un `response_model` en el router no cambia eso; tiparlas (o hacer que devuelvan el schema) es una
   decisión del plan, con el límite de AGENTS §3 de que los servicios no importan FastAPI (sí pueden importar
   `app.schemas`: el contrato de capas lo permite, y `user_service.py` ya importa `UserCreateByAdmin`).
3. **El mensaje del borrado de usuario lleva datos personales en el texto:** `app/services/user_service.py:298-301`,
   `f"La cuenta vinculada a {soft_deleted_user.email}, con C.C. {target_cedula} ha sido eliminada exitosamente."`.
   Un schema limita las claves, no el contenido de `message`; queda fuera del alcance de BE-65 (no es una clave).
4. **Ningún test cubre las claves extra** (`UID`; `cc`, `correo`, `nombre`, `apellido`): hoy cualquier cambio en ellas
   pasaría la compuerta. Los tests de forma que pida el plan nacen sin antecedente.
5. **El OpenAPI de las siete rutas** declara hoy el 200 con un schema vacío (FastAPI sin `response_model` ni anotación
   de retorno); el único precedente de test sobre `/openapi.json` es `tests/test_verification_resend.py:249-261`.

## Patrones de detección (copiables)
```bash
# Decoradores de ruta sin response_model (debe quedar vacío, salvo lo que el plan deje fuera, p. ej. GET / de main.py)
grep -nE "^@[a-z_]*router\.(get|post|put|patch|delete)\(" app/api/routers/*.py | grep -v response_model
grep -nE "^@[a-z_]*router\.(get|post|put|patch|delete)\($" -A2 app/api/routers/*.py   # decoradores multilínea
grep -nE "^@app\.(get|post|put|patch|delete)\(" app/main.py | grep -v response_model

# Servicios que devuelven dict sin tipar y los dict literales de respuesta
grep -nE "\) -> dict:" app/services/*.py
grep -nE "\"success\": True" app/services/*.py

# Claves extra de las formas 2 y 3 (en app/ y en tests/)
grep -rnE "\"UID\"|\"cc\"|\"correo\"|\"nombre\"|\"apellido\"" app/ tests/
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `0911898` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` =
  `git rev-parse origin/develop` = `09118987e8de03865eda287c1aeeb1cfcb7a3a0f`; rama `item/be-65`, árbol limpio).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Git Bash, raíz del repo; Python 3.14.3).

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```
- pytest: `845 passed, 29 warnings in 35.28s` (0 failed). Los 29 avisos son `StarletteDeprecationWarning`
  (`HTTP_422_UNPROCESSABLE_ENTITY`), ajenos al ítem.
- Cobertura total: `98.73%` (`TOTAL 1098 10 160 6 98.73%`; mínimo exigido 92.0 %).
- ruff format: `75 files already formatted`. ruff check: `All checks passed!` (0 errores).
- mypy: `Success: no issues found in 70 source files` (0 errores).
- import-linter: `Contracts: 4 kept, 0 broken.`
- docs: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
El plan debe declarar `response_model` en las siete rutas con un schema por forma: `MessageResponse` para
`verificar-email`, `DELETE /usuarios/{cedula}`, `activar` y `desactivar`; uno nuevo para `{success, message, UID}`
(borrado y recuperación de paquetes) y otro para `{success, cc, correo, nombre, apellido, message}` (recuperación de
usuario), sobre `BaseModel` sin validadores (A9), con las claves tal cual están (renombrarlas es P2). No debe tocar
`tests/test_route_guards.py`, las claves ni los textos, ni `app/main.py` salvo decisión explícita de David sobre `GET /`
(rincón 1, terreno de S5). Riesgo de contrato bajo y medido: el cliente Flutter no lee ninguna clave del cuerpo de estas
rutas. El riesgo real es la falta de tests: `UID` y las claves de la recuperación de usuario no las afirma nadie, así
que los tests RED deben fijar la forma exacta (`set(body) == {...}`) y el schema en `/openapi.json` de cada ruta antes
del cambio; decidir también si los servicios dejan de devolver `dict` sin tipar (rincón 2).

## Adenda — decisiones de David antes de planear (27 nov 2026, 17:48, sesión Mentor)

Resuelve lo que la conclusión deja abierto y **cambia su alcance**: donde la "Conclusión para el planificador" y esta
adenda difieran, rige la adenda. El planificador toma estas decisiones como dadas; lo demás (fases, tests, commits,
nombres) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base
aceptada:** `0911898`, compuerta completa en verde (845 passed · 98,73 % · ruff 0 en 75 · mypy 0 en 70 · 4 kept).

Contraste de la sesión Mentor contra el código de `1126d29`, sin correcciones de hecho: las siete rutas sin
`response_model` (`app/api/routers/user.py:97`, `:184`, `:274`; `app/api/routers/service.py:165`, `:186`, `:207`,
`:229`; de 22 rutas, 15 lo declaran); las tres formas (`app/services/user_service.py:178`, `:193-196`, `:296-302`,
`:458-465`; `app/services/tourist_services_service.py:148`, `:182-186`, `:225-229`); `grep` de `"UID"`, `"cc"`,
`"correo"`, `"nombre"` y `"apellido"` en `tests/`: 0; `app/main.py:205-207`. **No contrastado:** nada de lo que esta
verificación afirma del cliente Flutter; ese repositorio no está conectado a la sesión Mentor. Queda como leído por
el verificador.

### Decisiones

1. **Decidido (David, 17:27): las claves de las respuestas se conservan todas.** El cuerpo de las siete rutas no
   cambia: mismas claves y mismos valores, `UID`, `cc`, `correo`, `nombre` y `apellido` incluidas. La fila ya lo
   pedía (un schema por forma; las claves en español son de `(backlog P2)`). Razón de David: el backend envía y el
   cliente decide qué pinta; lo que hoy el cliente no usa queda disponible para cuando se mejore, y si algo sobra lo
   barato es que el cliente lo reciba y no lo muestre. Si un atributo resulta sensible, se quita del `response_model`
   el día que se determine.
2. **Decidido (David, 17:33): el servicio deja de armar la respuesta.** Las seis funciones que hoy devuelven un
   `dict` con `success` y un texto para el usuario (`verify_email_account`, `delete_user_account`,
   `recover_user_account`, `toggle_package_status`, `soft_delete_package`, `recover_package`) pasan a devolver un
   dato del dominio o nada; nunca `success` ni un texto para el usuario. Palabras de David: "no tiene sentido que el
   servicio esté envolviendo diccionarios. Sé que es más trabajo, pero ya que estamos hagámoslo bien hecho y
   completo". Va más allá de la fila, que pedía solo `response_model`; la sesión Mentor recomendó hacer solo eso y
   dar fila a lo demás. Qué devuelve cada función (nombres y tipos), del planificador.
3. **Decidido (David, 17:38): el router arma la respuesta y declara su `response_model`**, en las siete rutas, con
   un schema por forma (`MessageResponse`, de BE-64, para la forma 1; dos nuevos para las formas 2 y 3), sobre
   `BaseModel`, sin validadores y sin heredar de un DTO de entrada (AGENTS §3, A9). Los textos se mueven al router
   **letra por letra**, como constantes, igual que `RESEND_VERIFICATION_MESSAGE` (`app/api/routers/user.py:43-47`).
   Es el patrón que BE-64 ya usa: su servicio devuelve `VerificationResend | None` y el router arma el cuerpo.
4. **Decidido (David, 17:38): `verify_email_account` tiene dos mensajes** ("Su correo ya fue verificado." y "Cuenta
   verificada exitosamente. Ya puede iniciar sesión."): el servicio le dice al router cuál de los dos casos ocurrió,
   sin texto. La regla del enlace no cambia (ADR-0022).
5. **Decidido (David, 17:38): tests primero.** La forma exacta del cuerpo de cada ruta (`set(body) == {...}`, con
   las claves de más, que hoy no afirma nadie) y su esquema en `/openapi.json`, en RED antes de tocar `app/`. Los
   tests HTTP que ya existen no cambian de resultado, porque el cuerpo no cambia. Los unitarios que afirman sobre el
   `dict` del servicio se reescriben: hoy son `tests/test_user_service.py:288`, `:316` y `:335`
   (`result["success"] is True`). Medido por la sesión Mentor con `grep`: 13 llamadas a `verify_email_account` en
   `tests/`, 1 a `delete_user_account`, 2 a `recover_user_account`; las tres funciones de paquetes no tienen tests
   unitarios, se prueban por HTTP.
6. **Decidido (David, 17:38): la decisión pide ADR, el 0024**: el servicio devuelve datos del dominio y el router
   arma la respuesta. Es un patrón para todo el código, no solo para estas rutas (AGENTS §7). Lo escribe una fase del
   plan; la viñeta de AGENTS §3 la propone el plan y la commitea David tras la última auditoría. Relación: ADR-0003
   (el servicio no conoce el transporte) y ADR-0015 (`app.cli` es un segundo adaptador, que no quiere un `dict`
   pensado para HTTP).
7. **Decidido (David, 17:38): `GET /` queda fuera, sin fila** (rincón 1). Criterio de David: entra solo si una
   fuente de autoridad recomienda que un health check declare schema; si no, sería sobreingeniería. No se halló
   ninguna que lo exija (ver "Fuentes"). Su respuesta son dos textos fijos, sin datos de ninguna cuenta.
8. **Decidido (David, 17:38): el mensaje del borrado de una cuenta, con el correo y la cédula en el texto, queda
   como está** (rincón 3) y recibe fila en `B-FUTURO`, severidad Baja: `(backlog BE-66)`. Criterio de David: si las
   fuentes lo dan por aceptable para un MVP, se deja; si no, sería ítem nuevo. Quien recibe el mensaje es quien hizo
   el borrado: la cédula la puso en la URL y el correo es el suyo o el de una cuenta de rango inferior que ya puede
   consultar; no es una propiedad que no deba leer, aunque el texto no necesita repetirla (ver "Fuentes"). El texto
   se mueve al router sin cambiar una letra, así que el servicio devuelve lo necesario para armarlo.
9. **Decidido (David, 17:44): `image_uploader` queda como está, sin fila.**
   (`app/services/tourist_services_service.py:231-254`). La sesión Mentor la trajo por un `grep` de `-> dict` y no
   es el mismo caso: su ruta ya declara `response_model=ServiceImageOutput` (`app/api/routers/service.py:49-50`) y
   su `dict` solo lleva el dato (`{"image_urls": [...]}`), sin `success` ni texto.
10. **Fuera, sin cambios:** renombrar claves o textos `(backlog P2)`; `tests/test_route_guards.py` (las siete rutas
    ya están en el inventario); `app/main.py`; el `commit()` de los repositorios (A3); la auditoría de cada operación
    (ADR-0021), que sigue escribiéndose donde hoy; el cliente Flutter.

### Avisos para planear y ejecutar

- **No toca `app/models/` ni `alembic/`:** no hacen falta pasos contra PostgreSQL.
- Con `/deuda-planear` viaja la petición de medir en copias `git archive` (texto en la bitácora `2026-11-19`).
- Si Windows bloquea `_rustgrimp`, el ítem lleva una cláusula como la de E0, punto 3, de BE-64 `(backlog AF-17)`.
- El contrato de capas permite que un servicio importe `app.schemas`, pero la decisión 2 pide lo contrario para
  estas respuestas: ningún servicio construye un schema de salida ni un `dict` de respuesta.
- La comprobación en el cliente Flutter antes de mezclar la hace David: las siete acciones contra el backend de la
  rama (activar, desactivar, borrar y recuperar un paquete; borrar y recuperar un usuario; verificar un correo).
- **Sin decidir al escribir esta adenda:** el efecto lateral que el verificador anota en el cliente (el aviso de
  éxito del kanban de paquetes saldría sin texto). David lo está comprobando; es del cliente y no cambia este ítem.

### Fuentes

Buscadas por la sesión Mentor el 27 nov (búsqueda web; extractos, no las páginas enteras). **Si el ADR las cita, el
planificador las lee antes** (regla del 14 nov).

- IETF, Internet-Draft "Health Check Response Format for HTTP APIs", `draft-inadarei-api-health-check-06`
  (`https://datatracker.ietf.org/doc/draft-inadarei-api-health-check/`): propone un JSON con un único campo
  obligatorio, `status`; es un borrador individual, sin respaldo del IETF y expirado. No trata de declarar un schema.
- FastAPI, "Response Model - Return Type" (`https://fastapi.tiangolo.com/tutorial/response-model/`): `response_model`
  puede usarse en cualquier operación y sirve para documentar, validar y filtrar la salida. No menciona los health
  checks.
- OWASP API Security Top 10, API3:2023 "Broken Object Property Level Authorization"
  (`https://owasp.org/API-Security/editions/2023/pt-pt/0xa3-broken-object-property-level-authorization/`; leídos los
  extractos de las ediciones en portugués y en francés, no la inglesa): pide mantener las estructuras devueltas en el mínimo que el
  endpoint necesita; el defecto es exponer propiedades sensibles que ese usuario no debería leer.

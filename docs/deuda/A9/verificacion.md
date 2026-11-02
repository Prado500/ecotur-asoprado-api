# Verificación — A9: los DTO de salida heredan las validaciones de entrada (500 al leer)

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A2, fila A9, l.73) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` (§4, tag `A9`, l.563-575)
**Fecha:** 2026-11-02

## Qué describe el ítem
`UserResponse` hereda de `UserBase`, el DTO del formulario de entrada, así que FastAPI valida cada respuesta contra
las reglas del formulario (patrón de nombres, longitudes, `EmailStr`, patrón de teléfono y de cédula). Si un registro
guardado no cumple esas reglas (porque entró por migración, por carga inicial, por SQL a mano o porque el patrón cambió
después), leerlo devuelve un 500 `ResponseValidationError` en vez del recurso. El informe pone como ejemplo nombres
legítimos que el patrón rechaza: "Jean-Luc", "O'Brien" y "D'Angelo".

## Evidencia en el código
- `app/schemas/user.py:108` — `class UserResponse(UserBase):`. Es la ocurrencia que cuenta el backlog (**1**) y sigue igual.
- `app/schemas/user.py:18-49` — restricciones de entrada que `UserResponse` hereda:
  - `:21-27` `cedula`: `min_length=6, max_length=10, pattern=r"^\d{6,10}$"`
  - `:29` `email: EmailStr`
  - `:31-37` `first_name` y `:38-44` `last_name`: `min_length=2, max_length=65, pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$"`.
    El patrón no admite guion ni apóstrofo.
  - `:45-49` `phone`: `pattern=r"^3\d{9}$"`
  - `:19` `model_config = ConfigDict(str_strip_whitespace=True)`, que Pydantic v2 fusiona con el `model_config` de `:113`
- `app/schemas/user.py:52-59` — `format_title_case` (`v.title()`) también se ejecuta **al serializar la salida**, así
  que reescribe en silencio lo que está guardado (ver "Rincones").
- `app/schemas/user.py:113` — `model_config = {"from_attributes": True}`. Es el dict que cuenta S6.
- La base de datos no aplica las mismas reglas, así que puede guardar datos que el DTO de salida rechaza:
  - `app/models/user.py:34` `cedula = Column(String(13)…)`, frente a un máximo de 10 dígitos en el schema
  - `app/models/user.py:37-38` `first_name`/`last_name` `String(100)`, frente a `max_length=65` y el patrón
  - `app/models/user.py:39` `phone = Column(String(20)…)`, frente a `^3\d{9}$`
  - `alembic/versions/a0f621304d75_init_esquema_inicial_limpio.py:41-42` crea la tabla con `String(length=100)` y sin CHECK.
- Endpoints que validan su salida con `UserResponse`:
  - `app/api/routers/user.py:45` `POST /usuarios/registro`
  - `app/api/routers/user.py:114` `GET /usuarios/mi-perfil`
  - `app/api/routers/user.py:147` `PATCH /usuarios/{cedula}`. El servicio ya hizo commit cuando falla la serialización,
    así que la mutación queda guardada y el cliente recibe un 500.
  - `app/api/routers/user.py:178` `GET /usuarios/` con `list[UserResponse]`: **un solo** registro inválido tumba el directorio entero.
  - `app/api/routers/user.py:197` `GET /usuarios/admin/eliminados` con `list[UserResponse]`
  - `app/api/routers/user.py:238` `POST /usuarios/admin`
- `app/main.py:32` — solo hay handler para `RequestValidationError`; `ResponseValidationError` no tiene ninguno y
  acaba en 500 (`grep ResponseValidation app/` vacío).
- **Reproducción empírica** (script fuera del repo, en el scratchpad de la sesión: FastAPI + `TestClient` sobre los
  schemas reales y objetos con atributos, sin BD). Resultado con `venv/Scripts/python.exe`:
  ```
  ok 200 {... 'first_name': 'Jean', ...}
  hyphen 500 Internal Server Error          # first_name="Jean-Luc"
  apostrophe 500 Internal Server Error      # last_name="O'Brien"
  long66 500 Internal Server Error          # first_name de 66 caracteres (cabe en String(100))
  phone_landline 500 Internal Server Error  # phone="6012345678" (cabe en String(20))
  cedula_11 500 Internal Server Error       # cedula de 11 dígitos (cabe en String(13))
  email_local 500 Internal Server Error     # email="admin@localhost"
  mcdonald 200 {... 'last_name': 'Mcdonald' ...}   # guardado "McDonald", devuelto reescrito
  svc 500 Internal Server Error             # ServiceDetailResponse con name="Tour corto", max_capacity=50, base_price=1000
  ```
- Tests: ningún test cubre este comportamiento. `grep -rn "ResponseValidationError\|Jean\|O'Brien\|Brien" tests/`
  no devuelve nada, y `UserResponse` no aparece en `tests/`.

## Ficheros afectados (mapa completo)
- `app/schemas/user.py` — `UserResponse(UserBase)` en l.108; las restricciones heredadas en l.18-59.
- `app/schemas/service.py` — `ServiceListResponse(ServiceBase)` en l.60 y `ServiceDetailResponse(ServiceBase)` en l.66.
  Es el mismo defecto y la fuente no lo menciona (ver abajo).
- `app/api/routers/user.py` — consume `UserResponse` como `response_model` en l.45, 114, 147, 178, 197 y 238. No hay que
  tocarlo si el nombre del schema se mantiene.
- `app/api/routers/service.py` — consume `ServiceListResponse`/`ServiceDetailResponse` en l.32, 86, 110, 126 y 142.
  Tampoco hay que tocarlo si se mantienen los nombres.
- `app/models/user.py`, `app/models/service.py` — no hay que cambiarlos; explican por qué la BD admite datos que el DTO
  rechaza (l.34-39 y l.19, 22, 24).
- `tests/` — falta el test que reproduzca el 500 (rojo esperado antes de corregir).

## Rincones no mencionados por la fuente
1. **Paquetes turísticos, mismo defecto.** `app/schemas/service.py:60` `class ServiceListResponse(ServiceBase)` y
   `:66` `class ServiceDetailResponse(ServiceBase)` heredan de `ServiceBase` (l.15-48): `name` con `min_length=20,
   max_length=65` (l.18-23), `base_price` con `ge=40000` (l.27-33), `max_capacity` con `gt=0, le=30` (l.35),
   `description` con `max_length=1000` (l.24), y además el validador `format_service_name` (l.39-48). La columna admite
   más que el schema (`app/models/service.py:19` `name String(150)`; `:22` `Numeric(10, 2)` sin mínimo; `:23` `Integer`
   sin tope). El caso más expuesto es **`GET /servicios/` (público)** en `app/api/routers/service.py:32`, con
   `list[ServiceListResponse]`: basta un paquete fuera de regla (un nombre corto cargado a mano, o el precio mínimo o
   el aforo máximo cambiados mañana) para que el catálogo entero devuelva 500. Reproducido arriba (`svc 500`).
2. **Reescritura silenciosa en la lectura.** Los validadores `format_title_case` (`app/schemas/user.py:52-59`) y
   `format_service_name` (`app/schemas/service.py:39-48`) corren también en la salida: "McDonald" guardado sale como
   "Mcdonald" y "DeLaCruz" como "Delacruz". No hay 500, pero la API devuelve un dato distinto del guardado.
3. **500 después del commit en `PATCH /usuarios/{cedula}`** (`app/api/routers/user.py:147`) y en
   `PUT /servicios/{id}` (`app/api/routers/service.py:142`): si el registro ya era inválido, la escritura se guarda y la
   respuesta es 500. El cliente no sabe que el cambio se aplicó.
4. **No afectado:** `AuditLogResponse(AuditLogBase)` (`app/schemas/audit.py:25`) hereda de su base, pero
   `AuditLogBase` (l.7-14) no tiene restricciones. `ServiceImageResponse` y `TokenResponse` heredan de `BaseModel`.
5. **Fuera del alcance de A9 (para el backlog, no para este plan):** la bitácora del 2 nov (l.485) da S7 por
   desaparecido porque `grep "Field(default=\[\]"` sale vacío. Pero `app/schemas/service.py:53-54` sigue teniendo
   `image_urls: list[HttpUrl] = Field(` / `default=[],`, en dos líneas. Es un falso negativo del grep de una sola línea.

## Patrones de detección (copiables)
```bash
# 1. DTO de salida que hereda de una base de entrada (debe quedar vacío, salvo AuditLogResponse, que no tiene restricciones)
grep -rnE "class \w+Response\(\w+Base\)" app/schemas/

# 2. Las tres ocurrencias concretas de hoy
grep -nE "class (UserResponse|ServiceListResponse|ServiceDetailResponse)\(" app/schemas/

# 3. Endpoints que validan su salida con esos DTO (11 hoy: 6 en usuarios, 5 en servicios)
grep -rnE "response_model=(list\[)?(UserResponse|ServiceListResponse|ServiceDetailResponse)" app/api/routers/

# 4. Restricciones de formulario dentro de schemas (comparar antes y después: no deben aparecer en clases *Response)
grep -nE "pattern=|min_length=|max_length=|ge=|le=|gt=|EmailStr" app/schemas/user.py app/schemas/service.py

# 5. Ningún handler para ResponseValidationError (contexto; no es parte del fix)
grep -rn "ResponseValidation" app/

# 6. Tests que reproducen el defecto (hoy vacío; tras el plan debe tener resultados)
grep -rnE "Jean-Luc|O'Brien|ResponseValidation" tests/
```

## Línea base (python scripts/check.py)
- Base develop: `7c6d606` (`git fetch origin` OK; `merge-base HEAD origin/develop` == `rev-parse origin/develop` ==
  `7c6d606405157c56872166df2506a3f35b611fd0`; rama `bloque/b-higiene`, árbol limpio).
- Comando: `venv/Scripts/python.exe scripts/check.py`, desde la raíz del repo.
  Antes se corrió `python scripts/check.py` con el Python 3.14 del sistema y falló **por entorno**: faltan `mypy`,
  `importlinter` y `jwt`, y pytest no llega a cargar `conftest.py`. Las cifras de abajo salen del intérprete del `venv/`.
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
- ruff format: `140 files already formatted`.
- ruff check: `Found 97 errors.` (`[*] 19 fixable with the --fix option`). En los archivos de este ítem:
  `app/schemas/user.py` tiene **11** (I001 l.1, UP042 l.6, E501 l.26/36/43/58/66/74/92, D205 l.55/74) y
  `app/schemas/service.py` tiene **4** (I001 l.1, D205+D415 l.42, E501 l.56). ruff 0.17.2.
- mypy: `Found 44 errors in 12 files (checked 35 source files)`. **0** en `app/schemas/`.
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas api→services→repositories→models KEPT; servicios sin transporte
  HTTP KEPT; repositorios solo SQLAlchemy y modelos KEPT; modelos y schemas sin capas superiores KEPT).
- pytest: `333 passed, 1 warning in 12.41s`. 0 failed. El warning es S5 (`HTTP_422_UNPROCESSABLE_ENTITY`).
- Cobertura total: **92.76 %** (`Required test coverage of 92.0% reached`). `app/schemas/user.py` 84.85 %;
  `app/schemas/service.py` 95.74 %.
- **La compuerta ya falla antes de tocar nada** (ruff check y mypy, deuda heredada). El CI la corre con
  `--soft format,ruff,mypy` (`.azure-pipelines/ci-pipeline.yml:30`). La condición de cierre práctica es que no aparezcan
  errores nuevos de ruff ni de mypy en los archivos tocados, que pytest siga en verde y que la cobertura no baje del 92.76 %.

## Conclusión para el planificador
- Hay que resolver esto: los DTO de salida no pueden heredar restricciones ni validadores de entrada. `UserResponse`
  (`app/schemas/user.py:108`) es lo que pide el ítem. `ServiceListResponse` y `ServiceDetailResponse`
  (`app/schemas/service.py:60,66`) tienen la misma causa y exponen el catálogo público (`GET /servicios/`); el humano
  decide si entran en A9 (ver decisiones abiertas). El contrato JSON no debe cambiar: mismos nombres de campo, mismos
  tipos y mismos nombres de clase, para que routers y cliente Flutter queden intactos.
- Tests en rojo primero: un registro guardado en BD con `first_name="Jean-Luc"` (y otro con `last_name="O'Brien"`) debe
  responder 200 en `GET /usuarios/` y en `GET /usuarios/mi-perfil`, con el valor **tal cual está guardado**, no
  reescrito con title-case. Bordes: una lista con un solo registro inválido entre válidos, y un `PATCH` sobre un
  registro inválido. Hay que sembrar con `persist_user`, que escribe vía ORM y se salta los schemas. La regla de
  entrada se prueba aparte: que `POST /usuarios/registro` con "Jean-Luc" **siga** dando 422.
- No tocar: las reglas de entrada (`UserCreate`, `UserUpdate`, `ServiceCreate`, `ServiceUpdate`). Relajar el patrón para
  admitir guion o apóstrofo es una regla de negocio, no parte de A9. Tampoco tocar modelos, migraciones ni CHECK en BD
  (eso es S1/ADR-0002), ni D5 (`format_title_case` duplicado), D2 (`UserRole` doble), S6 (el dict de `model_config`;
  queda en `B-FUTURO` y lo arrastra cualquier copia de l.113) ni los 11+4 errores de ruff preexistentes. El hook de
  ruff los mostrará en cada edición; el plan debe declararlos residuales para que el ejecutor no los corrija "de paso".
- Riesgos: (1) Si se reordena la herencia, `str_strip_whitespace` y `from_attributes` deben seguir en el DTO de
  salida, o cambia lo que se serializa. (2) El I001 que el hook arregla solo en `schemas/user.py` y `schemas/service.py`
  es inofensivo (bitácora 2 nov, l.330), pero aparecerá en el diff. (3) Quitar el title-case de la salida no rompe los tests
  actuales: las dos aserciones sobre nombres (`tests/test_auth.py:39` y `:206`) entran por `UserCreate`/`UserUpdate`,
  que siguen aplicando el title-case en la entrada.

## Adenda — decisiones de David antes de planear (2 nov 2026, sesión Mentor)

1. **Paquetes: entran como Fase B, opcional por tiempo.** Fase A = `UserResponse` (`app/schemas/user.py`, tests de
   usuarios); Fase B = `ServiceListResponse` y `ServiceDetailResponse` (`app/schemas/service.py`, tests de paquetes).
   Misma causa (los DTO de salida heredan validadores y patrones de entrada). Si B no cabe en la media jornada, A9 cierra
   con A y los paquetes reciben fila propia en el cierre. Ninguna fase a medias.
2. **Patrón de nombres (guion, apóstrofo): fuera de A9.** Es regla de negocio; fila nueva en el backlog en el cierre.
3. **La salida devuelve lo guardado tal cual, sin `.title()` ni patrones.** La normalización es de entrada; un DTO de
   salida describe lo que hay, no valida ni transforma. `UserResponse` conserva `from_attributes=True`; `str_strip_whitespace`
   no es necesario en salida (no hay entrada que recortar), pero no es error conservarlo.
4. **S7 sigue como está** (`Field(default=[])` en `service.py:53-54`, schema de entrada): fuera de A9.
5. **Residuales de ruff en los archivos tocados:** se corrigen solo los que el hook exija para que el archivo quede en 0
   (ADR-0005) y se declaran aparte en el handoff; I001 tolerado hasta A4 (bitácora 2026-11-02; el reorden en
   `schemas/user.py` y `schemas/service.py` está bisecado como inofensivo).
6. **AGENTS §6 (compuerta con el Python del venv):** sí, en PR propio; no en este ítem.
7. **Corrección de David (16:56): la Fase B (paquetes) no es opcional.** A9 cierra con A y B auditadas; si hace falta,
   la reunión de las 18:00 se posterga un poco. Sustituye al "opcional por tiempo" del punto 1.

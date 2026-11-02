# PLAN — A9: Separar los DTO de salida de las reglas de entrada para que leer lo guardado nunca dé 500

- **Fecha:** 2026-11-02 · **Fuente:** `verificacion.md` (confirmada; la Adenda de David, puntos 1-7, manda sobre la
  "Conclusión para el planificador") · **Rama:** `bloque/b-higiene`
- **Base develop:** `7c6d606` (la de la verificación; el ejecutor la re-comprueba en su ritual de arranque)

## Resumen para aprobación

`UserResponse` hereda de `UserBase` (el formulario de registro) y `ServiceListResponse`/`ServiceDetailResponse` heredan
de `ServiceBase` (el formulario de paquetes). FastAPI valida cada respuesta contra esas reglas, así que un registro
guardado que no las cumple ("Jean-Luc", un fijo, un paquete de $1.000 o de 50 cupos) hace que la lectura responda 500.
Basta uno para tumbar el directorio de usuarios o el catálogo público. Además, la salida reescribe lo guardado
("McDonald" sale como "Mcdonald" y el dominio del correo sale en minúsculas). Se declaran los tres DTO de salida
directamente sobre `BaseModel`, con los mismos campos, tipos, orden, valores por defecto, nombres de clase y
`from_attributes`, pero sin patrones, longitudes, `EmailStr`, `ge`/`le` ni `.title()`. Dos fases, de dos archivos cada
una: A = usuarios, B = paquetes, y ambas obligatorias. Cada fase hace dos commits: primero `style` (limpia los errores
de ruff del schema sin cambiar comportamiento) y después `fix` (el cambio de A9 con sus tests). El riesgo principal es
que el documento OpenAPI pierde las restricciones y descripciones de esos tres componentes de respuesta. Los nombres y
tipos no cambian. NO se tocan las reglas de entrada, el patrón de nombres, routers, modelos, migraciones, S1, S6, S7,
D2 ni D5. No hace falta ADR.

## Objetivo y decisiones bloqueadas

Que la API devuelva lo que está guardado tal cual, sin volver a validarlo con las reglas del formulario. El contrato
JSON (nombres de campo, tipos y nombres de clase) y todas las reglas de entrada quedan idénticos.

1. Fase A = `UserResponse` (`app/schemas/user.py`). Fase B = `ServiceListResponse` y `ServiceDetailResponse`
   (`app/schemas/service.py`). Las dos son obligatorias y A9 cierra con A y B auditadas (adenda, puntos 1 y 7).
2. Los DTO de salida heredan de `BaseModel`, no de una base de entrada, y no tienen `Field(...)` con restricciones,
   descripciones de formulario ni `field_validator`. La salida no aplica `.title()`, no recorta y no normaliza
   (adenda, punto 3).
3. Se conservan los nombres de clase, los nombres de campo, los tipos (`str`, `int`, `bool`, `datetime`, `Decimal`,
   `UserRole`, `ServiceCategory`, `list[ServiceImageResponse]`), el orden de los campos, los valores por defecto y
   `from_attributes=True`. Para un registro válido, el JSON es idéntico byte a byte (sondeado, ver Análisis). Los
   routers no se tocan.
4. `UserBase`, `UserCreate`, `UserCreateByAdmin`, `UserUpdate`, `ServiceBase`, `ServiceCreate` y `ServiceUpdate`
   conservan todas sus reglas. El patrón de nombres no se relaja (adenda, punto 2).
5. Ruff (adenda, punto 5): en cada archivo de `app/schemas/` que se toque se corrige lo que el hook exija hasta dejarlo
   en 0, y eso va en un commit `style` propio **antes** del `fix`, sin cambiar comportamiento. I001 se tolera (el hook
   lo autocorrige; el reorden está bisecado como inofensivo en estos dos archivos). UP042 se silencia con un `noqa`
   en esa línea que cita D2, sin convertir a `StrEnum`.
6. Compuerta: `venv/Scripts/python.exe scripts/check.py`. Línea base: 333 passed, 92.76 %, ruff 97, mypy 44, 0 de mypy
   en `app/schemas/`, import-linter 4 KEPT. Para cerrar: ningún error nuevo de ruff ni de mypy en los archivos tocados,
   pytest en verde y cobertura ≥ 92.76 %.

## Análisis del redactor

**Comprobado hoy en el código.** `app/schemas/user.py:108` `class UserResponse(UserBase)` hereda las restricciones de
`:21-49` y el validador `format_title_case` de `:52-59`, más `str_strip_whitespace` (`:19`). `app/schemas/service.py:60`
y `:66` heredan de `ServiceBase` (`:15-48`: `min_length=20`, `max_length=65`, `ge=40000`, `max_digits`/`decimal_places`,
`gt=0, le=30`, `max_length=1000` y `format_service_name`). En el FastAPI instalado (0.135.1), `serialize_response`
(`venv/Lib/site-packages/fastapi/routing.py:273-306`) llama a `field.validate(response_content, …)` y, si hay errores,
lanza `ResponseValidationError`. `app/main.py` no tiene handler para esa excepción, así que acaba en 500. En el Pydantic
instalado (2.12.5), `validate_email` (`pydantic/networks.py:1318-1328`) devuelve `parts.normalized`: `EmailStr` en la
salida reescribe el correo guardado. Lo sondeé en el scratchpad (`"Ana@EXAMPLE.COM"` sale `"Ana@example.com"`), y es un
rincón más del punto 3 de la adenda. Hice otro sondeo en el scratchpad con las clases planas propuestas: para un
usuario y un paquete válidos, `model_dump_json()` es idéntico al de las clases actuales, y los ocho casos de usuario y
los cinco de paquete fuera de regla salen tal cual.

**Diseño.** Clases planas sobre `BaseModel`, con los campos en el mismo orden que hoy produce la herencia (primero los
de la base y luego los propios) y con los mismos valores por defecto (`phone=None`, `description=None`,
`category=ServiceCategory.otro`, `is_available=False`, `deleted_at=None`, `images=[]`). Así no cambian ni el JSON ni la
lista `required` del OpenAPI. Descarté tres alternativas: (a) una base de salida compartida para paquetes, porque añade
una clase y el patrón de detección 1 (`class \w+Response\(\w+Base\)`) la marcaría; (b)
`ServiceDetailResponse(ServiceListResponse)`, porque cambia el orden de las claves y ata el detalle a la lista; (c)
sobrescribir los campos en la subclase, porque los `field_validator` heredados siguen corriendo y es frágil. El precio
es duplicar seis declaraciones sin reglas entre las dos clases de paquetes. Es aceptable: cada DTO de salida se lee
entero en un solo sitio. `str_strip_whitespace` no pasa a la salida (punto 3: no hay entrada que recortar). En
`UserResponse` se conserva literal `model_config = {"from_attributes": True}` porque S6 está fuera de alcance. Los
paquetes ya usan `ConfigDict(from_attributes=True)`, y se conserva así.

**Por qué un commit `style` aparte (y no una lista en el handoff).** El hook (`.claude/hooks/ruff_on_edit.py`) aplica
`ruff format` y `ruff check --fix` en la **primera** edición, y devuelve los errores que no se pueden autocorregir. Si
esa limpieza se mezcla con el cambio de A9, el diff del `fix` deja de leerse línea por línea. Con un commit propio:
(1) la neutralidad se demuestra mecánicamente, con el mismo resultado de pytest y el documento `app.openapi()`
idéntico antes y después; (2) `git show <fix>` contiene solo A9, que es lo que David debe sustentar; (3) una lista en el
handoff no se puede verificar y un commit sí. Coste: un commit más por fase. `progress.json` guarda los dos hashes.

**Inventario de ruff (ruff 0.17.2, `--output-format concise`).** `app/schemas/user.py`: 11 errores (I001 l.1, UP042 l.6,
E501 l.26/36/43/58/66/74/92, D205 l.55/74). `app/schemas/service.py`: 4 errores (I001 l.1, D205+D415 l.42, E501 l.56).
`tests/test_services.py`: 0. `tests/test_user_response.py` no existe (nace en 0). Todos los E501 son descripciones,
docstrings o un comentario. Se reparten con concatenación implícita de cadenas, que da el mismo texto y por tanto el
mismo OpenAPI. UP042 (`UserRole(str, Enum)`) se resolvería con `StrEnum`, pero eso cambia `str()`/f-strings de un
enum que fluye hasta el ORM: es D2 (`Sale → B-FUTURO`). Por eso va un `noqa` en esa línea, con el mismo criterio que
`chore(alembic)` usó para F401 (bitácora 2 nov, decisión 15: "el `noqa` por línea muere con la línea").

**Qué congela qué.** Hoy no hay ningún test que use `UserResponse` ni datos fuera de regla (verificación). Los tests
nuevos congelan: (1) lectura tal cual, con valores que el formulario rechaza o reescribe, en cada lista y detalle;
(2) que un registro inválido no tumba la lista; (3) que el `PATCH`/`PUT` sobre un registro inválido responde 200 y
guarda el cambio; (4) que la entrada **sigue** rechazando (422 sin efecto en la BD) y **sigue** aplicando title-case.
Hoy ningún test demuestra (4): `tests/test_auth.py:39` y `:206` envían nombres que ya vienen en title-case. Siguen
congelando lo que ya congelaban: `tests/test_auth.py` (registro, PATCH, directorios, sobre datos válidos) y
`tests/test_services.py:155-186` (`PUT`, nombre y aforo válidos).

**Forma del RED.** `tests/conftest.py:68` usa `ASGITransport(app=app)`, y en httpx 0.28.1 `raise_app_exceptions=True`
por defecto. Por eso los casos rojos no ven un 500: la llamada del cliente **lanza** `ResponseValidationError` y pytest
marca el test como fallido con esa excepción. Los casos de reescritura (`McDonald`, dominio en mayúsculas, `DeLaCruz`)
fallan por aserción, con el valor reescrito.

**Orden y dependencias.** A y B son independientes: dominios distintos, archivos distintos y ningún import cruzado.
Se ordenan por severidad del ítem (A es la fila del backlog y la demo). A es la más pequeña: un DTO y 7 funciones de
test, frente a dos DTO y 8 funciones en B.

**Riesgos.** (1) OpenAPI: los componentes `UserResponse`, `ServiceListResponse` y `ServiceDetailResponse` pierden
`pattern`, `minLength`, `maxLength`, `format: email`, `exclusiveMinimum`, `maximum`, el `pattern` del `Decimal` y las
`description` de campo, y ganan la `description` de clase (el docstring). Nombres, tipos, `required` y `default` no
cambian. Si el cliente Flutter genera código desde el OpenAPI, no le afecta, porque los nombres y tipos son los mismos.
(2) `cedula`, `email` y los nombres se devuelven sin recortar. Para los datos que entraron por formulario no cambia
nada, porque ya entraron recortados. (3) Las aserciones de 422 leen la clave `"detalle"` (`app/main.py:94`), que es
deuda P2. Si P2 la renombra, esos tests se actualizan con ella. (4) El I001 que aplica el hook mueve solo el import de
`pydantic` debajo de la stdlib, y la bitácora del 2 nov lo bisecó como inofensivo en estos dos archivos.

**Qué NO se toca.** Los routers (`app/api/routers/user.py`, `service.py`), `app/main.py` (no se añade handler de
`ResponseValidationError`), modelos, migraciones, `tests/conftest.py`, `tests/test_auth.py`, los schemas de entrada
(salvo el reparto cosmético de líneas del commit `style`), `Field(default=[])` de `ServiceCreate` (S7), los documentos
vivos (los actualiza el cierre) y AGENTS §6.

## Regla de alcance

- **Sí:** las tres clases `*Response` señaladas; la limpieza de ruff de `app/schemas/user.py` y `app/schemas/service.py`
  (solo texto, comentarios, docstrings, orden de imports y un `noqa`); `tests/test_user_response.py` (nuevo); una
  sección nueva al final de `tests/test_services.py`.
- **No:** todo lo demás. Si aparece un hallazgo nuevo, va a Residuales y luego a `docs/backlog.md` en el cierre.

## Fases

**Ritual común a A y B** (`$SCRATCH` = scratchpad de la sesión ejecutora, fuera del repo):
`venv/Scripts/python.exe -c "import json; from app.main import app; print(json.dumps(app.openapi(), sort_keys=True, indent=1))"`
redirigido a `$SCRATCH/openapi-0.json` **antes de editar nada**, a `-1.json` tras el commit `style` y a `-2.json` tras
el `fix`. `diff 0 1` debe salir vacío. `diff 1 2` solo debe tocar los componentes de la fase. El ejecutor pega ambos
`diff --stat` en el handoff. Orden: commit `style`, después los tests en rojo (pegar la salida), después el cambio y
el verde, y por último el commit `fix`. El trailer `Co-Authored-By` lo añade la sesión ejecutora con su modelo. El resto
del mensaje es exacto.

### Fase A — `UserResponse` describe el usuario guardado (la más pequeña)

- **Archivos:** `app/schemas/user.py`, `tests/test_user_response.py` (nuevo).
- **Cambios exactos:**
  - *Commit A1 (`style`), solo `app/schemas/user.py`:* el I001 del hook; `class UserRole(str, Enum):  # noqa: UP042 (backlog D2)`;
    las descripciones largas de l.26, 36, 43 y 66 repartidas entre paréntesis con concatenación implícita (el texto
    resultante es idéntico carácter a carácter); el comentario de l.58 en dos líneas; los docstrings de l.55, 74 y 92
    reescritos con una línea de resumen ≤ 100 columnas, una línea en blanco y el cuerpo (mismo contenido). No cambia
    ningún identificador, regla ni valor. Resultado esperado: `ruff check app/schemas/user.py` sin errores.
  - *Commit A2 (`fix`):* `UserResponse` se sustituye por:
    ```python
    class UserResponse(BaseModel):
        """Serialized view of a stored user account.

        Declared on BaseModel on purpose: an output DTO describes what is stored and never
        re-applies the input rules of UserBase (patterns, lengths, EmailStr, title-case),
        so a row that predates or bypasses them is still readable (backlog A9).
        """

        cedula: str
        email: str
        first_name: str
        last_name: str
        phone: str | None = None
        id: int
        role: UserRole
        is_active: bool
        created_at: datetime
        model_config = {"from_attributes": True}
    ```
    La redacción del docstring es orientativa (inglés, Google Style, explica el porqué). Los campos, su orden, sus
    tipos, sus valores por defecto y el `model_config` son exactos. No cambia nada más en el archivo. `EmailStr`,
    `ConfigDict` y `Field` siguen en uso en las clases de entrada.
  - `tests/test_user_response.py`: docstring de módulo; fixture local `autouse` que hace
    `patch("app.api.routers.user.send_verification_email", autospec=True)`; constante `USER_RESPONSE_KEYS` con las 9
    claves; payload local `REGISTRATION_PAYLOAD`, con la misma forma que `tests/test_auth.py:10-18`; usuarios sembrados **solo** con `persist_user` (vía ORM, sin pasar por los schemas) y cabeceras con
    `make_auth_headers`.
- **Tests (RED primero)** (nombres exactos; se afirma sobre códigos, claves, valores guardados y estado de la BD, nunca
  sobre texto en español):
  1. `test_my_profile_returns_stored_values_verbatim`, parametrizado con `(campo, valor)`: `first_name="Jean-Luc"`,
     `last_name="O'Brien"`, `last_name="McDonald"`, `first_name="A" * 66`, `phone="6012345678"`,
     `cedula="12345678901"`, `email="admin@localhost"`, `email="Ana@EXAMPLE.COM"`. Llama a `GET /usuarios/mi-perfil`
     con las cabeceras de ese usuario y espera `200`, `set(body) == USER_RESPONSE_KEYS`, `body[campo] == valor`,
     `body["id"] == user.id` y `body["role"] == "tourist"`.
  2. `test_user_directory_survives_one_off_rule_record`: siembra un admin, dos turistas válidos y uno con
     `first_name="Jean-Luc"`. `GET /usuarios/` como admin responde `200`, el conjunto de `cedula` es igual a los cuatro
     sembrados y el elemento del caso raro trae `first_name == "Jean-Luc"`.
  3. `test_deleted_directory_returns_stored_names_verbatim`: siembra un turista con `last_name="O'Brien"`,
     `deleted_at=datetime.now(UTC)` e `is_active=False`. `GET /usuarios/admin/eliminados` como admin responde `200`,
     con un solo elemento, esa `cedula` y `last_name == "O'Brien"`.
  4. `test_patch_on_off_rule_record_returns_200_with_persisted_change`: un turista con `first_name="Jean-Luc"` hace
     `PATCH /usuarios/{cedula}` sobre sí mismo con `{"phone": "3001112233"}`. Espera `200`, `body["phone"] ==
     "3001112233"` y `body["first_name"] == "Jean-Luc"`. Tras `refresh`, la BD tiene el teléfono nuevo y el nombre
     intacto.
  5. `test_registration_still_rejects_hyphenated_name`: `POST /usuarios/registro` con un payload válido salvo
     `first_name="Jean-Luc"` responde `422`, y `[e["raw_field"] for e in body["detalle"]] == ["first_name"]`. No queda
     ningún `User` en la BD y el mock de correo no se llama (`assert_not_called`).
  6. `test_registration_still_title_cases_names`: `POST /usuarios/registro` con `first_name="jUAN"` y
     `last_name="pérez"` responde `201`, con `"Juan"`/`"Pérez"` en el cuerpo y en la BD. El mock se llama una vez:
     `assert_called_once_with(email_to=<email>, first_name="Juan", token=ANY, base_url=ANY)`.
  7. `test_patch_still_rejects_hyphenated_name`: un turista válido hace `PATCH` sobre sí mismo con
     `{"first_name": "Jean-Luc"}`. Responde `422`, `raw_field == "first_name"`, y el nombre de la BD no cambia.

  RED esperado sobre A1: fallan los 8 casos de 1. Seis lanzan `ResponseValidationError` y `McDonald` y
  `Ana@EXAMPLE.COM` fallan por aserción, con el valor reescrito. También fallan 2, 3 y 4 (`ResponseValidationError`;
  en 4 la mutación ya se guardó). 5, 6 y 7 están verdes hoy y siguen verdes: congelan la entrada (borde documentado,
  no RED). Son 7 funciones y 14 casos.
- **Criterio de aceptación:**
  - `venv/Scripts/python.exe -m pytest tests/test_user_response.py -q` → 14 passed. Suite completa: 333 + 14 = 347
    passed, 0 failed.
  - `venv/Scripts/python.exe -m ruff check app/schemas/user.py tests/test_user_response.py` → 0 errores (tolerado
    solo I001 si el hook no lo aplicó). `ruff format --check` sobre ambos → OK. Total de `ruff check .` ≤ 86 (97 − 11),
    o ≤ 87 si queda el I001.
  - `venv/Scripts/python.exe -m mypy` → ninguna línea de `app/schemas/user.py`; total ≤ 44.
  - `scripts/check.py`: import-linter 4 KEPT, docs ✔ y cobertura total ≥ 92.76 %.
  - Introspección: `UserResponse.__mro__[1] is BaseModel`, ningún campo con `metadata`, sin `field_validators`,
    `model_fields["email"].annotation is str` (comando en Verificación final).
  - `diff openapi-0 openapi-1` vacío. `diff openapi-1 openapi-2` limitado a `components.schemas.UserResponse`.
  - Mutaciones para el auditor, sobre la punta de A2 y restaurando después: M1, volver a `class UserResponse(UserBase)`
    → fallan 1 (8 casos), 2, 3 y 4. M2, `email: EmailStr` → falla el caso `Ana@EXAMPLE.COM` (y el de `localhost`).
    M3, quitar `format_title_case` de `UserBase` → falla 6.
- **Fuera de alcance de esta fase:** reglas de `UserBase`, `UserCreate`, `UserCreateByAdmin` y `UserUpdate`; el patrón
  de nombres; `UserRole` (D2) más allá del `noqa`; D5; S6 (el dict se conserva); `tests/test_auth.py`; los routers;
  un handler de `ResponseValidationError`; los paquetes.
- **Commit A1:**
  ```
  style(schemas): clear ruff findings in user schemas before A9

  app/schemas/user.py carried 11 ruff findings (I001, UP042, seven
  E501, two D205). A9 edits this file and ADR-0005 requires a touched
  file to end with zero findings, so the cleanup lands first in its
  own commit and the A9 fix that follows stays a pure behavior diff.

  - Long Field descriptions are split with implicit string
    concatenation: the strings, and therefore the OpenAPI document,
    are identical (app.openapi() diffed before and after).
  - Docstrings and one comment are re-wrapped into a summary line
    plus body (D205, E501); their content is unchanged.
  - I001 is the edit hook's autofix (pydantic import below the
    stdlib), bisected as harmless for this file (journal, 2 Nov).
  - UserRole keeps its (str, Enum) base behind a line-level noqa for
    UP042: StrEnum changes str() and f-string output of an enum that
    reaches the ORM, and unifying both UserRole enums is backlog D2.

  No behavior change: the test suite result is identical.
  ```
- **Commit A2:**
  ```
  fix(schemas): stop UserResponse from inheriting input validation

  UserResponse extended UserBase, the registration form DTO, so FastAPI
  validated every response against the form rules (name pattern,
  lengths, EmailStr, phone and cedula patterns) and re-ran its
  title-case validator. A stored row that predates or bypasses those
  rules made GET /usuarios/, /usuarios/mi-perfil and the deleted
  directory answer 500 (ResponseValidationError), and PATCH
  /usuarios/{cedula} committed the change and still answered 500. One
  such row took down the whole admin directory (backlog A9).

  - app/schemas/user.py: UserResponse now extends BaseModel and
    declares the same nine fields with plain types and no validators,
    so it describes what is stored instead of re-validating it: no
    pattern, no length limits, no EmailStr normalization, no
    title-case. Field names, types, order, defaults, the class name
    and from_attributes are unchanged. UserBase, UserCreate and
    UserUpdate keep every rule.
  - tests/test_user_response.py: off-rule stored values (hyphen,
    apostrophe, 66 chars, landline, 11-digit cedula, dotless domain,
    mixed-case surname and email domain) come back verbatim from
    /mi-perfil; the directory survives one off-rule row; the deleted
    directory and PATCH answer 200; registration and PATCH still
    reject a hyphenated name with 422 and registration still
    title-cases.

  The OpenAPI UserResponse component loses the input constraints and
  field descriptions. Relaxing the name pattern itself is a business
  rule tracked as its own backlog row.
  ```

### Fase B — `ServiceListResponse` y `ServiceDetailResponse` describen el paquete guardado

- **Archivos:** `app/schemas/service.py`, `tests/test_services.py`.
- **Cambios exactos:**
  - *Commit B1 (`style`), solo `app/schemas/service.py`:* el I001 del hook; el docstring de `format_service_name`
    (l.42) con una línea de resumen terminada en punto, una línea en blanco y el cuerpo (D205, D415); la `description`
    de l.56 repartida con concatenación implícita y el mismo texto. **No se toca `default=[]` de l.54** (S7). Resultado
    esperado: `ruff check app/schemas/service.py` sin errores.
  - *Commit B2 (`fix`):* las dos clases se sustituyen por:
    ```python
    class ServiceListResponse(BaseModel):
        """Serialized catalog view of a stored tourist package.

        Declared on BaseModel on purpose: it describes what is stored and never re-applies
        the input rules of ServiceBase (length, price floor, capacity cap, title-case), so
        one off-rule package cannot take the public catalog down (backlog A9).
        """

        name: str
        description: str | None = None
        category: ServiceCategory = ServiceCategory.otro
        base_price: Decimal
        max_capacity: int
        is_available: bool = False
        id: int
        images: list[ServiceImageResponse] = []
        model_config = ConfigDict(from_attributes=True)


    class ServiceDetailResponse(BaseModel):
        """Serialized detail view of a stored tourist package, including its timestamps.

        Same rationale as ServiceListResponse: no input rules on output (backlog A9).
        """

        name: str
        description: str | None = None
        category: ServiceCategory = ServiceCategory.otro
        base_price: Decimal
        max_capacity: int
        is_available: bool = False
        id: int
        created_at: datetime
        deleted_at: datetime | None = None
        images: list[ServiceImageResponse] = []
        model_config = ConfigDict(from_attributes=True)
    ```
    Igual que en A: los docstrings son orientativos y los campos, el orden, los defaults y la configuración son exactos.
    No cambia nada más del archivo.
  - `tests/test_services.py`: se añade una sección al final con un banner `# === A9: ... ===`, los imports
    `from datetime import UTC, datetime` y `from decimal import Decimal` (el hook los ordena), las constantes
    `LIST_RESPONSE_KEYS` (8 claves) y `DETAIL_RESPONSE_KEYS` (10) y un helper `async def _persist_package(db_session,
    **overrides) -> TouristService`. El helper siembra vía ORM con defaults válidos (`name="Paquete De Prueba
    Automatizada"`, `base_price=Decimal("50000.00")`, `max_capacity=15`, `category=ServiceCategory.agroturismo`,
    `is_available=True`), hace commit y refresh. Se reutilizan las fixtures existentes `admin_headers`
    (l.402) y `storage_double` (l.389), y los helpers `_create_payload`, `TEMP_URL`, `PERMANENT_URL` y
    `_assert_nothing_persisted`.
- **Tests (RED primero):**
  1. `test_public_catalog_returns_stored_package_verbatim`, parametrizado con `(campo, valor)`: `name="Tour corto"`,
     `name="Paquete " + "a" * 70`, `base_price=Decimal("1000.00")`, `max_capacity=50`, `description="d" * 1001` y
     `name="Ruta Cafetera DeLaCruz"`. `GET /servicios/` sin autenticación responde `200`, con un elemento cuyas
     claves son `LIST_RESPONSE_KEYS`. El valor se compara así: `Decimal(item["base_price"]) == valor` para el precio y
     `item[campo] == valor` para el resto.
  2. `test_public_catalog_survives_one_off_rule_package`: dos paquetes válidos y uno con `name="Tour corto"`, los tres
     activos. Responde `200`, con 3 elementos, y el conjunto de `id` es igual al sembrado.
  3. `test_inactive_column_returns_off_rule_package`: un paquete con `is_available=False` y `max_capacity=50`.
     `GET /servicios/admin/inactivos` con `admin_headers` responde `200`, con un elemento y `max_capacity == 50`.
  4. `test_deleted_column_returns_off_rule_package`: un paquete con `deleted_at=datetime.now(UTC)` y
     `base_price=Decimal("1000.00")`. `GET /servicios/admin/eliminados` responde `200`, con un elemento, claves
     `DETAIL_RESPONSE_KEYS`, `Decimal(item["base_price"]) == Decimal("1000.00")` y `item["deleted_at"] is not None`.
  5. `test_update_on_off_rule_package_returns_200_with_persisted_change`: un paquete con `name="Tour corto"` recibe
     `PUT /servicios/{id}` con `{"max_capacity": 10}`. Responde `200`, con `body["name"] == "Tour corto"` y
     `body["max_capacity"] == 10`. Tras `refresh`, la BD tiene el aforo 10 y el nombre intacto.
  6. `test_create_still_rejects_short_name`: `POST /servicios/` con `_create_payload([TEMP_URL])` y `name="Tour
     corto"`. Responde `422` y `[e["raw_field"] for e in body["detalle"]] == ["name"]`; `_assert_nothing_persisted`
     pasa; `storage_double.promote_to_permanent.assert_not_awaited()`.
  7. `test_update_still_rejects_capacity_over_limit`: un paquete válido recibe `PUT` con `{"max_capacity": 50}`.
     Responde `422`, `raw_field == "max_capacity"`, y la BD conserva el aforo 15.
  8. `test_create_still_title_cases_name`: con `storage_double.promote_to_permanent.return_value = PERMANENT_URL`,
     `POST /servicios/` con `_create_payload([TEMP_URL])` y `name="ruta cafetera del magdalena"`. Responde `201` con
     `body["name"] == "Ruta Cafetera Del Magdalena"`, igual en la BD, y
     `promote_to_permanent.assert_awaited_once_with(TEMP_URL)`.

  RED esperado sobre B1: fallan los 6 casos de 1. Cinco lanzan `ResponseValidationError` y `DeLaCruz` falla por
  aserción (sale `"Ruta Cafetera Delacruz"`). También fallan 2, 3, 4 y 5. 6, 7 y 8 están verdes hoy y siguen verdes
  (congelan la entrada). Son 8 funciones y 13 casos.
- **Criterio de aceptación:**
  - `venv/Scripts/python.exe -m pytest tests/test_services.py -q` → pasan los de antes más 13. Suite completa:
    347 + 13 = 360 passed, 0 failed.
  - `ruff check app/schemas/service.py tests/test_services.py` → 0 errores (tolerado solo I001). `ruff format --check`
    → OK. Total ≤ 82, o ≤ 84 si quedan los dos I001.
  - mypy: ninguna línea de `app/schemas/service.py`; total ≤ 44. Compuerta: import-linter 4 KEPT, docs ✔ y cobertura
    ≥ 92.76 %.
  - Introspección y `diff openapi-1 openapi-2`: lo mismo que en A, para `ServiceListResponse` y `ServiceDetailResponse`.
  - `grep -n "default=\[\]" app/schemas/service.py` → sigue en l.54 (S7 intacto).
  - Mutaciones para el auditor: M1, volver a `(ServiceBase)` en las dos clases → fallan 1-5. M2, solo
    `ServiceListResponse` vuelve a `(ServiceBase)` → fallan 1, 2 y 3, pero no 4 ni 5. M3, quitar
    `format_service_name` de `ServiceBase` → falla 8.
- **Fuera de alcance de esta fase:** `ServiceBase`, `ServiceCreate` y `ServiceUpdate` (reglas y S7);
  `ServiceImageResponse` y `ServiceImageOutput`; los fixtures legados de `tests/test_services.py` (`admin_token`,
  `test_package`); los routers; los usuarios.
- **Commit B1:**
  ```
  style(schemas): clear ruff findings in service schemas before A9

  app/schemas/service.py carried 4 ruff findings (I001, D205 and D415
  on one docstring, one E501). A9 edits this file and ADR-0005 requires
  a touched file to end with zero findings, so the cleanup lands first
  and the A9 fix that follows stays a pure behavior diff.

  - The format_service_name docstring gets a summary line ending in a
    period plus body; content unchanged.
  - The long image_urls description is split with implicit string
    concatenation; the text and the OpenAPI document are identical.
    Its default=[] is left as is on purpose (backlog S7).
  - I001 is the edit hook's autofix, bisected as harmless for this
    file (journal, 2 Nov).

  No behavior change: the test suite result is identical.
  ```
- **Commit B2:**
  ```
  fix(schemas): stop package responses from inheriting input validation

  ServiceListResponse and ServiceDetailResponse extended ServiceBase,
  the package form DTO, so every response was validated against the
  form rules (name length 20-65, price floor 40000, capacity cap 30,
  description length) and re-ran the title-case validator. One stored
  package outside those rules (manual load, or a floor or cap changed
  later) made the public catalog GET /servicios/ answer 500 for every
  visitor, and PUT /servicios/{id} committed the change and still
  answered 500 (backlog A9, same cause as UserResponse).

  - app/schemas/service.py: both responses now extend BaseModel and
    declare the same fields, order, defaults and from_attributes with
    plain types and no validators, so they describe what is stored.
    ServiceBase, ServiceCreate and ServiceUpdate keep every rule.
  - tests/test_services.py: off-rule stored packages (short and long
    name, price below the floor, capacity over the cap, long
    description, mixed-case name) come back verbatim from the public
    catalog; one off-rule package does not take it down; the inactive
    and deleted columns and PUT answer 200; create and update still
    reject off-rule input with 422 and create still title-cases.

  The OpenAPI components of both responses lose the input constraints
  and field descriptions; names and types are unchanged.
  ```

## Verificación final

```bash
# 1. Ningún DTO de salida hereda de una base de entrada (esperado: solo AuditLogResponse(AuditLogBase), sin reglas)
grep -rnE "class \w+Response\(\w+Base\)" app/schemas/
# 2. Las tres clases sobre BaseModel (esperado: 3 líneas, todas "(BaseModel)")
grep -nE "class (UserResponse|ServiceListResponse|ServiceDetailResponse)\(" app/schemas/
# 3. Endpoints consumidores sin cambio (esperado: 11, routers sin diff en A9)
grep -rnE "response_model=(list\[)?(UserResponse|ServiceListResponse|ServiceDetailResponse)" app/api/routers/
git diff 7c6d606 --stat -- app/api/routers/ app/main.py app/models/ alembic/   # esperado: vacío
# 4. Sin reglas ni validadores en la salida (esperado: 3 líneas "BaseModel {} {} <class 'str'|None>")
venv/Scripts/python.exe -c "from app.schemas.user import UserResponse as U; from app.schemas.service import ServiceListResponse as L, ServiceDetailResponse as D; [print(m.__name__, m.__mro__[1].__name__, {n: f.metadata for n, f in m.model_fields.items() if f.metadata}, m.__pydantic_decorators__.field_validators, getattr(m.model_fields.get('email'), 'annotation', None)) for m in (U, L, D)]"
# 4b. Las reglas de entrada siguen (esperado: mismo recuento que en 7c6d606)
grep -cE "pattern=|min_length=|max_length=|ge=|le=|gt=|EmailStr" app/schemas/user.py app/schemas/service.py
git show 7c6d606:app/schemas/user.py | grep -cE "pattern=|min_length=|max_length=|ge=|le=|gt=|EmailStr"
git show 7c6d606:app/schemas/service.py | grep -cE "pattern=|min_length=|max_length=|ge=|le=|gt=|EmailStr"
# 5. Contexto, no forma parte del arreglo (esperado: vacío, sin handler nuevo)
grep -rn "ResponseValidation" app/
# 6. Tests que reproducen el defecto (esperado: resultados en test_user_response.py y test_services.py)
grep -rnE "Jean-Luc|O'Brien|Tour corto|DeLaCruz" tests/
# 7. S7 intacto (esperado: 1 línea en app/schemas/service.py)
grep -n "default=\[\]" app/schemas/service.py
# 8. Trinquete (ADR-0005) y compuerta (línea base: ruff ✘ 97 · mypy ✘ 44 · 4 KEPT · 333 passed · 92.76 %)
venv/Scripts/python.exe -m ruff check app/schemas/user.py app/schemas/service.py tests/test_user_response.py tests/test_services.py
venv/Scripts/python.exe -m ruff check . | tail -1        # esperado: Found 82 errors (≤ 84 si quedan I001)
venv/Scripts/python.exe -m mypy | grep -E "app[\\/]schemas|^Found"   # esperado: solo "Found 44 errors"
venv/Scripts/python.exe -m pytest tests/test_user_response.py tests/test_services.py -q
venv/Scripts/python.exe scripts/check.py                 # esperado: 360 passed, cobertura ≥ 92.76 %
```

Nota sobre `4b`: los recuentos deben salir idénticos a los de `7c6d606`. Las clases `*Response` nunca tuvieron reglas
propias (las heredaban), y el commit `style` solo reparte cadenas, sin mover ningún argumento de `Field`. Si un recuento
difiere, el auditor revisa `git diff 7c6d606 -- app/schemas/` y confirma que no ha desaparecido ninguna regla de las
clases de entrada.

## Residuales

- **Patrón de nombres sin guion ni apóstrofo** (`app/schemas/user.py:35,42,129,135`). Es una regla de negocio y no
  forma parte de A9 (adenda, punto 2). "Jean-Luc" es solo semilla de test. Fila sugerida para `docs/backlog.md` §A:
  `| A9-R | Patrón de nombres rechaza guion y apóstrofo ("Jean-Luc", "O'Brien") en UserBase/UserUpdate | **4** patrones | Media | XS | **Sale → \`B-FUTURO\`** |`
- **Sin handler para `ResponseValidationError`** (`grep ResponseValidation app/` vacío). Tras A9 ya no hay DTO de
  salida con reglas, pero un desajuste futuro de tipos seguiría siendo un 500 sin log estructurado. No se añade
  porque taparía el síntoma. Destino sugerido: nota en la fila de observabilidad, o `B-FUTURO`.
- **La regla "un DTO de salida no hereda de uno de entrada" no es determinista.** Hoy la vigilan los tests de A9 y el
  grep 1. Si David quiere que valga para los DTO futuros (reservas, pagos), el sitio es una línea en AGENTS §3, en un
  PR humano. Otra opción, más cara, es un test que recorra los `*Response` de `app/schemas/` y falle si alguno tiene
  `metadata` o validadores. Ninguna de las dos va en este plan.
- **S7 sigue vivo** en `app/schemas/service.py:53-54` (`Field(` / `default=[]`, en dos líneas). Ya está en la fe de
  erratas de la bitácora del 2 nov. El cierre no debe marcarlo `Hecho`. B no lo toca.
- **S6:** el dict `model_config = {"from_attributes": True}` sigue en `UserResponse` (la métrica del backlog sigue en
  **1**).
- **D2:** el `# noqa: UP042` de `app/schemas/user.py:6` desaparece cuando D2 unifique `UserRole`. Hay que anotarlo en la
  Nota técnica de D2.
- **Esquema de BD más laxo que los formularios** (`app/models/user.py:34-39`, `app/models/service.py:19-23`, sin CHECK).
  Es S1/ADR-0002. A9 hace que la lectura tolere esa diferencia. No la cierra.

## Referencias

- **Context7:** las herramientas de Context7 no estaban disponibles en esta sesión. Las dos dudas de API (cómo valida
  FastAPI `response_model` y qué hace `EmailStr` en la salida) se resolvieron leyendo el código **instalado** en el
  `venv`, que es la fuente exacta para la versión en uso (lección 17 de la bitácora del 2 nov):
  `fastapi/routing.py:273-306` (`serialize_response` → `field.validate` → `ResponseValidationError`) y
  `pydantic/networks.py:1318-1328` (`validate_email` devuelve `parts.normalized`). Se confirmaron con dos sondeos en el
  scratchpad: los 500 y la reescritura de hoy, y el JSON idéntico de las clases planas.
- FastAPI · 0.135.1 · Response Model (la salida se valida y filtra con `response_model`) ·
  https://fastapi.tiangolo.com/tutorial/response-model/
- FastAPI · 0.135.1 · Extra Models (modelos de entrada y salida separados: `UserIn`/`UserOut`) ·
  https://fastapi.tiangolo.com/tutorial/extra-models/
- FastAPI · 0.135.1 · Separate OpenAPI Schemas for Input and Output (por qué cambian solo los componentes de salida) ·
  https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/
- Pydantic · 2.12.5 · `from_attributes` · https://docs.pydantic.dev/2.12/concepts/models/#arbitrary-class-instances
- Pydantic · 2.12.5 · los validadores se heredan con la clase · https://docs.pydantic.dev/2.12/concepts/validators/
- Pydantic · 2.12.5 · `EmailStr` (normaliza con email-validator 2.3.0) ·
  https://docs.pydantic.dev/2.12/api/networks/#pydantic.networks.EmailStr
- httpx · 0.28.1 · `ASGITransport(raise_app_exceptions=True)` por defecto (forma del RED) ·
  https://www.python-httpx.org/advanced/transports/#asgitransport

**ADR propuesto: ninguno.** Separar los modelos de entrada y de salida es la práctica que documenta el propio FastAPI
(Extra Models). No rompe ningún principio del proyecto ni introduce módulo, patrón o contrato HTTP nuevo: el JSON no
cambia, y el OpenAPI solo pierde restricciones que nunca debieron estar en la salida. La decisión ya está registrada
con autor y fecha (adenda, punto 3) y cada clase la explica en su docstring. Las dos elecciones locales (clases planas
frente a una base compartida, y `noqa` frente a `StrEnum`) están justificadas en este plan y se pueden revertir sin
coste. Si David quiere que la regla obligue a los DTO futuros, el sitio es AGENTS §3, no un ADR (ver Residuales).

## Retoques aprobados antes de `/implementar` (David + sesión Mentor, 2 nov, 17:25)

1. **Seis campos repetidos entre `ServiceListResponse` y `ServiceDetailResponse`: aceptado, con otra justificación.** El
   motivo no es que el patrón de detección marcaría una base compartida (un grep no diseña código; una
   `ServiceOutputFields(BaseModel)` sin reglas no tendría el defecto). El motivo es que lista y detalle difieren a
   propósito (`created_at`, `deleted_at`) y las dos clases viven adyacentes en el mismo archivo. Regla que gobierna la
   duplicación: **regla de tres** — la tercera clase de respuesta de paquete que aparezca obliga a extraer la base.
2. **`# noqa: UP042 (backlog D2)`: aceptado.** Convertir a `StrEnum` cambia `str()` de un enum que llega al ORM; es D2.
   La retirada del `noqa` se anota en la fila D2 del backlog en el cierre (misma regla que I001 en A4).
Lo demás del plan se ejecuta tal cual.

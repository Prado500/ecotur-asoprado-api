# PLAN — BE-37: Rechazar con 422 el `null` explícito sobre columnas NOT NULL en `UserUpdate` y `ServiceUpdate`

> Fuente: `docs/deuda/BE-37/verificacion.md` (confirmada; adenda de David, 17 nov 2026, 12:09, con siete decisiones
> dadas). Base: `32b8fd4` (HEAD de `item/be-37`; `app/`, `tests/`, `conftest.py` y `pyproject.toml` idénticos a
> `c3b5069`, la línea base de la verificación: 731 passed, 97,65 %, ruff 0, mypy 0 en 63 archivos, 4 kept).
> **Estado: aprobado por David con E0 (17 nov 2026, 15:16); ninguna fase ejecutada.** `Aprobado: 17 nov 2026`:
> `<FECHA>` = `17 nov 2026` y `<AAAA-MM-DD>` = `2026-11-17` (ADR-0020 y addendum de ADR-0018). Enmiendas al final, en
> "Enmiendas aprobadas".
> **Qué midió el redactor** (todo en copias `git archive 32b8fd4` del scratchpad, nunca en el repo; `git status` del
> repo sin cambios propios fuera de `docs/deuda/BE-37/`): (1) sondas HTTP antes y después, incluido el encargo del
> superadmin sobre otro superadmin con `{"is_active": null}` y el orden guard → 422; (2) el cuerpo real del 422 con tres
> mecanismos candidatos; (3) RED de cada fase (copia con solo los tests); (4) GREEN de cada fase con `scripts/check.py`
> completo; (5) 17 mutantes, suite completa cada uno; (6) los conteos de la Verificación final, con `grep` sobre la
> copia final; (7) el ancho de cada línea dictada, con el intérprete y con `ruff`. Si una cifra no cuadra, el ejecutor
> se detiene y lo anota en el handoff, sin "arreglar" código para que cuadre.

## Resumen para aprobación

Tres fases. (A) Escribe ADR-0020 (en un DTO de actualización, `null` explícito solo donde la columna admite vacío) y un
addendum de ADR-0018 (el `null` de un superadmin sobre otro pasa de 403 a 422; la decisión no cambia). (B) Crea
`app/schemas/partial_update.py` con un marcador `NoExplicitNull` (un `BeforeValidator` de Pydantic que rechaza `None`) y
lo pone en la anotación de `email`, `first_name`, `last_name`, `role` e `is_active` de `UserUpdate`; invierte el test
que congelaba `email=None` y añade 15 casos (731 → 746). (C) Pone el mismo marcador en `name`, `category`, `base_price`,
`max_capacity` e `is_available` de `ServiceUpdate` y añade 11 casos (746 → 757), incluido que el 422 llega antes de
cualquier llamada al CDN. Todo medido en copia: compuerta verde, 757 passed, cobertura 98,49 %.
**Riesgo principal:** contrato. Diez peticiones pasan de 409 a 422 y cuatro rechazos de la política pasan de 403 a 422
(aceptado en la adenda, decisión 3; el cuarto es el del addendum). Un cliente que mande hoy `null` en esos campos recibe
otro código; el cliente Flutter no se mira desde aquí.
**No se toca:** la política de acceso, los servicios, los routers, `app/main.py` (handlers de 422 y de
`IntegrityError`), `phone`, `description`, `image_urls`, los DTO de salida, `tests/test_route_guards.py`, `AGENTS.md`
(la viñeta la edita David tras la última auditoría y antes de `/pr`), BE-26, BE-38, BE-59, A3.

**Decisiones que la adenda deja a David y que quedan pendientes al aprobar el plan:**

1. **Texto del 422 (adenda, decisión 6) — pendiente. Recomendado: opción (a) con el texto
   `"Este campo no puede quedar vacío. Omítalo si no desea modificarlo."`** Cuerpos medidos (copia con las fases B y C,
   `PATCH` de superadmin sobre admin y `PUT` de admin; un campo por petición):

   | Campo | (a) `ValueError(<texto>)` — **dictada** | (b) `PydanticCustomError("null_not_allowed", …)` |
   |---|---|---|
   | `email` | `El correo electrónico ingresado no tiene un formato válido.` | `Error en 'correo electrónico': Revisar el formato ingresado.` |
   | `first_name` | `<texto>` | `Error en 'nombres': Revisar el formato ingresado.` |
   | `last_name` | `<texto>` | `Error en 'apellidos': Revisar el formato ingresado.` |
   | `role` | `<texto>` | `Error en 'role': Revisar el formato ingresado.` |
   | `is_active` | `<texto>` | `Error en 'is_active': Revisar el formato ingresado.` |
   | `name` | `<texto>` | `Error en 'nombre del paquete': Revisar el formato ingresado.` |
   | `category` | `<texto>` | `Error en 'category': Revisar el formato ingresado.` |
   | `base_price` | `<texto>` | `Error en 'precio base': Revisar el formato ingresado.` |
   | `max_capacity` | `<texto>` | `Error en 'capacidad máxima': Revisar el formato ingresado.` |
   | `is_available` | `<texto>` | `Error en 'is_available': Revisar el formato ingresado.` |

   Forma común: `{"detalle": [{"raw_field": "<campo>", "message": "<texto>"}]}`, un elemento por campo nulo (con
   `{"role": null, "is_active": null, "first_name": "Nuevo"}`, dos elementos, `role` e `is_active`). Por qué difieren:
   el handler (`app/main.py:77-84`) muestra el texto del validador si el error es `value_error`, salvo en `email`, que
   tiene su propia rama; cualquier otro tipo cae en el texto genérico, con el nombre del campo traducido si está en
   `field_dict` (`role`, `is_active`, `category` e `is_available` no lo están). La opción (c), quitar `| None` de la
   anotación, da exactamente los cuerpos de (b) (`string_type`, `enum`, `bool_type`…), pero mypy da 10 errores: queda
   descartada por la adenda. Si David elige (b), enmienda de dos líneas en `partial_update.py` (import y `raise`); si
   elige (a) con otro texto, cambia solo `_NULL_MESSAGE` (una línea; si pasa de 79 caracteres, entre paréntesis en dos
   literales). Los tests no afirman sobre el texto en ninguna opción.
2. **Textos de ADR-0020 y del addendum de ADR-0018 — pendiente. Recomendado: los de la fase A.**
3. **Alcance de los tests — pendiente. Recomendado: los 27 casos dictados** (16 en B, 11 en C). Sin test por campo de
   "texto del mensaje" ni gemelo unitario de cada caso HTTP: el unitario de la fase B que queda es el del correo
   (invertido por la adenda) más dos bordes (ausente ≠ `null`; dos `null` dan dos errores).

## Objetivo y decisiones bloqueadas

Que un `null` explícito sobre un campo cuya columna es NOT NULL se rechace en la frontera, con 422, sin mutación, sin
auditoría y sin CDN, en los dos DTO de actualización; y que el `null` legítimo (`phone`, `description`) siga borrando.

1. Alcance: `UserUpdate` y `ServiceUpdate`, `ServiceUpdate` en fase propia (adenda, decisión 1).
2. Campos que rechazan `null`: `email`, `first_name`, `last_name`, `role`, `is_active`; `name`, `category`,
   `base_price`, `max_capacity`, `is_available` (decisión 3). Rechazo en el schema, 422.
3. `phone` y `description` no cambian: `null` borra y da 200. Prohibido `exclude_none=True` o cualquier mecanismo que
   vuelva no-op ese `null` (decisión 4).
4. `image_urls: null` no se toca: sigue dando 200 sin cambiar imágenes (decisión 5). Su fila de auditoría es BE-38.
5. Se acepta que cuatro rechazos de la política pasen de 403 a 422 (decisión 3 y encargo del superadmin par).
6. Los guards de ruta siguen antes del 422: 401 sin token en las dos rutas; 403 a un turista en `PUT /servicios/{id}`.
7. Un solo mecanismo para los dos DTO; ningún DTO de salida lo lleva (A9); la anotación no miente a mypy.
8. La política de acceso, los servicios, los routers y `app/main.py` no cambian. M6 deja de ser alcanzable por HTTP y
   los unitarios de la política con `None` se quedan.
9. ADR-0020 corto antes del código que lo cita; ADR-0018 recibe un addendum (ADR-0009: aclara el cómo); la viñeta de
   AGENTS §3 la escribe David después de la última auditoría.

## Análisis del redactor

**Contraste con el código (`32b8fd4`).** Todo lo que la verificación cita sigue en su sitio: `app/schemas/user.py:166`
(`email`), `:167-172`, `:173-178`, `:179` (`phone`), `:180` (`role`), `:181` (`is_active`), `:183-190` (validador que
deja pasar `None` en `:187-188`); `app/schemas/service.py:107-122` (`ServiceUpdate`, sin docstring; su validador deja
pasar `None` en `:119-120`); `app/services/user_service.py:284` y `:287`;
`app/services/tourist_services_service.py:282`, `:287` y `:337`; `app/services/user_access_policy.py:97`, `:102`, `:105`
y `:114`; `app/main.py:31-97` (handler del 422) y `:100-114` (handler del 409); `tests/test_email_case.py:116-121`.

**Encargo 1 — superadmin sobre otro superadmin con `{"is_active": null}` (medido).** Antes: **403** (la guarda de
jerarquía, `user_access_policy.py:88-95`, porque `is_peer_reactivation` exige `is True`), `is_active` sigue `True`, 0
filas de auditoría. Después: **422** `{"detalle": [{"raw_field": "is_active", …}]}`, `is_active` sigue `True`, 0 filas.
ADR-0018 escribe en su decisión 1 que `null` "sigue dando 403": la fase A le añade un addendum (aclara el cómo; la
decisión, "`null` no reactiva", no cambia; ADR-0009, punto 2). Es el cuarto caso 403 → 422, junto a los tres de la
adenda; los cuatro están en el mismo test parametrizado de la fase B.

**Encargo 2 — mecanismo.** Elegido: un marcador `NoExplicitNull = BeforeValidator(_reject_explicit_null)` en un módulo
nuevo, `app/schemas/partial_update.py`, que se escribe en la anotación de cada campo:
`role: Annotated[UserRole | None, NoExplicitNull] = None`. Por qué así:

- **La anotación no miente:** conserva `| None`, porque un campo ausente vale `None` en el modelo; el validador `before`
  solo corre cuando el campo llega en el cuerpo (Pydantic no valida el valor por defecto), así que rechaza el `null`
  enviado y no el ausente. mypy: 0 errores en 65 archivos (medido). Quitar `| None` daría 10 errores (medido, opción c).
- **Un solo sitio para la regla y para el texto**, compartido por los dos DTO, y la regla al lado del campo que la
  lleva, como `LowercaseEmail` (ADR-0016) en el mismo archivo. Un `field_validator(…, mode="before")` por DTO con la
  lista de campos se comporta igual (sonda de la sesión Mentor y la mía), pero repite el validador y separa la lista de
  los campos.
- **Las restricciones siguen funcionando:** `min_length`, `pattern`, `ge`, `max_digits`, `gt`, `le` del `Field` se
  aplican igual sobre `Annotated[T | None, NoExplicitNull]` (medido: `"A"` en `first_name` sigue dando
  `string_too_short`; la suite entera, con `test_update_still_rejects_capacity_over_limit` y
  `test_patch_still_rejects_hyphenated_name`, en verde).
- **A9:** el marcador vive en `app/schemas/` y solo lo importan `user.py` y `service.py` para sus DTO de actualización;
  `UserResponse`, `ServiceListResponse` y `ServiceDetailResponse` no cambian (comando 2 de la Verificación final).
- **Import-linter:** `app.schemas` sigue sin importar capas superiores (4 kept, medido).

Consecuencia de limpieza (mismas líneas): los validadores `format_title_case` (`user.py:183-190`) y
`format_service_name` (`service.py:116-122`) ya no pueden recibir `None`; su rama `if v is None: return v` queda muerta
y se quita, con la firma `str -> str`. Era la línea sin cubrir `user.py:188` (rincón 8 de la verificación) y su gemela
`service.py:120`. `format_service_name` recibe la docstring que no tenía (AGENTS §4: función refactorizada).

**Encargo 3 — guards antes del 422 (medido y congelado).** FastAPI resuelve las dependencias (los guards) antes de
validar el cuerpo. Antes y después: `PATCH /usuarios/{cédula}` con `{"role": null}` sin token → 401;
`PUT /servicios/{id}` con `{"name": null}` sin token → 401 y con token de turista → 403. Ningún test lo congelaba
(`tests/test_route_guards.py` usa `{}` a propósito, l.36): lo congelan
`test_be37_missing_token_is_rejected_before_the_null` (B) y `test_be37_package_guard_answers_before_the_null` ×2 (C).

**Cuerpo del 422.** Lo arma el handler de `app/main.py:31-97`, que no se toca; los tests afirman sobre `detalle`,
`raw_field` y que `message` es `str`, nunca sobre el texto. Con la opción (a) la suite cubre además `app/main.py:61`,
`:79` y `:82` (antes sin cubrir).

**Tabla de mutantes** (copia con las fases B y C; suite completa por mutante; salida literal en "Mediciones"):

| Id | Archivo | Mutación | Suite | Lo matan |
|---|---|---|---|---|
| MU-email | `user.py` | quitar el marcador de `email` | 2 failed | test invertido del correo; H1[`superadmin-on-admin-email`] |
| MU-first_name | `user.py` | ídem `first_name` | 1 failed | H1[`…-first_name`] |
| MU-last_name | `user.py` | ídem `last_name` | 1 failed | H1[`…-last_name`] |
| MU-role | `user.py` | ídem `role` | 5 failed | U2, H1 ×3 (`role` sobre admin, sobre sí mismo, admin sobre turista), H2 |
| MU-is_active | `user.py` | ídem `is_active` | 4 failed | U2, H1 ×3 (sobre admin, turista sobre sí mismo, superadmin par) |
| MU-phone+ | `user.py` | poner el marcador en `phone` | 2 failed | H3 ×2 |
| MX-exclude_none | `user_service.py` | `exclude_none=True` en el `model_dump` (la alternativa descartada) | 2 failed | H3 ×2 |
| MF-falsy | `partial_update.py` | `if not value:` en vez de `if value is None:` | 10 failed | los que envían `is_active: false`: `test_auth.py` 1, be35 5, be36 1, be58 3 |
| MA-after | `partial_update.py` | `AfterValidator` en vez de `BeforeValidator` | **757 passed (vive)** | ninguno: equivalente (con `T \| None` el `None` pasa la unión y el validador posterior lo rechaza igual) |
| MS-name | `service.py` | quitar el marcador de `name` | 3 failed | S1[`name`], S2 ×2 |
| MS-category | `service.py` | ídem `category` | 1 failed | S1[`category`] |
| MS-base_price | `service.py` | ídem `base_price` | 1 failed | S1[`base_price`] |
| MS-max_capacity | `service.py` | ídem `max_capacity` | 1 failed | S1[`max_capacity`] |
| MS-is_available | `service.py` | ídem `is_available` | 1 failed | S1[`is_available`] |
| MS-description+ | `service.py` | poner el marcador en `description` | 1 failed | S3 |
| MS-image_urls+ | `service.py` | poner el marcador en `image_urls` | 1 failed | S4 |
| M6 | `user_access_policy.py` | `not update_dict.get("is_active", True)` | **757 passed (vive)** | ninguno, a propósito: por HTTP ya no llega `None` y la política no se toca (adenda) |

Ids de los tests (Anexo): U1 `test_be37_absent_fields_stay_unset`, U2 `test_be37_every_null_field_is_reported`, H1
`test_be37_null_on_not_null_field_returns_422_without_mutation` (×9), H2
`test_be37_null_beside_a_valid_field_changes_nothing`, H3 `test_be37_null_on_phone_still_clears_it` (×2), H4
`test_be37_missing_token_is_rejected_before_the_null`; S1
`test_be37_null_on_not_null_package_field_returns_422_without_side_effects` (×5), S2
`test_be37_null_beside_new_images_touches_no_blob` (×2), S3 `test_be37_null_on_description_still_clears_it`, S4
`test_be37_null_on_image_urls_still_keeps_the_images`, S5 `test_be37_package_guard_answers_before_the_null` (×2).

**Orden y dependencias.** A (2 archivos de `docs/adr/`) primero: el código y los tests de B y C citan ADR-0020. B crea
el marcador; C lo importa, así que C depende de B. B y C no comparten archivos. Regla, docstrings y tests de cada DTO
van en un commit, como en BE-35, BE-36 y BE-58.

**Tests que congelan comportamiento relacionado** (todos en verde con las fases B y C; medido con la suite completa):
`tests/test_user_response.py:181` (PATCH con nombre inválido → 422), `tests/test_services.py:739` (capacidad > 30 →
422), `:707` (PUT sobre paquete fuera de regla → 200), los de `is_active: false` de BE-35/BE-36/BE-58 y
`tests/test_auth.py` (los que MF-falsy hace caer), `tests/test_email_case.py:97-108` (el correo de `UserUpdate` llega en
minúsculas) y los unitarios de la política con `None` (`tests/test_user_access_policy.py:186-190` y `:287`), que se
quedan. `tests/test_user_service.py:171` construye `UserUpdate(first_name="Hacked")`: sin cambio.

**Riesgos.** (a) Contrato 409/403 → 422 (Resumen). (b) Texto del 422 (decisión pendiente 1). (c) MA-after sobrevive y es
equivalente (tabla); se dicta `BeforeValidator` porque dice que la regla mira el dato crudo, antes del tipo. (d) M6
sobrevive a propósito: la política no se toca y por HTTP ya no le llega `None` (adenda). (e) Los avisos de la
suite suben de 8 a 25: cada 422 que pasa por el handler emite el aviso de `HTTP_422_UNPROCESSABLE_ENTITY` deprecado (S5
del backlog; residual R2). (f) El OpenAPI sigue anunciando `null` en los diez campos (residual R1).

**Qué NO se toca.** `app/services/` (incluida la política), `app/api/`, `app/main.py`, `app/models/`,
`app/repositories/`, `app/core/`, `alembic/`, los DTO de salida y `UserBase`/`ServiceBase`/`ServiceCreate`,
`tests/test_user_access_policy.py`, `tests/test_route_guards.py`, `tests/conftest.py`, `conftest.py`, ADR-0017,
ADR-0019, `AGENTS.md`, `docs/CONTEXT.md`, `docs/backlog.md`.

## Regla de alcance

**Sí:** ADR-0020; addendum de ADR-0018; `app/schemas/partial_update.py` (nuevo); el marcador en los diez campos; la
docstring de los dos DTO de actualización; la rama muerta y la firma de sus dos validadores (y la docstring de
`format_service_name`); el test invertido de `tests/test_email_case.py`; `tests/test_user_update_null.py` (nuevo); la
sección be37 al final de `tests/test_services.py`.
**No:** la política (ADR-0017/0018/0019) y el mutante M6; el handler de `IntegrityError` y el del 422; el orden del CDN
(BE-26); la auditoría de no-ops y `image_urls: null` (BE-38); la lista vacía de imágenes (BE-59); `commit()` en
repositorios (A3); el OpenAPI (R1); el cliente Flutter; `AGENTS.md`, `docs/CONTEXT.md`, `docs/backlog.md` (cierre).

## Fases

| Fase | Qué | Archivos | Suite tras la fase | Commit |
|---|---|---|---|---|
| A | ADR-0020 y addendum de ADR-0018 | 2 (`docs/adr/`) | 731 passed · 97,65 % (sin código) | — |
| B | Marcador y `UserUpdate`; test del correo invertido; 15 casos | 4 | 746 passed · 98,33 % (medido) | — |
| C | `ServiceUpdate`; 11 casos | 2 | 757 passed · 98,49 % (medido) | — |

### Fase A — ADR-0020 y addendum de ADR-0018 (la más pequeña)

- **Archivos (2):** `docs/adr/0020-null-explicito-solo-donde-la-columna-admite-vacio.md` (nuevo) y
  `docs/adr/0018-un-superadmin-reactiva-a-otro.md` (solo se añade el addendum al final). Dominio: decisiones (docs).
- **Cambios exactos:** el texto del Anexo A, tal cual, sin las líneas de la valla. ADR-0020: 63 líneas (la más
  larga, 120 columnas). Addendum: 9 líneas, una en blanco y luego el encabezado, pegadas tras la última línea de
  ADR-0018 (que acaba en salto de línea). `<FECHA>` (formato `17 nov 2026`) y `<AAAA-MM-DD>` se sustituyen por los de la
  aprobación; nada más cambia en ADR-0018.
- **Tests (RED primero):** no aplica (solo documentación). Comprobación sustituta:
  `./venv/Scripts/python.exe scripts/check.py --no-tests` en verde (`check_docs` no escanea `docs/adr`,
  `scripts/check_docs.py:157`).
- **Criterio de aceptación:** `git diff --numstat 32b8fd4 HEAD -- docs/adr` = `63 0` para el 0020 y `9 0` para el 0018,
  y nada más; ningún `<FECHA>` ni `<AAAA-MM-DD>` en `docs/adr` (`git grep -n "<FECHA>\|<AAAA-MM-DD>" -- docs/adr` sin
  salida); compuerta completa en verde con 731 passed.
- **Fuera de alcance de esta fase:** `app/`, `tests/`; ADR-0017 y ADR-0019; cualquier línea previa de ADR-0018;
  `AGENTS.md`, `docs/CONTEXT.md`, `docs/backlog.md`, la bitácora.
- **Commit:**
  ```
  docs(adr): add ADR-0020, explicit null only where the column admits it

  A PATCH /usuarios or PUT /servicios body with null on a NOT NULL
  column reached the database and came back as a 409 that speaks of a
  record that already exists (BE-37, measured on ten fields). Any
  valid field sent beside it was lost, and on packages the 409 arrived
  after the CDN had deleted or promoted blobs, leaving a broken image.

  The ADR records David's rule before the code that cites it lands: in
  an update DTO an explicit null is accepted only where the column
  admits empty, so phone and description keep clearing with null and
  every other field rejects it at the schema with a 422. One marker on
  the field annotation keeps "| None", because an absent field is None
  on the model, and no output DTO carries it (A9).

  ADR-0018 gets an addendum: a superadmin sending is_active null to a
  peer now gets 422 from the schema instead of 403 from the policy.
  Null still never reactivates, so the decision does not change; only
  how it is enforced does (ADR-0009).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — El marcador y `UserUpdate`

- **Archivos (4):** `app/schemas/partial_update.py` (nuevo), `app/schemas/user.py`, `tests/test_user_update_null.py`
  (nuevo), `tests/test_email_case.py`. Dominio: actualización de cuentas de usuario (frontera de entrada).
  `git diff --numstat` esperado: `38 0`, `13 9`, `149 0`, `6 5` (medido en la copia).
- **Cambios exactos** (texto literal en el Anexo B):
  - `app/schemas/partial_update.py`: módulo nuevo con `_NULL_MESSAGE` (texto de la decisión pendiente 1),
    `_reject_explicit_null(value: Any) -> Any` (docstring Google; lanza `ValueError(_NULL_MESSAGE)` si `value is None`)
    y `NoExplicitNull = BeforeValidator(_reject_explicit_null)`.
  - `app/schemas/user.py`: `from app.schemas.partial_update import NoExplicitNull` (bloque propio tras el de pydantic);
    docstring de `UserUpdate` ampliada (tres líneas, cita ADR-0020); `email`, `first_name`, `last_name`, `role` e
    `is_active` pasan a `Annotated[<tipo> | None, NoExplicitNull]` con el mismo `Field`/valor por defecto; `phone` no
    cambia; `format_title_case` pasa a `(cls, v: str) -> str` sin la rama `if v is None: return v`.
  - `tests/test_email_case.py`: `from pydantic import ValidationError` (tras `from alembic.operations import
    Operations`); `test_a_patch_with_a_null_email_keeps_it_null` (`:116-121`) se sustituye por
    `test_be37_a_patch_with_a_null_email_is_rejected`.
  - `tests/test_user_update_null.py`: módulo nuevo (U1, U2, H1 ×9, H2, H3 ×2, H4).
- **Tests (RED primero)** — escritos y ejecutados **antes** de tocar `app/`. Fábricas de `tests/conftest.py`
  (`persist_user`, `make_auth_headers`); `persist_user` confirma antes de la petición y `refresh` relee después
  (ADR-0011); se afirma sobre código, `raw_field`, tipo de `message`, estado y auditoría, nunca sobre texto en español.
  - **RED esperado** (medido contra `32b8fd4`):
    `./venv/Scripts/python.exe -m pytest tests/test_user_update_null.py tests/test_email_case.py -k be37 -q` →
    `12 failed, 4 passed`. Fallan el test del correo, U2, H1 ×9 (5 × 409 y 4 × 403) y H2 (409). Pasan ya U1, H3 ×2 y
    H4: son los bordes que el cambio no debe romper. Suite completa: `12 failed, 734 passed`.
- **Criterio de aceptación:** `-k be37` sobre esos dos archivos → `16 passed`; compuerta
  `./venv/Scripts/python.exe scripts/check.py` con salida 0: `70 files already formatted`, ruff 0, mypy 0 en 65, 4 kept,
  `746 passed` y cobertura 98,33 % (≥ 97,65 %); mutantes MU-*, MX-exclude_none y MF-falsy de la tabla con el
  resultado declarado, anotados en el handoff.
- **Fuera de alcance de esta fase:** `app/schemas/service.py` y `tests/test_services.py` (fase C); `UserBase`,
  `UserCreate`, `UserCreateByAdmin`, `UserResponse`; `phone`; `app/services/`, `app/main.py`; los unitarios de la
  política con `None`; el OpenAPI; ADRs; `AGENTS.md`.
- **Commit:**
  ```
  fix(schemas): reject explicit null on NOT NULL fields of UserUpdate

  UserUpdate accepted null on email, first_name, last_name, role and
  is_active. The key survived exclude_unset, the service applied it and
  the database refused it on commit, so the client got a 409 about a
  record that already exists and lost any valid field sent beside it
  (BE-37, measured).

  - app/schemas/partial_update.py: new NoExplicitNull marker, a
    BeforeValidator that refuses None. It only runs for a field present
    in the body, so the annotation keeps "| None" for the absent case
    and mypy stays truthful (ADR-0020).
  - app/schemas/user.py: the marker on the five NOT NULL fields; phone
    keeps clearing with null. format_title_case can no longer receive
    None, so its dead branch goes.
  - tests/test_email_case.py: the test that froze email=None as valid
    now expects the rejection.
  - tests/test_user_update_null.py: 422 with no mutation and no audit
    row for each field, including the four rejections that were a 403
    of the access policy; a valid field beside a null is not saved;
    phone null still clears; 401 still comes before the 422.

  The access policy does not change. Treating None as a deactivation
  (mutant M6) is no longer reachable over HTTP.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase C — `ServiceUpdate`

- **Archivos (2):** `app/schemas/service.py`, `tests/test_services.py`. Dominio: actualización de paquetes turísticos
  (frontera de entrada). `git diff --numstat` esperado: `18 8` y `112 0` (medido en la copia).
- **Cambios exactos** (texto literal en el Anexo C): `from typing import Annotated` y
  `from app.schemas.partial_update import NoExplicitNull`; docstring nueva de `ServiceUpdate` (cita ADR-0020, nombra
  `description` e `image_urls`); `name`, `category`, `base_price`, `max_capacity` e `is_available` pasan a
  `Annotated[<tipo> | None, NoExplicitNull]` con el mismo `Field`/valor por defecto; `description` e `image_urls` no
  cambian; `format_service_name` pasa a `(cls, v: str) -> str` sin la rama `if v is None: return v` y con docstring.
  En `tests/test_services.py`, sección nueva al final del archivo (tras la l.767), con S1–S5.
- **Tests (RED primero)** — escritos y ejecutados **antes** de tocar `app/`. Fixtures del propio archivo
  (`admin_headers`, `storage_double`, `classifying_storage`, `_persist_package`, `_stored_image_urls`, `TEMP_URL`,
  `PERMANENT_URL`) y de `tests/conftest.py` (`persist_user`, `make_auth_headers`). Dobles del CDN con `autospec` (ya lo
  son); se afirma `assert_not_awaited()` sobre `delete_image` y `promote_to_permanent`.
  - **RED esperado** (medido con la fase B aplicada):
    `./venv/Scripts/python.exe -m pytest tests/test_services.py -k be37 -q` → `7 failed, 4 passed`. Fallan S1 ×5 (409)
    y S2 ×2 (409 tras llamar al CDN). Pasan ya S3, S4 y S5 ×2. Suite completa: `7 failed, 750 passed`.
- **Criterio de aceptación:** `-k be37` sobre `tests/test_services.py` → `11 passed`; compuerta con salida 0:
  `70 files already formatted`, ruff 0, mypy 0 en 65, 4 kept, `757 passed`, cobertura 98,49 %; comandos 1–13 de la
  Verificación final como se esperan; mutantes MA, MS-* y M6 con el resultado declarado, anotados en el handoff.
- **Fuera de alcance de esta fase:** `description`, `image_urls` (y su fila de auditoría, BE-38), la lista vacía
  (BE-59); `ServiceBase`, `ServiceCreate`, `ServiceListResponse`, `ServiceDetailResponse`;
  `tourist_services_service.py` (el orden del CDN es BE-26); `app/schemas/user.py` y `partial_update.py`; ADRs.
- **Commit:**
  ```
  fix(schemas): reject explicit null on NOT NULL fields of ServiceUpdate

  ServiceUpdate accepted null on name, category, base_price,
  max_capacity and is_available, with the same 409 as UserUpdate. On
  packages it was worse: the 409 came after the CDN calls, so
  {"name": null, "image_urls": []} deleted the only blob and left its
  row behind, and a temporal URL was promoted and orphaned (BE-37,
  measured).

  - app/schemas/service.py: the NoExplicitNull marker from the user
    phase on the five NOT NULL fields, so the null stops at the schema
    before any blob is touched (ADR-0020). description keeps clearing
    with null and image_urls null still leaves the images alone.
    format_service_name loses its dead None branch and gains a
    docstring.
  - tests/test_services.py: 422 with the row, the CDN and the audit
    log untouched for each field and for a null beside an image
    replacement; description null still clears; image_urls null still
    keeps the images; the admin guard still answers 401 or 403 first.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, con la rama tras la fase C. Los conteos incluyen el texto que dicta este plan (código, docstrings,
comentarios, nombres y docstrings de tests, ADR) y están medidos con `grep` sobre una copia de `32b8fd4` con las tres
fases aplicadas. Los patrones de detección de la verificación, recalculados, son los comandos 3, 4, 5, 7 y 8; los de
columnas NOT NULL (`app/models/`, migración inicial) y el handler del 409 no cambian (comando 11).

```bash
# 1. El marcador → 14 líneas: app/schemas/partial_update.py 2 (:36 comentario de uso, :38 asignación),
#    app/schemas/user.py 6 (import :7 y cinco campos), app/schemas/service.py 6 (import :8 y cinco campos)
git grep -n "NoExplicitNull" -- app

# 2. Solo en los DTO de actualización (A9) → 10 líneas: user.py :170 :173 :179 :186 :187 (UserUpdate empieza en :160 y
#    es la última clase) y service.py :117 :119 :120 :123 :124 (ServiceUpdate empieza en :109 y es la última clase)
git grep -n -F ", NoExplicitNull] =" -- app

# 3. Opcionales que admiten None, en los dos archivos → 9 líneas, ninguna de los diez campos: user.py :65 :152 :185
#    (phone de UserBase, UserResponse y UserUpdate); service.py :27 :76 :93 :118 (description), :100 (deleted_at),
#    :125 (image_urls)
grep -nE '^\s+\w+: [^=]*\| None = (None|Field\()' app/schemas/user.py app/schemas/service.py

# 4. Sin exclude_none → 0 líneas (exit 1); exclude_unset sin cambios → 3 líneas
#    (tourist_services_service.py:282 y :337, user_service.py:284)
git grep -n "exclude_none" -- app
git grep -n "exclude_unset=True" -- app/services

# 5. La guarda que muta M6 no cambia → 1 línea, app/services/user_access_policy.py:114 (M6 inalcanzable por HTTP)
git grep -n 'update_dict.get("is_active") is False' -- app

# 6. Ramas muertas fuera → 0 líneas (exit 1)
git grep -n "if v is None" -- app/schemas

# 7. null explícito en tests → 12 líneas: test_services.py 5, test_user_access_policy.py 2 (:190 y :287, sin
#    cambio), test_user_update_null.py 5
git grep -nE '"(role|is_active|email|first_name|last_name|phone|name|description|category|base_price|max_capacity|is_available|image_urls)": ?(None|null)' -- tests

# 8. El test del correo invertido → 1 línea (tests/test_email_case.py:120); el nombre viejo → 0 (exit 1)
git grep -n "email=None" -- tests/test_email_case.py
git grep -n "test_a_patch_with_a_null_email_keeps_it_null" -- tests

# 9. Citas de ADR-0020 → app 4 (partial_update.py :6 :37, service.py :114, user.py :167); tests 4 (test_email_case.py
#    :118, test_services.py :770, test_user_update_null.py :1 :67); docs/adr: los archivos 0018 y 0020
git grep -n "ADR-0020" -- app tests
git grep -l "ADR-0020" -- docs/adr

# 10. Tests del ítem → test_email_case.py:1, test_services.py:5, test_user_update_null.py:6; 27 casos; los de
#     BE-35, BE-36 y BE-58 siguen (41 casos)
git grep -c "def test_be37_" -- tests
./venv/Scripts/python.exe -m pytest -k be37 -q                                                    # → 27 passed
./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k "be35 or be36 or be58" -q   # → 41 passed

# 11. Nada fuera del alcance → salida vacía
git diff --stat 32b8fd4 HEAD -- app/services app/api app/main.py app/models app/repositories app/core app/cli app/db alembic tests/test_user_access_policy.py tests/test_route_guards.py tests/test_auth.py tests/test_user_service.py tests/conftest.py conftest.py pyproject.toml constraints.txt AGENTS.md docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md

# 12. Lo que sí cambia → exactamente 8 líneas: partial_update.py 38 0; service.py 18 8; user.py 13 9; ADR-0018 9 0;
#     ADR-0020 63 0; test_email_case.py 6 5; test_services.py 112 0; test_user_update_null.py 149 0
git diff --numstat 32b8fd4 HEAD -- app tests docs/adr

# 13. Compuerta completa → salida 0; 70 files already formatted; ruff 0; mypy 0 en 65; 4 kept; 757 passed;
#     cobertura 98,49 % (≥ 97,65 %)
./venv/Scripts/python.exe scripts/check.py
```

Verificación funcional que pedía la verificación (la cubren H1, S1 y S2; no hace falta repetirla a mano): `PATCH` de
superadmin sobre admin con `{"role": null}` y con `{"is_active": null}`, y `PUT` de admin con `{"name": null}` → 422,
sin mutación, sin auditoría y sin llamada al CDN.

## Residuales

- **R1 — El OpenAPI sigue anunciando `null` en los diez campos.** Medido sobre `app.openapi()` con las fases B y C:
  `UserUpdate.role` = `anyOf [UserRole, null]`, igual en los otros nueve. El contrato publicado dice que `null` vale y
  la API responde 422. Causa: la anotación conserva `| None` a propósito (decisión bloqueada 7). Arreglo posible:
  `SkipJsonSchema[None]` en la unión o `json_schema_input_type` del `BeforeValidator` (un tipo por campo, así que deja
  de ser un solo marcador). Fila sugerida para `docs/backlog.md`: "BE-60 · plan de BE-37 (residual R1) · El OpenAPI de
  `UserUpdate` y `ServiceUpdate` anuncia `null` en los diez campos que lo rechazan con 422 · Baja ·
  **Sale → `B-FUTURO`** · Quitar `null` del esquema sin que la anotación mienta a mypy; test sobre `app.openapi()`."
- **R2 — Los avisos de la suite suben de 8 a 25.** Cada 422 que atraviesa el handler emite
  `StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated` (`app/main.py:94`); la fase B añade 10 y
  la C 7 (medido: 8 → 18 → 25). Es S5 del backlog, sin cambio de decisión. Destino: nota en la fila S5 ("BE-37 añade 17
  avisos; se van con S5").
- **R3 — El 422 de `email` no usa el texto del validador** (opción a): la rama propia de `email` del handler
  (`app/main.py:77-79`) responde "no tiene un formato válido" también ante `null`. Con la opción (b), cuatro campos
  salen sin traducir (`role`, `is_active`, `category`, `is_available` no están en `field_dict`). Los dos son del
  handler, que este ítem no toca. Destino: decisión pendiente 1; si David quiere otro texto para `email`, nota en la
  fila P2 (handlers en español), la que reescribirá ese handler.
- **R4 — Ritual de cierre.** La viñeta de AGENTS §3 (ADR-0020) la escribe David después de la auditoría de la fase C y
  antes de `/pr` (adenda, decisión 7): el comando 11 exige `AGENTS.md` sin cambio desde `32b8fd4`, así que un commit
  anterior lo pondría en rojo sin que el ítem haya hecho nada mal. La bitácora del día de la aprobación menciona el
  addendum de ADR-0018 (ADR-0009, punto 5). La entrada de ADR-0020 en `docs/CONTEXT.md` y la fila BE-37 del backlog
  (con M6 inalcanzable, que cierra las notas de BE-35 y BE-58), la sesión Mentor. Fila sugerida: ninguna.
- **R5 — `image_urls: null` escribe una fila de auditoría de un no-cambio.** Ya anotado en BE-38 por la adenda; S4 no
  afirma sobre la auditoría para no congelarlo. Sin fila nueva.

## Referencias

- Pydantic 2.12.5 (`constraints.txt:56`) · `BeforeValidator` en `Annotated` ("field before validators"):
  https://docs.pydantic.dev/2.12/concepts/validators/#field-before-validator — comprobado en la docstring instalada
  (`pydantic.functional_validators.BeforeValidator`) y medido: las restricciones de `Field` siguen aplicándose.
- Pydantic 2.12.5 · los valores por defecto no se validan salvo `validate_default=True` (por eso el marcador no toca
  un campo ausente): https://docs.pydantic.dev/2.12/concepts/fields/#validate-default-values — medido (U1).
- pydantic-core 2.41.5 · `PydanticCustomError` (opción b de la decisión pendiente 1):
  https://docs.pydantic.dev/2.12/errors/errors/#custom-errors — medido.
- FastAPI 0.135.1 · los guards (dependencias) responden antes de validar el cuerpo: medido (encargo 3) y congelado por
  H4 y S5; https://fastapi.tiangolo.com/tutorial/dependencies/
- Context7 no conectó en esta sesión (timeout del servidor MCP): las APIs de Pydantic se comprobaron en el código
  instalado en `venv/` y con mediciones en copia.

## Mediciones (literales; scratchpad de la sesión, nunca en el repo)

**(1) Sondas antes (`32b8fd4`) y después (copia con B y C)**, un archivo de sondas del scratchpad con la `conftest.py`
del proyecto:

```
antes   P1 superadmin → superadmin {"is_active": null}: 403 · is_active True · 0 filas de auditoría
antes   P2 PATCH /usuarios/{cédula} {"role": null} sin token: 401
antes   P3 PUT /servicios/{id} {"name": null} sin token: 401
antes   P4 PUT /servicios/{id} {"name": null} como turista: 403
antes   P6/P7 email, first_name, last_name, role, is_active, name, category, base_price, max_capacity,
        is_available: 409 · phone, description, image_urls: 200
después P1: 422 {"detalle": [{"raw_field": "is_active", …}]} · is_active True · 0 filas
después P2/P3: 401 · P4: 403 (congelados por H4 y S5)
después P6/P7: los diez → 422 con un elemento y su raw_field · phone, description, image_urls: 200
después P8 {"role": null, "is_active": null, "first_name": "Nuevo"}: 422 con raw_field role e is_active
```

**(2) RED** (copias de `32b8fd4` con solo los tests; la de C, con B aplicada): fase B `-k be37` → `12 failed, 4 passed`,
suite `12 failed, 734 passed`; fase C `-k be37` → `7 failed, 4 passed`, suite `7 failed, 750 passed`. Nada fuera de los
be37 cae.

**(3) GREEN**, `scripts/check.py` completo, exit 0. Fase B (copia con solo B):

```
70 files already formatted
All checks passed!
Success: no issues found in 65 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1046     11    152      9  98.33%
746 passed, 18 warnings in 30.20s
Compuerta superada.
```

Fases A, B y C (copia final):

```
70 files already formatted
All checks passed!
Success: no issues found in 65 source files
Contracts: 4 kept, 0 broken.
app\main.py                                   57      1     18      1  97.33%   72
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
TOTAL                                       1046     10    150      8  98.49%
757 passed, 25 warnings in 30.50s
Compuerta superada.
```

`-k be37` → `27 passed`; `tests/test_user_access_policy.py -k "be35 or be36 or be58"` → `41 passed`. La cobertura sube
de 97,65 % a 98,49 %: desaparecen `user.py:188` y `service.py:120` (ramas muertas) y se cubren `main.py:61`, `:79` y
`:82` (rama `value_error` y la de `email` del handler).

**(4) Mutantes**, suite completa sobre la copia GREEN (sin la docstring de `format_service_name`, que no cambia
comportamiento), uno por ejecución, restaurando después:

```
== MU-email: 2 failed, 755 passed, 24 warnings in 29.78s
    FAILED tests/test_email_case.py::test_be37_a_patch_with_a_null_email_is_rejected
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-email]
== MU-first_name: 1 failed, 756 passed, 24 warnings in 29.91s
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-first_name]
== MU-last_name: 1 failed, 756 passed, 24 warnings in 30.10s
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-last_name]
== MU-role: 5 failed, 752 passed, 21 warnings in 30.33s
    FAILED tests/test_user_update_null.py::test_be37_every_null_field_is_reported
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-role]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-self-role]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[admin-on-tourist-role]
    FAILED tests/test_user_update_null.py::test_be37_null_beside_a_valid_field_changes_nothing
== MU-is_active: 4 failed, 753 passed, 22 warnings in 30.27s
    FAILED tests/test_user_update_null.py::test_be37_every_null_field_is_reported
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-is_active]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[tourist-on-self-is_active]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-peer-is_active]
== MU-phone+: 2 failed, 755 passed, 27 warnings in 28.82s
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== MX-exclude_none: 2 failed, 755 passed, 25 warnings in 28.66s
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== MF-falsy: 10 failed, 747 passed, 35 warnings in 30.26s
    FAILED tests/test_auth.py::test_tourist_self_is_active_change_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
    FAILED tests/test_user_access_policy.py::test_be36_peer_superadmin_deactivation_still_returns_403
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== MA-after: 757 passed, 25 warnings in 30.46s
== MS-name: 3 failed, 754 passed, 22 warnings in 31.50s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[name]
    FAILED tests/test_services.py::test_be37_null_beside_new_images_touches_no_blob[replace]
    FAILED tests/test_services.py::test_be37_null_beside_new_images_touches_no_blob[empty]
== MS-category: 1 failed, 756 passed, 24 warnings in 32.44s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[category]
== MS-base_price: 1 failed, 756 passed, 24 warnings in 31.71s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[base_price]
== MS-max_capacity: 1 failed, 756 passed, 24 warnings in 30.03s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[max_capacity]
== MS-is_available: 1 failed, 756 passed, 24 warnings in 30.96s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[is_available]
== MS-description+: 1 failed, 756 passed, 26 warnings in 30.62s
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
== MS-image_urls+: 1 failed, 756 passed, 26 warnings in 28.95s
    FAILED tests/test_services.py::test_be37_null_on_image_urls_still_keeps_the_images
== M6: 757 passed, 25 warnings in 29.27s
```

**(5) Mecanismo descartado (c), quitar `| None`:** `mypy app` → `Found 10 errors in 2 files` (`Incompatible types in
assignment (expression has type "None", variable has type "str")` y análogos, uno por campo).

**(6) Columnas.** Código y tests: `ruff format --check` y `ruff check` en verde en la copia (máximo 100). ADR-0020: 63
líneas, la más larga 120; addendum: 9 líneas, la más larga 118 (con `<FECHA>`). Asuntos de commit: 70, 67 y 70.

## Anexo A — texto de la fase A

ADR-0020 (archivo nuevo, completo):

```markdown
# ADR-0020 — En un DTO de actualización, `null` explícito solo donde la columna admite vacío

- **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-37)
- **Propuesta:** Claude, `plan-redactor` (17 nov 2026), sobre la adenda de David a la verificación (17 nov, 12:09)
- **Ubicación en el repo:** `docs/adr/0020-null-explicito-solo-donde-la-columna-admite-vacio.md`
- **Origen:** backlog BE-37; `docs/deuda/BE-37/verificacion.md` (veredicto y adenda); `docs/deuda/BE-37/plan.md`.
  Relación: ADR-0002 (la invariante ya vivía en la base; la frontera se alinea con ella), ADR-0016 (precedente de regla
  de campo escrita en la anotación: `LowercaseEmail`), ADR-0018 (addendum del mismo día: el `null` entre superadmins
  pasa de 403 a 422), AGENTS §3 (un DTO de salida no hereda de uno de entrada, A9).

## Contexto

En `PATCH /usuarios/{cédula}` y `PUT /servicios/{id}` un campo ausente significa "déjalo como está" y un `null`
explícito significa "vacíalo": `model_dump(exclude_unset=True)` conserva la clave con `None` y el servicio la aplica.
Diez campos de `UserUpdate` y `ServiceUpdate` admitían ese `null` sobre columnas NOT NULL. Medido el 17 nov: la base lo
rechazaba al confirmar y el handler de `IntegrityError` respondía 409 con un texto de "registro que ya existe"; un
cambio válido enviado al lado se perdía, y en paquetes el 409 llegaba después de borrar o promover blobs en el CDN
(`{"name": null, "image_urls": []}` dejaba una imagen rota). `phone` y `description` sí admiten vacío: su `null` borra
el dato y responde 200.

## Decisión

1. **En un DTO de actualización, un `null` explícito solo se admite en un campo cuya columna admite vacío.** En
   cualquier otro se rechaza en el schema con 422, antes de que corran la política de acceso, el CDN o la auditoría:
   nada cambia y no se escribe fila de auditoría.
2. **Un solo mecanismo, junto al campo:** el marcador `NoExplicitNull` (`app/schemas/partial_update.py`), un
   `BeforeValidator` que se escribe en la anotación: `Annotated[T | None, NoExplicitNull]`. La anotación conserva
   `| None` porque un campo ausente vale `None` en el modelo; el marcador rechaza solo el `null` que envía el cliente.
3. **Campos hoy:** `email`, `first_name`, `last_name`, `role` e `is_active` en `UserUpdate`; `name`, `category`,
   `base_price`, `max_capacity` e `is_available` en `ServiceUpdate`. `phone` y `description` siguen borrándose con
   `null`. `image_urls` no es columna: su `null` sigue sin cambiar las imágenes (BE-38, BE-59).
4. **Ningún DTO de salida lleva el marcador** (A9): describe lo que entra, no lo que ya está guardado.
5. **Un campo nuevo** de un DTO de actualización cuya columna sea NOT NULL nace con el marcador.

## Consecuencias

- Contrato: las diez peticiones con `null` sobre columna NOT NULL pasan de 409 a 422 con el cuerpo de validación de
  siempre (`{"detalle": [{"raw_field", "message"}]}`). Cuatro rechazos que daba la política con 403 pasan a 422 y siguen
  siendo rechazos: superadmin sobre sí mismo con `{"role": null}`, admin sobre turista con `{"role": null}`, turista
  sobre sí mismo con `{"is_active": null}` y superadmin sobre otro superadmin con `{"is_active": null}` (addendum de
  ADR-0018). Los guards de ruta siguen respondiendo antes: 401 sin token, 403 a un turista en paquetes.
- La política de acceso no cambia. Tratar `None` como desactivación (mutante M6 de BE-35 y BE-58) deja de ser
  alcanzable por HTTP.
- El handler de `IntegrityError` sigue siendo la red de los índices únicos; deja de recibir los NOT NULL de estas dos
  rutas.
- El OpenAPI sigue anunciando `null` en esos diez campos (`anyOf` con `null`); queda en el backlog.

## Alternativas consideradas

1. **`exclude_none=True` en el `model_dump` de los servicios.** Rechazada: vuelve no-op el `null` legítimo de `phone` y
   `description`, y el cliente creería haber borrado algo.
2. **Quitar `| None` de la anotación (`first_name: str = Field(None, …)`).** Rechazada: rechaza el `null`, pero la
   anotación miente, porque un campo ausente vale `None`; mypy da 10 errores (medido).
3. **Un `field_validator(…, mode="before")` por DTO con la lista de campos.** Mismo comportamiento (sonda de la sesión
   Mentor, 17 nov). Descartada: repite el validador en los dos DTO y separa la regla del campo que la lleva.
4. **No hacer nada.** Rechazada: 409 con un mensaje falso, cambios válidos perdidos e imágenes rotas en paquetes.

## Evidencia

- Verificación (17 nov, 27 sondas con la pila real de la suite): 409 en los diez campos, sin mutación ni auditoría; en
  paquetes, `delete_image` o `promote_to_permanent` antes del 409.
- Plan (17 nov): con el marcador, 422 en los diez, sin mutación, sin auditoría y sin llamada al CDN; `phone` y
  `description` siguen en 200. Tests y mutantes: `docs/deuda/BE-37/plan.md`.
```

Addendum, al final de ADR-0018 (la primera línea del bloque es la línea en blanco que lo separa):

```markdown

## Addendum — <FECHA> (David, al aprobar el plan de BE-37; bitácora `<AAAA-MM-DD>`)

Aclara cómo se cumple el punto 1 de la decisión con el valor `null`. Desde ADR-0020, `UserUpdate` rechaza un `null`
explícito en `is_active` con 422, en el schema y antes de que corra `UserAccessPolicy`: un superadmin que envía
`{"is_active": null}` sobre otro superadmin recibe 422, no 403 (medido el 17 nov con la pila real de la suite: 403
antes y 422 después, sin mutación ni fila de auditoría en los dos casos). La decisión no cambia: `null` no reactiva, y
la política lo sigue tratando como cualquier valor distinto de `true` (caso `"null"` de
`test_be36_peer_superadmin_update_other_than_reactivation_is_rejected`, que se queda).
```

## Anexo B — texto de la fase B

`app/schemas/partial_update.py` (archivo nuevo, completo):

```python
"""Field rule shared by the partial-update DTOs: explicit null only where the column admits it.

In a partial update an absent field means "leave it as it is" and an explicit null means "empty
it". Only a column that admits empty can store the second, so every other optional field of
UserUpdate and ServiceUpdate rejects null at the boundary, with a 422, before any policy,
storage call or audit row runs (ADR-0020).
"""

from typing import Any

from pydantic import BeforeValidator

_NULL_MESSAGE = "Este campo no puede quedar vacío."


def _reject_explicit_null(value: Any) -> Any:
    """Lets every value through except an explicit null.

    Runs before the field's own type and constraints, and only for a field present in the
    payload: an absent field keeps its None default without reaching this check.

    Args:
        value: The raw value received for the field.

    Returns:
        The same value, untouched.

    Raises:
        ValueError: If the value is None; the 422 handler shows its message.
    """
    if value is None:
        raise ValueError(_NULL_MESSAGE)
    return value


# Usage: Annotated[T | None, NoExplicitNull] on an update field whose column is NOT NULL. The
# annotation keeps "| None" because an absent field is None on the model (ADR-0020).
NoExplicitNull = BeforeValidator(_reject_explicit_null)
```

`app/schemas/user.py` (diff contra `32b8fd4`; solo estos dos bloques):

```diff
@@ -4,6 +4,8 @@ from typing import Annotated
 
 from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, field_validator
 
+from app.schemas.partial_update import NoExplicitNull
+
 
 class UserRole(str, Enum):  # noqa: UP042 (backlog D2)
     """Pydantic enumeration for user roles validation.
@@ -160,31 +162,33 @@ class UserUpdate(BaseModel):
 
     Enforces partial updates (PATCH/PUT behavior) by making all fields optional.
     Sensitive immutable fields such as 'cedula' and 'password' are fundamentally
-    excluded to prevent unauthorized architectural mutations.
+    excluded to prevent unauthorized architectural mutations. An explicit null is
+    accepted only on phone, whose column admits empty; on any other field it is a
+    422 (ADR-0020).
     """
 
-    email: LowercaseEmail | None = Field(None, description="Correo electrónico válido")
-    first_name: str | None = Field(
+    email: Annotated[LowercaseEmail | None, NoExplicitNull] = Field(
+        None, description="Correo electrónico válido"
+    )
+    first_name: Annotated[str | None, NoExplicitNull] = Field(
         None,
         min_length=2,
         max_length=65,
         pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
     )
-    last_name: str | None = Field(
+    last_name: Annotated[str | None, NoExplicitNull] = Field(
         None,
         min_length=2,
         max_length=65,
         pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
     )
     phone: str | None = Field(None, pattern=r"^3\d{9}$")
-    role: UserRole | None = None
-    is_active: bool | None = None
+    role: Annotated[UserRole | None, NoExplicitNull] = None
+    is_active: Annotated[bool | None, NoExplicitNull] = None
 
     @field_validator("first_name", "last_name")
     @classmethod
-    def format_title_case(cls, v: str | None) -> str | None:
+    def format_title_case(cls, v: str) -> str:
         """Silently applies title casing if the field is present in the payload."""
-        if v is None:
-            return v
         clean = " ".join(v.split())
         return clean.title()
```

`tests/test_email_case.py` (diff contra `32b8fd4`):

```diff
@@ -16,6 +16,7 @@ import jwt
 import pytest
 from alembic.migration import MigrationContext
 from alembic.operations import Operations
+from pydantic import ValidationError
 from sqlalchemy import Connection, create_engine, func, inspect, select
 from sqlalchemy.exc import IntegrityError
 from sqlalchemy.orm import Session
@@ -113,12 +114,12 @@ def test_a_non_ascii_local_part_is_lowercased_too() -> None:
     assert UserLogin(email="ÁNGEL@Test.com", password=PASSWORD).email == "ángel@test.com"
 
 
-def test_a_patch_with_a_null_email_keeps_it_null() -> None:
-    """Edge case: the optional email of UserUpdate accepts None and does not lower it."""
-    update = UserUpdate(email=None, phone="3001234567")
+def test_be37_a_patch_with_a_null_email_is_rejected() -> None:
+    """Unhappy path: the email column is NOT NULL, so UserUpdate refuses null (ADR-0020)."""
+    with pytest.raises(ValidationError) as exc_info:
+        UserUpdate(email=None, phone="3001234567")
 
-    assert update.email is None
-    assert update.model_dump(exclude_unset=True) == {"email": None, "phone": "3001234567"}
+    assert [error["loc"] for error in exc_info.value.errors()] == [("email",)]
 
 
 async def test_registration_stores_the_email_in_lowercase(client, db_session, mock_send_email):
```

`tests/test_user_update_null.py` (archivo nuevo, completo):

```python
"""Tests for BE-37: an explicit null on a NOT NULL user column is a 422 (ADR-0020).

UserUpdate rejects null on email, first_name, last_name, role and is_active before the access
policy runs, so the request changes nothing and writes no audit row. phone keeps accepting null,
which clears it, and an absent field still means "leave it as it is".
"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.audit import AuditLog
from app.models.user import UserRole
from app.schemas.user import UserUpdate


async def _audit_rows(db_session) -> list[AuditLog]:
    """Returns every audit row written so far."""
    return list((await db_session.execute(select(AuditLog))).scalars().all())


def test_be37_absent_fields_stay_unset() -> None:
    """Edge case: an empty payload sets nothing; absent is not null."""
    update = UserUpdate.model_validate({})

    assert update.model_dump(exclude_unset=True) == {}
    assert update.role is None
    assert update.is_active is None


def test_be37_every_null_field_is_reported() -> None:
    """Edge case: two nulls give two errors, and the valid field beside them does not save them."""
    with pytest.raises(ValidationError) as exc_info:
        UserUpdate.model_validate({"role": None, "is_active": None, "first_name": "Nuevo"})

    assert [error["loc"] for error in exc_info.value.errors()] == [("role",), ("is_active",)]


@pytest.mark.parametrize(
    ("actor_role", "target_role", "field"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, "email", id="superadmin-on-admin-email"),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "first_name", id="superadmin-on-admin-first_name"
        ),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "last_name", id="superadmin-on-admin-last_name"
        ),
        pytest.param(UserRole.superadmin, UserRole.admin, "role", id="superadmin-on-admin-role"),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "is_active", id="superadmin-on-admin-is_active"
        ),
        pytest.param(UserRole.superadmin, None, "role", id="superadmin-on-self-role"),
        pytest.param(UserRole.admin, UserRole.tourist, "role", id="admin-on-tourist-role"),
        pytest.param(UserRole.tourist, None, "is_active", id="tourist-on-self-is_active"),
        pytest.param(
            UserRole.superadmin, UserRole.superadmin, "is_active", id="superadmin-on-peer-is_active"
        ),
    ],
)
async def test_be37_null_on_not_null_field_returns_422_without_mutation(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role, field
):
    """Unhappy path: 422 naming the field; the account and the audit log stay as they were.

    The last four cases were a 403 of the access policy before BE-37; the null now stops at
    the schema, so the policy never sees it (ADR-0020; ADR-0018 addendum for the peer case).
    """
    actor = await persist_user(role=actor_role)
    target = actor if target_role is None else await persist_user(role=target_role)
    stored_before = getattr(target, field)

    response = await client.patch(
        f"/usuarios/{target.cedula}", json={field: None}, headers=make_auth_headers(actor)
    )

    assert response.status_code == 422
    errors = response.json()["detalle"]
    assert [error["raw_field"] for error in errors] == [field]
    assert isinstance(errors[0]["message"], str)
    await db_session.refresh(target)
    assert getattr(target, field) == stored_before
    assert await _audit_rows(db_session) == []


async def test_be37_null_beside_a_valid_field_changes_nothing(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the valid first_name sent beside a null role is not saved either."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": None, "first_name": "Nuevo"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 422
    assert [error["raw_field"] for error in response.json()["detalle"]] == ["role"]
    await db_session.refresh(admin)
    assert admin.first_name == "John"
    assert admin.role == UserRole.admin
    assert await _audit_rows(db_session) == []


@pytest.mark.parametrize(
    ("actor_role", "target_role"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, id="superadmin-on-admin"),
        pytest.param(UserRole.tourist, None, id="tourist-on-self"),
    ],
)
async def test_be37_null_on_phone_still_clears_it(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role
):
    """Happy path: the phone column admits empty, so null clears it and the change is audited."""
    actor = await persist_user(role=actor_role, phone="3001234567")
    target = (
        actor if target_role is None else await persist_user(role=target_role, phone="3001234567")
    )

    response = await client.patch(
        f"/usuarios/{target.cedula}", json={"phone": None}, headers=make_auth_headers(actor)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == target.cedula
    assert body["phone"] is None
    await db_session.refresh(target)
    assert target.phone is None
    audits = await _audit_rows(db_session)
    assert [(audit.entity_id, audit.changes) for audit in audits] == [
        (target.cedula, {"phone": None})
    ]


async def test_be37_missing_token_is_rejected_before_the_null(client, db_session, persist_user):
    """Unhappy path: without a token the guard answers 401 before the body is validated."""
    tourist = await persist_user()

    response = await client.patch(f"/usuarios/{tourist.cedula}", json={"role": None})

    assert response.status_code == 401
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist
    assert await _audit_rows(db_session) == []
```

## Anexo C — texto de la fase C

`app/schemas/service.py` (diff contra `32b8fd4`):

```diff
@@ -1,9 +1,11 @@
 from datetime import datetime
 from decimal import Decimal
+from typing import Annotated
 
 from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
 
 from app.models.service import ServiceCategory
+from app.schemas.partial_update import NoExplicitNull
 
 
 class ServiceImageResponse(BaseModel):
@@ -105,18 +107,26 @@ class ServiceImageOutput(BaseModel):
 
 
 class ServiceUpdate(BaseModel):
-    name: str | None = Field(None, min_length=20, max_length=65)
+    """Partial update of a tourist package: only the fields present in the payload change.
+
+    An explicit null is accepted only on description, whose column admits empty, and on
+    image_urls, where it leaves the images as they are; on any other field it is a 422
+    (ADR-0020).
+    """
+
+    name: Annotated[str | None, NoExplicitNull] = Field(None, min_length=20, max_length=65)
     description: str | None = Field(None, max_length=1000)
-    category: ServiceCategory | None = None
-    base_price: Decimal | None = Field(None, ge=40000, max_digits=10, decimal_places=2)
-    max_capacity: int | None = Field(None, gt=0, le=30)
-    is_available: bool | None = None
+    category: Annotated[ServiceCategory | None, NoExplicitNull] = None
+    base_price: Annotated[Decimal | None, NoExplicitNull] = Field(
+        None, ge=40000, max_digits=10, decimal_places=2
+    )
+    max_capacity: Annotated[int | None, NoExplicitNull] = Field(None, gt=0, le=30)
+    is_available: Annotated[bool | None, NoExplicitNull] = None
     image_urls: list[HttpUrl] | None = Field(None, max_length=10)
 
     @field_validator("name")
     @classmethod
-    def format_service_name(cls, v: str | None) -> str | None:
-        if v is None:
-            return v
+    def format_service_name(cls, v: str) -> str:
+        """Title-cases the package name and collapses repeated whitespace."""
         clean = " ".join(v.split())
         return clean.title()
```

`tests/test_services.py`: al final del archivo, tras la l.767 y dos líneas en blanco:

```python
# === BE-37: an explicit null on a NOT NULL package column is a 422 (ADR-0020) ===
# ServiceUpdate rejects the null before the service runs: no row changes, no blob is deleted or
# promoted and no audit row is written. description keeps clearing with null, and
# image_urls: null keeps the images.


@pytest.mark.parametrize(
    "field", ["name", "category", "base_price", "max_capacity", "is_available"]
)
async def test_be37_null_on_not_null_package_field_returns_422_without_side_effects(
    client, db_session, admin_headers, storage_double, field
):
    """Unhappy path: 422 naming the field; the row, the CDN and the audit log are untouched."""
    package = await _persist_package(db_session)
    stored_before = getattr(package, field)

    response = await client.put(
        f"/servicios/{package.id}", json={field: None}, headers=admin_headers
    )

    assert response.status_code == 422
    errors = response.json()["detalle"]
    assert [error["raw_field"] for error in errors] == [field]
    assert isinstance(errors[0]["message"], str)
    await db_session.refresh(package)
    assert getattr(package, field) == stored_before
    storage_double.delete_image.assert_not_awaited()
    storage_double.promote_to_permanent.assert_not_awaited()
    assert (await db_session.execute(select(AuditLog))).scalars().all() == []


@pytest.mark.parametrize(
    "image_urls", [pytest.param([TEMP_URL], id="replace"), pytest.param([], id="empty")]
)
async def test_be37_null_beside_new_images_touches_no_blob(
    client, db_session, admin_headers, classifying_storage, image_urls
):
    """Unhappy path: before BE-37 the 409 came after the CDN calls; now no blob is touched."""
    package = await _persist_package(db_session)
    package_id = package.id
    db_session.add(ServiceImage(service_id=package_id, image_url=PERMANENT_URL))
    await db_session.commit()

    response = await client.put(
        f"/servicios/{package_id}",
        json={"name": None, "image_urls": image_urls},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert [error["raw_field"] for error in response.json()["detalle"]] == ["name"]
    classifying_storage.delete_image.assert_not_awaited()
    classifying_storage.promote_to_permanent.assert_not_awaited()
    assert await _stored_image_urls(db_session, package_id) == [PERMANENT_URL]
    assert (await db_session.execute(select(AuditLog))).scalars().all() == []


async def test_be37_null_on_description_still_clears_it(client, db_session, admin_headers):
    """Happy path: the description column admits empty, so null clears it and is audited."""
    package = await _persist_package(db_session, description="Recorrido por la reserva")

    response = await client.put(
        f"/servicios/{package.id}", json={"description": None}, headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["description"] is None
    await db_session.refresh(package)
    assert package.description is None
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert [audit.changes for audit in audits] == [{"description": None}]


async def test_be37_null_on_image_urls_still_keeps_the_images(
    client, db_session, admin_headers, classifying_storage
):
    """Edge case: image_urls null is still a 200 that leaves the images and the CDN alone."""
    package = await _persist_package(db_session)
    package_id = package.id
    db_session.add(ServiceImage(service_id=package_id, image_url=PERMANENT_URL))
    await db_session.commit()

    response = await client.put(
        f"/servicios/{package_id}", json={"image_urls": None}, headers=admin_headers
    )

    assert response.status_code == 200
    assert [image["image_url"] for image in response.json()["images"]] == [PERMANENT_URL]
    classifying_storage.delete_image.assert_not_awaited()
    classifying_storage.promote_to_permanent.assert_not_awaited()
    assert await _stored_image_urls(db_session, package_id) == [PERMANENT_URL]


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [pytest.param(None, 401, id="anonymous"), pytest.param(UserRole.tourist, 403, id="tourist")],
)
async def test_be37_package_guard_answers_before_the_null(
    client, db_session, persist_user, make_auth_headers, role, expected_status
):
    """Unhappy path: the admin guard answers 401 or 403 before the body is validated."""
    package = await _persist_package(db_session)
    headers = {} if role is None else make_auth_headers(await persist_user(role=role))

    response = await client.put(f"/servicios/{package.id}", json={"name": None}, headers=headers)

    assert response.status_code == expected_status
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(package)
    assert package.name == "Paquete De Prueba Automatizada"
```


## Enmiendas aprobadas

### E0 — 17 nov 2026, 15:16 (David: "listo, apruebo las 3"; revisión de la sesión Mentor)

1. **Plan aprobado, tres fases, y ADR-0020 aceptado** con el texto del Anexo A, incluido el addendum de ADR-0018.
   `<FECHA>` = `17 nov 2026`; `<AAAA-MM-DD>` = `2026-11-17`.
2. **Decisión pendiente 1, texto del 422: opción (a), con el texto `"Este campo no puede quedar vacío."`** y sin la
   segunda frase que recomendaba el plan ("Omítalo si no desea modificarlo."): le habla a quien programa el cliente y
   el texto llega a la pantalla del usuario final, que no puede omitir un campo. **Ya aplicado en el Anexo B:** la línea
   de `app/schemas/partial_update.py` es `_NULL_MESSAGE = "Este campo no puede quedar vacío."` (51 columnas, medidas con
   el intérprete). Nada más cambia: el `numstat` de la fase B sigue en `38 0`, ningún test afirma sobre el texto y los
   conteos de la Verificación final no lo miran. Donde el Resumen y la tabla de cuerpos del 422 dicen `<texto>`, es
   este. Se acepta el residual R3: con `email` en `null` el handler responde con su texto propio para ese campo
   (`app/main.py:77-79`), no con este.
3. **Decisiones pendientes 2 y 3, aprobadas como se recomiendan:** textos de ADR-0020 y del addendum; los 27 casos.
4. **Cuarto rechazo 403 → 422, aceptado:** superadmin sobre otro superadmin con `{"is_active": null}` (encargo 1,
   medido por el planificador: 403 antes, 422 después, sin mutación ni auditoría). Se suma a los tres de la adenda.
5. **Residuales con destino.** R1 (el OpenAPI sigue anunciando `null`): fila **BE-60**, `Sale → B-FUTURO`, severidad
   Baja confirmada por David, con un dato de la sesión Mentor (pydantic 2.12.5, réplica mínima): `SkipJsonSchema[None]`
   en la unión quita el `null` del esquema y pasa mypy, pero cambia el tipo de error de otra validación (`"A"` en un
   campo con `min_length=2` pasa de `string_too_short` a `too_short`), y el handler del 422 elige el mensaje por tipo.
   R2 (avisos de 8 a 25): nota en la fila S5. R3: aceptado (punto 2). R4 y R5: como dice el plan.
6. **Sin correcciones de dictado.** Contraste de la sesión Mentor contra `32b8fd4`: `app/schemas/user.py:1-8` y
   `:160-190`; `app/schemas/service.py:107-122`; `tests/test_email_case.py:14-22` y `:116-121`;
   `tests/test_services.py` (767 líneas; fixtures en `:35`, `:366`, `:502`, `:513`, `:600`; `AuditLog`, `ServiceImage`,
   `UserRole` y `select` ya importados). Las cifras de las copias, los 17 mutantes y las columnas los midió el
   planificador; el ejecutor los repite y el auditor también.
7. **Orden para David:** la viñeta de AGENTS §3 (ADR-0020) se commitea **después** de la auditoría de la fase C y antes
   de `/pr` (el comando 11 exige `AGENTS.md` sin cambio desde `32b8fd4`).

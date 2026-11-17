# Verificación — BE-37: `null` explícito en los DTO de actualización acaba en 409 genérico

**Veredicto:** confirmada (y más ancha que la fila: el molde está también en `ServiceUpdate`)
**Fuente del ítem:** docs/backlog.md (fila BE-37, l.89; notas de BE-35 R2 y BE-58 R4 sobre el mutante M6) + rincón 4 de
`docs/deuda/BE-02/verificacion.md:92-95` y residual 3 de `docs/deuda/BE-02/plan.md:230-231`
**Fecha:** 2026-11-17

## Qué describe el ítem
`{"role": null}` enviado por un superadmin sobre un tercero responde **409** (handler genérico de `IntegrityError`), no
422: `UserUpdate` admite `None`, `model_dump(exclude_unset=True)` conserva la clave, la política la deja pasar y la base
rechaza el `NULL` por `NOT NULL`. La fila afirma que el molde se repite en `is_active` "y demás opcionales, sin medir", y
las notas de BE-35/BE-58 añaden que el mutante M6 (tratar `None` como desactivación) vive porque `null` llega a la
política; cerrar BE-37 lo vuelve inalcanzable.

## Evidencia en el código
Líneas actualizadas (las de la fila son de antes de BE-35, BE-36 y BE-58):

| Cita de la fila | Hoy | Contenido |
|---|---|---|
| `schemas/user.py:174` | `app/schemas/user.py:180` | `role: UserRole \| None = None` |
| `schemas/user.py:175` | `app/schemas/user.py:181` | `is_active: bool \| None = None` |
| `user_service.py:272` | `app/services/user_service.py:284` | `update_dict = update_data.model_dump(mode="json", exclude_unset=True)` |
| "l.60" (política) | `app/services/user_access_policy.py:97` | `if "role" in update_dict and actor.role != UserRole.superadmin:` (lee la clave; un superadmin pasa) |
| `a0f621304d75_*.py:44` | igual, `:44` | `sa.Column('role', …, nullable=False)` |
| `app/main.py:101-108` | `app/main.py:100-114` | `@app.exception_handler(IntegrityError)` → `HTTP_409_CONFLICT` (l.107) |

Cadena completa, `UserUpdate`:
- `app/schemas/user.py:166` — `email: LowercaseEmail | None = Field(None, …)`; columna NOT NULL (`app/models/user.py:42`,
  `alembic/versions/a0f621304d75_init_esquema_inicial_limpio.py:39`).
- `app/schemas/user.py:167-172` — `first_name: str | None`; NOT NULL (`models/user.py:44`, migración `:41`).
- `app/schemas/user.py:173-178` — `last_name: str | None`; NOT NULL (`models/user.py:45`, migración `:42`).
- `app/schemas/user.py:179` — `phone: str | None`; columna **nullable** (`models/user.py:46` `Mapped[str | None]`,
  migración `:43`): aquí `null` es legítimo (borra el teléfono).
- `app/schemas/user.py:180` — `role: UserRole | None`; NOT NULL (`models/user.py:47`, migración `:44`).
- `app/schemas/user.py:181` — `is_active: bool | None`; NOT NULL (`models/user.py:51`, migración `:46`).
- `app/schemas/user.py:183-190` — el validador `format_title_case` deja pasar `None` explícitamente (l.187-188).
- `app/services/user_service.py:284` → `:287` (`assert_can_update`) → `:290-291` (`setattr(target_user, key, value)`) →
  `:294-301` (auditoría, solo `if update_dict`) → `:303` (`save_user`).
- `app/services/user_access_policy.py:111-115` — la guarda de ADR-0017/0019 lee `update_dict.get("is_active") is False`;
  `None` no la dispara (de ahí el mutante M6: `not update_dict.get("is_active", True)` sobreviviría).
- `app/repositories/audit_repository.py:14-16` — `add` + `commit()` en la **misma sesión** de la petición: es el primer
  `commit` tras el `setattr`, así que es ese commit el que vuelca el `UPDATE … = NULL` y lanza el `IntegrityError` (leído;
  coherente con la sonda: cero filas de auditoría). Toda la transacción se deshace.

Mismo molde, `ServiceUpdate` (no citado por la fila):
- `app/schemas/service.py:108` `name: str | None` — NOT NULL (`app/models/service.py:34`, migración `:26`).
- `app/schemas/service.py:109` `description: str | None` — **nullable** (`models/service.py:35`, migración `:27`): `null`
  legítimo.
- `app/schemas/service.py:110` `category: ServiceCategory | None` — NOT NULL (`models/service.py:36-38`, migración `:28`).
- `app/schemas/service.py:111` `base_price: Decimal | None` — NOT NULL (`models/service.py:39`, migración `:29`).
- `app/schemas/service.py:112` `max_capacity: int | None` — NOT NULL (`models/service.py:40`, migración `:30`).
- `app/schemas/service.py:113` `is_available: bool | None` — NOT NULL (`models/service.py:41`, migración `:31`).
- `app/schemas/service.py:114` `image_urls: list[HttpUrl] | None` — no es columna; `null` se trata como "no enviado"
  (`tourist_services_service.py:287` `if update_data.image_urls is not None`) pero la auditoría lo registra.
- `app/services/tourist_services_service.py:282-284` — `model_dump(exclude_unset=True, exclude={"image_urls"})` + `setattr`;
  `:287-334` operaciones de CDN (borrar, promover) **antes** de cualquier commit; `:337-345` auditoría (primer commit);
  `:347` `save_service`.

Tests que tocan `None` hoy:
- `tests/test_email_case.py:116-121` — `test_a_patch_with_a_null_email_keeps_it_null` **congela** que `UserUpdate(email=None)`
  es válido y que `model_dump(exclude_unset=True) == {"email": None, …}`. Caerá con cualquier corrección en el schema.
- `tests/test_user_access_policy.py:186-190` (`{"role": None}` propio → `AuthorizationError`) y `:287` (caso `"null"` de
  `test_be36_peer_superadmin_update_other_than_reactivation_is_rejected`) — unitarios de la política; no dependen del
  schema y siguen siendo válidos.
- Ningún test HTTP envía `null` en `PATCH /usuarios/{cedula}` ni en `PUT /servicios/{id}` (grep abajo).

## Medición (sondas)
Copia `git archive HEAD` en el scratchpad, un archivo de sondas `tests/test_probe_be37.py` ejecutado con el Python del
`venv/` y la `conftest.py` del proyecto (SQLite + `StaticPool`; NOT NULL se comporta igual que en Postgres: ambas
lanzan `IntegrityError`). Nada se escribió en el repo. 27 casos, todos ejecutados:

`PATCH /usuarios/{cedula}` (columnas: HTTP · mutación · filas de auditoría nuevas)

| Actor → objetivo | Cuerpo | HTTP | Mutación | Auditoría |
|---|---|---|---|---|
| superadmin → admin | `{"role": null}` | **409** | no | 0 |
| superadmin → turista | `{"role": null}` | **409** | no | 0 |
| superadmin → sí mismo | `{"role": null}` | 403 (guarda de rol propio) | no | 0 |
| admin → turista | `{"role": null}` | 403 (solo superadmin cambia roles) | no | 0 |
| superadmin → admin | `{"role": null, "first_name": "Nuevo"}` | **409** (se pierde también el cambio válido) | no | 0 |
| superadmin → admin | `{"is_active": null}` | **409** | no | 0 |
| superadmin → sí mismo | `{"is_active": null}` | **409** | no | 0 |
| admin → sí mismo | `{"is_active": null}` | **409** | no | 0 |
| admin → turista | `{"is_active": null}` | **409** | no | 0 |
| turista → sí mismo | `{"is_active": null}` | 403 (turista no toca `is_active`) | no | 0 |
| superadmin → admin | `{"email": null}` | **409** | no | 0 |
| admin → turista | `{"email": null}` | **409** | no | 0 |
| turista → sí mismo | `{"email": null}` | **409** | no | 0 |
| superadmin → admin | `{"first_name": null}` | **409** | no | 0 |
| turista → sí mismo | `{"first_name": null}` | **409** | no | 0 |
| superadmin → admin | `{"last_name": null}` | **409** | no | 0 |
| superadmin → admin | `{"phone": null}` | 200 | `phone` → `null` | 1 |
| turista → sí mismo | `{"phone": null}` | 200 | `phone` → `null` | 1 |

`PUT /servicios/{id}` (admin)

| Cuerpo | HTTP | Mutación | Auditoría | CDN |
|---|---|---|---|---|
| `{"name": null}` | **409** | no | 0 | — |
| `{"category": null}` | **409** | no | 0 | — |
| `{"base_price": null}` | **409** | no | 0 | — |
| `{"max_capacity": null}` | **409** | no | 0 | — |
| `{"is_available": null}` | **409** | no | 0 | — |
| `{"description": null}` | 200 | `description` → `null` | 1 (`{"description": null}`) | — |
| `{"image_urls": null}` | 200 | ninguna | **1** (`{"image_urls": null}`, no-op auditado) | — |
| `{"name": null, "image_urls": [<temporal>]}` | **409** | no | 0 | `promote_to_permanent` ×1 **antes** del 409 |
| `{"name": null, "image_urls": []}` sobre un paquete con una imagen permanente | **409** | la fila `service_images` sigue apuntando al blob | 0 | `delete_image(<ese blob>)` ×1 **antes** del 409 |

Lectura: el 409 nunca deja mutación ni auditoría en la base (rollback completo), pero (a) un cambio legítimo enviado
junto al `null` se pierde con un mensaje que habla de "registro que ya existe"; (b) en paquetes, las operaciones de CDN
ya hechas no se deshacen: el último caso deja una imagen rota (fila en BD, blob borrado) y el penúltimo un blob promovido
huérfano.

## Ficheros afectados (mapa completo)
- `app/schemas/user.py` — `UserUpdate` (l.166, 167, 173, 180, 181 admiten `None` sobre columnas NOT NULL; l.179 `phone`
  sobre columna nullable; validador l.183-190).
- `app/schemas/service.py` — `ServiceUpdate` (l.108, 110, 111, 112, 113 sobre NOT NULL; l.109 `description` nullable;
  l.114 `image_urls`; validador l.116-122 deja pasar `None`).
- `app/services/user_service.py` — l.284 conserva las claves con `None`; l.290-291 las aplica; l.294-301 audita.
- `app/services/tourist_services_service.py` — l.282-284 y l.337 conservan `None`; l.287-334 efectos de CDN previos al
  commit.
- `app/services/user_access_policy.py` — l.97, l.102, l.105 leen la clave (`None` entra); l.114 lee el valor (`None` no
  dispara la guarda; M6).
- `app/main.py:100-114` — handler genérico que convierte el `IntegrityError` en 409 con texto de "registro ya existe".
- `app/repositories/audit_repository.py:16` — el `commit` que en la práctica lanza el error (efecto, no causa).
- `app/models/user.py:42,44,45,47,51` y `app/models/service.py:34,36,39,40,41` — columnas NOT NULL (fuente de verdad del
  esquema; `alembic/versions/a0f621304d75_init_esquema_inicial_limpio.py:26,28-31,39,41,42,44,46`).
- `tests/test_email_case.py:116-121` — test que congela `UserUpdate(email=None)` como válido.

## Rincones no mencionados por la fuente
1. **`ServiceUpdate` tiene el mismo molde** en cinco campos (`name`, `category`, `base_price`, `max_capacity`,
   `is_available`): 409 medido en los cinco.
2. **Efectos de CDN fuera de la transacción ante el 409** (`tourist_services_service.py:287-334` antes de `:337`):
   `{"name": null, "image_urls": []}` borra el blob y deja la fila → imagen rota; con una URL temporal, el blob se
   promueve y queda huérfano. Es la misma familia que BE-26 (`B-FUTURO`: CDN antes del commit), con un disparador nuevo
   que BE-37 elimina si el `null` se rechaza en el schema (422 antes de entrar al servicio).
3. **`null` legítimo en columnas nullable**: `phone` (`UserUpdate`) y `description` (`ServiceUpdate`) se borran con `null`
   y devuelven 200. Una corrección global (`exclude_none=True` en el `model_dump`, o "ningún opcional admite `None`")
   rompería ese uso o lo convertiría en no-op silencioso. Si el cliente Flutter borra teléfono o descripción enviando
   `null` no consta en este repo.
4. **`image_urls: null` audita un no-cambio** (`{"image_urls": null}` en `audit_logs`, 200 sin mutación). Vecino de BE-38
   (auditoría de claves, no de cambios), no de este ítem.
5. **Un campo válido junto a un `null` se pierde entero** (`{"role": null, "first_name": "Nuevo"}` → 409, nada se guarda).
6. **El caso propio de `{"role": null}` ya da 403** (BE-02, guarda `user_access_policy.py:102`); el de un tercero sigue en
   409, como anticipaba `docs/deuda/BE-02/plan.md:230`.
7. **`tests/test_email_case.py:116-121` congela el comportamiento a corregir** (ver arriba).
8. Cobertura: `app/schemas/user.py:188` (`return v` con `None` en `format_title_case`) es una de las 3 líneas sin cubrir
   del schema: ningún test HTTP ni unitario manda `first_name`/`last_name` a `None` por el validador.

## Patrones de detección (copiables)
```bash
# Opcionales que admiten None en schemas (filtrar los *Update: user.py:166-181, service.py:108-114)
grep -rnE '^\s+\w+: [^=]*\| None = (None|Field\()' app/schemas/
# Consumidores que conservan claves con None
grep -rn "exclude_unset=True" app/services/
# Columnas NOT NULL (Mapped sin "| None")
grep -nE 'Mapped\[[A-Za-z]+\] = mapped_column' app/models/user.py app/models/service.py
grep -n "nullable=False" alembic/versions/a0f621304d75_init_esquema_inicial_limpio.py
# Handler genérico 409
grep -n -A8 "exception_handler(IntegrityError)" app/main.py
# Guarda que M6 muta (lee el valor)
grep -n 'update_dict.get("is_active") is False' app/services/user_access_policy.py
# Tests que hoy envían o congelan None explícito
grep -rnE '"(role|is_active|email|first_name|last_name|phone|name|description|category|base_price|max_capacity|is_available|image_urls)": ?(None|null)' tests/
grep -n "email=None" tests/test_email_case.py
```
Verificación funcional (para el plan): `PATCH /usuarios/{cedula de un admin}` como superadmin con `{"role": null}` y con
`{"is_active": null}`; `PUT /servicios/{id}` como admin con `{"name": null}` → hoy 409; deben dejar de serlo, sin mutación
ni auditoría ni llamada al CDN.

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `c3b5069` (`git fetch origin` correcto; `merge-base HEAD origin/develop` = `origin/develop`; HEAD de la
  rama `fe3b628`, solo docs por encima de develop)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (Python 3.14.3)

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
- pytest: `731 passed, 8 warnings in 32.17s` (0 failed)
- Cobertura total: **97.65 %** (umbral 92 %)
- ruff format: `68 files already formatted` · ruff check: `All checks passed!` (0)
- mypy: `Success: no issues found in 63 source files` (0)
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas api|cli → services → repositories → models KEPT; Los servicios no
  conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los modelos y los schemas
  no dependen de capas superiores KEPT)
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
- Resolver: que un `null` explícito sobre un campo cuya columna es NOT NULL se rechace en la frontera (422, sin mutación,
  sin auditoría, sin CDN) en **`UserUpdate`** (`email`, `first_name`, `last_name`, `role`, `is_active`) y, por decisión de
  David, también en **`ServiceUpdate`** (`name`, `category`, `base_price`, `max_capacity`, `is_available`; `image_urls`
  a decidir). Si `ServiceUpdate` queda fuera, debe decirlo el plan y nacer fila propia.
- No romper el `null` legítimo de `phone` y `description` (columnas nullable; hoy 200 y borran): descartar
  `exclude_none=True` global sin decisión explícita; un validador por campo o un tipo "opcional no nulo" lo respeta.
- Invertir `tests/test_email_case.py:116-121` (hoy congela `email=None` como válido) y escribir RED HTTP por campo, sobre
  un **tercero** para `role` (el propio ya da 403). Tras el arreglo, M6 deja de ser alcanzable por HTTP; los unitarios
  de la política con `None` (`test_user_access_policy.py:186-190`, `:287`) no dependen del schema y pueden quedarse.
- No tocar: la política (ADR-0017/0018/0019), el handler de `IntegrityError` (sigue siendo la red para UNIQUE, p. ej.
  `tests/test_email_case.py:229-239`), BE-26 (orden del CDN), BE-38 (auditoría de no-ops, incl. `image_urls: null`), A3.
- Riesgos: contrato 409 → 422 en un cliente que hoy pudiera mandar `null` (no verificable desde este repo); que el
  validador de `ServiceUpdate`/`UserUpdate` se aplique por error a los DTO de salida (A9); un `null` en `phone`/
  `description` que deje de borrar sin que nadie lo decida.

## Adenda — decisiones de David antes de planear (17 nov 2026, 12:09, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador toma estas decisiones como dadas; lo demás (fases, tests,
commits, nombres, mecanismo) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada.
Línea base aceptada:** `c3b5069`, compuerta completa en verde (731 passed · 97,65 % · ruff 0 · mypy 0 en 63 archivos ·
4 kept).

Contraste de la sesión Mentor contra el código, sin correcciones de hecho: `app/schemas/user.py:166-181`,
`app/schemas/service.py:108-114`, `app/services/user_service.py:284`, `tests/test_email_case.py:116-121`,
`app/api/routers/service.py:141` (la ruta de paquetes es `PUT`), `app/main.py:78-97` (handler del 422).

### Decisiones (David: "adelante [...] y sí", sobre las siete que propuso la sesión Mentor)

1. **Alcance: `UserUpdate` y `ServiceUpdate`, en el mismo ítem.** `ServiceUpdate` va en fase propia (otro archivo, otro
   dominio) con el mismo mecanismo. Razón: el molde es el mismo y en paquetes el 409 llega después de tocar el CDN
   (rincón 2: `{"name": null, "image_urls": []}` borra el blob y deja la fila).
2. **Severidad: Media** (la fila decía Baja; propuesta de la sesión Mentor por la imagen rota medida).
3. **Un `null` explícito sobre un campo cuya columna es NOT NULL se rechaza en el schema con 422**, sin mutación, sin
   auditoría y sin llamada al CDN. Campos: `email`, `first_name`, `last_name`, `role`, `is_active` (`UserUpdate`);
   `name`, `category`, `base_price`, `max_capacity`, `is_available` (`ServiceUpdate`). **Cambio de código aceptado** en
   tres rechazos que hoy da la política y pasarán a darse antes, en el schema: superadmin sobre sí mismo con
   `{"role": null}`, admin sobre turista con `{"role": null}` y turista sobre sí mismo con `{"is_active": null}`
   (403 → 422). Siguen rechazados. Los guards de ruta (401, 403 por rol) siguen yendo antes que el 422: el plan lo
   congela con un test si no lo está ya.
4. **`phone` y `description` no cambian:** su columna admite vacío y `null` sigue borrando (200). Queda descartado
   `exclude_none=True` global y cualquier mecanismo que convierta ese `null` en no-op.
5. **`image_urls: null` no se toca en este ítem.** Hoy da 200 sin mutación y es el único `null` anómalo que funciona,
   así que el cliente Flutter podría enviarlo; rechazarlo exige mirar antes el cliente. La fila de auditoría que escribe
   ese no-op es de BE-38 (nota en su fila).
6. **Texto del 422:** es texto de usuario final y lo decide David. El planificador mide y pega en el plan, como decisión
   pendiente, el cuerpo real de la respuesta con cada mecanismo candidato (el handler de `app/main.py:78-97` muestra el
   texto del validador si el tipo es `value_error` y uno genérico en otro caso). Los tests no afirman sobre el texto.
7. **ADR-0020, corto, dictado por el plan:** en un DTO de actualización, `null` explícito solo se admite donde la
   columna admite vacío. La viñeta de AGENTS §3 la edita David **después** de la última auditoría y antes de `/pr`.

**Frase de David al aprobar (12:09), literal:** "la idea es que los logs registren lo verdaderamente hecho tanto con
usuarios como con paquetes turísticos; ese es el propósito definitivo de este ítem así haya sido inicialmente
circunscrito solo a la gestión de usuarios". La sesión Mentor la leyó primero como una descripción de BE-38 (que la auditoría registre cambios reales) y lo
preguntó. **Aclarado por David (12:16):** se refería a la decisión 1: está de acuerdo en que también en los paquetes
turísticos se impida que un `null` llegue a la base. No dice nada sobre el alcance de BE-38.

**Confirmado por David (12:13):** el `null` que borra el teléfono se sigue permitiendo
(decisión 4) y `image_urls` no se toca (decisión 5). Añade que un paquete sin imágenes no tiene sentido, pero vale para
el MVP: es trabajo futuro, fila BE-59 (`{"image_urls": []}`, la lista vacía, que no es el `null` de la decisión 5: el
`null` no cambia nada; la lista vacía quita todas las imágenes). Fuera del alcance de este ítem.

### Encargos de medición para el planificador (no son decisiones)

- **Superadmin sobre otro superadmin con `{"is_active": null}`:** ADR-0018 (decisión 1) dice que sigue dando 403; con
  la decisión 3 no llegará a la política y dará 422. La verificación no lo sondeó. Medirlo antes y después; si se
  confirma, el plan dicta un addendum a ADR-0018 que lo aclare (ADR-0009: aclara cómo se cumple; la decisión no cambia).
- **Mecanismo:** uno solo para los dos DTO; no se aplica a ningún DTO de salida (A9, AGENTS §3); la anotación de tipo no
  miente a mypy. Sonda de la sesión Mentor (17 nov; pydantic 2.12.5, `constraints.txt:56`; réplica mínima, sin FastAPI
  ni los schemas del repo): un `field_validator(..., mode="before")` que lanza `ValueError` si recibe `None` da
  ```
  {} -> ok {}
  {'phone': None} -> ok {'phone': None}
  {'first_name': None} -> 422 [(('first_name',), 'value_error')]
  {'first_name': 'Ana', 'is_active': None} -> 422 [(('is_active',), 'value_error')]
  {'is_active': True} -> ok {'is_active': True}
  ```
  y la alternativa `first_name: str = Field(None, ...)` da `string_type` con el `null` explícito y deja el atributo en
  `None` cuando no viene (la anotación `str` mentiría). Es un dato, no un dictado: el planificador elige y mide en una
  copia del repo.
- **Lo que ya se sabe:** `tests/test_email_case.py:116-121` se invierte; el mutante M6 deja de ser alcanzable por HTTP
  y la política no se toca (los unitarios con `None`, `tests/test_user_access_policy.py:186-190` y `:287`, se quedan);
  el handler de `IntegrityError` no se toca.
- **Fuera de alcance:** BE-26 (orden del CDN), BE-38, A3, `image_urls: null`, el cliente Flutter.

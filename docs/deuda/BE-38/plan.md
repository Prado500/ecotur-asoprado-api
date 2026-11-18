# PLAN — BE-38: Auditar solo lo que cambia, con valor anterior y nuevo, y cerrar los huecos de la vista de auditoría

> Fuente: `docs/deuda/BE-38/verificacion.md` (confirmada; adenda 17:24 con decisiones 1–9; re-verificación de los rincones
> 7 y 8; segunda adenda 18:37 con decisiones 10–15). Base: HEAD `6cae238` de `item/be-38`; `git diff --stat 290a942 HEAD
> -- app tests conftest.py pyproject.toml` vacío, así que vale la línea base de la verificación (757 passed · 98,49 % ·
> ruff 0 · mypy 0 en 65 · 4 kept; repetida en la copia: igual). Desde entonces el HEAD es `44b1fce` (apertura del 18
> nov: CONTEXT, PLAN y bitácora); `git diff --stat 6cae238 44b1fce -- app tests docs/adr AGENTS.md` sale vacío, así
> que `6cae238` sigue siendo la base de los comandos de este plan. **Estado: aprobado por David con E0 (18 nov 2026, 11:02),
> precio con la opción (b); ninguna fase ejecutada.** `Aprobado: 18 nov 2026` (esa es la `<FECHA>` de ADR-0021). Enmiendas al final. Redactado el 17 nov; **completado el 18 nov** a petición de la sesión Mentor (cuatro peticiones: nivel de
> dictado y medición de BE-37, R1 dentro del ítem, dos opciones de precio medidas, fases nuevas si hacen falta). Lo que
> cambió respecto del 17 nov, al final de "Análisis del redactor".
> **Qué midió el redactor** (copias `git archive 6cae238` en el scratchpad de la sesión, nunca en el repo; intérprete
> `./venv/Scripts/python.exe` del repo por ruta; `git status` del repo sin cambios propios fuera de
> `docs/deuda/BE-38/`): (1) RED de cada fase: copia con la fase anterior y solo los tests de esta, suite completa; (2)
> GREEN de cada fase con `scripts/check.py` completo; (3) las dos opciones de precio, cada una hasta la fase G, con una
> sonda de lo que muestran `POST`, `PUT`, `GET` y las filas; (4) 30 ejecuciones de mutantes sobre las copias finales (17
> mutantes, suite completa cada una) y M2 sobre la de D; (5) el esquema antes y después del `order_by` de R1; (6) los
> conteos de la Verificación final sobre las dos copias finales; (7) el ancho de cada línea dictada. Salidas literales
> en "Mediciones". Si una cifra no cuadra, el ejecutor se detiene y lo anota en el handoff, sin "arreglar" código para
> que cuadre.

## Resumen para aprobación

Siete fases. (A) El alta de una cuenta administrativa crea primero y audita después: un alta fallida ya no deja una fila
`CREATE` sin cuenta (decisión 15). (B) Dos funciones en `audit_service.py` calculan lo que cambió comparando el valor
validado con la fila; `PATCH /usuarios/{cedula}` audita solo eso como `{campo: {"old", "new"}}` y un no-cambio no deja
fila. (C) Verificar el correo deja un `UPDATE` de `is_active` con la propia cuenta como autora y deja de activar cuentas
borradas (404). (D) `PUT /servicios/{id}` y activar/desactivar un paquete, igual que B; las imágenes de un paquete se
cargan por `id` (R1 del 17 nov, ahora dentro). (E) **El precio se lee con la escala de su columna; la opción la elige
David** (abajo). (F) El alta de un paquete audita lo que quedó guardado (BE-61). (G) ADR-0021 y los comentarios de
`app/models/audit.py`. Todo medido en copia: compuerta verde tras cada fase; al final 793 passed · 98,68 % con la opción
(a) o 797 passed · 98,69 % con la (b). **Riesgo principal:** contrato. Cambia la forma de `changes` en las filas
`UPDATE` que devuelve `GET /auditoria/`, y la tabla queda con dos formatos (las filas viejas no se migran). **David
comprueba en el cliente Flutter qué hace el panel con `changes` antes de mezclar** (paso humano de la Verificación
final). **No se toca:** el `commit()` de los repositorios (A3), el enlace de un solo uso y V4 (BE-50), la longitud del
correo (BE-54), el orden del CDN (BE-26), la lista vacía (BE-59), el autor en paquetes (BE-48), la política de acceso,
los routers, `app/schemas/user.py`, `app/schemas/audit.py`, `GET /auditoria/` y el esquema de la base.

**Decisiones pendientes para David al aprobar:**

1. **Precio (fase E) — PENDIENTE; el plan no elige.** Objetivo de la sesión Mentor: que `old`, `new` y las respuestas de
   `POST`, `PUT` y `GET` muestren la misma grafía. Medido en copia con las fases A–G de cada opción (sonda: alta con
   `"base_price": 50000`, luego `PUT {"base_price": 60000}`, luego `GET /servicios/`; salida literal en "Mediciones", 3):

   | Qué se lee | Hoy (`6cae238`) | (a) `populate_existing` en `create_service` | (b) dos decimales al entrar, en el schema |
   |---|---|---|---|
   | `POST /servicios/` → `base_price` | `'50000'` | `'50000.00'` | `'50000.00'` |
   | fila `CREATE` → `base_price` | `'50000'` | `'50000.00'` | `'50000.00'` |
   | `PUT /servicios/{id}` → `base_price` | `'60000'` | **`'60000'`** | `'60000.00'` |
   | fila `UPDATE` → `changes` | `{'base_price': '60000'}` | **`{'old': '50000.00', 'new': '60000'}`** | `{'old': '50000.00', 'new': '60000.00'}` |
   | `GET /servicios/` → `base_price` | `'60000.00'` | `'60000.00'` | `'60000.00'` |
   | ¿Cumple el objetivo? | no | 3 de 5 (falla `PUT` y `new`) | 5 de 5 |

   | | (a) `populate_existing` | (b) dos decimales al entrar |
   |---|---|---|
   | Archivos de la fase E | `app/repositories/service_repository.py` (+4 −1), `tests/test_services.py` (+29) | `app/schemas/service.py` (+15), `tests/test_services.py` (+66 −1) |
   | Tests de la fase E | 3 casos nuevos (2 RED) | 7 casos nuevos (4 RED) y una línea reescrita del test de precio de D (RED) |
   | Suite final | 793 passed · 98,68 % | 797 passed · 98,69 % |
   | Contrato | `POST` responde `"50000.00"` (como `GET`); `PUT` sigue respondiendo lo enviado | `POST` y `PUT` responden `"…00"`; `"50000.000"` y `"5E+4"`, que hoy pasan tal cual, se guardan y responden `"50000.00"`; un tercer decimal sigue siendo 422 (`decimal_max_places`); OpenAPI idéntico (md5 medido) |
   | Riesgo | `populate_existing` borra cambios pendientes de la instancia: no hay (se llama tras el `commit()`); queda abierta la grafía de `PUT` y `new` (R3) | un validador más en cada DTO de entrada (como `format_service_name`, que ya está en los dos); ningún DTO de salida cambia (A9) |
   | Mutantes propios | M8a: muere | M8b, M8c, M13: mueren |
   | Fases que cambian | solo E (y el punto 8 de ADR-0021) | E, que reescribe una línea del test de precio de D (`"new": "60000.00"`), y el punto 8 de ADR-0021 |

   Con cualquiera de las dos, las fases A, B, C, D, F y G no cambian (salvo el punto 8 del ADR y su consecuencia, que el
   Anexo G dicta para cada opción) y la fila `CREATE` de F lleva `"50000.00"`. Sin la fase E, la fila `CREATE` llevaría
   `"50000"` (medido: "Mediciones", 3, `probe_a_nopop`).
2. **Las propuestas abiertas de la primera adenda, adoptadas tal cual:** misma columna `changes` sin migración; `CREATE`
   en forma de valores, sin `old`/`new` (ADR-0015 no se supersede); filas viejas sin migrar, distinguibles por forma
   (punto 7 de ADR-0021); `image_urls` como lista ordenada de URL definitivas, no como filas.
3. **Excepción declarada a AGENTS §5** (fases A y C): dobles `autospec` de `UserRepository` en `tests/test_user_service.py`,
   práctica ya existente en ese archivo. La carrera C2/C3 y el fallo C4 no se reproducen por HTTP sin sustituir el
   repositorio (conclusión de la re-verificación).
4. **R1 dentro del ítem (petición de la sesión Mentor):** `order_by=lambda: ServiceImage.id` en `TouristService.images`,
   en la fase D, con un test sobre el mapeo. No exige migración ni cambia el esquema (medido; respuesta sobre `alembic
   check` en "Análisis").
5. **Textos de ADR-0021** (Anexo G) y de los siete commits (dictados en cada fase).

## Objetivo y decisiones bloqueadas

Que la vista de auditoría muestre solo cambios reales, con su valor anterior y el nuevo, que ninguna mutación de cuenta
quede sin fila y que ninguna fila describa algo que no ocurrió.

1. Alcance: `PATCH /usuarios/{cedula}`, `PUT /servicios/{id}`, `PATCH /servicios/{id}/activar|desactivar`, verificación
   de correo, alta administrativa y alta de paquete (decisiones 1, 7, 9).
2. Un no-cambio responde como hoy (200) y no escribe fila; si cambia una parte, solo esa parte (decisiones 2, 12).
3. `UPDATE`: `{campo: {"old": <anterior>, "new": <nuevo>}}` en la misma columna, valores en forma JSON (decisión 3).
4. "Cambió" = valor validado `!=` valor de la columna, en Python (decisión 5).
5. El cálculo va **después** de `assert_can_update`, que sigue recibiendo el `update_dict` completo (condición 1).
6. El valor anterior se lee antes de cualquier `setattr` o `images.clear()` (condición 2).
7. Activación por correo: `UPDATE` con `{"is_active": {"old": false, "new": true}}`, `entity_id` = `performed_by` =
   cédula de la cuenta, sin `source`; ignora cuentas borradas (decisiones 10, 11, 13).
8. Alta administrativa: alta → auditoría, `entity_id=saved_user.cedula`; sin tocar `audit_repository.py:16` (decisión 15).
9. `CREATE` en forma de valores; `SOFT_DELETE`, `RECOVER`, `ACTIVATE`, `DEACTIVATE` sin `changes` (adenda 1, propuesta 2).
10. Las imágenes de un paquete se cargan por `id` (R1); sin migración: el esquema no cambia.
11. El precio, según la opción que elija David (decisión pendiente 1); ninguna otra fase depende de la elección salvo el
    punto 8 del ADR (y la línea del test de precio de D que la opción (b) reescribe en E).

## Análisis del redactor

**Contraste con el código (`6cae238`).** Todo lo que cita la verificación sigue en su sitio: `app/services/user_service.py`
:141 (`activate_user`), :284 (`model_dump(mode="json", exclude_unset=True)`), :287 (`assert_can_update`), :290-291
(`setattr`), :294-301 (`if update_dict:`), :425-433 (auditoría antes de `create_user`);
`app/services/tourist_services_service.py` :70-76 (`CREATE` con el cuerpo), :128-137 (toggle sin mirar el estado), :282-284,
:312-334, :337-345 (`payload_changes`); `app/repositories/user_repository.py:54-65` (`activate_user`, sin `deleted_at`);
`app/models/service.py:47-49` (`images` sin `order_by`); `app/models/audit.py:43` (comentario `old_values`) y :35
(comentario en español que ADR-0010 dejó "para el próximo PR que toque el archivo").

**Qué cambia y por qué así.** El defecto tiene un solo molde (auditar el cuerpo en vez de la diferencia), así que nace
una sola pieza: `changed_fields(entity, new_values)` y `audit_value(value)` como **funciones de módulo** en
`app/services/audit_service.py`. No son métodos de `AuditService` porque los tests unitarios usan
`create_autospec(AuditService)`, que las reemplazaría por dobles y escondería el cálculo. `audit_value` usa
`pydantic.TypeAdapter(Any)` (pydantic ya está en `pyproject.toml`; import-linter: 4 kept, medido): da `Decimal` y enums
como texto, como `mode="json"` hoy. En `PATCH /usuarios` el `update_dict` con `mode="json"` se queda para la política y el
`setattr` (sin cambio); `changed_fields` recibe el volcado en modo Python, porque `"50000"` y `"50000.00"` son textos
distintos pero el mismo `Decimal`. La activación por correo reutiliza `UserRepository.get_non_deleted_user_by_email` (ya
filtra `deleted_at`, cierra V5) y `save_user`; `activate_user` queda sin llamadores y se borra.

**R1 y `alembic check` (petición 2 de la sesión Mentor).** `order_by=lambda: ServiceImage.id` en el `relationship()` es
configuración del mapeador: cambia la consulta que carga las imágenes (`... WHERE service_images.service_id IN (?) ORDER
BY service_images.id`, medido) y no el esquema. **No exige `alembic check` por ADR-0010, punto 7**, y está comprobado, no
supuesto: (1) el DDL de PostgreSQL de las cuatro tablas e índices, compilado desde `Base.metadata` antes y después, es
idéntico byte a byte (57 líneas, md5 `11789bcfa202996016a9d9244ac6e3e5` en los dos); (2) `alembic.autogenerate.
compare_metadata` — la comparación que ejecuta `alembic check` — entre una base creada con los modelos de antes y los
modelos de después da `[]`; (3) `tests/test_models_schema.py` (que congela el esquema con literales) sigue en verde.
`alembic check` contra PostgreSQL **no se pudo ejecutar**: Docker Desktop no está arrancado en esta máquina (`failed to
connect to the docker API`) y las migraciones usan SQL propio de PostgreSQL (`ALTER TYPE`, `::text`), así que no corren
en SQLite. Si David quiere la prueba literal, `alembic check` antes y después de la fase D contra su base local debe dar
la misma salida; es opcional, no condición del plan. Por qué una `lambda` y no un texto: SQLAlchemy evalúa con `eval()`
un `order_by` de texto; la `lambda` se resuelve igual al configurar el mapeador y sin `eval()` (Referencias), y ADR-0010,
punto 5, ya pide no pasar destinos como texto. Por qué importa: la igualdad "misma lista" de D compara `old` (orden
de la base) con `new` (orden enviado); sin `ORDER BY`, PostgreSQL puede devolver otro orden y una lista reenviada se
auditaría como cambio. En SQLite el orden ya es el de `id`, así que el RED de R1 es el test del mapeo
(`test_service_images_load_in_stored_order`), no uno de HTTP; el comportamiento lo congelan, en SQLite, los dos tests de
lista reenviada y reordenada (D).

**Precio (petición 3).** Dos opciones medidas en "Decisiones pendientes", punto 1. Mecánica: (a) `create_service` ya
relee la fila tras el `commit()`, pero sin `populate_existing` el mapa de identidad conserva el `Decimal("50000")` que
puso el servicio; con la opción, los escalares se recargan de la base. `save_service` hace lo mismo y por eso `PUT`
responde lo enviado (R3); (a) no lo toca. (b) un `field_validator("base_price")` en `ServiceBase` y otro en
`ServiceUpdate` hace `v.quantize(Decimal("0.01"))` **después** de las restricciones del `Field`, así que un tercer
decimal sigue dando 422 y nada se redondea (lo congela `test_be38_schema_keeps_rejecting_a_third_decimal`; M13, el mismo
validador en modo `before`, redondearía y muere). Con (b) el servicio recibe ya `Decimal("60000.00")`, y `POST`, `PUT`,
la fila `CREATE`, `old` y `new` leen igual sin tocar repositorios. Ninguna de las dos toca la base ni el OpenAPI.

**Orden y dependencias.** A (independiente) → B (crea las funciones) → C (usa `changed_fields`; su test V4 lee la fila
de B) → D (usa las funciones; R1) → E (precio; con (b) reescribe una línea del test de precio de D) → F (usa
`audit_value`; su fila `CREATE` lleva `"50000.00"` solo si E está) → G (documenta lo ya hecho; el comentario del modelo
solo es cierto tras B–F). Las letras A–D son las del plan del 17 nov (la sesión Mentor pidió R1 "en la fase D"); el
precio entra como E, junto a BE-61, donde el 17 nov estaba `populate_existing`. Entre A y G el código cita ADR-0021
antes de que el archivo exista; G lo crea en el mismo PR (orden del plan del 17 nov, revisado por la sesión Mentor).
Cada fase deja la compuerta en verde (medido).

**Tamaño:** A = 50 líneas (+45 −5; la más pequeña de las fases que no dependen de la decisión); E(a) = 34 líneas, más
pequeña que A: no se adelanta porque su contenido depende de la decisión pendiente 1.

**Tests que congelan comportamiento** (medido en las copias RED; lista literal en cada fase): caen exactamente los 10
tests que congelaban el formato viejo en usuarios (`test_user_access_policy.py` l.692, 720, 961, 1008, 1053, 1096, 1199,
1308 y `test_user_update_null.py::test_be37_null_on_phone_still_clears_it` ×2), los 2 de paquetes
(`test_be37_null_on_description_still_clears_it`, `test_be37_null_on_image_urls_still_keeps_the_images`), el de
`test_create_package_promotes_temporal_url` (F) y los dos unitarios de verificación de `test_user_service.py` que
fijaban `activate_user` (`test_verify_email_activates_account`, `test_verify_email_missing_user_raises_not_found`). Las
cuatro `user_repo.activate_user.assert_not_awaited()` de los tests de token pasan a `get_non_deleted_user_by_email`:
verdes antes y después (sin el cambio, `activate_user` dejaría de existir en el doble `autospec` y fallarían por
`AttributeError`). Con la opción (b), E reescribe el test de precio de D (cae en su RED).
`test_create_administrative_account_provisions_admin` se ajusta (el doble devuelve el usuario) y sigue verde antes y
después. `tests/test_token_failure_paths.py` **no cambia** (sus casos fallan antes del repositorio; verde en todas las
copias). Los 20 tests con `audits == []` de rechazos siguen verdes. `test_deactivate_and_activate_package` (cambio real
de estado) sigue verde con el toggle nuevo.

**Riesgos.** (1) Contrato de `GET /auditoria/` (paso de David). (2) Filtrar antes de la política convertiría U2/U13 y la
excepción de ADR-0018 con claves extra en 200: lo congelan `test_be02_superadmin_self_role_noop_returns_403` (existe) y
dos guardas nuevas de B (M1 muere). (3) El hueco inverso de A3 (mutación sin fila si falla la auditoría) sigue; lo
declara ADR-0021. (4) M2 (comparar en forma JSON en vez de Python) **sobrevive con la opción (b)**: con el precio ya
normalizado al entrar, ningún valor alcanzable por HTTP distingue las dos comparaciones; con (a) muere. Se dicta la
comparación en Python porque lo decidió David (decisión 5) y porque es la que no depende de que el schema normalice.
(5) Los avisos de la suite no cambian (25, como la línea base).

**Qué NO se toca.** `user_access_policy.py`, `app/schemas/user.py`, `app/schemas/audit.py`, `app/schemas/partial_update.py`,
`app/api/*`, `app/main.py`, `audit_repository.py`, `superadmin_bootstrap.py`, `user_service.py` fuera de los tres métodos
citados, `register_tourist`, borrado y recuperación, el bucle de `setattr` (sigue aplicando todas las claves enviadas:
inocuo), `save_service`, `alembic/`, `tests/conftest.py`, `conftest.py`, `tests/test_route_guards.py`,
`tests/test_token_failure_paths.py`, `tests/test_superadmin_bootstrap.py`. Con (a) tampoco `app/schemas/service.py`; con
(b) tampoco `app/repositories/service_repository.py`.

**Mutantes** (copias finales de cada opción; suite completa por mutante; salida literal en "Mediciones", 4; el
ejecutor de cada fase repite los suyos sobre su fase). M2 se midió además sobre la copia de la fase D: `1 failed, 788
passed` (`[price-same-value]`).

| Id | Archivo | Mutación | (a) | (b) | Lo matan |
|---|---|---|---|---|---|
| M1 | `user_service.py` | `changes` antes de la política, y la política solo con las claves que cambian | 5 failed | 5 failed | las dos guardas de B, `test_b2_admin_self_role_noop_returns_403`, `test_be02_superadmin_self_role_noop_returns_403`, `test_be36_superadmin_reactivating_active_peer_returns_200` |
| M2 | `audit_service.py` | comparar en forma JSON: `audit_value(old) != audit_value(new)` | 1 failed | **797 passed (vive)** | (a): `…unchanged_package_update…[price-same-value]`; (b): ninguno, equivalente en lo alcanzable (riesgo 4, R7) |
| M3u | `user_service.py` | `changed_fields` después del bucle `setattr` | 9 failed | 9 failed | U7, los cinco de formato de la política, `phone` ×2, V4 |
| M3p | `tourist_services_service.py` | ídem en paquetes | 3 failed | 3 failed | P7, precio, `description` |
| M4 | `user_service.py` | `log_transaction` (con `user_data.cedula`) antes de `create_user` | 2 failed | 2 failed | los dos ids del test de A |
| M5 | `user_repository.py` | `get_non_deleted_user_by_email` sin `deleted_at.is_(None)` | 3 failed | 3 failed | V5, `test_self_soft_delete_keeps_row_and_blocks_login`, `test_token_for_soft_deleted_active_user_returns_401` |
| M6 | `tourist_services_service.py` | `if service.is_available != is_available:` → `if True:` | 2 failed | 2 failed | estado sin cambio ×2 |
| M7 | `tourist_services_service.py` | `"new": definitive_urls` → `"new": raw_urls` | 1 failed | 1 failed | P6 |
| M8a | `service_repository.py` | sin `populate_existing` (solo opción a) | 3 failed | — | precio de alta ×2 (`integer`, `one-decimal`), fila `CREATE` |
| M8b | `schemas/service.py` | sin el validador de `ServiceBase` (solo opción b) | — | 3 failed | precio de alta ×2, fila `CREATE` |
| M8c | `schemas/service.py` | sin el validador de `ServiceUpdate` (solo opción b) | — | 3 failed | precio de `PUT` ×2 (`integer`, `one-decimal`), precio auditado de D |
| M9 | `tourist_services_service.py` | comparar imágenes como conjuntos | 1 failed | 1 failed | lista reordenada |
| M10 | `models/service.py` | sin `order_by` (R1) | 1 failed | 1 failed | `test_service_images_load_in_stored_order` |
| M11 | `user_service.py` | la activación guarda y audita siempre | 2 failed | 2 failed | V3 unitario y HTTP |
| M12 | `user_service.py` | `performed_by=email` en la activación | 3 failed | 3 failed | V1 unitario y HTTP, V4 |
| M13 | `schemas/service.py` | el validador en modo `before` (redondea antes de comprobar decimales; solo opción b) | — | 1 failed | `test_be38_schema_keeps_rejecting_a_third_decimal` |
| M14 | `tourist_services_service.py` | `CREATE` con `image_urls = raw_urls` | 2 failed | 2 failed | fila `CREATE` y BE-61 |

29 de 30 ejecuciones matan su mutante; la que vive (M2 con (b)) está explicada.

**Qué cambió el 18 nov respecto del plan del 17 nov.** (1) Nivel de dictado de BE-37: anexos con el diff literal de cada
fase y el archivo nuevo completo; RED y GREEN medidos por fase; compuerta completa en las dos copias finales; mutantes
ejecutados; conteos de la Verificación final medidos; anchos medidos. (2) R1 entra en la fase D (`order_by` y su test);
deja de ser residual. (3) El precio pasa a ser la fase E, con dos opciones medidas y pendiente de David; el
`populate_existing` sale de la fase de BE-61 (si David elige (a), vive en E). (4) A–D conservan su letra; la E del 17
nov (BE-61) es F y la F (ADR) es G. (5) Tests nuevos frente al 17 nov: `test_be38_reordered_image_list_audits_the_
new_order` (la lista es ordenada: mata M9) y el de R1; los casos de precio de E; el test de V4 compara también
`performed_by`. (6) Al medir se corrigieron tres errores del dictado del 17 nov: el comentario de `populate_existing`
pasaba de 100 columnas; el test de BE-61 indexaba `changes`, que mypy rechaza (`dict[str, Any] | None`; la compuerta
corre mypy también sobre `tests/`); y `RED esperado: 14 failed` de paquetes pasa a 16 con los dos tests nuevos. (7) En G,
el comentario en español de `app/models/audit.py:35` se traduce (obligación de ADR-0010). (8) La Verificación final usa
`git grep` (solo archivos versionados): `grep -rn` sobre `app/` en el repo cuenta también los `.pyc` de `__pycache__`.

## Regla de alcance

Sí: lo que lista "Objetivo" y los tests que congelan el formato viejo. No: todo lo de "Qué NO se toca", BE-48 (los tests
de paquetes no afirman `performed_by`), BE-50 (docstrings de "single-use" incluidos), `AuditLogCreate` (P3),
`docs/backlog.md`, `docs/CONTEXT.md`, `AGENTS.md`. Hallazgos nuevos → handoff, nunca al código.
**Regla de grep:** ningún docstring ni comentario de `app/` contiene `changed_fields(`, `log_transaction(` ni
`if changes:` (cuentan en la Verificación final; medido: 0).

## Fases

| Fase | Qué | Archivos | `numstat` (medido) | Suite tras la fase (medido) |
|---|---|---|---|---|
| A | Alta administrativa: crear antes de auditar | 2 | +45 −5 | 759 passed · 98,50 % |
| B | `changed_fields`/`audit_value`; `PATCH /usuarios` | 5 | +229 −12 | 769 passed · 98,59 % |
| C | Verificación de correo | 4 | +129 −27 | 773 passed · 98,58 % |
| D | `PUT /servicios`, activar/desactivar, R1 | 4 | +265 −19 | 789 passed · 98,68 % |
| E | Precio: (a) `populate_existing` · (b) dos decimales al entrar | 2 | (a) +33 −1 · (b) +81 −1 | (a) 792 · 98,68 % · (b) 796 · 98,69 % |
| F | BE-61: el alta de un paquete audita lo guardado | 2 | +53 −5 | (a) 793 · 98,68 % · (b) 797 · 98,69 % |
| G | ADR-0021 y comentarios de `app/models/audit.py` | 2 | +88 −4 | (a) 793 · 98,68 % · (b) 797 · 98,69 % |

Todas las compuertas: `ruff format --check` (70 archivos en A; 71 desde B), ruff 0, mypy 0 (65 archivos en A; 66 desde
B), 4 kept, exit 0. Literal en "Mediciones", 2.

### Fase A — Alta administrativa: crear primero, auditar después (la más pequeña)
- **Archivos (2):** `app/services/user_service.py`, `tests/test_user_service.py`. Dominio: cuentas de usuario (alta
  administrativa). `numstat`: `6 3` y `39 2`. Texto literal: Anexo A.
- **Cambios exactos:** en `create_administrative_account`, `saved_user = await self.user_repo.create_user(new_user)`
  antes de `log_transaction`, que pasa a `entity_id=saved_user.cedula`; `return saved_user`. Docstring: una frase (Anexo
  A). Test: import de `IntegrityError` y `OperationalError`; `test_create_administrative_account_provisions_admin` con
  `create_user.side_effect = lambda user: user` y `assert result is created_user`; test nuevo parametrizado.
- **Tests (RED primero):** `test_create_administrative_account_insert_failure_writes_no_audit_row`, ids
  `race-on-unique-index` (`IntegrityError`, C2/C3) y `database-failure` (`OperationalError`, C4): `create_user` lanza →
  `pytest.raises(type(error))`; `create_user.assert_awaited_once_with(<el usuario construido>)` y
  `log_transaction.assert_not_awaited()`. **RED medido** (copia `6cae238` + solo los tests): suite `2 failed, 757
  passed`; fallan exactamente los dos ids.
- **Criterio de aceptación:** compuerta exit 0, `759 passed`, cobertura 98,50 % (≥ 98,49 %); M4 muere.
- **Fuera de alcance:** `register_tourist`, bootstrap, `audit_repository.py` (A3), BE-54.
- **Commit:** 
  ```
  fix(users): audit an administrative account after creating it

  The CREATE row of an administrative account was committed before the
  insert, so a race on the unique indexes (409) or a database failure
  (500) left a row for an account that does not exist, once on the
  cedula of another account (BE-38, C2 to C4, measured).

  Create first and audit the saved cedula, as register_tourist and the
  bootstrap already do. A3 stays out: if the audit write fails, the
  account exists without its row (ADR-0021).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Calcular lo que cambió; `PATCH /usuarios/{cedula}`
- **Archivos (5):** `app/services/audit_service.py`, `app/services/user_service.py`, `tests/test_user_update_audit.py`
  (nuevo), `tests/test_user_access_policy.py`, `tests/test_user_update_null.py`. Dominio: auditoría de cuentas.
  `numstat`: `44 0`, `10 5`, `152 0`, `22 6`, `1 1`. Texto literal: Anexo B.
- **Cambios exactos:** `audit_service.py`: `_JSON_VALUE: TypeAdapter[Any] = TypeAdapter(Any)`, `audit_value` y
  `changed_fields` (funciones de módulo, docstrings Google con ADR-0021). `user_service.update_user_account`: tras
  `assert_can_update` (sin cambios) y antes del bucle `setattr`, `changes = changed_fields(target_user,
  update_data.model_dump(exclude_unset=True))`; `if update_dict:` → `if changes:` y `changes=changes`; comentarios de
  pasos renumerados (3 → 5); dos líneas de docstring.
- **Tests (RED primero):** `tests/test_user_update_audit.py` (fábricas centrales; código, cuerpo, estado refrescado y
  filas de `AuditLog`): `test_be38_unchanged_user_update_returns_200_without_audit_row` ×6 (`role-same`,
  `first-name-same`, `first-name-normalized`, `phone-null-already-null`, `is-active-same`, `four-keys-same`),
  `test_be38_email_in_another_case_is_unchanged` (U9), `test_be38_partial_change_audits_only_the_changed_field` (U7) y dos
  guardas verdes desde el inicio (matan M1): `test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403` y
  `test_be38_admin_self_role_with_unchanged_value_returns_403` (U13). Reescritos: los 8 de `test_user_access_policy.py` y
  el de `test_user_update_null.py` (Anexo B). **RED medido** (copia con A + solo los tests): suite `18 failed, 751
  passed`: 8 de `test_user_update_audit.py` (las dos guardas pasan), 8 de `test_user_access_policy.py`, 2 de
  `test_user_update_null.py` (lista en "Mediciones", 1).
- **Criterio de aceptación:** compuerta exit 0, `769 passed`, 98,59 %; M1 y M3u mueren.
- **Fuera de alcance:** política, schemas, router, paquetes, activación, `GET /auditoria/`.
- **Commit:** 
  ```
  fix(audit)!: audit only changed user fields, as old and new values

  PATCH /usuarios/{cedula} audited the validated body, so a key resent
  with its current value wrote an UPDATE row for nothing (BE-38, U1 to
  U13, measured).

  - app/services/audit_service.py: changed_fields compares each
    validated value with the stored one as Python values; audit_value
    dumps old and new to their JSON form.
  - app/services/user_service.py: the comparison runs after the access
    policy, which still reads every key sent (BE-02, ADR-0018), and
    before any setattr. A request that changes nothing writes no row; a
    partial change audits only the changed field.
  - tests: the no-op cases, two guards that keep the policy deciding on
    the keys sent, and the ten tests that froze the old shape.

  BREAKING CHANGE: user UPDATE rows in GET /auditoria/ now carry
  {field: {"old": ..., "new": ...}}; rows written before keep the old
  shape.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase C — La activación por correo deja fila y no alcanza a cuentas borradas
- **Archivos (4):** `app/services/user_service.py`, `app/repositories/user_repository.py`, `tests/test_user_service.py`,
  `tests/test_auth.py`. Dominio: verificación de correo. `numstat`: `19 3`, `0 13`, `43 11`, `67 0`. Texto: Anexo C.
- **Cambios exactos:** en `verify_email_account`, el bloque `activate_user` se sustituye por la búsqueda con
  `get_non_deleted_user_by_email`, `NotFoundError` si es `None`, `changes = changed_fields(user, {"is_active": True})` y,
  si hay cambio, `user.is_active = True`, `save_user(user)` y `log_transaction(UPDATE, entity_id=user.cedula,
  performed_by=user.cedula, changes=changes)`; docstring ampliada. Se borra `UserRepository.activate_user` (único
  llamador).
- **Tests (RED primero):** `test_user_service.py`: `test_verify_email_activates_account` reescrito (afirma búsqueda,
  `save_user` y `log_transaction` con los cinco argumentos), nuevo `test_verify_email_on_active_account_writes_nothing`,
  `test_verify_email_missing_user_raises_not_found` con `return_value = None` y tres afirmaciones de llamadas, y las
  cuatro `activate_user.assert_not_awaited()` → `get_non_deleted_user_by_email.assert_not_awaited()`. `test_auth.py`:
  `test_verify_email_endpoint_activates_account` afirma la fila; nuevos `test_be38_verify_email_on_active_account_returns_
  200_without_audit_row` (V3, guarda), `test_be38_verify_email_on_deleted_account_returns_404_without_mutation` (V5) y
  `test_be38_verify_email_after_admin_deactivation_writes_an_audit_row` (V4; la reactivación misma es BE-50). **RED
  medido** (copia con A y B + solo los tests): suite `6 failed, 767 passed`: 3 unitarios y 3 HTTP; V3 y los cuatro de
  token, verdes.
- **Criterio de aceptación:** compuerta exit 0, `773 passed`, 98,58 %; `activate_user` 0 en `app/` y `tests/` (comando
  3); M5, M11 y M12 mueren.
- **Fuera de alcance:** BE-50 (segundo clic, enlace de un solo uso, que V4 ocurra), docstrings "single-use", registro.
- **Commit:** 
  ```
  fix(auth): audit email verification and skip deleted accounts

  Verifying an email activated the account with no audit row, and
  activate_user matched by email only, so a link reactivated a
  soft-deleted account (BE-38, V1 to V5, measured).

  The service now loads the non-deleted account and, if it is inactive,
  writes the same UPDATE of is_active an admin would, with the account
  as its own author; an account already active writes nothing. A
  deleted account answers 404, like an email without account.
  activate_user loses its only caller and is removed.

  The link reactivating an account an admin deactivated is BE-50; it is
  now visible in the trail.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase D — `PUT /servicios/{id}`, activar/desactivar sin cambio y el orden de las imágenes (R1)
- **Archivos (4):** `app/services/tourist_services_service.py`, `app/models/service.py`, `tests/test_services.py`,
  `tests/test_models_schema.py`. Dominio: auditoría de paquetes. `numstat`: `27 16`, `5 1`, `225 2`, `8 0`. Texto: Anexo D.
- **Cambios exactos:** `update_package_details`: `changes = changed_fields(service, update_dict)` antes del bucle
  `setattr`; `old_urls = [image.image_url for image in service.images]` antes de `images.clear()`; tras el `append`, `if
  definitive_urls != old_urls: changes["image_urls"] = {"old": old_urls, "new": definitive_urls}`; el bloque
  `payload_changes` pasa a `if changes:` con `changes=changes`. `toggle_package_status`: `estado` primero; mutación,
  `save_service` y auditoría dentro de `if service.is_available != is_available:`; la respuesta no cambia. Docstrings de
  los dos métodos. `app/models/service.py`: `order_by=lambda: ServiceImage.id` y dos líneas de docstring (R1).
- **Tests (RED primero):** sección al final de `tests/test_services.py` con `_audit_rows` y `_columns`:
  `test_be38_unchanged_package_update_returns_200_without_audit_row` ×6 (`name-same`, `name-normalized`,
  `price-same-value`, `available-same`, `description-null-already-null`, `empty-images-without-images`),
  `test_be38_resent_image_list_returns_200_without_audit_row` (P5, dos imágenes),
  `test_be38_reordered_image_list_audits_the_new_order` (mata M9), `test_be38_partial_package_change_audits_only_the_
  changed_field` (P7), `test_be38_price_change_audits_old_and_new_values` (`{"old": "50000.00", "new": "60000"}`: la
  grafía de hoy; la opción (b) de E reescribe esta línea), `test_be38_image_change_audits_the_stored_urls` (P6),
  `test_be38_status_route_without_change_returns_200_without_audit_row` ×2 y, guardas,
  `test_be38_status_route_with_change_audits_the_action` ×2. `tests/test_models_schema.py`:
  `test_service_images_load_in_stored_order` (R1). Reescritos: `test_be37_null_on_description_still_clears_it` (formato)
  y `test_be37_null_on_image_urls_still_keeps_the_images` (añade `audits == []`). Ningún test afirma `performed_by`
  (BE-48). **RED medido** (copia con A–C + solo los tests): suite `16 failed, 773 passed` (lista en "Mediciones", 1);
  las dos guardas de estado pasan.
- **Criterio de aceptación:** compuerta exit 0, `789 passed`, 98,68 %; M2, M3p, M6, M7, M9 y M10 mueren (M2, con la
  opción (b), deja de morir tras E: riesgo 4).
- **Fuera de alcance:** el precio (E), el alta (F), BE-26, BE-59, la recreación de filas de P5 (R2), BE-48,
  `save_service`.
- **Commit:** 
  ```
  fix(audit)!: audit only changed package fields, as old and new values

  PUT /servicios/{id} audited the body: same values, a null image list
  and the temporal URLs sent all wrote UPDATE rows that did not describe
  the package, and the status routes wrote ACTIVATE or DEACTIVATE for a
  package already so (BE-38, P1 to P13, measured).

  - app/services/tourist_services_service.py: scalars go through
    changed_fields; images are compared as the ordered list of stored
    URLs, the promoted list as new; the status routes save and audit
    only a real change.
  - app/models/service.py: images load ordered by id, so the same list
    reads the same on PostgreSQL as on SQLite. ORM only: the schema
    does not change (metadata compared, measured).
  - tests: no-op, partial, price, image and status cases; the two BE-37
    tests that froze the old shape.

  BREAKING CHANGE: package UPDATE rows in GET /auditoria/ now carry
  {field: {"old": ..., "new": ...}}.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase E — El precio con la escala de su columna (DECISIÓN PENDIENTE: el ejecutor aplica solo la opción aprobada)
- **Archivos (2).** Dominio: precio de paquetes. Texto literal: Anexo E(a) o Anexo E(b).
  - **(a)** `app/repositories/service_repository.py` (`4 1`) y `tests/test_services.py` (`29 0`).
  - **(b)** `app/schemas/service.py` (`15 0`) y `tests/test_services.py` (`66 1`).
- **Cambios exactos:** (a) `.execution_options(populate_existing=True)` en el `select` de `create_service` y dos líneas
  más del comentario que ya tiene. (b) `_CENTS = Decimal("0.01")` (con su comentario) y `format_base_price` (`v.quantize(
  _CENTS)`) en `ServiceBase` y en `ServiceUpdate`; en el test de precio de D, `"new": "60000"` pasa a `"new":
  "60000.00"`.
- **Tests (RED primero):** sección nueva al final de `tests/test_services.py`. Las dos opciones:
  `test_be38_create_answers_the_price_with_two_decimals` ×3 (`integer`, `one-decimal`, `two-decimals`: `POST`, `GET` y
  la fila guardada). Solo (b): `test_be38_update_answers_the_price_with_two_decimals` ×3,
  `test_be38_schema_keeps_rejecting_a_third_decimal` (borde; mata M13) y la línea reescrita de D. **RED medido** (copia
  con A–D + solo los tests): (a) `2 failed, 790 passed`: `integer` y `one-decimal` del test de alta; (b) `5 failed,
  791 passed`: esos dos, los mismos dos del test de `PUT` y la línea reescrita de D. `two-decimals` y el del tercer
  decimal pasan ya (son los bordes que el cambio no debe romper).
- **Criterio de aceptación:** compuerta exit 0; (a) `792 passed`, 98,68 %, M8a muere; (b) `796 passed`, 98,69 %, M8b,
  M8c y M13 mueren (y M2 deja de morir: riesgo 4).
- **Fuera de alcance:** la auditoría (D, F); con (a), `save_service` y la respuesta de `PUT` (R3); con (b), los DTO de
  salida (A9) y el repositorio.
- **Commit (a):** 
  ```
  fix(services): answer a new package with its stored price

  POST /servicios/ answered the price as sent ("50000") while GET
  answered it as stored ("50000.00"): create_service reloaded the row
  but kept the scalars of the instance the session already held
  (BE-38, measured).

  populate_existing reloads them too, so a new package, and the CREATE
  row that BE-61 writes from it, carry the price with the scale of its
  column. PUT keeps answering the price as sent, as decided with the
  plan.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```
- **Commit (b):** 
  ```
  fix(schemas): write the package price with two decimals at input

  POST and PUT /servicios answered the price as sent ("50000") while GET
  answered it as stored ("50000.00"), and the UPDATE row of a price
  change mixed both: old "50000.00", new "60000" (BE-38, measured).

  - app/schemas/service.py: ServiceCreate and ServiceUpdate write
    base_price with the two decimals of its NUMERIC(10, 2) column, after
    the decimal_places check, so a third decimal is still a 422 and
    nothing is rounded.
  - tests/test_services.py: POST, PUT and GET read the same; the audited
    price change now reads new "60000.00".

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase F — El alta de un paquete audita lo guardado (BE-61, fila hija)
- **Archivos (2):** `app/services/tourist_services_service.py`, `tests/test_services.py`. Dominio: auditoría de
  paquetes (alta). `numstat`: `7 3` y `46 2`. Texto: Anexo F.
- **Cambios exactos:** en `create_tourist_package`, `stored = {field: audit_value(getattr(saved, field)) for field in
  tourist_service_data}`, `stored["image_urls"] = [image.image_url for image in saved.images]` y `changes=stored`; import
  de `audit_value`; dos líneas de docstring.
- **Tests (RED primero):** `test_create_package_promotes_temporal_url` afirma la fila `CREATE` completa (`"base_price":
  "50000.00"`, `"image_urls": [PERMANENT_URL]`) y amplía su docstring; nuevo
  `test_be61_create_audits_every_promoted_url_in_order` (dos temporales → dos permanentes, en orden). **RED medido**
  (copia con A–E + solo los tests): (a) `2 failed, 791 passed`; (b) `2 failed, 795 passed`; fallan los dos tests
  citados, en las dos.
- **Criterio de aceptación:** compuerta exit 0; (a) `793 passed`, 98,68 %; (b) `797 passed`, 98,69 %; M14 muere (y M8a
  con (a), M8b con (b), por la fila).
- **Fuera de alcance:** `save_service` (R3), BE-26, BE-48, BE-59.
- **Commit:** 
  ```
  fix(services): audit a new package as stored (BE-61)

  The CREATE row of a package carried the body as sent: temporal image
  URLs and the price as typed. It now carries the saved package: its
  columns as the instance holds them after the insert and its promoted
  URLs, in order. The row keeps its shape: values, no old/new
  (ADR-0021).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase G — ADR-0021 y los comentarios del modelo
- **Archivos (2):** `docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md` (nuevo; texto del Anexo G con el punto
  8, la consecuencia y la alternativa 6 de la opción aprobada; `<FECHA>` = fecha de aprobación), `app/models/audit.py`.
  Dominio: decisiones y documentación del modelo de auditoría. `numstat`: `84 0` y `4 4`.
- **Cambios exactos:** docstring de `AuditLog`, comentario de `changes` (sin `old_values`) y traducción del comentario
  `# "User" o "TouristService"` (Anexo G).
- **Tests:** ninguno nuevo (documental). Comprobación sustituta: compuerta completa (`check_docs` no escanea `docs/adr`).
- **Criterio de aceptación:** compuerta exit 0 con la misma suite que F ((a) `793 passed`, 98,68 %; (b) `797 passed`,
  98,69 %); `old_values` 0 en `app/models/audit.py`; ningún `<FECHA>` en `docs/adr` (`git grep -n "<FECHA>" -- docs/adr`
  sin salida).
- **Fuera de alcance:** `AGENTS.md` (la viñeta la commitea David tras la última auditoría, R6), CONTEXT, backlog.
- **Commit:** 
  ```
  docs(adr): add ADR-0021, the audit records only what changed

  The ADR records the rules the previous commits put in code: an UPDATE
  row carries only the fields that changed, as old and new values; a
  request that changes nothing writes no row; a CREATE row is written
  after the insert and records what was stored; rows written before are
  not migrated and are told apart by their shape.

  app/models/audit.py: the comment on changes promised old_values and
  new_values, a shape the code never wrote; it now describes what is
  written. The Spanish comment ADR-0010 left for the next change to the
  file is translated.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, tras la fase G. Los conteos incluyen el texto que dicta este plan (código, docstrings, comentarios,
nombres y docstrings de tests, ADR) y están medidos con `grep` sobre las dos copias finales (una por opción; `git grep`
se emuló con `grep -rn --include='*.py'`, porque las copias no son repositorios git). Los patrones de detección de la
verificación y de la re-verificación, recalculados, son los comandos 1, 2, 3, 6, 7, 8, 9 y 12.

```bash
# 1. Puntos que escriben auditoría → 13 líneas (12 de hoy + la activación): user_service.py 6, tourist_services_service.py 5,
#    superadmin_bootstrap.py 1, audit_service.py 1 (la definición)
git grep -n "log_transaction(" -- app

# 2. El cálculo sale de la fila → 3 líneas: user_service.py :302 (mode="json", para la política y el setattr) y :308
#    (changed_fields); tourist_services_service.py :292
git grep -n "exclude_unset=True" -- app/services

# 3. Lo que auditaba el cuerpo, fuera → 0 líneas (exit 1)
git grep -n -E "if update_dict:|payload_changes|activation_success|activate_user|changes=update_dict" -- app tests

# 4. changed_fields → 4 líneas: audit_service.py:28 (definición); user_service.py :150 y :308; tourist_services_service.py
#    :293. Ninguna en docstring o comentario (regla de grep)
git grep -n "changed_fields(" -- app

# 5. Filas solo si algo cambia → user_service.py:2, tourist_services_service.py:1
git grep -c "if changes:" -- app/services

# 6. Activar/desactivar mira el estado → 1 línea, tourist_services_service.py:136 (mutación y auditoría dentro)
git grep -n "if service.is_available != is_available:" -- app

# 7. Crear antes de auditar → 10 líneas; los tres pares de alta van create_user → log_transaction:
#    user_service.py :94/:97 (registro) y :447/:449 (alta administrativa); superadmin_bootstrap.py :64/:66
git grep -n -E "log_transaction\(|create_user\(" -- app/services/user_service.py app/services/superadmin_bootstrap.py

# 8. A3 intacto → 6 líneas (7 de hoy menos el commit de activate_user): audit_repository.py:16; service_repository.py
#    :17 y :96 con (a) o :93 con (b); user_repository.py :50, :73, :101
git grep -n "\.commit()" -- app/repositories

# 9. El comentario del modelo → old_values 0 (exit 1); ADR-0021 en audit.py → 2 líneas (:28 y :43)
git grep -n "old_values" -- app/models/audit.py
git grep -n "ADR-0021" -- app/models/audit.py

# 10. R1 → 1 línea, app/models/service.py:52
git grep -n "order_by=lambda: ServiceImage.id" -- app

# 11. Precio → (a): 2 líneas, service_repository.py :19 (comentario) y :26; (b): 3 líneas, schemas/service.py :11 :61 :147
git grep -n -E "populate_existing|_CENTS" -- app

# 12. Tests que congelan changes → 14 líneas: test_auth.py 2, test_services.py 3, test_user_access_policy.py 5,
#     test_user_service.py 2, test_user_update_audit.py 1, test_user_update_null.py 1; "BE-38" en la política → 0
git grep -n -E "\.changes ==|a\.changes\) for|audit\.changes\) for|changes=\{" -- tests
git grep -n "BE-38" -- tests/test_user_access_policy.py

# 13. Citas de ADR-0021 → app 11 líneas (audit.py :28 :43; service.py :30; audit_service.py :17 :33;
#     tourist_services_service.py :35 :116 :267; user_service.py :114 :281 :412); tests 8 líneas (test_auth.py :131;
#     test_services.py 4; test_user_access_policy.py :1215; test_user_service.py :452; test_user_update_audit.py :4);
#     docs/adr: el archivo 0021
git grep -n "ADR-0021" -- app tests
git grep -l "ADR-0021" -- docs/adr

# 14. Tests del ítem → test_auth.py:3, test_services.py:10 con (a) o 12 con (b), test_user_update_audit.py:5;
#     `-k "be38 or be61"` → (a) `32 passed, 761 deselected`; (b) `36 passed, 761 deselected`
git grep -c -E "def test_be(38|61)_" -- tests
./venv/Scripts/python.exe -m pytest -k "be38 or be61" -q

# 15. Nada fuera del alcance → salida vacía. Con (a) se añade app/schemas/service.py a la lista; con (b),
#     app/repositories/service_repository.py
git diff --stat 6cae238 HEAD -- app/api app/main.py app/core app/cli app/db app/services/user_access_policy.py app/services/superadmin_bootstrap.py app/repositories/audit_repository.py app/schemas/user.py app/schemas/audit.py app/schemas/partial_update.py alembic tests/conftest.py conftest.py tests/test_route_guards.py tests/test_token_failure_paths.py tests/test_superadmin_bootstrap.py pyproject.toml constraints.txt AGENTS.md

# 16. Lo que sí cambia → (a) 15 líneas; (b) 15 líneas (lista literal en "Mediciones", 5)
git diff --numstat 6cae238 HEAD -- app tests docs/adr

# 17. Compuerta completa → exit 0; 71 files already formatted; ruff 0; mypy 0 en 66; 4 kept;
#     (a) 793 passed, cobertura 98,68 %; (b) 797 passed, 98,69 % (≥ 98,49 %); 25 avisos, como la línea base
./venv/Scripts/python.exe scripts/check.py
```

**Paso humano de David antes de mezclar (no es fase).** En el repositorio del cliente Flutter, desde `cmd`:
`findstr /s /n /i "changes" lib\*.dart` y revisar cómo pinta el panel de auditoría un valor que es un objeto
`{"old", "new"}` y uno que es un valor suelto (filas viejas). El resultado va al PR como riesgo declarado.

## Residuales

- **R1 — `TouristService.images` sin `order_by`:** **ya no es residual; entra en la fase D** (petición de la sesión
  Mentor, 18 nov).
- **R2 — Reenviar la misma lista recrea las filas de `service_images`** (P5; `tourist_services_service.py:320-334`),
  ahora sin fila de auditoría. Nota sugerida en BE-26 (mismo bloque de imágenes).
- **R3 — `save_service` tampoco repuebla escalares:** con la opción (a), `PUT /servicios/{id}` responde `"60000"` y
  `new` conserva esa grafía. Con la opción (b) desaparece (el valor ya llega con dos decimales). Fila sugerida, Baja, solo
  si David elige (a) y quiere igualar `PUT`/`new` después.
- **R4 — BE-49** cita el doble de `activate_user` (`tests/test_user_service.py:307`): tras la fase C ese método no
  existe. Nota sugerida en la fila.
- **R5 — BE-09**: revisar al cerrar BE-38 qué queda (su nota ya lo dice).
- **R6 — AGENTS §3**: viñeta sugerida para David tras la última auditoría: "Auditoría (ADR-0021): un `UPDATE` registra
  solo lo que cambió, `{campo: {"old", "new"}}`, calculado con `changed_fields` después de la política; un no-cambio no
  deja fila; un alta se audita después de guardar." El comando 15 exige `AGENTS.md` sin cambio desde `6cae238`: la viñeta
  va después de la auditoría de G y antes de `/pr`.
- **R7 — M2 sobrevive con la opción (b)** (Análisis, riesgo 4): sin destino; la comparación en Python la decidió David.
- **R8 — `alembic check` contra PostgreSQL no se ejecutó** (Docker parado); el esquema se comparó por metadatos. Sin
  fila: opcional para David antes del PR.

## Referencias

- SQLAlchemy 2.0.48 (`constraints.txt:71`) · `relationship(order_by=...)` acepta una función que se evalúa al configurar
  el mapeador (o un texto evaluado con `eval()`) — consultado en Context7 (`/websites/sqlalchemy_en_20_orm`):
  https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.order_by y
  https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#late-evaluation-of-relationship-arguments — medido
  (`ORDER BY service_images.id` en la consulta de `selectinload`).
- SQLAlchemy 2.0.48 · `execution_options(populate_existing=True)` refresca las instancias ya presentes en la sesión
  (opción a) — consultado en Context7: https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html#populate-existing —
  medido (sonda de precio).
- Alembic 1.18.4 (`constraints.txt:9`) · `alembic.autogenerate.compare_metadata`, la comparación de `alembic check`:
  https://alembic.sqlalchemy.org/en/latest/api/autogenerate.html#alembic.autogenerate.compare_metadata — medido (`[]`).
- pydantic 2.12.5 (`constraints.txt:56`) · `TypeAdapter(Any).dump_python(value, mode="json")`:
  https://docs.pydantic.dev/2.12/concepts/type_adapter/ ; `field_validator` en modo `after` corre tras las restricciones
  de `Field` (opción b): https://docs.pydantic.dev/2.12/concepts/validators/#field-after-validator — medidos en copia.

## Mediciones (literales; scratchpad de la sesión, nunca en el repo)

**(1) RED** (cada copia: la anterior con su código + solo los tests de la fase; `pytest -q -rf`, suite completa):

```
== RED fase A: 2 failed, 757 passed, 25 warnings in 37.49s
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[database-failure]
== RED fase B: 18 failed, 751 passed, 25 warnings in 38.09s
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_profile_update_returns_200
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_changes_third_party_role_returns_200
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_update_with_is_active_true_returns_200
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
    FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_update_with_is_active_true_returns_200
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[role-same]
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[first-name-same]
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[first-name-normalized]
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[phone-null-already-null]
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[is-active-same]
    FAILED tests/test_user_update_audit.py::test_be38_unchanged_user_update_returns_200_without_audit_row[four-keys-same]
    FAILED tests/test_user_update_audit.py::test_be38_email_in_another_case_is_unchanged
    FAILED tests/test_user_update_audit.py::test_be38_partial_change_audits_only_the_changed_field
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== RED fase C: 6 failed, 767 passed, 25 warnings in 37.61s
    FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account
    FAILED tests/test_auth.py::test_be38_verify_email_on_deleted_account_returns_404_without_mutation
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_service.py::test_verify_email_activates_account
    FAILED tests/test_user_service.py::test_verify_email_on_active_account_writes_nothing
    FAILED tests/test_user_service.py::test_verify_email_missing_user_raises_not_found
== RED fase D: 16 failed, 773 passed, 25 warnings in 36.27s
    FAILED tests/test_models_schema.py::test_service_images_load_in_stored_order
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
    FAILED tests/test_services.py::test_be37_null_on_image_urls_still_keeps_the_images
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[name-same]
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[name-normalized]
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[price-same-value]
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[available-same]
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[description-null-already-null]
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[empty-images-without-images]
    FAILED tests/test_services.py::test_be38_resent_image_list_returns_200_without_audit_row
    FAILED tests/test_services.py::test_be38_reordered_image_list_audits_the_new_order
    FAILED tests/test_services.py::test_be38_partial_package_change_audits_only_the_changed_field
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
    FAILED tests/test_services.py::test_be38_image_change_audits_the_stored_urls
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[activate-active]
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[deactivate-inactive]
== RED fase E (a): 2 failed, 790 passed, 25 warnings in 35.80s
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
== RED fase E (b): 5 failed, 791 passed, 25 warnings in 36.04s
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[one-decimal]
== RED fase F (a): 2 failed, 791 passed, 25 warnings in 34.89s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
== RED fase F (b): 2 failed, 795 passed, 25 warnings in 35.99s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
```

**(2) GREEN** (`./venv/Scripts/python.exe scripts/check.py`, exit 0 en todas; línea de cobertura y de pytest):

```
== GREEN fase A: 759 passed, 25 warnings in 37.12s
    70 files already formatted
    All checks passed!
    Success: no issues found in 65 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1047     10    150      8  98.50%
    Compuerta superada.
== GREEN fase B: 769 passed, 25 warnings in 37.36s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1055     10    150      7  98.59%
    Compuerta superada.
== GREEN fase C: 773 passed, 25 warnings in 37.78s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1051     10    150      7  98.58%
    Compuerta superada.
== GREEN fase D: 789 passed, 25 warnings in 36.14s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1055     10    154      6  98.68%
    Compuerta superada.
== GREEN fase E (a): 792 passed, 25 warnings in 40.15s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1055     10    154      6  98.68%
    Compuerta superada.
== GREEN fase E (b): 796 passed, 25 warnings in 40.16s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1064     10    154      6  98.69%
    Compuerta superada.
== GREEN fase F (a): 793 passed, 25 warnings in 39.61s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1057     10    154      6  98.68%
    Compuerta superada.
== GREEN fase F (b): 797 passed, 25 warnings in 42.01s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1066     10    154      6  98.69%
    Compuerta superada.
== GREEN fase G (a): 793 passed, 25 warnings in 41.82s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1057     10    154      6  98.68%
    Compuerta superada.
== GREEN fase G (b): 797 passed, 25 warnings in 41.83s
    71 files already formatted
    All checks passed!
    Success: no issues found in 66 source files
    Contracts: 4 kept, 0 broken.
    TOTAL                                       1066     10    154      6  98.69%
    Compuerta superada.
```

Compuerta completa de las dos copias finales (A–G):

```
== copia final (a)
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
app\db\database.py                            13      4      0      0  69.23%   31-35
app\main.py                                   57      1     18      1  97.33%   72
app\repositories\user_repository.py           53      1      6      1  96.61%   67
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
app\services\tourist_services_service.py     110      2     38      2  97.30%   51, 301
TOTAL                                       1057     10    154      6  98.68%
793 passed, 25 warnings in 41.82s
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura
Compuerta superada.
exit=0
== copia final (b)
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
app\db\database.py                            13      4      0      0  69.23%   31-35
app\main.py                                   57      1     18      1  97.33%   72
app\repositories\user_repository.py           53      1      6      1  96.61%   67
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
app\services\tourist_services_service.py     110      2     38      2  97.30%   51, 301
TOTAL                                       1066     10    154      6  98.69%
797 passed, 25 warnings in 41.83s
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura
Compuerta superada.
exit=0
```

**(3) Sonda de precio** (archivo de test temporal en cada copia, nunca en el repo; `pytest -s`):

```
== hoy (6cae238)
PROBE POST base_price: '50000'
PROBE CREATE row base_price: '50000'
PROBE CREATE row image_urls: ['https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/cover.jpg']
PROBE PUT base_price: '60000'
PROBE UPDATE row changes: {'base_price': '60000'}
PROBE GET base_price: ['60000.00']
== opción (a), fases A–G
PROBE POST base_price: '50000.00'
PROBE CREATE row base_price: '50000.00'
PROBE CREATE row image_urls: ['https://ecoturasopradocdn2026.blob.core.windows.net/ecotur-images/cover.jpg']
PROBE PUT base_price: '60000'
PROBE UPDATE row changes: {'base_price': {'old': '50000.00', 'new': '60000'}}
PROBE GET base_price: ['60000.00']
== probe_a_nopop: opción (a) sin populate_existing (= sin fase E)
PROBE POST base_price: '50000'
PROBE CREATE row base_price: '50000'
PROBE CREATE row image_urls: ['https://ecoturasopradocdn2026.blob.core.windows.net/ecotur-images/cover.jpg']
PROBE PUT base_price: '60000'
PROBE UPDATE row changes: {'base_price': {'old': '50000.00', 'new': '60000'}}
PROBE GET base_price: ['60000.00']
== opción (b), fases A–G
PROBE POST base_price: '50000.00'
PROBE CREATE row base_price: '50000.00'
PROBE CREATE row image_urls: ['https://ecoturasopradocdn2026.blob.core.windows.net/ecotur-images/cover.jpg']
PROBE PUT base_price: '60000.00'
PROBE UPDATE row changes: {'base_price': {'old': '50000.00', 'new': '60000.00'}}
PROBE GET base_price: ['60000.00']
```

Bordes de (b), `ServiceUpdate.model_validate({"base_price": v})` en la copia: `50000 -> Decimal('50000.00')`,
`50000.5 -> Decimal('50000.50')`, `'50000.000' -> Decimal('50000.00')` (hoy `Decimal('50000.000')`), `'5E+4' ->
Decimal('50000.00')`, `99999999.99 -> Decimal('99999999.99')`, `123456789 -> 422 ['decimal_whole_digits']` (igual hoy),
`'50000.555' -> 422 ['decimal_max_places']`. OpenAPI: md5 `e956fcd70a4198a55d0c2452a58a4a58` hoy, con (a) y con (b).

**(4) Mutantes** (copia final de cada opción; uno por ejecución, `app/` restaurado después):

```
== M1 (a): 5 failed, 788 passed, 25 warnings in 46.93s
    FAILED tests/test_user_access_policy.py::test_b2_admin_self_role_noop_returns_403
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_noop_returns_403
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
    FAILED tests/test_user_update_audit.py::test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403
    FAILED tests/test_user_update_audit.py::test_be38_admin_self_role_with_unchanged_value_returns_403
== M1 (b): 5 failed, 792 passed, 25 warnings in 43.54s
    FAILED tests/test_user_access_policy.py::test_b2_admin_self_role_noop_returns_403
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_noop_returns_403
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
    FAILED tests/test_user_update_audit.py::test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403
    FAILED tests/test_user_update_audit.py::test_be38_admin_self_role_with_unchanged_value_returns_403
== M2 (a): 1 failed, 792 passed, 25 warnings in 42.28s
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[price-same-value]
== M2 (b): 797 passed, 25 warnings in 41.94s
== M3u (a): 9 failed, 784 passed, 25 warnings in 43.34s
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_profile_update_returns_200
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_changes_third_party_role_returns_200
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
    FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
    FAILED tests/test_user_update_audit.py::test_be38_partial_change_audits_only_the_changed_field
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== M3u (b): 9 failed, 788 passed, 25 warnings in 44.74s
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_profile_update_returns_200
    FAILED tests/test_user_access_policy.py::test_be02_superadmin_changes_third_party_role_returns_200
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
    FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
    FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
    FAILED tests/test_user_update_audit.py::test_be38_partial_change_audits_only_the_changed_field
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== M3p (a): 3 failed, 790 passed, 25 warnings in 47.11s
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
    FAILED tests/test_services.py::test_be38_partial_package_change_audits_only_the_changed_field
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
== M3p (b): 3 failed, 794 passed, 25 warnings in 44.91s
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
    FAILED tests/test_services.py::test_be38_partial_package_change_audits_only_the_changed_field
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
== M4 (a): 2 failed, 791 passed, 25 warnings in 35.15s
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[database-failure]
== M4 (b): 2 failed, 795 passed, 25 warnings in 45.98s
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[race-on-unique-index]
    FAILED tests/test_user_service.py::test_create_administrative_account_insert_failure_writes_no_audit_row[database-failure]
== M5 (a): 3 failed, 790 passed, 25 warnings in 47.86s
    FAILED tests/test_auth.py::test_be38_verify_email_on_deleted_account_returns_404_without_mutation
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
== M5 (b): 3 failed, 794 passed, 25 warnings in 43.97s
    FAILED tests/test_auth.py::test_be38_verify_email_on_deleted_account_returns_404_without_mutation
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_token_failure_paths.py::test_token_for_soft_deleted_active_user_returns_401
== M6 (a): 2 failed, 791 passed, 25 warnings in 42.19s
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[activate-active]
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[deactivate-inactive]
== M6 (b): 2 failed, 795 passed, 25 warnings in 42.17s
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[activate-active]
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[deactivate-inactive]
== M7 (a): 1 failed, 792 passed, 25 warnings in 43.68s
    FAILED tests/test_services.py::test_be38_image_change_audits_the_stored_urls
== M7 (b): 1 failed, 796 passed, 25 warnings in 44.85s
    FAILED tests/test_services.py::test_be38_image_change_audits_the_stored_urls
== M8a (a): 3 failed, 790 passed, 25 warnings in 47.22s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
== M8b (b): 3 failed, 794 passed, 25 warnings in 44.99s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
== M8c (b): 3 failed, 794 passed, 25 warnings in 46.14s
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[one-decimal]
== M9 (a): 1 failed, 792 passed, 25 warnings in 35.41s
    FAILED tests/test_services.py::test_be38_reordered_image_list_audits_the_new_order
== M9 (b): 1 failed, 796 passed, 25 warnings in 43.73s
    FAILED tests/test_services.py::test_be38_reordered_image_list_audits_the_new_order
== M10 (a): 1 failed, 792 passed, 25 warnings in 47.10s
    FAILED tests/test_models_schema.py::test_service_images_load_in_stored_order
== M10 (b): 1 failed, 796 passed, 25 warnings in 41.87s
    FAILED tests/test_models_schema.py::test_service_images_load_in_stored_order
== M11 (a): 2 failed, 791 passed, 25 warnings in 42.40s
    FAILED tests/test_auth.py::test_be38_verify_email_on_active_account_returns_200_without_audit_row
    FAILED tests/test_user_service.py::test_verify_email_on_active_account_writes_nothing
== M11 (b): 2 failed, 795 passed, 25 warnings in 45.31s
    FAILED tests/test_auth.py::test_be38_verify_email_on_active_account_returns_200_without_audit_row
    FAILED tests/test_user_service.py::test_verify_email_on_active_account_writes_nothing
== M12 (a): 3 failed, 790 passed, 25 warnings in 43.71s
    FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_service.py::test_verify_email_activates_account
== M12 (b): 3 failed, 794 passed, 25 warnings in 44.03s
    FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account
    FAILED tests/test_auth.py::test_be38_verify_email_after_admin_deactivation_writes_an_audit_row
    FAILED tests/test_user_service.py::test_verify_email_activates_account
== M13 (b): 1 failed, 796 passed, 25 warnings in 32.44s
    FAILED tests/test_services.py::test_be38_schema_keeps_rejecting_a_third_decimal
== M14 (a): 2 failed, 791 passed, 25 warnings in 47.25s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
== M14 (b): 2 failed, 795 passed, 25 warnings in 46.24s
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url
    FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
== M2 sobre la copia de la fase D (sin precio normalizado): 1 failed, 788 passed, 25 warnings in 46.69s
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[price-same-value]
```

**(5) Esquema (R1) y `numstat`.**

```
images.order_by antes: False
images.order_by después: (Column('id', Integer(), table=<service_images>, primary_key=True, nullable=False),)
DDL PostgreSQL de Base.metadata: 57 líneas antes y después; md5 11789bcfa202996016a9d9244ac6e3e5 en los dos; cmp: idénticos
compare_metadata(base creada con los modelos de antes, metadatos de antes):   []
compare_metadata(base creada con los modelos de antes, metadatos de después): []
consulta de selectinload antes:   ... FROM service_images WHERE service_images.service_id IN (?)
consulta de selectinload después: ... FROM service_images WHERE service_images.service_id IN (?) ORDER BY service_images.id
```

`git diff --numstat` contra `6cae238` de cada copia final (`app`, `tests`, `docs/adr`):

```
== opción (a)
4	4	app/models/audit.py
5	1	app/models/service.py
4	1	app/repositories/service_repository.py
0	13	app/repositories/user_repository.py
44	0	app/services/audit_service.py
33	18	app/services/tourist_services_service.py
35	11	app/services/user_service.py
67	0	tests/test_auth.py
8	0	tests/test_models_schema.py
300	4	tests/test_services.py
22	6	tests/test_user_access_policy.py
82	13	tests/test_user_service.py
152	0	tests/test_user_update_audit.py
1	1	tests/test_user_update_null.py
84	0	docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md
== opción (b)
4	4	app/models/audit.py
5	1	app/models/service.py
0	13	app/repositories/user_repository.py
15	0	app/schemas/service.py
44	0	app/services/audit_service.py
33	18	app/services/tourist_services_service.py
35	11	app/services/user_service.py
67	0	tests/test_auth.py
8	0	tests/test_models_schema.py
336	4	tests/test_services.py
22	6	tests/test_user_access_policy.py
82	13	tests/test_user_service.py
152	0	tests/test_user_update_audit.py
1	1	tests/test_user_update_null.py
84	0	docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md
```

**(6) Columnas.** Código y tests: `ruff format --check` y `ruff check` (E501, 100) en verde en todas las copias. ADR-0021:
84 líneas, la más larga 100 (con `<FECHA>`; medido con el intérprete, por caracteres). Asuntos de commit: 61, 66, 61, 69,
57 (E, opción a), 64 (E, opción b), 52, 60; ninguna línea de cuerpo pasa de 72.


## Anexo A — texto de la fase A

Diff contra `6cae238` (copias; se omiten las líneas `index` y `diff --git`):

```diff
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -387,7 +387,8 @@ class UserService:
 
         The caller is a superadmin: the route's guard decided it (ADR-0012,
         point 1), so the service checks no role. The account is created
-        instantly without requiring email verification.
+        instantly without requiring email verification. It is created before its
+        audit entry, so a failed insert leaves no CREATE row (ADR-0021).
 
         Args:
             user_data (UserCreateByAdmin): DTO containing profile and explicit role definitions.
@@ -422,12 +423,14 @@ class UserService:
             is_active=user_data.is_active,
         )
 
+        saved_user = await self.user_repo.create_user(new_user)
+
         await self.audit_service.log_transaction(
             entity_name="User",
-            entity_id=user_data.cedula,
+            entity_id=saved_user.cedula,
             action=AuditAction.CREATE,
             performed_by=current_user.cedula,
             changes={"role": user_data.role.value},
         )
 
-        return await self.user_repo.create_user(new_user)
+        return saved_user
--- a/tests/test_user_service.py
+++ b/tests/test_user_service.py
@@ -6,7 +6,7 @@ from unittest.mock import create_autospec
 
 import jwt
 import pytest
-from sqlalchemy.exc import SQLAlchemyError
+from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
 
 from app.core.config import get_settings
 from app.core.exceptions import (
@@ -343,11 +343,13 @@ async def test_create_administrative_account_provisions_admin(
 ):
     """Happy path: a superadmin provisions an admin account in a single persistence call."""
     user_repo.get_user_by_email_or_cedula.return_value = None
+    user_repo.create_user.side_effect = lambda user: user
     actor = make_user(role=UserRole.superadmin)
 
-    await user_service.create_administrative_account(_admin_payload(), actor)
+    result = await user_service.create_administrative_account(_admin_payload(), actor)
 
     created_user = user_repo.create_user.call_args.args[0]
+    assert result is created_user
     assert created_user.role == UserRole.admin
     assert created_user.cedula == "5555555555"
     assert created_user.is_active is True
@@ -399,6 +401,41 @@ async def test_create_administrative_account_lookup_failure_writes_nothing(
     user_repo.create_user.assert_not_awaited()
 
 
+@pytest.mark.parametrize(
+    "error",
+    [
+        pytest.param(
+            IntegrityError("INSERT INTO users", {}, Exception("UNIQUE constraint failed")),
+            id="race-on-unique-index",
+        ),
+        pytest.param(
+            OperationalError("INSERT INTO users", {}, Exception("database is locked")),
+            id="database-failure",
+        ),
+    ],
+)
+async def test_create_administrative_account_insert_failure_writes_no_audit_row(
+    user_repo, audit_service, user_service, make_user, error
+):
+    """Unhappy path: a failed insert leaves no CREATE row behind (ADR-0021).
+
+    The race on the unique indexes (409) and a database failure (500) are not reproducible
+    over HTTP without replacing the repository, so the double raises them here.
+    """
+    user_repo.get_user_by_email_or_cedula.return_value = None
+    user_repo.create_user.side_effect = error
+
+    with pytest.raises(type(error)):
+        await user_service.create_administrative_account(
+            _admin_payload(), make_user(role=UserRole.superadmin)
+        )
+
+    created_user = user_repo.create_user.call_args.args[0]
+    assert created_user.cedula == "5555555555"
+    user_repo.create_user.assert_awaited_once_with(created_user)
+    audit_service.log_transaction.assert_not_awaited()
+
+
 # ==========================================
 # INTEGRATION (real HTTP stack)
 # ==========================================
```


## Anexo B — texto de la fase B

Diff contra la fase A:

```diff
--- a/app/services/audit_service.py
+++ b/app/services/audit_service.py
@@ -1,8 +1,52 @@
+from collections.abc import Mapping
 from typing import Any
 
+from pydantic import TypeAdapter
+
 from app.models.audit import AuditAction, AuditLog
 from app.repositories.audit_repository import AuditRepository
 
+# Dumps any column or validated value to its JSON form: Decimal and enum members become text.
+_JSON_VALUE: TypeAdapter[Any] = TypeAdapter(Any)
+
+
+def audit_value(value: Any) -> Any:
+    """Returns a value in the JSON form an audit row stores.
+
+    Decimal and enum members become text, as model_dump(mode="json") wrote them before
+    (ADR-0021).
+
+    Args:
+        value: A stored column value or a validated field value.
+
+    Returns:
+        The same value, ready for the JSON column of the audit row.
+    """
+    return _JSON_VALUE.dump_python(value, mode="json")
+
+
+def changed_fields(entity: object, new_values: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
+    """Returns the fields whose validated value differs from the stored one, as old and new.
+
+    Compares Python values, not their text: Decimal("50000") equals the stored
+    Decimal("50000.00"), and a value the schema normalizes to what is stored is no change
+    (ADR-0021). Runs after the access policy, which decides on the keys sent, and before
+    any setattr, which would overwrite the old value.
+
+    Args:
+        entity: The ORM row as it is stored.
+        new_values: The validated values sent, keyed by attribute name.
+
+    Returns:
+        {field: {"old": ..., "new": ...}} in JSON form for each field that changes; empty
+        when nothing does.
+    """
+    return {
+        field: {"old": audit_value(getattr(entity, field)), "new": audit_value(value)}
+        for field, value in new_values.items()
+        if getattr(entity, field) != value
+    }
+
 
 class AuditService:
     """Encapsulates business logic, rules, and operational logic of the Audit Trail ecosystem."""
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -22,7 +22,7 @@ from app.models.user import User, UserRole
 from app.repositories.user_repository import UserRepository
 from app.schemas.token import TokenResponse
 from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserUpdate
-from app.services.audit_service import AuditService
+from app.services.audit_service import AuditService, changed_fields
 from app.services.user_access_policy import UserAccessPolicy
 
 
@@ -261,6 +261,8 @@ class UserService:
         One exception to the rank rule: a superadmin may reactivate another
         superadmin outside the recycle bin, sending is_active true and nothing
         else (ADR-0018).
+        Only the fields whose value changes are audited, as old and new values;
+        a request that changes nothing writes no audit row (ADR-0021).
 
         Args:
             target_cedula (str): The primary identifier of the account to update.
@@ -286,18 +288,21 @@ class UserService:
         # 2. ABAC Hierarchical + Fail-Safe Invariants delegated to the access policy
         self.user_access_policy.assert_can_update(current_user, target_user, update_dict)
 
-        # 3. Apply Scalar Mutations
+        # 3. What actually changes, compared with the stored values before any setattr
+        changes = changed_fields(target_user, update_data.model_dump(exclude_unset=True))
+
+        # 4. Apply Scalar Mutations
         for key, value in update_dict.items():
             setattr(target_user, key, value)
 
-        # 4. Log Registry
-        if update_dict:
+        # 5. Log Registry
+        if changes:
             await self.audit_service.log_transaction(
                 entity_name="User",
                 entity_id=target_cedula,
                 action=AuditAction.UPDATE,
                 performed_by=current_user.cedula,
-                changes=update_dict,
+                changes=changes,
             )
 
         return await self.user_repo.save_user(target_user)
--- a/tests/test_user_access_policy.py
+++ b/tests/test_user_access_policy.py
@@ -689,7 +689,7 @@ async def test_be02_superadmin_self_profile_update_returns_200(
     assert len(audits) == 1
     assert audits[0].action == AuditAction.UPDATE
     assert audits[0].performed_by == superadmin.cedula
-    assert audits[0].changes == {"first_name": "Changed"}
+    assert audits[0].changes == {"first_name": {"old": "John", "new": "Changed"}}
 
 
 async def test_be02_superadmin_changes_third_party_role_returns_200(
@@ -717,7 +717,7 @@ async def test_be02_superadmin_changes_third_party_role_returns_200(
     assert len(audits) == 1
     assert audits[0].entity_id == admin.cedula
     assert audits[0].performed_by == superadmin.cedula
-    assert audits[0].changes == {"role": "tourist"}
+    assert audits[0].changes == {"role": {"old": "admin", "new": "tourist"}}
 
 
 # --- B3 regression: a superadmin deletes third-party accounts (audit B3) ---
@@ -977,6 +977,8 @@ async def test_be35_superadmin_self_update_with_is_active_true_returns_200(
 
     await db_session.refresh(superadmin)
     assert superadmin.is_active is True
+    audits = (await db_session.execute(select(AuditLog))).scalars().all()
+    assert audits == []
 
 
 async def test_be35_superadmin_deactivates_lower_rank_account_returns_200(
@@ -1005,7 +1007,7 @@ async def test_be35_superadmin_deactivates_lower_rank_account_returns_200(
     assert audits[0].action == AuditAction.UPDATE
     assert audits[0].entity_id == admin.cedula
     assert audits[0].performed_by == superadmin.cedula
-    assert audits[0].changes == {"is_active": False}
+    assert audits[0].changes == {"is_active": {"old": True, "new": False}}
 
 
 # --- BE-36 regression: a superadmin reactivates a peer superadmin, and nothing else ---
@@ -1050,7 +1052,12 @@ async def test_be36_recovered_superadmin_reactivated_by_peer_can_log_in(
     audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
     assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
         (AuditAction.RECOVER, peer.cedula, superadmin.cedula, None),
-        (AuditAction.UPDATE, peer.cedula, superadmin.cedula, {"is_active": True}),
+        (
+            AuditAction.UPDATE,
+            peer.cedula,
+            superadmin.cedula,
+            {"is_active": {"old": False, "new": True}},
+        ),
     ]
 
 
@@ -1093,7 +1100,12 @@ async def test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_l
     audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
     assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
         (AuditAction.CREATE, "777777", superadmin.cedula, {"role": "superadmin"}),
-        (AuditAction.UPDATE, "777777", superadmin.cedula, {"is_active": True}),
+        (
+            AuditAction.UPDATE,
+            "777777",
+            superadmin.cedula,
+            {"is_active": {"old": False, "new": True}},
+        ),
     ]
 
 
@@ -1200,7 +1212,7 @@ async def test_be36_superadmin_reactivating_active_peer_returns_200(
 ):
     """The exception does not read the current state: an active peer still gets 200.
 
-    The audit row this no-op writes is BE-38 and is not frozen here.
+    A no-op: no audit row is written (ADR-0021).
     """
     superadmin = await persist_user(role=UserRole.superadmin)
     peer = await persist_user(role=UserRole.superadmin)
@@ -1221,6 +1233,8 @@ async def test_be36_superadmin_reactivating_active_peer_returns_200(
     assert peer.is_active is True
     assert peer.deleted_at is None
     assert peer.role == UserRole.superadmin
+    audits = (await db_session.execute(select(AuditLog))).scalars().all()
+    assert audits == []
 
 
 # --- BE-58 regression: an administrative account never deletes or deactivates itself ---
@@ -1324,6 +1338,8 @@ async def test_be58_admin_self_update_with_is_active_true_returns_200(
 
     await db_session.refresh(admin)
     assert admin.is_active is True
+    audits = (await db_session.execute(select(AuditLog))).scalars().all()
+    assert audits == []
 
 
 # ==========================================
--- a/tests/test_user_update_null.py
+++ b/tests/test_user_update_null.py
@@ -132,7 +132,7 @@ async def test_be37_null_on_phone_still_clears_it(
     assert target.phone is None
     audits = await _audit_rows(db_session)
     assert [(audit.entity_id, audit.changes) for audit in audits] == [
-        (target.cedula, {"phone": None})
+        (target.cedula, {"phone": {"old": "3001234567", "new": None}})
     ]
 
 
```

`tests/test_user_update_audit.py` (archivo nuevo, completo):

```python
"""Tests for BE-38: PATCH /usuarios/{cedula} audits only what changes, as old and new values.

changed_fields compares each validated value with the stored one after the access policy
(ADR-0021): a request that changes nothing answers 200 as before and writes no audit row, and
a partial change audits only the changed field. The policy still decides on the keys sent, so
an unchanged key it forbids is still a 403 (BE-02, ADR-0018).
"""

import pytest
from sqlalchemy import select

from app.models.audit import AuditAction, AuditLog
from app.models.user import User, UserRole


async def _audit_rows(db_session) -> list[AuditLog]:
    """Returns every audit row written so far, oldest first."""
    result = await db_session.execute(select(AuditLog).order_by(AuditLog.id))
    return list(result.scalars().all())


def _profile(user: User) -> tuple:
    """Returns the columns a PATCH can change, to compare them before and after."""
    return (user.email, user.first_name, user.last_name, user.phone, user.role, user.is_active)


@pytest.mark.parametrize(
    ("actor_role", "target_role", "payload"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, {"role": "admin"}, id="role-same"),
        pytest.param(UserRole.tourist, None, {"first_name": "John"}, id="first-name-same"),
        pytest.param(
            UserRole.admin, UserRole.tourist, {"first_name": "jOHN"}, id="first-name-normalized"
        ),
        pytest.param(UserRole.tourist, None, {"phone": None}, id="phone-null-already-null"),
        pytest.param(UserRole.admin, UserRole.tourist, {"is_active": True}, id="is-active-same"),
        pytest.param(
            UserRole.superadmin,
            UserRole.admin,
            {"role": "admin", "is_active": True, "first_name": "John", "last_name": "Doe"},
            id="four-keys-same",
        ),
    ],
)
async def test_be38_unchanged_user_update_returns_200_without_audit_row(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role, payload
):
    """Edge case: every key sent already holds its value; 200, nothing changes, no audit row."""
    actor = await persist_user(role=actor_role)
    target = actor if target_role is None else await persist_user(role=target_role)
    before = _profile(target)

    response = await client.patch(
        f"/usuarios/{target.cedula}", json=payload, headers=make_auth_headers(actor)
    )

    assert response.status_code == 200
    assert response.json()["cedula"] == target.cedula
    await db_session.refresh(target)
    assert _profile(target) == before
    assert await _audit_rows(db_session) == []


async def test_be38_email_in_another_case_is_unchanged(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: the schema lowercases the email (ADR-0016), so the same address is no change."""
    tourist = await persist_user()
    stored_email = tourist.email

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"email": stored_email.upper()},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 200
    assert response.json()["email"] == stored_email
    await db_session.refresh(tourist)
    assert tourist.email == stored_email
    assert await _audit_rows(db_session) == []


async def test_be38_partial_change_audits_only_the_changed_field(
    client, db_session, persist_user, make_auth_headers
):
    """Happy path: of two keys sent, only the changed one is audited, with its old value."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"first_name": "John", "last_name": "Nuevo"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    assert response.json()["last_name"] == "Nuevo"
    await db_session.refresh(admin)
    assert (admin.first_name, admin.last_name) == ("John", "Nuevo")
    audits = await _audit_rows(db_session)
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (
            AuditAction.UPDATE,
            admin.cedula,
            superadmin.cedula,
            {"last_name": {"old": "Doe", "new": "Nuevo"}},
        )
    ]


async def test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the policy reads the keys sent, not the ones that change (ADR-0018).

    first_name already holds its value; dropping it before the policy would turn this body
    into the bare reactivation that ADR-0018 allows.
    """
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True, "first_name": "John"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(peer)
    assert peer.is_active is False
    assert await _audit_rows(db_session) == []


async def test_be38_admin_self_role_with_unchanged_value_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the role key on one's own account is a 403 even with its value (BE-02)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "admin", "first_name": "Otro"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(admin)
    assert admin.first_name == "John"
    assert await _audit_rows(db_session) == []
```


## Anexo C — texto de la fase C

Diff contra la fase B:

```diff
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -109,6 +109,10 @@ class UserService:
     async def verify_email_account(self, token: str) -> dict:
         """Decodes the verification token and activates the user account.
 
+        The activation is audited as the same UPDATE of is_active an admin would write,
+        with the account as its own author. An account already active is left as it is
+        and writes no audit row; a soft-deleted account is never reached (ADR-0021).
+
         Args:
             token (str): Single-use JWT issued during registration.
 
@@ -118,7 +122,7 @@ class UserService:
         Raises:
             InvalidVerificationTokenError: Token corrupted, expired or
                 carrying an unexpected scope.
-            NotFoundError: No user matches the token subject.
+            NotFoundError: No non-deleted account matches the token subject.
         """
         settings = get_settings()
         try:
@@ -138,11 +142,23 @@ class UserService:
         if email is None or scope != EMAIL_VERIFICATION_SCOPE:
             raise InvalidVerificationTokenError("Token de verificación inválido.")
 
-        activation_success = await self.user_repo.activate_user(email)
+        user = await self.user_repo.get_non_deleted_user_by_email(email)
 
-        if not activation_success:
+        if user is None:
             raise NotFoundError("Usuario no encontrado.")
 
+        changes = changed_fields(user, {"is_active": True})
+        if changes:
+            user.is_active = True
+            await self.user_repo.save_user(user)
+            await self.audit_service.log_transaction(
+                entity_name="User",
+                entity_id=user.cedula,
+                action=AuditAction.UPDATE,
+                performed_by=user.cedula,
+                changes=changes,
+            )
+
         return {
             "success": True,
             "message": "Cuenta verificada exitosamente. Ya puede iniciar sesión.",
--- a/app/repositories/user_repository.py
+++ b/app/repositories/user_repository.py
@@ -51,19 +51,6 @@ class UserRepository:
         await self.db.refresh(user)
         return user
 
-    async def activate_user(self, email: str) -> bool:
-        """Mutates the user's is_active state to True. Returns False if user is not found."""
-        stmt = select(User).where(User.email == email)
-        result = await self.db.execute(stmt)
-        user = result.scalars().first()
-
-        if not user:
-            return False
-
-        user.is_active = True
-        await self.db.commit()
-        return True
-
     async def soft_delete_user(self, cedula: str) -> User | None:
         """Applies logical deletion by stamping the current UTC time on deleted_at.
 
--- a/tests/test_user_service.py
+++ b/tests/test_user_service.py
@@ -260,9 +260,10 @@ async def test_authenticate_inactive_account_raises_account_not_active(
 # ==========================================
 
 
-async def test_verify_email_activates_account(user_repo, user_service):
-    """Happy path: a valid token activates the account and returns success."""
-    user_repo.activate_user.return_value = True
+async def test_verify_email_activates_account(user_repo, audit_service, user_service, make_user):
+    """Happy path: a valid token activates the account and audits it as its own UPDATE."""
+    user = make_user(email="turista@example.com", is_active=False)
+    user_repo.get_non_deleted_user_by_email.return_value = user
 
     result = await user_service.verify_email_account(
         create_verification_token("turista@example.com")
@@ -270,7 +271,34 @@ async def test_verify_email_activates_account(user_repo, user_service):
 
     assert result["success"] is True
     assert "message" in result
-    user_repo.activate_user.assert_awaited_once_with("turista@example.com")
+    assert user.is_active is True
+    user_repo.get_non_deleted_user_by_email.assert_awaited_once_with("turista@example.com")
+    user_repo.save_user.assert_awaited_once_with(user)
+    audit_service.log_transaction.assert_awaited_once_with(
+        entity_name="User",
+        entity_id=user.cedula,
+        action=AuditAction.UPDATE,
+        performed_by=user.cedula,
+        changes={"is_active": {"old": False, "new": True}},
+    )
+
+
+async def test_verify_email_on_active_account_writes_nothing(
+    user_repo, audit_service, user_service, make_user
+):
+    """Edge case: an account already active is left as it is: no save and no audit row."""
+    user_repo.get_non_deleted_user_by_email.return_value = make_user(
+        email="turista@example.com", is_active=True
+    )
+
+    result = await user_service.verify_email_account(
+        create_verification_token("turista@example.com")
+    )
+
+    assert result["success"] is True
+    user_repo.get_non_deleted_user_by_email.assert_awaited_once_with("turista@example.com")
+    user_repo.save_user.assert_not_awaited()
+    audit_service.log_transaction.assert_not_awaited()
 
 
 async def test_verify_email_corrupt_token_raises_invalid_verification_token(
@@ -280,7 +308,7 @@ async def test_verify_email_corrupt_token_raises_invalid_verification_token(
     with pytest.raises(InvalidVerificationTokenError):
         await user_service.verify_email_account("not-a-jwt")
 
-    user_repo.activate_user.assert_not_awaited()
+    user_repo.get_non_deleted_user_by_email.assert_not_awaited()
 
 
 async def test_verify_email_expired_token_raises_invalid_verification_token(
@@ -296,7 +324,7 @@ async def test_verify_email_expired_token_raises_invalid_verification_token(
         await user_service.verify_email_account(expired_token)
 
     assert type(exc_info.value.__cause__) is jwt.ExpiredSignatureError
-    user_repo.activate_user.assert_not_awaited()
+    user_repo.get_non_deleted_user_by_email.assert_not_awaited()
 
 
 async def test_verify_email_wrong_scope_raises_invalid_verification_token(
@@ -308,7 +336,7 @@ async def test_verify_email_wrong_scope_raises_invalid_verification_token(
     with pytest.raises(InvalidVerificationTokenError):
         await user_service.verify_email_account(wrong_scope_token)
 
-    user_repo.activate_user.assert_not_awaited()
+    user_repo.get_non_deleted_user_by_email.assert_not_awaited()
 
 
 async def test_verify_email_rejects_access_token_whose_data_names_the_verification_scope(
@@ -322,16 +350,20 @@ async def test_verify_email_rejects_access_token_whose_data_names_the_verificati
     with pytest.raises(InvalidVerificationTokenError):
         await user_service.verify_email_account(forged_token)
 
-    user_repo.activate_user.assert_not_awaited()
+    user_repo.get_non_deleted_user_by_email.assert_not_awaited()
 
 
-async def test_verify_email_missing_user_raises_not_found(user_repo, user_service):
-    """Unhappy path: a valid token for a missing account maps to the 404 domain error."""
-    user_repo.activate_user.return_value = False
+async def test_verify_email_missing_user_raises_not_found(user_repo, audit_service, user_service):
+    """Unhappy path: a valid token with no non-deleted account behind it is the 404 error."""
+    user_repo.get_non_deleted_user_by_email.return_value = None
 
     with pytest.raises(NotFoundError):
         await user_service.verify_email_account(create_verification_token("ghost@example.com"))
 
+    user_repo.get_non_deleted_user_by_email.assert_awaited_once_with("ghost@example.com")
+    user_repo.save_user.assert_not_awaited()
+    audit_service.log_transaction.assert_not_awaited()
+
 
 # ==========================================
 # ADMINISTRATIVE PROVISIONING
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -11,6 +11,7 @@ from app.core.security import (
     get_password_hash,
 )
 from app.main import app
+from app.models.audit import AuditAction, AuditLog
 from app.models.user import User, UserRole
 
 USER_PAYLOAD: dict[str, Any] = {
@@ -102,6 +103,72 @@ async def test_verify_email_endpoint_activates_account(client, db_session, persi
 
     await db_session.refresh(user)
     assert user.is_active is True
+    audits = (await db_session.execute(select(AuditLog))).scalars().all()
+    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
+        (AuditAction.UPDATE, user.cedula, user.cedula, {"is_active": {"old": False, "new": True}})
+    ]
+
+
+async def test_be38_verify_email_on_active_account_returns_200_without_audit_row(
+    client, db_session, persist_user
+):
+    """Edge case: the link of an account already active changes nothing and writes no row."""
+    user = await persist_user(is_active=True)
+    token = create_verification_token(user.email)
+
+    response = await client.get(f"/usuarios/verificar-email?token={token}")
+
+    assert response.status_code == 200
+    assert response.json()["success"] is True
+    await db_session.refresh(user)
+    assert user.is_active is True
+    assert (await db_session.execute(select(AuditLog))).scalars().all() == []
+
+
+async def test_be38_verify_email_on_deleted_account_returns_404_without_mutation(
+    client, db_session, persist_user
+):
+    """Unhappy path: a soft-deleted account answers like an email without account (ADR-0021)."""
+    user = await persist_user(is_active=False, deleted_at=datetime.now(UTC))
+    token = create_verification_token(user.email)
+
+    response = await client.get(f"/usuarios/verificar-email?token={token}")
+
+    assert response.status_code == 404
+    body = response.json()
+    assert set(body) == {"detail"}
+    assert isinstance(body["detail"], str)
+    await db_session.refresh(user)
+    assert user.is_active is False
+    assert user.deleted_at is not None
+    assert (await db_session.execute(select(AuditLog))).scalars().all() == []
+
+
+async def test_be38_verify_email_after_admin_deactivation_writes_an_audit_row(
+    client, db_session, persist_user, make_auth_headers
+):
+    """Edge case: the link still reactivates an account an admin deactivated, now in the trail.
+
+    That the link can do it at all is BE-50; here only its audit row is frozen.
+    """
+    admin = await persist_user(role=UserRole.admin)
+    tourist = await persist_user()
+    token = create_verification_token(tourist.email)
+
+    deactivated = await client.patch(
+        f"/usuarios/{tourist.cedula}", json={"is_active": False}, headers=make_auth_headers(admin)
+    )
+    verified = await client.get(f"/usuarios/verificar-email?token={token}")
+
+    assert deactivated.status_code == 200
+    assert verified.status_code == 200
+    await db_session.refresh(tourist)
+    assert tourist.is_active is True
+    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
+    assert [(a.entity_id, a.performed_by, a.changes) for a in audits] == [
+        (tourist.cedula, admin.cedula, {"is_active": {"old": True, "new": False}}),
+        (tourist.cedula, tourist.cedula, {"is_active": {"old": False, "new": True}}),
+    ]
 
 
 async def test_verify_email_invalid_token_returns_400(client):
```


## Anexo D — texto de la fase D

Diff contra la fase C:

```diff
--- a/app/services/tourist_services_service.py
+++ b/app/services/tourist_services_service.py
@@ -8,7 +8,7 @@ from app.models.service import ServiceImage, TouristService
 from app.models.user import User
 from app.repositories.service_repository import ServiceRepository
 from app.schemas.service import ServiceCreate, ServiceUpdate
-from app.services.audit_service import AuditService
+from app.services.audit_service import AuditService, changed_fields
 
 
 class TouristServicesService:
@@ -108,6 +108,8 @@ class TouristServicesService:
         """Mutates the public availability state of a specific non-soft-deleted package.
 
         Transitions a package between the 'Por Activar' and 'Activos' columns.
+        Activating an active package or deactivating an inactive one changes nothing
+        and writes no audit row (ADR-0021).
 
         Args:
             service_id (int): The unique identifier of the package.
@@ -125,18 +127,19 @@ class TouristServicesService:
         if not service:
             raise NotFoundError(detail="Paquete no encontrado.")
 
-        service.is_available = is_available
-        await self.service_repo.save_service(service)
+        estado = "activado" if is_available else "desactivado"
 
-        action = AuditAction.ACTIVATE if is_available else AuditAction.DEACTIVATE
-        await self.audit_service.log_transaction(
-            entity_name="TouristService",
-            entity_id=str(service_id),
-            action=action,
-            performed_by=current_user.cedula,
-        )
+        if service.is_available != is_available:
+            service.is_available = is_available
+            await self.service_repo.save_service(service)
 
-        estado = "activado" if is_available else "desactivado"
+            action = AuditAction.ACTIVATE if is_available else AuditAction.DEACTIVATE
+            await self.audit_service.log_transaction(
+                entity_name="TouristService",
+                entity_id=str(service_id),
+                action=action,
+                performed_by=current_user.cedula,
+            )
 
         return {"success": True, "message": f"El paquete ha sido {estado} exitosamente."}
 
@@ -255,6 +258,9 @@ class TouristServicesService:
         Implements SQLAlchemy's 'delete-orphan' cascade by clearing the image
         relationship array and re-instantiating it, ensuring absolute sync
         with the incoming payload.
+        Only the fields whose value changes are audited, as old and new values; the
+        images count as the ordered list of stored URLs, with the promoted ones as new.
+        A request that changes nothing writes no audit row (ADR-0021).
 
         Args:
             service_id (int): The target package ID.
@@ -278,8 +284,9 @@ class TouristServicesService:
                 detail="Paquete no encontrado. Está deshabilitado (deleted_at != None) o no exíste."
             )
 
-        # 1. Update primitive fields (Scalar Mutation)
+        # 1. Update primitive fields (Scalar Mutation), once what changes is read
         update_dict = update_data.model_dump(exclude_unset=True, exclude={"image_urls"})
+        changes = changed_fields(service, update_dict)
         for key, value in update_dict.items():
             setattr(service, key, value)
 
@@ -309,6 +316,7 @@ class TouristServicesService:
                 )
 
             # 2.3 Set up image comparison basis and delete removed images (if there's any)
+            old_urls = [image.image_url for image in service.images]
             old_images_urls = {str(img.image_url) for img in service.images}
             urls_to_delete = old_images_urls - set(raw_urls)
 
@@ -333,15 +341,18 @@ class TouristServicesService:
                 nueva_imagen = ServiceImage(image_url=str(url), is_primary=(idx == 0))
                 service.images.append(nueva_imagen)
 
-        # 3. Register changes made on audit table
-        payload_changes = update_data.model_dump(mode="json", exclude_unset=True)
-        if payload_changes:
+            # 2.8 The images change when the ordered list of stored URLs does
+            if definitive_urls != old_urls:
+                changes["image_urls"] = {"old": old_urls, "new": definitive_urls}
+
+        # 3. Register what changed on the audit table
+        if changes:
             await self.audit_service.log_transaction(
                 entity_name="TouristService",
                 entity_id=str(service_id),
                 action=AuditAction.UPDATE,
                 performed_by=current_user.cedula,
-                changes=payload_changes,
+                changes=changes,
             )
 
         return await self.service_repo.save_service(service)
--- a/app/models/service.py
+++ b/app/models/service.py
@@ -26,6 +26,8 @@ class TouristService(Base):
 
     Owns its images: deleting a service removes them both in the ORM
     (``delete-orphan`` cascade) and in the database (``ON DELETE CASCADE`` foreign key).
+    They load in the order they were stored (by id), so the first one is the primary
+    image and the same list reads the same on every database (ADR-0021).
     """
 
     __tablename__ = "tourist_services"
@@ -45,7 +47,9 @@ class TouristService(Base):
     deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
 
     images: Mapped[list[ServiceImage]] = relationship(
-        back_populates="service", cascade="all, delete-orphan"
+        back_populates="service",
+        cascade="all, delete-orphan",
+        order_by=lambda: ServiceImage.id,
     )
 
 
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -22,7 +22,7 @@ from app.core.exceptions import (
 )
 from app.core.storage import AzureStorageClient, StagedImage
 from app.main import app
-from app.models.audit import AuditLog
+from app.models.audit import AuditAction, AuditLog
 from app.models.service import ServiceCategory, ServiceImage, TouristService
 from app.models.user import UserRole
 
@@ -837,7 +837,9 @@ async def test_be37_null_on_description_still_clears_it(client, db_session, admi
     await db_session.refresh(package)
     assert package.description is None
     audits = (await db_session.execute(select(AuditLog))).scalars().all()
-    assert [audit.changes for audit in audits] == [{"description": None}]
+    assert [audit.changes for audit in audits] == [
+        {"description": {"old": "Recorrido por la reserva", "new": None}}
+    ]
 
 
 async def test_be37_null_on_image_urls_still_keeps_the_images(
@@ -858,6 +860,7 @@ async def test_be37_null_on_image_urls_still_keeps_the_images(
     classifying_storage.delete_image.assert_not_awaited()
     classifying_storage.promote_to_permanent.assert_not_awaited()
     assert await _stored_image_urls(db_session, package_id) == [PERMANENT_URL]
+    assert (await db_session.execute(select(AuditLog))).scalars().all() == []
 
 
 @pytest.mark.parametrize(
@@ -877,3 +880,223 @@ async def test_be37_package_guard_answers_before_the_null(
     assert isinstance(response.json()["detail"], str)
     await db_session.refresh(package)
     assert package.name == "Paquete De Prueba Automatizada"
+
+
+# === BE-38: a package update audits only what changes, as old and new values (ADR-0021) ===
+# Scalars are compared with the stored row before any setattr; images, as the ordered list of
+# stored URLs, with the promoted ones as new. A request that changes nothing, and activating
+# an active package or deactivating an inactive one, answer as before and write no audit row.
+
+
+async def _audit_rows(db_session) -> list[AuditLog]:
+    """Returns every audit row written so far, oldest first."""
+    result = await db_session.execute(select(AuditLog).order_by(AuditLog.id))
+    return list(result.scalars().all())
+
+
+def _columns(package: TouristService) -> tuple:
+    """Returns the columns a PUT can change, to compare them before and after."""
+    return (
+        package.name,
+        package.description,
+        package.category,
+        package.base_price,
+        package.max_capacity,
+        package.is_available,
+    )
+
+
+@pytest.mark.parametrize(
+    "payload",
+    [
+        pytest.param({"name": "Paquete De Prueba Automatizada"}, id="name-same"),
+        pytest.param({"name": "paquete de prueba automatizada"}, id="name-normalized"),
+        pytest.param({"base_price": 50000}, id="price-same-value"),
+        pytest.param({"is_available": True}, id="available-same"),
+        pytest.param({"description": None}, id="description-null-already-null"),
+        pytest.param({"image_urls": []}, id="empty-images-without-images"),
+    ],
+)
+async def test_be38_unchanged_package_update_returns_200_without_audit_row(
+    client, db_session, admin_headers, storage_double, payload
+):
+    """Edge case: every key sent already holds its value; 200, no CDN call and no audit row."""
+    package = await _persist_package(db_session)
+    before = _columns(package)
+
+    response = await client.put(f"/servicios/{package.id}", json=payload, headers=admin_headers)
+
+    assert response.status_code == 200
+    assert response.json()["id"] == package.id
+    await db_session.refresh(package)
+    assert _columns(package) == before
+    storage_double.delete_image.assert_not_awaited()
+    storage_double.promote_to_permanent.assert_not_awaited()
+    assert await _audit_rows(db_session) == []
+
+
+async def test_be38_resent_image_list_returns_200_without_audit_row(
+    client, db_session, admin_headers, classifying_storage
+):
+    """Edge case: the stored URLs sent again in the same order are no change (P5)."""
+    second_url = f"{CDN_BASE}/ecotur-images/second.jpg"
+    package = await _persist_package(db_session)
+    package_id = package.id
+    db_session.add_all(
+        [
+            ServiceImage(service_id=package_id, image_url=PERMANENT_URL, is_primary=True),
+            ServiceImage(service_id=package_id, image_url=second_url, is_primary=False),
+        ]
+    )
+    await db_session.commit()
+
+    response = await client.put(
+        f"/servicios/{package_id}",
+        json={"image_urls": [PERMANENT_URL, second_url]},
+        headers=admin_headers,
+    )
+
+    assert response.status_code == 200
+    urls = [image["image_url"] for image in response.json()["images"]]
+    assert urls == [PERMANENT_URL, second_url]
+    classifying_storage.delete_image.assert_not_awaited()
+    classifying_storage.promote_to_permanent.assert_not_awaited()
+    assert await _audit_rows(db_session) == []
+
+
+async def test_be38_reordered_image_list_audits_the_new_order(
+    client, db_session, admin_headers, classifying_storage
+):
+    """Edge case: the same URLs in another order are a change: the first one is the primary."""
+    second_url = f"{CDN_BASE}/ecotur-images/second.jpg"
+    package = await _persist_package(db_session)
+    package_id = package.id
+    db_session.add_all(
+        [
+            ServiceImage(service_id=package_id, image_url=PERMANENT_URL, is_primary=True),
+            ServiceImage(service_id=package_id, image_url=second_url, is_primary=False),
+        ]
+    )
+    await db_session.commit()
+
+    response = await client.put(
+        f"/servicios/{package_id}",
+        json={"image_urls": [second_url, PERMANENT_URL]},
+        headers=admin_headers,
+    )
+
+    assert response.status_code == 200
+    assert response.json()["images"][0]["image_url"] == second_url
+    classifying_storage.delete_image.assert_not_awaited()
+    audits = await _audit_rows(db_session)
+    assert [a.changes for a in audits] == [
+        {"image_urls": {"old": [PERMANENT_URL, second_url], "new": [second_url, PERMANENT_URL]}}
+    ]
+
+
+async def test_be38_partial_package_change_audits_only_the_changed_field(
+    client, db_session, admin_headers
+):
+    """Happy path: of two keys sent, only the changed one is audited, with its old value."""
+    package = await _persist_package(db_session)
+
+    response = await client.put(
+        f"/servicios/{package.id}",
+        json={"name": "Paquete De Prueba Automatizada", "max_capacity": 20},
+        headers=admin_headers,
+    )
+
+    assert response.status_code == 200
+    assert response.json()["max_capacity"] == 20
+    await db_session.refresh(package)
+    assert package.max_capacity == 20
+    audits = await _audit_rows(db_session)
+    assert [(a.action, a.entity_id, a.changes) for a in audits] == [
+        (AuditAction.UPDATE, str(package.id), {"max_capacity": {"old": 15, "new": 20}})
+    ]
+
+
+async def test_be38_price_change_audits_old_and_new_values(client, db_session, admin_headers):
+    """Happy path: the price is compared by value and audited as text, old and new."""
+    package = await _persist_package(db_session)
+
+    response = await client.put(
+        f"/servicios/{package.id}", json={"base_price": 60000}, headers=admin_headers
+    )
+
+    assert response.status_code == 200
+    await db_session.refresh(package)
+    assert package.base_price == Decimal("60000.00")
+    audits = await _audit_rows(db_session)
+    assert [a.changes for a in audits] == [{"base_price": {"old": "50000.00", "new": "60000"}}]
+
+
+async def test_be38_image_change_audits_the_stored_urls(
+    client, db_session, admin_headers, classifying_storage
+):
+    """Happy path: new is the list as stored, with the temporal URL already promoted (P6)."""
+    promoted_url = f"{CDN_BASE}/ecotur-images/new.jpg"
+    classifying_storage.promote_to_permanent.return_value = promoted_url
+    package = await _persist_package(db_session)
+    package_id = package.id
+    db_session.add(ServiceImage(service_id=package_id, image_url=PERMANENT_URL, is_primary=True))
+    await db_session.commit()
+
+    response = await client.put(
+        f"/servicios/{package_id}",
+        json={"image_urls": [PERMANENT_URL, TEMP_URL]},
+        headers=admin_headers,
+    )
+
+    assert response.status_code == 200
+    classifying_storage.promote_to_permanent.assert_awaited_once_with(TEMP_URL)
+    assert await _stored_image_urls(db_session, package_id) == [PERMANENT_URL, promoted_url]
+    audits = await _audit_rows(db_session)
+    assert [a.changes for a in audits] == [
+        {"image_urls": {"old": [PERMANENT_URL], "new": [PERMANENT_URL, promoted_url]}}
+    ]
+
+
+@pytest.mark.parametrize(
+    ("route", "is_available"),
+    [
+        pytest.param("activar", True, id="activate-active"),
+        pytest.param("desactivar", False, id="deactivate-inactive"),
+    ],
+)
+async def test_be38_status_route_without_change_returns_200_without_audit_row(
+    client, db_session, admin_headers, route, is_available
+):
+    """Edge case: activating an active package or deactivating an inactive one writes no row."""
+    package = await _persist_package(db_session, is_available=is_available)
+
+    response = await client.patch(f"/servicios/{package.id}/{route}", headers=admin_headers)
+
+    assert response.status_code == 200
+    assert set(response.json()) == {"success", "message"}
+    await db_session.refresh(package)
+    assert package.is_available is is_available
+    assert await _audit_rows(db_session) == []
+
+
+@pytest.mark.parametrize(
+    ("route", "is_available", "action"),
+    [
+        pytest.param("activar", False, AuditAction.ACTIVATE, id="activate-inactive"),
+        pytest.param("desactivar", True, AuditAction.DEACTIVATE, id="deactivate-active"),
+    ],
+)
+async def test_be38_status_route_with_change_audits_the_action(
+    client, db_session, admin_headers, route, is_available, action
+):
+    """Happy path: a real change of state still writes its ACTIVATE or DEACTIVATE row."""
+    package = await _persist_package(db_session, is_available=is_available)
+
+    response = await client.patch(f"/servicios/{package.id}/{route}", headers=admin_headers)
+
+    assert response.status_code == 200
+    assert response.json()["success"] is True
+    await db_session.refresh(package)
+    assert package.is_available is not is_available
+    audits = await _audit_rows(db_session)
+    assert [(a.action, a.entity_id, a.changes) for a in audits] == [(action, str(package.id), None)]
--- a/tests/test_models_schema.py
+++ b/tests/test_models_schema.py
@@ -156,3 +156,11 @@ def test_service_relationships_keep_target_direction_and_cascade() -> None:
     assert service.uselist is False
     assert service.back_populates == "images"
     assert set(service.cascade) == {"save-update", "merge"}
+
+
+def test_service_images_load_in_stored_order() -> None:
+    """The images load by id, so a package lists them as stored on any database (BE-38, R1)."""
+    order_by = inspect(TouristService).relationships["images"].order_by
+
+    assert order_by is not False
+    assert [str(column) for column in order_by] == ["service_images.id"]
```


## Anexo E(a) — fase E con la opción (a), `populate_existing`

Diff contra la fase D:

```diff
--- a/app/repositories/service_repository.py
+++ b/app/repositories/service_repository.py
@@ -16,11 +16,14 @@ class ServiceRepository:
         self.db.add(service)
         await self.db.commit()
         # The freshest db registry, in which all the tourist service's images are properly
-        # linked to their corresponding service, is retrieved.
+        # linked to their corresponding service, is retrieved. populate_existing reloads the
+        # scalars of the instance this session already holds too, so the caller gets what the
+        # database stored (the price with the two decimals of its column).
         stmt = (
             select(TouristService)
             .options(selectinload(TouristService.images))
             .where(TouristService.id == service.id)
+            .execution_options(populate_existing=True)
         )
         result = await self.db.execute(stmt)
         return result.scalar_one()
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -1100,3 +1100,32 @@ async def test_be38_status_route_with_change_audits_the_action(
     assert package.is_available is not is_available
     audits = await _audit_rows(db_session)
     assert [(a.action, a.entity_id, a.changes) for a in audits] == [(action, str(package.id), None)]
+
+
+# === BE-38: the price reads with the two decimals of its column (ADR-0021) ===
+
+
+@pytest.mark.parametrize(
+    ("sent", "answered"),
+    [
+        pytest.param(50000, "50000.00", id="integer"),
+        pytest.param(50000.5, "50000.50", id="one-decimal"),
+        pytest.param(50000.75, "50000.75", id="two-decimals"),
+    ],
+)
+async def test_be38_create_answers_the_price_with_two_decimals(
+    client, db_session, admin_headers, storage_double, sent, answered
+):
+    """Happy path: POST answers the price as its column stores it, the same as GET."""
+    storage_double.promote_to_permanent.return_value = PERMANENT_URL
+    payload = {**_create_payload([TEMP_URL]), "base_price": sent}
+
+    created = await client.post("/servicios/", json=payload, headers=admin_headers)
+    listed = await client.get("/servicios/")
+
+    assert created.status_code == 201
+    assert created.json()["base_price"] == answered
+    assert [package["base_price"] for package in listed.json()] == [answered]
+    stored = await db_session.get(TouristService, created.json()["id"])
+    assert stored is not None
+    assert stored.base_price == Decimal(answered)
```


## Anexo E(b) — fase E con la opción (b), dos decimales al entrar

Diff contra la fase D (incluye la línea reescrita del test de precio de D; 98 columnas):

```diff
--- a/app/schemas/service.py
+++ b/app/schemas/service.py
@@ -7,6 +7,9 @@ from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
 from app.models.service import ServiceCategory
 from app.schemas.partial_update import NoExplicitNull
 
+# Scale of tourist_services.base_price, NUMERIC(10, 2): every price is written with two decimals.
+_CENTS = Decimal("0.01")
+
 
 class ServiceImageResponse(BaseModel):
     id: int
@@ -51,6 +54,12 @@ class ServiceBase(BaseModel):
 
         return clean.title()
 
+    @field_validator("base_price")
+    @classmethod
+    def format_base_price(cls, v: Decimal) -> Decimal:
+        """Writes the price with the two decimals of its column: 50000 becomes 50000.00."""
+        return v.quantize(_CENTS)
+
 
 class ServiceCreate(ServiceBase):
     # HttpUrl delegates the image url string domain and protocol verification to Rust.
@@ -130,3 +139,9 @@ class ServiceUpdate(BaseModel):
         """Title-cases the package name and collapses repeated whitespace."""
         clean = " ".join(v.split())
         return clean.title()
+
+    @field_validator("base_price")
+    @classmethod
+    def format_base_price(cls, v: Decimal) -> Decimal:
+        """Writes the price with the two decimals of its column: 50000 becomes 50000.00."""
+        return v.quantize(_CENTS)
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -12,6 +12,7 @@ from typing import Any
 from unittest.mock import create_autospec
 
 import pytest
+from pydantic import ValidationError
 from sqlalchemy import select
 
 from app.api.dependencies import get_storage_client
@@ -25,6 +26,7 @@ from app.main import app
 from app.models.audit import AuditAction, AuditLog
 from app.models.service import ServiceCategory, ServiceImage, TouristService
 from app.models.user import UserRole
+from app.schemas.service import ServiceUpdate
 
 # ==========================================
 # TEST FIXTURES (Context Setup)
@@ -1028,7 +1030,7 @@ async def test_be38_price_change_audits_old_and_new_values(client, db_session, a
     await db_session.refresh(package)
     assert package.base_price == Decimal("60000.00")
     audits = await _audit_rows(db_session)
-    assert [a.changes for a in audits] == [{"base_price": {"old": "50000.00", "new": "60000"}}]
+    assert [a.changes for a in audits] == [{"base_price": {"old": "50000.00", "new": "60000.00"}}]
 
 
 async def test_be38_image_change_audits_the_stored_urls(
@@ -1100,3 +1102,66 @@ async def test_be38_status_route_with_change_audits_the_action(
     assert package.is_available is not is_available
     audits = await _audit_rows(db_session)
     assert [(a.action, a.entity_id, a.changes) for a in audits] == [(action, str(package.id), None)]
+
+
+# === BE-38: the price reads with the two decimals of its column (ADR-0021) ===
+
+
+@pytest.mark.parametrize(
+    ("sent", "answered"),
+    [
+        pytest.param(50000, "50000.00", id="integer"),
+        pytest.param(50000.5, "50000.50", id="one-decimal"),
+        pytest.param(50000.75, "50000.75", id="two-decimals"),
+    ],
+)
+async def test_be38_create_answers_the_price_with_two_decimals(
+    client, db_session, admin_headers, storage_double, sent, answered
+):
+    """Happy path: POST answers the price as its column stores it, the same as GET."""
+    storage_double.promote_to_permanent.return_value = PERMANENT_URL
+    payload = {**_create_payload([TEMP_URL]), "base_price": sent}
+
+    created = await client.post("/servicios/", json=payload, headers=admin_headers)
+    listed = await client.get("/servicios/")
+
+    assert created.status_code == 201
+    assert created.json()["base_price"] == answered
+    assert [package["base_price"] for package in listed.json()] == [answered]
+    stored = await db_session.get(TouristService, created.json()["id"])
+    assert stored is not None
+    assert stored.base_price == Decimal(answered)
+
+
+@pytest.mark.parametrize(
+    ("sent", "answered"),
+    [
+        pytest.param(60000, "60000.00", id="integer"),
+        pytest.param(60000.5, "60000.50", id="one-decimal"),
+        pytest.param(60000.75, "60000.75", id="two-decimals"),
+    ],
+)
+async def test_be38_update_answers_the_price_with_two_decimals(
+    client, db_session, admin_headers, sent, answered
+):
+    """Happy path: PUT answers the new price as its column stores it, the same as GET."""
+    package = await _persist_package(db_session)
+
+    updated = await client.put(
+        f"/servicios/{package.id}", json={"base_price": sent}, headers=admin_headers
+    )
+    listed = await client.get("/servicios/")
+
+    assert updated.status_code == 200
+    assert updated.json()["base_price"] == answered
+    assert [item["base_price"] for item in listed.json()] == [answered]
+    await db_session.refresh(package)
+    assert package.base_price == Decimal(answered)
+
+
+def test_be38_schema_keeps_rejecting_a_third_decimal() -> None:
+    """Unhappy path: two decimals are written, never rounded; a third one is still a 422."""
+    with pytest.raises(ValidationError) as exc_info:
+        ServiceUpdate.model_validate({"base_price": "50000.555"})
+
+    assert [error["loc"] for error in exc_info.value.errors()] == [("base_price",)]
```


## Anexo F — texto de la fase F

Diff contra la fase E con la opción (a) (con la (b), idéntico salvo los números de línea):

```diff
--- a/app/services/tourist_services_service.py
+++ b/app/services/tourist_services_service.py
@@ -8,7 +8,7 @@ from app.models.service import ServiceImage, TouristService
 from app.models.user import User
 from app.repositories.service_repository import ServiceRepository
 from app.schemas.service import ServiceCreate, ServiceUpdate
-from app.services.audit_service import AuditService, changed_fields
+from app.services.audit_service import AuditService, audit_value, changed_fields
 
 
 class TouristServicesService:
@@ -30,7 +30,9 @@ class TouristServicesService:
         """Creates a package, promoting its staged images to the permanent container.
 
         A new package only accepts blobs of the temporal container (uploaded first through
-        the staging endpoint); any other URL is rejected before touching the CDN.
+        the staging endpoint); any other URL is rejected before touching the CDN. The CREATE
+        row records the package as stored: its saved columns and its promoted image URLs, in
+        order (ADR-0021).
 
         Args:
             package_data: Validated creation payload, including the image URLs.
@@ -67,12 +69,14 @@ class TouristServicesService:
 
         saved = await self.service_repo.create_service(new_tourist_service)
 
+        stored = {field: audit_value(getattr(saved, field)) for field in tourist_service_data}
+        stored["image_urls"] = [image.image_url for image in saved.images]
         await self.audit_service.log_transaction(
             entity_name="TouristService",
             entity_id=str(saved.id),
             action=AuditAction.CREATE,
             performed_by=current_user.cedula,
-            changes=package_data.model_dump(mode="json"),
+            changes=stored,
         )
 
         return saved
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -455,7 +455,10 @@ async def test_create_package_promotion_outage_returns_503(
 async def test_create_package_promotes_temporal_url(
     client, admin_headers, storage_double, db_session
 ):
-    """Happy path: a temporal URL is promoted and stored as the primary image."""
+    """Happy path: a temporal URL is promoted and stored as the primary image.
+
+    The CREATE row records the package as stored, not the body sent (BE-61, ADR-0021).
+    """
     storage_double.promote_to_permanent.return_value = PERMANENT_URL
 
     response = await client.post(
@@ -469,7 +472,21 @@ async def test_create_package_promotes_temporal_url(
     assert images[0]["is_primary"] is True
     storage_double.promote_to_permanent.assert_awaited_once_with(TEMP_URL)
     audits = (await db_session.execute(select(AuditLog))).scalars().all()
-    assert len(audits) == 1
+    assert [(a.action, a.entity_id, a.changes) for a in audits] == [
+        (
+            AuditAction.CREATE,
+            str(response.json()["id"]),
+            {
+                "name": "Paquete De Imagenes Validadas",
+                "description": "Cuerpo valido para probar la clasificacion de URLs de imagen.",
+                "category": "otro",
+                "base_price": "50000.00",
+                "max_capacity": 10,
+                "is_available": True,
+                "image_urls": [PERMANENT_URL],
+            },
+        )
+    ]
 
 
 async def test_upload_images_non_image_returns_415(client, admin_headers, storage_double):
@@ -1129,3 +1146,30 @@ async def test_be38_create_answers_the_price_with_two_decimals(
     stored = await db_session.get(TouristService, created.json()["id"])
     assert stored is not None
     assert stored.base_price == Decimal(answered)
+
+
+# === BE-61: the CREATE row of a package records it as stored (ADR-0021) ===
+
+
+async def test_be61_create_audits_every_promoted_url_in_order(
+    client, db_session, admin_headers, storage_double
+):
+    """Edge case: with two images, the CREATE row lists both promoted URLs in the order sent."""
+    second_temp = f"{CDN_BASE}/temp-ecotur-images/second.jpg"
+    second_permanent = f"{CDN_BASE}/ecotur-images/second.jpg"
+    storage_double.promote_to_permanent.side_effect = [PERMANENT_URL, second_permanent]
+
+    response = await client.post(
+        "/servicios/", json=_create_payload([TEMP_URL, second_temp]), headers=admin_headers
+    )
+
+    assert response.status_code == 201
+    urls = [image["image_url"] for image in response.json()["images"]]
+    assert urls == [PERMANENT_URL, second_permanent]
+    awaited = [call.args for call in storage_double.promote_to_permanent.await_args_list]
+    assert awaited == [(TEMP_URL,), (second_temp,)]
+    audits = await _audit_rows(db_session)
+    assert [a.action for a in audits] == [AuditAction.CREATE]
+    changes = audits[0].changes
+    assert changes is not None
+    assert changes["image_urls"] == [PERMANENT_URL, second_permanent]
```


## Anexo G — texto de la fase G

`app/models/audit.py`, diff contra la fase F:

```diff
--- a/app/models/audit.py
+++ b/app/models/audit.py
@@ -24,15 +24,15 @@ class AuditAction(str, enum.Enum):  # noqa: UP042 (backlog D2)
 class AuditLog(Base):
     """SQLAlchemy domain model for the Audit Trail ecosystem.
 
-    Utilizes PostgreSQL's native JSONB data type to store structural
-    snapshots of domain entities regardless of their rigid schema.
+    changes holds, on UPDATE, {field: {"old": ..., "new": ...}} for the fields that
+    changed; on CREATE, the values of the new row; on any other action, None (ADR-0021).
     """
 
     __tablename__ = "audit_logs"
 
     id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
-    # "User" o "TouristService"
+    # "User" or "TouristService"
     entity_name: Mapped[str] = mapped_column(String(50), index=True)
 
     # String to gracefully support both INT (Service ID) and VARCHAR (Cedula)
@@ -40,7 +40,7 @@ class AuditLog(Base):
 
     action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, name="audit_action_enum"))
 
-    # Dictionary snapshot containing 'old_values' and 'new_values'
+    # UPDATE: {field: {"old", "new"}}; CREATE: the values of the new row (ADR-0021)
     changes: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
 
     # The 'cedula' of the administrator who triggered the transaction
```

ADR-0021 (archivo nuevo, completo) con la opción (a); `<FECHA>` (formato `18 nov 2026`) se sustituye por la de la aprobación:

```markdown
# ADR-0021 — La auditoría registra solo lo que cambió, con su valor anterior y el nuevo

- **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-38)
- **Propuesta:** Claude, `plan-redactor` (17 y 18 nov 2026), sobre las dos adendas de David a la
  verificación (17 nov, 17:24 y 18:37) y la revisión de la sesión Mentor (18 nov)
- **Ubicación en el repo:** `docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md`
- **Origen:** backlog BE-38 (BE-61 como fila hija); `docs/deuda/BE-38/verificacion.md`;
  `docs/deuda/BE-38/plan.md`. Relación: ADR-0015 (su punto 6 fija el `changes` del bootstrap; no se
  supersede), ADR-0016 (el correo se compara ya en minúsculas), ADR-0018 (la excepción entre
  superadmins sigue decidiendo por claves), ADR-0020 (ausente no es `null`).

## Contexto

`PATCH /usuarios/{cedula}` y `PUT /servicios/{id}` escribían en `audit_logs.changes` el cuerpo
validado, cambiara o no la fila: una clave reenviada con su valor dejaba un `UPDATE`, activar un
paquete activo dejaba un `ACTIVATE`, y la fila de un paquete guardaba la URL temporal enviada y no
la definitiva. Verificar el correo activaba una cuenta sin fila, también una borrada. El alta de una
cuenta administrativa escribía su `CREATE` antes del alta y lo conservaba si el alta fallaba (409 o
500), una vez sobre la cédula de otra cuenta. La vista de auditoría se usa en la demostración de la
sustentación.

## Decisión

1. **Una modificación (`UPDATE`) registra solo los campos cuyo valor cambió**, como `{campo: {"old":
   <anterior>, "new": <nuevo>}}`, en la misma columna `changes`, sin migración.
2. **"Cambió" compara el valor ya validado con el de la fila, como valores de Python**
   (`Decimal("50000") == Decimal("50000.00")`; un correo en otra grafía o un nombre que el schema
   normaliza al guardado no cambian). `old` y `new` se guardan en forma JSON. La comparación va
   después de la política de acceso, que decide por las claves recibidas.
3. **Una petición que no cambia nada responde como siempre y no escribe fila**, también activar un
   paquete activo, desactivar uno inactivo o usar el enlace de verificación sobre una cuenta ya
   activa.
4. **Las imágenes de un paquete se comparan como lista ordenada de URL** (la primera es la
   principal), no como filas; `new` es la lista guardada, con las temporales ya promovidas.
   `image_urls: null` no cambia nada. Las imágenes se cargan en el orden en que se guardaron (por
   `id`), para que la misma lista se lea igual en cualquier base.
5. **La activación por correo es un `UPDATE`** con `{"is_active": {"old": false, "new": true}}`, con
   la cédula de la cuenta en `entity_id` y en `performed_by`, y no alcanza a cuentas borradas
   (responde como un correo sin cuenta).
6. **Un alta (`CREATE`) se audita después de guardar y registra lo guardado, en forma de valores,
   sin `old`/`new`.** `SOFT_DELETE`, `RECOVER`, `ACTIVATE` y `DEACTIVATE` siguen sin `changes`.
7. **Las filas anteriores no se migran**: el valor anterior no se puede reconstruir. Un lector
   distingue el formato por la forma: en una fila `UPDATE` nueva cada valor de `changes` es un
   objeto con exactamente `old` y `new`; en las anteriores es el dato enviado (ningún campo auditado
   es un objeto).
8. **El alta devuelve el paquete como lo guardó la base** (`populate_existing` en
   `ServiceRepository.create_service`): la fila `CREATE` y la respuesta llevan el precio con la
   escala de su columna.

## Consecuencias

- Cambia la forma de `changes` en las filas `UPDATE` de `GET /auditoria/`, y la tabla mezcla dos
  formatos (punto 7). David comprueba el panel del cliente Flutter antes de mezclar.
- `POST /servicios/` responde el precio como lo devuelve la base (`"50000.00"`), como `GET`. En una
  modificación, `PUT` responde y `new` registra la grafía validada (`"60000"`), y `old` la de la
  columna (`"50000.00"`).
- No se adelanta la Unit of Work (A3): alta y auditoría siguen en dos `commit()`. Si falla la
  escritura de auditoría, la mutación queda sin su fila (medido en el registro).
- Reenviar la misma lista de imágenes sigue recreando sus filas, ahora sin fila de auditoría. Que el
  enlace reactive una cuenta desactivada por un admin sigue ocurriendo (BE-50), pero deja de ser
  invisible.

## Alternativas consideradas

1. **Conservar `{campo: valor_nuevo}` de lo que cambió** (recomendación de la sesión Mentor).
   Rechazada por David: la vista no mostraría desde qué valor se cambió.
2. **Columnas `old_values`/`new_values`.** Rechazada: migración sin ganancia; el JSONB ya admite la
   forma.
3. **Fila con `changes` vacío para un no-cambio.** Rechazada: la tabla registra cambios, no
   intentos.
4. **Acción `VERIFY` para la activación por correo.** Rechazada: migración del enum; "la cuenta pasó
   a activa" se escribe de una sola manera, la active un admin o un enlace.
5. **Hacer atómicas alta y auditoría ya.** Rechazada aquí: es A3 y toca el `commit()` del que
   dependen once puntos.
6. **Escribir el precio con dos decimales al entrar, en el schema.** Descartada al aprobar el plan
   (opción b): toca los dos DTO de entrada y cambia también la respuesta de `PUT`.

## Evidencia

- Verificación (17 nov): sondas U1–U13 y P1–P14; re-verificación V1–V6 y C1–C4, y barrido de los
  once puntos que auditan.
- Plan (17 y 18 nov): RED y GREEN de cada fase, compuerta completa y mutantes, medidos en copia del
  repositorio; el orden de las imágenes no cambia el esquema (comparación de metadatos medida).
  Detalle: `docs/deuda/BE-38/plan.md`.
```

Con la opción (b), estas son las únicas líneas que cambian (diff del archivo (a) al (b)):

```diff
--- a/docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md
+++ b/docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md
@@ -43,17 +43,17 @@ sustentación.
    distingue el formato por la forma: en una fila `UPDATE` nueva cada valor de `changes` es un
    objeto con exactamente `old` y `new`; en las anteriores es el dato enviado (ningún campo auditado
    es un objeto).
-8. **El alta devuelve el paquete como lo guardó la base** (`populate_existing` en
-   `ServiceRepository.create_service`): la fila `CREATE` y la respuesta llevan el precio con la
-   escala de su columna.
+8. **El precio se escribe con los dos decimales de su columna al entrar** (`ServiceCreate` y
+   `ServiceUpdate`): las respuestas de `POST`, `PUT` y `GET`, la fila `CREATE` y `old`/`new` lo
+   muestran igual (`"60000.00"`). Un tercer decimal sigue siendo 422: se escribe la escala, no se
+   redondea.
 
 ## Consecuencias
 
 - Cambia la forma de `changes` en las filas `UPDATE` de `GET /auditoria/`, y la tabla mezcla dos
   formatos (punto 7). David comprueba el panel del cliente Flutter antes de mezclar.
-- `POST /servicios/` responde el precio como lo devuelve la base (`"50000.00"`), como `GET`. En una
-  modificación, `PUT` responde y `new` registra la grafía validada (`"60000"`), y `old` la de la
-  columna (`"50000.00"`).
+- `POST /servicios/` y `PUT /servicios/{id}` responden el precio con dos decimales (`"50000.00"`),
+  como `GET`.
 - No se adelanta la Unit of Work (A3): alta y auditoría siguen en dos `commit()`. Si falla la
   escritura de auditoría, la mutación queda sin su fila (medido en el registro).
 - Reenviar la misma lista de imágenes sigue recreando sus filas, ahora sin fila de auditoría. Que el
@@ -72,8 +72,8 @@ sustentación.
    a activa" se escribe de una sola manera, la active un admin o un enlace.
 5. **Hacer atómicas alta y auditoría ya.** Rechazada aquí: es A3 y toca el `commit()` del que
    dependen once puntos.
-6. **Escribir el precio con dos decimales al entrar, en el schema.** Descartada al aprobar el plan
-   (opción b): toca los dos DTO de entrada y cambia también la respuesta de `PUT`.
+6. **`populate_existing` en `ServiceRepository.create_service`.** Descartada al aprobar el plan
+   (opción a): iguala el alta, pero `PUT` y `new` conservan la grafía enviada (`"60000"`).
 
 ## Evidencia
 
```

## Enmiendas aprobadas

### E0 — 18 nov 2026, 11:02 (David: "b y sí"; revisión de la sesión Mentor)

1. **Plan aprobado, siete fases, y ADR-0021 aceptado** con el texto del Anexo G en su variante de la opción (b).
   `<FECHA>` = `18 nov 2026`.
2. **Decisión pendiente 1, el precio: opción (b), dos decimales al entrar, en el schema.** El ejecutor de la fase E
   aplica el Anexo E(b) y solo ese; el Anexo E(a) no se ejecuta. Todas las cifras "(b)" del plan son las que rigen:
   E 796 passed · 98,69 %; F y G 797 passed · 98,69 %; comando 11 con `_CENTS` (3 líneas en `app/schemas/service.py`);
   comando 14 con 12 funciones en `tests/test_services.py` y `36 passed`; comando 15 con
   `app/repositories/service_repository.py` añadido a la lista de lo que no cambia. Se acepta que M2 deje de morir tras
   E (riesgo 4, R7). R3 desaparece.
3. **Decisiones pendientes 2 a 5, aprobadas como vienen:** las cuatro propuestas de la primera adenda; la excepción a
   AGENTS §5 en las fases A y C; R1 dentro de la fase D; textos de ADR-0021 y de los commits.
4. **`alembic check` antes y después de la fase D: lo ejecuta David, y es condición (corrige "no exige" del Análisis).**
   La fase D toca `app/models/service.py`, y ADR-0010, punto 7, pide para cualquier refactor de modelos `alembic check`
   contra la base real antes y después, con la misma salida, sin distinguir si cambia el esquema. La evidencia del plan
   (DDL idéntico, `compare_metadata` vacío, test de esquema en verde) se mantiene; esto la completa. **No lo hace un
   agente:** Alembic lee `DATABASE_URL` del `.env`, que los agentes no leen (AGENTS §2), y la base local es de David
   (mismo reparto que el paso 19 de BE-34). Desde `cmd`, con el PostgreSQL local encendido:
   ```
   venv\Scripts\python.exe -m alembic current
   venv\Scripts\python.exe -m alembic check
   ```
   Una vez **antes de `/implementar BE-38 D`** y otra **después de su auditoría**. Las dos deben dar el mismo `head` y
   `No new upgrade operations detected.`; la salida literal va a la bitácora. Si difieren, la fase D no se da por
   buena y se avisa a la sesión Mentor. El ejecutor y el auditor de D no lo corren ni lo esperan: su criterio es el del
   plan. Cierra R8.
5. **Nota de David, de memoria y por comprobar (11:02):** cree que la pantalla de edición de un paquete del cliente
   Flutter reenvía siempre la lista de imágenes con que cargó el paquete, y teme que entonces toda modificación deje
   fila de imágenes. **El plan ya cubre ese caso:** una lista reenviada igual y en el mismo orden no deja fila
   (`test_be38_resent_image_list_returns_200_without_audit_row`, P5), y el `order_by` de R1 es lo que hace que el orden
   que el cliente recibe y devuelve sea siempre el mismo también en PostgreSQL. Lo que sí dejaría fila, y sería un
   cambio real (cambia la imagen principal), es que el cliente devuelva la lista en otro orden. **El paso humano de la
   Verificación final se amplía:** además del panel de auditoría, David comprueba en el cliente qué envía la pantalla
   de edición en `image_urls` (si lo envía siempre, y en qué orden).
6. **Residuales con destino:** R2, nota en la fila BE-26; R4, nota en la fila BE-49; R3, sin efecto con (b); R7,
   aceptado; R8, punto 4; R5 y R6, como dice el plan (la viñeta de AGENTS §3, después de la auditoría de G).
7. **Sin correcciones de dictado.** La sesión Mentor leyó enteras las líneas 1–640 (cabecera, resumen, análisis, fases,
   Verificación final, residuales, referencias) y, de los anexos, el código de `app/` de las fases B, C, D, E(b) y F y
   parte de ADR-0021; no leyó las salidas de "Mediciones" completas, el Anexo A ni el texto de los tests. Contrastado
   contra `44b1fce`: en D, `changed_fields` antes del `setattr` y `old_urls` antes de `images.clear()`; en C,
   `get_non_deleted_user_by_email` ya filtra `deleted_at`; en E(b), de `ServiceBase` solo hereda `ServiceCreate`
   (`app/schemas/service.py:55`; los DTO de salida heredan de `BaseModel`, `:67` y `:86`), así que A9 se cumple.

### E1 — 18 nov 2026, 17:40 (David: "entonces tienes permiso para E1"; opcional de la auditoría de la fase D)

1. **En las fases E, F y G los mutantes se corren en copias, nunca sobre el árbol de trabajo del repo.** El ejecutor
   hace el commit de la fase con la compuerta en verde y después mide sus mutantes en copias `git archive <commit de la
   fase>` en el scratchpad, una por mutante, con la suite completa; el auditor ya lo hace así. Precisa la frase "el
   ejecutor de cada fase repite los suyos sobre su fase" (sección de mutantes del Análisis), que no decía dónde.
2. **Motivo.** En la fase D los seis mutantes se aplicaron sobre el árbol con la fase sin commitear y se restauraron a
   mano (`handoff-D.md`, "Mutantes de la fase"; `gaps.md`, opcional de D). No quedó resto: el auditor comparó los
   cuatro archivos por md5 contra el Anexo D y contra `53ea731`. Pero la compuerta solo delata un mutante olvidado si
   algún test lo mata, y M2 vive desde la fase E (E0.2, riesgo 4): aplicado en el árbol y sin restaurar, entraría en
   el commit con `check.py` en 0.
3. **Si un mutante que el plan da por muerto vive en la copia,** el ejecutor no lo arregla dentro de la fase: lo
   declara en su handoff y se detiene; lo decide la sesión Mentor con David.
4. **No cambia** código, tests, anexos, cifras, criterios de aceptación, la tabla de fases ni la Verificación final.
   `progress.json` no se toca: ninguna descripción de fase depende de dónde se miden los mutantes.

### E2 — 18 nov 2026, 18:32 (David: "Si, opción 1"; opcional de la auditoría de la fase E)

1. **La fase F aplica, además del Anexo F, el diff de abajo sobre `tests/test_services.py`.**
   `test_be38_schema_keeps_rejecting_a_third_decimal` pasa a comprobar los dos DTO: `ServiceCreate` (por `ServiceBase`)
   y `ServiceUpdate`. No toca `app/`. Va en el mismo commit de la fase F, con el mensaje que dicta el plan más una
   viñeta al final de la lista: `  - tests/test_services.py: the third-decimal guard also covers ServiceCreate.`
2. **Motivo.** La regla "un tercer decimal es un 422, nunca se redondea" vive en los dos DTO desde la fase E, y el test
   solo validaba `ServiceUpdate`. El auditor de E lo midió en copias `git archive 1d9752e`: M13base (el
   `format_base_price` de `ServiceBase` con `mode="before"`) y M13dpbase (`ServiceBase.base_price` sin
   `decimal_places=2`) → `796 passed` los dos (viven): `POST /servicios/` redondearía en silencio con la suite en verde.
3. **Medido por la sesión Mentor** (contenedor propio: pydantic 2.12.5, pytest 9.1.1; `app/schemas/service.py` y
   `partial_update.py` de `d6f880f`, con un `ServiceCategory` de sustitución; solo este test): sin mutar → `1 passed`;
   M13base → `1 failed` (`DID NOT RAISE ValidationError`); M13dpbase → `1 failed` (ídem); M13 y M13dp sobre
   `ServiceUpdate` → `1 failed` cada uno, como antes. El archivo resultante: `ruff format --check` y `ruff check`
   limpios a 100 columnas (línea más larga, 95); `git diff --numstat` del diff: `17 5`. **No medido:** la suite
   completa ni `mypy` con la configuración del repo; los confirma la compuerta del ejecutor de F.
4. **Cifras.** Es la misma función, sin parametrizar: los conteos del plan no cambian (F y G `797 passed` · 98,69 %;
   comando 14 con 12 funciones y `36 passed`; RED de F `2 failed, 795 passed`, porque este test ya pasa antes y
   después). Cambia el `numstat` de `tests/test_services.py` en la fase F: `46 2` → `63 7`; el total de F, `+53 −5` →
   `+70 −10`. El auditor de F compara el diff contra el Anexo F más este.
5. **Mutantes añadidos al criterio de F** (en copias, E1): M13base y M13dpbase mueren, con este test.
6. `progress.json` no se toca: la descripción de la fase F y sus conteos siguen valiendo.
7. **Orden de aplicación, medido con `patch --dry-run` sobre una copia de `d6f880f` fuera del repo.** Este diff está
   escrito contra `d6f880f` y aplica limpio (`checking file tests/test_services.py`, sin rechazos); se aplica **antes**
   que el Anexo F, porque su segundo hunk termina en el final del archivo. Del Anexo F, que está escrito contra la
   opción (a), los hunks de `app/` y los dos primeros de `tests/test_services.py` aplican sobre (b) con 2 líneas de
   desplazamiento; **el tercero (el bloque `# === BE-61` con `test_be61_create_audits_every_promoted_url_in_order`) no
   aplica mecánicamente** (`Hunk #3 FAILED`): espera que el archivo termine en
   `assert stored.base_price == Decimal(answered)` (`:1133`), y con (b) siguen dos tests de precio. Ese bloque va, tal
   cual, **al final del archivo**, como sección nueva después de `test_be38_schema_keeps_rejecting_a_third_decimal`.
   Dónde quede no cambia ningún conteo ni el `numstat`.

```diff
diff --git a/tests/test_services.py b/tests/test_services.py
--- a/tests/test_services.py
+++ b/tests/test_services.py
@@ -26,7 +26,7 @@ from app.main import app
 from app.models.audit import AuditAction, AuditLog
 from app.models.service import ServiceCategory, ServiceImage, TouristService
 from app.models.user import UserRole
-from app.schemas.service import ServiceUpdate
+from app.schemas.service import ServiceCreate, ServiceUpdate
 
 # ==========================================
 # TEST FIXTURES (Context Setup)
@@ -1160,8 +1160,20 @@ async def test_be38_update_answers_the_price_with_two_decimals(
 
 
 def test_be38_schema_keeps_rejecting_a_third_decimal() -> None:
-    """Unhappy path: two decimals are written, never rounded; a third one is still a 422."""
-    with pytest.raises(ValidationError) as exc_info:
-        ServiceUpdate.model_validate({"base_price": "50000.555"})
+    """Unhappy path: two decimals are written, never rounded; a third one is still a 422.
 
-    assert [error["loc"] for error in exc_info.value.errors()] == [("base_price",)]
+    Checked on both DTOs: ServiceCreate, through ServiceBase, and ServiceUpdate.
+    """
+    create_payload = {
+        "name": "Caminata por el sendero ecologico",
+        "base_price": "50000.555",
+        "max_capacity": "10",
+    }
+    for schema, payload in (
+        (ServiceCreate, create_payload),
+        (ServiceUpdate, {"base_price": "50000.555"}),
+    ):
+        with pytest.raises(ValidationError) as exc_info:
+            schema.model_validate(payload)
+
+        assert [error["loc"] for error in exc_info.value.errors()] == [("base_price",)], schema
```

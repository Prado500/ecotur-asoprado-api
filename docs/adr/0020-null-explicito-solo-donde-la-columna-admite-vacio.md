# ADR-0020 — En un DTO de actualización, `null` explícito solo donde la columna admite vacío

- **Estado:** aceptado (David, 17 nov 2026, al aprobar el plan de BE-37)
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

# ADR-0021 — La auditoría registra solo lo que cambió, con su valor anterior y el nuevo

- **Estado:** aceptado (David, 18 nov 2026, al aprobar el plan de BE-38)
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
8. **El precio se escribe con los dos decimales de su columna al entrar** (`ServiceCreate` y
   `ServiceUpdate`): las respuestas de `POST`, `PUT` y `GET`, la fila `CREATE` y `old`/`new` lo
   muestran igual (`"60000.00"`). Un tercer decimal sigue siendo 422: se escribe la escala, no se
   redondea.

## Consecuencias

- Cambia la forma de `changes` en las filas `UPDATE` de `GET /auditoria/`, y la tabla mezcla dos
  formatos (punto 7). David comprueba el panel del cliente Flutter antes de mezclar.
- `POST /servicios/` y `PUT /servicios/{id}` responden el precio con dos decimales (`"50000.00"`),
  como `GET`.
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
6. **`populate_existing` en `ServiceRepository.create_service`.** Descartada al aprobar el plan
   (opción a): iguala el alta, pero `PUT` y `new` conservan la grafía enviada (`"60000"`).

## Evidencia

- Verificación (17 nov): sondas U1–U13 y P1–P14; re-verificación V1–V6 y C1–C4, y barrido de los
  once puntos que auditan.
- Plan (17 y 18 nov): RED y GREEN de cada fase, compuerta completa y mutantes, medidos en copia del
  repositorio; el orden de las imágenes no cambia el esquema (comparación de metadatos medida).
  Detalle: `docs/deuda/BE-38/plan.md`.

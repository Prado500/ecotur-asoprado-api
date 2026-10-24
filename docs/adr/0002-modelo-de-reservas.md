# ADR-0002 — Modelo de reservas del MVP: un paquete, una fecha, una reserva

- **Estado:** propuesto (pasa a *aceptado* con el OK de David; validado verbalmente con la gerencia de ASOPRADO el 23 oct 2026)
- **Ubicación en el repo:** `docs/adr/0002-modelo-de-reservas.md`

## Decisión (resumen)

Una reserva es **un paquete en una fecha**, hecha por un usuario, con un estado y un precio
congelado. **Cada paquete se puede reservar como máximo una vez por fecha**; paquetes distintos
son independientes entre sí. El número de personas no es un dato de la reserva: es una
característica del paquete (individual, pareja, grupo de N). La regla "una por fecha" se
garantiza en la base de datos con un índice único parcial, no solo en el código.

## Contexto

- ASOPRADO no posee lanchas, hoteles ni restaurantes: cada paquete depende de terceros cuya
  disponibilidad real se desconoce. Por eso la gerencia fijó la capacidad más conservadora
  posible: **una prestación por paquete por día**. Es una decisión inicial de negocio, no una
  limitación técnica, y así se documenta.
- Los paquetes concretos aún no están definidos; sí sus "moldes":
  - **Ventana de disponibilidad:** *siempre reservable* (cualquier día del año) o *solo en
    franjas de fechas* (p. ej. del 7 al 16 de junio y del 1 al 5 de julio).
  - **Tamaño del grupo:** 1 persona, 2 personas (pareja) o N personas (grupo fijo).
  - **Precio:** el precio base sube en temporada alta (fin de año, puentes, fiestas).
- Reservar hoy para mañana debe ser posible (antelación mínima de 1 día).

## Modelo

### `Package` (existente; se amplía)
| Campo | Tipo | Significado |
|---|---|---|
| `party_size` | int ≥ 1 | Personas que cubre el paquete (1, 2 o N). *Hoy existe `max_capacity`; se renombra, porque "capacidad máxima" sugiere cupo y ya no lo es.* |
| `availability_mode` | enum `always` / `date_ranges` | Siempre reservable o solo en franjas. |
| `min_lead_days` | int, default 1 | Antelación mínima. |
| `base_price` | existente | Precio **del paquete completo** (no por persona). |

### `PackageAvailabilityWindow` (nueva, 1:N con `Package`)
`package_id`, `start_date`, `end_date`. Solo se consulta cuando `availability_mode = date_ranges`.
Varias filas = varias franjas (junio y julio).

### `Reservation` (nueva)
| Campo | Tipo | Nota |
|---|---|---|
| `id`, `package_id`, `user_id` | FK | |
| `reservation_date` | date | La fecha de la prestación. |
| `status` | enum `pending` / `confirmed` / `cancelled` / `expired` | Máquina de estados abajo. |
| `total_amount` | numeric | **Instantánea** del precio al reservar. El precio del paquete puede cambiar después; el de la reserva no. |
| `party_size_snapshot` | int | Instantánea del tamaño del grupo al reservar, por la misma razón. |
| `expires_at` | datetime | Solo para `pending`: ventana para pagar (30 min, decisión inicial). |
| `created_at`, `updated_at` | datetime | |

### Invariante en la base de datos (la parte importante)
```sql
CREATE UNIQUE INDEX uq_reservation_active_package_date
ON reservations (package_id, reservation_date)
WHERE status IN ('pending', 'confirmed');
```
Dos peticiones simultáneas pueden pasar la validación en código y ambas intentar insertar; solo
una gana. El índice parcial convierte la regla de negocio en una garantía que no depende de que
nadie se acuerde de comprobarla. La aplicación captura `IntegrityError` y lo traduce a la
excepción de dominio `DateAlreadyReserved` → HTTP 409.

### Disponibilidad de un paquete en una fecha `D`
Disponible si y solo si:
1. `D ≥ hoy + min_lead_days`;
2. `availability_mode = always`, o `D` cae dentro de alguna ventana del paquete;
3. el paquete está activo y no eliminado (guardia BE-13);
4. no existe reserva `pending` vigente ni `confirmed` para `(package_id, D)`.

Endpoint para el selector de fecha del cliente: `GET /packages/{id}/availability?from=&to=`
devuelve las fechas disponibles del rango (el calendario deshabilita el resto).

### Máquina de estados
`pending` —pago aprobado→ `confirmed` · `pending` —vence `expires_at`→ `expired` ·
`pending` / `confirmed` —usuario o admin→ `cancelled`.
Expiración **perezosa**: no hay scheduler. Antes de crear una reserva y al calcular
disponibilidad, en la misma transacción: `UPDATE … SET status='expired' WHERE status='pending'
AND expires_at < now()` para ese paquete y fecha; luego se inserta. Así una `pending` vencida
nunca bloquea el índice único.

## Consecuencias

- **Positivas:** modelo pequeño (2 tablas nuevas, 3 columnas en `Package`), refleja literalmente
  lo acordado con la gerencia, y la regla crítica vive en la BD. El precio congelado hace que la
  tarifa de temporada sea trabajo futuro sin tocar reservas.
- **Negativas / aceptadas:** capacidad fija en 1 por fecha; no hay cupo parcial ni varias
  prestaciones del mismo paquete el mismo día. Renombrar `max_capacity` → `party_size` toca
  migración, schemas y frontend (~30 min).
- **Camino de evolución documentado:** cuando ASOPRADO conozca su "ingrediente limitante"
  (cuántas lanchas, cuántos mototaxistas fiables), se añade `max_reservations_per_date` al
  paquete, se reemplaza el índice único por una comprobación bajo bloqueo (`SELECT … FOR UPDATE`
  sobre el paquete) y nada más cambia. Eso se escribe en el capítulo de trabajo futuro.

## Decisiones iniciales asumidas (para validar con la gerencia cuando convenga, no bloquean)
1. Precio por paquete completo, no por persona.
2. Antelación mínima: 1 día.
3. Ventana de pago de una reserva pendiente: 30 minutos.
4. Tarifa de temporada alta: fuera del MVP (BE-22); el precio congelado la hace trivial después.

## Fuera de alcance de este ADR
Pasarela de pago (ADR de pagos, pendiente), notificaciones, agendamiento por horas, cupos parciales.

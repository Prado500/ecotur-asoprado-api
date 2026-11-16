# ADR-0017 — Ningún superadmin se borra ni se desactiva a sí mismo: el número de superadmins no baja desde la aplicación

- **Estado:** aceptado (David, 16 nov 2026, al aprobar el plan de BE-35). **Superado parcialmente por ADR-0019**
  (16 nov 2026): el alcance "superadmin" de las dos guardas de la decisión 1 y la consecuencia "Turistas y admins no
  cambian"; el resto sigue vigente.
- **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 10:31)
- **Ubicación en el repo:** `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md`
- **Origen:** backlog BE-35; `docs/deuda/BE-35/verificacion.md` (veredicto y adenda); `docs/deuda/BE-35/plan.md`. El plan
  de BE-02 (`docs/deuda/BE-02/plan.md:72`) anunció que esta regla requeriría ADR. Relación: ADR-0012 (una regla que
  depende del dato va en la política), ADR-0003 (`AuthorizationError` → 403), ADR-0015 (primer superadmin y
  `count_active_superadmins`), BE-55 (baja de un superadmin sin SQL directo).

## Contexto

Un superadmin podía sacarse a sí mismo de la plataforma por dos vías de autoservicio: `DELETE /usuarios/{su cédula}` y
`PATCH /usuarios/{su cédula}` con `{"is_active": false}`. Las dos daban 200 y la petición siguiente, 401
(`get_current_user` rechaza a quien está borrado o inactivo). Si era el único, la plataforma se quedaba sin superadmin.
Medido el 16 nov (sonda de la verificación): un superadmin no puede desactivar ni borrar a otro (403 y 403), y el cambio
del propio rol lo cerró BE-02. Esas dos vías eran las únicas por las que bajaba el número de superadmins activos.

La fila del backlog proponía "siempre queda al menos un superadmin activo": contar antes de borrar o desactivar y
responder 409 al último.

## Decisión

1. **Ningún superadmin borra ni desactiva su propia cuenta, haya uno o varios.** `UserAccessPolicy.assert_can_delete`
   rechaza que un superadmin borre su cuenta; `assert_can_update` rechaza que ponga su `is_active` a `false`. "Su
   cuenta" es la de su misma cédula.
2. **La guarda de `is_active` lee el valor, no la clave:** `{"is_active": true}` sobre uno mismo sigue pasando.
3. **403 con `AuthorizationError`,** el molde de "nadie cambia su propio rol" (BE-02). Sin excepción nueva ni entrada
   nueva en `_DOMAIN_ERROR_STATUS`. Orden: 404 → 403. El rechazo no muta estado ni escribe auditoría.
4. **Sin conteo y sin bloqueo.** La política sigue pura y síncrona, con la misma firma. `count_active_superadmins`
   sigue siendo solo del primer superadmin (ADR-0015).

Con el punto 1 y la regla entre pares, el número de superadmins no baja nunca desde la aplicación: no hay "último" que
detectar, y dos peticiones simultáneas reciben el mismo rechazo.

## Consecuencias

- **Coste aceptado (David, 16 nov):** una cuenta de superadmin no se puede retirar desde la aplicación. Antes solo
  podía hacerlo su dueño; ahora, nadie. Si cambia el gerente o una cuenta se ve comprometida, la baja es SQL directo
  del operador, que no escribe auditoría, hasta que exista el mecanismo de BE-55.
- Cambio de contrato solo para un superadmin sobre sí mismo: `DELETE /usuarios/{cedula}` y `PATCH /usuarios/{cedula}`
  con `is_active` a `false` pasan de 200 a 403. Turistas y admins no cambian.
- `{"is_active": null}` no lo trata esta regla (BE-37).
- BE-36 sigue abierta: el caso "A se desactiva y B no puede reactivarlo" deja de poder producirse, pero la
  recuperación entre pares que deja la cuenta inactiva sigue ahí.
- Si BE-55 deja que un superadmin dé de baja a otro, vuelve el problema de contar bajo concurrencia (alternativa 2).

## Alternativas consideradas

1. **La regla de la fila, contando con `SELECT count(*)`.** Rechazada: con dos superadmins que se retiran a la vez,
   cada petición cuenta 2 y las dos pasan; quedan 0 (sonda de la adenda, abajo). Ningún `CHECK` puede contar filas.
2. **La regla de la fila, contando bajo bloqueo (`SELECT id … FOR UPDATE` sobre los superadmins activos).** Cierra la
   carrera en PostgreSQL. Descartada porque la regla del punto 1 no necesita contar; además, la política dejaría de ser
   pura (el conteo vive en `UserRepository`) y la suite no lo vería: SQLite ignora `FOR UPDATE` (BE-31). Queda como dato
   para BE-55.
3. **409 con una `DomainError` nueva.** Descartada: con la regla del punto 1 el rechazo no depende del estado de la
   plataforma; es una prohibición sobre la propia cuenta, como el rol propio de BE-02, que ya es 403.
4. **No hacer nada.** Rechazada: el único superadmin deja la plataforma sin superadmin con una petición.

## Evidencia

- Verificación (16 nov, pila real de la suite): único superadmin, `PATCH` propio `{"is_active": false}` → 200 y 401
  después; `DELETE` propio → 200 y 401 después; `count_active_superadmins()` = 0 en ambos. Entre dos superadmins: 403 y
  403.
- Sonda de la sesión Mentor (16 nov; PostgreSQL 16.15 propio, réplica mínima de `users`, psycopg2, `READ COMMITTED`;
  dos superadmins A y B que se borran a la vez, cada uno en su transacción):
  `plain count [('A', 'counted 2 -> deleted'), ('B', 'counted 2 -> deleted')] | active superadmins left: 0` y
  `FOR UPDATE [('A', 'counted 2 -> deleted'), ('B', 'counted 1 -> rejected')] | active superadmins left: 1`. Límites:
  SQL directo, no el repositorio ni asyncpg; no es una base de Azure.
- Tests y mutantes de la regla: `docs/deuda/BE-35/plan.md`, fase B.

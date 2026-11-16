# ADR-0018 — Un superadmin puede reactivar a otro superadmin, y nada más

- **Estado:** aceptado (David, 16 nov 2026, al aprobar el plan de BE-36)
- **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 12:22)
- **Ubicación en el repo:** `docs/adr/0018-un-superadmin-reactiva-a-otro.md`
- **Origen:** backlog BE-36; `docs/deuda/BE-36/verificacion.md` (veredicto y adenda); `docs/deuda/BE-36/plan.md`.
  Relación: ADR-0017 (lo complementa, no lo supersede: ver Consecuencias), ADR-0012 (una regla que depende del dato
  va en la política), ADR-0003 (`AuthorizationError` → 403), ADR-0009 (no es un addendum de ADR-0017: abre un caso
  que ese ADR no trataba), BE-55 (baja de un superadmin sin SQL directo).

## Contexto

Entre pares nadie modifica a nadie: `UserAccessPolicy.assert_can_update` responde 403 cuando el objetivo no tiene un
rango estrictamente menor que el del actor, sea cual sea el cambio. Nadie está por encima de un superadmin, así que
un superadmin inactivo no tiene a nadie que lo active. Dos puertas llevan a ese estado, medidas el 16 nov con la pila
real de la suite:

1. **Recuperación.** `PATCH /usuarios/{cédula}/recuperar` deja la cuenta de cualquier rol con `is_active = false`, a la
   espera de que alguien la active; entre superadmins esa activación da 403, y el recuperado recibe 403 al entrar.
   Desde ADR-0017 un superadmin solo llega a la papelera por SQL directo o si ya estaba en ella.
2. **Provisión.** `POST /usuarios/admin` con `role = superadmin` y sin `is_active` crea la cuenta inactiva (el schema
   lo pone a `false` por defecto); el `PATCH {"is_active": true}` de su creador da 403 y el nuevo no puede entrar.
   Esta puerta sigue abierta desde la aplicación.

## Decisión

1. **Excepción única a la regla entre pares:** un superadmin puede actualizar a otro superadmin cuando el conjunto de
   cambios es exactamente `{"is_active": true}`. Cualquier otra clave, sola o junto a `is_active`, y cualquier otro
   valor (`false`, `null`) siguen dando 403. Entre admins no se abre nada.
2. **La excepción lee la clave y el valor.** Si leyera solo la clave, dejaría que un superadmin desactivase a otro,
   que es lo que ADR-0017 cierra.
3. **El objetivo no puede estar en la papelera.** Reactivar no sustituye a la recuperación ni a su fila de auditoría:
   un superadmin borrado se recupera primero y se reactiva después.
4. **Nada más cambia:** la recuperación sigue dejando inactiva la cuenta de cualquier rol, el valor por defecto de
   `is_active` en la provisión sigue en `false`, la respuesta sigue siendo 403 con `AuthorizationError` y la política
   sigue pura, síncrona y con la misma firma.

## Consecuencias

- **Coste aceptado (David, 16 nov):** si un operador da de baja a un superadmin por SQL poniendo solo
  `is_active = false` (la baja que deja ADR-0017), otro superadmin puede reactivarlo desde la aplicación. Una baja que
  deba ser definitiva no puede consistir solo en `is_active = false`: dato para BE-55.
- **La premisa de ADR-0017 sigue en pie.** "Entre pares nadie modifica a nadie" pasa a ser "entre pares nadie
  modifica a nadie, salvo que un superadmin reactiva a otro". Para desactivar, borrar y degradar sigue siendo cierta:
  el número de superadmins activos no baja desde la aplicación; la excepción solo puede subirlo.
- Cambio de contrato: `PATCH /usuarios/{cédula}` con `{"is_active": true}` de un superadmin sobre otro que no está en
  la papelera pasa de 403 a 200 y escribe una fila de auditoría `UPDATE`. Ninguna otra petición cambia.
- Reactivar a un par que ya está activo también da 200 y escribe la fila aunque nada cambie (BE-38).
- La viñeta "Superadmins" de AGENTS §3 recoge la excepción; la edita David.

## Alternativas consideradas

1. **Que la recuperación reactive cuando actor y objetivo son superadmins.** Descartada: no cubre la puerta de la
   provisión, y haría de la recuperación una reactivación inmediata solo para un rol.
2. **Permitir la clave `is_active` entre pares, con cualquier valor.** Rechazada: dejaría a un superadmin desactivar a
   otro, que ADR-0017 cierra; exigiría superseder ese ADR.
3. **Poner a `true` el valor por defecto de `is_active` en la provisión.** Fuera de este ADR por decisión de David:
   solo cierra la segunda puerta y cambia lo que hoy recibe quien provisiona a un admin.
4. **No hacer nada.** Rechazada: un superadmin provisionado sin `is_active` no puede entrar nunca, y nadie lo arregla
   sin SQL.

## Evidencia

- Verificación (16 nov, pila real de la suite): recuperar a un par → 200 con `is_active` false; `PATCH
  {"is_active": true}` del par → 403; login del recuperado → 403. Superadmin → admin y admin → turista, mismo
  mecanismo: 200 · 200 · 200.
- Sonda del planificador (16 nov, pila real de la suite, fuera de `tests/`): el superadmin A crea al superadmin B sin
  `is_active` → 201, B inactivo; login de B → 403; `PATCH {"is_active": true}` de A sobre B → 403; login de B → 403.
  Un admin provisionado igual: 201 · 200 · 200. Superadmin aún en la papelera, `PATCH {"is_active": true}` → 403.
- Tests y mutantes de la regla: `docs/deuda/BE-36/plan.md`, fase B.

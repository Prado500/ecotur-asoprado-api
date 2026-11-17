# ADR-0019 — Ninguna cuenta administrativa se borra ni se desactiva a sí misma: su baja la decide un superadmin

- **Estado:** aceptado (David, 16 nov 2026, al aprobar el plan de BE-58)
- **Propuesta:** Claude, `plan-redactor` (16 nov 2026), sobre la adenda de David a la verificación (16 nov, 18:02)
- **Ubicación en el repo:** `docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md`
- **Supersede parcialmente:** ADR-0017, en dos puntos: el alcance "superadmin" de las dos guardas de su decisión 1 y
  su consecuencia "Turistas y admins no cambian". El resto de ADR-0017 sigue vigente (el número de superadmins no baja
  desde la aplicación; la baja de un superadmin es SQL directo hasta BE-55; las alternativas descartadas). ADR-0018 no
  cambia.
- **Origen:** backlog BE-58; `docs/deuda/BE-58/verificacion.md` (veredicto y adenda); `docs/deuda/BE-58/plan.md`.
  Relación: ADR-0009 (un addendum no puede ampliar el alcance de una decisión: esto es un ADR nuevo), ADR-0006 respecto
  de ADR-0003 (precedente de supersesión parcial), ADR-0012 (una regla que depende del dato va en la política),
  ADR-0003 (`AuthorizationError` → 403).

## Contexto

ADR-0017 cerró dos vías de autoservicio solo para superadmins, `DELETE /usuarios/{su cédula}` y
`PATCH /usuarios/{su cédula}` con `{"is_active": false}`, y dejó escrito "Turistas y admins no cambian". Un admin seguía
pudiendo usarlas: medido el 16 nov con la pila real de la suite, las dos dan 200, escriben una fila de auditoría con el
propio admin como autor y la petición siguiente recibe 401. David lo vio también en el cliente: un admin se desactiva
desde su tarjeta del kanban y su sesión queda muerta. La cuenta no se pierde: un superadmin la reactiva o la recupera
desde la aplicación (200 · 200 · 200); otro admin no puede (403).

## Decisión

1. **Ninguna cuenta administrativa borra ni desactiva su propia cuenta.** Cuenta administrativa es la de todo rol que no
   sea turista. Las dos guardas de ADR-0017 (`UserAccessPolicy.assert_can_delete` y `assert_can_update`) pasan de "el
   actor es superadmin" a "el actor no es turista". Una sola guarda por vía: no se añade otra. "Su cuenta" sigue siendo
   la de su misma cédula.
2. **La condición se escribe sobre "no es turista", no sobre "es admin o superadmin".** Hoy dicen lo mismo; un rol que
   se añada mañana queda bloqueado hasta que alguien decida abrirlo.
3. **Los turistas no cambian:** conservan el borrado de su propia cuenta y siguen sin poder enviar `is_active`.
4. **Lo demás de ADR-0017 se mantiene:** la guarda de `is_active` lee el valor (`false` → 403, `true` pasa, `null`
   es BE-37); 403 con `AuthorizationError`, sin excepción nueva; el rechazo no muta estado ni escribe auditoría; la
   política sigue pura, síncrona y con la misma firma.

La razón es de gobierno: **solo un superadmin decide cuándo se da de baja una cuenta administrativa** (David, 16 nov).
Un funcionario no debe poder interrumpir la operación retirando la cuenta que el gerente tenía prevista para su
reemplazo. No la sostiene que la cuenta "quede varada hasta que alguien entre a la base": la verificación midió que un
superadmin rescata a un admin desde la aplicación.

## Consecuencias

- Cambio de contrato solo para un admin sobre sí mismo: `DELETE /usuarios/{cédula}` y `PATCH /usuarios/{cédula}` con
  `is_active` a `false` pasan de 200 a 403, y un `PATCH` que mezcla `is_active: false` con otros campos se rechaza
  entero. `{"is_active": true}` sobre uno mismo sigue dando 200. Turistas y superadmins no cambian de código.
- La baja de un admin la da un superadmin desde la aplicación (borrar o desactivar a un rango inferior, sin cambio). La
  de un superadmin sigue como la deja ADR-0017: SQL directo hasta BE-55.
- Los dos avisos dejan de nombrar al superadministrador como sujeto y piden la baja a un superadministrador. Un
  superadmin recibe el mismo texto, aunque ningún par puede darle de baja desde la aplicación (ADR-0017; BE-55).
- La viñeta "Superadmins" de AGENTS §3 recoge la ampliación; la edita David.
- Cambiar el propio correo también deja muerto el token en uso (el token lleva el correo), pero no es una baja: queda
  fuera de esta regla (FE-01).

## Alternativas consideradas

1. **Una guarda nueva solo para admins, junto a las de ADR-0017.** Descartada: dos guardas por vía con el mismo efecto,
   y un rol nuevo obligaría a acordarse de una tercera.
2. **Escribir la condición sobre "admin o superadmin".** Descartada: equivale hoy, pero un rol nuevo quedaría abierto
   por omisión.
3. **Un addendum a ADR-0017.** Descartado: amplía el alcance de su decisión e invierte una consecuencia escrita, que
   ADR-0009 (punto 3) reserva a un ADR nuevo.
4. **No hacer nada, porque un superadmin rescata la cuenta.** Rechazada: la cuestión no es si la cuenta se recupera,
   sino quién decide su baja.

## Evidencia

- Verificación (16 nov, pila real de la suite): admin, `PATCH` propio `{"is_active": false}` → 200, el mismo token →
  401, login → 403; `DELETE` propio → 200, el mismo token → 401, login → 401. Otro admin no lo rescata (403); un
  superadmin sí (200 · 200 · 200). Con la regla inyectada: 403 sin mutación ni auditoría, y el token sigue sirviendo.
- Tests y mutantes de la regla: `docs/deuda/BE-58/plan.md`, fase B.

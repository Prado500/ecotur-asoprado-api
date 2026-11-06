# ADR-0012 — Frontera de autorización: el rol se decide en el guard, el dato en la política, y toda ruta protegida tiene un test de rechazo

- **Estado:** Aceptado (borrador del Mentor, 6 nov 2026, a partir de `docs/deuda/A2/verificacion.md`)
- **Propuesta:** sesión Mentor (6 nov 2026) · **Aprobada:** David (6 nov 2026)
- **Ubicación en el repo:** `docs/adr/0012-frontera-de-autorizacion-guard-y-politica.md`
- **Origen:** backlog A2 ("tres estrategias de autorización incompatibles", auditoría del 21 sep); `docs/deuda/A2/verificacion.md`
  (parcial, 6 nov); AGENTS §3 ("Autorización centralizada") y §7 (decisión no trivial → ADR). Relación: ADR-0003 (errores de
  dominio), BE-02 (rol propio por clave), `B-GHOST-ADMIN` (BE-34..BE-38).

## Contexto

AGENTS §3 ya dice que el rol se comprueba con el guard IoC (`get_current_admin_user`, `app/api/dependencies.py`) y que
`UserAccessPolicy` decide las reglas que dependen del dato (jerarquía, propiedad). Nunca se escribió como decisión, y la
verificación de A2 (6 nov) midió dónde no se cumple y, sobre todo, que **nadie lo vigila**:

- De las tres estrategias de septiembre quedan dos desviaciones: `GET /auditoria/` comprueba el rol dos veces (guard del
  router, `audit.py:8`, y `assert_is_admin_plus` en `audit_service.py:65`); `POST /usuarios/admin` aplica una regla de
  solo rol ("solo un superadmin crea administradores") dentro de la política (`user_access_policy.py:98-113`), sin guard
  de superadmin. Comentarios de `user.py:24-33` y `audit.py:28-32` se contradicen sobre la frontera; la identidad bajo
  guard admin se inyecta de tres formas distintas.
- **Ningún test HTTP depende del guard de rol.** Con el guard sin comprobar el rol, o sin guard en `/servicios`, o
  `/usuarios` admin bajo `get_current_user`, la suite queda en verde (mutantes M1–M3, M6, M7: `259 passed`); un turista
  recibiría 200 en `GET /usuarios/`. `tests/test_services.py` no tiene ningún 403. Solo el re-chequeo duplicado de
  auditoría (M5) y la provisión (M8) tienen test. Inventario: 22 rutas; 5 sin guard (públicas), 3 con guard user, 14 con
  guard admin, de las que 2 no cumplen la frontera.

## Decisión

1. **El rol se decide en el guard HTTP.** Toda regla que dependa solo del rol del actor (admin+, superadmin) se aplica
   con una dependencia de FastAPI en el router o en la ruta (`get_current_admin_user`; un guard de superadmin cuando haga
   falta). La política no vuelve a comprobar el rol.
2. **El dato se decide en la política.** `UserAccessPolicy` aplica las reglas que necesitan el objeto: jerarquía entre
   actor y objetivo, propiedad, estado de la cuenta, campos que un actor no puede tocar (BE-02). Recibe actores que ya
   pasaron el guard.
3. **Ninguna regla se comprueba dos veces.** Si el guard la decidió, el servicio no la repite; si la política la decide,
   no hay guard que la duplique. Una comprobación duplicada es deuda, no defensa en profundidad: tapa los tests del guard
   (es lo que pasó con `/auditoria/`).
4. **Toda ruta protegida tiene un test HTTP de rechazo** por la vía que la protege: sin token → 401, token de un rol
   inferior → 403, además del camino feliz. La prueba de que el test vigila es el mutante (quitar el guard o su
   comprobación de rol → el test cae). Es la condición de AGENTS §5 ("dos de fallo por camino feliz") aplicada a la
   autorización.
5. **La identidad bajo guard se inyecta de una sola forma** (`AdminDep` / `UserDep` de `user.py:20-21`), para que la
   ruta diga a la vista con qué derecho actúa.

## Consecuencias

- Trabajo con fila en el backlog: **BE-39** (tests de rechazo en las 14 rutas admin y las 3 de usuario, en RED con los
  mutantes M1–M7 de la verificación) y **BE-40** (aplicar la frontera: quitar el re-chequeo de `audit_service` y su
  inyección de la política; guard de superadmin para `POST /usuarios/admin`; una sola forma de inyectar identidad;
  comentarios). Bloque `B-GUARD-TESTS` `(PLAN §2b)`.
- Cambio de contrato declarado en BE-40: con el guard de superadmin, un admin que envía un cuerpo inválido a
  `POST /usuarios/admin` pasa de 422 a 403 (el guard corre antes de validar el cuerpo). Se confirma con el cliente Flutter
  (solo un superadmin ve esa pantalla, evidencia del 5 nov).
- `B-GHOST-ADMIN` (BE-34..BE-38) no cambia: sus reglas dependen del dato (último superadmin activo, pares) y siguen en
  la política.
- Riesgo aceptado: hasta que BE-39 esté mezclada, el guard sigue sin red; mientras tanto ningún PR toca
  `dependencies.py:119-136` ni los `APIRouter(dependencies=…)` sin añadir el test de rechazo de esa ruta en el mismo PR.

## Alternativas consideradas

1. **Defensa en profundidad: rol en el guard y otra vez en el servicio.** Rechazada: duplica la regla en dos capas que
   pueden divergir y oculta en los tests la ausencia del guard (M7 sobrevive porque el servicio de auditoría lo tapa).
2. **Todo en la política, sin guards.** Rechazada: cada servicio tendría que recibir y comprobar el actor para reglas que
   no dependen del dato; el router dejaría de declarar a la vista quién puede entrar; contradice AGENTS §3.
3. **Dejar las dos desviaciones como están y solo añadir tests.** Rechazada como decisión, aceptada como orden: BE-39
   (tests) va antes que BE-40 (refactor), porque los tests de rechazo son los que permiten mover las reglas sin romperlas.

## Evidencia

`docs/deuda/A2/verificacion.md` (6 nov 2026): inventario de 22 rutas, mapa de ficheros, mutantes M1–M8 sobre copia
desechable (`259 passed` en M1–M4, M6 y M7; `1 failed` en M5; `3 failed` en M8), línea base `86256b2`.

# ADR-0022 — Una marca de correo verificado decide el enlace de verificación

- **Estado:** aceptado (David, 19 nov 2026, al aprobar el plan de BE-50)
- **Propuesta:** Claude, `plan-redactor` (19 nov 2026), sobre la adenda de David a la verificación (19 nov, 10:34 a
  11:24)
- **Ubicación en el repo:** `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`
- **Origen:** backlog BE-50; `docs/deuda/BE-50/verificacion.md` (veredicto, sondas P1 a P5b y adenda);
  `docs/deuda/BE-50/plan.md`; `docs/aprendizaje/fichas/BE-50.md` (las tres opciones comparadas). Relación: ADR-0021
  (su punto 5 no cambia), ADR-0010 (estilo de la columna), ADR-0002 (el dato vive en la base), ADR-0018 (un admin
  sigue pudiendo activar a un turista).

## Contexto

Una cuenta tenía dos datos de estado, `is_active` y `deleted_at`. `is_active = false` significaba tres cosas: pendiente
de verificar el correo, desactivada por un administrador y recuperada de la papelera a la espera de aprobación. El
enlace de verificación (un JWT con `sub`, `scope` y `exp`, 15 minutos, sin identificador y sin guardar) activaba
cualquiera de las tres. Medido el 19 nov: el segundo clic respondía otra vez 200 "verificada" (P1), el enlace
reactivaba una cuenta que un administrador había desactivado (P2) y activaba una recuperada sin aprobación (P3). Siete
docstrings llamaban "single-use" al token.

## Decisión

1. **Columna `users.email_verified_at`** (`TIMESTAMP WITH TIME ZONE`, admite vacío): vacía hasta que el enlace se usa
   con éxito y llena desde entonces. Solo la escribe `verify_email_account`; ningún acto de un administrador la llena
   ni la vacía, y ningún DTO de entrada o salida la lleva.
2. **Regla del enlace**, con el token válido: cuenta borrada → 404, sin cambios; marca vacía → se llena y, si la cuenta
   está inactiva, pasa a activa; 200 con "Cuenta verificada exitosamente. Ya puede iniciar sesión."; marca llena → no
   cambia nada, no deja fila de auditoría y responde 200 con "Su correo ya fue verificado.", que no promete el acceso
   porque la cuenta puede estar desactivada.
3. **El enlace es de un solo efecto por el estado de la cuenta, no por consumir el token.** El token sigue sin `jti`,
   no se guarda y caduca a los 15 minutos.
4. **El enlace completa el alta de quien nunca lo usó, pase lo que pase entre medias:** también una cuenta borrada y
   recuperada (excepción declarada a "una cuenta recuperada espera la aprobación de un administrador") y una que un
   administrador activó y desactivó a mano. Para frenar un registro pendiente, el administrador borra la cuenta y no la
   recupera.
5. **Después del enlace, `is_active` es solo del administrador.**
6. **Auditoría:** el punto 5 de ADR-0021 no cambia. La fila es un `UPDATE` de `is_active` con la cuenta como autora y
   existe solo cuando el enlace cambia `is_active`; la marca no se audita, y cuándo se verificó lo dice ella misma.
7. **La migración `e50a7c3d9b12` no inventa verificaciones:** la columna nace vacía en todas las filas, también en las
   activas, porque una cuenta activa pudo activarla un administrador. Las cuentas administrativas y el superadmin del
   bootstrap no reciben enlace: su marca queda vacía.

## Consecuencias

- El segundo clic deja de decir "verificada" y deja de escribir; un administrador que desactiva a un turista ya
  verificado no ve su decisión deshecha por el enlace.
- **Es una simplificación frente al modelo de dos hechos.** El enlace sigue escribiendo a la vez "correo verificado"
  (la marca) y "cuenta activa" (`is_active`), y el login solo mira `is_active`. El modelo de la industria los separa:
  el enlace solo anota la marca y entrar exige las dos cosas. Se eligió esta opción para no cambiar el registro ni lo
  que el cliente muestra como "por activar" dentro del MVP; el modelo separado es la fila BE-62.
- **Riesgo aceptado:** si un administrador desactiva la cuenta justo después de la verificación, el turista vio la
  pantalla de éxito y no puede entrar, y el login le pide verificar el correo (BE-56).
- Un administrador puede activar a quien nunca verificó; esa cuenta queda activa con la marca vacía (BE-63).
- Sin reenvío del enlace (BE-64), un turista cuyo enlace caducó depende de un administrador. Con la marca, varios
  enlaces vigentes a la vez no son un riesgo: el primero que se usa la llena y los demás no cambian nada.
- Los enlaces emitidos en los 15 minutos previos al despliegue encuentran la marca vacía y activan su cuenta aunque un
  administrador la haya desactivado en ese plazo.
- Dos clics simultáneos pueden escribir dos filas: no hay bloqueo de fila (A3).

## Alternativas consideradas

1. **Dos hechos separados** (el enlace solo anota la marca; el turista nace habilitado; entrar exige marca y
   `is_active`). Es el modelo de Devise. Rechazada para el MVP por coste: cambia el registro, el kanban del cliente y
   supersede el punto 5 de ADR-0021. Queda como BE-62.
2. **Un acto del administrador mata el enlace** (una marca de "registro pendiente" que apagan el clic y cualquier
   acción administrativa). Rechazada: la cuenta podría quedar activa sin que nadie haya probado que el correo existe, y
   cada escritor de `is_active` tendría que acordarse de apagarla.
3. **Token de un solo uso con `jti` guardado.** Rechazada: protege el token y no la cuenta, exige una tabla y su
   limpieza, y con reenvío (BE-64) un segundo token vigente volvería a reactivar.
4. **Rechazar el segundo clic con un error.** Rechazada por David: mostraría un error a quien pulsa dos veces sobre una
   cuenta ya verificada, sin forma de pedir otro enlace.
5. **Rellenar la marca de las cuentas activas en la migración.** Rechazada (decisión 7). La wiki de Devise lo
   recomienda al añadir `confirmed_at` porque allí la marca habilita el login; aquí no habilita nada, así que dejarla
   vacía no deja a nadie fuera.

## Evidencia

- Verificación (19 nov): sondas P1, P2 (V4 de BE-38), P3, P4 y P5b; siete docstrings "single-use".
- Plan: tests de cada caso y mutantes en copias del repositorio (`docs/deuda/BE-50/plan.md`).
- OWASP, Email Validation and Verification Cheat Sheet, "Email Ownership Verification": tokens de un solo uso y con
  plazo, y "Do not activate accounts before verification is completed". Esta decisión cumple el plazo y da un solo
  efecto, no invalida el token, y la activación manual por un administrador (BE-63) es la desviación declarada.
- OWASP, Forgot Password Cheat Sheet, "Introduction": "Single use and expire after an appropriate period" (trata de la
  recuperación de contraseña; aplica por analogía).
- Devise, wiki "How-To: Add :confirmable to Users" (`confirmed_at` en columna propia; la migración marca confirmadas
  las cuentas existentes) y "How-To: Customize user account status validation when logging in"
  (`active_for_authentication?` combina con `super &&` la condición base y la propia).
- Fuentes leídas el 19 nov en el texto fuente que sirve Context7, no en la página publicada.

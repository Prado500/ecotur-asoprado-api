# ADR-0023 — El enlace de verificación se puede pedir de nuevo: a un turista sin verificar, con un mínimo entre envíos y la misma respuesta siempre

- **Estado:** aceptado (David, 19 nov 2026, al aprobar el plan de BE-64)
- **Propuesta:** Claude, `plan-redactor` (19 nov 2026), sobre la adenda de David a la verificación (19 nov, 17:13 a
  17:44)
- **Ubicación en el repo:** `docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md`
- **Origen:** backlog BE-64; `docs/deuda/BE-64/verificacion.md` (veredicto, rincones 1 a 3 y adenda);
  `docs/deuda/BE-64/plan.md`. Relación: ADR-0022 (la regla del enlace no cambia; esta decisión responde a su
  consecuencia "sin reenvío"), ADR-0019 (las cuentas administrativas las decide un superadmin), ADR-0016 (correo en
  minúsculas), ADR-0013 (variable nueva), ADR-0012 (ruta pública en el inventario), ADR-0010 (estilo de la columna),
  ADR-0021 (qué se audita). BE-65 reutiliza su schema de salida.

## Contexto

El enlace de verificación vive 15 minutos y solo lo emitía el registro. Pasado ese plazo la API respondía que había
caducado y pedía "solicite uno nuevo", sin ruta para pedirlo; registrarse otra vez da 400 porque el correo y la cédula
ya existen, y la cuenta quedaba inactiva hasta que un administrador la activara a mano (BE-63). La marca
`email_verified_at` (ADR-0022) no basta para decidir a quién se le emite: está vacía en las cuentas administrativas, en
el superadmin del bootstrap y en todas las filas anteriores a su migración, y un enlace con la marca vacía activa la
cuenta. La aplicación no tiene limitador de peticiones ni guardaba cuándo salió un enlace.

## Decisión

1. **Ruta pública `POST /usuarios/reenviar-verificacion`**, cuerpo `{"email": …}` (`LowercaseEmail`), con
   `response_model=MessageResponse` (`app/schemas/message.py`: exactamente `success: bool` y `message: str`, sobre
   `BaseModel`, sin validadores ni herencia de un DTO de entrada). Responde siempre 200 `{"success": true,
   "message": …}` con el mismo texto, exista o no la cuenta, sea cual sea su estado y haya pasado o no el intervalo.
   Un cuerpo que no es un correo es 422. La ruta va en español aunque es nueva: AGENTS §4 (b) exceptúa del inglés
   solo las rutas públicas ya existentes, y esta sigue a sus vecinas de `/usuarios` a sabiendas, porque unificar el
   idioma es `(backlog P2)`, en `B-FUTURO`, y una sola ruta en inglés haría la asimetría más visible. El manejador va
   en inglés.
2. **A quién:** a una cuenta de turista, no borrada, con `email_verified_at` vacía, activa o inactiva. Nunca a una
   cuenta administrativa. El filtro es la consulta del repositorio, no un `if` sobre el rol en el servicio.
3. **Cuándo:** columna `users.verification_sent_at` (`TIMESTAMP WITH TIME ZONE`, admite vacío). La escriben el registro
   y cada reenvío. Un enlace nuevo exige que la columna esté vacía o que hayan pasado al menos
   `VERIFICATION_RESEND_INTERVAL_SECONDS` (60 por defecto) desde el último. Sin tope total. La migración `a64d0c2e7f15`
   no rellena ninguna fila: vacía significa "no consta envío" y deja pedir uno ya.
4. **El enlace es el de siempre:** el mismo token (`sub`, `scope`, `exp`, 15 minutos, sin identificador, sin guardar).
   Varios vigentes a la vez no son un riesgo: el primero que se usa llena la marca y los demás no cambian nada.
5. **Sin auditoría:** ni el registro ni el reenvío dejan fila por el envío; la hora es un dato operativo y ningún DTO
   la lleva.
6. **El correo sale en segundo plano**, como tras el registro. El texto del enlace caducado no cambia.

## Consecuencias

- Un turista cuyo enlace caducó lo pide de nuevo sin depender de un administrador. Hasta FE-18, solo desde la API.
- Un turista que un administrador activó sin verificar (BE-63) puede pedir el enlace; al usarlo solo se llena la marca.
- **Riesgo aceptado:** un turista anterior a la migración de ADR-0022 que verificó su correo y que un administrador
  desactivó después tiene la marca vacía, es indistinguible de uno pendiente y puede reactivarse con un enlace nuevo.
  Ningún entorno tiene usuarios reales (palabra de David); lo cierra el modelo de dos hechos (BE-62).
- **Declarado:** la respuesta puede tardar algo más cuando la cuenta es elegible (SEC3); el registro sigue revelando si
  un correo o una cédula existen.
- **Declarado:** dos peticiones simultáneas pueden enviar dos correos; no hay bloqueo de fila (como los dos clics de
  ADR-0022).
- El texto de la respuesta dice "espere un minuto": cambiar la variable exige cambiar el texto.
- La comparación con el intervalo va en SQL: SQLite, donde corre la suite, guarda la columna como texto sin zona.

## Alternativas consideradas

1. **"Marca vacía y no borrada", sin mirar el rol.** Rechazada: un admin desactivado por un superadmin, o creado
   inactivo, se activaría solo (ADR-0019).
2. **Exigir además `is_active` falso.** Propuesta y retirada (17:36): dejaría sin enlace al turista que un
   administrador activó sin verificar, que es la única vía para que llegue a tener su correo probado.
3. **Reenviar solo a cuentas con la hora llena.** Rechazada: deja sin reenvío a todo turista pendiente anterior al
   despliegue, que es a quien el ítem quiere ayudar.
4. **Tope total de enlaces.** Rechazado: vuelve a dejar la cuenta sin salida.
5. **Una fila de auditoría por reenvío.** Rechazada: llenaría el historial con cada clic sin valor para el negocio.
6. **Respuestas distintas (404 sin cuenta, 429 dentro del intervalo).** Rechazadas: dirían qué correos tienen cuenta.
7. **Un limitador de peticiones por librería.** Fuera: no está en las dependencias, y el límite pedido es por cuenta.
8. **Devolver un `dict` sin `response_model`, como `verificar-email`.** Rechazada por David (AGENTS §3: un router
   devuelve schemas): sin schema nada limita qué claves salen ni las documenta. Las rutas que ya lo hacen son BE-65.

## Evidencia

- Verificación (19 nov): un solo emisor del token y una sola ruta que programa el correo (grep global); rincón 1 leído
  en el código; adenda con las decisiones 1 a 10.
- Plan: RED y GREEN de cada fase, compuerta completa y 33 mutantes medidos en copias del repositorio
  (`docs/deuda/BE-64/plan.md`).
- OWASP, Forgot Password Cheat Sheet, "Forgot Password Request": mensaje igual exista o no la cuenta, tiempo de
  respuesta uniforme y límite por cuenta contra envíos automatizados, sin cifra. Trata de la recuperación de
  contraseña: aplica por analogía.
- Supabase, tabla "Auth rate limits" de "Going into production": la petición de confirmación de registro se limita por
  la última petición, 60 segundos por defecto, configurable. Es el valor por defecto de un producto, no una norma;
  ninguna fuente leída fija 60 s como estándar.
- Fuentes leídas el 19 nov en el texto fuente que sirve Context7, no en la página publicada.

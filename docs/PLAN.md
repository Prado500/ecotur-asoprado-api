# Ecotur-ASOPRADO — Plan de 15 días (23 oct → 6 nov 2026)

> Guárdalo en el repo como `docs/PLAN.md`, junto a `docs/CONTEXT.md`.
> Estado: **v1.3 (24 oct, noche) — línea base medida; día 3 recortado a media jornada (David no está disponible el domingo por la mañana).**
> Progreso diario: `docs/bitacora/`. Estado actual del proyecto: `docs/CONTEXT.md` §8. Este plan no lleva estado: lleva fechas y alcance. Cambio mayor respecto a v1:
> el **módulo de reservas no existía** (ni tabla ni lógica; el botón "reservar" no hacía nada),
> así que los días 4–5 se dedican a construirlo. Lo compensa que BE-03 y BE-04 ya estaban resueltos.
> Capacidad: 15 días × 8 h = **120 h de David**, en bloques 08:00–12:00 y 14:00–18:00.
> **Ojo:** el 7 de noviembre es **sábado**. Confirmar hoy si la oficina de trabajo de grado
> recibe ese día o si la entrega es en línea; si no, la fecha real es el **viernes 6**.

---

## 1. Tres decisiones que necesitan tu OK (el plan está construido sobre ellas)

### D1. Pruebas de usabilidad: se hacen de verdad, en remoto
No se fabrica evidencia. Se hacen sesiones reales y baratas (una tarde) que cumplen lo que la
propuesta promete: *"sesiones controladas con miembros de la organización ASOPRADO"* +
usuarios con perfil turista. Protocolo en §7. El gerente es un miembro real de ASOPRADO y el
usuario administrador real; eso es exactamente lo que el jurado espera ver.

### D2. El flujo agéntico no se corrige: se simplifica radicalmente
Diagnóstico completo en §5. Resumen: las 25 observaciones del Word son correctas y son
síntomas de una sola causa: buscar determinismo escribiendo procedimientos en prosa cada vez
más largos para un LLM. Eso no converge. El determinismo viene de herramientas
(linters, type checker, tests, verificador de capas, CI). Se conservan las tres ideas buenas
del flujo; se elimina la maquinaria de premisas/rúbrica/bitácoras. **Timebox: día 1 (tarde)
y día 2.** Después se mejora usándolo, no analizándolo.

### D3. Alcance del MVP para el 7 de noviembre
Criterio: entra lo que la propuesta promete o lo que el gerente pidió en el último sprint
planning y es viable en 2–3 días. Todo lo demás es "trabajo futuro" documentado.

| Entra | Por qué |
|---|---|
| **Módulo de reservas** (nuevo, según ADR-0002: una reserva por paquete y fecha, ventanas de disponibilidad, expiración de pendientes) | Es el núcleo del objetivo general ("optimice la gestión de reservas") y prerrequisito del pago. No existía. |
| Pasarela **Wompi sandbox** (pago de una reserva) | Pedido del gerente; está en wireframes de la propuesta; ya tienes credenciales |
| **Historial de reservas** del turista | Consecuencia lógica del pago; "gestión de reservas" está prometida |
| **Métricas mínimas** del admin (reservas por estado, ingresos por período) | "Métricas de ventas" está prometida en 5.1; se resuelve con 1 endpoint de agregados + 1 pantalla |
| **Sistema de diseño** del frontend + skeleton loaders + manejo de sesión expirada (401 → login) | Pedido del gerente; es lo que quita el olor a "hecho por IA" |
| Deuda técnica de backend **prioritaria** (ver §4) + suite de tests endurecida + quality gate en CI | Objetivo específico 3 ("prácticas de integración continua") y defendibilidad ante jurado |

| Sale (trabajo futuro, documentado) | Por qué |
|---|---|
| Notificaciones de cupos liberados | Requiere infraestructura (push/email) que no cabe |
| Agendamiento y configuración avanzada de fechas | No prometido; alto esfuerzo |
| Motor de tarifas dinámicas y descuentos | No prometido; alto riesgo |
| Funcionamiento **offline** del panel administrativo | El panel administrativo web **sí entra**: build web de Flutter con vistas protegidas por rol (paquetes, usuarios, métricas), instalable como PWA básica porque Flutter web incluye `manifest.json` y service worker por defecto. Lo que sale es el modo offline. Día 9: verificar nombre e iconos de Ecotur en el manifest. |
| "Disponibilidad en tiempo real" | Se redacta honestamente como "consulta de disponibilidad actualizada por petición" |

**Verificado el día 1:** la reserva no existía en backend ni en base de datos. El modelo quedó
definido y validado con la gerencia en **ADR-0002** (un paquete, una fecha, una reserva;
`party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado;
expiración perezosa). Este plan no repite el modelo: cualquier duda, al ADR.

---

## 2. Reparto de trabajo

### David (120 h)
Código, calidad, pruebas, artefactos técnicos (UML, MER, OpenAPI, manual de despliegue),
capítulos de arquitectura / metodología / resultados. Y **30 minutos al final de cada día:
bitácora del día** (`docs/bitacora/AAAA-MM-DD.md`: qué se hizo, qué se decidió, qué se dejó).
Esa bitácora es la evidencia de Scrum y del desarrollo asistido por IA para el documento.

### María Paula (en paralelo, desde hoy)
Mensaje de hoy: pedirle que suba a un Drive lo que tenga y acordar esta lista.

| Cuándo | Qué |
|---|---|
| 23–25 oct | Vaciar en la plantilla de la universidad lo que ya existe en la propuesta: planteamiento, justificación, objetivos, marco de referencia (está casi todo escrito). Capítulo de **Marco Lógico** y requisitos funcionales / no funcionales (David le pasa el backlog consolidado el día 1). |
| 26–31 oct | Borrador del **manual de usuario final** (capturas del prototipo actual; se actualizan al final). Plantillas para: casos de prueba de caja negra, protocolo de usabilidad, consentimiento informado, cuestionario SUS. |
| 1–2 nov | Apoyar las sesiones de usabilidad (tomar notas, aplicar SUS), transcribir resultados. |
| 3–6 nov | Formato, figuras, referencias IEEE, corrección de estilo, lectura completa final. |

---

## 3. Cronograma día a día

Cada día tiene un entregable verificable. Si un día se desborda, se recorta alcance (§1-D3),
nunca sueño ni el bloque de documento.

| # | Día | Mañana (08–12) | Tarde (14–18) | Entregable del día |
|---|---|---|---|---|
| 1 | **Vie 23 oct** | Aprobar este plan. Escribir a María Paula y al gerente (agendar sesión del 2 nov). Consolidar backlog: notas `.txt` de "deuda funcional" + cards de Trello → `docs/backlog.md` con ID, severidad, decisión (entra / sale / documentar). Crear `CLAUDE.md` + `docs/CONTEXT.md` + `docs/PLAN.md` en el repo. | Tooling de calidad en backend: `ruff`, `mypy`, `pytest-cov`, `import-linter` (reglas de capas de Clean Architecture). Correrlos y anotar la **línea base** (nº errores lint, nº errores de tipos, % cobertura, violaciones de capas). Verificar el diagnóstico de la suite de tests contra el código. | Repo con quality gate local + números de línea base (evidencia "antes") |
| 2 | **Sáb 24** | Flujo agéntico v1 en Claude Code (§5 y ADR-0001): `CLAUDE.md` con reglas, 4 comandos, hooks; portar `deuda-verificador` y `handoff-auditor`; reescribir el paso 6 de `plan-redactor`. | Primera deuda real de punta a punta con el flujo: **BE-01** (500 al crear paquete con URLs inválidas → excepción de dominio + 422/409). Es pequeña, reproducible y tiene test obvio: ideal para calibrar el flujo. | Flujo v1 probado + 1 deuda saldada con PR verde |
| 3 | **Dom 25** (solo tarde) | — (no disponible) | Mezclar el PR de docs+tooling. **BE-01 por el flujo** (`/deuda-verificar` → `/deuda-planear` → `/implementar` → `/auditar`): primera calibración real. Si sobra: `check.py` en el CI de Azure. | Flujo v1 calibrado + BE-01 saldado + contrato de capas en verde |
| 4 | **Lun 26** | **Mañana:** `ruff --fix` + formato en un commit mecánico; S1 (modelos a `Mapped[]`); huecos de tests B2/B3/B4 con **BE-02** y **BE-07**; `check.py` en el CI. **Tarde: reservas, núcleo (implementar ADR-0002).** Migración Alembic: `max_capacity` → `party_size`, `availability_mode`, `min_lead_days`, tabla `package_availability_windows`, tabla `reservations` con el **índice único parcial** `(package_id, reservation_date) WHERE status IN ('pending','confirmed')`. Estados pendiente → confirmada / cancelada / expirada. | Casos de uso y endpoints: crear (guardia de paquete inactivo o eliminado **BE-13**; `IntegrityError` → `DateAlreadyReserved` → 409), cancelar, listar las mías. Tests RED → GREEN, incluido el de concurrencia sobre el índice. | Reservas funcionando sin pago |
| 5 | **Mar 27** | `GET /packages/{id}/availability?from=&to=` (antelación mínima, ventanas, sin reserva activa), expiración perezosa de pendientes **en la misma transacción** antes de insertar, listado de reservas para admin, endpoint de métricas (agregados). | **Redactar el ADR de pagos** (recibirá el siguiente número libre). Puerto `PaymentGateway` + `FakeAdapter`; flujo reserva → pago (fake) → confirmada, de punta a punta con tests. | Dominio de reservas completo; pago desacoplado del proveedor |
| 6 | **Mié 28** | `WompiAdapter` sandbox: crear transacción, firma de integridad, URL de checkout. | Webhook de eventos idempotente → estado de reserva. `display_order` en paquetes (**BE-08**: columna + `PATCH` + `ORDER BY`). PR develop → staging. **Corte de Wompi 18:00:** si no funciona de punta a punta, queda `FakeAdapter` y se documenta como integración parcial. | Backend del MVP completo en staging |
| 7 | **Jue 29** | Frontend base: `flutter analyze` + reglas de lint; tema con tokens (color, tipografía, espaciado, radios); componentes base (botón con hover generalizado **FE-06**, card, input, estados vacío/error). | Interceptor HTTP: 401 → limpiar sesión → pantalla de login (**FE-01**). Aplicar tema a autenticación y catálogo. | Sistema de diseño operativo en 3–4 pantallas |
| 8 | **Vie 30** | Aplicar el sistema de diseño al resto de pantallas (turista y admin). Skeleton loaders (shimmer) y estados de carga/error consistentes (**FE-11**). | Lista corta: **FE-03, FE-07, FE-08, FE-09**; refresco del kanban al volver a la vista (mitigación de BE-14). | Frontend visualmente consistente |
| 9 | **Sáb 31** | Flujo de reserva en Flutter (fecha, personas, confirmación) + checkout Wompi. | Historial de reservas; pantalla de métricas del admin; campo de orden de aparición en el kanban (**BE-08** lado cliente). Build Android (APK) y build web. | MVP funcional de punta a punta |
| 10 | **Dom 1 nov** | Bug bash propio (si la pantalla de métricas quedó pendiente, se cierra aquí). Casos de prueba de caja negra (tabla: caso, pasos, esperado, obtenido, estado). | **Sesiones de usabilidad remotas, perfil turista** (4–5 personas, §7). | Resultados de pruebas documentados |
| 11 | **Lun 2 nov** | **Sesión de usabilidad con el gerente** (admin, videollamada). Correcciones rápidas. | Despliegue a `main`. Capturas finales para manual y documento. | Prototipo entregado y evidencia completa |
| 12 | **Mar 3** | UML desde el código (Mermaid/PlantUML): clases, componentes, despliegue, secuencia de autenticación / reserva / pago. MER desde los modelos. | Exportar OpenAPI. Manual técnico de despliegue (pipeline + BD en nube: ya lo dominas; es narrar lo que existe). | Anexos técnicos listos |
| 13 | **Mié 4** | Capítulo de arquitectura (decisiones y trade-offs desde los ADR). | Capítulo de metodología: Scrum real + desarrollo asistido por IA + flujo agéntico (lecciones aprendidas). | Dos capítulos en borrador |
| 14 | **Jue 5** | Capítulo de resultados: línea base vs. final (lint, tipos, cobertura, capas), caja negra, usabilidad (SUS). | Integrar con lo de María Paula; conclusiones; trabajo futuro (= backlog "sale" + deuda conocida); referencias. | Documento completo en borrador |
| 15 | **Vie 6** | Lectura completa; correcciones; formato. | PDF final; checklist de entrega; **entregar** (o sáb 7 si la oficina recibe). | Entregado |

**Reserva de contingencia:** no hay días libres; la contingencia es el recorte de alcance
(§1-D3) y el corte de Wompi del día 6. Si el día 9 el frontend no está, el día 10 se usa para
terminarlo y las pruebas de caja negra se mueven a la mañana del día 11.

---

## 4. Definition of Done técnico (aplica a cada PR, desde el día 3)

- `ruff check` y `ruff format --check` limpios.
- `mypy` limpio en los módulos tocados (estricto gradual, no en todo el repo de golpe).
- `import-linter` sin violaciones de capas (dominio no importa infraestructura; casos de uso
  no importan FastAPI; etc.).
- `pytest` verde; cobertura **no baja** respecto a la línea base.
- PR a `develop` con CI verde; descripción = qué, por qué, trade-off.
- Decisiones no triviales → ADR de 10–15 líneas en `docs/adr/NNNN-titulo.md`
  (contexto, decisión, alternativas, consecuencias).

Orden de prioridad de la deuda: (a) indefendible ante jurado, (b) bloquea un feature del
alcance, (c) barata. Lo demás → `docs/backlog.md` como deuda conocida.

Nota sobre "n sesiones simultáneas por usuario": con JWT sin estado eso es **por diseño**,
no un bug. Revocar sesiones exige estado en servidor (lista de revocación o rotación de
refresh tokens). Para el MVP: access token corto + refresh token, y un ADR que lo explique.

---

## 5. Flujo agéntico v1 (lo que reemplaza a `.opencode/`)

### Diagnóstico del flujo actual
- Forma: `deuda-verificador` → `verificacion.md` → `plan-redactor` (borrador 0 → premisas
  → validación contra "fuentes de autoridad" en 2 rondas → rúbrica C1–C5 en 2 rondas →
  bitácoras, delta, residuales, citas por decisión → `plan.md` con prompts por fase) →
  sesiones ejecutoras → `handoff-auditor` → `gap.md`.
- Las observaciones 3.x, 7.x, 10.x, 14, 16.x, 21.x piden "instrucciones exactas para cada
  escenario". Cada instrucción nueva abre nuevas ambigüedades (tú lo detectaste en 12 y 14).
  Un procedimiento epistemológico en prosa no es un guardarraíl; es más superficie de
  interpretación y más contexto consumido.
- Lo que sí es guardarraíl: lo que falla con exit code ≠ 0.

### Se conserva (ideas correctas del flujo viejo)
1. **Verificar la deuda en todo el repo antes de planear** (observación 19 y 24: correctas).
2. **Plan corto antes de código, con aprobación humana.**
3. **Auditoría independiente después de ejecutar** (handoff-auditor: idea correcta;
   el auditor lee el diff y los resultados de los gates, no el relato de la sesión ejecutora).
4. **Fuera de alcance → backlog** (los "residuales").
5. **Decisiones con evidencia y trade-offs** → se convierten en ADR, el formato estándar.

### Se elimina
Premisas, rúbrica, bitácoras multicolumna, delta, citas por decisión, rondas máximas.
Sustitutos: gates deterministas (§4) + diff + handoff de 15 líneas + ADR.
La verificación "contra fuentes de autoridad" se reduce a: consultar documentación oficial
(Context7) **solo para las APIs que el plan usa**, y fijar versiones en `pyproject.toml`.

### Artefactos v1 (runtime Claude Code, compatible con OpenCode — detalle en `CONTEXT.md` §5)
- `AGENTS.md`: **la única copia** de las reglas del proyecto (stack, comandos, reglas de
  arquitectura, convenciones, DoD técnico, qué no tocar, dónde está el contexto). `CLAUDE.md` lo
  importa con `@AGENTS.md` y añade solo lo específico de Claude Code (hooks, subagentes).
- `make check` (o `scripts/check.sh`): la compuerta completa, tool-neutral. Los hooks de Claude
  Code la llaman; en OpenCode la llaman los agentes por instrucción.
- `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/backlog.md`, `docs/adr/`, `docs/bitacora/`.
- Comandos en `.claude/commands/`:
  - `/deuda-verificar <ID>` → busca el patrón en **todo** el repo, lista archivos y alcance
    → `docs/deuda/<ID>/verificacion.md`.
  - `/deuda-planear <ID>` → plan de 1 página: objetivo, archivos, pasos, tests que lo prueban,
    riesgos, fuera de alcance. **Se detiene** hasta tu aprobación.
  - `/implementar <ID>` → ejecuta el plan aprobado, corre los gates, escribe handoff
    (diff resumido + resultados).
  - `/auditar <ID>` → subagente independiente: plan vs. diff vs. gates → gaps.
- Hooks: tras cada edición de `.py`, `ruff format` + `ruff check --fix`; antes de terminar,
  `pytest -q` del paquete tocado.

### Qué pasa con las 2 semanas de análisis
Van al capítulo de metodología como lecciones aprendidas, con evidencia: "intenté X,
observé Y (25 observaciones documentadas), concluí Z (determinismo por herramientas)".
Eso es investigación aplicada, no tiempo perdido.

---

## 6. Línea base → resultado (métricas para el capítulo de resultados)

Línea base medida el **24 oct 2026** (`python scripts/check.py`, Python 3.14.3, `develop` en `e4fd14d`):

| Métrica | Línea base (24 oct) | Final (día 11) |
|---|---|---|
| Archivos sin formatear (`ruff format --check`) | 34 de 90 | |
| Errores `ruff check` | 531 (E501 137 · D212 110 · B008 41* · UP045 33 · I001 29 · D205 28 · W292 21 · UP006 21 · F401 16 · B904 7 · resto < 12 c/u) | |
| Errores `mypy` | 44 en 12 archivos (29 en los dos servicios grandes; causa dominante: modelos tipados como `Column[...]` → S1, y `SECRET_KEY: str \| None` → A4) | |
| Contratos `import-linter` | **3 KEPT · 1 BROKEN.** Roto: "los servicios no conocen el transporte HTTP", por dependencia **transitiva**: `services → core/storage → fastapi` (líneas 60, 86, 138: `HTTPException` 415/500; la 138 es BE-01) y `services → core/security → fastapi/starlette` (imports sin usar: P1). (Antes de evaluar hubo que crear `app/api/__init__.py`: era un namespace package.) | |
| Tests | 116 passed · 0 failed · 1 warning (S5) | |
| Cobertura (`pytest-cov`, ramas incluidas) | **89 %** (908 sentencias, 88 sin cubrir). Puntos ciegos: `core/storage.py` **28 %** (zona de BE-01, A7 y SEC2), `core/email.py` 69 %, `main.py` 77 %, `service_repository.py` 77 % | |
| Casos de caja negra pasados / totales | — | |
| SUS promedio (turista / admin) | — | |

\* B008 son los 41 `Depends(...)` en argumentos por defecto: patrón oficial de FastAPI; se configuró como
excepción y desaparece al migrar a `Annotated` (D6/S3).

---

## 7. Protocolo real de pruebas de usabilidad (una tarde)

- **Participantes:** gerente de ASOPRADO (usuario administrador, sesión por videollamada
  con pantalla compartida) + 4–5 personas con perfil turista (amigos/familia; muestra por
  conveniencia, **declarada como tal** en el documento). Remoto es un método reconocido.
- **Tareas por rol:** turista: registrarse, explorar un paquete, reservar, pagar en sandbox,
  ver su historial. Admin: iniciar sesión, crear/editar un paquete, ver reservas, ver métricas.
- **Instrumentos:** consentimiento informado (1 página), guion de tareas, tiempo y errores por
  tarea, cuestionario **SUS** (10 preguntas, estándar), 3 preguntas abiertas.
- **Evidencia:** capturas, tabla de resultados, SUS por participante, hallazgos → correcciones
  del día 11 → se documenta "qué se corrigió a partir de las pruebas".
- **Logística:** agendar al gerente **hoy** para el lunes 2 de noviembre.

---

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| **El módulo de reservas no existía** (descubierto el día 1, no el 12) | Días 4–5 dedicados; se liberaron al estar ya resueltos BE-03 y BE-04. Modelo mínimo según ADR-0002 (una reserva por paquete y fecha), sin agendamiento avanzado. Si el día 5 no está completo, Wompi se reduce a `FakeAdapter` desde el inicio del día 6. |
| Wompi consume más de 2 días | Corte el día 6 a las 18:00; `FakeAdapter` deja el flujo completo y testeable |
| Frontend se desborda (área débil) | Sistema de diseño primero (consistencia), belleza después; recortar métricas admin a una tabla si no hay tiempo |
| María Paula no responde o no tiene avances | El plan asume su aporte solo en formato, manual de usuario y plantillas; si no aparece, se recorta el manual de usuario a lo mínimo |
| El 7 es sábado | Confirmar hoy; asumir viernes 6 como fecha real |
| Tiempo en "meta-trabajo" del flujo | Timebox cerrado: día 2 a las 18:00 el flujo se usa, no se discute |
| Perfeccionismo en deuda | Regla a-b-c de §4; lo demás es deuda conocida documentada |

---

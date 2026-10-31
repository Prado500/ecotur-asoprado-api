# Ecotur-ASOPRADO — Plan de trabajo hasta la entrega

> **Versión 2.0 — 31 oct 2026.** Cambios de esta versión: bitácoras `2026-10-30` (decisiones del replan: capacidad en
> tres regímenes, orden de bloques, `B-PAGOS` partido, usabilidad por criterio, corte de código nuevo) y `2026-10-31`
> (escritura; paso 0 copia ↔ dueño por sección; acordeón; domingos comodín; orden de sacrificio). Versiones anteriores:
> `2026-10-28` (v1.7), `2026-10-27` (v1.6), `2026-10-26` (v1.5), `2026-10-25` (v1.4). Versionado según ADR-0007.
>
> **Premisas** (el plan se construye sobre ellas y no las repite): fecha y forma de entrega, capacidad de trabajo en
> tres regímenes, regla de los domingos comodín y roles del equipo `(CONTEXT §2)`; lo que la propuesta compromete
> `(CONTEXT §3)`; alcance por el criterio de §1-D3. Progreso diario: `docs/bitacora/`; estado del proyecto y próximo
> paso: `(CONTEXT §8)`; avance del plan: columna `Cierre` de §3.

---

## 1. Las tres decisiones sobre las que se construye el plan

- **D1 — Pruebas de usabilidad reales y remotas** `(CONTEXT §6)`. No se fabrica evidencia. Protocolo y criterio de
  fecha en §7.
- **D2 — Flujo agéntico simplificado: determinismo por herramientas, no por prosa** `(ADR-0001)`. Estado y diseño del
  flujo: `(CONTEXT §5)`; inventario: `.claude/`; guía de uso: `(README de sesiones)`.
- **D3 — Criterio de alcance del MVP.** Entra lo que la propuesta compromete `(CONTEXT §3)`, lo mínimo para que una
  reserva funcione de punta a punta (crear, pagar, ver que existe y en qué estado), y lo que el gerente pidió en el
  último sprint planning, si cabe antes del corte de código nuevo (fila-hito de §3). Lo demás es `B-FUTURO`, con
  justificación por ítem. Prioridad de la deuda: (a) indefendible ante jurado, (b) bloquea un feature del alcance,
  (c) barata. La decisión por ítem vive en `docs/backlog.md`; la agrupación en bloques y su secuencia, en §2b.

---

## 2. Reparto de trabajo

- **David:** código, calidad, pruebas, artefactos técnicos y capítulos de arquitectura, metodología y resultados
  `(CONTEXT §2)`. La bitácora diaria es evidencia de Scrum y del desarrollo asistido por IA; quién la redacta y quién
  responde por ella: `(README de sesiones)`.
- **María Paula:** documento `(CONTEXT §2)`. Sus bloques se definen tras la reunión (hito en §3); el reparto propuesto
  que se le lleva está en `(CONTEXT §7)`. Hasta entonces, `B-MP-DOC` es un marcador en §2b sin filas en §3.

## 2b. Bloques de trabajo (composición y secuencia)

Un bloque agrupa ítems del backlog que se implementan y se mezclan juntos (normalmente un PR). Esta tabla no lleva
fechas: la fecha de cada media jornada vive solo en §3, y el detalle de cada ítem solo en `docs/backlog.md`. La
columna **Secuencia** numera las medias jornadas de 4 h (`m1`, `m2`, …) de cada bloque, en orden y sin fechas; §3 las
cita por número (`B-RESERVAS m3`) y nunca las repite. Deslizar es mover un número a otra fecha; la secuencia no se
toca. `[señal]` marca una media jornada que necesita red.

| Bloque | Ítems del backlog | Qué es | Secuencia (m = media jornada de 4 h) |
|---|---|---|---|
| `B-BE01` | BE-01, P1, A7 | Primera deuda por el flujo: `storage.py` sin HTTP, imports muertos de `security.py`, copia síncrona; contrato de capas 4 KEPT | Hecho (PR #61) |
| `B-CHECK-DOCS` | AF-01 | Reglas de ADR-0008 y su addendum en `scripts/check_docs.py`: días fuera de §3 (también dentro de PLAN), fecha de entrega en PLAN = CONTEXT §2, bloque citado existe en §2b, encabezado de versión (ADR-0007), fila de §3 cerrada sin marca, listado de citas por dueño (`--copias`), copia de hecho duro sin cita como hallazgo, columna Decisión con exactamente un bloque | m1 especificación a dos manos (David + Mentor, ~1 h) → Claude Code: verificar → planear → implementar → auditar → `/pr` |
| `B-FORMATO` | `ruff format` + `ruff check --fix` sobre todo el repo | Un solo commit mecánico, sin cambios de lógica | m1 (compartida con `B-CI`): commit mecánico, PR propio |
| `B-CI` | `scripts/check.py` en `.azure-pipelines/ci-pipeline.yml` | El CI ejecuta la compuerta, no solo pytest | m1 (compartida con `B-FORMATO`): pipeline, PR propio |
| `B-HIGIENE` | S2, S4, S5, S6, S7, D2, D3, D4, D5, A6, A8, A9, SEC1, SEC3, P2 (`detalle`→`detail`), SEC2 (verificar; mínimo lista blanca sin SVG + tamaño), BE-23, BE-24, BE-25, BE-26 (decidir), P3 (al tocar) | Ítems XS/S de la auditoría; cada uno un commit pequeño. Es el bloque con tope y la palanca de la semana | m1–m2 ítems en orden de severidad; al final de la última `m` fechada, lo no hecho recibe decisión nueva en el backlog ese mismo día (`Sale → B-FUTURO` o `Decidir en B-QA`) |
| `B-S1` | S1, Alembic (`env.py` importa `app.models`) | Modelos a `Mapped[]`/`mapped_column` antes de crear `Reservation`; mypy cae a casi cero | m1 modelos a `Mapped[]` · m2 mypy casi a cero; `env.py` importa `app.models` |
| `B-TESTS` | §9, huecos B2/B3/B4, BE-02, BE-07, A2 (revisión) | Suite conforme a `AGENTS.md` §5; al cerrar, ADR-0005 caduca si la compuerta queda en verde | m1 fábricas y `conftest` · m2 huecos B2/B3/B4 · m3 BE-02, BE-07, §9 · m4 cierre; compuerta medida |
| `B-RESERVAS` | BE-19, BE-13, BE-17, BE-18, A3 (solo en el código nuevo) | Módulo de reservas según ADR-0002 | m1 modelos 2.0 (`Package` ampliado, `PackageAvailabilityWindow`, `Reservation` con `Index(unique=True, postgresql_where=…)`), enums de estado, tests RED · m2 migración `--autogenerate` **revisada** con tres comprobaciones: `max_capacity → party_size` como `alter_column` (no drop/add), `WHERE` del índice parcial presente, migración corrida contra el dump de staging; repositorio `add()`/`flush()` sin `commit()` (A3) · m3 crear: guardia BE-13 (409), expiración perezosa en la misma transacción, `DateAlreadyReserved` desde `IntegrityError` → 409 · m4 cancelar; listar las mías (BE-17, paginado); disponibilidad por rango · m5 admin (listar, filtrar por estado) y métricas (BE-18, un endpoint de agregados) · m6 auditoría, `/pr` |
| `B-PAGOS` | BE-16, ADR de pagos, A4, A5, BE-12 (ADR; código si cabe) | Puerto `PaymentGateway` de dos sentidos (iniciar pago; interpretar evento), `FakeAdapter` que aprueba por regla y puede notificar, ruta de webhook idempotente y transiciones de estado de la reserva: todo local, sin red; reservas, frontend y tests funcionan contra él. A4, A5 y BE-12 van aquí por ser configuración y trabajo local que cabe en las mismas mañanas, no por ser pagos | m1 ADR de pagos (puerto de dos sentidos, `FakeAdapter`, transiciones, idempotencia por id de transacción + estado) → aprobación · m2 `Settings` con pydantic-settings (A4) primero, con el conmutador Fake/Wompi en configuración; puerto + `FakeAdapter` + ruta de webhook + transiciones; flujo reserva → pago falso → evento falso → `confirmed`; tests con evento duplicado · m3 resto de m2; `echo`, `lifespan`, cliente Azure (A5); BE-12 (ADR; `session_version` si cabe) · m4 auditoría, `/pr`; PR `develop` → `staging`; **pre-aviso** al gerente con ventana para la usabilidad (§7) `[señal]` |
| `B-WOMPI` | BE-27 | Adaptador real: crea la transacción/checkout en el sandbox, verifica la firma del evento y lo mapea al evento del puerto. Sin lógica de negocio; necesita red y URL pública; deslizable sin bloquear nada | m1 adaptador (transacción, checkout, firma, mapeo) con fixtures de eventos · m2 prueba en sandbox con tarjetas de prueba y webhook real a `staging` `[señal]` · m3 cierre, PR aparte; si el criterio de §7 se cumple entero, confirmación de la ventana al gerente |
| `B-ORDEN` | BE-08 | `display_order` + endpoint + `ORDER BY` | m1 migración `display_order`, `PATCH /packages/{id}/display-order`, `ORDER BY display_order NULLS LAST, created_at` |
| `B-FE-BASE` | FE-01, FE-06, FE-12 | Interceptor 401, sistema de diseño (tokens, componentes base) | m1 lints de Flutter; tema con tokens (color, tipografía, espaciado, radios) · m2 componentes base (botón con hover, campos, tarjetas, estados vacío/error) · m3 interceptor 401 → login; tema aplicado a autenticación y catálogo |
| `B-FE-LISTA` | FE-03, FE-04 (layout), FE-05 (señal visual), FE-07, FE-08, FE-09, FE-11, refresco al volver + pull-to-refresh (mitigación de BE-14) | Aplicar el sistema de diseño a todo; skeletons; lista corta | m1 tokens en todas las pantallas; FE-03, FE-08, FE-09 · m2 skeletons en lista y detalle (FE-11); señal visual del kanban (FE-05); FE-07; refresco y pull-to-refresh |
| `B-FE-RESERVAS` | FE-13, BE-28, manifest PWA (nombre e iconos de Ecotur) | Reserva, checkout (Wompi o `FakeAdapter`), listado mínimo de mis reservas, métricas, orden en kanban; builds Android y web | m1 `reservation_service`; selector de fecha alimentado por disponibilidad · m2 flujo de reserva (crear; detalle que re-consulta el paquete y maneja 404/409 con mensaje claro) · m3 checkout contra `FakeAdapter` · m4 mis reservas (listado mínimo con estado) · m5 métricas admin (tabla mínima) · m6 orden en kanban (BE-28) · m7 manifest; builds Android y web · m8 PR a `staging`; prueba manual de punta a punta `[señal]` |
| `B-QA` | Caja negra, bug bash, D1 (usabilidad, criterio de §7), despliegue a `main` | Evidencia para el capítulo de evaluación | m1–m2 casos de caja negra por módulo (tabla) · m3 bug bash · m4 correcciones · m5 despliegue a `main`, capturas `[señal]` · m6 instrumentos de usabilidad (de María Paula si se acordó; si no, de David) · m7–m8 sesiones con testers turista `[señal]` · m9 sesión con el gerente `[señal]` · m10 transcripción, SUS, lista de correcciones · m11–m18 correcciones de usabilidad · m19 segunda pasada de caja negra · m20 OpenAPI revisado; cierre de PRs · m21 medición de §6; despliegue final a `main` `[señal]` · m22 corte de código nuevo (hito de §3) |
| `B-DOCS-TEC` | UML, MER, OpenAPI, manual técnico, README | Anexos técnicos | m1–m2 UML desde código (componentes, secuencia de reserva y pago, casos de uso) · m3 MER · m4 OpenAPI como anexo · m5–m6 manual técnico de despliegue · m7 README y revisión de anexos · m8 colchón del bloque |
| `B-TESIS` | Capítulos de arquitectura, metodología, resultados; integración con María Paula; entrega | El documento | m1–m3 arquitectura (desde los ADR) · m4–m6 metodología (Scrum + IA + flujo + lecciones; bitácoras como evidencia) · m7–m9 resultados (§6, caja negra, SUS, correcciones derivadas) · m10–m11 integración con María Paula · m12 `B-FUTURO` como capítulo · m13 conclusiones · m14 referencias · m15 primera lectura completa · m16–m17 correcciones · m18 formato, figuras, PDF · m19 segunda lectura · m20–m21 correcciones finales, checklist de entrega · m22 margen |
| `B-MP-DOC` | Por definir tras la reunión con María Paula | Marcador; se parte en los bloques que salgan de la reunión | — |
| `B-FUTURO` | Todo lo marcado "Sale" en el backlog (BE-09, BE-10, BE-11 derivado, BE-14 tiempo real, BE-20, BE-21, BE-22, FE-10, D6/S3 y P2-handlers si no caben) | Capítulo de trabajo futuro, con justificación por ítem | — |

---

## 3. Cronograma (acordeón)

La secuencia de cada bloque vive en §2b y no se toca. Aquí se fecha **solo la semana en curso** de cada régimen; la
siguiente se fecha al cierre del último día trabajado de la semana, contando las medias jornadas perdidas (PLAN sube
versión menor cada vez). Si una fila se desborda, se recorta alcance (§1-D3, orden en §8), nunca sueño ni el tiempo
del documento. La columna `Cierre` lleva la marca del día (`✔` hecho, `◐` parcial, `✘` ningún bloque de la fila) con
el número de la bitácora que lo cuenta; es una copia consciente de la bitácora `(ADR-0008)`.

**Presupuesto de cada régimen:** `m` disponibles `(CONTEXT §2)` − secuencia restante = colchón, recalculado en cada
fechado. Los domingos nunca entran en "disponibles"; un domingo comodín solo repaga déficit `(CONTEXT §2)`. Dos
disparadores: **colchón negativo** → primero el comodín del domingo si está disponible; si no alcanza, el orden de
sacrificio de §8 ese mismo día; **más de dos `m` perdidas en la primera semana de Prado** → mitigación de entorno (§8).
Regla de red: commits locales siempre; push, PR y despliegues en la siguiente media jornada con señal (sin push no hay
CI; hasta entonces `python scripts/check.py` local es la única compuerta).

**Hitos fijos (no se re-fechan):**

- **Vie 18 dic, 18:00 — corte de código nuevo.** Después solo correcciones de usabilidad, bugs de caja negra y lo que
  un bloque ya abierto necesite para cerrar su PR. Se mueve solo hacia antes: si la reserva de punta a punta y la
  usabilidad ya están, las horas sobrantes van al documento; nunca hacia después. Lo que no esté → `B-FUTURO` (§1-D3).
- **Lun 11 ene — entrega en línea** `(CONTEXT §2)`. El domingo anterior es margen, no día planificado.
- **Reunión con María Paula** (fechada abajo); de ella salen `B-MP-DOC` y la respuesta a la pregunta de `(CONTEXT §7)`.

### Días cerrados bajo el plan v1.x (historia; el detalle está en cada bitácora)

| Día | Bloques planeados | Cierre |
|---|---|---|
| Vie 23 oct | Aprobación del plan, backlog, CONTEXT/PLAN; tooling y línea base | ✔ 23 |
| Sáb 24 | Flujo agéntico v1; `B-BE01` | ◐ 24 |
| Dom 25 | (media jornada) PR docs+tooling, ADR-0004, `/deuda-verificar BE-01` | ◐ 25 |
| Lun 26 | `B-BE01`, `B-FORMATO`, `B-CI`, `B-HIGIENE` | ✘ 26 |
| Mar 27 | `B-BE01`; `B-FORMATO`, `B-CI`, `B-S1` | ◐ 27 |
| Mié 28 | `B-S1`, `B-TESTS`, `B-RESERVAS` (esquema) | ✘ 28 |
| Jue 29 | `B-RESERVAS`, `B-PAGOS` | ✘ 29 |
| Vie 30 | `B-PAGOS`, `B-ORDEN` | ✘ 30 |
| Sáb 31 | PLAN 2.0; `B-CHECK-DOCS` | ◐ 31 |

### Régimen Bogotá `(CONTEXT §2)`: hasta la mudanza

**Presupuesto:** disponibles **10 m** (lun a vie: el sábado 31 ya está cerrado en la tabla de arriba, el sábado
siguiente es la mudanza `(CONTEXT §2)`; los sábados sí cuentan en Prado y en el régimen final; domingos fuera).
Secuencia: 9 (`B-FORMATO`+`B-CI` 1 · `B-HIGIENE` 1 ·
`B-S1` 2 · `B-TESTS` 4 · cierre 1) + **1 m de colchón**. Primera aplicación de las reglas, el 31 oct: la secuencia
era 11 (`B-CHECK-DOCS` 1, `B-HIGIENE` 2) contra 10 → colchón −1; el domingo entra como comodín y repaga
`B-CHECK-DOCS`; `B-HIGIENE` baja de 2 m a 1 m y esa media jornada queda como colchón de la semana. El recorte se hace
al principio y se deshace al final si sobró, nunca al revés: si el viernes el colchón no se gastó, vuelve a
`B-HIGIENE`; si se gastó, lo no hecho de `B-HIGIENE` recibe decisión nueva en el backlog ese día.

| Día | Mañana | Tarde | Cierre |
|---|---|---|---|
| Dom 1 nov | **Comodín (fuera del presupuesto):** `B-CHECK-DOCS m1`: especificación a dos manos, implementación por Claude Code, `/pr` | — | |
| Lun 2 | `B-FORMATO`+`B-CI` m1 (dos PR propios). A primera hora: mensaje a María Paula para fijar la reunión | `B-HIGIENE m1` (tope: 1 m; lo que no quepa → decisión nueva en backlog hoy). **Hito: reunión con María Paula, 17:00–18:00, dentro de esta media jornada**; si ella no puede, mar 3 a la misma hora (come una hora de `B-S1 m2`); sus filas se escriben al cierre de ese día (PLAN 2.1) | |
| Mar 3 | `B-S1 m1` | `B-S1 m2` | |
| Mié 4 | `B-TESTS m1` | `B-TESTS m2` | |
| Jue 5 | `B-TESTS m3` | `B-TESTS m4`: cierre; compuerta medida (verde → ADR-0005 superado). Si no cierra, el cierre de hoy lo declara deslizado y mueve la fila; no se arrastra en silencio | |
| Vie 6 | **Colchón (1 m):** si no se gastó, `B-HIGIENE m2` devuelto | Cierre de Bogotá: PR `develop` → `staging` `[señal]`; dump de la base de staging para `B-RESERVAS m2`; preparar mudanza. **Fechar la semana siguiente (Prado)** | |

### Régimen Prado `(CONTEXT §2)`: solo mañanas

**Presupuesto:** 19 m `(CONTEXT §2)`; secuencia 18 (`B-RESERVAS` 6 · `B-PAGOS` 4 · `B-ORDEN` 1 · `B-FE-BASE` 3 ·
`B-FE-LISTA` 2 · `B-FE-RESERVAS` 2); **colchón 1**. Orden: `B-RESERVAS` → `B-PAGOS` → `B-ORDEN` → `B-FE-BASE` →
`B-FE-LISTA` → `B-FE-RESERVAS`. La única media jornada que exige señal es `B-PAGOS m4` (PR a `staging` y pre-aviso).
El día de la mudanza no es día planificado. Las semanas se fechan al cierre del último día trabajado de la anterior.

| Día | Mañana | Cierre |
|---|---|---|
| (se fecha el vie 6) | | |

### Régimen final `(CONTEXT §2)`: jornada completa, lugar por confirmar

**Presupuesto:** 62 m `(CONTEXT §2)`; secuencia 61 (`B-FE-RESERVAS` m3–m8 · `B-WOMPI` 3 · `B-QA` 22 · `B-DOCS-TEC` 8 ·
`B-TESIS` 22); **colchón 1** más el domingo anterior a la entrega. Orden: `B-FE-RESERVAS` → `B-WOMPI` → `B-QA` →
`B-DOCS-TEC` → `B-TESIS`. Mientras el lugar no esté confirmado, el plan asume los riesgos de Prado; cuando se confirme
Bogotá, una versión menor lo dice. Las semanas se fechan al cierre del último día trabajado de la anterior.

| Día | Mañana | Tarde | Cierre |
|---|---|---|---|
| (se fecha al cerrar Prado) | | | |

---

## 4. Definition of Done técnico

Aplica a cada PR: la compuerta `python scripts/check.py` pasa y la cobertura no baja `(AGENTS §6)`; mientras la
compuerta global esté en rojo rige el trinquete contra la línea base `(ADR-0005)`; decisiones no triviales → ADR
`(AGENTS §7)`. Sesiones concurrentes con JWT sin estado son por diseño, no un bug; las opciones y el ADR previsto
están en `(backlog BE-12)`.

## 5. Flujo agéntico

Diagnóstico, decisión y lo que se conservó del flujo v0: `(ADR-0001)`; estado y diseño de compatibilidad:
`(CONTEXT §5)`; inventario: `.claude/`; guía de uso y rituales: `(README de sesiones)`. Las dos semanas de análisis
previas van al capítulo de metodología como lecciones aprendidas, con las observaciones archivadas como evidencia.

---

## 6. Línea base → resultado (métricas para el capítulo de resultados)

Medido con `python scripts/check.py` (Python 3.14) sobre `develop`. Columnas: línea base, estado tras el primer
ciclo del flujo (`B-BE01`), y la medición al corte de código nuevo (hito de §3), que se rellena ese día.

| Métrica | 24 oct, `e4fd14d` | 27 oct, `c8853af` (PR #61) | Al corte de código |
|---|---|---|---|
| Archivos sin formatear (`ruff format --check`) | 34 de 90 | no medido | |
| Errores `ruff check` | 531 (E501 137 · D212 110 · B008 41* · UP045 33 · I001 29 · D205 28 · W292 21 · UP006 21 · F401 16 · B904 7 · resto < 12 c/u) | 362 | |
| Errores `mypy` | 44 en 12 archivos (29 en los dos servicios grandes; causa dominante: modelos tipados como `Column[...]` → S1, y `SECRET_KEY: str \| None` → A4) | 44 (mismo conjunto de líneas) | |
| Contratos `import-linter` | **3 KEPT · 1 BROKEN.** Roto: "los servicios no conocen el transporte HTTP", por dependencia transitiva `services → core/storage → fastapi` y `services → core/security → fastapi/starlette` (BE-01 y P1). Antes de evaluar hubo que crear `app/api/__init__.py` | **4 KEPT · 0 BROKEN** | |
| Tests | 116 passed · 0 failed · 1 warning (S5) | 145 passed | |
| Cobertura (`pytest-cov`, ramas incluidas) | **89 %** (908 sentencias, 88 sin cubrir). Puntos ciegos: `core/storage.py` 28 %, `core/email.py` 69 %, `main.py` 77 %, `service_repository.py` 77 % | **93 %** (`core/storage.py` 100 %) | |
| Casos de caja negra pasados / totales | — | — | |
| SUS promedio (turista / admin) | — | — | |

\* B008 son los 41 `Depends(...)` en argumentos por defecto: patrón oficial de FastAPI; se configuró como
excepción y desaparece al migrar a `Annotated` (D6/S3). Evidencia por fase del 27 oct: `(ADR-0006)`.

---

## 7. Protocolo real de pruebas de usabilidad

- **Cuándo (criterio, no fecha), en dos pasos:** **pre-aviso** al gerente cuando el backend de reservas y pagos esté
  en `staging` contra `FakeAdapter` (`B-PAGOS m4`), proponiendo una **ventana de una semana**, no un día (reprogramar
  una fecha concreta cuesta credibilidad); **confirmación** del día dentro de la ventana cuando el flujo de reserva
  funcione de punta a punta en `staging` desde el cliente, con Wompi en sandbox si `B-WOMPI` está mezclado o con
  `FakeAdapter` si no (declarándolo como limitación en resultados: se mide todo el flujo menos la pantalla de Wompi).
  Tope: **15 de diciembre**, para que las correcciones y el capítulo de resultados quepan. Alerta: el flujo completo
  en el cliente cae en la primera semana del régimen final; un deslizamiento de una semana en Prado deja la usabilidad
  en el tope sin días de corrección (mitigación en §8). La sesión es real: el gerente es un miembro real de ASOPRADO
  y el usuario administrador real.
- **Participantes:** gerente (usuario administrador, videollamada con pantalla compartida) + 4–5 personas con perfil
  turista (muestra por conveniencia, **declarada como tal** en el documento). Remoto es un método reconocido.
- **Tareas por rol:** turista: registrarse, explorar un paquete, reservar, pagar (sandbox o falso), verificar su
  reserva en "mis reservas". Admin: iniciar sesión, crear/editar un paquete, ver reservas, ver métricas.
- **Instrumentos:** consentimiento informado (1 página), guion de tareas, tiempo y errores por tarea, cuestionario
  **SUS** (10 preguntas, estándar), 3 preguntas abiertas.
- **Evidencia:** capturas, tabla de resultados, SUS por participante, hallazgos → correcciones en `B-QA` → se documenta
  "qué se corrigió a partir de las pruebas".

---

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| **Déficit en cualquier régimen: remedios en orden** | Primero el comodín del domingo, si está disponible, decidido al cierre del último día trabajado `(CONTEXT §2)`. Solo si no alcanza o no hay domingo, recorte en este orden; cada escalón es una decisión por ítem escrita en el backlog el día que se toma, y **sale, no se traslada**: (1) `B-WOMPI`: `BE-27 → B-FUTURO`; la usabilidad se declara con `FakeAdapter` (§7). (2) Lo de `B-HIGIENE` aparcado en `B-QA` → `B-FUTURO`. (3) Pulido que nadie prometió y nadie mide: skeletons (FE-11), señal del kanban (FE-05), refresco y pull-to-refresh, `B-ORDEN` y BE-28; en Prado, antes de eso, `B-FE-BASE` al mínimo (tokens, 401, componentes básicos). (4) Correcciones de `B-QA` que no afecten al SUS ni a la caja negra. (5) Historial completo del turista (filtros, pasadas/próximas, detalle extendido) → `B-FUTURO`; el listado mínimo de mis reservas se queda: §1-D3 y la tarea de usabilidad de §7 lo requieren. **No se recortan:** métricas de admin en su versión mínima (`CONTEXT §3` las compromete; piso: BE-18), listado mínimo de mis reservas, `B-TESIS`, `B-DOCS-TEC`, la sesión de usabilidad. La lista existe para que la decisión no se tome cansado ni en Prado |
| Señal de internet caída hasta dos días sin aviso, cortes de luz de horas (régimen Prado) | Lo mecánico y lo que el CI ejecuta solo (`B-FORMATO`, `B-CI`) queda antes de la mudanza; en Prado, acordeón de §3 (secuencia fija, fechas por semana) y regla de red; push y despliegues en medias jornadas con señal |
| Las condiciones de Prado consumen más medias jornadas de las que el colchón cubre | **Criterio:** si en la primera semana de Prado se pierden más de dos `m`, se activa la mitigación de entorno: trabajar desde un sitio con señal estable (casa de un amigo, otro sector). Si aun así el colchón queda negativo, orden de sacrificio de la primera fila |
| Sin push no hay CI | En Prado, `python scripts/check.py` local es la única compuerta hasta la siguiente media jornada con señal; ningún PR se abre sin haberla pasado localmente |
| La usabilidad llega al tope de §7 sin días de corrección (pago, listado y despliegue caen en la primera semana del régimen final) | Pre-aviso en dos pasos (§7) desacopla la semana de aviso del frontend; si al PR a `staging` de `B-PAGOS` el backend no está, `B-FE-BASE` se reduce al mínimo para defender la ventana; historial completo y pulido ceden antes que la usabilidad |
| Reprogramar la usabilidad cuesta credibilidad | Al gerente se le propone una ventana de una semana, no un día; se confirma el día dentro de la ventana cuando el criterio de §7 se cumple entero |
| `WompiAdapter` consume más de lo previsto o no hay red | `FakeAdapter` deja el flujo completo y testeable por el mismo camino (webhook incluido); `B-WOMPI` es solo adaptador, PR aparte, primero en el orden de sacrificio |
| Frontend se desborda (área débil) | Sistema de diseño primero, belleza después; métricas admin en su versión mínima; pulido y historial completo ceden antes |
| El documento se queda sin tiempo | Corte de código nuevo fijo (hito de §3), movible solo hacia antes; tres semanas reservadas; `B-TESIS` y `B-DOCS-TEC` fuera del orden de sacrificio; sueño no negociable |
| María Paula no responde o no tiene avances | Reunión esta semana (hito de §3); el plan solo asume su aporte en formato, manual de usuario y plantillas; si no aparece, el manual se recorta a lo mínimo |
| Usabilidad tarde o sin gerente | Aviso con ventana; tope en §7; si el gerente no puede, se hace con los testers turista y se declara la ausencia del perfil admin |
| Tiempo en meta-trabajo del flujo y de los documentos (del 26 al 31 oct) | El flujo y los documentos solo cambian si un bloque se bloquea por su culpa; `B-CHECK-DOCS` tiene alcance fijo; el fechado semanal son cinco minutos |
| Perfeccionismo en deuda | Regla a-b-c de §1-D3; lo demás es deuda conocida documentada |
| Línea base desactualizada entre ítems | Un solo ítem en curso; hash de la verificación comparado por el ejecutor `(ADR-0005)` |

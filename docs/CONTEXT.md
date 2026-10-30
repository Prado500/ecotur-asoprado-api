# Ecotur-ASOPRADO — Contexto de trabajo (briefing portable)

> **Para qué sirve este archivo.** Es la memoria del proyecto para cualquier sesión de IA
> (Claude Code, OpenCode, el chat de Claude) y para cualquier persona que entre al repo.
> Vive en `docs/CONTEXT.md`. Regla de oro: **el contexto vive en archivos versionados, no en la
> memoria de un chat.** Cada sesión nueva arranca leyendo esto.
>
> **Versión 3.0 — 30 oct 2026.** Cambios de esta versión: bitácora `2026-10-30` (§0: tabla hecho → dueño y política
> de copias, ADR-0008 —cambia una regla, por eso mayor—, regla de addendum y orden de resolución de huérfanas por el
> addendum de ADR-0008; §2: capacidad en tres regímenes hasta la entrega; §6: fila del ADR-0008 y fe de erratas de D1; §8). Versiones
> anteriores: `2026-10-29` (2.10: §8), `2026-10-28` (2.9: §0 versionado, §6 ADR-0007), `2026-10-27` (§2, §4, §8; no
> subió versión ese día). Versionado según ADR-0007; la historia anterior vive en las bitácoras del 22 al 26 oct.

---

## 0. Cómo se mantienen estos documentos (léelo antes de editar cualquiera)

**Principio: un hecho tiene un solo dueño.** Los demás documentos lo citan, no lo repiten. La política de
copias es **ADR-0008**: un hecho duro (fecha, número, nombre de bloque, versión, estado, persona o rol) aparece a lo
sumo una vez por documento, nunca en un título, siempre con cita de forma fija al dueño (`(CONTEXT §2)`, `(PLAN §2b)`,
`(backlog ID)`, `(ADR-NNNN)`, `(AGENTS §N)`, `(README de sesiones)`, `(bitácora AAAA-MM-DD)`, `(docs/deuda/ID/)`); una
explicación puede resumirse con cita donde el documento la necesite; un documento vivo conserva lo que depende de, no
lo que explica. Si copia y dueño divergen, gana el dueño (para decisiones, el ADR más reciente).

**Mapa hecho → dueño.** Cualquier documento puede citar cualquier hecho con la forma fija; la última columna anota
solo las copias derivadas que un documento concreto lleva por diseño.

| Hecho | Dueño | Copia permitida (ADR-0008) |
|---|---|---|
| Deadline, forma de entrega, capacidad de trabajo (h/día, días/semana), roles del equipo, evaluadores, stakeholder | CONTEXT §2 | — |
| Lo que la propuesta aprobada compromete | CONTEXT §3 | — |
| Criterio de alcance del MVP (la regla con la que se decide qué entra) | PLAN §1-D3 | — |
| Decisión por ítem (`Entra · B-x` / `Sale → B-FUTURO` / `Hecho`) y severidad | backlog, fila del ítem | — |
| Composición de bloques (qué ítems van juntos, de quién) | PLAN §2b | los demás nombran el bloque, nunca listan sus ítems |
| Qué bloque se hace qué día | PLAN §3 | ninguna: los demás nombran el bloque, nunca el día |
| Hecho / no hecho de cada día, decisiones del día, lecciones, cuota | bitácora del día | PLAN §3, columna `Cierre`: `✔/◐/✘ DD` |
| Línea base y mediciones de calidad | PLAN §6 | — |
| Protocolo de usabilidad | PLAN §7 | — |
| Riesgos y mitigación | PLAN §8 | — |
| Decisiones de diseño y de proceso | ADR (inmutable; se supersede) | CONTEXT §6: una fila por ADR (fecha, decisión, efecto) |
| Reglas de código, arquitectura, tests, git | AGENTS.md (`CLAUDE.md` lo importa) | — |
| Qué se verifica con exit code | `scripts/check.py`, `scripts/check_docs.py` | — |
| Flujo agéntico: inventario (agentes, comandos, hooks, skills) | `.claude/` | — |
| Flujo agéntico: estado y diseño | CONTEXT §5 | — |
| Rituales de apertura y cierre; guía humana del flujo | README de sesiones (`docs/sesiones/README.md`) | — |
| Estado de saldado de un ítem (presente o ausente) | `docs/deuda/<ID>/` | — |
| Estado actual del proyecto y próximo paso | CONTEXT §4 y §8 | — |
| Dudas de estudio | `docs/aprendizaje/preguntas.md` | la bitácora del día: conteo y enlace |
| Versión de un documento vivo | su encabezado (ADR-0007) | — |

La tabla crece por incidente: cuando aparece una divergencia sobre información cuyo dueño no está registrado aquí, se
determina el dueño (el documento que cambiaría **de fondo** si el hecho cambiara) y se añade la fila ese día. Si parece
afectar a más de un documento, la sesión sigue el orden del addendum de ADR-0008: partir (cada parte, su dueño) → si no
se parte, uno decide y el otro lleva copia citada → solo si dos deciden de fondo, consultar a David; en los tres casos
llega con una propuesta y David valida antes de que la tabla crezca. Esas divergencias se detectan al leer (de forma
oportunista: aperturas que contrastan, revisiones de David), por la regla "hecho duro sin cita" de `check_docs.py`
cuando exista, o al ir a consignar un hecho y no encontrar su fila (ADR-0008, puntos 3 y 5 y addendum).
Naturaleza de cada archivo: los ADR son inmutables: un ADR aceptado no se edita, se supersede, o recibe un **addendum
fechado** que aclara o corrige una omisión sin alterar el texto original ni cambiar la decisión (si la decisión cambia,
es un ADR nuevo; primer uso: ADR-0008, 30 oct); CONTEXT, PLAN, backlog y `docs/sesiones/` son
vivos y versionados; las bitácoras son append-only (si algo cambió, se escribe en la entrada del día en que cambió).

**Rituales de apertura y de cierre:** viven en un solo sitio, `docs/sesiones/README.md`. Toda sesión
los sigue; este archivo no los repite para que no diverjan.

**Versionado (ADR-0007):** este archivo, `PLAN.md`, `backlog.md` y los artefactos de `docs/sesiones/` se versionan
**como archivos**: una línea `Versión X.Y — fecha` en el encabezado, seguida solo de las bitácoras que explican esa
versión. Las secciones no llevan versión ni fecha de revisión; las fechas dentro del texto son fechas de hechos.
Mayor (X.0) cuando cambia una premisa (deadline, alcance, capacidad, reglas); menor (X.Y) cuando cambia el
contenido. Se incrementa una vez por día de cambios (es decir, cuando el archivo y/o sus contenidos sufren de modificaciones), en el ritual de cierre.

Así no hay que "releer todo": el único documento que resume estado es este, y se revisa por
secciones.

**Los días viven solo en el cronograma de `PLAN.md` §3.** El backlog y este archivo referencian
**bloques de trabajo** (`B-BE01`, `B-RESERVAS`…, definidos en `PLAN.md` §2b), nunca días. Un
deslizamiento del plan mueve bloques entre filas del cronograma y no toca ningún otro documento.
(Lección del 26 oct: 56 filas del backlog llevaban días copiados y quedaron falsas tras un deslizamiento.)

## 1. Acuerdo de trabajo

- **Piloto:** David. **Copiloto:** la IA, en rol de ingeniero senior / profesor con paciencia.
- **Estándar:** no "que funcione", sino "bien hecho y entendido". Toda decisión no trivial se
  explica con el trade-off que prioriza, por qué, y qué implicaciones tiene.
- **Prueba de fuego:** David debe poder sustentar cada parte del código ante un jurado.
- **Honestidad:** la IA dice las cosas como son, incluso si contradicen el plan. No se fabrica
  evidencia de ningún tipo (decisión D1 del plan).
- **Verificar antes de aceptar:** David contrasta cada triage o diagnóstico de la IA contra el
  código (el 23 oct eso cerró tres ítems que la IA daba por pendientes).
- Idioma: español; jerga técnica en inglés cuando es el estándar.

## 2. Hechos duros

| Hecho | Detalle |
|---|---|
| **Deadline** | **11 de enero de 2027** (prórroga aceptada, comunicada a David el 27 oct 2026). Hasta entonces el deadline era el 7 nov 2026; `PLAN.md` v1.x se construyó sobre esa fecha y queda superado: el nuevo cronograma (v2.0) se escribe el 28 oct. La entrega sigue siendo **en línea** (enlace de Drive). |
| **Qué se entrega** | Solo el **documento final**. No hay demo en vivo ese día; la sustentación se define después si el documento se aprueba. |
| **Capacidad** | Tres regímenes hasta la entrega (David, 30 oct). **Bogotá, hasta el 6 nov:** L–V 8 h (08:00–12:00 y 14:00–18:00), sáb 7 h o menos, dom descanso → 47 h/semana. **Prado, 7–30 nov (90 % de probabilidad):** solo mañanas 08:00–12:00, seis días → 24 h/semana planificables; las tardes son de la práctica en ASOPRADO y no se planifican. Riesgos propios de Prado: señal de internet caída hasta 2 días sin aviso; cortes de luz de horas. **1 dic–11 ene:** termina la práctica; 8 h/día, seis días → 47 h/semana, menos 24, 25 y 31 dic y 1 ene; lugar (Prado o Bogotá) por confirmar: el plan asume los riesgos de Prado hasta que David confirme Bogotá. Sueño 21:00–05:30, no negociable. Hora Colombia. |
| **Compañera de tesis** | María Paula Ramos Carrillo. Rol acordado: documento (plantilla, Marco Lógico, manual de usuario, formato, referencias). Pendiente que suba a un Drive lo que ya tiene. |
| **Evaluadores** | Desconocidos. Supuesto de diseño: al menos uno sabe de ingeniería de software → código defendible, no perfecto. |
| **Stakeholder** | Gerente de ASOPRADO: aliado total, valida y firma lo que sea **verdad**. Para él Ecotur es una idea que no presiona; para la universidad resuelve un problema real de diversificación. La propuesta compromete "dejar" el prototipo, no garantizar su adopción. Palabras del gerente (23 oct): "vaya implementándolo como usted piensa y lo pulimos sobre la marcha". |

## 3. Lo que la propuesta aprobada compromete (esto es la ley)

**Título:** Prototipo y desarrollo de Ecotur-ASOPRADO: ecosistema digital web y móvil para la
gestión, promoción y comercialización de la oferta turística del distrito de adecuación de
tierras de Prado, Tolima. **Tutor:** Juan José Betancourt Lozano. **Modalidad:** investigación.

**Objetivo general:** prototipo de ecosistema digital (app multiplataforma móvil/web + sistema
web administrativo) que **optimice la gestión de reservas** y la promoción de servicios
turísticos de ASOPRADO.

**Objetivos específicos (literal):** (1) diagnosticar y formalizar requerimientos con **Marco
Lógico**; (2) diseñar arquitectura y UX/UI con wireframes y **UML** (componentes, secuencia,
entidad-relación, casos de uso); (3) construir Backend API, Frontend Web y App Móvil con
**integración continua**; (4) evaluar con **pruebas de caja negra y de usabilidad** y consolidar
**documentación técnica y de usuario**.

**Entregables (sección 5):** app Flutter para turistas (oferta "Ruta del Arroz", disponibilidad,
reservas); panel administrativo web (PWA; inventarios, usuarios, métricas de ventas); API
FastAPI documentada (OpenAPI); repositorio con Clean Architecture; documentación de arquitectura
(UML + MER); **manual técnico de despliegue**; **manual de usuario final**.

**Pruebas (4.2.4):** API, caja negra por módulo, **usabilidad en campo con miembros de ASOPRADO**.

**Metodología (sección 4):** Scrum + **"AI-Augmented Development… asistido por IA y verificado
por el equipo humano"**. → El flujo agéntico es parte de la metodología declarada.

### 3.6 Cabos sueltos de la propuesta y cómo se resuelven (estado al 24 oct)
| Cabo | Resolución |
|---|---|
| Pasarela de pagos (wireframes la nombran; presupuesto dice "No aplica") | **Decidido:** Wompi sandbox, puerto + adaptador, corte fijo (`B-PAGOS`, PLAN §3). ADR de pagos: pendiente de redacción (en `B-PAGOS`); tomará el siguiente número libre. |
| "Gestión de reservas" prometida | **No existía nada** (ni tabla ni lógica). Se construye en `B-RESERVAS` según **ADR-0002**. |
| "Disponibilidad en tiempo real" | Se redacta como "consulta de disponibilidad por fecha, por petición" (`GET /packages/{id}/availability`). Sin websockets. |
| "Modelo de aprendizaje supervisado" (4.2.2) | No aplica al alcance; se justifica en el documento. |
| "Microservicios" (resumen) vs "modular" | Lo construido es un **monolito modular** con Clean Architecture; se argumenta como decisión correcta para un MVP. |
| PWA para el panel admin | **Entra** como build web de Flutter con vistas protegidas por rol; es instalable (manifest + service worker por defecto de Flutter web). **No** se implementa modo offline; el documento lo redacta así. |
| Cronograma original de 24 semanas | Sustituido por `docs/PLAN.md` (15 días). |

## 4. Estado técnico actual (verificado por David el 23 oct; actualizado 27 oct)

### Backend
- **Python 3.14 en dev, CI y producción** (**ADR-0004**, escrito por David el 25 oct). Antes convivían 3.14 (venv, CI) y 3.11 (Dockerfile, `.python-version`).
- **Stack:** FastAPI async, SQLAlchemy async, Alembic, Pydantic, uvicorn. Clean/Onion. Sin
  clases de dominio propias (los modelos SQLAlchemy actúan como entidades: trade-off consciente
  de MVP, documentar).
- **Hecho y verificado:** autenticación JWT, registro con hash, handlers globales de
  excepciones, `UserAccessPolicy` con ABAC jerárquico (cubre delete y update), auditoría básica
  (`test_audit.py`). **Desde el 27 oct, los cuatro contratos de capas de `import-linter` se cumplen**
  (`B-BE01`: `storage.py` y `security.py` dejaron de arrastrar FastAPI; ADR-0006): ningún servicio conoce
  el transporte HTTP, ni directa ni transitivamente.
- **No existe:** módulo de reservas (ver ADR-0002), pagos, paginación, recuperación de
  contraseña, `display_order` de paquetes.
- **Tests y calidad:** pytest + mocks; 145 tests, cobertura 93 % (27 oct; línea base del 24 oct:
  116 y 89 %, PLAN §6). Tooling desde el 24 oct: `ruff`, `mypy`, `import-linter`, `pytest-cov`, unidos
  en `scripts/check.py` (AGENTS §6); la compuerta global sigue en rojo por deuda heredada (ruff 362,
  mypy 44) y rige el trinquete de ADR-0005 hasta `B-TESTS`. El diagnóstico de la suite (mocks sin
  `spec`, setup duplicado, aserciones sobre texto, sesión ≠ `get_db`, huecos B2/B3/B4) es la fila
  §9/BE-15 del backlog y se corrige en `B-TESTS`.
- **Deuda y features:** inventario completo con decisión por ítem en `docs/backlog.md`.

### CI/CD e infraestructura (operativa)
GitHub → Azure DevOps → Azure (Web App for Containers + BD administrada) → Docker Hub.
Tres entornos (`develop`, `staging`, `main`) con resource group propio. PR → webhook → CI
(quality gate, hoy solo tests) → merge → CD construye y publica imagen con tag del entorno →
la Web App la hala al reiniciar. Operación: 2 clics.

### Frontend (Flutter, MVVM; web + Android)
- Servicios ya separados **por recurso** (`audit_service`, `auth_service`, `catalog_service`,
  `session_service`, `user_service`); en `B-FE-RESERVAS` se añade `reservation_service`.
- **No existe:** manejo de 401 (sesión vencida no redirige al login), sistema de diseño,
  skeleton loaders, flujo de reserva/pago, historial, métricas.
- Kanban con desplazamiento horizontal en pantallas estrechas (patrón aceptable; falta señal
  visual). Hover solo en algunos botones. Texto seleccionable parcial.

## 5. Flujo agéntico (estado al 26 oct)

- **Decidido:** ADR-0001 (se conservan `deuda-verificador` y `handoff-auditor` con poda; se reescribe el
  paso 6 de `plan-redactor`; el determinismo pasa a herramientas ejecutadas por el ejecutor, el auditor y
  el CI; decisiones → ADR) y ADR-0005 (trinquete contra la línea base mientras la compuerta global esté en
  rojo; caduca al quedar en verde; la verificación registra el hash medido y el ejecutor lo compara).
- **Runtime principal: Claude Code**, con **compatibilidad con OpenCode** como requisito (posible trabajo
  futuro con otras personas). Diseño de compatibilidad:
  - Las reglas del proyecto viven **una sola vez** en `AGENTS.md`; `CLAUDE.md` lo importa (`@AGENTS.md`) y
    añade solo lo específico de Claude Code.
  - La compuerta de calidad vive en `scripts/check.py`, un punto de entrada tool-neutral: los hooks de
    Claude Code lo invocan automáticamente; en OpenCode los agentes lo invocan por instrucción.
  - Los cuerpos de los agentes se escriben sin sintaxis específica de una herramienta; solo el frontmatter
    cambia entre `.claude/agents/` y `.opencode/agent/`. `.opencode/` queda **congelado** como evidencia
    histórica; cuando haga falta, se genera desde `.claude/` con un script corto.
- **Inventario:** no se describe aquí para que no se desactualice. Los agentes son los archivos de
  `.claude/agents/`; los comandos, los de `.claude/commands/`; hooks y permisos, `.claude/settings.json` y
  `.claude/hooks/`; skills, `.claude/skills/`. La guía de uso para humanos (cuándo, qué hace, qué no hace)
  es la tabla de comandos de `docs/sesiones/README.md`, y `scripts/check_docs.py` verifica que ambas
  coincidan (la guía con el inventario).
- **Estado:** v1 construida el 24 oct; **primer ciclo completo ejecutado el 27 oct** con `B-BE01` (verificar →
  planear → 4 fases con auditoría → `/pr`), con dos calibraciones ese día (frontmatter de los agentes entre
  comillas; propuesta de reglas para la sesión Mentor, pendiente). Pendientes de flujo con dueño en §8.4;
  `check.py` aún no corre en el CI de Azure (`B-CI`).
- **Artefactos de datos por ítem** (`docs/deuda/<ID>/`): `verificacion.md`, `plan.md`, `progress.json`,
  `handoff-<fase>.md`, `gaps.md`. El estado de un ítem es lo que existe en su carpeta; no hay índice aparte.

## 6. Decisiones tomadas (índice)

| Fecha | Decisión | Dueño | Impacto en el documento de grado |
|---|---|---|---|
| 23 oct | D1 Pruebas de usabilidad reales y remotas (gerente como admin + 4–5 perfil turista; SUS). Sesión con el gerente: fecha por concretar (la propuesta del 2 nov no fue confirmada por él; aplazada, bitácora 2026-10-29). | `PLAN.md` §1, §7 | Cap. de evaluación (obj. específico 4): protocolo, SUS, resultados |
| 23 oct | D2 Simplificar el flujo agéntico; determinismo por herramientas; runtime Claude Code compatible con OpenCode. | **ADR-0001** | Cap. de metodología (desarrollo asistido por IA) y lecciones aprendidas |
| 23 oct | D3 Alcance del MVP (entra / sale). | `PLAN.md` §1, `backlog.md` | Alcance del prototipo y cap. de trabajo futuro |
| 23 oct | Modelo de reservas: un paquete, una fecha, una reserva; `party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado; expiración perezosa. Validado con gerencia. | **ADR-0002** | Cap. de diseño (MER, diagrama de clases, secuencia de reserva) y requisitos |
| 23 oct | Nombre de paquete **no** único (gerencia). | `backlog.md` BE-06 | Requisitos (regla de negocio) |
| 23 oct | El gerente sí espera reordenar paquetes desde el kanban → `display_order`. | `backlog.md` BE-08 | Requisitos y manual de usuario |
| 25 oct | Una sola versión de Python (3.14) en desarrollo, CI y producción. | **ADR-0004** | Cap. de arquitectura/despliegue y manual técnico |
| 25–26 oct | Trinquete de calidad contra la línea base mientras la compuerta global esté en rojo (caduca al quedar en verde); la verificación registra el hash medido y el ejecutor lo compara. | **ADR-0005** | Cap. de metodología (introducción de herramientas de calidad en código existente) |
| 25 oct | PR con commits atómicos se mezclan con *merge commit*, no squash. | `.claude/commands/pr.md`, `docs/sesiones/README.md` | Cap. de metodología (control de versiones) |
| 26 oct | Bloques de trabajo: la composición vive en `PLAN.md` §2b y los días solo en el cronograma; backlog y CONTEXT referencian bloques. | `CONTEXT.md` §0, `PLAN.md` §2b | Cap. de metodología (gestión del plan) |
| 26 oct | Finales de línea normalizados a LF en el repositorio. | `.gitattributes` | — |
| 27 oct | Cronograma v1.6: segundo deslizamiento pagado con recortes explícitos; superado el mismo día por la prórroga (entrega 11 ene 2027). | `PLAN.md` (línea de estado), §2 | Cap. de metodología (gestión del plan con hechos) |
| 27 oct | El adaptador de almacenamiento lanza excepciones de dominio (nunca `HTTPException`); lista blanca de URLs del CDN; copia síncrona antes de borrar; `InvalidImageUrlError` → 400 por contrato con el cliente (remapeo a 422 con P2). Supersede el residuo de `storage.py` de ADR-0003. | **ADR-0006** | Cap. de arquitectura (manejo de errores por capas) y resultados (contrato de capas 4 KEPT, cobertura) |
| 28 oct | Versionado de los documentos vivos: la versión es del archivo, no de una sección; mayor cuando cambia una premisa, menor cuando cambia el contenido; encabezado con solo referencias a bitácoras; aplica a CONTEXT, PLAN, backlog y `docs/sesiones/`. | **ADR-0007** | Cap. de metodología (gestión documental del proyecto) |
| 30 oct | Copias derivadas de un hecho: hecho duro a lo sumo una vez por documento, con cita de forma fija al dueño; explicaciones resumidas con cita; gana el dueño; mapa hecho → dueño solo en §0, crece por incidente; verificación acotada en el cierre por `check_docs.py`. | **ADR-0008**, `CONTEXT.md` §0, README de sesiones paso 3 | Cap. de metodología (evaluator-optimizer con revisión humana, bitácoras 28–30 oct) |
| pendiente | Pagos: puerto `PaymentGateway`, `WompiAdapter`, `FakeAdapter`, webhook idempotente. | ADR de pagos (`B-PAGOS`, tomará el siguiente número libre) | Cap. de diseño (secuencia de pago) y arquitectura |

## 7. Preguntas abiertas

- Qué tiene ya María Paula del documento (Drive pendiente).
- Para mencionar al gerente cuando convenga (no bloquean; están asumidas en ADR-0002): precio
  por paquete completo, antelación mínima 1 día, 30 min para pagar una reserva pendiente,
  tarifa de temporada alta como trabajo futuro.

## 8. Próximo paso (vie 30 oct, cierre)

Dónde estamos: sin cambios técnicos desde el 27 (`B-BE01` mezclado; compuerta global en rojo, ADR-0005 vigente; ningún
ítem de deuda en curso). **El 28, 29 y 30 fueron calibración documental** (bitácoras): ADR-0007, ADR-0008 con addendum,
mapa hecho → dueño en §0, README 1.0. **PLAN v2.0 sigue sin escribirse**, pero el replan quedó **decidido** el 30 a las
18:00 (bitácora del 30, "Replan: decisiones"): capacidad en tres regímenes (§2); orden de bloques del 26 con el bloque
de reglas de `check_docs.py` primero y `B-HIGIENE` de vuelta con tope de un día; `B-PAGOS` partido estructuralmente
(puerto + `FakeAdapter` + `Settings` en noviembre; `WompiAdapter` + webhook como PR aparte, deslizable si falla la red de
Prado); usabilidad por criterio (flujo de reserva de punta a punta en staging, Wompi sandbox si está o `FakeAdapter`
declarándolo; una semana de aviso; tope 15 dic); lo que necesita red (Wompi, usabilidad remota, despliegues) se
programa en mañanas con señal o en Bogotá; corte de código nuevo a mediados de diciembre; `B-TESIS` + `B-DOCS-TEC` +
integración con María Paula ocupan al menos tres semanas; reunión con María Paula esta semana, sus bloques se escriben
después. Fe de erratas aplicada en §6 (D1); PLAN §3 y §7 siguen diciendo "2 nov" hasta PLAN v2.0.

1. Sáb 31 oct, 08:00, sesión Mentor fresca: **PLAN v2.0** en ≤ 1 h con las decisiones anteriores ya tomadas: paso 0 por
   sección (diff copia ↔ dueño antes de recortar), título sin fecha, encabezado = versión + premisas citadas `(CONTEXT
   §2)`, §1-D3 como criterio, §4 y §5 como punteros, §2b con el bloque de reglas (nombre nuevo), `B-PAGOS` partido y filas
   para María Paula "por definir tras la reunión", §3 con columna `Cierre` y los tres regímenes, §6 con mediciones y hash,
   §7 con el criterio de usabilidad, §8 por bloques. PLAN → 2.0.
2. Especificación del bloque de reglas de `check_docs.py` (escrita por la sesión Mentor) → Claude Code en sesión fresca,
   ítem corto, PR propio. Reglas: bitácora del 29 "Decisiones" (C) y addendum de ADR-0008.
3. `B-FORMATO` → `B-CI` → `B-HIGIENE` (tope un día) → `B-S1` → `B-TESTS` → `B-RESERVAS`, en ese orden.
4. Pendientes de flujo (no urgentes, con dueño): YAML estricto en `check_docs.py`; `--estado` no distingue "mezclado";
   `/pr` con `#N`; README: compuerta con el venv activo; formalizar en `docs/sesiones/` las reglas del Mentor (solo
   `git log`; nada fuera de `docs/`; propuesta y permiso antes de escribir); `mentor.md` o el ritual de apertura: conectar
   la carpeta del repo antes del primer mensaje; la sesión verifica con `git log` que la rama de trabajo contiene el
   último cierre antes de escribir.

## 9. Sesiones de IA
Cualquier sesión (ingeniería, documento, estudio, mentor) arranca con los prompts de `docs/sesiones/` y el ritual
de apertura descrito allí; ninguna conversación es fuente de verdad. Preguntas de estudio:
`docs/aprendizaje/preguntas.md` (único dueño de las dudas; la bitácora solo las cuenta y enlaza).

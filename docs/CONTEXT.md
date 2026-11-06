# Ecotur-ASOPRADO — Contexto de trabajo (briefing portable)

> **Para qué sirve este archivo.** Es la memoria del proyecto para cualquier sesión de IA
> (Claude Code, OpenCode, el chat de Claude) y para cualquier persona que entre al repo.
> Vive en `docs/CONTEXT.md`. Regla de oro: **el contexto vive en archivos versionados, no en la
> memoria de un chat.** Cada sesión nueva arranca leyendo esto.
>
> **Versión 3.6 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` (§6: filas del 5 nov, bloque
> `B-GHOST-ADMIN`, I001 no autocorregible hasta A4, rol propio bloqueado por clave; §8 tras BE-02 hecho, `B-TESTS`
> deslizado al viernes y A4 adelantado; pendientes de flujo al día: `unfixable` hecho, AF-07 con fila).
> Versiones anteriores: `2026-11-04` (3.5: §0: fila de las fichas de estudio por ítem; §6: fila de ADR-0011; §8 tras
> BE-07 desmentida y BE-15 hecho, con la lista de pendientes de flujo al día); `2026-11-03` (3.4: §4: modelos en estilo 2.0 y dominio
> unificado con ADR; `import-linter` medido de verdad en local desde AF-05; §6: fila de ADR-0010; §8 tras `B-S1`, AF-05 y
> AF-04); `2026-11-02` (3.3: §4: medición de calidad citada a PLAN §6 en
> vez de copiada tres veces, CI con la compuerta; §5: `check.py` ya corre en el CI; §8 tras `B-FORMATO`, `B-CI` y `B-HIGIENE`);
> `2026-11-01` (3.2: §8 sin días ni fecha en el título; §0: regla de addenda en ADR-0009; §6: fila de
> ADR-0009);
> `2026-10-31` (3.1: §0: fila de composición ampliada con la secuencia de medias jornadas; §2: fila de deadline al día,
> regla de los domingos comodín y del fechado semanal, roles del equipo con el de David; §7: reparto propuesto a María
> Paula; §8);
> `2026-10-30` (3.0: §0: tabla hecho → dueño y política
> de copias, ADR-0008 —cambia una regla, por eso mayor—, regla de addendum y orden de resolución de huérfanas por el
> addendum de ADR-0008; §2: capacidad en tres regímenes hasta la entrega; §6: fila del ADR-0008 y fe de erratas de D1; §8). Versiones
> `2026-10-29` (2.10: §8), `2026-10-28` (2.9: §0 versionado, §6 ADR-0007), `2026-10-27` (§2, §4, §8; no
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
| Composición de bloques (qué ítems van juntos, de quién) y secuencia de medias jornadas numeradas dentro del bloque, sin fechas | PLAN §2b | los demás nombran el bloque, nunca listan sus ítems; PLAN §3 cita la secuencia por número (`B-RESERVAS m3`) y nunca la repite |
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
| Ficha de estudio de un ítem de deuda (antes / cómo se saldó / qué preguntaría un jurado) | `docs/aprendizaje/fichas/<ID>.md` | la bitácora del día: enlace; "Después" solo al cerrar el ítem |
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
es un ADR nuevo; regla en **ADR-0009**, tras los dos addenda de ADR-0008); CONTEXT, PLAN, backlog y `docs/sesiones/` son
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
| **Deadline** | **11 de enero de 2027** (prórroga aceptada, comunicada a David el 27 oct 2026). Hasta entonces el deadline era el 7 nov 2026; `PLAN.md` v1.x se construyó sobre esa fecha; PLAN 2.0 (31 oct) se construye sobre la nueva. La entrega sigue siendo **en línea** (enlace de Drive). |
| **Qué se entrega** | Solo el **documento final**. No hay demo en vivo ese día; la sustentación se define después si el documento se aprueba. |
| **Capacidad** | Tres regímenes hasta la entrega (David, 30 oct). **Bogotá, hasta el 6 nov:** L–V 8 h (08:00–12:00 y 14:00–18:00), sáb 7 h o menos, dom descanso → 47 h/semana. **Domingos (David, 31 oct):** descanso por defecto; un domingo puede usarse como **comodín de recuperación**: nunca entra en el presupuesto del plan (disponibles − secuencia se calcula sin domingos), se decide al cierre del último día trabajado de la semana y solo si el colchón es cero o negativo (nunca para adelantar secuencia), y queda registrado como excepción (bitácora del domingo, marca en `Cierre`, versión de lo que toque). **Fechado semanal:** la semana siguiente se fecha al cierre del último día trabajado de la anterior (PLAN §3, acordeón). La unidad de planificación es la media jornada de 4 h (`m`). **Prado, 7–30 nov (90 % de probabilidad):** solo mañanas 08:00–12:00, seis días → 24 h/semana planificables; las tardes son de la práctica en ASOPRADO y no se planifican. Riesgos propios de Prado: señal de internet caída hasta 2 días sin aviso; cortes de luz de horas. **1 dic–11 ene:** termina la práctica; 8 h/día, seis días → 47 h/semana, menos 24, 25 y 31 dic y 1 ene; lugar (Prado o Bogotá) por confirmar: el plan asume los riesgos de Prado hasta que David confirme Bogotá. Sueño 21:00–05:30, no negociable. Hora Colombia. |
| **Roles del equipo** | **David:** código, calidad, pruebas, artefactos técnicos (UML, MER, OpenAPI, manual de despliegue) y capítulos de arquitectura, metodología y resultados; responde por la bitácora diaria (README de sesiones). **María Paula Ramos Carrillo** (compañera de tesis): documento. Reparto acordado en la reunión `(bitácora 2026-11-02)`: ella amplía la especificación de requisitos con las historias de usuario que David le entrega y redacta esa sección (OE1); completa wireframes y diagramas de UX/UI con la retroalimentación de David (OE2); redactó los avances de metodología, que David revisa para que la narrativa de Scrum sea correcta; manuales y documentación son de los dos (OE4). Resultados por objetivo y conclusiones: sin dueño acordado; el plan los asume de David en `B-TESIS` hasta que se decida. |
| **Evaluadores** | Desconocidos. Supuesto de diseño: al menos uno sabe de ingeniería de software → código defendible, no perfecto. |
| **Stakeholder** | Gerente de ASOPRADO, Juan Guillermo: aliado total, valida y firma lo que sea **verdad**. Para él Ecotur es una idea que no presiona; para la universidad resuelve un problema real de diversificación. La propuesta compromete "dejar" el prototipo, no garantizar su adopción. Palabras del gerente (23 oct): "vaya implementándolo como usted piensa y lo pulimos sobre la marcha". |

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
  clases de dominio propias: los modelos SQLAlchemy son las entidades, declarados en estilo 2.0 (`Mapped[]`,
  `mapped_column`) desde el 3 nov (`B-S1`), con registro explícito en `app/models/__init__.py` y test (**ADR-0010**).
- **Hecho y verificado:** autenticación JWT, registro con hash, handlers globales de
  excepciones, `UserAccessPolicy` con ABAC jerárquico (cubre delete y update), auditoría básica
  (`test_audit.py`). **Desde el 27 oct, los cuatro contratos de capas de `import-linter` se cumplen**
  (`B-BE01`: `storage.py` y `security.py` dejaron de arrastrar FastAPI; ADR-0006): ningún servicio conoce
  el transporte HTTP, ni directa ni transitivamente.
- **No existe:** módulo de reservas (ver ADR-0002), pagos, paginación, recuperación de
  contraseña, `display_order` de paquetes.
- **Tests y calidad:** pytest + mocks; la medición vigente (tests, cobertura, ruff, mypy, contratos) es la última columna
  de `(PLAN §6)` y no se copia aquí. Tooling desde el 24 oct: `ruff`, `mypy`, `import-linter`, `pytest-cov`, unidos
  en `scripts/check.py` (AGENTS §6); la compuerta global sigue en rojo por deuda heredada de ruff y mypy y rige el
  trinquete de ADR-0005 hasta `B-TESTS`. Desde el 3 nov (AF-05) la compuerta local busca `lint-imports` en el
  directorio de scripts del intérprete y sale en rojo si no está: un "4 KEPT" ya no puede ser un paso que no corrió. Los tests de `scripts/check_docs.py` corren en la suite pero fuera de la cobertura. El diagnóstico de la suite (mocks sin
  `spec`, setup duplicado, aserciones sobre texto, sesión ≠ `get_db`, huecos B2/B3/B4) es la fila
  §9/BE-15 del backlog y se corrige en `B-TESTS`.
- **Deuda y features:** inventario completo con decisión por ítem en `docs/backlog.md`.

### CI/CD e infraestructura (operativa)
GitHub → Azure DevOps → Azure (Web App for Containers + BD administrada) → Docker Hub.
Tres entornos (`develop`, `staging`, `main`) con resource group propio. PR → webhook → CI
(`scripts/check.py` con ruff y mypy tolerados en rojo hasta `B-TESTS`, PLAN §2b) → merge → CD construye y publica imagen con tag del entorno →
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
  `check.py` corre en el CI de Azure desde `B-CI` `(PLAN §2b)`.
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
| 1 nov | Addenda a ADR aceptados: sección fechada y firmada al final; puede aclarar, corregir una omisión, afinar un criterio o decir cómo se cumple un punto; no puede cambiar la decisión ni el alcance (eso es ADR nuevo); tres addenda son señal de superseder. Segundo addendum de ADR-0008 el mismo día: R6 y R7 de `check_docs.py` corren solo con `--cierre`. | **ADR-0009**, ADR-0008 (addendum 1 nov), `CONTEXT.md` §0 | Cap. de metodología (cómo evolucionan las decisiones registradas) |
| 3 nov | Dominio unificado y estilo de modelos: los modelos SQLAlchemy son las entidades (retroactivo: práctica desde `20486ad`, citada en AGENTS §3 sin ADR); todo modelo en estilo 2.0, nulabilidad solo por la anotación, tipo SQL explícito donde el tipo Python no lo determina, `Enum` con `name=`, relaciones anotadas, registro explícito con test; un refactor de modelos se prueba con `alembic check` antes y después (M0 = M1). | **ADR-0010**, AGENTS §3 (PR de AF-04) | Cap. de diseño (modelo de datos) y de resultados (mypy 44 → 10 sin tocar el esquema) |
| 4 nov | La app y el test usan sesiones distintas en la suite: `get_db` se sustituye por una sesión nueva por petición, aparte de la `db_session` del test, sobre la misma conexión SQLite (`StaticPool`); dos reglas al escribir tests, "commit antes de la petición" y "refresh después"; límite aceptado: aislamiento de sesión, no de transacción (aislamiento real exige Postgres, BE-31). | **ADR-0011**, AGENTS §5 (PR de cierre del 4 nov) | Cap. de pruebas (la suite puede detectar un `commit()` olvidado antes del UoW de `B-RESERVAS`) |
| 5 nov | Nadie cambia su propio rol, superadmin incluido: la política bloquea la **clave** `role` en toda auto-edición (403), no su valor; crear usuarios con rol es otro camino. Confirmada por el flujo (BE-02). | `docs/deuda/BE-02/` (verificación con adenda, plan), `app/services/user_access_policy.py` | Cap. de diseño (autorización) |
| 5 nov | Los "rincones" que una verificación mide fuera de su alcance no se arreglan de paso: cada uno recibe fila; los cinco de BE-02 forman el bloque `B-GHOST-ADMIN` (que ningún jurado pueda dejar la plataforma sin administrador). | `docs/backlog.md` (BE-34..BE-38), `PLAN.md` §2b | Cap. de metodología (gestión de deuda) |
| 5 nov | I001 se reporta pero no se autocorrige (`unfixable = ["I001"]` en `pyproject.toml`) hasta que A4 centralice la configuración: reordenar imports de `app/` cambia el orden de carga. Cierra la opción abierta el 2 nov; sustituye la edición por Bash para esquivar el hook (S1). | `pyproject.toml`, `(bitácora 2026-11-05)` | Cap. de metodología (compuerta) |
| 5 nov | Lo rojo de la compuerta debe tener dueño en el backlog: una cifra en PLAN §6 es medición, no trabajo. BE-33 recoge lo manual sin dueño de `B-FORMATO`; A4 lo que depende de configuración. | `docs/backlog.md` (BE-33), `docs/aprendizaje/fichas/BE-33.md` | Cap. de metodología (gestión de deuda) |
| pendiente | Pagos: puerto `PaymentGateway`, `WompiAdapter`, `FakeAdapter`, webhook idempotente. | ADR de pagos (`B-PAGOS`, tomará el siguiente número libre) | Cap. de diseño (secuencia de pago) y arquitectura |

## 7. Preguntas abiertas

- Qué tiene ya María Paula del documento (Drive pendiente desde el 31 oct; no se trató el 2 nov; el reparto ya está acordado: §2).
- Quién redacta resultados por objetivo y conclusiones y recomendaciones (sin dueño acordado; §2).
- Fecha de la próxima reunión con María Paula; en ella, plantillas de caja negra, consentimiento y SUS y apoyo en
  las sesiones de usabilidad, que la reunión del 2 nov no cerró.
- Para mencionar al gerente cuando convenga (no bloquean; están asumidas en ADR-0002): precio
  por paquete completo, antelación mínima 1 día, 30 min para pagar una reserva pendiente,
  tarifa de temporada alta como trabajo futuro.

## 8. Próximo paso

Dónde estamos (estado al cierre de la bitácora `2026-11-05`): **BE-02 hecho** (confirmada por el flujo, una fase, PR #80;
regla "nadie cambia su propio rol" por clave; `docs/deuda/BE-02/`). **BE-33 nueva** en `B-TESTS`: los residuales de ruff y
mypy de `app/` sin dueño (lo manual de `B-FORMATO`); con A4 son la compuerta en verde. **`B-GHOST-ADMIN` nuevo** `(PLAN §2b)`
con BE-34..BE-38, los cinco rincones de la verificación de BE-02, por fechar. **AF-07 nueva** (comando literal en seis
sitios; lo edita David). `unfixable = ["I001"]` en `pyproject.toml` hasta A4. Notas de BE-03, B1–B5, D1 y S1 cerradas
tras re-verificación contra el código. **`B-TESTS` deslizado y declarado** `(PLAN §3)`: `m3` no existió; el colchón del
viernes se gasta en el bloque. Compuerta global sigue en rojo (ADR-0005 vigente; excepción declarada en el plan de BE-02
para dos archivos, caduca con BE-33 + A4). Medición en `(PLAN §6)`.

1. **Siguiente: el último día de Bogotá** `(PLAN §3)`, por decisión de David (bitácora `2026-11-05`, 18:48): mañana BE-33, A2, AF-02
   (puntos 2 y 3) y BE-32, **todos completos** (BE-32 decide `tests/` en `mypy.files`: el Mentor recomienda que sí);
   AF-07 si no se hizo el jueves; tarde A4 (adelantado de `B-PAGOS`; `/deuda-verificar` y `/deuda-planear` primero;
   al cerrar, retirar `unfixable I001` y aplicar I001) y cierre; compuerta medida en `develop`, `--soft` fuera si verde
   y ADR-0005 marcado superado; si sobra, halar de `B-FUTURO` en orden. Si no se mezcla, el día siguiente `(PLAN §3)`. Pendiente de
   BE-02 para su nota: confirmar contra el frontend que ninguna otra pantalla envía `role` en un `PATCH`.
2. **Ritual de cierre:** paso 3 con `python scripts/check_docs.py --copias "<dueño>"` por dueño tocado y `--cierre` antes
   del commit de cierre (README de sesiones, paso 3). La regla del retoque está en el README; el 5 nov se aplicó tras
   una auditoría (E1 de BE-02: retoque de test, sección "Enmiendas aprobadas" de `plan.md`).
3. **Cierre de Bogotá** `(PLAN §3)`: sujeto al replan del viernes (David no viaja el sábado). Antes del PR a `staging`:
   `CORS_ORIGINS` en las tres Web Apps y prueba del frontend de `develop` `(docs/deuda/SEC1/)`; el síntoma del 5 nov (el
   navegador envía `OPTIONS` y nunca el `POST` desde Flutter web) encaja con SEC1 y se confirma ahí. Después: dump de
   staging para `B-RESERVAS m2`, mudanza, fechar la semana de Prado y `B-GHOST-ADMIN`.
4. Prado y régimen final: orden y presupuestos en PLAN §3; secuencias en §2b. `B-RESERVAS m1` decide BE-31
   (`sqlite_where` espejo en el `Index`).
5. Pendientes de flujo (no urgentes, con dueño; pasan a filas `AF-0x` cuando se decida atacarlos): YAML estricto en
   `check_docs.py`; `/pr` con `#N`; formalizar en `docs/sesiones/` las reglas del Mentor (solo `git log`; nada fuera de
   `docs/`; propuesta y permiso antes de escribir; excepciones declaradas en bitácora); `mentor.md` más ligero por cuota
   (los ADR por su fila de §6, abriendo solo el que cite el ítem del día; de la bitácora anterior, solo su cierre) y
   **que diga Opus, no Fable**, salvo decisiones que paguen su juicio `(bitácora 2026-11-02)` (el 4 nov corrió en Fable
   por excepción declarada de un día); conectar la carpeta del
   repo antes del primer mensaje; deny list de plumbing de git (`commit-tree`, `update-ref`, `replace`, `filter-branch`,
   `reset`) y AGENTS §9 "reescribir historia por cualquier medio" `(bitácora 2026-11-02)`; `.github/pull_request_template.md`
   diverge de la skill `pr-author` (copia sin dueño); `unfixable = ["I001"]` en `pyproject.toml` **hecho** el 5 nov (BE-02; se retira al cerrar A4); el auditor
   commitea `gaps.md` con el prefijo `docs(item-<id>):` como el resto (el 4 nov lo hizo David a mano siete veces); el ejecutor pone
   `current_target` en `null` al terminar la última fase (BE-15 y BE-02 lo dejaron en `"Auditoria"`; David lo pone a mano);
   el planificador, al añadir una fase por enmienda, también la añade a `progress.json` y fija `current_target` (E3 no lo
   hizo; lo hizo el Mentor); `--estado` lee `PASS` solo en la última línea de `gaps.md` (AF-02 punto 3). Ya con fila: AF-02 y AF-07 `(backlog)`; AF-06 en `B-FUTURO`.

## 9. Sesiones de IA
Cualquier sesión (ingeniería, documento, estudio, mentor) arranca con los prompts de `docs/sesiones/` y el ritual
de apertura descrito allí; ninguna conversación es fuente de verdad. Preguntas de estudio:
`docs/aprendizaje/preguntas.md` (único dueño de las dudas; la bitácora solo las cuenta y enlaza).

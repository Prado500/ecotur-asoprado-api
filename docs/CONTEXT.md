# Ecotur-ASOPRADO — Contexto de trabajo (briefing portable)

> **Para qué sirve este archivo.** Es la memoria del proyecto para cualquier sesión de IA
> (Claude Code, OpenCode, el chat de Claude) y para cualquier persona que entre al repo.
> Vive en `docs/CONTEXT.md`. Regla de oro: **el contexto vive en archivos versionados, no en la
> memoria de un chat.** Cada sesión nueva arranca leyendo esto.
>
> **Versión 2.9 — 28 oct 2026.** Cambios de esta versión: bitácoras `2026-10-27` (§2 deadline, §4, §8; no subió
> versión ese día) y `2026-10-28` (§0 versionado, §6 ADR-0007). Versionado según ADR-0007; la historia de versiones
> anteriores vive en las bitácoras del 22 al 26 oct.

---

## 0. Cómo se mantienen estos documentos (léelo antes de editar cualquiera)

**Principio: un hecho tiene un solo dueño.** Los demás documentos lo enlazan, no lo repiten.

| Documento | Naturaleza | Dueño del hecho… |
|---|---|---|
| `docs/adr/NNNN-*.md` | **Inmutable.** Un ADR aceptado no se edita: se *supersede* con otro ADR que lo enlaza. | …de cada decisión de diseño o de proceso (modelo de reservas, flujo agéntico, pagos…). |
| `docs/CONTEXT.md` (este) | **Vivo.** Resumen del estado del mundo. | …del estado actual y de "dónde está cada cosa". Nunca re-explica una decisión: dice "ver ADR-000X". |
| `docs/PLAN.md` | **Vivo.** Cronograma y alcance. | …de fechas, días y qué entra / sale. |
| `docs/backlog.md` | **Vivo.** Inventario de trabajo. | …del estado de cada ítem (entra, sale, cerrado). |
| `docs/bitacora/AAAA-MM-DD.md` | **Append-only.** Diario. | …de lo que pasó cada día. No se corrige: si algo cambió, se escribe en la entrada del día en que cambió. |

**Rituales de apertura y de cierre:** viven en un solo sitio, `docs/sesiones/README.md`. Toda sesión
los sigue; este archivo no los repite para que no diverjan.

**Versionado (ADR-0007):** este archivo, `PLAN.md`, `backlog.md` y los artefactos de `docs/sesiones/` se versionan
**como archivos**: una línea `Versión X.Y — fecha` en el encabezado, seguida solo de las bitácoras que explican esa
versión. Las secciones no llevan versión ni fecha de revisión; las fechas dentro del texto son fechas de hechos.
Mayor (X.0) cuando cambia una premisa (deadline, alcance, capacidad, reglas); menor (X.Y) cuando cambia el
contenido. Se incrementa una vez por día de cambios (es decir, cuando el archivo y/o sus contenidos sufren de modificaciones), en el ritual de cierre.

Así no hay que "releer todo": el único documento que resume estado es este, y se revisa por
secciones. Cuando dos documentos digan cosas distintas, gana el ADR más reciente.

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
| **Capacidad** | 8 h/día, 7 días/semana: 08:00–12:00 y 14:00–18:00 (hora Colombia). Sueño 21:00–05:30, no negociable. Excepción conocida: dom 25 oct solo por la tarde. |
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
| 23 oct | D1 Pruebas de usabilidad reales y remotas (gerente como admin + 4–5 perfil turista; SUS). Sesión con el gerente: lunes 2 nov. | `PLAN.md` §1, §7 | Cap. de evaluación (obj. específico 4): protocolo, SUS, resultados |
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
| pendiente | Pagos: puerto `PaymentGateway`, `WompiAdapter`, `FakeAdapter`, webhook idempotente. | ADR de pagos (`B-PAGOS`, tomará el siguiente número libre) | Cap. de diseño (secuencia de pago) y arquitectura |

## 7. Preguntas abiertas

- Qué tiene ya María Paula del documento (Drive pendiente).
- Para mencionar al gerente cuando convenga (no bloquean; están asumidas en ADR-0002): precio
  por paquete completo, antelación mínima 1 día, 30 min para pagar una reserva pendiente,
  tarifa de temporada alta como trabajo futuro.

## 8. Próximo paso (mar 27 oct, cierre)

Dónde estamos: `B-BE01` (BE-01 + P1 + A7) completo por el flujo, ciclo entero (verificar → planear → A, B,
C, D con auditoría → `/pr`); contrato de capas **4 KEPT**, `storage.py` 100 %, 145 tests, 93 %; ADR-0006
aceptado. Rama `deuda/BE-01` lista para PR → `develop` (estado del merge: bitácora del 27, cierre). Dos
calibraciones del flujo hoy (frontmatter de `handoff-auditor`; el Mentor no debe tocar git ni archivos
fuera de `docs/`: propuesta pendiente). `B-FORMATO`, `B-CI`, `B-S1`, `B-TESTS` no se han hecho; la
compuerta global sigue en rojo y ADR-0005 vigente. **El deadline pasó al 11 ene 2027 (§2): PLAN §3 v1.6
queda superado.**

1. Apertura del 28 en sesión Mentor fresca: **replan en ≤ 1 h → PLAN v2.0** (§1 D3 alcance, §2b bloques,
   §3 cronograma hasta el 11 ene, §7 usabilidad). Entradas que solo David puede dar: capacidad real por
   semana hasta enero; si la sesión con el gerente del lun 2 nov se mantiene como primera ronda de
   usabilidad; qué ítems de `B-FUTURO` vuelven a entrar. Regla que no cambia: el alcance del MVP (D3) es el
   alcance; el tiempo extra va a calidad (compuerta en verde antes de reservas), a lo prometido por la
   propuesta y al documento, no a features nuevas sin ADR.
2. Si el PR de BE-01 no se mezcló el 27: CI verde → merge commit → `backlog.md` BE-01/P1/A7 → `Hecho (PR #N)`.
3. Con PLAN v2.0 aprobado: `B-FORMATO` (sin modelo) → `B-CI` → `B-S1` → `B-TESTS`, en ese orden, porque
   S1 es prerrequisito de `Reservation` y `B-TESTS` hace caducar ADR-0005.
4. Pendientes de flujo (no urgentes, con dueño): `check_docs.py` parsea los frontmatter de `.claude/agents/`
   con YAML estricto; `/pr` deja de mostrar `#N` como marcador; README: la compuerta se corre con el venv
   activo; decidir dónde viven las reglas del Mentor (`docs/sesiones/`).

## 9. Sesiones de IA
Cualquier sesión (ingeniería, documento, estudio, mentor) arranca con los prompts de `docs/sesiones/` y el ritual
de apertura descrito allí; ninguna conversación es fuente de verdad. Preguntas de estudio:
`docs/aprendizaje/preguntas.md` (único dueño de las dudas; la bitácora solo las cuenta y enlaza).

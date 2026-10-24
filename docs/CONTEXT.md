# Ecotur-ASOPRADO — Contexto de trabajo (briefing portable)

> **Para qué sirve este archivo.** Es la memoria del proyecto para cualquier sesión de IA
> (Claude Code, OpenCode, el chat de Claude) y para cualquier persona que entre al repo.
> Vive en `docs/CONTEXT.md`. Regla de oro: **el contexto vive en archivos versionados, no en la
> memoria de un chat.** Cada sesión nueva arranca leyendo esto.
>
> **Versión 2 — 24 oct 2026.** Sustituye por completo a la del 22 oct. Fuentes: conversación con
> David (22–23 oct), propuesta de trabajo de grado aprobada (PDF), Word de observaciones del
> flujo agéntico, notas de deuda funcional, ADR-0001 y ADR-0002.

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

**Ritual de cierre (30 min al final de cada día, ya previsto en el plan):**
1. Escribir la bitácora del día.
2. Si hubo una decisión nueva → ADR nuevo.
3. Si ese ADR cambia el estado del mundo → actualizar **solo** la sección afectada de `CONTEXT.md`
   (y `PLAN.md` / `backlog.md` si cambia alcance o fechas), dejando el enlace al ADR.
4. Anotar en la bitácora qué documentos se tocaron.

Así no hay que "releer todo": el único documento que resume estado es este, y se revisa por
secciones. Cuando dos documentos digan cosas distintas, gana el ADR más reciente.

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
| **Deadline** | **7 de noviembre de 2026 — es sábado.** Pendiente confirmar si la oficina recibe ese día o si la entrega es en línea; si no, la fecha real es el **viernes 6**. |
| **Qué se entrega** | Solo el **documento final**. No hay demo en vivo ese día; la sustentación se define después si el documento se aprueba. |
| **Capacidad** | 8 h/día, 7 días/semana: 08:00–12:00 y 14:00–18:00 (hora Colombia). Sueño 21:00–05:30, no negociable. |
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
| Pasarela de pagos (wireframes la nombran; presupuesto dice "No aplica") | **Decidido:** Wompi sandbox, puerto + adaptador, corte fijo (PLAN día 6). ADR de pagos: pendiente de redacción (PLAN día 5); tomará el siguiente número libre. |
| "Gestión de reservas" prometida | **No existía nada** (ni tabla ni lógica). Se construye los días 4–5 según **ADR-0002**. |
| "Disponibilidad en tiempo real" | Se redacta como "consulta de disponibilidad por fecha, por petición" (`GET /packages/{id}/availability`). Sin websockets. |
| "Modelo de aprendizaje supervisado" (4.2.2) | No aplica al alcance; se justifica en el documento. |
| "Microservicios" (resumen) vs "modular" | Lo construido es un **monolito modular** con Clean Architecture; se argumenta como decisión correcta para un MVP. |
| PWA para el panel admin | Web responsive; `manifest.json` solo si sobra tiempo. |
| Cronograma original de 24 semanas | Sustituido por `docs/PLAN.md` (15 días). |

## 4. Estado técnico actual (verificado por David el 23 oct)

### Backend
- **Stack:** FastAPI async, SQLAlchemy async, Alembic, Pydantic, uvicorn. Clean/Onion. Sin
  clases de dominio propias (los modelos SQLAlchemy actúan como entidades: trade-off consciente
  de MVP, documentar).
- **Hecho y verificado:** autenticación JWT, registro con hash, handlers globales de
  excepciones, `UserAccessPolicy` con ABAC jerárquico (cubre delete y update), **ningún servicio
  importa FastAPI ni lanza `HTTPException`**, auditoría básica (`test_audit.py`).
- **No existe:** módulo de reservas (ver ADR-0002), pagos, paginación, recuperación de
  contraseña, `display_order` de paquetes.
- **Tests:** pytest + mocks. Diagnóstico previo de Claude Code (mocks sin `spec`, setup
  duplicado, aserciones sobre texto, sesión ≠ `get_db`, huecos B2/B3/B4) **pendiente de
  verificar contra el código** al montar el tooling. **Confirmado:** no hay linters, ni type
  checker, ni medición de cobertura.
- **Deuda y features:** inventario completo con decisión por ítem en `docs/backlog.md` (v1.1).

### CI/CD e infraestructura (operativa)
GitHub → Azure DevOps → Azure (Web App for Containers + BD administrada) → Docker Hub.
Tres entornos (`develop`, `staging`, `main`) con resource group propio. PR → webhook → CI
(quality gate, hoy solo tests) → merge → CD construye y publica imagen con tag del entorno →
la Web App la hala al reiniciar. Operación: 2 clics.

### Frontend (Flutter, MVVM; web + Android)
- Servicios ya separados **por recurso** (`audit_service`, `auth_service`, `catalog_service`,
  `session_service`, `user_service`); el día 9 se añade `reservation_service`.
- **No existe:** manejo de 401 (sesión vencida no redirige al login), sistema de diseño,
  skeleton loaders, flujo de reserva/pago, historial, métricas.
- Kanban con desplazamiento horizontal en pantallas estrechas (patrón aceptable; falta señal
  visual). Hover solo en algunos botones. Texto seleccionable parcial.

## 5. Flujo agéntico (estado al 24 oct)

- **Decidido (ADR-0001):** se conservan `deuda-verificador` y `handoff-auditor` con poda; se
  reescribe el paso 6 de `plan-redactor`; el determinismo pasa a herramientas (ruff, mypy,
  import-linter, pytest-cov) ejecutadas por el ejecutor, el auditor y el CI. Decisiones → ADR.
- **Runtime principal: Claude Code**, con **compatibilidad con OpenCode** como requisito
  (posible trabajo futuro con otras personas). Diseño de compatibilidad:
  - Las reglas del proyecto viven **una sola vez** en `AGENTS.md` (formato que leen varias
    herramientas); `CLAUDE.md` lo importa (`@AGENTS.md`) y añade solo lo específico de Claude Code.
  - La compuerta de calidad vive en un objetivo tool-neutral (`make check` o
    `scripts/check.sh`): los hooks de Claude Code la invocan automáticamente; en OpenCode los
    agentes la invocan por instrucción. Misma compuerta, distinto disparador.
  - Los cuerpos de los agentes se escriben sin sintaxis específica de una herramienta; solo el
    frontmatter cambia entre `.claude/agents/` y `.opencode/agent/`. Mientras OpenCode no se use
    de verdad, `.opencode/` queda **congelado** como evidencia histórica y no se mantiene en
    paralelo; cuando haga falta, se genera desde `.claude/` con un script de 20 líneas.
- **Por construir (PLAN día 2):** `AGENTS.md` + `CLAUDE.md`, `.claude/agents/`,
  `.claude/commands/` (`/deuda-verificar`, `/deuda-planear`, `/implementar`, `/auditar`),
  hooks, `make check`.
- **Artefactos de datos que se conservan:** `docs/deuda/<tag>/verificacion.md`, `plan.md`,
  `progress.json`, `gaps.md`, `docs/deuda/registro.json`.

## 6. Decisiones tomadas (índice)

| Fecha | Decisión | Dueño |
|---|---|---|
| 23 oct | D1 Pruebas de usabilidad reales y remotas (gerente como admin + 4–5 perfil turista; SUS). Sesión con el gerente: lunes 2 nov. | `PLAN.md` §1, §7 |
| 23 oct | D2 Simplificar el flujo agéntico; determinismo por herramientas; runtime Claude Code compatible con OpenCode. | **ADR-0001** |
| 23 oct | D3 Alcance del MVP (entra / sale). | `PLAN.md` §1, `backlog.md` |
| 23 oct | Modelo de reservas: un paquete, una fecha, una reserva; `party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado; expiración perezosa. Validado con gerencia. | **ADR-0002** |
| 23 oct | Nombre de paquete **no** único (gerencia). | `backlog.md` BE-06 |
| 23 oct | El gerente sí espera reordenar paquetes desde el kanban → `display_order`. | `backlog.md` BE-08 |
| pendiente | Pagos: puerto `PaymentGateway`, `WompiAdapter`, `FakeAdapter`, webhook idempotente. | ADR de pagos (día 5) |

## 7. Preguntas abiertas

- ¿La oficina de trabajo de grado recibe el **sábado 7**? Si no, la fecha es el viernes 6.
- Qué tiene ya María Paula del documento (Drive pendiente).
- Para mencionar al gerente cuando convenga (no bloquean; están asumidas en ADR-0002): precio
  por paquete completo, antelación mínima 1 día, 30 min para pagar una reserva pendiente,
  tarifa de temporada alta como trabajo futuro.

## 8. Próximo paso (sáb 24 oct, 08:00 — PLAN día 2)

1. Línea base de tooling que no alcanzó el día 1: ruff, mypy, pytest-cov, import-linter →
   números "antes" en `PLAN.md` §6. Verificar el diagnóstico de la suite contra el código.
2. Flujo v1: `AGENTS.md` + `CLAUDE.md`, agentes, comandos, hooks, `make check`.
3. Primera deuda real por el flujo: BE-01 (500 al crear paquete con URLs inválidas).
4. Cierre: bitácora del día + sincronizar `CONTEXT.md` si algo cambió.

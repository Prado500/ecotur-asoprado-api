# Sesiones de IA: cómo arrancar cualquiera sin depender de ninguna conversación anterior

Las sesiones **no se sincronizan entre sí: se sincronizan a través del repositorio.** Cada una arranca
leyendo los mismos archivos y cierra actualizándolos. Tres roles, tres prompts:

| Rol | Dónde | Prompt de arranque | Para qué |
|---|---|---|---|
| Ingeniería | Claude Code en la raíz del repo | no necesita: `CLAUDE.md` → `AGENTS.md` → `docs/` se cargan solos. Para pedir segunda opinión sobre un plan, usa `ingenieria-revision.md` | flujo de deuda y features; revisar planes; commits y PR con las skills |
| Documento | Claude (web/escritorio) con la carpeta del repo conectada | `documento.md` | escribir y revisar capítulos del trabajo de grado |
| Estudio | Claude (web/escritorio), sin repo o con él | `estudio.md` | las preguntas de `docs/aprendizaje/preguntas.md` |

**Ritual de apertura (toda sesión):** `git pull` → leer `docs/CONTEXT.md` §0 y §8 → mirar `docs/adr/` y la última
`docs/bitacora/` → recién entonces trabajar.
**Ritual de cierre (toda sesión):** bitácora del día (hecho, no hecho, decisiones, lecciones, documentos
tocados; las dudas van a `docs/aprendizaje/preguntas.md` y la bitácora solo las cuenta) → ADR si hubo
decisión → sección afectada de `CONTEXT.md`, `PLAN.md` o `backlog.md` → commit. Si una sesión no cerró con esto, la siguiente empieza desactualizada.

## Comandos de Claude Code (se escriben en la sesión abierta con `claude` en la raíz del repo)

| Comando | Cuándo | Qué hace | Qué NO hace |
|---|---|---|---|
| `/deuda-verificar BE-01` | Antes de planear cualquier ítem del backlog o tag de auditoría | `deuda-verificador` busca el patrón en todo el repo, corre la compuerta como línea base y escribe `docs/deuda/BE-01/verificacion.md` | No planea ni toca código |
| `/deuda-planear BE-01` | Cuando la verificación dice `confirmada` o `parcial` | `plan-redactor` escribe `plan.md` (fases ≤ 5 archivos, tests RED primero, commits exactos) y `progress.json`, y **se detiene a pedir tu aprobación** | No ejecuta ninguna fase |
| `/revisar BE-01 plan` | Cuando algo del artefacto no te convence o el redactor te dejó un trade-off para decidir | Segunda opinión senior que lee `AGENTS.md`, los ADR y el código antes de opinar; te dice qué aprobaría y qué cambiaría | No edita nada: la decisión es tuya y el cambio lo ejecuta el flujo |
| `/implementar BE-01 A` | Con el plan aprobado y `current_target` en esa fase (o con `gaps.md` con bloqueantes de esa fase) | `fase-ejecutor`, en contexto fresco: TDD, compuerta completa, commit con el mensaje exacto del plan, `progress.json`, `handoff-A.md` | No toca otras fases; no hace push |
| `/auditar BE-01 A` | Justo después de cada `/implementar` | `handoff-auditor` re-ejecuta la compuerta, contrasta plan ↔ diff ↔ `progress.json` y escribe `gaps.md` con `PASS` o `GAPS` | No corrige nada; si hay bloqueantes, vuelves a `/implementar` |
| `/duda <pregunta>` | Una pregunta de concepto suelta, en medio del trabajo | Modo profesor en el contexto de tu código; al final te ofrece anotarla en `docs/aprendizaje/preguntas.md` | No edita código ni otros documentos |
| `/pr` | Cuando la rama está lista para ir a `develop` | Con las skills `commit-author`/`pr-author`: título, descripción (por qué, commits, cómo se probó, residuales, referencias) y mensaje de merge | No hace push, no abre ni mezcla el PR |

**Ciclo típico de un ítem:** `/deuda-verificar` → `/deuda-planear` → (`/revisar` si dudas) → apruebas →
`/implementar A` → `/auditar A` → … última fase → `/pr` → abres el PR en GitHub → CI verde → merge commit.

**Argumentos:** el ID tal como aparece en `docs/backlog.md` (`BE-01`, `FE-03`, `A3`, `SEC2`); la fase es la
letra del plan (`A`, `B`, …); el artefacto de `/revisar` es `verificacion`, `plan`, `handoff-A` o `gaps`.

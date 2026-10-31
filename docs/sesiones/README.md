# Sesiones de IA: cómo arrancar cualquiera sin depender de ninguna conversación anterior

> **Versión 1.1 — 31 oct 2026.** Cambios de esta versión: bitácora `2026-10-31` (paso 1 del ritual de cierre: de quién
> es la bitácora y qué hace la sesión con ella; regla decidida el 29 y llevada a su dueño el 31). Versiones anteriores:
> `2026-10-30` (1.0, primera numerada según ADR-0007: paso 3 del ritual de cierre: dueños → tabla de `CONTEXT.md` §0;
> pasada de citas de ADR-0008; herramientas de git para saber cuál cambió último, addendum de ADR-0008).

Las sesiones **no se sincronizan entre sí: se sincronizan a través del repositorio.** Cada una arranca
leyendo los mismos archivos y cierra actualizándolos. Cuatro roles, cuatro prompts:

| Rol | Dónde | Prompt de arranque | Para qué |
|---|---|---|---|
| Ingeniería | Claude Code en la raíz del repo | no necesita: `CLAUDE.md` → `AGENTS.md` → `docs/` se cargan solos. Para pedir segunda opinión sobre un plan, usa `ingenieria-revision.md` | flujo de deuda y features; revisar planes; commits y PR con las skills |
| Documento | Claude (web/escritorio) con la carpeta del repo conectada | `documento.md` | escribir y revisar capítulos del trabajo de grado |
| Estudio | Claude (web/escritorio), sin repo o con él | `estudio.md` | las preguntas de `docs/aprendizaje/preguntas.md` |
| Mentor | Claude (web/escritorio) con la carpeta del repo conectada | `mentor.md` | acompañamiento del día: juzgar artefactos del flujo antes de aprobar, replanificar, ritual de cierre. Es el rol que tuvo la primera conversación (22–26 oct) |

**Ritual de apertura (toda sesión):** `git pull` → leer `docs/CONTEXT.md` secciones 0 y 8 → mirar
`docs/adr/` y la última `docs/bitacora/` → recién entonces trabajar. Es deliberadamente corto: cada rol
lee lo demás según lo pida su prompt.

**Ritual de cierre (toda sesión).** Responde a una sola pregunta: *¿cómo se entera la siguiente sesión de
lo que pasó en esta?* No por memoria (no la tiene), sino leyendo archivos. Cuatro pasos, en este orden
porque cada uno alimenta al siguiente:

1. **Bitácora del día** (`docs/bitacora/AAAA-MM-DD.md`, append-only): hecho, no hecho, decisiones,
   lecciones, documentos tocados. **La bitácora es responsabilidad de David; la sesión la redacta y le señala lo que
   falta** (decidido el 29 oct). Para las dudas, la sesión **no confía en su memoria**: lee
   `docs/aprendizaje/preguntas.md` y lo compara con la bitácora anterior (o con `git log -p` de ese
   archivo) para listar las dudas nuevas del día, incluidas las que entraron por `/duda` desde Claude Code;
   si alguna no se entiende, le pregunta a David. La bitácora las cuenta y enlaza; `preguntas.md` es el dueño.
2. **ADR si hubo decisión** de diseño o de proceso. La bitácora la menciona; el ADR la posee.
3. **Solo la sección afectada de cada documento dueño del hecho.** No se reescribe todo: se corrige lo que
   cambió, en el sitio que lo posee. **Quién posee qué lo dice la tabla hecho → dueño de `CONTEXT.md` §0**, única
   copia; este README no la repite. Si el cambio fue una decisión (criterio nuevo, regla nueva), además su ADR
   (paso 2). Si cambió un comando del flujo, también su fila en la tabla de comandos de este README, y `CLAUDE.md`
   si cambia lo que Claude Code debe saber al arrancar.

   Regla práctica: antes de cerrar, `git status` y `git log --since=<hoy>` dicen qué archivos cambiaron. **Pasada de
   citas (ADR-0008, punto 6):** por cada archivo dueño que cambió hoy, **la sesión que cierra** lista sus citas en los
   demás documentos (`scripts/check_docs.py` cuando tenga la regla; mientras tanto, `grep -n "(CONTEXT §2)"
   docs/*.md docs/sesiones/*.md`, una vez por dueño tocado) y revisa cada copia: si diverge, la corrige hacia el
   dueño; si cree que la copia es la correcta o más reciente, no corrige, lo anota en la bitácora y pregunta a David.
   Para saber cuál cambió último: `git log -1 --format=%ad -- <archivo>` (archivo) y `git blame -L <n>,<n> -- <archivo>`
   (línea); copia commiteada después que el dueño = alarma, no corrección (ADR-0008, addendum).
   Nada de esto recae en David salvo esa decisión. Lo que `check_docs.py` pueda verificar, lo verifica; lo demás es
   responsabilidad de la sesión que hizo el cambio.
4. **Commit** (y PR). Un archivo sin commitear no existe para una sesión que arranca con `git pull` en
   otra máquina o en otra rama.

Si una sesión no cierra con esto, la siguiente empieza desactualizada; y la que lo note deja fe de erratas
en la bitácora del día en que lo nota, nunca editando la bitácora anterior.

## Comandos de Claude Code (se escriben en la sesión abierta con `claude` en la raíz del repo)

| Comando | Cuándo | Qué hace                                                                                                                                                                  | Qué NO hace |
|---|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| `/deuda-verificar BE-01` | Antes de planear cualquier ítem del backlog o tag de auditoría | `deuda-verificador` busca el patrón en todo el repo, corre la compuerta como línea base y escribe `docs/deuda/BE-01/verificacion.md`                                      | No planea ni toca código |
| `/deuda-planear BE-01` | Cuando la verificación dice `confirmada` o `parcial` | `plan-redactor` escribe `plan.md` (fases ≤ 5 archivos, 1 dominio por fase,  tests RED primero, commits exactos) y `progress.json`, y **se detiene a pedir tu aprobación** | No ejecuta ninguna fase |
| `/revisar BE-01 plan` | Cuando algo del artefacto no te convence o el redactor te dejó un trade-off para decidir | Segunda opinión senior que lee `AGENTS.md`, los ADR y el código antes de opinar; te dice qué aprobaría y qué cambiaría                                                    | No edita nada: la decisión es tuya y el cambio lo ejecuta el flujo |
| `/implementar BE-01 A` | Con el plan aprobado y `current_target` en esa fase (o con `gaps.md` con bloqueantes de esa fase) | `fase-ejecutor`, en contexto fresco: TDD, compuerta completa, commit con el mensaje exacto del plan, `progress.json`, `handoff-A.md`                                      | No toca otras fases; no hace push |
| `/auditar BE-01 A` | Justo después de cada `/implementar` | `handoff-auditor` re-ejecuta la compuerta, contrasta plan ↔ diff ↔ `progress.json` y escribe `gaps.md` con `PASS` o `GAPS`                                                | No corrige nada; si hay bloqueantes, vuelves a `/implementar` |
| `/duda <pregunta>` | Una pregunta de concepto suelta, en medio del trabajo | Modo profesor en el contexto de tu código; al final te ofrece anotarla en `docs/aprendizaje/preguntas.md`                                                                 | No edita código ni otros documentos |
| `/pr` | Cuando la rama está lista para ir a `develop` | Con las skills `commit-author`/`pr-author`: título, descripción (por qué, commits, cómo se probó, residuales, referencias) y mensaje de merge                             | No hace push, no abre ni mezcla el PR |

**Ciclo típico de un ítem:** `/deuda-verificar` → `/deuda-planear` → (`/revisar` si dudas) → apruebas →
`/implementar A` → `/auditar A` → … última fase → `/pr` → abres el PR en GitHub → CI verde → merge commit.

**Argumentos:** el ID tal como aparece en `docs/backlog.md` (`BE-01`, `FE-03`, `A3`, `SEC2`); la fase es la
letra del plan (`A`, `B`, …); el artefacto de `/revisar` es `verificacion`, `plan`, `handoff-A` o `gaps`.

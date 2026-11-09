# Sesiones de IA: cómo arrancar cualquiera sin depender de ninguna conversación anterior

> **Versión 1.6 — 9 nov 2026.** Cambios de esta versión: bitácora `2026-11-09` (paso 3: qué se hace ante un falso positivo de
> `check_docs.py`: esquivar en el documento, declarar, fila `AF-xx`; el prompt de la batería pide la salida completa). Versiones
> anteriores: `2026-11-07` (1.5, bitácora `2026-11-07` (paso 3: la batería de `check_docs.py` la ejecuta
> Claude Code con un prompt fijo y la sesión que cierra revisa la salida, AF-10; `mentor.md` 2.0: modo ejemplo obligatorio y tres
> líneas fijas tras cada auditoría)); `2026-11-06` (1.4, bitácora `2026-11-06` ("modo ejemplo" al final de `estudio.md` y
> `mentor.md`: cómo pide David una explicación con dato real, acciones en orden, punto de ruptura y regla al final). Versiones
> anteriores: `2026-11-04` (1.3, regla del retoque: un retoque aprobado
> a un plan es una edición a `plan.md` antes de `/implementar`, o no existe; decidida el 2 nov, aplicada el 3 y el 4).
> Versiones anteriores: `2026-11-01` (1.2, paso 3: pasada de citas con `--copias`,
> candidatos con `--huerfanas` y `--cierre` antes del commit de cierre; AF-01); `2026-10-31` (1.1,
> paso 1 del ritual de cierre: de quién es la bitácora y qué hace la sesión con ella; regla decidida el 29 y llevada a
> su dueño el 31);
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
   demás documentos (`python scripts/check_docs.py --copias "<dueño>"`, una vez por dueño tocado; `--huerfanas` lista
   candidatos a hecho duro sin cita, ruidoso a propósito) y revisa cada copia: si diverge, la corrige hacia el
   dueño; si cree que la copia es la correcta o más reciente, no corrige, lo anota en la bitácora y pregunta a David.
   Para saber cuál cambió último: `git log -1 --format=%ad -- <archivo>` (archivo) y `git blame -L <n>,<n> -- <archivo>`
   (línea); copia commiteada después que el dueño = alarma, no corrección (ADR-0008, addendum).
   Nada de esto recae en David salvo esa decisión. Lo que `check_docs.py` pueda verificar, lo verifica; lo demás es
   responsabilidad de la sesión que hizo el cambio. **Antes del commit de cierre: `python scripts/check_docs.py --cierre`**
   (encabezados de versión no anteriores al último commit, ADR-0007; filas pasadas de PLAN §3 con marca). Son las dos
   reglas que dependen de `git` y del día, y por eso no corren en la compuerta (ADR-0008, addendum del 1 nov). **Quién la ejecuta (desde el 7 nov):** Claude Code, con el prompt fijo de la bitácora `2026-11-07` (una vez por dueño con
   cambios en `git status`, más `--huerfanas`, `--cierre` y `--estado`; salida literal, sin editar ni commitear), porque la sesión
   Mentor no puede correr el venv del repo; la sesión que cierra revisa esa salida y decide. AF-10 convertirá el prompt en comando.
   El prompt pide **la salida completa de cada comando**, no solo los exit codes (lección del 7 nov). **Falso positivo de
   `check_docs.py`** (decidido el 9 nov): cuando la herramienta se equivoca y el documento está bien, el trabajo no se detiene:
   se esquiva en el documento con la edición mínima que no cambie ningún hecho, se declara en la bitácora del día con la causa
   verificada (línea del script), y el defecto recibe fila `AF-xx` en `B-FUTURO`. No se arregla el script "de paso" (AGENTS §7) ni
   se deja la compuerta de cierre en rojo por una razón falsa. Primer caso: AF-11 (`_cells()` y la barra vertical escapada en una celda de PLAN §3).
4. **Commit** (y PR). Un archivo sin commitear no existe para una sesión que arranca con `git pull` en
   otra máquina o en otra rama.

Si una sesión no cierra con esto, la siguiente empieza desactualizada; y la que lo note deja fe de erratas
en la bitácora del día en que lo nota, nunca editando la bitácora anterior.

**Regla del retoque (decidida el 2 nov, aquí desde el 4).** Un retoque aprobado a un plan (una decisión que el
planificador dejó abierta, un cambio de alcance, una fase nueva) es una **edición a `plan.md`** (o a la adenda de
`verificacion.md`, si es anterior al plan) hecha antes de `/implementar`, o no existe: los agentes leen archivos, no
conversaciones. Se registra en la sección "Enmiendas aprobadas" de `plan.md` con fecha y hora, con el texto literal
de David, y el planificador recalcula lo que dependa de ella (tabla de fases, Verificación final, `progress.json`,
incluido `current_target` si la enmienda añade una fase). Ejemplos: la adenda y las cinco enmiendas de AF-05 (3 nov);
E1–E3 de BE-15 (4 nov).

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

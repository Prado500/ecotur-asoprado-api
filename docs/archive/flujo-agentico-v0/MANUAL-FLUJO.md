# Manual del Flujo Agéntico de Deuda Técnica

> Documento de operación para el mantenedor humano (tú y quien trabaja contigo el grado). Explica **cómo funciona** el flujo, **qué haces tú en cada momento**, y **cómo detectar y responder** a resultados no deseados. Léelo completo al menos una vez antes de usarlo.

---

## 1. Filosofía en 5 ideas

1. **Las sesiones nacen sin memoria.** Cada sesión de un agente arranca con contexto vacío. Por eso TODO el estado del trabajo vive en archivos del repo (`docs/deuda/`), no en el chat. Fuente: *Anthropic, "Effective harnesses for long-running agents" (2025)*.
2. **Un contexto fresco es una ventaja, no un problema.** El auditor revisa con ojos limpios (sin sesgo de quien escribió el código). Por eso auditar NUNCA se hace en la misma sesión que ejecutó. Fuente: *Anthropic, "Claude Code best practices"*.
3. **El humano aprueba antes de cada paso destructivo o costoso.** Nadie ejecuta un plan sin tu "sí". Fuente: *Anthropic, "Building effective agents" (human checkpoints)*.
4. **Una fase = lo que una sesión termina completa.** RED → GREEN → commit → progress → handoff. Si una fase no cabe en eso, está mal dimensionada. Fuente: *Anthropic harness (one feature per session)*.
5. **Solo se persiguen gaps que rompen corrección o contrato.** Los hallazgos cosméticos se documentan como trabajo futuro y se ignoran (anti over-engineering). Fuente: *Claude Code best practices (reviewer Callout)*.

---

## 2. Actores, responsabilidades y entregables

| Actor | Quién es | Responsabilidad | Entregables |
|---|---|---|---|
| **Tú (humano)** | Mantenedor | Apruebas planes, abres sesiones, decides sobre gaps, sincronizas git, creas el PR | Decisiones registradas en `registro.json` y aprobaciones en el historial |
| `deuda-verificador` | Subagente (solo lectura) | Confirma/desmiente un tag contra el código real; mapea TODOS los archivos afectados | `docs/deuda/<tag>/verificacion.md` + actualiza `registro.json` |
| `plan-redactor` | Subagente (solo escribe `docs/deuda/**`) | Convierte la verificación en plan ejecutable; valida con fuentes de autoridad; dimensiona fases; redacta prompts y artefactos git/GH | `plan.md`, `progress.json`, `resumen-humano.md` (todo bajo `docs/deuda/<tag>/`) |
| **Sesión ejecutora** | Sesión AISLADA (una por fase) | Ejecuta UNA fase con el prompt del Apéndice A del plan | Código + tests, commit de fase, `docs(progress)` commit, `progress.json` actualizado, Handoff Report |
| `handoff-auditor` | Subagente (contexto fresco) | Verifica plan ↔ realidad tras cada fase | `docs/deuda/<tag>/gaps.md` + veredicto PASS/GAPS + línea en `registro.json` |

**Comandos:** `/nueva-deuda <tag>` · `/verificar-deuda <tags|todos>` · `/auditar-handoff <tag> [fase]`

---

## 3. Anatomía de la memoria

```
docs/deuda/
├── registro.json      ← ÍNDICE global (pequeño): estado de cada tag + enlaces
└── <tag>/             ← carpeta por tag (d2, D1, A3, S2, b1...)
    ├── verificacion.md    ← qué se comprobó y dónde (evidencia archivo:línea)
    ├── plan.md            ← EL CONTRATO + Apéndices A (prompts), B (gaps), C (git/GH) + Fuentes
    ├── progress.json      ← memoria viva de ejecución (fases, current_target, handoffs)
    ├── gaps.md            ← hallazgos del auditor (BLOQUEANTE / OPCIONAL)
    └── resumen-humano.md  ← tu material de aprobación
```

**Ciclo de vida de un tag:** `pending → verificada → plan_aprobado → en_ejecucion → completed → completed-verificado` (o `desmentida`).

---

## 4. Ejemplo completo: saldar el tag `d2`

**Paso 0 — Tú (preparación, 5 min).** Abre `docs/Auditoría Ecotur-ASOPRADO.html`, busca la sección `d2` y léela. Confirmas que entiendes qué deuda describe. (No apruebas nada que no conozcas.)

**Paso 1 — Verificación.** Ejecutas:
```
/nueva-deuda d2
```
El comando orquesta: `deuda-verificador` inspecciona el código → escribe `verificacion.md` → `plan-redactor` redacta `plan.md` + `progress.json` + `resumen-humano.md`. Termina mostrándote el resumen.

**Paso 2 — Tú apruebas (puerta 1).** Lees `resumen-humano.md` y (si tienes dudas) `plan.md` y `verificacion.md`. Revisas especialmente: ¿las fases están bien dimensionadas? ¿el alcance excluye lo que debe excluir? ¿las fuentes citadas tienen URLs reales? Si algo no te convence, pides ajustes en la misma sesión del comando ("cambia la fase C para que no toque X"). Cuando apruebas, dices explícitamente "apruebo el plan".

**Paso 3 — Ejecución por fases (una sesión nueva por fase).** Abres una sesión limpia y pegas el prompt de la Fase A (Apéndice A del plan). Al terminar, te entrega un Handoff Report. TÚ revisas (checklist §6). Si todo bien, abres otra sesión limpia para la Fase B. Repite hasta la última fase.

**Paso 4 — Auditoría entre fases (opcional pero recomendado).** Ejecutas:
```
/auditar-handoff d2
```
Si sale PASS, sigue la siguiente fase. Si hay BLOQUEANTES, ver §7.

**Paso 5 — Cierre.** Con todas las fases en `completed`, ejecutas `/verificar-deuda d2` para la re-auditoría global (¿quedó deuda en rincones?). Luego tú creas el PR hacia `develop` usando el Apéndice C del plan (título, descripción y mensaje de squash ya redactados) y haces el squash merge.

---

## 5. Particularidades NO obvias del flujo (léelas antes de operar)

1. **Cada fase produce DOS commits.** El hash del commit de código es autorreferencial (no puedes escribirlo en un archivo dentro del mismo commit), así que el orden es: commit de fase → actualizar `progress.json` → commit separado `docs(progress): record Fase X completion and advance target to Fase Y`. Es correcto que lo veas así; no es un error.
2. **Los gaps NO van en `registro.json`.** Viven en `gaps.md`. El registro solo recibe el resumen de una línea (`"gaps": "2 bloqueantes en Fase B"`). El registro es un índice, no un diario.
3. **El auditor nunca corrige código.** Su salida termina en el reporte. Si hay BLOQUEANTES, abres TÚ una sesión nueva con el prompt del Apéndice B del plan.
4. **La skill test-sanitizer tiene una puerta de aprobación** ("detente y espera la aprobación del usuario" para formular planes de tests). Esa puerta ya está satisfecha porque el plan aprobado propone los tests: la sesión ejecutora salta directo a validar con Context 7 y ejecutar. Si una sesión se detiene pidiendo aprobación de tests NO contemplados en el plan, es señal de scope creep (ver §7).
5. **En Windows, `agents.md` y `AGENTS.md` son el MISMO archivo** (filesystem case-insensitive). El archivo del repo contiene tanto la identidad/reglas del proyecto como el protocolo del flujo. No intentes crear un AGENTS.md separado.
6. **Los tags son case-sensitive en el informe** (`d1` vs `D1` son cosas distintas) pero las carpetas en Windows no. Si dos tags colisionan por mayúsculas, se usa slug (`deuda-1`, `dup-1`) y se anota en `registro.json`.
7. **`agents.md`, `.agents/` y `.opencode/` están untracked y deben seguirlo** hasta que decidas commitearlos. Las sesiones tienen PROHIBIDO stagearlos (nada de `git add .`).
8. **La configuración de opencode no se recarga en caliente.** Tras crear/editar agentes, comandos o skills: cierra y reinicia opencode, o los cambios no existen.
9. **`/verificar-deuda` es para deuda YA corregida** (b1–b5 y d1 están en `completed` pero sin verificar). `/nueva-deuda` es para deuda PENDIENTE. No las confundas: la segunda produce un plan de ataque; la primera solo re-audita.
10. **Si una fase anterior dejó algo roto, la siguiente fase se DETIENE y te reporta** (está en su ritual de arranque). Es comportamiento correcto: arreglar lo roto antes de avanzar. Ese arreglo se hace con el flujo de gaps, no dentro de la fase nueva.

---

## 6. Checklist del humano (qué haces tú, siempre, y en qué momento)

**Antes de `/nueva-deuda`:** lees la sección del tag en el informe HTML. Si no la entiendes, no arrancas.

**Al recibir el resumen del plan (puerta 1):**
- [ ] Leíste `resumen-humano.md`.
- [ ] Las fases están dimensionadas (≤5 archivos, una termina completa por sesión).
- [ ] El alcance dice qué NO se toca.
- [ ] Las fuentes citadas tienen URLs reales (ábrelas si dudas).
- [ ] Aprobaste explícitamente ("apruebo el plan").

**Tras CADA fase ejecutada (antes de abrir la siguiente sesión):**
- [ ] `git log --oneline -5` muestra el commit de la fase con el mensaje EXACTO del plan + el `docs(progress)`.
- [ ] `git status` solo muestra untracked ajenos (`agents.md`, `.agents/`, `.opencode/`).
- [ ] `docs/deuda/<tag>/progress.json`: tu fase `completed` con hash real, `current_target` avanzado, `last_handoff` redactado.
- [ ] El Handoff Report de la sesión es concreto (archivos, tests, hash), no genérico.
- [ ] (Opcional) `pytest` en verde si quieres verlo con tus ojos.
- Solo entonces: cierras la sesión y abres la siguiente con el prompt de la nueva fase.

**Tras `/auditar-handoff`:**
- [ ] Si PASS → continúa.
- [ ] Si GAPS con `[BLOQUEANTE]` → abre mini-sesión con el prompt del Apéndice B (solo bloqueantes).
- [ ] Si solo `[OPCIONAL]` → copia a Residuales del plan/ADR como trabajo futuro. No abras sesión.

**Al cierre del tag:**
- [ ] `/verificar-deuda <tag>` da "sin residuos" (estado `completed-verificado`).
- [ ] Creas el PR con el Apéndice C y haces squash merge hacia `develop`.
- [ ] Actualizas `registro.json` si algo cambió fuera del flujo normal.

---

## 7. Señales de alarma: cómo detectar resultados no deseados y qué hacer

| Síntoma | Diagnóstico probable | Qué haces |
|---|---|---|
| El commit de fase toca archivos que no están en el plan | Scope creep | Mira `git show --stat <hash>`. Si es grave: pide revertir en mini-sesión o `git revert` tú. Si es menor y justificable, regístralo en `last_handoff` |
| La suite quedó en rojo tras una fase | Trabajo incompleto o commit sin verificar | BLOQUEANTE: abre mini-sesión con Apéndice B. NO abras la siguiente fase |
| `progress.json` sin hash o con `current_target` equivocado | La sesión no cumplió el ritual de salida | No avances. Corrige tú el archivo (cumpliendo `edit_rules`) o pídelo en mini-sesión. Verifica contra `git log` |
| Handoff Report vacío o vago ("todo listo") | Declaración de victoria prematura (fallo documentado de agentes) | No avances. Pide handoff concreto; si insiste, corre `/auditar-handoff` |
| El verificador "desmiente" una deuda que tú ves en el código | Falsa desmentida (greps insuficientes) | Lee `verificacion.md`, señala el archivo:línea que lo contradice y pide re-verificación |
| El plan cita fuentes sin URL o con URLs sospechosas | Citas inventadas | Pide re-citar con enlaces verificables (usa Context 7/websearch). No apruebes |
| La sesión ejecutora se detiene pidiendo aprobación de tests nuevos fuera del plan | Scope creep o plan incompleto | No autorices dentro de la fase. Regresa al plan: si el test era necesario, primero corrije el plan (puerta 1 de nuevo) |
| El auditor repite el mismo gap en la misma fase tras 2 intentos | El plan está mal o la fase mal dimensionada | STOP. Regla de las fuentes: tras dos correcciones fallidas, contexto contaminado. Replantea la fase en el plan (sesión de planificación nueva) y relanza |
| `registro.json` fue editado por alguien que no debía (o quedó incoherente) | Violación de la regla de escritor único | Restaura desde git si está commiteado; cruza estados con `git log` y `progress.json` reales |
| Los comandos `/nueva-deuda` etc. no aparecen | opencode no se reinició tras crear la config | Cierra y abre opencode (la config no es hot-reload) |
| Una sesión pide más contexto del que cabe (empieza a "olvidar" el plan) | Fase demasiado grande | Detén la sesión, commitea lo estable, divide la fase restante en el plan y relanza con la mitad |
| La sesión ejecutora intenta `git add .` o stagear `agents.md`/`.agents/` | Violación del protocolo | Deténla, corrige el staging (`git reset`) y relanza con énfasis en la regla |

---

## 8. FAQ rápido

- **¿Puedo usar el flujo para tags de cualquier letra (d, D, A, S, b)?** Sí. El flujo es categoría-agnóstico; lo que cambia es el contenido del plan. Solo vigila la colisión de mayúsculas en carpetas (§5.6).
- **¿Qué hago si el informe HTML cambia de nombre?** Actualiza el campo `informe` en `registro.json`. El verificador también busca cualquier `.html` de auditoría en `docs/`.
- **¿Puedo saltarme la auditoría entre fases?** Sí, es opcional — pero es la red de seguridad que detecta lo que tú no ves. Recomendada al menos en la primera y última fase de cada tag.
- **¿Quién commitea los archivos del flujo (`docs/deuda/`)?** Las propias sesiones (el `docs(progress)` de cada fase). El commit inicial del tag lo haces tú junto con la aprobación, o lo dejas para el primer `docs(progress)`.
- **¿Y si quiero ejecutar dos tags en paralelo?** No lo hagas en la misma rama: se pisarán los `progress.json` y los commits. Un tag a la vez, o ramas separadas por tag.

---

## 9. Referencias del diseño

- Anthropic Engineering — *Building effective agents* (2024): prompt chaining con gates humanas; evaluator-optimizer.
- Anthropic Engineering — *Effective harnesses for long-running agents* (2025): memoria en archivos, progreso incremental, estado limpio por sesión.
- Anthropic Engineering — *How we built our multi-agent research system* (2025): delegación con objetivo/formato/límites; artefactos en filesystem para evitar el teléfono roto.
- Anthropic — *Claude Code best practices*: explore→plan→code→commit; reviewer en contexto fresco; "flag only gaps that affect correctness"; reinicio de contexto tras correcciones fallidas.
- Conventional Commits 1.0.0 (conventionalcommits.org) y skills locales `commit-author` / `pr-author`.

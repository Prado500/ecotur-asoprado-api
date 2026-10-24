# Flujo de saldado de deuda técnica — Manual del mantenedor

> **Manual completo para humanos** (actores, checklist por etapa, señales de alarma y respuestas): [`MANUAL-FLUJO.md`](MANUAL-FLUJO.md)

Este flujo convierte cada tag de la auditoría (`d2`, `D1`, `A3`, `S2`, `b1`...) en un plan de ataque aprobado por ti y ejecutado por sesiones aisladas, con memoria en archivos.

## Actores

| Actor | Qué es | Archivo |
|---|---|---|
| `deuda-verificador` | Confirma o desmiente la deuda de un tag contra el código real | `.opencode/agent/deuda-verificador.md` |
| `plan-redactor` | Redacta el plan + prompts de sesión + artefactos git/GH | `.opencode/agent/plan-redactor.md` |
| `handoff-auditor` | Audita en contexto fresco cada fase ejecutada | `.opencode/agent/handoff-auditor.md` |
| Sesiones aisladas | Ejecutan UNA fase cada una (prompt del Apéndice A del plan) | no son agentes definidos: son sesiones nuevas |
| Tú | Apruebas planes, abres sesiones, corriges gaps bloqueantes | — |

## Comandos

- `/nueva-deuda d2` — verifica el tag y redacta el plan para tu aprobación.
- `/verificar-deuda b1 b2` o `/verificar-deuda todos` — re-audita deuda ya corregida buscando residuos en rincones.
- `/auditar-handoff d2` (o `d2 B`) — audita el handoff de la última fase (o de la fase B).

## Memoria en archivos

```
docs/deuda/
├── registro.json     ← ÍNDICE global: estado de cada tag (pequeño, siempre legible)
└── <tag>/            ← carpeta por tag
    ├── verificacion.md   ← veredicto del verificador + evidencia archivo:línea
    ├── plan.md           ← el contrato + apéndices (prompts, mensajes git, fuentes)
    ├── progress.json     ← estado de ejecución (fases, current_target, handoffs)
    ├── gaps.md           ← hallazgos del auditor (BLOQUEANTE / OPCIONAL)
    └── resumen-humano.md ← material de aprobación para ti
```

## Ciclo de vida de un tag

`pending → verificada → plan_aprobado → en_ejecucion → completed → completed-verificado`
(también `desmentida` si la deuda ya no existe)

## Transición entre fases (dónde vive el estado)

1. Solo la sesión que ejecuta la fase X escribe la entrada de la fase X en `progress.json` (regla de escritor único).
2. Al salir: fase → `completed` + hash real del commit, `current_target` → siguiente fase, `last_handoff` redactado.
3. El commit de progreso va SEPARADO del commit de código (el hash del commit de fase es autorreferencial): primero el commit de la fase, luego actualiza `progress.json` y commitea `docs(progress): ...`.
4. Entre fases, TU checklist: commit correcto → `progress.json` coherente → árbol limpio (solo untracked ajenos) → recién abrir la siguiente sesión.

## Gaps (auditoría entre fases)

- El auditor escribe `gaps.md` con hallazgos `[BLOQUEANTE]` / `[OPCIONAL]` y evidencia.
- BLOQUEANTE → abres una sesión aislada de corrección con el prompt del Apéndice B del plan.
- Solo OPCIONAL → se documentan en Residuales del plan / ADR como trabajo futuro. No se persiguen (anti over-engineering).
- El `registro.json` solo recibe el resumen de una línea (ej. `"gaps": "2 bloqueantes en Fase B"`).

## Reglas que toda sesión debe respetar (también en AGENTS.md)

- Prohibido `git add .` / `git add -A`; nunca stagear `agents.md` ni `.agents/` (untracked ajenos).
- Prohibido `git pull`, `git merge`, `git push` o cambiar de rama (el humano sincroniza).
- Commits atómicos en Conventional Commits; nunca commitear con la suite en rojo.
- `progress.json` solo se edita en los campos permitidos por su `edit_rules`.

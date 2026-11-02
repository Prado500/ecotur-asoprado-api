---
description: Ejecuta UNA fase de un plan aprobado con contexto fresco, compuerta y commit. Uso: /implementar BE-01 A
argument-hint: <ID> <Fase>
---

Argumentos: `$ARGUMENTS` (ID y letra de fase). Precondiciones: `docs/deuda/<ID>/plan.md` existe y yo (David, el
humano) lo aprobé explícitamente en la sesión de `/deuda-planear`; `progress.json` tiene `current_target` en esa fase. Si existe `docs/deuda/<ID>/gaps.md` con
hallazgos [BLOQUEANTE] para esa fase, el alcance es ESTRICTAMENTE resolver esos bloqueantes.

Usa el subagente `fase-ejecutor` con la instrucción: "Implementa la fase <Fase> del plan
`docs/deuda/<ID>/plan.md` según tu protocolo completo (ritual de arranque, TDD, compuerta, commit exacto,
progress.json, handoff)".

Cuando termine, muéstrame el handoff resumido y el `git diff --stat` del commit. Después de eso, mi
siguiente paso será `/auditar <ID> <Fase>`.

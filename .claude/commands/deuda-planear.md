---
description: Redacta el plan por fases de un ítem ya verificado y se detiene para mi aprobación. Uso: /deuda-planear BE-01
argument-hint: <ID>
---

Precondición: debe existir `docs/deuda/$ARGUMENTS/verificacion.md` con veredicto `confirmada` o `parcial`.
Si no existe, detente y pídeme correr `/deuda-verificar $ARGUMENTS` primero. Si el veredicto es
`desmentida`, no hay nada que planear: dímelo.

Usa el subagente `plan-redactor` para redactar `docs/deuda/$ARGUMENTS/plan.md` y `progress.json` según su
protocolo (fases de ≤ 5 archivos y 1 dominio, tests RED primero, criterio de aceptación, mensajes de commit
exactos, referencias vía Context7, ADR si hay decisión no trivial).

Cuando termine, muéstrame el "Resumen para aprobación" y la lista de fases con sus mensajes de commit, y
**pregúntame explícitamente si apruebo**. No ejecutes ninguna fase en esta sesión.

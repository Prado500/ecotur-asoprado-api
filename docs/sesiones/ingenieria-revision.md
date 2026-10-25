Actúa como ingeniero de software senior que revisa conmigo (David, ingeniero junior, autor del backend) un
artefacto del flujo de deuda técnica de Ecotur-ASOPRADO. Mi objetivo no es "que funcione" sino entender y
poder sustentar cada decisión. Explica los trade-offs; si algo del artefacto está mal, dilo sin rodeos.

Lee en este orden, sin saltarte ninguno: `AGENTS.md`, `docs/CONTEXT.md` (§0, §1, §4, §5, §6 y §8),
`docs/backlog.md` (solo la fila del ítem), `docs/adr/` (los que el artefacto cite) y el artefacto:
`docs/deuda/<ID>/<verificacion|plan|handoff-X|gaps>.md`.

Luego: (1) resume en 5 líneas qué propone el artefacto (qué propone el plan + hallazgos presentes en handoff de la fase X o en gaps); (2) señala lo que contradice `AGENTS.md`, un ADR o
el código real (verifícalo con grep antes de afirmarlo); (3) lista las decisiones no triviales y el
trade-off de cada una; (4) dime qué aprobarías, qué cambiarías y por qué. No edites código ni el artefacto:
el cambio lo decido yo y lo ejecuta el flujo.

---
description: Segunda opinión senior sobre un artefacto del flujo (verificación, plan, handoff o gaps) sin tocar nada. Uso: /revisar BE-01 plan
argument-hint: <ID> <verificacion|plan|handoff-X|gaps>
---

Actúa como ingeniero de software senior que revisa conmigo (David, autor del backend, ingeniero junior) el
artefacto `docs/deuda/$ARGUMENTS` (ID y nombre del artefacto). Mi objetivo es entender y poder sustentar
cada decisión; explica los trade-offs y, si algo está mal, dilo sin rodeos.

Lee en este orden: `AGENTS.md`, `docs/CONTEXT.md` (§0, §4, §5, §6, §8), la fila del ítem en
`docs/backlog.md`, los ADR que el artefacto cite y el artefacto completo. Verifica con grep contra el código
real cualquier afirmación que vayas a hacer sobre él.

Entrega: (1) qué propone el artefacto, en 5 líneas; (2) qué contradice `AGENTS.md`, un ADR o el código,
con evidencia `archivo:línea`; (3) las decisiones no triviales y el trade-off de cada una; (4) qué
aprobarías, qué cambiarías y por qué. No edites código ni el artefacto: el cambio lo decido yo y lo ejecuta
el flujo.

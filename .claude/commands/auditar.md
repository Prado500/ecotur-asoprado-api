---
description: Audita con contexto fresco la fase ejecutada de un plan (plan ↔ diff ↔ compuerta). Uso: /auditar BE-01 A
argument-hint: <ID> [Fase]
---

Usa el subagente `handoff-auditor` para auditar `$ARGUMENTS` según su protocolo: re-ejecutar la compuerta,
contrastar el commit contra el plan, verificar `progress.json`, y escribir `docs/deuda/<ID>/gaps.md`.

Cuando termine, muéstrame el veredicto (PASS o GAPS), la salida literal del RESUMEN de la compuerta y la
lista de hallazgos. Si hay bloqueantes, recuérdame que el siguiente paso es `/implementar <ID> <Fase>` con
`gaps.md` como alcance. No corrijas código en esta sesión.

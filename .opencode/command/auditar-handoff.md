---
description: Audita el handoff de un plan de deuda técnica ejecutado (o de una fase concreta) con contexto fresco. Uso: /auditar-handoff d2 | /auditar-handoff d2 B
agent: handoff-auditor
---

Audita el handoff del tag "$ARGUMENTS" según tu protocolo. Si se indica una fase (segundo argumento), audita esa fase; si no, la última fase registrada en docs/deuda/<tag>/progress.json. Entrega: veredicto PASS/GAPS, evidencia (pytest, git status, git log), gaps.md actualizado y registro.json actualizado. No corrijas código.

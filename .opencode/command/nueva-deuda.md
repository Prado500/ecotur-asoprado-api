---
description: Prepara un tag de deuda técnica de la auditoría: lo verifica contra el código y redacta el plan para tu aprobación. Uso: /nueva-deuda d2
subtask: true
---

Vas a orquestar la preparación del tag "$ARGUMENTS" de la auditoría de deuda técnica (busca el informe .html dentro de docs/). NO escribas código de aplicación ni modifiques nada fuera de docs/deuda/. El plan NO se ejecuta en esta sesión.

Paso 0 — Verificación previa: si docs/deuda/<tag>/verificacion.md YA existe con veredicto "confirmada" o "parcial" (y docs/deuda/registro.json tiene ese tag en estado "verificada"), NO invoques al deuda-verificador: pasa directo al Paso 2 (plan-redactor), que consume ese artefacto (verificacion.md) y lo contrasta contra el código en su Procedimiento. Solo verifica desde cero cuando el artefacto no exista o esté desactualizado.

Paso 1 — Verificación: invoca el subagente `deuda-verificador` (herramienta task) con la tarea: "Verifica el tag $ARGUMENTS según tu protocolo: lee la sección correspondiente del informe de auditoría en docs/, inspecciona el código real, corre el baseline de pytest, escribe docs/deuda/$ARGUMENTS/verificacion.md y actualiza docs/deuda/registro.json."

Paso 2 — Planificación: con el verificacion.md resultante, invoca el subagente `plan-redactor` con la tarea: "Redacta el plan de ataque completo para el tag $ARGUMENTS usando docs/deuda/$ARGUMENTS/verificacion.md. Entrega plan.md, progress.json y resumen-humano.md bajo docs/deuda/$ARGUMENTS/, con prompts de sesión por fase, artefactos git/GH (Apéndice C) y fuentes de autoridad citadas con enlaces verificables."

Paso 3 — Entrega: muestra en tu respuesta final el contenido de docs/deuda/$ARGUMENTS/resumen-humano.md y pide al usuario su aprobación explícita ANTES de ejecutar cualquier fase. Cuando el usuario APRUEBE el plan, actualiza docs/deuda/registro.json: estado del tag → "plan_aprobado" (la nota puede registrar la fecha de aprobación). Si el tag no existe en el informe, detente y repórtalo sin inventar.

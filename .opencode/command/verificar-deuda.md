---
description: Re-verifica que deuda o bloqueos ya marcados como corregidos no tengan residuos en rincones del código. Uso: /verificar-deuda b1 b2 | /verificar-deuda todos
agent: deuda-verificador
---

Ejecuta tu "Modo re-auditoría" (especificado en tu propio prompt de agente) sobre los tags listados: $ARGUMENTS

- Si "$ARGUMENTS" es "todos": lee docs/deuda/registro.json y re-audita TODOS los tags con estado "completed".
- Para cada tag: preservación del artefacto existente (append de sección fechada, prohibido borrar o reescribir secciones previas), re-ejecución de los patrones de detección documentados + greps globales de rincones, pytest, creación con la plantilla estándar si el artefacto no existe, y actualización de registro.json (completed-verificado | verificada con residuos).
- No edites código. Termina con un reporte por tag: sin residuos / con residuos + evidencia.

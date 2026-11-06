---
description: Verifica o desmiente un ítem de deuda contra todo el repo y deja docs/deuda/<ID>/verificacion.md. Uso: /deuda-verificar BE-01
argument-hint: <ID>
---

Usa el subagente `deuda-verificador` para verificar el ítem `$ARGUMENTS` según su protocolo: lee su
descripción en `docs/backlog.md` (y la sección del informe de auditoría si es un tag), busca el patrón en
TODO el repo antes de emitir veredicto, corre `./venv/Scripts/python.exe scripts/check.py` 
(en POSIX `./venv/bin/python`; AGENTS §6) como línea base y escribe `docs/deuda/$ARGUMENTS/verificacion.md`.

Cuando termine, muéstrame: veredicto, mapa de ficheros, línea base y "Conclusión para el planificador".
No planifiques ni modifiques código en esta sesión.

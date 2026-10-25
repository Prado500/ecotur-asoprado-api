# ADR-0005 — Trinquete de calidad: criterio de aceptación relativo a la línea base mientras la compuerta global esté en rojo

- **Estado:** propuesto (redactado por Claude el 25 oct; pendiente de revisión y aceptación por David)
- **Ubicación en el repo:** `docs/adr/0005-trinquete-de-calidad-contra-la-linea-base.md`
- **Relación:** complementa ADR-0001 (determinismo por herramientas). **Caduca** cuando `python scripts/check.py`
  pase completo en `develop`; entonces el criterio vuelve a ser "compuerta en verde" y este ADR se marca superado.

## Decisión (resumen)

Hasta que la compuerta global esté en verde, una fase del flujo se acepta si **no empeora nada y mejora lo
que toca**: pytest en verde; cobertura y contratos de `import-linter` KEPT nunca por debajo de la línea
base registrada en `docs/deuda/<ID>/verificacion.md`; cero errores de `ruff` y `mypy` en los archivos
tocados; totales de `ruff`/`mypy` que no crecen. El rojo heredado en archivos no tocados no bloquea.

## Contexto

- La línea base del 24 oct (PLAN §6) tiene 4 de 5 pasos de la compuerta en rojo por deuda heredada
  (531 avisos de ruff, 44 errores de mypy, 1 contrato roto) y pytest en verde (116 tests, 89 %).
- El `fase-ejecutor` exigía compuerta en verde antes de arrancar y al salir. Con la línea base actual
  no habría podido ejecutar ninguna fase: el flujo estaba bloqueado por su propia regla.
- La alternativa de "primero dejar todo en verde y después trabajar" posterga el valor de negocio
  (reservas, pagos) varios días en un plan de 15.

## Alternativas consideradas

1. **Compuerta global en verde como requisito previo.** Descartada por el calendario; además, mezclar la
   limpieza masiva con las correcciones de deuda haría ilegibles los PR.
2. **Ignorar ruff/mypy hasta el final.** Descartada: sin trinquete, cada fase podría añadir deuda nueva y
   nadie lo vería hasta el final.
3. **Trinquete contra la línea base (elegida).** Es la práctica habitual al introducir herramientas de
   calidad en código existente: se congela el estado actual y solo se permite mejorar.

## Consecuencias

- Cada verificación debe registrar la línea base completa (ya lo exige `deuda-verificador`).
- El ejecutor y el auditor comparan contra esa línea base; el auditor marca BLOQUEANTE cualquier retroceso.
- Riesgo aceptado: dos fases concurrentes con líneas base distintas; mitigación: una sola deuda en curso
  a la vez (como ya hace el flujo).
- Caducidad: tras el commit mecánico de `ruff --fix` y la corrección de mypy (PLAN día 4–5), se vuelve al
  criterio absoluto y este ADR se supersede.

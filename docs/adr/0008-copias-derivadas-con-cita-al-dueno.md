# ADR-0008 — Copias derivadas de un hecho: cada hecho duro una vez por documento, con cita al dueño, verificadas por `scripts/check_docs.py`

- **Estado:** aceptado
- **Propuesta:** sesión Mentor (29 oct 2026), a partir del diagnóstico de la sesión del 28 y de las observaciones de
  David · **Aprobada:** David (30 oct 2026), con diez ajustes de redacción sobre el borrador de la bitácora del 29
  (dudas 1–10 de la bitácora del 30).
- **Fecha de propuesta de la decisión:** 2026-10-29 · **Fecha de aceptación y registro:** 2026-10-30
- **Ubicación en el repo:** `docs/adr/0008-copias-derivadas-con-cita-al-dueno.md`
- **Relación:** CONTEXT §0 (dueño del mapa hecho → dueño); ADR-0007 (versionado); ADR-0001 (determinismo por
  herramientas, que este ADR aplica a la documentación); README de sesiones, ritual de cierre paso 3;
  bitácoras 2026-10-26 (bloques), 2026-10-28 (numeral 3), 2026-10-29 (decisión), 2026-10-30 (aceptación).

## Contexto

- Regla vigente desde el 23 oct (CONTEXT §0): un hecho tiene un solo dueño; los demás documentos lo enlazan.
  En seis días divergieron tres veces copias hechas con buena intención: 56 días copiados en el backlog (26 oct),
  cinco copias del deadline en PLAN de las que cuatro quedaron viejas tras la prórroga (27–28 oct), y PLAN §5
  describiendo un flujo agéntico que ya no existe (`make check`, 4 comandos).
- Causas (bitácora del 28, numeral 3): el mapa de dueños vivía en dos sitios en prosa (CONTEXT §0 por documento;
  README paso 3 por tipo de hecho) y a grano demasiado grueso; `check_docs.py` verificaba el síntoma
  (`rule_no_days` solo en backlog y CONTEXT) y no el principio; ninguna regla decía cuántas copias se permiten.
- Dos propuestas en tensión (28 y 29 oct): "una copia por documento, nunca en títulos" hace ilegible un plan
  que no puede decir su fecha; "n copias resumidas con cita" más reglas de lectura y escritura en prosa repite
  la estrategia que ADR-0001 descartó para el flujo (determinismo pidiéndoselo a un LLM).
- Markdown en GitHub no tiene transclusión (DITA `conref`, Sphinx `include`); DRY aplicado a documentación
  (Hunt y Thomas, *The Pragmatic Programmer*) exige entonces o enlazar sin repetir, o permitir copias derivadas
  verificables.

## Decisión

1. **Se distingue hecho duro de explicación.** Un hecho duro (fecha, número, nombre de bloque, versión, estado,
   nombre de persona o rol) aparece **a lo sumo una vez por documento**, nunca en un título, siempre con cita al
   dueño; la regla es por hecho, así que un documento puede citar varios hechos duros distintos, cada uno una vez.
   Una explicación (qué es el modelo de reservas, qué compromete la propuesta, qué hace el flujo) puede
   resumirse **donde el documento la necesite para cumplir su función**, con cita al dueño, y sin hechos duros
   dentro del resumen salvo los que ya se hayan citado una vez.
2. **Un documento vivo conserva lo que depende de, no lo que explica.** Prueba para decidir si una sección se
   queda: ¿el documento cambiaría si ese hecho cambiara? Si no, es un puntero de una línea.
3. **La cita tiene forma fija** para que `scripts/check_docs.py` la encuentre: `(CONTEXT §N)`, `(PLAN §N)`,
   `(backlog ID)`, `(ADR-NNNN)`, `(AGENTS §N)`, `(README de sesiones)`, `(bitácora AAAA-MM-DD)`,
   `(docs/deuda/ID/)`. Una copia sin cita es un hallazgo de `check_docs.py`, tenga o no su hecho un dueño
   registrado en CONTEXT §0. Si la copia sin cita apunta a un dueño registrado, el hallazgo se resuelve añadiendo
   la cita y corrigiendo la copia hacia el dueño; si la copia sin cita no apunta a ningún dueño registrado, no se
   resuelve inventando una cita: se determina el dueño (criterio del punto 5: el documento que
   cambiaría si cambiara la información de la copia huérfana) y se añade la fila en el mapa hecho -> dueño ese día.
4. **Si copia y dueño divergen, gana el dueño.** La copia se corrige hacia el dueño. Si quien lo nota cree que la
   copia es la correcta o más reciente, no corrige: lo anota en la bitácora del día y pregunta a David.
5. **El mapa hecho → dueño vive solo en CONTEXT §0** y crece por incidente: cuando aparece una divergencia sobre
   información cuyo dueño no está registrado en la tabla, se determina quién es o debería ser el dueño (criterio:
   el documento que cambiaría si el hecho cambiara; si serían dos, se consulta a David) y se añade la fila ese
   día. No se enumeran granos por anticipado. Esas divergencias no las encuentra la pasada del punto 6 (que parte
   de dueños ya registrados): aparecen al leer (apertura de una sesión, revisiones de David), por la regla "hecho
   duro sin cita" del punto 3, o al ir a consignar un hecho y no encontrar su fila; en los tres casos la fila se
   crea en ese momento.
6. **Verificación: una pasada acotada en el cierre, no una regla de lectura.** Paso 3 del ritual de cierre: por
   cada archivo dueño que cambió hoy (`git log --since`), `scripts/check_docs.py` lista sus citas en los demás
   documentos y la sesión revisa esas copias. Las que tienen carga verificable las compara la herramienta: días
   fuera de PLAN §3; fecha de entrega en PLAN ≠ CONTEXT §2; bloque citado no definido en PLAN §2b; encabezado de
   versión anterior al último commit del archivo (ADR-0007); fila de PLAN §3 con fecha anterior a hoy y sin marca
   en su columna `Cierre` (`✔ DD` / `◐ DD` / `✘ DD`, DD = la bitácora que lo cuenta). **Hasta que esas reglas
   existan en `check_docs.py`, la sesión que ejecuta el ritual de cierre hace la pasada con `grep`**
   (`grep -n "(CONTEXT §2)" docs/*.md docs/sesiones/*.md`, una vez por dueño tocado) y revisa cada copia que
   salga; nada de esto recae en David salvo la decisión del punto 4.
7. **Alcance:** los documentos vivos de CONTEXT §0 y `docs/sesiones/`. **No aplica** a ADR ni bitácoras: son
   fechados e inmutables, y un hecho viejo en ellos es historia, no divergencia.

## Alternativas consideradas

- **Solo punteros, sin copias.** Descartada: un plan que no dice su fecha ni su alcance obliga a abrir cuatro
  archivos para leerlo, y las sesiones de ingeniería con contexto fresco pagan ese coste en cada fase.
- **Una copia por documento, sin distinguir dato de explicación** (propuesta del 28). Descartada: trata igual
  una fecha y un resumen; prohíbe el resumen útil y permite la fecha repetida en el título.
- **n copias con reglas fuertes de lectura y escritura en prosa** (propuesta de David, 29 oct). Descartada en la
  envoltura, conservada en el núcleo (la cita): una regla "siempre compara con el dueño" sin exit code se
  cumple la mayoría de las veces, y convierte cada fase de ingeniería en una auditoría documental.
- **Mapa de dueños como skill de Claude Code o como segundo documento.** Descartada: sería una copia más del
  mapa, invisible para las sesiones Mentor y Documento.

## Consecuencias

- Positivas: PLAN v2.0 se lee solo y pesa menos; "¿quién es dueño de X?" tiene una respuesta buscable; las
  copias son greppables; la verificación es diaria, acotada a lo tocado y mayormente mecánica.
- Negativas / aceptadas: una copia puede divergir entre dos cierres (el dueño se actualiza a media mañana y la
  copia espera al cierre; la atrapa el punto 6 de la Decisión en el siguiente ritual); CONTEXT §0 pasa de 5 a
  ~18 filas; un marcador de cierre en PLAN §3 es una copia consciente del "hecho / no hecho" de la bitácora,
  permitida porque mide el avance del plan y porque `check_docs.py` la verifica (regla "fila cerrada sin marca",
  punto 6). Las reglas mecánicas del punto 6 son trabajo de flujo en un bloque por definir en PLAN v2.0 §2b;
  este ADR no se edita cuando el bloque reciba nombre (la bitácora de ese día lo dirá).
- Para el documento de grado: este ADR, el numeral 3 de la bitácora del 28 y la bitácora del 29 son un caso de
  evaluator-optimizer con revisión humana aplicado a la gestión documental del proyecto (cap. de metodología).

## Fuentes

- Hunt, A. y Thomas, D., *The Pragmatic Programmer* (DRY: "every piece of knowledge must have a single,
  unambiguous, authoritative representation within a system").
- Anthropic, *Building effective agents* (patrón evaluator-optimizer), citado en ADR-0001.

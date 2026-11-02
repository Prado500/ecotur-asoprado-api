# ADR-0009 — Addenda a ADR aceptados: qué son, qué pueden cambiar y cuándo son un ADR nuevo

- **Estado:** aceptado
- **Propuesta:** David (condición puesta el 30 oct al aceptar el primer addendum) · **Aprobada:** David (1 nov 2026)
- **Fecha de la decisión:** 2026-11-01 · **Fecha de registro:** 2026-11-01
- **Ubicación en el repo:** `docs/adr/0009-addenda-a-adr-aceptados.md`
- **Relación:** `docs/CONTEXT.md` §0 (regla operativa; este ADR posee la decisión) · ADR-0008 (los dos addenda que
  motivan la regla, 30 oct y 1 nov) · bitácoras `2026-10-30` (condición) y `2026-11-01` (segundo uso).

## Contexto

El 30 oct se decidió, como frase en CONTEXT §0 y no como ADR, que un ADR aceptado no se edita: se supersede o recibe
un addendum fechado. La condición de esa decisión fue explícita: "si el addendum se usa una segunda vez, ese día se
escribe el ADR que la formalice". El segundo uso es hoy (ADR-0008, addendum del 1 nov: cómo se cumple su punto 6 tras
AF-01). Una regla usada dos veces sin ADR es una convención que vive en la memoria de quien la aplicó.

## Decisión

1. **Un addendum es una sección fechada y firmada al final del ADR** (`## Addendum — D mmm AAAA (quién)`), que cita la
   bitácora del día. El texto anterior del ADR no se toca; si un punto y el addendum difieren, rige el addendum.
2. **Puede:** aclarar un punto ambiguo; corregir una omisión; afinar un criterio; decir **cómo** se cumple un punto
   (mecanismo, herramienta, momento) sin alterar **qué** se decidió.
3. **No puede:** cambiar la decisión; borrar o invertir un punto; ampliar el alcance a casos que el ADR no cubría;
   contradecir otro ADR. Cualquiera de esas cosas es un ADR nuevo que supersede al anterior (estado "superseded por
   ADR-NNNN" en el viejo).
4. **Señal de alarma:** un ADR con tres addenda es un ADR cuya decisión probablemente cambió; el tercero obliga a
   revisar si procede superseder antes de escribirlo.
5. La bitácora del día menciona el addendum; el ADR lo posee. CONTEXT §0 conserva la frase operativa citando este ADR.

## Alternativas consideradas

- **Editar el ADR en sitio.** Rechazada: rompe la inmutabilidad que hace citable a un ADR (una cita a "ADR-0008 punto 6"
  tiene que significar siempre lo mismo).
- **Un ADR nuevo por cada afinamiento.** Rechazada: multiplica documentos cortos que superseden sin cambiar nada de
  fondo; el lector pierde el hilo de la decisión.

## Consecuencias

- Las sesiones pueden afinar un ADR el mismo día de aplicarlo sin reabrir la decisión (es lo que pasó dos veces con
  ADR-0008), con un formato fijo que `scripts/check_docs.py` podría verificar más adelante (encabezado y cita a la bitácora).
- Coste: distinguir "cómo" de "qué" exige juicio; en caso de duda, es ADR nuevo.

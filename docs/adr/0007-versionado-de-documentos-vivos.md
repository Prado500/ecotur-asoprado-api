# ADR-0007 — Versionado de los documentos vivos: la versión es del archivo, no de una sección

- **Estado:** aceptado
- **Propuesta:** David a partir de un hallazgo de Claude · **Aprobada:** David (28 oct 2026)
- **Fecha de la decisión:** 2026-10-28 · **Fecha de registro:** 2026-10-28
- **Ubicación en el repo:** `docs/adr/0007-versionado-de-documentos-vivos.md`
- **Relación:** `docs/CONTEXT.md` §0 (dueño de la regla operativa; este ADR posee la decisión) · `docs/sesiones/README.md`
  (ritual de cierre, paso 3) · bitácora `2026-10-28` (hallazgos que la motivaron).

## Contexto

- `PLAN.md` llevaba en su encabezado la secuencia v1 → v1.4 → v1.5 → v1.6 → v1.7 → v2.0, que unas veces contaba
  cambios del **archivo** (v1: original; v1.5: nace §2b) y otras cambios de la **sección §3** (v1.4 y v1.6:
  deslizamientos de un día). La bitácora del 27 oct afirma que PLAN pasó a v1.7; esa versión nunca se escribió
  (`git log -- docs/PLAN.md`). "Cronograma v2.0" (PLAN) y "PLAN v2.0: §1, §2b, §3, §7" (CONTEXT §8) nombraban cosas
  distintas con el mismo número.
- `CONTEXT.md` y `backlog.md` sí se versionan como archivos, pero sus encabezados (2.8 — 26 oct; 1.7 — 26 oct) no se
  actualizaron cuando ambos cambiaron el 27 oct (commit `3bc65ac`). CONTEXT llevaba además sellos de fecha por
  sección ("estado al 24 oct", "estado al 26 oct", "actualizado 27 oct") que divergían entre sí y del encabezado.
- Los prompts de `docs/sesiones/` y su README no llevan versión.
- Hallazgo de David (28 oct): un lector humano no puede saber si "v1.6" es la versión del cronograma o la del fichero.

## Decisión

1. **La unidad versionada es el archivo.** Las secciones no tienen versión ni fecha de revisión propia. Las fechas
   que aparecen dentro del texto son fechas de **hechos** (cuándo pasó algo), nunca de revisión.
2. **Alcance:** los documentos vivos según CONTEXT §0 — `CONTEXT.md`, `PLAN.md`, `backlog.md` — y los artefactos de
   `docs/sesiones/` (README y prompts). **No aplica** a los ADR (inmutables; su línea de estado es su versión), a las
   bitácoras (append-only) ni a código, agentes y scripts (`.claude/`, `scripts/`), cuya versión es git.
3. **Forma del encabezado:** una línea `**Versión X.Y — D mmm AAAA.**` seguida **solo** de las referencias a las
   bitácoras donde se decidieron los cambios de esa versión. La historia no se narra en el encabezado: su dueño es la
   bitácora.
4. **Incremento:** **mayor** (X.0) cuando cambia una premisa que el lector daba por supuesta (deadline, alcance D3,
   capacidad, roles, reglas de un ritual); **menor** (X.Y) cuando cambia el contenido sin cambiar premisas
   (deslizamiento, bloque nuevo, filas del backlog, redacción de un prompt). Se incrementa **una vez por día de
   cambios** (es decir, solo se aumenta de versión menor y/o mayor si en determinado día ocurren modificaciones que sean motivo
   para el incremento de versión en los documentos vivos), en el paso 3 del ritual de cierre, sin importar cuántas secciones cambiaron. Analogía deliberada con
   SemVer: mayor = rompe lo que el lector asumía; menor = compatible con lo que asumía.
5. Los archivos del alcance que hoy no llevan versión nacen como **1.0** la primera vez que se modifiquen después de
   este ADR, con la referencia a la bitácora de ese día. Mientras no se toquen, no se les añade nada.

## Alternativas consideradas

- **Versionar el cronograma aparte** (un "v-cronograma" dentro de PLAN). Descartada: una sección no tiene identidad en
  git (`git log -- docs/PLAN.md` existe; `git log -- "PLAN.md §3"` no), y el cambio de deadline movió §1, §2b, §3 y §7
  a la vez, dejando sin significado a "versión del cronograma".
- **Sin versión manual; solo git.** Descartada: el número corto es la forma en que bitácoras y CONTEXT se refieren a un
  estado del plan ("v1.6") sin hashes, y CONTEXT ya lo hacía bien.
- **Changelog al pie de cada archivo.** Descartada: duplicaría la bitácora, dueña de lo que pasó cada día.

## Consecuencias

- **Positivas:** una sola semántica de versión para los documentos vivos; el encabezado deja de acumular historia;
  una referencia como "PLAN v2.0" significa una sola cosa.
- **Negativas / aceptadas:** se pierde la pista visual "esta sección es vieja" (que en 3 de 4 casos estaba
  equivocada); exige disciplina en el cierre. Mitigación mecánica posible: `scripts/check_docs.py` comprueba que la
  fecha del encabezado no sea anterior al último commit del archivo. Pendiente de flujo, no hoy.
- **Correcciones aplicadas el 28 oct:** encabezado de `PLAN.md` reescrito en la forma nueva, conservando **v1.6** como
  última versión real y marcada como superada; regla operativa en CONTEXT §0 y fila en §6; fe de erratas de la "v1.7"
  en la bitácora del 28. El ADR de pagos tomará **el siguiente número libre** (CONTEXT §6 decía "0007").

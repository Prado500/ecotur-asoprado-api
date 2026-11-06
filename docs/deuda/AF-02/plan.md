# PLAN — AF-02: Corregir la lectura de `--estado` y las fechas de R6 y R7 en `check_docs.py`

> Fuente: `docs/deuda/AF-02/verificacion.md` (parcial) y su adenda de siete puntos (6 nov, 15:55), que prevalece sobre la
> fila del backlog y sobre la conclusión. Base develop: `e4e7d43`. Redactado sobre `2644f72`.
> Estado: **aprobado por David (6 nov 2026, 16:50; E0 en "Enmiendas aprobadas"). P1 = B1 (desfase fijo −5 h, stdlib).**

## Resumen para aprobación

Dos fases, una por punto, en `scripts/check_docs.py` y `tests/test_check_docs.py`. **A (punto 3):** `--estado` deja de
mirar la última línea de `gaps.md` y lee el veredicto del último bloque `## Auditoría Fase`, con los seis formatos reales y
la línea de contrato; sin veredicto imprime `sin veredicto`, vacío o no UTF-8 imprime `ilegible`, y nunca lanza traceback.
Los 9 `gaps.md` reales pasan a `PASS` (hoy 4 son falsos "con gaps"). **B (puntos 2 y 2b):** cada fila de PLAN §3 toma el año
más cercano a la línea de versión, y R6 y R7 comparan días en el huso del proyecto. La suite pasa de 438 a 547 casos; la
compuerta sigue en rojo con los mismos 14 errores heredados.
**Riesgo principal:** la cobertura no mide `scripts/`, así que la compuerta no delataría un test ausente. Cada fase lo
demuestra con mutantes sobre una copia desechable: 16 en A y 15 en B, todos muertos en la sonda.
**Cambio visible en B:** con los mismos datos, `--cierre` pasa de 3 errores R6 a 2. El de `docs/CONTEXT.md` era falso
(`d7de2d6`, fecha UTC). No es una regresión ni un cierre adelantado; los de PLAN y backlog siguen hasta el cierre.
**No se toca:** `app/`, `.claude/`, `.opencode/`, `AGENTS.md`, `gaps.md` existentes, `read_progress`, `pyproject.toml` (salvo
que P1 elija la opción B2), puntos 1 y 5, "punto 6", `reconfigure`. Sin ADR.

**Preguntas para David**

- **P1 (bloquea B). `America/Bogota` no funciona con `zoneinfo` solo en este venv.** Medido: `ZoneInfo("America/Bogota")`
  lanza `ZoneInfoNotFoundError`, `TZPATH` vacío, 0 husos disponibles, `tzdata` ni instalado ni en `pyproject.toml`. La
  adenda 5 (`zoneinfo`, stdlib) y la fila ("Stdlib") no se cumplen a la vez en Windows.
  - **B1, desfase fijo (recomendada):** `timezone(timedelta(hours=-5), "America/Bogota")`. Solo stdlib, nada que instalar,
    mismo resultado en Windows y en CI. Medido contra la base IANA: 0 diferencias en las 324 336 horas de 1994 a 2030.
    Coste: se aparta de la letra `zoneinfo`, y si Colombia cambiara de huso habría que editar esa línea.
  - **B2, `tzdata` en el extra `dev`:** cumple la letra, pero es una dependencia nueva (AGENTS §2; wheel 2026.6, 348 KB) y
    añade `pyproject.toml` a la fase. David la instala en el venv antes de B. Sin ella, `--cierre` lanza traceback y 14
    tests fallan (medido); con el wheel en `PYTHONPATH`, 257 verdes (medido).
  - Descartada: `zoneinfo` con el desfase como respaldo; dos caminos, y cada sistema solo probaría uno.
- **P2 (no bloquea). ¿Añadir `OSError` a `read_progress`?** Un `progress.json` que no se puede abrir sigue dando traceback y
  exit 1 (medido con un directorio). Por la adenda 3, el plan no lo toca y reescribe `:497` para que no prometa de más.
  Recomendación: sí, una palabra y un caso más (548); requiere una enmienda tuya.
- **P3 (no bloquea). ¿Cuándo se mezcla la rama de AF-07?** Si `develop` avanza durante AF-02, el ritual 2b de `fase-ejecutor`
  detiene al ejecutor y exige re-verificar. Recomendación: mezclarla después del PR de AF-02.

## Objetivo y decisiones bloqueadas

Objetivo: que `--estado` diga el veredicto real de la última auditoría sin romperse nunca por un `gaps.md`, y que R6 y R7
fechen bien en el cambio de año y desde cualquier huso, antes de la primera edición de PLAN en enero.

1. **Alcance (adenda 1):** puntos 2 y 3, completos. Nada más de la fila ni de los residuales.
2. **Veredicto (adenda 2):** primera línea de veredicto del último bloque `## Auditoría Fase`; nunca se leen los hallazgos.
   La descripción entre paréntesis de la adenda no cubre AF-01 ni BE-02 (`Veredicto Fase D:` no contiene `Veredicto:`): manda
   "los seis formatos". Y su "contiene" se implementa anclado al inicio de línea (admite `- ` y negrita): la única mención real
   a mitad de línea es `BE-33/gaps.md:290`, y ese bloque ya tiene l.176.
3. **Salida de `--estado`:**

   | Situación de `gaps.md` | `read_last_audit` | Imprime |
   |---|---|---|
   | Veredicto `PASS` | `pass` | `última auditoría: PASS` |
   | Veredicto `GAPS` | `gaps` | `última auditoría: con gaps` |
   | Último bloque sin veredicto, o archivo sin bloques | `no_verdict` | `última auditoría: sin veredicto` |
   | Vacío, solo espacios, no UTF-8 o no se puede abrir | `unreadable` | `última auditoría: ilegible` |
   | No existe | no se llama | nada |

   El último bloque manda: si no tiene veredicto, no se hereda el de un bloque anterior. Un bloque `GAPS` con hallazgos
   `RESUELTO (<hash>)` sigue en `con gaps` hasta que una auditoría nueva añada su bloque.
4. **`progress.json` (adenda 3):** es dato. `read_progress` no cambia. Ya hecho en `eaf2303`; confirmado con `--estado`:
   A9, AF-05, S1, SEC1 y BE-33 salen "ejecutado".
5. **R7, año (adenda 4):** por fila, el de la fecha más cercana a la versión, entre versión −1, versión y versión +1. Se
   retira la monotonía. **Empate:** solo es posible si el año entre candidatos tiene 366 días (v`1 jun 2028`, fila `1 dic`,
   183 días a cada lado) y gana el año **anterior**: la fila cuenta como pasada y R7 exige su marca; el posterior la
   ocultaría como futura. Fecha que no existe en ningún candidato (`31 nov`, `29 feb` sin bisiesto): se salta, como hoy.
6. **Huso (adenda 5):** `project_date()` es el único punto de conversión; R6 y R7 pasan por él. Su definición depende de P1.
7. **Trinquete, sin excepción (adenda 6; ADR-0005):** ninguno de los dos archivos tiene rojo heredado, así que rige el ritual
   normal. El conjunto heredado se declara con la forma de BE-33 (decisión 2): igual conteo con otro error es BLOQUEANTE.

   | Archivo | Fase | Ruff | Mypy |
   |---|---|---|---|
   | `scripts/check_docs.py` | A, B | 0 → **0** | 0 → **0** |
   | `tests/test_check_docs.py` | A, B | 0 → **0** | 0 → **0** con `mypy <archivo>` |
   | I001 l.1 (8, A4): `app/api/dependencies.py`, `api/routers/audit.py`, `core/email.py`, `db/database.py`, `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`, `services/user_service.py` | no se tocan | **`Found 9 errors.`**, con BE-32 | |
   | I001 `tests/test_user_service.py:3` (1, BE-32) | no se toca | incluido arriba | |
   | Mypy (5, A4): `db/database.py:11`, `core/security.py:71`, `:87`, `services/user_service.py:124`, `api/dependencies.py:95` | no se tocan | | **`Found 5 errors in 4 files (checked 35 source files)`** |

   Resto de la línea base, medido hoy: format OK, 4 KEPT, docs OK, cobertura 96.11 %, 438 passed. Salida esperada de cada fase:
   `Compuerta NO superada: ruff check, mypy`, exit 1.
8. **Herramientas:** siempre `./venv/Scripts/python.exe` (prevalece sobre el `python …` de los rituales, AF-07). `ruff format`
   con `py314` reescribe `except (OSError, ValueError):` como `except OSError, ValueError:` (PEP 758, medido): se escribe así.

## Análisis del redactor

**Qué y por qué.** El parser ancla el veredicto al inicio de línea, de modo que los hallazgos no pueden confundirlo. La
fórmula de la fila para R7 no se usa (rompe 3 tests y falla en diciembre → enero). R6 necesita el instante del commit, no su
fecha: `%cs` da el día en la zona del committer y pierde la conversión, de ahí `%cI`.

**Orden.** A y B son independientes en código; solo comparten archivos. A primero: es la menor (+51/−4 en el script frente a
+69/−22) y no cambia ningún test existente. B queda bloqueada por P1; A no.

**Tests que congelan comportamiento.**
- `tests/test_check_docs.py:755-911` (R7): **ninguno cambia.** Medido: todos verdes con el año por cercanía, incluido
  `_plan_section_3` (l.797-802, versión `31 oct` anterior a tablas de noviembre, misma fecha elegida). Los ids
  `year-by-monotony` y `year-jump-*` quedan con nombre antiguo; se conservan por la adenda 4.
- **Cambian 5 de los 148 casos, fuera de ese rango, por `%cs` → `%cI`:** los 4 de `test_git_last_commit_date` (l.580-606:
  comando esperado, y `committed` pasa a `"2026-11-01T10:00:00-05:00\n"`) y `test_cierre_flag_fails…` (l.943-948: comando
  esperado). No hay forma de convertir el huso sin el instante. Los otros 143 siguen intactos.
- `test_repo_is_green` y `test_estado_on_real_repo_be01` siguen válidos: los `gaps.md` son registros que no se editan.

**Riesgos.**
- R7 fecha mal una fila a más de unos 6 meses de la versión (v`2 ene 2027`, fila `1 jun` → `2027-06-01`, medido). Es propio
  de la regla decidida. En el PLAN de hoy la distancia máxima es de 13 días; el proyecto termina el 11 ene 2027 `(CONTEXT §2)`.
- El parser no valida los conteos: `PASS (2 bloqueantes)` se lee `PASS`. El veredicto es del auditor; no se reabre.
- Hasta que AF-07 se mezcle, un auditor puede no escribir la línea y el `gaps.md` de AF-02 puede salir `sin veredicto`. No es
  un fallo: es la salida correcta para ese dato.
- El parser no distingue bloques de código, y ninguno de los 9 `gaps.md` tiene veredictos o bloques dentro de uno (medido).

**R6 en detalle.** Hoy: `git log -1 --format=%cs`, y `date.fromisoformat`. Después: `--format=%cI`, y
`project_date(datetime.fromisoformat(out))`. Caso real: `d7de2d6` tiene fecha `2026-11-06T00:37:13Z`, 19:37 del 5 nov en
Bogotá, y es el último commit de `docs/CONTEXT.md`. La verificación (l.92) midió los 60 últimos merges, todos `-0500`, y no lo
vio. Por eso cambia el resultado de `--cierre` sobre el repo real, medido con los mismos datos:

| Archivo | Versión | Último commit | Hoy | Tras B |
|---|---|---|---|---|
| `docs/CONTEXT.md:8` | 5 nov | `d7de2d6`, 5 nov en Bogotá | error R6 **falso** | sin error |
| `docs/PLAN.md:3` | 5 nov | `c0aef71`, 6 nov 14:57 −05:00 | error R6 esperado | igual |
| `docs/backlog.md:3` | 5 nov | `caebace`, 6 nov 15:13 −05:00 | error R6 esperado | igual |

Si el cierre del día llega antes que B, los tres desaparecen por la vía normal y esta tabla ya no se puede reproducir.

**¿ADR? No.** Las reglas son las de la adenda, documentadas en el script; ADR-0007 y ADR-0008 no fijan huso (grep vacío) y
ADR-0008 no fija el año (verificación). No hay módulo, patrón ni contrato HTTP nuevo.

**Medido** (sonda: copia desechable en el scratchpad con los textos de este plan): compuerta y `--estado` de `HEAD`; RED, verde
y los 31 mutantes; `--cierre` antes y después; `ZoneInfo` y wheel; R7 sobre copia del PLAN real (v`2 ene 2027`: de 0 a 4
errores; v`31 dic 2026`: 4 y 4; PLAN real: mismas 15 fechas); `TZ=AAA-14` por CLI (de 1 error a 0); offsets de commits (455
`-05:00` y 2 `Z`); `time.tzset` no existe en Windows; `%cI` de Git 2.56 emite `Z`.
**Solo leído:** CI en `ubuntu-latest` (`.azure-pipelines/ci-pipeline.yml`): no pude medir si trae base de husos ni qué forma
da su `%cI`; B1 no depende de lo primero y el test `utc-offset-next-day` cubre `+00:00`; bajo B2, `dev` instala `tzdata`.
Prompts de los auditores, ADR y bitácoras.
**Por aritmética sobre lo medido:** el RED de 88 y de 21 con el test de etiquetas, añadido después de medirlo, y los totales
526 y 547 de la compuerta (438 + casos nuevos); la sonda solo corrió `tests/test_check_docs.py`.

## Regla de alcance

**Sí:** `read_last_audit`, sus constantes y la rama de `estado()`; `_date_near`, `_dated_rows`, `project_date`, `project_today`,
`git_last_commit_date`, el reloj de R7; las docstrings que cada cambio vuelve falsas; los tests y mutantes de abajo.
**No:** `read_progress`; `gaps.md` existentes, incluido `BE-33/gaps.md:290`; `app/`; `.claude/`; `.opencode/`; `AGENTS.md`;
`scripts/check.py`; puntos 1 y 5; "punto 6"; `reconfigure`; mes heredado; `docs/backlog.md`, `CONTEXT` y `PLAN`.
**Lo hace David en rama aparte, con AF-07:** la línea de contrato en `handoff-auditor.md`. El parser funciona se haya mezclado
o no: la acepta como un formato más y no lee ese archivo (V7).
**Sesión de cierre, no este plan:** fila AF-08 (`Sale → B-FUTURO`, primera en el rescate de los AF: puntos 1 y 5, "punto 6",
`reconfigure`), párrafo "modo ejemplo" en `docs/sesiones/estudio.md` y `mentor.md`, AF-02 → Hecho, y `docs/CONTEXT.md:294`,
que queda obsoleta al salir A.

## Fases

Mutantes de ambas fases: sobre una carpeta **nueva** del scratchpad con `scripts/check_docs.py`, `tests/test_check_docs.py`,
`docs/` y `.claude/commands/`, nunca en el repo. Desde esa carpeta, con el Python del venv por ruta absoluta:
`pytest tests/test_check_docs.py -q --tb=no -p no:cacheprovider`. Primero el control M0 y luego cada mutante, por separado,
sobre el script sin mutar. **Muere** = al menos 1 `failed`. Tabla completa en el handoff.

### Fase A — Leer el veredicto del último bloque de `gaps.md` (la más pequeña)

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py`.
- **Cambios exactos:**
  1. Antes de `estado()`:
     ```python
     AUDIT_BLOCK_RE = re.compile(r"^## Auditoría Fase ")
     """Heading of an audit block: ``handoff-auditor`` adds one per audit to the item's ``gaps.md``."""

     VERDICT_RE = re.compile(
         r"^(?:- )?(?:\*\*)?Veredicto(?: Fase [^:*]+)?:(?:\*\*)? (?:\*\*)?(PASS|GAPS)\b"
     )
     """Verdict line, anchored at its start: a finding that merely mentions a verdict is not one."""

     AuditVerdict = Literal["pass", "gaps", "no_verdict", "unreadable"]

     STATE_AUDIT = "última auditoría: {verdict}"
     AUDIT_LABELS: dict[AuditVerdict, str] = {
         "pass": "PASS",
         "gaps": "con gaps",
         "no_verdict": "sin veredicto",
         "unreadable": "ilegible",
     }
     """What ``--estado`` prints for each ``AuditVerdict``."""


     def read_last_audit(path: Path) -> AuditVerdict:
         """Read the verdict of the last audit block of a ``gaps.md``.

         Only the first verdict line of the last ``## Auditoría Fase`` block counts: findings are never
         read, so a mention of ``[BLOQUEANTE]`` or of an old ``PASS`` cannot change the result.

         Args:
             path: Path of the ``gaps.md`` file.

         Returns:
             ``pass`` or ``gaps`` from the verdict line; ``no_verdict`` if the file has no block or its
             last block has no verdict line; ``unreadable`` if it is blank or cannot be read as UTF-8.
         """
         try:
             text = path.read_text(encoding="utf-8")
         except OSError, ValueError:  # ValueError covers UnicodeDecodeError
             return "unreadable"
         if not text.strip():
             return "unreadable"
         lines = text.splitlines()
         starts = [n for n, line in enumerate(lines) if AUDIT_BLOCK_RE.match(line)]
         if not starts:
             return "no_verdict"
         for line in lines[starts[-1] + 1 :]:
             m = VERDICT_RE.match(line)
             if m:
                 return "pass" if m.group(1) == "PASS" else "gaps"
         return "no_verdict"
     ```
  2. `estado()` (l.523-526): las cuatro líneas pasan a
     `parts.append(STATE_AUDIT.format(verdict=AUDIT_LABELS[read_last_audit(gaps)]))`.
  3. Docstrings. `:25` pasa a:
     ```text
       `--estado`: vista derivada de cada ítem de `docs/deuda/`; `progress.json` se lee como JSON y
           `gaps.md` por la línea de veredicto de su último bloque `## Auditoría Fase`.
     ```
     `:497` pasa a `0: the view is informative. An unreadable ``gaps.md`` is reported, never raised.` Sin P2 no puede decir
     `Always 0`: seguiría siendo falso para un `progress.json` que no se puede abrir.
- **Tests (RED primero):** tras `test_estado_on_real_repo_be01`, **88 casos nuevos**. Helpers: `_BLOCK =
  "## Auditoría Fase A — 2026-11-01\n\n"`, `_PASS_LINE = "Veredicto: PASS (0 bloqueantes, 1 opcional)."`, `_GAPS_LINE =
  "Veredicto: GAPS (1 bloqueantes, 0 opcionales)."`, `_last_audit(tmp_path, content)` y `_audit_state(verdict)`. Con mypy, los
  dos helpers guardan en una variable anotada antes de devolver (`check_docs` es `Any`). Se afirma con las constantes, nunca
  con texto en español.
  ```python
  _REAL_VERDICT_SHAPES = [
      "**Veredicto: {v} (0 bloqueantes, 4 opcionales).**",  # A9:84, BE-33:176
      "Veredicto: **{v} (0 bloqueantes, 4 opcionales)**. Commit auditado `bd9b8c7`.",  # AF-05:5
      "Veredicto: {v} (0 bloqueantes, 2 opcionales). Compuerta re-ejecutada.",  # BE-01:34, S1, SEC1
      "Veredicto Fase D: {v} (0 bloqueantes, 3 opcionales).",  # AF-01:177
      "Veredicto Fase A: **{v} (0 bloqueantes, 3 opcionales)**.",  # BE-02:58
      "- **Veredicto:** {v} (0 bloqueantes, 5 opcionales). F es la última fase.",  # BE-15:575
  ]
  _CONTRACT_SHAPES = [
      "**Veredicto Fase X: {v} (0 bloqueantes, 2 opcionales).**",
      "**Veredicto Fase D-bis: {v} (1 bloqueantes, 2 opcionales).**",
  ]
  _NOT_VERDICTS = [
      "- [OPCIONAL] — Fase D — un gaps.md con [BLOQUEANTE] y última línea no es PASS",  # BE-33:258
      "- [OPCIONAL] — Fase C — No es bloqueante porque el test existe y pasa",  # BE-33:141
      '  bloqueante: el plan dicta "se conservan" (`plan.md:370-372`).',  # BE-15:368
      '  bloqueante: D1 pidió un ADR "corto" y enumeró su contenido sin evidencia',  # BE-15:688
      "- [BLOQUEANTE] — Fase A — sin corregir — x.py:1",
      "- [BLOQUEANTE] — Fase A — corregido — x.py:1 RESUELTO (abc1234)",
      "Línea final (hallazgo 8). Veredicto Fase D: **GAPS (1 bloqueantes)**.",  # BE-33:290
      "Línea final (hallazgo 8). Veredicto Fase D: **PASS (0 bloqueantes)**.",  # BE-33:290
      "- Veredicto de cierre: el ítem está listo para el PR del bloque: PASS",  # BE-15:737
      "Veredicto: BYPASS del guard",
      "Veredicto: PASSWORD_RESET sin test",
      "Veredicto: pass",
      "BYPASS del guard",
      "no es PASS",
  ]
  ```

  | Test | Casos | Afirma |
  |---|---|---|
  | `test_read_last_audit_accepts_each_verdict_shape` | 16 | seis formatos + dos de contrato × `PASS`/`GAPS` → `pass`/`gaps` |
  | `test_read_last_audit_never_takes_a_finding_for_a_verdict` | 42 | cada `_NOT_VERDICTS`: solo → `no_verdict`; tras `_PASS_LINE` → `pass`; tras `_GAPS_LINE` → `gaps` |
  | `test_read_last_audit_reads_only_the_last_block` | 4 | PASS+GAPS → `gaps`; GAPS+PASS → `pass`; PASS+sin línea → `no_verdict`; sin línea+PASS → `pass` |
  | `test_read_last_audit_first_verdict_of_the_block_wins` | 4 | GAPS y luego PASS → `gaps`; al revés → `pass`; veredicto tras `### Hallazgos`/`### Cierre` → `pass`; PASS y luego `## Notas` sin línea → `pass` |
  | `test_read_last_audit_ignores_text_outside_blocks` | 4 | `# GAPS — BE-15` + bloque PASS → `pass`; + bloque sin línea → `no_verdict`; `_GAPS_LINE` antes del bloque PASS → `pass`; sin ningún bloque → `no_verdict` |
  | `test_read_last_audit_empty_or_not_utf8_is_unreadable` | 4 | bytes `b""`, `b"\n"`, `b"  \n\n"`, `b"## Auditor\xeda Fase A\n"` → `unreadable` |
  | `test_read_last_audit_unopenable_path_is_unreadable` | 1 | `gaps.md` es un directorio → `unreadable` |
  | `test_read_last_audit_real_block_without_verdict` | 2 | A9 cortado antes de `## Auditoría Fase B`, AF-01 antes de `Fase D`, escritos a `tmp_path` → `no_verdict` |
  | `test_estado_prints_every_item_and_never_raises` | 1 | ítems A PASS, B vacío, C `\xff\xfe`, D sin línea, E GAPS, F sin `gaps.md`: exit 0, seis líneas en orden, cada una termina en su `_audit_state`, F sin esa parte |
  | `test_estado_on_real_gaps_files` | 9 | los 9 ítems: `read_last_audit` = `pass` y la línea termina en `_audit_state("pass")` |
  | `test_audit_labels_cover_every_verdict_without_repeating` | 1 | claves = las 4; 4 valores distintos; `AUDIT_LABELS["pass"] == "PASS"` |

  RED esperado antes del código: `88 failed, 148 passed` (todos por función ausente; lo que prueba que detectan la lógica
  antigua es MA13). Resultado esperado de los 9 reales, con su línea:

  | Ítem | Última fase | Línea | Hoy | Tras A |
  |---|---|---|---|---|
  | A9 | B | l.84 | con gaps | PASS |
  | AF-01 | D | l.177 | PASS | PASS |
  | AF-05 | A | l.5 | con gaps | PASS |
  | BE-01 | D | l.34 | con gaps | PASS |
  | BE-02 | A | l.58 | PASS | PASS |
  | BE-15 | F | l.575 (`:737` no cuenta) | PASS | PASS |
  | BE-33 | D | l.176 (`:290` no cuenta) | PASS | PASS |
  | S1 | C | l.46 | PASS | PASS |
  | SEC1 | A | l.5 | con gaps | PASS |

- **Mutantes (M0: `236 passed`):**

  | Id | Cambio | Medido |
  |---|---|---|
  | MA1 (M1) | `return "pass"` al entrar en `read_last_audit` | 49 failed |
  | MA2 (M2) | `return "gaps"` al entrar | 63 failed |
  | MA3 (M3) | la rama de `estado()` pasa a `pass` | 10 failed |
  | MA4 | `starts[-1]` → `starts[0]` en el corte | 3 failed |
  | MA5 | quitar `\b` | 1 failed |
  | MA6 | quitar `^` y usar `.search` | 2 failed |
  | MA7 | `reversed(lines[…])`: gana el último veredicto | 2 failed |
  | MA8 | solo `except ValueError` | 1 failed |
  | MA9 | solo `except OSError` | 2 failed |
  | MA10 | quitar el `if not text.strip()` | 4 failed |
  | MA11 | buscar en `lines` enteras | 4 failed |
  | MA12 | quitar el `if not starts` | 1 failed |
  | MA13 | lógica antigua: `"PASS" in …splitlines()[-1]` | 48 failed |
  | MA14 | `AUDIT_BLOCK_RE` = `^## ` | 1 failed |
  | MA15 | etiquetas `pass` y `gaps` intercambiadas | 1 failed |
  | MA16 | `re.I` en `VERDICT_RE` | 1 failed |

- **Criterio de aceptación:**
  - `tests/test_check_docs.py`: `236 passed`. Compuerta: `526 passed`, cobertura 96.11 %, 4 KEPT; ruff y mypy con los
    conjuntos exactos de la decisión 7; `ruff` y `mypy` de los dos archivos, sin errores.
  - `--estado` sobre el repo: exit 0; los 9 `PASS`, ninguno `con gaps`, `sin veredicto` ni `ilegible` (V8).
  - Fixture con ítems A, B vacío y C por CLI: tres líneas, exit 0, sin traceback.
  - Los 16 mutantes mueren y el handoff lo muestra con M0. Ningún test existente cambia: `git show <hash> -- tests/test_check_docs.py`
    solo añade líneas.
- **Fuera de alcance:** R6, R7, reloj, `read_progress`, `.claude/`, cualquier `gaps.md`.
- **Commit:**
  ```text
  fix(flow): read --estado verdict from the last audit block of gaps.md

  --estado looked for PASS in the last line of gaps.md: 4 of the 9 real files
  showed "con gaps" with a PASS verdict, any PASS substring gave a false PASS,
  and an empty or non-UTF-8 file ended the view with a traceback and exit 1.

  - scripts/check_docs.py: read_last_audit takes the first verdict line of the
    last audit block and never reads findings. A block without one prints
    "sin veredicto"; a blank or undecodable file prints "ilegible".
  - tests/test_check_docs.py: 88 cases, built from the real gaps.md lines that
    fool a naive parser. Coverage does not measure scripts/, so 16 mutants on a
    disposable copy prove them.

  The gaps.md records are not edited. read_progress is unchanged (AF-02 addendum 3).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Fechar R7 por el año más cercano y evaluar R6 y R7 en el huso del proyecto

**Precondición: respuesta a P1, anotada por David en la línea `Estado` de la cabecera.** Si es B2: David instala `tzdata` en
el venv antes de arrancar.

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py` y, **solo con B2**, `pyproject.toml`.
- **Cambios exactos:**
  1. Import: `from datetime import UTC, date, datetime, timedelta, timezone`. Bajo B2: `UTC, date, datetime` y `from zoneinfo
     import ZoneInfo`; en `pyproject.toml`, `"tzdata"` en `dev`.
  2. Antes de `git_last_commit_date`:
     ```python
     PROJECT_TZ = timezone(timedelta(hours=-5), "America/Bogota")
     """The project's time zone: Colombia is on a fixed UTC-5, without daylight saving."""


     def project_date(instant: datetime) -> date:
         """Return the calendar day of an instant in the project's time zone.

         R6 and R7 compare days, and a machine or a committer in UTC is on the next day from
         19:00 in Bogotá. Both rules go through here, whatever the machine's zone is.

         Args:
             instant: A timezone-aware instant.

         Returns:
             Its date in the project's time zone.
         """
         return instant.astimezone(PROJECT_TZ).date()


     def _utc_now() -> datetime:
         return datetime.now(UTC)


     def project_today() -> date:
         """Return today's date in the project's time zone (R7's clock)."""
         return project_date(_utc_now())
     ```
     **Bajo B2** no hay `PROJECT_TZ` ni su docstring; `project_date` devuelve
     `instant.astimezone(ZoneInfo("America/Bogota")).date()`. Se construye dentro de la función para que la pasada por defecto
     no dependa de `tzdata` (medido: sin él, la pasada por defecto sigue en exit 0).
  3. `git_last_commit_date`: `"--format=%cI"` y `return project_date(datetime.fromisoformat(out))`. Primera línea de la
     docstring: `Return the project-zone day of a file's last commit (``git log -1 --format=%cI``).` Returns: `The commit's day
     in the project's time zone, or ``None`` if git is missing, fails (not a repository) or the file has no history (untracked,
     shallow clone).`
  4. Antes de `_dated_rows`:
     ```python
     def _date_near(month: int, day: int, anchor: date) -> date | None:
         """Date of a day and month in the year that leaves it nearest to ``anchor``.

         A tie (possible only across a 29 Feb, about six months away) takes the earlier year: the row
         counts as past and R7 demands its mark, while the later year would hide it as future.

         Args:
             month: Month number.
             day: Day of the month.
             anchor: The date the year is inferred from.

         Returns:
             The nearest valid date among the anchor's year and its two neighbours, or ``None`` if the
             day does not exist in any of them.
         """
         candidates: list[date] = []
         for year in (anchor.year - 1, anchor.year, anchor.year + 1):
             try:
                 candidates.append(date(year, month, day))
             except ValueError:
                 continue
         return min(candidates, key=lambda c: abs((c - anchor).days), default=None)
     ```
  5. `_dated_rows(lines, anchor: date)`: fuera `year` y `start_year`; `month = None` al abrir tabla; si la fila nombra el mes,
     `month = _MONTHS.index(m.group(3)) + 1`, sin `year += 1`; el `try/except` pasa a `day = _date_near(month, int(m.group(2)),
     anchor)` con `if day is None: continue`. Docstring:
     ```text
     Rows of the tables that have a ``Cierre`` column, with their date and ``Cierre`` cell.

     The first line of each table is its header and resets the month, which is inherited from the
     last row that names it. Each row takes the year nearest to ``anchor`` (``_date_near``). Rows
     without a date (``(se fecha …)``, separator) or before any month is named are skipped, and so
     is an impossible date.
     ```
  6. `rule_closed_days_marked`: `today: Callable[[], date] = project_today`; llamada `_dated_rows(…, version.when)`; `:724` pasa a
     `yet. Each row takes the year nearest to PLAN's version line (``_date_near``).`
  7. Docstring del módulo, `:29-33`:
     ```text
       R6. La línea de versión (ADR-0007) de cada archivo del alcance no es anterior a su último commit,
           con el día del commit en el huso del proyecto; un archivo sin línea de versión es error solo
           si su último commit es posterior al 28 oct 2026. Cambios sin commitear o git no disponible
           son avisos, nunca error.
       R7. Toda fila de PLAN §3 con fecha anterior a hoy (en el huso del proyecto) lleva en `Cierre` la
           marca `[✔◐✘] N`. El mes se hereda dentro de cada tabla; el año de cada fila es el que deja su
           fecha más cerca de la línea de versión de PLAN.
     ```
- **Tests (RED primero):** **21 casos nuevos y 5 existentes editados.**
  - Import del test: `from datetime import UTC, date, datetime`. Helper tras `_plan_section_3`: `_plan_versioned(tables, version)`
    (reemplaza `_version_line("31 oct 2026")`). Tablas con `_TABLE_HEAD`.
  - **Editados:** `%cs` → `%cI` en l.602 y l.944; en `test_git_last_commit_date`, `committed` usa
    `"2026-11-01T10:00:00-05:00\n"` y entran `utc-z-next-day` (`"2026-11-06T00:37:13Z\n"` → `date(2026, 11, 5)`) y
    `utc-offset-next-day` (`"2026-11-06T00:37:13+00:00\n"` → `date(2026, 11, 5)`).
  - `test_r7_year_is_the_nearest_to_the_version_line`, 5 casos de la verificación; fila `| Lun 28 dic | x | |`, `| Mar 29 | y | |`,
    `| Vie 1 ene | z | |` = DIC_ENE:

    | Id | Versión | Filas sin marca | Hoy | Errores | Hoy dan |
    |---|---|---|---|---|---|
    | `a-dec-version` | `31 dic 2026` | DIC_ENE | 2027-01-05 | 3 | 3 |
    | `b-jan-version` | `2 ene 2027` | DIC_ENE | 2027-01-05 | 3 | **0** |
    | `c-oct-nov-rows` | `2 ene 2027` | `Vie 23 oct`, `Lun 2 nov` | 2027-01-05 | 2 | **0** |
    | `d-future-january` | `31 dic 2026` | `Lun 4 ene`, `Mar 5` | 2026-12-31 | 0 | **2** |
    | `e-future-december` | `30 nov 2026` | `Mar 1 dic` | 2026-11-30 | 0 | 0 |

  - `test_r7_year_tie_and_impossible_dates`, 4 casos: `1 jun 2028`, `Vie 1 dic`, hoy 2028-06-02 → 1 (empate al anterior);
    `2 ene 2028`, `Mar 29 feb`, hoy 2028-03-01 → 1; `1 jul 2026`, `Mar 29 feb`, hoy 2028-03-01 → 0; `31 oct 2026`, `Lun 31 nov`,
    hoy 2027-06-01 → 0.
  - `test_project_date`, 3 casos: `2026-11-07 00:30 UTC` → 6 nov; `04:59:59 UTC` → 6 nov; `05:00:00 UTC` → 7 nov.
  - `_freeze_clock(monkeypatch)`: `_utc_now` devuelve `datetime(2030, 3, 2, 0, 30, tzinfo=UTC)`, 19:30 del 1 mar en Bogotá, lejos
    de cualquier ejecución real. `test_project_today_uses_the_project_zone` → `date(2030, 3, 1)`.
  - `test_cierre_r7_clock_is_the_project_zone`: versión `1 mar 2030`, filas sin marca `Jue 28 feb` y `Vie 1 mar`, `subprocess.run`
    con `create_autospec` y `side_effect=FileNotFoundError`: exit 1, una sola `: R7: `, la de `Jue 28 feb`. Mata el reloj local (0
    errores) y el reloj UTC (2).
  - `test_r6_compares_the_commit_date_in_the_project_zone`, 5 casos, con `rule_version_header` real y `subprocess.run` falso
    (`status` → `""`; `log` → el sello para `docs/PLAN.md`, `2026-10-27T12:00:00-05:00` para los demás). Versión `5 nov 2026`:
    `2026-11-06T00:37:13Z` (`real-d7de2d6`) → 0; `2026-11-06T04:59:59Z` → 0; `2026-11-06T05:00:00Z` → 1;
    `2026-11-05T23:00:00-05:00` → 0; `2026-11-06T00:30:00-05:00` → 1. Sin avisos en ninguno.

  RED esperado antes del código: `21 failed, 236 passed`: los 6 de `test_git_last_commit_date`, `test_cierre_flag…`, `b`, `c`, `d`,
  el empate, los 3 de `test_project_date`, `project_today`, `cierre_r7_clock` y los 5 de R6. **Pasan antes y son de
  caracterización:** `a`, `e` y los otros 3 de `tie_and_impossible`.
- **Mutantes (M0: `257 passed`). Exigidos por la adenda 7: MB1 año fijo, MB2 y MB3 hora local:**

  | Id | Cambio | Medido |
  |---|---|---|
  | MB1 | candidatos = `(anchor.year,)` | 5 failed |
  | MB2 | `project_today` → `date.today()` | 2 failed |
  | MB3 | `rule_closed_days_marked`: `today=date.today` | 1 failed |
  | MB4 | `project_date` → `.astimezone(UTC)` | 9 failed |
  | MB5 | R6 sin convertir: `datetime.fromisoformat(out).date()` | 4 failed |
  | MB6 (M4) | fórmula de la fila, con monotonía | 6 failed |
  | MB7 | candidatos en orden inverso: empate al posterior | 1 failed |
  | MB8 | sin `year − 1` | 3 failed |
  | MB9 | sin `year + 1` | 2 failed |
  | MB10 | el `except` de `_date_near` no captura `ValueError` | 3 failed |
  | MB11 | `hours=-4`; bajo B2, `"America/Caracas"` (B2 no medido) | 3 failed |
  | MB12 | vuelta a `%cs` | 7 failed |
  | MB13 | `max` en vez de `min` | 13 failed |
  | MB14 | quitar `if day is None` | 2 failed |
  | MB15 | anchor = 1 ene del año de la versión | 5 failed |

- **Criterio de aceptación:**
  - `tests/test_check_docs.py`: `257 passed`. Compuerta: `547 passed`, cobertura 96.11 %, 4 KEPT; ruff y mypy como en la
    decisión 7; el paso `docs` sigue OK.
  - **`--cierre` diferencial** sobre el mismo `HEAD`, con el script de la fase A sacado a scratchpad (`git show HEAD~:…`, o el
    padre del commit) y `--root` al repo: las líneas R7 no cambian, y entre las R6 la **única** diferencia posible es que
    desaparece `docs/CONTEXT.md:8` si su último commit sigue siendo `d7de2d6`. Exit 1 por errores R6 esperados **no es
    regresión**; un error nuevo sí lo es. En el handoff, ambas salidas literales.
  - **Reloj por CLI:** fixture con una fila de hoy en Bogotá sin marca, `TZ=AAA-14`, entre 05:00 y 24:00 de Bogotá: script de A → 1
    error R7, nuevo → 0. Si se ejecuta tras las 19:00, repetir con `TZ=UTC0`. La suite no puede fijar `TZ`: `time.tzset` no existe
    en Windows y la hora no se controla; por eso congela `_utc_now`.
  - Los 15 mutantes mueren, con M0 en el handoff. `git show --name-only --format= <hash>`: los dos archivos, o tres con B2.
- **Fuera de alcance:** `--estado`, `read_progress`, mes heredado (`Dom 1` tras `Sáb 31 oct`), renombrar ids de tests, `reconfigure`.
- **Commit** (con B2, se añade una viñeta de `pyproject.toml`):
  ```text
  fix(flow): date R7 rows by nearest year and read R6-R7 in project time

  R7 took the year of each table from PLAN's version line: with a January
  version, December rows were dated in the future and never evaluated, and with a
  December version a January table gave false errors. R6 and R7 also used the
  committer's and the machine's zone, so d7de2d6, committed from a UTC machine at
  19:37 on 5 Nov in Bogota, was flagged as 6 Nov.

  - scripts/check_docs.py: each row takes the year nearest to the version line, a
    tie goes to the earlier year; project_date is the only zone conversion and
    R6 reads the commit instant with %cI.
  - tests/test_check_docs.py: cases a-e of the verification, tie, leap day, zone
    boundaries and the real d7de2d6 stamp. The %cs expectations change to %cI;
    the R7 tests stay as they were. Mutants on a disposable copy prove them.

  The formula in the backlog row was not used: it breaks 3 tests and fails from
  December to January.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Expectativas medidas en la sonda con los textos literales de este plan (opción B1; bajo B2, V5 sigue en 1). Desde la raíz, en
Git Bash, tras la fase B.

```bash
# V1. Lectura de la última línea: 0
grep -c 'splitlines()\[-1\]' scripts/check_docs.py
# V2. Año y reloj antiguos: 0
grep -c -E 'version\.when\.year|start_year|date\.today' scripts/check_docs.py
# V3. Fecha de commit: %cs 0 y 0; %cI 2 y 2
grep -c '%cs' scripts/check_docs.py tests/test_check_docs.py
grep -c '%cI' scripts/check_docs.py tests/test_check_docs.py
# V4. Promesa retirada de :497: 0
grep -c 'Always 0' scripts/check_docs.py
# V5. Una sola definición del huso: 1
grep -c 'America/Bogota' scripts/check_docs.py
# V6. Una sola conversión y un solo reloj: 1 y 1
grep -c 'astimezone' scripts/check_docs.py
grep -c 'datetime\.now' scripts/check_docs.py
# V7. El parser no lee el prompt del auditor (vale mezclado o no): 0 y 0
grep -c -E '\.claude/agents|\.opencode' scripts/check_docs.py tests/test_check_docs.py
# V8. Los 9 reales: 9 y 0
./venv/Scripts/python.exe scripts/check_docs.py --estado | grep -E '^(A9|AF-01|AF-05|BE-01|BE-02|BE-15|BE-33|S1|SEC1):' | grep -c 'última auditoría: PASS'
./venv/Scripts/python.exe scripts/check_docs.py --estado | grep -E '^(A9|AF-01|AF-05|BE-01|BE-02|BE-15|BE-33|S1|SEC1):' | grep -c -E 'con gaps|sin veredicto|ilegible'
# V9. Tests del script: 257 passed
./venv/Scripts/python.exe -m pytest tests/test_check_docs.py -q
# V10. gaps.md existentes sin editar: como mucho docs/deuda/AF-02/gaps.md
git diff --name-only e4e7d43 HEAD -- 'docs/deuda/*/gaps.md'
# V11. Compuerta: 547 passed, 96.11 %, 4 kept, "Found 9 errors.", "Found 5 errors in 4 files", exit 1 solo por ruff check y mypy
./venv/Scripts/python.exe scripts/check.py
```

Con P2 aprobada, V9 da 258 y V11 548. **No entra aquí** `--cierre` a secas: su resultado depende de si ya se hizo el cierre.

## Residuales

| Hallazgo | Evidencia | Destino sugerido |
|---|---|---|
| **Mes heredado sin dueño:** la adenda 6 lo omite de AF-08 | `docs/deuda/AF-01/handoff-Fase_D.md:168-170`; discrepancia 3 de la verificación; `Dom 1` tras `Sáb 31 oct` da `2026-10-01` | Añadirlo a la fila AF-08 en el cierre |
| `read_progress` no captura `OSError` | Medido: `progress.json` directorio → traceback, exit 1 | P2; si no, fila AF-08 |
| `.opencode/agent/handoff-auditor.md:44-46` no fija `## Auditoría Fase X`; su `gaps.md` saldría `sin veredicto`, y cita un `registro.json` que no existe | Leído | Rama de David con AF-07 |
| Ids `year-by-monotony`, `year-resets-per-table`, `year-jump-*` describen una monotonía retirada | `tests/test_check_docs.py:834`, `:881-885` | BE-32; se conservan por la adenda 4 |

## Referencias

Context7 no estaba disponible entre mis herramientas en esta sesión: lo de abajo se comprobó ejecutándolo con las versiones
instaladas.

- Python · 3.14.3 · `zoneinfo` y fuentes de datos: https://docs.python.org/3/library/zoneinfo.html
- Python · 3.14.3 · `datetime.fromisoformat` (acepta `Z`, medido): https://docs.python.org/3/library/datetime.html
- Python · 3.14 · PEP 758, `except` sin paréntesis: https://peps.python.org/pep-0758/
- tzdata · 2026.6 (sin instalar; solo bajo B2): https://pypi.org/project/tzdata/
- Git · 2.56.0.windows.4 · `%cI`: https://git-scm.com/docs/pretty-formats
- Internas: ADR-0005, ADR-0007, ADR-0008; `docs/deuda/BE-33/plan.md` (decisión 2).

## Enmiendas aprobadas

**E0 — 6 nov 2026, 16:50 (David, sesión Mentor): plan aprobado; P1, P2 y P3 resueltos.** Ninguna fase, conjunto ni
total cambia; `progress.json` queda en `Fase_A`.

1. **P1, huso: B1.** `PROJECT_TZ = timezone(timedelta(hours=-5), "America/Bogota")`, solo stdlib; `pyproject.toml` no se
   toca. Razón: Colombia no tiene horario de verano desde 1993 (cero diferencias con la base IANA 1994–2030, medido por
   el planificador); `tzdata` sería una dependencia nueva (AGENTS §2) cuya ausencia rompe `--cierre` y 14 tests. Si el
   huso cambiara, se edita esa línea.
2. **P2, `OSError` en `read_progress`: no.** El punto 3 de la adenda se mantiene (`read_progress` no se toca). El
   docstring de `estado()` deja de prometer "siempre 0" sin matiz: *"Siempre 0, salvo que el sistema operativo impida
   leer un `progress.json` (sin permiso, bloqueado): ese caso termina con traceback y 1, declarado."* Decisión de David:
   el caso es raro y basta con declararlo.
3. **P3, rama de AF-07 (y la línea de contrato en `handoff-auditor.md`): después del PR de AF-02.** Un solo ítem en
   curso (ADR-0005); si `develop` avanzara, el ejecutor exigiría re-verificar.
4. **Desviaciones de la adenda aceptadas:** los 5 tests de `%cs` → `%cI` (necesarios para convertir el huso; los 148 de
   R7 intactos); el caso `TZ=UTC` medido por CLI en el handoff (Windows no tiene `time.tzset`; la suite congela
   `_utc_now`); el efecto visible de `--cierre` 3 → 2 errores R6 (el de CONTEXT era falso) no es regresión.
5. **570 líneas:** aceptadas hoy como "plan que dicta" (precedente BE-33). Si en el cierre hay una razón de peso o una
   fuente (no solo la letra de AGENTS §8) para volver a "plan de una página", se delibera entonces.
6. **Mes heredado** (residual del plan): a AF-08 con los puntos 1, 5, "6" y `reconfigure`, en el cierre.

**E1 — 6 nov 2026, 17:25 (David, tras la auditoría de A): la fase B corrige también la docstring del módulo,
`scripts/check_docs.py:19`.** "Comandos informativos (exit 0 siempre …)" pasa a "(exit 0, salvo la excepción declarada en
`estado()`: un `progress.json` que el sistema no deja leer)". Una línea de texto en un archivo que la fase B ya edita; no
cambia conteos ni tests. Hallazgo 1 de la auditoría de A. Los demás opcionales de A: 4 (veredicto heredado si el
encabezado del último bloque no se reconoce: `Fase_B`, sin tilde, `###`) → el contrato de `handoff-auditor.md` fija el
encabezado exacto `## Auditoría Fase <X> — <AAAA-MM-DD>` además de la línea de veredicto (David, rama de AF-07, también
en `.opencode/agent/handoff-auditor.md`), y la tolerancia del parser (`^##+ Auditor[ií]a Fase[ _]`) va a AF-08 como
punto propio; 2 (dos líneas nuevas en español en la docstring del módulo) → aceptadas, el encabezado ya está en español;
3, 5–8 (lecturas límite sin caso real) y 9–10 (partes de las regex sin fijar) → AF-08; 11–12 (cifras de la sonda) → sin
acción; 13 (`CONTEXT.md:294`, `backlog.md:165`) → cierre; 14 (`progress.json:13` "Needs David's answer to P1") → el
orquestador avisa al ejecutor de B que P1 está resuelta (E0.1); la regla de edición reserva ese archivo al ejecutor.

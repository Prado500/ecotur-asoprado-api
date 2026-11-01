# AF-01 — Especificación de `scripts/check_docs.py` (`B-CHECK-DOCS m1`)

- **Fecha:** 2026-11-01 (domingo comodín, `(PLAN §3)`). **Autores:** David + sesión Mentor, a dos manos. Cinco
  correcciones de David antes del commit (R4 vocabulario en el calificador, R5 fecha adyacente, R2 lookahead, §5 sin
  horas, versiones en el commit).
- **Ítem:** `(backlog AF-01)`. **Bloque:** `B-CHECK-DOCS` `(PLAN §2b)`.
- **Entradas:** `scripts/check_docs.py` en `2647ea3` (4 reglas); ADR-0008 puntos 1, 3, 6 y 7 y su addendum; ADR-0007
  puntos 3–5; bitácora `2026-10-29`, decisión C; bitácora `2026-10-31`, decisión 9 (`DECISION_RE` deja pasar cualquier
  cola); CONTEXT §8 punto 4 (`--estado` no distingue "mezclado").
- **Quién lee esto:** `deuda-verificador`, `plan-redactor`, `fase-ejecutor` y `handoff-auditor`. Este archivo es la
  fuente; la conversación en la que se escribió no lo es.

## 0. Decisiones tomadas al especificar (con su porqué)

1. **Alcance de archivos = ADR-0008 punto 7:** los documentos vivos de CONTEXT §0 (`docs/CONTEXT.md`, `docs/PLAN.md`,
   `docs/backlog.md`) y `docs/sesiones/*.md`. **Excluidos:** `docs/bitacora/`, `docs/adr/` (fechados e inmutables),
   `docs/deuda/**` (artefactos fechados de un ítem; un handoff del 27 oct que diga "lunes 27" es historia, no divergencia),
   `docs/aprendizaje/`, `docs/archive/`.
2. **Los encabezados (`#`) no se excluyen de ninguna regla.** ADR-0008 punto 1: un hecho duro "nunca en un título". La
   fecha de un archivo vivo vive en su línea de versión (ADR-0007 punto 3). CONTEXT §8 llevaba "(sáb 31 oct, cierre)" en
   el título y se corrigió en el primer commit de la rama, antes de que la regla existiera.
3. **Las correcciones de contenido que R2 y R4 habrían atrapado ya están hechas** (commit de docs de David, el primero de
   `item/af-01`): CONTEXT §8 sin días ni fecha en el título; siete filas del backlog (BE-09, B1–B5, D1, D4, D6/S3, P2,
   P3) sin bloques dentro del calificador. **El texto viejo de esas filas y de ese §8 se usa como fixture que debe
   fallar** (sección 4). El ejecutor no edita CONTEXT ni backlog en ninguna fase.
4. **Determinismo:** ninguna regla de la compuerta por defecto depende de `date.today()` ni de `git`. R6 y R7, que sí
   dependen, van en Fase C bajo `--cierre`. **Decisión de David (1 nov, 17:55): las tres fases corren hoy.** Lo que no
   entre al cierre del día pasa a un ítem nuevo (`AF-02`), no se arrastra.
5. **Testabilidad:** el script deja de hacer `os.chdir(REPO_ROOT)` al importar. Toda regla recibe `root: Path`; la CLI
   acepta `--root <dir>` (por defecto, la raíz del repo calculada como hoy). Sin esto no hay tests sobre fixtures.
6. **Calificador en la Decisión: se admite uno, entre paréntesis, sin bloques dentro.** Resuelve lo que `(backlog AF-01)`
   dejó pendiente. Un bloque dentro del paréntesis es decisión en prosa ("si no cabe → `B-FUTURO`") y además redundante:
   la regla "lo no hecho recibe decisión nueva ese día" ya vive en la celda de `B-HIGIENE` de PLAN §2b. "Hecho (…)" lleva
   paréntesis obligatorio (la referencia) y tampoco admite bloques dentro: una re-verificación pendiente va en otra
   columna, no en "Hecho".
7. **Las citas de forma fija se quitan de la línea antes de evaluar R2, R5 y R9** (una cita `(bitácora 2026-10-29)` no
   es una fecha huérfana). Forma fija (ADR-0008 punto 3), con o sin backticks alrededor:
   `(CONTEXT §N)`, `(PLAN §N)`, `(backlog ID)`, `(ADR-NNNN)`, `(AGENTS §N)`, `(README de sesiones)`,
   `(bitácora AAAA-MM-DD)`, `(docs/deuda/ID/)`. `N` admite sufijo de letra (`§2b`); `ID` es `[A-Z]+-\d+` o `[A-Z]\d+`
   (`BE-12`, `AF-01`, `A3`, `S1`).
8. **Solo biblioteca estándar.** Nada nuevo en `pyproject.toml` salvo `mypy.files += ["scripts/check_docs.py"]`.
   Cobertura sigue midiendo `app` (PLAN §6 está anclada a `app`; cambiar la fuente invalidaría la comparación). `ruff` ya
   lee `scripts/`: el archivo reescrito debe quedar en 0 errores de ruff, docstrings `D` incluidas.
9. **Tiempo:** `python scripts/check_docs.py` sobre el repo < 2 s (hoy ~0,1 s). Los tests no corren `git` ni subprocesos.

## 1. Cambios transversales (Fase A, primero)

- `read(root, rel)`; `sections(text) -> list[Section]` con `Section(num: str, title: str, start: int, end: int)` a partir
  de `^## (\d+[a-z]?)\.` (los `###` pertenecen al `##` anterior; `num` es `"0"`, `"2b"`, `"3"`…). Helper
  `lines_outside(root, rel, section_nums)` y `lines_inside(...)` que devuelven `(n, line)`.
- `strip_citations(line) -> str`: quita las citas de forma fija (decisión 7).
- `main(argv) -> int`: `--root`, `--estado`, `--copias [dueño]`, `--huerfanas`, `--cierre` (Fase C). Sin argumentos:
  reglas bloqueantes R1–R5 (y R6/R7 solo con `--cierre`). Avisos (`warnings: list[str]`) se imprimen y no cambian el
  exit code.
- Mensaje de éxito actualizado: lista las reglas que corrieron.
- `tests/test_check_docs.py` (sección 4) importa el módulo con `sys.path.insert(0, "<root>/scripts")`; no se crea paquete.

## 2. Reglas bloqueantes (exit 1 si hay errores)

Formato de cada error: `archivo:línea: <regla>: <mensaje> — "<texto recortado a 80>"`.

### R1 · `rule_commands` — sin cambios
Igual que hoy. Test de regresión: comando en disco sin fila y fila sin archivo.

### R2 · `rule_no_schedule_days` (sustituye a `rule_no_days`)
- **Detecta:** una fecha de cronograma fuera de PLAN §3: `día N` o día de la semana (abreviado o completo, con o sin
  tilde y mayúscula) seguido de número de uno o dos dígitos.
- **Archivos:** `docs/CONTEXT.md`, `docs/backlog.md`, `docs/sesiones/*.md` enteros; `docs/PLAN.md` fuera de la sección
  `3` (`sections`). Encabezados incluidos (decisión 2). Línea con citas quitadas (decisión 7).
- **Expresión** (`re.IGNORECASE`):
  `\b(?:d[ií]a|lun(?:es)?|mar(?:tes)?|mi[eé](?:rcoles)?|jue(?:ves)?|vie(?:rnes)?|s[aá]b(?:ado)?|dom(?:ingo)?)\.?\s+\d{1,2}\b(?![:\d])(?!\s*(?:h(?:oras?)?|m|%)(?!\w))`
  El primer lookahead descarta horas de reloj (`lun 17:00`); el segundo, unidades (`sáb 7 h`, `7 horas`, `4 m`,
  `90 %`). Se usa `(?!\w)` y no `\b` porque `\b` tras `%` exigiría una letra a continuación.
- **Imprime:** `… R2: fecha de cronograma fuera de PLAN §3 — "…"`.
- **Debe fallar:** backlog con `Corte el jueves 29 a las 18:00` (fila BE-16 del 30 oct); CONTEXT §8 del 31 oct con
  `Lun 2 → vie 6` y con `## 8. Próximo paso (sáb 31 oct, cierre)`; `docs/sesiones/x.md` con `día 11`.
- **Debe pasar:** CONTEXT §2 `sáb 7 h o menos, dom descanso`; PLAN §7 `Tope: 15 de diciembre`; PLAN §6 `24 oct, e4fd14d`;
  PLAN §3 `| Lun 2 | …` (dentro de §3); `reunión lun 17:00–18:00`; una línea con solo `(bitácora 2026-10-29)`;
  el repo tal como está en el commit de docs del 1 nov.

### R3 · `rule_blocks` — misma regla, alcance ampliado
- **Archivos:** `docs/backlog.md`, `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/sesiones/*.md`. (No `docs/deuda/`, decisión 1.)
- **Expresión:** definidos = `^\| `(B-[A-Z0-9-]+)` \|` en PLAN; usados = `B-[A-Z0-9-]+` en cada línea. Sin cambios.
- **Debe fallar:** `docs/sesiones/mentor.md` con `B-INEXISTENTE`. **Debe pasar:** el repo de hoy.

### R4 · `rule_decisions` — un bloque, un calificador opcional, nada más
- **Detecta:** celda "Decisión" fuera del vocabulario. Vocabulario: exactamente una de `Entra · \`B-X\``,
  `Sale → \`B-FUTURO\``, `Decidir en \`B-X\``, `Hecho (…)`; las tres primeras admiten **un** calificador opcional entre
  paréntesis; el paréntesis de `Hecho` es obligatorio. Ningún paréntesis contiene `B-…` ni paréntesis anidados. La celda
  entera va en negrita (`**…**`) y no hay nada más.
- **Archivos:** `docs/backlog.md`, todas las tablas con columna `Decisión` (hoy: A, A2, B, E). Se mantiene la
  partición de celdas por ` | ` y la localización de la columna por el encabezado de cada tabla (código actual).
- **Expresión:** con `QUAL = r"\((?:(?!B-[A-Z0-9-]+)(?!\b(?:Entra|Sale|Decidir|Hecho)\b)[^()])*\)"` (el calificador
  tampoco puede contener una palabra del vocabulario, en mayúscula inicial y como palabra completa):
  `^\*\*(?:(?:Entra · `B-[A-Z0-9-]+`|Sale → `B-FUTURO`|Decidir en `B-[A-Z0-9-]+`)(?: QUAL)?|Hecho QUAL)\*\*$`
- **Imprime:** `… R4: decisión fuera del vocabulario (un bloque, un calificador sin bloques) — "…"`.
- **Debe fallar:** BE-08 del 30 oct `**Entra · \`B-ORDEN\` (backend) y \`B-FE-RESERVAS\` (cliente)**`;
  BE-09 del 31 oct `**Decidir en \`B-HIGIENE\` (verificar lo que existe; luego \`B-FUTURO\`)**`;
  `**Entra · \`B-PAGOS\` (mitigación en \`B-FE-LISTA\`)**`; `**Entra · \`B-X\` (a) (b)**` (dos calificadores);
  `**Hecho**` (sin referencia); `**Hecho (ADR-0003; re-verificación en \`B-TESTS\`)**`; `Entra · \`B-X\`` sin negrita;
  `**Entra · \`B-X\` (Sale)**` y `**Entra · \`B-X\` (Hecho parcialmente)**` (vocabulario dentro del calificador).
- **Debe pasar:** BE-18 `**Entra · \`B-RESERVAS\` (mínimo)**`; FE-05 `**Entra · \`B-FE-LISTA\` (parcial: solo la señal
  visual)**`; BE-12 `**Entra · \`B-PAGOS\` (solo ADR; código si cabe)**`; BE-14 `**Sale → \`B-FUTURO\`**`;
  BE-10 `**Sale → \`B-FUTURO\` (con nota legal)**`; P2 nuevo `**Entra · \`B-HIGIENE\` (\`detalle\`→\`detail\`)**`;
  BE-01 `**Hecho (PR #61, 27 oct; ADR-0006)**`; `**Decidir en \`B-HIGIENE\`**`; el repo de hoy.
- **Nota:** la mitigación de BE-14 vive en su Nota técnica y en la celda de `B-FE-LISTA` de PLAN §2b; eso es correcto y la
  regla lo deja así. Las colas "si no cabe → `B-FUTURO`" de siete filas se movieron a otras columnas el 1 nov.

### R5 · `rule_deadline` (nueva)
- **Detecta:** una fecha de entrega distinta de la del dueño, o sin cita. Dueño: CONTEXT §2, fila `| **Deadline** |`;
  la primera fecha de esa celda es el deadline (hoy `11 de enero de 2027`). Si no se puede extraer, error de R5
  ("deadline no legible en CONTEXT §2").
- **Archivos:** `docs/PLAN.md`, `docs/backlog.md`, `docs/sesiones/*.md` (CONTEXT es el dueño: excluido).
- **Expresión:** disparador `(?i)\b(?:entrega|deadline|fecha l[ií]mite)\b` **y** al menos una fecha en la línea (citas
  quitadas), con `DATE = r"\b(\d{1,2})(?: de)? (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[a-z]*\b(?:(?: de)? (\d{4}))?|\b(\d{4})-(\d{2})-(\d{2})\b"`.
  La fecha evaluada es la **más cercana al disparador** dentro de una ventana de ±40 caracteres, a cualquier lado (el
  hito de PLAN §3 la lleva antes: `Lun 11 ene — entrega`). Si no hay fecha en la ventana, la línea no se evalúa; otras
  fechas de la línea no son asunto de R5. La línea es válida si esa fecha es igual al deadline (día y mes; año si lo
  trae) **y** la línea contiene `(CONTEXT §2)` (con o sin backticks).
- **Imprime:** `… R5: fecha de entrega "7 de noviembre" ≠ deadline de CONTEXT §2 — "…"` o `… R5: fecha de entrega sin
  cita (CONTEXT §2) — "…"`.
- **Debe fallar:** PLAN 1.7 `entrega del 7 de noviembre`; `entrega el 11 ene` sin cita; `**Lun 11 nov — entrega en
  línea** \`(CONTEXT §2)\`` (fecha antes del disparador, distinta del deadline); CONTEXT §2 de fixture sin fila `Deadline`.
- **Debe pasar:** PLAN §3 `**Lun 11 ene — entrega en línea** \`(CONTEXT §2)\``; PLAN §2b `… integración con María Paula;
  entrega | …` (sin fecha); PLAN `colchón 1 más el domingo anterior a la entrega` (el `1` no es fecha);
  `corte de código el 18 dic y entrega el 11 ene \`(CONTEXT §2)\`` (la fecha adyacente es 11 ene); el repo de hoy.

## 3. Comandos informativos (exit 0) y Fase C

### R8 · `--copias [dueño]` (Fase B)
- Lista `archivo:línea: <cita>: "<texto>"` de toda cita de forma fija (decisión 7) en los archivos del alcance
  (decisión 1). Con argumento (`--copias "CONTEXT §2"`, `--copias ADR-0008`, `--copias backlog`), solo las citas cuyo
  interior empieza por ese texto. Orden: archivo, línea. Es el mecanismo del paso 3 del ritual de cierre
  `(README de sesiones)` y de ADR-0008 punto 6.
- **Test:** fixture con tres citas en dos archivos; sin filtro salen 3; con filtro `CONTEXT §2` sale 1.

### R9 · `--huerfanas` (Fase B)
- Lista **candidatos** a hecho duro sin cita en la misma línea. Patrones: `DATE` de R5; `\b\d{1,3} %`;
  `\b\d+ tests\b`; `\b\d+ h\b`; `\b\d+ m\b` (medias jornadas). Se evalúa sobre la línea con citas quitadas y solo si
  la línea original **no** contiene ninguna cita de forma fija. **Excluye** las secciones dueñas de esos hechos
  (CONTEXT §2, §4, §6; PLAN §3, §6, §7), las líneas de versión (`**Versión `) y los archivos fuera del alcance.
- **Imprime:** `… candidato a hecho duro sin cita: "<fragmento>" — "<línea>"`. Nunca exit 1: el addendum de ADR-0008
  reconoce que no hay mecanismo bueno para huérfanas; esto es la ayuda ruidosa de la sesión que cierra.
- **Test:** fixture con una línea `cobertura 93 %` sin cita (sale) y otra `93 % (PLAN §6)` (no sale).

### `--estado` (Fase B, arreglo de CONTEXT §8 punto 4)
- Si `progress.json` existe, `current_target` es `null` y todas las fases están `completed` → `ejecutado (todas las
  fases); pendiente de PR o mezclado`, en vez de `en ejecución (objetivo: ?)`. No consulta git. Lo demás igual.
- **Test:** fixture `docs/deuda/X/progress.json` con `current_target: null` y dos fases `completed`.

### Fase C (bajo `--cierre`; el `plan-redactor` fija las regex finales a partir de esto)

- **Inyección para testear sin git ni reloj:** `rule_version_header(root, errors, warnings, *, last_commit_date=git_last_commit_date, is_dirty=git_is_dirty)`
  y `rule_closed_days_marked(root, errors, *, today=date.today)`. Los tests pasan funciones falsas; ningún test ejecuta
  `git`. Las funciones reales usan `subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=root)` y
  `git status --porcelain -- rel`; si `git` falla (ausente, sin historia, no es repo) devuelven `None` y la regla emite
  aviso "no verificable".
- **R6 · `rule_version_header`** (ADR-0007). Archivos: CONTEXT, PLAN, backlog, `docs/sesiones/*.md`. Línea
  `**Versión X.Y — D mmm AAAA.**`: su fecha ≥ fecha del último commit del archivo (`git log -1 --format=%cs -- <archivo>`).
  Archivo sin línea de versión: error solo si su último commit es posterior al 28 oct 2026 (ADR-0007 punto 5). Cambios
  sin commitear → **aviso**, nunca error (la versión se sube en el cierre, una vez al día; un error aquí bloquearía todo
  hook a media jornada). `git` ausente o sin historia (clon superficial en CI) → aviso "no verificable", nunca rojo falso.
  Un commit de solo erratas sin subir versión sale en rojo: es lo que ADR-0007 punto 4 pide. Expresión de la línea:
  `^> \*\*Versión (\d+)\.(\d+) — (\d{1,2}) (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic) (\d{4})\.\*\*`.
  `is_dirty` solo añade un aviso: nunca suspende la comparación encabezado ≥ último commit.
  **Debe fallar:** encabezado "31 oct 2026" con `last_commit_date` = 2026-11-01 (1 error), con `is_dirty` = False y
  también con `is_dirty` = True (1 error + 1 aviso); `mentor.md` sin línea de versión con `last_commit_date` =
  2026-10-31. **Debe pasar:** encabezado "1 nov 2026" con último commit 2026-11-01; el mismo con `is_dirty` = True
  (1 aviso, 0 errores); archivo sin versión con último commit 2026-10-27; `last_commit_date` = `None` (aviso "no
  verificable", 0 errores).
- **R7 · `rule_closed_days_marked`.** Solo con `--cierre` (depende de `date.today()`; en la compuerta por defecto haría
  que un PR se pusiera rojo por el paso del tiempo). Tablas de PLAN §3 cuya primera celda es `Dow N [mes]`; el mes se
  hereda de la última fila que lo nombra; el **año se infiere por monotonía** (mes menor que el anterior ⇒ año + 1),
  partiendo del año de la línea de versión (si se tomara el año del encabezado para toda la tabla, la semana del 28 dic
  al 2 ene fallaría). Toda fila con fecha anterior a hoy debe tener `Cierre` con la forma `[✔◐✘] N`. Filas
  `(se fecha …)` se ignoran. Opcional: que exista `docs/bitacora/AAAA-MM-DD.md` para la N de la marca. Primera celda:
  `^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom) (\d{1,2})(?: (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic))?`; celda `Cierre`:
  `^[✔◐✘] \d{1,2}$`. Columna `Cierre` localizada por el encabezado de cada tabla. **Debe fallar:** con `today` = 2026-11-03,
  tabla con `| Lun 2 | … | |` (Cierre vacío). **Debe pasar:** con `today` = 2026-11-01, la tabla de Bogotá de hoy (la
  fila del día no necesita marca); la tabla "Días cerrados"; una fila `| Sáb 2 ene | … | ✔ 2 |` tras `| Jue 31 dic |`
  con encabezado de 2026 (el año salta a 2027 por monotonía y no se considera cerrada sin marca con `today` = 2026-12-31).

## 4. Tests (`tests/test_check_docs.py`, AGENTS §5)

- Helper `make_repo(tmp_path, **files) -> Path` que escribe `docs/PLAN.md`, `docs/CONTEXT.md`, `docs/backlog.md`,
  `docs/sesiones/README.md` y `.claude/commands/*.md` mínimos pero válidos (una tabla de bloques con `B-FUTURO` y
  `B-HIGIENE`, una fila `Deadline`, una tabla de backlog con columna `Decisión`), y sobrescribe lo que cada test pase.
- Por regla: al menos un test que falla y uno que pasa, con los casos de las secciones 2 y 3, afirmando sobre el
  **número** de errores y sobre que el mensaje contiene el identificador de la regla (`R2`, `R4`…) y el `archivo:línea`.
  Prohibido afirmar sobre el texto completo del mensaje.
- Un test `test_repo_is_green` que corre todas las reglas bloqueantes sobre la raíz real del repo y exige 0 errores:
  es la afirmación "en verde sobre el repo de hoy". No corre `git`.
- Fixtures con el texto viejo (decisión 3): fila BE-08 del 30 oct, fila BE-09 del 31 oct, encabezado y punto 2 del
  CONTEXT §8 del 31 oct. Son la evidencia de que las reglas habrían atrapado lo que se corrigió a mano.

## 5. Fases propuestas al `plan-redactor` (él fija archivos, orden y mensajes de commit)

| Fase | Contenido | Archivos | Prioridad |
|---|---|---|---|
| A | Cambios transversales (sección 1); R2, R3, R4, R5; tests; `mypy.files`; mensaje de éxito | `scripts/check_docs.py`, `tests/test_check_docs.py`, `pyproject.toml` | Primera |
| B | R8, R9, `--estado` | `scripts/check_docs.py`, `tests/test_check_docs.py` | Segunda |
| C | R6, R7 bajo `--cierre`, con inyección de git y reloj | mismos | Tercera |

Las tres fases corren el 1 nov (decisión de David). Si al cierre del día una fase no está auditada, el ítem cierra con lo
auditado y el resto nace como `AF-02` en el backlog; ninguna fase a medias cruza de día.

Criterio de aceptación de cada fase (ADR-0005, trinquete): pytest en verde con los tests nuevos; `ruff` 0 en los
archivos tocados y total ≤ 362; `mypy` 0 en `scripts/check_docs.py` y total ≤ 44 (el archivo entra nuevo a `mypy.files`,
así que cualquier error suyo subiría el total: no se admite); `lint-imports` 4 KEPT; cobertura ≥ 93 % (no cambia:
`scripts/` no se mide); `python scripts/check_docs.py` exit 0 sobre el repo; `python scripts/check.py` con el mismo
resultado que antes salvo el paso "docs".

## 6. Fuera de alcance

YAML estricto del frontmatter de agentes; cualquier cambio en `.claude/` o en `scripts/check.py`; cobertura de
`scripts/`; nuevas dependencias; edición de CONTEXT, PLAN o backlog por el ejecutor (decisión 3); implementación de R6/R7
si al cierre del día no está auditada (→ `AF-02`). Los hallazgos que surjan van a `docs/backlog.md` en el cierre, no al código de paso.

## 7. Para la bitácora del día (lo escribe la sesión Mentor en el cierre)

R2 y R4 atraparon cosas reales antes de existir: siete filas del backlog con decisiones en prosa (bloques dentro del
calificador) y el CONTEXT §8 del 31 con días y con fecha en el título; detectadas con el `grep` equivalente durante la
especificación, corregidas en el primer commit de `item/af-01` por David, y conservadas como fixtures que fallan.

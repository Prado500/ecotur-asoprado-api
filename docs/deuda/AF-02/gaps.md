## Auditoría Fase A — 2026-11-06

**Veredicto Fase A: PASS (0 bloqueantes, 14 opcionales).**

Commit de fase `dc57ac0` (padre `9121f27`), progreso `2c4d63a`, rama `item/AF-02`, árbol limpio antes de escribir este bloque.
No es la última fase: la "Verificación final" completa toca a la Fase B; aquí corrí V1, V4, V7, V8 y V10.

### Compuerta re-ejecutada

`./venv/Scripts/python.exe scripts/check.py`, exit 1:

```text
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
526 passed, 5 warnings in 19.48s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Frente a la línea base: 438 → 526 passed (+88), cobertura 96.11 % = 96.11 %, 4 KEPT = 4, ruff 9 = 9 y mypy 5 = 5, con los conjuntos exactos de la decisión 7 (mismas rutas y líneas). Archivos de la fase, por separado: `2 files already formatted`, `All checks passed!`, `Success: no issues found in 1 source file` (dos veces). El rojo es el heredado de A4/BE-32.

### Contraste con el plan

| Punto | Resultado | Evidencia |
|---|---|---|
| Mensaje del commit | Idéntico | `diff` de `git log -1 --format=%B dc57ac0` contra `plan.md:316-331`: sin diferencias |
| Archivos | Solo los de la fase | `git show --name-only`: `scripts/check_docs.py`, `tests/test_check_docs.py`; `2c4d63a`: handoff y `progress.json` |
| Cambio exacto 1 | Literal | El bloque de `plan.md:161-209` está tal cual en el commit (comprobado por programa: `True`) |
| Cambios 2 y 3, y E0.2 | Presentes | `scripts/check_docs.py:575`, `:25-26`, `:547-549` |
| Tests | Exigidos, por conteo | `--collect-only`: 16, 42, 4, 4, 4, 4, 1, 2, 1, 9 y 1 = 88; `git show` borra 0 líneas |
| RED | `88 failed, 148 passed` | Script de `9121f27` con tests de `dc57ac0`: 86 y 1 `AttributeError`, 1 `IndexError` |
| `--estado` antes y después | 4 falsos `con gaps` → 9 `PASS` | V8: `9` y `0`; script de `9121f27` con `--root` al repo: A9, AF-05, BE-01 y SEC1 en `con gaps` |
| Fixture A, B vacío y C por CLI | Tres líneas, exit 0, sin traceback | `A: … PASS`, `B: … ilegible`, `C: … con gaps`, `exit=0` |
| V1, V4, V7, V10 | `0`, `0`, `0` y `0`, vacío | Comandos de `plan.md:521-544` |
| `progress.json` | Correcto | `dc57ac0` real, `Fase_A` `completed`, `current_target` `Fase_B`, `last_handoff` presente, `edit_rules` sin cambios en el diff |

### Mutantes (copia nueva desde objetos git, `PYTHONDONTWRITEBYTECODE=1`, M0 antes y después: `236 passed`)

| Id | Plan | Medido | Id | Plan | Medido |
|---|---|---|---|---|---|
| MA1 | 49 | 49 | MA9 | 2 | 2 |
| MA2 | 63 | 63 | MA10 | 4 | 4 |
| MA3 | 10 | 10 | MA11 | 4 | 4 |
| MA4 | 3 | 3 | MA12 | 1 | 1 |
| MA5 | 1 | 1 | MA13 | 48 | **46** |
| MA6 | 2 | 2 | MA14 | 1 | 1 |
| MA7 | 2 | 2 | MA15 | 1 | 1 |
| MA8 | 1 | 1 | MA16 | 1 | 1 |

Los 16 mueren; la regla del plan es "al menos 1 `failed`" (`plan.md:154`). El script del ejecutor aplica lo que dice el plan: los mismos cambios que la lista de la sonda del planificador (`scratchpad/probes/mutants.txt:14-29`), incluidos MA3 (sentencia `pass`) y la lógica de MA13.

Mutantes propios, fuera de los 16:

| Mutante | Resultado | Mutante | Resultado |
|---|---|---|---|
| X1 bloque con `search`, sin `^` | **sobrevive** | X13 solo `PASS` | 25 failed |
| X2 bloque con `^#+` | **sobrevive** | X14 ternario invertido | 63 failed |
| X3 bloque sin `Fase ` | **sobrevive** | X15 sin línea → `pass` | 19 failed |
| X4 bloque con `re.I` | **sobrevive** | X16 sin bloques → `pass` | 1 failed |
| X5 veredicto con cualquier calificador | **sobrevive** | X17 vacío → `no_verdict` | 4 failed |
| X6 `Fase \w+` | 2 failed | X18 `not text` | 2 failed |
| X7 sin `- ` | 3 failed | X19 etiquetas `no_verdict` y `unreadable` intercambiadas | **sobrevive** |
| X8 cualquier viñeta o sangría | **sobrevive** | X20 sin `if gaps.exists()` | 1 failed |
| X9 espacios libres tras los dos puntos | **sobrevive** | X21 `split("\n")` | sobrevive (equivalente salvo separadores exóticos) |
| X10 sin negrita en la palabra | 6 failed | X22 lectura `utf-8-sig` | **sobrevive** |
| X11 sin negrita en los dos puntos | 3 failed | X23 otro texto en `STATE_AUDIT` | **sobrevive** |
| X12 sin negrita inicial | 11 failed | X24 otro texto en tres etiquetas | **sobrevive** |

### Corpus real

Los 27 bloques de los 9 `gaps.md`, cortados por el siguiente, contra un lector independiente: sin diferencias. Sin veredicto: A9 A y AF-01 A, B y C; `pass` los otros 23; ninguno `gaps`. Con dos candidatas, gana la correcta: BE-15 F (l.575 frente a l.737) y BE-33 D (l.176 frente a l.290). Las tres líneas con la palabra que `VERDICT_RE` rechaza son `BE-15:737`, `BE-33:258` y `BE-33:290`. Ninguna tiene BOM. Hay 34 líneas de valla de código y 0 veredictos o encabezados dentro, como afirma `plan.md:109`.

### Hallazgos

Ninguno incumple el plan, E0, la adenda ni deja hoy un resultado incorrecto en los datos reales. Los que dependen de la regex la tienen dictada por `plan.md:162-167`: no son errores del ejecutor.

- [OPCIONAL] — Fase A — Contradicción. El encabezado del módulo promete `exit 0 siempre` para los comandos informativos, `--estado` incluido, y `estado()` declara la excepción de E0.2. No es bloqueante: ya era falso antes de la fase (`git blame` a `968dc25`), así que este cambio no lo volvió falso (`plan.md:140`), y E0.2 nombra solo la docstring de `estado()`. La Fase B deja `--estado` fuera de alcance (`plan.md:492`): corregirlo allí pide una enmienda; si no, AF-08 — `scripts/check_docs.py:19` frente a `:547-549`; medido con `progress.json` directorio: `PermissionError: [Errno 13]`, `exit=1`.
- [OPCIONAL] — Fase A — Contradicción con la letra de AGENTS §4 (docstrings en inglés): las dos líneas nuevas del encabezado del módulo están en español. No lo bloqueo porque es el texto literal de `plan.md:215-216`, aprobado, y el resto de ese encabezado ya está en español; `__doc__` no se usa como ayuda (`description=` propia, `:801`), así que la excepción (c) no aplica. Decide David — `scripts/check_docs.py:25-26`.
- [OPCIONAL] — Fase A — Contradicción de docstrings: "findings are never read… cannot change the result" y "a finding that merely mentions a verdict is not one" prometen más de lo que hace el anclaje. Una línea que empieza como un veredicto y va antes del real gana: `- Veredicto: PASS del auditor previo…` y luego `Veredicto Fase A: GAPS (1 bloqueantes).` da `pass`; lo mismo con `Veredicto: PASS anterior.` y con `- x Veredicto: GAPS` o `\x0c` antes de un PASS (da `gaps`, porque `splitlines` corta ahí). Es la regla "primera línea" de la decisión 2, 0 casos reales, y la línea de contrato como primera del bloque lo cierra. Quedan expuestos los bloques con veredicto al final, como `AF-01:177` y `BE-02:58` — `scripts/check_docs.py:493`, `:510-511`.
- [OPCIONAL] — Fase A — Falso PASS por veredicto heredado: una auditoría posterior bajo un encabezado que `AUDIT_BLOCK_RE` no reconoce no abre bloque, y manda el veredicto anterior. `PASS` y luego `GAPS` bajo `## Auditoría Fase_B` (las claves de `progress.json` son `Fase_B`), `## Auditoria Fase B`, `## Re-auditoría Fase A`, `### Auditoría Fase B`, dos espacios tras `##` o la í en NFD: los seis dan `pass`. Los 27 bloques reales usan la forma correcta y `.claude/agents/handoff-auditor.md:45` la fija; `.opencode/agent/handoff-auditor.md:44-46` no (residual ya anotado en `plan.md:557`). Destino: rama de AF-07 — `scripts/check_docs.py:487`.
- [OPCIONAL] — Fase A — Formas razonables que salen `sin veredicto`: `**Veredicto**: PASS`, `* **Veredicto:** PASS`, `  - **Veredicto:** PASS`, `Veredicto:PASS`, dos espacios o NBSP tras los dos puntos, `` Veredicto: `PASS` ``, `> **Veredicto: PASS` y `### Veredicto: PASS`. El fallo es conservador, no inventa un resultado, y `plan.md:107-108` lo acepta — `scripts/check_docs.py:490-492`.
- [OPCIONAL] — Fase A — `\b` admite `Veredicto: PASS-ish` y `Veredicto: PASS/GAPS` como `pass`. Cumple la "palabra completa" de la adenda 2; es de la misma familia que `PASS (2 bloqueantes)`, declarado en `plan.md:106` — `scripts/check_docs.py:491`.
- [OPCIONAL] — Fase A — BOM: un archivo con BOM y el encabezado en la línea 1 da `no_verdict` con veredicto `PASS`, y un archivo con solo BOM da `no_verdict` aunque la docstring dice que uno en blanco es `unreadable`. Lo produce Windows PowerShell 5 (`Out-File -Encoding utf8`). Los 9 reales no tienen BOM y empiezan por un título `# `, y con título el resultado es correcto (medido). `encoding="utf-8"` es texto del plan — `scripts/check_docs.py:518`, `:521`; X22 sobrevive.
- [OPCIONAL] — Fase A — Riesgo declarado, confirmado: una valla de código no aísla. Un encabezado citado en una valla tras el PASS da `no_verdict`, y un `Veredicto: PASS` citado en una valla antes de un GAPS da `pass`. Corpus real: 34 líneas de valla, 0 casos — `plan.md:109`.
- [OPCIONAL] — Fase A — La suite no fija varias piezas de las regex: X1, X2, X3, X4, X5, X8, X9 y X22 sobreviven (tabla de arriba). El más útil es X5: `_NOT_VERDICTS` parece proteger el calificador `de cierre`, pero tras sus dos puntos viene `el ítem`, no `PASS`, y por eso nada detecta aflojar la regex para que `Veredicto de cierre: PASS` cuente. X1 tampoco tiene un caso con `## Auditoría Fase` a mitad de línea. El código de hoy es correcto en todos (medido): es protección contra regresiones, no un defecto — `tests/test_check_docs.py:600`.
- [OPCIONAL] — Fase A — Las etiquetas visibles no están fijadas: intercambiar `sin veredicto` e `ilegible` (X19), cambiar `con gaps` (X24) o el prefijo (X23) deja `236 passed`, porque los tests leen las mismas constantes. Solo `labels["pass"]` es literal. Sigue AGENTS §5 y `plan.md:223-224` (no afirmar sobre texto en español), y el texto de hoy es correcto por CLI: es el coste de esa regla, no un olvido — `tests/test_check_docs.py:758-762`.
- [OPCIONAL] — Fase A — MA13 da 46 y no 48: causa localizada, no es un defecto. La sonda construía los bloques de `reads_only_the_last_block` con `{body}\n\n` (`scratchpad/probes/tests_a.py:82-85`), así que su última línea es blanca y la lógica antigua falla también en `gaps-then-pass` y `none-then-pass`. El test comprometido termina en `{last}\n`. Medido: sonda + MA13 = `48 failed` (3 en esa función); commit + MA13 = `46 failed` (1); commit con solo ese fixture cambiado a `\n\n` = `48 failed`, exactamente con `[gaps-then-pass]` y `[no-line-then-pass]`, y `236 passed` sin mutante. El plan no dicta ese texto, así que no hay desviación. Ningún fixture de la suite deja una línea en blanco tras el veredicto al final del archivo, el caso de `verificacion.md:110`; el parser lo resuelve bien (medido, `pass`) y no hace falta tocarlo. Esto resuelve la duda de `handoff-Fase_A.md:138-140` — `tests/test_check_docs.py:656`.
- [OPCIONAL] — Fase A — Otras dos cifras del plan no coinciden, ya declaradas en el handoff: `plan.md:270` dice que el RED es "todos por función ausente" y son 87 `AttributeError` y 1 `IndexError` (medido); `plan.md:91` estima +51/−4 y el commit da +55/−6 (`git show --numstat`). La explicación de `handoff-Fase_A.md:147` se queda corta: los −6 son las 4 líneas de `estado()` más las 2 de docstring reemplazadas (`:25` y `:497`). Ninguna es criterio de aceptación.
- [OPCIONAL] — Fase A — Documentación ya falsa tras esta fase, con dueño en el cierre (`plan.md:145-147`): `docs/CONTEXT.md:294` y el punto (3) de `docs/backlog.md:165` dicen que `--estado` lee `PASS` en la última línea. Fuera del alcance de la fase (`plan.md:142`); basta no olvidarlos al pasar AF-02 a Hecho.
- [OPCIONAL] — Fase A — `docs/deuda/AF-02/progress.json:13` dice `Needs David's answer to P1`, y E0.1 ya la dio (`plan.md:5`, `:577`). Viene de `9121f27`, no de esta fase; puede confundir al ejecutor de la Fase B, cuya precondición está cumplida.

### Medido y leído

**Medido:** compuerta; ruff y mypy de los dos archivos; mensaje y archivos del commit; bloque de código del plan contra el commit; RED; conteo de tests; los 16 mutantes, 24 propios y variantes de MA13; causa de MA13; `--estado` antes y después; V1, V4, V7, V8 y V10; fixtures por CLI; 54 entradas de `read_last_audit`; los 27 bloques reales; vallas, BOM y CRLF de los 9 archivos; traceback de `progress.json`; `--cierre` (3 errores R6, los esperados hasta la Fase B y el cierre).
**Solo leído:** `plan.md`, `verificacion.md` y su adenda; `handoff-Fase_A.md`; el script del ejecutor y la lista de la sonda; los prompts de auditor de `.claude` y `.opencode`; `docs/CONTEXT.md:294`, `docs/backlog.md:165`.
**No medido:** un `gaps.md` bloqueado o sin permiso de verdad (solo un directorio, que en Windows da `PermissionError`); el BOM generado por PowerShell 5 (escribí los bytes a mano); el CI en `ubuntu-latest`.

## Auditoría Fase B — 2026-11-06

**Veredicto Fase B: PASS (0 bloqueantes, 11 opcionales).**

Auditado: `HEAD` = `23af07b` (progreso y handoff) sobre `19d4efa` (código y tests), rama `item/AF-02`, árbol limpio antes de escribir este bloque, sin cambios ajenos. Última fase del plan: corrí V1-V11. Sin cambios de código ni commit por esta auditoría.

### Compuerta re-ejecutada

`./venv/Scripts/python.exe scripts/check.py`, exit 1:

```text
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
547 passed, 5 warnings in 18.70s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Frente a la línea base: 438 → 547 passed (+88 de A, +21 de B), cobertura 96.11 % = 96.11 %, 4 KEPT = 4, ruff 9 = 9 y mypy 5 = 5, con los conjuntos exactos de la decisión 7 (mismas rutas y líneas, `ruff check --output-format=concise .` y `mypy app`). Archivos de la fase, por separado: `2 files already formatted`, `All checks passed!`, `Success: no issues found in 1 source file` (dos veces). El rojo es el heredado de A4/BE-32.

### Contraste con el plan

| Punto | Resultado | Evidencia |
|---|---|---|
| Mensaje del commit | Idéntico | `diff` de `git log -1 --format=%B 19d4efa` contra `plan.md:495-513`: sin diferencias |
| Archivos | Solo los de la fase | `git show --name-only`: `scripts/check_docs.py`, `tests/test_check_docs.py`; `23af07b`: handoff y `progress.json`. `pyproject.toml`, `app/`, `.claude/` y `.opencode/` fuera de `git diff --name-only e4e7d43 HEAD` |
| Cambios 1 a 7 | Literales | Bloques de `plan.md:345-370`, `:381-402`, `:408-413`, `:419-425` en el script, comprobado por programa: `True` en los cuatro; import, `%cI`, docstring de `git_last_commit_date`, `today=project_today` y `:823`, también |
| E0.1 (B1) y E1 | Presentes | `scripts/check_docs.py:583`; `:19-20`. E1 en dos líneas conserva `excluyentes entre sí y con la pasada bloqueante`, que seguía siendo cierto: no contradice la enmienda, declarado en `handoff-Fase_B.md:190-195` |
| Tests | Exigidos, por conteo y texto | Diff: 6, 5, 4, 3, 1, 5 y 1 casos en las funciones del plan = 21 nuevos + 4 existentes en `test_git_last_commit_date`; más `test_cierre_flag…` editado: los 5 editados de E0.4. Se borran 5 líneas, ninguna de un test de R7 |
| RED | `21 failed, 236 passed` | Script de `dc57ac0` con tests de `19d4efa`, copia nueva; los 21 son los que lista `plan.md:458-460`. Causas 8 `ValueError`, 5 `AttributeError`, 4 `AssertionError`, 4 `assert`, como dice el handoff; los 5 de R6 fallan con `Invalid isoformat string: '2026-10-27T12:00:00-05:00'`, como declara su residual |
| `progress.json` | Correcto | `19d4efa` real, `Fase_B` `completed`, `current_target` JSON `null` (última fase, forma de `eaf2303`), `last_handoff` presente, `edit_rules` sin cambios desde `9121f27`; JSON válido; `--estado` lo lee como ejecutado |
| Precondición | Cumplida | `plan.md:5`; `origin/develop` y `merge-base` = `e4e7d43` (refs locales, sin `fetch` mío) |

Verificación final, `plan.md:521-546`: V1 `0`; V2 `0`; V3 `%cs` `0` y `0`, `%cI` `2` y `2`; V4 `0`; V5 `1`; V6 `1` y `1`; V7 `0` y `0`; V8 `9` y `0`; V9 `257 passed in 3.97s`; V10 `docs/deuda/AF-02/gaps.md`; V11 la compuerta de arriba. Las once coinciden.

### Mutantes (copia nueva desde objetos git de `19d4efa`, `PYTHONDONTWRITEBYTECODE=1`; M0 antes y después: `257 passed`)

| Id | Plan | Handoff | Medido | Id | Plan | Handoff | Medido |
|---|---|---|---|---|---|---|---|
| MB1 | 5 | 5 | 5 | MB9 | 2 | 2 | 2 |
| MB2 | 2 | 2 | 2 | MB10 | 3 | 3 | 3 |
| MB3 | 1 | 1 | 1 | MB11 | 3 | 3 | 3 |
| MB4 | 9 | 9 | 9 | MB12 | 7 | 7 | 7 |
| MB5 | 4 | 4 | 4 | MB13 | 13 | 13 | 13 |
| MB6 | 6 | 6 | 6 | MB14 | 2 | 2 | 2 |
| MB7 | 1 | 1 | 1 | MB15 | 5 | 5 | 5 |
| MB8 | 3 | 3 | 3 | | | | |

Los 15 mueren con los conteos del plan. Escribí mis propias ediciones desde la tabla del plan, incluida MB6 con otras variables. El script del ejecutor aplica lo que dice el plan: mismos textos que `scratchpad/probes/mutants.txt:32-50`, exige una sola coincidencia por edición y corre M0 antes y después. Su única diferencia de método con esta copia es que parte del árbol de trabajo, no de objetos git.

Mutantes propios, fuera de los 15:

| Mutante | Resultado | Mutante | Resultado |
|---|---|---|---|
| Y1 `_utc_now`: hora local etiquetada como UTC | **sobrevive** | Y14 anchor = versión + 1 día | 1 failed |
| Y2 `_utc_now`: fijo en 2000 | 1 failed | Y15 anchor = versión + 30 días | 1 failed |
| Y3 anchor = hoy | 2 failed | Y16 anchor = versión − 30 días | **sobrevive** |
| Y4 sin `abs` | 6 failed | Y17 corte de R6 con `>=` | 1 failed |
| Y5 `except` → `break` | 1 failed | Y18 R6 con `<=` | 5 failed |
| Y6 mes conservado entre tablas | 1 failed | Y19 R7 con `<=` | 3 failed |
| Y7 `hours=-6` | 3 failed | Y20 `ValueError` de `fromisoformat` → `None` | **sobrevive** |
| Y8 `replace(tzinfo)` | 8 failed | Y21 reloj en día UTC | 2 failed |
| Y9 sello reetiquetado como UTC | 1 failed | Y22 R6 en día UTC | 5 failed |
| Y10 `%aI` | 7 failed | Y23 sello sin offset | 4 failed |
| Y11 candidatos ±2 años | 1 failed | Y24 sin herencia de mes | 3 failed |
| Y12 orden `(−1, +1, 0)` | **sobrevive** | Y25 `default=anchor` | 2 failed |
| Y13 anchor = día 1 del mes de la versión | **sobrevive** | | |

### `--cierre` diferencial y reloj

Mismo `HEAD` `23af07b`, `--root` al repo, script de `dc57ac0` frente a `HEAD`; ambos exit 1. `docs/CONTEXT.md` sigue en `d7de2d6` (`2026-11-06T00:37:13Z`). `diff` de las dos salidas, completo:

```text
2d1
<   - docs/CONTEXT.md:8: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 3.6 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` ("
```

Quedan `docs/PLAN.md:3` y `docs/backlog.md:3`; sin líneas R7 en ninguna. Es la única diferencia que permite `plan.md:485-487`.

Reloj, fixture de `make_repo` sin git con `| Vie 6 nov | hoy | |` sin marca y versión `6 nov 2026`, medido a las 17:53 de Bogotá:

```text
=== TZ=AAA-14
local 2026-11-07T12:53:43 | utc 2026-11-06T22:53:43+00:00 | bogota 2026-11-06T17:53:43-05:00
A: docs/PLAN.md:16: R7: fila de PLAN §3 cerrada sin marca en Cierre — exit=1
B: Documentación coherente — exit=0
=== TZ=UTC0
local 2026-11-06T22:53:44 | utc 2026-11-06T22:53:44+00:00 | bogota 2026-11-06T17:53:44-05:00
A: Documentación coherente — exit=0
B: Documentación coherente — exit=0
```

(Salidas abreviadas: las dos llevan además 4 avisos R6 `no verificable`.) `TZ=COT5` da 0 y 0. **El cruce de las 19:00 con `TZ=UTC0` no está medido:** eran las 18:02 en Bogotá al terminar esta auditoría, y estas líneas no lo simulan.

### Sondas sin hallazgo

- `_date_near`, todas las fechas ancla de 2020 a 2035 con cada día y mes, 2 138 904 pares, contra un oráculo con ±5 años: 0 diferencias fuera del 29 feb. Empates: 1460, todos a 183 días, con 366 entre candidatos, y todos al año anterior, tanto si el anterior es `anchor.year − 1` como `anchor.year`. La docstring dice la verdad.
- 29 feb: un solo candidato posible, `None` en 1460 de 5844 anclas; ninguna diferencia con el oráculo. v`2 ene 2027` → `2028-02-29`, v`31 dic 2026` → `None`, como dicta `plan.md:67`. Años límite 1 y 9999: sin excepción.
- Copia del PLAN real, 81 versiones del 23 oct 2026 al 11 ene 2027, comparando el día de la semana de cada fila con la fecha calculada: script nuevo 0 diferencias, con y sin filas de diciembre y enero; script de A 165 y 209 filas erradas, todas en las 11 versiones de 2027.
- Copia del PLAN real con `Lun 2` sin marca y filas `Lun 28 dic`, `Vie 1 ene` sin marca: v`2 ene 2027`, hoy 5 ene: de 0 a **4**; v`31 dic 2026`: 4 y 4; v`5 nov 2026`: 4 y 4; v`11 ene 2027`, hoy 12 ene: de 0 a **4**. Los errores del script nuevo son los mismos en los cuatro escenarios, y todos son filas de verdad sin marca (`:137`, `:141` `Vie 6`, y las dos añadidas). Coincide con `plan.md:128-129` y `verificacion.md:154`. PLAN real, las mismas 15 fechas.
- `project_date` con `Z`, `+00:00`, `-00:00`, `-05:00`, `+14:00`, `-12:00`, fracciones, cruce de año y 29 feb: día correcto en todos. Commits reales, `git log --all --format=%cI`: 472, 470 con `-05:00` y 2 con `Z`, 0 que no se puedan leer.
- R6 sin línea de versión con commit `2026-10-29T00:30:00Z` (28 oct en Bogotá), por CLI con git real: script de A 4 errores `sin línea de versión`, nuevo 0. El corte de ADR-0007 también pasa por el huso.
- `tests/test_check_docs.py` bajo `TZ=UTC0`, `AAA-14` y `XXX+12`: `257 passed` en los tres.

### Hallazgos

Ninguno incumple el plan, E0, E1, la adenda ni AGENTS, ni deja hoy un resultado incorrecto en los datos reales.

- [OPCIONAL] — Fase B — `progress.json:13`: el campo `description` de `Fase_B` cambió (`Needs David's answer to P1.` → `P1 resolved: B1, fixed offset (E0.1).`). No es bloqueante: `edit_rules` reserva a la sesión que ejecuta cuatro campos y no nombra este, así que ni lo autoriza ni lo prohíbe; `plan.md:604` encarga avisar al ejecutor y dice que "la regla de edición reserva ese archivo al ejecutor", y fue esa sesión quien lo editó; el texto es verdadero (E0.1; 21, 5, 15, 547, ruff 9 y mypy 5, medidos), el JSON es válido y está declarado en `handoff-Fase_B.md:204-205`. Tampoco está en "Cambios exactos": la orden salió del orquestador, no del plan. Lo único que queda por decidir es si `edit_rules` debe nombrar `description` en el próximo ítem — `git show 23af07b -- docs/deuda/AF-02/progress.json`.
- [OPCIONAL] — Fase B — Pendiente de medición: el cruce de las 19:00 con `TZ=UTC0` sigue sin medir por CLI, ni en el handoff (17:41) ni aquí (17:53). `plan.md:489` solo lo exige "si se ejecuta tras las 19:00", y `handoff-Fase_B.md:166-168` lo declara, así que no hay incumplimiento; aun así, E0.4 lo da por medido en el handoff, y la adenda 5 lo pedía. Lo cubren `_utc_now` congelado, MB2, MB3, MB4 y, por el mismo mecanismo, `TZ=AAA-14`. Para cerrarlo basta repetir el reloj de arriba tras las 19:00 de Bogotá, antes del PR, con la fila del día: esperado A → 1 error R7, nuevo → 0.
- [OPCIONAL] — Fase B — Excepción nueva, medida: un commit con desfase de 24 h o más lanza `ValueError` donde `%cs` no lo hacía, y `--cierre` termina con traceback. Commit fabricado con `hash-object --literally`, `+2500`, `%cI` = `2025-11-07T01:37:13+25:00`: script de A `Documentación coherente`, exit 0; nuevo `ValueError: offset must be a timedelta strictly between…`, exit 1. Lo mismo a nivel de función con `+2400`, `-2400`, `-9959`, `+9999` y `+051800`; `+0060` y `+1060` se leen bien. No hay caso real: los 472 commits se leen, `git commit` no los produce (con `GIT_COMMITTER_DATE="1762389433 +2500"` escribe `-05:00`) y `git fsck` los rechaza (`badTimezone`). La línea `project_date(datetime.fromisoformat(out))` es texto de `plan.md:375`. Otras salidas inesperadas (`garbage`, varias líneas, `gpg:` delante) ya lanzaban `ValueError` antes: no empeoran. Un sello sin offset (`2026-11-06`), que `%cI` no emite, sí cambia: `project_date` lo lee como hora local y da 5 nov con `TZ=UTC0` y `AAA-14`, 6 nov con `COT5`. La docstring de `git_last_commit_date` no declara el `ValueError`, y R6 promete "git no disponible son avisos, nunca error"; Y20 sobrevive. Destino sugerido: AF-08, capturar `ValueError` y devolver `None` — `scripts/check_docs.py:634`.
- [OPCIONAL] — Fase B — `_utc_now` no está fijado: Y1 (`datetime.now().replace(tzinfo=UTC)`) deja `257 passed`, porque los tests lo congelan; en una máquina fuera de UTC ese mutante puede dar el día equivocado. Y2 (fijo en 2000) solo cae por `test_cierre_flag_fails_on_unmarked_closed_day_and_keeps_warnings`, que usa el reloj real. Es consecuencia de `plan.md:489-490`, y el código de hoy es correcto por CLI: protección contra regresiones — `scripts/check_docs.py:602-603`.
- [OPCIONAL] — Fase B — El empate solo está probado en una dirección: `tie-goes-to-earlier-year` es v`1 jun 2028` (candidatos `anchor.year − 1` y `anchor.year`). Y12, con los candidatos en orden `(−1, +1, 0)`, sobrevive y resolvería mal v`1 dic 2027`, fila `1 jun`. El código de hoy da `2027-06-01`, correcto (medido, y los 1460 empates). Un caso más lo fija — `tests/test_check_docs.py:1152`.
- [OPCIONAL] — Fase B — La suite no distingue el ancla exacta: Y13 (día 1 del mes de la versión) e Y16 (versión − 30 días) sobreviven; solo el caso de empate delata un ancla posterior (Y14, Y15). La diferencia solo aparece cerca de los 6 meses, y en el PLAN real la distancia máxima es de 13 días (`plan.md:105`): sin efecto hoy — `scripts/check_docs.py:836`.
- [OPCIONAL] — Fase B — Riesgo declarado, confirmado sin reclasificar (regla de la adenda 4, `plan.md:104-105`): a más de unos 6 meses de la versión el año se equivoca. v`2 ene 2027`, tabla jun-ago 2026: `2027-06-01`, `2027-07-01`, `2026-08-01`, con dos filas pasadas ocultas como futuras; una tabla de un año entero no queda en orden; una versión atrasada da falsos errores (v`1 jul 2026`, `Lun 4 ene` → `2026-01-04`). El barrido de las 81 versiones de la vida del proyecto no lo alcanza, y la entrega es el 11 ene 2027 `(CONTEXT §2)`.
- [OPCIONAL] — Fase B — E1 sigue prometiendo de más, aunque menos: el encabezado cubre R8 y R9 con "exit 0, salvo la excepción declarada en `estado()`", y `--copias` y `--huerfanas` terminan con traceback y exit 1 con un `docs/backlog.md` no UTF-8 (`UnicodeDecodeError`) o una raíz vacía (`FileNotFoundError`); `main()` dice también `0 coherent or informative command`. El texto es el de E1, decidido por David y aplicado bien; ese comportamiento no es de esta fase. Destino sugerido: AF-08 — `scripts/check_docs.py:19-20`, `:887`; medido por CLI.
- [OPCIONAL] — Fase B — `project_today` es pública y su docstring es de una línea, sin `Returns` (AGENTS §4). No lo bloqueo: es el texto literal de `plan.md:369` — `scripts/check_docs.py:606-608`.
- [OPCIONAL] — Fase B — Documentación fuera del alcance que sigue describiendo lo anterior, con dueño: `docs/backlog.md:165` (año por la línea de versión, fecha local, `--estado` por la última línea) y `docs/CONTEXT.md:294`, en el cierre (`plan.md:145-147`); los ids `year-by-monotony`, `year-resets-per-table` y `year-jump-*`, en BE-32 (`plan.md:558`). El resto dice la verdad tras el cambio, leído contra lo medido: módulo R6 y R7, `PROJECT_TZ`, `project_date`, `git_last_commit_date` salvo lo ya anotado, `_date_near`, `_dated_rows`, `rule_closed_days_marked`, `ADR-0008:136-137`, `docs/sesiones/README.md:51`.
- [OPCIONAL] — Fase B — Cifra del plan que no coincide, declarada: `plan.md:91` estima +69/−22 y el commit da +79/−29 (`git show --numstat`). `handoff-Fase_B.md:197-198` no localiza el origen; parte está en que la copia de la sonda (`scratchpad/probes/script_after_b.txt`) no llevaba E1 ni el texto de R6 y R7 del módulo (`diff`; no reconstruí el conteo línea a línea). No es criterio de aceptación.

Los opcionales 1 (E1) y 14 (`progress.json`) del bloque de la Fase A quedan atendidos en esta fase; ese bloque no se edita.

### Medido y leído

**Medido:** compuerta; ruff y mypy de los dos archivos y conjuntos heredados; mensaje, archivos y numstat del commit; bloques del plan contra el script; RED y sus causas; 15 mutantes y 25 propios; `--cierre` diferencial; reloj con `TZ=AAA-14`, `UTC0` y `COT5`; V1-V11; `_date_near` exhaustivo; tablas largas; copia real del PLAN; `project_date` con 18 formas; `git_last_commit_date` con 22 commits fabricados, 6 fechas por `GIT_COMMITTER_DATE` y 9 salidas simuladas; `--cierre` por CLI con `+2500`; corte de R6; `--copias`, `--huerfanas` y `--estado` con datos malos; suite bajo tres husos; JSON e historia de `progress.json`.
**Solo leído:** `plan.md`, `verificacion.md` y su adenda; `handoff-Fase_B.md`; `scratchpad/mutants_b.py` y `probes/mutants.txt`; docstrings; `ADR-0008`, `docs/sesiones/README.md:51`, `docs/backlog.md:165`, `docs/CONTEXT.md:294`; `.azure-pipelines/ci-pipeline.yml`.
**No medido:** el cruce de las 19:00 con `TZ=UTC0`; el CI en `ubuntu-latest` y la forma de su `%cI` (`+00:00` y `Z` se probaron con cadenas); un `git log` con firma GPG real (solo la salida simulada).

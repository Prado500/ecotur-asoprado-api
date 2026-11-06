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

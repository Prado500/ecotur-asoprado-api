# Handoff AF-01 Fase B

Commit: `da106b0` feat(flow): enforce ADR-0008 rules R2-R5 in check_docs.py
Base develop: `2647ea3` (`git fetch origin` hecho; `origin/develop` y `merge-base HEAD origin/develop` coinciden).
Compuerta medida con `venv/Scripts/python.exe scripts/check.py` (plan, decisión 7).

## Archivos tocados
```
 scripts/check_docs.py    | 227 ++++++++++++++++++++++++++++++++++++++++-------
 tests/test_check_docs.py | 224 ++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 417 insertions(+), 34 deletions(-)
```

## Qué cambió
- `scope_files(root)`: CONTEXT, PLAN, backlog y `docs/sesiones/*.md` ordenados. Lo usan R2, R3 y R5.
- R2 `rule_no_schedule_days` sustituye a `rule_no_days`: regex de la especificación §2 R2 (`re.IGNORECASE`), citas
  quitadas, PLAN con `lines_outside(..., {"3"})`. Un error por línea.
- R3 `rule_blocks`: alcance `scope_files`; regex sin cambios.
- R4 `DECISION_RE` con `_QUAL` copiado tal cual de §2 R4.
- R5 `rule_deadline` + `read_deadline`: `DATE_RE` y `TRIGGER_RE` de §2 R5, ventana ±40, deadline de la fila
  `| **Deadline** |` de CONTEXT.
- `main`: orden R1–R5 y mensaje de éxito nuevo; docstring del módulo actualizado.

## Compuerta (antes = después, salvo tests)
Antes (ritual de arranque) y después, el mismo RESUMEN:
```
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff format --check, ruff check, mypy
```
Conteos después: `27 files would be reformatted` · `Found 362 errors.` · `Found 44 errors in 12 files (checked 34
source files)` · `Contracts: 4 kept, 0 broken.` (vía `venv/Scripts/lint-imports`, porque el texto no sale en la
sección cuando se redirige, que es un residual ya conocido) · `219 passed, 1 warning` · `TOTAL 927 52 134 25 93%`.
Antes: 27 · 362 · 44 · 4 kept · 171 passed · 93 %. Nada empeoró.

Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
`mypy scripts/check_docs.py` → `Success: no issues found in 1 source file`.

RED: 37 failed / 37 passed antes de implementar (los 11 nuevos que ya pasaban son casos que el código viejo también
resolvía bien: R3 "pasa", los 8 "debe pasar" de R4, `**Hecho**` y la celda sin negrita). Después: 74 passed en
`tests/test_check_docs.py` (26 de A + 48 de B).

## Criterio de aceptación
- `grep -c "^def rule_" scripts/check_docs.py` → `5`.
- `grep -n "rule_no_days" scripts/check_docs.py` → vacío.
- Patrón de la verificación sobre `DECISION_RE` → `False`.
- `venv/Scripts/python.exe scripts/check_docs.py` sobre el repo, lanzado desde `C:\Users` → exit 0, `Documentación
  coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- mypy 0 en el script, total 44; ruff 0 en los dos archivos; cobertura 93 %; import-linter 4 KEPT.

## Desviaciones e interpretaciones (para el auditor)
1. **`scope_files` en minúscula.** El plan escribe `SCOPE_FILES(root)`; con la regla `N` de ruff activa, una función en
   mayúsculas da `N802`. Mismo comportamiento, otro nombre.
2. **Distancia de R5.** El plan dice "fechas cuyo `start` esté en `[t.start-40, t.end+40]`; la de menor distancia".
   Mido la distancia igual que la ventana, desde el `start` de la fecha hasta el tramo del disparador:
   `max(t.start - d.start, d.start - t.end, 0)`. Con distancia entre tramos (fin de fecha a inicio de disparador), el
   caso "debe pasar" `corte de código el 18 dic y entrega el 11 ene` elegiría `18 dic` (3 caracteres contra 4) y daría
   rojo. Con la métrica elegida gana `11 ene`, como pide la especificación.
3. **Aserciones de R5 sin texto en español.** El plan pide afirmar `sin cita` y `no legible`; AGENTS §5 prohíbe afirmar
   sobre texto en español. Distingo los tipos así: "fecha distinta" tiene `≠` en el mensaje, "sin cita" no lo tiene, y
   "deadline no legible" es el único error de R5 situado en `docs/CONTEXT.md`. La intención del plan (distinguir los
   tipos de error) se mantiene.
4. **Prioridad dentro de R5.** Si la fecha es distinta y además falta la cita, emito un solo error, el de `≠` (así el
   caso `entrega del 7 de noviembre` da 1 error, como pide el plan). Lo dejo escrito en la docstring.
5. **Tests extra, ninguno quitado:** R2 `| Lun 2 |` fuera de §3 (falla) y `Dom 4 m` (pasa); R5 año distinto (falla) e
   ISO `2027-01-11` (pasa); `test_r4_decision_re_rejects_two_blocks`; `test_main_fails_on_each_new_rule` (comprueba que
   `main` conecta R2–R5).
6. R3 recorre los bloques con `sorted(set(...))` en vez de `set(...)`, para que el orden de los errores sea
   determinista. No cambia qué detecta.

## Residuales / notas
- Los fixtures autouse de `tests/conftest.py` no dieron problemas (74 tests en ~1 s).
- En Windows, `Path.write_text` dejó CRLF en el árbol de trabajo mientras editaba; lo devolví a LF antes del commit. El
  diff solo tiene los cambios de la fase.
- `docs/deuda/AF-01/gaps.md` (auditoría de A, sin trackear) no se tocó ni se commiteó.

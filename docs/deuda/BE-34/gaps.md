# Gaps — BE-34

## Auditoría Fase A — 2026-11-14
**Veredicto Fase A: PASS (0 bloqueantes, 1 opcional).**

[OPCIONAL] — Fase A — Proceso, no código: el hook de `ruff check --fix` (`.claude/settings.json`) borró `import runpy` (F401) porque el import se escribió en una edición anterior a la del test que lo usa. El ejecutor lo volvió a añadir y el diff final es el dictado (`9 0`), así que no afecta a la fase A. Riesgo para C, D y E, que dictan imports nuevos (`SecretStr`, `func`, `UserRole`, `UserCreateByAdmin`): conviene escribir cada import en la misma edición que su primer uso, o comprobarlo con `git show --numstat` antes del commit, como hizo A — evidencia: `docs/deuda/BE-34/handoff-Fase_A.md`, sección "Residuales y dudas", viñeta 1.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `0147a71`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `d873b49` existe (`git show --stat`: `tests/test_config.py | 9 +++++++++`, 1 file changed), su padre es `c0e9096`
  y `git diff --name-only c0e9096 d873b49` → solo `tests/test_config.py`. El mensaje coincide byte a byte con el bloque
  "Commit" de la fase A, incluido el trailer `Co-Authored-By`.
- Segundo commit `0147a71` (`docs(progress): record BE-34 Fase_A completion`): solo `docs/deuda/BE-34/handoff-Fase_A.md` y
  `progress.json`. Se ajusta al protocolo: es el paso 6 de `.claude/agents/fase-ejecutor.md` (l. 62-63, mensaje
  `docs(progress): record <ID> <fase> completion`), y así se hizo en BE-39, BE-40, BE-42 y A4. No es hallazgo.
- `progress.json`: `Fase_A` `completed` con `commit: "d873b49"` (hash real); `current_target: "Fase_B"`; `last_handoff`
  presente; `edit_rules` y `allowed_statuses` intactos; las fases B–G, sin tocar (diff de `0147a71`: 8 líneas, solo esos
  campos). JSON válido.
- Cambios exactos (diff de `d873b49`): (1) `import runpy` antes de `from collections.abc import Callable`; (2)
  `ROOT_CONFTEST = …` justo tras `ENV_EXAMPLE = …`, sin línea en blanco; (3) `test_test_environment_fixes_every_setting` al
  final, con dos líneas en blanco antes, texto idéntico al dictado. Los tres están, nada más cambia.
- Criterio de aceptación: `git show --numstat --format= d873b49` → `9	0	tests/test_config.py`;
  `git grep -n 'TEST_ENVIRONMENT' -- tests | wc -l` → `1` (`tests/test_config.py:226`). UTF-8/ASCII, LF (0 `\r`).
- Fuera de alcance respetado: `conftest.py`, `REQUIRED`/`OPTIONAL_DEFAULTS` y `app/` no aparecen en el diff.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs coherente ·
  `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`. Igual a la fila A del plan y a lo que pegó el ejecutor. Frente a
  la línea base de `verificacion.md` (l. 127-131: 638 passed, 96.82 %, 61 files, 56 source files, 4 kept): +1 test, cobertura
  igual, 0 errores de ruff y mypy.
- Archivo tocado: `ruff check tests/test_config.py` → `All checks passed!`; `ruff format --check` → `1 file already formatted`;
  `mypy tests/test_config.py` → `Success: no issues found in 1 source file`.
- Mutante MA repetido por el auditor (copias nuevas de `git archive`, procedimiento común del plan):
  - sobre `d873b49`, sin la línea `CORS_ORIGINS`: `FAILED tests/test_config.py::test_test_environment_fixes_every_setting` ·
    `1 failed, 349 passed, 8 warnings` (= tabla);
  - sobre `c0e9096` con el mismo mutante: `349 passed, 8 warnings` (el hueco de BE-47 era real);
  - copia limpia de `d873b49`: `350 passed, 8 warnings` (= columna "Suite de la copia" de la fila A).
- AGENTS §5: el test nuevo no usa mocks ni fábricas, la aserción es sobre un conjunto de claves (sin texto en español) y el
  docstring dice su categoría ("Edge case"). Está anotado (`-> None`). Su único efecto lateral, que `runpy` repite
  `os.environ.update(TEST_ENVIRONMENT)` con los mismos valores, ya lo midió el plan (Análisis) y es inocuo.
- No es la última fase: la "Verificación final" del plan no aplica todavía.

## Auditoría Fase B — 2026-11-14
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `29b61b8`, rama `item/be-34`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `b08491b` existe, su padre es `4b2230a`; `git show --numstat --format= b08491b` →
  `76	0	docs/adr/0015-bootstrap-del-primer-superadmin.md` (1 file changed, solo el ADR). El mensaje (`git cat-file commit`)
  coincide byte a byte con el bloque "Commit" de la fase B, trailer `Co-Authored-By` incluido.
- Segundo commit `29b61b8` (`docs(progress): record BE-34 Fase_B completion`): solo `handoff-Fase_B.md` y `progress.json`
  (paso 6 de `fase-ejecutor`, como en la fase A). No es hallazgo.
- Texto del ADR contra el dictado: script del auditor que extrae el bloque ```` ```markdown ```` de la fase B de
  `plan.md` en `b08491b` (plan sin cambios desde `4b2230a`: `git diff 4b2230a HEAD -- docs/deuda/BE-34/plan.md` vacío),
  quita los dos espacios de sangría y sustituye `<FECHA>` por `13 nov 2026` (E0) → `IDENTICAL: True`, 76 líneas en ambos.
  Sin BOM, sin `\r`, termina en un único `\n`. La Evidencia cita `de 638 a 675 tests` (E0.3, E2 punto 1); R9 queda
  resuelto como preveía E2. La línea "Estado" lleva `13 nov 2026`, no `<FECHA>`.
- `progress.json` (diff de `29b61b8`): `Fase_B` `completed`, `commit: "b08491b"` (hash real); `current_target`
  `Fase_B` → `Fase_C`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos; las demás fases sin tocar.
  JSON válido.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`) → exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` ·
  `docs (coherencia): OK` · `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`. Igual a la fila B del plan, a lo
  que pegó el ejecutor y, frente a la línea base de `verificacion.md` (l. 127-131: 638 · 96.82 % · 61 · 56 · 4 kept), sin
  retroceso. Ningún `.py` tocado: ruff y mypy por archivo no aplican.
- Suite de la copia (directorio nuevo, `git archive b08491b`, sin `test_check*`): `350 passed, 8 warnings` (= fila B).
- Fuera de alcance respetado: `AGENTS.md`, `docs/CONTEXT.md`, el manual técnico y ADR-0013 no aparecen en el diff.
- AGENTS §7: el ADR sigue el formato Nygard (Contexto, Decisión, Consecuencias, Alternativas consideradas, Evidencia).
- No es la última fase: la "Verificación final" del plan no aplica todavía.

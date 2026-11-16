# Handoff — BE-58 · Fase A (ADR-0019 y la supersesión parcial de ADR-0017)

- Commit de la fase: `ccd84a4` — `docs(adr): add ADR-0019, no administrative account removes itself` (mensaje exacto
  del plan; bloque "Commit" de la fase A, plan l. 295-314, sin la sangría de dos espacios, comparado con `diff` contra
  `git log -1 --format=%B ccd84a4` sin la línea en blanco final → idéntico; trailer `Co-Authored-By` incluido; línea
  más larga, 67 columnas).
- Rama: `item/be-58`, sobre `62b9978` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E0.1 (ADR-0019 aceptado con el texto de la fase A, incluida la línea "Estado" de ADR-0017),
  E0.3 (decisión 3, texto del ADR y de la línea "Estado", como se recomienda), E0.5 (`AGENTS.md` no se toca). Nada en
  `app/` ni en `tests/`.

## Ritual de arranque

- `git status --short`: limpio. HEAD `62b9978`. `current_target` = `Fase_A`. No existe `gaps.md`.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `6b168e1`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `6b168e1`; `Base develop` de
  `verificacion.md` = `6b168e1`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la línea base de la
  verificación: `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1039 15 152 13 97.65%` · `726 passed, 8 warnings in 23.62s`.

## Archivos tocados (los dos de la fase)

`git show --stat --format= ccd84a4`:

```
 .../0017-ningun-superadmin-se-retira-a-si-mismo.md |  4 +-
 ...a-cuenta-administrativa-se-retira-a-si-misma.md | 71 ++++++++++++++++++++++
 2 files changed, 74 insertions(+), 1 deletion(-)
```

- `docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md` (nuevo).
- `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md`: solo la l.3 ("Estado"), que pasa a las tres líneas
  dictadas.

## Fidelidad al dictado (comprobada con `diff`, no a ojo)

- ADR-0019: plan l. 203-273, sin los cuatro espacios de la sangría de la lista y con `<FECHA>` → `16 nov 2026` (la de
  `Aprobado: 16 nov 2026`), contra el archivo escrito: `diff` sin salida → **idéntico**. 71 líneas, la más larga 120
  columnas (medido con el intérprete, UTF-8), final de línea LF y salto final.
- ADR-0017: plan l. 280-282 con la misma transformación contra las l. 3-5 del archivo: `diff` sin salida →
  **idéntico**; longitudes `[112, 116, 35]`, las que declara el plan. El resto del archivo (l. 1-2 y 4-70 de
  `HEAD~1`) contra l. 1-2 y 6-72 del nuevo: `diff` sin salida → **sin cambios**. La línea más larga del archivo (121,
  el título) ya existía en `62b9978`.
- `grep -c '<FECHA>'` en los dos archivos → `0` y `0`.

## Criterio de aceptación del plan

```
$ git diff --numstat 2cc8f73 HEAD -- docs/adr
3	1	docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md
71	0	docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md

$ git grep -l 'ADR-0019' -- docs/adr
docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md
docs/adr/0019-ninguna-cuenta-administrativa-se-retira-a-si-misma.md

$ git diff --stat 2cc8f73 HEAD -- docs/adr/0018-un-superadmin-reactiva-a-otro.md
(vacío)
```

`git diff --stat 2cc8f73 HEAD` fuera de `docs/deuda/` muestra además `docs/PLAN.md`, `docs/backlog.md` y
`docs/bitacora/2026-11-16.md`: vienen del commit de aprobación `62b9978` (`git show --stat 62b9978`), no de esta fase.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

Bloque RESUMEN literal:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Cifras literales:

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1039     15    152     13  97.65%
30 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 97.65%
726 passed, 8 warnings in 21.95s
```

Ratchet contra la línea base (726 passed · 97,65 % · ruff 0 · mypy 0 en 63 · 4 kept): igual en todo, como declara el
plan para una fase sin código. `ruff`/`mypy` sobre archivos tocados: no aplica (solo Markdown). Los tests RED no
aplican (plan: "solo documentación"); la comprobación sustituta (`--no-tests` en verde) queda cubierta por la compuerta
completa en verde.

## Residuales y dudas

- Ninguna desviación del plan. TDD no aplica a esta fase.
- Los residuales R1-R4 del plan no cambian con esta fase (R2: `AGENTS.md`, `docs/CONTEXT.md` y `docs/backlog.md` no se
  tocaron, como exige E0.5; la viñeta la edita David tras la auditoría de la fase B).

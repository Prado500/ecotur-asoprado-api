# Handoff — BE-37 · Fase A (ADR-0020 y addendum de ADR-0018)

- Commit de la fase: `4c4acb7` — `docs(adr): add ADR-0020, explicit null only where the column admits it` (mensaje
  exacto del plan; bloque "Commit" de la fase A, plan l. 223-243, sin la sangría de dos espacios, comparado con `diff`
  contra `git log -1 --format=%B 4c4acb7` sin la línea en blanco final → idéntico; trailer `Co-Authored-By` incluido;
  línea más larga, 70 columnas).
- Rama: `item/be-37`, sobre `928a16f` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 17 nov 2026.
- Enmiendas que aplican: E0.1 (`<FECHA>` = `17 nov 2026`, `<AAAA-MM-DD>` = `2026-11-17`), E0.3 (textos de ADR-0020 y
  del addendum, tal como los dicta el Anexo A), E0.7 (`AGENTS.md` no se toca). Nada en `app/` ni en `tests/`.

## Ritual de arranque

- `git status --short`: limpio. HEAD `928a16f`. `current_target` = `Fase_A`. No existe `gaps.md`.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `c3b5069`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `c3b5069`; `Base develop` de
  `verificacion.md` = `c3b5069`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la línea base de la
  verificación: `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1039 15 152 13 97.65%` · `731 passed, 8 warnings in 31.30s`.

## Archivos tocados (los dos de la fase)

`git show --stat --format= 4c4acb7`:

```
 docs/adr/0018-un-superadmin-reactiva-a-otro.md     |  9 ++++
 ...explicito-solo-donde-la-columna-admite-vacio.md | 63 ++++++++++++++++++++++
 2 files changed, 72 insertions(+)
```

- `docs/adr/0020-null-explicito-solo-donde-la-columna-admite-vacio.md` (nuevo).
- `docs/adr/0018-un-superadmin-reactiva-a-otro.md`: solo el addendum añadido al final (una línea en blanco y el bloque);
  ninguna línea previa cambia (`git diff 32b8fd4 HEAD` de ese archivo: 0 líneas borradas).

## Fidelidad al dictado (comprobada con `diff`, no a ojo)

- ADR-0020: plan l. 584-646 (Anexo A, sin la valla), con `<FECHA>` → `17 nov 2026`, contra el archivo escrito: `diff`
  sin salida → **idéntico**. 63 líneas, la más larga 120 columnas, UTF-8, LF, termina en salto de línea.
- Addendum: plan l. 652-660 con `<FECHA>` → `17 nov 2026` y `<AAAA-MM-DD>` → `2026-11-17`, contra las 9 últimas líneas de
  ADR-0018: `diff` sin salida → **idéntico**. ADR-0018 acababa en salto de línea antes del addendum.

## Criterio de aceptación

```
$ git diff --numstat 32b8fd4 HEAD -- docs/adr
9	0	docs/adr/0018-un-superadmin-reactiva-a-otro.md
63	0	docs/adr/0020-null-explicito-solo-donde-la-columna-admite-vacio.md
$ git grep -n "<FECHA>\|<AAAA-MM-DD>" -- docs/adr
(sin salida, exit 1)
```

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

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

- pytest: `731 passed, 8 warnings in 30.86s` (0 failed), como dice la tabla de fases.
- Cobertura: `TOTAL 1039 15 152 13 97.65%` (= línea base).
- ruff format: `68 files already formatted` · ruff check: `All checks passed!` (0) · mypy:
  `Success: no issues found in 63 source files` (0) · import-linter: `Contracts: 4 kept, 0 broken.`
- Ruff y mypy sobre los archivos tocados: no aplican (son `.md`); `check_docs` no escanea `docs/adr`
  (`scripts/check_docs.py:157`, según el plan).

## Desviaciones, residuales y dudas

- Desviaciones respecto al plan: ninguna.
- Residuales: ninguno nuevo. R1-R5 del plan siguen con el destino de E0.5; la viñeta de AGENTS §3 la escribe David tras
  la auditoría de la fase C (E0.7).
- Dudas: ninguna. Siguiente: `/implementar BE-37 B`.

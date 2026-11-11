# Gaps — BE-39

## Auditoría Fase A — 2026-11-11

**Veredicto Fase A: PASS (0 bloqueantes, 2 opcionales).**

Evidencia (auditor con contexto fresco, sobre `f551351`; commit de la fase `d89e942`):

- Árbol: `git status --short` vacío antes y después de la compuerta.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.29%` · `580 passed, 5 warnings in 17.78s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  +1 test, cobertura igual, ruff y mypy en 0. Coincide con la fila A del plan y con el handoff.
- Archivo de la fase: `ruff check tests/test_route_guards.py` → `All checks passed!`; `ruff format --check` → `1 file
  already formatted`; `mypy tests/test_route_guards.py` → `Success: no issues found in 1 source file`;
  `pytest tests/test_route_guards.py -q` → `1 passed`.
- Contenido: `plan.md:163-252` sin la sangría de dos espacios contra `git show d89e942:tests/test_route_guards.py`: `diff`
  vacío (idéntico byte a byte; `i/lf w/lf`). Tabla: 17 filas, 14 `"admin"`, 3 `"user"`; sin duplicados y sin solapes
  entre `PROTECTED_ROUTES` y `PUBLIC_ROUTES` (medido importando el módulo).
- Alcance: `git diff --name-only 72492af d89e942` → solo `tests/test_route_guards.py`; `git diff --name-only 9ecc176 HEAD --
  app alembic conftest.py tests/conftest.py` → 0 líneas. `f551351` toca solo `handoff-Fase_A.md` y `progress.json`.
- Mensaje de commit: `plan.md:262-276` contra `git show -s --format=%B d89e942` con `Claude Opus 5.5` → `<MODELO EJECUTOR>`:
  `diff` vacío.
- `progress.json`: JSON válido; `Fase_A` `completed` con `d89e942` (existe, `git show --stat` → 1 archivo, 90 inserciones);
  `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos.
- Mutantes re-medidos en directorios nuevos y vacíos del scratchpad (`audA_nomut`, `audA_m10`, `audA_m11`, extraídos con
  `git archive d89e942`; `find -name 'test_*probe*'` vacío en los tres), suite sin `test_check*.py`:
  sin mutante `291 passed`; M10 `1 failed, 290 passed` (`test_every_route_is_listed_as_protected_or_public`); M11
  `2 failed, 289 passed` (el inventario y `tests/test_services.py::test_inactive_column_returns_off_rule_package`).
  Las tres cifras son las del plan (`plan.md:254-256`) y las del handoff.
- AGENTS: sin mocks ni fixtures en la fase; identificadores, docstrings y mensaje de aserción en inglés; ninguna aserción
  sobre texto en español; `app/` intacto.

Hallazgos:

[OPCIONAL] — Fase A — El cuerpo del commit dice "The rejection tests that read the table come in the next two commits"; tras E0 vienen tres fases (B, C, D). El texto es el que dicta el plan y E0 congeló los commits de A, B y C, así que no es una desviación; el handoff ya lo declara. Sin acción; si se quiere, se aclara en la descripción del PR — evidencia: `git show -s d89e942` (línea 13 del cuerpo), `plan.md:273-274`, `plan.md:531-532`.
[OPCIONAL] — Fase A — El inventario prueba que cada ruta esté en alguna tabla, no que esté en la correcta: una ruta protegida nueva que se anote por error en `PUBLIC_ROUTES` sale de los tests de rechazo de B y C y nadie lo nota (la fase D cubre solo el error "admin" anotado como "user"). Tampoco detecta una entrada que esté a la vez en las dos tablas ni una fila duplicada, porque compara conjuntos (hoy hay 0 de cada, medido). Queda fuera del plan aprobado; destino posible: nota al cierre o fila de backlog (p. ej. un caso "pública sin token no responde 401") — evidencia: `tests/test_route_guards.py:86-90` (`protected | PUBLIC_ROUTES` como conjuntos).

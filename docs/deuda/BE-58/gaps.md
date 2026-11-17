# Gaps — BE-58

## Auditoría Fase A — 2026-11-16
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (auditor `handoff-auditor`, contexto fresco; nada se tomó del handoff sin
re-medirlo):

- Árbol: `git status --short` vacío. HEAD `69200b0` (registro: solo `docs/deuda/BE-58/handoff-Fase_A.md` y
  `progress.json`), padre `ccd84a4` (fase), padre de este `62b9978` (plan aprobado con E0): `git log -3 --format='%H %P %s'`.
- Commit de la fase: `git show --stat ccd84a4` → 2 archivos, `docs/adr/0017-…` (4 +-) y `docs/adr/0019-…` (71 +), los
  dos que fija el plan. Mensaje: bloque "Commit" de la fase A (plan l. 295-314, sin la sangría) contra
  `git log -1 --format=%B ccd84a4` → `diff` sin salida (idéntico, trailer incluido).
- ADR-0019: plan l. 203-273 sin la sangría de cuatro espacios y con `<FECHA>` → `16 nov 2026` contra
  `git show ccd84a4:docs/adr/0019-…` → `diff` sin salida; 71 líneas; línea más larga 120; 0 `FECHA`; sin CR.
  Declara lo que exige E0.2: l. 49-50 ("Un superadmin recibe el mismo texto, aunque ningún par puede darle de baja desde
  la aplicación (ADR-0017; BE-55).").
- ADR-0017: `git diff 62b9978 ccd84a4 -- docs/adr/0017-…` → un solo hunk, la l.3 "Estado" sustituida por las tres líneas
  dictadas (plan l. 280-282 con la fecha → `diff` sin salida; longitudes 112, 116, 35); el resto del archivo intacto
  (única edición admitida en un ADR aceptado, ADR-0009).
- Criterio de aceptación: `git diff --numstat 2cc8f73 HEAD -- docs/adr` → `3 1` (0017) y `71 0` (0019), nada más;
  `git grep -l 'ADR-0019' -- docs/adr` → esos dos archivos; `git diff --stat 2cc8f73 HEAD --
  docs/adr/0018-un-superadmin-reactiva-a-otro.md AGENTS.md app tests conftest.py pyproject.toml` → vacío (E0.5).
- `progress.json`: JSON válido; `Fase_A` `completed` con `ccd84a4` (hash real); `current_target` `Fase_B`;
  `last_handoff` presente; `edit_rules` y `allowed_statuses` sin cambio (`git diff 62b9978 69200b0`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1039 15 152 13 97.65%` · `726 passed, 8 warnings in 31.32s` · `Compuerta superada.` Igual a la línea base de
  `verificacion.md` (726 · 97,65 % · ruff 0 · mypy 0 en 63 · 4 kept) y a lo que pegó el ejecutor.
- Fase sin código: ruff/mypy por archivo, TDD y reglas de AGENTS sobre código no aplican. No es la última fase: la
  "Verificación final" del plan se ejecuta en la auditoría de la fase B.

## Auditoría Fase B — 2026-11-17
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (auditor `handoff-auditor`, contexto fresco; nada se tomó del handoff sin
re-medirlo):

- Árbol: `git status --short` vacío (antes y después de la compuerta). `git log --format='%h %p %s' -4`: `04b75fa`
  (registro, padre `72fd34b`; solo `docs/deuda/BE-58/handoff-Fase_B.md` y `progress.json`), `72fd34b` (fase, padre
  `7645e89`), `7645e89` (cierre del 16 nov, solo docs), `87379f1` (AGENTS.md, E1).
- Commit de la fase: `git show --stat 72fd34b` → 4 archivos, los cuatro del plan; `git diff --numstat 72fd34b~1 72fd34b`
  → `2 2` routers/user.py, `22 14` user_access_policy.py, `6 5` user_service.py, `110 5` tests/test_user_access_policy.py
  = el esperado (22/14, 6/5, 2/2, 110/5). Mensaje: bloque "Commit" de la fase B (plan l. 400-429, sin la sangría) contra
  `git log -1 --format=%B 72fd34b` → `diff` sin salida (idéntico, trailer incluido).
- Cambios exactos: el diff de `app/` reproduce letra a letra las dos guardas (`actor.role != UserRole.tourist`, l.50 y
  l.113), los dos avisos de David en dos literales (l.52-53, l.117-118), los docstrings de la clase, `assert_can_delete`
  y `assert_can_update`, los de `delete_user_account`/`update_user_account`, el comentario l.205 y el docstring de
  `eliminar_usuario`. Lógica de `user_service.py` sin cambio; sin excepción nueva ni entrada en `_DOMAIN_ERROR_STATUS`;
  política síncrona con la misma firma.
- Tests: el diff de `tests/test_user_access_policy.py` es el Anexo literal (docstring de `TestAssertCanDelete`, U1 y U2
  sustituyendo a los dos be35 de admin, sección `# --- BE-58 regression …` con H1, H2 ×2, H3, H4 tras el último be36 y
  antes de la sección C). Sin mocks, fábricas de `conftest`, `persist_user` antes y `refresh` después (ADR-0011), sin
  aserción sobre texto en español.
- RED reproducido por el auditor: copia `git archive 72fd34b` en el scratchpad con `app/services/user_access_policy.py`
  de `72fd34b~1` (la copia importa su propio `app/`) → `-k be58`: `6 failed, 1 passed, 100 deselected` (fallan U1, U2,
  H1, H2 ×2, H3; pasa H4), igual al RED esperado.
- GREEN en el repo: `-k be58` → `7 passed, 100 deselected`; `-k be35` → `15 passed, 92 deselected`; `-k be36` →
  `19 passed, 88 deselected`.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`; `mypy` de
  los tres de `app/` → `Success: no issues found in 3 source files`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1039 15 152 13 97.65%` · `731 passed, 8 warnings in 23.91s` · RESUMEN con los seis pasos en ✔ ·
  `Compuerta superada.` Contra la línea base de `verificacion.md` (726 · 97,65 % · ruff 0 · mypy 0 en 63 · 4 kept): +5
  tests, cobertura igual, `user_access_policy.py` al 100 % (entre los 30 omitidos); coincide con lo que pegó el ejecutor.
- `progress.json`: JSON válido; `Fase_B` `completed` con `72fd34b` (hash real); `current_target` `null` (última fase);
  `last_handoff` presente; `edit_rules` y `allowed_statuses` sin cambio (`git diff 7645e89 04b75fa`).
- Verificación final del plan (última fase), ejecutada por el auditor: 1 → `:50`, `:113`; 2 → `:50`, `:89`, `:112`,
  `:114`; 3 → `user_access_policy.py:6`; 4 → sin salida (exit 1); 5 → `tests/test_auth.py:168`,
  `tests/test_user_access_policy.py:41`; 6 → 13 líneas (router 1, política 6, servicio 6); 7 → `:1229`, `:1257`; 8 → 10
  líneas (AGENTS.md 2, app 6, tests 2); 9 → app 7 (política 3, servicio 3, router 1), tests `:1232`, `:1260`, docs/adr
  0017 y 0019; 10 → `:52`, `:117`, y los avisos de BE-35 sin salida (exit 1); 11 → ` AGENTS.md | 9 +++++----` y nada más,
  con `git log 2cc8f73..HEAD -- AGENTS.md` = solo `87379f1` (E1.2: no es hallazgo); 12 → `3	1	docs/adr/0017-…`;
  13 → be58 `6`, be35 `13`, y 7/15/19 passed; 14 → compuerta arriba. Todo como el plan.
- Mutantes: no re-ejecutados uno a uno por el auditor; el RED reproducido cubre R1 y R5 a la vez (las dos guardas de
  vuelta a "solo superadmin" → los seis be58 que deben caer, caen). El handoff pega la salida de los 17 y coincide con
  la tabla del plan.
- Residuales del plan sin cambio (R1 nota en BE-55, R2 `docs/CONTEXT.md` al cierre, R3 ya presente, R4 BE-37); E1.3
  (AGENTS §3 adelantado al código entre `87379f1` y `72fd34b`) se declara en la descripción del PR.

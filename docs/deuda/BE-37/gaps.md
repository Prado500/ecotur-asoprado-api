# Gaps — BE-37

## Auditoría Fase A — 2026-11-17
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (auditor `handoff-auditor`, contexto fresco, rama `item/be-37`, HEAD `83071bd`):

- Árbol: `git status --short` vacío antes de escribir este archivo.
- `progress.json`: JSON válido; `Fase_A` = `completed` con `commit` `4c4acb7` (`git show --stat 4c4acb7` lo confirma: 2
  archivos, 72 inserciones); `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` sin cambio
  (`git diff 928a16f HEAD -- docs/deuda/BE-37/progress.json` solo toca `current_target`, `status`, `commit` y
  `last_handoff`).
- Mensaje de commit: plan l. 223-243 sin la sangría contra `git log -1 --format=%B 4c4acb7` → `diff` sin salida
  (idéntico, trailer incluido).
- Archivos: `git diff --numstat 928a16f 4c4acb7` → `9 0` ADR-0018 y `63 0` ADR-0020, nada más. Fuera de alcance
  (`app`, `tests`, `AGENTS.md`, `conftest.py`, `pyproject.toml`, ADR-0017, ADR-0019) sin cambios desde `32b8fd4`
  (`git diff --stat` vacío). E0.7 respetada.
- Fidelidad al Anexo A con E0.1: plan l. 584-646 con `<FECHA>` → `17 nov 2026` contra ADR-0020 → `diff` sin salida;
  plan l. 652-660 con `<FECHA>` → `17 nov 2026` y `<AAAA-MM-DD>` → `2026-11-17` contra las 9 últimas líneas de ADR-0018
  → `diff` sin salida. ADR-0020: 63 líneas, UTF-8, LF, termina en salto de línea. ADR-0018: solo líneas añadidas
  (hunk `@@ -68,3 +68,12 @@`).
- Criterio de aceptación: `git grep -n "<FECHA>\|<AAAA-MM-DD>" -- docs/adr` sin salida (exit 1).
- Addendum conforme a ADR-0009 (punto 1: `## Addendum — D mmm AAAA (quién)` con cita a la bitácora; punto 5: la
  bitácora `2026-11-17` lo menciona, l. 125-126 y 133-134). El test que cita (`test_be36_peer_superadmin_update_other_than_reactivation_is_rejected`,
  caso `"null"`) existe en `tests/test_user_access_policy.py:290-292`.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la línea base de
  `verificacion.md` y a la del handoff: `68 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1039 15 152 13 97.65%` · `731 passed, 8 warnings in 30.07s`.

## Auditoría Fase B — 2026-11-17
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (auditor `handoff-auditor`, contexto fresco, rama `item/be-37`, HEAD `08a02eb`):

- Árbol: `git status --short` vacío antes de escribir este bloque.
- `progress.json`: JSON válido; `Fase_B` = `completed` con `commit` `99f48ae` (`git show --stat 99f48ae`: 4 archivos,
  206 inserciones, 14 borrados); `current_target` = `Fase_C`; `last_handoff` presente; `edit_rules` sin cambio
  (`git diff 83071bd 08a02eb -- docs/deuda/BE-37/progress.json` solo toca `current_target`, `status`, `commit` y
  `last_handoff`). El handoff no contiene `[exited with code` (`grep -c` → 0).
- Mensaje de commit: plan l. 279-304 sin la sangría contra `git cat-file commit 99f48ae` (cuerpo) → `diff` sin salida
  (idéntico, trailer incluido).
- Archivos: `git diff --numstat 05f4022 99f48ae` → `38 0` `partial_update.py`, `13 9` `user.py`, `6 5`
  `test_email_case.py`, `149 0` `test_user_update_null.py`; exactamente el criterio del plan, nada más. Fuera de alcance
  sin cambios desde `32b8fd4` (`app/services`, `app/api`, `app/main.py`, `app/models`, `app/core`, `app/repositories`,
  `alembic`, `app/schemas/service.py`, `tests/test_services.py`, `tests/test_user_access_policy.py`,
  `tests/test_route_guards.py`, `tests/conftest.py`, `conftest.py`, `pyproject.toml`, `docs/CONTEXT.md`, `AGENTS.md`;
  el único cambio en `docs/backlog.md` es del commit del plan, `928a16f`). E0.7 respetada.
- Fidelidad al Anexo B con E0.2: plan l. 668-705 contra `git show 99f48ae:app/schemas/partial_update.py` → `diff` sin
  salida (`_NULL_MESSAGE = "Este campo no puede quedar vacío."`); plan l. 799-947 contra
  `tests/test_user_update_null.py` → sin salida; hunks de `user.py` (l. 711-762) y `test_email_case.py` (l. 768-793)
  contra `git diff 05f4022 99f48ae` → sin salida.
- E0.3: 16 casos de la fase (1 en `test_email_case.py`, 15 en `test_user_update_null.py`: U1, U2, H1 ×9, H2, H3 ×2,
  H4); E0.4: caso `superadmin-on-peer-is_active` presente y verde. Ningún test afirma sobre texto en español (`message`
  solo se comprueba como `str`; `"Nuevo"` es dato de entrada; `"John"` es el valor por defecto de la fábrica,
  `tests/conftest.py:194`).
- RED reproducido en copia `git archive 05f4022` del scratchpad con solo los dos archivos de test de `99f48ae`:
  `-k be37` → `12 failed, 4 passed, 16 deselected` (`DID NOT RAISE` ×2: correo y U2; `assert 409 == 422` ×6: H1 ×5 y
  H2; `assert 403 == 422` ×4); suite completa → `12 failed, 734 passed, 8 warnings`. Igual al plan y al handoff.
- Mutantes de la fase B (copia `git archive 99f48ae`, suite completa por mutante; la copia sin mutar da `746 passed`):
  MU-email 2 failed, MU-first_name 1, MU-last_name 1, MU-role 5, MU-is_active 4, MU-phone+ 2, MX-exclude_none 2,
  MF-falsy 10 (`test_auth.py` 1, be35 5, be36 1, be58 3). Los ocho mueren con los tests que declara la tabla del plan.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`; `mypy` →
  `Success: no issues found in 4 source files`.
- AGENTS: el marcador vive en `app/schemas/` y solo lo usa `UserUpdate` (A9; `git grep -n NoExplicitNull -- app` → 8
  líneas); ninguna excepción de dominio nueva; sin mocks; docstrings Google en la función nueva; rama muerta
  `if v is None` fuera (`git grep` exit 1).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la del handoff y por encima
  de la línea base de `verificacion.md` (731 passed · 97,65 % · mypy 0 en 63 · 4 kept): `70 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 65 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1046 11 152 9 98.33%` · `746 passed, 18 warnings in 32.69s`. Avisos 8 → 18: residual R2 (E0.5, nota en S5).

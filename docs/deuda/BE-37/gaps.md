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

## Auditoría Fase C — 2026-11-17
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de lo comprobado (auditor `handoff-auditor`, contexto fresco, rama `item/be-37`, HEAD `d368a5d`):

- Árbol: `git status --short` vacío antes de escribir este bloque y después de los mutantes (todo en copias
  `git archive` del scratchpad).
- `progress.json`: JSON válido; `Fase_C` = `completed` con `commit` `dac6464` (`git show --stat dac6464`: 2 archivos,
  130 inserciones, 8 borrados); `current_target` = `null` (última fase); `last_handoff` presente; `edit_rules` sin
  cambio (`git show d368a5d -- docs/deuda/BE-37/progress.json` solo toca `current_target`, `status`, `commit` y
  `last_handoff`). El handoff no contiene `[exited with code` (`grep -c` → 0).
- Mensaje de commit: plan l. 332-352 sin la sangría contra `git log -1 --format=%B dac6464` → `diff` solo con la línea
  en blanco final que añade `%B`; asunto y cuerpo idénticos, trailer incluido.
- Archivos: `git diff --numstat 8cf2fd1 dac6464` → `18 8` `app/schemas/service.py` y `112 0` `tests/test_services.py`,
  nada más; `git diff --name-only 8cf2fd1 d368a5d` añade solo `handoff-Fase_C.md` y `progress.json`. `AGENTS.md`,
  `docs/CONTEXT.md` y `docs/backlog.md` sin cambio desde `8cf2fd1` (E0.7 respetada).
- Fidelidad al Anexo C: el diff del plan (l. 955-1001) aplicado sobre `git archive 8cf2fd1` da un `service.py` igual al
  de `dac6464` (`diff --strip-trailing-cr` sin salida; en el índice, LF). Plan l. 1007-1116 contra
  `tests/test_services.py` desde la l. 770 → `diff` sin salida; l. 768-769 en blanco; el diff de tests no borra nada.
- E0.3: 11 casos de la fase (S1 ×5, S2 ×2, S3, S4, S5 ×2); `-k be37` sobre `tests/test_services.py` → `11 passed`.
  "El 422 llega antes de cualquier llamada al CDN" probado aparte: en la copia RED, quitadas las dos aserciones de
  estado de S2, los dos casos siguen cayendo con `Expected delete_image to not have been awaited. Awaited 1 times.`,
  así que las aserciones del CDN muerden por sí solas. Dobles del CDN: `storage_double` y `classifying_storage` con
  `create_autospec(AzureStorageClient, instance=True)` (`tests/test_services.py:366-375`, `:502`), y el autouse de
  `tests/conftest.py:101-141`, también con `autospec`. Ningún test afirma sobre texto en español (`message` solo como
  `str`; `"Recorrido por la reserva"` es entrada; `"Paquete De Prueba Automatizada"` es el valor por defecto de
  `_persist_package`, estado y no mensaje).
- RED reproducido en copia `git archive 8cf2fd1` con solo `tests/test_services.py` de `dac6464`: `-k be37` →
  `7 failed, 4 passed, 36 deselected` (los siete con `assert 409 == 422`: S1 ×5, S2 ×2); suite completa →
  `7 failed, 750 passed, 18 warnings`. Igual al plan y al handoff.
- Mutantes de la fase C (copia `git archive dac6464`, sin mutar `757 passed`; suite completa por mutante, restaurada
  después): MA-after `757 passed` (vive, equivalente); MS-name 3 failed (S1[`name`], S2[`replace`], S2[`empty`]);
  MS-category, MS-base_price, MS-max_capacity, MS-is_available 1 failed cada uno (su S1); MS-description+ 1 failed
  (S3; mutada la ocurrencia de `ServiceUpdate`, `service.py:118`, porque la línea se repite en `ServiceBase:27`, la
  misma incidencia que anota el handoff); MS-image_urls+ 1 failed (S4); M6 `757 passed` (vive, a propósito). Los nueve
  coinciden con la tabla del plan y con el handoff.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`; `mypy` →
  `Success: no issues found in 2 source files`.
- AGENTS: el marcador solo en `ServiceUpdate` (A9; `ServiceBase`, `ServiceCreate` y los DTO de salida sin cambio,
  comando 2); ninguna excepción de dominio nueva; ninguna ruta nueva; rama muerta `if v is None` fuera (comando 6). La
  docstring de `format_service_name` es la de una línea que dicta el plan.
- Verificación final del plan (última fase), sobre la rama: #1 14 líneas (`partial_update.py` :36 :38; `service.py` :8
  :117 :119 :120 :123 :124; `user.py` :7 :170 :173 :179 :186 :187); #2 10 líneas, solo en los DTO de actualización; #3
  9 líneas (`user.py` :65 :152 :185; `service.py` :27 :76 :93 :100 :118 :125), ninguna de los diez campos; #4
  `exclude_none` exit 1 y `exclude_unset=True` 3 líneas (`tourist_services_service.py` :282 :337, `user_service.py`
  :284); #5 1 línea, `user_access_policy.py:114`; #6 exit 1; #7 12 líneas (`test_services.py` 5,
  `test_user_access_policy.py` :190 :287, `test_user_update_null.py` 5); #8 `test_email_case.py:120` y el nombre viejo
  exit 1; #9 app 4 y tests 4 en las líneas previstas, `docs/adr` 0018 y 0020; #10 `git grep -c` 1/5/6,
  `pytest -k be37` → `27 passed, 730 deselected`, `-k "be35 or be36 or be58"` → `41 passed, 66 deselected`; #11 salida
  vacía (incluye `AGENTS.md`); #12 exactamente las 8 líneas previstas (`38 0`, `18 8`, `13 9`, `9 0`, `63 0`, `6 5`,
  `112 0`, `149 0`); #13 la compuerta de abajo. La deuda no asoma en el repo.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la del handoff y a la copia
  final del plan, por encima de la línea base de `verificacion.md` (731 passed · 97,65 % · mypy 0 en 63 · 4 kept):
  `70 files already formatted` · `All checks passed!` · `Success: no issues found in 65 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1046 10 150 8 98.49%` · `757 passed, 25 warnings in 30.63s`. Avisos 18 → 25:
  residual R2 (E0.5, nota en S5). Residuales R1-R5 con el destino de E0.5; la viñeta de AGENTS §3 queda para David
  (E0.7).

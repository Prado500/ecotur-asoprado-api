# Gaps — BE-36

## Auditoría Fase A — 2026-11-16
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `e804528`, rama `item/be-36`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `dfed481` existe (`git show --stat`: `docs/adr/0018-un-superadmin-reactiva-a-otro.md | 70 +++`,
  1 file changed); su padre es `d8e3aca` (plan aprobado con E0) y `git diff --stat d8e3aca dfed481` → solo ese archivo.
  `git diff --name-only 62b9702 HEAD` → el ADR-0018, `docs/bitacora/2026-11-16.md` y `docs/deuda/BE-36/plan.md` (ambos del
  commit del plan `d8e3aca`, no de la fase), `handoff-Fase_A.md` y `progress.json` (commit de registro `e804528`). Ningún
  archivo de `app/`, `tests/`, `AGENTS.md`, `docs/CONTEXT.md` ni `docs/backlog.md`.
- Mensaje del commit: el bloque "Commit" de la fase A (plan l. 253-271, sin la sangría de dos espacios) comparado con
  `git log -1 --format=%B dfed481` (sin la línea en blanco final que añade `%B`) con `diff` → idéntico. Trailer
  `Co-Authored-By` incluido.
- Texto del ADR: el bloque dictado (plan l. 172-241, sin sangría, `<FECHA>` → `16 nov 2026`, la de la línea
  `Aprobado: 16 nov 2026` de la cabecera, E0.1) comparado con `git show dfed481:docs/adr/0018-…md` con `diff` → idéntico.
  `<FECHA>` sin sustituir: 0 apariciones. UTF-8, sin CR. `plan.md` sin cambios desde `d8e3aca`
  (`git diff --quiet d8e3aca HEAD -- docs/deuda/BE-36/plan.md`).
- Criterio de aceptación: `git grep -l 'ADR-0018' -- docs/adr` → solo `docs/adr/0018-un-superadmin-reactiva-a-otro.md`;
  `git diff --stat 62b9702 HEAD -- AGENTS.md docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md app tests conftest.py`
  → vacío (E0.3: `AGENTS.md` y ADR-0017 intactos).
- `progress.json` (diff de `e804528`): `Fase_A` → `completed`, `commit` `dfed481` (hash real), `current_target` →
  `Fase_B`, `last_handoff` presente y coherente con el handoff, `edit_rules` y `allowed_statuses` intactos; JSON válido.
- Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already
  formatted` · `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1038 15 152 13 97.65%` · `707 passed, 8 warnings in 30.19s`. Igual a la línea base de `verificacion.md`
  (707 · 97,65 % · ruff 0 · mypy 0 en 63 · 4 kept) y a lo que pegó el ejecutor. Ningún `.py` tocado: ruff/mypy por
  archivo no aplica.
- No es la última fase: la "Verificación final" del plan se ejecuta en la auditoría de la fase B.

## Auditoría Fase B — 2026-11-16
**Veredicto Fase B: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase B — La decisión E0.1 (2) ("reactivar a un par que ya está activo da 200, sin condición sobre el estado actual") no tiene test: los tres casos que esperan éxito (U1, H1, H2) usan un objetivo con `is_active` false. Un mutante N7 que añade `and target.is_active is False` a `is_peer_reactivation` sobrevive a `tests/test_user_access_policy.py` (`101 passed`) y al resto de la suite copiada (mismos fallos de entorno que el original, ninguno nuevo). El plan no dictó este test, así que no bloquea; candidato a un caso unitario más (superadmin activo → `{"is_active": True}` no lanza) en BE-38 o en el cierre — evidencia: `tests/test_user_access_policy.py:266-270` (U1, `is_active=False`); salida del mutante N7 en la copia del scratchpad.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `d7e9b5e`, rama `item/be-36`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `53f1660` existe; padre `f5fc1f4` (auditoría de la fase A). `git show --stat 53f1660` → exactamente
  `app/services/user_access_policy.py | 22`, `app/services/user_service.py | 5`, `tests/test_user_access_policy.py | 244`
  (3 files, 267+, 4-). El commit de registro `d7e9b5e` solo toca `handoff-Fase_B.md` y `progress.json`.
- Mensaje: bloque "Commit" de la fase B (plan l. 350-379, sin la sangría) contra `git log -1 --format=%B 53f1660` (sin la
  línea en blanco final) con `diff` → idéntico, trailer incluido. `plan.md` sin cambios desde `d8e3aca`.
- Cambios exactos en `app/`: el bloque `is_peer_reactivation` del plan, literal (actor superadmin, objetivo superadmin,
  `target.deleted_at is None`, `set(update_dict) == {"is_active"}` antes de `update_dict["is_active"] is True`), dentro de
  la guarda de jerarquía y no como `return` temprano: las guardas de `role`, turistas y ADR-0017 siguen después,
  intactas (el diff no toca `:89-` ni el `raise`). Docstring de la clase (`:14-16`), de `assert_can_update` (`:55-57`) y
  los dos de `user_service.py` (`:260-262`, `:338-339`) con el texto dictado. `user_service.py`: solo docstrings (el diff
  no tiene líneas de código).
- Tests: los dos bloques del Anexo están **literalmente** en el archivo (comparación de subcadena con un script: unitarios
  53 líneas y HTTP 185 líneas → `True`); imports según el plan (única línea borrada: `from app.models.user import
  UserRole`). Ubicación: unitarios al final de `TestAssertCanUpdate` (`:266-319`), sección HTTP tras los BE-35 y antes de
  `# C. GLOBAL EXCEPTION HANDLER TESTS` (`:1009-1195`). 12 funciones `test_be36_`, 18 casos. AGENTS §5: fábricas
  `make_user` / `persist_user` (commit antes de la petición) / `make_auth_headers`; sin mocks ni `User(...)` a mano; sin
  aserciones sobre texto en español (sin caracteres acentuados en las líneas añadidas; `detail` se comprueba por clave y
  tipo); código HTTP + estructura + mutación (`refresh` tras la petición, o `select` de una fila nueva en H2) + auditoría
  exacta en cada caso HTTP. Bordes de la adenda: `{"is_active": true}` → 200 (H1, H2), `false` → 403 (U2, H4), con
  `first_name` → 403 sin mutación (U3, H3), `first_name` solo → 403 (H3 `profile-only`), `role` → 403 (U3, H3), admin
  sobre admin → 403 (U5, H6), papelera → 403 (U4, H5, E0.1 (1)). E0.1 (2): ver el opcional.
- RED repetido por el auditor (copia en el scratchpad con `user_access_policy.py` de `f5fc1f4`): `-k be36` →
  `3 failed, 15 passed` (U1, H1, H2), igual al plan y al handoff.
- Mutantes repetidos por el auditor sobre la copia, `-k be36`: N1 `3 failed` (U1, H1, H2); N2 `1 failed` (U6); N3
  `18 passed` (equivalente, declarado); N4 `2 failed` (U4, H5); N5 `7 failed` (U3 ×4, H3 ×3); N6 `3 failed` (U2, U3
  `null`, H4); original restaurado `18 passed`. Igual al plan y al handoff.
- `progress.json` (diff de `d7e9b5e`): `Fase_B` → `completed`, `commit` `53f1660` (hash real), `current_target` → `null`
  (última fase), `last_handoff` presente y coherente con el handoff, `edit_rules` y `allowed_statuses` intactos; JSON
  válido.
- Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already
  formatted` · `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1039 15 152 13 97.65%` · `725 passed, 8 warnings in 32.13s`. Contra la línea base (707 · 97,65 % · ruff 0 ·
  mypy 0 en 63 · 4 kept): +18 tests, cobertura igual, `user_access_policy.py` al 100 % (entre los 30 omitidos). Igual a
  lo que pegó el ejecutor. Archivos tocados: `ruff check` → `All checks passed!`; `mypy` → `Success: no issues found in
  3 source files`.
- Verificación final del plan (última fase), salida del auditor: 1 → `app/services/user_service.py:363`. 2 →
  `app/repositories/user_repository.py:63`. 3 → sin salida, exit 1. 4 → `user_access_policy.py:75`, `:85`. 5 → `:79`;
  `:80`. 6 → `app/api/routers/user.py:234`, `user_access_policy.py:113`, `user_service.py:332`, `:359`. 7 →
  `user_repository.py:83`, `user_service.py:362`. 8 → `27`. 9 → app 5 líneas (`user_access_policy.py:16, :57, :74`;
  `user_service.py:262, :339`); tests sin salida (exit 1); docs/adr solo `docs/adr/0018-un-superadmin-reactiva-a-otro.md`;
  ADR-0017 en app `7`. 10 → `app/schemas/user.py:130: is_active: bool = False`. 11 → salida vacía (`AGENTS.md`,
  ADR-0017, schemas, core, api, repositories, models, cli, `tests/test_auth.py`, `tests/test_user_service.py`,
  `tests/test_route_guards.py`, ambos `conftest.py` intactos desde `62b9702`; E0.3 cumplida). 12 →
  `tests/test_user_access_policy.py:12` y `18 passed`. 13 → la compuerta de arriba. Todo como lo predice el plan.
- Fuera de alcance respetado: `git diff --stat 62b9702 HEAD` no toca `docs/CONTEXT.md` ni `docs/backlog.md`; el único
  otro archivo fuera de `app/`, `tests/` y `docs/deuda/BE-36/` es `docs/bitacora/2026-11-16.md`, del commit del plan
  `d8e3aca`, no de la fase.

## Auditoría Fase C — 2026-11-16
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. El OPCIONAL de la auditoría de la fase B (la decisión E0.1 (2), "reactivar a un par que ya está activo da 200", sin test; mutante N7 vivo) queda **RESUELTO (`202ec51`)**: H7 (`test_be36_superadmin_reactivating_active_peer_returns_200`, `tests/test_user_access_policy.py:1196-1221`) envía `{"is_active": true}` de un superadmin a un par superadmin **activo** (`persist_user` crea con `is_active=True` por defecto, `tests/conftest.py:186`) y fuera de la papelera, y exige 200, cuerpo con `is_active` true y la cuenta activa tras `refresh`. Con N7 en una copia completa la suite da `1 failed, 725 passed`, con H7 como único fallo: es el único test que lo mata. El bloque de B no se edita.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `2fb4ebd`, rama `item/be-36`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `202ec51` existe; padre `ad48494` (fase C escrita y aprobada con E2). `git show --stat 202ec51` →
  `tests/test_user_access_policy.py | 28 ++++` (1 file, 28+, 0-); `git diff --name-only ad48494 202ec51` → solo ese
  archivo. El commit de registro `2fb4ebd` solo toca `handoff-Fase_C.md` y `progress.json`. `git diff --stat 9c77da2
  HEAD -- app AGENTS.md docs/CONTEXT.md docs/backlog.md` → vacío (sin `app/`; E0.3 / E2.4: `AGENTS.md` intacto).
  `plan.md` sin cambios desde `ad48494`.
- Mensaje: bloque "Commit" de la fase C (plan l. 485-502, sin la sangría) contra `git log -1 --format=%B 202ec51` (sin la
  línea en blanco final) con `diff` → idéntico, trailer incluido.
- Cambios exactos: las líneas añadidas del diff, sin las en blanco, contra el bloque dictado (plan l. 411-436, sin
  sangría) con `diff` → idéntico (26 líneas de texto + 2 en blanco = las 28 del criterio). Ubicación: tras `assert
  audits == []` de `test_be36_admin_reactivating_peer_admin_returns_403` (l.1193 en el padre), dos en blanco antes y dos
  después, antes de `# C. GLOBAL EXCEPTION HANDLER TESTS`. Sin imports nuevos. AGENTS §5 / ADR-0011: fábricas
  `persist_user` (commit antes de la petición) y `make_auth_headers`, `refresh` después, sin mocks, sin aserciones sobre
  texto en español; código HTTP + estructura del cuerpo + estado. E2.3: ninguna aserción sobre la auditoría (BE-38).
  Unitario gemelo no añadido, como dicta la fase. Por archivo: `ruff check` → `All checks passed!`; `ruff format
  --check` → `1 file already formatted`; `mypy` → `Success: no issues found in 1 source file`.
- RED (E2.2) repetido por el auditor: copia `git archive 202ec51 | tar -x` en el scratchpad (árbol completo; el repo no
  se tocó). N7 = `            and target.is_active is False` tras `            and update_dict["is_active"] is True` en
  `app/services/user_access_policy.py` de la copia (`diff`: `80a81 >             and target.is_active is False`). Suite
  completa de la copia con el `venv` del repo: `FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200`
  · `1 failed, 725 passed, 8 warnings in 29.70s`. Restaurada (`git diff --no-index` contra el archivo del repo → sin
  diferencias): `726 passed, 8 warnings in 29.55s`. Igual al plan y al handoff.
- `progress.json` (diff de `2fb4ebd`): `Fase_C` → `completed`, `commit` `202ec51` (hash real), `current_target`
  `Fase_C` → `null` (última fase), `last_handoff` presente y coherente con el handoff, `edit_rules` y
  `allowed_statuses` intactos; JSON válido.
- Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already
  formatted` · `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1039 15 152 13 97.65%` · `726 passed, 8 warnings in 31.68s` · `Compuerta superada.` Contra la línea base de
  `verificacion.md` (707 · 97,65 % · ruff 0 · mypy 0 en 63 · 4 kept) y el cierre de B (725): +1 test, cobertura igual,
  `user_access_policy.py` al 100 % (entre los 30 omitidos). Igual a lo que pegó el ejecutor.
- Verificación final del plan (última fase; comandos como los deja E1), salida del auditor: 1 →
  `app/services/user_service.py:363`. 2 → `app/repositories/user_repository.py:63`. 3 → sin salida, exit 1. 4 →
  `user_access_policy.py:75`, `:85`. 5 → `:79`; `:80`. 6 → `app/api/routers/user.py:234`, `user_access_policy.py:113`,
  `user_service.py:332`, `:359`. 7 → `user_repository.py:83`, `user_service.py:362`. 8 → `27`. 9 → app 5 líneas
  (`user_access_policy.py:16, :57, :74`; `user_service.py:262, :339`); tests sin salida (exit 1); docs/adr solo
  `docs/adr/0018-un-superadmin-reactiva-a-otro.md`; ADR-0017 en app `7`. 10 → `app/schemas/user.py:130: is_active: bool
  = False`. 11 → salida vacía (`AGENTS.md`, ADR-0017, schemas, core, api, repositories, models, cli, `tests/test_auth.py`,
  `tests/test_user_service.py`, `tests/test_route_guards.py`, ambos `conftest.py` intactos desde `62b9702`). 12 →
  `tests/test_user_access_policy.py:13` y `19 passed, 83 deselected`. 13 → la compuerta de arriba. Todo como lo predice
  el plan tras E1.
- Pendiente fuera de esta auditoría (no es hallazgo): la viñeta de AGENTS §3 la commitea David ahora, antes de `/pr`
  (E0.3 / E2.4); R1–R3 del plan van al cierre.

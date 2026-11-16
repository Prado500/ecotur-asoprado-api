# Gaps — BE-35

## Auditoría Fase A — 2026-11-16
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `ba5e7b1`, rama `item/be-35`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `7de0808` existe (`git show --stat`: `.../0017-ningun-superadmin-se-retira-a-si-mismo.md | 70 +++`,
  1 file changed); su padre es `3cf22fc` (plan aprobado con E0) y `git diff --name-only 3cf22fc 7de0808` → solo
  `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md`. Ningún archivo de `app/`, `tests/`, `AGENTS.md`,
  `docs/CONTEXT.md` ni `docs/backlog.md` (fuera de alcance de la fase).
- Mensaje del commit: el bloque "Commit" de la fase A (plan l. 218-236, sin la sangría de dos espacios) comparado con
  `git log -1 --format=%B 7de0808` con `diff`: única diferencia, la línea en blanco final que añade `%B`. Trailer
  `Co-Authored-By` incluido.
- Texto del ADR: el bloque dictado (plan l. 139-208, sin sangría, `<FECHA>` → `16 nov 2026`, la de la línea
  `Aprobado: 16 nov 2026` de la cabecera, E0.1) comparado con `git show 7de0808:docs/adr/0017-…md` con `diff` → idéntico.
  UTF-8, sin CR. `plan.md` sin cambios desde `3cf22fc` (`git diff --quiet 3cf22fc HEAD -- docs/deuda/BE-35/plan.md`).
- Criterio de aceptación: `git grep -c 'ADR-0017' -- docs/adr` → `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md:1`
  (lo esperado); compuerta completa en verde con 691 passed (abajo). Tests RED: no aplica (fase solo de documentación,
  según el plan).
- Commit de registro `ba5e7b1` (`docs(progress): record BE-35 Fase_A completion`, padre `7de0808`): solo
  `docs/deuda/BE-35/handoff-Fase_A.md` y `docs/deuda/BE-35/progress.json`.
- `progress.json`: JSON válido; `Fase_A` `completed` con `commit: "7de0808"` (hash real); `current_target: "Fase_B"`;
  `last_handoff` presente; `edit_rules` y `allowed_statuses` idénticos a `3cf22fc`; `Fase_B` sigue `pending`.
- Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already formatted`
  · `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1034 15 148 13 97.63%` · `691 passed, 8 warnings in 22.13s` · `Compuerta superada.` Ratchet contra
  `verificacion.md` (691 passed · 97,63 % · ruff 0 · mypy 0 en 63 archivos · 4 kept): todo igual. Coincide con lo pegado
  en el handoff. `ruff`/`mypy` sobre archivos tocados: no aplica (Markdown).
- Formato Nygard del ADR (AGENTS §7): contexto, decisión, consecuencias, alternativas y evidencia presentes.

Valorado sin hallazgo — residual declarado por el ejecutor (título del ADR > 100 columnas): mide 120 caracteres
(medido con el intérprete). No incumple el plan (es el texto dictado y aprobado), ni la compuerta (`check_docs` excluye
`docs/adr`, `scripts/check_docs.py:157`), ni ninguna convención: el límite de 100 columnas es de `ruff` para Python, y
los ADR aceptados ya lo superan en el título (0005: 124, 0008: 140, 0012: 139, 0015: 121) y en el cuerpo (los 17 ADR
tienen líneas de más de 100). No afecta a corrección ni a requisitos; no se registra.

## Auditoría Fase B — 2026-11-16
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos.

Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `0eeef9a`, rama `item/be-35`):

- Árbol: `git status --short` vacío antes de la auditoría (después solo cambia este `gaps.md`).
- Commit de la fase: `84eef92` existe; padre `474d075` (auditoría PASS de la fase A). `git diff --name-only 474d075 84eef92`
  → exactamente los cuatro archivos de la fase: `app/api/routers/user.py`, `app/services/user_access_policy.py`,
  `app/services/user_service.py`, `tests/test_user_access_policy.py` (`git show --stat`: 4 files, +252 −18).
- Mensaje del commit: bloque "Commit" de la fase B (plan l. 349-380, sin la sangría de dos espacios) contra
  `git log -1 --format=%B 84eef92` con `diff` → única diferencia, la línea en blanco final que añade `%B`. Trailer incluido.
- Commit de registro `0eeef9a` (padre `84eef92`): solo `docs/deuda/BE-35/handoff-Fase_B.md` y `docs/deuda/BE-35/progress.json`.
- `progress.json`: JSON válido; `Fase_B` `completed` con `commit: "84eef92"` (hash real); `last_handoff` presente;
  `edit_rules` y `allowed_statuses` sin cambios (`git diff 474d075 0eeef9a`). `current_target: null`: es la convención de
  ítems sin fases restantes (los 18 `docs/deuda/*/progress.json` cerrados lo tienen en `null`, p. ej. BE-02, BE-34).
  `plan.md` sin cambios desde `3cf22fc`.
- Cambios exactos en `app/` contrastados línea a línea con el plan: las dos guardas tienen el código dictado y su sitio
  (borrado tras el `raise` de jerarquía, `user_access_policy.py:47-48`; `is_active` como última guarda, `:90-95`). La de
  `is_active` lee el valor: `update_dict.get("is_active") is False` (`:93`), no la clave. Docstrings de la clase,
  `assert_can_delete` (párrafo y `Raises`), `assert_can_update`, `delete_user_account` (párrafo y `Raises`), comentario de
  paso 2, `update_user_account` y el `DELETE` del router: idénticos a los textos dictados. En `user_service.py` y
  `routers/user.py` el diff solo toca docstrings y el comentario (lógica intacta). Sin excepción nueva ni conteo.
- Tests: los 15 `def test_be35_` (U1-U8, H1-H7) existen con los nombres del plan; U1 sustituye a
  `test_superadmin_self_delete_is_allowed`; docstrings de clase con el texto de E0.2; cabecera de sección y posición (antes
  de `# C. GLOBAL EXCEPTION HANDLER TESTS`) como dicta el plan. AGENTS §5: fábricas `make_user`, `persist_user`,
  `make_auth_headers` (ningún usuario ni token a mano); ningún mock; ninguna aserción sobre texto en español (solo
  `set(body) == {"detail"}` e `isinstance(..., str)`); código HTTP + estructura + mutación de estado (`deleted_at`,
  `is_active`, `first_name`, `AuditLog`); `refresh` tras cada petición (ADR-0011). Las desviaciones de forma declaradas
  (H2 refresca también `peer`; H5 refresca y afirma el estado del actor) refuerzan la regla 2 de ADR-0011 y no cambian
  conteos de la Verificación final.
- RED reproducido por el auditor (copia aislada en el scratchpad, `user_access_policy.py` de `474d075` + tests de
  `84eef92`, `-k be35`): `11 failed, 6 passed, 66 deselected` con los mismos 11 fallos del plan; GREEN con el código de
  `HEAD`: `17 passed, 66 deselected`.
- Mutantes re-ejecutados por el auditor sobre la misma copia (control `tests/test_user_access_policy.py`: 83 passed):
  M1 2 failed (`test_self_delete_tourist_is_allowed`, `test_be35_admin_self_delete_is_still_allowed`); M2 1
  (U2); M3 2 (U5 y H6); M4 2 (U8 y H7); M5 1 (U7); M7 1 (U6); M8 5 (U1, U2, H1, H2, H5); M9 7 (U4, U6, H3 ×3, H4, H5):
  todos muertos. M6 sobre la suite entera: `13 failed, 694 passed`, idéntico al control sin mutar (los 13 son de
  `tests/test_check_docs.py`, que lee `docs/deuda/`, ausente en la copia) → vivo, como declaran el plan y R2.
- Verificación final del plan (última fase), salida medida: 1 → 4 líneas, todas en `user_access_policy.py` (:38, :41, :47,
  :84); 2 → 1 (`:93`); 3 → 2 (`user_repository.py:23`, `superadmin_bootstrap.py:42`); 4 → 0 (exit 1); 5 → 0 (exit 1);
  6 → 1 (`app/main.py:107`); 7 → 4 (`test_auth.py:248`; `test_user_access_policy.py:867, :887, :934`); 8 → 7
  (`routers/user.py:135`; `user_access_policy.py:14, :27, :56`; `user_service.py:183, :205, :259`); 9 → 2
  (`user_access_policy.py:48, :95`); 10 → salida vacía; 11 → `tests/test_user_access_policy.py:15` y `17 passed`. Todo como
  el plan espera.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`; `mypy` →
  `Success: no issues found in 4 source files`.
- Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 0): `68 files already formatted`
  · `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1038 15 152 13 97.65%` · `707 passed, 8 warnings in 21.76s` · `Compuerta superada.`
  `user_access_policy.py` sigue al 100 % (fuera de la tabla, `30 files skipped due to complete coverage`). Ratchet contra
  `verificacion.md` (691 passed · 97,63 % · ruff 0 · mypy 0 en 63 archivos · 4 kept): 707 passed (691 − 1 + 17),
  97,65 % ≥ 97,63 %, totales iguales. Coincide con lo pegado en el handoff.

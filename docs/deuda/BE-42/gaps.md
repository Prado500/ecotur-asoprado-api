# Gaps — BE-42

## Auditoría Fase A — 2026-11-12
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `69c032d`, rama `item/be-42`):

- Árbol: `git status --short` vacío antes y después de la auditoría (salvo este `gaps.md`).
- Plan y aprobación: `plan.md` entra en un solo commit (`758a2fa`) y no cambia después (`git log -- docs/deuda/BE-42/plan.md`
  → solo `758a2fa`); `fed1f7c` solo toca `docs/bitacora/2026-11-12.md`. E0 aprueba A → C "como están escritas" y dice
  "sin correcciones de dictado" (`plan.md:611-616`): el texto de la fase A es el del cuerpo del plan.
- `progress.json`: `Fase_A` `completed` con `commit: "db6bc51"` (`git show --stat db6bc51` lo confirma);
  `current_target: "Fase_B"`; `last_handoff` presente; `edit_rules` igual que en `758a2fa` (`git show 69c032d --
  docs/deuda/BE-42/progress.json` solo cambia `current_target`, `status`, `commit` y `last_handoff`).
- Commit `db6bc51`: mensaje idéntico al de `plan.md:200-215`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`.
  `git show --numstat --format= db6bc51` → `5	1	app/core/security.py` y `2	1	app/services/user_service.py`
  (criterio de aceptación, `plan.md:195`). `git diff --name-only fed1f7c HEAD -- app tests conftest.py alembic` → solo
  esos dos archivos; `69c032d` solo toca `handoff-Fase_A.md` y `progress.json`.
- Cambios exactos: `app/core/security.py:46-55` (`"""` de cierre, línea en blanco, las dos líneas de comentario y
  `EMAIL_VERIFICATION_SCOPE = "email_verification"`, dos líneas en blanco, `def create_access_token`) y `:103`
  (`to_encode` con la constante); `app/services/user_service.py:14` (primer nombre del import partido) y `:138`
  (`if email is None or scope != EMAIL_VERIFICATION_SCOPE:`). Ningún otro cambio en el método.
- Fuera de alcance respetado: `git grep -n "ACCESS_TOKEN_SCOPE" -- app tests | wc -l` → `0`; las únicas apariciones de
  `create_access_token`, `activate_user` y `single-use` en `git diff fed1f7c db6bc51` son líneas de contexto, no `+`/`-`;
  `tests/conftest.py`, `app/api/dependencies.py` y los tests no aparecen en el diff.
- `git grep -n '"email_verification"' -- app | wc -l` → `1` (`app/core/security.py:51`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`,
  `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files`,
  `Contracts: 4 kept, 0 broken.`, `618 passed, 8 warnings`, `TOTAL 962 19 136 16 96.81%`. Igual a la línea base de
  `verificacion.md:179-184` (618 passed, 96,81 %, 961 stmts) salvo el `+1` stmt de la constante, y a la fila A del plan.
- Mutantes re-medidos en copias desechables del scratchpad (`git archive` + edición de una línea comprobada con `sed -n`;
  el árbol de trabajo no se tocó):
  - MV sobre `fed1f7c` (forma literal): `1 failed, 328 passed`
    (`test_verify_email_wrong_scope_raises_invalid_verification_token`).
  - MV sobre `db6bc51`: `1 failed, 328 passed` (el mismo test).
  - MEV sobre `db6bc51`: `1 failed, 328 passed` (`test_register_tourist_returns_registration_result`).
  - Control sobre `db6bc51`: `329 passed`.
  Coinciden con `plan.md:189-192`, la fila A de `plan.md:164` y el handoff.
- AGENTS: comentario y nombre en inglés; constante de módulo en `app/core/`, importada por el servicio (capa permitida,
  4 contratos KEPT); sin tests nuevos ni excepciones de dominio nuevas.

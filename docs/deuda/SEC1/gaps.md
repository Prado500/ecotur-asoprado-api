# Gaps — SEC1

## Auditoría Fase A — 2026-11-02

Veredicto: PASS (0 bloqueantes, 5 opcionales). Commit auditado `9ce0379` (+ `7d24bcc` docs(progress)).

Compuerta re-ejecutada por el auditor (`venv/Scripts/python.exe scripts/check.py`): 333 passed, cobertura 92.76 %
(línea base 92.68 %), ruff check 97 (línea base 98), mypy 44 (línea base 44), import-linter 4 kept / 0 broken, docs OK.
`ruff check` y `ruff format --check` sobre `app/main.py` y `tests/test_main.py`: limpios. `mypy`: ninguna línea de
`app/main.py` ni `tests/test_main.py`. `pytest tests/test_main.py`: 17 passed. Greps de la verificación final: sin
`allow_origins=["*"]`, sin `allow_credentials=True`, `CORS_ORIGINS` 1 línea en `.env.example`, sin `azurestaticapps`,
sin `pydantic_settings`, sin `load_dotenv` en `app/main.py`. Arranque con `CORS_ORIGINS="*"` -> `ValueError`.

- [OPCIONAL] — Fase A — El trailer del commit es `Co-Authored-By: Claude Sonnet 5.5` y el plan decía `Claude Fable 5.1`; el resto del mensaje (título y cuerpo) es idéntico al plan. Lo declara el handoff y es la atribución vigente de la sesión — `git show 9ce0379 --format=%B`.
- [OPCIONAL] — Fase A — El RED de los tests 7-10 contra el comportamiento viejo no se midió (el ImportError de colección lo ocultó); el handoff lo admite. Los tests existen y pasan contra el código nuevo — handoff-A.md "Evidencia".
- [OPCIONAL] — Fase A — `docs/deuda/SEC1/plan.md` sigue sin trackear (el commit `7d24bcc` solo añadió handoff y progress.json) y contiene una nota posterior (líneas 310-314) que cita `9ce0379`; hay que commitearlo en el cierre — `git status --short`: `?? docs/deuda/SEC1/plan.md`.
- [OPCIONAL] — Fase A — Árbol sucio fuera de `docs/deuda/`: `docs/bitacora/2026-11-02.md` modificado (documento de David, ajeno a la fase, sin código) — `git status --short`.
- [OPCIONAL] — Fase A — `CORS_ORIGINS` definido pero vacío da `[]` (fail-closed) y los tests 7 y 9 fallarían por `CORS_ORIGINS[0]`; decisión de David registrada en plan.md:310-314 y trasladada a A4. Sin acción en esta fase.

Comprobaciones sin hallazgo: `progress.json` válido (Fase_A completed, commit `9ce0379` real, `current_target` = "cierre", `last_handoff` presente, `edit_rules` intacto); archivos del commit = solo `.env.example`, `app/main.py`, `tests/test_main.py`; los 11 tests exigidos existen con los nombres exactos del plan; `app/main.py` cumple las firmas exactas (`DEFAULT_CORS_ORIGINS`, `parse_cors_origins`, `CORS_ORIGINS`, comentario `(backlog A4)`, cinco argumentos del middleware); sin excepciones de dominio nuevas, sin mocks, aserciones sobre códigos y cabeceras.

## Auditoría Fase A — 2026-11-07

**Veredicto Fase A: PASS (0 bloqueantes, 2 opcionales).**

[OPCIONAL] — Fase A — El RED de herramienta del plan está mal contado: `grep -cE "^tests.test_fixtures_contract"` da `3` antes, no `2`, porque mypy añade una línea `note:` en `:59` que empieza por la misma ruta. Los errores son 2, como dice el plan (`:59 [call-arg]`, `:61 [attr-defined]`), y el `0` de después coincide. Es una imprecisión del comando del plan, no de la fase: el criterio de aceptación (2 errores → 0; `mypy tests` 16 → 14) se cumple. Para los RED de herramienta de las fases siguientes conviene filtrar con `error:` — evidencia: mypy sobre la copia de `bcc7c8c:tests/test_fixtures_contract.py` en el scratchpad da `:59: error: ... [call-arg]`, `:59: note: "send_verification_email" defined in "app.core.email"`, `:61: error: ... [attr-defined]` (3 líneas con el patrón); `plan.md:165-167`; `handoff-Fase_A.md`, "Desviaciones y dudas".
[OPCIONAL] — Fase A — Aviso de Git CRLF→LF en `progress.json`: es informativo y no exige ninguna acción. El blob commiteado está en LF (0 CR, 49 LF) y la copia de trabajo, en CRLF (49 CR) porque el editor la escribió así. `.gitattributes` (`* text=auto eol=lf`) normaliza al hacer `git add`, por eso `git status` sale limpio y el repositorio no lleva ningún CR. El JSON es válido — evidencia: `git ls-files --eol docs/deuda/BE-32/progress.json` → `i/lf w/crlf attr/text=auto eol=lf`; recuento de bytes de `git show HEAD:docs/deuda/BE-32/progress.json` → `CR 0, LF 49`; `json.load` correcto.

Puntos juzgados sin hallazgo:

- **Commit aparte `e51784e` (handoff y `progress.json`):** el protocolo lo exige así. `.claude/agents/fase-ejecutor.md:62-63`
  pide `git add docs/deuda/<ID>/progress.json docs/deuda/<ID>/handoff-<fase>.md` y
  `git commit -m "docs(progress): record <ID> <fase> completion"`. El mensaje coincide letra a letra, y el commit toca solo
  esos 2 archivos (`2 files changed, 128 insertions(+), 4 deletions(-)`). Hay precedente en `23af07b` (AF-02 Fase_B).
- **Commit de la fase `e7c814d`:** el mensaje es idéntico al de `plan.md:173-185` (`diff` vacío, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`).
  Toca solo `tests/test_fixtures_contract.py` (`1 file changed, 4 insertions(+), 3 deletions(-)`). El cuerpo coincide con
  los "Cambios exactos" (`double: Any = ...`, `assert double is mock_send_email`, `await double(recipient="x")`,
  `double.assert_not_called()`), y la docstring y la firma no cambian.
- **`progress.json`:** `Fase_A` está `completed` con `e7c814d`, un commit real. `current_target` = `Fase_B`, `last_handoff`
  existe, `edit_rules` no cambia respecto a `bcb7271` y quedan 8 fases.
- **RED reproducido:** `mypy tests` en HEAD da `Found 14 errors in 8 files (checked 18 source files)` y 0 líneas de
  `test_fixtures_contract`. Los 9 de `tests/` que quedan son los 5 de BE-32 de la fase B (`test_audit.py:72`,
  `test_user_service.py:65`, `:71`, `test_services.py:157`, `conftest.py:239`) y los 4 de A4 (`test_user_service.py:103`,
  `:197`, `:274`, `:292`). `pytest tests/test_fixtures_contract.py -q` da `9 passed`.
- **Compuerta (fila A):** `57 files already formatted` · ruff `Found 9 errors.` (8 I001 `:1:1` de `app/` +
  `tests\test_user_service.py:3:1`) · mypy `Found 5 errors in 4 files (checked 35 source files)` (`app\db\database.py:11`,
  `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`, `app\api\dependencies.py:95`) ·
  `Contracts: 4 kept, 0 broken.` · `547 passed, 5 warnings` · `96.11%`. Coincide con la línea base
  (`verificacion.md:241-252`) y con el handoff. El rojo es exactamente el heredado (ADR-0005, decisión 5 del plan).
- **Archivo tocado:** `ruff check` → `All checks passed!`; `ruff format --check` → `1 file already formatted`; mypy no
  reporta ninguna línea del archivo.

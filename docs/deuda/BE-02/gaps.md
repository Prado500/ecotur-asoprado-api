# Gaps — BE-02

## Auditoría Fase A — 2026-11-05

Commit auditado `f55313c` (+ `ab26fb4` docs(progress) + handoff). Base develop `c6422ed`. Fase A es la única del plan:
incluye la Verificación final completa. Árbol limpio al empezar.

Compuerta re-ejecutada por el auditor (`./venv/Scripts/python.exe scripts/check.py`, exit 1 por el rojo heredado que el
plan prevé): 415 passed (línea base 396, +19), cobertura 94.82 % (línea base 94.81 %), `53 files already formatted`, ruff
`Found 53 errors.` (línea base 54), mypy `Found 10 errors in 5 files (checked 35 source files)` (línea base 10),
import-linter `Contracts: 4 kept, 0 broken.` (línea base 4 KEPT), docs OK. RESUMEN idéntico al del handoff.

### Hallazgos

- [OPCIONAL] — Fase A — `current_target` = `"Auditoria"`. El precedente que cita el ejecutor es cierto pero incompleto: BE-15 (`2a1ee41`) y AF-05 (`9971898`) dejaron ese valor, pero los dos quedaron como opcional en su auditoría, BE-15 lo corrigió a mano a `null` (`1f547a8`) y CONTEXT §8 lo lista como defecto pendiente del flujo. Los demás ítems usan `null` (BE-01, AF-01) o `"cierre"` (SEC1, A9, S1). Avanza y no rompe nada, pero `--estado` da BE-02 por "en ejecución". Destino: `null` al cerrar el ítem; lo decide David, porque `edit_rules` reserva el campo a la sesión que ejecuta — `docs/deuda/BE-02/progress.json:3`; `docs/CONTEXT.md:285`; `docs/deuda/BE-15/gaps.md:696-700`; `.claude/agents/fase-ejecutor.md:55` (no fija valor para la última fase); `scripts/check_docs.py:472`; `check_docs.py --estado` → `BE-02: … en ejecución (objetivo: Auditoria) → handoffs: Fase_A`.
- [OPCIONAL] — Fase A — Ningún test congela la decisión 3 (guarda nueva después de la de l.64). El mutante que la pone antes da `415 passed`. El código cumple: sonda HTTP con `{"role":"admin"}` sobre sí mismo, turista y admin reciben 403 con el `detail` de siempre, superadmin 403 con el nuevo. El plan no exige ese test y AGENTS §5 prohíbe afirmar sobre el texto; se podría fijar sin texto, comparando el `detail` de la auto-edición del admin con el de un admin que cambia el rol de un turista. Destino: backlog si David quiere fijarlo — `app/services/user_access_policy.py:64-70`.
- [OPCIONAL] — Fase A — `test_be02_self_role_guard_identifies_the_actor_by_cedula` promete más de lo que fija. Mata el mutante local de la guarda (`actor is target`), pero no el global de l.57 (`is_self_update = actor is target` o por email): `415 passed` en ambos, porque con el gemelo salta la guarda de jerarquía y el test pasa por otra razón. Sin efecto real hoy: el email es único (`app/models/user.py:39`) y en HTTP actor y destino son la misma instancia dentro de la sesión de la petición. La l.57 es anterior a esta fase. Un gemelo con `{"first_name": …}` que no lance mataría ambos — `tests/test_user_access_policy.py:177-182`; `app/services/user_access_policy.py:57`.

### Comprobaciones sin hallazgo

- `progress.json`: JSON válido; `Fase_A` = `completed`, `commit` `f55313c` (real, `git show --stat`); `last_handoff` presente; el diff de `ab26fb4` solo toca `current_target`, `status`, `commit` y `last_handoff`; `edit_rules` intacto.
- Commit: mensaje idéntico al del plan (comparación programática, con `Claude Opus 5.5` en el trailer). Archivos: los 3 de la fase, numstat `12 5`, `3 3`, `173 0`. `a120cae` y `e5a20f0` son anteriores y no se cuentan.
- Cambios exactos 1-4: presentes en el diff, texto del plan. Tests: 10 funciones y 19 casos; cada fila de la tabla coincide con sus aserciones; ubicación y comentario de bloque, los que pide el plan.
- RED reproducido en copia desechable sin la guarda: `10 failed, 9 passed, 57 deselected`, los 10 de la tabla, iguales al handoff.
- Decisión 2 (conjuntos por archivo y línea, medidos con `ruff --output-format=json` en copias de `c6422ed` y `HEAD`):
  - `user_access_policy.py`: base D205 l.20, 40, 71, 88, 103, 122; E501 l.36, 67, 99. HEAD D205 l.21, 78, 95, 110, 129; E501 l.37, 74, 106. Es la base menos D205 l.40, con desplazamiento +1 antes de l.40 y +7 después.
  - `user_service.py`: I001 l.1, E501 l.46, 217, 337, B904 l.126, 130; idéntico a la base. mypy l.124, 132, 133.
  - `tests/test_user_access_policy.py`: 0. Los otros archivos: 39 errores, conjunto idéntico a la base. Salida completa de mypy idéntica a la base.
  - Según la decisión 2, los errores heredados en archivos tocados no son hallazgo.
- Decisión 4: `unfixable = ["I001"]` en `pyproject.toml:72`, dentro de `[tool.ruff.lint]`. `ruff check --fix` no cambia ninguno de los 3 archivos. Control: sin esa línea, en una copia, ruff reordena los imports de `user_service.py`. El motivo es real: con un `.env` ficticio, `SECRET_KEY` vale el secreto con el orden actual y `None` con el reordenado.
- Riesgo (b) del plan, por HTTP: `{"role": null}` sobre sí mismo 403, sobre un tercero 409. `{"is_active": false}` sobre sí mismo sigue en 200 (BE-35).
- AGENTS: sin excepción de dominio nueva (`AuthorizationError` ya registrada); regla dentro de `UserAccessPolicy`, sin `if role ==` en el servicio; sin mocks nuevos; fábricas de `conftest.py`; sin aserciones sobre texto en español; `refresh` tras la petición; sin cambios de esquema, `schemas` ni router.

### Verificación final del plan (ejecutada por el auditor)

V1 sin coincidencias (exit 1). V2 4 líneas, todas en la política (l.57, 59, 64, 69). V3 `user_service.py:279`. V4 2 líneas (l.175, 187). V5 10 funciones, `19 passed, 57 deselected`. V6 2. V7 3 archivos, `12 5`, `3 3`, `173 0`. V8 8, 6, `All checks passed!`, `Found 53 errors.` V9 `Found 10 errors in 5 files`, 3 en `user_service.py`, 0 en la política. V10 exit 1 solo por ruff check y mypy, 415 passed, 94.82 %, 4 KEPT.

### Mutantes de la regla (copia desechable, suite completa; control sin mutar: `415 passed`)

| Mutante | Resultado | Lo mata |
|---|---|---|
| M01 sin la guarda | 10 failed | los 10 RED |
| M02 valor verdadero en vez de clave | 1 failed | `…with_role_none_is_rejected` |
| M03 solo si el valor difiere del actual | 2 failed | `nobody[superadmin-superadmin]`, `…noop…` |
| M04 sin `is_self_update` | 3 failed | `…keeps_powers…`, `…third_party…`, `test_superadmin_can_mutate_role` |
| M05 toda auto-edición | 6 failed | 2 be02 de perfil y 4 existentes |
| M06 identidad en la guarda | 1 failed | `…identifies_the_actor_by_cedula` |
| M07 solo degradar a `tourist` | 5 failed | be02 |
| M08 solo payload con `role` a secas | 1 failed | `…with_profile_fields_mutates_nothing` |
| M09 `ValueError` / M10 `NotFoundError` | 10 failed cada uno | los 10 RED |
| M13 sin la guarda vieja de l.64 | 3 failed | 3 existentes de escalada de admin |
| M17 sin ninguna de las dos guardas (`-k be02`) | 16 failed, 3 passed | incluye los 6 casos de turista y admin que eran verdes |
| M11 guarda antes de l.64 | 415 passed, sobrevive | ver opcional 2 |
| M12 bloquea también `is_active` propio | 415 passed, sobrevive | a propósito: el plan no lo congela para no estorbar a BE-35 |
| M14 / M15 l.57 por identidad / email | 415 passed, sobreviven | ver opcional 3 |
| M16 política después de `setattr` | 415 passed, sobrevive | equivalente: sin commit, el cambio no se persiste |

Veredicto Fase A: **PASS (0 bloqueantes, 3 opcionales)**.

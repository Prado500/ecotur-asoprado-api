# Gaps BE-01

## Auditoría Fase A — 2026-10-27

Veredicto: PASS (0 bloqueantes, 2 opcionales). Compuerta re-ejecutada con `venv/Scripts` en PATH.

- [OPCIONAL] — Fase A — `python scripts/check.py` con el Python del sistema (3.14) falla por dependencias ausentes (jwt, mypy, importlinter); solo funciona con el venv del repo — evidencia: `ModuleNotFoundError: No module named 'jwt'`. Documentar en README/CONTEXT que la compuerta exige el venv activo.
- [OPCIONAL] — Fase A — el commit de handoff/progress (`7ad4711`) va separado del de código; correcto, pero el plan no lo exige. Sin acción.

Verificado sin hallazgos: hash 170839c real y solo toca `app/core/security.py`; mensaje de commit idéntico al plan (coautor = modelo ejecutor); los 4 imports muertos eliminados; `ruff check`/`ruff format --check` en security.py limpios; mypy security.py = mismos 2 errores `[arg-type]` de `SECRET_KEY` (l.71 y l.87, antes 72 y 92; desplazamiento por borrado de imports y reformato); `lint-imports` 3 kept / 1 broken con una sola ruta (`tourist_services_service -> core.storage -> fastapi`); pytest 116 passed; cobertura 89 % (= base); totales ruff 489 -> 473 y mypy 44 = 44 (no suben); `progress.json` válido, `current_target` = Fase_B, Fase_A completed con hash; árbol sin cambios en app/tests/docs.

## Auditoría Fase B — 2026-10-27

Veredicto: PASS (0 bloqueantes, 2 opcionales). Compuerta re-ejecutada con `venv/Scripts` en PATH.

- [OPCIONAL] — Fase B — el handoff dice que la compuerta global queda en rojo por deuda heredada (ruff 416, mypy 44); confirmado y no atribuible a la fase: los 5 archivos tocados tienen `ruff check` limpio, `ruff format --check` limpio y 0 errores de mypy — evidencia: `All checks passed!`, `5 files already formatted`, mypy sin líneas para los 5 archivos. Sin acción.
- [OPCIONAL] — Fase B — `promote_to_permanent` ya solo captura `AzureError` (antes `Exception`): una excepción no-Azure inesperada ahora sale como 500 por el fallback en lugar de 500 envuelto; coherente con la decisión 3 del plan. Sin acción.

Verificación de la decisión 7 (detail conservados letra a letra, `git show 8bf9815:app/core/storage.py`): sin cambios. `upload_image` MIME (base l.59-63) = `"El archivo {image.filename} no es una imagen válida."` idéntico (storage.py:115); `upload_image` fallo Azure (base l.86-88) = `"Fallo al comunicar con Azure CDN: {str(e)}"` idéntico (storage.py:145); `promote_to_permanent` conserva `"Fallo al consolidar las imágenes en el CDN."`. Solo cambian el tipo de excepción y la coma/indentación. Textos nuevos (`"La imagen debe provenir del contenedor temporal de imágenes."`, `"La imagen indicada no existe en el CDN."`) son los únicos añadidos y el plan los permite.

Verificado sin hallazgos: commit 867e56c real, mensaje idéntico al plan (coautor = modelo ejecutor), toca exactamente los 5 archivos de la fase; a052267 solo progress.json; `current_target` = Fase_C, Fase_B completed con hash, `edit_rules` intacto; `grep HTTPException|from fastapi app/core/storage.py` vacío; ambas excepciones registradas en `_DOMAIN_ERROR_STATUS` (415 y 400); `lint-imports` 4 kept, 0 broken; pytest 135 passed (116 + 19); cobertura total 93 % (base 89 %), storage.py 100 %; ruff total 473 -> 416, mypy total 44 = 44 (no suben); árbol limpio.

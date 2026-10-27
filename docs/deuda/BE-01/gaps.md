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

## Auditoría Fase C — 2026-10-27

Veredicto: PASS (0 bloqueantes, 2 opcionales). Compuerta re-ejecutada con `venv/Scripts` en PATH.

- [OPCIONAL] — Fase C — el diff del servicio incluye reformato mecánico de `update_package_details` (343 ins / 129 del en 3 archivos) aunque el plan la declara fuera de alcance; la lógica no cambia (handoff lo declara) y es consecuencia de exigir ruff 0 en el archivo — evidencia: `git show --stat c5fc0b7`. Fase D debe revisar su diff con `-w`.
- [OPCIONAL] — Fase C — `python scripts/check.py` sigue en rojo global (ruff format, ruff check 362, mypy 44) por deuda heredada de archivos no tocados; no atribuible a la fase — evidencia: `Found 362 errors.`, `Found 44 errors in 12 files`.

Verificado sin hallazgos: c5fc0b7 real, mensaje idéntico al plan, toca exactamente los 3 archivos de la fase (6302530 solo handoff + progress.json); `progress.json` con Fase_C completed/c5fc0b7 y `current_target` = Fase_D; los 6 tests nuevos (rechazo URL ajena, permanente, blob inexistente, 503 en promoción, feliz con `assert_awaited_once_with`, 415) más el test de outage modificado existen y pasan; `grep "except Exception"` en el servicio vacío; `InvalidImageUrlError` importado y `StorageUnavailableError` ya no; `ruff check` y `ruff format --check` limpios en los 3 archivos; mypy del servicio = mismos 10 errores, solo desplazados (74,128,136,165,166,173,206,207,215,331), 44 = línea base; ruff total 416 -> 362; pytest 141 passed; cobertura 93 % (base 89 %); `lint-imports` 4 kept, 0 broken; árbol limpio.

# Gaps — BE-33

## Auditoría Fase A — 2026-11-06

**Veredicto: PASS (0 bloqueantes, 2 opcionales).** Auditado sobre `f960ae9` (commit de fase `6a3489d`), árbol limpio.

Compuerta re-ejecutada con `./venv/Scripts/python.exe scripts/check.py`, exit 1:

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

```text
54 files already formatted
Found 49 errors.
Found 10 errors in 5 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
416 passed, 5 warnings in 11.62s
```

Hallazgos:

- [OPCIONAL] — Fase A — La expectativa de V12 (`56 files already formatted`) quedará desfasada: tras la fase D serán 57 (54 de hoy + 3 tests nuevos). La causa es `.claude/hooks/notify_sound.py` (`7d02d14`), posterior a la base y ajeno a BE-33. El auditor de la fase D debe contar 57; 56 no sería un fallo de formato ni 57 una regresión — `docs/deuda/BE-33/plan.md:590`; `git diff --name-status bab25c2 HEAD -- '*.py'` lista ese archivo como `A`; la compuerta da 54 frente a los 53 de `verificacion.md:110`.
- [OPCIONAL] — Fase A — `AuditLogCreate` no se usa en ninguna parte, pero su docstring dice que la capa de servicio la usa. Es anterior a la fase: el plan fija el texto y deja el `pass` fuera de alcance. Destino sugerido: backlog (eliminar la clase o corregir el docstring) — `app/schemas/audit.py:17-18`; `git grep -n AuditLogCreate -- app tests` solo devuelve la definición.

No comprobado: la salida del hook de edición (`handoff-Fase_A.md:145`) y el `git fetch origin` del arranque (`handoff-Fase_A.md:23`) ocurrieron en la sesión del ejecutor. `origin/develop` y el `merge-base` valen `bab25c2` en la referencia local, sin refrescar en esta auditoría.

## Auditoría Fase B — 2026-11-06

**Veredicto: PASS (0 bloqueantes, 5 opcionales).** Commit de fase `b9a8907`, progreso `09601ee`. La compuerta se corrió dos veces: sobre `09601ee` y sobre `6301ca5`, un commit de David que entró durante la auditoría y solo toca `docs/aprendizaje/fichas/BE-33.md`. Dieron los mismos conteos.

Compuerta re-ejecutada con `./venv/Scripts/python.exe scripts/check.py`, exit 1:

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

```text
55 files already formatted
Found 41 errors.
Found 9 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
421 passed, 5 warnings in 12.07s
```

Hallazgos:

- [OPCIONAL] — Fase B — Ningún test distingue "la fila de este `id`" de "la única fila de la tabla": todos corren con 0 o 1 filas. Quitar el `WHERE` de `save_service` no lo detecta nadie. Con una segunda fila, un test candidato lo mata (`MultipleResultsFound`). Fuera de la tabla de tests del plan; la fase C o BE-32 pueden añadirlo — `tests/test_service_repository.py:48-107`; `app/repositories/service_repository.py:94`; mutante M5: `5 passed` en el archivo y `421 passed` en la suite completa.
- [OPCIONAL] — Fase B — `assert saved.id == package.id` no demuestra casi nada: `saved is package` da `True` por el mapa de identidad. Al retirar las dos aserciones, los 11 mutantes siguen muertos o vivos igual, y la única diferencia es que `returns_a_soft_deleted_row` deja de matar a M11, que fabrica una instancia con `id=-1`. En `test_save_service_commits_pending_changes_and_returns_the_row` M11 cae sin esa aserción, por el `refresh`. Con una segunda fila la aserción sí actúa (M6: `assert 2 == 1`). La tabla del plan pide "mismo `id`": no es incumplimiento — `tests/test_service_repository.py:59,92`; matrices A y B de la medición.
- [OPCIONAL] — Fase B — `assert saved.deleted_at is not None` no fija el valor: reescribir `deleted_at` a otra fecha dentro de `save_service` sobrevive. La forma exacta lo mata y tiene que ser `deleted_at.replace(tzinfo=None)`, porque SQLite devuelve la fecha sin zona. El handoff lo declara y la tabla del plan lo admite — `tests/test_service_repository.py:93`; `handoff-Fase_B.md:208`; mutante M10: `5 passed` y `421 passed`; matriz C: `1 failed, 5 passed`.
- [OPCIONAL] — Fase B — El docstring de `test_save_service_raises_when_the_row_was_physically_deleted` dice "behind the entity's back", pero el `delete()` corre en la misma sesión y la sincroniza: tras él, `package in db_session` es `False`. El test sí falla por su razón (`DID NOT RAISE` antes del cambio), pero no ejercita un borrado hecho por otra sesión — `tests/test_service_repository.py:74,76`; sonda: `t3 after delete: persistent=False deleted=True ... in_session=False`.
- [OPCIONAL] — Fase B — La justificación de la decisión 4 es inexacta en 2 de los 3 llamadores que ignoran el retorno, y parcial en el tercero. Con la fila borrada desde otra sesión y un cambio pendiente, `commit()` lanza `StaleDataError` antes de llegar a `first()` o `scalar_one()`, igual antes y después de la fase. Solo un toggle sin cambio neto alcanza esa rama: antes respondía éxito con 1 fila de auditoría; ahora lanza `NoResultFound` con 0. La decisión y el código siguen siendo correctos, y el ejecutor copió el texto del plan letra a letra. Lo inexacto es el argumento que David debe sustentar, y `Raises` omite `StaleDataError`. Destino sugerido: corregir plan y ficha; el mensaje de `b9a8907` ya no se cambia — `docs/deuda/BE-33/plan.md:80-81`; cuerpo de `b9a8907`; `docs/aprendizaje/fichas/BE-33.md:110-111`; `app/repositories/service_repository.py:86-88`; sonda sobre `tourist_services_service.py:129,168,209`, tabla de abajo.

```text
Llamador con la fila ya borrada     Antes de la fase (first)       Después (scalar_one)
toggle con cambio (l.129)           StaleDataError, 0 auditorías   StaleDataError, 0 auditorías
toggle sin cambio (l.129)           éxito, 1 auditoría             NoResultFound, 0 auditorías
soft_delete (l.168)                 StaleDataError, 0 auditorías   StaleDataError, 0 auditorías
recover (l.209)                     StaleDataError, 0 auditorías   StaleDataError, 0 auditorías
```

Evaluación de los 5 tests contra AGENTS §5 y `test-sanitizer`, con 11 mutantes sobre una copia desechable. Los cinco pueden fallar por la razón que declaran y cumplen el reparto de 1 feliz, 2 de fallo y 2 de borde.

| Test | Lo que lo mata | Lo que no demuestra |
|---|---|---|
| `commits_pending_changes_and_returns_the_row` | sin `commit` (M3), `flush` en vez de `commit` (M4) | "the row": hallazgos 1 y 2 |
| `raises_when_the_row_never_existed` | `first()` (M1, RED), `return service` (M7) | corre con la tabla vacía: hallazgo 1 |
| `raises_when_the_row_was_physically_deleted` | `first()` (M1, RED), `return service` (M7) | borrado desde otra sesión: hallazgo 4 |
| `returns_a_soft_deleted_row` | filtro `deleted_at IS NULL` (M8), `deleted_at = None` (M9) | el valor de `deleted_at`: hallazgo 3 |
| `returns_the_row_with_its_images_loaded` | sin `selectinload` (M2, `MissingGreenlet`) | nada que señalar |

No comprobado:

- La salida del hook de edición (`handoff-Fase_B.md:187`) y el `git fetch origin` del arranque (`handoff-Fase_B.md:21`) ocurrieron en la sesión del ejecutor. `origin/develop` y el `merge-base` valen `bab25c2` en la referencia local, sin refrescar en esta auditoría.
- El RED del handoff se reprodujo con el mutante M1 sobre la copia, no sobre el árbol anterior al commit: solo cambia la línea de retorno.
- Las mediciones de mutación y de la sonda corrieron sobre SQLite en memoria con variables ficticias. `StaleDataError` no se midió en PostgreSQL ni `update_package_details` (l.347) con la fila ausente.

Durante la auditoría, `docs/aprendizaje/fichas/BE-33.md` apareció modificado; David lo commiteó en `6301ca5`, y el árbol estaba limpio antes de escribir este bloque. No es hallazgo de la fase: ni `b9a8907` ni `09601ee` lo tocan.

## Auditoría Fase C — 2026-11-06

**Veredicto: PASS (0 bloqueantes, 6 opcionales).** Commit de fase `0c076b4` (padre `7f8a103`), progreso `3c85e13`, rama `item/be-33`, árbol limpio antes de escribir este bloque.

Compuerta re-ejecutada con `./venv/Scripts/python.exe scripts/check.py`, exit 1:

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

```text
56 files already formatted
Found 20 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
app\api\dependencies.py                       53      1      6      0  98.31%   63
TOTAL                                        943     27    138     19  95.74%
432 passed, 5 warnings in 11.79s
```

Contraste con el plan, medido:

- **Mensaje de commit:** comparado por programa contra `plan.md`, con `<MODELO EJECUTOR>` sustituido por `Claude Opus 5.5`: idéntico, 1186 caracteres.
- **Alcance y `numstat`:** solo los 5 archivos de la fase; `16 12`, `3 2`, `19 13`, `15 9` y `166 0`. `3c85e13` solo toca el handoff y `progress.json`.
- **Decisión 2:** ruff solo da I001 l.1 en `dependencies.py` y `user_service.py`, y 0 en los otros tres; mypy da `dependencies.py:95` y `user_service.py:124`, y 0 líneas `^tests`. Totales: I001 9, E501 8, W293 3.
- **V5, V7 y V8:** 0 y 3 líneas; 4 y 4; `usuario` y `email: str | None` en 0, y los 4 `noqa` UP042.
- **V9, extraído de `plan.md`:** `code=same` en `user_access_policy.py` y `strings=exact` en los diez archivos. `code=changed` solo en los cuatro que el plan espera.
- **RED real:** el test nuevo sobre el `app/` de `7f8a103` da `4 failed, 7 passed`, en las líneas 143 y 165 (`__cause__`).
- **Mutación del plan (401 → 403):** `7 failed, 4 passed`.
- **`progress.json`:** JSON válido; fase `completed` con hash real; `current_target` en `Fase_D`; `last_handoff` presente; `edit_rules` intacto.
- **`/openapi.json` entre `7f8a103` y `0c076b4`:** una sola diferencia, `/components/schemas/TokenResponse/description`. `properties` idénticas; `TokenData` no aparece. Es lo que el plan espera.
- **Respuestas HTTP:** 21 casos de token en `/usuarios/mi-perfil` y `/usuarios/verificar-email`, con estado, `WWW-Authenticate` y cuerpo idénticos entre padre y commit. Incluye `sub` nulo, entero y vacío, tras el cambio de `TokenData.email`.

Hallazgos:

- [OPCIONAL] — Fase C — `plan.md:353` promete más de lo que el test demuestra. La columna "Cubre" dice "ramas no intercambiadas", pero el test solo prueba que los dos `detail` son distintos. Intercambiar los textos (D1) e intercambiar las ramas (D2) sobreviven a la suite completa. No es bloqueante porque el test existe, pasa y cumple la columna "Esperado" ("`detail` distintos"), y el ejecutor lo declaró. D1 no se puede detectar sin leer el texto (AGENTS §5) o sin un código de error nuevo. D2 sí: un test candidato que exige `detail` de token corrupto igual al de usuario desconocido lo mata, y D1 lo sigue pasando. Destino sugerido: corregir la columna con una enmienda y llevar el candidato a BE-32 — `docs/deuda/BE-33/plan.md:353`; `tests/test_token_failure_paths.py:93-98`; D1 y D2: `11 passed` y `432 passed`; candidato bajo D2: `1 failed, 1 passed`.
- [OPCIONAL] — Fase C — En `verify_email_account`, la pérdida de `from err` se detecta en cada rama (U2, U3, U4, U5), pero ningún test distingue sus mensajes. Intercambiarlos (U1), responder a un token vencido con el mensaje de corrupto (U6) e invertir los `except` (U7) sobreviven a la suite completa. Las mutaciones equivalentes en `get_current_user` (D3, D4) sí mueren. Un candidato con `str(expired) != str(corrupt)` mata U6 y U7, no U1. La tabla del plan no lo exigía. Destino sugerido: BE-32 — `app/services/user_service.py:125-132`; `tests/test_user_service.py:254-281`; U1, U6 y U7: `11 passed` y `432 passed`.
- [OPCIONAL] — Fase C — Ningún test de la suite rechaza un token firmado con otra clave. Hoy el comportamiento es correcto: 401 en la ruta protegida y 400 en la verificación. Pero con `verify_signature` apagado y `verify_exp` encendido, la suite sigue en verde (D20 y U14) mientras un token falsificado recibe 200 en ambas rutas. La brecha es anterior a la fase y el plan no la pedía, pero es la de mayor riesgo de esta lista: un fallo de autenticación pasaría inadvertido. Destino sugerido: BE-32 o fila propia con prioridad — `app/api/dependencies.py:95`; `app/services/user_service.py:124`; D20 y U14: `11 passed` y `432 passed`; sonda: `forged_access_token 401 → 200`, `forged_verification_token 400 → 200`.
- [OPCIONAL] — Fase C — Ningún test fija que el token de un usuario con borrado lógico se rechace por `deleted_at`. Si la búsqueda incluye a los borrados (D17), la suite sigue en verde y ese usuario, activo, recibe 200. `soft_delete_user` también pone `is_active = False`, así que ese estado no se alcanza por la ruta normal. Destino sugerido: BE-32 — `app/api/dependencies.py:111`; `app/repositories/user_repository.py:61-62`; D17: `11 passed` y `432 passed`; sonda: `soft_deleted_active_user 401 → 200`.
- [OPCIONAL] — Fase C — `test_valid_token_on_protected_route_returns_the_user` y `test_token_for_unknown_user_returns_401` corren con 1 y 0 usuarios, así que no distinguen "el usuario que nombra el token" de "el único usuario". Si la búsqueda ignora `sub` (D11), el archivo da `11 passed`. La suite completa sí lo detecta (`11 failed`, en `test_auth.py`, `test_user_access_policy.py` y `test_user_response.py`), de modo que la propiedad está protegida; lo que queda corto es el docstring "the active user it names" — `tests/test_token_failure_paths.py:63-72,110-116`.
- [OPCIONAL] — Fase C — `user_repo.activate_user.assert_not_called()` aporta poco en el caso `expired`. `_expired_token` no lleva `scope`, y la aserción de causa va antes: con la expiración apagada (U9) el test cae en la l.165, y con expiración y `scope` apagados (U13), en `DID NOT RAISE` (l.162). Solo la alcanza un mutante que active antes de lanzar (U8). Sin esa línea, U8 pasa el archivo (`11 passed`) y la suite lo sigue detectando (`1 failed`) por `tests/test_user_service.py:281`. No es vacua, pero sí redundante. Destino sugerido: BE-32 — `tests/test_token_failure_paths.py:33-35,165-166`.

Evaluación de los 9 tests (11 casos) contra AGENTS §5 y `test-sanitizer`, con 29 mutantes sobre una copia desechable, cada uno contra el archivo y contra la suite completa, y 4 dirigidos (D21 a D24) solo contra el archivo. Reparto: 1 feliz, 3 de fallo y 3 de borde, más 4 casos de causa.

| Test | Lo que lo mata | Lo que no demuestra |
|---|---|---|
| `valid_token_..._returns_the_user` | `is_active` invertido (D23, `401 == 200`), otra `cedula` en el usuario devuelto (D24) | quién es el usuario con una sola fila: D11 |
| `expired_token_..._returns_401` | expiración apagada (D12), sin cabecera (D13), 403 (D16) | nada que señalar |
| `corrupt_token_..._returns_401` | sin cabecera (D14), 403 (D16) | "never reaches the user lookup": lo prueba el test de causa (D15) |
| `expired_and_corrupt_..._distinct_details` | mismo `detail` (D3), `except` invertidos (D4), D12 | el intercambio: D1 y D2 |
| `token_without_subject_returns_401` | sin la guarda de `sub` (D8, `ValidationError`), D14, D16 | nada que señalar |
| `token_for_unknown_user_returns_401` | sin `user is None` (D9, `AttributeError`), D14, D16 | con la tabla vacía: D11 |
| `token_for_inactive_user_returns_401` | sin `is_active` (D10), D14, D16 | nada que señalar |
| `get_current_user_chains_...` (2) | sin `from err` (D5, D6, D7), repositorio consultado antes (D15), D16 | nada que señalar |
| `verify_email_chains_...` (2) | sin `from err` (U2, U3, U4, U5), activar antes de lanzar (U8), U9, U13 | el texto (U1, U6, U7) y `activate_user`: hallazgo 6 |

Las aserciones de `_assert_bearer_401` actúan: `set(body)` mata un manejador que añade una clave (D22), `isinstance` mata un `detail` que no es `str` (D21) y la cabecera mata D13 y D14. `user_repo.mock_calls == []` tampoco es vacua: sin ella, D15 sobrevive a la suite (`432 passed`). Ningún test afirma sobre texto en español.

Sin hallazgo: el doble de `UserRepository` no es infraestructura externa (AGENTS §5), pero `plan.md:346` lo dicta y `tests/test_user_service.py:65` es el precedente. El fixture local `user_repo` duplica ese mismo archivo, y el plan prohíbe tocar `conftest.py`.

No comprobado:

- La salida del hook de edición, la edición paralela y el `git fetch origin` del arranque ocurrieron en la sesión del ejecutor. `origin/develop` y el `merge-base` valen `bab25c2` en la referencia local, sin refrescar en esta auditoría.
- Las mutaciones, la sonda HTTP y `/openapi.json` corrieron con variables ficticias sobre copias desechables. Las de HTTP y tests usaron SQLite en memoria, no PostgreSQL.
- La sonda HTTP cubre `/usuarios/mi-perfil` y `/usuarios/verificar-email`, no cada ruta que depende de `get_current_user`.
- Los candidatos citados no están en el repo: solo se midieron en la copia.
- Este bloque se limita a la fase C: la "Verificación final" completa corresponde a la fase D.

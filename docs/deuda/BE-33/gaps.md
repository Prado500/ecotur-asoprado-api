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

## Auditoría Fase D — 2026-11-06

**Veredicto: PASS (0 bloqueantes, 8 opcionales).** Commit de fase `c60ad12` (padre `0f9e178`), progreso `862e85e`, rama `item/be-33`, árbol limpio antes de escribir este bloque. Es la última fase: incluye la "Verificación final" completa.

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
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
app\api\dependencies.py                       53      1      6      0  98.31%   63
TOTAL                                        943     23    138     19  96.11%
438 passed, 5 warnings in 16.23s
```

Contra la línea base de `verificacion.md`: pytest 416 → 438, cobertura 94.82 % → 96.11 %, ruff 53 → 9, mypy 10 → 5, 4 KEPT. Los ocho I001 de `app/` y el de `tests/test_user_service.py:3` y los cinco `str | None` son lo que el plan deja en rojo.

Contraste con el plan, medido:

- **Mensaje de commit:** comparado por programa contra `plan.md`, con `<MODELO EJECUTOR>` sustituido por `Claude Opus 5.5`: idéntico, 888 caracteres.
- **Alcance y `numstat`:** solo los 3 archivos de la fase; `42 10`, `1 1` y `126 0`. `862e85e` solo toca el handoff y `progress.json`.
- **Cambios exactos:** los 4 bloques de CSS y los 3 del cuerpo aparecen en `email.py` con el texto y la sangría del plan. El comando de W293 sobre una copia del padre da `3 fixed`, y `database.py` queda con el mismo SHA-256 que en `c60ad12`.
- **Tests:** los 6 de la tabla existen y pasan. Sobre el `email.py` del padre también dan `6 passed`, como pide el plan. La mutación del plan (`href="#"`) da `1 failed, 5 passed`.
- **Decisión 2:** ruff solo da I001 l.1 en `email.py` y `database.py`, y 0 en `tests/test_email.py`; mypy da `database.py:11` y 0 líneas `^tests`. `email.py` al 100 %.
- **`progress.json`:** JSON válido; fase `completed` con hash real; `current_target` en `Auditoria`; `last_handoff` presente; `edit_rules` igual que al crearse. El diff de `862e85e` cambia solo esos campos.

Verificación final sobre `862e85e`:

| V | Resultado | Esperado |
|---|---|---|
| V1 | `All checks passed!` | igual |
| V2 | `Found 9 errors.`, los 9 I001: 8 en `app/` l.1 y `tests/test_user_service.py:3` | igual |
| V3 | 0 líneas | igual |
| V4 | `security.py:71`, `:87`, `database.py:11`, `user_service.py:124`, `dependencies.py:95`; `Found 5 errors in 4 files` | igual |
| V5 | 0 líneas; 3 líneas (`dependencies.py:96`, `user_service.py:134,135`) | igual |
| V6 | `first()` l.75; `scalar_one()` l.26 y l.97 | igual |
| V7 | 4 `from err` y 4 `as err`, 2 y 2 por archivo | igual |
| V8 | 0, 0, 0, y 4 `noqa` UP042 | igual |
| V9 | salida idéntica a la tabla del plan (`diff` sin diferencias); `email.py code=same strings=whitespace-only` | igual |
| V10 | 13 archivos; `numstat` de `app/` igual a los criterios de cada fase | igual |
| V11 | 5, 9 y 6 funciones; `22 passed`; 0 líneas `^tests` | igual |
| V12 | exit 1 solo por `ruff check` y `mypy`; 438; 96.11 %; 4 KEPT; Missing `63`; `email.py` al 100 %; `57 files` | igual, con E1 |

Única diferencia con el texto del plan: `plan.md:590` dice 56 archivos formateados y salen 57. E1 lo corrige y lo explica. V3 y V4 filtran una sola corrida de mypy guardada en un archivo: el filtro es el del plan.

Cuerpo renderizado entre `0f9e178` y `c60ad12`, con las dos versiones cargadas desde copias y el envío sustituido por un doble:

- Con espacios colapsados, **idéntico**: mismo SHA-256 y la misma secuencia de 252 tokens, así que ningún salto añadió ni quitó una separación. También coinciden el texto visible, el CSS, los atributos colapsados, los `href` sin colapsar, los 2 enlaces, el asunto, los destinatarios y el `subtype`.
- En bytes cambia: 2608 → 3092 bytes y 43 → 75 líneas.
- **Dos atributos `style` contienen ahora un salto de línea; ninguno lo tenía antes:** `<a>`: `'color: #ffffff !important;\n                        text-decoration: none;'`; `<p>`: `'font-size: 12px; color: #006875;\n                    word-break: break-all;'`.
- El MIME construido en local con `MailMsg`, sin enviar nada, va en `text/html` y base64; decodificado es igual al cuerpo, saltos incluidos.

Frontera con A4 desde `bab25c2`:

- **I001:** el mismo conjunto de 9, por archivo y línea (`diff` entre `bab25c2` y `HEAD` sin diferencias).
- **`str | None`:** los mismos 5, salvo `dependencies.py:92` → `:95`, que la decisión 2 prevé.
- **Imports:** idénticos, en texto y línea, en los 10 archivos.
- **`email.py`:** `conf`, `fast_mail` y `load_dotenv` idénticos; l.1-29 y el bloque desde `MessageSchema` hasta el envío, sin cambios.
- **`database.py`:** l.7-12 idénticas; solo cambia la l.16 (W293).
- **`jwt.decode`:** mismo texto en `dependencies.py` (l.92 → l.95) y `user_service.py:124`.
- **Sin cambios:** `pyproject.toml`, `alembic/`, `.azure-pipelines/`, `security.py`, `conftest.py` y `docs/backlog.md`. De `tests/` solo hay 3 archivos añadidos.

Hallazgos:

- [OPCIONAL] — Fase D — `body.count(VERIFICATION_LINK) == 2` demuestra dos apariciones, no que la segunda sea texto plano, como dice el nombre del test. Quitar o cambiar el segundo enlace muere (L2, L3), y una tercera copia también (L6). Moverlo a un comentario HTML (L4) o a un atributo `data-link` (L5) sobrevive a la suite. Un test candidato con `handle_data` mata L2 a L5 en la copia. Ocultarlo con `display: none` (L20) sobrevive a todo. Destino sugerido: BE-32 — `tests/test_email.py:73-77`; L4, L5 y L20: `6 passed` y `438 passed`.
- [OPCIONAL] — Fase D — La suite no fija lo que hace visible el botón ni el segundo `style`. `anchor["class"] == "btn"` fija un solo lado: renombrar el selector `.btn` del CSS (L15) sobrevive, y deja texto blanco sin fondo. También sobreviven dejar el `<a>` sin texto (L14), cambiar una regla por otra vacía con el mismo número de llaves (C10) y borrar el `style` del `<p>` (L17), uno de los dos que la fase partió. La tabla del plan no lo pedía. Hoy lo cubren V9 y la revisión visual pendiente, pero ninguna de las dos queda en la suite. Destino sugerido: BE-32 — `tests/test_email.py:84,87,125`; `app/core/email.py:57,90,94`; L14, L15, L17 y C10: `6 passed` y `438 passed`.
- [OPCIONAL] — Fase D — `isinstance(message.subject, str)` es vacua. Medida aparte en 68 mutantes, no falla por su razón en ninguno: `subject=None` (S3) y `subject=123` (S4) lanzan `ValidationError` antes de capturar el mensaje, porque el esquema declara `subject: str`. Solo se dispara en D5, por un `AttributeError` sobre una lista, y ahí el test real ya ha caído en l.67. La pide el plan (`plan.md:457`) y el handoff lo declara. La que actúa es l.69 (S1, S2) — `tests/test_email.py:68`; `venv/Lib/site-packages/fastapi_mail/schemas.py:46`.
- [OPCIONAL] — Fase D — `assert_awaited_once_with(message)` compara el argumento consigo mismo, porque `message` se captura de esa misma llamada. Enviar una copia con otro asunto (D8) sobrevive. No es vacua: mata la doble llamada (D1) y un argumento extra (D3), y D3 es lo único que aporta sobre `assert_awaited_once()`, deducido porque D3 hace una sola llamada. El handoff lo declara — `tests/test_email.py:52,66`; D8: `6 passed` y `438 passed`.
- [OPCIONAL] — Fase D — `_send_and_capture` depende de que el mensaje se pase por posición. `send_message(message=message)` (D4), con el mismo comportamiento, pone en rojo 4 tests con `IndexError`. Es una falsa alarma ante un refactor, no un falso verde. Destino sugerido: BE-32 — `tests/test_email.py:52`.
- [OPCIONAL] — Fase D — El argumento "HTML y CSS colapsan esos espacios, también dentro de `style`" y el "No text or attribute changes" del commit son inexactos en la parte de HTML. `html.parser` conserva el salto y la sangría en el valor de los dos atributos. Lo que puede hacerlos equivalentes es que CSS ignore esos espacios al leer las declaraciones. Eso no se midió en ningún cliente de correo, y es justo lo que la revisión visual debe mirar en el botón y en el enlace de texto. El código no cambia; el cuerpo de `c60ad12` no se reescribe (AGENTS §9). Destino sugerido: precisarlo en la descripción del PR — `docs/deuda/BE-33/plan.md:66`; cuerpo de `c60ad12`; `app/core/email.py:89-90,94-95`.
- [OPCIONAL] — Fase D — Los precedentes de `current_target = "Auditoria"` son reales, pero `docs/CONTEXT.md` los registra como defecto de flujo. `ab26fb4` (BE-02), `2a1ee41` (BE-15) y `9971898` (AF-05) lo dejaron así; David lo puso en `null` a mano en BE-02 (`a222217`) y BE-15 (`1f547a8`), y AF-05 sigue en `Auditoria`. El handoff no menciona esa nota. Su razón es correcta: con `null`, `read_progress` daría el ítem por ejecutado antes de la auditoría. Pero contradice lo que pide la nota de `CONTEXT`, y esa contradicción la tiene que resolver David. Destino sugerido: `null` a mano al cerrar BE-33 y aclarar cuándo se pone — `docs/deuda/BE-33/handoff-Fase_D.md:288-289`; `docs/CONTEXT.md:292`; `.claude/agents/fase-ejecutor.md:55`; `scripts/check_docs.py:471-477`.
- [OPCIONAL] — Fase D — `--estado` mostraba `última auditoría: con gaps` porque solo busca `PASS` en la última línea de `gaps.md`, y la de BE-33 era una viñeta de "No comprobado". No lee veredictos ni bloqueantes. El mismo efecto tienen A9, AF-05, BE-01 y SEC1, con veredictos PASS y 0 bloqueantes. Es deuda conocida (AF-02 punto 3), que solo recoge ese efecto. Medido con `--root` sobre carpetas de prueba: un `gaps.md` con `[BLOQUEANTE]` y última línea `no es PASS` da PASS; con una línea en blanco final da `con gaps`; vacío lanza `IndexError`, aunque `estado()` promete devolver siempre 0. Destino sugerido: AF-02 — `scripts/check_docs.py:523-526`; `docs/backlog.md:163`; `docs/CONTEXT.md:294`.

Evaluación de los 6 tests contra AGENTS §5 y `test-sanitizer`, con 68 mutantes de `email.py` sobre una copia desechable: 52 muertos y 16 vivos en el archivo. Cada aserción se midió también por separado, con una versión del test que no se detiene en el primer fallo. Reparto: 2 de camino feliz, 2 de fallo y 2 de borde. Solo se dobla SMTP, con `autospec`, que actúa: un argumento fuera de firma (D7) da `TypeError`. Ninguna aserción lee texto en español: `"María José"` es entrada del test. Con un guardián sobre `Connection.__aenter__`, que sí salta si se envía sin doble, la suite completa da `SMTP_ATTEMPTS=0`.

| Test | Lo que lo mata | Lo que no demuestra |
|---|---|---|
| `dispatches_one_html_message_...` | destinatario fijo, extra, duplicado o vacío (R1, R2, R3, R5), `plain` (T1), asunto vacío (S1, S2), doble envío (D1), sin `await` (D2), argumento extra (D3) | nombre visible con la misma dirección (R4), asunto en blanco (S5), hallazgos 3 y 4 |
| `body_carries_the_link_...` | `href` (L1, L16), segundo enlace (L2, L3, L6), ruta y token (L8, L9), ancla extra (L7), `class` (L10, L11), `style` (L12, L13, L19) | hallazgos 1 y 2 |
| `smtp_failure_propagates` | tragarse el error (E1), envolverlo (E2), error nuevo (E3), reintento (E4) | nada que señalar |
| `invalid_recipient_...` | tragarse `ValidationError` (V1), sin validar (V2), envío previo de respaldo (V4, solo por `assert_not_called`) | nada que señalar: el error sale de `('recipients', 0)` |
| `compound_first_name_verbatim` | primera palabra (N1), mayúsculas (N2), sin acentos (N5), nombre omitido o fijo (N6, N7) | `.title()` (N3) y `html.escape` (N4): sin efecto hoy, porque `UserCreate` ya aplica `.title()` y rechaza `<b>x</b>` y `A&B` |
| `css_braces_are_rendered_unescaped` | ver abajo | qué reglas son (C9, C10) |

Los vivos que no son hallazgo: L18 y C7 solo cambian espacios y deben sobrevivir, y T3 es equivalente porque Pydantic convierte `"html"` en el enum. Las aserciones de mock de l.99 y l.107 no llevan argumentos, y no hace falta: l.99 es la única que mata el reintento (E4), l.107 la única que mata V4, y los argumentos de la llamada los fija el test de envío. `style is not None` (l.86) estrecha el tipo para mypy y actúa ante un `style` sin valor (L19).

**`body.count("{") == 9`: caracterización legítima, sin hallazgo.** La tabla del plan la exige (`plan.md:462`). Protege el riesgo real de esta fase: perder una llave de una regla sigue siendo un f-string válido, y lo detectan el conteo (C3, C4) y nada más en el archivo original. Es insensible a los espacios (C7, L18 viven), que es lo que la fase necesita. Su fragilidad existe: añadir una regla legítima (C1) o un bloque `@media` (C8) la pone en rojo. El coste es actualizar un número, y a cambio avisa de que cambió la estructura del CSS, que ningún otro test mira. La alternativa, `count("{") == count("}")`, candidata medida en la copia, evita esas dos falsas alarmas y mata C3 y C4, pero deja vivo C2 (borrar una regla). `"{{" not in body` y `"}}" not in body` fallan en C5, C6 y C11, pero nunca solas: en los tres cae también un conteo. No son vacuas; solo un mutante del todo compensado las necesitaría, y ese no se midió.

Pendiente de David antes de `/pr`, sin ser incumplimiento de la fase:

- **Revisión visual del correo (E0, punto 3).** Ningún agente la hizo y esta auditoría tampoco. Se declara en "cómo se probó" del PR. Conviene mirar el botón y el enlace de texto, los dos elementos cuyo `style` tiene ahora un salto de línea.
- `current_target` a `null` al cerrar el ítem (hallazgo 7).

No comprobado:

- Ningún cliente de correo ni navegador pintó el HTML, y no se envió ningún correo.
- La salida del hook de edición y el `git fetch origin` del arranque ocurrieron en la sesión del ejecutor. `origin/develop` y el `merge-base` valen `bab25c2` en la referencia local, sin refrescar en esta auditoría.
- El orden "tests antes de editar" del handoff no se puede reconstruir. Lo que se midió es que los 6 tests pasan sobre el `email.py` del padre.
- Las mutaciones, el renderizado y las sondas corrieron con variables ficticias sobre copias, con SQLite en memoria. La compuerta sí corrió en el repo.
- De los 16 vivos, 13 se corrieron contra la suite completa (`438 passed` en todos); L18, C7 y T3 solo contra el archivo.
- En la medición aparte, si `pytest.raises` no salta, l.98 también cuenta como fallo: sus cifras incluyen ese arrastre. Los candidatos citados no están en el repo.
- Lo dicho sobre N3 y N4 se midió solo con `UserCreate`. `UserUpdate` declara el mismo patrón y validador, leído y no medido; otras vías de escritura de `first_name` no se revisaron.

Esta línea final deja que `--estado` lea el resultado (hallazgo 8). Veredicto Fase D: **PASS (0 bloqueantes, 8 opcionales)**.

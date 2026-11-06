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

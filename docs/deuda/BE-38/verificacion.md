# Verificación — BE-38: la auditoría registra las claves enviadas, no los cambios reales

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (sección A, fila BE-38, línea 90; rincón 5 de `docs/deuda/BE-02/verificacion.md:96-97`;
nota de BE-37 en la misma fila; residual R5 de `docs/deuda/BE-37/plan.md:445-446`). No hay tag del informe de sep-2026.
**Fecha:** 2026-11-17

## Qué describe el ítem
Las dos rutas de modificación (`PATCH /usuarios/{cedula}` y `PUT /servicios/{id}`) escriben en `audit_logs.changes` el
cuerpo validado tal como llegó (`model_dump(exclude_unset=True)`), no lo que cambió: una clave con el mismo valor que ya
tenía la fila genera una fila `UPDATE` aunque nada mute. La fila pide registrar solo lo que cambió (antes/después) con
test de no-op; la nota de BE-37 añade `{"image_urls": null}` en paquetes y deja a David decidir si el ítem alcanza a paquetes.

**Referencia cruzada errónea en la fila:** "Relación con BE-29 (auditoría)". BE-29 (`docs/backlog.md:82`) es el patrón de
nombres que rechaza guion y apóstrofo; no tiene que ver con la auditoría. Las filas que sí tocan `audit_logs` son BE-48
(l.101, nadie fija `performed_by` en paquetes), BE-30 (l.93, `audit_logs.timestamp` nullable), P3 (l.147, `AuditLogCreate`
sin uso) y A3 (`commit()` en el repositorio de auditoría). Lo corrige David en la fila.

## Evidencia en el código
Líneas actuales (HEAD `2e50880`; la fila cita `user_service.py:282-289`, que se movió con BE-35/36/58/37):

- `app/services/user_service.py:284` — `update_dict = update_data.model_dump(mode="json", exclude_unset=True)`: el
  conjunto a auditar sale del cuerpo, no de la fila.
- `app/services/user_service.py:287` — `assert_can_update(current_user, target_user, update_dict)`: la política lee las
  **claves** del mismo diccionario (ver riesgos).
- `app/services/user_service.py:290-291` — `setattr(target_user, key, value)` sin comparar con el valor actual; el valor
  viejo se pierde aquí.
- `app/services/user_service.py:294-301` — `if update_dict:` → `log_transaction(..., action=AuditAction.UPDATE,
  changes=update_dict)`. Única condición: que el cuerpo no esté vacío.
- `app/services/tourist_services_service.py:282-284` — `update_dict` (sin `image_urls`) y `setattr` sin comparar.
- `app/services/tourist_services_service.py:287` — `if update_data.image_urls is not None:` el `null` no toca imágenes…
- `app/services/tourist_services_service.py:337-345` — …pero `payload_changes = update_data.model_dump(mode="json",
  exclude_unset=True)` sí conserva `image_urls: None` y lo audita (`if payload_changes:`). Líneas de la nota de BE-37: vigentes.
- `app/services/tourist_services_service.py:312-334` — con `image_urls` presente, `service.images.clear()` y recreación
  siempre, aunque la lista sea la misma (filas de `service_images` nuevas); la auditoría guarda las URL **enviadas**
  (temporales), no las definitivas (`definitive_urls`, l.329).
- `app/services/tourist_services_service.py:70-76` — creación de paquete: `changes=package_data.model_dump(mode="json")`,
  también con las URL temporales enviadas, no las promovidas.
- `app/services/tourist_services_service.py:128-137` — `toggle_package_status`: escribe `ACTIVATE`/`DEACTIVATE` sin mirar
  el estado previo (no-op auditado; acción, no `changes`).
- `app/services/audit_service.py:13-33` — `log_transaction(entity_name, entity_id, action, performed_by, changes=None)`:
  pasa `changes` tal cual; no calcula nada.
- `app/repositories/audit_repository.py:13-18` — `add` + `commit()` + `refresh`: en `update_user_account` y
  `update_package_details` este commit (l.16) confirma también la mutación de la entidad, porque se llama antes de
  `save_user` (`user_service.py:303`) / `save_service` (`tourist_services_service.py:347`) (A3).
- `app/models/audit.py:43-44` — comentario `# Dictionary snapshot containing 'old_values' and 'new_values'` sobre
  `changes: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))`: el comentario
  describe un formato antes/después que el código nunca escribió. Docstring l.25-29: "structural snapshots".
- `alembic/versions/2cc4b57c136c_add_ddl_for_audit_logs.py:29` — `changes` JSON/JSONB `nullable=True`; ninguna migración
  posterior toca `audit_logs` (`9d54a65f0971` es un `pass`).
- `app/schemas/audit.py:15` — `changes: dict[str, Any] | None = None` en `AuditLogBase`; `AuditLogResponse` (l.25-31) lo
  sirve sin forma en `GET /auditoria/` (`app/api/routers/audit.py:10-34`). Contrato con el panel del cliente: sin forma fija.

Resto de puntos que escriben auditoría (grep global; no tienen no-op posible o no llevan `changes`):

- `app/services/user_service.py:97-102` — `CREATE` del registro de turista, sin `changes`.
- `app/services/user_service.py:212-217` — `SOFT_DELETE`, sin `changes` (un objetivo ya borrado da 404 antes, l.197-203).
- `app/services/user_service.py:367-372` — `RECOVER`, sin `changes` (exige `deleted_at` no nulo, l.356).
- `app/services/user_service.py:425-431` — `CREATE` de cuenta administrativa, `changes={"role": ...}`; se audita **antes**
  de `create_user` (l.433).
- `app/services/superadmin_bootstrap.py:66-72` — `CREATE` del CLI (`app/cli/bootstrap_superadmin.py:55` lo cablea),
  `changes={"role": "superadmin", "source": "bootstrap"}`; formato fijado en ADR-0015 punto 6
  (`docs/adr/0015-bootstrap-del-primer-superadmin.md:37-38`).
- `app/services/tourist_services_service.py:169-174` y `:211-216` — `SOFT_DELETE` y `RECOVER` de paquetes, sin `changes`.
- `app/services/user_service.py:141` — `verify_email_account` activa la cuenta (`activate_user`) **sin** fila de auditoría.

### Sondas (copia `git archive HEAD` en el scratchpad, pila real de la suite; nada en el repo)
`PATCH /usuarios/{cedula}` — usuarios de `persist_user` (`first_name="John"`, `last_name="Doe"`, `phone=None`, activos):

| # | Actor → objetivo · cuerpo | HTTP | Mutación | Fila de auditoría (`entity, id, action, performed_by, changes`) |
|---|---|---|---|---|
| U1 | superadmin → admin · `{"role":"admin"}` | 200 | ninguna | `UPDATE {'role': 'admin'}` |
| U2 | superadmin → sí mismo · `{"role":"superadmin"}` (caso original de BE-02) | **403** | ninguna | ninguna (BE-02 lo bloquea por clave) |
| U3 | turista → sí mismo · `{"first_name":"John"}` | 200 | ninguna | `UPDATE {'first_name': 'John'}` |
| U4 | admin → turista · `{"first_name":"John"}` | 200 | ninguna | `UPDATE {'first_name': 'John'}` |
| U5 | superadmin → sí mismo · `{"is_active":true}` (activo) | 200 | ninguna | `UPDATE {'is_active': True}` |
| U6 | superadmin → par superadmin activo · `{"is_active":true}` (BE-36) | 200 | ninguna | `UPDATE {'is_active': True}` |
| U7 | superadmin → admin · `{"first_name":"John","last_name":"Nuevo"}` (mixto) | 200 | `last_name` | `UPDATE {'first_name': 'John', 'last_name': 'Nuevo'}` |
| U8 | turista → sí mismo · `{"phone":null}` (ya nulo) | 200 | ninguna | `UPDATE {'phone': None}` |
| U9 | turista → sí mismo · `{"email":"PROBE9@TEST.COM"}` (igual tras minúsculas) | 200 | ninguna | `UPDATE {'email': 'probe9@test.com'}` |
| U10 | turista → sí mismo · `{}` | 200 | ninguna | ninguna (`if update_dict`) |
| U11 | admin → turista activo · `{"is_active":true}` | 200 | ninguna | `UPDATE {'is_active': True}` |
| U12 | superadmin → admin · `role`, `is_active`, `first_name`, `last_name` iguales | 200 | ninguna | `UPDATE` con las cuatro claves |
| U13 | admin → sí mismo · `{"role":"admin","first_name":"Otro"}` | **403** | ninguna | ninguna (clave `role` propia) |

`PUT /servicios/{id}` y rutas de estado — paquete con `name="Paquete De Prueba Automatizada"`, `base_price=50000.00`,
`max_capacity=15`, `is_available=True`, `description=None`:

| # | Cuerpo / ruta | HTTP | Mutación | Fila de auditoría (`changes` / acción) |
|---|---|---|---|---|
| P1 | `{"name": <mismo>}` | 200 | ninguna | `UPDATE {'name': 'Paquete De Prueba Automatizada'}` |
| P2 | `{"name": <mismo en minúsculas>}` (validador lo title-casea) | 200 | ninguna | `UPDATE {'name': 'Paquete De Prueba Automatizada'}` |
| P3 | `{"base_price": 50000}` | 200 | ninguna (`50000.00`) | `UPDATE {'base_price': '50000'}` |
| P4 | `{"image_urls": null}` (con 1 imagen) | 200 | ninguna (imagen id 1 intacta) | `UPDATE {'image_urls': None}` |
| P5 | `{"image_urls": [<misma URL permanente>]}` | 200 | **fila de imagen recreada** (id 1 → id 2, misma URL) | `UPDATE {'image_urls': [<URL permanente>]}` |
| P6 | `{"image_urls": [<permanente>, <temporal>]}` | 200 | 2 imágenes; la nueva queda como `ecotur-images/new.jpg` | `UPDATE` con la URL **temporal** `temp-ecotur-images/new.jpg` |
| P7 | `{"name": <mismo>, "max_capacity": 20}` (mixto) | 200 | `max_capacity` | `UPDATE {'name': ..., 'max_capacity': 20}` |
| P8 | `{}` | 200 | ninguna | ninguna |
| P9 | `{"is_available": true}` (activo) | 200 | ninguna | `UPDATE {'is_available': True}` |
| P10 | `{"description": null}` (ya nulo) | 200 | ninguna | `UPDATE {'description': None}` |
| P11 | `PATCH /servicios/{id}/activar` (ya activo) | 200 | ninguna | `ACTIVATE`, `changes=None` |
| P12 | `PATCH /servicios/{id}/desactivar` (ya inactivo) | 200 | ninguna | `DEACTIVATE`, `changes=None` |
| P13 | `{"image_urls": []}` (sin imágenes) | 200 | ninguna | `UPDATE {'image_urls': []}` |
| P14 | `POST /servicios/` con `image_urls=[<temporal>]` | 201 | imagen guardada como permanente | `CREATE` con la URL **temporal** y `base_price: '50000'` |

Lectura: en usuarios y paquetes, todo campo enviado se audita con independencia de que cambie; solo el cuerpo vacío no
escribe fila. El caso con el que se midió el rincón (U2) ya no es reproducible desde BE-02 (403), pero el defecto sigue en
cualquier objetivo ajeno (U1, U6, U11, U12) y en campos de perfil (U3, U4, U9). Además, en paquetes la fila no refleja el
estado resultante: guarda la URL temporal y no la promovida (P6, P14) y la grafía del cuerpo de `base_price` (P3).

## Ficheros afectados (mapa completo)
- `app/services/user_service.py` — l.284-303: cálculo de `changes` desde el cuerpo y orden setattr → auditoría → save.
- `app/services/tourist_services_service.py` — l.282-284, 287, 312-334, 337-345 (update), l.70-76 (create, URL temporal),
  l.128-137 (toggle sin mirar estado previo).
- `app/services/audit_service.py` — l.13-33: el contrato `changes: dict | None` que recibirían los nuevos valores.
- `app/models/audit.py` — l.43 comentario que ya promete `old_values`/`new_values`; l.25-29 docstring.
- `app/schemas/audit.py` — l.15 `changes: dict[str, Any] | None` (salida de `GET /auditoria/`); l.19-22 `AuditLogCreate` sin uso (P3).
- `app/repositories/audit_repository.py` — l.16 `commit()` (A3): hoy confirma la mutación de la entidad; fuera de alcance pero condiciona el orden.
- `alembic/versions/2cc4b57c136c_add_ddl_for_audit_logs.py` — l.29: `changes` JSONB nullable; no requiere migración si
  el antes/después cabe en el mismo JSONB.
- `tests/test_models_schema.py` — l.99-107: congela las columnas de `audit_logs` (cae si cambia el esquema).
- Tests que congelan `changes` de un cambio real (seguirán verdes si el arreglo conserva el formato `{campo: valor_nuevo}`;
  caen todos si pasa a antes/después):
  - `tests/test_user_access_policy.py:692` — `test_be02_superadmin_self_profile_update_returns_200`: `{"first_name": "Changed"}`.
  - `tests/test_user_access_policy.py:720` — `test_be02_superadmin_changes_third_party_role_returns_200`: `{"role": "tourist"}`.
  - `tests/test_user_access_policy.py:1008` — `test_be35_superadmin_deactivates_lower_rank_account_returns_200`: `{"is_active": False}`.
  - `tests/test_user_access_policy.py:1051-1054` — `test_be36_recovered_superadmin_reactivated_by_peer_can_log_in`:
    `RECOVER None` + `UPDATE {"is_active": True}` (cambio real: la recuperación lo dejó en `False`).
  - `tests/test_user_access_policy.py:1094-1097` — `test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in`:
    `CREATE {"role": "superadmin"}` + `UPDATE {"is_active": True}`.
  - `tests/test_user_update_null.py:133-136` — `test_be37_null_on_phone_still_clears_it` (3 casos): `{"phone": None}`
    sobre `phone="3001234567"` (cambio real).
  - `tests/test_services.py:839-840` — `test_be37_null_on_description_still_clears_it`: `[{"description": None}]` (cambio real).
  - `tests/test_user_service.py:358-364` — `CREATE` admin, `changes={"role": "admin"}` (unitario con mock autospec).
  - `tests/test_superadmin_bootstrap.py:71-77` — `CREATE` del bootstrap, `{"role": "superadmin", "source": "bootstrap"}`.
  - `tests/test_services.py:471-472` — creación de paquete: solo `len(audits) == 1`.
- Tests de no-op que **a propósito** no afirman sobre la auditoría y esperan a BE-38 (aquí van las aserciones nuevas):
  - `tests/test_user_access_policy.py:1199-1222` — `test_be36_superadmin_reactivating_active_peer_returns_200` (docstring
    l.1203: "The audit row this no-op writes is BE-38 and is not frozen here").
  - `tests/test_user_access_policy.py:961-979` — `test_be35_superadmin_self_update_with_is_active_true_returns_200` (H6 de BE-35).
  - `tests/test_user_access_policy.py:1308` — `test_be58_admin_self_update_with_is_active_true_returns_200` (gemelo de BE-58).
- Tests que afirman `audits == []` (rechazos; no deberían cambiar): `tests/test_user_access_policy.py:492-493, 599-600,
  620-621, 817-818, 860-861, 911-912, 1125-1126, 1147-1148, 1172-1173, 1194-1195, 1248-1249, 1278-1279`;
  `tests/test_services.py:381-383, 541-542, 798, 824`; `tests/test_user_update_null.py:83, 104, 149`.

## Rincones no mencionados por la fuente
1. **La fila de paquetes no describe el estado resultante.** `image_urls` se audita con las URL temporales enviadas, no
   con las permanentes que quedan (P6 al actualizar, P14 al crear: `tourist_services_service.py:75` y `:337`).
   `base_price` se audita con la grafía del cuerpo (`'50000'`) y no con la de la columna (`50000.00`) (P3, P14).
2. **Misma lista de imágenes recrea las filas** de `service_images` (P5: id 1 → 2) y audita; un "solo valores cambiados"
   ingenuo sobre `image_urls` necesita comparar la lista, no las filas.
3. **Activar un paquete activo / desactivar uno inactivo** escribe `ACTIVATE`/`DEACTIVATE` (P11, P12;
   `tourist_services_service.py:128-137`). Es no-op auditado por acción, no por `changes`.
4. **`{"image_urls": []}` sin imágenes** también audita (P13); `[]` con imágenes las borra (BE-59).
5. **Normalizaciones del schema producen no-ops invisibles para el cliente:** correo en otra grafía (U9, ADR-0016) y nombre
   de paquete en minúsculas (P2) se auditan como si cambiaran.
6. **El comentario de `app/models/audit.py:43`** promete `old_values`/`new_values`, formato que el código no escribe.
7. **`verify_email_account` activa una cuenta sin fila de auditoría** (`user_service.py:141`). Fuera del alcance (no es
   no-op), sin fila en el backlog que lo cite.
8. **`create_administrative_account` audita antes de crear** (`user_service.py:425-433`): si `create_user` falla después,
   queda una fila `CREATE` sin cuenta (dos `commit()`, A3). No medido; fuera de alcance.
9. **Referencia BE-29 de la fila no corresponde** (ver "Qué describe el ítem").

## Patrones de detección (copiables)
```bash
# Puntos que escriben auditoría (todos):
grep -rn "log_transaction(" app/
# 'changes' calculado desde el cuerpo y no desde la fila:
grep -n "exclude_unset=True" app/services/user_service.py app/services/tourist_services_service.py
grep -n -A8 "if update_dict:" app/services/user_service.py
grep -n -A8 "if payload_changes:" app/services/tourist_services_service.py
# Estado de estado sin mirar el previo:
grep -n -A10 "async def toggle_package_status" app/services/tourist_services_service.py
# Comentario que promete antes/después:
grep -n "old_values" app/models/audit.py
# Tests que congelan 'changes':
grep -rn -E "\.changes ==|a\.changes\) for|audit\.changes\) for|changes=\{" tests/
# Tests de no-op que esperan a BE-38:
grep -n "BE-38" tests/test_user_access_policy.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `290a942` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop` =
  `290a9429136098a05960f9b1e9910bc666977d84`; HEAD de la rama `2e50880`, solo docs encima).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (exit 0)

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```
- pytest: `757 passed, 25 warnings in 31.50s` (0 failed).
- Cobertura total: `TOTAL 1046 10 150 8 98.49%`.
- ruff format: `70 files already formatted`; ruff check: `All checks passed!` (0).
- mypy: `Success: no issues found in 65 source files` (0).
- import-linter: `Contracts: 4 kept, 0 broken.` (capas `api | cli -> services -> repositories -> models`, servicios sin
  transporte HTTP, repositorios solo SQLAlchemy y modelos, modelos y schemas sin capas superiores: KEPT).
- La compuerta no fallaba antes de tocar nada.

## Decisiones abiertas para David (no tomadas aquí)
1. **Alcance:** solo usuarios (`B-GHOST-ADMIN`, el bloque del ítem) o también paquetes (`PUT /servicios/{id}`, nota de
   BE-37). Si entran paquetes: ¿también `toggle_package_status` (P11, P12) y la URL temporal en `CREATE`/`UPDATE` (P6, P14)?
2. **No-op total:** ¿200 sin fila de auditoría, o fila igualmente (p. ej. con `changes` vacío) para dejar rastro del intento?
   Hoy solo `{}` no escribe fila.
3. **Formato de `changes`:** solo valores nuevos de lo que cambió (`{campo: nuevo}`, compatible con los tests que congelan
   cambios reales) o antes/después (`{campo: {"old": ..., "new": ...}}`), que rompe esos ~9 tests, cambia lo que ve
   `GET /auditoria/` (contrato con el panel del cliente Flutter, sin comprobar) y deja mezcladas en la tabla filas viejas y
   nuevas de formatos distintos. ¿Se homogeneiza `CREATE` (admin y bootstrap, ADR-0015 punto 6)?
4. **Esquema/ADR:** el antes/después cabe en el JSONB actual (sin migración; `tests/test_models_schema.py:104` no cambia).
   Columnas nuevas (`old_values`/`new_values`) sí exigen migración Alembic y cambian el test de esquema. Un formato nuevo de
   auditoría es una decisión de contrato: ¿ADR propio? (ADR-0015 fija hoy un `changes` concreto.)
5. **Comparación tras normalizar:** ¿un correo en otra grafía (U9) o un nombre de paquete title-caseado (P2) es no-op? Lo
   natural es comparar el valor ya validado con la columna, pero es una decisión.
6. **Referencia a BE-29** en la fila: corregirla (¿quería decir BE-48?).

## Conclusión para el planificador
El defecto está en dos sitios con el mismo molde: `user_service.py:284-301` y `tourist_services_service.py:282-345`;
el plan debe calcular el conjunto de cambios comparando el valor ya validado con el de la fila **antes** del `setattr`
(l.290-291 / l.283-284), y decidir con David si un no-op total escribe fila. **No** debe filtrar las claves antes de
`assert_can_update` (`user_service.py:287`): la política lee claves (`user_access_policy.py:84, 97, 102, 105, 114`) y
quitar `role` igual antes de ella convertiría U2/U13 (403 hoy, BE-02) en 200 y abriría la excepción de ADR-0018 a cuerpos
con más claves; el filtro va después de la política. Comparar en modo Python, no JSON (`Decimal('50000') == Decimal('50000.00')`;
`UserRole.admin == "admin"`), y `image_urls` como lista de URL, no como filas. No toca: el `commit()` del repositorio (A3),
el orden del CDN (BE-26), `image_urls: []` (BE-59), `performed_by` en paquetes (BE-48), `verify_email_account`. Riesgo: si
el formato cambia a antes/después caen ~9 tests que congelan cambios reales (lista arriba) y cambia la salida de
`GET /auditoria/`; los tres tests de no-op señalados (l.961, 1199, 1308 de `test_user_access_policy.py`) son donde nacen las
aserciones RED.

## Adenda — decisiones de David antes de planear (17 nov 2026, 17:24, sesión Mentor)

Resuelve las "Decisiones abiertas para David". El planificador toma estas decisiones como dadas; lo demás (fases,
tests, commits, nombres, mecanismo) es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado:
confirmada. Línea base aceptada:** `290a942`, compuerta completa en verde (757 passed · 98,49 % · ruff 0 · mypy 0 en 65
archivos · 4 kept). Severidad: Media, la de la fila.

Contraste de la sesión Mentor contra el código, sin correcciones de hecho: `app/services/user_service.py:284-303`,
`app/services/tourist_services_service.py:128-137` y `:337-345`, `app/models/audit.py:43`.

### Decisiones (David: "sobre la decisión 3, vamos por B. Todo lo demás lo acepto tal cual")

1. **Alcance: usuarios y paquetes.** Entran `PATCH /usuarios/{cedula}`, `PUT /servicios/{id}` y las rutas de activar y
   desactivar un paquete (P11, P12: activar uno ya activo o desactivar uno ya inactivo es el mismo defecto, una fila por
   algo que no pasó). Cada servicio, en su fase. **Fuera, con fila BE-61:** la URL temporal que audita el alta de un
   paquete (P14); no es un no-cambio, es otro defecto (el valor registrado no es el que queda guardado).
2. **Una petición que no cambia nada responde 200 y no escribe fila de auditoría.** Si cambia solo una parte, la fila
   lleva solo los campos que cambiaron (U7, P7). La tabla registra cambios, no intentos.
3. **Formato de `changes` en una modificación: antes y después, `{campo: {"old": <valor anterior>, "new": <valor
   nuevo>}}`** (opción B). **Es decisión de David contra la recomendación de la sesión Mentor**, que proponía conservar
   `{campo: valor_nuevo}` y dejar el antes/después para trabajo futuro. Costes que David acepta, medidos por la
   verificación: caen los tests que congelan `changes` de un cambio real (lista en "Ficheros afectados"), cambia lo que
   devuelve `GET /auditoria/` y las filas ya guardadas quedan en el formato anterior.
4. **ADR-0021, dictado por el plan:** la auditoría de una modificación registra solo lo que cambió, con su valor
   anterior y el nuevo, y un no-cambio no deja fila. Con la decisión 3 deja de ser un ADR corto: fija un formato que lee
   el cliente.
5. **"Cambió" se decide comparando el valor ya validado con el de la columna:** un correo en otra grafía (U9) o un
   nombre de paquete que el schema deja igual al guardado (P2) son no-cambio. Se comparan valores de Python, no su texto
   (`Decimal("50000") == Decimal("50000.00")`, P3).
6. **La referencia "BE-29" de la fila era un error por BE-09** (auditoría de cambios de paquetes, `docs/backlog.md:62`);
   corregida en la fila, con nota en BE-09.

### Lo que la decisión 3 deja abierto (propuestas de la sesión Mentor; David las confirma o las cambia al aprobar el plan)

- **Dónde se guarda:** en la misma columna `changes` (JSON/JSONB), sin migración ni columnas nuevas.
  `tests/test_models_schema.py:99-107` no cambia.
- **Las filas `CREATE` no cambian:** no tienen valor anterior, y ADR-0015 (punto 6) fija el `changes` del bootstrap.
  ADR-0021 no supersede a ADR-0015. `SOFT_DELETE`, `RECOVER`, `ACTIVATE` y `DEACTIVATE` siguen sin `changes`.
- **Las filas ya guardadas no se migran:** el valor anterior no se puede reconstruir. El plan dice cómo distingue un
  lector los dos formatos (por la forma del valor o por la fecha) y lo declara en ADR-0021.
- **El cliente Flutter:** el panel de auditoría consume `GET /auditoria/`. Qué hace con `changes` no consta en este
  repositorio. **Lo comprueba David en el cliente antes de mezclar**; el plan lo lleva como paso suyo de la Verificación
  final (escrito para `cmd`, si lleva comandos) y como riesgo declarado en el PR.
- **`image_urls`:** el plan propone y mide qué es "anterior" y "nuevo" (listas de URL, no filas; lo nuevo, las URL que
  quedan guardadas y no las temporales enviadas, P6) y qué pasa con la misma lista reenviada (P5: hoy recrea las filas
  de `service_images`; sin fila de auditoría, la recreación sigue siendo un residual a declarar).
- **`{"image_urls": null}`** (P4) y **`{"image_urls": []}` sobre un paquete sin imágenes** (P13): no cambian nada, así
  que no dejan fila (decisión 2). `[]` sobre un paquete con imágenes sigue borrándolas (BE-59, fuera de alcance).

### Condiciones para el planificador (no son decisiones)

- **El filtro de "lo que cambió" va después de `assert_can_update`, nunca antes** (`user_service.py:287`). La política
  decide por las claves que llegan (`user_access_policy.py:97, 102, 105`): quitar antes una clave "porque no cambia"
  convertiría U2 y U13 (403 hoy, BE-02) en 200 y abriría la excepción de ADR-0018 a cuerpos con más claves. El plan lo
  congela con un test.
- El valor anterior se lee **antes** del `setattr` (`user_service.py:290-291`; `tourist_services_service.py:283-284`).
- Lo que se guarda en `old` y `new` es serializable a JSON (como hoy, `mode="json"`); la comparación, en Python.
- Los tres tests de no-cambio que esperaban a este ítem reciben su aserción (`tests/test_user_access_policy.py:961`,
  `:1199`, `:1308`), y `test_be37_null_on_image_urls_still_keeps_the_images` (`tests/test_services.py`) también.
- El comentario de `app/models/audit.py:43` pasa a describir lo que el código escribe.
- **Fuera de alcance:** el `commit()` del repositorio de auditoría (A3), el orden del CDN (BE-26), la lista vacía
  (BE-59) y el autor en paquetes (BE-48). Los rincones 7 y 8 **entran** en el ítem: ver la ampliación de abajo.

### Ampliación del alcance (David, 17 nov 2026, 17:37)

La sesión Mentor había dejado los rincones 7 y 8 fuera de las seis decisiones y propuso decidir en el cierre si recibían
fila. **David no lo acepta:** "prefiero que se re-verifique [...] y que se ataque de una vez. Eso de dejar para después
en este caso no me convence, porque se trata de la vista de auditorías, algo 100 % utilizable durante una live demo en
la sustentación".

7. **Entran en BE-38 los rincones 7 y 8:** que verificar el correo deje fila de auditoría de la activación
   (`app/services/user_service.py:141`, hoy sin fila) y que el alta de una cuenta administrativa no pueda dejar una fila
   `CREATE` sin cuenta (`user_service.py:425-433`, hoy la auditoría se escribe antes del alta; leído, no medido).
8. **Antes de planear se re-verifican los dos**, con una sección añadida al final de este archivo (el cuerpo y esta
   adenda no se reescriben). La re-verificación revisa además, en cada punto que escribe auditoría, si la fila se
   escribe antes o después de la mutación, y si queda alguna mutación de cuenta o de paquete sin fila. Las decisiones
   que salgan de ahí (qué acción y qué `changes` lleva la activación por correo; quién figura como autor; el orden del
   alta) las toma David con la medición delante, en una segunda adenda.

9. **BE-61 entra también en BE-38** (David, 17:42: "entra en BE-38"), preguntado por la sesión Mentor porque la razón
   de los rincones 7 y 8 vale igual para esa fila. **Sustituye a la segunda frase de la decisión 1.** El alta de un
   paquete audita el estado que queda guardado (URL definitivas de las imágenes, precio como en la columna), no el
   cuerpo que llegó. Ya está medido (P14): no necesita re-verificación. Es fila hija (AGENTS §8): se salda como fase de
   este ítem, misma carpeta y mismo PR. La fila `CREATE` conserva su forma (valores, sin `old`/`new`).

El plan no se lanza hasta la segunda adenda, tras la re-verificación de los rincones 7 y 8.

## Re-verificación — rincones 7 y 8 (17 nov 2026)

Pedida por el punto 8 de la ampliación de la adenda. Solo lectura sobre el código; sondas en una copia `git archive HEAD`
(`054fee2`) en el scratchpad, con la pila real de la suite (`conftest.py` de la raíz, `tests/conftest.py`, Python del venv
por ruta). Nada se escribió en el repo fuera de este archivo.

**Línea base:** sigue vigente la del cuerpo. `git fetch origin` correcto; `git merge-base HEAD origin/develop` =
`git rev-parse origin/develop` = `290a942`; `git diff --stat 290a942 HEAD -- app tests` sale **vacío** (los commits
`f44a4b3` y `054fee2` solo tocan `docs/`). Base develop: `290a942` (757 passed · 98,49 % · ruff 0 · mypy 0 en 65
archivos · 4 kept, 0 broken). No se repitió la compuerta. El commit `054fee2` (BE-61 como fila hija, punto 9) no cambia
nada de lo medido aquí: BE-61 es la fila `CREATE` de paquetes (P14), ya medida.

### Rincón 7 — `verify_email_account` no deja fila (confirmado)

Código: `app/services/user_service.py:141` llama a `self.user_repo.activate_user(email)`;
`app/repositories/user_repository.py:54-65` busca **solo por correo** (sin filtrar `deleted_at` ni el estado), pone
`user.is_active = True` y hace `commit()` (l.64); devuelve `bool`, no el usuario. El servicio no llama a
`log_transaction` (l.141-149).

| # | Caso | HTTP | Mutación | Filas de `audit_logs` (`id, entity, entity_id, action, performed_by, changes`) |
|---|---|---|---|---|
| V1 | `POST /usuarios/registro` y después `GET /usuarios/verificar-email?token=<el del correo>` | 201 → 200 | `is_active` `False` → `True` | antes y después de verificar, la misma única fila: `(1, User, 1234567, CREATE, 1234567, None)` |
| V2 | Segundo uso del mismo enlace (BE-50) | 200, `success: true` | ninguna (ya activa) | ninguna nueva |
| V3 | Enlace de una cuenta que ya estaba activa (`persist_user(is_active=True)`) | 200, `success: true` | ninguna | ninguna |
| V4 | Admin desactiva a un turista (`PATCH {"is_active": false}`) y el turista usa un enlace vigente | 200 → 200 | `is_active` `False` → **`True`** | solo `UPDATE {'is_active': False}` del admin; la reactivación no deja fila |
| V5 | Admin borra a un turista (`DELETE /usuarios/{cedula}`) y el turista usa un enlace vigente | 200 → 200 | `is_active` → **`True`** con `deleted_at` puesto | solo `SOFT_DELETE`; nada de la activación |
| V6 | Enlace de un correo sin cuenta | 404 | ninguna | ninguna |

Lectura: toda activación por enlace es invisible en `GET /auditoria/`. V4 mide lo que BE-50 dejó "leído, no probado": el
enlace reactiva una cuenta que un admin desactivó, y la vista de auditoría muestra como último estado la desactivación
mientras la cuenta está activa. V5 es nuevo: el enlace deja una cuenta borrada con `is_active=True` (el login sigue
cerrado, `get_non_deleted_user_by_email`, `user_repository.py:43-46`; `recover_user_account` lo vuelve a `False`,
`user_service.py:364`). Hoy los datos no distinguen "pendiente de verificar" de "desactivada por un admin" (las dos son
`is_active=False`, `deleted_at=None`); sí distinguen la cuenta borrada.

**Autor posible.** No hay actor autenticado. `register_tourist` lo resuelve registrando a la cuenta como autora de su
propia alta: `performed_by=saved_user.cedula` (`user_service.py:97-102`); el bootstrap hace lo mismo y lo dice en su
docstring (`app/services/superadmin_bootstrap.py:29-30`, "as a tourist is in register_tourist"). Todas las filas de
`User` usan la cédula en `entity_id` y en `performed_by` (`String(50)`, sin FK, `app/models/audit.py:39, 47`). En
`verify_email_account` el servicio solo tiene el correo (`sub` del token, l.135) y `activate_user` devuelve `bool`: para
registrar la cédula hay que obtener el usuario (cambiar lo que devuelve el repositorio o leerlo antes). Con el correo
como `entity_id`, el filtro `GET /auditoria/?entity_id=<cédula>` no encontraría la fila.

**Acción posible.** `AuditAction.ACTIVATE` ya existe (`app/models/audit.py:20`) y está en el enum de la base
(`alembic/versions/2cc4b57c136c_add_ddl_for_audit_logs.py:28`); hoy solo lo usan los paquetes. Una acción nueva (p. ej.
`VERIFY`) exige migración Alembic del tipo `audit_action_enum` en PostgreSQL.

**Tests:** ninguno congela que la verificación no escriba fila. Con una llamada `log_transaction(..., ACTIVATE, ...)`
inyectada en la copia después de l.144, la suite completa da `757 passed` (los dobles de `tests/test_user_service.py:77-79`
y `tests/test_token_failure_paths.py:85` son `create_autospec(AuditService)` y no afirman `assert_not_awaited`). El test
RED es del plan.

### Rincón 8 — `create_administrative_account` audita antes de crear (confirmado y reproducido)

Código: `user_service.py:425-431` `log_transaction(... CREATE, changes={"role": ...})` → `audit_repository.py:15-17`
`add` + **`commit()`** + `refresh` → después `user_service.py:433` `create_user` → `user_repository.py:49-51` `add` +
`commit()`. Dos transacciones; la fila queda confirmada antes del `INSERT` del usuario. `get_db` (`app/db/database.py:29-35`)
solo cierra la sesión; no hay rollback que alcance un commit ya hecho.

Qué puede hacer fallar `create_user` después de la fila (la contraseña se hashea antes, l.419):
1. **Carrera sobre los índices únicos** `users.cedula`/`users.email` (`app/models/user.py:41-42`) entre la comprobación
   (l.403-410) y el `INSERT`: `IntegrityError` → handler global, **409** (`app/main.py:100-114`; su docstring nombra
   esta carrera).
2. **Fallo de la base o de la conexión** en el `INSERT`/`commit`/`refresh`: `OperationalError`/`DBAPIError` sin handler → 500.
3. **Correo de más de 150 caracteres** (BE-54, `B-FUTURO`): `EmailStr` acepta 196 (medido: 201 en SQLite, que no aplica
   longitudes); en PostgreSQL `String(150)` daría `DataError`, que no es `IntegrityError` (comprobado:
   `issubclass(DataError, IntegrityError)` es `False`) → 500, con la fila ya escrita. Leído, no ejecutado en PostgreSQL
   (sin Docker en esta máquina).
4. **Cancelación de la petición** entre los dos `await` (cliente que corta). Leído, no medido.

Sondas (la carrera se simula sustituyendo en la copia `UserRepository.get_user_by_email_or_cedula` por un doble que
devuelve `None`, como si otra petición hubiera insertado entre la comprobación y el alta; el fallo de base, con
`create_user` lanzando `OperationalError`):

| # | Caso | HTTP | Mutación | Filas de `audit_logs` |
|---|---|---|---|---|
| C1 | Alta normal de un admin por un superadmin | 201 | cuenta `7654321` admin activa | `(1, User, 7654321, CREATE, <superadmin>, {'role': 'admin'})` |
| C2 | Carrera por la **cédula**: ya existe un turista `7654321` | **409** (`detail` del handler de integridad) | ninguna; el turista sigue igual, no hay cuenta con el correo pedido | **`CREATE {'role': 'admin'}` sobre `7654321`**, que es la cédula del turista ajeno |
| C3 | Carrera por el **correo**: el correo pertenece a otra cédula | **409** | ninguna; no existe cuenta `7654321` | **`CREATE {'role': 'admin'}` sobre `7654321`, cédula sin cuenta** |
| C4 | `create_user` lanza `OperationalError` | **500** | ninguna | **`CREATE {'role': 'admin'}` sin cuenta** |

La fila sobrevive al rollback del `INSERT` fallido (C2, C3) y al cierre de una sesión que nunca confirmó el alta (C4):
la confirmó el `commit()` del repositorio de auditoría (A3). C2 es peor que una fila huérfana: la vista de auditoría
atribuye al superadmin la creación de un **admin** con la cédula de un turista que existe.

**Comparación de órdenes.**
- `register_tourist` (`user_service.py:94` → `:97-102`) y `bootstrap_superadmin` (`superadmin_bootstrap.py:64` → `:66-72`;
  ADR-0015) crean primero y auditan después, con `entity_id=saved_user.cedula`. El hueco que les queda es el inverso:
  cuenta sin fila si falla la auditoría. Medido en el registro (C6): `AuditRepository.create_audit_log` lanzando
  `OperationalError` → **500**, la cuenta queda guardada inactiva, sin fila y **sin correo de verificación** (la tarea se
  programa después, `app/api/routers/user.py:68-76`); repetir el registro da **400** (ya existe) y no hay ruta para
  reenviar el enlace (grep `resend|reenviar` en `app/`: ninguna ruta). Mismo hueco, leído, en el bootstrap: excepción sin
  capturar en `app/cli/bootstrap_superadmin.py:97-104` con el superadmin ya creado.
- El informe de sep-2026 (§A3, "Sin fronteras transaccionales") cita este mismo caso como "el más claro" de A3 y
  propone la Unit of Work (`add()`/`flush()` en repositorios, commit en el límite de la petición). La fila A3
  (`docs/backlog.md:127`, "auditoría antes que creación") está en `B-RESERVAS`. Invertir el orden en BE-38 cierra la
  fila fantasma; solo la UoW (A3) hace atómicas las dos escrituras.

**Orden invertido inyectado en la copia** (alta, después auditoría; solo para medir):
- Variante A, `entity_id=saved_user.cedula` (como `register_tourist`): suite completa **1 failed, 756 passed**. Cae
  `tests/test_user_service.py::test_create_administrative_account_provisions_admin` (`:341-364`), no por el orden sino
  porque el doble autospec de `create_user` devuelve un `AsyncMock` y `entity_id` deja de ser `'5555555555'` (l.358-364).
- Variante B, `entity_id=user_data.cedula`: suite completa **757 passed**. **Ningún test congela el orden.** Las sondas
  C1–C4 con el orden invertido: C1 igual (201, una fila); C2 409 y C3 409 **sin fila**; C4 500 **sin fila**.

### Barrido — cada punto que escribe auditoría: ¿antes o después de la mutación?

`commit()` de auditoría: `audit_repository.py:16`. Sesión con `autoflush=False` y `expire_on_commit=False`
(`app/db/database.py:14-20`).

| Punto (`log_transaction`) | Mutación | Orden | Transacciones |
|---|---|---|---|
| `user_service.py:97` registro de turista | `create_user`, l.94 (`user_repository.py:50` commit) | **después** del commit | 2; si falla la auditoría, cuenta sin fila (C6, medido) |
| `user_service.py:212` borrado de cuenta | `soft_delete_user`, l.209 (`user_repository.py:83-86` commit) | **después** del commit | 2 |
| `user_service.py:295` modificación de cuenta | `setattr`, l.290-291 (en memoria) | **después** de la mutación en memoria, **en el mismo commit** (el de auditoría confirma también el `UPDATE`); `save_user`, l.303, hace un commit vacío + `refresh` | 1 (atómico por accidente de A3) |
| `user_service.py:367` recuperación de cuenta | l.363-365 `save_user` (`user_repository.py:114` commit) | **después** del commit | 2 |
| `user_service.py:425` alta de cuenta administrativa | `create_user`, l.433 | **antes** de la mutación | 2; fila fantasma (C2–C4, medido) |
| `superadmin_bootstrap.py:66` bootstrap (CLI) | `create_user`, l.64 | **después** del commit | 2 |
| `tourist_services_service.py:70` alta de paquete | CDN `promote_to_permanent` l.63 + `create_service` l.68 (`service_repository.py:17` commit) | **después** del commit | 2 (+ CDN fuera de transacción) |
| `tourist_services_service.py:132` activar/desactivar | l.128-129 `save_service` (`service_repository.py:93` commit) | **después** del commit | 2 |
| `tourist_services_service.py:169` borrado de paquete | l.165-168 `save_service` | **después** del commit | 2 |
| `tourist_services_service.py:211` recuperación de paquete | l.206-209 `save_service` | **después** del commit | 2 |
| `tourist_services_service.py:339` modificación de paquete | `setattr` l.283-284, borrado en CDN l.315-317, `images.clear()` l.320, promoción l.329, `append` l.334 | **después** de la mutación en memoria, **en el mismo commit**; `save_service` l.347 hace un commit vacío + recarga | 1 en base; el CDN ya cambió antes (BE-26) |

**Mutaciones de cuenta o de paquete sin fila de auditoría** (grep global en `app/`: `setattr(`, asignaciones a
atributos de modelos, `.commit()`, `.add(`, `.delete(`, `images.clear|append`, métodos de repositorio, CLI):
1. **`verify_email_account` → `activate_user`** (`user_service.py:141`, `user_repository.py:63-64`): la única ruta de
   éxito que muta una cuenta sin fila (V1, V4, V5).
2. Ninguna otra en un camino de éxito. Las 7 escrituras con `commit()` de repositorios (`user_repository.py:50, 64, 86,
   114`; `service_repository.py:17, 93`; `audit_repository.py:16`) y las mutaciones en servicios (`setattr` ×2,
   `tourist_services_service.py:128, 165-166, 206-207`, `user_service.py:363-364`) están todas detrás de un
   `log_transaction`, salvo la 1. Los cuerpos `{}` (`if update_dict`, `if payload_changes`) no mutan.
3. En caminos de fallo, por las dos transacciones (A3): todo punto de la tabla con "2" puede dejar la mutación sin fila si
   falla la escritura de auditoría (medido en el registro, C6); el alta administrativa, al revés (C2–C4).
4. Fuera de la base, sin fila y sin ser mutación de paquete: `POST /servicios/upload-images/` sube blobs temporales
   (`tourist_services_service.py:224-248`).
5. Migraciones: `alembic/versions/22d7d68f4844_*.py:24` (`UPDATE users SET cedula …`) es un relleno histórico de esquema;
   no es mutación de la aplicación.

### Rincones nuevos
- **V4** (medido): el enlace reactiva una cuenta desactivada por un admin, sin fila. Es el caso "leído, no probado" de
  BE-50 (`B-FUTURO`).
- **V5** (medido): el enlace pone `is_active=True` en una cuenta borrada, sin fila. No está en BE-50 ni en otra fila.
- **C2** (medido): la fila fantasma puede nombrar la cédula de **otra** cuenta existente, con otro rol.
- **C6** (medido): un fallo de la auditoría en el registro deja una cuenta inactiva sin correo y sin forma de pedir otro
  enlace (repetir el registro da 400). Consecuencia de A3; fuera de BE-38.

### Patrones de detección (copiables)
```bash
# Puntos que escriben auditoría y su orden respecto de la mutación:
grep -rn -B6 "log_transaction(" app/services/
# Activación por enlace sin auditoría:
grep -n -A10 "activation_success = await" app/services/user_service.py
grep -n -A12 "async def activate_user" app/repositories/user_repository.py
# Alta administrativa: auditoría antes de create_user:
grep -n -E "log_transaction\(|create_user\(" app/services/user_service.py app/services/superadmin_bootstrap.py
# Commits de repositorio (A3):
grep -rn "\.commit()" app/repositories/
```

### Decisiones abiertas para David
1. **Acción y `changes` de la activación por correo:** `ACTIVATE` (existe en el enum y en la base, sin migración; hoy
   solo de paquetes), `UPDATE` con `{"is_active": {"old": false, "new": true}}` (formato de la decisión 3), o una acción
   nueva (`VERIFY`: migración del enum en PostgreSQL). ¿Lleva algo que la distinga de una reactivación por un admin (p. ej.
   un `source`, como el bootstrap en ADR-0015)?
2. **Autor:** la propia cuenta por su cédula, como `register_tourist` y el bootstrap (exige que el servicio obtenga el
   usuario: `activate_user` hoy devuelve `bool`), o el correo del token (rompe la uniformidad de `entity_id`/`performed_by`
   y el filtro por cédula de `GET /auditoria/`).
3. **Enlace sin cambio (V2, V3):** con la decisión 2 no deja fila. La respuesta sigue en 200 "verificada" (BE-50, `B-FUTURO`).
4. **V4 y V5:** si BE-38 solo añade la fila, la reactivación de una cuenta que un admin desactivó (V4) y la activación de
   una cuenta borrada (V5) quedarían registradas como activaciones legítimas. Opciones: (a) BE-38 audita lo que hoy hace
   `activate_user` y BE-50 sigue en `B-FUTURO`; (b) entra en BE-38 la parte que impide activar una cuenta borrada
   (distinguible por `deleted_at`). V4 no es distinguible hoy de una verificación legítima con los datos que hay (no existe
   marca de "verificada"); cerrarla exige decidir esa marca o un token de un solo uso, que es BE-50 entero.
5. **Orden del alta administrativa:** invertir a alta → auditoría, como el registro y el bootstrap (cierra C2–C4; queda el
   hueco inverso de C6 hasta A3), o hacer atómicas las dos escrituras ya en BE-38 (adelanta A3, que la adenda dejó fuera,
   y toca el `commit()` de `audit_repository.py:16`, del que dependen los 11 puntos del barrido). `entity_id` de la fila:
   `saved_user.cedula` (como los otros dos; cae `test_create_administrative_account_provisions_admin` por el doble) o
   `user_data.cedula` (verde).

### Conclusión para el planificador
Dos defectos confirmados y medidos: la activación por enlace no deja fila (`user_service.py:141`; V1, V4, V5) y el alta
administrativa deja una fila `CREATE` confirmada antes del alta (`user_service.py:425-433`; C2/C3 → 409 y C4 → 500 con
fila, C2 sobre la cédula de otra cuenta). Ningún test congela ni la ausencia de fila en la verificación (inyección: 757
passed) ni el orden del alta (variante B: 757 passed): los RED son del plan, y la carrera de C2/C3 no se reproduce por
HTTP sin sustituir el repositorio; un test unitario con los dobles autospec que ya usa `tests/test_user_service.py`
(`create_user` lanzando `IntegrityError` → `log_transaction` no llamado) la cubre sin dobles nuevos en tests HTTP (AGENTS
§5). El orden del resto de puntos (alta → auditoría) es el modelo; no tocar `audit_repository.py:16` ni los commits de
repositorios (A3), ni el segundo clic, ni el token de un solo uso (BE-50), ni la longitud del correo (BE-54), salvo que
David decida otra cosa en la segunda adenda. Riesgo: la fila de verificación necesita la cédula y `activate_user` devuelve
`bool` (cambia la firma del repositorio y sus dobles en `tests/test_user_service.py:263-273, 330` y
`tests/test_token_failure_paths.py`); sin decidir V4/V5, la nueva fila legitima en la vista de auditoría dos activaciones
que no deberían ocurrir.

## Segunda adenda — decisiones de David tras la re-verificación (17 nov 2026, 18:37, sesión Mentor)

Resuelve las "Decisiones abiertas para David" de la re-verificación. Continúa la numeración de la primera adenda (1 a 9).
Contraste de la sesión Mentor, sin correcciones de hecho: el verificador añadió 194 líneas y no cambió ninguna del cuerpo
ni de la adenda (`git diff` sin líneas borradas); `app/repositories/user_repository.py:54-65` busca solo por correo, pone
`is_active = True` y confirma, sin mirar `deleted_at`.

### Decisiones (David, 18:28: "nos vamos con (b)"; 18:37: "sí a las otras 4 y V5 va aquí en BE-38")

10. **La activación por correo deja fila de auditoría:** acción `UPDATE`, con
    `changes = {"is_active": {"old": false, "new": true}}` (el formato de la decisión 3), sin campo `source`. "Una cuenta
    pasó a activa" se escribe de una sola manera, la active un admin o un enlace. Sin acción nueva y sin migración;
    `ACTIVATE` sigue siendo solo de paquetes.
11. **Autor: la propia cuenta, por su cédula,** en `entity_id` y en `performed_by`, como `register_tourist`
    (`user_service.py:97-102`) y el bootstrap (ADR-0015). Nunca el correo: rompería el filtro por cédula de
    `GET /auditoria/`. El servicio tiene que obtener el usuario (`activate_user` hoy devuelve `bool`); cómo, lo decide el
    plan. Esa fila se distingue sola: un turista no cambia su `is_active` por ninguna otra vía.
12. **Un enlace sobre una cuenta ya activa (V2, V3) no deja fila** (decisión 2). La respuesta sigue siendo la de hoy; qué
    ve el usuario en el segundo clic es de BE-50.
13. **V5 se arregla en este ítem:** la activación por enlace ignora las cuentas borradas (`deleted_at` no nulo), como ya
    hace el login (`user_repository.py:43-46`). El enlace de una cuenta borrada responde como el de un correo sin cuenta
    (V6), no muta nada y no deja fila. No depende del enlace de un solo uso: V5 puede ocurrir en el primer uso (registro,
    borrado por un admin, primer clic).
14. **V4 no se arregla en este ítem; BE-50 entra en `B-GHOST-ADMIN` como ítem siguiente** (opción (b), elegida por David
    frente a dejarla en `B-FUTURO`). V4: el enlace reactiva una cuenta que un admin desactivó; los datos no distinguen
    "pendiente de verificar" de "desactivada por un admin" (las dos son `is_active = false`, `deleted_at` nulo), y
    cerrarlo exige un dato nuevo (marca de correo verificado o enlace de un solo uso), que es el contenido de BE-50, con
    su propia verificación, su plan y, si hace falta, su migración. Lo que BE-38 cambia de V4: la reactivación deja de
    ser invisible, porque escribe la fila de la decisión 10.
15. **El alta de una cuenta administrativa crea primero y audita después,** como el registro y el bootstrap, con la
    cédula de la cuenta guardada como `entity_id`. Cierra C2, C3 y C4 (fila `CREATE` sin cuenta, o sobre la cédula de
    otra cuenta). `tests/test_user_service.py:341-364` cae por su doble y se ajusta. **No se adelanta A3:** el `commit()`
    de `audit_repository.py:16` no se toca. Queda el hueco inverso, declarado en ADR-0021: si falla la auditoría, la
    cuenta existe sin fila (medido en el registro, C6).

### Alcance completo del ítem para el planificador (decisiones 1 a 15)

1. Modificar una cuenta o un paquete audita solo lo que cambió, con valor anterior y nuevo (1, 3, 5).
2. Un no-cambio no deja fila, incluido activar o desactivar un paquete que ya estaba así (2).
3. La activación por correo deja fila y no alcanza a cuentas borradas (10 a 13).
4. El alta administrativa no puede dejar una fila sin cuenta (15).
5. El alta de un paquete audita lo que queda guardado: BE-61, fila hija (9).
6. ADR-0021 recoge las reglas, el formato, lo que no se migra y el hueco de A3 (4, 15).

### Condiciones para el planificador

- RED de la decisión 15: la carrera de C2/C3 no se reproduce por HTTP sin sustituir el repositorio; un test unitario
  con los dobles `autospec` de `tests/test_user_service.py` (`create_user` lanza `IntegrityError` → `log_transaction` no
  se llamó) la cubre (conclusión del verificador; AGENTS §5).
- Si cambia la firma de `activate_user`, cambian sus dobles (`tests/test_user_service.py:263-273, 330`;
  `tests/test_token_failure_paths.py`).
- **Fuera de alcance:** el `commit()` de los repositorios (A3), el segundo clic y el enlace de un solo uso (BE-50), la
  longitud del correo (BE-54), el orden del CDN (BE-26), la lista vacía (BE-59), el autor en paquetes (BE-48).
- Siguen vigentes las condiciones de la primera adenda (el filtro, después de la política) y sus propuestas abiertas
  (misma columna `changes`; filas `CREATE` sin `old`/`new`; filas ya guardadas sin migrar; `image_urls` como listas).
- **Antes de mezclar, David comprueba en el cliente Flutter** qué hace el panel de auditoría con `changes`.

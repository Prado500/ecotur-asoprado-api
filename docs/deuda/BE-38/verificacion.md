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

El plan no se lanza hasta entonces. Sigue fuera de alcance, con fila, BE-61 (decisión 1), salvo que David la traiga
también: la sesión Mentor se lo pregunta, porque la razón que da para los rincones 7 y 8 vale igual para esa fila.

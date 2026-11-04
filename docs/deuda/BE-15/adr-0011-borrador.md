# ADR-0011 — La app y el test usan sesiones distintas en la suite (borrador)

> **Borrador del plan de BE-15** (`docs/deuda/BE-15/plan.md`, fase F). No es un ADR vigente. Si David aprueba el plan
> con la decisión D1 = "sí", la fase F lo copia a `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`: borra
> este aviso, quita "(borrador)" del título y cambia el estado a "aceptado". Si la fase F se recorta, el borrador se
> queda aquí y no entra en `docs/adr/`.

- **Estado:** propuesto (pasa a aceptado cuando se mezcle la fase F de BE-15)
- **Propuesta:** Claude, `plan-redactor` (4 nov 2026) · **Aprobada:** pendiente (David)
- **Ubicación en el repo:** `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`
- **Origen:** backlog BE-15, sub-hallazgo 4; `docs/deuda/BE-15/verificacion.md` (adenda, punto 4); AGENTS §5
  ("la sesión de prueba no es la sesión de la app"). **Relación:** prepara la meta A3 (los repositorios no hacen
  `commit()`) y `B-RESERVAS`.

## Contexto

- `tests/conftest.py` sustituía `get_db` por un generador que devolvía la misma `db_session` del test. La app y el
  test compartían sesión, mapa de identidad y transacción durante todo el test. En producción, `get_db`
  (`app/db/database.py:33-39`) abre una sesión por petición.
- Con la sesión compartida, si la app hace `flush()` y olvida el `commit()`, el test ve el dato igualmente. Hoy no
  muerde porque los repositorios confirman ellos mismos (A3). Cuando `B-RESERVAS` traiga repositorios que solo hacen
  `add()`/`flush()` y un servicio que confirma, la suite tiene que poder detectar que nadie confirmó.
- La suite corre sobre SQLite en memoria con `StaticPool`: hay una sola conexión DBAPI para todo el proceso, y las
  tablas se crean y se borran en cada test (`tests/conftest.py:19-46`).

## Decisión

1. El override de `get_db` en el fixture `client` abre **una sesión nueva por petición** con `TestingSessionLocal` y
   la cierra al terminar, igual que `get_db`. `db_session` sigue siendo la sesión del test y la app nunca la recibe.
2. **Convención A, antes de la petición:** todo dato que el test prepare se confirma con `commit()` antes de llamar
   al cliente. `persist_user` ya lo hace.
3. **Convención B, después de la petición:** cualquier objeto que el test ya tenga cargado se relee con
   `await db_session.refresh(obj)`. Un `select` nuevo devuelve la instancia que ya está en el mapa de identidad, con
   los valores viejos (`expire_on_commit=False`).
4. `tests/test_fixtures_contract.py` congela el contrato: cada petición recibe su propia sesión, un `flush()` sin
   `commit()` de la app no llega al test y un `commit()` sí llega.

## Consecuencias

- Positiva: un `commit()` olvidado en la app hace fallar el test que lee el dato. Es la red que necesita A3.
- Negativa, aceptada: el aislamiento es de **sesión**, no de **conexión**. Con `StaticPool` las dos sesiones
  comparten la conexión. Durante la petición, la app ve lo que el test dejó sin confirmar. Al cerrarse la sesión de
  la app, el pool hace `rollback` de esa conexión y se pierde lo que el test no había confirmado. Por eso existe la
  convención A.
- Negativa, aceptada: hay que recordar la convención B. Si se olvida, el test lee un valor viejo y falla en rojo.
  No da un falso verde salvo que el valor viejo coincida con el esperado.
- Coste medido al decidir: con el cambio aplicado sobre la suite de la línea base (376 tests), solo falla 1,
  `tests/test_auth.py::test_borrado_logico_usuario`, que relee con `select` un objeto que ya tenía cargado. BE-15
  lo reescribe con `refresh` antes de este cambio.

## Alternativas consideradas

1. **Mantener la sesión compartida.** Descartada: oculta el `commit()` olvidado, que es justo el fallo que A3 va a
   hacer posible.
2. **SQLite en fichero con `NullPool`** (una conexión real por sesión). Da aislamiento de conexión, pero obliga a
   gestionar un fichero por test, a convivir con los bloqueos de escritura de SQLite y a añadir más infraestructura
   de la que pide el problema.
3. **PostgreSQL de pruebas** (contenedor). Es lo más fiel a producción, y además ejercitaría el índice parcial de
   ADR-0002 (BE-31). Requiere dependencias e infraestructura nuevas. Si llega, será decisión de `B-RESERVAS`, no de
   BE-15.
4. **Transacción externa con SAVEPOINT por test.** Resuelve otra cosa (deshacer los datos entre tests, que aquí ya
   resuelve `drop_all`) y sigue compartiendo la conexión.

## Evidencia

- Ensayo en seco del 4 nov (`plan-redactor`, sin tocar el repo): `pytest --noconftest -p <copia de conftest con el
  override por petición>` sobre la línea base `dc09398` → `1 failed, 375 passed`. El único fallo es el descrito
  arriba.
- Sondeos en el intérprete del proyecto (Python 3.14.3, SQLAlchemy 2.0.48, aiosqlite 0.22.1, `StaticPool`): (a) un
  re-`select` tras el `commit()` de otra sesión devuelve el valor viejo, mientras que `refresh` y `populate_existing`
  devuelven el nuevo; (b) un `flush()` sin `commit()` de la sesión de la app no es visible tras cerrarla; (c) un
  `flush()` sin `commit()` del test desaparece cuando se cierra la sesión de la app.

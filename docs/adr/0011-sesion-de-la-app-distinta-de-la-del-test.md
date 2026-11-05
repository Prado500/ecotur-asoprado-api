# ADR-0011 — La app y el test usan sesiones distintas en la suite

- **Estado:** aceptado
- **Propuesta:** Claude, `plan-redactor` (4 nov 2026) · **Aprobada:** David (4 nov 2026, enmienda D1 al plan de BE-15)
- **Ubicación en el repo:** `docs/adr/0011-sesion-de-la-app-distinta-de-la-del-test.md`
- **Origen:** BE-15, sub-hallazgo 4 (`docs/deuda/BE-15/verificacion.md`, adenda punto 4); AGENTS §5

## Contexto

La suite sustituía `get_db` por la misma `db_session` del test, de modo que la app y el test compartían una sesión
durante todo el test. En producción, `get_db` abre una sesión por petición. Con la sesión compartida, un `flush()` al
que le falta el `commit()` es visible para el test, y la meta A3 (los repositorios dejan de hacer `commit()`) necesita
que la suite lo detecte. La suite usa SQLite en memoria con `StaticPool`.

## Decisión

El override de `get_db` en el fixture `client` abre una sesión nueva de `TestingSessionLocal` en cada petición y la
cierra al terminar, aparte de la `db_session` del test. La app nunca recibe la sesión del test.

## Límite aceptado

1. **La conexión es compartida.** `StaticPool` tiene una sola conexión, así que la sesión de la app y la del test
   usan la misma.
2. **El aislamiento es de sesión, no de transacción.** Durante la petición, la app ve lo que el test dejó sin
   confirmar. Al cerrarse la sesión de la app, el `rollback` que hace el pool al recibir la conexión borra también lo
   que el test no había confirmado.
3. **El commit olvidado se detecta al cerrar la sesión de la app.** Un `flush()` de la app sin `commit()` desaparece
   cuando su sesión se cierra al final de la petición. Antes de ese momento la suite no lo distingue.

## Consecuencias

- Todo test sigue dos reglas:
  1. **Commit antes de la petición:** lo que el test prepara se confirma con `commit()` antes de llamar al cliente
     (`persist_user` ya lo hace).
  2. **Refresh después:** todo objeto que el test ya tenga cargado se relee con `await db_session.refresh(obj)` tras
     la petición. Un `select` nuevo devuelve la instancia vieja del mapa de identidad.
- `tests/test_fixtures_contract.py` congela que cada petición tiene su sesión, que un `flush()` sin `commit()` de la
  app no llega al test y que un `commit()` sí llega.
- Las dos reglas pasan a AGENTS §5 en un PR de David al cerrar BE-15.

## Alternativas consideradas

1. **Sesión compartida (el estado anterior).** Descartada: oculta el commit olvidado.
2. **Conexiones separadas** (SQLite en fichero con `NullPool`). Aíslan también la transacción, pero hay que gestionar
   un fichero por test y los bloqueos de escritura de SQLite. Es más infraestructura de la que pide el problema.
3. **PostgreSQL de pruebas.** Es lo más fiel a producción y además ejercitaría el índice parcial de ADR-0002. Se
   decide en BE-31 (`B-RESERVAS`), no aquí.

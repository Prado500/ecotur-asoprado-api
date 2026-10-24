# Ecotur-ASOPRADO — Backlog consolidado (triage v1.3, 24 oct 2026 — sincronizado con ADR-0002 y ADR-0003; absorbe registro.json)

> Guárdalo en el repo como `docs/backlog.md`. Fuentes: 19 notas `.txt` de "deuda funcional",
> Word "deuda técnica adicional identificada", cards del Trello (según David), auditoría previa de
> Claude Code sobre la suite de tests, y último sprint planning con el gerente.
>
> **Severidad:** Alta = indefendible ante jurado, seguridad o error 500 reproducible ·
> Media = afecta uso real · Baja = cosmético.
> **Decisión:** Entra (día del plan) · Sale (trabajo futuro documentado) · Cerrado · **Decidir** (pregunta para David).

---

## A. Backend

| ID | Origen | Qué | Sev. | Decisión | Nota técnica |
|---|---|---|---|---|---|
| BE-01 | B1 (txt) | Crear paquete con URLs de blobs inexistentes o ajenas al CDN devuelve **500** ("Fallo al consolidar las imágenes en el CDN") | Alta | **Entra · día 4** | Validar en el schema que cada URL pertenece al dominio del CDN; el error del cliente de storage se traduce a excepción de dominio (`ImageNotFound`/`InvalidImageSource`) → handler global → 422/409. Un 500 reproducible desde Postman es lo primero que prueba un jurado curioso. |
| BE-02 | B1 (txt) | Superadmin puede auto-degradarse de rol | Alta | **Entra · día 4** | Regla en la política de acceso: nadie cambia su propio rol; solo un superadmin cambia roles ajenos. Test explícito. |
| BE-03 | B3 (txt) | `update_user` sin ABAC jerárquico | — | **Cerrado (ya resuelto)** | David verificó: existe `UserAccessPolicy` con el cálculo del ABAC jerárquico para decidir si un sujeto puede editar un objeto. Queda una revisión "por no dejar" el día 2 (que `update_user` y `delete_user_account` usen la misma política y haya test de ambos). |
| BE-04 | B1 (txt) | `HTTPException` dentro de servicios | — | **Cerrado (ya resuelto)** | David verificó: ninguno de los tres servicios (usuarios, servicios turísticos, audit) importa FastAPI ni lanza `HTTPException`. Para que **siga** siendo así sin depender de la memoria de nadie: contrato de `import-linter` el día 1 (`app.services` no puede importar `fastapi`). Respuesta a la duda original: no hay caso que lo justifique; el único argumento sería velocidad, y los handlers ya existen. |
| BE-05 | txt (duda) | ¿Dos handlers globales separados (paquete vs usuario)? | — | **Cerrado** | No. Los handlers se organizan por **tipo de excepción** (NotFound, Conflict, Forbidden, Validation), no por entidad. Un handler por entidad duplica lógica y crece linealmente con el dominio. Se documenta en el ADR de excepciones (día 2). |
| BE-06 | txt | Se pueden crear paquetes turísticos idénticos | — | **Cerrado** | Gerencia confirmó (23 oct) que el nombre **no** debe ser único. No hay trabajo. |
| BE-07 | txt | Al actualizar un paquete, el schema permite superar las 10 imágenes | Media | **Entra · día 4** | Mismo validador en el schema de update que en el de create (o un tipo compartido). Test. |
| BE-08 | txt | Orden de paquetes en catálogo: al reactivar, el paquete cae al final | Media | **Entra completo · días 6 y 9** | El gerente espera poder reordenar. Backend (día 6): columna `display_order` + `PATCH /packages/{id}/display-order` + `ORDER BY display_order NULLS LAST, created_at`. Frontend (día 9): campo numérico en la tarjeta del kanban. Nada de drag & drop. |
| BE-09 | txt | Auditoría de cambios de paquetes (parcial / completa) | Media | **Verificar · día 1, luego Sale** | Ya existe `test_audit.py`: hay algo de auditoría. Se documenta lo que hay; ampliar a dos modos es trabajo futuro. |
| BE-10 | B1 (txt) | Autobaja de cuentas (turista / admin) | Media | **Sale + nota** | Decisión de producto y legal, no técnica. Dos datos a verificar antes de publicar en Android: la política de Google Play exige opción de borrado de cuenta para apps con registro, y la Ley 1581 de 2012 (habeas data, Colombia) reconoce el derecho de supresión. No soy abogado: confírmalo. Para el MVP: "solicitud de baja" documentada como trabajo futuro. |
| BE-11 | B1 (txt) | Cuenta `jpa@gmail.com` no inicia sesión | — | **Cerrado** | Resuelto por ti (contraseña olvidada). Derivado: **recuperación de contraseña** no existe → Sale (requiere envío de correo). |
| BE-12 | txt | Sesiones concurrentes; token "con amnesia" | Media | **ADR · día 4; código solo si cabe** | JWT sin estado = múltiples sesiones **por diseño**. Opciones: (1) access token corto + refresh token con rotación; (2) `session_version` por usuario comparada en `get_current_user` (ya hay lectura de BD por petición, así que el coste es nulo). Se escribe el ADR; se implementa (2) si el día 4 sobra tiempo. |
| BE-13 | Word adicional | Reservar/pagar un paquete ya eliminado o inactivo que seguía cargado en el cliente | **Alta** (con pagos) | **Entra · día 5** | Guardia **en el servidor**: crear reserva/transacción sobre paquete inactivo o eliminado → 409 con motivo. El cliente re-consulta el paquete al abrir el detalle y maneja 404/409 con mensaje claro. "Ver cambios en caliente" (push/websocket) → Sale. |
| BE-14 | Word adicional | Dos admins con el kanban abierto no ven los cambios del otro | Baja | **Sale** | Mitigación barata en FE: refrescar al volver a la vista + pull-to-refresh. Tiempo real es trabajo futuro. |
| BE-15 | Auditoría CC | Suite de tests: mocks sin `spec`, setup duplicado, aserciones sobre texto en español, sesión de prueba ≠ `get_db`, sin cobertura ni linters, huecos B2/B3/B4 | Alta | **Entra · día 3** | Se verifica contra el código el día 1 (tarde) al montar el tooling; se corrige el día 3. |
| BE-16 | Sprint planning | Pasarela **Wompi sandbox** | — | **Entra · días 4–6** | Puerto `PaymentGateway` + `WompiAdapter` + `FakeAdapter`; webhook idempotente; estados de reserva. Corte el día 6 a las 18:00. |
| BE-17 | Trello | Historial de reservas del turista | — | **Entra · día 6** | Endpoint paginado por usuario autenticado. |
| BE-18 | Trello / propuesta | Dashboard y métricas del negocio | — | **Entra mínimo · día 6** | Un endpoint de agregados (reservas por estado, ingresos por período). Dashboard completo → Sale. |
| BE-19 | Trello | **Módulo de reservas completo (no existía)** | **Alta** | **Entra · días 4–5** | Verificado contra la BD desplegada: no hay tabla de reservas y el botón "reservar" no hace nada. Modelo definido y validado con gerencia en **ADR-0002** (un paquete, una fecha, una reserva; `party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado; expiración perezosa). Guardia BE-13 incluida. |
| BE-20 | Trello | Notificaciones de cupos liberados | — | **Sale** | Requiere infraestructura de notificaciones. |
| BE-21 | Trello | Agendamiento y configuración de fechas | — | **Sale** | No prometido en la propuesta; alto esfuerzo. |
| BE-22 | Trello | Motor de tarifas dinámicas y descuentos (incluye tarifa de temporada alta mencionada por gerencia el 23 oct) | — | **Sale** | No prometido; alto riesgo. ADR-0002 congela el precio en cada reserva, así que añadirlo después no toca el módulo de reservas. |
| BE-23 | ADR-0003 | `AlreadyExistsError` responde 400; 409 es lo correcto | Baja | **Decidir · día 3** | Residuo declarado en ADR-0003. Cambia el contrato del cliente: hay que revisar dónde Flutter maneja el 400 de duplicados. Si es un solo sitio, entra el día 3 junto con los tests; si no, trabajo futuro. |

### A2. Tags de la auditoría HTML corregidos antes del flujo (migrados desde `registro.json`, que se elimina)

| ID | Qué | Decisión | Nota |
|---|---|---|---|
| b1–b5 | Bloqueos 1–5 de la auditoría (`docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html`) | **Cerrado · re-verificación día 3** | Corregidos con DeepSeek + verificación de David. Sin `verificacion.md`: el día 3 el verificador corre su procedimiento completo sobre ellos (los huecos de tests B2/B3/B4 son de esta misma auditoría). |
| d1 | Inversión de dependencias en la capa de servicios | **Cerrado · re-verificación día 3** | Commits `e581c6a`, `cf115a0`, `9cd96c0`, `aab1d3a`. Decisión registrada en **ADR-0003**. |
| d2…, D*, A*, S* | **Tags restantes del HTML: sin triage** | **Pendiente · día 2** | El backlog v1 se armó con las notas y el Trello, no con el HTML. Hay que volcar cada tag restante aquí con severidad y decisión antes de planear nada más. |

## B. Frontend (Flutter)

| ID | Origen | Qué | Sev. | Decisión | Nota técnica |
|---|---|---|---|---|---|
| FE-01 | txt | Token vencido: no redirige al login; 401 en cada acción | Alta | **Entra · día 7** | Interceptor global en el cliente HTTP: 401 → limpiar sesión → `pushAndRemoveUntil(Login)` vía `GlobalKey<NavigatorState>`. Lo que te explicaron es correcto. Temporizador de inactividad → Sale. |
| FE-02 | txt | Un solo servicio para todos los tipos de usuario (`TouristService`) | — | **Cerrado (ya resuelto)** | David verificó: ya hay separación por recurso (`audit_service`, `auth_service`, `catalog_service`, `session_service`, `user_service`). Correcto. El día 9 se añade `reservation_service` siguiendo el mismo patrón. |
| FE-03 | C (txt) | El admin se ve a sí mismo en el kanban de usuarios | Baja | **Entra · día 8** | Filtrar por id del usuario autenticado. Trivial. |
| FE-04 | C (txt) | Refactor kanban: scroll infinito → paginación + nuevo layout | Media | **Entra parcial · día 8** | Layout con el sistema de diseño sí. **Paginación sale**: el backend no pagina (confirmado) y construirla no justifica el tiempo con el volumen actual. Se documenta como trabajo futuro con el umbral que la haría necesaria. |
| FE-05 | txt | Kanban no responsivo en web | Baja | **Cerrado parcial · revisar día 8** | Hoy se resuelve con desplazamiento horizontal (arrastrar). Es un patrón aceptado para tableros kanban en pantallas estrechas (es lo que hace Trello); lo que lo vuelve "profesional" es la señal visual: barra de desplazamiento visible o indicador de más columnas. Se añade el día 8 dentro del sistema de diseño. |
| FE-06 | txt | Hover zoom en botones | Baja | **Entra · día 7** | Existe solo en algunos botones (vista inicial de admin, crear paquete/usuario). Al construir el botón base del sistema de diseño, el hover se define una vez y lo heredan todos. |
| FE-07 | txt | Se muestran nombres del CDN al editar paquete | Baja | **Entra · día 8** | Mostrar miniatura o nombre amigable. |
| FE-08 | txt | No se puede seleccionar texto (correo) para copiar | Baja | **Entra · día 8** | Parcialmente hecho en el kanban de usuarios. Completar con `SelectableText` donde falte. Trivial. |
| FE-09 | txt | No hay "editar detalles" en la columna "por activar" | Baja | **Entra · día 8** | Habilitar edición excepto en "eliminados". |
| FE-10 | Word adicional | Búsqueda (lupa) en el kanban | Baja | **Sale** | Trabajo futuro, salvo que sobre tiempo el día 9. |
| FE-11 | Sprint planning | Skeleton loaders al cargar | — | **Entra · día 8** | Shimmer en listas y detalle; estados vacío/error consistentes. |
| FE-12 | Sprint planning | "Que no se vea prototipo": sistema de diseño | — | **Entra · días 7–8** | Tokens (color, tipografía, espaciado, radios), componentes base, aplicación a todas las pantallas. |
| FE-13 | Alcance | Flujo de pago (Wompi) + historial de reservas + métricas admin | — | **Entra · día 9** | Depende de BE-16/17/18. |

## C. Preguntas (respondidas el 23 oct)

1. BE-06 nombre único → **No** (gerencia). Cerrado.
2. BE-08 reordenar desde el kanban → **Sí**, el gerente lo espera. Entra completo.
3. BE-19 qué hace hoy una reserva → **Nada**: no existe tabla ni lógica. Entra como módulo nuevo.
4. Paginación en backend → **No existe**. FE-04 paginación sale.

Pregunta del modelo de reservas: **resuelta el 23 oct con el gerente** → ADR-0002.

## D. Resumen del impacto sobre el plan (v1.1)

- Tres ítems que creíamos deuda ya estaban resueltos (BE-03, BE-04, FE-02): se liberan ~1 día.
- El hallazgo que lo cambia todo: **las reservas no existían**. Se construyen los días 4–5 con un
  modelo mínimo y defendible; Wompi se monta encima el día 6 con corte estricto.
- Lo demás "funcional" es barato y cabe en los días 3, 7 y 8.
- Nada de lo que sale compromete un entregable de la propuesta; todo lo que sale va al capítulo
  de trabajo futuro con su justificación.

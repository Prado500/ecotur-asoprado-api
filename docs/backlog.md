# Ecotur-ASOPRADO — Backlog consolidado (v1.6, 26 oct 2026 — las decisiones apuntan a bloques de trabajo (PLAN §2b); los días viven solo en PLAN.md)

> Guárdalo en el repo como `docs/backlog.md`. Fuentes: 19 notas `.txt` de "deuda funcional",
> Word "deuda técnica adicional identificada", cards del Trello (según David), auditoría previa de
> Claude Code sobre la suite de tests, y último sprint planning con el gerente.
>
> **Severidad:** Alta = indefendible ante jurado, seguridad o error 500 reproducible ·
> Media = afecta uso real · Baja = cosmético.
> **Decisión:** Entra · `B-<bloque>` (el bloque está en `PLAN.md` §2b; el día, solo en el cronograma de PLAN) · Sale → `B-FUTURO` · Cerrado · **Decidir**.

---

## A. Backend

| ID | Origen | Qué | Sev. | Decisión | Nota técnica |
|---|---|---|---|---|---|
| BE-01 | nota `B1_*.txt` de David (no es el tag B1 de la auditoría) + import-linter | Crear paquete con URLs de blobs inexistentes o ajenas al CDN devuelve **500**. **Localizado:** `app/core/storage.py:138` lanza `HTTPException(500, "Fallo al consolidar…")`; además 415 (l.60) y 500 (l.86). Por eso `services → storage → fastapi` rompe el contrato de capas. | Alta | **Entra · `B-BE01`** | `storage.py` deja de conocer HTTP: `UnsupportedMediaTypeError` → 415, `StorageUnavailableError` → 503 (ya existe), blob inexistente / URL ajena al CDN → excepción de dominio → 422. Registrar las nuevas en `_DOMAIN_ERROR_STATUS` (ADR-0003). Incluye A7 (copia síncrona antes de borrar el origen) y tests para `storage.py` (hoy 28 % de cobertura). Verificación final: `lint-imports` → 4 KEPT. |
| BE-02 | B1 (txt) | Superadmin puede auto-degradarse de rol | Alta | **Entra · `B-TESTS`** | Regla en la política de acceso: nadie cambia su propio rol; solo un superadmin cambia roles ajenos. Test explícito. |
| BE-03 | B3 (txt) | `update_user` sin ABAC jerárquico | — | **Cerrado (ya resuelto)** | David verificó: existe `UserAccessPolicy` con el cálculo del ABAC jerárquico para decidir si un sujeto puede editar un objeto. Queda una revisión "por no dejar" en `B-TESTS` (que `update_user` y `delete_user_account` usen la misma política y haya test de ambos). |
| BE-04 | B1 (txt) | `HTTPException` dentro de servicios | — | **Cerrado (ya resuelto)** | David verificó: ninguno de los tres servicios (usuarios, servicios turísticos, audit) importa FastAPI ni lanza `HTTPException`. Para que **siga** siendo así sin depender de la memoria de nadie: contrato de `import-linter` desde el 24 oct (`app.services` no puede importar `fastapi`). Respuesta a la duda original: no hay caso que lo justifique; el único argumento sería velocidad, y los handlers ya existen. |
| BE-05 | txt (duda) | ¿Dos handlers globales separados (paquete vs usuario)? | — | **Cerrado** | No. Los handlers se organizan por **tipo de excepción** (NotFound, Conflict, Forbidden, Validation), no por entidad. Un handler por entidad duplica lógica y crece linealmente con el dominio. Ya documentado: ADR-0003. |
| BE-06 | txt | Se pueden crear paquetes turísticos idénticos | — | **Cerrado** | Gerencia confirmó (23 oct) que el nombre **no** debe ser único. No hay trabajo. |
| BE-07 | txt | Al actualizar un paquete, el schema permite superar las 10 imágenes | Media | **Entra · `B-TESTS`** | Mismo validador en el schema de update que en el de create (o un tipo compartido). Test. |
| BE-08 | txt | Orden de paquetes en catálogo: al reactivar, el paquete cae al final | Media | **Entra · `B-ORDEN` (backend) y `B-FE-RESERVAS` (cliente)** | El gerente espera poder reordenar. Backend (`B-ORDEN`): columna `display_order` + `PATCH /packages/{id}/display-order` + `ORDER BY display_order NULLS LAST, created_at`. Frontend (`B-FE-RESERVAS`): campo numérico en la tarjeta del kanban. Nada de drag & drop. |
| BE-09 | txt | Auditoría de cambios de paquetes (parcial / completa) | Media | **Verificar en `B-HIGIENE`; luego `B-FUTURO`** | Ya existe `test_audit.py`: hay algo de auditoría. Se documenta lo que hay; ampliar a dos modos es trabajo futuro. |
| BE-10 | B1 (txt) | Autobaja de cuentas (turista / admin) | Media | **Sale + nota** | Decisión de producto y legal, no técnica. Dos datos a verificar antes de publicar en Android: la política de Google Play exige opción de borrado de cuenta para apps con registro, y la Ley 1581 de 2012 (habeas data, Colombia) reconoce el derecho de supresión. No soy abogado: confírmalo. Para el MVP: "solicitud de baja" documentada como trabajo futuro. |
| BE-11 | B1 (txt) | Cuenta `jpa@gmail.com` no inicia sesión | — | **Cerrado** | Resuelto por ti (contraseña olvidada). Derivado: **recuperación de contraseña** no existe → Sale (requiere envío de correo). |
| BE-12 | txt | Sesiones concurrentes; token "con amnesia" | Media | **ADR en `B-PAGOS`; código solo si cabe** | JWT sin estado = múltiples sesiones **por diseño**. Opciones: (1) access token corto + refresh token con rotación; (2) `session_version` por usuario comparada en `get_current_user` (ya hay lectura de BD por petición, así que el coste es nulo). Se escribe el ADR; se implementa (2) si sobra tiempo en `B-PAGOS`. |
| BE-13 | Word adicional | Reservar/pagar un paquete ya eliminado o inactivo que seguía cargado en el cliente | **Alta** (con pagos) | **Entra · `B-RESERVAS`** | Guardia **en el servidor**: crear reserva/transacción sobre paquete inactivo o eliminado → 409 con motivo. El cliente re-consulta el paquete al abrir el detalle y maneja 404/409 con mensaje claro. "Ver cambios en caliente" (push/websocket) → Sale. |
| BE-14 | Word adicional | Dos admins con el kanban abierto no ven los cambios del otro | Baja | **Sale** | Mitigación barata en FE: refrescar al volver a la vista + pull-to-refresh. Tiempo real es trabajo futuro. |
| BE-15 | Auditoría CC | Suite de tests: mocks sin `spec`, setup duplicado, aserciones sobre texto en español, sesión de prueba ≠ `get_db`, sin cobertura ni linters, huecos B2/B3/B4 | Alta | **Entra · `B-TESTS`** | Línea base medida el 24 oct; se corrige en `B-TESTS`. |
| BE-16 | Sprint planning | Pasarela **Wompi sandbox** | — | **Entra · `B-PAGOS`** | Puerto `PaymentGateway` + `WompiAdapter` + `FakeAdapter`; webhook idempotente; estados de reserva. Corte el jueves 29 a las 18:00 (ver PLAN). |
| BE-17 | Trello | Historial de reservas del turista | — | **Entra · `B-RESERVAS`** | Endpoint paginado por usuario autenticado. |
| BE-18 | Trello / propuesta | Dashboard y métricas del negocio | — | **Entra mínimo · `B-RESERVAS`** | Un endpoint de agregados (reservas por estado, ingresos por período). Dashboard completo → `B-FUTURO`. |
| BE-19 | Trello | **Módulo de reservas completo (no existía)** | **Alta** | **Entra · `B-RESERVAS`** | Verificado contra la BD desplegada: no hay tabla de reservas y el botón "reservar" no hace nada. Modelo definido y validado con gerencia en **ADR-0002** (un paquete, una fecha, una reserva; `party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado; expiración perezosa). Guardia BE-13 incluida. |
| BE-20 | Trello | Notificaciones de cupos liberados | — | **Sale** | Requiere infraestructura de notificaciones. |
| BE-21 | Trello | Agendamiento y configuración de fechas | — | **Sale** | No prometido en la propuesta; alto esfuerzo. |
| BE-22 | Trello | Motor de tarifas dinámicas y descuentos (incluye tarifa de temporada alta mencionada por gerencia el 23 oct) | — | **Sale** | No prometido; alto riesgo. ADR-0002 congela el precio en cada reserva, así que añadirlo después no toca el módulo de reservas. |
| BE-23 | ADR-0003 | `AlreadyExistsError` responde 400; 409 es lo correcto | Baja | **Decidir en `B-HIGIENE`** | Residuo declarado en ADR-0003. Cambia el contrato del cliente: hay que revisar dónde Flutter maneja el 400 de duplicados. Si es un solo sitio, entra en `B-HIGIENE`; si no, `B-FUTURO`. |

### A2. Auditoría técnica del backend (21 sep 2026, HEAD f0de961) — triage completo al 24 oct

Fuente: `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html`. `registro.json` queda absorbido aquí y
archivado. **Estado verificado contra el código de `develop` el 24 oct** (grep sobre el snapshot), no
contra el informe: la auditoría tiene un mes y mucho ya cambió. Esfuerzo: XS ≤ 15 min · S ≤ 1 h · M ≤ 3 h · L > 3 h.

| Tag | Hallazgo (resumen) | Verificación 24 oct | Sev. | Esf. | Decisión |
|---|---|---|---|---|---|
| B1–B5 | Bloqueos: módulo caído, escalada de privilegios, superadmin bloqueado, 404, guard de PATCH | Corregidos (DeepSeek + David); 110 tests hoy vs. 26 entonces | — | — | **Cerrado · re-verificación en `B-TESTS`**
| A1 | Servicios acoplados a FastAPI (`HTTPException`) | **0** en `app/services`; 5 en `core/storage.py` (residuo declarado) | — | — | **Cerrado · ADR-0003**
| A2 | Tres estrategias de autorización incompatibles | `UserAccessPolicy` existe; commit `e581c6a` centralizó audit | Media | S | **Revisar en `B-TESTS`**
| A3 | Repositorios hacen `commit()` (sin Unit of Work; auditoría antes que creación) | **7** `commit()` en repositorios, 0 en servicios | Alta | M | **Entra · `B-RESERVAS` (código nuevo con UoW); repos existentes si cabe, si no → deuda conocida**
| A4 | Configuración dispersa: 14 `os.getenv`, `pydantic-settings` sin usar | **14** `os.getenv`, **0** `BaseSettings` | Alta | S–M | **Entra · `B-PAGOS`**
| A5 | `echo=True` fijo; sin `lifespan`; cliente Azure por petición | `echo=True` **1**; `lifespan` **aparece 2** (verificar) | Media | XS–S | **Entra · `B-PAGOS`**
| A6 | Sin `logging`; 2 `print()`; `IntegrityError` descartado sin registro | **0** `logging`, **2** `print(` | Media | S | **Entra · `B-HIGIENE`**
| A7 | `promote_to_permanent` borra el origen sin esperar la copia (pérdida de imágenes) | `start_copy_from_url` **1**, sin espera de `copy_status` | Alta | S | **Entra · `B-BE01`**
| A8 | `get_deleted_users` filtra en memoria | **1** comprensión sobre `deleted_at` | Baja | XS | **Entra · `B-HIGIENE`**
| A9 | `UserResponse` hereda validaciones de entrada → 500 al leer nombres válidos | **1** `class UserResponse(UserBase` | Alta | S | **Entra · `B-HIGIENE`**
| D1 | Regla "es administrador" escrita 6 veces | `UserAccessPolicy` + commit `e581c6a` | — | — | **Cerrado · ADR-0003 / re-verificación en `B-TESTS`**
| D2 | `UserRole` definido dos veces | **2** definiciones | Media | XS | **Entra · `B-HIGIENE`**
| D3 | `jwt.decode` duplicado fuera de `core/security` | **2** fuera | Media | XS | **Entra · `B-HIGIENE`**
| D4 | Límite de 10 imágenes triplicado (2 copias muertas) | **3** `> 10` | Baja | XS | **Entra · `B-HIGIENE` (con BE-07 en `B-TESTS`)**
| D5 | `format_title_case` duplicado y divergente; patrones repetidos | **2** definiciones | Media | S | **Entra · `B-HIGIENE`**
| D6 / S3 | Firma de inyección repetida en 22 endpoints; `Depends` por defecto en vez de `Annotated` | **42** `= Depends(`, **2** `Annotated[` | Baja | S–M | **`B-HIGIENE` si sobra; si no, `B-FUTURO`**
| S1 | Modelos en estilo SQLAlchemy 1.x (`Column`) sobre base 2.0 | **33** `Column(`, **0** `mapped_column` | Media | M | **Entra · `B-S1`**
| S2 | `sqlalchemy.future` legado | **3** | Baja | XS | **Entra · `B-HIGIENE`**
| S4 | `typing.List/Optional` mezclados con nativos | **10** imports | Baja | XS | **Entra · `B-FORMATO`** (`ruff --fix`, regla UP)
| S5 | `HTTP_422_UNPROCESSABLE_ENTITY` deprecado | **1** | Baja | XS | **Entra · `B-HIGIENE`**
| S6 | `PUT` con semántica `PATCH`; `model_config` como dict | `@router.put` **0** (ya corregido); dict **1** | Baja | XS | **Entra · `B-HIGIENE`** (solo el dict)
| S7 | `Field(default=[])` | **1** | Baja | XS | **Entra · `B-HIGIENE`**
| P1 | `core/security` importa `User`, `UserRole`, `HTTPException` y `status` sin usarlos (arrastra el engine y rompe el contrato de capas por transitividad) | **4** imports muertos (l.6–10) | Media | XS | **Entra · `B-BE01` (fase A)**
| P2 | Spanglish: 12 handlers en español; clave `"detalle"` vs `"detail"` | **12** handlers, **1** `"detalle"` | Media (el `detalle` es bug funcional) | XS + S | **`detalle`→`detail` en `B-HIGIENE`; renombrar handlers si sobra, si no `B-FUTURO`**
| P3 | 8 docstrings que contradicen al código | No verificado por grep | Baja | S | **Se corrigen al tocar cada archivo (`B-HIGIENE`); lo que quede → `B-FUTURO`**
| SEC1 | CORS `*` con credenciales | **1** `allow_origins=["*"]` | Alta | XS | **Entra · `B-HIGIENE`**
| SEC2 | Subida de imágenes: sin límite de tamaño, tipo confiado al cliente, SVG permitido | `.read()` **0** (cambió); `svg` **0** (no excluido) | Alta | S | **Verificar en `B-HIGIENE`**: mínimo lista blanca sin SVG + límite de tamaño
| SEC3 | Detalle interno en errores (`str(e)`); enumeración de cuentas por tiempo en login | **4** `str(e)`; `verify_password` **2** | Media | S | **Entra · `B-HIGIENE`**
| §9 | Suite: mocks sin `spec`, setup duplicado, aserciones en español, sesión ≠ `get_db`, sin cobertura | `MagicMock()` sin spec **1**; `spec=` **13**; aserciones `detail ==` **4**; 110 tests | Alta | M | **Entra · `B-TESTS`**
| Alembic | `env.py` depende de un efecto colateral de importación | 3 imports de modelos (verificar que importa `app.models` completo) | Baja | XS | **Entra · `B-S1`**

**Lectura:** de 31 hallazgos, 7 están cerrados, ~17 son XS/S y forman el bloque `B-HIGIENE`,
y 4 son estructurales (A3, A4, S1, SEC2) con día asignado. Ninguno bloquea el módulo de reservas.

## B. Frontend (Flutter)

| ID | Origen | Qué | Sev. | Decisión | Nota técnica |
|---|---|---|---|---|---|
| FE-01 | txt | Token vencido: no redirige al login; 401 en cada acción | Alta | **Entra · `B-FE-BASE`** | Interceptor global en el cliente HTTP: 401 → limpiar sesión → `pushAndRemoveUntil(Login)` vía `GlobalKey<NavigatorState>`. Lo que te explicaron es correcto. Temporizador de inactividad → `B-FUTURO`. |
| FE-02 | txt | Un solo servicio para todos los tipos de usuario (`TouristService`) | — | **Cerrado (ya resuelto)** | David verificó: ya hay separación por recurso (`audit_service`, `auth_service`, `catalog_service`, `session_service`, `user_service`). Correcto. En `B-FE-RESERVAS` se añade `reservation_service` siguiendo el mismo patrón. |
| FE-03 | C (txt) | El admin se ve a sí mismo en el kanban de usuarios | Baja | **Entra · `B-FE-LISTA`** | Filtrar por id del usuario autenticado. Trivial. |
| FE-04 | C (txt) | Refactor kanban: scroll infinito → paginación + nuevo layout | Media | **Entra parcial · `B-FE-LISTA`** | Layout con el sistema de diseño sí. **Paginación sale**: el backend no pagina (confirmado) y construirla no justifica el tiempo con el volumen actual. Se documenta como trabajo futuro con el umbral que la haría necesaria. |
| FE-05 | txt | Kanban no responsivo en web | Baja | **Cerrado parcial · revisar en `B-FE-LISTA`** | Hoy se resuelve con desplazamiento horizontal (arrastrar). Es un patrón aceptado para tableros kanban en pantallas estrechas (es lo que hace Trello); lo que lo vuelve "profesional" es la señal visual: barra de desplazamiento visible o indicador de más columnas. Se añade en `B-FE-LISTA` dentro del sistema de diseño. |
| FE-06 | txt | Hover zoom en botones | Baja | **Entra · `B-FE-BASE`** | Existe solo en algunos botones (vista inicial de admin, crear paquete/usuario). Al construir el botón base del sistema de diseño, el hover se define una vez y lo heredan todos. |
| FE-07 | txt | Se muestran nombres del CDN al editar paquete | Baja | **Entra · `B-FE-LISTA`** | Mostrar miniatura o nombre amigable. |
| FE-08 | txt | No se puede seleccionar texto (correo) para copiar | Baja | **Entra · `B-FE-LISTA`** | Parcialmente hecho en el kanban de usuarios. Completar con `SelectableText` donde falte. Trivial. |
| FE-09 | txt | No hay "editar detalles" en la columna "por activar" | Baja | **Entra · `B-FE-LISTA`** | Habilitar edición excepto en "eliminados". |
| FE-10 | Word adicional | Búsqueda (lupa) en el kanban | Baja | **Sale** | `B-FUTURO`, salvo que sobre tiempo en `B-FE-RESERVAS`. |
| FE-11 | Sprint planning | Skeleton loaders al cargar | — | **Entra · `B-FE-LISTA`** | Shimmer en listas y detalle; estados vacío/error consistentes. |
| FE-12 | Sprint planning | "Que no se vea prototipo": sistema de diseño | — | **Entra · `B-FE-BASE`** | Tokens (color, tipografía, espaciado, radios), componentes base, aplicación a todas las pantallas. |
| FE-13 | Alcance | Flujo de pago (Wompi) + historial de reservas + métricas admin | — | **Entra · `B-FE-RESERVAS`** | Depende de BE-16/17/18. |

## C. Preguntas (respondidas el 23 oct)

1. BE-06 nombre único → **No** (gerencia). Cerrado.
2. BE-08 reordenar desde el kanban → **Sí**, el gerente lo espera. Entra completo.
3. BE-19 qué hace hoy una reserva → **Nada**: no existe tabla ni lógica. Entra como módulo nuevo.
4. Paginación en backend → **No existe**. FE-04 paginación sale.

Pregunta del modelo de reservas: **resuelta el 23 oct con el gerente** → ADR-0002.

## D. Cómo se lee este backlog junto al plan

- Cada ítem tiene **una** decisión: `Entra · B-<bloque>`, `Sale → B-FUTURO`, `Cerrado` o `Decidir`.
- La composición de cada bloque está en `docs/PLAN.md` §2b; **el día en que se ataca un bloque está solo en
  el cronograma de `PLAN.md` §3**. Si el plan se desliza, aquí no cambia nada.
- Hallazgos que cambiaron el plan: BE-03, BE-04 y FE-02 ya estaban resueltos (23 oct); las reservas no
  existían (23 oct, → `B-RESERVAS`); `import-linter` localizó BE-01 y P1 (24 oct, → `B-BE01`).
- Nada de lo que sale compromete un entregable de la propuesta; `B-FUTURO` se redacta como capítulo de
  trabajo futuro con la justificación de cada ítem.

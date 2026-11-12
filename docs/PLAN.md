# Ecotur-ASOPRADO — Plan de trabajo hasta la entrega

> **Versión 3.3 — 12 nov 2026.** Bitácora `2026-11-12` (§2b: `B-GUARD-TESTS` cerrado con BE-40 y BE-42; bloque nuevo `B-TESTS-2`, sin fechar, con BE-48 y BE-49;
> BE-50 en el orden de `B-FUTURO`; §3: marca del jueves, viernes y sábado re-fechados, domingo como comodín provisional, colchón global 2 m; §6: medición tras BE-42).
> Versiones anteriores: 3.2 — 11 nov 2026, bitácora `2026-11-11` (§2b: `B-TESTS` cerrado con el CI duro y BE-46; `B-GUARD-TESTS m1` hecho; BE-47 en `B-GHOST-ADMIN`;
> §3: marca del miércoles, semana re-fechada, colchón global 3 m; §4 y §8: el trinquete de ADR-0005 deja de regir; §6: columna
> del CI duro y medición tras BE-39);
> 3.1 — 10 nov 2026, bitácora `2026-11-10` (§2b: A4 sale de `B-PAGOS` y entra en `B-TESTS`, hecho en rama junto con
> AF-16; BE-42 en `B-GUARD-TESTS`; §3: marca del martes y nota de fechado; §6: medición sobre `item/a4`, compuerta en verde sin
> `--soft`); 3.0 — 9 nov 2026, cambio de premisa, bitácora `2026-11-09` (la capacidad pasa a un solo régimen, Bogotá hasta
> nuevo aviso, 11 m/semana `(CONTEXT §2)`: §3 funde "Régimen Prado" y "Régimen final" en una sola tabla con presupuesto
> recalculado y la semana en curso fechada; §2b: `B-TESTS`, `B-GHOST-ADMIN` y `B-GUARD-TESTS` con la nota de fechado; §8: los
> riesgos de Prado pasan a condicionales y entra el riesgo del documento después del corte de código; al cierre del mismo día:
> §2b `B-TESTS` con AF-12 y AF-13; §3 marca del lunes, A4 deslizado un día y la semana re-fechada; §6 medición sobre
> `item/af-12`);
> 2.7 — 7 nov 2026, bitácora `2026-11-07` (§2b: `B-TESTS` con AF-07 y BE-32
> hechos, pendientes A4, medición y `--soft`; §3: marca del sábado y nota de estado, sin fechar la
> semana siguiente por decisión de David; §6: medición al cierre del 7 nov sobre `item/be-32`, con `tests/` dentro de mypy);
> 2.6 — 6 nov 2026, bitácora `2026-11-06` (§2b: `B-TESTS` con BE-33, A2, AF-02 y AF-07
> hechos y BE-32 pendiente; bloque nuevo `B-GUARD-TESTS` (BE-39, BE-40), por fechar; §3: marca del viernes, fila nueva del último día de
> Bogotá (sábado de trabajo) y nota del presupuesto; §6: medición al cierre del 6 nov, todo lo rojo con dueño). Versiones
> anteriores: 2.5 — 5 nov 2026, bitácora `2026-11-05` (§2b: `B-TESTS` recibe BE-33, los
> residuales de ruff y mypy de `app/` sin dueño; bloque nuevo `B-GHOST-ADMIN` con BE-34..BE-38, los cinco rincones de la
> verificación de BE-02, por fechar en §3; al cierre: §2b `B-TESTS` con BE-02 hecho y AF-07, `B-PAGOS` con A4 adelantado;
> §3: marca del jueves, `B-TESTS` deslizado y declarado, fila del viernes reescrita con la decisión de David; §6: medición
> al cierre del 5 nov). Versiones anteriores: 2.4 — 4 nov 2026, bitácora `2026-11-04` (§2b: celda de `B-TESTS` tras BE-15
> hecho y BE-07 desmentida: `m3`/`m4` recompuestos, `.env` sale a A4; §3: marca del miércoles, alargado en horas; §6:
> medición de `bloque/b-tests` al cierre, sin abrir columna). Versiones anteriores: 2.3 — 3 nov 2026, bitácora
> `2026-11-03` (§2b: `B-S1` hecho; `B-TESTS` pierde AF-03, AF-04 y AF-05, hechos el martes; §3: marca del martes,
> adelantado, y nota en el presupuesto; §6: medición al cierre del 3 nov); 2.2 — 2 nov 2026, bitácora `2026-11-02` (§2b: `B-FORMATO` y `B-CI` hechos,
> `B-HIGIENE` cerrado con dos ítems y el resto reasignado, `B-TESTS` retira `--soft` del CI y recibe AF-02/03/04, `B-FUTURO`
> recibe lo no hecho en orden de criticidad; §3: marca del lunes y filas de la reunión con María Paula; §6: columna del 2 nov y nota sobre la
> precisión; §8: riesgo del flag `--soft`). Versiones anteriores: 2.1 — 1 nov 2026, bitácora `2026-11-01` (§3: marca del
> domingo comodín; §2b: `B-CHECK-DOCS` hecho); 2.0 — 31 oct 2026, bitácoras `2026-10-30` (decisiones del replan: capacidad en
> tres regímenes, orden de bloques, `B-PAGOS` partido, usabilidad por criterio, corte de código nuevo) y `2026-10-31`
> (escritura; paso 0 copia ↔ dueño por sección; acordeón; domingos comodín; orden de sacrificio). Versiones anteriores:
> `2026-10-28` (v1.7), `2026-10-27` (v1.6), `2026-10-26` (v1.5), `2026-10-25` (v1.4). Versionado según ADR-0007.
>
> **Premisas** (el plan se construye sobre ellas y no las repite): fecha y forma de entrega, capacidad de trabajo en un
> solo régimen, reglas de los dos comodines (tarde del sábado, domingo) y roles del equipo `(CONTEXT §2)`; lo que la propuesta compromete
> `(CONTEXT §3)`; alcance por el criterio de §1-D3. Progreso diario: `docs/bitacora/`; estado del proyecto y próximo
> paso: `(CONTEXT §8)`; avance del plan: columna `Cierre` de §3.

---

## 1. Las tres decisiones sobre las que se construye el plan

- **D1 — Pruebas de usabilidad reales y remotas** `(CONTEXT §6)`. No se fabrica evidencia. Protocolo y criterio de
  fecha en §7.
- **D2 — Flujo agéntico simplificado: determinismo por herramientas, no por prosa** `(ADR-0001)`. Estado y diseño del
  flujo: `(CONTEXT §5)`; inventario: `.claude/`; guía de uso: `(README de sesiones)`.
- **D3 — Criterio de alcance del MVP.** Entra lo que la propuesta compromete `(CONTEXT §3)`, lo mínimo para que una
  reserva funcione de punta a punta (crear, pagar, ver que existe y en qué estado), y lo que el gerente pidió en el
  último sprint planning, si cabe antes del corte de código nuevo (fila-hito de §3). Lo demás es `B-FUTURO`, con
  justificación por ítem. Prioridad de la deuda: (a) indefendible ante jurado, (b) bloquea un feature del alcance,
  (c) barata. La decisión por ítem vive en `docs/backlog.md`; la agrupación en bloques y su secuencia, en §2b.

---

## 2. Reparto de trabajo

- **David:** código, calidad, pruebas, artefactos técnicos y capítulos de arquitectura, metodología y resultados
  `(CONTEXT §2)`. La bitácora diaria es evidencia de Scrum y del desarrollo asistido por IA; quién la redacta y quién
  responde por ella: `(README de sesiones)`.
- **María Paula:** documento, con el reparto acordado en `(CONTEXT §2)`. Su trabajo es `B-MP-DOC` (§2b), sin medias
  jornadas: su tiempo no se planifica aquí; las revisiones de David se pagan dentro de `B-TESIS`.

## 2b. Bloques de trabajo (composición y secuencia)

Un bloque agrupa ítems del backlog que se implementan y se mezclan juntos (normalmente un PR). Esta tabla no lleva
fechas: la fecha de cada media jornada vive solo en §3, y el detalle de cada ítem solo en `docs/backlog.md`. La
columna **Secuencia** numera las medias jornadas de 4 h (`m1`, `m2`, …) de cada bloque, en orden y sin fechas; §3 las
cita por número (`B-RESERVAS m3`) y nunca las repite. Deslizar es mover un número a otra fecha; la secuencia no se
toca. `[señal]` marca una media jornada que necesita red.

| Bloque | Ítems del backlog | Qué es | Secuencia (m = media jornada de 4 h) |
|---|---|---|---|
| `B-BE01` | BE-01, P1, A7 | Primera deuda por el flujo: `storage.py` sin HTTP, imports muertos de `security.py`, copia síncrona; contrato de capas 4 KEPT | Hecho (PR #61) |
| `B-CHECK-DOCS` | AF-01 | Reglas de ADR-0008 y su addendum en `scripts/check_docs.py`: días fuera de §3 (también dentro de PLAN), fecha de entrega en PLAN = CONTEXT §2, bloque citado existe en §2b, encabezado de versión (ADR-0007), fila de §3 cerrada sin marca, listado de citas por dueño (`--copias`), copia de hecho duro sin cita como hallazgo, columna Decisión con exactamente un bloque | m1 especificación a dos manos (David + Mentor, ~1 h) → Claude Code: verificar → planear → implementar → auditar → `/pr`. **Hecho** `(backlog AF-01)`; residuales en `(backlog AF-02)` |
| `B-FORMATO` | `ruff check --fix` (sin I001: `(backlog A4)`) + `ruff format` sobre todo el repo | Dos commits mecánicos en ese orden (lint-fix, luego format), sin cambios de lógica; `.git-blame-ignore-revs` los oculta en `blame` | **Hecho (PR #70)** |
| `B-CI` | `scripts/check.py` en `.azure-pipelines/ci-pipeline.yml`; `fail_under` y `precision` de cobertura | El CI ejecutó la compuerta con `--soft format,ruff,mypy` (tolerados en rojo) hasta que `B-TESTS` lo retiró; piso de cobertura con holgura, no trinquete `(ADR-0005)` | **Hecho (PR #71)** |
| `B-HIGIENE` | SEC1, A9 | Ítems XS/S de la auditoría por el flujo entero, en orden de severidad; el bloque tenía tope de 1 m y lo no hecho recibió decisión nueva el mismo día (todo en la celda de `B-FUTURO`, en orden de criticidad) | **Cerrado** (dos ítems en 1 m; la media jornada entera cupo dos ítems por el flujo, dato para dimensionar XS en Prado) |
| `B-S1` | S1, Alembic (`env.py` importa `app.models`) | Modelos a `Mapped[]`/`mapped_column` antes de crear `Reservation`; mypy cae a casi cero | **Hecho (PR #74; ADR-0010).** Fue una sola jornada corta: tres fases en un PR, mypy 44 → 10; el resto del día fue a AF-05 y AF-04, de `B-TESTS` |
| `B-TESTS` | BE-15 (= §9; huecos B2/B3/B4 dentro), BE-02, BE-33 (residuales de ruff y mypy de `app/` sin dueño; con A4 es la compuerta en verde), A2 (revisión), AF-02 (puntos 2 y 3), BE-32 (residuales de BE-15), AF-07 (comando literal en seis sitios; lo edita David), AF-12 (import-linter por su entry point, sin `.exe`: la compuerta debe correr bajo Smart App Control; hallado el 9 nov al ir a verificar A4), AF-13 (`run()` captura `OSError`: la compuerta nunca muere sin RESUMEN; fase B del mismo ítem), A4 (configuración centralizada en un `Settings` validado al arrancar, ADR-0013; viene de `B-PAGOS` por decisión de David: es el ítem que deja la compuerta en verde y permite retirar `--soft`), AF-16 (Context7 alcanzable desde `plan-redactor` y `fase-ejecutor`), BE-46 (dependencias fijadas en `constraints.txt`, ADR-0014; trabajo emergente del miércoles: el CI estricto instalaba un FastAPI distinto del de desarrollo). **Hechos:** el CI duro y BE-46 el miércoles (PR #89: `--soft` y el grupo de variables fuera del YAML, ADR-0005 superado; PR #92 `(backlog BE-46)`); A4 y AF-16 el martes en `item/a4` (nueve fases, nueve PASS, compuerta en verde sin `--soft`; PR #88 mezclado esa noche `(backlog A4)`); AF-12 y AF-13 el
lunes en `item/af-12` (dos fases, dos PASS, PR #87 mezclado esa noche `(backlog AF-12)`); BE-33 el viernes (PR #81, cuatro fases, ruff 53 → 9, mypy 10 → 5); A2 el viernes como decisión (ADR-0012, PR #82; su trabajo nació como BE-39/BE-40 en `B-GUARD-TESTS`); AF-02 el viernes (PR #83, puntos 2, 2b y 3); AF-07 el viernes en rama, mezclado esa noche (PR #84); **BE-32 el sábado** (PR #85; nueve fases, nueve PASS, `tests/` dentro de `mypy.files`; cifras en `(backlog BE-32)`); BE-02 el jueves (PR #80, confirmada por el flujo, una fase); BE-15 el miércoles (seis fases + D-bis, ADR-0011); BE-07 desmentida el miércoles, sin código; AF-03, AF-04 y AF-05 por adelantado el martes (días en §3). "La suite deja de depender de `.env`" lo saldó A4 en su fase B (`conftest.py` de la raíz) | Suite conforme a `AGENTS.md` §5 (lo que quede fuera, declarado en BE-32 con dueño); al cerrar, ADR-0005 caduca si la compuerta queda en verde y se **retira `--soft` del YAML del CI** (parte del entregable: CI duro) | m1–m2 BE-15 (hecho, con alargue en horas) · m3 `/deuda-verificar BE-02` antes de planear (misma fuente que BE-07), A2, BE-32 si cabe · m4 cierre; compuerta medida; `--soft` fuera; AF-02 (puntos 2 y 3) en PR propio (hecho). **Bloque cerrado el miércoles:** medición final en `develop`, `--soft` fuera y CI estricto probado en su propio PR (columna nueva en §6) |
| `B-RESERVAS` | BE-19, BE-13, BE-17, BE-18, A3 (solo en el código nuevo) | Módulo de reservas según ADR-0002 | m1 modelos 2.0 (`Package` ampliado, `PackageAvailabilityWindow`, `Reservation` con `Index(unique=True, postgresql_where=…)`), enums de estado, tests RED · m2 migración `--autogenerate` **revisada** con tres comprobaciones: `max_capacity → party_size` como `alter_column` (no drop/add), `WHERE` del índice parcial presente, migración corrida contra el dump de staging; repositorio `add()`/`flush()` sin `commit()` (A3) · m3 crear: guardia BE-13 (409), expiración perezosa en la misma transacción, `DateAlreadyReserved` desde `IntegrityError` → 409 · m4 cancelar; listar las mías (BE-17, paginado); disponibilidad por rango · m5 admin (listar, filtrar por estado) y métricas (BE-18, un endpoint de agregados) · m6 auditoría, `/pr` |
| `B-PAGOS` | BE-16, ADR de pagos, A5, BE-12 (ADR; código si cabe) | Puerto `PaymentGateway` de dos sentidos (iniciar pago; interpretar evento), `FakeAdapter` que aprueba por regla y puede notificar, ruta de webhook idempotente y transiciones de estado de la reserva: todo local, sin red; reservas, frontend y tests funcionan contra él. A5 y BE-12 van aquí por ser configuración y trabajo local que cabe en las mismas mañanas, no por ser pagos (A4 estuvo aquí hasta pasar a `B-TESTS`) | m1 ADR de pagos (puerto de dos sentidos, `FakeAdapter`, transiciones, idempotencia por id de transacción + estado) → aprobación · m2 conmutador Fake/Wompi como un campo del `Settings` que ya existe `(ADR-0013)`; puerto + `FakeAdapter` + ruta de webhook + transiciones; flujo reserva → pago falso → evento falso → `confirmed`; tests con evento duplicado · m3 resto de m2; `echo`, `lifespan`, cliente Azure (A5); BE-12 (ADR; `session_version` si cabe) · m4 auditoría, `/pr`; PR `develop` → `staging`; **pre-aviso** al gerente con ventana para la usabilidad (§7) `[señal]` |
| `B-WOMPI` | BE-27 | Adaptador real: crea la transacción/checkout en el sandbox, verifica la firma del evento y lo mapea al evento del puerto. Sin lógica de negocio; necesita red y URL pública; deslizable sin bloquear nada | m1 adaptador (transacción, checkout, firma, mapeo) con fixtures de eventos · m2 prueba en sandbox con tarjetas de prueba y webhook real a `staging` `[señal]` · m3 cierre, PR aparte; si el criterio de §7 se cumple entero, confirmación de la ventana al gerente |
| `B-ORDEN` | BE-08 | `display_order` + endpoint + `ORDER BY` | m1 migración `display_order`, `PATCH /packages/{id}/display-order`, `ORDER BY display_order NULLS LAST, created_at` |
| `B-FE-BASE` | FE-01, FE-06, FE-12 | Interceptor 401, sistema de diseño (tokens, componentes base) | m1 lints de Flutter; tema con tokens (color, tipografía, espaciado, radios) · m2 componentes base (botón con hover, campos, tarjetas, estados vacío/error) · m3 interceptor 401 → login; tema aplicado a autenticación y catálogo |
| `B-FE-LISTA` | FE-03, FE-04 (layout), FE-05 (señal visual), FE-07, FE-08, FE-09, FE-11, refresco al volver + pull-to-refresh (mitigación de BE-14) | Aplicar el sistema de diseño a todo; skeletons; lista corta | m1 tokens en todas las pantallas; FE-03, FE-08, FE-09 · m2 skeletons en lista y detalle (FE-11); señal visual del kanban (FE-05); FE-07; refresco y pull-to-refresh |
| `B-FE-RESERVAS` | FE-13, BE-28, manifest PWA (nombre e iconos de Ecotur) | Reserva, checkout (Wompi o `FakeAdapter`), listado mínimo de mis reservas, métricas, orden en kanban; builds Android y web | m1 `reservation_service`; selector de fecha alimentado por disponibilidad · m2 flujo de reserva (crear; detalle que re-consulta el paquete y maneja 404/409 con mensaje claro) · m3 checkout contra `FakeAdapter` · m4 mis reservas (listado mínimo con estado) · m5 métricas admin (tabla mínima) · m6 orden en kanban (BE-28) · m7 manifest; builds Android y web · m8 PR a `staging`; prueba manual de punta a punta `[señal]` |
| `B-QA` | Caja negra, bug bash, D1 (usabilidad, criterio de §7), despliegue a `main` | Evidencia para el capítulo de evaluación | m1–m2 casos de caja negra por módulo (tabla) · m3 bug bash · m4 correcciones · m5 despliegue a `main`, capturas `[señal]` · m6 instrumentos de usabilidad (de María Paula si se acordó; si no, de David) · m7–m8 sesiones con testers turista `[señal]` · m9 sesión con el gerente `[señal]` · m10 transcripción, SUS, lista de correcciones · m11–m18 correcciones de usabilidad · m19 segunda pasada de caja negra · m20 OpenAPI revisado; cierre de PRs · m21 medición de §6; despliegue final a `main` `[señal]` · m22 corte de código nuevo (hito de §3) |
| `B-DOCS-TEC` | UML, MER, OpenAPI, manual técnico, README | Anexos técnicos | m1–m2 UML desde código (componentes, secuencia de reserva y pago, casos de uso) · m3 MER · m4 OpenAPI como anexo · m5–m6 manual técnico de despliegue · m7 README y revisión de anexos · m8 colchón del bloque |
| `B-TESIS` | Capítulos de arquitectura, metodología, resultados; integración con María Paula; entrega | El documento | m1–m3 arquitectura (desde los ADR) · m4–m6 metodología (Scrum + IA + flujo + lecciones; bitácoras como evidencia) · m7–m9 resultados (§6, caja negra, SUS, correcciones derivadas) · m10–m11 integración con María Paula · m12 `B-FUTURO` como capítulo · m13 conclusiones · m14 referencias · m15 primera lectura completa · m16–m17 correcciones · m18 formato, figuras, PDF · m19 segunda lectura · m20–m21 correcciones finales, checklist de entrega · m22 margen |
| `B-MP-DOC` | Especificación de requisitos ampliada con historias de usuario (OE1); wireframes y diagramas de UX/UI completados (OE2); avances de metodología; manuales y documentación compartidos (OE4) | Trabajo de María Paula según el reparto acordado `(CONTEXT §2)`; David entrega las historias de usuario, revisa wireframes, diagramas y la narrativa de Scrum. Sin medias jornadas: su tiempo no se planifica aquí; lo que David revisa se paga con las `m` de `B-TESIS` (m10–m11, integración) | — (hitos de revisión por fechar en §3 cuando haya fecha de entrega) |
| `B-GHOST-ADMIN` | BE-34 (bootstrap de superadmin), BE-35 (siempre queda un superadmin activo), BE-36 (recuperar y reactivar entre pares), BE-37 (`null` en opcionales → 422), BE-38 (auditoría de cambios reales), BE-47 (un test exige que `TEST_ENVIRONMENT` cubra todos los campos de `Settings`; entra con BE-34, que añade campos, sin media jornada propia) | Que ningún jurado pueda dejar la plataforma sin administrador: los cinco rincones que la verificación de BE-02 (5 nov) midió fuera de su alcance, todos casos de prueba de sustentación. Primero `/deuda-verificar` de cada uno por regla, aunque la verificación de BE-02 ya los midió | m1 BE-34 y BE-35 (las dos Altas: bootstrap y regla del último superadmin) · m2 BE-36, BE-37, BE-38 y cierre. Bloque creado el 5 nov; fechado en §3 el 9 nov con la razón de David: el día de la demostración ningún jurado puede degradarse ni dejar la plataforma sin superadmin |
| `B-GUARD-TESTS` | BE-39 (un test de rechazo por ruta protegida, en RED con los mutantes M1–M7), BE-40 (aplicar la frontera de ADR-0012: re-chequeo de auditoría, guard de superadmin, una forma de inyectar identidad, comentarios), BE-42 (`get_current_user` exige el `scope` de acceso: un token de verificación de correo no sirve de bearer; hallado por la auditoría de la fase D de A4) | Que la suite vigile la autorización: la verificación de A2 (6 nov) midió que ningún test depende del guard de rol (quitarlo deja la suite en verde). Tema nuevo, distinto de `B-GHOST-ADMIN` (reglas de dato). Primero `/deuda-verificar` de cada uno por regla, aunque la verificación de A2 ya los midió | m1 BE-39 (17 rutas, tests en RED, mutantes re-ejecutados) · m2 BE-40, BE-42 (los dos tocan `dependencies.py`, ya con la red de m1) y cierre. **m1 hecho** (PR #91 `(backlog BE-39)`: cinco fases, 45 casos en `tests/test_route_guards.py`); **m2 hecho:** BE-40 (PR #94 `(backlog BE-40)`: cinco fases, frontera de ADR-0012 aplicada) y BE-42 (PR #95 `(backlog BE-42)`: tres fases, solo un token de acceso abre una ruta protegida). **Bloque cerrado el jueves.** Bloque creado el 6 nov; fechado en §3 el 9 nov, justo después del CI duro y antes de `B-GHOST-ADMIN` |
| `B-TESTS-2` | BE-48 (ningún test fija `performed_by` en las seis mutaciones de paquetes), BE-49 (dobles de `tests/test_user_service.py` sin aserción de argumentos; residual de la fase E de BE-40) | Huecos de la suite hallados después de cerrar `B-TESTS`, que no son defecto del ítem que los encontró. Bloque creado el 12 nov por decisión de David: existe para que el hallazgo tenga fila y sitio, pero **no entra en la secuencia ni en el presupuesto de §3**; David lo considera trabajo futuro mientras no lo feche | — (sin medias jornadas; si David lo fecha, se estima ese día y la secuencia restante de §3 sube en lo que cueste) |
| `B-FUTURO` | Todo lo marcado "Sale" en el backlog. Lo que salió de `B-HIGIENE`, del más crítico al menos, para halar de vuelta en ese orden si se libera colchón: SEC2 · BE-26 · SEC3 · BE-50 (enlace de verificación reutilizable; no viene de `B-HIGIENE`: David la coloca aquí por ser experiencia de usuario visible en una demostración) · A6 · D5 · P2 (`detalle`→`detail`) · BE-25 · D2 · D3 · BE-24 · BE-23 · D4 · A8 · S5 · S2 · S6 · S7 · P3 · BE-09 · D6/S3. Lo demás: BE-10, BE-11 derivado, BE-14 tiempo real, BE-20, BE-21, BE-22, BE-29, FE-10 | Capítulo de trabajo futuro, con justificación por ítem | — |

---

## 3. Cronograma (acordeón)

La secuencia de cada bloque vive en §2b y no se toca. Aquí se fecha **solo la semana en curso**; la
siguiente se fecha al cierre del último día trabajado de la semana, contando las medias jornadas perdidas (PLAN sube
versión menor cada vez). Si una fila se desborda, se recorta alcance (§1-D3, orden en §8), nunca sueño ni el tiempo
del documento. La columna `Cierre` lleva la marca del día (`✔` hecho, `◐` parcial, `✘` ningún bloque de la fila) con
el número de la bitácora que lo cuenta; es una copia consciente de la bitácora `(ADR-0008)`.

**Presupuesto:** `m` disponibles `(CONTEXT §2)` − secuencia restante = colchón, recalculado en cada
fechado. Ni la tarde del sábado ni el domingo entran en "disponibles": la tarde del sábado es comodín que adelanta o
repaga y se decide ese mismo sábado; el domingo solo repaga déficit y se decide al cierre `(CONTEXT §2)`. Disparador:
**colchón negativo** → primero los comodines disponibles; si no alcanzan, el orden de sacrificio de §8 ese mismo día.
Regla de red (vigente solo si David se muda, `(CONTEXT §2)`): commits locales siempre; push, PR y despliegues en la
siguiente media jornada con señal (sin push no hay CI; hasta entonces la compuerta local es la única).

**Hitos fijos (no se re-fechan):**

- **Vie 18 dic, 18:00 — corte de código nuevo.** Después solo correcciones de usabilidad, bugs de caja negra y lo que
  un bloque ya abierto necesite para cerrar su PR. Se mueve solo hacia antes: si la reserva de punta a punta y la
  usabilidad ya están, las horas sobrantes van al documento; nunca hacia después. Lo que no esté → `B-FUTURO` (§1-D3).
  Inclinación de David (9 nov, por formalizar al fechar la semana del 7 dic; riesgo en §8): declarar el corte el día
  que `B-QA m21` cierre, tomando el 18 dic como tope y no como fecha, para que el documento reciba las `m` sobrantes.
- **Lun 11 ene — entrega en línea** `(CONTEXT §2)`. El domingo anterior es margen, no día planificado.
- **Reunión con María Paula**: hecha; `B-MP-DOC` definido en §2b y reparto en `(CONTEXT §2)`. Próxima reunión y entrega de las historias de usuario de David a ella: por fechar (se añaden aquí cuando tengan fecha).

### Días cerrados bajo el plan v1.x (historia; el detalle está en cada bitácora)

| Día | Bloques planeados | Cierre |
|---|---|---|
| Vie 23 oct | Aprobación del plan, backlog, CONTEXT/PLAN; tooling y línea base | ✔ 23 |
| Sáb 24 | Flujo agéntico v1; `B-BE01` | ◐ 24 |
| Dom 25 | (media jornada) PR docs+tooling, ADR-0004, `/deuda-verificar BE-01` | ◐ 25 |
| Lun 26 | `B-BE01`, `B-FORMATO`, `B-CI`, `B-HIGIENE` | ✘ 26 |
| Mar 27 | `B-BE01`; `B-FORMATO`, `B-CI`, `B-S1` | ◐ 27 |
| Mié 28 | `B-S1`, `B-TESTS`, `B-RESERVAS` (esquema) | ✘ 28 |
| Jue 29 | `B-RESERVAS`, `B-PAGOS` | ✘ 29 |
| Vie 30 | `B-PAGOS`, `B-ORDEN` | ✘ 30 |
| Sáb 31 | PLAN 2.0; `B-CHECK-DOCS` | ◐ 31 |

### Semana del 2 al 7 nov, bajo el plan de tres regímenes (cerrada; historia)

**Presupuesto:** disponibles **10 m** (lun a vie: el sábado 31 ya está cerrado en la tabla de arriba, el sábado
siguiente es la mudanza `(CONTEXT §2)`; los sábados sí cuentan en Prado y en el régimen final; domingos fuera).
Secuencia: 9 (`B-FORMATO`+`B-CI` 1 · `B-HIGIENE` 1 ·
`B-S1` 2 · `B-TESTS` 4 · cierre 1) + **1 m de colchón**. Primera aplicación de las reglas, el 31 oct: la secuencia
era 11 (`B-CHECK-DOCS` 1, `B-HIGIENE` 2) contra 10 → colchón −1; el domingo entra como comodín y repaga
`B-CHECK-DOCS`; `B-HIGIENE` baja de 2 m a 1 m y esa media jornada queda como colchón de la semana. El recorte se hace
al principio y se deshace al final si sobró, nunca al revés: si el viernes el colchón no se gastó, vuelve a
`B-HIGIENE`; si se gastó, lo no hecho de `B-HIGIENE` recibe decisión nueva en el backlog ese día. Estado al cierre del
martes 3: `B-S1` cerró en poco más de un módulo y el resto del día hizo AF-05 y AF-04 de `B-TESTS` por adelantado, en
un día normal con colchón positivo (no comodín); el colchón del viernes sigue intacto y `B-TESTS` arranca el miércoles
con tres ítems menos. **Estado al cierre del viernes 6:** el colchón se gastó en `B-TESTS` como se decidió; aun así BE-32, A4, la medición y `--soft` no cupieron (BE-33 ocupó la mañana entera: cuatro fases por el flujo, 4 h). El sábado 7 pasa a ser día de trabajo en Bogotá (+2 m, fuera del presupuesto original de 10 m; David no viaja ese día) y es el último de este régimen: lo que no cierre el sábado recibe decisión nueva al fechar Prado. **Estado al cierre del sábado 7:** BE-32 hecha (PR #85, mezclado al cierre); A4, la medición y `--soft` no empezaron (nueve fases de BE-32, 11:24–17:11). David no viaja a Prado hasta nuevo aviso y declaró su capacidad para las semanas que vienen `(bitácora 2026-11-07)`; **la semana siguiente se fecha en la apertura del lunes, no en este cierre** (decisión de David, 17:37), y ese día se actualizan CONTEXT §2 y las tablas de régimen de esta sección.

| Día | Mañana | Tarde | Cierre |
|---|---|---|---|
| Dom 1 nov | **Comodín (fuera del presupuesto):** `B-CHECK-DOCS m1`: especificación a dos manos, implementación por Claude Code, `/pr` | — | ✔ 1 |
| Lun 2 | `B-FORMATO`+`B-CI` m1 (dos PR propios). A primera hora: mensaje a María Paula para fijar la reunión | `B-HIGIENE m1` (tope: 1 m; lo que no quepa → decisión nueva en backlog hoy). **Hito: reunión con María Paula, 17:00–18:00, dentro de esta media jornada**; si ella no puede, mar 3 a la misma hora (come una hora de `B-S1 m2`); sus filas se escriben al cierre de ese día (PLAN 2.1) | ◐ 2 |
| Mar 3 | `B-S1 m1` (tres fases, PR #74 mezclado 15:15) | `B-S1 m2` no hizo falta: AF-05 (PR #75) y AF-04 (PR abierto con el cierre), adelantados de `B-TESTS` | ✔ 3 |
| Mié 4 | `B-TESTS m1`: BE-07 desmentida por el flujo (sin código); BE-15 verificado, planeado y fases A–C | `B-TESTS m2`: BE-15 fases D, E, D-bis y F, PR abierto con el cierre. Arranque real 08:30; pausa 16:00–17:28 (documento); el día se alargó en horas por decisión de David, sin gastar colchón | ✔ 4 |
| Jue 5 | `B-TESTS m3` **no existió** (mañana: lectura, aclaraciones y PR #78 de cierre de BE-15; mediodía y tarde: mercado hasta las 16:30) | `B-TESTS m4` parcial: BE-02 verificado, planeado, una fase, auditado y mezclado (PR #80); BE-33..BE-38 y `B-GHOST-ADMIN` en el backlog; AF-07 nueva. **`B-TESTS` deslizado y declarado:** BE-33, A2, AF-02 (2 y 3), BE-32, AF-07, compuerta y `--soft` pasan al viernes | ◐ 5 |
| Vie 6 | **Colchón gastado en `B-TESTS` (decisión de David, 5 nov 18:48):** BE-33, A2, AF-02 puntos 2 y 3, BE-32, **todos completos**; AF-07 si no se hizo el jueves | A4 (adelantado de `B-PAGOS`) y cierre; si sobra tiempo, halar de `B-FUTURO` en el orden en que salió de `B-HIGIENE`. Compuerta medida en `develop`; `--soft` fuera si verde (→ ADR-0005 superado). **Si no se alcanza a mezclar, sábado 7** (David no viaja a Prado ese día; replan por hacer en el cierre del viernes, no el jueves). El cierre de Bogotá (CORS en las tres Web Apps, prueba del frontend, PR `develop` → `staging` `[señal]`, dump para `B-RESERVAS m2`, mudanza, fechar Prado) queda sujeto a ese replan | ◐ 6 |
| Sáb 7 | **Día de trabajo en Bogotá (David no viaja; decisión 5 nov 18:48, confirmada el 6 a las 17:26): cerrar la semana.** Merge del PR de `item/af-07` (AF-07 + contrato del auditor + cierre del 6). `B-TESTS`: BE-32 **completo** (`/deuda-verificar` → adenda con la lista acumulada en su fila → planear → fases; `tests/` entra en `mypy.files`, opción b; los 4 opcionales `str`/`None` de A4 como conjunto declarado) | A4 (adelantado de `B-PAGOS`): primero los dos tests de firma (precondición, fila A4), `/deuda-verificar` y `/deuda-planear`, fases hasta donde alcance; al cerrar, `unfixable I001` fuera e I001 aplicado; compuerta medida en `develop`; `--soft` fuera si verde (→ ADR-0005 superado). El cierre de Bogotá (CORS en las tres Web Apps, prueba del frontend, PR `develop` → `staging` `[señal]`, dump para `B-RESERVAS m2`) solo si sobra; si no, primera media jornada con señal de Prado. Fechar la semana de Prado y `B-GHOST-ADMIN`/`B-GUARD-TESTS` en el cierre del sábado; la fecha de la mudanza, por confirmar `(CONTEXT §2)`. Domingo 8: descanso | ◐ 7 |

### Régimen Bogotá hasta nuevo aviso `(CONTEXT §2)`: desde la semana del 9 nov hasta el final del plan

Sustituye a las secciones "Régimen Prado" (19 m, colchón 1) y "Régimen final" (62 m, colchón 1) de PLAN 2.x: la capacidad
es una sola `(CONTEXT §2)` y el régimen de Prado no arranca. Fechado el 9 nov, en la apertura, por decisión del 7 nov.

**Presupuesto (calculado el 9 nov):** disponibles **91 m** hasta el sábado 9 ene: 6 semanas completas de 11 m (9–14 nov,
16–21, 23–28, 30 nov–5 dic, 7–12 dic, 14–19 dic) = 66; semana del 21 al 26 dic = 7 (24 y 25 fuera); semana del 28 dic al
2 ene = 7 (31 y 1 fuera); semana del 4 al 9 ene = 11. Festivos colombianos sin descontar (candidatos: lun 16 nov, mar 8 dic;
−2 m cada uno si no se trabajan; David lo declara al fechar cada semana). **Secuencia restante: 87 m** = planificación del
9 nov 0,5 · `B-TESTS` 3 (AF-12 0,5 + A4 2 + CI duro 0,5) · `B-GUARD-TESTS` 2 · `B-GHOST-ADMIN` 2 · puesta en `staging` 0,5
(configuración, sin flujo: `CORS_ORIGINS` en las tres Web Apps, PR a `staging`, cliente Flutter contra `staging`, dump)
· `B-RESERVAS` 6 · `B-PAGOS` 4 · `B-ORDEN` 1 · `B-FE-BASE` 3 · `B-FE-LISTA` 2 · `B-FE-RESERVAS` 8 · `B-WOMPI` 3 · `B-QA` 22 ·
`B-DOCS-TEC` 8 · `B-TESIS` 22. **Colchón 4 m** al fechar; **3,5 m al cierre del lunes 9** (AF-12 costó 1 m; −0,5 si los dos festivos no se trabajan), más las tardes de sábado que
existan y el domingo de margen anterior al día final `(CONTEXT §2)`. **Orden decidido por David al fechar esta semana:** `B-TESTS` (A4, CI duro) → `B-GUARD-TESTS`
→ `B-GHOST-ADMIN` → puesta en `staging` → `B-RESERVAS` → `B-PAGOS` → `B-ORDEN` → `B-FE-BASE` → `B-FE-LISTA` →
`B-FE-RESERVAS` → `B-WOMPI` → `B-QA` → `B-DOCS-TEC` → `B-TESIS`. **Reparto del colchón alrededor del corte (18 dic):** hasta
el corte, 66 disponibles contra 57 de secuencia (+9); después, 25 disponibles contra 30 de `B-DOCS-TEC` + `B-TESIS`
(−5). El total cierra, el tramo del documento no: el riesgo y sus dos salidas están en §8 y se deciden al fechar la
semana del 7 dic. `B-PAGOS m4` (PR a `staging` y pre-aviso al gerente) ya no exige señal: la red es la de Bogotá.

**Estimaciones de A4 y del CI duro (dato detrás de las cifras):** A4 toca 15 `os.getenv` en 6 archivos de `app/`
`(backlog A4)`, ~4 fases con lógica (tests de firma; `Settings` con `security`/`database`; `email`/`storage`/`routers/user`/
`main`; I001 y `unfixable` fuera, los dos `jwt.encode` de `tests/` a `make_token`) a ~55 min por fase medidos en BE-33, más
verificar (~15 min), planear (~25 min) y PR → 2 m. CI duro: medir sobre `develop`, un commit al YAML, la línea de estado de
ADR-0005 y la columna de §6 → 0,5 m.

| Día | Mañana | Tarde | Cierre |
|---|---|---|---|
| Lun 9 nov | Planificación de la semana (½ m: 15 pendientes decididos, CONTEXT 4.0, PLAN 3.0, PR #86 mezclado en `bb03f46`). **Trabajo emergente:** al ir a verificar A4, Smart App Control bloqueó `lint-imports.exe` y la compuerta murió sin RESUMEN → AF-12 por el flujo en `item/af-12` (verificación confirmada, adenda con AF-13 como fase B). Bloqueo del cliente Flutter resuelto en local (`--web-port 3000`; era la lista blanca de SEC1) | AF-12 (`6ee6923`) y AF-13 (`5cbdec1`), dos auditorías PASS, commit de documentos de David (`3e47d99`), `/pr` a las 18:05; la tarde entera (1 m, no ½): verificar 15 min, planear 25, dos fases ~27 min cada una más auditorías y aclaraciones. **A4 no empezó**: pasa al martes | ◐ 9 |
| Mar 10 | Arranque a las 09:51. **A4** en `item/a4`: verificación confirmada y adenda de 13 puntos (inventario de variables de las tres Web Apps incluido). **Trabajo emergente:** AF-16 (los agentes no alcanzaban Context7 por su lista cerrada de herramientas), arreglado antes de planear. Plan de nueve fases aprobado con E0, ADR-0013; fase A (tests de firma) | Fases B–I, nueve auditorías PASS, E1; **compuerta en verde sin `--soft`** (§6); prueba de humo en local con el `.env` real; `/pr`; CI del PR en verde y PR #88 mezclado a las 20:29. **CI duro no empezó** (era "si alcanza"): miércoles por la mañana, como prevé la fila siguiente | ◐ 10 |
| Mié 11 | Arranque a las 09:00. **CI duro hecho:** compuerta medida en `develop` (`c957941`), `--soft` y el grupo de variables fuera del YAML, ADR-0005 superado, PR #89 mezclado en `4956346` con el CI estricto en verde (§6). `B-GUARD-TESTS m1`: BE-39 verificada con adenda, plan de tres fases y E0 (fase D); fase A | Fases B–E de BE-39 (E2 añadió la fase E), cinco auditorías PASS, **622 tests · 96,47 %**; PR #90 mezcló por error un solo commit y PR #91 llevó el ítem (`a0578ae`). **Trabajo emergente:** el CI de #91 cayó porque instalaba un FastAPI más nuevo que el del venv → todas las dependencias fijadas en `constraints.txt` (PR #92, ADR-0014, BE-46). Jornada hasta las 19:30. **`B-GUARD-TESTS m2` no empezó**: pasa al jueves | ◐ 11 |
| Jue 12 | Arranque a las 09:10. `B-GUARD-TESTS m2`, primera mitad: **BE-40** en `item/be-40`: verificación confirmada y adenda de cinco puntos; plan de cuatro fases aprobado con E0 (dos correcciones de dictado halladas por el Mentor); fases A–D con cuatro PASS; la fase E nació del opcional de la auditoría de D (E1, E2) y cerró un mutante que sobrevivía a toda la suite; PR #94 mezclado en `deb0b1e` a las 13:35, con la mañana alargada 35 min | **BE-42** en `item/be-42`: verificación confirmada y adenda de cinco puntos; plan de tres fases con E0; tres PASS sin opcionales; PR #95 mezclado en `86b0617` a las 17:54. **`B-GUARD-TESTS` cerrado**; 638 tests · 96,82 % (§6). Filas nuevas BE-48 y BE-49 (bloque `B-TESTS-2`, sin fechar) y BE-50. Cierre documental y AGENTS en `docs/agents-test-factories`. **`B-GHOST-ADMIN m1` no empezó**: pasa al viernes | ◐ 12 |
| Vie 13 | `B-GHOST-ADMIN m1` (BE-34 con BE-47, BE-35) | `B-GHOST-ADMIN m2` (BE-36, BE-37, BE-38), `/pr`, merge | |
| Sáb 14 | Puesta en `staging` (½ m): `CORS_ORIGINS` en las tres Web Apps, `JWT_SECRET_KEY` de `staging` rotada, PR `develop` → `staging`, login y registro desde el cliente (registro = correo real: cierra BE-33 D; login con tokens que ya llevan `scope`), `grep` de `role` en el Flutter (cierra la nota de BE-02), dump de `staging`. Luego `/deuda-verificar BE-19` y adenda | Comodín `(CONTEXT §2)`: `B-RESERVAS m1` (modelos 2.0, BE-31 decidida, tests RED) si hay tarde, que David confirma el viernes o ese mismo sábado; si no, pasa a la semana siguiente. Fechar la semana del 16 | |
| Dom 15 | Comodín de recuperación `(CONTEXT §2)`, **provisional** (David, jueves 12): `B-RESERVAS m2` (migración `--autogenerate` revisada contra el dump), la media jornada que el jueves dejó sin sitio en la semana. Se hala hacia atrás si viernes y sábado abren hueco; David lo confirma o lo anula al cierre del sábado | — | |

**Re-fechado al cierre del lunes 9:** AF-12 + AF-13 costaron 1 m, no ½ (el flujo completo de dos fases con sus auditorías y
las aclaraciones de David), y A4 no empezó. Secuencia restante de la semana 9 m (A4 2 · CI duro 0,5 · `B-GUARD-TESTS` 2 ·
`B-GHOST-ADMIN` 2 · `staging` 0,5 · `B-RESERVAS` m1–m2 2) contra 9 m disponibles (mar–vie 8 + sáb 1) → **colchón 0**;
`B-RESERVAS m3` sale de la semana (era el sábado por la mañana) y solo vuelve con el comodín de la tarde del sábado.
`B-RESERVAS m3`–`m6` caen en la semana del 16, que se fecha el sábado 14 al cierre. Secuencia total del plan sin cambio (87 m);
el colchón global baja de 4 a 3,5 m.

**Fechado al cierre del martes 10:** sin cambios. A4 costó las 2 m estimadas (el arranque tardío se repuso por la tarde) e
incluyó AF-16. Secuencia restante de la semana 7 m (CI duro 0,5 · `B-GUARD-TESTS` 2 · `B-GHOST-ADMIN` 2 · `staging` 0,5 ·
`B-RESERVAS` m1–m2 2) contra 7 m disponibles (mié–vie 6 + sáb 1): colchón 0; colchón global 3,5 m. Dato para estimar: las
nueve fases de A4 costaron ~15–20 min cada una con su auditoría, también las que tocan `app/`, frente a los ~55 min de BE-33
con que se estimó; la diferencia la explica un plan que dicta el código y mide con sonda `(bitácora 2026-11-10)`.

**Re-fechado al cierre del miércoles 11:** el día hizo el CI duro (0,5 m) y `B-GUARD-TESTS m1` (1 m), y `m2` no empezó. BE-39
costó más que su media jornada: dos fases nacieron de enmiendas (D y E), el PR #90 hubo que repetirlo como #91 y fijar las
dependencias (BE-46) fue trabajo emergente fuera de la secuencia. Secuencia restante de la semana 5,5 m (`B-GUARD-TESTS m2` 1 ·
`B-GHOST-ADMIN` 2 · `staging` 0,5 · `B-RESERVAS` m1–m2 2) contra 5 m disponibles (jue–vie 4 + sáb 1): **colchón −0,5 m**.
Decisión de David: `B-RESERVAS m2` no sale de la semana; va a la tarde del sábado como comodín `(CONTEXT §2)`, que confirma el
viernes o ese mismo sábado; si no hay tarde, pasa a la semana del 16. Colchón global: 3,5 → **3 m**. Riesgo señalado por el
Mentor: `B-GUARD-TESTS m2` son dos ítems (BE-40 y BE-42), cada uno con verificación, plan y fases, en una mañana; si no cierran,
`B-GHOST-ADMIN m1` se desliza y se re-fecha el jueves.

**Re-fechado al cierre del jueves 12:** el día hizo `B-GUARD-TESTS m2` entero (BE-40 y BE-42) y costó las 2 m del día, no la
media jornada de la secuencia: es el riesgo que el Mentor señaló el miércoles (dos ítems, cada uno con verificación, plan y
fases). `B-GHOST-ADMIN m1` no empezó. Secuencia restante de la semana 4,5 m (`B-GHOST-ADMIN` 2 · `staging` 0,5 · `B-RESERVAS`
m1–m2 2) contra 3 m disponibles (vie 2 + sáb 1): **colchón −1,5 m**. **Decisión de David:** lo que el jueves no alcanzó va
provisionalmente al domingo, y se hala hacia atrás si en los días siguientes las fases salen en menos tiempo y se abre
espacio. Para no romper el orden de la secuencia (m1 antes que m2 en cada bloque), todo se corre media jornada y al domingo
va la última de la semana: `B-GHOST-ADMIN` completo el viernes; puesta en `staging` el sábado por la mañana; `B-RESERVAS m1`
en el comodín de la tarde del sábado; `B-RESERVAS m2` en el comodín del domingo, provisional. El domingo se declara el
jueves y no al cierre del último día trabajado, como pide `(CONTEXT §2)`: por eso es provisional y David lo confirma o lo
anula al cierre del sábado, cuando también se fecha la semana del 16. Con los dos comodines la semana cierra con +0,5 m;
sin el domingo, `B-RESERVAS m2` cae en la semana del 16. Secuencia total del plan sin cambio (`B-TESTS-2` no tiene medias
jornadas); colchón global 3 → **2 m**, que cada comodín usado repone en lo que cubra. Dato para estimar: las fases corrieron
a ~12 min cada una con su auditoría (BE-40: cuatro en 50 min; BE-42: tres en 40 min); el día se fue en lo que las rodea: de
la verificación escrita a la primera fase pasaron 2 h 25 min en BE-40 y 1 h 50 min en BE-42 (adenda, plan, revisión y
aprobación) `(bitácora 2026-11-12)`.

---

## 4. Definition of Done técnico

Aplica a cada PR: la compuerta `python scripts/check.py` pasa completa, también en el CI, que ya no tolera nada, y la
cobertura no baja `(AGENTS §6)`; el trinquete contra la línea base dejó de regir al quedar la compuerta en verde
`(ADR-0005)`; decisiones no triviales → ADR
`(AGENTS §7)`. Sesiones concurrentes con JWT sin estado son por diseño, no un bug; las opciones y el ADR previsto
están en `(backlog BE-12)`.

## 5. Flujo agéntico

Diagnóstico, decisión y lo que se conservó del flujo v0: `(ADR-0001)`; estado y diseño de compatibilidad:
`(CONTEXT §5)`; inventario: `.claude/`; guía de uso y rituales: `(README de sesiones)`. Las dos semanas de análisis
previas van al capítulo de metodología como lecciones aprendidas, con las observaciones archivadas como evidencia.

---

## 6. Línea base → resultado (métricas para el capítulo de resultados)

Medido con `python scripts/check.py` (Python 3.14) sobre `develop`. Columnas: línea base, estado tras el primer
ciclo del flujo (`B-BE01`), y la medición al corte de código nuevo (hito de §3), que se rellena ese día.

| Métrica | 24 oct, `e4fd14d` | 27 oct, `c8853af` (PR #61) | 2 nov, `7c6d606` (PR #71) | 11 nov, `c957941` (CI duro, PR #89) | Al corte de código |
|---|---|---|---|---|---|
| Archivos sin formatear (`ruff format --check`) | 34 de 90 | no medido | 0 | 0 de 60 | |
| Errores `ruff check` | 531 (E501 137 · D212 110 · B008 41* · UP045 33 · I001 29 · D205 28 · W292 21 · UP006 21 · F401 16 · B904 7 · resto < 12 c/u) | 362 | 98 | **0** | |
| Errores `mypy` | 44 en 12 archivos (29 en los dos servicios grandes; causa dominante: modelos tipados como `Column[...]` → S1, y `SECRET_KEY: str \| None` → A4) | 44 (mismo conjunto de líneas) | 44 | **0** en 55 archivos | |
| Contratos `import-linter` | **3 KEPT · 1 BROKEN.** Roto: "los servicios no conocen el transporte HTTP", por dependencia transitiva `services → core/storage → fastapi` y `services → core/security → fastapi/starlette` (BE-01 y P1). Antes de evaluar hubo que crear `app/api/__init__.py` | **4 KEPT · 0 BROKEN** | 4 KEPT | 4 KEPT | |
| Tests | 116 passed · 0 failed · 1 warning (S5) | 145 passed | 317 passed | 579 passed | |
| Cobertura (`pytest-cov`, ramas incluidas) | **89 %** (908 sentencias, 88 sin cubrir). Puntos ciegos: `core/storage.py` 28 %, `core/email.py` 69 %, `main.py` 77 %, `service_repository.py` 77 % | **93 %** (`core/storage.py` 100 %) | **92.68 %** | **96.29 %** | |
| Casos de caja negra pasados / totales | — | — | — | — | |
| SUS promedio (turista / admin) | — | — | — | — | |

Medición intermedia del 1 nov (`f6f73a9`, PR #69, AF-01): ruff 362; mypy 44 con `scripts/check_docs.py` ya dentro de
`mypy.files`; import-linter 4 KEPT; cobertura 93 % (solo `app`); **293 tests** (145 de `app` + 148 del script de docs).
No abre columna: el trinquete de ADR-0005 compara contra el 27 oct y el código de `app` no cambió.

Columna del 2 nov: medida por `/deuda-verificar SEC1` sobre `develop` tras `B-FORMATO` y `B-CI` `(docs/deuda/SEC1/)`.
**Precisión:** hasta el 1 nov la herramienta imprimía la cobertura sin decimales; desde `B-CI` (`precision = 2`) imprime dos,
y esa cifra es la que se registra. Las columnas anteriores no se recalculan (mediciones fechadas con el método de su día).
El 92.68 % frente al 93 % del 27 oct no es una bajada: `ruff --fix` borró imports muertos (sentencias ejecutadas y
cubiertas), así que numerador y denominador bajaron; por eso `fail_under` es un piso (92) y no un trinquete. Al cierre
del 2 nov, `bloque/b-higiene` sin mezclar (`99593c1`): 360 tests · 94.77 % · ruff 82 · mypy 44 · 4 KEPT `(docs/deuda/A9/)`.
**Al cierre del 3 nov, `develop` = `e39825f` (PR #74 S1 + PR #75 AF-05):** 376 tests · 94.81 % · ruff 60 · mypy 10 en 5
archivos (ninguno en `app/models`; 34 de los 44 eran los modelos tipados como `Column[...]`, S1) · `Contracts: 4 kept, 0
broken.` **Desde `e39825f` la compuerta local no puede imprimir un contrato no medido** (AF-05): los "4 KEPT" de las
columnas anteriores medidos en local con el venv sin activar entre el 2 y el 3 nov no fueron medidos por la compuerta;
el del 27 oct (venv activo) y los del CI sí. El esquema no cambió con S1: `alembic check` idéntico antes y después
`(docs/bitacora/2026-11-03.md)`. No abre columna: el trinquete sigue comparando contra la última columna hasta `B-TESTS`.
**Al cierre del 4 nov, `bloque/b-tests` sin mezclar (`2a1ee41`, BE-15 completo):** 396 tests · 94.81 % · ruff 54 (en
`tests/` 1) · mypy 10 · `Contracts: 4 kept, 0 broken.` Cada fase medida por el auditor con la cifra exacta de la tabla
del plan `(docs/deuda/BE-15/gaps.md)`. Tampoco abre columna: la columna de `B-TESTS` se escribe al cerrar el bloque
con la compuerta en `develop`.
**Al cierre del 5 nov, `develop` = `c83150c` (PR #80, BE-02):** 416 tests · 94.82 % · ruff 53 (en `tests/` 1) · mypy 10 ·
`Contracts: 4 kept, 0 broken.` Medido por David con el venv por ruta sobre `50d489e` antes de mezclar. No abre columna:
`B-TESTS` sigue abierto (deslizado al viernes, §3).
**Al cierre del 6 nov, `develop` = `2872a11` (PR #83, AF-02; antes PR #81 BE-33 y PR #82 A2):** **547 tests · 96,11 % ·
ruff 9 (8 I001 de A4 en `app/` + 1 en `tests/test_user_service.py:3`, BE-32) · mypy 5 (`str | None`, A4) · `Contracts: 4 kept, 0
broken.`** Medido por el auditor de la fase B de AF-02 sobre `23af07b` (misma base de código que el merge). BE-33 bajó ruff 53 → 9
y mypy 10 → 5 y subió la cobertura 94,82 → 96,11 % (las ramas de token de `dependencies.py` y todo `email.py` pasan a tener
tests). **Todo lo rojo tiene dueño: A4 y BE-32.** No abre columna: `B-TESTS` sigue abierto (BE-32 y la medición final, sábado §3).
**Al cierre del 7 nov, `develop` = `08c3a3d` (PR #85, BE-32; medido sobre `a7991a4`, mismo código que el merge):** **548 tests · 96,11 % (`TOTAL 943 23 138 19`, idéntico) · ruff 8 (los 8 I001 de `app/`, A4) · mypy 9 (5 de `app/` + `tests/test_user_service.py:105,203,280,298`, todos `str | None` de A4) · `Contracts: 4 kept, 0 broken.`** Medido por el auditor de la fase I. **Desde BE-32 mypy mide `tests/`** (`pyproject.toml` `files` con `"tests"`, 53 fuentes frente a 35): la cifra de mypy no es comparable con las anteriores sin esa aclaración; la suite propia pasó de 7 errores a 0 y el 9 es íntegramente el conjunto de A4. 547 → 548: tres copias HTTP fuera, cuatro tests nuevos. No abre columna: `B-TESTS` sigue abierto (A4, medición en `develop`, `--soft`).

**Al cierre del 9 nov, `develop` = `f6a4201` (PR #87, AF-12 y AF-13; medido sobre `5cbdec1`, mismo código que el merge):** **549 tests · 96,11 % (`TOTAL 943 23 138 19`,
idéntico) · ruff 8 · mypy 9 (conjunto de A4) · `Contracts: 4 kept, 0 broken.`** Medido por el auditor de la fase B con la
compuerta completa **imprimiendo RESUMEN**: desde AF-12 import-linter corre por su entry point (sin `lint-imports.exe`) y desde
AF-13 un paso que no arranca sale `FALLA (<tipo>)` en vez de abortar la compuerta. 548 → 546 (siete tests de AF-05
sustituidos por cinco) → 549 (tres de AF-13). La línea base del día se midió paso a paso porque la compuerta abortaba en
la máquina de David (`docs/deuda/AF-12/verificacion.md`). No abre columna: `B-TESTS` sigue abierto (A4, CI duro).

**Al cierre del 10 nov, `develop` = `2dfb564` (PR #88, A4 y AF-16; medido sobre `c122cb1`, mismo código que el merge):** **579 tests · 96,29 % (`TOTAL 968 22 138 19`) ·
ruff 0 (`All checks passed!`) · mypy 0 (`Success: no issues found in 55 source files`) · `Contracts: 4 kept, 0 broken.` ·
`Compuerta superada.`, exit 0, sin `--soft`.** Medido por el auditor de la fase I. **Es la primera compuerta en verde completa
desde la línea base del 24 oct.** 549 → 579: 3 tests de firma JWT, 23 de configuración (`tests/test_config.py`) y 4 de los
consumidores (uno por fase D, E, F y G). La suite pasa sin `.env` ni variables del CI (copia exportada, `579 passed`). 0
`os.getenv` y 0 `load_dotenv` en `app/` y `alembic/`. El CI del PR (Linux, Python 3.14.10) dio las mismas cifras con los seis pasos en verde y `Compuerta superada.` sin tolerar
nada, ya sin bloque `env:`. No abre columna: la abre el CI duro al medir `develop`.

**Columna del 11 nov (CI duro, cierre de `B-TESTS`):** medida por David sobre `develop` = `c957941` con el venv por ruta, sin
`--soft`: `Compuerta superada.`, exit 0; 60 archivos con formato; `All checks passed!`; `Success: no issues found in 55 source
files`; `Contracts: 4 kept, 0 broken.`; `579 passed`; `TOTAL 968 22 138 19 96.29%`. El CI de PR #89 (Linux, Python 3.14.10) dio
las mismas cifras ejecutando `python scripts/check.py` sin `--soft` y sin grupo de variables: desde `4956346` un paso en rojo
bloquea el PR, y ADR-0005 queda superado. Frente a la línea base del 24 oct: ruff 531 → 0, mypy 44 → 0, contratos 3 → 4,
tests 116 → 579, cobertura 89 % → 96,29 %.
**Al cierre del 11 nov, `develop` = `a0578ae` (PR #91, BE-39; antes PR #92, BE-46):** **622 tests · 96,47 % · ruff 0 · mypy 0 (56
archivos) · `Contracts: 4 kept, 0 broken.` · `Compuerta superada.`** Medido por el auditor de la fase E de BE-39 sobre `fee04bc`
(mismos `app/` y `tests/` que el merge; `develop` añade `constraints.txt`, sin código); el CI de PR #91, ya con las
dependencias fijadas, dio `622 passed` y 96,47 % (revisado por David). 579 → 622: 45 casos de
`tests/test_route_guards.py` menos los 2 de `tests/test_audit.py` que sustituyen. La cobertura sube porque tres casos de 422
ejercitan el handler de validación de `app/main.py`; por lo mismo la compuerta muestra 8 warnings en vez de 5, todos la
constante deprecada de S5. **Desde PR #92 el CI y la imagen instalan con `-c constraints.txt`** (ADR-0014): el CI de ese PR
instaló 76 distribuciones, ninguna con versión distinta de la del venv de desarrollo.
**Al cierre del 12 nov, `develop` = `86b0617` (PR #95, BE-42; antes PR #94, BE-40):** **638 tests · 96,82 % · ruff 0 · mypy 0 (56
archivos) · `Contracts: 4 kept, 0 broken.` · `Compuerta superada.`** Medido por el auditor de la fase C de BE-42 sobre `8c38f47`
(mismos `app/` y `tests/` que el merge). 622 → 618 con BE-40: salen los 8 tests de las dos reglas de solo rol retiradas de la
política y entran 4 netos (delegación y filtros de auditoría, caso "admin → 403" de la ruta de superadmin). 618 → 638 con
BE-42: 17 casos de token de verificación como bearer, 2 en `tests/test_token_failure_paths.py` y 1 del `scope` impuesto.
El check de CI de PR #94 salió en verde en GitHub sobre `a17ab55` (build #20261112.3); su log, con las cifras exactas, no se
pudo abrir ese día (Azure DevOps sin responder). El de PR #95 también salió en verde (visto por David en GitHub).

\* B008 son los 41 `Depends(...)` en argumentos por defecto: patrón oficial de FastAPI; se configuró como
excepción y desaparece al migrar a `Annotated` (D6/S3). Evidencia por fase del 27 oct: `(ADR-0006)`.

---

## 7. Protocolo real de pruebas de usabilidad

- **Cuándo (criterio, no fecha), en dos pasos:** **pre-aviso** al gerente cuando el backend de reservas y pagos esté
  en `staging` contra `FakeAdapter` (`B-PAGOS m4`), proponiendo una **ventana de una semana**, no un día (reprogramar
  una fecha concreta cuesta credibilidad); **confirmación** del día dentro de la ventana cuando el flujo de reserva
  funcione de punta a punta en `staging` desde el cliente, con Wompi en sandbox si `B-WOMPI` está mezclado o con
  `FakeAdapter` si no (declarándolo como limitación en resultados: se mide todo el flujo menos la pantalla de Wompi).
  Tope: **15 de diciembre**, para que las correcciones y el capítulo de resultados quepan. Alerta: con la secuencia de
  §3 el flujo completo en el cliente (`B-FE-RESERVAS m8`, 31,5 m de secuencia desde el 9 nov) cae a unas dos semanas y
  media del tope; un deslizamiento de una
  semana deja la usabilidad en el tope sin días de corrección (mitigación en §8). La sesión es real: el gerente es un miembro real de ASOPRADO
  y el usuario administrador real.
- **Participantes:** gerente (usuario administrador, videollamada con pantalla compartida) + 4–5 personas con perfil
  turista (muestra por conveniencia, **declarada como tal** en el documento). Remoto es un método reconocido.
- **Tareas por rol:** turista: registrarse, explorar un paquete, reservar, pagar (sandbox o falso), verificar su
  reserva en "mis reservas". Admin: iniciar sesión, crear/editar un paquete, ver reservas, ver métricas.
- **Instrumentos:** consentimiento informado (1 página), guion de tareas, tiempo y errores por tarea, cuestionario
  **SUS** (10 preguntas, estándar), 3 preguntas abiertas.
- **Evidencia:** capturas, tabla de resultados, SUS por participante, hallazgos → correcciones en `B-QA` → se documenta
  "qué se corrigió a partir de las pruebas".

---

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| **Déficit en cualquier régimen: remedios en orden** | Primero el comodín del domingo, si está disponible, decidido al cierre del último día trabajado `(CONTEXT §2)`. Solo si no alcanza o no hay domingo, recorte en este orden; cada escalón es una decisión por ítem escrita en el backlog el día que se toma, y **sale, no se traslada**: (1) `B-WOMPI`: `BE-27 → B-FUTURO`; la usabilidad se declara con `FakeAdapter` (§7). (2) Lo de `B-HIGIENE` aparcado en `B-QA` → `B-FUTURO`. (3) Pulido que nadie prometió y nadie mide: skeletons (FE-11), señal del kanban (FE-05), refresco y pull-to-refresh, `B-ORDEN` y BE-28; en Prado, antes de eso, `B-FE-BASE` al mínimo (tokens, 401, componentes básicos). (4) Correcciones de `B-QA` que no afecten al SUS ni a la caja negra. (5) Historial completo del turista (filtros, pasadas/próximas, detalle extendido) → `B-FUTURO`; el listado mínimo de mis reservas se queda: §1-D3 y la tarea de usabilidad de §7 lo requieren. **No se recortan:** métricas de admin en su versión mínima (`CONTEXT §3` las compromete; piso: BE-18), listado mínimo de mis reservas, `B-TESIS`, `B-DOCS-TEC`, la sesión de usabilidad. La lista existe para que la decisión no se tome cansado ni en Prado |
| **El documento no cabe después del corte de código** (medido el 9 nov al fechar con la capacidad nueva): tras el 18 dic quedan 25 m de calendario (24, 25, 31 dic y 1 ene fuera) para 30 m de `B-DOCS-TEC` + `B-TESIS`, mientras que antes del corte sobran 9 m. El total del plan cierra; el tramo del documento no | Dos salidas, ambas dentro de las reglas del hito (§3: "se mueve solo hacia antes"): (a) `B-DOCS-TEC m1`–`m4` (UML, MER, OpenAPI: se generan desde código que ya existe) empiezan antes del corte, en las esperas de `B-QA` (ventana del pre-aviso, sesiones con testers); (b) el corte se declara el día que `B-QA m21` cierre y el 18 dic queda como tope. Inclinación de David (9 nov): (b), y además (a) si hace falta. Lo que **no** se hace: abrir el corte a features nuevos después de declararlo; la puerta para lo que pida gerencia es antes del corte, por §1-D3, y después solo las correcciones que el hito ya admite. Se formaliza al fechar la semana del 7 dic |
| Mudanza a Prado (hoy no prevista, `(CONTEXT §2)`): señal de internet caída hasta dos días sin aviso, cortes de luz de horas | Si ocurre: acordeón de §3 (secuencia fija, fechas por semana) y regla de red (push, PR y despliegues en medias jornadas con señal); si en la primera semana allí se pierden más de dos `m`, mitigación de entorno (trabajar desde un sitio con señal estable); si aun así el colchón queda negativo, orden de sacrificio de la primera fila |
| Sin push no hay CI (solo con la mudanza) | La compuerta local `(AGENTS §6)` es la única hasta la siguiente media jornada con señal; ningún PR se abre sin haberla pasado localmente |
| La usabilidad llega al tope de §7 sin días de corrección (pago, listado y despliegue desde el cliente caen a dos semanas y media del tope, §7) | Pre-aviso en dos pasos (§7) desacopla la semana de aviso del frontend; si al PR a `staging` de `B-PAGOS` el backend no está, `B-FE-BASE` se reduce al mínimo para defender la ventana; historial completo y pulido ceden antes que la usabilidad |
| Reprogramar la usabilidad cuesta credibilidad | Al gerente se le propone una ventana de una semana, no un día; se confirma el día dentro de la ventana cuando el criterio de §7 se cumple entero |
| `WompiAdapter` consume más de lo previsto o no hay red | `FakeAdapter` deja el flujo completo y testeable por el mismo camino (webhook incluido); `B-WOMPI` es solo adaptador, PR aparte, primero en el orden de sacrificio |
| Frontend se desborda (área débil) | Sistema de diseño primero, belleza después; métricas admin en su versión mínima; pulido y historial completo ceden antes |
| El documento se queda sin tiempo | Corte de código nuevo fijo (hito de §3), movible solo hacia antes; tres semanas reservadas; `B-TESIS` y `B-DOCS-TEC` fuera del orden de sacrificio; sueño no negociable |
| María Paula no responde o no tiene avances | Reunión esta semana (hito de §3); el plan solo asume su aporte en formato, manual de usuario y plantillas; si no aparece, el manual se recorta a lo mínimo |
| Usabilidad tarde o sin gerente | Aviso con ventana; tope en §7; si el gerente no puede, se hace con los testers turista y se declara la ausencia del perfil admin |
| Tiempo en meta-trabajo del flujo y de los documentos (del 26 al 31 oct) | El flujo y los documentos solo cambian si un bloque se bloquea por su culpa; `B-CHECK-DOCS` tiene alcance fijo; el fechado semanal son cinco minutos |
| Perfeccionismo en deuda | Regla a-b-c de §1-D3; lo demás es deuda conocida documentada |
| Línea base desactualizada entre ítems | Un solo ítem en curso; hash de la verificación comparado por el ejecutor. Con la compuerta en verde y el CI estricto, una línea base vieja ya no puede esconder deuda nueva: el criterio es absoluto `(ADR-0005)` |
| El CI toleraba ruff y mypy en rojo (`--soft`, `B-CI`): un PR que añadiera deuda nueva pasaba en verde | **Riesgo cerrado al cerrar `B-TESTS`:** `--soft` salió del YAML y el CI ejecuta la compuerta estricta (§6); el trinquete del auditor `(ADR-0005)` dejó de hacer falta. Riesgo que lo sustituye, también cerrado: el CI instalaba versiones distintas de las de desarrollo `(ADR-0014)` |

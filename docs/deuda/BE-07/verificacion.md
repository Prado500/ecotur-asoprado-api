# Verificación — BE-07: el schema de update permite superar las 10 imágenes

**Veredicto:** desmentida
**Fuente del ítem:** docs/backlog.md (sección A, fila BE-07, línea 37; pareja citada en §A2 fila D4, línea 83) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` §D4 (línea 632) como contraste
**Fecha:** 2026-11-04

## Qué describe el ítem
Nota de David (`txt`): "Al actualizar un paquete, el schema permite superar las 10 imágenes". Resolución
propuesta: "Mismo validador en el schema de update que en el de create (o un tipo compartido). Test."
Prioridad Media, bloque `B-TESTS` (m3). La fila D4 del backlog lo describe como "su pareja BE-07 (validador de
update)". El propio informe (§D4) contradice la premisa: dice que la comprobación `> 10` del update es código
muerto **porque Pydantic ya la rechazó con `max_length=10` en el schema**.

## Evidencia en el código
- `app/schemas/service.py:114` — `ServiceUpdate.image_urls: list[HttpUrl] | None = Field(None, max_length=10)`.
  El límite existe en el schema de update.
- `app/schemas/service.py:55-57` — `ServiceCreate.image_urls: list[HttpUrl] = Field(default=[], max_length=10, ...)`.
  Mismo validador (mismo `max_length=10`) que en update: la resolución "mismo validador" ya se cumple.
- `app/schemas/service.py:104` — `ServiceImageOutput.image_urls: ... Field(default_factory=list, max_length=10)` (DTO de salida del uploader; tercera copia del literal en schemas).
- Historia: `git show 0544e04:app/schemas/service.py` (29 jul 2026) ya tenía en la línea 78
  `image_urls: Optional[List[HttpUrl]] = Field(None, max_length=10)`; `7f99c7f` (2 nov) solo lo reescribió a
  `list[HttpUrl] | None` (ruff UP). El límite en update lleva en el código desde el 29 jul.
- Comprobación en tiempo de ejecución (lectura, sin tocar código):
  `ServiceUpdate(image_urls=[u]*10)` → OK; `ServiceUpdate(image_urls=[u]*11)` → `too_long` en `('image_urls',)`;
  JSON Schema publicado: `'maxItems': 10` en la rama array del `anyOf`.
- `tests/test_services.py:295-314` — `test_update_package_image_ceiling_limit_rejection` (desde `4d10898`, 27 ago):
  PUT con 11 URLs → `assert response.status_code == 422` y `assert "image_urls" in response.text`. Pasa en la
  línea base. La parte "Test." de la resolución también existe.
- `app/services/tourist_services_service.py:289` — `if len(update_data.image_urls) > 10:` en `update_package_details`.
  Inalcanzable: la cobertura de la línea base marca **290** (el `raise`) como no ejecutada. Es deuda D4, no BE-07.
- `app/services/tourist_services_service.py:48` — `if len(package_data.image_urls) > 10:` en create. Inalcanzable
  por el mismo motivo: cobertura marca **49** como no ejecutada. Deuda D4.
- `app/services/tourist_services_service.py:238` — `if len(images_files) > 10:` en `image_uploader`. **Necesaria**:
  opera sobre `list[UploadFile]` multipart (`app/api/routers/service.py:55`), sin schema que limite. Cubierta por
  `tests/test_services.py:210-224` (11 ficheros → 400, `upload_image.assert_not_awaited()`).
- Única ruta de escritura de imágenes en un paquete existente: `PUT /servicios/{service_id}`
  (`app/api/routers/service.py:142`, cuerpo `ServiceUpdate` en :145). La semántica es de **reemplazo total**
  (`service.images.clear()` en `tourist_services_service.py:320`, luego `append` por cada URL en :332-334), así
  que el total tras el update es exactamente `len(image_urls) ≤ 10`; no hay acumulación con las imágenes previas.
  No existe otro endpoint ni repositorio que añada `ServiceImage` (grep `ServiceImage\(|images\.append` en `app/`:
  solo :65-66 de create y :333-334 de update).

## Ficheros afectados (mapa completo)
- `app/schemas/service.py` — contiene el límite en create (:57), update (:114) y salida del uploader (:104). Sin
  defecto respecto a BE-07; el literal `10` repetido tres veces es la vertiente DRY de D4.
- `app/services/tourist_services_service.py` — dos copias muertas del límite (:48, :289) y una necesaria (:238). D4.
- `tests/test_services.py` — el test de BE-07 ya existe (:295-314); el del uploader (:210-224).
- `app/api/routers/service.py` — solo rutas (:50-55 uploader multipart, :142-145 PUT); sin lógica de límite.
- `alembic/` — sin restricción de número de imágenes por paquete (`service_images` creada en
  `alembic/versions/c48e057bd4cd_creacion_tabla_service_images_y_.py:24` sin CHECK ni trigger). No exigible por
  CHECK de fila (es un agregado entre filas); se menciona solo para que el planificador no lo dé por existente.

## Rincones no mencionados por la fuente
- **Calidad del test existente frente a AGENTS §5.** `tests/test_services.py:295-314` afirma solo código 422 y que
  la cadena `"image_urls"` aparece en el texto. Su docstring promete "rejected prior to any Azure Blob Storage I/O
  execution", pero no lo afirma (no hay `assert_not_awaited` sobre `promote_to_permanent`/`delete_image`), ni
  verifica que las imágenes del paquete en BD no cambiaron (mutación de estado), ni usa la estructura del JSON
  (`detail[0]["loc"] == ["body", "image_urls"]`, `type == "too_long"`).
- **Bordes sin test:** no hay test de update con exactamente 10 URLs (aceptado) ni de create (`POST /servicios/`)
  con 11 URLs (422). `grep -n "range(1[01])\|range(10)" tests/` solo devuelve :216 (uploader) y :305 (update).
- **D4 confirmada de paso:** las copias de :48 y :289 son inalcanzables (cobertura 49 y 290 en "Missing"). Esto no
  es BE-07; la fila D4 del backlog la manda a `B-FUTURO`.
- **Etiquetado del backlog:** la fila D4 (línea 83) llama a BE-07 "validador de update" como si faltara; el
  informe §D4 dice lo contrario. La premisa de BE-07 es falsa desde el 29 jul.

## Patrones de detección (copiables)
```bash
# 1. El límite en los schemas (debe seguir devolviendo create :57, update :114, output :104)
grep -n "max_length=10" app/schemas/service.py

# 2. Ninguna lista de imágenes de entrada sin max_length (debe devolver solo las líneas con max_length)
grep -nE "image_urls: .*list\[HttpUrl\]" app/schemas/service.py

# 3. Comprobaciones manuales del límite (D4: :48 y :289 muertas, :238 necesaria)
grep -rnE "len\(.*\) > 10" app/

# 4. Rutas que escriben imágenes (solo create :65-66 y update :333-334)
grep -rnE "ServiceImage\(|images\.append" app/

# 5. Tests del límite (update :305, uploader :216)
grep -rnE "range\(1[01]\)" tests/

# 6. Prueba de comportamiento directa del schema
./venv/Scripts/python.exe -I -c "import sys; sys.path.insert(0,'.'); from app.schemas.service import ServiceUpdate as U; U(image_urls=['https://x.blob.core.windows.net/a/b.jpg']*11)"
#   -> ValidationError too_long en image_urls
```

## Línea base (python scripts/check.py)
- Base develop: `7877829` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` == `git rev-parse origin/develop` == `78778296f39e564c00db70f8446294d4f5c0686f`; HEAD = misma revisión, rama `bloque/be-tests-BE-07`)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (exit 1)

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

- pytest: `376 passed, 5 warnings in 19.55s` (0 failed)
- Cobertura total: `94.81%` (`Required test coverage of 92.0% reached. Total coverage: 94.81%`)
- ruff format: `52 files already formatted`
- ruff check: `Found 60 errors.` / `[*] 11 fixable with --fix (9 unsafe fixes available with --fix --unsafe-fixes).`
- mypy: `Found 10 errors in 5 files (checked 35 source files)`
- import-linter: `Contracts: 4 kept, 0 broken.` (los 4 KEPT)
- Cobertura de los archivos del ítem: `app\schemas\service.py 96.23%` (Missing 120);
  `app\services\tourist_services_service.py 96.38%` (Missing 49, 290, 338->347)

**La compuerta ya falla antes de tocar nada** (ruff check y mypy); son fallos preexistentes, ajenos a BE-07,
conocidos en `B-TESTS`/backlog (p. ej. `service_repository.py:83` es el residual de S1).

## Conclusión para el planificador
BE-07 no tiene defecto de código que corregir: `ServiceUpdate.image_urls` tiene `max_length=10` desde el 29 jul,
rechaza 11 con 422 y existe test. No hace falta plan de corrección; lo honesto es cerrar el ítem como "desmentida"
en el backlog (y corregir la redacción de D4, que lo presenta como validador ausente). Si David quiere aprovechar
el hueco en `B-TESTS m3`, lo único con valor es **endurecer el test** existente (`tests/test_services.py:295-314`)
según AGENTS §5: estructura del 422 (`loc`/`type`), CDN no tocado (`assert_not_awaited`), imágenes en BD sin
cambios, y bordes 10-aceptado en update y 11-rechazado en create. NO tocar: las copias `> 10` de
`tourist_services_service.py:48/:289` (eso es D4, `B-FUTURO`) ni la de :238 (necesaria; borrarla abre la puerta a
subidas multipart ilimitadas). Un "tipo compartido" (`Annotated[list[HttpUrl], Field(max_length=10)]`) es DRY
opcional y también pertenece a D4, no a BE-07.

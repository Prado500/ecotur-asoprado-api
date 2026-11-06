# Verificación — BE-33: residuales de ruff y mypy en `app/` sin dueño

**Veredicto:** parcial (49 de 50 persisten: 44 de ruff y 5 de mypy; solo se corrigió la D205 de `user_access_policy.py:40`, por BE-02)
**Fuente del ítem:** `docs/backlog.md` (fila BE-33, l.68). No remite a un tag de auditoría; la fila S1 (l.100) apunta aquí por `service_repository.py:83`
**Fecha:** 2026-11-06

## Qué describe el ítem
Lo manual que `B-FORMATO` no autocorrigió el 2 nov y quedó como medición en PLAN §6 sin fila que lo trabaje: 45 de ruff
en `app/` (E501 19, D205 13, D415 6, B904 4, W293 3) y 5 de mypy (`dependencies.py:93,108`, `user_service.py:132,133`,
`service_repository.py:83`). Excluye lo que tiene dueño A4: 8 I001 en `app/` y 5 `str | None`. Promete "sin cambio de
comportamiento" y que BE-33 + A4 dejan la compuerta en verde.

## Evidencia en el código

Conteo real de hoy: **44 de ruff** (E501 19, **D205 12**, D415 6, B904 4, W293 3), no 45. Mypy, los 5 en las líneas citadas.

### Ruff (44)
- `app/api/dependencies.py` (6): D205 `:80`; E501 `:80,83,120` (docstrings); B904 `:99` (`except jwt.ExpiredSignatureError: raise HTTPException(`), `:105` (`except jwt.InvalidTokenError: raise credentials_exception`).
- `app/core/email.py` (10): E501 `:37,38,44,45,55,56,59,63`; W293 `:57,61`. **Las diez están dentro del f-string HTML del correo** (`html_content`, l.31-73), es decir, en datos de ejecución.
- `app/db/database.py` (1): W293 `:16`, dentro de una cadena suelta usada como comentario (l.13-17), sin efecto en ejecución.
- `app/repositories/audit_repository.py` (1): D205 `:27`.
- `app/repositories/service_repository.py` (8): D415 `:15,28,38,48,75`; D205 `:60`; E501 `:18` (comentario), `:60` (docstring).
- `app/repositories/user_repository.py` (1): D205 `:46`.
- `app/schemas/audit.py` (2): D205 `:18,26`.
- `app/schemas/token.py` (2): D205 y D415 `:5`.
- `app/services/user_access_policy.py` (8): D205 `:21,78,95,110,129`; E501 `:37,74,106`. Las tres E501 son **textos de `AuthorizationError` que lee el usuario final**.
- `app/services/user_service.py` (5): E501 `:46` (docstring), `:217` (**f-string de `message` que lee el usuario**), `:337` (docstring); B904 `:126,130`.

### Mypy (5)
- `app/api/dependencies.py:93` — `email: str = payload.get("sub")`; la l.94 comprueba `if email is None`, así que la anotación es falsa.
- `app/api/dependencies.py:108` — `get_non_deleted_user_by_email(token_data.email)`. Causa distinta de la l.93: `TokenData.email` es `str | None = None` (`app/schemas/token.py:21`). `TokenData` se usa solo en `dependencies.py:97`.
- `app/services/user_service.py:132,133` — `email: str = payload.get("sub")`, `scope: str = payload.get("scope")`; la l.135 comprueba `email is None`.
- `app/repositories/service_repository.py:83` — `save_service(...) -> TouristService` termina en `return result.scalars().first()`.

### La parte corregida
- `app/services/user_access_policy.py:40` (numeración previa a BE-02): esa D205 desapareció al reescribir el docstring en PR #80. Comprobado con ruff sobre el archivo anterior a la mezcla (9 errores frente a los 8 de hoy) y en `docs/deuda/BE-02/handoff-Fase_A.md:83-84`.

### Frontera con A4 (comprobada; fuera de BE-33)
- I001 (8): `app/api/dependencies.py`, `app/api/routers/audit.py`, `app/core/email.py`, `app/db/database.py`, `app/repositories/user_repository.py`, `app/schemas/audit.py`, `app/services/audit_service.py`, `app/services/user_service.py`, todos en la l.1.
- Mypy `str | None` (5): `app/db/database.py:11`, `app/core/security.py:71,87`, `app/api/dependencies.py:92`, `app/services/user_service.py:124`.

## Ficheros afectados (mapa completo)
| Archivo | Ruff BE-33 | Mypy BE-33 | Rojo de A4 que sigue tras BE-33 |
|---|---|---|---|
| `app/api/dependencies.py` | 6 | 2 | I001; mypy l.92 |
| `app/core/email.py` | 10 | 0 | I001 |
| `app/db/database.py` | 1 | 0 | I001; mypy l.11 |
| `app/repositories/audit_repository.py` | 1 | 0 | ninguno |
| `app/repositories/service_repository.py` | 8 | 1 | ninguno |
| `app/repositories/user_repository.py` | 1 | 0 | I001 |
| `app/schemas/audit.py` | 2 | 0 | I001 |
| `app/schemas/token.py` | 2 | 0 | ninguno |
| `app/services/user_access_policy.py` | 8 | 0 | ninguno |
| `app/services/user_service.py` | 5 | 2 | I001; mypy l.124 |
| **Total: 10 archivos** | **44** | **5** | |

Sin errores de estas reglas en `tests/`, `scripts/` ni `alembic/env.py`. Solo se tocaría `app/`, salvo los tests que pida el plan.

Cuenta esperada tras BE-33: ruff 53 → **9** (8 I001 en `app/` + 1 en `tests/test_user_service.py:3`, BE-32); mypy 10 → **5**.

## Rincones no mencionados por la fuente
1. **Dos zonas de BE-33 sin ninguna prueba.** La compuerta marca `app/core/email.py` Missing `29-82`: todos los tests parchean `send_verification_email` (`tests/conftest.py:140`), nadie afirma sobre el HTML. Y marca `app/api/dependencies.py` Missing `63, 95, 98-105, 111`: las dos B904 (l.99, 105) están en ramas que ningún test ejercita; `tests/` no tiene un token vencido o inválido contra una ruta protegida. Con la suite actual, "sin cambio de comportamiento" no queda demostrado ahí. En cambio, `user_service.py:126,130` sí están cubiertas (`tests/test_user_service.py:254,264`).
2. **Partir textos de usuario sin red.** Ningún test afirma sobre esas cadenas (AGENTS §5 lo prohíbe; grep en `tests/` sin resultados), de modo que un espacio perdido al partir `user_access_policy.py:37,74,106` o `user_service.py:217` no lo detecta nadie.
3. **W293 en `email.py:57,61` cambia los bytes del correo.** Quitar el espacio de esas líneas altera `html_content` (solo espacio en blanco). La igualdad exacta del cuerpo no es posible en esas dos líneas.
4. **Autofixes inseguros.** Las 9 "unsafe fixes" de ruff son D415 ×6 y W293 ×3, incluidas las del HTML. E501, D205 y B904 no tienen autofix. Las D205 de resumen partido suelen pedir reescribir el resumen, no solo insertar una línea (`token.py:5` ya tiene D205 + D415).
5. **`service_repository.py:83` tiene dos salidas y ambas pesan.** `save_service` tiene 4 llamadas (`tourist_services_service.py:129,168,209,347`). La de l.347 es el `return` de `update_package_details -> TouristService` (l.252): ensanchar a `TouristService | None` mueve el error a ese archivo, ajeno al mapa. Usar `scalar_one()` como `create_service` (`service_repository.py:25`) cambia una rama: sin fila, lanza en vez de devolver `None`. No hay borrado físico en `app/repositories` ni `app/services` (grep sin resultados), lo que hace esa rama muy improbable, no imposible. El archivo también tiene `commit()` (A3, l.17 y l.76).
6. **Criterio de ADR-0005 inalcanzable en 6 de los 10 archivos.** Exige "cero errores de ruff y mypy en los archivos tocados", pero `dependencies.py`, `email.py`, `database.py`, `user_repository.py`, `schemas/audit.py` y `user_service.py` conservan rojo de A4. Además, el hook `.claude/hooks/ruff_on_edit.py` saldrá con código 2 por I001 en cada edición de esos seis archivos; `unfixable = ["I001"]` (`pyproject.toml`) impide que los reordene, y no deben reordenarse a mano (riesgo de carga de `.env`, bitácora 2026-11-02). Precedente de excepción declarada: plan de BE-02 (l.228) y `docs/CONTEXT.md` §8.
7. **El desglose citado por la fila está viejo.** `docs/deuda/BE-15/verificacion.md` midió 60 errores en una base anterior y sus líneas de `user_access_policy.py` y `user_service.py` ya no valen. La fuente vigente es este archivo.
8. **`alembic/versions` no se mide.** Excluido por `extend-exclude`; con `ruff --isolated` da 16 errores de estas mismas reglas (E501 8, D415 6, W293 1, D205 1). No es `app/` ni entra en la compuerta; las migraciones aplicadas no se reescriben por estilo. No es deuda de BE-33.
9. **Para BE-32, no para BE-33.** `mypy tests` hoy da **11** errores en `tests/`, no los 6 (2+2+2) del residual 7 de la bitácora del 5 nov. Cuatro son `str | None` que dependen de A4 (`tests/test_user_service.py:103,197,274,292`). `tests/` sigue fuera de `mypy.files` (`pyproject.toml`), así que no cuentan en esta línea base.
10. **Hallazgos colaterales para el backlog, no para este ítem.** Docstrings falsos: `service_repository.py:28,38` citan `is_active`, pero el modelo y el filtro usan `is_available` (`app/models/service.py:41`); esas líneas tienen D415 y se tocarán. Español en código (AGENTS §4): `app/core/email.py:28`, `app/db/database.py:12`, `usuario` en `app/api/dependencies.py:108`.

## Patrones de detección (copiables)
```bash
# Ruff de BE-33: hoy "Found 44 errors."; objetivo 0
./venv/Scripts/python.exe -m ruff check app --select E501,D205,D415,B904,W293 --statistics
./venv/Scripts/python.exe -m ruff check app --select E501,D205,D415,B904,W293 --output-format=concise

# Mypy de BE-33 (por mensaje, porque las líneas se desplazan): hoy 5 líneas; objetivo 0
./venv/Scripts/python.exe -m mypy | grep -E 'Incompatible types in assignment|Incompatible return value type|"get_non_deleted_user_by_email"'

# Frontera con A4: deben seguir en 8 y 5 al cerrar BE-33, ni más ni menos
./venv/Scripts/python.exe -m ruff check app --select I001 --statistics
./venv/Scripts/python.exe -m mypy | grep -E 'has incompatible type "str \| None"' | grep -v get_non_deleted_user_by_email

# Fuente de los errores de mypy
grep -rnE '(email|scope): str = payload\.get' app
grep -n 'scalars().first()' app/repositories/service_repository.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `bab25c2`. Refrescada con `git fetch origin`; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop`.
- Comando: `./venv/Scripts/python.exe scripts/check.py` (salida redirigida a un archivo temporal para leerla). Python 3.14.3. Exit 1.
- **La compuerta ya falla antes de tocar nada:** ruff check y mypy en rojo, heredado.

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

- Pytest: `416 passed, 5 warnings in 12.60s` (416 pasados, 0 fallidos).
- Cobertura total: **94.82 %** (`TOTAL 944 34 138 22 94.82%`; piso 92).
- ruff format: `53 files already formatted`.
- ruff check: `Found 53 errors.` (`9 unsafe fixes available`). E501 19 · D205 12 · I001 9 · D415 6 · B904 4 · W293 3. En `app/` 52, en `tests/` 1.
- mypy: `Found 10 errors in 5 files (checked 35 source files)`.
- import-linter: `Contracts: 4 kept, 0 broken.` (4 KEPT, 0 BROKEN).
- check_docs: `Documentación coherente`.

## Conclusión para el planificador
- **Debe resolver:** los 44 de ruff y los 5 de mypy del mapa, con esos conteos y no los 45 de la fila; son 10 archivos, así que con el límite de 5 por fase hacen falta al menos dos fases. Resultado medible: ruff 9 y mypy 5, sin mover la frontera con A4 (compuerta aún en rojo: BE-33 solo no da el verde).
- **No debe tocar:** I001 ni el orden de imports, los 5 `str | None` de A4, `unfixable` en `pyproject.toml`, `--soft` del CI, los `commit()` de A3, `alembic/versions` ni los residuales de `tests/` (BE-32).
- **Debe declarar la excepción a ADR-0005** para los 6 archivos que conservan rojo de A4 (rincón 6), y que el aviso del hook por I001 en ellos es esperado.
- **Riesgo principal:** `email.py` y las ramas `except` de `dependencies.py:98-105` carecen de pruebas, de modo que el plan debe decidir cómo demostrar la ausencia de cambio de comportamiento (test de caracterización primero, RED/GREEN según aplique); W293 cambia bytes del correo aunque no su render (rincones 1 y 3).
- **Decisiones que el plan debe tomar explícitamente:** cómo partir textos de usuario sin alterarlos (rincón 2), `save_service` (rincón 5), `dependencies.py:108` con `TokenData.email`, que no se arregla con la anotación de la l.93, y si B904 usa `from err` o `from None` (precedente: `) from e`, `app/core/storage.py:138,210`).
- **Orden con A4 (hoy por la tarde):** ambos ítems tocan `dependencies.py`, `user_service.py`, `database.py` y `email.py`; las líneas que A4 cite se desplazarán, y su verificación debe medirse después de mezclar BE-33.

## Adenda — decisiones de David antes de planear (6 nov 2026, 09:41, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir.

1. **Veredicto aceptado: parcial (44 ruff + 5 mypy).** Planear con esos conteos; la fila BE-33 del backlog (45) se
   corrige en el cierre del día con esta verificación como fuente. Resultado medible al cerrar: ruff 53 → 9, mypy 10 → 5.
2. **Excepción a ADR-0005 declarada en el plan** para los seis archivos que conservan rojo de A4 (`dependencies.py`,
   `email.py`, `database.py`, `user_repository.py`, `schemas/audit.py`, `user_service.py`): conjuntos exactos por
   archivo (regla y línea) medidos antes y después de cada fase, forma del plan de BE-02 (decisión D2). El aviso del
   hook por I001 en esos archivos es esperado y no se corrige a mano. Los totales de I001 (9) y `str | None` (5) no
   cambian.
3. **Ramas sin test de `dependencies.py:98-105` (B904 l.99 y l.105): tests primero.** Dos tests HTTP nuevos contra una
   ruta protegida, token vencido → 401 y token inválido → 401, con estructura del JSON y cabecera `WWW-Authenticate`
   (sin afirmar sobre el texto), en RED antes de tocar las líneas. Las dos B904 de `user_service.py:126,130` ya tienen
   test (`tests/test_user_service.py:254,264`).
4. **`email.py` (rincón 1 y 3): test de caracterización de estructura, no de bytes.** Antes de tocar el f-string: un
   test que ejercite `send_verification_email` real con el cliente de correo doblado (`autospec`), afirme que se llamó
   con argumentos (`assert_called_once_with` o equivalente sobre destinatario y asunto) y que el cuerpo contiene el
   `verification_link`. La igualdad exacta del HTML no se exige (W293 cambia bytes por diseño). Es una fase propia o
   comparte fase con `database.py`.
5. **Textos de usuario (rincón 2): partir con concatenación implícita de literales**, nunca con `\n` ni cambiando una
   letra; el auditor compara la cadena resultante con la original (mismo valor en tiempo de ejecución), no el diff.
   Aplica a `user_access_policy.py:37,74,106` y `user_service.py:217`.
6. **B904: `raise … from err`** en los cuatro sitios, por consistencia con `app/core/storage.py:138,210` y porque
   conserva la causa para logging (A6). `from None` no.
7. **`save_service` (mypy :83): `scalar_one()`**, como `create_service` (l.25). No se ensancha la firma a `| None`
   (movería el error a `update_package_details`, fuera del mapa). Justificación y trade-off en
   `docs/aprendizaje/fichas/BE-33.md`.
8. **`TokenData.email` pasa a `str`** (`app/schemas/token.py:21`, hoy `str | None = None`): `TokenData` se usa solo en
   `dependencies.py:97`, con un `email` que ya pasó el `if email is None`. Cierra `dependencies.py:108` sin tocar el
   contrato HTTP. Las tres anotaciones `email: str = payload.get(...)` / `scope: str = …` se corrigen a `str | None`
   con el estrechamiento que la línea siguiente ya hace.
9. **Colaterales (rincón 10), regla del 4 nov (adenda de BE-15):** lo que esté en una línea que el plan ya reescribe se
   corrige aquí, declarado: docstrings `is_active` → `is_available` en `service_repository.py:28,38` (líneas con D415);
   `usuario` → `user` en `dependencies.py:108` (línea del mypy). Lo que no esté en línea tocada va al backlog en el
   cierre: español en `email.py:28` y `database.py:12` (nota en P2); `alembic/versions` no se toca (rincón 8).
10. **Rincón 9 es de BE-32, no de aquí.** Decisión tomada hoy para BE-32: opción (b) del residual 7 (`tests/` entra en
    `mypy.files`) y, para los 4 errores que dependen de A4 (`tests/test_user_service.py:103,197,274,292`), **el orden
    se mantiene** (BE-32 antes de A4): BE-32 los declara como conjunto de A4 en su excepción a ADR-0005 y la verificación
    de A4, medida tras mezclar BE-33 y BE-32, los cuenta. Se escribe en la adenda de `docs/deuda/BE-32/verificacion.md`
    cuando exista.
11. **Fases:** diez archivos, tope de cinco y un dominio por fase. Orden sugerido por riesgo, no vinculante para el
    planificador: A repositorios + schemas (docstrings, `:83`, `TokenData`); B `dependencies.py` + `user_service.py` +
    `user_access_policy.py` (tests de 3 primero, B904, mypy, textos de 5); C `email.py` + `database.py` (test de 4
    primero). Cada fase mide los conjuntos de la decisión 2.

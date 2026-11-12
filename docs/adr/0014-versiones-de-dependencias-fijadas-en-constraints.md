# ADR-0014 — Versiones de dependencias fijadas: `constraints.txt` con la versión exacta de todo lo instalado

- **Estado:** aceptado (David, 11 nov 2026)
- **Propuesta:** sesión Mentor (11 nov 2026), a partir del fallo del CI de PR #91
- **Ubicación en el repo:** `docs/adr/0014-versiones-de-dependencias-fijadas-en-constraints.md`
- **Origen:** backlog BE-46; bitácora `2026-11-11`; PR #92 (`3ee7213`, `dc9e1a9`; merge `6d649df`). Relación: ADR-0004 (una
  sola versión de Python), ADR-0001 (determinismo por herramientas), ADR-0005 (superado el mismo día: CI sin `--soft`).

## Contexto

`pyproject.toml` declara las dependencias de ejecución sin versión (`"fastapi"`, `"sqlalchemy"`, `"pyjwt"`…) y las de prueba
y desarrollo con un mínimo (`"pytest>=8.4.1"`). El CI (`pip install -e .[test,dev]`) y la imagen (`Dockerfile`,
`pip install -e .[test]`) instalaban, en una máquina limpia, lo más reciente de cada librería ese día. El venv de
desarrollo conserva lo que se instaló al crearlo.

El 11 nov, el primer ítem mezclado bajo el CI estricto (BE-39) pasó en local con 622 tests y cayó en el CI de PR #91 con un
solo fallo: `tests/test_route_guards.py:122`, `unexpected route type: _IncludedRouter(...)`. El venv tiene FastAPI 0.135.1,
cuyo `fastapi/routing.py` no contiene `_IncludedRouter`; el CI había instalado una versión posterior en la que
`app.routes` ya no es una lista plana de rutas. Las dos compuertas medían programas distintos, y la imagen desplegada se
construía con versiones que nadie había probado en local.

## Decisión

1. **`constraints.txt`, en la raíz, lleva la versión exacta (`nombre==versión`) de toda distribución instalada**, directa o
   transitiva. Se genera desde el venv de desarrollo con `pip freeze --exclude-editable`.
2. **`pyproject.toml` no cambia de papel:** declara qué necesita el proyecto; `constraints.txt` dice qué versión exacta.
3. **Toda instalación automatizada usa `-c constraints.txt`:** el CI (`.azure-pipelines/ci-pipeline.yml`) y la imagen
   (`Dockerfile`). Local, CI e imagen instalan lo mismo.
4. **Cambiar una versión es un cambio deliberado:** se actualiza el venv, se regenera el archivo, se corre la compuerta
   y va en el mismo PR. Una librería nueva entra en `pyproject.toml` y en `constraints.txt` a la vez.
5. **Lo que solo existe en Linux se fija a mano** con un comentario que lo diga, tomando la versión del log del CI
   (hoy solo `uvloop`, que `uvicorn[standard]` instala fuera de Windows). Al regenerar, esas líneas se conservan.

## Consecuencias

- Un fallo del CI que no se reproduce en local deja de poder deberse a la versión de una librería.
- Las actualizaciones, incluidas las de seguridad, ya no llegan solas: hay que ir a buscarlas. Para un MVP con fecha de
  entrega es el intercambio correcto; revisarlas es trabajo con fila cuando se decida.
- Subir FastAPI por encima de 0.135.1 hará caer el test de inventario de rutas a propósito
  (`tests/test_route_guards.py`, su `assert isinstance(route, Route)`); adaptarlo es parte de ese cambio.
- Límites declarados: (a) la versión de parche de Python no queda fijada por este archivo (3.14.3 en el venv, 3.14.10 en
  el CI; ADR-0004 fija solo 3.14); (b) las herramientas que pip usa para construir el paquete en modo editable se
  instalan aparte y no pasan por las restricciones; (c) el archivo se genera en Windows, así que una dependencia nueva
  exclusiva de Linux solo se ve en el log del CI.
- El archivo contiene `colorama`, que solo Windows instala: una restricción no obliga a instalar.

## Alternativas consideradas

1. **Fijar solo FastAPI y Starlette** (propuesta inicial del Mentor, para desbloquear el PR). Descartada por David: deja
   viva la misma causa en las demás librerías; "¿para qué esperarnos a que falle y nos vuelva a bloquear?".
2. **`==` en `pyproject.toml`.** Descartada: fija solo las dependencias directas; Starlette, pydantic-core, anyio y el
   resto de transitivas seguirían flotando.
3. **Un gestor con archivo de bloqueo multiplataforma** (uv, Poetry, pip-tools). Resuelve el límite (c) y añade hashes,
   pero introduce una herramienta nueva en local, en el CI y en la imagen. Se reconsidera si el archivo generado a mano
   da problemas.
4. **Adaptar el test a la versión nueva y seguir sin fijar.** Descartada: arregla el síntoma de hoy y deja que mañana
   cambie otra librería.

## Evidencia

- CI de PR #91 antes de fijar (11 nov): cinco pasos en verde y `pytest + cobertura` en rojo, un fallo, el citado arriba.
- `constraints.txt` (`dc9e1a9`): 77 versiones; comparado por la sesión Mentor con `venv/Lib/site-packages/*.dist-info`:
  0 versiones distintas; fuera del archivo solo el propio proyecto y `pip`; en el archivo y no en el venv, solo `uvloop`.
- CI de PR #92 sobre `3ee7213` (línea `Successfully installed`, pegada por David): 76 distribuciones, 0 con versión
  distinta de la del archivo, `fastapi-0.135.1`, `starlette-1.3.1`; la única sin restricción, `uvloop-0.23.0`, fijada en
  `dc9e1a9`. `579 passed · 96.29 %`, `Compuerta superada.`
- CI de PR #91 después de fijar (mismo test que había caído): `622 passed`, 96,47 %, `Compuerta superada.` (revisado por
  David).
- Limpieza del venv: `python-jose`, `ecdsa`, `rsa`, `pyasn1` y `six` desinstalados (ningún import ni requisito en el
  proyecto; el CI no los instalaba); compuerta local después, según David: `579 passed`, `Compuerta superada.`

# Handoff SEC1 · Fase A

Commit: `9ce0379` `fix(cors): allow only configured origins and stop sending credentials`

## Archivos tocados
`app/main.py`, `tests/test_main.py`, `.env.example`.

```
 .env.example       |   6 +++
 app/main.py        |  41 +++++++++++++++++--
 tests/test_main.py | 115 ++++++++++++++++++++++++++++++++++++++++++++++++++---
 3 files changed, 154 insertions(+), 8 deletions(-)
```

## Evidencia
RED: `tests/test_main.py` fallaba en colección con `ImportError: cannot import name 'CORS_ORIGINS' from 'app.main'`
(los tests 1-6 y, por arrastre, todo el módulo). No se midió el RED individual de 7-10 contra el comportamiento viejo
(el ImportError lo impedía); GREEN: `17 passed` en `tests/test_main.py`.

Línea base antes (ritual de arranque): 317 passed, 92.68 %, ruff 98, mypy 44, import-linter 4 kept.

Compuerta tras la fase (`venv/Scripts/python.exe scripts/check.py`):
```
333 passed, 1 warning in 12.41s
TOTAL 927 52 136 25 92.76%
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura
Compuerta NO superada: ruff format --check, ruff check, mypy
```
- ruff check total: Found 97 errors (antes 98; baja el E501 de `tests/test_main.py`). mypy: Found 44 errors, ninguna línea de `app/main.py`.
- `ruff check` y `ruff format --check` sobre los dos archivos tocados: limpios. import-linter: 4 kept, 0 broken.
- `ruff format --check` global falla SOLO por `docs/deuda/SEC1/plan.md:149` (ruff formatea los bloques de código del markdown; el plan
  está sin trackear y no es de esta fase). Ya fallaba antes de tocar nada por el mismo archivo; no se tocó.
- Greps del plan: `allow_origins=["*"]` vacío; `allow_credentials=True` vacío; `CORS_ORIGINS` en `.env.example` 1 línea;
  `load_dotenv` en `app/main.py` vacío; `set_cookie|Cookie` vacío; `azurestaticapps` y `pydantic_settings` vacíos.
- Arranque con comodín (`CORS_ORIGINS="*" python -c "import app.main"`):
  `app/main.py line 189, in parse_cors_origins: raise ValueError("CORS_ORIGINS must list explicit origins; wildcards are not allowed")` -> `ValueError`.

## Desviaciones menores
- Comentarios (orientativos según el plan) reformulados para que los greps del plan den vacío y que la línea de `allow_methods`
  quepa en 100 columnas: ya no contienen las palabras `load_dotenv` ni `cookies`.
- `tests/test_main.py` añade una constante `ROOT_BODY` reutilizada por `test_read_root` y el test 7 (mismo contenido).
- Trailer del commit: `Co-Authored-By: Claude Sonnet 5.5` (la atribución vigente de la sesión) en lugar de `Claude Fable 5.1` del plan.
- `.env` local: no se leyó; si definiera `CORS_ORIGINS` vacío, `CORS_ORIGINS[0]` fallaría en los tests 7 y 9.

## Residuales / dudas
- `docs/deuda/SEC1/plan.md` y `progress.json` estaban sin trackear al arrancar; `docs/bitacora/2026-11-02.md` modificado (no mío). `plan.md`
  queda sin commitear por mí.
- Residuales del plan intactos (allow_methods/headers, docker-compose, manual de despliegue, `withCredentials` del Flutter web, validación de forma).

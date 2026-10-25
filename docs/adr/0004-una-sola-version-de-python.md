# ADR-0004 — Una sola versión de Python (3.14) en desarrollo, CI y producción

- **Estado:** aceptado
- **Propuesta:** Claude (24 oct 2026) · **Aprobada:** David (25 oct 2026)
- **Fecha de la decisión:** 2026-10-25 · **Fecha de registro:** 2026-10-25
- **Ubicación en el repo:** `docs/adr/0004-una-sola-version-de-python.md`

## Decisión (resumen)

Se adopta Python 3.14 como versión estándar del backend de Ecotur-ASOPRADO en todos los entornos.

La versión se declara en cinco sitios de cuatro archivos. Cambiaron: `Dockerfile`
(`FROM python:3.14-slim`), `.python-version` (`3.14`) y `pyproject.toml` (`requires-python >= 3.14`,
`ruff target-version = py314`, `mypy python_version = 3.14`). Ya estaban en 3.14 y se conservan:
`.azure-pipelines/ci-pipeline.yml` (variable `pythonVersion`) y el venv local (`venv/pyvenv.cfg`: 3.14.3).

## Contexto

- Las versiones 3.11 (`Dockerfile`, `.python-version`) y 3.14 (venv, CI) convivían de forma asimétrica:
  el desarrollo local del backend llevaba realizándose bajo Python 3.14 desde hacía un tiempo no
  determinado, mientras que la versión declarada en el `Dockerfile` que se usa para el despliegue en Azure
  había sido Python 3.11 desde la versión 0 del proyecto.
- Como consecuencia, la compuerta de calidad (pipeline de CI en Azure) validaba un Python distinto al de
  producción.
- Inicialmente se había escogido 3.11 porque David la consideró "la opción LTS por excelencia". Sin
  embargo, según la guía oficial de desarrollo de Python
  ([Status of Python versions](https://devguide.python.org/versions/)), Python no tiene versiones LTS:
  cada versión recibe unos cinco años de soporte (dos de corrección de errores y después solo parches de
  seguridad). La 3.11, lanzada en octubre de 2022, termina su vida útil en octubre de 2027 y hoy solo
  recibe parches de seguridad. La 3.14, lanzada en octubre de 2025, tiene vida útil hasta octubre de 2030
  y recibirá parches de seguridad tres años más que la 3.11.
- Por lo anterior se decidió eliminar la asimetría adoptando 3.14 como estándar: ya se usaba en local y en
  CI, y el ajuste solo tocaba tres archivos.

## Alternativas

- **3.11 en todo.** Descartada: obligaba a reinstalar el entorno local y el CI; producción era el único
  entorno rezagado y las dependencias ya instalan en 3.14 tanto en Windows como en Linux.

## Consecuencias

- La primera construcción de la imagen con `python:3.14-slim` ocurre en el pipeline CD del entorno
  `develop`. Si falla, se revierte únicamente el `Dockerfile` y se abre un ítem en el backlog; cualquier
  decisión nueva se registra en un ADR posterior.
- `requires-python = ">=3.14"` garantiza que el proyecto solo pueda instalarse sobre la versión correcta:
  `pip` falla de forma ruidosa e inmediata si alguien intenta construirlo con un intérprete distinto
  (por ejemplo, un `Dockerfile` que volviera a declarar 3.11). Es un guardarraíl, no un estorbo.
- Quien se incorpore al proyecto debe instalar 3.14; `.python-version` permite que herramientas como
  `uv` o `pyenv` lo seleccionen automáticamente.

## Evidencia

- `python scripts/check.py` imprime "Python 3.14.3"; 116 tests en verde bajo 3.14.
- Fuente de fechas de soporte: https://devguide.python.org/versions/ (consultada el 25 oct 2026).

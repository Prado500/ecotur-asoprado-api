# Handoff — BE-50 · Fase A (ADR-0022)

- **Commit de la fase:** `e530980` — `docs(adr): add ADR-0022, a verified-email mark decides the link` (mensaje exacto
  del plan, fase A).
- **Rama:** `item/be-50`. **Base develop:** `c478e38` (`git fetch origin` correcto; `origin/develop` y
  `merge-base HEAD origin/develop` = `c478e38`, igual a `verificacion.md`).
- **Compuerta:** invocada según E1 como `./venv/Scripts/python.exe scripts/check.py --soft imports`.

## Archivos tocados
- `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md` (nuevo): texto del Anexo A del plan (líneas
  333-420 de `plan.md`), extraído con `sed` sin reescribirlo. Única diferencia con el Anexo, comprobada con `diff`:
  `<FECHA DE APROBACIÓN>` → `19 nov 2026` (E0.1).

## Diff (`git show --stat e530980`)
```
 ...-marca-de-correo-verificado-decide-el-enlace.md | 88 ++++++++++++++++++++++
 1 file changed, 88 insertions(+)
```

## Comprobaciones mecánicas del plan
- Antes: `ls docs/adr/0022-*` → `No such file or directory`.
- Después: `ls docs/adr/0022-*` → `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md` (1 archivo).
- `grep -c "<FECHA" docs/adr/0022-*.md` → `0`.

## Compuerta de arranque (antes de tocar nada)
Exit 0. `71 files already formatted` · `All checks passed!` · `Success: no issues found in 66 source files` ·
import-linter `ImportError: DLL load failed while importing _rustgrimp: An Application Control policy has blocked this
file.` · docs coherente · `797 passed, 25 warnings` · `Total coverage: 98.69%`. Igual a la línea base de
`verificacion.md` salvo import-linter, que es el caso que E1 tolera.

## Compuerta de salida (literal)
Código de salida: `0`.

Paso import-linter:
```
=== import-linter ===
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from importlinter.cli import lint_imports_command; lint_imports_command()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\importlinter\__init__.py", line 5, in <module>
    from .domain.contract import Contract, ContractCheck  # noqa
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\importlinter\domain\contract.py", line 4, in <module>
    from grimp import ImportGraph
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\grimp\__init__.py", line 3, in <module>
    from .application.graph import DetailedImport, Import, ImportGraph
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\grimp\application\graph.py", line 6, in <module>
    from grimp import _rustgrimp as rust  # type: ignore[attr-defined]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ImportError: DLL load failed while importing _rustgrimp: An Application Control policy has blocked this file.
--- import-linter: FALLA (exit 1) en 0.9s
```

RESUMEN:
```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✘ import-linter (soft)
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada; tolerados en rojo: import-linter
```

Otras líneas del log:
```
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).
TOTAL                                       1066     10    154      6  98.69%
Required test coverage of 92.0% reached. Total coverage: 98.69%
797 passed, 25 warnings in 32.55s
```

**Criterio E1.2:** (a) exit 0 ✔; (b) última línea `Compuerta superada; tolerados en rojo: import-linter` ✔; (c) el
único `✘` es `import-linter (soft)` ✔; (d) la salida del paso contiene `DLL load failed while importing _rustgrimp` ✔.
E1.3 no aplica: el paso no llegó a evaluar contratos (no hay línea `Contracts:`).

**Ratchet:** pytest 797 passed / 0 failed (= línea base); cobertura 98,69 % (= línea base); ruff 0 (= 0); mypy 0 en
66 archivos (= 0); contratos no medibles en esta máquina (E1.5: los mide la sesión Mentor sobre
`git archive e530980`). Ruff y mypy sobre archivos tocados: no aplican (solo un `.md` en `docs/adr`, fuera de
`check_docs`).

## Residuales
- Ninguno nuevo. La skill `test-sanitizer` no aplica: la fase no tiene tests.

## Dudas / pendiente para la fase B
- E1.5: la fase B no empieza hasta que la sesión Mentor anote en la bitácora la salida de import-linter sobre
  `git archive e530980` en Linux.
- Paso de David antes de B (plan, fase B): `alembic current` → `b51f3c9e2a64 (head)` y `alembic check` →
  `No new upgrade operations detected.`, con salida literal en la bitácora.

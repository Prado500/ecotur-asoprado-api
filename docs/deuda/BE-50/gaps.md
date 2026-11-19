# Gaps — BE-50

## Auditoría Fase A — 2026-11-19
**Veredicto Fase A: PASS (0 bloqueantes, 1 opcionales).**
[OPCIONAL] — Fase A — Los contratos de import-linter siguen sin medirse para `e530980`: en esta máquina el paso no llega a evaluarlos (DLL `_rustgrimp` bloqueada). E1.5 manda que la sesión Mentor los mida sobre `git archive e530980` en Linux y lo anote en la bitácora antes de empezar B; en el repo todavía no hay evidencia de esa anotación. El riesgo es nulo porque la fase no toca código, pero es una condición previa de B, no algo que A deba corregir — evidencia: paso import-linter abajo (sin línea `Contracts:`); plan.md, E1.5; handoff-Fase_A.md:92-93.

### Evidencia

**Árbol y commits.** `git status --short` → vacío. `git log --oneline -3`: `787ee5c docs(progress): record BE-50 Fase_A completion`, `e530980 docs(adr): add ADR-0022, a verified-email mark decides the link`, `271abf5 docs(item-be50): E1, gate with --soft imports on a blocked machine`.

**Commit de la fase (`e530980`).** `git show --stat e530980` → 1 archivo, `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`, 88 inserciones. Comparé con `diff` el mensaje (`git log -1 --format=%B`) contra plan.md:118-131 (sin la sangría): idéntico salvo la línea vacía final que añade git. El alcance de `git diff --name-only 271abf5 e530980` es solo el ADR.

**Cambios exactos.** Comparé con `diff` plan.md:333-420 (Anexo A) contra el ADR. La única diferencia es la línea 3: `<FECHA DE APROBACIÓN>` pasa a ser `19 nov 2026`, como manda E0.1. `ls docs/adr/0022-*` → 1 archivo; `grep -c "<FECHA" docs/adr/0022-*.md` → `0`. No hay índice de ADR que actualizar: el precedente de ADR-0021 (`e3cdc4b`) tampoco tocó ninguno.

**Segundo commit (`787ee5c`).** Es conforme. El protocolo de `fase-ejecutor` (`.claude/agents/fase-ejecutor.md:62-63`) manda commitear aparte `progress.json` y `handoff-<fase>.md` con `docs(progress): record <ID> <fase> completion`, y así lo hicieron todas las fases anteriores (`04a5a71`, `9cdc9d1` de BE-38; `d368a5d` de BE-37). El mensaje único del plan es el del commit de la fase, que es `e530980`. `787ee5c` toca solo `docs/deuda/BE-50/` y ningún archivo de otra fase.

**progress.json.** JSON válido. `Fase_A`: `completed`, `commit: "e530980"` (un hash real; `git show --stat` lo confirma). `current_target` pasó de `Fase_A` a `Fase_B`. `last_handoff` está presente. `edit_rules` y `allowed_statuses` no cambiaron (`git show 787ee5c -- docs/deuda/BE-50/progress.json`).

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py --soft imports`, E1.1). Código de salida `0`.

Paso import-linter (literal):
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
--- import-linter: FALLA (exit 1) en 0.7s
```

RESUMEN (literal):
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

Otras líneas: `71 files already formatted` · `All checks passed!` · `Success: no issues found in 66 source files` · `Documentación coherente (...)` · `TOTAL 1066 10 154 6 98.69%` · `Required test coverage of 92.0% reached. Total coverage: 98.69%` · `797 passed, 25 warnings in 23.71s`.

**E1.2:** (a) exit 0 ✔; (b) última línea `Compuerta superada; tolerados en rojo: import-linter` ✔; (c) el único `✘` es `import-linter (soft)` ✔; (d) contiene `DLL load failed while importing _rustgrimp` ✔. **E1.3:** no aplica, porque no hay línea `Contracts:`.

**Ratchet frente a la línea base** (verificacion.md:162-163, 182: 797 passed · 98,69 % · ruff 0 · mypy 0 en 66 · 4 kept): pytest 797/0 failed, igual; cobertura 98,69 %, igual; ruff 0, igual; mypy 0 en 66, igual; contratos no medibles aquí (tolerado por E1, ver el opcional). Ruff y mypy sobre los archivos tocados no aplican: la fase solo toca un `.md`. Coincide con lo que pegó el ejecutor (handoff-Fase_A.md:31-86).

**Criterio de aceptación de A:** el archivo existe ✔; `<FECHA` = 0 ✔; la compuerta pasa según E1 con 797 passed y sin cambios en código ✔. La fase no lleva tests (lo dice el plan). No es la última fase, así que la Verificación final no se ejecuta. No hay código nuevo, así que las comprobaciones de AGENTS §3-§5 no aplican.

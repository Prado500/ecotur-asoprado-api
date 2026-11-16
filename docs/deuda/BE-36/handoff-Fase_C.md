# Handoff — BE-36 · Fase C (H7: un superadmin reactiva a un par ya activo → 200)

- Commit de la fase: `202ec51` — `test(access-policy): cover a superadmin reactivating an active peer` (mensaje exacto
  del plan; bloque "Commit" de la fase C, plan l. 485-502, sin la sangría de dos espacios, comparado con `diff` contra
  `git log -1 --format=%B 202ec51` sin la línea en blanco final → idéntico; trailer `Co-Authored-By` incluido).
- Rama: `item/be-36`, sobre `ad48494` (fase C escrita por el planificador y aprobada con E2).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E1.1 (la fase), E2.1 (aprobada sin correcciones), E2.2 (sin RED de código; el RED es N7 en una
  copia), E2.3 (H7 sin aserción sobre la auditoría, BE-38), E2.4 / E0.3 (`AGENTS.md` no se tocó). Nada en `app/`.

## Ritual de arranque

- `git status --short`: limpio. HEAD `ad48494`. `current_target` = `Fase_C`. `gaps.md`: fases A y B PASS, sin
  bloqueantes (el opcional de B es lo que resuelve esta fase).
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `09f529b`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `09f529b`; `Base develop` de
  `verificacion.md` = `09f529b`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual al cierre de la fase B:
  `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1039 15 152 13 97.65%` · `725 passed, 8 warnings in 23.80s`.

## Archivos tocados (el único de la fase)

`git show --stat --format= 202ec51`:

```
 tests/test_user_access_policy.py | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)
```

- `tests/test_user_access_policy.py`: H7 (`test_be36_superadmin_reactivating_active_peer_returns_200`) insertado con un
  script tras la l.1193 (`    assert audits == []`, última línea de `test_be36_admin_reactivating_peer_admin_returns_403`),
  con dos líneas en blanco antes y dos después, antes de `# ==========================================` de la sección C.
  El script comprobó las anclas (l.1193, l.1194-1195 en blanco, l.1196 la cabecera) antes de escribir.
- Texto literal: el bloque del plan (l. 411-436, sin la sangría) comparado con `diff` contra el texto insertado → idéntico;
  presencia como subcadena en el archivo → `True`; columna máxima 84. Sin imports nuevos. Sin CR en el archivo.
- `git diff --name-only ad48494 202ec51` → solo `tests/test_user_access_policy.py`; `git diff --stat 9c77da2 HEAD -- app`
  → vacío.
- Por archivo: `ruff format --check` → `1 file already formatted`; `ruff check` → `All checks passed!`; `mypy` →
  `Success: no issues found in 1 source file`.

## RED (E2.2): mutante N7 en una copia completa del commit de la fase

Copia en el scratchpad con `git archive 202ec51 | tar -x` (árbol completo, con `docs/` y `.claude/`); nunca se mutó el
repo. N7 = `            and target.is_active is False` añadido tras `            and update_dict["is_active"] is True`
en `app/services/user_access_policy.py` de la copia (`diff` del mutado contra el original: `80a81 >             and
target.is_active is False`). Suite completa de la copia con el intérprete del `venv` del repo
(`python -m pytest -q -p no:cacheprovider -rf tests`, desde la raíz de la copia):

```
== N7, suite completa de la copia (202ec51) con H7
FAILED tests/test_user_access_policy.py::test_be36_superadmin_reactivating_active_peer_returns_200
1 failed, 725 passed, 8 warnings in 22.58s
```

Restaurada (archivo original de la copia; `git diff --no-index` contra el `app/services/user_access_policy.py` del repo →
sin diferencias):

```
== restaurada, suite completa de la copia (202ec51)
726 passed, 8 warnings in 21.90s
```

N7 muerto, H7 único fallo; coincide con la medición del planificador (`1 failed, 725 passed`).

## GREEN

`./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be36 -q -p no:cacheprovider`:

```
19 passed, 83 deselected in 1.65s
```

## Compuerta (salida literal, comando 13, sobre el árbol de `202ec51`; `git status` limpio)

`./venv/Scripts/python.exe scripts/check.py` → exit 0.

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1039     15    152     13  97.65%
726 passed, 8 warnings in 22.08s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

`app/services/user_access_policy.py` no aparece en la tabla de líneas sin cubrir (100 %, "30 files skipped due to
complete coverage"). Ratchet: 725 → 726 passed; cobertura 97,65 % = línea base; ruff 0; mypy 0 en 63; 4 kept = línea
base. (La compuerta se corrió también antes del commit, con el mismo árbol: idénticas cifras, `726 passed ... in 22.00s`.)

## Verificación final (comandos 1-13, rama tras la fase C)

```
# 1
app/services/user_service.py:363:        target_user.is_active = False
# 2
app/repositories/user_repository.py:63:        user.is_active = True
# 3
exit=1
# 4
app/services/user_access_policy.py:75:        is_peer_reactivation = (
app/services/user_access_policy.py:85:            and not is_peer_reactivation
# 5a
app/services/user_access_policy.py:79:            and set(update_dict) == {"is_active"}
# 5b
app/services/user_access_policy.py:80:            and update_dict["is_active"] is True
# 6
app/api/routers/user.py:234:    return await user_service.recover_user_account(
app/services/user_access_policy.py:113:    def assert_can_recover(self, actor: User, target: User) -> None:
app/services/user_service.py:332:    async def recover_user_account(self, target_cedula: str, current_user: User) -> dict:
app/services/user_service.py:359:        self.user_access_policy.assert_can_recover(current_user, target_user)
# 7
app/repositories/user_repository.py:83:        user.deleted_at = datetime.now(UTC)
app/services/user_service.py:362:        target_user.deleted_at = None
# 8
27
# 9a
app/services/user_access_policy.py:16:    outside the recycle bin, sending is_active true and nothing else (ADR-0018).
app/services/user_access_policy.py:57:        is_active true and nothing else (ADR-0018).
app/services/user_access_policy.py:74:        # ADR-0018: a superadmin may reactivate a peer outside the recycle bin, nothing else.
app/services/user_service.py:262:        else (ADR-0018).
app/services/user_service.py:339:        is_active true (ADR-0018).
# 9b
exit=1
# 9c
docs/adr/0018-un-superadmin-reactiva-a-otro.md
# 9d
7
# 10
app/schemas/user.py:130:    is_active: bool = False
# 11
(fin 11)
# 12a
tests/test_user_access_policy.py:13
# 12b
19 passed, 83 deselected in 1.40s
```

Comando 13: la compuerta de arriba. Todos dan lo esperado por el plan tras E1 (8 → 27; 12 → `:13` y `19 passed`;
13 → `726 passed`; 11 vacío).

## Checklist `test-sanitizer` (solo los "Ecotur Enterprise Test Standards")

1. Mocks con `spec`: H7 no usa mocks. 2. Fábricas: `persist_user` (confirma antes de la petición) y
`make_auth_headers`; ningún usuario ni token a mano; `refresh` tras la petición (ADR-0011). 3. Inglés en nombre,
variables y docstring. 4. Contrato: claves `cedula`, `role`, `is_active` del cuerpo. 5. ABAC: el borde que faltaba
(objetivo activo) queda cubierto. Sin aserciones sobre texto en español. Ninguna prueba existente reescrita.

## Desviaciones y residuales

- Ninguna desviación del dictado. Todas las cifras cuadran con las del planificador.
- La copia del mutante es `git archive` del commit de la fase (`202ec51`), como dicta el plan, por eso N7 se corrió
  después del commit. Queda además en el scratchpad una copia anterior (`copyC`, `ad48494` + H7) sin usar para ninguna
  medición: el permiso de `rm -rf` está denegado y no se borró.
- H7 no afirma nada sobre la auditoría (E2.3; la fila del no-op es BE-38).
- `progress.json`: `current_target` → `null` (no quedan fases; misma convención que tras la fase B).
- Pendiente para David (E2.4): la viñeta de AGENTS §3 después de la auditoría de la fase C y antes de `/pr`.

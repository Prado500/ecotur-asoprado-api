# Handoff — BE-02 Fase_A: guarda de auto-edición de rol, docstrings y tests

**Commit de la fase:** `f55313c` (`fix(access-policy): block self role changes for superadmins too`), mensaje letra a
letra del plan con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:** `/auditar BE-02`.

## Archivos tocados

`git show --stat --format= f55313c`:

```text
 app/services/user_access_policy.py |  17 ++--
 app/services/user_service.py       |   6 +-
 tests/test_user_access_policy.py   | 173 +++++++++++++++++++++++++++++++++++++
 3 files changed, 188 insertions(+), 8 deletions(-)
```

## Ritual de arranque

- Árbol limpio. `current_target` = `Fase_A`.
- `git fetch origin` correcto. `origin/develop` = `c6422ed`; `merge-base HEAD origin/develop` = `c6422ed`; `Base develop`
  de `verificacion.md` = `c6422ed`.
- Compuerta antes de tocar nada, igual a la línea base: `396 passed`, 94.81 %, ruff `Found 54 errors.`, mypy `Found 10
  errors in 5 files`, `Contracts: 4 kept, 0 broken.`, formato `53 files already formatted`, exit 1.

## RED

Tests escritos sin tocar `app/`. Comando: `./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -q -k be02
--no-cov --tb=no -p no:warnings -rfE`.

```text
F..F..F..FF.FFFFF..                                                      [100%]
=========================== short test summary info ===========================
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be02_nobody_can_send_own_role[superadmin-superadmin]
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be02_nobody_can_send_own_role[admin-superadmin]
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be02_nobody_can_send_own_role[tourist-superadmin]
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be02_superadmin_self_update_with_role_none_is_rejected
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be02_self_role_guard_identifies_the_actor_by_cedula
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_change_returns_403_without_mutation[tourist]
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_change_returns_403_without_mutation[admin]
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_noop_returns_403
FAILED tests/test_user_access_policy.py::test_be02_superadmin_self_role_with_profile_fields_mutates_nothing
FAILED tests/test_user_access_policy.py::test_be02_superadmin_keeps_powers_after_rejected_self_demotion
10 failed, 9 passed, 57 deselected in 0.44s
```

Los 10 rojos son exactamente los de la tabla del plan. En los ids parametrizados el orden es `[new_role-actor_role]`: los
tres primeros son el actor superadmin.

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, sobre el commit, exit 1)

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

```text
53 files already formatted
Found 53 errors.
Found 10 errors in 5 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        944     34    138     22  94.82%
Required test coverage of 92.0% reached. Total coverage: 94.82%
415 passed, 5 warnings in 17.31s
```

| Métrica | Línea base | Fase_A | Criterio |
|---|---|---|---|
| pytest | 396 passed | 415 passed | 415 passed |
| Cobertura | 94.81 % | 94.82 % | ≥ 94.81 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 54 | 53 | 53 |
| mypy total | 10 en 5 archivos | 10 en 5 archivos | 10 |

## Trinquete (decisión 2)

- `app/services/user_access_policy.py`: 8 errores (D205 ×5 en l.21, 78, 95, 110, 129; E501 ×3 en l.37, 74, 106). Son los
  9 de la línea base menos la D205 de l.40; los demás solo se desplazan por las líneas añadidas.
- `app/services/user_service.py`: ruff 6 (I001 l.1, E501 l.46, 217 y 337, B904 l.126 y 130), mypy 3 (l.124, 132, 133).
- `tests/test_user_access_policy.py`: `All checks passed!`.
- Comparé el conjunto completo regla + archivo + línea de ruff entre la compuerta de arranque y la final: la única
  diferencia es la de la política descrita arriba. La salida de mypy es idéntica.

## Verificación final del plan (sobre `f55313c`)

```text
### V1
exit=1
### V2
app/services/user_access_policy.py:57:        is_self_update = actor.cedula == target.cedula
app/services/user_access_policy.py:59:        if not is_self_update and self._ROLE_RANK[actor.role] <= self._ROLE_RANK[target.role]:
app/services/user_access_policy.py:64:        if "role" in update_dict and actor.role != UserRole.superadmin:
app/services/user_access_policy.py:69:        if is_self_update and "role" in update_dict:
### V3
app/services/user_service.py:279:            setattr(target_user, key, value)
### V4
tests/test_user_access_policy.py:175:            policy.assert_can_update(superadmin, superadmin, {"role": None})
tests/test_user_access_policy.py:187:        policy.assert_can_update(superadmin, superadmin, {"first_name": "Updated"})
### V5
tests/test_user_access_policy.py:10
...................                                                      [100%]
19 passed, 57 deselected in 0.33s
### V6
tests/test_user_access_policy.py:2
### V7
app/services/user_access_policy.py
app/services/user_service.py
tests/test_user_access_policy.py
12	5	app/services/user_access_policy.py
3	3	app/services/user_service.py
173	0	tests/test_user_access_policy.py
### V8
5	D205	missing-blank-line-after-summary
3	E501	line-too-long
Found 8 errors.
3	E501	line-too-long
2	B904	raise-without-from-inside-except
1	I001	unsorted-imports
Found 6 errors.
All checks passed!
Found 53 errors.
### V9
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\repositories\service_repository.py:83: error: Incompatible return value type (got "TouristService | None", expected "TouristService")  [return-value]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:132: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\services\user_service.py:133: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\api\dependencies.py:92: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:93: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
app\api\dependencies.py:108: error: Argument 1 to "get_non_deleted_user_by_email" of "UserRepository" has incompatible type "str | None"; expected "str"  [arg-type]
Found 10 errors in 5 files (checked 35 source files)
### V10
exit=1; ver bloque RESUMEN y conteos de arriba
```

Los diez pasos dan lo que el plan esperaba.

## Checklist `test-sanitizer`

Sin mocks nuevos; usuarios y cabeceras salen de `make_user`, `persist_user` y `make_auth_headers`; nombres e identificadores
en inglés; ninguna aserción sobre texto en español (`detail` solo se comprueba como clave y como `str`); `refresh` tras cada
petición sobre lo que el test ya tenía cargado (ADR-0011). No reescribí ningún test existente.

## Residuales

- Rojo heredado de la compuerta: ruff 53 y mypy 10 (BE-33 y A4). Sin tocar, según la decisión 2.
- Los del plan siguen vigentes: retirar `unfixable I001` al cerrar A4; BE-37 se mide sobre un tercero; BE-34 a BE-38 siguen
  abiertos; el frontend no se verificó contra otro builder de `PATCH`.
- El hook de edición salió con código 2 al editar la política (9, 9 y 8 errores en las tres ediciones sucesivas) y
  `user_service.py` (6), como anticipa la decisión 4. No corregí nada.

## Desviaciones y dudas

- Sin desviaciones de código ni de tests respecto al plan.
- `current_target` queda en `Auditoria`: el plan no tiene más fases y es el valor que usaron BE-15 y AF-05 tras su última fase.

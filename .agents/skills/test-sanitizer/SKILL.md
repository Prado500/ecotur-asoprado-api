---
name: test-sanitizer

description: Sanitiza las pruebas unitarias de Ecotur-ASOPRADO en paralelo a las refactorizaciones de código. Asegura resiliencia, corrección/no-introducción de anti-patrones, sintaxis moderna y especificaciones correctas de mocks.

---

# Ecotur-ASOPRADO Test Sanitizer

Esta skill garantiza que, al refactorizar el código backend, las pruebas unitarias correspondientes se actualicen pasivamente a una compuerta de calidad de grado comercial. Tambien garantiza que no exista código resultante de refactorizaciones / esfuerzos por saldar deuda técnica para el cual no existan sus pruebas unitarias correspondientes.  

## Cuándo usarla
- Al arreglar deuda técnica del backend y necesitar actualizar las pruebas unitarias afectadas.
- Al arreglar deuda técnica del backend y necesitar crear las pruebas unitarias correspondientes (en caso de no estar seguro de si tiene sentido o no introducir una nueva prueba unitaria, se debe usar context 7 para seguir las recomendaciones de las máximas fuentes de autoridad actualizadas en la materia al respecto).
- Cuando el usuario te pida generar, sanitizar o refactorizar pruebas para Ecotur-ASOPRADO.

## Flujo de Trabajo (Planificar y Ejecutar)

**REGLA ESTRICTA:** NO escribas el código final de las pruebas inmediatamente. Debes seguir un proceso de dos fases:

### Fase 1: Planificar y Validar (Obligatorio usar Context 7)
0. Si estas siguiendo un plan en formato .md que ya propone plan(es) de ataque para la implementación de la(s) prueba(s) asociada(s) al código introducido y/o que se va a introducir o a modificar, avisa al usuario y ve directo al paso 3. Si no estas siguiendo ningún plan en formato .md, o si el plan no indica que pruebas deben implementarse, ignora este paso y retoma desde el que le sigue, que es el paso 1.  
1. Identifica las pruebas existentes asociadas al código que acabas de refactorizar. De no existir pruebas unitarias asociadas, debes obligatoriamente evaluar que tan pertinente es crear pruebas unitarias para el código refactorizado, y deberás verificar o desmentir tus conclusiones acudiendo a fuentes de información de autoridad en la materia, que sean fiables, verificables y actualizadas (ej. context 7) para luego darme un informe. Luego de que el usuario autorice explicitamente la creación de la(s) prueba(s), ve al siguiente paso.
2. formula un plan de ataque para implementar y/o actualizarl las pruebas aplicando los "Estándares Enterprise" descritos abajo. Si estas siguiendo un plan, y en el ya se formula el plan e ataque, ve directamente al siguiente paso
3. **OBLIGATORIO:** Usa tu herramienta MCP Context 7 para buscar en la documentación oficial (ej. fixtures de `pytest`, `unittest.mock.MagicMock` con `spec=`, `TestClient` de FastAPI) y validar que la arquitectura de pruebas que propones (o que se propone en el plan en formato .md) es completa, idiomática y moderna.
4. Devuelve el plan validado y un resumen de la documentación oficial consultada. Detente y espera la aprobación del usuario.

### Fase 2: Ejecución
Una vez que el usuario apruebe el plan, ejecuta el código de las pruebas atómicamente, asegurando que pasen en verde.

## Ecotur Enterprise Test Standards (Reglas Innegociables)

Al planificar y escribir las pruebas, debes cumplir estrictamente estos estándares:

1. **Mocks Resilientes (Cero falsos positivos):** Nunca uses mocks ilimitados o genéricos. Todo mock de dependencias externas (como `AzureStorageClient`) DEBE usar explícitamente `spec=` o `autospec=True`. Si la firma del método real cambia en el futuro, la prueba debe fallar.
2. **Fixtures DRY:** Erradica la preparación de pruebas duplicada (ej. creación manual de usuarios, contraseñas o tokens repetida en múltiples pruebas). Extrae esta lógica a fixtures de fábrica centralizados en `conftest.py`.
3. **Erradicar Spanglish:** Los nombres de las funciones de prueba, las variables internas y las aserciones deben estar 100% en inglés (ej. `test_user_registration_success`, NUNCA `test_registro_usuario_exitoso`).
4. **Consistencia de Contratos de Datos:** Asegúrate de que las pruebas aserten contra las claves JSON correctas definidas por la nueva arquitectura (ej. esperar `{"detail": ...}` en lugar del defecto anterior `{"detalle": ...}`).
5. **Cobertura Robusta de ABAC:** Prueba explícitamente los casos límite (edge cases) vulnerables de la política de acceso. Por ejemplo, incluye aserciones que demuestren que un admin *no puede* escalar a superadmin, que el error 404 (existencia) salta antes que el 403 (permisos), o que un admin *no puede* hacer escalamiento por interpuesta persona de un turista a superadmin.
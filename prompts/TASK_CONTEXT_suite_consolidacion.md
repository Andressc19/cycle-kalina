---
project: ciclo_kalina_tercero
task_id: 2026-09-30-suite-consolidacion
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-30
---

# TASK_CONTEXT — Verificar la suite de la rama de consolidación y regenerar el Excel consolidado

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\integracion-base-29sep`
(rama `integracion/KSC_11_base_29sep`). Solo ejecutar y reportar: **no modificar ni crear
código, no hacer commits.** Ignora los demás `TASK_CONTEXT*.md`. Usa el python
`D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` con cwd en el worktree. Todas las
salidas van a `resultados/2026-09-30_consolidacion/` dentro del worktree (nunca `/tmp`).

Contexto: se fusionaron A+B (`TeqpVerificado`, `verificar_turbina`), `ui_campos.py`, los
barridos de Fases 1-3 y el catálogo de 4 niveles (`NO_CONVERGIO < INVIABLE < CORREGIBLE <
KALINA`; ya no existen `VALIDO_ADVERTENCIA` ni `DEGENERADO`). Ver
`docs/NOTAS_CONSOLIDACION_29sep.md`.

## Pasos

1. Suite principal:
   `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py`
   salida a `resultados/2026-09-30_consolidacion/pytest_suite.log`.
2. Compilación: `python -m py_compile app.py src/sensitivity.py src/ui_campos.py src/ui_helpers.py src/ui_inputs.py src/ui_barrido.py src/ui_backend.py src/ui_clasificacion.py`.
3. Regenerar el Excel consolidado: `python scripts/consolidar_excel_barridos.py`
   (lee `datos/primeros_barridos_e_iteraciones_kalina.xlsx`, escribe
   `datos/barridos_e_iteraciones_kalina_consolidado.xlsx`; no re-ejecuta el ciclo). Salida
   a `resultados/2026-09-30_consolidacion/consolidar.log`. Después, con openpyxl, listar
   las hojas resultantes con su número de filas y contar cuántas celdas de la columna de
   clasificación contienen `VALIDO_ADVERTENCIA` o `DEGENERADO` en todo el libro.
4. Grep (solo lectura) de `VALIDO_ADVERTENCIA` y `DEGENERADO` en `src/`, `tests/` y
   `scripts/*.py`; reportar cada coincidencia con archivo:línea.

## Reportar

- Pasados / fallados / omitidos de la suite. Para cada fallo: archivo, prueba, línea del
  error y si es uno de los 8 previos conocidos (2 de `test_restricciones_convenciones.py`
  por `src/ui_campos.py` inexistente — ahora debería existir; 6 de
  `test_verificacion_iapws_g4.py` por Cv/w) o uno nuevo.
- Resultado del paso 2, hojas del Excel y conteo del paso 3, coincidencias del paso 4.
- Si algo necesita arreglarse, repórtalo en `UNRESOLVED`; no lo arregles.

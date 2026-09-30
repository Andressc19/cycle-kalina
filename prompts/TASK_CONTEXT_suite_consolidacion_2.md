---
project: ciclo_kalina_tercero
task_id: 2026-09-30-suite-consolidacion-2
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-30
---

# TASK_CONTEXT — Re-verificar tras corregir el test de Fase 3 y las clases del consolidador

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\integracion-base-29sep`. Solo
ejecutar y reportar: **no modificar ni crear código, no commits.** Ignora los demás
`TASK_CONTEXT*.md`. Python: `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe`,
cwd en el worktree, salidas a `resultados/2026-09-30_consolidacion/` (nunca `/tmp`).

Cambios ya hechos: `tests/test_sensibilidad_fase3.py` (test renombrado a
`test_ejecutar_barrido_acepta_t_amb_diseno`, ahora afirma que la firma SÍ acepta
`T_amb_diseno`) y la tupla de clases de 6 a 4 niveles en `scripts/consolidar_excel_barridos.py`
y otros 5 scripts.

1. `python -u -m pytest -q -p no:cacheprovider tests/test_sensibilidad_fase3.py tests/test_sensitivity.py tests/test_sensitivity_verificacion.py tests/test_restricciones.py tests/test_restricciones_convenciones.py` → `pytest_rapida.log`.
2. `python -m py_compile` de los 6 scripts editados: `scripts/barrido_eps_fijos_085.py scripts/barrido_literatura_kcs11.py scripts/barrido_margen2k.py scripts/barrido_pinch6_realista.py scripts/consolidar_excel_barridos.py scripts/reclasificar_o2_tamb_realista.py`.
3. `python scripts/consolidar_excel_barridos.py` → `consolidar_2.log`. Con openpyxl, leer la hoja
   `Resumen` (fila 4 = cabeceras) y reportar esas cabeceras y las 3 primeras filas de datos; y
   contar en TODO el libro las celdas con `VALIDO_ADVERTENCIA` o `DEGENERADO`.

Reportar pasados/fallados por archivo, resultado del paso 2 y lo pedido en el 3.

---
project: ciclo_kalina_tercero
task_id: 2026-09-27-suite-sin-ui
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Re-correr la suite tras revertir la parte de interfaz de A+B

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\teqp-doble-verificacion`.
Solo ejecutar y reportar: **no modificar ni crear código, no commits.** Ignora los
demás `TASK_CONTEXT*.md`.

Se revirtieron `app.py`, `src/ui_backend.py`, `src/ui_barrido.py` a su versión original
y se quitaron `src/ui_verificacion.py` y `tests/test_ui_verificacion.py`. Quedan:
`src/properties/teqp_verificado.py`, `src/verificacion_motor_real.py`, cambios en
`src/sensitivity.py`, `tests/test_sensitivity.py`, `tests/test_sensitivity_verificacion.py`,
`tests/test_teqp_verificado.py`, `tests/test_verificacion_motor_real.py`.

1. Con `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` y cwd en el worktree:
   `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py`
   salida a `resultados/2026-09-27_integracion_AB/pytest_sin_ui.log` (dentro del
   worktree; nunca `/tmp`).
2. `python -m py_compile app.py src/ui_backend.py src/ui_barrido.py src/sensitivity.py`.
3. Reportar pasados/fallados/omitidos y, para cada fallo, si es uno de los 8 previos
   conocidos (2 de `test_restricciones_convenciones.py` por `src/ui_campos.py`
   inexistente; 6 de `test_verificacion_iapws_g4.py` por Cv/w) o uno nuevo, con la
   línea del error.

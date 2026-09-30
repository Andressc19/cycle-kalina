---
project: ciclo_kalina_tercero
task_id: 2026-09-30-suite-final
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-30
---

# TASK_CONTEXT — Suite completa final de la rama base

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\integracion-base-29sep`. Solo
ejecutar y reportar: **no modificar ni crear código, no commits.** Ignora los demás
`TASK_CONTEXT*.md`. Python: `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe`,
cwd en el worktree, salida a `resultados/2026-09-30_consolidacion/` (nunca `/tmp`).

Cambio hecho: en `tests/test_verificacion_iapws_g4.py` los fallos de Cv y w del motor teqp
(desviación documentada en `resultados/2026-09-23_verificacion_iapws_g4/`) pasan a `xfail`;
cualquier otro fallo de ese archivo sigue siendo fallo.

1. `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py -rxX` → `pytest_final.log`.
2. Reportar pasados / fallados / omitidos / xfailed. Para cada fallo: archivo, prueba, línea
   del error. Confirmar cuántos xfail vienen de `test_verificacion_iapws_g4.py` (se esperan
   6 nuevos además de los 2 que ya había).

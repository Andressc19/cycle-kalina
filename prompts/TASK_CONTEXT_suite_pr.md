---
project: ciclo_kalina_tercero
task_id: 2026-09-27-suite-pr
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Correr la suite en el worktree del PR (solo ejecutar y reportar)

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\pr-proteccion-teqp`.
**No modificar ni crear código, no commits, no push.** Ignora otros TASK_CONTEXT.

1. Con `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` y cwd en este worktree:
   `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py`
   con salida a `pytest_pr2.txt` dentro del worktree (no `/tmp`, no lo agregues a git).
2. Reportar pasados/fallados/omitidos. Fallos esperados: solo los 6 de
   `tests/test_verificacion_iapws_g4.py` (Cv/w de teqp vs guía IAPWS). Deben PASAR
   ahora: `tests/test_sensibilidad_fase3.py::test_ejecutar_barrido_t_amb_diseno_es_opcional`,
   `scripts/barridos_2026-09-19/fase1_profesor/test_fase1_profesor.py::test_resolver_punto_esquema_y_sintoma_documentado`
   y todo `tests/test_sensitivity_verificacion.py`. Cualquier otro fallo: línea del error.

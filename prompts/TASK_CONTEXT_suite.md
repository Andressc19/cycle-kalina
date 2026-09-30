---
project: ciclo_kalina_tercero
task_id: 2026-09-27-suite-teqp-verificado
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Correr la suite existente en el worktree `fix/teqp-doble-verificacion`

Estás en `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\teqp-doble-verificacion`.
Solo ejecutar y reportar: **no modificar ni crear código, no commits.** Los demás
`TASK_CONTEXT*.md` son otras tareas: ignóralos.

1. Con `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` y cwd en este
   worktree, correr:
   `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py`
   redirigiendo la salida a `resultados/2026-09-27_teqp_verificado/pytest_suite.log`
   (**dentro del worktree**; nunca escribas en `/tmp` ni fuera del worktree).
2. Si hay fallos: para cada test fallado, decir si importa o usa
   `src/properties/teqp_verificado.py`. Si no lo usa, es un fallo previo a este
   cambio (este cambio solo añade archivos nuevos).
3. Reportar en RESULTS: pasados / fallados / omitidos, lista de fallados con la
   línea del error y el veredicto del punto 2.

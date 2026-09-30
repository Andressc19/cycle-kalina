---
project: ciclo_kalina_tercero
task_id: 2026-09-30-suite-consolidacion-3
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-30
---

# TASK_CONTEXT — Verificar la corrección de la hoja Resumen del consolidador

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\integracion-base-29sep`. Solo
ejecutar y reportar: **no modificar ni crear código, no commits.** Ignora los demás
`TASK_CONTEXT*.md`. Python: `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe`,
cwd en el worktree, salidas a `resultados/2026-09-30_consolidacion/`.

Se corrigió `scripts/consolidar_excel_barridos.py` (filas `Fase *` del Resumen: ahora 8 celdas
en el orden KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO).

1. `python scripts/consolidar_excel_barridos.py` → `consolidar_3.log`.
2. Con openpyxl, en la hoja `Resumen`: reportar la fila de cabeceras (fila 4) y las filas de
   `Fase 1`, `Fase 2`, `Fase 3` y las 2 primeras de los barridos `09xx`; verificar que en cada
   fila la suma KALINA+CORREGIBLE+INVIABLE+NO_CONVERGIO sea igual a `Puntos` (las que tengan
   `-` se omiten) y reportar cualquier fila que no cumpla; y que ninguna fila tenga más celdas
   con valor que las cabeceras.
3. Contar en todo el libro las celdas con `VALIDO_ADVERTENCIA` o `DEGENERADO`.

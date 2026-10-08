# TASK_CONTEXT — Consolidar M5c, M4c, M7 y M8 en `datos/Excel_final_kalina.xlsx`

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.

## Restricciones

- NO modificar `src/` ni ningún script existente. No tocar `resultados/`.
- Cada `.py` debe tener como máximo 200 líneas: si hace falta, dos scripts. No hacer commit. No
  inventar datos.

## Tarea

Crear `scripts/barrido_final/excel_m5c_m7_m8.py`, con el mismo patrón que `excel_m5.py` (léelo):

- reutiliza `escribir_tabla`;
- crea o reemplaza sus hojas y añade o actualiza sus filas en `Resumen`;
- si se vuelve a ejecutar, el resultado tiene que ser el mismo.

| Hoja | Origen |
|---|---|
| `M5c_malla` | `resultados/2026-10-07_final_M5c/m5c_malla.csv` |
| `M5c_frontera` | `.../m5c_frontera.csv` |
| `M4c_lhs` | `resultados/2026-10-07_final_M4c/m4c_lhs.csv` |
| `M4c_techo` | `.../m4c_techo.csv` |
| `M4c_techo_Palta` | `.../m4c_techo_por_palta.csv` |
| `M7_optimos` | `resultados/2026-10-07_final_M7/m7_optimos.csv` |
| `M7_trayectorias` | `.../m7_trayectorias.csv` |
| `M7_evaluaciones` | `.../m7_evaluaciones.csv` |
| `M8_ANECDOTICO_oat` | `resultados/2026-10-07_final_M8_anecdotico/m8_oat.csv`. La descripción al final debe decir "ANECDÓTICO: valores fuera de [0.40, 0.95] no son realistas" |
| `M5c_M4c_M7_M8_figuras` | `m5c_mapa.png`, `m4c_techo.png`, `m7_convergencia.png` y `m8_curvas.png`, con `openpyxl.drawing.image.Image` |

## Pasos

1. Crear el script o los scripts.
2. Ejecutar en orden: `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py`,
   `excel_m5.py` y el nuevo.
3. Verificar desde un script escrito con `write`:
   - que las hojas nuevas existen y su número de filas coincide con su CSV;
   - que todas las hojas anteriores siguen presentes;
   - que `Resumen` tiene las filas nuevas.

## Formato de salida

El obligatorio de `AGENTS.md`.

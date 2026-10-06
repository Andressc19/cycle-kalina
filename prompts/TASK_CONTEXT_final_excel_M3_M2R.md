# TASK_CONTEXT — Consolidar M3 y M2R en `datos/Excel_final_kalina.xlsx`

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. Nunca desde la
  terminal (nada de heredocs, `Set-Content` ni `python -c` que escriba archivos).
- PowerShell 5.1: no existen `tee` ni `&&`; usa `;`.

## Restricciones

- NO modificar `src/` ni ningún script existente, salvo la lectura que se pide abajo. Tampoco tocar
  los CSV ni los reportes de `resultados/`.
- Cada `.py` debe tener como máximo 200 líneas. No hacer commit. No inventar datos.

## Tarea

Crear `scripts/barrido_final/excel_m3_m2r.py`, con el mismo patrón que
`scripts/barrido_final/excel_m2.py` (léelo):

- abre el libro existente;
- crea o reemplaza las hojas de M3 y M2R, reutilizando `escribir_tabla` de `excel_final.py` y su
  formato (unidades, colores de clase, filtro y descripción al final);
- añade o actualiza sus filas en `Resumen`;
- si se vuelve a ejecutar, el resultado tiene que ser el mismo.

Hojas que debe crear:

- `M3_ofat` ← `resultados/2026-10-06_final_M3/m3_ofat.csv`
- `M3_resumen` ← `m3_resumen.csv`
- `M3_cruces` ← `m3_cruces.csv`
- `M2R_n1` ← `resultados/2026-10-06_final_M2R/m2r_n1_malla.csv` + `m2r_n1_biseccion.csv` (con una
  columna `fase` que distinga malla de bisección)
- `M2R_n2a`, `M2R_n2b` y `M2R_n3` ← lo mismo para cada parte (n3 no tiene bisección)
- `M2R_fronteras` ← `m2r_fronteras.csv`
- `M2R_kalina` ← `m2r_kalina.csv`
- `M2R_resumen` ← `m2r_resumen.csv`

Además, insertar la imagen `resultados/2026-10-06_final_M3/m3_tornado.png` en una hoja
`M3_figuras` (con `openpyxl.drawing.image.Image`, que requiere Pillow; si Pillow no está, NO lo
instales: deja la hoja con la ruta de la figura y repórtalo).

## Pasos

1. Crear el script.
2. Ejecutar en orden: `python scripts/barrido_final/excel_final.py`,
   `python scripts/barrido_final/excel_m2.py` y `python scripts/barrido_final/excel_m3_m2r.py`.
3. Verificar con openpyxl, desde un script escrito con `write`: los nombres de las hojas y que el
   número de filas de datos de cada hoja nueva coincide con su CSV de origen. Imprimir el resultado.

## Formato de salida

El obligatorio de `AGENTS.md`.

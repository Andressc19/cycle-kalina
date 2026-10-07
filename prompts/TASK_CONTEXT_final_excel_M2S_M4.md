# TASK_CONTEXT — Consolidar M2S, M4 y M4b en `datos/Excel_final_kalina.xlsx`

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.
- **En paralelo corre M5** (`m5_*`, `resultados/2026-10-07_final_M5/`): no toques esos archivos.

## Restricciones

- NO modificar `src/` ni ningún script existente. No tocar `resultados/`.
- Cada `.py` debe tener como máximo 200 líneas. No hacer commit. No inventar datos.

## Tarea

Crear `scripts/barrido_final/excel_m2s_m4.py`, con el mismo patrón que `excel_m3_m2r.py` (léelo):

- reutiliza `escribir_tabla` de `excel_final.py`;
- crea o reemplaza sus hojas y añade o actualiza sus filas en `Resumen`;
- si se vuelve a ejecutar, el resultado tiene que ser el mismo.

| Hoja | Origen |
|---|---|
| `M2S_malla` | `resultados/2026-10-06_final_M2S/m2s_malla.csv` |
| `M2S_biseccion` | `.../m2s_biseccion.csv` |
| `M2S_resumen` | `.../m2s_resumen.csv` |
| `M2S_kalina` | `.../m2s_kalina.csv` |
| `M4_lhs500` | `resultados/2026-10-06_final_M4/m4_lhs.csv` (300) + `resultados/2026-10-07_final_M4b/m4b_lhs.csv` (200), con una columna `lote` (M4/M4b) |
| `M4_rsa` | `resultados/2026-10-07_final_M4b/m4b_rsa.csv` |
| `M4_prcc` | `.../m4b_prcc.csv` |
| `M4_pawn` | `.../m4b_pawn.csv` |
| `M4_presiones_rangos` | `.../m4b_rangos_presiones.csv` |
| `M4_ventana_Palta` | `.../m4b_ventana_por_palta.csv` |
| `M4_ventana_Tfuente` | `.../m4b_ventana_por_tfuente.csv` |
| `M4_ventana_Tsumidero` | `.../m4b_ventana_por_tsumidero.csv` |
| `M4_bloqueo_rP` | `.../m4b_bloqueo_por_rP.csv` |
| `M4_top_kalina` | `.../m4b_top_kalina.csv` |
| `M4_convergencia` | `.../m4b_convergencia.csv` |

Además, una hoja `M4_figuras` con las imágenes `m4b_plano_presiones.png`, `m4b_hist_dP_rP.png` y
`m4b_rsa_ks.png` (`openpyxl.drawing.image.Image`). Si Pillow no está disponible, NO lo instales:
pon las rutas y repórtalo.

Unidades nuevas para el formato: `dP (kPa)`, `rP (−)`, `dT_fs (K)`, `KS (−)`, `p_valor (−)`,
`PRCC (−)`, `lo`/`hi` (según la variable, o "(−)"), `n_kalina (−)` y `pct_kalina (%)`.

## Pasos

1. Crear el script.
2. Ejecutar en orden: `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py` y `excel_m2s_m4.py`.
3. Verificar desde un script escrito con `write`: los nombres de las hojas y que el número de
   filas de datos de cada hoja nueva coincide con su CSV de origen (500 en `M4_lhs500`).

## Formato de salida

El obligatorio de `AGENTS.md`.

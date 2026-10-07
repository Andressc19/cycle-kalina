# TASK_CONTEXT — Consolidar M5 en `datos/Excel_final_kalina.xlsx`

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.

## Restricciones

- NO modificar `src/` ni ningún script existente. No tocar `resultados/`.
- Cada `.py` debe tener como máximo 200 líneas. No hacer commit. No inventar datos.

## Tarea

Crear `scripts/barrido_final/excel_m5.py`, con el mismo patrón que `excel_m2s_m4.py` (léelo):

- reutiliza `escribir_tabla` de `excel_final.py`;
- crea o reemplaza sus hojas y añade o actualiza sus filas en `Resumen`;
- si se vuelve a ejecutar, el resultado tiene que ser el mismo.

| Hoja | Origen (`resultados/2026-10-07_final_M5/`) |
|---|---|
| `M5_lhs` | `m5_lhs.csv` (600 filas; incluye la columna `escenario` y la columna `omitido`) |
| `M5_resumen` | `m5_resumen.csv` |
| `M5_rangos` | `m5_rangos.csv` |
| `M5_cercano_profesor` | `m5_cercano_profesor.csv` |
| `M5_escenarios` | Tabla fija con 5 filas: `escenario`, `se_conserva`, `variables_libres`, `KALINA_LHS`, `nota`. Los textos están abajo; `KALINA_LHS` se toma de `m5_resumen.csv` |
| `M5_figuras` | Las imágenes `m5_S1.png` … `m5_S5.png` (`openpyxl.drawing.image.Image`). Si Pillow no está, NO lo instales: pon las rutas y repórtalo |

Textos de `M5_escenarios`:

- **S1:**
  - se_conserva: "T_fuente 623.15 K + T_sumidero 300.03 K"
  - variables_libres: "P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond"
  - nota: "KALINA con eps_hrvg ~0.5, P_baja 1394-1953 kPa, eps_cond >= 0.86"
- **S2:**
  - se_conserva: "P_alta 3000 + P_baja 400 kPa"
  - variables_libres: "T_fuente, T_sumidero, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond"
  - nota: "0 KALINA en el LHS, pero factible en una franja angosta: T_fuente ~390-405 K con eps_cond >= 0.92 (KALINA de M2R: 403 K, eps_cond 0.95, eta 9.50 %)"
- **S3:**
  - se_conserva: "P_alta 3000 + P_baja 400 kPa + T_sumidero 300.03 K"
  - variables_libres: "T_fuente, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond"
  - nota: la misma que S2
- **S4:**
  - se_conserva: "P_alta 3000 kPa + T_fuente 623.15 K + T_sumidero 300.03 K"
  - variables_libres: "P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond"
  - nota: "KALINA con P_baja 993-1928 kPa, eps_cond >= 0.88; todos fuera de rango confiable"
- **S5:**
  - se_conserva: "T_fuente 623.15 K + x_b 0.50"
  - variables_libres: "T_sumidero, P_alta, P_baja, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond"
  - nota: "KALINA con P_baja 889-1772 kPa, eps_cond >= 0.84; todos fuera de rango confiable"

Unidades de las columnas nuevas: `escenario (−)`, `omitido (−)`, `d (−)`, `D (−)`, `KALINA_LHS (−)`
y `se_conserva`/`variables_libres`/`nota` (texto).

## Pasos

1. Crear el script.
2. Ejecutar en orden: `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py` y
   `excel_m5.py`.
3. Verificar desde un script escrito con `write`: los nombres de las hojas, que el número de filas
   de datos de cada hoja de M5 coincide con su CSV de origen, que todas las hojas anteriores
   (M0–M4) siguen presentes y que `Resumen` tiene las filas de M5.

## Formato de salida

El obligatorio de `AGENTS.md`.

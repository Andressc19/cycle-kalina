---
project: ciclo_kalina_tercero
task_id: 2026-09-21-excel-iteraciones-3-fases
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-21
---

# TASK_CONTEXT — Excel consolidado de todas las iteraciones (Fase 1, 2, 3)

## Task ID

2026-09-21-excel-iteraciones-3-fases

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Tarea de exportación pura — lee los
CSV ya generados, NO corre ningún punto del ciclo nuevo, NO modifica ningún CSV existente.

## Objective

Generar un archivo Excel (`.xlsx`, con `openpyxl`, ya es dependencia del proyecto) que
contenga TODAS las iteraciones ya corridas de las 3 fases, con la misma información que ya
se le mostró al usuario en un panel interactivo: cada punto con TODAS sus columnas
originales, incluida la columna de mensaje/clasificación (el texto de por qué corrigió o
qué falló, cuando exista esa columna en el CSV de origen — NO la resumas ni la recortes).

## Fuente de datos (léelos tal cual están, no inventes ni completes nada)

- `resultados/barridos_2026-09-19/fase1_profesor/*.csv` (3 archivos: eta_vs_Palta_profesor,
  eta_vs_xb_profesor, eta_vs_Tambiente_profesor)
- `resultados/barridos_2026-09-19/fase2_libre/*.csv` (TODOS los CSV que empiecen por
  `busqueda_`, `sensibilidad_`, `mapa_2d_`, `prescan_` — NO incluyas `ancla_estados.csv` ni
  `ancla_balance.csv`, esos no son "iteraciones" de barrido, son la tabla del punto ancla;
  inclúyelos en una hoja aparte si quieres, pero identifícalos como tal)
- `resultados/barridos_2026-09-19/fase3_real/*.csv` (mismo criterio: TODOS los
  `busqueda_`/`sensibilidad_`/`mapa_2d_`, ancla aparte)

**Nota importante sobre duplicados de nombre**: en `fase3_real/` hay archivos con nombres
casi iguales por mayúsculas/versión (`sensibilidad_palta.csv` y `sensibilidad_P_baja.csv`,
`sensibilidad_pbaja.csv` y `sensibilidad_P_baja.csv`, `sensibilidad_xb.csv` y
`sensibilidad_x_b.csv`) — son de rondas distintas (`palta`/`pbaja`/`xb` son de la Fase 3
original antes del ancla final 690/0.75; `P_baja`/`x_b` son del barrido final). Incluye
TODOS, cada uno en su propia hoja/tabla con su nombre de archivo real como identificador —
no los fusiones ni descartes ninguno asumiendo que es un duplicado exacto.

## Estructura del Excel

Una hoja de Excel por fase como mínimo (`Fase 1`, `Fase 2`, `Fase 3`), y dentro de cada hoja,
una tabla por cada CSV de origen (con el nombre del archivo como encabezado de sección antes
de cada tabla, y una fila en blanco entre tablas) — o, si prefieres más claro para el
usuario, una hoja de Excel POR CADA CSV (nombra la hoja como el archivo, recortando a los 31
caracteres que permite Excel si hace falta) agrupadas por prefijo `Fase1_`/`Fase2_`/`Fase3_`
en el nombre de hoja. Decide tú cuál de las dos organizaciones queda más navegable — ambas
son válidas, prioriza que no se pierda ninguna columna ni fila.

Añade también una hoja `Resumen` al principio con: conteo de filas por fase, conteo de
`clasificacion` por fase (KALINA/CORREGIBLE/NO_CONVERGIO/otro), y una nota de una línea por
fase (reusa lo ya documentado en `resultados/barridos_2026-09-19/RESUMEN_CRUZADO_3_FASES.md`
y `REPORTE_FASE2_FASE3.md`, no inventes texto nuevo).

## Dónde guardar

**Ruta absoluta exacta**:
`D:\Desktop\ciclo_kalina_tercero\primeros_barridos_e_iteraciones_kalina.xlsx`

Esa es la carpeta RAÍZ del proyecto (el checkout principal, NO este worktree
`D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barridos-tercero-f7448d`). Es una ruta
fuera del control de versiones de esta rama — created el archivo directamente con Python
(`pandas`/`openpyxl`), no lo agregues a git ni intentes comitearlo.

## Files

Puedes crear UN script en `scripts/barridos_2026-09-19/` (p.ej. `excel_iteraciones.py`,
≤200 líneas) que lea los CSV y escriba el Excel en la ruta de arriba. Es el único archivo
nuevo permitido dentro del repo — el `.xlsx` en sí vive FUERA del repo (ver "Dónde guardar").

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ningún CSV existente, ningún archivo
de `resultados/` ni `scripts/barridos_2026-09-19/fase1_profesor|fase2_libre|fase3_real/`.

## Constraints

1. Script ≤200 líneas.
2. No corras ningún punto del ciclo — es solo lectura de CSV + escritura de Excel.
3. No pierdas ninguna columna de ningún CSV de origen.
4. Verifica al final que el `.xlsx` se generó (existe, se puede reabrir con
   `pd.read_excel` o `openpyxl.load_workbook`, número de hojas y filas totales razonable) y
   repórtalo con números concretos.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: ruta final del archivo, número de hojas, número total de
filas por fase.

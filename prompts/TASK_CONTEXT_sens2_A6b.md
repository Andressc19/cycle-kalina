# TASK_CONTEXT — Sensibilidad 2, A6b: hoja F7 del libro con los resultados de rigor estadístico

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy, openpyxl, pytest; **sin** scikit-learn ni yaml).
**Contexto:** plan en `docs/PLAN_SENS2_MEJORA.md` (sección 6). Sin corridas nuevas del motor (el «motor» es el programa que
calcula el ciclo; aquí solo se analizan datos ya calculados). Otras tareas corren a la vez sobre OTROS archivos: **toca solo los
archivos que esta tarea te asigna** y no hagas `git add`, `git commit`, `git stash`, `git checkout` ni `git reset` (el director commitea).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba archivos). PowerShell 5.1,
  sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. Cada `.py` máximo 200 líneas (divide en módulos si hace falta).
- Scripts nuevos en `scripts/sens2/`; importa con `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. Se ejecutan con
  `$env:PYTHONPATH = "scripts/sens2"` y `..\..\..\.venv\Scripts\python.exe -I scripts\sens2\<script>.py` (si tu shell no admite
  `$env:`, ejecuta el script desde la raíz: ya inserta su carpeta en `sys.path`).
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda salida: «confiable»,
  «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol», «sin respaldo».
- Los umbrales salen de los datos o de este documento; no inventes ninguno. Todo número sale de un archivo. Semilla fija indicada.
- Si algo es ambiguo, repórtalo en `UNRESOLVED` en lugar de decidir. Reporte final en el formato de `AGENTS.md`.

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/s2_f7.py` (nuevo) y la salida de prueba
`resultados/2026-10-18_sens2_F1/_prueba_f7.xlsx`. **No toques** `datos/Kalina_anal_sensible_2.xlsx`, `s2_construir.py` ni ningún otro módulo
(el director integra la hoja después). Si necesitas más de 200 líneas, divide en `s2_f7.py` y `s2_f7b.py` (ambos tuyos).

## Qué construir

Un módulo `s2_f7.py` con la función `hoja_f7_rigor(wb, datos)` y la lista `HOJAS_F7 = [hoja_f7_rigor]`, que crea la hoja
**`F7 Rigor estadistico`** (sin tildes en el nombre de hoja). **Copia el patrón de `scripts/sens2/s2_f6.py`** (imports, `titulo`, `condiciones`,
`subtitulo`, `tabla`, `bloque`, `nota`, `descripcion`, `numero`; rutas con `RAIZ`; nota «Base» en `condiciones`). Cada gráfico se hace con
`bloque(...)` de `x5_graficos` (la tabla del gráfico queda a su izquierda y el gráfico a la derecha); **todas las columnas de la tabla de un
`bloque` son series del gráfico** salvo que uses `n_series=` (las demás columnas son auxiliares); **no mezcles en un mismo gráfico magnitudes de escalas
distintas** (conteos con proporciones). Barras de error: `bloque(..., n_series=k, errores={indice_de_serie: (indice_col_mas, indice_col_menos)})`,
donde los índices son posiciones en `encabezados` (0 = categoría) de las columnas auxiliares con el aumento y la disminución (ver `s2_f5u.py`, primer
gráfico de la sección 1, para un ejemplo funcionando). Después de cada `tabla(...)` que no sea un `bloque` pon `f += 1` antes de la siguiente cosa
(la función devuelve la última fila usada).

Todos los números salen de CSV en `resultados/2026-10-18_sens2_F1/` (léelos con pandas; ninguna cifra a mano). Secciones, en este orden:

1. **NO_CONVERGIO por estudio** (`p6_nc_fraccion.csv`: `estudio, centro, n, nc, frac_nc`). Tabla por estudio (suma de `n` y `nc` sobre los centros,
   `frac_nc` = nc/n) ordenada por estudio, y gráfico de barras de `frac_nc` (en %) por estudio (una serie).
2. **Clase por cuartil de T_fuente** (`p6_nc_cuartiles.csv`: `bloque, cuartil_T_fuente, T_min, T_max, n, KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO,
   p_kalina_nc_cero, p_nc, p_kalina_si_convergio, ic_lo, ic_hi`). Tabla completa. Gráfico de barras con 16 categorías (`C1 Q1` … `C4 Q4`: usa el
   centro corto C1..C4 del nombre del bloque y el cuartil) y 2 series: `P(KALINA), NO_CONVERGIO = no KALINA` y `P(KALINA) si convergio`, esta última con
   barras de error (aumento `ic_hi − p`, disminución `p − ic_lo`; columnas auxiliares).
3. **Estabilidad de los tres primeros** (`p6_nc_top3.csv`: `bloque, top3_nc_como_no_kalina, top3_sin_nc, top3_nc_como_kalina, igual_sin_nc, igual_nc_como_kalina`).
   Solo tabla y una nota que explique en lenguaje llano la lectura.
4. **Comparación pareada** (`p6_pareado_dist.csv`: `variante, grupo, calculo, n, l1_min, l1_max, estimador, ic_lo, ic_hi, pendiente`). Tabla con las filas
   de `variante == "mismo_centro"` y `grupo == "todos"` cuyo `calculo` empieza por `tramo`. Gráfico de barras de `estimador` (mediana de la diferencia de eta
   en puntos porcentuales) por tramo de distancia con barras de error (IC). Nota: el vecino cercano da la cifra defendible; el ajuste lineal es inestable.
5. **Envolventes de equipos según el diseño** (`p6_equipos_diseno.csv`: `ambito, cantidad, conjunto, n, p5, p50, p95, desplazamiento, sensible`).
   Tabla: por ámbito (`todos`, C1..C4) el número de cantidades con `sensible == "si"` y el total de cantidades, y gráfico de barras con el número de
   cantidades sensibles por ámbito (una serie).
6. **Fronteras de la regresión logística con intervalo** (`p6_fronteras_ic.csv`: `bloque, variante, variable, coef_estandar, error_tipico, x_frontera, ic_lo,
   ic_hi, fraccion_valida, auc, calidad, frontera_barrido, barrido_dentro_ic`). Tabla con las filas `variante == "sin_nc"`, `calidad == "aceptable"` y variable en
   {`T_sumidero`, `P_baja`, `x_b`, `eps_cond`} (las más interpretables): bloque, variable, frontera, IC, frontera del barrido, si el barrido cae dentro. Nota con
   el AUC por bloque (de las mismas filas). Sin gráfico.
7. **Validación cruzada de las superficies** (`p6_superficies_cv.csv`: `par, bloque, n_celdas, r2, r2_cv, rmse, rmse_cv, clase_celda_max_ajuste, en_borde`).
   Tabla completa y gráfico de barras con 2 series (`R2 en la muestra`, `R2 con validacion cruzada`) por malla (categoría `par bloque-corto`).
8. **Potencia de la propagación de incertidumbre** (`p6_potencia_u1.csv`, filas con `tabla == "entre_lotes"`: `centro, n, p1, p2, dif, z, d_min, d_min_peor`).
   Solo tabla y una nota con la diferencia mínima detectable en el peor caso.
9. Al final: `descripcion(ws, f + 1, [...])` con dos líneas llanas.

## Prueba (sin tocar el libro principal)

Crea un `Workbook()`, quita la hoja inicial, llama a `hoja_f7_rigor(wb, None)`, ejecuta `from x5_graficos import dibujar_todos; dibujar_todos(wb)` y guarda en
`resultados/2026-10-18_sens2_F1/_prueba_f7.xlsx`. Reabre con `openpyxl` y comprueba que la hoja existe, que tiene al menos 6 gráficos, que ninguna celda de las
tablas de los gráficos está vacía y que ninguna cadena contiene las palabras prohibidas. Reporta en RESULTS el número de gráficos y de filas de la hoja.
Atención: `x5_graficos.GRAFICOS` es una lista global que acumula los gráficos registrados; haz la prueba en un proceso nuevo.

## Criterios de aceptación

- Corre sin error, ≤ 200 líneas por archivo, sin cifras escritas a mano, sin modificar archivos existentes.

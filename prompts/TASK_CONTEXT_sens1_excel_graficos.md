# TASK_CONTEXT — Excel Sensibilidad 1: crear los gráficos nativos que faltan y endurecer el verificador

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Código existente:** `scripts/sens1/x1_cargar.py` … `x8_verificar.py`, `conclusiones.py`. Ya se resolvió la
terminología; **no cambies textos ni cifras**, solo añade gráficos y endurece `x8`.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas de otro directorio en la terminal**: el sandbox las rechaza
  (`external_directory`) y aborta toda la ejecución (pasó en el intento anterior, run 103). La terminal ya
  está en el directorio de trabajo: usa **rutas relativas** (`scripts\sens1\x7_construir.py`,
  `datos\Kalina_anal_sensible_1.xlsx`) y el intérprete como
  `..\..\..\.venv\Scripts\python.exe` (desde este worktree, la raíz del proyecto está tres niveles arriba).
- **El libro es `datos\Kalina_anal_sensible_1.xlsx`** (no existe ningún `resultados\sensibilidad1_kalina.xlsx`).
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`). Solo ASCII en los `print`.
- `timeout=1800000` en la shell. **NO ejecutes `pytest`.** El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, los CSV de `resultados/` ni
  otros libros Excel. Cada `.py`: máximo 200 líneas (divide en `x5b_graficos_a.py`, `x5c_graficos_b.py`
  si hace falta).
- Reglas de formato del usuario (ya vigentes): gráficos **nativos** de Excel, con los datos **visibles** y
  **junto a la tabla de la que salen**, sin tapar celdas ni otros gráficos; gráfico y tabla cuentan lo
  mismo; todas las tablas con cuadrícula; **sin freeze panes**; nada de abreviaturas de dos letras; todo
  en español. Usa los ayudantes de `scripts/analisis_final/a2_graf_estilo.py` (`overlay=False`,
  `varyColors=False`, `invertIfNegative=False`, nunca `solidFill` y `noFill` a la vez en la misma línea).
- Terminología: «KALINA (total)», «dentro del rango experimental», «fuera del rango experimental» (control
  7 de `x8`: ninguna celda ni título de gráfico con «confiable», «fuera de rango», «sin respaldo»,
  «no citable», «indicio» o «extrapol»).

## Problema a resolver (verificado por el director abriendo el libro en Excel real)

El libro tiene **solo 2 gráficos** (uno en `Conclusion consolidada`, otro en `E1 Una variable`) y **los dos
tienen 0 series** (vacíos). Los otros no se registraron: `x4_resumenes.py` llama `registrar(...)` una sola
vez y `x6_sintesis.py` otra. El control 4 de `x8_verificar.py` solo mira la «estructura» y lo dejó pasar.

1. **Averigua por qué esos 2 gráficos tienen 0 series** (en `x5_graficos.py`, `_barras`/`_linea`) y corrígelo.
2. **Crea los gráficos de la lista** (cada uno junto a una tabla visible de su hoja de resumen; si la tabla
   no existe todavía, créala a la izquierda o arriba del gráfico, con encabezado de condiciones):

| Hoja | Gráfico | Tipo | Datos |
|---|---|---|---|
| `E0 Referencia Husavik` | η (%) de cada punto | barras | 11 puntos de `fase0` (categoría = id_punto) |
| `E1 Una variable` | KALINA por variable, centro C1 y otro para C2 | barras agrupadas | series: total / dentro / fuera del rango experimental, categoría = variable |
| `E2 Pares` | KALINA por par B1–B6 | barras agrupadas | series: C1, C2 |
| `E3 LHS 9 variables` | puntos por clase y centro | barras apiladas | series: KALINA, CORREGIBLE, NO_CONVERGIO, INVIABLE |
| `E4 Fuente 70-300 C` | KALINA por nivel de T_fuente (dentro y fuera) y otro con η máxima por nivel | barras apiladas + líneas | 13 niveles (°C) |
| `E5 Condensador y clima` | P_baja mínima con KALINA frente a ε_cond | líneas | una línea por T_sumidero (10, 20, 30 °C); celdas vacías donde no hay KALINA |
| `E6 P_alta baja y x_b` | KALINA por x_b | barras agrupadas | series: C1, C2 |
| `E7 Fuente fria` | KALINA por banda de T_fuente (70–80 … 120–130 °C) | barras | total |
| `E8 Mapa fuente y clima` | P_baja mínima con KALINA frente a T_sumidero y otro con η máxima | líneas | una línea por T_fuente (6) |
| `E9 Equipos baratos` | η (%) por combinación de η_t/ε_HRVG/ε_reg | barras agrupadas | 27 categorías, series C1 y C2 |
| `E10 Centros nuevos 1 variable` | KALINA por variable | barras agrupadas | series: total / dentro / fuera, un gráfico por centro C3 y C4 |
| `E11 Centros nuevos pares` | KALINA por par B1–B4 | barras agrupadas | series: C3, C4 |
| `Conclusion consolidada` | S1: clases por estudio (apiladas); S5: η máxima por estudio (dentro del rango experimental y todos los KALINA) | barras | 12 estudios |

   Son ≥ 20 gráficos. Cada uno con título, ejes rotulados con unidades, y una **nota de pie en una celda
   debajo** con el criterio (qué incluye, fuente de datos y n).
3. **Endurece `x8_verificar.py` (control 4 estricto)**: para CADA gráfico del libro (lee con openpyxl),
   (a) tiene ≥ 1 serie; (b) cada serie tiene referencia de valores a celdas del mismo libro, en hoja
   visible, y esas celdas contienen **números** (al menos una celda numérica; no todas vacías); (c) la
   cantidad de puntos de la serie coincide con la de su tabla; (d) imprime una línea por gráfico
   (hoja, título, nº de series, nº de puntos). Falla si hay menos de 20 gráficos en total, o si alguna hoja
   `E0`…`E11` de resumen no tiene al menos 1.
4. Control 5 (solapes): compara las celdas de anclaje de cada gráfico con las dimensiones de las tablas
   **y** de los demás gráficos de su hoja (ancho 16 cm ≈ 10 columnas, alto 8 cm ≈ 16 filas) y falla si
   se solapan.

## Ejecución

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

**No des `done` si algún control está en FALLA, ni si el nº de gráficos es < 20.** Reporta en el formato de
`AGENTS.md`; en RESULTS pega la salida completa de `x8_verificar.py` (incluidas las líneas por gráfico).

# TASK_CONTEXT — Sensibilidad 2, A3: fronteras con intervalo y validación cruzada de superficies

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p6_fronteras_ic.py` (nuevo), `scripts/sens2/p6_superficies_cv.py` (nuevo)
y las salidas en `resultados/2026-10-18_sens2_F1/` (ya existe): `p6_fronteras_ic.csv`, `p6_fronteras_ic.md`, `p6_superficies_cv.csv`,
`p6_superficies_cv.md`.

## Parte 1 — Frontera con intervalo (`p6_fronteras_ic.py`)

Datos: `resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv`. Bloques LHS: estudio 3 con `centro` igual a `C1 Husavik` y `C2 ancla A*`;
estudio 14 con `C3 caliente 150 C` y `C4 frio 110 C`. Variables de entrada (9; `eta_p` es constante en estos LHS):
`T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eps_hrvg, eps_reg, eps_cond`. Respuesta: `1` si `clasificacion == "KALINA"`, si no `0`.
Dos variantes por bloque: **todas** (NO_CONVERGIO cuenta como 0) y **sin_nc** (se quitan las filas NO_CONVERGIO).

Centros (T_fuente K, T_sumidero K, P_alta kPa, P_baja kPa, x_b, eta_t, eps_hrvg, eps_reg, eps_cond):
C1 (394.15, 278.15, 3300, 690, 0.82, 0.85, 0.85, 0.75, 0.95); C2 (403.0, 300.15, 3000, 563.64, 0.50, 0.85, 0.85, 0.75, 0.95);
C3 (423.15, 280.5, 3150, 950, 0.75, 0.85, 0.85, 0.75, 0.95); C4 (383.15, 282.5, 3880, 910, 0.88, 0.85, 0.85, 0.75, 0.95).

1. Ajusta una regresión logística con las 9 variables estandarizadas (media y desviación del bloque) por IRLS con ridge 1e-3 sobre los
   coeficientes (no sobre el intercepto), hasta 100 iteraciones, tolerancia 1e-8 (implementa tu propia función; `p3_metodos.logistica`
   no devuelve el intercepto). Calcula el AUC por la fórmula de rangos (Mann-Whitney) y el error típico de cada coeficiente con la
   inversa de la matriz de información.
2. **Frontera en la variable v con las otras 8 en el centro:** con `z_j = (centro_j − media_j)/desv_j`, la frontera (probabilidad 0.5)
   es `z_v* = −(b0 + Σ_{j≠v} b_j z_j) / b_v` y `x_v* = media_v + desv_v · z_v*`. Si `|b_v| < 1e-6` no hay frontera.
3. **Bootstrap** de 1 000 remuestreos de filas (semilla 20261018), reajustando cada vez; guarda `x_v*` de los remuestreos donde la
   regresión converge y `b_v` conserva el signo del ajuste original. Reporta los percentiles 2.5 y 97.5 y la fracción de remuestreos
   válidos. Si la fracción válida es < 0.80 o el AUC < 0.80, marca la fila `calidad = "pobre"`; si no, `"aceptable"`.
4. **Comparación con la frontera de barridos de una variable:** `resultados/2026-10-17_sens2_P1/p1_fronteras.csv` (columnas `centro`,
   `variable`, `forma`, `direccion`, `valor_frontera`). Para cada (centro, variable) con filas `escalon` o `ventana`, une los valores
   de frontera en la columna `frontera_barrido` (separados por `;`) y calcula `barrido_dentro_ic` = `"si"` si algún valor cae en
   [IC bajo, IC alto]. Las variables con nombre distinto: `eps_cond`, `eta_t`, etc. coinciden con las del dataset; ignora las que no
   existan en uno de los lados.
5. Salida `p6_fronteras_ic.csv` con columnas `bloque, variante, variable, coef_estandar, error_tipico, x_frontera, ic_lo, ic_hi,
   fraccion_valida, auc, calidad, frontera_barrido, barrido_dentro_ic`, y `p6_fronteras_ic.md` con: el AUC por bloque y variante, y una
   tabla en lenguaje llano de las filas con calidad aceptable. Imprime cuántas filas son aceptables y cuántas coinciden con el barrido.

## Parte 2 — Validación cruzada de las superficies (`p6_superficies_cv.py`)

Usa `import s2_calc as C` (en `scripts/sens2`): `C.BLOQUES` (lista de los 4 nombres de bloque), `C.malla_clases(bloque, par)` con `par`
en `"B2"` (P_baja x x_b) y `"B3"` (P_alta x P_baja), que devuelve `(eta, cls, av, bv)` (eta con NaN fuera de las celdas KALINA; `cls`
con `"K"`, `"C"`, `"NC"`, `"I"` o `"-"`), y `C.ajuste_cuadratico(eta, av, bv)` (ajuste en la muestra; devuelve un dict con `n`, `r2`,
`rmse`, `max_ajuste` = (a, b, eta) o `None` si hay menos de 8 celdas KALINA).

Para cada par y bloque (8 mallas): replica el ajuste cuadrático `eta ~ 1 + a + b + a² + b² + ab` con a y b estandarizadas (media y desviación
de las celdas KALINA) y calcula la **validación cruzada dejando una celda fuera**: para cada celda KALINA reajusta sin ella y predice
esa celda; acumula `SSE_cv` y `SST` (respecto de la media de eta de las celdas KALINA) y reporta `r2_cv = 1 − SSE_cv/SST`,
`rmse_cv = sqrt(SSE_cv/n)`. Reporta también el `r2` y `rmse` en la muestra (los de `ajuste_cuadratico`, deben coincidir con tu propio
ajuste a 1e-6; si no, repórtalo), la clase de la celda donde cae el máximo del ajuste sobre toda la malla (`cls` de esa celda) y si esa
celda está en el borde de la malla (primera o última fila o columna).
Salida `p6_superficies_cv.csv` con columnas `par, bloque, n_celdas, r2, r2_cv, rmse, rmse_cv, clase_celda_max_ajuste, en_borde` y
`p6_superficies_cv.md` con una tabla y una frase llana por par: si la validación cruzada degrada mucho el R² (diferencia > 0.2).
Las mallas con menos de 8 celdas KALINA se reportan con `r2`, `r2_cv` vacíos y `nota = "menos de 8 celdas KALINA"`.

## Criterios de aceptación

- Ambos scripts corren en menos de 5 minutos cada uno y respetan 200 líneas.
- Los CSV contienen todas las combinaciones esperadas: Parte 1 = 4 bloques x 2 variantes x 9 variables = 72 filas (menos las sin frontera);
  Parte 2 = 8 mallas.
- No toques `s2_calc.py` ni ningún otro archivo existente.

# TASK_CONTEXT — Sensibilidad 2, A7t: eficiencia del ciclo frente a T_fuente con los datos existentes (sin motor)

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p6_ciclo_T.py` (nuevo), `scripts/sens2/s2_f4t.py` (nuevo) y las salidas en
`resultados/2026-10-18_sens2_F1/`: `p6_ciclo_T.csv`, `p6_ciclo_T.md` y la prueba `_prueba_f4t.xlsx` (borra esta al final).
**No toques** `s2_construir.py` ni el libro `datos/Kalina_anal_sensible_2.xlsx`; el director integra la hoja.

## Objetivo

La pregunta 3 del profesor pide el comportamiento del ciclo (no solo del regenerador) frente a la temperatura de la fuente. Sin correr el motor se puede describir
lo que ya está muestreado: la mejor η observada y sus condiciones, por banda de T_fuente.

## Parte 1 — `p6_ciclo_T.py`

Datos: `resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv` (3 663 filas; columnas `id_punto, estudio, centro, clasificacion, kalina, fuera_rango, T_fuente, T_sumidero, P_alta, P_baja,
x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, eta_pct, wnet_mb`). Bandas de T_fuente de 20 K: `[340, 360)`, `[360, 380)`, …, `[560, 580)` (usa `pandas.cut` con `right=False`;
T_fuente de 343.15 a 573.15 K). Para cada banda:
1. `n` (todas las filas), `n_kalina`, `n_corregible`, `n_inviable`, `n_no_convergio`, `p_kalina` (KALINA/n, NO_CONVERGIO como no KALINA) y `p_kalina_si_convergio` (KALINA/(n − NO_CONVERGIO)).
2. Sobre los KALINA con `eta_pct` finita: `eta_max` y el `id_punto`, `T_fuente`, `P_alta`, `P_baja`, `x_b`, `eta_t`, `eps_reg`, `eps_cond` del punto de mayor η, `fuera_rango` de ese punto; `eta_max_dentro` (máximo
   solo entre los KALINA dentro del rango experimental, `fuera_rango == False`); `eta_p90`, `eta_mediana`; `wnet_mb_max` y `wnet_mb_mediana`.
3. Lo mismo `eta_mediana_lhs` y `n_kalina_lhs` solo con los puntos de los estudios 3 y 14 (muestreo LHS), para ver si el patrón depende del diseño.
4. Salidas: `p6_ciclo_T.csv` (una fila por banda, columnas con esos nombres, más `T_centro_C` = centro de la banda en °C) y `p6_ciclo_T.md` con una tabla llana (banda en °C, n, P(KALINA), eta máxima dentro del rango, P_alta y x_b
   del máximo) y una nota que diga que el máximo es el mayor valor muestreado (no hay optimizador), que las bandas con pocos KALINA (< 10) no concluyen y que NO_CONVERGIO sesga hacia abajo la P(KALINA) de las bandas frías.

## Parte 2 — hoja del libro (`s2_f4t.py`)

Crea `hoja_f4_ciclo_T(wb, datos)` y `HOJAS_F4T = [hoja_f4_ciclo_T]`, que genera la hoja **`F4 Ciclo vs T_fuente`**. **Copia el patrón de `scripts/sens2/s2_f6.py`** (imports, `titulo`, `condiciones` con una línea que empiece por «Base:»,
`subtitulo`, `tabla`, `bloque`, `nota`, `descripcion`, `numero`). Contenido, leído de `p6_ciclo_T.csv`:
1. Tabla completa por banda (todas las columnas relevantes, redondeadas con `numero(x, 3)`; celdas vacías como cadena vacía).
2. Gráfico de líneas con `bloque(..., tipo="linea", x_vals=<T_centro_C>)`: categoría = `T_centro_C` (°C) y series `eta_max_dentro`, `eta_p90` y `eta_mediana` (todas en %); solo las bandas con al menos 10 KALINA (filtra las filas antes).
3. Gráfico de barras con `bloque(...)`: categoría = banda en °C (texto), dos series `p_kalina` y `p_kalina_si_convergio` (para mostrar el efecto de NO_CONVERGIO en las bandas frías).
4. Nota: el máximo es el mayor valor muestreado y no el óptimo; el panorama de η frente a T_fuente se aplana desde ≈ 150 °C según los barridos de una variable (conclusión E8), sin afirmar nada que los datos no den.
Después de cada `tabla(...)` que no sea un `bloque`, haz `f += 1`. **Prueba**: en un proceso nuevo crea un `Workbook()`, quita la hoja inicial, llama a la función, `from x5_graficos import dibujar_todos; dibujar_todos(wb)`,
guarda en `resultados/2026-10-18_sens2_F1/_prueba_f4t.xlsx`, reabre con `openpyxl` y verifica que la hoja existe, que hay 2 gráficos, que no hay celdas vacías en las tablas de los gráficos y que no hay palabras prohibidas. Borra el `.xlsx` de prueba al terminar.

## Aceptación

Corre en menos de 2 minutos; cada archivo ≤ 200 líneas; reporta en RESULTS la tabla de `p6_ciclo_T.md` y el número de gráficos.

# TASK_CONTEXT — Sensibilidad 2, B1: calibración de la regla «distinguible» y M5 con dos pruebas (sin motor)

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy, openpyxl, pytest; **sin** scikit-learn ni yaml).
**Contexto:** plan en `docs/PLAN_SENS2_MEJORA.md`. Sin corridas del motor (el «motor» es el programa que calcula el ciclo; aquí solo se
analizan datos ya calculados). Otra tarea (B2) corre a la vez sobre OTROS archivos: **toca solo los archivos asignados** y no hagas
`git add`, `git commit`, `git stash`, `git checkout` ni `git reset` (el director commitea).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba archivos). PowerShell 5.1,
  sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. Cada `.py` máximo 200 líneas.
- Scripts nuevos en `scripts/sens2/`; importa con `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. Ejecuta desde la raíz:
  `..\..\..\.venv\Scripts\python.exe scripts\sens2\<script>.py`.
- **Terminología:** prohibido en toda salida: «confiable», «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol», «sin respaldo».
- Los umbrales salen de los datos o de este documento; no inventes ninguno. Semilla fija indicada. Si algo es ambiguo, repórtalo en `UNRESOLVED`.
  Reporte final en el formato de `AGENTS.md`.

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p6_calibra_regla.py` (nuevo), `scripts/sens2/p6_m5_pruebas.py` (nuevo) y las salidas
en `resultados/2026-10-18_sens2_F1/`: `p6_calibra_regla.csv`, `p6_calibra_regla.md`, `p6_m5_pruebas.csv`, `p6_m5_pruebas.md`.
**No toques** `p6_nulo.py`, `p6_m5_lhs.py`, `s2_construir.py` ni el libro; el director integra los resultados.

## Parte 1 — `p6_calibra_regla.py`: tasa de falsos positivos de la REGLA

Entrada: `resultados/2026-10-18_sens2_F1/p6_nulo_perm.csv` (columnas `caja, bloque, respuesta, variable, tipo` {real, dummy}, `metodo`,
`familia_metodo`, `n`, `obs`, `p_perm`, `q_bloque`, `q_respuesta`). La regla actual: una variable es «distinguible» si `q_bloque < 0.05`
en **al menos 2 métodos** (dentro de su bloque y respuesta). Filtra `caja == "no"` (la caja común está vacía/inviable; repórtalo si hay filas).
1. **Tasa de la regla en las dummy:** por bloque × respuesta, cuenta para cada variable `dummy` en cuántos métodos `q_bloque < 0.05`; la regla marca la dummy si ≥ 2.
   Reporta: n de dummies evaluadas, cuántas marca la regla, fracción (con IC de Wilson 95 %), en total y por respuesta (Y1, Y2, Y3). Repite con umbrales k = 1, 2, 3, 4
   métodos (tabla k → fracción de dummies marcadas y fracción de reales marcadas).
2. **Familia global:** aplica Benjamini–Hochberg a `p_perm` sobre TODAS las pruebas de todos los bloques y respuestas juntas (una sola familia,
   por método o con todos los métodos mezclados; haz ambas) y reporta cuántas variables reales siguen siendo «distinguibles» (≥ 2 métodos con q global < 0.05)
   frente a las que lo son con la regla por bloque (cuenta las de `q_bloque`). Entrega la tabla por bloque × respuesta: reales marcadas (por bloque), reales marcadas (global).
3. Salidas: `p6_calibra_regla.csv` (una fila por línea de las tablas anteriores, con columna `tabla` que las distingue) y `p6_calibra_regla.md` (explicación llana de 6-10 líneas:
   qué es una dummy, qué tasa de falsos positivos tiene la regla, qué pasa con la corrección global; sin juicios más fuertes que los datos). Imprime el resumen.

## Parte 2 — `p6_m5_pruebas.py`: M5 con KS y con Mann–Whitney

Copia el patrón de `scripts/sens2/p6_m5_lhs.py` (léelo; usa `p2_comun`, `p2_robustez.puntos_frontera`, normalizaciones `completo` y `lhs`). Para cada normalización y bloque
(C1..C4) calcula, sobre `dist_frontera` de `Top10` frente a `resto` (filas LHS, estudios 3 y 14): n, medianas, p de KS (`ks_2samp`) y p de Mann–Whitney
(`scipy.stats.mannwhitneyu`, alternativa `two-sided`), y cada p con Bonferroni (×4, tope 1). Salidas: `p6_m5_pruebas.csv` (columnas `normalizacion, bloque, n_top, n_resto, med_top, med_resto,
p_ks, p_ks_bonf, p_mw, p_mw_bonf`) y `p6_m5_pruebas.md` (tabla + 3 líneas: en cuántas de las 8 combinaciones sale p < 0.05 con cada prueba, sin y con Bonferroni). **Control:**
las columnas `p_ks` deben coincidir (tolerancia 1e-9) con las de `p6_m5_lhs.csv`; reporta si no.

## Aceptación

Ambos scripts corren en menos de 3 minutos; cada archivo ≤ 200 líneas; reporta en RESULTS: fracción de dummies marcadas por la regla (con IC), reales marcadas por bloque vs global,
y la tabla de M5 con las dos pruebas.

# TASK_CONTEXT — Campaña final, M4: sensibilidad global orientada a KALINA (LHS + RSA + PAWN + PRCC + CART)

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (scipy, numpy, pandas,
matplotlib y scikit-learn 1.9.1)
**Leer antes de empezar:**
- `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` §2 y §6 (fórmulas de LHS, RSA, PAWN, PRCC, CART y
  bootstrap);
- `scripts/barrido_final/comun.py` (`evaluar_punto(..., t_amb_diseno=...)` ya acepta el piso por
  punto);
- `scripts/barrido_final/m3_ofat.py` (patrón de pool y CSV).

**OJO:** en paralelo corre OTRA tarea de OpenCode (M2S). **No toques `comun.py` ni
`test_comun*.py`**, ni los archivos `m2s_*` ni `resultados/2026-10-06_final_M2S/`. Tampoco el Excel.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal (nada de heredocs, `Set-Content` ni `python -c` que escriba archivos).
- PowerShell 5.1: no existen `tee` ni `&&`. Para la corrida larga usa `Start-Process`
  redirigiendo stdout y stderr a archivos.
- Las verificaciones van en un script escrito con `write`. Lanza la corrida larga UNA sola vez.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py` ni ningún script existente.
- Cada `.py` debe tener como máximo 200 líneas: separa la corrida y el análisis en varios archivos.
- No inventar valores. No hacer commit.

## Pregunta

Moviendo **las 10 variables a la vez** dentro de rangos favorables y realistas:
- ¿qué variables deciden que el ciclo sea KALINA?
- ¿en qué rango hay que ponerlas?
- ¿qué combinaciones dan KALINA con mayor η?

## Caja de muestreo (fijada por el director, con su respaldo)

| Variable | Rango | Respaldo |
|---|---|---|
| T_fuente (K) | [380, 500] | KALINA de M2 entre 390 y 434 K; Elsayed 2013 con 373–463 K; Húsavík 394 K; Fase 2 con 470 K |
| T_sumidero (K) | [278.15, 303.55] | Húsavík 5 °C; Elsayed 283 K; clima del profesor 297.95–303.55 K |
| P_alta (kPa) | [2000, 5000] | Elsayed 10–40 bar; Húsavík 33 bar; Nemati 50 bar; KALINA previos 3000–5000 kPa; por encima de 5000, huecos de teqp |
| P_baja (kPa) | [300, 1500] | KALINA observados entre 445 y 1318 kPa; Húsavík 670–690 kPa |
| x_b (−) | [0.50, 0.85] | profesor 0.50; Elsayed "estable" 0.55–0.9; Húsavík 0.82; KALINA previos 0.60–0.80 |
| eta_t (−) | [0.75, 0.92] | Elsayed 0.80; profesor 0.85; Húsavík 0.90 |
| eta_p (−) | [0.65, 0.90] | Nguyen 0.70; profesor 0.75; Elsayed y Húsavík 0.80 |
| eps_hrvg (−) | [0.60, 0.95] | profesor 0.85; un ε_HRVG bajo solo hace falta con 623 K (M2R) |
| eps_reg (−) | [0.60, 0.95] | M3: KALINA desde 0.72; la mejor η con 0.95 |
| eps_cond (−) | [0.70, 0.95] | Húsavík 0.95; profesor 0.80; M3: KALINA desde 0.79 |

- `m_b = 1.0`.
- **El piso de O2 sigue al clima:** `evaluar_punto(combo, motor="teqp", tag=..., t_amb_diseno=combo["T_sumidero"])`.
- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
  `convergio=True` y `NO_CONVERGIO` es espuria (N2) y es NO genuina en todo.

## Diseño

1. **Muestreo:** `scipy.stats.qmc.LatinHypercube(d=10, seed=20261006)`, con **N = 300**, escalado
   a la caja con `qmc.scale`. Se guarda la matriz en `m4_muestra.csv` ANTES de correr.
2. **Corrida:** las 300 corridas en `ProcessPoolExecutor(max_workers=5)`. Cada fila se escribe con
   flush en `resultados/2026-10-06_final_M4/m4_lhs.csv`, con la columna `id_muestra` más las de
   `COLS`. Se imprime `[n/300] clase eta t_s`.
3. **Variables derivadas**, que se añaden en el análisis:
   - `dP = P_alta − P_baja`;
   - `rP = P_alta/P_baja`;
   - `dT_fs = T_fuente − T_sumidero`.

## Análisis (sobre el CSV; se puede volver a ejecutar sin recalcular)

Fórmulas de MATEMATICA §6.

- **RSA:** grupo B = KALINA y B̄ = el resto. Para las 10 variables y las 3 derivadas:
  - `KS_i`, `p_valor` (`scipy.stats.ks_2samp`) e IC95 % por bootstrap (1000 remuestreos, semilla fija);
  - el rango favorable = percentiles 5–95 de la variable dentro de B.

  Se repite con las separaciones `converge` (genuino vs no genuino), `cumple_O2` (entre genuinos)
  y `cumple_O1` (entre genuinos). Salida: `m4_rsa.csv`.
- **Requisito:** si |B| < 20, **no** se amplía el muestreo por cuenta propia. Se reporta
  explícitamente en el reporte y en UNRESOLVED; el director decide.
- **PAWN** (10 franjas, mediana y máximo de KS) sobre η de los genuinos con W_net > 0, y sobre D
  de los genuinos. Salida: `m4_pawn.csv`.
- **PRCC** (rangos, residuos de regresión lineal y prueba t) sobre η (genuinos con W_net > 0) y
  sobre `m_O1`, `m_O2` y `m_O5` (genuinos). Salida: `m4_prcc.csv`.
- **CART** (`sklearn.tree.DecisionTreeClassifier`, `max_depth=4`, `min_samples_leaf=5`,
  `random_state=0`) para KALINA vs no. Se reporta la exactitud con validación cruzada de 5
  particiones y se exportan las reglas con `export_text` a `m4_cart.txt`.
- **Convergencia:** se recalculan KS (RSA KALINA) y PRCC(η) con los primeros 150 puntos y se
  compara el ranking con el de los 300 mediante el ρ de Spearman. Salida: `m4_convergencia.csv`.
- **Top KALINA:** los 10 KALINA de mayor η, con sus 10 variables. Salida: `m4_top_kalina.csv`.

## Figuras

- `m4_cdf_kalina.png`: las CDF de B y de B̄ para cada variable, con el KS en el título.
- `m4_prcc_eta.png`: barras de PRCC sobre η, con su IC.
- `m4_rsa_ks.png`: barras de KS por variable, para la separación KALINA.
- `m4_cart.png`: el árbol (`sklearn.tree.plot_tree`).

## Reporte `REPORTE_M4.md` (lenguaje llano)

1. La pregunta.
2. Qué se hizo, en simple.
3. Cuántos KALINA salieron, con sus conteos por clase.
4. **Qué variables deciden KALINA y su rango favorable** (tabla del RSA ordenada por KS, con su IC
   y su valor p).
5. Qué variables mueven η y en qué sentido (PAWN y PRCC).
6. Las reglas del árbol, en palabras.
7. Los diferenciales recomendados (dP, rP y dT_fs) dentro de KALINA.
8. Los 10 mejores KALINA.
9. La convergencia (si el ranking es estable).
10. Los tiempos.
11. La conclusión.
12. Lo que no se sabe:
    - las diferencias de η menores que 0.4–0.7 pp;
    - los puntos fuera de rango;
    - que es una caja favorable, no todo el espacio.
13. Qué sigue (M5, lo decide el director).

## Pasos

1. Crear `scripts/barrido_final/m4_corrida.py`, `m4_analisis.py` y, si hace falta,
   `m4_reporte.py`, todos con como máximo 200 líneas.
2. Humo con `M4_HUMO=1`: N = 6, con salida en `.../2026-10-06_final_M4/humo/` (el análisis puede
   reportar que no hay datos suficientes).
3. Corrida real (N = 300) y después el análisis y el reporte.
4. Verificación con un script escrito con `write`:
   - que `m4_muestra.csv` y `m4_lhs.csv` coincidan;
   - que se cumpla la propiedad LHS (un punto por franja en cada variable);
   - que el KS de 2 variables, recalculado a mano, coincida;
   - que los números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.

# TASK_CONTEXT — Sensibilidad 1, Fase C (muestreo LHS de 9 variables, 2 centros)

**Fecha:** 2026-10-14 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (trae scipy 1.18 con
`scipy.stats.qmc`, numpy y pandas; **no** trae scikit-learn: no lo uses).
**Base de código a copiar:** `scripts/sens1/faseB_corrida.py` (corrida con `evaluar_punto(extra=True)`,
5 procesos, escritura incremental).

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: usa solo ASCII en los `print`.
- **La corrida del paso 2 tarda ~1 h. Pasa `timeout=7200000` a la herramienta de shell.** En primer plano,
  sin `Start-Process`, no la relances si tarda.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas (divide en dos o tres si hace falta).
- No inventes valores; lo que falte, a UNRESOLVED.
- Cada número del reporte debe salir de un archivo generado en esta tarea.
- `m_b = 1.0`, `η_p` fijo, `t_amb_diseno = T_sumidero` del punto, motor `teqp`, `extra=True`.
- No sobrescribas archivos de las Fases 0, A y B.

## Objetivo

Con las fases A y B ya se conocen las ventanas de cada variable y de cada par. Aquí se mueven **9
variables a la vez** dentro de una caja alrededor de cada centro, con un muestreo de hipercubo latino
(LHS), para responder: dentro de qué rangos conjuntos sigue habiendo KALINA, qué variables lo
controlan, y qué rangos de η y de equipos resultan.

## Paso 1 — `scripts/sens1/faseC_corrida.py`

**Muestreo:** `scipy.stats.qmc.LatinHypercube(d=9, seed=20261014)` por centro, **250 puntos por centro**
(500 en total). Escala cada columna al rango de la tabla y luego **redondea** así:
temperaturas a 0.5 K, presiones a 10 kPa, `x_b` a 0.01, y **eficiencias/efectividades al múltiplo de 0.05
más cercano** (regla del usuario: paso 0.05). Elimina duplicados exactos tras redondear (si quedan menos de
250, repórtalo).

| Variable | C1 Húsavík | C2 A\* |
|---|---|---|
| T_fuente [K] | 363.15–443.15 | 393.15–463.15 |
| T_sumidero [K] | 278.15–288.15 | 278.15–303.15 |
| P_alta [kPa] | 2000–5000 | 2000–4000 |
| P_baja [kPa] | 500–1300 | 400–1200 |
| x_b | 0.55–0.95 | 0.40–0.65 |
| η_t | 0.50–0.95 | 0.50–0.95 |
| ε_HRVG | 0.50–0.95 | 0.50–0.95 |
| ε_reg | 0.50–0.95 | 0.50–0.95 |
| ε_cond | 0.80–0.95 | 0.70–0.95 |

**Fijos:** `η_p` = 0.80 (C1) y 0.75 (C2); `m_b` = 1.0.

Cada fila lleva además `id_punto` (`C1-LHS-0001`), `centro` y `tipo = "lhs"`. Salidas en
`resultados/2026-10-14_sens1_faseC/`: `faseC_filas.csv` (columnas de `COLS` + `COLS_EXTRA` + las 3
anteriores; escritura incremental con `flush`) y `faseC_log.txt`. Crea la carpeta desde el script.

## Paso 2 — Ejecutar la corrida

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseC_corrida.py 2>&1 | Tee-Object -FilePath resultados\2026-10-14_sens1_faseC\faseC_log.txt
```

## Paso 3 — `scripts/sens1/faseC_reporte.py` (+ `faseC_reporte2.py` si pasa de 200 líneas)

Lee `faseC_filas.csv` y escribe en `resultados/2026-10-14_sens1_faseC/`:

1. **`faseC_resumen_centros.csv`**: por centro, nº de puntos, nº por clase, nº de KALINA, nº de KALINA
   confiables, % de KALINA, η mínimo / mediana / máximo entre los confiables.
   **KALINA confiable:** clase KALINA, `fuera_rango` falso/vacío, y todos los `eta_*`, `eps_*` en
   [0.40, 0.95].
2. **`faseC_ventanas.csv`**: por centro y variable, entre los KALINA confiables: mínimo, p10, mediana,
   p90, máximo; y, entre los no KALINA, los mismos percentiles, para ver qué se solapa.
3. **`faseC_ks.csv`** (filtrado Monte Carlo, RSA): por centro y variable, el estadístico de
   Kolmogorov-Smirnov (`scipy.stats.ks_2samp`) entre la distribución de la variable en KALINA confiables
   y en los demás puntos genuinos (convergio=True y clase ≠ NO_CONVERGIO), con su p-valor; ordenado de
   mayor a menor.
4. **`faseC_prcc.csv`**: por centro, el coeficiente de correlación parcial por rangos (PRCC) de cada
   variable con η, **solo sobre los KALINA confiables**. Cálculo: transforma las 9 variables y η a
   rangos; para cada variable, regresa su rango y el rango de η contra los rangos de las otras 8
   (mínimos cuadrados con numpy) y correlaciona los residuos (Pearson). Ordenado por |PRCC|.
5. **`faseC_top10.csv`**: por centro, los 10 KALINA confiables de mayor η con sus 9 variables.
6. **`faseC_equipos.csv`**: por centro, mín / mediana / máx entre KALINA confiables de `dh_turb` [kJ/kg],
   `Wnet/m_b`, `Qin = Qi/m_b`, `Qreg/Qi`, `Qout/m_b`, `P_alta/P_baja`, `m_O2`.
7. **`faseC_resumen.md`** con las tablas anteriores en lenguaje llano y una frase de conclusión por
   centro: ventana conjunta (p10–p90) de las variables entre los KALINA, las 3 variables con mayor KS y
   las 3 con mayor |PRCC|.

## Paso 4 — Ejecutar el reporte

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseC_reporte.py
```

(Y `faseC_reporte2.py` si existe.)

## Paso 5 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS pega: nº de puntos por centro y clase, nº de KALINA
confiables, las 3 variables con mayor KS y mayor |PRCC| por centro, y las ventanas p10–p90, tal como
salieron de los archivos.

# TASK_CONTEXT — Sensibilidad 1, Ronda 3 de barridos nuevos (N9, N10, N8)

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa desde aquí):** `..\..\..\.venv\Scripts\python.exe` (scipy 1.18 con `qmc`, numpy,
pandas; **sin** scikit-learn).
**Código a copiar (no reinventar):** `scripts/sens1/ronda2_puntos.py`, `ronda2_corrida.py`,
`ronda2_reporte.py`, `ronda2_reporte2.py` (un proceso por punto, 5 simultáneos, tope duro de 600 s,
reanudable por barrido, modo `a`) y `scripts/sens1/faseC_corrida.py` (muestreo LHS y redondeo). Usa
`scripts/barrido_final/comun.py::evaluar_punto(..., extra=True)`.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal** (el sandbox las rechaza y aborta toda la
  ejecución). Usa rutas relativas e intérprete `..\..\..\.venv\Scripts\python.exe`.
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`.
- **Cada corrida larga con `timeout=7200000` en la herramienta de shell, en primer plano, sin
  `Start-Process`**. La corrida es **por barrido** y reanudable: si una invocación se corta, relanza el MISMO
  comando. **NO ejecutes `pytest`.** No abras los CSV completos con un volcado: usa pandas dentro de scripts.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, ni archivos de fases, rondas o
  del Excel anteriores. Cada `.py`: máximo 200 líneas (`ronda3_puntos.py`, `ronda3_corrida.py`,
  `ronda3_reporte.py`, `ronda3_reporte2.py`).
- No inventes valores; lo que falte, a UNRESOLVED. Cada número del reporte sale de un archivo generado.
- **Reglas del usuario:** T_fuente 70–300 °C; eficiencias y efectividades 0.40–0.95 con paso 0.05;
  T_sumidero 5–30 °C (278.15–303.15 K); `m_b = 1.0`; `t_amb_diseno = T_sumidero` del punto; motor `teqp`;
  `extra=True`. Se conservan todas las clases.
- **Terminología:** «KALINA (total)», «dentro del rango experimental», «fuera del rango experimental
  (líquido > 420 K)». Prohibido: «confiable», «no citable», «fuera de rango del motor», «extrapolación».

## Centros (valores EXACTOS; `η_p = 0.80`, `m_b = 1.0`, η_t 0.85, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95)

| Centro | T_fuente [K] | T_sumidero [K] | P_alta | P_baja | x_b |
|---|---|---|---|---|---|
| C1 Húsavík | 394.15 | 278.15 | 3300 | 690 | 0.82 |
| C3 caliente 150 °C | 423.15 | 280.5 | 3150 | 950 | 0.75 |
| C4 frío 110 °C | 383.15 | 282.5 | 3880 | 910 | 0.88 |

## Paso 1 — `ronda3_puntos.py` y `ronda3_corrida.py` (argumento `N9`, `N10`, `N8` o `all`)

Cada punto lleva `id_punto`, `barrido`, `centro`, `par`/`variable` y el `combo` de las 10 variables + `m_b`.
Elimina duplicados por (barrido, centro, combinación). Salidas en
`resultados/2026-10-16_sens1_ronda3/`: `ronda3_filas.csv`, `ronda3_log_<barrido>.txt`, `ronda3_diseno.csv`,
`ronda3_descartes.csv`.

### N9 — Pares del regenerador y la turbina en C3 y C4 (196 puntos)

Para C3 y C4, dos mallas 7 × 7 (el resto en el valor del centro; **b** = valor del centro):

| Par | Variable 1 | Variable 2 |
|---|---|---|
| B5 | ε_reg ∈ {0.50, 0.60, 0.70, 0.75**b**, 0.80, 0.90, 0.95} | η_t ∈ {0.50, 0.60, 0.70, 0.80, 0.85**b**, 0.90, 0.95} |
| B6 | ε_HRVG ∈ {0.50, 0.60, 0.70, 0.80, 0.85**b**, 0.90, 0.95} | T_fuente [°C]: C3 {110, 130, 140, 150**b**, 160, 180, 200}; C4 {80, 90, 100, 110**b**, 120, 135, 150} (sumar 273.15) |

`id_punto = N9-{centro}-{par}-{nnnn}`. El punto base se evalúa una vez por centro (`par="base"`).

### N10 — Extensión de P_alta más allá de 5000 kPa (105 puntos)

La η máxima de C3 (14.4 %) cayó en el borde de la caja, P_alta = 5000 kPa. Para C1, C3 y C4, malla 5 × 7:

- P_alta ∈ {4000, 5000, 6000, 7000, 8000} kPa.
- P_baja: C1 {500, 600, 690**b**, 800, 950, 1100, 1300}; C3 {500, 650, 800, 950**b**, 1100, 1300, 1600};
  C4 {500, 650, 800, 910**b**, 1050, 1250, 1500}.

`id_punto = N10-{centro}-{nnnn}`. (Nota: el límite de presión de la ecuación es 40 MPa; no se espera
cruzar el lugar crítico a 8 MPa, pero no se vigila: lo que salga como NO_CONVERGIO o INVIABLE queda como
resultado.)

### N8 — Muestreo LHS de 9 variables en C3 y C4 (hasta 500 puntos)

`scipy.stats.qmc.LatinHypercube(d=9, seed=20261017)` por centro, **250 puntos por centro**. Variables en el
orden T_fuente, T_sumidero, P_alta, P_baja, x_b, η_t, ε_HRVG, ε_reg, ε_cond (η_p = 0.80 y m_b = 1 fijos).
Redondeo: temperaturas a 0.5 K, presiones a 10 kPa, x_b a 0.01, eficiencias al múltiplo de 0.05 más
cercano. Descarta (no resamplees) los puntos con `P_alta < 1.3 × P_baja` y repórtalo. Elimina duplicados
tras redondear.

| Variable | C3 caliente | C4 frío |
|---|---|---|
| T_fuente [K] | 363.15–463.15 | 353.15–423.15 |
| T_sumidero [K] | 278.15–295.65 | 278.15–290.65 |
| P_alta [kPa] | 1500–5000 | 1500–5000 |
| P_baja [kPa] | 500–1800 | 700–1800 |
| x_b | 0.40–0.95 | 0.55–0.95 |
| η_t, ε_HRVG, ε_reg | 0.50–0.95 | 0.50–0.95 |
| ε_cond | 0.85–0.95 | 0.85–0.95 |

`id_punto = N8-{centro}-{nnnn}`.

## Paso 2 — Ejecutar (en este orden, cada comando en primer plano con `timeout=7200000`)

```
..\..\..\.venv\Scripts\python.exe scripts\sens1\ronda3_corrida.py N9
..\..\..\.venv\Scripts\python.exe scripts\sens1\ronda3_corrida.py N10
..\..\..\.venv\Scripts\python.exe scripts\sens1\ronda3_corrida.py N8
```

(Redirige a `ronda3_log_<barrido>.txt` con `2>&1 | Tee-Object -FilePath ...`.) Antes de correr, verifica el
conteo de `ronda3_diseno.csv` (N9 ≈ 196, N10 = 105, N8 ≤ 500) y repórtalo. Estimo ~3.5 h en total.

## Paso 3 — Reporte (`ronda3_reporte.py`, `ronda3_reporte2.py`)

Un punto **dentro del rango experimental** es KALINA sin la marca `fuera_rango` y con η/ε en [0.40, 0.95].
Escribe en `resultados/2026-10-16_sens1_ronda3/`:

1. `ronda3_resumen_barridos.csv`: por barrido y centro: puntos, clases, KALINA (total), dentro, fuera, η
   mín/mediana/máx entre KALINA (total) y entre los de dentro.
2. **N9**: matrices 7 × 7 de clase (K/c/n/i) y de η [%] por centro y par; nº de KALINA por par **contando
   el base**; el KALINA de mayor η por par.
3. **N10**: matriz 5 × 7 de clase y de η [%] por centro; si la η máxima de cada centro sigue subiendo con
   P_alta o tiene un máximo interior (di en qué P_alta).
4. **N8**: por centro, ventanas p10–p90 de las 9 variables entre los KALINA (total), KS de cada variable
   (KALINA frente al resto de puntos genuinos, `scipy.stats.ks_2samp`), PRCC con η entre los KALINA (rangos
   y residuos con numpy), top 10 de η, y rangos de equipos (Δh de turbina, Wnet por kg/s, Qreg/Qi, r_P).
5. `ronda3_resumen.md` con lo anterior en lenguaje llano.

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: puntos planeados vs. evaluados por barrido, clases, KALINA
(total, dentro y fuera) por barrido y centro, nº con tiempo agotado y las tablas de N9 y N10 tal como
salieron de los archivos.

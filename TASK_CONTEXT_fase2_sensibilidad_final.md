---
project: ciclo_kalina_tercero
task_id: 2026-09-20-fase2-sensibilidad-final
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Fase 2: barrido de sensibilidad FINAL (OFAT + malla 2D)

## Task ID

2026-09-20-fase2-sensibilidad-final

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente`. **Corre en paralelo con
`TASK_CONTEXT_fase3_sensibilidad_final.md` (otra sesión, trabaja solo en
`scripts/barridos_2026-09-19/fase3_real/` y prefijo `fase3_` en figuras) — no la toques.**

Esta es la tarea FINAL de Fase 2: ya no es exploración, es el análisis de sensibilidad que
se va a reportar. El candidato base ya está confirmado con el motor real
(`resultados/barridos_2026-09-19/fase2_libre/confirmacion_motor_real_v2.json`) y el rango de
`eps_hrvg` ya fue corregido con evidencia
(`resultados/barridos_2026-09-19/fase2_libre/PRESCAN_EPS_HRVG.md`,
`BASE_LIBRE_v2.md` §3 ya actualizado).

## MUY IMPORTANTE — motor de propiedades

**Todo el barrido (OFAT y malla 2D) se corre con `TeqpAdapter`, NUNCA con
`AmmoniaWaterAdapter`** para el grueso de los puntos — es una instrucción explícita del
director. El motor real solo se usa para el spot-check selectivo de puntos cercanos a una
frontera de clasificación (ver más abajo), no para el barrido completo. El punto ancla YA
está confirmado con motor real — cítalo, no lo vuelvas a correr.

## Base/centro confirmado (NO cambies estos valores)

`P_alta=3000, P_baja=400, x_b=0.40, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95, T_amb_diseno=303.55`
→ KALINA, η=0.124296 (motor real, ya confirmado, cítalo).

## Objective

1. **5 barridos OFAT** (uno a la vez, el resto de variables fijas en el centro), ~7 puntos
   cada uno, usando `Fijo`/`Barrido` + `ejecutar_barrido`/`tabla_barrido` de
   `src/sensitivity.py` (API ya validada, NO la modifiques, solo impórtala):
   - `x_b`: 0.35 – 0.45
   - `P_baja`: 400 – 500 kPa
   - `eps_cond`: 0.85 – 0.95
   - `eta_t`: 0.80 – 0.90
   - `eps_hrvg`: **0.80 – 0.99** (rango corregido, ver `PRESCAN_EPS_HRVG.md` — el original
     0.80-0.90 no llegaba a ninguna frontera; este sí bracketea la frontera S5 esperada cerca
     de 0.99, así que espera puntos KALINA e INVIABLE/NO_CONVERGIO en este barrido, regístralos
     igual, no es un error)
   ≈35 puntos.
2. **1 malla 2D** `P_baja × eps_cond` (6×6 = 36 puntos, resto en el centro) — el par que
   gobierna juntos el criterio O2 (cavitación), para mapear la frontera KALINA/CORREGIBLE
   como región 2D, no solo como dos líneas independientes.
3. **Confirmación selectiva con motor real**: para cualquier punto (de los 5 OFAT o de la
   malla) cuyo margen del criterio que decide la clasificación (O1: q4-0.90, o O2:
   T_sat_L-T9_amb, o S5: T_fuente-T2) esté a menos de ~1-2 K (o 0.02 en q2/q4) del borde,
   re-resuélvelo con `AmmoniaWaterAdapter` y añade una columna `motor_confirmado`
   (`True`/`False`/`None` si no aplicaba) al CSV correspondiente. Esperamos que sean pocos
   puntos (quizás 3-8 en total) — NO conviertas esto en un segundo barrido completo con motor
   real.

## Entregables

Todo bajo `resultados/barridos_2026-09-19/fase2_libre/` (CSVs/JSON) y
`resultados/barridos_2026-09-19/figuras/` (PNG, con prefijo `fase2_` para no chocar con Fase 3):

- **A — Tablas del punto ancla** (puedes usar/adaptar `ui_helpers.tabla_estados` importándola,
  o construir el equivalente a mano si es más simple para un script suelto):
  - `resultados/barridos_2026-09-19/fase2_libre/ancla_estados.csv` (los 10 estados: T,P,h,s,x,m,q,fase)
  - `resultados/barridos_2026-09-19/fase2_libre/ancla_balance.csv` (Qi,Qout,Wt,Wp,Wnet,eta +
    verificación de cierre N2: |Qi-Qout-Wnet| vs 1e-3*Qi)
- **B — Por cada una de las 5 variables OFAT**:
  - `sensibilidad_<var>.csv` (columnas de `tabla_barrido` + margen del criterio ligante +
    `motor_confirmado`)
  - `fase2_sensibilidad_<var>.png`: η vs la variable, puntos coloreados por clasificación
    (KALINA=verde `#2ca02c`, CORREGIBLE=ámbar `#ff7f0e`, cualquier otra
    [INVIABLE/DEGENERADO/NO_CONVERGIO/VALIDO_ADVERTENCIA]=rojo `#d62728`), con leyenda.
    Usa `matplotlib.figure.Figure` directo (sin pyplot global), estilo consistente con
    `src/plots.py` (título y ejes en español con unidades, grid alpha 0.3), `fig.savefig(...)`.
- **C — Malla 2D**:
  - `mapa_2d_pbaja_epscond.csv` (P_baja, eps_cond, clasificacion, eta, O2_margen)
  - `fase2_mapa_2d_pbaja_epscond.png`: heatmap o contorno de la clasificación (categórica) en
    el plano P_baja × eps_cond, con la frontera KALINA/CORREGIBLE visible.
- **D (parcial)**: `resumen_fase2.json` con
  `{"fase": "2_libre", "clasificacion_ancla": "KALINA", "eta_ancla": 0.124296,
  "leccion_aprendida": "<una frase>"}`.

## Files

Scripts nuevos en `scripts/barridos_2026-09-19/fase2_libre/` (sufijo `_sensibilidad`/`_ofat`/
`_2d`, ≤200 líneas/archivo — divide en varios archivos si hace falta, sigue el patrón de
paralelismo/checkpointing de `busqueda_libre_v2.py` ya existente en esa carpeta).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni `scripts/barridos_2026-09-19/fase3_real/`
ni `fase1_profesor/`. **NO sobrescribas** ningún archivo `_v2` existente ni `PRESCAN_EPS_HRVG.md`.

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Solo `TeqpAdapter` para el barrido; motor real SOLO para los spot-checks descritos arriba
   y el punto ancla (ya confirmado, no re-correr).
3. Presupuesto: ~150-250 puntos Teqp total (35 OFAT + 36 malla + margen); motor real: no más
   de ~10 puntos de spot-check.
4. Todo punto probado se registra igual, converja o no.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: conteo de clasificaciones por barrido, y confirma que las
figuras PNG se generaron y abren sin error.

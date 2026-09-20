---
project: ciclo_kalina_tercero
task_id: 2026-09-20-fase3-sensibilidad-final
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Fase 3 (Húsavík): barrido de sensibilidad FINAL (OFAT + malla 2D)

## Task ID

2026-09-20-fase3-sensibilidad-final

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente`. **Corre en paralelo con
`TASK_CONTEXT_fase2_sensibilidad_final.md` (otra sesión, trabaja solo en
`scripts/barridos_2026-09-19/fase2_libre/` y prefijo `fase2_` en figuras) — no la toques.**

Esta es la tarea FINAL de Fase 3. El ancla `P_baja=690 kPa, eps_reg=0.75` ya quedó
confirmada con el motor real
(`resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real_690.json`,
`CASO_HUSAVIK_v2.md` §1 ya actualizado con esto como ancla final).

## MUY IMPORTANTE — motor de propiedades

**Todo el barrido (OFAT y malla 2D) se corre con `TeqpAdapter`, NUNCA con
`AmmoniaWaterAdapter`** para el grueso de los puntos — instrucción explícita del director. El
motor real solo para el spot-check selectivo de puntos cerca de una frontera (ver abajo). El
punto ancla YA está confirmado con motor real — cítalo (η=0.12730), no lo vuelvas a correr.

## Base/centro confirmado (NO cambies estos valores)

`P_alta=3300, P_baja=690, x_b=0.82, T_fuente=394.15, T_sumidero=278.15, m_b=1.0, eta_t=0.90,
eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95, T_amb_diseno=283.15`
→ KALINA, η=0.12730 (motor real, confirmado, cítalo).

## Objective

1. **5 barridos OFAT** (uno a la vez, resto fijo en el centro), ~7 puntos cada uno, con
   `Fijo`/`Barrido` + `ejecutar_barrido`/`tabla_barrido` de `src/sensitivity.py` (API ya
   validada, NO la modifiques):
   - `P_baja`: 600 – 800 kPa
   - `eps_cond`: 0.90 – 0.99
   - `eps_reg`: 0.75 – 0.95
   - `x_b`: 0.78 – 0.86
   - `eta_t`: 0.85 – 0.95
   ≈35 puntos.
2. **1 malla 2D** `P_baja × eps_reg` (6×6 = 36 puntos, resto en el centro) — el par crítico
   de O2 en este caso (ya vimos en la exploración que `eps_reg` también afecta si se pasa O2
   en algunos puntos, junto con `P_baja`).
3. **Confirmación selectiva con motor real**: cualquier punto (OFAT o malla) con margen del
   criterio ligante (O1, O2, o S5 si aplica) a menos de ~1-2 K del borde, re-resuélvelo con
   `AmmoniaWaterAdapter`, columna `motor_confirmado` en el CSV. Esperado: pocos puntos
   (3-8), NO un segundo barrido completo.

## Entregables

Todo bajo `resultados/barridos_2026-09-19/fase3_real/` (CSVs/JSON) y
`resultados/barridos_2026-09-19/figuras/` (PNG, prefijo `fase3_`):

- **A — Tablas del punto ancla**:
  - `resultados/barridos_2026-09-19/fase3_real/ancla_estados.csv` (10 estados)
  - `resultados/barridos_2026-09-19/fase3_real/ancla_balance.csv` (Qi,Qout,Wt,Wp,Wnet,eta +
    verificación N2)
- **B — Por cada una de las 5 variables OFAT**:
  - `sensibilidad_<var>.csv` (esquema `tabla_barrido` + margen del criterio ligante +
    `motor_confirmado`)
  - `fase3_sensibilidad_<var>.png`: η vs variable, coloreado por clasificación (KALINA=verde
    `#2ca02c`, CORREGIBLE=ámbar `#ff7f0e`, otra=rojo `#d62728`), mismo estilo que
    `src/plots.py` (`matplotlib.figure.Figure` directo, español, grid alpha 0.3).
- **C — Malla 2D**:
  - `mapa_2d_pbaja_epsreg.csv` (P_baja, eps_reg, clasificacion, eta, O2_margen)
  - `fase3_mapa_2d_pbaja_epsreg.png`: heatmap/contorno de clasificación.
- **D (parcial)**: `resumen_fase3.json` con
  `{"fase": "3_husavik", "clasificacion_ancla": "KALINA", "eta_ancla": 0.12730,
  "leccion_aprendida": "<una frase>"}`.

## Files

Scripts nuevos en `scripts/barridos_2026-09-19/fase3_real/` (sufijo `_sensibilidad`/`_ofat`/
`_2d`, ≤200 líneas/archivo, sigue el patrón de `busqueda_husavik_v2.py`).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni `scripts/barridos_2026-09-19/fase2_libre/`
ni `fase1_profesor/`. **NO sobrescribas** ningún archivo `_v2`/`_690` existente.

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Solo `TeqpAdapter` para el barrido; motor real SOLO para spot-checks + ancla ya confirmada.
3. Presupuesto: ~150-250 puntos Teqp total; motor real: no más de ~10 puntos.
4. Todo punto probado se registra igual, converja o no.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: conteo de clasificaciones por barrido, confirmar que las
figuras se generaron sin error.

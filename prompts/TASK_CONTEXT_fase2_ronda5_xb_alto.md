---
project: ciclo_kalina_tercero
task_id: 2026-09-29-fase2-ronda5-xb-alto
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-29
---

# TASK_CONTEXT — Fase 2 Ronda 5: explorar x_b alto (0.70-0.85), vigilando O1 Y O2

## Task ID

2026-09-29-fase2-ronda5-xb-alto

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Quinta ronda de Fase 2. Las rondas
1-4 exploraron `x_b` en [0.35, 0.50] (797 filas en
`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`). El paper externo
Karimi & Ahmad (2016) — ver
`resultados/barridos_2026-09-19/fase2_libre/` o pregunta si hace falta el resumen — reporta
que la zona de MAYOR eficiencia de un KCS-11 real está en `x_b=0.75-0.85`, región que nunca
hemos tocado en Fase 2. Objetivo de esta ronda: explorarla.

## Lección aprendida de la Ronda 4 (spot-check ya hecho, LÉELA con cuidado)

`resultados/barridos_2026-09-19/fase2_libre/spotcheck_ronda4_motor_real.json` ya confirmó
con motor real 10 puntos KALINA de la Ronda 4: **8/10 coincidieron casi exactamente con
Teqp** (confiable), pero:
1. **2/10 el motor real dio `NO_CONVERGIO`** aunque Teqp decía KALINA — ambos casos con
   `x_b=0.40-0.45` y `P_baja` relativamente bajo (<1100 kPa). El motor real tiene un dominio
   más estrecho que Teqp ahí.
2. **El criterio que de verdad limita estos puntos NO es solo O2, es O1** (calidad de vapor
   de turbina, `q4≥0.90`) — en varios de los 8 confirmados, el margen de O1 real era muy
   estrecho (hasta q4=0.9436, margen 0.04). **Esta ronda debe registrar y vigilar el margen
   de O1 explícitamente, no solo el de O2**, algo que las rondas 1-4 no hicieron de forma
   sistemática.

## MUY IMPORTANTE — reglas (mismas de la Ronda 4, con un añadido)

1. **Ancla fija**: `T_fuente=470.0 K`, `T_sumidero=300.032917 K`.
2. **`x_b` en [0.70, 0.85]** (región nueva, nunca explorada en Fase 2) — paso 0.025 o 0.05,
   tu criterio.
3. **Efectividades en [0.75, 0.85]** (`eps_hrvg`, `eps_reg`, `eps_cond`) — sin cambios.
4. **`eta_t` 0.80-0.90, `eta_p` 0.70-0.80** — sin cambios.
5. **`P_baja` es la palanca principal** para cerrar O2 — con `x_b` tan alto (mezcla rica en
   NH3), es probable que el punto de burbuja a `P_baja` moderado sea bajo, así que puede que
   necesites explorar un rango de `P_baja` amplio (usa lo aprendido de la Ronda 4 sobre la
   forma de la frontera para no perder tiempo en zonas evidentemente CORREGIBLE).
6. **`P_alta`**: puedes variar 2800-3300 kPa como en rondas previas, PERO si al explorar ves
   que subir `P_alta` más allá de 3300 (hasta un techo de 4500 kPa, dentro de lo citado por
   Karimi & Ahmad como rango de la literatura — NO subas más de eso sin autorización) ayuda
   a encontrar KALINA donde antes no lo había, repórtalo como hallazgo pero NO lo conviertas
   en el eje principal de esta ronda sin decirlo explícitamente en el reporte.
7. **NUEVO — registra el margen de O1 (`margen_O1` = q4−0.90) en cada punto**, además del de
   O2, en las columnas nuevas que agregues (ver esquema abajo). Si algún punto queda KALINA
   con `margen_O1 < 0.05`, márcalo como "al filo de O1" en el mensaje o una columna aparte.
8. **Motor: TeqpAdapter para el grueso**, pero esta vez SÍ hagas un **spot-check con motor
   real de 5-8 puntos** (los KALINA de menor margen combinado O1/O2), aplicando la misma
   lección de la Ronda 4 — no se repite el hueco de no verificar nada.
9. **No repitas combinaciones ya evaluadas** — lee TODOS los CSV de `fase2_libre/` (incluidas
   las 797 filas ya en `busqueda_libre_v2.csv`) antes de generar candidatas nuevas.
10. **`T_amb_diseno=303.55`** sin cambios.

## MUY IMPORTANTE — dónde guardar

**NO crees ningún CSV nuevo para el barrido.** Agrega (append) las filas nuevas al final de
`busqueda_libre_v2.csv`, mismo esquema de 19 columnas (lee la cabecera real). Si necesitas
columnas adicionales para `margen_O1`, agrégalas de forma retrocompatible (si el CSV no las
tenía antes, decide tú si las agregas a todo el archivo con `NaN` en las filas viejas, o si
las llevas en un CSV/JSON aparte SOLO para esta ronda — documenta la decisión).

El spot-check de motor real de esta ronda sí puede ir en un JSON nuevo (mismo patrón que
`spotcheck_ronda4_motor_real.json`): `spotcheck_ronda5_motor_real.json`.

## Files

Scripts nuevos en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej. `ronda5_xb_alto.py`,
≤200 líneas cada uno, puedes reusar patrones de `ronda4_columnas.py`/`ronda4_campana.py`).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, otras carpetas de
`scripts/barridos_2026-09-19/`/`resultados/barridos_2026-09-19/` fuera de `fase2_libre/`.

## Constraints

1. Cada script ≤200 líneas.
2. Cero puntos repetidos.
3. Todo punto se registra, converja o no.
4. Checkpointing por lotes (lección de rondas anteriores).
5. Presupuesto: ~300-600 puntos Teqp (más acotado que la Ronda 4, no necesitas 3h — esta
   región es más pequeña) + 5-8 puntos motor real.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: cuántos KALINA nuevos, su rango de η (compáralo con las
rondas 1-4), cuántos quedan "al filo de O1", y el resultado del spot-check de motor real.

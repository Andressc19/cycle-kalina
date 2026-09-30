---
project: ciclo_kalina_tercero
task_id: 2026-09-29-fase2-ronda4-spotcheck-motor-real
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-29
---

# TASK_CONTEXT — Fase 2 Ronda 4: confirmar con motor real los puntos de menor margen O2

## Task ID

2026-09-29-fase2-ronda4-spotcheck-motor-real

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. La Ronda 4
(`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`, filas 185-798, 613
puntos) corrió **solo con `TeqpAdapter`**, sin ningún spot-check de motor real — a
diferencia de las rondas de sensibilidad final de Fase 2/3, donde sí se verificaron puntos
cerca de fronteras. El director quiere cerrar ese hueco antes de diseñar la Ronda 5.

## Objective

1. De las 613 filas de la Ronda 4 (busca cómo identificarlas: son las filas posteriores a
   las primeras 184 del archivo — verifica leyendo el archivo completo, no asumas offsets),
   selecciona los **8-10 puntos con `clasificacion=KALINA` y menor `|O2_margen|`** (el margen
   más cercano a cero, tanto positivo como negativo si hay CORREGIBLE cerca del filo también
   — pero prioriza KALINA, que es lo que se reportaría como candidato válido).
2. Para cada uno de esos puntos, corre `resolver_ciclo` + `evaluar_ciclo` con el motor real
   `AmmoniaWaterAdapter` (mismos parámetros exactos de la fila: `P_alta, P_baja, x_b, m_b,
   eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, T_fuente, T_sumidero`, y
   `T_amb_diseno=303.55`, igual que toda Fase 2).
3. Compara la clasificación y `eta` del motor real contra lo que dice la fila de
   `busqueda_libre_v2.csv` (que viene de `TeqpAdapter`). Reporta CADA comparación
   explícitamente — si algún punto cambia de KALINA a otra cosa (o viceversa), es
   exactamente lo que se quiere detectar, no lo suavices.
4. No hace falta re-ejecutar TODO con motor real — son 8-10 puntos, el motor real tarda
   ~2-9 min cada uno, así que el total es manejable en una sola tarea.

## MUY IMPORTANTE — dónde guardar

Este NO es un barrido nuevo, es una verificación — no agregues filas a
`busqueda_libre_v2.csv`. Guarda el resultado en un JSON nuevo:
`resultados/barridos_2026-09-19/fase2_libre/spotcheck_ronda4_motor_real.json`, con esta
estructura por punto: los parámetros de entrada, `eta`/`clasificacion` de Teqp (tal como
está en el CSV), `eta`/`clasificacion` del motor real, y si coinciden o no.

## Files

Puedes crear UN script en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej.
`ronda4_spotcheck.py`, ≤200 líneas).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, `busqueda_libre_v2.csv` ni ningún otro
CSV/resultado existente, ni otras carpetas de `scripts/barridos_2026-09-19/` o
`resultados/barridos_2026-09-19/` fuera de `fase2_libre/`.

## Constraints

1. Script ≤200 líneas.
2. Motor real solo para los 8-10 puntos seleccionados — no conviertas esto en un barrido
   completo con motor real.
3. Si algún punto no converge con el motor real (posible, ya visto antes cerca de
   fronteras), regístralo igual como discrepancia, no lo descartes silenciosamente.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: tabla de los 8-10 puntos con clasificación Teqp vs motor real,
y cuántos coincidieron vs cuántos discreparon.

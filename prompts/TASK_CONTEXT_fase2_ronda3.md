---
project: ciclo_kalina_tercero
task_id: 2026-09-21-fase2-ronda3-malla-fina
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-21
---

# TASK_CONTEXT — Fase 2: tercera ronda, malla fina P_alta×P_baja cerca de una frontera

## Task ID

2026-09-21-fase2-ronda3-malla-fina

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Tercera ronda de Fase 2, sigue
directamente a la ronda 2 (`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`
ya tiene 160 filas: 80 originales + 80 de la ronda 2).

## Contexto puntual

En la ronda 2 se encontró que `(P_alta=3200, P_baja=650, x_b=0.50, eps_cond=0.95)` clasificó
KALINA mientras que `(P_alta=3000, P_baja=650, x_b=0.50, eps_cond=0.95)` quedó CORREGIBLE por
solo 0.15 K de margen O2. El director quiere cerrar esa frontera con una malla fina.

## MUY IMPORTANTE — reglas (idénticas a la ronda 2)

1. **Ancla fija**: `T_fuente=470.0 K`, `T_sumidero=300.032917 K`. `x_b=0.50` y `eps_cond=0.95`
   fijos también en esta ronda (son los valores del punto que se quiere delimitar) — solo
   `P_alta` y `P_baja` varían.
2. **Motor: solo `TeqpAdapter`**.
3. **No repitas combinaciones ya evaluadas** — lee TODOS los CSV de
   `resultados/barridos_2026-09-19/fase2_libre/` (incluida la ronda 2 ya agregada a
   `busqueda_libre_v2.csv`) y arma el conjunto de combinaciones `(P_alta, P_baja, x_b, eta_t,
   eta_p, eps_hrvg, eps_reg, eps_cond)` ya probadas (tolerancia 3 decimales) antes de generar
   la malla nueva.
4. **Resto de variables en los valores del ancla ya usados en Fase 2**: `eta_t=0.85,
   eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75` (los mismos de siempre en esta fase — no los
   cambies, esta ronda es específicamente sobre P_alta/P_baja).
5. **T_amb_diseno=303.55** (el mismo de toda Fase 2, no lo cambies).

## Objective

1. Malla fina: `P_alta` de 3100 a 3300 kPa (paso 50 kPa → 5 valores) × `P_baja` de 630 a 670
   kPa (paso 10 kPa → 5 valores) = 25 combinaciones candidatas, menos las que ya estén
   probadas (probablemente 3200/650 ya está de la ronda 2 — exclúyela).
2. Corre esa malla con `TeqpAdapter`.
3. Identifica dónde exactamente cruza la frontera KALINA/CORREGIBLE en ese rectángulo
   (reporta el margen O2 de cada punto, no solo la clasificación).

## MUY IMPORTANTE — dónde guardar

**NO crees ningún CSV nuevo.** Agrega (append) las filas nuevas al final de
`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`, mismo esquema de 19
columnas que ya tiene el archivo (léela de la cabecera real, no la asumas). El archivo debe
quedar como una sola tabla válida (una cabecera, todas las filas anteriores + las nuevas).

## Files

Puedes crear UN script nuevo en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej.
`ronda3_malla_fina.py`, ≤200 líneas, puedes reusar/importar la lógica de `ronda2_pbaja.py` ya
existente en esa carpeta en vez de reescribirla).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni otras carpetas de
`scripts/barridos_2026-09-19/`/`resultados/barridos_2026-09-19/` fuera de `fase2_libre/`. NO
toques `sensibilidad_*.csv`, `mapa_2d_*.csv`, `prescan_eps_hrvg.csv`.

## Constraints

1. Script nuevo ≤200 líneas.
2. Cero puntos repetidos (documenta cuántas de las 25 candidatas se descartaron por
   duplicado).
3. Todo punto se registra, converja o no.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: la tabla de la malla con clasificación y margen O2 de cada
punto, y dónde queda exactamente la frontera.

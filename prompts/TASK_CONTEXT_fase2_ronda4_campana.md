---
project: ciclo_kalina_tercero
task_id: 2026-09-28-fase2-ronda4-campana-3h
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-28
---

# TASK_CONTEXT — Fase 2: campaña extendida (~3 h), efectividades realistas estrictas

## Task ID

2026-09-28-fase2-ronda4-campana-3h

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Cuarta ronda de Fase 2, sigue a las
rondas 1-3 ya en `resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv` (184
filas). El director quiere una campaña LARGA (presupuesto de tiempo ~3 horas de cómputo) con
reglas de realismo MÁS ESTRICTAS que las rondas anteriores.

## MUY IMPORTANTE — reglas de esta ronda (más estrictas que rondas 1-3, LÉELAS con cuidado)

1. **Ancla fija**: `T_fuente=470.0 K`, `T_sumidero=300.032917 K` (igual que siempre en
   Fase 2).
2. **Efectividades SIEMPRE en [0.75, 0.85]**: `eps_hrvg`, `eps_reg`, `eps_cond` — ninguna
   puede salir de ese rango en esta ronda (en rondas anteriores se permitió `eps_cond` hasta
   0.95; ESO YA NO APLICA AQUÍ, el techo real ahora es 0.85).
3. **`x_b` NO se baja**: usa `x_b` en `[0.40, 0.50]` — NO repitas la palanca de las rondas 2-3
   que bajaba `x_b` a 0.35 para relajar O2. Esta ronda cierra el criterio O2 de otra forma
   (ver punto 4).
4. **La palanca para cerrar O2 es `P_baja`, no las efectividades.** Con `eps_cond` topado en
   0.85 (más bajo que antes), vas a necesitar `P_baja` más alto que en rondas anteriores para
   que el margen de O2 sea positivo — eso es exactamente lo que se quiere medir: hasta dónde
   hay que subir `P_baja` para compensar el techo más bajo de `eps_cond`. Explora `P_baja` en
   un rango AMPLIO, bastante más allá de lo ya cubierto (hasta ahora se cubrió hasta ~800 kPa
   en algunas celdas; sube hasta donde haga falta, dentro del límite de `CAMPOS_CICLO`
   [50, 5000] kPa, para encontrar la zona KALINA con estas efectividades más bajas).
5. **`P_alta`**: puedes variarla (rango realista ya usado en Fase 2: 2800-3300 kPa) si ayuda
   a cerrar la frontera, pero `P_baja` sigue siendo la palanca principal.
6. **`eta_t` 0.80-0.90, `eta_p` 0.70-0.80** (rangos ya usados en rondas anteriores, sin
   cambios).
7. **Motor: solo `TeqpAdapter`**. **`T_amb_diseno=303.55`** (sin cambios, correcto para el
   clima del profesor).
8. **No repitas combinaciones ya evaluadas** — lee TODOS los CSV de
   `resultados/barridos_2026-09-19/fase2_libre/` (incluidas las 184 filas ya en
   `busqueda_libre_v2.csv` de las rondas 1-3) y arma el conjunto de 8-tuplas `(P_alta,
   P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond)` ya probadas (tolerancia 3
   decimales) antes de generar cualquier combinación nueva.

## Objective — campaña extendida, presupuesto ~3 horas

1. Diseña una campaña de exploración GRANDE (no un solo barrido de 30-80 puntos como las
   rondas anteriores) que cubra sistemáticamente el espacio `(P_baja, x_b, eps_cond)` —con
   `eps_hrvg`/`eps_reg` fijos en un valor razonable del rango [0.75,0.85], p.ej. 0.80, salvo
   que quieras cruzarlos también en una submalla más pequeña— buscando la frontera KALINA con
   las efectividades más bajas de esta ronda. Con 4 workers y ~10-40 s/punto con
   `TeqpAdapter` (medido en rondas anteriores), un presupuesto de ~3 horas de cómputo permite
   del orden de 1000-2500 puntos — usa tu criterio para no excederte, pero SÍ aprovecha el
   presupuesto (no te quedes corto con 80-100 puntos como antes, esta ronda es
   deliberadamente más grande).
2. **Checkpointing obligatorio**: guarda progreso incrementalmente (cada lote de ~20-50
   puntos) al CSV, no acumules todo en memoria hasta el final — si el proceso se interrumpe,
   no debe perderse el trabajo ya hecho (aplica la lección de la ronda de sensibilidad final
   de Fase 2, donde un bug hizo perder 18 min de motor real por no tener checkpointing).
3. Identifica y reporta dónde queda la frontera KALINA/CORREGIBLE con estas efectividades más
   bajas — cuánto `P_baja` adicional hace falta comparado con las rondas anteriores (que
   usaban `eps_cond` hasta 0.95) para lograr el mismo margen de O2.

## MUY IMPORTANTE — dónde guardar

**NO crees ningún CSV nuevo.** Agrega (append) TODAS las filas nuevas al final de
`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`, mismo esquema de 19
columnas que ya tiene el archivo (lee la cabecera real, no la asumas). Un solo archivo, una
sola cabecera, todas las filas (viejas + nuevas) debajo.

## Files

Puedes crear script(s) nuevos en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej.
`ronda4_campana.py`, ≤200 líneas cada uno — divide en varios archivos si la lógica no cabe;
puedes reusar/importar `ronda2_pbaja.py`/`ronda3_malla_fina.py` ya existentes en esa carpeta
en vez de reescribir todo).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni otras carpetas de
`scripts/barridos_2026-09-19/`/`resultados/barridos_2026-09-19/` fuera de `fase2_libre/`. NO
toques `sensibilidad_*.csv`, `mapa_2d_*.csv`, `prescan_eps_hrvg.csv`, `ancla_*.csv`. **NO
toques `app.py` ni ningún `ui_*.py`** (fuera de alcance de esta tarea).

## Constraints

1. Cada script ≤200 líneas.
2. Cero puntos repetidos (documenta cuántas candidatas se generaron y cuántas se descartaron
   por duplicado).
3. Todo punto se registra, converja o no.
4. Efectividades/eficiencias ESTRICTAMENTE dentro de los rangos del punto "reglas" de
   arriba — ningún valor fuera de [0.75,0.85] para eps_hrvg/eps_reg/eps_cond, ningún `x_b`
   por debajo de 0.40.
5. Si en algún momento el proceso lleva corriendo más de ~3 horas de cómputo real (no de
   pared, de cómputo), cierra ordenadamente con lo que tengas: guarda el CSV, escribe el
   reporte final con lo alcanzado hasta ese punto, no lo dejes a medias sin reporte.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: cuántos puntos nuevos en total, cuántos KALINA nuevos, el
`P_baja` mínimo que logra KALINA para cada valor de `eps_cond` explorado (tabla), y
comparación explícita contra el `P_baja` que hacía falta en rondas anteriores con
`eps_cond` más alto.

---
project: ciclo_kalina_tercero
task_id: 2026-09-21-fase2-ronda2-pbaja
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-21
---

# TASK_CONTEXT — Fase 2: segunda ronda de exploración, ancla T_fuente/T_sumidero fijas

## Task ID

2026-09-21-fase2-ronda2-pbaja

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Segunda ronda de exploración de
Fase 2 (base libre) — el director quiere MÁS puntos que conviertan región CORREGIBLE en
KALINA, sin repetir combinaciones ya probadas, apoyándose sobre todo en mover `P_baja`.

## MUY IMPORTANTE — reglas de esta ronda

1. **Ancla fija (NO se mueve en esta ronda)**: `T_fuente=470.0 K`, `T_sumidero=300.032917 K`.
   Todas las demás variables SÍ se pueden mover.
2. **Motor: solo `TeqpAdapter`** (ningún punto con motor real en esta ronda).
3. **No repitas combinaciones ya evaluadas.** Antes de correr nada, lee TODOS los CSV que ya
   existen en `resultados/barridos_2026-09-19/fase2_libre/` (`busqueda_libre.csv`,
   `busqueda_libre_v2.csv`, `prescan_eps_hrvg.csv`, `sensibilidad_*.csv`,
   `mapa_2d_pbaja_epscond.csv`) y arma el conjunto de combinaciones `(P_alta, P_baja, x_b,
   eta_t, eta_p, eps_hrvg, eps_reg, eps_cond)` ya probadas (redondea a una tolerancia
   razonable, p.ej. 3 decimales, para detectar duplicados aunque no coincidan bit a bit).
   Genera SOLO combinaciones nuevas que no estén en ese conjunto.
4. **Efectividades y eficiencias en rango REALISTA — no las fuerces a los extremos de
   `CAMPOS_CICLO`.** Ya se estableció en tareas anteriores de este proyecto que valores como
   `eps_cond=0.99` no son un punto de diseño defendible. Mantén: `eta_t` 0.80–0.90, `eta_p`
   0.70–0.80, `eps_hrvg` 0.80–0.95, `eps_reg` 0.70–0.85, `eps_cond` 0.80–0.95 — estos son los
   rangos "realistas" ya usados en este repo, no los amplíes sin justificar por qué hace
   falta.
5. **La palanca principal a explorar es `P_baja`** (el director sospecha que moviéndola se
   pueden encontrar más puntos KALINA), cruzada con `x_b` y `eps_cond` (las 3 variables que
   más mueven el criterio O2, que es la causa de CASI TODOS los CORREGIBLE encontrados hasta
   ahora en Fase 2 — ver `resultados/barridos_2026-09-19/fase2_libre/*.csv`, columna
   `criterio_ligante`/mensaje). `P_alta` puede moverse también si ayuda, pero no es la
   palanca prioritaria.

## Objective

1. Diseña una rejilla NUEVA (no repetida) de `(P_baja, x_b, eps_cond)` — y opcionalmente
   `P_alta`/`eta_t`/`eps_hrvg`/`eps_reg` dentro de los rangos realistas del punto 4 — que
   cubra zonas del espacio de búsqueda que las corridas anteriores dejaron como CORREGIBLE,
   buscando específicamente convertirlas en KALINA subiendo o bajando `P_baja` (recuerda:
   `P_baja` más alto sube el punto de burbuja de la mezcla a esa presión, lo que ayuda a
   pasar el criterio O2 — pero balancéalo con no perder demasiada eficiencia).
2. Corre esa rejilla con `TeqpAdapter` (`resolver_ciclo` + `evaluar_ciclo`, con
   `T_amb_diseno=303.55` — el mismo usado en toda Fase 2, no lo cambies: es correcto para el
   clima del profesor, ver `BASE_LIBRE_v2.md`).
3. Presupuesto: 80-150 puntos nuevos (usa tu criterio para no pasarte, prioriza cobertura de
   la zona CORREGIBLE→KALINA sobre cantidad).

## MUY IMPORTANTE — dónde guardar el resultado

**NO crees un CSV nuevo separado.** Las filas nuevas se AGREGAN (append) al final de
`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`, con exactamente el mismo
esquema de columnas que ya tiene ese archivo (`T_fuente,T_sumidero,P_alta,P_baja,x_b,m_b,
eta_t,eta_p,eps_hrvg,eps_reg,eps_cond,T_sat_L,T9_amb,O2_margen,convergio,clasificacion,eta,
Wnet,mensaje`) — lee la cabecera real del archivo antes de escribir para confirmar el orden
exacto de columnas, no lo asumas de este texto. El archivo resultante debe seguir siendo un
CSV válido de una sola tabla (cabecera una vez, todas las filas viejas + las nuevas debajo).

## Files

Puedes crear UN script nuevo en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej.
`ronda2_pbaja.py`, ≤200 líneas) que lea los CSV existentes, calcule las combinaciones nuevas,
corra el barrido, y haga el append a `busqueda_libre_v2.csv`. No crees más archivos de
resultados de los estrictamente necesarios (el script sí puede ser nuevo, el CSV de
resultados NO debe ser nuevo).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni ninguna otra carpeta de
`scripts/barridos_2026-09-19/` o `resultados/barridos_2026-09-19/` fuera de `fase2_libre/`.
**NO toques** ningún archivo `sensibilidad_*.csv`, `mapa_2d_*.csv`, ni `prescan_eps_hrvg.csv`
— solo `busqueda_libre_v2.csv` recibe filas nuevas.

## Constraints

1. El script nuevo ≤200 líneas.
2. Cero puntos repetidos (verificación explícita contra las combinaciones ya existentes,
   documentada en el reporte: cuántas candidatas se generaron, cuántas se descartaron por
   duplicado).
3. Todo punto se registra, converja o no.
4. Efectividades/eficiencias dentro de los rangos realistas del punto 4 de arriba — ningún
   valor forzado a los extremos de `CAMPOS_CICLO`.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: cuántos puntos nuevos, cuántos KALINA nuevos encontrados (si
los hay), y el rango de `P_baja` donde aparecieron (si aplica).

---
project: ciclo_kalina_tercero
task_id: 2026-09-19-fase3-caso-real
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-19
---

# TASK_CONTEXT — Fase 3: base anclada a un caso real de Kalina (planta Húsavík)

## Task ID

2026-09-19-fase3-caso-real

## Project

`ciclo_kalina_tercero`, rama `test/vv-strategy`. Fase 3 de 3 fases PARALELAS (ver
`AGENTS.md`). **Corre al mismo tiempo que `TASK_CONTEXT_fase1_profesor.md` y
`TASK_CONTEXT_fase2_libre.md` — trabaja ÚNICAMENTE en
`scripts/barridos_2026-09-19/fase3_real/` y `resultados/barridos_2026-09-19/fase3_real/`, no
toques `fase1_profesor/` ni `fase2_libre/` ni ningún archivo que puedan estar editando las
otras dos tareas.**

## Objective

Anclar una base de operación a un caso REAL de aplicación de ciclo Kalina (no
necesariamente KSC-11 exacto ni cementera — puede ser cualquier aplicación real
documentada, geotérmica, industrial, etc.), tomando de ahí `T_fuente`, `T_sumidero`
(sumidero/ambiente) y, como punto de partida, `x_b`/`P_alta`, y luego AJUSTAR el resto de
variables (`P_baja`, efectividades, eficiencias) dentro de `CAMPOS_CICLO` hasta que el
punto clasifique `KALINA` — para poder correr un análisis de sensibilidad con sentido físico
real alrededor de esa base.

## El caso real (ya investigado por el director, no lo vuelvas a buscar)

**Planta geotérmica de Húsavík, Islandia** — ciclo Kalina real, en operación desde el año
2000, 2 MW nominales, ampliamente documentada en la literatura (Mlcak et al.). Parámetros
reales publicados:

- `T_fuente` (salmuera geotérmica): 121 °C = **394.15 K**.
- `x_b` (fracción másica de NH3 del fluido de trabajo): **≈0.82**.
- `P_alta` (entrada turbina): 32-34 bar ≈ **3300 kPa** (punto de partida; confírmalo tú
  mismo contra `CAMPOS_CICLO`, está dentro de sus límites 500-20000 kPa).
- `T_sumidero` (agua de refrigeración): 5 °C = **278.15 K**.
- `eta_t` ≈ 0.90, `eta_p` ≈ 0.80 (valores citados en análisis de la literatura sobre este
  caso, no en la ficha técnica original de la planta — trátalos como punto de partida
  razonable, no como dato absoluto).
- `T0`/`P0` (estado muerto, para exergía si aplica en tareas futuras): usa `T0=T_sumidero=
  278.15 K` (agua de refrigeración = mejor proxy disponible del ambiente en Húsavík) y
  `P0=101.325 kPa` (atmosférica estándar, mismo default que `CONTEXT.md` — Húsavík está a
  nivel del mar). Esto es una elección razonable del director, no un dato publicado exacto
  de la planta — decláralo como supuesto en tu reporte.
- `P_baja`, `eps_hrvg`, `eps_reg`, `eps_cond`: NO están fijados por el caso real — son tuyos
  para calibrar (ver Approach).

Fuentes (búsqueda web hecha por el director 2026-09-19, no las repitas):
https://en.wikipedia.org/wiki/Husavik_Power_station,
https://www.researchgate.net/publication/335443981 (resumen del proyecto),
literatura citando Mlcak et al. 2002 "Kalina Cycle Concepts for Low Temperature Geothermal".

## Approach

1. Calibra `P_baja`: la presión mínima que da `bubble_point(P_baja, x_b≈0.82) ≈ T_sumidero
   + ΔT_app,cond` con `ΔT_app,cond≈3 K` (mismo supuesto ya usado en la Fase B0 anterior de
   este proyecto — no inventes otro), dentro de `CAMPOS_CICLO` (50-5000 kPa).
2. Prueba `resolver_ciclo` con `(P_alta=3300, P_baja=calibrado, x_b=0.82, T_fuente=394.15,
   T_sumidero=278.15, m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75,
   eps_cond=0.80)` — los ε quedan en el default de `CONTEXT.md` como punto de partida.
   `T_fuente=394.15 K` es bastante más frío que los casos que fallaron antes en este
   proyecto (470-623 K), así que hay buenas chances de que converja sin más ajuste — pero
   verifícalo, no lo asumas.
3. Si no converge o no clasifica `KALINA`, ajusta con `TeqpAdapter` (rápido): primero
   `P_alta`/`x_b` cerca del rango real citado (no te alejes mucho sin justificarlo — este es
   el caso que SÍ debe quedar anclado a algo real), luego `eps_hrvg`/`eps_reg`/`eps_cond` si
   hace falta. Registra cada intento en
   `resultados/barridos_2026-09-19/fase3_real/busqueda_husavik.csv` (mismo esquema que
   `tabla_barrido`).
4. Con la base `KALINA` encontrada, confirma con el motor real `AmmoniaWaterAdapter` y
   guarda en `resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real.json`.
5. (Si el tiempo alcanza, opcional): con la base ya `KALINA` confirmada, corre 2-3 barridos
   pequeños de sensibilidad alrededor de ella (p.ej. `eta vs P_alta`, `eta vs x_b`) con
   `TeqpAdapter`, guardados como CSV en la misma carpeta — es un adelanto útil para la fase
   de barridos completa que viene después, pero NO es obligatorio si el tiempo no alcanza.
6. Escribe `resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK.md` (español): el caso
   real citado con sus fuentes, la base final `KALINA` con todos sus valores, qué se ajustó
   respecto a los datos reales publicados y por qué (qué criterio de `restricciones/` dejaba
   de fallar), y la confirmación con motor real.

## Files

Todo nuevo en `scripts/barridos_2026-09-19/fase3_real/` y
`resultados/barridos_2026-09-19/fase3_real/`. Límite 200 líneas por archivo `.py`.

**NO modifiques**: `src/cycle_solver.py`, `src/sensitivity.py`, `src/properties/`,
`src/restricciones/`, `src/components/`, `src/state.py`, `src/ui_*.py`, `app.py`,
`CONTEXT.md`. **NO toques `fase1_profesor/` ni `fase2_libre/`** (tareas paralelas).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Dentro de `CAMPOS_CICLO` siempre. A diferencia de la Fase 2, aquí SÍ importa quedarse
   cerca de lo real citado arriba — si tienes que alejarte mucho de `x_b≈0.82`/`P_alta≈3300
   kPa` para lograr `KALINA`, documenta la magnitud del ajuste con honestidad (no lo
   escondas ni lo minimices).
3. Tope: ~150-200 puntos con `TeqpAdapter`, 1-3 con motor real para confirmar.
4. Todo punto probado se registra, converja o no.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: la base `KALINA` final con su justificación frente al caso
real, y la confirmación con motor real.

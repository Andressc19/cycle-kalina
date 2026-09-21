---
project: ciclo_kalina_tercero
task_id: 2026-09-19-fase2-busqueda-libre
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-19
---

# TASK_CONTEXT — Fase 2: búsqueda LIBRE de una base que clasifique KALINA

## Task ID

2026-09-19-fase2-busqueda-libre

## Project

`ciclo_kalina_tercero`, rama `test/vv-strategy`. Fase 2 de 3 fases PARALELAS (ver
`AGENTS.md`). **Corre al mismo tiempo que `TASK_CONTEXT_fase1_profesor.md` y
`TASK_CONTEXT_fase3_real.md` — trabaja ÚNICAMENTE en
`scripts/barridos_2026-09-19/fase2_libre/` y
`resultados/barridos_2026-09-19/fase2_libre/`, no toques las carpetas `fase1_profesor/` ni
`fase3_real/` ni ningún archivo que puedan estar editando las otras dos tareas.**

## Objective

Partiendo de la base del profesor (P_alta=3000 kPa, P_baja=400 kPa, x_b=0.50,
T_fuente=623.15 K, T_sumidero=300.032917 K, m_b=1.0, eta_t=0.85, eta_p=0.75,
eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80 — que YA SABEMOS que falla, no lo vuelvas a
probar, es trabajo de la Fase 1 paralela), **ajusta libremente las variables que haga
falta** — presión baja, temperaturas (fuente y/o sumidero), efectividades — dentro de los
límites de `CAMPOS_CICLO` (`src/ui_helpers.py`) hasta encontrar AL MENOS UNA combinación
que `src.restricciones.evaluar_ciclo` clasifique como `KALINA`. **Este ejercicio NO necesita
estar anclado a ningún caso real** — es una prueba de que el modelo/solver de este repo
puede producir un punto válido, punto de partida para la Fase 3 (que sí ancla a un caso
real) y para diseñar barridos de sensibilidad con sentido.

## Contexto ya investigado (pista fuerte, empieza por aquí)

`CONTEXT.md` (nota 2026-09-17, "Sustancia de trabajo") documenta que con
**`T_fuente=470.0 K`** (bastante más frío que los 623.15 K del profesor) el estado 2 del
HRVG SÍ cae dentro de la campana bifásica para varios T1 de prueba (T1_sol=386.52 K,
T2=464.07 K, verificado en su momento por el solver). **`T_fuente=470 K` es justo el valor
por defecto de `CAMPOS_CICLO`** — es decir, el caso con TODOS los valores por defecto de
`CONTEXT.md` (P_alta=3000, P_baja=400, x_b=0.50, T_fuente=470.0, T_sumidero=300.032917,
m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80) **es el primer
candidato obvio a probar** — puede que ya converja y clasifique KALINA sin tocar nada más.
Empieza por ahí antes de explorar cualquier otra cosa.

También se sabe (de la Fase B0 anterior, ver
`resultados/barridos_2026-09-19/b0_scan_cementera.csv` y
`resultados/barridos_2026-09-19/b0_confirmacion_motor_real.json`, ya en el repo): con
`T_fuente` alto (583-623 K) y `P_alta` en 2000-7000 kPa, la sonda de arranque del bracket
search (`_bracketear`, `src/cycle_solver.py`) evalúa un T1 cercano a `T_fuente`, lo que
sobrecalienta el estado 2 de esa sonda por encima de la campana bifásica y hace fallar el
punto ANTES de llegar al punto de equilibrio real — confirmado con `TeqpAdapter` Y con el
motor real. Si necesitas mantener un `T_fuente` alto por algún motivo, esto es lo que vas a
chocar; si no hay requisito de mantenerlo alto, baja `T_fuente` es la vía más directa.

## Approach

1. Prueba primero el punto por defecto exacto de `CAMPOS_CICLO` (arriba). Si converge y
   clasifica `KALINA`, ya tienes tu candidato — documenta y pasa al punto 4.
2. Si no converge o no clasifica `KALINA`, explora con `TeqpAdapter` (rápido) variando
   `P_baja`, `T_fuente`, `T_sumidero`, `eps_hrvg`, `eps_reg`, `eps_cond` — en cualquier
   combinación razonable, dentro de `CAMPOS_CICLO` — hasta encontrar un punto `KALINA`.
   Registra cada intento (converja o no) en
   `resultados/barridos_2026-09-19/fase2_libre/busqueda_libre.csv` (mismo esquema de
   columnas que `tabla_barrido`: todas las variables + `convergio`, `clasificacion`, `eta`,
   `Wnet`, `mensaje`).
3. Una vez tengas 1-3 candidatos `KALINA` con `TeqpAdapter`, confirma el mejor (o los 3, si
   el tiempo lo permite) con el motor real `AmmoniaWaterAdapter` — guarda el resultado en
   `resultados/barridos_2026-09-19/fase2_libre/confirmacion_motor_real.json`.
4. Escribe `resultados/barridos_2026-09-19/fase2_libre/BASE_LIBRE.md` (español): el
   candidato final `(P_alta, P_baja, x_b, T_fuente, T_sumidero, eta_t, eta_p, eps_hrvg,
   eps_reg, eps_cond)`, su `eta`/`Wnet`, qué tan lejos quedó de los valores del profesor y
   por qué tuviste que moverte (qué criterio de `restricciones/` dejaba de fallar al mover
   cada variable), y confirmación con motor real.

## Files

Todo nuevo en `scripts/barridos_2026-09-19/fase2_libre/` y
`resultados/barridos_2026-09-19/fase2_libre/`. Límite 200 líneas por archivo `.py`.

**NO modifiques**: `src/cycle_solver.py`, `src/sensitivity.py`, `src/properties/`,
`src/restricciones/`, `src/components/`, `src/state.py`, `src/ui_*.py`, `app.py`,
`CONTEXT.md`. **NO toques `fase1_profesor/` ni `fase3_real/`** (tareas paralelas).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Dentro de `CAMPOS_CICLO` siempre (no inventes límites nuevos). No hay restricción de
   "realismo industrial" en esta fase — es exploración libre del modelo, dilo así en el
   reporte para que no se confunda con la Fase 3 (que sí debe ser realista).
3. Tope: ~150-200 puntos con `TeqpAdapter`, 1-3 con motor real para confirmar.
4. Todo punto probado se registra, converja o no.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: el candidato `KALINA` encontrado (o el mejor no-KALINA y por
qué, si de verdad no se logra ninguno tras esfuerzo razonable — repórtalo honesto).

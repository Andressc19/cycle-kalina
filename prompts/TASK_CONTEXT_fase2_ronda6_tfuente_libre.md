---
project: ciclo_kalina_tercero
task_id: 2026-09-29-fase2-ronda6-tfuente-libre-xb-alto
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-29
---

# TASK_CONTEXT — Fase 2 Ronda 6: liberar T_fuente y explorar x_b alto (0.70-0.85)

## Task ID

2026-09-29-fase2-ronda6-tfuente-libre-xb-alto

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad`. Sigue a la Ronda 5
(`resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`, ahora 945 filas), que
encontró un MURO estructural: con `T_fuente=470.0 K` fija, `x_b≥0.70` casi no converge (0/24
en el rango nominal de P_alta) y ninguno converge en `x_b=0.85`. Causa identificada: la
temperatura de rocío de la mezcla a `P_alta`/`x_b` alto se acerca a `T_fuente`, el HRVG
entrega una mezcla casi saturada y el separador pierde la campana bifásica.

## Objective

**Esta vez NO fijes `T_fuente=470K`. Libéralo como variable de búsqueda**, cruzado con
`x_b` alto (0.70-0.85), para encontrar en qué combinación `(T_fuente, x_b)` SÍ existe una
zona KALINA competitiva (η comparable o mejor que el mejor histórico de Fase 2, 0.1243 de
la Ronda 1-3) — replicando la lógica de Karimi & Ahmad (2016), que varían T_fuente
libremente junto con x_b y por eso sí encuentran una zona de alta eficiencia en x_b=0.80.

## Rango de búsqueda

1. **`T_fuente`**: 380-500 K (cubre el rango de Karimi & Ahmad, 373-473 K, más un margen de
   ~30 K). NO subas de 500 K sin reportarlo como decisión explícita — recuerda que
   `T_fuente` alto ya rompió Fase 1 completa (623 K) y las rondas 1-4 usan 470 K como techo
   de referencia conocido que sí converge.
2. **`x_b`**: 0.70-0.85, paso 0.05 (igual que Ronda 5).
3. **`P_alta`**: 2800-4500 kPa (la Ronda 5 ya mostró que a `x_b` alto puede hacer falta
   subir hasta 4500 kPa — mantenlo como variable libre en este rango, NO lo fijes).
4. **`P_baja`**: la palanca principal para cerrar O2, como en todas las rondas anteriores —
   busca, para cada combinación `(T_fuente, x_b, P_alta)` prometedora, el `P_baja` mínimo que
   da KALINA (mismo método de "columnas" ya usado en Rondas 4 y 5,
   `ronda4_columnas.py`/`ronda5_columnas.py` — reutilízalo o adáptalo, no lo reinventes).
5. **Efectividades en [0.75, 0.85]** (`eps_hrvg`, `eps_reg`, `eps_cond`) — sin cambios,
   sigue la regla vigente.
6. **`eta_t` 0.80-0.90, `eta_p` 0.70-0.80** — sin cambios.
7. **`T_sumidero=300.032917 K`, `T_amb_diseno=303.55 K`** fijos, sin cambios.
8. **Vigila margen O1 Y O2 explícitamente** (lección de las rondas 4 y 5 — regístralos
   ambos en columnas del companion, igual que hizo la Ronda 5).

## Estrategia sugerida (evita fuerza bruta 4D completa)

No hagas una malla completa `T_fuente × x_b × P_alta × P_baja` (sería excesivo). En su lugar:
1. Para cada `x_b ∈ {0.70, 0.75, 0.80, 0.85}` y cada `T_fuente` en una rejilla gruesa (paso
   ~20-30 K en 380-500 K), primero verifica RÁPIDO (con `bubble_point`/`dew_point`, sin
   resolver el ciclo completo) si la campana bifásica a un `P_alta` razonable (usa 3000 y
   4000 kPa como referencia) puede cubrir ese `T_fuente` — descarta de entrada las
   combinaciones donde ni siquiera la campana alcanza, como se hizo en la Fase B0 original.
2. Para las combinaciones que sobrevivan ese filtro, corre el ciclo completo y busca el
   `P_baja` mínimo que da KALINA (búsqueda tipo "columna", como en rondas anteriores).
3. Reporta, para cada `x_b`, el rango de `T_fuente` donde SÍ hay KALINA y con qué η —
   esto es lo que responde la pregunta de fondo: ¿existe una zona `(T_fuente, x_b alto)`
   competitiva con las rondas 1-3?

## MUY IMPORTANTE — dónde guardar

Igual que rondas anteriores: **append a `busqueda_libre_v2.csv`** (mismo esquema de 19
columnas, cabecera real, sin crear CSV nuevo para el barrido). Puedes usar un companion CSV
nuevo para las columnas de diagnóstico extra (`margen_O1`, `margen_O2`, etc.), como ya se
hizo en `ronda5_diagnostico.csv` — sigue ese mismo patrón, nombra el nuevo
`ronda6_diagnostico.csv`.

Si encuentras candidatos KALINA competitivos (η comparable a 0.10+), haz un spot-check de
motor real de 5-8 puntos (mismo patrón que rondas 4 y 5) y guarda
`spotcheck_ronda6_motor_real.json`.

## Sobre el bug de `_bracketear` (contexto, NO lo arregles)

La Ronda 5 encontró que `src/_cycle_loops.py::_bracketear` no envuelve en `try/except` la
evaluación del extremo superior del bracket, lo que puede matar puntos con raíz válida como
falsos NO_CONVERGIO cerca de la campana. **NO toques `src/` en esta tarea** (sigue fuera de
alcance) — pero si ves este mismo patrón de fallo, anótalo en el reporte como ya
diagnosticado, no lo vuelvas a investigar desde cero.

## Files

Scripts nuevos en `scripts/barridos_2026-09-19/fase2_libre/` (p.ej. `ronda6_tfuente.py`,
`ronda6_columnas.py`, ≤200 líneas cada uno — reusa lo que puedas de rondas 4/5).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, otras carpetas de
`scripts/barridos_2026-09-19/`/`resultados/barridos_2026-09-19/` fuera de `fase2_libre/`.

## Constraints

1. Cada script ≤200 líneas.
2. Cero puntos repetidos (verifica contra las 945 filas ya existentes).
3. Todo punto se registra, converja o no.
4. Motor: `TeqpAdapter` para el grueso, motor real solo para spot-check final (5-8 puntos).
5. Presupuesto: ~400-700 puntos Teqp (el filtro de campana debería evitar desperdiciar
   cómputo en combinaciones evidentemente inviables).

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: la tabla de qué `(T_fuente, x_b)` sí da KALINA competitivo y
con qué η, contrastado explícitamente contra el mejor histórico de Fase 2 (η=0.1243) y contra
la tabla de Karimi & Ahmad (2016) citada en `04_PROJECTS/active/Ciclo Kalina/referencias/` del
vault (si no tienes acceso al vault, usa el resumen: máximo 18.37% a T=463K/x_b=0.80 con
equipos 100% ideales — NO esperes igualar ese número con eficiencias realistas, compara
tendencia, no magnitud absoluta).

---
project: ciclo_kalina_tercero
task_id: 2026-09-24-verificacion-motor-real-y-salto-solver
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — (B) salto del solver en (0.60, 4000, 394) y (A) verificación con motor real de 3 KALINA

## Task ID

2026-09-24-verificacion-motor-real-y-salto-solver

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. El barrido
`resultados/2026-09-24_margen2k/` (efectividades fijas 0.85/0.80/0.85, `P_baja`
ajustado por brentq para 2 K de subenfriamiento, motor `TeqpAdapter`) dio 22 KALINA.
Dos cosas pendientes:

- **(B)** En `(x_b=0.60, P_alta=4000, T_fuente=394)` la función margen(P_baja) es
  discontinua: en ~0.5 kPa η salta 0.034 ↔ 0.080 y `T9_amb` salta ~0.41 K (ver
  `resultados/2026-09-24_margen2k/evaluaciones_margen.csv` y el hallazgo 5 de
  `REPORTE_MARGEN2K.md`). Hipótesis a comprobar: el lazo exterior de
  `resolver_ciclo` (brentq sobre `F(T1) = T1_nuevo − T1`, bracket por
  `_bracketear` en `src/_cycle_loops.py`) tiene más de una raíz y según el bracket
  cae en una u otra.
- **(A)** Ningún KALINA se ha confirmado con el motor real `AmmoniaWaterAdapter`.

**Nota:** `TASK_CONTEXT.md` y los demás `TASK_CONTEXT_*.md` de la raíz son OTRAS
tareas: no los ejecutes ni los modifiques. Tu tarea es solo este archivo.

Haz la Parte B primero (rápida, teqp) y luego la Parte A (lenta, motor real).

## Parte B — Diagnóstico del salto (solo TeqpAdapter)

Script `scripts/diagnostico_salto_solver.py`. Punto fijo: `x_b=0.60`,
`P_alta=4000`, `T_fuente=394`, `T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`,
`eps_hrvg=0.85`, `eps_reg=0.80`, `eps_cond=0.85`.

1. Leer `evaluaciones_margen.csv` y localizar las dos `P_baja` más cercanas entre
   sí a ambos lados del salto de η (una con η≈0.034 y otra con η≈0.080).
2. Barrido fino de `P_baja` en ±5 kPa alrededor del salto, paso 0.25 kPa: por
   cada P, `resolver_ciclo` y registrar `T1` de la solución (`estados["e1"].T`),
   `T2`, `q` o fase de e2 si está disponible, `m3` (vapor a turbina), η, Wnet,
   `T9`.
3. Para 2 valores de P (uno a cada lado del salto): evaluar `F(T1)` directamente
   (usar `evaluar` de `src/_cycle_loops.py`, misma firma que usa `resolver_ciclo`)
   en una malla de T1 desde `T_sumidero+1` hasta `T_fuente−1` cada 1 K
   (capturando excepciones por punto). Contar cambios de signo de F: ¿hay más de
   una raíz? ¿cuál elige brentq y por qué (bracket inicial de `_bracketear`)?
4. Si hay varias raíces, para cada una registrar η, Wnet, T2, m3 y la
   clasificación con `evaluar_ciclo(..., T_amb_diseno=283.15)`: ¿cuál es la
   solución física/de operación y cuál es artefacto?
5. **No modificar `src/`**. Si la causa es clara, proponer la corrección en
   RECOMMENDATIONS (no aplicarla).

Salidas: `resultados/2026-09-24_verificacion/salto_barrido_fino.csv`,
`salto_F_T1.csv`, y sección B del reporte.

## Parte A — Verificación con AmmoniaWaterAdapter (motor real)

Script `scripts/verificacion_motor_real_kalina.py`. Tres puntos, con el `P_baja`
exacto de `resultados/2026-09-24_margen2k/barrido_margen2k.csv` (leerlo de ahí,
no recalcularlo):

| x_b | P_alta | T_fuente | P_baja (del CSV) |
|---|---|---|---|
| 0.65 | 5000 | 423 | 704.644595 |
| 0.80 | 5000 | 394 | 952.892781 |
| 0.80 | 4000 | 394 | 1101.510788 |

Para cada punto, con AMBOS motores (`TeqpAdapter(x=x_b)` y
`AmmoniaWaterAdapter(x=x_b)`), mismos parámetros (eps fijos 0.85/0.80/0.85,
`T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`):
- `resolver_ciclo` con ese `P_baja`;
- margen O2 calculado como en `src/restricciones/operativos.py`: `T9_amb` =
  `condensador.resolver(e8, backend, T_sumidero=283.15, eps=0.85, m=1.0)[0].T`,
  `T_bur = backend.bubble_point(P_baja, x_b)`, margen = `T_bur − T9_amb`;
- `evaluar_ciclo(..., T_amb_diseno=283.15)`;
- registrar η, Wnet, Qi, T1..T10, x3, x5, m3, T9_amb, T_bur, margen,
  clasificación, fallas y el tiempo de cómputo.
- NO re-optimizar `P_baja` con el motor real: se verifica el punto tal cual.

Correr cada punto del motor real en su propio proceso o con captura de
excepciones, de modo que si uno falla o no converge, los otros sigan. Registrar
el error real si falla.

Salidas: `resultados/2026-09-24_verificacion/verificacion_motor_real.csv` y
sección A del reporte.

## Reporte

`resultados/2026-09-24_verificacion/REPORTE_VERIFICACION.md`:
- Parte B: ¿hay múltiples raíces en F(T1)? evidencia numérica, cuál solución es la
  buena, y si el fenómeno podría afectar otros puntos del barrido (mira en
  `evaluaciones_margen.csv` si hay otros saltos de η > 0.02 entre evaluaciones con
  |ΔP| < 5 kPa del mismo punto y lístalos).
- Parte A: tabla lado a lado teqp vs motor real por punto (η, Wnet, margen O2,
  clasificación, diferencias absolutas y relativas), y veredicto por punto:
  **confirmado** (misma clasificación), **no confirmado** (clasificación
  distinta) o **no evaluable** (motor real no converge).

## Files

Crear:
- `scripts/diagnostico_salto_solver.py`
- `scripts/verificacion_motor_real_kalina.py`
- `resultados/2026-09-24_verificacion/` con los CSV, `run_B.log`, `run_A.log` y
  `REPORTE_VERIFICACION.md`.

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni ningún
`TASK_CONTEXT*.md`).

## Constraints

- Parte B: solo TeqpAdapter. Parte A: ambos motores, nada más.
- Efectividades fijas 0.85/0.80/0.85 en todo.
- Capturar excepciones por evaluación; nunca abortar ni ocultar un resultado.
- `python -u`, salida a los logs indicados.
- Cada `.py` nuevo ≤ 250 líneas.
- El motor real tarda ~8-15 min por ciclo: no lances más corridas del motor real
  que las 3 pedidas.

## Acceptance criteria

1. Parte B con evidencia de F(T1) en dos P y veredicto sobre múltiples raíces.
2. Parte A con los 3 puntos evaluados (o su error real) en ambos motores.
3. RESULTS incluye ambas tablas resumen y las rutas.

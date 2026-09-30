---
project: ciclo_kalina_tercero
task_id: 2026-09-23-barrido-eps-fijos-085
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Barrido con efectividades fijas realistas (0.85/0.80/0.85) y P_baja ajustada por O2

## Task ID

2026-09-23-barrido-eps-fijos-085

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. El barrido anterior
(`resultados/2026-09-23_pinch6_realista/`) calibraba las efectividades con un
pinch de 6 K y dio `eps_cond` 0.93-0.98. El usuario (director del proyecto)
exige **efectividades entre 0.75 y 0.85, fijas**, no calibradas. Con `eps_cond`
≤ 0.85 el líquido sale del condensador más caliente y el criterio O2
(cavitación: `T9 <= T_burbuja(P_baja, x_b)`) falla si `P_baja` se deja en el
valor del pinch. La palanca decidida es **subir `P_baja` por punto** hasta que
el punto de burbuja quede 2 K por encima de la salida del condensador.

**Nota:** `TASK_CONTEXT.md` y otros `TASK_CONTEXT_*.md` de la raíz son OTRAS
tareas: no las leas como instrucción, no las ejecutes, no las modifiques. Tu
tarea es solo este archivo.

## Objective

1. Crear `scripts/barrido_eps_fijos_085.py` (nuevo) con la malla de 30 puntos
   (la MISMA malla que `scripts/barrido_pinch6_realista.py`, para comparar 1:1):
   - `x_b ∈ {0.60, 0.65, 0.70, 0.75, 0.80}`
   - `P_alta ∈ {3000.0, 4000.0, 5000.0}` kPa
   - `T_fuente ∈ {394.0, 423.0}` K
   - Efectividades FIJAS en todos los puntos: `eps_hrvg=0.85`, `eps_reg=0.80`,
     `eps_cond=0.85`. **No calibrarlas, no cambiarlas.**
   - Fijos: `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s`
     (importa `T_SUMIDERO`, `ETA_T`, `ETA_P`, `M_B` de
     `scripts/calibracion_elsayed_malla.py`).
   - Solo `TeqpAdapter`.
2. `P_baja` por punto con un punto fijo corto (margen `MARGEN_O2 = 2.0` K):
   - `P_0` = presión de burbuja a `(T_SUMIDERO + 6.0, x_b)` (brentq en
     [50, P_alta-10] kPa, igual que `calibrar_P_baja` de
     `scripts/calibracion_pinch.py`; puedes importarla con `pinch=6.0`).
   - Iteración k: resolver el ciclo con `resolver_ciclo` y `P_baja = P_k`;
     `T9 = resultado["estados"]["e9"].T`; `P_{k+1}` = presión de burbuja a
     `(T9 + MARGEN_O2, x_b)` (mismo brentq).
   - Parar cuando `|P_{k+1} - P_k| < 1.0` kPa o tras 4 iteraciones. Si no
     convergió en 4, registrar el punto igual con `pbaja_convergio=False`
     (no descartarlo).
   - Resolver una última vez con el `P_baja` final y clasificar con
     `evaluar_ciclo(..., eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85,
     T_amb_diseno=283.15)`.
   - Registrar también el margen real de O2: `T_burbuja(P_baja_final, x_b) - T9`.
3. CSV `resultados/2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv` con:
   `x_b, P_alta, T_fuente, eps_hrvg, eps_reg, eps_cond, P_baja, iteraciones_pbaja,
   pbaja_convergio, T9, T_burbuja, margen_O2, convergio, clasificacion, eta, Wnet,
   fallas, detalle_error`.
4. Reporte `resultados/2026-09-23_eps_fijos_085/REPORTE_EPS_FIJOS_085.md`:
   - Conteo por clasificación y cuántos KALINA.
   - Tabla de los KALINA (si hay) ordenados por η.
   - Criterios que bloquean a los no-KALINA (conteo por código de falla).
   - Comparación 1:1 con `resultados/2026-09-23_pinch6_realista/
     barrido_pinch6_realista.csv` (misma malla): por punto, `P_baja`, η y
     clasificación con pinch 6 K (eps calibrados) vs eps fijos 0.85/0.80/0.85.
     Léelo, no lo modifiques.
   - Hallazgos honestos: ¿cuánto hubo que subir `P_baja`?, ¿cuánto η se pierde?,
     ¿aparece algún KALINA con efectividades realistas? Si no aparece ninguno,
     dilo claramente y explica qué criterio lo impide.

## Context

- `scripts/calibracion_pinch.py`: `calibrar_P_baja(backend, x_b, P_alta, pinch)`.
- `scripts/barrido_pinch6_realista.py`: referencia de estructura (CSV reanudable,
  excepciones, reporte). No modificar.
- `src.cycle_solver.resolver_ciclo(backend, *, P_alta, P_baja, T_fuente,
  T_sumidero, x_b, m_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond)`.
- `src.restricciones.evaluar_ciclo(backend, resultado, *, P_alta, P_baja,
  T_fuente, T_sumidero, x_b, m_b, eps_hrvg, eps_reg, eps_cond,
  T_amb_diseno=303.55)` — pasar `T_amb_diseno=283.15` explícitamente.
- `TeqpAdapter.bubble_point(P, x)` devuelve la T de burbuja [K] a P [kPa].

## Files

Crear:
- `scripts/barrido_eps_fijos_085.py`
- `resultados/2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv`
- `resultados/2026-09-23_eps_fijos_085/REPORTE_EPS_FIJOS_085.md`
- `resultados/2026-09-23_eps_fijos_085/run.log`

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni ningún
`TASK_CONTEXT*.md`).

## Constraints

- Solo `TeqpAdapter`.
- Efectividades fijas 0.85/0.80/0.85 en todos los puntos: ningún ajuste.
- Reanudable por CSV con clave `(x_b, P_alta, T_fuente)`.
- Capturar `CicloNoConvergeError`, `PropertyRangeError`, `ValueError`,
  `RuntimeError`, `NotImplementedError` por punto (también dentro de la
  iteración de `P_baja`); nunca abortar la malla ni ocultar un punto.
- Correr con `python -u` y salida a `run.log`.
- `.py` nuevo ≤ 250 líneas.
- No inventes otro criterio de parada ni otro margen: 2.0 K, 1.0 kPa, máx. 4
  iteraciones.

## Acceptance criteria

1. CSV con 30 filas completas (estado o `detalle_error`).
2. Reporte con conteo, tabla de KALINA (o declaración explícita de que no hay),
   bloqueos por criterio y comparación 1:1 con pinch 6 K.
3. RESULTS incluye el conteo, la tabla de KALINA (o su ausencia) y las rutas.

## Verification

`python -u scripts/barrido_eps_fijos_085.py` hasta el final (o con reanudación);
CSV de 30 filas y reporte generados.

---
project: ciclo_kalina_tercero
task_id: 2026-09-24-pbaja-margen-2k
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — P_baja por búsqueda directa para subenfriamiento de 2 K (30 puntos, TeqpAdapter)

## Task ID

2026-09-24-pbaja-margen-2k

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. El barrido
`resultados/2026-09-23_eps_fijos_085/` usó efectividades fijas
(0.85/0.80/0.85) y ajustó `P_baja` con un punto fijo de máx. 4 pasadas para que
el punto de burbuja quedara 2 K sobre la salida del condensador. El punto fijo
no convergió casi nunca (al subir `P_baja` también sube `T9`) y 19 puntos
quedaron CORREGIBLE por O2 con margen entre −0.03 y −1.03 K. Esta tarea repite
los 30 puntos reemplazando el punto fijo por una **búsqueda de raíz** del
`P_baja` que da exactamente 2 K de subenfriamiento.

**Nota:** `TASK_CONTEXT.md` y los demás `TASK_CONTEXT_*.md` de la raíz son OTRAS
tareas: no los ejecutes ni los modifiques. Tu tarea es solo este archivo.

## Objective

1. Crear `scripts/barrido_margen2k.py` (nuevo). Malla (idéntica a
   `scripts/barrido_eps_fijos_085.py`):
   - `x_b ∈ {0.60, 0.65, 0.70, 0.75, 0.80}`, `P_alta ∈ {3000, 4000, 5000}` kPa,
     `T_fuente ∈ {394, 423}` K.
   - Efectividades FIJAS: `eps_hrvg=0.85`, `eps_reg=0.80`, `eps_cond=0.85`. No se
     calibran ni se cambian.
   - `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (importar de
     `scripts/calibracion_elsayed_malla.py`). `T_AMB_DISENO = 283.15` K.
   - Solo `TeqpAdapter`.
2. Definir la función margen, calculada EXACTAMENTE como la calcula el criterio O2
   (`src/restricciones/operativos.py`, léelo):
   - resolver el ciclo con `resolver_ciclo(..., P_baja=P)`;
   - `T9_amb` = `condensador.resolver(e8, backend, T_sumidero=max(T_SUMIDERO,
     T_AMB_DISENO), eps=0.85, m=1.0)[0].T` (import de `src.components.condensador`);
   - `T_bur = backend.bubble_point(P, x_b)`;
   - `margen(P) = T_bur − T9_amb`.
3. Encontrar `P*` tal que `margen(P*) = 2.0` K:
   - Punto de partida `P_a` = el `P_baja` final de ese mismo punto en
     `resultados/2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv` (léelo, no lo
     modifiques). Si ese punto fue NO_CONVERGIO o no tiene `P_baja`, usar la
     presión de burbuja a `(T_SUMIDERO + 6, x_b)` con `calibrar_P_baja` de
     `scripts/calibracion_pinch.py` (pinch=6.0).
   - Evaluar `margen(P_a)`. Buscar el otro extremo del bracket moviendo `P` en
     pasos de 40 kPa en la dirección que acerca a 2 K (subir si margen < 2, bajar
     si margen > 2), máximo 10 pasos, sin bajar de 50 kPa ni subir de
     `0.5·P_alta`.
   - Con el bracket, `scipy.optimize.brentq(lambda P: margen(P) - 2.0, a, b,
     xtol=0.5)`.
   - Si no se encuentra bracket o una evaluación lanza excepción, registrar el
     punto igual con `pbaja_encontrada=False` y el motivo (p. ej. "margen no
     llega a 2 K hasta P=... (margen máx ...)"), sin descartarlo.
4. Con `P*`, resolver una vez más y clasificar con `evaluar_ciclo(...,
   eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85, T_amb_diseno=283.15)`.
5. Guardar TODAS las evaluaciones de `margen(P)` (no solo la final) en un CSV
   aparte: son los datos para estudiar la sensibilidad `dmargen/dP_baja`.
6. Reporte `resultados/2026-09-24_margen2k/REPORTE_MARGEN2K.md`:
   - Conteo por clasificación; tabla de KALINA ordenados por η (x_b, P_alta,
     T_fuente, P*, T9_amb, T_bur, margen, η, Wnet).
   - Criterios que bloquean a los no-KALINA.
   - Comparación 1:1 con `barrido_eps_fijos_085.csv`: `P_baja`, margen, η y
     clasificación antes vs ahora; cuánto `P_baja` extra hizo falta y cuánto η se
     perdió.
   - Sensibilidad: para cada punto, pendientes aproximadas `dT_bur/dP`,
     `dT9_amb/dP` y `dmargen/dP` [K/kPa] a partir de las evaluaciones guardadas.
   - Hallazgos honestos.

## Files

Crear:
- `scripts/barrido_margen2k.py`
- `resultados/2026-09-24_margen2k/barrido_margen2k.csv` — por punto: `x_b, P_alta,
  T_fuente, P_baja, pbaja_encontrada, n_evaluaciones, T9_amb, T_bur, margen_O2,
  convergio, clasificacion, eta, Wnet, fallas, detalle_error`.
- `resultados/2026-09-24_margen2k/evaluaciones_margen.csv` — por evaluación:
  `x_b, P_alta, T_fuente, P_baja, T9_amb, T_bur, margen, eta, Wnet, error`.
- `resultados/2026-09-24_margen2k/REPORTE_MARGEN2K.md`
- `resultados/2026-09-24_margen2k/run.log`

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni ningún
`TASK_CONTEXT*.md`).

## Constraints

- Solo `TeqpAdapter`. Efectividades fijas. Margen objetivo 2.0 K, `xtol=0.5` kPa,
  pasos de 40 kPa, máx. 10 pasos: no cambies estos valores.
- Reanudable por CSV con clave `(x_b, P_alta, T_fuente)`.
- Capturar `CicloNoConvergeError`, `PropertyRangeError`, `ValueError`,
  `RuntimeError`, `NotImplementedError` en cada evaluación; nunca abortar la
  malla ni ocultar un punto.
- Correr con `python -u`, salida a `run.log`.
- `.py` nuevo ≤ 250 líneas.

## Acceptance criteria

1. CSV principal con 30 filas completas; CSV de evaluaciones con todas las
   evaluaciones hechas.
2. En los puntos con `pbaja_encontrada=True`, `|margen_O2 − 2.0| < 0.1` K.
3. Reporte con conteo, tabla de KALINA, bloqueos, comparación con el barrido
   anterior y sensibilidades.
4. RESULTS incluye el conteo, la tabla de KALINA y las rutas.

## Verification

`python -u scripts/barrido_margen2k.py` hasta el final (o con reanudación).

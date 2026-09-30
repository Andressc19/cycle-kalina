---
project: ciclo_kalina_tercero
task_id: 2026-09-23-barrido-pinch6-realista
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Barrido realista con pinch de 6 K (30 puntos, TeqpAdapter)

## Task ID

2026-09-23-barrido-pinch6-realista

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. Los barridos del
2026-09-22 (ver `resultados/BITACORA_BARRIDOS.md`) calibraron `P_baja` y los tres
`eps` con un pinch de 4 K. Eso dio efectividades muy altas (`eps_cond` 0.93-0.975,
un `eps_reg` = 0.999 recortado) y un margen de O2 de solo ~4 K por construcción
(15 puntos fallan O2 por centésimas). El usuario pide iteraciones con datos
realistas: sin efectividades de 0.99 y sin fracciones de amoníaco bajas. Esta tarea
repite el método con **pinch de 6 K** en una malla nueva.

**Nota:** `TASK_CONTEXT.md` (raíz) contiene OTRA tarea distinta (límites de teqp)
que NO es la tuya: no la leas como instrucción, no la ejecutes, no la modifiques.

## Objective

1. Crear `scripts/calibracion_pinch.py` (nuevo): mismo método EXACTO que
   `scripts/calibracion_elsayed_malla.py` (léelo completo, NO lo modifiques), pero
   con el pinch como parámetro en vez de la constante `PINCH=4.0`:
   - `calibrar_P_baja(backend, x_b, P_alta, pinch)`: presión de burbuja a
     `(T_sumidero + pinch, x_b)`, brentq en [50, P_alta-10] kPa.
   - `calibrar_eps(backend, *, x_b, P_alta, P_baja, T_fuente, pinch)`: paso base con
     eps (0.85, 0.75, 0.80), despeje cerrado para `T2 = T_fuente - pinch`,
     `T6 = T10 + pinch`, `T9 = T_sumidero + pinch`, recorte a [0.01, 0.999],
     re-resolución. Devuelve `dict(eps_hrvg, eps_reg, eps_cond, resultado)`.
   - Reutiliza por import las constantes `T_SUMIDERO`, `ETA_T`, `ETA_P`, `M_B`,
     `EPS_PARTIDA` de `calibracion_elsayed_malla.py`.
   - Verificación obligatoria: con `pinch=4.0` y el caso base (x_b=0.55,
     P_alta=1500, T_fuente=373) debe dar el mismo `P_baja` (273.5454 kPa) y los
     mismos eps (0.8882/0.9380/0.9625, ±1e-3) que el script original. Reporta el
     resultado de esta verificación en TESTS.
2. Crear `scripts/barrido_pinch6_realista.py` (nuevo) con la malla de 30 puntos:
   - `pinch = 6.0` K
   - `x_b ∈ {0.60, 0.65, 0.70, 0.75, 0.80}`
   - `T_fuente ∈ {394.0, 423.0}` K (394 K ≈ fuente de Húsavík)
   - `P_alta ∈ {3000.0, 4000.0, 5000.0}` kPa
   - Fijos: `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s`.
   - Clasificar con `evaluar_ciclo(..., T_amb_diseno=283.15)` (piso realista ya
     validado; pásalo explícitamente).
   - Solo `TeqpAdapter`.
3. CSV `resultados/2026-09-23_pinch6_realista/barrido_pinch6_realista.csv` con:
   `x_b, P_alta, T_fuente, pinch, P_baja, eps_hrvg, eps_reg, eps_cond, eps_realista,
   convergio, clasificacion, eta, Wnet, fallas, detalle_error`.
   - `eps_realista` = `True` si los tres eps son ≤ 0.95, `False` si alguno es > 0.95
     (incluye los recortados a 0.999). Es solo una marca: NO descartes el punto.
4. Reporte `resultados/2026-09-23_pinch6_realista/REPORTE_PINCH6_REALISTA.md`:
   - Conteo por clasificación, y aparte cuántos son **KALINA con eps_realista=True**
     (el número que le importa al usuario).
   - Tabla de los KALINA realistas ordenados por η (x_b, P_alta, T_fuente, P_baja,
     los 3 eps, η, Wnet).
   - Mejor punto por `x_b`.
   - Comparación contra pinch 4 K: para los puntos de la malla que también
     existen en `resultados/2026-09-22_o2_tamb_realista/reclasificacion_o2.csv`
     (mismo x_b, P_alta, T_fuente; solo coinciden x_b 0.60/0.65/0.70, T_fuente 423,
     P_alta 3000/5000), mostrar η y clasificación con pinch 4 vs pinch 6 (usa la
     columna `clasificacion_realista`). Léelo, no lo modifiques.
   - Hallazgos: ¿bajaron los eps a valores realistas?, ¿se cerró O2 con más margen?,
     ¿cuánto η se pierde por el pinch mayor? Sé honesto si el resultado no es el
     esperado.

## Context

- `scripts/calibracion_elsayed_malla.py`: método a generalizar (no modificar).
- `scripts/frontera_tfuente_teqp.py` y `scripts/reclasificar_o2_tamb_realista.py`:
  referencia de estructura (CSV reanudable, manejo de excepciones, reporte). No
  modificar.
- `src.restricciones.evaluar_ciclo(backend, resultado, *, P_alta, P_baja, T_fuente,
  T_sumidero, x_b, m_b, eps_hrvg, eps_reg, eps_cond, T_amb_diseno=303.55)`.

## Files

Crear:
- `scripts/calibracion_pinch.py`
- `scripts/barrido_pinch6_realista.py`
- `resultados/2026-09-23_pinch6_realista/barrido_pinch6_realista.csv`
- `resultados/2026-09-23_pinch6_realista/REPORTE_PINCH6_REALISTA.md`

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni
`TASK_CONTEXT.md`).

## Constraints

- Solo `TeqpAdapter` (pedido explícito del usuario).
- Reanudable por CSV con clave `(x_b, P_alta, T_fuente)`.
- Capturar `CicloNoConvergeError`, `PropertyRangeError`, `ValueError`,
  `RuntimeError` por punto; nunca abortar la malla ni ocultar un punto.
- Correr el barrido redirigiendo la salida a
  `resultados/2026-09-23_pinch6_realista/run.log` y con `python -u`.
- Archivos `.py` nuevos ≤ 250 líneas cada uno.

## Acceptance criteria

1. Verificación de `calibracion_pinch.py` con pinch=4 reproduce el caso base.
2. CSV con 30 filas completas (estado o `detalle_error`).
3. El reporte da explícitamente el número de KALINA con eps realistas y la
   comparación pinch 4 vs pinch 6.
4. RESULTS incluye el conteo, la tabla de KALINA realistas y las rutas.

## Verification

`python -u scripts/barrido_pinch6_realista.py` hasta el final (o con
reanudación); CSV de 30 filas y reporte generados.

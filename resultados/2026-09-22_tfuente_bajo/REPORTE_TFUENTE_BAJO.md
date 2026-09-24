# Reporte — T_fuente bajo (333 K) con x_b variable

Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-22-tfuente-bajo-barrido-xb (no toca `src/`).
5 puntos: `T_fuente=333 K` y `P_alta=1500 kPa` fijos, `x_b` en (0.55, 0.6, 0.65, 0.7, 0.75); `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (importadas de `calibracion_elsayed_malla.py`).

## Resumen ejecutivo

Convergen 1 de 5 puntos y 0 se evaluan con clasificacion (**0 KALINA**); comparacion vs `reclasificacion_o2.csv` (mismo `x_b`, `P_alta=1500`, `T_fuente=373 K`, col `clasificacion_realista`):

## Tabla de los 5 puntos vs T_fuente=373 K

| x_b | T_fuente [K] | Clasif | eta | Wnet [kW] | Fallas | T_fuente ref [K] | Clasif ref | eta ref | Wnet ref [kW] | Fallas ref | Δη [pp] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 333 | **NO_CONVERGIO** | - | - | - | 373 | **KALINA** | 0.110554 | 49.2456 | - | - |
| 0.60 | 333 | **NO_CONVERGIO** | - | - | - | 373 | **KALINA** | 0.102503 | 59.6543 | - | - |
| 0.65 | 333 | **NO_CONVERGIO** | - | - | - | 373 | **KALINA** | 0.094917 | 67.7003 | - | - |
| 0.70 | 333 | **NO_CONVERGIO** | - | - | - | 373 | **CORREGIBLE** | 0.088348 | 74.1732 | O2 | - |
| 0.75 | 333 | **NO_CONVERGIO** | 0.072354 | 22.1434 | - | 373 | no disponible | - | - | - | - |

## Comentario: ayudar / perjudicar / no cambiar

**Conclusion: bajar `T_fuente` 373 -> 333 K **perjudica** drasticamente la evaluabilidad**: 4 de 5 puntos no convergen por `PropertyRangeError` (liquido comprimido profundo a `P_alta=1500` con pinch de 4 K, ~329 K, fuera del dominio de teqp) y el quinto converge pero su evaluacion (O2, `bubble_point`) tampoco entra en dominio. Ningun punto es clasificable a 333 K, frente a 3 KALINA + 1 CORREGIBLE(O2) a 373 K con el mismo metodo y piso realista. Es una limitacion de cobertura del motor, no una regla termodinamica general del ciclo.

- **x_b=0.55**: el ciclo NO converge a 333 K — PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-11814.3
- **x_b=0.6**: el ciclo NO converge a 333 K — PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-8312.7 
- **x_b=0.65**: el ciclo NO converge a 333 K — PropertyRangeError: equilibrio_liquido_vapor(P=1500.0 kPa, T=308.86782813541754 K): no existe equilibrio bifásico para ninguna composición (T fuera de
- **x_b=0.7**: el ciclo NO converge a 333 K — PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-2911.22
- **x_b=0.75**: el ciclo SI converge (eta=0.072354) pero `evaluar_ciclo` falla: PropertyRangeError: bubble_point(P, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o).

## Metodologia y limites

- `P_baja`/`eps_*` calibrados por punto (import de `calibracion_elsayed_malla.py`); un resolve; piso realista fijo `T_amb_diseno=283.15 K` = `T_sumidero`. Ningun punto se oculta: `convergio=False` + `detalle_error` real.
- x_b=0.75 extiende la malla anterior (llegaba a 0.70); su equivalente a 373 K no existe todavia.
- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78; T_fuente 333-473 K.

## Entregables

- `exploracion_tfuente_bajo.csv` — 5 filas: x_b, P_alta, T_fuente, P_baja, eps_hrvg, eps_reg, eps_cond, convergio, clasificacion, eta, Wnet, fallas, detalle_error.
- Este reporte.

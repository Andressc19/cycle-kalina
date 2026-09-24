# Reporte — Frontera de cobertura de teqp entre 333 K y 373 K

Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-22-frontera-tfuente-bajo (no toca `src/`).
Malla 3x5 = 15 puntos: `T_fuente` en (340.0, 350.0, 360.0), `x_b` en (0.55, 0.6, 0.65, 0.7, 0.75), `P_alta=1500 kPa` fijo; `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (importadas de `calibracion_elsayed_malla.py`), `T_amb_diseno=283.15 K`.

## Resumen ejecutivo

Bordes ya conocidos (no recalcados): 333 K -> 4/5 fallan con `PropertyRangeError` (`2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv`); 373 K -> 3 KALINA + 1 CORREGIBLE (`2026-09-22_o2_tamb_realista/reclasificacion_o2.csv`). Aqui: 340 K -> 3/5 convergen, 3/5 evaluan; 350 K -> 4/5 convergen, 4/5 evaluan; 360 K -> 5/5 convergen, 5/5 evaluan.

## Mapa T_fuente x x_b (15 puntos)

| T_fuente \ x_b | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | converge | evaluan |
|---|---|---|---|---|---|---|---|
| 340 K | **NO** (PropertyRangeError) | **NO** (PropertyRangeError) | KALINA (η=0.075056) | KALINA (η=0.079802) | KALINA (η=0.077264) | 3/5 | 3/5 |
| 350 K | **NO** (PropertyRangeError) | KALINA (η=0.09057) | KALINA (η=0.089014) | KALINA (η=0.084504) | KALINA (η=0.079918) | 4/5 | 4/5 |
| 360 K | KALINA (η=0.102576) | KALINA (η=0.098719) | KALINA (η=0.095852) | KALINA (η=0.086787) | CORREGIBLE (η=0.081667) | 5/5 | 5/5 |

## Conclusion explicita

**Frontera: T_fuente = 360 K** — a partir de ese valor los 5 x_b convergen y pasan `evaluar_ciclo` con el piso realista 283.15 K. Por debajo no hay cobertura completa (340 K -> 3/5 convergen, 3/5 evaluan; 350 K -> 4/5 convergen, 4/5 evaluan; 360 K -> 5/5 convergen, 5/5 evaluan).

**La frontera NO es uniforme: depende de x_b** (x_b=0.55: 360 K; x_b=0.60: 350 K; x_b=0.65: 340 K; x_b=0.70: 340 K; x_b=0.75: 340 K) — primera T limpia entre 340 y 360 K en esta ventana.

Patron de errores (todos en el CSV): PropertyRangeError x3. El `PropertyRangeError` dominante a 333 K (liquido comprimido fuera del dominio de teqp cerca de T1~329 K) SIGUE PRESENTE aqui.

## Puntos con error (nunca ocultados)

- **T_fuente=340 K, x_b=0.55**: NO converge — `PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-5459.37`
- **T_fuente=340 K, x_b=0.60**: NO converge — `PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-1.0326e`
- **T_fuente=350 K, x_b=0.55**: NO converge — `PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: h=-7322.93`

## Metodologia y limites

- `P_baja`/`eps_*` calibrados por punto (import directo de `calibracion_elsayed_malla.py`); un resolve; piso realista fijo `T_amb_diseno=283.15 K`. Captura de `CicloNoConvergeError`/`PropertyRangeError` sin abortar la malla; ningun punto se oculta (`convergio=False` + `detalle_error` real tal cual lo reporta el motor).
- Reanudable por CSV sobre clave `(x_b, T_fuente)`.
- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78; 333-473 K.

## Entregables

- `frontera_tfuente_teqp.csv` — 15 filas: x_b, P_alta, T_fuente, P_baja, eps_hrvg, eps_reg, eps_cond, convergio, clasificacion, eta, Wnet, fallas, detalle_error.
- Este reporte.

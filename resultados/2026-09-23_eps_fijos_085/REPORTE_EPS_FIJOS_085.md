# Reporte — Barrido efectividades fijas 0.85/0.80/0.85 (30 puntos)

Fecha: 2026-09-23 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-23-barrido-eps-fijos-085 (no toca `src/` ni archivos existentes).
Grid: 5 x 3 x 2 = 30 puntos; `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (de `calibracion_elsayed_malla.py`); efectividades **fijas** `eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85`. P_baja: P_0 = burbuja a (`T_sumidero`+6 K, x_b) + punto fijo (margen O2 2.0 K, tol 1.0 kPa, max 4 iters). Clasificacion con `T_amb_diseno=283.15 K`.

## Resumen ejecutivo

**KALINA: 7 de 30 puntos** con eps fijos 0.85/0.80/0.85. Convergen 26; los demas estan en el CSV con `detalle_error`. P_baja subio 179.1 kPa de media vs pinch 6 K; eta media baja 2.49 pp.

## Conteo por clasificacion

| Clasificacion | Puntos |
|---|---|
| KALINA | 7 |
| VALIDO_ADVERTENCIA | 0 |
| CORREGIBLE | 19 |
| DEGENERADO | 0 |
| INVIABLE | 0 |
| NO_CONVERGIO | 4 |
| **Total** | **30** |
| **KALINA** | **7** |

## KALINA con efectividades fijas, ordenados por eta

| x_b | P_alta | T_fuente | P_baja | T9 | margen_O2 | eta | Wnet [kW] |
|---|---|---|---|---|---|---|---|
| 0.6 | 5000.0 | 423.0 | 516.513364 | 298.591742 | 1.037992 | 0.121969 | 57.6139 |
| 0.75 | 5000.0 | 394.0 | 729.605409 | 297.619946 | 0.510381 | 0.111448 | 49.2387 |
| 0.6 | 3000.0 | 394.0 | 511.559277 | 297.915143 | 1.416678 | 0.105004 | 46.5363 |
| 0.65 | 4000.0 | 394.0 | 565.081001 | 295.481414 | 1.972106 | 0.103933 | 38.6801 |
| 0.7 | 5000.0 | 394.0 | 598.125929 | 293.150771 | 1.999609 | 0.091635 | 27.4122 |
| 0.6 | 4000.0 | 394.0 | 426.235541 | 291.414112 | 2.407949 | 0.080235 | 19.4705 |
| 0.65 | 5000.0 | 394.0 | 449.959437 | 288.553933 | 1.999985 | 0.009185 | 1.372 |

## Criterios que bloquean a los no-KALINA

| Criterio | Puntos |
|---|---|
| O2 | 19 |
| NO_CONVERGIO | 4 |

## Comparacion 1:1 — pinch 6 K (eps calibrados) vs eps fijos 0.85/0.80/0.85 (30 puntos comunes)

| x_b | P_alta | T_fuente | P_baja 6K | P_baja fijos | dP_baja [kPa] | eta 6K | eta fijos | deta [pp] | clasif 6K | clasif fijos |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.6 | 3000.0 | 394.0 | 360.842 | 511.559 | +150.7 | 0.131964 | 0.105004 | -2.70 | KALINA | KALINA |
| 0.6 | 4000.0 | 394.0 | 360.842 | 426.236 | +65.4 | - | 0.080235 | - | NO_CONVERGIO | KALINA |
| 0.6 | 5000.0 | 394.0 | 360.842 | 360.842 | +0.0 | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.6 | 3000.0 | 423.0 | 360.842 | 601.65 | +240.8 | 0.140771 | 0.110359 | -3.04 | KALINA | CORREGIBLE |
| 0.6 | 4000.0 | 423.0 | 360.842 | 552.737 | +191.9 | 0.154607 | 0.123887 | -3.07 | KALINA | CORREGIBLE |
| 0.6 | 5000.0 | 423.0 | 360.842 | 516.513 | +155.7 | 0.156843 | 0.121969 | -3.49 | KALINA | KALINA |
| 0.65 | 3000.0 | 394.0 | 426.697 | 617.141 | +190.4 | 0.130284 | 0.105294 | -2.50 | KALINA | CORREGIBLE |
| 0.65 | 4000.0 | 394.0 | 426.697 | 565.081 | +138.4 | 0.128502 | 0.103933 | -2.46 | KALINA | KALINA |
| 0.65 | 5000.0 | 394.0 | 426.697 | 449.959 | +23.3 | - | 0.009185 | - | NO_CONVERGIO | KALINA |
| 0.65 | 3000.0 | 423.0 | 426.697 | 704.201 | +277.5 | 0.13458 | 0.105756 | -2.88 | KALINA | CORREGIBLE |
| 0.65 | 4000.0 | 423.0 | 426.697 | 656.956 | +230.3 | 0.150851 | 0.123154 | -2.77 | KALINA | CORREGIBLE |
| 0.65 | 5000.0 | 423.0 | 426.697 | 622.724 | +196.0 | 0.158416 | 0.128589 | -2.98 | KALINA | CORREGIBLE |
| 0.7 | 3000.0 | 394.0 | 488.459 | 708.093 | +219.6 | - | 0.104061 | - | NO_CONVERGIO | CORREGIBLE |
| 0.7 | 4000.0 | 394.0 | 488.459 | 675.748 | +187.3 | 0.1354 | 0.111606 | -2.38 | KALINA | CORREGIBLE |
| 0.7 | 5000.0 | 394.0 | 488.459 | 598.126 | +109.7 | - | 0.091635 | - | NO_CONVERGIO | KALINA |
| 0.7 | 3000.0 | 423.0 | 488.459 | 784.859 | +296.4 | 0.129452 | 0.102702 | -2.68 | KALINA | CORREGIBLE |
| 0.7 | 4000.0 | 423.0 | 488.459 | 743.206 | +254.7 | 0.147299 | 0.122436 | -2.49 | KALINA | CORREGIBLE |
| 0.7 | 5000.0 | 423.0 | 488.459 | 713.742 | +225.3 | 0.157547 | 0.131771 | -2.58 | KALINA | CORREGIBLE |
| 0.75 | 3000.0 | 394.0 | 544.028 | 780.025 | +236.0 | 0.124502 | 0.102879 | -2.16 | KALINA | CORREGIBLE |
| 0.75 | 4000.0 | 394.0 | 544.028 | 754.22 | +210.2 | 0.136657 | 0.11551 | -2.11 | KALINA | CORREGIBLE |
| 0.75 | 5000.0 | 394.0 | 544.028 | 729.605 | +185.6 | 0.132273 | 0.111448 | -2.08 | KALINA | KALINA |
| 0.75 | 3000.0 | 423.0 | 544.028 | 841.813 | +297.8 | 0.125403 | 0.101204 | -2.42 | CORREGIBLE | CORREGIBLE |
| 0.75 | 4000.0 | 423.0 | 544.028 | 607.963 | +63.9 | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.75 | 5000.0 | 423.0 | 544.028 | 785.177 | +241.1 | 0.156187 | 0.13399 | -2.22 | KALINA | CORREGIBLE |
| 0.8 | 3000.0 | 394.0 | 592.935 | 834.508 | +241.6 | 0.122053 | 0.102078 | -2.00 | CORREGIBLE | CORREGIBLE |
| 0.8 | 4000.0 | 394.0 | 592.935 | 816.575 | +223.6 | 0.136365 | 0.117475 | -1.89 | KALINA | CORREGIBLE |
| 0.8 | 5000.0 | 394.0 | 592.935 | 798.889 | +206.0 | 0.14078 | 0.121517 | -1.93 | KALINA | CORREGIBLE |
| 0.8 | 3000.0 | 423.0 | 592.935 | 660.399 | +67.5 | 0.122281 | - | - | CORREGIBLE | NO_CONVERGIO |
| 0.8 | 4000.0 | 423.0 | 592.935 | 592.935 | +0.0 | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.8 | 5000.0 | 423.0 | 592.935 | 838.776 | +245.8 | 0.15492 | 0.13599 | -1.89 | CORREGIBLE | CORREGIBLE |

## Hallazgos

1. **KALINA = 7 de 30** (tabla arriba).
2. **Subida de P_baja**: promedio 179.1 kPa, maximo 297.8 kPa vs pinch 6 K (eps calibrados) en 30 puntos con par; punto fijo sin cerrar en 28.
3. **Costo de eta**: se pierden 2.49 pp de eta media (fijos vs calibrados 6 K) en 22 puntos comunes.
4. **Bloqueo dominante**: O2 (19); O2 en 19 convergente(s), O1 en 0.
5. **Margen O2 medio** en convergentes: 0.10 K; iteraciones del punto fijo: media 3.60 de 4.

## Metodologia y limites

- `P_0` = burbuja a (`T_sumidero`+6 K, x_b) via `calibracion_pinch.calibrar_P_baja(pinch=6.0)`; en cada iteracion se resuelve el ciclo con `P_baja=P_k`, `T9=estados[e9].T` y `P_k+1` = burbuja a (`T9`+2 K, x_b); parada |dP|<1.0 kPa o 4 iters; si no cierra se registra igual con `pbaja_convergio=False`.
- Resolucion final con el P_baja cerrado y clasificacion con `evaluar_ciclo(..., T_amb_diseno=283.15)` \[margen real O2 = `T_burbuja(P_baja, x_b) - T9`].
- Captura de `CicloNoConvergeError`/`PropertyRangeError`/`ValueError`/`RuntimeError`/`NotImplementedError` por punto y dentro de la iteracion de P_baja; reanudable por CSV; ningun punto se oculta.
- Ventana: T_fuente 394 K (aprox. Husavik) y 423 K; P_alta 3000-5000 kPa; x_b 0.60-0.80.

## Entregables

- `barrido_eps_fijos_085.csv` (30 filas: x_b, P_alta, T_fuente, eps_hrvg, eps_reg, eps_cond, P_baja, iteraciones_pbaja, pbaja_convergio, T9, T_burbuja, margen_O2, convergio, clasificacion, eta, Wnet, fallas, detalle_error).
- `run.log`.
- Este reporte.

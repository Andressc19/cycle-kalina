# Reporte — Reclasificacion de O2 con piso realista (T_amb_diseno=283.15 K vs 303.55 K)

Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-22-reclasificar-o2-tamb-realista (no toca `src/`).
Grid: 60 puntos — x_b x P_alta x T_fuente = 4 x 5 x 3; `T_sumidero=283.0 K` fijo, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s`. Un solo resolve por punto; `evaluar_ciclo` x2 sobre el mismo resultado: `T_amb_diseno=303.55 K` (tropical) y `T_amb_diseno=283.15 K` (= `T_sumidero` real, 10 C, criterio de la Fase 3).

## Resumen ejecutivo

**KALINA: 0 punto(s) con el piso tropical vs **16** con el piso realista** de 60. Convergen 33; cambian 18; no-KALINA a KALINA: 16.

## Conteo por clasificacion, lado a lado

| Clasificacion | Tropical (303.55 K) | Realista (283.15 K) |
|---|---|---|
| KALINA | 0 | 16 |
| VALIDO_ADVERTENCIA | 0 | 2 |
| CORREGIBLE | 32 | 14 |
| DEGENERADO | 0 | 0 |
| INVIABLE | 0 | 0 |
| NO_CONVERGIO | 28 | 28 |
| **Total** | **60** | **60** |

## Puntos que cambian de clasificacion al bajar el piso de O2

| x_b | P_alta [kPa] | T_fuente [K] | eta | Wnet [kW] | Tropical (fallas) | Realista (fallas) |
|---|---|---|---|---|---|---|
| 0.55 | 1000.0 | 373.0 | 0.087667 | 57.8669 | CORREGIBLE (O2) | KALINA (-) |
| 0.55 | 1500.0 | 373.0 | 0.110554 | 49.2456 | CORREGIBLE (O2) | KALINA (-) |
| 0.55 | 2000.0 | 373.0 | 0.117791 | 30.4924 | CORREGIBLE (O2) | KALINA (-) |
| 0.55 | 3000.0 | 423.0 | 0.152782 | 111.8096 | CORREGIBLE (O2) | KALINA (-) |
| 0.55 | 5000.0 | 423.0 | 0.158315 | 44.8012 | CORREGIBLE (O2) | KALINA (-) |
| 0.55 | 5000.0 | 463.0 | 0.176485 | 182.5052 | CORREGIBLE (O1,O2) | VALIDO_ADVERTENCIA (O1) |
| 0.6 | 1000.0 | 373.0 | 0.07686 | 60.3577 | CORREGIBLE (O2) | KALINA (-) |
| 0.6 | 1500.0 | 373.0 | 0.102503 | 59.6543 | CORREGIBLE (O2) | KALINA (-) |
| 0.6 | 2000.0 | 373.0 | 0.115983 | 47.2442 | CORREGIBLE (O2) | KALINA (-) |
| 0.6 | 3000.0 | 423.0 | 0.145299 | 128.3828 | CORREGIBLE (O2) | KALINA (-) |
| 0.6 | 5000.0 | 423.0 | 0.164886 | 74.5596 | CORREGIBLE (O2) | KALINA (-) |
| 0.65 | 1500.0 | 373.0 | 0.094917 | 67.7003 | CORREGIBLE (O2) | KALINA (-) |
| 0.65 | 2000.0 | 373.0 | 0.111221 | 61.399 | CORREGIBLE (O2) | KALINA (-) |
| 0.65 | 3000.0 | 373.0 | 0.112592 | 23.4376 | CORREGIBLE (O2) | KALINA (-) |
| 0.65 | 5000.0 | 423.0 | 0.164618 | 101.805 | CORREGIBLE (O2) | KALINA (-) |
| 0.7 | 2000.0 | 373.0 | 0.106329 | 73.6226 | CORREGIBLE (O2) | KALINA (-) |
| 0.7 | 3000.0 | 373.0 | 0.121842 | 46.336 | CORREGIBLE (O1,O2) | VALIDO_ADVERTENCIA (O1) |
| 0.7 | 5000.0 | 423.0 | 0.162815 | 127.1025 | CORREGIBLE (O2) | KALINA (-) |

## Tabla resumen por x_b — mejor punto con cada criterio

| x_b | Criterio trop | Clasif trop | eta trop | Punto trop (P_alta/T_fuente) | Criterio real | Clasif real | eta real | Punto real (P_alta/T_fuente) |
|---|---|---|---|---|---|---|---|---|
| 0.55 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.176485 | 5000.0/463.0 | KALINA | KALINA | 0.158315 | 5000.0/423.0 |
| 0.60 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.169504 | 5000.0/463.0 | KALINA | KALINA | 0.164886 | 5000.0/423.0 |
| 0.65 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.164618 | 5000.0/423.0 | KALINA | KALINA | 0.164618 | 5000.0/423.0 |
| 0.70 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.162815 | 5000.0/423.0 | KALINA | KALINA | 0.162815 | 5000.0/423.0 |

## Bloqueos por criterio (puntos convergentes)

| Criterio | Tropical | Realista |
|---|---|---|
| VALIDO_ADVERTENCIA | 0 | 0 |
| CORREGIBLE | 0 | 0 |
| DEGENERADO | 0 | 0 |
| INVIABLE | 0 | 0 |
| NO_CONVERGIO | 0 | 0 |
| C1 | 1 | 1 |
| C2 | 0 | 0 |
| C3 | 2 | 2 |

## Hallazgos

1. **El patron de la Fase 3 (rama `test/fases-sensibilidad`) SE REPITE**: bajar el piso de O2 de 303.55 K a 283.15 K abre 16 punto(s) nuevo(s) a KALINA: x_b=0.55, P_alta=1000.0, T_fuente=373.0 (eta=0.087667, Wnet=57.8669 kW); x_b=0.55, P_alta=1500.0, T_fuente=373.0 (eta=0.110554, Wnet=49.2456 kW); x_b=0.55, P_alta=2000.0, T_fuente=373.0 (eta=0.117791, Wnet=30.4924 kW); x_b=0.55, P_alta=3000.0, T_fuente=423.0 (eta=0.152782, Wnet=111.8096 kW); x_b=0.55, P_alta=5000.0, T_fuente=423.0 (eta=0.158315, Wnet=44.8012 kW); x_b=0.6, P_alta=1000.0, T_fuente=373.0 (eta=0.07686, Wnet=60.3577 kW); x_b=0.6, P_alta=1500.0, T_fuente=373.0 (eta=0.102503, Wnet=59.6543 kW); x_b=0.6, P_alta=2000.0, T_fuente=373.0 (eta=0.115983, Wnet=47.2442 kW); x_b=0.6, P_alta=3000.0, T_fuente=423.0 (eta=0.145299, Wnet=128.3828 kW); x_b=0.6, P_alta=5000.0, T_fuente=423.0 (eta=0.164886, Wnet=74.5596 kW); x_b=0.65, P_alta=1500.0, T_fuente=373.0 (eta=0.094917, Wnet=67.7003 kW); x_b=0.65, P_alta=2000.0, T_fuente=373.0 (eta=0.111221, Wnet=61.399 kW); x_b=0.65, P_alta=3000.0, T_fuente=373.0 (eta=0.112592, Wnet=23.4376 kW); x_b=0.65, P_alta=5000.0, T_fuente=423.0 (eta=0.164618, Wnet=101.805 kW); x_b=0.7, P_alta=2000.0, T_fuente=373.0 (eta=0.106329, Wnet=73.6226 kW); x_b=0.7, P_alta=5000.0, T_fuente=423.0 (eta=0.162815, Wnet=127.1025 kW).
2. O2 sigue bloqueando 15 punto(s) incluso con el piso realista (18 quedan liberados de O2 sin alcanzar KALINA); margen exacto en el log de la corrida.
3. Con el piso realista, 17 punto(s) convergente(s) siguen sin ser KALINA, bloqueados por: N2 (1), O1 (5), O2 (15), O5 (1), C1 (1), C3 (2).
4. Errores registrados (nunca ocultados): PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido ; PropertyRangeError: equilibrio_liquido_vapor(P=1000.0 kPa, T=462.8499610351539 K; PropertyRangeError: equilibrio_liquido_vapor(P=1000.0 kPa, T=462.8499711017988 K; PropertyRangeError: equilibrio_liquido_vapor(P=1000.0 kPa, T=462.8499803665554 K.

## Metodologia y limites

- `P_baja`/`eps_*` calibrados por punto (import directo de `calibracion_elsayed_malla.py`); tropical-vs-realista solo sobre `evaluar_ciclo` (re-resuelve el condensador para O2, no el ciclo). Unicamente `TeqpAdapter`; sin reintentos.
- Piso realista = mismo valor para toda la malla (283.15 K = `T_sumidero` fijo), no calibracion por punto. Todo punto —converja o no— esta en el CSV con su `detalle_error` real.
- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78.

## Entregables

- `reclasificacion_o2.csv` — 60 filas: x_b, P_alta, T_fuente, P_baja, eps_hrvg, eps_reg, eps_cond, convergio, eta, Wnet, clasificacion_tropical, fallas_tropical, clasificacion_realista, fallas_realista, detalle_error.
- Este reporte.

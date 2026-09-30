# Reporte — Barrido pinch 6 K realista (30 puntos)

Fecha: 2026-09-23 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-23-barrido-pinch6-realista (no toca `src/` ni archivos existentes).
Grid: 5 x 3 x 2 = 30 puntos; `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (de `calibracion_elsayed_malla.py`); pinch **6 K** (`calibracion_pinch.py`, mismo metodo con el pinch como parametro). Clasificacion con `T_amb_diseno=283.15 K` (piso realista validado, pasado explicitamente).

## Resumen ejecutivo

**KALINA: 19 de 30 puntos; con eps realistas (<= 0.95): **5**. Convergen 23; los demas estan en el CSV con `detalle_error`.

## Conteo por clasificacion

| Clasificacion | Puntos |
|---|---|
| KALINA | 19 |
| VALIDO_ADVERTENCIA | 0 |
| CORREGIBLE | 4 |
| DEGENERADO | 0 |
| INVIABLE | 0 |
| NO_CONVERGIO | 7 |
| **Total** | **30** |
| **KALINA con eps_realista=True** | **5** |

## KALINA con eps realistas, ordenados por eta

| x_b | P_alta | T_fuente | P_baja | eps_hrvg | eps_reg | eps_cond | eta | Wnet [kW] |
|---|---|---|---|---|---|---|---|---|
| 0.6 | 5000.0 | 423.0 | 360.842178 | 0.84226 | 0.94888 | 0.945917 | 0.156843 | 66.9044 |
| 0.7 | 4000.0 | 394.0 | 488.458544 | 0.833879 | 0.929271 | 0.947608 | 0.1354 | 63.475 |
| 0.75 | 5000.0 | 394.0 | 544.02827 | 0.75782 | 0.9329 | 0.941855 | 0.132273 | 48.3141 |
| 0.6 | 3000.0 | 394.0 | 360.842155 | 0.829602 | 0.931184 | 0.942866 | 0.131964 | 53.9679 |
| 0.65 | 4000.0 | 394.0 | 426.696688 | 0.762855 | 0.934903 | 0.932831 | 0.128502 | 38.6902 |

## Mejor punto por x_b

| x_b | criterio | clasificacion | eta | Wnet [kW] | P_alta/T_fuente |
|---|---|---|---|---|---|
| 0.60 | KALINA + eps_realista | KALINA | 0.156843 | 66.9044 | 5000.0/423.0 |
| 0.65 | KALINA + eps_realista | KALINA | 0.128502 | 38.6902 | 4000.0/394.0 |
| 0.70 | KALINA + eps_realista | KALINA | 0.1354 | 63.475 | 4000.0/394.0 |
| 0.75 | KALINA + eps_realista | KALINA | 0.132273 | 48.3141 | 5000.0/394.0 |
| 0.80 | KALINA (algun eps > 0.95) | KALINA | 0.14078 | 79.6857 | 5000.0/394.0 |

## Comparacion pinch 4 K vs pinch 6 K (6 puntos comunes con `reclasificacion_o2.csv`)

| x_b | P_alta | T_fuente | eta 4K | clasif 4K | eta 6K | clasif 6K |
|---|---|---|---|---|---|---|
| 0.6 | 3000.0 | 423.0 | 0.145299 | KALINA | 0.140771 | KALINA |
| 0.6 | 5000.0 | 423.0 | 0.164886 | KALINA | 0.156843 | KALINA |
| 0.65 | 3000.0 | 423.0 | 0.138786 | CORREGIBLE | 0.13458 | KALINA |
| 0.65 | 5000.0 | 423.0 | 0.164618 | KALINA | 0.158416 | KALINA |
| 0.7 | 3000.0 | 423.0 | 0.133456 | CORREGIBLE | 0.129452 | KALINA |
| 0.7 | 5000.0 | 423.0 | 0.162815 | KALINA | 0.157547 | KALINA |

## Hallazgos

1. **Eps realistas**: de 23 convergentes, 5 tienen los tres eps <= 0.95 y 18 tienen alguno > 0.95 (marcados `eps_realista=False`); 0 recorte(s) clavados en 0.999. Puntos con eps > 0.95 por columna: eps_hrvg=0, eps_reg=0, eps_cond=18. Maximos: eps_hrvg=0.9282, eps_reg=0.9489, eps_cond=0.9767.
2. **KALINA con eps realistas = 5 de 30** (el numero que importa); 19 son KALINA en total, de los cuales 14 tienen algun eps > 0.95.
3. **O2**: 4 punto(s) convergente(s) siguen bloqueados por O2 en esta malla; en los 6 puntos comunes, pinch 4K bloqueaba O2 en 2 y pinch 6K en 0.
4. **Costo de eta del pinch mayor**: en los 6 puntos comunes la eta media baja 0.54 puntos porcentuales (4K -> 6K).
5. **Rango usado**: x_b >= 0.60 (sin fracciones de NH3 bajas); recorte de eps a [0.01, 0.999]; solo `TeqpAdapter`.
6. Errores registrados (nunca ocultados): PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cub; PropertyRangeError: equilibrio_liquido_vapor(P=5000.0 kPa, T.

## Metodologia y limites

- `P_baja` = burbuja a (`T_sumidero` + 6 K, x_b), brentq en [50, P_alta-10] kPa; eps despejados en forma cerrada (T2 = T_fuente - 6, T6 = T10 + 6, T9 = T_sumidero + 6), recortados a [0.01, 0.999] y re-resolucion. `eps_realista` es una marca (los tres eps <= 0.95), nunca descarta el punto.
- Un resolve por punto; captura de `CicloNoConvergeError`/`PropertyRangeError`/`ValueError`/`RuntimeError`; reanudable por CSV.
- Ventana: T_fuente 394 K (≈ Húsavík) y 423 K; P_alta 3000-5000 kPa; x_b 0.60-0.80.

## Entregables

- `barrido_pinch6_realista.csv` — 30 filas: x_b, P_alta, T_fuente, pinch, P_baja, eps_hrvg, eps_reg, eps_cond, eps_realista, convergio, clasificacion, eta, Wnet, fallas, detalle_error.
- `run.log` de la corrida.
- Este reporte.

# Sensibilidad 1 — Fase C: LHS de 9 variables alrededor de 2 centros

**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · **t_amb_diseno:** T_sumidero de cada punto (piso de O2).
**Puntos:** 500 (C1=250, C2=250); semilla 20261014, 250 por centro, redondeo por tipo de variable.
**KALINA confiable:** `clasificacion == KALINA`, `fuera_rango` falso y todos los `eta_*`/`eps_*` en [0.40, 0.95].

## 1. Puntos y clases por centro

| centro | puntos | KALINA | CORREGIBLE | INVIABLE | NO_CONVERGIO | confiables | % KALINA | eta min [%] | eta med [%] | eta max [%] |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 250 | 118 | 90 | 4 | 38 | 113 | 47.20 | 0.69 | 6.65 | 13.67 |
| C2 | 250 | 131 | 95 | 6 | 18 | 89 | 52.40 | 0.31 | 5.02 | 12.37 |

## 2. Ventanas (p10–p90) entre KALINA confiables

### C1

| variable | n | min | p10 | mediana | p90 | max |
|---|---|---|---|---|---|---|
| T_fuente | 113 | 364.5 | 373.6 | 399.5 | 428.4 | 441 |
| T_sumidero | 113 | 278 | 279 | 282.5 | 287 | 288 |
| P_alta | 113 | 2010 | 2252 | 3370 | 4468 | 4940 |
| P_baja | 113 | 510 | 662 | 990 | 1238 | 1300 |
| x_b | 113 | 0.56 | 0.59 | 0.71 | 0.868 | 0.95 |
| eta_t | 113 | 0.5 | 0.55 | 0.7 | 0.9 | 0.95 |
| eps_hrvg | 113 | 0.5 | 0.55 | 0.7 | 0.9 | 0.95 |
| eps_reg | 113 | 0.5 | 0.55 | 0.75 | 0.9 | 0.95 |
| eps_cond | 113 | 0.8 | 0.85 | 0.9 | 0.95 | 0.95 |

### C2

| variable | n | min | p10 | mediana | p90 | max |
|---|---|---|---|---|---|---|
| T_fuente | 89 | 394 | 398.3 | 414 | 433.7 | 453 |
| T_sumidero | 89 | 278 | 280.3 | 289.5 | 299.5 | 303 |
| P_alta | 89 | 2000 | 2126 | 2770 | 3632 | 3990 |
| P_baja | 89 | 410 | 558 | 870 | 1134 | 1190 |
| x_b | 89 | 0.41 | 0.44 | 0.52 | 0.61 | 0.65 |
| eta_t | 89 | 0.5 | 0.55 | 0.7 | 0.9 | 0.95 |
| eps_hrvg | 89 | 0.5 | 0.55 | 0.7 | 0.9 | 0.9 |
| eps_reg | 89 | 0.5 | 0.55 | 0.75 | 0.9 | 0.95 |
| eps_cond | 89 | 0.7 | 0.75 | 0.85 | 0.95 | 0.95 |

## 3. KS (KALINA confiable vs demás genuinos) — top 3 por centro

- **C1:** x_b KS=0.46563 (p=6.73308e-11); P_baja KS=0.312595 (p=4.52513e-05); eps_cond KS=0.276035 (p=0.000474393)

- **C2:** T_fuente KS=0.61342 (p=7.12469e-20); P_baja KS=0.224326 (p=0.00646955); T_sumidero KS=0.197376 (p=0.0233913)

## 4. PRCC con eta (KALINA confiables) — top 3 por centro

- **C1:** eta_t PRCC=0.742893; P_baja PRCC=-0.611997; x_b PRCC=0.582277

- **C2:** eta_t PRCC=0.713355; x_b PRCC=0.687671; P_baja PRCC=-0.685596

## 5. Equipos (mín / mediana / máx entre KALINA confiables)

| centro | magnitud | n | mínimo | mediana | máximo |
|---|---|---|---|---|---|
| C1 | dh_turb [kJ/kg] | 113 | 47.7071 | 128.278 | 244.111 |
| C1 | Wnet/m_b [kW por kg/s] | 113 | 1.15496 | 38.7796 | 119.106 |
| C1 | Qin = Qi/m_b [kW por kg/s] | 113 | 147.303 | 575.731 | 1219.91 |
| C1 | Qreg/Qi | 113 | 0.0383837 | 0.30887 | 1.98273 |
| C1 | Qout/m_b [kW por kg/s] | 113 | 144.481 | 540.279 | 1174.23 |
| C1 | P_alta/P_baja | 113 | 1.76744 | 3.53968 | 9.09434 |
| C1 | m_O2 | 113 | 0.0261191 | 13.2215 | 41.078 |
| C2 | dh_turb [kJ/kg] | 89 | 59.7292 | 136.355 | 244.192 |
| C2 | Wnet/m_b [kW por kg/s] | 89 | 0.270663 | 25.3931 | 87.4415 |
| C2 | Qin = Qi/m_b [kW por kg/s] | 89 | 86.3751 | 465.732 | 1164.97 |
| C2 | Qreg/Qi | 89 | 0.102557 | 0.573377 | 4.07243 |
| C2 | Qout/m_b [kW por kg/s] | 89 | 86.1044 | 436.794 | 1125.54 |
| C2 | P_alta/P_baja | 89 | 1.84034 | 3.3012 | 9.02326 |
| C2 | m_O2 | 89 | 0.539518 | 18.8695 | 65.3529 |

## 6. Puntos con tiempo agotado (tope 600 s)

- 1 punto(s), centro(s) C1. T_fuente: [405.5, 405.5]; T_sumidero: [287.5, 287.5]; P_alta: [4970, 4970]; P_baja: [980, 980]; x_b: [0.92, 0.92]; eta_t: [0.6, 0.6]; eps_hrvg: [0.55, 0.55]; eps_reg: [0.9, 0.9]; eps_cond: [0.9, 0.9]

## 7. Conclusión por centro

- **C1:** 113 KALINA confiables de 250 puntos (47.20% KALINA). Con mayor KS: x_b, P_baja, eps_cond. Con mayor |PRCC| con eta: eta_t, P_baja, x_b.
- **C2:** 89 KALINA confiables de 250 puntos (52.40% KALINA). Con mayor KS: T_fuente, P_baja, T_sumidero. Con mayor |PRCC| con eta: eta_t, x_b, P_baja.

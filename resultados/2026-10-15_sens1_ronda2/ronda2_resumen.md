# Sensibilidad 1 — Ronda 2 (barridos N2, N5, N6)

**Fecha:** 2026-10-15 · **Motor:** teqp · **m_b:** 1.0 · **t_amb_diseno:** T_sumidero de cada punto.
**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacio y `eta_*`/`eps_*` en [0.40, 0.95]; **KALINA fuera de rango** se reporta aparte.

## 1. Resumen por barrido y centro

| barrido | centro | puntos | KALINA | CORR | INV | NOCONV | confiables | fuera rango | eta min [%] | eta med [%] | eta max [%] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N2 | NA | 144 | 45 | 32 | 12 | 55 | 45 | 0 | 0.26 | 6.36 | 10.45 |
| N5 | NA | 360 | 188 | 143 | 14 | 15 | 138 | 50 | 2.68 | 7.10 | 13.14 |
| N6 | C1 | 27 | 25 | 0 | 0 | 2 | 25 | 0 | 0.25 | 5.63 | 9.17 |
| N6 | C2 | 27 | 18 | 0 | 6 | 3 | 18 | 0 | 0.05 | 1.77 | 4.85 |
| N6 | TOTAL | 54 | 43 | 0 | 6 | 5 | 43 | 0 | 0.05 | 3.69 | 9.17 |

## 2. N2 — ventanas entre KALINA (confiables+no)

- n_puntos=144, n_kal_total=45

### Top 5 KALINA por eta

| pos | id_punto | eta [%] | T_fuente | P_alta | P_baja | x_b | T_sumidero |
|---|---|---|---|---|---|---|---|
| 1 | N2-007 | 10.45 | 374.5 | 2970 | 570 | 0.71 | 280.5 |
| 2 | N2-138 | 10.38 | 386 | 2400 | 360 | 0.55 | 289.5 |
| 3 | N2-135 | 9.97 | 399.5 | 2150 | 460 | 0.57 | 279.5 |
| 4 | N2-110 | 9.69 | 368.5 | 2200 | 530 | 0.69 | 281 |
| 5 | N2-054 | 9.23 | 380.5 | 1790 | 490 | 0.62 | 289 |

## 3. N5 — frontera (primeras 30 filas de ronda2_N5_frontera.csv)

| T_fuente [C] | T_sum [C] | P_baja_min [kPa] | eta_max [%] | P_baja_eta_max | hay_confiable |
|---|---|---|---|---|---|
| 90 | 5 | 400 | 8.05 | 400 | si |
| 90 | 10 | 500 | 7.44 | 500 | si |
| 90 | 15 | 600 | 6.93 | 600 | si |
| 90 | 20 | 700 | 6.49 | 700 | si |
| 90 | 25 | 800 | 6.11 | 800 | si |
| 90 | 30 | 900 | 5.78 | 900 | si |
| 110 | 5 | 500 | 11.65 | 500 | si |
| 110 | 10 | 500 | 11.90 | 500 | si |
| 110 | 15 | 600 | 11.02 | 600 | si |
| 110 | 20 | 700 | 10.27 | 700 | si |
| 110 | 25 | 800 | 9.60 | 800 | si |
| 110 | 30 | 900 | 9.00 | 900 | si |
| 130 | 5 | 500 | 12.68 | 500 | si |
| 130 | 10 | 600 | 11.71 | 600 | si |
| 130 | 15 | 700 | 10.86 | 700 | si |
| 130 | 20 | 800 | 10.11 | 800 | si |
| 130 | 25 | 900 | 9.44 | 900 | si |
| 130 | 30 | 1000 | 8.82 | 1000 | si |
| 150 | 5 | 500 | 13.14 | 500 | si |
| 150 | 10 | 600 | 12.09 | 600 | si |
| 150 | 15 | 700 | 11.18 | 700 | si |
| 150 | 20 | 800 | 10.38 | 800 | si |
| 150 | 25 | 900 | 9.65 | 900 | si |
| 150 | 30 | 1250 | 7.23 | 1250 | si |
| 170 | 5 | 600 | 11.93 | 600 | no |
| 170 | 10 | 700 | 11.01 | 700 | no |
| 170 | 15 | 800 | 10.19 | 800 | no |
| 170 | 20 | 900 | 9.46 | 900 | no |
| 170 | 25 | 1250 | 7.07 | 1250 | no |
| 170 | 30 | 1250 | 7.17 | 1250 | no |

Mallas completas: ver `ronda2_N5_mallas.md`.

## 4. Equipos (min / mediana / max entre KALINA confiables)

| barrido | centro | magnitud | n | minimo | mediana | maximo |
|---|---|---|---|---|---|---|
| N2 | NA | dh_turb [kJ/kg] | 45 | 35.2741 | 151.422 | 236.225 |
| N2 | NA | Wnet/m_b [kW por kg/s] | 45 | 0.264961 | 22.7048 | 94.3575 |
| N2 | NA | Qi/m_b [kW por kg/s] | 45 | 91.386 | 405.335 | 1038.97 |
| N2 | NA | Qreg/Qi | 45 | 0.0950546 | 0.527208 | 2.20505 |
| N2 | NA | Qout/m_b [kW por kg/s] | 45 | 90.318 | 382.751 | 962.009 |
| N2 | NA | P_alta/P_baja | 45 | 1.30435 | 3.15385 | 6.66667 |
| N5 | NA | dh_turb [kJ/kg] | 138 | 81.9686 | 147.257 | 243.896 |
| N5 | NA | Wnet/m_b [kW por kg/s] | 138 | 6.47913 | 51.5715 | 141.285 |
| N5 | NA | Qi/m_b [kW por kg/s] | 138 | 208.973 | 582.111 | 1075.13 |
| N5 | NA | Qreg/Qi | 138 | 0.137618 | 0.320521 | 1.08385 |
| N5 | NA | Qout/m_b [kW por kg/s] | 138 | 196.904 | 534.759 | 1015.86 |
| N5 | NA | P_alta/P_baja | 138 | 2 | 3.33333 | 7.5 |
| N6 | C1 | dh_turb [kJ/kg] | 25 | 26.9964 | 110.129 | 145.974 |
| N6 | C1 | Wnet/m_b [kW por kg/s] | 25 | 1.12 | 36.5926 | 69.566 |
| N6 | C1 | Qi/m_b [kW por kg/s] | 25 | 418.937 | 605.149 | 798.061 |
| N6 | C1 | Qreg/Qi | 25 | 0.0994986 | 0.212212 | 0.45401 |
| N6 | C1 | Qout/m_b [kW por kg/s] | 25 | 388.568 | 577.415 | 761.054 |
| N6 | C1 | P_alta/P_baja | 25 | 4.78261 | 4.78261 | 4.78261 |
| N6 | C2 | dh_turb [kJ/kg] | 18 | 99.8772 | 139.524 | 178.772 |
| N6 | C2 | Wnet/m_b [kW por kg/s] | 18 | 0.144991 | 4.82241 | 13.5781 |
| N6 | C2 | Qi/m_b [kW por kg/s] | 18 | 160.51 | 279.701 | 360.755 |
| N6 | C2 | Qreg/Qi | 18 | 0.433786 | 0.862826 | 1.74872 |
| N6 | C2 | Qout/m_b [kW por kg/s] | 18 | 160.096 | 271.709 | 356.717 |
| N6 | C2 | P_alta/P_baja | 18 | 5.32255 | 5.32255 | 5.32255 |
| N6 | TOTAL | dh_turb [kJ/kg] | 43 | 26.9964 | 114.422 | 178.772 |
| N6 | TOTAL | Wnet/m_b [kW por kg/s] | 43 | 0.144991 | 13.7356 | 69.566 |
| N6 | TOTAL | Qi/m_b [kW por kg/s] | 43 | 160.51 | 433.628 | 798.061 |
| N6 | TOTAL | Qreg/Qi | 43 | 0.0994986 | 0.350193 | 1.74872 |
| N6 | TOTAL | Qout/m_b [kW por kg/s] | 43 | 160.096 | 420.242 | 761.054 |
| N6 | TOTAL | P_alta/P_baja | 43 | 4.78261 | 4.78261 | 5.32255 |

## 5. Conclusiones

### N2 — esquina 70-130 °C con presiones bajas

- KALINA (confiables+fuera rango) en 45 puntos de N2.
- Ver `ronda2_N2_ventanas.csv` y `ronda2_N2_top5.csv`.

### N5 — frontera por fuente y clima

- Hay KALINA en 36 combinaciones (T_fuente,C)x(T_sum,C).
- Eta maxima 13.14% a T_fuente=150°C, T_sum=5°C con P_baja=500 kPa.

### N6 — equipos de baja efectividad

- C1: combinacion mas barata (suma de efectividades minima) que sigue siendo KALINA confiable: eta_t=0.4, eps_hrvg=0.4, eps_reg=0.4 (eta=0.25%).
- C2: combinacion mas barata (suma de efectividades minima) que sigue siendo KALINA confiable: eta_t=0.4, eps_hrvg=0.55, eps_reg=0.55 (eta=0.26%).

### Puntos con tiempo agotado (tope 600 s)

- Ninguno.


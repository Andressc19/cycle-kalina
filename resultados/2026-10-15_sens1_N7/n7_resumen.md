# Sensibilidad 1 — N7 (N7A una variable; N7B pares; C3 y C4)

**Fecha:** 2026-10-15 · **Motor:** teqp · **m_b:** 1.0 · **t_amb_diseno:** T_sumidero de cada punto.
**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacio y `eta_*`/`eps_*` en [0.40, 0.95]; **KALINA fuera de rango** aparte.

## 1. Resumen por barrido y centro

| barrido | centro | puntos | KALINA | CORR | INV | NOCONV | confiables | fuera rango |
|---|---|---|---|---|---|---|---|---|
| N7A | C3 | 139 | 117 | 17 | 1 | 4 | 104 | 13 |
| N7A | C4 | 140 | 101 | 15 | 1 | 23 | 95 | 6 |
| N7B | C3 | 180 | 111 | 61 | 1 | 7 | 101 | 10 |
| N7B | C4 | 181 | 92 | 64 | 4 | 21 | 92 | 0 |

## 2. Ranking de variables por amplitud de η entre KALINA

### C3

| # | variable | amplitud KALINA [pp] | η min [%] | η max [%] |
|---|---|---|---|---|
| 1 | P_alta | 11.4606 | 0.4292 | 11.8898 |
| 2 | P_baja | 9.1133 | 3.6853 | 12.7986 |
| 3 | x_b | 6.7007 | 3.7824 | 10.4831 |
| 4 | eta_t | 6.3174 | 4.2800 | 10.5974 |
| 5 | T_fuente | 2.9375 | 6.5341 | 9.4715 |
| 6 | eps_hrvg | 1.4897 | 7.9827 | 9.4725 |
| 7 | eps_reg | 0.7978 | 8.9555 | 9.7533 |
| 8 | T_sumidero | 0.5185 | 9.3848 | 9.9033 |
| 9 | eps_cond | 0.3644 | 9.4511 | 9.8155 |
| 10 | eta_p | 0.3571 | 9.1426 | 9.4997 |

### C4

| # | variable | amplitud KALINA [pp] | η min [%] | η max [%] |
|---|---|---|---|---|
| 1 | P_alta | 10.8855 | 0.8857 | 11.7712 |
| 2 | eps_hrvg | 9.8824 | 1.6247 | 11.5070 |
| 3 | eta_t | 7.6177 | 4.9185 | 12.5362 |
| 4 | x_b | 6.9784 | 4.5914 | 11.5698 |
| 5 | P_baja | 6.8095 | 5.2659 | 12.0754 |
| 6 | T_fuente | 2.8047 | 9.5120 | 12.3166 |
| 7 | eps_reg | 1.0359 | 10.5118 | 11.5477 |
| 8 | eta_p | 0.6864 | 10.5613 | 11.2477 |
| 9 | T_sumidero | 0.5426 | 10.9720 | 11.5146 |
| 10 | eps_cond | 0.0000 | 11.1545 | 11.1545 |

## 3. N7B — mallas de pares (resumen)

Matrices 7x7 de clase y η: ver `n7_mallas.md`.

| centro | par | var1 × var2 | puntos | descartado | KALINA | confiables | área [%] | η min [%] | mejor η [%] |
|---|---|---|---|---|---|---|---|---|---|
| C3 | B1 | T_fuente × P_baja | 49 | 0 | 40 | 30 | 81.6327 | 4.9727 | 12.2570 |
| C3 | B2 | P_baja × x_b | 49 | 0 | 36 | 36 | 73.4694 | 4.3038 | 13.2586 |
| C3 | B3 | P_alta × P_baja | 48 | 1 | 40 | 40 | 81.6327 | 3.5601 | 14.3824 |
| C3 | B4 | eps_cond × T_sumidero | 49 | 0 | 8 | 8 | 16.3265 | 9.3848 | 9.8939 |
| C4 | B1 | T_fuente × P_baja | 49 | 0 | 25 | 25 | 51.0204 | 6.1912 | 13.2336 |
| C4 | B2 | P_baja × x_b | 49 | 0 | 39 | 39 | 79.5918 | 2.8660 | 12.9101 |
| C4 | B3 | P_alta × P_baja | 49 | 0 | 34 | 34 | 69.3878 | 4.4595 | 12.6108 |
| C4 | B4 | eps_cond × T_sumidero | 49 | 0 | 5 | 5 | 10.2041 | 10.9720 | 11.4015 |

## 4. Equipos (min / mediana / max entre KALINA confiables)

| centro | magnitud | n | minimo | mediana | maximo |
|---|---|---|---|---|---|
| C3 | dh_turb [kJ/kg] | 205 | 7.88605 | 166.719 | 253.889 |
| C3 | Wnet/m_b [kW por kg/s] | 205 | 6.95291 | 100.03 | 161.309 |
| C3 | Qi/m_b [kW por kg/s] | 205 | 318.63 | 1116.9 | 1619.89 |
| C3 | Qreg/Qi | 205 | 0.0157261 | 0.12092 | 1.35033 |
| C3 | Qout/m_b [kW por kg/s] | 205 | 306.578 | 1006.63 | 1612.93 |
| C3 | P_alta/P_baja | 205 | 1.05263 | 3.31579 | 7.69231 |
| C4 | dh_turb [kJ/kg] | 187 | 13.4568 | 157.907 | 231.41 |
| C4 | Wnet/m_b [kW por kg/s] | 187 | 6.97757 | 85.3206 | 179.603 |
| C4 | Qi/m_b [kW por kg/s] | 187 | 243.367 | 860.886 | 1458.24 |
| C4 | Qreg/Qi | 187 | 0.0196103 | 0.128216 | 1.30766 |
| C4 | Qout/m_b [kW por kg/s] | 187 | 227.133 | 766.201 | 1320.73 |
| C4 | P_alta/P_baja | 187 | 1.0989 | 4.26374 | 7.76 |

## 5. Comparacion con C1 y C2 (amplitud de η entre KALINA, pp)

Fuente C1/C2: `faseA_resumen_variables_corregido.csv`.

| variable | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| base | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| T_fuente | 2.3877 | 6.8250 | 2.9375 | 2.8047 |
| T_sumidero | 0.2176 | 0.9934 | 0.5185 | 0.5426 |
| P_alta | 4.2737 | 6.8379 | 11.4606 | 10.8855 |
| P_baja | 6.6616 | 6.5351 | 9.1133 | 6.8095 |
| x_b | 6.6792 | 6.2031 | 6.7007 | 6.9784 |
| eta_t | 8.0710 | 5.9293 | 6.3174 | 7.6177 |
| eta_p | 0.5333 | 1.2956 | 0.3571 | 0.6864 |
| eps_hrvg | 2.8691 | 6.5705 | 1.4897 | 9.8824 |
| eps_reg | 1.2081 | 5.3269 | 0.7978 | 1.0359 |
| eps_cond | 0.0000 | 0.5467 | 0.3644 | 0.0000 |

## 6. Descartes y tiempo agotado

Descartes N7B (`P_alta < 1.3*P_baja`; N7A no aplica):

| barrido | centro | n_candidatas | n_descartados | n_duplicados | n_final |
|---|---|---|---|---|---|
| N7A | C3 | 148 | 0 | 9 | 139 |
| N7A | C4 | 148 | 0 | 8 | 140 |
| N7A | TOTAL | 296 | 0 | 17 | 279 |
| N7B | C3 | 196 | 1 | 15 | 180 |
| N7B | C4 | 196 | 0 | 15 | 181 |
| N7B | TOTAL | 392 | 1 | 30 | 361 |

Puntos con tiempo agotado (tope 600 s):

- N7A / C4: 1 punto(s)
- N7B / C4: 2 punto(s)


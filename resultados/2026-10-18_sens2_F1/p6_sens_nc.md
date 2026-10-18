# Sens2 F1 - NO_CONVERGIO y la existencia

Tres lecturas de Y1 en cada LHS. Los 3 primeros se ordenan por el rango medio de |PRCC| y KS (1 = mayor).

| bloque | 3 primeros (NO_CONVERGIO = no KALINA) | 3 primeros sin NO_CONVERGIO | 3 primeros (NO_CONVERGIO = KALINA) | igual sin NC | igual NC=KALINA |
|---|---|---|---|---|---|
| E3 C1 Husavik | x_b, P_baja, eps_cond | x_b, P_baja, eps_cond | x_b, P_baja, T_fuente | si | no |
| E3 C2 ancla A* | P_baja, eps_cond, x_b | x_b, eps_cond, P_baja | x_b, eps_cond, P_baja | si | si |
| E14 C3 caliente 150 C | P_baja, eps_cond, x_b | P_baja, x_b, T_sumidero | P_baja, x_b, T_sumidero | no | no |
| E14 C4 frio 110 C | T_fuente, P_baja, P_alta | P_baja, x_b, eps_cond | P_baja, T_fuente, T_sumidero | no | no |

## Clase por cuartil de T_fuente (LHS)

| bloque | cuartil | T_fuente (K) | n | NO_CONVERGIO | P(KALINA), NC = 0 | P(KALINA) si convergio [IC] |
|---|---|---|---|---|---|---|
| E3 C1 Husavik | 1 | 363.5 a 383.0 | 63 | 22 | 0.44 | 0.68 [0.53, 0.80] |
| E3 C1 Husavik | 2 | 383.5 a 403.0 | 62 | 8 | 0.56 | 0.65 [0.51, 0.76] |
| E3 C1 Husavik | 3 | 403.5 a 423.0 | 63 | 4 | 0.49 | 0.53 [0.40, 0.65] |
| E3 C1 Husavik | 4 | 423.5 a 443.0 | 62 | 4 | 0.39 | 0.41 [0.30, 0.54] |
| E3 C2 ancla A* | 1 | 393.5 a 410.5 | 63 | 12 | 0.62 | 0.76 [0.63, 0.86] |
| E3 C2 ancla A* | 2 | 411.0 a 428.0 | 62 | 4 | 0.61 | 0.66 [0.53, 0.76] |
| E3 C2 ancla A* | 3 | 428.5 a 445.5 | 63 | 1 | 0.48 | 0.48 [0.36, 0.61] |
| E3 C2 ancla A* | 4 | 446.0 a 463.0 | 62 | 1 | 0.39 | 0.39 [0.28, 0.52] |
| E14 C3 caliente 150 C | 1 | 363.5 a 389.0 | 59 | 28 | 0.41 | 0.77 [0.60, 0.89] |
| E14 C3 caliente 150 C | 2 | 389.5 a 412.5 | 58 | 11 | 0.60 | 0.74 [0.60, 0.85] |
| E14 C3 caliente 150 C | 3 | 413.0 a 438.0 | 59 | 7 | 0.61 | 0.69 [0.56, 0.80] |
| E14 C3 caliente 150 C | 4 | 438.5 a 463.0 | 58 | 8 | 0.45 | 0.52 [0.39, 0.65] |
| E14 C4 frio 110 C | 1 | 353.5 a 371.5 | 59 | 37 | 0.36 | 0.95 [0.78, 0.99] |
| E14 C4 frio 110 C | 2 | 372.0 a 388.5 | 58 | 13 | 0.59 | 0.76 [0.61, 0.86] |
| E14 C4 frio 110 C | 3 | 389.0 a 405.5 | 56 | 4 | 0.73 | 0.79 [0.66, 0.88] |
| E14 C4 frio 110 C | 4 | 406.0 a 423.0 | 58 | 3 | 0.71 | 0.75 [0.62, 0.84] |

## Variable que mas separa NO_CONVERGIO del resto (KS)

| bloque | variable | KS | n NO_CONVERGIO |
|---|---|---|---|
| E14 C4 frio 110 C | T_fuente | 0.62 | 57 |
| E3 C2 ancla A* | T_fuente | 0.58 | 18 |
| E3 C1 Husavik | T_fuente | 0.43 | 38 |
| E14 C3 caliente 150 C | T_fuente | 0.39 | 54 |

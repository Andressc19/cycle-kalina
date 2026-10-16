# Sensibilidad 1 - Ronda 3 (barridos N9, N10 y N8)

**Fecha:** 2026-10-16 - **Motor:** teqp - **m_b:** 1.0 - **t_amb_diseno:** T_sumidero de cada punto.

**Como se lee.** *KALINA (total)* es toda fila clasificada KALINA; *dentro del rango experimental* es KALINA sin la marca `fuera_rango` y con eta/eps entre 0.40 y 0.95; *fuera del rango experimental (liquido > 420 K)* es KALINA con esa marca. En las matrices, K/c/n/i = KALINA/CORREGIBLE/NO_CONVERGIO/INVIABLE.

## 1. Resumen por barrido y centro

| barrido | centro | puntos | KALINA (total) | dentro | fuera | CORR | INV | NOCONV | eta min (KALINA) [%] | eta med (KALINA) [%] | eta max (KALINA) [%] | eta min (dentro) [%] | eta med (dentro) [%] | eta max (dentro) [%] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N9 | C3 | 97 | 97 | 86 | 11 | 0 | 0 | 0 | 5.22 | 9.23 | 10.94 | 5.22 | 9.09 | 10.94 |
| N9 | C4 | 97 | 87 | 87 | 0 | 0 | 0 | 10 | 1.62 | 10.72 | 12.98 | 1.62 | 10.72 | 12.98 |
| N9 | TOTAL | 194 | 184 | 173 | 11 | 0 | 0 | 10 | 1.62 | 9.41 | 12.98 | 1.62 | 9.43 | 12.98 |
| N10 | C1 | 35 | 14 | 14 | 0 | 7 | 0 | 14 | 8.24 | 10.89 | 14.01 | 8.24 | 10.89 | 14.01 |
| N10 | C3 | 35 | 24 | 24 | 0 | 11 | 0 | 0 | 7.09 | 10.91 | 14.53 | 7.09 | 10.91 | 14.53 |
| N10 | C4 | 35 | 9 | 9 | 0 | 10 | 1 | 15 | 7.63 | 10.26 | 12.20 | 7.63 | 10.26 | 12.20 |
| N10 | TOTAL | 105 | 47 | 47 | 0 | 28 | 1 | 29 | 7.09 | 10.90 | 14.53 | 7.09 | 10.90 | 14.53 |
| N8 | C3 | 234 | 121 | 93 | 28 | 49 | 10 | 54 | 0.22 | 4.86 | 12.11 | 0.22 | 4.52 | 10.19 |
| N8 | C4 | 231 | 137 | 137 | 0 | 28 | 9 | 57 | 0.20 | 4.76 | 11.18 | 0.20 | 4.76 | 11.18 |
| N8 | TOTAL | 465 | 258 | 230 | 28 | 77 | 19 | 111 | 0.20 | 4.78 | 12.11 | 0.20 | 4.64 | 11.18 |

### Planeados vs evaluados

- **N10**: planeados 105 (ronda3_diseno.csv) vs evaluados 105 (ronda3_filas.csv).
- **N8**: planeados 465 (ronda3_diseno.csv) vs evaluados 465 (ronda3_filas.csv).
- **N9**: planeados 194 (ronda3_diseno.csv) vs evaluados 194 (ronda3_filas.csv).

## 2. N9 - pares del regenerador y la turbina en C3 y C4

Dos mallas 7x7 por centro con el resto de variables en el valor del centro (B5: eps_reg x eta_t; B6: eps_hrvg x T_fuente). El punto base se evaluo una sola vez por centro y ocupa la celda central de las dos mallas.

- **C3**: 97 puntos evaluados; 97 KALINA (total), de los cuales 86 estan dentro del rango experimental y 11 fuera del rango experimental (liquido > 420 K). Ademas 0 NO_CONVERGIO. La eta mas alta entre los KALINA (total) es 10.94% (mediana 9.23%, minima 5.22%).
- **C4**: 97 puntos evaluados; 87 KALINA (total), de los cuales 87 estan dentro del rango experimental y 0 fuera del rango experimental (liquido > 420 K). Ademas 10 NO_CONVERGIO. La eta mas alta entre los KALINA (total) es 12.98% (mediana 10.72%, minima 1.62%).

- El diseno de N9 queda en 194 puntos (la referencia previa era de aproximadamente 196): el dedup por (barrido, centro, combinacion) deja el punto base una sola vez por centro, asi que cada centro aporta 1 base + 48 celdas de B5 + 48 de B6.

### KALINA por par (contando el punto base) y eta mas alta

| centro | par | celdas | KALINA (contando base) | var1 | var2 | val1 del mejor | val2 del mejor | mejor id | eta [%] |
|---|---|---|---|---|---|---|---|---|---|
| C3 | B5 | 49 | 49 | eps_reg | eta_t | 0.95 | 0.95 | N9-C3-B5-0048 | 10.94 |
| C3 | B6 | 49 | 49 | eps_hrvg | T_fuente | 0.95 | 423.15 | N9-C3-B6-0045 | 9.47 |
| C4 | B5 | 49 | 49 | eps_reg | eta_t | 0.95 | 0.95 | N9-C4-B5-0048 | 12.98 |
| C4 | B6 | 49 | 39 | eps_hrvg | T_fuente | 0.95 | 423.15 | N9-C4-B6-0048 | 12.32 |

### Matrices 7x7 (clase y eta) por centro y par

### C3 - par B5 (eps_reg x eta_t)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| eps_reg \ eta_t | 0.5 | 0.6 | 0.7 | 0.8 | 0.85 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|
| 0.5 | K | K | K | K | K | K | K |
| 0.6 | K | K | K | K | K | K | K |
| 0.7 | K | K | K | K | K | K | K |
| 0.75 | K | K | K | K | K | K | K |
| 0.8 | K | K | K | K | K | K | K |
| 0.9 | K | K | K | K | K | K | K |
| 0.95 | K | K | K | K | K | K | K |

eta [%]:

| eps_reg \ eta_t | 0.5 | 0.6 | 0.7 | 0.8 | 0.85 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|
| 0.5 | 5.22 | 6.33 | 7.44 | 8.54 | 9.09 | 9.64 | 10.20 |
| 0.6 | 5.31 | 6.43 | 7.55 | 8.67 | 9.23 | 9.79 | 10.35 |
| 0.7 | 5.39 | 6.53 | 7.67 | 8.81 | 9.38 | 9.95 | 10.52 |
| 0.75 | 5.43 | 6.58 | 7.73 | 8.88 | 9.45 | 10.02 | 10.60 |
| 0.8 | 5.47 | 6.63 | 7.79 | 8.95 | 9.53 | 10.10 | 10.68 |
| 0.9 | 5.56 | 6.74 | 7.91 | 9.09 | 9.68 | 10.26 | 10.85 |
| 0.95 | 5.60 | 6.79 | 7.98 | 9.16 | 9.75 | 10.34 | 10.94 |

### C3 - par B6 (eps_hrvg x T_fuente)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| eps_hrvg \ T_fuente | 383.15 | 403.15 | 413.15 | 423.15 | 433.15 | 453.15 | 473.15 |
|---|---|---|---|---|---|---|---|
| 0.5 | K | K | K | K | K | K | K |
| 0.6 | K | K | K | K | K | K | K |
| 0.7 | K | K | K | K | K | K | k |
| 0.8 | K | K | K | K | K | k | k |
| 0.85 | K | K | K | K | K | k | k |
| 0.9 | K | K | K | K | k | k | k |
| 0.95 | K | K | K | K | k | k | k |

eta [%]:

| eps_hrvg \ T_fuente | 383.15 | 403.15 | 413.15 | 423.15 | 433.15 | 453.15 | 473.15 |
|---|---|---|---|---|---|---|---|
| 0.5 | 6.99 | 7.93 | 8.26 | 8.57 | 8.86 | 9.23 | 9.28 |
| 0.6 | 7.63 | 8.43 | 8.72 | 8.98 | 9.22 | 9.43 | 9.45 |
| 0.7 | 8.09 | 8.80 | 9.05 | 9.26 | 9.41 | 9.47 | 9.47 |
| 0.8 | 8.45 | 9.08 | 9.28 | 9.41 | 9.47 | 9.43 | 9.41 |
| 0.85 | 8.60 | 9.19 | 9.36 | 9.45 | 9.47 | 9.39 | 9.37 |
| 0.9 | 8.74 | 9.28 | 9.41 | 9.47 | 9.46 | 9.35 | 9.33 |
| 0.95 | 8.86 | 9.35 | 9.45 | 9.47 | 9.44 | 9.31 | 9.29 |

### C4 - par B5 (eps_reg x eta_t)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| eps_reg \ eta_t | 0.5 | 0.6 | 0.7 | 0.8 | 0.85 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|
| 0.5 | K | K | K | K | K | K | K |
| 0.6 | K | K | K | K | K | K | K |
| 0.7 | K | K | K | K | K | K | K |
| 0.75 | K | K | K | K | K | K | K |
| 0.8 | K | K | K | K | K | K | K |
| 0.9 | K | K | K | K | K | K | K |
| 0.95 | K | K | K | K | K | K | K |

eta [%]:

| eps_reg \ eta_t | 0.5 | 0.6 | 0.7 | 0.8 | 0.85 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|
| 0.5 | 6.04 | 7.37 | 8.70 | 10.03 | 10.69 | 11.35 | 12.01 |
| 0.6 | 6.15 | 7.50 | 8.85 | 10.20 | 10.87 | 11.55 | 12.22 |
| 0.7 | 6.25 | 7.63 | 9.00 | 10.37 | 11.06 | 11.74 | 12.43 |
| 0.75 | 6.31 | 7.69 | 9.08 | 10.46 | 11.15 | 11.85 | 12.54 |
| 0.8 | 6.36 | 7.76 | 9.16 | 10.55 | 11.25 | 11.95 | 12.64 |
| 0.9 | 6.47 | 7.90 | 9.32 | 10.74 | 11.45 | 12.16 | 12.87 |
| 0.95 | 6.53 | 7.97 | 9.40 | 10.83 | 11.55 | 12.26 | 12.98 |

### C4 - par B6 (eps_hrvg x T_fuente)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| eps_hrvg \ T_fuente | 353.15 | 363.15 | 373.15 | 383.15 | 393.15 | 408.15 | 423.15 |
|---|---|---|---|---|---|---|---|
| 0.5 | n | K | K | K | K | K | K |
| 0.6 | n | K | K | K | K | K | K |
| 0.7 | n | K | K | K | K | K | K |
| 0.8 | n | n | K | K | K | K | K |
| 0.85 | n | K | K | K | K | n | K |
| 0.9 | n | n | K | K | K | K | K |
| 0.95 | n | K | K | K | K | K | K |

eta [%]:

| eps_hrvg \ T_fuente | 353.15 | 363.15 | 373.15 | 383.15 | 393.15 | 408.15 | 423.15 |
|---|---|---|---|---|---|---|---|
| 0.5 | ? | 6.58 | 8.65 | 1.62 | 9.72 | 10.25 | 10.62 |
| 0.6 | ? | 7.74 | 9.50 | 10.05 | 10.40 | 10.81 | 11.21 |
| 0.7 | ? | 8.57 | 10.08 | 10.50 | 10.88 | 11.27 | 11.70 |
| 0.8 | ? | 9.22 | 10.47 | 10.97 | 11.28 | 11.70 | 12.11 |
| 0.85 | ? | 9.51 | 10.72 | 11.15 | 11.47 | ? | 12.23 |
| 0.9 | ? | ? | 10.90 | 11.33 | 11.66 | 12.07 | 12.30 |
| 0.95 | ? | 9.96 | 11.07 | 11.51 | 11.84 | 12.20 | 12.32 |

Tambien en `ronda3_N9_matrices.md`.

## 3. N10 - extension de P_alta mas alla de 5000 kPa

Malla 5x7 por centro (P_alta en {4000, 5000, 6000, 7000, 8000} kPa; P_baja segun el centro) y sin punto base: 35 puntos por centro. Cada celda es el punto de esa combinacion.

### C1 - malla 5x7 (P_alta x P_baja)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| P_alta \ P_baja | 500 | 600 | 690 | 800 | 950 | 1100 | 1300 |
|---|---|---|---|---|---|---|---|
| 4000 | c | K | K | K | K | K | K |
| 5000 | c | K | K | K | K | K | K |
| 6000 | c | c | c | c | c | K | K |
| 7000 | n | n | n | n | n | n | n |
| 8000 | n | n | n | n | n | n | n |

eta [%]:

| P_alta \ P_baja | 500 | 600 | 690 | 800 | 950 | 1100 | 1300 |
|---|---|---|---|---|---|---|---|
| 4000 | 14.90 | 13.73 | 12.81 | 11.82 | 10.65 | 9.63 | 8.44 |
| 5000 | 15.11 | 14.01 | 13.15 | 12.23 | 11.14 | 10.20 | 9.12 |
| 6000 | 13.39 | 12.43 | 11.69 | 10.89 | 9.96 | 9.16 | 8.24 |
| 7000 | ? | ? | -22.86 | -21.94 | ? | -19.81 | -18.61 |
| 8000 | ? | ? | ? | ? | ? | ? | ? |

### C3 - malla 5x7 (P_alta x P_baja)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| P_alta \ P_baja | 500 | 650 | 800 | 950 | 1100 | 1300 | 1600 |
|---|---|---|---|---|---|---|---|
| 4000 | c | K | K | K | K | K | K |
| 5000 | c | K | K | K | K | K | K |
| 6000 | c | K | K | K | K | K | K |
| 7000 | c | c | K | K | K | K | K |
| 8000 | c | c | c | c | c | c | K |

eta [%]:

| P_alta \ P_baja | 500 | 650 | 800 | 950 | 1100 | 1300 | 1600 |
|---|---|---|---|---|---|---|---|
| 4000 | 15.31 | 13.56 | 12.12 | 10.91 | 9.85 | 8.63 | 7.09 |
| 5000 | 16.03 | 14.38 | 13.03 | 11.89 | 10.90 | 9.75 | 8.29 |
| 6000 | 16.08 | 14.53 | 13.27 | 12.21 | 11.28 | 10.21 | 8.85 |
| 7000 | 15.31 | 13.89 | 12.73 | 11.76 | 10.91 | 9.94 | 8.71 |
| 8000 | 12.98 | 11.75 | 10.76 | 9.92 | 9.21 | 8.38 | 7.36 |

### C4 - malla 5x7 (P_alta x P_baja)

Clase (K/c/n/i; la letra en minuscula marca los fuera del rango experimental):

| P_alta \ P_baja | 500 | 650 | 800 | 910 | 1050 | 1250 | 1500 |
|---|---|---|---|---|---|---|---|
| 4000 | c | c | K | K | K | K | K |
| 5000 | c | n | c | K | K | K | K |
| 6000 | i | c | c | c | c | c | c |
| 7000 | n | n | n | n | n | n | n |
| 8000 | n | n | n | n | n | n | n |

eta [%]:

| P_alta \ P_baja | 500 | 650 | 800 | 910 | 1050 | 1250 | 1500 |
|---|---|---|---|---|---|---|---|
| 4000 | 11.96 | 13.65 | 12.20 | 11.29 | 10.26 | 8.99 | 7.63 |
| 5000 | 9.76 | ? | 12.60 | 11.75 | 10.80 | 9.62 | 8.38 |
| 6000 | -10.74 | 9.72 | 8.77 | 8.15 | 7.46 | 6.62 | 5.75 |
| 7000 | ? | ? | ? | ? | ? | ? | ? |
| 8000 | ? | ? | ? | ? | ? | ? | ? |

### La eta maxima sube con P_alta o tiene maximo interior?

- **C1**: eta max por P_alta [kPa -> %]: 4000 -> 13.73, 5000 -> 14.01, 6000 -> 9.16, 7000 -> ?, 8000 -> ?. Veredicto: maximo interior (eta max en 5000 kPa); mejor punto N10-C1-0009 (14.01 %).
- **C3**: eta max por P_alta [kPa -> %]: 4000 -> 13.56, 5000 -> 14.38, 6000 -> 14.53, 7000 -> 12.73, 8000 -> 7.36. Veredicto: maximo interior (eta max en 6000 kPa); mejor punto N10-C3-0016 (14.53 %).
- **C4**: eta max por P_alta [kPa -> %]: 4000 -> 12.20, 5000 -> 11.75, 6000 -> ?, 7000 -> ?, 8000 -> ?. Veredicto: la eta maxima desciende con P_alta (eta max en 4000 kPa); mejor punto N10-C4-0003 (12.20 %).
- En el veredicto, `eta max en X kPa` dice en que P_alta esta el maximo de ese centro; `sigue subiendo` significa que el maximo cae en el borde superior de la caja (8000 kPa).

## 4. N8 - muestreo LHS de 9 variables (C3 y C4)

Por centro: 250 candidatas LHS (semilla 20261017) redondeadas; las con P_alta < 1.3*P_baja se descartaron sin re-muestrear (ver ronda3_descartes.csv) y los duplicados tras redondear se quitaron una sola vez. eta_p = 0.80 y m_b = 1.0 fijos.

### C3 (234 puntos)

Clases: 121 KALINA (total), 49 CORREGIBLE, 10 INVIABLE y 54 NO_CONVERGIO.

Ventanas p10-p90 de las 9 variables entre los KALINA (total); el redondeo (0.5 K, 10 kPa, 0.01 y 0.05) marca la resolucion de estas cifras:

| variable | p10 | mediana | p90 | n |
|---|---|---|---|---|
| T_fuente | 377 | 413.5 | 449.5 | 121 |
| T_sumidero | 279.5 | 286.5 | 293 | 121 |
| P_alta | 2030 | 3420 | 4640 | 121 |
| P_baja | 740 | 1250 | 1660 | 121 |
| x_b | 0.48 | 0.66 | 0.85 | 121 |
| eta_t | 0.55 | 0.75 | 0.9 | 121 |
| eps_hrvg | 0.55 | 0.7 | 0.9 | 121 |
| eps_reg | 0.55 | 0.75 | 0.9 | 121 |
| eps_cond | 0.85 | 0.9 | 0.95 | 121 |

KS de cada variable: KALINA (total) frente al resto de puntos genuinos (CORREGIBLE + INVIABLE). D va de 0 (mismo muestreo) a 1; p-valor bajo (< 0.05) se lee como distribucion distinta (con valores redondeados, indicativo):

| variable | D | p-valor | n KALINA | n resto |
|---|---|---|---|---|
| T_fuente | 0.216 | 0.0406 | 121 | 59 |
| T_sumidero | 0.261 | 0.00704 | 121 | 59 |
| P_alta | 0.176 | 0.15 | 121 | 59 |
| P_baja | 0.477 | 9.19e-09 | 121 | 59 |
| x_b | 0.376 | 1.53e-05 | 121 | 59 |
| eta_t | 0.19 | 0.0987 | 121 | 59 |
| eps_hrvg | 0.206 | 0.057 | 121 | 59 |
| eps_reg | 0.0854 | 0.904 | 121 | 59 |
| eps_cond | 0.23 | 0.0245 | 121 | 59 |

PRCC con eta entre los KALINA (total): rangos con promedio en empates y residuos de minimos cuadrados con intercepta (solo numpy). +1 sube eta, -1 la baja, ~0 no aporta linealmente:

| variable | PRCC |
|---|---|
| T_fuente | 0.555 |
| T_sumidero | -0.0314 |
| P_alta | 0.521 |
| P_baja | -0.721 |
| x_b | 0.701 |
| eta_t | 0.629 |
| eps_hrvg | 0.286 |
| eps_reg | 0.362 |
| eps_cond | -0.0692 |

Lectura: la mayor influencia positiva lineal es **x_b** (PRCC 0.701) y la mayor negativa **P_baja** (PRCC -0.721).

Top 10 de eta entre los KALINA (total):

| puesto | id | eta [%] | Wnet [kW] | T_fuente [K] | P_alta [kPa] | P_baja [kPa] | x_b | eta_t |
|---|---|---|---|---|---|---|---|---|
| 1 | N8-C3-0091 | 12.11 | 159.13 | 445 | 4710 | 1050 | 0.73 | 0.9 |
| 2 | N8-C3-0083 | 10.19 | 96.28 | 425 | 3510 | 930 | 0.69 | 0.85 |
| 3 | N8-C3-0014 | 10.17 | 160.56 | 460.5 | 4020 | 920 | 0.67 | 0.8 |
| 4 | N8-C3-0034 | 10.16 | 84.035 | 391 | 3490 | 1180 | 0.85 | 0.95 |
| 5 | N8-C3-0216 | 9.86 | 114.39 | 421.5 | 3970 | 1540 | 0.88 | 0.95 |
| 6 | N8-C3-0046 | 9.74 | 65.915 | 461 | 3470 | 630 | 0.42 | 0.85 |
| 7 | N8-C3-0219 | 9.63 | 93.34 | 440.5 | 3730 | 700 | 0.66 | 0.7 |
| 8 | N8-C3-0162 | 9.55 | 98.664 | 438.5 | 4130 | 840 | 0.84 | 0.65 |
| 9 | N8-C3-0093 | 9.42 | 90.577 | 440 | 4910 | 1560 | 0.92 | 0.85 |
| 10 | N8-C3-0020 | 9.40 | 49.254 | 402.5 | 4700 | 890 | 0.74 | 0.85 |

Rangos de equipos entre los KALINA (total): dh_turb en kJ/kg, Wnet en kW con m_b = 1.0 kg/s (kW por kg/s), Qreg/Qi y r_P = P_alta/P_baja sin unidades:

| variable | unidad | min | p10 | mediana | p90 | max | n |
|---|---|---|---|---|---|---|---|
| dh_turb | kJ/kg | 23.0732 | 55.8058 | 108.445 | 166.512 | 249.44 | 121 |
| Wnet | kW por kg/s | 0.421371 | 8.00864 | 32.737 | 90.5774 | 160.562 | 121 |
| Qreg_Qi | (adim) | 0.0214162 | 0.0716836 | 0.28474 | 0.934042 | 2.35546 | 121 |
| r_P | (adim) | 1.32353 | 1.61157 | 2.74825 | 4.91667 | 6.78947 | 121 |

### C4 (231 puntos)

Clases: 137 KALINA (total), 28 CORREGIBLE, 9 INVIABLE y 57 NO_CONVERGIO.

Ventanas p10-p90 de las 9 variables entre los KALINA (total); el redondeo (0.5 K, 10 kPa, 0.01 y 0.05) marca la resolucion de estas cifras:

| variable | p10 | mediana | p90 | n |
|---|---|---|---|---|
| T_fuente | 367.8 | 396 | 417.7 | 137 |
| T_sumidero | 279 | 284 | 289 | 137 |
| P_alta | 2036 | 3240 | 4564 | 137 |
| P_baja | 862 | 1280 | 1654 | 137 |
| x_b | 0.606 | 0.75 | 0.88 | 137 |
| eta_t | 0.55 | 0.75 | 0.9 | 137 |
| eps_hrvg | 0.55 | 0.75 | 0.9 | 137 |
| eps_reg | 0.55 | 0.75 | 0.9 | 137 |
| eps_cond | 0.85 | 0.9 | 0.95 | 137 |

KS de cada variable: KALINA (total) frente al resto de puntos genuinos (CORREGIBLE + INVIABLE). D va de 0 (mismo muestreo) a 1; p-valor bajo (< 0.05) se lee como distribucion distinta (con valores redondeados, indicativo):

| variable | D | p-valor | n KALINA | n resto |
|---|---|---|---|---|
| T_fuente | 0.142 | 0.541 | 137 | 37 |
| T_sumidero | 0.271 | 0.0218 | 137 | 37 |
| P_alta | 0.0953 | 0.926 | 137 | 37 |
| P_baja | 0.411 | 6.12e-05 | 137 | 37 |
| x_b | 0.291 | 0.0111 | 137 | 37 |
| eta_t | 0.109 | 0.835 | 137 | 37 |
| eps_hrvg | 0.14 | 0.558 | 137 | 37 |
| eps_reg | 0.0525 | 1 | 137 | 37 |
| eps_cond | 0.238 | 0.0605 | 137 | 37 |

PRCC con eta entre los KALINA (total): rangos con promedio en empates y residuos de minimos cuadrados con intercepta (solo numpy). +1 sube eta, -1 la baja, ~0 no aporta linealmente:

| variable | PRCC |
|---|---|
| T_fuente | 0.524 |
| T_sumidero | 0.0497 |
| P_alta | 0.602 |
| P_baja | -0.681 |
| x_b | 0.607 |
| eta_t | 0.579 |
| eps_hrvg | 0.286 |
| eps_reg | 0.329 |
| eps_cond | -0.0912 |

Lectura: la mayor influencia positiva lineal es **x_b** (PRCC 0.607) y la mayor negativa **P_baja** (PRCC -0.681).

Top 10 de eta entre los KALINA (total):

| puesto | id | eta [%] | Wnet [kW] | T_fuente [K] | P_alta [kPa] | P_baja [kPa] | x_b | eta_t |
|---|---|---|---|---|---|---|---|---|
| 1 | N8-C4-0090 | 11.18 | 108.37 | 410.5 | 4710 | 1160 | 0.79 | 0.9 |
| 2 | N8-C4-0192 | 10.29 | 122.65 | 408.5 | 4280 | 1550 | 0.91 | 0.95 |
| 3 | N8-C4-0087 | 10.02 | 93.747 | 419.5 | 4810 | 1120 | 0.82 | 0.7 |
| 4 | N8-C4-0013 | 9.51 | 100.29 | 421.5 | 4020 | 1050 | 0.75 | 0.8 |
| 5 | N8-C4-0033 | 9.22 | 65.913 | 372.5 | 3490 | 1270 | 0.88 | 0.95 |
| 6 | N8-C4-0082 | 9.20 | 69.717 | 396.5 | 3510 | 1070 | 0.76 | 0.85 |
| 7 | N8-C4-0215 | 9.04 | 86.03 | 394 | 3970 | 1580 | 0.9 | 0.95 |
| 8 | N8-C4-0045 | 8.62 | 40.688 | 422 | 3470 | 810 | 0.56 | 0.85 |
| 9 | N8-C4-0092 | 8.49 | 68.259 | 407 | 4910 | 1600 | 0.93 | 0.85 |
| 10 | N8-C4-0176 | 8.37 | 89.538 | 412.5 | 3430 | 930 | 0.8 | 0.7 |

Rangos de equipos entre los KALINA (total): dh_turb en kJ/kg, Wnet en kW con m_b = 1.0 kg/s (kW por kg/s), Qreg/Qi y r_P = P_alta/P_baja sin unidades:

| variable | unidad | min | p10 | mediana | p90 | max | n |
|---|---|---|---|---|---|---|---|
| dh_turb | kJ/kg | 27.7638 | 47.6316 | 94.2665 | 142.5 | 195.753 | 137 |
| Wnet | kW por kg/s | 0.236263 | 7.88016 | 27.1829 | 67.081 | 122.653 | 137 |
| Qreg_Qi | (adim) | 0.0047194 | 0.0838083 | 0.240975 | 0.931287 | 2.74943 | 137 |
| r_P | (adim) | 1.36257 | 1.55436 | 2.55828 | 4.13435 | 5.50602 | 137 |

### Puntos con tiempo agotado: tope duro de 600 s y presupuesto de 300 s

- N10 / C1 (300s): 10 punto(s)
- N10 / C4 (300s): 4 punto(s)
- N8 / C3 (300s): 2 punto(s)
- N8 / C3 (600s): 1 punto(s)
- N8 / C4 (300s): 5 punto(s)
- N9 / C4 (300s): 3 punto(s)


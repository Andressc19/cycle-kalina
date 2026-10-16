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

### Planeados vs evaluados

- **N10**: planeados 105 (ronda3_diseno.csv) vs evaluados 105 (ronda3_filas.csv).
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

## 4. N8

- N8: todavia no se definio ni se corro; el corredor ya acepta el argumento N8 y el reporte se limita a los barridos con filas.

### Puntos con tiempo agotado: tope duro de 600 s y presupuesto de 300 s

- N10 / C1 (300s): 10 punto(s)
- N10 / C4 (300s): 4 punto(s)
- N9 / C4 (300s): 3 punto(s)


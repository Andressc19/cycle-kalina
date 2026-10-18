# Sens2 F1 - A2b, Parte 1: comparacion pareada CORREGIBLE frente a KALINA

Para cada CORREGIBLE con centro se toma el KALINA (total) mas cercano por
distancia L1 (10 entradas al rango [0, 1] del dataset completo). d_eta es
eta(vecino) - eta(CORREGIBLE): positivo quiere decir que el KALINA cercano rinde
mas que el CORREGIBLE. IC 95 % por bootstrap percentil (1000, semilla 20261018).

## d_eta por grupo

| variante | grupo | n | mediana | IC 95 % mediana |
|---|---|---|---|---|
| mismo_centro | todos | 734 | -0.4307 | [-0.5517, -0.3647] |
| mismo_centro | C1 Husavik | 329 | -0.3909 | [-0.4961, -0.2968] |
| mismo_centro | C2 ancla A* | 171 | -0.7560 | [-1.3509, -0.4343] |
| mismo_centro | C3 caliente 150 C | 128 | -0.3516 | [-0.5385, -0.2009] |
| mismo_centro | C4 frio 110 C | 106 | -0.4852 | [-0.6836, -0.2821] |
| mismo_centro | LHS | 262 | -1.7186 | [-2.1322, -1.3740] |
| mismo_centro | otros | 472 | -0.2795 | [-0.3447, -0.2229] |
| mismo_centro | O1 | 25 | 1.3364 | [-0.2467, 1.7078] |
| mismo_centro | O2 | 709 | -0.4357 | [-0.5735, -0.3721] |
| mismo_centro_y_diseno | todos | 734 | -0.4712 | [-0.5994, -0.3944] |
| mismo_centro_y_diseno | C1 Husavik | 329 | -0.4129 | [-0.5795, -0.3236] |
| mismo_centro_y_diseno | C2 ancla A* | 171 | -0.7568 | [-1.3608, -0.4441] |
| mismo_centro_y_diseno | C3 caliente 150 C | 128 | -0.3622 | [-0.5845, -0.2030] |
| mismo_centro_y_diseno | C4 frio 110 C | 106 | -0.5825 | [-0.7828, -0.3936] |
| mismo_centro_y_diseno | LHS | 262 | -2.0633 | [-2.3854, -1.6355] |
| mismo_centro_y_diseno | otros | 472 | -0.2795 | [-0.3447, -0.2229] |
| mismo_centro_y_diseno | O1 | 25 | 1.3364 | [-0.2467, 1.7078] |
| mismo_centro_y_diseno | O2 | 709 | -0.4973 | [-0.6184, -0.4027] |

## Control

Mediana de d_eta (mismo_centro, grupo todos, solo los cuatro bloques con centro): **-0.4307** (objetivo -0.6405 +/- 0.05).
No se cumple el control: la mediana queda fuera del margen.
Si se incluye ademas el bloque sin centro (los cinco bloques juntos), la mediana de d_eta es -0.6405, que es el valor de la fila de referencia.

d_wnet (mismo esquema de grupos y de IC) esta en `p6_pareado.csv`, junto con
la media y los limites de cada grupo.

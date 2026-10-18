# Sens2 F1 - la diferencia pareada de eta segun la distancia al vecino KALINA

d_eta = eta del KALINA mas cercano - eta del CORREGIBLE. `ajuste`: d_eta = a + b*L1; el estimador es a (diferencia a distancia cero, pp de eta).
`tramo`: mediana de d_eta en cada tramo de distancia L1 (normalizada). IC 95 % por bootstrap (1000, semilla 20261018).

| variante | grupo | calculo | n | estimador | IC 95 % |
|---|---|---|---|---|---|
| mismo_centro | todos | ajuste | 734 | -0.026 | [-0.308, 0.266] |
| mismo_centro | todos | tramo L1 0.0 a 0.2 | 214 | -0.557 | [-0.688, -0.440] |
| mismo_centro | todos | tramo L1 0.2 a 0.5 | 180 | -0.186 | [-0.299, -0.052] |
| mismo_centro | todos | tramo L1 0.5 a mas | 340 | -0.871 | [-1.233, -0.382] |
| mismo_centro | LHS | ajuste | 262 | -1.836 | [-3.555, -0.338] |
| mismo_centro | LHS | tramo L1 0.2 a 0.5 | 9 | -0.937 | [-2.360, -0.434] |
| mismo_centro | LHS | tramo L1 0.5 a mas | 253 | -1.813 | [-2.158, -1.423] |
| mismo_centro | otros | ajuste | 472 | -1.192 | [-1.477, -0.882] |
| mismo_centro | otros | tramo L1 0.0 a 0.2 | 214 | -0.557 | [-0.688, -0.440] |
| mismo_centro | otros | tramo L1 0.2 a 0.5 | 171 | -0.167 | [-0.288, 0.011] |
| mismo_centro | otros | tramo L1 0.5 a mas | 87 | 1.001 | [0.720, 1.376] |
| mismo_centro_y_diseno | todos | ajuste | 734 | 0.080 | [-0.193, 0.374] |
| mismo_centro_y_diseno | todos | tramo L1 0.0 a 0.2 | 214 | -0.557 | [-0.688, -0.440] |
| mismo_centro_y_diseno | todos | tramo L1 0.2 a 0.5 | 175 | -0.179 | [-0.288, -0.052] |
| mismo_centro_y_diseno | todos | tramo L1 0.5 a mas | 345 | -1.119 | [-1.521, -0.792] |
| mismo_centro_y_diseno | LHS | ajuste | 262 | -2.700 | [-4.415, -1.045] |
| mismo_centro_y_diseno | LHS | tramo L1 0.5 a mas | 258 | -2.106 | [-2.452, -1.660] |
| mismo_centro_y_diseno | otros | ajuste | 472 | -1.192 | [-1.477, -0.882] |
| mismo_centro_y_diseno | otros | tramo L1 0.0 a 0.2 | 214 | -0.557 | [-0.688, -0.440] |
| mismo_centro_y_diseno | otros | tramo L1 0.2 a 0.5 | 171 | -0.167 | [-0.288, 0.011] |
| mismo_centro_y_diseno | otros | tramo L1 0.5 a mas | 87 | 1.001 | [0.720, 1.376] |

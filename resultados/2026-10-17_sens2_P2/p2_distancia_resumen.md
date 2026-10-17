# Sens2 P2 - Paso 3: distancia a KALINA y que mover

Distancia L1 normalizada (10 entradas al rango [0, 1] observado) al KALINA
(total) mas cercano dentro del mismo centro.

## Rescate univariado
Fraccion de CORREGIBLE a una sola variable de un KALINA (sobre el total de
CORREGIBLE): P_baja sube 24 %, eps_cond sube 16 %, x_b baja 3 %, T_fuente baja 3 %, P_alta baja 1 %.

## Distribucion (todos)
- L1: P10 0.07895, mediana 0.3648, P90 0.8428.
- N de variables distintas: P10 1, mediana 2, P90 7.

## Cambio de eta al rescatar
eta(vecino KALINA) - eta(CORREGIBLE): mediana -0.6405; IC 95 % ic_lo=-0.7861;ic_hi=-0.2972 (n = 968).

## D frente a L1
Spearman rho = +0.297 (p=3.501e-21).

Los detalles por centro y por violacion dominante estan en
`p2_distancia_resumen.csv`.

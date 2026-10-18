# Sens2 F1 - A7t: eficiencia del ciclo frente a T_fuente

Bandas de T_fuente de 20 K sobre los 3663 puntos de `p2_dataset_dedup.csv`.
eta en % y P(KALINA) = KALINA/n. El maximo es el mayor valor muestreado (no hay
optimizador: no se busca el optimo, solo se describe lo ya calculado).

## Mejor eta dentro del rango experimental por banda

| Banda (T_centro, C) | n | P(KALINA) | eta maxima dentro del rango (%) | P_alta del maximo (kPa) | x_b del maximo (-) |
|---|---|---|---|---|---|
| 76.9 | 106 | 0.160 | 7.010 | 1770.000 | 0.700 |
| 96.9 | 344 | 0.497 | 12.095 | 3300.000 | 0.820 |
| 116.9 | 1257 | 0.542 | 14.010 | 5000.000 | 0.820 |
| 136.9 | 736 | 0.652 | 13.290 | 3640.000 | 0.660 |
| 156.9 | 632 | 0.652 | 14.534 | 6000.000 | 0.750 |
| 176.9 | 248 | 0.504 | 12.317 | 4550.000 | 0.730 |
| 196.9 | 138 | 0.500 | 12.316 | 3900.000 | 0.640 |
| 216.9 | 36 | 0.556 | 3.688 | 3880.000 | 0.880 |
| 236.9 | 35 | 0.571 |  | 3880.000 | 0.880 |
| 256.9 | 34 | 0.382 |  | 3880.000 | 0.880 |
| 276.9 | 35 | 0.400 |  | 3150.000 | 0.750 |
| 296.9 | 62 | 0.403 |  | 4330.000 | 0.760 |

Notas:

- El maximo por banda es el mayor valor muestreado y no el optimo del ciclo.
- Las bandas con menos de 10 KALINA dentro del rango experimental: 6 de 12 bandas; en ellas el maximo dentro del rango no concluye (columna n_kalina_dentro del CSV).
- Sobre ~150 C el limite de 420 K del liquido deja casi todos los KALINA fuera del rango experimental: la caida del maximo dentro del rango en las bandas calientes coincide con ese corte y no es una caida del ciclo.
- El maximo de un conjunto crece con su tamano y las bandas tienen tamanos y disenos de muestreo distintos.
- NO_CONVERGIO sesga hacia abajo la P(KALINA) de las bandas frias;
  p_kalina_si_convergio usa (n - NO_CONVERGIO) como denominador.

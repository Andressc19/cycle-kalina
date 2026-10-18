# Sens2 F1 - A2b, Parte 3: potencia de U1

Cada escenario de U1 tiene 48 puntos nuevos por centro. `precision` resume el
error tipico (sqrt(p(1-p)/n)), el ancho del intervalo de Wilson y el n que haria
falta para una semiamplitud de +/-0.05 y +/-0.10 con la p observada y con el peor
caso p = 0.5. `entre_lotes` compara los lotes U1A y U1A2 por centro.

## Que diferencia entre lotes no se habria detectado

Con 48 puntos por lote, una diferencia de proporcion entre los lotes U1A y U1A2 menor que ~28.6 puntos no se habria detectado con potencia 80 % y nivel 5 %: es el limite en el peor caso (p = 0.5), que es el mismo en todos los centros porque todos tienen 48 puntos. Con la p observada el limite es menor en cada centro (columna de la tabla).

Detalle por centro de la comparacion entre lotes:

| centro | p U1A | p U1A2 | dif | z | dif. minima detectable | peor caso |
|---|---|---|---|---|---|---|
| C1 | 0.479 | 0.458 | +0.021 | 0.20 | 0.2852 | 0.2858 |
| C2 | 0.979 | 1.000 | -0.021 | -1.01 | 0.0580 | 0.2858 |
| C3 | 1.000 | 1.000 | +0.000 | . | 0.0000 | 0.2858 |
| C4 | 0.854 | 0.854 | +0.000 | 0.00 | 0.2017 | 0.2858 |

n por escenario y centro: U1A n=48, U1A2 n=48, U1Ap n=96, U1B n=48, U1C n=48.

La tabla de precision completa esta en `p6_potencia_u1.csv`.

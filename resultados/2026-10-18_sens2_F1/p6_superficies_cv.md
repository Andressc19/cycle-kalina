# Sens2 F1 - p6_superficies_cv: validacion cruzada del ajuste cuadratico de eta

Ajuste eta ~ 1 + a + b + a^2 + b^2 + ab con a y b estandarizadas (media y desviacion de
las celdas KALINA). `r2` y `rmse` son en la muestra; `r2_cv` y `rmse_cv` son dejando una
celda KALINA fuera. `clase_celda_max_ajuste` es la clase de la celda donde cae el maximo
del ajuste sobre toda la malla y `en_borde` si esa celda es la primera o la ultima fila
o columna. `nota` avisa de las mallas con menos de 8 celdas KALINA.

| par | bloque | n celdas | R2 | R2 cv | RMSE | RMSE cv | clase del maximo | en borde |
|---|---|---|---|---|---|---|---|---|
| B2 | C1 Husavik | 43 | 0.9886 | 0.9836 | 0.2697 | 0.3238 | C | si |
| B2 | C2 ancla A* | 23 | 0.9623 | 0.9096 | 0.4903 | 0.7596 | C | si |
| B2 | C3 caliente 150 C | 36 | 0.9987 | 0.9979 | 0.0838 | 0.1057 | C | si |
| B2 | C4 frio 110 C | 39 | 0.9807 | 0.9691 | 0.3621 | 0.4576 | C | si |
| B3 | C1 Husavik | 41 | 0.9993 | 0.9990 | 0.0666 | 0.0788 | C | si |
| B3 | C2 ancla A* | 41 | 0.9735 | 0.9566 | 0.4438 | 0.5676 | K | si |
| B3 | C3 caliente 150 C | 40 | 0.9994 | 0.9991 | 0.0695 | 0.0838 | C | si |
| B3 | C4 frio 110 C | 34 | 0.9999 | 0.9998 | 0.0234 | 0.0286 | C | si |

## Lectura por par

En el par B2 la validacion cruzada casi no degrada el R2: la mayor caida es 0.053 (por debajo de 0.2), asi que el ajuste cuadratico no depende de celdas sueltas.
En el par B3 la validacion cruzada casi no degrada el R2: la mayor caida es 0.017 (por debajo de 0.2), asi que el ajuste cuadratico no depende de celdas sueltas.

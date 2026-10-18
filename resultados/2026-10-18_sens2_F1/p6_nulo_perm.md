# Sens2 F1 - nulo por permutacion y Benjamini-Hochberg

2000 permutaciones por indice; semilla 20261018; q = 0.05 por bloque y respuesta; distinguible = q < 0.05 en al menos 2 metodos.

Calibracion: fraccion de pruebas con p < 0.05 en las 3 variables dummy (debe ser cercana a 0.05): caja=no 0.035

## Caja comun = no

| respuesta | distinguibles con BH | distinguibles con el criterio anterior (P3) | en ambos |
|---|---|---|---|
| Y1 KALINA (total) | 12 | 15 | 11 |
| Y2 eta (%) | 22 | 31 | 22 |
| Y3 W_net/m_b | 21 | 35 | 21 |

## Caja comun de rangos (comparar magnitudes entre bloques)

Puntos de cada LHS que caen dentro del rango comun de las 9 variables de los 4 bloques: E3 C1 Husavik 9, E3 C2 ancla A* 8, E14 C3 caliente 150 C 1, E14 C4 frio 110 C 3.
Quedan menos de 30 puntos por bloque, asi que no se calculan indices en la caja comun: las magnitudes de los indices no se comparan entre bloques; solo se usan los rangos y las pruebas dentro de cada bloque.


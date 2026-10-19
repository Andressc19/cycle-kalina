# Sens2 etapa B - pisos de P_baja con paso de 25 kPa

Piso refinado = menor P_baja desde el cual todos los puntos corridos (paso 25 kPa) hasta el piso de la malla son KALINA. 'mejora' = piso de la malla menos piso refinado.

| centro | x_b | nivel inferior malla | piso malla | puntos | KALINA | CORREGIBLE | NO_CONVERGIO | piso refinado | mejora (kPa) |
|---|---|---|---|---|---|---|---|---|---|
| C1 | 0.82 | 500 | 600 | 3 | 1 | 2 | 0 | 575 | 25 |
| C1 | 0.90 | 600 | 690 | 3 | 1 | 2 | 0 | 675 | 15 |
| C1 | 0.95 | 690 | 800 | 4 | 3 | 1 | 0 | 740 | 60 |
| C2 | 0.50 | - | 400 | 3 | 0 | 3 | 0 | 400 | 0 |
| C2 | 0.55 | 500 | 564 | 2 | 2 | 0 | 0 | 525 | 39 |
| C2 | 0.60 | 564 | 700 | 5 | 3 | 2 | 0 | 639 | 61 |
| C3 | 0.75 | 500 | 650 | 5 | 2 | 3 | 0 | 600 | 50 |
| C3 | 0.88 | 650 | 800 | 5 | 0 | 4 | 1 | 800 | 0 |
| C3 | 0.95 | 800 | 950 | 5 | 5 | 0 | 0 | 825 | 125 |
| C4 | 0.83 | 500 | 650 | 5 | 0 | 4 | 1 | 650 | 0 |
| C4 | 0.88 | 650 | 800 | 5 | 3 | 2 | 0 | 725 | 75 |
| C4 | 0.95 | 800 | 910 | 4 | 3 | 0 | 1 | 875 | 35 |

Los NO_CONVERGIO cuentan como 'no KALINA' al buscar el piso (cortan la secuencia).

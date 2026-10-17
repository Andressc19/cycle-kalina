# Sens2 P1 - paso 2: existencia y P(KALINA)

Rangos en `p1_existencia_rangos.csv`; P(KALINA) por nivel en `p1_existencia_prob.csv`.

## Advertencia sobre la P(KALINA) por nivel

Los puntos probados mezclan tres disenos distintos: barridos OFAT (una variable),
mallas de pares/mapas y muestreos LHS. Por eso la P(KALINA) por nivel de una variable
**depende del diseno**: en un OFAT el resto de variables esta fijo y el nivel aisla su
efecto, mientras que en el LHS todas se mueven a la vez y el nivel es un promedio sobre
las demas. La columna `muestra` distingue `todos` (los 3 921 puntos) de `lhs`.

El LHS usado son los estudios **3** (ids `C1-LHS-*`/`C2-LHS-*`, LHS de 9 variables en
C1 y C2) y **14** (ids `N8-C3-*`/`N8-C4-*`, LHS de 9 variables en C3 y C4): 965 puntos
en total, con >= 9 variables moviendose a la vez en cada punto.
Estudios N1 y N2 tambien usan LHS, pero de 4 y 5 variables: quedan fuera de esta
seleccion por no mover 9 variables a la vez.

## Niveles

Se usa el nivel exacto de la variable si tiene <= 14 valores distintos; si tiene mas,
se divide en 8 cuantiles (tramos `[lo, hi)`). Cada fila lleva su n y el intervalo de
Wilson al 95 %. Los puntos con la variable sin dato (2 casos de `eta_p`) entran como
nivel `sin dato`, para que el n por nivel sume el total del centro.

# Sens2 P1 - paso 3: reglas de la region KALINA (solo LHS)

Solo puntos de los estudios LHS 3 y 14. Cada seccion se calcula por centro y para
todos los puntos LHS juntos.

## C1 Husavik

Puntos 248, KALINA 118 (47.6 %). Regresion logistica: convergio.

### Cortes unicos (stump), mejor primero

| lugar | variable | umbral | lado KALINA | ganancia Gini |
|---|---|---|---|---|
| 1 | x_b | 0.785 | <= | 0.0716 |
| 2 | P_baja | 955 | > | 0.0365 |
| 3 | eps_cond | 0.875 | > | 0.0255 |
| 4 | P_alta | 4475 | <= | 0.0203 |
| 5 | T_fuente | 431.75 | <= | 0.0173 |

### Reglas del arbol (pureza >= 0.9, n >= 30)

**KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

**no-KALINA:**
- `x_b > 0.785 Y eps_cond <= 0.875` -> n = 51, KALINA = 6 % (pureza 0.94)

## C2 ancla A*

Puntos 250, KALINA 131 (52.4 %). Regresion logistica: convergio.

### Cortes unicos (stump), mejor primero

| lugar | variable | umbral | lado KALINA | ganancia Gini |
|---|---|---|---|---|
| 1 | x_b | 0.555 | <= | 0.0479 |
| 2 | P_baja | 715 | > | 0.0477 |
| 3 | eps_cond | 0.875 | > | 0.0425 |
| 4 | T_fuente | 452.25 | <= | 0.0318 |
| 5 | T_sumidero | 296.25 | <= | 0.0237 |

### Reglas del arbol (pureza >= 0.9, n >= 30)

**KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

**no-KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

## C3 caliente 150 C

Puntos 234, KALINA 121 (51.7 %). Regresion logistica: convergio.

### Cortes unicos (stump), mejor primero

| lugar | variable | umbral | lado KALINA | ganancia Gini |
|---|---|---|---|---|
| 1 | P_baja | 1205 | > | 0.0423 |
| 2 | x_b | 0.855 | <= | 0.0194 |
| 3 | T_sumidero | 279.75 | <= | 0.0188 |
| 4 | eps_cond | 0.925 | > | 0.0134 |
| 5 | T_fuente | 395.75 | > | 0.0115 |

### Reglas del arbol (pureza >= 0.9, n >= 30)

**KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

**no-KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

## C4 frio 110 C

Puntos 231, KALINA 137 (59.3 %). Regresion logistica: convergio.

### Cortes unicos (stump), mejor primero

| lugar | variable | umbral | lado KALINA | ganancia Gini |
|---|---|---|---|---|
| 1 | T_fuente | 366.25 | > | 0.0560 |
| 2 | P_baja | 955 | > | 0.0358 |
| 3 | x_b | 0.885 | <= | 0.0276 |
| 4 | P_alta | 2860 | <= | 0.0159 |
| 5 | eps_cond | 0.875 | > | 0.0156 |

### Reglas del arbol (pureza >= 0.9, n >= 30)

**KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

**no-KALINA:**
- `T_fuente <= 366.25 Y P_alta > 2800` -> n = 32, KALINA = 3 % (pureza 0.97)

## todos

Puntos 963, KALINA 507 (52.6 %). Regresion logistica: convergio.

### Cortes unicos (stump), mejor primero

| lugar | variable | umbral | lado KALINA | ganancia Gini |
|---|---|---|---|---|
| 1 | P_baja | 865 | > | 0.0343 |
| 2 | eps_cond | 0.875 | > | 0.0215 |
| 3 | x_b | 0.895 | <= | 0.0154 |
| 4 | T_fuente | 366.25 | > | 0.0114 |
| 5 | T_sumidero | 279.75 | <= | 0.0071 |

### Reglas del arbol (pureza >= 0.9, n >= 30)

**KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

**no-KALINA:**
- (ninguna regla cumple pureza >= 0.9 con n >= 30)

Nota: el signo de la logistica es el efecto sobre P(KALINA) con las demas variables
fijas en su media (variables estandarizadas); las variables constantes del bloque se
omiten y se listan solo las que quedan.
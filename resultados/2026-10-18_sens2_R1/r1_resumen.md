# Sens2 R1 - contraste fuera de muestra del libro viejo

Puntos `cerca` (dist <= 0.15) usados en A y B: 430.

## A. KALINA viejos dentro de los rangos KALINA de Sens2

- C1 Husavik: 7/7 dentro en las 10 variables (100.0 %).
- C2 ancla A*: 165/182 dentro en las 10 variables (90.7 %).
- C3 caliente 150 C: 8/23 dentro en las 10 variables (34.8 %).
- C4 frio 110 C: 1/1 dentro en las 10 variables (100.0 %).
- Total: 181/213 (85.0 %) dentro en las 10 variables a la vez.

Aportes (KALINA viejo fuera de rango de Sens2): 2 filas centro-variable;
32 KALINA con al menos una variable fuera del rango de su centro.

| centro | variable | n |
|---|---|---|
| C2 ancla A* | T_fuente | 17 |
| C3 caliente 150 C | eps_cond | 15 |

## B. Acuerdo de las fronteras

Tasa de acuerdo global (n >= 5): 0.561 (2043 aciertos / 3644 puntos).
Fronteras evaluadas con n >= 5: 26; con n insuficiente: 0.

Contradicciones (acuerdo < 0.5): 8.

| centro | variable | forma | direccion | frontera | n | acuerdo |
|---|---|---|---|---|---|---|
| C2 ancla A* | P_alta | escalon | a no-KALINA | 3875.0 | 399 | 0.499 |
| C3 caliente 150 C | eps_cond | escalon | a KALINA | 0.875 | 34 | 0.441 |
| C4 frio 110 C | P_alta | ventana | a no-KALINA | 1625.0 | 6 | 0.167 |
| C4 frio 110 C | P_alta | ventana | a KALINA | 1875.0 | 6 | 0.167 |
| C4 frio 110 C | T_fuente | ventana | a KALINA | 358.15 | 7 | 0.143 |
| C4 frio 110 C | T_fuente | ventana | a no-KALINA | 528.15 | 7 | 0.143 |
| C4 frio 110 C | T_sumidero | escalon | a no-KALINA | 291.9 | 15 | 0.267 |
| C4 frio 110 C | x_b | escalon | a KALINA | 0.625 | 6 | 0.167 |

## C. Cobertura de huecos por centro

| centro | clase | n <= 0.15 | n <= 0.25 |
|---|---|---|---|
| C1 Husavik | KALINA | 7 | 7 |
| C1 Husavik | CORREGIBLE | 4 | 20 |
| C1 Husavik | NO_CONVERGIO | 0 | 1 |
| C1 Husavik | INVIABLE | 0 | 8 |
| C2 ancla A* | KALINA | 182 | 211 |
| C2 ancla A* | CORREGIBLE | 157 | 220 |
| C2 ancla A* | NO_CONVERGIO | 19 | 36 |
| C2 ancla A* | INVIABLE | 21 | 49 |
| C3 caliente 150 C | KALINA | 23 | 124 |
| C3 caliente 150 C | CORREGIBLE | 11 | 64 |
| C3 caliente 150 C | NO_CONVERGIO | 0 | 7 |
| C3 caliente 150 C | INVIABLE | 0 | 2 |
| C4 frio 110 C | KALINA | 1 | 3 |
| C4 frio 110 C | CORREGIBLE | 5 | 15 |
| C4 frio 110 C | NO_CONVERGIO | 0 | 0 |
| C4 frio 110 C | INVIABLE | 0 | 0 |
- Ganador por cobertura <= 0.25: C2 ancla A* (516 puntos).
- Mayor ganancia al pasar de 0.15 a 0.25: C3 caliente 150 C (+163 puntos; +101 KALINA).
- El centro C4 sube de 6 a 18 puntos al pasar de 0.15 a 0.25.

## D. Respuestas
- Fraccion de KALINA viejos dentro de los rangos de Sens2: 85.0 %.
- Acuerdo global de las fronteras: 0.561; 8 de 26 filas con n >= 5 se contradicen.
- Centro con mas puntos a <= 0.25: C2 ancla A*; centro que mas gana al ampliar de 0.15 a 0.25: C3 caliente 150 C.
- Cautela: C1 (7 KALINA) y C4 (1 KALINA) no permiten concluir; los 15 aportes de C3 en eps_cond son un solo valor repetido (0.841826, 0.008 bajo el minimo de Sens2) y los 17 de C2 en T_fuente estan a menos de 3.2 K del minimo: aportes marginales, no un rango nuevo.
- Cautela: la tasa global de acuerdo de las fronteras queda cerca del azar; esta dominada por C2 y varias filas tienen n de 6 o 7 (no concluyente en C4).

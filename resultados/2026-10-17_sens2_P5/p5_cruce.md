# Sens2 P5 - cruce de cifras entre conclusiones

Numeros con unidad de `p5_conclusiones.csv` agrupados por (unidad, dos palabras previas). Un grupo con al menos 2 conclusiones distintas y al menos 2 valores distintos (a 2 decimales) es un candidato a contradiccion. La lista es para revision manual: un candidato no es un error.

- apariciones: 393
- claves (pares clave, unidad): 338
- candidatos: 18

## Candidatos

### (sin palabras previas) | %

- conclusiones: L2, M1
- valores (2 decimales): 14.82, 49

| id | campo | valor | contexto |
|---|---|---:|---|
| M1 | evidencia | 14.82 | 14.82 %: fuente 443.15 K, P_alta 4550 kPa, P_baja 610 kPa, x_b 0.73 |
| L2 | evidencia | 49.0 | 49 % de los 968 CORREGIBLE está a una sola variable de un KALINA |

### c3 y | K

- conclusiones: D5, U1, U4
- valores (2 decimales): 8.1, 291.9

| id | campo | valor | contexto |
|---|---|---:|---|
| D5 | evidencia | 291.9 | subir T_sumidero por encima de 284.4 K (C1), 296.9 K (C3) y 291.9 K (C4). En C2 (centro a 300.15 K) no hay cambio en el barrido |
| U1 | evidencia | 8.1 | 2 con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4); entre ε_cond 0.92 y 0.95 el margen cae ≈ 1.9 K por ca |
| U4 | evidencia | 8.1 | n con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4). |

### con m_o2 | K

- conclusiones: U1, U4
- valores (2 decimales): 0.1, 0.3

| id | campo | valor | contexto |
|---|---|---:|---|
| U1 | evidencia | 0.1 | tro): C1 es KALINA desde ε_cond 0.922 (CORREGIBLE con m_O2 −0.1 K en 0.911), C4 desde 0.906 (m_O2 −0.0 K en 0.900), y C2 y C3 |
| U4 | evidencia | 0.3 |  C1 entre 0.917 (sin convergencia) y 0.922 (KALINA con m_O2 0.3 K); C4 entre 0.900 (CORREGIBLE) y 0.906 (KALINA con m_O2 0.3  |
| U4 | evidencia | 0.3 | .3 K); C4 entre 0.900 (CORREGIBLE) y 0.906 (KALINA con m_O2 0.3 K); C2 y C3 KALINA en todo el barrido de 0.90 a 0.95. La regr |

### con η | %

- conclusiones: L4, M2
- valores (2 decimales): 12, 15

| id | campo | valor | contexto |
|---|---|---:|---|
| M2 | evidencia | 12.0 | cada: P_alta 3300, P_baja 690, ε_cond 0.95) es KALINA con η 12.00 %. |
| L4 | evidencia | 15.0 | Entre los 2047 KALINA (total) con η: 15 % fuera. El máximo global (14.82 %) está fuera; el máximo den |

### de los | puntos

- conclusiones: M6, U1
- valores (2 decimales): 66, 106

| id | campo | valor | contexto |
|---|---|---:|---|
| U1 | evidencia | 66.0 |  el barrido: 1.2 y 1.7 K; la relación no es lineal). De los 66 puntos que pierden la clase en A, 64 son CORREGIBLE por cavitación |
| M6 | evidencia | 106.0 | °C, fuera del rango. En la banda de 77 °C la mayoría de los 106 puntos no convergió (P(KALINA) 0.16; 0.81 si se excluyen los NO_CO |

### el | %

- conclusiones: L1, L4
- valores (2 decimales): 15, 96

| id | campo | valor | contexto |
|---|---|---:|---|
| L1 | afirmacion | 96.0 | El 96 % de los CORREGIBLE muestreados falla por cavitación (O2) y e |
| L4 | afirmacion | 15.0 | El 15 % de los KALINA muestreados está fuera del rango experimental |

### en el | %

- conclusiones: E3, E4, E5, E9, F1
- valores (2 decimales): 3.5, 10

| id | campo | valor | contexto |
|---|---|---:|---|
| E3 | evidencia | 10.0 | salida q4 en KALINA: mínimo 0.9014 (límite O1: 0.90). En el 10 % de mayor η: mediana 0.9355 y P5 0.9101, frente a 0.950 de t |
| E3 | implicacion | 10.0 |  η (M1 y M2) el margen al límite es de 0.006 a 0.009; en el 10 % de mayor η su mediana es 0.036 (máximo 0.055) y solo el 5 % |
| E4 | evidencia | 10.0 | D mediana 37.7 K; UA mediana 4.29 kW/K por kg/s (3.14 en el 10 % de mayor η); Q_reg/Q_i mediana 0.21 (0.03 a 1.31). Sin cruc |
| E5 | evidencia | 10.0 | Mediana: 721 kW por kg/s y 9.2 K. En el 10 % de mayor η: 542 a 1275 kW por kg/s. La carga la fija T_fuen |
| F1 | evidencia | 3.5 |  3 dummy) a 22; las pruebas de las dummy dan p < 0.05 en el 3.5 % de los casos. |
| E9 | evidencia | 10.0 |  neto (0.071); fluido 0.007 a 0.129 kg/s por kW neto. En el 10 % de mayor η (n = 205): Q_i 7.4 a 8.6 kW por kW neto (8.2), Q |

### es m_o2 | K

- conclusiones: M1, M2
- valores (2 decimales): 0.7, 3.7

| id | campo | valor | contexto |
|---|---|---:|---|
| M1 | evidencia | 0.7 | cuentra valores mayores). Su margen de cavitación es m_O2 = 0.7 K en el de 14.82 % y 6.7 K en el de 14.53 %. |
| M2 | implicacion | 3.7 | (600 kPa a x_b 0.82, D8); su margen de cavitación es m_O2 = 3.7 K (L7). |

### frente a | %

- conclusiones: D3, F6
- valores (2 decimales): 7.7, 36

| id | campo | valor | contexto |
|---|---|---:|---|
| D3 | evidencia | 36.0 |  sí convergieron, el 95 % es KALINA en C4 [78, 99] frente a 36 % si NO_CONVERGIO cuenta como no KALINA. T_fuente es la varia |
| F6 | evidencia | 7.7 | Medianas sin parear de η: 10.2 % frente a 7.7 % (+2.47 puntos, IC 95 % [+2.18, +2.70]); dentro de cada bloq |

### fuente de | °C

- conclusiones: L4, M1, M2
- valores (2 decimales): 121, 150

| id | campo | valor | contexto |
|---|---|---:|---|
| M1 | implicacion | 150.0 | Para una fuente de 150 °C los puntos muestreados llegan a ≈ 14.5 % con P_alta alta (≥ |
| M2 | implicacion | 121.0 | Con la misma fuente de 121 °C, ganar ≈ 2.0 puntos exige más presión y quedar cerca del pi |
| L4 | evidencia | 150.0 |  del rango es 14.53 %. La marca empieza hacia una fuente de 150 °C. |

### k c1 | K

- conclusiones: D3, D5, U1, U4
- valores (2 decimales): 11.8, 296.9, 468.15

| id | campo | valor | contexto |
|---|---|---:|---|
| D3 | evidencia | 468.15 | .62). Techo en los barridos de una variable: 440.65 K (C1), 468.15 K (C2), 568.15 K (C3), 528.15 K (C4). |
| D5 | evidencia | 296.9 |  de existir al subir T_sumidero por encima de 284.4 K (C1), 296.9 K (C3) y 291.9 K (C4). En C2 (centro a 300.15 K) no hay cambi |
| U1 | evidencia | 11.8 | son en todo el barrido. m_O2 con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4); entre ε_cond 0.92 y 0.95 el |
| U4 | evidencia | 11.8 | puntos. Margen de cavitación con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4). |

### k c2 | K

- conclusiones: D3, U1, U4
- valores (2 decimales): 14.9, 568.15

| id | campo | valor | contexto |
|---|---|---:|---|
| D3 | evidencia | 568.15 | los barridos de una variable: 440.65 K (C1), 468.15 K (C2), 568.15 K (C3), 528.15 K (C4). |
| U1 | evidencia | 14.9 | l barrido. m_O2 con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4); entre ε_cond 0.92 y 0.95 el margen cae ≈ |
| U4 | evidencia | 14.9 | n de cavitación con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4). |

### llega a | %

- conclusiones: M2, M3
- valores (2 decimales): 13.95, 14

| id | campo | valor | contexto |
|---|---|---:|---|
| M2 | afirmacion | 14.0 | Para Húsavík el mejor KALINA muestreado llega a 14.0 % subiendo P_alta a 5000 kPa y bajando P_baja a 600 kPa, unos |
| M3 | afirmacion | 13.95 | _t y ε_reg en 0.95), el punto muestreado de Húsavík llega a 13.95 % sin cambiar las presiones. |

### mediana | kW

- conclusiones: E5, E6
- valores (2 decimales): 721, 790

| id | campo | valor | contexto |
|---|---|---:|---|
| E5 | evidencia | 721.0 | Mediana: 721 kW por kg/s y 9.2 K. En el 10 % de mayor η: 542 a 1275 kW por  |
| E6 | evidencia | 790.0 | Mediana 790 kW por kg/s; T_fuente − T3 de 2.1 a 44.0 K. La carga la fija T |

### medio entre | m

- conclusiones: F1, F3
- valores (2 decimales): 6, 8

| id | campo | valor | contexto |
|---|---|---:|---|
| F1 | evidencia | 6.0 | Rango medio entre 6 métodos (1 = mayor; η existe solo en los KALINA: 118 a 137 pu |
| F3 | evidencia | 8.0 | Rango medio entre 8 métodos en Y1 (1 = mayor): C1 x_b 1.0, P_baja 2.6, ε_cond 2.8 |

### solo el | %

- conclusiones: E3, L6
- valores (2 decimales): 5, 6

| id | campo | valor | contexto |
|---|---|---:|---|
| E3 | implicacion | 5.0 | 0 % de mayor η su mediana es 0.036 (máximo 0.055) y solo el 5 % tiene 0.01 o menos. |
| L6 | evidencia | 6.0 | mallas de pares la de ε_cond×T_sumidero deja KALINA solo el 6 % (C1), 67 % (C2), 16 % (C3) y 10 % (C4); la de ε_reg×η_t es  |

### y el | %

- conclusiones: L1, U5
- valores (2 decimales): 4, 56

| id | campo | valor | contexto |
|---|---|---:|---|
| L1 | afirmacion | 4.0 | e los CORREGIBLE muestreados falla por cavitación (O2) y el 4 % por título de salida (O1). |
| U5 | evidencia | 56.0 |  por debajo de la frontera el 72 % del intervalo en C1 y el 56 % en C4. Con 48 puntos por centro los intervalos de C1 se sol |

### δh mediana | kJ/kg

- conclusiones: E1, E2
- valores (2 decimales): 47, 152.7

| id | campo | valor | contexto |
|---|---|---:|---|
| E1 | evidencia | 152.7 | KALINA (total), n = 2047: r_P mediana 3.47; Δh mediana 152.7 kJ/kg; Wt 10.7 a 145.9 kW por kg/s de m_b; T de entrada 361 a 443 |
| E2 | evidencia | 47.0 | (n = 507 en el muestreo LHS). Por bandas de r_P: Δh mediana 47 kJ/kg en [1, 1.5) y 236 kJ/kg en [6, 10); η mediana 2.5 % y 10.1  |


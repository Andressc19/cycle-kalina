# REPORTE M4 — sensibilidad global con LHS (10 variables a la vez)
## 1. La pregunta
Moviendo **las 10 variables a la vez** dentro de un rango favorable y realista: **¿qué variables deciden que el ciclo sea KALINA?, ¿en qué rango hay que ponerlas? y ¿qué combinaciones dan KALINA con mayor η?**
## 2. Qué se hizo, en simple
- **Muestreo.** 6 puntos con muestreo latino hipercubico (LHS, semilla 20261006): cada rango se divide en 6 franjas y cae exactamente un punto en cada franja de cada variable, así ninguna zona de la caja queda sin explorar. La muestra quedó en `m4_muestra.csv` ANTES de correr.
- **Corrida.** Los 6 puntos se resolvieron con el motor `teqp` y 5 procesos, con el piso de O2 de cada punto igual a su propia `T_sumidero`. Todo quedó en `m4_lhs.csv`.
- **Punto bueno (genuino).** Solo cuentan KALINA, CORREGIBLE e INVIABLE. Una fila que el solver cerró pero que el clasificador marca NO_CONVERGIO es un punto fijo espurio (N2) y es NO genuina en todo.
- **Análisis.** RSA (KS, valor p, IC95 % por bootstrap de 1000 remuestreos y rango favorable = percentiles 5–95) con cuatro separaciones; PAWN con 10 franjas; PRCC con rangos, residuos y prueba t; un árbol CART; la convergencia del ranking con los primeros 150 puntos; y el top-10.
## 3. Cuántos KALINA salieron
De **6** puntos: **2 KALINA**. Conteos por clase: CORREGIBLE = 3, KALINA = 2, NO_CONVERGIO = 1.
Puntos genuinos: 5. Espurios N2 (`convergio=True` y NO_CONVERGIO): 0. Fuera del rango confiable del motor de propiedades: 3.
## 4. Qué variables deciden KALINA y su rango favorable
Separación **KALINA vs el resto** (B = los 2 KALINA; B̄ = los 4 demás), ordenada por KS. El rango favorable es donde viven los KALINA (percentiles 5–95 dentro de B):

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| P_alta | 1.000 | [1.000, 1.000] | 0.1333 | [4042.62, 4758.37] | 2 | 4 |
| eps_hrvg | 1.000 | [1.000, 1.000] | 0.1333 | [0.648732, 0.698129] | 2 | 4 |
| T_sumidero | 0.750 | [0.500, 1.000] | 0.4 | [280.732, 289.024] | 2 | 4 |
| eps_cond | 0.750 | [0.500, 1.000] | 0.4 | [0.834562, 0.938852] | 2 | 4 |
| T_fuente | 0.500 | [0.250, 1.000] | 0.9333 | [426.305, 471.857] | 2 | 4 |
| P_baja | 0.500 | [0.500, 1.000] | 0.9333 | [662.257, 1413.61] | 2 | 4 |
| x_b | 0.500 | [0.500, 1.000] | 0.9333 | [0.536626, 0.721829] | 2 | 4 |
| eta_t | 0.500 | [0.250, 1.000] | 0.9333 | [0.83672, 0.88312] | 2 | 4 |
| eta_p | 0.500 | [0.500, 1.000] | 0.9333 | [0.717482, 0.874649] | 2 | 4 |
| eps_reg | 0.500 | [0.500, 1.000] | 0.9333 | [0.732027, 0.891054] | 2 | 4 |
| dP | 0.500 | [0.500, 1.000] | 0.9333 | [2629.01, 4096.11] | 2 | 4 |
| rP | 0.500 | [0.500, 1.000] | 0.9333 | [2.99954, 7.48339] | 2 | 4 |
| dT_fs | 0.500 | [0.250, 1.000] | 0.9333 | [137.281, 191.125] | 2 | 4 |

**Aviso:** estos grupos quedaron con menos de 20 puntos y NO se amplió el muestreo por cuenta propia (el director decide):
- `KALINA/T_fuente: n_B=2, n_Bbar=4`
- `KALINA/T_sumidero: n_B=2, n_Bbar=4`
- `KALINA/P_alta: n_B=2, n_Bbar=4`
- `KALINA/P_baja: n_B=2, n_Bbar=4`
- `KALINA/x_b: n_B=2, n_Bbar=4`
- `KALINA/eta_t: n_B=2, n_Bbar=4`
- `KALINA/eta_p: n_B=2, n_Bbar=4`
- `KALINA/eps_hrvg: n_B=2, n_Bbar=4`
- `KALINA/eps_reg: n_B=2, n_Bbar=4`
- `KALINA/eps_cond: n_B=2, n_Bbar=4`
- `KALINA/dP: n_B=2, n_Bbar=4`
- `KALINA/rP: n_B=2, n_Bbar=4`
- `KALINA/dT_fs: n_B=2, n_Bbar=4`
- `converge/T_fuente: n_B=5, n_Bbar=1`
- `converge/T_sumidero: n_B=5, n_Bbar=1`
- `converge/P_alta: n_B=5, n_Bbar=1`
- `converge/P_baja: n_B=5, n_Bbar=1`
- `converge/x_b: n_B=5, n_Bbar=1`
- `converge/eta_t: n_B=5, n_Bbar=1`
- `converge/eta_p: n_B=5, n_Bbar=1`
- `converge/eps_hrvg: n_B=5, n_Bbar=1`
- `converge/eps_reg: n_B=5, n_Bbar=1`
- `converge/eps_cond: n_B=5, n_Bbar=1`
- `converge/dP: n_B=5, n_Bbar=1`
- `converge/rP: n_B=5, n_Bbar=1`
- `converge/dT_fs: n_B=5, n_Bbar=1`
- `cumple_O2/T_fuente: n_B=2, n_Bbar=3`
- `cumple_O2/T_sumidero: n_B=2, n_Bbar=3`
- `cumple_O2/P_alta: n_B=2, n_Bbar=3`
- `cumple_O2/P_baja: n_B=2, n_Bbar=3`
- `cumple_O2/x_b: n_B=2, n_Bbar=3`
- `cumple_O2/eta_t: n_B=2, n_Bbar=3`
- `cumple_O2/eta_p: n_B=2, n_Bbar=3`
- `cumple_O2/eps_hrvg: n_B=2, n_Bbar=3`
- `cumple_O2/eps_reg: n_B=2, n_Bbar=3`
- `cumple_O2/eps_cond: n_B=2, n_Bbar=3`
- `cumple_O2/dP: n_B=2, n_Bbar=3`
- `cumple_O2/rP: n_B=2, n_Bbar=3`
- `cumple_O2/dT_fs: n_B=2, n_Bbar=3`
- `cumple_O1/T_fuente: n_B=5, n_Bbar=0`
- `cumple_O1/T_sumidero: n_B=5, n_Bbar=0`
- `cumple_O1/P_alta: n_B=5, n_Bbar=0`
- `cumple_O1/P_baja: n_B=5, n_Bbar=0`
- `cumple_O1/x_b: n_B=5, n_Bbar=0`
- `cumple_O1/eta_t: n_B=5, n_Bbar=0`
- `cumple_O1/eta_p: n_B=5, n_Bbar=0`
- `cumple_O1/eps_hrvg: n_B=5, n_Bbar=0`
- `cumple_O1/eps_reg: n_B=5, n_Bbar=0`
- `cumple_O1/eps_cond: n_B=5, n_Bbar=0`
- `cumple_O1/dP: n_B=5, n_Bbar=0`
- `cumple_O1/rP: n_B=5, n_Bbar=0`
- `cumple_O1/dT_fs: n_B=5, n_Bbar=0`
### 4.1 Las otras separaciones (misma caja)
**Genuino vs no genuino:**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| T_fuente | 1.000 | n/d | 0.3333 | [411.984, 494.064] | 5 | 1 |
| T_sumidero | 1.000 | n/d | 0.3333 | [281.3, 296.934] | 5 | 1 |
| P_baja | 1.000 | n/d | 0.3333 | [652.313, 1406.62] | 5 | 1 |
| x_b | 1.000 | n/d | 0.3333 | [0.544224, 0.750755] | 5 | 1 |
| eps_cond | 1.000 | n/d | 0.3333 | [0.757991, 0.931656] | 5 | 1 |
| dT_fs | 1.000 | n/d | 0.3333 | [115.671, 203.937] | 5 | 1 |
| P_alta | 0.800 | n/d | 0.6667 | [2299.4, 4639.08] | 5 | 1 |
| eps_reg | 0.800 | n/d | 0.6667 | [0.63548, 0.875697] | 5 | 1 |
| dP | 0.800 | n/d | 0.6667 | [1140.55, 3963.05] | 5 | 1 |
| rP | 0.800 | n/d | 0.6667 | [1.87089, 7.1826] | 5 | 1 |
| eta_t | 0.600 | n/d | 1 | [0.781889, 0.895322] | 5 | 1 |
| eta_p | 0.600 | n/d | 1 | [0.666686, 0.871423] | 5 | 1 |
| eps_hrvg | 0.600 | n/d | 1 | [0.656965, 0.886968] | 5 | 1 |

**Cumple O2 vs no (entre genuinos):**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| P_alta | 1.000 | [1.000, 1.000] | 0.2 | [4042.62, 4758.37] | 2 | 3 |
| eps_hrvg | 1.000 | [1.000, 1.000] | 0.2 | [0.648732, 0.698129] | 2 | 3 |
| T_sumidero | 0.667 | [0.500, 1.000] | 0.6 | [280.732, 289.024] | 2 | 3 |
| eta_t | 0.667 | [0.667, 1.000] | 0.6 | [0.83672, 0.88312] | 2 | 3 |
| eps_reg | 0.667 | [0.500, 1.000] | 0.6 | [0.732027, 0.891054] | 2 | 3 |
| eps_cond | 0.667 | [0.500, 1.000] | 0.6 | [0.834562, 0.938852] | 2 | 3 |
| P_baja | 0.500 | [0.500, 1.000] | 0.9 | [662.257, 1413.61] | 2 | 3 |
| x_b | 0.500 | [0.500, 1.000] | 0.9 | [0.536626, 0.721829] | 2 | 3 |
| eta_p | 0.500 | [0.500, 1.000] | 0.9 | [0.717482, 0.874649] | 2 | 3 |
| dP | 0.500 | [0.500, 1.000] | 0.9 | [2629.01, 4096.11] | 2 | 3 |
| rP | 0.500 | [0.500, 1.000] | 0.9 | [2.99954, 7.48339] | 2 | 3 |
| T_fuente | 0.333 | [0.333, 1.000] | 1 | [426.305, 471.857] | 2 | 3 |
| dT_fs | 0.333 | [0.333, 1.000] | 1 | [137.281, 191.125] | 2 | 3 |

**Cumple O1 vs no (entre genuinos):**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| T_fuente | n/d | n/d | n/d | [411.984, 494.064] | 5 | 0 |
| T_sumidero | n/d | n/d | n/d | [281.3, 296.934] | 5 | 0 |
| P_alta | n/d | n/d | n/d | [2299.4, 4639.08] | 5 | 0 |
| P_baja | n/d | n/d | n/d | [652.313, 1406.62] | 5 | 0 |
| x_b | n/d | n/d | n/d | [0.544224, 0.750755] | 5 | 0 |
| eta_t | n/d | n/d | n/d | [0.781889, 0.895322] | 5 | 0 |
| eta_p | n/d | n/d | n/d | [0.666686, 0.871423] | 5 | 0 |
| eps_hrvg | n/d | n/d | n/d | [0.656965, 0.886968] | 5 | 0 |
| eps_reg | n/d | n/d | n/d | [0.63548, 0.875697] | 5 | 0 |
| eps_cond | n/d | n/d | n/d | [0.757991, 0.931656] | 5 | 0 |
| dP | n/d | n/d | n/d | [1140.55, 3963.05] | 5 | 0 |
| rP | n/d | n/d | n/d | [1.87089, 7.1826] | 5 | 0 |
| dT_fs | n/d | n/d | n/d | [115.671, 203.937] | 5 | 0 |
## 5. Qué variables mueven η y en qué sentido
**PAWN** (sobre η de los genuinos con W_net > 0 y sobre D de los genuinos; cuanto más alto el índice, más cambia la distribución al fijar la variable):

| variable | PAWN η (mediana) | PAWN η (máx) | PAWN D (mediana) | PAWN D (máx) |
|---|---|---|---|---|
| T_fuente | 0.600 | 0.800 | 0.600 | 0.800 |
| T_sumidero | 0.600 | 0.800 | 0.600 | 0.800 |
| P_alta | 0.600 | 0.800 | 0.500 | 0.800 |
| P_baja | 0.600 | 0.800 | 0.600 | 0.800 |
| x_b | 0.600 | 0.800 | 0.600 | 0.800 |
| eta_t | 0.600 | 0.800 | 0.600 | 0.800 |
| eta_p | 0.600 | 0.800 | 0.600 | 0.800 |
| eps_hrvg | 0.600 | 0.800 | 0.600 | 0.800 |
| eps_reg | 0.600 | 0.800 | 0.600 | 0.800 |
| eps_cond | 0.600 | 0.800 | 0.600 | 0.800 |

Las tres con más peso sobre η por PAWN: T_fuente (0.600), T_sumidero (0.600), P_alta (0.600).

**PRCC** (negativo = subir la variable baja η; el IC95 % que no cruza al cero indica que el efecto se distingue del ruido):

| variable | PRCC η | IC95 % (η) | valor p (η) | PRCC m_O1 | PRCC m_O2 | PRCC m_O5 |
|---|---|---|---|---|---|---|
| eta_p | 1.000 | n/d | n/d | -0.661 | 0.194 | 0.982 |
| P_alta | 0.982 | n/d | n/d | -0.758 | 0.804 | 0.826 |
| eps_hrvg | -0.852 | n/d | n/d | 0.956 | -0.304 | 0.735 |
| eta_t | 0.832 | n/d | n/d | -0.742 | -0.162 | 0.510 |
| P_baja | 0.771 | n/d | n/d | 0.811 | 0.351 | 0.930 |
| T_fuente | -0.626 | n/d | n/d | 0.667 | 0.922 | -0.835 |
| eps_reg | 0.523 | n/d | n/d | 0.537 | 0.951 | -0.525 |
| T_sumidero | -0.415 | n/d | n/d | 0.498 | 0.378 | -0.414 |
| eps_cond | 0.126 | n/d | n/d | 0.039 | 0.710 | -0.129 |
| x_b | 0.108 | n/d | n/d | 0.730 | 0.590 | 0.512 |

Las de mayor |PRCC| sobre η: eta_p (1.000), P_alta (0.982), eps_hrvg (-0.852).
## 6. Las reglas del árbol, en palabras
Clasificador CART (`max_depth=4`, `min_samples_leaf=5`, `random_state=0`) sobre las 10 variables, KALINA vs no KALINA. exactitud CV (5 particiones): NO CALCULADA (muestra pequeña).
- si (sin condiciones) → **no KALINA** (n = 6, 33.3 % KALINA)
## 7. Los diferenciales recomendados dentro de KALINA
Las tres variables derivadas, con su KS en la separación KALINA y su rango favorable (percentiles 5–95 dentro de los KALINA): dP: KS 0.500 y rango favorable [2629.01, 4096.11], rP: KS 0.500 y rango favorable [2.99954, 7.48339], dT_fs: KS 0.500 y rango favorable [137.281, 191.125].
## 8. Los 10 mejores KALINA
Los 2 KALINA de mayor η de la corrida:

| # | id | η | W_net (kW) | D | T_fuente | T_sumidero | P_alta | P_baja | x_b | eta_t | eta_p | eps_hrvg | eps_reg | eps_cond |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.0 | 0.1520 | 177.79 | 0.00 | 474.388 | 280.271 | 4798.13 | 620.516 | 0.732118 | 0.834143 | 0.88338 | 0.645988 | 0.899889 | 0.944646 |
| 2 | 0.0 | 0.0495 | 19.17 | 0.00 | 423.775 | 289.485 | 4002.85 | 1455.35 | 0.526337 | 0.885697 | 0.70875 | 0.700874 | 0.723192 | 0.828768 |
## 9. La convergencia
ρ de Spearman entre el ranking con los primeros 150 puntos y el de los 6: **KS (KALINA) = 1.0000** y **PRCC(η) = 1.0000**. Variables que cambian 2 o más posiciones: ninguna variable cambia 2 o más posiciones.
## 10. Los tiempos
El tiempo total de la corrida no está en stdout.txt. Por punto (`t_s`): mínimo 104.6 s, mediana 160.1 s, máximo 203.3 s, media 151.0 s (6 puntos).
## 11. La conclusión
El RSA de §4 dice qué variables separan KALINA del resto y en qué rango viven los KALINA; PAWN y PRCC de §5 dicen qué variables mueven η y en qué sentido; el árbol de §6 da reglas sí/no que se leen directo; y §7 da los diferenciales (dP, rP, dT_fs) recomendados dentro de KALINA. No se propone ningún valor nuevo: las tablas son insumos para que el director decida.
## 12. Lo que no se sabe
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes: es la banda de incertidumbre del modelo de propiedades (G4-01).
- Hay puntos fuera de rango (motor de propiedades sin respaldo experimental): 3 de 6. Sus η hay que tomarlas con pinzas.
- Esto es una **caja favorable**, no todo el espacio: fuera de los rangos de `TASK_CONTEXT final_M4` no se dijo nada.
## 13. Qué sigue
M5 (búsqueda dirigida hacia KALINA con las variables que señala el RSA). El orden concreto lo decide el director.

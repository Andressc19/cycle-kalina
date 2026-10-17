# Sens2 P1 - paso 4: fronteras y zonas grises

## 1. Fronteras en los barridos de una sola variable (OFAT)

Estudios con la columna `variable` (estudios 1 y 10). Por centro y variable: donde la
clase cambia, con el nivel anterior y el siguiente. Forma = escalon (un cambio), rampa
(mas de un cambio o niveles intermedios mixtos) o ventana (dos cambios).

| centro | variable | forma | niveles | fronteras |
|---|---|---|---|---|
| C1 Husavik | P_alta | sin cambio | 13 | 0 |
| C1 Husavik | P_baja | escalon | 13 | 1 |
| C1 Husavik | T_fuente | ventana | 31 | 2 |
| C1 Husavik | T_sumidero | escalon | 10 | 1 |
| C1 Husavik | eps_cond | sin cambio | 11 | 0 |
| C1 Husavik | eps_hrvg | sin cambio | 11 | 0 |
| C1 Husavik | eps_reg | sin cambio | 11 | 0 |
| C1 Husavik | eta_p | sin cambio | 11 | 0 |
| C1 Husavik | eta_t | sin cambio | 11 | 0 |
| C1 Husavik | x_b | ventana | 14 | 2 |
| C2 ancla A* | P_alta | escalon | 12 | 1 |
| C2 ancla A* | P_baja | escalon | 13 | 1 |
| C2 ancla A* | T_fuente | ventana | 31 | 2 |
| C2 ancla A* | T_sumidero | sin cambio | 11 | 0 |
| C2 ancla A* | eps_cond | escalon | 11 | 1 |
| C2 ancla A* | eps_hrvg | sin cambio | 11 | 0 |
| C2 ancla A* | eps_reg | sin cambio | 11 | 0 |
| C2 ancla A* | eta_p | sin cambio | 11 | 0 |
| C2 ancla A* | eta_t | sin cambio | 11 | 0 |
| C2 ancla A* | x_b | ventana | 13 | 2 |
| C3 caliente 150 C | P_alta | sin cambio | 17 | 0 |
| C3 caliente 150 C | P_baja | escalon | 19 | 1 |
| C3 caliente 150 C | T_fuente | ventana | 23 | 2 |
| C3 caliente 150 C | T_sumidero | escalon | 11 | 1 |
| C3 caliente 150 C | eps_cond | escalon | 11 | 1 |
| C3 caliente 150 C | eps_hrvg | sin cambio | 11 | 0 |
| C3 caliente 150 C | eps_reg | sin cambio | 11 | 0 |
| C3 caliente 150 C | eta_p | sin cambio | 11 | 0 |
| C3 caliente 150 C | eta_t | sin cambio | 11 | 0 |
| C3 caliente 150 C | x_b | escalon | 13 | 1 |
| C4 frio 110 C | P_alta | ventana | 17 | 2 |
| C4 frio 110 C | P_baja | escalon | 19 | 1 |
| C4 frio 110 C | T_fuente | ventana | 23 | 2 |
| C4 frio 110 C | T_sumidero | escalon | 11 | 1 |
| C4 frio 110 C | eps_cond | sin cambio | 11 | 0 |
| C4 frio 110 C | eps_hrvg | rampa | 11 | 4 |
| C4 frio 110 C | eps_reg | sin cambio | 11 | 0 |
| C4 frio 110 C | eta_p | sin cambio | 11 | 0 |
| C4 frio 110 C | eta_t | sin cambio | 11 | 0 |
| C4 frio 110 C | x_b | escalon | 14 | 1 |

Conteo de formas: escalon=12, rampa=1, ventana=7, sin cambio=20.

## 2. Zonas grises (CORREGIBLE con D bajo)

Cuantil 25 % de D entre los CORREGIBLE: **0.2781**.
Zonas grises = CORREGIBLE con D <= ese cuantil: **255** de 1018 CORREGIBLE.

### Conteo por centro

| centro | zonas grises |
|---|---|
| C1 Husavik | 114 |
| C4 frio 110 C | 48 |
| C3 caliente 150 C | 40 |
| (sin centro) | 38 |
| C2 ancla A* | 15 |

### Conteo por violacion dominante

| violacion dominante | zonas grises |
|---|---|
| viol_O2 | 249 |
| viol_O1 | 6 |
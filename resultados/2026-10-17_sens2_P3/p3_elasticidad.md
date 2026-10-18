# Sens2 P3 - elasticidades locales (Paso 3)

Elasticidad = (d eta / eta0) / (d v / v0) en el punto base. Estudios con columna `variable`:
1, 10.

## Elasticidad por variable y centro

| variable | C1 Husavik | C2 ancla A* | C3 caliente 150 C | C4 frio 110 C |
|---|---|---|---|---|
| P_alta | 0.389 | -1.178 | 0.721 | 0.409 |
| P_baja | -0.614 | -0.600 | -0.791 | -0.621 |
| T_fuente | 1.023 | 13.156 | 0.252 | 1.283 |
| T_sumidero | 0.999 | 1.629 | 0.838 | 1.076 |
| eps_cond | . | -0.389 | -0.733 | . |
| eps_hrvg | 0.308 | 0.666 | 0.051 | 0.275 |
| eps_reg | 0.140 | 0.991 | 0.117 | 0.129 |
| eta_p | 0.038 | 0.151 | 0.033 | 0.053 |
| eta_t | 1.037 | 1.153 | 1.031 | 1.054 |
| x_b | 0.588 | 3.906 | 0.599 | 0.717 |

## Detalle (tipo de diferencia por centro y variable)

| centro | variable | eta0 | nivel menos | nivel mas | tipo | elasticidad |
|---|---|---|---|---|---|---|
| C1 Husavik | P_alta | 0.1200 | 3250.0 | 3500.0 | centrada | 0.389 |
| C1 Husavik | P_baja | 0.1200 | 600.0 | 700.0 | centrada | -0.614 |
| C1 Husavik | T_fuente | 0.1200 | 393.15 | 398.15 | centrada | 1.023 |
| C1 Husavik | T_sumidero | 0.1200 |  | 280.65 | hacia adelante | 0.999 |
| C1 Husavik | eps_cond | 0.1200 | 0.9 |  | sin KALINA vecino | . |
| C1 Husavik | eps_hrvg | 0.1200 | 0.8 | 0.9 | centrada | 0.308 |
| C1 Husavik | eps_reg | 0.1200 | 0.7 | 0.8 | centrada | 0.140 |
| C1 Husavik | eta_p | 0.1200 | 0.75 | 0.85 | centrada | 0.038 |
| C1 Husavik | eta_t | 0.1200 | 0.8 | 0.9 | centrada | 1.037 |
| C1 Husavik | x_b | 0.1200 | 0.8 | 0.85 | centrada | 0.588 |
| C2 ancla A* | P_alta | 0.0794 | 2750.0 | 3250.0 | centrada | -1.178 |
| C2 ancla A* | P_baja | 0.0794 | 500.0 | 600.0 | centrada | -0.600 |
| C2 ancla A* | T_fuente | 0.0794 | 398.15 | 403.15 | centrada | 13.156 |
| C2 ancla A* | T_sumidero | 0.0794 | 298.15 | 300.65 | centrada | 1.629 |
| C2 ancla A* | eps_cond | 0.0794 | 0.9 |  | hacia atras | -0.389 |
| C2 ancla A* | eps_hrvg | 0.0794 | 0.8 | 0.9 | centrada | 0.666 |
| C2 ancla A* | eps_reg | 0.0794 | 0.7 | 0.8 | centrada | 0.991 |
| C2 ancla A* | eta_p | 0.0794 | 0.7 | 0.8 | centrada | 0.151 |
| C2 ancla A* | eta_t | 0.0794 | 0.8 | 0.9 | centrada | 1.153 |
| C2 ancla A* | x_b | 0.0794 | 0.45 | 0.55 | centrada | 3.906 |
| C3 caliente 150 C | P_alta | 0.0945 | 3000.0 | 3250.0 | centrada | 0.721 |
| C3 caliente 150 C | P_baja | 0.0945 | 900.0 | 1000.0 | centrada | -0.791 |
| C3 caliente 150 C | T_fuente | 0.0945 | 413.15 | 433.15 | centrada | 0.252 |
| C3 caliente 150 C | T_sumidero | 0.0945 | 278.15 | 280.65 | centrada | 0.838 |
| C3 caliente 150 C | eps_cond | 0.0945 | 0.9 |  | hacia atras | -0.733 |
| C3 caliente 150 C | eps_hrvg | 0.0945 | 0.8 | 0.9 | centrada | 0.051 |
| C3 caliente 150 C | eps_reg | 0.0945 | 0.7 | 0.8 | centrada | 0.117 |
| C3 caliente 150 C | eta_p | 0.0945 | 0.75 | 0.85 | centrada | 0.033 |
| C3 caliente 150 C | eta_t | 0.0945 | 0.8 | 0.9 | centrada | 1.031 |
| C3 caliente 150 C | x_b | 0.0945 | 0.7 | 0.8 | centrada | 0.599 |
| C4 frio 110 C | P_alta | 0.1115 | 3750.0 | 4000.0 | centrada | 0.409 |
| C4 frio 110 C | P_baja | 0.1115 | 900.0 | 1000.0 | centrada | -0.621 |
| C4 frio 110 C | T_fuente | 0.1115 | 373.15 | 393.15 | centrada | 1.283 |
| C4 frio 110 C | T_sumidero | 0.1115 | 280.65 | 283.15 | centrada | 1.076 |
| C4 frio 110 C | eps_cond | 0.1115 | 0.9 |  | sin KALINA vecino | . |
| C4 frio 110 C | eps_hrvg | 0.1115 | 0.8 | 0.9 | centrada | 0.275 |
| C4 frio 110 C | eps_reg | 0.1115 | 0.7 | 0.8 | centrada | 0.129 |
| C4 frio 110 C | eta_p | 0.1115 | 0.75 | 0.85 | centrada | 0.053 |
| C4 frio 110 C | eta_t | 0.1115 | 0.8 | 0.9 | centrada | 1.054 |
| C4 frio 110 C | x_b | 0.1115 | 0.85 | 0.9 | centrada | 0.717 |
# Sens2 F1 - p6_fronteras_ic: frontera con intervalo y contraste con el barrido

Regresion logistica (respuesta 1 = KALINA) con 9 variables estandarizadas por bloque;
la frontera es el valor de una variable (probabilidad 0.5) con las otras 8 en el centro.
`todas` cuenta NO_CONVERGIO como 0; `sin_nc` quita las filas NO_CONVERGIO.
El intervalo es el percentil 2.5-97.5 de 1 000 remuestreos bootstrap (semilla 20261018)
donde el ajuste converge y el coeficiente conserva su signo. `calidad` es `aceptable` si
la fraccion valida >= 0.80 y el AUC >= 0.80.

## AUC por bloque y variante

| bloque | variante | AUC |
|---|---|---|
| E3 C1 Husavik | todas | 0.8286 |
| E3 C1 Husavik | sin_nc | 0.9739 |
| E3 C2 ancla A* | todas | 0.8287 |
| E3 C2 ancla A* | sin_nc | 0.9389 |
| E14 C3 caliente 150 C | todas | 0.7110 |
| E14 C3 caliente 150 C | sin_nc | 0.9259 |
| E14 C4 frio 110 C | todas | 0.7503 |
| E14 C4 frio 110 C | sin_nc | 0.8739 |

## Fronteras de calidad aceptable (en llano)

x_frontera es el valor de la variable donde la probabilidad de KALINA cruza 0.5; el
intervalo es su rango de bootstrap. `barrido` es la frontera de los barridos de una
variable de P1; `coincide` dice si algun valor del barrido cae dentro del intervalo.

| bloque | variante | variable | x_frontera (IC 2.5-97.5) | barrido | coincide |
|---|---|---|---|---|---|
| E3 C1 Husavik | todas | T_sumidero | 279.8619 [268.4333, 284.9223] | 284.4 | si |
| E3 C1 Husavik | todas | P_alta | 3692.4945 [1976.2757, 5639.9762] | - | - |
| E3 C1 Husavik | todas | P_baja | 618.5557 [267.1051, 872.7135] | 550 | si |
| E3 C1 Husavik | todas | x_b | 0.8463 [0.7558, 0.9559] | 0.525;0.925 | si |
| E3 C1 Husavik | todas | eps_hrvg | 0.9830 [0.2760, 3.1588] | - | - |
| E3 C1 Husavik | todas | eps_cond | 0.9353 [0.8864, 1.0010] | - | - |
| E3 C1 Husavik | sin_nc | T_fuente | 406.6945 [381.1607, 446.2775] | 358.15;440.65 | si |
| E3 C1 Husavik | sin_nc | T_sumidero | 281.8504 [270.6626, 291.6794] | 284.4 | si |
| E3 C1 Husavik | sin_nc | P_baja | 613.2537 [437.5486, 764.5930] | 550 | si |
| E3 C1 Husavik | sin_nc | x_b | 0.8418 [0.7958, 0.8901] | 0.525;0.925 | no |
| E3 C1 Husavik | sin_nc | eta_t | 0.4399 [-2.1313, 1.4025] | - | - |
| E3 C1 Husavik | sin_nc | eps_hrvg | 0.9327 [0.7751, 1.2047] | - | - |
| E3 C1 Husavik | sin_nc | eps_reg | 1.0685 [0.5375, 5.4225] | - | - |
| E3 C1 Husavik | sin_nc | eps_cond | 0.9337 [0.9013, 0.9681] | - | - |
| E3 C2 ancla A* | todas | T_fuente | 440.6102 [366.0128, 513.5457] | 390.65;468.15 | si |
| E3 C2 ancla A* | todas | T_sumidero | 311.8027 [296.3761, 373.6747] | - | - |
| E3 C2 ancla A* | todas | P_alta | 5373.6498 [1776.6133, 42890.2538] | 3875 | si |
| E3 C2 ancla A* | todas | P_baja | 366.6588 [-41.7976, 648.0520] | 350 | si |
| E3 C2 ancla A* | todas | x_b | 0.5741 [0.4601, 0.7216] | 0.425;0.575 | si |
| E3 C2 ancla A* | todas | eps_reg | 0.3766 [-2.5420, 0.9788] | - | - |
| E3 C2 ancla A* | todas | eps_cond | 0.8895 [0.8145, 0.9804] | 0.775 | no |
| E3 C2 ancla A* | sin_nc | T_fuente | 447.2305 [426.3772, 464.5952] | 390.65;468.15 | no |
| E3 C2 ancla A* | sin_nc | T_sumidero | 327.9014 [309.2704, 383.4266] | - | - |
| E3 C2 ancla A* | sin_nc | P_alta | -2454.9583 [-54177.7649, 938.2603] | 3875 | no |
| E3 C2 ancla A* | sin_nc | P_baja | 122.7932 [-154.8116, 374.5443] | 350 | si |
| E3 C2 ancla A* | sin_nc | x_b | 0.6098 [0.5529, 0.6664] | 0.425;0.575 | si |
| E3 C2 ancla A* | sin_nc | eta_t | 2.7674 [1.2052, 18.8782] | - | - |
| E3 C2 ancla A* | sin_nc | eps_hrvg | 1.5893 [1.0841, 4.3880] | - | - |
| E3 C2 ancla A* | sin_nc | eps_reg | -1.2278 [-17.2926, 0.3376] | - | - |
| E3 C2 ancla A* | sin_nc | eps_cond | 0.8263 [0.7801, 0.8894] | 0.775 | no |
| E14 C3 caliente 150 C | sin_nc | T_fuente | 482.0804 [446.3627, 573.5044] | 358.15;568.15 | si |
| E14 C3 caliente 150 C | sin_nc | T_sumidero | 291.6109 [285.1142, 302.2072] | 296.9 | si |
| E14 C3 caliente 150 C | sin_nc | P_alta | 394.8348 [-8437.1887, 2421.3265] | - | - |
| E14 C3 caliente 150 C | sin_nc | P_baja | 635.0518 [392.6630, 852.4219] | 550 | si |
| E14 C3 caliente 150 C | sin_nc | x_b | 0.9043 [0.8014, 1.0562] | 0.375 | no |
| E14 C3 caliente 150 C | sin_nc | eps_hrvg | 1.2170 [0.9382, 2.1429] | - | - |
| E14 C3 caliente 150 C | sin_nc | eps_cond | 0.8865 [0.8230, 0.9260] | 0.875 | si |
| E14 C4 frio 110 C | sin_nc | T_fuente | 462.3587 [412.5671, 784.4809] | 358.15;528.15 | si |
| E14 C4 frio 110 C | sin_nc | T_sumidero | 291.3349 [285.5607, 301.6351] | 291.9 | si |
| E14 C4 frio 110 C | sin_nc | P_baja | 454.5397 [-343.1609, 776.1236] | 750 | si |
| E14 C4 frio 110 C | sin_nc | x_b | 1.1286 [0.9442, 2.0414] | 0.625 | no |
| E14 C4 frio 110 C | sin_nc | eps_hrvg | 1.8258 [1.0217, 12.4582] | - | - |
| E14 C4 frio 110 C | sin_nc | eps_cond | 0.8848 [0.8271, 0.9197] | - | - |

# REPORTE — `TeqpVerificado` sobre los 22 puntos KALINA (TASK 2026-09-27-teqp-verificado)

Generado por `scripts/regresion_teqp_verificado.py` el 2026-09-27 02:20:48. Datos: `resultados/2026-09-27_teqp_verificado/regresion_22.csv` (22 puntos) y `regresion_recurrencias.csv` (1 llamadas respaldadas).

## Qué se comparó

Cada punto KALINA del barrido `2026-09-24_margen2k` se resolvió en SU `P_baja` con `TeqpAdapter` y con `TeqpVerificado` (T_sumidero=283.0 K, T_amb_diseno=283.15 K, η_t=η_p=0.8, ε=(0.85, 0.8, 0.85), ṁ_b=1.0 kg/s) y se clasificó con `evaluar_ciclo` sobre el MISMO adapter que resolvió el ciclo.

## Resumen

| Magnitud | Valor |
|---|---|
| Puntos | 22 |
| Puntos con error | 0 |
| Puntos donde η cambia | 1 de 22 |
| Puntos donde cambia la clasificación | 0 |
| Recurrencias totales al motor real | 1 |
| Recurrencias con `fallo=True` | 0 |
| Puntos con `verificacion_incompleta` | 0 |
| Tiempo medio `TeqpAdapter` | 30.27 s/punto |
| Tiempo medio `TeqpVerificado` | 30.34 s/punto |
| **Sobrecosto** | **+0.23 %** |
| Tiempo total en motor real | 3.7 s |

## Diferencias por punto

| # | x_b | P_alta | T_fuente | P_baja | η teqp | η verif | Δη | clas teqp | clas verif | rec | t_real [s] | incompleta | t teqp [s] | t verif [s] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KALINA-01 | 0.6 | 3000 | 394 | 523.750 | 0.103715729 | 0.103715729 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 34.4 | 33.4 |
| KALINA-02 | 0.6 | 4000 | 394 | 424.170 | 0.080412106 | 0.08041229 | 1.84e-07 | KALINA | KALINA | 1 | 3.67 | False | 40.06 | 41.17 |
| KALINA-03 | 0.6 | 3000 | 423 | 752.472 | 0.096152424 | 0.096152424 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 27.32 | 27.13 |
| KALINA-04 | 0.6 | 4000 | 423 | 625.242 | 0.116752144 | 0.116752144 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 29.47 | 29.54 |
| KALINA-05 | 0.6 | 5000 | 423 | 535.443 | 0.120151383 | 0.120151383 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 31.07 | 31.2 |
| KALINA-06 | 0.65 | 3000 | 394 | 687.980 | 0.098608559 | 0.098608559 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 28.32 | 28.98 |
| KALINA-07 | 0.65 | 4000 | 394 | 568.015 | 0.103672926 | 0.103672926 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 35.51 | 35.73 |
| KALINA-08 | 0.65 | 5000 | 394 | 451.969 | 0.009114415 | 0.009114415 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 43.71 | 43.26 |
| KALINA-09 | 0.65 | 3000 | 423 | 967.999 | 0.08422344 | 0.08422344 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 26.6 | 26.62 |
| KALINA-10 | 0.65 | 4000 | 423 | 812.575 | 0.109810156 | 0.109810156 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 27.98 | 28.22 |
| KALINA-11 | 0.65 | 5000 | 423 | 704.645 | 0.121500395 | 0.121500395 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 30.81 | 31.41 |
| KALINA-12 | 0.7 | 3000 | 394 | 868.093 | 0.09055203 | 0.09055203 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 27.9 | 28.19 |
| KALINA-13 | 0.7 | 4000 | 394 | 731.746 | 0.106948892 | 0.106948892 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 25.45 | 25.46 |
| KALINA-14 | 0.7 | 5000 | 394 | 600.662 | 0.091447933 | 0.091447933 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 39.63 | 39.39 |
| KALINA-15 | 0.7 | 4000 | 423 | 1016.276 | 0.101529576 | 0.101529576 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 27.32 | 27.57 |
| KALINA-16 | 0.7 | 5000 | 423 | 890.811 | 0.118001733 | 0.118001733 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 24.5 | 24.63 |
| KALINA-17 | 0.75 | 3000 | 394 | 1060.025 | 0.081356002 | 0.081356002 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 28.27 | 28.01 |
| KALINA-18 | 0.75 | 4000 | 394 | 910.074 | 0.103581982 | 0.103581982 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 29.02 | 28.72 |
| KALINA-19 | 0.75 | 5000 | 394 | 767.936 | 0.108586549 | 0.108586549 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 30.04 | 30.43 |
| KALINA-20 | 0.75 | 5000 | 423 | 1089.671 | 0.112369281 | 0.112369281 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 23.66 | 23.69 |
| KALINA-21 | 0.8 | 4000 | 394 | 1101.511 | 0.097347953 | 0.097347953 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 24.68 | 24.8 |
| KALINA-22 | 0.8 | 5000 | 394 | 952.893 | 0.110590562 | 0.110590562 | 0.0 | KALINA | KALINA | 0 | 0.0 | False | 30.32 | 30.0 |

### Puntos con Δη ≠ 0

- **KALINA-02** (x_b=0.6, P_baja=424.170 kPa): η 0.080412106 -> 0.08041229 (Δ=+0.000000184), 1 recurrencia(s), clasificación KALINA -> KALINA.

### Cambios de clasificación

Ninguno.

### Recurrencias al motor real

| # | método | P [kPa] | x | x_molar | T_teqp [K] | Ta [K] | Tw [K] | criterio | origen | valor_teqp | valor_real | t_real [s] | fallo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KALINA-02 | `h(P,s,x)` | 424.169832 | 0.974976 | 0.976311 | 272.8322 | 272.8322 | 418.8853 | rico_NH3 | T_invertida | 1625.694045 | 1486.768121 | 3.6665 | False |

## Lectura

- **Costo**: +0.23 % de media por punto (30.27 -> 30.34 s; mediana del ratio por punto +0.33 %). El ruido de reloj entre corridas es de ±1-2 s por punto (~5 %), o sea que esta media está DENTRO del ruido. Lo sistemático es el coste de detección (0.475 ms por inversión, medido en `scripts/costo_soluciones_teqp.py`) y el resto son los 3.7 s de motor real. El +2.8 % del prototipo NO es comparable: allí se contrastó la media de 3 puntos NORMALES contra la media de los 22 (líneas base distintas).
- **Coherencia**: `TeqpVerificado` no cambia ningún resultado fuera de la zona de riesgo: en los puntos sin recurrencia la salida es bit a bit la de `TeqpAdapter`. La única diferencia posible es la corrección de la raíz falsa (y su efecto en las iteraciones de la búsqueda de Brent).
- `verificacion_incompleta=False` en los 22 puntos: el motor real cubrió todas las recurrencias que hubo.
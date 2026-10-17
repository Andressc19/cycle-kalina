# Sens2 P2 - Paso 4: robustez del optimo

Distancia L1 normalizada de cada KALINA (total) con eta valida a la frontera
no-KALINA mas cercana del mismo centro.

## Top 10 % de eta frente al resto (distancia a la frontera)

| centro | n Top10 | n resto | mediana Top10 | mediana resto | KS | p |
|---|---|---|---|---|---|---|
| todos | 207 | 1840 | 0.1383 | 0.3684 | 0.357 | 9.965e-22 |
| C1 Husavik | 46 | 408 | 0.1133 | 0.3636 | 0.474 | 5.321e-09 |
| C2 ancla A* | 41 | 368 | 0.1957 | 0.3664 | 0.189 | 0.1234 |
| C3 caliente 150 C | 41 | 368 | 0.1564 | 0.4273 | 0.509 | 2.663e-09 |
| C4 frio 110 C | 39 | 344 | 0.1561 | 0.4545 | 0.411 | 7.439e-06 |
| Sin centro (muestreo o malla) | 40 | 352 | 0.1053 | 0.3421 | 0.531 | 6.376e-10 |

## Respuesta: zona segura o cerca de la frontera
La mediana de la distancia a la frontera del 10 % de mayor eta es 0.1383 y la del resto es 0.3684. Por tanto el optimo esta MAS CERCA de la frontera que el resto.

## Top-10 de eta por centro

| centro | lugar | id | eta | dist frontera | rango | atipico |
|---|---|---|---|---|---|---|
| todos | 1 | N1-T170-14 | 14.82 | 0.2719 | fuera del rango experimental | no |
| todos | 2 | N10-C3-0016 | 14.53 | 0.07895 | dentro del rango experimental | no |
| todos | 3 | N7B-C3-B3-036 | 14.38 | 0.07895 | dentro del rango experimental | no |
| todos | 4 | N7B-C3-B3-029 | 14.06 | 0.07895 | dentro del rango experimental | no |
| todos | 5 | C1-B3-0127 | 14.01 | 0.05263 | dentro del rango experimental | no |
| todos | 6 | C1-B5-0228 | 13.95 | 0.6364 | dentro del rango experimental | no |
| todos | 7 | C1-B3-0120 | 13.92 | 0.05263 | dentro del rango experimental | no |
| todos | 8 | C1-B5-0221 | 13.85 | 0.5455 | dentro del rango experimental | no |
| todos | 9 | N10-C1-0002 | 13.73 | 0.05263 | dentro del rango experimental | no |
| todos | 10 | C1-LHS-0186 | 13.67 | 0.6749 | dentro del rango experimental | no |
| C1 Husavik | 1 | C1-B3-0127 | 14.01 | 0.05263 | dentro del rango experimental | no |
| C1 Husavik | 2 | C1-B5-0228 | 13.95 | 0.6364 | dentro del rango experimental | no |
| C1 Husavik | 3 | C1-B3-0120 | 13.92 | 0.05263 | dentro del rango experimental | no |
| C1 Husavik | 4 | C1-B5-0221 | 13.85 | 0.5455 | dentro del rango experimental | no |
| C1 Husavik | 5 | N10-C1-0002 | 13.73 | 0.05263 | dentro del rango experimental | no |
| C1 Husavik | 6 | C1-LHS-0186 | 13.67 | 0.6749 | dentro del rango experimental | no |
| C1 Husavik | 7 | C1-B5-0214 | 13.59 | 0.3636 | dentro del rango experimental | no |
| C1 Husavik | 8 | C1-B3-0113 | 13.56 | 0.05263 | dentro del rango experimental | no |
| C1 Husavik | 9 | C1-eta_t-0092 | 13.46 | 0.2727 | dentro del rango experimental | no |
| C1 Husavik | 10 | C1-B2-0052 | 13.35 | 0.1077 | dentro del rango experimental | no |
| C2 ancla A* | 1 | C2-LHS-0124 | 13.12 | 0.8755 | fuera del rango experimental | no |
| C2 ancla A* | 2 | C2-LHS-0186 | 12.76 | 0.7814 | fuera del rango experimental | no |
| C2 ancla A* | 3 | C2-LHS-0005 | 12.37 | 0.8843 | dentro del rango experimental | no |
| C2 ancla A* | 4 | C2-LHS-0067 | 12.21 | 0.7611 | dentro del rango experimental | no |
| C2 ancla A* | 5 | C2-B5-0228 | 12.02 | 0.61 | dentro del rango experimental | no |
| C2 ancla A* | 6 | C2-B1-0029 | 11.76 | 0.02632 | fuera del rango experimental | no |
| C2 ancla A* | 7 | C2-B1-0037 | 11.68 | 0.02632 | fuera del rango experimental | no |
| C2 ancla A* | 8 | C2-B5-0227 | 11.31 | 0.5191 | dentro del rango experimental | no |
| C2 ancla A* | 9 | C2-T_fuente-0020 | 11.24 | 0.03349 | fuera del rango experimental | no |
| C2 ancla A* | 10 | C2-B6-0256 | 11.22 | 0.1244 | fuera del rango experimental | no |
| C3 caliente 150 C | 1 | N10-C3-0016 | 14.53 | 0.07895 | dentro del rango experimental | no |
| C3 caliente 150 C | 2 | N7B-C3-B3-036 | 14.38 | 0.07895 | dentro del rango experimental | no |
| C3 caliente 150 C | 3 | N7B-C3-B3-029 | 14.06 | 0.07895 | dentro del rango experimental | no |
| C3 caliente 150 C | 4 | N7B-C3-B3-022 | 13.56 | 0.07895 | dentro del rango experimental | no |
| C3 caliente 150 C | 5 | N10-C3-0017 | 13.27 | 0.1579 | dentro del rango experimental | no |
| C3 caliente 150 C | 6 | N7B-C3-B2-003 | 13.26 | 0.1077 | dentro del rango experimental | no |
| C3 caliente 150 C | 7 | N7B-C3-B3-037 | 13.03 | 0.1579 | dentro del rango experimental | no |
| C3 caliente 150 C | 8 | N7B-C3-B3-015 | 12.86 | 0.07895 | dentro del rango experimental | no |
| C3 caliente 150 C | 9 | N7A-C3-P_baja-005 | 12.8 | 0.05263 | dentro del rango experimental | no |
| C3 caliente 150 C | 10 | N10-C3-0024 | 12.73 | 0.07895 | dentro del rango experimental | no |
| C4 frio 110 C | 1 | N7B-C4-B1-045 | 13.23 | 0.06522 | dentro del rango experimental | no |
| C4 frio 110 C | 2 | N9-C4-B5-0048 | 12.98 | 0.6364 | dentro del rango experimental | no |
| C4 frio 110 C | 3 | N7B-C4-B2-010 | 12.91 | 0.07692 | dentro del rango experimental | no |
| C4 frio 110 C | 4 | N9-C4-B5-0041 | 12.87 | 0.5455 | dentro del rango experimental | no |
| C4 frio 110 C | 5 | N9-C4-B5-0034 | 12.64 | 0.3636 | dentro del rango experimental | no |
| C4 frio 110 C | 6 | N7B-C4-B3-031 | 12.61 | 0.05571 | dentro del rango experimental | no |
| C4 frio 110 C | 7 | N7A-C4-eta_t-011 | 12.54 | 0.2727 | dentro del rango experimental | no |
| C4 frio 110 C | 8 | N7B-C4-B3-024 | 12.46 | 0.07895 | dentro del rango experimental | no |
| C4 frio 110 C | 9 | N9-C4-B5-0021 | 12.43 | 0.3636 | dentro del rango experimental | no |
| C4 frio 110 C | 10 | N7B-C4-B1-031 | 12.41 | 0.06522 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 1 | N1-T170-14 | 14.82 | 0.2719 | fuera del rango experimental | no |
| Sin centro (muestreo o malla) | 2 | N1-T150-01 | 13.6 | 0.3118 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 3 | N5-T150-S05-03 | 13.14 | 0.05263 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 4 | N5-T130-S05-03 | 12.68 | 0.05263 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 5 | N1-T190-01 | 12.68 | 0.2685 | fuera del rango experimental | no |
| Sin centro (muestreo o malla) | 6 | N5-T150-S10-04 | 12.09 | 0.05263 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 7 | N5-T170-S05-04 | 11.93 | 0.05263 | fuera del rango experimental | no |
| Sin centro (muestreo o malla) | 8 | N5-T150-S05-04 | 11.91 | 0.1053 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 9 | N5-T110-S10-03 | 11.9 | 0.05263 | dentro del rango experimental | no |
| Sin centro (muestreo o malla) | 10 | N5-T200-S05-04 | 11.84 | 0.05263 | fuera del rango experimental | no |

Del 10 % de mayor eta a una sola variable de la frontera: P_baja 73, T_fuente 31, x_b 9, P_alta 6, eps_hrvg 2.

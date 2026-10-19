# Sens2 etapa B - eta maxima frente a T_fuente con busqueda local

Busqueda coordenada a coordenada de P_alta, P_baja y x_b por banda; solo cuentan los puntos KALINA. Es un maximo local con tope de evaluaciones, no un optimo global. Comparacion orientativa: eta maxima del conjunto muestreado (todos los KALINA) en la ventana [T-10, T+10) K, con y sin los puntos fuera del rango experimental (liquido > 420 K); el muestreo mezcla eta_t hasta 0.95 y otras T_sumidero, mientras la busqueda fija eta_t = 0.85 y T_sumidero = 280.5 K, asi que la mejora no es una comparacion a igual configuracion.

| T_fuente (C) | evaluaciones | KALINA | eta max (%) | P_alta | P_baja | x_b | fuera de rango | eta max dentro del rango (%) | eta max muestreo (%) | mejora (pp) | eta max muestreo dentro del rango (%) | mejora dentro del rango (pp) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 31 | 19 | 11.02 | 2850 | 675 | 0.917 | no | 11.02 | 7.01 | +4.01 | 7.01 | +4.01 |
| 100 | 29 | 19 | 13.05 | 4030 | 710 | 0.925 | no | 13.05 | 12.09 | +0.95 | 12.09 | +0.95 |
| 120 | 22 | 12 | 14.39 | 4850 | 600 | 0.835 | no | 14.39 | 14.01 | +0.38 | 14.01 | +0.38 |
| 140 | 31 | 22 | 15.27 | 5250 | 550 | 0.772 | no | 15.27 | 13.29 | +1.98 | 13.29 | +1.98 |
| 160 | 29 | 17 | 16.77 | 6500 | 610 | 0.805 | si | 16.73 | 14.53 | +2.23 | 14.53 | +2.20 |
| 180 | 21 | 11 | 15.29 | 4850 | 610 | 0.738 | si | - | 14.82 | +0.46 | 12.32 | - |
| 200 | 30 | 17 | 13.95 | 4350 | 640 | 0.708 | si | - | 12.68 | +1.26 | 12.32 | - |
| 220 | 32 | 19 | 16.67 | 6280 | 810 | 0.910 | si | - | 12.31 | +4.37 | 3.69 | - |
| 240 | 31 | 17 | 15.90 | 6280 | 910 | 0.910 | si | - | 12.29 | +3.61 | - | - |
| 260 | 30 | 17 | 15.45 | 5700 | 850 | 0.880 | si | - | 12.27 | +3.18 | - | - |
| 280 | 31 | 19 | 14.10 | 5530 | 920 | 0.828 | si | - | 9.30 | +4.80 | - | - |
| 300 | 30 | 16 | 13.44 | 5100 | 850 | 0.760 | si | - | 10.93 | +2.51 | - | - |

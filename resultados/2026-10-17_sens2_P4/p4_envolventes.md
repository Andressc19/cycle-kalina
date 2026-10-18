# Sens2 P4 - Paso 1: envolventes y lo que debe cubrir cada equipo

Todos los numeros salen del dataset P2 unido a los estados del motor.
m_b = 1 salvo el estudio 0 (m_b != 1); toda cantidad extensiva va dividida
entre m_b (por kg/s de m_b). Presiones en kPa, temperaturas en K, h en
kJ/kg, potencia en kW.

## n por centro y conjunto

| centro | KALINA (total) | KALINA dentro del rango | 10 % de KALINA (total) con mayor eta |
|---|---|---|---|
| C1 Husavik | 454 | 444 | 45 |
| C2 ancla A* | 409 | 339 | 41 |
| C3 caliente 150 C | 409 | 351 | 41 |
| C4 frio 110 C | 383 | 377 | 38 |
| Sin centro (muestreo o malla) | 392 | 230 | 39 |

## Lo que debe cubrir cada equipo (P5-P95)

P5 y P95 del conjunto KALINA (total) y del 10 % de KALINA (total) con mayor
eta, sobre todos los centros juntos. n = puntos con la cantidad disponible.

| equipo | cantidad | n total | P5 total | P50 total | P95 total | n top10 | P5 top10 | P50 top10 | P95 top10 |
|---|---|---|---|---|---|---|---|---|---|
| Turbina | rp | 2047 | 1.6977 | 3.4742 | 5.5077 | 205 | 4.2637 | 4.7826 | 7.2529 |
| Turbina | dh_turb | 2047 | 65.2511 | 152.7177 | 230.4314 | 205 | 171.7307 | 198.3703 | 248.7237 |
| Turbina | Wt_mb | 2047 | 10.7218 | 62.0713 | 145.9309 | 205 | 83.0166 | 115.5268 | 184.3794 |
| Turbina | q4 | 2047 | 0.9231 | 0.9499 | 0.9802 | 205 | 0.9101 | 0.9355 | 0.9498 |
| Turbina | T3 | 2047 | 361.2295 | 392.5320 | 443.1864 | 205 | 371.9788 | 383.2675 | 425.1792 |
| Turbina | T4 | 2047 | 296.0257 | 335.2131 | 405.1350 | 205 | 291.8945 | 303.9066 | 361.0667 |
| Turbina | m_v_mb | 2047 | 0.0835 | 0.4810 | 0.8867 | 205 | 0.3458 | 0.6148 | 0.8893 |
| Regenerador | dT_A | 2047 | 24.6203 | 56.7453 | 126.4107 | 205 | 47.9147 | 65.1463 | 114.2425 |
| Regenerador | dT_B | 2047 | 9.6515 | 24.9956 | 46.6955 | 205 | 6.7135 | 24.8903 | 37.4651 |
| Regenerador | pinch_reg | 2047 | 9.6515 | 24.9956 | 46.6955 | 205 | 6.7135 | 24.8903 | 37.4651 |
| Regenerador | LMTD_reg | 2047 | 18.6734 | 37.7375 | 73.6398 | 205 | 23.5575 | 41.1761 | 66.7202 |
| Regenerador | UA_reg | 2047 | 0.7591 | 4.2872 | 13.3256 | 205 | 0.7600 | 3.1438 | 7.5659 |
| Regenerador | qreg_qi | 2047 | 0.0313 | 0.2102 | 1.3054 | 205 | 0.0302 | 0.1401 | 0.4186 |
| Condensador | Qout_mb | 2047 | 217.9849 | 721.1982 | 1561.3302 | 205 | 541.7500 | 803.9891 | 1274.9014 |
| Condensador | aprox_cond_sal | 2047 | 2.6142 | 9.1594 | 23.4084 | 205 | 6.2563 | 9.0977 | 15.2402 |
| Condensador | aprox_cond_ent | 2047 | 20.7348 | 44.8757 | 115.4193 | 205 | 20.7476 | 33.1813 | 76.3839 |
| HRVG | Qi_mb | 2047 | 228.7833 | 789.5061 | 1695.2760 | 205 | 625.7454 | 916.7756 | 1449.8363 |
| HRVG | aprox_fuente | 2047 | 2.1100 | 11.3439 | 43.9802 | 205 | 6.0472 | 13.6327 | 41.1528 |
| Bomba | Wp_mb | 2047 | 1.4181 | 3.9604 | 6.1743 | 205 | 4.1269 | 5.2917 | 7.5967 |
| Bomba | Wp_Wt | 2047 | 0.0238 | 0.0600 | 0.3014 | 205 | 0.0272 | 0.0423 | 0.0781 |
| Bomba | P_alta | 2047 | 1940.0000 | 3150.0000 | 4500.0000 | 205 | 3000.0000 | 3300.0000 | 5000.0000 |
| Bomba | P_baja | 2047 | 563.6400 | 910.0000 | 1600.0000 | 205 | 500.0000 | 690.0000 | 910.0000 |

## Detalle por centro (KALINA total: P5 / P50 / P95)

| centro | cantidad | n | P5 | P50 | P95 |
|---|---|---|---|---|---|
| C1 Husavik | rp | 454 | 2.1103 | 4.5513 | 5.6353 |
| C1 Husavik | dh_turb | 454 | 79.0669 | 154.6492 | 213.3187 |
| C1 Husavik | Wt_mb | 454 | 16.2706 | 74.7763 | 132.4752 |
| C1 Husavik | q4 | 454 | 0.9248 | 0.9533 | 0.9806 |
| C1 Husavik | T3 | 454 | 359.0452 | 380.1551 | 408.2892 |
| C1 Husavik | T4 | 454 | 289.6733 | 314.8124 | 362.2720 |
| C1 Husavik | m_v_mb | 454 | 0.1503 | 0.5345 | 0.7760 |
| C1 Husavik | dT_A | 454 | 29.9918 | 59.0223 | 84.5028 |
| C1 Husavik | dT_B | 454 | 9.6210 | 23.8653 | 46.0599 |
| C1 Husavik | pinch_reg | 454 | 9.6210 | 23.8653 | 46.0599 |
| C1 Husavik | LMTD_reg | 454 | 20.4511 | 39.7271 | 59.0338 |
| C1 Husavik | UA_reg | 454 | 1.4110 | 3.6689 | 11.9506 |
| C1 Husavik | qreg_qi | 454 | 0.0625 | 0.1746 | 0.9186 |
| C1 Husavik | Qout_mb | 454 | 290.9264 | 748.0112 | 1074.9065 |
| C1 Husavik | aprox_cond_sal | 454 | 4.4751 | 9.1555 | 21.0897 |
| C1 Husavik | aprox_cond_ent | 454 | 19.6630 | 37.3923 | 74.6366 |
| C1 Husavik | Qi_mb | 454 | 314.9179 | 821.3303 | 1195.8611 |
| C1 Husavik | aprox_fuente | 454 | 3.1933 | 13.9258 | 36.5534 |
| C1 Husavik | Wp_mb | 454 | 1.8087 | 4.6316 | 6.5468 |
| C1 Husavik | Wp_Wt | 454 | 0.0268 | 0.0549 | 0.2086 |
| C1 Husavik | P_alta | 454 | 2000.0000 | 3300.0000 | 4453.5000 |
| C1 Husavik | P_baja | 454 | 600.0000 | 690.0000 | 1300.0000 |
| C1 Husavik | eta_pct | 454 | 3.5436 | 8.8952 | 12.8246 |
| C1 Husavik | wnet_mb | 454 | 13.8310 | 70.4451 | 128.0050 |
| C2 ancla A* | rp | 409 | 2.3064 | 5.3225 | 6.6613 |
| C2 ancla A* | dh_turb | 409 | 97.6408 | 194.4030 | 248.1542 |
| C2 ancla A* | Wt_mb | 409 | 7.9109 | 29.5739 | 87.7753 |
| C2 ancla A* | q4 | 409 | 0.9220 | 0.9400 | 0.9727 |
| C2 ancla A* | T3 | 409 | 389.8732 | 399.3378 | 436.4768 |
| C2 ancla A* | T4 | 409 | 318.5571 | 340.3658 | 388.5322 |
| C2 ancla A* | m_v_mb | 409 | 0.0464 | 0.1374 | 0.4546 |
| C2 ancla A* | dT_A | 409 | 22.3449 | 37.1793 | 76.6257 |
| C2 ancla A* | dT_B | 409 | 9.5336 | 25.2723 | 51.4151 |
| C2 ancla A* | pinch_reg | 409 | 9.5336 | 25.2723 | 50.9442 |
| C2 ancla A* | LMTD_reg | 409 | 15.3978 | 30.5446 | 58.1082 |
| C2 ancla A* | UA_reg | 409 | 2.9639 | 9.5829 | 21.8430 |
| C2 ancla A* | qreg_qi | 409 | 0.2075 | 0.8074 | 1.6754 |
| C2 ancla A* | Qout_mb | 409 | 185.6054 | 325.5307 | 872.7732 |
| C2 ancla A* | aprox_cond_sal | 409 | 2.1545 | 5.1341 | 30.5070 |
| C2 ancla A* | aprox_cond_ent | 409 | 20.8978 | 37.7411 | 86.6925 |
| C2 ancla A* | Qi_mb | 409 | 194.9913 | 347.4061 | 954.3366 |
| C2 ancla A* | aprox_fuente | 409 | 2.1100 | 5.1502 | 23.5952 |
| C2 ancla A* | Wp_mb | 409 | 2.0930 | 3.9674 | 4.9286 |
| C2 ancla A* | Wp_Wt | 409 | 0.0391 | 0.1342 | 0.5008 |
| C2 ancla A* | P_alta | 409 | 2074.0000 | 3000.0000 | 3708.0000 |
| C2 ancla A* | P_baja | 409 | 460.0000 | 563.6400 | 1186.0000 |
| C2 ancla A* | eta_pct | 409 | 1.8481 | 6.6752 | 10.8287 |
| C2 ancla A* | wnet_mb | 409 | 3.9557 | 25.5546 | 83.9681 |
| C3 caliente 150 C | rp | 409 | 1.6170 | 3.3158 | 5.3846 |
| C3 caliente 150 C | dh_turb | 409 | 59.8868 | 150.5678 | 218.5837 |
| C3 caliente 150 C | Wt_mb | 409 | 13.5488 | 85.0705 | 156.2274 |
| C3 caliente 150 C | q4 | 409 | 0.9238 | 0.9487 | 0.9797 |
| C3 caliente 150 C | T3 | 409 | 366.3258 | 409.2664 | 439.1094 |
| C3 caliente 150 C | T4 | 409 | 308.9246 | 359.9675 | 396.5976 |
| C3 caliente 150 C | m_v_mb | 409 | 0.1429 | 0.6149 | 0.8926 |
| C3 caliente 150 C | dT_A | 409 | 29.3421 | 80.3111 | 126.7395 |
| C3 caliente 150 C | dT_B | 409 | 9.3336 | 30.4516 | 48.2446 |
| C3 caliente 150 C | pinch_reg | 409 | 9.3336 | 30.4516 | 48.2446 |
| C3 caliente 150 C | LMTD_reg | 409 | 21.5138 | 50.0748 | 76.5661 |
| C3 caliente 150 C | UA_reg | 409 | 0.7097 | 3.1478 | 12.3822 |
| C3 caliente 150 C | qreg_qi | 409 | 0.0276 | 0.1477 | 0.8152 |
| C3 caliente 150 C | Qout_mb | 409 | 327.7062 | 950.7467 | 1515.6137 |
| C3 caliente 150 C | aprox_cond_sal | 409 | 5.3201 | 11.4852 | 23.2230 |
| C3 caliente 150 C | aprox_cond_ent | 409 | 31.6273 | 70.9963 | 111.2036 |
| C3 caliente 150 C | Qi_mb | 409 | 344.7668 | 1027.5356 | 1628.9378 |
| C3 caliente 150 C | aprox_fuente | 409 | 4.4426 | 13.7955 | 45.8568 |
| C3 caliente 150 C | Wp_mb | 409 | 1.4288 | 3.7875 | 6.6937 |
| C3 caliente 150 C | Wp_Wt | 409 | 0.0230 | 0.0443 | 0.2254 |
| C3 caliente 150 C | P_alta | 409 | 2034.0000 | 3150.0000 | 4916.0000 |
| C3 caliente 150 C | P_baja | 409 | 650.0000 | 950.0000 | 1600.0000 |
| C3 caliente 150 C | eta_pct | 409 | 2.8159 | 8.3657 | 11.7370 |
| C3 caliente 150 C | wnet_mb | 409 | 10.7758 | 80.3367 | 152.3826 |
| C4 frio 110 C | rp | 383 | 1.5813 | 4.0000 | 4.8500 |
| C4 frio 110 C | dh_turb | 383 | 48.6613 | 135.8692 | 195.1671 |
| C4 frio 110 C | Wt_mb | 383 | 12.0480 | 70.6667 | 133.4302 |
| C4 frio 110 C | q4 | 383 | 0.9178 | 0.9490 | 0.9857 |
| C4 frio 110 C | T3 | 383 | 358.6661 | 372.0958 | 405.6734 |
| C4 frio 110 C | T4 | 383 | 296.1355 | 310.0596 | 363.4619 |
| C4 frio 110 C | m_v_mb | 383 | 0.1124 | 0.6102 | 0.8461 |
| C4 frio 110 C | dT_A | 383 | 26.6706 | 55.0243 | 91.1490 |
| C4 frio 110 C | dT_B | 383 | 8.2791 | 20.7389 | 40.3953 |
| C4 frio 110 C | pinch_reg | 383 | 8.2791 | 20.7389 | 40.3953 |
| C4 frio 110 C | LMTD_reg | 383 | 17.6311 | 35.2092 | 57.0188 |
| C4 frio 110 C | UA_reg | 383 | 1.0417 | 3.5027 | 12.4755 |
| C4 frio 110 C | qreg_qi | 383 | 0.0371 | 0.1473 | 0.9466 |
| C4 frio 110 C | Qout_mb | 383 | 258.4257 | 753.0757 | 1139.2231 |
| C4 frio 110 C | aprox_cond_sal | 383 | 3.9851 | 8.7774 | 20.2029 |
| C4 frio 110 C | aprox_cond_ent | 383 | 19.5038 | 32.2793 | 74.2987 |
| C4 frio 110 C | Qi_mb | 383 | 271.1028 | 841.4297 | 1269.6454 |
| C4 frio 110 C | aprox_fuente | 383 | 1.9430 | 11.1696 | 37.1771 |
| C4 frio 110 C | Wp_mb | 383 | 1.3338 | 5.3942 | 6.6085 |
| C4 frio 110 C | Wp_Wt | 383 | 0.0315 | 0.0663 | 0.2764 |
| C4 frio 110 C | P_alta | 383 | 2054.0000 | 3880.0000 | 4600.0000 |
| C4 frio 110 C | P_baja | 383 | 800.0000 | 910.0000 | 1639.0000 |
| C4 frio 110 C | eta_pct | 383 | 2.5060 | 8.3660 | 12.2884 |
| C4 frio 110 C | wnet_mb | 383 | 8.9928 | 65.8734 | 127.7125 |
| Sin centro (muestreo o malla) | rp | 392 | 1.5483 | 2.7778 | 5.0000 |
| Sin centro (muestreo o malla) | dh_turb | 392 | 63.7142 | 137.4656 | 217.0451 |
| Sin centro (muestreo o malla) | Wt_mb | 392 | 9.5268 | 66.7913 | 165.1501 |
| Sin centro (muestreo o malla) | q4 | 392 | 0.9252 | 0.9544 | 0.9795 |
| Sin centro (muestreo o malla) | T3 | 392 | 361.5066 | 410.6274 | 476.9462 |
| Sin centro (muestreo o malla) | T4 | 392 | 295.8978 | 362.3332 | 437.4982 |
| Sin centro (muestreo o malla) | m_v_mb | 392 | 0.1028 | 0.5361 | 0.9484 |
| Sin centro (muestreo o malla) | dT_A | 392 | 21.5909 | 68.6233 | 153.5665 |
| Sin centro (muestreo o malla) | dT_B | 392 | 15.6450 | 28.4427 | 44.4478 |
| Sin centro (muestreo o malla) | pinch_reg | 392 | 15.6450 | 28.4427 | 44.4478 |
| Sin centro (muestreo o malla) | LMTD_reg | 392 | 19.1573 | 45.8174 | 85.8001 |
| Sin centro (muestreo o malla) | UA_reg | 392 | 0.3291 | 3.8202 | 11.2308 |
| Sin centro (muestreo o malla) | qreg_qi | 392 | 0.0128 | 0.1696 | 1.0836 |
| Sin centro (muestreo o malla) | Qout_mb | 392 | 210.9882 | 904.5290 | 1957.5669 |
| Sin centro (muestreo o malla) | aprox_cond_sal | 392 | 2.3403 | 10.1076 | 22.7653 |
| Sin centro (muestreo o malla) | aprox_cond_ent | 392 | 20.0155 | 64.3407 | 147.9232 |
| Sin centro (muestreo o malla) | Qi_mb | 392 | 222.2336 | 960.0409 | 2101.8501 |
| Sin centro (muestreo o malla) | aprox_fuente | 392 | 1.3792 | 10.8741 | 88.1055 |
| Sin centro (muestreo o malla) | Wp_mb | 392 | 0.9467 | 3.0259 | 5.0847 |
| Sin centro (muestreo o malla) | Wp_Wt | 392 | 0.0182 | 0.0410 | 0.2571 |
| Sin centro (muestreo o malla) | P_alta | 392 | 1465.5000 | 3000.0000 | 4380.0000 |
| Sin centro (muestreo o malla) | P_baja | 392 | 500.0000 | 1000.0000 | 1794.5000 |
| Sin centro (muestreo o malla) | eta_pct | 392 | 2.7407 | 6.6178 | 10.9195 |
| Sin centro (muestreo o malla) | wnet_mb | 392 | 7.4611 | 63.7925 | 162.4561 |

Lectura: P5-P95 es el cuerpo del conjunto (deja fuera el 5 % mas bajo y
el 5 % mas alto); es lo que un equipo preseleccionado debe poder cubrir.
`minimo` y `maximo` quedan en el CSV, no en esta tabla.

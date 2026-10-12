# Tabla 1.1-3 · Comparación antes y después de la F1

**Estudio 1.1** · Repetir el caso del profesor · **Partes:** 1.1b, 1.1a, 1.1c, 1.1d  
**Punto base:** PP = punto del profesor (los 11 datos del enunciado; ver GLOSARIO)  
**Datos fijos: T_fuente = 623.15 K; P_baja = 400 kPa; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8.**  
**Datos barridos: T_sumidero [297.95–303.55] K (23 valores); P_alta [2000–4000] kPa (9 valores); x_b [0.4–0.7] (7 valores); motor de propiedades (2 valores).**  

| Grupo | Valor | Clase (antes) | Clase (ahora) | Misma clase | η (antes) [%] | η (ahora) [%] | Δη [pp] | Mensaje (antes) | Mensaje (ahora) |
|---|---|---|---|---|---|---|---|---|---|
| base |  | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  |  | presupuesto de tiempo agotado: 1 evaluaciones de F en 316.5 s (presupuesto 300 s |
| P_alta | 2000 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=2000.0 kPa, T=623.0000091226806 K): no existe equilib | extremos [301.0329, 307.1500] K sin cambio de signo de F (F(lo)=76.814, F(hi)=71 |
| P_alta | 2250 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=2250.0 kPa, T=623.0000058142358 K): no existe equilib | extremos [301.0329, 317.1500] K sin cambio de signo de F (F(lo)=79.155, F(hi)=65 |
| P_alta | 2500 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=2500.0 kPa, T=623.0000024147047 K): no existe equilib | extremos [301.0329, 327.1500] K sin cambio de signo de F (F(lo)=81.794, F(hi)=59 |
| P_alta | 2750 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=2750.0 kPa, T=622.9999988927121 K): no existe equilib | extremos [301.0329, 337.1500] K sin cambio de signo de F (F(lo)=84.509, F(hi)=52 |
| P_alta | 3000 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [301.0329, 347.1500] K sin cambio de signo de F (F(lo)=87.376, F(hi)=45 |
| P_alta | 3250 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3250.0 kPa, T=622.9999916547947 K): no existe equilib | extremos [301.0329, 352.1500] K sin cambio de signo de F (F(lo)=90.346, F(hi)=43 |
| P_alta | 3500 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3500.0 kPa, T=622.9999884354551 K): no existe equilib | extremos [301.0329, 362.1500] K sin cambio de signo de F (F(lo)=93.153, F(hi)=36 |
| P_alta | 3750 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3750.0 kPa, T=622.9999846467892 K): no existe equilib | extremos [301.0329, 367.1500] K sin cambio de signo de F (F(lo)=93.01, F(hi)=33. |
| P_alta | 4000 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=4000.0 kPa, T=622.9999807869 K): no existe equilibrio | extremos [301.0329, 372.1500] K sin cambio de signo de F (F(lo)=92.621, F(hi)=30 |
| x_b | 0.4 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.999986634595 K): no existe equilibr | extremos [306.0329, 387.1500] K sin cambio de signo de F (F(lo)=92.575, F(hi)=21 |
| x_b | 0.45 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999908239907 K): no existe equilib | extremos [301.0329, 367.1500] K sin cambio de signo de F (F(lo)=94.732, F(hi)=33 |
| x_b | 0.5 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [301.0329, 347.1500] K sin cambio de signo de F (F(lo)=87.376, F(hi)=45 |
| x_b | 0.55 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999995938454 K): no existe equilib | extremos [301.0329, 322.1500] K sin cambio de signo de F (F(lo)=85.287, F(hi)=66 |
| x_b | 0.6 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 20 | sin dos extremos evaluables en el rango físico de T1 (repliegues_lo=64, repliegu |
| x_b | 0.65 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 20 | sin dos extremos evaluables en el rango físico de T1 (repliegues_lo=64, repliegu |
| x_b | 0.7 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver TASK_CONTEXT 20 | sin dos extremos evaluables en el rango físico de T1 (repliegues_lo=64, repliegu |
| T_amb | 299.4 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.4000, 347.1500] K sin cambio de signo de F (F(lo)=87.835, F(hi)=45 |
| T_amb | 299.2 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.2000, 347.1500] K sin cambio de signo de F (F(lo)=87.98, F(hi)=45. |
| T_amb | 299.1 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.1000, 347.1500] K sin cambio de signo de F (F(lo)=88.053, F(hi)=45 |
| T_amb | 298.95 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.9500, 347.1500] K sin cambio de signo de F (F(lo)=88.162, F(hi)=45 |
| T_amb | 298.9 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.9000, 347.1500] K sin cambio de signo de F (F(lo)=88.198, F(hi)=45 |
| T_amb | 298.7 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.7000, 347.1500] K sin cambio de signo de F (F(lo)=88.343, F(hi)=45 |
| T_amb | 298.5 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.5000, 347.1500] K sin cambio de signo de F (F(lo)=88.489, F(hi)=45 |
| T_amb | 298.3 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.3000, 347.1500] K sin cambio de signo de F (F(lo)=88.634, F(hi)=45 |
| T_amb | 298.2 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.2000, 347.1500] K sin cambio de signo de F (F(lo)=88.707, F(hi)=45 |
| T_amb | 298 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.0000, 347.1500] K sin cambio de signo de F (F(lo)=88.853, F(hi)=45 |
| T_amb | 297.95 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [298.9500, 347.1500] K sin cambio de signo de F (F(lo)=88.889, F(hi)=45 |
| T_amb | 298.65 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [299.6500, 347.1500] K sin cambio de signo de F (F(lo)=88.38, F(hi)=45. |
| T_amb | 300.485 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [301.4850, 347.1500] K sin cambio de signo de F (F(lo)=87.048, F(hi)=45 |
| T_amb | 301.55 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [302.5500, 347.1500] K sin cambio de signo de F (F(lo)=86.277, F(hi)=46 |
| T_amb | 302.4 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [303.4000, 347.1500] K sin cambio de signo de F (F(lo)=85.664, F(hi)=46 |
| T_amb | 303.1 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [304.1000, 347.1500] K sin cambio de signo de F (F(lo)=85.193, F(hi)=46 |
| T_amb | 303.55 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [304.5500, 347.1500] K sin cambio de signo de F (F(lo)=84.9, F(hi)=46.9 |
| T_amb | 302.9 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [303.9000, 347.1500] K sin cambio de signo de F (F(lo)=85.323, F(hi)=46 |
| T_amb | 302.25 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [303.2500, 347.1500] K sin cambio de signo de F (F(lo)=85.772, F(hi)=46 |
| T_amb | 301.655 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [302.6550, 347.1500] K sin cambio de signo de F (F(lo)=86.202, F(hi)=46 |
| T_amb | 300.9 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [301.9000, 347.1500] K sin cambio de signo de F (F(lo)=86.748, F(hi)=46 |
| T_amb | 299.8 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.8000, 347.1500] K sin cambio de signo de F (F(lo)=87.545, F(hi)=45 |
| T_amb | 299.2 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.2000, 347.1500] K sin cambio de signo de F (F(lo)=87.98, F(hi)=45. |
| T_amb | 299.15 | NO_CONVERGIO | NO_CONVERGIO | sí |  |  |  | equilibrio_liquido_vapor(P=3000.0 kPa, T=622.9999953066318 K): no existe equilib | extremos [300.1500, 347.1500] K sin cambio de signo de F (F(lo)=88.016, F(hi)=45 |

**Notas:** Filtro: sin filtro (comparación punto a punto). n = 41 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: resultados/2026-10-06_final_M1/m1_comparacion.csv.

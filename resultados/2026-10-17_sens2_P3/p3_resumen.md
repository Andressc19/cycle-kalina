# Sens2 P3 - resumen (Paso 4)

Indices given-data con 3 variables dummy como piso de ruido y IC bootstrap (500 remuestreos de filas, 95 %). Un indice es `distinguible del ruido` si su limite inferior del IC supera el maximo de las dummy. `rango medio` = puesto medio entre metodos (1 = mas importante).

## C1 Husavik
- Que decide que haya KALINA (Y1): x_b (rango 1.0, si), P_baja (rango 2.6, si), eps_cond (rango 2.8, si). Mejor dummy: rango 6.8.
- Que mueve eta (Y2): eta_t (rango 1.2, si), P_baja (rango 3.2, si), T_fuente (rango 3.7, si).
- Que mueve W_net/m_b (Y3): T_fuente (rango 1.0, si), eta_t (rango 3.2, si), eps_hrvg (rango 4.2, si).
- Bajan D (Y4, PRCC negativo): eps_cond (PRCC -0.62), P_baja (PRCC -0.61), P_alta (PRCC -0.35).
- Pares con interaccion fuerte: B2 (eta 1-R2=0.06, ind 1-R2=0.52, sinergico), B4 (eta 1-R2=nan, ind 1-R2=0.52, no_aplica), B6 (eta 1-R2=0.28, ind 1-R2=0.72, sinergico (fuerte)).
- Elasticidades mayores en el base: eta_t (1.04, centrada), T_fuente (1.02, centrada), T_sumidero (1.00, hacia adelante).

## C2 ancla A*
- Que decide que haya KALINA (Y1): eps_cond (rango 1.6, si), P_baja (rango 1.8, si), x_b (rango 2.6, si). Mejor dummy: rango 8.5.
- Que mueve eta (Y2): eta_t (rango 1.3, si), P_baja (rango 3.0, si), T_fuente (rango 3.7, si).
- Que mueve W_net/m_b (Y3): T_fuente (rango 1.0, si), eta_t (rango 3.3, si), eps_hrvg (rango 4.3, si).
- Bajan D (Y4, PRCC negativo): eps_cond (PRCC -0.78), P_baja (PRCC -0.66), P_alta (PRCC -0.63).
- Pares con interaccion fuerte: B1 (eta 1-R2=0.08, ind 1-R2=0.29, sinergico), B2 (eta 1-R2=0.18, ind 1-R2=0.26, antagonico), B4 (eta 1-R2=0.18, ind 1-R2=0.33, antagonico), B6 (eta 1-R2=0.07, ind 1-R2=0.26, antagonico).
- Elasticidades mayores en el base: T_fuente (13.16, centrada), x_b (3.91, centrada), T_sumidero (1.63, centrada).

## C3 caliente 150 C
- Que decide que haya KALINA (Y1): P_baja (rango 1.0, si), x_b (rango 3.6, si), eps_hrvg (rango 4.0, no). Mejor dummy: rango 8.6.
- Que mueve eta (Y2): P_alta (rango 2.0, si), x_b (rango 2.2, si), eta_t (rango 3.0, si).
- Que mueve W_net/m_b (Y3): T_fuente (rango 1.8, si), x_b (rango 1.8, si), eps_hrvg (rango 4.0, si).
- Bajan D (Y4, PRCC negativo): P_baja (PRCC -0.72), eps_cond (PRCC -0.70), P_alta (PRCC -0.18).
- Pares con interaccion fuerte: B2 (eta 1-R2=0.08, ind 1-R2=0.29, antagonico), B4 (eta 1-R2=0.17, ind 1-R2=0.37, antagonico).
- Elasticidades mayores en el base: eta_t (1.03, centrada), T_sumidero (0.84, centrada), P_baja (-0.79, centrada).

## C4 frio 110 C
- Que decide que haya KALINA (Y1): T_fuente (rango 1.0, si), P_baja (rango 2.0, si), eps_cond (rango 3.2, no). Mejor dummy: rango 7.1.
- Que mueve eta (Y2): P_alta (rango 1.8, si), x_b (rango 2.7, si), eta_t (rango 3.0, si).
- Que mueve W_net/m_b (Y3): x_b (rango 1.3, si), T_fuente (rango 2.0, si), eps_hrvg (rango 3.3, si).
- Bajan D (Y4, PRCC negativo): P_baja (PRCC -0.46), P_alta (PRCC -0.34), x_b (PRCC -0.33).
- Pares con interaccion fuerte: B2 (eta 1-R2=0.08, ind 1-R2=0.40, antagonico), B4 (eta 1-R2=0.28, ind 1-R2=0.46, sinergico (fuerte)).
- Elasticidades mayores en el base: T_fuente (1.28, centrada), T_sumidero (1.08, centrada), eta_t (1.05, centrada).

## Metodos: coincidencias y discrepancias

- E3 C1 Husavik / Y1 KALINA (total): mejor real x_b (rango 1.0) frente a mejor dummy dummy_1 (rango 6.8); variables distinguibles: 3 de 9.
- E3 C1 Husavik / Y2 eta (%): mejor real eta_t (rango 1.2) frente a mejor dummy dummy_2 (rango 6.8); variables distinguibles: 8 de 9.
- E3 C1 Husavik / Y3 W_net/m_b: mejor real T_fuente (rango 1.0) frente a mejor dummy dummy_2 (rango 8.0); variables distinguibles: 9 de 9.
- E3 C2 ancla A* / Y1 KALINA (total): mejor real eps_cond (rango 1.6) frente a mejor dummy dummy_2 (rango 8.5); variables distinguibles: 5 de 9.
- E3 C2 ancla A* / Y2 eta (%): mejor real eta_t (rango 1.3) frente a mejor dummy dummy_1 (rango 7.8); variables distinguibles: 9 de 9.
- E3 C2 ancla A* / Y3 W_net/m_b: mejor real T_fuente (rango 1.0) frente a mejor dummy dummy_1 (rango 6.5); variables distinguibles: 9 de 9.
- E14 C3 caliente 150 C / Y1 KALINA (total): mejor real P_baja (rango 1.0) frente a mejor dummy dummy_1 (rango 8.6); variables distinguibles: 5 de 9.
- E14 C3 caliente 150 C / Y2 eta (%): mejor real P_alta (rango 2.0) frente a mejor dummy dummy_1 (rango 6.3); variables distinguibles: 6 de 9.
- E14 C3 caliente 150 C / Y3 W_net/m_b: mejor real T_fuente (rango 1.8) frente a mejor dummy dummy_1 (rango 7.3); variables distinguibles: 8 de 9.
- E14 C4 frio 110 C / Y1 KALINA (total): mejor real T_fuente (rango 1.0) frente a mejor dummy dummy_1 (rango 7.1); variables distinguibles: 2 de 9.
- E14 C4 frio 110 C / Y2 eta (%): mejor real P_alta (rango 1.8) frente a mejor dummy dummy_1 (rango 7.2); variables distinguibles: 8 de 9.
- E14 C4 frio 110 C / Y3 W_net/m_b: mejor real x_b (rango 1.3) frente a mejor dummy dummy_3 (rango 7.7); variables distinguibles: 9 de 9.
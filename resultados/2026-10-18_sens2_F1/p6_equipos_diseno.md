# Sens2 F1 - A2b, Parte 2: envolventes de equipos por diseno

P5, P50 y P95 de cada cantidad de equipo sobre los KALINA (total), por ambito,
en tres conjuntos: a_todos (todos los KALINA), b_solo_LHS (solo estudios 3 y 14)
y c_peso_igual (peso 1 / n(centro, estudio): cada combinacion centro-estudio
aporta lo mismo). desplazamiento = (p50_conjunto - p50_a) / (p95_a - p5_a);
sensible si el mayor |desplazamiento| de b y c pasa de 0.15.

a_todos reproduce p4_envolventes.csv: 0 filas con P50 distinta en mas de 1e-6.

## Cantidades sensibles por ambito

| ambito | sensibles | de las de equipo (CANT_DEP) |
|---|---|---|
| todos | dh_turb, Wt_mb, q4, m_v_mb, aprox_cond_sal, eta_pct, wnet_mb | 4 de 11 |
| C1 Husavik | rp, dh_turb, Wt_mb, m_v_mb, dT_A, LMTD_reg, qreg_qi, Qout_mb, aprox_cond_sal, Qi_mb, Wp_Wt, P_baja, eta_pct, wnet_mb | 8 de 11 |
| C2 ancla A* | rp, dh_turb, q4, T3, T4, m_v_mb, dT_A, qreg_qi, Qout_mb, aprox_cond_sal, aprox_cond_ent, Qi_mb, aprox_fuente, P_baja | 7 de 11 |
| C3 caliente 150 C | rp, dh_turb, Wt_mb, q4, T3, m_v_mb, dT_A, dT_B, pinch_reg, LMTD_reg, UA_reg, qreg_qi, Qout_mb, aprox_cond_ent, Qi_mb, Wp_Wt, P_baja, eta_pct, wnet_mb | 10 de 11 |
| C4 frio 110 C | rp, dh_turb, Wt_mb, q4, T4, m_v_mb, dT_A, Qout_mb, aprox_cond_sal, aprox_cond_ent, Qi_mb, Wp_mb, P_alta, P_baja, eta_pct, wnet_mb | 7 de 11 |

Lectura: si al restringir a los estudios LHS o al dar el mismo peso a cada
combinacion centro-estudio la mediana se corre mas de 0.15 veces el ancho
P5-P95, la envolvente depende del diseno de muestreo y hay que citarla con esa
precision. Los numeros completos estan en `p6_equipos_diseno.csv`.

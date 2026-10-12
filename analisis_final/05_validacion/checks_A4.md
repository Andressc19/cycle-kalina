# Checks A4 — validación cruzada contra la tabla canónica

Filas: 78 · ✔ 76 · ✘ 2 · NO EVALUABLE 0

| id_check | caso | filtro | cifra | esperado | recalculado | resultado | nota |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V01 | KF-M01 | todas las filas | filas; genuinas | 42 filas; 42 NO_CONVERGIO o N2 (0 genuinas) | 42 filas; 0 genuinas | ✔ |  |
| V02 | KF-M02-N1 | malla + bisección | n KALINA | 0 KALINA | 0 KALINA | ✔ |  |
| V03 | KF-M02-N2-A | todas las filas | n KALINA | 0 KALINA | 0 KALINA | ✔ |  |
| V04 | KF-M02-N2-B | KALINA | T_fuente; mín P_baja KALINA | T_fuente ∈ {390,403,420,434} K; mín P_baja 445.455 kPa con η 0.0245 (T_fuente 390) | T_fuente [390.0, 403.0, 420.0, 434.0]; mín P_baja 445.455 kPa con η 0.0245 (T_fuente 390) | ✔ |  |
| V05 | KF-M02-N2-B | KALINA | n KALINA; fuera de rango | 59; 11 | 59; 11 | ✔ |  |
| V06 | KF-M02R | todas las filas | n KALINA; fuera de rango | 14; 13 | 20; 19 | ✘ | El reporte (m2r_kalina.csv) cuenta puntos distintos: 14 y 13 fuera. La canónica no deduplica (malla y bisección solapan). |
| V07 | KF-M02S | KALINA | únicos (base,T_sumidero,P_baja); KALINA en B4 | 123; 0 | 123; 0 | ✔ |  |
| V08 | KF-M02S-B1 | KALINA en T_sumidero 278.15 y 300.032917 | η máx; P_baja mín | 278.15: (0.1041; 290.625) / 300.03: (0.0849; 562.5) | 278.15: (0.1041; 290.625) / 300.03: (0.0849; 562.5) | ✔ | η en la P_baja mínima coincide con η máx (η baja al subir P_baja). |
| V08 | KF-M02S-B2 | KALINA en T_sumidero 278.15 y 300.032917 | η máx; P_baja mín | 278.15: (0.1191; 393.75) / 300.03: (0.0911; 740.625) | 278.15: (0.1191; 393.75) / 300.03: (0.0911; 740.625) | ✔ | η en la P_baja mínima coincide con η máx (η baja al subir P_baja). |
| V08 | KF-M02S-B3 | KALINA en T_sumidero 278.15 y 300.032917 | η máx; P_baja mín | 278.15: (0.0969; 750) / 300.03: (0.063; 1312.5) | 278.15: (0.0969; 750) / 300.03: (0.0630; 1312.5) | ✔ | η en la P_baja mínima coincide con η máx (η baja al subir P_baja). |
| V09 | KF-M03 | todas las filas | filas; genuinas; KALINA; fuera | 171; 148; 86; 8 | 171; 148; 86; 8 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη x_b [pp] | 10.78 | 10.78 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη P_baja [pp] | 6.80 | 6.80 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη eps_hrvg [pp] | 6.69 | 6.69 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη eta_t [pp] | 6.32 | 6.32 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη P_alta [pp] | 5.14 | 5.14 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη eps_reg [pp] | 4.99 | 4.99 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη T_fuente [pp] | 3.67 | 3.67 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη eta_p [pp] | 1.38 | 1.38 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη T_sumidero [pp] | 0.85 | 0.85 | ✔ |  |
| V10 | KF-M03 | malla, genuinas con W_net>0 | Δη eps_cond [pp] | 0.82 | 0.82 | ✔ |  |
| V11 | KF-M03 | malla, KALINA | η máx eps_reg | 0.1096 en 0.95 | 0.1096 en 0.95 | ✔ |  |
| V11 | KF-M03 | malla, KALINA | η máx eta_t | 0.0962 en 0.95 | 0.0962 en 0.95 | ✔ |  |
| V12 | KF-M04 + KF-M04b | todas las filas | filas; KALINA; fuera | 500; 121; 222 | 500; 121; 222 | ✔ |  |
| V13 | KF-M04 + KF-M04b | KALINA | p5–p95 P_alta | [2155.69; 4841.78] | [2155.69; 4841.78] | ✔ |  |
| V13 | KF-M04 + KF-M04b | KALINA | p5–p95 P_baja | [683.165; 1460.71] | [683.165; 1460.71] | ✔ |  |
| V13 | KF-M04 + KF-M04b | KALINA | p5–p95 dP | [968.027; 3717.63] | [968.027; 3717.63] | ✔ |  |
| V13 | KF-M04 + KF-M04b | KALINA | p5–p95 rP | [1.68614; 5.33942] | [1.68614; 5.33942] | ✔ |  |
| V14 | KF-M04c | todas las filas | filas; omitidas; evaluadas | 150; 15; 135 | 150; 15; 135 | ✔ |  |
| V15 | KF-M05 | subcasos KF-M05-1…5 = S1…S5 | filas; omitidas; KALINA por esc. (S1→S5); fuera de rango (de evaluadas) | 600; 2; [4,0,0,6,10]; 322 de 598 | 600; 2; [4, 0, 0, 6, 10]; 322 de 598 | ✔ |  |
| V16 | KF-M05c | todas las filas | filas; KALINA | 165; 104 | 165; 104 | ✔ |  |
| V17 | KF-M07-A1 | KALINA | η máx | 0.1498 | 0.1498 | ✔ |  |
| V17 | KF-M07-A2 | KALINA | η máx | 0.1548 | 0.1548 | ✔ |  |
| V17 | KF-M07-A3 | KALINA | η máx | 0.1274 | 0.1274 | ✔ |  |
| V17 | KF-M07-A4 | KALINA | η máx | 0.1560 | 0.1560 | ✔ |  |
| V17 | KF-M07-A5 | KALINA | η máx | 0.1109 | 0.1109 | ✔ |  |
| V18 | KF-M09-R0-T_fuente | ronda 0, conservados T_fuente | n; genuinas; KALINA; confiables | 100; 60; 7; 0 | 100; 60; 7; 0 | ✔ |  |
| V18 | KF-M09-R0-eficiencias | ronda 0, conservados eficiencias | n; genuinas; KALINA; confiables | 100; 88; 13; 11 | 100; 88; 13; 11 | ✔ |  |
| V18 | KF-M09-R0-P_alta | ronda 0, conservados P_alta | n; genuinas; KALINA; confiables | 100; 88; 19; 12 | 100; 88; 19; 12 | ✔ |  |
| V18 | KF-M09-R0-P_baja | ronda 0, conservados P_baja | n; genuinas; KALINA; confiables | 100; 85; 1; 1 | 100; 85; 1; 1 | ✔ |  |
| V18 | KF-M09-R0-T_sumidero | ronda 0, conservados T_sumidero | n; genuinas; KALINA; confiables | 100; 87; 17; 13 | 100; 87; 17; 13 | ✔ |  |
| V18 | KF-M09-R0-x_b | ronda 0, conservados x_b | n; genuinas; KALINA; confiables | 100; 85; 29; 15 | 100; 85; 29; 15 | ✔ |  |
| V18 | KF-M09-R1-x_b+T_fuente | ronda 1, conservados x_b+T_fuente | n; genuinas; KALINA; confiables | 30; 20; 2; 0 | 30; 20; 2; 0 | ✔ |  |
| V18 | KF-M09-R1-x_b+eficiencias | ronda 1, conservados x_b+eficiencias | n; genuinas; KALINA; confiables | 30; 26; 11; 6 | 30; 26; 11; 6 | ✔ |  |
| V18 | KF-M09-R1-x_b+P_alta | ronda 1, conservados x_b+P_alta | n; genuinas; KALINA; confiables | 30; 28; 11; 7 | 30; 28; 11; 7 | ✔ |  |
| V18 | KF-M09-R1-x_b+P_baja | ronda 1, conservados x_b+P_baja | n; genuinas; KALINA; confiables | 30; 27; 4; 3 | 30; 27; 4; 3 | ✔ |  |
| V18 | KF-M09-R1-x_b+T_sumidero | ronda 1, conservados x_b+T_sumidero | n; genuinas; KALINA; confiables | 30; 26; 9; 5 | 30; 26; 9; 5 | ✔ |  |
| V18 | KF-M09-R2-x_b+P_alta+T_fuente | ronda 2, conservados x_b+P_alta+T_fuente | n; genuinas; KALINA; confiables | 30; 19; 3; 0 | 30; 19; 3; 0 | ✔ |  |
| V18 | KF-M09-R2-x_b+P_alta+eficiencias | ronda 2, conservados x_b+P_alta+eficiencias | n; genuinas; KALINA; confiables | 30; 28; 13; 7 | 30; 28; 13; 7 | ✔ |  |
| V18 | KF-M09-R2-x_b+P_alta+P_baja | ronda 2, conservados x_b+P_alta+P_baja | n; genuinas; KALINA; confiables | 30; 28; 2; 2 | 30; 28; 2; 2 | ✔ |  |
| V18 | KF-M09-R2-x_b+P_alta+T_sumidero | ronda 2, conservados x_b+P_alta+T_sumidero | n; genuinas; KALINA; confiables | 30; 27; 8; 6 | 30; 27; 8; 6 | ✔ |  |
| V18 | KF-M09-R3-x_b+P_alta+eficiencias+T_fuente | ronda 3, conservados x_b+P_alta+eficiencias+T_fuente | n; genuinas; KALINA; confiables | 30; 0; 0; 0 | 30; 0; 0; 0 | ✔ |  |
| V18 | KF-M09-R3-x_b+P_alta+eficiencias+P_baja | ronda 3, conservados x_b+P_alta+eficiencias+P_baja | n; genuinas; KALINA; confiables | 30; 28; 5; 5 | 30; 28; 5; 5 | ✔ |  |
| V18 | KF-M09-R3-x_b+P_alta+eficiencias+T_sumidero | ronda 3, conservados x_b+P_alta+eficiencias+T_sumidero | n; genuinas; KALINA; confiables | 30; 29; 6; 4 | 30; 29; 6; 4 | ✔ |  |
| V19 | KF-M09-R3-x_b+P_alta+eficiencias+P_baja | KALINA | n; confiables; T redondeadas | 5; 5; T_fuente [391,409] K; T_sumidero [280,293] K | 5; 5; T_fuente [391,409]; T_sumidero [280,293] | ✔ |  |
| V20 | KF-M09 | conservados que incluyen T_fuente | KALINA confiables | 0 en todas las rondas | 0 | ✔ | Subcasos: KF-M09-R0-T_fuente, KF-M09-R1-x_b+T_fuente, KF-M09-R2-x_b+P_alta+T_fuente, KF-M09-R3-x_b+P_alta+eficiencias+T_fuente |
| V21 | KF-M10-F3 | todas las filas | filas; KALINA | 97; 97 | 97; 97 | ✔ |  |
| V22 | KF-M10-MALLA + KF-M10b-MALLA | KALINA (malla) | P_baja mín KALINA por x_b vs REPORTE_M10b | ≤0.45 sin KALINA; 0.50→200; 0.55→300; 0.60→400; 0.65→500; 0.70→500 | coincide | ✔ |  |
| V22 | KF-M10-MALLA + KF-M10b-MALLA | KALINA (malla) | P_baja mín KALINA por x_b vs REPORTE_M10 | 0.70→500; 0.73→600; 0.76→600; 0.79→700; 0.82→700; 0.85→800; 0.88→800; 0.91→800 | coincide | ✔ |  |
| V22 | KF-M10-MALLA + KF-M10b-MALLA | x_b ≤ 0.475 | genuinos con W_net > 0 | 0 | 0 | ✔ |  |
| V22 | KF-M10-MALLA + KF-M10b-MALLA | KALINA (malla) | primer x_b con KALINA y su P_baja mín | 0.55 con 300 kPa | 0.5 con 200.0 kPa | ✘ | REPORTE_M10b §4 dice 0.50 con 200 kPa (KALINA formal, η≈0.1–1.2 %); 0.55 es el primero 'útil' según la nota del director, no el primero KALINA. |
| V23 | KF-M01 | todas las filas | N2 | (información) | 0 | ✔ | solo información |
| V23 | KF-M02-N1 | todas las filas | N2 | (información) | 21 | ✔ | solo información |
| V23 | KF-M02-N2 | todas las filas | N2 | (información) | 12 | ✔ | solo información |
| V23 | KF-M02R | todas las filas | N2 | (información) | 4 | ✔ | solo información |
| V23 | KF-M02S | todas las filas | N2 | (información) | 0 | ✔ | solo información |
| V23 | KF-M03 | todas las filas | N2 | (información) | 6 | ✔ | solo información |
| V23 | KF-M04 | todas las filas | N2 | (información) | 7 | ✔ | solo información |
| V23 | KF-M04b | todas las filas | N2 | (información) | 6 | ✔ | solo información |
| V23 | KF-M04c | todas las filas | N2 | (información) | 6 | ✔ | solo información |
| V23 | KF-M05 | todas las filas | N2 | (información) | 12 | ✔ | solo información |
| V23 | KF-M05c | todas las filas | N2 | (información) | 15 | ✔ | solo información |
| V23 | KF-M06 | todas las filas | N2 | (información) | 0 | ✔ | solo información |
| V23 | KF-M07 | todas las filas | N2 | (información) | 1 | ✔ | solo información |
| V23 | KF-M08 | todas las filas | N2 | (información) | 2 | ✔ | solo información |
| V23 | KF-M09 | todas las filas | N2 | (información) | 29 | ✔ | solo información |
| V23 | KF-M10 | todas las filas | N2 | (información) | 0 | ✔ | solo información |
| V23 | KF-M10b | todas las filas | N2 | (información) | 16 | ✔ | solo información |

## Resumen

- ✔ coinciden: 76
- ✘ no coinciden: 2
- NO EVALUABLE: 0

### Lista de ✘

- V06 · KF-M02R · n KALINA; fuera de rango: esperado 14; 13 / recalculado 20; 19 — El reporte (m2r_kalina.csv) cuenta puntos distintos: 14 y 13 fuera. La canónica no deduplica (malla y bisección solapan).
- V22 · KF-M10-MALLA + KF-M10b-MALLA · primer x_b con KALINA y su P_baja mín: esperado 0.55 con 300 kPa / recalculado 0.5 con 200.0 kPa — REPORTE_M10b §4 dice 0.50 con 200 kPa (KALINA formal, η≈0.1–1.2 %); 0.55 es el primero 'útil' según la nota del director, no el primero KALINA.

### Lista de NO EVALUABLE

- ninguno

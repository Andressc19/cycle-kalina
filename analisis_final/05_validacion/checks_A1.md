# Checks A1 — tabla canónica y condiciones

## 1. Filas leídas = filas en la tabla canónica

- **OK** — resultados/2026-10-06_final_M1/m1_filas.csv: 42 leídas vs 42 en la tabla
- **OK** — resultados/2026-10-06_final_M2/m2n1_malla.csv: 100 leídas vs 100 en la tabla
- **OK** — resultados/2026-10-06_final_M2/m2n1_biseccion.csv: 32 leídas vs 32 en la tabla
- **OK** — resultados/2026-10-06_final_M2/m2n2_malla.csv: 144 leídas vs 144 en la tabla
- **OK** — resultados/2026-10-06_final_M2/m2n2_biseccion.csv: 36 leídas vs 36 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n1_malla.csv: 60 leídas vs 60 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n1_biseccion.csv: 20 leídas vs 20 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n2a_malla.csv: 60 leídas vs 60 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n2a_biseccion.csv: 0 leídas vs 0 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n2b_malla.csv: 48 leídas vs 48 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n2b_biseccion.csv: 16 leídas vs 16 en la tabla
- **OK** — resultados/2026-10-06_final_M2R/m2r_n3_malla.csv: 21 leídas vs 21 en la tabla
- **OK** — resultados/2026-10-06_final_M2S/m2s_malla.csv: 200 leídas vs 200 en la tabla
- **OK** — resultados/2026-10-06_final_M2S/m2s_biseccion.csv: 120 leídas vs 120 en la tabla
- **OK** — resultados/2026-10-06_final_M3/m3_ofat.csv: 171 leídas vs 171 en la tabla
- **OK** — resultados/2026-10-06_final_M4/m4_lhs.csv: 300 leídas vs 300 en la tabla
- **OK** — resultados/2026-10-07_final_M4b/m4b_lhs.csv: 200 leídas vs 200 en la tabla
- **OK** — resultados/2026-10-07_final_M4c/m4c_lhs.csv: 150 leídas vs 150 en la tabla
- **OK** — resultados/2026-10-07_final_M5/m5_lhs.csv: 600 leídas vs 600 en la tabla
- **OK** — resultados/2026-10-07_final_M5c/m5c_malla.csv: 165 leídas vs 165 en la tabla
- **OK** — resultados/2026-10-07_final_M7/m7_evaluaciones.csv: 560 leídas vs 560 en la tabla
- **OK** — resultados/2026-10-07_final_M8_anecdotico/m8_oat.csv: 160 leídas vs 160 en la tabla
- **OK** — resultados/2026-10-08_final_M6/m6_verificacion.csv: 24 leídas vs 24 en la tabla
- **OK** — resultados/2026-10-08_final_M6/m6_piso_30_4C.csv: 12 leídas vs 12 en la tabla
- **OK** — resultados/2026-10-08_final_M6/m6_subenfriamiento_evals.csv: 131 leídas vs 131 en la tabla
- **OK** — resultados/2026-10-08_final_M9/m9_paso1.csv: 600 leídas vs 600 en la tabla
- **OK** — resultados/2026-10-08_final_M9/m9_paso2.csv: 360 leídas vs 360 en la tabla
- **OK** — resultados/2026-10-08_final_M9/m9_husavik.csv: 24 leídas vs 24 en la tabla
- **OK** — resultados/2026-10-08_final_M9/m9_motor_real_raw.csv: 3 leídas vs 3 en la tabla
- **OK** — resultados/2026-10-09_final_M10_husavik/m10_recorrida_fase3.csv: 97 leídas vs 97 en la tabla
- **OK** — resultados/2026-10-09_final_M10_husavik/m10_ofat.csv: 150 leídas vs 150 en la tabla
- **OK** — resultados/2026-10-09_final_M10_husavik/m10_malla_xb_pbaja.csv: 64 leídas vs 64 en la tabla
- **OK** — resultados/2026-10-09_final_M10b_xb_bajo/m10b_ofat_xb.csv: 17 leídas vs 17 en la tabla
- **OK** — resultados/2026-10-09_final_M10b_xb_bajo/m10b_malla_xb_pbaja.csv: 54 leídas vs 54 en la tabla
- **OK** — total 4741 filas de FUENTES vs 4741 en la tabla

## 2. Identificadores completos

- **OK** — campos vacíos: {'id_caso': 0, 'id_subcaso': 0, 'bloque_director': 0}

## 3. id_punto único

- **OK** — id_punto duplicados = 0 (n = 4741)

## 4. Conteo por caso y clase

| id_caso | n_puntos | genuinos | KALINA | KALINA_confiables | CORREGIBLE | INVIABLE | NO_CONVERGIO_sin_N2 | N2 | omitidos | fuera_rango |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KF-M01 | 42 | 0 | 0 | 0 | 0 | 0 | 42 | 0 | 0 | 0 |
| KF-M02-N1 | 132 | 15 | 0 | 0 | 13 | 2 | 96 | 21 | 0 | 32 |
| KF-M02-N2 | 180 | 165 | 59 | 48 | 106 | 0 | 3 | 12 | 0 | 105 |
| KF-M02R | 225 | 154 | 20 | 1 | 133 | 1 | 67 | 4 | 0 | 152 |
| KF-M02S | 320 | 269 | 153 | 119 | 113 | 3 | 51 | 0 | 0 | 89 |
| KF-M03 | 171 | 148 | 86 | 86 | 57 | 5 | 17 | 6 | 0 | 8 |
| KF-M04 | 300 | 266 | 76 | 57 | 181 | 9 | 27 | 7 | 0 | 128 |
| KF-M04b | 200 | 186 | 45 | 26 | 127 | 14 | 8 | 6 | 0 | 94 |
| KF-M04c | 150 | 120 | 75 | 45 | 43 | 2 | 9 | 6 | 15 | 58 |
| KF-M05 | 600 | 382 | 20 | 2 | 219 | 143 | 204 | 12 | 2 | 322 |
| KF-M05c | 165 | 149 | 104 | 104 | 30 | 15 | 1 | 15 | 0 | 0 |
| KF-M07 | 560 | 549 | 419 | 331 | 130 | 0 | 10 | 1 | 0 | 131 |
| KF-M08 | 160 | 151 | 84 | 84 | 60 | 7 | 7 | 2 | 0 | 13 |
| KF-M06 | 167 | 151 | 142 | 137 | 9 | 0 | 16 | 0 | 0 | 6 |
| KF-M09 | 987 | 806 | 181 | 118 | 475 | 150 | 148 | 29 | 4 | 502 |
| KF-M10 | 311 | 309 | 253 | 253 | 56 | 0 | 2 | 0 | 0 | 0 |
| KF-M10b | 71 | 38 | 29 | 29 | 9 | 0 | 17 | 16 | 0 | 0 |
- **OK** — conteo por caso y clase (tabla Markdown)

## 5. Bloques con firma inconsistente (INFORMACIÓN)

- bloque B01 (subcasos: KF-M01-P_alta; KF-M01-base; KF-M01-x_b; KF-M01-T_amb): T_sumidero: KF-M01-P_alta=fijo 300.033; KF-M01-base=fijo 300.033; KF-M01-x_b=fijo 300.033; KF-M01-T_amb=barrido [297.95, 303.55] n=23 || P_alta: KF-M01-P_alta=barrido [2000, 4000] n=9; KF-M01-base=fijo 3000; KF-M01-x_b=fijo 3000; KF-M01-T_amb=fijo 3000 || x_b: KF-M01-P_alta=fijo 0.5; KF-M01-base=fijo 0.5; KF-M01-x_b=barrido [0.4, 0.7] n=7; KF-M01-T_amb=fijo 0.5 || motor: KF-M01-P_alta=fijo teqp; KF-M01-base=barrido n=2; KF-M01-x_b=fijo teqp; KF-M01-T_amb=fijo teqp
- bloque B12 (subcasos: KF-M06-VER; KF-M06-PISO; KF-M06-SUB; KF-M09-REAL): T_amb_diseno: KF-M06-VER=barrido [278.15, 302.581] n=5; KF-M06-PISO=fijo 303.55; KF-M06-SUB=sin_dato; KF-M09-REAL=barrido [283.15, 300.033] n=2 || motor: KF-M06-VER=barrido n=2; KF-M06-PISO=fijo teqp; KF-M06-SUB=sin_dato; KF-M09-REAL=fijo real

## 5b. OAT: variables no movidas barridas por grupo (INFORMACIÓN)

- subcaso KF-M08, movida eta_t: T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_p, eps_hrvg, eps_reg, eps_cond, T_amb_diseno
- subcaso KF-M08, movida eta_p: T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eps_hrvg, eps_reg, eps_cond, T_amb_diseno
- subcaso KF-M08, movida eps_hrvg: T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_reg, eps_cond, T_amb_diseno
- subcaso KF-M08, movida eps_reg: T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_cond, T_amb_diseno
- subcaso KF-M08, movida eps_cond: T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, T_amb_diseno

## 6. Conteo de N2 por caso

| id_caso | N2 |
| --- | --- |
| KF-M01 | 0 |
| KF-M02-N1 | 21 |
| KF-M02-N2 | 12 |
| KF-M02R | 4 |
| KF-M02S | 0 |
| KF-M03 | 6 |
| KF-M04 | 7 |
| KF-M04b | 6 |
| KF-M04c | 6 |
| KF-M05 | 12 |
| KF-M05c | 15 |
| KF-M07 | 1 |
| KF-M08 | 2 |
| KF-M06 | 0 |
| KF-M09 | 29 |
| KF-M10 | 0 |
| KF-M10b | 16 |
- **OK** — N2 por caso: total = 137

**Resultado: TODO OK**

# TAB-M05c-02 · Frontera KALINA con las presiones del profesor

**Caso(s):** KF-M05c · **Bloque(s):** B10  
**Punto base:** PP = punto del profesor con P_alta y P_baja fijas  
**Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; eta_t = 0.85; eta_p = 0.75; eps_hrvg = 0.85; eps_reg = 0.75; motor = teqp.**  
**Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); eps_cond [0.85–0.95] (5 valores); T_amb_diseno [278.15–300.03] K (3 valores).**  

| Temperatura del sumidero, T_sumidero [K] | Efectividad del condensador, ε_cond [–] | KALINA | T_fuente mínima [K] | T_fuente máxima [K] | η en T_fuente mínima [%] | η en T_fuente máxima [%] |
|---|---|---|---|---|---|---|
| 278.1 | 0.850 | 8 | 390.0 | 407.5 | 1.92 | 9.83 |
| 278.1 | 0.875 | 9 | 390.0 | 410.0 | 1.89 | 10.13 |
| 278.1 | 0.900 | 9 | 390.0 | 410.0 | 1.86 | 10.02 |
| 278.1 | 0.925 | 9 | 390.0 | 410.0 | 1.84 | 9.91 |
| 278.1 | 0.950 | 9 | 390.0 | 410.0 | 1.81 | 9.80 |
| 290.6 | 0.850 | 8 | 390.0 | 407.5 | 2.27 | 10.40 |
| 290.6 | 0.875 | 9 | 390.0 | 410.0 | 2.24 | 10.70 |
| 290.6 | 0.900 | 9 | 390.0 | 410.0 | 2.21 | 10.58 |
| 290.6 | 0.925 | 9 | 390.0 | 410.0 | 2.17 | 10.46 |
| 290.6 | 0.950 | 9 | 390.0 | 410.0 | 2.15 | 10.35 |
| 300.0 | 0.850 | 0 |  |  |  |  |
| 300.0 | 0.875 | 1 | 390.0 | 390.0 | 2.54 | 2.54 |
| 300.0 | 0.900 | 2 | 390.0 | 392.5 | 2.51 | 5.03 |
| 300.0 | 0.925 | 4 | 390.0 | 397.5 | 2.47 | 7.85 |
| 300.0 | 0.950 | 9 | 390.0 | 410.0 | 2.44 | 10.81 |

**Notas:** Filtro: todos los puntos del barrido. n = 15. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: resultados/2026-10-07_final_M5c/m5c_frontera.csv.

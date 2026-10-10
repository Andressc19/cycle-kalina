# TAB-M02R-02 · Malla con η y ε en [0.40, 0.95]

**Caso(s):** KF-M02R · **Bloque(s):** B04-n1, B04-n2a, B04-n2b, B04-n3  
**Punto base:** PP = punto del profesor con η/ε dentro de [0.40, 0.95]  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; motor = teqp.**  
**Datos barridos: T_fuente [403–560] K (7 valores); P_baja [400–2000] kPa (20 valores); eta_t [0.4–0.95] (12 valores); eta_p [0.4–0.95] (12 valores); eps_hrvg [0.4–0.95] (32 valores); eps_reg [0.4–0.95] (12 valores); eps_cond [0.4–0.95] (12 valores).**  

| Parte | Variable 1 | Valor 1 | Variable 2 | Genuinos | KALINA | Falsos convergidos (N2) | d menor | Valor 1 del d menor | Valor 2 del d menor | η en el d menor [%] | η mayor [%] | Valor 1 de la η mayor | Valor 2 de la η mayor | Bloqueantes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n1 | eps_hrvg |  |  | 24 | 0 | 2 |  |  |  |  |  |  |  | O2(24) · O1(4) |
| n1 | eps_reg |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n1 | eps_cond |  |  | 0 | 0 | 2 |  |  |  |  |  |  |  |  |
| n1 | eta_t |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n1 | eta_p |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n2a | eps_hrvg | 0.4 | eps_cond | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n2a | eps_hrvg | 0.5 | eps_cond | 11 | 0 | 0 |  |  |  |  |  |  |  | O2(11) |
| n2a | eps_hrvg | 0.6 | eps_cond | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) · O1(1) |
| n2a | eps_hrvg | 0.7 | eps_cond | 9 | 0 | 0 |  |  |  |  |  |  |  | O2(9) · O1(3) |
| n2a | eps_hrvg | 0.8 | eps_cond | 4 | 0 | 0 |  |  |  |  |  |  |  | O1(4) · O2(4) |
| n2b | eps_hrvg | 0.4 | P_baja | 16 | 8 | 0 | 1.498 | 0.4 | 1318.18 | 6.27 | 6.27 | 0.4 | 1318.18 | O2(8) |
| n2b | eps_hrvg | 0.5 | P_baja | 14 | 5 | 0 | 1.626 | 0.5 | 1736.36 | 4.34 | 4.34 | 0.5 | 1736.36 | O2(9) |
| n2b | eps_hrvg | 0.6 | P_baja | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n2b | eps_hrvg | 0.7 | P_baja | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n3 | T_fuente | 403 | eps_cond | 3 | 1 | 0 | 1.050 | 403 | 0.95 | 9.50 | 9.50 | 403 | 0.95 | O2(2) |
| n3 | T_fuente | 420 | eps_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) · S3(1) |
| n3 | T_fuente | 434 | eps_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) |
| n3 | T_fuente | 466 | eps_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) |
| n3 | T_fuente | 497 | eps_cond | 2 | 0 | 0 |  |  |  |  |  |  |  | O2(2) |
| n3 | T_fuente | 529 | eps_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) · O1(2) |
| n3 | T_fuente | 560 | eps_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O1(3) · O2(3) |

**Notas:** Filtro: todos los puntos de la malla. n = 21. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: resultados/2026-10-06_final_M2R/m2r_resumen.csv.

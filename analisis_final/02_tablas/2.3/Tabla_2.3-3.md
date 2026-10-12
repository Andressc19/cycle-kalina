# Tabla 2.3-3 · Malla con η y ε en [0.40, 0.95]

**Estudio 2.3** · Dos cambios con η y ε en 0.40–0.95 · **Partes:** 2.3a, 2.3b, 2.3c, 2.3d  
**Punto base:** PP = punto del profesor con η/ε dentro de [0.40, 0.95]  
**Parte 2.3a (un cambio):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: η_t [0.4–0.95] (12 valores); η_p [0.4–0.95] (12 valores); ε_HRVG [0.4–0.95] (32 valores); ε_reg [0.4–0.95] (12 valores); ε_cond [0.4–0.95] (12 valores).**  
**Parte 2.3b (ε_HRVG × ε_cond):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: ε_HRVG [0.4–0.8] (5 valores); ε_cond [0.4–0.95] (12 valores).**  
**Parte 2.3c (ε_HRVG × P_baja):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: P_baja [400–2000] kPa (20 valores); ε_HRVG [0.4–0.7] (4 valores).**  
**Parte 2.3d (T_fuente × ε_cond):**  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [403–560] K (7 valores); ε_cond [0.85–0.95] (3 valores).**  

| Parte | Variable 1 | Valor 1 | Variable 2 | Genuinos | KALINA | Falsos convergidos | d menor | Valor 1 del d menor | Valor 2 del d menor | η en el d menor [%] | η mayor [%] | Valor 1 de la η mayor | Valor 2 de la η mayor | Bloqueantes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n1 | ε_HRVG |  |  | 24 | 0 | 2 |  |  |  |  |  |  |  | O2(24) · O1(4) |
| n1 | ε_reg |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n1 | ε_cond |  |  | 0 | 0 | 2 |  |  |  |  |  |  |  |  |
| n1 | η_t |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n1 | η_p |  |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| n2a | ε_HRVG | 0.4 | ε_cond | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n2a | ε_HRVG | 0.5 | ε_cond | 11 | 0 | 0 |  |  |  |  |  |  |  | O2(11) |
| n2a | ε_HRVG | 0.6 | ε_cond | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) · O1(1) |
| n2a | ε_HRVG | 0.7 | ε_cond | 9 | 0 | 0 |  |  |  |  |  |  |  | O2(9) · O1(3) |
| n2a | ε_HRVG | 0.8 | ε_cond | 4 | 0 | 0 |  |  |  |  |  |  |  | O1(4) · O2(4) |
| n2b | ε_HRVG | 0.4 | P_baja | 16 | 8 | 0 | 1.498 | 0.4 | 1318.18 | 6.27 | 6.27 | 0.4 | 1318.18 | O2(8) |
| n2b | ε_HRVG | 0.5 | P_baja | 14 | 5 | 0 | 1.626 | 0.5 | 1736.36 | 4.34 | 4.34 | 0.5 | 1736.36 | O2(9) |
| n2b | ε_HRVG | 0.6 | P_baja | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n2b | ε_HRVG | 0.7 | P_baja | 12 | 0 | 0 |  |  |  |  |  |  |  | O2(12) |
| n3 | T_fuente | 403 | ε_cond | 3 | 1 | 0 | 1.050 | 403 | 0.95 | 9.50 | 9.50 | 403 | 0.95 | O2(2) |
| n3 | T_fuente | 420 | ε_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) · S3(1) |
| n3 | T_fuente | 434 | ε_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) |
| n3 | T_fuente | 466 | ε_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) |
| n3 | T_fuente | 497 | ε_cond | 2 | 0 | 0 |  |  |  |  |  |  |  | O2(2) |
| n3 | T_fuente | 529 | ε_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O2(3) · O1(2) |
| n3 | T_fuente | 560 | ε_cond | 3 | 0 | 0 |  |  |  |  |  |  |  | O1(3) · O2(3) |

**Notas:** Filtro: todos los puntos de la malla. n = 21 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: resultados/2026-10-06_final_M2R/m2r_resumen.csv.

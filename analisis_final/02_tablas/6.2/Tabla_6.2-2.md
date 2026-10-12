# Tabla 6.2-2 · Corridas por parte y por clase

**Estudio 6.2** · Planta real de Húsavík · **Partes:** 6.2a, 6.2b, 6.2c, 6.2d  
**Punto base:** ancla de Húsavík (P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K); la parte 6.2a conserva los datos de septiembre  
**Parte 6.2a (Fase 3 de septiembre):**  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; m_b = 1 kg/s; η_p = 0.8; ε_HRVG = 0.85; motor de propiedades = teqp.**  
**Datos barridos: P_alta [3300–3500] kPa (3 valores); P_baja [670–1500] kPa (40 valores); x_b [0.78–0.83333] (6 valores); η_t [0.85–0.98] (8 valores); ε_reg [0.75–0.95] (12 valores); ε_cond [0.95–0.99] (5 valores); piso de O2 [283.15–303.55] K (2 valores).**  
**Parte 6.2b (una variable a la vez):**  
**Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.82; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): T_fuente [380–430] K (15 valores); T_sumidero [273.15–293.15] K (15 valores); P_alta [2500–4000] kPa (15 valores); P_baja [500–1200] kPa (15 valores); x_b [0.6–0.95] (15 valores); η_t [0.75–0.95] (15 valores); η_p [0.6–0.9] (15 valores); ε_HRVG [0.6–0.95] (15 valores); ε_reg [0.4–0.95] (15 valores); ε_cond [0.7–0.95] (15 valores).**  
**Parte 6.2c (malla x_b × P_baja (x_b 0.70–0.91); malla x_b × P_baja (x_b 0.30–0.70)):**  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp.**  
**Datos barridos: P_baja [200–1200] kPa (8 valores); x_b [0.3–0.91] (9 valores).**  
**Parte 6.2d (x_b bajo (0.30–0.70)):**  
**Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.3; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): x_b [0.3–0.7] (17 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 6.2a · Fase 3 de septiembre | 97 | 0 | 97 | 97 | 83 | 0 | 0 | 0 | 0 | 0 |
| 6.2b · una variable a la vez | 150 | 0 | 148 | 107 | 107 | 41 | 0 | 2 | 0 | 0 |
| 6.2c · malla x_b × P_baja (x_b 0.70–0.91) | 64 | 0 | 64 | 49 | 49 | 15 | 0 | 0 | 0 | 0 |
| 6.2d · x_b bajo (0.30–0.70) | 17 | 0 | 8 | 8 | 8 | 0 | 0 | 5 | 4 | 0 |
| 6.2c · malla x_b × P_baja (x_b 0.30–0.70) | 54 | 0 | 30 | 21 | 21 | 9 | 0 | 12 | 12 | 0 |

**Notas:** Filtro: conteo por parte. n = 5 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

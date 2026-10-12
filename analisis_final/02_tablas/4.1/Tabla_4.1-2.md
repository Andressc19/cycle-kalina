# Tabla 4.1-2 · Corridas por parte y por clase

**Estudio 4.1** · Escenarios de conservación · **Partes:** 4.1a, 4.1b, 4.1c, 4.1d, 4.1e  
**Punto base:** PP parcial según escenario S1 a S5  
**Parte 4.1a (conserva sus temperaturas):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.**  
**Datos barridos: P_alta [2000.1–4986.6] kPa (120 valores); P_baja [202.14–1989.7] kPa (120 valores); x_b [0.50124–0.84895] (120 valores); η_t [0.40062–0.94745] (120 valores); η_p [0.4043–0.94919] (120 valores); ε_HRVG [0.40441–0.94919] (120 valores); ε_reg [0.40384–0.9479] (120 valores); ε_cond [0.40087–0.94579] (120 valores).**  
**Parte 4.1b (conserva sus presiones):**  
**Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [381.61–621.77] K (120 valores); T_sumidero [278.26–303.48] K (120 valores); x_b [0.50084–0.84732] (120 valores); η_t [0.40268–0.94858] (120 valores); η_p [0.40103–0.9471] (120 valores); ε_HRVG [0.40217–0.94755] (120 valores); ε_reg [0.40228–0.9466] (120 valores); ε_cond [0.40209–0.9474] (120 valores); piso de O2 [278.26–303.48] K (120 valores).**  
**Parte 4.1c (conserva sus presiones y su clima):**  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.23–622.4] K (120 valores); x_b [0.50023–0.84932] (120 valores); η_t [0.40006–0.94769] (120 valores); η_p [0.4036–0.94548] (120 valores); ε_HRVG [0.40016–0.94888] (120 valores); ε_reg [0.40216–0.9486] (120 valores); ε_cond [0.40424–0.94685] (120 valores).**  
**Parte 4.1d (conserva su P_alta y sus temperaturas):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.**  
**Datos barridos: P_baja [211.42–1985.6] kPa (120 valores); x_b [0.50226–0.84794] (120 valores); η_t [0.40325–0.94578] (120 valores); η_p [0.40037–0.94661] (120 valores); ε_HRVG [0.40425–0.94958] (120 valores); ε_reg [0.40094–0.9466] (120 valores); ε_cond [0.40217–0.94675] (120 valores).**  
**Parte 4.1e (conserva su fuente y su x_b):**  
**Datos fijos: T_fuente = 623.15 K; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.28–303.36] K (120 valores); P_alta [2023–4997.5] kPa (120 valores); P_baja [206.13–1999.3] kPa (120 valores); η_t [0.4033–0.94995] (120 valores); η_p [0.40348–0.9476] (120 valores); ε_HRVG [0.40414–0.94874] (120 valores); ε_reg [0.40265–0.94725] (120 valores); ε_cond [0.40127–0.94825] (120 valores); piso de O2 [278.28–303.36] K (119 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 4.1a · conserva sus temperaturas | 120 | 1 | 59 | 4 | 2 | 40 | 15 | 58 | 2 | 53 |
| 4.1b · conserva sus presiones | 120 | 0 | 95 | 0 | 0 | 57 | 38 | 23 | 2 | 66 |
| 4.1c · conserva sus presiones y su clima | 120 | 0 | 84 | 0 | 0 | 29 | 55 | 30 | 6 | 64 |
| 4.1d · conserva su P_alta y sus temperaturas | 120 | 0 | 62 | 6 | 0 | 38 | 18 | 56 | 2 | 57 |
| 4.1e · conserva su fuente y su x_b | 120 | 1 | 82 | 10 | 0 | 55 | 17 | 37 | 0 | 82 |

**Notas:** Filtro: conteo por parte. n = 5 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

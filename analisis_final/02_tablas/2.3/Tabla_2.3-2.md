# Tabla 2.3-2 · Corridas por parte y por clase

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

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.3a · un cambio | 80 | 0 | 24 | 0 | 0 | 24 | 0 | 52 | 4 | 28 |
| 2.3b · ε_HRVG × ε_cond | 60 | 0 | 48 | 0 | 0 | 48 | 0 | 12 | 0 | 48 |
| 2.3c · ε_HRVG × P_baja | 64 | 0 | 62 | 19 | 0 | 43 | 0 | 2 | 0 | 62 |
| 2.3d · T_fuente × ε_cond | 21 | 0 | 20 | 1 | 1 | 18 | 1 | 1 | 0 | 14 |

**Notas:** Filtro: conteo por parte. n = 4 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

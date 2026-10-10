# TAB-M02S-01 · Corridas por subcaso del caso M02S

**Caso(s):** KF-M02S · **Bloque(s):** B05-B1, B05-B2, B05-B3, B05-B4  
**Punto base:** B1 a B4 = cuatro bases distintas (una por subcaso)  
**Bloque B05-B1 (KF-M02S-B1):**  
**Datos fijos: T_fuente = 403 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Bloque B05-B2 (KF-M02S-B2):**  
**Datos fijos: T_fuente = 420 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Bloque B05-B3 (KF-M02S-B3):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.4; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (30 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Bloque B05-B4 (KF-M02S-B4):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (10 valores); piso de O2 [278.15–300.03] K (5 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M02S-B1 | 90 | 0 | 90 | 59 | 59 | 29 | 2 | 0 | 0 | 0 |
| KF-M02S-B2 | 90 | 0 | 90 | 60 | 60 | 29 | 1 | 0 | 0 | 0 |
| KF-M02S-B3 | 90 | 0 | 89 | 34 | 0 | 55 | 0 | 1 | 0 | 89 |
| KF-M02S-B4 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 50 | 0 | 0 |

**Notas:** Filtro: conteo_por_subcaso. n = 4. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

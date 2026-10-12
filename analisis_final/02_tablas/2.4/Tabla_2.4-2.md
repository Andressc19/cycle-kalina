# Tabla 2.4-2 · Corridas por parte y por clase

**Estudio 2.4** · Sumidero más frío · **Partes:** 2.4a, 2.4b, 2.4c, 2.4d  
**Punto base:** 2.4a a 2.4d = cuatro bases distintas (una por parte)  
**Parte 2.4a (fuente a 403 K):**  
**Datos fijos: T_fuente = 403 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4b (fuente a 420 K):**  
**Datos fijos: T_fuente = 420 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4c (ε_HRVG = 0.40 (fuente del profesor)):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.4; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (30 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4d (datos exactos del profesor):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (10 valores); piso de O2 [278.15–300.03] K (5 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.4a · fuente a 403 K | 90 | 0 | 90 | 59 | 59 | 29 | 2 | 0 | 0 | 0 |
| 2.4b · fuente a 420 K | 90 | 0 | 90 | 60 | 60 | 29 | 1 | 0 | 0 | 0 |
| 2.4c · ε_HRVG = 0.40 (fuente del profesor) | 90 | 0 | 89 | 34 | 0 | 55 | 0 | 1 | 0 | 89 |
| 2.4d · datos exactos del profesor | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 50 | 0 | 0 |

**Notas:** Filtro: conteo por parte. n = 4 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

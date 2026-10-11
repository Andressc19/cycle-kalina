# TAB-M10b-01 · Corridas por subcaso del caso M10b

**Caso(s):** KF-M10b · **Bloque(s):** B14-OFATb, B14-MALLA  
**Punto base:** ancla de Húsavík con x_b de 0.30 a 0.70  
**Bloque B14-OFATb (KF-M10b-OFAT):**  
**Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.3; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): x_b [0.3–0.7] (17 valores).**  
**Bloque B14-MALLA (KF-M10b-MALLA):**  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp.**  
**Datos barridos: P_baja [200–700] kPa (6 valores); x_b [0.3–0.7] (9 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M10b-OFAT | 17 | 0 | 8 | 8 | 8 | 0 | 0 | 5 | 4 | 0 |
| KF-M10b-MALLA | 54 | 0 | 30 | 21 | 21 | 9 | 0 | 12 | 12 | 0 |

**Notas:** Filtro: conteo_por_subcaso. n = 2 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

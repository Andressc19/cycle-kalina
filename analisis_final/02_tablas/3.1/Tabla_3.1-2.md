# Tabla 3.1-2 · Corridas por parte y por clase

**Estudio 3.1** · Sensibilidad local alrededor de A*  
**Punto base:** A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa  
**Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.1 | 171 | 0 | 148 | 86 | 86 | 57 | 5 | 17 | 6 | 8 |

**Notas:** Filtro: conteo por parte. n = 1 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

# Tabla 3.2-2 · Corridas por parte y por clase

**Estudio 3.2** · Sensibilidad global (500 puntos)  
**Punto base:** caja estudio 3.2 = las 10 variables barridas dentro de su caja (ver Tabla 3.2-1)  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.2 | 300 | 0 | 266 | 76 | 57 | 181 | 9 | 27 | 7 | 128 |
| 3.2 | 200 | 0 | 186 | 45 | 26 | 127 | 14 | 8 | 6 | 94 |

**Notas:** Filtro: conteo por parte. n = 2 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

# TAB-M04c-01 · Corridas por subcaso del caso M04c

**Caso(s):** KF-M04c · **Bloque(s):** B08  
**Punto base:** caja M4 con P_baja dentro de 1500 a 2500 kPa  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.75–499.83] K (150 valores); T_sumidero [278.28–303.41] K (150 valores); P_alta [2015.7–4995.8] kPa (150 valores); P_baja [1501.3–2494.5] kPa (150 valores); x_b [0.5023–0.84953] (150 valores); η_t [0.75103–0.91919] (150 valores); η_p [0.65119–0.89988] (150 valores); ε_HRVG [0.60089–0.94845] (150 valores); ε_reg [0.60038–0.9477] (150 valores); ε_cond [0.70004–0.94966] (150 valores); piso de O2 [278.28–303.41] K (135 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M04c | 150 | 15 | 120 | 75 | 45 | 43 | 2 | 9 | 6 | 58 |

**Notas:** Filtro: conteo_por_subcaso. n = 1. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

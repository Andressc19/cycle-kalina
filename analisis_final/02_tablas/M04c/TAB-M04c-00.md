# TAB-M04c-00 · Condiciones del caso M04c

**Caso(s):** KF-M04c · **Bloque(s):** B08  
**Punto base:** caja M4 con P_baja dentro de 1500 a 2500 kPa  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.75–499.83] K (150 valores); T_sumidero [278.28–303.41] K (150 valores); P_alta [2015.7–4995.8] kPa (150 valores); P_baja [1501.3–2494.5] kPa (150 valores); x_b [0.5023–0.84953] (150 valores); η_t [0.75103–0.91919] (150 valores); η_p [0.65119–0.89988] (150 valores); ε_HRVG [0.60089–0.94845] (150 valores); ε_reg [0.60038–0.9477] (150 valores); ε_cond [0.70004–0.94966] (150 valores); piso de O2 [278.28–303.41] K (135 valores).**  

| Subcaso | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| KF-M04c | Temperatura de la fuente, T_fuente [K] | Barrida | 380.7 – 499.8 | 150 |  | K |
| KF-M04c | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.3 – 303.4 | 150 |  | K |
| KF-M04c | Presión de alta, P_alta [kPa] | Barrida | 2016 – 4996 | 150 |  | kPa |
| KF-M04c | Presión de baja, P_baja [kPa] | Barrida | 1501 – 2495 | 150 |  | kPa |
| KF-M04c | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida | 0.502 – 0.850 | 150 |  | – |
| KF-M04c | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M04c | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.751 – 0.919 | 150 |  | – |
| KF-M04c | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.651 – 0.900 | 150 |  | – |
| KF-M04c | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.601 – 0.948 | 150 |  | – |
| KF-M04c | Efectividad del regenerador, ε_reg [–] | Barrida | 0.600 – 0.948 | 150 |  | – |
| KF-M04c | Efectividad del condensador, ε_cond [–] | Barrida | 0.700 – 0.950 | 150 |  | – |
| KF-M04c | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.3 – 303.4 | 135 |  | K |
| KF-M04c | motor de propiedades | Fija | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 13. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

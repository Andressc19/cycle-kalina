# Tabla 3.3-1 · Condiciones: qué quedó fijo y qué se barrió

**Estudio 3.3** · P_baja alta (1500–2500 kPa)  
**Punto base:** caja estudio 3.2 con P_baja dentro de 1500 a 2500 kPa  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.75–499.83] K (150 valores); T_sumidero [278.28–303.41] K (150 valores); P_alta [2015.7–4995.8] kPa (150 valores); P_baja [1501.3–2494.5] kPa (150 valores); x_b [0.5023–0.84953] (150 valores); η_t [0.75103–0.91919] (150 valores); η_p [0.65119–0.89988] (150 valores); ε_HRVG [0.60089–0.94845] (150 valores); ε_reg [0.60038–0.9477] (150 valores); ε_cond [0.70004–0.94966] (150 valores); piso de O2 [278.28–303.41] K (135 valores).**  

| Parte | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| 3.3 | Temperatura de la fuente, T_fuente [K] | Barrida | 380.7 – 499.8 | 150 |  | K |
| 3.3 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.3 – 303.4 | 150 |  | K |
| 3.3 | Presión de alta, P_alta [kPa] | Barrida | 2016 – 4996 | 150 |  | kPa |
| 3.3 | Presión de baja, P_baja [kPa] | Barrida | 1501 – 2495 | 150 |  | kPa |
| 3.3 | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida | 0.502 – 0.850 | 150 |  | – |
| 3.3 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 3.3 | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.751 – 0.919 | 150 |  | – |
| 3.3 | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.651 – 0.900 | 150 |  | – |
| 3.3 | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.601 – 0.948 | 150 |  | – |
| 3.3 | Efectividad del regenerador, ε_reg [–] | Barrida | 0.600 – 0.948 | 150 |  | – |
| 3.3 | Efectividad del condensador, ε_cond [–] | Barrida | 0.700 – 0.950 | 150 |  | – |
| 3.3 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.3 – 303.4 | 135 |  | K |
| 3.3 | motor de propiedades | Fija | teqp |  |  | – |

**Notas:** Filtro: cada parte y cada variable. n = 13 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

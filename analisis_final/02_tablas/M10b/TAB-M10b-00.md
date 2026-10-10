# TAB-M10b-00 · Condiciones del caso M10b

**Caso(s):** KF-M10b · **Bloque(s):** B14-OFATb, B14-MALLA  
**Punto base:** ancla de Húsavík con x_b de 0.30 a 0.70  
**Bloque B14-OFATb (KF-M10b-OFAT):**  
**Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.3; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): x_b [0.3–0.7] (17 valores).**  
**Bloque B14-MALLA (KF-M10b-MALLA):**  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp.**  
**Datos barridos: P_baja [200–700] kPa (6 valores); x_b [0.3–0.7] (9 valores).**  

| Subcaso | Variable | Estado | Valor en el punto base | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|---|
| KF-M10b-OFAT | Temperatura de la fuente, T_fuente [K] | Fija | 394.1 | 394.15 |  | no | K |
| KF-M10b-OFAT | Temperatura del sumidero, T_sumidero [K] | Fija | 278.1 | 278.15 |  | no | K |
| KF-M10b-OFAT | Presión de alta, P_alta [kPa] | Fija | 3300 | 3300.0 |  | no | kPa |
| KF-M10b-OFAT | Presión de baja, P_baja [kPa] | Fija | 690.0 | 690.0 |  | no | kPa |
| KF-M10b-OFAT | Fracción de amoníaco de la mezcla base, x_b [–] | Una a la vez | 0.300 | 0.300 – 0.700 | 17 |  | – |
| KF-M10b-OFAT | Flujo másico base, m_b [kg/s] | Fija | 1 | 1.0 |  | sí | kg/s |
| KF-M10b-OFAT | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.900 | 0.9 |  | no | – |
| KF-M10b-OFAT | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.800 | 0.8 |  | no | – |
| KF-M10b-OFAT | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.850 | 0.85 |  | sí | – |
| KF-M10b-OFAT | Efectividad del regenerador, ε_reg [–] | Fija | 0.750 | 0.75 |  | sí | – |
| KF-M10b-OFAT | Efectividad del condensador, ε_cond [–] | Fija | 0.950 | 0.95 |  | no | – |
| KF-M10b-OFAT | Piso de O2 (T de diseño de la bomba) [K] | Fija | 283.1 | 283.15 |  | no | K |
| KF-M10b-OFAT | motor de propiedades | Fija |  | teqp |  |  | – |
| KF-M10b-MALLA | Temperatura de la fuente, T_fuente [K] | Fija |  | 394.15 |  | no | K |
| KF-M10b-MALLA | Temperatura del sumidero, T_sumidero [K] | Fija |  | 278.15 |  | no | K |
| KF-M10b-MALLA | Presión de alta, P_alta [kPa] | Fija |  | 3300.0 |  | no | kPa |
| KF-M10b-MALLA | Presión de baja, P_baja [kPa] | Barrida |  | 200.0 – 700.0 | 6 |  | kPa |
| KF-M10b-MALLA | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida |  | 0.300 – 0.700 | 9 |  | – |
| KF-M10b-MALLA | Flujo másico base, m_b [kg/s] | Fija |  | 1.0 |  | sí | kg/s |
| KF-M10b-MALLA | Eficiencia isentrópica de la turbina, η_t [–] | Fija |  | 0.9 |  | no | – |
| KF-M10b-MALLA | Eficiencia isentrópica de la bomba, η_p [–] | Fija |  | 0.8 |  | no | – |
| KF-M10b-MALLA | Efectividad del generador de vapor, ε_HRVG [–] | Fija |  | 0.85 |  | sí | – |
| KF-M10b-MALLA | Efectividad del regenerador, ε_reg [–] | Fija |  | 0.75 |  | sí | – |
| KF-M10b-MALLA | Efectividad del condensador, ε_cond [–] | Fija |  | 0.95 |  | no | – |
| KF-M10b-MALLA | Piso de O2 (T de diseño de la bomba) [K] | Fija |  | 283.15 |  | no | K |
| KF-M10b-MALLA | motor de propiedades | Fija |  | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 26. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

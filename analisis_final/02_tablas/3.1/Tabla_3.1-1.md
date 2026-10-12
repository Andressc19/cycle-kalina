# Tabla 3.1-1 · Condiciones: qué quedó fijo y qué se barrió

**Estudio 3.1** · Sensibilidad local alrededor de A*  
**Punto base:** A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa  
**Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.**  
**Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).**  

| Parte | Variable | Estado | Valor en el punto base | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|---|
| 3.1 | Temperatura de la fuente, T_fuente [K] | Una a la vez | 403.0 | 340.0 – 623.1 | 18 |  | K |
| 3.1 | Temperatura del sumidero, T_sumidero [K] | Una a la vez | 300.0 | 283.1 – 303.6 | 18 |  | K |
| 3.1 | Presión de alta, P_alta [kPa] | Una a la vez | 3000 | 1000 – 10000 | 18 |  | kPa |
| 3.1 | Presión de baja, P_baja [kPa] | Una a la vez | 563.6 | 150.0 – 1500 | 18 |  | kPa |
| 3.1 | Fracción de amoníaco de la mezcla base, x_b [–] | Una a la vez | 0.500 | 0.300 – 0.900 | 18 |  | – |
| 3.1 | Flujo másico base, m_b [kg/s] | Fija | 1 | 1.0 |  | sí | kg/s |
| 3.1 | Eficiencia isentrópica de la turbina, η_t [–] | Una a la vez | 0.850 | 0.400 – 0.950 | 18 |  | – |
| 3.1 | Eficiencia isentrópica de la bomba, η_p [–] | Una a la vez | 0.750 | 0.400 – 0.950 | 18 |  | – |
| 3.1 | Efectividad del generador de vapor, ε_HRVG [–] | Una a la vez | 0.850 | 0.400 – 0.950 | 18 |  | – |
| 3.1 | Efectividad del regenerador, ε_reg [–] | Una a la vez | 0.750 | 0.400 – 0.950 | 18 |  | – |
| 3.1 | Efectividad del condensador, ε_cond [–] | Una a la vez | 0.800 | 0.400 – 0.950 | 18 |  | – |
| 3.1 | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  |  | K |
| 3.1 | motor de propiedades | Fija |  | teqp |  |  | – |

**Notas:** Filtro: cada parte y cada variable. n = 13 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

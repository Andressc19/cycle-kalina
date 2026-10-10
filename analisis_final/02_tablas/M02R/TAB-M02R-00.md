# TAB-M02R-00 · Condiciones del caso M02R

**Caso(s):** KF-M02R · **Bloque(s):** B04-n1, B04-n2a, B04-n2b, B04-n3  
**Punto base:** PP = punto del profesor con η/ε dentro de [0.40, 0.95]  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; motor = teqp.**  
**Datos barridos: T_fuente [403–560] K (7 valores); P_baja [400–2000] kPa (20 valores); eta_t [0.4–0.95] (12 valores); eta_p [0.4–0.95] (12 valores); eps_hrvg [0.4–0.95] (32 valores); eps_reg [0.4–0.95] (12 valores); eps_cond [0.4–0.95] (12 valores).**  

| Subcaso | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| KF-M02R-n1 | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| KF-M02R-n1 | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| KF-M02R-n1 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02R-n1 | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| KF-M02R-n1 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02R-n1 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02R-n1 | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| KF-M02R-n1 | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| KF-M02R-n1 | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.950 | 32 |  | – |
| KF-M02R-n1 | Efectividad del regenerador, ε_reg [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| KF-M02R-n1 | Efectividad del condensador, ε_cond [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| KF-M02R-n1 | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| KF-M02R-n1 | motor | Fija | teqp |  |  | – |
| KF-M02R-n2a | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| KF-M02R-n2a | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| KF-M02R-n2a | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02R-n2a | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| KF-M02R-n2a | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02R-n2a | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02R-n2a | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02R-n2a | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n2a | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.800 | 5 |  | – |
| KF-M02R-n2a | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n2a | Efectividad del condensador, ε_cond [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| KF-M02R-n2a | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| KF-M02R-n2a | motor | Fija | teqp |  |  | – |
| KF-M02R-n2b | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| KF-M02R-n2b | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| KF-M02R-n2b | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02R-n2b | Presión de baja, P_baja [kPa] | Barrida | 400.0 – 2000 | 20 |  | kPa |
| KF-M02R-n2b | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02R-n2b | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02R-n2b | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02R-n2b | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n2b | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.700 | 4 |  | – |
| KF-M02R-n2b | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n2b | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| KF-M02R-n2b | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| KF-M02R-n2b | motor | Fija | teqp |  |  | – |
| KF-M02R-n3 | Temperatura de la fuente, T_fuente [K] | Barrida | 403.0 – 560.0 | 7 |  | K |
| KF-M02R-n3 | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| KF-M02R-n3 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02R-n3 | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| KF-M02R-n3 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02R-n3 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02R-n3 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02R-n3 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n3 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| KF-M02R-n3 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02R-n3 | Efectividad del condensador, ε_cond [–] | Barrida | 0.850 – 0.950 | 3 |  | – |
| KF-M02R-n3 | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| KF-M02R-n3 | motor | Fija | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 52. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

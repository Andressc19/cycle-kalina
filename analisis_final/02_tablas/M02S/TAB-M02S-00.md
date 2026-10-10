# TAB-M02S-00 · Condiciones del caso M02S

**Caso(s):** KF-M02S · **Bloque(s):** B05-B1, B05-B2, B05-B3, B05-B4  
**Punto base:** B1 a B4 = cuatro bases distintas (una por subcaso)  
**Datos fijos: P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; eta_t = 0.85; eta_p = 0.75; eps_reg = 0.75; eps_cond = 0.8; motor = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (30 valores); T_amb_diseno [278.15–300.03] K (5 valores).**  

| Subcaso | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| KF-M02S-B1 | Temperatura de la fuente, T_fuente [K] | Fija | 403.0 |  | no | K |
| KF-M02S-B1 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B1 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02S-B1 | Presión de baja, P_baja [kPa] | Barrida | 150.0 – 1500 | 28 |  | kPa |
| KF-M02S-B1 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02S-B1 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02S-B1 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B1 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B1 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B1 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B1 | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| KF-M02S-B1 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B1 | motor | Fija | teqp |  |  | – |
| KF-M02S-B2 | Temperatura de la fuente, T_fuente [K] | Fija | 420.0 |  | no | K |
| KF-M02S-B2 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B2 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02S-B2 | Presión de baja, P_baja [kPa] | Barrida | 150.0 – 1500 | 28 |  | kPa |
| KF-M02S-B2 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02S-B2 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02S-B2 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B2 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B2 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B2 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B2 | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| KF-M02S-B2 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B2 | motor | Fija | teqp |  |  | – |
| KF-M02S-B3 | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| KF-M02S-B3 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B3 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02S-B3 | Presión de baja, P_baja [kPa] | Barrida | 150.0 – 1500 | 30 |  | kPa |
| KF-M02S-B3 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02S-B3 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02S-B3 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B3 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B3 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.4 |  | no | – |
| KF-M02S-B3 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B3 | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| KF-M02S-B3 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B3 | motor | Fija | teqp |  |  | – |
| KF-M02S-B4 | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| KF-M02S-B4 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B4 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M02S-B4 | Presión de baja, P_baja [kPa] | Barrida | 150.0 – 1500 | 10 |  | kPa |
| KF-M02S-B4 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M02S-B4 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M02S-B4 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B4 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B4 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| KF-M02S-B4 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M02S-B4 | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| KF-M02S-B4 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 5 |  | K |
| KF-M02S-B4 | motor | Fija | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 52. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

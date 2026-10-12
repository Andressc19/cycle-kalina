# Tabla 2.3-1 · Condiciones: qué quedó fijo y qué se barrió

**Estudio 2.3** · Dos cambios con η y ε en 0.40–0.95 · **Partes:** 2.3a, 2.3b, 2.3c, 2.3d  
**Punto base:** PP = punto del profesor con η/ε dentro de [0.40, 0.95]  
**Parte 2.3a (un cambio):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: η_t [0.4–0.95] (12 valores); η_p [0.4–0.95] (12 valores); ε_HRVG [0.4–0.95] (32 valores); ε_reg [0.4–0.95] (12 valores); ε_cond [0.4–0.95] (12 valores).**  
**Parte 2.3b (ε_HRVG × ε_cond):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: ε_HRVG [0.4–0.8] (5 valores); ε_cond [0.4–0.95] (12 valores).**  
**Parte 2.3c (ε_HRVG × P_baja):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: P_baja [400–2000] kPa (20 valores); ε_HRVG [0.4–0.7] (4 valores).**  
**Parte 2.3d (T_fuente × ε_cond):**  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [403–560] K (7 valores); ε_cond [0.85–0.95] (3 valores).**  

| Parte | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| 2.3a · un cambio | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| 2.3a · un cambio | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| 2.3a · un cambio | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| 2.3a · un cambio | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| 2.3a · un cambio | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| 2.3a · un cambio | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 2.3a · un cambio | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| 2.3a · un cambio | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| 2.3a · un cambio | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.950 | 32 |  | – |
| 2.3a · un cambio | Efectividad del regenerador, ε_reg [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| 2.3a · un cambio | Efectividad del condensador, ε_cond [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| 2.3a · un cambio | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| 2.3a · un cambio | motor de propiedades | Fija | teqp |  |  | – |
| 2.3b · ε_HRVG × ε_cond | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| 2.3b · ε_HRVG × ε_cond | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| 2.3b · ε_HRVG × ε_cond | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| 2.3b · ε_HRVG × ε_cond | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| 2.3b · ε_HRVG × ε_cond | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| 2.3b · ε_HRVG × ε_cond | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 2.3b · ε_HRVG × ε_cond | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| 2.3b · ε_HRVG × ε_cond | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| 2.3b · ε_HRVG × ε_cond | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.800 | 5 |  | – |
| 2.3b · ε_HRVG × ε_cond | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| 2.3b · ε_HRVG × ε_cond | Efectividad del condensador, ε_cond [–] | Barrida | 0.400 – 0.950 | 12 |  | – |
| 2.3b · ε_HRVG × ε_cond | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| 2.3b · ε_HRVG × ε_cond | motor de propiedades | Fija | teqp |  |  | – |
| 2.3c · ε_HRVG × P_baja | Temperatura de la fuente, T_fuente [K] | Fija | 623.15 |  | sí | K |
| 2.3c · ε_HRVG × P_baja | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| 2.3c · ε_HRVG × P_baja | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| 2.3c · ε_HRVG × P_baja | Presión de baja, P_baja [kPa] | Barrida | 400.0 – 2000 | 20 |  | kPa |
| 2.3c · ε_HRVG × P_baja | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| 2.3c · ε_HRVG × P_baja | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 2.3c · ε_HRVG × P_baja | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| 2.3c · ε_HRVG × P_baja | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| 2.3c · ε_HRVG × P_baja | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.400 – 0.700 | 4 |  | – |
| 2.3c · ε_HRVG × P_baja | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| 2.3c · ε_HRVG × P_baja | Efectividad del condensador, ε_cond [–] | Fija | 0.8 |  | sí | – |
| 2.3c · ε_HRVG × P_baja | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| 2.3c · ε_HRVG × P_baja | motor de propiedades | Fija | teqp |  |  | – |
| 2.3d · T_fuente × ε_cond | Temperatura de la fuente, T_fuente [K] | Barrida | 403.0 – 560.0 | 7 |  | K |
| 2.3d · T_fuente × ε_cond | Temperatura del sumidero, T_sumidero [K] | Fija | 300.032917 |  | sí | K |
| 2.3d · T_fuente × ε_cond | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| 2.3d · T_fuente × ε_cond | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| 2.3d · T_fuente × ε_cond | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| 2.3d · T_fuente × ε_cond | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 2.3d · T_fuente × ε_cond | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| 2.3d · T_fuente × ε_cond | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| 2.3d · T_fuente × ε_cond | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| 2.3d · T_fuente × ε_cond | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| 2.3d · T_fuente × ε_cond | Efectividad del condensador, ε_cond [–] | Barrida | 0.850 – 0.950 | 3 |  | – |
| 2.3d · T_fuente × ε_cond | Piso de O2 (T de diseño de la bomba) [K] | Sin dato |  |  |  | K |
| 2.3d · T_fuente × ε_cond | motor de propiedades | Fija | teqp |  |  | – |

**Notas:** Filtro: cada parte y cada variable. n = 52 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

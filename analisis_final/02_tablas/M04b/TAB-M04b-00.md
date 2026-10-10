# TAB-M04b-00 · Condiciones del caso M04b

**Caso(s):** KF-M04b · **Bloque(s):** B07  
**Punto base:** caja M4 = las 10 variables barridas dentro de su caja (ver TAB-M04-00)  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.29–499.53] K (200 valores); T_sumidero [278.18–303.47] K (200 valores); P_alta [2009.9–4986.6] kPa (200 valores); P_baja [304.74–1497.2] kPa (200 valores); x_b [0.50012–0.84879] (200 valores); η_t [0.75036–0.91969] (200 valores); η_p [0.65092–0.89886] (200 valores); ε_HRVG [0.60061–0.94834] (200 valores); ε_reg [0.60167–0.94916] (200 valores); ε_cond [0.70052–0.94921] (200 valores); piso de O2 [278.18–303.47] K (200 valores).**  

| Subcaso | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| KF-M04b | Temperatura de la fuente, T_fuente [K] | Barrida | 380.3 – 499.5 | 200 |  | K |
| KF-M04b | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.2 – 303.5 | 200 |  | K |
| KF-M04b | Presión de alta, P_alta [kPa] | Barrida | 2010 – 4987 | 200 |  | kPa |
| KF-M04b | Presión de baja, P_baja [kPa] | Barrida | 304.7 – 1497 | 200 |  | kPa |
| KF-M04b | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida | 0.500 – 0.849 | 200 |  | – |
| KF-M04b | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M04b | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.750 – 0.920 | 200 |  | – |
| KF-M04b | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.651 – 0.899 | 200 |  | – |
| KF-M04b | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.601 – 0.948 | 200 |  | – |
| KF-M04b | Efectividad del regenerador, ε_reg [–] | Barrida | 0.602 – 0.949 | 200 |  | – |
| KF-M04b | Efectividad del condensador, ε_cond [–] | Barrida | 0.701 – 0.949 | 200 |  | – |
| KF-M04b | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.2 – 303.5 | 200 |  | K |
| KF-M04b | motor de propiedades | Fija | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 13. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

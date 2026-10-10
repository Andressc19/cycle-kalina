# TAB-M05c-00 · Condiciones del caso M05c

**Caso(s):** KF-M05c · **Bloque(s):** B10  
**Punto base:** PP = punto del profesor con P_alta y P_baja fijas  
**Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; eta_t = 0.85; eta_p = 0.75; eps_hrvg = 0.85; eps_reg = 0.75; motor = teqp.**  
**Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); eps_cond [0.85–0.95] (5 valores); T_amb_diseno [278.15–300.03] K (3 valores).**  

| Subcaso | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| KF-M05c | Temperatura de la fuente, T_fuente [K] | Barrida | 385.0 – 410.0 | 11 |  | K |
| KF-M05c | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 3 |  | K |
| KF-M05c | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| KF-M05c | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| KF-M05c | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| KF-M05c | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| KF-M05c | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| KF-M05c | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| KF-M05c | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| KF-M05c | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| KF-M05c | Efectividad del condensador, ε_cond [–] | Barrida | 0.850 – 0.950 | 5 |  | – |
| KF-M05c | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 3 |  | K |
| KF-M05c | motor | Fija | teqp |  |  | – |

**Notas:** Filtro: condiciones_por_subcaso (cada subcaso y variable). n = 13. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

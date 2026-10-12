# Tabla 4.2-1 · Condiciones: qué quedó fijo y qué se barrió

**Estudio 4.2** · Mapa con las presiones del profesor  
**Punto base:** PP = punto del profesor con P_alta y P_baja fijas  
**Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); ε_cond [0.85–0.95] (5 valores); piso de O2 [278.15–300.03] K (3 valores).**  

| Parte | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| 4.2 | Temperatura de la fuente, T_fuente [K] | Barrida | 385.0 – 410.0 | 11 |  | K |
| 4.2 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.1 – 300.0 | 3 |  | K |
| 4.2 | Presión de alta, P_alta [kPa] | Fija | 3000.0 |  | sí | kPa |
| 4.2 | Presión de baja, P_baja [kPa] | Fija | 400.0 |  | sí | kPa |
| 4.2 | Fracción de amoníaco de la mezcla base, x_b [–] | Fija | 0.5 |  | sí | – |
| 4.2 | Flujo másico base, m_b [kg/s] | Fija | 1.0 |  | sí | kg/s |
| 4.2 | Eficiencia isentrópica de la turbina, η_t [–] | Fija | 0.85 |  | sí | – |
| 4.2 | Eficiencia isentrópica de la bomba, η_p [–] | Fija | 0.75 |  | sí | – |
| 4.2 | Efectividad del generador de vapor, ε_HRVG [–] | Fija | 0.85 |  | sí | – |
| 4.2 | Efectividad del regenerador, ε_reg [–] | Fija | 0.75 |  | sí | – |
| 4.2 | Efectividad del condensador, ε_cond [–] | Barrida | 0.850 – 0.950 | 5 |  | – |
| 4.2 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.1 – 300.0 | 3 |  | K |
| 4.2 | motor de propiedades | Fija | teqp |  |  | – |

**Notas:** Filtro: cada parte y cada variable. n = 13 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/condiciones_por_subcaso.csv.

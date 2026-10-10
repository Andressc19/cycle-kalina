# TAB-M05c-01 · Corridas por subcaso del caso M05c

**Caso(s):** KF-M05c · **Bloque(s):** B10  
**Punto base:** PP = punto del profesor con P_alta y P_baja fijas  
**Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); ε_cond [0.85–0.95] (5 valores); piso de O2 [278.15–300.03] K (3 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M05c | 165 | 0 | 149 | 104 | 104 | 30 | 15 | 1 | 15 | 0 |

**Notas:** Filtro: conteo_por_subcaso. n = 1. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

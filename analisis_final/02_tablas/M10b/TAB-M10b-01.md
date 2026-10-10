# TAB-M10b-01 · Corridas por subcaso del caso M10b

**Caso(s):** KF-M10b · **Bloque(s):** B14-OFATb, B14-MALLA  
**Punto base:** Húsavík con x_b bajo  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; eta_t = 0.9; eta_p = 0.8; eps_hrvg = 0.85; eps_reg = 0.75; eps_cond = 0.95; T_amb_diseno = 283.15 K; motor = teqp.**  
**Datos barridos: P_baja [200–700] kPa (6 valores); x_b [0.3–0.7] (17 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M10b-OFAT | 17 | 0 | 8 | 8 | 8 | 0 | 0 | 5 | 4 | 0 |
| KF-M10b-MALLA | 54 | 0 | 30 | 21 | 21 | 9 | 0 | 12 | 12 | 0 |

**Notas:** Filtro: conteo_por_subcaso. n = 2. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

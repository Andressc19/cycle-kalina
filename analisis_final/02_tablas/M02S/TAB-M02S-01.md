# TAB-M02S-01 · Corridas por subcaso del caso M02S

**Caso(s):** KF-M02S · **Bloque(s):** B05-B1, B05-B2, B05-B3, B05-B4  
**Punto base:** B1 a B4 = cuatro bases distintas (una por subcaso)  
**Datos fijos: P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; eta_t = 0.85; eta_p = 0.75; eps_reg = 0.75; eps_cond = 0.8; motor = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (30 valores); T_amb_diseno [278.15–300.03] K (5 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M02S-B1 | 90 | 0 | 90 | 59 | 59 | 29 | 2 | 0 | 0 | 0 |
| KF-M02S-B2 | 90 | 0 | 90 | 60 | 60 | 29 | 1 | 0 | 0 | 0 |
| KF-M02S-B3 | 90 | 0 | 89 | 34 | 0 | 55 | 0 | 1 | 0 | 89 |
| KF-M02S-B4 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 50 | 0 | 0 |

**Notas:** Filtro: conteo_por_subcaso. n = 4. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

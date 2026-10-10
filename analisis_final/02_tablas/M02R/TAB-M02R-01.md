# TAB-M02R-01 · Corridas por subcaso del caso M02R

**Caso(s):** KF-M02R · **Bloque(s):** B04-n1, B04-n2a, B04-n2b, B04-n3  
**Punto base:** PP = punto del profesor con η/ε dentro de [0.40, 0.95]  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; motor = teqp.**  
**Datos barridos: T_fuente [403–560] K (7 valores); P_baja [400–2000] kPa (20 valores); eta_t [0.4–0.95] (12 valores); eta_p [0.4–0.95] (12 valores); eps_hrvg [0.4–0.95] (32 valores); eps_reg [0.4–0.95] (12 valores); eps_cond [0.4–0.95] (12 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M02R-n1 | 80 | 0 | 24 | 0 | 0 | 24 | 0 | 52 | 4 | 28 |
| KF-M02R-n2a | 60 | 0 | 48 | 0 | 0 | 48 | 0 | 12 | 0 | 48 |
| KF-M02R-n2b | 64 | 0 | 62 | 19 | 0 | 43 | 0 | 2 | 0 | 62 |
| KF-M02R-n3 | 21 | 0 | 20 | 1 | 1 | 18 | 1 | 1 | 0 | 14 |

**Notas:** Filtro: conteo_por_subcaso. n = 4. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

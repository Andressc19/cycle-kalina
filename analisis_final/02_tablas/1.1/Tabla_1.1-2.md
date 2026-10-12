# Tabla 1.1-2 · Corridas por parte y por clase

**Estudio 1.1** · Repetir el caso del profesor · **Partes:** 1.1b, 1.1a, 1.1c, 1.1d  
**Punto base:** PP = punto del profesor (los 11 datos del enunciado; ver GLOSARIO)  
**Datos fijos: T_fuente = 623.15 K; P_baja = 400 kPa; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8.**  
**Datos barridos: T_sumidero [297.95–303.55] K (23 valores); P_alta [2000–4000] kPa (9 valores); x_b [0.4–0.7] (7 valores); motor de propiedades (2 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1b · solo P_alta | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |
| 1.1a · punto del profesor | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| 1.1c · solo x_b | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 |
| 1.1d · temperatura ambiente hora a hora | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 24 | 0 | 0 |

**Notas:** Filtro: conteo por parte. n = 4 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

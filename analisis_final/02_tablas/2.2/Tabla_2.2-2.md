# Tabla 2.2-2 · Corridas por parte y por clase

**Estudio 2.2** · Dos cambios · **Partes:** 2.2a, 2.2b  
**Punto base:** PP = punto del profesor salvo el par movido  
**Parte 2.2a (conservar la fuente (ε_HRVG × P_baja)):**  
**Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: P_baja [400–2000] kPa (12 valores); ε_HRVG [0.75–0.81] (3 valores).**  
**Parte 2.2b (bajar la fuente (T_fuente × P_baja)):**  
**Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380–560] K (9 valores); P_baja [400–2000] kPa (32 valores).**  

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.2a · conservar la fuente (ε_HRVG × P_baja) | 36 | 0 | 36 | 0 | 0 | 36 | 0 | 0 | 0 | 36 |
| 2.2b · bajar la fuente (T_fuente × P_baja) | 144 | 0 | 129 | 59 | 48 | 70 | 0 | 3 | 12 | 69 |

**Notas:** Filtro: conteo por parte. n = 2 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.

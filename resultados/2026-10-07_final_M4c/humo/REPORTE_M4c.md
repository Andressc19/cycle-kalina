# REPORTE M4c — dónde termina KALINA al subir P_baja
## 1. La pregunta
¿En qué P_baja se acaba el KALINA y qué criterio es el que lo corta? ¿Y cómo depende ese techo de P_alta?
## 2. Qué se hizo
- **LHS de 150 puntos** con `LatinHypercube(d=10, seed=20261008)` sobre la caja de M4 pero con **P_baja ∈ [1500, 2500] kPa** (todo lo demás: T_fuente, T_sumidero, P_alta, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond); `id_muestra` de 500 a 649.
- Puntos con `P_baja ≥ P_alta − 300` sin evaluar (`omitido=True`): **0 omitidos**, 3 evaluados. Motor `teqp`, **piso de O2 = T_sumidero**, 7 procesos en el mismo pool que M5c. Punto genuino = KALINA, CORREGIBLE o INVIABLE.
- Apoyo: los 500 de **M4 + M4b** (`leer_union()`), cuya caja llega solo hasta P_baja = 1500 kPa: sirven para el piso 1300–1500 y para el techo por P_alta.
## 3. Dónde termina KALINA (franjas de 100 kPa)
**M4c no produjo ningún KALINA**: con P_baja ∈ [1500, 2500] el ciclo ya no es viable en ningún punto.

| franja P_baja (kPa) | fuente | n | KALINA | % KALINA | P_baja máx KALINA |
|---|---|---|---|---|---|
| 1300–1400 | M4+M4b | 42 | 15 | 35.7 | 1384.32 |
| 1400–1500 | M4+M4b | 42 | 21 | 50.0 | 1493.2 |
| 1500–1600 | M4c | 0 | 0 | n/d | n/d |
| 1600–1700 | M4c | 0 | 0 | n/d | n/d |
| 1700–1800 | M4c | 1 | 0 | 0.0 | n/d |
| 1800–1900 | M4c | 0 | 0 | n/d | n/d |
| 1900–2000 | M4c | 0 | 0 | n/d | n/d |
| 2000–2100 | M4c | 0 | 0 | n/d | n/d |
| 2100–2200 | M4c | 1 | 0 | 0.0 | n/d |
| 2200–2300 | M4c | 0 | 0 | n/d | n/d |
| 2300–2400 | M4c | 1 | 0 | 0.0 | n/d |
| 2400–2500 | M4c | 0 | 0 | n/d | n/d |
## 4. Qué criterio la corta
Conteo de `codigos_falla` sobre los genuinos **no KALINA** de M4c (0 por encima de n/d kPa y 0 hasta ese valor):
- **Por encima del techo:** sin puntos no KALINA genuinos · **Dentro de la zona KALINA:** sin puntos no KALINA genuinos.
## 5. Cómo cambia el techo con P_alta (las 6 franjas de M4b, sobre M4+M4b+M4c)
| franja P_alta (kPa) | n | KALINA | % KALINA | P_baja máx KALINA |
|---|---|---|---|---|
| 2000–2500 | 83 | 18 | 21.7 | 1459.36 |
| 2500–3000 | 84 | 16 | 19.0 | 1440.71 |
| 3000–3500 | 84 | 21 | 25.0 | 1416.58 |
| 3500–4000 | 84 | 29 | 34.5 | 1479.81 |
| 4000–4500 | 85 | 18 | 21.2 | 1493.2 |
| 4500–5000 | 83 | 19 | 22.9 | 1464.87 |
- Franjas de 100 kPa con al menos un KALINA: 1300–1400 … 1400–1500 kPa.
## 6. La ventana completa de P_baja (300 → 2500 kPa)
- **Piso:** P_baja mínimo de cualquier KALINA de M4+M4b+M4c = **546.972 kPa**; **techo:** máximo = **1493.2 kPa**.
- Franjas de 100 kPa con KALINA en algún momento: 2 de 12 (lista completa en `m4c_techo.csv`).
- ¿Sigue KALINA más allá de 1500 kPa? no: M4c no dio ningún KALINA en [1500, 2500].
## 7. Lo que no se sabe
- El LHS tiene 150 puntos en una caja de 10 dimensiones: el techo está acotado por los puntos muestreados, no es una frontera calculada.
- Los 0 puntos omitidos no informan nada y no entran en ningún %; y la franja 1300–1500 kPa viene de M4 + M4b (dos LHS distintos), % no comparable punto a punto con M4c.

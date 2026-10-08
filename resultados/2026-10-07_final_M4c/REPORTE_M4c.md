# REPORTE M4c — dónde termina KALINA al subir P_baja
## 1. La pregunta
¿En qué P_baja se acaba el KALINA y qué criterio es el que lo corta? ¿Y cómo depende ese techo de P_alta?
## 2. Qué se hizo
- **LHS de 150 puntos** con `LatinHypercube(d=10, seed=20261008)` sobre la caja de M4 pero con **P_baja ∈ [1500, 2500] kPa** (todo lo demás: T_fuente, T_sumidero, P_alta, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond); `id_muestra` de 500 a 649.
- Puntos con `P_baja ≥ P_alta − 300` sin evaluar (`omitido=True`): **15 omitidos**, 135 evaluados. Motor `teqp`, **piso de O2 = T_sumidero**, 7 procesos en el mismo pool que M5c. Punto genuino = KALINA, CORREGIBLE o INVIABLE.
- Apoyo: los 500 de **M4 + M4b** (`leer_union()`), cuya caja llega solo hasta P_baja = 1500 kPa: sirven para el piso 1300–1500 y para el techo por P_alta.
## 3. Dónde termina KALINA (franjas de 100 kPa)
El KALINA de mayor P_baja con M4c es **2494.53 kPa** (75 de 135 puntos de M4c).

| franja P_baja (kPa) | fuente | n | KALINA | % KALINA | P_baja máx KALINA |
|---|---|---|---|---|---|
| 1300–1400 | M4+M4b | 42 | 15 | 35.7 | 1384.32 |
| 1400–1500 | M4+M4b | 42 | 21 | 50.0 | 1493.2 |
| 1500–1600 | M4c | 15 | 5 | 33.3 | 1593.04 |
| 1600–1700 | M4c | 15 | 8 | 53.3 | 1655.51 |
| 1700–1800 | M4c | 14 | 7 | 50.0 | 1759.83 |
| 1800–1900 | M4c | 15 | 10 | 66.7 | 1896.95 |
| 1900–2000 | M4c | 13 | 9 | 69.2 | 1981.4 |
| 2000–2100 | M4c | 13 | 8 | 61.5 | 2096.18 |
| 2100–2200 | M4c | 14 | 7 | 50.0 | 2198.69 |
| 2200–2300 | M4c | 14 | 5 | 35.7 | 2292.55 |
| 2300–2400 | M4c | 10 | 7 | 70.0 | 2388.23 |
| 2400–2500 | M4c | 12 | 9 | 75.0 | 2494.53 |
## 4. Qué criterio la corta
Conteo de `codigos_falla` sobre los genuinos **no KALINA** de M4c (0 por encima de 2494.53 kPa y 45 hasta ese valor):
- **Por encima del techo:** sin puntos no KALINA genuinos · **Dentro de la zona KALINA:** `O2` (44 de 45), `O3` (1 de 45), `O5` (1 de 45).
## 5. Cómo cambia el techo con P_alta (las 6 franjas de M4b, sobre M4+M4b+M4c)
| franja P_alta (kPa) | n | KALINA | % KALINA | P_baja máx KALINA |
|---|---|---|---|---|
| 2000–2500 | 94 | 23 | 24.5 | 1921.43 |
| 2500–3000 | 107 | 29 | 27.1 | 2423.02 |
| 3000–3500 | 109 | 34 | 31.2 | 2479.36 |
| 3500–4000 | 108 | 43 | 39.8 | 2494.53 |
| 4000–4500 | 109 | 32 | 29.4 | 2418.82 |
| 4500–5000 | 108 | 35 | 32.4 | 2482.36 |
- Franjas de 100 kPa con al menos un KALINA: 1300–1400 … 2400–2500 kPa.
## 6. La ventana completa de P_baja (300 → 2500 kPa)
- **Piso:** P_baja mínimo de cualquier KALINA de M4+M4b+M4c = **546.972 kPa**; **techo:** máximo = **2494.53 kPa**.
- Franjas de 100 kPa con KALINA en algún momento: 12 de 12 (lista completa en `m4c_techo.csv`).
- ¿Sigue KALINA más allá de 1500 kPa? sí: el KALINA de mayor P_baja está en 2494.53 kPa.
## 7. Lo que no se sabe
- El LHS tiene 150 puntos en una caja de 10 dimensiones: el techo está acotado por los puntos muestreados, no es una frontera calculada.
- Los 15 puntos omitidos no informan nada y no entran en ningún %; y la franja 1300–1500 kPa viene de M4 + M4b (dos LHS distintos), % no comparable punto a punto con M4c.

## 8. Nota del director (Claude, auditoría 2026-10-07)

- El KALINA de mayor P_baja (2494.53 kPa; P_alta 3655, T_fuente 438.2 K) es el **único de M4c con `B_verificado = False`** (|Δh4s| = 2.02 kJ/kg, apenas sobre el umbral de 2.0). Los otros 74 KALINA están verificados. El techo verificado más alto es el siguiente KALINA de la franja de 2400–2500 kPa.
- **Lectura:** entre 1500 y 2500 kPa **no aparece ningún techo de clasificación** (33–75 % KALINA por franja). Lo que limita a P_baja es la razón de presiones: los KALINA de M4c tienen rP de 1.16 a 3.04, y hay que respetar P_baja < P_alta − 300. Además, η cae: mediana de 4.35 % y máximo de 8.35 %. **El techo de P_baja es estructural (rP) y de eficiencia, no de cavitación.**
- 30 de los 75 KALINA están fuera del rango confiable (líquido > 420 K).

# REPORTE M5c — la franja KALINA con las presiones del profesor
## 1. La pregunta
Con **P_alta = 3000 kPa y P_baja = 400 kPa** (las presiones del profesor), ¿en qué franja exacta de T_fuente, ε_cond y T_sumidero el ciclo es KALINA?
## 2. Qué se hizo
- **Malla completa:** T_fuente ∈ {385, 387.5, …, 410} K (11 valores), ε_cond ∈ {0.85, 0.875, 0.90, 0.925, 0.95} (5) y T_sumidero ∈ {278.15, 290.65, 300.032917} K (3): 11 × 5 × 3 = **3 corridas**, cada una con flush en `m5c_malla.csv`.
- **Todo lo demás igual a `comun.PROFESOR`:** x_b = 0.50, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85, ε_reg = 0.75, m_b = 1.0. Motor `teqp`, 7 procesos en el mismo pool que M4c y **piso de O2 = T_sumidero** en todo punto.
- **Punto genuino:** KALINA, CORREGIBLE o INVIABLE. Las NO_CONVERGIO no cuentan.
## 3. La franja exacta
De los 3 puntos de la malla: **2 KALINA**.

| T_sumidero (K) | ε_cond | celdas KALINA | T_fuente mín (K) | T_fuente máx (K) | η en el mínimo | η en el máximo |
|---|---|---|---|---|---|---|
| 278.15 | 0.85 | 0 | n/d | n/d | n/d | n/d |
| 278.15 | 0.875 | 0 | n/d | n/d | n/d | n/d |
| 278.15 | 0.9 | 0 | n/d | n/d | n/d | n/d |
| 278.15 | 0.925 | 0 | n/d | n/d | n/d | n/d |
| 278.15 | 0.95 | 0 | n/d | n/d | n/d | n/d |
| 290.65 | 0.85 | 0 | n/d | n/d | n/d | n/d |
| 290.65 | 0.875 | 0 | n/d | n/d | n/d | n/d |
| 290.65 | 0.9 | 1 | 397.5 | 397.5 | 0.0747 | 0.0747 |
| 290.65 | 0.925 | 0 | n/d | n/d | n/d | n/d |
| 290.65 | 0.95 | 0 | n/d | n/d | n/d | n/d |
| 300.033 | 0.85 | 0 | n/d | n/d | n/d | n/d |
| 300.033 | 0.875 | 0 | n/d | n/d | n/d | n/d |
| 300.033 | 0.9 | 0 | n/d | n/d | n/d | n/d |
| 300.033 | 0.925 | 0 | n/d | n/d | n/d | n/d |
| 300.033 | 0.95 | 1 | 410 | 410 | 0.1081 | 0.1081 |
## 4. La franja en palabras
El ciclo es KALINA solo en estas combinaciones de la malla:
- **T_sumidero:** 290.65 K … 300.033 K (2 de los 3 valores; los que no aparecen no tienen ningún KALINA).
- **ε_cond:** 0.9 … 0.95 (2 de los 5 valores).
- **T_fuente:** de 397.5 a 410 K (los extremos exactos de la franja; entre ellos puede haber huecos, que la columna «celdas KALINA» de §3 revela).
- T_sumidero = 278.15 K: ningún punto KALINA; el criterio que más se rompe es `None` (0/0).
## 5. Qué bloquea a cada lado de la franja
Criterio de conteo: entre los puntos **genuinos que NO son KALINA** con T_fuente **por debajo** de la franja (0 puntos) y **por encima** de ella (0 puntos), se cuenta cada código de `codigos_falla`.

- **Por debajo de 397.5 K:** `None` rompe 0 de 0.
- **Por encima de 410 K:** `None` rompe 0 de 0.
- Celdas de la malla sin ningún KALINA: 13 de 15 (las verás con «celdas KALINA» = 0 en §3; los T_sumidero sin ningún KALINA, si los hay, quedan listados en §4).
## 6. La mejor η dentro de la franja
El KALINA de mayor η es el id 164: **η = 0.1081** (T_fuente = 410 K, ε_cond = 0.95, T_sumidero = 300.033 K, D = 0.000, fuera de rango = no, B_verificado = True).
## 7. Lo que no se sabe
- La malla tiene paso 2.5 K en T_fuente y 0.025 en ε_cond: la franja está delimitada a esa resolución, no con precisión continua.
- Los puntos **fuera de rango** del motor de propiedades (líquido > 420 K) hay que tomarlos con pinzas; aquí T_fuente ≤ 410 K, pero los estados internos pueden superar ese valor.
- Solo se variaron T_fuente, ε_cond y T_sumidero: con las demás variables fijas en `comun.PROFESOR` no se dice nada sobre otras combinaciones.

# Ficha 2.4 — Efecto de un sumidero más frío

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80.
> - **A\* (punto ancla):** PP con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %).
> - **Piso de O2:** temperatura con la que se evalúa la cavitación. **Desde este caso es igual a la
>   T_sumidero de cada punto.** Antes era 300.03 K fija.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades y con
>   todas sus η y ε en [0.40, 0.95].

### ID del caso:
**Estudio 2.4** · Sumidero más frío. Responde la pregunta 2: ¿Qué es lo mínimo que hay que cambiar para que funcione?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 2.4a (fuente a 403 K); 2.4b (fuente a 420 K); 2.4c (ε_HRVG = 0.40 (fuente del profesor)); 2.4d (datos exactos del profesor).
Familia **F** · 2026-10-06 · commit `8d88070` · código de origen: M02S.

### Nombre del caso:
Sumidero frío con P_baja libre.

### Objetivo del barrido:
Medir cuánto baja la P_baja necesaria para KALINA, y cuánto sube η, si el sitio es más frío y la
cavitación se evalúa con ese clima.

### ¿Qué se barrió?
T_sumidero × P_baja, en 4 bases distintas.

### ¿Por qué se barrió?
El enunciado usa un clima tropical (300 K). Un sitio más frío facilita condensar y alivia la
cavitación; había que cuantificarlo antes de fijar los rangos de presión.

### Datos o variables barridas:
- T_sumidero ∈ {278.15, 283.15, 288.15, 293.15, 300.03} K, con el piso de O2 igual a cada valor.
- P_baja: 150–1500 kPa, 10 valores, más bisección.
- Total: **320 corridas**.

### Datos modificados (todo lo demás en PP):

| Base | Qué cambia respecto al profesor |
|---|---|
| 2.4a | T_fuente = 403 K (la fuente de A\*) |
| 2.4b | T_fuente = 420 K (el KALINA de mayor η de estudios 2.1 y 2.2) |
| 2.4c | ε_HRVG = 0.40 (conserva la fuente de 623 K; ruta de estudio 2.3) |
| 2.4d | ninguno (profesor exacto) |

### Métodos aplicados:
Malla de P_baja por base y clima, más bisección donde cambia "ser KALINA" o el signo de O2
(tolerancia 10 kPa, como máximo 7 iteraciones).

### Resultados obtenidos:

| Base | KALINA (confiables) | 300.03 K: P_baja mín. / η máx. | 278.15 K: P_baja mín. / η máx. |
|---|---|---|---|
| 2.4a (403 K) | 59 (59) | 562.5 kPa / 8.49 % | 290.6 kPa / 10.41 % |
| 2.4b (420 K) | 60 (60) | 740.6 kPa / 9.11 % | 393.8 kPa / 11.91 % |
| 2.4c (ε_HRVG 0.40) | 34 (**0**) | 1312.5 kPa / 6.30 % | 750 kPa / 9.69 % |
| 2.4d (profesor) | 0 | — | — |

123 KALINA únicos en total. Todas estas cifras fueron verificadas en V07 y V08. La η máxima de
cada clima ocurre justo en la P_baja mínima: η baja al subir P_baja.

Tablas: 2.4-1, 2.4-2, 2.4-3. Figuras: 2.4-1.

### Conclusiones del caso:
1. **Un sumidero ~22 K más frío reduce a la mitad la P_baja necesaria** (2.4a: 563 → 291 kPa) y
   **sube η entre 2 y 3 puntos**.
2. **El profesor exacto (2.4d) nunca es KALINA**, ni siquiera con clima frío: el problema es la fuente, no el clima.
3. La ruta que conserva la fuente de 623 K (2.4c) da KALINA, pero **ninguno es confiable**.

### Advertencias, supuestos y limitaciones:
- El cambio de regla del piso de O2 (= T_sumidero) hace que estos resultados no se comparen punto a
  punto con estudio 1.1–estudio 3.1 (piso fijo de 300.03 K).
- A 278.15 K, 11 de 64 puntos no son genuinos (cerca del límite del motor).
- Malla de P_baja con paso de 150 kPa.

### Recomendaciones:
Al recomendar presiones, decir siempre el clima de diseño: la P_baja mínima depende fuertemente de
él. Para el diseño, preferir 2.4a y 2.4b (fuente ~400–420 K), que son confiables.

**Fuentes:** `resultados/2026-10-06_final_M2S/REPORTE_M2S.md`, `m2s_malla.csv`, `m2s_biseccion.csv`, `m2s_resumen.csv`; verificación V07, V08.

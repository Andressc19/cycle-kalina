# Ficha 2.3 — Repetición de estudios 2.1 y 2.2 con eficiencias y efectividades en [0.40, 0.95]

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades
>   (sin líquido por encima de 420 K) y con todas sus η y ε en [0.40, 0.95].
> - **O2:** cavitación (el líquido debe llegar subenfriado a la bomba).

### ID del caso:
**Estudio 2.3** · Dos cambios con η y ε en 0.40–0.95. Responde la pregunta 2: ¿Qué es lo mínimo que hay que cambiar para que funcione?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 2.3a (un cambio); 2.3b (ε_HRVG × ε_cond); 2.3c (ε_HRVG × P_baja); 2.3d (T_fuente × ε_cond).
Familia **F** · 2026-10-06 · commit `ef30e9f` · código de origen: M02R.

### Nombre del caso:
estudios 2.1 y 2.2 repetido con el rango de eficiencias y efectividades abierto.

### Objetivo del barrido:
Responder si se puede llegar a KALINA **conservando la fuente (623 K) y el clima del profesor**,
cambiando solo variables de diseño, ahora que η y ε pueden moverse en [0.40, 0.95].

### ¿Qué se barrió?

| Parte | Qué se mueve | Corridas |
|---|---|---|
| 2.3a | una variable a la vez, con η/ε en [0.40, 0.95] | 80 |
| 2.3b | ε_HRVG (0.40–0.80) × ε_cond (0.40–0.95), con P_baja = 400 kPa | 60 |
| 2.3c | ε_HRVG (0.40–0.70) × P_baja (400–2000 kPa) | 64 |
| 2.3d | T_fuente × ε_cond, con la P_baja del profesor | 21 |

### ¿Por qué se barrió?
estudios 2.1 y 2.2 limitó η y ε a [0.75, 0.85]. El rango aceptado del proyecto es [0.40, 0.95], y faltaba saber si
el límite anterior era lo que impedía conservar la fuente del profesor.

### Datos o variables barridas:
Ver la tabla anterior. Las variables que no se mueven en cada parte quedan en PP y el piso de O2
en 300.03 K. Total: **225 corridas**.

### Datos modificados:
Solo las variables de cada parte (máximo 2). El resto, igual que el profesor.

### Métodos aplicados:
Mallas de 12 valores por variable (paso 0.05 en η/ε), más bisección de las fronteras. Los puntos
genuinos se cuentan como en estudios 2.1 y 2.2 (los N2 no cuentan).

### Resultados obtenidos:
- **14 puntos KALINA distintos.** La tabla completa tiene 20 filas KALINA porque la malla y la
  bisección repiten puntos (verificación V06).

| Parte | KALINA (filas) | KALINA confiables | Lectura |
|---|---|---|---|
| 2.3a | 0 | 0 | un solo cambio sigue sin alcanzar |
| 2.3b | 0 | 0 | ε_HRVG y ε_cond con la fuente de 623 K y P_baja = 400 kPa: no alcanza (48 corregibles, todos por O2) |
| 2.3c | 19 (13 distintos) | **0** | ε_HRVG = 0.40 con P_baja 1318–2000 kPa (η ≤ 6.3 %) y ε_HRVG = 0.50 con P_baja 1736–2000 kPa (η ≤ 4.3 %): KALINA, pero **todos fuera de rango** |
| 2.3d | 1 | **1** | **T_fuente = 403 K y ε_cond = 0.95 con las presiones del profesor:** KALINA confiable, η = 9.50 % |

- Tablas: 2.3-1, 2.3-2, 2.3-3. Figuras: 2.3-1, 2.3-2, 2.3-3, 2.3-4.

### Conclusiones del caso:
1. **Con la fuente del profesor (623 K) sí aparece KALINA**: hay que bajar mucho la efectividad del
   HRVG (0.40–0.50) y subir P_baja a ~1300–2000 kPa. Pero **ninguno de esos puntos es confiable**:
   quedan fuera del rango validado del modelo de propiedades.
2. **Con las presiones exactas del profesor (3000 y 400 kPa) también hay KALINA**, si la fuente
   baja a 403 K y el condensador es muy efectivo (ε_cond = 0.95). Este punto es confiable.
3. El bloqueo de fondo es siempre el mismo: el lado caliente y la cavitación (O2).

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 2.3-1.** Con 623 K, mover η_t, η_p, ε_reg o ε_cond en todo su rango no desbloquea nada; solo ε_HRVG
  (0.40–0.82) da Corregibles.
- **Figura 2.3-2.** Los «No convergió» forman un bloque en ε_HRVG 0.7–0.8 con ε_cond bajo. Dos rojos aislados
  en plena zona Corregible (ε_cond 0.80/ε_HRVG 0.50 y ε_cond 0.95/ε_HRVG 0.80) parecen fallas numéricas del
  solver (hipótesis; no probado).
- **Figura 2.3-3.** Los 19 KALINA son los 19 fuera de rango: con ε_HRVG 0.40 la frontera está en ≈1320 kPa y con
  0.50 en ≈1740, ≈ +400 kPa por cada +0.10 de ε_HRVG. La leyenda original no lo decía.
- **Figura 2.3-4.** El único KALINA confiable es **un punto** (403 K, ε_cond 0.95) en una malla de 3 valores
  de ε_cond: es una existencia, no una región (la región la da el estudio 4.2).

### Advertencias, supuestos y limitaciones:
- 13 de los 14 KALINA distintos están fuera de rango: sus η (3.1 a 6.3 %) se toman con cautela.
- 4 puntos N2 se descartaron.
- El paso de 0.05 en η/ε puede dejar sin ver zonas KALINA angostas.

### Recomendaciones:
- No presentar la ruta "ε_HRVG = 0.40 con la fuente de 623 K" como diseño: no es confiable.
- El punto de la parte 2.3d (presiones del profesor, T_fuente 403 K, ε_cond 0.95) es el antecedente
  de estudio 4.2, que mapea esa franja en detalle.

**Fuentes:** `resultados/2026-10-06_final_M2R/REPORTE_M2R.md`, `m2r_*_malla.csv`, `m2r_*_biseccion.csv`, `m2r_kalina.csv`; verificación V06.

# FICHA KF-M02R — Repetición de M2 con eficiencias y efectividades en [0.40, 0.95]

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades
>   (sin líquido por encima de 420 K).
> - **O2:** cavitación (el líquido debe llegar subenfriado a la bomba).

### ID del caso:
`KF-M02R` · cuatro bloques, uno por parte, que no se mezclan: **B04-n1, B04-n2a, B04-n2b y B04-n3**.
Familia **F**, diseño: malla y bisección. 2026-10-06, commit `ef30e9f`.

### Nombre del caso:
M2 repetido con el rango de eficiencias y efectividades abierto.

### Objetivo del barrido:
Responder si se puede llegar a KALINA **conservando la fuente (623 K) y el clima del profesor**,
cambiando solo variables de diseño, ahora que η y ε pueden moverse en [0.40, 0.95].

### ¿Qué se barrió?

| Parte | Qué se mueve | Corridas |
|---|---|---|
| n1 | una variable a la vez, con η/ε en [0.40, 0.95] | 80 |
| n2a | ε_HRVG (0.40–0.80) × ε_cond (0.40–0.95), con P_baja = 400 kPa | 60 |
| n2b | ε_HRVG (0.40–0.70) × P_baja (400–2000 kPa) | 64 |
| n3 | T_fuente × ε_cond, con la P_baja del profesor | 21 |

### ¿Por qué se barrió?
M2 limitó η y ε a [0.75, 0.85]. El rango aceptado del proyecto es [0.40, 0.95], y faltaba saber si
el límite anterior era lo que impedía conservar la fuente del profesor.

### Datos o variables barridas:
Ver la tabla anterior. Las variables que no se mueven en cada parte quedan en PP y el piso de O2
en 300.03 K. Total: **225 corridas**.

### Datos modificados:
Solo las variables de cada parte (máximo 2). El resto, igual que el profesor.

### Métodos aplicados:
Mallas de 12 valores por variable (paso 0.05 en η/ε), más bisección de las fronteras. Los puntos
genuinos se cuentan como en M2 (los N2 no cuentan).

### Resultados obtenidos:
- **14 puntos KALINA distintos.** La tabla completa tiene 20 filas KALINA porque la malla y la
  bisección repiten puntos (A4, V06).

| Parte | KALINA (filas) | KALINA confiables | Lectura |
|---|---|---|---|
| n1 | 0 | 0 | un solo cambio sigue sin alcanzar |
| n2a | 0 | 0 | ε_HRVG y ε_cond con la fuente de 623 K y P_baja = 400 kPa: no alcanza (48 corregibles, todos por O2) |
| n2b | 19 (13 distintos) | **0** | ε_HRVG = 0.40 con P_baja 1318–2000 kPa (η ≤ 6.3 %) y ε_HRVG = 0.50 con P_baja 1736–2000 kPa (η ≤ 4.3 %): KALINA, pero **todos fuera de rango** |
| n3 | 1 | **1** | **T_fuente = 403 K y ε_cond = 0.95 con las presiones del profesor:** KALINA confiable, η = 9.50 % |

- Tablas: TAB-M02R-00/01/02. Figuras FIG-M02R-n1, -n2a, -n2b y -n3 (una por parte).

### Conclusiones del caso:
1. **Con la fuente del profesor (623 K) sí aparece KALINA**: hay que bajar mucho la efectividad del
   HRVG (0.40–0.50) y subir P_baja a ~1300–2000 kPa. Pero **ninguno de esos puntos es confiable**:
   quedan fuera del rango validado del modelo de propiedades.
2. **Con las presiones exactas del profesor (3000 y 400 kPa) también hay KALINA**, si la fuente
   baja a 403 K y el condensador es muy efectivo (ε_cond = 0.95). Este punto es confiable.
3. El bloqueo de fondo es siempre el mismo: el lado caliente y la cavitación (O2).

### Advertencias, supuestos y limitaciones:
- 13 de los 14 KALINA distintos están fuera de rango: sus η (~6.3 %) se toman con cautela.
- 4 puntos N2 se descartaron.
- El paso de 0.05 en η/ε puede dejar sin ver zonas KALINA angostas.

### Recomendaciones:
- No presentar la ruta "ε_HRVG = 0.40 con la fuente de 623 K" como diseño: no es confiable.
- El punto de la parte n3 (presiones del profesor, T_fuente 403 K, ε_cond 0.95) es el antecedente
  de M5c, que mapea esa franja en detalle.

**Fuentes:** `resultados/2026-10-06_final_M2R/REPORTE_M2R.md`, `m2r_*_malla.csv`, `m2r_*_biseccion.csv`, `m2r_kalina.csv`; A4 (V06).

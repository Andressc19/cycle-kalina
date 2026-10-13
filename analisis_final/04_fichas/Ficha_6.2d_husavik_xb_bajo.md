# Ficha 6.2d — Húsavík con poco amoníaco (x_b 0.30–0.70)

> **Antes de leer**
> - **Ancla de Húsavík:** P_alta = 3300 kPa, T_fuente = 394.15 K, T_sumidero = 278.15 K,
>   η_t = 0.90, η_p = 0.80, ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.95, con el piso de O2 en 283.15 K.
> - **x_b:** fracción de amoníaco de la mezcla base. Los Kalina suelen usar 0.55–0.95.
> - **O3:** el ciclo debe producir trabajo neto positivo. **O5:** el separador debe recibir dos fases.
> - **N2 (falso convergido):** el solver dice que convergió, pero el clasificador lo descarta.

### ID del caso:
**Estudio 6.2d** · Planta real de Húsavík. Responde la pregunta 6: ¿Son confiables los resultados?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 6.2c (malla x_b × P_baja (x_b 0.30–0.70)); 6.2d (x_b bajo (0.30–0.70)).
Familia **H** · 2026-10-09 · commit `97aa4e2` · código de origen: M10b.

### Nombre del caso:
¿Sigue habiendo KALINA en Húsavík si la mezcla tiene poco amoníaco?

### Objetivo del barrido:
Extender hacia abajo el rango de x_b de estudio 6.2 (0.60–0.95) y ver hasta dónde funciona el ciclo.

### ¿Qué se barrió?
- **6.2d:** x_b de 0.30 a 0.70, 17 valores, con P_baja = 690 kPa.
- **6.2c:** x_b ∈ {0.30, 0.35, …, 0.70} × P_baja ∈ {200, …, 700} kPa.

### ¿Por qué se barrió?
El enunciado del profesor usa x_b = 0.50, que es baja para un Kalina. Había que saber si con poco
amoníaco el ciclo puede funcionar.

### Datos o variables barridas:

| Parte | Variable | Rango | n |
|---|---|---|---|
| 6.2d | x_b (P_baja fija en 690 kPa) | 0.30 – 0.70 | 17 |
| 6.2c | x_b × P_baja | x_b 0.30–0.70 (9) × P_baja 200–700 kPa (6) | 54 |

Total: **71 corridas**.

### Datos modificados:
Ancla de Húsavík: P_alta 3300 kPa, T_fuente 394.15 K, T_sumidero 278.15 K, η_t 0.90, η_p 0.80,
ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95, con el piso de O2 en 283.15 K. Respecto a estudio 6.2, solo cambia el
rango de x_b, que baja hasta 0.30.

### Métodos aplicados:
Una variable a la vez y malla 2D completa. Los x_b menores que 0.55 se etiquetan como "x_b bajo,
fuera de lo habitual en Kalina": es una etiqueta, no un filtro.

### Resultados obtenidos (validación V22):

| x_b | Qué pasa |
|---|---|
| 0.30 – 0.45 | **No hay ciclo**: de 32 corridas, 16 no convergen y 16 son falsos convergidos (N2); ninguna es genuina |
| 0.50 | KALINA desde P_baja = 200 kPa, pero con **η de solo 0.1–1.2 %**: KALINA formal, sin utilidad práctica |
| 0.55 | **Primer KALINA útil**: P_baja mínima de 300 kPa, η = 9.6 % |
| 0.60 / 0.65 / 0.70 | P_baja mínima de 400 / 500 / 500 kPa |

- 71 corridas: 38 genuinas y 29 KALINA, todos confiables.
- Tablas: 6.2-1, 6.2-2, 6.2-3, 6.2-4, 6.2-5. Figuras: 6.2-1, 6.2-2.

### Conclusiones del caso:
1. **Por debajo de x_b = 0.50 el modelo no encuentra ningún ciclo.** Las soluciones aparentes (N2) muestran
   trabajo negativo (O3) y separador sin dos fases (O5), pero son espurias: sirven como indicio, no como prueba.
2. **x_b = 0.50 (la del profesor) es el límite**: es formalmente KALINA, pero casi no produce trabajo
   en las condiciones de Húsavík.
3. **El KALINA útil empieza en x_b ≈ 0.55**, y a menor x_b permite una P_baja más baja.

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 6.2-1 (zona x_b ≤ 0.475).** Los puntos con x_b 0.30 y 0.35 son «No convergió» y los de 0.40 y 0.45
  «Falso convergido»; la malla los marca como «sin ciclo». En x_b = 0.50 aparece KALINA incluso a 200 kPa.
  El borde es un corte, no una pendiente.

### Advertencias, supuestos y limitaciones:
- La conclusión sobre x_b = 0.50 vale con el ancla de Húsavík (T_fuente 394 K y P_alta 3300 kPa).
  Con otras condiciones (por ejemplo, estudio 4.2), x_b = 0.50 sí da η de ~8–11 %.
- El reporte original decía "primer KALINA en 0.55". La validación cruzada precisó que el primero formal
  es 0.50 y el primero útil es 0.55.

### Recomendaciones:
Al discutir la composición del profesor (x_b = 0.50), aclarar que funciona, pero cerca del límite
inferior de la tecnología. Los diseños robustos usan x_b ≥ 0.55.

**Fuentes:** `resultados/2026-10-09_final_M10b_xb_bajo/REPORTE_M10b.md`, `m10b_ofat_xb.csv`, `m10b_malla_xb_pbaja.csv`; validación V22.

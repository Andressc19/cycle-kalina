# FICHA KF-M10b — Húsavík con poco amoníaco (x_b 0.30–0.70)

> **Antes de leer**
> - **Ancla de Húsavík:** P_alta = 3300 kPa, T_fuente = 394.15 K, T_sumidero = 278.15 K,
>   η_t = 0.90, η_p = 0.80, ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.95, con el piso de O2 en 283.15 K.
> - **x_b:** fracción de amoníaco de la mezcla base. Los Kalina suelen usar 0.55–0.95.
> - **O3:** el ciclo debe producir trabajo neto positivo. **O5:** el separador debe recibir dos fases.
> - **N2 (falso convergido):** el solver dice que convergió, pero el clasificador lo descarta.

### ID del caso:
`KF-M10b`, con subcasos OFAT y MALLA. Bloques **B14-OFATb** y **B14-MALLA**; este último comparte el
bloque con la malla de M10 porque tiene los mismos datos fijos. Familia **H**. 2026-10-09, commit `97aa4e2`.

### Nombre del caso:
¿Sigue habiendo KALINA en Húsavík si la mezcla tiene poco amoníaco?

### Objetivo del barrido:
Extender hacia abajo el rango de x_b de M10 (0.60–0.95) y ver hasta dónde funciona el ciclo.

### ¿Qué se barrió?
- **OFAT:** x_b de 0.30 a 0.70, 17 valores, con P_baja = 690 kPa.
- **MALLA:** x_b ∈ {0.30, 0.35, …, 0.70} × P_baja ∈ {200, …, 700} kPa.

### ¿Por qué se barrió?
El enunciado del profesor usa x_b = 0.50, que es baja para un Kalina. Había que saber si con poco
amoníaco el ciclo puede funcionar.

### Datos o variables barridas:

| Subcaso | Variable | Rango | n |
|---|---|---|---|
| OFAT | x_b (P_baja fija en 690 kPa) | 0.30 – 0.70 | 17 |
| MALLA | x_b × P_baja | x_b 0.30–0.70 (9) × P_baja 200–700 kPa (6) | 54 |

Total: **71 corridas**.

### Datos modificados:
Ancla de Húsavík: P_alta 3300 kPa, T_fuente 394.15 K, T_sumidero 278.15 K, η_t 0.90, η_p 0.80,
ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95, con el piso de O2 en 283.15 K. Respecto a M10, solo cambia el
rango de x_b, que baja hasta 0.30.

### Métodos aplicados:
Una variable a la vez y malla 2D completa. Los x_b menores que 0.55 se etiquetan como "x_b bajo,
fuera de lo habitual en Kalina": es una etiqueta, no un filtro.

### Resultados obtenidos (A4, V22):

| x_b | Qué pasa |
|---|---|
| 0.30 – 0.45 | **No hay ciclo**: de 32 corridas, 16 no convergen y 16 son falsos convergidos (N2); ninguna es genuina |
| 0.50 | KALINA desde P_baja = 200 kPa, pero con **η de solo 0.1–1.2 %**: KALINA formal, sin utilidad práctica |
| 0.55 | **Primer KALINA útil**: P_baja mínima de 300 kPa, η = 9.6 % |
| 0.60 / 0.65 / 0.70 | P_baja mínima de 400 / 500 / 500 kPa |

- 71 corridas: 38 genuinas y 29 KALINA, todos confiables.
- Tablas: TAB-M10b-00 a -02. Figura: comparte FIG-M10-01 (malla x_b × P_baja), en el mismo bloque.

### Conclusiones del caso:
1. **Por debajo de x_b = 0.50 el modelo no encuentra ningún ciclo.** Las soluciones aparentes (N2) muestran
   trabajo negativo (O3) y separador sin dos fases (O5), pero son espurias: sirven como indicio, no como prueba.
2. **x_b = 0.50 (la del profesor) es el límite**: es formalmente KALINA, pero casi no produce trabajo
   en las condiciones de Húsavík.
3. **El KALINA útil empieza en x_b ≈ 0.55**, y a menor x_b permite una P_baja más baja.

### Advertencias, supuestos y limitaciones:
- La conclusión sobre x_b = 0.50 vale con el ancla de Húsavík (T_fuente 394 K y P_alta 3300 kPa).
  Con otras condiciones (por ejemplo, M5c), x_b = 0.50 sí da η de ~8–11 %.
- El reporte original decía "primer KALINA en 0.55". La validación A4 precisó que el primero formal
  es 0.50 y el primero útil es 0.55.

### Recomendaciones:
Al discutir la composición del profesor (x_b = 0.50), aclarar que funciona, pero cerca del límite
inferior de la tecnología. Los diseños robustos usan x_b ≥ 0.55.

**Fuentes:** `resultados/2026-10-09_final_M10b_xb_bajo/REPORTE_M10b.md`, `m10b_ofat_xb.csv`, `m10b_malla_xb_pbaja.csv`; A4 (V22).

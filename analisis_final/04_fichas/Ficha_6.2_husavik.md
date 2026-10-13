# Ficha 6.2 — Húsavík revisitado

> **Antes de leer**
> - **Húsavík:** planta Kalina real (Islandia). Se usa como caso de contraste con datos reales.
> - **Ancla de Húsavík:** P_alta = 3300 kPa, P_baja = 690 kPa, T_fuente = 394.15 K,
>   T_sumidero = 278.15 K, η_t = 0.90, η_p = 0.80, ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.95,
>   con el piso de O2 en 283.15 K.
> - **Fase 3 (6.2a):** el estudio de Húsavík de septiembre, hecho con el código de entonces.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades y con
>   todas sus η y ε en [0.40, 0.95].

### ID del caso:
**Estudio 6.2** · Planta real de Húsavík. Responde la pregunta 6: ¿Son confiables los resultados?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 6.2a (Fase 3 de septiembre); 6.2b (una variable a la vez); 6.2c (malla x_b × P_baja (x_b 0.70–0.91)); 6.2c (malla x_b × P_baja (x_b 0.30–0.70)); 6.2d (x_b bajo (0.30–0.70)); 6.2e (P_baja mínima con su piso de diseño).
Familia **H** · 2026-10-09 · commit `77b1ae8` · código de origen: M10, M10b.

### Nombre del caso:
¿Se confirman los KALINA de Húsavík con el código actual y qué pasa en las variables que no se movieron?

### Objetivo del barrido:
1. Re-evaluar los 97 KALINA de la Fase 3.
2. Barrer las variables que entonces no se movieron.
3. Mapear x_b × P_baja.

### ¿Qué se barrió?
- **6.2a:** los 97 puntos KALINA de septiembre, tal cual.
- **6.2b:** 10 variables, de a una, 15 valores cada una, alrededor del ancla de Húsavík.
- **6.2c:** x_b de 0.70 a 0.91 (8 valores) × P_baja de 500 a 1200 kPa (8 valores).

### ¿Por qué se barrió?
Para validar la campaña con un caso real: si el modelo actual reproduce una planta que existe, sus
conclusiones sobre el caso del profesor ganan credibilidad.

### Datos o variables barridas:

| Parte | Variables barridas | Rango | n |
|---|---|---|---|
| 6.2a (re-evaluación) | P_alta, P_baja, x_b, η_t, ε_reg, ε_cond (según la familia) | P_alta 3300–3500 kPa · P_baja 670–1500 kPa · x_b 0.78–0.83 · η_t 0.85–0.98 · ε_reg 0.75–0.95 · ε_cond 0.95–0.99 | 97 |
| 6.2b | las 10 variables, una a la vez | T_fuente 380–430 K · T_sumidero 273–293 K · P_alta 2500–4000 kPa · P_baja 500–1200 kPa · x_b 0.60–0.95 · η_t 0.75–0.95 · η_p 0.60–0.90 · ε_HRVG 0.60–0.95 · ε_reg 0.40–0.95 · ε_cond 0.70–0.95 | 150 |
| 6.2c | x_b × P_baja | x_b 0.70–0.91 (8) × P_baja 500–1200 kPa (8) | 64 |

Total: **311 corridas**.

### Datos modificados:
No se parte del profesor, sino del **ancla de Húsavík**: P_alta 3300 kPa, P_baja 690 kPa,
T_fuente 394.15 K, T_sumidero 278.15 K, η_t 0.90, η_p 0.80, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95,
con el piso de O2 en 283.15 K. Lo que no se barre en 6.2b y 6.2c queda en esos valores. Los puntos
6.2a conservan sus datos de septiembre, con pisos de O2 de 283.15 o 303.55 K según la familia.

### Métodos aplicados:
Re-evaluación punto a punto; una variable a la vez (15 puntos); malla 2D completa.

### Resultados obtenidos:
- **6.2a: 97 de 97 siguen siendo KALINA y ninguno cambia de clase** (validación V21); **83 son KALINA confiables**;
  los otros 14 usan η o ε > 0.95 y no cuentan como confiables (ver advertencias). Las η coinciden
  a 10⁻¹¹ pp.
- **6.2b (148 genuinos, 107 KALINA):** rangos KALINA con lo demás en el ancla:

| Variable | KALINA desde – hasta | Qué rompe fuera |
|---|---|---|
| T_fuente | 380 – 401 K | O2 al subir |
| T_sumidero | 273 – 283 K | O2 al subir |
| P_alta | 2821 – 4000 kPa | O2 al bajar |
| P_baja | 700 – 1200 kPa | O2 al bajar |
| x_b | 0.60 – 0.825 | O2 al subir |
| ε_HRVG | 0.60 – 0.925 | O2 al subir (en 0.95, por 0.006 K) |
| η_t, η_p, ε_reg | todo el rango probado | — |
| ε_cond | solo 0.95 | O2 al bajar |

- **6.2c:** la P_baja mínima KALINA sube con x_b: 500 kPa con x_b = 0.70, y 800 kPa con x_b ≥ 0.85.
- Con su piso de diseño (10 °C), la P_baja mínima KALINA coincide con su valor real, 690 kPa (estudio 4.3).
  El motor real lo confirma (η = 12.73 %).
- Tablas: 6.2-1, 6.2-2, 6.2-3, 6.2-4, 6.2-5. Figuras: 6.2-1, 6.2-2.

### Conclusiones del caso:
1. **El modelo actual reproduce exactamente los KALINA de Húsavík** y coincide con su presión real
   de condensación. Es una validación fuerte.
2. Húsavík está, como los diseños del profesor modificado, **al filo de la cavitación (O2)**: casi
   todas las variables rompen por O2.
3. Una mezcla más rica en amoníaco (x_b alta) pide más P_baja para evitar la cavitación.

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 6.2-1.** La P_baja mínima de KALINA sube en escalones con x_b: 200 kPa (0.50), 300 (0.55), 400 (0.60),
  500 (0.65–0.70), 600 (0.73–0.76), 700 (0.79–0.82) y 800 (0.85–0.91), es decir, ≈ +150 kPa por cada +0.10 de x_b
  (resolución de la malla: 100 kPa). Para x_b ≥ 0.73 la malla empieza en 500 kPa y no mide más abajo.
- **Figura 6.2-2.** La clase cambia de forma abrupta (KALINA → Corregible) en T_fuente (≈405 K), P_alta
  (≈2800 kPa), P_baja (≈650–700 kPa), x_b (≈0.85) y ε_cond (solo 0.95 es KALINA: es el **tope** permitido, sin
  holgura). El corte en T_sumidero = 283.15 K coincide con el piso de O2 de la corrida: es una condición
  impuesta, no un hallazgo. η_t es la palanca más fuerte (10.5 → 13.5 %).
- Hay dos «No convergió» aislados dentro de curvas lisas (x_b ≈0.625 y ε_cond ≈0.755): se leen como fallas
  numéricas (hipótesis).

### Advertencias, supuestos y limitaciones:
- 6.2b de 15 puntos: las fronteras quedan entre dos muestras; no se bisecaron.
- Solo se re-evaluaron los KALINA de septiembre, no los CORREGIBLE ni los no convergidos.
- 6.2b y 6.2c solo con teqp.
- **Algunos puntos 6.2a de septiembre usan η_t hasta 0.98 y ε_cond hasta 0.99**, por encima del
  tope realista del proyecto (0.95): son **14 de los 97** (11 de la familia F3-A y 3 de F3-D). Se
  reproducen tal cual porque son los de la Fase 3, pero no deben citarse como diseño. Los otros
  **83 KALINA tienen todas sus η y ε ≤ 0.95**, así que la validación con Húsavík no depende de ellos.

### Recomendaciones:
Citar Húsavík en el informe como validación del modelo, y su P_baja (690 kPa) como referencia real
dentro de la ventana de presiones de estudio 3.2.

**Fuentes:** `resultados/2026-10-09_final_M10_husavik/REPORTE_M10.md`, `m10_recorrida_fase3.csv`, `m10_ofat.csv`, `m10_malla_xb_pbaja.csv`, `m10_ofat_rangos.csv`; estudio 4.3 (Húsavík con el motor real); validación V21, V22.

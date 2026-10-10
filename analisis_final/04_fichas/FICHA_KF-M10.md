# FICHA KF-M10 — Húsavík revisitado

> **Antes de leer**
> - **Húsavík:** planta Kalina real (Islandia). Se usa como caso de contraste con datos reales.
> - **Ancla de Húsavík:** P_alta = 3300 kPa, P_baja = 690 kPa, T_fuente = 394.15 K,
>   T_sumidero = 278.15 K, η_t = 0.90, η_p = 0.80, ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.95,
>   con el piso de O2 en 283.15 K.
> - **Fase 3 (F3):** el estudio de Húsavík de septiembre, hecho con el código de entonces.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades.

### ID del caso:
`KF-M10`, con subcasos F3 (re-evaluación), OFAT y MALLA. Cada subcaso es su propio bloque:
**B14-F3, B14-OFAT y B14-MALLA**. Familia **H** (caso real). 2026-10-09, commit `77b1ae8`.

### Nombre del caso:
¿Se confirman los KALINA de Húsavík con el código actual y qué pasa en las variables que no se movieron?

### Objetivo del barrido:
1. Re-evaluar los 97 KALINA de la Fase 3.
2. Barrer las variables que entonces no se movieron.
3. Mapear x_b × P_baja.

### ¿Qué se barrió?
- **F3:** los 97 puntos KALINA de septiembre, tal cual.
- **OFAT:** 10 variables, de a una, 15 valores cada una, alrededor del ancla de Húsavík.
- **MALLA:** x_b de 0.70 a 0.91 (8 valores) × P_baja de 500 a 1200 kPa (8 valores).

### ¿Por qué se barrió?
Para validar la campaña con un caso real: si el modelo actual reproduce una planta que existe, sus
conclusiones sobre el caso del profesor ganan credibilidad.

### Datos o variables barridas / Datos modificados:
Ver arriba. En OFAT y MALLA, lo que no se mueve queda en el ancla de Húsavík. Los puntos F3
conservan sus datos de septiembre: varias familias, con pisos de O2 de 283.15 y 303.55 K.
Total: **311 corridas**.

### Métodos aplicados:
Re-evaluación punto a punto; una variable a la vez (15 puntos); malla 2D completa.

### Resultados obtenidos:
- **F3: 97 de 97 KALINA, todos confiables, y ninguno cambia de clase** (A4, V21). Las η coinciden
  a 10⁻¹¹ pp.
- **OFAT (148 genuinos, 107 KALINA):** rangos KALINA con lo demás en el ancla:

| Variable | KALINA desde – hasta | Qué rompe fuera |
|---|---|---|
| T_fuente | 380 – 401 K | O2 al subir |
| T_sumidero | 273 – 283 K | O2 al subir |
| P_alta | 2821 – 4000 kPa | O2 al bajar |
| P_baja | 700 – 1200 kPa | O2 al bajar |
| x_b | 0.60 – 0.825 | O2 al subir |
| η_t, η_p, ε_reg | todo el rango probado | — |
| ε_cond | solo 0.95 | O2 al bajar |

- **MALLA:** la P_baja mínima KALINA sube con x_b: 500 kPa con x_b = 0.70, y 800 kPa con x_b ≥ 0.85.
- Con su piso de diseño (10 °C), la P_baja mínima KALINA coincide con su valor real, 690 kPa (M9).
  El motor real lo confirma (η = 12.73 %).
- Tablas: TAB-M10-00 a -03. Figuras FIG-M10-01 (malla) y FIG-M10-02 (OFAT).

### Conclusiones del caso:
1. **El modelo actual reproduce exactamente los KALINA de Húsavík** y coincide con su presión real
   de condensación. Es una validación fuerte.
2. Húsavík está, como los diseños del profesor modificado, **al filo de la cavitación (O2)**: casi
   todas las variables rompen por O2.
3. Una mezcla más rica en amoníaco (x_b alta) pide más P_baja para evitar la cavitación.

### Advertencias, supuestos y limitaciones:
- OFAT de 15 puntos: las fronteras quedan entre dos muestras; no se bisecaron.
- Solo se re-evaluaron los KALINA de septiembre, no los CORREGIBLE ni los no convergidos.
- OFAT y MALLA solo con teqp.

### Recomendaciones:
Citar Húsavík en el informe como validación del modelo, y su P_baja (690 kPa) como referencia real
dentro de la ventana de presiones de M4.

**Fuentes:** `resultados/2026-10-09_final_M10_husavik/REPORTE_M10.md`, `m10_recorrida_fase3.csv`, `m10_ofat.csv`, `m10_malla_xb_pbaja.csv`, `m10_ofat_rangos.csv`; M9 (Húsavík con el motor real); A4 (V21, V22).

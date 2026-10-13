# Ficha 4.2 — La franja KALINA con las presiones del profesor

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80.
> - **Piso de O2 = T_sumidero:** la cavitación se evalúa con el clima de cada punto.
> - **O3:** el ciclo debe producir trabajo neto positivo.

### ID del caso:
**Estudio 4.2** · Mapa con las presiones del profesor. Responde la pregunta 4: ¿Qué datos del profesor se pueden conservar?
Familia **C** · 2026-10-07 · código de origen: M05c.

### Nombre del caso:
Mapa fino de la franja KALINA conservando P_alta = 3000 y P_baja = 400 kPa.

### Objetivo del barrido:
Delimitar exactamente en qué combinaciones de T_fuente, ε_cond y T_sumidero el ciclo es KALINA con
las dos presiones del profesor.

### ¿Qué se barrió?
T_fuente, ε_cond y T_sumidero, en una malla completa.

### ¿Por qué se barrió?
estudio 2.3 encontró un KALINA con las presiones del profesor (T_fuente 403 K y ε_cond 0.95), pero el LHS
de estudio 4.1 no encontró ninguno: la franja es demasiado angosta para un muestreo al azar. Hacía falta una
malla dirigida.

### Datos o variables barridas:

| Variable | Valores | n | Unidad |
|---|---|---|---|
| T_fuente | 385 – 410, cada 2.5 | 11 | K |
| ε_cond | 0.85 / 0.875 / 0.90 / 0.925 / 0.95 | 5 | – |
| T_sumidero (= piso de O2) | 278.15 / 290.65 / 300.03 | 3 | K |

Total: **165 corridas**.

### Datos modificados:
Respecto al profesor: T_fuente (385–410 K en vez de 623.15 K), ε_cond (≥ 0.85 en vez de 0.80) y,
en dos de los tres climas, T_sumidero. **Se conservan exactamente** P_alta = 3000 kPa,
P_baja = 400 kPa, x_b = 0.50, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85 y ε_reg = 0.75.

### Métodos aplicados:
Malla completa; conteo de clases por celda; criterios que fallan a cada lado de la franja.

### Resultados obtenidos:
- **165 corridas: 149 genuinas y 104 KALINA, todos confiables** (verificación V16). Hay 15 N2.
- **Con T_fuente entre 390 y 410 K hay KALINA** en casi todas las celdas. Por debajo de 390 K, el
  ciclo produce trabajo negativo (O3, 15 de 15).
- **Con el clima del profesor (300.03 K)**, KALINA exige un condensador más efectivo:

| ε_cond | Celdas KALINA a 300.03 K | Rango de T_fuente |
|---|---|---|
| 0.85 | 0 | — |
| 0.875 | 1 | 390 K |
| 0.90 | 2 | 390–392.5 K |
| 0.925 | 4 | 390–397.5 K |
| 0.95 | 9 | 390–410 K |

- Con un clima más frío (278.15 o 290.65 K) basta ε_cond = 0.85, con T_fuente de 390 a 407.5 K.
- La mejor η de la franja es **10.81 %** (T_fuente 410 K, ε_cond 0.95, clima de 300.03 K). En estudio 6.1,
  el motor real lo confirma con la misma η.
- Tablas: 4.2-1, 4.2-2, 4.2-3. Figuras: 4.2-1.

### Conclusiones del caso:
1. **Las dos presiones del profesor (3000 y 400 kPa) son compatibles con KALINA**, conservando
   además su x_b, sus eficiencias y casi todas sus efectividades.
2. Para eso hay que **bajar la fuente a 390–410 K** y, con su clima de 300 K, **subir ε_cond a 0.875
   o más** (0.95 da toda la franja).
3. Con un sitio más frío, incluso ε_cond = 0.85 alcanza.

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 4.2-1.** La región KALINA es una **cuña**: a 300 K de sumidero, con ε_cond 0.95 hay KALINA de 390 a
  410 K; con 0.925, de 390 a ≈397; con 0.90, solo 390–392.5; con 0.875, solo 390 K; con 0.85, ninguno.
  «ε_cond ≥ 0.875» es cierto solo en el borde izquierdo (390 K); cubrir toda la franja a 300 K exige 0.95
  (el tope permitido).
- Por debajo de 390 K no hay KALINA a ningún clima (385 K: Falso convergido; 387.5 K: Inviable).
  Con sumidero frío (278/290 K) hay KALINA de 390 a ≈407 K con ε_cond ≥ 0.85.

### Advertencias, supuestos y limitaciones:
- Resolución: 2.5 K en T_fuente y 0.025 en ε_cond.
- No se exploró T_fuente > 410 K: el borde superior de la franja no está medido.
- O2 se cumple sin margen propio de subenfriamiento. estudio 6.1 muestra que exigir 2 K cuesta ~25 kPa de
  P_baja (400 → ~425 kPa).

### Recomendaciones:
Es el mejor argumento para el informe: **con las presiones del profesor, el ciclo funciona si la
fuente está a ~400 K**. Conviene, en una fase futura, extender T_fuente hasta ~430 K para cerrar el
borde superior.

**Fuentes:** `resultados/2026-10-07_final_M5c/REPORTE_M5c.md`, `m5c_malla.csv`, `m5c_frontera.csv`; estudio 6.1 (P03); verificación V16.

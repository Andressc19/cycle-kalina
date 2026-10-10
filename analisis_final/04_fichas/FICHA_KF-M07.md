# FICHA KF-M07 — La máxima eficiencia dentro de la región KALINA

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80.
> - **Arranque:** el punto de partida de una búsqueda, con los datos que esa búsqueda no puede mover.
> - **D (índice de cercanía):** qué tan lejos está un punto de cumplir todos los criterios. D = 0 es KALINA.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades.

### ID del caso:
`KF-M07`, con 5 subcasos (arranques A1 a A5). Cada arranque es su propio bloque (**B11-A1 … B11-A5**).
Familia **O** (optimización), diseño: búsqueda por patrones. 2026-10-07.

### Nombre del caso:
Búsqueda de la η máxima, con y sin datos del profesor conservados.

### Objetivo del barrido:
Dentro de la región KALINA ya acotada, encontrar la η más alta: libre, y conservando distintos datos del profesor.

### ¿Qué se barrió?
Las variables libres de cada arranque, moviéndose paso a paso hacia la mejor η.

### ¿Por qué se barrió?
Para dar una cota superior de η realista y mostrar cuánto se pierde al conservar datos del enunciado.
**Nota:** el objetivo principal de la campaña son los rangos KALINA; η es secundaria.

### Datos o variables barridas:
En cada arranque se mueven las variables que no conserva, con pasos de ±10 % del rango que se van
achicando. No es una malla: la búsqueda solo visita los puntos que le sirven. Recorrido real
(mín–máx visitado):
- A3: P_alta 3606–5000 kPa, P_baja 1140–1580 kPa, x_b 0.79–0.85.
- A4: T_fuente 391–427 K y η/ε hasta 0.95.
- A5: P_alta 4508–5000 kPa, P_baja 802–1462 kPa.

### Datos modificados:

| Arranque | Datos del profesor conservados | Parte de |
|---|---|---|
| A1 | ninguno | mejor KALINA de M4b |
| A2 | ninguno | mejor KALINA de M2S (base B2, a 278.15 K) |
| A3 | sus temperaturas (T_fuente 623.15 K, T_sumidero 300.03 K) | — |
| A4 | sus presiones (3000/400 kPa) y su clima (300.03 K) | — |
| A5 | su fuente y su x_b (623.15 K y 0.50) | — |

Caja de las variables libres: T_fuente 380–500 K, T_sumidero 278.15–303.55 K, P_alta 2000–5000 kPa,
P_baja 300–2500 kPa, x_b 0.50–0.85 y η/ε 0.40–0.95. **560 evaluaciones** en total.

### Métodos aplicados:
Búsqueda por patrones con objetivo lexicográfico: primero llegar a D = 0 y después maximizar η.
Pasos de ±10 % del rango que se dividen a la mitad cuando no hay mejora; corte en un paso < 1 % o
en 120 evaluaciones por arranque (MATEMATICA §7.2).

### Resultados obtenidos (η validadas por A4, V17):

| Arranque | η máx. | Dónde termina | ¿KALINA confiables en la búsqueda? |
|---|---|---|---|
| A1 libre | 14.98 % | P_alta 4382, P_baja 808 kPa, T_fuente 436 K | sí (98 de 102) |
| A2 libre | 15.48 % | P_alta 3000, P_baja 394 kPa, T_fuente 420 K, η_t = ε_reg = 0.95 | sí (63 de 63) |
| A3 sus temperaturas | 12.74 % | P_alta 5000, P_baja 1360 kPa, x_b 0.85 | sí (90 de 91) |
| **A4 sus presiones y su clima** | **15.60 %** | T_fuente 415 K; η_t, ε_HRVG, ε_reg y ε_cond = 0.95 | sí (80 de 80) |
| A5 su fuente y su x_b | 11.09 % | P_alta 4808, P_baja 1022 kPa | **no (0 de 83)** |

Tablas: TAB-M07-00/01/02. Figura FIG-M07-01 (η por iteración, una línea por arranque).

### Conclusiones del caso:
1. **La η más alta encontrada es 15.6 %, conservando las presiones y el clima del profesor** (A4),
   con T_fuente = 415 K y los equipos en su mejor eficiencia (0.95). El motor real la confirma.
2. Conservando las temperaturas del profesor (A3) se llega a 12.7 %, **con KALINA confiables**, a
   costa de alejarse del resto del enunciado: P_alta = 5000 kPa, P_baja ~1360 kPa y x_b = 0.85.
   Es la prueba de que la fuente de 623 K **sí** admite KALINA confiables, pero solo con mucho
   amoníaco y presiones altas, nunca con la x_b ni las presiones del profesor.
3. **Todo el arranque A5 (fuente de 623 K y x_b 0.50) queda fuera del rango confiable**: su 11.1 %
   no es un resultado de diseño.
4. Los óptimos terminan en los bordes de la caja (eficiencias en 0.95) y al filo de la cavitación:
   la η máxima depende de suponer equipos muy eficientes.

### Advertencias, supuestos y limitaciones:
- Es una búsqueda local: puede haber óptimos mejores no visitados.
- Los óptimos están al filo de O2. Con un margen de 2 K, η baja 0.3–3.7 pp según el punto (M6).
- η_t = 0.95 y ε = 0.95 son el tope del rango aceptado: son optimistas.

### Recomendaciones:
- Reportar η como una cota superior ("hasta ~15 % con equipos de alta eficiencia"), no como valor de diseño.
- Para el diseño, preferir η con eficiencias medias (~8–11 %, M3/M5c).

**Fuentes:** `resultados/2026-10-07_final_M7/REPORTE_M7.md`, `m7_evaluaciones.csv`, `m7_optimos.csv`, `m7_trayectorias.csv`; `conteo_por_subcaso.csv`; M6/M9 (motor real); A4 (V17).

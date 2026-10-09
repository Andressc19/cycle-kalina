# REPORTE M10b — Húsavík con poco amoníaco (x_b 0.30–0.70)

**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final` · **Motor:** teqp (protección A+B, bracket tolerante).

## 1. La pregunta

M10 barrió x_b de 0.60 a 0.95. ¿Qué pasa con Húsavík si la mezcla tiene poco amoníaco, entre 0.30 y 0.70? ¿Sigue habiendo KALINA? ¿Con qué P_baja? ¿Qué criterio falla?

## 2. Método

- OFAT de x_b: `numpy.linspace(0.30, 0.70, 17)` con P_baja 690 y el resto en el ancla de Húsavík (1 corridas).
- Malla x_b × P_baja: x_b [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7] × P_baja [200, 300, 400, 500, 600, 700] (1 corridas).
- Ancla: P_alta 3300, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90, eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0; piso de O2 283.15 K.
- **x_b bajo (< 0.55), fuera de lo habitual en Kalina:** es una etiqueta de reporte, no un filtro.

## 3. Por cada x_b de la malla (una tabla por valor)

### x_b = 0.30 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | NO_CONVERGIO | — | — | — | — | — | False |

### x_b = 0.35 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.40 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.45 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.50 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.55

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.60

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.65

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

### x_b = 0.70

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|

## 4. P_baja mínima KALINA para cada x_b

| x_b | P_baja mín KALINA (kPa) | n KALINA | etiqueta |
|---|---|---|---|
| 0.30 | — | 0/1 | x_b bajo (<0.55) |
| 0.35 | — | 0/0 | x_b bajo (<0.55) |
| 0.40 | — | 0/0 | x_b bajo (<0.55) |
| 0.45 | — | 0/0 | x_b bajo (<0.55) |
| 0.50 | — | 0/0 | x_b bajo (<0.55) |
| 0.55 | — | 0/0 |  |
| 0.60 | — | 0/0 |  |
| 0.65 | — | 0/0 |  |
| 0.70 | — | 0/0 |  |

## 5. Qué criterio falla con x_b bajo

Con x_b < 0.55 hay 1 filas en la malla; ninguna reporta código de falla.

## 6. Lo que no se sabe

- La malla muestrea 6 P_baja (200–700 kPa): la P_baja mínima KALINA real queda entre dos muestras; no se bisecó la frontera.
- El OFAT usa pasos de 0.025 en x_b: la frontera exacta entre clases queda entre dos muestras.
- Todo es teqp; no se re-confirmó con el motor real.
- Cambiar el ancla (T_fuente, T_sumidero, eta_t/eta_p, eps_*) mueve la frontera de clase.

# REPORTE M10b — Húsavík con poco amoníaco (x_b 0.30–0.70)

**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final` · **Motor:** teqp (protección A+B, bracket tolerante).

## 1. La pregunta

M10 barrió x_b de 0.60 a 0.95. ¿Qué pasa con Húsavík si la mezcla tiene poco amoníaco, entre 0.30 y 0.70? ¿Sigue habiendo KALINA? ¿Con qué P_baja? ¿Qué criterio falla?

## 2. Método

- OFAT de x_b: `numpy.linspace(0.30, 0.70, 17)` con P_baja 690 y el resto en el ancla de Húsavík (17 corridas).
- Malla x_b × P_baja: x_b [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7] × P_baja [200, 300, 400, 500, 600, 700] (54 corridas).
- Ancla: P_alta 3300, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90, eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0; piso de O2 283.15 K.
- **x_b bajo (< 0.55), fuera de lo habitual en Kalina:** es una etiqueta de reporte, no un filtro.

## 3. Por cada x_b de la malla (una tabla por valor)

### x_b = 0.30 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 300.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 400.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 500.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 600.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 700.0 | NO_CONVERGIO | — | — | — | — | — | False |

### x_b = 0.35 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 300.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 400.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 500.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 600.0 | NO_CONVERGIO | — | — | — | — | — | False |
| 700.0 | NO_CONVERGIO | — | — | — | — | — | False |

### x_b = 0.40 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | NO_CONVERGIO | -1.605 | 0.01136 | 18.96 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 300.0 | NO_CONVERGIO | -1.419 | 0.02036 | 30.54 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 400.0 | NO_CONVERGIO | -1.279 | 0.02645 | 39.44 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 500.0 | NO_CONVERGIO | -1.166 | 0.0312 | 46.78 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 600.0 | NO_CONVERGIO | -1.07 | 0.03524 | 53.09 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 700.0 | NO_CONVERGIO | -0.9863 | 0.03883 | 58.66 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |

### x_b = 0.45 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | NO_CONVERGIO | -0.4644 | 0.01171 | 9.472 | -0.001 | N2,O3,O5,C1,C3,C3 | False |
| 300.0 | NO_CONVERGIO | -0.4127 | 0.0212 | 20.7 | -0.001 | N2,O3,O5,C1,C3,C3 | False |
| 400.0 | NO_CONVERGIO | -0.3738 | 0.0275 | 29.34 | -0.001 | N2,O3,O5,C1,C3,C3 | False |
| 500.0 | NO_CONVERGIO | -0.342 | 0.03232 | 36.47 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 600.0 | NO_CONVERGIO | -0.315 | 0.03634 | 42.59 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |
| 700.0 | NO_CONVERGIO | -0.2914 | 0.03989 | 48 | -0.001 | N2,S6,O3,O5,C1,C3,C3 | False |

### x_b = 0.50 — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | KALINA | 0.01225 | 0.0114 | 0.4462 | 0.01801 | — | False |
| 300.0 | KALINA | 0.008266 | 0.02043 | 11.36 | 0.01801 | — | False |
| 400.0 | KALINA | 0.00552 | 0.02654 | 19.75 | 0.01801 | — | False |
| 500.0 | KALINA | 0.003484 | 0.0313 | 26.68 | 0.01801 | — | False |
| 600.0 | KALINA | 0.001911 | 0.03533 | 32.63 | 0.01801 | — | False |
| 700.0 | KALINA | 0.0006683 | 0.03892 | 37.89 | 0.01801 | — | False |

### x_b = 0.55

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | CORREGIBLE | 0.1102 | 0.01174 | -4.623 | 0.1076 | O2 | False |
| 300.0 | KALINA | 0.09562 | 0.0213 | 3.567 | 0.1076 | — | False |
| 400.0 | KALINA | 0.08474 | 0.02763 | 11.76 | 0.1076 | — | False |
| 500.0 | KALINA | 0.07607 | 0.03246 | 18.52 | 0.1076 | — | False |
| 600.0 | KALINA | 0.06885 | 0.03649 | 24.33 | 0.1076 | — | False |
| 700.0 | KALINA | 0.06265 | 0.04003 | 29.45 | 0.1076 | — | False |

### x_b = 0.60

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | CORREGIBLE | 0.1376 | 0.01178 | -10.25 | 0.2043 | O2 | False |
| 300.0 | CORREGIBLE | 0.1305 | 0.02195 | -0.396 | 0.1983 | O2 | False |
| 400.0 | KALINA | 0.1164 | 0.02862 | 4.835 | 0.1983 | — | False |
| 500.0 | KALINA | 0.1051 | 0.03359 | 11.45 | 0.1984 | — | False |
| 600.0 | KALINA | 0.09232 | 0.03764 | 17.12 | 0.1984 | — | False |
| 700.0 | KALINA | 0.0874 | 0.04117 | 22.14 | 0.1984 | — | False |

### x_b = 0.65

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | CORREGIBLE | 0.0979 | 0.01172 | -15.01 | 0.3063 | O2 | False |
| 300.0 | CORREGIBLE | 0.1503 | 0.02229 | -4.439 | 0.2903 | O2 | False |
| 400.0 | CORREGIBLE | 0.1346 | 0.02943 | -0.1034 | 0.2903 | O2 | False |
| 500.0 | KALINA | 0.1217 | 0.03464 | 5.432 | 0.2903 | — | False |
| 600.0 | KALINA | 0.111 | 0.0388 | 11 | 0.2903 | — | False |
| 700.0 | KALINA | 0.1016 | 0.04234 | 15.91 | 0.2903 | — | False |

### x_b = 0.70

| P_baja | clasificacion | eta | m_O1 | m_O2 | m_O5 | codigos_falla | fuera_rango |
|---|---|---|---|---|---|---|---|
| 200.0 | CORREGIBLE | 0.0266 | 0.01177 | -18.72 | 0.4186 | O2 | False |
| 300.0 | CORREGIBLE | 0.1623 | 0.0223 | -8.337 | 0.3917 | O2 | False |
| 400.0 | CORREGIBLE | 0.147 | 0.02995 | -0.4351 | 0.3835 | O2 | False |
| 500.0 | KALINA | 0.1331 | 0.03553 | 0.3864 | 0.3836 | — | False |
| 600.0 | KALINA | 0.1215 | 0.03988 | 5.855 | 0.3836 | — | False |
| 700.0 | KALINA | 0.1114 | 0.04351 | 10.68 | 0.3836 | — | False |

## 4. P_baja mínima KALINA para cada x_b

| x_b | P_baja mín KALINA (kPa) | n KALINA | etiqueta |
|---|---|---|---|
| 0.30 | — | 0/6 | x_b bajo (<0.55) |
| 0.35 | — | 0/6 | x_b bajo (<0.55) |
| 0.40 | — | 0/6 | x_b bajo (<0.55) |
| 0.45 | — | 0/6 | x_b bajo (<0.55) |
| 0.50 | 200 | 6/6 | x_b bajo (<0.55) |
| 0.55 | 300 | 5/6 |  |
| 0.60 | 400 | 4/6 |  |
| 0.65 | 500 | 3/6 |  |
| 0.70 | 500 | 3/6 |  |

## 5. Qué criterio falla con x_b bajo

- Con x_b = 0.30, 0.35 el solver **no converge** (NO_CONVERGIO sin códigos): el ciclo no cierra y no hay margen que evaluar.
- O1 no falla en x_b < 0.55 (margen mínimo 0.01136).
- O2 no falla en x_b < 0.55 (margen mínimo 0.4462).
- **O3 sí falla** en x_b < 0.55: margen de -70.64 a 2.008 (12 de 18 filas convergidas).
- **O5 sí falla** en x_b < 0.55: margen de -0.001 a 0.01801 (12 de 18 filas convergidas).
- Además esos puntos convergidos traen otros códigos (C1, C3, N2, S6): N2 = no genuino; S6/C1/C3 = otras restricciones del solver.
- El x_b más bajo con KALINA en la malla es **0.50** (P_baja mínima 200 kPa).

## 6. Lo que no se sabe

- La malla muestrea 6 P_baja (200–700 kPa): la P_baja mínima KALINA real queda entre dos muestras; no se bisecó la frontera.
- El OFAT usa pasos de 0.025 en x_b: la frontera exacta entre clases queda entre dos muestras.
- Todo es teqp; no se re-confirmó con el motor real.
- Cambiar el ancla (T_fuente, T_sumidero, eta_t/eta_p, eps_*) mueve la frontera de clase.

## Nota del director (Claude, auditoría 2026-10-09)

- **Con x_b ≤ 0.475 no hay ciclo Kalina en Húsavík.**
  - Entre 0.30 y 0.375 el solver ni siquiera encuentra un intervalo físico para T1.
  - Entre 0.40 y 0.475 "converge", pero de forma espuria (N2). Esos puntos tienen **O5**: el
    separador recibe líquido (q2 < 0.001). También tienen **O3**: potencia neta negativa,
    η de −0.15 a −1.6.
  - La causa física es que, con poca agua amoniacal, la mezcla se comporta como agua y una fuente de
    394 K no la evapora a 3300 kPa.
- **x_b = 0.50 es KALINA solo en lo formal.** η queda entre 0.1 y 1.2 %, con ~2 % de vapor en el
  separador (m_O5 ≈ 0.018 a 690 kPa). No es un diseño útil: es el borde de O5.
- **De 0.55 a 0.70 sí es útil.**
  - La P_baja mínima baja con menos amoníaco: 300 kPa con 0.55, 400 con 0.60 y 500 con 0.65–0.70.
  - η máxima de la malla: 16.2 %, pero es CORREGIBLE (x_b 0.70 a 300 kPa, falla O2). El mejor
    KALINA es **13.3 %** (x_b 0.70 a 500 kPa).
- **Cambio de criterio limitante con x_b.** Con x_b alto (≥ 0.85) limita **O2** (cavitación). Con x_b
  bajo (≤ 0.50) limitan **O5/O3**: no hay vapor. La ventana útil para Húsavík queda en
  **x_b ≈ 0.55–0.82** a su P_baja real, y hasta 0.91 si se sube P_baja a 800 kPa.

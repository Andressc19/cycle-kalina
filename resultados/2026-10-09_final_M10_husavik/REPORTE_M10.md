# REPORTE M10 — Húsavík revisitado (Fase 3 + barridos que faltaban)

**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final` · **Motor:** teqp (protección A+B, bracket tolerante).

## 1. La pregunta

¿Con el motor actual (después del bracket tolerante y de la protección A+B de teqp), se confirman los KALINA que en septiembre encontró la Fase 3 de Húsavík? ¿Y qué pasa en las variables que entonces no se movieron (T_fuente, T_sumidero, P_alta, P_baja, x_b fino, eta_p, eps_hrvg) y en una malla x_b × P_baja?

## 2. Catálogo (una fila por familia)

| familia | origen | variables movidas | piso O2 | n | KALINA sept | KALINA ahora | confiables ahora | coincide | d_eta_pp medio | d_eta_pp máx |
|---|---|---|---|---|---|---|---|---|---|---|
| F3-A | sept | P_alta, P_baja, x_b, eta_t, eps_reg, eps_cond | 303.6 | 14 | 14 | 14 | 14 | 14 | 0 | 0 |
| F3-B | sept | P_baja, eps_reg, eps_cond | 283.1 | 27 | 27 | 27 | 27 | 27 | 5.201e-13 | 1.404e-11 |
| F3-C | sept | P_baja x eps_reg | 283.1 | 24 | 24 | 24 | 24 | 24 | 3.055e-13 | 7.258e-12 |
| F3-D | sept | una variable por archivo (P_baja, eps_cond, eps_reg, eta_t, x_b) | 283.1 | 26 | 26 | 26 | 26 | 26 | 9.153e-13 | 2.063e-11 |
| F3-E | sept | una variable por archivo (P_alta, P_baja, x_b) | 303.6 | 6 | 6 | 6 | 6 | 6 | 4.324e-07 | 2.594e-06 |
| B1-T_fuente | nuevo | T_fuente | 283.1 | 15 | — | 7 | 7 | — | — | — |
| B1-T_sumidero | nuevo | T_sumidero | 283.1 | 15 | — | 8 | 8 | — | — | — |
| B1-P_alta | nuevo | P_alta | 283.1 | 15 | — | 12 | 12 | — | — | — |
| B1-P_baja | nuevo | P_baja | 283.1 | 15 | — | 11 | 11 | — | — | — |
| B1-x_b | nuevo | x_b | 283.1 | 15 | — | 9 | 9 | — | — | — |
| B1-eta_t | nuevo | eta_t | 283.1 | 15 | — | 15 | 15 | — | — | — |
| B1-eta_p | nuevo | eta_p | 283.1 | 15 | — | 15 | 15 | — | — | — |
| B1-eps_hrvg | nuevo | eps_hrvg | 283.1 | 15 | — | 14 | 14 | — | — | — |
| B1-eps_reg | nuevo | eps_reg | 283.1 | 15 | — | 15 | 15 | — | — | — |
| B1-eps_cond | nuevo | eps_cond | 283.1 | 15 | — | 1 | 1 | — | — | — |
| B2 | nuevo | x_b x P_baja | 283.1 | 64 | — | 49 | 49 | — | — | — |

## 3. ¿Se confirman los KALINA de septiembre?

De los **97** puntos KALINA de septiembre re-evaluados, **97** siguen KALINA (**97** además confiables: fuera_rango=False y B_verificado=True). Cambian de clase: **0**.

Ninguno cambió de clase: el motor actual (teqp con la protección A+B y el bracket tolerante) reproduce la clasificación de septiembre en los 97 puntos.

## 4. Rangos de B1 (OFAT de 15 puntos) — x_b destacada

| variable | mín KALINA | máx KALINA | rompe abajo | rompe arriba | η mín | η máx | n KALINA |
|---|---|---|---|---|---|---|---|
| T_fuente | 380 | 401.4 | — | CORREGIBLE (O2) | 0.1221 | 0.1296 | 7 |
| T_sumidero | 273.1 | 283.1 | — | CORREGIBLE (O2) | 0.1251 | 0.1296 | 8 |
| P_alta | 2821 | 4000 | CORREGIBLE (O2) | — | 0.1184 | 0.136 | 12 |
| P_baja | 700 | 1200 | CORREGIBLE (O2) | — | 0.08492 | 0.1258 | 11 |
| **x_b** | 0.6 | 0.825 | — | CORREGIBLE (O2) | 0.08816 | 0.1278 | 9 |
| eta_t | 0.75 | 0.95 | — | — | 0.1053 | 0.1346 | 15 |
| eta_p | 0.6 | 0.9 | — | — | 0.1258 | 0.1278 | 15 |
| eps_hrvg | 0.6 | 0.925 | — | CORREGIBLE (O2) | 0.1163 | 0.1299 | 14 |
| eps_reg | 0.4 | 0.95 | — | — | 0.1194 | 0.1322 | 15 |
| eps_cond | 0.95 | 0.95 | CORREGIBLE (O2) | — | 0.1273 | 0.1273 | 1 |

**x_b (lo que se pedía ampliar):** con el resto en el ancla, el punto es KALINA de x_b = 0.6 a 0.825; por debajo lo rompe — y por arriba CORREGIBLE (O2). En septiembre solo se había mirado 0.78–0.86.

## 5. B2 — la malla x_b × P_baja

| x_b | P_baja mín KALINA | P_baja máx KALINA | n KALINA | total |
|---|---|---|---|---|
| 0.70 | 500 | 1200 | 8 | 8 |
| 0.73 | 600 | 1200 | 7 | 8 |
| 0.76 | 600 | 1200 | 7 | 8 |
| 0.79 | 700 | 1200 | 6 | 8 |
| 0.82 | 700 | 1200 | 6 | 8 |
| 0.85 | 800 | 1200 | 5 | 8 |
| 0.88 | 800 | 1200 | 5 | 8 |
| 0.91 | 800 | 1200 | 5 | 8 |

El P_baja KALINA más bajo de la malla es **500 kPa**, con x_b = 0.70.

## 6. Lo que no se sabe

- B1 muestrea 15 puntos por variable: los límites exactos entre clases quedan entre dos muestras; no se bisecó la frontera.
- Solo se re-evaluaron las filas KALINA de septiembre; los puntos CORREGIBLE/INVIABLE/no convergidos de entonces no se volvieron a correr.
- B2 usa un ancla fija (T_fuente 394.15, T_sumidero 278.15, eta_t/eta_p 0.90/0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95): cambiar cualquiera de esas mueve la frontera.
- Todo es teqp; no se re-confirmó con el motor real.

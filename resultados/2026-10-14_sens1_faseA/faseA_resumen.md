# Sensibilidad 1 — Fase A: barridos OFAT alrededor de 2 centros

**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · **t_amb_diseno:** T_sumidero de cada punto (piso de O2).
**Puntos:** 273 (C1=137, C2=136) · KALINA total: 186.
Se eliminan combinaciones repetidas: el punto base (misma combinación que aparece en cada barrido) se evalúa UNA vez por centro con `variable="base"`.

## 1. Clase del punto base

- **C1** (Húsavík): KALINA (η 11.9998 %)
- **C2** (ancla A*, clima del profesor): KALINA (η 7.9405 %)

## 2. Conteo de puntos por centro y clase

| centro | puntos | KALINA | CORREGIBLE | INVIABLE | NO_CONVERGIO | genuinos |
|---|---|---|---|---|---|---|
| C1 | 137 | 93 | 34 | 1 | 9 | 128 |
| C2 | 136 | 93 | 25 | 4 | 14 | 122 |

## 3. Rangos KALINA por variable

### Centro C1

| variable | n KALINA | valores KALINA | η min [%] | η max [%] | ↓ deja KALINA | ↑ deja KALINA | contiguo |
|---|---|---|---|---|---|---|---|
| T_fuente | 15 | 363.15–438.15 | 10.2727 | 12.6604 | 353.15 → NO_CONVERGIO | 443.15 → CORREGIBLE | sí |
| T_sumidero | 2 | 280.65–283.15 | 12.1075 | 12.2174 | borde del barrido | 285.65 → CORREGIBLE | sí |
| P_alta | 13 | 2000–5000 | 8.8975 | 13.1712 | borde del barrido | borde del barrido | sí |
| P_baja | 10 | 600–1500 | 6.3018 | 12.9634 | 500 → CORREGIBLE | borde del barrido | sí |
| x_b | 8 | 0.55–0.9 | 5.8978 | 12.5771 | 0.5 → INVIABLE | 0.95 → CORREGIBLE | sí |
| eta_t | 11 | 0.4–0.95 | 5.3926 | 13.4636 | borde del barrido | borde del barrido | sí |
| eta_p | 11 | 0.4–0.95 | 11.5389 | 12.0723 | borde del barrido | borde del barrido | sí |
| eps_hrvg | 11 | 0.4–0.95 | 9.4541 | 12.3232 | borde del barrido | borde del barrido | sí |
| eps_reg | 11 | 0.4–0.95 | 11.2541 | 12.4622 | borde del barrido | borde del barrido | sí |
| eps_cond | 0 | — | — | — | borde del barrido | borde del barrido | no |

### Centro C2

| variable | n KALINA | valores KALINA | η min [%] | η max [%] | ↓ deja KALINA | ↑ deja KALINA | contiguo |
|---|---|---|---|---|---|---|---|
| T_fuente | 13 | 393.15–463.15 | 4.4143 | 11.2394 | 388.15 → INVIABLE | 473.15 → CORREGIBLE | sí |
| T_sumidero | 11 | 278.15–303.15 | 7.0792 | 8.0726 | borde del barrido | borde del barrido | sí |
| P_alta | 7 | 2000–3750 | 1.8142 | 8.6521 | borde del barrido | 4000 → NO_CONVERGIO | sí |
| P_baja | 12 | 400–1500 | 2.9757 | 9.5108 | 300 → CORREGIBLE | borde del barrido | sí |
| x_b | 2 | 0.45–0.55 | 3.7355 | 9.9385 | 0.4 → NO_CONVERGIO | 0.6 → CORREGIBLE | sí |
| eta_t | 11 | 0.4–0.95 | 3.0881 | 9.0175 | borde del barrido | borde del barrido | sí |
| eta_p | 11 | 0.4–0.95 | 6.8953 | 8.1909 | borde del barrido | borde del barrido | sí |
| eps_hrvg | 11 | 0.4–0.95 | 1.9224 | 8.4929 | borde del barrido | borde del barrido | sí |
| eps_reg | 11 | 0.4–0.95 | 5.2661 | 10.5930 | borde del barrido | borde del barrido | sí |
| eps_cond | 3 | 0.8–0.9 | 8.1029 | 8.4872 | 0.75 → CORREGIBLE | borde del barrido | sí |

## 4. Ranking por amplitud de η entre los puntos KALINA (pp)

### Centro C1

| puesto | variable | n KALINA | amplitud η [pp] |
|---|---|---|---|
| 1 | eta_t | 11 | 8.0710 |
| 2 | x_b | 8 | 6.6792 |
| 3 | P_baja | 10 | 6.6616 |
| 4 | P_alta | 13 | 4.2737 |
| 5 | eps_hrvg | 11 | 2.8691 |
| 6 | T_fuente | 15 | 2.3877 |
| 7 | eps_reg | 11 | 1.2081 |
| 8 | eta_p | 11 | 0.5333 |
| 9 | T_sumidero | 2 | 0.1098 |
| 10 | eps_cond | 0 | — |

### Centro C2

| puesto | variable | n KALINA | amplitud η [pp] |
|---|---|---|---|
| 1 | P_alta | 7 | 6.8379 |
| 2 | T_fuente | 13 | 6.8250 |
| 3 | eps_hrvg | 11 | 6.5705 |
| 4 | P_baja | 12 | 6.5351 |
| 5 | x_b | 2 | 6.2031 |
| 6 | eta_t | 11 | 5.9293 |
| 7 | eps_reg | 11 | 5.3269 |
| 8 | eta_p | 11 | 1.2956 |
| 9 | T_sumidero | 11 | 0.9934 |
| 10 | eps_cond | 3 | 0.3843 |

## 5. Preselección de equipos (mín/máx entre los KALINA)

### Centro C1

| magnitud | mínimo entre KALINA | máximo entre KALINA |
|---|---|---|
| dh_turb [kJ/kg] | 88.4013 | 220.858 |
| Wnet [kW por kg/s] | 17.5277 | 188.329 |
| Qreg/Qi | 0.0383651 | 1.17724 |
| m_O2 | 0.06056 | 33.69 |

### Centro C2

| magnitud | mínimo entre KALINA | máximo entre KALINA |
|---|---|---|
| dh_turb [kJ/kg] | 96.6599 | 260.324 |
| Wnet [kW por kg/s] | 2.93305 | 161.458 |
| Qreg/Qi | 0.114804 | 2.02182 |
| m_O2 | 0.204101 | 48.5079 |

## 6. Puntos genuinos (convergio=True y clase ≠ NO_CONVERGIO)

- **C1**: 128 genuinos de 137; los N2 espurios (convergio=True y clase NO_CONVERGIO) no cuentan.
- **C2**: 122 genuinos de 136; los N2 espurios (convergio=True y clase NO_CONVERGIO) no cuentan.

Resumen por variable en `faseA_resumen_variables.csv` (22 filas).

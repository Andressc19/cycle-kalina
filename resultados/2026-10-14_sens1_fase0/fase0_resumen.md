# Sensibilidad 1 — Fase 0: H*, no-regresión y escalado con m_b

**Fecha:** 2026-10-14 · **Motor:** teqp · **t_amb_diseno:** 283.15 K · **H\*** = Húsavík (T_fuente 394.15, T_sumidero 278.15, P_alta 3300, P_baja 690, x_b 0.82, m_b 1.0, eta_t 0.85, eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.90).

## 1. Los 11 puntos

| id_punto | clasificacion | convergio | eta [%] | Wnet | m_O2 | Qi | Qreg | dh_turb | t_s |
|---|---|---|---|---|---|---|---|---|---|
| H0 | CORREGIBLE | True | 12.4178 | 111.323 | -0.260932 | 896.476 | 116.21 | 188.195 | 44.35 |
| H0_noextra | CORREGIBLE | True | 12.4178 | 111.323 | -0.260932 | — | — | — | 43.82 |
| M5 | CORREGIBLE | True | 12.4178 | 556.614 | -0.260932 | 4482.38 | 581.051 | 188.195 | 44.79 |
| M10 | CORREGIBLE | True | 12.4178 | 1113.23 | -0.260932 | 8964.76 | 1162.1 | 188.195 | 43.66 |
| M15 | CORREGIBLE | True | 12.4178 | 1669.84 | -0.260932 | 13447.1 | 1743.15 | 188.195 | 45.38 |
| M20 | CORREGIBLE | True | 12.4178 | 2226.46 | -0.260932 | 17929.5 | 2324.2 | 188.195 | 43.09 |
| E95 | KALINA | True | 11.9998 | 110.802 | 0.795421 | 923.367 | 129.276 | 187.827 | 48.08 |
| E85 | CORREGIBLE | True | 12.7234 | 110.351 | -0.587907 | 867.307 | 102.4 | 188.595 | 51.14 |
| E80 | CORREGIBLE | True | 12.8484 | 107.325 | -0.967793 | 835.317 | 87.6987 | 189.038 | 48.55 |
| P600 | CORREGIBLE | True | 13.3621 | 119.815 | -0.383086 | 896.678 | 116.307 | 203.014 | 46.03 |
| P800 | CORREGIBLE | True | 11.3596 | 101.785 | -0.121939 | 896.027 | 115.995 | 172.174 | 35.78 |

## 2. Control de no-regresión (H0 vs H0_noextra)

- η: H0 = 0.124178181789 · H0_noextra = 0.124178181789 · |Δη| = 0.000e+00 → OK (< 1e-9)
- Wnet: H0 = 111.322818179 · H0_noextra = 111.322818179 · |ΔWnet| = 0.000e+00 → iguales
- clasificacion: H0 = CORREGIBLE · H0_noextra = CORREGIBLE → iguales

**Control de no-regresión: PASA** (H0 con extra=True y H0_noextra con extra=False deben coincidir en η, Wnet y clase).

## 3. Escalado con m_b (H0, M5, M10, M15, M20)

| id_punto | m_b | eta | \|Δη\| vs H0 | misma clase | Wnet/m_b ÷ H0 | Qi/m_b ÷ H0 | Qreg/m_b ÷ H0 |
|---|---|---|---|---|---|---|---|
| H0 | 1 | 0.1241781818 | 0.000e+00 | sí | 1 | 1 | 1 |
| M5 | 5 | 0.1241781818 | 1.637e-11 | sí | 0.9999999999 | 1 | 1 |
| M10 | 10 | 0.1241781818 | 1.637e-11 | sí | 0.9999999999 | 1 | 1 |
| M15 | 15 | 0.1241781818 | 6.274e-12 | sí | 1 | 1 | 1 |
| M20 | 20 | 0.1241781818 | 1.637e-11 | sí | 0.9999999999 | 1 | 1 |

Desviación máxima de η respecto a H0: **1.637e-11** (tol 1e-06).
Desviación máxima de las razones (|razón − 1|): Wnet/m_b = **1.318e-10**, Qi/m_b = **4.444e-12**, Qreg/m_b = **2.435e-11** (tol 0.0001).
¿Misma clasificación en los cinco?: **sí**.

**ESCALA**: η y la clase se mantienen y las potencias escalan con m_b dentro de tolerancia.

## 4. Puntos genuinos

Puntos genuinos (convergio=True y clasificacion != NO_CONVERGIO): **11 de 11** (H0, H0_noextra, M5, M10, M15, M20, E95, E85, E80, P600, P800).
Los N2 espurios no cuentan como genuinos.

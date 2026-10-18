# Sensibilidad 1 — Ronda 1 (barridos N1, N3, N4)

**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 · **t_amb_diseno:** T_sumidero de cada punto. **KALINA confiable:** clase KALINA, `fuera_rango` falso/vacio y `eta_*`/`eps_*` en [0.40, 0.95]; **KALINA fuera de rango** se reporta aparte.

## 1. Resumen por barrido y centro

| barrido | centro | puntos | KALINA | CORR | INV | NOCONV | confiables | fuera rango | eta min [%] | eta med [%] | eta max [%] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N1 | NA | 343 | 159 | 59 | 6 | 119 | 47 | 112 | 1.21 | 4.82 | 13.60 |
| N3 | C1 | 192 | 17 | 126 | 47 | 2 | 17 | 0 | 6.42 | 8.13 | 12.12 |
| N4 | C1 | 49 | 34 | 13 | 0 | 2 | 34 | 0 | 2.24 | 5.78 | 12.02 |
| N4 | C2 | 49 | 13 | 21 | 7 | 8 | 13 | 0 | 2.86 | 5.86 | 8.65 |
| N4 | TOTAL | 98 | 47 | 34 | 7 | 10 | 47 | 0 | 2.24 | 5.86 | 12.02 |

## 2. N1 — ventana de presiones por temperatura de fuente

| T [C] | puntos | conf | fuera | P_alta p10-p90 | P_baja p10-p90 | x_b p10-p90 | T_sum p10-p90 | eta_max [%] | punto eta_max |
|---|---|---|---|---|---|---|---|---|---|
| 70 | 25 | 2 | 0 | 1687–2143 | 777–833 | 0.705–0.745 | 282.1–286.9 | 5.26 | N1-T070-09 |
| 90 | 27 | 8 | 0 | 1656–3141 | 784–1634 | 0.564–0.869 | 279.55–299.25 | 5.33 | N1-T090-12 |
| 110 | 26 | 12 | 0 | 1814–3862 | 803–1708 | 0.505–0.907 | 282.5–298.35 | 11.15 | N1-T110-06 |
| 130 | 25 | 10 | 0 | 2112–3805 | 628–1585 | 0.483–0.742 | 278.95–299.15 | 9.96 | N1-T130-11 |
| 150 | 24 | 11 | 2 | 2080–4332 | 706–1756 | 0.43–0.746 | 279.7–290.8 | 13.60 | N1-T150-01 |
| 170 | 28 | 2 | 18 | 1870–4568 | 602–1847 | 0.398–0.827 | 280.95–301.5 | 14.82 | N1-T170-14 |
| 190 | 26 | 1 | 15 | 2210–4460 | 710–1890 | 0.37–0.77 | 282.25–298.25 | 12.68 | N1-T190-01 |
| 210 | 28 | 1 | 15 | 2230–4520 | 935–1815 | 0.365–0.78 | 280.25–298 | 10.37 | N1-T210-09 |
| 230 | 27 | 0 | 16 | 2200–4410 | 715–1815 | 0.375–0.77 | 280.5–297.5 | 9.26 | N1-T230-04 |
| 250 | 26 | 0 | 10 | 2861–4844 | 1059–1807 | 0.389–0.743 | 281.2–297.1 | 11.41 | N1-T250-22 |
| 270 | 27 | 0 | 12 | 2384–4252 | 997–1754 | 0.361–0.739 | 280.7–295.4 | 8.35 | N1-T270-20 |
| 290 | 27 | 0 | 13 | 2130–4590 | 934–1840 | 0.336–0.73 | 280.2–301.2 | 10.93 | N1-T290-20 |
| 300 | 27 | 0 | 11 | 1880–4380 | 1020–1800 | 0.35–0.65 | 280.5–298.5 | 8.38 | N1-T300-05 |

## 3. N3 — frontera del condensador (P_baja minima con KALINA)

| T_sum [C] | eps_cond | P_baja min [kPa] | eta [%] | estado |
|---|---|---|---|---|
| 10 | 0.60 | — | — | ninguna |
| 10 | 0.65 | — | — | ninguna |
| 10 | 0.70 | — | — | ninguna |
| 10 | 0.75 | — | — | ninguna |
| 10 | 0.80 | — | — | ninguna |
| 10 | 0.85 | 1250 | 8.45 | kalina |
| 10 | 0.90 | 1000 | 9.87 | kalina |
| 10 | 0.95 | 700 | 12.12 | kalina |
| 20 | 0.60 | — | — | ninguna |
| 20 | 0.65 | — | — | ninguna |
| 20 | 0.70 | — | — | ninguna |
| 20 | 0.75 | — | — | ninguna |
| 20 | 0.80 | — | — | ninguna |
| 20 | 0.85 | — | — | ninguna |
| 20 | 0.90 | 1250 | 8.43 | kalina |
| 20 | 0.95 | 1000 | 9.88 | kalina |
| 30 | 0.60 | — | — | ninguna |
| 30 | 0.65 | — | — | ninguna |
| 30 | 0.70 | — | — | ninguna |
| 30 | 0.75 | — | — | ninguna |
| 30 | 0.80 | — | — | ninguna |
| 30 | 0.85 | — | — | ninguna |
| 30 | 0.90 | — | — | ninguna |
| 30 | 0.95 | 1250 | 8.44 | kalina |

Mallas: ver `ronda1_N3_mallas.md` y `ronda1_N4_mallas.md`.

## 4. Equipos (min / mediana / max entre KALINA confiables)

| barrido | centro | magnitud | n | minimo | mediana | maximo |
|---|---|---|---|---|---|---|
| N1 | NA | dh_turb [kJ/kg] | 47 | 41.9594 | 107.505 | 300.872 |
| N1 | NA | Wnet/m_b [kW por kg/s] | 47 | 2.61371 | 39.2901 | 107.672 |
| N1 | NA | Qi/m_b [kW por kg/s] | 47 | 202.986 | 724.056 | 1552.64 |
| N1 | NA | Qreg/Qi | 47 | 0.0115855 | 0.256574 | 1.63242 |
| N1 | NA | Qout/m_b [kW por kg/s] | 47 | 195.238 | 659.766 | 1481.5 |
| N1 | NA | P_alta/P_baja | 47 | 1.37594 | 2.17112 | 10.4878 |
| N3 | C1 | dh_turb [kJ/kg] | 17 | 99.8492 | 121.716 | 186.472 |
| N3 | C1 | Wnet/m_b [kW por kg/s] | 17 | 58.2887 | 71.5926 | 110.211 |
| N3 | C1 | Qi/m_b [kW por kg/s] | 17 | 850.907 | 881.096 | 909.683 |
| N3 | C1 | Qreg/Qi | 17 | 0.111416 | 0.123574 | 0.134759 |
| N3 | C1 | Qout/m_b [kW por kg/s] | 17 | 779.985 | 799.473 | 850.306 |
| N3 | C1 | P_alta/P_baja | 17 | 2.2 | 2.64 | 4.71429 |
| N4 | C1 | dh_turb [kJ/kg] | 34 | 54.2412 | 128.2 | 190.449 |
| N4 | C1 | Wnet/m_b [kW por kg/s] | 34 | 6.47265 | 46.2553 | 134.516 |
| N4 | C1 | Qi/m_b [kW por kg/s] | 34 | 228.404 | 820.189 | 1424.49 |
| N4 | C1 | Qreg/Qi | 34 | 0.0315281 | 0.230488 | 1.57681 |
| N4 | C1 | Qout/m_b [kW por kg/s] | 34 | 221.931 | 758.789 | 1379.03 |
| N4 | C1 | P_alta/P_baja | 34 | 1.44928 | 2.53623 | 4.34783 |
| N4 | C2 | dh_turb [kJ/kg] | 13 | 85.511 | 160.218 | 220.539 |
| N4 | C2 | Wnet/m_b [kW por kg/s] | 13 | 5.28131 | 28.7455 | 47.9252 |
| N4 | C2 | Qi/m_b [kW por kg/s] | 13 | 184.508 | 549.023 | 960.612 |
| N4 | C2 | Qreg/Qi | 13 | 0.154961 | 0.419546 | 1.80008 |
| N4 | C2 | Qout/m_b [kW por kg/s] | 13 | 179.227 | 503.914 | 920.541 |
| N4 | C2 | P_alta/P_baja | 13 | 1.77418 | 3.10482 | 5.32255 |
| N4 | TOTAL | dh_turb [kJ/kg] | 47 | 54.2412 | 131.161 | 220.539 |
| N4 | TOTAL | Wnet/m_b [kW por kg/s] | 47 | 5.28131 | 40.7852 | 134.516 |
| N4 | TOTAL | Qi/m_b [kW por kg/s] | 47 | 184.508 | 713.203 | 1424.49 |
| N4 | TOTAL | Qreg/Qi | 47 | 0.0315281 | 0.290643 | 1.80008 |
| N4 | TOTAL | Qout/m_b [kW por kg/s] | 47 | 179.227 | 655.501 | 1379.03 |
| N4 | TOTAL | P_alta/P_baja | 47 | 1.44928 | 2.53623 | 5.32255 |

## 5. Conclusiones

### N1 — ventana por temperatura

- KALINA confiable en 8 de 13 niveles (70 a 210 C).
- eta maxima 14.82% a T=170 C (punto N1-T170-14: P_alta=4550, P_baja=610, x_b=0.73, T_sum=282 K).
- Ventanas p10-p90 por nivel: ver tabla de la seccion 2 y `ronda1_N1_por_temperatura.csv`.

### N3 — menor eps_cond que sirve por clima

- T=10 C: eps_cond min 0.85 con KALINA a P_baja=1250 kPa (eta 8.45%).
- T=20 C: eps_cond min 0.90 con KALINA a P_baja=1250 kPa (eta 8.43%).
- T=30 C: eps_cond min 0.95 con KALINA a P_baja=1250 kPa (eta 8.44%).

### N4 — KALINA confiable con P_alta <= 2000 kPa

- C1: 25 KALINA con P_alta<=2000 kPa; eta max 8.78%.
- C2: 10 KALINA con P_alta<=2000 kPa; eta max 8.22%.

### Puntos con tiempo agotado (tope 600 s)

- Ninguno.


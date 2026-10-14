# Sensibilidad 1 — Fase B: mallas de 2 variables alrededor de 2 centros

**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · **t_amb_diseno:** T_sumidero de cada punto (piso de O2).
**Puntos únicos evaluados:** 542 (C1=271, C2=271). Cada par es una malla 7×7 (49 celdas); las combinaciones repetidas entre pares (base y líneas-coordenada) se evalúan una vez y se reutilizan.

**KALINA confiable:** `clasificacion == KALINA`, `fuera_rango` falso y todos los `eta_*`/`eps_*` en [0.40, 0.95].

## 1. Tabla por par

| centro | par | variable 1 × variable 2 | KALINA | confiables | área [%] | η min [%] | η max [%] | real | esperado | interacción |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | B1 | T_fuente × P_baja | 39 | 34 | 79.59 | 6.23 | 12.96 | 39 | 35 | no |
| C1 | B2 | P_baja × x_b | 43 | 43 | 87.76 | 3.46 | 13.35 | 43 | 30 | no |
| C1 | B3 | P_alta × P_baja | 41 | 41 | 83.67 | 3.73 | 14.01 | 41 | 25 | no |
| C1 | B4 | eps_cond × T_sumidero | 3 | 3 | 6.12 | 12.00 | 12.22 | 3 | 3 | — |
| C1 | B5 | eps_reg × eta_t | 49 | 49 | 100.00 | 6.55 | 13.95 | 49 | 49 | — |
| C1 | B6 | eps_hrvg × T_fuente | 46 | 45 | 93.88 | 2.12 | 12.66 | 46 | 49 | sí |
| C2 | B1 | T_fuente × P_baja | 35 | 20 | 71.43 | 2.20 | 11.76 | 35 | 36 | sí |
| C2 | B2 | P_baja × x_b | 23 | 23 | 46.94 | 1.81 | 9.94 | 23 | 18 | no |
| C2 | B3 | P_alta × P_baja | 41 | 41 | 83.67 | 0.62 | 10.52 | 41 | 36 | no |
| C2 | B4 | eps_cond × T_sumidero | 33 | 33 | 67.35 | 7.08 | 8.49 | 33 | 12 | no |
| C2 | B5 | eps_reg × eta_t | 49 | 49 | 100.00 | 3.05 | 12.02 | 49 | 49 | — |
| C2 | B6 | eps_hrvg × T_fuente | 39 | 26 | 79.59 | 0.71 | 11.24 | 39 | 42 | sí |

## 2. Rango conjunto con KALINA

- **C1 B1**: KALINA con T_fuente ∈ [90, 165] y P_baja ∈ [600, 1300] (39/49 puntos; sin interacción).
- **C1 B2**: KALINA con P_baja ∈ [500, 1300] y x_b ∈ [0.55, 0.95] (43/49 puntos; sin interacción).
- **C1 B3**: KALINA con P_alta ∈ [2000, 5000] y P_baja ∈ [600, 1300] (41/49 puntos; sin interacción).
- **C1 B4**: KALINA con eps_cond ∈ [0.95, 0.95] y T_sumidero ∈ [278.15, 283.15] (3/49 puntos; sin interacción).
- **C1 B5**: KALINA con eps_reg ∈ [0.5, 0.95] y eta_t ∈ [0.5, 0.95] (49/49 puntos; sin interacción).
- **C1 B6**: KALINA con eps_hrvg ∈ [0.5, 0.95] y T_fuente ∈ [90, 165] (46/49 puntos; hay interacción (real < esperado)).
- **C2 B1**: KALINA con T_fuente ∈ [120, 190] y P_baja ∈ [400, 1200] (35/49 puntos; hay interacción (real < esperado)).
- **C2 B2**: KALINA con P_baja ∈ [400, 1200] y x_b ∈ [0.45, 0.7] (23/49 puntos; sin interacción).
- **C2 B3**: KALINA con P_alta ∈ [2000, 3750] y P_baja ∈ [400, 1200] (41/49 puntos; sin interacción).
- **C2 B4**: KALINA con eps_cond ∈ [0.65, 0.95] y T_sumidero ∈ [278.15, 303.15] (33/49 puntos; sin interacción).
- **C2 B5**: KALINA con eps_reg ∈ [0.5, 0.95] y eta_t ∈ [0.5, 0.95] (49/49 puntos; sin interacción).
- **C2 B6**: KALINA con eps_hrvg ∈ [0.5, 0.95] y T_fuente ∈ [120, 190] (39/49 puntos; hay interacción (real < esperado)).

## 3. Preselección de equipos (mín/máx entre KALINA confiables)

| centro | par | magnitud | mínimo | máximo |
|---|---|---|---|---|
| C1 | B1 | dh_turb [kJ/kg] | 104.91 | 210.964 |
| C1 | B1 | Wnet/m_b [kW por kg/s] | 32.0506 | 158.792 |
| C1 | B1 | Qreg/Qi | 0.0736745 | 0.358683 |
| C1 | B1 | Qout/m_b [kW por kg/s] | 457.651 | 1157.77 |
| C1 | B1 | P_alta/P_baja | 2.53846 | 5.5 |
| C1 | B2 | dh_turb [kJ/kg] | 110.309 | 233.707 |
| C1 | B2 | Wnet/m_b [kW por kg/s] | 10.2687 | 138.554 |
| C1 | B2 | Qreg/Qi | 0.0280594 | 1.1773 |
| C1 | B2 | Qout/m_b [kW por kg/s] | 276.085 | 1089.73 |
| C1 | B2 | P_alta/P_baja | 2.53846 | 6.6 |
| C1 | B3 | dh_turb [kJ/kg] | 59.2503 | 231.028 |
| C1 | B3 | Wnet/m_b [kW por kg/s] | 41.6735 | 120.336 |
| C1 | B3 | Qreg/Qi | 0.0754305 | 0.303065 |
| C1 | B3 | Qout/m_b [kW por kg/s] | 590.057 | 1075.86 |
| C1 | B3 | P_alta/P_baja | 1.53846 | 8.33333 |
| C1 | B4 | dh_turb [kJ/kg] | 187.827 | 188.014 |
| C1 | B4 | Wnet/m_b [kW por kg/s] | 110.802 | 111.142 |
| C1 | B4 | Qreg/Qi | 0.134767 | 0.140005 |
| C1 | B4 | Qout/m_b [kW por kg/s] | 798.564 | 812.565 |
| C1 | B4 | P_alta/P_baja | 4.78261 | 4.78261 |
| C1 | B5 | dh_turb [kJ/kg] | 110.221 | 210.349 |
| C1 | B5 | Wnet/m_b [kW por kg/s] | 62.7028 | 125.031 |
| C1 | B5 | Qreg/Qi | 0.0896024 | 0.182952 |
| C1 | B5 | Qout/m_b [kW por kg/s] | 770.651 | 894.031 |
| C1 | B5 | P_alta/P_baja | 4.78261 | 4.78261 |
| C1 | B6 | dh_turb [kJ/kg] | 57.1741 | 218.391 |
| C1 | B6 | Wnet/m_b [kW por kg/s] | 7.39581 | 179.755 |
| C1 | B6 | Qreg/Qi | 0.0484669 | 0.795222 |
| C1 | B6 | Qout/m_b [kW por kg/s] | 264.781 | 1240.51 |
| C1 | B6 | P_alta/P_baja | 4.78261 | 4.78261 |
| C2 | B1 | dh_turb [kJ/kg] | 122.536 | 260.324 |
| C2 | B1 | Wnet/m_b [kW por kg/s] | 4.29004 | 47.6532 |
| C2 | B1 | Qreg/Qi | 0.646452 | 1.53659 |
| C2 | B1 | Qout/m_b [kW por kg/s] | 184.405 | 425.522 |
| C2 | B1 | P_alta/P_baja | 2.5 | 7.5 |
| C2 | B2 | dh_turb [kJ/kg] | 123.317 | 261.859 |
| C2 | B2 | Wnet/m_b [kW por kg/s] | 3.59121 | 72.1268 |
| C2 | B2 | Qreg/Qi | 0.209291 | 1.67589 |
| C2 | B2 | Qout/m_b [kW por kg/s] | 189.119 | 705.374 |
| C2 | B2 | P_alta/P_baja | 2.5 | 7.5 |
| C2 | B3 | dh_turb [kJ/kg] | 74.2536 | 277.819 |
| C2 | B3 | Wnet/m_b [kW por kg/s] | 1.06285 | 52.6429 |
| C2 | B3 | Qreg/Qi | 0.419006 | 2.02241 |
| C2 | B3 | Qout/m_b [kW por kg/s] | 166.996 | 530.015 |
| C2 | B3 | P_alta/P_baja | 1.66667 | 9.375 |
| C2 | B4 | dh_turb [kJ/kg] | 220.246 | 220.7 |
| C2 | B4 | Wnet/m_b [kW por kg/s] | 24.9976 | 25.946 |
| C2 | B4 | Qreg/Qi | 0.852747 | 1.01555 |
| C2 | B4 | Qout/m_b [kW por kg/s] | 279.691 | 328.114 |
| C2 | B4 | P_alta/P_baja | 5.32255 | 5.32255 |
| C2 | B5 | dh_turb [kJ/kg] | 129.27 | 247.19 |
| C2 | B5 | Wnet/m_b [kW por kg/s] | 12.3196 | 30.8066 |
| C2 | B5 | Qreg/Qi | 0.482395 | 1.47084 |
| C2 | B5 | Qout/m_b [kW por kg/s] | 225.497 | 391.434 |
| C2 | B5 | P_alta/P_baja | 5.32255 | 5.32255 |
| C2 | B6 | dh_turb [kJ/kg] | 210.192 | 234.932 |
| C2 | B6 | Wnet/m_b [kW por kg/s] | 0.976227 | 64.9831 |
| C2 | B6 | Qreg/Qi | 0.447515 | 2.18664 |
| C2 | B6 | Qout/m_b [kW por kg/s] | 136.97 | 561.364 |
| C2 | B6 | P_alta/P_baja | 5.32255 | 5.32255 |


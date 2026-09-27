# Reporte - Validacion por tendencias vs Elsayed et al. (2013) / Embaye et al.

Tarea 2026-09-24-validacion-tendencias-embaye. 33 filas (27 convergen). Metodo reusado de scripts/calibracion_elsayed_malla.py (igual que el punto unico VALIDACION_ELSAYED2013.md): P_baja = burbuja a (T_sumidero+4 K, x_b); eps* por despeje de un paso del pinch 4 K; T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1; teqp + 3 controles AmmoniaWaterAdapter; curvas paper LEIDAS (no recalculadas); nunca se extrapola => 333 K x_b=0.65 sin eta_paper.

Figura: `resultados/2026-09-24_validacion_tendencias/comparacion_tendencias_v2.png` (4 paneles: Fig. 7, Fig. 3, Fig. 2+Fig. 5 y paridad; 6 de 33 puntos no convergieron y no se dibujan; P en bar; sustituye a la anterior `comparacion_tendencias.png`).

## 1. Tabla de todos los puntos

| serie | T_fuente | P_alta | x_b | motor | P_baja | eps_hrvg | eps_reg | eps_cond | conv | eta_mod | eta_pap | dpp | drel% | q4 | Wnet | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig7_KCS11_0p55 | 373.0 | 1100 | 0.55 | teqp | 273.5 | 0.9130 | 0.9287 | 0.9709 | SI | 9.3592 | 9.7810 | -0.4218 | -4.3130 | 0.956 | 57.3 | - |
| Fig7_KCS11_0p55 | 373.0 | 1200 | 0.55 | teqp | 273.5 | 0.9084 | 0.9315 | 0.9690 | SI | 9.8778 | 10.2824 | -0.4046 | -3.9350 | 0.955 | 56.1 | - |
| Fig7_KCS11_0p55 | 373.0 | 1500 | 0.55 | teqp | 273.5 | 0.8882 | 0.9380 | 0.9625 | SI | 11.0554 | 11.4317 | -0.3763 | -3.2920 | 0.953 | 49.2 | - |
| Fig7_KCS11_0p55 | 373.0 | 1800 | 0.55 | teqp | 273.5 | 0.8548 | 0.9429 | 0.9540 | SI | 11.7057 | 11.9892 | -0.2835 | -2.3650 | 0.952 | 38.9 | - |
| Fig7_KCS11_0p55 | 373.0 | 2000 | 0.55 | teqp | 273.5 | 0.8199 | 0.9457 | 0.9464 | SI | 11.7791 | 11.8911 | -0.1120 | -0.9420 | 0.952 | 30.5 | - |
| Fig7_KCS11_0p55 | 373.0 | 2200 | 0.55 | teqp | 273.5 | 0.7665 | 0.9481 | 0.9357 | SI | 11.3286 | 10.9521 | 0.3765 | 3.4370 | 0.951 | 21.0 | - |
| Fig7_KCS11_0p55 | 373.0 | 2300 | 0.55 | teqp | 273.5 | 0.7281 | 0.9492 | 0.9286 | SI | 10.7057 | 9.5470 | 1.1587 | 12.1370 | 0.950 | 16.0 | - |
| Fig7_KCS11_0p66 | 373.0 | 1100 | 0.66 | teqp | 410.2 | 0.9375 | 0.9106 | 0.9780 | SI | 7.2539 | 7.4325 | -0.1786 | -2.4030 | 0.967 | 64.1 | - |
| Fig7_KCS11_0p66 | 373.0 | 1500 | 0.66 | teqp | 410.2 | 0.9308 | 0.9204 | 0.9741 | SI | 9.3514 | 9.5212 | -0.1698 | -1.7830 | 0.961 | 69.1 | - |
| Fig7_KCS11_0p66 | 373.0 | 2000 | 0.66 | teqp | 410.2 | 0.9110 | 0.9316 | 0.9684 | SI | 11.0216 | 11.1671 | -0.1455 | -1.3030 | 0.959 | 64.0 | - |
| Fig7_KCS11_0p66 | 373.0 | 2500 | 0.66 | teqp | 410.2 | 0.8697 | 0.9396 | 0.9604 | SI | 11.9131 | 11.9770 | -0.0639 | -0.5340 | 0.956 | 50.2 | - |
| Fig7_KCS11_0p66 | 373.0 | 3000 | 0.66 | teqp | 410.2 | 0.7698 | 0.9462 | 0.9457 | SI | 11.6095 | 11.3358 | 0.2737 | 2.4150 | 0.944 | 28.1 | - |
| Fig3_15bar | 373.0 | 1500.0 | 0.45 | teqp | 161.5 | 0.7633 | 0.9490 | 0.9307 | SI | 11.5568 | 11.0417 | 0.5151 | 4.6650 | 0.943 | 18.4 | - |
| Fig3_15bar | 373.0 | 1500.0 | 0.55 | teqp | 273.5 | 0.8882 | 0.9380 | 0.9625 | SI | 11.0554 | 11.3942 | -0.3388 | -2.9740 | 0.953 | 49.2 | - |
| Fig3_15bar | 373.0 | 1500.0 | 0.65 | teqp | 398.1 | 0.9283 | 0.9223 | 0.9734 | SI | 9.4917 | 9.6708 | -0.1791 | -1.8520 | 0.960 | 67.7 | - |
| Fig3_15bar | 373.0 | 1500.0 | 0.75 | teqp | 508.7 | 0.9485 | 0.8973 | 0.9790 | SI | 8.2904 | 8.3190 | -0.0286 | -0.3440 | 0.966 | 79.7 | - |
| Fig3_15bar | 373.0 | 1500.0 | 0.85 | teqp | 595.2 | 0.9607 | 0.8979 | 0.9821 | SI | 7.5063 | 7.4583 | 0.0480 | 0.6430 | 0.970 | 89.2 | - |
| Fig3_15bar | 423.0 | 1500.0 | 0.45 | teqp | 161.5 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cub |
| Fig3_15bar | 423.0 | 1500.0 | 0.6 | teqp | 336.1 | 0.9166 | 0.9490 | 0.9865 | SI | 9.8449 | 10.1058 | -0.2609 | -2.5820 | 0.940 | 149.4 | - |
| Fig3_15bar | 423.0 | 1500.0 | 0.75 | teqp | 508.7 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cub |
| Fig3_15bar | 333.0 | 1500.0 | 0.65 | teqp | 398.1 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: equilibrio_liquido_vapor(P=1500.0 kPa, T |
| Fig3_15bar | 333.0 | 1500.0 | 0.75 | teqp | 508.7 | 0.7082 | 0.8668 | 0.9546 | SI | 7.2354 | 7.3562 | -0.1208 | -1.6420 | - | 22.1 | - |
| Fig3_15bar | 333.0 | 1500.0 | 0.85 | teqp | 595.2 | 0.8882 | 0.7055 | 0.9735 | SI | 6.8760 | 6.9394 | -0.0634 | -0.9140 | - | 49.1 | - |
| Fig2_10bar | 373.0 | 1000.0 | 0.45 | teqp | 161.5 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cub |
| Fig2_10bar | 373.0 | 1000.0 | 0.6 | teqp | 336.1 | 0.9282 | 0.9160 | 0.9761 | SI | 7.6860 | 7.9883 | -0.3023 | -3.7840 | 0.963 | 60.4 | - |
| Fig2_10bar | 373.0 | 1000.0 | 0.8 | teqp | 554.7 | 0.9519 | 0.9255 | 0.9831 | SI | 4.7599 | 4.6896 | 0.0703 | 1.5000 | 0.979 | 58.3 | - |
| Fig5_32bar | 423.0 | 3200.0 | 0.6 | teqp | 336.1 | 0.9301 | 0.9600 | 0.9765 | SI | 14.9090 | 15.2025 | -0.2935 | -1.9310 | 0.915 | 124.2 | - |
| Fig5_32bar | 423.0 | 3200.0 | 0.8 | teqp | 554.7 | 0.9518 | 0.9474 | 0.9839 | SI | 13.0771 | 13.0651 | 0.0120 | 0.0920 | 0.928 | 182.2 | - |
| Fig5_32bar | 463.0 | 3200.0 | 0.6 | teqp | 336.1 | 0.9175 | 0.9608 | 0.9883 | SI | 13.9682 | 14.2777 | -0.3095 | -2.1670 | 0.903 | 263.9 | - |
| Fig5_32bar | 463.0 | 3200.0 | 0.8 | teqp | 554.7 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: T_from_Ph(P, h, x): el motor teqp no cub |
| Fig7_KCS11_0p55 | 373.0 | 1500.0 | 0.55 | AmmoniaWater | 273.5 | 0.8882 | 0.9380 | 0.9625 | SI | 11.0542 | 11.4317 | -0.3775 | -3.3020 | 0.953 | 49.2 | - |
| Fig7_KCS11_0p66 | 373.0 | 2500.0 | 0.66 | AmmoniaWater | 410.2 | 0.8698 | 0.9396 | 0.9604 | SI | 11.9119 | 11.9770 | -0.0651 | -0.5440 | 0.956 | 50.2 | - |
| Fig3_15bar | 423.0 | 1500.0 | 0.6 | AmmoniaWater | 336.1 | - | - | - | NO | - | - | - | - | - | - | PropertyRangeError: h(P, s, x): el motor NH3-H2O portado no  |

## 2. Estadistica global (comparables: motor teqp, convergen, q4>=0.90, eta_paper disponible)

n=23 | d.medio=-0.0615 pp | |d|.medio=0.2749 pp | |d|.max=1.1587 pp (12.1 %) | mediana |d rel|=2.365 %.

- Los 2 puntos AmmoniaWater que convergen (seccion 6) son control del motor (iapws) y NO se
  suman a la estadistica; el 3er punto AmmoniaWater no convergio.

## 3. Fig. 7 x_b=0.55: forma (sube-maximo-baja) y posicion del maximo

Paper: max eta=12.01 % a P=19.10 bar. Modelo (teqp, 1100-2300 kPa): max eta=11.78 % a P=20.00 bar.

## 4. Fig. 3, 373 K: signo de pendientes eta vs x_b (modelo vs paper)

- 0.45->0.55: mod 11.56->11.06 (-), paper 11.04->11.39 (+) => difiere
- 0.55->0.65: mod 11.06->9.49 (-), paper 11.39->9.67 (-) => coincide
- 0.65->0.75: mod 9.49->8.29 (-), paper 9.67->8.32 (-) => coincide
- 0.75->0.85: mod 8.29->7.51 (-), paper 8.32->7.46 (-) => coincide

## 5. Efecto de T_fuente (Fig. 3, 15 bar, 373 vs 423 K, mismo x_b)

- No cuantificable: 423 K x_b=0.45/0.75 no convergen con teqp (T_from_Ph fuera de cobertura); sin x_b comun con 373 K.

## 6. Control teqp vs AmmoniaWaterAdapter (mismos puntos de operacion)

- Fig7_KCS11_0p55 x_b=0.55: teqp=11.0554 %, AmH2O=11.0542 %, d=-0.0012 pp
- Fig7_KCS11_0p66 x_b=0.66: teqp=11.9131 %, AmH2O=11.9119 %, d=-0.0012 pp

## 7. Eps calibrados (fuera de 0.75-0.85 es esperado: replican el pinch 4 K del paper)

eps_hrvg: [0.7082, 0.9607] (27 convergentes)

## 8. Conclusion honesta

Coincidencias y divergencias en secciones 3-6; los 333 K se evaluaron igual y se registran con su error real (arranque del solver con T_fuente baja: resultados/2026-09-23_limites_teqp). Fuentes esperadas de discrepancia: EOS distinta (Ibrahim-Klein vs Tillner-Roth/teqp), traduccion pinch->efectividad de un paso, P_baja = burbuja a T_sumidero+4 K, sin cota de titulo >=0.90 del paper. No se fuerza conclusion favorable.

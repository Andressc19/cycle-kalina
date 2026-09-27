# REPORTE — Tiempos reales de teqp / A / B / A+B

Generado por `scripts/medicion_tiempos_AB.py` el 2026-09-27 10:05:54. Datos en `resultados/2026-09-27_medicion_AB/`: `medicion_puntos.csv` (23 puntos), `medicion_bubble_point.csv` (25 llamadas), `medicion_ruido_reloj.csv` (6 corridas), `run.log`.

Definiciones: **t_teqp**/**t_A** = `resolver_ciclo` + `evaluar_ciclo` con `TeqpAdapter`/`TeqpVerificado`; **t_B** = SOLO el costo de `verificar_turbina` sobre el de `TeqpAdapter`; **t_AB** = t_A + `verificar_turbina` sobre el de `TeqpVerificado`. Parámetros: T_sumidero=283.0 K, T_amb_diseno=283.15 K, η_t=η_p=0.8, ε=(0.85, 0.8, 0.85), ṁ_b=1.0 kg/s, umbral de B = 2.0 kJ/kg. Puntos: los 22 KALINA de `2026-09-24_margen2k/barrido_margen2k.csv` (en su P_baja) + el espurio (x_b=0.6, P_alta=4000, T_fuente=394, P_baja=423.914831).

## Resumen de tiempos (una corrida por modo y punto)

| Modo | media [s] | mediana [s] | min [s] | max [s] | rango [s] | sobrecosto vs teqp |
|---|---|---|---|---|---|---|
| teqp (`TeqpAdapter`) | 31.08 | 29.06 | 23.87 | 43.91 | 20.04 | — |
| A (`TeqpVerificado`) | 31.73 | 29.75 | 24.60 | 48.42 | 23.82 | **+2.1 %** |
| B (verificación sobre teqp) | 3.54 | 2.92 | 2.11 | 11.85 | 9.74 | **+11.4 %** (añadido) |
| B (verificación sobre A) | 1.72 | 1.69 | 1.04 | 2.35 | 1.31 | — (solo diagnóstico, caché caliente) |
| A+B | 33.45 | 31.18 | 26.23 | 49.46 | 23.23 | **+7.6 %** |

## Tabla por punto

| # | P_baja [kPa] | t_teqp [s] | t_A [s] | t_B [s] | t_AB [s] | η teqp | η A | clas teqp | clas A | Δh4s B(teqp) | verif | Δh4s B(A+B) | verif | rec. A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KALINA-01 | 523.750 | 36.43 | 35.88 | 3.77 | 37.34 | 0.103715729 | 0.103715729 | KALINA | KALINA | -1.0015 | True | -1.0015 | True | 0 |
| KALINA-02 | 424.170 | 43.91 | 45.5 | 2.26 | 47.57 | 0.080412106 | 0.08041229 | KALINA | KALINA | -0.748 | True | -0.748 | True | 1 |
| KALINA-03 | 752.472 | 29.06 | 28.86 | 3.19 | 30.53 | 0.096152424 | 0.096152424 | KALINA | KALINA | -1.4881 | True | -1.4881 | True | 0 |
| KALINA-04 | 625.242 | 31.77 | 30.84 | 2.53 | 32.74 | 0.116752144 | 0.116752144 | KALINA | KALINA | -1.2771 | True | -1.2771 | True | 0 |
| KALINA-05 | 535.443 | 33.85 | 33.65 | 2.71 | 35.27 | 0.120151383 | 0.120151383 | KALINA | KALINA | -1.0688 | True | -1.0688 | True | 0 |
| KALINA-06 | 687.980 | 30.35 | 29.75 | 11.85 | 31.18 | 0.098608559 | 0.098608559 | KALINA | KALINA | -1.1173 | True | -1.1173 | True | 0 |
| KALINA-07 | 568.015 | 34.59 | 34.81 | 3.54 | 37.16 | 0.103672926 | 0.103672926 | KALINA | KALINA | -0.8604 | True | -0.8604 | True | 0 |
| KALINA-08 | 451.969 | 42.32 | 42.69 | 4.44 | 44.4 | 0.009114415 | 0.009114415 | KALINA | KALINA | -0.7142 | True | -0.7142 | True | 0 |
| KALINA-09 | 967.999 | 26.08 | 26.17 | 3.04 | 28.04 | 0.08422344 | 0.08422344 | KALINA | KALINA | -1.5833 | True | -1.5833 | True | 0 |
| KALINA-10 | 812.575 | 27.41 | 27.75 | 2.56 | 28.88 | 0.109810156 | 0.109810156 | KALINA | KALINA | -1.3743 | True | -1.3743 | True | 0 |
| KALINA-11 | 704.645 | 30.49 | 30.33 | 2.11 | 31.86 | 0.121500395 | 0.121500395 | KALINA | KALINA | -1.1716 | True | -1.1716 | True | 0 |
| KALINA-12 | 868.093 | 27.41 | 27.76 | 2.64 | 29.45 | 0.09055203 | 0.09055203 | KALINA | KALINA | -1.2161 | True | -1.2161 | True | 0 |
| KALINA-13 | 731.746 | 24.61 | 25.15 | 2.53 | 27.12 | 0.106948892 | 0.106948892 | KALINA | KALINA | -0.9618 | True | -0.9618 | True | 0 |
| KALINA-14 | 600.662 | 38.67 | 38.63 | 3.57 | 40.48 | 0.091447933 | 0.091447933 | KALINA | KALINA | -0.8171 | True | -0.8171 | True | 0 |
| KALINA-15 | 1016.276 | 27.08 | 27.03 | 2.57 | 28.49 | 0.101529576 | 0.101529576 | KALINA | KALINA | -1.4596 | True | -1.4596 | True | 0 |
| KALINA-16 | 890.811 | 23.87 | 24.6 | 2.29 | 26.23 | 0.118001733 | 0.118001733 | KALINA | KALINA | -1.2603 | True | -1.2603 | True | 0 |
| KALINA-17 | 1060.025 | 27.94 | 28.23 | 6.55 | 29.83 | 0.081356002 | 0.081356002 | KALINA | KALINA | -1.2995 | True | -1.2995 | True | 0 |
| KALINA-18 | 910.074 | 28.82 | 31.96 | 2.92 | 34.17 | 0.103581982 | 0.103581982 | KALINA | KALINA | -1.0505 | True | -1.0505 | True | 0 |
| KALINA-19 | 767.936 | 32.5 | 31.82 | 4.78 | 33.79 | 0.108586549 | 0.108586549 | KALINA | KALINA | -0.9093 | True | -0.9093 | True | 0 |
| KALINA-20 | 1089.671 | 25.08 | 25.26 | 2.79 | 26.85 | 0.112369281 | 0.112369281 | KALINA | KALINA | -1.3364 | True | -1.3364 | True | 0 |
| KALINA-21 | 1101.511 | 27.57 | 25.49 | 2.98 | 27.39 | 0.097347953 | 0.097347953 | KALINA | KALINA | -1.1272 | True | -1.1272 | True | 0 |
| KALINA-22 | 952.893 | 29.03 | 29.15 | 3.71 | 31.13 | 0.110590562 | 0.110590562 | KALINA | KALINA | -0.9923 | True | -0.9923 | True | 0 |
| ESPURIO | 423.915 | 35.98 | 48.42 | 2.12 | 49.46 | 0.03359365 | 0.080184141 | KALINA | KALINA | 138.9672 | False | 0.0 | True | 6 |

## Proyección: barrido de 30 puntos con ~20 KALINA (los ~10 no KALINA pasarían por teqp+A sin B)

| Modo | s/punto | s/30 puntos |
|---|---|---|
| teqp | 31.08 | 932 |
| A | 31.73 | 952 |
| B (solo KALINA) | 31.08 | 1003 |
| A+B (solo KALINA) | 33.45 | 986 |

## Costo medido de `bubble_point` en el motor real

- 25 llamadas (5 puntos distintos x 5 repeticiones): media **8.04 s**, mediana 8.24 s, min 7.34 s, max 8.67 s, rango 1.33 s. Es 2.3 veces el costo de B por punto (3.54 s): si B comprobara además el punto de burbuja de O2, su sobrecosto iría de +11.4 % a +37.3 % y el barrido de 1003 s a 1164 s.

## Repetibilidad y ruido de reloj

- 3 repeticiones de cada modo en UN mismo punto (KALINA-01, x_b=0.6, P_baja=523.749936), con detalle en `medicion_ruido_reloj.csv`. El rango `min..max` de la tabla (20.0 s en teqp) mezcla el ruido de reloj (±1-2 s) y la variación REAL entre puntos (x_b, P_baja, nº de iteraciones de los dos lazos del solver): es una cota superior del ruido, no su medida. t_B y t_BA comparten la caché `_kalina_flash._ultimaT` dentro del mismo punto, y en modo A ese motor ya se usó durante el ciclo: **t_BA está sesgado a la baja**.

## ¿Detecta B el caso espurio?

- Con **TeqpAdapter** (B solo): Δh4s = 138.9672 kJ/kg → **verificado = False**; η = 0.03359365, clasificación KALINA. Sí: muy por encima del umbral de 2.0 kJ/kg.
- Con **A+B**: Δh4s = 0.0 kJ/kg → **verificado = True**; η = 0.080184141, clasificación KALINA, con 6 recurrencia(s) de A. Puntos verificados: 22/23 con B sobre teqp, 23/23 con B sobre A.

## Lectura

- **A** cuesta +2.1 % frente a teqp, y solo hubo 7 recurrencia(s) al motor real en los 23 puntos (el respaldo de A solo se dispara en la zona de riesgo). **B** cuesta +11.4 % por punto (31.08 → 34.62 s) y da un veredicto por punto con UNA llamada al motor real, sin cambiar el resultado del ciclo: solo lo señala (en A+B un Δh4s pequeño significa que A ya sustituyó el valor, no que teqp acertara).

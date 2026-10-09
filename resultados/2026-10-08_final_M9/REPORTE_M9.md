# REPORTE M9 — escalera de conservación de los datos del profesor

## La pregunta
¿Qué datos del profesor se pueden conservar tal cual y aun así obtener un ciclo KALINA? ¿Cuál es el conjunto máximo de sus datos compatible con KALINA? Para cada conjunto, ¿en qué rangos quedan las demás variables, sobre todo P_alta, P_baja, dP = P_alta − P_baja y rP = P_alta/P_baja? La eficiencia es secundaria.

## Qué se hizo
Se evaluó el ciclo con `comun.evaluar_punto` (motor teqp) sobre un barrido LHS. Paso 1: conservar un grupo del profesor. Paso 2: sumar grupos de a uno (selección hacia adelante) hasta que el conjunto máximo deje de dar KALINA. Paso 3: 3 puntos de control con el motor real. Todo con `ProcessPoolExecutor(max_workers=7)`.

## La escalera

| ronda | conservados | n.º de datos | n corridas | genuinos | KALINA | KALINA confiables | D mín | criterio más roto | elegido |
|---|---|---|---|---|---|---|---|---|---|
| 0 | EF | 5 | 100 | 88 | 13 | 11 | 0 | O2:75 | no |
| 0 | PA | 1 | 100 | 88 | 19 | 12 | 0 | O2:69 | no |
| 0 | PB | 1 | 100 | 85 | 1 | 1 | 0 | O2:84 | no |
| 0 | TF | 1 | 100 | 60 | 7 | 0 | 0 | O2:53 | no |
| 0 | TS | 1 | 100 | 87 | 17 | 13 | 0 | O2:68 | no |
| 0 | XB | 1 | 100 | 85 | 29 | 15 | 0 | O2:51 | sí |
| 1 | XB+EF | 6 | 30 | 26 | 11 | 6 | 0 | O2:15 | no |
| 1 | XB+PA | 2 | 30 | 28 | 11 | 7 | 0 | O2:17 | sí |
| 1 | XB+PB | 2 | 30 | 27 | 4 | 3 | 0 | O2:23 | no |
| 1 | XB+TF | 2 | 30 | 20 | 2 | 0 | 0 | O2:18 | no |
| 1 | XB+TS | 2 | 30 | 26 | 9 | 5 | 0 | O2:16 | no |

## El conjunto máximo de datos del profesor compatible con KALINA
Se conservan **2 datos del profesor** (grupos `XB+PA`) y aun así hay KALINA: 11 KALINA (7 confiables) en 30 corridas.
Así, la escalera llegó a 2 grupos conservados (`XB+PA`).
- `T_fuente`: KALINA en 391 – 483 (mediana 423, n=11).
- `T_sumidero`: KALINA en 280 – 301 (mediana 290, n=11).
- `P_baja`: KALINA en 545 – 1.85e+03 (mediana 1.39e+03, n=11).
- `eta_t`: KALINA en 0.411 – 0.901 (mediana 0.679, n=11).
- `eta_p`: KALINA en 0.428 – 0.947 (mediana 0.798, n=11).
- `eps_hrvg`: KALINA en 0.448 – 0.904 (mediana 0.692, n=11).
- `eps_reg`: KALINA en 0.416 – 0.93 (mediana 0.719, n=11).
- `eps_cond`: KALINA en 0.53 – 0.946 (mediana 0.84, n=11).
- `dP`: KALINA en 1.15e+03 – 2.45e+03 (mediana 1.61e+03, n=11).
- `rP`: KALINA en 1.62 – 5.5 (mediana 2.16, n=11).

## Qué bloquea
El conjunto `XB+PA` todavía da KALINA.
El paso 2 se detuvo tras la ronda 1 — la ronda 2 no se exploró por presupuesto de tiempo. Las rondas siguientes (hasta conservar 4 grupos) quedaron **no exploradas**; eso no significa 'sin KALINA'.

## Húsavík
En la malla de P_baja 500–1000 kPa: con el piso 278.15 K hay KALINA desde P_baja = 600 kPa; con el piso 283.15 K hay KALINA desde P_baja = 690 kPa. η a 690 kPa: 0.127.

## Los 3 puntos del motor real
| punto | clase teqp | clase real | η teqp | η real | d_eta_pp (pp) |
|---|---|---|---|---|---|
| A* | KALINA | KALINA | 0.0848 | 0.0848 | 0.000145 |
| A4 | KALINA | KALINA | 0.156 | 0.156 | 0.000278 |
| HUS | KALINA | KALINA | 0.127 | 0.127 | -0.00229 |

## Lo que no se sabe
- La ronda 1 se corrió con 30 puntos por conjunto, así que es una exploración y no un mapa fino de la frontera KALINA.
- El barrido es por muestreo (LHS + búsqueda por patrones): un conjunto que dio 0 KALINA en la muestra puede tener franjas angostas no vistas (la búsqueda dirigida lo mitiga para la última ronda).
- Las corridas usan presupuestos de tiempo fijos (teqp 300 s, motor real 1500 s); un punto en el borde del presupuesto puede no converger.
- El reporte de rangos vale para la caja explorada, no fuera de ella.

## Nota del director (Claude, auditoría 2026-10-08)

- **"Conjunto máximo = 2 datos" se lee mal si se cuentan grupos y no variables.** El ranking elige
  por número de KALINA confiables, y por eso queda `XB+PA` (2 variables, 7 confiables). Pero
  `XB+EF` conserva **6 de los 11 datos del profesor** (x_b, η_t, η_p, ε_HRVG, ε_reg y ε_cond) y da
  11 KALINA, 6 de ellos confiables. Medido en datos conservados, ese es el conjunto mayor de M9.
- **Fases previas conservan aún más: 9 de 11.**
  - M2, ruta B, conserva P_alta, x_b, T_sumidero, las η y las ε; mueve solo T_fuente (390–434 K)
    y P_baja (≥ 445–945 kPa).
  - M5c conserva las 2 presiones, x_b, las η, ε_HRVG, ε_reg y su clima; mueve T_fuente
    (~390–410 K) y ε_cond (≥ 0.875).

  M9 se mueve por grupos y con muestreo grueso: confirma la tendencia, pero no supera a esas
  búsquedas dirigidas.
- **Lectura consolidada (M2 + M5c + M9):**
  - el dato del profesor que NO se puede conservar con confianza es **T_fuente = 623.15 K**
    (0 KALINA confiables en C_TF y en XB+TF);
  - el segundo más restrictivo es **P_baja = 400 kPa** (1/100 sola, 3/30 con x_b). Solo funciona
    en la franja angosta de M5c;
  - todos los demás (x_b, P_alta, T_sumidero, las η y las ε) se conservan sin problema;
  - el criterio que manda en TODOS los conjuntos es O2 (cavitación).
- **Húsavík cae dentro de la ventana.** Con su piso de diseño (10 °C), la P_baja mínima KALINA es
  exactamente su valor real (690 kPa), y el motor real lo confirma (η 12.73 %, Δ −0.002 pp).

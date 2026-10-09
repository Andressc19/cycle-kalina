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
| 2 | XB+PA+EF | 7 | 30 | 28 | 13 | 7 | 0 | O2:14 | sí |
| 2 | XB+PA+PB | 3 | 30 | 28 | 2 | 2 | 0 | O2:26 | no |
| 2 | XB+PA+TF | 3 | 30 | 19 | 3 | 0 | 0 | O2:16 | no |
| 2 | XB+PA+TS | 3 | 30 | 27 | 8 | 6 | 0 | O2:19 | no |
| 3 | XB+PA+EF+PB | 8 | 30 | 28 | 5 | 5 | 0 | O2:22 | sí |
| 3 | XB+PA+EF+TF | 8 | 30 | 0 | 0 | 0 |  | — | no |
| 3 | XB+PA+EF+TS | 8 | 30 | 29 | 6 | 4 | 0 | O2:21 | no |

## El conjunto máximo de datos del profesor compatible con KALINA
Se conservan **8 datos del profesor** (grupos `XB+PA+EF+PB`) y aun así hay KALINA: 5 KALINA (5 confiables) en 30 corridas.
Así, la escalera llegó a 4 grupos conservados (`XB+PA+EF+PB`).
- `T_fuente`: KALINA en 391 – 409 (mediana 399, n=5).
- `T_sumidero`: KALINA en 280 – 293 (mediana 284, n=5).
- `dP`: KALINA en 2.6e+03 – 2.6e+03 (mediana 2.6e+03, n=5).
- `rP`: KALINA en 7.5 – 7.5 (mediana 7.5, n=5).

## Qué bloquea
El conjunto `XB+PA+EF+PB` todavía da KALINA.

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

### Nota del director — rondas 2 y 3 (auditoría 2026-10-09)

- **La escalera se completó: 4 rondas y 18 conjuntos.** No queda ninguna ronda sin explorar: con
  4 grupos, el siguiente paso es el punto completo del profesor, que ya se sabe NO_CONVERGIO (M1).
- **Conjunto final elegido: `XB+PA+EF+PB`.** Conserva **8 de los 10 datos de diseño** del profesor:
  P_alta 3000, P_baja 400, x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75 y ε_cond 0.80.
  Da 5 KALINA en 30 puntos, los 5 confiables.
  - Solo se mueven las dos temperaturas: **T_fuente 391–409 K** y **T_sumidero 280–293 K**.
  - η llega hasta 10.6 %.
  - Los 5 tienen m_O2 ≥ 2 K, es decir, subenfriamiento real.
- **Con el clima del profesor (300 K) en lugar de P_baja: `XB+PA+EF+TS`** da 6 KALINA, 4 de ellos
  confiables, con T_fuente 392–417 K y P_baja 587–1660 kPa.
- **No se puede conservar a la vez sus 2 presiones, su ε_cond = 0.80 y su clima de 300 K.**
  Coincide con M5c, donde con ese clima hace falta ε_cond ≥ 0.875.
- **Su fuente de 623 K es el bloqueo estructural.** `XB+PA+EF+TF` da 30/30 NO_CONVERGIO, sin ningún
  genuino: es la misma causa que en el punto del profesor (F sin cambio de signo; el HRVG
  sobrecalienta). Por eso no hubo búsqueda dirigida, porque no hay un genuino de dónde partir.

**Respuesta a la pregunta del trabajo:** los datos del profesor son un Kalina válido si se cambia
**solo la temperatura de la fuente**, de 623 K a ~390–410 K, y se usa un sumidero algo más frío
(≤ ~293 K), o bien se sube ε_cond a ≥ 0.875 con su clima (M5c). Todo lo demás se conserva.

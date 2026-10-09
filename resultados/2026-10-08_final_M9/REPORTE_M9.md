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

## El conjunto máximo de datos del profesor compatible con KALINA
Se conservan **1 datos del profesor** (grupos `XB`) y aun así hay KALINA: 29 KALINA (15 confiables) en 100 corridas.
- `T_fuente`: KALINA en 388 – 515 (mediana 429, n=29).
- `T_sumidero`: KALINA en 279 – 303 (mediana 289, n=29).
- `P_alta`: KALINA en 2.02e+03 – 4.9e+03 (mediana 3.37e+03, n=29).
- `P_baja`: KALINA en 340 – 2e+03 (mediana 1.36e+03, n=29).
- `eta_t`: KALINA en 0.415 – 0.929 (mediana 0.703, n=29).
- `eta_p`: KALINA en 0.427 – 0.929 (mediana 0.662, n=29).
- `eps_hrvg`: KALINA en 0.41 – 0.95 (mediana 0.613, n=29).
- `eps_reg`: KALINA en 0.402 – 0.941 (mediana 0.751, n=29).
- `eps_cond`: KALINA en 0.493 – 0.948 (mediana 0.857, n=29).
- `dP`: KALINA en 526 – 4.07e+03 (mediana 2.23e+03, n=29).
- `rP`: KALINA en 1.29 – 9 (mediana 2.56, n=29).

## Qué bloquea
El conjunto `XB` todavía da KALINA.
El paso 2 se detuvo tras la ronda 0 — se pasaron 3 h 15 min. Las rondas siguientes (hasta conservar 4 grupos) quedaron **no exploradas**; eso no significa 'sin KALINA'.

## Húsavík
En la malla de P_baja 500–1000 kPa: con el piso 278.15 K hay KALINA desde P_baja = 600 kPa; con el piso 283.15 K hay KALINA desde P_baja = 690 kPa. η a 690 kPa: 0.127.

## Los 3 puntos del motor real
| punto | clase teqp | clase real | η teqp | η real | d_eta_pp (pp) |
|---|---|---|---|---|---|
| A* | KALINA | KALINA | 0.0848 | 0.0848 | 0.000145 |
| A4 | KALINA | KALINA | 0.156 | 0.156 | 0.000278 |
| HUS | KALINA | KALINA | 0.127 | 0.127 | -0.00229 |

## Lo que no se sabe
- El barrido es por muestreo (LHS + búsqueda por patrones): un conjunto que dio 0 KALINA en la muestra puede tener franjas angostas no vistas (la búsqueda dirigida lo mitiga para la última ronda).
- Las corridas usan presupuestos de tiempo fijos (teqp 300 s, motor real 1500 s); un punto en el borde del presupuesto puede no converger.
- El reporte de rangos vale para la caja explorada, no fuera de ella.

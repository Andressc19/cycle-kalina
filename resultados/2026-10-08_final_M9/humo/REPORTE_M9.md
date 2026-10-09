# REPORTE M9 — escalera de conservación de los datos del profesor

## La pregunta
¿Qué datos del profesor se pueden conservar tal cual y aun así obtener un ciclo KALINA? ¿Cuál es el conjunto máximo de sus datos compatible con KALINA? Para cada conjunto, ¿en qué rangos quedan las demás variables, sobre todo P_alta, P_baja, dP = P_alta − P_baja y rP = P_alta/P_baja? La eficiencia es secundaria.

## Qué se hizo
Se evaluó el ciclo con `comun.evaluar_punto` (motor teqp) sobre un barrido LHS. Paso 1: conservar un grupo del profesor. Paso 2: sumar grupos de a uno (selección hacia adelante) hasta que el conjunto máximo deje de dar KALINA. Paso 3: 3 puntos de control con el motor real. Todo con `ProcessPoolExecutor(max_workers=7)`.

## La escalera

| ronda | conservados | n.º de datos | n corridas | genuinos | KALINA | KALINA confiables | D mín | criterio más roto | elegido |
|---|---|---|---|---|---|---|---|---|---|
| 0 | EF | 5 | 2 | 2 | 0 | 0 | 1.73 | O2:2 | no |
| 0 | PA | 1 | 2 | 2 | 0 | 0 | 8.12 | O2:2 | no |
| 0 | PB | 1 | 2 | 2 | 0 | 0 | 1.89 | O2:2 | no |
| 0 | TF | 1 | 2 | 1 | 1 | 1 | 0 | — | sí |
| 0 | TS | 1 | 2 | 2 | 1 | 1 | 0 | O2:1 | no |
| 0 | XB | 1 | 2 | 1 | 0 | 0 | 31.9 | O2:1 | no |
| 1 | TF+EF | 6 | 2 | 0 | 0 | 0 |  | — | no |
| 1 | TF+PA | 2 | 2 | 2 | 0 | 0 | 2.41 | O2:2 | no |
| 1 | TF+PB | 2 | 2 | 1 | 0 | 0 | 3.22 | O2:1 | no |
| 1 | TF+TS | 2 | 2 | 1 | 0 | 0 | 3.77 | O2:1 | no |
| 1 | TF+XB | 2 | 2 | 2 | 1 | 0 | 0 | O2:1 | sí |
| 2 | TF+XB+EF | 7 | 2 | 0 | 0 | 0 |  | — | no |
| 2 | TF+XB+PA | 3 | 2 | 2 | 0 | 0 | 17.8 | O2:2 | no |
| 2 | TF+XB+PB | 3 | 2 | 1 | 0 | 0 | 23.5 | O2:1 | no |
| 2 | TF+XB+TS | 3 | 2 | 2 | 0 | 0 | 15 | O2:2 | sí |

## El conjunto máximo de datos del profesor compatible con KALINA
Se conservan **2 datos del profesor** (grupos `TF+XB`) y aun así hay KALINA: 1 KALINA (0 confiables) en 2 corridas.
- `T_sumidero`: KALINA en 301 – 301 (mediana 301, n=1).
- `P_alta`: KALINA en 2.24e+03 – 2.24e+03 (mediana 2.24e+03, n=1).
- `P_baja`: KALINA en 971 – 971 (mediana 971, n=1).
- `eta_t`: KALINA en 0.902 – 0.902 (mediana 0.902, n=1).
- `eta_p`: KALINA en 0.8 – 0.8 (mediana 0.8, n=1).
- `eps_hrvg`: KALINA en 0.755 – 0.755 (mediana 0.755, n=1).
- `eps_reg`: KALINA en 0.814 – 0.814 (mediana 0.814, n=1).
- `eps_cond`: KALINA en 0.937 – 0.937 (mediana 0.937, n=1).
- `dP`: KALINA en 1.27e+03 – 1.27e+03 (mediana 1.27e+03, n=1).
- `rP`: KALINA en 2.31 – 2.31 (mediana 2.31, n=1).

## Qué bloquea
El grupo que rompe el ciclo es el último sumado para llegar a `TF+XB+TS`: ese conjunto dio 0 KALINA (criterio más frecuente: O2:2).

## Húsavík
En la malla de P_baja 500–1000 kPa: con el piso 278.15 K hay KALINA desde P_baja = 690 kPa; con el piso 283.15 K hay KALINA desde P_baja = 690 kPa. η a 690 kPa: 0.127.

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

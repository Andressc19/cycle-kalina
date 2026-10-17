# Sens2 P2 - Paso 1: comparacion de distribuciones

CORREGIBLE frente a KALINA, por centro y todos, frente a KALINA (total) y
KALINA dentro del rango experimental. KS (scipy), diferencia de medianas
con IC bootstrap (1000 remuestreos, semilla 20261017, 95 %) y delta de Cliff.

## Respuesta: eta y W_net especifico (Wnet/m_b)

| ambito | referencia | variable | mediana CORREGIBLE | mediana KALINA | dif (COR-KAL) | IC 95 % | lectura |
|---|---|---|---|---|---|---|---|
| todos los puntos | KALINA (total) | eta (%) | 10.2 | 7.729 | +2.469 | [+2.184, +2.703] | CORREGIBLE sobreestima |
| todos los puntos | KALINA (total) | Wnet/m_b (kW/kg/s) | 82.7 | 57.86 | +24.84 | [+19.04, +29.66] | CORREGIBLE sobreestima |
| todos los puntos | KALINA en rango experimental | eta (%) | 10.2 | 7.771 | +2.427 | [+2.137, +2.654] | CORREGIBLE sobreestima |
| todos los puntos | KALINA en rango experimental | Wnet/m_b (kW/kg/s) | 82.7 | 52.04 | +30.66 | [+26, +35.89] | CORREGIBLE sobreestima |
| LHS (estudios 3 y 14) | KALINA (total) | eta (%) | 8.565 | 5.465 | +3.1 | [+2.464, +3.646] | CORREGIBLE sobreestima |
| LHS (estudios 3 y 14) | KALINA (total) | Wnet/m_b (kW/kg/s) | 72.63 | 31.72 | +40.91 | [+33.39, +48.04] | CORREGIBLE sobreestima |
| LHS (estudios 3 y 14) | KALINA en rango experimental | eta (%) | 8.565 | 5.227 | +3.338 | [+2.67, +3.875] | CORREGIBLE sobreestima |
| LHS (estudios 3 y 14) | KALINA en rango experimental | Wnet/m_b (kW/kg/s) | 72.63 | 29.26 | +43.38 | [+35.24, +49.57] | CORREGIBLE sobreestima |

## eta y W_net especifico por centro (KALINA total, todos los puntos)

| centro | variable | n COR | n KAL | mediana COR | mediana KAL | dif | IC 95 % | KS | p | lectura |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 Husavik | eta (%) | 329 | 454 | 10.4 | 8.895 | +1.5 | [+0.8744, +2.43] | 0.203 | 2.3e-07 | CORREGIBLE sobreestima |
| C1 Husavik | Wnet/m_b (kW/kg/s) | 329 | 454 | 82.9 | 70.45 | +12.45 | [+4.151, +20.18] | 0.126 | 0.00433 | CORREGIBLE sobreestima |
| C2 ancla A* | eta (%) | 171 | 409 | 8.666 | 6.675 | +1.991 | [+1.421, +2.506] | 0.355 | 4.84e-14 | CORREGIBLE sobreestima |
| C2 ancla A* | Wnet/m_b (kW/kg/s) | 171 | 409 | 56.5 | 25.55 | +30.95 | [+23.61, +35.78] | 0.476 | 2.72e-25 | CORREGIBLE sobreestima |
| C3 caliente 150 C | eta (%) | 128 | 409 | 9.779 | 8.366 | +1.413 | [+0.7535, +1.996] | 0.346 | 6.91e-11 | CORREGIBLE sobreestima |
| C3 caliente 150 C | Wnet/m_b (kW/kg/s) | 128 | 409 | 95.15 | 80.34 | +14.81 | [+2.594, +24.25] | 0.19 | 0.00151 | CORREGIBLE sobreestima |
| C4 frio 110 C | eta (%) | 106 | 383 | 11.61 | 8.366 | +3.241 | [+2.284, +3.846] | 0.407 | 6.94e-13 | CORREGIBLE sobreestima |
| C4 frio 110 C | Wnet/m_b (kW/kg/s) | 106 | 383 | 82.1 | 65.87 | +16.22 | [+6.643, +25.73] | 0.217 | 0.000625 | CORREGIBLE sobreestima |
| Sin centro (muestreo o malla) | eta (%) | 234 | 392 | 11.04 | 6.618 | +4.421 | [+3.742, +4.891] | 0.55 | 2.81e-41 | CORREGIBLE sobreestima |
| Sin centro (muestreo o malla) | Wnet/m_b (kW/kg/s) | 234 | 392 | 107.2 | 63.79 | +43.39 | [+21.28, +58.08] | 0.272 | 4.96e-10 | CORREGIBLE sobreestima |

Lectura: dif = mediana(CORREGIBLE) - mediana(KALINA); dif > 0 = el
CORREGIBLE sobreestima, dif < 0 = subestima; si el IC cruza 0, sin diferencia
clara. n validos = puntos con la variable presente y finita.

## m_b por estudio (dataset completo, antes de deduplicar)

Toda comparacion de W_net usa W_net especifico = Wnet/m_b (kW por kg/s).
Estudios con algun m_b distinto de 1: 0.

| estudio | valores de m_b |
|---|---|
| 0 * | 1, 5, 10, 15, 20 |
| 1 | 1 |
| 2 | 1 |
| 3 | 1 |
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |
| 9 | 1 |
| 10 | 1 |
| 11 | 1 |
| 14 | 1 |
| 15 | 1 |
| 16 | 1 |

(*) Estudios que usan m_b distinto de 1 (el resto usa m_b = 1).
En el dataset deduplicado de P2, los puntos con distinto m_b se conservan
con su m_b; los W_net se comparan siempre divididos por m_b.

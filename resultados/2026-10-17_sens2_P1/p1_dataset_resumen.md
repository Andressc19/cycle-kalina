# Sens2 P1 - paso 1: dataset unificado

Total de filas: **3921** (esperado 3 921: coincide).

## n por estudio y por clase

| estudio | puntos | KALINA | CORREGIBLE | NO_CONVERGIO | INVIABLE |
|---|---|---|---|---|---|
| 0 | 11 | 1 | 10 | 0 | 0 |
| 1 | 273 | 186 | 59 | 23 | 5 |
| 2 | 542 | 398 | 108 | 35 | 1 |
| 3 | 500 | 249 | 185 | 56 | 10 |
| 4 | 343 | 159 | 59 | 119 | 6 |
| 5 | 192 | 17 | 126 | 2 | 47 |
| 6 | 98 | 47 | 34 | 10 | 7 |
| 7 | 144 | 45 | 32 | 55 | 12 |
| 8 | 360 | 188 | 143 | 15 | 14 |
| 9 | 54 | 43 | 0 | 5 | 6 |
| 10 | 279 | 218 | 32 | 27 | 2 |
| 11 | 361 | 203 | 125 | 28 | 5 |
| 14 | 465 | 258 | 77 | 111 | 19 |
| 15 | 194 | 184 | 0 | 10 | 0 |
| 16 | 105 | 47 | 28 | 29 | 1 |
| **total** | **3921** | **2243** | **1018** | **525** | **135** |

Puntos sin centro asignado en el cargador: 847 (estudios N1, N2 y N5).

## Duplicados exactos

Se consideran duplicadas dos filas con las **mismas 10 entradas** y el mismo `centro`:
Hay 226 grupos con esa condicion (484 filas dentro de ellos).
Cada fila sigue siendo un punto distinto de su estudio (mismo vector de entradas,
otro id de estudio): el dataset conserva las 3 921 filas, una por punto, como pide el paso 1.

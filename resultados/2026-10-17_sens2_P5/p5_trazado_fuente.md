# Sens2 P5 - trazado de las cifras contra las fuentes citadas por cada conclusion

Cada cifra se busca solo en los CSV de la columna `fuente` de su conclusion (y en los valores de `p5_hechos`, que alimentan los marcadores, y en `p5_trazado_permitidos.csv`).

- total de numeros: 1237
- trazados contra su fuente: 1127 (91.1 %)
- triviales: 110
- no trazados (escritos a mano sin respaldo directo en la fuente citada): 0 (0.0 %)
- poder del control: una cifra inventada de dos decimales se habria trazado en el 39.3 % de los casos con esta restriccion (con todos los CSV: 100 %).

Los no trazados no son necesariamente erroneos (rangos redondeados, cifras de la literatura, constantes de diseno), pero no tienen respaldo automatico: las mas importantes se vigilan con `p5_cifras_check*.py`.

## No trazados

| id | campo | numero | contexto |
|---|---|---|---|

## Poder por conclusion

Porcentaje de cifras inventadas de dos decimales que se trazarian contra las fuentes de esa conclusion (200 por conclusion, semilla 20261018). Arriba del 80 % el trazado de esa conclusion es poco informativo y su respaldo real son los controles independientes.

| id | poder (%) | trazado poco informativo |
|---|---|---|
| D1 | 8 | no |
| D2 | 13 | no |
| D3 | 8 | no |
| D4 | 7 | no |
| D5 | 4 | no |
| D6 | 7 | no |
| E1 | 22 | no |
| E2 | 17 | no |
| E3 | 27 | no |
| E4 | 26 | no |
| E5 | 22 | no |
| E6 | 22 | no |
| E7 | 23 | no |
| M1 | 78 | no |
| M2 | 79 | no |
| M3 | 78 | no |
| M4 | 82 | si |
| M5 | 10 | no |
| F1 | 64 | no |
| F2 | 10 | no |
| F3 | 12 | no |
| F4 | 11 | no |
| F5 | 8 | no |
| F6 | 21 | no |
| L1 | 86 | si |
| L2 | 12 | no |
| L3 | 10 | no |
| L4 | 82 | si |
| L5 | 30 | no |
| D7 | 90 | si |
| E8 | 76 | no |
| L6 | 90 | si |
| R1 | 77 | no |
| U1 | 81 | si |
| U2 | 83 | si |
| U3 | 76 | no |
| D8 | 82 | si |
| L7 | 92 | si |
| U4 | 76 | no |
| L8 | 8 | no |
| L9 | 8 | no |
| M6 | 83 | si |
| E9 | 14 | no |
| D9 | 8 | no |
| L10 | 10 | no |
| E10 | 10 | no |
| U5 | 80 | no |
| M7 | 8 | no |

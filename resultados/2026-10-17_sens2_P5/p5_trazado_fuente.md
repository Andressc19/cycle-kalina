# Sens2 P5 - trazado de las cifras contra las fuentes citadas por cada conclusion

Cada cifra se busca solo en los CSV de la columna `fuente` de su conclusion (y en los valores de `p5_hechos`, que alimentan los marcadores, y en `p5_trazado_permitidos.csv`).

- total de numeros: 1004
- trazados contra su fuente: 908 (90.4 %)
- triviales: 96
- no trazados (escritos a mano sin respaldo directo en la fuente citada): 0 (0.0 %)
- poder del control: una cifra inventada de dos decimales se habria trazado en el 45.0 % de los casos con esta restriccion (con todos los CSV: 100 %).

Los no trazados no son necesariamente erroneos (rangos redondeados, cifras de la literatura, constantes de diseno), pero no tienen respaldo automatico: las mas importantes se vigilan con `p5_cifras_check*.py`.

## No trazados

| id | campo | numero | contexto |
|---|---|---|---|

## Poder por conclusion

Porcentaje de cifras inventadas de dos decimales que se trazarian contra las fuentes de esa conclusion (200 por conclusion, semilla 20261018). Arriba del 80 % el trazado de esa conclusion es poco informativo y su respaldo real son los controles independientes.

| id | poder (%) | trazado poco informativo |
|---|---|---|
| D1 | 8 | no |
| D2 | 12 | no |
| D3 | 8 | no |
| D4 | 6 | no |
| D5 | 4 | no |
| D6 | 6 | no |
| E1 | 20 | no |
| E2 | 16 | no |
| E3 | 26 | no |
| E4 | 26 | no |
| E5 | 21 | no |
| E6 | 22 | no |
| E7 | 21 | no |
| M1 | 78 | no |
| M2 | 79 | no |
| M3 | 78 | no |
| M4 | 82 | si |
| M5 | 4 | no |
| F1 | 64 | no |
| F2 | 10 | no |
| F3 | 10 | no |
| F4 | 8 | no |
| F5 | 7 | no |
| F6 | 20 | no |
| L1 | 86 | si |
| L2 | 12 | no |
| L3 | 8 | no |
| L4 | 81 | si |
| L5 | 28 | no |
| D7 | 90 | si |
| E8 | 76 | no |
| L6 | 90 | si |
| R1 | 77 | no |
| U1 | 81 | si |
| U2 | 83 | si |
| U3 | 76 | no |
| D8 | 82 | si |
| L7 | 92 | si |
| U4 | 75 | no |
| L8 | 7 | no |
| L9 | 8 | no |
| M6 | 83 | si |
| E9 | 14 | no |

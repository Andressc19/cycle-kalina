# Sens2 P5 - trazado de las cifras contra las fuentes citadas por cada conclusion

Cada cifra se busca solo en los CSV de la columna `fuente` de su conclusion (y en los valores de `p5_hechos`, que alimentan los marcadores, y en `p5_trazado_permitidos.csv`).

- total de numeros: 983
- trazados contra su fuente: 888 (90.3 %)
- triviales: 93
- no trazados (escritos a mano sin respaldo directo en la fuente citada): 2 (0.2 %)
- poder del control: una cifra inventada de dos decimales se habria trazado en el 45.0 % de los casos con esta restriccion (con todos los CSV: 100 %).

Los no trazados no son necesariamente erroneos (rangos redondeados, cifras de la literatura, constantes de diseno), pero no tienen respaldo automatico: las mas importantes se vigilan con `p5_cifras_check*.py`.

## No trazados

| id | campo | numero | contexto |
|---|---|---|---|
| D5 | implicacion | 278 |  diseño de Húsavík (278 K) no se traslada a |
| M5 | evidencia | 0.016 |  frente a 0.75, p = 0.016) y no en C2 (0.79 f |

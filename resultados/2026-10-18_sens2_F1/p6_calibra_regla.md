# Sens2 F1 - calibracion de la regla "distinguible"

Una variable dummy es una columna de numeros aleatorios que se incluye como control: no tiene relacion con la respuesta, asi que cada vez que la regla la marca cuenta como falso positivo.
Regla: una variable es distinguible si su q (Benjamini-Hochberg por bloque y respuesta sobre todas las pruebas) queda por debajo de 0.05 en al menos 2 metodos. Aplicada a las 3 dummy en los 4 bloques y las 3 respuestas (36 evaluaciones), la regla marca 1 (2.8 %, IC 95 % de Wilson [0.5 %, 14.2 %]).
Por respuesta: Y1 KALINA (total) 0 de 12, Y2 eta (%) 1 de 12, Y3 W_net/m_b 0 de 12.
Al bajar el umbral a k = 1 salen 1 de 36 dummy (2.8 %); con k = 3 y k = 4, ninguna.
Si la correccion se hiciera solo con las 3 dummy (sin las reales) ninguna queda marcada a ningun k (0 de 36 a k = 2).
Familia global: al juntar todas las pruebas en una sola familia, las reales distinguidas suman 55 con la regla por bloque, 56 con BH por metodo y 54 con los metodos mezclados (de 108 en total).
Filas con caja distinta de "no": 0 (la caja comun queda vacia/inviable y no se calcula).

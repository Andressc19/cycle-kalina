# REPORTE M2 nivel 1 — ¿con UN solo cambio al enunciado del profesor aparece KALINA?
## 1. La pregunta
Se cambia **una sola** variable de los datos del profesor, con las otras 10 exactamente como él las dio, y se pregunta si con ese único cambio el ciclo converge y es KALINA. Si la respuesta es sí, interesa además cuánto hay que mover esa variable.
## 2. Qué se hizo
- **La malla.** Cada una de las 10 variables se recorrió con 10 valores equiespaciados de su rango (100 corridas en total), con todo lo demás clavado en el valor del profesor: un peine de 10 dientes por variable. Eso muestra, a ojo, en qué tramo de cada variable empieza a funcionar el ciclo.
- **La bisección.** Entre cada par de valores vecinos de la malla donde cambia el resultado —de no convergir a convergir, o de no ser KALINA a serlo— se parte el intervalo por la mitad, una y otra vez, hasta dejar la frontera acotada a su tolerancia (10 kPa en las presiones, 0.5 K en las temperaturas, 0.005 en composiciones, efectividades y eficiencias). Todas las fronteras avanzan en paralelo, ronda a ronda, con los mismos 6 procesos.

## 3. Tabla por variable (primero diseño, después sitio)

| Variable | ¿Converge en algún valor? | ¿KALINA en algún valor? | Valor KALINA más cercano al profesor (d) | Mejor D | Criterio que más bloquea |
|---|---|---|---|---|---|
| P_alta | no | no | — | — | — |
| P_baja | no | no | — | — | — |
| x_b | sin datos | no | — | — | — |
| eta_t | sin datos | no | — | — | — |
| eta_p | sin datos | no | — | — | — |
| eps_hrvg | sin datos | no | — | — | — |
| eps_reg | sin datos | no | — | — | — |
| eps_cond | sin datos | no | — | — | — |
| T_fuente | sin datos | no | — | — | — |
| T_sumidero | sin datos | no | — | — | — |

## 4. Fronteras encontradas, con su precisión

Ninguna frontera que refinar: la corrida de humo no hace bisección.
## 5. Tiempos
- Malla: 88 s · Bisección: 0 s · Total: 88 s.
- Por punto (`t_s`): mínimo 32.0 s, mediana 68.4 s, máximo 84.7 s, media 62.0 s (4 puntos).
## 6. Conclusión
Con un solo cambio **no** se alcanza KALINA: ninguna variable sola lo logra; las que al menos hacen converger el ciclo no existen, y el criterio que queda bloqueando es ninguno.
## 7. Lo que no se sabe
- La malla tiene solo 10 valores por variable: entre dos vecinos queda un hueco de (b−a)/9. Si la zona KALINA de una variable fuera más estrecha que eso y cayera justo entre dos puntos, la malla no la vería y la bisección no la buscaría.
- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos; todo lo que aparezca y desaparezca dentro de un mismo hueco queda fuera de este nivel.
- Aquí solo se cambia UNA variable a la vez; este reporte no dice nada sobre combinaciones de dos o más (eso es el nivel 2).
- Esta es una corrida de humo (2 variables × 2 valores, sin bisección): las cifras de arriba no son las de la corrida real.
## 8. Qué sigue
El nivel 2 (cambiar pares de variables) lo decide el director a partir de este reporte. Aquí no se proponen pares concretos: lo que hay son las fronteras del nivel 1 y sus cercanías al punto del profesor.

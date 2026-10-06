# REPORTE M2 nivel 1 — ¿con UN solo cambio al enunciado del profesor aparece KALINA?
## 1. La pregunta
Se cambia **una sola** variable de los datos del profesor, con las otras 10 exactamente como él las dio, y se pregunta si con ese único cambio el ciclo converge y es KALINA. Si la respuesta es sí, interesa además cuánto hay que mover esa variable.
## 2. Qué se hizo
- **La malla.** Cada una de las 10 variables se recorrió con 10 valores equiespaciados de su rango (100 corridas en total), con todo lo demás clavado en el valor del profesor: un peine de 10 dientes por variable. Eso muestra, a ojo, en qué tramo de cada variable empieza a funcionar el ciclo.
- **La bisección.** Entre cada par de valores vecinos de la malla donde cambia el resultado —de no convergir a convergir, o de no ser KALINA a serlo— se parte el intervalo por la mitad, una y otra vez, hasta dejar la frontera acotada a su tolerancia (10 kPa en las presiones, 0.5 K en las temperaturas, 0.005 en composiciones, efectividades y eficiencias). Todas las fronteras avanzan en paralelo, ronda a ronda, con los mismos 6 procesos.

## 3. Tabla por variable (primero diseño, después sitio)

| Variable | ¿Converge en algún valor? | ¿KALINA en algún valor? | Valor KALINA más cercano al profesor (d) | Mejor D | Criterio que más bloquea |
|---|---|---|---|---|---|
| P_alta | sí (13) | no | — | 28.5885 en 8000 | C3(26) · N2(13) · O1(13) · O2(13) · O5(13) · C1(13) |
| P_baja | no | no | — | — | — |
| x_b | sí (2) | no | — | 17.1941 en 0.3 | O1(2) · O2(2) · O5(2) · C3(2) · N2(1) · C1(1) |
| eta_t | no | no | — | — | — |
| eta_p | no | no | — | — | — |
| eps_hrvg | sí (9) | no | — | 18.0756 en 0.75 | O1(9) · O2(9) · C3(4) · N2(2) · O5(2) · C1(2) |
| eps_reg | no | no | — | — | — |
| eps_cond | no | no | — | — | — |
| T_fuente | sí (12) | no | — | 2.01753 en 402.922 | C3(10) · O2(9) · O5(6) · N2(5) · C1(5) · O1(5) · S6(3) · O3(3) |
| T_sumidero | no | no | — | — | — |
**Nota (x_b bajo, no preferido):** x_b = 0.3 → INVIABLE; x_b = 0.316667 → NO_CONVERGIO. El proyecto considera estos valores de x_b «bajo, no preferido»; se reportan igual, sin ocultarlos.
## 4. Fronteras encontradas, con su precisión

| Variable | Tipo | Frontera | Lado que SÍ cumple | Lado que NO cumple | Ancho final | Iteraciones | Clase del lado SÍ | D del lado SÍ | Códigos del lado SÍ |
|---|---|---|---|---|---|---|---|---|---|
| P_alta | diseño | convergencia | 5414.06 | 5406.25 | 7.8125 | 7 | NO_CONVERGIO | 33.5613 | N2,O1,O2,O5,C1,C3,C3 |
| P_alta | diseño | convergencia | 9617.19 | 9625 | 7.8125 | 7 | NO_CONVERGIO | 29.091 | N2,O1,O2,O5,C1,C3,C3 |
| x_b | diseño | convergencia | 0.316667 | 0.320833 | 0.00416667 | 4 | NO_CONVERGIO | 21.306 | N2,O1,O2,O5,C1,C3,C3 |
| eps_hrvg | diseño | convergencia | 0.825 | 0.827778 | 0.00277778 | 2 | NO_CONVERGIO | 24.6379 | N2,O1,O2,O5,C1,C3,C3 |
| T_fuente | sitio | convergencia | 368.512 | 368.02 | 0.49158 | 6 | NO_CONVERGIO | 68.7517 | N2,S6,O3,O5,C1,C3,C3 |
| T_fuente | sitio | convergencia | 600.046 | 600.537 | 0.49158 | 6 | NO_CONVERGIO | 28.176 | N2,O1,O2,O5,C1,C3,C3 |
## 5. Tiempos
- Malla: 1408 s · Bisección: 1054 s · Total: 2462 s.
- Por punto (`t_s`): mínimo 33.9 s, mediana 76.3 s, máximo 246.8 s, media 87.6 s (132 puntos).
## 6. Conclusión
Con un solo cambio **no** se alcanza KALINA: ninguna variable sola lo logra; las que al menos hacen converger el ciclo son P_alta, x_b, eps_hrvg, T_fuente, y el criterio que queda bloqueando es C3.
## 7. Lo que no se sabe
- La malla tiene solo 10 valores por variable: entre dos vecinos queda un hueco de (b−a)/9. Si la zona KALINA de una variable fuera más estrecha que eso y cayera justo entre dos puntos, la malla no la vería y la bisección no la buscaría.
- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos; todo lo que aparezca y desaparezca dentro de un mismo hueco queda fuera de este nivel.
- Aquí solo se cambia UNA variable a la vez; este reporte no dice nada sobre combinaciones de dos o más (eso es el nivel 2).

## 8. Qué sigue
El nivel 2 (cambiar pares de variables) lo decide el director a partir de este reporte. Aquí no se proponen pares concretos: lo que hay son las fronteras del nivel 1 y sus cercanías al punto del profesor.

## 9. Nota del director (Claude, auditoría 2026-10-06): corrige la lectura de §6

La conclusión de §6 ("el criterio que más bloquea es C3") cuenta como convergidos 21 puntos que
el solver cerró pero que el clasificador marca NO_CONVERGIO por **N2** (punto fijo espurio). Sus
códigos C1/C3/O5 no describen un ciclo real. Recontado solo sobre los puntos **genuinos**
(CORREGIBLE/INVIABLE), a partir de `m2n1_malla.csv` + `m2n1_biseccion.csv`:

| Variable | Puntos genuinos | Qué bloquea |
|---|---|---|
| T_fuente | 4 CORREGIBLE (403–497 K) | **solo O2** |
| T_fuente | 2 CORREGIBLE (529–560 K) | O1 + O2 |
| T_fuente | 1 INVIABLE (592 K) | O1 + O2 + O5 |
| eps_hrvg | 7 CORREGIBLE (0.75–0.817, con el T_fuente = 623.15 K del profesor) | O1 (al filo, q4 ≈ 0.899–0.900) + O2 (≈ −18 a −20 K) |
| x_b | 1 INVIABLE (0.30) | O1 + O2 + O5 |

- **El bloqueo real es O2 (cavitación) y, en algunos casos, O1.** El punto más cercano es
  T_fuente = 402.9 K: solo falla O2, con un déficit de 2.02 K, y η = 9.86 %.
- Las 6 fronteras de §4 se refinaron sobre la bandera `convergio` del solver. Por eso separan
  el cierre numérico de su zona espuria (N2), **no** las fronteras de clase. La frontera de
  clase útil de T_fuente (N2 a 371.5 K → CORREGIBLE a 402.9 K) quedó sin refinar.
- **Rango confiable:** los CORREGIBLE con T_fuente ≥ 434 K y todos los de eps_hrvg tienen
  T2/T5 > 420 K (`fuera_rango`: G4-01 no tiene respaldo experimental para líquido por encima
  de esa temperatura). El de T_fuente = 402.9 K está dentro del rango.
- Consecuencia para el nivel 2: O2 se cierra con P_baja (regla del proyecto). Los pares a
  probar son (T_fuente, P_baja) y (eps_hrvg, P_baja); este último conserva los datos del sitio
  del profesor.

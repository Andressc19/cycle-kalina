# REPORTE M2 nivel 2 — ¿con DOS cambios al enunciado del profesor aparece KALINA?
## 1. La pregunta
Se cambian **dos** variables de los datos del profesor —siempre `P_baja`, que es la regla del proyecto para cerrar O2, y una segunda que abre el lado caliente— y se pregunta si con ese par el ciclo converge y es KALINA. Si la respuesta es sí, interesa además cuánto hay que mover cada una.
## 2. Qué se hizo
- **Las dos rutas.** Ruta A (solo diseño): `eps_hrvg` ∈ {0.75, 0.78, 0.81}, con toda la fuente y el sitio del profesor (T_fuente = 623.15 K). Ruta B (sitio + diseño): `T_fuente` ∈ {380, 390, 403, 420, 434, 466, 497, 529, 560} K, con todo lo demás del profesor (eps_hrvg = 0.85). En ambas rutas las otras nueve variables quedan exactamente como él las dio.
- **La malla.** Para cada valor de la variable 1, `P_baja` recorre `numpy.linspace(400, 2000, 12)`: (3 + 9) × 12 = 144 corridas con 6 procesos.
- **La bisección.** Entre cada par de vecinos de la malla donde cambia ser KALINA, o donde cambia `m_O2 >= 0` (solo cuando ambos vecinos son genuinos), se parte el intervalo por la mitad hasta acotar la frontera a 10 kPa o agotar 8 iteraciones, ronda a ronda en paralelo.
- **Punto genuino.** Solo cuentan como converge los puntos `KALINA`, `CORREGIBLE` e `INVIABLE`; una fila que el solver cerró pero que el clasificador marca `NO_CONVERGIO` es un punto fijo espurio (N2) y se trata como NO convergido en conteos, fronteras y conclusiones.
- **Escala de `d`.** El índice de cercanía usa los rangos del nivel 1: eps_hrvg [0.75, 0.85], T_fuente [340, 623.15] y P_baja [150, 1500] kPa, **aunque la malla de este nivel llegue a 2000 kPa**: un KALINA por encima de 1500 kPa queda con d > 1.
## 3. Tabla por ruta (una fila por valor de la variable 1)

### Ruta A — solo diseño (eps_hrvg con la fuente y el sitio del profesor)

| eps_hrvg | ¿Hay KALINA? | Menor P_baja KALINA (kPa) | η en ese punto | Fuera de rango | Qué bloquea si no hay KALINA |
|---|---|---|---|---|---|
| 0.75 | no | — | — | — | O2(2) · O1(1) |
| 0.78 | no | — | — | — | — |
| 0.81 | no | — | — | — | — |

### Ruta B — sitio + diseño (T_fuente con todo lo demás del profesor)

| T_fuente | ¿Hay KALINA? | Menor P_baja KALINA (kPa) | η en ese punto | Fuera de rango | Qué bloquea si no hay KALINA |
|---|---|---|---|---|---|
| 380 | no | — | — | — | — |
| 390 | no | — | — | — | — |
| 403 | no | — | — | — | — |
| 420 | no | — | — | — | — |
| 434 | no | — | — | — | — |
| 466 | no | — | — | — | — |
| 497 | no | — | — | — | — |
| 529 | no | — | — | — | — |
| 560 | no | — | — | — | — |
## 4. KALINA de menor d y de mayor η, por ruta

| Ruta | Criterio | valor de la variable 1 | P_baja (kPa) | η | d |
|---|---|---|---|---|---|
| A | menor d | — | — | — | — |
| A | mayor η | — | — | — | — |
| B | menor d | — | — | — | — |
| B | mayor η | — | — | — | — |
## 5. Tiempos
- Malla: 98 s · Bisección: 0 s · Total: 98 s.
- Por punto (`t_s`): mínimo 45.7 s, mediana 87.8 s, máximo 94.6 s, media 76.6 s (4 puntos).
## 6. Conclusión
Con dos cambios **no** se alcanza KALINA. Ruta A (conservando la fuente del profesor): ninguno de los 3 valores de eps_hrvg alcanza KALINA; lo que bloquea es O2. Ruta B: ninguno de los 9 valores de T_fuente alcanza KALINA; la ruta no tiene ni un punto genuino.
## 7. Lo que no se sabe
- No se encontró ningún punto KALINA: no hay ninguno fuera del rango confiable (T > 420 K de líquido).
- Los puntos medios de la bisección se evalúan a ciegas y pueden caer en zonas espurias (N2); cuando eso pasa en una frontera O2 se anota `punto medio no genuino` en `m2n2_biseccion.csv` y se toma como el lado que NO cumple.
- La malla de P_baja tiene solo 12 valores entre 400 y 2000 kPa por valor de la variable 1: el hueco entre vecinos es de 145.5 kPa; una zona KALINA más estrecha que eso y dentro de un hueco no aparece ni en la malla ni en la bisección.
- Esta es una corrida de humo (1 valor por ruta × 2 valores de P_baja, sin bisección): las cifras de arriba no son las de la corrida real.
## 8. Qué sigue
El siguiente paso lo decide el director a partir de las tablas de §3 y §4: aquí no se proponen valores concretos, solo los dos extremos medidos de cada frontera.

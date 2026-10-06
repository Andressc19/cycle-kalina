# REPORTE M2R — repetición de M2 con η y ε en [0.40, 0.95]
## 1. La pregunta
M2 limitó `eta_t`, `eta_p`, `eps_hrvg`, `eps_reg` y `eps_cond` a [0.75, 0.85], pero el rango permitido es [0.40, 0.95]. Se repite M2 con ese rango abierto para saber qué condicionó el límite viejo y, sobre todo, para responder: **¿se puede llegar a KALINA conservando la fuente (T_fuente = 623.15 K) y el sitio (T_sumidero) del profesor, cambiando solo variables de diseño?**
## 2. Qué cambió respecto a M2
- **Rangos.** Las 5 variables de rendimiento pasan de [0.75, 0.85] a [0.40, 0.95] (12 valores equiespaciados, paso 0.05).
- **Fronteras.** Las de «convergencia» de la parte 1 se definen ahora con *es genuino* (KALINA, CORREGIBLE o INVIABLE), no con la bandera `convergio`: un punto N2 ya no cuenta como que converge.
- **Partes.** La 2 añade `eps_cond` como segunda variable (y `eps_hrvg` hasta 0.80, `P_baja` hasta 2000 kPa); la 3 es nueva: (T_fuente, eps_cond) con `P_baja` del profesor.
- **Escala de `d`.** Σ |v − v_prof|/(b − a) con los rangos de M3 (ε/η en [0.40, 0.95], T_fuente [340, 623.15], P_baja [150, 1500] kPa) y `m_b` nunca cambiado (término 0): un KALINA con P_baja > 1500 kPa queda con d > 1.
## 3. Parte 1 — una variable a la vez con el rango nuevo
| Variable | Genuinos | ¿KALINA? | Valor KALINA más cercano al profesor (d) | η ahí | Criterios que bloquean |
|---|---|---|---|---|---|
| eps_hrvg | 1 | no | — | — | O2(1) |
## 4. Parte 2 — conservando la fuente del profesor (T_fuente = 623.15 K)
**No: con la fuente y el sitio del profesor (T_fuente = 623.15 K) no se llega a KALINA** en ninguna de las 2 combinaciones de la parte 2.
| Parte | eps_hrvg | Genuinos | KALINA | N2 | KALINA de menor d (dónde) | η ahí | Mayor η (dónde) | Criterios que bloquean |
|---|---|---|---|---|---|---|---|---|
| n2a | 0.4 | 1 | 0 | 0 | — | — | — | O2(1) |
| n2b | 0.4 | 1 | 0 | 0 | — | — | — | O2(1) |
## 5. Parte 3 — (T_fuente, eps_cond) con P_baja = 400 kPa del profesor
**No.** Con P_baja = 400 kPa ninguna de las 21 parejas (T_fuente, eps_cond) da KALINA: ε_cond no sustituye a P_baja.
| Parte | T_fuente | Genuinos | KALINA | N2 | KALINA de menor d (dónde) | η ahí | Mayor η (dónde) | Criterios que bloquean |
|---|---|---|---|---|---|---|---|---|
| n3 | 403 | 1 | 0 | 0 | — | — | — | O2(1) |
## 6. Comparación con M2
- M2: T_fuente = 390 K, P_baja = 445.455 kPa, η = 0.0245, d ≈ 0.857 con la escala vieja. Recalculado con la escala nueva (rangos de M3): **d = 0.8571** y **2 variables cambiadas**. El valor de d no cambia porque los rangos de T_fuente y P_baja son los mismos en las dos escalas.
- M2R: 0 KALINA distintos; el de menor d tiene d = — y el de menos cambios tiene — cambios.
- **Respuesta: no hay un KALINA con menos cambios que el de M2 y no hay uno con menor d.**
## 7. Tiempos
- Malla: 271 s · Bisección: 0 s · Total: 271 s (0 fronteras, 4 puntos evaluados).
- Por punto (`t_s`): mínimo 171.1 s, mediana 242.7 s, máximo 260.7 s, media 228.7 s (4 puntos).
## 8. Conclusión
No se llega a KALINA con los rangos abiertos: la parte 1 da 0 KALINA con un solo cambio, la parte 2 0 conservando la fuente del profesor y la parte 3 0. El bloqueo de fondo sigue siendo el mismo de siempre (lado caliente y O2) y se cierra como en M2: bajando `eps_hrvg`/`eps_cond` o subiendo `P_baja`.
## 9. Lo que no se sabe
- Ninguno de los 0 puntos KALINA queda fuera del rango confiable.
- 0 puntos son fijos espurios (N2: `convergio` con `clasificacion = NO_CONVERGIO`): se contaron como NO genuinos en todo.
- La malla tiene 12 valores por variable: hueco de (b−a)/11; una zona más estrecha caída dentro de un hueco no aparece ni en la malla ni en la bisección.
- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos.
- Esta es una corrida de humo (1 punto por parte, sin bisección): las cifras no son las de la corrida real.
## 10. Qué sigue
Los puntos concretos que llegan a KALINA están en `m2r_kalina.csv` (con su `d`, sus cambios y su `fuera_rango`); cuál proponer lo decide el director.

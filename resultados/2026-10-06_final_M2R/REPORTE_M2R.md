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
| eps_hrvg | 24 | no | — | — | O2(24) · O1(4) |
| eps_reg | 0 | no | — | — | — |
| eps_cond | 0 | no | — | — | — |
| eta_t | 0 | no | — | — | — |
| eta_p | 0 | no | — | — | — |
## 4. Parte 2 — conservando la fuente del profesor (T_fuente = 623.15 K)
**Sí: se llega a KALINA conservando la fuente y el sitio del profesor (T_fuente = 623.15 K, T_sumidero = 300.032917 K), cambiando solo variables de diseño.** Hay 13 puntos KALINA: n2b con eps_hrvg = 0.4 y P_baja = 1318.18 (d = 1.4983, η = 0.0627); n2b con eps_hrvg = 0.5 y P_baja = 1736.36 (d = 1.6263, η = 0.0434). P_baja queda en 400 kPa en la parte 2a y se barre hasta 2000 kPa en la 2b.
| Parte | eps_hrvg | Genuinos | KALINA | N2 | KALINA de menor d (dónde) | η ahí | Mayor η (dónde) | Criterios que bloquean |
|---|---|---|---|---|---|---|---|---|
| n2a | 0.4 | 12 | 0 | 0 | — | — | — | O2(12) |
| n2a | 0.5 | 11 | 0 | 0 | — | — | — | O2(11) |
| n2a | 0.6 | 12 | 0 | 0 | — | — | — | O2(12) · O1(1) |
| n2a | 0.7 | 9 | 0 | 0 | — | — | — | O2(9) · O1(3) |
| n2a | 0.8 | 4 | 0 | 0 | — | — | — | O1(4) · O2(4) |
| n2b | 0.4 | 16 | 8 | 0 | P_baja = 1318.18 (d = 1.4983) | 0.0627 | 0.0627 (P_baja = 1318.18) | O2(8) |
| n2b | 0.5 | 14 | 5 | 0 | P_baja = 1736.36 (d = 1.6263) | 0.0434 | 0.0434 (P_baja = 1736.36) | O2(9) |
| n2b | 0.6 | 12 | 0 | 0 | — | — | — | O2(12) |
| n2b | 0.7 | 12 | 0 | 0 | — | — | — | O2(12) |
## 5. Parte 3 — (T_fuente, eps_cond) con P_baja = 400 kPa del profesor
**Sí.** Con P_baja = 400 kPa, las 7 parejas (T_fuente, eps_cond) dan 1 KALINA: T_fuente = 403 con eps_cond = 0.95. ε_cond sí puede sustituir a P_baja como segundo cambio.
| Parte | T_fuente | Genuinos | KALINA | N2 | KALINA de menor d (dónde) | η ahí | Mayor η (dónde) | Criterios que bloquean |
|---|---|---|---|---|---|---|---|---|
| n3 | 403 | 3 | 1 | 0 | eps_cond = 0.95 (d = 1.0502) | 0.0950 | 0.0950 (eps_cond = 0.95) | O2(2) |
| n3 | 420 | 3 | 0 | 0 | — | — | — | O2(3) · S3(1) |
| n3 | 434 | 3 | 0 | 0 | — | — | — | O2(3) |
| n3 | 466 | 3 | 0 | 0 | — | — | — | O2(3) |
| n3 | 497 | 2 | 0 | 0 | — | — | — | O2(2) |
| n3 | 529 | 3 | 0 | 0 | — | — | — | O2(3) · O1(2) |
| n3 | 560 | 3 | 0 | 0 | — | — | — | O1(3) · O2(3) |
## 6. Comparación con M2
- M2: T_fuente = 390 K, P_baja = 445.455 kPa, η = 0.0245, d ≈ 0.857 con la escala vieja. Recalculado con la escala nueva (rangos de M3): **d = 0.8571** y **2 variables cambiadas**. El valor de d no cambia porque los rangos de T_fuente y P_baja son los mismos en las dos escalas.
- M2R: 14 KALINA distintos; el de menor d tiene d = 1.0502 y el de menos cambios tiene 2 cambios.
- **Respuesta: no hay un KALINA con menos cambios que el de M2 y no hay uno con menor d.**
## 7. Tiempos
- Malla: 5768 s · Bisección: 1087 s · Total: 6856 s (9 fronteras, 225 puntos evaluados).
- Por punto (`t_s`): mínimo 17.9 s, mediana 139.2 s, máximo 321.2 s, media 147.5 s (225 puntos).
## 8. Conclusión
Sí se llega a KALINA con los rangos abiertos: la parte 1 da 0 KALINA con un solo cambio, la parte 2 13 conservando la fuente del profesor y la parte 3 1. El bloqueo de fondo sigue siendo el mismo de siempre (lado caliente y O2) y se cierra como en M2: bajando `eps_hrvg`/`eps_cond` o subiendo `P_baja`.
## 9. Lo que no se sabe
- **13 de 14 puntos KALINA quedan fuera del rango confiable** (T > 420 K de líquido, IAPWS G4-01 sin respaldo experimental): n2b eps_hrvg = 0.4, P_baja = 1318.18, n2b eps_hrvg = 0.4, P_baja = 1327.27, n2b eps_hrvg = 0.4, P_baja = 1345.45, n2b eps_hrvg = 0.4, P_baja = 1418.18, n2b eps_hrvg = 0.4, P_baja = 1563.64, n2b eps_hrvg = 0.4, P_baja = 1709.09, n2b eps_hrvg = 0.4, P_baja = 1854.55, n2b eps_hrvg = 0.4, P_baja = 2000, n2b eps_hrvg = 0.5, P_baja = 1736.36, n2b eps_hrvg = 0.5, P_baja = 1745.45, n2b eps_hrvg = 0.5, P_baja = 1781.82, n2b eps_hrvg = 0.5, P_baja = 1854.55, n2b eps_hrvg = 0.5, P_baja = 2000.
- 4 puntos son fijos espurios (N2: `convergio` con `clasificacion = NO_CONVERGIO`): se contaron como NO genuinos en todo.
- La malla tiene 12 valores por variable: hueco de (b−a)/11; una zona más estrecha caída dentro de un hueco no aparece ni en la malla ni en la bisección.
- La bisección solo refina fronteras que la malla sí detectó entre dos vecinos consecutivos.
## 10. Qué sigue
Los puntos concretos que llegan a KALINA están en `m2r_kalina.csv` (con su `d`, sus cambios y su `fuera_rango`); cuál proponer lo decide el director.

# REPORTE M1 — ¿el código actual reproduce la Fase 1 del profesor?

## 1. La pregunta
¿El código actualizado (bracket tolerante MA, protección A+B con `TeqpVerificado`, marca de rango y piso de diseño de O2 en 300.032917 K) da la MISMA clase que la corrida del 2026-09-19 en los 41 puntos de la Fase 1 del profesor?

## 2. Qué se hizo
42 corridas con `evaluar_punto` (`scripts/barrido_final/comun.py`), todas con `bracket_tolerante=True` y `presupuesto_s=300`, repartidas en 6 procesos (spawn): el punto base dos veces (motor `teqp` y motor `real`), 9 puntos de `P_alta` (2000–4000 kPa), 7 de `x_b` (0.40–0.70) y las 24 horas de `tamb_profesor.csv` como `T_sumidero`. Son 41 puntos comparables: el punto base aporta el del motor real, porque el 2026-09-19 también usó el motor real.

## 3. Conteo por clase (los 41 puntos comparables)

| Clase | Antes (2026-09-19) | Ahora (2026-10-06) |
|---|---|---|
| KALINA | 0 | 0 |
| CORREGIBLE | 0 | 0 |
| INVIABLE | 0 | 0 |
| NO_CONVERGIO | 41 | 41 |

## 4. Tasa de coincidencia
**41/41 = 100.0 %** de los puntos conservan su clase.

## 5. Tiempos
- Total de pared de la corrida: 603 s.
- Por punto (`t_s`): mínimo 62.8 s, mediana 75.7 s, máximo 316.5 s, media 83.6 s.

## 6. Puntos que cambiaron de clase
Ninguno: los 41 puntos conservan su clase.

## 7. Nota sobre el piso de O2 y el bracket tolerante
La corrida del 2026-09-19 usó el piso de O2 **por defecto** (303.55 K) y **no** usó MA; esta usa **300.032917 K** y MA. Ese cambio solo puede afectar a puntos que **converjan**: si el punto no converge, O2 y el resto de criterios operativos nunca se evalúan. En los puntos que no convergen, cualquier diferencia de mensaje viene del recorrido del lazo, no del criterio.

## 8. Lo que no se sabe y qué sigue
- No se puede separar el efecto de MA del resto de cambios: la corrida anterior no incluye el contraexperimento sin MA.
- El punto base solo se compara con motor real; la corrida con `teqp` se conserva como dato de recurrencias de la protección A.
- `d_eta_pp` va vacío cuando no hay η en ninguno de los dos lados (ninguno de los dos puntos convergió).
- Siguiente paso: si la coincidencia es 41/41, M1 cierra y la campaña sigue con M2 (distancia a Kalina desde el punto del profesor).

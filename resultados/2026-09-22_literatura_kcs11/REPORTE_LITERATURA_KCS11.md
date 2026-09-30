# Reporte — Barrido dentro de la ventana validada por Elsayed et al. (2013) — KCS11

Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** (nada toca `src/`).
Grid: 60 puntos — x_b x P_alta x T_fuente = 4 x 5 x 3; `T_sumidero=283.0 K` fijo, `eta_t=eta_p=0.80` (valores del paper), `m_b=1.0 kg/s`.

## Resumen ejecutivo

**0 punto(s) KALINA** de 60. Conteo por clasificacion: CORREGIBLE=32, NO_CONVERGIO=28

## Tabla resumen por x_b

| x_b | Motivo mejor punto | Clasificacion | Mejor η | Punto (P_alta/T_fuente) | P_baja [kPa] | Wnet [kW] | Fallas |
|---|---|---|---|---|---|---|---|
| 0.55 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.176485 | 5000.0 / 463.0 | 273.545422 | 182.5052 | O1,O2 |
| 0.60 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.169504 | 5000.0 / 463.0 | 336.094595 | 206.7369 | O1,O2 |
| 0.65 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.164618 | 5000.0 / 423.0 | 398.118726 | 101.805 | O2 |
| 0.70 | mejor eta (ningun punto KALINA) | CORREGIBLE | 0.162815 | 5000.0 / 423.0 | 456.322837 | 127.1025 | O2 |

## Conteo total por clasificacion

| Clasificacion | Puntos |
|---|---|
| KALINA | 0 |
| VALIDO_ADVERTENCIA | 0 |
| CORREGIBLE | 32 |
| DEGENERADO | 0 |
| INVIABLE | 0 |
| NO_CONVERGIO | 28 |

## Hallazgos inesperados

1. **Cero KALINA, incluso dentro de la ventana que el propio paper validó.**
   O2 (riesgo de cavitación en la bomba, `T9 > T_bubble(P_baja, x_b)` bajo
   `max(T_sumidero, T_amb_diseño)`) bloquea **los 33 puntos convergentes, sin
   excepción**. Ni uno solo cierra O2 en toda la malla. Es el mismo resultado
   del barrido industrial previo y del caso base Elsayed (0.55/1500/373 →
   CORREGIBLE solo por O2, η=0.1106, que es el 11.38% del paper reproducido
   a ~2.9%). Bloqueadores entre los convergentes: O2 (33), O1 (5), y en un
   único punto N2/O5/C1/C3 (solución con balance roto, ver punto 4).

2. **O1 (título de turbina ≥ 0.90) se pierde en el vértice caliente/alto de
   la malla**: los puntos de máxima η (5000 kPa, 463 K) violan O1 en los 4
   `x_b` (η=0.159–0.176, que además es el mejor η de cada `x_b`), más
   `x_b=0.70` en (3000 kPa, 373 K). El óptimo de η de la ventana queda
   CORREGIBLE, no KALINA.

3. **Hoyos de convergencia estructurados del motor teqp — no monótonos ni en
   `P_alta` ni en `T_fuente`** (banda diagonal exigida por el dominio del
   motor, `PropertyRangeError` en `T_from_Ph`/`equilibrio_liquido_vapor`):

   | T_fuente \ P_alta | 1000 | 1500 | 2000 | 3000 | 5000 |
   |---|---|---|---|---|---|
   | 373 K | 4/4 | 4/4 | 4/4 | 2/4 | 0/4 |
   | 423 K | 0/4 | 3/4 | 2/4 | 4/4 | 4/4 |
   | 463 K | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |

   (conteo = `x_b` que convergen de los 4 probados). Fuente fría + presión
   alta y fuente caliente + presión baja salen del dominio; `T_fuente=423 K`
   es el más robusto, pero falla completo en `P_alta=1000`. No es el "hoyo"
   puntual de `x_b=0.80` del barrido anterior (que era un solo `x_b` en banda
   ancha de P_alta), pero sí confirma la misma naturaleza: el motor teqp
   abandona el rango en bandas no monótonas.

4. **Un punto "converge" con N2 roto**: `x_b=0.65, P_alta=3000, T_fuente=463`
   devuelve η=0.130277 con fallas N2,O2,O5,C1,C3 — el solver encuentra una
   solución pero el balance de energía no cierra; queda clasificado
   NO_CONVERGIO (mismo fenómeno documentado como hallazgo #4 del barrido
   industrial). No se oculta: está en el CSV con `convergio=True`,
   `clasificacion=NO_CONVERGIO`.

5. **Los 27 NO_CONVERGIO restantes son todos `PropertyRangeError` del motor**
   (mensaje tal cual en `detalle_error`); sin reintentos con otro backend
   (norma de la tarea). Ningún punto falla en la calibración de `P_baja` ni
   de `eps_*` (todos los que calibran, convergen o el error es del solve).

## Metodologia y limites

- `P_baja` calibrada por punto (burbuja a `T_sumidero+4 K`, mismo metodo que `scripts/validacion_elsayed2013.py`); `eps_*` calibrados por punto (paso base 0.85/0.75/0.80, despeje en forma cerrada para T2/T6/T9, re-resolucion, clamp [0.01, 0.999]). Todo queda en el CSV para auditar que la calibracion es por punto.
- Unicamente `TeqpAdapter` (motor rapido; verificado <0.5 % en h/s contra el motor real). Sin reintentos con otro motor.
- Todo punto probado —converja o no— esta en el CSV con su `detalle_error` real; ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78.

## Entregables

- `barrido_literatura_kcs11.csv` — 60 filas: x_b, P_alta, T_fuente, P_baja, eps_hrvg, eps_reg, eps_cond, convergio, clasificacion, eta, Wnet, fallas, detalle_error.
- Este reporte.

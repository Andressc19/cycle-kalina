# Comprobación de O5: ¿los `NO_CONVERGIO` con "fuera de la campana binaria" fallan por eso?

**Task:** `2026-10-01-comprobacion-o5-t2min` · rama `feature/rango_motores` · corrida del 2026-10-01/02.
**Salidas:** `comprobacion_o5_filas.csv` (361 combinaciones) y `comprobacion_o5_control.csv` (50 filas de control), en esta misma carpeta. Script: `scripts/comprobacion_o5_t2min.py` (199 líneas).

## La pregunta

Muchos barridos del proyecto quedaron marcados `NO_CONVERGIO` con el mensaje *"no existe equilibrio bifásico para ninguna composición"*, que en el papel significa que la salida del intercambiador calor-sal (HRVG) quedó fuera de la zona de mezcla líquido-vapor. La intuición dice que esos puntos son inviables por diseño (**criterio O5**), pero el mensaje no lo demuestra: el mismo texto aparece cuando el equilibrium sí existe y el `fsolve` simplemente no converge. La pregunta es: **¿cuáles de esos puntos quedan realmente fuera de la campana binaria, y cuántos solo fallaron por cálculo?**

## Cómo funciona la prueba (en simple)

Sin resolver el ciclo. Solo se usa la ecuación del HRVG, que es una mezcla de la salida del condensador con vapor a presión alta:

```
h2 = (1−ε)·h1 + ε·h2max
```

- **h1 / h2**: entalpía específica (kJ/kg de solución) a la salida del condensador y a la salida del HRVG. Entalpía alta = más caliente.
- **h2max**: la mayor entalpía que puede sacar el HRVG si el condensador entrega todo su vapor (ε = 1): `h(P_alta, T_fuente, x_b)`.
- **ε (eps_hrvg)**: efectividad del HRVG. En este proyecto se diseña entre 0.75 y 0.85.
- **T_sumidero / T_fuente**: temperatura del sumsidero (frío) y de la fuente caliente.
- **P_alta, x_b**: presión alta del ciclo y fracción másica de amoníaco en la salida del condensador.
- **h_rocio**: entalpía del vapor saturado a esa `(P_alta, x_b)`. **h_burbuja**: entalpía del líquido saturado a esa misma `(P_alta, x_b)`. Entre ambos dos valores el estado es líquido-vapor; por encima de `h_rocio` es vapor sobrecalentado; por debajo de `h_burbuja` es líquido comprimido.

Como físicamente `T1` (la temperatura del condensador) no puede estar por debajo del sumsidero, la entalpía de salida del HRVG está **acotada**:

```
h2_min = (1−ε)·h(P_alta, T_sumidero, x_b) + ε·h2max     (peor caso frío)
h2_max_posible = h2max                                    (peor caso caliente)
```

Eso da tres veredictos, sin invertir nada:

- **SOBRECALENTADA_DEMOSTRADA**: `h2_min ≥ h_rocio`. Ningún `T1` posible, ni ninguna efectividad posible, deja la salida dentro de la campana → el criterio O5 queda **probado**.
- **LIQUIDA_DEMOSTRADA**: `h2max < h_burbuja`. Aun con el HRVG al máximo la salida se queda líquida → O5 queda **probado** por la otra rama.
- **DENTRO_DE_CAMPANA_POSIBLE**: ninguna de las dos. Hay algún `T1` para el que la salida sí cae dentro de la campana, así que **el fallo del flash no se explica por O5**; queda abierto como posible fallo numérico. No se concluye nada más.
- **NO_EVALUABLE**: el motor no pudo calcular la comprobación; se anota el mensaje real.

## Cómo se hizo

1. Se recorrieron todos los CSV de `resultados/` (recursivo, saltando `_tmp/`) y se tomaron las filas con `clasificacion == NO_CONVERGIO` cuyo mensaje contiene la frase del flash: **383 filas crudas**.
2. Se deduplicó por `(P_alta, x_b, T_fuente, T_sumidero, eps_lo)`, guardando todos los CSV de origen en `csv_origen`. Quedaron **361 combinaciones únicas** (133 puntos físicos distintos; el resto son diferencias de `ε` o de parámetros). Ninguna combinación quedó sin parámetros: 0 filas `PARAMETROS_NO_RECONSTRUIBLES`.
3. Los parámetros que el CSV no traía se leyeron del script que lo generó (`b0_scan_cementera.py`: `T_fuente = 583.15 K`, `T_sumidero = 300.032917 K`; `calibracion_elsayed_malla.py`: `T_sumidero = 283.0 K`, heredado por los barridos de literatura, `T_fuente` baja y pinch6).
4. Motor: solo `AmmoniaWaterAdapter.h`, `bubble_point` y `dew_point`, con caché por `(P_alta, x_b)` y `(P_alta, T, x_b)`. No se llamó `resolver_ciclo`, ni `evaluar`, ni `T_from_Ph`. Cada fila va en su propio `try/except`: un fallo se registra y nunca aborta.
5. Antes: humo de 6 filas dentro de un worker real (OK, 6 `DENTRO_DE_CAMPANA_POSIBLE`), luego corrida desacoplada con `nohup`, 6 workers, una fila escrita al CSV por cada una terminada (con `flush`), progreso en `progreso.log`. El CSV es reanudable.
6. **Control de validez (obligatorio):** 25 filas `KALINA` + 25 `CORREGIBLE` con paso uniforme, la misma prueba. Esas filas sí convergieron con su estado 2 dentro de la campana, así que el veredicto esperado era `DENTRO_DE_CAMPANA_POSIBLE` en el 100 %.
7. Todas las cifras de este reporte se recalcularon desde el CSV de salida.

## Resultados

Universo: **361 combinaciones únicas** (de 383 filas crudas).

| Veredicto | Combinaciones | Qué significa |
|---|---|---|
| SOBRECALENTADA_DEMOSTRADA | **37** | O5 probado, rama sobrecalentada |
| LIQUIDA_DEMOSTRADA | **8** | O5 probado, rama líquida (4 puntos físicos, cada uno con ε = 0.75 y 0.85) |
| DENTRO_DE_CAMPANA_POSIBLE | **316** | O5 **no** es la explicación del fallo |
| NO_EVALUABLE | **0** | el motor cubrió todas las combinaciones; 0 errores |
| **Total** | **361** | |

### Por CSV de origen

| CSV de origen | SOBREC | LIQUIDA | DENTRO | NO_EVAL | Total |
|---|---|---|---|---|---|
| `2026-09-19/barridos_2026-09-19/b0_scan_cementera.csv` | 23 | 0 | 286 | 0 | 309 |
| `2026-09-19/barridos_2026-09-19/fase1_profesor/eta_vs_Tambiente_profesor.csv` | 9 | 0 | 15 | 0 | 24 |
| `2026-09-19/barridos_2026-09-19/fase1_profesor/eta_vs_Palta_profesor.csv` | 4 | 0 | 5 | 0 | 9 |
| `2026-09-19/barridos_2026-09-19/fase1_profesor/eta_vs_xb_profesor.csv` | 1 | 0 | 3 | 0 | 4 |
| `2026-10-01_benchmark_reintento/benchmark_filas.csv` | 0 | 4 | 4 | 0 | 8 |
| `2026-10-01_benchmark_reintento/respaldo_parteA_filas.csv` | 0 | 4 | 4 | 0 | 8 |
| `2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv` | 0 | 4 | 3 | 0 | 7 |
| `2026-10-01_benchmark_reintento/benchmark_minibarrido.csv` | 0 | 2 | 2 | 0 | 4 |
| `2026-10-01_benchmark_reintento/benchmark_minibarrido_mb_corregido.csv` | 0 | 2 | 2 | 0 | 4 |
| `2026-10-01_benchmark_reintento/respaldo_minibarrido_93puntos.csv` | 0 | 2 | 2 | 0 | 4 |
| `2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv` | 0 | 0 | 1 | 0 | 1 |
| `2026-09-23_pinch6_realista/barrido_pinch6_realista.csv` | 0 | 0 | 1 | 0 | 1 |
| **Suma (con doble conteo de las 10 combinaciones multi-origen)** | 37 | 8 | 316 | 0 | **383** |

Las 12 filas de la tabla suman 383 = las filas crudas, porque 10 combinaciones aparecen en más de un CSV y se cuentan en cada origen. La columna de cada CSV cuenta su combinación una sola vez.

Los 37 `SOBRECALENTADA_DEMOSTRADA` son 37 puntos físicos distintos (`P_alta` de 2000 a 7000 kPa, `x_b` de 0.35 a 0.70). La fase 1 del profesor aporta 35 combinaciones: 14 demostradas y 21 posibles.

### Control de la lógica

| Control | Filas | `DENTRO_DE_CAMPANA_POSIBLE` | Falsas "demostradas" | Errores |
|---|---|---|---|---|
| `KALINA` | 25 | 25 | 0 | 0 |
| `CORREGIBLE` | 25 | 25 | 0 | 0 |
| **Total** | **50** | **50 (100 %)** | **0** | **0** |

El margen `h2_min − h_rocio` de las 50 filas de control va de −1559 a −249.7 kJ/kg (mediana −753.6): ninguna se acerca al borde, así que el control no discrimina el caso límite.

### Qué tan holgada es la prueba

Margen `h2_min − h_rocio` [kJ/kg] en las 37 demostradas por la rama sobrecalentada (positivo = probada):

| Mínimo | p25 | Mediana | p75 | Máximo |
|---|---|---|---|---|
| **0.13** | 2.3 | **15.7** | 30.4 | 148.2 |

- 32 de 37 tienen margen mayor que 1 kJ/kg; 5 están entre 0.13 y 1 kJ/kg, es decir **al borde de la tolerancia numérica**.
- Reevaluando con `T_sumidero` 2 K más bajo, **31 de 37** siguen demostradas (las 6 que se caen son exactamente las de margen ≤ 1.5 kJ/kg). Con `T_sumidero` 2 K más alto, siguen las 37.
- Los 8 `LIQUIDA_DEMOSTRADA` son holgados: `h_burbuja − h2max` entre 66.1 y 592.5 kJ/kg (mediana 114.6). Esa prueba **no depende ni de ε ni de `T_sumidero`**, porque usa solo la cota superior.
- Las 316 `DENTRO_DE_CAMPANA_POSIBLE` están lejos del borde en la mediana (hueco de 530 kJ/kg hasta `h_rocio`), pero 10 de ellas quedan a menos de 1 kJ/kg de la frontera: para esos puntos el veredicto es "puede estar dentro", y un error de 1 kJ/kg en el motor los cambiaría de veredicto.
- `eps_supuesta = True` en 9 filas (las que no traían ε: literatura, `T_fuente` baja y pinch6), todas con `ε_lo = 0.75`. **Ninguna de las 37 demostradas sobrecalentadas depende de ese valor supuesto**: las 4 `LIQUIDA` con ε supuesto son concluyentes igual, porque su prueba no usa ε.

## Conclusión

- **O5 queda demostrado en 45 de 361 combinaciones (12.5 %): 37 sobrecalentadas y 8 líquidas.** Esas son inviables por diseño, no por cálculo: no hay forma de que la salida del HRVG caiga dentro de la campana binaria con los parámetros dados.
- **En las otras 316 (87.5 %) la hipótesis O5 no se sostiene.** El mensaje "fuera de la campana" no describe esos puntos: la salida del HRVG *podría* caer dentro de la campana, así que el `NO_CONVERGIO` de esas filas apunta a un problema numérico (o a otra causa) del flash, no a inviabilidad. Es el hallazgo más importante: la lectura "todo `NO_CONVERGIO` es inviable" no aguanta.
- En particular, **el escaneo de la cementera (309 combinaciones) es en un 92.6 % caso de flash mal resuelto**, no de puntos inviables; y la fase 1 del profesor, 21 de 35 combinaciones (60 %).
- La prueba es **dura con la rama sobrecalentada y muy blanda con la numérica**: demuestra infactibilidad, pero no dice qué pasó con las 316 restantes.
- Coherencia interna verificada: 0 filas contradicen la regla del veredicto, 0 filas con `h2_min > h2max`, tabla por origen cuadrada a 383 y control 50/50 con 0 falsas "demostradas".

## Lo que no sabemos

1. **Qué falló de verdad en las 316 filas.** La prueba solo descarta O5; no identifica la causa (convergencia del `fsolve`, braket, tolerancias, o un criterio distinto). No se investigó.
2. **Los puntos al borde.** 5 demostradas sobrecalentadas (margen ≤ 1 kJ/kg) y 10 "posibles" a menos de 1 kJ/kg de la frontera están dentro del ruido del motor. Para esas hay que mirar el margen con más decimales o repetir el flash con otro punto inicial antes de etiquetarlas.
3. **`T_sumidero` reconstruido.** 9 de los 12 CSV no traen ese parámetro; se leyó del script generador (`300.032917 K` para la cementera, `283.0 K` para literatura/pinch6). Si algún script se modificó después de correr el barrido, la reconstrucción no corresponde a la corrida real.
4. **Los supuestos de la cota.** La cota inferior asume `T1 ≥ T_sumidero` (el condensador no enfría por debajo del sumsidero) y la cota superior asume `T1 ≤ T_fuente`. Si el solver de esos barridos admitió valores fuera de ese rango, la cota se estrecha o se ensancha. `ε ≤ 1` y `h2max ≥ h1` se cumplen siempre.
5. **No se corrió el solver del ciclo en ningún momento**, así que no hay verificación cruzada de estos veredictos contra un flash que sí converja.
6. **Qué hace el motor con la zona de arrastre.** Si el flash usa el modelo psicrométrico de mezcla (aire húmedo) en vez de la mezcla binaria simple, la comparación por entalpía no es la misma comparación; esta tarea comparó solo el modelo binario.

## Qué sigue

1. **Etiquetar por veredicto, no por mensaje.** Separar en los barridos: (a) 45 combinaciones `INVIABLE_O5`, que son 41 puntos físicos distintos (37 sobrecalentadas, cada una con su propio `(P_alta, x_b, T_fuente, T_sumidero)`, más 4 líquidos, que aparecen dos veces cada uno por los dos valores de ε = 0.75 y 0.85), y (b) 316 combinaciones `REVISAR_NUMERICO`. Los `NO_CONVERGIO` no deben tratarse como una categoría única.
2. **Repetir el flash en las 316 con punto inicial distinto** (p. ej. empezar por `h = h_burbuja` o por `h = h_rocio`) y ver cuántas convergen. Si convergen, era `fsolve`; si no, hay que abrir otra hipótesis (por ejemplo, modelo de mezcla o límite de compositions del modelo).
3. **Afinar el borde.** Para las 15 filas a menos de 1 kJ/kg de la frontera, repetir el cálculo con la tolerancia del motor y reportar el margen con 3 decimales.
4. **Nada de esto pide tocar `src/`.** Si el director decide que el criterio O5 debe quedar explícito en el solver, es una tarea aparte con su propio `TASK_CONTEXT`.
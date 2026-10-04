# Tests primero del reintento tolerante — qué se preguntó y qué se midió hoy

## La pregunta

`resolver_ciclo` se rendía demasiado pronto: cuando el motor de propiedades no podía
evaluar un extremo del bracket lanzaba `PropertyRangeError` y el punto quedaba marcado
`NO_CONVERGIO`, aunque casi siempre había un bracket válido "un poco más adentro".
La pregunta de esta tarea es: **¿escribimos primero los tests que fijan ese
comportamiento (reintento solo si falla) y comprobamos que hoy fallan por lo único
correcto — que la API todavía no existe?**

Respuesta corta: sí. Hay 11 tests escritos, 10 en rojo y 1 en verde, y el rojo es
`TypeError: resolver_ciclo() got an unexpected keyword argument 'reintento_tolerante'`
en los 10. Nada de `src/` se ha tocado.

## Qué se especificó

La API que los tests exigen (decisión del director, no se cambia):

```python
resolver_ciclo(..., reintento_tolerante: bool = False,
               max_repliegues: int = 6, paso_repliegue: float = 5.0)
```

- `reintento_tolerante=False`: lo de ahora, bit a bit, y sin claves nuevas.
- `reintento_tolerante=True`: primero se intenta el camino actual (`T10_inicial`
  original, `_bracketear` original). Si eso falla por `PropertyRangeError` o
  `CicloNoConvergeError` **mientras se evalúan los extremos**, se repite **una** vez
  arrancando en `T_sumidero + 5 K` y con bracket tolerante: cada extremo que lance
  `PropertyRangeError` se repliegue hacia dentro `paso_repliegue` K, hasta
  `max_repliegues` repliegues por extremo. Cualquier otra excepción se propaga sin
  envolver. Si no hay cambio de signo, `CicloNoConvergeError`; si a `brentq` le toca
  un punto interior no evaluable, `CicloNoConvergeError` con la T en el mensaje.
- El resultado lleva `reintento_usado` **solo** si el flag está activo.

## Qué se probó

Fake: el mismo backend lineal de `tests/test_cycle_solver.py` (h = T + 10·x + 1e-3·P,
s = 0.01·T + x, campana bifásica 350–370 K a x=0.5), con una subclase que inyecta el
fallo en las T elegidas y cuenta las llamadas. Sin teqp, sin motor real: los 11 tests
corren en 1 s.

Dos casos base, porque una sola campana no reacha para todo:

| Caso base | `T_sumidero` | `T_fuente` | bracket | T1 | eta |
|---|---|---|---|---|---|
| `BASE` | 350 K | 369 K | [351, 368] | 355.572065 | −0.1392824807 |
| `BASE_ANCHO` | 330 K | 365 K | [331, 364] | 343.847315 | −0.1201222802 |

Las T donde se inyecta el fallo (368.0, 364.0, 331.0 y la banda 355.5–355.6 K) se
eligieron **midiendo** qué T visita de verdad la cascada: los extremos que se rompen
no son estados internos de la cascada, así que el fallo cae en la **primera llamada**
de la evaluación del extremo, igual que en el caso real (37 de 40 fallos reales están
en un extremo). Con las tolerancias justas (`tol_T1=1e-10`, `tol_T10=1e-8`) el mismo
punto da el mismo `eta` con brackets distintos (<1e-12); con las de fábrica la
diferencia llegaba a 7e-7 y la comparación a 1e-9 no habría servido de nada.

| # | Caso | Qué exige | Resultado hoy |
|---|---|---|---|
| 1 | Sin el flag | `eta`, T1, claves y nº de llamadas idénticos a hoy; sin `reintento_usado` | **VERDE** |
| 2 | Flag, sin fallos | mismos `eta`/T1 y **mismas llamadas** que sin flag; `reintento_usado is False` | ROJO (TypeError) |
| 3 | Extremo alto (368 K) falla | converge, `reintento_usado=True`, `eta` a <1e-9 del caso sin fallos; el extremo falla en su primera llamada (2 intentos) | ROJO (TypeError) |
| 4 | Extremo bajo (331 K) y ambos extremos | los dos subcasos convergen con el `eta` de referencia; fallan 331, 331, 364 | ROJO (TypeError) |
| 5 | Todo el rango falla (banda 300–500 K) | `CicloNoConvergeError` y nº de llamadas acotado por `2·max_repliegues + 4` (medido: 15 con tope 6) | ROJO (TypeError) |
| 6 | F sin cambio de signo | `CicloNoConvergeError` | ROJO (TypeError) |
| 7 | `max_repliegues` = 2 vs 3 | con tope 2 y 3 fallos seguidos del extremo: no converge y **no llega a evaluar el 4º intento** (349 K); con tope 3 sí converge y sí llega | ROJO (TypeError) |
| 8 | `paso_repliegue=2.0` | las T evaluadas son 366 K (368−2) y **no** 363 K (368−5) | ROJO (TypeError) |
| 9 | `ValueError` en el extremo | se propaga y **no** hay segundo intento (una sola falla registrada) | ROJO (TypeError) |
| 10 | Punto interior no evaluable (banda 355.5–355.6 K, solo la toca `brentq`) | `CicloNoConvergeError` con la T (355.555 K) en el mensaje | ROJO (TypeError) |
| 11 | Dos llamadas seguidas iguales | mismo `eta`, misma T1, mismo nº de llamadas y misma secuencia de T: el intento fallido no deja estado | ROJO (TypeError) |

Salida completa: `pytest_rojo.txt` (10 failed, 1 passed en 0.99 s).

**Los tests son satisfacibles**: con un prototipo del reintento inyectado por
monkeypatch (fuera del repo, no es parte de la entrega) los 11 pasan en 0.07 s. Eso
descarta que estén rojos por un error del fake o de las constantes.

## Verificación lenta con el motor real

`scripts/verificar_controles_reintento.py` (126 líneas) toma de `sonda_filas.csv` las
10 filas de control (`ctl_*`) y 5 rescatadas por el prototipo (2 `f2_T_from_Ph`, 2
`lit_T_from_Ph`, 1 `lit_bifasico`: las primeras, en orden de CSV, donde el intento
original falla y V2 converge), llama a `resolver_ciclo(..., reintento_tolerante=True)`
con `TeqpVerificado` y compara `eta` (|Δη| < 1e-4) y la clasificación.

Hoy: **15/15 filas con el mismo TypeError de API**, una línea por fila en
`progreso.log`, y salida con código 1 y el mensaje claro de que la implementación está
pendiente.

El guion se comprobó con el motor real y el prototipo en 3 filas:

| Fila | eta | Δη | clasificación | `reintento_usado` |
|---|---|---|---|---|
| `ctl_literatura` 0 | 0.087667 | −2.6e−07 | CORREGIBLE (ref CORREGIBLE) | False |
| `ctl_KALINA_f2` 0 | 0.118260 | +5.6e−17 | KALINA (ref KALINA) | False |
| `lit_T_from_Ph` 5 (rescatada) | 0.075082 | −2.6e−07 | CORREGIBLE (ref CORREGIBLE) | **True** |

## Línea base

`pytest -q -rf --ignore=tests/test_reintento_tolerante.py` →
**182 passed, 1 skipped, 8 xfailed, 0 failed** en 686.56 s (`linea_base_suite.txt`).
Sin cambios en la suite que ya existía: el archivo nuevo solo añade los 11 tests.

## Lo que no sabemos

- Cuál de las dos lecturas de `max_repliegues` implementará el código: los tests
  asumen `max_repliegues` = número de **repliegues**, o sea `max_repliegues + 1`
  intentos por extremo (con tope 2 se intentan 368, 363, 358). Si se implementa como
  número de intentos, el caso 7 espera un 4º intento que no ocurriría.
- De las 15 filas del guion solo se ejecutaron 3 con el prototipo. Las otras 12
  dependen de la implementación real (y de ella depende que 802, 885, 11 y 10 salgan
  `CORREGIBLE` con `eta` igual a la del CSV).
- El caso 10 depende de una banda estrecha (0.1 K) alrededor de 355.555 K. Es
  determinista mientras el bracket siga siendo [351, 363] y `brentq` sea `brentq`,
  pero si la implementación cambiara el orden de evaluación de los extremos, la banda
  podría tocar un extremo y el test cambiaría de significado.
- Las 12 filas del caso real que ninguna variante rescata (motivos ajenos al arranque:
  `h(P, s, x)`, ELV inexistente, `T_from_Ph` sin cobertura) seguirá sin convergir con
  este reintento: aquí solo se acota lo que el repliegue del bracket puede arreglar.

## Qué sigue

1. Implementar la API en `src/cycle_solver.py` siguiendo la spec de arriba (tarea de
   implementación, no esta).
2. Correr `.venv\Scripts\python -m pytest tests/test_reintento_tolerante.py` y
   esperar 11 verdes.
3. Correr `.venv\Scripts\python scripts\verificar_controles_reintento.py` y esperar
   15 filas con `|Δη| < 1e-4` y la clasificación del CSV (esto cuesta ~15–20 min).
4. Comparar contra la línea base: la suite completa debe seguir en 182 passed.
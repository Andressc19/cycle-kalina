---
project: ciclo_kalina_tercero
task_id: 2026-10-01-comprobacion-o5-t2min
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Comprobación rigurosa y barata de "salida del HRVG fuera de la campana" (O5) en los NO_CONVERGIO. SIN tocar `src/`, SIN correr el solver del ciclo

## Task ID

2026-10-01-comprobacion-o5-t2min

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques.

## Contexto

Muchos `NO_CONVERGIO` de `resultados/` tienen el mensaje `equilibrio_liquido_vapor(...): no existe equilibrio bifásico para ninguna composición (T fuera de la campana binaria a esa P...)`: Fase 1 del profesor (33 de 40 filas), el escaneo de la cementera (≈309 de 352), 7 de la ventana de literatura y algunos más. Se supone que son puntos donde la salida del HRVG (estado 2) queda fuera de la campana (criterio **O5**, INVIABLE), pero **no está demostrado**: (a) el mensaje venía de un extremo del bracket del solver, no de la solución; (b) ese mismo texto lo emite el flash cuando de verdad no hay equilibrio **y también cuando el `fsolve` no converge** (fallo numérico). El director NO quiere asumirlo ni arriesgar el motor: quiere una prueba que no dependa del solver del ciclo.

## La prueba (cota exacta, sin resolver el ciclo)

El HRVG cumple `h2 = (1−ε)·h1 + ε·h2max`, con `h1 = h(P_alta, T1, x_b)` y `h2max = h(P_alta, T_fuente, x_b)`. `h2` crece con `h1` y con ε (ε ≤ 1, h2max ≥ h1). Físicamente `T1 ≥ T_sumidero` (y T1 ≤ T_fuente). Por tanto, para cualquier solución posible del ciclo:

- **Cota inferior** `h2_min = (1−ε_lo)·h(P_alta, T_sumidero, x_b) + ε_lo·h2max`, con `ε_lo` = la menor efectividad HRVG admisible (ver abajo).
- **Cota superior** `h2_max_posible = h2max` (T1 = T_fuente y ε = 1).

Veredicto por fila (comparando ENTALPÍAS, sin invertir T con `T_from_Ph`, que es la parte frágil):
1. `h2_min ≥ h_rocio` donde `h_rocio = h(P_alta, T = T_rocio(P_alta, x_b), x_b)` → **SOBRECALENTADA_DEMOSTRADA** (ningún T1 posible deja el estado 2 dentro de la campana; es O5 por la rama sobrecalentada).
2. `h2max < h_burbuja` donde `h_burbuja = h(P_alta, T = T_burbuja(P_alta, x_b), x_b)` → **LIQUIDA_DEMOSTRADA**.
3. Ninguna de las dos → **DENTRO_DE_CAMPANA_POSIBLE**: para algún T1 la salida podría estar dentro de la campana, así que el fallo del flash NO se explica por O5 y podría ser numérico. NO se concluye nada más.
4. Si el motor falla en la comprobación misma → **NO_EVALUABLE** con el mensaje real (no se reintenta con otra cosa, no se inventa).

**Efectividades:** si el CSV trae `eps_hrvg` para la fila, `ε_lo = eps_hrvg` de la fila. Si está vacío (como en los NO_CONVERGIO de literatura), usar `ε_lo = 0.75` y marcar la columna `eps_supuesta = True`, de modo que el veredicto SOBRECALENTADA_DEMOSTRADA signifique "para todo ε_hrvg ≥ 0.75" (banda de diseño del proyecto: 0.75–0.85). No inventes otro valor.

## Objective

1. Crear `scripts/comprobacion_o5_t2min.py` (nuevo, ≤200 líneas).
2. **Universo:** todas las filas de los CSV en `resultados/` (recursivo, ignorando `_tmp/`) con `clasificacion == NO_CONVERGIO` cuyo mensaje (`mensaje`, `detalle_error` o equivalente) contenga "no existe equilibrio bifásico". Deduplica por `(P_alta, x_b, T_fuente, T_sumidero, eps_hrvg)` (varios CSV repiten puntos; conserva la lista de orígenes). Los parámetros que el CSV no traiga (p. ej. `T_sumidero`) se leen del script que generó el CSV; si no se pueden reconstruir con certeza, marca la fila `PARAMETROS_NO_RECONSTRUIBLES` y sigue (no inventes).
3. Motor: `AmmoniaWaterAdapter` (motor de referencia; **solo** `h`, `bubble_point`, `dew_point`, 3–4 llamadas por combinación distinta, con caché por `(P_alta, x_b)` y por `(P_alta, T, x_b)`). **No** llamar a `resolver_ciclo`, `evaluar`, `_bracketear` ni `T_from_Ph`. Cada fila dentro de `try/except` (`PropertyRangeError`, `ValueError`, `RuntimeError`, `ArithmeticError`): un fallo se registra en la fila y NUNCA aborta la corrida.
4. **Control de validez de la lógica (obligatorio):** tomar 25 filas con `clasificacion == KALINA` y 25 `CORREGIBLE` de los CSV de barridos (repartidas con paso uniforme) y aplicar la misma prueba. Como esas filas SÍ convergieron con su estado 2 dentro de la campana, el veredicto esperado es **DENTRO_DE_CAMPANA_POSIBLE** en el 100 %. Si alguna sale SOBRECALENTADA_DEMOSTRADA o LIQUIDA_DEMOSTRADA, la lógica o los parámetros están mal: **detén el resto, reporta la fila y la causa**, no continúes.
5. Ejecución: cálculo largo desacoplado con `nohup`, **una fila escrita al CSV por cada una terminada** (con `flush`), progreso en `resultados/2026-10-01_comprobacion_o5/progreso.log`, 6 workers (`ProcessPoolExecutor`; en Windows los parches/aislamientos se aplican dentro del worker). Nunca un comando de más de ~90 s en primer plano. Antes de la corrida completa, humo de 6 filas **dentro de un worker**. El CSV debe ser reanudable (omitir las filas ya presentes).

## Constraints

- **No modificar** `src/`, `tests/`, ni ningún script/CSV existente. Archivos nuevos solo en `scripts/` y `resultados/2026-10-01_comprobacion_o5/`. Nada en la raíz del repo ni `.log` sueltos.
- No instanciar teqp; no correr barridos; no cambiar ninguna constante del motor.
- Registrar `git branch --show-current` y `git status --short src` al inicio y al final y reportarlos (otras sesiones comparten el checkout); si `src/` cambia, detente y repórtalo. No ejecutes `git checkout/switch/commit/stash`.
- Sin credenciales; no leer fuera de `D:\Desktop\ciclo_kalina_tercero`.
- Recalcula toda cifra del reporte desde los CSV y verifica que las tablas suman.

## Outputs

- `resultados/2026-10-01_comprobacion_o5/comprobacion_o5_filas.csv`: una fila por combinación única con `csv_origen(s)`, parámetros, `eps_supuesta`, `h1_min`, `h2max`, `h2_min`, `h_rocio`, `h_burbuja`, `T_rocio`, `T_burbuja`, `margen_sobrecalentada = h2_min − h_rocio` [kJ/kg], `veredicto`, `error`.
- `comprobacion_o5_control.csv` (las 50 filas de control y su veredicto).
- `REPORTE_COMPROBACION_O5.md`, en lenguaje llano, formato: **La pregunta · Cómo funciona la prueba (en simple) · Cómo se hizo · Resultados (tabla de veredictos por CSV de origen; control) · Conclusión · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea. Indica explícitamente cuántas de las filas con ese mensaje son SOBRECALENTADA_DEMOSTRADA, cuántas LIQUIDA_DEMOSTRADA, cuántas DENTRO_DE_CAMPANA_POSIBLE (posible fallo numérico del flash) y cuántas NO_EVALUABLE; y el margen mínimo/mediana de `h2_min − h_rocio` en las demostradas (qué tan holgada es la prueba).

## Done criteria

- Control de 50 filas: 0 falsas "demostradas".
- Todas las filas del universo con veredicto o error registrado; CSV con filas únicas; sumas verificadas.
- Reporte con las 4 cifras de veredicto y la interpretación honesta (qué prueba y qué NO prueba).
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS). No decidir cambios en `src/` ni de etiquetas.

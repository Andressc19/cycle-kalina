---
project: ciclo_kalina_tercero
task_id: 2026-10-01-benchmark-reintento-tolerante
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Benchmark de tiempos del "reintento tolerante" (modos, topes y salida temprana). SIN tocar `src/`

## Task ID

2026-10-01-benchmark-reintento-tolerante

## Project

`ciclo_kalina_tercero`, rama `fix/solver-bracket-tolerante`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques. Esta tarea continúa `prompts/TASK_CONTEXT_ablacion_arranque_tiempos.md`; reutiliza `scripts/sonda_arranque_solver.py` (`muestra()`, `Proxy`, `_bracket_tol`, parámetros por fila) y `scripts/sonda_ablacion_tiempos.py` sin modificarlos.

## Contexto

Se va a implementar un **reintento tolerante** en el solver (V2 = arranque `T10_inicial = T_sumidero+5 K` + bracket con repliegue de 5 K cuando un extremo lanza `PropertyRangeError`). Lo que ya se sabe (sonda previa, 56 filas): rescata 28 de 40 filas que fallaban; cuesta ~3.4x más evaluaciones de `F` solo en las filas que fallaban; los 12 no rescatables son los más caros (media 121 s, p90 290 s). Los CSV de los barridos históricos NO traen tiempos por punto, y los reportes solo traen medias sueltas (p. ej. teqp ≈ 31 s/punto en el barrido de 30 puntos de `2026-09-27_costo_soluciones`; x_b industrial ≈ 65 min para 117 puntos). El director necesita **tiempos reales** para decidir CUÁNDO aplicar el reintento sin perder la ventaja de velocidad de teqp.

## Modos a comparar (todos reimplementados DENTRO del script, sin editar `src/`)

- **M0 (actual):** `T10_inicial=None`, `_bracketear` original. (Referencia.)
- **MA (siempre tolerante):** V2 desde el primer intento.
- **MB (reintento solo si falla):** correr M0; si lanza `PropertyRangeError` o `CicloNoConvergeError` durante el bracketeo (en los extremos), repetir con V2. El tiempo de MB = tiempo del intento fallido de M0 + tiempo de V2. Si M0 converge, MB = M0 exactamente (verifica que T1, η y número de evaluaciones coinciden).
- **Topes:** `max_repliegues` ∈ {2, 3, 6} intentos por extremo, con paso de 5 K (el 6 es V2 actual; en la sonda previa `_bracket_tol` ya admite un tope: si no es parametrizable desde el script, escribe una copia local, sin editar el original).
- **Salida temprana (ST):** regla EXACTA, no la amplíes: si el error de un extremo es `PropertyRangeError` de `equilibrio_liquido_vapor` con el texto "no existe equilibrio bifásico" Y el extremo opuesto falla con el mismo error en su primer intento de repliegue, abortar con `NoBracket` sin seguir replegando. Medir con ST activada y desactivada.

Combinaciones a medir sobre las filas que M0 no resuelve: MB con tope {2,3,6} × ST {sí,no} = 6 configuraciones. MA solo con tope 6 y sin ST (es V2: tómalo de `resultados/2026-10-01_ablacion_tiempos/ablacion_filas.csv`, no lo recalcules).

## Objective

### Parte A — Tiempos reales de los puntos (calibración)
1. **Filas que fallan:** las 40 filas que M0 no resuelve de la muestra de la sonda (`muestra()`), con las 6 configuraciones de MB. Por fila: `convergio`, `clasificacion`, `eta`, `t_s`, `nF`, causa.
2. **Filas que convergen:** 30 filas `convergio=True` tomadas de los CSV de barridos en los que `muestra()` ya sabe reconstruir parámetros (`busqueda_libre_v2.csv`, `barrido_literatura_kcs11.csv`), repartidas con paso uniforme (no las 30 primeras). Medir M0 y verificar que MB da exactamente el mismo resultado y `nF`. Estas filas dan el coste real de un punto sano.
3. 6 workers como las sondas previas. **Medir todo en la misma carga**; reportar tiempo de pared.

### Parte B — Mini-barrido de validación del tiempo
Armar un mini-barrido de **60 puntos** con la mezcla de resultado real (≈30 % `NO_CONVERGIO`, ≈70 % convergentes) sacando puntos de los CSV reales (mismos parámetros que ya se corrieron). Correrlo de extremo a extremo con 6 workers en M0, MB(mejor configuración de la Parte A según criterio de abajo) y MA. Medir **tiempo de pared total del mini-barrido** en cada modo.

### Parte C — Extrapolación a cada barrido histórico
Para cada CSV de barrido (`busqueda_libre_v2`, `ronda5_diagnostico`, `ronda6_diagnostico`, `barrido_xb_industria`, `barrido_literatura_kcs11`, `barrido_margen2k`, `barrido_pinch6_realista`): contar filas totales y filas `NO_CONVERGIO` (de los propios CSV) y estimar el tiempo total en M0, MA y MB(mejor) con los costes medidos en la Parte A (tiempo medio de fila sana, de fila fallida en M0, de fila fallida en MB). Etiquetar claramente que es **extrapolación** y qué parte es medida. Incluir también una fila "tiempo real conocido" cuando el reporte del barrido lo traiga (p. ej. x_b industrial ≈ 65 min); si no hay dato, escribir "sin dato registrado".

## Criterio para elegir la "mejor configuración" de MB (sin inventar otro)
Entre las 6 configuraciones, la de menor tiempo total sobre las 40 filas que fallan **sujeta a** no perder más de 2 filas rescatadas respecto de MB(tope 6, ST no). Si ninguna cumple, la de tope 6 sin ST. Repórtalo con la tabla completa; la decisión final es del director.

## Outputs

- `scripts/benchmark_reintento_tolerante.py` (nuevo, ≤200 líneas; si no cabe, divide en 2 archivos).
- `resultados/2026-10-01_benchmark_reintento/benchmark_filas.csv`, `benchmark_minibarrido.csv`, `extrapolacion_barridos.csv`.
- `resultados/2026-10-01_benchmark_reintento/progreso.log`: **el script debe escribir aquí una línea cada vez que termine una fila** (`n/total (segundos transcurridos)`), con `flush`. Es lo que usa el verificador de actividad del director.
- `resultados/2026-10-01_benchmark_reintento/REPORTE_BENCHMARK.md`, con este formato: La pregunta · Cómo se midió · Resultados (tablas) · Tiempos · Conclusión · Lo que no sabemos · Qué sigue. Lenguaje llano, define cada término técnico en una línea.

## Constraints

- **No modificar** `src/`, `tests/`, ni scripts/CSV existentes. No crear archivos fuera de `scripts/` y `resultados/2026-10-01_benchmark_reintento/` (nada en la raíz del repo, ni `.log` sueltos, ni `_verif.txt`).
- Backend: `TeqpVerificado`. Filas que salgan KALINA: verificar con `verificar_turbina` + `AmmoniaWaterAdapter` (una instancia). Las `CORREGIBLE` rescatadas no se verifican con motor real: dilo.
- Recalcula toda cifra del reporte desde los CSV generados y verifica que las tablas suman (en tareas previas hubo sumas inconsistentes y columnas mal rotuladas; revisa las etiquetas).
- Si el total supera ~120 min de reloj de pared, reduce la Parte B a 30 puntos y repórtalo.
- No escribir credenciales; no leer fuera de `D:\Desktop\ciclo_kalina_tercero`.

## Done criteria

- 6 configuraciones de MB medidas en las 40 filas que fallan; M0 y MB idénticos en las 30 filas sanas.
- Tiempo de pared del mini-barrido en M0/MB/MA.
- Tabla de extrapolación por barrido con partes medidas y extrapoladas diferenciadas.
- `progreso.log` escrito durante toda la corrida.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS). No decidir cambios en `src/`.

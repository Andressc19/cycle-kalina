---
project: ciclo_kalina_tercero
task_id: 2026-10-01-benchmark-cierre-topes
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Cierre del benchmark: corregir los topes (ERROR del director), reutilizar lo ya medido, Parte C y reporte. SIN tocar `src/`

## Task ID

2026-10-01-benchmark-cierre-topes

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques. Esta tarea CONTINÚA y SUSTITUYE los pasos pendientes de `prompts/TASK_CONTEXT_benchmark_reintento_tolerante.md`, que fue interrumpida a propósito.

## Qué ya está hecho (NO repetir; reutilizar desde disco)

En `resultados/2026-10-01_benchmark_reintento/` existen:
- `benchmark_filas.csv` (Parte A, 340 filas: M0, MB con tope 2/3/6 y ST sí/no; 40 filas que M0 no resuelve + 30 sanas). **Es la fuente de verdad de lo ya medido.** Copia: `respaldo_parteA_filas.csv`.
- `benchmark_minibarrido.csv` (Parte B de **93 puntos** × 3 modos M0/MB(tope 6)/MA). Copia: `respaldo_minibarrido_93puntos.csv`. Una repetición de 60 puntos quedó incompleta y se descarta (no la uses; `stdout_parte_b.txt` y `progreso.log` son de esa corrida).
- Scripts: `scripts/benchmark_reintento_tolerante.py`, `scripts/benchmark_modos.py`, `scripts/benchmark_extrapolacion.py` (no los modifiques; si necesitas cambios, copia a un archivo nuevo).

## El error que corrige esta tarea

La tarea anterior asumió que "tope 6 = V2 actual". **Es falso:** `_bracket_tol` de `scripts/sonda_arranque_solver.py` NO tiene tope de intentos (repliega 5 K por vez mientras `lo + paso < hi`). Con tope 6 el modo MB recuperó solo **11 de las 40** filas (V2, sin tope, recuperó 28). Por eso los topes {2,3,6} no sirven para decidir. Los resultados de `MB_t6_*` de la Parte B de 93 puntos también están afectados en recuperación (los tiempos sí son válidos).

## Objective

### Parte A2 — Barrido de topes corregido (las 40 filas que M0 no resuelve)
Medir MB (reintento solo si falla, como en la tarea anterior) con paso 5 K y:
- `max_repliegues` ∈ {10, 15} con ST no;
- **sin tope** (repliega hasta agotar el rango, equivalente a V2) con ST no y con ST sí.
Total 4 configuraciones × 40 filas. Reutiliza M0 y MB_t2/t3/t6 de `benchmark_filas.csv` sin recalcular. Misma regla de ST de la tarea anterior (no la amplíes). 6 workers, misma instrumentación (`nF`, `t_s`, `t_intento1_s`, `reintento_usado`, causa). Escribe `benchmark_filas_topes.csv` (solo las filas nuevas) y progreso en `progreso_cierre.log` (una línea por fila con `flush`).

**Control de coherencia:** MB sin tope debe reproducir las 28 filas recuperadas de V2 (`resultados/2026-10-01_ablacion_tiempos/ablacion_filas.csv`) y el mismo `eta` (|Δη| < 1e-6) en las filas comunes. Si no coincide, repórtalo antes de seguir y explica por qué.

### Parte A3 — La discrepancia en filas sanas
En la Parte A, MB_t6_STno "reproduce a M0 en 29/30 filas sanas (1 discrepancia)". Identifica la fila, compara fila a fila M0 vs MB (`eta`, `T1_sol`, `nF`, `reintento_usado`) y explica la causa con evidencia. No supongas: si no se puede explicar, repórtalo en UNRESOLVED.

### Parte A4 — Elegir la configuración
Criterio EXACTO (no inventes otro): entre las configuraciones con ST no, la **de menor tope que recupera el mismo número de filas que "sin tope"**; si dos empatan en filas, la de menor tiempo total sobre las 40. Reporta la tabla completa (config, filas recuperadas, tiempo total de las 40, nF medio, filas/1000 s) y la elegida. La decisión final es del director.

### Parte B2 — Corrección del mini-barrido (93 puntos)
Repite SOLO el modo MB con la configuración elegida en A4 sobre los mismos 93 puntos de `benchmark_minibarrido.csv` (6 workers, misma carga); M0 y MA se toman del CSV existente sin recalcular. Escribe `benchmark_minibarrido_mb_corregido.csv`. Reporta tiempo de pared de M0, MB corregido y MA, filas recuperadas por modo y la fracción de puntos NO_CONVERGIO original.

### Parte C — Extrapolación por barrido histórico
Con `scripts/benchmark_extrapolacion.py` (o una copia mejorada), para `busqueda_libre_v2`, `ronda5_diagnostico`, `ronda6_diagnostico`, `barrido_xb_industria`, `barrido_literatura_kcs11`, `barrido_margen2k`, `barrido_pinch6_realista`: contar filas y `NO_CONVERGIO` desde los propios CSV y estimar tiempo total en M0, MB corregido y MA con los costes MEDIDOS (fila sana, fila fallida en M0, fila fallida en MB corregido). Separa explícitamente lo medido de lo extrapolado; si un reporte trae tiempo real conocido, inclúyelo (p. ej. xb_industria ≈ 65 min, 117 puntos; costo_soluciones: 30.98 s/punto teqp); si no, "sin dato registrado". Escribe `extrapolacion_barridos.csv`.

## Constraints

- **No modificar** `src/`, `tests/`, ni los CSV/scripts ya existentes (son la evidencia). Archivos nuevos solo en `scripts/` y `resultados/2026-10-01_benchmark_reintento/`. Nada en la raíz del repo, ni `.log` sueltos.
- Backend: `TeqpVerificado`. Filas KALINA que salgan: verificar con `verificar_turbina` + `AmmoniaWaterAdapter`; las `CORREGIBLE` no se verifican con motor real: dilo.
- **Otras sesiones comparten este checkout** (el repo puede cambiar de rama durante la corrida). Al inicio y al final registra `git branch --show-current` y `git status --short src` y repórtalos; si `src/` cambió, avisa porque invalida las mediciones. No ejecutes `git checkout`/`switch`/`commit`/`stash`.
- Recalcula toda cifra del reporte desde los CSV y verifica que las tablas suman y que las columnas están bien rotuladas (en tareas previas hubo sumas y etiquetas mal).
- Si el total supera ~100 min de reloj de pared, avisa en el reporte qué partes se redujeron.
- No escribir credenciales; no leer fuera de `D:\Desktop\ciclo_kalina_tercero`.

## Outputs

- `benchmark_filas_topes.csv`, `benchmark_minibarrido_mb_corregido.csv`, `extrapolacion_barridos.csv`, `progreso_cierre.log`.
- `resultados/2026-10-01_benchmark_reintento/REPORTE_BENCHMARK.md` con este formato, en lenguaje llano y definiendo cada término técnico en una línea: **La pregunta · Cómo se midió (incluye cómo se desarrolló: scripts, instrumentación, qué se reutilizó) · Resultados (tablas) · Tiempos · Conclusión · Lo que no sabemos · Qué sigue**. Incluye una sección corta "Corrección del error de los topes".

## Done criteria

- 4 configuraciones nuevas medidas en 40 filas; MB sin tope reproduce las 28 de V2.
- Discrepancia de la fila sana explicada o declarada sin explicar.
- Configuración elegida con el criterio dado.
- Mini-barrido de 93 puntos con MB corregido y tiempos de los tres modos.
- Tabla de extrapolación por barrido con partes medidas y extrapoladas diferenciadas.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS). No decidir cambios en `src/`.

---
project: ciclo_kalina_tercero
task_id: 2026-10-01-benchmark-continuacion
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Continuación del cierre del benchmark (A2 ya ejecutada por procesos huérfanos). SIN tocar `src/`

## Task ID

2026-10-01-benchmark-continuacion

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques. Esta tarea CONTINÚA `prompts/TASK_CONTEXT_benchmark_cierre_topes.md` (léelo completo: es la especificación; este archivo solo cambia el punto de partida y la forma de ejecutar).

## Qué ocurrió (punto de partida)

La ejecución anterior de OpenCode fue **terminada por el límite de tiempo de su comando en segundo plano** a mitad de la etapa A2. Los procesos de Python de A2 (160 mediciones, 6 workers, lanzados por esa ejecución) sobrevivieron como huérfanos y escriben en `resultados/2026-10-01_benchmark_reintento/` (`stdout_cierre_a2.txt`, `benchmark_filas_topes.csv`, `progreso_cierre.log`). El piloto previo confirmó que MB sin tope reproduce V2 exactamente en la fila `busqueda_libre_v2` 1411 (Δη = 0).

## ACTUALIZACIÓN (18:15): A2 FALLÓ y no dejó datos

Los procesos huérfanos terminaron a las 18:12 con **`RecursionError`** y **`benchmark_filas_topes.csv` NO existe** (se perdieron ~35 min de cómputo de 6 workers). La causa, vista en `stdout_cierre_a2.txt`: en `scripts/benchmark_cierre_modos.py`, `cfg_nombre` (línea ~51) llama a `BM.cfg_nombre(cfg)`, y `medir` (línea ~92) hace `BM.cfg_nombre = cfg_nombre` (el parche); desde ese momento `BM.cfg_nombre` ES `cfg_nombre` y se llama a sí misma sin fin. Debe guardarse la referencia original ANTES del parche (como ya se hace con `_BRACKET_TOPE = BM._bracket_tope`). La prueba piloto no lo detectó porque no pasó por el camino con el parche aplicado dentro de un worker.

## Paso 0 (obligatorio, antes de nada)

1. Verifica el estado: no debe haber procesos `python.exe` ejecutando `benchmark_*.py` y `benchmark_filas_topes.csv` **no existe**. Si de pronto existiera con 160 filas, úsalo y salta al Paso 3.
2. Registra `git branch --show-current` y `git status --short src` (inicio y fin). No ejecutes `git checkout/switch/commit/stash`.
3. **Corrige el bug** en `scripts/benchmark_cierre_modos.py` (archivo creado por la ejecución interrumpida de esta misma tarea; este es el único archivo existente que puedes editar, con el cambio mínimo: guardar `_CFG_NOMBRE_ORIG = BM.cfg_nombre` antes del parche y llamarlo desde `cfg_nombre`). Revisa si hay OTRA referencia circular análoga en `benchmark_cierre_topes.py`.
4. **Haz el humo por el camino real:** ejecuta, con el mismo `pool`/`medir`/parche que usará la corrida completa y **dentro de un worker (ProcessPool)**, 2 filas × 4 configuraciones nuevas (8 mediciones) y comprueba que devuelven resultados sin excepción. Solo entonces lanza A2 completa.
5. **Haz A2 incremental y reanudable:** cada fila terminada debe **añadirse inmediatamente** a `benchmark_filas_topes.csv` (con `flush`) y registrarse con una línea en `progreso_cierre.log` (`A2 n/160 (segundos) <config> <fila>`); si el CSV ya tiene filas, la corrida omite las ya hechas. Una excepción en una fila se registra en la propia fila (columna `causa`/`msg`) y NO aborta la corrida. Así ningún fallo vuelve a destruir el trabajo.

## Objective

Completar, con lo ya generado en disco, las partes que faltaban de `TASK_CONTEXT_benchmark_cierre_topes.md`: **A2 (control de coherencia sobre el CSV de topes), A3, A4, B2, C y el reporte final.** No repitas mediciones que ya existen (A2, Parte A anterior, Parte B de 93 puntos con M0 y MA).

## Forma de ejecutar (IMPORTANTE: la causa del incidente)

El comando de shell del agente tiene un límite de tiempo. Cualquier cálculo de más de ~1 minuto debe lanzarse **desacoplado** y seguirse con consultas cortas:

```
nohup .venv\Scripts\python -u scripts/<script>.py <args> > resultados/2026-10-01_benchmark_reintento/stdout_<tarea>.txt 2>&1 &
```
y luego consultar con comandos de pocos segundos (`tail`, `tasklist`). Nunca esperes con un `sleep` mayor de ~90 s en un solo comando. Cada script nuevo debe escribir **una línea de progreso por fila terminada** (con `flush`) en `progreso_cierre.log`, para que el director pueda vigilarlo.

## Constraints

- Mismas que `TASK_CONTEXT_benchmark_cierre_topes.md`: no modificar `src/`, `tests/` ni los CSV/scripts existentes; archivos nuevos solo en `scripts/` y `resultados/2026-10-01_benchmark_reintento/`; nada en la raíz; `TeqpVerificado`; KALINA verificadas con `verificar_turbina` + `AmmoniaWaterAdapter`; recalcular cada cifra desde los CSV y verificar sumas y etiquetas de columnas; sin credenciales; sin leer fuera del proyecto.
- Si algo en `src/` aparece modificado (`git status --short src` no vacío), detente y repórtalo: invalida las mediciones.

## Outputs

Los de `TASK_CONTEXT_benchmark_cierre_topes.md` (`benchmark_minibarrido_mb_corregido.csv`, `extrapolacion_barridos.csv`, `REPORTE_BENCHMARK.md` con el formato indicado, en lenguaje llano), más una sección en el reporte que cuente el incidente (ejecución interrumpida, A2 completada por procesos huérfanos, verificación del CSV de 160 filas).

## Done criteria

- Paso 0 reportado (160 filas, rama, estado de `src/`).
- Control de coherencia: MB sin tope = V2 (28 recuperadas, |Δη| < 1e-6 en filas comunes) o discrepancia explicada.
- A3, A4, B2 y C completas según la especificación original.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS). No decidir cambios en `src/`.

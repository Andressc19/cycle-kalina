---
project: ciclo_kalina_tercero
task_id: 2026-10-01-tests-primero-reintento-tolerante
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Tests PRIMERO del reintento tolerante (deben FALLAR contra el código actual). SIN tocar `src/`

## Task ID

2026-10-01-tests-primero-reintento-tolerante

## Project

`ciclo_kalina_tercero`, rama `fix/solver-bracket-tolerante`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques.

## Contexto

Desarrollo guiado por tests: se escriben ANTES de implementar. Todavía NO se implementa nada en `src/`. Las pruebas definen el comportamiento esperado del **reintento tolerante** de `resolver_ciclo`, y deben fallar hoy (por API inexistente) y pasar después de la implementación. Evidencia de respaldo: `resultados/2026-10-01_ablacion_tiempos/REPORTE_ABLACION_TIEMPOS.md` y `resultados/2026-09-30_arranque_solver/REPORTE_ARRANQUE_SOLVER.md` (el script `scripts/sonda_arranque_solver.py` tiene un prototipo de la lógica: `F_seguro`, `_bracket_tol`; úsalo solo como referencia de comportamiento, no lo importes en los tests).

## Especificación de la API (decisión del director; no la cambies)

`resolver_ciclo(..., reintento_tolerante: bool = False, max_repliegues: int = 6, paso_repliegue: float = 5.0)`

- `reintento_tolerante=False` (por defecto): comportamiento **idéntico al actual**, bit a bit.
- `reintento_tolerante=True` (modo "reintento solo si falla"): se ejecuta primero el camino actual (`T10_inicial` original, `_bracketear` original). Si ese intento lanza `PropertyRangeError` o `CicloNoConvergeError` **durante el bracketeo** (evaluación de los extremos), se repite UNA vez con: arranque `T10_inicial = T_sumidero + 5.0 K` en la primera evaluación y bracket tolerante (si el extremo `lo`/`hi` lanza `PropertyRangeError`, se repliega hacia el interior `paso_repliegue` K por intento, hasta `max_repliegues` intentos por extremo; otras excepciones se propagan). Si tras el repliegue no hay cambio de signo → `CicloNoConvergeError`. Si `brentq` encuentra un punto interior no evaluable (`PropertyRangeError` dentro de la búsqueda) → `CicloNoConvergeError` con el valor de T en el mensaje (no se inventa otra recuperación).
- El dict de salida lleva la clave extra `reintento_usado` (bool) **solo si** `reintento_tolerante=True`; con `False` las claves son exactamente las actuales.
- Solo se toleran `PropertyRangeError`; `ValueError`, `TypeError` y demás se propagan sin envolver.

## Objective

1. **`tests/test_reintento_tolerante.py`** (nuevo, ≤200 líneas, rápido, SIN teqp ni motor real; usa un `PropertyBackend` fake como `tests/test_cycle_solver.py`, extendido en el propio archivo con una subclase que lance `PropertyRangeError` en temperaturas elegidas). Casos mínimos:
   1. Sin el flag: resultado idéntico al actual (mismo `eta`, `T1`, mismas claves) y número de llamadas al backend idéntico.
   2. Con el flag y sin fallos: mismos `eta`/`T1`, **mismo número de llamadas al backend** que sin el flag, `reintento_usado == False`.
   3. Con el flag y el extremo alto (T ≥ cierto umbral) lanzando `PropertyRangeError`: converge, `reintento_usado == True`, y el `eta` coincide con el del caso sin fallos (tolerancia 1e-9 en el fake).
   4. Idem con el extremo bajo fallando; idem con ambos fallando pero un interior evaluable.
   5. Ambos extremos fallan en TODO el rango → `CicloNoConvergeError`, sin bucle infinito (el número de llamadas al backend está acotado por `2*max_repliegues + constante`; comprueba la cota con un contador).
   6. Sin cambio de signo de F en el rango evaluable → `CicloNoConvergeError`.
   7. Respeta `max_repliegues`: con tope 2 y un extremo que falla 3 veces seguidas → `CicloNoConvergeError`; con tope 3 → converge.
   8. `paso_repliegue` distinto de 5.0 se respeta (comprueba las T evaluadas).
   9. Una excepción distinta de `PropertyRangeError` (p. ej. `ValueError`) en un extremo se propaga sin reintento.
   10. Punto interior no evaluable durante `brentq` → `CicloNoConvergeError` con la T en el mensaje.
   11. Con `reintento_tolerante=True` el intento fallido del camino original no deja estado compartido: dos llamadas seguidas con los mismos datos dan el mismo resultado.
2. **`scripts/verificar_controles_reintento.py`** (nuevo, ≤200 líneas): verificación **lenta** con `TeqpVerificado`, fuera de la suite normal. Toma de `resultados/2026-09-30_arranque_solver/sonda_filas.csv` las 10 filas de control (grupos `ctl_*`) y 5 filas rescatadas (grupos `f2_T_from_Ph`, `lit_T_from_Ph`, `lit_bifasico`, 2/2/1) y compara, llamando a `resolver_ciclo(..., reintento_tolerante=True)`, `eta`/clasificación contra el CSV (`|Δη| < 1e-4`). Debe poder ejecutarse hoy y **fallar con un error claro de API** (argumento desconocido). Escribe una línea de progreso por fila en `resultados/2026-10-01_tests_reintento/progreso.log`.
3. **Demostrar que los tests miden algo:** ejecutar `pytest tests/test_reintento_tolerante.py` ahora y guardar la salida: deben fallar los 11 casos por la API inexistente (TypeError por argumento). El caso 1 (sin flag) puede pasar; indícalo. Después ejecutar la suite completa **sin** el archivo nuevo y reportar el conteo base (passed/skipped/xfailed/failed) como línea base para la rama.
4. Verificar que el fake de los tests reproduce los fallos del caso real: el fallo del extremo debe ocurrir en la **primera evaluación de F** (como en los datos reales: 37 de 40 fallos en un extremo).

## Constraints

- **No modificar `src/`** ni tests existentes. Archivos nuevos solo: `tests/test_reintento_tolerante.py`, `scripts/verificar_controles_reintento.py`, `resultados/2026-10-01_tests_reintento/` (salida de pytest, línea base, reporte). Nada en la raíz del repo.
- No agregar dependencias. Python del venv (`.venv\Scripts\python`).
- Cada archivo ≤200 líneas. Sin credenciales; sin leer fuera del proyecto.
- No implementes el reintento "para que pasen": los tests deben quedar en rojo.

## Outputs

- Los dos archivos nuevos, `resultados/2026-10-01_tests_reintento/pytest_rojo.txt` (salida actual), `linea_base_suite.txt` (suite sin el archivo nuevo) y `REPORTE_TESTS_PRIMERO.md` (formato: La pregunta · Qué se especificó · Qué se probó (tabla de los 11 casos y su resultado hoy) · Línea base · Lo que no sabemos · Qué sigue; lenguaje llano).
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- 11 casos escritos; hoy fallan por la causa esperada (API), no por errores de sintaxis del fake o de importación.
- Línea base de la suite registrada.
- Script lento de controles ejecutable y fallando con error de API claro.
- `git status` muestra solo los archivos permitidos.

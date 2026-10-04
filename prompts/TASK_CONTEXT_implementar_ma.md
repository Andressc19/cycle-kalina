---
project: ciclo_kalina_tercero
task_id: 2026-10-02-implementar-ma
delegated_to: executor
created: 2026-10-02
---

# TASK_CONTEXT — Implementar el bracket tolerante MA en `src/` (pasos 1 y 2: implementar y verificar)

## Task ID

2026-10-02-implementar-ma

## Project

`ciclo_kalina_tercero`, **worktree** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\solver-bracket`, rama `fix/solver-bracket-tolerante` (commit base `2de6050`). **Trabaja SOLO dentro de este worktree** (es tu directorio actual). El checkout principal `D:\Desktop\ciclo_kalina_tercero` lo usa otra sesión: no escribas ni ejecutes nada allí. El venv vive en el checkout principal: usa siempre `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` **con el directorio actual = el worktree** (así `src` se importa desde el worktree). Los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes.

## Contrato (no se discute)

- **Especificación:** `prompts/TASK_CONTEXT_tests_ma.md`, sección "Especificación de la API". Léela entera.
- **Tests:** `tests/test_bracket_tolerante.py` (16 tests). **No los modifiques.** Si un test te parece incorrecto, repórtalo en UNRESOLVED con la evidencia y deja ese test en rojo; no lo "arregles".
- Convenciones confirmadas por el director: `nF` = evaluaciones de F sin contar la evaluación final con T1 ya resuelto; el presupuesto se comprueba entre evaluaciones (el rebasamiento mínimo es una evaluación completa).
- Referencia de comportamiento (NO importar desde `src/`): `scripts/sonda_arranque_solver.py` (`_bracket_tol`, `F_seguro`, variante V2 de `orquestar`) y el prototipo de la tarea anterior (`C:\Users\Usuario\AppData\Local\Temp\opencode\proto_ma.py`, que pasó los 16 tests; puedes leerlo, no copiarlo a ciegas).

## Objective

### Paso 1 — Implementar
1. `src/cycle_solver.py`: añadir a `resolver_ciclo` los parámetros `bracket_tolerante=False, paso_repliegue=5.0, max_repliegues=None, presupuesto_s=None` con la semántica de la especificación. Con `bracket_tolerante=False` el camino debe ser **exactamente** el actual (mismas llamadas, mismo resultado, mismas claves).
2. La lógica nueva (F_seguro, repliegue, error de punto interior, presupuesto con `time.perf_counter()` vía `import time`, diccionario `bracket`) va en un módulo nuevo `src/_bracket_tolerante.py` para respetar el límite de 200 líneas por archivo. `src/_cycle_loops.py` solo se toca si es imprescindible (`evaluar` ya acepta `T10_inicial`).
3. Patrón adapter: los módulos del solver no importan backends concretos (ni `iapws`, ni `teqp`, ni `_kalina_flash`/`_nh3h2o_engine`). Solo `PropertyRangeError` desde `src.properties.adapter`.
4. Actualizar el docstring de `resolver_ciclo` (parámetros nuevos, en el estilo actual del archivo). No tocar UI (`app.py`, `ui_*.py`), ni `sensitivity.py`, ni otros módulos.

### Paso 2 — Verificar
1. `pytest tests/test_bracket_tolerante.py -v` → **16 passed**. Guardar la salida en `resultados/2026-10-02_implementar_ma/pytest_ma.txt`.
2. **Suite completa** (≈11 min): lanzarla desacoplada (`nohup ... > resultados/2026-10-02_implementar_ma/suite.txt 2>&1 &`) y seguirla con consultas cortas. Esperado: **198 passed, 1 skipped, 8 xfailed** (línea base 182/1/8 + 16 nuevos). Cualquier test que antes pasaba y ahora falla es una regresión: repórtala con detalle.
3. **Controles con motor real:** `scripts/verificar_controles_ma.py` completo (18 filas, `TeqpVerificado`), desacoplado, con su `progreso.log` (lo escribe en `resultados/2026-10-02_tests_ma/progreso.log`; si puedes redirigirlo a `resultados/2026-10-02_implementar_ma/` sin modificar el script, mejor; si no, déjalo). Esperado: **18/18 OK** (`|Δη| < 1e-4` y misma clasificación que V2). Si alguna fila falla, repórtala con su diferencia y causa; no ajustes tolerancias.
4. Medir y reportar el **tiempo por fila** de los controles (sanas y rescatadas por separado) y comparar con lo medido antes (filas sanas ~46 s, rescatadas ~60–220 s, con 6 workers).
5. Ejecución de la suite y de los controles **en secuencia** (no a la vez: los tiempos se contaminan).

## Constraints

- Archivos que puedes modificar/crear: `src/cycle_solver.py`, `src/_bracket_tolerante.py` (nuevo), y solo si es imprescindible `src/_cycle_loops.py`; salidas en `resultados/2026-10-02_implementar_ma/`. Nada más. No edites tests ni scripts existentes.
- Cada archivo ≤ 200 líneas. Sin dependencias nuevas.
- **No hagas commits** ni `git checkout/switch/stash/reset` (el director revisa y commitea). Al final reporta `git status --short` y `git diff --stat`.
- Cálculos de más de ~1 minuto: desacoplados con `nohup` y seguidos con consultas de pocos segundos; nunca un comando de más de ~90 s en primer plano.
- No escribir credenciales; no leer fuera de `D:\Desktop\ciclo_kalina_tercero` salvo el prototipo en el temporal del usuario.

## Outputs

- Código en `src/`; `resultados/2026-10-02_implementar_ma/` con `pytest_ma.txt`, `suite.txt`, salida de los controles y `REPORTE_IMPLEMENTAR_MA.md` con el formato, en lenguaje llano: **La pregunta · Qué se cambió (en simple) · Cómo se verificó · Resultados (tablas: tests, suite, 18 controles) · Tiempos · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- 16/16 tests de MA en verde sin tocarlos.
- Suite completa sin regresiones (198/1/8 esperado).
- 18/18 controles OK con motor real (o fallos reportados con causa).
- Sin flag, comportamiento idéntico al actual (lo garantiza el test 1 y la suite).

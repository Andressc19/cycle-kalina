---
project: ciclo_kalina_tercero
task_id: 2026-10-01-ablacion-arranque-y-tiempos
delegated_to: executor
created: 2026-10-01
---

# TASK_CONTEXT — Ablación (¿arranque o bracket?) y comportamiento de los tiempos (SIN tocar `src/`)

## Task ID

2026-10-01-ablacion-arranque-y-tiempos

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques. Esta tarea continúa `prompts/TASK_CONTEXT_arranque_solver.md`; sus resultados están en `resultados/2026-09-30_arranque_solver/` (`sonda_filas.csv`, 56 filas; `REPORTE_ARRANQUE_SOLVER.md`) y su script en `scripts/sonda_arranque_solver.py`. Reutiliza su muestra, su orquestación y sus parámetros por fila; no los rediseñes.

## Contexto

La sonda previa definió: V0 (solver actual), V1 (V0 + `T10_inicial = T_sumidero+5 K`), V2 (V1 + bracket tolerante con repliegue de 5 K). V2 rescató 28 de 40 fallas de V0, pero **V2 incluye V1**, así que no aísla el aporte del bracket tolerante. Además V2 costó ~5.5x (mediana 92.5 s vs 16.6 s de V0). El director necesita (a) saber qué cambio es el que de verdad ayuda, y (b) entender y reducir el coste, antes de tocar `src/`.

## Objective

Ampliar la sonda (nuevo script `scripts/sonda_ablacion_tiempos.py`, ≤200 líneas, importando lo que haga falta de `scripts/sonda_arranque_solver.py` sin modificarlo) con estas variantes, sobre las MISMAS 56 filas:

- **VB:** V0 + SOLO bracket tolerante (arranque original `T10_inicial=None` en la primera evaluación; repliegue de 5 K como en V2). Aísla el aporte del bracket.
- **VC:** V0 + SOLO arranque (es V1; NO la recalcules: toma sus columnas del CSV existente).
- **V3:** V1 + bracket tolerante con **repliegue por bisección**: si un extremo no se evalúa, probar el punto medio entre ese extremo y el extremo opuesto (o el último punto evaluable), y avanzar hacia el interior reduciendo a la mitad la distancia, con un máximo de 6 intentos por extremo. Objetivo: igual tasa de rescate que V2 con menos evaluaciones de F.
- V0 y V2 se toman del CSV existente (no se recalculan), salvo que necesites re-medir tiempos en la misma carga; en ese caso, repórtalo.

Para VB y V3, y para V0/V1/V2 desde el CSV, producir por fila: `convergio`, `clasificacion`, `eta`, `nF` (número de evaluaciones de F), `iter_lazo_frio_total` (suma de iteraciones del lazo frío en todas las evaluaciones), `t_s`, y `t_por_F = t_s/nF`. Si V0/V1/V2 del CSV no traen `nF` ni iteraciones, instrumenta una corrida de referencia con el mismo `Proxy`/contador de la sonda previa para esas filas y repórtalo.

## Análisis a reportar (en `REPORTE_ABLACION_TIEMPOS.md`)

1. **Tabla de ablación:** por grupo (FASE2 T_from_Ph, FASE2 h(P,s,x), Literatura T_from_Ph, Literatura bifásico), cuántas de las 40 filas que V0 no resuelve rescata cada variante: VC (solo arranque), VB (solo bracket), V2 (ambos), V3. Indica explícitamente la conclusión: ¿el arranque aporta algo por sí mismo, algo solo en combinación, o nada?
2. **Tiempos:** media, mediana y p90 de `t_s`, `nF`, `iter_lazo_frio_total` y `t_por_F` por variante y por estado (filas convergidas / no convergidas). Responder: ¿el sobrecoste de V2 viene de más evaluaciones de F (nF), de más iteraciones por evaluación, o de evaluaciones individuales más caras?
3. **Efecto del arranque en iteraciones:** en las filas que convergen con V0 y con V1, comparar `iter_lazo_frio_total` y `t_s` (¿el arranque físico acelera?). Controles: las 10 filas de control deben dar el mismo η que el CSV original (|Δη| < 1e-4).
4. **Costo/beneficio:** para cada variante, filas rescatadas por cada 1000 s de cómputo.
5. **Filas no rescatadas por ninguna variante:** listarlas con la causa (`NoBracket` sin cambio de signo, sin extremos evaluables, `PuntoNoEvaluable`) para decidir si son "sin solución" o "recuperables con otra estrategia". No inventes una estrategia nueva; solo clasifica.

## Constraints

- **No modificar** `src/`, `tests/`, ni scripts/CSV existentes.
- Backend: `TeqpVerificado` (como la sonda previa). Las filas rescatadas que salgan KALINA se verifican con `verificar_turbina` y un `AmmoniaWaterAdapter`; las `CORREGIBLE` rescatadas NO se verifican con el motor real: dilo en el reporte.
- 6 workers como la sonda previa; reporta tiempo de pared. Si excede ~90 min, reduce a la mitad de la muestra conservando el reparto por grupo y repórtalo.
- Archivos nuevos solo en `scripts/` y `resultados/2026-10-01_ablacion_tiempos/` (`ablacion_filas.csv`, `REPORTE_ABLACION_TIEMPOS.md`).
- No escribir credenciales ni leer fuera de `D:\Desktop\ciclo_kalina_tercero`.
- Recalcula todas las cifras del reporte directamente desde el CSV generado y verifica que las tablas suman los totales (en la tarea previa el primer borrador tuvo sumas inconsistentes).

## Done criteria

- Ablación completa sobre las 40 filas que V0 no resuelve, con VC, VB, V2 y V3 comparables fila a fila.
- Tiempos con `nF`, iteraciones y `t_por_F` por variante.
- Controles sin regresión.
- Conclusión explícita y numérica de "qué cambio ayuda" y "de dónde viene el coste". No decidir si se cambia `src/`: eso lo decide el director.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

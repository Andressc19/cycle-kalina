---
project: ciclo_kalina_tercero
task_id: 2026-09-20-actualizar-rangos-fase2-fase3
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Determinar (NO ejecutar el barrido final) los nuevos rangos de Fase 2 y Fase 3

## Task ID

2026-09-20-actualizar-rangos-fase2-fase3

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente` (aquí ya vive
`T_amb_diseno`, el nuevo parámetro configurable de `evaluar_ciclo`/`verificar_operativos`,
ver `src/restricciones/operativos.py` y `src/restricciones/clasificacion.py` — YA
IMPLEMENTADO Y CON TESTS EN VERDE en esta rama, NO lo toques, solo úsalo). **Esta tarea es
de EXPLORACIÓN/DETERMINACIÓN DE VALORES, no de ejecución del barrido final** — el objetivo
es dejar los rangos y candidatos bien justificados por escrito para que el director decida
antes de correr el análisis de sensibilidad completo (eso viene después, con autorización
aparte).

## Contexto que ya tenemos (no lo repitas, parte de aquí)

1. **El criterio O2 (cavitación de bomba) ya NO está atado a un piso fijo de 303.55 K
   (30.4°C).** Ahora `evaluar_ciclo(..., T_amb_diseno=<lo que quieras>)` — default 303.55 K
   si no lo pasas (retrocompatible), pero se puede bajar a cualquier valor realista del caso.
   El criterio sigue siendo `T_amb_evaluar = max(T_sumidero, T_amb_diseno)`.
2. **Fase 2 (libre, base del profesor)**: con `T_amb_diseno` fijo en el viejo 303.55 K, ya
   se encontró un punto KALINA subiendo `P_baja` a 450 kPa y `eps_cond` a 0.99 (ver
   `resultados/barridos_2026-09-19/fase2_libre/`). El director consideró ese `eps_cond=0.99`
   poco realista y pidió explorar TAMBIÉN `x_b` más bajo (0.35-0.50, nunca probado) cruzado
   con `P_baja` 400-600 kPa y `eps_cond` 0.80-0.95 (rango razonable). **Ahora, además, hay
   que sumar `T_amb_diseno` como palanca**: el 30.4°C viene de la tabla del profesor
   (clima tropical); si se justifica un piso más bajo y realista para ESTE caso, se puede
   usar en vez de 303.55 K — pero decide tú si hay justificación para cambiarlo en el caso
   del profesor (su propia tabla SÍ llega a 30.4°C en la hora 17, así que ahí probablemente
   NO se deba bajar sin más — analízalo, no lo asumas).
3. **Fase 3 (Húsavík, caso real)**: con `T_amb_diseno=303.55 K` (heredado, pero
   FÍSICAMENTE INCORRECTO para Islandia — nunca hace 30.4°C en Húsavík), se necesitó
   `P_baja=1200 kPa` (pinch de condensador ~9 K) para pasar O2. El director ya señaló que un
   piso realista para Islandia sería mucho más bajo (~10°C = 283.15 K, un margen conservador
   razonable sobre los 5°C de diseño del caso real, no una media). **Repite la búsqueda de
   base con `T_amb_diseno` realista para Islandia en vez de 303.55 K**, y compara el `P_baja`
   mínimo necesario y el pinch resultante contra el resultado viejo (1200 kPa, pinch ~9K) —
   se espera que baje sustancialmente, posiblemente cerca del mínimo de condensación ya
   calibrado (~468 kPa, pinch ~3K).

## Objective

Para CADA una de las dos fases (Fase 2 libre, Fase 3 Húsavík), determinar y dejar
documentado por escrito (NO es un barrido de sensibilidad final, es la etapa previa de
"encontrar y justificar los rangos/candidatos"):

1. Un candidato base que clasifique `KALINA` usando rangos MÁS realistas que los usados
   hasta ahora (para fase 2: `x_b` más bajo en vez de `eps_cond` extremo; para fase 3:
   `T_amb_diseno` realista de Islandia en vez del piso tropical heredado).
2. El rango completo de 3-5 variables (con sus límites concretos) que se usarían para el
   análisis de sensibilidad posterior alrededor de ese candidato — la ENTREGA de esta tarea
   es la tabla de rangos, no las corridas de sensibilidad en sí (esas van después, con
   autorización aparte).
3. Comparación explícita: cuánto mejoró (o no) el punto KALINA al usar `T_amb_diseno`
   realista en vez del default heredado — esto es el resultado más importante a reportar.

## Approach

### Fase 2 (libre) — trabaja en `scripts/barridos_2026-09-19/fase2_libre/` (NO borres lo
que ya hay ahí, añade archivos nuevos con sufijo `_v2`)

1. Con `TeqpAdapter`, escanea `x_b` de 0.35 a 0.50 (paso 0.05) cruzado con `P_baja` 400-600
   kPa (paso 50) y `eps_cond` 0.80-0.95 (paso 0.05), sobre la base del profesor
   (`P_alta=3000, T_fuente=470.0` — el que SÍ converge, ver `CONTEXT.md` — `T_sumidero=
   300.032917`, resto de eficiencias/efectividades en default de `CONTEXT.md`), con
   `T_amb_diseno=303.55` (default, es el caso del profesor, su propia tabla real llega a
   30.4°C — no hay justificación para bajarlo aquí, documenta por qué NO lo tocas en este
   caso).
2. Encuentra el mejor candidato KALINA de ese barrido (el de mayor η con efectividades
   razonables, no forzadas a los extremos de `CAMPOS_CICLO`).
3. Guarda el CSV como `busqueda_libre_v2.csv` y un resumen corto en `BASE_LIBRE_v2.md`
   (mismo formato que el `BASE_LIBRE.md` que ya existe, pero compáralo explícitamente con el
   candidato viejo de `BASE_LIBRE.md`).
4. Propón la tabla de rangos de 3-5 variables para el análisis de sensibilidad posterior
   alrededor de este nuevo candidato (con su justificación).

### Fase 3 (Húsavík) — trabaja en `scripts/barridos_2026-09-19/fase3_real/` (NO borres lo
que ya hay, añade archivos nuevos con sufijo `_v2`)

1. Repite la calibración de `P_baja` (regla `bubble_point(P_baja, x_b=0.82) = T_sumidero +
   3 K`, ya usada antes — no la cambies) pero esta vez evaluando O2 con `T_amb_diseno=
   283.15 K` (10°C, margen conservador razonable sobre los 5°C reales de Húsavík — decisión
   ya tomada por el director, no inventes otro valor sin justificarlo).
2. Con `TeqpAdapter`, escanea `P_baja` de forma fina entre el mínimo calibrado (~468 kPa) y
   1200 kPa (el valor viejo), buscando el `P_baja` MÍNIMO que ya pase O2 con
   `T_amb_diseno=283.15` — ese es el candidato de menor pinch. Base: `P_alta=3300, x_b=0.82,
   T_fuente=394.15, T_sumidero=278.15`, resto de eficiencias/efectividades en los valores ya
   usados (`eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.95, eps_cond=0.95` — o
   documenta si con el nuevo `T_amb_diseno` ya no hace falta forzar `eps_reg`/`eps_cond` tan
   altos, sería una mejora adicional a reportar).
3. Confirma el mejor candidato con el motor real (`AmmoniaWaterAdapter`, 1 punto).
4. Guarda el CSV como `busqueda_husavik_v2.csv`, la confirmación en
   `confirmacion_motor_real_v2.json`, y el resumen en `CASO_HUSAVIK_v2.md` — compara
   explícitamente el `P_baja` y el pinch nuevo contra el viejo (1200 kPa, ~9K).
5. Propón la tabla de rangos de 3-5 variables para el análisis de sensibilidad posterior
   alrededor de este nuevo candidato (con su justificación).

## Files

Todo lo nuevo en `scripts/barridos_2026-09-19/fase2_libre/` y
`scripts/barridos_2026-09-19/fase3_real/` (archivos con sufijo `_v2`, no borres ni
sobrescribas los que ya existen — son historial de la iteración anterior, útil para
comparar). Resultados en `resultados/barridos_2026-09-19/fase2_libre/` y
`resultados/barridos_2026-09-19/fase3_real/`, mismo criterio de sufijo `_v2`.

**NO modifiques**: nada de `src/` (incluido `src/restricciones/operativos.py` y
`clasificacion.py`, que ya están bien como están en esta rama), `TASK_CONTEXT.md` (es de
otra tarea, ya cerrada), `TASK_CONTEXT_fase1_profesor.md` (Fase 1 no cambia: su propio
T_amb_diseno de 30.4°C es correcto, es su propio clima).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Usa `TeqpAdapter` para explorar, motor real solo para 1-2 confirmaciones por fase.
3. Tope: ~150 puntos por fase con `TeqpAdapter`.
4. Esta tarea NO corre el análisis de sensibilidad completo — solo determina y justifica el
   candidato base y la tabla de rangos propuestos. Déjalo muy claro en el reporte final para
   que no se confunda con el barrido de sensibilidad definitivo (ese requiere autorización
   aparte del director).

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: los 2 candidatos nuevos (Fase 2 v2, Fase 3 v2) con su
comparación explícita contra los candidatos viejos, y las 2 tablas de rangos propuestos
para el análisis de sensibilidad posterior.

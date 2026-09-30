---
project: ciclo_kalina_tercero
task_id: 2026-09-20-fase2-prescan-eps-hrvg
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Fase 2: pre-escaneo de `eps_hrvg` (cerrar el vacío detectado)

## Task ID

2026-09-20-fase2-prescan-eps-hrvg

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente`. **Corre en paralelo con
`TASK_CONTEXT_fase3_confirma_690.md` (otra sesión, trabaja solo en
`scripts/barridos_2026-09-19/fase3_real/`) — no la toques, no hay conflicto de archivos si
respetas tu carpeta.**

## Contexto

El candidato aprobado de Fase 2 es `P_alta=3000, P_baja=400, x_b=0.40, T_fuente=470.0,
T_sumidero=300.032917, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
T_amb_diseno=303.55` → KALINA, η=0.124296 (confirmado con motor real, ver
`resultados/barridos_2026-09-19/fase2_libre/BASE_LIBRE_v2.md`). La tabla de rangos propuesta
para el barrido de sensibilidad posterior incluye `eps_hrvg: 0.80–0.90` (centro 0.85), pero
**esa variable nunca se barrió ni siquiera en exploración gruesa** — el rango es una
suposición, no evidencia. Objetivo de esta tarea: cerrar ese vacío antes de comprometer la
resolución final del barrido.

## Objective

1. Con `TeqpAdapter`, escanea `eps_hrvg` de 0.70 a 0.95 (paso 0.05, 6 puntos) sobre el
   candidato base de Fase 2 (arriba), resto de variables fijas en sus valores del candidato.
2. Determina si en ese rango el punto se mantiene KALINA, cruza a otra clasificación (p.ej.
   O5 por q2 fuera de banda, o algún otro criterio), o es plano (sin cambio de
   clasificación).
3. Si el rango 0.80-0.90 propuesto originalmente resulta ADECUADO (cruza o se acerca a una
   frontera dentro de ese rango, o confirma que es representativo), dilo así. Si resulta
   INADECUADO (todo el rango da KALINA sin acercarse a ningún borde, o al revés, todo falla),
   PROPÓN un rango corregido con la misma lógica que las demás variables de la tabla
   (debe bracketing la frontera de clasificación si existe una en `CAMPOS_CICLO` [0.05,0.99]
   dentro de un entorno razonable del candidato).
4. Registra todos los puntos (converjan o no) en
   `resultados/barridos_2026-09-19/fase2_libre/prescan_eps_hrvg.csv` (esquema `tabla_barrido`).
5. Escribe un resumen corto (10-20 líneas) en
   `resultados/barridos_2026-09-19/fase2_libre/PRESCAN_EPS_HRVG.md`: qué se encontró y el
   rango final recomendado para `eps_hrvg` en la tabla de sensibilidad de Fase 2 (actualiza
   la fila correspondiente de la tabla de rangos que ya existe en `BASE_LIBRE_v2.md` §3, sin
   borrar el resto del documento — solo edítalo para corregir esa fila si hace falta, con una
   nota de por qué cambió).

## Files

Todo nuevo en `scripts/barridos_2026-09-19/fase2_libre/` (sufijo `prescan_eps_hrvg`) y
`resultados/barridos_2026-09-19/fase2_libre/`. Puedes editar
`resultados/barridos_2026-09-19/fase2_libre/BASE_LIBRE_v2.md` SOLO para actualizar la fila de
`eps_hrvg` en la tabla de rangos (§3), nada más de ese archivo.

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni `scripts/barridos_2026-09-19/fase3_real/`
ni `scripts/barridos_2026-09-19/fase1_profesor/` (tareas ajenas/paralelas).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Solo `TeqpAdapter` — no hace falta motor real para un pre-escaneo de 6 puntos.
3. No inventes límites nuevos de `CAMPOS_CICLO`; el rango de `eps_hrvg` corregido debe caer
   dentro de [0.05, 0.99].

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: los 6 puntos y el rango final recomendado.

---
project: ciclo_kalina_tercero
task_id: 2026-09-24-grafica-tendencias
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — Rehacer la gráfica de validación por tendencias (sin recalcular nada)

## Task ID

2026-09-24-grafica-tendencias

## Contexto

La tarea `2026-09-24-validacion-tendencias-embaye` (`opencode_run_024.log`) produjo
`resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv` (33 filas, correcto) y
una gráfica `comparacion_tendencias.png` que Claude **rechazó en auditoría**: cada punto del
modelo tiene un color distinto (no un color por serie), así que no se sabe a qué curva del paper
pertenece cada punto. Además el reporte dice `n=25` comparables, pero con su propio criterio
(motor = teqp, convergió, η_paper disponible, título salida turbina ≥ 0.90) son **23**
(recalculado por Claude: Δ medio −0.061 pp, |Δ| medio 0.275 pp, |Δ| máx 1.159 pp, mediana
|Δ rel| 2.37 %); los 2 puntos AmmoniaWater son control del motor, no se suman.

**No se corre el ciclo. Solo se leen CSV existentes.**

## Objective

Crear `scripts/grafica_validacion_tendencias.py` (nuevo, ≤ 150 líneas, matplotlib) que lea:
- `resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`
- `resultados/2026-09-24_embaye_vectorial/curvas_embaye_eta_vs_xb.csv`
- `resultados/2026-09-24_embaye_vectorial/curvas_embaye_fig7.csv`

y genere `resultados/2026-09-24_validacion_tendencias/comparacion_tendencias_v2.png`
(dpi 200) con **4 paneles** (2×2):

1. **Fig. 7 — η vs P_alta [bar], T_fuente 373 K**: líneas del paper x_b=0.55 y x_b=0.66;
   puntos del modelo (teqp) del **mismo color que su serie**, marcador círculo; los 2 puntos
   AmmoniaWater como marcador "x" negro (etiqueta "control motor iapws").
2. **Fig. 3 — η vs x_b, 15 bar**: líneas del paper 333/373/423 K; puntos del modelo del color de
   su T_fuente. Puntos que convergieron pero sin título computable (333 K x_b 0.75/0.85):
   marcador hueco (sin relleno) y nota en la leyenda "no comparable (título no calculado)".
3. **Fig. 2 (10 bar, 373 K) y Fig. 5 (32 bar, 423 y 463 K)** en un mismo panel η vs x_b:
   líneas del paper y puntos del modelo por color de serie (usa línea continua para 10 bar y
   discontinua para 32 bar, y dilo en la leyenda).
4. **Paridad**: η_modelo vs η_paper de los 23 puntos comparables, línea y = x y bandas ±0.5 pp;
   colorear por serie; anotar en el panel n=23, Δ medio, |Δ| medio, |Δ| máx.

Puntos que NO convergieron: no se dibujan (y así se indica en una nota al pie de la figura:
"6 de 33 puntos no convergieron; ver CSV").

Ejes con unidades; títulos por panel; P en **bar** (P_alta_kPa/100). Leyendas que no tapen datos.

Además, **editar solo** `resultados/2026-09-24_validacion_tendencias/REPORTE_VALIDACION_TENDENCIAS.md`
para: (a) corregir la estadística global a n=23 con los valores de arriba (recalcúlalos del CSV
en el script e imprímelos; si difieren de los de Claude en más de 0.001, repórtalo en
UNRESOLVED); (b) aclarar que los 2 puntos AmmoniaWater son control de motor y no se suman;
(c) referenciar `comparacion_tendencias_v2.png` en lugar de la anterior. No borres
`comparacion_tendencias.png`.

## Constraints

- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero`** (ni temporales).
- No modificar ningún otro archivo. No correr el ciclo.
- No puedes ver imágenes: verifica la figura por código (número de series/puntos dibujados por
  panel, impresos en consola) y reporta esos conteos.

## Acceptance criteria

1. `comparacion_tendencias_v2.png` con los 4 paneles.
2. Reporte corregido (n=23).
3. RESULTS: estadística recalculada y conteo de puntos por panel/serie.

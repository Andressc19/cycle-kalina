---
project: ciclo_kalina_tercero
task_id: 2026-09-24-rama-fisica-22-kalina
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — Comprobar con el motor real la salida isentrópica de turbina de los 22 KALINA

## Task ID

2026-09-24-rama-fisica-22-kalina

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. La tarea anterior
(`resultados/2026-09-24_rama_turbina/REPORTE_RAMA_TURBINA.md`) demostró que
`TeqpAdapter` puede devolver una salida isentrópica de turbina falsa
(`h4s = backend.h(P_baja, s=s3, x=x3)`, `src/components/turbina.py:35`): el flash
de teqp da un estado espurio en el punto de burbuja, `s(T)` deja de ser creciente y
la inversión cae en una raíz no física en franjas de `P_baja` de ~5 kPa. La prueba
de estabilidad ±0.5 kPa no detecta un punto que esté entero dentro de una franja.
Esta tarea comprueba directamente, con el motor real, si cada uno de los 22 KALINA
de `resultados/2026-09-24_margen2k/barrido_margen2k.csv` está en la rama física.
Sospechoso principal: `(x_b=0.65, P_alta=5000, T_fuente=394)` con η=0.009.

**Nota:** `TASK_CONTEXT.md` y los demás `TASK_CONTEXT_*.md` de la raíz son OTRAS
tareas: no los ejecutes ni los modifiques. Tu tarea es solo este archivo.

## Objective

Script `scripts/rama_fisica_22_kalina.py` (nuevo).

1. Para cada fila con `clasificacion == KALINA` en `barrido_margen2k.csv` (22
   filas), con su `P_baja = P*` y los parámetros del barrido (efectividades fijas
   0.85/0.80/0.85, `T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`):
   - Resolver el ciclo con `TeqpAdapter(x=x_b)` en `P*`. Guardar `s3`, `x3`, `h3`,
     `T3`, `h4`, `T4`, η, Wnet, y `h4s_teqp = backend.h(P*, s=s3, x=x3)`,
     `T4s_teqp = backend.T_from_Ps(P*, s3, x3)`.
   - Con `AmmoniaWaterAdapter(x=x_b)`: `h4s_real = h(P*, s=s3, x=x3)` y
     `T4s_real = T_from_Ps(P*, s3, x3)` (mismos `s3`, `x3` de teqp). Registrar el
     tiempo. Capturar excepciones.
   - `dh4s = h4s_teqp − h4s_real`, `dT4s = T4s_teqp − T4s_real`.
   - `rama_fisica = True` si `|dh4s| ≤ 2.0` kJ/kg y `|dT4s| ≤ 0.5` K; si no,
     `False`. Si el motor real falla, `rama_fisica = "no evaluable"` con el error.
   - Registrar también la fase que reporta teqp para el estado `(P*, T4s_teqp,
     x3)` (`backend.fase_de`), para ver si coincide con lo esperado.
2. Para los puntos con `rama_fisica = False` (si hay), y **solo si son 3 o menos**:
   resolver el ciclo completo con `AmmoniaWaterAdapter` en el mismo `P*` y
   registrar η, Wnet, margen O2 (calculado como en
   `src/restricciones/operativos.py`: condensador re-resuelto a
   `T_sumidero=283.15`, `T_bur = bubble_point(P*, x_b)`) y clasificación con
   `evaluar_ciclo(..., T_amb_diseno=283.15)`. Si son más de 3, no corras ciclos
   con motor real; solo lístalos.
3. CSV `resultados/2026-09-24_rama_22/rama_fisica_22.csv` con una fila por punto.
4. Reporte `resultados/2026-09-24_rama_22/REPORTE_RAMA_22.md`:
   - Tabla de los 22: x_b, P_alta, T_fuente, P*, η_teqp, h4s_teqp, h4s_real, dh4s,
     T4s_teqp, T4s_real, dT4s, rama_fisica.
   - Cuántos están en la rama física y cuáles no.
   - Para los no físicos corridos con motor real: η y clasificación reales vs teqp.
   - Lista final de **KALINA confirmados en rama física**, ordenada por η.

## Files

Crear:
- `scripts/rama_fisica_22_kalina.py`
- `resultados/2026-09-24_rama_22/rama_fisica_22.csv`
- `resultados/2026-09-24_rama_22/REPORTE_RAMA_22.md`
- `resultados/2026-09-24_rama_22/run.log`

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni ningún
`TASK_CONTEXT*.md`).

## Constraints

- Motor real: solo las 22 parejas de llamadas `h`/`T_from_Ps` y, como máximo, 3
  ciclos completos (paso 2).
- Capturar excepciones por punto; nunca abortar ni ocultar.
- `python -u`, salida a `run.log`.
- `.py` nuevo ≤ 250 líneas.
- Umbrales fijos: 2.0 kJ/kg y 0.5 K. No los cambies.

## Acceptance criteria

1. CSV con 22 filas y `rama_fisica` evaluada (o error real).
2. Reporte con la tabla, el conteo y la lista de KALINA confirmados en rama física.
3. RESULTS incluye el conteo, la lista final y las rutas.

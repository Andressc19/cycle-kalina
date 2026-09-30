---
project: ciclo_kalina_tercero
task_id: 2026-09-24-rama-turbina-y-estabilidad
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — (1) Cuál rama de la salida de turbina es la física y (2) estabilidad de los 22 KALINA

## Task ID

2026-09-24-rama-turbina-y-estabilidad

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. La tarea anterior
(`resultados/2026-09-24_verificacion/REPORTE_VERIFICACION.md`, Parte B) mostró que
en `(x_b=0.60, P_alta=4000, T_fuente=394)`, con efectividades fijas
0.85/0.80/0.85, el estado de salida de turbina calculado con `TeqpAdapter` salta
entre dos ramas al mover `P_baja` 0.25 kPa cerca de 424 kPa: con el mismo estado 3
(h3≈1794.71 kJ/kg, x3≈0.97496), h4 pasa 1659.49 ↔ 1547.74 kJ/kg, T4 313.94 ↔
290.41 K, η 0.034 ↔ 0.080. F(T1) tiene una sola raíz: el salto está en la
expansión isentrópica de `src/components/turbina.py`
(`h4s = backend.h(P_salida, s=s3, x=x3)`). Solo una rama puede ser física.

**Nota:** `TASK_CONTEXT.md` y los demás `TASK_CONTEXT_*.md` de la raíz son OTRAS
tareas: no los ejecutes ni los modifiques. Tu tarea es solo este archivo.

Haz la Parte 1 y luego la Parte 2.

## Parte 1 — Qué rama es la física

Script `scripts/diagnostico_rama_turbina.py`.

1. Con `TeqpAdapter(x=0.60)`, resolver el ciclo (efectividades 0.85/0.80/0.85,
   `P_alta=4000`, `T_fuente=394`, `T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`) en
   `P_baja = 423.914831` y `P_baja = 424.169832` (valores de
   `resultados/2026-09-24_margen2k/evaluaciones_margen.csv`). Guardar de cada uno:
   `s3`, `x3`, `h3`, `h4s` (= `backend.h(P_baja, s=s3, x=x3)`), `h4`, `T4`.
2. Barrido de la expansión isentrópica aislada con teqp: con `s3` y `x3` de la
   solución a `P_baja=424.169832`, evaluar `h(P, s=s3, x=x3)` y `T_from_Ps(P, s3,
   x3)` para `P` de 419.0 a 429.0 kPa cada 0.25 kPa. Registrar dónde salta.
3. Monotonía de `s(T)` con teqp a `P = 424.0` kPa y `x = x3`: evaluar
   `backend.s(P, T=T, x=x3)` de 250 a 350 K cada 0.5 K. ¿Es `s(T)` estrictamente
   creciente? Si no, indicar los T donde no lo es: eso explicaría dos raíces en la
   inversión `T_from_Ps`.
4. Referencia con el motor real: con `AmmoniaWaterAdapter(x=0.60)` evaluar
   `h(P, s=s3, x=x3)` y `T_from_Ps(P, s3, x3)` en `P ∈ {420.0, 422.0, 424.169832}`
   (mismos `s3`, `x3`). Son 3 llamadas; captura excepciones y registra el tiempo.
5. Veredicto: comparar las dos ramas de teqp con el motor real. La rama que
   coincide (±2 kJ/kg en h, ±0.5 K en T) es la física; la otra es artefacto de
   teqp. Si el motor real no coincide con ninguna, decirlo.
6. **No modificar `src/`.** Si identificas la causa en el código (p. ej. el
   bracket o el brentq de `TeqpAdapter._T_de` / la inversión por `s`), describirla
   con archivo:línea en RECOMMENDATIONS, sin aplicarla.

Salidas: `resultados/2026-09-24_rama_turbina/expansion_P.csv`,
`s_de_T.csv`, `motor_real.csv`, sección 1 del reporte.

## Parte 2 — Estabilidad de los 22 KALINA de `barrido_margen2k.csv`

Script `scripts/estabilidad_kalina_margen2k.py`. Solo `TeqpAdapter`.

Para cada fila con `clasificacion == KALINA` en
`resultados/2026-09-24_margen2k/barrido_margen2k.csv`, con su `P_baja = P*` y los
mismos parámetros (efectividades 0.85/0.80/0.85, `T_sumidero=283`,
`eta_t=eta_p=0.80`, `m_b=1`, `T_amb_diseno=283.15`):
- resolver en `P* − 0.5`, `P*` y `P* + 0.5` kPa;
- registrar en cada uno η, Wnet, h4, T4, margen O2 (calculado como en
  `src/restricciones/operativos.py`) y clasificación;
- marcar `estable = False` si entre los tres valores |Δη| > 0.01 o |Δh4| > 10 kJ/kg
  o cambia la clasificación; si no, `estable = True`.
- Captura excepciones por evaluación; nunca abortar ni ocultar.

Salida: `resultados/2026-09-24_rama_turbina/estabilidad_kalina.csv` y sección 2 del
reporte con la lista de KALINA estables e inestables.

## Reporte

`resultados/2026-09-24_rama_turbina/REPORTE_RAMA_TURBINA.md`: secciones 1 y 2, con
tablas y veredictos. Honesto si algo no es concluyente.

## Files

Crear:
- `scripts/diagnostico_rama_turbina.py`
- `scripts/estabilidad_kalina_margen2k.py`
- `resultados/2026-09-24_rama_turbina/` con los CSV, `run_1.log`, `run_2.log` y el
  reporte.

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni ningún
`TASK_CONTEXT*.md`).

## Constraints

- Motor real solo en las 3 llamadas de la Parte 1, paso 4.
- Efectividades fijas 0.85/0.80/0.85.
- `python -u`, salida a los logs indicados.
- Cada `.py` nuevo ≤ 250 líneas.

## Acceptance criteria

1. Parte 1 con veredicto de cuál rama es la física, apoyado en el motor real.
2. Parte 2 con las 22 filas evaluadas y marcadas estable/inestable.
3. RESULTS incluye ambos veredictos y las rutas.

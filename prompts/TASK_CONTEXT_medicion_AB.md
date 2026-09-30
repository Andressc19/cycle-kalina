---
project: ciclo_kalina_tercero
task_id: 2026-09-27-medicion-tiempos-A-B
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Implementar B (verificación final) como prototipo y medir tiempos reales de teqp / A / B / A+B

## Task ID

2026-09-27-medicion-tiempos-A-B

## Project

Estás en el worktree
`D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\teqp-doble-verificacion` (rama
`fix/teqp-doble-verificacion`). Trabaja SOLO aquí. **No hagas commits.** Los demás
`TASK_CONTEXT*.md` son otras tareas: ignóralos.

Python: `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` con cwd en este
worktree. **Nunca escribas en `/tmp` ni fuera del worktree** (el sandbox lo bloquea
y aborta la ejecución): todos los logs van a `resultados/2026-09-27_medicion_AB/`.

Contexto: ya existe `src/properties/teqp_verificado.py` (opción **A**: `TeqpAdapter`
que consulta al motor real `AmmoniaWaterAdapter` solo en la zona de riesgo). Falta
**B**: una verificación final que, para un punto ya resuelto, recalcula con el motor
real la salida isentrópica de turbina y compara con la de teqp. La eficiencia de
cómputo es prioritaria: el objetivo de esta tarea es **medir tiempos reales** para
decidir.

Datos de calibración ya medidos (no hace falta volver a medirlos): en puntos normales
`h4s_teqp − h4s_real` = −0.7 a −1.6 kJ/kg; en el caso espurio (x_b=0.60,
P_alta=4000, T_fuente=394, P_baja=423.914831) teqp da h4s=1625.7 y el real 1486.7
(139 kJ/kg). Umbral de B: 2.0 kJ/kg.

## Objective

### 1. Prototipo de B: `src/verificacion_motor_real.py` (archivo nuevo, ≤ 120 líneas)

Función `verificar_turbina(resultado, *, P_baja, motor_real, umbral_kJkg=2.0,
backend_teqp=None) -> dict`:
- `resultado` es el dict de `resolver_ciclo` (usa `resultado["estados"]["e3"]` para
  `s3`, `x3`).
- `h4s_real = motor_real.h(P_baja, s=s3, x=x3)`.
- `h4s_teqp`: si se pasa `backend_teqp`, `backend_teqp.h(P_baja, s=s3, x=x3)`; si no,
  reconstruirlo sin llamar a ningún motor a partir de `e3.h`, `e4.h` y `eta_t`
  (`h4s = h3 − (h3 − h4)/eta_t`, que es la inversa exacta de
  `src/components/turbina.py`) — añade `eta_t` como argumento obligatorio si eliges
  esta vía. Elige la vía más barata que sea exacta y justifícala.
- Devuelve `dict(h4s_teqp, h4s_real, dh4s, verificado: bool (|dh4s| <= umbral),
  t_real_s, error)`. Si el motor real falla: `verificado=None`, `error` con el
  mensaje real; nunca inventar.
- No modificar ningún archivo existente.

Tests `tests/test_verificacion_motor_real.py`: detecta el caso espurio
(`verificado=False`, |dh4s| > 100) resolviendo con `TeqpAdapter`; pasa un punto
normal (`(0.65, 5000, 423, P_baja=704.644595)`, `verificado=True`).

### 2. Medición de tiempos: `scripts/medicion_tiempos_AB.py`

Puntos: los 22 KALINA de `resultados/2026-09-24_margen2k/barrido_margen2k.csv` (en su
`P_baja`) + el caso espurio (P_baja=423.914831). Parámetros: efectividades
0.85/0.80/0.85, `T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`,
`T_amb_diseno=283.15`.

Para cada punto, medir con `time.perf_counter` y registrar por separado:
- `t_teqp`: `resolver_ciclo` + `evaluar_ciclo` con `TeqpAdapter`;
- `t_A`: lo mismo con `TeqpVerificado` (y sus recurrencias);
- `t_B`: solo el costo de `verificar_turbina` sobre el resultado de `TeqpAdapter`
  (la parte de motor real);
- `t_AB`: `t_A` + `verificar_turbina` sobre el resultado de `TeqpVerificado`.
Usa **una sola instancia** de `AmmoniaWaterAdapter` por `x_b` para B (la creación
también se mide aparte, una vez, como `t_init_motor_real`).
Registrar también η y clasificación en cada modo, y `verificado`/`dh4s` de B.

Medir además, 5 veces cada una, el costo de `AmmoniaWaterAdapter.bubble_point(P_baja,
x_b)` en 5 puntos distintos (para decidir si B debe incluir el punto de burbuja de O2).

### 3. Reporte

`resultados/2026-09-27_medicion_AB/REPORTE_MEDICION_AB.md` con:
- Tabla por punto: t_teqp, t_A, t_B, t_AB, η, clasificación, dh4s, verificado.
- Resumen: media y mediana de cada tiempo; sobrecosto % de A, B y A+B frente a
  teqp; proyección para un barrido de 30 puntos con ~20 KALINA (B solo sobre KALINA).
- Costo medido de `bubble_point` en el motor real.
- ¿B detecta el caso espurio con TeqpAdapter? ¿Con A+B queda verificado?
- Honesto con el ruido de reloj (±1-2 s por ciclo): indica la dispersión.

## Files

Crear (solo en este worktree):
- `src/verificacion_motor_real.py`
- `tests/test_verificacion_motor_real.py`
- `scripts/medicion_tiempos_AB.py`
- `resultados/2026-09-27_medicion_AB/` (CSV, `run.log`, reporte)

**No modificar ningún archivo existente. No commits.**

## Constraints

- Motor real: solo en B, en las recurrencias de A y en las 25 llamadas de
  `bubble_point`. Ningún ciclo completo con el motor real.
- `python -u`, logs en `resultados/2026-09-27_medicion_AB/run.log`.
- `.py` nuevos ≤ 250 líneas.
- Correr también `pytest -q tests/test_verificacion_motor_real.py` y reportar.

## Acceptance criteria

1. B implementado y con tests pasando.
2. Tiempos medidos para los 23 puntos en los 4 modos.
3. Tabla de sobrecostos y proyección de barrido.
4. RESULTS incluye la tabla resumen de tiempos y las rutas.

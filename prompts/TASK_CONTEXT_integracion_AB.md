---
project: ciclo_kalina_tercero
task_id: 2026-09-27-integracion-A-B
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Integrar A (`TeqpVerificado`) + B (`verificar_turbina`) en el solver de barridos y en la app

## Task ID

2026-09-27-integracion-A-B

## Project

Worktree `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\teqp-doble-verificacion`,
rama `fix/teqp-doble-verificacion`. Trabaja SOLO aquí. **No hagas commits.** Los
demás `TASK_CONTEXT*.md` son otras tareas: ignóralos.

Python: `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` con cwd en este
worktree. **Nunca escribas en `/tmp` ni fuera del worktree.** Logs a
`resultados/2026-09-27_integracion_AB/`.

Ya existen y están probados (no los reescribas; solo úsalos):
- **A**: `src/properties/teqp_verificado.py` → `TeqpVerificado(x)`: `TeqpAdapter`
  que consulta `AmmoniaWaterAdapter` solo en la zona de riesgo; atributos
  `n_recurrencias`, `verificacion_incompleta`, `recurrencias`,
  `reiniciar_registro()`.
- **B**: `src/verificacion_motor_real.py` → `verificar_turbina(resultado, *, P_baja,
  motor_real, eta_t, umbral_kJkg=2.0)`: una llamada al motor real, devuelve
  `dh4s`, `verificado` (True/False/None), `t_real_s`, `error`.

Costos medidos (`resultados/2026-09-27_medicion_AB/REPORTE_MEDICION_AB.md`): A +2 %,
B ~3.5 s por punto verificado. Decisión del usuario: **usar A+B**. B se aplica
**solo a puntos KALINA** (es donde se reporta y donde se paga).

## Objective

### 1. `src/ui_backend.py` — el camino "teqp" usa A

- `construir_backend(BACKEND_TEQP, x)` debe devolver `TeqpVerificado(x=x)` en vez de
  `TeqpAdapter(x=x)`. Mantener el identificador y el valor de `BACKEND_TEQP`
  ("TeqpAdapter") sin cambios (otros módulos y el estado de sesión lo usan).
- Actualizar el texto descriptivo de la opción (línea ~22) para decir que incluye
  respaldo automático del motor real en la zona de riesgo y verificación final en
  puntos KALINA. Breve.

### 2. `src/sensitivity.py` — B (y registro de A) en `ejecutar_barrido`

- Nuevo parámetro keyword opcional `motor_real=None` (retrocompatible: sin él, el
  comportamiento es exactamente el actual).
- Si `motor_real` no es None: en cada fila con `clasificacion == "KALINA"`, llamar
  `verificar_turbina(resultado, P_baja=combo["P_baja"], motor_real=motor_real,
  eta_t=combo["eta_t"])` y añadir columnas `B_verificado`, `B_dh4s`, `B_t_s`,
  `B_error`. En filas no KALINA esas columnas van en None.
- Si el backend tiene `n_recurrencias` (es `TeqpVerificado`): añadir por fila
  `A_recurrencias` (las de ESE punto: diferencia del contador antes/después) y
  `A_verificacion_incompleta`. Si no lo tiene, None.
- Un KALINA con `B_verificado == False` NO se reclasifica ni se oculta: se deja la
  clasificación y se marca en las columnas. (Decisión de ingeniería del usuario:
  señalar, no corregir.)

### 3. `src/ui_barrido.py` — pasar el motor real cuando el backend es teqp

- Cuando el backend elegido es `BACKEND_TEQP`, construir un `AmmoniaWaterAdapter`
  (una sola instancia por barrido) y pasarlo como `motor_real` a
  `ejecutar_barrido`. Con el motor real como backend, no pasar `motor_real` (no hay
  nada que verificar).
- Las columnas nuevas deben aparecer en la tabla/descarga del barrido que ya
  muestra la UI (sin rediseñar la UI: el proyecto usa pestañas de nivel superior,
  nunca acordeones anidados).

### 4. `app.py` — análisis puntual

- En `_ejecutar`, si el backend es teqp y la clasificación es KALINA, correr
  `verificar_turbina` y guardar el resultado en el estado de sesión junto a los
  demás resultados; mostrar en la vista de resultados/clasificación una línea
  clara: "Verificación con motor real (salida de turbina): ✔ verificada
  (Δh4s = x.xx kJ/kg)" / "✘ NO verificada (Δh4s = …)" / "no evaluable (error)", y
  si `A_recurrencias > 0`, una nota "el motor real corrigió N llamadas de teqp en
  zona de riesgo".
- **`app.py` tiene 198 líneas y el límite del proyecto es 200**: pon la lógica de
  presentación en un módulo nuevo (p. ej. `src/ui_verificacion.py`) y en `app.py`
  deja solo las 1-3 líneas de llamada. Verifica con `wc -l` que ningún archivo
  tocado supere 200 líneas.

### 5. Documentación

- Añadir a `CONTEXT.md` una sección breve "Motor teqp: protección A+B" (qué hace
  `TeqpVerificado`, qué hace `verificar_turbina`, costos medidos, y la regla: todo
  barrido con teqp debe usar `TeqpVerificado` y verificar sus KALINA con
  `verificar_turbina`).

### 6. Tests y verificación

- `tests/test_sensitivity.py`: añadir tests con el backend fake que ya usa ese
  archivo y un `motor_real` fake: (a) sin `motor_real` las filas no cambian; (b) con
  `motor_real`, las filas KALINA tienen `B_*` rellenas y las no KALINA en None.
- Test de `ui_backend.construir_backend(BACKEND_TEQP, 0.6)` → instancia de
  `TeqpVerificado`.
- `python -m py_compile` de todos los archivos tocados.
- Suite: `python -u -m pytest -q -p no:cacheprovider
  --ignore=tests/test_validacion_elsayed2013.py
  --ignore=tests/test_ammonia_water_adapter.py` con salida a
  `resultados/2026-09-27_integracion_AB/pytest.log`. Fallos previos conocidos (no
  los arregles): 2 en `test_restricciones_convenciones.py` (`src/ui_campos.py` no
  existe) y 6 en `test_verificacion_iapws_g4.py` (Cv/w). Cualquier OTRO fallo es
  tuyo.
- Prueba de humo del barrido real: `ejecutar_barrido` con `TeqpVerificado` y
  `motor_real` sobre 2 combinaciones (x_b=0.65, P_alta=5000, T_fuente=423,
  P_baja=704.644595 y el espurio x_b=0.60, P_alta=4000, T_fuente=394,
  P_baja=423.914831; efectividades 0.85/0.80/0.85, T_sumidero=283, eta_t=eta_p=0.80,
  m_b=1). Guardar filas en `resultados/2026-09-27_integracion_AB/humo.csv`.

## Files

Modificar: `src/ui_backend.py`, `src/sensitivity.py`, `src/ui_barrido.py`,
`app.py` (mínimo), `CONTEXT.md`, `tests/test_sensitivity.py`.
Crear: `src/ui_verificacion.py` (o nombre equivalente), tests nuevos si hace falta,
`resultados/2026-09-27_integracion_AB/`.
**No modificar** `src/properties/` (ni el motor ni `teqp_verificado.py`), ni
`src/verificacion_motor_real.py`, ni `src/cycle_solver.py`, ni `src/restricciones/`.

## Constraints

- Retrocompatibilidad: sin `motor_real`, `ejecutar_barrido` se comporta igual que hoy.
- Archivos ≤ 200 líneas.
- No commits.

## Acceptance criteria

1. Suite sin fallos nuevos; tests nuevos pasan.
2. Humo: el punto normal sale KALINA con `B_verificado=True`; el espurio sale con
   η≈0.080 (A lo corrige) y `A_recurrencias > 0`.
3. RESULTS: archivos tocados con su nº de líneas, resultado de la suite, filas del
   humo.

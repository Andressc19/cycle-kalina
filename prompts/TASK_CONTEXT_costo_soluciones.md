---
project: ciclo_kalina_tercero
task_id: 2026-09-27-costo-soluciones-teqp
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Medir el costo en segundos de las soluciones al estado espurio de teqp

## Task ID

2026-09-27-costo-soluciones-teqp

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. `TeqpAdapter` se usa por
velocidad (~25-32 s por ciclo, vs ~280-335 s del motor real `AmmoniaWaterAdapter`).
Se encontró un estado espurio en `src/properties/_teqp_flash.py`: para mezclas muy
ricas en NH3, en la franja `Ta < T <= Ta + 0.3` K (`Ta` = T de saturación del NH3
puro a esa P, `ng.Tsat_pure`), `_fase_monofasica` (líneas 138-140) devuelve "vapor"
sin calcular el equilibrio, `s(T)` deja de ser creciente y la inversión
`TeqpAdapter._T_de` (`src/properties/teqp_adapter.py:78-89`) puede caer en una raíz
falsa (ver `resultados/2026-09-24_rama_turbina/REPORTE_RAMA_TURBINA.md`).

El usuario NO quiere modificar el motor. Opciones a comparar, y **hay que medir
cuánto tiempo cuesta cada una antes de elegir**:
- **A — "teqp verificado"**: envoltorio que, solo cuando el resultado cae en la zona
  de riesgo, repite esa llamada con el motor real y usa su resultado.
- **B — verificación final**: al terminar cada punto KALINA, comparar su salida
  isentrópica de turbina con el motor real (una llamada `h(P,s,x)` + una
  `T_from_Ps`).

**Nota:** `TASK_CONTEXT.md` y los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no
los ejecutes ni los modifiques. Tu tarea es solo este archivo.

**No modificar ningún archivo existente**, en particular nada de `src/`. Todo va en
archivos nuevos dentro de `scripts/` y `resultados/`.

## Objective

Script `scripts/costo_soluciones_teqp.py`.

### Parte 1 — Instrumentación: cuántas llamadas caen en la zona de riesgo

1. Definir en el script una subclase `TeqpContado(TeqpAdapter)` que solo CUENTE y
   CRONOMETRE (no cambia ningún resultado): por método público (`h` con T, `h` con
   s, `s`, `T_from_Ph`, `T_from_Ps`, `bubble_point`, `dew_point`,
   `equilibrio_liquido_vapor`, `fase_de` si existe) número de llamadas y tiempo
   total. Para las inversiones (`h` con s, `T_from_Ph`, `T_from_Ps`) registrar la T
   resultante y marcar la llamada como **"en zona"** si
   `x_molar >= 0.9` y `abs(T - Ta(P)) < 1.0` K, o si `x_molar <= 0.1` y
   `abs(T - Tw(P)) < 1.0` K (`Ta, Tw = ng.Tsat_pure(P_pa)`, import de
   `src.properties._teqp_engine` como `ng`; léelo para confirmar nombre y unidades).
   Medir también el tiempo de una llamada a `ng.Tsat_pure` (costo de la detección).
2. Correr `resolver_ciclo` con `TeqpContado` en estos puntos (efectividades fijas
   0.85/0.80/0.85, `T_sumidero=283`, `eta_t=eta_p=0.80`, `m_b=1`):
   - los 22 KALINA de `resultados/2026-09-24_margen2k/barrido_margen2k.csv`, cada
     uno en su `P_baja = P*`;
   - el punto problemático `(x_b=0.60, P_alta=4000, T_fuente=394)` en
     `P_baja = 423.914831` (rama espuria) y `424.169832` (rama física).
   Registrar por punto: tiempo total, llamadas totales por método, llamadas en
   zona, y η.

### Parte 2 — Costo del motor real por llamada

Con `AmmoniaWaterAdapter`, medir 5 llamadas de cada tipo, en estados reales tomados
de la Parte 1 (salida de turbina de varios puntos): `h(P, s=, x=)`,
`T_from_Ps`, `T_from_Ph`. Reportar media y máximo en segundos.

### Parte 3 — Prototipo de A y medición real

1. En el script, subclase `TeqpVerificado(TeqpAdapter)`: sobrescribe `h` (caso s),
   `T_from_Ps` y `T_from_Ph`. Hace la inversión de teqp **una sola vez** (sin
   duplicar costo fuera de la zona); si el resultado cae en la zona (mismo criterio
   de la Parte 1), repite esa llamada con `AmmoniaWaterAdapter` y devuelve el
   resultado del motor real. Fuera de la zona, el resultado debe ser idéntico al de
   `TeqpAdapter`. Contar cuántas veces recurre al motor real.
2. Correr `resolver_ciclo` con `TeqpVerificado` en: 3 KALINA normales
   (`(0.65,5000,423)`, `(0.80,5000,394)`, `(0.60,3000,394)` a su P*) y el punto
   problemático en `P_baja = 423.914831` y `424.169832`.
3. Registrar tiempo, recurrencias al motor real y η; comparar η con `TeqpAdapter`
   puro. Comprobar: en los 3 normales η idéntico; en `423.914831`, ¿`TeqpVerificado`
   da la rama física (η ≈ 0.080) en vez de la espuria (0.034)?

### Parte 4 — Tabla de costos y recomendación numérica

Reporte `resultados/2026-09-27_costo_soluciones/REPORTE_COSTO_SOLUCIONES.md` con:
- Costo por punto (segundos) de: teqp puro, A (medido), B (teqp + costo de una
  verificación final medido en Parte 2), y motor real puro (usar ~280-335 s de
  `resultados/2026-09-24_verificacion/verificacion_motor_real.csv`, o medir 1 si
  hace falta; no más de 1 ciclo del motor real).
- Frecuencia de la zona de riesgo: % de llamadas y % de puntos que la tocan.
- Proyección para un barrido de 30 puntos con cada opción.
- ¿A detecta y corrige el caso espurio? ¿B lo detecta?
- Recomendación basada en los números, honesta.

## Files

Crear:
- `scripts/costo_soluciones_teqp.py`
- `resultados/2026-09-27_costo_soluciones/` con CSV de cada parte, `run.log` y el
  reporte.

## Constraints

- No modificar ningún archivo existente.
- Motor real: solo lo necesario (Parte 2: 15 llamadas; Parte 3: las recurrencias
  que el prototipo haga; como mucho 1 ciclo completo del motor real).
- `python -u`, salida a `run.log`.
- `.py` nuevo ≤ 300 líneas.

## Acceptance criteria

1. Conteo real de llamadas en zona para los 24 ciclos de la Parte 1.
2. Costo medido por llamada del motor real y por ciclo con `TeqpVerificado`.
3. Tabla comparativa de segundos por punto y por barrido de 30 puntos.
4. RESULTS incluye la tabla y la recomendación.

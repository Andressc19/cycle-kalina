---
project: ciclo_kalina_tercero
task_id: 2026-09-23-limites-teqp
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Mapa de límites del motor `TeqpAdapter` (diagnóstico, sin tocar `src/`)

## Task ID

2026-09-23-limites-teqp

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. Las tareas previas
(`resultados/2026-09-22_tfuente_bajo/`, `resultados/2026-09-22_frontera_tfuente/`)
muestran que `TeqpAdapter` lanza `PropertyRangeError` a `T_fuente` ≤ 350 K. El
usuario pregunta **cuáles son los límites reales del motor teqp**. Hay que separar
dos cosas distintas que hoy se reportan con el mismo mensaje genérico
("el motor teqp no cubre el estado pedido"):

- (A) límites del **modelo** Tillner-Roth & Friend vía `teqp` (física/EOS);
- (B) límites del **envoltorio numérico** del proyecto en `src/properties/`
  (`teqp_adapter.py`, `_teqp_engine.py`, `_teqp_flash.py`): constantes y
  heurísticas fijas. Puntos concretos a caracterizar (léelos en el código):
  1. `TeqpAdapter._T_de`: bracket fijo `lo, hi = 230.0, 650.0` K y chequeo
     `flo > 0 or fhi < 0` → `ValueError "... fuera de dominio"`; además cualquier
     excepción de `_tf.estado` dentro de `brentq` aborta la inversión.
  2. `_teqp_engine.rho_liquido`: arranque en 60000 mol/m3, abandona si baja de
     5000 mol/m3 o de 500 mol/m3 → `"sin raiz de liquido"`.
  3. `_teqp_engine.rho_vapor`: → `"sin raiz de vapor"`.
  4. `_teqp_engine.Psat_pure`/`Tsat_pure`: clamps de agua (`_T_MIN_H2O`,
     `_T_MAX_H2O`, `_P_MIN_H2O`, `_P_MAX_H2O`) y extrapolación de NH3 por encima
     de `_TC_NH3=405.3` K con constante 2500.
  5. `_teqp_flash._fase_monofasica`: banda `Ta+0.3 < T < Tw-0.3`; si
     `bubbleP`/`dewP` no convergen → `"equilibrio no resoluble"`.
  6. `_teqp_flash.flash_TP`: devuelve `None` si fsolve no converge con 4 semillas.
  7. `_teqp_flash._satT` (bubble/dew point): `brentq` entre `Ta+0.05` y `Tw-0.05`.

## Objective

Crear `scripts/limites_teqp.py` (archivo nuevo) que produzca un mapa empírico de
cobertura y un diagnóstico de causa raíz. **Solo lectura del código de `src/`,
no modificarlo.** Partes:

### Parte 1 — Mapa de `h(P, T, x)` (dirección directa)

Llamar `_teqp_flash.estado(T, P_Pa, w2m(w))` en la malla:
- `T` de 230 a 650 K cada 10 K (43 valores)
- `P` ∈ {100, 300, 700, 1500, 3000, 6000, 11000} kPa
- `w` (fracción másica NH3) ∈ {0.05, 0.20, 0.35, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.90, 0.95}

Por punto registrar: `ok`, `fase`, `h` [J/mol], y si falla, el tipo de fallo
clasificado por el texto del mensaje: `sin_raiz_liquido`, `sin_raiz_vapor`,
`equilibrio_no_resoluble`, `otro` (con el mensaje literal truncado a 200 chars).

### Parte 2 — Monotonía de `h(T)` a (P, w) fijos

Con los datos de la Parte 1 (y si hace falta una malla más fina de 2 K solo en
las (P,w) donde se detecte algo raro), comprobar si `h(T)` es estrictamente
creciente en [230, 650] K — requisito de `brentq` en `_T_de`. Reportar
cualquier (P, w, T) donde no lo sea o donde haya saltos.

### Parte 3 — `bubble_point` / `dew_point` y `equilibrio_liquido_vapor`

`TeqpAdapter().bubble_point(P, w)` y `.dew_point(P, w)` en la malla P × w de la
Parte 1. Registrar ok/T/error.

### Parte 4 — Reproducir los fallos reales del ciclo y dar causa raíz

Casos (tomados de los CSV existentes, léelos para obtener P_baja/eps de cada uno;
NO recalcular la malla entera):
- `resultados/2026-09-22_frontera_tfuente/frontera_tfuente_teqp.csv`:
  (340 K, x_b 0.55), (340 K, 0.60), (350 K, 0.55)
- `resultados/2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv`:
  (333 K, 0.55), (333 K, 0.65), (333 K, 0.75)

Para cada caso, repetir el mismo cálculo que hicieron esos scripts
(`scripts/frontera_tfuente_teqp.py` / `scripts/exploracion_tfuente_bajo.py`,
reutilizando sus funciones o las de `scripts/calibracion_elsayed_malla.py` por
import, sin modificarlos) pero con una **subclase de `TeqpAdapter` definida en el
script nuevo** que sobreescriba `_T_de` (y si hace falta `bubble_point` /
`equilibrio_liquido_vapor`) para **registrar** antes de re-lanzar: `P`, `w`, valor
objetivo (h o s, en J/mol y en kJ/kg), `f(230)`, `f(650)`, cuál condición del
bracket falló, o la excepción interna de `estado` con el `T` donde ocurrió. La
subclase solo registra; el resultado numérico debe ser idéntico al de
`TeqpAdapter`.

Con el último estado fallido registrado de cada caso, evaluar la misma consulta
(`T_from_Ph` / `bubble_point` / `equilibrio_liquido_vapor` con los mismos
argumentos) en el motor de referencia `AmmoniaWaterAdapter` (el que ya usa el
proyecto; ver `src/properties/`). Si ahí sí resuelve, anotar la T que devuelve.
Esto es lo que separa (A) de (B): si el motor de referencia resuelve el mismo
estado, el fallo es del envoltorio teqp, no del modelo.

Además indicar si el `h` objetivo es físicamente razonable: compararlo con
`h(T, P, w)` teqp a T = 230 K y a la T de burbuja a esa P (el objetivo debería caer
entre esos valores para un líquido comprimido). Si el objetivo cae por debajo de
`h(230 K)`, decirlo explícitamente: significa que el solver del ciclo pidió un
estado a < 230 K (posible estado intermedio no físico del iterador, no un
límite de teqp) — no intentes arreglar el solver, solo repórtalo.

### Parte 5 — Reporte

`resultados/2026-09-23_limites_teqp/REPORTE_LIMITES_TEQP.md` con:
1. Mapa de cobertura de la Parte 1 resumido: por cada (P, w), rango de T que
   funciona y tipo de fallo en los huecos (tabla compacta; el detalle va al CSV).
2. Resultado de monotonía (Parte 2).
3. Tabla bubble/dew (Parte 3).
4. Tabla de los 6 casos de la Parte 4: operación que falló, P, w, h objetivo,
   f(230), f(650), condición que falló, ¿resuelve `AmmoniaWaterAdapter`? (T),
   veredicto **(A) modelo / (B) envoltorio / (C) estado no físico pedido por el
   solver** — con la evidencia que lo justifica. Si no es concluyente, decirlo.
5. Lista de límites del envoltorio (puntos B1–B7 de arriba) indicando cuáles se
   **activaron efectivamente** en los datos y cuáles no.

**No propongas ni apliques correcciones al código de `src/`**; si ves una causa
clara, déjala en RECOMMENDATIONS.

## Files

Crear:
- `scripts/limites_teqp.py`
- `resultados/2026-09-23_limites_teqp/mapa_estado.csv` (Parte 1)
- `resultados/2026-09-23_limites_teqp/saturacion.csv` (Parte 3)
- `resultados/2026-09-23_limites_teqp/casos_ciclo.csv` (Parte 4)
- `resultados/2026-09-23_limites_teqp/REPORTE_LIMITES_TEQP.md`

**No modificar ningún archivo existente**, incluido todo `src/` y `scripts/`.

## Constraints

- Nunca leer fuera de `D:\Desktop\ciclo_kalina_tercero` (ver AGENTS.md).
- No inventar el rango de validez publicado de Tillner-Roth & Friend (1998): no
  está en `CONTEXT.md`. El mapa es empírico; si quieres mencionarlo, ponlo en
  UNRESOLVED como dato pendiente.
- Reanudable por CSV en la Parte 1 (clave `(P, w, T)`), como los scripts previos.
- Capturar todas las excepciones por punto; nunca abortar la malla. Ningún
  punto se oculta.
- `.py` nuevo ≤ 300 líneas.

## Acceptance criteria

1. Los 3 CSV y el reporte existen; `mapa_estado.csv` tiene 43×7×11 = 3311 filas.
2. Los 6 casos de la Parte 4 tienen veredicto A/B/C (o "no concluyente") con
   evidencia numérica.
3. RESULTS incluye: resumen del mapa (qué zonas T/P/w fallan y por qué), la tabla
   de los 6 casos, y la lista de límites del envoltorio que se activaron.

## Verification

`python scripts/limites_teqp.py` corrido hasta el final (con reanudación si hace
falta); pegar en RESULTS el tiempo total y las tablas resumen.

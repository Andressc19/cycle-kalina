---
project: ciclo_kalina_tercero
task_id: 2026-09-20-ui-tamb-diseno-visible
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Rediseño del campo `T_amb_diseno` en la UI (visible + checkbox de margen)

## Task ID

2026-09-20-ui-tamb-diseno-visible

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente`. Continuación directa de la tarea
`2026-09-20-t-amb-diseno-configurable` (ya implementada y con tests en verde en esta misma
rama: `src/restricciones/operativos.py`/`clasificacion.py` tienen el parámetro
`T_amb_diseno: float = 303.55`, y `src/ui_campos.py` ya tiene `CAMPOS_DISENO` con ese campo
metido en un expander plegado "Criterio de diseño (cavitación)"). **Esta tarea corre en
paralelo con `TASK_CONTEXT_rangos_actualizados.md` (otra sesión, trabaja solo en
`scripts/barridos_2026-09-19/`) — no toques esa carpeta ni `resultados/barridos_2026-09-19/`,
no hay conflicto de archivos si respetas esto.**

## Objective (2 cambios de UI, decisión ya tomada por el usuario tras revisar la app)

1. **Sacar el campo `T_amb_diseno` del expander plegado** ("Criterio de diseño
   (cavitación)") y ponerlo VISIBLE, sin plegar, justo debajo de la sección "Rendimiento de
   equipos" (columna derecha de `app.py`/`ui_inputs.renderizar_inputs`, donde ya está esa
   sección) — el usuario considera que es un dato tan importante para si el ciclo clasifica
   KALINA como cualquiera de los de "Rendimiento de equipos", no debe quedar oculto.
2. **Añadir un checkbox "Aplicar margen de peor caso"** (marcado/True por defecto, para
   preservar el comportamiento actual): 
   - Marcado → el campo numérico `T_amb_diseno` está activo/editable, se usa tal cual el
     usuario lo ponga (comportamiento actual, sin cambios).
   - Desmarcado → el campo numérico se deshabilita (o se oculta, tu decisión de UX, lo que
     sea más claro) y el valor efectivo que se pasa a `evaluar_ciclo` es **el mismo
     `T_sumidero` de esa corrida** (sin ningún margen adicional — el `max(T_sumidero,
     T_amb_diseno)` del criterio O2 colapsa a `T_sumidero` solo). Esto le da al usuario
     control explícito de "quiero evaluar el peor caso" vs. "quiero evaluar solo mi punto
     puntual", en vez de tener que sincronizar manualmente dos campos.
3. Ajusta el tooltip del campo para dejar clara la relación con `T0` (estado muerto): ambos
   se derivan del mismo perfil horario de T_ambiente del enunciado del profesor — `T0` es el
   PROMEDIO (300.032917 K) y `T_amb_diseno` es el MÁXIMO/peor caso (303.55 K) — pero son
   variables independientes con propósitos distintos: `T0` es una referencia contable para
   exergía (no afecta clasificación), `T_amb_diseno` sí afecta si el punto clasifica KALINA
   (criterio O2). No los fusiones en una sola variable — son conceptualmente distintos aunque
   compartan la fuente de datos.

## Approach

1. Lee `src/ui_campos.py`, `src/ui_inputs.py`, `app.py` completos (ya deberían estar
   familiarizados de la tarea anterior en esta rama, pero verifica el estado actual real, no
   asumas).
2. En `src/ui_inputs.py`: mueve el render de `CAMPOS_DISENO` fuera del expander plegado, a un
   bloque visible justo después de la sección "Rendimiento de equipos" (en la misma columna
   derecha del layout 2×2 que ya existe, o donde tenga más sentido visualmente — tu decisión,
   pero debe quedar SIN plegar, visible sin clics adicionales). Añade el checkbox de "Aplicar
   margen de peor caso" (usa `st.checkbox`, key explícita p.ej. `"input_aplica_margen_o2"`)
   junto al campo numérico, y la lógica de deshabilitar/usar `T_sumidero` cuando está
   desmarcado (`st.number_input` acepta `disabled=True`, o simplemente no renders el campo y
   usa `T_sumidero` directamente — tu decisión de UX, documenta cuál elegiste).
3. En `app.py` (`_ejecutar`): la llamada a `evaluar_ciclo(...)` debe recibir
   `T_amb_diseno=vals["T_sumidero"]` cuando el checkbox está desmarcado, o
   `vals["T_amb_diseno"]` cuando está marcado — revisa cómo `renderizar_inputs()` devuelve
   `destino` (el dict de valores) y decide si el checkbox también viaja en ese dict (p.ej.
   `destino["aplica_margen_o2"]`) para que `app.py` pueda leerlo.
4. Actualiza `dict_parametros` en `src/ui_helpers.py` si hace falta (que el Excel exportado
   refleje el valor EFECTIVO de `T_amb_diseno` usado en esa corrida, no el del widget si
   estaba deshabilitado).
5. Verifica que todos los archivos tocados sigan ≤ 200 líneas (`wc -l`).
6. Corre `python -m pytest tests/ -q --ignore=tests/test_ammonia_water_adapter.py
   --ignore=tests/test_teqp_adapter.py --ignore=tests/test_validacion_elsayed2013.py`
   (criterio ya usado en la tarea anterior de esta rama para evitar los tests lentos de motor
   real) — no debe haber regresiones. Si tocaste algo que interactúa con los tests de motor
   real, corre también esos y repórtalo.
7. Verifica que la app arranca sin errores: `python -m py_compile app.py src/ui_inputs.py
   src/ui_helpers.py src/ui_campos.py` y `python -c "import app"`.

## Files

Puedes modificar: `src/ui_campos.py`, `src/ui_inputs.py`, `src/ui_helpers.py`, `app.py`.

**NO modifiques**: `src/restricciones/operativos.py`, `src/restricciones/clasificacion.py`
(ya están bien como están, esta tarea es solo de presentación/UI), `src/cycle_solver.py`,
`src/sensitivity.py`, `src/properties/`, `src/components/`, `src/ui_barrido.py` (si el
barrido necesita este mismo tratamiento es una tarea aparte, no la hagas aquí sin que se
pida explícitamente), `tests/test_restricciones.py`,
`tests/test_restricciones_convenciones.py` (ya tienen su cobertura, no deberían necesitar
cambios para un cambio puramente de UI — si SÍ necesitas tocarlos, explica por qué en el
reporte). **NO toques** `scripts/barridos_2026-09-19/`, `resultados/barridos_2026-09-19/`,
ni `TASK_CONTEXT_rangos_actualizados.md` (tarea paralela en curso).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. El comportamiento por defecto (checkbox marcado) debe ser IDÉNTICO al actual — no cambies
   el default de `T_amb_diseno` (303.55) ni el criterio O2 en sí.
3. No inventes nombres de criterios ni fórmulas nuevas — este es un cambio de presentación e
   interacción de UI, no de física.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS.

## Verification

Tests sin regresiones, app importa/compila sin error, todos los archivos ≤200 líneas, y una
descripción clara en el reporte de dónde quedó el checkbox y el campo en el layout final.

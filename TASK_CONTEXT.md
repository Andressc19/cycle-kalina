---
project: ciclo_kalina_tercero
task_id: 2026-09-20-t-amb-diseno-configurable
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Hacer configurable el piso de T_ambiente del criterio O2 (cavitación)

## Task ID

2026-09-20-t-amb-diseno-configurable

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente` (creada por el director para esta
tarea específica, distinta de las tareas de barridos en curso — **NO toques
`scripts/barridos_2026-09-19/`, `resultados/barridos_2026-09-19/`, ni los archivos
`TASK_CONTEXT_fase*.md`**, son trabajo de otras tareas en paralelo/pausadas que se retoman
después). Esta SÍ es una tarea de cambio de código real, autorizada explícitamente por el
usuario — a diferencia de las tareas de barrido anteriores, aquí SÍ puedes modificar
`src/restricciones/` y los módulos de UI.

## Contexto — por qué se pide este cambio

`src/restricciones/operativos.py` tiene el criterio **O2** (cavitación en la succión de la
bomba): evalúa el condensador contra `T_amb_evaluar = max(T_sumidero, T_AMB_CAVITACION)`,
donde `T_AMB_CAVITACION = 303.55` K (30.4 °C) es una **constante de módulo hardcodeada**
("piso de diseño", decisión previa documentada del vault). El usuario (el director humano
del proyecto) considera que fijar ese piso a 30.4 °C sin poder cambiarlo es una limitación
injustificada — el ciclo no necesariamente debe evaluarse siempre contra ese peor caso
concreto — y pide **convertirlo en una variable de entrada configurable**, con ese mismo
valor (303.55 K) como DEFAULT (para no cambiar el comportamiento de nadie que no la toque
explícitamente), expuesta también en la interfaz Streamlit.

## Objective

1. En `src/restricciones/operativos.py`: quitar la constante de módulo
   `T_AMB_CAVITACION = 303.55` y convertirla en un parámetro de
   `verificar_operativos(...)`, p.ej. `T_amb_diseno: float = 303.55` (keyword-only, con ese
   default explícito para preservar el comportamiento actual de todo el que no lo pase). El
   criterio sigue calculando `T_amb_evaluar = max(T_sumidero, T_amb_diseno)` igual que antes,
   solo que `T_amb_diseno` ya no es una constante fija sino el valor recibido. Actualiza el
   docstring del módulo/función para reflejar que ahora es configurable (sin perder la
   justificación física de por qué existe un piso, que sigue siendo válida como DEFAULT).
2. En `src/restricciones/clasificacion.py`: añade `T_amb_diseno: float = 303.15` — **usa el
   mismo default 303.55 que ya tenía la constante, no otro** — como parámetro keyword-only de
   `evaluar_ciclo(...)` y pásalo a `verificar_operativos(...)`. Debe seguir siendo
   retrocompatible: todas las llamadas existentes a `evaluar_ciclo(...)` que no pasen este
   argumento (ver `src/sensitivity.py`, `app.py`, `tests/test_restricciones.py`, y los
   scripts de `scripts/barridos_2026-09-19/` — NO los toques, solo verifica que sigan
   funcionando) deben comportarse EXACTAMENTE igual que antes.
3. Expón `T_amb_diseno` como un campo configurable en la interfaz Streamlit
   (`src/ui_helpers.py`/`src/ui_inputs.py`), en la misma línea que ya existe para `T0`/`P0`
   (`CAMPOS_ESTADO`, patrón `Campo` namedtuple + `_render_filas`/expander). **Decide tú si
   añadirlo a `CAMPOS_ESTADO` o crear un grupo nuevo** (p.ej. "Criterio de diseño
   (cavitación)") — lo que quede más claro para el usuario final de la app, ya que
   semánticamente NO es el estado muerto de exergía, es un piso de diseño del criterio O2.
   Default 303.55 K, rango sugerido 250.0-400.0 K (mismo rango que ya usa el campo `T0`),
   paso 0.001, formato `%.3f` (no hace falta tanta precisión como T0, que es un promedio
   calculado; aquí es una decisión de diseño de pocos decimales).
4. Conecta el nuevo valor en `app.py` (la llamada a `evaluar_ciclo(...)` en `_ejecutar`) y en
   `src/ui_barrido.py` si ese módulo también llama a `evaluar_ciclo`/`ejecutar_barrido` de
   forma que necesite el nuevo valor (revísalo tú, no asumas).
5. Actualiza `dict_parametros` en `src/ui_helpers.py` para que el nuevo campo también
   aparezca en el snapshot de parámetros del Excel exportado (mismo patrón que `T0`/`P0`).

## Restricción de tamaño de archivo — IMPORTANTE

`src/ui_helpers.py` ya está EXACTAMENTE en 200 líneas (el límite del proyecto) antes de este
cambio. **No puedes simplemente añadir código ahí** sin excederlo. Tienes que reorganizar:
la opción más simple es mover el esquema de campos (`Campo`, `CAMPOS_CICLO`, `CAMPOS_ESTADO`,
`agrupar_campos`, y el nuevo campo) a un archivo nuevo, p.ej. `src/ui_campos.py`, y que
`ui_helpers.py` los re-exporte o que `ui_inputs.py`/`app.py` importen del nuevo archivo
directamente (tu decisión de diseño, documenta cuál elegiste). Cualquier archivo que edites
debe quedar ≤ 200 líneas al terminar — verifícalo con `wc -l` antes de dar por terminada la
tarea.

## Approach

1. Lee `src/restricciones/operativos.py`, `src/restricciones/clasificacion.py`,
   `src/ui_helpers.py`, `src/ui_inputs.py`, `src/ui_barrido.py`, `app.py`,
   `tests/test_restricciones.py`, `tests/test_restricciones_convenciones.py` completos antes
   de tocar nada.
2. Haz el cambio en `operativos.py` y `clasificacion.py` primero; corre
   `python -m pytest tests/test_restricciones.py tests/test_restricciones_convenciones.py -v`
   — deben seguir pasando TODOS sin cambiar su código (retrocompatibilidad por el default).
3. Añade al menos un test nuevo en `tests/test_restricciones.py` que demuestre que
   `T_amb_diseno` cambia el resultado de O2 (p.ej. un punto que con el default 303.55 K
   dispara O2/CORREGIBLE, pero con `T_amb_diseno` más bajo, digamos igual a `T_sumidero` de
   ese caso, deja de dispararlo — o al revés, un punto sano que empieza a fallar O2 si subes
   mucho `T_amb_diseno`). Usa el patrón de mocks/fixtures que ya usa ese archivo de test, no
   inventes uno nuevo.
4. Haz el cambio de UI (`ui_helpers.py`/nuevo `ui_campos.py`/`ui_inputs.py`/`app.py`), verifica
   que la app sigue arrancando: `streamlit run app.py` (o al menos que no haya errores de
   import: `python -c "import app"` tras ajustar `sys.path` si hace falta, o revisa con
   `python -m py_compile app.py src/ui_helpers.py src/ui_inputs.py src/ui_barrido.py`).
5. Corre la suite completa (`python -m pytest -q`, sin el motor real si es muy lento —
   usa el criterio ya establecido en este repo de mockear el backend en tests unitarios) y
   reporta el resultado.

## Files

Puedes modificar: `src/restricciones/operativos.py`, `src/restricciones/clasificacion.py`,
`src/ui_helpers.py`, `src/ui_inputs.py`, `src/ui_barrido.py`, `app.py`,
`tests/test_restricciones.py`, `tests/test_restricciones_convenciones.py`. Puedes CREAR un
archivo nuevo (p.ej. `src/ui_campos.py`) si lo necesitas para el límite de 200 líneas.

**NO modifiques**: `src/cycle_solver.py`, `src/sensitivity.py`, `src/properties/`,
`src/components/`, `src/state.py`, `src/exergy.py`, `src/export_excel.py`, `src/plots.py`,
`src/ui_backend.py`, `src/ui_clasificacion.py`. **NO toques**
`scripts/barridos_2026-09-19/`, `resultados/barridos_2026-09-19/`, ni
`TASK_CONTEXT_fase1_profesor.md`/`_fase2_libre.md`/`_fase3_real.md` (tareas paralelas en
otras ramas/sesiones).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas — verifica TODOS los que toques o crees.
2. El default de `T_amb_diseno` debe ser EXACTAMENTE 303.55 (K) en ambas firmas
   (`verificar_operativos` y `evaluar_ciclo`) — es el valor que ya estaba hardcodeado, para
   no romper ningún resultado existente.
3. No inventes rangos ni fórmulas nuevas: el criterio O2 en sí (`max(T_sumidero,
   T_amb_diseno)`, comparación contra `bubble_point(P_baja, x_b)`) no cambia, solo de dónde
   viene el segundo argumento del `max`.
4. Todos los tests existentes deben seguir pasando sin modificar su lógica (solo puedes
   AÑADIR tests nuevos, no cambiar el comportamiento esperado de los que ya había).

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `TESTS`, incluye la salida real de pytest (conteo pass/fail). En
`FILES_CHANGED`, lista explícitamente cada archivo tocado o creado y por qué.

## Verification

`python -m pytest -q` sin regresiones, más el test nuevo de `T_amb_diseno` en verde, más
confirmación de que ningún archivo `.py` tocado supera 200 líneas.

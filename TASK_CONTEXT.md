---
project: ciclo_kalina_tercero
task_id: 2026-09-17-ui-streamlit
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-17
---

# TASK_CONTEXT — UI Streamlit (app.py)

## Task ID

2026-09-17-ui-streamlit

## Project

ciclo_kalina_tercero. Última pieza para tener el proyecto visualmente completo (por decisión
del usuario, la sensibilidad paramétrica queda para después — esta UI corre **una sola
simulación por clic**, no barridos). Conecta todo lo ya construido y verificado: adapter de
propiedades, componentes, solver, exergía, Excel y gráficas.

## Objective

Implementar `app.py` (hoy stub `TODO`): una app Streamlit en español para un público **poco
familiarizado con software académico** (`Kalina_ksc_11_tercero.md`, sección 8), que permita
introducir los parámetros de entrada, ejecutar la simulación real, ver los resultados
(estados, energías, exergía), descargar el Excel y las gráficas.

## Context — pieza crítica: el cálculo real tarda ~8-9 minutos

`resolver_ciclo` con el backend real (`AmmoniaWaterAdapter`) tarda del orden de **8-9 minutos**
por corrida (motor NH3-H2O riguroso, ya diagnosticado y optimizado en una tarea anterior — no
es un bug, es el costo real de la física). La UI **debe**:
- Mostrar un aviso explícito y visible ANTES de que el usuario pulse "Ejecutar simulación"
  (algo como: "⏱ El cálculo con el motor de propiedades real puede tardar varios minutos —
  no cierres esta pestaña mientras corre").
- Usar `st.spinner(...)` con un mensaje mientras corre, para que no parezca colgada.
- Guardar el resultado en `st.session_state` (no recalcular en cada rerun de Streamlit —
  Streamlit re-ejecuta el script en cada interacción; solo se debe llamar a `resolver_ciclo`
  cuando el usuario pulsa el botón, nunca implícitamente).
- Capturar `CicloNoConvergeError` (de `src/cycle_solver.py`) y `PropertyRangeError` (de
  `src/properties/adapter.py`) y mostrarlas como un mensaje de advertencia claro en español
  (no un traceback crudo) — coherente con `Kalina_ksc_11_tercero.md` sección 6 ("Emitir
  advertencias claras cuando los datos salgan del rango válido").

Revisa las firmas reales antes de escribir, no las asumas:
- `src/cycle_solver.py::resolver_ciclo(backend, *, P_alta, P_baja, T_fuente, T_sumidero,
  x_b, m_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, tol_T1=..., tol_T10=...,
  max_iter_frio=...) -> dict` y `CicloNoConvergeError`.
- `src/exergy.py::calcular_exergia(resultado_ciclo, backend, *, T0, P0) -> dict`.
- `src/export_excel.py::generar_excel(resultado_ciclo, resultado_exergia, parametros, backend_nombre) -> bytes`.
- `src/plots.py::grafico_balance_energia(resultado_ciclo) -> Figure`,
  `grafico_exergia_destruida(resultado_exergia) -> Figure`.
- `src/properties/ammonia_water_adapter.py::AmmoniaWaterAdapter`,
  `src/properties/iapws_adapter.py::IAPWSAdapter`,
  `src/properties/pyfluids_adapter.py::PyfluidsAdapter`.

Valores por defecto de todos los campos: usa la tabla de `CONTEXT.md` ("Valores por defecto
sugeridos para la UI"), **ya actualizada** (T_fuente=470.0 K). T0=300.032917 K, P0=101.325 kPa
(estado muerto).

## Layout sugerido (ajustable, no es obligatorio pixel a pixel)

1. **Cabecera**: título, breve descripción del ciclo KSC-11 (puedes usar el diagrama
   Mermaid de `Kalina_ksc_11_tercero.md` sección 1 como texto/imagen si es simple, o
   omitirlo si complica — no es un requisito duro).
2. **Sidebar o sección de entradas**: todos los campos numéricos con:
   - Etiqueta clara + unidad visible.
   - `help=` (tooltip) explicando qué es cada parámetro, en español sencillo.
   - Valor por defecto de `CONTEXT.md`.
   - Selector de backend de propiedades: **por defecto y único camino real,
     `AmmoniaWaterAdapter`**; puedes listar `IAPWSAdapter`/`PyfluidsAdapter` en el selector
     pero deshabilitados o marcados "(no aplica a la mezcla NH3-H2O en este entorno)" — no
     dejes que el usuario elija un backend que sabes que va a fallar sin advertirlo.
3. **Botón "Ejecutar simulación"** (con el aviso de tiempo ANTES del botón, no después).
4. **Resultados** (solo tras ejecutar, desde `st.session_state`):
   - Tabla de los 10 estados (T, P, h, s, x, m, q, fase, exergía física) — `st.dataframe`.
   - Métricas destacadas (`st.metric`): `η` energético, `η` exergético (`Wnet/Ex_Qi`), `Wnet`,
     `Qi`, `Qout`.
   - Las dos gráficas de `plots.py` (`st.pyplot`).
   - Tabla de `Sgen`/`Ed` por componente.
   - Panel de advertencias (si `CicloNoConvergeError`/`PropertyRangeError`, o si algún `Sgen`
     saliera negativo — repórtalo como advertencia de 2ª ley, no lo ocultes).
5. **Descargas**: botón de Excel (`st.download_button`, `generar_excel(...)`) y botones para
   descargar cada gráfica como PNG (usa `fig.savefig` a un buffer `BytesIO`).
6. **Sección de sensibilidad**: un `st.tabs`/`st.expander` visible pero con contenido tipo
   "Próximamente — barrido de sensibilidad paramétrica" (la lógica de `sensitivity.py` no
   existe todavía, es una tarea futura). No implementes nada funcional aquí, solo el espacio
   reservado en la UI, coherente con `Kalina_ksc_11_tercero.md` sección 9 ("la UI debe quedar
   preparada para configurarlos sin reescribir el solver").

## Files

Implementar (hoy stub `TODO`):
- `app.py`

Si `app.py` no cabe en 200 líneas con todo lo anterior, divide en `app.py` (orquestación
principal) + un módulo de ayuda, por ejemplo `src/ui_helpers.py` (construcción de la tabla de
estados como DataFrame, formateo de advertencias, etc.) — mismo patrón de división ya usado
antes cuando un archivo se acerca al límite.

No tocar ningún otro archivo — esta tarea es pura integración de lo ya construido.

## Constraints

- No implementes nada de sensibilidad real (solo el placeholder de UI).
- No hagas que la app llame a `resolver_ciclo` fuera del clic explícito del botón (ni en la
  carga inicial de la página, ni en cada rerun).
- Cada archivo `.py` ≤ 200 líneas.
- No se puede probar esta tarea con `pytest` de forma significativa (es una app interactiva) —
  en su lugar, verifica manualmente que `streamlit run app.py` levanta sin errores de sintaxis/
  import (usa `python -c "import ast; ast.parse(open('app.py').read())"` como mínimo, y si es
  posible, arráncala con `streamlit run app.py --server.headless true` unos segundos y
  verifica en el log que no hay excepción de arranque, luego mátala).

## Acceptance criteria

1. `streamlit run app.py` levanta sin errores (verificado como se describe arriba).
2. Todos los campos de entrada de `CONTEXT.md` están presentes, con etiqueta, unidad,
   tooltip y valor por defecto.
3. El botón de ejecutar muestra el aviso de tiempo, usa `st.spinner`, y solo llama a
   `resolver_ciclo` al pulsar (no antes).
4. `CicloNoConvergeError`/`PropertyRangeError` se capturan y se muestran como advertencia
   clara en español, no como traceback.
5. Los botones de descarga (Excel + gráficas) están conectados a las funciones reales de las
   tareas anteriores.
6. Ningún archivo supera 200 líneas.

## Expected output

`app.py` funcional, integrando todo el proyecto, con la sensibilidad reservada como
"próximamente" para la tarea que sigue después.

## Verification

Arranque manual de `streamlit run app.py` (o equivalente headless) sin excepciones, más
`python -c "import ast; ast.parse(open('app.py').read())"` limpio. Reporta en RESULTS qué
verificaste exactamente y qué viste en pantalla/log.

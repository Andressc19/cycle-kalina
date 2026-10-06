# TASK_CONTEXT — Campaña final, M0 (protocolo + utilidades) y M1 (reproducir la Fase 1 del profesor)

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`. Es un
worktree dentro del proyecto. TODO se crea y se ejecuta aquí; no se escribe nada en la raíz del
proyecto.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (ya trae scipy, pandas,
openpyxl y scikit-learn).
**Documentos de referencia (leerlos antes de empezar):** `docs/METODOLOGIA_BARRIDOS_FINAL.md`
(§1 y M1), `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` (§1–§3), `CONTEXT.md`.

## Notas de entorno (OBLIGATORIAS; la corrida 051 falló por esto)

- **Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.** NUNCA desde
  la terminal: nada de `cat <<`, here-strings, `Set-Content`, `Write-Content` ni `python -c` que
  escriba archivos.
- La terminal es Windows PowerShell 5.1. Úsala solo para EJECUTAR comandos, por ejemplo
  `& "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" -m pytest ...`.
  - No existe `tee`: usa `... 2>&1 | Tee-Object -FilePath <ruta>`.
  - No existe `&&`: encadena con `;`.
- Para las ejecuciones largas (el paso 4), lanza el script y espera a que termine; no lo
  relances si tarda.

## Objetivo

1. Crear las utilidades comunes de la campaña (configuración congelada, evaluación de un punto,
   márgenes de O1/O2/O3/O5 e índice D).
2. Volver a correr los 41 puntos de la Fase 1 del profesor con el código actual.
3. Comparar punto por punto con la corrida del 2026-09-19.
4. Crear el libro nuevo `datos/Excel_final_kalina.xlsx` con las hojas de M0 y M1.

## Restricciones

- **NO modificar nada en `src/`, `app.py`, `ui_*.py` ni `scripts/formatear_excel_barridos.py`.**
  `src/` se usa solo como librería.
- Cada `.py` nuevo debe tener como máximo 200 líneas.
- No inventar valores. Lo que falte se reporta en UNRESOLVED.
- **Nunca reportar una ejecución que no ocurrió.** Cada número del reporte tiene que salir de un
  archivo generado en esta tarea. Si un paso falla, el STATUS es `partial` o `failed` y se dice cuál.
- No borrar nada fuera de lo que esta tarea crea.

## Archivos a crear

### 1. `scripts/barrido_final/comun.py`

Contenido mínimo:

- **Constantes de la configuración congelada:**
  - `PROFESOR = dict(T_fuente=623.15, T_sumidero=300.032917, P_alta=3000.0, P_baja=400.0,
    x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)`
  - `T_AMB_DISENO = 300.032917`
  - `TAU = dict(O1=0.01, O2=1.0, O3=1.0, O5=0.01)`
  - `PRESUPUESTO_S = 300`
  - `VARS` = las 11 variables en el orden de `src.sensitivity.VARIABLES_BARRIBLES`.

- **`margenes(backend, resultado, combo) -> dict`.** Replica EXACTAMENTE las fórmulas de
  `src/restricciones/operativos.py::verificar_operativos`, pero devuelve números en lugar de fallas:
  - `q4` = `backend.fase_de(P_baja, e4.T, e4.x)[1]` → `m_O1 = q4 − 0.90`
  - Se toma `T_amb = max(T_sumidero, T_AMB_DISENO)` y se resuelve
    `estado9_amb, _ = condensador.resolver(e8, backend, T_sumidero=T_amb, eps=eps_cond, m=m_b)`
    (importar `condensador` desde `src.components`). Después,
    `T_bub = backend.bubble_point(P_baja, x_b)` y `m_O2 = T_bub − estado9_amb.T`.
  - `m_O3 = resultado["Wnet"]`
  - `q2` = `backend.fase_de(P_alta, e2.T, x_b)[1]` → `m_O5 = min(q2 − 0.001, 0.999 − q2)`
  - Devuelve `q4, q2, T9_amb, T_bub, m_O1, m_O2, m_O3, m_O5`. Si un cálculo lanza una excepción,
    ese valor queda en `None` y el mensaje se guarda en `err_margenes`.

- **`indice_D(m) -> (D, viol)`.** `viol_k = max(0, −m_k)` y `D = Σ viol_k / TAU[k]` para
  k ∈ {O1, O2, O3, O5}. Si algún margen es `None`, D es `None`.

- **`evaluar_punto(combo, *, motor="teqp", tag=None) -> dict`.** Es una función de nivel de módulo
  (el pool de procesos usa spawn). Sigue la misma receta que `scripts/prueba_pr2.py::_con_ma` de la
  raíz del proyecto (copiada aquí en espíritu; no importar ese archivo):
  - Con `motor="teqp"`: `backend = TeqpVerificado(x=x_b)` y `motor_real = AmmoniaWaterAdapter(x=x_b)`.
  - Con `motor="real"`: `backend = AmmoniaWaterAdapter(x=x_b)` y `motor_real = None`.
  - Se guardan los contadores A antes de resolver: `(backend.n_recurrencias, backend.n_fallos)`,
    solo si existen.
  - `res = resolver_ciclo(backend, **combo, bracket_tolerante=True, presupuesto_s=PRESUPUESTO_S)`.
    Si lanza `CicloNoConvergeError` o `PropertyRangeError`, la fila queda como NO_CONVERGIO con el
    mensaje de la excepción. Cualquier otra excepción se registra en `error_inesperado` y NO se
    trata como NO_CONVERGIO.
  - Si converge: `evaluar_ciclo(backend, res, **{k: combo[k] for k in sensitivity._CRIT},
    T_amb_diseno=T_AMB_DISENO)`. Después `sensitivity._anotar_ab(...)` (solo para teqp),
    `anotar_rango(fila, combo, res, motor, backend, "extrapolar_marcar")`, `margenes` e `indice_D`.
    También se anotan los datos del bracket (`res["bracket"]`: lo, hi, repliegues_lo,
    repliegues_hi, nF), si existen.
  - La fila incluye `tag`, el motor, `pid`, `t_s` (tiempo de pared) y todas las entradas.

### 2. `scripts/barrido_final/m1_reproducir_f1.py`

- Construye las tareas exactamente como lo hace
  `scripts/barridos_2026-09-19/fase1_profesor/correr_fase1_profesor.py`:
  - P_alta: `generar_valores(Barrido(2000, 4000, 250))`, 9 puntos.
  - x_b: `Barrido(0.40, 0.70, 0.05)`, 7 puntos.
  - T_sumidero: las 24 filas de `scripts/barridos_2026-09-19/fase1_profesor/tamb_profesor.csv`,
    con su `hora`.
  - El resto de las variables en `PROFESOR`.
  - Punto base: dos corridas, una con `motor="teqp"` y otra con `motor="real"`. La de motor real
    es la que se compara con la corrida de 2026-09-19, que también usó el motor real.
  - Total: 42 corridas.
- Las corridas se ejecutan con `ProcessPoolExecutor(max_workers=6)`. Cada fila se escribe en
  `resultados/2026-10-06_final_M1/m1_filas.csv` en cuanto termina, con flush. Después de cada
  punto se imprime `[n/42] grupo i clase t_s`, también con flush, para poder vigilar el avance.
- **Comparación** (`m1_comparacion.csv`) contra:
  - `resultados/barridos_2026-09-19/fase1_profesor/eta_vs_Palta_profesor.csv`,
    `eta_vs_xb_profesor.csv` y `eta_vs_Tambiente_profesor.csv`. El emparejamiento es por el valor
    de la variable barrida; para T_amb, por `hora`.
  - El punto base anterior, que es NO_CONVERGIO según
    `resultados/barridos_2026-09-19/fase1_profesor/CONSTANCIA_PROFESOR.md` §2.
  - Columnas: `grupo, valor, clase_antes, clase_ahora, misma_clase, eta_antes, eta_ahora,
    d_eta_pp, mensaje_antes (80 caracteres), mensaje_ahora (80 caracteres)`.
- **`REPORTE_M1.md`** en lenguaje llano, con estas secciones: la pregunta, qué se hizo, una tabla
  de conteos por clase (antes y ahora), la tasa de coincidencia (aciertos/41), los tiempos (total y
  por punto), cada punto que cambió de clase con su explicación según el mensaje (si no hay
  explicación, se dice así), lo que no se sabe y qué sigue.
- Nota que debe incluirse: la corrida de 2026-09-19 usó el piso de O2 por defecto (303.55 K) y no
  usó MA; esta corrida usa 300.032917 K y MA. Solo afecta a puntos que converjan.

### 3. `scripts/barrido_final/excel_final.py`

Genera `datos/Excel_final_kalina.xlsx` en el worktree:

- **Hoja `M0_protocolo`:** pares clave/valor con el commit (`git rev-parse HEAD`), la fecha, el
  motor (`TeqpVerificado` + B + `bracket_tolerante=True`, `presupuesto_s=300`, `motor_rango`), la
  `T_AMB_DISENO`, las `TAU`, el punto `PROFESOR`, las ε permitidas [0.75, 0.85] y las rutas de los
  documentos de metodología.
- **Hojas `M1_profesor_P_alta`, `M1_profesor_x_b`, `M1_profesor_T_amb`, `M1_profesor_base`** con
  las filas de `m1_filas.csv` de cada grupo, y la hoja **`M1_comparacion`**.
- **Hoja `Resumen`** con el conteo por clase de cada hoja.
- **Formato** (las reglas del proyecto):
  - Títulos con la unidad entre paréntesis y coloreados por tipo (entrada / resultado /
    diagnóstico / clase / texto).
  - Filtro en todas las tablas.
  - Clase coloreada: KALINA `C6EFCE`, CORREGIBLE `FFD9A0`, NO_CONVERGIO `F8B4B4`, INVIABLE `FFF2A8`.
  - Columnas `mensaje` y de errores anchas, con ajuste de texto.
  - Al final de cada tabla, 2 filas vacías y una descripción corta: qué se iteró, qué quedó fijo y
    el conteo por clase.

  Se pueden IMPORTAR funciones y constantes de `scripts/formatear_excel_barridos.py` (por ejemplo
  `COLOR_CLASE`, `COLOR_TITULO`, `unidad`, `tipo_col`), pero sin modificar ese archivo. Unidades
  de las columnas nuevas: `m_O1` (−), `m_O2` (K), `m_O3` (kW), `m_O5` (−), `D` (−), `T9_amb` (K),
  `T_bub` (K), `t_s` (s).
- El script se puede volver a ejecutar: reescribe el libro completo a partir de los CSV de
  `resultados/2026-10-06_final_M*`.

### 4. `scripts/barrido_final/test_comun.py` (pytest, con mocks, sin el motor real)

- `indice_D`:
  - Todos los márgenes ≥ 0 → D = 0.
  - Con `m_O1 = −0.03` y `m_O2 = −2`, D = 5.0 (el ejemplo del documento de matemática).
  - Con un margen `None`, D es `None`.
- `margenes` con un backend falso (stubs de `fase_de`, `bubble_point` y un `condensador.resolver`
  sustituido con monkeypatch): comprobar que m_O1, m_O2, m_O3 y m_O5 salen con las fórmulas
  anteriores.
- El conteo de tareas de M1 es 42, con 41 comparables.

## Pasos

1. Crear los 4 archivos.
2. `python -m pytest scripts/barrido_final/test_comun.py -q` → todo verde.
3. Humo: `evaluar_punto(PROFESOR, motor="teqp")` una sola vez; imprimir la fila.
4. Crear la carpeta `resultados/2026-10-06_final_M1/` y ejecutar
   `python scripts/barrido_final/m1_reproducir_f1.py 2>&1 | Tee-Object -FilePath
   resultados/2026-10-06_final_M1/stdout.txt`. El tiempo esperado es de 10 a 30 minutos; no
   interrumpirlo.
5. Ejecutar `python scripts/barrido_final/excel_final.py`.
6. Comprobar que `m1_filas.csv` tiene 42 filas y `m1_comparacion.csv` tiene 41, y que el xlsx
   existe y tiene las hojas pedidas (abrirlo con openpyxl e imprimir los nombres de las hojas).
7. NO hacer commit.

## Formato de salida

El obligatorio de `AGENTS.md`: STATUS / SUMMARY / FILES_CHANGED / TESTS / RESULTS / ERRORS /
ASSUMPTIONS / UNRESOLVED / RECOMMENDATIONS. En RESULTS deben ir los conteos por clase, la tasa de
coincidencia y las rutas de todos los archivos generados.

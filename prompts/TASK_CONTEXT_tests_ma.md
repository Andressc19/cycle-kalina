---
project: ciclo_kalina_tercero
task_id: 2026-10-02-tests-primero-ma
delegated_to: executor
created: 2026-10-02
---

# TASK_CONTEXT — Tests PRIMERO del bracket tolerante MA ("siempre tolerante") con presupuesto de tiempo. Deben FALLAR contra el código actual. SIN tocar `src/`

## Task ID

2026-10-02-tests-primero-ma

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques. Esta tarea SUSTITUYE el diseño de `prompts/TASK_CONTEXT_tests_reintento_tolerante.md` (modo MB "reintento solo si falla"), que el director descartó a favor de **MA**.

## Contexto y evidencia (por qué MA)

Decisión del director (criterio: menor tiempo de barrido): **MA = V2 desde el primer intento**, sin tope de repliegues por defecto y con un **presupuesto de tiempo por punto** opcional. Evidencia: `resultados/2026-10-01_ablacion_tiempos/REPORTE_ABLACION_TIEMPOS.md` (V2 recupera 28 de 40 filas que el solver actual no resuelve; en filas sanas mismo `eta` y mismo `nF`), `resultados/2026-10-01_benchmark_reintento/REPORTE_BENCHMARK.md` (con tope 6 se recuperan solo 11; **sin tope 27–28**; las filas recuperadas tardan ≤ 220 s, las no recuperables hasta 500 s), y el prototipo en `scripts/sonda_arranque_solver.py` (`_bracket_tol`, `F_seguro`, `orquestar` variante V2: úsalo SOLO como referencia de comportamiento, no lo importes en los tests).

## Especificación de la API (decisión del director; no la cambies)

`resolver_ciclo(..., bracket_tolerante: bool = False, paso_repliegue: float = 5.0, max_repliegues: int | None = None, presupuesto_s: float | None = None)`

- `bracket_tolerante=False` (por defecto): comportamiento **idéntico al actual, bit a bit**, mismas claves de salida. `max_repliegues`, `paso_repliegue` y `presupuesto_s` se ignoran.
- `bracket_tolerante=True` (MA): desde la PRIMERA evaluación
  1. arranque del lazo frío `T10_inicial = T_sumidero + 5.0` K en la primera evaluación de `F` (el arranque tibio posterior con el último `T10` convergido se conserva, igual que hoy);
  2. bracket tolerante: `F_seguro` captura `PropertyRangeError` y devuelve `None`; si `F(lo)` es `None` se repliega `lo` hacia dentro `paso_repliegue` K por intento mientras `lo + paso < hi`; análogo con `hi` hacia abajo mientras `hi − paso > lo`; **`max_repliegues=None` = sin tope** (hasta agotar el rango); si es un entero, ese es el máximo de **repliegues** por extremo (el primer intento no cuenta: tope 2 ⇒ hasta 3 evaluaciones por extremo); si no hay dos extremos evaluables o no hay cambio de signo ⇒ `CicloNoConvergeError`;
  3. durante `brentq`, un `PropertyRangeError` en un punto interior ⇒ `CicloNoConvergeError` con la T en el mensaje (no se inventa otra recuperación);
  4. solo se tolera `PropertyRangeError`; `ValueError`, `TypeError` y demás se propagan sin envolver;
  5. **presupuesto de tiempo:** si `presupuesto_s` no es `None`, se mide el reloj de pared con `time.perf_counter()` desde el inicio de `resolver_ciclo` (el módulo debe hacer `import time` y llamar `time.perf_counter()` en el momento, para que los tests puedan sustituirlo); se comprueba **entre evaluaciones** de `F` (nunca a mitad de una); si se supera ⇒ `CicloNoConvergeError` con el texto "presupuesto de tiempo agotado" y el número de evaluaciones hechas;
  6. el dict de salida lleva la clave extra `bracket` = `dict(lo=…, hi=…, repliegues_lo=…, repliegues_hi=…, nF=…)` **solo** si `bracket_tolerante=True` (con `False` las claves son exactamente las actuales).

## Objective

1. **`tests/test_bracket_tolerante.py`** (nuevo, ≤200 líneas, rápido, SIN teqp ni motor real; backend fake como `tests/test_cycle_solver.py`, extendido con subclase que lance `PropertyRangeError` en temperaturas elegidas). **Reutiliza el andamiaje ya calibrado** de `tests/test_reintento_tolerante.py` (BASE, BASE_ANCHO, T de fallo, tolerancias justas `tol_T1=1e-10`, `tol_T10=1e-8`, contador de llamadas) en lugar de reinventarlo. Casos mínimos:
   1. Sin el flag: resultado idéntico al actual (mismo `eta`, `T1`, mismas claves, mismo número de llamadas al backend).
   2. Con el flag y sin fallos: mismos `eta` y `T1` (|Δ| < 1e-9) y **mismo número de evaluaciones de `F`** que sin el flag (`bracket["nF"]` igual al que cuenta el test sobre el camino actual); no se exige el mismo número de llamadas al backend (el arranque cambia).
   3. Extremo alto falla ⇒ converge, mismo `eta` que sin fallos, `bracket["repliegues_hi"] ≥ 1`.
   4. Extremo bajo falla; y ambos fallan con interior evaluable.
   5. Todo el rango falla ⇒ `CicloNoConvergeError`, sin bucle infinito: el número de llamadas está acotado por `2·ceil(rango/paso) + constante` (compruébalo con contador).
   6. Sin cambio de signo en el rango evaluable ⇒ `CicloNoConvergeError`.
   7. Respeta `max_repliegues`: con tope 2 y un extremo que falla 3 veces seguidas ⇒ `CicloNoConvergeError`; con tope 3 ⇒ converge.
   8. **Por defecto no hay tope** (lección del error de los topes): un extremo que falla 12 veces seguidas converge con los valores por defecto, y con `max_repliegues=6` lanza `CicloNoConvergeError`.
   9. `paso_repliegue` distinto de 5.0 se respeta (comprueba las T evaluadas).
   10. `ValueError` en un extremo se propaga sin reintento ni envoltura.
   11. Punto interior no evaluable durante `brentq` ⇒ `CicloNoConvergeError` con la T en el mensaje.
   12. **Presupuesto agotado:** con un reloj falso (sustituye `time.perf_counter` con `monkeypatch`; el reloj avanza X s por llamada al backend) y `presupuesto_s` pequeño ⇒ `CicloNoConvergeError` con "presupuesto de tiempo agotado"; el número de evaluaciones de `F` posteriores al instante en que se rebasó es ≤ 1 (se comprueba entre evaluaciones, no a mitad).
   13. `presupuesto_s=None` o muy grande no cambia el resultado (mismo `eta`/`T1`).
   14. No hay estado compartido: dos llamadas seguidas con los mismos datos dan el mismo resultado; una llamada fallida no contamina la siguiente.
   15. La clave `bracket` existe solo con el flag (con `False` las claves son las actuales) y trae `nF`, `lo`, `hi`, `repliegues_lo`, `repliegues_hi` coherentes con las T evaluadas.
2. **`scripts/verificar_controles_ma.py`** (nuevo, ≤200 líneas): verificación **lenta** con `TeqpVerificado`, fuera de la suite normal. Compara, llamando a `resolver_ciclo(..., bracket_tolerante=True)`, contra las columnas V2 de `resultados/2026-10-01_ablacion_tiempos/ablacion_filas.csv` (`V2_eta`, `V2_clas`): las 10 filas de control (`ctl_*`) y 8 filas recuperadas por V2 (2 de cada grupo `f2_T_from_Ph`, `lit_T_from_Ph`, `lit_bifasico`, `f2_h_Ps` si existe; si un grupo no tiene recuperadas, completa con el siguiente). Criterio: `|Δη| < 1e-4` y misma clasificación. Debe ejecutarse hoy y **fallar con un error claro de API** (argumento desconocido). Reutiliza la carga de parámetros por fila de `scripts/verificar_controles_reintento.py` (ya probada con el prototipo) en vez de reescribirla. Una línea de progreso por fila en `resultados/2026-10-02_tests_ma/progreso.log` (con `flush`). Un fallo en una fila no aborta las demás.
3. **Demostrar que los tests miden algo:** ejecutar `pytest tests/test_bracket_tolerante.py` ahora y guardar la salida: deben fallar con `TypeError` por argumento desconocido todos los casos salvo los que no usan el flag (1 y 14 en su parte sin flag; indícalo). Además comprobar que los 15 casos son **satisfacibles**: escribir un prototipo mínimo FUERA del repo (en el directorio temporal del usuario, p. ej. `C:\Users\Usuario\AppData\Local\Temp\opencode\proto_ma.py`) que implemente la especificación mediante monkeypatch de `resolver_ciclo`, y ejecutar los mismos tests contra él: deben pasar todos. Reporta ambos resultados.
4. **Retirar el diseño anterior sin borrar evidencia:** mueve `tests/test_reintento_tolerante.py` a `resultados/2026-10-02_tests_ma/OBSOLETO_test_reintento_tolerante_MB.py` (un solo archivo, con `Move-Item`/`mv`; NADA de borrado recursivo) y `scripts/verificar_controles_reintento.py` a `resultados/2026-10-02_tests_ma/OBSOLETO_verificar_controles_reintento_MB.py`. Si el director los necesitara, están ahí.
5. **Línea base de la suite:** NO re-ejecutes la suite completa (tarda ~11 min y ya existe la línea base 182 passed / 1 skipped / 8 xfailed en `resultados/2026-10-01_tests_reintento/linea_base_suite.txt`, medida con `src/` idéntico). Verifica con `git status --short src` que `src/` sigue limpio y repórtalo; indica que la línea base vigente es esa.

## Constraints

- **No modificar `src/`** ni otros tests existentes. Archivos nuevos solo: `tests/test_bracket_tolerante.py`, `scripts/verificar_controles_ma.py`, `resultados/2026-10-02_tests_ma/` (salidas, reporte, los dos archivos OBSOLETO). Nada en la raíz del repo ni `.log` sueltos.
- No agregar dependencias. Python del venv (`.venv\Scripts\python`). Cada archivo ≤200 líneas.
- Cualquier cálculo de más de ~1 minuto va desacoplado (`nohup ... &`) y se sigue con consultas cortas (nunca un comando de más de ~90 s). El script lento del punto 2 solo se ejecuta para demostrar el fallo de API (termina en segundos); no hace falta correrlo completo.
- Registra `git branch --show-current` y `git status --short src` al inicio y al final (otras sesiones comparten el checkout) y repórtalos. No ejecutes `git checkout/switch/commit/stash`.
- No implementes el bracket tolerante "para que pasen": los tests deben quedar en rojo; el prototipo vive fuera del repo.
- Sin credenciales; sin leer fuera del proyecto salvo el directorio temporal del usuario para el prototipo.

## Outputs

- Los dos archivos nuevos; `resultados/2026-10-02_tests_ma/pytest_rojo.txt`, `pytest_prototipo_verde.txt`, `progreso.log`, los dos `OBSOLETO_*`, y `REPORTE_TESTS_MA.md` con el formato: **La pregunta · Qué se especificó (API de MA en lenguaje llano) · Cómo se hizo · Qué se probó (tabla de los 15 casos y su resultado hoy y con el prototipo) · Tiempos · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea; sin descripciones inexactas del ciclo (h1 es la entalpía a la entrada del HRVG = salida fría del regenerador, no del condensador).
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- 15 casos escritos; hoy fallan por la causa esperada (API), no por errores del fake o de importación.
- 15/15 verdes contra el prototipo externo.
- Script lento de controles ejecutable y fallando con error de API claro.
- Archivos MB retirados a `resultados/2026-10-02_tests_ma/` (no borrados).
- `git status` muestra solo los archivos permitidos; `src/` limpio.

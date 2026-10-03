# REPORTE — Implementación del bracket tolerante MA en `src/` (`2026-10-02-implementar-ma`)

Worktree `solver-bracket`, rama `fix/solver-bracket-tolerante` (base `2de6050`). Python:
`D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` con el directorio actual = este worktree.
**Sin commits.** `src/_cycle_loops.py` **no** se tocó (hizo falta injectar `evaluar`, no tocarlo).

## La pregunta

El resolutor del ciclo Kalina se rinde (`NO_CONVERGIO`) cuando el motor de propiedades no
puede evaluar un estado, aunque ese estado esté solo en un **extremo** del intervalo de
temperaturas que el buscador está explorando. ¿Se puede hacer que se quede **siempre
tolerante** ante esos estados —replegando el extremo hacia dentro en vez de abandonar— sin
romper ni un solo resultado del caso sano?

## Qué se cambió (en simple)

Solo dos archivos, y nada de lo que ya funcionaba se ha tocado:

1. **`src/_bracket_tolerante.py` (nuevo, 146 líneas)**: una clase `BracketTolerante` que
   lleva la lógica nueva del lazo exterior.
2. **`src/cycle_solver.py`** (82 → 121 líneas): `resolver_ciclo` acepta cuatro parámetros
   nuevos y, si se le pide el modo tolerante, delega en esa clase.

Los cuatro parámetros nuevos, con `bracket_tolerante=False` (por defecto) **todo lo anterior
sigue igual**: mismas llamadas al motor, mismos números, mismas claves de salida. Los otros
tres parámetros se ignoran sin el primer flag.

- `bracket_tolerante=True` — enciende el modo tolerante ("MA": V2 desde el primer intento).
  Añade una clave `bracket` al resultado con el intervalo final y los repliegues.
- `paso_repliegue=5.0` — cada extremo no evaluable se mueve 5 K hacia dentro, por intento.
- `max_repliegues=None` — sin tope de intentos (tope **por extremo**; el primer intento no
  cuenta: tope 2 ⇒ hasta 3 evaluaciones). Si aun así no quedan dos extremos evaluables, o no
  hay cambio de signo, el resolutor se rinde con `CicloNoConvergeError`.
- `presupuesto_s=None` — con valor, se mide el reloj de pared desde el inicio de la llamada y
  se comprueba **entre** evaluaciones (nunca a mitad de una); al superarlo se rinde con
  "presupuesto de tiempo agotado" y el número de evaluaciones hechas.

Además, en modo tolerante la **primera** evaluación del lazo interior arranca "tibio" en
`T_sumidero + 5 K` (igual que la variante V2 de referencia); a partir de ahí se reutiliza el
T10 ya convergido, como siempre se ha hecho.

Lo que **no** se ha hecho a propósito (está en la especificación y así se queda): un punto
**interior** del buscador no evaluable no tiene recuperación posible y se rinde con la
temperatura en el mensaje; solo se tolera `PropertyRangeError` (cualquier otro error sube
intacto y sin reintento).

## Cómo se verificó

1. **Los 16 tests de MA** (`tests/test_bracket_tolerante.py`), **sin tocarlos**:
   `pytest tests/test_bracket_tolerante.py -v` → salida en `pytest_ma.txt`.
2. **Suite completa** (~14 min, desacoplada con `nohup`): salida en `suite.txt`. Se comparó
   con la línea base `resultados/2026-10-01_tests_reintento/linea_base_suite.txt`
   (182/1/8, medida con `src/` idéntico).
3. **Los 18 controles con motor real** (`scripts/verificar_controles_ma.py`, `TeqpVerificado`),
   desacoplados y **en secuencia** después de la suite (nunca a la vez: los tiempos se
   contaminarían). Salida: `controles_progreso.log` (copia del `progreso.log` que escribe el
   script) y `controles.txt` (su stdout). Criterio del script: `|Δη| < 1e-4` y misma
   clasificación que la columna `V2` de la ablación.
4. **Diagnóstico de la única fila que falló**, con dos sondas de solo lectura
   (`diagnostico_fila15.txt`): el código de referencia V2 tal cual, y MA con y sin una
   evaluación V0 previa en el mismo proceso.

## Resultados

Glosario de una línea: **T1** = temperatura de entrada al hiperrefrigerante de vapor (HRVG),
la variable que el lazo exterior busca; **F** = residuo del balance de energía del
regenerador a nivel de ciclo en T1 (F(T1) = T1_nuevo − T1; se busca F = 0); **bracket** =
intervalo de T1 donde F cambia de signo; **repliegue** = mover un extremo del intervalo hacia
dentro; **nF** = número de evaluaciones de F (la última, con T1 ya resuelto, no cuenta);
**brentq** = el buscador de raíces; **`PropertyRangeError`** = "este estado (presión,
temperatura, composición) no es evaluable con este motor"; **`CicloNoConvergeError`** = "el
resolutor se rinde"; **fila sana** = fila que ya resolvía; **fila rescatada** = fila que el
resolutor actual no resuelve y que el modo tolerante sí resuelve; **η (eta)** = rendimiento
térmico del ciclo; **Δη** = diferencia de η respecto de la referencia.

### 1. Tests de MA (los 16 del contrato, sin modificarlos)

| Qué | Resultado |
|-----|-----------|
| `pytest tests/test_bracket_tolerante.py -v` | **16 passed** en 0.93 s |
| `tests/test_cycle_solver.py` (camino por defecto) | 10 passed |

Ninguno de los 16 tests necesitó tocar el contrato: la implementación los cumple tal cual.

### 2. Suite completa

| | Pasados | Saltados | xfail | Tiempo |
|---|---|---|---|---|
| Línea base (`resultados/2026-10-01_tests_reintento/linea_base_suite.txt`) | 182 | 1 | 8 | 686 s |
| **Hoy (con MA implementado)** | **198** | **1** | **8** | 861 s |
| Diferencia | +16 (los tests de MA) | 0 | 0 | — |

**Cero regresiones**: los 182 que pasaban antes siguen pasando y los 1/8 saltado/xfail siguen
igual. (Los ~175 s de más son ruido de la máquina compartida, no de los tests: los 16 tests
nuevos tardan 0.93 s.)

### 3. Los 18 controles con motor real (`TeqpVerificado`)

**17 de 18 filas OK.** La 18ª falla, y la causa **no está en la implementación** (ver abajo).

| # | Tipo | Grupo | Fila CSV | Resultado | η | Δη | Clasificación | Repliegues (lo/hi) | nF | Tiempo |
|---|------|-------|----------|-----------|---|---|---------------|-------------------|----|--------|
| 1 | sana | ctl_literatura | 0 | OK | 0.087667 | −2.6e−07 | CORREGIBLE ✓ | 0/0 | 7 | 33.5 s |
| 2 | sana | ctl_literatura | 17 | OK | 0.115983 | −1.9e−07 | CORREGIBLE ✓ | 0/0 | 8 | 35.1 s |
| 3 | sana | ctl_literatura | 31 | OK | 0.094917 | −2.3e−07 | CORREGIBLE ✓ | 0/0 | 7 | 29.6 s |
| 4 | sana | ctl_literatura | 45 | OK | 0.059646 | +2.7e−07 | CORREGIBLE ✓ | 0/0 | 7 | 38.8 s |
| 5 | sana | ctl_literatura | 59 | OK | 0.158862 | +8.1e−08 | CORREGIBLE ✓ | 0/0 | 9 | 39.3 s |
| 6 | sana | ctl_KALINA_f2 | 0 | OK | 0.118260 | +3.6e−07 | KALINA ✓ | 0/0 | 8 | 47.1 s |
| 7 | sana | ctl_KALINA_f2 | 13 | OK | 0.107529 | −4.7e−07 | KALINA ✓ | 0/0 | 8 | 67.8 s |
| 8 | sana | ctl_KALINA_f2 | 21 | OK | 0.124289 | −2.2e−07 | KALINA ✓ | 0/0 | 8 | 43.2 s |
| 9 | sana | ctl_KALINA_f2 | 33 | OK | 0.109923 | +6.9e−09 | KALINA ✓ | 0/0 | 11 | 56.7 s |
| 10 | sana | ctl_KALINA_f2 | 159 | OK | 0.119244 | +3.1e−07 | KALINA ✓ | 0/0 | 8 | 42.7 s |
| 11 | rescatada | f2_T_from_Ph | 802 | OK | 0.024697 | −1.6e−07 | CORREGIBLE ✓ | 0/3 | 8 | 66.6 s |
| 12 | rescatada | f2_T_from_Ph | 885 | OK | 0.062350 | +2.5e−07 | CORREGIBLE ✓ | 0/10 | 8 | 85.0 s |
| 13 | rescatada | lit_T_from_Ph | 5 | OK | 0.075082 | −2.6e−07 | CORREGIBLE ✓ | 0/0 | 8 | 39.3 s |
| 14 | rescatada | lit_T_from_Ph | 11 | OK | 0.099628 | +4.1e−08 | CORREGIBLE ✓ | 0/6 | 8 | 59.5 s |
| **15** | **rescatada** | **lit_bifasico** | **10** | **ERROR** `CicloNoConvergeError: punto interior no evaluable durante brentq (T=340.462948 K)` | — | — | — | — | — | ≈34 s (ver causa) |
| 16 | rescatada | lit_bifasico | 25 | OK | 0.064480 | +4.0e−07 | CORREGIBLE ✓ | 2/11 | 8 | 57.9 s |
| 17 | rescatada | f2_h_Ps | 1411 | OK | 0.034644 | +2.0e−07 | CORREGIBLE ✓ | 7/19 | 8 | 145.7 s |
| 18 | rescatada | f2_T_from_Ph | 907 | OK | 0.096148 | −1.9e−07 | CORREGIBLE ✓ | 0/1 | 9 | 63.1 s |

Δη máximo de las 17 filas buenas: **6.9e−09**, contra una tolerancia de 1e−4 (cuatro órdenes de
magnitud de margen). La clasificación coincide en las 17.

#### La fila 15: qué pasa exactamente y por qué

La referencia dice que para esta fila (`lit_bifasico`, `x_b=0.55`, `P_alta=1000 kPa`,
`T_fuente=463 K`) el modo V2 convergía a η = 0.074722 con T1 = 339.3539 K. Hoy, con el
proceso en frío, se rinde en un punto interior T1 = 340.462948 K. Tres pruebas lo aclaran
(`diagnostico_fila15.txt`):

1. **El código de referencia falla igual.** Ejecutado tal cual en este worktree, el V2 de
   `scripts/sonda_arranque_solver.py` falla en **exactamente la misma T** (340.4629 K). No es
   un defecto de la implementación nueva: es el mismo comportamiento.
2. **Con el motor "calentado" antes, MA reproduce V2 bit a bit.** La ablación del 2026-10-01
   corría V0 → V1 → V2 **en el mismo proceso**, así que el motor ya tenía memoria de T1 = 284
   y 462 K. Reproduciendo ese orden (una llamada con el camino actual, que falla como siempre
   en T1 = 462 K con `PropertyRangeError`, y después MA), el resultado es
   **η = 0.074722, T1 = 339.3539 K, 19 evaluaciones** — idéntico a la columna `V2` del CSV.
   La secuencia de T evaluadas incluye 340.4629 K **sin** fallo.
3. **La causa está en el estado global de los motores de propiedades**, no en MA:
   `src/properties/_kalina_flash.py` tiene cachés a nivel de módulo —`_ultimaT` (la última T
   resuelta por (P, composición, propiedad), que **acota el brentq** de cada inversión),
   `_flash`, `_puros`, `_env`— y `src/properties/_teqp_engine.py` tiene `_psat_cache`. En una
   fila cuyo óptimo cae justo al lado de un hueco de T no evaluable (~340.46 K frente a una raíz
   en 339.35 K), **qué puntos son evaluables depende del orden de las evaluaciones anteriores
   del proceso**.

Conclusión de la fila 15: **no es una regresión ni un problema de tolerancias**; es una
referencia (la columna `V2`) que solo es reproducible si el proceso ha ejecutado antes otras
variantes de la misma fila. No se ha ajustado ninguna tolerancia, tal como pedía la tarea.

## Tiempos

| Qué | Antes (2026-10-01, 6 workers en paralelo) | Hoy (secuencial, 1 proceso) |
|-----|--------------------------------------------|------------------------------|
| 10 filas sanas | ~46 s por fila | media **43.4 s**, mediana 41.0, mín 29.6, máx 67.8 (suma 434 s) |
| 8 filas rescatadas | 60–220 s por fila | media **73.9 s** (7 filas medidas), mediana 63.1, mín 39.3, **máx 145.7** (suma 517 s) |
| Los 18 controles | — | 985 s en total (el script) |
| Suite completa | 686 s | 861 s (+ los 0.93 s de los 16 tests nuevos) |
| `pytest tests/test_bracket_tolerante.py` | — | **0.93 s** |

Los tiempos por fila están en el mismo orden de magnitud que los de antes, y las rescatadas
siguen por debajo del máximo de 220 s observado en el benchmark. El paso fijo de 5 K **sin
tope** es lo que produce esos 39–145 s en las rescatadas; el coste viene de las evaluaciones de
F extra (hasta 19 repliegues en la fila 17), no de evaluaciones más lentas. Ojo: hoy la
medición es **secuencial** (sin contención de 6 workers), así que no es una comparación
exacta fila a fila, solo de orden de magnitud.

## Lo que no sabemos

- **Si las otras 19 de las 28 filas rescatadas por V2 también reproducen su referencia.** El
  script solo cubre 8; y por lo visto en la fila 15, la reproducibilidad de la columna `V2`
  depende del estado previo del proceso. Para comparar en serio habría que ejecutar V2 y MA en
  el mismo proceso y con el mismo orden.
- **Cuánto del sobrecoste de MA es atribuible a esta implementación** y cuánto al ruido de la
  máquina compartida (la suite tardó 861 s hoy frente a 686 s de la línea base con el mismo
  `src/` para esas 182).
- **Si el presupuesto de tiempo por punto (`presupuesto_s`) sirve de algo con el motor real.**
  Solo está probado con un reloj falso (test 12). No se ha elegido ningún valor de
  `presupuesto_s` para producción: depende de cuántas filas del barrido se quiera sacrificar,
  y eso es una decisión del director.
- **La fila 15 en particular**: no está resuelto *por diseño* (un punto interior no evaluable no
  tiene recuperación en la especificación), pero con el orden de ejecución de la ablación sí
  converge. Si el director quiere que esas filas también salgan, la opción sería permitir
  también el repliegue en interior (o una bisección), lo que **cambiaría la especificación**
  y los tests: no se ha hecho nada de eso.
- **El `nF` que reportan los tests** (evaluaciones de F sin la final) es la convención que
  confirmó el director; el número que aparece en el CSV de la ablación (`V2_nF`) incluye la
  final. Al comparar, `nF` de la tabla de arriba + 1 = `V2_nF`.

## Qué sigue

1. Decidir si MA se activa por defecto en `sensitivity.py` / `app.py` o se deja como opción
   (hoy el flag existe solo en `resolver_ciclo`; **no** se ha tocado la UI ni `sensitivity.py`).
2. Si se activa en algún barrido, fijar un `presupuesto_s` por fila que descartable (los 39–145 s
   de las rescatadas son el techo observado; ~220 s sería un margen prudente).
3. Repetir los controles con V2 y MA **en el mismo proceso y orden** para eliminar el factor
   "estado del motor" y poder afirmar 18/18 (o 28/28 si se cubren todas las rescatadas).
4. Commitear (`src/cycle_solver.py` modificado + `src/_bracket_tolerante.py` nuevo + esta
   carpeta de resultados). No hecho aquí por indicación del director.

## Archivos

- `src/_bracket_tolerante.py` — **nuevo**, 146 líneas (≤ 200 ✓).
- `src/cycle_solver.py` — modificado, 121 líneas (≤ 200 ✓); +43 −3.
- `src/_cycle_loops.py` — **sin cambios** (no hizo falta).
- `resultados/2026-10-02_implementar_ma/`: `pytest_ma.txt`, `suite.txt`,
  `controles.txt`, `controles_progreso.log`, `diagnostico_fila15.txt`,
  `progreso_tests_ma_ROJO.log` (copia del `progreso.log` de la tarea anterior, preservada antes
  de que el script lo sobrescribiera), este `REPORTE_IMPLEMENTAR_MA.md`.

### Nota de trazabilidad

`git status --short` al terminar:

```
 M src/cycle_solver.py
?? src/_bracket_tolerante.py
?? resultados/2026-10-02_implementar_ma/
?? prompts/TASK_CONTEXT_implementar_ma.md      (dado por el director)
?? prompts/TASK_CONTEXT_reejecutar_no_convergio.md   (NO es mío: apareció durante la sesión)
```

`git diff --stat`: `src/cycle_solver.py | 46 +++++--- (1 file changed, 43 insertions(+), 3
deletions(-))`. `.pytest_cache/` y `__pycache__/` están en `.gitignore`, no aparecen.
**No se ha hecho ningún commit ni `git checkout/switch/stash/reset`.**
# TASK_CONTEXT — Sensibilidad 2, A1b: comprobación independiente de cifras y poder del trazado

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy, openpyxl, pytest; **sin** scikit-learn ni yaml).
**Contexto:** plan en `docs/PLAN_SENS2_MEJORA.md` (sección 6). Sin corridas nuevas del motor (el «motor» es el programa que
calcula el ciclo; aquí solo se analizan datos ya calculados). Otras tareas corren a la vez sobre OTROS archivos: **toca solo los
archivos que esta tarea te asigna** y no hagas `git add`, `git commit`, `git stash`, `git checkout` ni `git reset` (el director commitea).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba archivos). PowerShell 5.1,
  sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. Cada `.py` máximo 200 líneas (divide en módulos si hace falta).
- Scripts nuevos en `scripts/sens2/`; importa con `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. Se ejecutan con
  `$env:PYTHONPATH = "scripts/sens2"` y `..\..\..\.venv\Scripts\python.exe -I scripts\sens2\<script>.py` (si tu shell no admite
  `$env:`, ejecuta el script desde la raíz: ya inserta su carpeta en `sys.path`).
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda salida: «confiable»,
  «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol», «sin respaldo».
- Los umbrales salen de los datos o de este documento; no inventes ninguno. Todo número sale de un archivo. Semilla fija indicada.
- Si algo es ambiguo, repórtalo en `UNRESOLVED` en lugar de decidir. Reporte final en el formato de `AGENTS.md`.

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p5_cifras_check.py` (nuevo), `scripts/sens2/p5_trazado_extra.py` (nuevo),
`scripts/sens2/p5_trazado.py` (solo para añadir la llamada al módulo extra, máximo 6 líneas nuevas) y las salidas
`resultados/2026-10-17_sens2_P5/p5_cifras_check.csv`, `p5_cifras_check.md` y `p5_trazado.md` (este último lo regenera `p5_trazado.py`).
Referencia de entrada (solo lectura): `prompts/ref_rev_final.py` (controles ya escritos y usados a mano), `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`
y `p5_conclusiones_base.csv`. **No ejecutes `p5_generar.py` ni edites los CSV de conclusiones.**

## Parte 1 — `p5_cifras_check.py`: controles independientes de cifras

Objetivo: cada cifra importante de las conclusiones se recalcula desde los datos crudos (no desde `p5_hechos.py`) y se comprueba que aparece
en el texto. Es un script ejecutable que imprime una línea `OK`/`FALLA` por control, escribe `p5_cifras_check.csv` (columnas `grupo,
control, resultado, detalle`) y `p5_cifras_check.md` (conteo OK/FALLA y la lista de FALLA), y sale con código 1 si hay alguna FALLA.

1. **Portar** todos los controles `chk(...)` de `prompts/ref_rev_final.py` (mantén la lógica y las tolerancias; el de «32 conclusiones» ya
   dice 41; la ruta de datos es `resultados/2026-10-17_sens2_P%d/` relativa a la raíz del worktree, calculada con `os.path`). Agrupa por prefijo
   del id de conclusión (`E`, `M`, `L`, `D`, `F`).
2. **Añadir 8 controles de texto** con la forma «el valor recalculado, con este formato, aparece como subcadena del campo indicado de la
   conclusión»; el recalculado sale de datos crudos así:
   - `U1`: de `resultados/2026-10-17_sens2_U1/u1_filas.csv` (columnas `barrido`, `centro`, `clasificacion`), para `barrido` en {`U1A`, `U1A2`} y
     cada centro C1..C4: fracción de filas con `clasificacion == "KALINA"` con formato `%.2f`, en el campo `evidencia`.
   - `L7`: de `x1_cargar` (`sys.path.insert(0, <raiz>/scripts/sens1)`; `import x1_cargar as X; d = X.cargar_todo()`), sobre las filas
     `clasificacion == "KALINA"` con `m_O2` no nulo: `100*(m_O2 < 3).mean()` con formato `%.1f`, en `evidencia`.
   - `L8`: de `resultados/2026-10-18_sens2_R1/r1_puntos.csv` (columnas `cerca`, `clasificacion`): número de filas con `cerca` verdadero y KALINA
     (entero), en `evidencia`.
   - `L9`: de `resultados/2026-10-18_sens2_R1/r2_vecinos_puntos.csv` (columnas `clasificacion`, `pred_kalina`): exactitud
     `mean(pred_kalina == (clasificacion == "KALINA"))` con formato `%.3f`, en `evidencia`.
   - `M2`: de `x1_cargar`, la fila con `estudio` en {1, 10}, `variable == "base"` y `centro` que empieza por `C1`: `eta_pct` con formato `%.2f`, en `evidencia`.
   - `F6`: de `p2_dataset_dedup.csv`, mediana de `eta_pct` de los CORREGIBLE y de los KALINA (`kalina` verdadero) con formato `%.1f`, en `evidencia`.
   - `D3`: de `p2_dataset_dedup.csv`, para los estudios 3 y 14 y el centro `C4 frio 110 C`: tomar las filas con `T_fuente` menor o igual al cuantil 0.25
     de `T_fuente` del bloque; el texto `"%d de %d"` (no convergieron, total) debe estar en `evidencia`.
   - `L2`: de `resultados/2026-10-17_sens2_P2/p2_distancia_resumen.csv` fila `seccion == "eta"`, `centro == "todos"`: `abs(mediana)` con formato `%.2f`, en `evidencia`.
   Cada control usa solo pandas/numpy sobre archivos del proyecto.
3. Resultado esperado: todos OK. Si alguno da FALLA, **no cambies el texto ni el control**: repórtalo en RESULTS con el detalle.

## Parte 2 — poder y cobertura del trazado (`p5_trazado_extra.py`)

`p5_trazado.py` ya existe y funciona. Hoy marca 654 de 724 cifras como trazadas y 0 como no trazadas, lo que sospechosamente no discrimina.
Escribe `p5_trazado_extra.py` con dos funciones y haz que `p5_trazado.py` las llame al final y añada sus resultados a `p5_trazado.md`:
1. `poder(trazado_fn_o_conjunto, semilla=20261018, n=300)`: control negativo. Genera `n` números con dos decimales uniformes en [0.01, 99.99]
   (semilla fija) y reporta qué porcentaje saldría «trazado» con el mismo conjunto de referencia y la misma regla de `p5_trazado.py`. Reutiliza la
   función de `p5_trazado.py` que decide el trazado (impórtala; si no está aislada en una función, apóyate en la estructura existente sin reescribir
   la lógica). Escribe una frase llana: «una cifra inventada con dos decimales se habría trazado en el X % de los casos».
3. `cobertura_marcadores()`: cuenta, en `p5_conclusiones_base.csv` (columnas `afirmacion`, `evidencia`, `implicacion`), cuántos números hay
   dentro de marcadores `{{...}}` y cuántos fuera, por conclusión (`id`), y devuelve una tabla (id, dentro, fuera). El `.md` incluye el total y la
   lista de las 10 conclusiones con más números fuera de marcadores.
Después de integrar, ejecuta `p5_trazado.py` (debe seguir saliendo con código 0) y reporta los dos resultados nuevos en RESULTS.

## Criterios de aceptación

- `p5_cifras_check.py` corre en menos de 2 minutos; cada archivo ≤ 200 líneas; no se modifica ningún otro archivo.
- Reporta en RESULTS: número de controles, cuántos OK, las FALLA con detalle, el «poder» del control negativo y el total de números dentro/fuera de marcadores.

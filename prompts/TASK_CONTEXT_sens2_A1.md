# TASK_CONTEXT — Sensibilidad 2, A1: regla de confianza v2 y trazado de cifras

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p5_confianza.py`, `resultados/2026-10-17_sens2_P5/p5_evidencia.csv`
(solo la columna `robusto_diseno`), `scripts/sens2/p5_trazado.py` (nuevo), `resultados/2026-10-17_sens2_P5/p5_trazado_permitidos.csv` (nuevo)
y las salidas `resultados/2026-10-17_sens2_P5/p5_trazado.csv` y `p5_trazado.md`. Para regenerar `p5_conclusiones.csv` ejecuta
`scripts/sens2/p5_generar.py` (no lo edites a mano ni toques `p5_conclusiones_base.csv`).

## Parte 1 — Regla v2 (`p5_confianza.py`)

1. En `p5_confianza.py` el conjunto `OK` pasa a `{"si", "acotado", "na"}`. Documenta en el docstring el nuevo valor de `robusto_diseno`:
   `acotado` = el enunciado de la conclusión limita su alcance a la rebanada o escenario donde se midió (por ejemplo «con las demás
   variables en el centro» o «con tolerancias supuestas») y la cifra vale en esa rebanada; `parcial` = se enuncia en general pero
   depende del diseño de muestreo. Solo `si`, `acotado` y `na` permiten Alta. No cambies nada más de la regla.
2. En `p5_evidencia.csv` cambia `robusto_diseno` de `parcial` a `acotado` en exactamente estos ids: D2, D3, D5, D6, D7, D8, F4, F6,
   L7, L9, U1, U2, U3, U4. No cambies ninguna otra celda ni otra fila.
3. Ejecuta `scripts/sens2/p5_generar.py` y reporta el reparto de `confianza` (Alta, Media, Baja) y las filas Baja con su
   `criterio_confianza`. No ajustes la regla para que salga un reparto concreto.

## Parte 2 — Trazado de cifras (`p5_trazado.py`)

Objetivo: detectar cifras de las conclusiones que no salen de ningún CSV de resultados (cifras inventadas o desactualizadas).

Entrada: `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`, columnas `afirmacion`, `evidencia`, `implicacion` (una fila por `id`).

1. **Extracción de números.** Expresión regular que capture: enteros y decimales con punto (`14.53`, `0.047`, `-0.64`); miles con espacio
   (`2 619`, `3 921`); ignora un número si está pegado a una letra o guion bajo (`C1`, `P5`, `D8`, `N10-C3-0016`, `m_O2`, `T9`, `x_b`,
   `O2`); ignora el número de un rango de ids (`D1 a D6` no tiene números sueltos). Para cada número guarda `numero` (texto tal cual),
   `decimales` (cuántos dígitos tras el punto), `valor` (float; sin espacios de miles) y `campo`.
2. **Conjunto de referencia.** Con `pandas`, lee TODAS las columnas numéricas de cada `.csv` de estas carpetas (recursivo en cada una):
   `resultados/2026-10-17_sens2_P1`, `P2`, `P3`, `P4`, `resultados/2026-10-17_sens2_U1`, `resultados/2026-10-18_sens2_R1`.
   Añade además los valores del diccionario que devuelve `p5_hechos.hechos()` (importa `from p5_hechos import hechos`; cada valor
   numérico). Para cada valor `v` finito guarda, por cada d en 0..4: `round(v, d)`, `round(abs(v), d)` y `round(100*v, d)` (las fracciones
   aparecen como porcentaje) y `round(100*(1-v), d)`. Construye `dict[d] -> dict[valor_redondeado -> primera fuente "archivo:columna"]`.
   Usa operaciones vectorizadas; hay archivos de ~4 000 filas.
3. **Trazado.** Un número está `trazado = "si"` si su `valor` redondeado a sus `decimales` está en el conjunto de referencia de esos
   decimales (usa tolerancia exacta de redondeo, sin tolerancias adicionales), o aparece en `p5_trazado_permitidos.csv`. Si no, `"no"`.
   Para decimales > 4 usa 4. Para números enteros pequeños (valor entero con |valor| < 10 y 0 decimales) marca `"trivial"` y no los
   cuentes como no trazados.
4. **Lista de permitidos** `p5_trazado_permitidos.csv` (columnas `valor,motivo`): créala con estas constantes de diseño y límites que
   las conclusiones citan: 0.90, 420, 0.95, 0.85, 0.75, 0.7, 5, 3, 1, 0.02, 0.05, 0.15, 0.10, 0.80, 0.40, 3300, 690, 394.15, 403, 423.15,
   383.15, 3000, 563.64, 3150, 950, 3880, 910, 278.15, 300.15, 280.5, 282.5, 121, 150, 110, 95, 5000, 600, 4000, 2000. Motivo común:
   «constante de diseño o límite del criterio, citada tal cual». (Son valores de entrada, no resultados.)
5. **Salidas.** `p5_trazado.csv` con columnas `id, campo, numero, decimales, trazado, fuente`; `p5_trazado.md` con: total de números,
   trazados, triviales, no trazados, porcentaje de trazados, y la tabla de los no trazados (id, campo, numero, contexto de 40
   caracteres alrededor). El script imprime las mismas cifras y sale con código 0 siempre (es un informe, no una prueba).
6. **Prueba.** Ejecuta el script sobre las conclusiones actuales y reporta en RESULTS el total, los trazados y la lista de los
   primeros 60 no trazados. **No corrijas los textos**: el director decidirá.

## Criterios de aceptación

- Los tres scripts/archivos cumplen el límite de 200 líneas y no tocan otros archivos.
- `p5_generar.py` corre sin error tras tu cambio.
- `p5_trazado.py` corre en menos de 2 minutos.

# TASK_CONTEXT — Sensibilidad 2, B2: control de palabras fuertes y cifras de los documentos (sin motor)

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy, openpyxl, pytest; **sin** scikit-learn ni yaml).
**Contexto:** plan en `docs/PLAN_SENS2_MEJORA.md`. Sin corridas del motor (solo se leen textos y CSV ya existentes). Otra tarea (B1) corre a la vez
sobre OTROS archivos: **toca solo los archivos asignados** y no hagas `git add`, `git commit`, `git stash`, `git checkout` ni `git reset` (el director commitea).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba archivos). PowerShell 5.1,
  sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. Cada `.py` máximo 200 líneas.
- Scripts nuevos en `scripts/sens2/`; importa con `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. Ejecuta desde la raíz:
  `..\..\..\.venv\Scripts\python.exe scripts\sens2\<script>.py`.
- **Terminología:** prohibido en toda salida (propia, no en lo que citas del documento): «confiable», «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol», «sin respaldo».
- Los umbrales salen de este documento. Si algo es ambiguo, repórtalo en `UNRESOLVED`. Reporte final en el formato de `AGENTS.md`.

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p5_lint_texto.py` (nuevo), `scripts/sens2/p5_docs_check.py` (nuevo) y las salidas en
`resultados/2026-10-17_sens2_P5/`: `p5_lint_texto.csv`, `p5_lint_texto.md`, `p5_docs_check.csv`, `p5_docs_check.md`.
**No modifiques** ningún texto, CSV de conclusiones ni documento: estos scripts solo leen e informan; el director corrige.

## Parte 1 — `p5_lint_texto.py`: palabras fuertes

Lee `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv` (columnas de texto: `afirmacion`, `evidencia`, `implicacion`, `alcance` si existe; usa `p5_trazado.CAMPOS` si lo prefieres),
`docs/INFORME_SENS2.md` y `docs/VALIDACION_SENS2.md`. Busca (sin distinguir mayúsculas, como palabra completa) estas palabras fuertes:
`solo`, `unico`, `unica`, `única`, `único`, `siempre`, `nunca`, `todos`, `todas`, `ninguno`, `ninguna`, `demuestra`, `prueba que`, `garantiza`, `confirma`, `definitivo`, `claramente`, `evidentemente`, `se debe a`, `causa`.
Por cada aparición escribe una fila: `archivo, id (conclusion o numero de linea), campo, palabra, contexto` (60 caracteres a cada lado). Salidas: `p5_lint_texto.csv`
y `p5_lint_texto.md` con conteo por palabra y por archivo y la lista agrupada por palabra para revisión manual. Es informativo: sale con código 0. Imprime el resumen.

## Parte 2 — `p5_docs_check.py`: cifras de los documentos frente a los CSV

Para `docs/INFORME_SENS2.md` y `docs/VALIDACION_SENS2.md`: extrae todos los números con decimales o con `%` (reutiliza las funciones de `scripts/sens2/p5_trazado.py`: `import p5_trazado as T`;
lee ese archivo para ver `extraer`, `clasificar`, `permitidos`, `_agregar` y cómo `scripts/sens2/p5_trazado_fuente.py` arma la referencia; si `extraer` pide un `campo`, pásale el nombre del archivo).
Compara cada número contra: (a) `p5_conclusiones.csv` (todo su texto), (b) todos los CSV de `resultados/2026-10-17_sens2_P*` y `resultados/2026-10-18_sens2_*`, (c) `p5_trazado_permitidos.csv`.
Escribe `p5_docs_check.csv` (`archivo, linea, numero, estado` con estado `en_conclusiones` | `en_csv` | `permitido` | `trivial` | `no_trazado`, y `contexto`) y `p5_docs_check.md` con el conteo por estado y
la lista de los `no_trazado` con su contexto. Esta parte SÍ sale con código 1 si hay `no_trazado` (la lista es la que el director revisará), pero imprime siempre el resumen completo antes de salir.

## Aceptación

Ambos scripts corren en menos de 2 minutos; cada archivo ≤ 200 líneas; reporta en RESULTS el conteo por palabra fuerte (top 10) y el conteo por estado de las cifras de los documentos, con la lista de `no_trazado`.

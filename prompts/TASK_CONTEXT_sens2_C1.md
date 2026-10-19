# TASK_CONTEXT — Sensibilidad 2, C1: detector de frases de estado caducas y chequeo cruzado entre conclusiones (sin motor)

**Fecha:** 2026-10-19 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa, bash):** `../../../.venv/Scripts/python.exe` (numpy, pandas, scipy, openpyxl, pytest; **sin** scikit-learn ni yaml).
**Contexto:** análisis de datos ya calculados; **sin corridas del motor**. Otras tareas del director corren a la vez sobre OTROS archivos: **toca solo
los archivos que esta tarea te asigna** y no hagas `git add`, `git commit`, `git stash`, `git checkout` ni `git reset` (el director commitea).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.** El shell es bash: rutas con `/`.
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings ni `python -c` que escriba archivos). Solo ASCII en los `print`. `timeout=1800000`.
  Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/`; en cada uno `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`.
  Ejecuta desde la raíz del worktree: `../../../.venv/Scripts/python.exe scripts/sens2/<script>.py`.
- **Terminología:** prohibido en tu salida: «confiable», «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol», «sin respaldo».
- Los umbrales salen de este documento. Si algo es ambiguo, repórtalo en `UNRESOLVED`. Reporte final en el formato de `AGENTS.md`.

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p5_lint_estado.py` (nuevo), `scripts/sens2/p5_cruce.py` (nuevo) y sus salidas en
`resultados/2026-10-17_sens2_P5/`: `p5_lint_estado.csv`, `p5_lint_estado.md`, `p5_cruce.csv`, `p5_cruce.md`. **No modifiques** ningún documento ni CSV de conclusiones.

## Parte 1 — `p5_lint_estado.py`: frases de estado caducas

Lee `docs/INFORME_SENS2.md`, `docs/VALIDACION_SENS2.md`, `docs/PLAN_SENS2_MEJORA.md` y la columna de texto (`afirmacion`, `evidencia`, `implicacion`) de
`resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`. En `PLAN_SENS2_MEJORA.md` **ignora** las líneas entre el encabezado `## 6.` y el encabezado `## 7.` (sección histórica).
Busca (sin distinguir mayúsculas) estas frases de estado: `queda pendiente`, `quedan pendientes`, `siguen abiertos`, `sigue abierto`, `pendiente de`, `no se corrió`,
`no se corrio`, `sin hacer`, `por hacer`, `etapa C`, `requiere el motor`, `requieren el motor`, `necesita el motor`, `falta el motor`, `aún no`, `todavía no`, `sin commit`.
Por cada aparición una fila: `archivo, linea (o id de conclusion y campo), frase, contexto (80 caracteres a cada lado), tema, resultado_existente`.
`tema` y `resultado_existente` se asignan así: si el contexto contiene alguna de las palabras `reintent`, `piso`, `densidad`, `caudal`, `bomba`, `simétric`, `simetric`,
`T_fuente`, `optimiz`, `NO_CONVERGIO`, el tema es la primera que coincida; `resultado_existente` = `si` cuando existe alguno de estos archivos según el tema:
reintent/NO_CONVERGIO → `resultados/2026-10-18_sens2_F1/p6_reintento_nc.csv`; piso → `p6_pisos25.csv`; densidad/caudal/bomba → `p6_dens.csv`; simétric → `p6_sim.csv`;
T_fuente/optimiz → `p6_opt_T.csv` (todos en `resultados/2026-10-18_sens2_F1/`); si no hay tema, `-`. Una frase con `resultado_existente = si` es sospechosa de estar caduca.
Salidas: `p5_lint_estado.csv` y `p5_lint_estado.md` (conteo por frase y por archivo, y lista de las sospechosas con su contexto). Informativo: sale con código 0. Imprime el resumen.

## Parte 2 — `p5_cruce.py`: mismo dato, distinto valor entre conclusiones

Lee `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv` (columnas `id`, `afirmacion`, `evidencia`, `implicacion`). Para cada conclusión y cada campo extrae los números con unidad
mediante la expresión regular `(-?\d+(?:[.,]\d+)?)\s*(%|kPa|K|°C|kJ/kg|pp|puntos|kW|L/s|kg/m³|m)(?![A-Za-z])` y toma como **clave** el par (unidad, las dos palabras que preceden
inmediatamente al número, en minúsculas y sin signos de puntuación). Agrupa por clave entre conclusiones DISTINTAS. Un grupo es **candidato a contradicción** si tiene al menos 2 conclusiones
distintas y al menos 2 valores distintos (comparados redondeados a 2 decimales). Salidas: `p5_cruce.csv` (una fila por aparición: `clave, unidad, valor, id, campo, contexto` con 60 caracteres
de contexto, ordenada por clave) y `p5_cruce.md` (lista de los candidatos con sus apariciones; es una lista para revisión manual, un candidato no es un error). Sale con código 0. Imprime el número de claves, de candidatos y los 15 primeros.

## Aceptación

Ambos scripts corren en menos de 1 minuto; cada archivo ≤ 200 líneas; reporta en RESULTS el conteo por frase de la parte 1 (con las sospechosas) y el número de candidatos de la parte 2 con los 10 primeros.

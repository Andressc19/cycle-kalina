# TASK_CONTEXT — Sensibilidad 2, A5: orquestador, pruebas, supuestos y estadísticas de m_O2

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/make_sens2.py` (nuevo), `scripts/sens2/sens2_supuestos.json` (nuevo),
`scripts/sens2/p6_mO2.py` (nuevo), `tests/test_sens2_libro.py`, `tests/test_sens2_cifras.py`, `tests/test_sens2_r1.py` (nuevos), y
añadir (solo añadir al final) líneas a `.gitignore`. Salidas en `resultados/2026-10-18_sens2_F1/` (ya existe).

## Parte 1 — `p6_mO2.py`

Con `import x1_cargar as X` (agrega `sys.path.insert(0, "scripts/sens1")`), `d = X.cargar_todo()`; toma las filas con `clasificacion == "KALINA"`
y `m_O2` no nulo. Escribe `resultados/2026-10-18_sens2_F1/p6_mO2_estadisticas.csv` con columnas `centro, n, p_menor_1K, p_menor_3K,
p_menor_5K` (porcentajes de 0 a 100) para `todos` y para cada centro cuyo nombre de `centro` empieza por `C1`, `C2`, `C3`, `C4`
(filas separadas); no cambies la definición. Imprime la tabla. Debe reproducir, para `todos`, 2.6, 7.0 y 13.2 % (n = 2243).

## Parte 2 — `sens2_supuestos.json`

Un solo JSON con todos los supuestos y umbrales del análisis, cada uno con `valor` y `donde` (el módulo que lo define). Lee los valores
de los módulos, no los inventes: `semilla` (p3_comun.SEMILLA), `n_boot` (p3_comun.N_BOOT), `n_perm` (p3_comun.N_PERM),
`tolerancias_u1` (u1_puntos.TOL), `escenarios_u1` (u1_puntos.ESCENARIOS), `cercania_r1` (r1_filtro.CERCANO), `cobertura_r1` (r1_filtro.COBERTURA),
`tolerancia_eficiencias_r2` (r2_eficiencias.TOL_EF), `k_vecinos` (r2_vecinos.K), `banda_modelo_pp` (u1_analisis.BANDA_MODELO). Añade con
valor fijo y `donde: "docs/PLAN_SENS2_MEJORA.md"`: `semilla_f1` 20261018, `q_fdr` 0.05, `n_permutaciones_f1` 500, `n_min_confianza` 30, `auc_minimo` 0.8,
`procedencia`: {"u1_808_puntos": "corridos por el director con u1_corrida.py (OpenCode no arrancó)", "r1": "OpenCode con vigilante; r2: director"}.
Genera el JSON desde un script `scripts/sens2/make_supuestos.py` (nuevo, ≤ 80 líneas) que lo escribe; ejecútalo.

## Parte 3 — `make_sens2.py` (orquestador)

CLI con `argparse`: `--lista` (imprime los pasos), `--solo NOMBRE` (varios permitidos), `--desde NOMBRE`, `--todo` (incluye P1 a P4, U1 y R1), `--registro`
(ruta del JSON de registro; por defecto `resultados/2026-10-18_sens2_F1/make_sens2_registro.json`). Pasos, en orden (nombre = archivo sin `.py`):
- Base (siempre): `p5_generar`, `p6_mO2`, `p6_nulo`, `p6_nc`, `p6_pareado`, `p6_equipos_diseno`, `p6_potencia_u1`, `p6_fronteras_ic`, `p6_superficies_cv`,
  `p5_trazado`, `s2_construir`, `s2_verificar`, `s2_informe`, `s2_figuras`, `s2_informe_pdf`.
- Con `--todo`, antes de los anteriores: `p1_dataset`, `p1_existencia`, `p1_fronteras`, `p1_reglas`, `p2_comparacion`, `p2_violaciones`,
  `p2_distancia`, `p2_robustez`, `p3_indices`, `p3_elasticidad`, `p3_interaccion`, `p3_resumen`, `p4_envolventes`, `p4_dependencias`, `p4_bandas`,
  `u1_analisis`, `r1_filtro`, `r1_contraste`, `r2_eficiencias`, `r2_vecinos`, `r2_agregado`.
- Cada paso: `subprocess.run([sys.executable, "-I", ruta], env con PYTHONPATH=scripts/sens2 y PYTHONIOENCODING=utf-8, cwd=raíz del worktree)`.
  Si el script **no existe**, salta con aviso «no existe todavía» (no es fallo). Si falla (código ≠ 0), detén y sal con ese código.
- Registro JSON: para cada paso `{nombre, estado, segundos, codigo}`; además `commit` (`git rev-parse HEAD`), versión de Python, numpy, pandas,
  scipy, openpyxl, y el sha256 de `resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv` y de `resultados/2026-10-17_sens2_U1/u1_filas.csv`.
- Al final de los pasos base, ejecuta `pytest -q tests/test_sens2_libro.py tests/test_sens2_cifras.py tests/test_sens2_r1.py -p no:cacheprovider`
  (como paso `pruebas`) salvo `--sin-pruebas`.
- **Para esta tarea ejecuta solo `--lista` y `--solo p6_mO2 p5_generar`** (no corras los pasos pesados ni `--todo`).

## Parte 4 — Pruebas (pytest, solo lectura)

Tres archivos en `tests/`, cada uno con funciones `test_*` que NO escriben archivos del proyecto (usa `tmp_path`):
- `test_sens2_libro.py`: `datos/Kalina_anal_sensible_2.xlsx` abre con `openpyxl`; la primera hoja es `LEEME`; hay al menos 23 hojas;
  existen las hojas `F5 Incertidumbre` y `F6 Respaldo libro viejo`; ninguna celda de texto contiene las palabras prohibidas del encabezado
  (insensible a mayúsculas; excluye la hoja `LEEME` solo para la lista de palabras prohibidas que ella misma define si la contiene);
  el número de filas de datos de la hoja `Conclusion consolidada` que empiezan por un id de conclusión es igual al número de filas de
  `p5_conclusiones.csv` (cuenta celdas de la primera columna que coinciden con algún `id` del CSV).
- `test_sens2_cifras.py`: `p5_conclusiones.csv` no contiene `{{`; `confianza` solo toma `Alta`, `Media`, `Baja`; los `id` son únicos y
  coinciden con los de `p5_evidencia.csv`; los valores de `p5_hechos.hechos()` clave `u1p.C1.p_kalina` (0.469 ± 0.001), `mo2.todos.p3` (7.0 ± 0.1),
  `l8.n` (213) y `r2.agr.evaluaciones_ventanas_una_vez` (665) son los esperados; `p5_generar.rellenar` aplicado a todas las plantillas de
  `p5_conclusiones_base.csv` reproduce exactamente `afirmacion`, `evidencia` e `implicacion` de `p5_conclusiones.csv`.
- `test_sens2_r1.py`: `r1_cascada.csv` es monótona no creciente en `n_unicos`; `r1_puntos.csv` no comparte ninguna entrada (10 variables
  redondeadas a 4 decimales) con `dataset_dedup()`; todo punto de `r1_puntos.csv` tiene `dist` ≥ 0 y `cerca == (dist <= 0.15)`.
Ejecuta `..\..\..\.venv\Scripts\python.exe -m pytest -q tests/test_sens2_libro.py tests/test_sens2_cifras.py tests/test_sens2_r1.py -p no:cacheprovider`
(solo esos tres archivos; **no** corras toda la carpeta `tests/`). Si una prueba falla por un dato real, no cambies datos: repórtalo.

## Parte 5 — `.gitignore`

Añade al final las líneas `~$*.xlsx`, `__pycache__/` y `*.log` solo si no están ya.

## Criterios de aceptación

- `make_sens2.py --lista` imprime los pasos; `--solo p6_mO2 p5_generar` los corre y crea el registro; las 3 pruebas pasan.
- Cada archivo ≤ 200 líneas; no se modifica ningún archivo existente salvo `.gitignore` (solo añadir).

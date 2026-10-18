# TASK_CONTEXT — Sensibilidad 2, A1c: pruebas de coherencia del libro y comprobación independiente de F1 a F3

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

**Archivos que puedes tocar (y solo estos):** `tests/test_sens2_libro.py` (añadir pruebas; no borres las existentes), `tests/test_sens2_cifras.py`
(solo la prueba del conjunto de valores de `confianza`, ver abajo), `scripts/sens2/p5_cifras_check_c.py` (nuevo) y sus salidas
`resultados/2026-10-17_sens2_P5/p5_cifras_check_c.csv` y `.md`. **No edites** `p5_cifras_check.py` ni `p5_cifras_check_b.py`: el director añadirá la llamada.

## Parte 1 — pruebas nuevas en `tests/test_sens2_libro.py` (solo lectura)

Usa `zipfile` para contar los gráficos del libro `datos/Kalina_anal_sensible_2.xlsx` (archivos `xl/charts/chart*.xml`; cuenta solo los que
coinciden con `^xl/charts/chart\d+\.xml$`) y `openpyxl` para contar hojas.
1. `test_informe_y_validacion_dicen_hojas_y_graficos_reales`: el texto `"(%d hojas, %d gráficos)" % (n_hojas, n_graficos)` debe aparecer en
   `docs/INFORME_SENS2.md` y en `docs/VALIDACION_SENS2.md` (lee con `encoding="utf-8"`).
2. `test_confianza_tiene_los_41_ids`: en la hoja `Confianza`, recoge los valores de la columna A que coinciden con algún `id` de
   `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`; deben ser exactamente los ids del CSV (41, sin repetidos ni faltantes).
3. `test_toda_hoja_esta_en_la_guia_del_leeme`: cada nombre de hoja (salvo `LEEME`) aparece como texto exacto en alguna celda de la columna A de la hoja
   `LEEME`, y cada texto de la columna A de `LEEME` que sea nombre de hoja existe.
4. `test_confianza_coincide_con_la_regla`: para cada fila de `p5_evidencia.csv` calcula `from p5_confianza import regla` (agrega
   `sys.path.insert(0, <raiz>/scripts/sens2)`), y comprueba que la confianza del CSV de conclusiones coincide (`regla(fila)[0]`).
En `tests/test_sens2_cifras.py` el conjunto permitido de `confianza` pasa a `{"Alta", "Media", "Baja", "No aplica"}`.

## Parte 2 — `p5_cifras_check_c.py`: recalcular de forma independiente las variables «distinguibles»

Entrada: `resultados/2026-10-18_sens2_F1/p6_nulo_perm.csv` (columnas `caja, bloque, respuesta, variable, tipo, metodo, familia_metodo, n, obs, p_perm`).
1. Solo filas con `tipo == "real"`. Para cada `(bloque, respuesta)`: calcula los q-valores de Benjamini-Hochberg de TODOS los `p_perm` de ese grupo
   (implementación propia: ordena, `p*m/rango`, mínimos acumulados de atrás hacia delante, tope 1). Una variable es distinguible si tiene `q < 0.05` en al menos
   2 métodos del grupo.
2. Compara con el texto: `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`, campo `evidencia`. Para las respuestas `Y2 eta (%)` → conclusión `F1`, `Y3 W_net/m_b` → `F2`,
   `Y1 KALINA (total)` → `F3`; el texto contiene fragmentos `C1 <lista>; C2 <lista>; C3 <lista>; C4 <lista>` (listas de variables separadas por coma, tras
   la frase «son distinguibles»; el bloque `E3 C1 Husavik` es C1, `E3 C2 ancla A*` es C2, `E14 C3 caliente 150 C` es C3, `E14 C4 frio 110 C` es C4). Para cada bloque comprueba que el
   conjunto de variables recalculado es igual al de la lista del texto (extrae la lista con una expresión regular sobre el fragmento que sigue a `C<k> ` hasta el siguiente `;` o
   `.`; ten en cuenta que puede haber más de una aparición de `C1 `; usa la que viene después de la frase «distinguibles» o «son distinguibles»).
3. Además cuenta, para cada respuesta, cuántas variables son distinguibles con umbral de 1 método, 2 métodos y 3 métodos (suma de los 4 bloques) y escribe esa tabla en el `.md`
   (sirve para mostrar qué tan sensible es la regla de «al menos 2 métodos»).
4. Salidas: `p5_cifras_check_c.csv` (columnas `control, resultado, detalle`; un control por conclusión y bloque: 12 controles) y `p5_cifras_check_c.md` (OK/FALLA, tabla de umbrales).
   Sale con código 1 si hay FALLA. Ejecuta el script y reporta en RESULTS el número de controles OK y la tabla de umbrales; si hay FALLA **no cambies nada**, repórtala con detalle.

## Ejecución y aceptación

`..\..\..\.venv\Scripts\python.exe -I scripts\sens2\p5_cifras_check_c.py` y
`..\..\..\.venv\Scripts\python.exe -m pytest -q tests/test_sens2_libro.py tests/test_sens2_cifras.py -p no:cacheprovider`.
Las pruebas 1 a 3 pueden FALLAR hoy (el informe y el libro están cambiando); repórtalo con el mensaje de error, no cambies los datos ni el libro. Cada archivo ≤ 200 líneas.

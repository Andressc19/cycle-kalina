# TASK_CONTEXT — Sensibilidad 2, A2b: pareado, equipos por diseño y potencia de U1

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p6_pareado.py`, `scripts/sens2/p6_equipos_diseno.py`,
`scripts/sens2/p6_potencia_u1.py` (nuevos) y sus salidas en `resultados/2026-10-18_sens2_F1/` (ya existe): `p6_pareado.csv`, `p6_pareado.md`,
`p6_equipos_diseno.csv`, `p6_equipos_diseno.md`, `p6_potencia_u1.csv`, `p6_potencia_u1.md`.

## Parte 1 — Comparación pareada (`p6_pareado.py`)

Datos: `resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv` (3 663 filas; columnas `id_punto, estudio, centro, clasificacion, kalina, eta_pct,
wnet_mb, viol_O1, viol_O2` y las 10 variables `T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond`).
Bloques con centro: `C1 Husavik`, `C2 ancla A*`, `C3 caliente 150 C`, `C4 frio 110 C` (ignora `Sin centro (muestreo o malla)`).
1. Normaliza cada una de las 10 variables a [0, 1] con el mínimo y el máximo del dataset completo. Para cada CORREGIBLE busca el KALINA
   más cercano por distancia L1 (suma de diferencias absolutas) en dos variantes: `mismo_centro` (cualquier KALINA del mismo centro) y
   `mismo_centro_y_diseno` (además del mismo diseño, donde diseño = `LHS` si `estudio` está en {3, 14} y `otros` si no). Usa numpy por bloques
   de 200 filas; no bucles O(n²) en Python puro.
2. Para cada par con η finito en ambos: `d_eta = eta_vecino − eta_corregible` y `d_wnet = wnet_mb_vecino − wnet_mb_corregible`. Violación dominante:
   `O2` si `viol_O2 >= viol_O1` y `viol_O2 > 0`, `O1` si `viol_O1 > viol_O2`, `otra` en otro caso.
3. Resúmenes (grupos: `todos`, cada centro, cada diseño del CORREGIBLE, cada violación dominante): n, mediana y media de `d_eta` y `d_wnet`,
   con IC 95 % por bootstrap percentil (1 000 remuestreos, semilla 20261018) de la mediana y de la media. Salida `p6_pareado.csv` con columnas
   `variante, grupo, variable, n, mediana, ic_med_lo, ic_med_hi, media, ic_media_lo, ic_media_hi`, y `p6_pareado.md` con una tabla de
   `d_eta` por grupo en lenguaje llano.
4. **Control:** la variante `mismo_centro`, grupo `todos` (sin «sin centro»), debe dar una mediana de `d_eta` dentro de ±0.05 de −0.64
   (el valor de `resultados/2026-10-17_sens2_P2/p2_distancia_resumen.csv` fila `seccion == "eta"`, `centro == "todos"`). Si no, repórtalo.

## Parte 2 — Envolventes de equipos por diseño (`p6_equipos_diseno.py`)

Usa `import p4_comun as c` (en `scripts/sens2`): `c.cargar()` devuelve el DataFrame con las cantidades derivadas por equipo (columnas de
`c.CANTIDADES`, además de `centro`, `estudio`, `kalina`, `eta_pct`); `c.mascara(df, c.REF_TOTAL)` selecciona KALINA (total).
Para cada cantidad de `c.CANTIDADES` y cada ámbito (`todos` y cada uno de los 4 centros con nombre, sin «Sin centro»), calcula P5, P50 y P95 en
tres conjuntos de los KALINA (total):
- `a_todos`: todos los KALINA (reproduce `p4_envolventes.csv`; compara y reporta si P50 difiere más de 1e-6 en alguna fila);
- `b_solo_LHS`: solo `estudio` en {3, 14};
- `c_peso_igual`: todos los KALINA con peso `1 / n(centro, estudio)` (cada combinación centro-estudio aporta lo mismo); percentil ponderado
  = valor donde la suma acumulada de pesos, tras ordenar por valor, alcanza p/100 del total (interpolación no necesaria).
Calcula `desplazamiento_b = (p50_b − p50_a) / (p95_a − p5_a)` y `desplazamiento_c` igual; marca `sensible = "si"` si algún
|desplazamiento| > 0.15. Si `p95_a == p5_a`, deja vacío. Salida `p6_equipos_diseno.csv` con columnas `ambito, cantidad, conjunto, n, p5, p50, p95,
desplazamiento, sensible` y `p6_equipos_diseno.md` con la lista de cantidades sensibles por ámbito y cuántas de las cantidades de equipo
(`c.CANT_DEP`) lo son.

## Parte 3 — Potencia de U1 (`p6_potencia_u1.py`)

Entradas: `resultados/2026-10-17_sens2_U1/u1_resumen.csv` (columnas `escenario, centro, n, n_kalina, p_kalina, p_lo, p_hi`; escenarios
`U1A`, `U1A2`, `U1Ap` (lotes 1+2 combinados), `U1B`, `U1C`). Por escenario y centro: error típico `sqrt(p(1−p)/n)`, ancho del IC
de Wilson (`p_hi − p_lo`), número de puntos necesario para una semiamplitud de IC de ±0.05 y de ±0.10 con la `p` observada
(`n = 1.96² · p(1−p) / h²`, redondeo hacia arriba) y con el peor caso `p = 0.5`. Para la comparación entre lotes (`U1A` frente a `U1A2` en cada centro):
diferencia de proporciones, estadístico z con `sqrt(p̂(1−p̂)(2/n))` (p̂ combinada; si p̂ es 0 o 1 deja z vacío) y la diferencia mínima detectable
con potencia 80 % y nivel 5 % (`2.8 · sqrt(2 · p̂(1−p̂)/n)`, con p̂ = 0.5 para el peor caso). Salida `p6_potencia_u1.csv` (dos tablas
apiladas con una columna `tabla` = `precision` o `entre_lotes`) y `p6_potencia_u1.md` con una frase llana: qué diferencia entre lotes no se
habría detectado.

## Criterios de aceptación

- Los tres scripts corren en menos de 5 minutos cada uno, respetan 200 líneas y usan la semilla indicada.
- `p6_pareado.csv` cumple el control de la Parte 1 (o lo reporta).
- No toques ningún archivo existente.

# TASK_CONTEXT — Sensibilidad 2, A7k: requisitos de equipos por kW neto (sin motor)

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

**Archivos que puedes tocar (y solo estos):** `scripts/sens2/p6_equipos_kw.py` (nuevo), `scripts/sens2/s2_f4k.py` (nuevo) y las salidas en
`resultados/2026-10-18_sens2_F1/`: `p6_equipos_kw.csv`, `p6_equipos_kw.md`, y la prueba `_prueba_f4k.xlsx` (borra esta al final).
**No toques** `s2_construir.py` ni el libro `datos/Kalina_anal_sensible_2.xlsx`; el director integra la hoja.

## Objetivo

Los requisitos de equipos del libro están por kg/s de fluido de trabajo (m_b). Para preseleccionar equipos hace falta por kW neto: de las
columnas que ya existen se obtienen sin correr el motor.

## Parte 1 — `p6_equipos_kw.py`

Con `import p4_comun as c` (en `scripts/sens2`; agrega `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`): `d = c.cargar()` devuelve el
DataFrame con las columnas por kg/s de m_b: `Qi_mb` (calor de entrada, kW), `Qout_mb` (calor rechazado, kW), `Wt_mb` (trabajo de turbina, kW), `Wp_mb` (trabajo de bomba, kW),
`wnet_mb` (trabajo neto, kW), `qreg_qi` (cociente Q_reg/Q_i), `UA_reg` (kW/K), `dh_turb` (kJ/kg), `eta_pct`, `centro`, `estudio`, `kalina`, `fuera_rango`; `c.mascara(d, c.REF_TOTAL)` selecciona KALINA (total).
1. Quédate con los KALINA (total) con `wnet_mb` finito y mayor que 0. Calcula por kW neto: `Qi_kW = Qi_mb/wnet_mb`, `Qout_kW = Qout_mb/wnet_mb`, `Qreg_kW = qreg_qi*Qi_mb/wnet_mb`,
   `Wt_kW = Wt_mb/wnet_mb`, `Wp_kW = Wp_mb/wnet_mb` (todas «kW por kW neto»), `UA_kW = UA_reg/wnet_mb` (K^-1) y `m_b_kW = 1/wnet_mb` (kg/s de fluido por kW neto).
2. Control: `Qi_kW` debe ser igual a `100/eta_pct` con tolerancia relativa 1 % en al menos el 99 % de las filas; reporta la fracción que cumple (si es menor, repórtalo, no lo corrijas).
3. P5, P50 y P95 (cuantiles 0.05, 0.5, 0.95) y n de cada una de las 7 magnitudes en estos ámbitos: `todos`, cada uno de los cuatro centros (`C1 Husavik`, `C2 ancla A*`, `C3 caliente 150 C`, `C4 frio 110 C`),
   `solo LHS` (estudio en {3, 14}) y `10 % de mayor eta` (usa `c.mascara(d, c.REF_TOP10)`).
4. Ejemplo de dimensionamiento para 100 kW netos: multiplica por 100 las magnitudes «kW por kW neto» y `m_b_kW` (kg/s) y por 100 `UA_kW` (kW/K); fila adicional `ejemplo 100 kW` en el `.md` con P5-P50-P95 del ámbito `todos`.
5. Salidas: `p6_equipos_kw.csv` (columnas `ambito, magnitud, unidad, n, p5, p50, p95`) y `p6_equipos_kw.md` (tabla llana por magnitud, el control del paso 2 y la advertencia
   «son envolventes de un muestreo numérico, por kg/s de fluido; no son especificaciones de compra»). Imprime el resumen.

## Parte 2 — hoja del libro (`s2_f4k.py`)

Crea `hoja_f4_kw(wb, datos)` y `HOJAS_F4K = [hoja_f4_kw]`, que genera la hoja **`F4 Equipos por kW`**. **Copia el patrón de `scripts/sens2/s2_f6.py`** (imports, `titulo`, `condiciones` con una línea que
empiece por «Base:», `subtitulo`, `tabla`, `bloque`, `nota`, `descripcion`, `numero`; rutas con `RAIZ`). Contenido, todo leído de `p6_equipos_kw.csv`:
1. Tabla del ámbito `todos` (magnitud, unidad, n, P5, P50, P95) y nota con el ejemplo de 100 kW.
2. Gráfico con `bloque(...)`: categorías = ámbitos (`todos`, C1..C4), series = P50 de `Qi_kW`, `Qout_kW` y `Qreg_kW` (mismas unidades, «kW por kW neto»).
3. Gráfico con `bloque(...)`: categorías = ámbitos, una serie = P50 de `m_b_kW` (kg/s por kW neto).
4. Tabla de todos los ámbitos para `UA_kW`.
Después de cada `tabla(...)` que no sea un `bloque`, haz `f += 1` (devuelve la última fila usada). **Prueba**: en un proceso nuevo crea un `Workbook()`, quita la hoja inicial, llama a la función,
`from x5_graficos import dibujar_todos; dibujar_todos(wb)`, guarda en `resultados/2026-10-18_sens2_F1/_prueba_f4k.xlsx`, reabre con `openpyxl` y verifica: la hoja existe, hay al menos 2 gráficos, sin celdas vacías en las tablas de los gráficos, sin palabras prohibidas. Borra el `.xlsx` de prueba al terminar.

## Aceptación

Ambos scripts corren en menos de 2 minutos; cada archivo ≤ 200 líneas; reporta en RESULTS la tabla de P5-P50-P95 de `todos`, el cumplimiento del control y el número de gráficos de la hoja.

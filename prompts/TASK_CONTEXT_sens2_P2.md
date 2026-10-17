# TASK_CONTEXT — Sensibilidad 2, P2: CORREGIBLE frente a KALINA y distancia a KALINA (Fase C)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy; **sin** scikit-learn).
**Entrada:** `resultados/2026-10-17_sens2_P1/p1_dataset.csv` (3 921 filas, ya auditada). Lee antes
`docs/PLAN_SENS2_ANALISIS.md`. Sin corridas nuevas del motor.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba
  archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/`, salidas en
  `resultados/2026-10-17_sens2_P2/`. No modifiques nada existente.
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda
  salida: «confiable», «no confiable», «no citable», «fuera de rango del motor».
- Los umbrales salen de los datos y se reportan; no inventes ninguno. Todo número sale de un archivo.
- Semilla fija 20261017 para cualquier bootstrap (1000 remuestreos, IC al 95 %).

## Decisiones del director que debes aplicar

1. **Duplicados:** el dataset tiene 258 filas duplicadas (mismas 10 entradas y centro; son puntos base repetidos
   en varios estudios). En P2 usa el dataset **deduplicado** (conserva la primera aparición; reporta n = 3 663 o la
   cifra real). Escribe `p2_dataset_dedup.csv`.
2. **W_net escala con m_b.** El punto `M10` (estudio 0) tiene W_net 1113 kW frente a 111 kW en `H0_noextra` con las
   mismas entradas: el estudio 0 no usa m_b = 1. El CSV de P1 no trae `m_b`: añádelo leyéndolo de `x1_cargar`
   (columna `m_b`) y haz que **toda comparación de W_net use W_net / m_b** (W_net específico, kW por kg/s). Reporta
   qué estudios tienen m_b ≠ 1. Guarda `m_b` en `p2_dataset_dedup.csv`.
3. Las salidas η, W_net, Δh, Q_reg solo existen en puntos convergidos: reporta `n` válidos en cada comparación.

## Paso 1 — Comparación de distribuciones (`p2_comparacion.py`)

Para CORREGIBLE frente a KALINA (total) y KALINA dentro del rango experimental, por centro y «todos», y para las
variables `eta_pct`, `Wnet/m_b`, `rp`, `qreg_qi`, `dh_turb`, `q4`: n válidos, mediana, P10, P90, y
- estadístico KS (`scipy.stats.ks_2samp`) y su p-valor;
- diferencia de medianas (CORREGIBLE − KALINA) con IC bootstrap;
- delta de Cliff (calculado con rangos, sin bucles O(n²) si n > 3000).
Haz la comparación **dos veces**: (a) todos los puntos; (b) solo los puntos de muestreo LHS (estudios 3 y 14), para no
mezclar diseños. Pregunta que debe responder el `.md`: ¿los CORREGIBLE sobreestiman o subestiman η y W_net
específico respecto de los KALINA? (con la cifra y su IC; si el IC cruza cero, dilo como «sin diferencia clara»).

## Paso 2 — Por qué falla cada CORREGIBLE (`p2_violaciones.py`)

Por centro: reparto de la violación dominante (la mayor de `viol_O1, viol_O2, viol_O3, viol_O5`; empates → lista),
mediana/P90 de `D` y de cada violación entre los CORREGIBLE, y tabla cruzada violación dominante × cuartil de `D`.
Salida `p2_violaciones.csv` y un párrafo llano.

## Paso 3 — Distancia a KALINA y qué mover (`p2_distancia.py`)

Espacio normalizado: cada una de las 10 variables se lleva a [0, 1] con el mínimo y el máximo observados en el
dataset deduplicado. Para cada CORREGIBLE busca, **dentro del mismo centro**, el KALINA (total) más cercano por
distancia L1 normalizada (usa numpy por bloques; no un bucle O(n²) en Python puro). Reporta por punto: id, centro,
`D`, violación dominante, id del vecino KALINA, distancia L1, número de variables que difieren (tolerancia 1e-9 en
el espacio normalizado), la variable que más cambia, su valor de origen y destino y la dirección (sube/baja).
Salida `p2_distancia.csv`. Resúmenes en `p2_distancia_resumen.csv/.md`:
1. Fracción de CORREGIBLE a **una sola variable** de un KALINA («rescate univariado»), por variable y dirección,
   por centro y violación dominante.
2. Distribución de la distancia L1 y del nº de variables que difieren (P10/mediana/P90).
3. Diferencia η(vecino KALINA) − η(CORREGIBLE) cuando ambos tienen η: mediana e IC. Responde: ¿rescatar un
   CORREGIBLE cambia mucho la eficiencia o solo lo mueve de clase?
4. Relación `D` ↔ distancia L1 (correlación de Spearman con su p-valor): ¿`D` predice qué tan lejos está el KALINA?

## Paso 4 — Robustez del óptimo (`p2_robustez.py`)

Para los KALINA (total) con η válida, por centro: para cada uno, la distancia L1 normalizada al punto **no-KALINA**
más cercano del mismo centro. Compara (KS y mediana) el 10 % de KALINA con mayor η frente al resto. Cuenta cuántos del
10 % superior tienen un no-KALINA a una sola variable de distancia y en qué variable. Pregunta: ¿el óptimo está
cerca de la frontera o en zona segura? Reporta el top-10 de η por centro con su distancia a la frontera, si están
dentro/fuera del rango experimental, y si coinciden con alguno de los 7 puntos atípicos (ids en
`datos/Kalina_anal_sensible_1.xlsx` hoja LEEME: `C1-B6-0236`, `N1-T090-10`, `N7A-C3-P_alta-001`,
`N7A-C4-P_alta-001`, `N7A-C4-eps_hrvg-003`, `N9-C4-B6-0004`, `N8-C4-0141`). Salida `p2_robustez.csv/.md`.

## Paso 5 — Resumen y verificación

`p2_resumen.md` con las respuestas a: ¿sobre/subestiman?, ¿vale rescatar?, ¿qué variable rescata más?, ¿el óptimo
está en zona segura? `p2_verificacion.py`: n dedup = 3 921 − duplicados; Σ clases = n; cada KALINA vecino existe y
es KALINA del mismo centro; distancia L1 ≥ 0 y = 0 solo si las entradas coinciden (no debería, tras
deduplicar: si ocurre, repórtalo); el número de variables que difieren es coherente con la distancia; sin
palabras prohibidas. Una línea OK/FALLA por control; no des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\p2_comparacion.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p2_violaciones.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p2_distancia.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p2_robustez.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p2_verificacion.py
```

(`p2_comparacion.py` crea `p2_dataset_dedup.csv` primero si no existe; si prefieres, hazlo en un módulo común
`p2_comun.py`.) Reporte en el formato de `AGENTS.md`; en RESULTS: las respuestas del paso 5 con sus cifras y la
salida de `p2_verificacion.py`.

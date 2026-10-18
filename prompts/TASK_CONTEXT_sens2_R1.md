# TASK_CONTEXT — Sensibilidad 2, R1: respaldo y aportes del libro viejo (campaña M1–M10b)

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy, openpyxl; **sin** scikit-learn).
**Objetivo:** el libro principal es `datos/Kalina_anal_sensible_2.xlsx` (Sensibilidad 2). El libro viejo
`datos/Excel_kalina_final_final_final.xlsx` (hoja `Datos`, 4 581 filas) sirve SOLO como (a) respaldo fuera de muestra
de las conclusiones de Sens2 y (b) fuente de corridas que Sens2 no tiene. Todo se mide con los parámetros de Sens2:
las 10 variables, los 4 centros y los rangos de abajo. **Sin corridas nuevas del motor.** No modifiques el libro
principal ni ningún archivo existente.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba
  archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/`, salidas en
  `resultados/2026-10-18_sens2_R1/` (créala). Importa con `sys.path.insert(0, 'scripts/sens2')`.
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda
  salida: «confiable», «no confiable», «no citable», «fuera de rango del motor», «indicio», «extrapol».
  La columna `fuera_rango` del libro viejo se reporta con ese nombre tal cual («marca fuera_rango del libro
  viejo»), sin equipararla al rango experimental.
- Los umbrales salen de los datos y se reportan; no inventes ninguno. Todo número sale de un archivo.

## Datos de partida (ya auditados por el director)

- Libro viejo, hoja `Datos`, columnas: `id_punto, Estudio, Parte, clasificacion, omitido, fuera_rango, T_fuente,
  T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, T_amb_diseno, eta_pct, Wnet,
  codigos_falla` (entre otras). Léela con `pandas.read_excel(..., sheet_name='Datos')`.
- Sens2: `from s2_cargar import dataset_dedup` (3 663 filas, columnas `T_fuente ... eps_cond`, `centro`, `kalina`,
  `clasificacion`, `eta_pct`); `resultados/2026-10-17_sens2_P1/p1_existencia_rangos.csv` (columnas `centro,
  variable, min_kalina, max_kalina`) y `p1_fronteras.csv` (columnas `centro, variable, forma, direccion,
  valor_frontera`).
- Nombres de centro EXACTOS: `C1 Husavik`, `C2 ancla A*`, `C3 caliente 150 C`, `C4 frio 110 C`.
- Centros (T_fuente K, T_sumidero K, P_alta kPa, P_baja kPa, x_b): C1 (394.15, 278.15, 3300, 690, 0.82); C2 (403.0,
  300.15, 3000, 563.64, 0.50); C3 (423.15, 280.5, 3150, 950, 0.75); C4 (383.15, 282.5, 3880, 910, 0.88).
- Escalas para distancias (rango de Sens2 de cada variable): T_fuente 230.0, T_sumidero 25.15, P_alta 7180.0,
  P_baja 1900.0, x_b 0.65. Distancia de un punto a un centro = máximo sobre las 5 variables de
  |valor − centro| / escala (norma infinito). Las eficiencias NO entran en la distancia.
- Dominio de Sens2 (un punto está dentro si cumple TODO): T_fuente 343.15–573.15; T_sumidero 278.0–303.15; P_alta
  820–8000; P_baja 100–2000; x_b 0.30–0.95; eta_t, eta_p, eps_hrvg, eps_reg, eps_cond cada una 0.40–0.95.
- Piso de O2 comparable: Sens2 usa piso = T_sumidero (99.4 % de sus filas). Un punto viejo es comparable si
  `T_amb_diseno` es nulo o `T_amb_diseno <= T_sumidero + 1e-6`. Los demás (p. ej. casi todo el estudio 6.2, con
  T_amb_diseno 283.15 > T_sumidero 278.15) se EXCLUYEN: su clase usa otro criterio de cavitación.

## Paso 1 — Filtro y asignación (`scripts/sens2/r1_filtro.py`)

Cascada, contando filas y puntos únicos tras cada filtro y guardándola en `r1_cascada.csv`
(columnas `paso, n_filas, n_unicos, n_kalina`):
1. Hoja `Datos` completa; 2. `omitido == False`; 3. las 10 variables no nulas; 4. piso de O2 comparable;
5. dentro del dominio de Sens2; 6. únicos por las 10 variables redondeadas a 4 decimales (si una misma entrada
aparece en varias partes, conserva una fila y guarda todas las partes en la columna `partes` separadas por `;`);
7. quita las que ya están en `dataset_dedup()` (misma clave de 10 variables redondeadas a 4 decimales; guarda
cuántas eran en `r1_cascada.csv`).
Asigna a cada punto restante el centro más cercano (norma infinito) y su distancia `dist`; columna
`cerca = dist <= 0.15`. Salida `r1_puntos.csv` con: `id_punto, Estudio, partes, las 10 variables, clasificacion,
fuera_rango, eta_pct, Wnet, codigos_falla, centro, dist, cerca`. Además `r1_resumen.csv`: conteo por
`Estudio × centro × clasificacion` solo de los `cerca`.

## Paso 2 — Contraste fuera de muestra (`scripts/sens2/r1_contraste.py`)

Usa solo los puntos `cerca` (dist ≤ 0.15) de `r1_puntos.csv`.

**A. Rangos (conclusiones de existencia).** Para los KALINA (total) viejos de cada centro: para cada variable,
fracción dentro de `[min_kalina, max_kalina]` de ese centro y variable (de `p1_existencia_rangos.csv`), y
fracción dentro en las 10 variables a la vez. Lista (`r1_fuera_de_rango_sens2.csv`) los KALINA viejos con al
menos una variable fuera del rango KALINA de Sens2, indicando cuál. Esa lista es el aporte principal: son
KALINA que Sens2 no tiene.

**B. Fronteras de una variable.** Para cada fila de `p1_fronteras.csv` con `forma` igual a `escalon` o
`ventana` (centro c, variable v, valor_frontera f, dirección «a KALINA» o «a no-KALINA»): toma los puntos viejos
asignados a c cuya distancia calculada **sin la variable v** (norma infinito sobre las otras 4 de las 5 variables
de distancia; si v es una eficiencia, usa las 5) sea ≤ 0.15. Predice con la frontera: para «a KALINA» lado
KALINA = v ≥ f; para «a no-KALINA» lado no-KALINA = v ≥ f en un escalón, y en una ventana el lado KALINA es
la zona entre el par de fronteras del mismo centro y variable (si solo hay una frontera de la ventana, evalúa
únicamente el lado que esa frontera define). Reporta por fila: n, aciertos, tasa de acuerdo (KALINA vs
no-KALINA, donde no-KALINA = cualquier otra clase). `r1_fronteras_contraste.csv` con las columnas
`centro, variable, forma, direccion, valor_frontera, n, aciertos, acuerdo` y la lista de desacuerdos en
`r1_desacuerdos.csv` (id_punto, centro, variable, valor, clase real, clase predicha). Si n < 5 pon `acuerdo`
vacío y márcalo «n insuficiente»; no lo cuentes en el resumen.

**C. Cobertura de huecos.** Por centro: n de puntos viejos con dist ≤ 0.25 (no solo ≤ 0.15) por clase, y los
5 KALINA de mayor `eta_pct` por centro (con su distancia y estudio). Pregunta: ¿qué centro gana más
cobertura? (C4 tiene casi ninguno con ≤ 0.15; reporta si con ≤ 0.25 mejora.) Salida `r1_cobertura.csv`.

**D. Resumen** `r1_resumen.md` (lenguaje llano): respuestas con cifras a: ¿qué fracción de los KALINA viejos
cae dentro de los rangos de Sens2?; ¿qué tasa de acuerdo global tienen las fronteras (suma de aciertos / suma
de n de las filas con n ≥ 5), y cuáles se contradicen?; ¿qué aportes (KALINA fuera de rango de Sens2) hay por
centro y variable?; ¿qué centro gana cobertura? No interpretes más allá de los números; todo hallazgo sin
datos suficientes se dice «no concluyente».

## Paso 3 — Verificación (`scripts/sens2/r1_verificacion.py`)

Una línea OK/FALLA por control, **cálculo independiente** (no repitas la fórmula del script): (1) la cascada es
monótona y el último paso coincide con el número de filas de `r1_puntos.csv`; (2) ningún punto de `r1_puntos.csv`
tiene `T_amb_diseno` > `T_sumidero + 1e-6` ni valores fuera del dominio (relee el libro viejo por `id_punto`);
(3) ninguna clave de `r1_puntos.csv` está en `dataset_dedup()`; (4) `centro` y `dist` recalculados desde cero
coinciden; (5) suma de `r1_resumen.csv` = número de filas `cerca`; (6) en B, recalcula a mano (en el
verificador) 3 filas elegidas al azar con semilla 20261018 y compara n y aciertos; (7) sin palabras prohibidas
en los `.md/.csv`. No des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\r1_filtro.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\r1_contraste.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\r1_verificacion.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: la cascada, las respuestas de `r1_resumen.md` con sus cifras
y la salida de `r1_verificacion.py`. Si algo es ambiguo, repórtalo en UNRESOLVED en lugar de decidir.

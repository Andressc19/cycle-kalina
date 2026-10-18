# TASK_CONTEXT — Sensibilidad 2, P3: índices globales de sensibilidad, interacciones y elasticidades (Fase B)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy; **sin** scikit-learn).
**Entradas:** `resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv` (3 663 filas deduplicadas, con `m_b` y `wnet_mb`) y,
para pares y filas por estudio, `scripts/sens1/x1_cargar.py::cargar_todo()` (columnas `estudio, centro, variable,
par, var1, var2, val1, val2, valor`). Lee antes `docs/PLAN_SENS2_ANALISIS.md` y
`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md` §1 y §6. Sin corridas nuevas del motor.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba
  archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/`, salidas en `resultados/2026-10-17_sens2_P3/`.
  No modifiques nada existente.
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda
  salida: «confiable», «no confiable», «no citable», «fuera de rango del motor».
- Todo umbral o parámetro sale de los datos o de esta tarea y se reporta. Todo número sale de un archivo.
- Semilla fija 20261017. Bootstrap: 500 remuestreos de filas, IC al 95 %. Implementa todo con numpy/scipy.

## Diseño del conjunto de análisis

Muestreo LHS = estudios **3** (centros C1 y C2) y **14** (C3 y C4), ya deduplicados, **por centro** (nunca mezcles
centros en un mismo índice: tienen constantes de bloque distintas). Variables de entrada = las de las 10 que **no
son constantes** en ese bloque (averígualo; reporta cuáles usaste). `m_b` no es una entrada.
Se añaden **3 variables dummy** (uniformes [0,1] independientes, semilla fija) como piso de ruido: un índice de una
variable real solo se considera distinguible del ruido si su límite inferior del IC supera el **máximo** de los
índices de las 3 dummy.
Tres respuestas:
- **Y1 = indicador KALINA (total)** en TODOS los puntos del bloque (los que no convergen cuentan como 0);
- **Y2 = η (%)** y **Y3 = W_net/m_b** solo en los KALINA (total) del bloque; repite Y2 y Y3 también restringido a
  KALINA dentro del rango experimental (`fuera_rango == False`);
- **Y4 = D** en los CORREGIBLE (distancia de factibilidad), para saber qué la reduce.

## Paso 1 — Índices given-data (`p3_indices.py` + `p3_metodos.py`)

Para cada bloque, respuesta y variable (reales + dummy) calcula, con IC bootstrap:
1. **PRCC** (correlación parcial de rangos: rangos, residuos de las demás variables por mínimos cuadrados, correlación
   de Pearson de los residuos).
2. **SRC** (coeficientes de regresión lineal estandarizados) y R² del modelo lineal.
3. **KS/RSA** (solo Y1): `ks_2samp` de los valores de la variable entre KALINA y no-KALINA.
4. **PAWN**: la variable se parte en 10 cuantiles; KS entre la distribución de Y global y la de Y en cada rebanada;
   índice = mediana (y máximo) de esos KS. Para Y1 la CDF de un binario se trata como tal.
5. **δ de Borgonovo (given-data)**: 10 rebanadas equiprobables de la variable; densidad de Y por histograma de 10
   cajas equiprobables (Y1: dos cajas); δ = ½ Σ_i p_i Σ_j |f_Y(j) − f_Y|X_i(j)|.
6. **HSIC**: kernel gaussiano con ancho por la heurística de la mediana, HSIC normalizado (CKA) sobre las filas;
   p-valor por 200 permutaciones.
7. **η² (razón de correlación)**: varianza entre rebanadas (10 cuantiles) / varianza total.
8. **Regresión logística estandarizada** (solo Y1; IRLS con ridge 1e-6): |coeficiente| y su error estándar.
Salida larga `p3_indices.csv` (bloque, respuesta, variable, método, valor, ic_lo, ic_hi, n) y `p3_ranking.csv`: por
bloque y respuesta, el rango medio de cada variable entre métodos y su marca «distinguible del ruido» (según dummy).
En `p3_ranking.md`, una tabla por bloque y respuesta con las 5 variables de mayor rango medio, el signo del efecto
(PRCC o logística) y la marca de ruido. Si un método no se puede calcular (n pequeño, varianza cero), escribe el
motivo en una fila `no_aplica`, no lo omitas.

## Paso 2 — Interacciones desde las mallas de pares (`p3_interaccion.py`)

Pares: B1 T_fuente×P_baja; B2 P_baja×x_b; B3 P_alta×P_baja; B4 eps_cond×T_sumidero; B5 eps_reg×eta_t;
B6 eps_hrvg×T_fuente. Centros: C1 y C2 (estudio 2), C3 y C4 (estudio 11: solo B1–B4). **Un punto pertenece a la malla
de un par si todas las variables distintas de las dos del par valen exactamente lo del centro (redondeo a 2
decimales)**; NO uses la etiqueta `par` (los puntos compartidos están asignados solo a un par). Centros:

| Centro | T_fuente | T_sumidero | P_alta | P_baja | x_b | eta_t | eta_p | eps_hrvg | eps_reg | eps_cond |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 394.15 | 278.15 | 3300 | 690 | 0.82 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |
| C2 | 403.0 | 300.15 | 3000 | 563.64 | 0.50 | 0.85 | 0.75 | 0.85 | 0.75 | 0.95 |
| C3 | 423.15 | 280.5 | 3150 | 950 | 0.75 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |
| C4 | 383.15 | 282.5 | 3880 | 910 | 0.88 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |

Por par y centro, sobre las celdas de la malla (valores distintos de cada eje): tabla de η de los KALINA y matriz
de indicador KALINA. **Índice de no aditividad**: ajusta el modelo aditivo (media de fila + media de columna −
media global) sobre las celdas con valor y reporta (a) 1 − R² del modelo aditivo para η y (b) lo mismo para el
indicador KALINA; añade el nº de celdas válidas. Clasifica cada par: sinérgico/antagónico/aditivo según 1 − R² (≥ 0.25
fuerte; < 0.05 aditivo; umbrales que declaras aquí, no se ajustan después). Salidas `p3_interaccion.csv/.md`.

## Paso 3 — Elasticidades locales (`p3_elasticidad.py`)

Con los barridos de una variable (filas con `variable` distinta de `base`, estudios 1, 4–10 que lo contengan; averigua
cuáles por columna `variable`), por centro y variable: elasticidad de η respecto de la variable en el punto base,
(Δη/η0)/(Δv/v0), por diferencia centrada con los dos niveles vecinos del base **si ambos son KALINA** (si no, por
diferencia hacia adelante o hacia atrás y márcalo; si ninguno es KALINA, escribe `sin KALINA vecino`). Salida
`p3_elasticidad.csv/.md` con una tabla variable × centro.

## Paso 4 — Resumen y verificación

`p3_resumen.md` en lenguaje llano: por centro, las variables que deciden si hay KALINA (Y1), las que mueven η (Y2) y
W_net/m_b (Y3), las que bajan D (Y4), los pares con interacción fuerte, las elasticidades, y qué métodos coinciden o
discrepan (con su cifra). `p3_verificacion.py`: (a) n de cada bloque coincide con el dataset; (b) cada índice finito
y en su rango (PRCC y δ, KS y PAWN en [0,1]; HSIC ≥ 0); (c) las dummy quedan por debajo de las variables reales más
fuertes; (d) pertenencia a la malla: n de celdas por par = n de valores del eje 1 × n del eje 2 (reporta los pares
donde falten celdas); (e) la aditividad: 1 − R² entre 0 y 1; (f) sin palabras prohibidas. Una línea OK/FALLA por
control; no des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\p3_indices.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p3_interaccion.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p3_elasticidad.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p3_verificacion.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: las tablas de ranking por bloque (Y1, Y2, Y3), los pares con
interacción fuerte y la salida de `p3_verificacion.py`.

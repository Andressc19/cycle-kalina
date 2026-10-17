# TASK_CONTEXT — Sensibilidad 2, P1: dataset unificado y Fase A (existencia y fronteras de KALINA)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy; **sin** scikit-learn).
**Contexto:** `docs/PLAN_SENS2_ANALISIS.md` y `docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md` (léelos). No hay
corridas nuevas del motor: todo sale de los CSV ya existentes.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con las herramientas `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c`
  que escriba archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Sin modificar `src/`, `scripts/barrido_final/comun.py`, `scripts/sens1/*`, ni
  ningún CSV de `resultados/` existente ni el libro de datos. Scripts nuevos en `scripts/sens2/` (importa
  `x1_cargar` añadiendo `scripts/sens1` a `sys.path`); salidas en `resultados/2026-10-17_sens2_P1/`.
- **Terminología:** «KALINA (total)», «dentro del rango experimental», «fuera del rango experimental (líquido >
  420 K)». Prohibido en cualquier salida: «confiable», «no confiable», «no citable», «fuera de rango del motor».
  (`x1_cargar.derivar` crea una columna interna llamada `confiable`: NO la exportes; usa `fuera_rango`.)
- No inventes umbrales: los que uses salen de los datos (cuantiles) y se reportan. Todo número sale de un archivo.

## Paso 1 — Dataset unificado (`scripts/sens2/p1_dataset.py`)

Con `x1_cargar.cargar_todo()` escribe `p1_dataset.csv` con una fila por punto de todos los estudios (0–11 y 14–16) y
las columnas: `id_punto, estudio, centro, clasificacion, kalina` (bool), `fuera_rango` (bool: fuera del rango
experimental), las 10 entradas (`T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg,
eps_cond`), `eta_pct, Wnet, D, viol_O1, viol_O2, viol_O3, viol_O5, rp, qreg_qi, dh_turb, Qi, Qreg, q4, t_s`.
Reporta en `p1_dataset_resumen.md`: n por estudio y por clase, y que el total es 3 921 (si no coincide, dilo).
Deduplica solo si dos filas tienen exactamente las mismas 10 entradas **y** el mismo centro; reporta cuántas.

## Paso 2 — Existencia por variable y centro (`p1_existencia.py`)

Para cada centro (C1–C4 y «todos») y cada una de las 10 variables: mínimo y máximo de la variable entre los KALINA
(total), entre los KALINA dentro del rango experimental, y entre todos los puntos probados; n de KALINA y de
puntos. Además P(KALINA) = KALINA/puntos por nivel exacto de la variable (si tiene ≤ 14 valores distintos) o por 8
cuantiles (si tiene más), con n por nivel y su intervalo de Wilson al 95 %. Salidas: `p1_existencia_rangos.csv` y
`p1_existencia_prob.csv`. Advertencia obligatoria en el `.md`: los diseños mezclan OFAT, mallas y LHS, por lo que la
P(KALINA) por nivel depende del diseño; dilo y repórtala **también solo con el LHS** (estudios de muestreo LHS; averigua
sus ids con la columna `estudio`/`id_punto`/`tipo` y di cuáles usaste).

## Paso 3 — Reglas de la región KALINA (`p1_reglas.py`)

Solo con los puntos de muestreo LHS (donde ≥ 9 variables varían a la vez), por centro y «todos»:
1. **Regresión logística** (IRLS en numpy, variables estandarizadas, ridge 1e-6) de `kalina` sobre las 10 entradas
   (las constantes del bloque se omiten): coeficientes, error estándar, signo. Si el ajuste no converge, repórtalo.
2. **Mejor corte único («stump»)** por variable: umbral y dirección que maximizan la reducción de impureza de Gini,
   con la ganancia, y el ranking de variables por ganancia.
3. **Árbol de profundidad 2** (implementación propia con numpy): las 3 reglas más puras (pureza ≥ 0.9 y n ≥ 30) para
   KALINA y para no-KALINA.
Salida: `p1_reglas.csv` y `p1_reglas.md` (en lenguaje llano; cada regla con n, % KALINA).

## Paso 4 — Fronteras y zonas grises (`p1_fronteras.py`)

1. **Frontera por variable** (en los estudios OFAT/barrido de una variable, por centro): el valor donde la clase pasa
   de no-KALINA a KALINA (o al revés), con el nivel anterior y el siguiente; forma observada (escalón, rampa,
   ventana con dos fronteras). Salida `p1_fronteras.csv`.
2. **Zonas grises**: puntos CORREGIBLE con `D` ≤ el cuantil 25 % de `D` entre los CORREGIBLE (reporta el valor del
   cuantil) y su violación dominante (cuál de `viol_O1..O5` es la mayor). Salida `p1_zonas_grises.csv` + conteo por
   centro y por violación dominante en el `.md`.

## Paso 5 — Resumen y verificación

`p1_resumen.md`: tabla de rangos de existencia por variable y centro, las 5 reglas más fuertes, las fronteras y el
número de zonas grises. `p1_verificacion.py` comprueba: total 3 921 (o la diferencia explicada), Σ clases = total,
mín ≤ máx en cada rango, P(KALINA) entre 0 y 1, n por nivel suma al total del centro, sin las palabras prohibidas en
ningún `.md`/`.csv` nuevo. Imprime una línea OK/FALLA por control; no des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\p1_dataset.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p1_existencia.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p1_reglas.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p1_fronteras.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p1_verificacion.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: tabla de rangos de existencia por centro, reglas principales y
salida de `p1_verificacion.py`.

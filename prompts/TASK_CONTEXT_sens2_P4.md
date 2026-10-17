# TASK_CONTEXT — Sensibilidad 2, P4: requisitos para preseleccionar equipos (turbina, regenerador, condensador, HRVG, bomba)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (numpy, pandas, scipy; **sin** scikit-learn).
**Entradas:** `scripts/sens1/x1_cargar.py::cargar_todo()` (trae `Qi, Qout, Wt, Wp, Qreg, m_v, m_l, dh_turb, q4, T_e1..T_e10,
h_e1..h_e10, m_b, rp, qreg_qi, fuera_rango, kalina, estudio, centro`) y
`resultados/2026-10-17_sens2_P2/p2_dataset_dedup.csv` (3 663 filas, ids deduplicados). Une por `id_punto`. Lee
`docs/PLAN_SENS2_ANALISIS.md` y `docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md` §5. Sin corridas del motor.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` ni here-docs que
  escriban archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/`, salidas en `resultados/2026-10-17_sens2_P4/`.
  No modifiques nada existente.
- **Terminología:** «KALINA (total)», «dentro/fuera del rango experimental (líquido > 420 K)». Prohibido en toda
  salida: «confiable», «no confiable», «no citable», «fuera de rango del motor».
- Umbrales y parámetros salen de los datos y se reportan. Todo número sale de un archivo. Semilla 20261017.

## Numeración de estados (de `CONTEXT.md`; úsala tal cual, no inventes otra)

3 = entrada de turbina, 4 = salida de turbina, 8 = entrada de condensador (mezcla), 9 = salida de condensador (líquido
a la bomba), 10 = salida de bomba, 1 = salida fría del regenerador (entrada al HRVG), 5 → 6 = lado caliente del
regenerador (el lado frío va 10 → 1). Temperaturas en K, h en kJ/kg, energías en kW, flujos en kg/s, presiones en kPa.
`m_b = 1` salvo el estudio 0 (m_b ≠ 1): divide toda cantidad extensiva (Qi, Qout, Wt, Wp, Qreg, m_v, m_l) entre
`m_b`, y llama a la columna «por kg/s de m_b».

## Cantidades derivadas por punto (módulo `p4_comun.py`)

Solo para puntos convergidos con las T_e/h_e disponibles; reporta n válidos en cada columna:
- Turbina: `rp = P_alta/P_baja`, `dh_turb`, `Wt/m_b`, `q4` (calidad de salida), `T3`, `T4`, `m_v/m_b`.
- Regenerador (contraflujo): `dT_A = T5 − T1`, `dT_B = T6 − T10`, `pinch_reg = min(dT_A, dT_B)`,
  `LMTD_reg = (dT_A − dT_B)/ln(dT_A/dT_B)` (si `dT_A = dT_B`, = `dT_A`; si alguno ≤ 0, el punto tiene cruce: no
  calcules LMTD y cuéntalo), `UA_reg = Qreg/m_b / LMTD_reg` [kW/K por kg/s], `Qreg/Qi`.
- Condensador: `Qout/m_b`, `aprox_cond_sal = T9 − T_sumidero`, `aprox_cond_ent = T8 − T_sumidero` (diferencias de
  temperatura frente al sumidero; no son un pinch de diseño: dilo).
- HRVG: `Qi/m_b`, `aprox_fuente = T_fuente − T3`.
- Bomba: `Wp/m_b`, `Wp/Wt`, `P_alta`, `P_baja`.
- Ciclo: `eta_pct`, `Wnet/m_b`.

## Paso 1 — Envolventes por centro (`p4_envolventes.py`)

Por centro (C1–C4, y «Sin centro» como estaba en P2), para tres conjuntos: KALINA (total), KALINA dentro del rango
experimental, y el 10 % de KALINA (total) con mayor η: n, mínimo, P5, mediana, P95, máximo de cada cantidad derivada.
Salidas `p4_envolventes.csv/.md`. En el `.md` una tabla llana «lo que debe cubrir cada equipo» (P5–P95 del conjunto
KALINA (total) y del 10 % superior) para turbina, regenerador, condensador, HRVG y bomba.

## Paso 2 — Qué variable fija cada requisito (`p4_dependencias.py`)

Correlación de Spearman (con p-valor) de cada cantidad de equipo `{rp, dh_turb, Wt/m_b, q4, UA_reg, pinch_reg,
Qreg/Qi, Qout/m_b, aprox_cond_sal, Qi/m_b, Wp/Wt}` con cada una de las 10 entradas, por centro, usando KALINA (total)
de los estudios LHS (3 y 14, deduplicados) para que las entradas varíen a la vez. Tabla variable × cantidad con las
3 asociaciones más fuertes por cantidad. Regresión de `dh_turb` sobre `rp` (mínimos cuadrados con numpy, R² y
pendiente por centro). Salida `p4_dependencias.csv/.md`.

## Paso 3 — Restricciones activas y cruces (`p4_restricciones.py`)

Para KALINA (total) por centro: fracción con `q4 < 0.90` (debería ser 0 por definición de O1; verifícalo), con
`pinch_reg ≤ 0` (cruce), y con `pinch_reg` en los cuartiles inferiores; distribución de `pinch_reg` (P5, P50, P95).
Entre los CORREGIBLE: lo mismo, más la fracción con `T9 − T_sumidero` < la mediana de los KALINA (síntoma de O2).
Una tabla comparativa KALINA frente a CORREGIBLE. Salida `p4_restricciones.csv/.md`. Si alguna cantidad no se puede
derivar con la numeración de estados anterior, escríbelo en UNRESOLVED en vez de adivinar.

## Paso 4 — Bandas de diseño (`p4_bandas.py`)

Bandas de `rp` = [1, 1.5), [1.5, 2), [2, 3), [3, 4), [4, 6), [6, 10]: por banda y centro, n de KALINA, η mediana (P10–P90),
`dh_turb` mediana, `q4` mediana, `Wt/m_b` mediana, `pinch_reg` mediana, `UA_reg` mediana. Responde: ¿a qué relación de
presiones la turbina entrega más Δh y a cuál más η? Salida `p4_bandas.csv/.md`.

## Paso 5 — Resumen y verificación

`p4_resumen.md` en lenguaje llano con la preselección por equipo (rango a cubrir, variable que lo fija, restricción
activa) y los límites del análisis (qué es una aproximación respecto de un diseño real). `p4_verificacion.py`:
(a) n de KALINA por centro coincide con P2; (b) `q4 ≥ 0.90` en todos los KALINA (reporta las excepciones); (c) `LMTD > 0`
y `UA > 0` donde se calculan; (d) las sumas de n por banda de `rp` = n de KALINA con `rp` válida; (e) balance del
regenerador: `Qreg/m_b ≈ m·(h1 − h10)` o, si no es verificable con las columnas, dilo; (f) sin palabras prohibidas.
Una línea OK/FALLA por control; no des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\p4_envolventes.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p4_dependencias.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p4_restricciones.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p4_bandas.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\p4_verificacion.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: la tabla de qué debe cubrir cada equipo, las dependencias más
fuertes, la comparación de restricciones y la salida de `p4_verificacion.py`.

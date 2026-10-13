# TASK_CONTEXT — A3b-2: tres remates de leyendas (figuras 2.4-1, 6.1-1 y gráficos de Excel)

**Directorio de trabajo (cwd):** `D:/Desktop/ciclo_kalina_tercero/.claude/worktrees/barrido-final`
**Python:** `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe`
**Antes de correr cualquier script:** `PYTHONIOENCODING=utf-8` (la consola es cp1252 y falla con «η»):
`PYTHONIOENCODING=utf-8 D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe scripts/analisis_final/<script>.py`

## Notas de entorno (OBLIGATORIAS)

- Modifica archivos SOLO con `edit` (los scripts tienen cambios sin commit que no se deben perder) o `write`.
- Git Bash: rutas con `/`, relativas al cwd; un comando por llamada; **timeout = 7200000** en cada comando.
- No leer ni listar nada fuera de `D:/Desktop/ciclo_kalina_tercero`. No hacer commit. No borrar nada.
- Escribir SOLO en `scripts/analisis_final/a3_m02s.py`, `a3_m07.py`, `a2_graf_casos_b.py`,
  `analisis_final/03_figuras/` (salidas) y `datos/Excel_kalina_final_final_final.xlsx` (solo vía su script).
- Scripts de 200 líneas como máximo (si un archivo ya pasa de 200, no lo agrandes: reporta el conteo).
- No cambiar números, clases, ejes ni títulos. **Solo leyendas, notas y nombres de serie.**

## D1. Figura 2.4-1 (`a3_m02s.py`) — la leyenda roza los datos

En el panel izquierdo la leyenda de 2.4c (`… · fuera de rango`) llega hasta x ≈ 293 K y toca la línea naranja.
Parte el rótulo de la base 2.4c en dos líneas con `\n` **justo antes de** `· fuera de rango`
(p. ej. `"2.4c · ε_HRVG = 0.40 (fuente del profesor)\n· fuera de rango"`) en ambas leyendas, para que
la leyenda quede más angosta. No cambies la posición de la leyenda salvo que siga tocando datos;
si sigue tocándolos, usa `fontsize=7`. Comprueba abriendo el PNG resultante con la herramienta de lectura.

## D2. Figura 6.1-1 (`a3_m07.py::fig_m06`) — identidad de diseño

La tarea anterior usó la columna `id` como identidad del diseño y por eso concluyó 5 diseños para 5 corridas.
Pero P08 (`m6_comparacion.csv`, origen «M7, óptimo A4») y A4 (`m9_motor_real.csv`, origen «Óptimo A4 de M7»)
son el MISMO diseño: ambos tienen `eta_teqp` = 0.1559965… y T_fuente 415 K, P_baja 400 kPa.

Define **diseño = valor de `eta_teqp` redondeado a 6 decimales** (ambos CSV traen `eta_teqp`; es la única columna
común que identifica el diseño). Cuenta, sobre las corridas con `eta_real` no nulo de la figura, k = corridas y
u = valores distintos. Si u < k, agrega al pie (en `marcas` o como línea propia, como ya hace el script) la frase:
«Hay {k} corridas con η real sobre {u} diseños distintos: un mismo diseño (el óptimo A4 de 5.1d) se corrió con
los dos presupuestos de tiempo (300 s y 1500 s).» Escribe en RESULTS los valores `eta_teqp` agrupados que
justifican u. No cambies puntos ni la leyenda (n = 2 y n = 3 son correctos: son corridas).

## D3. Gráficos nativos de Excel (`a2_graf_casos_b.py`) — paridad con las figuras corregidas

Los pies ya se copian de los `.pie.md`; faltan los nombres de serie / estructura de tres gráficos:

- **FIG-M04c-01 (3.3-1, `graf_m04c`)**: dos series apiladas (columnas con `grouping="stacked"`,
  `overlap = 100`): «KALINA dentro del rango (n = {n1})» y «KALINA fuera de rango (n = {n2})» (n sumados
  sobre todas las franjas; deben ser 45 y 30), con los % por franja calculados igual que en
  `a3_m04c.py` (confiables = `fuera_rango` False; fuera = True; suma = % total actual, que NO debe cambiar:
  33, 53, 50, 67, 69, 62, 50, 36, 70, 75). Los datos de la serie deben quedar **visibles** en el bloque de la
  hoja de datos de gráficos (columnas nuevas junto a la existente).
- **FIG-M02S-01 (2.4-1)**: el nombre de la serie 2.4c lleva el sufijo « · fuera de rango» (mismo criterio
  de datos que `a3_m02s.py`: si todos los KALINA de la base son fuera de rango; «k de n» si solo algunos).
- **FIG-M07-01 (5.1-1)**: el nombre de cada serie de arranque termina en « · último paso +X.XX pp» con el mismo
  cálculo de `a3_m07.py` (η del último paso aceptado menos el anterior, ×100, ordenado por `iteracion`).
  Valores esperados: 5.1a +0.45, 5.1b +0.41, 5.1c +0.08, 5.1d +0.06, 5.1e +0.18.

Si alguno de estos tres gráficos no se construye en `a2_graf_casos_b.py` (p. ej. lo arma otro módulo `a2_graf_*`),
localiza el módulo con `grep` y edítalo ahí; si es `a2_graf_casos_a.py` o `a2_graf_base.py`, está permitido
SOLO para estos tres gráficos.

## Verificación obligatoria (en este orden)

1. `a3_m02s.py` y `a3_m07.py` (con PYTHONIOENCODING) → «OK». Abre `Figura_2.4-1_*.png` y comprueba que la
   leyenda no toca los datos.
2. `a3_verificar.py` → «30 de 30 figuras completas; fallas = 0».
3. `git status --short -- "analisis_final/03_figuras/**/*_clases.json"`: solo los dos que ya estaban modificados
   (3.1-3 y 3.2-1).
4. `a2_excel_libro.py` y luego `a2_verificar.py` → «TODO OK». Reporta el nº de hojas.
5. En RESULTS copia: el pie de 6.1-1, los nombres de serie nuevos de los tres gráficos de Excel y los %
   por franja de 3.3 (deben ser los de arriba).

## Si algo es ambiguo
No decidas: repórtalo en `UNRESOLVED` (formato de salida de AGENTS.md).

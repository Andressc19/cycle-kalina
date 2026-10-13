# TASK_CONTEXT — A3b: corregir leyendas y notas de las figuras (revisión de figuras 2026-10-12)

**Directorio de trabajo (cwd):** `D:/Desktop/ciclo_kalina_tercero/.claude/worktrees/barrido-final`
**Python:** `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe`
**Lee primero:** `scripts/analisis_final/a3_comun.py` (190 líneas), `scripts/analisis_final/estilo.py`,
`scripts/analisis_final/pies.py` (solo `armar_pie`, que ya acepta `marcas=`).

## Notas de entorno (OBLIGATORIAS)

- Los archivos se modifican SOLO con las herramientas `edit` y `write`. **Usa `edit`** sobre los scripts
  existentes: varios tienen cambios sin commit (a3_m04.py, a3_m07.py) que NO se deben perder.
- La shell es Git Bash: usa rutas con `/` y relativas al cwd. **No uses rutas con `\`** (Bash las rompe).
  Sin `&&` con PowerShell; un comando por llamada.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
- No leer ni listar nada fuera de `D:/Desktop/ciclo_kalina_tercero`. No hacer commit. No borrar nada.
- Escribir SOLO en: `scripts/analisis_final/a3_comun.py`, `a3_m02r.py`, `a3_m02s.py`, `a3_m04.py`,
  `a3_m04c.py`, `a3_m05.py`, `a3_m07.py`, `a3_m10.py`, `a3_m02.py`, `analisis_final/03_figuras/`
  (salidas) y, al final, `datos/Excel_kalina_final_final_final.xlsx` (solo vía su script).
- No tocar `estilo.py`, `nombres.py`, `pies.py`, `codigos*.py`, `a4_*`, `a5_*`, `a6_*`, tablas ni datos.
- No cambiar números, clases, ejes, títulos ni conclusiones de ninguna figura: **solo leyendas, notas y
  el pie**. Los `*_clases.json` deben quedar idénticos (se compara al final).
- Scripts de 200 líneas como máximo.

## Problema

Los marcadores huecos significan «fuera del rango validado del motor de propiedades», pero varias
leyendas no lo dicen y el lector toma esos puntos como KALINA válidos. Además hay cuatro leyendas/pies
que inducen a error. Corrige exactamente lo siguiente.

## Cambios

### C1. `a3_comun.dispersion` y `a3_comun.leyenda_fig` — hueco con su propia entrada de leyenda
- En `dispersion`: para cada clase con marcador distinto de "x", la serie rellena lleva
  `label=f"{ETIQUETA_CLASE[c]} (n = {n_rellenos})"` y la serie hueca lleva
  `label=f"{ETIQUETA_CLASE[c]}, fuera de rango (n = {n_huecos})"`. Si una de las dos está vacía, NO se
  crea su entrada (ni «n = 0»). Para clases con marcador "x" se mantiene una sola entrada con el n total.
- En `leyenda_fig(fig, sub, marcadores=None)`: agrega el parámetro opcional `marcadores` (dict clase →
  marcador de matplotlib) que reemplaza `MARCADOR_CLASE[c]` en el handle de la leyenda. Además, para cada
  clase con marcador ≠ "x" que tenga puntos con `fuera_rango` True en `sub`, crea una entrada hueca
  (`markerfacecolor="none"`) `"<clase>, fuera de rango (n = k)"` y deja la entrada rellena con
  `n = total − k`. Si no hay huecos, el comportamiento es el de hoy.
- **Auditoría:** busca en todos los `a3_*.py` cualquier otro lugar que dibuje marcadores huecos
  (`facecolors="none"`, `fuera_rango`, `hueco`) sin pasar por esas dos funciones (p. ej. a3_m02.py,
  a3_m02r.py, a3_m05.py, a3_m10.py) y aplica la misma regla de etiquetado. Lista cada uno en RESULTS.

### C2. FIG-M05c-01 (Figura 4.2-1, `a3_m05.py::fig_m05c`)
Los KALINA se dibujan como cuadrado (`"s"`) pero la leyenda muestra círculo. Llama
`leyenda_fig(fig, sub, marcadores={"KALINA": "s"})`. No cambies el marcador del gráfico.

### C3. FIG-M02S-01 (Figura 2.4-1, `a3_m02s.py`)
Cada línea (base) usa solo puntos KALINA. Calcula para cada base cuántos de esos KALINA tienen
`fuera_rango` True (columna de `analisis_final/01_datos/todos_los_puntos.csv`, filtrada por el mismo
bloque/subcaso que ya usa el script). Si todos: agrega `" · fuera de rango"` al final de su `label`;
si solo algunos (k de n): `" · k de n fuera de rango"`; si ninguno: sin cambio. Aplica el sufijo a los
labels de ambas leyendas (P_baja mínima y η máxima). Agrega al pie (`marcas=`) la frase
«Las líneas marcadas “fuera de rango” se apoyan en KALINA fuera del rango validado del modelo de propiedades».

### C4. FIG-M04c-01 (Figura 3.3-1, `a3_m04c.py`)
Las barras mezclan KALINA confiables con KALINA fuera de rango. Apila cada barra en dos tramos:
(a) KALINA con `fuera_rango` False, verde sólido `#2E7D32`; (b) KALINA con `fuera_rango` True, mismo verde
con `hatch="//"`, `facecolor="none"` y borde verde. El número sobre la barra sigue siendo el % total (como
hoy). Agrega leyenda: «KALINA dentro del rango (n = …)» y «KALINA fuera de rango (n = …)» con n sumados
sobre todas las franjas. Pie: `marcas=` «Barra sólida: KALINA dentro del rango; rayada: KALINA fuera de rango».
Los porcentajes totales por franja deben ser IDÉNTICOS a los actuales (impresos en el log).

### C5. FIG-M07-01 (Figura 5.1-1, `a3_m07.py::fig_m07`)
En el `label` de cada línea (arranque) agrega al final `" · último paso +X.XX pp"`, donde X.XX =
100·(η del último paso aceptado − η del paso aceptado anterior) del mismo arranque (ordenado por
`iteracion`). Si el arranque tiene un solo paso, `" · sin pasos previos"`. Mantén el `: {máx} %` actual.
En el pie, después de la lista de arranques, agrega la línea: «El último paso muestra cuánto seguía
subiendo cada búsqueda al detenerse; la η máxima de una búsqueda con último paso grande es una cota
inferior, no un óptimo confirmado.»

### C6. FIG-M06-01 (Figura 6.1-1, `a3_m07.py::fig_m06`)
Mira las columnas de `resultados/2026-10-08_final_M6/m6_comparacion.csv` y
`resultados/2026-10-08_final_M9/m9_motor_real.csv`. Define «diseño distinto» como el conjunto de valores
únicos de las columnas que describen el punto (un identificador de punto si existe; si no, las variables de
diseño T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond redondeadas a
6 decimales). Agrega al pie: «Hay {k} corridas con η real sobre {u} diseños distintos: un mismo diseño se
corrió con los dos presupuestos de tiempo (300 s y 1500 s).» **Solo si {u} < {k}**; si {u} = {k}, no
agregues nada. Si no puedes determinar la identidad del diseño con las columnas disponibles, NO inventes:
repórtalo en UNRESOLVED y no cambies el pie.

### C7. FIG-M04-01 y FIG-M04-02 (Figuras 3.2-1 y 3.2-2, `a3_m04.py`)
Al `armar_pie(..., marcas=...)` de ambas agrega la nota (con los valores calculados de `sub["P_baja"]`
del bloque B07, mínimo y máximo, 0 decimales):
«P_baja se muestreó entre {min} y {max} kPa: el borde superior de P_baja de los KALINA es el borde de
la caja de muestreo, no una frontera física (el estudio 3.3 explora hasta 2500 kPa).»
Si ya hay `marcas`, concatena con un espacio.

## Verificación obligatoria (en este orden)

1. Antes de editar, ejecuta `git status --short -- analisis_final/03_figuras` y guarda la lista de
   `*_clases.json` que YA aparecen modificados (se reportan al final; no se tocan a propósito). No copies carpetas.
2. Después de editar, corre cada script de figuras tocado desde la raíz del cwd, uno por llamada:
   `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe scripts/analisis_final/a3_m02.py` y lo
   mismo con `a3_m02r.py`, `a3_m02s.py`, `a3_m04.py`, `a3_m04c.py`, `a3_m05.py`, `a3_m07.py`, `a3_m10.py`.
   (Si un script falla por un cambio tuyo, arréglalo; si falla por otra causa, repórtalo.)
3. `python scripts/analisis_final/a3_verificar.py` debe terminar sin «FALTA» ni «FALLA».
4. `git diff --stat -- "analisis_final/03_figuras/**/*_clases.json"`: no debe haber diferencias nuevas
   respecto de las que ya estaban antes de tu tarea (las que ya aparecían modificadas antes no cuentan:
   repórtalas, no las toques). Si un `_clases.json` cambió por tu tarea, es un error.
5. Reconstruir el libro: `python scripts/analisis_final/a2_excel_libro.py` y luego
   `python scripts/analisis_final/a2_verificar.py`. Debe terminar sin fallas. (El libro copia los pies de las
   figuras.) El hash de `datos/Excel_final_kalina.xlsx` no debe cambiar (el script lo comprueba).
6. Lista en RESULTS, por figura, el archivo `.png` regenerado con su fecha, y copia textualmente las
   nuevas líneas de leyenda de C1 (los `label=`) y el pie de C5.

## Criterio de aceptación

- Ninguna figura con marcadores huecos queda sin entrada «fuera de rango» en su leyenda.
- 4.2-1 muestra KALINA como cuadrado en la leyenda; 3.3-1 apilada; 2.4-1 con sufijo; 5.1-1 con el último paso.
- `a3_verificar.py` y `a2_verificar.py` sin fallas; `_clases.json` idénticos.

## Si algo es ambiguo

No decidas: repórtalo en `UNRESOLVED`. En particular, si `a3_m02s.py` no permite saber qué puntos KALINA
sostienen cada línea, o si `a2_excel_libro.py` tarda más de 30 min.

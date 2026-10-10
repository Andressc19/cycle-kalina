# TASK_CONTEXT — A1b: correcciones a A1 (condiciones de barridos de una variable a la vez, bloque B05, pies)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-datos`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Contexto:** es la continuación de `prompts/TASK_CONTEXT_af_A1_datos.md` (léelo). Los scripts de A1 ya
existen en `scripts/analisis_final/`.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`. Cada comando con el PARÁMETRO `timeout` de la
  herramienta shell = 7200000, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. Modificar SOLO `scripts/analisis_final/a1_*.py`,
  `pies.py` y lo que esos scripts generan en `analisis_final/`. No hacer commit. Archivos ≤ 200 líneas.

## Corrección 1 — barridos de una variable a la vez (OAT)

Problema: en los subcasos donde se mueve **una variable por vez**, con las demás fijas en un punto base,
`condiciones_por_subcaso.csv` marca casi todo como "barrido", y el pie dice que no hay nada fijo. Es
falso: en cada tramo solo se mueve una variable.

Subcasos OAT: los que tienen la columna `variable` no vacía en la tabla canónica (KF-M02-N1, KF-M03,
KF-M08, KF-M10-OFAT y KF-M10b-OFAT, si la tienen).

En `a1_condiciones.py`:
- Agrega a `condiciones_por_subcaso.csv` las columnas `es_oat` (sí/no) y `valor_base`. El `valor_base` es
  el valor más frecuente (moda) de esa variable en el subcaso, redondeado a 6 cifras significativas.
  Se calcula para todas las variables numéricas de los subcasos OAT y queda vacío en los demás.
- Nuevo archivo `analisis_final/00_inventario/condiciones_oat.csv`, con una fila por
  (id_subcaso, variable_movida, variable): `estado` (fijo/barrido), `valor_fijo`, `min`, `max`,
  `n_valores`, calculada **solo con las filas de ese `variable_movida`**. Si en un grupo alguna variable
  que no es la movida resulta "barrido", anótala en `checks_A1.md` como INFORMACIÓN. No es FALLA.

En `pies.py`, `condiciones_texto(id_subcasos)`: si todos los subcasos pedidos son OAT, devuelve:
`"Punto base (las demás variables quedan fijas en): <var> = <valor_base> <unidad>; ... Cada panel o tramo mueve solo su variable."`
`"Datos barridos (uno a la vez): <var> [min–max] <unidad> (n valores); ..."`
Agrega el parámetro opcional `variable_movida=None`: si se da, usa `condiciones_oat.csv` para ese grupo.

## Corrección 2 — el bloque B05 se separa por base

En `a1_fuentes.py`, cambia `bloque_director` de M2S (m2s_malla y m2s_biseccion) de `B05` a `B05-<base>`.
Las 4 bases tienen T_fuente o ε_HRVG fijas distintas, así que no son el mismo bloque.

## Corrección 3 — criterio de consistencia de bloque

En `bloques.csv`, la columna `consistente` compara SOLO las variables **fijas** (estado y valor). Que
dos subcasos tengan una variable barrida con rangos o n de valores distintos **no** los vuelve
inconsistentes. Pasa a "no" cuando una variable es fija en un subcaso y barrida en otro, o fija con
valores distintos. Para los subcasos OAT, la comparación se hace con `valor_base`. Agrega la columna
`diferencias_barrido` con las diferencias de rango (como información).

## Corrección 4 — detalles de `pies.py`

- `motor` no lleva unidad: escribe `motor = teqp`, sin "–".
- En `armar_pie`, si `n` es None o NaN, omite la frase `n = …` en vez de escribir "NA".
- Las variables con `estado = sin_dato` no aparecen ni en fijos ni en barridos.

## Comandos (cada uno con timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_cargar.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_condiciones.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_estrella.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_verificar.py
```

Después, imprime (con `python -c`, importando `pies`):
- `condiciones_texto(["KF-M03"])`
- `condiciones_texto(["KF-M03"], variable_movida="P_baja")`
- `condiciones_texto(["KF-M02S-B1"])`
- `condiciones_texto(["KF-M04", "KF-M04b"])`

y la tabla de `bloques.csv` (`bloque_director`, `consistente`, `diferencias`).

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS, pega esas 4 salidas y la tabla de bloques.

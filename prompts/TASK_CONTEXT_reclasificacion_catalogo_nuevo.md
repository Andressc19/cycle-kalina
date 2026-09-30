---
project: ciclo_kalina_tercero
task_id: 2026-09-29-reclasificar-historico-catalogo-nuevo
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-29
---

# TASK_CONTEXT — Reclasificar histórico de barridos al catálogo nuevo (CSVs + Excel)

## Task ID

2026-09-29-reclasificar-historico-catalogo-nuevo

## Project

`ciclo_kalina_tercero`, rama `test/fases-sensibilidad` (cambia a esa rama si no estás ahí —
es donde viven los CSV de resultados; el cambio de código en sí ya está comiteado en
`fix/clasificacion-o1-c1-o5-corregible`, fc8edcd, NO hace falta tocar `src/` para esta
tarea).

## Contexto

Se acaba de cambiar el catálogo de `Clasificacion` (ver commit `fc8edcd` en
`fix/clasificacion-o1-c1-o5-corregible`): `VALIDO_ADVERTENCIA` y `DEGENERADO` ya no existen.
El mapeo es **exacto y sin ambigüedad** (confirmado por el análisis del propio código: cada
valor viejo solo lo producía un conjunto fijo de criterios):

- `VALIDO_ADVERTENCIA` → **`CORREGIBLE`** (lo producían O1 y C1-banda-estrecha, ambos ahora
  CORREGIBLE).
- `DEGENERADO` → **`INVIABLE`** (lo producía solo O5-sobrecalentado, ahora INVIABLE).
- Todo lo demás (`NO_CONVERGIO`, `CORREGIBLE`, `INVIABLE`, `KALINA`) queda igual.

Todos los CSV de `resultados/barridos_2026-09-19/` (fase1_profesor, fase2_libre, fase3_real)
se generaron con el catálogo VIEJO y tienen filas con esos dos valores obsoletos en la
columna `clasificacion` — y algunos también en el texto de `mensaje` (que empieza con
`[VALIDO_ADVERTENCIA] ...` o `[DEGENERADO] ...`). El Excel
`D:\Desktop\ciclo_kalina_tercero\primeros_barridos_e_iteraciones_kalina.xlsx` se generó a
partir de esos CSV, así que hereda el mismo problema.

**No hace falta re-resolver NINGÚN punto del ciclo** — es un remapeo mecánico de texto, el
resultado físico (`eta`, `Wnet`, convergencia) no cambia, solo la etiqueta.

## Objective

1. Para CADA archivo `.csv` bajo `resultados/barridos_2026-09-19/` que tenga una columna
   `clasificacion` (usa pandas, recórrelos todos con un glob — no asumas cuáles son, hay
   varias decenas entre `fase1_profesor/`, `fase2_libre/`, `fase3_real/`):
   - Reemplaza el valor literal `"VALIDO_ADVERTENCIA"` por `"CORREGIBLE"` en la columna
     `clasificacion`.
   - Reemplaza el valor literal `"DEGENERADO"` por `"INVIABLE"` en la columna
     `clasificacion`.
   - Si existe columna `mensaje` (o similar, texto libre con el formato
     `[CLASIFICACION] CODIGO: ...`), reemplaza el prefijo `[VALIDO_ADVERTENCIA]` por
     `[CORREGIBLE]` y `[DEGENERADO]` por `[INVIABLE]` dentro del texto — con cuidado de NO
     tocar ninguna otra ocurrencia casual de esas palabras que no sea el prefijo de
     clasificación (verifica con un regex ancorado al inicio o al patrón `[XXX]`, no un
     `str.replace` ciego sobre todo el texto si hay riesgo de falso positivo — revisa un
     ejemplo real de `mensaje` antes de decidir la técnica).
   - **Sobrescribe el mismo archivo** (no crees copias `_v2`/`_nuevo` — es una corrección in
     place del catálogo, no una nueva versión de datos).
   - También revisa columnas de diagnóstico específicas de algunas rondas que puedan guardar
     pesos/mapas por clasificación (p.ej. `scripts/barridos_2026-09-19/fase3_real/
     busqueda_base_husavik.py` tiene un diccionario `peso` con esas claves — es CÓDIGO, no
     dato, así que si lo encuentras en un `.py` de `scripts/`, actualiza también esa clave
     del diccionario para que siga funcionando con el catálogo nuevo, pero NO ejecutes ese
     script, solo corrige la clave del diccionario como mantenimiento).
2. Regenera el Excel `D:\Desktop\ciclo_kalina_tercero\primeros_barridos_e_iteraciones_kalina.xlsx`
   a partir de los CSV ya corregidos — reusa
   `scripts/barridos_2026-09-19/excel_iteraciones.py` (ya existe de la tarea anterior) si
   sigue vigente con el esquema de datos actual; si algo cambió desde entonces (hay CSVs
   nuevos de rondas 4-6 que ese script quizás no contemplaba), actualízalo para que incluya
   TODO lo que hay hoy en `fase2_libre/`/`fase3_real/` (rondas 4, 5, 6 incluidas — revisa
   qué hay ahora, no asumas que es lo mismo que cuando se escribió el script originalmente).
3. Verifica al final: `grep -r "VALIDO_ADVERTENCIA\|DEGENERADO"` sobre todos los `.csv` de
   `resultados/barridos_2026-09-19/` y sobre el Excel regenerado debe dar CERO coincidencias
   (excepto, si aplica, en archivos que sean reportes `.md` narrativos que citan el catálogo
   viejo como referencia histórica de una decisión ya tomada — esos NO son datos, son texto
   narrativo, decide caso por caso y documenta qué dejaste y por qué).

## Files

Puedes modificar: cualquier `.csv` bajo `resultados/barridos_2026-09-19/` que tenga columna
`clasificacion` o `mensaje`, el archivo Excel en
`D:\Desktop\ciclo_kalina_tercero\primeros_barridos_e_iteraciones_kalina.xlsx` (fuera del
repo, ya lo tocaste en la tarea anterior), y `scripts/barridos_2026-09-19/excel_iteraciones.py`
si hace falta actualizarlo. También puedes tocar el diccionario `peso` de
`scripts/barridos_2026-09-19/fase3_real/busqueda_base_husavik.py` (solo esa clave, sin
ejecutar el script).

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni el contenido narrativo de los
`.md` (`BASE_LIBRE_v2.md`, `CASO_HUSAVIK_v2.md`, `RESUMEN_CRUZADO_3_FASES.md`,
`REPORTE_FASE2_FASE3.md`, etc.) — esos son reportes ya escritos y aprobados, no los
reescribas salvo que citen literalmente una clasificación de un punto de datos (en cuyo caso
sí corrígelo, mismo criterio que los CSV).

## Constraints

1. No re-resuelvas ningún punto del ciclo — es un remapeo de texto/etiqueta, no una
   recomputación física.
2. No pierdas ninguna fila ni columna de ningún CSV al reescribirlo.
3. Verifica la integridad de cada CSV después de escribirlo (mismo número de filas antes y
   después, mismas columnas).

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: cuántos archivos CSV se corrigieron, cuántas filas cambiaron
de `VALIDO_ADVERTENCIA`→`CORREGIBLE` y de `DEGENERADO`→`INVIABLE` en total, y confirmación de
que el Excel quedó regenerado y limpio.

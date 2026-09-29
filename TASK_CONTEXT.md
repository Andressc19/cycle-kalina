---
project: ciclo_kalina_tercero
task_id: 2026-09-29-eliminar-valido-advertencia-y-degenerado
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-29
---

# TASK_CONTEXT — Eliminar VALIDO_ADVERTENCIA y DEGENERADO; O1/C1→CORREGIBLE, O5(sobrecalentado)→INVIABLE

## Task ID

2026-09-29-eliminar-valido-advertencia-y-degenerado

## Project

`ciclo_kalina_tercero`, rama `fix/clasificacion-o1-c1-o5-corregible` (creada por el director
específicamente para esta tarea — "fork antes de tocar src/", regla ya establecida del
proyecto). **Esta tarea SÍ modifica `src/restricciones/`** — está explícitamente autorizado
por el usuario, a diferencia de las tareas de barrido anteriores.

## Contexto — decisión del director

El catálogo actual de `Clasificacion` (`src/restricciones/modelos.py`) tiene 6 niveles:
`NO_CONVERGIO < INVIABLE < DEGENERADO < CORREGIBLE < VALIDO_ADVERTENCIA < KALINA`. El
director decidió simplificarlo a 4 niveles, reasignando las fallas que hoy producen
`VALIDO_ADVERTENCIA` y `DEGENERADO`:

1. **O1** (título de vapor en la salida de la turbina, `q4 < 0.90`, hoy clasifica
   `VALIDO_ADVERTENCIA`) → debe clasificar **`CORREGIBLE`**.
2. **C1** (banda de separación de composiciones bajo la incertidumbre del motor, hoy
   clasifica `VALIDO_ADVERTENCIA` — OJO: el otro caso de C1, "orden de composiciones
   invertido", ya es `INVIABLE` y NO cambia) → el caso de banda estrecha debe clasificar
   **`CORREGIBLE`**.
3. **O5, caso sobrecalentado** (el ciclo deja de ser Kalina y se comporta como Rankine, hoy
   clasifica `DEGENERADO` — OJO: el otro caso de O5, "salida del HRVG líquida", ya es
   `INVIABLE` y NO cambia) → el caso sobrecalentado debe clasificar **`INVIABLE`**.
4. Como consecuencia de 1-3, **ningún criterio implementado vuelve a producir
   `VALIDO_ADVERTENCIA` ni `DEGENERADO`** — elimina esos dos valores del enum `Clasificacion`
   por completo (no los dejes "muertos" en el código).

**El catálogo final de `Clasificacion` queda en 4 niveles**:
`NO_CONVERGIO < INVIABLE < CORREGIBLE < KALINA`.

## Objective

1. **`src/restricciones/modelos.py`**: elimina `DEGENERADO` y `VALIDO_ADVERTENCIA` del enum
   `Clasificacion` y de `_ORDEN_CLASIFICACION`. Actualiza el docstring del enum (dice "de más
   a menos severa", mantenlo correcto con los 4 niveles restantes) y cualquier comentario que
   los mencione.
2. **`src/restricciones/operativos.py`**:
   - O1: cambia `clasificacion=Clasificacion.VALIDO_ADVERTENCIA` a
     `clasificacion=Clasificacion.CORREGIBLE`. Revisa el docstring del módulo/función que
     dice "(tecnológico, VALIDO_ADVERTENCIA)" y corrígelo.
   - O5 (rama sobrecalentada, `q2 > 1.0 - DQ`): cambia
     `clasificacion=Clasificacion.DEGENERADO` a `clasificacion=Clasificacion.INVIABLE`. NO
     toques la otra rama de O5 (`q2 < DQ`, ya es INVIABLE).
   - Decide tú si `Severidad` de O1 sigue siendo `TECNOLOGICO` o si ya no tiene sentido esa
     etiqueta con la nueva clasificación — si la mantienes, documenta por qué (severidad y
     clasificación son conceptos separados en este código: `Severidad` describe el TIPO de
     causa, `Clasificacion` el resultado final — probablemente no hace falta tocar
     `Severidad`, pero verifícalo leyendo cómo se usa en el resto del código antes de asumir).
3. **`src/restricciones/composicion.py`**: en C1, la rama de banda estrecha (`(x_rico -
   x_pobre) <= _BANDA_C1`) cambia `clasificacion=Clasificacion.VALIDO_ADVERTENCIA` a
   `clasificacion=Clasificacion.CORREGIBLE`. NO toques la otra rama de C1 (orden invertido,
   ya es INVIABLE).
4. **`src/restricciones/clasificacion.py`**: revisa `_PRIORIDAD` (o el nombre que tenga ahí
   el diccionario de prioridad de severidad para elegir la falla principal) — debe quedar
   consistente con los 4 niveles restantes, sin referencias a los valores eliminados.
5. **`src/ui_clasificacion.py`**: revisa `CLASIFICACION_INFO` (o como se llame el diccionario
   que mapea clasificación → etiqueta/tipo de aviso de Streamlit) — quita las entradas de
   `VALIDO_ADVERTENCIA`/`DEGENERADO` si existen, para que no quede una clave muerta apuntando
   a un valor de enum que ya no existe.
6. **`src/sensitivity.py`**: si menciona `VALIDO_ADVERTENCIA`/`DEGENERADO` en docstrings o
   comentarios (no en lógica ejecutable, revisa), actualízalo. Si NO los usa en lógica
   ejecutable, es probable que no necesite cambios de código, solo de documentación.
7. **Cuando reportes la síntesis/conclusión de un punto** (esto ya lo hace
   `ResultadoValidacion.mensaje_reporte()` — no inventes un mecanismo nuevo, verifica que
   siga funcionando igual con los 4 niveles): debe seguir explicando POR QUÉ el punto no
   logra ser KALINA (criterio que falla, valor medido vs esperado, causa probable,
   sugerencia) — este comportamiento YA EXISTE, tu trabajo es no rompimiento al quitar los 2
   niveles, no reconstruirlo.

## Tests — actualiza los que asuman el catálogo viejo

- `tests/test_restricciones.py`: busca tests que esperen `VALIDO_ADVERTENCIA` o
  `DEGENERADO` (p.ej. uno que se llame algo como "test_falla_b_hrvg_sobrecalentado_da_...")
  y actualiza la aserción a la nueva clasificación — el nombre del test puede quedar
  desactualizado si prefieres no renombrarlo, pero la ASERCIÓN debe reflejar la nueva regla;
  documenta en tu reporte si renombraste o no.
- `tests/test_sensitivity.py`: revisa si depende de estos valores.
- Corre la suite completa (`python -m pytest -q`, puedes excluir los tests de motor real
  lentos como en tareas anteriores de este repo: `--ignore=tests/test_ammonia_water_adapter.py
  --ignore=tests/test_teqp_adapter.py --ignore=tests/test_validacion_elsayed2013.py` y
  correrlos aparte si hace falta) y que no haya regresiones.

## Files

Puedes modificar: `src/restricciones/modelos.py`, `src/restricciones/operativos.py`,
`src/restricciones/composicion.py`, `src/restricciones/clasificacion.py`,
`src/ui_clasificacion.py`, `src/sensitivity.py` (solo si hace falta),
`tests/test_restricciones.py`, `tests/test_sensitivity.py`.

**NO modifiques**: `src/cycle_solver.py`, `src/properties/`, `src/components/`,
`src/restricciones/numericos.py`, `src/restricciones/segunda_ley.py` (S1-S8 no cambian),
`app.py`, `src/ui_helpers.py`, `src/ui_inputs.py`, `src/ui_campos.py`, `src/ui_barrido.py`,
`TASK_CONTEXT_fase2_*.md`, nada de `scripts/barridos_2026-09-19/` ni
`resultados/barridos_2026-09-19/` (son de otras tareas — los archivos históricos de esas
carpetas seguirán mencionando `VALIDO_ADVERTENCIA`/`DEGENERADO` en datos ya generados; eso es
esperado y NO hay que "arreglarlo", son resultados históricos con el catálogo de su momento).

## Constraints

1. Cada archivo `.py` que toques debe seguir ≤200 líneas.
2. No inventes una clasificación nueva ni una quinta/sexta categoría — son EXACTAMENTE los 4
   niveles indicados.
3. No cambies ninguna fórmula física ni umbral numérico (`0.90` de O1, `_BANDA_C1`, `DQ` de
   O5) — solo la `Clasificacion` resultante de cada rama.
4. Si algo no queda claro (p.ej. qué hacer con `Severidad` de O1/C1), repórtalo en
   `UNRESOLVED` con tu mejor criterio aplicado, no lo dejes sin resolver silenciosamente.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `TESTS`: salida real de pytest (pass/fail). En `FILES_CHANGED`: cada
archivo y qué cambió exactamente.

## Verification

`python -m pytest -q` (con las exclusiones de motor real de siempre) sin regresiones, más
confirmación explícita de que `Clasificacion` ya no tiene `VALIDO_ADVERTENCIA` ni
`DEGENERADO` (p.ej. `python -c "from src.restricciones import Clasificacion; print(list(Clasificacion))"`).

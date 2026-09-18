---
project: ciclo_kalina_tercero
task_id: 2026-09-18-validar-teqp-nh3h2o
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-18
---

# TASK_CONTEXT — Validar teqp como motor NH3-H2O alternativo (rendimiento)

## Task ID

2026-09-18-validar-teqp-nh3h2o

## Project

ciclo_kalina_tercero. El motor actual de la mezcla NH3-H2O
(`src/properties/_nh3h2o_engine.py` + `_kalina_flash.py`, IAPWS G4-01 portado) es correcto
pero **muy lento**: una corrida completa de `resolver_ciclo` con `AmmoniaWaterAdapter` tarda
**8-15+ minutos** (medido en la sesión de hoy, con las validaciones de `src/restricciones/`
añadidas — ver `CONTEXT.md`). Esta tarea investiga si `teqp` (paquete NIST, dominio público,
mismo modelo Tillner-Roth/G4-01) puede sustituirlo con el mismo rigor pero mucho más rápido.

**Esto NO es una tarea de integración al solver todavía.** Es una tarea de validación aislada:
construir un adapter de prueba, verificarlo a fondo contra el motor actual (que sí está
validado contra IAPWS G4-01 en el proyecto hermano — ver `tests/test_ammonia_water_adapter.py`
líneas 3-5), y reportar si es confiable y cuánto más rápido es. La decisión de reemplazar
`AmmoniaWaterAdapter` es una tarea posterior, solo si esta valida bien.

## Objective

1. Construir un módulo de prueba (`src/properties/_teqp_prototipo.py`, NO tocar
   `ammonia_water_adapter.py` ni ningún archivo existente) que calcule, para la mezcla NH3-H2O
   vía `teqp.AmmoniaWaterTillnerRoth()`: `h(T,P,x)`, `s(T,P,x)`, `bubble_point(P,x)`,
   `dew_point(P,x)`.
2. Cross-validar cada resultado contra el equivalente de `AmmoniaWaterAdapter` (el motor
   actual, ya validado) para al menos 8 puntos (T,P,x) distintos dentro del dominio real de
   barrido del proyecto (P_alta 2000-4000 kPa, P_baja 300-600 kPa, x_b 0.40-0.70,
   T 280-480 K aprox — ver `CAMPOS_CICLO` en `src/ui_helpers.py` para los rangos exactos de la
   UI). Reportar el error relativo de cada comparación.
3. Medir el tiempo de cada llamada de teqp y compararlo contra el tiempo medido del motor
   actual para los MISMOS puntos.
4. Reportar honestamente si teqp es confiable (no solo rápido) con la evidencia numérica.

## Context — lo ya investigado hoy (no repetir, partir de aquí)

- `pip install teqp` instala sin compilar (wheel `cp313-win_amd64`, teqp 0.23.2). `pip install
  CoolProp` igual (CoolProp 8.0.0, wheel `cp312-abi3` compatible con 3.13) — SÍ hace falta
  instalar `CoolProp` (no solo `pyfluids`) para poder generar el JSON de gas ideal de los
  componentes puros.
- `teqp.AmmoniaWaterTillnerRoth()` es un modelo de **Helmholtz residual únicamente**: expone
  `get_Ar00`, `get_Ar01`, `get_Ar10`, etc. NO da h/s directo.
- Receta oficial verificada (NIST, "Heat Pump Model",
  https://pages.nist.gov/teqp-docs/en/main/recipes/HeatPumpModel.html — leída hoy, la receta
  mostrada ahí es para un fluido puro R125, no para la mezcla; hay que adaptarla a 2
  componentes con `teqp.IdealHelmholtz([jig_nh3, jig_h2o])`):
  ```python
  jig_nh3 = teqp.convert_CoolProp_idealgas(json.dumps(json.loads(CP.get_fluid_param_string('Ammonia','JSON'))[0]), 0)
  jig_h2o = teqp.convert_CoolProp_idealgas(json.dumps(json.loads(CP.get_fluid_param_string('Water','JSON'))[0]), 0)
  aig = teqp.IdealHelmholtz([jig_nh3, jig_h2o])   # ORDEN sin confirmar, ver abajo
  model = teqp.AmmoniaWaterTillnerRoth()

  def h(T, rhomolar, molefrac):
      Atot10 = model.get_Ar10(T, rhomolar, molefrac) + aig.get_Aig10(T, rhomolar, molefrac)
      return R * T * (1 + model.get_Ar01(T, rhomolar, molefrac) + Atot10)

  def s(T, rhomolar, molefrac):
      Atot10 = model.get_Ar10(T, rhomolar, molefrac) + aig.get_Aig10(T, rhomolar, molefrac)
      Atot00 = model.get_Ar00(T, rhomolar, molefrac) + aig.get_Aig00(T, rhomolar, molefrac)
      return R * (Atot10 - Atot00)
  ```
  **IMPORTANTE**: verificar `R` — usar `model.get_R(molefrac)`, no asumir 8.314.
- **`h`/`s` toman `(T, rhomolar, molefrac)`, NO `(T, P, x)`**: hace falta resolver la densidad
  molar a la presión pedida (un solve adicional, p.ej. sobre `model.get_pr` o el método de
  presión que exponga el modelo — revisar `dir(model)` para el método de presión exacto, no
  está confirmado en esta investigación).
- El flash `model.mix_VLE_Tx(T, rhovecL0, rhovecV0, xspec, atol, reltol, axtol, relxtol,
  maxiter)` **requiere semillas de densidad para ambas fases** (no es caja negra). Probado hoy
  con semillas crudas (densidades de saturación de los puros vía CoolProp, escaladas por
  composición): convergió (`xtol_satisfied`) en **0.65 ms**, pero el resultado de la fase
  líquida salió sospechoso — `rhoL` con las DOS componentes en la MISMA densidad molar
  (`[22161.5, 22161.5]`), lo que implica composición líquida = 0.5 exactamente, igual a la
  composición global de entrada. Eso probablemente sea una **convergencia espuria/trivial**
  (el solver "convergió" sin encontrar el equilibrio físico real), NO una confirmación de que
  el flash funciona. **No confíes en ese resultado — repite con semillas mejores y verifica
  contra el motor actual antes de sacar cualquier conclusión de velocidad real.**
- **Orden de composición sin confirmar**: no se determinó si el índice 0 de
  `molefrac`/`xspec`/`rhovec*` en `AmmoniaWaterTillnerRoth` es NH3 o H2O. Determínalo
  empíricamente: evalúa en el límite `x→0`/`x→1` (o usa `pure_VLE_T` con `molefrac=[1,0]` y
  `[0,1]`) y compara el punto de ebullición resultante contra el de NH3 puro (~239.7 K a
  101.325 kPa) y H2O puro (~373.15 K a 101.325 kPa) — no lo asumas.
- **Unidades**: `AmmoniaWaterAdapter` (el motor actual) usa P en kPa y composición en
  **fracción MÁSICA** (`w`); `teqp`/`_nh3h2o_engine.py` usan P en MPa y fracción **MOLAR**.
  `_nh3h2o_engine.py` ya tiene los conversores `w2m`/`m2w` (masa↔molar) — reutilízalos para
  traducir, no reimplementes la conversión.
- Motor actual, tiempos de referencia ya medidos hoy: una corrida completa de
  `resolver_ciclo` (10 estados, ~8 llamadas al backend por iteración de cada uno de los 2
  lazos anidados) tarda 8-15+ min. `bubble_point`/`dew_point`/`equilibrio_liquido_vapor`
  individuales no se cronometraron por separado hoy — hazlo tú como parte de esta tarea
  (son la comparación directa contra `pure_VLE_T`/`mix_VLE_Tx` de teqp).

## Files

Crear (prototipo aislado, no wire al resto del proyecto):
- `src/properties/_teqp_prototipo.py` — funciones sueltas (NO necesita implementar
  `PropertyBackend`, esto es solo para medir y validar, no es la interfaz final).
- `tests/test_teqp_prototipo.py` — el cross-check contra `AmmoniaWaterAdapter` y las
  mediciones de tiempo, como tests de pytest (marca con `pytest.mark.skip` o similar si teqp
  no está instalado, para no romper el resto de la suite si alguien corre los tests sin él).

**No modifiques ningún archivo existente.** Si necesitas añadir `teqp`/`CoolProp` a
`requirements.txt`, añádelos como comentario opcional (igual que `pyfluids` ya está comentado
ahí), NO como dependencia activa — esta tarea es exploratoria.

## Constraints

- Cada archivo `.py` ≤ 200 líneas.
- No inventes la fórmula de h/s ni el orden de composición — verifícalos empíricamente como
  se describe arriba y reporta cómo los verificaste.
- No reemplaces ni toques `ammonia_water_adapter.py`, `_nh3h2o_engine.py`, `_kalina_flash.py`,
  `cycle_solver.py`, `restricciones/`, ni `sensitivity.py`.
- Si algo de la receta de h/s o el flash no converge de forma confiable tras un esfuerzo
  razonable de ajustar semillas, repórtalo en UNRESOLVED — no inventes un resultado ni ocultes
  la falla.

## Acceptance criteria

1. Al menos 8 puntos (T,P,x) comparados: `h`, `s`, `bubble_point`, `dew_point` de teqp vs.
   `AmmoniaWaterAdapter`, con el error relativo de cada uno reportado explícitamente (no solo
   "parece razonable").
2. El orden de composición (NH3 vs H2O en índice 0) queda confirmado con evidencia, no
   supuesto.
3. Tiempos de `bubble_point`/`dew_point`/flash de teqp vs. los del motor actual, medidos para
   los mismos puntos (no una comparación contra un número de otra corrida).
4. Si algún punto de comparación tiene error relativo > 1% en h/s o > 0.5 K en
   bubble/dew_point, repórtalo como discrepancia sin suavizarlo — es la señal de si teqp sirve
   o no para este proyecto.

## Expected output

Un reporte claro: ¿teqp da resultados consistentes con el motor ya validado, dentro de qué
tolerancia, y cuánto más rápido es? Con eso, el director (Claude) decide si vale la pena una
tarea de integración real (reemplazar `AmmoniaWaterAdapter`) o si se descarta.

## Verification

`pytest tests/test_teqp_prototipo.py -v` con el reporte de errores relativos y tiempos
impreso o incluido en el RESULTS de la respuesta final (no solo pass/fail de los asserts).

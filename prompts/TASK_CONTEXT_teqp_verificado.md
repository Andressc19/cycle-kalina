---
project: ciclo_kalina_tercero
task_id: 2026-09-27-teqp-verificado
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Implementar `TeqpVerificado` (opción A) sin modificar el motor

## Task ID

2026-09-27-teqp-verificado

## Project

`ciclo_kalina_tercero`. **Estás en un worktree aparte**:
`D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\teqp-doble-verificacion`, rama
`fix/teqp-doble-verificacion` (creada desde `9c40f64`). Trabaja SOLO dentro de este
directorio. No toques el directorio principal del repo ni otras ramas.

Python: este worktree no tiene `.venv` propio. Usa el intérprete del repo principal:
`D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` (ejecútalo con el cwd en
este worktree para que importe el `src/` de ESTE worktree; verifícalo imprimiendo
`src.__file__` una vez).

### El problema

`TeqpAdapter` (`src/properties/teqp_adapter.py`) es ~10× más rápido que el motor real
`AmmoniaWaterAdapter`, pero tiene un fallo silencioso: en
`src/properties/_teqp_flash.py:138-140` (`_fase_monofasica`), si
`Ta < T <= Ta + 0.3` K (`Ta, Tw = ng.Tsat_pure(P)`, T de saturación de NH3 y agua
puros), devuelve "vapor" sin calcular el equilibrio. Para mezclas muy ricas en NH3
(vapor de turbina, x ≈ 0.975) la mezcla ahí es bifásica, `s(T)` deja de ser creciente
y la inversión `TeqpAdapter._T_de` (líneas 78-89) puede caer en una raíz falsa: en
`(x_b=0.60, P_alta=4000, T_fuente=394)` con `P_baja=423.914831` kPa la salida
isentrópica de turbina sale 139 kJ/kg mal y η=0.034 en vez de 0.080, sin que ningún
criterio lo detecte. Evidencia: `REPORTE_RAMA_TURBINA.md` y
`REPORTE_COSTO_SOLUCIONES.md` del repo principal (no hace falta leerlos; lo esencial
está aquí).

### La solución decidida (opción A)

Un envoltorio **nuevo** que NO modifica el motor: hereda de `TeqpAdapter`, y solo
cuando el resultado de una llamada cae en la zona de riesgo, repite esa llamada con
`AmmoniaWaterAdapter` y usa su resultado. Fuera de la zona, resultado idéntico al de
`TeqpAdapter`. Costo medido en un prototipo: +2.8 % por punto (31.85 vs 30.98 s);
detección 0.475 ms por llamada; zona tocada en 9 de 5404 inversiones. Prototipo de
referencia (funciona, léelo y reutiliza la lógica): clase `TeqpVerificado` en
`scripts/costo_soluciones_teqp.py` (copiado en este worktree).

**Nota:** los `TASK_CONTEXT*.md` que no sean este archivo son OTRAS tareas: no los
ejecutes ni los modifiques.

## Objective

### 1. Nuevo módulo `src/properties/teqp_verificado.py` (archivo nuevo)

Clase `TeqpVerificado(TeqpAdapter)`:
- Mismo constructor que `TeqpAdapter` (`x`), más `umbral_K: float = 1.0` y
  `x_molar_rico: float = 0.9`, `x_molar_pobre: float = 0.1`.
- Instancia de `AmmoniaWaterAdapter` creada de forma perezosa (solo la primera vez que
  haga falta).
- **Zona de riesgo** (igual que el prototipo): con `Ta, Tw = ng.Tsat_pure(P_pa)` y
  `x_molar = ng.w2m(w)`: `x_molar >= x_molar_rico and abs(T - Ta) < umbral_K`, o
  `x_molar <= x_molar_pobre and abs(T - Tw) < umbral_K`. Confirma en
  `src/properties/_teqp_engine.py` los nombres y unidades de `Tsat_pure` y `w2m`.
- Métodos cubiertos:
  - inversiones: `h(P, s=, x=)`, `T_from_Ps`, `T_from_Ph` — la T a evaluar es la
    invertida por teqp (capturarla sin repetir la inversión, como hace el prototipo
    con `_T_de`);
  - llamadas directas con T: `h(P, T=, x=)` y `s(P, T=, x=)` — la T a evaluar es la
    T de entrada (chequeo antes o después de la llamada, sin costo extra de teqp).
- Si la llamada cae en zona: repetirla con el motor real y devolver ese valor.
- **Registro**: lista `self.recurrencias` de dicts (método, P, x, x_molar, T_teqp, Ta o
  Tw, valor_teqp, valor_real, t_real_s) y contador. Método `reiniciar_registro()`.
- Si el motor real falla en una recurrencia: devolver el valor de teqp PERO registrar
  el evento con `fallo=True` y exponer la propiedad `verificacion_incompleta`
  (bool) para que quien use el adapter pueda marcar el punto. No inventar valores.
- Si la inversión de teqp misma lanza excepción, se propaga como hoy (fuera de
  alcance).
- Docstring breve del por qué (zona `Ta..Ta+0.3` de `_fase_monofasica`) con
  referencia a archivo:línea. Módulo ≤ 200 líneas.

**No modificar ningún archivo existente de `src/`** (ni `teqp_adapter.py`, ni
`_teqp_flash.py`, ni `properties/__init__.py`). Se importa por ruta completa:
`from src.properties.teqp_verificado import TeqpVerificado`.

### 2. Tests `tests/test_teqp_verificado.py` (nuevo)

Parámetros comunes: efectividades 0.85/0.80/0.85, `T_sumidero=283`,
`eta_t=eta_p=0.80`, `m_b=1`.
1. **Unitario del caso espurio**: con `TeqpVerificado(x=0.60)`,
   `h(P=423.914831, s=5.704153, x=0.974965)` debe dar ~1486 kJ/kg (±3), no ~1626; y
   registrar ≥ 1 recurrencia. Con `TeqpAdapter` el mismo llamado da ~1626
   (documenta el bug; si ya no lo reproduce, que el test lo diga explícitamente).
2. **Ciclo espurio corregido**: `resolver_ciclo` con `TeqpVerificado` en
   `(0.60, 4000, 394)`, `P_baja=423.914831` → η entre 0.079 y 0.082.
3. **Sin cambios fuera de zona**: en `(0.65, 5000, 423, P_baja=704.644595)` y
   `(0.80, 5000, 394, P_baja=952.892781)`, η de `TeqpVerificado` == η de
   `TeqpAdapter` exactamente, y 0 recurrencias.
4. Tests rápidos del criterio de zona (sin motor real).

### 3. Regresión de los 22 KALINA

Script `scripts/regresion_teqp_verificado.py` (nuevo): para las 22 filas
`clasificacion == KALINA` de `resultados/2026-09-24_margen2k/barrido_margen2k.csv`
(copiado en este worktree), resolver con `TeqpAdapter` y con `TeqpVerificado` en su
`P_baja`, clasificar ambos con `evaluar_ciclo(..., T_amb_diseno=283.15)`, y registrar
η, clasificación, recurrencias, `verificacion_incompleta` y tiempo de cada uno.
Salida: `resultados/2026-09-27_teqp_verificado/regresion_22.csv` y
`REPORTE_TEQP_VERIFICADO.md` con: diferencias de η y clasificación por punto,
recurrencias totales, tiempo medio por punto de cada adapter y sobrecosto %.

### 4. Suite existente

Correr `pytest -q` en el worktree **excluyendo** `tests/test_validacion_elsayed2013.py`
y otros tests que usen solo `AmmoniaWaterAdapter` por su lentitud (no los afecta este
cambio, que no toca ese motor). Reportar pasados/fallados; si hay fallos, decir si
existían ya antes de este cambio (compara corriendo los mismos tests sin el archivo
nuevo, o revisando que no importan `teqp_verificado`).

## Files

Crear (solo en este worktree):
- `src/properties/teqp_verificado.py`
- `tests/test_teqp_verificado.py`
- `scripts/regresion_teqp_verificado.py`
- `resultados/2026-09-27_teqp_verificado/` (CSV, `run.log`, reporte)

**No modificar ningún archivo existente. No hacer commits** (Claude revisa antes).

## Constraints

- Motor real: solo en recurrencias dentro de la zona, y en los tests 1-3.
- `python -u` y logs a `resultados/2026-09-27_teqp_verificado/run.log`.
- `.py` nuevos ≤ 250 líneas (el módulo de `src/` ≤ 200).

## Acceptance criteria

1. `TeqpVerificado` corrige el caso espurio (tests 1 y 2 pasan).
2. Fuera de zona, resultados idénticos a `TeqpAdapter` (test 3 y regresión de 22).
3. Sobrecosto medido en la regresión (esperado del orden de +3 %).
4. RESULTS incluye: tests pasados/fallados, tabla resumen de la regresión,
   sobrecosto %, recurrencias y rutas.

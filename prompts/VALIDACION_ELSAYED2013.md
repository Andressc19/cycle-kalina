# Validación externa — Elsayed et al. (2013)

Resumen de la validación de `ciclo_kalina_tercero` contra un caso publicado en la
literatura académica. Hecho en la rama `test/vv-strategy`, sesión del 2026-09-19.

## Por qué esta validación

Hasta este punto el proyecto solo tenía **verificación interna** (consistencia entre
`AmmoniaWaterAdapter` y `TeqpAdapter`, balances de masa/energía, round-trips de
propiedades). Ninguna de esas pruebas compara contra un dato **externo e
independiente** — algo publicado por alguien que no escribió este código. Esta
validación cubre ese hueco: un caso numérico de un paper revisado por pares, con
una ecuación de estado NH3-H2O **distinta** a la de este repo.

## El paper

> Elsayed, A., Embaye, M., AL-Dadah, R., Mahmoud, S., & Rezk, A. (2013). *Thermodynamic
> performance of Kalina cycle system 11 (KCS11): feasibility of using alternative
> zeotropic mixtures.* International Journal of Low-Carbon Technologies, 8(suppl_1),
> i69–i78. https://doi.org/10.1093/ijlct/ctt020

Encontrado y leído completo (no solo el abstract) específicamente para esta tarea.
Modela la misma topología KCS11 (turbina, absorbedor, condensador, evaporador/HRVG,
separador, regenerador, bomba, válvula) que este repo, pero:

- Usa **Ibrahim & Klein (1993)** para las propiedades NH3-H2O (vía EES+Refprop) —
  **distinta** a la EOS de este repo (**Tillner-Roth & Friend, 1998** / IAPWS G4-01,
  la misma que implementan tanto `AmmoniaWaterAdapter` como `TeqpAdapter`). Por eso
  esta comparación mide incertidumbre **inter-modelo** real, no solo una diferencia
  de implementación entre dos motores que calculan la misma ecuación.
- Cierra HRVG, condensador y regenerador por **pinch point** (ΔT mínimo = 4 K), no
  por efectividad como este repo (`CONTEXT.md`).

**Caso numérico citado** (texto literal del paper):

> *"at a pressure of 15 bars, the KCS11 thermal efficiency (11.38%) with the
> ammonia-water concentration of 0.55... with the heat source temperature of
> 373 K and the heat sink temperature of 283 K"*

Con eficiencia isentrópica de turbina y bomba = 80% en ambos casos.

## Cómo se definió la prueba

El paper da los datos de entrada (P_alta, x_b, T_fuente, T_sumidero, η_t, η_p) pero
cierra los intercambiadores por un método distinto (pinch point) al que usa este
repo (efectividad). Para poder correr el mismo caso en `resolver_ciclo`, hubo dos
supuestos explícitos, ambos autorizados por el usuario ("traduce el pinch a una
efectividad o temperatura de entrada aproximada"):

1. **Traducción pinch → efectividad.** Las fórmulas de `CONTEXT.md` ya definen la
   efectividad como la distancia a la temperatura del reservorio (`h_ideal` se evalúa
   en `T_fuente`, `T_sumidero`, o `T10` según el componente) — el mismo terminal que
   usa el pinch del paper. Entonces:
   - HRVG: T2 objetivo = T_fuente − 4 = 369 K
   - Condensador: T9 objetivo = T_sumidero + 4 = 287 K
   - Regenerador: T6 objetivo = T10 + 4 (T10 es un resultado del propio solver, el
     paper no lo necesita porque no cierra por efectividad)
2. **P_baja asumida.** El paper no la da como dato independiente. Se fijó como la
   presión de burbuja a (T_sumidero+4 K, x_b=0.55) — la presión de condensación "de
   diseño" consistente con que el condensador entregue líquido saturado a esa
   temperatura.

## Desarrollo de la prueba

Script: [`scripts/validacion_elsayed2013.py`](scripts/validacion_elsayed2013.py).

1. **Calibración de P_baja**: búsqueda de raíz (`scipy.optimize.brentq`) sobre
   `TeqpAdapter.bubble_point` para que la presión de burbuja a x_b=0.55 dé T=287 K.
   Resultado: **P_baja = 273.55 kPa**.
2. **Calibración de ε (de primer orden, no un root-find exacto sobre el ciclo
   completo — sería carísimo en tiempo de cómputo con el motor real):**
   - Un paso base con los ε por defecto del proyecto (0.85/0.75/0.80) para obtener
     un estado de referencia (h1, T10, h5, x5, h8).
   - Con ese estado base, despeje en forma cerrada de ε_hrvg/ε_reg/ε_cond a partir
     de las fórmulas de `CONTEXT.md`, para que T2/T6/T9 den los objetivos de arriba.
   - Una corrida de verificación con esos ε calibrados.
   - Calibración con `TeqpAdapter` (rápido, ~1 min); corrida final de comparación
     con `AmmoniaWaterAdapter` (motor real, el camino real del proyecto).

## Resultados y comparaciones

**ε calibrados**: ε_HRVG=0.8882, ε_reg=0.9380, ε_cond=0.9625 — los tres bastante más
altos que los valores por defecto del proyecto (0.85/0.75/0.80), coherente con que un
pinch de 4 K es una aproximación muy cercana al ideal en este rango de temperaturas.

Qué tan cerca quedaron T2/T6/T9 de los objetivos de la traducción (verificado con
`AmmoniaWaterAdapter`):

| Objetivo | Buscado | Obtenido | Δ |
|---|---|---|---|
| T2 (HRVG, target T_fuente−4) | 369.00 K | 369.11 K | 0.11 K |
| T9 (condensador, target T_sumidero+4) | 287.00 K | 286.33 K | 0.67 K |
| T6 (regenerador, target T10+4) | 290.53 K* | 291.85 K | 1.32 K |

\* el T10 usado para fijar este objetivo fue el del paso base (304.93 K); en la
corrida final T10 convergió a 286.52 K — el regenerador es el más sensible a que la
calibración es de un solo paso (no iterada a punto fijo), por eso su residuo es el
mayor de los tres.

**Eficiencia térmica — el número que se compara contra el paper:**

| Fuente | η |
|---|---|
| Elsayed et al. (2013), paper | **11.38%** |
| `ciclo_kalina_tercero`, `AmmoniaWaterAdapter` (motor real) | **11.054%** |
| `ciclo_kalina_tercero`, `TeqpAdapter` | 11.055% |

**Diferencia: 0.33 puntos porcentuales absolutos, ~2.9% relativo.**

Resultado completo (los 10 estados: T, P, h, s, x, m, q, fase): [`validacion_elsayed2013.json`](validacion_elsayed2013.json).

## Conclusión aceptada (~3%)

**El usuario aceptó el ~2.9% de diferencia relativa como resultado de validación
final**, sin iterar la calibración a punto fijo. Razonamiento:

Un ~3% relativo es un acuerdo razonable, no un error, porque se apilan tres fuentes
de discrepancia *esperadas*, ninguna de ellas un error de cómputo:

1. **EOS distinta** (Tillner-Roth & Friend 1998 vs Ibrahim & Klein 1993 del paper) —
   esto es precisamente la incertidumbre inter-modelo que se quería medir, no ruido.
2. **Traducción aproximada** de un pinch point (que sigue el perfil de temperatura
   con *glide* de la mezcla, no lineal) a una efectividad terminal de un solo paso,
   no iterada a convergencia exacta.
3. **P_baja asumida** — el paper no la da como dato.

**Verificación adicional, gratis**: `AmmoniaWaterAdapter` y `TeqpAdapter` coinciden
en η a 0.001 puntos porcentuales en este punto de operación — muy distinto del caso
por defecto del proyecto (P_alta 5x menor, T_fuente 97 K menor) — refuerza la
confianza en que ambos motores implementan la misma EOS consistentemente fuera del
rango ya probado antes.

## Test persistente

[`tests/test_validacion_elsayed2013.py`](tests/test_validacion_elsayed2013.py) —
usa los ε/P_baja ya calibrados arriba (fijos, no se recalibran en cada corrida de la
suite) y corre el ciclo una vez con `AmmoniaWaterAdapter`, verificando que η quede
dentro de **5% relativo** del 11.38% del paper. Tolerancia deliberadamente holgada
(no es la 1e-3 de los balances internos): compara contra una EOS distinta con una
traducción aproximada, no un balance interno del propio ciclo. Pasa:
`1 passed in 256.67s`.

## Nota sobre alcance (fuera de esta validación)

Durante esta sesión también se investigó por qué este repo no modela la fuente/
sumidero con capacidad calorífica finita (masa de gas + Cp), como sí lo hacía el
proyecto original del curso — se decidió **mantener el alcance actual** (reservorios
de capacidad infinita), sin cambios de código. Detalle completo en el vault de
Obsidian del proyecto (`decisiones/alcance-fuente-capacidad-infinita-ciclo-kalina-
tercero-20260919.md`).

## Ver también

- Metodología y decisiones con más detalle: vault de Obsidian del proyecto,
  `04_PROJECTS/active/Ciclo Kalina/decisiones/validacion-elsayed2013-ciclo-kalina-
  tercero-20260919.md`.

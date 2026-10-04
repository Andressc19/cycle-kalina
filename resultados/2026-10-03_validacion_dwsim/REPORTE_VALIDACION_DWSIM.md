# Reporte — Validación cruzada: solver del proyecto vs DWSIM con el mismo cierre por efectividad

Fecha: 2026-10-03. Tarea: `prompts/TASK_CONTEXT_validacion_dwsim.md`. Rama: `feature/rango_motores`; `src/` sin cambios.

## La pregunta

1. ¿Cuánto difieren los dos motores del proyecto (motor real `AmmoniaWaterAdapter` y `TeqpVerificado`)?
2. Si DWSIM resuelve **exactamente las mismas ecuaciones de cierre por efectividad** que el
   solver del proyecto, ¿cuánto difiere su resultado? Así la única diferencia que queda es el
   modelo de propiedades (Tillner-Roth & Friend en el proyecto, Peng-Robinson en DWSIM).

## Cómo funciona (en simple)

- **Efectividad (ε)**: qué fracción del intercambio máximo posible hace un intercambiador.
  El proyecto la define sobre entalpías (CONTEXT.md). DWSIM no trae esa definición, así que
  se impuso "desde afuera": un lazo en Python calcula con el mismo Peng-Robinson las
  entalpías de referencia (h2,max, h6,min, h9,min), las convierte en temperaturas de salida
  (T2, T9 y la ΔT del regenerador) y se las da a DWSIM; repite hasta que las tres
  especificaciones dejan de cambiar (residuo < 1e-3 K).
- **Sub-relajación**: en cada vuelta se aplica solo el 70 % del cambio, para no "pasarse"
  (como un termostato que corrige suave).
- No se comparan entalpías absolutas (cada modelo tiene su propio cero), sino trabajos,
  calores, η, temperaturas, composiciones y caudales.

## Cómo se desarrolló

- **Etapa 2 (OpenCode, corridas 047–048)**: `scripts/dwsim/motor_puntos_validacion.py`
  resolvió los 6 puntos con los dos motores → `motor_puntos.csv` (motor real 7.5–10.5
  min/punto). Coincide con resultados previos (KALINA-11/21/22 en
  `2026-09-24_verificacion`, ELSAYED = 11.054 % de la validación §7).
- **Etapa 1 (OpenCode empezó, Claude terminó tras rate limit del proveedor)**:
  `scripts/dwsim/_kcs11_dwsim_base.py` (diagrama) + `kcs11_efectividad_dwsim.py` (lazo).
  La primera versión de OpenCode (calor fijo + corte en la bomba sustituido) **oscilaba**
  60 iteraciones sin cerrar; se reformuló imponiendo temperaturas de salida y fijando el
  corte S9 a la misma T9 → converge en 8–10 iteraciones (~30 s).
- **Etapa 3 (Claude)**: `scripts/dwsim/comparar_validacion.py` → `comparacion.csv`.
- Verificación de cada punto DWSIM: energía de cada equipo = cambio de entalpía de sus
  corrientes; cierre global; ε resultantes = ε pedidas.

## Resultados

### Tolerancia entre los dos motores del proyecto (6 de 6 puntos)

| Punto | η motor real | η teqp | teqp − real |
|---|---|---|---|
| ELSAYED | 11.0542 % | 11.0554 % | +0.0011 pp |
| KALINA-11 | 12.1492 % | 12.1500 % | +0.0009 pp |
| KALINA-22 | 11.0574 % | 11.0591 % | +0.0017 pp |
| KALINA-21 | 9.7334 % | 9.7348 % | +0.0014 pp |
| KALINA-01 | 10.3704 % | 10.3716 % | +0.0012 pp |
| KALINA-16 | 11.7994 % | 11.8002 % | +0.0008 pp |

Diferencia < 0.002 pp de η (~0.01 % relativo); T de estados < 0.03 K; x3, x5, m3 iguales a
5 decimales.

### Proyecto vs DWSIM con el mismo cierre por efectividad (2 de 6 puntos)

| Punto | η motor real | η DWSIM-ε | DWSIM − real | Verificación DWSIM |
|---|---|---|---|---|
| ELSAYED (1500 kPa) | 11.054 % | 11.644 % | +0.59 pp (+5.3 %) | equipos 0.0000 kW; cierre −0.010 kW; Δε ≤ 3e-5 |
| KALINA-01 (3000 kPa) | 10.370 % | 10.741 % | +0.37 pp (+3.6 %) | equipos 0.0000 kW; cierre −0.002 kW; Δε ≤ 5e-6 |

Detalle ELSAYED (DWSIM − motor real): caudal a turbina m3 **+10.2 %**, Wt +11.0 %, Qi
+5.4 %; x5 −0.020; x3 +0.0007; temperaturas dentro de ±2.4 K (máx. T8). KALINA-01: m3
+6.1 %, Wt +7.1 %, Qi +3.2 %; temperaturas dentro de ±1.7 K.

**Descomposición del caso ELSAYED** (antes no se sabía):

| Fuente | η | Paso |
|---|---|---|
| Motor del proyecto (efectividad) | 11.05 % | — |
| DWSIM con efectividad | 11.64 % | +0.59 pp = **efecto de las propiedades** (PR vs Tillner-Roth) |
| DWSIM con pinch 4 K | 12.20 % | +0.56 pp = **efecto del cierre** (pinch vs ε calibradas) |

### Puntos que DWSIM no pudo resolver (4 de 6)

KALINA-11, -16, -21, -22 (P_alta 4000–5000 kPa, x_b 0.65–0.80): el flash P-T del
Peng-Robinson de DWSIM agota iteraciones en **líquido comprimido** (regenerador o bomba).
Sonda `_dbg_franja.py`: a 5000 kPa falla en temperaturas sueltas/franjas (w=0.80: 300–301.5 K;
w=0.65: 314–319 K). No se destrabó con más iteraciones, otras tolerancias, amortiguamiento,
reintentos con desplazamientos de hasta ±0.25 K ni cambiando el algoritmo de flash (los 7
probados dan idéntico resultado). Además, `CalculateFlowsheet2` **devuelve cero errores** con
media planta sin calcular: ahora el script lo detecta equipo por equipo.

## Conclusión

- **Motores del proyecto**: teqp (A+B) y motor real son intercambiables para η (< 0.002 pp).
- **Modelo matemático**: con las mismas ecuaciones de cierre, DWSIM — implementación
  independiente — llega a η a +0.4–0.6 pp; todos sus balances y efectividades cuadran. La
  diferencia sale de las propiedades: PR separa más vapor en el separador (m3 +6–10 %), en
  línea con su error medido contra IAPWS G4-01 (fracción de vapor 0.03, Δh 4 %; sonda de
  paquetes). Esto **respalda la estructura del modelo** (topología y balances), no las
  propiedades del motor (esas se verifican contra IAPWS G4-01).
- La diferencia de 1.15 pp que se veía antes en ELSAYED se reparte casi por mitades entre
  propiedades y forma de cierre.

## Lo que no sabemos

- Cómo se comporta la comparación a 4000–5000 kPa: DWSIM-PR no resuelve esos puntos. Con 2
  puntos (1500 y 3000 kPa) no se puede afirmar una tendencia de la diferencia con P_alta.
- Si otro simulador con un modelo NH3-H2O de referencia (p. ej. con REFPROP) cerraría la
  brecha de propiedades: DWSIM no lo tiene.

## Qué sigue

1. Si se quieren más puntos comparables: elegir puntos KALINA con P_alta ≤ 3000 kPa
   (donde DWSIM-PR sí resuelve), p. ej. KALINA-06/-12/-17 de `regresion_22.csv`.
2. Decidir si esta comparación entra a `PLANTEAMIENTO_MATEMATICO.md` §7 como evidencia
   adicional (tercera columna) y si se versiona `scripts/dwsim/`.
3. Los `_dbg_*`/`_explora_*` de esta carpeta son evidencia de diagnóstico; se pueden archivar.

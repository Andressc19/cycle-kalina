# Caso Húsavík — Base KALINA anclada al caso real

**Tarea:** `2026-09-19-fase3-caso-real` · **Fecha:** 2026-09-19 · **Worktree:** `barridos-tercero-f7448d`

## 1. Caso real (destino del anclaje)

| Parámetro | Valor | Origen |
|---|---|---|
| Planta | Húsavík, Islandia (geotérmica, c. 2000, ~2 MW) | TASK_CONTEXT (Mlcak et al.) |
| `T_fuente` | 394.15 K (121 °C, salmuera) | citado |
| `T_sumidero` | 278.15 K (5 °C, agua de enfriamiento) | citado |
| `x_b` | 0.82 (fracción másica NH3) | citado |
| `P_alta` | 3300 kPa (32–34 bar) | citado |
| `P_baja` | **no publicada** → calibrada (abajo) | regla B0 |
| `eta_t` / `eta_p` | 0.90 / 0.80 | citados |

## 2. Calibración y ajustes (trazabilidad)

1. **Calibración mínima de `P_baja`** (regla B0): `bubble(P_baja, x_b=0.82) = T_sumidero + 3 K = 281.15 K` → **467.6 kPa**. Con esa presión el punto converge pero clasifica `CORREGIBLE` por el criterio **O2**: bajo el peor caso ambiental (`T_amb = max(T_sumidero, 30.4 °C) = 303.55 K`) el piso de la succión de bomba queda `T9_amb ≈ 303.55 K` y cualquier `P_baja ≤ 1000 kPa` deja `bubble(P_baja) < T9_amb` → riesgo de cavitación.
2. **Ajuste autorizado dentro de CAMPOS_CICLO** (el criterio O2 sugiere "aumentar el margen de subenfriamiento de diseño del condensador"): `P_baja` **1200 kPa**, `eps_reg` **0.95**, `eps_cond` **0.95**. `eta_t = 0.90`, `eta_p = 0.80`, `x_b = 0.82`, `P_alta = 3300`, `eps_hrvg = 0.85` quedan **sin ajustar** (valores citados/default).
3. **Resultado:** clasifica **KALINA** (pasa los 17 criterios). La frontera O2 está en `P_baja ≈ 1175–1200 kPa`; la base se deja en 1200 con margen ~1–3 K.

## 3. Estados de la base (TeqpAdapter, `m_b = 1.0 kg/s`)

| Estado | Descripción | T (K) | P (kPa) | h (kJ/kg) | x (fracción NH3) | m (kg/s) |
|---|---|---|---|---|---|---|
| 1 | Mezcla al evaporador | 321.77 | 3300 | 382.81 | 0.82000 | 1.0000 |
| 2 | Salida evaporador | 380.53 | 3300 | 1277.58 | 0.82000 | 1.0000 |
| 3 | Vapor separador | 380.53 | 3300 | 1781.13 | 0.98114 | 0.6177 |
| 4 | Salida turbina | 328.15 | 1200 | 1647.33 | 0.98114 | 0.6177 |
| 5 | Líquido separador | 380.53 | 3300 | 463.96 | 0.55964 | 0.3823 |
| 6 | Salida regenerador líquido | 292.61 | 3300 | 36.84 | 0.55964 | 0.3823 |
| 7 | Entrada condensador 1 | 292.96 | 1200 | 36.84 | 0.55964 | 0.3823 |
| 8 | Mezcla recombinada (entrada condensador 2) | 327.64 | 1200 | 1031.64 | 0.82000 | 1.0000 |
| 9 | Salida condensador | 287.29 | 1200 | 215.77 | 0.82000 | 1.0000 |
| 10 | Salida bomba | 287.78 | 3300 | 219.53 | 0.82000 | 1.0000 |

| Balance | Valor |
|---|---|
| `Qi` (evaporador) | 894.77 kW |
| `Qout` (condensadores) | 815.87 kW |
| `Wnet` | **78.90 kW** (a `m_b = 1.0 kg/s`) |
| `eta` | **0.0882 (8.82 %)** |

## 4. Confirmación con motor real (iapws G4-01)

`AmmoniaWaterAdapter` (lento, ~5.8 min/punto; warnings numéricos internos del flash que **no** afectan el resultado):

| Punto | Teqp (η / Wnet) | Motor real (η / Wnet) | Clasificación |
|---|---|---|---|
| Base (3300, 1200, 0.82, 0.90, 0.95, 0.95) | 0.08818 / 78.90 | 0.08817 / 78.89 | **KALINA** |
| Vecino (3300, 1150, 0.82, 0.90, 0.95, 0.98) | 0.09002 / 81.80 | 0.09000 / 81.78 | **KALINA** |

Coincidencia ≤ 0.02 % → consistencia de ambos motores.

## 5. Sensibilidad (una variable a la vez; CSVs en esta carpeta)

| Barrido | Valores → clasificación (η) | Lectura |
|---|---|---|
| `P_alta` (kPa) | 3000 → CORR (0.081); 3200 → CORR (0.086); **3300 → KALINA (0.088)**; 3400 → KALINA (0.090); 3500 → KALINA (0.092) | Frontera O2 en `P_alta ≈ 3250–3300`; η sube con P_alta (~+4 %/500 kPa) |
| `x_b` | 0.78 → KALINA (0.086); 0.80 → KALINA (0.087); **0.82 → KALINA (0.088)**; 0.84 → CORR (0.089); 0.86 → CORR (0.090) | Frontera O2 en `x_b ≈ 0.83`; a mayor NH3 el óptimo de η cae justo sobre la frontera |
| `P_baja` (kPa) | 1100 → CORR (0.095); 1150 → CORR (0.092); **1200 → KALINA (0.088)**; 1250 → KALINA (0.085); 1300 → KALINA (0.082) | Frontera O2 en `P_baja ≈ 1175`; η cae ~−1.3 %/100 kPa de margen de diseño |

**Observación:** el máximo de eficiencia (η ≈ 0.089–0.095) queda *justo en la frontera O2*; la base elegida (P_baja = 1200) sacrifica ~0.006 de η para contar con margen de cavitación bajo el peor caso ambiental.

## 6. Veredicto

**SÍ hay una base KALINA anclada al caso real** dentro de `CAMPOS_CICLO`, confirmada con el motor real. Presupuesto usado: **69 puntos** en `busqueda_husavik.csv` (búsqueda + ajustes) + **12** en CSVs de sensibilidad + **2** con motor real (≈ 83 de 150–200 permitidos).

**Reservas honestas:**
1. `P_baja` no está publicada para Húsavík: la calibración mínima (467.6 kPa) queda `CORREGIBLE` (O2) bajo la cota ambiental de diseño de 30.4 °C; se adoptó 1200 kPa como margen de subenfriamiento (sugerencia literal del propio criterio O2). Costo: ~12 % de η y pinch de condensador real ≈ 9 K (vs. 3 K de la regla B0).
2. `eps_cond = 0.95` y `eps_reg = 0.95` son efectividades altas (dentro del rango 0.05–0.99 de `CAMPOS_CICLO`; el modelo usa efectividad hacia el mínimo termodinámico, no NTU).
3. `eta_t = 0.90` citado no da KALINA con `eps_cond = 0.80`: se necesitaron las efectividades altas (no se modificó η_t ni η_p).

## 7. Archivos producidos (solo dentro del alcance de la tarea)

- `scripts/barridos_2026-09-19/fase3_real/busqueda_base_husavik.py` (búsqueda A/B/C, 45 pts)
- `scripts/barridos_2026-09-19/fase3_real/ajuste_p_baja_husavik.py` (frontera O2, 24 pts)
- `scripts/barridos_2026-09-19/fase3_real/confirma_motor_real.py` (2 pts, iapws G4-01)
- `scripts/barridos_2026-09-19/fase3_real/sensibilidad_husavik.py` (3 barridos, 12 pts)
- `resultados/barridos_2026-09-19/fase3_real/busqueda_husavik.csv` (69 filas, esquema `tabla_barrido`)
- `resultados/barridos_2026-09-19/fase3_real/sensibilidad_{palta,xb,pbaja}.csv`
- `resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real.json`
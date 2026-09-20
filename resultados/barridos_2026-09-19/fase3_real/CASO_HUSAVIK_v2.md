# Caso Húsavík v2 — Base KALINA con `T_amb_diseno` realista (283.15 K)

**Tarea:** `2026-09-20-actualizar-rangos-fase2-fase3` · **Fecha:** 2026-09-20 ·
**Rama:** `fix/temperatura-ambiente` (worktree `barridos-tercero-f7448d`)

**Etapa:** determinación de rangos/candidatos (NO es el barrido de sensibilidad
final). Cambio central vs v1: el criterio O2 ya no se evalúa contra el piso
tropical heredado 303.55 K (físicamente incorrecto para Islandia) sino contra
**`T_amb_diseno = 283.15 K` (10 °C)** — margen conservador de 5 °C sobre la
temperatura real de diseño del caso (decisión explícita del director).

---

## 1. Candidato base v2 (confirmado con el motor real)

### 1.0 ANCLA FINAL (decisión del director, 2026-09-20): 690 / 0.75 / 0.95

> **El candidato elegido es `P_baja=690 kPa, eps_reg=0.75, eps_cond=0.95`** —
> no 670/0.95/0.95. Decisión por robustez (margen O2 +1.19 K vs +0.30 K del
> 670, que quedaba al filo) y realismo físico (eps_reg vuelve a su default
> 0.75; el forzado 0.95 era poco realista). Este punto SOLO se había probado
> con `TeqpAdapter`; se confirma aquí con el motor real — cierra el vacío
> metodológico de anclar un barrido de sensibilidad a un punto no verificado
> con el motor riguroso, dado que ya se documentó que `TeqpAdapter` y el motor
> real discrepan cerca de fronteras de clasificación.

**Confirmación con motor real (`AmmoniaWaterAdapter`, iapws G4-01) — punto
exacto (3300/690/0.82/0.90/0.80/0.85/0.75/0.95, `T_amb_diseno=283.15 K`):**

| Métrica | TeqpAdapter | Motor real | Dif. rel. |
|---|---|---|---|
| Clasificación | KALINA | **KALINA** (17/17) | — |
| η | 0.12732 | **0.12730** | −0.018 % |
| Wnet | 117.588 kW | 117.570 kW | −0.016 % |

(Archivo: `confirmacion_motor_real_690.json`. Los valores Teqp se
re-calcularon en la misma corrida, like-for-like, y reproducen la tabla de
diagnóstico del §2.)

**Histórico conservado (sigue siendo un punto de referencia válido, ya NO es
el candidato elegido):** la comparación 670/0.95/0.95 de la tabla de abajo se
mantiene intacta como referencia de menor pinch y mayor η (0.13445), pero se
descarta como ancla por margen O2 al filo (+0.30 K) y por el `eps_reg=0.95`
forzado.

| Variable | v2 (nuevo) | v1 (viejo) | caso real citado |
|---|---|---|---|
| P_alta | 3300 kPa | 3300 kPa | 3300 (32-34 bar) |
| **P_baja** | **670 kPa** | **1200 kPa** | no publicada (calibrada) |
| x_b | 0.82 | 0.82 | 0.82 |
| T_fuente | 394.15 K | 394.15 K | 121 °C |
| T_sumidero | 278.15 K | 278.15 K | 5 °C |
| eta_t / eta_p | 0.90 / 0.80 | 0.90 / 0.80 | citados |
| eps_hrvg | 0.85 | 0.85 | — |
| **eps_reg** | **0.95** (0.75 también pasa, §2) | **0.95** | — |
| **eps_cond** | **0.95** | **0.95** | — |
| **T_amb_diseno** | **283.15 K** (nuevo) | 303.55 K (heredado) | 5 °C reales → piso 10 °C |

**Resultados (motor real `AmmoniaWaterAdapter`, iapws G4-01):**

| Métrica | TeqpAdapter | Motor real |
|---|---|---|
| η | 0.13447 | **0.13445** |
| Wnet | 120.44 kW | 120.42 kW |
| Clasificación | KALINA | **KALINA** (17/17) |
| Margen O2 (T_sat_L − T9_amb, a 283.15) | +0.30 K | +0.30 K |
| Pinch de condensador (T9 − T_sumidero) | 8.68 K | 8.67 K |

### Comparación explícita vs v1 (1200 kPa, pinch ~9 K)

| Métrica | v1 (303.55 K) | v2 (283.15 K) | Δ |
|---|---|---|---|
| **P_baja mínima que pasa O2** | 1200 kPa | **670 kPa** | **−44 %** |
| **η** | 0.0882 | **0.13447** | **+52.5 % rel.** |
| Wnet | 78.90 kW | 120.44 kW | +52.6 % |
| Pinch de condensador (T9−T_sumidero) | 9.14 K | 8.68 K | −0.5 K (≈ igual; lo gobierna eps_cond, no T_amb_diseno) |
| Margen O2 relativo a su piso | +0.08 K (knife-edge) | +0.30 K | 3.8× mayor |
| T_sat_L − blanco B0 (T_sumidero+3 K) | 30.1 K | 10.7 K | mucho más cerca del mínimo de condensación |

**Lectura honesta:** el piso realista de Islandia baja el `P_baja` necesario de
1200 a 670 kPa y casi duplica la eficiencia. NO llega al mínimo calibrado de
~468 kPa (pinch ~3 K) porque el criterio O2 evalúa el condensador a
`max(T_sumidero, T_amb_diseno)=283.15 K` y, con `eps_cond=0.95`, el estado 9
re-resuelto queda pegado a la saturación (T9_amb ≈ 291.5 K, con T8 ≈ 308 K): se
necesita `bubble(P_baja) ≥ ~291.5 K` ⇒ `P_baja ≥ ~670 kPa`. Llegar a 468 kPa
exigiría `T_amb_diseno ≈ 281 K` **y** `eps_cond → 1`, i. e., margen cero — no es
un punto de diseño defendible.

### Los 2 pisos comparados en el mismo punto (motor real, like-for-like)

Punto único (3300, 670, 0.82, 0.90, 0.85/0.95/0.95):

| T_amb_diseno | Clasificación | Causa |
|---|---|---|
| **283.15 K (v2)** | **KALINA** (η=0.13445) | — |
| 303.55 K (viejo) | CORREGIBLE (O2) | T9_amb medido 303.74 K > bubble 291.84 K |

Prueba directa de que era el piso tropical heredado lo que obligaba a 1200 kPa.

---

## 2. Barrido v2 y relajación de efectividades

`busqueda_husavik_v2.csv` (37 puntos, Paso 20 kPa en P_baja 470–1190 + 3 puntos
línea B):

- **Línea A** (eps_reg=0.95, eps_cond=0.95, valores ya usados): 470–630 kPa
  → CORREGIBLE (O2, margen −2.1 a −0.05 K); **670 kPa → primer KALINA**
  (margen +0.30 K, η=0.13447); 690–1190 → KALINA con margen creciente
  (+1.2 a +19 K) y η decreciente (0.132 → 0.089).
- **Línea B** (defaults eps_reg=0.75, eps_cond=0.80) en 630–670: CORREGIBLE
  (margen −1.0 K). Con defaults solos no alcanza.
- **Diagnóstico de relajación** (en P_baja=690, Teqp):

| eps_reg | eps_cond | T_amb 283.15 | T_amb 303.55 |
|---|---|---|---|
| 0.95 | 0.95 | **KALINA** (η=0.13223) | CORREGIBLE |
| **0.75** | **0.95** | **KALINA** (η=0.12732) | CORREGIBLE |
| 0.95 | 0.80 | CORREGIBLE | CORREGIBLE |
| 0.75 | 0.80 | CORREGIBLE | CORREGIBLE |

**Mejora adicional reportable:** con `T_amb_diseno=283.15`, **`eps_reg` ya no
necesita forzarse a 0.95** — con su default 0.75 el punto sigue KALINA
(η=0.12732, −3.7 % respecto a 0.95). Solo `eps_cond=0.95` sigue siendo
necesario (0.80 no alcanza). En v1 ambas efectividades tenían que llevarse a
0.95.

**Resolución (2026-09-20):** el director eligió la alternativa con más colchón
como ANCLA FINAL: **P_baja=690 kPa, eps_reg=0.75, eps_cond=0.95** (margen O2
+1.19 K, η=0.12730 confirmado con motor real — ver §1.0). El punto de menor
pinch (670/0.95/0.95, η=0.13445) queda como referencia histórica válida, no
como candidato. El barrido de sensibilidad posterior deberá cubrir las 4
combinaciones de esta tabla alrededor del ancla 690/0.75/0.95.

---

## 3. Estados de la base v2 (motor real, m_b = 1.0 kg/s, P_baja=670)

| Estado | Descripción | T (K) | P (kPa) | x (fracción NH3) | m (kg/s) |
|---|---|---|---|---|---|
| 1 | Mezcla al evaporador | 307.87 | 3300 | 0.820 | 1.0000 |
| 2 | Salida evaporador | 359.64 | 3300 | 0.820 | 1.0000 |
| 3 | Vapor separador | 359.64 | 3300 | 0.97487 | 0.6032 |
| 4 | Salida turbina | 310.35 | 670 | — | 0.6032 |
| 5 | Líquido separador | 359.64 | 3300 | 0.58748 | 0.3968 |
| 8 | Mezcla recombinada (entrada condensador) | 308.03 | 670 | 0.820 | 1.0000 |
| 9 | Salida condensador | 286.82 | 670 | 0.820 | 1.0000 |

| Balance | Valor |
|---|---|
| `Qi` (evaporador) | 895.5 kW |
| `Qout` (condensadores) | 775.1 kW |
| `Wnet` | **120.42 kW** |
| `eta` | **0.13445** |

(En el JSON de confirmación, `T1/T2/T8/T9/x3/x5/m_v/m_l/Qi/Qout`; los estados
4/6/7/10 no se volcaron al JSON en esta corrida.)

---

## 4. Tabla de rangos propuesta para el análisis de sensibilidad posterior

(NO se ejecuta en esta tarea — requiere autorización del director.)

Alrededor del ANCLA FINAL (3300 / 690 / 0.82 / 0.90 / 0.85 / 0.75 / 0.95):

| # | Variable | Límites | Centro (candidato) | Justificación |
|---|---|---|---|---|
| 1 | `P_baja` | 600 – 800 kPa | **690** | Variable crítica: frontera O2 en ~660-670; mapear ambos lados (CORREGIBLE abajo, KALINA arriba) |
| 2 | `eps_cond` | 0.90 – 0.99 | **0.95** | Única efectividad que no se puede relajar (0.80 falla; verificar hasta dónde aguanta) |
| 3 | `eps_reg` | 0.75 – 0.95 | **0.75** | Relajado al default (decisión de ancla); probar si 0.90/0.85 siguen pasando |
| 4 | `x_b` | 0.78 – 0.86 | **0.82** | Frontera O2 de composición ya vista en v1 (~0.83) |
| 5 | `eta_t` | 0.85 – 0.95 | **0.90** | Valor citado; vigilar O1 (q4 ≥ 0.90) y η |

Fijas: `P_alta=3300`, `T_fuente=394.15`, `T_sumidero=278.15`, `m_b=1.0`,
`eta_p=0.80`, `eps_hrvg=0.85`, **`T_amb_diseno=283.15`** (este ya es el piso
realista; no se debe volver a usar 303.55 para Islandia salvo nueva decisión
del director).

---

## 5. Trazabilidad y límites

- Archivos nuevos con sufijo `_v2` (no se tocó el historial v1):
  `busqueda_husavik_v2.py`, `confirma_motor_real_v2.py`,
  `busqueda_husavik_v2.csv`, `confirmacion_motor_real_v2.json`, este informe.
- Confirmación del ANCLA final (tarea `2026-09-20-fase3-confirma-690`):
  `confirma_690.py` + `confirmacion_motor_real_690.json`. Motor real: **+1
  punto** (690/0.75/0.95 → KALINA, η=0.12730). Teqp: **+1 punto** de referencia
  like-for-like en la misma corrida (η=0.12732) — ver §1.0.
- Puntos Teqp: **40** (37 línea A + 3 línea B; tope ~150). Motor real: **1
  punto, 2 clasificaciones** (mismo punto con 283.15 y 303.55 — cabe en el tope
  de 1-2 confirmaciones).
- Calibración B0 intacta: `bubble_point(P_baja, 0.82) = 281.15 K` →
  `P_baja = 467.6 kPa` (misma regla y valor que v1).
- Todo punto probado registrado en `busqueda_husavik_v2.csv` (esquema
  `tabla_barrido` + T_sat_L / T9_amb / O2_margen / pinch_K).
- No se modificó nada de `src/`, ni `TASK_CONTEXT*.md`, ni el historial v1.
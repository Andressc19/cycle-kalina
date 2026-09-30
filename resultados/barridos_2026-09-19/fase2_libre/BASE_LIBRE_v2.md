# BASE LIBRE v2 — Fase 2 (búsqueda libre): nuevo candidato KALINA con x_b bajo

**Task:** `2026-09-20-actualizar-rangos-fase2-fase3` · **Fecha:** 2026-09-20 ·
**Rama:** `fix/temperatura-ambiente` (worktree `barridos-tercero-f7448d`)

**Etapa:** determinación de rangos/candidatos (NO es el barrido de sensibilidad
final — ese requiere autorización aparte del director). Esta iteración v2
explota la palanca nueva `x_b` bajo (0.35–0.50, nunca probada en v1) para dejar
de forzar `eps_cond=0.99`.

---

## 1. Candidato base v2 (confirmado con el motor real)

| Variable | v2 (nuevo) | v1 (viejo) | profesor |
|---|---|---|---|
| P_alta | 3000 kPa | 3000 kPa | 3000 |
| **P_baja** | **400 kPa** | **450 kPa** | 400 |
| **x_b** | **0.40** | **0.50** | 0.50 |
| **T_fuente** | **470.0 K** | **470.0 K** | 623.15 K (corregido en CONTEXT.md) |
| T_sumidero | 300.032917 K | 300.032917 K | 300.032917 |
| m_b | 1.0 kg/s | 1.0 kg/s | 1.0 |
| eta_t | 0.85 | 0.85 | 0.85 |
| eta_p | 0.75 | 0.75 | 0.75 |
| eps_hrvg | 0.85 | 0.85 | 0.85 |
| eps_reg | 0.75 | 0.75 | 0.75 |
| **eps_cond** | **0.95** | **0.99** | 0.80 |
| **T_amb_diseno** | **303.55 K** (default) | 303.55 K | — |

**Resultados (motor real `AmmoniaWaterAdapter`, iapws G4-01):**

| Métrica | TeqpAdapter | Motor real |
|---|---|---|
| η | 0.12429 | **0.124296** |
| Wnet | 166.61 kW | 166.62 kW |
| Clasificación | KALINA | **KALINA** (17/17 criterios) |
| Margen O2 (T_sat_L − T9_amb) | +3.91 K | — (misma mecánica) |

### Comparación explícita vs candidato v1 (450 kPa, x_b=0.50, eps_cond=0.99)

| Métrica | v1 | v2 | Δ |
|---|---|---|---|
| η (motor real) | 0.12276 | 0.124296 | **+1.25 % rel.** |
| Wnet | 218.78 kW | 166.62 kW | −23.8 % (honesto: x_b menor ⇒ menos fracción de vapor ⇒ menos Wnet; η manda) |
| eps_cond | **0.99** (borde de `CAMPOS_CICLO`, poco realista) | **0.95** | exigencia de diseño relajada |
| P_baja | 450 kPa (movida del default) | **400 kPa (default del profesor)** | se recupera la base del profesor |
| Regla de otra variable | nada | | x_b 0.50 → 0.40 (nueva palanca, dentro de CAMPOS_CICLO) |
| Margen O2 | 0.41–0.45 K en el punto 450/0.98 no-KALINA; el 450/0.99 quedaba "cómodo" | +3.91 K | margen ~9× mayor |

**Por qué la palanca nueva funciona:** con `x_b` menor (más agua en la mezcla),
el bubble point a `P_baja` sube de forma importante — a 400 kPa:
`T_sat_L(0.50)=304.5 K` → `T_sat_L(0.40)=320.9 K`. Eso relaja el criterio O2
(cavitación, evaluado contra `T_amb_diseno=303.55 K`) SIN necesidad de subir
`eps_cond` hasta 0.99 ni de mover `P_baja` de su default. Es justo la palanca
que el director sospechaba ("x_b más bajo nunca probado").

**Por qué NO se toca `T_amb_diseno` en Fase 2:** este es el caso del profesor,
y su propia tabla horaria real de temperatura ambiente SÍ alcanza 30.4 °C
(= 303.55 K) en la hora 17 (dato del TASK_CONTEXT, no supuesto mío). El piso de
diseño 303.55 K es correcto aquí; bajarlo estaría contradiciendo el clima del
propio caso. Se documenta como decisión explícita.

---

## 2. Barrido v2 (`busqueda_libre_v2.csv`, 80 puntos TeqpAdapter, 4 workers)

Escanearon `x_b = {0.35, 0.40, 0.45, 0.50}` × `P_baja = {400..600 paso 50}` ×
`eps_cond = {0.80..0.95 paso 0.05}`, resto en defaults de CONTEXT.md, con
`T_amb_diseno=303.55`.

- **76/80 convergen**, **19 KALINA**, 57 CORREGIBLE (todos por O2), 4
  NO_CONVERGIO (borde de campana del motor teqp: 450/0.45/0.90, 500/0.35/0.95,
  600/0.35/0.95, 600/0.40/0.90 — mismo tipo de falla de dominio ya vista en v1).
- **Patrón:** los KALINA aparecen con `eps_cond ≥ 0.90` y `x_b ≤ 0.45`; a
  `x_b=0.50` NINGÚN punto del rango razonable clasifica (coherente con v1, que
  necesitaba 0.99). Todos los CORREGIBLE son O2 (ningún otro criterio bloquea).
- Mejores KALINA:

| P_baja | x_b | eps_cond | η | Wnet | margen O2 |
|---|---|---|---|---|---|
| **400** | **0.40** | **0.95** | **0.12429** | 166.6 | **+3.91 K** |
| 400 | 0.35 | 0.90 | 0.12191 | 134.7 | +3.13 K |
| 400 | 0.35 | 0.95 | 0.11826 | 134.0 | +15.19 K |
| 450 | 0.40 | 0.95 | 0.11767 | 157.7 | +7.61 K |
| 500 | 0.45 | 0.95 | 0.11620 | 179.1 | +0.45 K (filo) |

**Criterio de selección:** mayor η dentro del rango razonable (`eps_cond ≤
0.95`, no forzado al extremo 0.99); se descartaron los puntos con margen O2
< 1 K (500/0.45/0.95 queda con +0.45 K, en el filo) aunque tuvieran más Wnet.

---

## 3. Tabla de rangos propuesta para el análisis de sensibilidad posterior

(NO se ejecuta en esta tarea — requiere autorización del director.)

Alrededor del candidato v2 (400/0.40/0.95, resto defaults):

| # | Variable | Límites | Centro (candidato) | Justificación |
|---|---|---|---|---|
| 1 | `x_b` | 0.35 – 0.45 | **0.40** | Palanca nueva; vigilar C1 (x5 < x_b < x3) y O2 (T_sat_L sube al bajar x_b) |
| 2 | `P_baja` | 400 – 500 kPa | **400** | Default del profesor; subirla quita η y da margen O2 (ver barrido) |
| 3 | `eps_cond` | 0.85 – 0.95 | **0.95** | Palanca directa de O2; por debajo de 0.90 casi todo CORREGIBLE |
| 4 | `eta_t` | 0.80 – 0.90 | **0.85** | Afecta O1 (q4 ≥ 0.90, margen modesto en v1) y η directamente |
| 5 | `eps_hrvg` | 0.80 – 0.99 | **0.85** | Afecta O5 (q2) y η; la frontera real es S5 (T2→T_fuente) en ≈0.99, no 0.90 — rango corregido por el pre-escaneo (nota abajo) |

> Nota (pre-escaneo eps_hrvg, 2026-09-20, `PRESCAN_EPS_HRVG.md`): el rango
> 0.80–0.90 original era una suposición sin evidencia. El pre-escaneo (6 pts
> TeqpAdapter, `prescan_eps_hrvg.csv`) dio todo KALINA en 0.70–0.95 sin
> acercarse a frontera (margen S5 ≥ +3.98 K a 0.90); la frontera S5
> (T2>T_fuente=470 K → INVIABLE) está extrapolada a eps_hrvg ≈ 0.99, el tope
> de `CAMPOS_CICLO`. Por eso el tope se amplía a 0.99 para bracketing; el piso
> 0.80 se conserva (sin fronteras debajo en un entorno razonable).

Fijas durante el barrido de sensibilidad: `P_alta=3000`, `T_fuente=470.0`,
`T_sumidero=300.032917`, `m_b=1.0`, `eta_p=0.75`, `eps_reg=0.75`,
`T_amb_diseno=303.55`. Variables de vigilancia en cada corrida: clasificación
(frontera O2 = knuckle), margen O1, margen O2.

---

## 4. Trazabilidad y límites

- Archivos nuevos con sufijo `_v2` (no se borró ni sobrescribió nada de v1):
  `busqueda_libre_v2.py`, `confirmacion_motor_real_v2.py`,
  `busqueda_libre_v2.csv`, `confirmacion_motor_real_v2.json`, este informe.
- Puntos Teqp: **80** (tope ~150); motor real: **1** (tope 1-2).
- Todo punto probado registrado (converja o no) en `busqueda_libre_v2.csv`
  (esquema `tabla_barrido` + columnas O2: T_sat_L, T9_amb, O2_margen).
- No se tocó ningún archivo de `src/`, ni `TASK_CONTEXT*.md`, ni el historial v1.
- Los 4 NO_CONVERGIO son fallas de dominio del motor teqp cerca de la campana
  fría (T≈296-307 K, x≈0.14-0.17), misma clase que la discrepancia 500/0.98 de
  v1 — no afectan la base elegida (está lejos de ese borde: T9_amb≈317 K).
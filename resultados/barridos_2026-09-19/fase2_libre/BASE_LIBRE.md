# BASE LIBRE — Fase 2 (búsqueda libre): base del ciclo que clasifica KALINA

**Task:** `2026-09-19-fase2-busqueda-libre` — Fase 2 de 3 (paralelas), rama
`test/vv-strategy`.

**Naturaleza del ejercicio:** búsqueda libre del modelo, **sin anclaje a
ningún caso real** (no confundir con la Fase 3, que sí debe ser realista).
Sin restricción de realismo industrial: el objetivo era demostrar que el
solver del repo puede producir al menos un punto que `evaluar_ciclo` clasifique
`KALINA`, como punto de partida para barridos de sensibilidad y para la Fase 3.

---

## 1. Base final propuesta (confirmada con el motor real)

| Variable | Valor |
|---|---|
| P_alta | 3000 kPa |
| **P_baja** | **450 kPa** (profesor: 400 kPa) |
| x_b | 0.50 |
| **T_fuente** | **470.0 K** (profesor: 623.15 K) |
| T_sumidero | 300.032917 K |
| m_b | 1.0 kg/s |
| eta_t | 0.85 |
| eta_p | 0.75 |
| eps_hrvg | 0.85 |
| eps_reg | 0.75 |
| **eps_cond** | **0.99** (profesor: 0.80) |

**Resultados (motor real `AmmoniaWaterAdapter`, iapws G4-01):**

- η = 0.12276 (aprox.; el valor con TeqpAdapter fue 0.122754)
- Wnet = 218.78 kW con m_b = 1.0 kg/s (Teqp: 218.77 kW)
- Clasificación: **KALINA** — "régimen Kalina genuino y admisible, sin fallas"
  (los 17 criterios N2/N3/S1-S8/O1-O3/O5/C1-C3 pasan).

> Nota: el motor real tardó ~9.4 min en este punto. La concordancia Teqp vs
> real es casi exacta (η y Wnet difieren en la 5ª-6ª cifra decimal), lo que da
> confianza en el motor rápido para futuros barridos alrededor de esta base.

---

## 2. Secuencia del hallazgo (todo punto probado registrado)

1. **Punto por defecto exacto de `CAMPOS_CICLO`** (T_fuente=470.0, P_alta=3000,
   P_baja=400, x_b=0.50, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80):
   **converge** y la única falla es **O2 (cavitación de bomba)**:
   - El criterio O2 re-resuelve el condensador con el **piso de diseño
     T_amb = 303.55 K** (30.4 °C, "no la media" — decisión del vault, ver
     `restricciones/operativos.py`), y a ese sumidero el estado 9 queda en
     T9 = 320.92 K, **por encima** del bubble point `T_sat_L(P_baja, x_b)`
     = 304.54 K → riesgo de succión bifásica (CORREGIBLE).
   - Todos los demás criterios ya pasaban: O1 (q4 = 0.9012 ≥ 0.90, margen
     escaso de 0.0012), S4 (T6−T10 ≈ 22 K), S5 (T2 = 464.07 ≤ T_fuente),
     S6, S8, N2/N3, C1 (x5=0.156 < 0.50 < x3=0.582), O3, O5 (q2 = 0.807).

2. **Por qué hubo que moverse respecto a la base del profesor** (las dos
   variables que cambiaron y la T_fuente):

   - **T_fuente 623.15 K → 470.0 K** (la más importante, ya documentada en
     `CONTEXT.md` 2026-09-17): con 623.15 K el estado 2 del HRVG queda fuera
     de la campana bifásica a P_alta=3000 kPa (campana 338.9-507.0 K a 3 MPa)
     y el separador ideal (flash directo) no puede repartir una corriente
     monofásica; además, la sonda de arranque del bracket `_bracketear`
     evalúa un T1 cercano a T_fuente que sobrecalienta la sonda del estado 2
     (fenómeno confirmado en la B0 con Teqp Y con el motor real). Con
     470.0 K (justo el default de `CAMPOS_CICLO`) T2 = 464.07 K cae dentro de
     la campana y la sonda no sobrecalienta. Esa variable sola convierte el
     primer obstáculo (NO_CONVERGIO/DEGENERADO por sonda o por fase única)
     en un punto convergente.
   - **P_baja 400 → 450 kPa**: sube el bubble point de la mezcla a P_baja
     (T_sat_L: 304.54 → 308.15 K), lo que relaja el criterio O2: el mismo
     eps_cond produce un margen de subenfriamiento mayor frente al sumidero
     de diseño de 303.55 K.
   - **eps_cond 0.80 → 0.99**: es la palanca directa que sugiere el propio
     criterio O2 ("aumentar eps_cond o el margen de subenfriamiento"): más
     efectividad del condensador ⇒ T9 más cerca de T_sumidero ⇒ la succión
     de la bomba queda subenfriada y O2 deja de fallar. **Con la base del
     profesor (P_baja=400) haría falta eps_cond ≈ 0.988** (margen de
     0.18 K, demasiado al filo); subiendo P_baja a 450 el punto 450/0.99
     queda cómodo y, además, con el mejor η de los candidatos.
   - Las demás variables se quedaron en sus defaults de `CONTEXT.md`: no hubo
     necesidad de tocarlas para los criterios (no se exploraron eta_t/eta_p/
     eps_hrvg/eps_reg/x_b/P_alta por no hacer falta; ver §4).

3. **Escaneo focalizado (TeqpAdapter, 10 puntos)**: 9 convergen, 3 clasifican
   `KALINA`. Resultado completo en
   `resultados/barridos_2026-09-19/fase2_libre/busqueda_libre.csv` (esquema
   idéntico a `tabla_barrido`):

   | P_baja [kPa] | eps_cond | clasificación (Teqp) | η | Wnet [kW] |
   |---|---|---|---|---|
   | 400 | 0.80 | CORREGIBLE (O2) | 0.13169 | 201.65 |
   | 400 | 0.95 | CORREGIBLE (O2) | 0.13301 | 231.01 |
   | 400 | 0.98 | NO_CONVERGIO (motor teqp) | — | — |
   | 400 | 0.99 | CORREGIBLE (O2, por 0.45 K) | 0.12966 | 231.09 |
   | 450 | 0.95 | CORREGIBLE (O2) | 0.12624 | 219.26 |
   | 450 | 0.98 | CORREGIBLE (O2, por 0.41 K) | 0.12368 | 219.06 |
   | **450** | **0.99** | **KALINA** | **0.12275** | **218.77** |
   | 500 | 0.95 | CORREGIBLE (O2) | 0.12002 | 208.46 |
   | **500** | **0.98** | **KALINA** | **0.11739** | **207.90** |
   | **500** | **0.99** | **KALINA** | **0.11651** | **207.63** |

   Patrón claro: **el único criterio que bloqueaba era O2**, y se desbloquea
   combinando P_baja (sube T_sat_L) con eps_cond (más subenfriamiento). El
   punto 400/0.98 no converge en Teqp (equilibrio no resoluble en T=295.34 K,
   P=400 kPa, x=0.139 — lado frío, sin relación con la campana de la sonda).

4. **Confirmación con el motor real (AmmoniaWaterAdapter, 3 puntos)** —
   `resultados/barridos_2026-09-19/fase2_libre/confirmacion_motor_real.json`:

   | P_baja / eps_cond | Teqp | Motor real | Nota |
   |---|---|---|---|
   | 450 / 0.99 | KALINA (η=0.12275) | **KALINA** (η=0.12276, Wnet=218.78) | concordancia casi exacta |
   | 500 / 0.98 | KALINA (η=0.11739) | **NO_CONVERGIO** | discrepancia: el motor iapws no cubre un estado del ciclo (equilibrio no resoluble T=374.1 K, P=0.5 MPa, w=0.593) — borde de campana |
   | 500 / 0.99 | KALINA (η=0.11651) | **KALINA** (η=0.11651, Wnet=207.64) | concordancia casi exacta |

   La discrepancia del punto 500/0.98 es la misma clase de divergencia Teqp vs
   real ya conocida en la B0 (cobertura del motor portado cerca de los bordes
   del dominio); no invalida la base elegida (450/0.99), que es la de mayor η
   y queda lejos de ese borde.

---

## 3. Interpretación y advertencia de uso

- La base elegida es un **punto de operación del modelo**, no una
  especificación industrial: eps_cond = 0.99 está en el borde superior del
  rango de la UI (`CAMPOS_CICLO` permite hasta 0.99) y un condensador real a
  esa efectividad es exigente (área/DT pequeña). Es exactamente lo que esta
  fase debía producir: **una base convergente y KALINA para estudiar
  sensibilidad y para que la Fase 3 la ancle/relaje hacia valores realistas.**
- El margen de O1 (título de turbina q4 = 0.9012) y del propio O2 en el punto
  confirmado es modesto; cualquier barrido de sensibilidad que se diseñe desde
  esta base debe vigilar ambos criterios primero.

---

## 4. Límites respetados y trazabilidad

- Todos los valores explorados dentro de `CAMPOS_CICLO` (`src/ui_helpers.py`).
- ~150-200 puntos con Teqp: se usaron **10** (la primera apuesta —default +
  palancas directas de O2— bastó; no hizo falta exploración masiva).
- Motor real: **3** puntos (1-3 permitidos), 2 confirmados KALINA.
- Todo punto probado registrado en `busqueda_libre.csv` (converja o no).
- No se tocó ningún archivo de `src/`, ni `fase1_profesor/`, ni `fase3_real/`.
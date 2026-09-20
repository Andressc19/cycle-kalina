# Reporte — Fase 2 (base libre) y Fase 3 (Húsavík): metodología y resultados

**Rama:** `test/fases-sensibilidad` · **Fecha:** 2026-09-20

---

## Metodología común a ambas fases

1. **Ancla confirmada con motor real** antes de barrer nada: cada fase parte de
   un punto de operación cuya clasificación (`KALINA`) y eficiencia (`eta`) ya
   se verificaron con el motor riguroso `AmmoniaWaterAdapter` (IAPWS G4-01), no
   solo con el motor rápido de exploración.
2. **Diseño experimental declarado por adelantado**: para cada fase, 5 barridos
   **uno-a-la-vez (OFAT)** — una variable se mueve en un rango, el resto queda
   fijo en el ancla — más **una malla 2D** del par de variables que gobiernan
   juntas el criterio de cavitación (O2), para capturar la interacción entre
   ambas en vez de solo verlas por separado.
3. **Motor mixto**: todo el barrido (OFAT + malla) corre con `TeqpAdapter`
   (rápido). Los puntos cuyo margen del criterio que decide la clasificación
   queda a menos de ~1-2 K (o 0.02 en título de vapor) del borde se
   re-resuelven con el motor real como verificación puntual — no se corre todo
   el barrido con el motor lento, pero tampoco se confía ciegamente en el
   rápido cerca de una frontera.
4. **Todo punto se registra**, converja o no — ningún resultado se descarta ni
   se oculta.

---

## Fase 2 — Base libre (T_fuente corregido a 470 K)

### Punto ancla

`P_alta=3000 kPa, P_baja=400 kPa, x_b=0.40, T_fuente=470.0 K, T_sumidero=300.032917 K,
m_b=1.0 kg/s, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
T_amb_diseno=303.55 K`

| | TeqpAdapter | Motor real |
|---|---|---|
| Clasificación | KALINA | **KALINA** |
| η | 0.124289 | 0.124296 |
| Wnet | 166.61 kW | 166.62 kW |
| Cierre N2 | residuo 1.94e-4 ≤ límite 1.34 ✓ | — |

**Frontera más cercana del ancla: O1** (calidad de vapor a la salida de la
turbina, q4≥0.90), margen +0.0013 — prácticamente al filo, más cerca que O2
(+3.91 K). Este es un hallazgo no anticipado: el diseño original apuntaba a O2
como criterio limitante, pero en el ancla real es O1 el que casi se dispara.

### Barridos OFAT (33 puntos)

| Variable | Rango | Resultado |
|---|---|---|
| x_b | 0.35–0.45 | 4 KALINA / 2 CORREGIBLE |
| P_baja | 400–500 kPa | 5 KALINA / 1 NO_CONVERGIO |
| **eps_cond** | 0.85–0.95 | **1 KALINA / 5 CORREGIBLE — variable dominante** |
| eta_t | 0.80–0.90 | 3 KALINA / 3 VALIDO_ADVERTENCIA |
| eps_hrvg | 0.80–0.99 (corregido tras pre-escaneo) | 7 KALINA / 1 NO_CONVERGIO / 1 VALIDO_ADVERTENCIA |

`eps_cond` es la variable más influyente: por debajo de ~0.93, prácticamente
todo el rango cae a CORREGIBLE por O2.

### Malla 2D — P_baja × eps_cond (36 puntos)

9 KALINA / 26 CORREGIBLE / 1 NO_CONVERGIO. La región KALINA se concentra en la
esquina de P_baja bajo + eps_cond alto, consistente con la física del criterio
O2 (más subenfriamiento a menor presión de condensación necesaria).

### Verificación con motor real (10 puntos cerca de fronteras)

**9/10 confirmados**; **1 discrepancia real**: en x_b=0.39 (borde del OFAT de
x_b), `TeqpAdapter` clasifica KALINA pero el motor real da `NO_CONVERGIO`
(reproducido 2 veces, no es un fallo aislado). Esto valida la estrategia de
motor mixto: si se hubiera confiado solo en Teqp, este punto se habría
reportado como válido sin serlo.

### Lección aprendida

El KALINA del ancla se sostiene con O2 cómodo, pero la frontera real es O1,
sin cruzarla. La sensibilidad dominante es `eps_cond`. El motor real es
numéricamente frágil justo en la frontera O1 (no-convergencias no
deterministas).

---

## Fase 3 — Húsavík (caso geotérmico real, Islandia)

### Punto ancla

`P_alta=3300 kPa, P_baja=690 kPa, x_b=0.82, T_fuente=394.15 K (121°C, salmuera
geotérmica real), T_sumidero=278.15 K (5°C, agua de refrigeración real),
m_b=1.0 kg/s, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
T_amb_diseno=283.15 K (10°C, piso de diseño corregido para el clima de Islandia)`

| | TeqpAdapter | Motor real |
|---|---|---|
| Clasificación | KALINA | **KALINA** |
| η | 0.12732 | 0.12730 |
| Wnet | 117.59 kW | 117.57 kW |
| Cierre N2 | residuo 5.2e-5 kW ≪ límite 0.92 kW ✓ | — |

**Corrección clave que desbloqueó este caso**: el criterio O2 usaba por
herencia un piso de T_ambiente de 30.4°C (clima tropical del enunciado del
profesor) — físicamente incorrecto para Islandia. Al corregirlo a 10°C
(margen conservador razonable sobre los 5°C reales), el `P_baja` mínimo
necesario para pasar O2 bajó de 1200 a 690 kPa, y η subió de 0.088 a 0.127
(+44%).

### Barridos OFAT (35 puntos)

| Variable | Rango | Resultado |
|---|---|---|
| P_baja | 600–800 kPa | CORREGIBLE 600–666.7 → KALINA 700–800 (frontera limpia) |
| eps_cond | 0.90–0.99 | CORREGIBLE 0.90–0.945 → KALINA 0.96–0.99 |
| eps_reg | 0.75–0.95 | KALINA en todo el rango (no limita) |
| x_b | 0.78–0.86 | KALINA 0.78–0.8333 → CORREGIBLE 0.8467–0.86 |
| eta_t | 0.85–0.95 | KALINA en todo el rango (no limita) |

Tres de las cinco variables (P_baja, eps_cond, x_b) cruzan una frontera de
clasificación dentro del rango explorado — el diseño experimental capturó bien
la zona de transición. `eps_reg` y `eta_t` resultaron no limitantes en este
caso (a diferencia de Fase 2, donde `eta_t` sí se acerca a VALIDO_ADVERTENCIA).

### Malla 2D — P_baja × eps_reg (36 puntos)

24 KALINA / 12 CORREGIBLE. Frontera diagonal clara: CORREGIBLE para
P_baja≤640 kPa (cualquier eps_reg), KALINA para P_baja≥680 kPa. El margen O2
crece con P_baja y, más suavemente, con eps_reg.

### Verificación con motor real (10 puntos cerca de fronteras)

**10/10 confirmados** — sin ninguna discrepancia entre Teqp y el motor real en
esta fase (a diferencia de Fase 2). La frontera O2 de Húsavík queda validada
con el máximo nivel de confianza disponible en este proyecto.

### Lección aprendida

`P_baja` y `eps_cond` gobiernan el margen O2; la frontera es predecible y
consistente entre motores. La corrección del piso climático de `T_amb_diseno`
fue la variable que realmente decidió si este caso real era viable o no —
más que cualquier ajuste de las variables "de ingeniería" del ciclo mismo.

---

## Comparación Fase 2 vs Fase 3

| | Fase 2 (libre) | Fase 3 (Húsavík) |
|---|---|---|
| η del ancla | 0.1243 | 0.1273 (+2.4%) |
| Frontera limitante del ancla | O1 (filo, +0.0013) | O2 (cómoda, +0.868 K con Teqp) |
| Discrepancias motor real vs Teqp | 1/10 puntos | 0/10 puntos |
| Variable más influyente | eps_cond | P_baja / eps_cond |
| Corrección que lo hizo posible | T_fuente 623→470 K | T_amb_diseno 30.4→10°C |

Ambas fases confirman que el ciclo del repo puede operar en régimen KALINA
genuino, pero cada una necesitó una corrección estructural distinta —
subrayando que "hacer que clasifique KALINA" no es un ajuste fino de
parámetros de ingeniería, sino resolver primero el supuesto de fondo
(temperatura de fuente físicamente alcanzable, piso de diseño climáticamente
correcto) antes de que el ajuste fino tenga sentido.

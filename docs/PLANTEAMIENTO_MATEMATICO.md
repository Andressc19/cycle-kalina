# Planteamiento matemático — Ciclo Kalina KCS-11

Este documento reúne, en un solo lugar, todas las ecuaciones que implementa el código de este
repositorio para simular el ciclo Kalina KCS-11 (mezcla amoníaco-agua). No es una introducción
genérica al ciclo Kalina: describe exactamente lo que está programado, con referencia a los
archivos fuente correspondientes, para que sirva de respaldo matemático del proyecto.

> Fuente de verdad interna: [`CONTEXT.md`](CONTEXT.md). Este documento es una exposición
> ordenada de ese contenido más el resto del código (`src/`), no un reemplazo.

---

## 1. Topología del ciclo y convención de signos

### 1.1 Mapa de 10 estados

```
10 →[Regenerador frío]→ 1 →[HRVG]→ 2 →[Separador]→ { 3 →[Turbina]→ 4 ; 5 →[Regenerador caliente]→ 6 →[Válvula]→ 7 }
4 + 7 →[Absorbedor]→ 8 →[Condensador]→ 9 →[Bomba]→ 10
```

8 componentes: **HRVG** (generador de vapor recuperador de calor / caldera), **Separador**
(flash ideal líquido-vapor), **Turbina**, **Regenerador** (un solo componente que modela el
lado caliente y el lado frío del recuperador interno), **Válvula** (estrangulamiento
isoentálpico), **Absorbedor** (mezclador adiabático), **Condensador** y **Bomba**.

Todas las variables de estado usan las unidades: $T$ [K], $P$ [kPa], $h$ [kJ/kg],
$s$ [kJ/kg·K], $x$ = fracción másica de NH₃, $\dot m$ [kg/s].

### 1.2 Balance global y signos

Con $Q_i$ = calor entregado por la fuente en el HRVG, $Q_{out}$ = calor rechazado en el
condensador, $W_t$ = trabajo entregado por la turbina, $W_p$ = trabajo consumido por la bomba
(todos en kW, todos definidos como cantidades positivas que entran o salen del fluido de
trabajo):

$$
Q_i + W_p = Q_{out} + W_t \qquad\Longrightarrow\qquad
W_{net} = W_t - W_p, \qquad \eta = \frac{W_{net}}{Q_i}
$$

---

## 2. Ecuaciones por componente

### 2.1 HRVG (caldera / generador de vapor recuperador de calor)

Cierre por **efectividad térmica** (no por *pinch point*):

$$
h_{2,\max} = h(P_{alta}, T_{fuente}, x_b), \qquad
h_2 = h_1 + \varepsilon_{HRVG}\,(h_{2,\max} - h_1)
$$

$$
\varepsilon_{HRVG} = \frac{h_2 - h_1}{h_{2,\max} - h_1}, \qquad
Q_i = \dot m_b\,(h_2 - h_1)
$$

### 2.2 Separador (flash ideal L-V)

El separador no tiene eficiencia propia: reparte la corriente 2 en vapor saturado (3, hacia
la turbina) y líquido saturado (5, hacia el regenerador), a la misma $T,P$ de equilibrio, con
las composiciones de equilibrio líquido-vapor $(x_l, y_v)$ de la mezcla NH₃-H₂O obtenidas del
backend de propiedades, y la composición global $x_b$ repartida por **regla de la palanca**:

$$
f_{vapor} = \frac{x_b - x_l}{y_v - x_l}, \qquad
\dot m_3 = f_{vapor}\,\dot m_2, \qquad \dot m_5 = (1 - f_{vapor})\,\dot m_2
$$

con $x_3 = y_v,\ q_3=1$ (vapor saturado) y $x_5 = x_l,\ q_5=0$ (líquido saturado).

### 2.3 Turbina

Eficiencia isentrópica estándar:

$$
h_{4s} = h(P_{baja}, s_3, x_3), \qquad
h_4 = h_3 - \eta_t\,(h_3 - h_{4s}), \qquad
W_t = \dot m_3\,(h_3 - h_4)
$$

### 2.4 Regenerador (recuperador interno)

El lado caliente (5→6) se cierra por efectividad respecto al mínimo posible, que es enfriar la
corriente 5 hasta la temperatura de entrada del lado frío ($T_{10}$):

$$
h_{6,\min} = h(P_{alta}, T_{10}, x_5), \qquad
h_6 = h_5 - \varepsilon_{reg}\,(h_5 - h_{6,\min}), \qquad
Q_{reg} = \dot m_5\,(h_5 - h_6)
$$

El lado frío (10→1) **no** se resuelve dentro del componente: se cierra a nivel de ciclo por
balance de energía (ver §3), porque su temperatura de salida $T_1$ es a su vez la variable que
alimenta el HRVG y por tanto forma parte del lazo de convergencia del ciclo completo.

### 2.5 Válvula

Isoentálpica, sin trabajo ni transferencia de calor:

$$
h_7 = h_6
$$

($T_7$ y $s_7$ se recalculan a partir de $h_7$ y $P_{baja}$.)

### 2.6 Absorbedor

Mezcla adiabática de las corrientes 4 (salida turbina) y 7 (salida válvula), sin caída de
presión ni modelo cinético:

$$
\dot m_8 = \dot m_4 + \dot m_7, \qquad
h_8 = \frac{\dot m_4 h_4 + \dot m_7 h_7}{\dot m_8}, \qquad
x_8 = \frac{\dot m_4 x_4 + \dot m_7 x_7}{\dot m_8}
$$

En régimen estacionario, $x_8$ debe reconstruir la composición global $x_b$ (es el criterio de
admisibilidad N3, §4).

### 2.7 Condensador

Cierre por efectividad, análogo al HRVG:

$$
h_{9,\min} = h(P_{baja}, T_{sumidero}, x_b), \qquad
h_9 = h_8 - \varepsilon_{cond}\,(h_8 - h_{9,\min}), \qquad
Q_{out} = \dot m_8\,(h_8 - h_9)
$$

### 2.8 Bomba

Eficiencia isentrópica estándar:

$$
h_{10s} = h(P_{alta}, s_9, x_9), \qquad
h_{10} = h_9 + \frac{h_{10s} - h_9}{\eta_p}, \qquad
W_p = \dot m_9\,(h_{10} - h_9)
$$

---

## 3. Cierre del ciclo: lazos de convergencia

El estado 1 (entrada al HRVG, salida fría del regenerador) se determina por balance de energía
a nivel de ciclo, no dentro del componente `Regenerador`:

$$
h_1^{nuevo} = h_{10} + \frac{\dot m_5}{\dot m_b}\,(h_5 - h_6), \qquad
T_1^{nuevo} = T_{from\_Ph}(P_{alta}, h_1^{nuevo}, x_b)
$$

Esto exige resolver dos lazos anidados, porque $T_1$ afecta a $T_2$ (HRVG), que afecta a la
composición de separación, que afecta a $T_6$ (regenerador), que afecta a $T_{10}$, que
retroalimenta a $T_1$:

- **Lazo interno** (`lazo_frio`): sustitución sucesiva sobre $T_{10}$ — se recorre
  regenerador → válvula → absorbedor → condensador → bomba → nuevo $T_{10}$, hasta que
  $|T_{10}^{nuevo} - T_{10}^{supuesto}| < \text{tol}_{T_{10}}$ (por defecto $10^{-3}$ K).
- **Lazo externo**: método de Brent (`scipy.optimize.brentq`) sobre
  $F(T_1) = T_1^{nuevo} - T_1$, acotado estrictamente dentro de
  $(T_{sumidero}, T_{fuente})$.

---

## 4. Modelo de propiedades de la mezcla NH₃-H₂O

### 4.1 Ecuación de estado

Ambos backends de propiedades usan la misma EOS física de referencia
**Tillner-Roth & Friend (1998) / IAPWS G4-01**:

- **`AmmoniaWaterAdapter`** (motor "real", `iapws.ammonia.H2ONH3`), con dos correcciones
  aplicadas sobre el paquete instalado (no sobre una copia): una errata en el exponente de
  $dT_n/dx$ (Ec. 4 de G4-01, $1.12455 \to 1.125455$) y una regla del producto faltante en
  $d(\Delta\Phi^r)/dx$ (Ec. 8) — sin estas correcciones no se reproducen las Tablas 7-8
  (bifásicas) de la guía IAPWS G4-01.
- **`TeqpAdapter`** (motor de alto rendimiento, `teqp.AmmoniaWaterTillnerRoth()` +
  contribución de gas ideal vía CoolProp), ~20× más rápido por estado, validado contra
  `AmmoniaWaterAdapter` con error <0.5% en $h,s$ (diferencia atribuible a un offset constante
  de estado de referencia entre bases de datos, que se cancela en cualquier $\Delta h,\Delta s$
  del ciclo) y <0.01% en presiones/temperaturas de saturación.

### 4.2 Equilibrio líquido-vapor y flash

Ambos adaptadores implementan directamente `equilibrio_liquido_vapor(P, T)` — un flash a T,P
fijos que entrega las composiciones de líquido y vapor en equilibrio — en vez de invertir el
punto de burbuja/rocío por bisección, porque esa inversión es lenta/inestable para
composiciones extremas. El flash se resuelve por igualdad de fugacidades (Newton/`fsolve`),
inicializado con un valor K de Raoult y con arranque en caliente desde el punto de flash
convergido más cercano.

La calidad de una corriente bifásica se obtiene por regla de la palanca sobre la composición:

$$
q = \frac{x_b - x_l}{x_v - x_l}
$$

### 4.3 Estado muerto y exergía física

Estado de referencia (para exergía física, no química — cada corriente se enfría/despresuriza
hasta $(T_0,P_0)$ manteniendo **su propia composición**, sin "desmezclar" hasta un ambiente):

$$
T_0 = 300.032917\ \text{K}, \qquad P_0 = 101.325\ \text{kPa}
$$

$$
ex_{fisica} = (h - h_0) - T_0\,(s - s_0), \qquad
h_0 = h(P_0, T_0, x_{corriente}), \qquad s_0 = s(P_0, T_0, x_{corriente})
$$

### 4.4 Generación de entropía y exergía destruida por componente

$$
E_d = T_0 \cdot S_{gen}
$$

| Componente | $S_{gen}$ |
|---|---|
| HRVG (fuente a $T_{fuente}$) | $\dot m_b(s_2-s_1) - Q_i/T_{fuente}$ |
| Separador | $\dot m_3 s_3 + \dot m_5 s_5 - \dot m_2 s_2$ |
| Turbina | $\dot m_3(s_4-s_3)$ |
| Regenerador | $\dot m_5(s_6-s_5) + \dot m_b(s_1-s_{10})$ |
| Válvula | $\dot m_6(s_7-s_6)$ |
| Absorbedor | $\dot m_8 s_8 - \dot m_4 s_4 - \dot m_7 s_7$ |
| Condensador (sumidero a $T_{sumidero}$) | $\dot m_8(s_9-s_8) + Q_{out}/T_{sumidero}$ |
| Bomba | $\dot m_9(s_{10}-s_9)$ |

Cierre global (verificación, no un dato de referencia externo):

$$
Ex_{Q_i} = Q_i\Big(1-\frac{T_0}{T_{fuente}}\Big), \qquad
Ex_{Q_{out}} = Q_{out}\Big(1-\frac{T_0}{T_{sumidero}}\Big)
$$

$$
Ex_{Q_i} - W_{net} - Ex_{Q_{out}} \approx E_{d,total} = \sum E_{d,componente}
$$

---

## 5. Criterios de admisibilidad (17 restricciones)

Filtran cada punto resuelto del ciclo según severidad decreciente:
`NO_CONVERGIO > INVIABLE > DEGENERADO > CORREGIBLE > VALIDO_ADVERTENCIA > KALINA`.

### 5.1 Numéricos (tolerancia relativa $10^{-3}$)

- **N2** — balance de energía global: $|Q_i - Q_{out} - W_{net}| \le 10^{-3}|Q_i|$
- **N3** — balance de especie:
  separador $|\dot m_2 x_b - \dot m_3 x_3 - \dot m_5 x_5| \le 10^{-3}\,\dot m_2 x_b$;
  absorbedor $|x_8 - x_b| \le 10^{-3}\,x_b$

### 5.2 Segunda ley

- **S1**: $s_4 \ge s_3$ (la entropía no puede disminuir en la turbina)
- **S2**: $s_{10} \ge s_9$ (idem en la bomba)
- **S3**: $s_7 \ge s_6$ (idem en la válvula)
- **S4**: $T_5 > T_1$ **y** $T_6 > T_{10}$ (sin cruce de temperaturas en el regenerador)
- **S5**: $T_2 \le T_{fuente}$ (la salida del HRVG no puede superar la temperatura de la fuente)
- **S6**: $T_9 \ge T_{sumidero}$ (la salida del condensador no puede bajar del sumidero)
- **S7**: $\varepsilon_{HRVG},\varepsilon_{reg},\varepsilon_{cond} \in [0,1]$
- **S8**: $\eta < \eta_{Carnot} = 1 - T_{sumidero}/T_{fuente}$ (Kelvin-Planck)

### 5.3 Operacionales

- **O1** (advertencia): $q_4 \ge 0.90$ — calidad a la salida de la turbina, umbral de erosión
  de álabes.
- **O2** (corregible): cavitación en la succión de la bomba, re-evaluada a
  $T_{amb}=\max(T_{sumidero}, 303.55\ \text{K})$ — falla si
  $T_9(T_{amb}) > T_{burbuja}(P_{baja}, x_b)$.
- **O3** (inviable): $W_{net} > 0$.
- **O5**: calidad $q_2$ a la salida del HRVG, con margen $DQ=10^{-3}$ —
  $q_2 < DQ$ → INVIABLE ("HRVG entrega líquido, nada que separar");
  $q_2 > 1-DQ$ → DEGENERADO ("sobrecalentado, el ciclo degenera a Rankine").

### 5.4 Composición

- **C1**: orden $x_5\,(\text{pobre}) < x_b < x_3\,(\text{rica})$ → inviable si se viola;
  advertencia si la brecha $x_3-x_5 \le 0.01$ (banda de incertidumbre del equilibrio del motor).
- **C2**: toda composición de estado $x \in (0,1)$.
- **C3**: $\dot m_3+\dot m_5=\dot m_b$ (tolerancia relativa $10^{-6}$) y cada fracción
  $\dot m_3/\dot m_b,\ \dot m_5/\dot m_b \in [0,1]$.

### 5.5 Explícitamente fuera de alcance

F1 (solo pinch), S9 (capacidad finita sin cruce), O6 (punto de rocío ácido), CD (cierre
declarado), O4 (redundante con O3), C1b (nunca definido formalmente), N4 (dominio de validez
del modelo de propiedades — sin resolver).

---

## 6. Barrido paramétrico

Cualquiera de las 11 variables de entrada al solver —
$T_{fuente}, T_{sumidero}, P_{alta}, P_{baja}, x_b, \dot m_b, \eta_t, \eta_p,
\varepsilon_{HRVG}, \varepsilon_{reg}, \varepsilon_{cond}$ — se declara como un valor **fijo**
o como un **barrido** $(inicio, fin, paso)$. Con varias variables en barrido se toma el
**producto cartesiano** completo (no un optimizador), porque el dominio tiene discontinuidades
(separador) y huecos de cavitación que un optimizador de gradiente podría saltarse.

Para cada combinación se resuelve el ciclo; si no converge, se marca `NO_CONVERGIO` y el
barrido continúa (nunca aborta). Si converge, se aplican los 17 criterios de §5 y se registran
$\eta$, $W_{net}$ y la clasificación. La exergía **no** se calcula dentro del barrido — es un
análisis posterior, por punto, con el módulo de exergía de §4.4.

---

## 7. Validación externa — Elsayed et al. (2013), KCS-11

Caso citado: $P_{alta}=1500$ kPa, $x_b=0.55$, $T_{fuente}=373$ K, $T_{sumidero}=283$ K,
$\eta_t=\eta_p=0.80$, $\eta_{paper}=11.38\%$.

**Diferencia metodológica de fondo**: el paper cierra HRVG/condensador/regenerador por
***pinch point*** ($\Delta T_{min}=4$ K) con propiedades de Ibrahim & Klein (1993, vía
EES+Refprop); este código cierra por **efectividad** con Tillner-Roth & Friend (1998)/IAPWS
G4-01 — la comparación mide incertidumbre entre modelos termodinámicos distintos, no solo una
diferencia de implementación.

Traducción pinch → efectividad:

$$
T_2 = T_{fuente}-4 = 369\ \text{K}, \qquad
T_9 = T_{sumidero}+4 = 287\ \text{K}, \qquad
T_6 = T_{10}+4
$$

$P_{baja}$ (no dado por el paper) se asume igual a la presión de burbuja en
$(T_{sumidero}+4,\ x_b)$, resuelta por Brent → $P_{baja}=273.55$ kPa.

Calibración de un solo paso (no un punto fijo completo, por costo computacional): se resuelve
una vez con $\varepsilon$ por defecto, se invierten en forma cerrada las fórmulas de
efectividad de §2 para dar en los objetivos $T_2,T_6,T_9$, y se re-resuelve con esos
$\varepsilon$ calibrados:

$$
\varepsilon_{HRVG}=0.8882,\quad \varepsilon_{reg}=0.9380,\quad \varepsilon_{cond}=0.9625
$$

**Resultado de la comparación**:

| Fuente | $\eta$ |
|---|---|
| Elsayed et al. (2013) | 11.38 % |
| Este código, `AmmoniaWaterAdapter` | 11.054 % |
| Este código, `TeqpAdapter` | 11.055 % |

Diferencia ≈ 0.33 puntos porcentuales absolutos (~2.9 % relativo), atribuida a tres causas
apiladas: (1) EOS distinta (Tillner-Roth/Friend vs. Ibrahim/Klein), (2) traducción de un solo
paso pinch→efectividad en vez de seguir el *glide* real, y (3) $P_{baja}$ asumida por no estar
dada en el paper. El test de regresión (`tests/test_validacion_elsayed2013.py`) fija estos
valores calibrados y exige $|\eta-0.1138|/0.1138 < 5\%$.

---

## 8. Verificación cruzada con DWSIM (2026-10-03)

**Qué es y qué no es.** DWSIM (simulador de procesos independiente, v9, vía pythonnet) se
usó para comprobar que este código **implementa correctamente** las ecuaciones de §1–§3
(topología, balances, cierre por efectividad). No es una validación experimental: DWSIM
también es una simulación, y su modelo de propiedades es otro.

**Modelo de propiedades en DWSIM.** De los 28 paquetes de DWSIM, solo Peng-Robinson (PR)
trae parámetro de interacción binaria NH₃-H₂O ($k_{ij}=-0.2533$). Contra IAPWS G4-01 se
desvía ~14 % en presiones de saturación, 0.012 en composiciones de fase y ~4 % en $\Delta h$
(`resultados/2026-10-03_dwsim_paquetes/REPORTE_PAQUETES_DWSIM.md`).

**Mismas ecuaciones de cierre.** Las efectividades de §2.1, §2.4 y §2.7 se impusieron en
DWSIM con las mismas definiciones (entalpías de referencia calculadas con el mismo PR,
traducidas a temperaturas de salida y resueltas por un lazo externo hasta residuo
$<10^{-3}$ K). En cada punto: energía de cada equipo = cambio de entalpía de sus corrientes
($|\text{dif}|\le 3\times10^{-4}$ kW), cierre global $\le 0.007$ kW y efectividades
resultantes = pedidas ($|\Delta\varepsilon|\le 2.4\times10^{-5}$).

**Comparación dato a dato** (6 ciclos KALINA de `regresion_22.csv`, $P_{alta}=3000$ kPa,
$T_{sumidero}=283$ K, $\varepsilon=0.85/0.80/0.85$, $\eta_t=\eta_p=0.80$). Entalpías llevadas
a referencia común $h_{rel}=h-h(P_{alta},T_0,x_{estado})$:

| Ciclo | $x_b$ | $T_{fuente}$ | $\eta$ código | $\eta$ DWSIM | $\Delta\eta$ |
|---|---|---|---|---|---|
| KALINA-01 | 0.60 | 394 K | 10.370 % | 10.741 % | +0.37 pp |
| KALINA-03 | 0.60 | 423 K | 9.615 % | 9.924 % | +0.31 pp |
| KALINA-06 | 0.65 | 394 K | 9.860 % | 10.066 % | +0.21 pp |
| KALINA-09 | 0.65 | 423 K | 8.422 % | 8.624 % | +0.20 pp |
| KALINA-12 | 0.70 | 394 K | 9.054 % | 9.151 % | +0.10 pp |
| KALINA-17 | 0.75 | 394 K | 8.135 % | 8.158 % | +0.02 pp |

- Coinciden: temperaturas de los 10 estados (±2.6 K), composiciones globales, balances
  internos (separador, absorbedor, válvula y regenerador cierran a 0 en los dos), entalpías
  de los estados líquidos fríos (≤ 4.4 kJ/kg) y el **orden de los 6 ciclos por $\eta$**.
- Difieren de forma sistemática (atribuido a PR, no a este código): DWSIM separa más vapor
  (caudal a turbina +1 a +6 %), da ~10 % más trabajo de bomba y hasta ~25 kJ/kg más
  entalpía en estados con vapor; la brecha de $\eta$ baja al subir $x_b$.
- Caso Elsayed (§7) con efectividades: DWSIM 11.64 % vs código 11.05 %. La diferencia de
  1.15 pp frente a DWSIM con pinch (12.20 %) se reparte en +0.59 pp por propiedades y
  +0.56 pp por la forma de cierre (`resultados/2026-10-03_validacion_dwsim/`).

**Límites.** DWSIM-PR no resuelve los ciclos con $P_{alta}$ de 4000–5000 kPa (su flash
P-T no converge en líquido comprimido), así que esa zona no está cubierta. La causa del
+10 % de la bomba (probablemente el volumen del líquido en PR) no se midió.

**Constancia.** `tests/test_verificacion_dwsim.py` comprueba sobre los resultados guardados
los criterios anteriores (31 casos). Reporte completo:
`resultados/2026-10-03_dato_a_dato/REPORTE_DATO_A_DATO.md`; scripts en `scripts/dwsim/`.

---

## 9. Segunda fuente independiente — Nemati et al. (2017)

Nemati, Nami, Ranjbar & Yari (2017), *Case Studies in Thermal Engineering* 9, 1–13
(Univ. de Tabriz; EES): KCS11 con la misma topología, Tabla 5 con los 9 estados del ciclo
($x_b=0.90$, 50/10.61 bar, $\eta_t=0.85$, $\eta_p=0.75$, gas a 429 K, agua a 298.15 K). Grupo
distinto al de Elsayed/Embaye y a 5000 kPa (zona sin cobertura de DWSIM). No da $\eta$ del
Kalina para ese caso: se comparan estados.

| Prueba | Nemati | Este código | Diferencia |
|---|---|---|---|
| $T_{burbuja}$(1061 kPa, 0.90) | 303.15 K | 303.54 K | +0.39 K |
| NH₃ en vapor, 50 bar/415 K (molar) | 0.9567 | 0.9511 | −0.006 (dentro de ±0.01 G4-01) |
| NH₃ en líquido, 50 bar/415 K (molar) | 0.5313 | 0.5174 | −0.014 (borde de ±0.01) |
| $T_1, T_4, T_8, T_{10}$ (no fijadas por la calibración) | — | — | −0.78, +2.49, +2.07, +0.20 K |
| Fracción de vapor (masa) del separador | 0.873 | 0.891 | +0.018 |

Efectividades calibradas en un paso desde sus $T_2, T_6, T_9$ (como en §7). Constancia:
`tests/test_benchmark_nemati2017.py`; reporte `resultados/2026-10-03_benchmark_nemati/`.

## 10. Banda de incertidumbre de $\eta$ por el modelo de propiedades

Propagando a $\eta$ la incertidumbre publicada de G4-01 (equilibrio L-V ±0.01 molar; entalpía
de exceso ±200 J/mol con forma supuesta $4x_m(1-x_m)$), una perturbación a la vez:

| Punto | $\eta$ | Banda | Comparación externa | ¿Dentro? |
|---|---|---|---|---|
| ELSAYED | 11.06 % | +0.46 / −0.34 pp | Elsayed 11.38 % (+0.33 pp) | Sí |
| KALINA-01 | 10.37 % | +0.59 / −0.46 pp | DWSIM-PR 10.74 % (+0.37 pp) | Sí |
| KALINA-11 | 12.15 % | +0.45 / −0.42 pp | — | — |

La banda (~±0.4–0.7 pp) la domina el equilibrio L-V del separador; la entalpía de exceso
aporta ≤ 0.003 pp. La diferencia típica del benchmark de 23 puntos (0.28 pp) también cae
dentro; su máximo (1.16 pp) no. Reporte: `resultados/2026-10-03_incertidumbre_eta/`.

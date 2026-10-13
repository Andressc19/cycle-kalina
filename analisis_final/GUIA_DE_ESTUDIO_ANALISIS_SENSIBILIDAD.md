# Guía de estudio — Análisis de sensibilidad del ciclo Kalina KCS-11

*Para entender y exponer la campaña final de barridos (6 al 9 de octubre de 2026) y todo lo que contiene el
libro `datos/Excel_kalina_final_final_final.xlsx`. Escrita el 2026-10-12. Todas las cifras salen de
`analisis_final/01_datos/todos_los_puntos.csv` y del informe `INFORME_BARRIDOS_CAMPANA_FINAL.md`.*

---

## 0. Cómo usar esta guía

| Si tienes… | Lee… |
|---|---|
| 5 minutos | §1 (la historia en 60 segundos) y §7 (conclusiones) |
| 30 minutos | §1 a §4 (vocabulario, cómo se decide, métodos) y §7 |
| Una exposición | Todo en orden; en cada estudio (§6) hay un recuadro **«Para exponer»** y al final (§10) las preguntas probables con su respuesta |
| Dudas sobre el Excel | §8 (mapa del libro) y la hoja `LEEME` del propio Excel |

Notación: **η** es la eficiencia térmica del ciclo; **ε** es la efectividad de un intercambiador;
**kPa** y **K** son las unidades de presión y temperatura; **pp** son puntos porcentuales (8 % → 11 % son 3 pp).

---

## 1. La historia en 60 segundos

1. **El problema.** El enunciado del profesor fija un ciclo Kalina con fuente a 623.15 K (350 °C) y sumidero
   a 300.03 K (27 °C), y unos datos de diseño (presiones, composición, eficiencias).
2. **Pregunta 1 — ¿funciona?** No. Con los datos exactos del profesor el modelo no encuentra un ciclo
   (0 de 41 corridas convergen).
3. **Pregunta 2 — ¿qué hay que cambiar?** Cambiar una sola variable no basta. Cambiando dos (bajar la fuente a
   ~403 K y subir P_baja a 563.64 kPa) aparece un ciclo KALINA. Ese punto se llama **ancla A\***.
4. **Pregunta 3 — ¿qué variables importan?** Se hizo un análisis de sensibilidad local (alrededor de A\*) y uno
   global (500 puntos al azar). Lo que decide si el ciclo es KALINA es la **P_baja y la efectividad del
   condensador**; lo que mueve la **eficiencia** es otro grupo (P_alta, η_t, ε_reg).
5. **Pregunta 4 — ¿qué datos del profesor se pueden conservar?** Con la fuente a ~390–410 K se conservan
   **8 de los 10** datos de diseño. Lo único que no se puede conservar es la fuente a 623 K.
6. **Pregunta 5 — ¿cuánta eficiencia?** Hasta 15.6 % con equipos muy buenos (0.95); con equipos medios, 8–11 %.
7. **Pregunta 6 — ¿es confiable?** Verificado, no validado: un segundo motor de propiedades da los mismos
   resultados y se contrastó con la planta real de Húsavík (sin validación experimental). Pero los diseños KALINA están **pegados a la
   frontera de cavitación**, sin margen.

> **Para exponer (una frase):** *«Con los datos del profesor el ciclo no funciona; moviendo la fuente a unos
> 400 K y subiendo un poco P_baja sí, y casi todo lo demás del enunciado se puede conservar.»*

---

## 2. Vocabulario imprescindible

### Los datos (variables de entrada)

| Símbolo | Qué es | Valor del profesor |
|---|---|---|
| T_fuente | Temperatura de la fuente de calor (gases) | 623.15 K |
| T_sumidero | Temperatura del sumidero (agua/aire de enfriamiento) | 300.03 K |
| P_alta | Presión de alta del ciclo | 3000 kPa |
| P_baja | Presión de baja del ciclo | 400 kPa |
| x_b | Fracción de amoníaco de la mezcla base | 0.50 |
| η_t, η_p | Eficiencia isentrópica de la turbina y de la bomba | 0.85 y 0.75 |
| ε_HRVG | Efectividad del generador de vapor | 0.85 |
| ε_reg | Efectividad del regenerador | 0.75 |
| ε_cond | Efectividad del condensador | 0.80 |

Derivadas que aparecen mucho: **ΔP = P_alta − P_baja** y **r_P = P_alta / P_baja** (razón de presiones).

### Puntos de referencia

| Término | Significado |
|---|---|
| **PP** (punto del profesor) | Los datos del enunciado tal cual. No converge |
| **A\*** (punto ancla) | El PP con solo dos cambios: T_fuente = 403 K y P_baja = 563.64 kPa. Es KALINA con η = 8.48 % |
| **Vecinos de A\*** | Dos puntos pegados a A\* por variable, a ±1 % del rango; sirven para medir la pendiente local |

### Cómo se clasifica un punto

| Clase | Significado | Color en el libro |
|---|---|---|
| **KALINA** | Cumple todos los criterios | verde |
| **CORREGIBLE** | Falla un criterio operativo (casi siempre O2) | naranja |
| **INVIABLE** | Falla un criterio estructural (O3, O5…) | amarillo |
| **NO_CONVERGIO** | El modelo no encontró un ciclo | rojo |
| **Falso convergido (N2)** | El solver dijo que convergió pero el clasificador lo descarta; no cuenta | gris |

| Criterio | Qué exige |
|---|---|
| **O1** | El vapor sale de la turbina con título suficiente (q4 ≥ 0.90) |
| **O2** | **Cavitación:** el líquido debe llegar subenfriado a la bomba (margen = T_burbuja − T de entrada a la bomba) |
| **O3** | El ciclo debe producir trabajo neto (W_net > 0) |
| **O5** | El separador debe recibir una mezcla de dos fases |

### Palabras de los análisis

| Término | Significado |
|---|---|
| **Genuino** | Punto que el modelo resolvió de verdad (KALINA, CORREGIBLE o INVIABLE) |
| **KALINA confiable** | KALINA dentro del rango validado del modelo de propiedades y con todas las η y ε entre 0.40 y 0.95 |
| **Fuera de rango** | Estados fuera del rango validado de propiedades (p. ej. líquido a más de 420 K); su η se toma con cautela |
| **Banda de η** | Incertidumbre del modelo: ±0.4–0.7 pp. Diferencias menores no son concluyentes |
| **Piso de O2** | Temperatura con la que se evalúa la cavitación: 300.03 K fija en los primeros estudios; desde 2.4 es igual a la T_sumidero de cada punto |
| **Parte** (2.4a) | Subconjunto de un estudio con sus propios datos fijos. **Solo se comparan puntos de la misma parte** |
| **teqp / motor real** | Dos motores de propiedades termodinámicas; teqp es el rápido y se verifica contra el motor real |

---

## 3. Cómo se decide si un punto es KALINA

Para cada combinación de datos, el programa hace tres pasos:

1. **Resuelve el ciclo** (balances de energía y masa con el motor de propiedades).
2. **Calcula los márgenes** de cada criterio: cuánto le sobra o le falta a O1, O2, O3 y O5.
3. **Clasifica**: si cumple todo es KALINA; si falla solo un criterio operativo, CORREGIBLE; si falla uno
   estructural, INVIABLE; si no encontró solución, NO_CONVERGIO.

**Índice de cercanía D:** convierte «qué tan cerca está un punto de ser KALINA» en un número.
`D = v_O1/0.01 + v_O2/1 K + v_O5/0.01 + v_O3/1 kW`, donde cada `v` es cuánto viola el criterio
(0 si lo cumple). D = 0 significa que cumple todos los criterios operativos.

> **Analogía:** es como un examen con cuatro preguntas obligatorias. KALINA es tener las cuatro bien;
> D es «cuántos puntos te faltan para aprobar».

El criterio que casi siempre bloquea es **O2**: el líquido llega a la bomba demasiado cerca de hervir.

---

## 4. Los métodos usados (y por qué)

### 4.1 Por qué estos métodos y no otros

Tres rasgos del problema condicionan todo:

- **Cada punto cuesta ~30 segundos o más**, así que no se pueden hacer miles.
- **Muchos puntos no convergen**; ahí no existe η ni los márgenes.
- **La salida principal es una clase** (KALINA / CORREGIBLE / …), no un número, y tiene fronteras bruscas.

Por eso se eligieron métodos que funcionan con pocos puntos, toleran fallos y sirven con salidas de tipo
«cumple / no cumple».

### 4.2 Resumen

| Método | Para qué sirve | Dónde se usó |
|---|---|---|
| **Malla 1D / 2D** | Barrer una o dos variables en una cuadrícula | Estudios 2.1–2.4, 4.2, 6.2 |
| **Bisección de fronteras** | Afinar el valor exacto donde cambia la clase | Estudios 2.1–2.4 |
| **OAT** (una variable a la vez) | Ver el efecto de cada variable por separado, cerca de un punto | 3.1, 6.2 |
| **Elasticidad** | Cuánto cambia η (en %) por cada 1 % que cambia una variable | 3.1 |
| **LHS** (muestreo hipercubo latino) | Repartir puntos al azar pero de forma pareja en todo el espacio | 3.2, 3.3, 4.1, 4.3 |
| **RSA + KS** | Qué variables separan los KALINA del resto | 3.2 |
| **PRCC** | Qué variables mueven η y en qué sentido | 3.2 |
| **PAWN** | Importancia sin suponer linealidad (control del PRCC) | 3.2 |
| **CART** (árbol de decisión) | Reglas legibles de la región KALINA | 3.2 |
| **Bootstrap** | Intervalo de confianza al 95 % de los estadísticos | 3.2 |
| **Prueba de convergencia** | Verificar que el ranking no cambia al pasar de 300 a 500 puntos | 3.2 |
| **Búsqueda por patrones** | Encontrar la η máxima dentro de KALINA | 5.1 |
| **Escalera de conservación** | Elegir, ronda a ronda, qué datos del profesor se conservan | 4.3 |
| **Verificación cruzada** | Repetir puntos clave con otro motor de propiedades | 6.1 |

### 4.3 Cada método, explicado

**Malla y bisección.** Se barre una variable (o dos) en una cuadrícula regular y, donde la clase cambia, se
parte el intervalo en dos varias veces para ubicar la frontera con precisión.
*Analogía: buscar un número entre 1 y 100 diciendo «más alto / más bajo».*

**OAT y elasticidad.** Se mueve una variable con las otras nueve fijas en A\*. Para cada una se calculan:
el **Δη** (diferencia entre su mayor y menor η) y la **elasticidad E = (Δη/η) / (Δv/v)**: con E = 10.9,
un 1 % más de T_fuente da un 10.9 % más de η *pegado a A\**.
*Límite:* solo vale alrededor de A\* y no ve interacciones.

**LHS.** Cada variable se divide en tantos tramos como puntos hay, y cada tramo se usa exactamente una vez.
Así 500 puntos cubren el espacio de forma pareja, mejor que 500 al azar sin control.

**RSA y KS (el método principal).** Se separan los puntos en dos grupos: KALINA y no KALINA. Para cada
variable se comparan sus dos distribuciones con la prueba de Kolmogorov–Smirnov. **KS** vale de 0 a 1:
0 = el grupo KALINA y el resto tienen la misma distribución (la variable no decide); cerca de 1 = totalmente
distintas (la variable decide).
*Cómo se lee en la figura 3.2-1:* dos curvas acumuladas por variable; cuanto más separadas, más decide.
Los puntos que no convergieron no estorban, porque caen en «no KALINA».

**PRCC.** Correlación parcial entre cada entrada y η, **sacando el efecto de las demás**, y usando rangos
(así acepta relaciones curvas pero siempre crecientes o siempre decrecientes). Da un número de −1 a +1:
**el signo dice si subir la variable sube o baja η**. Se calcula solo con los puntos que dieron η.

**PAWN.** Compara la distribución de η con y sin fijar una variable. No supone linealidad. Se usó para
confirmar que el grupo líder es el mismo que el del PRCC.

**CART.** Un árbol de decisión que intenta clasificar KALINA con reglas del tipo «si ε_cond > 0.89 y…».
Resultó apenas mejor que decir «nunca es KALINA» (78.8 % contra 75.8 %): la frontera no es una regla simple.

**Bootstrap.** Se repite el cálculo 1000 veces con muestras remuestreadas para obtener un intervalo de
confianza al 95 %. Si dos intervalos se solapan, **no se puede decir cuál variable pesa más**.

**Búsqueda por patrones.** Desde un punto de arranque, mueve las variables paso a paso hacia donde sube η,
sin salir de KALINA.

### 4.4 Métodos descartados (y la razón)

| Método | Razón |
|---|---|
| **Morris** | Pierde la mitad de los efectos cuando una parte de los puntos no converge; con solo 10 variables aporta poco |
| **Sobol** | Pediría ~6 100 puntos (unas 53 h) y exige una salida en todos los puntos |
| **eFAST** | Mismos problemas que Sobol |
| **Metamodelo + Sobol** | Los sustitutos suaves se ajustan mal a fronteras bruscas; queda como trabajo futuro |

---

## 5. Las fases, en orden

La campaña tiene **6 preguntas**, y cada una se responde con uno o más **estudios**. Dentro de un estudio, cuando
hay datos fijos distintos, se separa en **partes** (a, b, c…).

| Pregunta | Estudio | Qué se hizo | Método | Corridas |
|---|---|---|---|---|
| **1** ¿Funciona con los datos del profesor? | **1.1** | Repetir el caso del profesor | Repetición punto a punto | 42 |
| **2** ¿Qué hay que cambiar? | **2.1** | Un solo cambio | OAT 10 variables + bisección | 132 |
| | **2.2** | Dos cambios (P_baja + otra) | Malla 2D + bisección | 180 |
| | **2.3** | Dos cambios con η y ε en 0.40–0.95 | Mallas + bisección | 225 |
| | **2.4** | Sumidero más frío | Malla 2D + bisección | 320 |
| **3** ¿Qué importa y cuánto? | **3.1** | Sensibilidad local alrededor de A\* | OAT 15 valores + elasticidad ±1 % | 171 |
| | **3.2** | Sensibilidad global | LHS 500 puntos; RSA/KS, PRCC, PAWN, CART | 500 |
| | **3.3** | P_baja alta (1500–2500 kPa) | LHS de 150 | 150 (135 evaluados) |
| **4** ¿Qué se puede conservar? | **4.1** | Cinco escenarios de conservación | LHS de 120 por escenario | 600 |
| | **4.2** | Presiones del profesor | Malla dirigida 11×5×3 | 165 |
| | **4.3** | Escalera de conservación | Selección hacia adelante | 987 |
| **5** ¿Cuánta eficiencia? | **5.1** | Búsqueda de la η máxima | Búsqueda por patrones, 5 arranques | 560 |
| **6** ¿Es confiable? | **6.1** | Verificación con el motor real | teqp contra motor real | 167 |
| | **6.2** | Planta real de Húsavík | Re-evaluación + OFAT + malla | 382 |
| Anexo | **A.1** | Equipos fuera del rango realista | η y ε de 0.20 a 0.99 | (no entra en conclusiones) |

*Total: 4 560 puntos evaluados sin el anexo; los resultados se generaron entre el 6 y el 9 de octubre de 2026.*

**Orden lógico de la historia:** 1 (no funciona) → 2 (qué cambiar mínimo) → 3 (qué variables mandan) → 4 (qué
se conserva) → 5 (hasta dónde llega η) → 6 (¿nos fiamos?).

---

## 6. Estudio por estudio

Cada tabla se llama **Tabla N.M-k** (estudio N.M, tabla k) y cada figura **Figura N.M-k**. En el Excel,
cada tabla es una hoja y cada figura está en la hoja de gráficos de su pregunta **y** copiada junto a la
tabla de la que salen sus datos.

### Tablas que tienen todos los estudios

| Tabla | Qué muestra |
|---|---|
| **N.M-1 Condiciones** | Qué quedó fijo y qué se barrió, variable por variable, parte por parte |
| **N.M-2 Corridas por parte y por clase** | Cuántos puntos hay de cada clase (KALINA, corregible, …) en cada parte |
| **N.M-R Resultados por barrido** | Todos los puntos del estudio, bloque por bloque: valor de la variable, clase, η, W_net, ΔP, r_P |

*Cómo leer una `N.M-R`:* cada bloque es un barrido; si en una parte hay una variable a la vez, hay un bloque
por variable. La columna «Tipo de punto» distingue malla, vecino de A\*, ancla y bisección.

---

### Pregunta 1 — ¿Funciona el ciclo con los datos del profesor?

#### Estudio 1.1 — Repetir el caso del profesor
- **Qué se hizo:** repetir los 41 puntos de la Fase 1 (caso base, P_alta 2000–4000, x_b 0.40–0.70, temperatura
  ambiente hora a hora).
- **Resultado:** 42 corridas, **0 genuinas**. La clase coincide con la de la Fase 1 en 41 de 41.
- **Tablas:** 1.1-1, 1.1-2 y **1.1-3 «Comparación antes y después de la F1»** (cada punto con su clase y η de
  antes y de ahora, para comprobar que el código reproduce al profesor).
- **Figuras:** ninguna (no hay nada que graficar: no converge).
- **Conclusión:** el código actual reproduce al profesor; mover solo P_alta, x_b o el clima no cambia nada.
  El bloqueo está en el lado caliente.

> **Para exponer:** *«Antes de cambiar nada comprobé que mi código da lo mismo que el del profesor: no converge.»*

---

### Pregunta 2 — ¿Qué es lo mínimo que hay que cambiar?

#### Estudio 2.1 — Un solo cambio
- **Qué se hizo:** cada una de las 10 variables, de a una, con 10 valores + bisección (η y ε entre 0.75 y 0.85).
- **Resultado:** 132 corridas, 15 genuinas, **0 KALINA**, 21 falsos convergidos.
- **Tabla 2.1-3 «Distancia al punto del profesor»:** por variable, cuántos puntos convergen, el valor
  convergido más cercano al PP, y el índice D mínimo.
- **Figura 2.1-1 (10 paneles):** un panel por variable. El eje horizontal es el valor de la variable; el
  vertical es la **fila de la clase** (KALINA arriba, no convergió abajo). Marcador hueco = fuera de rango.
- **Conclusión:** con un cambio no hay KALINA. El que más acerca es bajar la fuente a ~400 K (a 402.9 K solo
  falla O2 por 2.0 K).

#### Estudio 2.2 — Dos cambios
- **Qué se hizo:** P_baja combinada con una variable del lado caliente.
  - **Parte 2.2a (ruta A):** conserva la fuente de 623 K y mueve ε_HRVG × P_baja.
  - **Parte 2.2b (ruta B):** baja la fuente: T_fuente × P_baja.
- **Resultado:** ruta A, 36 genuinas y **0 KALINA** (bloquea O2). Ruta B: **59 KALINA** (48 confiables) con
  T_fuente entre 390 y 434 K.
- **Tabla 2.2-3 «Resumen de la malla de dos cambios»:** por ruta y valor, cuántos genuinos y KALINA, la
  P_baja mínima KALINA y la η en ese punto.
- **Figuras 2.2-1 y 2.2-2:** dispersión de P_baja (horizontal) contra la variable movida (vertical), con
  forma y color de la clase.
- **Conclusión:** conservar 623 K no funciona; bajar la fuente sí. De ahí sale **A\*** (T_fuente 403 K,
  P_baja 563.64 kPa), elegido entre el más eficiente (420 K) y el más parecido al profesor (390 K).

#### Estudio 2.3 — Dos cambios con η y ε en 0.40–0.95
- **Partes:** 2.3a (una variable), 2.3b (ε_HRVG × ε_cond), 2.3c (ε_HRVG × P_baja), 2.3d (T_fuente × ε_cond).
- **Resultado:** 2.3a y 2.3b, 0 KALINA; 2.3c, 19 filas pero ninguna confiable; **2.3d, 1 KALINA confiable**
  (presiones del profesor + T_fuente 403 K + ε_cond 0.95, η = 9.50 %).
- **Tabla 2.3-3 «Malla con η y ε»:** por parte, genuinos, KALINA, el punto más cercano al PP y su η.
- **Figuras 2.3-1 a 2.3-4:** una por parte (tiras por variable en 2.3a; dispersión de las dos variables
  movidas en 2.3b–2.3d).
- **Conclusión:** conservando 623 K solo hay KALINA bajando mucho ε_HRVG y subiendo P_baja, y ninguno es
  confiable. Con las presiones del profesor y la fuente a 403 K sí hay uno.

#### Estudio 2.4 — Sumidero más frío
- **Partes (cada una con su base):** 2.4a (fuente 403 K), 2.4b (fuente 420 K), 2.4c (ε_HRVG = 0.40 con la
  fuente del profesor), 2.4d (datos exactos del profesor).
- **Resultado:** al bajar T_sumidero de 300 a 278 K, la P_baja mínima baja a la mitad y η sube 2–3 pp;
  2.4d nunca es KALINA.
- **Tabla 2.4-3 «Malla T_sumidero × P_baja por base»:** por base y temperatura, P_baja mínima KALINA, η
  mínima, η máxima, criterio que bloquea.
- **Figura 2.4-1 (2 paneles):** P_baja mínima KALINA contra T_sumidero, y η máxima contra T_sumidero, una
  línea por base.
- **Conclusión:** un clima más frío ayuda porque permite bajar P_baja; el profesor exacto nunca funciona:
  **el problema es la fuente, no el clima**.

---

### Pregunta 3 — ¿Qué variables importan y cuánto?

#### Estudio 3.1 — Sensibilidad local alrededor de A\*
- **Qué se hizo:** 10 variables × 15 valores (OAT) + A\* ± 1 % del rango para la elasticidad.
- **Resultado:** 171 corridas, 148 genuinas, 86 KALINA.
- **Tabla 3.1-3 «Influencia y margen por variable»:** por variable, rango explorado, valor en A\*,
  **elasticidad E**, **Δη**, η máxima KALINA, la zona KALINA y la **distancia a la frontera de O2**.
- **Figuras:**
  - **3.1-1 (tornado):** barras del Δη por variable, ordenadas. La más larga mueve más η.
  - **3.1-2 (elasticidades):** barras de E; verde sube η, rojo la baja.
  - **3.1-3 (10 paneles):** η contra cada variable, una a la vez. Línea punteada vertical = valor en A\*;
    banda verde = η de A\* ± 0.7 pp; ✕ en η = −0.6 = punto sin η.
  - **3.1-4 (márgenes):** distancia de A\* a la frontera de O2, como fracción del rango. Rojo = menos del 6 %.
- **Conclusión:** mayor elasticidad T_fuente (E = 10.9) y x_b (3.4); mayor Δη x_b (10.8 pp) y P_baja
  (6.8 pp). **A\* está al filo de O2: en 8 de 9 variables la frontera está a menos del 6 % del rango.**

> **Para exponer:** *«Alrededor del ancla, la fuente y la fracción de amoníaco son las más sensibles, pero
> sobre todo el ancla está pegada a la frontera de cavitación: casi cualquier cambio la rompe.»*

#### Estudio 3.2 — Sensibilidad global (500 puntos)
- **Qué se hizo:** LHS de 500 puntos (300 + 200) dentro de una caja realista: T_fuente 380–500 K,
  T_sumidero 278–303.5 K, P_alta 2000–5000, P_baja 300–1500 kPa, x_b 0.50–0.85, η y ε realistas.
- **Resultado:** 452 genuinas, **121 KALINA (83 confiables)**; 48 puntos sin resultado.
- **Tablas:**
  - **3.2-3 «Separación KALINA / no KALINA (RSA y KS)»:** por variable, el KS, su valor p, su intervalo y el
    rango favorable. *Se lee:* KS alto = la variable decide.
  - **3.2-4 «Influencia de cada variable sobre η (PRCC)»:** PRCC, estadístico t, valor p e intervalo; hay
    filas para η y para los márgenes de cada criterio.
  - **3.2-5 «Rangos de presión de los KALINA»:** mínimo, p5, mediana, p95 y máximo de P_alta, P_baja, ΔP, r_P.
  - **3.2-6, 3.2-7 y 3.2-8 «Ventana KALINA por franjas»:** de P_alta, T_fuente y T_sumidero; en cada franja,
    cuántos son KALINA y entre qué P_baja, ΔP y r_P.
- **Figuras:**
  - **3.2-1 (10 curvas acumuladas):** KALINA (verde), resto genuino (gris punteado), sin resultado (rojo
    punteado). Cuanto más separadas, más decide la variable.
  - **3.2-2 (plano de presiones):** P_alta contra P_baja, color por clase; las dos líneas son r_P en el
    percentil 5 y 95 de los KALINA.
  - **3.2-3 (PRCC):** barras con intervalo; positivo sube η, negativo la baja.
  - **3.2-4 (histogramas):** ΔP y r_P de KALINA, resto y sin resultado.
- **Conclusión:** **KALINA lo deciden P_baja y ε_cond (KS 0.43 cada una)**, luego r_P (0.35). **η la mueven
  P_baja (−0.68), P_alta (+0.58), η_t (+0.38).** El 90 % de los KALINA tiene r_P entre 1.7 y 5.3.

> **Para exponer:** *«Hay dos preguntas distintas: qué variables hacen que el ciclo sea KALINA (P_baja y
> ε_cond) y qué variables suben la eficiencia (P_alta, η_t, ε_reg). No son las mismas.»*

#### Estudio 3.3 — Techo de P_baja (1500–2500 kPa)
- **Resultado:** 135 evaluados (15 omitidos), 120 genuinos, 75 KALINA (45 confiables), entre 33 y 75 % de
  KALINA según la franja.
- **Tablas 3.3-3 y 3.3-4:** P_baja máxima KALINA por franja (de P_baja y de P_alta).
- **Figura 3.3-1:** barras del % de KALINA por franja de P_baja.
- **Conclusión:** no hay techo de clasificación hasta 2500 kPa; lo que limita una P_baja alta es que r_P tiende
  a 1 y la eficiencia cae (mediana 4.29 %).

---

### Pregunta 4 — ¿Qué datos del profesor se pueden conservar?

#### Estudio 4.1 — Escenarios de conservación (120 puntos por escenario)
| Parte | Conserva | KALINA | Confiables | Ejes de la figura |
|---|---|---|---|---|
| 4.1a | T_fuente y T_sumidero | 4 | 2 | P_alta × P_baja |
| 4.1b | P_alta y P_baja | 0 | 0 | T_fuente × ε_cond |
| 4.1c | presiones y clima | 0 | 0 | T_fuente × ε_cond |
| 4.1d | P_alta y temperaturas | 6 | 0 | x_b × P_baja |
| 4.1e | T_fuente y x_b | 10 | 0 | P_alta × P_baja |

- **Tablas:** **4.1-3 «Resumen por escenario»** (evaluados, KALINA, genuinos, factible, criterio que bloquea,
  D mínimo) y **4.1-4 «Rangos por escenario»** (percentiles de cada variable en KALINA contra no KALINA).
- **Figuras 4.1-1 a 4.1-5:** una dispersión por escenario, color por clase.
- **Conclusión:** conservar 623 K casi nunca da KALINA confiable (2 de 20). Las presiones del profesor sí son
  posibles, pero en una franja tan angosta que el muestreo al azar no la encontró: eso lleva al 4.2.

#### Estudio 4.2 — La franja KALINA con las presiones del profesor
- **Qué se hizo:** malla dirigida T_fuente 385–410 K (11 valores) × ε_cond 0.85–0.95 (5) × tres climas (3).
- **Resultado:** 165 corridas, **104 KALINA, todos confiables**.
- **Tabla 4.2-3 «Frontera KALINA»:** por clima y ε_cond, cuántas celdas son KALINA y entre qué T_fuente.
- **Figura 4.2-1 (3 paneles):** un panel por clima; T_fuente contra ε_cond.
- **Conclusión:** **las dos presiones del profesor son compatibles con KALINA si la fuente está a 390–410 K y
  ε_cond ≥ 0.875** (con clima más frío basta 0.85). Mejor η: 10.81 %.

#### Estudio 4.3 — Escalera de conservación
- **Qué se hizo:** ronda por ronda se elige qué dato conservar más (selección hacia adelante), midiendo los
  KALINA confiables que quedan.
- **Resultado:** el conjunto final **conserva 8 de 10 datos** (P_alta, P_baja, x_b y las cinco η/ε); solo se
  mueven T_fuente (391–409 K) y T_sumidero (280–293 K): 5 de 5 KALINA confiables, η hasta 10.6 %.
- **Tablas:** **4.3-3 «Escalera»** (por ronda y conjunto, los KALINA confiables, qué criterio rompe, cuál se
  eligió) y **4.3-4 «Verificación teqp contra motor real»**.
- **Figura 4.3-1:** barras de KALINA confiables por conjunto; verde oscuro = el elegido de cada ronda.
- **Conclusión:** ningún conjunto que conserve T_fuente = 623 K da KALINA confiable.

---

### Pregunta 5 — ¿Cuánta eficiencia se puede lograr?

#### Estudio 5.1 — Búsqueda de la η máxima
- **Qué se hizo:** 5 búsquedas (arranques) que conservan datos distintos del profesor.
- **Resultado:** η máxima **15.6 %** (parte 5.1d: presiones y clima del profesor, T_fuente 415 K, equipos a
  0.95). 5.1a, 15.0 %; 5.1b, 15.5 %; 5.1c, 12.7 %; 5.1e, 11.1 %.
- **Tabla 5.1-3 «Óptimos de η por arranque»:** el mejor punto de cada arranque, con todos sus datos.
- **Figura 5.1-1:** η contra iteración, una línea por arranque (trayectoria aceptada) y los puntos grises
  evaluados que no se aceptaron.
- **Conclusión:** 15.6 % es una **cota superior** con equipos al máximo, no un diseño.

---

### Pregunta 6 — ¿Son confiables los resultados?

#### Estudio 6.1 — Verificación con el motor real
- **Resultado:** teqp y el motor real coinciden en los puntos que el motor real resolvió (|Δη| < 0.003 pp).
  Con el piso de O2 en 303.55 K, 9 de 12 puntos clave pasan a CORREGIBLE (déficit 0.5–3.2 K).
- **Tablas:** **6.1-3 «Paridad teqp contra el motor real»** y **6.1-4 «Costo del subenfriamiento»** (exigir
  2 K de margen cuesta +25–46 kPa de P_baja y −0.3 a −0.5 pp de η).
- **Figura 6.1-1:** η con teqp (horizontal) contra η con el motor real (vertical); si todos están sobre la
  recta 1:1, los dos motores coinciden. La banda verde es ±0.7 pp.
- **Conclusión:** los resultados no dependen del motor, pero **los diseños están al filo**.

#### Estudio 6.2 — Húsavík
- **Qué se hizo:** reproducir la planta real de septiembre y explorarla.
  - **6.2a:** los 97 KALINA de septiembre se reproducen sin cambio de clase.
  - **6.2b (OFAT):** una variable a la vez desde el ancla de Húsavík.
  - **6.2c (malla):** x_b × P_baja.
  - **6.2d:** Húsavík con poco amoníaco (x_b 0.30–0.70).
  - **6.2e:** P_baja mínima con su piso de diseño.
- **Tablas:** 6.2-3 (catálogo de la reproducción), 6.2-4 (rangos KALINA por variable) y 6.2-5 (frontera al variar x_b).
- **Figuras:** 6.2-1 (malla x_b × P_baja con la línea de P_baja mínima) y 6.2-2 (η contra cada variable, una a la vez).
- **Conclusión:** la P_baja mínima KALINA sube unos 144 kPa por cada 0.1 de x_b. Con x_b ≤ 0.45 no hay ciclo.

---

### Anexo A.1 — Fuera del rango realista
Equipos con η y ε de 0.20 a 0.99. Solo ilustrativo: **no entra en las conclusiones ni en los gráficos**.

---

### Tablas de síntesis (S)

| Tabla | Qué muestra |
|---|---|
| **S-1 Resumen por estudio** | Una fila por estudio: diseño, corridas, genuinas, KALINA, confiables, criterio que más bloquea |
| **S-2 Qué se movió en cada barrido** | Matriz parte × variable: barrida, fija o igual al profesor (con colores) |
| **S-3 Rangos KALINA comparados** | p5, mediana y p95 de cada variable en los KALINA confiables de cada parte |
| **S-4 Datos del profesor conservables** | Cada dato del profesor y si se conserva con KALINA |
| **S-5 Criterios que bloquean** | Por estudio, qué % de los genuinos no KALINA falla cada criterio |

**Figura S-1:** barras apiladas: puntos por clase en cada estudio. **Figura S-2:** es la tabla S-2 con colores.

---

## 7. Las conclusiones (con su grado de confianza)

**Grados:** *Fuerte* = estadísticamente significativo y repetido en dos casos o métodos; *Moderada* =
significativo en uno o con intervalos solapados; *Indicativa* = patrón visible pero con pocos datos.

| # | Conclusión | Grado |
|---|---|---|
| C1 | La factibilidad la deciden **P_baja y ε_cond** (KS 0.43) y la razón de presiones (0.35); las eficiencias de las máquinas casi nada | Fuerte |
| C2 | La frontera KALINA es un umbral y los diseños quedan pegados a ella (A\* a < 6 % del rango en 8 de 9 variables) | Fuerte |
| C3 | El efecto de P_baja depende de P_alta (interacción): la P_baja mínima baja de 913 a 547 kPa | Fuerte |
| C4 | La frontera es multivariada: reglas de una variable no la capturan (CART 78.8 % contra 75.8 % base) | Moderada |
| C5 | **Lo que decide la clase no es lo que mueve η**: ε_cond decide sin mover η; P_alta, η_t y ε_reg mueven η sin decidir | Fuerte |
| C6 | P_baja es antagónica: asegura KALINA pero baja η 0.40–0.55 pp por cada 100 kPa | Fuerte |
| C7 | Cerca de A\*, η responde de forma lineal a las eficiencias y de forma no monótona a T_fuente y x_b | Fuerte / moderada |
| C8 | Un sumidero más frío ayuda sobre todo porque permite bajar P_baja (−12.5 a −25.7 kPa por K) | Fuerte |
| C9 | Más amoníaco exige más P_baja (+144 kPa por cada 0.1 de x_b) | Fuerte en Húsavík |
| C10 | La fuente a 623 K es incompatible con el resto del enunciado | Fuerte |
| C11 | Con la fuente a ~390–410 K se conservan 8 de los 10 datos de diseño | Fuerte |

### Robustez
- **Ranking estable** entre 300 y 500 puntos (ρ de Spearman 0.93 en KS y 0.99 en PRCC).
- **PAWN** da el mismo grupo líder que el PRCC.
- **teqp = motor real** en los 5 puntos comparables.
- **Reproducibilidad:** 41 de 41 de la Fase 1 y 97 de 97 de Húsavík.

### Lo que NO se puede afirmar
- El **orden** entre P_baja y ε_cond como decisores (sus intervalos se solapan).
- Una **regla de corte simple** para la factibilidad.
- **Tendencias globales** a partir de 3.1 (T_fuente y x_b no son monótonas alrededor de A\*).
- Lo que pasa con T_fuente > 410 K en el estudio 4.2, ni fuera de las cajas de muestreo.
- Diferencias de η menores de 0.7 pp.

---

## 8. Mapa del Excel

El libro tiene **95 hojas**. Se organiza así:

| Hojas | Qué hay |
|---|---|
| **LEEME**, **Nomenclatura**, **Indice** | Cómo leer el libro, cómo se numeran estudios y partes, y la lista de todas las hojas con vínculo |
| **Tablero** | Un selector (celda B2) que cambia cifras, condiciones y gráficos según el estudio o parte elegidos |
| **Punto_profesor** | Los 11 datos del profesor y el ancla A\* |
| **S-1 … S-5** y **S Gráficos** | Síntesis de toda la campaña |
| **N.M-1, N.M-2, N.M-3…** | Las tablas de cada estudio (condiciones, conteos, resultados) |
| **N.M-R Resultados por barrido** | Todos los puntos de cada estudio, barrido por barrido, **con sus gráficos al lado** |
| **N Gráficos** (2, 3, 4, 5, 6) | Los gráficos nativos de Excel de cada pregunta, todos juntos |
| **N Datos de gráficos** | Los números con los que Excel dibuja cada gráfico |
| **A.1** | El anexo fuera de rango |
| **Datos**, **Condiciones**, **Partes** | La tabla completa de puntos y las condiciones, con filtros |

**Cómo encontrar la gráfica de una tabla:** busca la hoja de la tabla (p. ej. `3.1-3`). La figura que se
construye con sus datos está debajo; las que se construyen con los puntos están a la derecha en la hoja
`N.M-R`.

**Dos cosas que conviene saber:**
- Una figura puede mostrar menos filas que su tabla porque **el gráfico dibuja solo lo que tiene resultado**
  (η) o, en las líneas de resumen, un valor derivado (por ejemplo, la P_baja mínima de cada clima).
- En 3.1 las figuras dibujan la malla **y** los vecinos de A\*; el ancla va aparte en «Puntos de referencia».

---

## 9. Los números que hay que recordar

| Dato | Valor |
|---|---|
| Datos del profesor | converge **0 de 41** |
| Ancla A\* | T_fuente 403 K, P_baja 563.64 kPa, η = 8.48 % |
| Lo que decide KALINA | P_baja y ε_cond (KS 0.43) |
| Lo que mueve η | P_baja (−0.68), P_alta (+0.58), η_t (+0.38) |
| Margen de A\* a la frontera de O2 | < 6 % del rango en 8 de 9 variables |
| Datos conservables | 8 de 10, con fuente a 391–409 K |
| Franja con presiones del profesor | T_fuente 390–410 K, ε_cond ≥ 0.875 |
| η máxima | 15.6 % (cota con equipos a 0.95); 8–11 % con equipos medios |
| Costo de 1 K de margen | ~14 kPa de P_baja y ~0.16 pp de η |
| Banda de incertidumbre de η | ±0.4–0.7 pp |

---

## 10. Preguntas probables y cómo responderlas

**1. ¿Por qué no usaron un análisis de varianza clásico (Sobol)?**
Porque pide ~6 100 puntos (unas 53 horas), exige resultado en todos los puntos y aquí muchos no
convergen. Se usó RSA/KS, que está hecho para salidas del tipo «cumple / no cumple» y tolera los fallos.

**2. ¿Qué es un LHS y por qué no puntos al azar?**
Es un muestreo que reparte los puntos de forma pareja en cada variable (cada tramo se usa una vez); con
pocos puntos cubre mejor el espacio que el azar simple.

**3. ¿Por qué estudian la sensibilidad alrededor de A\* y no del punto del profesor?**
Porque en el punto del profesor el ciclo no converge: no hay η ni márgenes que derivar. A\* es el punto
funcional más cercano al enunciado.

**4. ¿Qué significa KS = 0.43?**
Que la mayor diferencia entre las dos curvas acumuladas (la de los KALINA y la del resto) es de 0.43, es
decir, 43 puntos de probabilidad. Es de las mayores de todas las variables (empata con ε_cond) y p < 10⁻¹⁵:
no es casualidad.

**5. Si P_baja asegura KALINA, ¿por qué no subirla siempre?**
Porque baja la eficiencia (0.40–0.55 pp por cada 100 kPa) y, a P_baja muy alta, la razón de presiones tiende
a 1. Es una variable antagónica: ayuda a la clase y perjudica a η.

**6. ¿Los resultados dependen del programa de propiedades usado?**
No: teqp y el motor real coinciden en η con una diferencia menor de 0.003 pp en los puntos que el motor
real alcanzó a resolver. El motor real tiene un límite de tiempo y se cortó en varios.

**7. ¿Qué tan confiables son los diseños KALINA?**
Están pegados a la frontera de cavitación: con 2 K más de margen exigido, la P_baja sube 25–46 kPa y η
baja 0.3–0.5 pp. Un diseño sin margen es frágil frente al clima.

**8. ¿Por qué hay figuras con menos puntos que su tabla?**
Porque una figura de η solo puede dibujar los puntos que tienen η (los que no convergieron no tienen), y
porque algunas figuras son resúmenes (la P_baja mínima de cada clima, por ejemplo). La tabla `N.M-R` trae
todos los puntos.

**9. ¿Qué dato del profesor no se puede conservar?**
La temperatura de la fuente a 623 K. Todos los demás se pueden conservar si la fuente baja a unos 390–410 K.

**10. ¿Cuál es la eficiencia que se puede esperar?**
8 a 11 % con eficiencias medias de equipo y hasta ~15 % con equipos de 0.95 (que es un tope, no un diseño).

---

## 11. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Excel final | `datos/Excel_kalina_final_final_final.xlsx` |
| Informe de resultados | `analisis_final/INFORME_BARRIDOS_CAMPANA_FINAL.md` |
| Una ficha por estudio (objetivo, datos, resultados) | `analisis_final/04_fichas/Ficha_N.M_….md` |
| Tablas (CSV y Markdown) | `analisis_final/02_tablas/<estudio>/` |
| Figuras de Matplotlib (PNG, SVG y pie) | `analisis_final/03_figuras/<estudio>/` |
| Tabla canónica de todos los puntos | `analisis_final/01_datos/todos_los_puntos.csv` |
| Por qué se eligieron estos métodos | `docs/ESTUDIO_METODOS_SENSIBILIDAD.md` |
| Matemática del índice D y los márgenes | `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` |
| Tablero interactivo en HTML | `analisis_final/06_tablero/tablero_kalina.html` |

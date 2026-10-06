# Matemática de las iteraciones y del análisis de sensibilidad — campaña final

**Fecha:** 2026-10-05 · **Rama:** `test/barrido_final`
**Relacionados:** `docs/METODOLOGIA_BARRIDOS_FINAL.md` (qué se hace y en qué orden) ·
`docs/ESTUDIO_METODOS_SENSIBILIDAD.md` (por qué se eligieron estos métodos) ·
`docs/PLANTEAMIENTO_MATEMATICO.md` (ecuaciones del ciclo).

Este documento explica **cómo se calcula** cada paso. Cada sección empieza con una idea en lenguaje
sencillo y después da la fórmula. Los valores marcados como *propuesto* son tolerancias numéricas
del procedimiento, no supuestos de ingeniería del ciclo, y pueden ajustarse antes de ejecutar.

---

## 1. El modelo visto como una función

**Idea.** Para el análisis, el simulador es una "caja": recibe 10 números y devuelve una clase,
una eficiencia y unos márgenes.

Vector de entradas (10 variables):

```
v = (T_fuente, T_sumidero, P_alta, P_baja, x_b, ε_HRVG, ε_reg, ε_cond, η_t, η_p)
```

Cada evaluación f(v) resuelve el ciclo con `resolver_ciclo` (lazos de punto fijo en T1/T10 con
bracket tolerante MA) y lo clasifica con los 17 criterios. Devuelve:

```
f(v) → { clase ∈ {KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO},  η,  W_net,  m_O1, m_O2, m_O3, m_O5 }
```

**Normalización.** Para comparar variables con unidades distintas (K, kPa, adimensionales), cada
una se lleva al intervalo [0, 1] dentro de su rango realista [a_i, b_i]:

```
u_i = (v_i − a_i) / (b_i − a_i)
```

## 2. Márgenes y el índice de cercanía D

**Idea.** La clase solo dice "pasa" o "no pasa". Los márgenes dicen **cuánto** le falta al punto.
Un margen positivo significa que el criterio se cumple; uno negativo, que no se cumple.

| Criterio | Margen m (≥ 0 ⇒ cumple) | Unidad | Tolerancia τ |
|---|---|---|---|
| O1, título a la salida de la turbina | m_O1 = q4 − 0.90 | título | 0.01 |
| O2, cavitación de la bomba | m_O2 = T_burbuja(P_baja, x_b) − T9(T_amb = 300.03 K) | K | 1 K |
| O5, el separador recibe una mezcla bifásica | m_O5 = min(q2 − 0.001, 0.999 − q2) | título | 0.01 |
| O3, potencia neta positiva | m_O3 = W_net | kW | 1 kW |

T9 se recalcula con el condensador evaluado a max(T_sumidero, T_amb_diseno), igual que en
`src/restricciones/operativos.py`.

**Violación de cada criterio** (cero si se cumple):

```
viol_k = max(0, −m_k)
```

**Índice de cercanía a KALINA** (las τ las aprobó el usuario el 2026-10-05):

```
D = Σ_k viol_k / τ_k        k ∈ {O1, O2, O3, O5}
```

- D = 0 significa que el punto cumple todos los criterios operativos. Si además cumple los demás,
  es KALINA.
- Ejemplo: q4 = 0.87 y T9 está 2 K por encima de la burbuja ⇒ D = 0.03/0.01 + 2/1 = 3 + 2 = **5**.
  Este punto está "más lejos" que otro con D = 1.
- D siempre se reporta junto con el vector (viol_O1, viol_O2, viol_O3, viol_O5), para que se vea
  qué criterio falla.
- Los NO_CONVERGIO no tienen D, porque sin solución no hay estados. Sí entran en el RSA (§6).

## 3. M1 — Comparación con la corrida anterior

**Idea.** Se corren los mismos 41 puntos y se comparan uno por uno.

Para cada punto j se verifica:

```
clase_nueva(j) = clase_anterior(j)
|η_nueva(j) − η_anterior(j)| < 0.05 pp     (solo si ambas existen)
```

Se reporta la tasa de coincidencia (aciertos/41). Cualquier diferencia se explica antes de seguir.

## 4. M2 — Búsqueda del cambio mínimo (bisección)

**Idea.** Se mueve una variable desde el valor del profesor hasta que el ciclo empieza a funcionar.
En vez de probar todos los valores, se parte el intervalo por la mitad una y otra vez, como al
buscar una palabra en un diccionario.

**Paso 1: localizar la frontera.** Se avanza con pasos gruesos desde el valor del profesor v⁰
hasta encontrar un valor v⁺ donde el punto ya converge, mientras que en v⁻ (el anterior) no.

**Paso 2: bisección.** Se repite:

```
v_m = (v⁻ + v⁺)/2
si f(v_m) converge  → v⁺ = v_m
si no               → v⁻ = v_m
hasta que |v⁺ − v⁻| < tol
```

Número de evaluaciones: n ≈ log₂(|v⁺ − v⁻| / tol). Por ejemplo, bajar T_fuente de 623 K
explorando 243 K con tol = 0.5 K cuesta ~9 evaluaciones.

Tolerancias *propuestas*: T 0.5 K · P 10 kPa · x_b 0.005 · ε y η 0.005.

Se hace lo mismo para la frontera "convergente → KALINA", usando como señal el signo del margen
que bloquea.

**Paso 3: cierre de O2 con P_baja.** La regla del proyecto es que O2 se cierra con P_baja y nunca
subiendo las ε. Se busca la menor P_baja que cumple O2, porque una P_baja mayor reduce la expansión
en la turbina y con ello η:

```
P_baja* = mín { P_baja : m_O2(P_baja) ≥ 0 }      (bisección, tol 1 kPa — propuesto)
```

**Paso 4: distancia al profesor.** Por cada punto KALINA encontrado:

```
d = Σ_i |v_i − v_i^prof| / (b_i − a_i)
```

El **ancla A\*** es el punto KALINA con la menor d, es decir, el que exige cambiar menos los datos
del profesor. Si ningún punto llega a KALINA, A\* es el convergido con la menor D.

## 5. M3 — Una variable a la vez (OAT, 15 puntos)

**Idea.** Desde A\* se mueve una sola variable por todo su rango, en 15 pasos iguales, con las demás
fijas. Así se ve qué pasa con η y con los márgenes al moverla.

**Malla:**

```
v_i^(j) = a_i + (j − 1)·(b_i − a_i)/14        j = 1 … 15
```

10 variables × 15 = 150 evaluaciones.

**a) Elasticidad en A\*** (si sube la variable un 1 %, ¿qué % cambia η?). Se calcula con los dos
vecinos de A\*, mediante una diferencia centrada:

```
E_i = [η(v_i + h) − η(v_i − h)] / (2h) · (v_i / η)
```

|E_i| > 1 significa que η reacciona más que proporcionalmente.

**b) Efecto en el rango:** Δη_i = máx_j η − mín_j η, considerando solo los puntos convergidos.

**c) Dónde se cruza una frontera.** Si un margen cambia de signo entre dos puntos consecutivos
(m_j > 0 y m_{j+1} < 0), el valor de cruce se estima por interpolación lineal:

```
v* = v_j − m_j · (v_{j+1} − v_j) / (m_{j+1} − m_j)
```

Ejemplo: si m_O2 = +0.6 K con P_baja = 700 kPa y −0.4 K con 650 kPa, entonces
v* = 700 − 0.6·(650 − 700)/(−0.4 − 0.6) = 700 − 30 = **670 kPa**. Por debajo de 670 kPa aparece cavitación.

**d) Regla de lectura:** una diferencia de η menor que la banda de incertidumbre (±0.4–0.7 pp,
G4-01) se marca como **no concluyente**.

## 6. M4 — Muestreo global LHS y análisis de sensibilidad

### 6.1 Muestreo LHS (Latin Hypercube)

**Idea.** Se quieren 250 puntos repartidos de forma pareja por todo el espacio de 10 dimensiones.
Cada rango se divide en 250 franjas iguales y se pone exactamente un punto en cada franja de cada
variable. Así ninguna zona queda sin explorar, algo que puede pasar con un sorteo al azar.

```
u_i^(n) = (π_i(n) − U_i^(n)) / N        n = 1 … N,   N = 250
```

π_i es una permutación aleatoria de {1, …, N} distinta para cada variable, y U ~ Uniforme(0, 1)
sitúa el punto dentro de su franja. Después se vuelve a unidades físicas con
v_i = a_i + u_i (b_i − a_i). La semilla queda fija y anotada (`scipy.stats.qmc.LatinHypercube`).

### 6.2 RSA — análisis regional (método principal)

**Idea.** Los 250 puntos se separan en dos grupos: B = KALINA y B̄ = los demás (incluidos los
NO_CONVERGIO). Para cada variable se pregunta: ¿sus valores se reparten igual en los dos grupos?
- Si se reparten igual, esa variable no decide nada.
- Si no, decide la factibilidad, y la diferencia muestra en qué rango hay que ponerla.

**Distribución acumulada empírica** de la variable i en el grupo B (fracción de puntos KALINA cuyo
valor es ≤ u):

```
F_B(u) = (1/|B|) · #{ n ∈ B : u_i^(n) ≤ u }
```

Lo mismo se calcula para F_B̄(u).

**Estadístico de Kolmogorov–Smirnov:** la máxima separación vertical entre las dos curvas.

```
KS_i = máx_u | F_B(u) − F_B̄(u) |       ∈ [0, 1]
```

- KS_i ≈ 0: la variable da igual para ser KALINA.
- KS_i cercano a 1: la variable decide. Por ejemplo, todos los KALINA tienen P_baja alta y ninguno
  de los demás.
- Valor p: prueba KS de dos muestras (`scipy.stats.ks_2samp`). Con p < 0.05, la diferencia no se
  explica por azar.

**Rango favorable:** el intervalo entre los percentiles 5 y 95 de la variable dentro de B. Es
"donde viven" los puntos KALINA.

**Por criterio:** el mismo cálculo se repite con otras separaciones, por ejemplo "cumple O2 / no
cumple O2" o "converge / no converge". Así se sabe qué variable controla cada barrera.

**Requisito *propuesto*:** al menos 20 puntos en cada grupo. Si B queda chico, se añade un segundo
LHS concentrado en la caja que señalan los rangos favorables.

### 6.3 PAWN — sensibilidad sin suponer formas

**Idea.** Se mira cuánto cambia la distribución completa de η (o de D) cuando se fija una variable
en una franja de su rango. Si al fijarla la distribución casi no cambia, la variable importa poco.

1. F_y = distribución acumulada de y (η o D) con todos los puntos convergidos.
2. El rango de u_i se divide en n = 10 franjas *(propuesto)*. En cada franja c se calcula
   F_{y|c}, la distribución acumulada de y usando solo los puntos que caen en esa franja.
3. Para cada franja: KS_{i,c} = máx_y | F_y(y) − F_{y|c}(y) |.
4. Índice de la variable: **T_i = mediana_c KS_{i,c}**. También se reporta el máximo.

### 6.4 PRCC — en qué sentido conviene mover cada variable

**Idea.** La correlación dice si al subir una variable η sube o baja. La versión "parcial de
rangos" quita el efecto de las otras 9 variables y funciona aunque la relación sea curva, siempre
que vaya en un solo sentido.

1. Se reemplaza cada valor por su posición (rango) dentro de la muestra.
2. Se calculan los residuos de la variable i y de la salida, quitándoles lo que explican las demás
   variables por regresión lineal:
   ```
   r_x = rango(v_i) − ajuste(rango(v_i) | rangos de las otras 9)
   r_y = rango(y)   − ajuste(rango(y)   | rangos de las otras 9)
   ```
3. **PRCC_i = correlación(r_x, r_y)**, que va de −1 a +1.
   - +1: subir la variable siempre sube y.
   - −1: subir la variable siempre baja y.
   - 0: no hay relación.
4. Significancia: t = PRCC · √[(N − 2 − p)/(1 − PRCC²)], con p = 9 variables de control.

Se calcula para η y para cada margen, por ejemplo "subir P_baja aumenta m_O2".

### 6.5 CART — reglas de la región KALINA

**Idea.** Un árbol de decisión que hace preguntas sí/no ("¿P_baja > 650?") y termina diciendo
"KALINA" o "no KALINA". Lo útil es que las reglas se leen directamente.

En cada nodo se elige la variable y el umbral que dejan los dos grupos lo más "puros" posible.
La impureza se mide con el índice de Gini:

```
G = 1 − Σ_c p_c²
```

p_c es la fracción de cada clase en el nodo: G = 0 si el nodo es todo de una clase y G = 0.5 si
está mitad y mitad.

Para que las reglas sean legibles: profundidad máxima 4 y al menos 5 puntos por hoja
*(propuesto)*. La exactitud se valida con validación cruzada de 5 particiones (`scikit-learn`).

### 6.6 Robustez de los índices

**Bootstrap.** Se toman 1 000 muestras de 250 puntos con reemplazo a partir de la muestra original
y se recalcula cada índice (KS, T_i, PRCC). El intervalo de confianza del 95 % va del percentil
2.5 al 97.5. Si dos variables tienen intervalos solapados, su orden en el ranking no es seguro.

**Convergencia.** Los índices se calculan con los primeros 150 puntos y con los 250. Si el orden
cambia (correlación de Spearman entre ambos rankings < 0.9 *(propuesto)*), se amplía la muestra.

## 7. M5 — Variables derivadas y búsqueda dirigida

### 7.1 Diferenciales de diseño

Con los mismos puntos se calculan las variables derivadas y el RSA y el PRCC se aplican también
sobre ellas:

```
ΔP     = P_alta − P_baja          [kPa]
r_P    = P_alta / P_baja          [−]
ΔT_fs  = T_fuente − T_sumidero    [K]
ΔT_HRVG = T_fuente − T2           [K]   (approach del HRVG)
```

El rango favorable de cada uno (percentiles 5–95 dentro de KALINA) es la **recomendación de
diseño**, y se contrasta con los valores publicados por Elsayed 2013, Nguyen 2014 y Nemati 2017.

### 7.2 Búsqueda dirigida hacia KALINA (búsqueda por patrones)

**Idea.** Se parte de los mejores puntos y se prueba mover cada variable un paso hacia arriba y
hacia abajo, aceptando el cambio si mejora. Cuando ningún movimiento mejora, el paso se reduce a
la mitad. No necesita derivadas, y un punto que no converge simplemente se rechaza.

**Objetivo lexicográfico** (primero acercarse a KALINA y después ganar eficiencia):

```
minimizar  (D, −η)       primero D; a igual D (= 0), mayor η
sujeto a   a_i ≤ v_i ≤ b_i,   ε ∈ [0.75, 0.85]
```

**Algoritmo:**

```
paso_i = 0.1·(b_i − a_i)
repetir:
  para cada variable i señalada por el RSA:
    probar v ± paso_i·e_i; aceptar si (D, −η) mejora
  si ninguna mejoró: paso_i ← paso_i/2
hasta paso_i < tol_i   o   60 evaluaciones por arranque
```

Se usan 3 arranques: A\* y los 2 mejores puntos del LHS.

## 8. M6 — Verificación

Para los puntos verificados con el motor riguroso (`AmmoniaWaterAdapter`):

```
misma clase   y   |η_real − η_teqp| / η_real
```

Y para toda comparación de η entre puntos se aplica la regla:

```
|Δη| < banda (0.4–0.7 pp)  ⇒  "no distinguible"
```

## 9. Resumen de costos (~31 s por evaluación)

| Paso | Evaluaciones | Fórmula de costo |
|---|---|---|
| M1 | 41 | fijo |
| M2, bisecciones | ~10 por frontera × ~8 fronteras + mallas 2D | log₂(rango/tol) |
| M3, OAT | 150 | 15 × 10 |
| M4, LHS | 250 (+ ampliación si hace falta) | N |
| M5, búsqueda | ≤ 180 | 3 arranques × 60 |
| M6 | ~10 con el motor real (~5 min c/u) | — |

## Referencias

Las referencias de los métodos están en `docs/ESTUDIO_METODOS_SENSIBILIDAD.md`.

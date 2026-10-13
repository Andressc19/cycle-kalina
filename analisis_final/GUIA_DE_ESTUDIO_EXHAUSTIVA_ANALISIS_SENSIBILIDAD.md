# Guía de estudio exhaustiva — Análisis de sensibilidad del ciclo Kalina KCS-11

*Explica, resultado por resultado, qué se hizo en la campaña final de barridos (resultados generados entre el
6 y el 9 de octubre de 2026), con qué método, qué tablas y gráficos lo sostienen y en qué hoja del libro
`datos/Excel_kalina_final_final_final.xlsx` se ven. Escrita el 2026-10-12.*

*Las cifras de tablas, figuras y hojas se generan automáticamente desde los datos
(`scripts/analisis_final/a6_guia_exhaustiva.py`); la narrativa viene de las fichas de cada estudio
(`04_fichas/`) y del informe de la campaña.*

---

## Cómo está organizada esta guía

| Parte | Contenido | Para qué sirve |
|---|---|---|
| **I. Base conceptual** | Problema, variables, criterios, clases, métodos con sus fórmulas | Entender las palabras y los métodos antes de ver resultados |
| **II. Resultados** | Once resultados, cada uno con: qué se hizo, tablas, figuras, hojas del Excel, qué dice y qué no dice | **Explicar el trabajo**: está ordenado por lo que se encontró, no por fecha |
| **III. El libro Excel, hoja por hoja** | Las 95 hojas con lo que contiene cada una | Saber dónde está cada cosa |
| **IV. Catálogo de tablas** | Las 58 tablas con su fuente, filtro y columnas | Consultar una tabla concreta |
| **V. Catálogo de figuras** | Las 30 figuras con su pie completo | Consultar una figura concreta |
| **VI. Cierre** | Preguntas probables, límites, inconsistencias conocidas y fuentes | Preparar la exposición |

**Cómo leer un resultado (Parte II).** Cada uno sigue el mismo orden: *la pregunta* → *el resultado en una
frase* → *qué se hizo* → *tablas* → *figuras* → *dónde verlo en el Excel* → *qué dice y qué no dice* →
*cómo explicarlo en 30 segundos*.

---

# PARTE I — Base conceptual

## I.1 El problema

El enunciado del curso fija un ciclo Kalina **KCS-11** (mezcla amoníaco–agua) con una fuente de gases a
350 °C (623.15 K), un sumidero a 27 °C (300.03 K) y unos datos de diseño. Los componentes del ciclo son:
generador de vapor de recuperación de calor (**HRVG**), separador, turbina, regenerador, válvula de
estrangulamiento, absorbedor, condensador y bomba.

La campaña respondió seis preguntas:

1. ¿Funciona el ciclo con los datos del profesor?
2. Si no, ¿qué es lo mínimo que hay que cambiar para que funcione?
3. ¿Qué variables importan y cuánto?
4. ¿Qué datos del profesor se pueden conservar?
5. ¿Cuánta eficiencia se puede lograr?
6. ¿Son confiables los resultados?

## I.2 Las variables

**Variables de entrada (10):**

| Símbolo | Qué es | Valor del profesor (PP) |
|---|---|---|
| T_fuente | Temperatura de la fuente de calor | 623.15 K |
| T_sumidero | Temperatura del sumidero | 300.03 K |
| P_alta | Presión de alta | 3000 kPa |
| P_baja | Presión de baja | 400 kPa |
| x_b | Fracción de amoníaco de la mezcla base | 0.50 |
| η_t | Eficiencia isentrópica de la turbina | 0.85 |
| η_p | Eficiencia isentrópica de la bomba | 0.75 |
| ε_HRVG | Efectividad del generador de vapor | 0.85 |
| ε_reg | Efectividad del regenerador | 0.75 |
| ε_cond | Efectividad del condensador | 0.80 |

Además hay un flujo másico base **m_b = 1 kg/s**, que no se mueve (por eso W_net se da «por kg/s»).

**Variables derivadas** (se calculan con las anteriores):

| Símbolo | Definición | Para qué se usa |
|---|---|---|
| ΔP | P_alta − P_baja | Ventana de presiones de diseño |
| r_P | P_alta / P_baja (razón de presiones) | Ventana de presiones de diseño; r_P → 1 significa casi sin expansión |
| ΔT_fs | T_fuente − T_sumidero | Salto térmico disponible |

**Salidas:** la **clase** del punto; η (eficiencia térmica, en %); W_net (trabajo neto, kW por kg/s); los
**márgenes** de cada criterio (cuánto le sobra o le falta).

## I.3 Cómo se decide si un punto es KALINA

Para cada combinación de datos el programa resuelve el ciclo y evalúa una lista de restricciones. Las que
aparecen en las tablas con su código son:

| Código | Qué comprueba |
|---|---|
| **N2** | Balance de energía global del ciclo (si no cierra, el punto es un «falso convergido») |
| **N3** | Balance de especie (separador y absorbedor) |
| **S1–S3** | La entropía no puede bajar en turbina, bomba y válvula |
| **S4** | Sin cruce de temperaturas en el regenerador |
| **S5** | La salida del HRVG no supera la temperatura de la fuente |
| **S6** | La salida del condensador no baja de la temperatura del sumidero |
| **S7–S8** | Efectividades en [0, 1]; η menor que la de Carnot |
| **C1** | Orden de composiciones: pobre < x_b < rica |
| **C2, C3** | Composiciones en (0, 1); caudales del separador que suman el base |
| **O1** | Vapor a la salida de la turbina con título q4 ≥ 0.90 |
| **O2** | **Cavitación**: el líquido llega subenfriado a la bomba (T_burbuja(P_baja, x_b) − T de entrada ≥ 0) |
| **O3** | Trabajo neto positivo (W_net > 0) |
| **O5** | El separador recibe mezcla de dos fases (q2 entre 0.001 y 0.999) |

**Clases** (4 niveles + falsos convergidos):

| Clase | Significado | Color |
|---|---|---|
| **KALINA** | Cumple todos los criterios | verde |
| **CORREGIBLE** | Falla un criterio operativo (casi siempre O2) | naranja |
| **INVIABLE** | Falla un criterio estructural (O3, O5…) | amarillo |
| **NO_CONVERGIO** | El modelo no encontró un ciclo | rojo |
| **Falso convergido** | El solver dijo que convergió pero la solución es espuria; no cuenta | gris |

**Palabras que se repiten:**

| Término | Significado |
|---|---|
| **Genuino** | KALINA, CORREGIBLE o INVIABLE: el modelo lo resolvió de verdad |
| **KALINA confiable** | KALINA dentro del rango validado del modelo de propiedades (IAPWS G4-01) y con todas las η y ε entre 0.40 y 0.95 |
| **Fuera de rango** | Estados fuera del rango validado (p. ej. líquido por encima de 420 K): su η se toma con cautela |
| **Banda de η** | Incertidumbre del modelo de propiedades: ±0.4–0.7 pp. Una diferencia menor no es concluyente |
| **Piso de O2** | Temperatura con la que se evalúa la cavitación: 300.03 K fija en 1.1–3.1; desde 2.4 es igual a la T_sumidero de cada punto |
| **PP** | Punto del profesor: sus datos exactos |
| **A\*** | Punto ancla: el PP con solo T_fuente = 403 K y P_baja = 563.64 kPa; es KALINA con η = 8.48 % |
| **Parte** | Subconjunto de un estudio con sus propios datos fijos (2.4a). **Solo se comparan puntos de la misma parte** |
| **Motor teqp / motor real** | teqp es el motor de propiedades rápido; el «motor real» es el riguroso (más lento) con el que se verifica |
| **Protección A+B** | A: si el resultado de teqp cae en una zona de riesgo de fase, se repite esa llamada con el motor real. B: a los KALINA se les recalcula h4s con el motor real y, si difiere más de 2.0 kJ/kg, se marcan «no verificados» (se señala, no se reclasifica) |

**Índice de cercanía D.** Convierte «qué tan lejos está un punto de ser KALINA» en un número:

```
D = v_O1/0.01 + v_O2/1 K + v_O5/0.01 + v_O3/1 kW
```

donde cada `v` es cuánto viola su criterio (0 si lo cumple). D = 0 significa que cumple todos los criterios
operativos. Ejemplo: q4 = 0.87 y T9 está 2 K por encima de la burbuja → D = 0.03/0.01 + 2/1 = 5. Los puntos
que no convergen no tienen D.

## I.4 Los métodos, con sus fórmulas

### Malla y bisección (estudios 2.1–2.4, 4.2, 6.2)
Se barre una (o dos) variables en una cuadrícula y, donde cambia la clase, se parte el intervalo a la mitad
repetidamente:

```
v_m = (v⁻ + v⁺)/2 ;  si f(v_m) converge → v⁺ = v_m  si no → v⁻ = v_m ;  hasta |v⁺ − v⁻| < tol
```

Tolerancias: 0.5 K en temperaturas, 10 kPa en presiones, 0.005 en fracciones y efectividades. Número de
evaluaciones ≈ log₂(|v⁺ − v⁻| / tol).

### Cierre de O2 con P_baja
La regla del proyecto es cerrar O2 subiendo P_baja y nunca subiendo las ε. Se busca la **menor** P_baja con
margen de O2 ≥ 0, porque una P_baja mayor reduce la expansión de la turbina y con ella η.

### Distancia al profesor
Para cada KALINA: **d = Σ |v_i − v_i,prof| / (b_i − a_i)**, con [a_i, b_i] el rango de la variable. El ancla A\*
es el KALINA de menor d.

### OAT y elasticidad (estudio 3.1)
Una variable a la vez, 15 puntos equiespaciados `v = a + (j−1)(b−a)/14`. Para cada variable:

- **Elasticidad** `E = [η(v+h) − η(v−h)] / (2h) · (v/η)` con h = 1 % del rango; |E| > 1 = η reacciona más que
  proporcionalmente.
- **Δη = η máx − η mín** sobre los puntos genuinos con W_net > 0.
- **Cruce de frontera**: si un margen cambia de signo entre dos puntos, `v* = v_j − m_j (v_{j+1}−v_j)/(m_{j+1}−m_j)`.

### LHS — muestreo hipercubo latino (estudios 3.2, 3.3, 4.1, 4.3)
Cada variable se divide en N franjas iguales y se pone exactamente un punto por franja, con permutaciones
distintas por variable. Cubre el espacio de forma pareja con pocos puntos. Semilla fija (p. ej. 20261007 + k
en 4.1).

### RSA y KS (método principal de 3.2)
Los puntos se separan en B = KALINA y B̄ = el resto (incluidos los que no convergieron). Para cada variable se
comparan las dos curvas acumuladas:

```
KS = máx_u | F_B(u) − F_B̄(u) |   ∈ [0, 1]
```

KS ≈ 0: la variable no decide; KS cercano a 1: decide. El **rango favorable** es el intervalo entre los
percentiles 5 y 95 de la variable dentro de B. El mismo cálculo se repite por criterio («cumple O2»,
«cumple O1», «converge»).

### PRCC (3.2)
Correlación parcial de rangos: se reemplaza cada valor por su posición, se quita lo que explican las otras
9 variables por regresión lineal y se correlacionan los residuos. Va de −1 a +1; el signo dice si subir la
variable sube o baja la salida. Significancia: `t = PRCC·√[(N−2−p)/(1−PRCC²)]` con p = 9.

### PAWN (3.2)
Compara la distribución de η con y sin fijar una variable en franjas (n = 10) mediante KS; el índice es la
mediana de los KS por franja. No supone linealidad ni monotonía.

### CART (3.2)
Árbol de decisión (profundidad 4, mínimo 5 puntos por hoja, validación cruzada de 5 particiones). Impureza
de Gini `G = 1 − Σ p_c²`.

### Bootstrap y convergencia (3.2)
Bootstrap: 1000 remuestreos con reemplazo para el intervalo de confianza al 95 %. Si dos intervalos se
solapan, su orden no es seguro. Convergencia: se repiten los índices con 300 y con 500 puntos; si la
correlación de Spearman entre rankings baja de 0.9, se amplía la muestra.

### Búsqueda por patrones (5.1)
Objetivo lexicográfico: primero D → 0 y después máxima η. Pasos de ±10 % del rango que se reducen a la
mitad si nada mejora; corte con paso < 1 % o 120 evaluaciones por arranque.

### Escalera de conservación (4.3)
Selección hacia adelante: en cada ronda se suma al mejor conjunto un grupo más de datos del profesor y se
elige el que deja más KALINA confiables.

### Verificación cruzada (6.1, 4.3)
Los puntos clave se repiten con el motor real y se compara clase y η; el motor real necesita ~1500 s por
punto, y con 300 s se corta.

### Métodos que se revisaron y no se usaron

| Método | Motivo |
|---|---|
| Morris | Pierde ~la mitad de los efectos si p = 0.3 de los puntos no converge; con solo 10 variables aporta poco |
| Sobol | ~6 100 puntos (~53 h) y exige salida en todos los puntos |
| eFAST | Mismos problemas que Sobol |
| Metamodelo + Sobol | Los sustitutos suaves se ajustan mal a fronteras bruscas; queda como trabajo futuro |

## I.5 Nomenclatura y cómo se lee una hoja

Todo se numera **pregunta (1–6) → estudio (2.4) → parte (2.4a)**. Tablas y figuras siguen al estudio
(Tabla 4.1-1, Figura 3.2-2); las de síntesis llevan **S**; el anexo, **A**.

**Tipos de punto** (columna «Tipo de punto» en las hojas `N.M-R`):

| Tipo | Qué es |
|---|---|
| **malla** | Punto de una cuadrícula regular |
| **bisección** | Punto agregado para afinar una frontera |
| **oat** | Punto de un barrido de una variable a la vez (Húsavík) |
| **ancla** | A\* mismo |
| **vecino** | Punto pegado a A\* (±1 % del rango) para la elasticidad |
| **lhs** | Punto de un muestreo hipercubo latino |
| **busqueda** | Punto evaluado por la búsqueda por patrones |
| **control** | Punto de verificación o de control |

**Tres tablas que tiene cada estudio:** `N.M-1` (qué quedó fijo y qué se barrió), `N.M-2` (corridas por parte
y por clase) y `N.M-R` (todos los puntos, barrido por barrido).

---

# PARTE II — Los resultados

*Las equivalencias entre este orden y el cronológico están en la Parte III (hoja `Nomenclatura`).*

## R1. Con los datos del profesor el ciclo no converge

**Pregunta que responde:** ¿funciona el ciclo con los datos del enunciado?

**Resultado en una frase:** no. De 42 corridas con los datos del profesor y variaciones menores, **ninguna
converge**.

### Qué se hizo (estudio 1.1)
Se repitieron los 41 puntos de la Fase 1 de septiembre más el punto base con el otro motor (42 corridas):

| Parte | Qué se movió | Rango | n |
|---|---|---|---|
| 1.1a | nada (punto del profesor con teqp y con el motor real) | — | 2 |
| 1.1b | P_alta | 2000–4000 kPa | 9 |
| 1.1c | x_b | 0.40–0.70 | 7 |
| 1.1d | T_sumidero (perfil horario del enunciado) | 297.95–303.55 K | 24 |

Método: repetición punto a punto y comparación de clase antes/después (criterio: misma clase y
|Δη| < 0.05 pp). 6 procesos, 300 s por punto; 603 s en total, mediana 76 s.

### Tablas que lo sostienen

**Tabla 1.1-2 — Corridas por parte y por clase.** Cuenta cuántos puntos hay de cada clase en cada parte.

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1b · solo P_alta | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |
| 1.1a · punto del profesor | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| 1.1c · solo x_b | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 |
| 1.1d · temperatura ambiente hora a hora | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 24 | 0 | 0 |

*Tabla 1.1-2 · hoja «1.1-2 Corridas por parte y por» · 4 filas.*

Columnas:
- **Parte.** Subconjunto del estudio con sus propios datos fijos (p. ej. 2.4a). Solo se comparan puntos de la misma parte.
- **Corridas.** Puntos calculados en la parte.
- **Omitidos.** Puntos que el modelo no llegó a evaluar; no aparecen ni en las tablas de resultados ni en los gráficos.
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **KALINA.** Puntos que cumplen todos los criterios.
- **KALINA confiables.** KALINA dentro del rango validado de propiedades (IAPWS G4-01) y con η y ε entre 0.40 y 0.95.
- **Corregibles.** Puntos que fallan un criterio operativo (casi siempre O2, cavitación).
- **Inviables.** Puntos que fallan un criterio estructural (O3, O5…).
- **No convergidos.** Puntos en que el modelo no encontró un ciclo.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **Fuera de rango.** Puntos con estados fuera del rango validado de propiedades (p. ej. líquido por encima de 420 K); su η se toma con cautela.

*Lectura:* en las cuatro partes, «No convergidos» es igual a «Corridas» y «Genuinos» es 0.

**Tabla 1.1-3 — Comparación antes y después de la Fase 1.** Una fila por punto de la Fase 1 (41): clase y η de
septiembre contra la del código actual, con el mensaje del solver. Primeras filas:

| Grupo | Valor | Clase (antes) | Clase (ahora) | Misma clase | η (antes) [%] | η (ahora) [%] |
|---|---|---|---|---|---|---|
| base | — | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 2000 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 2250 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 2500 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 2750 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 3000 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 3250 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |
| P_alta | 3500 | NO_CONVERGIO | NO_CONVERGIO | sí | — | — |

*Tabla 1.1-3 · hoja «1.1-3 Comparación antes y despu» · 41 filas (se muestran 8).*

Columnas:
- **Grupo.** Qué se movió en ese punto (base, P_alta, x_b, T_sumidero); en 3.2-5 y 4.1-4, el grupo comparado (KALINA o no KALINA).
- **Valor.** Valor de la variable del grupo.
- **Clase (antes).** Clase que tuvo el punto en la Fase 1 de septiembre.
- **Clase (ahora).** Clase con el código actual.
- **Misma clase.** «sí» si ambas clases coinciden.
- **η (antes) [%].** Eficiencia de la Fase 1 (vacía si no convergió).
- **η (ahora) [%].** Eficiencia con el código actual (vacía si no convergió).
- **Δη [pp].** η de ahora − η de la Fase 1, en puntos porcentuales (vacía si alguna no existe).
- **Mensaje (antes).** Texto con que el solver explicó el fallo en la Fase 1.
- **Mensaje (ahora).** Texto con que el solver explica el fallo ahora.

*Lectura:* la columna «Misma clase» es verdadera en los 41 puntos: el código actual reproduce al profesor.
Los mensajes dicen por qué no converge: *«no existe equilibrio líquido-vapor»* a T = 623 K y, en el motor
real, *«presupuesto de tiempo agotado»*.

**Tabla 1.1-1 — Condiciones.** Qué quedó fijo y qué se barrió en cada parte (52 filas, siete columnas).

Columnas:
- **Parte.** Subconjunto del estudio con sus propios datos fijos (p. ej. 2.4a). Solo se comparan puntos de la misma parte.
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Estado.** Papel de la variable en la parte: «Una a la vez» (se mueve ella sola, con las demás fijas), «Barrida» (se mueve junto con otras), «Fija» (queda en un valor) o «Sin dato» (no aplica).
- **Valor o rango.** Valor fijo, o rango [mínimo – máximo] barrido.
- **n valores.** Cantidad de valores distintos probados de esa variable en la parte.
- **¿Igual al profesor?.** «sí» si el valor fijo coincide con el del enunciado.
- **Unidad.** Unidad de la variable.

### Figuras
**Ninguna.** No hay nada que graficar: no hay resultados.

### Dónde verlo en el Excel
Hojas `1.1-1`, `1.1-2`, `1.1-3` y `1.1-R Resultados por barrido` (los 42 puntos, todos «No convergió»).

### Refuerzos de este resultado en otros estudios
- **2.1:** con un solo cambio sobre el profesor, 0 KALINA.
- **2.4d:** profesor exacto con clima de 278 a 300 K: 0 genuinos en los cinco climas (Tabla 2.4-3, Base B4).
- **4.3, ronda 3:** el conjunto «x_b + P_alta + eficiencias + T_fuente» da 30 de 30 NO_CONVERGIO.

### Qué dice y qué no dice
- **Dice:** el código actual reproduce al profesor; mover solo P_alta, x_b o el clima no cambia nada, así que
  el bloqueo está en el lado caliente.
- **No dice:** que el ciclo Kalina «no funcione» en general; dice que **no con estos datos y este modelo**.
- **Límite:** no se corrió el contraexperimento sin el bracket tolerante, así que no se separa su efecto del
  de los otros cambios de código. Además, la Fase 1 usó un piso de O2 de 303.55 K; no importa aquí porque O2
  solo se evalúa en puntos que convergen.

> **Cómo explicarlo (30 s):** *«Antes de cambiar nada comprobé que mi código da lo mismo que el del
> profesor: con sus datos el ciclo no converge, en los 41 puntos. Mover presión, composición o clima no lo
> arregla. El problema está del lado caliente.»*

---

## R2. Un solo cambio no alcanza; con dos cambios aparece el punto ancla A\*

**Pregunta:** ¿qué es lo mínimo que hay que cambiar?

**Resultado:** con un cambio, 0 KALINA; con dos (bajar la fuente a ~403 K y subir P_baja a 563.64 kPa), sí.
Ese punto es **A\***, con η = 8.48 %.

### Qué se hizo

**Estudio 2.1 — un solo cambio.** Cada una de las 10 variables, de a una, con las otras nueve en el valor del
profesor: 10 valores equiespaciados por variable + bisección de las fronteras (132 corridas: 100 de malla y
32 de bisección). Las η y ε se movieron en [0.75, 0.85]. Tolerancias de bisección: 10 kPa, 0.5 K, 0.005.

**Estudio 2.2 — dos cambios.** O2 se cierra subiendo P_baja, así que P_baja es siempre la segunda variable:

| Ruta | Variable 1 | Variable 2 | Malla | Corridas |
|---|---|---|---|---|
| **A** (conserva fuente y sitio del profesor) | ε_HRVG: 0.75 / 0.78 / 0.81 | P_baja 400–2000 kPa, 12 valores | 3 × 12 | 36 |
| **B** (baja la fuente) | T_fuente: 380, 390, 403, 420, 434, 466, 497, 529, 560 K | P_baja 400–2000 kPa, 12 valores | 9 × 12 | 108 + 36 de bisección |

Total 180 corridas. Bisección sobre P_baja donde cambia «ser KALINA» o el signo del margen de O2 (tolerancia
10 kPa, hasta 8 iteraciones).

### Tablas

**Tabla 2.1-2 — Corridas por clase.**

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.1 | 132 | 0 | 15 | 0 | 0 | 13 | 2 | 96 | 21 | 32 |

*Tabla 2.1-2 · hoja «2.1-2 Corridas por parte y por» · 1 filas.*

**Tabla 2.1-3 — Distancia al punto del profesor, una variable a la vez.** Una fila por variable: cuántos
puntos convergen, cuántos son KALINA, el valor que más se acerca al profesor y el D mínimo.

| Variable | Tipo | Convergen | KALINA | Corregibles | Inviables | No convergidos | Valor convergido más cercano al PP | D mínimo | Valor de D mínimo |
|---|---|---|---|---|---|---|---|---|---|
| P_alta | diseño | 13 | 0 | 0 | 0 | 24 | 5414.062 | 28.588 | 8000 |
| P_baja | diseño | 0 | 0 | 0 | 0 | 10 | — | — | — |
| x_b | diseño | 2 | 0 | 0 | 1 | 13 | 0.317 | 17.194 | 0.3 |
| η_t | diseño | 0 | 0 | 0 | 0 | 10 | — | — | — |
| η_p | diseño | 0 | 0 | 0 | 0 | 10 | — | — | — |
| ε_HRVG | diseño | 9 | 0 | 7 | 0 | 5 | 0.825 | 18.076 | 0.75 |
| ε_reg | diseño | 0 | 0 | 0 | 0 | 10 | — | — | — |
| ε_cond | diseño | 0 | 0 | 0 | 0 | 10 | — | — | — |
| T_fuente | sitio | 12 | 0 | 6 | 1 | 15 | 600.046 | 2.018 | 402.922 |
| T_sumidero | sitio | 0 | 0 | 0 | 0 | 10 | — | — | — |

*Tabla 2.1-3 · hoja «2.1-3 Distancia al punto del pr» · 10 filas.*

Columnas:
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Tipo.** «diseño» (dato de diseño del ciclo) o «sitio» (condición del lugar: T_fuente, T_sumidero).
- **Convergen.** Puntos de la variable en que el solver reportó convergencia (incluye los falsos convergidos).
- **KALINA.** Puntos que cumplen todos los criterios.
- **Corregibles.** Puntos que fallan un criterio operativo (casi siempre O2, cavitación).
- **Inviables.** Puntos que fallan un criterio estructural (O3, O5…).
- **No convergidos.** Puntos en que el modelo no encontró un ciclo.
- **Valor convergido más cercano al PP.** Valor de la variable más cercano al del profesor entre los puntos que convergen.
- **Valor KALINA más cercano al PP.** Valor de la variable más cercano al del profesor entre los KALINA (vacío si no hay).
- **d normalizado.** Distancia al profesor del KALINA más cercano: Σ|v − v_prof| / (b − a). Vacío si no hay KALINA.
- **D mínimo.** Menor índice de cercanía D de la fila (0 = cumple todos los criterios operativos).
- **Valor de D mínimo.** Valor de la variable en el que D es mínimo.
- **Criterios bloqueantes frecuentes.** Códigos de restricción que más fallan entre los puntos de la fila, con su conteo entre paréntesis (ver el glosario de códigos).

*Lectura:* solo T_fuente y ε_HRVG dan puntos corregibles; en todas las demás hay 0 o solo falsos
convergidos. La fila de T_fuente tiene D mínimo = 2.018 en T_fuente = 402.9 K: es el punto más cercano a ser
KALINA, y le falta cumplir O2 por 2.0 K.

**Tabla 2.2-3 — Resumen de la malla de dos cambios.** Una fila por ruta y valor de la variable 1.

| Ruta | Variable 1 | Valor 1 | Genuinos | KALINA | Falsos convergidos | P_baja mínima KALINA [kPa] | η mínima KALINA [%] | Fuera de rango en la mínima KALINA | D mínimo |
|---|---|---|---|---|---|---|---|---|---|
| A | ε_HRVG | 0.75 | 12 | 0 | 0 | — | — | — | 5.773 |
| A | ε_HRVG | 0.78 | 12 | 0 | 0 | — | — | — | 6.686 |
| A | ε_HRVG | 0.81 | 12 | 0 | 0 | — | — | — | 7.609 |
| B | T_fuente | 380 | 0 | 0 | 12 | — | — | — | 7.172 |
| B | T_fuente | 390 | 20 | 17 | 0 | 445.455 | 2.446 | no | 0 |
| B | T_fuente | 403 | 20 | 16 | 0 | 563.636 | 8.482 | no | 0 |
| B | T_fuente | 420 | 20 | 15 | 0 | 736.364 | 9.15 | no | 0 |
| B | T_fuente | 434 | 21 | 11 | 0 | 945.455 | 8.234 | sí | 0 |
| B | T_fuente | 466 | 12 | 0 | 0 | — | — | — | 1.172 |
| B | T_fuente | 497 | 12 | 0 | 0 | — | — | — | 5.068 |
| B | T_fuente | 529 | 12 | 0 | 0 | — | — | — | 6.051 |
| B | T_fuente | 560 | 12 | 0 | 0 | — | — | — | 6.975 |

*Tabla 2.2-3 · hoja «2.2-3 Resumen de la malla de do» · 12 filas.*

Columnas:
- **Ruta.** A = conserva la fuente del profesor (ε_HRVG × P_baja); B = baja la fuente (T_fuente × P_baja).
- **Variable 1.** Primera variable movida en la fila.
- **Valor 1.** Valor de la primera variable.
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **KALINA.** Puntos que cumplen todos los criterios.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **P_baja mínima KALINA [kPa].** Menor P_baja con la que el punto es KALINA.
- **η mínima KALINA [%].** η del punto KALINA de P_baja mínima (no es la menor η de la fila).
- **Fuera de rango en la mínima KALINA.** Si el punto de P_baja mínima está fuera del rango validado.
- **P_baja mínima con O2 [kPa].** Menor P_baja con margen de cavitación O2 ≥ 0 (por bisección).
- **D mínimo.** Menor índice de cercanía D de la fila (0 = cumple todos los criterios operativos).
- **P_baja del mejor D [kPa].** P_baja en la que D es mínimo.
- **Criterios bloqueantes frecuentes.** Códigos de restricción que más fallan entre los puntos de la fila, con su conteo entre paréntesis (ver el glosario de códigos).

*Lectura:* la **ruta A** tiene 0 KALINA en sus tres filas. En la **ruta B**, hay KALINA solo con T_fuente de
390, 403, 420 y 434 K; con 380 K no converge y con 466 K o más no hay KALINA. La P_baja mínima crece al
subir la fuente (445.5 → 945.5 kPa) y η no es monótona (2.45 % en 390 K; 9.15 % en 420 K). Los 11 KALINA
fuera de rango están todos en 434 K.

**Tablas 2.1-1 y 2.2-1 — Condiciones.** Qué quedó fijo y qué se barrió.

### Figuras

**Figura 2.1-1 (10 paneles).**

> **Figura 2.1-1. Con un solo cambio sobre los datos del profesor hay 0 KALINA.**
> Estudio 2.1. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Punto base (las demás variables quedan fijas en): T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [340–623.15] K (22 valores); T_sumidero [283.15–303.55] K (10 valores); P_alta [1000–10000] kPa (24 valores); P_baja [150–1500] kPa (10 valores); x_b [0.3–0.9] (14 valores); η_t [0.75–0.9] (10 valores); η_p [0.65–0.85] (10 valores); ε_HRVG [0.75–0.85] (12 valores); ε_reg [0.75–0.85] (10 valores); ε_cond [0.75–0.85] (10 valores).
> Filtro: estudio 2.1 (2.1), barrido de una variable a la vez.
> n = 132. Fuente: todos_los_puntos.csv.

*Cómo se lee:* un panel por variable. El eje horizontal es el valor de la variable. El vertical **no es η**:
es la *fila de la clase* (KALINA arriba; no convergió y falso convergido abajo), porque en la mayoría de los
barridos no hay η que graficar. Cada punto tiene forma y color según su clase; un marcador hueco indica
fuera de rango. Un panel casi vacío arriba significa que casi nada llega a ser KALINA.

**Figura 2.2-1 (ruta A) y Figura 2.2-2 (ruta B).**

> **Figura 2.2-1. Ruta A: conservando la fuente del profesor (623 K), 0 KALINA.**
> Estudio 2.2 · parte(s) 2.2a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
> Datos barridos: P_baja [400–2000] kPa (12 valores); ε_HRVG [0.75–0.81] (3 valores).
> Filtro: parte 2.2a (2.2a).
> n = 36. Fuente: todos_los_puntos.csv.

> **Figura 2.2-2. Ruta B: KALINA con T_fuente entre 390 y 434 K.**
> Estudio 2.2 · parte(s) 2.2b. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
> Datos barridos: T_fuente [380–560] K (9 valores); P_baja [400–2000] kPa (32 valores).
> Filtro: parte 2.2b (2.2b).
> n = 144. Fuente: todos_los_puntos.csv.

*Cómo se leen:* dispersión de P_baja (horizontal) contra la variable movida (vertical: ε_HRVG en 2.2-1,
T_fuente en 2.2-2); color y forma según la clase. En 2.2-1 no hay ningún marcador verde; en 2.2-2, los
verdes aparecen en franjas de T_fuente de 390 a 434 K.

### Dónde verlo en el Excel
`2.1-1`, `2.1-2`, `2.1-3`, `2.1-R`, `2.2-1`, `2.2-2`, `2.2-3`, `2.2-R` y la hoja `2 Gráficos` (las figuras
están además a la derecha de sus bloques en las hojas `-R`).

### Qué dice y qué no dice
- **Dice:** un cambio no basta; el más cercano es bajar T_fuente a ~400 K; el bloqueo dominante es O2; dos
  cambios (fuente + P_baja) sí dan KALINA; con la fuente del profesor, ninguno en este rango de η/ε.
- **Cómo se eligió A\*:** entre el KALINA de mayor η (420 K, 736 kPa, 9.15 %) y el más parecido al profesor
  (390 K), se tomó la opción intermedia: **T_fuente = 403 K y P_baja = 563.64 kPa**. Es una **decisión de
  diseño**, no un óptimo.
- **Límites:** malla de 10 valores (paso 1/9 del rango) en 2.1 y de 145 kPa en P_baja de 2.2: una zona KALINA
  más angosta podría no verse. Las fronteras de 2.1 se refinaron sobre la bandera del solver, no sobre la
  clase. Con el motor real a 300 s, A\* sale NO_CONVERGIO por límite de tiempo; con 1500 s coincide (η 8.48 %).
- **Corrección registrada:** el reporte original atribuía el bloqueo de 2.1 a «C3», lo que venía de contar los
  21 falsos convergidos como convergidos.

> **Cómo explicarlo (30 s):** *«Probé cambiar una variable del profesor a la vez: ninguna da un ciclo
> válido. Bajar la fuente a unos 400 K es lo que más acerca, pero falla la cavitación por 2 K. Con dos
> cambios —fuente a 403 K y P_baja a 564 kPa— sí funciona; ese es mi punto ancla.»*

---

## R3. Conservando la fuente de 623 K solo hay KALINA no confiables (salvo con presiones del profesor y fuente a 403 K)

**Pregunta:** si se abre el rango de eficiencias y efectividades a [0.40, 0.95], ¿se puede conservar la fuente
del profesor?

**Resultado:** aparecen KALINA con la fuente de 623 K (bajando mucho ε_HRVG y subiendo P_baja), pero **ninguno
es confiable**. El único KALINA confiable con las presiones exactas del profesor es el de T_fuente = 403 K y
ε_cond = 0.95 (η = 9.50 %).

### Qué se hizo (estudio 2.3)
Repetir 2.1 y 2.2 con η y ε en [0.40, 0.95] (el rango aceptado del proyecto; 2.1 y 2.2 usaron [0.75, 0.85]).
Mallas de 12 valores por variable (paso 0.05) más bisección. 225 corridas:

| Parte | Qué se mueve | Corridas |
|---|---|---|
| 2.3a | una variable a la vez | 80 |
| 2.3b | ε_HRVG (0.40–0.80) × ε_cond (0.40–0.95), P_baja = 400 kPa | 60 |
| 2.3c | ε_HRVG (0.40–0.70) × P_baja (400–2000 kPa) | 64 |
| 2.3d | T_fuente × ε_cond, con la P_baja del profesor | 21 |

### Tablas

**Tabla 2.3-2 — Corridas por clase.**

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.3a · un cambio | 80 | 0 | 24 | 0 | 0 | 24 | 0 | 52 | 4 | 28 |
| 2.3b · ε_HRVG × ε_cond | 60 | 0 | 48 | 0 | 0 | 48 | 0 | 12 | 0 | 48 |
| 2.3c · ε_HRVG × P_baja | 64 | 0 | 62 | 19 | 0 | 43 | 0 | 2 | 0 | 62 |
| 2.3d · T_fuente × ε_cond | 21 | 0 | 20 | 1 | 1 | 18 | 1 | 1 | 0 | 14 |

*Tabla 2.3-2 · hoja «2.3-2 Corridas por parte y por» · 4 filas.*

**Tabla 2.3-3 — Malla con η y ε en [0.40, 0.95].** Una fila por parte y valor de la variable 1.

| Parte | Variable 1 | Valor 1 | Variable 2 | Genuinos | KALINA | Falsos convergidos | d menor | η en el d menor [%] | η mayor [%] |
|---|---|---|---|---|---|---|---|---|---|
| n1 | ε_HRVG | — | — | 24 | 0 | 2 | — | — | — |
| n1 | ε_reg | — | — | 0 | 0 | 0 | — | — | — |
| n1 | ε_cond | — | — | 0 | 0 | 2 | — | — | — |
| n1 | η_t | — | — | 0 | 0 | 0 | — | — | — |
| n1 | η_p | — | — | 0 | 0 | 0 | — | — | — |
| n2a | ε_HRVG | 0.4 | ε_cond | 12 | 0 | 0 | — | — | — |
| n2a | ε_HRVG | 0.5 | ε_cond | 11 | 0 | 0 | — | — | — |
| n2a | ε_HRVG | 0.6 | ε_cond | 12 | 0 | 0 | — | — | — |
| n2a | ε_HRVG | 0.7 | ε_cond | 9 | 0 | 0 | — | — | — |
| n2a | ε_HRVG | 0.8 | ε_cond | 4 | 0 | 0 | — | — | — |
| n2b | ε_HRVG | 0.4 | P_baja | 16 | 8 | 0 | 1.498 | 6.271 | 6.271 |
| n2b | ε_HRVG | 0.5 | P_baja | 14 | 5 | 0 | 1.626 | 4.337 | 4.337 |
| n2b | ε_HRVG | 0.6 | P_baja | 12 | 0 | 0 | — | — | — |
| n2b | ε_HRVG | 0.7 | P_baja | 12 | 0 | 0 | — | — | — |
| n3 | T_fuente | 403 | ε_cond | 3 | 1 | 0 | 1.05 | 9.505 | 9.505 |
| n3 | T_fuente | 420 | ε_cond | 3 | 0 | 0 | — | — | — |
| n3 | T_fuente | 434 | ε_cond | 3 | 0 | 0 | — | — | — |
| n3 | T_fuente | 466 | ε_cond | 3 | 0 | 0 | — | — | — |
| n3 | T_fuente | 497 | ε_cond | 2 | 0 | 0 | — | — | — |
| n3 | T_fuente | 529 | ε_cond | 3 | 0 | 0 | — | — | — |
| n3 | T_fuente | 560 | ε_cond | 3 | 0 | 0 | — | — | — |

*Tabla 2.3-3 · hoja «2.3-3 Malla con η y ε en 0.40,» · 21 filas.*

> **Atención:** esta tabla usa los códigos antiguos de parte: **n1 = 2.3a, n2a = 2.3b, n2b = 2.3c,
> n3 = 2.3d.**

Columnas:
- **Parte.** Subconjunto del estudio con sus propios datos fijos (p. ej. 2.4a). Solo se comparan puntos de la misma parte.
- **Variable 1.** Primera variable movida en la fila.
- **Valor 1.** Valor de la primera variable.
- **Variable 2.** Segunda variable movida en la fila.
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **KALINA.** Puntos que cumplen todos los criterios.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **d menor.** Menor distancia d al profesor entre los KALINA de la fila.
- **Valor 1 del d menor.** Valor de la variable 1 en el KALINA más cercano al profesor.
- **Valor 2 del d menor.** Valor de la variable 2 en el KALINA más cercano al profesor.
- **η en el d menor [%].** η de ese punto.
- **η mayor [%].** Mayor η entre los KALINA de la fila.
- **Valor 1 de la η mayor.** Valor de la variable 1 en el KALINA de mayor η.
- **Valor 2 de la η mayor.** Valor de la variable 2 en el KALINA de mayor η.
- **Bloqueantes.** Criterios que fallan entre los genuinos de la fila, con su conteo.

*Lectura:*
- **2.3a (n1)** y **2.3b (n2a):** 0 KALINA; 2.3b son 48 corregibles, todos por O2.
- **2.3c (n2b):** ε_HRVG = 0.40 con P_baja 1318 kPa → KALINA con η = 6.27 %; ε_HRVG = 0.50 con P_baja 1736 kPa
  → η = 4.34 %. Todos fuera de rango.
- **2.3d (n3):** T_fuente = 403 K con ε_cond = 0.95 → KALINA con η = 9.5 %, confiable.

### Figuras

> **Figura 2.3-1. Parte 2.3a: 0 KALINA con η y ε en [0.40, 0.95].**
> Estudio 2.3 · parte(s) 2.3a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: η_t [0.4–0.95] (12 valores); η_p [0.4–0.95] (12 valores); ε_HRVG [0.4–0.95] (32 valores); ε_reg [0.4–0.95] (12 valores); ε_cond [0.4–0.95] (12 valores).
> Filtro: parte 2.3a (2.3a).
> n = 80. Fuente: todos_los_puntos.csv.

> **Figura 2.3-2. Parte 2.3b: 0 KALINA con η y ε en [0.40, 0.95].**
> Estudio 2.3 · parte(s) 2.3b. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; motor de propiedades = teqp.
> Datos barridos: ε_HRVG [0.4–0.8] (5 valores); ε_cond [0.4–0.95] (12 valores).
> Filtro: parte 2.3b (2.3b).
> n = 60. Fuente: todos_los_puntos.csv.

> **Figura 2.3-3. Parte 2.3c: 19 KALINA con η y ε en [0.40, 0.95].**
> Estudio 2.3 · parte(s) 2.3c. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
> Datos barridos: P_baja [400–2000] kPa (20 valores); ε_HRVG [0.4–0.7] (4 valores).
> Filtro: parte 2.3c (2.3c).
> n = 64. Fuente: todos_los_puntos.csv.

> **Figura 2.3-4. Parte 2.3d: 1 KALINA con η y ε en [0.40, 0.95].**
> Estudio 2.3 · parte(s) 2.3d. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.
> Datos barridos: T_fuente [403–560] K (7 valores); ε_cond [0.85–0.95] (3 valores).
> Filtro: parte 2.3d (2.3d).
> n = 21. Fuente: todos_los_puntos.csv.

*Cómo se leen:* 2.3-1 es la tira de clases por variable (como 2.1-1) con η/ε en el rango ampliado. 2.3-2,
2.3-3 y 2.3-4 son dispersiones de las dos variables movidas en cada parte (eje horizontal = variable 2; eje
vertical = variable 1), con color y forma según la clase.

### Dónde verlo en el Excel
`2.3-1`, `2.3-2`, `2.3-3`, `2.3-R` y `2 Gráficos`.

### Qué dice y qué no dice
- **Dice:** la fuente de 623 K puede dar KALINA solo con equipos muy degradados y presión alta, y esos puntos
  quedan fuera del rango validado. Con las presiones exactas del profesor, bajar la fuente a 403 K y subir
  ε_cond a 0.95 funciona.
- **Límites:** 13 de los 14 KALINA distintos están fuera de rango; paso de 0.05 en η/ε; 4 puntos N2
  descartados. La tabla completa tiene 20 filas KALINA porque malla y bisección repiten puntos.
- **Qué no presentar:** la ruta «ε_HRVG = 0.40 con la fuente de 623 K» no es un diseño.

> **Cómo explicarlo (30 s):** *«Aun abriendo el rango de eficiencias, conservar la fuente de 623 K solo da
> ciclos con equipos muy malos y fuera del rango validado. Lo que sí funciona es mantener las presiones del
> profesor, bajar la fuente a 403 K y un condensador muy efectivo.»*

---

## R4. Lo que decide que el ciclo sea KALINA: P_baja, ε_cond y la razón de presiones

**Pregunta:** ¿qué variables deciden si un punto es KALINA?

**Resultado:** **P_baja y ε_cond (KS = 0.43 cada una)**, luego **r_P (0.35)** y T_fuente (0.29). Las
eficiencias de las máquinas casi no deciden (KS ≤ 0.12).

### Qué se hizo (estudio 3.2 y, para P_baja alta, estudio 3.3)
**Muestreo:** LHS de 500 puntos (300 + 200) dentro de una caja realista, sin punto base:

| Parte | Variable | Estado | Valor o rango | n valores | ¿Igual al profesor? | Unidad |
|---|---|---|---|---|---|---|
| 3.2 | Temperatura de la fuente, T_fuente [K] | Barrida | 380.2 – 499.9 | 300 | — | K |
| 3.2 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.2 – 303.5 | 300 | — | K |
| 3.2 | Presión de alta, P_alta [kPa] | Barrida | 2005 – 4991 | 300 | — | kPa |
| 3.2 | Presión de baja, P_baja [kPa] | Barrida | 302.9 – 1498 | 300 | — | kPa |
| 3.2 | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida | 0.500 – 0.850 | 300 | — | – |
| 3.2 | Flujo másico base, m_b [kg/s] | Fija | 1.0 | — | sí | kg/s |
| 3.2 | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.750 – 0.920 | 300 | — | – |
| 3.2 | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.650 – 0.899 | 300 | — | – |
| 3.2 | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.600 – 0.949 | 300 | — | – |
| 3.2 | Efectividad del regenerador, ε_reg [–] | Barrida | 0.601 – 0.950 | 300 | — | – |
| 3.2 | Efectividad del condensador, ε_cond [–] | Barrida | 0.700 – 0.949 | 300 | — | – |
| 3.2 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.2 – 303.5 | 300 | — | K |
| 3.2 | motor de propiedades | Fija | teqp | — | — | – |
| 3.2 | Temperatura de la fuente, T_fuente [K] | Barrida | 380.3 – 499.5 | 200 | — | K |
| 3.2 | Temperatura del sumidero, T_sumidero [K] | Barrida | 278.2 – 303.5 | 200 | — | K |
| 3.2 | Presión de alta, P_alta [kPa] | Barrida | 2010 – 4987 | 200 | — | kPa |
| 3.2 | Presión de baja, P_baja [kPa] | Barrida | 304.7 – 1497 | 200 | — | kPa |
| 3.2 | Fracción de amoníaco de la mezcla base, x_b [–] | Barrida | 0.500 – 0.849 | 200 | — | – |
| 3.2 | Flujo másico base, m_b [kg/s] | Fija | 1.0 | — | sí | kg/s |
| 3.2 | Eficiencia isentrópica de la turbina, η_t [–] | Barrida | 0.750 – 0.920 | 200 | — | – |
| 3.2 | Eficiencia isentrópica de la bomba, η_p [–] | Barrida | 0.651 – 0.899 | 200 | — | – |
| 3.2 | Efectividad del generador de vapor, ε_HRVG [–] | Barrida | 0.601 – 0.948 | 200 | — | – |
| 3.2 | Efectividad del regenerador, ε_reg [–] | Barrida | 0.602 – 0.949 | 200 | — | – |
| 3.2 | Efectividad del condensador, ε_cond [–] | Barrida | 0.701 – 0.949 | 200 | — | – |
| 3.2 | Piso de O2 (T de diseño de la bomba) [K] | Barrida | 278.2 – 303.5 | 200 | — | K |
| 3.2 | motor de propiedades | Fija | teqp | — | — | – |

*Tabla 3.2-1 · hoja «3.2-1 Condiciones qué quedó fij» · 26 filas.*

*Nota:* los 500 puntos son la unión de dos LHS (una muestra de 300 y otra de 200); cada mitad es un LHS
estricto, la unión no.

**Resultado del muestreo:** 452 genuinas, **121 KALINA (83 confiables)**, 222 fuera de rango.

**Análisis sobre el mismo muestreo:** RSA/KS (con intervalos bootstrap), PRCC, PAWN, árbol CART y prueba de
convergencia. **Estudio 3.3:** 150 puntos con la misma caja salvo P_baja en 1500–2500 kPa (15 omitidos).

### Tablas

**Tabla 3.2-2 — Corridas por parte y clase.**

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.2 | 300 | 0 | 266 | 76 | 57 | 181 | 9 | 27 | 7 | 128 |
| 3.2 | 200 | 0 | 186 | 45 | 26 | 127 | 14 | 8 | 6 | 94 |

*Tabla 3.2-2 · hoja «3.2-2 Corridas por parte y por» · 2 filas.*

**Tabla 3.2-3 — Separación KALINA / no KALINA (RSA y KS).** 52 filas: 4 separaciones × 13 variables (las 10
de entrada más ΔP, r_P y ΔT_fs). La separación «KALINA»:

| Separación | Variable | n en B (KALINA) | n en B̄ (no KALINA) | n excluidos | KS | Valor p | IC inferior | IC superior | Rango favorable, p05 | Rango favorable, p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| KALINA | T_fuente | 121 | 379 | 0 | 0.287 | < 0.001 | 0.207 | 0.388 | 383.658 | 486.22 |
| KALINA | T_sumidero | 121 | 379 | 0 | 0.2 | 0.001 | 0.136 | 0.312 | 278.969 | 301.676 |
| KALINA | P_alta | 121 | 379 | 0 | 0.13 | 0.08 | 0.08 | 0.231 | 2155.689 | 4841.777 |
| KALINA | P_baja | 121 | 379 | 0 | 0.427 | < 0.001 | 0.365 | 0.519 | 683.165 | 1460.713 |
| KALINA | x_b | 121 | 379 | 0 | 0.193 | 0.002 | 0.142 | 0.301 | 0.514 | 0.817 |
| KALINA | η_t | 121 | 379 | 0 | 0.085 | 0.485 | 0.06 | 0.197 | 0.758 | 0.91 |
| KALINA | η_p | 121 | 379 | 0 | 0.095 | 0.349 | 0.069 | 0.206 | 0.663 | 0.887 |
| KALINA | ε_HRVG | 121 | 379 | 0 | 0.074 | 0.665 | 0.061 | 0.185 | 0.617 | 0.93 |
| KALINA | ε_reg | 121 | 379 | 0 | 0.122 | 0.12 | 0.074 | 0.225 | 0.624 | 0.933 |
| KALINA | ε_cond | 121 | 379 | 0 | 0.426 | < 0.001 | 0.353 | 0.524 | 0.74 | 0.946 |
| KALINA | dP | 121 | 379 | 0 | 0.138 | 0.053 | 0.107 | 0.242 | 968.027 | 3717.631 |
| KALINA | rP | 121 | 379 | 0 | 0.353 | < 0.001 | 0.299 | 0.446 | 1.686 | 5.339 |
| KALINA | dT_fs | 121 | 379 | 0 | 0.248 | < 0.001 | 0.173 | 0.343 | 91.385 | 199.35 |

*Tabla 3.2-3 · hoja «3.2-3 Separación KALINA  no KAL» · 13 filas.*

Columnas:
- **Separación.** Cómo se partió la muestra en dos grupos: «KALINA» (KALINA contra el resto), «converge», «cumple_O2» o «cumple_O1».
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **n en B (KALINA).** Puntos del grupo que cumple (B).
- **n en B̄ (no KALINA).** Puntos del grupo que no cumple (B̄), incluidos los que no convergieron.
- **n excluidos.** Puntos que no entran en la comparación de esa variable.
- **KS.** Estadístico de Kolmogorov–Smirnov: máxima separación entre las dos curvas acumuladas (0 = iguales, 1 = totalmente distintas).
- **Valor p.** Probabilidad de ver esa separación por azar (prueba KS de dos muestras).
- **IC inferior.** Límite inferior del intervalo de confianza al 95 % (bootstrap de 1000 remuestreos).
- **IC superior.** Límite superior del intervalo de confianza al 95 %.
- **Rango favorable, p05.** Percentil 5 de la variable dentro del grupo que cumple: extremo inferior de «donde viven» los KALINA.
- **Rango favorable, p95.** Percentil 95: extremo superior del rango favorable.

*Lectura:* ordenando por KS: **P_baja 0.427, ε_cond 0.426, r_P 0.353, T_fuente 0.287, ΔT_fs 0.248,
T_sumidero 0.200, x_b 0.193**; las demás, menores de 0.14 (P_alta 0.130, p = 0.08; η_t, η_p, ε_HRVG y ε_reg,
no significativas). Los intervalos de P_baja (0.365–0.519) y ε_cond (0.353–0.524) **se solapan casi por
completo**: no se puede afirmar cuál de las dos pesa más.

Las otras tres separaciones de la misma tabla (`converge`, `cumple_O2`, `cumple_O1`) dicen *qué variable
controla cada barrera*, no solo la clase final.

**Tabla 3.2-5 — Rangos de presión de los KALINA.** Para P_alta, P_baja, ΔP y r_P: mínimo, percentil 5,
mediana, percentil 95 y máximo de los KALINA y de los no KALINA genuinos.

| Variable | Grupo | N | Mínimo | Percentil 5 | Mediana | Percentil 95 | Máximo | KS | Valor p |
|---|---|---|---|---|---|---|---|---|---|
| P_alta | KALINA | 121 | 2005.395 | 2155.689 | 3571.407 | 4841.777 | 4960.892 | 0.149 | 0.035 |
| P_alta | no_KALINA_genuino | 331 | 2009.945 | 2135.216 | 3365.236 | 4818.999 | 4991.234 | 0.149 | 0.035 |
| P_baja | KALINA | 121 | 546.972 | 683.165 | 1182.621 | 1460.713 | 1493.2 | 0.437 | < 0.001 |
| P_baja | no_KALINA_genuino | 331 | 302.949 | 349.325 | 767.043 | 1416.741 | 1497.997 | 0.437 | < 0.001 |
| dP | KALINA | 121 | 710.238 | 968.027 | 2463.669 | 3717.631 | 4117.11 | 0.1 | 0.311 |
| dP | no_KALINA_genuino | 331 | 654.761 | 1142.674 | 2575.19 | 4089.495 | 4589.512 | 0.1 | 0.311 |
| rP | KALINA | 121 | 1.548 | 1.686 | 3.111 | 5.339 | 8.376 | 0.347 | < 0.001 |
| rP | no_KALINA_genuino | 331 | 1.483 | 1.958 | 4.31 | 10.08 | 14.433 | 0.347 | < 0.001 |

*Tabla 3.2-5 · hoja «3.2-5 Rangos de presión de los» · 8 filas.*

Columnas:
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Grupo.** Grupo comparado: KALINA o no KALINA genuino.
- **N.** Cantidad de puntos usados (n).
- **Mínimo.** Menor valor del grupo.
- **Percentil 5.** Valor bajo el cual queda el 5 % del grupo.
- **Mediana.** Valor central del grupo.
- **Percentil 95.** Valor bajo el cual queda el 95 % del grupo.
- **Máximo.** Mayor valor del grupo.
- **KS.** Estadístico de Kolmogorov–Smirnov: máxima separación entre las dos curvas acumuladas (0 = iguales, 1 = totalmente distintas).
- **Valor p.** Probabilidad de ver esa separación por azar (prueba KS de dos muestras).

*Lectura:* los KALINA tienen P_baja 683–1461 kPa (p5–p95) contra una mediana de 767 kPa de los no KALINA;
r_P entre 1.69 y 5.34. Es decir, **el 90 % de los KALINA vive con r_P entre 1.7 y 5.3**.

**Tablas 3.2-6, 3.2-7 y 3.2-8 — Ventana KALINA por franjas** de P_alta, T_fuente y T_sumidero. La de P_alta:

| Variable | Franja | Límite inferior | Límite superior | N | KALINA | KALINA [%] | P_baja mínima [kPa] | P_baja máxima [kPa] | ΔP mínima [kPa] | ΔP máxima [kPa] | r_P mínima [–] | r_P máxima [–] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P_alta | 1 | 2000 | 2500 | 83 | 18 | 21.7 | 912.814 | 1459.364 | 710.238 | 1413.88 | 1.548 | 2.348 |
| P_alta | 2 | 2500 | 3000 | 83 | 16 | 19.3 | 683.165 | 1440.71 | 1122.632 | 2184.142 | 1.779 | 4.197 |
| P_alta | 3 | 3000 | 3500 | 84 | 21 | 25 | 607.329 | 1416.578 | 1868.606 | 2673.483 | 2.319 | 5.291 |
| P_alta | 4 | 3500 | 4000 | 83 | 29 | 34.9 | 546.972 | 1479.809 | 2217.957 | 3071.417 | 2.508 | 6.485 |
| P_alta | 5 | 4000 | 4500 | 84 | 18 | 21.4 | 634.297 | 1493.2 | 2550.325 | 3764.413 | 2.746 | 6.935 |
| P_alta | 6 | 4500 | 5000 | 83 | 19 | 22.9 | 558.165 | 1464.867 | 3208.354 | 4117.11 | 3.21 | 8.376 |

*Tabla 3.2-6 · hoja «3.2-6 Ventana KALINA por franja» · 6 filas.*

Columnas:
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Franja.** Intervalo de la variable en que se agrupan los puntos (número de franja o rango en kPa).
- **Límite inferior.** Extremo inferior de la franja.
- **Límite superior.** Extremo superior de la franja.
- **N.** Cantidad de puntos usados (n).
- **KALINA.** Puntos que cumplen todos los criterios.
- **KALINA [%].** Porcentaje de los puntos de la franja que son KALINA.
- **P_baja mínima [kPa].** Menor P_baja de los KALINA de la franja.
- **P_baja máxima [kPa].** Mayor P_baja de los KALINA de la franja.
- **ΔP mínima [kPa].** Menor ΔP = P_alta − P_baja entre los KALINA de la franja.
- **ΔP máxima [kPa].** Mayor ΔP entre los KALINA de la franja.
- **r_P mínima [–].** Menor razón de presiones r_P = P_alta / P_baja entre los KALINA de la franja.
- **r_P máxima [–].** Mayor r_P entre los KALINA de la franja.

*Lectura (interacción):* la P_baja mínima KALINA baja de 913 kPa (franja 2000–2500 de P_alta) a 547 kPa
(franja 3500–4000) y deja de bajar después. Por eso P_alta, sola, no es significativa (KS = 0.13) pero r_P
sí.

**Tabla 3.3-3 — Techo de P_baja antes de cortar KALINA** (franjas de 100 kPa de P_baja; las dos primeras
vienen de 3.2, el resto de 3.3):

| Fuente | Franja | Límite inferior | Límite superior | N | KALINA | KALINA [%] | P_baja máxima KALINA [kPa] |
|---|---|---|---|---|---|---|---|
| estudio 3.2+estudio 3.2 | 1300–1400 | 1300 | 1400 | 42 | 15 | 35.7 | 1384.325 |
| estudio 3.2+estudio 3.2 | 1400–1500 | 1400 | 1500 | 42 | 21 | 50 | 1493.2 |
| estudio 3.3 | 1500–1600 | 1500 | 1600 | 15 | 5 | 33.3 | 1593.045 |
| estudio 3.3 | 1600–1700 | 1600 | 1700 | 15 | 8 | 53.3 | 1655.513 |
| estudio 3.3 | 1700–1800 | 1700 | 1800 | 14 | 7 | 50 | 1759.83 |
| estudio 3.3 | 1800–1900 | 1800 | 1900 | 15 | 10 | 66.7 | 1896.95 |
| estudio 3.3 | 1900–2000 | 1900 | 2000 | 13 | 9 | 69.2 | 1981.397 |
| estudio 3.3 | 2000–2100 | 2000 | 2100 | 13 | 8 | 61.5 | 2096.182 |
| estudio 3.3 | 2100–2200 | 2100 | 2200 | 14 | 7 | 50 | 2198.694 |
| estudio 3.3 | 2200–2300 | 2200 | 2300 | 14 | 5 | 35.7 | 2292.552 |
| estudio 3.3 | 2300–2400 | 2300 | 2400 | 10 | 7 | 70 | 2388.226 |
| estudio 3.3 | 2400–2500 | 2400 | 2500 | 12 | 9 | 75 | 2494.529 |

*Tabla 3.3-3 · hoja «3.3-3 Techo de P_baja antes de» · 12 filas.*

**Tabla 3.3-4 — Techo de P_baja por franja de P_alta:**

| Franja | Límite inferior | Límite superior | N | KALINA | KALINA [%] | P_baja máxima KALINA [kPa] |
|---|---|---|---|---|---|---|
| 2000–2500 | 2000 | 2500 | 94 | 23 | 24.5 | 1921.427 |
| 2500–3000 | 2500 | 3000 | 107 | 29 | 27.1 | 2423.019 |
| 3000–3500 | 3000 | 3500 | 109 | 34 | 31.2 | 2479.359 |
| 3500–4000 | 3500 | 4000 | 108 | 43 | 39.8 | 2494.529 |
| 4000–4500 | 4000 | 4500 | 109 | 32 | 29.4 | 2418.817 |
| 4500–5000 | 4500 | 5000 | 108 | 35 | 32.4 | 2482.357 |

*Tabla 3.3-4 · hoja «3.3-4 Techo de P_baja por franj» · 6 filas.*

*Lectura:* hay KALINA en **todas** las franjas hasta 2500 kPa, entre 33 y 75 % de los evaluados; el KALINA de
mayor P_baja tiene 2494.5 kPa. No hay un techo de clasificación.

**Tabla 3.2-4 — filas de margen.** Además del PRCC sobre η (ver R5), la tabla trae el PRCC sobre el margen
de cavitación m_O2, que **explica el mecanismo**: P_baja +0.76, ε_cond +0.73, T_fuente −0.68, T_sumidero
−0.54, x_b −0.47 (n = 452); las eficiencias de turbina y bomba no lo mueven (|PRCC| < 0.05, p > 0.4).

| Salida | Variable | N | PRCC | t de Student | Valor p | IC inferior | IC superior |
|---|---|---|---|---|---|---|---|
| m_O2 | T_fuente | 452 | -0.68 | -19.455 | < 0.001 | -0.748 | -0.611 |
| m_O2 | T_sumidero | 452 | -0.537 | -13.36 | < 0.001 | -0.616 | -0.458 |
| m_O2 | P_alta | 452 | 0.263 | 5.726 | < 0.001 | 0.173 | 0.353 |
| m_O2 | P_baja | 452 | 0.757 | 24.347 | < 0.001 | 0.696 | 0.818 |
| m_O2 | x_b | 452 | -0.47 | -11.192 | < 0.001 | -0.553 | -0.388 |
| m_O2 | η_t | 452 | -0.01 | -0.202 | 0.84 | -0.103 | 0.084 |
| m_O2 | η_p | 452 | 0.04 | 0.837 | 0.403 | -0.054 | 0.133 |
| m_O2 | ε_HRVG | 452 | -0.268 | -5.83 | < 0.001 | -0.358 | -0.177 |
| m_O2 | ε_reg | 452 | -0.041 | -0.853 | 0.394 | -0.134 | 0.053 |
| m_O2 | ε_cond | 452 | 0.732 | 22.574 | < 0.001 | 0.668 | 0.796 |

*Tabla 3.2-4 · hoja «3.2-4 Influencia de cada variab» · 10 filas.*

*Lectura del mecanismo:* subir P_baja eleva la temperatura de burbuja; un condensador más efectivo enfría
más el líquido; una fuente más caliente, un sumidero más caliente o más amoníaco empujan el líquido hacia la
saturación.

### Figuras

**Figura 3.2-1 — curvas acumuladas por variable (10 paneles).**

> **Figura 3.2-1. Qué variables separan a los KALINA del resto (LHS de 500 puntos).**
> Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
> Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
> Filtro: estudio 3.2: 452 genuinos y 48 sin resultado (no convergió o falso convergido).
> n = 500. Fuente: todos_los_puntos.csv.

*Cómo se lee:* un panel por variable. Curva verde = distribución de los KALINA; gris punteada = resto
genuino; roja punteada = puntos sin resultado (no convergió o falso convergido). **Cuanto más separadas
estén la verde y la gris, más decide la variable.** El KS de cada panel está escrito arriba a la izquierda.
En P_baja y ε_cond la curva verde va claramente a la derecha de la gris: los KALINA tienen valores más altos.

**Figura 3.2-2 — plano de presiones.**

> **Figura 3.2-2. El 90 % de los KALINA tiene razón de presiones entre 1.7 y 5.3.**
> Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
> Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
> Filtro: estudio 3.2.
> n = 500. Fuente: todos_los_puntos.csv.

*Cómo se lee:* P_alta (horizontal) contra P_baja (vertical), un punto por corrida, color y forma por clase.
Las dos rectas punteadas son r_P en el percentil 5 y 95 de los KALINA: **entre las dos rectas está el 90 % de
los KALINA**.

**Figura 3.2-4 — histogramas de ΔP y r_P.**

> **Figura 3.2-4. El 90 % de los KALINA tiene ΔP 968–3718 kPa y r_P 1.7–5.3.**
> Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
> Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
> Filtro: estudio 3.2: 452 genuinos y 48 sin resultado.
> n = 500. Fuente: todos_los_puntos.csv.

*Cómo se lee:* a la izquierda, ΔP; a la derecha, r_P. Barras verdes = KALINA, grises = resto genuino, rojas =
sin resultado, con los mismos intervalos. Los KALINA se concentran a la izquierda en r_P: la cola larga a la
derecha es de no KALINA.

**Figura 3.3-1 — % de KALINA por franja de P_baja (1500–2500 kPa).**

> **Figura 3.3-1. Fracción de KALINA al subir P_baja entre 1500 y 2500 kPa.**
> Estudio 3.3. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
> Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: T_fuente [380.75–499.83] K (150 valores); T_sumidero [278.28–303.41] K (150 valores); P_alta [2015.7–4995.8] kPa (150 valores); P_baja [1501.3–2494.5] kPa (150 valores); x_b [0.5023–0.84953] (150 valores); η_t [0.75103–0.91919] (150 valores); η_p [0.65119–0.89988] (150 valores); ε_HRVG [0.60089–0.94845] (150 valores); ε_reg [0.60038–0.9477] (150 valores); ε_cond [0.70004–0.94966] (150 valores); piso de O2 [278.28–303.41] K (135 valores).
> Filtro: estudio 3.3, puntos evaluados.
> n = 135. Fuente: todos_los_puntos.csv.

*Cómo se lee:* cada barra es una franja de 100 kPa; la altura es el porcentaje de KALINA. Ninguna barra cae
a cero: no hay techo.

### Dónde verlo en el Excel
`3.2-1` a `3.2-8`, `3.3-1` a `3.3-4`, `3.2-R`, `3.3-R`, y las hojas `3 Gráficos` y `3 Datos de gráficos`.

### Qué dice y qué no dice
- **Dice:** la factibilidad depende del lado frío (P_baja, ε_cond) y de la razón de presiones; es un **umbral de
  cavitación (O2)**. En el 88–100 % de los genuinos no KALINA falla O2 (Tabla S-5).
- **No dice:** cuál de P_baja o ε_cond pesa más (intervalos solapados); tampoco una regla de corte simple: el
  árbol CART clasifica 78.8 % contra 75.8 % de «nunca es KALINA». Sus cortes principales (ε_cond ≈ 0.89,
  P_baja ≈ 770–1025 kPa, T_fuente ≈ 416 K) son orientativos.
- **Robustez:** el ranking es estable entre 300 y 500 puntos (ρ de Spearman 0.93 en KS y 0.99 en PRCC) y PAWN
  da el mismo grupo líder.
- **Límites:** 222 de 500 puntos están fuera de rango; los rangos de presión se calcularon con todos los KALINA
  (121), no solo los confiables (83); es una caja: fuera de ella no se afirma nada; 150 puntos en 10
  dimensiones acotan el techo de 3.3 pero no lo calculan.

> **Cómo explicarlo (30 s):** *«De 500 puntos al azar dentro de una caja realista, 121 son KALINA. Lo que los
> separa del resto es la presión de baja y la efectividad del condensador; el 90 % vive con una razón de
> presiones entre 1.7 y 5.3. La razón de fondo es la cavitación: la bomba necesita líquido subenfriado.»*

---

## R5. Lo que mueve la eficiencia no es lo que decide la clase

**Pregunta:** entre los puntos que funcionan, ¿qué variables mueven η, y en qué sentido?

**Resultado:** η la mueven **P_baja (−0.68), P_alta (+0.58), η_t (+0.38)**, T_fuente (+0.29) y ε_reg (+0.27).
**ε_cond decide la clase pero casi no mueve η** (+0.08); P_alta, η_t y ε_reg mueven η pero no deciden la
clase. Solo P_baja está en los dos grupos, con signo opuesto.

### Qué se hizo
- **Global (estudio 3.2):** PRCC de cada variable sobre η, con los 430 puntos genuinos con W_net > 0.
- **Local (estudio 3.1):** OAT alrededor de A\*: 10 variables × 15 valores equiespaciados + A\* ± 1 % del rango
  (20 corridas) + el ancla = 171 corridas (teqp, 5 procesos, 5822 s; mediana de 153 s por punto). Rangos:

| Variable | Rango | Paso |
|---|---|---|
| T_fuente | 340 – 623.15 K | 20.22 K |
| T_sumidero | 283.15 – 303.55 K | 1.457 K |
| P_alta | 1000 – 10000 kPa | 642.9 kPa |
| P_baja | 150 – 1500 kPa | 96.43 kPa |
| x_b | 0.30 – 0.90 | 0.0429 |
| η_t, η_p, ε_HRVG, ε_reg, ε_cond | 0.40 – 0.95 | 0.0393 |

### Tablas

**Tabla 3.2-4 — Influencia de cada variable sobre η (PRCC).** Filas de la salida η:

| Salida | Variable | N | PRCC | t de Student | Valor p | IC inferior | IC superior |
|---|---|---|---|---|---|---|---|
| eta | T_fuente | 430 | 0.291 | 6.234 | < 0.001 | 0.199 | 0.383 |
| eta | T_sumidero | 430 | -0.041 | -0.848 | 0.397 | -0.137 | 0.055 |
| eta | P_alta | 430 | 0.583 | 14.694 | < 0.001 | 0.505 | 0.661 |
| eta | P_baja | 430 | -0.681 | -19.018 | < 0.001 | -0.751 | -0.61 |
| eta | x_b | 430 | 0.236 | 4.971 | < 0.001 | 0.143 | 0.329 |
| eta | η_t | 430 | 0.375 | 8.284 | < 0.001 | 0.286 | 0.464 |
| eta | η_p | 430 | 0.01 | 0.196 | 0.845 | -0.086 | 0.106 |
| eta | ε_HRVG | 430 | 0.008 | 0.168 | 0.867 | -0.088 | 0.104 |
| eta | ε_reg | 430 | 0.267 | 5.661 | < 0.001 | 0.174 | 0.359 |
| eta | ε_cond | 430 | 0.083 | 1.708 | 0.088 | -0.013 | 0.179 |

*Tabla 3.2-4 · hoja «3.2-4 Influencia de cada variab» · 10 filas.*

Columnas:
- **Salida.** Magnitud explicada: η, o el margen de un criterio (m_O1, m_O2, m_O5).
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **N.** Cantidad de puntos usados (n).
- **PRCC.** Coeficiente de correlación parcial de rangos, de −1 a +1: signo y fuerza del efecto de la variable sobre la salida, sin el efecto de las demás.
- **t de Student.** Estadístico con que se prueba que el PRCC no es cero.
- **Valor p.** Probabilidad de ver un PRCC así si no hubiera relación (prueba t); «< 0.001» = prácticamente cero.
- **IC inferior.** Límite inferior del intervalo de confianza al 95 % (bootstrap de 1000 remuestreos).
- **IC superior.** Límite superior del intervalo de confianza al 95 %.

*Lectura:* los PRCC significativos son P_baja −0.681, P_alta +0.583, η_t +0.375, T_fuente +0.291, ε_reg
+0.267 y x_b +0.236 (p < 0.001); ε_cond +0.083 tiene p = 0.088 (no significativo) y T_sumidero, η_p y ε_HRVG
son prácticamente cero.

**Tabla 3.1-3 — Influencia y margen por variable (Δη y O2).** Una fila por variable, ordenada por |E|.

| Variable | Rango explorado | Valor en A* | Elasticidad E en A* | Δη (genuinos) [pp] | η máx. KALINA en la malla [%] | Valor de esa η máx. | Zona KALINA | Criterios que bloquean | Distancia a la frontera de O2 [–] |
|---|---|---|---|---|---|---|---|---|---|
| Temperatura de la fuente, T_fuente [K] | 340.0 – 623.1 | 403 | 10.871 | 3.667 | 7.901 | 400.675 | 400.7 – 400.7 | O2(9) | 0.024 |
| Fracción de amoníaco de la mezcla base, x_b [–] | 0.300 – 0.900 | 0.5 | 3.402 | 10.775 | 6.424 | 0.471 | 0.471 – 0.471 | O2(9) · O3(3) | 0.018 |
| Temperatura del sumidero, T_sumidero [K] | 283.1 – 303.6 | 300 | 1.614 | 0.853 | 8.443 | 299.179 | 283.1 – 299.2 | O2(3) | 0.022 |
| Presión de alta, P_alta [kPa] | 1000 – 10000 | 3000 | -1.165 | 5.145 | 4.655 | 3571.429 | 3571 – 3571 | O2(4) | 0.007 |
| Eficiencia isentrópica de la turbina, η_t [–] | 0.400 – 0.950 | 0.85 | 1.146 | 6.315 | 9.625 | 0.95 | 0.675 – 0.950 | O2(7) | 0.343 |
| Efectividad del regenerador, ε_reg [–] | 0.400 – 0.950 | 0.75 | 0.86 | 4.991 | 10.956 | 0.95 | 0.754 – 0.950 | O2(9) | 0.057 |
| Efectividad del generador de vapor, ε_HRVG [–] | 0.400 – 0.950 | 0.85 | 0.644 | 6.691 | 8.365 | 0.832 | 0.400 – 0.832 | O2(3) · S3(1) | 0.039 |
| Presión de baja, P_baja [kPa] | 150.0 – 1500 | 563.6 | -0.581 | 6.801 | 7.912 | 632.143 | 632.1 – 1500 | O2(5) · O3(1) | 0.016 |
| Efectividad del condensador, ε_cond [–] | 0.400 – 0.950 | 0.8 | -0.406 | 0.821 | 8.349 | 0.832 | 0.832 – 0.950 | O2(7) | 0.012 |
| Eficiencia isentrópica de la bomba, η_p [–] | 0.400 – 0.950 | 0.75 | 0.149 | 1.378 | 8.748 | 0.95 | 0.400 – 0.950 | ninguno | — |

*Tabla 3.1-3 · hoja «3.1-3 Influencia y margen por v» · 10 filas.*

Columnas:
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Rango explorado.** Intervalo barrido de la variable.
- **Valor en A*.** Valor de la variable en el ancla.
- **Elasticidad E en A*.** E = (Δη/η) / (Δv/v) por diferencia central con ±1 % del rango.
- **Δη (genuinos) [pp].** η máxima − η mínima en la malla, solo con genuinos de W_net > 0.
- **η máx. KALINA en la malla [%].** Mayor η entre los KALINA de la malla de esa variable.
- **Valor de esa η máx..** Valor de la variable en ese punto.
- **Zona KALINA.** Tramo contiguo a A* donde la clase sigue siendo KALINA.
- **Criterios que bloquean.** Criterios que fallan fuera de la zona KALINA, con su conteo.
- **Distancia a la frontera de O2 [–].** |valor de cruce − valor en A*| / rango. Cuanto menor, más cerca de la frontera.

*Lectura:* T_fuente tiene la mayor elasticidad (E = 10.87) y x_b la mayor Δη (10.78 pp). Las palancas que
suben η sin perder KALINA son **ε_reg** (hasta 10.96 %) y **η_t** (hasta 9.62 %), ambas en 0.95. P_alta y x_b
mueven mucho η pero casi toda su malla cae fuera de KALINA.

**Tabla 3.1-2 — Corridas por clase.**

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.1 | 171 | 0 | 148 | 86 | 86 | 57 | 5 | 17 | 6 | 8 |

*Tabla 3.1-2 · hoja «3.1-2 Corridas por parte y por» · 1 filas.*

**Tabla 3.1-1 — Condiciones.** *Nota:* en «n valores» aparece 18, no 15: son los 15 valores de la malla, los
2 vecinos de A\* y el ancla.

### Figuras

**Figura 3.1-1 — tornado de Δη.**

> **Figura 3.1-1. Cerca de A*, x_b y P_baja son las que más mueven η en su rango.**
> Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
> Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
> Filtro: estudio 3.1, malla, puntos genuinos con W_net > 0.
> n = 123. Fuente: todos_los_puntos.csv.

*Cómo se lee:* una barra por variable, ordenadas por tamaño; la longitud es η máx − η mín al recorrer todo
el rango de esa variable con las demás en A\*. La barra más larga mueve más η.

**Figura 3.1-2 — elasticidades.**

> **Figura 3.1-2. Pegado a A*, T_fuente es la variable más sensible (E = 10.9).**
> Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
> Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
> Filtro: m3_resumen.csv (E_eta de la malla).
> n = 10. Fuente: resultados/2026-10-06_final_M3/m3_resumen.csv.

*Cómo se lee:* barra verde = subir la variable sube η; roja = la baja. La longitud es la elasticidad en A\*.
**Solo vale pegado a A\***: no se debe extrapolar.

**Figura 3.1-3 — η contra cada variable, una a la vez (10 paneles).**

> **Figura 3.1-3. Eficiencia según cada variable, una a la vez, alrededor de A*.**
> Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
> Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
> Filtro: estudio 3.1, malla y vecinos de A* (±1 % del rango).
> n = 170. Fuente: todos_los_puntos.csv.

*Cómo se lee:* un panel por variable. **Línea vertical punteada** = valor de la variable en A\*; **línea
horizontal punteada y banda verde** = η de A\* ± 0.7 pp (banda de incertidumbre); **✕ al fondo (η = −0.6)** =
punto sin η (no convergió o no genuino). Dibuja la malla y los 2 vecinos de A\*.

*Qué se ve:* ε_reg, η_t, ε_HRVG y η_p suben η casi en línea recta; T_fuente y x_b alternan entre no
convergió, KALINA y CORREGIBLE (no son monótonas); P_baja baja η al subir.

**Figura 3.2-3 — PRCC sobre η.**

> **Figura 3.2-3. Influencia de cada variable sobre η (PRCC, 430 puntos).**
> Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
> Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
> Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
> Filtro: m4b_prcc.csv (fila de salida = η).
> n = 430. Fuente: resultados/2026-10-07_final_M4b/m4b_prcc.csv.

*Cómo se lee:* barras horizontales con intervalo de confianza al 95 %; positivo sube η, negativo la baja.
Una barra cuyo intervalo cruza el cero (T_sumidero, η_p, ε_HRVG, ε_cond) no es distinguible de cero.

### Dónde verlo en el Excel
`3.1-1`, `3.1-2`, `3.1-3`, `3.1-R`, `3.2-4`, y `3 Gráficos` (28 gráficos de la pregunta 3).

### Qué dice y qué no dice
- **Dice:** primero se elige ε_cond y P_baja para ser KALINA; después se sube η con P_alta, η_t y ε_reg sin
  arriesgar la clase.
- **P_baja es antagónica:** subirla asegura KALINA pero baja η 0.40–0.55 pp por cada 100 kPa (en 2.4a,
  0.55 pp/100 kPa con R² = 0.98).
- **Local contra global:** ε_HRVG sube η con fuerza en A\* (+0.115 pp por 0.01) pero su PRCC global es ≈ 0:
  es un efecto que depende del punto.
- **Límites:** OAT no ve interacciones; las diferencias entre T_sumidero (0.85 pp), ε_cond (0.82) y η_p (1.38)
  quedan dentro de la banda de η y no son concluyentes entre sí; el Δη original del reporte (50.7 pp para
  P_baja) incluía puntos con W_net ≤ 0: no usarlo; la malla tiene paso de 1/14 del rango (una zona KALINA más
  angosta puede no verse; le pasa a T_fuente, x_b y P_alta).

> **Cómo explicarlo (30 s):** *«Hay dos preguntas distintas: qué hace que el ciclo funcione y qué lo hace
> más eficiente. Para que funcione mandan P_baja y el condensador. Para la eficiencia, P_alta, la turbina y
> el regenerador. La única que está en las dos es P_baja y con efectos contrarios.»*

---

## R6. La frontera de KALINA es un umbral y los diseños quedan pegados a ella

**Pregunta:** ¿cuánto margen tienen los diseños KALINA?

**Resultado:** casi ninguno. A\* está a menos del 6 % del rango de la frontera de O2 en **8 de 9 variables**
(en P_alta, a 0.7 %: bajarla 64 kPa rompe O2). Con el piso de O2 en 303.55 K, **9 de 12** puntos clave pasan
a CORREGIBLE.

### Qué se hizo
- **Estudio 3.1:** se midió, por interpolación, el valor donde cada margen cambia de signo.
- **Estudio 6.1:** 12 puntos clave de las fases anteriores (A\*, óptimos de 5.1, franja de 4.2, mejor de 3.2…):
  6.1a, 12 puntos × 2 motores (24 corridas); 6.1b, los mismos 12 con piso de O2 en 303.55 K (12 corridas);
  6.1c, bisección de P_baja en 8 de ellos para exigir 2 K y 5 K de subenfriamiento (131 evaluaciones).

### Tablas

**Tabla 3.1-3 (columna «Distancia a la frontera de O2»).** Ver R5. Valores: P_alta 0.007, ε_cond 0.012,
P_baja 0.016, x_b 0.018, T_sumidero 0.022, T_fuente 0.024, ε_HRVG 0.039, ε_reg 0.057 y η_t 0.343 (la única
holgada).

**Tabla 6.1-4 — Costo del subenfriamiento.** Cuánta P_baja extra cuesta exigir un margen de 2 K o 5 K.

| Identificador | Origen | Subenfriamiento, ΔT_sub [K] | Alcanzable | P_baja original [kPa] | P_baja requerida [kPa] | ΔP_baja [kPa] | η original [%] | η requerida [%] | Δη [pp] | Nota |
|---|---|---|---|---|---|---|---|---|---|---|
| P05 | estudio 5.1, óptimo A1 | 2 | sí | 808.34 | 1251.079 | 442.739 | 14.978 | 11.308 | -3.67 | hueco NO_CONVERGIO en 1231.3 kPa, 1244.5 kPa, 1247.8 kPa |
| P03 | estudio 4.2, presiones del profesor, techo | 5 | sí | 400 | 468.359 | 68.359 | 10.807 | 10.008 | -0.799 | — |
| P03 | estudio 4.2, presiones del profesor, techo | 2 | sí | 400 | 424.609 | 24.609 | 10.807 | 10.506 | -0.301 | — |
| P06 | estudio 5.1, óptimo A2 | 2 | sí | 393.75 | 393.75 | 0 | 15.482 | 15.482 | 0 | — |
| P01 | Ancla A* | 2 | sí | 563.636 | 597.443 | 33.807 | 8.482 | 8.193 | -0.288 | — |
| P01 | Ancla A* | 5 | sí | 563.636 | 650.568 | 86.932 | 8.482 | 7.769 | -0.713 | — |
| P07 | estudio 5.1, óptimo A3 | 2 | sí | 1359.557 | 1359.557 | 0 | 12.739 | 12.739 | 0 | — |
| P02 | estudios 2.1 y 2.2, mayor η | 2 | sí | 736.364 | 782.067 | 45.703 | 9.15 | 8.775 | -0.376 | — |
| P02 | estudios 2.1 y 2.2, mayor η | 5 | sí | 736.364 | 852.699 | 116.335 | 9.15 | 8.232 | -0.918 | — |
| P09 | estudio 5.1, óptimo A5 | 2 | sí | 1022.274 | 1022.274 | 0 | 11.094 | 11.094 | 0 | — |
| P09 | estudio 5.1, óptimo A5 | 5 | sí | 1022.274 | 1022.274 | 0 | 11.094 | 11.094 | 0 | — |
| P05 | estudio 5.1, óptimo A1 | 5 | sí | 808.34 | 1251.079 | 442.739 | 14.978 | 11.308 | -3.67 | hueco NO_CONVERGIO en 1231.3 kPa, 1244.5 kPa, 1247.8 kPa |
| P08 | estudio 5.1, óptimo A4 | 5 | sí | 400 | 471.094 | 71.094 | 15.6 | 14.426 | -1.174 | — |
| P08 | estudio 5.1, óptimo A4 | 2 | sí | 400 | 427.344 | 27.344 | 15.6 | 15.128 | -0.472 | — |
| P06 | estudio 5.1, óptimo A2 | 5 | sí | 393.75 | 412.976 | 19.226 | 15.482 | 15.15 | -0.332 | — |
| P07 | estudio 5.1, óptimo A3 | 5 | sí | 1359.557 | 1408.56 | 49.003 | 12.739 | 12.41 | -0.329 | — |

*Tabla 6.1-4 · hoja «6.1-4 Costo del subenfriamiento» · 16 filas.*

Columnas:
- **Identificador.** Etiqueta del punto de control (P01…P12).
- **Origen.** Estudio y punto del que viene.
- **Subenfriamiento, ΔT_sub [K].** Margen de subenfriamiento exigido a la entrada de la bomba.
- **Alcanzable.** Si existe una P_baja que lo cumple.
- **P_baja original [kPa].** P_baja del punto sin exigir margen.
- **P_baja requerida [kPa].** P_baja necesaria para tener ese margen.
- **ΔP_baja [kPa].** Aumento de P_baja que cuesta el margen.
- **η original [%].** η del punto original.
- **η requerida [%].** η con la P_baja requerida.
- **Δη [pp].** η con la P_baja requerida − η original, en puntos porcentuales (negativo = cuesta eficiencia).
- **Razón de presiones requerida, r_P [–].** r_P con la P_baja requerida.
- **Margen O1 requerido [–].** Margen de O1 con la P_baja requerida.
- **Iteraciones.** Pasos de bisección usados.
- **Nota.** Advertencia sobre ese cálculo.

*Lectura:* exigir **2 K** cuesta **+25 a +46 kPa** de P_baja y **−0.3 a −0.5 pp** de η (mediana por kelvin:
13.9 kPa y 0.16 pp en 10 pares); exigir 5 K, +19 a +116 kPa y −0.3 a −1.2 pp. Con las presiones del profesor
(P03), 2 K piden subir P_baja de 400 a ~425 kPa. *Advertencia:* el cálculo de P05 (óptimo 5.1a) no es
confiable (hay un hueco NO_CONVERGIO y la bisección saltó).

**Tabla S-5 — Criterios que bloquean, por estudio.**

| Estudio | Genuinos no KALINA | O1 (n) | O1 [%] | O2 (n) | O2 [%] | O3 (n) | O3 [%] | O5 (n) | O5 [%] |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 | 0 | 0 | — | 0 | — | 0 | — | 0 | — |
| 2.1 | 15 | 11 | 73.333 | 15 | 100 | 0 | 0 | 2 | 13.333 |
| 2.2 | 106 | 5 | 4.717 | 106 | 100 | 0 | 0 | 0 | 0 |
| 2.3 | 134 | 17 | 12.687 | 134 | 100 | 0 | 0 | 0 | 0 |
| 2.4 | 116 | 14 | 12.069 | 116 | 100 | 3 | 2.586 | 0 | 0 |
| 3.1 | 62 | 0 | 0 | 61 | 98.387 | 4 | 6.452 | 0 | 0 |
| 3.2 | 331 | 21 | 6.344 | 324 | 97.885 | 22 | 6.647 | 0 | 0 |
| 3.3 | 45 | 0 | 0 | 44 | 97.778 | 1 | 2.222 | 1 | 2.222 |
| 4.1 | 362 | 20 | 5.525 | 362 | 100 | 142 | 39.227 | 1 | 0.276 |
| 4.2 | 45 | 0 | 0 | 30 | 66.667 | 15 | 33.333 | 0 | 0 |
| 6.1 | 9 | 0 | 0 | 9 | 100 | 0 | 0 | 0 | 0 |
| 5.1 | 130 | 29 | 22.308 | 114 | 87.692 | 0 | 0 | 0 | 0 |
| 4.3 | 625 | 30 | 4.8 | 613 | 98.08 | 149 | 23.84 | 0 | 0 |
| 6.2 | 65 | 0 | 0 | 65 | 100 | 0 | 0 | 0 | 0 |

*Tabla S-5 · hoja «S-5 Criterios que bloquean, por» · 14 filas.*

Columnas:
- **Estudio.** Estudio (N.M).
- **Genuinos no KALINA.** Genuinos que no son KALINA (los que tienen algún criterio fallado).
- **O1 (n).** Genuinos no KALINA en que falla O1.
- **O1 [%].** Porcentaje de los genuinos no KALINA en que falla O1.
- **O2 (n).** Genuinos no KALINA en que falla O2.
- **O2 [%].** Porcentaje de los genuinos no KALINA en que falla O2.
- **O3 (n).** Genuinos no KALINA en que falla O3.
- **O3 [%].** Porcentaje de los genuinos no KALINA en que falla O3.
- **O5 (n).** Genuinos no KALINA en que falla O5.
- **O5 [%].** Porcentaje de los genuinos no KALINA en que falla O5.

*Lectura:* **O2 es el criterio que bloquea en el 88–100 % de los genuinos no KALINA** de todos los estudios,
salvo 4.2 (67 %). O3 pesa en 4.1 (39 %) y 4.2 (33 %), por fuentes frías o x_b baja.

### Figuras

**Figura 3.1-4 — márgenes a la frontera de O2.**

> **Figura 3.1-4. A* está a menos del 6 % del rango de la frontera de O2 en 8 de 9 variables.**
> Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
> Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
> Filtro: m3_cruces.csv (tipo = margen).
> n = 9. Fuente: resultados/2026-10-06_final_M3/m3_cruces.csv.

*Cómo se lee:* una marca por variable con la distancia de A\* a su frontera de O2, como fracción del rango
de la variable. En la figura de Matplotlib hay una **línea punteada en 0.06** (6 %); en el gráfico de Excel
las barras **rojas** son las que quedan por debajo del 6 %. La más corta es P_alta.

### Dónde verlo en el Excel
`3.1-3`, `6.1-3`, `6.1-4`, `S-5`, y `3 Gráficos`.

### Qué dice y qué no dice
- **Dice:** el criterio O2 del modelo **no tiene margen propio**; un diseño «KALINA» sin margen de
  subenfriamiento es frágil frente a pequeñas variaciones del clima. Los óptimos de 5.1 terminan al borde de
  O2 o de O1.
- **Dar un margen es barato:** ~25–46 kPa y menos de 0.5 pp de η, y no cambia materialmente ningún rango.
- **No dice:** que los diseños sean inviables; dice que hay que dimensionar con margen.

> **Cómo explicarlo (30 s):** *«Todos los diseños KALINA están pegados a la frontera de cavitación; a mi
> punto ancla le basta bajar la presión alta 64 kPa para fallar. Pedir 2 K de margen cuesta unos 25–45 kPa de
> presión de baja y menos de medio punto de eficiencia.»*

---

## R7. El clima y la composición mueven la frontera

**Pregunta:** ¿cómo cambian los rangos KALINA con el sitio (T_sumidero) y con la mezcla (x_b)?

**Resultado:** un sumidero 22 K más frío **reduce a la mitad la P_baja necesaria** y sube η 2–3 pp; más
amoníaco **exige más P_baja** (+144 kPa por cada 0.1 de x_b en Húsavík). El profesor exacto nunca es KALINA ni
con clima frío: el problema es la fuente.

### Qué se hizo

**Estudio 2.4 — sumidero más frío.** T_sumidero × P_baja en 4 bases, con T_sumidero ∈ {278.15, 283.15,
288.15, 293.15, 300.03} K y el piso de O2 igual a cada valor; P_baja 150–1500 kPa (10 valores) + bisección
(tolerancia 10 kPa, hasta 7 iteraciones). 320 corridas.

| Parte | Base | Qué cambia respecto al profesor |
|---|---|---|
| 2.4a | B1 | T_fuente = 403 K (la fuente de A\*) |
| 2.4b | B2 | T_fuente = 420 K (el KALINA de mayor η de 2.1–2.2) |
| 2.4c | B3 | ε_HRVG = 0.40 (conserva la fuente de 623 K) |
| 2.4d | B4 | nada (profesor exacto) |

**Estudio 6.2 — Húsavík.** Se parte de un ancla distinta (planta real): P_alta 3300 kPa, P_baja 690 kPa,
T_fuente 394.15 K, T_sumidero 278.15 K, η_t 0.90, η_p 0.80, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95, con piso de O2
en 283.15 K. Partes: 6.2b una variable a la vez (15 valores × 10 variables = 150); 6.2c malla x_b × P_baja
(x_b 0.70–0.91 × 8 valores de P_baja = 64; y con x_b 0.30–0.70 la malla de 9 × 6 = 54); 6.2d x_b 0.30–0.70 (17
valores, P_baja = 690 kPa).

### Tablas

**Tabla 2.4-3 — Malla T_sumidero × P_baja por base.**

| Base | Temperatura del sumidero, T_sumidero [K] | Genuinos | KALINA | P_baja mínima KALINA [kPa] | η mínima KALINA [%] | Fuera de rango en la mínima KALINA | Bloqueantes (genuinos) |
|---|---|---|---|---|---|---|---|
| B1 | 278.15 | 18 | 11 | 290.625 | 10.409 | no | CORREGIBLE(7) |
| B1 | 283.15 | 18 | 12 | 337.5 | 10.034 | no | CORREGIBLE(6) |
| B1 | 288.15 | 18 | 12 | 393.75 | 9.606 | no | CORREGIBLE(6) |
| B1 | 293.15 | 18 | 15 | 459.375 | 9.143 | no | CORREGIBLE(2) · INVIABLE(1) |
| B1 | 300.033 | 18 | 9 | 562.5 | 8.492 | no | CORREGIBLE(8) · INVIABLE(1) |
| B2 | 278.15 | 18 | 12 | 393.75 | 11.908 | no | CORREGIBLE(6) |
| B2 | 283.15 | 18 | 15 | 459.375 | 11.276 | no | CORREGIBLE(3) |
| B2 | 288.15 | 18 | 13 | 534.375 | 10.622 | no | CORREGIBLE(5) |
| B2 | 293.15 | 18 | 12 | 618.75 | 9.957 | no | CORREGIBLE(6) |
| B2 | 300.033 | 18 | 8 | 740.625 | 9.115 | no | CORREGIBLE(9) · INVIABLE(1) |
| B3 | 278.15 | 17 | 6 | 750 | 9.687 | sí | CORREGIBLE(11) |
| B3 | 283.15 | 18 | 7 | 862.5 | 8.89 | sí | CORREGIBLE(11) |
| B3 | 288.15 | 18 | 10 | 984.375 | 8.109 | sí | CORREGIBLE(8) |
| B3 | 293.15 | 18 | 7 | 1115.625 | 7.342 | sí | CORREGIBLE(11) |
| B3 | 300.033 | 18 | 4 | 1312.5 | 6.302 | sí | CORREGIBLE(14) |
| B4 | 278.15 | 0 | 0 | — | — | — | — |
| B4 | 283.15 | 0 | 0 | — | — | — | — |
| B4 | 288.15 | 0 | 0 | — | — | — | — |
| B4 | 293.15 | 0 | 0 | — | — | — | — |
| B4 | 300.033 | 0 | 0 | — | — | — | — |

*Tabla 2.4-3 · hoja «2.4-3 Malla T_sumidero x P_baja» · 20 filas.*

Columnas:
- **Base.** Base del barrido: B1 = 2.4a (fuente 403 K), B2 = 2.4b (420 K), B3 = 2.4c (ε_HRVG 0.40), B4 = 2.4d (profesor exacto).
- **Temperatura del sumidero, T_sumidero [K].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **KALINA.** Puntos que cumplen todos los criterios.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **P_baja mínima KALINA [kPa].** Menor P_baja con la que el punto es KALINA.
- **η mínima KALINA [%].** η del punto KALINA de P_baja mínima (no es la menor η de la fila).
- **B verificado en la mínima KALINA.** Si el punto de P_baja mínima pasó la verificación B (el motor real recalcula h4s; marca «no verificado» si |Δh4s| > 2.0 kJ/kg).
- **Fuera de rango en la mínima KALINA.** Si el punto de P_baja mínima está fuera del rango validado.
- **η máxima KALINA [%].** Mayor η entre los KALINA de la fila.
- **P_baja en la η máxima KALINA [kPa].** P_baja en la que se da esa η máxima.
- **Bloqueantes (genuinos).** Clases de los genuinos que no son KALINA, con su conteo.
- **Códigos de bloqueo.** Criterios que fallan en esos genuinos.

*Lectura:* en B1, la P_baja mínima baja de 562.5 kPa (300 K) a 290.6 kPa (278 K) y η sube de 8.49 a 10.41 %.
En B3 (ε_HRVG = 0.40) toda la columna «fuera de rango» es verdadera: ninguno es confiable. **B4 tiene 0
genuinos en los cinco climas.** La pendiente de la P_baja mínima es −12.5 kPa/K en B1 (R² = 0.99), −15.9 en B2
y −25.7 en B3; η sube +0.088, +0.128 y +0.155 pp/K.

**Tabla 6.2-4 — Rangos KALINA por variable (Húsavík, una a la vez).**

| Variable | Mínimo KALINA | Máximo KALINA | Criterio que rompe al bajar la variable | Criterio que rompe al subir la variable | η mínima [%] | η máxima [%] | KALINA |
|---|---|---|---|---|---|---|---|
| T_fuente | 380 | 401.429 | — | CORREGIBLE (O2) | 12.208 | 12.962 | 7 |
| T_sumidero | 273.15 | 283.15 | — | CORREGIBLE (O2) | 12.509 | 12.963 | 8 |
| P_alta | 2821.429 | 4000 | CORREGIBLE (O2) | — | 11.836 | 13.602 | 12 |
| P_baja | 700 | 1200 | CORREGIBLE (O2) | — | 8.492 | 12.581 | 11 |
| x_b | 0.6 | 0.825 | — | CORREGIBLE (O2) | 8.816 | 12.778 | 9 |
| η_t | 0.75 | 0.95 | — | — | 10.534 | 13.464 | 15 |
| η_p | 0.6 | 0.9 | — | — | 12.58 | 12.783 | 15 |
| ε_HRVG | 0.6 | 0.925 | — | CORREGIBLE (O2) | 11.634 | 12.995 | 14 |
| ε_reg | 0.4 | 0.95 | — | — | 11.941 | 13.223 | 15 |
| ε_cond | 0.95 | 0.95 | CORREGIBLE (O2) | — | 12.732 | 12.732 | 1 |

*Tabla 6.2-4 · hoja «6.2-4 Rangos KALINA por variabl» · 10 filas.*

Columnas:
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **Mínimo KALINA.** Menor valor de la variable con KALINA.
- **Máximo KALINA.** Mayor valor de la variable con KALINA.
- **Criterio que rompe al bajar la variable.** Primer criterio que falla más allá del mínimo KALINA.
- **Criterio que rompe al subir la variable.** Primer criterio que falla más allá del máximo KALINA.
- **η mínima [%].** Menor η entre los KALINA de la variable.
- **η máxima [%].** Mayor η entre los KALINA del escenario (en 6.2-4, de los KALINA de la variable).
- **KALINA.** Puntos que cumplen todos los criterios.

*Lectura:* con lo demás en el ancla de Húsavík, hay KALINA con T_fuente 380–401 K, T_sumidero 273–283 K,
P_alta 2821–4000 kPa, P_baja 700–1200 kPa, x_b 0.60–0.825 y ε_HRVG 0.60–0.925; ε_cond solo en 0.95. η_t, η_p y
ε_reg: todo el rango probado. Casi todo rompe por O2.

**Tabla 6.2-5 — Frontera KALINA al variar x_b (Húsavík, x_b bajo).**

| x_b | P_baja mínima KALINA [kPa] | η en ese punto [%] | Criterio que más bloquea |
|---|---|---|---|
| 0.3 | — | — | — |
| 0.35 | — | — | — |
| 0.4 | — | — | O3 |
| 0.45 | — | — | O3 |
| 0.5 | 200 | 1.225 | — |
| 0.55 | 300 | 9.562 | O2 |
| 0.6 | 400 | 11.637 | O2 |
| 0.65 | 500 | 12.173 | O2 |
| 0.7 | 500 | 13.312 | O2 |

*Tabla 6.2-5 · hoja «6.2-5 Frontera KALINA al variar» · 9 filas.*

Columnas:
- **x_b.** Fracción de amoníaco de la mezcla base.
- **P_baja mínima KALINA [kPa].** Menor P_baja con la que el punto es KALINA.
- **η en ese punto [%].** η en la P_baja mínima KALINA.
- **Criterio que más bloquea.** Criterio que más falla en esa fila.

*Lectura:* **con x_b ≤ 0.45 no hay ciclo** (0 genuinos de 32: 16 no convergen y 16 son falsos convergidos);
**x_b = 0.50** es KALINA formal pero con η de 0.1–1.2 %; **x_b = 0.55** es el primer KALINA útil (P_baja mín.
300 kPa, η = 9.6 %); luego P_baja mínima 400, 500 y 500 kPa para 0.60, 0.65 y 0.70.

### Figuras

**Figura 2.4-1 (2 paneles).**

> **Figura 2.4-1. Un sumidero más frío baja la P_baja mínima de KALINA y sube η.**
> Estudio 2.4 (figura de síntesis: cada base es una parte con sus propios datos fijos y cada línea es una parte).
> Parte 2.4a (T_fuente = 403 K (A*)): Datos fijos: T_fuente = 403.0; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
> Parte 2.4b (T_fuente = 420 K): Datos fijos: T_fuente = 420.0; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
> Parte 2.4c (ε_HRVG = 0.40 (fuente del profesor)): Datos fijos: T_fuente = 623.15; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.4; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
> Base B4 (datos del profesor, T_fuente 623.15 K): 0 KALINA; no se dibuja (queda nombrada en el pie).
> Filtro: mínimos de P_baja y máximos de η de los KALINA por (base, T_sumidero).
> n = 15 puntos por panel (3 bases × 5 T_sumidero). Fuente: todos_los_puntos.csv.

*Cómo se lee:* izquierda, P_baja mínima KALINA contra T_sumidero; derecha, η máxima KALINA contra T_sumidero,
una línea por base (2.4a, 2.4b, 2.4c). Las líneas son casi rectas y paralelas: la relación es lineal en
278–300 K. 2.4d no aparece porque no tiene KALINA.

**Figura 6.2-1 — malla x_b × P_baja.**

> **Figura 6.2-1. Húsavík: la P_baja mínima de KALINA sube con la fracción de amoníaco x_b.**
> Estudio 6.2 · parte(s) 6.2c. Punto base: Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K
> Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp.
> Datos barridos: P_baja [200–1200] kPa (8 valores); x_b [0.3–0.91] (9 valores).
> Filtro: todos los puntos de las dos mallas (mismos datos fijos); línea = P_baja mínima KALINA por x_b; x_b = 0.50 es KALINA con η < 1.3 %.
> n = 118. Fuente: todos_los_puntos.csv.

*Cómo se lee:* x_b (horizontal) contra P_baja (vertical), color por clase, y una **línea punteada negra** que
une la P_baja mínima KALINA de cada x_b: sube con x_b.

**Figura 6.2-2 — η una variable a la vez (10 paneles).**

> **Figura 6.2-2. Húsavík: eficiencia según cada variable, una a la vez (casi todas rompen por O2).**
> Estudio 6.2 · parte(s) 6.2b. Punto base: Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K
> Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.82; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
> Datos barridos (uno a la vez): T_fuente [380–430] K (15 valores); T_sumidero [273.15–293.15] K (15 valores); P_alta [2500–4000] kPa (15 valores); P_baja [500–1200] kPa (15 valores); x_b [0.6–0.95] (15 valores); η_t [0.75–0.95] (15 valores); η_p [0.6–0.9] (15 valores); ε_HRVG [0.6–0.95] (15 valores); ε_reg [0.4–0.95] (15 valores); ε_cond [0.7–0.95] (15 valores).
> Filtro: η solo en genuinos con W_net > 0; ✕ sobre el eje = no genuino.
> n = 150. Fuente: todos_los_puntos.csv.

*Cómo se lee:* igual que 3.1-3 pero alrededor del ancla de Húsavík; los puntos sin η se dibujan en η = 0.

**Gráfico adicional (sin número de figura): «Húsavík con poco amoníaco: η según x_b».** Está en `6 Gráficos`
y junto a la parte 6.2d en la hoja `6.2-R`; muestra los 17 valores de x_b con P_baja = 690 kPa.

### Dónde verlo en el Excel
`2.4-1`, `2.4-2`, `2.4-3`, `2.4-R`, `6.2-4`, `6.2-5`, `6.2-R`, y las hojas `2 Gráficos` y `6 Gráficos`.

### Qué dice y qué no dice
- **Dice:** al recomendar presiones hay que decir siempre el clima de diseño; la ventaja del clima frío llega
  por la vía indirecta (relaja O2 → permite P_baja menor → sube η), no por un efecto directo (con P_baja
  fija, T_sumidero mueve η solo 0.85 pp, dentro de la banda).
- **Límites:** a 278.15 K, 11 de 64 puntos no son genuinos; paso de 150 kPa en P_baja; el cambio de regla del
  piso de O2 (= T_sumidero) impide comparar punto a punto con 1.1–3.1; la conclusión sobre x_b = 0.50 vale con
  el ancla de Húsavík (con otras condiciones, p. ej. 4.2, x_b = 0.50 da η de 8–11 %); las soluciones aparentes
  con x_b bajo son espurias: son indicio, no prueba.

> **Cómo explicarlo (30 s):** *«Un clima 22 K más frío permite la mitad de presión de baja y sube la
> eficiencia 2–3 puntos, pero no arregla el caso del profesor: el problema es la fuente. Y con más amoníaco
> hace falta más presión de baja, unos 144 kPa por cada 0.1.»*

---

## R8. Qué datos del profesor se pueden conservar: casi todos, menos la fuente a 623 K

**Pregunta:** ¿cuánto del enunciado se puede mantener y ser KALINA?

**Resultado:** **8 de 10 datos** (P_alta, P_baja, x_b y las cinco η/ε) con la fuente a 391–409 K y el sumidero
a 280–293 K. Con las dos presiones del profesor, ε_cond ≥ 0.875 y fuente a 390–410 K. **La fuente de 623 K no
se conserva.**

### Qué se hizo

**Estudio 4.1 — escenarios (exploración).** Un LHS de 120 puntos por escenario; las variables no conservadas
se sortean en la caja P_alta 2000–5000 kPa, P_baja 200–2000 kPa, T_fuente 380–623.15 K, T_sumidero
278.15–303.55 K, x_b 0.50–0.85, η/ε 0.40–0.95. Piso de O2 = T_sumidero. 600 puntos (2 omitidos).

| Parte | Datos conservados | Datos abandonados |
|---|---|---|
| 4.1a | T_fuente 623.15 K y T_sumidero 300.03 K | los otros 8 |
| 4.1b | P_alta 3000 y P_baja 400 kPa | los otros 8 |
| 4.1c | P_alta, P_baja y T_sumidero 300.03 K | los otros 7 |
| 4.1d | P_alta 3000 kPa, T_fuente 623.15 K y T_sumidero | los otros 7 |
| 4.1e | T_fuente 623.15 K y x_b 0.50 | los otros 8 |

**Estudio 4.2 — malla dirigida con las presiones del profesor.** T_fuente 385–410 K (cada 2.5; 11 valores) ×
ε_cond {0.85, 0.875, 0.90, 0.925, 0.95} × T_sumidero (= piso de O2) {278.15, 290.65, 300.03} K = 165 corridas.
Se conservan exactamente P_alta = 3000, P_baja = 400, x_b = 0.50, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85 y
ε_reg = 0.75. Se hizo porque 4.1 no encontró la franja (muy angosta para un muestreo al azar).

**Estudio 4.3 — escalera.** Ronda 0: se conserva un grupo (6 opciones, 100 puntos cada una); rondas 1 a 3: al
mejor conjunto se le suma un grupo (30 puntos por opción). En el conjunto final solo se barren T_fuente
(384–520 K) y T_sumidero (278–303.4 K). 987 corridas. Verificación de 3 puntos con el motor real (1500 s).

### Tablas

**Tabla 4.1-3 — Resumen por escenario.**

| Escenario | N | Omitidos | Evaluados | KALINA | Genuinos | Falsos convergidos | Fuera de rango | Factible | Criterio bloqueante | Veces que bloquea | D mínimo | η máxima [%] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 1 | 119 | 4 | 59 | 2 | 53 | sí | O2 | 55 | 0 | 9.289 |
| 2 | 120 | 0 | 120 | 0 | 95 | 2 | 66 | no | O2 | 95 | 0.22 | — |
| 3 | 120 | 0 | 120 | 0 | 84 | 6 | 64 | no | O2 | 84 | 1.57 | — |
| 4 | 120 | 0 | 120 | 6 | 62 | 2 | 57 | sí | O2 | 56 | 0 | 6.72 |
| 5 | 120 | 1 | 119 | 10 | 82 | 0 | 82 | sí | O2 | 72 | 0 | 8.458 |

*Tabla 4.1-3 · hoja «4.1-3 Resumen por escenario de» · 5 filas.*

Columnas:
- **Escenario.** Escenario de conservación (1 = 4.1a … 5 = 4.1e).
- **N.** Cantidad de puntos usados (n).
- **Omitidos.** Puntos que el modelo no llegó a evaluar; no aparecen ni en las tablas de resultados ni en los gráficos.
- **Evaluados.** Puntos evaluados (corridas − omitidos).
- **KALINA.** Puntos que cumplen todos los criterios.
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **Fuera de rango.** Puntos con estados fuera del rango validado de propiedades (p. ej. líquido por encima de 420 K); su η se toma con cautela.
- **Factible.** True si el escenario tiene al menos un KALINA.
- **Criterio bloqueante.** Criterio que más falla entre los genuinos no KALINA.
- **Veces que bloquea.** Cuántas veces falla ese criterio.
- **D mínimo.** Menor índice de cercanía D de la fila (0 = cumple todos los criterios operativos).
- **Identificador del D mínimo.** Punto con el menor D del escenario.
- **Identificador del más cercano.** Punto KALINA más cercano al profesor.
- **d del más cercano.** Distancia d de ese punto al profesor.
- **η del más cercano [%].** η de ese punto.
- **Identificador de la η máxima.** Punto KALINA de mayor η.
- **η máxima [%].** Mayor η entre los KALINA del escenario (en 6.2-4, de los KALINA de la variable).
- **Tiempo total [s].** Tiempo de cómputo total del escenario.

*Lectura:* KALINA = 4, 0, 0, 6, 10 (4.1a a 4.1e); en **todos** el criterio bloqueante es O2. «Factible = no»
en 4.1b y 4.1c significa que el muestreo no encontró KALINA, **no** que no existan (4.2 los encuentra).

**Tabla 4.1-4 — Rangos por escenario (KALINA contra no KALINA).** 58 filas: por escenario y variable, los
percentiles de cada grupo y su KS. Primeras filas:

| Escenario | Variable | Grupo | N | Mínimo | Percentil 5 | Mediana | Percentil 95 | Máximo | KS | Valor p |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P_alta | KALINA | 4 | 2102.199 | 2267.997 | 3556.735 | 4597.618 | 4719.677 | — | — |
| 1 | P_alta | no_KALINA | 115 | 2044.196 | 2201.352 | 3522.053 | 4850.241 | 4986.581 | — | — |
| 1 | P_baja | KALINA | 4 | 1359.557 | 1394.418 | 1735.658 | 1952.681 | 1965.621 | — | — |
| 1 | P_baja | no_KALINA | 115 | 202.14 | 294.477 | 1059.919 | 1885.435 | 1989.717 | — | — |
| 1 | x_b | KALINA | 4 | 0.577 | 0.581 | 0.657 | 0.812 | 0.829 | — | — |
| 1 | x_b | no_KALINA | 115 | 0.501 | 0.518 | 0.677 | 0.832 | 0.849 | — | — |
| 1 | η_t | KALINA | 4 | 0.492 | 0.536 | 0.809 | 0.836 | 0.836 | — | — |
| 1 | η_t | no_KALINA | 115 | 0.401 | 0.43 | 0.667 | 0.92 | 0.947 | — | — |

*Tabla 4.1-4 · hoja «4.1-4 Rangos por escenario (KAL» · 58 filas (se muestran 8).*

**Tabla 4.2-3 — Frontera KALINA con las presiones del profesor.**

| Temperatura del sumidero, T_sumidero [K] | Efectividad del condensador, ε_cond [–] | KALINA | T_fuente mínima [K] | T_fuente máxima [K] | η en T_fuente mínima [%] | η en T_fuente máxima [%] |
|---|---|---|---|---|---|---|
| 278.15 | 0.85 | 8 | 390 | 407.5 | 1.925 | 9.827 |
| 278.15 | 0.875 | 9 | 390 | 410 | 1.893 | 10.133 |
| 278.15 | 0.9 | 9 | 390 | 410 | 1.864 | 10.016 |
| 278.15 | 0.925 | 9 | 390 | 410 | 1.836 | 9.905 |
| 278.15 | 0.95 | 9 | 390 | 410 | 1.809 | 9.8 |
| 290.65 | 0.85 | 8 | 390 | 407.5 | 2.271 | 10.402 |
| 290.65 | 0.875 | 9 | 390 | 410 | 2.237 | 10.699 |
| 290.65 | 0.9 | 9 | 390 | 410 | 2.205 | 10.577 |
| 290.65 | 0.925 | 9 | 390 | 410 | 2.175 | 10.462 |
| 290.65 | 0.95 | 9 | 390 | 410 | 2.146 | 10.352 |
| 300.033 | 0.85 | 0 | — | — | — | — |
| 300.033 | 0.875 | 1 | 390 | 390 | 2.539 | 2.539 |
| 300.033 | 0.9 | 2 | 390 | 392.5 | 2.505 | 5.031 |
| 300.033 | 0.925 | 4 | 390 | 397.5 | 2.473 | 7.854 |
| 300.033 | 0.95 | 9 | 390 | 410 | 2.442 | 10.807 |

*Tabla 4.2-3 · hoja «4.2-3 Frontera KALINA con las p» · 15 filas.*

Columnas:
- **Temperatura del sumidero, T_sumidero [K].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Efectividad del condensador, ε_cond [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **KALINA.** Puntos que cumplen todos los criterios.
- **T_fuente mínima [K].** Menor T_fuente con KALINA en ese clima y ε_cond.
- **T_fuente máxima [K].** Mayor T_fuente con KALINA.
- **η en T_fuente mínima [%].** η en el extremo inferior de la franja.
- **η en T_fuente máxima [%].** η en el extremo superior de la franja.

*Lectura:* con el clima del profesor (300.03 K): ε_cond 0.85 → 0 celdas KALINA; 0.875 → 1 (390 K); 0.90 → 2
(390–392.5); 0.925 → 4 (390–397.5); 0.95 → 9 (390–410 K). Con clima más frío (278 o 290.65 K) basta 0.85. La
mejor η es **10.81 %** (410 K, ε_cond 0.95, 300 K). Por debajo de 390 K, falla O3 (trabajo negativo) en 15 de
15.

**Tabla 4.3-3 — Escalera de conservación.**

| Ronda | Datos conservados | Datos del profesor conservados | Evaluadas | Genuinos | KALINA | KALINA confiables | D mínimo | Criterio más roto | Elegido | KALINA por búsqueda |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | T_fuente | 1 | 100 | 60 | 7 | 0 | 0 | O2:53 | no | no |
| 0 | eficiencias | 5 | 100 | 88 | 13 | 11 | 0 | O2:75 | no | no |
| 0 | P_alta | 1 | 100 | 88 | 19 | 12 | 0 | O2:69 | no | no |
| 0 | P_baja | 1 | 100 | 85 | 1 | 1 | 0 | O2:84 | no | no |
| 0 | T_sumidero | 1 | 100 | 87 | 17 | 13 | 0 | O2:68 | no | no |
| 0 | x_b | 1 | 100 | 85 | 29 | 15 | 0 | O2:51 | sí | no |
| 1 | x_b+T_fuente | 2 | 30 | 20 | 2 | 0 | 0 | O2:18 | no | no |
| 1 | x_b+eficiencias | 6 | 30 | 26 | 11 | 6 | 0 | O2:15 | no | no |
| 1 | x_b+P_alta | 2 | 30 | 28 | 11 | 7 | 0 | O2:17 | sí | no |
| 1 | x_b+P_baja | 2 | 30 | 27 | 4 | 3 | 0 | O2:23 | no | no |
| 1 | x_b+T_sumidero | 2 | 30 | 26 | 9 | 5 | 0 | O2:16 | no | no |
| 2 | x_b+P_alta+T_fuente | 3 | 30 | 19 | 3 | 0 | 0 | O2:16 | no | no |
| 2 | x_b+P_alta+eficiencias | 7 | 30 | 28 | 13 | 7 | 0 | O2:14 | sí | no |
| 2 | x_b+P_alta+P_baja | 3 | 30 | 28 | 2 | 2 | 0 | O2:26 | no | no |
| 2 | x_b+P_alta+T_sumidero | 3 | 30 | 27 | 8 | 6 | 0 | O2:19 | no | no |
| 3 | x_b+P_alta+eficiencias+T_fuente | 8 | 30 | 0 | 0 | 0 | — | — | no | no |
| 3 | x_b+P_alta+eficiencias+P_baja | 8 | 30 | 28 | 5 | 5 | 0 | O2:22 | sí | no |
| 3 | x_b+P_alta+eficiencias+T_sumidero | 8 | 30 | 29 | 6 | 4 | 0 | O2:21 | no | no |

*Tabla 4.3-3 · hoja «4.3-3 Escalera de conservación» · 18 filas.*

Columnas:
- **Ronda.** Ronda de la escalera (0 a 3).
- **Datos conservados.** Grupo de datos del profesor que se conserva en ese conjunto.
- **Datos del profesor conservados.** Cantidad de datos del profesor que se conservan exactamente en ese conjunto.
- **Evaluadas.** Evaluaciones del conjunto.
- **Genuinos.** Puntos que el modelo resolvió de verdad: KALINA + Corregibles + Inviables.
- **KALINA.** Puntos que cumplen todos los criterios.
- **KALINA confiables.** KALINA dentro del rango validado de propiedades (IAPWS G4-01) y con η y ε entre 0.40 y 0.95.
- **D mínimo.** Menor índice de cercanía D de la fila (0 = cumple todos los criterios operativos).
- **Criterio más roto.** Criterio que más falla entre los genuinos, con su conteo.
- **Elegido.** True si fue el conjunto elegido de esa ronda.
- **KALINA por búsqueda.** Marca interna de si los KALINA del conjunto salen de la búsqueda dirigida; en esta campaña vale «no» en las 18 filas.

*Lectura:* el conjunto elegido de cada ronda es el de «Elegido = sí»: x_b (15 confiables), x_b + P_alta (7),
x_b + P_alta + eficiencias (7) y **x_b + P_alta + eficiencias + P_baja (5 de 5 confiables)**. Ningún conjunto
con T_fuente da confiables; «x_b + P_alta + eficiencias + T_fuente» da 0 genuinos de 30.

**Tabla 4.3-4 — Verificación contra el motor real (1500 s).**

| Identificador | Origen | Clase con teqp | η con teqp [%] | Clase con el motor real | η con el motor real [%] | Δη [pp] | Coincide la clase |
|---|---|---|---|---|---|---|---|
| A* | Ancla A* | KALINA | 8.482 | KALINA | 8.482 | 0 | sí |
| A4 | Óptimo A4 de estudio 5.1 | KALINA | 15.6 | KALINA | 15.6 | 0 | sí |
| HUS | Base de Húsavík | KALINA | 12.732 | KALINA | 12.73 | -0.002 | sí |

*Tabla 4.3-4 · hoja «4.3-4 Verificación teqp contra» · 3 filas.*

**Tabla S-4 — Datos del profesor conservables.**

| Dato | Valor del profesor | ¿Se conserva con KALINA? | Respaldo |
|---|---|---|---|
| P_alta | 3000 kPa | sí | estudio 4.3 (x_b+P_alta+eficiencias+P_baja), estudio 4.2 |
| P_baja | 400 kPa | sí | estudio 4.3; con su clima de 300 K exige ε_cond ≥ 0.875 (estudio 4.2) |
| x_b | 0.50 | sí | estudio 4.3 (η hasta 10.6 %); con el ancla de Húsavík queda al límite, η < 1.3 % (estudio 6.2) |
| η_t | 0.85 | sí | estudio 4.3 (grupo EF) |
| η_p | 0.75 | sí | estudio 4.3 (grupo EF) |
| ε_HRVG | 0.85 | sí | estudio 4.3 (grupo EF) |
| ε_reg | 0.75 | sí | estudio 4.3 (grupo EF) |
| ε_cond | 0.80 | sí, si el sitio es más frío (≤ ~293 K) | estudio 4.3; con 300 K hace falta ≥ 0.875 (estudio 4.2) |
| T_sumidero | 300.03 K | con condiciones: o se baja a 280–293 K, o se sube ε_cond | estudio 4.3, estudio 4.2 |
| T_fuente | 623.15 K | no (bloqueo estructural) | estudio 1.1, estudios 2.1 y 2.2, estudio 4.3 (0 confiables con TF) |
| m_b | 1 kg/s | sí (base de cálculo) | todas |

*Tabla S-4 · hoja «S-4 Datos del profesor conserva» · 11 filas.*

### Figuras

**Figuras 4.1-1 a 4.1-5 (una por escenario).**

> **Figura 4.1-1. Parte 4.1a (conserva sus temperaturas, T_fuente y T_sumidero): 4 KALINA de 119 evaluados, 2 confiables.**
> Estudio 4.1 · parte(s) 4.1a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
> Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.
> Datos barridos: P_alta [2000.1–4986.6] kPa (120 valores); P_baja [202.14–1989.7] kPa (120 valores); x_b [0.50124–0.84895] (120 valores); η_t [0.40062–0.94745] (120 valores); η_p [0.4043–0.94919] (120 valores); ε_HRVG [0.40441–0.94919] (120 valores); ε_reg [0.40384–0.9479] (120 valores); ε_cond [0.40087–0.94579] (120 valores).
> Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
> n = 119. Fuente: todos_los_puntos.csv.

*Cómo se leen:* dispersión por escenario con los dos ejes más relevantes: **4.1a** P_alta × P_baja,
**4.1b** y **4.1c** T_fuente × ε_cond, **4.1d** x_b × P_baja, **4.1e** P_alta × P_baja. Color y forma por
clase; hueco = fuera de rango. Un escenario sin marcadores verdes (4.1b y 4.1c) no encontró KALINA.

**Figura 4.2-1 (3 paneles).**

> **Figura 4.2-1. Con las presiones del profesor hay KALINA desde T_fuente ≈ 390 K; con su clima (300 K) hace falta ε_cond ≥ 0.875.**
> Estudio 4.2. Punto base: PP con P_alta = 3000 kPa y P_baja = 400 kPa conservadas
> Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.
> Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); ε_cond [0.85–0.95] (5 valores); piso de O2 [278.15–300.03] K (3 valores).
> Filtro: todos los puntos de la malla (cuadrado verde = KALINA).
> n = 165. Fuente: todos_los_puntos.csv.

*Cómo se lee:* un panel por clima; T_fuente (horizontal) contra ε_cond (vertical). La franja de marcadores
verdes aparece a la derecha de 390 K y sube con ε_cond; en el clima de 300 K solo en las filas de ε_cond ≥
0.875.

**Figura 4.3-1 — escalera.**

> **Figura 4.3-1. Se conservan 8 de los 10 datos de diseño del profesor y sigue habiendo KALINA.**
> Estudio 4.3 (escalera de conservación; figura de síntesis: una barra por conjunto conservado). Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50).
> Datos fijos: los 10 datos de diseño del profesor; cada barra conserva el subconjunto que indica su etiqueta.
> Datos barridos: 100 puntos (ronda 0) o 30 (rondas 1–3) por conjunto.
> Filtro: KALINA confiables por conjunto conservado; el elegido de cada ronda se resalta con borde negro.
> n = 18 conjuntos. Fuente: resultados/2026-10-08_final_M9/m9_escalera.csv.

*Cómo se lee:* una barra por conjunto (R = ronda), alto = KALINA confiables; **verde oscuro = el elegido** de
cada ronda.

### Dónde verlo en el Excel
`4.1-1` a `4.1-4`, `4.2-1` a `4.2-3`, `4.3-1` a `4.3-4`, `S-4`, sus hojas `-R`, y `4 Gráficos`.

### Qué dice y qué no dice
- **Dice:** conservar 623 K casi nunca da KALINA confiable (2 de 20 en los escenarios con esa fuente, con
  P_baja 1.36–1.97 MPa y x_b 0.71–0.83); los datos del profesor son un ciclo Kalina válido si **solo se baja
  la fuente** (a ~390–410 K) y el sumidero a ≤ ~293 K. No se pueden conservar a la vez sus 2 presiones,
  ε_cond = 0.80 y su clima de 300 K: hace falta ε_cond ≥ 0.875.
- **Límites:** 120 puntos por escenario es una exploración, no un mapa; resolución de 2.5 K en T_fuente y 0.025
  en ε_cond en 4.2, **sin explorar T_fuente > 410 K**; el ranking de la escalera elige por KALINA confiables,
  no por cantidad de datos (x_b + P_alta con 2 datos le ganó a x_b + eficiencias con 6 en la ronda 1);
  búsquedas más finas conservan hasta 9 de 11 datos.

> **Cómo explicarlo (30 s):** *«Los datos del profesor funcionan si solo se cambia la temperatura de la
> fuente: de 623 K a unos 400 K, con un sumidero un poco más frío. Conservé presiones, composición y las cinco
> eficiencias. La fuente a 623 K es el único dato incompatible con el resto.»*

---

## R9. Cuánta eficiencia se puede lograr: hasta ~15.6 % con equipos de 0.95; 8–11 % con equipos medios

**Pregunta:** ¿cuál es la η máxima dentro de KALINA?

**Resultado:** **15.60 %**, conservando las presiones y el clima del profesor, con T_fuente = 415 K y η_t,
ε_HRVG, ε_reg y ε_cond en 0.95. Es una **cota superior**, no un diseño.

### Qué se hizo (estudio 5.1)
Cinco búsquedas por patrones (arranques) que conservan distintos datos del profesor; caja libre: T_fuente
380–500 K, T_sumidero 278.15–303.55 K, P_alta 2000–5000 kPa, P_baja 300–2500 kPa, x_b 0.50–0.85, η/ε
0.40–0.95. 560 evaluaciones; objetivo lexicográfico (D → 0, luego máxima η); pasos de ±10 % del rango que se
parten a la mitad; corte con paso < 1 % o 120 evaluaciones.

| Arranque | Datos del profesor conservados | Parte de |
|---|---|---|
| 5.1a | ninguno | mejor KALINA de 3.2 |
| 5.1b | ninguno | mejor KALINA de 2.4 (base 2.4b, 278.15 K) |
| 5.1c | sus temperaturas (623.15 K y 300.03 K) | — |
| 5.1d | sus presiones (3000/400 kPa) y su clima | — |
| 5.1e | su fuente y su x_b | — |

### Tablas

**Tabla 5.1-3 — Óptimos de η por arranque.**

| Arranque | Clase del ciclo | Índice de cercanía D [–] | Eficiencia térmica del ciclo, η [%] | Temperatura de la fuente, T_fuente [K] | Presión de alta, P_alta [kPa] | Presión de baja, P_baja [kPa] | Fracción de amoníaco de la mezcla base, x_b [–] | Evaluaciones |
|---|---|---|---|---|---|---|---|---|
| A1 | KALINA | 0 | 14.978 | 436.097 | 4381.823 | 808.34 | 0.705 | 117 |
| A2 | KALINA | 0 | 15.482 | 420 | 3000 | 393.75 | 0.5 | 105 |
| A3 | KALINA | 0 | 12.739 | 623.15 | 5000 | 1359.557 | 0.85 | 112 |
| A4 | KALINA | 0 | 15.6 | 415 | 3000 | 400 | 0.5 | 113 |
| A5 | KALINA | 0 | 11.094 | 623.15 | 4808.342 | 1022.274 | 0.5 | 113 |

*Tabla 5.1-3 · hoja «5.1-3 Óptimos de η por arranque» · 5 filas.*

Columnas:
- **Arranque.** Punto de partida de la búsqueda (A1 = 5.1a … A5 = 5.1e).
- **Clase del ciclo.** Clase del punto óptimo.
- **Índice de cercanía D [–].** D del punto (0 = cumple los criterios operativos).
- **Eficiencia térmica del ciclo, η [%].** η del ciclo.
- **Trabajo neto, W_net [kW] (m_b = 1 kg/s).** Trabajo neto por kg/s de mezcla base.
- **Temperatura de la fuente, T_fuente [K].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Temperatura del sumidero, T_sumidero [K].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Presión de alta, P_alta [kPa].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Presión de baja, P_baja [kPa].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Fracción de amoníaco de la mezcla base, x_b [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Eficiencia isentrópica de la turbina, η_t [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Eficiencia isentrópica de la bomba, η_p [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Efectividad del generador de vapor, ε_HRVG [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Efectividad del regenerador, ε_reg [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Efectividad del condensador, ε_cond [–].** Valor de la variable en ese punto (la columna lleva su unidad).
- **Margen O1 [–].** q4 − 0.90.
- **Margen O2 [K].** T_burbuja − T de entrada a la bomba.
- **Margen O5 [–].** Margen del separador (distancia de q2 al borde del intervalo bifásico).
- **Fuera de rango.** Puntos con estados fuera del rango validado de propiedades (p. ej. líquido por encima de 420 K); su η se toma con cautela.
- **B verificado.** Si pasó la verificación B: el motor real recalcula la entalpía isentrópica h4s y el punto queda marcado como no verificado si |Δh4s| > 2.0 kJ/kg (se señala, no se reclasifica).
- **Iteraciones.** Pasos de bisección usados.
- **Evaluaciones.** Evaluaciones usadas por la búsqueda.

*Lectura:* 5.1a 14.98 %, 5.1b 15.48 %, 5.1c 12.74 %, **5.1d 15.60 %**, 5.1e 11.09 %. En KALINA confiables
dentro de cada búsqueda: 98 de 102, 63 de 63, 90 de 91, 80 de 80 y **0 de 83** (5.1e).

**Tabla 5.1-2 — Corridas por parte y clase.**

| Parte | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| 5.1a · libre, desde el mejor de 3.2 | 117 | 0 | 117 | 102 | 98 | 15 | 0 | 0 | 0 | 6 |
| 5.1b · libre, desde el mejor de 2.4 | 105 | 0 | 104 | 63 | 63 | 41 | 0 | 1 | 0 | 6 |
| 5.1c · conserva sus temperaturas | 112 | 0 | 105 | 91 | 90 | 14 | 0 | 7 | 0 | 1 |
| 5.1d · conserva sus presiones y su clima | 113 | 0 | 113 | 80 | 80 | 33 | 0 | 0 | 0 | 7 |
| 5.1e · conserva su fuente y su x_b | 113 | 0 | 110 | 83 | 0 | 27 | 0 | 2 | 1 | 111 |

*Tabla 5.1-2 · hoja «5.1-2 Corridas por parte y por» · 5 filas.*

### Figuras

**Figura 5.1-1.**

> **Figura 5.1-1. La búsqueda llega a η = 15.6 % dentro de la región KALINA (equipos a 0.95).**
> Estudio 5.1 · partes 5.1a … 5.1e (figura de síntesis: cada línea es un arranque con sus propios datos conservados).
> 5.1a · libre (desde el mejor de 3.2).
> 5.1b · libre (desde el mejor de 2.4).
> 5.1c · conserva sus temperaturas.
> 5.1d · conserva sus presiones y su clima.
> 5.1e · conserva su fuente y su x_b (fuera de rango).
> Filtro: líneas = pasos aceptados de cada búsqueda (cada uno es KALINA genuino, D = 0); puntos grises = evaluaciones que no se aceptaron.
> n = 550 evaluaciones (41 pasos aceptados y 509 no aceptados; las evaluaciones sin η no se dibujan). Fuente: m7_trayectorias.csv y m7_evaluaciones.csv.

*Cómo se lee:* η (vertical) contra la iteración de la búsqueda (horizontal); una línea por arranque (la
trayectoria aceptada) y, debajo, **puntos grises** = evaluaciones que no se aceptaron. Las líneas suben
porque cada paso aceptado mejora η.

### Dónde verlo en el Excel
`5.1-1`, `5.1-2`, `5.1-3`, `5.1-R`, `5 Gráficos`.

### Qué dice y qué no dice
- **Dice:** conservando las temperaturas (5.1c) se llega a 12.7 % **con KALINA confiables**, pero a costa de
  P_alta = 5000 kPa, P_baja ~1360 kPa y x_b = 0.85: la fuente de 623 K sí admite confiables, solo lejos del
  enunciado. **El arranque 5.1e queda fuera del rango confiable:** su 11.1 % no es un resultado de diseño.
- **Límites:** es una búsqueda local (puede haber óptimos mejores no visitados); los óptimos terminan en los
  bordes de la caja (eficiencias en 0.95) y al filo de O2; con 2 K de margen, η baja ~0.5 pp en 5.1d.
- **Cómo reportarlo:** «8–11 % con eficiencias medias; hasta ~15 % con equipos de alta eficiencia».

> **Cómo explicarlo (30 s):** *«La mejor eficiencia que encontré es 15.6 %, con las presiones del profesor y
> equipos al 95 %. Es un techo teórico. Con equipos medios, lo esperable es 8 a 11 %.»*

---

## R10. Los resultados son confiables, con una salvedad: no hay margen de cavitación

**Pregunta:** ¿se puede confiar en el modelo y en las conclusiones?

**Resultado:** verificado, no validado. teqp y el motor real coinciden (en 5 puntos); el modelo reproduce los KALINA de la planta real de
Húsavík; el código reproduce al profesor (reproduce el fallo); y los rankings son estables.

### Qué se hizo
- **Motor real contra teqp (6.1, 4.3):** comparación punto a punto de clase, η y márgenes.
- **Húsavík (6.2a):** re-evaluación de los 97 KALINA de septiembre (Fase 3) con el código actual.
- **Reproducibilidad (1.1):** 41 de 41 de la Fase 1.
- **Robustez (3.2):** convergencia del ranking, bootstrap, PAWN, CART.

### Tablas

**Tabla 6.1-3 — Paridad teqp contra el motor real (12 puntos).**

| Identificador | Origen | Clase con teqp | Clase con el motor real | Coincide la clase | η con teqp [%] | η con el motor real [%] | Δη [pp] | Dentro de la banda |
|---|---|---|---|---|---|---|---|---|
| P01 | Ancla A* | KALINA | NO_CONVERGIO | no | 8.482 | — | — | — |
| P02 | estudios 2.1 y 2.2, mayor η | KALINA | NO_CONVERGIO | no | 9.15 | — | — | — |
| P03 | estudio 4.2, presiones del profesor, techo | KALINA | KALINA | sí | 10.807 | 10.807 | 0 | sí |
| P04 | estudio 4.2, presiones del profesor, ε_cond mínima | KALINA | NO_CONVERGIO | no | 2.539 | — | — | — |
| P05 | estudio 5.1, óptimo A1 | KALINA | NO_CONVERGIO | no | 14.978 | — | — | — |
| P06 | estudio 5.1, óptimo A2 | KALINA | NO_CONVERGIO | no | 15.482 | — | — | — |
| P07 | estudio 5.1, óptimo A3 | KALINA | NO_CONVERGIO | no | 12.739 | — | — | — |
| P08 | estudio 5.1, óptimo A4 | KALINA | KALINA | sí | 15.6 | 15.6 | 0 | sí |
| P09 | estudio 5.1, óptimo A5 | KALINA | NO_CONVERGIO | no | 11.094 | — | — | — |
| P10 | estudio 3.2, top 1 | KALINA | NO_CONVERGIO | no | 12.302 | — | — | — |
| P11 | estudio 3.3, mayor P_baja KALINA | KALINA | NO_CONVERGIO | no | 2.669 | — | — | — |
| P12 | estudio 2.3, fuente del profesor | KALINA | NO_CONVERGIO | no | 6.271 | — | — | — |

*Tabla 6.1-3 · hoja «6.1-3 Paridad teqp contra el mo» · 12 filas.*

Columnas:
- **Identificador.** Etiqueta del punto de control (P01…P12; A*, A4, HUS).
- **Origen.** Estudio y punto del que viene (P01…P12).
- **Clase con teqp.** Clase con el motor rápido (teqp).
- **Clase con el motor real.** Clase con el motor de referencia (AmmoniaWaterAdapter, más lento y riguroso).
- **Coincide la clase.** Si ambos motores dan la misma clase.
- **η con teqp [%].** Eficiencia con teqp.
- **η con el motor real [%].** Eficiencia con el motor de referencia (vacía si se cortó por tiempo).
- **Δη [pp].** η con el motor real − η con teqp, en puntos porcentuales.
- **Dentro de la banda.** Si |Δη| queda dentro de la banda de incertidumbre (±0.7 pp).
- **Margen O1 con teqp [–].** q4 − 0.90 con teqp (positivo = cumple).
- **Margen O1 con el motor real [–].** Ídem con el motor de referencia.
- **Margen O2 con teqp [K].** T_burbuja − T de entrada a la bomba con teqp (positivo = cumple).
- **Margen O2 con el motor real [K].** Ídem con el motor de referencia.
- **Fuera de rango.** Puntos con estados fuera del rango validado de propiedades (p. ej. líquido por encima de 420 K); su η se toma con cautela.
- **B verificado.** Si pasó la verificación B: el motor real recalcula la entalpía isentrópica h4s y el punto queda marcado como no verificado si |Δh4s| > 2.0 kJ/kg (se señala, no se reclasifica).

*Lectura:* con 300 s, solo **2 de 12** terminan en el motor real (P03 de 4.2, η 10.81 %, y P08, el óptimo 5.1d,
η 15.60 %): ambos coinciden con teqp (misma clase, |Δη| < 0.001 pp). Los otros 10 se cortan **por tiempo, no
por la física**. Con 1500 s (Tabla 4.3-4), A\*, el óptimo 5.1d y Húsavík coinciden (Δη ≤ 0.003 pp).

**Tabla 6.2-3 — Catálogo Húsavík (reproducción de la Fase 3).**

| Familia | Origen | Variables movidas | Piso de O2 [K] | N | KALINA (septiembre) | KALINA (ahora) | Confiables ahora | Coincide | \|Δη\| medio [pp] | \|Δη\| máximo [pp] |
|---|---|---|---|---|---|---|---|---|---|---|
| F3-A | sept | P_alta, P_baja, x_b, eta_t, eps_reg, eps_cond | 303.55 | 14 | 14 | 14 | 14 | 14 | 0 | 0 |
| F3-B | sept | P_baja, eps_reg, eps_cond | 283.15 | 27 | 27 | 27 | 27 | 27 | 0 | 0 |
| F3-C | sept | P_baja x eps_reg | 283.15 | 24 | 24 | 24 | 24 | 24 | 0 | 0 |
| F3-D | sept | una variable por archivo (P_baja, eps_cond, eps_reg, eta_t, x_b) | 283.15 | 26 | 26 | 26 | 26 | 26 | 0 | 0 |
| F3-E | sept | una variable por archivo (P_alta, P_baja, x_b) | 303.55 | 6 | 6 | 6 | 6 | 6 | 0 | 0 |
| B1-T_fuente | nuevo | T_fuente | 283.15 | 15 | — | 7 | 7 | — | — | — |
| B1-T_sumidero | nuevo | T_sumidero | 283.15 | 15 | — | 8 | 8 | — | — | — |
| B1-P_alta | nuevo | P_alta | 283.15 | 15 | — | 12 | 12 | — | — | — |
| B1-P_baja | nuevo | P_baja | 283.15 | 15 | — | 11 | 11 | — | — | — |
| B1-x_b | nuevo | x_b | 283.15 | 15 | — | 9 | 9 | — | — | — |
| B1-eta_t | nuevo | η_t | 283.15 | 15 | — | 15 | 15 | — | — | — |
| B1-eta_p | nuevo | η_p | 283.15 | 15 | — | 15 | 15 | — | — | — |
| B1-eps_hrvg | nuevo | ε_HRVG | 283.15 | 15 | — | 14 | 14 | — | — | — |
| B1-eps_reg | nuevo | ε_reg | 283.15 | 15 | — | 15 | 15 | — | — | — |
| B1-eps_cond | nuevo | ε_cond | 283.15 | 15 | — | 1 | 1 | — | — | — |
| B2 | nuevo | x_b x P_baja | 283.15 | 64 | — | 49 | 49 | — | — | — |

*Tabla 6.2-3 · hoja «6.2-3 Catálogo Húsavík (reprodu» · 16 filas.*

Columnas:
- **Familia.** Familia de puntos de Húsavík (F3-A…F3-E de septiembre; B1, B2 nuevas) o, en S-1, familia de método del estudio.
- **Origen.** «sept» = punto de la Fase 3 de septiembre; «nuevo» = barrido nuevo de esta campaña.
- **Variables movidas.** Variables que se mueven en la familia.
- **Piso de O2 [K].** Temperatura con que se evalúa la cavitación.
- **N.** Cantidad de puntos usados (n).
- **KALINA (septiembre).** KALINA que tenía la familia en septiembre.
- **KALINA (ahora).** KALINA con el código actual.
- **Confiables ahora.** Cuántos de ellos son confiables.
- **Coincide.** Cuántos mantienen la clase de septiembre.
- **|Δη| medio [pp].** Diferencia media de η con septiembre.
- **|Δη| máximo [pp].** Diferencia máxima de η con septiembre.

*Lectura:* en las cinco familias de septiembre (F3-A a F3-E) **97 de 97 siguen siendo KALINA, ninguno cambia
de clase** y |Δη| < 10⁻¹¹ pp; **83 son confiables** (los otros 14 usan η_t o ε_cond > 0.95, tope del
proyecto). Las filas «nuevo» (B1-…, B2) son los barridos de 6.2b y 6.2c.

**Tabla 1.1-3** — reproducibilidad (ver R1).

### Figuras

**Figura 6.1-1 — paridad teqp contra motor real.**

> **Figura 6.1-1. teqp y el motor real coinciden en los 5 puntos que el motor real resolvió.**
> Estudio 6.1 · partes 6.1a y 6.1d (puntos de control, cada uno con sus propios datos, no comparables entre sí).
> Puntos: P03 = estudio 4.2, presiones del profesor, techo; P08 = estudio 5.1, óptimo A4; A* = Ancla A*; A4 = Óptimo A4 de estudio 5.1; HUS = Base de Húsavík.
> Sin η real (motor real cortado por el límite de 300 s, no por la física): P01, P02, P04, P05, P06, P07, P09, P10, P11, P12.
> Filtro: pares con η de ambos motores. Marcas: recta 1:1 y banda ±0.7 pp (incertidumbre del modelo de propiedades).
> n = 5. Fuente: m6_comparacion.csv y m9_motor_real.csv.

*Cómo se lee:* η con teqp (horizontal) contra η con el motor real (vertical). **Si un punto cae sobre la
recta 1:1, los dos motores coinciden**; la banda verde es ±0.7 pp. Hay 5 puntos con η real (2 con 300 s,
azules; 3 con 1500 s, verdes); los otros no tienen η real y no se dibujan. Esta figura toma datos de **dos
tablas** (6.1-3 y 4.3-4), por eso está junto a ambas en el Excel.

### Dónde verlo en el Excel
`6.1-1` a `6.1-4`, `6.2-1` a `6.2-5`, `4.3-4`, `1.1-3`, `6 Gráficos`.

### Robustez
| Prueba | Resultado | Lectura |
|---|---|---|
| Convergencia del ranking (300 → 500) | ρ de Spearman 0.93 (KS) y 0.99 (PRCC) | rankings estables |
| Significancia con 10 pruebas | 6 de 10 PRCC sobre η con p < 10⁻⁵ | sobreviven a Bonferroni (α = 0.005) |
| PAWN sobre η | P_baja 0.44, P_alta 0.42, η_t 0.30, T_fuente 0.27 | mismo grupo líder que el PRCC |
| Motor | teqp = motor real (Δη < 0.003 pp) | no depende del motor |
| Reproducibilidad | 41/41 (Fase 1) y 97/97 (Húsavík) | el código reproduce lo anterior |
| Banda de η | ±0.4–0.7 pp | no se concluye sobre diferencias menores |

### Qué dice y qué no dice
- **Dice:** los resultados no dependen del motor de propiedades; el modelo es coherente con una planta real (sin potencia medida),
  incluida su P_baja (690 kPa = su mínima KALINA).
- **Salvedad:** los diseños están al filo de la cavitación (R6).
- **Límites:** el motor real necesita ~1500 s por punto y solo confirmó 5; no corre la verificación B; 6.2b y
  6.2c solo con teqp; solo se re-evaluaron los KALINA de septiembre (no los corregibles); 14 de los 97 de
  septiembre usan η_t hasta 0.98 y ε_cond hasta 0.99, por encima del tope del proyecto.

> **Cómo explicarlo (30 s):** *«Verifiqué con dos motores de propiedades y dan lo mismo; reproduje los 97
> diseños de la planta real de Húsavík, incluida su presión de baja (sin validación experimental). Lo único delicado es que todos los
> diseños están pegados a la cavitación.»*

---

## R11. Visión de conjunto: la síntesis de toda la campaña

### Tabla S-1 — Resumen por estudio

| Estudio | Nombre | Familia | Partes | Punto base | Diseño | Corridas | Genuinas | KALINA | KALINA confiables | Falsos convergidos | Criterio que más bloquea |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Repetir el caso del profesor | R | 1.1a, 1.1b, 1.1c, 1.1d | PP | una variable a la vez sobre PP | 42 | 0 | 0 | 0 | 0 | — |
| 2.1 | Un solo cambio | F | 2.1 | PP | malla 10 + bisección | 132 | 15 | 0 | 0 | 21 | O2 (15 de 15) |
| 2.2 | Dos cambios | F | 2.2a, 2.2b | PP | malla 2D + bisección | 180 | 165 | 59 | 48 | 12 | O2 (106 de 106) |
| 2.3 | Dos cambios con η y ε en 0.40–0.95 | F | 2.3a, 2.3b, 2.3c, 2.3d | PP | mallas + bisección | 225 | 154 | 20 | 1 | 4 | O2 (134 de 134) |
| 2.4 | Sumidero más frío | F | 2.4a, 2.4b, 2.4c, 2.4d | 4 bases | malla 2D + bisección | 320 | 269 | 153 | 119 | 0 | O2 (116 de 116) |
| 3.1 | Sensibilidad local alrededor de A* | L | 3.1 | A* | OAT 15 + A* ± 1 % | 171 | 148 | 86 | 86 | 6 | O2 (61 de 62) |
| 3.2 | Sensibilidad global (500 puntos) | G | 3.2 | caja | LHS | 500 | 452 | 121 | 83 | 13 | O2 (324 de 331) |
| 3.3 | P_baja alta (1500–2500 kPa) | G | 3.3 | caja | LHS | 150 | 120 | 75 | 45 | 6 | O2 (44 de 45) |
| 4.1 | Escenarios de conservación | C | 4.1a, 4.1b, 4.1c, 4.1d, 4.1e | PP parcial | LHS por escenario | 600 | 382 | 20 | 2 | 12 | O2 (362 de 362) |
| 4.2 | Mapa con las presiones del profesor | C | 4.2 | PP con PA y PB | malla 11×5×3 | 165 | 149 | 104 | 104 | 15 | O2 (30 de 45) |
| 6.1 | Verificación con el motor de referencia | V | 6.1a, 6.1b, 6.1c | puntos clave | puntos de control | 167 | 151 | 142 | 137 | 0 | O2 (9 de 9) |
| 5.1 | Búsqueda de la η máxima | O | 5.1a, 5.1b, 5.1c, 5.1d, 5.1e | 5 arranques | búsqueda por patrones | 560 | 549 | 419 | 331 | 1 | O2 (114 de 130) |
| 4.3 | Escalera de conservación | C | 20 partes (ver tabla de condiciones) | PP parcial | selección hacia adelante + LHS | 987 | 806 | 181 | 118 | 29 | O2 (613 de 625) |
| 6.2 | Planta real de Húsavík | H | 6.2a, 6.2b, 6.2c, 6.2d | ancla de Húsavík | recorrida + OFAT + malla | 382 | 347 | 282 | 268 | 16 | O2 (65 de 65) |

*Tabla S-1 · hoja «S-1 Resumen por estudio» · 14 filas.*

Columnas:
- **Estudio.** Estudio (N.M).
- **Nombre.** Nombre del estudio.
- **Familia.** Familia de método del estudio: R reproducibilidad, F factibilidad, L local, G global, C conservación, V verificación, O optimización, H caso real.
- **Partes.** Partes del estudio.
- **Punto base.** Punto del que parte el barrido (PP, A*, caja…).
- **Diseño.** Diseño del barrido (malla, OAT, LHS, búsqueda…).
- **Corridas.** Puntos calculados en la parte.
- **Genuinas.** Corridas genuinas.
- **KALINA.** Puntos que cumplen todos los criterios.
- **KALINA confiables.** KALINA dentro del rango validado de propiedades (IAPWS G4-01) y con η y ε entre 0.40 y 0.95.
- **Falsos convergidos.** El solver dijo que convergió pero el clasificador lo descartó (solución espuria); no cuentan como genuinos.
- **Criterio que más bloquea.** Criterio que más falla en esa fila.

*Lectura:* 14 estudios y 4 581 corridas (21 omitidas; 4 560 evaluadas), sin el anexo A.1. KALINA por estudio:
2.2 (59), 2.3 (20), 2.4 (153), 3.1 (86), 3.2 (121), 3.3 (75), 4.1 (20), 4.2 (104), 4.3 (181), 5.1 (419), 6.1
(142) y 6.2 (282); en total 1 662.

### Tabla S-2 — Qué se movió en cada barrido
Matriz parte × variable (58 filas): «barrido: …» en azul, «fijo: profesor» en gris y «fijo: otro valor» en
naranja. Sirve para **no comparar partes con datos distintos**. Columnas: una por variable más el piso de O2 y
el motor.

### Tabla S-3 — Rangos KALINA comparados
Para cada parte, p5, mediana y p95 de P_alta, P_baja, ΔP, r_P, T_fuente y x_b entre los KALINA confiables.

| Estudio | Parte | Datos fijos | Variable | n KALINA confiables | p5 | Mediana | p95 |
|---|---|---|---|---|---|---|---|
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Presión de alta, P_alta [kPa] | 83 | 2161.456 | 3558.443 | 4906.739 |
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Presión de baja, P_baja [kPa] | 83 | 681.278 | 1152.816 | 1464.452 |
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Diferencia de presiones, ΔP [kPa] | 83 | 972.657 | 2528.97 | 3761.484 |
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Razón de presiones, r_P [–] | 83 | 1.712 | 3.211 | 6.197 |
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Temperatura de la fuente, T_fuente [K] | 83 | 382.467 | 409.355 | 455.278 |
| estudio 3.2 | 3.2 | Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp. | Fracción de amoníaco de la mezcla base, x_b [–] | 83 | 0.515 | 0.66 | 0.808 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Presión de alta, P_alta [kPa] | 2 | 3242.441 | 3556.735 | 3871.029 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Presión de baja, P_baja [kPa] | 2 | 1389.86 | 1662.589 | 1935.318 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Diferencia de presiones, ΔP [kPa] | 2 | 1307.123 | 1894.146 | 2481.169 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Razón de presiones, r_P [–] | 2 | 1.694 | 2.252 | 2.811 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Temperatura de la fuente, T_fuente [K] | 2 | 623.15 | 623.15 | 623.15 |
| estudio 4.1 escenario S1 | 4.1a | Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp. | Fracción de amoníaco de la mezcla base, x_b [–] | 2 | 0.719 | 0.771 | 0.824 |

*Tabla S-3 · hoja «S-3 Rangos KALINA comparados» · 34 filas (se muestran 12).*

Columnas:
- **Estudio.** Estudio (N.M).
- **Parte.** Subconjunto del estudio con sus propios datos fijos (p. ej. 2.4a). Solo se comparan puntos de la misma parte.
- **Datos fijos.** Datos que quedan fijos en la parte.
- **Variable.** Dato de entrada (o del modelo) al que se refiere la fila.
- **n KALINA confiables.** Cantidad de KALINA confiables en la parte.
- **p5.** Percentil 5 de la variable entre los KALINA confiables.
- **Mediana.** Valor central del grupo.
- **p95.** Percentil 95 de la variable entre los KALINA confiables.

### Tabla S-4 — Datos del profesor conservables (ver R8)

### Figuras de síntesis
**Figura S-1 — resultado de cada barrido.**

> **Figura S-1. Resultado de cada barrido: puntos por clase.**
> Estudios 1.1 a 6.2 (figura de síntesis: una barra por estudio), sin el anexo A.1.
> Datos fijos: no aplica (figura de síntesis).
> Filtro: todos los puntos menos los de A.1.
> n = 4560. Fuente: todos_los_puntos.csv.

*Cómo se lee:* una barra por estudio (de arriba a abajo, 1.1 a 6.2), apilada por clase (verde KALINA,
naranja corregible, amarillo inviable, rojo no convergió, gris falso convergido). Muestra a la vez el tamaño
de cada estudio y su proporción de KALINA.

**Figura S-2 — qué se movió en cada barrido.** Es la Tabla S-2 con colores (no tiene gráfico aparte).

### Anexo A.1 — equipos fuera del rango realista
η y ε de 0.20 a 0.99 (160 corridas: 90 dentro de [0.40, 0.95] y 70 fuera; 84 KALINA, 60 CORREGIBLE, 7
INVIABLE, 9 sin converger; O2 aparece 66 veces). Es anecdótico: **no entra en las conclusiones, ni en el
tablero ni en las figuras**. Está en la hoja `A.1 Anexo fuera de rango`.

---

# PARTE III — El libro Excel, hoja por hoja

El libro tiene **95 hojas**. Su orden va de lo general a lo particular: portada y guías, síntesis, y luego
cada pregunta con sus tablas, su hoja de resultados, sus gráficos y los datos de sus gráficos; al final, los
datos completos y las hojas auxiliares ocultas.

**Cómo encontrar la gráfica de una tabla.** Cada gráfico está en dos sitios: en la hoja `N Gráficos` (todos
los de la pregunta juntos) y **junto a la tabla de la que salen sus datos**: a la derecha del bloque de su
parte o variable en `N.M-R`, o debajo de su tabla resumen (`3.1-3`, `3.2-4`, `4.3-3`, `4.3-4`, `6.1-3`,
`S-1`). Los números con los que Excel los dibuja están en `N Datos de gráficos`.

| # | Hoja | Filas × columnas | Gráficos | Qué contiene |
|---|---|---|---|---|
| 1 | `LEEME` | 32 × 1 |  | Cómo leer el libro, glosario y colores de clase. |
| 2 | `Nomenclatura` | 25 × 5 |  | Equivalencias entre la numeración nueva (pregunta → estudio → parte) y los códigos antiguos (M05, KF-M05-3, B09-3). |
| 3 | `Tablero` | 904 × 36 | 3 | Selector (celda B2) que cambia cifras, condiciones y tres gráficos según el estudio o la parte elegidos. |
| 4 | `Indice` | 87 × 4 |  | Lista de todas las hojas con vínculo, estudio, partes y qué muestra. |
| 5 | `Punto_profesor` | 14 × 4 |  | Los 11 datos del enunciado y el ancla A* lado a lado. |
| 6 | `S-1 Resumen por estudio` | 52 × 12 | 1 | Tabla S-1: Resumen por estudio. |
| 7 | `S-2 Qué se movió en cada barrid` | 67 × 14 |  | Tabla S-2: Qué se movió en cada barrido. |
| 8 | `S-3 Rangos KALINA comparados` | 43 × 8 |  | Tabla S-3: Rangos KALINA comparados. |
| 9 | `S-4 Datos del profesor conserva` | 20 × 4 |  | Tabla S-4: Datos del profesor conservables. |
| 10 | `S-5 Criterios que bloquean, por` | 23 × 10 |  | Tabla S-5: Criterios que bloquean, por estudio. |
| 11 | `S Gráficos` | 34 × 1 | 1 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 12 | `S Datos de gráficos` | 19 × 6 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 13 | `1.1-1 Condiciones qué quedó fij` | 62 × 7 |  | Tabla 1.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 14 | `1.1-2 Corridas por parte y por` | 14 × 11 |  | Tabla 1.1-2: Corridas por parte y por clase. |
| 15 | `1.1-3 Comparación antes y despu` | 51 × 10 |  | Tabla 1.1-3: Comparación antes y después de la F1. |
| 16 | `1.1-R Resultados por barrido` | 70 × 11 |  | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 17 | `2.1-1 Condiciones qué quedó fij` | 23 × 8 |  | Tabla 2.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 18 | `2.1-2 Corridas por parte y por` | 11 × 11 |  | Tabla 2.1-2: Corridas por parte y por clase. |
| 19 | `2.1-3 Distancia al punto del pr` | 20 × 13 |  | Tabla 2.1-3: Distancia al punto del profesor moviendo una variable a la vez. |
| 20 | `2.1-R Resultados por barrido` | 190 × 12 | 10 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 21 | `2.2-1 Condiciones qué quedó fij` | 40 × 7 |  | Tabla 2.2-1: Condiciones: qué quedó fijo y qué se barrió. |
| 22 | `2.2-2 Corridas por parte y por` | 16 × 11 |  | Tabla 2.2-2: Corridas por parte y por clase. |
| 23 | `2.2-3 Resumen de la malla de do` | 26 × 13 |  | Tabla 2.2-3: Resumen de la malla de dos cambios. |
| 24 | `2.2-R Resultados por barrido` | 197 × 13 | 2 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 25 | `2.3-1 Condiciones qué quedó fij` | 72 × 7 |  | Tabla 2.3-1: Condiciones: qué quedó fijo y qué se barrió. |
| 26 | `2.3-2 Corridas por parte y por` | 24 × 11 |  | Tabla 2.3-2: Corridas por parte y por clase. |
| 27 | `2.3-3 Malla con η y ε en 0.40,` | 41 × 15 |  | Tabla 2.3-3: Malla con η y ε en [0.40, 0.95]. |
| 28 | `2.3-R Resultados por barrido` | 271 × 13 | 8 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 29 | `2.4-1 Condiciones qué quedó fij` | 72 × 7 |  | Tabla 2.4-1: Condiciones: qué quedó fijo y qué se barrió. |
| 30 | `2.4-2 Corridas por parte y por` | 24 × 11 |  | Tabla 2.4-2: Corridas por parte y por clase. |
| 31 | `2.4-3 Malla T_sumidero x P_baja` | 40 × 13 |  | Tabla 2.4-3: Malla T_sumidero x P_baja por base. |
| 32 | `2.4-R Resultados por barrido` | 351 × 13 | 2 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 33 | `2 Gráficos` | 273 × 1 | 22 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 34 | `2 Datos de gráficos` | 63 × 107 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 35 | `3.1-1 Condiciones qué quedó fij` | 23 × 8 |  | Tabla 3.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 36 | `3.1-2 Corridas por parte y por` | 11 × 11 |  | Tabla 3.1-2: Corridas por parte y por clase. |
| 37 | `3.1-3 Influencia y margen por v` | 72 × 10 | 2 | Tabla 3.1-3: Influencia y margen por variable (Δη y O2). |
| 38 | `3.1-R Resultados por barrido` | 231 × 12 | 11 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 39 | `3.2-1 Condiciones qué quedó fij` | 36 × 7 |  | Tabla 3.2-1: Condiciones: qué quedó fijo y qué se barrió. |
| 40 | `3.2-2 Corridas por parte y por` | 12 × 11 |  | Tabla 3.2-2: Corridas por parte y por clase. |
| 41 | `3.2-3 Separación KALINA  no KAL` | 62 × 11 |  | Tabla 3.2-3: Separación KALINA / no KALINA (RSA y KS). |
| 42 | `3.2-4 Influencia de cada variab` | 76 × 8 | 1 | Tabla 3.2-4: Influencia de cada variable sobre η (PRCC). |
| 43 | `3.2-5 Rangos de presión de los` | 18 × 10 |  | Tabla 3.2-5: Rangos de presión de los KALINA. |
| 44 | `3.2-6 Ventana KALINA por franja` | 16 × 13 |  | Tabla 3.2-6: Ventana KALINA por franjas de P_alta. |
| 45 | `3.2-7 Ventana KALINA por franja` | 16 × 13 |  | Tabla 3.2-7: Ventana KALINA por franjas de T_fuente. |
| 46 | `3.2-8 Ventana KALINA por franja` | 14 × 13 |  | Tabla 3.2-8: Ventana KALINA por franjas de T_sumidero. |
| 47 | `3.2-R Resultados por barrido` | 510 × 22 | 13 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 48 | `3.3-1 Condiciones qué quedó fij` | 23 × 7 |  | Tabla 3.3-1: Condiciones: qué quedó fijo y qué se barrió. |
| 49 | `3.3-2 Corridas por parte y por` | 11 × 11 |  | Tabla 3.3-2: Corridas por parte y por clase. |
| 50 | `3.3-3 Techo de P_baja antes de` | 22 × 8 |  | Tabla 3.3-3: Techo de P_baja antes de cortar KALINA. |
| 51 | `3.3-4 Techo de P_baja por franj` | 16 × 7 |  | Tabla 3.3-4: Techo de P_baja por franja de P_alta. |
| 52 | `3.3-R Resultados por barrido` | 145 × 22 | 1 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 53 | `3 Gráficos` | 329 × 1 | 28 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 54 | `3 Datos de gráficos` | 336 × 166 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 55 | `4.1-1 Condiciones qué quedó fij` | 88 × 7 |  | Tabla 4.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 56 | `4.1-2 Corridas por parte y por` | 28 × 11 |  | Tabla 4.1-2: Corridas por parte y por clase. |
| 57 | `4.1-3 Resumen por escenario de` | 28 × 19 |  | Tabla 4.1-3: Resumen por escenario de conservación. |
| 58 | `4.1-4 Rangos por escenario (KAL` | 81 × 11 |  | Tabla 4.1-4: Rangos por escenario (KALINA contra no KALINA). |
| 59 | `4.1-R Resultados por barrido` | 632 × 20 | 5 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 60 | `4.2-1 Condiciones qué quedó fij` | 23 × 7 |  | Tabla 4.2-1: Condiciones: qué quedó fijo y qué se barrió. |
| 61 | `4.2-2 Corridas por parte y por` | 11 × 11 |  | Tabla 4.2-2: Corridas por parte y por clase. |
| 62 | `4.2-3 Frontera KALINA con las p` | 25 × 7 |  | Tabla 4.2-3: Frontera KALINA con las presiones del profesor. |
| 63 | `4.2-R Resultados por barrido` | 175 × 14 | 3 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 64 | `4.3-1 Condiciones qué quedó fij` | 289 × 7 |  | Tabla 4.3-1: Condiciones: qué quedó fijo y qué se barrió. |
| 65 | `4.3-2 Corridas por parte y por` | 49 × 11 |  | Tabla 4.3-2: Corridas por parte y por clase. |
| 66 | `4.3-3 Escalera de conservación` | 72 × 11 | 1 | Tabla 4.3-3: Escalera de conservación de datos del profesor. |
| 67 | `4.3-4 Verificación teqp contra` | 40 × 23 | 1 | Tabla 4.3-4: Verificación teqp contra el motor real. |
| 68 | `4.3-R Resultados por barrido` | 1107 × 17 |  | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 69 | `4 Gráficos` | 196 × 1 | 9 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 70 | `4 Datos de gráficos` | 63 × 92 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 71 | `5.1-1 Condiciones qué quedó fij` | 88 × 7 |  | Tabla 5.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 72 | `5.1-2 Corridas por parte y por` | 28 × 11 |  | Tabla 5.1-2: Corridas por parte y por clase. |
| 73 | `5.1-3 Óptimos de η por arranque` | 28 × 22 |  | Tabla 5.1-3: Óptimos de η por arranque. |
| 74 | `5.1-R Resultados por barrido` | 594 × 22 | 1 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 75 | `5 Gráficos` | 32 × 1 | 1 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 76 | `5 Datos de gráficos` | 514 × 12 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 77 | `6.1-1 Condiciones qué quedó fij` | 48 × 7 |  | Tabla 6.1-1: Condiciones: qué quedó fijo y qué se barrió. |
| 78 | `6.1-2 Corridas por parte y por` | 12 × 11 |  | Tabla 6.1-2: Corridas por parte y por clase. |
| 79 | `6.1-3 Paridad teqp contra el mo` | 49 × 15 | 1 | Tabla 6.1-3: Paridad teqp contra el motor real. |
| 80 | `6.1-4 Costo del subenfriamiento` | 25 × 14 |  | Tabla 6.1-4: Costo del subenfriamiento. |
| 81 | `6.1-R Resultados por barrido` | 189 × 18 |  | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 82 | `6.2-1 Condiciones qué quedó fij` | 85 × 8 |  | Tabla 6.2-1: Condiciones: qué quedó fijo y qué se barrió. |
| 83 | `6.2-2 Corridas por parte y por` | 25 × 11 |  | Tabla 6.2-2: Corridas por parte y por clase. |
| 84 | `6.2-3 Catálogo Húsavík (reprodu` | 26 × 11 |  | Tabla 6.2-3: Catálogo Húsavík (reproducción de la Fase 3). |
| 85 | `6.2-4 Rangos KALINA por variabl` | 20 × 8 |  | Tabla 6.2-4: Rangos KALINA por variable (Húsavík OFAT). |
| 86 | `6.2-5 Frontera KALINA al variar` | 19 × 4 |  | Tabla 6.2-5: Frontera KALINA al variar x_b (Húsavík, x_b bajo). |
| 87 | `6.2-R Resultados por barrido` | 506 × 16 | 12 | Todos los puntos del estudio, un bloque por barrido (y por variable); con sus gráficos a la derecha. |
| 88 | `6 Gráficos` | 150 × 1 | 13 | Gráficos nativos de Excel de la pregunta, con su título arriba y su pie abajo. |
| 89 | `6 Datos de gráficos` | 75 × 67 |  | Los números con los que Excel dibuja cada gráfico de la pregunta, un bloque por figura. |
| 90 | `A.1 Anexo fuera de rango` | 9 × 2 |  | Conteo por clase del anexo (η y ε de 0.20 a 0.99); no entra en las conclusiones. |
| 91 | `Datos` | 4582 × 31 |  | Tabla canónica: un punto por fila (4 560), con sus 10 variables, clase, η, W_net, ΔP, r_P y códigos de falla; con filtros. |
| 92 | `Condiciones` | 768 × 15 |  | Qué quedó fijo y qué se barrió, por parte y variable (insumo del Tablero). |
| 93 | `Partes` | 52 × 8 |  | Lista de partes con sus datos fijos y diferencias internas. |
| 94 | `Aux_tablero` *(oculta)* | 33 × 51 |  | Hoja oculta: listas y fórmulas que alimentan el Tablero. |
| 95 | `Aux_puntos` *(oculta)* | 309 × 400 |  | Hoja oculta: puntos ordenados por parte para los gráficos del Tablero. |

---

# PARTE IV — Catálogo de tablas

Las 58 tablas, con su hoja, fuente, filtro y columnas. Las tablas `N.M-1` (condiciones) y `N.M-2` (corridas
por parte y por clase) tienen siempre las mismas columnas, definidas en R1.

#### Tabla 1.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `1.1-1 Condiciones qué quedó fij` · **Filas:** 52 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 1.1-2 · Corridas por parte y por clase
- **Hoja:** `1.1-2 Corridas por parte y por` · **Filas:** 4 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 2.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `2.1-1 Condiciones qué quedó fij` · **Filas:** 13 · **Columnas:** 8
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor en el punto base*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 2.1-2 · Corridas por parte y por clase
- **Hoja:** `2.1-2 Corridas por parte y por` · **Filas:** 1 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 2.2-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `2.2-1 Condiciones qué quedó fij` · **Filas:** 26 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 2.2-2 · Corridas por parte y por clase
- **Hoja:** `2.2-2 Corridas por parte y por` · **Filas:** 2 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 2.3-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `2.3-1 Condiciones qué quedó fij` · **Filas:** 52 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 2.3-2 · Corridas por parte y por clase
- **Hoja:** `2.3-2 Corridas por parte y por` · **Filas:** 4 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 2.4-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `2.4-1 Condiciones qué quedó fij` · **Filas:** 52 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 2.4-2 · Corridas por parte y por clase
- **Hoja:** `2.4-2 Corridas por parte y por` · **Filas:** 4 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 3.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `3.1-1 Condiciones qué quedó fij` · **Filas:** 13 · **Columnas:** 8
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor en el punto base*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 3.1-2 · Corridas por parte y por clase
- **Hoja:** `3.1-2 Corridas por parte y por` · **Filas:** 1 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 3.2-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `3.2-1 Condiciones qué quedó fij` · **Filas:** 26 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 3.2-2 · Corridas por parte y por clase
- **Hoja:** `3.2-2 Corridas por parte y por` · **Filas:** 2 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 3.3-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `3.3-1 Condiciones qué quedó fij` · **Filas:** 13 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 3.3-2 · Corridas por parte y por clase
- **Hoja:** `3.3-2 Corridas por parte y por` · **Filas:** 1 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 4.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `4.1-1 Condiciones qué quedó fij` · **Filas:** 65 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 4.1-2 · Corridas por parte y por clase
- **Hoja:** `4.1-2 Corridas por parte y por` · **Filas:** 5 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 4.2-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `4.2-1 Condiciones qué quedó fij` · **Filas:** 13 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 4.2-2 · Corridas por parte y por clase
- **Hoja:** `4.2-2 Corridas por parte y por` · **Filas:** 1 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 6.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `6.1-1 Condiciones qué quedó fij` · **Filas:** 39 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 6.1-2 · Corridas por parte y por clase
- **Hoja:** `6.1-2 Corridas por parte y por` · **Filas:** 3 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 5.1-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `5.1-1 Condiciones qué quedó fij` · **Filas:** 65 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 5.1-2 · Corridas por parte y por clase
- **Hoja:** `5.1-2 Corridas por parte y por` · **Filas:** 5 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 4.3-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `4.3-1 Condiciones qué quedó fij` · **Filas:** 260 · **Columnas:** 7
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 4.3-2 · Corridas por parte y por clase
- **Hoja:** `4.3-2 Corridas por parte y por` · **Filas:** 20 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 6.2-1 · Condiciones: qué quedó fijo y qué se barrió
- **Hoja:** `6.2-1 Condiciones qué quedó fij` · **Filas:** 65 · **Columnas:** 8
- **Fuente:** `analisis_final/00_inventario/condiciones_por_subcaso.csv` · **Filtro:** cada parte y cada variable
- **Columnas:** *Parte*; *Variable*; *Estado*; *Valor en el punto base*; *Valor o rango*; *n valores*; *¿Igual al profesor?*; *Unidad*

#### Tabla 6.2-2 · Corridas por parte y por clase
- **Hoja:** `6.2-2 Corridas por parte y por` · **Filas:** 5 · **Columnas:** 11
- **Fuente:** `analisis_final/00_inventario/conteo_por_subcaso.csv` · **Filtro:** conteo por parte
- **Columnas:** *Parte*; *Corridas*; *Omitidos*; *Genuinos*; *KALINA*; *KALINA confiables*; *Corregibles*; *Inviables*; *No convergidos*; *Falsos convergidos*; *Fuera de rango*

#### Tabla 1.1-3 · Comparación antes y después de la F1
- **Hoja:** `1.1-3 Comparación antes y despu` · **Filas:** 41 · **Columnas:** 10
- **Fuente:** `resultados/2026-10-06_final_M1/m1_comparacion.csv` · **Filtro:** sin filtro (comparación punto a punto)
- **Columnas:** *Grupo*; *Valor*; *Clase (antes)*; *Clase (ahora)*; *Misma clase*; *η (antes) [%]*; *η (ahora) [%]*; *Δη [pp]*; *Mensaje (antes)*; *Mensaje (ahora)*

#### Tabla 2.1-3 · Distancia al punto del profesor moviendo una variable a la vez
- **Hoja:** `2.1-3 Distancia al punto del pr` · **Filas:** 10 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-06_final_M2/m2n1_resumen.csv` · **Filtro:** todos los puntos del barrido OAT
- **Columnas:** *Variable*; *Tipo*; *Convergen*; *KALINA*; *Corregibles*; *Inviables*; *No convergidos*; *Valor convergido más cercano al PP*; *Valor KALINA más cercano al PP*; *d normalizado*; *D mínimo*; *Valor de D mínimo*; *Criterios bloqueantes frecuentes*

#### Tabla 2.2-3 · Resumen de la malla de dos cambios
- **Hoja:** `2.2-3 Resumen de la malla de do` · **Filas:** 12 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-06_final_M2/m2n2_resumen.csv` · **Filtro:** todos los puntos de la malla
- **Columnas:** *Ruta*; *Variable 1*; *Valor 1*; *Genuinos*; *KALINA*; *Falsos convergidos*; *P_baja mínima KALINA [kPa]*; *η mínima KALINA [%]*; *Fuera de rango en la mínima KALINA*; *P_baja mínima con O2 [kPa]*; *D mínimo*; *P_baja del mejor D [kPa]*; *Criterios bloqueantes frecuentes*

#### Tabla 2.3-3 · Malla con η y ε en [0.40, 0.95]
- **Hoja:** `2.3-3 Malla con η y ε en 0.40,` · **Filas:** 21 · **Columnas:** 15
- **Fuente:** `resultados/2026-10-06_final_M2R/m2r_resumen.csv` · **Filtro:** todos los puntos de la malla
- **Columnas:** *Parte*; *Variable 1*; *Valor 1*; *Variable 2*; *Genuinos*; *KALINA*; *Falsos convergidos*; *d menor*; *Valor 1 del d menor*; *Valor 2 del d menor*; *η en el d menor [%]*; *η mayor [%]*; *Valor 1 de la η mayor*; *Valor 2 de la η mayor*; *Bloqueantes*

#### Tabla 2.4-3 · Malla T_sumidero x P_baja por base
- **Hoja:** `2.4-3 Malla T_sumidero x P_baja` · **Filas:** 20 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-06_final_M2S/m2s_resumen.csv` · **Filtro:** todos los puntos de la malla
- **Columnas:** *Base*; *Temperatura del sumidero, T_sumidero [K]*; *Genuinos*; *KALINA*; *Falsos convergidos*; *P_baja mínima KALINA [kPa]*; *η mínima KALINA [%]*; *B verificado en la mínima KALINA*; *Fuera de rango en la mínima KALINA*; *η máxima KALINA [%]*; *P_baja en la η máxima KALINA [kPa]*; *Bloqueantes (genuinos)*; *Códigos de bloqueo*

#### Tabla 3.2-3 · Separación KALINA / no KALINA (RSA y KS)
- **Hoja:** `3.2-3 Separación KALINA  no KAL` · **Filas:** 52 · **Columnas:** 11
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_rsa.csv` · **Filtro:** todos los puntos de la caja M4
- **Columnas:** *Separación*; *Variable*; *n en B (KALINA)*; *n en B̄ (no KALINA)*; *n excluidos*; *KS*; *Valor p*; *IC inferior*; *IC superior*; *Rango favorable, p05*; *Rango favorable, p95*

#### Tabla 3.2-4 · Influencia de cada variable sobre η (PRCC)
- **Hoja:** `3.2-4 Influencia de cada variab` · **Filas:** 40 · **Columnas:** 8
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_prcc.csv` · **Filtro:** todos los puntos de la caja M4
- **Columnas:** *Salida*; *Variable*; *N*; *PRCC*; *t de Student*; *Valor p*; *IC inferior*; *IC superior*

#### Tabla 3.2-5 · Rangos de presión de los KALINA
- **Hoja:** `3.2-5 Rangos de presión de los` · **Filas:** 8 · **Columnas:** 10
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_rangos_presiones.csv` · **Filtro:** todos los KALINA (121, incluidos los fuera de rango) contra los genuinos no KALINA (331)
- **Columnas:** *Variable*; *Grupo*; *N*; *Mínimo*; *Percentil 5*; *Mediana*; *Percentil 95*; *Máximo*; *KS*; *Valor p*

#### Tabla 3.2-6 · Ventana KALINA por franjas de P_alta
- **Hoja:** `3.2-6 Ventana KALINA por franja` · **Filas:** 6 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_ventana_por_palta.csv` · **Filtro:** puntos genuinos de la caja M4
- **Columnas:** *Variable*; *Franja*; *Límite inferior*; *Límite superior*; *N*; *KALINA*; *KALINA [%]*; *P_baja mínima [kPa]*; *P_baja máxima [kPa]*; *ΔP mínima [kPa]*; *ΔP máxima [kPa]*; *r_P mínima [–]*; *r_P máxima [–]*

#### Tabla 3.2-7 · Ventana KALINA por franjas de T_fuente
- **Hoja:** `3.2-7 Ventana KALINA por franja` · **Filas:** 6 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_ventana_por_tfuente.csv` · **Filtro:** puntos genuinos de la caja M4
- **Columnas:** *Variable*; *Franja*; *Límite inferior*; *Límite superior*; *N*; *KALINA*; *KALINA [%]*; *P_baja mínima [kPa]*; *P_baja máxima [kPa]*; *ΔP mínima [kPa]*; *ΔP máxima [kPa]*; *r_P mínima [–]*; *r_P máxima [–]*

#### Tabla 3.2-8 · Ventana KALINA por franjas de T_sumidero
- **Hoja:** `3.2-8 Ventana KALINA por franja` · **Filas:** 4 · **Columnas:** 13
- **Fuente:** `resultados/2026-10-07_final_M4b/m4b_ventana_por_tsumidero.csv` · **Filtro:** puntos genuinos de la caja M4
- **Columnas:** *Variable*; *Franja*; *Límite inferior*; *Límite superior*; *N*; *KALINA*; *KALINA [%]*; *P_baja mínima [kPa]*; *P_baja máxima [kPa]*; *ΔP mínima [kPa]*; *ΔP máxima [kPa]*; *r_P mínima [–]*; *r_P máxima [–]*

#### Tabla 3.3-3 · Techo de P_baja antes de cortar KALINA
- **Hoja:** `3.3-3 Techo de P_baja antes de` · **Filas:** 12 · **Columnas:** 8
- **Fuente:** `resultados/2026-10-07_final_M4c/m4c_techo.csv` · **Filtro:** todos los puntos del barrido de P_baja
- **Columnas:** *Fuente*; *Franja*; *Límite inferior*; *Límite superior*; *N*; *KALINA*; *KALINA [%]*; *P_baja máxima KALINA [kPa]*

#### Tabla 3.3-4 · Techo de P_baja por franja de P_alta
- **Hoja:** `3.3-4 Techo de P_baja por franj` · **Filas:** 6 · **Columnas:** 7
- **Fuente:** `resultados/2026-10-07_final_M4c/m4c_techo_por_palta.csv` · **Filtro:** todos los puntos del barrido de P_baja
- **Columnas:** *Franja*; *Límite inferior*; *Límite superior*; *N*; *KALINA*; *KALINA [%]*; *P_baja máxima KALINA [kPa]*

#### Tabla 4.1-3 · Resumen por escenario de conservación
- **Hoja:** `4.1-3 Resumen por escenario de` · **Filas:** 5 · **Columnas:** 19
- **Fuente:** `resultados/2026-10-07_final_M5/m5_resumen.csv` · **Filtro:** todos los puntos de los escenarios S1 a S5
- **Columnas:** *Escenario*; *N*; *Omitidos*; *Evaluados*; *KALINA*; *Genuinos*; *Falsos convergidos*; *Fuera de rango*; *Factible*; *Criterio bloqueante*; *Veces que bloquea*; *D mínimo*; *Identificador del D mínimo*; *Identificador del más cercano*; *d del más cercano*; *η del más cercano [%]*; *Identificador de la η máxima*; *η máxima [%]*; *Tiempo total [s]*

#### Tabla 4.1-4 · Rangos por escenario (KALINA contra no KALINA)
- **Hoja:** `4.1-4 Rangos por escenario (KAL` · **Filas:** 58 · **Columnas:** 11
- **Fuente:** `resultados/2026-10-07_final_M5/m5_rangos.csv` · **Filtro:** puntos genuinos de los escenarios
- **Columnas:** *Escenario*; *Variable*; *Grupo*; *N*; *Mínimo*; *Percentil 5*; *Mediana*; *Percentil 95*; *Máximo*; *KS*; *Valor p*

#### Tabla 4.2-3 · Frontera KALINA con las presiones del profesor
- **Hoja:** `4.2-3 Frontera KALINA con las p` · **Filas:** 15 · **Columnas:** 7
- **Fuente:** `resultados/2026-10-07_final_M5c/m5c_frontera.csv` · **Filtro:** todos los puntos del barrido
- **Columnas:** *Temperatura del sumidero, T_sumidero [K]*; *Efectividad del condensador, ε_cond [–]*; *KALINA*; *T_fuente mínima [K]*; *T_fuente máxima [K]*; *η en T_fuente mínima [%]*; *η en T_fuente máxima [%]*

#### Tabla 6.1-3 · Paridad teqp contra el motor real
- **Hoja:** `6.1-3 Paridad teqp contra el mo` · **Filas:** 12 · **Columnas:** 15
- **Fuente:** `resultados/2026-10-08_final_M6/m6_comparacion.csv` · **Filtro:** puntos emparejados teqp y motor real
- **Columnas:** *Identificador*; *Origen*; *Clase con teqp*; *Clase con el motor real*; *Coincide la clase*; *η con teqp [%]*; *η con el motor real [%]*; *Δη [pp]*; *Dentro de la banda*; *Margen O1 con teqp [–]*; *Margen O1 con el motor real [–]*; *Margen O2 con teqp [K]*; *Margen O2 con el motor real [K]*; *Fuera de rango*; *B verificado*

#### Tabla 6.1-4 · Costo del subenfriamiento
- **Hoja:** `6.1-4 Costo del subenfriamiento` · **Filas:** 16 · **Columnas:** 14
- **Fuente:** `resultados/2026-10-08_final_M6/m6_subenfriamiento.csv` · **Filtro:** puntos con el subenfriamiento aplicado
- **Columnas:** *Identificador*; *Origen*; *Subenfriamiento, ΔT_sub [K]*; *Alcanzable*; *P_baja original [kPa]*; *P_baja requerida [kPa]*; *ΔP_baja [kPa]*; *η original [%]*; *η requerida [%]*; *Δη [pp]*; *Razón de presiones requerida, r_P [–]*; *Margen O1 requerido [–]*; *Iteraciones*; *Nota*

#### Tabla 5.1-3 · Óptimos de η por arranque
- **Hoja:** `5.1-3 Óptimos de η por arranque` · **Filas:** 5 · **Columnas:** 22
- **Fuente:** `resultados/2026-10-07_final_M7/m7_optimos.csv` · **Filtro:** mejores KALINA de cada arranque
- **Columnas:** *Arranque*; *Clase del ciclo*; *Índice de cercanía D [–]*; *Eficiencia térmica del ciclo, η [%]*; *Trabajo neto, W_net [kW] (m_b = 1 kg/s)*; *Temperatura de la fuente, T_fuente [K]*; *Temperatura del sumidero, T_sumidero [K]*; *Presión de alta, P_alta [kPa]*; *Presión de baja, P_baja [kPa]*; *Fracción de amoníaco de la mezcla base, x_b [–]*; *Eficiencia isentrópica de la turbina, η_t [–]*; *Eficiencia isentrópica de la bomba, η_p [–]*; *Efectividad del generador de vapor, ε_HRVG [–]*; *Efectividad del regenerador, ε_reg [–]*; *Efectividad del condensador, ε_cond [–]*; *Margen O1 [–]*; *Margen O2 [K]*; *Margen O5 [–]*; *Fuera de rango*; *B verificado*; *Iteraciones*; *Evaluaciones*

#### Tabla 4.3-3 · Escalera de conservación de datos del profesor
- **Hoja:** `4.3-3 Escalera de conservación` · **Filas:** 18 · **Columnas:** 11
- **Fuente:** `resultados/2026-10-08_final_M9/m9_escalera.csv` · **Filtro:** todas las rondas de la escalera
- **Columnas:** *Ronda*; *Datos conservados*; *Datos del profesor conservados*; *Evaluadas*; *Genuinos*; *KALINA*; *KALINA confiables*; *D mínimo*; *Criterio más roto*; *Elegido*; *KALINA por búsqueda*

#### Tabla 4.3-4 · Verificación teqp contra el motor real
- **Hoja:** `4.3-4 Verificación teqp contra` · **Filas:** 3 · **Columnas:** 23
- **Fuente:** `resultados/2026-10-08_final_M9/m9_motor_real.csv` · **Filtro:** puntos emparejados teqp y motor real
- **Columnas:** *Identificador*; *Origen*; *Clase con teqp*; *η con teqp [%]*; *Clase con el motor real*; *η con el motor real [%]*; *Δη [pp]*; *Coincide la clase*; *Piso de O2 (T de diseño de la bomba) [K]*; *Temperatura de la fuente, T_fuente [K]*; *Temperatura del sumidero, T_sumidero [K]*; *Presión de alta, P_alta [kPa]*; *Presión de baja, P_baja [kPa]*; *Fracción de amoníaco de la mezcla base, x_b [–]*; *Eficiencia isentrópica de la turbina, η_t [–]*; *Eficiencia isentrópica de la bomba, η_p [–]*; *Efectividad del generador de vapor, ε_HRVG [–]*; *Efectividad del regenerador, ε_reg [–]*; *Efectividad del condensador, ε_cond [–]*; *Fuera de rango*; *B verificado*; *Tiempo [s]*; *Mensaje*

#### Tabla 6.2-3 · Catálogo Húsavík (reproducción de la Fase 3)
- **Hoja:** `6.2-3 Catálogo Húsavík (reprodu` · **Filas:** 16 · **Columnas:** 11
- **Fuente:** `resultados/2026-10-09_final_M10_husavik/m10_catalogo.csv` · **Filtro:** todos los puntos de Húsavík
- **Columnas:** *Familia*; *Origen*; *Variables movidas*; *Piso de O2 [K]*; *N*; *KALINA (septiembre)*; *KALINA (ahora)*; *Confiables ahora*; *Coincide*; *|Δη| medio [pp]*; *|Δη| máximo [pp]*

#### Tabla 6.2-4 · Rangos KALINA por variable (Húsavík OFAT)
- **Hoja:** `6.2-4 Rangos KALINA por variabl` · **Filas:** 10 · **Columnas:** 8
- **Fuente:** `resultados/2026-10-09_final_M10_husavik/m10_ofat_rangos.csv` · **Filtro:** todos los puntos por variable
- **Columnas:** *Variable*; *Mínimo KALINA*; *Máximo KALINA*; *Criterio que rompe al bajar la variable*; *Criterio que rompe al subir la variable*; *η mínima [%]*; *η máxima [%]*; *KALINA*

#### Tabla 3.1-3 · Influencia y margen por variable (Δη y O2)
- **Hoja:** `3.1-3 Influencia y margen por v` · **Filas:** 10 · **Columnas:** 10
- **Fuente:** `canónico + m3_resumen.csv + m3_cruces.csv` · **Filtro:** puntos genuinos con W_net > 0 de la malla B06
- **Columnas:** *Variable*; *Rango explorado*; *Valor en A**; *Elasticidad E en A**; *Δη (genuinos) [pp]*; *η máx. KALINA en la malla [%]*; *Valor de esa η máx.*; *Zona KALINA*; *Criterios que bloquean*; *Distancia a la frontera de O2 [–]*

#### Tabla 6.2-5 · Frontera KALINA al variar x_b (Húsavík, x_b bajo)
- **Hoja:** `6.2-5 Frontera KALINA al variar` · **Filas:** 9 · **Columnas:** 4
- **Fuente:** `canónico (KF-M10b-MALLA)` · **Filtro:** todos los puntos de KF-M10b-MALLA
- **Columnas:** *x_b*; *P_baja mínima KALINA [kPa]*; *η en ese punto [%]*; *Criterio que más bloquea*

#### Tabla S-1 · Resumen por estudio
- **Hoja:** `S-1 Resumen por estudio` · **Filas:** 14 · **Columnas:** 12
- **Fuente:** `todos_los_puntos.csv` · **Filtro:** todos los puntos (sin el anexo A.1)
- **Columnas:** *Estudio*; *Nombre*; *Familia*; *Partes*; *Punto base*; *Diseño*; *Corridas*; *Genuinas*; *KALINA*; *KALINA confiables*; *Falsos convergidos*; *Criterio que más bloquea*

#### Tabla S-2 · Qué se movió en cada barrido
- **Hoja:** `S-2 Qué se movió en cada barrid` · **Filas:** 58 · **Columnas:** 14
- **Fuente:** `casos_x_variables.csv` · **Filtro:** todas las partes (sin el anexo A.1)
- **Columnas:** *Parte*; *Temperatura de la fuente, T_fuente [K]*; *Temperatura del sumidero, T_sumidero [K]*; *Presión de alta, P_alta [kPa]*; *Presión de baja, P_baja [kPa]*; *Fracción de amoníaco de la mezcla base, x_b [–]*; *Flujo másico base, m_b [kg/s]*; *Eficiencia isentrópica de la turbina, η_t [–]*; *Eficiencia isentrópica de la bomba, η_p [–]*; *Efectividad del generador de vapor, ε_HRVG [–]*; *Efectividad del regenerador, ε_reg [–]*; *Efectividad del condensador, ε_cond [–]*; *Piso de O2 (T de diseño de la bomba) [K]*; *motor*

#### Tabla S-3 · Rangos KALINA comparados
- **Hoja:** `S-3 Rangos KALINA comparados` · **Filas:** 34 · **Columnas:** 8
- **Fuente:** `todos_los_puntos.csv` · **Filtro:** solo KALINA confiables
- **Columnas:** *Estudio*; *Parte*; *Datos fijos*; *Variable*; *n KALINA confiables*; *p5*; *Mediana*; *p95*

#### Tabla S-4 · Datos del profesor conservables
- **Hoja:** `S-4 Datos del profesor conserva` · **Filas:** 11 · **Columnas:** 4
- **Fuente:** `fichas 4.2 y 4.3; verificación cruzada de cifras` · **Filtro:** conclusiones con cifras verificadas por A4
- **Columnas:** *Dato*; *Valor del profesor*; *¿Se conserva con KALINA?*; *Respaldo*

#### Tabla S-5 · Criterios que bloquean, por estudio
- **Hoja:** `S-5 Criterios que bloquean, por` · **Filas:** 14 · **Columnas:** 10
- **Fuente:** `todos_los_puntos.csv` · **Filtro:** genuinos que no son KALINA
- **Columnas:** *Estudio*; *Genuinos no KALINA*; *O1 (n)*; *O1 [%]*; *O2 (n)*; *O2 [%]*; *O3 (n)*; *O3 [%]*; *O5 (n)*; *O5 [%]*


---

# PARTE V — Catálogo de figuras

Las 30 figuras con su pie completo (título, estudio, punto base, datos fijos, barridos, filtro, n y fuente).

#### Figura 2.1-1. Con un solo cambio sobre los datos del profesor hay 0 KALINA.
- Estudio 2.1. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Punto base (las demás variables quedan fijas en): T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [340–623.15] K (22 valores); T_sumidero [283.15–303.55] K (10 valores); P_alta [1000–10000] kPa (24 valores); P_baja [150–1500] kPa (10 valores); x_b [0.3–0.9] (14 valores); η_t [0.75–0.9] (10 valores); η_p [0.65–0.85] (10 valores); ε_HRVG [0.75–0.85] (12 valores); ε_reg [0.75–0.85] (10 valores); ε_cond [0.75–0.85] (10 valores).
- Filtro: estudio 2.1 (2.1), barrido de una variable a la vez.
- n = 132. Fuente: todos_los_puntos.csv.

#### Figura 2.2-1. Ruta A: conservando la fuente del profesor (623 K), 0 KALINA.
- Estudio 2.2 · parte(s) 2.2a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
- Datos barridos: P_baja [400–2000] kPa (12 valores); ε_HRVG [0.75–0.81] (3 valores).
- Filtro: parte 2.2a (2.2a).
- n = 36. Fuente: todos_los_puntos.csv.

#### Figura 2.2-2. Ruta B: KALINA con T_fuente entre 390 y 434 K.
- Estudio 2.2 · parte(s) 2.2b. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
- Datos barridos: T_fuente [380–560] K (9 valores); P_baja [400–2000] kPa (32 valores).
- Filtro: parte 2.2b (2.2b).
- n = 144. Fuente: todos_los_puntos.csv.

#### Figura 2.3-1. Parte 2.3a: 0 KALINA con η y ε en [0.40, 0.95].
- Estudio 2.3 · parte(s) 2.3a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: η_t [0.4–0.95] (12 valores); η_p [0.4–0.95] (12 valores); ε_HRVG [0.4–0.95] (32 valores); ε_reg [0.4–0.95] (12 valores); ε_cond [0.4–0.95] (12 valores).
- Filtro: parte 2.3a (2.3a).
- n = 80. Fuente: todos_los_puntos.csv.

#### Figura 2.3-2. Parte 2.3b: 0 KALINA con η y ε en [0.40, 0.95].
- Estudio 2.3 · parte(s) 2.3b. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; motor de propiedades = teqp.
- Datos barridos: ε_HRVG [0.4–0.8] (5 valores); ε_cond [0.4–0.95] (12 valores).
- Filtro: parte 2.3b (2.3b).
- n = 60. Fuente: todos_los_puntos.csv.

#### Figura 2.3-3. Parte 2.3c: 19 KALINA con η y ε en [0.40, 0.95].
- Estudio 2.3 · parte(s) 2.3c. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.
- Datos barridos: P_baja [400–2000] kPa (20 valores); ε_HRVG [0.4–0.7] (4 valores).
- Filtro: parte 2.3c (2.3c).
- n = 64. Fuente: todos_los_puntos.csv.

#### Figura 2.3-4. Parte 2.3d: 1 KALINA con η y ε en [0.40, 0.95].
- Estudio 2.3 · parte(s) 2.3d. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.
- Datos barridos: T_fuente [403–560] K (7 valores); ε_cond [0.85–0.95] (3 valores).
- Filtro: parte 2.3d (2.3d).
- n = 21. Fuente: todos_los_puntos.csv.

#### Figura 2.4-1. Un sumidero más frío baja la P_baja mínima de KALINA y sube η.
- Estudio 2.4 (figura de síntesis: cada base es una parte con sus propios datos fijos y cada línea es una parte).
- Parte 2.4a (T_fuente = 403 K (A*)): Datos fijos: T_fuente = 403.0; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
- Parte 2.4b (T_fuente = 420 K): Datos fijos: T_fuente = 420.0; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
- Parte 2.4c (ε_HRVG = 0.40 (fuente del profesor)): Datos fijos: T_fuente = 623.15; P_alta = 3000.0; x_b = 0.5; m_b = 1.0; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.4; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Datos barridos: P_baja; piso de O2; T_sumidero.
- Base B4 (datos del profesor, T_fuente 623.15 K): 0 KALINA; no se dibuja (queda nombrada en el pie).
- Filtro: mínimos de P_baja y máximos de η de los KALINA por (base, T_sumidero).
- n = 15 puntos por panel (3 bases × 5 T_sumidero). Fuente: todos_los_puntos.csv.

#### Figura 3.1-1. Cerca de A*, x_b y P_baja son las que más mueven η en su rango.
- Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
- Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
- Filtro: estudio 3.1, malla, puntos genuinos con W_net > 0.
- n = 123. Fuente: todos_los_puntos.csv.

#### Figura 3.1-2. Pegado a A*, T_fuente es la variable más sensible (E = 10.9).
- Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
- Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
- Filtro: m3_resumen.csv (E_eta de la malla).
- n = 10. Fuente: resultados/2026-10-06_final_M3/m3_resumen.csv.

#### Figura 3.1-3. Eficiencia según cada variable, una a la vez, alrededor de A*.
- Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
- Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
- Filtro: estudio 3.1, malla y vecinos de A* (±1 % del rango).
- n = 170. Fuente: todos_los_puntos.csv.

#### Figura 3.1-4. A* está a menos del 6 % del rango de la frontera de O2 en 8 de 9 variables.
- Estudio 3.1. Punto base: A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)
- Punto base (las demás variables quedan fijas en): T_fuente = 403 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 563.64 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [340–623.15] K (17 valores); T_sumidero [283.15–303.55] K (17 valores); P_alta [1000–10000] kPa (17 valores); P_baja [150–1500] kPa (17 valores); x_b [0.3–0.9] (17 valores); η_t [0.4–0.95] (17 valores); η_p [0.4–0.95] (17 valores); ε_HRVG [0.4–0.95] (17 valores); ε_reg [0.4–0.95] (17 valores); ε_cond [0.4–0.95] (17 valores).
- Filtro: m3_cruces.csv (tipo = margen).
- n = 9. Fuente: resultados/2026-10-06_final_M3/m3_cruces.csv.

#### Figura 3.2-1. Qué variables separan a los KALINA del resto (LHS de 500 puntos).
- Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
- Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
- Filtro: estudio 3.2: 452 genuinos y 48 sin resultado (no convergió o falso convergido).
- n = 500. Fuente: todos_los_puntos.csv.

#### Figura 3.2-2. El 90 % de los KALINA tiene razón de presiones entre 1.7 y 5.3.
- Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
- Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
- Filtro: estudio 3.2.
- n = 500. Fuente: todos_los_puntos.csv.

#### Figura 3.2-3. Influencia de cada variable sobre η (PRCC, 430 puntos).
- Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
- Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
- Filtro: m4b_prcc.csv (fila de salida = η).
- n = 430. Fuente: resultados/2026-10-07_final_M4b/m4b_prcc.csv.

#### Figura 3.2-4. El 90 % de los KALINA tiene ΔP 968–3718 kPa y r_P 1.7–5.3.
- Estudio 3.2. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
- Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.23–499.94] K (300 valores); T_sumidero [278.18–303.54] K (300 valores); P_alta [2005.4–4991.2] kPa (300 valores); P_baja [302.95–1498] kPa (300 valores); x_b [0.50012–0.84998] (300 valores); η_t [0.75036–0.91969] (300 valores); η_p [0.6504–0.89919] (300 valores); ε_HRVG [0.60004–0.94905] (300 valores); ε_reg [0.60097–0.94997] (300 valores); ε_cond [0.70014–0.94941] (300 valores); piso de O2 [278.18–303.54] K (300 valores).
- Filtro: estudio 3.2: 452 genuinos y 48 sin resultado.
- n = 500. Fuente: todos_los_puntos.csv.

#### Figura 3.3-1. Fracción de KALINA al subir P_baja entre 1500 y 2500 kPa.
- Estudio 3.3. Punto base: Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'
- Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.75–499.83] K (150 valores); T_sumidero [278.28–303.41] K (150 valores); P_alta [2015.7–4995.8] kPa (150 valores); P_baja [1501.3–2494.5] kPa (150 valores); x_b [0.5023–0.84953] (150 valores); η_t [0.75103–0.91919] (150 valores); η_p [0.65119–0.89988] (150 valores); ε_HRVG [0.60089–0.94845] (150 valores); ε_reg [0.60038–0.9477] (150 valores); ε_cond [0.70004–0.94966] (150 valores); piso de O2 [278.28–303.41] K (135 valores).
- Filtro: estudio 3.3, puntos evaluados.
- n = 135. Fuente: todos_los_puntos.csv.

#### Figura 4.1-1. Parte 4.1a (conserva sus temperaturas, T_fuente y T_sumidero): 4 KALINA de 119 evaluados, 2 confiables.
- Estudio 4.1 · parte(s) 4.1a. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.
- Datos barridos: P_alta [2000.1–4986.6] kPa (120 valores); P_baja [202.14–1989.7] kPa (120 valores); x_b [0.50124–0.84895] (120 valores); η_t [0.40062–0.94745] (120 valores); η_p [0.4043–0.94919] (120 valores); ε_HRVG [0.40441–0.94919] (120 valores); ε_reg [0.40384–0.9479] (120 valores); ε_cond [0.40087–0.94579] (120 valores).
- Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
- n = 119. Fuente: todos_los_puntos.csv.

#### Figura 4.1-2. Parte 4.1b (conserva sus presiones, P_alta y P_baja): 0 KALINA de 120 evaluados, 0 confiables.
- Estudio 4.1 · parte(s) 4.1b. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_fuente [381.61–621.77] K (120 valores); T_sumidero [278.26–303.48] K (120 valores); x_b [0.50084–0.84732] (120 valores); η_t [0.40268–0.94858] (120 valores); η_p [0.40103–0.9471] (120 valores); ε_HRVG [0.40217–0.94755] (120 valores); ε_reg [0.40228–0.9466] (120 valores); ε_cond [0.40209–0.9474] (120 valores); piso de O2 [278.26–303.48] K (120 valores).
- Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
- n = 120. Fuente: todos_los_puntos.csv.

#### Figura 4.1-3. Parte 4.1c (conserva sus presiones y su clima): 0 KALINA de 120 evaluados, 0 confiables.
- Estudio 4.1 · parte(s) 4.1c. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_sumidero = 300.03 K; P_alta = 3000 kPa; P_baja = 400 kPa; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.
- Datos barridos: T_fuente [380.23–622.4] K (120 valores); x_b [0.50023–0.84932] (120 valores); η_t [0.40006–0.94769] (120 valores); η_p [0.4036–0.94548] (120 valores); ε_HRVG [0.40016–0.94888] (120 valores); ε_reg [0.40216–0.9486] (120 valores); ε_cond [0.40424–0.94685] (120 valores).
- Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
- n = 120. Fuente: todos_los_puntos.csv.

#### Figura 4.1-4. Parte 4.1d (conserva su P_alta y sus temperaturas): 6 KALINA de 120 evaluados, 0 confiables.
- Estudio 4.1 · parte(s) 4.1d. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; T_sumidero = 300.03 K; P_alta = 3000 kPa; m_b = 1 kg/s; piso de O2 = 300.03 K; motor de propiedades = teqp.
- Datos barridos: P_baja [211.42–1985.6] kPa (120 valores); x_b [0.50226–0.84794] (120 valores); η_t [0.40325–0.94578] (120 valores); η_p [0.40037–0.94661] (120 valores); ε_HRVG [0.40425–0.94958] (120 valores); ε_reg [0.40094–0.9466] (120 valores); ε_cond [0.40217–0.94675] (120 valores).
- Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
- n = 120. Fuente: todos_los_puntos.csv.

#### Figura 4.1-5. Parte 4.1e (conserva su fuente y su composición, T_fuente y x_b): 10 KALINA de 119 evaluados, 0 confiables.
- Estudio 4.1 · parte(s) 4.1e. Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)
- Datos fijos: T_fuente = 623.15 K; x_b = 0.5; m_b = 1 kg/s; motor de propiedades = teqp.
- Datos barridos: T_sumidero [278.28–303.36] K (120 valores); P_alta [2023–4997.5] kPa (120 valores); P_baja [206.13–1999.3] kPa (120 valores); η_t [0.4033–0.94995] (120 valores); η_p [0.40348–0.9476] (120 valores); ε_HRVG [0.40414–0.94874] (120 valores); ε_reg [0.40265–0.94725] (120 valores); ε_cond [0.40127–0.94825] (120 valores); piso de O2 [278.28–303.36] K (119 valores).
- Filtro: todos los puntos evaluados (omitidos no se dibujan; marcador hueco = fuera del rango confiable).
- n = 119. Fuente: todos_los_puntos.csv.

#### Figura 4.2-1. Con las presiones del profesor hay KALINA desde T_fuente ≈ 390 K; con su clima (300 K) hace falta ε_cond ≥ 0.875.
- Estudio 4.2. Punto base: PP con P_alta = 3000 kPa y P_baja = 400 kPa conservadas
- Datos fijos: P_alta = 3000 kPa; P_baja = 400 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; motor de propiedades = teqp.
- Datos barridos: T_fuente [385–410] K (11 valores); T_sumidero [278.15–300.03] K (3 valores); ε_cond [0.85–0.95] (5 valores); piso de O2 [278.15–300.03] K (3 valores).
- Filtro: todos los puntos de la malla (cuadrado verde = KALINA).
- n = 165. Fuente: todos_los_puntos.csv.

#### Figura 4.3-1. Se conservan 8 de los 10 datos de diseño del profesor y sigue habiendo KALINA.
- Estudio 4.3 (escalera de conservación; figura de síntesis: una barra por conjunto conservado). Punto base: PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50).
- Datos fijos: los 10 datos de diseño del profesor; cada barra conserva el subconjunto que indica su etiqueta.
- Datos barridos: 100 puntos (ronda 0) o 30 (rondas 1–3) por conjunto.
- Filtro: KALINA confiables por conjunto conservado; el elegido de cada ronda se resalta con borde negro.
- n = 18 conjuntos. Fuente: resultados/2026-10-08_final_M9/m9_escalera.csv.

#### Figura 5.1-1. La búsqueda llega a η = 15.6 % dentro de la región KALINA (equipos a 0.95).
- Estudio 5.1 · partes 5.1a … 5.1e (figura de síntesis: cada línea es un arranque con sus propios datos conservados).
- 5.1a · libre (desde el mejor de 3.2).
- 5.1b · libre (desde el mejor de 2.4).
- 5.1c · conserva sus temperaturas.
- 5.1d · conserva sus presiones y su clima.
- 5.1e · conserva su fuente y su x_b (fuera de rango).
- Filtro: líneas = pasos aceptados de cada búsqueda (cada uno es KALINA genuino, D = 0); puntos grises = evaluaciones que no se aceptaron.
- n = 550 evaluaciones (41 pasos aceptados y 509 no aceptados; las evaluaciones sin η no se dibujan). Fuente: m7_trayectorias.csv y m7_evaluaciones.csv.

#### Figura 6.1-1. teqp y el motor real coinciden en los 5 puntos que el motor real resolvió.
- Estudio 6.1 · partes 6.1a y 6.1d (puntos de control, cada uno con sus propios datos, no comparables entre sí).
- Puntos: P03 = estudio 4.2, presiones del profesor, techo; P08 = estudio 5.1, óptimo A4; A* = Ancla A*; A4 = Óptimo A4 de estudio 5.1; HUS = Base de Húsavík.
- Sin η real (motor real cortado por el límite de 300 s, no por la física): P01, P02, P04, P05, P06, P07, P09, P10, P11, P12.
- Filtro: pares con η de ambos motores. Marcas: recta 1:1 y banda ±0.7 pp (incertidumbre del modelo de propiedades).
- n = 5. Fuente: m6_comparacion.csv y m9_motor_real.csv.

#### Figura 6.2-1. Húsavík: la P_baja mínima de KALINA sube con la fracción de amoníaco x_b.
- Estudio 6.2 · parte(s) 6.2c. Punto base: Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K
- Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp.
- Datos barridos: P_baja [200–1200] kPa (8 valores); x_b [0.3–0.91] (9 valores).
- Filtro: todos los puntos de las dos mallas (mismos datos fijos); línea = P_baja mínima KALINA por x_b; x_b = 0.50 es KALINA con η < 1.3 %.
- n = 118. Fuente: todos_los_puntos.csv.

#### Figura 6.2-2. Húsavík: eficiencia según cada variable, una a la vez (casi todas rompen por O2).
- Estudio 6.2 · parte(s) 6.2b. Punto base: Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K
- Punto base (las demás variables quedan fijas en): T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; P_baja = 690 kPa; x_b = 0.82; m_b = 1 kg/s; η_t = 0.9; η_p = 0.8; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.95; piso de O2 = 283.15 K; motor de propiedades = teqp. Cada panel o tramo mueve solo su variable.
- Datos barridos (uno a la vez): T_fuente [380–430] K (15 valores); T_sumidero [273.15–293.15] K (15 valores); P_alta [2500–4000] kPa (15 valores); P_baja [500–1200] kPa (15 valores); x_b [0.6–0.95] (15 valores); η_t [0.75–0.95] (15 valores); η_p [0.6–0.9] (15 valores); ε_HRVG [0.6–0.95] (15 valores); ε_reg [0.4–0.95] (15 valores); ε_cond [0.7–0.95] (15 valores).
- Filtro: η solo en genuinos con W_net > 0; ✕ sobre el eje = no genuino.
- n = 150. Fuente: todos_los_puntos.csv.

#### Figura S-1. Resultado de cada barrido: puntos por clase.
- Estudios 1.1 a 6.2 (figura de síntesis: una barra por estudio), sin el anexo A.1.
- Datos fijos: no aplica (figura de síntesis).
- Filtro: todos los puntos menos los de A.1.
- n = 4560. Fuente: todos_los_puntos.csv.

#### Figura S-2. Qué variables se movieron y cuáles quedaron fijas en cada barrido.
- Todos los estudios, sin el anexo A.1 (figura de síntesis: una fila por parte).
- Datos fijos: celda gris (PP/teqp), naranja (valor fijo distinto del profesor) o vacía (no aplica).
- Datos barridos: celdas azules (rango en Tabla S-2); antes: celdas con el rango [mín, máx] o 'n = 2'.
- Filtro: casos_x_variables.csv, una fila por barrido.
- n = 58 barridos. Fuente: 00_inventario/casos_x_variables.csv.


---

# PARTE VI — Cierre

## VI.1 Preguntas probables y cómo responderlas

**1. ¿Qué es lo que hizo exactamente en esta campaña?**
Seis preguntas, 14 estudios, 4 581 corridas (4 560 evaluadas). Primero comprobé que el ciclo no funciona con los datos del
profesor (R1); busqué el cambio mínimo (R2, R3); medí qué variables deciden la clase y cuáles mueven η (R4,
R5); cuánto margen hay (R6); cómo influyen clima y composición (R7); qué se puede conservar (R8); hasta dónde
llega η (R9); y verifiqué con otro motor y con una planta real (R10).

**2. ¿Por qué no usó Sobol?**
Pide ~6 100 puntos (unas 53 horas) y exige un resultado en todos los puntos; aquí muchos no convergen. RSA/KS
está hecho para salidas «cumple / no cumple» y tolera los fallos.

**3. ¿Qué es un LHS y por qué no puntos al azar?**
Divide cada variable en franjas iguales y usa cada una una vez: cubre el espacio de forma pareja con pocos
puntos.

**4. ¿Por qué estudia la sensibilidad alrededor de A\* y no del punto del profesor?**
Porque ahí el ciclo no converge: no hay η ni márgenes que derivar. A\* es el punto funcional más cercano.

**5. ¿Qué significa KS = 0.43?**
La mayor diferencia entre las curvas acumuladas de los KALINA y del resto es de 0.43 (43 puntos de
probabilidad); con p < 10⁻¹⁵ no es casualidad.

**6. ¿Cuál pesa más, P_baja o ε_cond?**
No se puede decir: sus KS son 0.427 y 0.426 y sus intervalos de confianza se solapan casi por completo.

**7. Si subir P_baja asegura KALINA, ¿por qué no subirla siempre?**
Porque baja la eficiencia (0.40–0.55 pp por cada 100 kPa) y, con P_baja muy alta, r_P tiende a 1 y el ciclo
produce poco trabajo.

**8. ¿Qué es el criterio O2?**
Cavitación: el líquido debe llegar subenfriado a la bomba; margen = T_burbuja − T de entrada. Es el criterio
que casi siempre bloquea (88–100 % de los genuinos no KALINA).

**9. ¿Qué dato del profesor no se puede conservar?**
La temperatura de la fuente a 623 K. Todos los demás se conservan si la fuente baja a unos 390–410 K.

**10. ¿Qué eficiencia esperar?**
8–11 % con equipos medios; hasta ~15 % con equipos al 95 % (un tope).

**11. ¿Qué es un «falso convergido»?**
El solver dice que convergió pero el clasificador lo descarta (no cierra el balance de energía, por ejemplo).
Se cuenta aparte y nunca como genuino.

**12. ¿Por qué hay figuras con menos puntos que su tabla?**
Una figura de η solo puede dibujar los puntos que tienen η; y las figuras de resumen (por ejemplo la P_baja
mínima de cada clima en 2.4-1) dibujan un valor derivado. La hoja `N.M-R` trae todos los puntos.

## VI.2 Lo que NO se puede afirmar

- El **orden** entre P_baja y ε_cond como decisores de KALINA.
- Una **regla de corte simple** para la factibilidad.
- **Tendencias globales** a partir de 3.1: T_fuente y x_b no son monótonas alrededor de A\*.
- Lo que pasa con **T_fuente > 410 K** en 4.2 ni fuera de las cajas de muestreo.
- Diferencias de η menores de **0.7 pp** (banda de incertidumbre).
- Que los diseños KALINA tengan **margen de cavitación**: no lo tienen (O2 se cumple sin margen propio).

## VI.3 Inconsistencias conocidas del material

| Dónde | Qué pasa | Cómo leerlo |
|---|---|---|
| Tabla 2.3-3 | La columna «Parte» usa códigos antiguos | n1 = 2.3a, n2a = 2.3b, n2b = 2.3c, n3 = 2.3d |
| Tabla 2.4-3 | La columna «Base» usa B1…B4 | B1 = 2.4a, B2 = 2.4b, B3 = 2.4c, B4 = 2.4d |
| Tabla 3.1-1 | «n valores» = 18 en vez de 15 | 15 de la malla + 2 vecinos + el ancla |
| Tabla S-4 | Algunas celdas dicen «grupo EF» y «0 confiables con TF» | EF = eficiencias; TF = T_fuente |
| Estudio 4.3 en `Datos` | Incluye filas de las partes 6.1d y 6.2e | Vienen del caso de origen M09 (verificación con el motor real y P_baja mínima de Húsavík); aparecen bajo el estudio 4.3 en la tabla canónica |
| Subtítulo de varias figuras | «Estudio 3.2 · estudio 3.2» | Duplicación en la traducción automática de códigos; no afecta a los datos |
| Figuras de Matplotlib 3.1-3, 3.2-1, 3.2-4 y 5.1-1 | Se regeneraron el 2026-10-12 para coincidir con el Excel | Muestran los vecinos (3.1-3), los puntos sin resultado (3.2-1, 3.2-4) y todas las evaluaciones (5.1-1) |

## VI.4 Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Excel final | `datos/Excel_kalina_final_final_final.xlsx` |
| Informe de resultados | `analisis_final/INFORME_BARRIDOS_CAMPANA_FINAL.md` |
| Una ficha por estudio (objetivo, datos, métodos, advertencias) | `analisis_final/04_fichas/Ficha_N.M_….md` |
| Tablas (CSV y Markdown) | `analisis_final/02_tablas/<estudio>/` |
| Figuras (PNG, SVG, pie y conteo por clase) | `analisis_final/03_figuras/<estudio>/` |
| Tabla canónica de todos los puntos | `analisis_final/01_datos/todos_los_puntos.csv` |
| Resultados originales de cada barrido | `resultados/2026-10-0N_final_M*/` (con su `REPORTE_M*.md`) |
| Por qué se eligieron estos métodos | `docs/ESTUDIO_METODOS_SENSIBILIDAD.md` |
| Matemática de D, OAT, LHS, RSA, PRCC, PAWN, CART | `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` |
| Planteamiento del modelo y restricciones | `docs/PLANTEAMIENTO_MATEMATICO.md` |
| Tablero interactivo en HTML | `analisis_final/06_tablero/tablero_kalina.html` |
| Guía corta (versión resumida de este documento) | `analisis_final/GUIA_DE_ESTUDIO_ANALISIS_SENSIBILIDAD.md` |

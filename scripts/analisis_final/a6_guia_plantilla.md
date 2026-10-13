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

{{T 1.1-2}}

Columnas:
{{COLS 1.1-2}}

*Lectura:* en las cuatro partes, «No convergidos» es igual a «Corridas» y «Genuinos» es 0.

**Tabla 1.1-3 — Comparación antes y después de la Fase 1.** Una fila por punto de la Fase 1 (41): clase y η de
septiembre contra la del código actual, con el mensaje del solver. Primeras filas:

{{T 1.1-3 | cols=Grupo;Valor;Clase (antes);Clase (ahora);Misma clase;η (antes) [%];η (ahora) [%] | n=8}}

Columnas:
{{COLS 1.1-3}}

*Lectura:* la columna «Misma clase» es verdadera en los 41 puntos: el código actual reproduce al profesor.
Los mensajes dicen por qué no converge: *«no existe equilibrio líquido-vapor»* a T = 623 K y, en el motor
real, *«presupuesto de tiempo agotado»*.

**Tabla 1.1-1 — Condiciones.** Qué quedó fijo y qué se barrió en cada parte (52 filas, siete columnas).

Columnas:
{{COLS 1.1-1}}

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

{{T 2.1-2}}

**Tabla 2.1-3 — Distancia al punto del profesor, una variable a la vez.** Una fila por variable: cuántos
puntos convergen, cuántos son KALINA, el valor que más se acerca al profesor y el D mínimo.

{{T 2.1-3 | cols=Variable;Tipo;Convergen;KALINA;Corregibles;Inviables;No convergidos;Valor convergido más cercano al PP;D mínimo;Valor de D mínimo}}

Columnas:
{{COLS 2.1-3}}

*Lectura:* solo T_fuente y ε_HRVG dan puntos corregibles; en todas las demás hay 0 o solo falsos
convergidos. La fila de T_fuente tiene D mínimo = 2.018 en T_fuente = 402.9 K: es el punto más cercano a ser
KALINA, y le falta cumplir O2 por 2.0 K.

**Tabla 2.2-3 — Resumen de la malla de dos cambios.** Una fila por ruta y valor de la variable 1.

{{T 2.2-3 | cols=Ruta;Variable 1;Valor 1;Genuinos;KALINA;Falsos convergidos;P_baja mínima KALINA [kPa];η mínima KALINA [%];Fuera de rango en la mínima KALINA;D mínimo}}

Columnas:
{{COLS 2.2-3}}

*Lectura:* la **ruta A** tiene 0 KALINA en sus tres filas. En la **ruta B**, hay KALINA solo con T_fuente de
390, 403, 420 y 434 K; con 380 K no converge y con 466 K o más no hay KALINA. La P_baja mínima crece al
subir la fuente (445.5 → 945.5 kPa) y η no es monótona (2.45 % en 390 K; 9.15 % en 420 K). Los 11 KALINA
fuera de rango están todos en 434 K.

**Tablas 2.1-1 y 2.2-1 — Condiciones.** Qué quedó fijo y qué se barrió.

### Figuras

**Figura 2.1-1 (10 paneles).**

{{P 2.1-1}}

*Cómo se lee:* un panel por variable. El eje horizontal es el valor de la variable. El vertical **no es η**:
es la *fila de la clase* (KALINA arriba; no convergió y falso convergido abajo), porque en la mayoría de los
barridos no hay η que graficar. Cada punto tiene forma y color según su clase; un marcador hueco indica
fuera de rango. Un panel casi vacío arriba significa que casi nada llega a ser KALINA.

**Figura 2.2-1 (ruta A) y Figura 2.2-2 (ruta B).**

{{P 2.2-1}}

{{P 2.2-2}}

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

{{T 2.3-2}}

**Tabla 2.3-3 — Malla con η y ε en [0.40, 0.95].** Una fila por parte y valor de la variable 1.

{{T 2.3-3 | cols=Parte;Variable 1;Valor 1;Variable 2;Genuinos;KALINA;Falsos convergidos;d menor;η en el d menor [%];η mayor [%]}}

> **Atención:** esta tabla usa los códigos antiguos de parte: **n1 = 2.3a, n2a = 2.3b, n2b = 2.3c,
> n3 = 2.3d.**

Columnas:
{{COLS 2.3-3}}

*Lectura:*
- **2.3a (n1)** y **2.3b (n2a):** 0 KALINA; 2.3b son 48 corregibles, todos por O2.
- **2.3c (n2b):** ε_HRVG = 0.40 con P_baja 1318 kPa → KALINA con η = 6.27 %; ε_HRVG = 0.50 con P_baja 1736 kPa
  → η = 4.34 %. Todos fuera de rango.
- **2.3d (n3):** T_fuente = 403 K con ε_cond = 0.95 → KALINA con η = 9.5 %, confiable.

### Figuras

{{P 2.3-1}}

{{P 2.3-2}}

{{P 2.3-3}}

{{P 2.3-4}}

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

{{T 3.2-1}}

*Nota:* los 500 puntos son la unión de dos LHS (una muestra de 300 y otra de 200); cada mitad es un LHS
estricto, la unión no.

**Resultado del muestreo:** 452 genuinas, **121 KALINA (83 confiables)**, 222 fuera de rango.

**Análisis sobre el mismo muestreo:** RSA/KS (con intervalos bootstrap), PRCC, PAWN, árbol CART y prueba de
convergencia. **Estudio 3.3:** 150 puntos con la misma caja salvo P_baja en 1500–2500 kPa (15 omitidos).

### Tablas

**Tabla 3.2-2 — Corridas por parte y clase.**

{{T 3.2-2}}

**Tabla 3.2-3 — Separación KALINA / no KALINA (RSA y KS).** 52 filas: 4 separaciones × 13 variables (las 10
de entrada más ΔP, r_P y ΔT_fs). La separación «KALINA»:

{{T 3.2-3 | filtro=Separación=KALINA}}

Columnas:
{{COLS 3.2-3}}

*Lectura:* ordenando por KS: **P_baja 0.427, ε_cond 0.426, r_P 0.353, T_fuente 0.287, ΔT_fs 0.248,
T_sumidero 0.200, x_b 0.193**; las demás, menores de 0.14 (P_alta 0.130, p = 0.08; η_t, η_p, ε_HRVG y ε_reg,
no significativas). Los intervalos de P_baja (0.365–0.519) y ε_cond (0.353–0.524) **se solapan casi por
completo**: no se puede afirmar cuál de las dos pesa más.

Las otras tres separaciones de la misma tabla (`converge`, `cumple_O2`, `cumple_O1`) dicen *qué variable
controla cada barrera*, no solo la clase final.

**Tabla 3.2-5 — Rangos de presión de los KALINA.** Para P_alta, P_baja, ΔP y r_P: mínimo, percentil 5,
mediana, percentil 95 y máximo de los KALINA y de los no KALINA genuinos.

{{T 3.2-5}}

Columnas:
{{COLS 3.2-5}}

*Lectura:* los KALINA tienen P_baja 683–1461 kPa (p5–p95) contra una mediana de 767 kPa de los no KALINA;
r_P entre 1.69 y 5.34. Es decir, **el 90 % de los KALINA vive con r_P entre 1.7 y 5.3**.

**Tablas 3.2-6, 3.2-7 y 3.2-8 — Ventana KALINA por franjas** de P_alta, T_fuente y T_sumidero. La de P_alta:

{{T 3.2-6}}

Columnas:
{{COLS 3.2-6}}

*Lectura (interacción):* la P_baja mínima KALINA baja de 913 kPa (franja 2000–2500 de P_alta) a 547 kPa
(franja 3500–4000) y deja de bajar después. Por eso P_alta, sola, no es significativa (KS = 0.13) pero r_P
sí.

**Tabla 3.3-3 — Techo de P_baja antes de cortar KALINA** (franjas de 100 kPa de P_baja; las dos primeras
vienen de 3.2, el resto de 3.3):

{{T 3.3-3}}

**Tabla 3.3-4 — Techo de P_baja por franja de P_alta:**

{{T 3.3-4}}

*Lectura:* hay KALINA en **todas** las franjas hasta 2500 kPa, entre 33 y 75 % de los evaluados; el KALINA de
mayor P_baja tiene 2494.5 kPa. No hay un techo de clasificación.

**Tabla 3.2-4 — filas de margen.** Además del PRCC sobre η (ver R5), la tabla trae el PRCC sobre el margen
de cavitación m_O2, que **explica el mecanismo**: P_baja +0.76, ε_cond +0.73, T_fuente −0.68, T_sumidero
−0.54, x_b −0.47 (n = 452); las eficiencias de turbina y bomba no lo mueven (|PRCC| < 0.05, p > 0.4).

{{T 3.2-4 | filtro=Salida=m_O2}}

*Lectura del mecanismo:* subir P_baja eleva la temperatura de burbuja; un condensador más efectivo enfría
más el líquido; una fuente más caliente, un sumidero más caliente o más amoníaco empujan el líquido hacia la
saturación.

### Figuras

**Figura 3.2-1 — curvas acumuladas por variable (10 paneles).**

{{P 3.2-1}}

*Cómo se lee:* un panel por variable. Curva verde = distribución de los KALINA; gris punteada = resto
genuino; roja punteada = puntos sin resultado (no convergió o falso convergido). **Cuanto más separadas
estén la verde y la gris, más decide la variable.** El KS de cada panel está escrito arriba a la izquierda.
En P_baja y ε_cond la curva verde va claramente a la derecha de la gris: los KALINA tienen valores más altos.

**Figura 3.2-2 — plano de presiones.**

{{P 3.2-2}}

*Cómo se lee:* P_alta (horizontal) contra P_baja (vertical), un punto por corrida, color y forma por clase.
Las dos rectas punteadas son r_P en el percentil 5 y 95 de los KALINA: **entre las dos rectas está el 90 % de
los KALINA**.

**Figura 3.2-4 — histogramas de ΔP y r_P.**

{{P 3.2-4}}

*Cómo se lee:* a la izquierda, ΔP; a la derecha, r_P. Barras verdes = KALINA, grises = resto genuino, rojas =
sin resultado, con los mismos intervalos. Los KALINA se concentran a la izquierda en r_P: la cola larga a la
derecha es de no KALINA.

**Figura 3.3-1 — % de KALINA por franja de P_baja (1500–2500 kPa).**

{{P 3.3-1}}

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

{{T 3.2-4 | filtro=Salida=eta}}

Columnas:
{{COLS 3.2-4}}

*Lectura:* los PRCC significativos son P_baja −0.681, P_alta +0.583, η_t +0.375, T_fuente +0.291, ε_reg
+0.267 y x_b +0.236 (p < 0.001); ε_cond +0.083 tiene p = 0.088 (no significativo) y T_sumidero, η_p y ε_HRVG
son prácticamente cero.

**Tabla 3.1-3 — Influencia y margen por variable (Δη y O2).** Una fila por variable, ordenada por |E|.

{{T 3.1-3}}

Columnas:
{{COLS 3.1-3}}

*Lectura:* T_fuente tiene la mayor elasticidad (E = 10.87) y x_b la mayor Δη (10.78 pp). Las palancas que
suben η sin perder KALINA son **ε_reg** (hasta 10.96 %) y **η_t** (hasta 9.62 %), ambas en 0.95. P_alta y x_b
mueven mucho η pero casi toda su malla cae fuera de KALINA.

**Tabla 3.1-2 — Corridas por clase.**

{{T 3.1-2}}

**Tabla 3.1-1 — Condiciones.** *Nota:* en «n valores» aparece 18, no 15: son los 15 valores de la malla, los
2 vecinos de A\* y el ancla.

### Figuras

**Figura 3.1-1 — tornado de Δη.**

{{P 3.1-1}}

*Cómo se lee:* una barra por variable, ordenadas por tamaño; la longitud es η máx − η mín al recorrer todo
el rango de esa variable con las demás en A\*. La barra más larga mueve más η.

**Figura 3.1-2 — elasticidades.**

{{P 3.1-2}}

*Cómo se lee:* barra verde = subir la variable sube η; roja = la baja. La longitud es la elasticidad en A\*.
**Solo vale pegado a A\***: no se debe extrapolar.

**Figura 3.1-3 — η contra cada variable, una a la vez (10 paneles).**

{{P 3.1-3}}

*Cómo se lee:* un panel por variable. **Línea vertical punteada** = valor de la variable en A\*; **línea
horizontal punteada y banda verde** = η de A\* ± 0.7 pp (banda de incertidumbre); **✕ al fondo (η = −0.6)** =
punto sin η (no convergió o no genuino). Dibuja la malla y los 2 vecinos de A\*.

*Qué se ve:* ε_reg, η_t, ε_HRVG y η_p suben η casi en línea recta; T_fuente y x_b alternan entre no
convergió, KALINA y CORREGIBLE (no son monótonas); P_baja baja η al subir.

**Figura 3.2-3 — PRCC sobre η.**

{{P 3.2-3}}

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

{{T 6.1-4 | cols=Identificador;Origen;Subenfriamiento, ΔT_sub [K];Alcanzable;P_baja original [kPa];P_baja requerida [kPa];ΔP_baja [kPa];η original [%];η requerida [%];Δη [pp];Nota}}

Columnas:
{{COLS 6.1-4}}

*Lectura:* exigir **2 K** cuesta **+25 a +46 kPa** de P_baja y **−0.3 a −0.5 pp** de η (mediana por kelvin:
13.9 kPa y 0.16 pp en 10 pares); exigir 5 K, +19 a +116 kPa y −0.3 a −1.2 pp. Con las presiones del profesor
(P03), 2 K piden subir P_baja de 400 a ~425 kPa. *Advertencia:* el cálculo de P05 (óptimo 5.1a) no es
confiable (hay un hueco NO_CONVERGIO y la bisección saltó).

**Tabla S-5 — Criterios que bloquean, por estudio.**

{{T S-5}}

Columnas:
{{COLS S-5}}

*Lectura:* **O2 es el criterio que bloquea en el 88–100 % de los genuinos no KALINA** de todos los estudios,
salvo 4.2 (67 %). O3 pesa en 4.1 (39 %) y 4.2 (33 %), por fuentes frías o x_b baja.

### Figuras

**Figura 3.1-4 — márgenes a la frontera de O2.**

{{P 3.1-4}}

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

{{T 2.4-3 | cols=Base;Temperatura del sumidero, T_sumidero [K];Genuinos;KALINA;P_baja mínima KALINA [kPa];η mínima KALINA [%];Fuera de rango en la mínima KALINA;Bloqueantes (genuinos)}}

Columnas:
{{COLS 2.4-3}}

*Lectura:* en B1, la P_baja mínima baja de 562.5 kPa (300 K) a 290.6 kPa (278 K) y η sube de 8.49 a 10.41 %.
En B3 (ε_HRVG = 0.40) toda la columna «fuera de rango» es verdadera: ninguno es confiable. **B4 tiene 0
genuinos en los cinco climas.** La pendiente de la P_baja mínima es −12.5 kPa/K en B1 (R² = 0.99), −15.9 en B2
y −25.7 en B3; η sube +0.088, +0.128 y +0.155 pp/K.

**Tabla 6.2-4 — Rangos KALINA por variable (Húsavík, una a la vez).**

{{T 6.2-4}}

Columnas:
{{COLS 6.2-4}}

*Lectura:* con lo demás en el ancla de Húsavík, hay KALINA con T_fuente 380–401 K, T_sumidero 273–283 K,
P_alta 2821–4000 kPa, P_baja 700–1200 kPa, x_b 0.60–0.825 y ε_HRVG 0.60–0.925; ε_cond solo en 0.95. η_t, η_p y
ε_reg: todo el rango probado. Casi todo rompe por O2.

**Tabla 6.2-5 — Frontera KALINA al variar x_b (Húsavík, x_b bajo).**

{{T 6.2-5}}

Columnas:
{{COLS 6.2-5}}

*Lectura:* **con x_b ≤ 0.45 no hay ciclo** (0 genuinos de 32: 16 no convergen y 16 son falsos convergidos);
**x_b = 0.50** es KALINA formal pero con η de 0.1–1.2 %; **x_b = 0.55** es el primer KALINA útil (P_baja mín.
300 kPa, η = 9.6 %); luego P_baja mínima 400, 500 y 500 kPa para 0.60, 0.65 y 0.70.

### Figuras

**Figura 2.4-1 (2 paneles).**

{{P 2.4-1}}

*Cómo se lee:* izquierda, P_baja mínima KALINA contra T_sumidero; derecha, η máxima KALINA contra T_sumidero,
una línea por base (2.4a, 2.4b, 2.4c). Las líneas son casi rectas y paralelas: la relación es lineal en
278–300 K. 2.4d no aparece porque no tiene KALINA.

**Figura 6.2-1 — malla x_b × P_baja.**

{{P 6.2-1}}

*Cómo se lee:* x_b (horizontal) contra P_baja (vertical), color por clase, y una **línea punteada negra** que
une la P_baja mínima KALINA de cada x_b: sube con x_b.

**Figura 6.2-2 — η una variable a la vez (10 paneles).**

{{P 6.2-2}}

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

{{T 4.1-3 | cols=Escenario;N;Omitidos;Evaluados;KALINA;Genuinos;Falsos convergidos;Fuera de rango;Factible;Criterio bloqueante;Veces que bloquea;D mínimo;η máxima [%]}}

Columnas:
{{COLS 4.1-3}}

*Lectura:* KALINA = 4, 0, 0, 6, 10 (4.1a a 4.1e); en **todos** el criterio bloqueante es O2. «Factible = no»
en 4.1b y 4.1c significa que el muestreo no encontró KALINA, **no** que no existan (4.2 los encuentra).

**Tabla 4.1-4 — Rangos por escenario (KALINA contra no KALINA).** 58 filas: por escenario y variable, los
percentiles de cada grupo y su KS. Primeras filas:

{{T 4.1-4 | n=8}}

**Tabla 4.2-3 — Frontera KALINA con las presiones del profesor.**

{{T 4.2-3}}

Columnas:
{{COLS 4.2-3}}

*Lectura:* con el clima del profesor (300.03 K): ε_cond 0.85 → 0 celdas KALINA; 0.875 → 1 (390 K); 0.90 → 2
(390–392.5); 0.925 → 4 (390–397.5); 0.95 → 9 (390–410 K). Con clima más frío (278 o 290.65 K) basta 0.85. La
mejor η es **10.81 %** (410 K, ε_cond 0.95, 300 K). Por debajo de 390 K, falla O3 (trabajo negativo) en 15 de
15.

**Tabla 4.3-3 — Escalera de conservación.**

{{T 4.3-3}}

Columnas:
{{COLS 4.3-3}}

*Lectura:* el conjunto elegido de cada ronda es el de «Elegido = sí»: x_b (15 confiables), x_b + P_alta (7),
x_b + P_alta + eficiencias (7) y **x_b + P_alta + eficiencias + P_baja (5 de 5 confiables)**. Ningún conjunto
con T_fuente da confiables; «x_b + P_alta + eficiencias + T_fuente» da 0 genuinos de 30.

**Tabla 4.3-4 — Verificación contra el motor real (1500 s).**

{{T 4.3-4 | cols=Identificador;Origen;Clase con teqp;η con teqp [%];Clase con el motor real;η con el motor real [%];Δη [pp];Coincide la clase}}

**Tabla S-4 — Datos del profesor conservables.**

{{T S-4}}

### Figuras

**Figuras 4.1-1 a 4.1-5 (una por escenario).**

{{P 4.1-1}}

*Cómo se leen:* dispersión por escenario con los dos ejes más relevantes: **4.1a** P_alta × P_baja,
**4.1b** y **4.1c** T_fuente × ε_cond, **4.1d** x_b × P_baja, **4.1e** P_alta × P_baja. Color y forma por
clase; hueco = fuera de rango. Un escenario sin marcadores verdes (4.1b y 4.1c) no encontró KALINA.

**Figura 4.2-1 (3 paneles).**

{{P 4.2-1}}

*Cómo se lee:* un panel por clima; T_fuente (horizontal) contra ε_cond (vertical). La franja de marcadores
verdes aparece a la derecha de 390 K y sube con ε_cond; en el clima de 300 K solo en las filas de ε_cond ≥
0.875.

**Figura 4.3-1 — escalera.**

{{P 4.3-1}}

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

{{T 5.1-3 | cols=Arranque;Clase del ciclo;Índice de cercanía D [–];Eficiencia térmica del ciclo, η [%];Temperatura de la fuente, T_fuente [K];Presión de alta, P_alta [kPa];Presión de baja, P_baja [kPa];Fracción de amoníaco de la mezcla base, x_b [–];Evaluaciones}}

Columnas:
{{COLS 5.1-3}}

*Lectura:* 5.1a 14.98 %, 5.1b 15.48 %, 5.1c 12.74 %, **5.1d 15.60 %**, 5.1e 11.09 %. En KALINA confiables
dentro de cada búsqueda: 98 de 102, 63 de 63, 90 de 91, 80 de 80 y **0 de 83** (5.1e).

**Tabla 5.1-2 — Corridas por parte y clase.**

{{T 5.1-2}}

### Figuras

**Figura 5.1-1.**

{{P 5.1-1}}

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

**Resultado:** sí. teqp y el motor real coinciden; el modelo reproduce los KALINA de la planta real de
Húsavík; el código reproduce al profesor; y los rankings son estables.

### Qué se hizo
- **Motor real contra teqp (6.1, 4.3):** comparación punto a punto de clase, η y márgenes.
- **Húsavík (6.2a):** re-evaluación de los 97 KALINA de septiembre (Fase 3) con el código actual.
- **Reproducibilidad (1.1):** 41 de 41 de la Fase 1.
- **Robustez (3.2):** convergencia del ranking, bootstrap, PAWN, CART.

### Tablas

**Tabla 6.1-3 — Paridad teqp contra el motor real (12 puntos).**

{{T 6.1-3 | cols=Identificador;Origen;Clase con teqp;Clase con el motor real;Coincide la clase;η con teqp [%];η con el motor real [%];Δη [pp];Dentro de la banda}}

Columnas:
{{COLS 6.1-3}}

*Lectura:* con 300 s, solo **2 de 12** terminan en el motor real (P03 de 4.2, η 10.81 %, y P08, el óptimo 5.1d,
η 15.60 %): ambos coinciden con teqp (misma clase, |Δη| < 0.001 pp). Los otros 10 se cortan **por tiempo, no
por la física**. Con 1500 s (Tabla 4.3-4), A\*, el óptimo 5.1d y Húsavík coinciden (Δη ≤ 0.003 pp).

**Tabla 6.2-3 — Catálogo Húsavík (reproducción de la Fase 3).**

{{T 6.2-3}}

Columnas:
{{COLS 6.2-3}}

*Lectura:* en las cinco familias de septiembre (F3-A a F3-E) **97 de 97 siguen siendo KALINA, ninguno cambia
de clase** y |Δη| < 10⁻¹¹ pp; **83 son confiables** (los otros 14 usan η_t o ε_cond > 0.95, tope del
proyecto). Las filas «nuevo» (B1-…, B2) son los barridos de 6.2b y 6.2c.

**Tabla 1.1-3** — reproducibilidad (ver R1).

### Figuras

**Figura 6.1-1 — paridad teqp contra motor real.**

{{P 6.1-1}}

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
- **Dice:** los resultados no dependen del motor de propiedades; el modelo coincide con una planta real,
  incluida su P_baja (690 kPa = su mínima KALINA).
- **Salvedad:** los diseños están al filo de la cavitación (R6).
- **Límites:** el motor real necesita ~1500 s por punto y solo confirmó 5; no corre la verificación B; 6.2b y
  6.2c solo con teqp; solo se re-evaluaron los KALINA de septiembre (no los corregibles); 14 de los 97 de
  septiembre usan η_t hasta 0.98 y ε_cond hasta 0.99, por encima del tope del proyecto.

> **Cómo explicarlo (30 s):** *«Verifiqué con dos motores de propiedades y dan lo mismo; reproduje los 97
> diseños de la planta real de Húsavík, incluida su presión de baja. Lo único delicado es que todos los
> diseños están pegados a la cavitación.»*

---

## R11. Visión de conjunto: la síntesis de toda la campaña

### Tabla S-1 — Resumen por estudio

{{T S-1}}

Columnas:
{{COLS S-1}}

*Lectura:* 14 estudios y 4 581 corridas (21 omitidas; 4 560 evaluadas), sin el anexo A.1. KALINA por estudio:
2.2 (59), 2.3 (20), 2.4 (153), 3.1 (86), 3.2 (121), 3.3 (75), 4.1 (20), 4.2 (104), 4.3 (181), 5.1 (419), 6.1
(142) y 6.2 (282); en total 1 662.

### Tabla S-2 — Qué se movió en cada barrido
Matriz parte × variable (58 filas): «barrido: …» en azul, «fijo: profesor» en gris y «fijo: otro valor» en
naranja. Sirve para **no comparar partes con datos distintos**. Columnas: una por variable más el piso de O2 y
el motor.

### Tabla S-3 — Rangos KALINA comparados
Para cada parte, p5, mediana y p95 de P_alta, P_baja, ΔP, r_P, T_fuente y x_b entre los KALINA confiables.

{{T S-3 | n=12}}

Columnas:
{{COLS S-3}}

### Tabla S-4 — Datos del profesor conservables (ver R8)

### Figuras de síntesis
**Figura S-1 — resultado de cada barrido.**

{{P S-1}}

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

{{HOJAS}}

---

# PARTE IV — Catálogo de tablas

Las 58 tablas, con su hoja, fuente, filtro y columnas. Las tablas `N.M-1` (condiciones) y `N.M-2` (corridas
por parte y por clase) tienen siempre las mismas columnas, definidas en R1.

{{CAT_TABLAS}}

---

# PARTE V — Catálogo de figuras

Las 30 figuras con su pie completo (título, estudio, punto base, datos fijos, barridos, filtro, n y fuente).

{{CAT_FIGURAS}}

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

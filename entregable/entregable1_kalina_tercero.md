---
title: "Análisis de sensibilidad del ciclo Kalina KCS11"
subtitle: "Entregable 1 — Formulación, verificación, resultados y conclusiones"
lang: es
---

# NOMENCLATURA

## Variables

| Símbolo | Descripción | Unidad |
|---|---|---|
| $C$ | Número de componentes químicos independientes | — |
| $\dot{E}_d$ | Exergía destruida | kW |
| $ex$ | Exergía física específica | kJ/kg |
| $F$ | Grados de libertad | — |
| $h$ | Entalpía específica | kJ/kg |
| $\dot{m}$ | Flujo másico | kg/s |
| $M$ | Masa molar | g/mol |
| $P$ | Presión | kPa |
| $\mathcal{P}$ | Número de fases en equilibrio | — |
| $q$ | Título o calidad de vapor | — |
| $\dot{Q}$ | Flujo de calor | kW |
| $s$ | Entropía específica | kJ/(kg·K) |
| $\dot{S}_{gen}$ | Entropía generada | kW/K |
| $T$ | Temperatura absoluta | K |
| $\dot{W}$ | Potencia | kW |
| $x$ | Fracción másica de amoníaco | kg NH₃ / kg mezcla |

## Letras griegas

| Símbolo | Descripción | Unidad |
|---|---|---|
| $\varepsilon$ | Efectividad de intercambiador | — |
| $\eta$ | Eficiencia térmica del ciclo | — |
| $\eta_p$ | Eficiencia isentrópica de la bomba | — |
| $\eta_t$ | Eficiencia isentrópica de la turbina | — |
| $\Phi$ | Energía libre de Helmholtz reducida | — |

## Subíndices

| Símbolo | Descripción |
|---|---|
| 0 | Estado muerto (referencia exergética) |
| 1…10 | Estados del ciclo |
| b | Solución básica |
| burbuja | Punto de burbuja |
| cond | Condensador |
| d | Destruida (exergía) |
| f | Fuente térmica |
| gen | Generada (entropía) |
| glide | Deslizamiento de temperatura |
| in | Suministrado |
| max, min | Valor límite termodinámico |
| net | Neto |
| out | Rechazado |
| p | Bomba |
| reg | Regenerador |
| rocío | Punto de rocío |
| s | Sumidero térmico |
| t | Turbina |

## Superíndices y notación auxiliar

| Símbolo | Descripción |
|---|---|
| $\circ$ | Contribución de gas ideal |
| $r$ | Contribución residual |
| $s$ (como en $h_{4s}$) | Estado isentrópico de referencia |

## Siglas

| Sigla | Significado |
|---|---|
| DCSS | *Distillation and Condensation Sub-System* |
| HRVG | *Heat Recovery Vapor Generator* |
| IAPWS | *International Association for the Properties of Water and Steam* |
| KCS | *Kalina Cycle System* |
| KCS11 | *Kalina Cycle System 11* |
| NIST | *National Institute of Standards and Technology* |
| VLE | Equilibrio líquido-vapor |

\newpage

# 1. INTRODUCCIÓN

La disponibilidad de energía constituye uno de los factores determinantes del desarrollo económico y social contemporáneo. La industria, el transporte, la climatización de espacios y la generación eléctrica dependen de un suministro continuo de energía en formas útiles, y buena parte de ese suministro proviene todavía de la conversión de energía térmica en trabajo mecánico: los combustibles fósiles, la biomasa y el calor residual de procesos industriales constituyen fuentes térmicas cuyo aprovechamiento eficiente resulta cada vez más determinante, tanto por razones económicas como por la creciente exigencia de reducir el impacto ambiental asociado a su uso (Cengel y Boles, 2012). En este contexto, la ingeniería mecánica enfrenta el reto no solo de generar energía, sino de hacerlo con la mayor eficiencia posible a partir de los recursos disponibles.

Esa exigencia ha impulsado, por un lado, la diversificación de las fuentes primarias de energía. Recursos como la radiación solar, el viento, la geotermia o la biomasa se han incorporado progresivamente a la matriz energética como alternativas o complementos a los combustibles convencionales, cada uno con su propia tecnología de conversión —paneles fotovoltaicos y colectores térmicos para la energía solar, aerogeneradores para la eólica, entre otros—. Estas fuentes, sin embargo, no agotan el potencial energético disponible: junto a ellas existe un volumen considerable de energía térmica de baja temperatura que hoy se desaprovecha o se aprovecha solo parcialmente, proveniente tanto de recursos geotérmicos de baja entalpía como del calor residual que descartan al ambiente los procesos industriales, los motores de combustión y las turbinas de gas.

Este tipo de fuentes térmicas —calor de desecho o de baja temperatura— ha recibido, en comparación con los combustibles convencionales y con las energías renovables de mayor escala, una atención tecnológica más reciente y todavía limitada. La razón es fundamentalmente termodinámica: los ciclos de potencia convencionales, como el ciclo Rankine con un fluido puro, pierden eficiencia de forma marcada al operar entre una fuente y un sumidero de temperatura moderada, porque un fluido puro evapora y condensa a temperatura constante mientras que las corrientes externas de las que se extrae o a las que se rechaza el calor varían la suya de forma continua, lo que genera diferencias de temperatura amplias —y, con ellas, una irreversibilidad considerable— en al menos una parte del intercambio térmico (Moran y Shapiro, 2004). Aprovechar eficientemente estas fuentes exige, en consecuencia, una configuración de ciclo capaz de adaptar su propio perfil térmico al de la fuente y al del sumidero disponibles.

Frente a esta necesidad surge el ciclo Kalina, propuesto por Kalina (1984), un ciclo de potencia que resuelve el problema anterior mediante un cambio en el fluido de trabajo: en lugar de una sustancia pura, emplea una mezcla binaria de amoníaco y agua. A diferencia de un fluido puro, esta mezcla cambia de fase con variación de temperatura —fenómeno conocido como deslizamiento de temperatura o *glide*— y admite además variaciones de composición entre los distintos estados del ciclo. Ambas propiedades permiten ajustar el perfil térmico del fluido de trabajo al de las corrientes externas a lo largo de todo el intercambio de calor, reduciendo la diferencia de temperatura promedio y, con ella, la irreversibilidad asociada a la transferencia de calor (Kalina, 1984).

Los beneficios de esta solución se traducen en un desempeño termodinámico superior al de los ciclos convencionales precisamente en el rango de temperaturas donde estos últimos son menos eficientes: estudios comparativos han reportado que ciclos de potencia con mezcla amoníaco-agua, como el Kalina, producen más potencia que un ciclo Rankine de vapor convencional operando como ciclo de cola sobre fuentes de calor de temperatura moderada, como los gases de escape de motores de combustión (Ibrahim y Klein, 1996; Jonsson y Yan, 2001). A esto se suma una ventaja adicional inexistente en los fluidos puros: la composición de la mezcla constituye un parámetro de ajuste propio del ciclo, que permite modificar su desempeño y su acoplamiento térmico sin alterar la configuración física de los equipos.

Estos beneficios no son solo teóricos. El ciclo Kalina cuenta con aplicaciones reales documentadas, principalmente en el aprovechamiento de recursos geotérmicos de baja y media entalpía —la planta de Húsavík, en Islandia, es el caso de referencia más citado en la literatura (Mlcak et al., 2002)— y, más recientemente, en la recuperación de calor residual de procesos industriales de alta demanda térmica. La industria cementera constituye un ejemplo particularmente pertinente: los gases del precalentador del horno y el circuito de enfriamiento de clínker liberan corrientes de gas a varios cientos de grados Celsius y con caudales del orden de decenas de kilogramos por segundo, que hoy se rechazan en buena medida sin aprovechamiento, y para las cuales ya se han propuesto y evaluado plantas Kalina de recuperación (Mirolli, 2005). Estas aplicaciones confirman que el ciclo Kalina no es una alternativa exclusivamente académica, sino una tecnología con antecedentes de implementación efectiva en el aprovechamiento de fuentes de calor que, de otro modo, se rechazarían sin utilidad.

El presente trabajo desarrolla el modelo termodinámico de un ciclo Kalina en su configuración KCS-11, alimentado por una corriente de gases de escape y enfriado mediante agua, y evalúa su comportamiento mediante dos análisis complementarios. El **análisis energético** determina el calor suministrado $\dot Q_{in}$, el calor rechazado $\dot Q_{out}$, la potencia neta $\dot W_{net}$ y la eficiencia térmica $\eta$ del ciclo. El **análisis exergético**, restringido a la exergía física —se excluye explícitamente la exergía química, justificado en la sección 13—, identifica la entropía generada y la exergía destruida en cada componente, lo que permite distinguir cuáles de ellos concentran las mayores irreversibilidades del sistema: a diferencia de un análisis puramente energético, que trataría por igual una pérdida de calor al ambiente y una irreversibilidad interna del mismo tamaño en kW, el balance exergético revela cuál de las dos representa una pérdida real de capacidad de producir trabajo (Moran y Shapiro, 2004).

El modelo se implementa en Python, empleando como motor de propiedades una implementación de la formulación de referencia de Tillner-Roth y Friend (1998) —adoptada por la *International Association for the Properties of Water and Steam* como guía IAPWS G4-01 (IAPWS, 2001)—, verificada de forma cruzada contra una segunda implementación independiente de la misma ecuación de estado (criterio C6, sección 7). La herramienta computacional cumple, no obstante, un papel instrumental: el centro del análisis permanece en el comportamiento termodinámico del sistema, y la arquitectura del código que lo resuelve no es objeto de este documento. Disponer de un modelo computacional no garantiza, además, una representación fiel del ciclo si no incorpora las condiciones no ideales de su operación: por ello el modelo contempla eficiencias isentrópicas para la turbina y la bomba, y efectividades para los tres intercambiadores de calor —el generador de vapor de recuperación de calor, el regenerador interno y el condensador—, alejando deliberadamente el análisis del modelo ideal.

La estructura del documento responde a esa finalidad. La sección 3 expone el fundamento termodinámico de la mezcla amoníaco-agua y de la exergía física, necesario para interpretar correctamente los estados del ciclo y los resultados del balance de irreversibilidades. La sección 4 describe la configuración analizada y sus componentes. La sección 5 declara las hipótesis bajo las cuales opera el modelo. La sección 6 desarrolla la formulación matemática completa, energética y exergética, que describe cada proceso y sobre la cual se construye el modelo implementado. La sección 7 declara los criterios de verificación que el modelo aplica sobre sus propios resultados. La sección 8 resume el respaldo del modelo frente a normas, simuladores y modelos publicados, y la sección 9 describe el diseño de la campaña de barridos con que se explora su comportamiento. La sección 10 presenta los resultados organizados por pregunta, la sección 11 el análisis de sensibilidad y la sección 12 las conclusiones. La sección 13 cierra el documento declarando el alcance y las limitaciones del modelo y de los resultados bajo los cuales se plantea el análisis.

\newpage

# 2. OBJETIVOS

## 2.1 Objetivo general

Modelar termodinámicamente un ciclo Kalina KCS-11, alimentado por una corriente de gases de escape y enfriado mediante agua, para evaluar su desempeño energético y exergético bajo condiciones reales de operación.

## 2.2 Objetivos específicos

- Formular los balances de masa, especie y energía de cada componente del ciclo, incorporando eficiencias isentrópicas en turbina y bomba, y efectividades en los intercambiadores de calor.
- Formular el balance de exergía física del ciclo, determinando la entropía generada y la exergía destruida por componente a partir de un estado muerto de referencia.
- Establecer los criterios de verificación —restricciones de segunda ley e identidades de cierre— que permiten comprobar la consistencia interna del modelo antes de emplearlo para evaluar el desempeño del ciclo.
- Declarar explícitamente el alcance y las simplificaciones bajo las cuales se plantea el modelo, distinguiendo lo que el análisis cubre de lo que queda fuera de su propósito.

\newpage

# 3. MARCO TEÓRICO

## 3.1 Comportamiento zeotrópico de mezclas binarias

Una mezcla zeotrópica, también llamada no azeotrópica, es aquella cuyos componentes tienen puntos de ebullición distintos, de modo que sus fases líquida y vapor en equilibrio presentan composiciones diferentes entre sí y distintas de la composición global de la mezcla. Su condición opuesta es la mezcla azeotrópica, que a presión constante cambia de fase a temperatura constante y se comporta, dentro de un circuito termodinámico, de manera equivalente a un fluido puro.

El principio físico que gobierna una mezcla zeotrópica es sencillo de enunciar: al combinar dos sustancias con volatilidades distintas, la fase vapor que se forma durante una evaporación parcial se enriquece en el componente más volátil, mientras que la fase líquida residual se empobrece en él (Elsayed et al., 2013). Por ser el amoníaco el componente de menor punto de ebullición del par NH₃-H₂O, el vapor generado en una evaporación parcial de la mezcla resulta siempre más rico en amoníaco que el líquido del cual proviene. Este comportamiento zeotrópico, sistemáticamente reportado en la literatura sobre ciclos de potencia y sistemas de absorción para el sistema amoníaco-agua (Tillner-Roth y Friend, 1998), constituye el fundamento físico que el ciclo Kalina aprovecha en su separador: al no coexistir las dos fases con la misma composición, es posible extraer de una única corriente bifásica dos corrientes de propiedades distintas, una rica en amoníaco destinada a producir trabajo y otra pobre en amoníaco destinada a la recuperación interna de calor.

## 3.2 Deslizamiento de temperatura (*glide*)

El deslizamiento de temperatura se define como la diferencia entre las temperaturas de rocío y de burbuja de la mezcla, evaluadas a presión y composición global constantes:

$$\Delta T_{glide} = T_{rocío}(P,\,x) - T_{burbuja}(P,\,x) \qquad (1)$$

Para una sustancia pura, la temperatura de rocío coincide con la de burbuja a cualquier presión dada, de modo que el cambio de fase ocurre a temperatura constante. Para una mezcla zeotrópica, en cambio, ambas temperaturas se separan, y el cambio de fase transcurre a lo largo de un intervalo continuo de temperatura mientras la composición de cada fase varía progresivamente desde el líquido saturado hasta el vapor saturado.

La consecuencia de este fenómeno sobre el desempeño de un intercambiador de calor es directa. Cuando el fluido de trabajo es una sustancia pura, su temperatura permanece constante durante el cambio de fase mientras la corriente externa (gases de escape o agua de enfriamiento) varía la suya de forma continua; la diferencia de temperatura entre ambas corrientes resulta entonces necesariamente amplia en alguna región del intercambiador, y esa diferencia finita de temperatura constituye, por sí misma, una fuente de generación de entropía. Al emplear una mezcla zeotrópica, el fluido de trabajo también varía su temperatura durante el cambio de fase, lo que permite que su perfil térmico se aproxime al de la corriente externa a lo largo de todo el intercambiador, reduciendo la diferencia de temperatura promedio y, con ella, la irreversibilidad asociada a la transferencia de calor (Kalina, 1984; Ibrahim y Klein, 1996). Esta es la razón termodinámica que sustenta el empleo de la mezcla amoníaco-agua en el ciclo Kalina, y el motivo por el cual el análisis exergético de la sección 6.3 resulta especialmente informativo en este ciclo: permite cuantificar, componente por componente, cuánto de esa reducción teórica de irreversibilidad se materializa realmente bajo las condiciones de operación declaradas.

El deslizamiento no es, sin embargo, una propiedad libre de elegir: para una composición global $x$ dada, $\Delta T_{glide}$ queda fijado por la propia termodinámica de la mezcla a cada presión, y solo puede modificarse cambiando esa composición. Esta dependencia es la que conecta el fenómeno con la regla de fases desarrollada en la sección 3.3: el deslizamiento es, en el fondo, la manifestación observable de que, en la región bifásica de una mezcla binaria, temperatura y composición de cada fase están acopladas por los dos grados de libertad disponibles, y no son ajustables de forma independiente.

## 3.3 Regla de fases de Gibbs

El número de propiedades intensivas independientes que deben especificarse para fijar por completo el estado intensivo de un sistema en equilibrio se obtiene de la regla de fases de Gibbs, un resultado general de la termodinámica del equilibrio que no depende de la sustancia particular que se analice:

$$F = C - \mathcal{P} + 2 \qquad (2)$$

donde $F$ es el número de grados de libertad, $C$ el número de componentes químicos independientes y $\mathcal{P}$ el número de fases presentes en equilibrio. El término aditivo 2 corresponde a las dos variables intensivas que pueden fijarse con independencia de la composición: la presión y la temperatura. Su origen se encuentra en un argumento de conteo: antes de imponer el equilibrio, cada una de las $\mathcal{P}$ fases se describe con $C+1$ variables intensivas propias (su temperatura, su presión y $C-1$ fracciones de composición, pues la fracción restante queda fijada por la condición de que todas sumen la unidad), lo que da un total de $\mathcal{P}(C+1)$ variables. El equilibrio entre las fases impone tres condiciones: igual temperatura, igual presión e igual potencial químico de cada uno de los $C$ componentes en todas ellas; cada una de estas $C+2$ condiciones equivale a $\mathcal{P}-1$ ecuaciones independientes (igualar cada fase con una fase de referencia), de modo que el equilibrio introduce $(\mathcal{P}-1)(C+2)$ ecuaciones de restricción en total. Restando estas restricciones del total de variables se obtiene $F = \mathcal{P}(C+1) - (\mathcal{P}-1)(C+2) = C - \mathcal{P} + 2$.

Para una sustancia pura, $C=1$, y la regla predice que basta con dos propiedades independientes para fijar un estado monofásico ($F=2$), y una sola para fijar un estado de saturación ($F=1$, la razón por la cual, dada la presión, la temperatura de saturación de una sustancia pura queda determinada sin ambigüedad, y no admite un deslizamiento como el descrito en la sección 3.2).

La mezcla amoníaco-agua tiene $C=2$, de donde resultan dos situaciones de interés:

| Situación | $\mathcal{P}$ | $F$ | Especificaciones requeridas |
|---|---|---|---|
| Región monofásica (líquido o vapor) | 1 | 3 | Presión, temperatura (o entalpía) y composición |
| Región bifásica (equilibrio líquido-vapor) | 2 | 2 | Presión y temperatura únicamente |

La consecuencia de este resultado es doble y gobierna toda la especificación de estados del ciclo (sección 6.1). En primer lugar, a diferencia de una sustancia pura, para la cual bastan dos propiedades en región monofásica, **una mezcla binaria monofásica exige tres especificaciones independientes** —normalmente presión, una propiedad energética y composición—, porque la composición es ahora una variable de estado adicional y no un dato fijo del fluido. En segundo lugar, y de manera menos intuitiva, en la región bifásica quedan solamente dos grados de libertad: una vez fijadas la presión y la temperatura, **las composiciones de las fases líquida y vapor en equilibrio quedan determinadas por la termodinámica de la mezcla** y no pueden imponerse de forma independiente. Esta segunda consecuencia es la que rige el comportamiento del separador del ciclo: las composiciones de las corrientes de vapor y de líquido que abandonan ese equipo no son datos del problema, sino resultado del equilibrio evaluado a la presión y temperatura del estado que entra a él, y es la misma razón por la cual el deslizamiento de temperatura de la sección 3.2 queda determinado y no es un parámetro libre del modelo.

## 3.4 Formulaciones de propiedades para la mezcla amoníaco-agua

La determinación de las propiedades termodinámicas de una mezcla como la de amoníaco y agua no la resuelve una única expresión universalmente aceptada: distintas formulaciones, desarrolladas en momentos distintos y con rangos de validez diferentes, compiten por representar su comportamiento no ideal. Para una mezcla zeotrópica, los estados termodinámicos son funciones fuertemente no lineales de las propiedades independientes empleadas para calcularlos, y su evaluación en la región bifásica exige resolver un equilibrio de fases líquido-vapor en cada punto de estado, no una simple interpolación de tablas (Rattner y Garimella, 2015).

Ziegler y Trepp (1984) propusieron una de las formulaciones de mayor uso histórico, basada en una relación fundamental válida hasta aproximadamente 5 MPa. Ibrahim y Klein (1993) extendieron esa formulación ajustando sus coeficientes a datos de mayor presión e incorporando una corrección basada en fugacidad, con lo que alcanzaron validez hasta aproximadamente 11 MPa; su correlación trata la fase gaseosa como solución ideal y recurre a la energía de Gibbs de exceso para representar el apartamiento del comportamiento ideal en la fase líquida, con un rango declarado de 0.2 a 110 bar y de 230 a 600 K.

La formulación de Tillner-Roth y Friend (1998), adoptada por la *International Association for the Properties of Water and Steam* como guía G4-01, constituye la representación de mayor exactitud disponible para las propiedades de las fases fluidas de la mezcla en un amplio rango de condiciones (IAPWS, 2001). Es una ecuación fundamental para la energía libre de Helmholtz molar reducida, expresada como

$$\Phi(\tau,\,\delta,\,x) = \frac{f}{RT} = \Phi^{\circ}(\tau,\,\delta,\,x) + \Phi^{r}(\tau,\,\delta,\,x) \qquad (3)$$

donde $\Phi^{\circ}$ corresponde a la contribución de gas ideal y $\Phi^{r}$ a la contribución residual, construida a partir de los residuales del agua pura y del amoníaco puro más una función de partida empírica que representa la desviación respecto del comportamiento de mezcla ideal (IAPWS, 2001). Formular la mezcla como una única energía libre —en lugar de combinar por separado las propiedades de sus componentes puros— es lo que permite derivar de ella, de forma termodinámicamente consistente, tanto las propiedades monofásicas como el equilibrio líquido-vapor que gobierna el separador y que da lugar al deslizamiento de temperatura de la sección 3.2. Esta formulación es válida en las fases líquida y vapor hasta 40 MPa a temperaturas subcríticas, con incertidumbres declaradas de ±0.01 en las fracciones molares de líquido y vapor en coexistencia (hasta ±0.04 cerca del lugar geométrico crítico) y de 1-2% en las densidades de las fases monofásicas (IAPWS, 2001).

Este trabajo adopta la formulación de Tillner-Roth y Friend como referencia teórica. Su elección frente a las anteriores responde tanto a su mayor exactitud declarada como a que su rango de validez cubre con holgura las condiciones de presión y temperatura del ciclo analizado, condición que las formulaciones de Ziegler y Trepp o de Ibrahim y Klein no garantizan de forma igualmente amplia; los criterios que verifican en la práctica que cada estado del ciclo permanece dentro de ese rango, junto con las dos implementaciones computacionales independientes empleadas para evaluarla, se presentan en la sección 7.

## 3.5 Fundamento del análisis exergético

La exergía de un flujo de materia cuantifica el trabajo máximo que podría obtenerse al llevar dicho flujo, de manera reversible, hasta el equilibrio termomecánico con un ambiente de referencia (Moran y Shapiro, 2004). Ese ambiente se caracteriza por un **estado muerto**, definido por una temperatura $T_0$ y una presión $P_0$ de referencia. Cuando el análisis se restringe a la componente física de la exergía —dejando fuera la exergía química, asociada al desequilibrio de composición entre la corriente y un ambiente de referencia universal—, el estado muerto de cada corriente se evalúa a $(T_0, P_0)$ **conservando la composición propia de esa corriente**, y no una composición ambiental externa. Esta distinción es la que separa conceptualmente la exergía física de la química: la primera solo exige enfriar y despresurizar la corriente hasta las condiciones ambientales sin alterar su composición; la segunda exigiría además una "desmezcla" hasta los componentes puros de referencia del ambiente, proceso que este trabajo no evalúa (sección 8).

Con esa definición, la exergía física específica de una corriente se expresa como

$$ex = (h - h_0) - T_0(s - s_0) \qquad (4)$$

donde $h_0 = h(P_0, T_0, x)$ y $s_0 = s(P_0, T_0, x)$ se evalúan con la composición $x$ propia de la corriente.

La segunda ley establece que todo proceso real genera entropía, y que esa entropía generada, evaluada a la temperatura del ambiente de referencia, mide directamente la exergía destruida —trabajo potencial perdido de forma irrecuperable— por ese proceso (Kotas, 1985; Moran y Shapiro, 2004):

$$\dot E_d = T_0 \dot S_{gen} \qquad (5)$$

Esta relación es la que permite, en la sección 6.3, calcular la exergía destruida en cada componente del ciclo a partir de un balance de entropía en estado estacionario, sin necesidad de evaluar directamente el trabajo perdido de cada proceso.

\newpage

# 4. DESCRIPCIÓN DEL SISTEMA

## 4.1 Configuración analizada

Bajo la denominación genérica de ciclo Kalina se agrupa una familia de configuraciones que, compartiendo el uso de la mezcla amoníaco-agua, difieren en su disposición de componentes y se identifican mediante designaciones propias según la fuente térmica a la que van dirigidas: el KCS5 se destina a plantas de combustión directa, el KCS6 a ciclos combinados con turbina de gas, y el KCS11 y el KCS34 a la explotación de fuentes de baja y media temperatura (Elsayed et al., 2013). La configuración analizada en este trabajo corresponde topológicamente al **Kalina Cycle System 11 (KCS11)**, que consta de generador de vapor de recuperación de calor, separador, turbina, regenerador, válvula de estrangulamiento, absorbedor, condensador y bomba (Elsayed et al., 2013). Una característica distintiva del KCS11 frente a configuraciones de mayor escala como el KCS5 es que **no incorpora un subsistema de destilación y condensación**: su separador opera en un único nivel de presión, inmediatamente aguas abajo del generador de vapor, sin reconcentración adicional a baja presión (Zhang et al., 2012).

![Configuración del ciclo Kalina KCS-11 analizado.](figura1_ciclo.png){width=90%}

*Figura 1. Configuración del ciclo Kalina KCS-11 analizado. Los estados numerados 1 a 10 corresponden a los definidos en la sección 4.3; las interacciones térmicas con la fuente y el sumidero se representan únicamente a través del fluido de trabajo, conforme a la hipótesis H8 (sección 5). Elaboración propia.*

Los componentes se agrupan funcionalmente según el nivel de presión en el que operan:

| Subsistema | Componentes | Nivel de presión |
|---|---|---|
| Generación y separación | HRVG, separador | Alta |
| Expansión | Turbina | Alta → Baja |
| Recuperación interna | Regenerador, válvula | Alta → Baja |
| Absorción y condensación | Absorbedor, condensador | Baja |
| Bombeo | Bomba | Baja → Alta |

## 4.2 Componentes y funcionamiento

**Generador de vapor de recuperación de calor (HRVG), 1 → 2.** Recibe la solución básica precalentada procedente del regenerador y le transfiere calor desde la corriente de gases de escape, evaporándola parcialmente. A diferencia de un generador de vapor convencional, no incorpora sección de sobrecalentamiento: su corriente de salida debe permanecer bifásica, porque alimenta al separador, componente que exige precisamente ese estado para operar. El equipo se modela como un volumen de control único, con una sola entrada, una sola salida y una única interacción térmica con la fuente externa.

**Separador, 2 → 3 y 5.** Recibe la corriente bifásica proveniente del HRVG y la divide en sus dos fases en equilibrio: una corriente de vapor rica en amoníaco, que se dirige a la turbina, y una corriente de líquido pobre en amoníaco, que se dirige al regenerador. Este componente es el elemento que distingue estructuralmente al ciclo Kalina de un ciclo Rankine convencional: al operar sobre una mezcla zeotrópica, la separación produce dos corrientes de composición distinta entre sí y distinta de la composición de entrada, lo que introduce un grado de libertad adicional inexistente en los fluidos puros (sección 3.3). Opera sin interacción de calor ni de trabajo con el exterior.

**Turbina, 3 → 4.** Expande la corriente rica en amoníaco desde la presión de alta hasta la de baja, produciendo trabajo mecánico. La expansión real se aparta del comportamiento isentrópico ideal, apartamiento que se cuantifica mediante una eficiencia isentrópica.

**Regenerador, 5 → 6 (lado caliente) y 10 → 1 (lado frío).** Intercambiador interno en contracorriente que aprovecha la corriente líquida caliente proveniente del separador para precalentar la solución básica descargada por la bomba, antes de su ingreso al generador de vapor. Su función es recuperar internamente energía que de otro modo se rechazaría al sumidero, reduciendo el calor que debe suministrar la fuente externa. No intercambia calor con el exterior.

**Válvula de estrangulamiento, 6 → 7.** Reduce la presión de la corriente pobre en amoníaco desde el nivel de alta hasta el de baja, para permitir su recombinación posterior con la descarga de la turbina. Al no realizar trabajo ni intercambiar calor apreciable, el proceso es isoentálpico e intrínsecamente irreversible: toda caída de presión sin producción de trabajo genera entropía.

**Absorbedor, 4 y 7 → 8.** Recibe simultáneamente la corriente 4 —vapor húmedo rico en amoníaco, procedente de la turbina— y la corriente 7 —líquido pobre en amoníaco, procedente de la válvula—, ambas ya al nivel de presión de baja, condición necesaria para que puedan ponerse en contacto directo sin equipo mecánico adicional. Al mezclarse, la fase líquida pobre en amoníaco absorbe una parte del vapor de la corriente rica: el amoníaco se disuelve en el agua hasta que la mezcla alcanza una única composición y un único estado de equilibrio, el de la composición básica $x_b$. Este es el fenómeno que da nombre al componente y al ciclo, y es el mismo principio que opera en los sistemas de refrigeración por absorción: la absorción de un vapor en un líquido con el que tiene afinidad es un proceso exotérmico, de modo que, aunque el equipo no intercambia calor con el exterior (adiabático), internamente se libera calor de mezcla que eleva la entalpía de la corriente resultante por encima de la que tendría una simple mezcla mecánica sin cambio de fase.

El resultado termodinámico de este mecanismo es el que justifica la existencia del componente dentro del ciclo. El vapor rico en amoníaco que sale de la turbina, por sí solo, condensaría a la presión de baja a una temperatura sensiblemente inferior a la que el agua de enfriamiento disponible puede alcanzar. Al absorberse en la corriente pobre y recuperar la composición básica —más rica en agua—, la mezcla resultante presenta, a esa misma presión, una temperatura de rocío compatible con el sumidero: el absorbedor es, en ese sentido, el paso que hace posible que el condensador aguas abajo pueda operar con el sumidero de enfriamiento disponible. En la configuración analizada se modela como una cámara de mezcla adiabática, sin equipo mecánico ni intercambio térmico con el exterior; los balances de masa, especie y energía que gobiernan su salida se desarrollan en la sección 6.2.6.

**Condensador, 8 → 9.** Rechaza calor hacia la corriente de agua de enfriamiento, llevando la solución básica a estado líquido apto para el bombeo. Constituye la única interacción térmica del ciclo con el sumidero.

**Bomba, 9 → 10.** Eleva la presión de la solución básica desde el nivel de baja hasta el de alta, consumiendo trabajo. Al igual que la turbina, su comportamiento real se aparta del isentrópico.

## 4.3 Tabla de corrientes

La tabla siguiente resume, de forma exclusivamente descriptiva, el origen, destino, nivel de presión y fase esperada de cada uno de los diez estados del ciclo, así como la relación entre sus composiciones. No incluye valores numéricos de operación: estos corresponden a datos de un caso de estudio particular y se reservan para el Entregable 2, conforme al alcance declarado en la sección 8.

| Estado | Origen → Destino | Nivel de presión | Fase esperada | Concentración |
|---|---|---|---|---|
| 1 | Regenerador → HRVG | Alta | Líquido | $x_b$ |
| 2 | HRVG → Separador | Alta | Bifásico | $x_b$ |
| 3 | Separador → Turbina | Alta | Vapor saturado | $x_3 > x_b$ |
| 4 | Turbina → Absorbedor | Baja | Vapor húmedo | $x_3$ |
| 5 | Separador → Regenerador | Alta | Líquido saturado | $x_5 < x_b$ |
| 6 | Regenerador → Válvula | Alta | Líquido | $x_5$ |
| 7 | Válvula → Absorbedor | Baja | Líquido subenfriado o bifásico$^*$ | $x_5$ |
| 8 | Absorbedor → Condensador | Baja | Bifásico | $x_b$ |
| 9 | Condensador → Bomba | Baja | Líquido | $x_b$ |
| 10 | Bomba → Regenerador | Alta | Líquido | $x_b$ |

Las concentraciones $x_3$ y $x_5$ no son datos del problema, sino resultado del equilibrio líquido-vapor evaluado a la presión y temperatura del estado 2, conforme a la regla de fases desarrollada en la sección 3.3.

$^*$El estado 7 no tiene una fase fija de antemano: al ser la válvula isoentálpica (H6, ecuación (21)), su fase depende de cuánto caiga la presión respecto a la presión de saturación del líquido de entrada (estado 6) a esa misma entalpía y composición. Una caída de presión pequeña puede dejar la corriente como líquido subenfriado; una caída mayor produce una expansión súbita (*flash*) que la lleva a la región bifásica. Cuál de los dos casos ocurre es, por tanto, un resultado del cálculo y no un supuesto del modelo.

\newpage

# 5. HIPÓTESIS DEL MODELO

Las hipótesis siguientes delimitan por completo el alcance físico del modelo y se invocan explícitamente en la formulación de la sección 6 al reducir cada balance a su forma final. Su propósito es dejar constancia exhaustiva de las condiciones bajo las cuales el modelo es válido, de modo que cualquier resultado obtenido con él se interprete dentro de ese marco y no más allá de él.

**H1. Estado estacionario.** Todos los balances se plantean en régimen permanente, sin acumulación de masa ni de energía en ningún volumen de control. El análisis no contempla arranques, paradas ni transitorios de carga.

**H2. Energías cinética y potencial despreciables.** Las variaciones de energía cinética y potencial entre estados son de un orden muy inferior a las variaciones de entalpía asociadas a los procesos de intercambio de calor y de trabajo, por lo que se omiten de los balances de energía.

**H3. Caídas de presión y pérdidas de calor en tuberías despreciables.** La presión permanece constante dentro de cada nivel (alta o baja), y las tuberías de interconexión no intercambian calor con el ambiente. Bajo esta hipótesis, habitual en el análisis del KCS11, el sistema queda descrito por dos únicos niveles de presión independientes.

**H4. Cada equipo se modela como un volumen de control único.** No se resuelve la distribución interna de secciones ni los perfiles internos de temperatura de ningún intercambiador; el comportamiento de cada componente se considera como un todo, gobernado por una eficiencia o una efectividad global. Esta hipótesis es la que permite cerrar el intercambio de calor mediante efectividades en lugar de coeficientes globales de transferencia y áreas, cuyo dimensionamiento queda fuera del alcance de este documento.

**H5. Separador ideal.** Las corrientes de vapor y de líquido abandonan el separador en equilibrio termodinámico mutuo, a la misma temperatura y presión que el estado de entrada, como vapor saturado y líquido saturado respectivamente. No se considera arrastre de líquido en la corriente de vapor ni de vapor en la corriente de líquido.

**H6. Estrangulamiento isoentálpico.** La válvula no realiza trabajo ni intercambia calor apreciable, y las variaciones de energía cinética a través de ella son despreciables conforme a H2.

**H7. Absorbedor adiabático.** El absorbedor se modela como una cámara de mezcla sin intercambio de calor con el exterior; la totalidad del calor rechazado por el ciclo se transfiere en el condensador.

**H8. Fuente y sumidero como reservorios de capacidad térmica infinita.** La fuente de gases de escape y el sumidero de enfriamiento se modelan como reservorios a temperatura constante, $T_f$ y $T_s$ respectivamente, sin considerar la capacidad calorífica finita de sus corrientes reales ($\dot m_{fuente}\cdot c_{p,fuente}$ y su análogo en el sumidero). Esta simplificación desacopla la evaluación del ciclo de un caudal de gas o de agua específico; sus implicaciones se declaran explícitamente en la sección 8.

**H9. Eficiencias isentrópicas y efectividades constantes.** Las eficiencias isentrópicas de turbina y bomba, y las efectividades de los tres intercambiadores de calor, se toman como parámetros constantes del modelo, independientes del punto de operación evaluado.

**H10. Exergía física únicamente.** El análisis exergético considera solo la componente física de la exergía; se excluye la exergía química. En consecuencia, el estado muerto de cada corriente se evalúa a $(T_0, P_0)$ conservando la composición propia de esa corriente ($x_0 = x_{corriente}$), y no una composición ambiental universal, conforme al fundamento expuesto en la sección 3.5.

**H11. Presión de referencia del estado muerto como parámetro configurable.** La temperatura de referencia $T_0$ se fija a partir de la condición ambiental declarada del sumidero; la presión de referencia $P_0$ no se deriva de ningún dato termodinámico propio del problema, por lo que se trata como un parámetro configurable, con un valor por defecto atmosférico estándar.

**H12. Validez restringida al rango declarado del backend de propiedades.** Todo estado del ciclo debe evaluarse dentro del rango de presión y temperatura en el que la formulación de la sección 3.4 es válida (hasta 40 MPa, en fase subcrítica). Un estado que caiga fuera de ese rango no se extrapola: se reporta como no resuelto, conforme al criterio de verificación correspondiente (sección 7).

\newpage

# 6. FORMULACIÓN MATEMÁTICA APLICADA

## 6.1 Grados de libertad y especificación de estados

Conforme a la regla de fases desarrollada en la sección 3.3, cada estado monofásico del ciclo requiere tres especificaciones independientes. En todos los casos, dos de ellas corresponden a la presión y a la composición, quedando la tercera determinada por una ecuación propia del modelo. Los estados 3 y 5, situados sobre las curvas de equilibrio del separador, se determinan en cambio mediante presión, temperatura y la identificación de la fase (vapor o líquido saturado).

| Estado | Especificación 1 | Especificación 2 | Especificación 3 | Origen de la tercera |
|---|---|---|---|---|
| 1 | $P_{alta}$ | $x_b$ | $h_1$ | Balance del regenerador, Ec. (18) |
| 2 | $P_{alta}$ | $x_b$ | $h_2$ | Cierre del HRVG, Ec. (9) |
| 3 | $P_{alta}$ | $T_3=T_2$ | $q_3=1$ | Equilibrio en el separador |
| 4 | $P_{baja}$ | $x_4=x_3$ | $h_4$ | Eficiencia de la turbina, Ec. (16) |
| 5 | $P_{alta}$ | $T_5=T_2$ | $q_5=0$ | Equilibrio en el separador |
| 6 | $P_{alta}$ | $x_6=x_5$ | $h_6$ | Cierre del regenerador, Ec. (20) |
| 7 | $P_{baja}$ | $x_7=x_5$ | $h_7=h_6$ | Válvula, Ec. (21) |
| 8 | $P_{baja}$ | $x_b$ | $h_8$ | Balance del absorbedor, Ec. (24) |
| 9 | $P_{baja}$ | $x_b$ | $h_9$ | Cierre del condensador, Ec. (26) |
| 10 | $P_{alta}$ | $x_b$ | $h_{10}$ | Eficiencia de la bomba, Ec. (28) |

## 6.2 Balances energéticos

### 6.2.1 Generador de vapor de recuperación de calor (1 → 2)

Balance de masa y de especie:

$$\dot m_1 = \dot m_2 = \dot m_b \qquad (6)$$
$$x_2 = x_1 = x_b \qquad (7)$$

Balance de energía, conforme a H1, H2 y H3:

$$\dot Q_{in} = \dot m_b (h_2 - h_1) \qquad (8)$$

Ecuación de cierre: la efectividad se define sobre el fluido de trabajo, tomando como estado límite el que alcanzaría dicho fluido si fuese llevado hasta la temperatura de la fuente, a igual presión y composición:

$$\varepsilon_{HRVG} = \frac{h_2 - h_1}{h_{2,max} - h_1}, \qquad h_{2,max} = h(T_f,\,P_{alta},\,x_b) \qquad (9)$$

Que el estado límite $h_{2,max}$ se evalúe directamente a la temperatura de la fuente $T_f$, y no a partir de un balance conjunto entre el fluido de trabajo y la corriente de gases, es una consecuencia directa de H8: al modelarse la fuente como un reservorio de capacidad térmica infinita, su temperatura no cambia por ceder calor al fluido de trabajo, de modo que $T_f$ es, en sí misma, la cota que ningún estado del fluido puede superar. Si en cambio la fuente se modelara como una corriente real de capacidad finita ($\dot m_{fuente}\cdot c_{p,fuente}$), el límite termodinámico ya no sería la temperatura de entrada de la fuente, sino el estado que resultaría de un intercambio de calor ideal (a contracorriente, sin pinzamiento) entre las dos corrientes reales; ese límite dependería entonces de cuál de las dos corrientes tiene la capacidad térmica mínima, siguiendo la misma lógica que gobierna la efectividad del regenerador en la sección 6.2.4, y ya no se reduciría a evaluar una propiedad a una única temperatura fija.

Si esta ecuación resultase inaplicable —por situar el estado límite fuera de la región en que el separador puede operar (H5), o fuera del rango de validez declarado en H12— se reporta como no resuelto en lugar de sustituirla por un supuesto adicional no verificado.

### 6.2.2 Separador (2 → 3 y 5)

Balances de masa, especie y energía:

$$\dot m_2 = \dot m_3 + \dot m_5 \qquad (10)$$
$$\dot m_2\,x_2 = \dot m_3\,x_3 + \dot m_5\,x_5 \qquad (11)$$
$$\dot m_2\,h_2 = \dot m_3\,h_3 + \dot m_5\,h_5 \qquad (12)$$

Condición de separación ideal, conforme a H5:

$$T_3 = T_5 = T_2, \qquad P_3 = P_5 = P_{alta}, \qquad q_3 = 1,\ q_5 = 0 \qquad (13)$$

La ecuación (13) determina por completo las composiciones $x_3$ y $x_5$. De las ecuaciones (10) y (11) se obtiene la forma resuelta del reparto de flujos, conocida como regla de la palanca:

La ecuación (12) no es, en cambio, una ecuación de resolución independiente: una vez fijadas las composiciones $x_3$ y $x_5$ por la ecuación (13) y los flujos $\dot m_3$, $\dot m_5$ por las ecuaciones (10) y (11), la entalpía $h_2$ del estado bifásico de entrada queda determinada por definición del título como $h_2 = (1-q_2)h_5 + q_2 h_3$, con $q_2 = \dot m_3/\dot m_2$; la ecuación (12) resulta entonces satisfecha automáticamente por esa misma relación, sin aportar información adicional al sistema. Se incluye en la formulación como identidad de verificación —para comprobar a posteriori que una solución cumple el balance de energía del separador dentro de una tolerancia numérica pequeña— y no como una ecuación que se resuelva junto con las demás.

$$\dot m_3 = \dot m_b\,\frac{x_b - x_5}{x_3 - x_5} \qquad (14)$$

### 6.2.3 Turbina (3 → 4)

Estado isentrópico de referencia y eficiencia isentrópica:

$$s_{4s} = s_3,\quad P_{4s} = P_{baja} \;\Rightarrow\; h_{4s} \qquad (15)$$
$$\eta_t = \frac{h_3 - h_4}{h_3 - h_{4s}} \qquad (16)$$

Potencia desarrollada:

$$\dot W_t = \dot m_3 (h_3 - h_4) \qquad (17)$$

### 6.2.4 Regenerador (5 → 6 lado caliente; 10 → 1 lado frío)

Balance de energía del intercambiador, adiabático hacia el exterior:

$$\dot m_5 (h_5 - h_6) = \dot m_b (h_1 - h_{10}) \qquad (18)$$

La corriente a la que se refiere la efectividad es la de menor capacidad térmica, $C = \dot m \, c_p$, y no simplemente la de menor flujo másico: al ser $C$ el producto del flujo másico por el calor específico, y al tener el lado caliente ($x_5$, más pobre en amoníaco) y el lado frío ($x_b$, la composición básica) calores específicos distintos por su distinta composición, la sola condición $\dot m_5 < \dot m_b$ no basta, en rigor, para concluir que $C_5 < C_b$. Lo que decide la comparación es que el amoníaco líquido tiene un calor específico mayor que el del agua líquida en el rango de temperaturas del regenerador, de modo que la corriente más pobre en amoníaco ($x_5 < x_b$) tiene también el calor específico menor; este efecto composicional refuerza, en lugar de contrarrestar, la ventaja que ya aporta $\dot m_5 < \dot m_b$, y es lo que permite afirmar con seguridad que $\dot m_5\, c_{p,5} < \dot m_b\, c_{p,10}$ y no solo $\dot m_5 < \dot m_b$. El estado límite corresponde, por tanto, al líquido caliente enfriado hasta la temperatura de entrada de la corriente fría:

$$h_{6,min} = h(T_{10},\,P_{alta},\,x_5) \qquad (19)$$
$$\varepsilon_{reg} = \frac{h_5 - h_6}{h_5 - h_{6,min}} \qquad (20)$$

### 6.2.5 Válvula de estrangulamiento (6 → 7)

Conforme a H6, el balance de energía se reduce a la conservación de la entalpía:

$$h_7 = h_6 \qquad (21)$$

### 6.2.6 Absorbedor (4 y 7 → 8)

Balance de masa y de especie, del cual se recupera la composición básica:

$$\dot m_8 = \dot m_4 + \dot m_7 = \dot m_b \qquad (22)$$
$$\dot m_8\,x_8 = \dot m_4\,x_4 + \dot m_7\,x_7 \;\Rightarrow\; x_8 = x_b \qquad (23)$$

Balance de energía, sin términos de calor ni de trabajo conforme a H7:

$$\dot m_8\,h_8 = \dot m_4\,h_4 + \dot m_7\,h_7 \qquad (24)$$

### 6.2.7 Condensador (8 → 9)

Balance de energía:

$$\dot Q_{out} = \dot m_b (h_8 - h_9) \qquad (25)$$

Ecuación de cierre, definida de forma análoga a la ecuación (9), tomando el sumidero como referencia:

$$\varepsilon_{cond} = \frac{h_8 - h_9}{h_8 - h_{9,min}}, \qquad h_{9,min} = h(T_s,\,P_{baja},\,x_b) \qquad (26)$$

Al igual que en el HRVG, que $h_{9,min}$ se evalúe directamente a la temperatura del sumidero $T_s$ es consecuencia de H8: el sumidero, como reservorio de capacidad infinita, fija esa temperatura como cota sin que ceder calor la modifique. Esta definición presupone, además, que el estado límite $(T_s, P_{baja}, x_b)$ cae en la región de líquido —solo así $h_{9,min}$ representa un líquido más frío que el que el condensador podría entregar, y la efectividad conserva su sentido de "fracción de lo máximo alcanzable". Esa condición no está garantizada de antemano: si la temperatura del sumidero fuese mayor que la temperatura de burbuja de la mezcla a $P_{baja}$ y $x_b$, el estado $(T_s, P_{baja}, x_b)$ sería bifásico o vapor, y ningún condensador, por grande que fuera, podría enfriar la corriente 9 hasta ese límite manteniéndola líquida; la ecuación (26) perdería entonces su interpretación física, aunque siguiera siendo evaluable como expresión algebraica. Por eso la validez de la ecuación (26) exige verificar, antes de aplicarla, que $T_s < T_{burbuja}(P_{baja},\,x_b)$ — condición que se incorpora explícitamente al criterio C7 (sección 7).

### 6.2.8 Bomba (9 → 10)

Estado isentrópico de referencia y eficiencia isentrópica:

$$s_{10s} = s_9,\quad P_{10s} = P_{alta} \;\Rightarrow\; h_{10s} \qquad (27)$$
$$\eta_p = \frac{h_{10s} - h_9}{h_{10} - h_9} \qquad (28)$$

Potencia consumida:

$$\dot W_p = \dot m_b (h_{10} - h_9) \qquad (29)$$

### 6.2.9 Desempeño global

$$\dot W_{net} = \dot W_t - \dot W_p \qquad (30)$$
$$\eta = \frac{\dot W_{net}}{\dot Q_{in}} \qquad (31)$$

## 6.3 Balances exergéticos

La exergía física específica de cada corriente se evalúa con la ecuación (4). La exergía destruida en cada componente se obtiene de la relación (5), a partir de un balance de entropía en estado estacionario planteado sobre ese mismo componente, sin generación de entropía en las corrientes en sí mismas —solo en los procesos que las conectan—.

**HRVG** (calor $\dot Q_{in}$ suministrado por la fuente, modelada como reservorio a $T_f$ conforme a H8):

$$\dot S_{gen,HRVG} = \dot m_b (s_2 - s_1) - \frac{\dot Q_{in}}{T_f} \qquad (32)$$

**Separador** (adiabático, sin trabajo):

$$\dot S_{gen,sep} = \dot m_3\,s_3 + \dot m_5\,s_5 - \dot m_2\,s_2 \qquad (33)$$

**Turbina** (adiabática, mismo caudal en 3 y 4):

$$\dot S_{gen,turb} = \dot m_3 (s_4 - s_3) \qquad (34)$$

**Regenerador** (intercambio interno, sin calor con el ambiente; suma de ambos lados):

$$\dot S_{gen,reg} = \dot m_5 (s_6 - s_5) + \dot m_b (s_1 - s_{10}) \qquad (35)$$

**Válvula** (adiabática):

$$\dot S_{gen,val} = \dot m_5 (s_7 - s_6) \qquad (36)$$

**Absorbedor** (adiabático, mezcla):

$$\dot S_{gen,abs} = \dot m_8\,s_8 - \dot m_4\,s_4 - \dot m_7\,s_7 \qquad (37)$$

**Condensador** (calor $\dot Q_{out}$ rechazado al sumidero, modelado como reservorio a $T_s$ conforme a H8):

$$\dot S_{gen,cond} = \dot m_b (s_9 - s_8) + \frac{\dot Q_{out}}{T_s} \qquad (38)$$

**Bomba** (adiabática):

$$\dot S_{gen,bomba} = \dot m_b (s_{10} - s_9) \qquad (39)$$

La exergía destruida total del ciclo es la suma de las ocho contribuciones anteriores, cada una llevada a exergía mediante la ecuación (5):

$$\dot E_{d,total} = T_0 \sum_i \dot S_{gen,i} \qquad (40)$$

\newpage

# 7. CRITERIOS DE VERIFICACIÓN Y ADMISIBILIDAD

El modelo formulado en la sección 6 no se da por válido con solo resolverse: debe además satisfacer un conjunto de restricciones derivadas directamente de las leyes de la termodinámica, cuyo cumplimiento certifica que la solución obtenida es físicamente admisible. Cada criterio se presenta junto con su justificación termodinámica, de modo que quede claro no solo qué verifica el modelo, sino por qué esa verificación es necesaria y qué indica su incumplimiento.

**C1. No cruce de temperaturas en el regenerador.**

$$T_6 \ge T_{10}, \qquad T_1 \le T_5 \qquad (41)$$

*Justificación:* en un intercambiador de calor real, la corriente caliente no puede salir a una temperatura inferior a la de entrada de la corriente fría, ni la corriente fría puede salir a una temperatura superior a la de entrada de la corriente caliente, sin que ello implique una transferencia de calor en sentido contrario al gradiente de temperatura —una violación directa de la segunda ley. Este criterio es el que, en la práctica, acota qué tan alta puede ser la efectividad $\varepsilon_{reg}$ declarada sin generar una solución físicamente inconsistente.

**C2. Eficiencia térmica acotada por el límite de Carnot.**

$$\eta < \eta_{Carnot} = 1 - \frac{T_s}{T_f} \qquad (42)$$

*Justificación:* ningún ciclo que opere entre dos reservorios a $T_f$ y $T_s$ puede superar la eficiencia del ciclo de Carnot equivalente, cota superior teórica impuesta por la segunda ley (Cengel y Boles, 2012). Una solución que la excediera indicaría necesariamente un error de formulación o de cómputo, nunca un desempeño real del ciclo.

**C3. Identidad del balance global de energía.**

$$\dot Q_{in} - \dot Q_{out} - \dot W_{net} = 0 \qquad (43)$$

*Justificación:* esta relación no es una ecuación adicional que se resuelve, sino una consecuencia algebraica de sumar los ocho balances de energía de la sección 6.2 y cancelar por pares las entalpías internas del ciclo. Verificarla a posteriori sobre la solución obtenida constituye una prueba de consistencia interna independiente de la formulación misma: si no se cumple dentro de una tolerancia numérica pequeña, la implementación contiene un error, con independencia de que cada balance individual se haya planteado correctamente.

**C4. Identidad del balance global de exergía.**

$$\dot{Ex}_{Q_i} - \dot W_{net} - \dot{Ex}_{Q_{out}} \approx \dot E_{d,total} \qquad (44)$$

donde $\dot{Ex}_{Q_i} = \dot Q_{in}(1 - T_0/T_f)$ y $\dot{Ex}_{Q_{out}} = \dot Q_{out}(1 - T_0/T_s)$ son, respectivamente, la exergía entregada por la fuente y la que abandona el ciclo junto con el calor rechazado. *Justificación:* de forma análoga a C3, esta identidad es la verificación cruzada del balance exergético de la sección 6.3: la exergía neta que entra al ciclo debe repartirse exactamente entre el trabajo neto producido y la exergía destruida en el conjunto de los ocho componentes. Es, además, la única verificación disponible para las ecuaciones (32)-(40) que no depende de un valor de referencia externo, porque compara al modelo consigo mismo.

**C5. Validez de los estados dentro del rango declarado del motor de propiedades.**

*Justificación:* la formulación de la sección 3.4 garantiza sus incertidumbres declaradas únicamente dentro del rango de presión y temperatura en el que fue ajustada y validada (hasta 40 MPa, en fase subcrítica). Evaluar un estado fuera de ese rango no constituye un error de cómputo detectable por las identidades anteriores, sino un uso del modelo fuera de su dominio de validez; por ello se verifica de forma independiente y explícita en cada estado, conforme a H12.

**C6. Verificación cruzada entre dos implementaciones independientes de la ecuación de estado.**

*Justificación:* la formulación teórica de la sección 3.4 admite, en principio, más de una implementación computacional, y una implementación puede introducir errores propios de su código que la formulación teórica en sí misma no comete. Este trabajo emplea como motor principal el paquete `iapws`, que expone la ecuación de Tillner-Roth y Friend (1998) con dos correcciones documentadas sobre su derivada composicional —necesarias porque la distribución original del paquete presentaba un error tipográfico en un exponente y omitía un término de la regla del producto en esa derivada—, verificado contra las tablas de referencia de la guía G4-01 con errores relativos máximos inferiores a 4×10⁻³ %. Como verificación independiente de que esa implementación no arrastra un error propio de su código, se emplea una segunda implementación construida sobre la librería `teqp`, que expone la misma ecuación de estado (`teqp.AmmoniaWaterTillnerRoth`, distribución de dominio público del NIST) complementada con `CoolProp` para la contribución de gas ideal de los componentes puros, sobre la cual se reimplementó el mismo algoritmo de equilibrio líquido-vapor por sustitución sucesiva que emplea la implementación principal, en lugar de recurrir a las rutinas de flash de `teqp`, cuya robustez numérica con semillas genéricas resultó insuficiente en pruebas previas. Ambas implementaciones parten de la misma ecuación fundamental y difieren solo en la biblioteca numérica subyacente y en la referencia de entalpía/entropía de cada una —diferencia que se cancela en cualquier cálculo de ciclo, dependiente únicamente de $\Delta h$ y $\Delta s$ entre estados—, de modo que su coincidencia es una comprobación que ninguna de las dos podría ofrecer por sí sola. La implementación principal permanece como camino de cálculo por defecto; la segunda se reserva como referencia de contraste, dado su menor volumen de validación exhaustiva frente a las tablas de la guía G4-01.

**C7. Consistencia de fase en el separador, en el estado límite del condensador y en la succión de la bomba.**

*Justificación:* el separador exige que el estado 2 sea bifásico para poder repartirlo en sus dos fases en equilibrio (H5); un estado 2 monofásico invalida la operación de ese componente y no es un caso que el separador ideal pueda resolver. La ecuación de cierre del condensador (26) exige, a su vez, que el estado límite $(T_s, P_{baja}, x_b)$ caiga en la región de líquido, es decir, que $T_s < T_{burbuja}(P_{baja}, x_b)$ (sección 6.2.7); si esa condición no se cumple, la efectividad $\varepsilon_{cond}$ pierde su interpretación física y no puede usarse como ecuación de cierre. De forma análoga, la bomba exige succión en fase líquida: un estado 9 bifásico implicaría cavitación o compresión de una mezcla de dos fases, condición que la formulación de la ecuación (27) no contempla. Las tres condiciones se verifican explícitamente sobre la solución antes de aceptarla como admisible.

\newpage

# 8. VERIFICACIÓN Y CONTRASTE DEL MODELO

Antes de interpretar los resultados conviene precisar qué respaldo tiene el modelo formulado en la sección 6, porque de ese respaldo depende el alcance de toda conclusión posterior. La formulación se ha sometido a seis comprobaciones de naturaleza distinta, resumidas en la Tabla 10. Su resultado conjunto es que el modelo está **verificado y contrastado con modelos publicados; no cuenta con validación experimental**, porque no se dispone de mediciones de planta con las que compararlo.

| Comprobación | Referencia | Resultado | Alcance |
|---|---|---|---|
| Propiedades | IAPWS G4-01 (IAPWS, 2001) | 44 de 44 valores evaluables dentro de tolerancia (1 punto en la vecindad del lugar crítico no converge); error relativo máximo < 4×10⁻³ % | Verifica el motor de propiedades, no el ciclo |
| Dos motores | `iapws` frente a `teqp` | 6 de 6 puntos; \|Δη\| < 0.002 pp; temperaturas de estado < 0.03 K | Dos implementaciones de la misma ecuación de estado |
| Ciclo, mismo cierre | DWSIM con Peng-Robinson | 6 ciclos: Δη de +0.02 a +0.37 pp; caso Elsayed con efectividades: +0.59 pp | Respalda la estructura del modelo, no sus propiedades |
| Estados, segunda fuente | Nemati et al. (2017) | Temperaturas de estado dentro de 2.5 K; un punto a 5000 kPa | Compara estados, no η |
| Ciclo, modelo publicado | Elsayed et al. (2013) | 23 puntos: Δη medio −0.06 pp; \|Δη\| medio 0.28 pp; máximo 1.16 pp | Una sola fuente de η |
| Banda de η | G4-01 propagada al ciclo | ±0.4 a ±0.7 pp | Tres puntos de operación |

*Nota.* Elaboración propia a partir de los reportes de verificación del proyecto (`prompts/VALIDACION_ELSAYED2013.md`, `resultados/2026-10-03_validacion_dwsim`, `resultados/2026-10-03_benchmark_nemati`, `resultados/2026-10-03_incertidumbre_eta`, `docs/PLANTEAMIENTO_MATEMATICO.md`). Δη: diferencia de eficiencia térmica entre la fuente externa y el modelo, o entre motores, en puntos porcentuales (pp).

**Propiedades y motores.** El motor de propiedades reproduce las tablas oficiales de la guía IAPWS G4-01 (IAPWS, 2001), basada en la formulación de Tillner-Roth y Friend (1998): los 44 valores evaluables quedan dentro de la tolerancia (un punto en la vecindad del lugar crítico no converge y queda sin evaluar), con errores relativos máximos inferiores a 4×10⁻³ % (criterio C6, sección 7). La segunda implementación, construida sobre `teqp`, coincide con el motor principal en la eficiencia a menos de 0.002 pp en los seis puntos comparados. Esta coincidencia descarta un error propio del código de cada implementación, pero no dice nada sobre la ecuación de estado compartida.

**Contraste con DWSIM.** DWSIM, un simulador de procesos independiente, se empleó con las mismas ecuaciones de cierre por efectividad, de modo que la única diferencia restante es el modelo de propiedades (Peng-Robinson en DWSIM, Tillner-Roth y Friend en este trabajo). En seis ciclos a 3000 kPa de presión alta, con sumidero a 283 K y eficiencias isentrópicas de 0.80, DWSIM da una eficiencia mayor entre +0.02 y +0.37 pp, conserva el orden de los seis ciclos y los balances internos cuadran en ambos. La diferencia disminuye al aumentar la fracción de amoníaco. En el caso de Elsayed con efectividades, la diferencia es de +0.59 pp, que se reparte casi por mitades entre las propiedades y la forma del cierre (el cierre por pinch de 4 K en DWSIM da 12.20 %, frente a 11.64 % con efectividad y 11.05 % en este trabajo). DWSIM con Peng-Robinson no resolvió los ciclos de 4000 a 5000 kPa, de modo que esa zona queda sin esta comprobación.

**Segunda fuente independiente.** Nemati et al. (2017), de la Facultad de Ingeniería Mecánica de la Universidad de Tabriz, resuelven en EES un KCS-11 con la misma topología y publican sus nueve estados (x_b = 0.90; 5000 y 1061 kPa; η_t = 0.85; η_p = 0.75; gases a 429 K). Con las efectividades calibradas para reproducir tres de sus temperaturas, las temperaturas de los estados que la calibración no fija quedan dentro de 2.5 K, la temperatura de burbuja a la salida del condensador difiere en +0.39 K y la composición de amoníaco en el vapor difiere en −0.006 (fracción molar), dentro de la incertidumbre de ±0.01 de la guía. La composición del líquido difiere en −0.014, apenas fuera de ese margen, lo que se traduce en un 2 % más de vapor enviado a la turbina (0.891 frente a 0.873). Dos reservas acompañan este contraste: la fuente no publica la eficiencia del Kalina para ese caso, de modo que se comparan estados y no η; y la efectividad del condensador calibrada (0.9787) excede el tope de 0.95 que rige el resto del trabajo, porque es una calibración inversa y no un caso de diseño.

**Modelo publicado de Elsayed et al.** Frente a las curvas de Elsayed et al. (2013), 23 de 33 condiciones de operación resultaron comparables. La diferencia media con signo es de −0.06 pp, la diferencia absoluta media es de 0.28 pp (mediana relativa de 2.4 %) y el máximo es de 1.16 pp; el modelo reproduce la forma de las curvas y la posición de su máximo. En el caso puntual citado en el artículo, la eficiencia publicada es de 11.38 % y la calculada, de 11.05 %.

**Banda de incertidumbre de η.** Se propagó a η la incertidumbre publicada de la guía G4-01 (equilibrio líquido-vapor de ±0.01 en fracción molar y entalpía de exceso de ±200 J/mol), perturbando una magnitud a la vez en tres puntos de operación. La banda resultante es de +0.46/−0.34 pp en el caso Elsayed (11.06 %), +0.59/−0.46 pp en KALINA-01 (10.37 %) y +0.45/−0.42 pp en KALINA-11 (12.15 %); es decir, **±0.4 a ±0.7 pp**, y casi toda proviene del equilibrio líquido-vapor del separador. Con ella, la diferencia de 0.33 pp frente a Elsayed y la diferencia media de 0.28 pp del benchmark caben dentro de lo que el propio modelo de propiedades no puede asegurar. La diferencia de +0.59 pp frente a DWSIM en el caso Elsayed y el máximo de 1.16 pp quedan fuera de la banda; el segundo no se ha analizado todavía y se declara como una discrepancia abierta.

**Lo que este respaldo no es.** Todas las comprobaciones se hacen contra otras simulaciones o contra valores publicados por modelos; la eficiencia solo se contrasta con **una fuente** (Elsayed et al., 2013) y ninguna comprobación utiliza datos experimentales de planta. El caso de Húsavík (Mlcak et al., 2002) se emplea más adelante como contraste de qué rangos convergen, no de una potencia medida.

\newpage

# 9. DISEÑO DE LA CAMPAÑA DE BARRIDOS

## 9.1 Punto de partida y preguntas

El enunciado del curso fija un KCS-11 con una fuente de gases a 623.15 K y un sumidero a 300.03 K. El conjunto de datos de partida, que en adelante se denomina *punto del profesor*, es: P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50, T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85, ε_reg = 0.75 y ε_cond = 0.80, con un flujo de base de cálculo de 1 kg/s. Son diez datos de diseño; el flujo másico de solución básica nunca se varió en la campaña. Un segundo punto, el *punto ancla A\**, difiere del anterior en dos datos (T_fuente = 403 K y P_baja = 563.64 kPa), resulta KALINA (η = 8.48 %) y sirve de base a los estudios locales.

La campaña respondió seis preguntas, que ordenan los estudios y la numeración de las tablas y figuras de origen: (1) si el ciclo funciona con los datos del profesor; (2) qué es lo mínimo que hay que cambiar para que funcione; (3) qué variables importan y cuánto; (4) qué datos del profesor pueden conservarse; (5) cuánta eficiencia puede lograrse; y (6) si los resultados son confiables. Cada estudio se identifica con el número de su pregunta seguido de un ordinal (por ejemplo, estudio 3.2) y, cuando agrupa casos con datos fijos distintos, con una letra por parte (3.2a).

## 9.2 Clasificación de los puntos

Cada punto resuelto se clasifica en cuatro niveles. **KALINA** es un régimen Kalina genuino que cumple todos los criterios; **CORREGIBLE** es un punto admisible solo con un ajuste de diseño (falla el título de turbina, O1, o la cavitación, O2); **INVIABLE** viola un criterio físico que no puede ajustarse (segunda ley, operación del separador, orden de composiciones); y **NO_CONVERGIO** es un punto en que el solver no llegó a una solución. Los tres primeros niveles son puntos *genuinos*. Se identifican además los *falsos convergidos* (N2): soluciones que el solver reporta como convergidas pero que el clasificador descarta, y que se cuentan como no convergidas. Los criterios de la clasificación se nombran O1 (título del vapor), O2 (cavitación: el líquido debe llegar a la bomba por debajo de su temperatura de burbuja), O3 (trabajo neto positivo) y O5 (separador bifásico).

Un punto es **KALINA confiable** cuando es KALINA, no tiene ninguna marca de fuera de rango del modelo de propiedades (IAPWS, 2001) y sus eficiencias isentrópicas y efectividades están en [0.40, 0.95]. La eficiencia térmica se trata como resultado secundario: el objetivo de la campaña es determinar el rango de operación KALINA conservando la mayor cantidad posible de datos del profesor.

## 9.3 Diseños y métodos

La campaña reúne 4 741 corridas en 14 estudios y un anexo; 4 581 corresponden a los 14 estudios (Tabla 11, Figura 2) y el resto, a un anexo con equipos fuera del rango realista que no entra en las conclusiones. Los métodos se eligieron según la pregunta:

- **Factibilidad (preguntas 1 y 2):** mallas de una y dos variables con bisección de fronteras, partiendo del punto del profesor.
- **Sensibilidad local (estudio 3.1):** una variable a la vez (*OAT*) con 15 valores equiespaciados por variable alrededor de A\*, más perturbaciones de ±1 % para la elasticidad local.
- **Sensibilidad global (estudios 3.2 y 3.3):** muestreo por hipercubo latino (*LHS*) de 500 puntos, formado por dos muestreos de 300 y 200 puntos dentro de una caja de rangos realistas, analizado con filtrado Monte Carlo (RSA) con el estadístico de Kolmogorov-Smirnov (KS), coeficiente de correlación parcial por rangos (PRCC), PAWN y árboles CART, con intervalos bootstrap de 1000 remuestreos. La caja abarca T_fuente de 380 a 500 K, T_sumidero de 278 a 303.5 K, P_alta de 2000 a 5000 kPa, P_baja de 300 a 1500 kPa y x_b de 0.50 a 0.85, con las eficiencias y efectividades dentro de rangos realistas. Los métodos de Morris, Sobol y FAST se descartaron porque no toleran los puntos NO_CONVERGIO, que son parte del resultado.
- **Conservación de datos (pregunta 4):** muestreos LHS por escenario, una malla dirigida con las presiones del profesor y una escalera de selección hacia adelante.
- **Eficiencia máxima (pregunta 5):** búsqueda por patrones, primero hacia KALINA y después hacia η, desde cinco arranques.
- **Confiabilidad (pregunta 6):** contraste entre motores en puntos clave y re-evaluación del caso de Húsavík.

Dos reglas de presentación gobiernan los resultados: los puntos con datos fijos distintos nunca se mezclan en una misma tabla o figura, y toda diferencia de η menor que la banda de ±0.4 a ±0.7 pp (sección 8) se considera no concluyente.

| Estudio | Nombre | Corridas | Genuinas | KALINA | KALINA confiables | Falsos convergidos |
|---|---|---|---|---|---|---|
| 1.1 | Repetir el caso del profesor | 42 | 0 | 0 | 0 | 0 |
| 2.1 | Un solo cambio | 132 | 15 | 0 | 0 | 21 |
| 2.2 | Dos cambios | 180 | 165 | 59 | 48 | 12 |
| 2.3 | Dos cambios con η y ε en 0.40–0.95 | 225 | 154 | 20 | 1 | 4 |
| 2.4 | Sumidero más frío | 320 | 269 | 153 | 119 | 0 |
| 3.1 | Sensibilidad local alrededor de A\* | 171 | 148 | 86 | 86 | 6 |
| 3.2 | Sensibilidad global (500 puntos) | 500 | 452 | 121 | 83 | 13 |
| 3.3 | P_baja alta (1500–2500 kPa) | 150 | 120 | 75 | 45 | 6 |
| 4.1 | Escenarios de conservación | 600 | 382 | 20 | 2 | 12 |
| 4.2 | Mapa con las presiones del profesor | 165 | 149 | 104 | 104 | 15 |
| 4.3 | Escalera de conservación | 987 | 806 | 181 | 118 | 29 |
| 5.1 | Búsqueda de la η máxima | 560 | 549 | 419 | 331 | 1 |
| 6.1 | Verificación con el motor de referencia | 167 | 151 | 142 | 137 | 0 |
| 6.2 | Planta real de Húsavík | 382 | 347 | 282 | 268 | 16 |

*Nota.* Elaboración propia a partir de `analisis_final/02_tablas/S/Tabla_S-1.md`. Excluye el anexo de equipos fuera del rango realista.
![Resultado de cada barrido por clase.](fig02_resultado_por_barrido.png){width=90%}

*Figura 2. Resultado de cada barrido por clase de punto. Una barra por estudio, sin el anexo. Elaboración propia a partir de la tabla canónica de la campaña (`analisis_final/03_figuras/S/Figura_S-1`).*

\newpage

# 10. RESULTADOS POR PREGUNTA

## 10.1 Pregunta 1: ¿funciona el ciclo con los datos del profesor?

No. El estudio 1.1 repite el caso del profesor en cuatro partes (el punto exacto, P_alta de 2000 a 4000 kPa, x_b de 0.40 a 0.70 y la temperatura ambiente hora a hora, con 297.95 a 303.55 K) y el resultado es el mismo en todas: ninguna de las 42 corridas converge (Tabla 12). La clase coincide con la obtenida en la primera fase del proyecto en 41 de 41 puntos comparables.

| Parte | Corridas | Genuinas | KALINA | No convergidas |
|---|---|---|---|---|
| 1.1a · punto del profesor | 2 | 0 | 0 | 2 |
| 1.1b · solo P_alta | 9 | 0 | 0 | 9 |
| 1.1c · solo x_b | 7 | 0 | 0 | 7 |
| 1.1d · temperatura ambiente horaria | 24 | 0 | 0 | 24 |

*Nota.* Fuente: Tabla 1.1-2 de `analisis_final/02_tablas`. Los demás datos permanecen en el punto del profesor.

**Interpretación y límite.** El resultado indica que el bloqueo no está en la presión alta, la composición ni el clima, y apunta al lado caliente. Debe leerse con cautela: el código reproduce el fallo previo, lo que no prueba que el modelo sea correcto, solo que es consistente con él.

## 10.2 Pregunta 2: ¿qué es lo mínimo que hay que cambiar?

La Tabla 13 resume los cuatro estudios de la pregunta. Con un solo cambio no hay ningún KALINA (estudio 2.1): de 132 corridas, solo T_fuente, ε_HRVG y x_b producen puntos genuinos, y el más cercano es T_fuente = 402.9 K, que falla únicamente O2 por 2.0 K (η = 9.86 %). Con dos cambios, conservar la fuente del profesor y mover ε_HRVG con P_baja da 0 KALINA en 36 puntos genuinos; en cambio, mover T_fuente con P_baja da 59 KALINA (48 confiables) con T_fuente entre 390 y 434 K, con P_baja mínima de 445.5 kPa a 390 K (η = 2.45 %) y η máxima de 9.15 % a 420 K y 736 kPa. De esa malla se toma A\*.

Cuando las eficiencias y efectividades se restringen a [0.40, 0.95] (estudio 2.3), conservar la fuente del profesor solo produce KALINA bajando ε_HRVG a 0.40–0.50 y subiendo P_baja a 1318–2000 kPa (13 puntos distintos, todos fuera de rango). El único KALINA confiable conserva las dos presiones del profesor, con T_fuente = 403 K y ε_cond = 0.95 (η = 9.50 %).

| Estudio | Qué se cambió | KALINA (confiables) | Resultado principal |
|---|---|---|---|
| 2.1 | Una variable | 0 | Más cercano: T_fuente = 402.9 K, falla O2 por 2.0 K |
| 2.2 | Dos variables, ruta A (fuente del profesor) | 0 | 36 genuinos, todos bloqueados por O2 |
| 2.2 | Dos variables, ruta B (T_fuente × P_baja) | 59 (48) | T_fuente 390–434 K; η máx. 9.15 % |
| 2.3 | Dos variables con η y ε en 0.40–0.95 | 20 filas (1) | Con 623 K, solo fuera de rango |
| 2.4 | Sumidero más frío con P_baja libre | 153 (119) | P_baja mínima baja 43–48 % con 22 K menos |

*Nota.* Fuente: Tabla S-1 y verificación cruzada A4 (V04, V05, V08) de `analisis_final`. El estudio 2.3 contiene 14 puntos KALINA distintos en sus 20 filas.

El estudio 2.4 muestra que el clima del sitio es una palanca de primer orden. Con tres bases de T_fuente (403 K, 420 K y 623 K con ε_HRVG = 0.40), un sumidero 22 K más frío (278.15 K en lugar de 300.03 K) reduce la P_baja mínima KALINA de 562.5 a 290.6 kPa, de 740.6 a 393.8 kPa y de 1312.5 a 750 kPa (reducciones de 48 %, 47 % y 43 %), y eleva η máxima de 8.49 a 10.41 %, de 9.11 a 11.91 % y de 6.30 a 9.69 % (Figura 3). La tercera base solo contiene KALINA fuera de rango, y con los datos exactos del profesor ningún sumidero produce KALINA.

![Efecto del sumidero sobre la P_baja mínima y la η máxima.](fig03_sumidero_pbaja_eta.png){width=90%}

*Figura 3. Un sumidero más frío reduce la P_baja mínima de KALINA y aumenta η, para tres bases con datos fijos distintos. Elaboración propia a partir de `analisis_final/03_figuras/2.4/Figura_2.4-1`.*

**Interpretación y límite.** El mínimo cambio que produce un KALINA confiable es bajar la fuente a unos 400 K (y ajustar P_baja o el sumidero); no existe un cambio único. Con los datos exactos del profesor, el clima no basta. Las figuras muestran qué ocurre, pero no explican por sí solas la causa física, que se discute en la sección 11.

## 10.3 Pregunta 3: ¿qué variables importan y cuánto?

La respuesta cuantitativa se desarrolla en la sección 11; aquí se presentan los rangos de operación que el muestreo global identifica. De los 500 puntos del estudio 3.2, 452 son genuinos y 121 son KALINA (83 confiables); 222 puntos quedan fuera del rango del modelo de propiedades. El 90 % de los KALINA tiene P_baja de 683 a 1461 kPa y razón de presiones r_P de 1.7 a 5.3 (Tabla 14, Figura 4), mientras que P_alta y ΔP no discriminan (KS de 0.149 y 0.100).

| Variable | p5 | Mediana | p95 | KS | Valor p |
|---|---|---|---|---|---|
| P_alta [kPa] | 2156 | 3571 | 4842 | 0.149 | 0.035 |
| P_baja [kPa] | 683 | 1183 | 1461 | 0.437 | < 0.001 |
| ΔP [kPa] | 968 | 2464 | 3718 | 0.100 | 0.311 |
| r_P [–] | 1.69 | 3.11 | 5.34 | 0.347 | < 0.001 |

*Nota.* Fuente: Tabla 3.2-5 de `analisis_final/02_tablas/3.2`. Percentiles de los 121 KALINA; KS frente a los 331 puntos genuinos que no son KALINA (n = 500 en total).

![Distribución de ΔP y r_P en los puntos KALINA.](fig04_hist_dP_rP.png){width=90%}

*Figura 4. El 90 % de los KALINA tiene ΔP de 968 a 3718 kPa y r_P de 1.7 a 5.3. Elaboración propia a partir de `analisis_final/03_figuras/3.2/Figura_3.2-4`.*

**Interpretación y límite.** El techo de 1461 kPa de P_baja es el borde de la caja muestreada (303 a 1498 kPa), no una frontera física: el estudio 3.3, con P_baja de 1500 a 2500 kPa, encuentra 75 KALINA (45 confiables) en 120 puntos genuinos, y concluye que lo que limita una P_baja alta es que r_P tiende a 1 y que η es baja (mediana de 4.29 %), no la cavitación. La P_baja mínima KALINA depende de P_alta: baja de 913 kPa con P_alta de 2000 a 2500 kPa a 547 kPa con 3500 a 4000 kPa, y deja de bajar por encima de 4000 kPa.

## 10.4 Pregunta 4: ¿qué datos del profesor pueden conservarse?

Los muestreos aleatorios por escenario (estudio 4.1, 600 corridas) muestran que conservar la fuente de 623 K casi nunca produce KALINA confiable: de 20 KALINA solo 2 son confiables, con P_baja de 1.36 a 1.97 MPa y x_b de 0.71 a 0.83, es decir, lejos del enunciado. Conservar las dos presiones y el clima no produce ninguno, pero ese resultado se debe a que la franja es angosta y el muestreo no la encuentra.

La malla dirigida del estudio 4.2 la encuentra (Figura 5): con P_alta = 3000 kPa y P_baja = 400 kPa hay 104 KALINA, todos confiables, en 165 corridas, con T_fuente de 390 a 410 K. En el clima de 300.03 K, ε_cond = 0.85 no produce ninguno, 0.875 lo hace solo a 390 K, 0.90 hasta 392.5 K, 0.925 hasta 397.5 K y 0.95 hasta 410 K; con sumideros de 290.65 K y 278.15 K basta 0.85. La mejor eficiencia es de 10.81 % (410 K, ε_cond = 0.95, 300.03 K) y fue confirmada por el motor de referencia. Por debajo de 390 K el trabajo neto es negativo (O3).

![Franja KALINA con las presiones del profesor.](fig05_franja_presiones_profesor.png){width=90%}

*Figura 5. Con las presiones del profesor hay KALINA desde T_fuente ≈ 390 K; con su clima (300 K) hace falta ε_cond de 0.875 (a 390 K) a 0.95 (a 410 K). Elaboración propia a partir de `analisis_final/03_figuras/4.2/Figura_4.2-1`.*

La escalera del estudio 4.3 selecciona hacia adelante los datos que pueden conservarse (Tabla 15). El conjunto final conserva P_alta, P_baja, x_b y las cinco eficiencias y efectividades, es decir, 8 de los 10 datos; solo se mueven T_fuente (391 a 409 K) y T_sumidero (280 a 293 K), con 5 KALINA confiables y η hasta 10.6 %. Todos los conjuntos que conservan T_fuente = 623.15 K dan 0 KALINA confiables.

| Ronda | Datos conservados | Datos del profesor | Evaluadas | Genuinas | KALINA | Confiables |
|---|---|---|---|---|---|---|
| 0 | x_b | 1 | 100 | 85 | 29 | 15 |
| 1 | x_b + P_alta | 2 | 30 | 28 | 11 | 7 |
| 2 | x_b + P_alta + eficiencias | 7 | 30 | 28 | 13 | 7 |
| 3 | x_b + P_alta + eficiencias + P_baja | 8 | 30 | 28 | 5 | 5 |
| 3 | x_b + P_alta + eficiencias + T_fuente | 8 | 30 | 0 | 0 | 0 |

*Nota.* Fuente: Tabla 4.3-3 de `analisis_final/02_tablas/4.3` (filas elegidas en cada ronda y la alternativa con T_fuente). Los demás datos se barren dentro de la caja del estudio.

**Interpretación y límite.** La fuente a 623 K es incompatible con el resto del enunciado; el resto de los datos es conservable si la fuente baja a unos 390–410 K y el sumidero o ε_cond acompañan. La T_fuente mayor que 410 K no se exploró en el estudio 4.2, y los muestreos de los estudios 4.1 y 4.3 son exploraciones, no mapas completos.

## 10.5 Pregunta 5: ¿cuánta eficiencia puede lograrse?

Con equipos de eficiencia media la eficiencia térmica ronda 8 a 11 % (A\*: 8.48 %; mejor punto de la franja del estudio 4.2: 10.81 %). La búsqueda del estudio 5.1 llega a **15.60 %** conservando las presiones y el clima del profesor (arranque A4), con T_fuente = 415 K y η_t, ε_HRVG, ε_reg y ε_cond en 0.95 (η_p = 0.805). Es el mejor punto aceptado de una búsqueda convergida; las búsquedas 5.1a y 5.1b se detuvieron todavía subiendo, de modo que sus 14.98 y 15.48 % son cotas inferiores (Tabla 16, Figura 6).

| Arranque | Qué conserva | η máx. [%] | T_fuente [K] | P_alta [kPa] | P_baja [kPa] | x_b | KALINA confiables |
|---|---|---|---|---|---|---|---|
| A1 | Nada (desde 3.2) | 14.98 | 436.1 | 4382 | 808.3 | 0.705 | 98 de 102 |
| A2 | Nada (desde 2.4) | 15.48 | 420.0 | 3000 | 393.8 | 0.500 | 63 de 63 |
| A3 | Temperaturas del profesor | 12.74 | 623.1 | 5000 | 1360 | 0.850 | 90 de 91 |
| A4 | Presiones y clima del profesor | 15.60 | 415.0 | 3000 | 400.0 | 0.500 | 80 de 80 |
| A5 | Fuente y x_b del profesor | 11.09 | 623.1 | 4808 | 1022 | 0.500 | 0 de 83 |

*Nota.* Fuente: Tabla 5.1-3 de `analisis_final/02_tablas/5.1` y Tabla S-1. A1 y A2 son cotas inferiores (búsqueda sin converger).

![Búsqueda de la eficiencia máxima.](fig06_busqueda_eta.png){width=90%}

*Figura 6. La búsqueda llega a η = 15.6 % dentro de la región KALINA con equipos a 0.95. Elaboración propia a partir de `analisis_final/03_figuras/5.1/Figura_5.1-1`.*

**Interpretación y límite.** Los óptimos quedan pegados a la frontera de O2: durante la búsqueda se rechazaron evaluaciones con η cercana a 17 % porque violaban la restricción. El valor de 15.6 % es el mayor η encontrado con equipos de 0.95, no un máximo demostrado ni un diseño; conservar a la vez la fuente y la x_b del profesor (A5) no produjo ningún KALINA confiable.

## 10.6 Pregunta 6: ¿son confiables los resultados?

**Motor de referencia.** Se re-evaluaron 12 puntos clave de la campaña con el motor real (`iapws`). En el tiempo asignado, 2 de los 12 resolvieron en ambos motores, con coincidencia de clase y diferencias de η de 9×10⁻⁵ y 3×10⁻⁴ pp; los otros 10 se cortaron por tiempo y no por la física (Tabla 17). Con un tiempo mayor (estudio 4.3) se confirmaron además A\*, el óptimo A4 y un punto de Húsavík: en total, 5 corridas sobre 4 diseños distintos, una muestra mínima.

| Punto | Origen | η con teqp [%] | η con motor real [%] | Δη [pp] | Margen O2 con teqp [K] |
|---|---|---|---|---|---|
| P01 | Ancla A\* | 8.48 | tiempo agotado | — | 0.3 |
| P02 | Estudios 2.1 y 2.2, mayor η | 9.15 | tiempo agotado | — | 0.0 |
| P03 | Estudio 4.2, techo de la franja | 10.81 | 10.81 | 0.0001 | 0.4 |
| P04 | Estudio 4.2, ε_cond mínima | 2.54 | tiempo agotado | — | 0.1 |
| P05 | Estudio 5.1, óptimo A1 | 14.98 | tiempo agotado | — | 0.4 |
| P06 | Estudio 5.1, óptimo A2 | 15.48 | tiempo agotado | — | 3.8 |
| P07 | Estudio 5.1, óptimo A3 | 12.74 | tiempo agotado | — | 3.8 |
| P08 | Estudio 5.1, óptimo A4 | 15.60 | 15.60 | 0.0003 | 0.1 |
| P09 | Estudio 5.1, óptimo A5 | 11.09 | tiempo agotado | — | 5.7 |
| P10 | Estudio 3.2, mejor punto | 12.30 | tiempo agotado | — | 5.5 |
| P11 | Estudio 3.3, mayor P_baja KALINA | 2.67 | tiempo agotado | — | 49.4 |
| P12 | Estudio 2.3, fuente del profesor | 6.27 | tiempo agotado | — | 0.2 |

*Nota.* Fuente: Tabla 6.1-3 de `analisis_final/02_tablas/6.1`. Los puntos P09, P11 y P12 están fuera del rango del modelo de propiedades.

**Margen de cavitación.** Los diseños quedan al filo de O2. Si el piso de O2 sube a 303.55 K, 9 de los 12 puntos pasan a CORREGIBLE, con déficits de 0.5 a 3.2 K. Exigir 2 K de subenfriamiento real cuesta entre +24.6 y +45.7 kPa de P_baja y entre −0.29 y −0.47 pp de η en los cuatro diseños evaluados con resultado completo (A\*, P02, P03 y el óptimo A4); el óptimo A1 requiere +442.7 kPa y −3.67 pp, con huecos de no convergencia en el tramo, y A2, A3 y A5 ya cumplen el margen.

**Planta de Húsavík.** Los 97 KALINA de la fase de septiembre del proyecto se reproducen sin cambio de clase (Δη < 10⁻¹¹ pp); 83 son confiables, porque los otros 14 usan η_t o ε_cond mayores que 0.95. En la malla de x_b con las condiciones de Húsavík, la P_baja mínima KALINA aumenta con la fracción de amoníaco: de 500 kPa con x_b = 0.70 a 800 kPa con x_b ≥ 0.85, aproximadamente +144 kPa por cada 0.1 de x_b (R² = 0.97) (Figura 7). Con x_b de 0.30 a 0.45 no hay ningún punto genuino (0 de 32), y con x_b = 0.50 hay KALINA pero con η < 1.3 %.

![Malla de x_b y P_baja en las condiciones de Húsavík.](fig07_malla_xb_pbaja_husavik.png){width=90%}

*Figura 7. En las condiciones de Húsavík, la P_baja mínima de KALINA aumenta con x_b. Elaboración propia a partir de `analisis_final/03_figuras/6.2/Figura_6.2-1`.*

**Interpretación y límite.** El modelo reproduce los rangos en que converge el caso de la planta (Mlcak et al., 2002) y coincide entre motores en los puntos que el motor real alcanzó a resolver; eso contrasta qué rangos convergen, pero no valida una potencia medida, que no se tiene. La coincidencia entre motores se apoya en 5 corridas sobre 4 diseños.

\newpage

# 11. ANÁLISIS DE SENSIBILIDAD

## 11.1 Sensibilidad local alrededor de A\*

El estudio 3.1 varía una variable a la vez alrededor de A\* (171 corridas: 148 genuinas y 86 KALINA). La Tabla 18 ordena las diez variables por su elasticidad local E = (Δη/η)/(Δv/v) en A\* y reporta la variación total de η en el rango explorado y la distancia de A\* a la frontera de O2 como fracción del rango. T_fuente es la variable de mayor elasticidad (E = 10.9), seguida de x_b (3.4); en variación total de η, x_b (10.8 pp) y P_baja (6.8 pp) son las que más mueven el resultado, seguidas de ε_HRVG (6.7 pp), η_t (6.3 pp) y P_alta (5.1 pp) (Figura 8). Las que suben η sin perder la clase son ε_reg (hasta 10.96 %) y η_t (hasta 9.62 %), ambas con valor de 0.95.

| Variable | Elasticidad E en A\* | Δη en el rango [pp] | Distancia a la frontera de O2 [fracción del rango] |
|---|---|---|---|
| T_fuente | 10.87 | 3.67 | 0.024 |
| x_b | 3.40 | 10.78 | 0.018 |
| T_sumidero | 1.61 | 0.85 | 0.022 |
| P_alta | −1.17 | 5.14 | 0.007 |
| η_t | 1.15 | 6.32 | 0.343 |
| ε_reg | 0.86 | 4.99 | 0.057 |
| ε_HRVG | 0.64 | 6.69 | 0.039 |
| P_baja | −0.58 | 6.80 | 0.016 |
| ε_cond | −0.41 | 0.82 | 0.012 |
| η_p | 0.15 | 1.38 | — |

*Nota.* Fuente: Tabla 3.1-3 de `analisis_final/02_tablas/3.1` (puntos genuinos con W_net > 0 de la malla). Ordenada por |E|. —: ninguna restricción bloquea dentro del rango.

![Variación de η por variable alrededor de A\*.](fig08_tornado_delta_eta.png){width=90%}

*Figura 8. Cerca de A\*, x_b y P_baja son las variables que más mueven η en su rango. Elaboración propia a partir de `analisis_final/03_figuras/3.1/Figura_3.1-1`.*

Las eficiencias responden de forma monótona y casi lineal: +0.115 pp por cada 0.01 de η_t (R² = 1.00), +0.089 pp por 0.01 de ε_reg (R² = 0.98) y +0.115 pp por 0.01 de ε_HRVG (R² = 0.95). T_fuente y x_b, en cambio, no son monótonas dentro del rango: la clase alterna entre no convergencia, KALINA y CORREGIBLE. Por eso las elasticidades de ambas solo valen pegadas a A\* y no deben extrapolarse.

## 11.2 Sensibilidad global

El estudio 3.2 (500 puntos) separa dos preguntas que el análisis local mezcla: qué decide que un punto sea KALINA y qué mueve η (Tabla 19, Figura 9). La factibilidad la deciden P_baja y ε_cond (KS = 0.43 cada una, con intervalos bootstrap que se solapan casi por completo), seguidas de r_P (0.35) y T_fuente (0.29); las eficiencias isentrópicas y las demás efectividades no deciden la clase (KS ≤ 0.12). En cambio, η la mueven P_baja (PRCC = −0.68), P_alta (+0.58), η_t (+0.38), T_fuente (+0.29) y ε_reg (+0.27). Solo P_baja aparece en ambos grupos, con efectos opuestos: subirla asegura KALINA pero reduce η.

| Variable | KS (decide KALINA) | PRCC sobre η | IC 95 % del PRCC |
|---|---|---|---|
| P_baja | 0.427 | −0.68 | −0.75 a −0.61 |
| ε_cond | 0.426 | +0.08 (p = 0.09) | −0.01 a 0.18 |
| r_P | 0.353 | — | — |
| T_fuente | 0.287 | +0.29 | 0.20 a 0.38 |
| T_sumidero | 0.200 | ≈ 0 (p > 0.39) | — |
| x_b | 0.193 | +0.24 | 0.14 a 0.33 |
| P_alta | 0.130 | +0.58 | 0.51 a 0.66 |
| ε_reg | 0.122 | +0.27 | 0.17 a 0.36 |
| η_p | 0.095 | ≈ 0 (p > 0.39) | — |
| η_t | 0.085 | +0.38 | 0.29 a 0.46 |
| ε_HRVG | 0.074 | ≈ 0 (p > 0.39) | — |

*Nota.* Los KS de esta tabla se calculan contra los 379 puntos no KALINA (incluye no convergidos) y los de la Tabla 14 contra los 331 genuinos no KALINA; por eso difieren (por ejemplo, P_baja 0.427 frente a 0.437). Fuente: Tabla 3.2-3 (KS, 121 KALINA frente a 379 no KALINA) y PRCC de `m4b_prcc.csv` (n = 430 genuinos con W_net > 0), recogidos en `analisis_final/INFORME_BARRIDOS_CAMPANA_FINAL.md`. —: no se calculó PRCC para r_P, que es una combinación de P_alta y P_baja.

![Influencia de cada variable sobre η (PRCC).](fig09_prcc_eta.png){width=90%}

*Figura 9. Influencia de cada variable sobre η, medida con PRCC sobre 430 puntos genuinos. Elaboración propia a partir de `analisis_final/03_figuras/3.2/Figura_3.2-3`.*

La robustez del ranking se comprobó de tres maneras: al pasar de 300 a 500 puntos el ranking se mantiene (ρ de Spearman de 0.93 para KS y de 0.99 para PRCC); PAWN sobre η identifica el mismo grupo líder (P_baja 0.44, P_alta 0.42, η_t 0.30 y T_fuente 0.27); y 6 de 10 PRCC sobre η sobreviven a una corrección de Bonferroni (α = 0.005). Un árbol CART de profundidad 4 clasifica KALINA con 78.8 % de exactitud en validación cruzada, apenas por encima del 75.8 % que se obtendría diciendo "nunca KALINA", de modo que no existe una regla simple de corte paralela a los ejes.

## 11.3 Signo de P_alta en el análisis local y global

La presión alta tiene una elasticidad local de −1.2 en A\* (Tabla 18) y un PRCC global de +0.58 (Tabla 19). No es una contradicción: el análisis local mide la pendiente en un punto, y A\* (3000 kPa) queda del lado descendente de un máximo situado cerca de 2300 kPa; el global resume toda la caja de 2000 a 5000 kPa con las demás variables cambiando. Por ello no debe resumirse como "P_alta sube η" sin precisar el punto de operación. Lo mismo ocurre con ε_HRVG: sube η con fuerza en A\* (+0.115 pp por 0.01), pero su PRCC global es cercano a cero; es un efecto que depende del punto y no una tendencia de toda la caja.

## 11.4 Frontera KALINA, razón de presiones y cavitación

**La frontera es nítida.** En las figuras 2.1-1, 2.2-2, 3.1-3, 4.2-1, 6.2-1 y 6.2-2 de la campaña se pasa de KALINA a CORREGIBLE en un solo paso de la malla. A\* está a menos del 6 % del rango de la frontera de O2 en 8 de las 9 variables que la tienen (a 0.7 % en P_alta: bajarla 64 kPa rompe O2). Un punto KALINA no avisa que está a un paso del borde.

**La frontera se desplaza de forma ordenada.** La P_baja mínima KALINA baja 12.5, 15.9 y 25.7 kPa por cada kelvin de sumidero más frío en las tres bases del estudio 2.4 (R² ≥ 0.99), y η en esa P_baja mínima sube 0.088, 0.128 y 0.155 pp por kelvin. En Húsavík sube unos 144 kPa por cada 0.1 de x_b. Con P_baja fija, el efecto directo de T_sumidero sobre η es pequeño (0.85 pp en todo el rango, comparable a la banda); el beneficio de un clima frío llega por vía indirecta, porque relaja O2, permite una P_baja menor y esa P_baja menor sube η (−0.55 pp por cada 100 kPa en la base 2.4a, R² = 0.98).

**r_P discrimina y ΔP no.** El KS de r_P (0.35, Tabla 14) es el de una variable que decide, y el de ΔP (0.10) no lo es; casi no hay KALINA con r_P por encima de 6 aproximadamente (Figura 4). La interacción entre P_alta y P_baja explica que P_alta sola no discrimine: la ventana de diseño debe darse en r_P junto con P_baja, no en P_alta.

**O2 es la restricción dominante.** La cavitación bloquea entre 88 y 100 % de los puntos genuinos que no son KALINA en todos los estudios, salvo en el estudio 4.2 (66.7 %), donde O3 pesa 33.3 % por fuentes frías. El mecanismo es el margen de cavitación: su PRCC (n = 452) es de +0.76 con P_baja, +0.73 con ε_cond, −0.68 con T_fuente, −0.54 con T_sumidero y −0.47 con x_b, y las eficiencias de turbina y bomba no lo mueven (|PRCC| < 0.05). Subir P_baja eleva la temperatura de burbuja; un condensador más efectivo enfría más el líquido; una fuente más caliente, un sumidero más caliente o más amoníaco empujan el líquido hacia la saturación. Estas explicaciones son interpretación coherente con los signos, no una prueba de causalidad.

\newpage

# 12. CONCLUSIONES

El objetivo de la campaña fue determinar el rango en que el ciclo es KALINA conservando la mayor cantidad posible de datos del profesor; la eficiencia es un resultado secundario. Cada conclusión indica su resultado, su interpretación y su límite.

1. **El caso del profesor no converge, y un solo cambio no basta.** *Resultado:* 0 de 42 corridas convergen con los datos del profesor y 0 KALINA en 132 corridas con un cambio (Tablas 12 y 13). *Interpretación:* el bloqueo está en el lado caliente. *Límite:* reproducir el fallo no prueba que el modelo sea correcto.

2. **Con la fuente a 390–410 K se conservan 8 de los 10 datos de diseño.** *Resultado:* 5 KALINA confiables con P_alta, P_baja, x_b y las cinco eficiencias del profesor, con T_fuente de 391 a 409 K y T_sumidero de 280 a 293 K (Tabla 15); alternativamente, las dos presiones del profesor dan 104 KALINA confiables con T_fuente de 390 a 410 K, y en su clima la ε_cond exigida crece con T_fuente: 0.875 solo a 390 K y 0.95 para llegar a 410 K (Figura 5). *Interpretación:* la fuente de 623 K es incompatible con el resto del enunciado (0 confiables en los cuatro conjuntos que la conservan). *Límite:* T_fuente > 410 K no se exploró en el estudio 4.2.

3. **La cavitación (O2) es el criterio que manda.** *Resultado:* bloquea entre 88 y 100 % de los genuinos no KALINA, salvo en el estudio 4.2 (66.7 %). *Interpretación:* el margen de cavitación depende sobre todo de P_baja, ε_cond, T_fuente y T_sumidero (sección 11.4). *Límite:* el margen del modelo es de 0 K; con el piso en 303.55 K, 9 de 12 puntos clave pasan a CORREGIBLE (Tabla 17).

4. **La ventana de presiones se da en r_P.** *Resultado:* el 90 % de los KALINA tiene P_baja de 683 a 1461 kPa y r_P de 1.7 a 5.3 (Tabla 14, Figura 4). *Interpretación:* discrimina r_P (KS = 0.35) y no ΔP (KS = 0.10), ambos de la Tabla 14. *Límite:* el techo de P_baja es el borde de la caja muestreada; hay KALINA hasta 2500 kPa (estudio 3.3).

5. **Lo que decide la clase no es lo que mueve η.** *Resultado:* ε_cond decide la clase (KS = 0.43) con PRCC de +0.08 sobre η; P_alta, η_t y ε_reg mueven η (PRCC +0.58, +0.38 y +0.27) sin decidir la clase; P_baja está en ambos con efecto opuesto (−0.68) (Tabla 19). *Interpretación:* primero se fijan ε_cond y P_baja para ser KALINA y después se sube η. *Límite:* los intervalos de P_baja y ε_cond se solapan, por lo que no puede afirmarse cuál pesa más.

6. **Un clima más frío ayuda sobre todo por permitir una P_baja menor.** *Resultado:* 22 K menos de sumidero reducen la P_baja mínima 43 a 48 % y elevan η máxima 1.9 a 3.4 pp (Figura 3). *Interpretación:* la ganancia llega por vía indirecta (O2). *Límite:* el efecto directo con P_baja fija (0.85 pp) es comparable a la banda de ±0.4 a ±0.7 pp.

7. **La eficiencia es secundaria y acotada.** *Resultado:* 8 a 11 % con equipos de eficiencia media y hasta 15.60 % con equipos a 0.95 conservando las presiones del profesor (Tabla 16). *Interpretación:* los óptimos quedan pegados a la restricción de O2. *Límite:* 15.60 % es el mayor η encontrado con equipos de 0.95, no un máximo demostrado ni un diseño, y diferencias menores que ±0.7 pp no son concluyentes.

8. **El modelo está verificado y contrastado con modelos publicados; no tiene validación experimental.** *Resultado:* concuerda con IAPWS G4-01, entre dos motores (< 0.002 pp), con DWSIM (+0.02 a +0.37 pp en seis ciclos), con Nemati et al. (2017) en estados (dentro de 2.5 K) y con Elsayed et al. (2013) en η (|Δη| medio de 0.28 pp, máximo de 1.16 pp); reproduce los 97 KALINA de Húsavík (Tabla 10). *Interpretación:* respalda la estructura y los rangos de convergencia del modelo. *Límite:* una sola fuente de η, ninguna medición de planta y apenas 5 corridas del motor real.

La Tabla 20 resume, con su respaldo, qué datos del profesor pueden conservarse.

| Dato | Valor del profesor | ¿Se conserva con KALINA? | Respaldo |
|---|---|---|---|
| P_alta | 3000 kPa | Sí | Estudios 4.3 y 4.2 |
| P_baja | 400 kPa | Sí; con su clima de 300 K exige ε_cond de 0.875 (a 390 K) a 0.95 (a 410 K) | Estudios 4.3 y 4.2 |
| x_b | 0.50 | Sí (con el ancla de Húsavík queda al límite, η < 1.3 %) | Estudios 4.3 y 6.2 |
| η_t, η_p, ε_HRVG, ε_reg | 0.85, 0.75, 0.85, 0.75 | Sí | Estudio 4.3 |
| ε_cond | 0.80 | Sí, si el sitio es más frío (≤ ~293 K) | Estudios 4.3 y 4.2 |
| T_sumidero | 300.03 K | Con condiciones: baja a 280–293 K o sube ε_cond | Estudios 4.3 y 4.2 |
| T_fuente | 623.15 K | No (bloqueo estructural) | Estudios 1.1, 2.1, 2.2 y 4.3 |

*Nota.* Fuente: Tabla S-4 de `analisis_final/02_tablas/S`. El flujo másico de 1 kg/s es la base de cálculo y no se varió.

\newpage

# 13. ALCANCE Y LIMITACIONES DECLARADAS

Este documento delimita explícitamente el alcance físico del modelo, de modo que ningún resultado obtenido con él se interprete más allá de las condiciones bajo las cuales fue formulado.

## 13.1 Limitaciones del modelo

**Exergía química excluida.** El análisis exergético de la sección 6.3 se restringe a la exergía física (H10). La exergía química —asociada a la diferencia de composición entre una corriente y un ambiente de referencia universal, y relevante cuando se compara el ciclo con procesos de combustión o de separación de especies— no se evalúa en este trabajo. Su inclusión exigiría definir una composición de referencia ambiental para el amoníaco y el agua por separado, dato que excede el alcance declarado del proyecto.

**Sin subsistema de destilación.** Conforme a la sección 4.1, la configuración KCS11 analizada no incorpora el subsistema de destilación y condensación (DCSS) presente en configuraciones Kalina de mayor escala. El separador opera en un único nivel de presión, y no se evalúa el efecto de una reconcentración adicional de la mezcla a baja presión.

**Reservorios de capacidad térmica infinita (H8).** La fuente y el sumidero se modelan sin capacidad calorífica finita, lo que desacopla el análisis de un caudal específico de gas o de agua de enfriamiento. Esta simplificación introduce una incertidumbre no cuantificada en este documento sobre los valores absolutos de $\dot Q_{in}$, $\dot Q_{out}$ y $\dot W_{net}$ frente a un escenario de fuente real y finita; no afecta, en cambio, a las relaciones adimensionales del ciclo —como la eficiencia térmica $\eta$— que dependen de las temperaturas de los reservorios y no de su capacidad calorífica.

**Presión de referencia del estado muerto como supuesto de ingeniería (H11).** A diferencia de la temperatura de referencia $T_0$, que se ancla a la condición declarada del sumidero, la presión $P_0$ no está determinada por ningún dato termodinámico propio del problema. Se trata, por tanto, como un parámetro configurable con un valor por defecto atmosférico estándar, y cualquier resultado exergético que dependa sensiblemente de su valor debe interpretarse a la luz de este supuesto explícito. Conviene precisar en qué magnitudes se manifiesta esa dependencia: la ecuación (5) muestra que la exergía física de una corriente se calcula respecto de un estado de referencia $(h_0, s_0)$ evaluado en $(T_0, P_0)$, de modo que un cambio en $P_0$ desplaza $h_0$ y $s_0$ de la misma manera para todos los estados del ciclo. Como la exergía destruida de cada componente (ecuaciones (33)-(40)) se obtiene de diferencias de entropía entre estados —no de valores absolutos de $ex$—, ese desplazamiento común se cancela y $\dot E_d$ resulta insensible a $P_0$. Lo que sí depende de $P_0$ es la exergía física reportada para cada corriente individual, $ex_i$: al no cancelarse el desplazamiento cuando se reporta un único estado en lugar de una diferencia entre dos, cualquier valor absoluto de exergía por corriente que se presente en trabajos posteriores debe declarar explícitamente el $P_0$ usado para calcularlo.

**Separador sin arrastre y sin eficiencia propia (H5).** El separador se modela como ideal: no tiene un parámetro de eficiencia propio, y no contempla arrastre de una fase en la otra. Un separador real presentaría una eficiencia de separación inferior a la unidad, no evaluada aquí.

**Parámetros de operación constantes (H9).** Las eficiencias isentrópicas y las efectividades de los intercambiadores se toman como constantes, independientes del punto de operación. En un equipo real, ambas magnitudes varían con la carga y con las condiciones de las corrientes; esa dependencia no forma parte del alcance de este modelo.

## 13.2 Limitaciones de los resultados

**Sin validación experimental.** Ningún resultado del trabajo se ha contrastado con mediciones de planta. La eficiencia solo se compara con una fuente (Elsayed et al., 2013), cuya diferencia máxima de 1.16 pp queda fuera de la banda de incertidumbre y no se ha analizado todavía. El caso de Húsavík se reproduce en sus rangos de convergencia, pero no existe una potencia medida con la cual comparar (sección 10.6).

**El punto ancla está al filo de la cavitación.** A\* queda a menos del 6 % del rango de la frontera de O2 en 8 de sus 9 variables, y el criterio O2 del modelo no incluye margen propio (0 K). Un diseño clasificado como KALINA sin margen de subenfriamiento es frágil frente a pequeñas variaciones del clima; exigir 2 K de margen cuesta entre 25 y 46 kPa de P_baja en los diseños evaluados (sección 10.6). Los efectos locales de la sección 11.1 valen únicamente en esa vecindad.

**El flujo másico nunca se varió.** Se mantuvo en 1 kg/s en todos los estudios; ninguna conclusión cubre su efecto sobre las razones adimensionales ni sobre las magnitudes absolutas $\dot W_{net}$ y $\dot Q$.

**Soluciones espurias del solver.** La campaña contiene 135 falsos convergidos (Tabla 11), que el clasificador descarta y que se cuentan como no convergidos. Algunos puntos NO_CONVERGIO aislados dentro de zonas lisas parecen fallas numéricas del solver; sin un reintento, no está probado que lo sean, y podrían ocultar KALINA que la campaña no cuenta. La verificación frente al motor real, además, solo confirmó 5 corridas sobre 4 diseños.

**Cierre por efectividad sin verificación del perfil interno.** El criterio C1 comprueba las temperaturas extremas del regenerador, pero el modelo no verifica el cruce de temperaturas dentro del HRVG, el regenerador ni el condensador (pinch interno). Los resultados deben leerse como válidos bajo el cierre por efectividad adoptado en la formulación (sección 6.2), no como diseño térmico de los intercambiadores.

**Extrapolación del modelo de propiedades.** El respaldo experimental de la formulación cubre líquido por debajo de 420 K y vapor por debajo de 10 MPa (IAPWS, 2001); más allá, la formulación se extrapola con precisión desconocida. Los barridos llegan a T_fuente de 623 K y 222 de los 500 puntos del estudio 3.2 quedan fuera de ese rango, por lo que no se consideran confiables aunque sean KALINA.

**Cobertura incompleta del espacio de diseño.** Los muestreos por escenario (estudios 4.1 y 4.3) son exploraciones; las franjas angostas solo se mapearon con mallas dirigidas, y en el estudio 4.2 no se exploró T_fuente > 410 K. En la malla de Húsavík no se midió P_baja < 500 kPa para x_b ≥ 0.73. Por último, las figuras muestran qué ocurre, no por qué: las explicaciones de la sección 11 son interpretación coherente con los signos observados, no una prueba de causalidad.

\newpage

# 14. REFERENCIAS

Cengel, Y. A., y Boles, M. A. (2012). *Termodinámica* (7.ª ed.). McGraw-Hill.

Elsayed, A., Embaye, M., Al-Dadah, R., Mahmoud, S., y Rezk, A. (2013). Thermodynamic performance of Kalina cycle system 11 (KCS11): Feasibility of using alternative zeotropic mixtures. *International Journal of Low-Carbon Technologies, 8*(supl. 1), i69–i78. https://doi.org/10.1093/ijlct/ctt020

IAPWS. (2001). *Guideline on the IAPWS formulation 2001 for the thermodynamic properties of ammonia-water mixtures* (IAPWS G4-01). International Association for the Properties of Water and Steam.

Ibrahim, O. M., y Klein, S. A. (1993). Thermodynamic properties of ammonia-water mixtures. *ASHRAE Transactions, 99*(1), 1495–1502.

Ibrahim, O. M., y Klein, S. A. (1996). Absorption power cycles. *Energy, 21*(1), 21–27. https://doi.org/10.1016/0360-5442(95)00083-6

Jonsson, M., y Yan, J. (2001). Ammonia-water bottoming cycles: A comparison between gas engines and gas diesel engines as prime movers. *Energy, 26*(1), 31–44. https://doi.org/10.1016/S0360-5442(00)00043-8

Kalina, A. I. (1984). Combined-cycle system with novel bottoming cycle. *Journal of Engineering for Gas Turbines and Power, 106*(4), 737–742. https://doi.org/10.1115/1.3239632

Kotas, T. J. (1985). *The exergy method of thermal plant analysis*. Butterworths.

Mirolli, M. D. (2005). The Kalina cycle for cement kiln waste heat recovery power plants. *Conference Record, Cement Industry Technical Conference 2005*, 330–336. IEEE. https://doi.org/10.1109/CITCON.2005.1516374

Mlcak, H., Mirolli, M., Hjartarson, H., y Ralph, M. (2002). Notes from the North: A report on the debut year of the 2 MW Kalina cycle geothermal power plant in Húsavík, Iceland. *Geothermal Resources Council Transactions, 26*, 715–718.

Moran, M. J., y Shapiro, H. N. (2004). *Fundamentos de termodinámica técnica* (2.ª ed.). Reverté.

Nemati, A., Nami, H., Ranjbar, F., y Yari, M. (2017). A comparative thermodynamic analysis of ORC and Kalina cycles for waste heat recovery: A case study for CGAM cogeneration system. *Case Studies in Thermal Engineering, 9*, 1–13. https://doi.org/10.1016/j.csite.2016.11.003

Rattner, A. S., y Garimella, S. (2015). Fast, stable computation of thermodynamic properties of ammonia-water mixtures. *International Journal of Refrigeration, 62*, 39–59. https://doi.org/10.1016/j.ijrefrig.2015.09.009

Tillner-Roth, R., y Friend, D. G. (1998). A Helmholtz free energy formulation of the thermodynamic properties of the mixture {water + ammonia}. *Journal of Physical and Chemical Reference Data, 27*(1), 63–96. https://doi.org/10.1063/1.556015

Zhang, X., He, M., y Zhang, Y. (2012). A review of research on the Kalina cycle. *Renewable and Sustainable Energy Reviews, 16*(7), 5309–5318.

Ziegler, B., y Trepp, Ch. (1984). Equation of state for ammonia-water mixtures. *International Journal of Refrigeration, 7*(2), 101–106. https://doi.org/10.1016/0140-7007(84)90022-7

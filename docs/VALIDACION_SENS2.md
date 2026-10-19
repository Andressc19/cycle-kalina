# Informe de validación de Sensibilidad 2

Revisión del análisis P1–P4, del libro `datos/Kalina_anal_sensible_2.xlsx` y de `docs/INFORME_SENS2.md` con la
lista de comprobación de `validate-data` y los criterios de `statistical-analysis` y `data-visualization`
(plugin `data` de Anthropic; se aplicaron sus instrucciones leyendo sus `SKILL.md`, no como skills cargadas por la
sesión). Fecha: 2026-10-17. Rama `test/anal_terremoto`.

## Actualización 2026-10-18 (evaluaciones tipo profesor y plan de mejora)

El libro actual tiene 43 conclusiones y 808 puntos nuevos del motor (F5 Incertidumbre, corridos por el director, no por OpenCode) y el
contraste con la campaña anterior (F6, L8 y L9): (28 hojas, 88 gráficos). Cuatro revisores independientes lo evaluaron como un profesor
exigente. Notas (0 a 5) en el orden rigor, coherencia, sobre-afirmaciones, cobertura, trazabilidad y libro: evaluación 1 = 2.5, 2.5, 2.5, 3.5, 3.0, 3.5;
evaluación 2 (tras la etapa A del plan `docs/PLAN_SENS2_MEJORA.md`) = 3.5, 3.0, 3.0, 3.5, 3.8, 3.8; evaluación 3 = 3.8, 3.5, 3.5, 3.5, 4.2, 4.0;
evaluación 4 = 3.9, 3.7, 3.6, 3.8, 4.1, 4.1; evaluación 5 = 4.0, 3.8, 3.8, 3.9, 3.8, 4.2; evaluación 6 = 4.0, 3.8, 3.7, 3.9, 3.9, 4.2. La cobertura de las preguntas 3 y 4 del profesor es el criterio que no sube de ≈ 3.8 sin el motor.

Etapa A (hecha): conclusiones generadas desde los CSV con marcadores (`p5_conclusiones_base.csv`, `p5_hechos.py`, `p5_generar.py`), regla de
confianza por código con criterios cumplidos de 6 (`p5_confianza.py`, `p5_evidencia.csv`; hoja Confianza), controles independientes de cifras
(`p5_cifras_check*.py`), prueba de permutación con 2 000 barajados y corrección de Benjamini–Hochberg (hoja F7 Nulo y correccion FDR), sensibilidad
a NO_CONVERGIO, comparación pareada por distancia y diseño, envolventes de equipos por diseño, fronteras con intervalo, validación cruzada de las
superficies, potencia de U1, hojas F4 Ciclo vs T_fuente y F4 Equipos por kW (sin motor), orquestador `make_sens2.py` (probado con `--todo`) y
pruebas pytest que vigilan los conteos del libro.

Hallazgos de las evaluaciones 2 a 6 atendidos (en la última ronda: el «49 % a una sola variable» pasó a conteo del diseño, 68 % en barridos y mallas y 0 % en el LHS; el ajuste lineal de L2 deja de usarse como evidencia; M5 con Bonferroni y con otra normalización, con su script `p6_m5_lhs.py`; el trazado contra la fuente citada es ahora una compuerta que falla si queda una cifra sin respaldo): M2 con la línea base correcta; U1 y U4 (con ε_cond sobre el umbral todavía se pierden puntos;
pendiente del margen de cavitación ≈ 1.9 K por −0.01 entre 0.92 y 0.95); L2 con el pareado de los 4 bloques (n = 734), separado por diseño y sin
afirmar una dependencia con la distancia; D1 y D5 solo con la regresión logística donde su intervalo es informativo; F1 con 6 métodos y solo «distinguible
del ruido»; M1 a M4 como valores muestreados; enunciados de E1, E4, E5 y E6 como lo observado en los KALINA muestreados; E2 limitada a Δh y con
una sola línea; M6 limitada a las bandas con al menos 10 KALINA dentro del rango experimental; las tablas de preguntas del LEEME y de la conclusión consolidada
con las hojas nuevas. Siguen abiertos, porque requieren el motor y autorización: reintentar NO_CONVERGIO, el ciclo frente a T_fuente optimizado por
temperatura y el flujo volumétrico de la turbina y la altura de la bomba (etapas B y C del plan).

## Evaluación global: compartir con caveats

Las cifras se recalcularon con código distinto del que las genera (p5_cifras_check*.py) y coinciden. Los hallazgos corregidos están abajo. Quedan
caveats que deben comunicarse (sección «Caveats obligatorios»).

## Revisión de método

- **Pregunta y población.** El análisis responde las 4 preguntas del profesor (rangos con KALINA, partir de KALINA
  y mover variables, regenerador, datos de equipos). La población son los 3 921 puntos de Sensibilidad 1; se
  deduplicaron 258 filas exactas (3 663).
- **Métricas.** η y W_net/m_b solo existen en puntos convergidos. W_net se divide entre m_b porque el estudio 0 usa
  m_b distinto de 1.
- **Comparación justa.** CORREGIBLE frente a KALINA se hace sobre todos los puntos y solo sobre el muestreo LHS,
  para no mezclar diseños.
- **Índices.** Se calculan solo sobre el LHS de cada bloque, con 3 variables dummy como piso de ruido.

## Problemas hallados y corregidos (11)

| N.º | Gravedad | Problema | Corrección |
|---|---|---|---|
| 1 | Alta | El BLUF del libro daba η máxima 17.37 / 18.68 % (máximo de todas las clases); lo correcto es 14.53 / 14.82 % (solo KALINA). El control no lo detectó porque repetía la fórmula | Filtro por KALINA; control reescrito de forma independiente y cruzado con la conclusión M1 |
| 2 | Alta | Conclusión F5 decía que casi todos los pares son aditivos sobre η; los datos dan 0.00–0.18 (fuertes: B6 en C1 y B4 en C4) | Texto corregido en conclusiones, libro e informe |
| 3 | Media | Hoja F1 decía «sin duplicados» y usa los 3 921 puntos con duplicados | Nota de base en LEEME y en cada hoja F1 a F4 |
| 4 | Media | Gráfico de fronteras mezclaba kPa y K en un solo eje | Separado en dos gráficos |
| 5 | Media | Gráfico de ganancia de cortes mostraba 0 para variables que sí tienen ganancia (solo se tomaban los 5 mejores) | Usa todas las variables; 0 solo si la variable es constante en el bloque |
| 6 | Media | En los gráficos de importancia, el piso de ruido (dummy) era indistinguible de una variable | Tres series: supera el ruido (verde), no lo supera (ámbar), dummy (gris) |
| 7 | Baja | La elasticidad de T_fuente en C2 (13.2) aplastaba el resto del gráfico | Excluida del gráfico con nota; sigue en la tabla |
| 8 | Media | Los p-valores y los IC de la comparación sobre todos los puntos suponen independencia que no se cumple (barridos y mallas) | Nota en F2, en la conclusión L5 y en el informe; la cifra defendible es la de LHS (+3.10 puntos de η, IC [+2.46, +3.65]) |
| 9 | Alta | La conclusión M5 (óptimos pegados a la frontera, p ≈ 1e-21) depende del diseño: con el muestreo LHS solo la diferencia es significativa en C1 (0.62 frente a 0.75, p = 0.016); C2 p = 0.63, C3 p = 0.09, C4 p = 0.48 | Reescrita como tendencia dependiente del diseño, confianza Media; BLUF del informe suavizado |
| 10 | Media | El criterio «distinguible del ruido» es laxo: de 175 variables marcadas, 38 lo son por un solo método y solo 72 por 4 o más | Declarado en F3, en L5 y en el informe; las variables citadas lo superan en 3 a 8 métodos |
| 11 | Media | Faltaba definir «cavitación (O2)» y qué significa «confianza» | Definidos en LEEME (corregido en la segunda evaluación: O2 es m_O2 ≥ 0, margen cero, no «1 K»); confianza = robustez dentro del modelo |

## Objeciones previsibles de un evaluador (y estado)

1. **«Todo es el modelo.»** Cierto: solo teqp, sin validación experimental; se contrasta con modelos publicados y un simulador, no con experimentos. Declarado.
2. **«Falta propagar incertidumbre y superficies de respuesta.»** Hecho después de esta revisión: 808 puntos del motor (F5 Incertidumbre) y 8 mallas con ajuste cuadratico (F5 Superficies de respuesta). Reservas: las tolerancias (±5 K, ±3 K, ±5 %, ±0.02, ±0.05; el doble en B) son supuestos de escenario y las entradas se tomaron independientes y uniformes (incertidumbre estándar ±a/√3); con 48 puntos por celda los IC de Wilson son anchos, pero un segundo lote independiente de 48 (96 en total) coincide con el primero (diferencias de P(KALINA) de 0.00 a 0.02, |z| ≤ 1.0), son compatibles, pero con 48 puntos por lote eso no prueba que el muestreo sea estable; un escenario con ε_cond fija en 0.95 (192 puntos) y un barrido fino de ε_cond (40 puntos) aislaron el sesgo del tope 0.95: la pérdida de clase no se debe solo al condensador (con ε_cond fija en 0.95 el escenario recupera casi todo, pero con ε_cond ≥ 0.92 siguen sin ser KALINA 11 de 54 puntos en C1 y 8 de 84 en C4); los percentiles P5 y P95 son aproximados; la banda del modelo (±0.7 pp) se suma de forma determinista.
3. **«La regla de ruido con 3 dummy es débil.»** Cierto: se declara y se usa solo con 3 a 8 métodos concordantes.
4. **«¿Por qué el regenerador pierde peso al subir T_fuente?»** Resuelto en la segunda evaluación (conclusión E8): el lado caliente es el líquido pobre y Q_reg = m_l·(h5 − h6); al subir T_fuente casi todo el fluido se vaporiza y m_l/m_b cae de 0.81 a 0.006.
5. **«Los requisitos de equipos son envolventes, no especificaciones.»** Cierto: faltan flujo volumétrico de la turbina, altura de la bomba y geometría. Declarado.
6. **«El pinch del regenerador sale de ε_reg prefijada, no del diseño óptimo.»** Cierto en parte: en el LHS ε_reg se muestrea de 0.40 a 0.95, y el pinch y el UA observados (E4) dependen de ese rango; no son requisitos.
7. **«Los barridos no son comparables entre sí.»** Declarado; los índices globales usan solo el LHS.

## Comprobaciones de cálculo (independientes)

- Total, clases y duplicados de P1/P2: verificado.
- Medianas de η y W_net/m_b, L1, nº de variables distintas y fracción de rescate univariado (P2): verificado.
- Percentiles de r_P, Δh, q4, pinch, LMTD, UA, Q_out y bandas de r_P (P4): verificado.
- PRCC de η y KS de existencia en C1 y C4 (P3): verificado (±0.01 por el bootstrap).
- Elasticidades y 10 correlaciones citadas en las conclusiones: verificado.
- Rangos mínimos de ε_cond por bloque y fronteras de P1: verificado.
- Control cruzado de la η máxima del BLUF contra la conclusión M1: incluido en `s2_verificar.py`.
- No verificado: fuentes web de la Etapa 0 (10 marcadas ⚠) y cifras de otros autores citadas en la conclusión E1.

## Revisión de gráficos (los 56 de esta revisión se abrieron y exportaron desde Excel real; los demás gráficos del libro actual se auditaron con Excel real el 2026-10-18)

Los 41 de la primera versión y los 15 de las hojas añadidas después (márgenes de operación y regenerador frente a T_fuente) tienen series numéricas, ejes rotulados con unidades, sin vacíos, solapes ni celdas tapadas. Las barras
parten de cero salvo las de elasticidad y coeficientes (con signo, con escala propia). Reservas que quedan:
(1) los gráficos de P(KALINA) por banda usan el número de cuantil en el eje, no el valor de la variable (el valor
está en la tabla); (2) la paleta verde/rojo no es óptima para daltonismo (se mantiene la del libro 1; las series
siempre llevan leyenda); (3) los títulos describen la métrica y no enuncian el hallazgo.

## Caveats obligatorios para quien lea el libro

- Solo motor teqp, sin validación experimental propia del ciclo; el lugar crítico no se vigila.
- El 15 % de los KALINA está fuera del rango experimental (líquido > 420 K); se muestran aparte.
- Los diseños mezclan barridos, mallas y LHS; la P(KALINA) por nivel depende del diseño.
- η y las potencias existen solo en puntos convergidos (sesgo de supervivencia en las comparaciones).
- Los p-valores sobre todos los puntos suponen independencia que no se cumple; usar la cifra sobre LHS.
- m_b no se barrió. Las elasticidades salen de dos estudios. LMTD y UA se reconstruyen de los estados.
- 7 puntos atípicos del libro 1 no se descartan ni se validaron con el motor real.

## Mejoras sugeridas

1. Validar con el motor real los 7 atípicos y los óptimos M1 a M4.
2. Abrir las 10 fuentes ⚠ de la Etapa 0 (o repetir esa búsqueda con la skill `investigacion-documental`).
3. Si el profesor quiere comparar diseños, repetir CORREGIBLE frente a KALINA con un diseño pareado (mismos
   puntos, solo cambia la variable de rescate).

# TASK_CONTEXT — Sensibilidad 2, Etapa 0: investigación bibliográfica (solo lectura y redacción)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd` ni rutas absolutas en la terminal; no leas nada fuera de este directorio.** Rutas relativas.
- Archivos SOLO con las herramientas `write` y `edit`. PowerShell 5.1, sin `&&`. No ejecutes `pytest`.
- Esta tarea NO calcula nada ni ejecuta el motor. Solo investigas en la web (foros técnicos, papers, documentación,
  libros de acceso público) y redactas.
- Ya existen en el proyecto `docs/ESTUDIO_METODOS_SENSIBILIDAD.md` y `docs/METODOLOGIA_ANALISIS_RESULTADOS.md`:
  léelos primero y NO los repitas; amplíalos con lo nuevo.
- **Terminología:** nunca «confiable / no confiable / no citable». Di «dentro del rango experimental» y «fuera del
  rango experimental (líquido > 420 K)».

## Contexto del problema

Ciclo Kalina KSC-11 (NH3-H2O) con 10 variables de entrada: T_fuente (70–300 °C), T_sumidero (5–30 °C), P_alta,
P_baja, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond (0.40–0.95). Dataset: 3 921 puntos (OFAT, mallas de pares, LHS de 500
puntos en 9 variables). Clases: KALINA / CORREGIBLE / NO_CONVERGIO / INVIABLE; salida continua η, W_net, Q_reg, Δh
turbina, márgenes de cavitación. Frontera de clase brusca, salida binaria y muchos puntos sin solución.

## Preguntas a investigar (cita fuente con URL y año de cada hallazgo)

1. Métodos de sensibilidad aplicables cuando la salida es mixta (binaria + continua) y hay puntos sin solución:
   PRCC, Morris, Sobol/Saltelli, FAST, ANOVA, SRC, elasticidades, regresión logística, árboles/importancia por
   permutación, KS/Kolmogorov–Smirnov (filtrado de Monte Carlo regionalizado), indicadores de dependencia
   (HSIC, delta de Borgonovo). Cuáles se pueden calcular sobre un muestreo LHS ya existente sin nuevas corridas.
2. Sensibilidad aplicada al ciclo Kalina NH3-H2O: variables críticas reportadas, rangos típicos, eficiencias de
   referencia, óptimo de x_b y de P_alta, efecto de T_fuente, del recuperador y del condensador. Configuraciones
   (KCS-11, con recuperador, con separador, dos presiones).
3. Cómo estructurar el informe técnico de sensibilidad para diseño de ciclos (secciones, tablas, gráficas).
4. Criterios para tratar regiones de no convergencia y «regiones grises» en simulaciones termodinámicas; cómo medir
   la «distancia a la factibilidad» desde un punto no factible (márgenes, proyección, análisis de restricción).
5. Dimensionamiento y preselección de turbina (ΔP, relación de expansión, título de salida, Δh, flujo volumétrico),
   regenerador (ε, NTU, UA) y condensador (carga, LMTD) para ciclos Kalina de baja temperatura (geotermia,
   70–300 °C); rangos de referencia de la literatura.

## Entregable (un solo archivo)

`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md`, máximo 400 líneas, en español, con estas secciones:
1. Métodos recomendados (tabla: método, qué mide, requisitos, ¿sirve con LHS existente?, riesgo con puntos sin
   solución, fuente).
2. Hallazgos Kalina (variables de mayor impacto, valores de referencia con fuente).
3. Plantilla de informe (índice propuesto).
4. Tratamiento de no convergencia / distancia a KALINA.
5. Criterios de preselección de equipos (valores de referencia con fuente).
6. Capacidades necesarias: lista de librerías Python o herramientas que haría falta (scipy, numpy, pandas ya hay;
   **sin scikit-learn**: dilo si algún método lo requiere y qué alternativa hay con numpy/scipy).
7. Fuentes (lista numerada con URL; marca las que NO pudiste abrir).

Reglas: no inventes cifras; si no encuentras una, dilo en UNRESOLVED. Cada cifra lleva su fuente. No copies más de
una frase breve de ninguna fuente: parafrasea.

Reporte final en el formato de `AGENTS.md`.

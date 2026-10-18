# TASK_CONTEXT — Sensibilidad 2, P5a: libro `Kalina_anal_sensible_2.xlsx` (parte 1: LEEME, conclusión, Fases A y C, hojas de datos)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (openpyxl, numpy, pandas).
**Lee antes:** `docs/PLAN_SENS2_ANALISIS.md`; el código del libro anterior `scripts/sens1/x2_formato.py`,
`x5_graficos.py` y `x7_construir.py` (REUTILÍZALOS importándolos con `sys.path`: `titulo, subtitulo, condiciones,
encabezado, fila_datos, tabla, nota, descripcion, anchos_col` y `bloque, grafico_sobre_tabla, dibujar_todos`). No
copies ni modifiques `scripts/sens1/`. Sin corridas del motor.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` ni here-docs que
  escriban archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. Scripts nuevos en `scripts/sens2/` con prefijo `s2_`. Salida:
  `datos/Kalina_anal_sensible_2.xlsx`. El libro no debe estar abierto en Excel.
- **Terminología:** «KALINA (total)», «dentro del rango experimental», «fuera del rango experimental (líquido >
  420 K)». Prohibido en TODO texto y hoja: «confiable», «no confiable», «no citable», «fuera de rango del motor»,
  «sin respaldo», «indicio», «extrapol». Todo número sale de un CSV de `resultados/2026-10-17_sens2_P1..P4` o de
  `resultados/2026-10-17_sens2_P5/p5_conclusiones.csv`; ninguno se escribe a mano.

## Reglas de formato del libro (iguales al libro 1)

Español; unidades en el encabezado de cada columna; cuadrícula visible; **sin paneles inmovilizados**; cada
tabla lleva sobre ella un bloque «Condiciones» (qué quedó fijo y qué se barrió); **cada gráfico es nativo de Excel,
está junto a la tabla de la que sale (a su derecha, columna L) y leyendo los datos de esa tabla**; gráfico = tabla
(mismos números); nada de gráficos vacíos, solapados ni que tapen celdas con datos; la descripción corta al final de
cada hoja. Colores de clase como en el libro 1 (`x2_formato`).

## Arquitectura (módulos en `scripts/sens2/`)

- `s2_cargar.py`: lee los CSV de P1–P4 y `p5_conclusiones.csv` en DataFrames (una función por fuente).
- `s2_construir.py`: ensambla el libro con una lista `HOJAS = [...]` de funciones `hoja_xxx(wb, datos)` que **otras
  tareas ampliarán** (la parte 2 añadirá `s2_f3.py` y `s2_f4.py`); llama a `dibujar_todos(wb)`, pone `LEEME` primera y
  guarda. Debe poder correr con solo las hojas que existan (importa los módulos opcionales con `try/except
  ImportError`).
- Una hoja de resumen por módulo: `s2_leeme.py`, `s2_conclusion.py`, `s2_f1.py`, `s2_f2.py`, `s2_datos.py`.

## Hojas de esta parte (en este orden)

1. **`LEEME`**: título, qué es el libro y de qué campaña viene (3 921 puntos de Sensibilidad 1, 3 663 sin duplicados),
   guía de hojas (incluidas las que añadirá la parte 2: `F3 Indices globales`, `F3 Interacciones`, `F3 Elasticidades`,
   `F4 Turbina`, `F4 Regenerador y condensador`, `F4 Preseleccion`), terminología (rango experimental, igual que el
   libro 1: copia el párrafo `TEXTO_RANGO` de `x7_construir.py`), los 4 centros de bloque (C1–C4 con sus constantes), las
   preguntas del profesor y en qué hoja se responde cada una, y las **limitaciones** (cita las de la conclusión L5).
2. **`Conclusion consolidada`**: (a) bloque BLUF de 5 filas con las cifras de cabecera (calculadas de los CSV: nº de
   puntos, % KALINA, η máxima dentro y fuera del rango experimental, % de CORREGIBLE por cavitación, variable que más
   rescata); (b) las **29 conclusiones** de `p5_conclusiones.csv` en tablas por categoría en este orden: DISEÑO REAL,
   EQUIPOS, MÁXIMA EFICIENCIA, FLUCTUACIÓN, LÍMITES KALINA (columnas: id, fase, afirmación, evidencia, implicación,
   confianza, fuente; texto con ajuste de línea y anchos legibles, sin cortar); (c) tabla «Respuesta a las 4
   preguntas del profesor» (rangos con KALINA → hoja F1; partir de KALINA y mover 1 o 2 variables → hoja F2;
   comportamiento del regenerador → F4; datos para preseleccionar equipos → F4 Preseleccion) con la conclusión que la
   contesta; (d) un gráfico de barras del nº de conclusiones por categoría y confianza junto a su tabla.
3. **`F1 Existencia`** (de P1): tabla «mínimo y máximo de cada variable con KALINA (total) por bloque» (10 variables ×
   4 bloques, formato largo legible) + gráfico de barras con la ε_cond mínima por bloque; tabla de **fronteras** de los
   barridos de una variable (`p1_fronteras.csv`: bloque, variable, forma, dirección, valor de la frontera) + gráfico
   de barras de la frontera de P_baja y la de T_fuente (inferior y superior) por bloque; tabla **P(KALINA) por nivel**
   de las variables con ≤ 14 niveles (de `p1_existencia_prob.csv`, usa las del muestreo LHS si hay columna que lo
   distinga) con gráfico de línea para x_b y P_baja por bloque; nota con la advertencia de diseño de `p1_existencia.md`.
4. **`F1 Reglas y zonas grises`** (de P1): tabla de los mejores cortes únicos por bloque (variable, umbral, lado,
   ganancia) + gráfico de barras de ganancia por variable; coeficientes de la regresión logística con signo + gráfico;
   las reglas del árbol; conteo de zonas grises por bloque y por violación dominante + gráfico apilado.
5. **`F2 CORREGIBLE vs KALINA`** (de P2): tabla de comparación (η, W_net/m_b, r_P, Q_reg/Q_i, Δh, q4: medianas, P10,
   P90, diferencia con IC, KS), dos gráficos de barras (η y W_net/m_b, medianas CORREGIBLE frente a KALINA por bloque);
   tabla de violación dominante por bloque + gráfico apilado; tabla de D por cuartil.
6. **`F2 Distancia y rescate`** (de P2): tabla de rescate univariado (variable, dirección, % de CORREGIBLE) + gráfico de
   barras; distribución de la distancia L1 y del nº de variables distintas por bloque + gráfico; cambio de η al
   rescatar (mediana e IC); **robustez**: tabla del 10 % de mayor η frente al resto (distancia mediana, KS, p) +
   gráfico, y el top-10 de η por bloque (id, η, distancia a la frontera, rango experimental).
7. **Hojas de datos** (sin gráficos, una tabla cada una, con filtro): `D1 Datos puntos` (`p2_dataset_dedup.csv`),
   `D2 Datos fronteras` (`p1_fronteras.csv`), `D3 Datos zonas grises` (`p1_zonas_grises.csv`),
   `D4 Datos distancia` (`p2_distancia.csv`). Valores numéricos como números (no texto), unidades en el encabezado.

## Verificación (`scripts/sens2/s2_verificar.py`; la parte 2 la ampliará)

Con openpyxl (`data_only=False`; recorre las series de cada gráfico y lee sus celdas): (1) existen las hojas
anteriores en ese orden; (2) cada gráfico tiene ≥ 1 serie con ≥ 2 valores numéricos; (3) ninguna celda de las tablas
de gráfico está vacía; (4) los gráficos de una hoja no se solapan entre sí ni con celdas con datos (usa las anclas y
tamaños); (5) sin paneles inmovilizados; (6) ningún texto contiene las palabras prohibidas; (7) cada cifra de BLUF
coincide con su CSV; (8) las 29 conclusiones están todas y sin celdas vacías; (9) filas de `D1 Datos puntos` = n del
CSV. Una línea OK/FALLA por control; no des `done` con FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\s2_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\s2_verificar.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: lista de hojas con su nº de gráficos, y la salida de
`s2_verificar.py` (sin la lista larga de gráficos).

# TASK_CONTEXT — Sensibilidad 1: libro Excel único `Kalina_anal_sensible_1.xlsx`

**Fecha:** 2026-10-15 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (openpyxl, pandas, numpy; **sin**
scikit-learn). **Salida:** `datos/Kalina_anal_sensible_1.xlsx` (un solo archivo; sin `_v2` ni copias).

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: solo ASCII en los `print`.
- La construcción tarda minutos, no horas; usa `timeout=1800000` en la herramienta de shell. **NO ejecutes
  `pytest`.**
- El libro de salida NO debe estar abierto en Excel; si falla el guardado por bloqueo, repórtalo.

## Restricciones

- **NO modificar** `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, los CSV de
  `resultados/` ni `datos/Excel_kalina_final_final_final.xlsx` ni `datos/Excel_final_kalina.xlsx`.
- Cada `.py` nuevo: máximo 200 líneas (divide en módulos `x1_…` a `x8_…`, ver más abajo).
- No inventes valores: **todo número del libro se calcula desde los CSV** (no copies cifras de los
  `*_resumen.md` de OpenCode: uno de ellos ya omitió el punto base). Los textos de conclusión de este
  documento (Apéndice A) se escriben tal cual, pero **cada cifra que citan debe verificarse contra los
  datos** en `x8_verificar.py`; si una no coincide, repórtalo en UNRESOLVED y NO la publiques.
- Reglas de formato del usuario, **todas obligatorias**:
  1. **Gráficos nativos de Excel** (no imágenes), con sus datos **visibles** (nada en hojas ocultas) y
     **junto a la tabla de la que salen**, sin tapar celdas ni otros gráficos. Gráfico y tabla cuentan lo
     mismo (si difieren, el criterio va en una columna).
  2. **Todas las tablas con cuadrícula** (bordes), filtros en las tablas de datos, **sin paneles
     inmovilizados (freeze panes)**.
  3. Clasificación coloreada en tonos claros: KALINA verde, CORREGIBLE naranja, NO_CONVERGIO rojo,
     INVIABLE amarillo.
  4. Títulos de columna con unidad entre paréntesis (`T_fuente (K)`, `P_baja (kPa)`, `η (%)`).
  5. **Nada de abreviaturas de dos letras** (TF, XB, PA…): usa siempre el nombre (T_fuente, x_b, P_alta,
     ε_HRVG). Tampoco códigos internos sueltos (`N7B`, `C3`): acompáñalos de su nombre en palabras.
  6. Todo en español. Cada tabla abre con un encabezado de **condiciones** (qué quedó fijo y en qué valor,
     qué se barrió) y **no mezcla** puntos con datos fijos distintos.
  7. Al final de cada hoja de datos, 2 filas de separación y una **descripción corta**: qué se iteró, qué
     quedó fijo, conteo por clase.
  8. Trampas de openpyxl ya resueltas: usa los ayudantes de `scripts/analisis_final/a2_graf_base.py` y
     `a2_graf_estilo.py` (léelos y reutilízalos): `overlay=False` en títulos, `varyColors=False`,
     `invertIfNegative=False`, y nunca `line.solidFill` y `noFill` a la vez (Excel no abre el libro).

## Datos de entrada (CSV, todos en el worktree)

| Estudio | Archivo | Puntos |
|---|---|---|
| 0 Referencia de Húsavík | `resultados/2026-10-14_sens1_fase0/fase0_filas.csv` | 11 |
| 1 Una variable (C1, C2) | `resultados/2026-10-14_sens1_faseA/faseA_filas.csv` | 273 |
| 2 Pares (C1, C2) | `resultados/2026-10-14_sens1_faseB/faseB_filas.csv` | 542 |
| 3 LHS de 9 variables | `resultados/2026-10-14_sens1_faseC/faseC_filas.csv` | 500 |
| 4 Fuente 70–300 °C | `resultados/2026-10-14_sens1_ronda1/ronda1_filas.csv` (barrido N1) | 343 |
| 5 Condensador × clima | idem (barrido N3) | 192 |
| 6 P_alta baja × x_b | idem (barrido N4) | 98 |
| 7 Fuente fría, presiones bajas | `resultados/2026-10-15_sens1_ronda2/ronda2_filas.csv` (barrido N2) | 144 |
| 8 Mapa fuente × clima × P_baja | idem (barrido N5) | 360 |
| 9 Equipos baratos | idem (barrido N6) | 54 |
| 10 Centros nuevos, una variable | `resultados/2026-10-15_sens1_N7/n7_filas.csv` (barrido N7A) | 279 |
| 11 Centros nuevos, pares | idem (barrido N7B) | 361 |

Total: **3 157** filas. Los CSV tienen campos con saltos de línea en `mensaje`: léelos con
`pandas.read_csv` (no cuentes líneas). Si falta una columna en un archivo (p. ej. `variable`, `par`),
déjala vacía.

## Definiciones (úsalas en LEEME y en todas las hojas)

- **KALINA confiable:** clase KALINA, `fuera_rango` falso/vacío y todo `eta_*`/`eps_*` en [0.40, 0.95].
- **KALINA fuera de rango del motor:** clase KALINA con `fuera_rango` verdadero (T2 o T5 > 420 K);
  se muestra aparte y nunca se suma a los confiables.
- **Punto genuino:** `convergio` verdadero y clase distinta de NO_CONVERGIO.
- **Centros:** C1 Húsavík (T_fuente 394.15 K, T_sumidero 278.15 K, P_alta 3300, P_baja 690, x_b 0.82,
  η_p 0.80); C2 ancla A\* (403.0 K, 300.15 K, 3000, 563.64, 0.50, η_p 0.75); C3 caliente 150 °C (423.15 K,
  280.5 K, 3150, 950, 0.75, η_p 0.80); C4 frío 110 °C (383.15 K, 282.5 K, 3880, 910, 0.88, η_p 0.80). En
  todos: η_t 0.85, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.95, m_b 1.0 kg/s, y el piso de O2 = T_sumidero.
- **Reglas de la campaña:** T_fuente 70–300 °C; eficiencias y efectividades 0.40–0.95 con paso 0.05;
  T_sumidero 5–30 °C; m_b fijo (solo escala las potencias); motor teqp, sin validación experimental.

## Estructura del libro (en este orden)

1. **`LEEME`**: qué es, para qué (los 4 pedidos del profesor), cómo se lee, definiciones, centros y
   reglas, y una **guía de hojas** (índice con enlaces internos).
2. **`Conclusion consolidada`**: las conclusiones de la campaña (Apéndice B), con las tablas de síntesis
   debajo (ver paso 6) y sus gráficos.
3. Por cada estudio 0–11, **dos hojas**: `E{n} {nombre corto}` (resumen: condiciones, tablas de resultados
   con gráfico nativo al lado, y **conclusión del barrido** del Apéndice A) y `E{n} Datos {nombre}` (todos
   los puntos: id_punto, centro, variable o par, T_fuente (K), T_sumidero (K), P_alta (kPa), P_baja (kPa),
   x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond, m_b (kg/s), T_amb_diseno (K), clasificación, convergió,
   fuera de rango, KALINA confiable (sí/no), η (%), Wnet (kW), m_O1, m_O2 (K), m_O3 (kW), m_O5, Qi, Qout,
   Wt, Wp, Qreg (kW), dh_turb (kJ/kg), Qreg/Qi, P_alta/P_baja, t_s (s), mensaje, y T_e1…T_e10 (K) y
   h_e1…h_e10 (kJ/kg) al final). Nombres de hoja ≤ 31 caracteres.

## Módulos a crear (`scripts/sens1/`, ≤ 200 líneas cada uno)

- `x1_cargar.py`: carga y normaliza los 12 conjuntos en un solo DataFrame con `estudio`, `centro`,
  `variable`/`par`, columnas calculadas (KALINA confiable, fuera de rango como booleano, η %, Qreg/Qi,
  P_alta/P_baja). Exporta `ESTUDIOS` con nombre largo/corto, archivo y filtro.
- `x2_formato.py`: estilos (cuadrícula, colores de clase, anchos, encabezados de unidad, wrap de
  `mensaje`), sin freeze panes.
- `x3_hojas_datos.py`: hojas `E{n} Datos …` con filtro y la descripción final.
- `x4_resumenes.py`: tablas de las hojas de resumen por estudio (conteos por clase y centro, ventanas por
  variable, η mín/mediana/máx entre confiables, equipos por kg/s).
- `x5_graficos.py`: gráficos nativos junto a cada tabla (mínimo uno por estudio):
  1: η (%) de los KALINA confiables frente a cada variable (líneas, por centro);
  2: KALINA por par y centro (barras);
  3: KALINA por variable en la caja (barras);
  4: KALINA confiables y fuera de rango por T_fuente, y η máxima por T_fuente (líneas);
  5: P_baja mínima con KALINA frente a ε_cond, una línea por T_sumidero;
  6: KALINA por x_b y P_alta (barras agrupadas por centro);
  7: KALINA por T_fuente (barras);
  8: P_baja mínima con KALINA frente a T_sumidero, una línea por T_fuente; y η máxima confiable;
  9: η (%) por combinación de equipos (barras);
  10 y 11: igual que 1 y 2 para C3 y C4.
- `x6_sintesis.py`: hoja de síntesis dentro de `Conclusion consolidada`: S1 conteo por estudio × clase;
  S2 ventanas KALINA de cada variable en los 4 centros (de los estudios 1 y 10); S3 frontera del
  condensador (estudio 5) y mapa fuente × clima (estudio 8); S4 rangos de equipos por kg/s por estudio;
  S5 η máxima confiable por estudio y el punto que la logra. Con gráfico nativo junto a S1 y S5.
- `x7_construir.py`: ensambla el libro en el orden indicado y lo guarda.
- `x8_verificar.py`: ver abajo.
- `conclusiones.py`: los textos de los Apéndices A y B como diccionarios (sin lógica).

## Verificación (`x8_verificar.py`, obligatoria; imprime una línea OK/FALLA por control)

1. El libro abre con `openpyxl.load_workbook`; ninguna hoja oculta; ningún freeze panes; todas las hojas
   ≤ 31 caracteres.
2. Filas de cada hoja `E{n} Datos`: el número de filas de datos coincide con su CSV (tabla de arriba).
3. Totales por clase de los estudios: 1 → 273 (KALINA 186, CORREGIBLE 59, NO_CONVERGIO 23, INVIABLE 5);
   2 → 542 (398, 108, 35, 1); 3 → 500 (KALINA 249: C1 118, C2 131); 4 → 343 (KALINA 159: 47 confiables,
   112 fuera de rango); 5 → 192 (KALINA 17); 6 → 98 (KALINA 47); 7 → 144 (KALINA 45); 8 → 360 (KALINA
   188: 138 confiables, 50 fuera de rango); 9 → 54 (KALINA 43); 10 → 279 (C3 117 KALINA, C4 101);
   11 → 361 (C3 111, C4 92).
4. Cada serie de cada gráfico apunta a celdas del mismo libro, en una hoja visible, y el número de
   puntos de la serie coincide con el de su tabla.
5. Que ningún gráfico se solape con una tabla (compara las celdas ancla con las dimensiones de las
   tablas de su hoja).
6. Cada cifra citada en el Apéndice A/B coincide con el dato (donde el texto trae una cifra, el script
   la recalcula desde los datos y compara).

## Orden de ejecución

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

Si `x8_verificar.py` reporta FALLA, corrige y repite. No des el STATUS `done` con controles en FALLA.

## Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: la lista de hojas (nombre y filas), el resultado de cada
control de `x8_verificar.py` y el peso del archivo. En UNRESOLVED: lo que no se pudo verificar.

---

## ADENDA (2026-10-15, pedida por el usuario): los KALINA «fuera de rango» NO se excluyen, se muestran completos

El usuario preguntó por qué se marcan los KALINA con T_fuente > ~170 °C si el límite de la campaña llega
a 300 °C. Respuesta verificada en `src/rangos_motor.py` y en los datos, que debe quedar escrita en el libro:

- **Qué mide la marca:** no es la T_fuente. Es la temperatura de un **estado interno del ciclo** (líquido o
  bifásico: T2 a la salida del HRVG, T5 del líquido del separador) por encima de **420 K**. Fuente: IAPWS
  G4-01 §6 (Tillner-Roth y Friend 1998): los datos experimentales de líquido de la ecuación llegan solo
  hasta 420 K; por encima, el motor **extrapola**. El punto se calcula igual y se clasifica igual; solo se
  señala que el número viene de una extrapolación. Es la política «extrapolar y marcar» (modo A) del
  proyecto. El techo de presión del modelo (40 MPa) no se cruzó en ningún punto: todas las marcas de esta
  campaña (275 de los 1 753 KALINA) son de este tipo (`respaldo_experimental`, T > 420 K).
- **Por qué empieza hacia 150 °C:** T2 queda ~11 K (mediana) por debajo de la T_fuente; los KALINA sin marca
  llegan a T2 = T5 = 419.9 K como máximo.
- **Porcentaje de KALINA marcados por banda de T_fuente** (calcúlalo desde los datos y ponlo en una tabla):
  hasta 140 °C: 0 %; 140–150 °C: ~1 %; 150–160 °C: ~31 %; 160–170 °C: ~76 %; 170–180 °C: ~93 %;
  180–200 °C: ~97 %; 200–250 °C: ~98 %; 250–300 °C: 100 %.

**Cambios obligatorios por esta adenda:**

1. En `LEEME` añade la sección **«¿Por qué hay KALINA fuera de rango del motor?»** con el texto de arriba y
   la tabla por banda de T_fuente.
2. En TODA tabla resumen y gráfico donde aparezcan KALINA, muestra **tres cifras lado a lado**: *KALINA
   total*, *de ellos confiables* y *de ellos fuera de rango (extrapolación del motor)*. Nada se oculta ni
   se descarta; la palabra «no citable» NO se usa en ninguna parte del libro: se dice «el cálculo es
   extrapolación del motor, el ciclo sí es KALINA según el modelo».
3. En el Apéndice B, punto 1, usa el texto corregido de abajo (reemplaza al anterior), y en el estudio 4
   sustituye «Desde 170 °C casi todo KALINA está fuera del rango del motor» por: «La marca de
   extrapolación del motor (líquido > 420 K) aparece desde ~150 °C y afecta a ~76 % de los KALINA entre
   160 y 170 °C y a más del 93 % por encima de 170 °C; el ciclo sigue siendo KALINA según el modelo».

## ADENDA 2 (2026-10-16): corrección de redacción tras leer IAPWS G4-01 §6 (reemplaza lo dicho en la ADENDA)

Se leyó el PDF (`reference/IAPWS_G4-01_nh3h2o.pdf`, §6 «Range of Validity»). Lo que dice: la superficie
termodinámica cubre el espacio entre la línea de puntos triples y el **lugar crítico**, y es válida en
líquido y vapor hasta 40 MPa a temperaturas subcríticas. **Los datos experimentales** de una sola fase se
limitan a «líquido por debajo de 420 K y 40 MPa, y vapor por debajo de 10 MPa». No es un límite de validez
de la ecuación: es el límite de sus **datos experimentales**. Por encima de 420 K en líquido no hay datos
con que contrastarla y el documento no da su incertidumbre allí (solo dice que la extrapolación al
supercrítico «da resultados razonables, pero la exactitud es desconocida»). La guía declara 2 % de
incertidumbre en densidad de líquido, 1 % en vapor y 200 J/mol en entalpía de exceso, «en la región
descrita».

**Por tanto, cambia en TODO el libro la redacción (hojas, encabezados, gráficos, conclusiones, LEEME):**

- «fuera de rango del motor» → **«sin respaldo experimental (líquido > 420 K)»**.
- «extrapolación del motor» / «el motor extrapola» → **«sin datos experimentales de líquido; el modelo
  declara validez hasta el lugar crítico (IAPWS G4-01 §6) pero su incertidumbre allí no está documentada»**.
- «KALINA confiables» se mantiene como nombre de la columna, con la definición «KALINA con respaldo
  experimental (sin la marca de líquido > 420 K) y η/ε en [0.40, 0.95]».
- La columna del CSV sigue llamándose `fuera_rango`; en el libro su título es «Sin respaldo experimental
  (T líquido > 420 K)».
- Añade en LEEME: «El lugar crítico no se vigila en el motor (la guía avisa que su ubicación es incierta);
  con P_alta ≤ 5 MPa en esta campaña no se espera cruzarlo, pero no se comprobó punto por punto.»
- Mantén las cifras (275 de 1 753 KALINA con la marca; porcentajes por banda de T_fuente).

## Apéndice A — Conclusión de cada barrido (texto para las hojas de resumen)

**Estudio 0, referencia de Húsavík (fase 0).** Con ε_cond = 0.90, Húsavík (T_fuente 394.15 K, P_alta 3300,
P_baja 690, x_b 0.82) es CORREGIBLE por cavitación (m_O2 −0.26 K con piso 283.15 K); con ε_cond = 0.95 es
KALINA (η 12.0 %, m_O2 +0.80 K). El caudal no cambia η ni la clase: m_b de 1 a 20 kg/s solo multiplica las
potencias (diferencia de η 1.6e-11).

**Estudio 1, una variable.** Las eficiencias y efectividades (η_t, η_p, ε_HRVG, ε_reg) mantienen KALINA en
todo 0.40–0.95 en ambos centros. Lo que saca al ciclo de KALINA es la condensación, la presión baja y la
composición: en C1 ε_cond solo funciona en 0.95 y x_b en 0.55–0.90; en C2 x_b solo en 0.45–0.55 y P_alta
hasta 3750 kPa. En C1 η_t mueve η 8.1 puntos porcentuales entre sus KALINA; en C2 P_alta 6.8 y T_fuente 6.8.

**Estudio 2, pares.** ε_reg × η_t mantiene KALINA en las 49 combinaciones de ambos centros. ε_cond ×
T_sumidero en C1 solo tiene 3 de 49 KALINA (ε_cond 0.95 con sumidero de 5 a 10 °C); en C2 tiene 33 de 49.
Hay interacción (la combinación se cae antes que cada variable sola) en C1 ε_HRVG × T_fuente y en C2
T_fuente × P_baja y ε_HRVG × T_fuente.

**Estudio 3, LHS de 9 variables.** Con las 9 variables moviéndose a la vez, ~47 % (C1) y ~52 % (C2) de los
puntos son KALINA. Separan KALINA del resto: x_b, P_baja y ε_cond en C1; T_fuente, P_baja y T_sumidero en C2.
Mueven η (PRCC): η_t (+0.74 y +0.71), P_baja (−0.61 y −0.69) y x_b (+0.58 y +0.69). η máxima en el
muestreo: 13.7 % (C1) y 12.4 % (C2).

**Estudio 4, fuente de 70 a 300 °C.** Hay KALINA en los 13 niveles de T_fuente. A 70 °C aparece el primer
KALINA confiable (2 puntos; P_alta 1630–2200, P_baja 770–840, x_b 0.70–0.75; η 5.3 %). Desde 170 °C casi
todo KALINA está fuera del rango del motor (T2/T5 > 420 K) y desde 230 °C no hay ninguno confiable. η
máxima confiable: 13.6 % a 150 °C.

**Estudio 5, condensador × clima.** Con ε_cond < 0.85 no hay KALINA en ningún clima probado. La P_baja
mínima con ε_cond 0.95 es 700 kPa (10 °C), 1000 (20 °C) y 1250 (30 °C); con 0.90 sube a 1000 y 1250 (10 y
20 °C); con 0.85 solo hay KALINA a 10 °C con 1250 kPa. Cada −0.05 de ε_cond cuesta +250 a +300 kPa de P_baja.

**Estudio 6, P_alta baja × composición.** En C1 hay KALINA desde P_alta = 1000 kPa con x_b 0.40–0.80 (34
de 49 celdas; η máxima 12.0 %). En C2 solo con x_b 0.40–0.50, para cualquier P_alta entre 1000 y 3000 kPa
(13 de 49; η máxima 8.7 %).

**Estudio 7, fuente fría con presiones bajas.** Con fuente de 70–130 °C hay 45 KALINA confiables, con
P_baja 260–870 kPa, P_alta 820–2970 kPa y x_b 0.35–0.79. Mejor η: 10.5 % a 101 °C (P_alta 2970, P_baja
570, x_b 0.71).

**Estudio 8, mapa fuente × clima × P_baja** (P_alta 3000, x_b 0.70). La P_baja mínima con KALINA sube
alrededor de 100 kPa por cada +5 K de T_sumidero y con la T_fuente: de 400 kPa (90 °C, clima 5 °C) a 1250
kPa (170–200 °C, 25–30 °C). η máxima confiable 13.1 % (150 °C, 5 °C, P_baja 500). A 170 y 200 °C hay KALINA
pero ninguno confiable.

**Estudio 9, equipos baratos** (ε_cond 0.95). En C1, 25 de 27 combinaciones de η_t, ε_HRVG y ε_reg en
{0.40, 0.55, 0.70} son KALINA; con 0.40/0.40/0.40 sigue siendo KALINA pero con η 0.2 %; con
0.70/0.70/0.70, η 9.2 %. En C2, 18 de 27 son KALINA.

**Estudio 10, centros nuevos, una variable.** C3 (150 °C): KALINA con P_baja ≥ 600 kPa, T_sumidero hasta
22.5 °C y ε_cond 0.90–0.95. C4 (110 °C): P_baja ≥ 800 kPa, T_sumidero hasta 17.5 °C y solo ε_cond 0.95. Las
eficiencias 0.40–0.95 no sacan a ninguno de KALINA (salvo ε_HRVG baja en C4, con η de hasta 1.6 %).

**Estudio 11, centros nuevos, pares.** η máxima confiable: 14.4 % (C3, 150 °C, P_alta 5000 kPa —borde de la
caja—, P_baja 650, x_b 0.75) y 13.2 % (C4, 150 °C, P_baja 800, x_b 0.88). El par ε_cond × T_sumidero es el
más restrictivo (C3: 8 de 49 KALINA; C4: 5 de 49, contando el punto base de cada malla). Hubo 3 puntos que agotaron el tope de 600 s, los tres en
C4 con ε_cond 0.60–0.65.

## Apéndice B — Conclusión consolidada

1. **Hay KALINA en todo el rango de fuente de 70 a 300 °C.** Hasta ~150 °C todos están dentro del respaldo
   experimental del motor; entre 150 y 170 °C una parte (31–76 %) lleva la marca de extrapolación (líquido
   > 420 K, IAPWS G4-01 §6) y por encima de 170 °C casi todos. Esa marca indica que el número del motor
   viene de una extrapolación de la ecuación de estado, no que el ciclo deje de ser KALINA; por eso se
   muestran siempre las dos cifras (total y confiables).
2. **El condensador manda.** Con ε_cond < 0.85 no hay KALINA; cada −0.05 cuesta +250 a +300 kPa de P_baja
   (y por tanto eficiencia), y un clima cálido exige la efectividad máxima.
3. **Las eficiencias de turbina, bomba, HRVG y regenerador no sacan al ciclo de KALINA** en 0.40–0.95;
   solo mueven η. La palanca principal de η es η_t, seguida de P_baja (a menor P_baja, mayor η) y x_b.
4. **Presiones por clima y fuente:** la P_baja mínima sube ~100 kPa por cada +5 K de clima, y con la
   T_fuente. P_alta tiene mucho margen (desde 1000 kPa hay KALINA en C1; en C2 casi no influye).
5. **Eficiencia alcanzable:** 13–14.4 % confiable con fuente de ~150 °C, clima de 5–10 °C, P_baja
   410–800 kPa y equipos de 0.85–0.95; con equipos de 0.70, ~9 %.
6. **Para preselección de equipos**, los rangos por kg/s de caudal (Δh de turbina, Wnet, Qreg/Qi, r_P, Qout)
   están en la síntesis S4; el caudal solo escala las potencias.
7. **Límites:** modelo teqp sin validación experimental; los KALINA a fuente > 170 °C quedan fuera del
   rango confiable; los muestreos (estudios 3, 4 y 7) dan ventanas aproximadas, no fronteras exactas; m_b
   no se barrió porque solo escala las potencias.

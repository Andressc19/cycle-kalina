# Metodología de análisis, organización y reporte de resultados — campaña final M1–M10b

**Fecha:** 2026-10-10 · **Rama:** `test/barrido_final` (worktree `.claude/worktrees/barrido-final`) ·
**Estado:** EJECUTADA el 2026-10-10 (ver `analisis_final/REPORTE_ANALISIS_FINAL.md`). **Rev. 2 (2026-10-10):** se agregan las reglas de
presentación del §3A (bloques de comparabilidad, condiciones fijas en cada figura y tabla, pies de
figura completos y todo en español) y el libro nuevo `datos/Excel_kalina_final_final_final.xlsx`.
**Alcance:** solo la campaña final (M1–M10b). Las fases F1/F2/F3 de septiembre
(`resultados/barridos_2026-09-19/`) se citan como antecedente, no se analizan como casos.
**Fuentes de datos:** `resultados/2026-10-0*_final_*/` (CSV + `REPORTE_*.md`) y
`datos/Excel_final_kalina.xlsx` (81 hojas). Protocolo de los barridos:
`docs/METODOLOGIA_BARRIDOS_FINAL.md`; fórmulas: `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md`.

> Este documento NO corre barridos nuevos. Todo lo que aquí se calcula sale de los CSV que ya existen.
> Las suposiciones van marcadas como **[SUPUESTO]**.

---

## 0. Reglas de la casa que este análisis respeta

| Regla | Consecuencia para el análisis |
|---|---|
| Claude diseña y verifica; OpenCode ejecuta todo el código | Cada script de tablas/figuras sale de un `TASK_CONTEXT` y se audita antes de aceptarse (§9) |
| No tocar `src/`, `app.py`, `ui_*.py` | Todo el código nuevo va en `scripts/analisis_final/` |
| El Excel nunca se edita a mano | Las tablas nuevas se generan con script; si van al Excel, con el formato F1/F2/F3 de `scripts/formatear_excel_barridos.py` |
| Ningún punto se oculta | NO_CONVERGIO, N2 y `fuera_rango` aparecen en conteos y figuras (con su marca) |
| η/ε en [0.40, 0.95] | Lo que esté fuera (M8) se etiqueta ANECDÓTICO y no entra en conclusiones |
| Prioridad: RANGOS KALINA conservando datos del profesor; η es secundaria | El orden de los capítulos y de las conclusiones sigue esa prioridad |
| Reportes en lenguaje llano | Cada ficha: pregunta → método simple → tabla → conclusión → lo no sabido → qué sigue |

---

## 1. Definiciones comunes (se aplican igual en todos los casos)

| Término | Definición operativa | Columna(s) |
|---|---|---|
| Punto del profesor (PP) | P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50, T_fuente 623.15 K, T_sumidero 300.032917 K, ε 0.85/0.75/0.80, η_t 0.85, η_p 0.75, m_b 1 kg/s | `comun.PROFESOR` |
| Ancla A\* | PP con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η 8.48 %) | — |
| **Punto genuino** | clase ∈ {KALINA, CORREGIBLE, INVIABLE}. Una fila con `convergio=True` y clase NO_CONVERGIO es un fijo espurio **N2** y cuenta como NO convergido | `clasificacion`, `convergio` |
| KALINA confiable | KALINA y `fuera_rango = False` (IAPWS G4-01 §6) | `fuera_rango` |
| Punto omitido | `P_baja ≥ P_alta − 300` en M4c/M5: no se evaluó; se reporta, no se clasifica | `omitido` |
| Criterios de bloqueo | O1 título a la salida de turbina · O2 cavitación (subenfriamiento en bomba) · O3 trabajo neto ≤ 0 · O5 separador · C1/C3/S6/N2 convergencia | `codigos_falla`, `viol_O*`, `m_O*` |
| Piso de O2 | 300.032917 K en M1–M3; desde M2S = `T_sumidero` del punto | `T_amb_diseno` |
| Índice de cercanía D | Ver MATEMATICA §2 (τ = 0.01 / 1 K / 1 kW / 0.01) | `D` |
| Distancia al profesor d | Σ \|v − v_PP\| / (b − a) con rangos de M3 | `d` |
| Diferenciales | dP = P_alta − P_baja; rP = P_alta / P_baja; dT_fs = T_fuente − T_sumidero | derivadas |
| Banda de incertidumbre de η | ±0.4–0.7 pp (G4-01). Diferencias menores = **no concluyentes** | — |
| Δη válido | Solo sobre puntos genuinos con W_net > 0 (lección de la nota del director en M3) | `Wnet` |

---

## 2. Organización de datos: barridos y variables modificadas (tarea 1)

### 2.1 Inventario de casos

Leyenda de variables: TF T_fuente · TS T_sumidero · PA P_alta · PB P_baja · XB x_b ·
ηt, ηp · εH ε_HRVG · εR ε_reg · εC ε_cond. "Base" = punto desde el que se mueve.

| ID caso | Fecha | Familia | Base | Variables barridas | Diseño | Corridas (aprox.) | CSV principal |
|---|---|---|---|---|---|---|---|
| KF-M01 | 10-06 | R | PP | PA, XB, TS (perfil horario) | 1D sobre PP | 42 | `m1_filas.csv` |
| KF-M02-N1 | 10-06 | F | PP | las 10, una a la vez | malla 10 + bisección | 100 + bisec. | `m2n1_malla.csv` |
| KF-M02-N2 | 10-06 | F | PP | εH o TF, cada uno × PB | malla 2D 12 + bisección | 144 + bisec. | `m2n2_kalina.csv` |
| KF-M02R | 10-06 | F | PP | igual que M2 con η/ε en [0.40, 0.95]; + (TF, εC) | malla + bisección (3 partes) | ~300 | `m2r_kalina.csv` |
| KF-M02S | 10-06 | F | B1–B4 | TS × PB (4 bases) | malla 2D + bisección | 200 + bisec. | `m2s_malla.csv` |
| KF-M03 | 10-06 | L | A\* | las 10, una a la vez | OAT 15 + A\*±1 % | 171 | `m3_ofat.csv` |
| KF-M04 | 10-06 | G | caja M4 | las 10 a la vez | LHS 300 (semilla 20261006) | 300 | `m4_lhs.csv` |
| KF-M04b | 10-07 | G | caja M4 | las 10 a la vez | LHS 200 (semilla 20261007) → unión 500 | 200 | `m4b_lhs.csv` |
| KF-M04c | 10-07 | G | caja M4, PB 1500–2500 | las 10 | LHS 150 (semilla 20261008) | 135 + 15 omit. | `m4c_lhs.csv` |
| KF-M05 | 10-07 | C | PP parcial | libres según escenario S1–S5 | LHS 120 × 5 | 600 | `m5_lhs.csv` |
| KF-M05c | 10-07 | C | PP con PA/PB fijas | TF × εC × TS | malla 11×5×3 | 165 | `m5c_malla.csv` |
| KF-M06 | 10-08 | V | puntos clave | — (motor real vs teqp; subenfriamiento) | verificación | ~10 + evals | `m6_*.csv` |
| KF-M07 | 10-07 | O | mejores KALINA | según arranque A1–A5 | búsqueda por patrones | ver CSV | `m7_evaluaciones.csv` |
| KF-M08 | 10-07 | X | A\* | η/ε fuera de [0.40, 0.95] | OAT | ver CSV | `m8_oat.csv` |
| KF-M09 | 10-08/09 | C | PP parcial | grupos EF/PA/PB/TF/TS/XB conservados | escalera forward + LHS | ~850 | `m9_escalera.csv` |
| KF-M10 | 10-09 | H | Húsavík (Fase 3) | 10 variables OFAT + malla XB × PB | recorrida + OFAT + malla 2D | ver CSV | `m10_*.csv` |
| KF-M10b | 10-09 | H | Húsavík | XB 0.30–0.70 × PB | OFAT + malla 2D | ver CSV | `m10b_*.csv` |

Familias: **R** reproducibilidad · **F** factibilidad / distancia al profesor · **L** sensibilidad local ·
**G** sensibilidad global · **C** conservación de datos del profesor · **O** optimización de η ·
**V** verificación · **H** caso real Húsavík · **X** anecdótico (fuera de rango realista).

Los conteos "ver CSV" y los marcados "aprox." quedaron fijados por A1 leyendo los CSV
(`analisis_final/00_inventario/conteo_por_subcaso.csv`; revisado el 2026-10-10).

### 2.2 "Qué se modificó" respecto al profesor

Para cada caso el agente A1 genera la matriz `casos_x_variables.csv`:
filas = casos/subcasos, columnas = 11 variables (+ piso O2, motor, rango η/ε),
celda ∈ {`=PP` fijo en el valor del profesor, `fijo:<valor>` fijo en otro valor, `barrido:[a,b]`, `n/a`}.
Así queda explícito, por ejemplo, que en M3 TF y PB están fijas en valores distintos del profesor
aunque no se barran, y que el piso de O2 cambió de regla en M2S.

### 2.3 Tabla canónica única

Todos los CSV se apilan en **una** tabla larga `todos_los_puntos.csv` (una fila por evaluación) con:
`id_punto, id_caso, id_subcaso, tipo_punto (malla/biseccion/vecino/lhs/patron/control), origen_csv, fila_origen`
+ las 11 entradas + `T_amb_diseno, motor` + salidas (`clasificacion, eta, Wnet, m_O1…m_O5, D, codigos_falla`)
+ banderas calculadas (`genuino, es_N2, kalina_confiable, omitido, wnet_pos`) + derivadas (`dP, rP, dT_fs, d`).
Las columnas que un CSV no trae quedan vacías (nunca rellenadas con supuestos).

---

## 3. Conclusiones (tarea 2) — estructura y borrador

### 3.1 Plantilla de conclusión por barrido
Una conclusión por caso = **una frase de respuesta a la pregunta** + **la cifra que la sostiene** +
**el criterio que bloquea** + **la confianza** (n genuinos, n KALINA confiables, banda de η).

### 3.2 Conclusiones por barrido (validadas por A4 el 2026-10-10: 76 de 78 cifras coinciden; las 2 diferencias son de definición y están corregidas aquí)

| Caso | Conclusión en una línea |
|---|---|
| M1 | El código actual reproduce la F1 del profesor: 41 de 41 puntos siguen siendo NO_CONVERGIO |
| M2-N1 | Con un solo cambio no hay KALINA; lo que más acerca es bajar T_fuente a ~400 K (solo falla O2, por 2 K) |
| M2-N2 | Con dos cambios sí: T_fuente 390–434 K + P_baja → 59 KALINA (48 confiables); conservando la fuente del profesor (ruta ε_HRVG), 0 |
| M2R | 14 KALINA distintos con η/ε en [0.40, 0.95]. Los que conservan la fuente de 623 K (ε_HRVG 0.40–0.50 + P_baja 1318–2000 kPa) están todos fuera de rango; con las presiones del profesor + T_fuente 403 K + ε_cond 0.95 hay 1 confiable (η 9.5 %) |
| M2S | Un sumidero ~22 K más frío reduce a la mitad la P_baja mínima (B1: 563 → 291 kPa) y sube η 2–3 pp; el profesor exacto nunca es KALINA |
| M3 | A\* está a menos del 6 % del rango de la frontera de O2 en 8 de 9 variables; las palancas que suben η sin perder KALINA son ε_reg (hasta 10.96 %) y η_t (9.62 %) |
| M4/M4b | El 90 % de los 121 KALINA (p5–p95) tiene P_alta 2156–4842 kPa, P_baja 683–1461 kPa, ΔP 968–3718 kPa y r_P 1.69–5.34; deciden P_baja y ε_cond (KS 0.43) |
| M4c | Entre 1500 y 2500 kPa de P_baja sigue habiendo KALINA (33–75 % por franja): el límite superior es de eficiencia y de r_P, no de cavitación |
| M5 | Por muestreo, los escenarios que conservan la fuente de 623 K dan 2 KALINA confiables de 20; las presiones del profesor solo funcionan en una franja angosta que el LHS no alcanzó |
| M5c | Con las presiones del profesor: 104 de 165 KALINA, todos confiables, con T_fuente 390–410 K; con su clima (300 K) hace falta ε_cond ≥ 0.875 |
| M6 | teqp coincide con el motor real (que necesita ~1500 s por punto); O2 no tiene margen propio y 2 K de subenfriamiento cuestan +25–46 kPa de P_baja y < 0.5 pp de η |
| M7 | η máx. 15.6 % conservando las presiones y el clima del profesor (T_fuente 415 K, equipos a 0.95); 12.7 % conservando sus temperaturas (con x_b 0.85 y P_alta 5000 kPa) |
| M8 | Anecdótico; no se usa en conclusiones |
| M9 | Se conservan 8 de 10 datos de diseño (XB+PA+EF+PB) moviendo solo T_fuente (391–409 K) y T_sumidero (280–293 K): 5 de 5 KALINA confiables; ningún conjunto con TF da KALINA confiables |
| M10 | Húsavík: 97 de 97 KALINA de la Fase 3 reproducidos; P_baja mínima de 500 a 800 kPa al pasar x_b de 0.70 a 0.91; su P_baja real (690 kPa) coincide con la mínima KALINA |
| M10b | Con x_b < 0.50 el modelo no encuentra ciclo (0 genuinos de 32); x_b = 0.50 es KALINA formal con η < 1.3 %; el KALINA útil empieza en x_b ≈ 0.55 (P_baja mín. 300 kPa) |

### 3.3 Conclusiones generales (validadas)
1. **El bloqueo estructural del enunciado es la fuente a 623 K.** Con ella el punto del profesor no
   converge. Solo aparecen KALINA confiables alejándose mucho del resto del enunciado (x_b 0.71–0.85,
   P_alta 3200–5000 kPa, P_baja 1.36–1.97 MPa; M7-A3 y M5-S1). Combinada con la x_b o las presiones
   del profesor, no hay ninguno (M9, M2S-B3, M5-S4/S5 y M7-A5: 0 confiables).
2. **Bajando la fuente a ~390–410 K, casi todo el enunciado se conserva:** 8 de 10 datos de diseño
   (M9), o las 2 presiones con ε_cond ≥ 0.875 en su clima de 300 K (M5c).
3. **La cavitación (O2) es el criterio que manda** en todas las familias. Se cierra subiendo P_baja,
   y dar 2 K de margen cuesta poco (M6).
4. **Ventana de presiones:** el 90 % de los KALINA tiene P_baja de 683 a 1461 kPa y r_P de 1.7 a 5.3
   (M4/M4b). La P_baja mínima baja con un clima frío (M2S) y sube con más amoníaco (M10).
5. **η es secundaria:** ~8–11 % en diseños con eficiencias medias (A\*, M5c, M9) y hasta 15.6 % con
   equipos a 0.95 (M7). Las diferencias menores que 0.7 pp no son concluyentes.
6. **El modelo queda validado** por la reproducción de M1 y Húsavík (M10), la coincidencia con el
   motor real (M6/M9) y la validación cruzada de A4.

---

## 3A. Reglas de presentación: no mezclar datos con condiciones distintas

Los barridos no comparten los mismos datos fijos. M3 fija todo en A\* con el piso de O2 en 300.03 K;
M4 mueve las 10 variables en una caja con el piso de O2 igual a T_sumidero; cada escenario de M5 fija
un subconjunto distinto de datos del profesor. Un punto de M3 y uno de M5-S2 **no son comparables**,
aunque tengan la misma P_baja. Por eso toda la presentación se organiza por **bloques de
comparabilidad** y cada figura y cada tabla dicen exactamente bajo qué datos se obtuvieron.

### 3A.1 Bloques de comparabilidad

Un bloque es un conjunto de puntos que comparten **las mismas variables fijas, con los mismos valores,
el mismo piso de O2, el mismo rango de η/ε y el mismo motor**. Solo se grafican o tabulan juntos los
puntos de un mismo bloque.

| Bloque | Casos / subcasos | Qué tienen en común | Qué cambia dentro del bloque |
|---|---|---|---|
| B01 | KF-M01 | PP; piso O2 300.03 K | P_alta, x_b o T_sumidero (una a la vez) |
| B02 | KF-M02-N1 | PP; η/ε en [0.75, 0.85]; piso O2 300.03 K | una variable a la vez |
| B03 | KF-M02-N2-A / -B (una figura por ruta) | PP salvo el par movido; piso O2 300.03 K | ε_HRVG o T_fuente, × P_baja |
| B04 | KF-M02R (una figura por parte: n1, n2a, n2b, n3) | PP; η/ε en [0.40, 0.95]; piso O2 300.03 K | según la parte |
| B05 | KF-M02S-B1 … B4 (una curva por base, nunca mezcladas en el mismo eje sin leyenda) | PP salvo la base; **piso O2 = T_sumidero** | T_sumidero × P_baja |
| B06 | KF-M03 | A\*; piso O2 300.03 K | una variable a la vez |
| B07 | KF-M04 + KF-M04b (unión permitida: misma caja, mismo piso) | caja M4; piso O2 = T_sumidero | las 10 a la vez |
| B08 | KF-M04c | caja M4 con P_baja 1500–2500 kPa | las 10 a la vez |
| B09 | KF-M05-S1 … S5 (un bloque por escenario) | los datos del profesor que conserva cada escenario | las variables libres del escenario |
| B10 | KF-M05c | P_alta 3000 y P_baja 400 kPa, resto PP; piso O2 = T_sumidero | T_fuente × ε_cond × T_sumidero |
| B11 | KF-M07-A1 … A5 (uno por arranque) | restricción de cada arranque | búsqueda por patrones |
| B12 | KF-M06 | puntos de control | motor (teqp contra motor real) |
| B13 | KF-M09-R0 … R3 (uno por conjunto conservado) | los grupos conservados en esa ronda | variables libres |
| B14 | KF-M10, KF-M10b (según §3A.2) | base Húsavík | OFAT o x_b × P_baja |
| BX | KF-M08 | — | **ANECDÓTICO**; nunca se mezcla con nada |

**Confirmado por A1 (2026-10-10):** la columna "qué tienen en común" sale de los REPORTE_* y A1 la confirmó o
la corrigió al **detectar desde los datos** qué columnas son constantes en cada subcaso (§3A.2). Si A1
encuentra que dos subcasos que aquí aparecen en el mismo bloque no tienen las mismas condiciones, el
bloque se parte.

### 3A.2 Tabla de condiciones (generada desde los datos, no escrita a mano)

A1 produce `00_inventario/condiciones_por_subcaso.csv`: una fila por subcaso × variable, con
`estado ∈ {fijo, barrido}`, `valor_fijo` (si es fijo), `min, max, n_valores` (si es barrido),
`igual_al_profesor (sí/no)` y `unidad`. Incluye T_amb_diseno (piso de O2), el motor y el rango
nominal de η/ε. **Los pies de figura y los encabezados de tabla se arman leyendo este archivo**, así
que no pueden contradecir los datos.

### 3A.3 Qué se grafica y qué no, según el diseño del barrido

| Diseño | Se grafica | No se grafica |
|---|---|---|
| Una variable a la vez (M1, M2-N1, M3, M10 OFAT) | curva salida–variable, un panel por variable, con la base marcada | varias variables en un mismo eje x (tienen unidades distintas); el único eje común permitido es la fracción del rango, y solo en FIG-M03-04 |
| Malla 2D (M2-N2, M2R, M2S, M5c, M10 malla) | mapa de clases en el plano de las dos variables movidas, con la frontera de bisección | proyecciones 1D que ocultan la segunda variable |
| LHS (M4, M4b, M4c, M5, M9) | dispersión en planos con sentido físico (P_alta–P_baja, T_fuente–P_baja), CDF del RSA, índices de sensibilidad, histogramas de dP y rP | curvas que unan puntos: en un LHS no hay orden |
| Búsqueda (M7) | η por iteración y tabla de óptimos | dispersión de las evaluaciones como si fueran una muestra |
| Verificación (M6) | paridad teqp contra motor real | — |

Reglas que valen para todo:
- η solo se grafica en puntos genuinos con W_net > 0. Los demás aparecen como marca sobre el eje, sin valor.
- Una variable que en ese bloque está fija **nunca** va en un eje.
- Si una figura junta dos subcasos (por ejemplo, curvas de M2S por base), cada serie se identifica en
  la leyenda con lo que la distingue ("Base B2: T_fuente = 420 K").

### 3A.4 Contenido obligatorio de cada figura

1. **Título** (dentro de la figura, una línea, en español): qué muestra. Ejemplo: "Eficiencia según
   cada variable, una a la vez, alrededor del ancla A\*".
2. **Ejes** con el nombre completo en español y la unidad: "Presión de baja, P_baja [kPa]".
3. **Leyenda** en español, con n por serie: "KALINA (n = 86)".
4. **Recuadro de condiciones** (texto pequeño dentro de la figura, esquina libre): bloque, caso y lo
   fijo esencial. Así la imagen se entiende aunque se copie sola.
5. **Pie de figura** (debajo de la imagen, en el informe y en el Excel), con esta plantilla:

```
Figura FIG-M03-03. <Qué muestra, en una frase>.
Caso: KF-M03 (bloque B06) — sensibilidad local alrededor de A*.
Datos fijos: T_fuente = 403.0 K; P_baja = 563.6 kPa; P_alta = 3000 kPa; x_b = 0.50;
  T_sumidero = 300.03 K; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.80;
  piso de O2 = 300.03 K; motor teqp. En cada panel se mueve solo la variable del eje x.
Datos barridos: cada variable en 15 valores equiespaciados de su rango (ver TAB-M03-00).
Filtro: puntos genuinos; η solo con trabajo neto > 0; × = no convergido o falso convergido (N2).
Marcas: línea punteada = valor en A*; marcador hueco = fuera del rango confiable (IAPWS G4-01).
n = 171 corridas (148 genuinas, 86 KALINA). Fuente: resultados/2026-10-06_final_M3/m3_ofat.csv.
```

Los pies se guardan también como `03_figuras/<ID>.pie.md`, para que el informe y el Excel usen el mismo texto.

**Regla de términos (pedido del usuario, 2026-10-10):** ningún símbolo propio del proyecto aparece
solo. Los términos son A\*, PP, N2, O1–O5, el piso de O2, D, d, "genuino" y "fuera de rango".
- Toda ficha abre con un recuadro "Antes de leer" que define los que usa.
- Todo pie de figura y todo encabezado de tabla nombran el punto base con su definición corta. Ejemplo:
  "A\* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa".
- El tablero y el libro Excel llevan el glosario completo (`LEEME` y pestaña Glosario).
- La lista de definiciones vive en `scripts/analisis_final/nombres.py` (`GLOSARIO`), para que todos
  los productos usen el mismo texto.

### 3A.5 Contenido obligatorio de cada tabla

Cada tabla (en Markdown y en su hoja del Excel) tiene tres partes, en este orden:
1. **Encabezado:** ID, título en español, caso y bloque, datos fijos (en una línea, como en el pie de figura).
2. **Cuerpo:** columnas con el nombre en español y la unidad entre corchetes.
3. **Notas:** filtro aplicado, n, significado de † y ‡, fuente (CSV y filtro) y [SUPUESTO] si hay.

Una tabla nunca junta filas de bloques distintos. Las únicas excepciones son las tablas de síntesis
(§6.2, `TAB-G*`). En ellas cada fila es un caso y lleva su propia columna de "datos fijos": resumen
casos lado a lado, no mezcla sus puntos.

### 3A.6 Nombres en español (diccionario único)

`scripts/analisis_final/nombres.py` (lo escribe A1) traduce cada columna a su nombre de presentación. Ejemplos:

| Columna | Nombre en figuras y tablas |
|---|---|
| T_fuente | Temperatura de la fuente, T_fuente [K] |
| T_sumidero | Temperatura del sumidero, T_sumidero [K] |
| P_alta / P_baja | Presión de alta / de baja [kPa] |
| x_b | Fracción de amoníaco de la mezcla base, x_b [–] |
| eta_t / eta_p | Eficiencia isentrópica de la turbina / de la bomba [–] |
| eps_hrvg / eps_reg / eps_cond | Efectividad del generador de vapor / del regenerador / del condensador [–] |
| eta | Eficiencia térmica del ciclo, η [%] |
| Wnet | Trabajo neto, W_net [kW] (base m_b = 1 kg/s) |
| dP / rP | Diferencia de presiones, ΔP [kPa] / Razón de presiones, r_P [–] |
| m_O2 | Margen de cavitación en la bomba, O2 [K] (T de burbuja a P_baja − T9; confirmado en `src/restricciones/operativos.py`) |
| clasificacion | Clase del ciclo |
| N2 | Falso convergido (N2) |

---

## 4. Catálogo de gráficas Matplotlib (tarea 3)

### 4.1 Reglas de estilo comunes (`scripts/analisis_final/estilo.py`)

Estas reglas salen de las skills `data:data-visualization` y `data:build-dashboard`, adaptadas al proyecto:
- **El título dice la conclusión**, no solo el contenido: "A\* está a menos del 6 % del rango de la
  frontera de O2 en 8 de 9 variables" es mejor que "Distancia a la frontera". El subtítulo (2.ª
  línea, más chica) dice el caso y el bloque.
- **El color nunca va solo.** Cerca del 8 % de los hombres no distingue el verde del rojo, y KALINA
  (verde) contra NO_CONVERGIO (rojo) es justo ese par. Por eso cada clase lleva también una forma
  propia: KALINA ●, Corregible ▲, Inviable ■, No convergió ✕, N2 ✕ gris. La figura se tiene que
  entender también impresa en blanco y negro.
- **Las barras arrancan en cero**, y los paneles que se comparan comparten la escala (`sharey`).
- **Se muestra la incertidumbre:** banda de η ±0.7 pp e intervalos de bootstrap en los índices de M4.
- **Se ordena por magnitud** (rankings, tornado), salvo que haya un orden natural (rondas de M9, valores de la malla).
- **Sin decoración:** no se usan 3D, tortas ni rejillas fuertes. El doble eje y solo se acepta en
  FIG-M02S-01, y ahí se reemplaza por 2 paneles.
- **Todo en español:** títulos, ejes, leyendas, recuadro de condiciones y pies (diccionario del §3A.6).
- **Título dentro de la figura** (una línea) y **pie completo debajo** (§3A.4). El recuadro de
  condiciones va dentro de la figura, en letra de 7 pt.
- Colores por clase (mismo tono que el Excel, más saturado para el trazo): KALINA `#2E7D32`,
  CORREGIBLE `#EF8A17`, INVIABLE `#C9A227`, NO_CONVERGIO `#C62828`; falso convergido (N2) gris `#9E9E9E`.
- Marcadores: punto genuino ● · NO_CONVERGIO y N2 × sobre el eje · fuera del rango confiable = marcador hueco.
- Referencias: punto del profesor = estrella negra; A\* = rombo; línea punteada en el valor base.
- η en %, presiones en kPa, temperaturas en K; decimales iguales a los de las tablas (§6.1).
- 16 × 10 cm (o 16 × 20 cm con paneles), 300 dpi, PNG + SVG, letra de 9–10 pt.
- Cuando se comparen valores de η, se sombrea la banda de ±0.7 pp.

### 4.2 Catálogo (una figura = un bloque, salvo las de síntesis `FIG-G*`)

| ID | Bloque | Caso / subcaso | Tipo | Eje x | Eje y | Color / leyenda | Filtro | Título (en la figura) |
|---|---|---|---|---|---|---|---|---|
| FIG-G01 | síntesis | todos | barras horizontales apiladas | número de corridas | caso | clase (4 + N2) | ninguno | Resultado de cada barrido por clase |
| FIG-G02 | síntesis | todos | matriz de estados | variable | caso | barrida / fija en el valor del profesor / fija en otro valor | — | Qué variables se movieron y cuáles quedaron fijas en cada barrido |
| — | B01 | KF-M01 | **solo tabla** (41/41 NO_CONVERGIO: no hay nada que graficar) | — | — | — | — | — |
| FIG-M02-01 | B02 | KF-M02-N1 | 10 paneles, uno por variable, cada uno con su eje en sus unidades | la variable | clase (franja de color) | clase | todos | Un solo cambio sobre los datos del profesor |
| FIG-M02-02a/b | B03 | KF-M02-N2 ruta A / ruta B (una figura por ruta) | mapa de clases | P_baja [kPa] | ε_HRVG (ruta A) / T_fuente [K] (ruta B) | clase; frontera de bisección como línea | genuinos + no convergidos | Dos cambios sobre los datos del profesor — ruta A/B |
| FIG-M02R-01…04 | B04 | KF-M02R, una por parte | mapa o curva, según la parte | variable 1 | variable 2 | clase | todos | Dos cambios con η y ε en [0.40, 0.95] — parte … |
| FIG-M02S-01 | B05 | KF-M02S-B1…B3 | 2 paneles: P_baja mínima y η máxima | T_sumidero [K] | P_baja mín. [kPa] / η [%] | una serie por base, con su dato en la leyenda | KALINA | Efecto de un sumidero más frío (piso de O2 = T_sumidero) |
| FIG-M03-01 | B06 | KF-M03 | tornado | Δη [pp] | variable | — | genuinos con W_net > 0 | Variación de η en el rango de cada variable alrededor de A\* |
| FIG-M03-02 | B06 | KF-M03 | barras | elasticidad E [–] | variable | signo de E | — | Elasticidad local de η en A\* |
| FIG-M03-03 | B06 | KF-M03 | 10 paneles | la variable | η [%] | clase | todos (× para no convergidos) | Eficiencia según cada variable, una a la vez, alrededor de A\* |
| FIG-M03-04 | B06 | KF-M03 | puntos sobre escala común | distancia a la frontera (fracción del rango) [–] | variable | margen que se rompe | cruces | Qué tan cerca está A\* de cada frontera |
| FIG-M04-01 | B07 | KF-M04 + M04b | CDF, un panel por variable | la variable | probabilidad acumulada [–] | KALINA / no KALINA; KS y p en la leyenda | genuinos | Qué variables separan a los KALINA del resto |
| FIG-M04-02 | B07 | KF-M04 + M04b | dispersión | P_alta [kPa] | P_baja [kPa] | clase; rectas r_P = 1.69 y 5.34 | todos | Ventana de presiones donde aparece KALINA |
| FIG-M04-03 | B07 | KF-M04 + M04b | barras | índice PRCC / PAWN [–] | variable | signo | genuinos con W_net > 0 | Influencia de cada variable sobre η |
| FIG-M04-04 | B07 | KF-M04 + M04b | 2 histogramas | ΔP [kPa] / r_P [–] | número de puntos | KALINA / resto | genuinos | Diferencia y razón de presiones en los KALINA |
| FIG-M04c-01 | B08 | KF-M04c | barras por franja | P_baja (franjas de 100 kPa) | % KALINA | P_alta en terciles | evaluados | Dónde termina KALINA al subir P_baja |
| FIG-M05-01…05 | B09 | KF-M05-S1…S5 (**una figura por escenario**) | dispersión | P_alta [kPa] (si está libre) | P_baja [kPa] | clase | evaluados | Escenario S…: conservando … del profesor |
| FIG-M05c-01 | B10 | KF-M05c | 3 mapas, uno por T_sumidero | T_fuente [K] | ε_cond [–] | clase | — | Franja KALINA con las presiones del profesor |
| FIG-M06-01 | B12 | KF-M06 | paridad | η con teqp [%] | η con el motor real [%] | coincide sí/no; banda de ±0.7 pp | pares válidos | teqp contra el motor real |
| FIG-M07-01 | B11 | KF-M07 (una curva por arranque) | curvas | iteración | η [%] | arranque, con su restricción en la leyenda | — | Avance de la búsqueda de η máxima |
| FIG-M09-01 | síntesis | KF-M09 R0…R3 | barras | conjunto conservado | KALINA confiables | ronda; el conjunto elegido resaltado | — | Escalera de conservación de los datos del profesor |
| FIG-M10-01 | B14 | KF-M10 (+ M10b si A1 confirma que comparten condiciones) | mapa de clases | x_b [–] | P_baja [kPa] | clase; curva de P_baja mínima | todos | Húsavík: composición contra presión de baja |

Se eliminan la antigua FIG-G03, que juntaba rangos de M4b, M5, M9 y M10 en un solo eje, y la
dispersión antes/después de M1. Esa comparación pasa a la tabla de síntesis TAB-G03, donde cada fila
lleva sus propios datos fijos.

### 4.3 Código base

```python
# scripts/analisis_final/estilo.py  (lo escribe OpenCode a partir de este bloque)
import matplotlib.pyplot as plt

COLOR_CLASE = {"KALINA": "#2E7D32", "CORREGIBLE": "#EF8A17",
               "INVIABLE": "#C9A227", "NO_CONVERGIO": "#C62828", "N2": "#9E9E9E"}
ORDEN_CLASE = ["KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO", "N2"]
MARCADOR_CLASE = {"KALINA": "o", "CORREGIBLE": "^", "INVIABLE": "s",
                  "NO_CONVERGIO": "x", "N2": "x"}   # forma + color: se entiende sin color

def aplicar_estilo():
    plt.rcParams.update({"figure.figsize": (6.3, 3.9), "figure.dpi": 150,
                         "savefig.dpi": 300, "font.size": 9, "axes.grid": True,
                         "grid.alpha": 0.3, "axes.spines.top": False,
                         "axes.spines.right": False, "legend.frameon": False})

def clase_trazo(row):
    """Clase para colorear: separa N2 (convergio=True pero NO_CONVERGIO)."""
    if row["clasificacion"] == "NO_CONVERGIO" and bool(row.get("convergio")):
        return "N2"
    return row["clasificacion"]

ETIQUETA_CLASE = {"KALINA": "KALINA", "CORREGIBLE": "Corregible", "INVIABLE": "Inviable",
                  "NO_CONVERGIO": "No convergió", "N2": "Falso convergido (N2)"}

def recuadro_condiciones(ax, texto):
    """Recuadro con el bloque y los datos fijos esenciales, dentro de la figura."""
    ax.text(0.99, 0.01, texto, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7, bbox=dict(boxstyle="round", fc="white", ec="0.7", alpha=0.9))

def guardar(fig, ruta_sin_ext, pie):
    """Guarda PNG + SVG y el pie de figura en <ruta>.pie.md (mismo texto para informe y Excel)."""
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(f"{ruta_sin_ext}.{ext}", bbox_inches="tight")
    with open(f"{ruta_sin_ext}.pie.md", "w", encoding="utf-8") as f:
        f.write(pie)
    plt.close(fig)
```

```python
# Ejemplo: FIG-M04-02, plano de presiones del bloque B07 (M4 + M4b)
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from estilo import (COLOR_CLASE, ORDEN_CLASE, ETIQUETA_CLASE, MARCADOR_CLASE, aplicar_estilo,
                    clase_trazo, recuadro_condiciones, guardar)
from nombres import NOMBRE                       # diccionario del §3A.6
from pies import armar_pie                       # lee condiciones_por_subcaso.csv

aplicar_estilo()
df = pd.read_csv("analisis_final/01_datos/todos_los_puntos.csv")
df = df[df["bloque"] == "B07"].copy()            # se filtra por BLOQUE, nunca por una lista suelta de casos
df["clase_t"] = df.apply(clase_trazo, axis=1)

fig, ax = plt.subplots()
for c in ORDEN_CLASE[::-1]:                      # KALINA queda encima
    s = df[df["clase_t"] == c]
    hueco = s["fuera_rango"].fillna(False).astype(bool)
    ax.scatter(s.loc[~hueco, "P_alta"], s.loc[~hueco, "P_baja"], s=14,
               color=COLOR_CLASE[c], label=f"{ETIQUETA_CLASE[c]} (n = {len(s)})",
               marker=MARCADOR_CLASE[c])
    ax.scatter(s.loc[hueco, "P_alta"], s.loc[hueco, "P_baja"], s=14,
               facecolors="none", edgecolors=COLOR_CLASE[c], marker=MARCADOR_CLASE[c])
pa = np.linspace(df["P_alta"].min(), df["P_alta"].max(), 50)
for rp in (1.69, 5.34):                          # p5 y p95 de r_P en los KALINA (REPORTE_M4b §13)
    ax.plot(pa, pa / rp, "k--", lw=0.8)
ax.set_title("KALINA aparece solo con razón de presiones entre 1.7 y 5.3\n"
             "Bloque B07 · M4 + M4b", fontsize=9)   # el título dice la conclusión (validada por A4)
ax.set_xlabel(NOMBRE["P_alta"]); ax.set_ylabel(NOMBRE["P_baja"])
ax.legend(loc="upper left", fontsize=8)
recuadro_condiciones(ax, "Bloque B07 · M4 + M4b (LHS de 500 puntos)\n"
                         "10 variables libres · piso de O2 = T_sumidero · motor teqp")
guardar(fig, "analisis_final/03_figuras/FIG-M04-02_plano_presiones",
        pie=armar_pie("FIG-M04-02", bloque="B07", filtro="todos los puntos evaluados",
                      marcas="rectas punteadas: r_P = 1.69 y 5.34 (p5 y p95 de los KALINA)"))
```

---

## 4B. Tableros interactivos (dashboards)

### 4B.1 Qué formato se usa para qué

Hay tres formas de mostrar los **mismos datos** (la tabla canónica y `condiciones_por_subcaso.csv`). Cada una sirve para algo distinto:

| Formato | Para qué sirve | Interactividad | Lo construye | Estado |
|---|---|---|---|---|
| **Matplotlib** (PNG/SVG) | Informe escrito, presentación y tesis: figuras fijas con pie completo | ninguna | A3 | §4 |
| **Tablero HTML** (`tablero_kalina.html`) | **El tablero principal para el profesor.** Se abre con doble clic en cualquier navegador, sin instalar nada, y se puede compartir como enlace privado | alta: filtros por bloque, caso y clase, ejes a elección, tooltips, tabla ordenable | A5 (nuevo) | §4B.2 |
| **Tablero en Excel** (hoja `Tablero` del libro nuevo) | Que el profesor explore desde Excel, que ya conoce | media: lista desplegable de bloque → KPIs y gráficos que se actualizan solos, más filtros de tabla | A2 | §4B.3 |
| **Power BI** | **Descartado** (decisión del usuario, 2026-10-10) | — | — | §4B.4 |

**Decisión (2026-10-10, usuario):** todo queda en **Excel** por practicidad; la hoja `Tablero` es el
tablero interactivo oficial y el HTML es un extra. Power BI se descarta: no lo exige ninguna skill y,
además, **Power BI Desktop no está instalado** en este equipo: el chequeo del 2026-10-10 encontró solo
Office ProPlus 2024. Además, un `.pbix` no se puede generar desde un script; hay que armarlo a mano en
Power BI Desktop. Lo que sí se deja listo es el modelo de datos para importarlo.

### 4B.2 Tablero HTML (sigue la skill `data:build-dashboard`)

Un solo archivo HTML con los datos embebidos en JSON (~4 000 puntos, dentro del rango de 1 000–10 000
filas que la skill recomienda embeber). Usa Chart.js 4 y no necesita servidor.
**Estado real (2026-10-10):** Chart.js 4.5.1 se carga desde el CDN, así que el tablero web necesita
internet. Incrustarlo queda a decisión del usuario; desde el 2026-10-10 el tablero oficial es el de Excel.

**Tres pestañas:**

1. **Resumen de la campaña** (síntesis, cada fila con sus datos fijos)
   - Tarjetas KPI: corridas totales · % de puntos genuinos · KALINA confiables · datos del profesor
     conservables (8 de 10) · ventana de r_P (1.7–5.3).
   - Barras apiladas de clases por caso (FIG-G01 interactiva).
   - Matriz "qué se movió en cada barrido" (FIG-G02).
   - Escalera de M9 y tabla de datos del profesor conservables (TAB-G04).
2. **Explorador por bloque** (el corazón del tablero)
   - Filtros: **Bloque** → **Caso/subcaso** (solo los del bloque) → clases (casillas) → "solo
     confiables" → "solo W_net > 0".
   - **Los selectores de eje x/y ofrecen solo las variables que se barren en ese bloque** (se leen de
     `condiciones_por_subcaso.csv`). Así el tablero impide mezclar o graficar una variable fija: la
     regla del §3A queda implementada en la interfaz.
   - Panel **"Condiciones de este bloque"**, siempre visible: tabla de variables fijas con su valor
     (resaltadas las que difieren del profesor) y el pie generado automáticamente.
   - KPIs del bloque: corridas, genuinas, KALINA, KALINA confiables, η máx. KALINA y criterio que más bloquea.
   - Gráfico principal: dispersión x/y con color y forma por clase; los puntos fuera de rango van huecos.
   - Gráfico según el diseño: OAT → η contra la variable; LHS → histogramas de ΔP y r_P y CDF de
     KALINA contra el resto; malla 2D → mapa de clases.
   - Barras de criterios de bloqueo (O1, O2, O3, O5, convergencia).
   - Tabla de puntos ordenable y paginada (50 por página), exportable a CSV.
3. **Metodología y glosario**: punto genuino, N2, fuera de rango, O1–O5, banda de η, bloques y las
   fichas de cada caso enlazadas.

**Diseño:** encabezado oscuro con los filtros, tarjetas KPI, dos gráficos lado a lado y la tabla
abajo. Los colores de clase son los mismos de Matplotlib y del Excel. Tiene modo impresión y se
adapta a pantallas chicas.

### 4B.3 Tablero en Excel (hoja `Tablero` de `Excel_kalina_final_final_final.xlsx`)

Funciona sin macros y con funciones de Excel 2024 (las del Office instalado):
- Celda **Bloque** con lista desplegable (validación de datos) y celda **Caso** dependiente de ella.
- Tarjetas KPI hechas con `CONTAR.SI.CONJUNTO` / `MAX.SI.CONJUNTO` sobre la hoja `Datos` (la tabla
  canónica como Tabla de Excel con filtros).
- Bloque de **condiciones** con `FILTRAR` sobre la hoja `Condiciones`: cambia al elegir otro bloque.
- Gráficos nativos de Excel que se actualizan solos: barras de clases del bloque, barras de criterios
  de bloqueo y una dispersión de las **2 variables principales del bloque** (definidas por bloque en
  `bloques.csv`), alimentada por rangos auxiliares de tamaño fijo rellenos con `#N/A`.
- Limitación: `openpyxl` no crea segmentaciones (slicers) ni tablas dinámicas. Si se quieren, se
  agregan a mano en 2 minutos (A2 deja la Tabla lista para eso).
- La hoja `Tablero` usa solo fórmulas clásicas (INDEX/MATCH/IF/NA), sin `FILTRAR` ni macros: funciona
  en cualquier versión de Excel.

### 4B.4 Power BI (descartado; datos conservados por si acaso)

A1 deja los datos en **esquema estrella**, que es lo que Power BI importa directo:
`hechos_puntos.csv` (un punto por fila), `dim_caso.csv`, `dim_bloque.csv`, `dim_condiciones.csv`,
`dim_variable.csv` (nombre en español y unidad) y `dim_clase.csv` (color y orden). Con eso, más una
guía de 1 página con las medidas DAX básicas (conteos por clase y % KALINA), el usuario puede armar el
tablero en Power BI Desktop cuando lo instale. **No se hará:** el usuario decidió quedarse en Excel.

---

## 5. Metodología de sensibilidad aplicada (tarea 4) — síntesis

| Capa | Pregunta | Método | Casos | Qué entrega | Limitación |
|---|---|---|---|---|---|
| 0. Reproducibilidad | ¿El código da lo mismo que antes? | repetición punto a punto | M1 | clase antes/después | solo F1 |
| 1. Distancia al profesor | ¿Cuál es el cambio mínimo hacia KALINA? | mallas 1D/2D + bisección de fronteras por niveles (1→2→3 cambios) | M2, M2R, M2S | fronteras, A\*, d | huecos de malla; bisección ciega a lo que la malla no ve |
| 2. Local | ¿Qué variable mueve η y la clase cerca de A\*? | OAT 15 pts + elasticidad A\*±1 % + cruces de margen | M3, M10 | ranking \|E\|, Δη, zona KALINA, distancia a frontera | no ve interacciones |
| 3. Global | ¿Qué decide KALINA y en qué rango? | LHS + RSA/KS (principal), PAWN, PRCC, CART, bootstrap, convergencia ρ | M4, M4b, M4c | rangos p5–p95, ranking KS, reglas | unión de LHS no es LHS estricto; ρ KS < 0.9 en M4 (0.93 en 500) |
| 4. Conservación | ¿Qué datos del profesor se pueden mantener? | escenarios LHS + escalera forward + malla dirigida | M5, M5c, M9 | conjunto máximo conservable y rangos | 120 pts/escenario es exploración |
| 5. Optimización | ¿Cuánto η cabe en la región KALINA? | búsqueda por patrones desde varios arranques | M7 | η máx. por restricción | óptimos al filo de O1/O2 |
| 6. Verificación | ¿teqp = motor real? ¿margen de O2? | contraste puntual | M6 | paridad, costo del subenfriamiento | motor real necesita ~1500 s |
| 7. Caso real | ¿Se sostiene en Húsavík? | recorrida + OFAT + malla 2D | M10, M10b | reproducción 97/97, mapas XB×PB | un solo sitio |

Por qué no Morris/Sobol/FAST: no toleran puntos NO_CONVERGIO (ver `docs/ESTUDIO_METODOS_SENSIBILIDAD.md`).

---

## 6. Tablas para presentación (tarea 5)

### 6.1 Reglas de formato
- Estructura de encabezado, cuerpo y notas del §3A.5. Todo en español.
- Columnas: identificación → entradas **barridas** → salidas → banderas → comentario. Las entradas
  fijas **no** van como columnas repetidas; van en el encabezado de condiciones.
- Unidades en el encabezado (`P_baja [kPa]`); η en % con 2 decimales; presiones sin decimales
  (o 1 si < 1000); temperaturas con 1 decimal; ε/η/x_b con 3; índices (KS, PRCC, E) con 3.
- Orden de filas: por familia (R, F, L, G, C, O, V, H, X) y dentro por ID; en rankings, por magnitud descendente.
- Celda de clase coloreada como en el Excel; `fuera_rango` con † ; N2 con ‡.
- Cada tabla termina con una línea "Fuente: <csv> · n = … · filtro: …".

### 6.2 Tablas previstas

**Juego mínimo por caso.** Todos los casos tienen las mismas tres tablas, para que se lean igual:

| ID | Contenido |
|---|---|
| TAB-Mnn-00 | **Condiciones del caso:** cada variable con su estado (fija o barrida), su valor o rango, n de valores, si es igual al valor del profesor y su unidad. Sale de `condiciones_por_subcaso.csv` |
| TAB-Mnn-01 | **Conteo por clase:** corridas, genuinas, KALINA, KALINA confiables, corregibles, inviables, no convergidas, N2, fuera de rango y omitidas, por subcaso |
| TAB-Mnn-02… | **Resultado principal** del caso (ranking, fronteras, rangos, óptimos…), según su diseño |

**Tablas de síntesis** (cada fila es un caso con sus propios datos fijos; no se juntan puntos):

| ID | Contenido | Columnas | Orden | Criterio de inclusión |
|---|---|---|---|---|
| TAB-G01 | Resumen de casos | ID, nombre, familia, bloque, base, variables barridas, diseño, corridas, genuinas, KALINA, KALINA confiables, N2, criterio dominante | familia, ID | todos |
| TAB-G02 | Qué se modificó | caso × 11 variables + piso de O2 + rango de η/ε | familia, ID | todos |
| TAB-G03 | Rangos KALINA comparados | caso, bloque, **datos fijos**, variable, p5, mediana, p95, n | variable, caso | KALINA confiables |
| TAB-G04 | Datos del profesor conservables | dato, valor PP, ¿conservable?, condición, caso que lo respalda | orden del enunciado | M5, M5c, M9 |
| TAB-G05 | Criterios de bloqueo | caso × {O1, O2, O3, O5, convergencia} (n y %) | familia | genuinos no-KALINA |
| TAB-M03-01 | Ranking local | variable, rango, E, Δη (W_net>0), zona KALINA, falla al bajar/subir, distancia a frontera | \|E\| desc. | genuinos |
| TAB-M04-01 | RSA/PAWN/PRCC | variable, KS, p, rango favorable, PAWN, PRCC, signo | KS desc. | genuinos |
| TAB-M07-01 | Óptimos | arranque, restricción, η, clase, entradas, márgenes | η desc. | KALINA |
| TAB-M06-01 | Paridad | id, origen, clase teqp/real, η teqp/real, Δη, dentro de ±0.7 pp | id | — |

### 6.3 Libro nuevo `datos/Excel_kalina_final_final_final.xlsx`

Es un libro aparte. `Excel_final_kalina.xlsx` (81 hojas, con los datos crudos) no se toca. El libro
nuevo es para **presentar**: tiene las tablas y las figuras ya organizadas por bloque. Lo genera un
script (A2), nunca se edita a mano y conserva el formato de la casa (colores por clase, filtros,
unidades en los títulos, descripción al final).

| Orden | Hoja | Contenido |
|---|---|---|
| 1 | `LEEME` | Para qué es el libro, cómo leerlo, glosario (punto genuino, N2, fuera de rango, O1–O5, banda de η) y significado de los colores |
| 2 | `Tablero` | Tablero interactivo de Excel (§4B.3): se elige el bloque y cambian los KPIs, las condiciones y los gráficos |
| 2b | `Indice` | Una fila por hoja: nombre, caso, bloque, qué muestra y figura asociada (con hipervínculo) |
| 3 | `Punto_profesor` | Los 11 datos del profesor y el ancla A\* |
| 4 | `G01_resumen_casos` … `G05_bloqueos` | Tablas de síntesis TAB-G01…G05 |
| 5 | `Mnn_00_condiciones`, `Mnn_01_conteo`, `Mnn_02_<resultado>` … | Juego de tablas de cada caso, en el orden de los IDs. **Una hoja nunca junta dos bloques** |
| 6 | `Mnn_figuras` | Las figuras PNG del caso, cada una con su pie completo debajo |
| 7 | `X_M08_anecdotico` | Con una franja de aviso "ANECDÓTICO — fuera del rango realista" |
| 8 | `Datos`, `Condiciones`, `Bloques`, `Aux_tablero` | Al final: la tabla canónica y las condiciones (como Tablas de Excel con filtros) que alimentan el `Tablero`; `Aux_tablero` está oculta |

Cada hoja `Mnn_*` empieza con el mismo bloque de encabezado: título; caso y bloque; punto base;
datos fijos y barridos (bloque por bloque si la tabla abarca varios); filtro y fuente. La tabla
empieza tras una fila en blanco y las notas van al final.
Los nombres de hoja respetan el límite de 31 caracteres de Excel.

---

## 7. Organización de casos: clasificación, IDs y nomenclatura (tarea 6)

| Nivel | Patrón | Ejemplo |
|---|---|---|
| Campaña | `KF` (Kalina Final) | KF |
| Caso | `KF-M<nn>[<sufijo>]` (nn con 2 dígitos) | `KF-M04b`, `KF-M02R` |
| Subcaso | `<caso>-<etiqueta>` (nivel, ruta, base, escenario, arranque, ronda) | `KF-M02-N2-B`, `KF-M05-S4`, `KF-M02S-B3`, `KF-M07-A4`, `KF-M09-R3` |
| Punto | `<subcaso>-<nnnn>` (orden de la fila en el CSV de origen) | `KF-M03-0042` |
| Tabla | `TAB-<G|Mnn>-<nn>` | `TAB-M03-01` |
| Figura | `FIG-<G|Mnn>-<nn>_<descriptor>` | `FIG-M04-02_plano_presiones.png` |
| Ficha | `FICHA_<ID caso>.md` | `FICHA_KF-M03.md` |

Clasificación de cada caso en dos ejes: **familia** (R/F/L/G/C/O/V/H/X, §2.1) y **diseño**
(malla+bisección · OAT · LHS · malla 2D · escalera · búsqueda por patrones · verificación).
Los IDs `Mnn` son los mismos que ya usan los CSV, reportes, hojas del Excel y commits: no se renumera nada.

---

## 8. Reporte por caso (tarea 7)

Plantilla obligatoria (`analisis_final/04_fichas/PLANTILLA_FICHA.md`):

```
### ID del caso:
### Nombre del caso:
### Objetivo del barrido:
### ¿Qué se barrió?
### ¿Por qué se barrió?
### Datos o variables barridas:      (tabla: variable, rango [a, b], n valores, paso, unidad)
### Datos modificados:               (tabla: variable, valor PP → valor en la base del caso)
### Métodos aplicados:
### Resultados obtenidos:            (conteo por clase + tabla clave + 1–3 figuras)
### Conclusiones del caso:
### Advertencias, supuestos y limitaciones:
### Recomendaciones:
Fuentes: REPORTE_*.md, CSV, hoja(s) del Excel, commit.
```

Ficha piloto: `analisis_final/04_fichas/FICHA_KF-M03.md` (para validar el formato antes de escalar a 17).

---

## 9. Agentes y delegación a OpenCode

### 9.1 Reparto
Claude (director) diseña, redacta conclusiones y fichas, y audita. **Todo código** lo ejecuta OpenCode,
un `TASK_CONTEXT` por agente, cada uno en **su propio worktree** creado desde `test/barrido_final`
y con **su propia carpeta de salida**, de modo que no comparten archivos.

| Agente | Rol | Worktree / rama | Escribe solo en | Depende de | Modo |
|---|---|---|---|---|---|
| A1 Inventario y limpieza | apilar los CSV en la tabla canónica con columna `bloque`; banderas y derivadas; **detectar las variables fijas y barridas por subcaso** (`condiciones_por_subcaso.csv`); `nombres.py` y `pies.py`; conteos; esquema estrella para Power BI (§4B.4) | `.claude/worktrees/af-datos` · `analisis/datos` | `scripts/analisis_final/a1_*.py`, `nombres.py`, `pies.py`, `analisis_final/00_inventario/`, `01_datos/` | — | síncrono (primero) |
| A2 Tablas y libro | TAB-G01…G05 y el juego TAB-Mnn-00/01/02 en CSV + MD; después arma `Excel_kalina_final_final_final.xlsx` (§6.3) | `af-tablas` · `analisis/tablas` | `scripts/analisis_final/a2_*.py`, `02_tablas/`, `datos/Excel_kalina_final_final_final.xlsx` | A1 (y A3 para insertar las figuras) | paralelo con A3; el libro, al final |
| A3 Figuras | `estilo.py` + catálogo del §4, con títulos, recuadro de condiciones y pies del §3A.4 | `af-figuras` · `analisis/figuras` | `scripts/analisis_final/a3_*.py`, `estilo.py`, `03_figuras/` | A1 | paralelo con A2 |
| A4 Validación cruzada | recalcula cifras de los REPORTE_* y del §3.2 desde la tabla canónica; señala discrepancias | `af-validacion` · `analisis/validacion` | `scripts/analisis_final/a4_*.py`, `05_validacion/` | A1 | paralelo |
| A5 Tablero HTML | arma `tablero_kalina.html` (§4B.2) desde la tabla canónica y las condiciones | `af-tablero` · `analisis/tablero` | `scripts/analisis_final/a5_*.py`, `06_tablero/` | A1 (y A4 para las cifras de las tarjetas) | paralelo con A2/A3 |
| Claude | fichas, conclusiones, reporte final, BLUF, Obsidian | worktree `barrido-final` | `04_fichas/`, `REPORTE_ANALISIS_FINAL.md`, docs | A2–A4 | — |

Integración: Claude mergea las ramas `analisis/*` en `test/barrido_final` en orden A1 → A4 → A2 → A3
(no hay conflictos porque cada una toca carpetas distintas). Sin push ni PR sin preguntar.

### 9.2 Instrucciones fijas en cada TASK_CONTEXT (lecciones de la campaña)
- Definición de **punto genuino** y de **N2** literal (§1); OpenCode suele contar N2 como convergidos.
- Δη solo con W_net > 0.
- Usar solo las herramientas write/edit para crear archivos; nada de `&&` en PowerShell; `Tee-Object` para logs.
- Comando exacto a correr, en **primer plano**, con `timeout=7200000` en la herramienta de shell.
- `comun.py` no tiene helpers de CSV: leer con pandas, no inventar funciones.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`.
- Salida final en el formato STATUS/SUMMARY/… de `AGENTS.md`.

### 9.3 Validación de lo que entrega cada agente

| Agente | Prueba de aceptación |
|---|---|
| A1 | n filas de la tabla canónica = Σ filas de los CSV de origen; conteo por clase por caso igual al de la hoja `Resumen` del Excel y de cada REPORTE; 0 filas sin `id_caso` ni `bloque`; las condiciones detectadas coinciden con la tabla de bloques del §3A.1 (o se informa en qué difieren) |
| A2 | 3 cifras por tabla recalculadas por Claude contra el CSV; unidades en todos los encabezados; ninguna hoja `Mnn_*` mezcla bloques; el encabezado de condiciones de cada hoja coincide con `condiciones_por_subcaso.csv` |
| A3 | inspección visual de cada PNG; n en leyenda = n en tabla; colores por clase correctos; N2 en gris; todo en español; cada figura tiene su `.pie.md` con los datos fijos, los barridos, el filtro y la fuente |
| A4 | lista de discrepancias vacía o explicada; cada cifra del §3.2 con su ✔/✘ |
| A5 | Claude lo abre en el navegador integrado: sin errores en la consola; los KPIs de 3 bloques coinciden con TAB-Mnn-01; los selectores de eje no ofrecen variables fijas; el panel de condiciones coincide con TAB-Mnn-00; funciona sin internet |

---

## 10. Skills de datos: dónde entra cada una

| Paso | Skill | Qué aporta concretamente |
|---|---|---|
| Después de A1 | `data:explore-data` | Perfil de la tabla canónica: nulos por columna, rangos, duplicados, columnas constantes por subcaso. Sirve para confirmar los bloques del §3A.1 |
| Al diseñar figuras y tableros | `data:data-visualization` · `dataviz` | Elección del tipo de gráfico (§3A.3), forma + color por clase, títulos que dicen la conclusión, barras desde cero, paneles con la misma escala (§4.1) |
| Al diseñar el tablero | `data:build-dashboard` | Estructura de filtros → KPIs → gráficos → tabla; datos embebidos; tabla paginada; modo impresión (§4B.2) |
| Al revisar M4/M4b y los rangos | `data:statistical-analysis` | Lectura correcta de KS, valor p, PRCC, bootstrap y percentiles 5–95; qué diferencias son significativas y cuáles caen en la banda de η |
| Antes de entregar | `data:validate-data` | Auditoría de la metodología, los cálculos, los sesgos (por ejemplo, contar N2 como convergidos) y que cada conclusión esté respaldada; se cruza con A4 |
| Libro Excel | `anthropic-skills:xlsx` | Revisar fórmulas, validaciones y gráficos de la hoja `Tablero` |
| Resumen ejecutivo | `anthropic-skills:bluf` | BLUF para el profesor |
| Opcional | `anthropic-skills:apa7-riguroso` | Versión Word académica, si después se pide |

Las skills con los nombres "Data Analysis Pro", "Visualization Pro", "CSV Analysis", "Pandas Expert" o
"Data Storyteller" no forman parte del catálogo de Anthropic disponible en esta sesión; sus funciones
ya las cubren las de la tabla, así que no se instala nada. Las skills `data:sql-queries` /
`data:write-query` no aplican, porque no hay base de datos: todo son CSV.

---

---

## 11. Estructura de carpetas

```
analisis_final/
├── 00_inventario/      casos.csv · bloques.csv · condiciones_por_subcaso.csv · casos_x_variables.csv
│                       · diccionario_columnas.csv · fuentes.csv
├── 01_datos/           todos_los_puntos.csv (tabla canónica, con columna bloque) · LEEME.md
├── 02_tablas/          G/ (síntesis) · M01/ … M10b/  →  TAB-*.csv · TAB-*.md
├── 03_figuras/         G/ · M02/ … M10b/  →  FIG-*.png · FIG-*.svg · FIG-*.pie.md
├── 04_fichas/          PLANTILLA_FICHA.md · FICHA_KF-Mnn.md (17)
├── 05_validacion/      discrepancias.csv · checks_A1.md · checks_A4.md
├── 06_tablero/         tablero_kalina.html
├── 07_powerbi/         hechos_puntos.csv · dim_*.csv · GUIA_POWERBI.md (opcional)
├── REPORTE_ANALISIS_FINAL.md
└── BLUF_ANALISIS_FINAL.md
datos/                  Excel_kalina_final_final_final.xlsx (libro de presentación, §6.3)
scripts/analisis_final/ estilo.py · nombres.py · pies.py · a1_*.py … a5_*.py
prompts/                TASK_CONTEXT_af_A1_datos.md · …_A2_tablas.md · …_A3_figuras.md · …_A4_validacion.md · …_A5_tablero.md
```

Nombres: minúsculas con guion bajo en scripts y CSV; IDs en mayúsculas con guion; fechas ISO.

---

## 12. Plan de trabajo

| Paso | Qué | Quién | Autorización |
|---|---|---|---|
| 0 | Esta metodología + ficha piloto M3 + BLUF + nota Obsidian | Claude | hecho |
| 1 | TASK_CONTEXT A1 (tabla canónica, condiciones, bloques, esquema estrella) → corrida → auditoría con `data:explore-data` | Claude / OpenCode | **pedir antes de lanzar** |
| 2 | A3 (figuras) y A4 (validación) en paralelo, cada uno en su worktree → auditoría | Claude / OpenCode | pedir antes de lanzar |
| 3 | Corregir §3 y los títulos-conclusión con lo que diga A4 | Claude | — |
| 4 | A2 (tablas + libro Excel con hoja `Tablero`) y A5 (tablero HTML) en paralelo → revisión en el navegador y en Excel | Claude / OpenCode | pedir antes de lanzar |
| 5 | 16 fichas restantes (orden: C → G → F → L → H → O → V → R → X) | Claude | — |
| 6 | REPORTE_ANALISIS_FINAL.md + BLUF final + Obsidian; auditoría final con `data:validate-data` | Claude | — |
| 7 | Publicar el tablero HTML como enlace privado para el profesor | Claude | **pedir antes de publicar** |
| 8 | Merge de ramas `analisis/*` a `test/barrido_final` → master local | Claude | pedir antes de push/PR |
| — | ~~Tablero en Power BI~~ | — | descartado: todo queda en Excel |

## 13. Checklist de verificación

- [x] Σ filas tabla canónica = Σ filas CSV de origen (por caso)
- [x] Conteos por clase = hoja `Resumen` del Excel y REPORTE_* (o discrepancia explicada)
- [x] N2 contados como no genuinos en todas las tablas y figuras
- [x] Δη calculado solo con W_net > 0
- [x] `fuera_rango` señalado en tablas (†) y figuras (hueco)
- [x] Diferencias de η < 0.7 pp marcadas como no concluyentes
- [x] M8 marcado ANECDÓTICO y fuera de conclusiones
- [x] Cada cifra del §3 con fuente (CSV + fila/filtro)
- [x] Cada ficha con las 12 secciones de la plantilla
- [x] Unidades en todos los ejes y encabezados; todo en español
- [x] Ninguna figura ni tabla de caso mezcla bloques; en las de síntesis, cada fila lleva sus datos fijos
- [x] Ninguna variable fija aparece en un eje
- [x] Cada figura tiene título, recuadro de condiciones y pie con datos fijos, barridos, filtro, n y fuente
- [x] Cada hoja `Mnn_*` del libro nuevo abre con su encabezado de condiciones
- [x] `Excel_final_kalina.xlsx` sin cambios (comparar el hash antes y después)
- [x] Ningún archivo de `src/`, `app.py` ni `ui_*.py` modificado
- [x] [SUPUESTO] marcados y listados en el reporte final
- [x] Figuras legibles en blanco y negro (forma por clase); barras desde cero; paneles comparados con la misma escala
- [x] Tablero HTML: sin errores de consola (⚠ requiere internet para Chart.js), KPIs = TAB-Mnn-01, ejes solo con variables barridas
- [x] Hoja `Tablero` de Excel: la lista de bloques cambia los KPIs, las condiciones y los gráficos

## 14. Decisiones del usuario (rev. 3, 2026-10-10)
1. Todo en español: títulos, ejes, leyendas, pies y tablas.
2. Las tablas no van al Excel existente: se crea `datos/Excel_kalina_final_final_final.xlsx`.
3. La presentación no mezcla barridos con datos fijos distintos; cada figura y cada tabla dice bajo
   qué datos se obtuvo (§3A).
4. Se usan las skills de datos y se agregan tableros interactivos (§4B). Claude decide los detalles
   técnicos: tablero HTML principal + hoja `Tablero` en Excel + Power BI opcional. Los mismos datos
   también se presentan en Matplotlib.
5. Pendiente: que el usuario revise la ficha piloto `FICHA_KF-M03.md` antes de aprobar el formato.

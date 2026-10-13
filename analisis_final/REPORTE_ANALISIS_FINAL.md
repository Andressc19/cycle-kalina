# Reporte final del análisis de resultados — campaña final de barridos

> **Nomenclatura (2026-10-12).** Todo se numera como los capítulos de un informe: pregunta (1–6) → estudio (2.4) → parte (2.4a, cuando hay datos fijos distintos; reemplaza al antiguo "bloque"). Tablas y figuras siguen al estudio (Tabla 4.1-1, Figura 3.2-2); las de síntesis llevan S. Los números de sección de este documento llevan § para no confundirse con los estudios. Los códigos antiguos (M05, KF-M05-3, B09-3, TAB-M05-00) solo quedan como "código de origen".

| Pregunta | Estudios (código de origen) |
|---|---|
| 1 · ¿Funciona el ciclo con los datos del profesor? | **1.1** Repetir el caso del profesor (M01) |
| 2 · ¿Qué es lo mínimo que hay que cambiar para que funcione? | **2.1** Un solo cambio (M02-N1); **2.2** Dos cambios (M02-N2); **2.3** Dos cambios con η y ε en 0.40–0.95 (M02R); **2.4** Sumidero más frío (M02S) |
| 3 · ¿Qué variables importan y cuánto? | **3.1** Sensibilidad local alrededor de A* (M03); **3.2** Sensibilidad global (500 puntos) (M04, M04b); **3.3** P_baja alta (1500–2500 kPa) (M04c) |
| 4 · ¿Qué datos del profesor se pueden conservar? | **4.1** Escenarios de conservación (M05); **4.2** Mapa con las presiones del profesor (M05c); **4.3** Escalera de conservación (M09) |
| 5 · ¿Cuánta eficiencia se puede lograr? | **5.1** Búsqueda de la η máxima (M07) |
| 6 · ¿Son confiables los resultados? | **6.1** Verificación con el motor de referencia (M06); **6.2** Planta real de Húsavík (M10, M10b) |
| A · Anexo: equipos fuera del rango realista (no entra en las conclusiones) | **A.1** Equipos fuera del rango realista (M08) |

**Fecha:** 2026-10-10 · **Rama:** `test/barrido_final` · **Metodología:** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md`

## §1. La pregunta

Con los barridos ya terminados: ¿qué dicen los datos, organizados de modo que no se mezclen casos con
datos fijos distintos? Y ¿cómo se presentan al profesor con tablas, figuras y tableros que se entiendan solos?

## §2. Qué se hizo, en simple

1. **Una sola tabla con los 4 741 puntos** de la campaña, cada uno con su estudio y su **parte**.
   Una parte reúne los puntos que comparten las mismas variables fijas en los mismos valores. Las
   condiciones (qué quedó fijo y en qué valor, y qué se barrió) se **detectaron desde los datos**, no
   se escribieron a mano.
2. **Verificación cruzada de cifras:** se recalcularon desde esa tabla 78 cifras de los reportes. Coinciden 76;
   las 2 restantes eran diferencias de definición y quedaron corregidas.
3. **Productos de presentación** (todo en español):
   - 30 figuras Matplotlib, cada una con su título-conclusión, su recuadro de condiciones y su pie completo;
   - 62 tablas en CSV y Markdown;
   - un libro Excel nuevo con una hoja interactiva `Tablero`;
   - un tablero web interactivo;
   - los datos preparados para Power BI;
   - 16 fichas para los 17 casos (estudio 3.2 y estudio 3.2 comparten ficha porque son el misma parte).

### Cómo se ejecutó

Claude diseñó todo y lo auditó. El código lo empezó OpenCode con 5 agentes, cada uno en su propio
worktree (A1 datos, A2 tablas y Excel, A3 figuras, A4 validación, A5 tablero). A mitad de camino, el
modelo de OpenCode (big-pickle) dejó de responder. Un modelo alternativo gratuito (nemotron) se perdió
en las rutas y también se colgó. Con autorización del usuario, Claude terminó lo que faltaba, en los
mismos worktrees y con los mismos verificadores:
- 4 scripts de figuras y los arreglos de diseño de las figuras;
- la integración del tablero;
- el libro Excel.

Los vigilantes (skill `vigilante-tareas`) detectaron el cuelgue a los 10 minutos y comprobaron que
ningún archivo protegido se tocara: el `Excel_final_kalina.xlsx` original conserva su huella SHA-256.

## §3. Productos

| Producto | Ruta | Cómo se verificó |
|---|---|---|
| Tabla canónica y condiciones | `analisis_final/01_datos/`, `00_inventario/` | 4 741 filas = suma de las filas de los CSV de origen; 0 identificadores vacíos o repetidos |
| Verificación cruzada de cifras | `analisis_final/05_validacion/checks_A4.md` | 76 de 78 coinciden; 2 diferencias de definición explicadas |
| Fichas por caso | `analisis_final/04_fichas/` | 16 fichas (17 casos) con las 12 secciones de la plantilla, más un recuadro "Antes de leer" |
| Figuras | `analisis_final/03_figuras/` | 30 de 30 con PNG, SVG y pie; conteos de cada figura iguales a los de la verificación cruzada; revisión visual |
| Tablas | `analisis_final/02_tablas/` | 3 conteos al azar iguales a `conteo_por_subcaso`; ranking de estudio 3.1 igual al verificado |
| Libro Excel | `datos/Excel_kalina_final_final_final.xlsx` (95 hojas) | Tablero recalculado en Excel con 6 partes: cifras resumen correctas |
| Tablero web | `analisis_final/06_tablero/tablero_kalina.html` | Revisado en el navegador: sin errores, cifras resumen iguales a la verificación, gráficos visibles |
| Power BI | `analisis_final/07_powerbi/` + `GUIA_POWERBI.md` | Descartado por el usuario (todo queda en Excel); los CSV se conservan |

## §4. Conclusiones (cifras verificadas)

1. **El bloqueo del enunciado es la fuente a 623 K.** Con ella el punto del profesor no converge.
   Solo hay KALINA confiables alejándose mucho del resto del enunciado: x_b de 0.71 a 0.85, P_alta
   de 3200 a 5000 kPa y P_baja de 1.36 a 1.97 MPa.
2. **Bajando la fuente a ~390–410 K se conserva casi todo el enunciado**:
   - 8 de los 10 datos de diseño, con un sumidero de 280–293 K (estudio 4.3);
   - o las dos presiones del profesor, con ε_cond ≥ 0.875 en su clima de 300 K (estudio 4.2).
3. **La cavitación (O2) es el criterio que manda**: bloquea al 87–100 % de los puntos genuinos que no
   son KALINA en casi todos los casos (Tabla S-5). Darle un margen de 2 K cuesta solo 25–46 kPa más de
   P_baja (estudio 6.1).
4. **Ventana de presiones**: el 90 % de los KALINA tiene P_baja de 683 a 1461 kPa y r_P de 1.7 a 5.3
   (estudio 3.2). Un clima frío baja la P_baja necesaria (estudio 2.4); más amoníaco la sube (estudio 6.2).
5. **Eficiencia (secundaria)**: ~8–11 % con equipos de eficiencia media, y hasta 15.6 % con equipos
   a 0.95 conservando las presiones del profesor (estudio 5.1). Ese 15.6 % es el mejor aceptado de una
   búsqueda convergida (5.1d); 5.1a y 5.1b se detuvieron todavía subiendo y sus 15.0 y 15.5 % son cotas inferiores.
6. **El modelo está verificado y contrastado con modelos publicados; sin validación experimental disponible**:
   - reproduce el resultado del profesor (estudio 1.1), es decir, **reproduce el fallo** (todo NO_CONVERGIO), lo que no prueba que el modelo sea correcto; y reproduce los 97 KALINA de Húsavík (estudio 6.2), lo que contrasta qué rangos convergen, no una potencia medida;
   - coincide con el motor real en **5 puntos (4 diseños distintos): una muestra mínima**, los únicos que el motor real alcanzó a resolver (estudio 6.1 / estudio 4.3);
   - pasa la **verificación cruzada de cifras** de A4 (consistencia interna de las cifras, no validación física).

## §4b. Revisión de calidad (2026-10-10, segunda pasada)

Volví a revisar todo contra los objetivos. Encontré y corregí:

| Producto | Defecto encontrado | Corrección |
|---|---|---|
| Fichas | 5 fichas (estudio 4.1, estudio 5.1, estudio 4.3, estudio 6.2) juntaban "Datos barridos" y "Datos modificados" en una sola sección | Separadas, con tablas de rangos sacadas de `condiciones_por_subcaso.csv`; las 16 tienen las 12 secciones |
| Ficha estudio 2.3 | Describía mal la parte n2a, y en n2b omitía los KALINA con ε_HRVG = 0.50 | Corregida con los datos: n2a = ε_HRVG × ε_cond; n2b = KALINA con ε_HRVG 0.40–0.50 y P_baja 1318–2000 kPa (13 puntos distintos, todos fuera de rango) |
| Ficha estudio 6.2 | No advertía que 14 de los 97 puntos de la Fase 3 usan η_t hasta 0.98 o ε_cond hasta 0.99 | Advertencia agregada: los otros 83 tienen todas sus η y ε ≤ 0.95 |
| Figuras | El recuadro de condiciones tapaba datos (en M02R-n3 tapaba el único KALINA); leyendas sobre los puntos; tiras en diagonal que parecían tendencia; matriz G02 ilegible; escalera de estudio 4.3 sin rótulos | Recuadro debajo del eje, leyendas fuera, tiras por clase, matriz con alto proporcional y solo los valores relevantes, escalera rehecha |
| Excel, hoja Tablero | **Los 3 gráficos salían vacíos en Excel** (graficaban columnas ocultas); cifras resumen cortadas; pie truncado | Gráficos visibles (verificado en Excel: 1, 1 y 4 series), cifras en columnas propias, pie completo, colores de clase |
| Excel, tablas | Decimales sin redondear; nombres de columna inconsistentes; `criterio_bajo/alto` mal traducidos; hojas "G02_qué" | 5 cifras significativas; nombres unificados; `traducciones_columnas.csv` generado; hojas G con nombre claro |
| Tablero web | No marcaba con * los valores del punto base que difieren del profesor | Corregido (en estudio 3.1 marca solo T_fuente y P_baja) |
| Código | Funciones muertas en `a3_comun.py`; 2 scripts de más de 200 líneas | Eliminadas; todos los scripts ≤ 200 líneas |

## §4c. Revisión de calidad (2026-10-10, tercera pasada, hecha directamente por Claude)

Revisión punto por punto, sin OpenCode: cada cifra de las 16 fichas se recalculó con consultas
propias sobre `todos_los_puntos.csv`, y la tabla canónica se cotejó fila por fila con los 33 CSV de
origen (sin diferencias). Encontré y corregí:

| Producto | Defecto encontrado | Corrección |
|---|---|---|
| Figura G02 | **Las etiquetas de fila estaban invertidas**: la fila "1.1b" mostraba los datos de Húsavík | Etiquetas en el orden de la matriz; leyenda con "sin dato en la fuente"; menos espacio vacío |
| Encabezados de tablas y hojas del Excel | En los casos con varias partes (estudio 2.3, estudio 2.4, estudio 4.1, estudio 5.1, estudio 4.3, estudio 6.2) **juntaban las condiciones de todos las partes**; en Excel solo cabían 2 líneas y se veía únicamente el primer parte | Condiciones parte por parte (compactas en estudio 4.3); el Excel muestra todas las líneas; estudio 6.1 se presenta como puntos de control |
| Tablas de resultados | M06-02/03, M09-03, M10-02/03 y M10b-02 heredaban las partes de todo el caso | Cada tabla declara solo sus partes; filtro de Tabla 3.2-5 corregido (usa los 121 KALINA, no solo los confiables) |
| Pies y recuadros | En OAT contaban el valor base como un valor más (16 en vez de 15); símbolos crudos (`eta_t`, `eps_hrvg`) | Conteo desde `condiciones_oat.csv`; símbolos en español (η_t, ε_HRVG, piso de O2) en pies, tablas, títulos de panel y PRCC |
| Datos | 125 KALINA de M6-SUB marcados sin W_net > 0 (la fuente no trae W_net), así que el tablero web no graficaba su η | W_net > 0 se deduce de η > 0 cuando falta W_net |
| Tabla huérfana | Tabla 3.1-4 (volcado crudo de una corrida vieja de OpenCode) seguía en el registro y en el Excel | Retirada; quedan 62 tablas y 88 hojas |
| Fichas | estudio 2.1 contaba P_alta entre las variables que convergen (sus 13 "convergidos" son N2); estudio 6.2 omitía ε_HRVG (rompe en 0.95) y decía "todos confiables" sin matiz; estudio 5.1 y estudio 6.1 discrepaban en el costo de 2 K; estudio 6.2 apoyaba "no hay ciclo" en soluciones N2; estudio 3.1 conservaba avisos de "pendiente"; estudio 3.3, estudio 4.1 y estudio 4.2 tenían cifras aproximadas | Corregidas con cifras recalculadas |
| Metodología | [SUPUESTO] ya resueltos seguían abiertos (unidad de m_O2, Chart.js, FILTRAR) | Cerrados con lo verificado |
| Definición de "KALINA confiable" | Contaba como confiables 14 puntos F3 de Húsavík con η_t o ε_cond de 0.98–0.99, contra la regla del proyecto (η y ε ≤ 0.95) | Confiable exige además η y ε en [0.40, 0.95]: estudio 6.2 pasa de 253 a 239 confiables (F3: 83 de 97); el resto de los casos no cambia |
| Notas de las tablas | "n = 3" sin decir de qué | "n = 3 filas en la tabla" |
| BLUF del análisis | Recomendaba publicar el tablero web como principal | El tablero oficial es la hoja Tablero del Excel; verificado otra vez en Excel 2024 (estudios 3.2, parte 6.2a, estudio 4.2 y estudio 6.1: cifras correctas, 0 errores, gráficos con series) |

## §4d. Excel con gráficos nativos y cuadrícula (2026-10-11)

A pedido del usuario, el libro ya no pega las imágenes de Matplotlib en cada caso:
- **74 gráficos nativos de Excel** en 10 hojas `*_graficos`, que replican las 30 figuras con los mismos
  datos, parte, título y pie. Se verificaron abriendo el libro en Excel 2024 y exportando cada gráfico:
  los 74 tienen series y el número de puntos coincide con los datos (por ejemplo, la malla de Húsavík
  dibuja 118 puntos más los 12 de la línea de P_baja mínima).
- Las 30 figuras de Matplotlib quedan **una sola vez**, al final, en `Figuras_matplotlib_ref`; para el
  informe escrito siguen en `03_figuras/`.
- **Todas las tablas llevan cuadrícula.**
- Diferencias con Matplotlib: los paneles múltiples son gráficos pequeños en rejilla; las anotaciones
  (p. ej. "P08 = A4") van en el pie; la matriz G02 queda como tabla (hoja `G02_que_se_movio`).
- Código: `scripts/analisis_final/a2_graf_base.py`, `a2_graf_estilo.py`, `a2_graf_casos_a.py` y
  `a2_graf_casos_b.py`; el verificador `a2_verificar.py` comprueba las hojas de gráficos.

## §5. Lo que no se sabe

- Los muestreos LHS por escenario (estudio 4.1, estudio 4.3) son exploraciones. Las franjas angostas solo se mapearon
  con mallas dirigidas (estudio 4.2).
- En estudio 4.2 no se exploró T_fuente > 410 K: el borde superior de la franja no está medido.
- El motor real solo confirmó 5 puntos; los otros se cortaron por tiempo, no por la física.
- Las diferencias de η menores que 0.7 pp no son concluyentes.

## §6. Qué sigue

1. Que el usuario revise las fichas, las figuras, el Excel y el tablero, y diga qué corregir.
2. Borrar los worktrees temporales `af-*` (ya integrados). El tablero web queda como extra; el oficial es el Excel.
3. Llevar `test/barrido_final` a master local; push o PR solo si el usuario lo pide.
4. Opcional: un informe Word en APA 7 con las figuras y tablas. Power BI descartado: todo queda en Excel.

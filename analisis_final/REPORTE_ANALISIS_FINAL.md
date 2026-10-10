# Reporte final del análisis de resultados — campaña de barridos M1–M10b

**Fecha:** 2026-10-10 · **Rama:** `test/barrido_final` · **Metodología:** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md`

## 1. La pregunta

Con los barridos ya terminados: ¿qué dicen los datos, organizados de modo que no se mezclen casos con
datos fijos distintos? Y ¿cómo se presentan al profesor con tablas, figuras y tableros que se entiendan solos?

## 2. Qué se hizo, en simple

1. **Una sola tabla con los 4 741 puntos** de la campaña, cada uno con su caso, subcaso y **bloque**.
   Un bloque reúne los puntos que comparten las mismas variables fijas en los mismos valores. Las
   condiciones (qué quedó fijo y en qué valor, y qué se barrió) se **detectaron desde los datos**, no
   se escribieron a mano.
2. **Validación cruzada:** se recalcularon desde esa tabla 78 cifras de los reportes. Coinciden 76;
   las 2 restantes eran diferencias de definición y quedaron corregidas.
3. **Productos de presentación** (todo en español):
   - 30 figuras Matplotlib, cada una con su título-conclusión, su recuadro de condiciones y su pie completo;
   - 62 tablas en CSV y Markdown;
   - un libro Excel nuevo con una hoja interactiva `Tablero`;
   - un tablero web interactivo;
   - los datos preparados para Power BI;
   - 16 fichas para los 17 casos (M4 y M4b comparten ficha porque son el mismo bloque).

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

## 3. Productos

| Producto | Ruta | Cómo se verificó |
|---|---|---|
| Tabla canónica y condiciones | `analisis_final/01_datos/`, `00_inventario/` | 4 741 filas = suma de las filas de los CSV de origen; 0 identificadores vacíos o repetidos |
| Validación cruzada | `analisis_final/05_validacion/checks_A4.md` | 76 de 78 coinciden; 2 diferencias de definición explicadas |
| Fichas por caso | `analisis_final/04_fichas/` | 16 fichas (17 casos) con las 12 secciones de la plantilla, más un recuadro "Antes de leer" |
| Figuras | `analisis_final/03_figuras/` | 30 de 30 con PNG, SVG y pie; conteos de cada figura iguales a los de la validación; revisión visual |
| Tablas | `analisis_final/02_tablas/` | 3 conteos al azar iguales a `conteo_por_subcaso`; ranking de M3 igual al validado |
| Libro Excel | `datos/Excel_kalina_final_final_final.xlsx` (88 hojas) | Tablero recalculado en Excel con 6 bloques: cifras resumen correctas |
| Tablero web | `analisis_final/06_tablero/tablero_kalina.html` | Revisado en el navegador: sin errores, cifras resumen iguales a la verificación, gráficos visibles |
| Power BI | `analisis_final/07_powerbi/` + `GUIA_POWERBI.md` | Descartado por el usuario (todo queda en Excel); los CSV se conservan |

## 4. Conclusiones (validadas)

1. **El bloqueo del enunciado es la fuente a 623 K.** Con ella el punto del profesor no converge.
   Solo hay KALINA confiables alejándose mucho del resto del enunciado: x_b de 0.71 a 0.85, P_alta
   de 3200 a 5000 kPa y P_baja de 1.36 a 1.97 MPa.
2. **Bajando la fuente a ~390–410 K se conserva casi todo el enunciado**:
   - 8 de los 10 datos de diseño, con un sumidero de 280–293 K (M9);
   - o las dos presiones del profesor, con ε_cond ≥ 0.875 en su clima de 300 K (M5c).
3. **La cavitación (O2) es el criterio que manda**: bloquea al 87–100 % de los puntos genuinos que no
   son KALINA en casi todos los casos (TAB-G05). Darle un margen de 2 K cuesta solo 25–46 kPa más de
   P_baja (M6).
4. **Ventana de presiones**: el 90 % de los KALINA tiene P_baja de 683 a 1461 kPa y r_P de 1.7 a 5.3
   (M4/M4b). Un clima frío baja la P_baja necesaria (M2S); más amoníaco la sube (M10).
5. **Eficiencia (secundaria)**: ~8–11 % con equipos de eficiencia media, y hasta 15.6 % con equipos
   a 0.95 conservando las presiones del profesor (M7).
6. **El modelo está validado**:
   - reproduce el resultado del profesor (M1) y los 97 KALINA de Húsavík (M10);
   - coincide con el motor real en los 5 puntos que el motor real alcanzó a resolver (M6/M9);
   - pasa la validación cruzada de A4.

## 4b. Revisión de calidad (2026-10-10, segunda pasada)

Volví a revisar todo contra los objetivos. Encontré y corregí:

| Producto | Defecto encontrado | Corrección |
|---|---|---|
| Fichas | 5 fichas (M05, M07, M09, M10, M10b) juntaban "Datos barridos" y "Datos modificados" en una sola sección | Separadas, con tablas de rangos sacadas de `condiciones_por_subcaso.csv`; las 16 tienen las 12 secciones |
| Ficha M02R | Describía mal la parte n2a, y en n2b omitía los KALINA con ε_HRVG = 0.50 | Corregida con los datos: n2a = ε_HRVG × ε_cond; n2b = KALINA con ε_HRVG 0.40–0.50 y P_baja 1318–2000 kPa (13 puntos distintos, todos fuera de rango) |
| Ficha M10 | No advertía que 14 de los 97 puntos de la Fase 3 usan η_t hasta 0.98 o ε_cond hasta 0.99 | Advertencia agregada: los otros 83 tienen todas sus η y ε ≤ 0.95 |
| Figuras | El recuadro de condiciones tapaba datos (en M02R-n3 tapaba el único KALINA); leyendas sobre los puntos; tiras en diagonal que parecían tendencia; matriz G02 ilegible; escalera de M9 sin rótulos | Recuadro debajo del eje, leyendas fuera, tiras por clase, matriz con alto proporcional y solo los valores relevantes, escalera rehecha |
| Excel, hoja Tablero | **Los 3 gráficos salían vacíos en Excel** (graficaban columnas ocultas); cifras resumen cortadas; pie truncado | Gráficos visibles (verificado en Excel: 1, 1 y 4 series), cifras en columnas propias, pie completo, colores de clase |
| Excel, tablas | Decimales sin redondear; nombres de columna inconsistentes; `criterio_bajo/alto` mal traducidos; hojas "G02_qué" | 5 cifras significativas; nombres unificados; `traducciones_columnas.csv` generado; hojas G con nombre claro |
| Tablero web | No marcaba con * los valores del punto base que difieren del profesor | Corregido (en B06 marca solo T_fuente y P_baja) |
| Código | Funciones muertas en `a3_comun.py`; 2 scripts de más de 200 líneas | Eliminadas; todos los scripts ≤ 200 líneas |

## 4c. Revisión de calidad (2026-10-10, tercera pasada, hecha directamente por Claude)

Revisión punto por punto, sin OpenCode: cada cifra de las 16 fichas se recalculó con consultas
propias sobre `todos_los_puntos.csv`, y la tabla canónica se cotejó fila por fila con los 33 CSV de
origen (sin diferencias). Encontré y corregí:

| Producto | Defecto encontrado | Corrección |
|---|---|---|
| Figura G02 | **Las etiquetas de fila estaban invertidas**: la fila "KF-M01-P_alta" mostraba los datos de Húsavík | Etiquetas en el orden de la matriz; leyenda con "sin dato en la fuente"; menos espacio vacío |
| Encabezados de tablas y hojas del Excel | En los casos con varios bloques (M02R, M02S, M05, M07, M09, M10, M10b) **juntaban las condiciones de todos los bloques**; en Excel solo cabían 2 líneas y se veía únicamente el primer bloque | Condiciones bloque por bloque (compactas en M09); el Excel muestra todas las líneas; M06 se presenta como puntos de control |
| Tablas de resultados | M06-02/03, M09-03, M10-02/03 y M10b-02 heredaban los subcasos de todo el caso | Cada tabla declara solo sus subcasos; filtro de TAB-M04-04 corregido (usa los 121 KALINA, no solo los confiables) |
| Pies y recuadros | En OAT contaban el valor base como un valor más (16 en vez de 15); símbolos crudos (`eta_t`, `eps_hrvg`) | Conteo desde `condiciones_oat.csv`; símbolos en español (η_t, ε_HRVG, piso de O2) en pies, tablas, títulos de panel y PRCC |
| Datos | 125 KALINA de M6-SUB marcados sin W_net > 0 (la fuente no trae W_net), así que el tablero web no graficaba su η | W_net > 0 se deduce de η > 0 cuando falta W_net |
| Tabla huérfana | TAB-M03-03 (volcado crudo de una corrida vieja de OpenCode) seguía en el registro y en el Excel | Retirada; quedan 62 tablas y 88 hojas |
| Fichas | M02-N1 contaba P_alta entre las variables que convergen (sus 13 "convergidos" son N2); M10 omitía ε_HRVG (rompe en 0.95) y decía "todos confiables" sin matiz; M07 y M06 discrepaban en el costo de 2 K; M10b apoyaba "no hay ciclo" en soluciones N2; M03 conservaba avisos de "pendiente"; M04c, M05 y M05c tenían cifras aproximadas | Corregidas con cifras recalculadas |
| Metodología | [SUPUESTO] ya resueltos seguían abiertos (unidad de m_O2, Chart.js, FILTRAR) | Cerrados con lo verificado |

## 5. Lo que no se sabe

- Los muestreos LHS por escenario (M5, M9) son exploraciones. Las franjas angostas solo se mapearon
  con mallas dirigidas (M5c).
- En M5c no se exploró T_fuente > 410 K: el borde superior de la franja no está medido.
- El motor real solo confirmó 5 puntos; los otros se cortaron por tiempo, no por la física.
- Las diferencias de η menores que 0.7 pp no son concluyentes.

## 6. Qué sigue

1. Que el usuario revise las fichas, las figuras, el Excel y el tablero, y diga qué corregir.
2. Decidir si el tablero web se publica como enlace privado para el profesor.
3. Llevar `test/barrido_final` a master local; push o PR solo si el usuario lo pide.
4. Opcional: un informe Word en APA 7 con las figuras y tablas. Power BI descartado: todo queda en Excel.

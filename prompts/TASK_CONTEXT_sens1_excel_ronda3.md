# TASK_CONTEXT — Excel Sensibilidad 1: incorporar la Ronda 3 (estudios 14, 15 y 16) y cerrar los 2 defectos pendientes

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa desde aquí):** `..\..\..\.venv\Scripts\python.exe`
**Código existente:** `scripts/sens1/x1_cargar.py` … `x8_verificar.py`, `x5b/x5c`, `x8b`, `x9*` si existen,
`conclusiones.py`. El libro `datos/Kalina_anal_sensible_1.xlsx` ya tiene 26 hojas, 31 gráficos, S1–S5, `E12`
(regenerador y turbina) y `E13` (preselección de equipos); el director lo verificó contra los CSV de forma
independiente. **No cambies lo que ya está bien.**

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal** (el sandbox las rechaza y aborta toda la
  ejecución). Usa rutas relativas e intérprete `..\..\..\.venv\Scripts\python.exe`.
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`. `timeout=1800000` en la shell.
  **NO ejecutes `pytest`.** El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, ningún CSV de `resultados/`,
  ni otros libros. Cada `.py`: máximo 200 líneas (divide en módulos nuevos si hace falta).
- Reglas de formato vigentes: gráficos nativos con datos visibles junto a su tabla, cuadrícula, sin freeze
  panes, español, unidades, nada de abreviaturas de dos letras, **terminología «KALINA (total) / dentro del
  rango experimental / fuera del rango experimental (líquido > 420 K)»**, sin «confiable», «fuera de
  rango», «sin respaldo», «no citable», «indicio», «extrapol».
- Todo número del libro se calcula desde los CSV; los textos de conclusión de abajo se escriben tal cual
  y cada cifra se verifica en `x8` contra los datos (si una no coincide, repórtalo y no la publiques).

## Parte 1 — Tres estudios nuevos (cada uno con hoja de resumen, hoja de datos y gráficos)

Numeración: los estudios 12 y 13 ya existen como hojas de análisis (`E12 Regenerador y turbina`,
`E13 Preseleccion de equipos`). Los nuevos son **14, 15 y 16** y sus hojas van **al final** del libro:

| Estudio | Hojas | Datos | Filtro |
|---|---|---|---|
| 14 · LHS de 9 variables en centros caliente y frío | `E14 LHS C3 y C4`, `E14 Datos LHS C3 C4` | `resultados/2026-10-16_sens1_ronda3/ronda3_filas.csv` | `barrido == "N8"` (465 filas: C3 234, C4 231) |
| 15 · Pares del regenerador y la turbina (C3, C4) | `E15 Pares regenerador`, `E15 Datos Pares` | idem | `barrido == "N9"` (194 filas) |
| 16 · P_alta de 4000 a 8000 kPa (C1, C3, C4) | `E16 P_alta alta`, `E16 Datos P_alta` | idem | `barrido == "N10"` (105 filas) |

Regístralos en `ESTUDIOS` de `x1_cargar.py`. **Todas las tablas de síntesis (S1 a S5), `E12`, `E13` y
`LEEME` deben leer del registro y por tanto incluirlos** (S1 pasa a 15 filas, estudios 0–11 y 14–16; S4 y S5
también). Las hojas de datos tienen el mismo formato y columnas que las demás.

**Contenido de cada hoja de resumen** (tablas con gráfico nativo al lado, y encabezado de condiciones):

- **E14:** (a) clases por centro (KALINA total, dentro, fuera, CORREGIBLE, NO_CONVERGIO, INVIABLE; Total
  debe sumar 234 y 231); (b) ventanas p10 / mediana / p90 de las 9 variables entre los KALINA (total) por
  centro; (c) PRCC con η entre los KALINA y estadístico KS de cada variable, por centro (calcúlalos con
  numpy y `scipy.stats.ks_2samp` como en `scripts/sens1/ronda3_reporte3.py`); (d) tabla de causas de los
  NO_CONVERGIO (agrupa el mensaje: «sin dos extremos evaluables de T1», «balance global de energía no
  cierra», «sin cambio de signo de F», «punto interior no evaluable», `PropertyRangeError` del motor,
  «tiempo agotado», otros) por centro. Gráficos: clases apiladas por centro; barras del |PRCC| por
  variable y centro; barras de las causas de NO_CONVERGIO.
- **E15:** nº de KALINA por par (B5 ε_reg × η_t; B6 ε_HRVG × T_fuente) y centro **contando el punto base**
  (esperado: C3 49 y 49, C4 49 y 39), η máxima por par y matrices 7 × 7 de clase y de η (%) por centro y
  par. Gráfico: barras de KALINA por par y centro; barras de η máxima por par y centro.
- **E16:** matriz 5 × 7 de clase y de η (%) por centro (P_alta × P_baja); η máxima por P_alta y centro;
  P_alta óptimo por centro. Gráfico: líneas de η máxima frente a P_alta, una línea por centro; barras de
  KALINA por P_alta y centro.

## Parte 2 — Dos defectos pendientes (verificados por el director)

**D5. `E12` omite el valor base en sus dos primeras tablas.** La tabla «Regenerador frente a ε_reg» no
tiene la fila 0.75 y la de «Turbina frente a η_t» no tiene la fila 0.85, porque el punto base (variable
`base`) no se cuenta en el barrido de su variable. Inclúyelo (cada centro tiene su base: ε_reg 0.75, η_t
0.85). Así cada tabla tiene 12 filas (0.40–0.95 paso 0.05).

**D6. `E13 §3` («Efectividad mínima por equipo») está incompleta.** Hoy deja en blanco la ε_cond mínima de
C2, C3 y C4 y trae una fila «Sin centro (muestreo o malla)» sin sentido. Recalcula **por centro** (C1, C2,
C3, C4), con los barridos de una variable y de pares de ese centro, más el estudio 5 para C1: ε_cond
mínima con KALINA (total) y la P_baja del punto que la logra; ε_reg, ε_HRVG y η_t mínimas con KALINA (total).
Elimina la fila «Sin centro». Valores esperados de la ε_cond mínima (verifica): C1 0.85 (a 1250 kPa, clima
10 °C); C2 0.65 o 0.80 (según el barrido que la logre: calcúlalo y di cuál); C3 0.65 u otro valor; C4
0.60 u otro valor: calcula y no supongas.

## Parte 3 — Textos (escríbelos en `conclusiones.py`; cifras ya verificadas por el director)

**Apéndice A, estudio 14.** «Muestreo LHS de 9 variables (semilla 20261017, redondeo 0.5 K / 10 kPa / 0.01 /
0.05) en C3 y C4: 465 puntos (234 y 231) tras descartar 35 con P_alta < 1.3 × P_baja. KALINA (total): C3
121 (93 dentro del rango experimental, 28 fuera) y C4 137 (todos dentro). η máxima entre los KALINA: C3
12.1 % y C4 11.2 %. La η crece con x_b (PRCC +0.70 y +0.61) y decrece con P_baja (PRCC −0.72 y −0.68); en C3
también con η_t (+0.63) y en C4 con P_alta (+0.60). La variable que más separa KALINA del resto es P_baja
(KS 0.48 y 0.41), seguida de x_b (0.38 y 0.29). Los NO_CONVERGIO (54 y 57) se concentran en fuente de 60 a
115 °C con P_alta mayor de 2500 kPa: la fuente no alcanza para llevar el fluido a esa presión.»

**Apéndice A, estudio 15.** «Pares del regenerador y la turbina en C3 y C4 (mallas 7 × 7 con el base): ε_reg
× η_t mantiene KALINA en las 49 combinaciones de ambos centros (η máxima 10.9 % en C3 y 13.0 % en C4);
ε_HRVG × T_fuente da 49 de 49 en C3 (η máxima 9.5 %; 11 puntos fuera del rango experimental) y 39 de 49 en
C4 (η máxima 12.3 %). Con los estudios 2 y 11, el regenerador y la turbina no sacan al ciclo de KALINA en
0.50–0.95 en ninguno de los cuatro centros.»

**Apéndice A, estudio 16.** «P_alta de 4000 a 8000 kPa: la η máxima tiene un máximo interior. C1: 14.0 %
a 5000 kPa (converge hasta 6000; con 7000 y 8000 todos NO_CONVERGIO). C3: 14.5 % a 6000 kPa con P_baja
650 kPa (converge hasta 8000, donde la η cae a 7.4 %). C4: 12.2 % a 4000 kPa (sin KALINA a 6000; con 7000 y
8000 todos NO_CONVERGIO). Los 47 KALINA del estudio están dentro del rango experimental.»

**Apéndice B (consolidada).** Sustituye el punto 4 por: «Presiones: la P_baja mínima sube ~100 kPa por cada
+5 K de clima y con la T_fuente. P_alta tiene mucho margen (desde 1000 kPa hay KALINA en C1; en C2 casi no
influye) y la η tiene un máximo interior: ~5000 kPa en Húsavík, ~6000 kPa con fuente de 150 °C y ~4000 kPa
con fuente de 110 °C; por encima, el ciclo deja de converger.» Sustituye el punto 5 por: «Eficiencia
alcanzable: la η máxima del conjunto es [CALCULAR desde los datos: valor, centro y punto] (esperado 14.5 %,
C3, P_alta 6000 kPa); con fuente de ~150 °C, clima de 5–10 °C y equipos de 0.85–0.95 se logran 13–14.5 %; con
equipos de 0.70, ~9 %.» Añade el punto 8: «Lo que más mueve la η al variar todo a la vez son P_baja
(decreciente) y x_b (creciente) (estudios 3 y 14).» Mantén el resto.

## Parte 4 — Verificación (endurece `x8_verificar.py`; no quites los controles anteriores)

14. Filas de las hojas de datos nuevas: 465, 194 y 105; ids únicos; igual que su CSV filtrado.
15. S1 incluye los estudios 14–16 (15 filas); Total = suma de las 4 clases = puntos del estudio.
16. Totales por clase de los estudios nuevos: 14 → C3 KALINA 121 (93 dentro, 28 fuera) y C4 137 (137
    dentro), NO_CONVERGIO 54 y 57; 15 → C3 B5 49 y B6 49, C4 B5 49 y B6 39; 16 → KALINA C1 14, C3 24, C4 9.
17. `E12`: las tablas de ε_reg y de η_t tienen 12 filas e incluyen 0.75 y 0.85.
18. `E13 §3`: sin celdas vacías de ε_cond mínima en ninguno de los 4 centros y sin fila «Sin centro».
19. Que el libro tenga ≥ 40 gráficos, todos con series y valores numéricos, y sin solapes.
Los controles 1–13 siguen en OK.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

No des `done` con algún control en FALLA. Reporte en el formato de `AGENTS.md`; en RESULTS: salida completa
de `x8_verificar.py` (sin la lista larga de gráficos), nº de hojas y de gráficos, y la ε_cond mínima por
centro calculada.

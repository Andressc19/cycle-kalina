# TASK_CONTEXT — Sensibilidad 2, P5b: libro `Kalina_anal_sensible_2.xlsx` (parte 2: correcciones, Fase B y equipos)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe` (openpyxl, numpy, pandas).
**Continúa** `prompts/TASK_CONTEXT_sens2_P5a.md` (léelo: formato, arquitectura y terminología son los mismos) y el
código ya escrito en `scripts/sens2/s2_*.py`. Reutiliza `scripts/sens1/x2_formato.py` y `x5_graficos.py`. No
modifiques `scripts/sens1/`. Sin corridas del motor.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- Archivos SOLO con `write` y `edit` (nada de `cat <<`, here-strings, `Set-Content`, `python -c` ni here-docs que
  escriban archivos). PowerShell 5.1, sin `&&`. Solo ASCII en los `print`. `timeout=1800000`. **NO `pytest`.**
- Cada `.py` máximo 200 líneas. El libro `datos/Kalina_anal_sensible_2.xlsx` no debe estar abierto en Excel.
- Terminología prohibida y regla «todo número sale de un CSV»: como en P5a. Los gráficos son nativos, junto a su
  tabla (columna L), gráfico = tabla, sin vacíos, sin solapes.

## Parte 1 — Correcciones al libro actual (el director encontró 2 problemas)

1. **BLUF de `Conclusion consolidada` (fila «eta maxima dentro / fuera del rango experimental»)** muestra
   17.37 / 18.68: es un error, calcula el máximo de **todas** las clases. Debe calcularse **solo sobre KALINA (total)
   con η válida** (`kalina == True`): el resultado correcto es **14.53 dentro / 14.82 fuera** del rango experimental.
   Corrige `scripts/sens2/s2_conclusion.py` (aplica el filtro `kalina` antes de calcular).
2. **El control 7 de `s2_verificar.py` pasó con el error porque repetía la misma fórmula.** Reescríbelo para que
   calcule cada cifra del BLUF de forma independiente (p. ej. `max` de `eta_pct` con `kalina` y `fuera_rango` en el
   CSV) y añade un control cruzado: la η máxima de BLUF debe coincidir con la que cita la conclusión **M1** de
   `p5_conclusiones.csv` (14.82 y 14.53). Revisa también que `% KALINA` es KALINA/puntos del CSV deduplicado y que el
   `% de CORREGIBLE por cavitación` sea el dominante O2 entre CORREGIBLE.
3. **Aviso de base de datos.** F1 usa los 3 921 puntos de P1 (con duplicados) y F2, F3 y F4 usan los 3 663 sin
   duplicados con η válida; por eso los n difieren (p. ej. C1: 502 KALINA en F1 y 454 en F2). Añade esta nota a
   `LEEME`, y en el bloque «Condiciones» de cada hoja F1 a F4 la línea «Base: N puntos (con/sin duplicados)».

## Parte 2 — Hojas nuevas (módulos `s2_f3.py`, `s2_f3b.py`, `s2_f4.py`, `s2_f4b.py`; registra en `HOJAS`)

Entradas: `resultados/2026-10-17_sens2_P3/` y `.../P4/` (CSV). Orden de las hojas nuevas: después de `F2 Distancia y
rescate` y antes de las de datos.

1. **`F3 Indices globales`** (`p3_ranking.csv`, `p3_indices.csv`): explicación llana de los índices (PRCC, KS,
   PAWN, δ, HSIC, η², logística; el piso de ruido de las 3 variables dummy). Por bloque (C1–C4) y respuesta
   (Y1 KALINA, Y2 η, Y3 W_net/m_b, Y4 D): tabla de las 9 variables con rango medio, signo y marca «distinguible del
   ruido», y **un gráfico de barras horizontales del rango medio (invertido: más alto = más importante) por bloque
   para Y1, Y2 y Y3 (12 gráficos)**; usa para la barra una cantidad que crezca con la importancia (p. ej.
   `10 − rango medio`) rotulada «Importancia (10 − rango medio)». Tabla de coincidencias y discrepancias entre métodos.
2. **`F3 Interacciones`** (`p3_interaccion.csv`): tabla de pares × bloque con 1 − R² para η y para el indicador
   KALINA, clasificación (aditivo / sinérgico / antagónico / fuerte), n de celdas; gráfico de barras agrupadas del
   1 − R² del indicador KALINA por par y bloque, y otro para η. Matrices 7×7 de η y de KALINA para los dos pares más
   fuertes de cada bloque (cuentas por pertenencia a la malla, ya calculadas en el CSV de P3 si están; si no, dilo).
3. **`F3 Elasticidades`** (`p3_elasticidad.csv`): tabla variable × bloque (con tipo de diferencia), gráfico de barras
   agrupadas por bloque, y la nota sobre la elasticidad de T_fuente en C2 (rampa de la frontera) y sobre los dos
   estudios usados.
4. **`F4 Turbina`** (`p4_envolventes.csv`, `p4_bandas.csv`, `p4_dependencias.csv`): tabla P5/mediana/P95 de r_P, Δh,
   W_t, q4, T3, T4, m_v por bloque (KALINA total y 10 % de mayor η) con gráfico de barras de r_P y Δh del 10 % de
   mayor η frente a todo KALINA; **tabla de bandas de r_P** con η y Δh medianas + gráfico de línea (η y Δh frente a la
   banda); regresión Δh~r_P por bloque (pendiente, R²) + gráfico; asociaciones más fuertes de cada cantidad de
   turbina con las entradas.
5. **`F4 Regenerador y condensador`** (los mismos CSV y `p4_restricciones.csv`): pinch, LMTD, UA, Q_reg/Q_i del
   regenerador; Q_out, acercamientos del condensador; Q_i, T_fuente − T3 del HRVG; W_p/W_t de la bomba, todas por
   bloque (P5/mediana/P95) con un gráfico de barras para pinch y otro para UA; tabla de restricciones activas
   (KALINA frente a CORREGIBLE: q4 < 0.90, cruces, T9 − T_sumidero) + gráfico; las asociaciones que fijan cada
   cantidad. Notas de los límites (LMTD reconstruido, contraflujo puro, los acercamientos no son pinch de diseño).
6. **`F4 Preseleccion`**: tabla llana «qué debe cubrir cada equipo» tomada de `p4_resumen.md`/CSV (rango a cubrir
   para todo KALINA y para el 10 % de mayor η; variable que lo fija; restricción activa), con las referencias de la
   Etapa 0 (`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md` §5: turbina radial para EPR < 10, título ≥ 0.90,
   pinch 4–5 K, etc.; cada referencia lleva su número de fuente) y un gráfico de barras con el nº de requisitos
   por equipo. Más: tabla de **límites de la preselección** (de `p4_resumen.md`).
7. **Hojas de datos nuevas**: `D5 Datos indices` (`p3_indices.csv`) y `D6 Datos equipos` (`p4_bandas.csv` o el CSV
   más completo de P4 que se pueda mostrar como tabla plana).
8. Actualiza `LEEME` (la guía de hojas ya las nombra: ajusta los nombres si cambiaste alguno).

## Verificación (amplía `s2_verificar.py`; mantén los controles anteriores)

Los de P5a (con el 7 reescrito) y: (10) mínimo 40 gráficos en total y todos con series numéricas; (11) cada tabla
de ranking por bloque tiene las 9 variables; (12) las cifras de `F4 Preseleccion` coinciden con `p4_envolventes.csv`
(compara 3 cifras por equipo, calculadas desde el CSV); (13) `D5` tiene tantas filas como `p3_indices.csv`;
(14) la nota de base aparece en `LEEME` y en F1 a F4; (15) sin palabras prohibidas, sin celdas vacías en tablas de
gráfico, sin solapes. No des `done` con ningún control en FALLA.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\s2_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens2\s2_verificar.py
```

Reporte en el formato de `AGENTS.md`; en RESULTS: lista de hojas con su nº de gráficos, la fila BLUF de la η máxima
tal como quedó en el libro y la salida de `s2_verificar.py` (sin la lista larga de gráficos).

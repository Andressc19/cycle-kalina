# TASK_CONTEXT — Excel Sensibilidad 1: corrección del piso del condensador, etiquetas de matrices y puntos atípicos

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa desde aquí):** `..\..\..\.venv\Scripts\python.exe`
**Contexto:** el libro `datos/Kalina_anal_sensible_1.xlsx` (34 hojas, 41 gráficos) pasa sus 19 controles, pero
la verificación independiente del director encontró 3 problemas que `x8` no detecta. Esta tarea los corrige.
**No cambies lo que ya está bien.**

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d`, `cd ..` ni rutas absolutas en la terminal** (el sandbox las rechaza y aborta toda
  la ejecución). Usa rutas relativas e intérprete `..\..\..\.venv\Scripts\python.exe`.
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`. `timeout=1800000`. **NO ejecutes `pytest`.**
  El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, ningún CSV de `resultados/`, ni otros
  libros. Cada `.py`: máximo 200 líneas (divide en módulos nuevos si hace falta).
- Reglas de formato vigentes (gráficos nativos con datos visibles junto a su tabla, cuadrícula, sin freeze panes,
  español, terminología «KALINA (total) / dentro / fuera del rango experimental»; nada de «confiable», «fuera de
  rango», «sin respaldo», «no citable», «indicio», «extrapol»).
- Todo número del libro se calcula desde los CSV.

## Problema 1 (el más importante): el piso del condensador depende de x_b

El libro dice en la conclusión consolidada (punto 2) y en el estudio 5 que «con ε_cond < 0.85 no hay KALINA».
Eso solo vale para la configuración de Húsavík del estudio 5 (x_b 0.82). Con **todos** los estudios juntos, la
ε_cond mínima con KALINA (total) depende de x_b (calculado por el director):

| Banda de x_b | ε_cond mínima con KALINA | Puntos KALINA |
|---|---|---|
| 0.30–0.45 | 0.70 | 113 |
| 0.45–0.55 | 0.65 | 461 |
| 0.55–0.65 | 0.75 | 207 |
| 0.65–0.75 | 0.80 | 685 |
| 0.75–0.85 | 0.85 | 434 |
| 0.85–0.95 | 0.85 | 342 |

Y por centro, sobre todos los estudios: C1 **0.80** (estudio 3, P_baja 520 kPa), C2 **0.65** (estudio 2, P_baja
563.64), C3 **0.85** (estudio 14, P_baja 570), C4 **0.85** (estudio 14, P_baja 760).

**Correcciones:**
1. **`E13 §3`**: calcula la ε_cond mínima por centro sobre **todos** los estudios (no solo los de una
   variable y de pares), con el estudio y la P_baja del punto que la logra; mantén ε_reg, ε_HRVG y η_t mínimas.
   Valores esperados: los de arriba (verifica contra los datos; si difieren, reporta).
2. **Tabla nueva en `E13`** (sección 4) y en `Conclusion consolidada` dentro de **S3 (c)**: «ε_cond mínima con
   KALINA por banda de x_b» (las 6 bandas de arriba, calculadas desde los datos: ε_cond mínima, nº de puntos
   KALINA y P_baja mediana). Con gráfico nativo de barras de la ε_cond mínima por banda, junto a la tabla.
3. **Textos** (en `conclusiones.py`):
   - **Estudio 5:** «Con ε_cond < 0.85 no hay KALINA en ningún clima probado» pasa a: «En la configuración de
     Húsavík (x_b 0.82, P_alta 3300 kPa, fuente 121 °C) no hay KALINA con ε_cond < 0.85 en ningún clima
     probado.» (el resto del texto de ese estudio no cambia).
   - **Apéndice B, punto 2:** «El condensador manda, y su piso depende de la composición. La ε_cond mínima
     con KALINA sube con x_b: 0.65–0.70 con x_b 0.30–0.55, 0.75 con 0.55–0.65, 0.80 con 0.65–0.75 y 0.85 con
     x_b mayor de 0.75 (todos los estudios). En Húsavík (x_b 0.82) cada −0.05 de ε_cond cuesta +250 a +300 kPa
     de P_baja y un clima cálido exige la efectividad máxima.»
   - Cualquier otra frase del libro que generalice «ε_cond < 0.85 no hay KALINA» (revisa `LEEME`, S3 y las
     hojas E5 y E13) se acota igual: «en la configuración de Húsavík».

## Problema 2: matrices sin rótulo de ejes

En `E15` y `E16` las matrices 7×7 y 5×7 rotulan solo las filas; no dicen qué variable corre por columnas.
Cambia la celda de esquina de cada matriz por un rótulo de dos ejes, por ejemplo
«filas: ε_reg (-) · columnas: η_t (-)» (E15 B5), «filas: ε_HRVG (-) · columnas: T_fuente (°C)» (E15 B6),
«filas: P_alta (kPa) · columnas: P_baja (kPa)» (E16). Revisa también `E2`, `E11`, `E5`, `E8` y `E9` si tienen
matrices con el mismo problema.

## Problema 3: puntos atípicos señalados

Entre los 1 780 KALINA con η_t ≥ 0.8 hay 7 con una caída de entalpía de turbina anormalmente baja respecto de
su banda de r_P. Regla (calcúlala desde los datos, sobre los estudios 1–11 y 14–16): KALINA (total) con
η_t ≥ 0.8 y `dh_turb` < 0.6 × la mediana de `dh_turb` de los KALINA de su banda de r_P = P_alta/P_baja (bandas
[1, 1.5), [1.5, 2), [2, 3), [3, 4), [4, 6), [6, 10]). El director encontró 7: `C1-B6-0236`, `N1-T090-10`,
`N7A-C3-P_alta-001`, `N7A-C4-P_alta-001`, `N7A-C4-eps_hrvg-003`, `N9-C4-B6-0004`, `N8-C4-0141`. El más claro es
`N9-C4-B6-0004` (idéntico a `N7A-C4-eps_hrvg-003`): C4, ε_HRVG 0.50, fuente 110 °C, η 1.6 % con Δh de turbina
40 kJ/kg frente a ~151–156 en sus vecinos (η 8.7 % y 9.7 %) y 277–316 s de cómputo: probablemente una
solución en otra rama del solver.

Añade a `LEEME` la sección **«Puntos atípicos»** con una tabla (id_punto, estudio, centro, T_fuente (K), r_P,
Δh de turbina (kJ/kg), mediana de la banda, η (%), tiempo de cómputo (s)) y la nota: «No se descartan: se señalan
porque su caída de entalpía de turbina es anormalmente baja respecto de puntos vecinos; pueden ser soluciones del
solver en otra rama.» En `E15`, junto a la matriz de B6 en C4, añade una nota que remita a esa tabla. No toques
las hojas de datos.

## Verificación (añade controles a `x8_verificar.py`; no quites los anteriores)

20. `E13 §3`: ε_cond mínima por centro C1 0.80, C2 0.65, C3 0.85, C4 0.85 (con estudio y P_baja), sin celdas
    vacías.
21. La tabla por banda de x_b existe en `E13` y en S3 (c), con las 6 bandas y los valores de arriba; el gráfico
    tiene series numéricas.
22. Ningún texto del libro contiene la frase «con eps_cond < 0.85 no hay KALINA» sin el acotamiento a Húsavík.
23. Las matrices de `E15` y `E16` tienen rótulo de filas y de columnas en la celda de esquina.
24. `LEEME` tiene la tabla de puntos atípicos con exactamente los 7 ids de arriba (si la regla da otros,
    reporta cuáles y por qué).
25. ≥ 43 gráficos en total, sin solapes y todos con valores numéricos.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

No des `done` con algún control en FALLA. Reporte en el formato de `AGENTS.md`; en RESULTS: salida completa de
`x8_verificar.py` (sin la lista larga de gráficos), la tabla por banda de x_b y la ε_cond mínima por centro, tal
como salieron del libro.

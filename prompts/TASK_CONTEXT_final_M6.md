# TASK_CONTEXT — M6: verificación con el motor real + margen de subenfriamiento (O2) + Excel

**Fecha:** 2026-10-08 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal (nada de `Set-Content`, `Out-File`, here-strings ni `Add-Content`).
- PowerShell 5.1: no existen `tee` ni `&&`.
- Las corridas largas van EN PRIMER PLANO, sin `Start-Process` ni jobs, y cada una se lanza UNA
  sola vez. Si tarda, espera: no la relances.

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` nuevo debe tener como
  máximo 200 líneas: si hace falta, varios scripts.
- Usa `comun.evaluar_punto(combo, motor=..., tag=..., t_amb_diseno=...)` para cada evaluación.
  `motor="teqp"` es el motor principal; `motor="real"` es el motor riguroso (`AmmoniaWaterAdapter`).
- `ProcessPoolExecutor(max_workers=7)`. No hacer commit. No inventar datos.
- **Punto genuino** = clase KALINA, CORREGIBLE o INVIABLE. `convergio=True` con clase
  NO_CONVERGIO es un punto espurio (N2) y NO cuenta como genuino.

## Parte A — verificación cruzada teqp vs. motor real (24 corridas)

Cada punto se evalúa dos veces: con `motor="teqp"` y con `motor="real"`, con el mismo `combo`
(las 11 variables de `comun.PROFESOR`) y el mismo piso de O2 (`t_amb_diseno`).

| id | Origen | Cómo se construye | Piso O2 |
|---|---|---|---|
| P01 | Ancla A\* | `dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)` | 300.032917 |
| P02 | M2, mayor η | `dict(PROFESOR, T_fuente=420.0, P_baja=<val2>)`, con `<val2>` = la P_baja de la fila de `resultados/2026-10-06_final_M2/m2n2_kalina.csv` con T_fuente 420 y mayor η | 300.032917 |
| P03 | M5c, presiones del profesor, techo | `dict(PROFESOR, T_fuente=410.0, eps_cond=0.95)` | 300.032917 |
| P04 | M5c, presiones del profesor, ε_cond mínima | `dict(PROFESOR, T_fuente=390.0, eps_cond=0.875)` | 300.032917 |
| P05–P09 | M7, óptimos A1…A5 | las 11 variables de cada fila de `resultados/2026-10-07_final_M7/m7_optimos.csv` (m_b = 1.0) | su `T_sumidero` |
| P10 | M4b, top 1 | fila `puesto=1` de `resultados/2026-10-07_final_M4b/m4b_top_kalina.csv` (m_b = 1.0) | su `T_sumidero` |
| P11 | M4c, mayor P_baja KALINA | fila KALINA con mayor P_baja de `resultados/2026-10-07_final_M4c/m4c_lhs.csv` | su `T_sumidero` |
| P12 | M2R, fuente del profesor | `resultados/2026-10-06_final_M2R/m2r_kalina.csv`: fila KALINA con ε_HRVG 0.40 y fuente 623.15 K (la de menor P_baja). Reconstruir el combo a partir de `PROFESOR` + `var1/val1/var2/val2` | 300.032917 |

Si alguna fila de origen no existe o es ambigua, repórtalo en `UNRESOLVED` y sigue con las demás.
Antes de la corrida real, haz un humo con 2 puntos (`M6_HUMO=1`).

**Salida:** `resultados/2026-10-08_final_M6/m6_verificacion.csv`, con una fila por (punto, motor),
todas las columnas de `comun.COLS` más `id` y `origen`, y `m6_comparacion.csv`, con una fila por
punto:

- `clase_teqp`, `clase_real` y `coincide_clase`;
- `eta_teqp`, `eta_real` y `d_eta_pp = 100·(eta_real − eta_teqp)`;
- `dentro_banda = |d_eta_pp| ≤ 0.7` (la banda de incertidumbre de η, G4-01);
- `m_O1` y `m_O2` de los dos motores;
- `fuera_rango` y `B_verificado` de teqp.

## Parte B — margen de subenfriamiento en la succión de la bomba (O2)

**Contexto (no lo cambies):** `src/restricciones/operativos.py` exige solo `T9 ≤ T_bub(P_baja,
x_b)` evaluado al piso, es decir, un subenfriamiento ≥ 0 K. En esta campaña `m_O2 = T_bub − T9`
ES el subenfriamiento disponible, y varios óptimos tienen menos de 0.5 K. La pregunta es cuánto
cuesta en η y en P_baja exigir un margen real de subenfriamiento ΔT_sub.

**B1, re-evaluación con el piso por defecto del código (12 corridas, solo teqp):** los 12 puntos
de la Parte A con `t_amb_diseno=303.55` (el default de `verificar_operativos`, 30.4 °C). Se
reportan la clase, η y m_O2.

**B2, P_baja mínima para un ΔT_sub dado (solo teqp):**

- Puntos: P01, P02, P03 y P05–P09, cada uno con su piso de la Parte A.
- Objetivos: ΔT_sub ∈ {2.0, 5.0} K.
- Predicado: `clasificacion == "KALINA" and m_O2 >= ΔT_sub`.
- Bisección SOLO sobre P_baja, con el resto de las variables fijas:
  - `lo` = la P_baja del punto, donde el predicado debe fallar;
  - `hi` = `min(0.6·P_alta, 2500)`;
  - primero se evalúa `hi`: si allí el predicado no se cumple, se registra "no alcanzable con
    P_baja" y no se biseca;
  - si en `lo` ya se cumple, se registra `P_baja_req = lo`;
  - se itera hasta que `hi − lo ≤ 5 kPa` o 12 iteraciones, y se toma como `P_baja_req` el último
    `hi` que cumple.
- Las 16 bisecciones (8 puntos × 2 objetivos) son independientes: se paralelizan entre ellas.
- Se registran todas las evaluaciones en `m6_subenfriamiento_evals.csv` y un resumen en
  `m6_subenfriamiento.csv`, con estas columnas: id, ΔT_sub, alcanzable, P_baja_orig, P_baja_req,
  ΔP_baja, eta_orig, eta_req, `d_eta_pp`, `rP_req = P_alta/P_baja_req`, m_O1_req e iteraciones.
- Si el predicado no es monótono en P_baja (por ejemplo, un hueco NO_CONVERGIO dentro del
  intervalo), anótalo en una columna `nota`. No lo escondas.

## Parte C — reporte y Excel

1. `resultados/2026-10-08_final_M6/REPORTE_M6.md`, en lenguaje llano:
   - la pregunta;
   - la tabla de la Parte A, con cuántos puntos coinciden en clase y cuántos quedan dentro de la
     banda de ±0.7 pp;
   - la tabla de B1;
   - la tabla de B2;
   - lo que no se sabe.
   Todas las cifras del reporte deben salir del CSV.
2. `m6_verificar.py`: recalcula desde los CSV los conteos y las cifras del reporte e imprime OK o
   FALLA por cada una.
3. `scripts/barrido_final/excel_m6.py`, con el mismo patrón que `excel_m5c_m7_m8.py` (léelo:
   reutiliza `excel_final.escribir_tabla`, es idempotente y añade o actualiza sus filas en
   `Resumen`). Hojas: `M6_verificacion`, `M6_comparacion`, `M6_piso_30_4C` (B1),
   `M6_subenfriamiento` y `M6_subenf_evals`.
4. Ejecuta en orden `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py`,
   `excel_m5.py`, `excel_m5c_m7_m8.py` y `excel_m6.py`.
5. Verifica con un script hecho con `write`:
   - que las hojas M6 existen con el número de filas de su CSV;
   - que las 59 hojas anteriores siguen presentes;
   - que `Resumen` tiene las filas de M6.

## Pasos

1. Crear los scripts: corrida A+B1, bisección B2, análisis/reporte, verificador y Excel.
2. Humo, corrida A+B1, corrida B2, análisis, verificación y Excel.

## Formato de salida

El obligatorio de `AGENTS.md`.

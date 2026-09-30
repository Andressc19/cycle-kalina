---
project: ciclo_kalina_tercero
task_id: 2026-09-24-validacion-tendencias-embaye
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — Validación por tendencias contra Elsayed et al. (2013) / Embaye et al.

## Task ID

2026-09-24-validacion-tendencias-embaye

## Contexto

La validación actual (`VALIDACION_ELSAYED2013.md`) es de **un solo punto** (11.05 % vs 11.38 %,
−0.33 pp). Esta tarea la extiende a ~30 puntos sobre las curvas del modelo publicado, para
comparar **tendencias** (forma de las curvas, posición del máximo), no solo un valor.

Datos del paper: ya extraídos de forma exacta del PDF vectorial por la tarea previa
(`resultados/2026-09-24_embaye_vectorial/curvas_embaye_eta_vs_xb.csv` y
`curvas_embaye_fig7.csv`; léelos, no los recalcules). Referencia: Elsayed et al. (2013),
IJLCT 8(suppl_1) i69–i78, y su versión de congreso Embaye et al. (mismo modelo EES, Ibrahim &
Klein 1993, η_t = η_p = 0.80, **pinch 4 K** en evaporador, condensador y regenerador,
T_sumidero = 283 K, título a la salida de turbina limitado a ≥ 0.90).

## Método (el mismo ya aceptado por el usuario para el punto único — no cambiarlo)

Reutilizar por import `scripts/calibracion_elsayed_malla.py` (no modificarlo):
- `calibrar_P_baja(backend, x_b, P_alta)` → P_baja = presión de burbuja a (T_sumidero+4 K, x_b).
- `calibrar_eps(backend, x_b=..., P_alta=..., P_baja=..., T_fuente=...)` → ε calibradas para
  reproducir el pinch de 4 K (un paso) + resultado del ciclo.
- Constantes `T_SUMIDERO`, `ETA_T`, `ETA_P`, `M_B` de ese módulo.

Las ε calibradas quedarán **fuera** de la banda 0.75–0.85 del proyecto: es **correcto y
esperado aquí**, porque se replican las hipótesis del paper (ver `CONTEXT.md`/memoria de
validación). Regístralas en el CSV; no las recortes.

Motor: `TeqpAdapter` para todos los puntos. Además, **3 puntos de control con
`AmmoniaWaterAdapter`** (el motor de referencia, verificado contra IAPWS G4-01): (x_b=0.55,
15 bar, 373 K), (x_b=0.66, 25 bar, 373 K) y (x_b=0.60, 15 bar, 423 K). Si no convergen con
alguno de los motores, se registra, no se oculta.

## Puntos a evaluar

Solo se evalúa un punto si su x_b (o P) cae **dentro del rango** de la serie extraída del paper
(nunca extrapolar la curva del paper). η_paper = interpolación lineal de la serie en ese x.

| Serie del paper | T_fuente [K] | P_alta [kPa] | Variable | Valores |
|---|---|---|---|---|
| Fig. 7, KCS11 Con.=0.55 | 373 | 1100, 1200, 1500, 1800, 2000, 2200, 2300 | P | x_b = 0.55 |
| Fig. 7, KCS11 Con.=0.66 | 373 | 1100, 1500, 2000, 2500, 3000 | P | x_b = 0.66 |
| Fig. 3 (15 bar) | 373 | 1500 | x_b | 0.45, 0.55, 0.65, 0.75, 0.85 |
| Fig. 3 (15 bar) | 423 | 1500 | x_b | 0.45, 0.60, 0.75 |
| Fig. 3 (15 bar) | 333 | 1500 | x_b | 0.65, 0.75, 0.85 |
| Fig. 2 (10 bar) | 373 | 1000 | x_b | 0.45, 0.60, 0.80 |
| Fig. 5 (32 bar) | 423 | 3200 | x_b | 0.60, 0.80 |
| Fig. 5 (32 bar) | 463 | 3200 | x_b | 0.60, 0.80 |

(x_b = fracción másica de NH3 a la salida del evaporador = x_b del proyecto. Para las series de
Fig. 7, la "Con." del paper es esa misma fracción másica.)

Se espera que los puntos de 333 K NO converjan (problema conocido del arranque del solver con
T_fuente baja, ver `resultados/2026-09-23_limites_teqp/REPORTE_LIMITES_TEQP.md`): se evalúan
igual y se reportan como `no_converge` con el error real. **No intentar arreglar el solver.**

## Por punto, registrar

`serie, T_fuente_K, P_alta_kPa, x_b, motor, P_baja_kPa, eps_hrvg, eps_reg, eps_cond,
convergio, eta_modelo_pct, eta_paper_pct, delta_pp, delta_rel_pct, titulo_salida_turbina,
Wnet_kW, detalle_error`.

`titulo_salida_turbina` = calidad del estado 4 (el paper limita a ≥ 0.90; si en el modelo sale
< 0.90, márcalo: ese punto no es comparable 1:1 con el paper).

## Análisis de tendencias (en el reporte)

1. Tabla de todos los puntos (con Δ en pp y relativo).
2. Estadística global sobre los puntos que convergen y son comparables: n, Δ medio, Δ medio
   absoluto, Δ máximo absoluto (en pp y %).
3. **Fig. 7, x_b = 0.55**: ¿el modelo reproduce la forma (sube, máximo, cae)? P del máximo del
   modelo (entre los puntos evaluados) vs P del máximo de la serie del paper.
4. **Fig. 3, 373 K**: ¿el orden y el sentido de la variación de η con x_b coinciden (signo de
   las pendientes entre puntos consecutivos, modelo vs paper)?
5. **Efecto de T_fuente** a 15 bar (373 vs 423 K, mismo x_b): ¿el modelo sube η como el paper?
6. Diferencia teqp vs AmmoniaWaterAdapter en los 3 puntos de control.
7. Gráfica `comparacion_tendencias.png` (matplotlib): paneles con las series del paper (línea)
   y los puntos del modelo (marcadores) — Fig. 7 (η vs P) y Fig. 3 (η vs x_b, por T_fuente).
8. Conclusión honesta: dónde coincide, dónde no, y las fuentes esperadas de discrepancia (EOS
   distinta Ibrahim-Klein vs Tillner-Roth; traducción pinch→efectividad de un paso; P_baja
   supuesta). **No** fuerces una conclusión favorable.

## Files

Crear:
- `scripts/validacion_tendencias_embaye.py` (≤ 250 líneas), reanudable por CSV (clave
  `(serie, T_fuente_K, P_alta_kPa, x_b, motor)`), captura de excepciones por punto sin abortar.
- `resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`
- `resultados/2026-09-24_validacion_tendencias/comparacion_tendencias.png`
- `resultados/2026-09-24_validacion_tendencias/REPORTE_VALIDACION_TENDENCIAS.md`

**No modificar ningún archivo existente** (ni `src/`, ni `scripts/`, ni
`VALIDACION_ELSAYED2013.md`).

## Constraints

- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero`** (ni temporales): el
  sandbox aborta la ejecución completa.
- La corrida puede tardar (~1–2 min por punto): lánzala de forma que el CSV se vaya escribiendo
  punto a punto; si se corta, relanza y continúa. No imprimas trazas enormes al log.
- No inventar valores ni tolerancias de "aceptación": se reportan las desviaciones tal cual.

## Acceptance criteria

1. CSV con todas las filas (convergidas o no, con su error).
2. Reporte con los 8 puntos de análisis y la gráfica.
3. RESULTS: estadística global, veredicto por tendencia (1 frase cada una) y control
   teqp vs AmmoniaWaterAdapter.

## Verification

`.venv/Scripts/python.exe scripts/validacion_tendencias_embaye.py` corrido hasta el final;
salida en el formato obligatorio de AGENTS.md.

## Nota de Claude tras auditar la extracción (2026-09-24)

Los CSV de `resultados/2026-09-24_embaye_vectorial/` están verificados (control independiente:
serie Fig. 3 / 373 K, identificada por color, da 11.39 % en x_b=0.55 vs 11.38 % del texto).
Las imágenes `auditoria_pag*.png` de esa tarea tienen un error de proyección (los puntos no se
dibujan sobre las curvas): ignóralas, no las uses ni las corrijas. En `curvas_embaye_fig7.csv`
la columna `curva` vale `KCS11(Con.=0.55)` / `KCS11(Con.=0.66)`.

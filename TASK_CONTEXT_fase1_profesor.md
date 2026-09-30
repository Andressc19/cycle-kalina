---
project: ciclo_kalina_tercero
task_id: 2026-09-19-fase1-profesor
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-19
---

# TASK_CONTEXT — Fase 1: correr y documentar el fallo con los datos EXACTOS del profesor

## Task ID

2026-09-19-fase1-profesor

## Project

`ciclo_kalina_tercero`, rama `test/vv-strategy` (ya mergeada). Esta es la Fase 1 de 3 fases
paralelas de la tarea de barridos de sensibilidad (ver `AGENTS.md` para el protocolo y
formato de reporte). **Corre en paralelo con `TASK_CONTEXT_fase2_libre.md` y
`TASK_CONTEXT_fase3_real.md` — NO toques archivos fuera de tu carpeta asignada
(`scripts/barridos_2026-09-19/fase1_profesor/` y
`resultados/barridos_2026-09-19/fase1_profesor/`) para no chocar con las otras dos tareas
que corren al mismo tiempo.**

## Objective

Transcribir literalmente el enunciado real del profesor (documento Word "5 CICLO KALINA",
ya leído por el director — los datos exactos están abajo, no hace falta releer el docx) al
solver de este repo, correr el punto base y el análisis de sensibilidad pedido, y DEJAR
CONSTANCIA documentada del resultado — se espera que la mayoría o todos los puntos NO
clasifiquen `KALINA` (ya se sabe por experiencia previa con `T_fuente` alto en este repo:
ver `CONTEXT.md`, nota 2026-09-17, y las corridas de la Fase B0 anterior en
`resultados/barridos_2026-09-19/b0_scan_cementera.csv` — mismo síntoma con T_fuente=583 K).
**Este NO es un ejercicio de optimización**: se corre tal cual, se registra el resultado
completo (converja o no), y se documenta. No autorizado a ajustar ninguna variable para
"hacerlo funcionar" — eso es la Fase 2, una tarea distinta.

## Datos EXACTOS del enunciado (transcritos del Word por el director, no inventes nada más)

- Fluido: mezcla NH3-H2O. `m_b` (m9=m10) = 1.0 kg/s. `x_b` = 0.50.
- Fuente térmica: `T_fuente` = 350 °C = **623.15 K**. `eps_hrvg` = 0.85.
- Sumidero: `T_sumidero` = 27 °C = 300.15 K de forma nominal, PERO el enunciado da una
  **tabla horaria real de T_ambiente de 24 valores** (transcrita en
  `scripts/barridos_2026-09-19/fase1_profesor/tamb_profesor.csv`, columnas `hora,T_amb_K`,
  promedio 300.032917 K — coincide exactamente con el `T_sumidero` por defecto de
  `CONTEXT.md`). Úsala tal cual para el barrido de T_ambiente (no inventes otro rango).
  `eps_cond` = 0.80.
- `P_alta` = 3000 kPa (puntos 1,2,3,5,6,10). `P_baja` = 400 kPa (puntos 4,7,8,9).
- `eps_reg` = 0.75.
- `eta_t` = 0.85, `eta_p` = 0.75.
- Válvula isoentálpica (ya implementado en `src/components/valvula.py`, no lo toques).
- Rangos de sensibilidad pedidos EXPLÍCITAMENTE por el enunciado:
  1. `P_alta`: 2000 a 4000 kPa.
  2. `x_b`: 0.4 a 0.7.
  3. `T_ambiente`: la tabla horaria real de 24 valores (no un rango sintético).

## Approach

1. Corre el punto base exacto (`P_alta=3000, P_baja=400, x_b=0.50, T_fuente=623.15,
   T_sumidero=300.032917` [promedio de la tabla, o el valor de una hora concreta si
   prefieres barrer las 24 horas directamente — tu elección, documenta cuál usaste],
   `m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80`) con
   `resolver_ciclo` + `evaluar_ciclo` (motor real `AmmoniaWaterAdapter` para el punto base
   — es solo 1 punto, el costo es aceptable).
2. Corre los 3 barridos de sensibilidad pedidos, con `TeqpAdapter` (rápido, es un barrido
   de exploración/documentación, no una publicación final):
   - `eta_vs_Palta_profesor`: P_alta de 2000 a 4000 kPa, paso 250 kPa (9 puntos). Resto base.
   - `eta_vs_xb_profesor`: x_b de 0.40 a 0.70, paso 0.05 (7 puntos). Resto base.
   - `eta_vs_Tambiente_profesor`: las 24 T_amb de
     `scripts/barridos_2026-09-19/fase1_profesor/tamb_profesor.csv`, usadas como
     `T_sumidero` (y también como `T_fuente` si el enunciado lo implicara — NO lo hace: el
     enunciado fija `T_fuente=623.15 K` aparte; la tabla de T_ambiente es el sumidero/ambiente,
     no la fuente — no confundas los dos). Resto base.
3. Registra CADA punto (converja o no) en 3 CSV separados en
   `resultados/barridos_2026-09-19/fase1_profesor/`: `eta_vs_Palta_profesor.csv`,
   `eta_vs_xb_profesor.csv`, `eta_vs_Tambiente_profesor.csv`, con columnas: la variable
   barrida, el resto de parámetros fijos, `convergio`, `clasificacion`, `eta`, `Wnet`,
   `mensaje` (usa `Fijo`/`Barrido` + `ejecutar_barrido`/`tabla_barrido` de
   `src/sensitivity.py`, es la herramienta ya validada para esto).
4. Escribe `resultados/barridos_2026-09-19/fase1_profesor/CONSTANCIA_PROFESOR.md` (español):
   valores usados, conteo de puntos por `clasificacion` en cada uno de los 3 barridos, y la
   conclusión explícita de que los datos del profesor se corrieron tal cual y el resultado
   real obtenido (sea el que sea — si algún punto SÍ clasifica KALINA contra lo esperado,
   repórtalo igual, sin sesgo).

## Files

Todo nuevo en `scripts/barridos_2026-09-19/fase1_profesor/` (ya existe, con
`tamb_profesor.csv` ya puesto ahí) y `resultados/barridos_2026-09-19/fase1_profesor/`.
Límite 200 líneas por archivo `.py`.

**NO modifiques**: `src/cycle_solver.py`, `src/sensitivity.py`, `src/properties/`,
`src/restricciones/`, `src/components/`, `src/state.py`, `src/ui_*.py`, `app.py`,
`CONTEXT.md`. **NO toques ninguna carpeta `fase2_libre/` ni `fase3_real/`** (otras tareas
corriendo en paralelo).

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. No inventes valores: todo lo que necesites ya está en este documento o en
   `tamb_profesor.csv`. Si te falta algo, repórtalo en `UNRESOLVED`.
3. Tope: ~25 puntos con `TeqpAdapter` (barridos) + 1 punto con el motor real (base). No
   necesitas más — esta fase es de documentación, no de búsqueda.
4. Un punto que no converge se registra igual (`NO_CONVERGIO`, con `mensaje`), nunca se omite.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS` incluye el conteo de clasificaciones de los 3 barridos.

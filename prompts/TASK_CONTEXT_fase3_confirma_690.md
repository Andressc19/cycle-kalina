---
project: ciclo_kalina_tercero
task_id: 2026-09-20-fase3-confirma-690
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-20
---

# TASK_CONTEXT — Fase 3: confirmar con motor real el punto ancla aprobado (690/0.75/0.95)

## Task ID

2026-09-20-fase3-confirma-690

## Project

`ciclo_kalina_tercero`, rama `fix/temperatura-ambiente`. **Corre en paralelo con
`TASK_CONTEXT_fase2_eps_hrvg.md` (otra sesión, trabaja solo en
`scripts/barridos_2026-09-19/fase2_libre/`) — no la toques.**

## Contexto

En `resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK_v2.md` el candidato confirmado
con motor real fue `P_baja=670 kPa, eps_reg=0.95, eps_cond=0.95` (η=0.13445). El director
decidió DESPUÉS, por criterio de robustez (margen O2 muy al filo, +0.30 K) y realismo
(`eps_reg=0.95` es forzado, poco realista), cambiar el candidato ANCLA a
**`P_baja=690 kPa, eps_reg=0.75, eps_cond=0.95`** — este punto solo se probó con
`TeqpAdapter` (η≈0.12732, ver tabla de diagnóstico en `CASO_HUSAVIK_v2.md` §2), **NUNCA se
confirmó con el motor real**. Esto es un vacío metodológico: no se puede reportar un barrido
de sensibilidad alrededor de un punto ancla no verificado con el motor riguroso, dado que ya
se documentó que `TeqpAdapter` y el motor real discrepan cerca de fronteras de clasificación.

## Objective

1. Corre `resolver_ciclo` + `evaluar_ciclo` con el motor real (`AmmoniaWaterAdapter`) en el
   punto EXACTO: `P_alta=3300, P_baja=690, x_b=0.82, T_fuente=394.15, T_sumidero=278.15,
   m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
   T_amb_diseno=283.15`.
2. Reporta si clasifica `KALINA` (esperado, según `TeqpAdapter`) y compara `eta`/`Wnet`
   contra el valor de `TeqpAdapter` (0.12732) — igual que se hizo para los candidatos
   anteriores (diferencia relativa esperada < 1%, si es mayor repórtalo como discrepancia sin
   suavizarla).
3. Guarda el resultado en
   `resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real_690.json` (mismo
   formato que `confirmacion_motor_real_v2.json`, que ya existe — sigue ese esquema).
4. Actualiza `resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK_v2.md`: añade una
   sección corta (o actualiza la tabla del §1) dejando explícito que el candidato ANCLA final
   es 690/0.75/0.95 (no 670/0.95/0.95), con su confirmación de motor real — SIN borrar la
   comparación histórica que ya existe (670 sigue siendo un punto de referencia válido, solo
   ya no es el candidato elegido).

## Files

Puedes crear `scripts/barridos_2026-09-19/fase3_real/confirma_690.py` (o reutilizar/adaptar
`confirma_motor_real_v2.py` como referencia, sin sobrescribirlo). Editar SOLO
`resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK_v2.md` (la sección que documenta el
candidato ancla) y crear el JSON nuevo.

**NO modifiques**: nada de `src/`, `TASK_CONTEXT*.md`, ni `scripts/barridos_2026-09-19/fase2_libre/`
ni `scripts/barridos_2026-09-19/fase1_profesor/`.

## Constraints

1. Cada archivo `.py` ≤ 200 líneas.
2. Es 1 solo punto con motor real (~5-10 min) — no hace falta más.

## Report format

`AGENTS.md`: STATUS/SUMMARY/FILES_CHANGED/TESTS/RESULTS/ERRORS/ASSUMPTIONS/UNRESOLVED/
RECOMMENDATIONS. En `RESULTS`: eta/Wnet/clasificación del motor real vs Teqp para este punto.

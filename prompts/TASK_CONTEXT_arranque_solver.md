---
project: ciclo_kalina_tercero
task_id: 2026-09-30-arranque-solver-falsos-negativos
delegated_to: executor
created: 2026-09-30
---

# TASK_CONTEXT — ¿El arranque del solver produce falsos NO_CONVERGIO? (sonda de diagnóstico, SIN tocar `src/`)

## Task ID

2026-09-30-arranque-solver-falsos-negativos

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques.

## Contexto (hipótesis a contrastar, no a asumir)

Una auditoría (2026-09-30) contó los `NO_CONVERGIO` de los CSV de `resultados/`. La mayoría (cientos de filas en Fase 2; 20 de 28 en la ventana de literatura) son `PropertyRangeError` en `T_from_Ph`/`h(P,s,x)` con mensajes como "equilibrio no resoluble en T=296.92 K, P=5e+05 Pa, x=0.1626" o "h=-6412.95 fuera de dominio". Esas T y x no son estados plausibles del ciclo: parecen estados **intermedios visitados por el solver**, no el punto de diseño.

**Hipótesis H1:** `evaluar` (en `src/_cycle_loops.py`) arranca el lazo frío con `T10_guess = T1_trial` y `_bracketear` evalúa F en los extremos `T_sumidero+1` y `T_fuente-1`; en esos puntos se visitan estados no físicos, el backend lanza `PropertyRangeError` y el error aborta la solución aunque exista una raíz interior. Si H1 es cierta, parte de esos `NO_CONVERGIO` serían falsos negativos.

**Hipótesis nula H0:** el error ocurre también en el punto final/raíz, es decir, el motor realmente no cubre el estado del ciclo.

## Objective

Crear `scripts/sonda_arranque_solver.py` (nuevo, ≤200 líneas) y, con él, medir para una muestra de filas `NO_CONVERGIO`:

1. **Dónde** se lanza la excepción (instrumentación): en qué evaluación de F, con qué `T1_trial`, en qué iteración del lazo frío, y si es un extremo del bracket o un punto interior de brentq.
2. **Cuántas** filas se recuperan con cambios SOLO dentro del script (reimplementando la orquestación de `resolver_ciclo` llamando a `src._cycle_loops.evaluar` y `brentq`; **no editar `src/`**):
   - **V0 (control):** réplica fiel del comportamiento actual (`T10_inicial=None` en la primera evaluación, bracket de `_bracketear` tal cual). Debe reproducir el `NO_CONVERGIO` original; si no lo reproduce, repórtalo.
   - **V1:** igual que V0 pero `T10_inicial = T_sumidero + 5.0` K en la primera evaluación de cada F (el warm-start posterior `ultimo_T10` se conserva).
   - **V2:** V1 + bracket tolerante: una función `F_seguro` que captura `PropertyRangeError`, devuelve `None`, y el bracket se repliega hacia el interior en pasos de 5 K desde cada extremo hasta hallar dos extremos evaluables con cambio de signo. Si no hay ninguno, V2 falla.
3. Para cada fila recuperada por V1/V2: resolver hasta el final, pasar `evaluar_ciclo` (`src.restricciones`) y reportar `clasificacion`, `eta`, `Wnet`.

## Muestra (leer de los CSV, no inventar parámetros)

- `resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv`: 15 filas `NO_CONVERGIO` con `T_from_Ph` y 5 con `h(P, s, x)`, repartidas (no las primeras 20; tomar con paso uniforme sobre el listado).
- `resultados/2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv`: las 20 filas con `T_from_Ph` (o todas si hay menos), más las 7 con "no existe equilibrio bifásico" como grupo aparte.
- **Control positivo:** 5 filas `KALINA` de `busqueda_libre_v2.csv` y 5 `KALINA` de la ventana de literatura; V1 y V2 deben dar la misma clasificación y η (|Δη| < 1e-4) que el CSV original. Si cambian, repórtalo: es un riesgo de regresión.

Los parámetros fijos que el CSV no trae (T_sumidero, eta_t, eta_p, m_b, T_amb_diseno, motor) se leen del script que generó cada CSV (`scripts/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.py`, `scripts/barrido_literatura_kcs11.py`); si un valor no está ahí, repórtalo en `UNRESOLVED`, no lo supongas.

## Constraints

- **No modificar** nada en `src/`, `tests/` ni los scripts/CSV existentes.
- Backend: `TeqpVerificado` (regla de CONTEXT.md, "Motor teqp: protección A+B") para toda la muestra; al final, las filas recuperadas que salgan KALINA se verifican con `verificar_turbina` y un `AmmoniaWaterAdapter` (una instancia). Si el CSV original usó otro backend, indícalo.
- No escribir credenciales ni leer fuera de `D:\Desktop\ciclo_kalina_tercero`.
- Archivos nuevos solo en `scripts/` y `resultados/2026-09-30_arranque_solver/`.
- Tiempo: ~30 s por punto con teqp; si la muestra completa excede ~60 min, reduce a la mitad (conservando reparto) y repórtalo.

## Outputs

- `scripts/sonda_arranque_solver.py`
- `resultados/2026-09-30_arranque_solver/sonda_filas.csv`: una fila por muestra con parámetros, `clasificacion_original`, resultado V0/V1/V2 (convergió, clasificación, eta, mensaje), y para V0: `donde_falla` (`extremo_lo`/`extremo_hi`/`interior_brentq`/`lazo_frio`/`punto_final`), `T1_trial`, `iter_lazo_frio`.
- `resultados/2026-09-30_arranque_solver/REPORTE_ARRANQUE_SOLVER.md` con: tabla resumen (cuántas filas por grupo se recuperan en V1 y V2, distribución de `donde_falla`), control positivo (sí/no cambia algo), y conclusión explícita H1 vs H0 con los números. **No generalices más allá de la muestra**: si la muestra no basta, dilo.

## Done criteria

- V0 reproduce el `NO_CONVERGIO` en ≥90 % de la muestra (si no, explicar).
- Se reporta `donde_falla` para todas las filas que no convergen.
- Control positivo evaluado en 10 filas.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS). No decidir si cambiar `src/`: eso lo decide el director; solo reportar evidencia.

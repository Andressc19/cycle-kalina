---
project: ciclo_kalina_tercero
task_id: 2026-10-02-reejecutar-no-convergio
delegated_to: executor
created: 2026-10-02
---

# TASK_CONTEXT — Pasos 3 y 4: re-ejecutar los NO_CONVERGIO con el solver MA y verificar con el motor real. SIN tocar `src/`

## Task ID

2026-10-02-reejecutar-no-convergio

## Project

`ciclo_kalina_tercero`, **worktree** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\solver-bracket`, rama `fix/solver-bracket-tolerante`, que ya contiene MA implementado y verificado (`resultados/2026-10-02_implementar_ma/REPORTE_IMPLEMENTAR_MA.md`). **Trabaja SOLO dentro de este worktree** (directorio actual); el checkout principal lo usa otra sesión. Python: `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` con el directorio actual = el worktree. Los demás `TASK_CONTEXT_*.md` son OTRAS tareas.

## Paso 3 — Re-ejecutar los NO_CONVERGIO históricos con MA

### Universo
Todas las filas `clasificacion == NO_CONVERGIO` de los CSV de **barridos** en `resultados/`:
`barridos_2026-09-19/**` (fase 1, fase 2, fase 3, `b0_scan_cementera.csv`), `2026-09-21_xb_industria`, `2026-09-22_literatura_kcs11`, `2026-09-22_tfuente_bajo`, `2026-09-22_frontera_tfuente`, `2026-09-23_eps_fijos_085`, `2026-09-23_pinch6_realista`, `2026-09-24_margen2k`.
**Excluir** los CSV derivados que solo reclasifican o repiten puntos (`2026-09-22_o2_tamb_realista/reclasificacion_o2.csv`) y todas las carpetas de análisis `2026-09-30_*`, `2026-10-01_*`, `2026-10-02_*`. **Deduplicar** por la tupla de las 11 variables de `resolver_ciclo` + `T_amb_diseno`, conservando la lista de CSV de origen.

### Parámetros
Reconstruir cada fila con las mismas reglas ya probadas en `scripts/sonda_arranque_solver.py` (`muestra()`) y `scripts/comprobacion_o5_t2min.py` (lectura de constantes del script generador). Para filas sin `eps_*` en el CSV (NO_CONVERGIO de literatura), usar `EPS_PARTIDA = (0.85, 0.75, 0.80)` como hizo la sonda y marcar `eps_supuesta=True`. `T_amb_diseno`: el que pasó el script generador de cada barrido (p. ej. 303.55 K en fase 2; 283.15 K en fase 3; lo que diga cada script); si no se puede determinar, `PARAMETROS_NO_RECONSTRUIBLES` y seguir (no inventar).

### Ejecución
- `resolver_ciclo(..., bracket_tolerante=True, presupuesto_s=300)` con `TeqpVerificado(x=x_b)` (regla A+B de `CONTEXT.md`), y `evaluar_ciclo(...)` **dentro del mismo `try`** (un error de clasificación no debe abortar nada). Filas KALINA: `verificar_turbina` con una instancia de `AmmoniaWaterAdapter` por worker.
- 6 workers (`ProcessPoolExecutor`), lanzado con `nohup`, **CSV incremental y reanudable** (una fila escrita con `flush` al terminar; al reanudar se omiten las hechas), una línea por fila en `resultados/2026-10-02_reejecucion/progreso.log` (`n/total (s) origen fila resultado`). Humo previo de 6 filas **dentro de un worker**. Una excepción en una fila se escribe como fila (`causa`, `msg`) y nunca aborta.
- **Orden:** primero los barridos pequeños (literatura, margen2k, pinch6, eps_fijos, tfuente_bajo, frontera, xb_industria, fase 3, fase 1), luego fase 2, y la cementera al final.
- **Límite global:** si el reloj de pared supera **6 h**, detener ordenadamente, dejar el CSV válido y reportar lo hecho (es reanudable).

### Por fila registrar
Parámetros, origen(es), `mensaje_original`, `convergio`, `clasificacion`, `eta`, `Wnet`, `T1`, `nF`, `repliegues_lo/hi`, `t_s`, `causa` (`presupuesto agotado`, `sin cambio de signo`, `sin extremos evaluables`, `punto interior no evaluable`, otro), `fallas` (códigos de criterios), `B_verificado`/`B_dh4s` si KALINA.

### Cruce con la comprobación O5
Con `resultados/2026-10-01_comprobacion_o5/comprobacion_o5_filas.csv` (cruza por P_alta, x_b, T_fuente, T_sumidero, eps): de las 45 `*_DEMOSTRADA`, cuántas convergen ahora (deberían ser 0; si alguna converge con estado 2 dentro de la campana, es una contradicción: repórtala); de las 316 `DENTRO_DE_CAMPANA_POSIBLE`, cuántas convergen (→ no eran O5) y cuántas siguen fallando y por qué.

## Paso 4 — Verificar con el motor real

Elegir **10 filas recuperadas** en el paso 3 (convergieron ahora y antes eran NO_CONVERGIO), repartidas por barrido de origen y por clasificación (todas las KALINA si hay ≤ 3; incluir la de mayor `eta` y la de menor `eta`; si alguna fila tiene una falla N2, incluirla). Resolver cada una completa con `AmmoniaWaterAdapter` y `bracket_tolerante=True`, `presupuesto_s=None` (motor real, ~5–10 min por punto; 6 workers, desacoplado, incremental). Comparar con teqp: criterio `|Δη|/η < 0.5 %` y **misma clasificación**. Reportar cualquier discrepancia con su causa probable; no ajustar el criterio.

## Constraints

- **No modificar `src/`, `tests/`, ni scripts/CSV existentes.** Nuevos: `scripts/reejecutar_no_convergio.py` (y si hace falta un segundo archivo, `scripts/verificar_recuperadas_real.py`), cada uno ≤ 200 líneas; salidas en `resultados/2026-10-02_reejecucion/`.
- No hagas commits ni `git checkout/switch/stash/reset`. Reporta `git status --short` al final.
- Nunca un comando de más de ~90 s en primer plano; todo lo largo con `nohup` y consultas cortas.
- Recalcula toda cifra del reporte desde los CSV; verifica que las tablas suman y que las etiquetas son correctas.
- Sin credenciales; no leer fuera de `D:\Desktop\ciclo_kalina_tercero`.

## Outputs

- `resultados/2026-10-02_reejecucion/reejecucion_filas.csv`, `verificacion_real.csv`, `progreso.log`.
- `REPORTE_REEJECUCION.md`, en lenguaje llano, formato: **La pregunta · Cómo funciona (en simple) · Cómo se hizo · Resultados** (tabla por barrido: NO_CONVERGIO originales únicos, recuperados, de ellos KALINA/CORREGIBLE/INVIABLE, siguen sin converger por causa; tabla del cruce con O5; tabla de la verificación real) **· Tiempos** (por fila y total, y cuántas cortó el presupuesto de 300 s) **· Conclusión · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- Todas las filas únicas del universo con resultado o causa registrada (o parada ordenada a las 6 h con lo hecho reportado).
- Cruce con O5 hecho.
- 10 filas verificadas con el motor real.

## Nota del director (2026-10-02, tras implementar MA): dependencia del estado del proceso

`resultados/2026-10-02_implementar_ma/diagnostico_fila15.txt` demostró que el resultado de un punto puede depender de lo que el mismo proceso calculó ANTES (cachés globales de arranque de los motores de propiedades): la fila `lit_bifasico` 10 falla con "punto interior no evaluable" en un proceso frío, y converge (mismo η que la referencia) si antes se calculó otro punto. Por tanto, en el paso 3:
- registra por fila el `pid` del worker y el número de orden de la fila dentro de ese worker;
- cuenta aparte las filas que terminan en "punto interior no evaluable";
- **no** cambies el método para "arreglarlo" (no reintentes en otro proceso, no limpies cachés): solo regístralo. El director decidirá después.

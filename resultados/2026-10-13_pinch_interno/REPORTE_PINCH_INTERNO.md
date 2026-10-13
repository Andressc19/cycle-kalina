# Corrección 4 — Pinch interno del regenerador, HRVG y condensador

**Fecha:** 2026-10-13 · **Rama:** `feature/solucion-4` · **Ejecutó:** OpenCode (log `logs/opencode/pinch_interno_run1.log`) · **Auditó:** Claude

## BLUF

**En los 131 puntos evaluados no aparece ningún cruce de temperaturas dentro del regenerador, el HRVG ni el condensador.** El acercamiento mínimo del regenerador es 4.45 K (un punto calibrado de Elsayed con ε_reg = 0.949); en los 100 puntos propios del proyecto es 4.79 K. Esto es una verificación posterior sobre puntos medidos con el cierre por efectividad, no una prueba de que el equipo sea realizable y no se extrapola a los 4 741 puntos.

- **Por qué no hay cruce (hallazgo estructural):** en 127 de 131 puntos el fluido frío llega al regenerador y sale de él **como líquido subenfriado** (T1 < T de burbuja a P_alta). La ebullición ocurre dentro del HRVG, no en el regenerador. Con ambos lados en líquido, la diferencia de temperatura baja casi linealmente de un extremo al otro y el mínimo cae en un extremo. Por eso en 130 de 131 puntos el mínimo está en el extremo frío (T6 − T10), que el criterio S4 ya comprueba; el interior no aporta un pinch nuevo.
- **El riesgo que sí existe** queda acotado: solo habría un tramo de ebullición dentro del regenerador si T1 ≥ T_burbuja, y eso pasa en 4 puntos del benchmark de Elsayed (por 0.2 a 0.7 K), que igual no cruzan.
- **Efecto en las conclusiones:** ninguna cambia. 0 de los 131 puntos evaluados dejan de ser "KALINA confiable". Corresponde a la opción (a): declararlo como limitación **verificada en n puntos**.

## 1. Qué se hizo (en lenguaje llano)

El motor cierra los intercambiadores con una efectividad ε, lo que asegura el balance de energía pero no revisa si las temperaturas se cruzan por dentro. Se tomó cada punto ya resuelto, se partió el calor del regenerador en 100 tramos y se calculó la temperatura de ambos lados en cada tramo, en contracorriente. El HRVG y el condensador, que van contra reservorios a temperatura constante (H8), se partieron en 40 tramos y se midió su acercamiento mínimo. Todo se hizo desde fuera del motor (`scripts/pinch_interno*.py`); no se tocó `src/`.

**Corrección respecto del encargo:** el texto pedía `h_f = h10 + f·(h1−h10)`, que empareja el extremo caliente de un lado con el frío del otro (cocorriente). Se usó contracorriente: `h_f = h1 − f·(h1−h10)`, con f medido desde el extremo caliente (donde entra 5 y sale 1).

## 2. Puntos evaluados (131; 0 sin convergir, 0 sin evaluar)

| Grupo | n | Cruce | Estrecho (< 5 K) | Pinch mín. [K] | Nota |
|---|---|---|---|---|---|
| A* (3.1) | 1 | 0 | 0 | 21.7 | |
| Óptimos 5.1 | 4 | 0 | 0 | 5.73 | la parte 5.1e no tiene punto confiable |
| Franja 4.2 | 8 | 0 | 0 | 21.5 | |
| Final 4.3 | 9 | 0 | 0 | 20.8 | ronda 3 completa (no 5) |
| Húsavík | 3 | 0 | 0 | 24.9 | |
| Estratificada 3.2 + 5.1 | 58 | 0 | 1 | 4.96 | 9 celdas ε_reg × ε_HRVG |
| Extremos (mayor ε_reg o ε_HRVG) | 17 | 0 | 3 | 4.79 | los 3 estrechos tienen T_fuente = 623 K |
| Elsayed (control positivo) | 27 | 0 | 6 | 4.45 | son 27, no 23 |
| Motor real (control) | 4 | 0 | 1 | 4.97 | |
| **Todos** | **131** | **0** | **11 (8.4 %)** | **4.45** | mediana 8.75 K |
| Propios, teqp (sin Elsayed) | 100 | 0 | 4 | 4.79 | mediana 19.2 K |

## 3. Cómo depende del ε_reg y del ε_HRVG (teqp, 127 puntos)

| ε_reg | n | Cruce | Estrecho | Pinch mín. [K] |
|---|---|---|---|---|
| 0.40–0.60 | 0 | — | — | sin puntos |
| 0.60–0.80 | 47 | 0 | 0 | 12.4 |
| 0.80–0.90 | 18 | 0 | 0 | 5.81 |
| 0.90–0.95 | 60 | 0 | 10 | 4.45 |
| > 0.95 (Elsayed calibrados) | 2 | 0 | 0 | 5.65 |

El pinch baja con ε_reg, como se espera, pero **no llega a cruzarse hasta ε_reg = 0.95** (y 0.961 en Elsayed). Con ε_reg ≥ 0.90 el 17 % de los puntos queda estrecho (< 5 K); los 11 estrechos tienen ε_reg ≥ 0.943. El ε_HRVG no ordena el pinch del regenerador (mínimo 4.45 K en 0.60–0.80 y 4.71 K en 0.80–0.90).

| Equipo | Resultado |
|---|---|
| HRVG | Acercamiento T_fuente − T2 mínimo = 1.30 K (ε_HRVG = 0.925); nunca negativo. En los 131 puntos el fluido hierve dentro del HRVG (T1 < T_burbuja < T2). |
| Condensador | Acercamiento T9 − T_sumidero mínimo = 1.68 K; nunca negativo. |

## 4. Control con el motor real

Los 4 puntos con el motor real (≈ 1 000–1 400 s cada uno) coinciden con su par teqp en el pinch del regenerador dentro de 0.015 K (A*: −0.004 K; óptimo 5.1a: −0.002 K; Húsavík: −0.015 K; est_20_9: +0.007 K). Misma clase en los cuatro.

## 5. Lo que OpenCode reportó y no es correcto

OpenCode dijo que `cond_min_K` era negativo en varios puntos. **No es así:** en el CSV es positivo en los 131 (mínimo 1.68 K). Probablemente confundió el mínimo de la columna con un signo de la salida. Los 11 puntos "estrechos" sí son correctos.

## 6. Lo que no se pudo verificar

- **Fuente y sumidero finitos:** se mantiene H8 (reservorios isotermos), por decisión del 2026-10-06. Contra un reservorio el HRVG y el condensador no pueden cruzarse por construcción; el chequeo real de 2.º orden (gases con capacidad finita) queda como limitación.
- **Cobertura:** 131 puntos (100 propios + 27 de Elsayed + 4 reales), no los ~1 340 KALINA confiables. No hay puntos con ε_reg < 0.60 porque 3.2 y 5.1 no tienen KALINA confiable ahí; ver la ronda corta de la sección 6b.
- **Una irregularidad sin explicar:** en el perfil del lado caliente de A* hay un pequeño quiebre cerca de f ≈ 0.97 (ver `pinch_regenerador.png`). Ocurre con ΔT ≈ 21 K, así que no afecta la conclusión, pero conviene revisarlo con `perfiles_todos.csv` si se quiere citar el perfil.
- **Discretización:** 100 tramos. Como el mínimo cae en el extremo, no depende de la resolución en estos puntos.
- Los avisos de runtime del motor (`overflow in exp`, `divide by zero in log`) no afectaron a los resultados; no se investigaron.

## 6b. Ronda corta con ε_reg < 0.60 (10 puntos construidos)

Se tomaron 5 puntos ya medidos (A*, óptimos 5.1a y 5.1b, franja 4.2 a 410 K con ε_cond 0.95, Húsavík `husavik_2`) y se cambió **solo** ε_reg a 0.40 y 0.55 (teqp, 236 s). **No son KALINA confiables**: es una comprobación del pinch, no un estudio nuevo.

| ε_reg | n | Cruce | Estrecho | Pinch del regenerador [K] |
|---|---|---|---|---|
| 0.40 | 5 | 0 | 0 | 47.5 – 63.1 |
| 0.55 | 5 | 0 | 0 | 37.0 – 49.0 |

El mínimo cae siempre en el extremo frío (pos_f = 1) y el fluido frío sale subenfriado (T1 < T_burbuja) en los 10. Con ε_reg bajo el pinch es amplio, como se espera: no hay riesgo en ese rango. Archivos en `bajo_ereg/`. OpenCode corrió el comando en bash (no PowerShell) con la traducción mínima de sintaxis.

## 7. Texto propuesto (NO editado en el entregable; requiere tu aprobación)

**§6.2 / §7 — nuevo criterio de verificación posterior "C-P: pinch interno".**
> Tras resolver cada punto se discretizó el regenerador en 100 tramos en contracorriente y se calculó ΔT(f) = T_c(f) − T_f(f). El punto se considera con cruce si ΔT ≤ 0 en algún tramo, y estrecho si el mínimo es < 5 K. En el HRVG y el condensador, contra reservorios isotermos, se reporta el acercamiento mínimo. Este chequeo es un post-proceso: no forma parte del clasificador.

**§13.2 — "Cierre por efectividad sin verificación del perfil interno".**
> Verificado en 131 puntos (100 del proyecto, 27 del benchmark de Elsayed y 4 con el motor real). Resultado: sin cruce interno bajo el cierre por efectividad; pinch mínimo del regenerador 4.45 K (4.79 K en los puntos del proyecto), con 11 puntos estrechos (< 5 K), todos con ε_reg ≥ 0.94. En estos puntos el fluido frío sale del regenerador subenfriado, por lo que el mínimo cae en el extremo frío. Queda sin verificar: fuente y sumidero de capacidad finita (H8) y puntos con ε_reg < 0.60.

**Conclusiones afectadas:** ninguna cambia. Donde se hable de "KALINA confiable" puede añadirse una frase: "sin cruce interno en los 131 puntos verificados". No se afirma realizabilidad física.

## 8. Recomendación

(a) **Declararlo como limitación verificada** (texto de §7). (b) Sumar C-P al clasificador tocaría `src/` y hoy no cambiaría ninguna clasificación: solo se justificaría si en el futuro aparecen puntos con T1 ≥ T_burbuja, que es la única condición donde el regenerador tendría ebullición interna. **Solo propuesta, no implementada.**

## 9. Archivos

`pinch_puntos.csv` (131 filas) · `perfiles_todos.csv` (183 filas por punto) · `perfiles_ejemplo.csv` · `pinch_resumen.csv` · `pinch_regenerador.png` · `stdout_*.txt` · `humo/`. Scripts: `scripts/pinch_interno.py`, `pinch_interno_muestra.py`, `pinch_interno_reporte.py`; orden en `prompts/TASK_CONTEXT_pinch_interno.md`.

# Corrección del solver: bracket tolerante (MA)

Fecha: 2026-10-03 · Rama `fix/solver-bracket-tolerante` · Código: `src/_bracket_tolerante.py`, `src/cycle_solver.py` (`bracket_tolerante=True`) · Tests: `tests/test_bracket_tolerante.py`.
Resultados completos: `resultados/2026-10-02_reejecucion/REPORTE_REEJECUCION.md` y carpetas `resultados/2026-09-30_arranque_solver` … `2026-10-02_implementar_ma`.

---

## 1. El fallo

Muchos puntos de los barridos salían `NO_CONVERGIO` aunque el ciclo sí tenía solución: eran **falsos negativos**.

**Causa:** el lazo exterior busca T1 (entrada al HRVG) con Brent entre `T_sumidero + 1` y `T_fuente − 1`. Para arrancar, evalúa el ciclo en esos dos extremos. Si el motor de propiedades no puede calcular un extremo (`PropertyRangeError`, por ejemplo una zona de dos fases que el motor no cubre), el solver se rendía de inmediato. No probaba un poco más adentro del rango, donde sí había solución.

**Cuántos:** 796 puntos únicos `NO_CONVERGIO` en 17 CSV de barridos.

## 2. La solución

Con `resolver_ciclo(..., bracket_tolerante=True)` (modo **MA**, "siempre tolerante"):

- **Repliegue de extremos:** si un extremo no se puede evaluar, se corre 5 K hacia dentro y vuelve a probar, sin tope de intentos, hasta tener dos extremos evaluables.
- **Arranque tibio:** la primera evaluación del lazo interior parte de `T10 = T_sumidero + 5 K`.
- **Presupuesto de tiempo opcional:** `presupuesto_s` en segundos, comprobado entre evaluaciones del ciclo.
- **Diagnóstico:** la salida incluye la clave `bracket` (`lo`, `hi`, `repliegues_lo`, `repliegues_hi`, `nF`).
- **Apagado por defecto:** con `bracket_tolerante=False` el código hace exactamente lo de antes. Hay un test que lo comprueba bit a bit.

No cambia ninguna fórmula, criterio físico ni clasificación.

**Cómo se llegó a MA:**
1. Sondas confirmaron que la causa estaba en los extremos.
2. Una ablación midió tiempos.
3. Un benchmark comparó MA y MB. Ambos recuperan lo mismo; se eligió MA por tiempo. Los topes de repliegue perdían recuperaciones.
4. Se escribieron los tests primero, luego se implementó y verificó con 18 controles.

## 3. Resultados

| | Puntos |
|---|---|
| Universo `NO_CONVERGIO` (únicos) | 796 |
| Convergen con MA | 580 |
| — soluciones falsas, atrapadas por N2 | 20 |
| **Recuperados de verdad** | **560 (70.4 %)** |
| — KALINA / CORREGIBLE / INVIABLE | 9 / 544 / 7 |
| Siguen sin converger | 216 |

- La Fase 1 (profesor) sigue en 0 recuperados: la mezcla sale sobrecalentada de verdad, coherente con O5.
- Verificación con el motor riguroso (`AmmoniaWaterAdapter`):
  - 3 KALINA, 6 CORREGIBLE, 10 CORREGIBLE de Fase 2 y 10 de cementera. Las muestras de Fase 2 y cementera se tomaron con paso uniforme.
  - Además, 7 puntos espurios, que reproducen igual.
  - **Entre los puntos válidos: 16 confirmados (|Δη|/η ≤ 0.022 %, misma clase), 4 sin resultado (el motor riguroso falla dentro de la búsqueda), 0 contradichos.**
- Tiempo: 796 puntos en 4 h 32 min con 6 procesos. Media de 123 s por punto con teqp. El motor riguroso tarda de 6 a 32 min por punto.

**Nota de evaluación del director: 8/10.** Se atacó la causa real sin tocar la física, se probó antes de aplicarlo, no rompe nada y lo recuperado es verdadero. No es 10 por lo que queda en el aire (sección 5).

## 4. Análisis final (revisión de tres miradas, previa al merge)

### Cómo se revisó
1. Lectura línea por línea de `src/_bracket_tolerante.py` y del cambio en `cycle_solver.py`, contra el código original.
2. Suite completa: 198 passed, 1 skipped, 8 xfailed antes de la simplificación. Después de la simplificación: **196 passed, 1 skipped, 8 xfailed**; los 2 tests retirados solo probaban los parámetros eliminados.
3. Todas las cifras se recalcularon desde los CSV y coinciden: 796, 580, 20 espurias con N2, 9 KALINA, 544 CORREGIBLE, 7 INVIABLE, y las cuatro verificaciones con el motor riguroso.

### Las soluciones, una por una

| Solución | ¿Se usó? | ¿Aporta? | Veredicto |
|---|---|---|---|
| Replegar 5 K los extremos no evaluables | Sí | Sí: recupera 560 puntos | ✅ Núcleo; se queda |
| Arranque del lazo interior en T_sumidero + 5 K | Sí | Sí (ablación de tiempos) | ✅ Se queda |
| `presupuesto_s` | Sí, con 300 s | Parcial: cortó 4 puntos, no los 2 más lentos | ⚠️ Útil, incompleto |
| `max_repliegues` (tope) | No | Ninguno: los topes perdían puntos | ❌ Peso muerto → **retirado** |
| `paso_repliegue` | No; siempre 5 K | Ninguno | ❌ Peso muerto → **retirado** (constante `PASO_REPLIEGUE`) |
| Clave `bracket` en la salida | Sí | Sí: diagnóstico por punto | ✅ Se queda |
| Modo MB y salida temprana | Descartados | — | ✅ No entraron al código |

### Mirada optimista
- El 70 % de los `NO_CONVERGIO` eran falsos negativos y se recuperan.
- Apagado por defecto, con resultado idéntico bit a bit: el merge no puede romper nada.
- 10 puntos de control dan el mismo η (diferencia < 5e-7).
- Cuando el motor riguroso logra calcular, coincide con teqp (diferencias ≤ 0.022 %).
- N2 atrapa las 20 soluciones falsas.

### Mirada crítica

**Fallos o huecos en el código:**
1. **Sin ensanche final.** Al no encontrar cambio de signo, MA se rinde; el código original ensanchaba una vez más, hasta casi `T_sumidero`/`T_fuente`. Por física es inocuo: T1 no puede quedar a menos de 1 K del sumidero, por el condensador con eps < 1 y la bomba. No se pudo medir, porque los CSV de barridos no guardan T1. **Ahora está documentado en el docstring.**
2. **Tramo no evaluable en medio del rango.** Si Brent cae en una zona que el motor no cubre, MA se rinde ("punto interior no evaluable"). Explica 67 de los puntos que siguen perdidos y los 4 fallos del motor riguroso. Es la mayor pérdida restante.
3. **Solo tolera `PropertyRangeError`.** Si el lazo interior no converge en un extremo, MA no repliega. Es decisión de diseño y cuesta pocos puntos.
4. **`nF` no cuenta las evaluaciones fallidas.** El mensaje de "presupuesto agotado" muestra menos trabajo del real. Es menor.
5. **El presupuesto no corta una evaluación lenta.** Dos puntos tardaron 848 s y 1534 s dentro de una sola evaluación: el lazo interior agotó sus 300 iteraciones.
6. **Dependencia del estado del proceso.** Un mismo punto puede dar distinto según lo calculado antes en el mismo proceso (cachés de los motores). Está registrado (`pid`, orden) pero no analizado. Es el riesgo de reproducibilidad más serio. Uno de los fallos del motor riguroso ocurrió en un extremo que teqp sí evaluó.

**¿Son justas las comparaciones?**
- ✅ Las muestras de Fase 2 y cementera son de paso uniforme, no se eligieron a mano.
- ⚠️ La primera muestra (10 puntos) quedó sesgada hacia soluciones falsas. Está documentado y se compensó con otras 26.
- ⚠️ Teqp y el motor riguroso usan el mismo solver. Que coincidan prueba que los motores concuerdan, no que la solución sea la única físicamente posible.
- ⚠️ Lo honesto es "16 confirmados, 4 sin confirmar, 0 contradichos", no "16 de 16".
- ⚠️ De las 9 KALINA:
  - Solo 3 se verificaron con el ciclo completo en el motor riguroso.
  - 2 no pasan la verificación B (Δh4s ≈ −2.2 kJ/kg frente a un umbral de 2.0).
  - 3 tienen η de 0.8–1.9 % (P_baja muy cerca de P_alta).
  - 3 tienen x_b de 0.35–0.475.
  - Cumplen los criterios, pero tienen poco valor práctico.

### Mirada neutral
La corrección hace lo que promete y no rompe nada. Lo pendiente son mejoras posibles, no errores.

### Conclusión
**La corrección es adecuada y no se encontraron fallos que la invaliden.** Suma de verdad: 560 puntos recuperados, 0 resultados contradichos, 0 cambios cuando está apagada. Los dos detalles que impedían decir "sin fallos" quedaron resueltos antes del merge (commit `a407628`): el ensanche eliminado está documentado y los dos parámetros de peso muerto fueron retirados.

## 5. Lo que quedó en el aire

| Pendiente | Por qué importa | Propuesta |
|---|---|---|
| 216 puntos siguen sin converger: 78 sin cambio de signo, 67 punto interior no evaluable, 61 sin extremos evaluables, 6 otros, 4 por presupuesto | Unos 67 probablemente también son falsos negativos | Estrategia para fallos interiores, por ejemplo acortar el bracket por el lado evaluable |
| Dependencia del estado del proceso | Reproducibilidad | Analizar con los `pid` y el orden ya registrados en `reejecucion_filas.csv` |
| El presupuesto no corta evaluaciones lentas | Barridos largos | Presupuesto dentro del lazo interior o menos iteraciones |
| 4 puntos sin resultado con el motor riguroso (3 de cementera, todos con `eps_hrvg` = 0.65) | No se sabe si son reales | Revisar más puntos con ese valor |
| 6 KALINA de Fase 2 sin verificación de ciclo completo con el motor riguroso | Son el resultado de mayor interés | Verificarlas |
| Incorporar los resultados a los CSV/Excel de barridos | Hoy viven solo en `reejecucion_filas.csv` | Columna nueva, sin sobrescribir los originales |
| `bracket_tolerante` está apagado por defecto | Los barridos nuevos no lo usan si no se pide | Decidir si los scripts de barrido lo activan |

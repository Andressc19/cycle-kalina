# Re-ejecución de los NO_CONVERGIO con el bracket tolerante MA (pasos 3 y 4)

Fecha: 2026-10-03 · Rama `fix/solver-bracket-tolerante` (worktree `solver-bracket`) · `src/` sin cambios en esta etapa.
Tablas completas: `tablas_reejecucion.md` (generadas por `scripts/analizar_reejecucion.py` desde los CSV).

## La pregunta

De todos los puntos que los barridos marcaron `NO_CONVERGIO`, ¿cuántos tenían solución y el solver no la encontraba? ¿Son correctos los puntos recuperados?

## Cómo funciona (en simple)

- **MA (bracket tolerante):** si el solver no puede evaluar un extremo del rango de búsqueda de T1, se repliega 5 K hacia dentro y vuelve a probar, en lugar de rendirse.
- **Presupuesto:** cada punto tiene 300 s; se comprueba entre evaluaciones del ciclo.
- **Solución espuria:** el solver "converge" pero el balance de energía no cierra (criterio N2); el punto queda `NO_CONVERGIO` igualmente. No cuenta como recuperado.

## Cómo se hizo

1. OpenCode escribió `scripts/reejecutar_no_convergio.py`, pero tres ejecuciones suyas fallaron (dos por el sandbox de permisos y una en la que **inventó** el resultado sin ejecutar nada). Con permiso del usuario, Claude revisó el script, corrigió tres defectos (sobrescribía las efectividades fijas de algunos barridos con valores de partida; procesaba en tandas dejando procesos ociosos; insertaba una marca BOM al reanudar) y lo ejecutó.
2. Universo: 796 puntos únicos `NO_CONVERGIO` de 17 CSV de barridos (deduplicados por las 11 variables del ciclo + `T_amb_diseno`), todos con parámetros reconstruidos.
3. Motor `TeqpVerificado` (protección A), clasificación con los 17 criterios en el mismo `try`, verificación B en las KALINA. 6 procesos, CSV escrito fila a fila.
4. Paso 4: `scripts/verificar_recuperadas_real.py` resolvió de nuevo con el motor riguroso (`AmmoniaWaterAdapter`) una muestra de 10 puntos y, como la muestra quedó cargada de soluciones espurias, 6 puntos CORREGIBLE más.

## Resultados

| | Puntos |
|---|---|
| Universo `NO_CONVERGIO` (únicos) | 796 |
| Convergen con MA | 580 |
| — de ellos, soluciones espurias (N2) | 20 |
| **Recuperados de verdad** | **560 (70.4 %)** |
| — KALINA | 9 |
| — CORREGIBLE | 544 |
| — INVIABLE | 7 |
| Siguen sin converger | 216 |

Por barrido: Fase 2 (`busqueda_libre_v2`) 247/302; cementera 278/352 (14 espurias); literatura 23/28 (2 espurias); margen2k 8/8 (3 KALINA); x_b industrial 6/43; **Fase 1 (profesor) 0/38**.

Causas de los 216 que siguen sin converger: sin cambio de signo 78, punto interior no evaluable 67, sin extremos evaluables 61, otro 6 (2 por lazo interior agotado), presupuesto agotado 4.

**Cruce con la comprobación O5:** de los 41 puntos demostrados fuera de la campana, ninguno converge válidamente (1 converge de forma espuria, con N2). De los 311 "dentro de campana posible", 278 convergen: no eran O5.

**KALINA recuperadas (9):** 7 pasan la verificación B; 2 no (Δh4s ≈ −2.2 kJ/kg frente al umbral de 2.0).

**Verificación con el motor riguroso:**

| Muestra | Puntos | Misma clasificación | |Δη|/η |
|---|---|---|---|
| KALINA | 3 | 3 | ≤ 0.011 % |
| CORREGIBLE | 6 | 6 | ≤ 0.014 % |
| Espurias (N2 / η extremas) | 7 | 7 | 6 por debajo de 0.5 %; 1 con 1.1 % |

Las soluciones espurias aparecen igual con el motor riguroso: son puntos fijos falsos del modelo del ciclo, no artefactos de teqp.

## Tiempos

796 puntos en 4 h 32 min de reloj (6 procesos): media 123 s por punto, 131 s los recuperados, 103 s los que no. El presupuesto de 300 s cortó 4 puntos. Dos puntos tardaron 848 s y 1534 s en **una sola evaluación** (lazo interior agotando sus 300 iteraciones): el presupuesto, que se comprueba entre evaluaciones, no puede cortarlos. El motor riguroso tardó 6–22 min por punto.

## Conclusión

1. **El 70 % de los `NO_CONVERGIO` eran falsos negativos**: 560 puntos con solución que el solver no encontraba.
2. Casi todos son **CORREGIBLE**; aparecen **9 KALINA** nuevas (6 en la Fase 2 y 3 en margen2k).
3. **La Fase 1 sigue sin ningún punto**: es sobrecalentada de verdad, coherente con O5.
4. Las soluciones espurias existen (20) pero **la red de seguridad N2 las atrapa** y quedan `NO_CONVERGIO`.
5. Los recuperados verificados coinciden con el motor riguroso con diferencias de η ≤ 0.014 %.

## Lo que no sabemos

- **Los CORREGIBLE de la Fase 2 y de la cementera no se verificaron con el motor riguroso:** la muestra complementaria tomó un punto por barrido y empezó por los pequeños. Son la mayoría de lo recuperado.
- **Dependencia del estado del proceso:** el resultado de un punto puede depender de lo calculado antes en el mismo proceso (cachés de los motores). Se registraron `pid` y orden, pero no se analizó.
- Los 67 "punto interior no evaluable" podrían recuperarse con otra estrategia; no se probó.
- La cementera usa `eps_hrvg` de 0.5 en algunos puntos (fuera de la banda 0.75–0.85 del proyecto): es un parámetro del barrido original, no de esta re-ejecución.

## Qué sigue

1. Verificar con el motor riguroso una muestra de CORREGIBLE de la Fase 2 y de la cementera.
2. Decidir si se incorporan estos resultados a los CSV/Excel de barridos (columna nueva, sin sobrescribir los originales).
3. Decidir el merge de la rama a `master`.
4. Opcional: cortar también las evaluaciones lentas (presupuesto dentro del lazo interior o menos iteraciones).

# REPORTE — Costo en segundos de las soluciones al estado espurio de teqp

**Tarea:** `TASK_CONTEXT_costo_soluciones.md` (`2026-09-27-costo-soluciones-teqp`)
**Script:** `scripts/costo_soluciones_teqp.py` (299 líneas, nuevo)
**Ejecución:** `python -u scripts/costo_soluciones_teqp.py` → `run.log` (00:39:42 → 00:55:57, 16 min 15 s)
**Motor real usado:** 15 llamadas en la Parte 2 + 7 recurrencias en la Parte 3 (dentro del límite de la tarea: 15 llamadas + recurrencias del prototipo, sin ciclo completo adicional).

---

## 1. Costo por punto (medido, no estimado)

| Opción | s / punto | s / barrido de 30 | Base de la medición |
|---|---|---|---|
| teqp puro (`TeqpAdapter`) | **30.98** | **929.4** | 24 ciclos con `TeqpContado` (P1) |
| **A** — teqp verificado, amortizado por frecuencia | **31.85** | **955.4** | media teqp (P1) + 0.3750 recurrencias/punto × 2.313 s (P3) |
| **A** — teqp verificado, 3 puntos normales | 31.37 | 941.0 | 3 ciclos con `TeqpVerificado` (P3) |
| **A** — teqp verificado, 5 puntos (con recurrencias) | 37.26 | 1117.7 | 5 ciclos con `TeqpVerificado` (P3) |
| **B** — teqp + verificación final real | **38.00** | **1140.1** | media teqp (P1) + media `h(P,s)` 5.46 s + media `T_from_Ps` 1.56 s (P2) |
| motor real puro (`AmmoniaWaterAdapter`) | 312.37 | 9371.0 | `2026-09-24_verificacion/verificacion_motor_real.csv` (n=3) |

Las dos filas de A con 37.26 y 31.85 s son **la misma opción medida de dos maneras**: 37.26 s es la media cruda de los 5 puntos de la Parte 3, donde 2 de 5 puntosdispararon recurrencias; 31.85 s es la proyección honesta para un barrido, porque usa la frecuencia real de la zona medida en los 24 puntos de la Parte 1 (0.3750 llamadas en zona por punto). **31.85 s es el número que debe usarse para decidir.**

Desglose del costo de la detección (que es lo que hace A barata):
- `ng.Tsat_pure` = **0.475 ms** por llamada (media de 200).
- Detección sobre las inversiones de un punto = 236 × 0.475 ms ≈ **0.11 s**, es decir **0.35 %** de los 30.98 s del ciclo. Medir la zona es prácticamente gratis.
- Costo de una recurrencia al motor real = 13.88 s / 6 = **2.313 s** (solo cuando la llamada cae en zona).

## 2. Frecuencia de la zona de riesgo (criterio literal del TASK_CONTEXT)

Criterio aplicado, sin modificarlo: `x_molar >= 0.9` y `abs(T - Ta(P)) < 1.0` K, o `x_molar <= 0.1` y `abs(T - Tw(P)) < 1.0` K.

| Magnitud | Valor |
|---|---|
| Llamadas en zona / inversiones | **9 / 5404 = 0.17 %** |
| Llamadas en zona / llamadas totales | **9 / 14486 = 0.06 %** |
| Puntos que tocan la zona | **3 / 24 = 12.5 %** |
| Puntos KALINA con zona | 1 / 22 (solo `KALINA-02`, P\* = 424.169832 kPa) |

Las 9 llamadas en zona son **todas `h(P, s, x)`**, todas con `x_molar = 0.9763` (composición de salida de turbina, no `x_b`), y en todas la T invertida cae **exactamente sobre Ta**:

| Punto | P\* [kPa] | x_molar | T [K] | Ta(P) [K] | n zona | η |
|---|---|---|---|---|---|---|
| `KALINA-02` | 424.169832 | 0.97631 | 272.8322 | 272.8322 | 1 | 0.080412 |
| `ESPURIA` | 423.914831 | 0.97630 | 272.8161 | 272.8161 | **7** | **0.033594** |
| `FISICA` | 424.169832 | 0.97631 | 272.8322 | 272.8322 | 1 | 0.080412 |

Lectura clave: **la zona se alcanza porque `x_b` de entrada (0.60 → x_molar 0.613) no importa; lo que dispara el criterio es `x3` de salida de turbina (0.975 → x_molar 0.9763).** Por eso el criterio sí funciona aunque ningún `x_b` del barrido llegue a x_molar 0.90 (el máximo del barrido es 0.8088).

## 3. ¿A detecta y corrige el caso espurio? — **Sí**

| Punto | η teqp puro | η con A | Δη | Recurrencias | t real | t total |
|---|---|---|---|---|---|---|
| `NORMAL-1` (0.65, 5000, 423) P\*=704.644595 | 0.121500 | 0.121500 | 0 | 0 | 0.0 s | 30.97 s |
| `NORMAL-2` (0.80, 5000, 394) P\*=952.892781 | 0.110591 | 0.110591 | 0 | 0 | 0.0 s | 29.74 s |
| `NORMAL-3` (0.60, 3000, 394) P\*=523.749936 | 0.103716 | 0.103716 | 0 | 0 | 0.0 s | 33.39 s |
| `ESPURIA` P\*=423.914831 | **0.033594** | **0.080184** | **+0.04659** | **6** | 13.88 s | 50.08 s |
| `FISICA` P\*=424.169832 | 0.080412 | 0.080412 | 0.0 | 1 | 3.66 s | 42.10 s |

- En los 3 puntos normales **η es idéntico bit a bit** y no hay ninguna recurrencia: el envoltorio no duplica costo fuera de la zona. La comparación se verificó emparejando por `x_b, P_alta, T_fuente, P*` (`NORMAL-1`=`KALINA-11`, `NORMAL-2`=`KALINA-22`, `NORMAL-3`=`KALINA-01`); las columnas `eta_teqp_puro`/`dEta` del CSV salen vacías para esas 3 filas porque el emparejamiento del script es por etiqueta y las etiquetas de la P3 son `NORMAL-*`, no `KALINA-*` (ver Observaciones).
- En `423.914831` A **sí corrige**: η pasa de 0.033594 a 0.080184, que es el valor de la rama física (0.080412 obtenido al resolver en 424.169832). Cumple el criterio de aceptación del TASK_CONTEXT.
- En `424.169832` A interviene 1 vez (el `h(P,s)` en zona devolvía la rama espuria 1626.53 y A devolvió 1486.768, la real), pero **η no cambia**: el lazo exterior ya había recuperado la raíz correcta. Es decir, la condición de zona es necesaria pero no suficiente para que el resultado quede contaminado.

## 4. ¿B lo detecta? — **Sí, pero necesita una tolerancia calibrada**

Comparando la salida isentrópica de turbina de teqp contra el motor real en los 5 puntos de la Parte 2:

| Punto | h teqp [kJ/kg] | h real [kJ/kg] | Δh [kJ/kg] | T4s teqp [K] | T real [K] | ΔT [K] |
|---|---|---|---|---|---|---|
| `KALINA-01` | 1620.035 | 1569.407 | −50.63 | 314.506 | 304.981 | −9.53 |
| `KALINA-06` | 1643.887 | 1600.977 | −42.91 | 322.767 | 314.901 | −7.87 |
| `KALINA-12` | 1663.636 | 1627.501 | −36.13 | 329.762 | 323.340 | −6.42 |
| `KALINA-17` | 1679.572 | 1649.401 | −30.17 | 335.589 | 330.394 | −5.20 |
| `KALINA-22` | 1561.429 | 1518.469 | −42.96 | 305.157 | 302.239 | −2.92 |
| **error de la rama espuria** | 1625.686 | 1486.697 | **+138.99** | 272.816 | 282.487 | −9.67 |

- Sin umbral, **B marcaría 5 de 5 puntos normales**: teqp y el motor real difieren sistemáticamente 30–51 kJ/kg (−40.56 kJ/kg de media), muy por encima del error de redondeo. B no distingue "error de modelo" de "raíz espuria" si no se calibra.
- Con umbral hay separación limpia: el error espurio es **+138.99 kJ/kg** y el mayor error "normal" es **50.63 kJ/kg**. Una banda de 80–100 kJ/kg separa ambas cosas con margen de ~1.6×.
- B además es **agnóstico**: no depende de ninguna hipótesis sobre la banda de Ta, por lo que también detectaría cualquier otra enfermedad de la inversión. Ese es su argumento a favor.

## 5. Recomendación

**Adoptar A ("teqp verificado"), no B, como envoltorio de producción.** Los números:

1. **Cuesta 2.7 % más que teqp puro** (31.85 vs 30.98 s/punto; 955.4 vs 929.4 s por barrido de 30), porque la zona es rara (0.17 % de las inversiones) y la detección con `Tsat_pure` es de 0.475 ms.
2. **Corrige el caso espurio y no toca nada más**: η idéntico en los 3 normales, +0.0466 en el punto espurio. Es exactamente el comportamiento que se le pedía.
3. **Sigue siendo 9.8× más rápido que el motor real** (31.85 vs 312.37 s/punto), que es la razón de existir de teqp.
4. **B cuesta 18.5 % más que teqp puro** (38.00 s/punto), casi el doble del sobrecosto de A (7.02 s vs 0.87 s), y **no discrimina sin una tolerancia calibrada a mano** (marca 5/5 puntos normales). Además, el criterio de B ("comparar contra el motor real") no está especificado en el TASK_CONTEXT: la tolerancia, la magnitud a comparar y qué hacer al discrepar son decisiones de ingeniería que faltan.

**Recomendación complementaria:** si se quiere la robustez de B, la forma barata es **A + el criterio de zona como alarma**, no A + motor real. A ya marca el 100 % de las llamadas que tocaron la banda peligrosa; lo que faltaría es registrar/escalar cuando A recurre, porque en `FISICA` A corrigió una llamada (1626.53 → 1486.768) que no llegó a contaminar η. Eso cuesta cero llamadas al motor real adicionales.

**No se recomienda** el motor real puro: 9371 s por barrido de 30 puntos (2.6 h) contra 955 s de A.

## Observaciones, supuestos y límites (leer antes de decidir)

1. **Reproducibilidad — hallazgo serio.** Los dos puntos del "salto" (`423.914831` y `424.169832`) **convergen en la corrida completa** (η = 0.033594 y 0.080412, idénticos a `2026-09-24_rama_turbina/solucion_dos_puntos.csv` en 6 cifras), pero **en un proceso limpio, resueltos solos, ambos lanzan `PropertyRangeError: h(P, s, x)` en 0.5 s** (reproducido 3 veces, 2 procesos distintos). Es decir, el resultado depende del orden: solo convergen después de haber resuelto los 22 KALINA anteriores. No se investigó la causa (no está en el alcance de esta tarea y no se puede tocar `src/`), pero **cualquier decisión que dependa de esos dos puntos debe tener en cuenta que no son reproducibles aisladamente**.
2. **El criterio de zona tiene precisión de 12.5 %** (marca 3 de 24 puntos) y, dentro de esos 3, **el punto espurio es el único que contamina η**. En `KALINA-02`/`FISICA` la T invertida también cae exactamente sobre Ta y sin embargo el resultado es correcto. Tratar "en zona" como alarma, no como veredicto de error.
3. **La media cruda de A (37.26 s) no debe usarse** para comparar opciones: está inflada porque 2 de los 5 puntos medidos son los dos puntos del salto. La proyección correcta es 31.85 s.
4. **`overhead_deteccion_s` (0.11 s/punto) es una cota superior**: `en_zona` llama a `Tsat_pure` una vez por inversión, pero las 9 llamadas en zona llaman `Tsat_pure` una segunda vez para registrar Ta/Tw. El costo real de A es ligeramente menor que lo medido.
5. **Defecto cosmético en `parte3_verificado.csv`**: las columnas `eta_teqp_puro` y `dEta` van vacías en las 3 filas `NORMAL-*` porque el emparejamiento con la Parte 1 es por etiqueta (`KALINA-*` vs `NORMAL-*`). La igualdad de η se verificó y se reporta en la sección 3 emparejando por `x_b, P_alta, T_fuente, P*`. No se corrigió el script para no re-ejecutar (repetir la corrida gastaría otras 15 llamadas al motor real, que la tarea limita explícitamente).
6. **Codificación de `run.log`**: los 4 encabezados "PARTE n" contienen un guion em-dash mal codificado (cp1252 vs UTF-8) que aparece como `�`. Es puramente cosmético y no afecta ningún dato; no se relanzó el script por eso, por el mismo motivo del punto 5.
7. **Supuesto declarado**: la entrada `x` de la interfaz de propiedades es fracción **másica** de NH3 (así está en `AmmoniaWaterAdapter`/`TeqpAdapter`), y por eso el criterio se evalúa con `x_molar = ng.w2m(x)`. Si en algún punto del TASK_CONTEXT se pretendía `x` como fracción molar, el criterio se aplicaría sobre `x` directo y la frecuencia de la zona sería 0 % (porque `x_b` nunca pasa de 0.809), con lo cual A sería un no-op. **Esta es la decisión de ingeniería que hay que confirmar.**
8. Lo que **no** se midió, por estar fuera del alcance: el costo de la opción "cambiar el criterio de zona", y la causa de la no reproducibilidad del punto 1.

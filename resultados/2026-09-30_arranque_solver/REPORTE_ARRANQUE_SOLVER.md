# Sonda de arranque del solver — falsos `NO_CONVERGIO`

**Tarea:** `2026-09-30-arranque-solver-falsos-negativos` · **Fecha:** 2026-10-01
**Script:** `scripts/sonda_arranque_solver.py` (200 líneas) · **Datos:** `sonda_filas.csv` (56 filas × 60 columnas)
**Backend:** `TeqpVerificado` (opción A de `CONTEXT.md`) en las tres variantes.
**Reproducir:** `.venv\Scripts\python -u scripts/sonda_arranque_solver.py` (6 workers, ~31 min de reloj de pared).

---

## 1. Conclusión: **H1 CONFIRMADA**

De **46 filas marcadas `NO_CONVERGIO`** en los CSV originales, 40 fallaban de verdad
y la sonda rescata **28 de esas 40 (70 %)**:

- **3** con solo el warm start (V1).
- **25** solo con el bracket tolerante (V2), sin necesitar V1.
- **12** no se pueden rescatar (ver §6).

Las otras 6 ya convergían con V0: su `NO_CONVERGIO` original venía del barrido con
otro backend o de la calibración de `eps`, no del arranque del solver.

De las 12 no rescatadas, 11 fallan por una razón distinta y ya identificada (ausencia
real de par bífásico, `F` sin cambio de signo en todo el rango físico, o punto
interior no evaluable); **solo 1** llega a clasificarse y sigue siendo
`NO_CONVERGIO` de forma físicamente correcta (`eta = -0.4496`: el punto de trabajo
no produce trabajo neto).

**Ninguna fila de la muestra empeoró al aplicar V1 o V2.** El mecanismo dominante
**no es el arranque frío**: es la evaluación de los **extremos del bracket** en
`_bracketear`.

| Grupo `NO_CONVERGIO` | Filas | V0 falla | Rescata V1 | Rescata V2 (solo) | Sin rescatar |
|---|---|---|---|---|---|
| FASE2 `T_from_Ph` | 15 | 15 | 0 | 11 | 4 |
| FASE2 `h(P, s, x)` | 5 | 5 | 0 | 1 | 4 |
| Literatura `T_from_Ph` | 19 | 13 | 3 | 10 | 0 |
| Literatura bifásico | 7 | 7 | 0 | 3 | 4 |
| **Total** | **46** | **40** | **3** | **25** | **12** |

Las 6 restantes (literatura `T_from_Ph`) ya convergían con V0.

## 2. Dónde falla exactamente (instrumentación V0)

Sobre las 40 filas donde V0 lanza `PropertyRangeError`:

| Punto de la cascada | Filas | Interpretación |
|---|---|---|
| `abs.T8` | 18 | `T_from_Ph` en el absorbedor |
| `sep.ELV` | 8 | equilibrio líquido-vapor en el separador |
| `hrvg.T2` | 5 | `T_from_Ph` en el regenerador |
| `turb.h4s` | 4 | `h(P, s, x)` en la turbina |
| `valv.T7` | 4 | `T_from_Ph` en la válvula |
| `bom.h10s` | 1 | `h(P, s, x)` en la bomba |

**Ubicación del fallo en el bracket:** 25 en `extremo_hi`, 12 en `extremo_lo`, 3 en
`interior_brentq`. **37 de 40 (92.5 %)** ocurren al evaluar un extremo del bracket,
no en el punto interior que `brentq` refina después. Esta es la evidencia central
de H1: el fallo está en el *sondeo* del rango, no en el refinamiento.

Iteración del lazo frío al fallar: 1 (22 filas), 0 (17, antes de entrar al lazo) y
4 (1 fila). El fallo es sistemático y temprano, no por deriva de iteraciones.

La cascada se decodifica con las tablas `PRE` (13 llamadas) y `COLD` (15 por
iteración), verificadas empíricamente contra la traza real: 74 llamadas =
13 + 4×15 + 1 de cierre, con el `PRE` byte a byte igual a la traza.

## 3. Variantes

| Variante | Arranque | Resultado en las 46 `NO_CONVERGIO` |
|---|---|---|
| **V0** | `T10_inicial=None`, `_bracketear` original | 40 `error_backend` (fallo de propiedad) |
| **V1** | `T10_inicial = T_sumidero + 5 K` | rescata 3 (las 3 salen `CORREGIBLE`); las otras 37 siguen fallando |
| **V2** | V1 + `F_seguro` + bracket replegado 5 K | rescata 25 más (33 `CORREGIBLE` en total); 12 no |

V1 por sí solo es insuficiente: el warm start cambia el estado de partida pero no
evita que el primer `F(lo)` o `F(hi)` se evalúe fuera del dominio del backend.

## 4. Controles

**FASE2 `KALINA` (5 filas, filas 0/13/21/33/159):** las tres variantes reproducen la
clasificación `KALINA` y `eta` con **delta = 0.0** respecto al CSV original
(`d_eta_V0 = d_eta_V1 = d_eta_V2 = 0.0`). La verificación B con `AmmoniaWaterAdapter`
da `verificado = True` en las tres, con `dh4s` entre −1.144 y −1.250 kJ/kg
(coherente con `eta_t` en el rango 0.80–0.85 de esas filas).

**Literatura `CORREGIBLE` (5 filas):** las tres variantes reproducen `CORREGIBLE` con
`|delta eta| ≤ 2.6e-7` (redondeo del CSV de origen, que guarda 6 decimales).

Ninguna regresión: los 10 controles se comportan igual bajo V0, V1 y V2.

## 5. Por qué V2 es lento

Tiempo total por variante (56 filas, 6 workers, reloj de pared 1859 s):
V0 1910 s (mediana 16.6 s), V1 1985 s (mediana 17.4 s), **V2 6856 s (mediana 92.5 s)**.

V2 multiplica el coste por ~5.5 porque cada extremo del bracket que no evalúa se
reintenta en pasos de 5 K, y cada reintento es una evaluación completa de la
cascada (74 llamadas de propiedades). El coste es propio del diagnóstico, no un
defecto de la variante.

## 6. Las 12 filas que no se rescatan

| Causa | Filas | Detalle |
|---|---|---|
| `NoBracket` sin cambio de signo | 3 | p. ej. `f2_h_Ps` 865: `f_lo=-6.62`, `f_hi=-93.8` en `[371, 459] K` — `F` no se anula en el rango físico |
| `NoBracket` sin extremos evaluables | 4 | los 4 bifásicos restantes: `sep.ELV` no resuelve en todo el rango |
| `PuntoNoEvaluable` en brentq | 5 | punto interior no evaluable (p. ej. `T=301.03 K`) |

Estas no son falsas `NO_CONVERGIO`: son casos donde no existe solución en el rango
físico admisible, o donde el bracket original fallaba por evaluar un extremo
inválido y ahora falla legítimamente al no encontrar cambio de signo.

## 7. Desviaciones del enunciado

0. **`PuntoNoEvaluable` no tiene precedent en `src/`.** El enunciado pedía decidir qué
   hacer cuando no hay bracket; brentq no admite `None`, así que un punto interior
   no evaluable lanza una excepción propia y la fila se registra como
   `V2 = no_convergio` con el `T` exacto en el mensaje. No se inventó ninguna
   recuperación alternativa (muestreo, regularización o cambio de raíz) porque no
   estaba especificada. 5 de las 12 filas no rescatadas caen en este caso, así que
   V2 puede estar dejando soluciones sobre la mesa por esa decisión de diseño.
1. **Muestra de literatura `T_from_Ph`: 19 filas, no 20.** El CSV de literatura tiene
   28 `NO_CONVERGIO`: 20 con `T_from_Ph` en `detalle_error`, 7 sin equilibrio
   bifásico y 1 (fila 43) que **converge pero queda `NO_CONVERGIO` por fallas de
   clasificación** (`N2,O2,O5,C1,C3`), por lo que su `detalle_error` está vacío.
   La fila 43 queda fuera por definición del grupo. Total muestra:
   15 + 5 + 19 + 7 + 5 + 5 = **56**.
2. **Controles de literatura: `CORREGIBLE` en vez de `KALINA`.** El barrido de
   literatura no contiene ninguna fila `KALINA` (clasificaciones: 32 `CORREGIBLE`,
   28 `NO_CONVERGIO`), por lo que se usaron las 5 `CORREGIBLE` como mejor control
   disponible. Los 5 `KALINA` exigidos se tomaron de FASE2.
3. **`eps` vacío en las 28 filas `NO_CONVERGIO` de literatura.** Se reprodujeron con
   `EPS_PARTIDA = (0.85, 0.75, 0.80)`, el paso base de `calibrar_eps`. Los CSV
   originales no registran qué `eps` concretos fallaron.
4. **Grupo FASE2 `h(P, T, x)` con `x_b=0.85`:** 15 filas, fuera de muestra por
   completo (el enunciado las excluye). Se recomendadas en una tarea aparte.
5. **Backend distinto al del barrido original.** Los CSV se generaron con
   `TeqpAdapter`; la sonda usa `TeqpVerificado` por requisito. Esto puede explicar
   las 6 filas que V0 ya converge y que el barrido marcó `NO_CONVERGIO`.

## 8. Supuestos

- `T_amb_diseno = 303.55 K` para las filas FASE2 (es el valor que
  `busqueda_libre_v2.py` pasa explícitamente). Para literatura se usó el default
  de `evaluar_ciclo`, que coincide.
- `x_backend = 0.5` para FASE2 (el valor con el que se ejecutó
  `busqueda_libre_v2.py`) y `x_b` de cada fila para literatura.
- La decodificación de la cascada se apoya en que `evaluar` es determinista: la
  traza real de 74 llamadas se verificó contra `PRE`/`COLD` antes de confiar en ella.

## 9. Conclusión operativa

El arranque frío (V1) explica **3 de 46** falsos `NO_CONVERGIO`. El mecanismo real
es la evaluación de extremos del bracket: **37 de 40 fallos de V0 (92.5 %)** ocurren
en `extremo_lo` o `extremo_hi`, y V2 (bracket tolerante) rescata 25 filas por sí
solo. Si se quisiera corregir `src/`, el cambio de mayor rendimiento sería hacer
tolerante `_bracketear` al evaluar `F(lo)` y `F(hi)`, no ajustar `T10_inicial`. El
warm start sigue siendo una mejora legítima y barata, pero por sí solo no recupera
estos casos.

Esa modificación **no se ha aplicado**: queda fuera del alcance de esta tarea
(diagnóstico sin cambios en `src/`).
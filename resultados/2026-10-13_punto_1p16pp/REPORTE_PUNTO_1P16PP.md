# Reporte — Punto del benchmark Elsayed con Δη = +1.16 pp (P_alta = 2300 kPa, x_b = 0.55)

Fecha: 2026-10-13. Rama `feature/solucion-3`. `src/`, tests y datos originales sin cambios.
Estado: **punto excluido por decisión del usuario; causa abierta y acotada. Diagnóstico completo diferido a después de la entrega.**

## BLUF

- **Decisión (usuario):** por ahora el punto se excluye del benchmark. No es una exclusión por criterio objetivo y así debe declararse.
- **Estadística sin el punto (n = 22):** Δ medio −0.117 pp; |Δ| medio 0.235 pp; |Δ| máx 0.515 pp (4.7 % relativo); mediana |Δ| relativa 2.27 %. Con el punto (n = 23): −0.062 / 0.275 / 1.159 pp (12.1 %) / 2.37 %.
- **Lo que se descartó con evidencia:** la digitalización de la curva del paper. Explica ≤ 0.05–0.1 pp de los 1.16.
- **Lo que apunta a la causa:** el error no es un punto aislado, es un patrón. Los 4 puntos con ε_HRVG < 0.80 tienen Δ positivo (+0.27 a +1.16 pp); los 19 con ε_HRVG ≥ 0.80 tienen Δ ≤ +0.07 pp. Es decir, el desajuste crece cuando la calibración de un paso de la efectividad del HRVG da un ε bajo (zona cercana al punto de burbuja a la salida del HRVG).
- **Lo que NO está demostrado:** el mecanismo exacto (muro de burbuja, T2, ecuación de estado). Eso lo mide la sonda diferida (pasos 3 y 4 del TASK_CONTEXT).

## La pregunta

¿El +1.16 pp a 2300 kPa es un error del modelo, del benchmark o de la lectura de la figura?

## Método simple

1. Releer la curva del paper con tres interpolaciones y con los marcadores del PDF vectorial.
2. Mirar el punto dentro de los 23 (orden por ε_HRVG, W_net, título q4).
3. Recalcular la estadística con y sin el punto y con criterios uniformes alternativos.

OpenCode escribió y ejecutó dos scripts (`scripts/punto_1p16_datos.py`, `scripts/punto_1p16_marcadores.py`) a partir de `prompts/TASK_CONTEXT_punto_1p16pp.md`; Claude revisó las salidas.

## Resultados

### H1 — Digitalización / lectura de la curva: **en contra** (≤ 0.05–0.1 pp)

| Lectura de η_paper a 2300 kPa | η [%] | Diferencia con la usada |
|---|---|---|
| Lineal entre vértices (la del benchmark) | 9.547 | — |
| PCHIP | 9.586 | +0.04 pp |
| Spline cúbico | 9.598 | +0.05 pp |
| Entre los dos marcadores del PDF que encierran 2300 (22.595 y 23.384 bar) | ≈ 9.51 (cálculo de Claude a mano) | −0.04 pp |

- Pendiente local del paper en ese tramo: −1.75 pp/bar (−2.66 pp/bar en el segmento siguiente). Un error de 0.007 bar (calibración del eje) mueve η ≈ 0.01 pp.
- Los marcadores de la cola de la curva coinciden con la línea central de la curva digitalizada dentro de ~0.1 pp (puntos a 22.6 y 23.4 bar). La separación máxima marcador–curva (2.9 pt) ocurre a 20.6 bar, donde la curva es plana, y allí no pesa.
- Fuente: `h1_interpolacion.csv`, `h1_marcadores_fig7.csv`.

### H5 — Duplicados del paper: **cuantifica la incertidumbre de lectura**

Mismo estado (x_b = 0.55, 1500 kPa): Fig. 7 = 11.4317 %, Fig. 3 = 11.3942 %, texto = 11.38 %. Dispersión de lectura: 0.04–0.05 pp, unas 25 veces menor que 1.16. (`h5_duplicados.csv`).

### Patrón en los 23 puntos (`diagnostico_23.csv`)

| Grupo | n | Δ [pp] |
|---|---|---|
| ε_HRVG < 0.80 (2300, 2200, Fig3 x_b 0.45, 0.66/3000 kPa) | 4 | +1.16, +0.52, +0.38, +0.27 |
| ε_HRVG ≥ 0.80 | 19 | −0.42 a +0.07 (medio ≈ −0.20) |

W_net también ordena: los tres más bajos (16.0, 18.4, 21.0 kW) son los tres Δ más altos. El punto de 2300 kPa es el extremo de una tendencia, no un valor suelto.

### Estadística con y sin (`estadistica_con_sin.csv`)

| Criterio (aplicado a los 23) | n | Δ medio [pp] | \|Δ\| medio [pp] | \|Δ\| máx [pp] | Mediana \|Δ\| rel [%] |
|---|---|---|---|---|---|
| Todos | 23 | −0.062 | 0.275 | 1.159 | 2.37 |
| **Sin el punto 2300 (decisión del usuario)** | **22** | **−0.117** | **0.235** | **0.515** | **2.27** |
| W_net ≥ 20 kW (excluye 2: 2300 y Fig3 x_b 0.45) | 21 | −0.147 | 0.221 | 0.422 | 2.17 |
| W_net ≥ 25 kW (excluye 3) | 20 | −0.173 | 0.214 | 0.422 | 2.05 |
| ε_HRVG ≥ 0.80 (excluye 4) | 19 | −0.197 | 0.211 | 0.422 | 1.93 |
| ε_HRVG ≥ 0.85 (excluye 5) | 18 | −0.202 | 0.216 | 0.422 | 2.05 |

Lectura: ningún criterio uniforme excluye *solo* el punto de 2300; el más natural (ε_HRVG ≥ 0.80) excluye 4. Excluir solo uno es una decisión, no un criterio.

## Banda de incertidumbre frente a los nuevos máximos

- Banda de η por propiedades (xL ±0.01, yV ±0.01, h_exceso ±200 J/mol): ±0.4–0.7 pp en 3 puntos (`2026-10-03_incertidumbre_eta`). **No se calculó en 2300 kPa** (pendiente).
- Sin el punto, el máximo es 0.515 pp (Fig. 3, x_b = 0.45, 373 K): cae dentro de ±0.4–0.7 pp, pero ese punto tampoco tiene banda calculada, y el límite superior asimétrico del caso 11.06 % es +0.46 pp. Se puede decir "del orden de la banda", no "dentro" con rigor.

## Lo que no se sabe

1. Por qué ε_HRVG bajo produce Δ positivo. Hipótesis de trabajo (sin confirmar): la mezcla a la salida del HRVG (T2 = T_fuente − 4 K = 369 K, x = 0.55) se acerca a su punto de burbuja; cerca de ese muro η es hipersensible a P y T2, y el paper lo tiene más cerca que el modelo (~24.1 bar). A ~0.7 bar de desplazamiento horizontal entre curvas habría ~1 K de T2.
2. Cuánto de ese desplazamiento es la ecuación de estado (Ibrahim–Klein del paper vs Tillner-Roth/G4-01 del modelo) y cuánto la calibración de un paso.
3. Si el paper aplica la cota q4 ≥ 0.90 distinto. En el modelo q4 = 0.950 en este punto, así que no está activa.
4. El motor real (`AmmoniaWaterAdapter`) no se corrió en 2300 kPa; solo hay controles del motor real en 1500 y 2500 kPa (η coincide con teqp en 0.001 pp).

## Defecto conocido de la sonda ejecutada

`h1_desplazamiento.csv`: las columnas `P_paper_bar` y `dP_bar` salen en kPa/bar mezclados (error de unidades de OpenCode). Valores correctos en kPa (P_paper a igual η_modelo, rama descendente del paper): 2000 → 2042 (Δ = −42 kPa), 2200 → 2143 (+57), 2300 → 2220 (+80). Los puntos de 1100–1800 kPa están en la rama ascendente del modelo y no son comparables con ese cálculo. Hay que regenerar el CSV antes de citarlo.

## Qué sigue (diferido por el usuario)

- Paso 3 del TASK_CONTEXT (teqp, ~40 min): muro de burbuja a dT = 2–6 K, curva fina η(P) en 2100–2600 kPa, sensibilidad a ε_HRVG y P, banda de propiedades en 2300 kPa.
- Paso 4 (motor real, 1–3 h): punto 2300 con `AmmoniaWaterAdapter`.
- Con eso se decide entre "explicado y acotado" (banda ampliada para la zona ε_HRVG < 0.80) y "criterio objetivo" (ε_HRVG ≥ 0.80, n = 19).

## Texto propuesto (solo propuesta; no se editó el entregable)

**Sección 8, "Modelo publicado de Elsayed":**
> Se contrastaron 23 puntos de las curvas de Elsayed et al. (2013), leídas del PDF vectorial de Embaye et al. Los 23 puntos arrojan |Δη| medio 0.27 pp con un máximo de 1.16 pp (12 %) a P_alta = 2300 kPa, x_b = 0.55. Ese punto se excluye de la estadística principal (n = 22: Δ medio −0.12 pp; |Δη| medio 0.23 pp; máximo 0.52 pp) y se reporta aparte como discrepancia abierta. Su causa no está establecida; se descartó la lectura de la figura (≤ 0.1 pp) y se observa que los cuatro puntos con efectividad de HRVG calibrada inferior a 0.80, cercanos al punto de burbuja a la salida del evaporador, presentan Δη positivo.

**Sección 8, "Banda de incertidumbre de η":**
> La banda por propiedades (±0.4–0.7 pp) se calculó en tres puntos, ninguno a 2300 kPa. El máximo del benchmark sin el punto excluido (0.52 pp) es del orden de esa banda; el punto excluido (1.16 pp) la supera.

**Sección 13.2, "Sin validación experimental":**
> El modelo se verifica y contrasta con modelos publicados (Elsayed et al., Nemati et al., DWSIM); no existe validación experimental. Persiste una discrepancia abierta de +1.16 pp en la zona de efectividad de HRVG baja (ε < 0.80, P_alta ≥ 2200 kPa para x_b = 0.55), cuya causa no está determinada y queda como trabajo futuro.

**Tabla 10, fila Elsayed:** n = 22 (23 con el punto); Δ medio −0.12 (−0.06) pp; |Δ| medio 0.23 (0.27) pp; |Δ| máx 0.52 (1.16) pp; "un punto excluido por decisión, causa abierta".

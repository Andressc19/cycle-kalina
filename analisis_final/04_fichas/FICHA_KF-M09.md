# FICHA KF-M09 — Escalera de conservación de los datos del profesor

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge.
> - **Grupos de datos del profesor:** EF = las 5 eficiencias y efectividades (η_t, η_p, ε_HRVG,
>   ε_reg, ε_cond); PA = P_alta; PB = P_baja; TF = T_fuente; TS = T_sumidero; XB = x_b.
> - **Escalera:** se conserva un grupo, se elige el mejor, y se le suma otro grupo por ronda.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades.

### ID del caso:
`KF-M09`. Tiene un subcaso por (ronda, conjunto conservado), por ejemplo `KF-M09-R3-XB_PA_EF_PB`,
más HUS (Húsavík) y REAL (motor real). Cada conjunto es su propio bloque (**B13-<conjunto>**).
Familia **C** (conservación), diseño: escalera de selección hacia adelante con LHS.
2026-10-08/09, commits `a366b93`, `789c1dc` y `20b21fc`.

### Nombre del caso:
¿Cuál es el conjunto más grande de datos del profesor que todavía da KALINA?

### Objetivo del barrido:
Encontrar el conjunto máximo de datos del enunciado compatible con KALINA, y los rangos de las
demás variables (sobre todo las presiones).

### ¿Qué se barrió?
- **Ronda 0:** se conserva un grupo (6 opciones) y las demás variables se sortean (100 puntos por opción).
- **Rondas 1 a 3:** al mejor conjunto se le suma un grupo más (30 puntos por opción).

### ¿Por qué se barrió?
El usuario pidió una "escalera de conservación" para responder directamente qué parte del
enunciado se puede mantener. M5 había dado respuestas parciales con muestreo grueso.

### Datos o variables barridas:
En cada conjunto se sortean (LHS) las variables que **no** se conservan, dentro de la caja de M5:
T_fuente 380–623 K, T_sumidero 278–303.5 K, P_alta 2000–5000 kPa, P_baja 200–2000 kPa, x_b 0.50–0.85
y η/ε 0.40–0.95. Son 100 puntos por conjunto en la ronda 0 y 30 en las rondas 1–3. En el conjunto
final (XB+PA+EF+PB) solo se barren **T_fuente (384–520 K) y T_sumidero (278–303.4 K)**.
Total: **987 corridas**. El piso de O2 es la T_sumidero de cada punto.

### Datos modificados:

| Conjunto final XB+PA+EF+PB | Valor |
|---|---|
| Conservados exactamente del profesor | P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.80 |
| Abandonados (se sortean) | T_fuente (623.15 K en el enunciado) y T_sumidero (300.03 K) |

### Métodos aplicados:
LHS por conjunto; elección del conjunto con más KALINA confiables en cada ronda; verificación de
3 puntos con el motor real (1500 s).

### Resultados obtenidos (todos validados por A4, V18–V20):

| Ronda | Conjunto elegido | Datos del profesor conservados | KALINA (confiables) |
|---|---|---|---|
| 0 | XB | 1 | 29 (15) |
| 1 | XB+PA | 2 | 11 (7) |
| 2 | XB+PA+EF | 7 | 13 (7) |
| 3 | **XB+PA+EF+PB** | **8 de 10** | **5 (5)** |

- **Conjunto final XB+PA+EF+PB:** conserva P_alta = 3000, P_baja = 400, x_b = 0.50 y las 5
  eficiencias. Solo se mueven las temperaturas: **T_fuente 391–409 K y T_sumidero 280–293 K**.
  Los 5 KALINA son confiables, con η hasta 10.6 % y subenfriamiento real ≥ 2 K.
- **Ningún conjunto que conserve TF (623 K) da KALINA confiable**, en ninguna ronda. XB+PA+EF+TF da
  30 de 30 NO_CONVERGIO.
- Con el clima del profesor en lugar de su P_baja (XB+PA+EF+TS): 6 KALINA, 4 confiables.
- **Motor real (1500 s):** A\*, el óptimo A4 de M7 y Húsavík coinciden con teqp (Δη ≤ 0.003 pp).
- Tablas: TAB-M09-00 a -03. Figura FIG-M09-01 (la escalera).

### Conclusiones del caso:
1. **Los datos del profesor son un ciclo Kalina válido si se cambia solo la temperatura de la
   fuente** (de 623 K a ~390–410 K) y se usa un sumidero algo más frío (≤ ~293 K).
2. **La fuente de 623 K es el único dato que no se puede conservar junto con los demás.** Es el
   bloqueo estructural del enunciado. Con 623 K solo aparecen KALINA confiables lejos del resto del
   enunciado (x_b ~0.7–0.85, P_alta hasta 5000 kPa, P_baja ~1.4–2 MPa; ver M7-A3 y M5-S1). En la
   escalera, ningún conjunto que incluya TF da un KALINA confiable.
3. No se pueden conservar a la vez sus 2 presiones, su ε_cond = 0.80 y su clima de 300 K. Para eso
   hace falta ε_cond ≥ 0.875 (lo confirma M5c).

### Advertencias, supuestos y limitaciones:
- 30 puntos por conjunto en las rondas 1 a 3 es una exploración; la búsqueda dirigida solo se hizo en la última ronda.
- El ranking elige por número de KALINA confiables, no por número de datos conservados. Por eso
  XB+PA (2 datos) le ganó a XB+EF (6 datos) en la ronda 1.
- Búsquedas más finas (M2 ruta B y M5c) conservan hasta 9 de 11 datos. M9 confirma la tendencia, pero no las supera.

### Recomendaciones:
Usar este caso como la respuesta central del informe a "¿qué se puede conservar del enunciado?".
Presentarlo junto con M5c (presiones del profesor + ε_cond ≥ 0.875).

**Fuentes:** `resultados/2026-10-08_final_M9/REPORTE_M9.md` (incluidas las notas del director), `m9_paso1.csv`, `m9_paso2.csv`, `m9_escalera.csv`, `m9_motor_real.csv`; A4 (V18–V20).

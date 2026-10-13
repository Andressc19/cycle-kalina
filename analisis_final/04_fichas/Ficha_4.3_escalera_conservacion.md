# Ficha 4.3 — Escalera de conservación de los datos del profesor

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge.
> - **Grupos de datos del profesor:** cada grupo se nombra con su variable (T_fuente, T_sumidero,
>   P_alta, P_baja, x_b); "eficiencias" = las 5 eficiencias y efectividades (η_t, η_p, ε_HRVG,
>   ε_reg, ε_cond). Un conjunto se escribe con "+", p. ej. x_b + P_alta + eficiencias + P_baja.
> - **Escalera:** se conserva un grupo, se elige el mejor, y se le suma otro grupo por ronda.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades y con
>   todas sus η y ε en [0.40, 0.95].

### ID del caso:
**Estudio 4.3** · Escalera de conservación. Responde la pregunta 4: ¿Qué datos del profesor se pueden conservar?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): una por conjunto conservado en cada ronda (p. ej. 4.3 x_b+P_alta); 6.1d y 6.2e son puntos de control que se calcularon dentro de este barrido.
Familia **C** · 2026-10-08/09 · commit `a366b93`, `789c1dc`, `20b21fc` · código de origen: M09.

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
enunciado se puede mantener. estudio 4.1 había dado respuestas parciales con muestreo grueso.

### Datos o variables barridas:
En cada conjunto se sortean (LHS) las variables que **no** se conservan, dentro de la caja de estudio 4.1:
T_fuente 380–623 K, T_sumidero 278–303.5 K, P_alta 2000–5000 kPa, P_baja 200–2000 kPa, x_b 0.50–0.85
y η/ε 0.40–0.95. Son 100 puntos por conjunto en la ronda 0 y 30 en las rondas 1–3. En el conjunto
final (x_b + P_alta + eficiencias + P_baja) solo se barren **T_fuente (384–520 K) y T_sumidero (278–303.4 K)**.
Total: **987 corridas**. El piso de O2 es la T_sumidero de cada punto.

### Datos modificados:

| Conjunto final x_b + P_alta + eficiencias + P_baja | Valor |
|---|---|
| Conservados exactamente del profesor | P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.80 |
| Abandonados (se sortean) | T_fuente (623.15 K en el enunciado) y T_sumidero (300.03 K) |

### Métodos aplicados:
LHS por conjunto; elección del conjunto con más KALINA confiables en cada ronda; verificación de
3 puntos con el motor real (1500 s).

### Resultados obtenidos (todos validados, V18–V20):

| Ronda | Conjunto elegido | Datos del profesor conservados | KALINA (confiables) |
|---|---|---|---|
| 0 | x_b | 1 | 29 (15) |
| 1 | x_b + P_alta | 2 | 11 (7) |
| 2 | x_b + P_alta + eficiencias | 7 | 13 (7) |
| 3 | **x_b + P_alta + eficiencias + P_baja** | **8 de 10** | **5 (5)** |

- **Conjunto final x_b + P_alta + eficiencias + P_baja:** conserva P_alta = 3000, P_baja = 400, x_b = 0.50 y las 5
  eficiencias. Solo se mueven las temperaturas: **T_fuente 391–409 K y T_sumidero 280–293 K**.
  Los 5 KALINA son confiables, con η hasta 10.6 % y subenfriamiento real ≥ 2 K.
- **Ningún conjunto que conserve T_fuente (623 K) da KALINA confiable**, en ninguna ronda. x_b + P_alta + eficiencias + T_fuente da
  30 de 30 NO_CONVERGIO.
- Con el clima del profesor en lugar de su P_baja (x_b + P_alta + eficiencias + T_sumidero): 6 KALINA, 4 confiables.
- **Motor real (1500 s):** A\*, el óptimo 5.1d de estudio 5.1 y Húsavík coinciden con teqp (Δη ≤ 0.003 pp).
- Tablas: 4.3-1, 4.3-2, 4.3-3, 4.3-4. Figuras: 4.3-1.

### Conclusiones del caso:
1. **Los datos del profesor son un ciclo Kalina válido si se cambia solo la temperatura de la
   fuente** (de 623 K a ~390–410 K) y se usa un sumidero algo más frío (≤ ~293 K).
2. **La fuente de 623 K es el único dato que no se puede conservar junto con los demás.** Es el
   bloqueo estructural del enunciado. Con 623 K solo aparecen KALINA confiables lejos del resto del
   enunciado (x_b 0.71–0.85, P_alta 3200–5000 kPa, P_baja 1.36–1.97 MPa; ver estudio 5.1c y estudio 4.1a). En la
   escalera, ningún conjunto que incluya T_fuente da un KALINA confiable.
3. No se pueden conservar a la vez sus 2 presiones, su ε_cond = 0.80 y su clima de 300 K. Para eso
   hace falta ε_cond ≥ 0.875 (lo confirma estudio 4.2).

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 4.3-1.** Conservar más datos reduce los KALINA confiables (15 → 7 → 7 → 5 por ronda) pero no los
  elimina. **Todo conjunto que incluye T_fuente da 0.** Después de T_fuente, P_baja es el dato más caro de
  conservar (1 KALINA en la ronda 0).
- Son conteos absolutos de 5–15 puntos y sin denominador en la figura.

### Advertencias, supuestos y limitaciones:
- 30 puntos por conjunto en las rondas 1 a 3 es una exploración; la búsqueda dirigida solo se hizo en la última ronda.
- El ranking elige por número de KALINA confiables, no por número de datos conservados. Por eso
  x_b + P_alta (2 datos) le ganó a x_b + eficiencias (6 datos) en la ronda 1.
- Búsquedas más finas (estudios 2.1 y 2.2 ruta B y estudio 4.2) conservan hasta 9 de 11 datos. estudio 4.3 confirma la tendencia, pero no las supera.

### Recomendaciones:
Usar este caso como la respuesta central del informe a "¿qué se puede conservar del enunciado?".
Presentarlo junto con estudio 4.2 (presiones del profesor + ε_cond ≥ 0.875).

**Fuentes:** `resultados/2026-10-08_final_M9/REPORTE_M9.md` (incluidas las notas del director), `m9_paso1.csv`, `m9_paso2.csv`, `m9_escalera.csv`, `m9_motor_real.csv`; validación V18–V20.

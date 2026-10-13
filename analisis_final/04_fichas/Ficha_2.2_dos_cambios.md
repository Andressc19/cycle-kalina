# Ficha 2.2 — Con dos cambios al enunciado, ¿aparece KALINA?

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge.
> - **A\* (punto ancla):** el punto que sale de este caso y se usa después. Es PP con
>   **T_fuente = 403 K y P_baja = 563.64 kPa**. Es KALINA, con η = 8.48 %.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades y con
>   todas sus η y ε en [0.40, 0.95].
> - **d (distancia al profesor):** suma de los cambios de cada variable, cada uno dividido por el
>   ancho del rango de esa variable. d = 0 es el profesor exacto.
> - **O2:** cavitación (el líquido debe llegar subenfriado a la bomba).

### ID del caso:
**Estudio 2.2** · Dos cambios. Responde la pregunta 2: ¿Qué es lo mínimo que hay que cambiar para que funcione?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 2.2a (conservar la fuente (ε_HRVG × P_baja)); 2.2b (bajar la fuente (T_fuente × P_baja)).
Familia **F** · 2026-10-06 · commit `c6fb1e1` · código de origen: M02-N2.

### Nombre del caso:
Nivel 2: cambiar dos variables del profesor (siempre P_baja, más una del lado caliente).

### Objetivo del barrido:
Encontrar la combinación de dos cambios más parecida al profesor que dé KALINA y elegir el punto
ancla A\* para los estudios siguientes.

### ¿Qué se barrió?
- **Ruta A** (conserva la fuente y el sitio del profesor): ε_HRVG ∈ {0.75, 0.78, 0.81} × P_baja.
- **Ruta B** (cambia la fuente): T_fuente ∈ {380, 390, 403, 420, 434, 466, 497, 529, 560} K × P_baja.

### ¿Por qué se barrió?
El nivel 1 mostró que el ciclo converge con una fuente más fría o un HRVG menos efectivo, pero
falla la cavitación (O2). O2 se cierra subiendo P_baja; por eso P_baja siempre es la segunda variable.

### Datos o variables barridas:

| Ruta | Variable 1 | Variable 2 | Malla | Corridas |
|---|---|---|---|---|
| A | ε_HRVG: 0.75 / 0.78 / 0.81 | P_baja: 400–2000 kPa, 12 valores | 3 × 12 | 36 |
| B | T_fuente: 9 valores, 380–560 K | P_baja: 400–2000 kPa, 12 valores | 9 × 12 | 108 + 36 de bisección |

Total: **180 corridas**.

### Datos modificados:
Solo el par de cada ruta; las otras 9 variables quedan en PP. En la ruta B se cambian T_fuente y
P_baja; en la ruta A, ε_HRVG y P_baja. El piso de O2 queda en 300.03 K.

### Métodos aplicados:
Malla 2D, más bisección sobre P_baja allí donde cambia "ser KALINA" o el signo del margen de O2
(tolerancia 10 kPa, como máximo 8 iteraciones). Solo cuentan los puntos genuinos (MATEMATICA §4).

### Resultados obtenidos:
- **Ruta A: 36 genuinas, 0 KALINA.** Con la fuente de 623 K, ningún ε_HRVG del rango alcanza; bloquea O2.
- **Ruta B: 59 KALINA, 48 de ellos confiables** (validado, V04 y V05).
  - Hay KALINA solo con **T_fuente ∈ {390, 403, 420, 434} K**. Con 380 K no converge; con 466 K o
    más no hay KALINA.
  - La menor P_baja KALINA es **445.5 kPa con T_fuente = 390 K** (η = 2.45 %).
  - El de mayor η es T_fuente = 420 K con P_baja = 736 kPa (η = 9.15 %).
  - Los 11 KALINA fuera de rango están todos en T_fuente = 434 K.
- **A\* elegido:** la opción intermedia, **T_fuente = 403 K y P_baja = 563.64 kPa** (η = 8.48 %).
- Tablas: 2.2-1, 2.2-2, 2.2-3. Figuras: 2.2-1, 2.2-2.

### Conclusiones del caso:
1. **Con dos cambios sí hay KALINA**, pero solo si se baja la fuente a 390–434 K y se sube P_baja.
2. **Conservando la fuente del profesor (623 K) no hay KALINA** dentro del rango de eficiencias de ese momento.
3. Cuanto más fría la fuente, menor P_baja necesita KALINA (445 kPa a 390 K), pero menor es η.
   Entre esos extremos se eligió A\*.

### Lo que muestran las figuras:

_Lectura directa de las figuras (valores con «≈» leídos de la gráfica; el marcador hueco es «fuera de rango»). Detalle: `analisis_final/CONCLUSIONES_DESDE_FIGURAS.md`._

- **Figura 2.2-1 (ruta A).** Los 36 puntos son Corregible sin importar P_baja (400–2000 kPa): con la fuente
  de 623 K, **subir P_baja no cambia la clase**.
- **Figura 2.2-2 (ruta B).** La región KALINA es una **cuña**: la P_baja mínima sube de ≈450 kPa (390 K) a ≈600
  (403 K), ≈740 (420 K) y ≈950 (434 K), es decir, ≈ +500 kPa en 44 K. A 380 K todo es Falso convergido.
- Desde ≈434 K los marcadores son huecos: la zona caliente sale del rango del motor antes de llegar a 623 K.

### Advertencias, supuestos y limitaciones:
- La malla de P_baja tiene un paso de 145 kPa: una zona KALINA más angosta podría no verse.
- Los puntos medios de la bisección que caen en zonas espurias (N2) se toman como "no cumple".
- La elección de A\* es una decisión de diseño (la opción intermedia), no un óptimo.
- Al verificar A\* con el motor real, en estudio 6.1 dio NO_CONVERGIO por límite de tiempo (300 s). En estudio 4.3,
  con 1500 s, el motor real lo confirma (η 8.48 %, Δ < 0.001 pp).

### Recomendaciones:
- Usar A\* como punto base de la sensibilidad local (estudio 3.1).
- Abrir el rango de eficiencias a [0.40, 0.95] para ver si la ruta A (fuente del profesor) se vuelve
  posible. Eso es estudio 2.3.

**Fuentes:** `resultados/2026-10-06_final_M2/REPORTE_M2_N2.md`, `m2n2_malla.csv`, `m2n2_biseccion.csv`, `m2n2_resumen.csv`; validación V03–V05; estudio 4.3 (motor real).

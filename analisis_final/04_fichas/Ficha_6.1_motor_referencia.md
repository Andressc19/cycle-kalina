# Ficha 6.1 — Verificación con el motor real y costo del margen de cavitación

> **Antes de leer**
> - **teqp:** el motor de propiedades rápido que se usó en casi todos los barridos.
> - **Motor real:** la implementación de referencia del modelo de propiedades. Es más lenta y se usa para confirmar.
> - **A\* (punto ancla):** el punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa
>   (KALINA, η = 8.48 %).
> - **O2 / subenfriamiento:** el líquido debe llegar a la bomba por debajo de su temperatura de
>   burbuja. El subenfriamiento ΔT_sub es esa diferencia, en K.
> - **Banda de η:** ±0.4–0.7 pp; diferencias menores no son concluyentes.

### ID del caso:
**Estudio 6.1** · Verificación con el motor de referencia. Responde la pregunta 6: ¿Son confiables los resultados?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 6.1a (teqp frente al motor real); 6.1b (piso de cavitación a 30.4 °C); 6.1c (costo de exigir subenfriamiento).
Familia **V** · 2026-10-08 · commit `d98cd7d` · código de origen: M06.

### Nombre del caso:
teqp contra el motor real, piso de O2 más exigente y costo del subenfriamiento.

### Objetivo del barrido:
1. Confirmar que teqp y el motor real dan lo mismo en los puntos importantes.
2. Ver qué pasa si el piso de O2 sube a 303.55 K (30.4 °C).
3. Medir cuánta P_baja extra hace falta para exigir 2 K o 5 K de subenfriamiento real.

### ¿Qué se barrió?
12 puntos clave de las fases anteriores: A\*, los óptimos de estudio 5.1, la franja de estudio 4.2, el mejor de estudio 3.2
y otros. En la parte 6.1c, P_baja por bisección en 8 de esos puntos.

### ¿Por qué se barrió?
Todos los barridos usaron teqp. Antes de concluir había que asegurarse de que el motor real dice
lo mismo, y de que el criterio O2 (que exige subenfriamiento ≥ 0 K, sin margen) no deja los
diseños demasiado al filo.

### Datos o variables barridas:
- **6.1a:** 12 puntos × 2 motores (24 corridas).
- **6.1b:** los mismos 12 con el piso de O2 en 303.55 K (12 corridas).
- **6.1c:** 8 puntos × ΔT_sub ∈ {2, 5} K, buscando la P_baja necesaria (131 evaluaciones).

### Datos modificados:
Cada punto conserva sus datos de origen. En 6.1b cambia solo el piso de O2; en 6.1c, solo P_baja.

### Métodos aplicados:
Comparación punto a punto de clase, η y margen de O2; bisección de P_baja para cada subenfriamiento objetivo.

### Resultados obtenidos:
- **Motor real con 300 s:** solo 2 de 12 terminan, P03 (estudio 4.2, η 10.81 %) y P08 (óptimo 5.1d de estudio 5.1,
  η 15.60 %). Ambos coinciden con teqp: misma clase y |Δη| < 0.001 pp. Los otros 10 se cortaron
  **por tiempo**, no por física. En estudio 4.3, con 1500 s, A\*, 5.1d y Húsavík también coinciden (Δη ≤ 0.003 pp).
- **Piso de 303.55 K:** 9 de 12 pasan a CORREGIBLE, por un déficit de cavitación de 0.5 a 3.2 K.
  Casi todos los diseños están al filo de O2.
- **Costo del subenfriamiento:**
  - exigir **2 K** cuesta **+25 a +46 kPa de P_baja** y **−0.3 a −0.5 pp de η**;
  - exigir **5 K**, +19 a +116 kPa y −0.3 a −1.2 pp.
  - Con las presiones del profesor (P03, P08), 2 K piden subir P_baja de 400 a ~425 kPa.
  - Los óptimos 5.1b, 5.1c y 5.1e de estudio 5.1 ya tenían 2 K de margen: costo 0. El de 5.1a (P05) daría +443 kPa
    y −3.7 pp, pero ese cálculo no es confiable (ver advertencias).
- Tablas: 6.1-1, 6.1-2, 6.1-3, 6.1-4. Figuras: 6.1-1.

### Conclusiones del caso:
1. **teqp y el motor real coinciden** en todos los puntos que el motor real alcanza a resolver. Los
   resultados de la campaña son válidos.
2. **Los diseños KALINA están casi todos al filo de la cavitación.** El criterio O2 del modelo no
   tiene margen propio.
3. **Dar un margen de 2 K es barato**: ~25–46 kPa más de P_baja y menos de 0.5 pp de η. No cambia
   ningún rango KALINA de forma material.

### Advertencias, supuestos y limitaciones:
- El motor real necesita ~1500 s por punto; con 300 s se corta.
- El costo de P05 (óptimo 5.1a) no es confiable: hay un hueco NO_CONVERGIO y la bisección saltó.
- El motor real no corre la verificación B.

### Recomendaciones:
En el informe, recomendar P_baja con un margen de ~2 K de subenfriamiento: sumar ~25–50 kPa a la
P_baja mínima KALINA de cada caso.

**Fuentes:** `resultados/2026-10-08_final_M6/REPORTE_M6.md` (incluida la nota del director), `m6_comparacion.csv`, `m6_subenfriamiento.csv`; `resultados/2026-10-08_final_M9/REPORTE_M9.md` (motor real con 1500 s).

# FICHA KF-M08 — ANECDÓTICO: eficiencias y efectividades fuera del rango realista

> **⚠ ANECDÓTICO — fuera del rango realista.** Este caso es una curiosidad. Los valores de η y ε
> fuera de [0.40, 0.95] no son realistas para este proyecto: **nada de esta ficha es un resultado de
> diseño ni entra en las conclusiones generales.**
>
> **Antes de leer**
> - **A\* (punto ancla):** el punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa
>   (KALINA, η = 8.48 %).
> - **Óptimo A1 de M7:** el KALINA de mayor η sin restricciones del primer arranque de M7 (η = 14.98 %).

### ID del caso:
`KF-M08` · bloque **BX** (no se mezcla con nada) · familia **X** (anecdótico) · diseño: una variable
a la vez · 2026-10-07.

### Nombre del caso:
Qué pasa si las eficiencias y efectividades salen del rango [0.40, 0.95].

### Objetivo del barrido:
Satisfacer una curiosidad: ver cómo responde el ciclo con equipos irrealmente malos (0.20) o casi perfectos (0.99).

### ¿Qué se barrió?
η_t, η_p, ε_HRVG, ε_reg y ε_cond, de a una, con 16 valores de 0.20 a 0.99.

### ¿Por qué se barrió?
Pedido anecdótico del usuario. No forma parte del protocolo de la campaña.

### Datos o variables barridas:
2 bases × 5 variables × 16 valores = **160 corridas**: 90 dentro de [0.40, 0.95] y 70 fuera.

### Datos modificados:
- **Base B1 = A\***, con el piso de O2 en 300.03 K.
- **Base B2 = el óptimo A1 de M7**, con el piso de O2 en 279.1 K.
- En cada tramo se mueve solo la eficiencia o efectividad correspondiente.

### Métodos aplicados:
Una variable a la vez, con la clase y η de cada punto.

### Resultados obtenidos:
- 160 corridas: 84 KALINA, 60 CORREGIBLE, 7 INVIABLE y 9 sin converger.
- El criterio que más aparece es O2 (66 veces).
- Las curvas η–variable están en `m8_curvas.png`. No se rehacen en el catálogo nuevo: el caso es anecdótico.

### Conclusiones del caso:
Solo ilustrativas. Fuera del rango realista el ciclo sigue la tendencia esperada (más eficiencia de
equipo, más η), y la cavitación (O2) sigue siendo el criterio que más falla. **No se usa para
recomendar nada.**

### Advertencias, supuestos y limitaciones:
Los 90 puntos dentro del rango tampoco sustituyen a M3/M4/M7, que son los barridos que exploran la
región de trabajo.

### Recomendaciones:
Mantenerlo al final del Excel con su franja de aviso y excluirlo del tablero y de las figuras.

**Fuentes:** `resultados/2026-10-07_final_M8_anecdotico/REPORTE_M8.md`, `m8_oat.csv`.

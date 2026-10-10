# FICHA KF-M04c — ¿Dónde termina KALINA al subir P_baja?

> **Antes de leer**
> - **LHS:** muestreo al azar que reparte bien los puntos dentro de una caja de rangos.
> - **Punto omitido:** no se evaluó porque P_baja quedaba a menos de 300 kPa de P_alta
>   (restricción física del proyecto).
> - **r_P:** razón de presiones P_alta / P_baja.
> - **Verificación B:** comprobación independiente de la turbina en los KALINA.
> - **O2:** cavitación.

### ID del caso:
`KF-M04c` · bloque **B08** (la caja de M4, pero con P_baja de 1500 a 2500 kPa) · familia **G** ·
diseño LHS de 150 puntos (semilla 20261008) · 2026-10-07.

### Nombre del caso:
El techo de P_baja de la región KALINA.

### Objetivo del barrido:
Saber si existe un techo de P_baja por encima del cual KALINA desaparece, qué criterio lo corta y
cómo depende de P_alta.

### ¿Qué se barrió?
Las 10 variables a la vez, con la caja de M4 salvo P_baja, que pasa a 1500–2500 kPa.

### ¿Por qué se barrió?
La caja de M4/M4b llegaba solo hasta 1500 kPa y en ese borde todavía había KALINA: no se sabía dónde terminaba.

### Datos o variables barridas:
- P_baja: 1500–2500 kPa.
- Las demás variables, en la caja de M4 (ver la ficha de KF-M04).
- 150 puntos: 15 omitidos y 135 evaluados.

### Datos modificados:
No hay punto base. Respecto a M4 solo cambia el rango de P_baja.

### Métodos aplicados:
LHS, conteo por franjas de 100 kPa de P_baja y de 500 kPa de P_alta, y conteo de los criterios que fallan.

### Resultados obtenidos:
- **135 evaluados: 120 genuinos, 75 KALINA (45 confiables)** (A4, V14).
- **Hay KALINA en todas las franjas, de 1500 a 2500 kPa**, con un 33–75 % de KALINA por franja.
  El KALINA de mayor P_baja tiene 2494.5 kPa.
- Dentro de esta zona, los no KALINA fallan por O2 (44 de 45).
- Los KALINA de M4c tienen r_P de 1.16 a 3.04, y η baja: mediana de 4.35 % y máximo de 8.35 %.
- Tablas: TAB-M04c-00 a -03. Figura FIG-M04c-01 (% de KALINA por franja).

### Conclusiones del caso:
1. **No hay un techo de clasificación entre 1500 y 2500 kPa**: KALINA sigue apareciendo.
2. **Lo que limita una P_baja alta es la razón de presiones y la eficiencia, no la cavitación**:
   con P_baja alta, r_P se acerca a 1, el ciclo produce poco trabajo y η cae.
3. Con M4/M4b, **la P_baja de los KALINA va de ~550 a ~2500 kPa** en toda la caja explorada.

### Advertencias, supuestos y limitaciones:
- 150 puntos en 10 dimensiones: el techo está acotado por los puntos muestreados; no es una frontera calculada.
- El KALINA de mayor P_baja (2494.5 kPa) es el único sin verificación B (por 0.02 kJ/kg sobre el umbral).
- 30 de los 75 KALINA están fuera de rango.
- La franja 1300–1500 kPa viene de M4/M4b, otra muestra: no se compara punto a punto con M4c.

### Recomendaciones:
Para el diseño, una P_baja alta no tiene interés práctico: la eficiencia cae. Recomendar presiones
dentro de la ventana de M4/M4b y mencionar M4c solo para decir que el límite superior es de
eficiencia, no de factibilidad.

**Fuentes:** `resultados/2026-10-07_final_M4c/REPORTE_M4c.md` (incluida la nota del director), `m4c_lhs.csv`, `m4c_techo.csv`, `m4c_techo_por_palta.csv`; A4 (V14).

# FICHA KF-M04 + KF-M04b — Sensibilidad global: LHS de 500 puntos (10 variables a la vez)

> **Antes de leer**
> - **LHS (muestreo latino hipercúbico):** forma de repartir puntos al azar en una "caja" de rangos,
>   de modo que cada variable quede bien cubierta de punta a punta.
> - **Caja:** el rango en que se mueve cada variable. No hay punto base: las 10 variables se mueven a la vez.
> - **RSA / KS:** compara la distribución de cada variable entre los KALINA y el resto. KS va de 0 a 1;
>   cuanto más alto, más decide esa variable si el ciclo sale KALINA.
> - **PRCC:** mide si subir una variable sube (+) o baja (−) la eficiencia η, descontando el efecto de las demás.
> - **p5–p95:** el rango donde está el 90 % central de los KALINA.
> - **Piso de O2 = T_sumidero:** la cavitación se evalúa con el clima de cada punto.
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades y con
>   todas sus η y ε en [0.40, 0.95].

### ID del caso:
`KF-M04` (300 puntos, semilla 20261006) y `KF-M04b` (200 puntos, semilla 20261007). Ambos forman
el bloque **B07**: misma caja y mismo piso de O2, así que se analizan juntos. Familia **G**
(sensibilidad global), diseño LHS. 2026-10-06/07, commits `4fd325b` y `d82219b`.

### Nombre del caso:
Qué variables deciden que el ciclo sea KALINA y en qué ventana de presiones vive.

### Objetivo del barrido:
Saber qué variables separan los KALINA del resto, en qué rango, y en qué ventana de P_alta,
P_baja, ΔP y r_P aparece KALINA.

### ¿Qué se barrió?
Las 10 variables a la vez, dentro de una caja realista y favorable.

### ¿Por qué se barrió?
M3 (una variable a la vez) no ve interacciones entre variables. Este caso es el análisis global que
el protocolo exige para cerrar ese hueco.

### Datos o variables barridas:

| Variable | Caja | Unidad |
|---|---|---|
| T_fuente | 380 – 500 | K |
| T_sumidero | 278.15 – 303.55 | K |
| P_alta | 2000 – 5000 | kPa |
| P_baja | 300 – 1500 | kPa |
| x_b | 0.50 – 0.85 | – |
| η_t | 0.75 – 0.92 | – |
| η_p | 0.65 – 0.90 | – |
| ε_HRVG / ε_reg | 0.60 – 0.95 | – |
| ε_cond | 0.70 – 0.95 | – |

### Datos modificados:
No hay punto base: todas las variables se sortean dentro de la caja. Solo quedan fijos m_b = 1 kg/s,
el motor teqp y la regla de piso de O2 = T_sumidero.

### Métodos aplicados:
LHS; RSA con KS, valor p e intervalo bootstrap (1000 remuestreos); PRCC sobre η; PAWN; árbol CART;
prueba de convergencia del ranking (300 contra 500 puntos, ρ = 0.93). Ver MATEMATICA §6.

### Resultados obtenidos:
- **500 corridas: 452 genuinas, 121 KALINA (83 confiables) y 222 fuera de rango** (A4, V12).
- **Ventana de presiones de los KALINA (p5–p95)** (A4, V13):

| Magnitud | p5 – p95 | mín – máx | Unidad |
|---|---|---|---|
| P_alta | 2156 – 4842 | 2005 – 4961 | kPa |
| P_baja | 683 – 1461 | 547 – 1493 | kPa |
| ΔP = P_alta − P_baja | 968 – 3718 | 710 – 4117 | kPa |
| r_P = P_alta / P_baja | 1.69 – 5.34 | 1.55 – 8.38 | – |

- **Qué decide KALINA (KS, los 121 KALINA contra los 379 puntos restantes):**
  - P_baja (0.43) y ε_cond (0.43) son las que más deciden.
  - Les siguen r_P (0.35), T_fuente (0.29), T_sumidero (0.20) y x_b (0.19).
  - η_t, η_p, ε_HRVG y ε_reg casi no deciden la clase (KS < 0.13, p > 0.1).
- **Qué mueve η (PRCC, 430 genuinos con W_net > 0):**
  - Bajan η: P_baja (−0.68).
  - Suben η: P_alta (+0.58), η_t (+0.38), T_fuente (+0.29), ε_reg (+0.27) y x_b (+0.24).
- **La ventana de P_baja crece con P_alta:**
  - con P_alta de 2000 a 2500 kPa, los KALINA tienen P_baja ≥ 913 kPa;
  - con P_alta de 3500 a 4000 kPa, bajan hasta 547 kPa.
- Fuera de la ventana, el criterio que rompe es casi siempre O2: 324 de los 331 genuinos no KALINA (REPORTE_M4b §6).
- Tablas: TAB-M04-00 a -07. Figuras FIG-M04-01 (CDF), -02 (plano de presiones), -03 (PRCC) y -04 (ΔP y r_P).

### Conclusiones del caso:
1. **P_baja es la variable que más decide KALINA**: los KALINA están en 683–1461 kPa (p5–p95),
   mientras que los no KALINA se concentran en presiones bajas (mediana de 767 kPa).
2. **La efectividad del condensador (ε_cond) decide tanto como P_baja**: con el condensador poco
   efectivo, la cavitación (O2) no se cumple.
3. **El 90 % de los KALINA tiene r_P entre 1.7 y 5.3.** Por encima de 5.3, los no KALINA dominan
   (120 de 331), fallando O2 y a veces O1.
4. **Lo que favorece KALINA y lo que favorece η van en sentidos opuestos en P_baja**: subirla ayuda
   a cumplir O2, pero baja η. Por eso los óptimos de η quedan al filo de O2 (ver M7).

### Advertencias, supuestos y limitaciones:
- La unión de dos LHS no es un LHS estricto de 500; cada mitad sí lo es.
- 222 de 500 puntos están fuera de rango: sus η se toman con cautela. Los rangos de presión se
  calcularon con todos los KALINA (121), no solo con los confiables (83).
- Es una caja: fuera de ella no se dice nada. Por ejemplo, P_baja > 1500 kPa se estudia en M4c.
- Diferencias de η menores que 0.7 pp no son concluyentes.

### Recomendaciones:
- Presentar la ventana de presiones como "el 90 % de los KALINA" (p5–p95) junto con el mínimo y el
  máximo, no como un límite duro.
- Agregar los rangos calculados solo con KALINA confiables, para el informe (lo hace A2 en TAB-G03).

**Fuentes:** `resultados/2026-10-06_final_M4/REPORTE_M4.md` (§14, nota del director), `resultados/2026-10-07_final_M4b/REPORTE_M4b.md`, `m4b_rsa.csv`, `m4b_prcc.csv`, `m4b_rangos_presiones.csv`, `m4b_ventana_por_*.csv`; A4 (V12, V13).

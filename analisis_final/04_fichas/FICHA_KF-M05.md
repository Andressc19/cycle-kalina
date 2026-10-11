# FICHA KF-M05 — ¿Qué datos del profesor se pueden conservar y aun así tener KALINA?

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80.
> - **Escenario:** grupo de datos del profesor que se deja fijo. Las demás variables se sortean (LHS).
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades
>   (sin líquido por encima de 420 K) y con todas sus η y ε en [0.40, 0.95].
> - **O2:** cavitación.

### ID del caso:
`KF-M05`, con 5 subcasos (KF-M05-1 a KF-M05-5 = escenarios S1 a S5). Cada escenario es su propio
bloque (**B09-1 … B09-5**), porque fija datos distintos. Familia **C** (conservación), diseño LHS de
120 puntos por escenario. 2026-10-07, commit `91082fa`.

### Nombre del caso:
Escenarios de conservación de datos del profesor.

### Objetivo del barrido:
Ver qué subconjuntos de datos del profesor se pueden mantener tal cual, y en qué rangos tienen que
estar las demás variables, en especial las presiones.

### ¿Qué se barrió?
En cada escenario, las variables **no** conservadas, dentro de una caja: P_alta 2000–5000 kPa,
P_baja 200–2000 kPa, T_fuente 380–623.15 K, T_sumidero 278.15–303.55 K, x_b 0.50–0.85 y
η/ε 0.40–0.95.

### ¿Por qué se barrió?
El usuario priorizó saber cuánto del enunciado se puede conservar, por encima de maximizar η.

### Datos o variables barridas:

| Escenario | Variables sorteadas (LHS, 120 puntos) | Rangos |
|---|---|---|
| S1 | P_alta, P_baja, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond | P_alta 2000–5000 kPa · P_baja 200–2000 kPa · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| S2 | T_fuente, T_sumidero, x_b, η_t, η_p, ε (×3) | T_fuente 380–623 K · T_sumidero 278–303.5 K · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| S3 | T_fuente, x_b, η_t, η_p, ε (×3) | T_fuente 380–623 K · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| S4 | P_baja, x_b, η_t, η_p, ε (×3) | P_baja 200–2000 kPa · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| S5 | T_sumidero, P_alta, P_baja, η_t, η_p, ε (×3) | T_sumidero 278–303.5 K · P_alta 2000–5000 kPa · P_baja 200–2000 kPa · η/ε 0.40–0.95 |

600 puntos en total: 2 omitidos y 598 evaluados. El piso de O2 es la T_sumidero de cada punto.

### Datos modificados:

| Escenario | Datos del profesor conservados exactamente | Datos del profesor que se abandonan |
|---|---|---|
| S1 | T_fuente 623.15 K, T_sumidero 300.03 K | los otros 8 (se sortean) |
| S2 | P_alta 3000 kPa, P_baja 400 kPa | los otros 8 |
| S3 | P_alta, P_baja y T_sumidero 300.03 K | los otros 7 |
| S4 | P_alta 3000 kPa, T_fuente 623.15 K y T_sumidero 300.03 K | los otros 7 |
| S5 | T_fuente 623.15 K y x_b 0.50 | los otros 8 |

### Métodos aplicados:
Un LHS por escenario (semilla 20261007 + k) y rangos p5–p95 dentro de KALINA. Se buscó también el
KALINA más parecido al profesor.

### Resultados obtenidos (A4, V15):

| Escenario | KALINA | KALINA confiables | Lectura |
|---|---|---|---|
| S1 (sus temperaturas) | 4 | **2** | posible, pero con P_baja muy alta (~1400–1950 kPa) |
| S2 (sus presiones) | 0 | 0 | el muestreo no lo encontró; **sí existe** en una franja angosta (M2R y M5c) |
| S3 (presiones + clima) | 0 | 0 | ídem |
| S4 (P_alta + temperaturas) | 6 | **0** | todos fuera de rango |
| S5 (fuente + x_b) | 10 | **0** | todos fuera de rango |

- El bloqueo dominante en todos los escenarios es O2.
- 322 de los 598 evaluados están fuera de rango.
- Tablas: TAB-M05-00 a -03. Figuras FIG-M05-S1 a FIG-M05-S5 (una por escenario).

### Conclusiones del caso:
1. **Conservar la fuente del profesor (623 K) casi nunca da un KALINA confiable.** De 20 KALINA en
   los escenarios con esa fuente (S1, S4 y S5), solo 2 son confiables, ambos de S1, y requieren alejarse
   mucho del resto del enunciado: P_baja de 1.36 y 1.97 MPa, x_b de 0.83 y 0.71 y ε_HRVG de ~0.5. M7 (arranque A3)
   confirma que con 623 K hay KALINA confiables solo con x_b alta (~0.85) y presiones altas.
2. **Las presiones del profesor sí son conservables**, pero solo en una franja angosta (T_fuente
   ≈ 390–410 K con un condensador muy efectivo). Un muestreo de 120 puntos no la encuentra; por
   eso se hizo M5c, una malla dirigida.
3. La pregunta "¿qué se conserva?" se responde mejor con búsquedas dirigidas (M5c, M9) que con
   muestreo al azar.

### Advertencias, supuestos y limitaciones:
- 120 puntos por escenario es una exploración, no un mapa.
- El reporte original declaraba S2 y S3 "no factibles". El director lo corrigió: es un efecto del
  muestreo, no de la física.
- Los escenarios no se comparan entre sí punto a punto: cada uno fija datos distintos.

### Recomendaciones:
- No presentar S4/S5 como opciones de diseño: no hay KALINA confiables.
- Usar M5c y M9 para las conclusiones sobre conservación.

**Fuentes:** `resultados/2026-10-07_final_M5/REPORTE_M5.md` (§6 y §7b, nota del director), `m5_lhs.csv`, `m5_resumen.csv`, `m5_rangos.csv`; `conteo_por_subcaso.csv`; A4 (V15).

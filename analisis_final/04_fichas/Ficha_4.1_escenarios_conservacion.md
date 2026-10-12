# Ficha 4.1 — ¿Qué datos del profesor se pueden conservar y aun así tener KALINA?

> **Antes de leer**
> - **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50,
>   T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
>   ε_reg = 0.75, ε_cond = 0.80.
> - **Escenario:** grupo de datos del profesor que se deja fijo. Las demás variables se sortean (LHS).
> - **KALINA confiable:** KALINA dentro del rango validado del modelo de propiedades
>   (sin líquido por encima de 420 K) y con todas sus η y ε en [0.40, 0.95].
> - **O2:** cavitación.

### ID del caso:
**Estudio 4.1** · Escenarios de conservación. Responde la pregunta 4: ¿Qué datos del profesor se pueden conservar?
**Partes** (cada letra tiene sus propios datos fijos; solo se comparan puntos de la misma parte): 4.1a (conserva sus temperaturas); 4.1b (conserva sus presiones); 4.1c (conserva sus presiones y su clima); 4.1d (conserva su P_alta y sus temperaturas); 4.1e (conserva su fuente y su x_b).
Familia **C** · 2026-10-07 · commit `91082fa` · código de origen: M05.

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
| 4.1a | P_alta, P_baja, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond | P_alta 2000–5000 kPa · P_baja 200–2000 kPa · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| 4.1b | T_fuente, T_sumidero, x_b, η_t, η_p, ε (×3) | T_fuente 380–623 K · T_sumidero 278–303.5 K · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| 4.1c | T_fuente, x_b, η_t, η_p, ε (×3) | T_fuente 380–623 K · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| 4.1d | P_baja, x_b, η_t, η_p, ε (×3) | P_baja 200–2000 kPa · x_b 0.50–0.85 · η/ε 0.40–0.95 |
| 4.1e | T_sumidero, P_alta, P_baja, η_t, η_p, ε (×3) | T_sumidero 278–303.5 K · P_alta 2000–5000 kPa · P_baja 200–2000 kPa · η/ε 0.40–0.95 |

600 puntos en total: 2 omitidos y 598 evaluados. El piso de O2 es la T_sumidero de cada punto.

### Datos modificados:

| Escenario | Datos del profesor conservados exactamente | Datos del profesor que se abandonan |
|---|---|---|
| 4.1a | T_fuente 623.15 K, T_sumidero 300.03 K | los otros 8 (se sortean) |
| 4.1b | P_alta 3000 kPa, P_baja 400 kPa | los otros 8 |
| 4.1c | P_alta, P_baja y T_sumidero 300.03 K | los otros 7 |
| 4.1d | P_alta 3000 kPa, T_fuente 623.15 K y T_sumidero 300.03 K | los otros 7 |
| 4.1e | T_fuente 623.15 K y x_b 0.50 | los otros 8 |

### Métodos aplicados:
Un LHS por escenario (semilla 20261007 + k) y rangos p5–p95 dentro de KALINA. Se buscó también el
KALINA más parecido al profesor.

### Resultados obtenidos (validación V15):

| Escenario | KALINA | KALINA confiables | Lectura |
|---|---|---|---|
| 4.1a (sus temperaturas) | 4 | **2** | posible, pero con P_baja muy alta (~1400–1950 kPa) |
| 4.1b (sus presiones) | 0 | 0 | el muestreo no lo encontró; **sí existe** en una franja angosta (estudio 2.3 y estudio 4.2) |
| 4.1c (presiones + clima) | 0 | 0 | ídem |
| 4.1d (P_alta + temperaturas) | 6 | **0** | todos fuera de rango |
| 4.1e (fuente + x_b) | 10 | **0** | todos fuera de rango |

- El bloqueo dominante en todos los escenarios es O2.
- 322 de los 598 evaluados están fuera de rango.
- Tablas: 4.1-1, 4.1-2, 4.1-3, 4.1-4. Figuras: 4.1-1, 4.1-2, 4.1-3, 4.1-4, 4.1-5.

### Conclusiones del caso:
1. **Conservar la fuente del profesor (623 K) casi nunca da un KALINA confiable.** De 20 KALINA en
   los escenarios con esa fuente (4.1a, 4.1d y 4.1e), solo 2 son confiables, ambos de 4.1a, y requieren alejarse
   mucho del resto del enunciado: P_baja de 1.36 y 1.97 MPa, x_b de 0.83 y 0.71 y ε_HRVG de ~0.5. estudio 5.1 (arranque 5.1c)
   confirma que con 623 K hay KALINA confiables solo con x_b alta (~0.85) y presiones altas.
2. **Las presiones del profesor sí son conservables**, pero solo en una franja angosta (T_fuente
   ≈ 390–410 K con un condensador muy efectivo). Un muestreo de 120 puntos no la encuentra; por
   eso se hizo estudio 4.2, una malla dirigida.
3. La pregunta "¿qué se conserva?" se responde mejor con búsquedas dirigidas (estudio 4.2, estudio 4.3) que con
   muestreo al azar.

### Advertencias, supuestos y limitaciones:
- 120 puntos por escenario es una exploración, no un mapa.
- El reporte original declaraba 4.1b y 4.1c "no factibles". El director lo corrigió: es un efecto del
  muestreo, no de la física.
- Los escenarios no se comparan entre sí punto a punto: cada uno fija datos distintos.

### Recomendaciones:
- No presentar 4.1d y 4.1e como opciones de diseño: no hay KALINA confiables.
- Usar estudio 4.2 y estudio 4.3 para las conclusiones sobre conservación.

**Fuentes:** `resultados/2026-10-07_final_M5/REPORTE_M5.md` (§6 y §7b, nota del director), `m5_lhs.csv`, `m5_resumen.csv`, `m5_rangos.csv`; `conteo_por_subcaso.csv`; validación V15.

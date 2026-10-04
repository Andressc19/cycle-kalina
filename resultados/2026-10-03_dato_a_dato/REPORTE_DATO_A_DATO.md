# Reporte — Tu motor vs DWSIM, dato a dato, en 6 ciclos Kalina

Fecha: 2026-10-03. Ejecutado por Claude (a pedido). `src/` sin cambios.

## La pregunta

En ciclos Kalina dentro del rango donde DWSIM funciona bien (P_alta = 3000 kPa), ¿cuánto
difieren tu código y DWSIM en cada estado y en cada componente, incluida la entalpía? ¿El
patrón se mantiene al cambiar de ciclo?

## Cómo funciona (en simple)

- **Ciclos**: 6 puntos KALINA de `resultados/2026-09-27_teqp_verificado/regresion_22.csv`,
  todos con P_alta = 3000 kPa, T_sumidero = 283 K, ε = 0.85/0.80/0.85, η_t = η_p = 0.80,
  ṁ = 1 kg/s; varían x_b (0.60–0.75) y T_fuente (394 / 423 K).
- **Mismas ecuaciones**: DWSIM se resolvió con tu cierre por efectividad; la única diferencia
  es el modelo de propiedades (Tillner-Roth & Friend vs Peng-Robinson).
- **Entalpía comparable**: cada modelo tiene su propio cero, así que se compara
  **h_rel = h − h(P_alta, T0, x_estado)** = "entalpía por encima de la misma mezcla líquida a
  300 K". Las energías de cada equipo (Q, W) no dependen de esa referencia.

## Cómo se hizo

- `scripts/dwsim/dato_a_dato_motor.py <ciclo>` (.venv, motor real; 10–19 min/ciclo; los 5
  nuevos en paralelo) → `motor_<ciclo>.json`. η coincide con `regresion_22.csv`.
- `scripts/dwsim/dato_a_dato_dwsim.py <ciclos>` (DWSIM-PR; ~30 s/ciclo, arranca de los
  estados del motor) → `dwsim_<ciclo>.json`. Los 6 convergieron (8–9 iteraciones), todos los
  equipos cuadran (|dif| ≤ 0.0003 kW), cierre global ≤ 0.007 kW, ε resultantes = pedidas
  (|Δε| ≤ 2.4e-5).
- `scripts/dwsim/comparar_dato_a_dato.py <ciclos>` → `estados_<ciclo>.csv`,
  `componentes_<ciclo>.csv`, `resumen_ciclos.csv`, `comparacion_consola.txt`.

## Resultados

### Resumen por ciclo

| Ciclo | x_b | T_fuente | η motor | η DWSIM | Δη | máx \|ΔT\| | máx \|Δh_rel\| estados líquidos fríos* | máx \|Δh_rel\| estados con vapor | Δṁ turbina | ΔWt | ΔWp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KALINA-01 | 0.60 | 394 K | 10.370 % | 10.741 % | +0.37 pp | 1.69 K | 3.6 kJ/kg | 23.3 kJ/kg | +6.1 % | +7.1 % | +10.7 % |
| KALINA-03 | 0.60 | 423 K | 9.615 % | 9.924 % | +0.31 pp | 2.62 K | 3.6 kJ/kg | 9.8 kJ/kg | +2.0 % | +2.7 % | +11.2 % |
| KALINA-06 | 0.65 | 394 K | 9.860 % | 10.066 % | +0.21 pp | 1.22 K | 3.0 kJ/kg | 23.9 kJ/kg | +3.6 % | +4.7 % | +10.5 % |
| KALINA-09 | 0.65 | 423 K | 8.422 % | 8.624 % | +0.20 pp | 2.27 K | 4.4 kJ/kg | 9.8 kJ/kg | +1.2 % | +1.9 % | +11.2 % |
| KALINA-12 | 0.70 | 394 K | 9.054 % | 9.151 % | +0.10 pp | 0.92 K | 3.1 kJ/kg | 24.4 kJ/kg | +2.2 % | +3.3 % | +9.9 % |
| KALINA-17 | 0.75 | 394 K | 8.135 % | 8.158 % | +0.02 pp | 0.85 K | 3.3 kJ/kg | 24.9 kJ/kg | +1.2 % | +2.3 % | +9.1 % |

\* Estados 1, 6, 7, 9, 10 (líquido a ≤ 356 K). El estado 5 (líquido pobre a la salida del
separador, ~383–414 K) llega a 9.8–10.7 kJ/kg con T_fuente = 423 K; con 394 K queda ≤ 1.9 kJ/kg. Detalle por estado y por
equipo de cada ciclo en `estados_<ciclo>.csv` y `componentes_<ciclo>.csv`.

### Comportamiento por equipo (los 6 ciclos)

| Equipo | Qué pasa en todos los ciclos |
|---|---|
| Separador, absorbedor, válvula | Balance = 0 en los dos modelos (h6 = h7; sin pérdidas). |
| Regenerador | Lado caliente = lado frío en los dos; diferencia entre modelos −2.9 % a +0.3 %. |
| HRVG (Qi) | +1.6 a +3.2 % con T_fuente = 394 K; −0.9 % con 423 K. |
| Condensador (Qout) | +1.6 a +2.7 % con 394 K; −1.1 a −1.2 % con 423 K. |
| Turbina (Wt) | Siempre mayor en DWSIM (+1.9 a +7.1 %), sobre todo por más caudal (ṁ3 +1.2 a +6.1 %). |
| Bomba (Wp) | Siempre ~10 % mayor en DWSIM (+9.1 a +11.2 %), en todos los ciclos. |

## Conclusión

- **Los 6 ciclos cuentan la misma historia**: temperaturas dentro de ±2.6 K, composiciones
  globales exactas, balances internos idénticos (separador, absorbedor, válvula,
  regenerador) y entalpías de los estados líquidos fríos dentro de ~4.4 kJ/kg.
- **La diferencia es sistemática y ordenada, no aleatoria**: DWSIM da η mayor en los 6, y la
  brecha baja de forma regular al subir x_b (con 394 K: 0.37 → 0.21 → 0.10 → 0.02 pp para
  x_b 0.60 → 0.65 → 0.70 → 0.75). Un error de programación no produciría un patrón tan
  suave; un modelo de propiedades distinto sí.
- **De dónde sale**: (1) PR predice más vapor en el separador → más caudal a la turbina;
  (2) PR da ~10 % más trabajo de bomba en todos los ciclos, firma de una diferencia
  sistemática del líquido (probablemente volumen específico; no medido); (3) las entalpías
  de los estados con vapor difieren hasta ~25 kJ/kg.
- **Para tu código**: refuerza lo de KALINA-01 con 5 ciclos más — la implementación de las
  ecuaciones (topología, balances, cierre por efectividad) es coherente con un simulador
  independiente; las diferencias se explican por el modelo de propiedades.

## Lo que no sabemos

- Cuál modelo se acerca más a la realidad en cada dato: es una comparación entre modelos. Las
  propiedades de tu motor se apoyan en IAPWS G4-01 (incertidumbre de entalpía de exceso
  ±11–12 kJ/kg, CONTEXT.md); las diferencias en estados con vapor (hasta 25 kJ/kg) superan
  esa banda.
- Por qué la brecha de η se achica con x_b alto (lo más probable: con mezcla más rica el
  vapor es casi NH3 puro y ambos modelos lo describen parecido; no demostrado).
- La causa exacta del +10 % de la bomba (no se midió el volumen del líquido).
- Fuera de 3000 kPa: no hay datos de DWSIM a 4000–5000 kPa (falla su flash) y el único punto
  a 1500 kPa es Elsayed (otras ε).

## Qué sigue

1. Confirmar la causa de la bomba comparando el volumen específico del estado 9 en ambos
   modelos (rápido).
2. Decidir si esta comparación entra a `PLANTEAMIENTO_MATEMATICO.md` §7 y si se versiona
   `scripts/dwsim/` y estas carpetas de resultados.

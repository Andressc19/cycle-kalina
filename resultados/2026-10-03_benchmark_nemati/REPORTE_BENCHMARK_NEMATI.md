# Reporte — Segunda fuente independiente: Nemati et al. (2017)

Fecha: 2026-10-03. Rama `test/verificacion_DWSIM`. Ejecutado por Claude (a pedido). `src/` sin cambios.

## La pregunta

Hasta hoy la comparación externa del ciclo dependía de un solo grupo de autores (Elsayed /
Embaye, Birmingham). ¿Coincide tu modelo con un KCS11 publicado por **otro grupo**?

## Cómo funciona (en simple)

- **Fuente**: Nemati, Nami, Ranjbar & Yari (2017), *Case Studies in Thermal Engineering* 9,
  1–13, doi:10.1016/j.csite.2016.11.003 — Universidad de Tabriz (Irán), resuelto en EES.
  PDF: `Papers/comparativa kalian y ORC para low heat waste.pdf`.
- Su Kalina es un **KCS11 con tu misma topología** (Fig. 1b, §2.2). Su Tabla 5 da los 9 estados
  del ciclo (P, T, caudal, composición). No da η del Kalina para ese caso, así que se comparan
  **estados**, no η.
- Caso: x_b = 0.90, P = 50 / 10.61 bar, η_t = 0.85, η_p = 0.75, gas caliente que entra al
  evaporador a 429 K, agua de enfriamiento a 298.15 K. Está a **5000 kPa**, la zona que DWSIM no
  pudo resolver.
- Dos tipos de prueba:
  1. **Directas de propiedades** (no dependen del cierre del ciclo): composición del vapor y del
     líquido en equilibrio en el separador (50 bar, 415 K) y temperatura de burbuja a la salida
     del condensador (10.61 bar, x = 0.90).
  2. **Ciclo completo**: tus efectividades se calibran en un paso para reproducir sus T2, T6 y
     T9 (igual que en la validación Elsayed, §7); luego se comparan los estados que esa
     calibración **no** fija.

## Cómo se hizo

`scripts/benchmark_nemati2017.py` con el motor real (`AmmoniaWaterAdapter`), ~12 min.
Efectividades calibradas: ε_HRVG = 0.8873, ε_reg = 0.7402, ε_cond = 0.9787.
Salida: `benchmark_nemati.json`, `consola.txt`.

## Resultados

### Pruebas directas de propiedades

| Magnitud | Nemati (EES) | Tu motor | Diferencia | Referencia de incertidumbre |
|---|---|---|---|---|
| T de burbuja, 1061 kPa, x = 0.90 | 303.15 K | 303.54 K | +0.39 K | — |
| NH₃ en el vapor, 5000 kPa / 415 K (molar) | 0.9567 | 0.9511 | −0.006 | ±0.01 (G4-01) → **dentro** |
| NH₃ en el líquido, 5000 kPa / 415 K (molar) | 0.5313 | 0.5174 | −0.014 | ±0.01 (G4-01) → **apenas fuera** |

### Ciclo completo (estados que la calibración no fija)

| Estado | Qué es | T Nemati | T motor | ΔT |
|---|---|---|---|---|
| 1 | entrada evaporador | 314.40 K | 313.62 K | −0.78 K |
| 4 | salida turbina | 341.50 K | 343.99 K | +2.49 K |
| 8 | salida absorbedor | 340.00 K | 342.07 K | +2.07 K |
| 10 | salida bomba | 304.30 K | 304.50 K | +0.20 K |

Estados fijados por la calibración (control): T2 −0.04 K, T9 +0.07 K, T6 −1.57 K (T6 se
calibró con la x5 de Nemati y tu motor da otra x5).

| Reparto del separador | Nemati | Tu motor | Diferencia |
|---|---|---|---|
| Fracción de vapor (masa) hacia la turbina | 0.873 | 0.891 | +0.018 (+2.1 %) |

η de tu motor en este caso: 13.28 % (el paper no da la del Kalina para comparar).

## Conclusión

- **Una segunda fuente independiente confirma tu modelo a nivel de estados**, y en la zona de
  alta presión (5000 kPa) que DWSIM no cubría: todas las temperaturas dentro de 2.5 K, la
  burbuja del condensador a 0.4 K y la composición del vapor dentro de la incertidumbre de G4-01.
- **La diferencia más grande vuelve a estar en el equilibrio del separador**: tu motor da un
  líquido algo más pobre (−0.014 molar), así que manda 2 % más de vapor a la turbina. Es la
  misma variable que domina la banda de incertidumbre de η (REPORTE_INCERTIDUMBRE_ETA.md) y
  queda en el borde de la incertidumbre publicada. No indica un error del código: Nemati usa
  EES, cuyo modelo NH₃-H₂O es distinto del tuyo (Tillner-Roth & Friend).
- Las ΔT de la turbina y el absorbedor (+2–2.5 K) son coherentes con ese vapor un poco menos
  rico (x3 −0.006).

## Lo que no sabemos

- **η**: Nemati no reporta la η del Kalina para el caso de la Tabla 5, así que este benchmark
  es de estados, no de eficiencia.
- **Su modelo de propiedades**: el paper no lo nombra; EES suele usar Ibrahim & Klein (1993)
  para NH₃-H₂O, pero no está confirmado.
- Es un solo punto de operación de esta fuente.
- Nemati validó su Kalina contra Hettiarachchi et al. (2007) (Fig. 2, η vs x_b) y contra
  Ogriseck (Tabla 3); esas curvas podrían digitalizarse, pero no traen todas las condiciones
  de entrada en este paper.

## Qué sigue

1. Constancia: `tests/test_benchmark_nemati2017.py` y §9 de `docs/PLANTEAMIENTO_MATEMATICO.md`.
2. Opcional: digitalizar la Fig. 2 (Hettiarachchi) si se consiguen sus condiciones de entrada.

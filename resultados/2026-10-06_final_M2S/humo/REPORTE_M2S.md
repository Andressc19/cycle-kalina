# REPORTE M2S — efecto de un sumidero frío con P_baja libre
## 1. La pregunta
Si el sitio es más frío y el criterio de cavitación (O2) se evalúa con **ese** clima —el piso de O2 es `T_sumidero`, no el piso tropical heredado—, ¿cuánto baja la P_baja necesaria para KALINA y cuánto sube η?
## 2. Qué se hizo
- **Cuatro bases**, con todo lo demás como `comun.PROFESOR`: B1 `T_fuente` = 403.0 K (el ancla de M3); B2 `T_fuente` = 420.0 K (el KALINA de mayor η de M2); B3 `eps_hrvg` = 0.40 (conserva la fuente de 623.15 K, la ruta de M2R); B4 **ningún cambio** (el profesor exacto).
- **Climas**: `T_sumidero` ∈ {278.15, 283.15, 288.15, 293.15, 300.032917} K, **siempre con `t_amb_diseno = T_sumidero`**: el piso de O2 sigue al clima del sitio.
- **Malla**: `P_baja` ∈ `numpy.linspace(150, 1500, 10)` → 4 × 5 × 10 = **200 corridas** con 5 procesos, cada fila con flush en `m2s_malla.csv`.
- **Bisección**: por cada (base, T_sumidero), sobre P_baja, en cada par de vecinos donde cambia «es KALINA» o donde cambia `m_O2 >= 0` con ambos vecinos genuinos; tolerancia 10 kPa, máximo 7 iteraciones, rondas paralelas. Filas en `m2s_biseccion.csv`.
- **Punto genuino**: `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con `convergio=True` y `NO_CONVERGIO` es espuria (N2) y se trata como NO genuina en conteos, fronteras y conclusiones.
- **Salidas**: `m2s_resumen.csv`, `m2s_kalina.csv` (KALINA sin duplicados), la figura `m2s_pbaja_eta.png` y este reporte.
## 3. Tabla por base (filas: T_sumidero; columnas: P_baja mínima KALINA y su η)

| T_sumidero (K) | B1 P_baja (kPa) | B1 η | B2 P_baja (kPa) | B2 η | B3 P_baja (kPa) | B3 η | B4 P_baja (kPa) | B4 η |
|---|---|---|---|---|---|---|---|---|
| 278.15 | 1500 | 0.0312 | — | — | — | — | — | — |
| 283.15 | 1500 | 0.0320 | — | — | — | — | — | — |
| 288.15 | — | — | — | — | — | — | — | — |
| 293.15 | — | — | — | — | — | — | — | — |
| 300.033 | — | — | — | — | — | — | — | — |
## 4. ¿El sumidero frío solo (B4) vuelve KALINA al profesor?
**No.** Con el profesor exacto (B4) **ninguno** de los 5 climas probados da un punto KALINA: 278.15 K → sin criterio; 283.15 K → sin criterio; 288.15 K → sin criterio; 293.15 K → sin criterio; 300.033 K → sin criterio.
## 5. Cuánto sube η por cada paso de 5 K de sumidero más frío
Variación de η en el punto de P_baja mínima KALINA al bajar el sumidero de un nivel al siguiente (los pasos de 278.15 a 293.15 K son exactamente de 5 K; el último, de 293.15 a 300.032917 K, mide 6.883 K):

- **B1**: 283.15 → 278.15 K (ΔT = 5.000 K): η -0.00078 · 288.15 → 283.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 293.15 → 288.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 300.033 → 293.15 K (ΔT = 6.883 K): — (sin KALINA en un extremo)
- **B2**: 283.15 → 278.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 288.15 → 283.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 293.15 → 288.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 300.033 → 293.15 K (ΔT = 6.883 K): — (sin KALINA en un extremo)
- **B3**: 283.15 → 278.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 288.15 → 283.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 293.15 → 288.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 300.033 → 293.15 K (ΔT = 6.883 K): — (sin KALINA en un extremo)
- **B4**: 283.15 → 278.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 288.15 → 283.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 293.15 → 288.15 K (ΔT = 5.000 K): — (sin KALINA en un extremo) · 300.033 → 293.15 K (ΔT = 6.883 K): — (sin KALINA en un extremo)
## 6. Comparación con Húsavík
Húsavík (sumidero de 5 °C, piso de 10 °C, P_baja de 670–690 kPa y η de 12.7–13.4 %) **es otro ciclo**: x_b = 0.82 y P_alta = 3300 kPa, así que la comparación es de **tendencia, no de valor**.
Nuestro KALINA en los climas más fríos, contra su sumidero de 5 °C con piso de 10 °C:

| Base | T_sumidero (K) | P_baja mínima KALINA (kPa) | η |
|---|---|---|---|
| B1 | 278.15 | 1500 | 0.0312 |
| B1 | 283.15 | 1500 | 0.0320 |
| B2 | 278.15 | — | — |
| B2 | 283.15 | — | — |
| B3 | 278.15 | — | — |
| B3 | 283.15 | — | — |
| B4 | 278.15 | — | — |
| B4 | 283.15 | — | — |
## 7. Tiempos
- Malla: 145 s · Bisección: 0 s · Total: 145 s.
- Por punto (`t_s`): mínimo 129.7 s, mediana 135.3 s, máximo 138.8 s, media 134.2 s (4 puntos).
## 8. Conclusión
- **1 de 4 bases** alcanzan KALINA (B1); hay **2** puntos KALINA sin duplicados en total.
- **B1**: al bajar el sumidero de 283.15 a 278.15 K, η de 0.0320 a 0.0312 (-0.00078) y la P_baja mínima de 1500 a 1500 kPa.
## 9. Lo que no se sabe
- Ninguno de los 2 puntos KALINA queda fuera del rango confiable (IAPWS G4-01).
- En el clima más frío (278.15 K) 0 de 2 puntos no son genuinos (N2 o no convergen): son los que quedan más cerca del límite del motor.
- La malla de P_baja tiene 10 valores entre 150 y 1500 kPa (paso de 150 kPa): una zona KALINA más estrecha que eso no aparece ni en la malla ni en la bisección.
- Esta es una corrida de humo (1 base × 2 T_sumidero × 2 P_baja, sin bisección): las cifras de arriba NO son las de la corrida real.
## 10. Qué sigue
El siguiente paso lo decide el director con la tabla de §3 y la figura `m2s_pbaja_eta.png` (una curva por base: η y P_baja mínimas contra el clima). Aquí no se proponen valores concretos: solo lo medido en la malla y acotado por la bisección.

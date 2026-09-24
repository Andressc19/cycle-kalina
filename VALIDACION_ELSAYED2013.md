# Verificación y validación del modelo KCS11 — IAPWS G4-01 y Elsayed et al. (2013)

Documento de sustento de la validación de `ciclo_kalina_tercero`. Describe **qué** se
comprobó, **cómo** (paso a paso), **con qué datos** y **qué cálculos** se hicieron, de modo
que cada número pueda rastrearse hasta su archivo y reproducirse.

- Versión 1 (2026-09-19): validación de un solo punto contra Elsayed et al. (2013) — sección 7.
- Versión 2 (2026-09-23/24): verificación del motor de propiedades contra IAPWS G4-01 y
  extensión de la comparación con Elsayed a 33 puntos / 23 comparables (tendencias).

---

## 1. Resumen de resultados

| Nivel | Qué se comprueba | Referencia | Resultado |
|---|---|---|---|
| 1. Propiedades | que el motor calcula bien la mezcla NH3-H2O | IAPWS G4-01 (2001), Tablas 6–8 | Motor de referencia: **44/44 valores evaluables dentro de tolerancia** (error ≤ 3·10⁻⁸ en región monofásica) |
| 2. Balances | que el solver conserva masa y energía | primer principio | error relativo < 10⁻⁴ (test automático) |
| 3. Ciclo completo | que el modelo del ciclo reproduce un modelo publicado | Elsayed et al. (2013) / Embaye et al. | **23 puntos comparables: Δη medio −0.06 pp, \|Δη\| medio 0.28 pp, mediana \|Δη\| relativa 2.4 %, máx 1.16 pp**; reproduce forma y posición del máximo de las curvas |

**Cómo debe citarse** (alcance exacto): *verificación del motor de propiedades frente a los
valores oficiales de IAPWS G4-01 y comparación del modelo del ciclo frente a un modelo
publicado (benchmark), en 23 condiciones de operación.* No es una validación experimental
(no hay datos de planta) y la referencia del nivel 3 es **una sola fuente** (ver §4.1).

---

## 2. Modelo que se valida (definiciones usadas en los cálculos)

Ciclo KCS11 de 10 estados (`CONTEXT.md`):

```
10 →[Regenerador]→ 1 →[HRVG]→ 2 →[Separador]→ { 3 →[Turbina]→ 4 ; 5 →[Regenerador]→ 6 →[Válvula]→ 7 }
4 + 7 →[Absorbedor]→ 8 →[Condensador]→ 9 →[Bomba]→ 10
```

- Propiedades: Tillner-Roth & Friend (1998) / IAPWS G4-01, con dos implementaciones:
  `AmmoniaWaterAdapter` (motor de referencia, paquete `iapws`) y `TeqpAdapter` (motor rápido,
  paquete `teqp`).
- Intercambiadores cerrados por **efectividad** (`CONTEXT.md`):
  - HRVG: h₂ = h₁ + ε_HRVG·(h₂,máx − h₁), con h₂,máx = h(P_alta, T_fuente, x_b)
  - Regenerador: h₆ = h₅ − ε_reg·(h₅ − h₆,mín), con h₆,mín = h(P_alta, T₁₀, x₅)
  - Condensador: h₉ = h₈ − ε_cond·(h₈ − h₉,mín), con h₉,mín = h(P_baja, T_sumidero, x_b)
- Rendimiento térmico (`src/cycle_solver.py`):

  **η = W_net / Q_i = (W_t − W_p) / Q_i**

  con W_t potencia de turbina, W_p potencia de bomba y Q_i calor absorbido en el HRVG [kW].

---

## 3. Nivel 1 — Verificación del motor de propiedades contra IAPWS G4-01

### 3.1 Qué es y por qué

IAPWS G4-01 (2001) es la guía oficial de la formulación de Tillner-Roth & Friend (1998) para
la mezcla amoníaco-agua. Su §8 publica valores de verificación "para comprobar
implementaciones". Reproducirlos demuestra que el motor calcula la ecuación de estado
correctamente — es la base de todo lo demás.

### 3.2 Paso a paso

1. Se transcribieron las Tablas 6 (región monofásica: f, p, C_v, w a x, T, ρ dados), 7 (puntos
   de burbuja) y 8 (puntos de rocío) de la guía (`reference/IAPWS_G4-01_nh3h2o.pdf`, §8).
2. Se evaluaron los 12 puntos con los dos motores (`scripts/verificacion_iapws_g4.py`).
3. Criterios fijados **antes** de correr: Tabla 6 p con error relativo < 10⁻⁶; C_v, w < 10⁻⁴;
   Tablas 7–8 presión y densidades < 10⁻³ relativo, composiciones < 10⁻³ absoluto (del orden
   del último dígito publicado).

### 3.3 Resultados (`resultados/2026-09-23_verificacion_iapws_g4/`)

| Motor | Tabla 6 (monofásica) | Tabla 7 (burbuja) | Tabla 8 (rocío) |
|---|---|---|---|
| `AmmoniaWaterAdapter` (referencia) | 24/24 ✔ (peor: p 2.6·10⁻⁸, C_v 9.5·10⁻¹⁰, w 8.5·10⁻¹⁰, f 4.1·10⁻⁹) | 2/3 puntos ✔ | 3/3 ✔ |
| `TeqpAdapter` | p ✔ (≈10⁻¹¹); C_v ✘ (1.2–3.8·10⁻³); w ✘ (2.5–6.1·10⁻⁴); f con desfase | 2/3 puntos ✔ | 3/3 ✔ |

Interpretación:
- **El motor de referencia reproduce la guía oficial al redondeo.**
- En `TeqpAdapter` la parte **residual** (la que describe la mezcla) coincide con la guía; la
  desviación de C_v, w y f proviene de que el adaptador usa la parte de **gas ideal** de
  CoolProp (NH3 y H2O puros) en lugar de la ec. (2) de G4-01. Evidencia: el error de C_v es
  idéntico a alta y baja densidad para cada x (0.098, 0.138, 0.061 J/mol·K), firma de un
  término que depende solo de T. Efecto sobre el ciclo: 0.001 pp en η (§4.10).
- El punto de burbuja x_L = 0.6, T = 500 K falla en **ambos** motores: el algoritmo de flash
  del proyecto converge a la solución trivial (vapor = líquido, 20.6 MPa en vez de
  16.698 MPa). Es una limitación del algoritmo de equilibrio, no de la ecuación; está fuera
  del dominio del ciclo (T ≤ 473 K, P ≤ 5 MPa).

Test persistente: `tests/test_verificacion_iapws_g4.py`.

---

## 4. Nivel 3 — Comparación del ciclo con Elsayed et al. (2013) / Embaye et al.

### 4.1 Fuentes

- **Elsayed, A., Embaye, M., AL-Dadah, R., Mahmoud, S., & Rezk, A. (2013).** Thermodynamic
  performance of Kalina cycle system 11 (KCS11): feasibility of using alternative zeotropic
  mixtures. *International Journal of Low-Carbon Technologies*, 8(suppl_1), i69–i78.
  https://doi.org/10.1093/ijlct/ctt020 (`ctt020.pdf`).
- **Embaye, M., AL-Dadah, R., Mahmoud, S., Elsayed, A., & Rezk, A.** Performance of Kalina
  Cycle System 11 (KCS11) using low temperature heat sources. University of Birmingham
  (versión de congreso) (`PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf`).

**Advertencia de independencia**: ambos documentos son del **mismo grupo y el mismo modelo**
(EES, propiedades Ibrahim & Klein 1993, mismas hipótesis, mismo valor 11.38 %). Se tratan
como **una sola fuente**. Se usa Embaye porque sus figuras son vectoriales (datos exactos) y
contiene más curvas.

### 4.2 Hipótesis del paper y cómo se replicaron

| Hipótesis del paper | Cómo se replica en este modelo |
|---|---|
| η_turbina = η_bomba = 0.80 | igual (`ETA_T = ETA_P = 0.80`) |
| T_sumidero = 283 K | igual |
| Pinch 4 K en evaporador, condensador y regenerador | efectividades **calibradas** por punto para dar T₂ = T_fuente − 4 K, T₉ = T_sumidero + 4 K, T₆ = T₁₀ + 4 K (§4.5) |
| P de condensación no publicada | P_baja = presión de burbuja de la mezcla a (T_sumidero + 4 K, x_b) (§4.5) |
| Propiedades Ibrahim & Klein (1993) | Tillner-Roth & Friend (1998) — **diferencia inevitable**, fuente esperada de discrepancia |
| Título a la salida de turbina ≥ 0.90 | se registra el título del estado 4; puntos con título < 0.90 o no calculable se excluyen de la estadística |

Las efectividades calibradas resultan entre 0.71 y 0.96, fuera de la banda 0.75–0.85 que el
proyecto usa para diseño. Esto es **correcto en validación**: para comparar dos modelos hay
que usar las mismas hipótesis; si no, una diferencia no permitiría saber si el modelo calcula
mal o si simplemente supone otra cosa. La banda 0.75–0.85 aplica al análisis paramétrico
propio, no a la validación.

### 4.3 Paso 1 — Obtención de los datos del paper (extracción vectorial)

1. Se verificó que las figuras de Embaye son vectoriales: páginas 4 y 5 del PDF contienen
   1579 y 4530 elementos de trazado y ninguna imagen (las de `ctt020.pdf` son imágenes
   rasterizadas; dos intentos de digitalizarlas por píxeles se rechazaron en auditoría).
2. Con `pymupdf` se leyeron las coordenadas de cada curva (`scripts/extraer_embaye_vectorial.py`).
3. **Calibración de ejes**: transformación lineal coordenada-PDF → dato con las etiquetas
   extremas de cada eje, comprobada contra las etiquetas intermedias:

   | Figura | Error máx. eje x | Error máx. eje y |
   |---|---|---|
   | Fig. 2 (10 bar) | 0.0003 (fracción) | 0.010 pp |
   | Fig. 3 (15 bar) | 0.0002 | 0.021 pp |
   | Fig. 4 (23.5 bar) | 0.0002 | 0.021 pp |
   | Fig. 5 (32 bar) | 0.0002 | 0.010 pp |
   | Fig. 7 (η vs P) | 0.007 bar | 0.010 pp |

4. **Identificación de series** por el color de la leyenda (Figs. 2–5: azul/rojo/verde =
   333/373/423 K o rojo/verde/negro = 373/423/463 K).
5. **Controles** contra valores escritos en el texto del paper (no usados para calibrar):

   | Control | Extraído | Texto del paper | Diferencia |
   |---|---|---|---|
   | Fig. 3, 373 K, x_b = 0.55 (serie identificada por color) | 11.394 % | 11.38 % | +0.014 pp |
   | Fig. 7, KCS11 x_b = 0.55, 15 bar | 11.432 % | 11.38 % | +0.052 pp |
   | Fig. 7, ORC amoníaco, 15 bar | 6.755 % | ≈ 7 % | — |
   | Fig. 7, ORC R134a, 15 bar | 9.263 % | ≈ 9.2 % | — |

   Las dos figuras del propio paper difieren entre sí 0.04 pp en el mismo punto: ese es el
   nivel de incertidumbre de los datos de referencia.

Datos: `resultados/2026-09-24_embaye_vectorial/curvas_embaye_eta_vs_xb.csv` (400 puntos) y
`curvas_embaye_fig7.csv` (68 puntos).

### 4.4 Paso 2 — Selección de puntos

33 evaluaciones, elegidas para cubrir las tres variables del paper (presión, composición y
temperatura de fuente), **siempre dentro del rango** de cada curva publicada (sin extrapolar):

| Serie | T_fuente [K] | P_alta [kPa] | x_b |
|---|---|---|---|
| Fig. 7 (η vs P) | 373 | 1100, 1200, 1500, 1800, 2000, 2200, 2300 | 0.55 |
| Fig. 7 (η vs P) | 373 | 1100, 1500, 2000, 2500, 3000 | 0.66 |
| Fig. 3 (15 bar) | 373 | 1500 | 0.45, 0.55, 0.65, 0.75, 0.85 |
| Fig. 3 (15 bar) | 423 | 1500 | 0.45, 0.60, 0.75 |
| Fig. 3 (15 bar) | 333 | 1500 | 0.65, 0.75, 0.85 |
| Fig. 2 (10 bar) | 373 | 1000 | 0.45, 0.60, 0.80 |
| Fig. 5 (32 bar) | 423 y 463 | 3200 | 0.60, 0.80 |
| Control de motor (`AmmoniaWaterAdapter`) | 373 / 373 / 423 | 1500 / 2500 / 1500 | 0.55 / 0.66 / 0.60 |

Nota: (Fig. 7, 1500 kPa, 0.55) y (Fig. 3, 373 K, 0.55) son **la misma condición de
operación** comparada contra dos figuras distintas del paper; por eso los 23 puntos
comparables corresponden a 22 condiciones distintas.

### 4.5 Paso 3 — Configuración del modelo en cada punto

Implementado en `scripts/calibracion_elsayed_malla.py` (mismo método aceptado en la v1):

**(a) Presión baja.** Se resuelve con `brentq`:

  T_burbuja(P_baja, x_b) = T_sumidero + 4 K = 287 K

Valores obtenidos: x_b = 0.45 → 161.52 kPa; 0.55 → 273.55 kPa; 0.60 → 336.09 kPa;
0.65 → 398.12 kPa; 0.66 → 410.15 kPa; 0.75 → 508.68 kPa; 0.80 → 554.71 kPa; 0.85 → 595.20 kPa.

**(b) Efectividades.** Primero se resuelve el ciclo con las efectividades por defecto
(ε⁰ = 0.85 / 0.75 / 0.80) para obtener un estado base (superíndice 0). Luego se despejan en
forma cerrada:

  ε_HRVG = [h(P_alta, T_fuente − 4, x_b) − h₁⁰] / [h(P_alta, T_fuente, x_b) − h₁⁰]

  ε_reg = [h₅⁰ − h(P_alta, T₁₀⁰ + 4, x₅⁰)] / [h₅⁰ − h(P_alta, T₁₀⁰, x₅⁰)]

  ε_cond = [h₈⁰ − h(P_baja, T_sumidero + 4, x_b)] / [h₈⁰ − h(P_baja, T_sumidero, x_b)]

limitadas a [0.01, 0.999]; con ellas se resuelve el ciclo de nuevo (resultado final). Es una
calibración de **un paso** (no iterada a punto fijo); en la v1 dejó residuos de 0.1–1.3 K
sobre las temperaturas objetivo (§7).

### 4.6 Paso 4 — Cálculo del modelo

`resolver_ciclo` (tanteo sobre T₁ con `brentq` y lazo interior sobre T₁₀) → estados y
potencias → η = (W_t − W_p)/Q_i. Motor: `TeqpAdapter` en todos los puntos; tres puntos se
repiten con `AmmoniaWaterAdapter` como control. Script: `scripts/validacion_tendencias_embaye.py`.

### 4.7 Paso 5 — Comparación

Para cada punto, η del paper por interpolación lineal entre los dos puntos extraídos que
rodean la abscisa del modelo (x_b o P):

  η_paper(x) = η_a + (η_b − η_a)·(x − x_a)/(x_b − x_a),  con x_a ≤ x ≤ x_b

Desviaciones:

  Δ [pp] = η_modelo − η_paper      Δ_rel [%] = 100·Δ / η_paper

Estadística sobre los N puntos comparables:

  Δ medio = (1/N)·ΣΔᵢ   |Δ| medio = (1/N)·Σ|Δᵢ|   |Δ| máx = máx|Δᵢ|

### 4.8 Ejemplo de cálculo completo (punto x_b = 0.55, P_alta = 15 bar, T_fuente = 373 K)

1. P_baja: T_burbuja(P, 0.55) = 287 K → **P_baja = 273.545 kPa**.
2. Efectividades calibradas: **ε_HRVG = 0.8882, ε_reg = 0.9380, ε_cond = 0.9625**.
3. Ciclo resuelto (`TeqpAdapter`): **W_net = 49.2456 kW**, **η_modelo = 11.0554 %**
   (⇒ Q_i = W_net/η = 49.2456/0.110554 = 445.44 kW).
4. η_paper (Fig. 7, curva x_b = 0.55), puntos extraídos vecinos:
   (14.9815 bar; 11.42677 %) y (15.9515 bar; 11.68386 %):

   η_paper(15) = 11.42677 + (11.68386 − 11.42677)·(15 − 14.9815)/(15.9515 − 14.9815)
             = 11.42677 + 0.25709·0.01908 = **11.4317 %**

5. Δ = 11.0554 − 11.4317 = **−0.3763 pp**; Δ_rel = 100·(−0.3763)/11.4317 = **−3.29 %**.
6. Título a la salida de turbina: 0.9525 ≥ 0.90 → comparable.
7. Control: el mismo punto con `AmmoniaWaterAdapter` da η = 11.0542 % (diferencia entre
   motores 0.0012 pp).

Contra el valor escrito en el texto del paper (11.38 %): Δ = −0.325 pp (−2.9 %), igual que en
la v1.

### 4.9 Resultados — todos los puntos

Fuente: `resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`.
"Comp." = cuenta para la estadística (convergió, η_paper disponible, motor teqp, título ≥ 0.90).

| Serie | T_f [K] | P [kPa] | x_b | Motor | ε_HRVG | ε_reg | ε_cond | η_mod [%] | η_pap [%] | Δ [pp] | Δ_rel [%] | Título 4 | Comp. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig7 0.55 | 373 | 1100 | 0.55 | teqp | 0.913 | 0.929 | 0.971 | 9.359 | 9.781 | −0.422 | −4.31 | 0.956 | sí |
| Fig7 0.55 | 373 | 1200 | 0.55 | teqp | 0.908 | 0.932 | 0.969 | 9.878 | 10.282 | −0.405 | −3.94 | 0.955 | sí |
| Fig7 0.55 | 373 | 1500 | 0.55 | teqp | 0.888 | 0.938 | 0.963 | 11.055 | 11.432 | −0.376 | −3.29 | 0.953 | sí |
| Fig7 0.55 | 373 | 1800 | 0.55 | teqp | 0.855 | 0.943 | 0.954 | 11.706 | 11.989 | −0.284 | −2.37 | 0.952 | sí |
| Fig7 0.55 | 373 | 2000 | 0.55 | teqp | 0.820 | 0.946 | 0.946 | 11.779 | 11.891 | −0.112 | −0.94 | 0.952 | sí |
| Fig7 0.55 | 373 | 2200 | 0.55 | teqp | 0.767 | 0.948 | 0.936 | 11.329 | 10.952 | +0.377 | +3.44 | 0.951 | sí |
| Fig7 0.55 | 373 | 2300 | 0.55 | teqp | 0.728 | 0.949 | 0.929 | 10.706 | 9.547 | +1.159 | +12.14 | 0.950 | sí |
| Fig7 0.66 | 373 | 1100 | 0.66 | teqp | 0.937 | 0.911 | 0.978 | 7.254 | 7.433 | −0.179 | −2.40 | 0.967 | sí |
| Fig7 0.66 | 373 | 1500 | 0.66 | teqp | 0.931 | 0.920 | 0.974 | 9.351 | 9.521 | −0.170 | −1.78 | 0.961 | sí |
| Fig7 0.66 | 373 | 2000 | 0.66 | teqp | 0.911 | 0.932 | 0.968 | 11.022 | 11.167 | −0.146 | −1.30 | 0.959 | sí |
| Fig7 0.66 | 373 | 2500 | 0.66 | teqp | 0.870 | 0.940 | 0.960 | 11.913 | 11.977 | −0.064 | −0.53 | 0.956 | sí |
| Fig7 0.66 | 373 | 3000 | 0.66 | teqp | 0.770 | 0.946 | 0.946 | 11.610 | 11.336 | +0.274 | +2.42 | 0.944 | sí |
| Fig3 15 bar | 373 | 1500 | 0.45 | teqp | 0.763 | 0.949 | 0.931 | 11.557 | 11.042 | +0.515 | +4.67 | 0.943 | sí |
| Fig3 15 bar | 373 | 1500 | 0.55 | teqp | 0.888 | 0.938 | 0.963 | 11.055 | 11.394 | −0.339 | −2.97 | 0.953 | sí |
| Fig3 15 bar | 373 | 1500 | 0.65 | teqp | 0.928 | 0.922 | 0.973 | 9.492 | 9.671 | −0.179 | −1.85 | 0.960 | sí |
| Fig3 15 bar | 373 | 1500 | 0.75 | teqp | 0.948 | 0.897 | 0.979 | 8.290 | 8.319 | −0.029 | −0.34 | 0.966 | sí |
| Fig3 15 bar | 373 | 1500 | 0.85 | teqp | 0.961 | 0.898 | 0.982 | 7.506 | 7.458 | +0.048 | +0.64 | 0.970 | sí |
| Fig3 15 bar | 423 | 1500 | 0.45 | teqp | — | — | — | no converge | — | — | — | — | no |
| Fig3 15 bar | 423 | 1500 | 0.60 | teqp | 0.917 | 0.949 | 0.987 | 9.845 | 10.106 | −0.261 | −2.58 | 0.940 | sí |
| Fig3 15 bar | 423 | 1500 | 0.75 | teqp | — | — | — | no converge | — | — | — | — | no |
| Fig3 15 bar | 333 | 1500 | 0.65 | teqp | — | — | — | no converge | — | — | — | — | no |
| Fig3 15 bar | 333 | 1500 | 0.75 | teqp | 0.708 | 0.867 | 0.955 | 7.235 | 7.356 | −0.121 | −1.64 | n/c | no |
| Fig3 15 bar | 333 | 1500 | 0.85 | teqp | 0.888 | 0.706 | 0.973 | 6.876 | 6.939 | −0.063 | −0.91 | n/c | no |
| Fig2 10 bar | 373 | 1000 | 0.45 | teqp | — | — | — | no converge | — | — | — | — | no |
| Fig2 10 bar | 373 | 1000 | 0.60 | teqp | 0.928 | 0.916 | 0.976 | 7.686 | 7.988 | −0.302 | −3.78 | 0.963 | sí |
| Fig2 10 bar | 373 | 1000 | 0.80 | teqp | 0.952 | 0.926 | 0.983 | 4.760 | 4.690 | +0.070 | +1.50 | 0.979 | sí |
| Fig5 32 bar | 423 | 3200 | 0.60 | teqp | 0.930 | 0.960 | 0.977 | 14.909 | 15.203 | −0.294 | −1.93 | 0.915 | sí |
| Fig5 32 bar | 423 | 3200 | 0.80 | teqp | 0.952 | 0.947 | 0.984 | 13.077 | 13.065 | +0.012 | +0.09 | 0.928 | sí |
| Fig5 32 bar | 463 | 3200 | 0.60 | teqp | 0.917 | 0.961 | 0.988 | 13.968 | 14.278 | −0.310 | −2.17 | 0.903 | sí |
| Fig5 32 bar | 463 | 3200 | 0.80 | teqp | — | — | — | no converge | — | — | — | — | no |
| Fig7 0.55 | 373 | 1500 | 0.55 | iapws | 0.888 | 0.938 | 0.962 | 11.054 | 11.432 | −0.378 | −3.30 | 0.953 | control |
| Fig7 0.66 | 373 | 2500 | 0.66 | iapws | 0.870 | 0.940 | 0.960 | 11.912 | 11.977 | −0.065 | −0.54 | 0.956 | control |
| Fig3 15 bar | 423 | 1500 | 0.60 | iapws | — | — | — | no converge | — | — | — | — | control |

n/c = el título del estado 4 no se pudo calcular (el cálculo de fase falló); el ciclo sí convergió.

### 4.10 Estadística global

N = 23 puntos comparables (motor teqp; los 2 puntos del motor iapws son control de motor y no
se suman). Valores recalculados directamente del CSV:

| Métrica | Valor |
|---|---|
| Δ medio (sesgo) | **−0.061 pp** |
| \|Δ\| medio | **0.275 pp** |
| \|Δ_rel\| medio | 2.67 % |
| \|Δ_rel\| mediana | **2.37 %** |
| \|Δ\| máximo | 1.159 pp (12.1 %), Fig. 7, x_b = 0.55, 2300 kPa |
| \|Δ\| medio sin los 2 puntos de "desplome" (2300 kPa y x_b = 0.45) | 0.22 pp |

Control de motor: teqp vs `AmmoniaWaterAdapter` difieren **0.0012 pp** en los dos puntos donde
ambos convergen (11.0554 vs 11.0542 %; 11.9131 vs 11.9119 %).

### 4.11 Tendencias

1. **η vs presión (Fig. 7, x_b = 0.55)** — ✔ reproducida. Modelo y paper suben, alcanzan un
   máximo y caen. Máximo del modelo en 2000 kPa (11.78 %) entre los puntos evaluados; máximo de
   la curva del paper en 19.1 bar (12.01 %). Coinciden dentro del paso de la malla (200 kPa).
2. **η vs presión (Fig. 7, x_b = 0.66)** — ✔ reproducida. Ambos suben hasta ~25–27 bar y
   luego bajan; |Δ| ≤ 0.27 pp en los 5 puntos.
3. **η vs x_b (Fig. 3, 373 K)** — ✔ en 3 de 4 tramos. Pendientes entre puntos consecutivos:

   | Tramo | Modelo | Paper | ¿Coincide? |
   |---|---|---|---|
   | 0.45 → 0.55 | 11.56 → 11.06 (baja) | 11.04 → 11.39 (sube) | no |
   | 0.55 → 0.65 | baja | baja | sí |
   | 0.65 → 0.75 | baja | baja | sí |
   | 0.75 → 0.85 | baja | baja | sí |

   El único desacuerdo está donde la curva del paper tiene su máximo (x_b ≈ 0.48); el modelo
   lo sitúa algo más a la izquierda.
4. **Efecto de T_fuente (373 vs 423 K a 15 bar, mismo x_b)** — ✘ **no cuantificable**: los
   puntos de 423 K con x_b = 0.45 y 0.75 no convergieron y el de 0.60 no tiene pareja evaluada a
   373 K.

### 4.12 Puntos que no convergieron (6 de 33)

| Punto | Error | Interpretación |
|---|---|---|
| 423 K, 15 bar, x_b 0.45 y 0.75 | `PropertyRangeError: T_from_Ph` (teqp) | el solver pide estados intermedios fuera del rango de búsqueda del motor (ver `resultados/2026-09-23_limites_teqp/`) |
| 333 K, 15 bar, x_b 0.65 | `PropertyRangeError: equilibrio_liquido_vapor` | estado de separador sin equilibrio bifásico posible a esa T, P |
| 373 K, 10 bar, x_b 0.45 | `PropertyRangeError: T_from_Ph` | ídem |
| 463 K, 32 bar, x_b 0.80 | `PropertyRangeError: T_from_Ph` | ídem |
| 423 K, 15 bar, x_b 0.60 (iapws) | `PropertyRangeError: h(P, s, x)` | el motor de referencia también falla en este punto |

Ninguno se descartó ni se ocultó; son limitaciones numéricas del solver/motor, no resultados
físicos ("no converge" ≠ "ciclo inviable").

### 4.13 Fuentes de discrepancia esperadas

1. **Ecuación de estado distinta**: Ibrahim & Klein (1993) en el paper vs Tillner-Roth &
   Friend (1998) aquí. Es la principal y la que se quería medir.
2. **Pinch vs efectividad**: el paper impone la diferencia mínima de temperatura en cualquier
   punto del intercambiador; aquí se traduce a una efectividad terminal calibrada en un paso.
3. **P_baja supuesta** (el paper no la publica).
4. **Zonas de desplome**: las dos mayores desviaciones (2300 kPa y x_b = 0.45) están donde la
   curva del paper cae varios puntos en un intervalo muy corto (el separador casi no produce
   vapor). En esas zonas un pequeño desplazamiento del límite de fases entre las dos
   ecuaciones de estado produce una Δη grande. Es una hipótesis coherente con que sea el único
   patrón de error, no una demostración.
5. **Incertidumbre del propio dato de referencia**: el paper difiere consigo mismo 0.04–0.05 pp
   entre sus figuras y su texto (§4.3); la incertidumbre de entalpía de Tillner-Roth es
   ±200 J/mol (≈ 11 kJ/kg) según IAPWS G4-01 §7.

---

## 5. Nivel 2 — Balances internos

`tests/test_cycle_solver.py::test_resolver_ciclo_balance_global_y_eta` comprueba el primer
principio a nivel de ciclo, Q_i + W_p = Q_out + W_t, con error relativo < 10⁻⁴, y el cierre del
regenerador m_l·(h₅ − h₆) = m_b·(h₁ − h₁₀) con tolerancia relativa 10⁻⁴.

---

## 6. Limitaciones que deben declararse

1. Comparación **modelo contra modelo publicado**, no contra datos experimentales.
2. **Una sola fuente** (Elsayed 2013 y Embaye son el mismo modelo). Una segunda fuente
   independiente con tabla de estados (p. ej. Hettiarachchi et al., 2007) no se consultó por
   estar tras un muro de pago.
3. Se compara η; no se comparan estados individuales (el paper no publica tabla de estados).
4. Efecto de T_fuente no cuantificado; 333 K solo parcialmente (2 puntos convergidos, no
   comparables por título).
5. Efectividades calibradas fuera de la banda de diseño 0.75–0.85 (justificado en §4.2).

---

## 7. Versión 1 (2026-09-19): validación de un solo punto

Caso citado en el texto del paper: *"at a pressure of 15 bars, the KCS11 thermal efficiency
(11.38%) with the ammonia-water concentration of 0.55 ... heat source temperature of 373 K and
the heat sink temperature of 283 K"*, η_t = η_p = 0.80.

Residuos de la calibración de un paso (verificado con `AmmoniaWaterAdapter`):

| Objetivo | Buscado | Obtenido | Δ |
|---|---|---|---|
| T₂ (HRVG, T_fuente − 4) | 369.00 K | 369.11 K | 0.11 K |
| T₉ (condensador, T_sumidero + 4) | 287.00 K | 286.33 K | 0.67 K |
| T₆ (regenerador, T₁₀ + 4) | 290.53 K* | 291.85 K | 1.32 K |

\* T₁₀ del paso base (304.93 K); en la corrida final T₁₀ = 286.52 K — por eso el regenerador
tiene el mayor residuo.

| Fuente | η |
|---|---|
| Elsayed et al. (2013), texto | 11.38 % |
| Modelo, `AmmoniaWaterAdapter` | 11.054 % |
| Modelo, `TeqpAdapter` | 11.055 % |

Diferencia: −0.33 pp (−2.9 %). Aceptada por el usuario. Test persistente:
`tests/test_validacion_elsayed2013.py` (tolerancia 5 % relativa). Estados completos:
`validacion_elsayed2013.json`. La v2 (§4) reproduce este mismo punto (−0.325 pp contra el
texto; −0.376 pp contra la curva extraída de la Fig. 7).

---

## 8. Reproducibilidad

| Paso | Comando | Salida |
|---|---|---|
| Verificación IAPWS | `.venv/Scripts/python.exe scripts/verificacion_iapws_g4.py` | `resultados/2026-09-23_verificacion_iapws_g4/` |
| Test IAPWS | `.venv/Scripts/python.exe -m pytest tests/test_verificacion_iapws_g4.py` | — |
| Extracción de curvas | `.venv/Scripts/python.exe scripts/extraer_embaye_vectorial.py` | `resultados/2026-09-24_embaye_vectorial/` |
| Comparación 33 puntos | `.venv/Scripts/python.exe scripts/validacion_tendencias_embaye.py` (~60 min, reanudable) | `resultados/2026-09-24_validacion_tendencias/` |
| Gráfica | `.venv/Scripts/python.exe scripts/grafica_validacion_tendencias.py` | `comparacion_tendencias_v2.png` |
| Punto único (v1) | `.venv/Scripts/python.exe -m pytest tests/test_validacion_elsayed2013.py` | — |

## 9. Referencias

- IAPWS (2001). *Guideline on the IAPWS Formulation 2001 for the Thermodynamic Properties of
  Ammonia-Water Mixtures* (G4-01). `reference/IAPWS_G4-01_nh3h2o.pdf`.
- Tillner-Roth, R., & Friend, D. G. (1998). A Helmholtz free energy formulation of the
  thermodynamic properties of the mixture {water + ammonia}. *J. Phys. Chem. Ref. Data*, 27(1),
  63–96. https://doi.org/10.1063/1.556015
- Ibrahim, O. M., & Klein, S. A. (1993). Thermodynamic properties of ammonia-water mixtures.
  *ASHRAE Transactions*, 99(1), 1495–1502.
- Elsayed, A., Embaye, M., AL-Dadah, R., Mahmoud, S., & Rezk, A. (2013). *Int. J. Low-Carbon
  Technol.*, 8(suppl_1), i69–i78. https://doi.org/10.1093/ijlct/ctt020
- Embaye, M., AL-Dadah, R., Mahmoud, S., Elsayed, A., & Rezk, A. Performance of Kalina Cycle
  System 11 (KCS11) using low temperature heat sources. University of Birmingham.

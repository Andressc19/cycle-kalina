# Informe de iteraciones y conclusiones — 8 (noche) y 9 de octubre de 2026

**Rama:** `test/barrido_final`, mergeada a master local por fast-forward.
**Informes previos:** `docs/INFORME_ITERACIONES_2026-10-06.md`, `..._2026-10-07.md` y
`..._2026-10-08.md`. El de hoy cierra **la sección de barridos** de la campaña final.
**Motor:** teqp con las protecciones A+B, MA y la marca de rango. El motor real (`AmmoniaWaterAdapter`)
solo se usó en puntos de control, porque tarda ~800–1000 s por punto.

---

## 1. Trabajo realizado

| Fase | Qué respondió | Corridas | Resultado clave |
|---|---|---|---|
| M6 | ¿Coinciden teqp y el motor real? ¿Cuánto margen tiene O2? | 36 + 131 | Sí coinciden. O2 exige ≥ 0 K; 2 K de margen cuestan +25–46 kPa de P_baja |
| M9, escalera | ¿Cuántos datos del profesor se conservan a la vez? | 960 + 24 + 3 | **8 de 10** (sus presiones, x_b, η y ε) |
| M10 + M10b, Húsavík | ¿Eran correctas las corridas de la Fase 3? ¿Qué faltaba? | 311 + 71 | 97/97 confirmados; x_b de 0.60–0.95 y T_fuente, T_sumidero, η_p y ε_HRVG nuevos |

---

## 2. M9 — escalera de conservación de los datos del profesor

**Idea (del usuario):** conservar solo un grupo de datos del profesor, liberar el resto y sumar
grupos de a uno mientras siga habiendo KALINA.

**Método:**

- 6 grupos: T_fuente, las η/ε, P_alta, P_baja, T_sumidero y x_b.
- Ronda 0: 100 puntos LHS por grupo.
- Rondas 1–3: 30 puntos por conjunto, sumando al mejor conjunto cada grupo restante.
- El mejor conjunto se elige por KALINA **confiables**: dentro de rango y verificados con B.
- La escalera termina con 4 grupos, porque con todos es el punto del profesor, que no converge (M1).

**Resultados (KALINA / confiables):**

| Ronda | Conjunto | Datos conservados | KALINA | Confiables |
|---|---|---|---|---|
| 0 | x_b | 1 | 29/100 | 15 |
| 0 | T_sumidero | 1 | 17/100 | 13 |
| 0 | P_alta | 1 | 19/100 | 12 |
| 0 | η/ε | 5 | 13/100 | 11 |
| 0 | P_baja | 1 | 1/100 | 1 |
| 0 | T_fuente 623 K | 1 | 7/100 | **0** |
| 1 | x_b + P_alta | 2 | 11/30 | 7 |
| 2 | x_b + P_alta + η/ε | 7 | 13/30 | 7 |
| 3 | **x_b + P_alta + η/ε + P_baja** | **8 de 10** | **5/30** | **5** |
| 3 | x_b + P_alta + η/ε + T_sumidero | 8 de 10 | 6/30 | 4 |
| 3 | x_b + P_alta + η/ε + T_fuente | 8 de 10 | 0/30 (30 NO_CONVERGIO) | 0 |

En total, M9 hizo 984 corridas con teqp: **178 KALINA, 115 de ellos confiables**.

**Deducción:** el enunciado del profesor es un Kalina válido si se cambia **solo la temperatura de la
fuente** (623 → **391–409 K**) y se usa un sumidero algo más frío (**280–293 K**). Con eso, η llega
hasta 10.6 % con ≥ 2 K de subenfriamiento. Con su clima de 300 K hace falta, además, ε_cond ≥ 0.875
(M5c). Su fuente de 623 K es el bloqueo estructural: el HRVG sobrecalienta la mezcla.

---

## 3. M6 — verificación y margen de subenfriamiento

- **teqp coincide con el motor real** en los 5 puntos que convergieron: misma clase y |Δη| ≤ 0.003 pp.
  Con 300 s, el motor real se corta por tiempo; necesita ~1500 s.
- **O2 no trae margen propio.** El código exige T9 ≤ T_burbuja al piso, y varios puntos quedan con
  0.04–0.4 K. El costo de un margen real es bajo:

  | Margen | P_baja adicional | Pérdida de η |
  |---|---|---|
  | 2 K | +25–46 kPa | −0.3 a −0.5 pp |
  | 5 K | +19–116 kPa | −0.3 a −1.2 pp |

---

## 4. M10 — Húsavík revisitado

### 4.1 Catálogo de barridos de Húsavík, clasificados por variables movidas

| Familia | Origen | Variables movidas | Piso O2 | n | KALINA en sept. | KALINA ahora |
|---|---|---|---|---|---|---|
| F3-A, búsqueda v1 | sept. | P_alta, P_baja, x_b, η_t, ε_reg, ε_cond | 303.55 | 14 | 14 | 14 |
| F3-B, búsqueda v2 | sept. | P_baja, ε_reg, ε_cond | 283.15 | 27 | 27 | 27 |
| F3-C, mapa 2D | sept. | P_baja × ε_reg | 283.15 | 24 | 24 | 24 |
| F3-D, OFAT de 7 puntos | sept. | P_baja, ε_cond, ε_reg, η_t, x_b | 283.15 | 26 | 26 | 26 |
| F3-E, OFAT de 4 puntos | sept. | P_alta, P_baja, x_b | 303.55 | 6 | 6 | 6 |
| B1, OFAT de 15 puntos | nuevo | las 10 variables, una por vez | 283.15 | 150 | — | 107 |
| B2, malla | nuevo | **x_b × P_baja** | 283.15 | 64 | — | 49 |

**Re-corrida de la Fase 3:** **97 de 97 KALINA se confirman** con el motor actual. η es idéntica
(|Δη| < 3·10⁻⁶ pp), los 97 están dentro de rango y verificados con B. Los datos de septiembre
eran correctos: las protecciones A+B y MA no cambian ningún punto KALINA de Húsavík.

### 4.2 OFAT alrededor del ancla (690 kPa, piso de 10 °C)

| Variable | Rango barrido | Rango KALINA | Se rompe por | η en KALINA |
|---|---|---|---|---|
| T_fuente | 380–430 K | 380–401 K | O2 (arriba) | 12.2–13.0 % |
| T_sumidero | 0–20 °C | 0–10 °C | O2 (arriba) | 12.5–13.0 % |
| P_alta | 2500–4000 kPa | 2821–4000 kPa | O2 (abajo) | 11.8–13.6 % |
| P_baja | 500–1200 kPa | 700–1200 kPa | O2 (abajo) | 8.5–12.6 % |
| **x_b** | **0.60–0.95** | **0.60–0.825** | **O2 (arriba)** | **8.8–12.8 %** |
| η_t | 0.75–0.95 | todo | — | 10.5–13.5 % |
| η_p | 0.60–0.90 | todo | — | 12.6–12.8 % |
| ε_HRVG | 0.60–0.95 | 0.60–0.925 | O2 (arriba) | 11.6–13.0 % |
| ε_reg | 0.40–0.95 | todo | — | 11.9–13.2 % |
| ε_cond | 0.70–0.95 | solo 0.95 | O2 (abajo) | 12.7 % |

### 4.3 Concentración de amoníaco variable (malla x_b × P_baja)

| x_b | 0.70 | 0.73 | 0.76 | 0.79 | 0.82 | 0.85 | 0.88 | 0.91 |
|---|---|---|---|---|---|---|---|---|
| P_baja mínima KALINA (kPa) | 500 | 600 | 600 | 700 | 700 | 800 | 800 | 800 |
| η en esa P_baja | 13.3 % | 12.6 % | 13.1 % | 12.3 % | 12.6 % | 11.9 % | 12.1 % | 12.2 % |

Hay 49 KALINA de 64, todos confiables.

**Deducción:** al subir x_b sube la presión de saturación de la mezcla, así que para evitar la
cavitación hay que subir P_baja: unos +300 kPa entre x_b 0.70 y 0.91. A P_baja fija, η sube con
x_b (+2.5 pp de 0.70 a 0.91), pero la ventana se desplaza. Húsavík (x_b 0.82, 690 kPa) está justo
en el borde de O2, coherente con una planta diseñada al mínimo de P_baja.

---

### 4.4 M10b — concentración de amoníaco baja (x_b 0.30–0.70)

**Motivo:** el usuario preguntó por qué no se bajó de 0.60. Se corrieron 71 puntos: un OFAT de 17
puntos a 690 kPa y una malla x_b × P_baja de 200 a 700 kPa.

| x_b | Resultado | P_baja mínima KALINA | Criterio |
|---|---|---|---|
| 0.30–0.375 | No hay ciclo (el solver no encuentra T1) | — | — |
| 0.40–0.475 | Espurio N2; separador con líquido, W_net < 0 | — | **O5, O3** |
| 0.50 | KALINA formal, η 0.1–1.2 % (~2 % de vapor) | 200 kPa | borde de O5 |
| 0.55 | KALINA | 300 kPa | O2 abajo |
| 0.60 | KALINA | 400 kPa | O2 abajo |
| 0.65–0.70 | KALINA, η hasta 13.3 % | 500 kPa | O2 abajo |

**Deducción:** al bajar el amoníaco, el criterio que limita pasa de **O2** (cavitación, con x_b alto)
a **O5/O3** (no hay vapor, con x_b bajo). Con la fuente de Húsavík (394 K), la ventana útil es
**x_b ≈ 0.55–0.82** a su P_baja real, y llega a 0.91 con P_baja de 800 kPa. Los valores x_b < 0.55
quedan marcados como "fuera de lo habitual en Kalina".

## 5. Conclusiones de la sección de barridos

1. **Datos del profesor:** se conservan 8 de 10 (sus presiones 3000/400 kPa, x_b 0.50 y sus η/ε). Hay
   que cambiar la fuente a ~390–410 K y usar un sumidero ≤ ~293 K, o bien ε_cond ≥ 0.875 con su clima.
   **Su fuente de 623 K no es compatible con un Kalina** con el resto de sus datos.
2. **Región KALINA global:**
   - P_baja ≥ ~550 kPa (por O2) y rP ≈ 1.7–5.3, creciente con P_alta;
   - T_fuente ≈ 384–486 K;
   - ε_cond ≥ ~0.75;
   - la P_baja mínima crece con x_b.
3. **El criterio que manda es O2** (cavitación). Conviene diseñar con ~2 K de subenfriamiento.
4. **Validación:**
   - Húsavík cae en la ventana con su P_baja real;
   - las 97 corridas KALINA de septiembre se reproducen;
   - teqp coincide con el motor riguroso.
5. **η** (secundaria): hasta ~15.6 % dentro de los límites del proyecto (M7) y ~10–13 % en los
   casos realistas (profesor modificado, Húsavík).

## 6. Lo que no se sabe

- Las rondas 1–3 de la escalera tienen 30 puntos por conjunto: prueban que las combinaciones existen,
  pero no trazan bordes finos.
- El motor real se verificó solo en 5 puntos, por su costo.
- Fuera de las cajas barridas no se afirma nada.

## 7. Archivos

- `resultados/2026-10-08_final_M6/`, `..._M9/` , `resultados/2026-10-09_final_M10_husavik/` y `..._M10b_xb_bajo/` (CSV, PNG
  y `REPORTE_*.md` con notas del director).
- Excel: `datos/Excel_final_kalina.xlsx` (81 hojas).
- Protocolos: `prompts/TASK_CONTEXT_final_M6.md`, `..._M9*.md` y `..._M10_husavik.md`.

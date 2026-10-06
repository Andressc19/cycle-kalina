# Barridos finales — resumen de resultados y conclusiones (6 de octubre de 2026)

**Rama:** `test/barrido_final` · **Libro de datos:** `datos/Excel_final_kalina.xlsx` (27 hojas)
**Protocolo:** `docs/METODOLOGIA_BARRIDOS_FINAL.md` · **Fórmulas:** `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md`
**Método de sensibilidad elegido y por qué:** `docs/ESTUDIO_METODOS_SENSIBILIDAD.md`

Todos los cálculos los ejecutó OpenCode a partir de un `TASK_CONTEXT` por fase. Claude los vigiló
en vivo y auditó cada resultado contra los CSV. El motor usado es teqp con la protección A+B, el
bracket tolerante MA y la marca de rango G4-01. Los KALINA se verificaron con el motor riguroso
(verificación B).

---

## 1. Punto de partida: los datos del profesor

| Parámetro | Valor |
|---|---|
| T_fuente / T_sumidero | 623.15 K / 300.03 K (promedio del perfil horario) |
| P_alta / P_baja | 3000 / 400 kPa |
| x_b, m_b | 0.50, 1 kg/s |
| η_t / η_p | 0.85 / 0.75 |
| ε_HRVG / ε_reg / ε_cond | 0.85 / 0.75 / 0.80 |
| Piso de cavitación O2 | 300.03 K (clima del profesor) |

## 2. Qué se ha hecho (≈ 950 combinaciones evaluadas)

| Fase | Pregunta | Qué se varió | Puntos | Resultado |
|---|---|---|---|---|
| **M1** | ¿El código nuevo reproduce lo anterior? | La Fase 1 del profesor: P_alta, x_b y las 24 horas de T_amb | 41 | **41/41 iguales** (todos NO_CONVERGIO) |
| **M2 nivel 1** | ¿Basta UN cambio? | Las 10 variables, una a la vez (ε/η en 0.75–0.85) | 132 | **0 KALINA** |
| **M2 nivel 2** | ¿Bastan DOS cambios? | T_fuente × P_baja; ε_HRVG × P_baja | 180 | **49 KALINA** (T_fuente de 390 a 434 K) |
| **M2R** | Lo mismo, con ε/η en 0.40–0.95 | Las 5 ε/η solas; ε_HRVG × ε_cond; ε_HRVG × P_baja; T_fuente × ε_cond | 225 | **14 KALINA**, incluidos algunos **con la fuente del profesor** |
| **M3** | Sensibilidad alrededor del ancla | Las 10 variables, 15 valores cada una, en torno a 403 K / 564 kPa | 171 | Ranking de variables y fronteras |
| M2S | Efecto de un sumidero frío | En curso | — | — |
| M4 | Mapa global | En preparación | — | — |

## 3. Resultados principales

### 3.1 ¿Por qué los datos del profesor no funcionan?
Con una fuente de 623 K, la mezcla sale del HRVG **sobrecalentada**, por encima de la campana
bifásica. Así el separador no tiene líquido y vapor que separar y el ciclo deja de ser un Kalina.
**Ningún cambio de una sola variable lo arregla.**

### 3.2 Las rutas encontradas hacia KALINA (2 cambios respecto al profesor)

| Ruta | Cambios | η | ¿Rango confiable? | Verificado con el motor riguroso |
|---|---|---|---|---|
| **Conservar la fuente de 623 K** | ε_HRVG 0.85 → **0.40** · P_baja 400 → **1318 kPa** | 6.27 % | no (líquido > 420 K) | sí |
| Fuente más fría + P_baja | T_fuente → **390 K** · P_baja → **445 kPa** | 2.45 % | sí | sí |
| Fuente más fría + P_baja | T_fuente → **403 K** · P_baja → **564 kPa** (**ancla A\***) | 8.48 % | sí | sí |
| Fuente más fría + P_baja (la mejor η) | T_fuente → **420 K** · P_baja → **736 kPa** | **9.15 %** | sí | sí |
| Fuente más fría + condensador | T_fuente → **403 K** · ε_cond → **0.95** (P_baja del profesor) | **9.50 %** | sí | sí |

- Ventana de T_fuente con KALINA (P_alta = 3000 kPa, x_b = 0.50): **≈ 390–434 K**. Por encima de
  ~466 K, la cavitación (O2) ya no se cierra ni con P_baja = 2000 kPa.
- Conservando la fuente de 623 K, **solo se llega a KALINA con un HRVG poco efectivo (0.40–0.50)
  y una P_baja alta (≥ 1318 kPa)**. El costo es una η baja (3–6 %) y estados fuera del rango
  experimental del modelo.
- Ninguna ε ni η sola, ni siquiera en 0.40–0.95, vuelve KALINA al enunciado.

### 3.3 Sensibilidad alrededor del ancla (M3)

| Variable | Sigue KALINA hasta (aprox.) | Qué se rompe | Efecto sobre η |
|---|---|---|---|
| T_fuente | ≤ 410 K | O2 | el más fuerte localmente (elasticidad +10.9) |
| T_sumidero | ≤ 300.5 K | O2 | bajo (+1.6) |
| P_alta | ≥ 2936 kPa | O2 | −1.2 |
| P_baja | ≥ 542 kPa | O2 | −0.6 (la "perilla de seguridad") |
| x_b | 0.47–0.51 | O2 / trabajo negativo | +3.4, pero con un pasillo muy estrecho |
| η_t | ≥ 0.66 | O2 | 0.95 → **η = 9.62 %** |
| η_p | todo el rango 0.40–0.95 | nada | casi irrelevante |
| ε_HRVG | ≤ 0.87 | O2 | +0.6 |
| ε_reg | ≥ 0.72 | O2 | 0.95 → **η = 10.96 %** (la mejor palanca) |
| ε_cond | ≥ 0.79 | O2 | −0.4 |

**Lectura:** el ancla está **al filo de la cavitación (O2)**, el criterio que siempre se rompe
primero. Para ganar η sin perder KALINA, las palancas son el **regenerador (ε_reg)** y la
**turbina (η_t)**. Para ganar margen de seguridad, la palanca es **P_baja**.

## 4. Conclusiones actuales

1. **El enunciado del profesor no es un Kalina viable tal como está.** La fuente de 623 K es
   demasiado caliente para un KCS-11 a 3 MPa con ε_HRVG = 0.85.
2. **Queda a dos cambios de serlo:**
   - con su misma fuente: un HRVG de baja efectividad y una P_baja alta (η ≈ 6 %);
   - o con una fuente de ~400–420 K y una P_baja de ~550–750 kPa, o un condensador de 0.95
     (η ≈ 8.5–9.5 %).
3. **El criterio que limita es la cavitación de la bomba (O2)**, en todas las fases.
4. Alrededor del punto funcional, **ε_reg y η_t son las mejores palancas de eficiencia**: hasta
   ~11 % con ε_reg = 0.95.
5. Lo que tenemos son **cortes del mapa que pasan por el punto del profesor**, no el mapa completo
   de la región Kalina.

## 5. Lo que falta o no se sabe

- **Sumidero frío (M2S, en curso):** hasta ahora T_sumidero se varió con P_baja fija y con el piso
  de O2 fijo en el clima del profesor, y así su beneficio no se ve. El caso Húsavík (5 °C, piso de
  10 °C) mostró que hecho bien baja la P_baja necesaria y sube η (12.7–13.4 %).
- **Interacciones y mapa global (M4, en preparación):** un LHS de 300 puntos con las 10 variables
  a la vez, en una caja de rangos favorables tomada de los papers (Elsayed 2013, Nguyen 2014,
  Nemati 2017) y de las campañas previas (Húsavík, Fases 2/3, ventana de Elsayed). El piso de O2
  sigue al clima de cada punto.
- **Incertidumbre:** las diferencias de η menores que 0.4–0.7 pp no son concluyentes (incertidumbre
  del modelo G4-01). Los estados con líquido > 420 K son extrapolación del modelo.
- **No probado todavía:** combinaciones con x_b > 0.55 y P_alta de 4000–5000 kPa partiendo del
  enunciado del profesor (M4 las cubre).

## 6. Dónde está cada cosa

| Fase | Reporte | Commit |
|---|---|---|
| M0–M1 | `resultados/2026-10-06_final_M1/REPORTE_M1.md` | `1b01096` |
| M2 nivel 1 | `resultados/2026-10-06_final_M2/REPORTE_M2_N1.md` (ver §9, nota del director) | `02f64b6` |
| M2 nivel 2 | `resultados/2026-10-06_final_M2/REPORTE_M2_N2.md` | `c6fb1e1` |
| M3 y M2R | `resultados/2026-10-06_final_M3/REPORTE_M3.md` (ver §11) · `resultados/2026-10-06_final_M2R/REPORTE_M2R.md` | `ef30e9f` |
| Excel (27 hojas) | `datos/Excel_final_kalina.xlsx` | `6dfc433` |

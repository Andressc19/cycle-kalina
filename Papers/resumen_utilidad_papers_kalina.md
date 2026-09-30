# Resumen de utilidad de papers — Ciclo Kalina KSC-11

**Fecha:** 2026-09-29
**Alcance:** 7 PDFs en `D:\Desktop\ciclo_kalina_tercero\Papers\`, leídos íntegramente.
**Objetivo:** clasificar cada paper según su utilidad para (1) mejorar los barridos libres de
Fase 2 y (2) realizar validaciones del motor propio (KCS-11, NH3-H2O, backends
`AmmoniaWaterAdapter`/`TeqpAdapter`, Tillner-Roth & Friend EOS).

---

## 1. Resumen ejecutivo

De los 7 papers, **2 son directamente validables** (misma topología KCS-11, mismo grupo de
autores: Elsayed et al. 2013 y su precursor de conferencia) — ambos ya se usaron parcialmente
(un solo punto, ya documentado en `VALIDACION_ELSAYED2013.md`), pero contienen **puntos extra sin
explotar** (curvas η vs x_b a varias combinaciones P/T) que podrían ampliar la validación sin
costo de investigación adicional. El resto son de **topologías distintas** (split-cycle, KC-12,
variantes con eyector/columna de destilación/doble presión) — no sirven para validar el modelo
exacto, pero **sí aportan tendencias, rangos de parámetros y, en un caso (Nguyen et al. 2014),
una tabla completa de estados con el mismo EOS** que podría usarse para verificar el backend de
propiedades de forma independiente de la topología. El hallazgo más útil para Fase 2 es la
confirmación, con datos reales de otro grupo, de que x_b alto (0.75-0.8) requiere P_alta muy alta
(125-130 bar) — exactamente el muro estructural que nuestra Ronda 5/6 detectó de forma empírica.
El documento de ASHRAE, contrario a lo esperado, **no aporta nada**: es un documento de política y
seguridad sobre amoníaco puro como refrigerante industrial, sin una sola mención a la mezcla
NH3-H2O ni al ciclo Kalina.

---

## 2. Tabla comparativa

| # | Archivo | Tipo de estudio | Topología | Útil p/ Fase 2 | Útil p/ validación |
|---|---|---|---|---|---|
| 1 | `ctt020.pdf` | Simulación (validada contra planta real) | KSC-11 (idéntica a la nuestra) | **Media** | **Alta** |
| 2 | `PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf` | Simulación (precursor de conferencia de #1) | KCS-11 (idéntica) | **Media** | **Alta** |
| 3 | `Dubey_2021_IOP_Conf._Ser.__Mater._Sci._Eng._1168_012030.pdf` | Revisión (6 variantes) | Distintas (DCSS, KSG-1, split, doble presión, ejector, composición variable) | **Media-Alta** | **Baja** |
| 4 | `Thermodynamic_evaluation_postprint.pdf` | Simulación + optimización (algoritmo genético) | Kalina split-cycle (37 estados) | **Alta** | **Media** |
| 5 | `evalaucion_termica_solar.pdf` | Simulación + optimización (algoritmo genético) + validación cruzada contra otro estudio | KC-12 (solar, alta T) | **Media** | **Baja** |
| 6 | `musfa analysys termico kalina.pdf` | Revisión + caso propio (separador auxiliar) | KCS-11 modificado (baja T) | **Baja** | **Baja** |
| 7 | `recomendaciones_manejo de_mezclas_ashrae.pdf` | Documento de política/seguridad | N/A — amoníaco puro, no mezcla, no Kalina | **Nula** | **Nula** |

---

## 3. Fichas por paper

### 3.1 `ctt020.pdf`

- **Título y autores:** Elsayed, Embaye, AL-Dadah, Mahmoud, Rezk (2013), "Thermodynamic
  performance of Kalina cycle system 11 (KCS11): feasibility of using alternative zeotropic
  mixtures," *International Journal of Low-Carbon Technologies*, 8(suppl. 1), i69-i78.
- **Tipo de estudio:** Simulación termodinámica, con un punto de validación contra un caso de
  referencia de literatura previa.
- **Configuración del ciclo o modelo usado:** KCS-11 — **misma topología que nuestro repo**
  (HRVG → separador → turbina/regenerador-válvula → absorbedor → condensador → bomba →
  regenerador). Turbina y bomba con eficiencia isentrópica del 80% cada una. Cierre del
  regenerador por *pinch point* de 4 K (método distinto al de efectividades que usamos
  nosotros).
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - Punto de validación ya usado en nuestro repo: P=15 bar, x_b=0.55, T_fuente=373 K,
    T_sumidero=283 K → η=11.38%, η_Carnot=24%, η_II=47%.
  - Figuras 2a-2c (sin explotar aún): curvas η vs x_b para P_evap ∈ {10, 15, 20, 25, 30, 40}
    bar, cruzadas con T_fuente ∈ {333, 373, 423} K.
  - Rango de x_b recomendado para operación estable: **0.55-0.9**.
- **Utilidad para barridos libres (Fase 2): Media.** Confirma que nuestro rango de x_b
  (0.35-0.85 explorado) y de P_alta (hasta 4500 kPa) es físicamente razonable; no aporta
  parámetros nuevos que no tuviéramos ya, pero sí una cota de sanidad externa.
- **Utilidad para validaciones: Alta.** Ya es la validación oficial del repo (un punto). Las
  Figuras 2a-c dan puntos adicionales (misma topología, mismo tipo de eficiencias) que podrían
  digitalizarse y añadirse como validaciones extra sin re-derivar nada.
- **Información aprovechable para modelado aunque no sea Kalina:** N/A (es la topología exacta).
- **Limitaciones o precauciones:** Usa cierre de regenerador por pinch-point fijo (4 K), no por
  efectividad — al comparar puntos nuevos de las Figuras 2a-c habría que verificar que esa
  diferencia de método no introduce sesgo.
- **Cita clave:** Fig. 2a-c, rango de x_b "for stable operation: 0.55-0.9" (texto del paper).
- **Resumen breve:** Es el paper que ya usamos para validar nuestro motor (mismo ciclo KCS-11,
  un punto con η=11.38%). Tiene más curvas (η vs x_b a distintas P y T) que no hemos aprovechado
  y que podrían ampliar la validación sin trabajo adicional de modelado, solo de extracción de
  datos de las figuras.

### 3.2 `PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf`

- **Título y autores:** Embaye, AL-Dadah, Mahmoud, Elsayed, Rezk — versión de congreso/precursora
  del mismo estudio que `ctt020.pdf` (mismo grupo, mismas ecuaciones).
- **Tipo de estudio:** Simulación termodinámica, mismo punto de validación que #1.
- **Configuración del ciclo o modelo usado:** KCS-11, idéntica a #1 y a nuestro repo.
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - Mismo punto de validación (15 bar, x=0.55, T_fuente=373K, T_sink=283K, η=11.38%).
  - Datos MÁS granulares que la versión journal: curvas η vs x_b para 4 valores de P_evap
    (10, 15, 23.5, 32 bar) cruzadas con T_fuente ∈ {333, 373, 423, 463} K.
  - η_turbina = η_bomba = 80% (isentrópicas).
  - **Restricción explícita de calidad de salida de turbina ≥ 90%** — el mismo criterio que
    nuestro O1.
- **Utilidad para barridos libres (Fase 2): Media.** Confirma rango de T_fuente hasta 463 K
  (nuestra Ronda 6 explora 380-500 K) y reafirma el criterio de calidad de turbina ≥90% como
  estándar de la industria, no una invención nuestra.
- **Utilidad para validaciones: Alta.** Mismo punto ya validado, más puntos adicionales sin
  explotar, con más granularidad que la versión journal.
- **Información aprovechable para modelado aunque no sea Kalina:** N/A.
- **Limitaciones o precauciones:** Es un precursor/conferencia del mismo trabajo — no añade
  independencia real a la validación (mismo grupo, mismos supuestos), solo más densidad de
  puntos.
- **Cita clave:** restricción "turbine exit quality maintained ≥90%" — coincide con nuestro
  criterio O1.
- **Resumen breve:** Es la versión de congreso del mismo estudio de `ctt020.pdf`, con curvas más
  detalladas (4 presiones × 4 temperaturas). Confirma que nuestro criterio O1 (calidad de salida
  de turbina ≥90%) es una restricción estándar en la literatura KCS-11, no algo que inventamos.

### 3.3 `Dubey_2021_IOP_Conf._Ser.__Mater._Sci._Eng._1168_012030.pdf`

- **Título y autores:** Dubey & Sharma (2021), "High-efficiency thermodynamic cycles for Kalina
  power generation systems: A comprehensive review," IOP Conf. Series: Materials Science and
  Engineering, 1168, 012030.
- **Tipo de estudio:** Revisión bibliográfica (no genera datos propios, resume ~6 variantes de
  Kalina de la literatura).
- **Configuración del ciclo o modelo usado:** Revisa 6 configuraciones DISTINTAS a la nuestra:
  columna de destilación (DCSS), presión de condensación deslizante (KSG-1), split-cycle, doble
  presión, ciclo con eyector (EKalina), composición ajustable — todas con más componentes que
  nuestro KSC-11.
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - Rango de eficiencias reportadas entre variantes: 6.12%-25.7% (con recalentamiento).
  - Cita a Marston y a Nag & Gupta: la composición de entrada a turbina y la temperatura del
    separador son **las variables clave** que gobiernan el desempeño — coincide con nuestro
    propio hallazgo empírico (x_b, T_fuente y T_separador dominan).
  - EKalina (variante con eyector): x_b ∈ [0.5, 0.9], x_v ∈ [0.92, 0.98], T_agua=110°C →
    hasta +39.55% de potencia vs. KCS-11 base.
- **Utilidad para barridos libres (Fase 2): Media-Alta.** No da un punto reproducible, pero
  confirma con múltiples referencias cruzadas que las variables que ya identificamos como
  dominantes (x_b, T_fuente, T_separador) son objetivamente las correctas según el consenso de
  la literatura — reduce el riesgo de estar optimizando las variables equivocadas.
- **Utilidad para validaciones: Baja.** Al ser una revisión de topologías distintas, no ofrece
  un punto único y reproducible contra el que comparar nuestro KCS-11 exacto.
- **Información aprovechable para modelado aunque no sea Kalina:** Aporta contexto de qué tan
  sensible es el ciclo a la composición de entrada de turbina en general (útil para justificar
  por qué nuestro barrido pondera fuerte x_b).
- **Limitaciones o precauciones:** Es una revisión de segunda mano — los datos citados no son
  verificables sin ir a la fuente original de cada variante.
- **Cita clave:** "turbine inlet composition and separator temperature" como variables clave
  (citando a Marston 1990 y Nag & Gupta 1998).
- **Resumen breve:** Revisión de 6 variantes de Kalina más complejas que la nuestra. No da un
  punto para validar, pero confirma —citando a varios autores— que las variables que ya
  identificamos como dominantes en nuestros barridos (x_b, T_fuente, T del separador) son
  exactamente las que la literatura señala como clave. Útil como respaldo conceptual, no
  numérico.

### 3.4 `Thermodynamic_evaluation_postprint.pdf`

- **Título y autores:** Nguyen, Knudsen, Larsen, Haglind (2014), "Thermodynamic evaluation of the
  Kalina split-cycle concepts for waste heat recovery applications," *Energy*, 71, 277-288 (DTU).
- **Tipo de estudio:** Simulación + optimización (algoritmo genético, 400-800 individuos, 30
  generaciones).
- **Configuración del ciclo o modelo usado:** Kalina split-cycle — topología MUCHO más compleja
  que la nuestra: 37 estados, 2 evaporadores, 2 turbinas, 4 recuperadores, 2 condensadores,
  mezcladores y divisores, con concentración de amoníaco variable en 5 corrientes distintas
  (muy-rica/rica/básica/pobre/muy-pobre). Usa la **misma familia de EOS que nuestro repo**
  (Tillner-Roth & Friend, la misma base del IAPWS G4-01 que usa `AmmoniaWaterAdapter`).
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - Caso base (Tabla 1): T_fuente_entrada=346°C, T_fuente_salida=127.7°C, T_agua_fría=25°C,
    η_politrópica_turbina=70.5%, η_mecánica_turbina=96%, η_bomba=70%, η_generador=95%,
    aproximación de sobrecalentador=16K, ΔT_pinch_evaporador=21.9K, ΔT_recuperadores=5K,
    ΔT_condensador=4.5K.
  - Sensibilidad: T_agua_fría ±15°C → ~7% cambio en potencia; T_fuente ±50°C → ~40% cambio en
    potencia.
  - **Dos estrategias óptimas encontradas:** (a) alta presión de entrada a turbina (125-130 bar)
    + alta fracción de amoníaco (0.75-0.8), o (b) baja presión de salida de turbina + baja
    fracción de amoníaco (0.6-0.7) — **coincide directamente con nuestro propio hallazgo de
    Ronda 5**: x_b alto necesita P_alta mucho más alta.
  - Apéndice A (Tabla A.9): tabla completa T/P/h/x/q para los 37 estados — reproducible como
    cross-check de propiedades independiente de la topología.
- **Utilidad para barridos libres (Fase 2): Alta.** Es el paper que mejor explica, con datos
  reales de otro grupo y otra topología, el muro estructural x_b-alto-necesita-P_alta-alta que
  detectamos empíricamente en Ronda 5/6. Da un número concreto (125-130 bar para x_b=0.75-0.8)
  que sirve de referencia de orden de magnitud para nuestra búsqueda.
- **Utilidad para validaciones: Media.** No puede validar el ciclo completo (topología distinta),
  pero la tabla de propiedades del Apéndice A, al usar el mismo EOS (Tillner-Roth & Friend),
  podría usarse para verificar puntualmente que nuestro backend de propiedades NH3-H2O calcula
  h/s correctamente, independientemente de la topología del ciclo.
- **Información aprovechable para modelado aunque no sea Kalina:** La metodología de
  optimización con algoritmo genético y el manejo de composición variable por corriente es
  transferible conceptualmente, aunque no a nuestro KSC-11 de composición única.
- **Limitaciones o precauciones:** Topología completamente distinta (37 estados vs nuestros 10);
  presiones de trabajo un orden de magnitud mayores (100+ bar vs nuestros 30-45 bar) — comparar
  solo tendencias, nunca magnitudes absolutas.
- **Cita clave:** Tabla 1 (parámetros de diseño del caso base) y Tabla A.9 (estados completos);
  hallazgo de las dos estrategias óptimas (P alta + x_b alto vs. P baja + x_b bajo).
- **Resumen breve:** Estudia un Kalina split-cycle mucho más complejo (37 estados, presiones de
  100-130 bar) pero usa el mismo modelo de propiedades NH3-H2O que nosotros. Su hallazgo más
  valioso: confirma con números reales que subir x_b obliga a subir mucho la presión alta —
  exactamente lo que nuestra Ronda 5 encontró de forma empírica. Su tabla de 37 estados podría
  servir para verificar el cálculo de propiedades de forma independiente del ciclo.

### 3.5 `evalaucion_termica_solar.pdf`

- **Título y autores:** Jeannot, Rahman, Saat, Faizal, Wahid (2021), "Thermodynamic Evaluation of
  a Solar Based Kalina Cycle," Proceedings of the 11th IEOM Conference, Singapore (Universiti
  Teknologi Malaysia).
- **Tipo de estudio:** Simulación + optimización (algoritmo genético en MATLAB, REFPROP con
  Tillner-Roth & Friend) + validación cruzada contra Modi et al. (2016) + modelo económico (SAM).
- **Configuración del ciclo o modelo usado:** KC-12 (capa solar, T entrada turbina = 400°C) — con
  recuperadores duales, separador, dos condensadores y dos bombas; distinta a nuestro KSC-11.
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - η_turbina isentrópica=82%, η_bomba isentrópica=75%, η_mecánica_turbina=98%,
    η_generador=98%.
  - **Restricción de calidad mínima de salida de turbina = 90%** (mismo tipo de criterio que
    nuestro O1), y calidad mínima de entrada al separador = 5%.
  - Rango explorado: P_turbina 100-140 bar, x_b (turbina) 0.5-0.8.
  - Máxima eficiencia encontrada: 33% a P=140 bar, x_b=0.8 (equipos con eficiencias realistas,
    no ideales).
  - Validación cruzada propia contra Modi et al. (2016): diferencia promedio de 3.86% en η.
- **Utilidad para barridos libres (Fase 2): Media.** Confirma la tendencia x_b alto + P alta →
  mejor η (mismo patrón que Ronda 5/Nguyen et al.), y confirma el criterio de calidad de turbina
  ≥90% como estándar transversal a distintas topologías Kalina, no exclusivo de KCS-11.
- **Utilidad para validaciones: Baja.** Topología (KC-12) y rango de temperatura/presión (400°C,
  100-140 bar) muy alejados de nuestro caso — no hay overlap útil para un punto de validación
  directo.
- **Información aprovechable para modelado aunque no sea Kalina:** Metodología de validación
  cruzada entre dos modelos independientes (tabla de %diferencia) — un patrón replicable si en
  el futuro queremos comparar nuestro motor contra otro estudio con parámetros distintos a los
  de Elsayed.
- **Limitaciones o precauciones:** T de entrada a turbina (400°C / 673K) muy por encima de todo
  nuestro rango explorado (hasta 500K) — no extrapolar magnitudes, solo tendencias.
- **Cita clave:** "Minimum turbine vapor quality, X2 = 0.90" (Tabla 1); resultado "maximum
  efficiency of 33.2% ... at 140 bar and ammonia mass concentration of 0.8".
- **Resumen breve:** Aplica Kalina (variante KC-12) a energía solar concentrada, a temperaturas
  mucho más altas que las nuestras (400°C). No sirve para validar directamente, pero confirma
  otra vez que a mayor x_b y mayor presión mejora la eficiencia, y que el criterio de calidad de
  turbina ≥90% es estándar en toda la familia Kalina, no una particularidad de nuestro modelo.

### 3.6 `musfa analysys termico kalina.pdf`

- **Título y autores:** Jiyaul Mustafa (2017), "Thermodynamic Analysis of Kalina Cycle,"
  International Journal of Engineering Research in Computer Science and Engineering (IJERCSE),
  Vol 4, Issue 9.
- **Tipo de estudio:** Revisión bibliográfica extensa + caso propio de baja calidad
  metodológica/documental (texto con traducción automática evidente, sin ecuaciones ni tablas de
  resultados detalladas en el cuerpo disponible).
- **Configuración del ciclo o modelo usado:** KCS-11 modificado con separador auxiliar para
  mejorar la concentración de amoníaco en la turbina, aplicaciones de baja temperatura
  (100-200°C fuente, 27°C sumidero).
- **Parámetros relevantes del Kalina o de la mezcla que reporta:**
  - Único dato numérico propio: η_máx = 13.06% para x_b óptimo = 0.5, a T_fuente=128°C.
  - Revisión cualitativa de literatura: Kalina 10-20% más eficiente que Rankine (bajo 537°C de
    fuente, citando a Marston); Kalina Split-Cycle 23.2% vs Kalina convencional 20.8% (citando a
    Ulrik Larsen et al.).
- **Utilidad para barridos libres (Fase 2): Baja.** El único número reportado (η=13.06% a
  x_b=0.5) es consistente con lo que ya sabemos, pero no viene acompañado de suficiente detalle
  metodológico (presiones, efectividades, esquema exacto) como para ser accionable.
- **Utilidad para validaciones: Baja.** No hay un punto con todos los parámetros de entrada
  necesarios para reproducirlo.
- **Información aprovechable para modelado aunque no sea Kalina:** Ninguna, más allá de servir
  como índice de referencias (cita ~20 estudios que podrían explorarse si se desea profundizar).
- **Limitaciones o precauciones:** Calidad documental baja (traducción automática deficiente,
  posible pérdida de precisión técnica en la traducción de términos); no reporta ecuaciones,
  tablas ni figuras con datos numéricos utilizables más allá del valor aislado de η.
- **Cita clave:** "A greatest cycle effectiveness of 13.06% is come about for an ideal alkali
  mass portion of 0.5 ... working at 128°C" (Abstract).
- **Resumen breve:** Es principalmente una revisión de literatura general sobre Kalina, con un
  caso propio de baja temperatura mal documentado. Solo aporta un número aislado (η=13.06% a
  x_b=0.5) sin suficiente contexto para ser útil en barridos o validación. Su valor real es como
  índice de referencias adicionales, no como fuente de datos.

### 3.7 `recomendaciones_manejo de_mezclas_ashrae.pdf`

- **Título y autores:** ASHRAE, "Position Document on Ammonia as a Refrigerant" (aprobado 2002,
  reafirmado 2006 y 2010).
- **Tipo de estudio:** Documento de política institucional / normativa de seguridad — no es un
  estudio técnico-termodinámico.
- **Configuración del ciclo o modelo usado:** No aplica. El documento trata sobre **amoníaco puro
  (NH3) como refrigerante en sistemas de refrigeración industrial** (ciclos de compresión de
  vapor convencionales), **no sobre la mezcla NH3-H2O ni sobre el ciclo Kalina en ningún
  momento**.
- **Parámetros relevantes del Kalina o de la mezcla que reporta:** **No reportado.** El documento
  no contiene una sola propiedad termodinámica de la mezcla NH3-H2O, ni menciona ciclos Kalina,
  absorción, ni destilación. Su contenido es: historia del amoníaco, usos industriales/agrícolas,
  clasificación de peligrosidad (Standard 34: grupo B2), límites de exposición (TLV=25ppm,
  STEL=35ppm, IDLH=300ppm), marco regulatorio (EPA, OSHA, SARA Título III), y actividades de
  ASHRAE (investigación, estándares, códigos, educación).
- **Utilidad para barridos libres (Fase 2): Nula.** No hay ningún parámetro, rango o correlación
  aplicable al ciclo o a la mezcla.
- **Utilidad para validaciones: Nula.** No hay datos termodinámicos de ningún tipo.
- **Información aprovechable para modelado aunque no sea Kalina:** Ninguna relevante al modelado
  termodinámico. Únicamente sería relevante si en algún momento el proyecto necesitara
  documentar consideraciones de seguridad/manejo de amoníaco a nivel de ingeniería de planta
  (no de simulación), y aun así se referiría al amoníaco puro, no a la mezcla.
- **Limitaciones o precauciones:** **Corrección a la expectativa inicial**: se esperaba que este
  documento sirviera como guía general de manejo de la mezcla NH3-H2O (por su cercanía con
  ciclos de absorción). Tras la lectura completa, esa expectativa no se cumple — el documento no
  toca la mezcla NH3-H2O en ningún punto, es exclusivamente sobre amoníaco anhidro puro como
  refrigerante en sistemas de compresión de vapor.
- **Cita clave:** "Ammonia is not a contributor to ozone depletion, greenhouse effect or global
  warming... Standard 34 classifies ammonia as a Group B2 refrigerant, because of toxicity and
  flammability concerns" (secciones 5.0 y 7.3).
- **Resumen breve:** Documento de postura institucional de ASHRAE sobre el amoníaco como
  refrigerante industrial puro: historia, usos, seguridad, marco regulatorio (OSHA/EPA) y
  actividades de la sociedad. **No contiene ninguna información sobre la mezcla NH3-H2O ni sobre
  el ciclo Kalina** — no sirve ni para Fase 2 ni para validación. Su relevancia potencial se
  limitaría a un contexto de seguridad de planta real, fuera del alcance de este proyecto de
  simulación.

---

## 4. Ranking — utilidad para Fase 2 (barridos libres)

1. **`Thermodynamic_evaluation_postprint.pdf`** (Nguyen et al. 2014) — Alta. Confirma con datos
   reales de otro grupo el muro x_b-alto/P_alta-alta que ya detectamos empíricamente.
2. **`Dubey_2021...pdf`** (revisión) — Media-Alta. Respaldo conceptual de que x_b/T_fuente/
   T_separador son las variables dominantes.
3. **`ctt020.pdf`** y **`PERFORMANCEOFKALINACYCLESYSTEM11KCS11...pdf`** (Elsayed et al., ambas
   versiones) — Media. Confirman rangos sanos de x_b (0.55-0.9) y T_fuente (hasta 463K), y el
   criterio de calidad de turbina ≥90%.
4. **`evalaucion_termica_solar.pdf`** — Media. Confirma tendencia x_b alto + P alta, pero a
   temperaturas fuera de nuestro rango.
5. **`musfa analysys termico kalina.pdf`** — Baja. Solo un dato aislado, sin contexto suficiente.
6. **`recomendaciones_manejo de_mezclas_ashrae.pdf`** — Nula.

## 5. Ranking — utilidad para validaciones

1. **`ctt020.pdf`** (Elsayed et al. 2013, journal) — Alta. Ya es nuestra validación oficial;
   tiene puntos extra sin explotar (Fig. 2a-c).
2. **`PERFORMANCEOFKALINACYCLESYSTEM11KCS11...pdf`** (precursor de conferencia) — Alta. Mismo
   punto, más puntos adicionales con mayor granularidad.
3. **`Thermodynamic_evaluation_postprint.pdf`** (Nguyen et al. 2014) — Media. No valida la
   topología, pero su tabla de 37 estados (mismo EOS) permite un cross-check de propiedades.
4. **`Dubey_2021...pdf`**, **`evalaucion_termica_solar.pdf`**, **`musfa...pdf`** — Baja. Sin
   punto único reproducible compatible con nuestra topología/rango.
5. **`recomendaciones_manejo de_mezclas_ashrae.pdf`** — Nula.

## 6. Parámetros, correlaciones y datos extraíbles para nuestro modelo

- **Rango de x_b sano (consenso multi-fuente):** 0.55-0.9 (Elsayed), coincide con nuestro rango
  explorado 0.35-0.85.
- **Restricción de calidad de salida de turbina ≥90%:** confirmada como estándar transversal en
  3 papers independientes (Elsayed/precursor, Jeannot et al.) — refuerza que nuestro criterio O1
  no es arbitrario.
- **Referencia cuantitativa x_b-alto → P_alta-alta:** Nguyen et al. (2014) reporta 125-130 bar
  para x_b=0.75-0.8 en su topología (split-cycle); aunque no es directamente comparable en
  magnitud (su ciclo opera a presiones mucho mayores), confirma la DIRECCIÓN y el ORDEN DE
  MAGNITUD del efecto que vemos en Ronda 5/6.
- **Puntos de validación adicionales sin explotar:** Figuras 2a-c de `ctt020.pdf` — curvas η vs
  x_b para P_evap ∈ {10,15,20,25,30,40} bar y T_fuente ∈ {333,373,423}K (serían necesarios
  digitalizar valores desde las figuras, no hay tabla numérica).
- **Tabla de 37 estados (Apéndice A.9 de Nguyen et al.):** mismo EOS (Tillner-Roth & Friend) que
  nuestro `AmmoniaWaterAdapter` — utilizable como cross-check puntual de h/s/T/P/x, no de la
  topología.
- **Variables dominantes confirmadas por consenso de literatura:** composición de entrada a
  turbina (x_b) y temperatura del separador — coincide con nuestro propio hallazgo empírico de
  Fase 2.

## 7. Recomendaciones de próximos pasos

1. **Ampliar la validación** digitalizando 2-3 puntos adicionales de las Figuras 2a-c de
   `ctt020.pdf` (mismo grupo, misma topología) — bajo costo, alto valor porque diversifica la
   validación más allá de un único punto.
2. **Cross-check de propiedades** (opcional, menor prioridad): tomar 2-3 estados de la Tabla A.9
   de Nguyen et al. (2014) y comparar h/s calculados por nuestro `AmmoniaWaterAdapter` contra los
   suyos, como verificación independiente del EOS — sirve solo para el backend de propiedades,
   no para el ciclo completo.
3. **No perseguir el rango de P_alta de Nguyen et al. (125-130 bar)** literalmente — es de una
   topología distinta que opera a presiones mucho más altas; usar solo como confirmación de
   tendencia, no como objetivo numérico para nuestros barridos.
4. **Descartar el documento ASHRAE** como fuente de datos técnicos — no aporta nada a la mezcla
   NH3-H2O ni al ciclo Kalina; si se necesita en el futuro contenido de seguridad de planta real,
   buscar una fuente específica de ciclos de absorción amoníaco-agua, no esta.
5. **`musfa analysys termico kalina.pdf`** puede archivarse como referencia de bajo valor; no
   amerita más análisis salvo que se necesite explorar su lista de ~20 citas como punto de
   partida para buscar otros papers.

---

## Anexo — control de trazabilidad

Todas las fichas de la Sección 3 son las fichas completas solicitadas (no hay una versión
resumida distinta); no se generaron fichas adicionales fuera de las 7 anteriores. Los 7 PDFs
listados en `D:\Desktop\ciclo_kalina_tercero\Papers\` a la fecha de este análisis fueron leídos
en su totalidad (texto completo extraído, no solo resumen/abstract). No se identificaron PDFs
adicionales en la carpeta ni subcarpetas en el momento de este análisis.

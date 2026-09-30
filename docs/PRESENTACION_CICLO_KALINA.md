# Presentación: Ciclo Kalina KCS-11 — Modelado, verificación y validación

> **Supuestos tomados por no estar especificados en la petición** (ajústalos si no aplican):
> - **Público objetivo:** `[pendiente — no se indicó]`. Se redactó asumiendo un jurado/profesor evaluador de un curso de termodinámica aplicada (Entregable 1), con conocimiento técnico pero sin contexto previo de este proyecto específico. Si el público real es distinto (clientes, estudiantes de un curso introductorio, etc.), el tono de las diapositivas 4-11 debería suavizarse.
> - **Duración:** 10-15 minutos (no especificada, se usó el valor por defecto indicado en la petición).
> - **Número de diapositivas:** 15 (no especificado, se usó el valor por defecto indicado en la petición).
> - **Tono:** formal-técnico con apoyo didáctico — coherente con que el respaldo es el material interactivo "Atlas del Ciclo Kalina" ya construido, que sí tiene modo niño/ingeniero.
> - Todos los datos numéricos citados abajo provienen del material ya generado en este proyecto (`PLANTEAMIENTO_MATEMATICO.md`, `VALIDACION_ELSAYED2013.md`, `resultados/BITACORA_BARRIDOS.md`, y el Atlas interactivo). Ningún dato fue inventado; donde falta información se marca `[pendiente]`.

---

## Diapositiva 1: Portada
- **Contenido breve:**
  - Ciclo Kalina KCS-11: modelado termodinámico, verificación y validación
  - `[pendiente — nombre del curso / asignatura]`
  - `[pendiente — nombre(s) del/los autor(es)]`
  - `[pendiente — fecha de exposición]`
- **Elementos visuales sugeridos:** el ícono/marca del Atlas interactivo (el cuadrado "K" con degradado teal→ámbar usado en la cabecera del material interactivo) sobre fondo limpio; opcionalmente el esquema de los 10 estados en miniatura como fondo tenue.
- **Notas del expositor:** "Voy a presentar el trabajo de modelado del ciclo Kalina KCS-11 que constituye el Entregable 1: qué se construyó, cómo se verificó contra la literatura, y qué queda pendiente. Todo el material de estudio detallado está además disponible como una guía interactiva que dejo como referencia."

## Diapositiva 2: Agenda
- **Contenido breve:**
  - Qué es el Ciclo Kalina y por qué importa
  - Cómo se modeló matemáticamente
  - Cómo se verificó (17 criterios) y se validó (Elsayed et al. 2013)
  - Demo del material interactivo
  - Estado actual y próximos pasos
- **Elementos visuales sugeridos:** lista simple con iconografía (termómetro, engranaje, check, pantalla, bandera de meta) — sin imágenes complejas, esta diapositiva es solo de orientación.
- **Notas del expositor:** "La estructura sigue el mismo orden del material de estudio: primero el fundamento físico, luego el código, luego la evidencia de que funciona, y al final el estado del proyecto."

## Diapositiva 3: El problema que resuelve
- **Contenido breve:**
  - Fuentes de calor de baja temperatura (geotermia, calor residual) se enfrían progresivamente
  - Un Rankine de agua pura hierve a T constante → desperdicia potencial contra esa fuente
  - El Kalina usa una mezcla NH₃-H₂O que hierve sobre un rango de temperatura (*glide*)
  - Eso permite seguir más de cerca la curva de enfriamiento de la fuente
- **Elementos visuales sugeridos:** el gráfico de comparación de perfiles T vs. calor transferido (fuente / fluido puro / mezcla con glide) — está construido en SVG en la sección 02 del Atlas interactivo; se puede capturar como imagen o recrear en la herramienta de la presentación.
- **Notas del expositor:** "Esta es la motivación de fondo: el Kalina no es 'mejor' en abstracto, resuelve un problema específico de acoplamiento térmico con fuentes que se enfrían, como la geotermia de baja entalpía."

## Diapositiva 4: Topología del ciclo — KCS-11
- **Contenido breve:**
  - 10 estados termodinámicos, 8 componentes
  - HRVG → Separador → {Turbina ; Regenerador+Válvula} → Absorbedor → Condensador → Bomba
  - El separador y el absorbedor no existen en un Rankine convencional
- **Elementos visuales sugeridos:** el diagrama de flujo SVG de los 10 estados (Atlas, sección 01) — es la pieza visual más informativa del material existente, capturar tal cual o redibujar en la herramienta de presentación.
- **Notas del expositor:** "Esta es la configuración específica que se implementó, llamada KCS-11 en la literatura. El separador reparte la mezcla en una fase rica y otra pobre en amoníaco; el absorbedor las vuelve a juntar antes de la bomba."

## Diapositiva 5: El "compresor térmico"
- **Contenido breve:**
  - El ciclo nunca comprime vapor con trabajo de eje
  - Absorbedor → líquido; Bomba → sube presión de un líquido (barato); HRVG → revaporiza con calor
  - Mismo mecanismo que un ciclo de refrigeración por absorción, aplicado al revés
  - Por eso `W_bomba` es órdenes de magnitud menor que `W_turbina`
- **Elementos visuales sugeridos:** diagrama de 3 pasos (Absorbedor → Bomba → HRVG) con iconos simples (gota, flecha hacia arriba, llama); es un concepto conceptual, no necesita gráfico de datos.
- **Notas del expositor:** "Este es un punto que suele pasar desapercibido y que vale la pena remarcar: la 'compresión' hasta la presión alta no la hace una máquina mecánica, la hace el conjunto absorbedor-bomba-HRVG usando calor. Es la razón por la que el trabajo de bombeo es tan pequeño frente al de la turbina."

## Diapositiva 6: Planteamiento matemático
- **Contenido breve:**
  - Balances de masa, energía y (para exergía) entropía en cada componente
  - HRVG, regenerador y condensador cierran por **efectividad térmica**, no por *pinch point*
  - Turbina y bomba con eficiencia isentrópica estándar
  - Documento completo: `PLANTEAMIENTO_MATEMATICO.md`
- **Elementos visuales sugeridos:** una sola ecuación destacada como ejemplo representativo (sugerido: la de efectividad del HRVG, `h_2 = h_1 + ε·(h_2,max − h_1)`) en tipografía grande — no saturar la diapositiva con las 8 ecuaciones completas, esas están en el material interactivo (sección 04) con despeje y ejemplo numérico paso a paso.
- **Notas del expositor:** "No voy a mostrar las ocho ecuaciones aquí — eso está detallado con derivación y ejemplo numérico en el material interactivo que voy a mostrar más adelante. Lo importante ahora es la decisión de diseño: cerrar por efectividad en vez de pinch, que se justifica y se cuantifica más adelante."

## Diapositiva 7: Verificación — 17 criterios de admisibilidad
- **Contenido breve:**
  - Numéricos (balance de energía y especie), segunda ley (8 criterios), operacionales, composición
  - Severidad: `NO_CONVERGIO > INVIABLE > DEGENERADO > CORREGIBLE > VALIDO_ADVERTENCIA > KALINA`
  - Ningún punto se oculta: todo punto de barrido queda clasificado y registrado
- **Elementos visuales sugeridos:** pirámide o escala de severidad de 6 niveles (de rojo a verde) con la etiqueta de cada nivel — visual simple tipo semáforo/embudo.
- **Notas del expositor:** "Cada punto que resuelve el ciclo pasa por 17 chequeos antes de llamarse una solución válida. La regla del proyecto es que ningún resultado se descarta silenciosamente: si algo falla, queda etiquetado y visible en los datos."

## Diapositiva 8: Arquitectura del código
- **Contenido breve:**
  - Patrón adapter: interfaz única `PropertyBackend` (8 métodos) para propiedades termodinámicas
  - Dos motores intercambiables: `AmmoniaWaterAdapter` (riguroso, IAPWS G4-01) y `TeqpAdapter` (rápido, validado contra el primero con error <0.5 %)
  - Barrido cartesiano sobre 11 variables de entrada (Fijo o Barrido), no un optimizador
- **Elementos visuales sugeridos:** diagrama simple de caja: "Solver del ciclo → interfaz PropertyBackend → [AmmoniaWaterAdapter | TeqpAdapter]" para mostrar el desacople.
- **Notas del expositor:** "El adapter permite que el ciclo se resuelva igual sin importar qué motor de propiedades está detrás. Eso permitió cruzar dos implementaciones independientes como verificación cruzada."

## Diapositiva 9: Cierre del ciclo — dos lazos anidados
- **Contenido breve:**
  - El estado 1 (entrada al HRVG) depende de un balance que retroalimenta sobre sí mismo
  - Lazo interno: sustitución sucesiva sobre `T_10` (tolerancia 10⁻³ K)
  - Lazo externo: método de Brent sobre `T_1`, acotado en `(T_sumidero, T_fuente)`
- **Elementos visuales sugeridos:** el diagrama de flujo de los dos lazos anidados (Atlas, sección 08) — capturar directamente, es la explicación visual más clara ya construida para este punto.
- **Notas del expositor:** "Esto no se resuelve en un solo paso hacia adelante: hay que iterar. El material interactivo tiene un ejemplo numérico completo que muestra justo este residuo de convergencia paso a paso."

## Diapositiva 10: Validación externa — Elsayed et al. (2013)
- **Contenido breve:**
  - Caso KCS-11 replicado: `P_alta=1500 kPa`, `x_b=0.55`, `T_fuente=373 K`, `T_sumidero=283 K`
  - η paper = 11.38 % · η este proyecto = 11.05–11.055 % (ambos motores)
  - Diferencia ≈0.33 pp, atribuida a: EOS distinta, traducción pinch→efectividad de un solo paso, `P_baja` asumida
  - Validación extendida: 23 puntos comparables, Δη medio −0.06 pp
- **Elementos visuales sugeridos:** tabla o gráfico de barras de 3 valores (paper, `AmmoniaWaterAdapter`, `TeqpAdapter`) con el δ marcado; puede ser una tabla simple, no necesita ser complejo.
- **Notas del expositor:** "Esta es la pieza central de evidencia: no solo se comparó un punto, se comparó contra 23 puntos de tendencia, y la diferencia observada tiene una explicación causal identificada, no es un ajuste sin justificar."

## Diapositiva 11: Qué muestran los barridos paramétricos
- **Contenido breve:**
  - Más de una decena de barridos documentados en `resultados/BITACORA_BARRIDOS.md`
  - Hallazgo clave: el piso de temperatura ambiente de cavitación (criterio O2) bloqueaba casi todo el espacio explorado por un supuesto climático no verificado
  - Al corregirlo con el sumidero real (283.15 K), aparecieron 16 puntos KALINA de 60 evaluados
- **Elementos visuales sugeridos:** gráfico de barras "antes/después" mostrando 0 → 16 puntos KALINA al corregir el supuesto de temperatura ambiente.
- **Notas del expositor:** "Este hallazgo ilustra por qué la verificación de supuestos es tan importante como el modelo mismo: un solo número mal justificado casi invalidaba el barrido completo."

## Diapositiva 12: Demo — material interactivo "Atlas del Ciclo Kalina"
- **Contenido breve:**
  - Guía interactiva con 15 secciones navegables (fundamentos, código, análisis, respaldo, defensa)
  - Modo Ingeniero / Modo Niño con un clic
  - Ejemplo numérico encadenado componente a componente, con despeje algebraico
  - Sección dedicada: "El profesor te va a preguntar…" (20 preguntas con respuesta)
- **Elementos visuales sugeridos:** captura de pantalla real del Atlas (sección de inicio con el índice lateral visible), y una segunda captura de la sección de matemáticas mostrando un bloque de despeje + ejemplo.
- **Notas del expositor:** *(aquí se recomienda hacer la demo en vivo, no solo mostrar capturas)* "Voy a mostrar brevemente la herramienta en vivo: el índice de navegación, el cambio de modo, y la sección de preguntas de defensa."

## Diapositiva 13: Estado actual del proyecto
- **Contenido breve:**
  - Logrado: dos motores cruzados (<0.5 % error), correcciones IAPWS G4-01 verificadas, validación Elsayed (punto + 23 puntos), UI con pestañas de nivel superior
  - Pendiente: confirmar 3-5 puntos KALINA adicionales con el motor riguroso
  - Pendiente: documentar formalmente la elección de cierre por efectividad y el piso de O2 en el informe final
  - `N4` (dominio de validez del modelo de propiedades) queda explícitamente sin resolver
- **Elementos visuales sugeridos:** checklist visual de dos columnas ("Logrado" con check verde / "Pendiente" con reloj o flecha) — sin gráficos de datos, es una lista de estado.
- **Notas del expositor:** "Quiero ser explícito sobre qué falta, no solo sobre qué se logró: eso es parte de la honestidad metodológica del trabajo."

## Diapositiva 14: Conclusiones
- **Contenido breve:**
  - El modelo reproduce la física esperada (glide, compresor térmico, segunda ley) con verificación de 17 criterios
  - La validación externa confirma el orden de magnitud y la tendencia frente a literatura publicada
  - Los supuestos con más impacto (cierre por efectividad, piso de O2) están identificados y cuantificados, no escondidos
  - El material interactivo deja trazabilidad completa para revisión
- **Elementos visuales sugeridos:** una sola imagen de síntesis, por ejemplo el esquema de los 10 estados reutilizado de la diapositiva 4, para cerrar visualmente donde se abrió.
- **Notas del expositor:** "En resumen: se construyó, se verificó internamente y se validó externamente un modelo del ciclo Kalina KCS-11, documentando explícitamente tanto lo que funciona como sus límites conocidos."

## Diapositiva 15: Cierre y preguntas
- **Contenido breve:**
  - Gracias
  - Enlace/acceso al material interactivo (Atlas del Ciclo Kalina)
  - `[pendiente — datos de contacto si aplica]`
  - Espacio abierto para preguntas
- **Elementos visuales sugeridos:** diapositiva minimalista, fondo consistente con la portada, sin más elementos que el texto de cierre.
- **Notas del expositor:** "Quedo abierto a preguntas — y si alguna pregunta coincide con las que ya anticipé en la sección de defensa del material interactivo, lo menciono para mostrar que se pensó de antemano."

---

## Checklist de diseño

- [ ] Una idea principal por diapositiva (ninguna diapositiva mezcla dos temas no relacionados)
- [ ] Máximo 5 bullets por diapositiva, frases cortas (no párrafos)
- [ ] Contraste de texto suficiente sobre el fondo elegido (verificar en modo claro y oscuro si la plantilla lo permite)
- [ ] Jerarquía visual consistente: mismo tamaño/peso de título en todas las diapositivas, mismo estilo de bullet
- [ ] Paleta de color consistente en las 15 diapositivas (se sugiere reutilizar la paleta teal/ámbar del Atlas interactivo para dar continuidad visual entre ambos materiales)
- [ ] Las capturas del Atlas interactivo (diapositivas 3, 4, 9, 12) se toman a buena resolución, sin recortar texto
- [ ] Números y datos citados (validación, barridos) coinciden exactamente con los del material interactivo y `VALIDACION_ELSAYED2013.md` — no redondear de más ni parafrasear cifras
- [ ] Revisar que ningún `[pendiente]` quede sin resolver antes de la exposición final
- [ ] Ensayar la demo en vivo del Atlas (diapositiva 12) antes de la presentación real, con conexión/equipo de respaldo si el acceso depende de un enlace

## Materiales y recursos necesarios

- Acceso al material interactivo "Atlas del Ciclo Kalina" (enlace del artefacto) para la demo en vivo y para capturas de pantalla
- `PLANTEAMIENTO_MATEMATICO.md`, `VALIDACION_ELSAYED2013.md` y `resultados/BITACORA_BARRIDOS.md` a mano para responder preguntas con precisión numérica
- Herramienta de presentación (Gemini, PowerPoint, Google Slides, etc.) con una plantilla que permita fondo claro y oscuro consistente
- Equipo/proyector con salida a internet o el archivo del Atlas descargado localmente, por si la demo en vivo no tiene conectividad
- `[pendiente]` — nombre del curso, autores y fecha, para completar la diapositiva 1
- `[pendiente]` — confirmar el público objetivo real antes de ajustar el tono de las diapositivas 4-11

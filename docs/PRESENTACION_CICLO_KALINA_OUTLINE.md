# Ciclo Kalina KCS-11: modelado, verificación y validación

## Ciclo Kalina KCS-11
- Modelado termodinámico, verificación y validación
- [pendiente — nombre del curso / asignatura]
- [pendiente — autor(es)]
- [pendiente — fecha]

> Notas: Voy a presentar el trabajo de modelado del ciclo Kalina KCS-11, Entregable 1: qué se construyó, cómo se verificó contra la literatura, y qué queda pendiente. Todo el material de estudio detallado está disponible además como una guía interactiva que dejo como referencia.

## Agenda
- Qué es el Ciclo Kalina y por qué importa
- Cómo se modeló matemáticamente
- Cómo se verificó (17 criterios) y se validó (Elsayed et al., 2013)
- Demo del material interactivo
- Estado actual y próximos pasos

> Notas: La estructura sigue el mismo orden del material de estudio: primero el fundamento físico, luego el código, luego la evidencia de que funciona, y al final el estado del proyecto.

## El problema que resuelve
- Las fuentes de calor de baja temperatura (geotermia, calor residual) se enfrían progresivamente al ceder calor
- Un Rankine de agua pura hierve a temperatura constante → desperdicia potencial contra una fuente que no lo es
- El Kalina usa una mezcla NH₃-H₂O que hierve sobre un rango de temperatura (glide zeotrópico)
- El glide permite que el fluido de trabajo siga más de cerca la curva de enfriamiento de la fuente, reduciendo la exergía destruida

> Notas: Esta es la motivación de fondo: el Kalina no es "mejor" en abstracto, resuelve un problema específico de acoplamiento térmico con fuentes que se enfrían, típico de geotermia de baja entalpía o calor residual industrial.
> Visual sugerido: gráfico de perfiles de temperatura (fuente / fluido puro / mezcla con glide) — está en la sección 02 del Atlas interactivo.

## Topología del ciclo KCS-11
- 10 estados termodinámicos, 8 componentes
- Ruta principal: HRVG → Separador → {Turbina ; Regenerador + Válvula} → Absorbedor → Condensador → Bomba
- El separador reparte la corriente en vapor rico y líquido pobre en amoníaco
- El absorbedor vuelve a juntar ambas corrientes antes de la bomba
- Separador y absorbedor no existen en un Rankine convencional

> Notas: Esta es la configuración específica implementada, llamada KCS-11 en la literatura.
> Visual sugerido: diagrama de flujo de los 10 estados (Atlas interactivo, sección 01).

## El ciclo no tiene compresor: tiene un "compresor térmico"
- El ciclo nunca comprime vapor con trabajo de eje
- Absorbedor: el vapor de turbina se absorbe en el líquido pobre → vuelve a ser líquido
- Bomba: sube de presión un líquido (barato, casi incompresible)
- HRVG: revaporiza con calor, no con trabajo mecánico
- Mismo mecanismo que un ciclo de refrigeración por absorción, aplicado al revés
- Consecuencia medible: W_bomba es órdenes de magnitud menor que W_turbina

> Notas: Punto que suele pasar desapercibido y vale la pena remarcar: la "compresión" hasta presión alta no la hace una máquina mecánica, la hace el trío absorbedor-bomba-HRVG usando calor.

## Planteamiento matemático
- Balances de masa, energía y (para exergía) entropía en cada componente
- HRVG, regenerador y condensador cierran por efectividad térmica (ε), no por pinch point
- Turbina y bomba con eficiencia isentrópica estándar (η_t, η_p)
- Ejemplo — cierre del HRVG: h₂ = h₁ + ε_HRVG·(h₂,max − h₁)
- Documento completo con las 8 ecuaciones, despeje y ejemplo numérico: `PLANTEAMIENTO_MATEMATICO.md` y sección 04 del Atlas interactivo

> Notas: No voy a mostrar las ocho ecuaciones aquí — eso está detallado con derivación y ejemplo numérico paso a paso en el material interactivo. Lo importante ahora es la decisión de diseño: cerrar por efectividad en vez de pinch, justificada y cuantificada más adelante.

## Verificación: 17 criterios de admisibilidad
- Numéricos: balance de energía global (N2) y de especie (N3)
- Segunda ley: 8 criterios (S1–S8), incluyendo el techo de Carnot
- Operacionales: título de vapor en turbina (O1), cavitación en bomba (O2), trabajo neto positivo (O3), título en HRVG (O5)
- Composición: orden físico x₅ < x_b < x₃ (C1), rangos válidos (C2, C3)
- Severidad decreciente: NO_CONVERGIO > INVIABLE > DEGENERADO > CORREGIBLE > VALIDO_ADVERTENCIA > KALINA
- Ningún punto se oculta: todo resultado de barrido queda clasificado y registrado

> Notas: Cada punto que resuelve el ciclo pasa por estos 17 chequeos antes de llamarse una solución válida. La regla del proyecto es que ningún resultado se descarta silenciosamente.

## Arquitectura del código
- Patrón adapter: interfaz única `PropertyBackend` (8 métodos) para propiedades termodinámicas
- Dos motores intercambiables:
  - `AmmoniaWaterAdapter` — riguroso, IAPWS G4-01, ~312 s/punto
  - `TeqpAdapter` — rápido (~20×), validado contra el primero con error <0.5 % en h, s
- Barrido cartesiano sobre 11 variables de entrada (cada una Fijo o Barrido), no un optimizador de gradiente
- El dominio tiene discontinuidades (separador, cavitación) que un optimizador podría saltarse

> Notas: El adapter permite que el ciclo se resuelva igual sin importar qué motor de propiedades está detrás. Eso permitió cruzar dos implementaciones independientes como verificación.

## Cierre del ciclo: dos lazos anidados
- El estado 1 (entrada al HRVG) depende de un balance que retroalimenta sobre sí mismo
- Lazo interno: sustitución sucesiva sobre T₁₀ (tolerancia 10⁻³ K)
- Lazo externo: método de Brent sobre T₁, acotado en (T_sumidero, T_fuente)
- No se puede resolver en un solo paso hacia adelante

> Notas: El material interactivo (sección 08) tiene un ejemplo numérico completo que muestra este residuo de convergencia paso a paso.
> Visual sugerido: diagrama de los dos lazos anidados (Atlas interactivo, sección 08).

## Validación externa: Elsayed et al. (2013)
- Caso replicado: P_alta=1500 kPa, x_b=0.55, T_fuente=373 K, T_sumidero=283 K, η_t=η_p=0.80
- η del paper: 11.38 %
- η de este proyecto: 11.05 % (AmmoniaWaterAdapter) / 11.055 % (TeqpAdapter)
- Diferencia ≈ 0.33 puntos porcentuales (~2.9 % relativo), dentro del umbral de 5 % del test de regresión
- Causas identificadas: ecuación de estado distinta (Tillner-Roth/Friend vs. Ibrahim/Klein), traducción pinch→efectividad de un solo paso, P_baja asumida
- Validación extendida: 23 puntos comparables, Δη medio −0.06 pp

> Notas: Esta es la pieza central de evidencia: se comparó no solo un punto, sino 23 puntos de tendencia, y la diferencia observada tiene una causa identificada, no es un ajuste sin justificar.

## Qué muestran los barridos paramétricos
- Más de una decena de barridos documentados en `resultados/BITACORA_BARRIDOS.md`
- Hallazgo clave: el piso de temperatura ambiente del criterio de cavitación (O2) bloqueaba casi todo el espacio explorado
- Ese piso (30.4 °C) era un supuesto climático genérico, no verificado
- Al corregirlo con el sumidero real (283.15 K): aparecieron 16 puntos KALINA de los mismos 60 evaluados
- Sensibilidad adicional al margen de pinch (2 K, 4 K, 6 K): cada nivel de margen cuesta eficiencia de forma medible

> Notas: Este hallazgo ilustra por qué verificar los supuestos es tan importante como el modelo mismo: un solo número mal justificado casi invalidaba el barrido completo.

## Demo: Atlas del Ciclo Kalina (material interactivo)
- Guía interactiva con 15 secciones navegables: fundamentos, código, análisis, respaldo, defensa
- Modo Ingeniero / Modo Niño intercambiable con un clic
- Ejemplo numérico encadenado componente a componente, con despeje algebraico completo
- Sección dedicada "El profesor te va a preguntar…": 20 preguntas incisivas con respuesta lista
- Glosario y bibliografía citada (Tillner-Roth & Friend 1998, Ibrahim & Klein 1993, Elsayed et al. 2013)

> Notas: Se recomienda hacer la demo en vivo, no solo mostrar capturas: mostrar el índice de navegación, el cambio de modo, y la sección de preguntas de defensa.

## Estado actual del proyecto
- Logrado: dos motores de propiedades cruzados (<0.5 % error), dos correcciones IAPWS G4-01 verificadas contra las Tablas 7-8
- Logrado: validación externa Elsayed (punto único + 23 puntos de tendencia)
- Logrado: interfaz con pestañas de nivel superior sobre el mismo backend intercambiable
- Pendiente: confirmar 3–5 puntos KALINA adicionales con el motor riguroso
- Pendiente: documentar formalmente la elección de cierre por efectividad y la justificación del piso de O2 en el informe final
- N4 (dominio de validez completo del modelo de propiedades) queda explícitamente sin resolver

> Notas: Quiero ser explícito sobre qué falta, no solo sobre qué se logró — es parte de la honestidad metodológica del trabajo.

## Conclusiones
- El modelo reproduce la física esperada (glide, compresor térmico, segunda ley) bajo 17 criterios de verificación
- La validación externa confirma orden de magnitud y tendencia frente a literatura publicada
- Los supuestos de mayor impacto (cierre por efectividad, piso de O2) están identificados y cuantificados, no escondidos
- El material interactivo deja trazabilidad completa para revisión y defensa

> Notas: En resumen: se construyó, se verificó internamente y se validó externamente un modelo del ciclo Kalina KCS-11, documentando tanto lo que funciona como sus límites conocidos.

## Gracias
- Acceso al material interactivo: Atlas del Ciclo Kalina
- [pendiente — datos de contacto si aplica]
- Espacio abierto para preguntas

> Notas: Quedo abierto a preguntas — si alguna coincide con las que ya anticipé en la sección de defensa del material interactivo, lo menciono para mostrar que se pensó de antemano.

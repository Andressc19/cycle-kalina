# CONTEXT.md — Datos de ingeniería confirmados (ciclo Kalina KSC-11)

Este archivo es la única fuente de verdad para valores por defecto y fórmulas que no estén
explícitas en el `TASK_CONTEXT.md` de una tarea puntual. Viene del prompt base
(`Kalina_ksc_11_tercero.md`) más lo confirmado contra el vault de Obsidian del proyecto
hermano (Ciclo Kalina, sesiones previas con Claude). **No hay que inventar nada de lo que
sigue; lo que no está aquí y no está en el prompt de la tarea, se reporta en UNRESOLVED.**

## Mapa de estados (10 estados, confirmado)

```
10 →[Regenerador frío]→ 1 →[HRVG]→ 2 →[Separador]→ { 3 →[Turbina]→ 4 ; 5 →[Regenerador caliente]→ 6 →[Válvula]→ 7 }
4 + 7 →[Absorbedor]→ 8 →[Condensador]→ 9 →[Bomba]→ 10
```

## Fórmulas de efectividad (método a implementar en esta versión)

- **HRVG**: ε_HRVG = (h2 − h1) / (h2,max − h1), con h2,max = h(T_fuente, P_alta, x_b).
  Código de referencia: `h2 = h1 + eps_hrvg * (h2_ideal - h1)`.
- **Regenerador**: ε_reg = (h5 − h6) / (h5 − h6,min), con h6,min = h(T10, P_alta, x5).
  Código de referencia: `h6 = h5 - eps_reg * (h5 - h6_ideal)`.
- **Condensador**: ε_cond = (h8 − h9) / (h8 − h9,min), con h9,min = h(T_sumidero, P_baja, x_b).
  Código de referencia: `h9 = h8 - eps_cond * (h8 - h9_ideal)`.

(Existe también un "método por approach/pinch" alternativo documentado en el proyecto hermano,
pero **no es el que pide esta versión** — usar solo el método de efectividad anterior salvo que
una tarea puntual diga explícitamente lo contrario.)

## Separador

Separador **ideal**: no tiene parámetro de eficiencia propio. Reparte la corriente 2 en vapor
saturado (3, hacia turbina) y líquido saturado (5, hacia regenerador) a la misma P y T de
equilibrio, con las composiciones de equilibrio líquido-vapor de la mezcla NH3-H2O a esa P,T y
la composición global x_b (regla de la palanca). Si el backend de propiedades no da directamente
el equilibrio L-V, reportar en `UNRESOLVED` en vez de aproximar con un supuesto no pedido.

## Absorbedor

Mezcla adiabática de las corrientes 4 (salida turbina) y 7 (salida válvula), sin caída de
presión, sin modelo cinético:

- Balance de masa: ṁ8 = ṁ4 + ṁ7
- Balance de especie: x8 = x_b (recuperado por la regla de la palanca del separador; en estado
  estacionario x8 debe reconstruir la composición global de la mezcla).
- Balance de energía: ṁ8 · h8 = ṁ4 · h4 + ṁ7 · h7

## Válvula

Isoentálpica: h7 = h6.

## Turbina y bomba

Eficiencia isentrópica estándar:

- Turbina: h4 = h3 − η_t · (h3 − h4s), h4s = h(P_baja, s3, x3)
- Bomba: h10 = h9 + (h10s − h9) / η_p, h10s = h(P_alta, s9, x9)

## Estado muerto (para exergía física)

- **T0 = 300.032917 K** (confirmado: media de un perfil horario de temperatura ambiente,
  297.95–303.55 K).
- **P0: NO está definido en ninguna fuente disponible.** Queda como campo configurable en la
  interfaz, con valor por defecto **P0 = 101.325 kPa** (atmosférica estándar) — supuesto
  explícito, documentar en `ASSUMPTIONS` de la tarea que lo use.
- **x0 NO hace falta.** Como esta versión excluye exergía química (solo exergía física), el
  estado de referencia de cada corriente se evalúa a `(T0, P0)` **con la composición propia de
  esa corriente** (`x0 = x_corriente`, no una composición ambiental universal) — es
  precisamente lo que distingue la exergía física de la química: no hay "desmezcla" hasta el
  ambiente, solo enfriar/despresurizar la corriente hasta `(T0, P0)` manteniendo su propia
  composición. Fórmula por corriente:
  ```
  ex_fisica = (h − h0) − T0 · (s − s0),  con  h0 = h(P0, T0, x_corriente),  s0 = s(P0, T0, x_corriente)
  ```

## Balance de entropía/exergía por componente (para la tarea de exergía)

Exergía destruida de un componente: `Ed = T0 · Sgen`. `Sgen` (balance de entropía en
estado estacionario, sin generación en las corrientes mismas) para cada componente:

- HRVG (calor `Qi` suministrado por la fuente, modelada como reservorio a `T_fuente`):
  `Sgen = m_b·(s2 − s1) − Qi / T_fuente`
- Separador (adiabático, sin trabajo): `Sgen = m3·s3 + m5·s5 − m2·s2`
- Turbina (adiabática): `Sgen = m3·(s4 − s3)` (mismo caudal, `m3=m4`)
- Regenerador (intercambio interno, sin calor con el ambiente):
  `Sgen = m5·(s6 − s5) + m10·(s1 − s10)` (lado caliente + lado frío; `m10=m1=m_b`)
- Válvula (adiabática): `Sgen = m6·(s7 − s6)`
- Absorbedor (adiabático, mezcla): `Sgen = m8·s8 − m4·s4 − m7·s7`
- Condensador (calor `Qout` rechazado al sumidero, modelado como reservorio a `T_sumidero`):
  `Sgen = m8·(s9 − s8) + Qout / T_sumidero`
- Bomba (adiabática): `Sgen = m9·(s10 − s9)`

Verificación de cierre (balance de exergía global del ciclo, debe cumplirse dentro de
tolerancia numérica — es la forma correcta de comprobar que las fórmulas anteriores están
bien, sin necesitar un valor de referencia externo):
```
Ex_Qi = Qi · (1 − T0/T_fuente)         # exergía entregada por la fuente
Ex_Qout = Qout · (1 − T0/T_sumidero)   # exergía que se va con el calor rechazado
Ex_Qi − Wnet − Ex_Qout ≈ Ed_total = Σ Ed_componente
```

## Valores por defecto sugeridos para la UI (no obligatorios, el usuario puede cambiarlos)

| Variable | Valor por defecto |
|---|---|
| P_high | 3.0 MPa |
| P_low | 0.4 MPa |
| x_NH3 (x_b, composición global) | 0.50 |
| T_fuente | 470.0 K (197 °C) |
| T0 / T_amb | 300.032917 K |
| η_turbina (isentrópica) | 0.85 |
| η_bomba (isentrópica) | 0.75 |
| ε_HRVG | 0.85 |
| ε_regenerador | 0.75 |
| ε_condensador | 0.80 |
| ṁ_work (base de cálculo) | 1.0 kg/s |
| T_agua_in | = T0 por defecto (sumidero se puede asumir infinito si el usuario no da ṁ_agua) |

No hay eficiencia de separador (es ideal, ver arriba).

**Nota (2026-09-17, tarea `2026-09-17-diagnostico-rendimiento-solver`):**
`T_fuente` bajó de 623.15 K a **470.0 K** porque con 623.15 K el estado 2 del
HRVG quedaba fuera de la campana bifásica a P_alta=3000 kPa (campana
338.87-507.00 K a 3 MPa), y el separador (flash directo) no puede repartir una
corriente monofásica. Con T_fuente=470 K, T2≈464 K queda dentro de la campana
para varios T1 de prueba (310-350 K) — verificado por Claude y por el solver en
la tarea de diagnóstico (T1_sol=386.52 K, T2=464.07 K).

## Sustancia de trabajo y backends (ACTUALIZADO 2026-09-17, decisión con el usuario)

**Cambio respecto al prompt base:** se probó `pyfluids`/CoolProp 8.0.0 contra la mezcla real
NH3-H2O y **no funciona en este equipo** — CoolProp no tiene el par binario amoníaco-agua
(`AbstractState("HEOS", "Ammonia&Water")` falla con "Could not match the binary pair"); solo lo
cubriría el backend REFPROP, que requiere una DLL licenciada de NIST no disponible. Verificado
empíricamente el 2026-09-17 (ver `TASK_CONTEXT.md` de la tarea `scaffold-y-adapter-propiedades`).

- **Mezcla NH3-H2O: `iapws.ammonia.H2ONH3`** (ya viene con `iapws==1.5.5`, no es una librería
  nueva). Es la ecuación de estado de referencia Tillner-Roth & Friend (1998) / IAPWS G4-01.
  **Reutilizar, no reinventar**, el motor ya validado del proyecto hermano (vault "Ciclo
  Kalina"): `codigo/src/nh3h2o.py` (capa de propiedades sobre `iapws.ammonia`, con dos
  correcciones documentadas y validadas contra las Tablas 6-8 de la guía IAPWS G4-01) +
  `codigo/src/kalina.py` líneas 26-203 (`Tsat_puros`, `flash_TP`, `_mono`, `estado`,
  `estado_de` — la capa de flash T,P,w -> h,s,fase,título y su inversión h/s -> T). Rutas
  absolutas de referencia:
  - `D:\Archivo mental\Archivo mental\04_PROJECTS\active\Ciclo Kalina\codigo\src\nh3h2o.py`
  - `D:\Archivo mental\Archivo mental\04_PROJECTS\active\Ciclo Kalina\codigo\src\kalina.py`
  Convención de ese motor: T en K, P en **MPa** (¡no kPa!), h en kJ/kg, s en kJ/kg·K,
  composición w = fracción **másica** de NH3 (igual que `x` en la interfaz `PropertyBackend`
  de este proyecto) — el motor convierte internamente a fracción molar donde lo necesita.
- **Agua pura** (lado sumidero/fuente si aplica): **IAPWS 1.5.5**, vía `iapws.iapws97`
  (`IAPWSAdapter`, ya implementado en la tarea 1). Sin cambios.
- **`pyfluids` queda retirado del camino real** de la mezcla (no puede resolverla en este
  entorno). El `PyfluidsAdapter` ya escrito se conserva solo como referencia/futuro (si algún
  día hay licencia REFPROP), documentado explícitamente como no funcional para NH3-H2O hoy —
  no debe ser el que use `cycle_solver.py`.
- Patrón adapter obligatorio, sin cambios de fondo: interfaz abstracta `PropertyBackend`
  (`h`, `s`, `T_from_Ph`, `T_from_Ps`, `bubble_point`, `dew_point`, `PropertyRangeError`) con
  implementaciones `AmmoniaWaterAdapter` (mezcla, vía el motor portado) e `IAPWSAdapter` (agua
  pura). El solver del ciclo nunca importa `iapws`/el motor directamente, solo la interfaz.

## Rango de validez del modelo NH3-H2O (Tillner-Roth & Friend 1998) — confirmado 2026-09-23

Fuente: IAPWS G4-01 (2001), §6 "Range of Validity" y §7 "Estimates of Uncertainty"
(https://iapws.org/public/documents/5_L4w/nh3h2o.pdf); artículo base Tillner-Roth & Friend,
J. Phys. Chem. Ref. Data 27, 63 (1998). Aplica a los dos motores del proyecto
(`AmmoniaWaterAdapter` y `TeqpAdapter` implementan el mismo modelo). En esta sección, x es la
fracción **molar** de NH3 (convertir desde la másica del proyecto con `w2m`).

- **Límite inferior**: línea sólido-líquido-vapor (puntos triples), ec. (9) de G4-01:
  - 0 ≤ x ≤ 0.33367: T_tr/273.16 K − 1 = c11·x + c12·x² + c13·x⁷
  - 0.33367 < x ≤ 0.58396: T_tr/193.549 K − 1 = c21·(x − 0.5)²
  - 0.58396 < x ≤ 0.81473: T_tr/194.380 K − 1 = c31·(x − 2/3)² + c32·(x − 2/3)³
  - 0.81473 < x ≤ 1: T_tr/195.495 K − 1 = c41·(1 − x) + c42·(1 − x)⁴
  - c11 = −0.3439823, c12 = −1.3274271, c13 = −274.973, c21 = −4.987368,
    c31 = −4.886151, c32 = 10.37298, c41 = −0.323998, c42 = −15.87560
  - Valores de referencia (x_b másica → T_tr): 0.05 → 267 K, 0.20 → 236 K, 0.35 → 175 K,
    0.55 → 190 K, 0.65 → 194 K, 0.75 → 188 K, 0.95 → 192 K.
- **Límite superior**: el lugar crítico de la mezcla (se obtiene del propio modelo, puede
  dar problemas de convergencia; su ubicación es incierta por datos escasos e inconsistentes).
  Comportamiento clásico, no el teórico, en la vecindad inmediata del punto crítico.
- **Presión**: válido en líquido y vapor hasta **40 MPa** (a temperaturas subcríticas).
- **Respaldo experimental** (solo subcrítico): líquido **< 420 K** y < 40 MPa; vapor
  **< 10 MPa**. Supercrítico: extrapolación "razonable" con **precisión desconocida**.
- **Incertidumbres**: composiciones de equilibrio L-V ±0.01 (fracción molar), hasta ±0.04 cerca
  del lugar crítico; densidad de vapor 1 %, de líquido 2 %; entalpía de exceso **±200 J/mol**
  (≈ 11–12 kJ/kg para las composiciones del ciclo). Mal descrito: el lugar de máximos de
  densidad cerca de la línea de fusión.
- Tc de los puros en el modelo: agua 647.096 K, NH3 405.40 K.

Implicaciones para el proyecto:
- Un `PropertyRangeError` en un estado **dentro** de este rango **no** es un límite del
  modelo: es del envoltorio numérico del backend o de un estado no físico pedido por el
  solver. Así hay que reportarlo.
- Los límites fijos del envoltorio de `TeqpAdapter` (bracket 230–650 K en `_T_de`,
  extrapolación de Psat de NH3 con constante 2500 por encima de 405.3 K) **no** vienen del
  modelo: 230 K recorta el dominio válido para la mayoría de composiciones y 650 K > Tc del
  agua es extrapolación.
- La incertidumbre de ±11 kJ/kg en h afecta sobre todo a los valores **absolutos** de η/Wnet
  (p. ej. al comparar contra literatura). Entre puntos vecinos de un mismo barrido parte del
  error es sistemático y se cancela, pero cuánto se cancela no está cuantificado. Si se
  afirma que una diferencia pequeña es real, hay que decirlo con esa cautela.

## Arquitectura y límites

- Python 3.13.x. Cada archivo `.py` ≤ 200 líneas.
- Estructura de carpetas: ver `Kalina_ksc_11_tercero.md`, sección 7.
- Tests con pytest + pytest-cov, cobertura > 80%, mockeando el adapter de propiedades para no
  depender del backend real en los tests unitarios de componentes/solver.

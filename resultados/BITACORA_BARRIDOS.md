# Bitácora de barridos — Ciclo Kalina KCS-11

Índice de todas las iteraciones guardadas. Datos punto por punto en
`barridos_e_iteraciones_kalina_consolidado.xlsx` (raíz del repo; se regenera con
`python scripts/consolidar_excel_barridos.py`). Cada barrido tiene además su CSV y
su reporte en la carpeta indicada.

## Resumen por barrido

| Barrido | Carpeta / hoja Excel | Variables y rangos | Puntos | KALINA | Resultado clave |
|---|---|---|---|---|---|
| Fase 1 (profesor) | `barridos_2026-09-19/fase1_profesor` (rama `test/fases-sensibilidad`) | `T_fuente=623.15 K`, `P_alta` 2-4 MPa, `x_b` 0.4-0.7 | 40 | 0 | Todo NO_CONVERGIO: fuente demasiado caliente para la campana bifásica. |
| Fase 2 (base libre) | `barridos_2026-09-19/fase2_libre` | `T_fuente=470 K`, OFAT + malla `P_baja × eps_cond` | 269 | 101 | Ancla KALINA η=0.1243; `eps_cond` la variable más influyente. |
| Fase 3 (Húsavík) | `barridos_2026-09-19/fase3_real` | `T_fuente=394.15 K`, OFAT + malla `P_baja × eps_reg` | 192 | 97 | Ancla KALINA η=0.1273 tras corregir el piso de O2 a 10 °C; 10/10 confirmados con motor real. |
| x_b industrial | `2026-09-21_xb_industria` / `0921_xb_industria` | `x_b` 0.78-0.85, `P_alta` 5000-10500 kPa, `P_baja` 400 y 500-1500, `T_fuente=470 K`, `ε` fijos 0.85/0.75/0.80 | 117 | 0 | Mejor η≈0.16 con `P_baja`≈900, pero O1/O2 siempre bloquean. |
| Ventana Elsayed | `2026-09-22_literatura_kcs11` / `0922_literatura_KCS11` | `x_b` {0.55…0.70} × `P_alta` {1000…5000} × `T_fuente` {373, 423, 463} | 60 | 0 | O2 bloquea los 33 puntos que convergen. |
| Cálculo puntual O2 | (sin CSV; nota en el Excel) | Caso base: `P_baja=273.545 kPa`, `x_b=0.55` | 1 | — | Burbuja 287.00 K vs piso 303.55 K: ningún `eps_cond` cierra O2. Umbral: piso ≤ 287.0 K. |
| O2 con clima real | `2026-09-22_o2_tamb_realista` / `0922_O2_Tamb_realista` | Mismos 60 puntos, piso 303.55 K vs 283.15 K | 60 | 0 → 16 | Mejor KALINA η=0.165 (`x_b=0.60`, 5000 kPa, 423 K). 15 siguen en O2 por centésimas. |
| Fuente fría 333 K | `2026-09-22_tfuente_bajo` / `0922_Tfuente_333K` | `T_fuente=333 K`, `P_alta=1500`, `x_b` 0.55-0.75 | 5 | 0 | Ninguno clasificable: huecos del motor `teqp`. |
| Frontera `T_fuente` | `2026-09-22_frontera_tfuente` / `0922_frontera_Tfuente` | `T_fuente` {340, 350, 360} × `x_b` {0.55…0.75}, `P_alta=1500` | 15 | 11 | Con `x_b` alto funciona desde 340 K; η 0.075-0.103, η/η_Carnot 41-48 %. |
| Pinch 6 K realista | `2026-09-23_pinch6_realista` / `0923_pinch6_realista` | Pinch 6 K; `x_b` {0.60…0.80} × `P_alta` {3000, 4000, 5000} × `T_fuente` {394, 423} | 30 | 19 (5 con ε ≤ 0.95) | Ningún ε recortado a 0.999; O2 bloquea 4 (antes 15); η baja ~0.5 pp frente a pinch 4 K. Mejor realista: `x_b=0.60`, 5000 kPa, 423 K, η=0.157. |
| ε fijas 0.85/0.80/0.85 | `2026-09-23_eps_fijos_085` / `0923_eps_fijos_085` | Misma malla que pinch 6 K; ε fijas; `P_baja` subida por punto (burbuja 2 K sobre `T9`, punto fijo máx. 4 pasadas) | 30 | 7 (6 útiles) | `P_baja` +179 kPa y η −2.5 pp de media vs pinch 6 K. 19 CORREGIBLE por O2 a menos de 1.03 K porque el ajuste de `P_baja` no se estabilizó. Mejor: `x_b=0.60`, 5000 kPa, 423 K, η=0.122. |
| Subenfriamiento exacto 2 K | `2026-09-24_margen2k` / `0924_margen2k` | Misma malla y ε fijas; `P_baja` por brentq para margen O2 = 2.0 K | 30 | 22 (21 útiles) | `P_baja` +154 kPa y η −0.98 pp vs barrido anterior. Mejor: `x_b=0.65`, 5000 kPa, 423 K, η=0.1215. 3 huecos de `teqp`; 5 sin llegar a 2 K dentro de +400 kPa. Evaluaciones de sensibilidad en `evaluaciones_margen.csv`. |

## Método de los barridos del 22-09

- Motor `TeqpAdapter` en todos; ninguno verificado aún con `AmmoniaWaterAdapter`.
- `T_sumidero=283 K`, `η_t=η_p=0.80`, `m_b=1 kg/s` (valores de Elsayed et al. 2013).
- `P_baja` = presión de burbuja a `T_sumidero+4 K`; `ε_hrvg`, `ε_reg`, `ε_cond`
  calibrados por punto en un solo paso (pinch de 4 K), recortados a [0.01, 0.999].
- Clasificación con los 17 criterios; ningún punto se oculta.

## Conclusiones

1. El bloqueo principal era el piso de O2 de 30.4 °C, heredado de un clima tropical.
   Con el clima real del sumidero frío aparecen 16 puntos KALINA (igual que en Húsavík).
2. El margen de O2 es de ~4 K por construcción (`P_baja` apunta a `T_sumidero+4 K`);
   por eso 15 puntos fallan por centésimas. Para más margen: pinch mayor o `P_baja` más alta.
3. Fuera de la ventana de la literatura (`P_alta > 5000 kPa`, `T_fuente ≤ 333 K`)
   aparecen huecos del motor `teqp`, no conclusiones sobre el ciclo.
4. Los puntos de mayor η (5000 kPa, 463 K, hasta 0.176) no cumplen O1 (título de turbina).
5. Con más NH₃ el ciclo tolera fuentes más frías (340 K con `x_b` ≥ 0.65; 360 K con 0.55).
6. Las eficiencias de fuente fría son plausibles (η/η_Carnot como el 47 % publicado),
   pero no están confirmadas.

## Verificaciones (2026-09-24, `2026-09-24_verificacion/`)

- **Motor real:** 3 KALINA de `0924_margen2k` (`x_b=0.65`/5000/423, `0.80`/5000/394,
  `0.80`/4000/394) confirmados con `AmmoniaWaterAdapter`: misma clasificación, η
  difiere < 0.02 % relativo, margen O2 2.02-2.03 K (teqp: 2.00 K).
- **Salto del solver en (0.60, 4000, 394):** no son varias raíces del lazo exterior
  (F(T1) tiene una sola raíz). Es la salida de turbina calculada con `teqp`: con el
  mismo estado 3 y `P_baja` distinta en 0.25 kPa, h4 salta 1659 ↔ 1548 kJ/kg y η
  0.034 ↔ 0.080. Ambas ramas pasan los 17 criterios.
- **Rama física (`2026-09-24_rama_turbina/`):** la rama bifásica (η=0.080, h4s≈1486
  kJ/kg) coincide con el motor real (±0.75 kJ/kg, ±0.31 K). La otra es un artefacto:
  el flash de `teqp` devuelve un estado espurio en el punto de burbuja (a 424 kPa,
  273.0 K: s=6.15, h=1626 con fase "líquido"), `s(T)` deja de ser creciente y la
  inversión isentrópica cae en una raíz falsa entre ~419.1 y ~424.1 kPa.
- **Estabilidad ±0.5 kPa de los 22 KALINA:** 21 estables, 1 inestable (0.60/4000/394).
  Ojo: la prueba no detecta un punto que esté entero dentro de una franja espuria.
- **Salida isentrópica de los 22 KALINA vs motor real (`2026-09-24_rama_22/`):** los 22
  están en la rama física. Diferencias teqp−real: h4s −0.71 a −1.58 kJ/kg, T4s −0.11 a
  −0.71 K (offset sistemático teqp↔IAPWS). La rama espuria difiere ~140 kJ/kg y ~9 K.
  El reporte marca 11 como "no físicos" solo porque el umbral de 0.5 K era demasiado
  estricto (fallan por ≤0.21 K); 2 de esos 11 ya estaban confirmados con ciclo real
  completo (η igual al 0.02 %). El punto η=0.009 (0.65/5000/394) es físico: baja
  eficiencia real, no artefacto.

- **Costo de las soluciones (`2026-09-27_costo_soluciones/`):** teqp 30.98 s/punto;
  A ("teqp verificado", recurre al motor real solo en zona de riesgo) 31.85 s/punto
  (+2.8 %) y corrige el caso espurio (η 0.034 → 0.080); B (verificación final) +7 s por
  punto verificado; motor real 312 s/punto. La zona se tocó en 9 de 5404 inversiones.
  **Correcciones de la revisión al reporte:** (1) la tabla de B compara `h4` real de teqp
  contra `h4s` isentrópico del motor real; la comparación correcta (`2026-09-24_rama_22`)
  da 0.7–1.6 kJ/kg, así que B sí discrimina con umbral de 2 kJ/kg (espurio: 139 kJ/kg).
  (2) La afirmación de que los puntos 423.91/424.17 kPa fallan en un proceso limpio
  contradice `2026-09-24_rama_turbina/run_1.log`, donde se resolvieron como primer
  cálculo de un proceso nuevo; queda sin confirmar.

## Protección A+B del motor teqp (2026-09-27, rama `fix/teqp-doble-verificacion`)

Commit `aba754a` de la rama `fix/teqp-doble-verificacion`, traído a
`test/teqp-con-validacion` el 2026-09-27. Resultados en `resultados/2026-09-27_*`.
Hojas `0927_*` del Excel.

- **A (`TeqpVerificado`, `src/properties/teqp_verificado.py`):** consulta al motor real
  solo cuando la T calculada cae a < 1 K de la ebullición del NH3/agua puros con mezcla
  muy rica/pobre. Regresión 22 KALINA: 21 idénticos, 1 cambia en 1.8e-7, ninguno cambia
  de clase, 1 recurrencia. Corrige el espurio (η 0.034 → 0.080).
- **B (`verificar_turbina`, `src/verificacion_motor_real.py`):** una llamada al motor
  real por punto KALINA; umbral 2 kJ/kg en la salida isentrópica de turbina. Detecta el
  espurio (139 kJ/kg).
- **Tiempos reales (23 puntos):** teqp 31.1 s, A 31.7 s (+2 %), B +3.5 s por punto
  verificado. Barrido de 30 con 20 KALINA: teqp 932 s, A+B ~1023 s (+10 %); motor real
  9371 s. Revisar el punto de burbuja en B costaría 8 s por llamada: descartado.
- **Integración:** solo en código (`sensitivity.ejecutar_barrido(..., motor_real=)`
  añade columnas `A_*`/`B_*`). La app NO usa A+B (decisión del usuario: no tocar la
  interfaz). Suite: 131 pasan, 8 fallos previos conocidos.
- **Pendiente conocido (interfaz, no tocado):** en la rama de trabajo el botón
  "Ejecutar simulación" de la app falla (`KeyError: 'T_amb_diseno'`) desde el 22-09,
  porque se trajo el cambio del piso de O2 sin su campo de interfaz.

## Pendiente

- Confirmar 3-5 puntos KALINA con el motor real, sobre todo los que están cerca de un límite.
- Declarar en el paper: cierre por efectividad (sin pinch interno), calibración de un
  solo paso y justificación del piso de O2 = 283.15 K.

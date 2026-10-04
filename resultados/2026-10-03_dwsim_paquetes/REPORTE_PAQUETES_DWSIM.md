# Reporte — Paquetes de propiedades de DWSIM para NH3-H2O y KCS11 (caso Elsayed) en DWSIM

Fecha: 2026-10-03. Ejecutado por Claude directamente (las corridas OpenCode 043–046 se
abortaron o colgaron; la 044 dejó la referencia del motor y la exploración de la API,
`_explora*.py/.txt`, que se reutilizaron).

## La pregunta

1. ¿Qué paquete de propiedades de DWSIM reproduce mejor la mezcla amoníaco-agua?
2. Recreando el KCS11 del caso Elsayed en DWSIM, ¿qué eficiencia da y qué dice eso del
   modelo matemático del proyecto?

## Cómo funciona (en simple)

- **Paquete de propiedades**: la "tabla de vapor" que usa el simulador para la mezcla.
- **BIP** (parámetro de interacción binaria): coeficiente que ajusta un modelo genérico a
  un par concreto de sustancias; sin él el modelo "adivina" cómo se mezclan.
- **Flash**: cálculo que, dados P y T (o P y h), dice cuánto es vapor, cuánto líquido y
  con qué composición.
- **Punto de burbuja / rocío**: presión o temperatura a la que aparece la primera burbuja de
  vapor / la primera gota de líquido.

Se midió cada paquete contra dos referencias: los valores publicados en la guía IAPWS
G4-01 (Tablas 7 y 8) y el motor del proyecto (`AmmoniaWaterAdapter`) en 4 puntos del
caso Elsayed.

## Cómo se hizo

- `scripts/dwsim/sonda_paquetes_dwsim.py`: para cada paquete, puntos de burbuja/rocío por
  bisección sobre flash P-T, composiciones de fase, flash del separador (1500 kPa, 369 K)
  y Δh = h(369 K) − h(300 K) a 1500 kPa (diferencia: el estado de referencia se cancela).
  Mismos ajustes de flash que el ciclo (más iteraciones, tolerancia 1e-8).
- `scripts/dwsim/referencia_motor_ciclo.py` (corrida OpenCode 044): referencia del motor.
- Salidas: `comparacion.csv` (por paquete × magnitud), `resumen_paquetes.csv`,
  `sonda_consola.txt`.

## Resultados — paquetes

28 paquetes; 7 excluidos sin medir (agua pura, agua de mar, petróleo, CAPE-OPEN externo,
incompresibles, GERG-2008). De los 21 medidos:

| Paquete | Error p_sat (rel. medio) | Error composición (abs.) | Error T sat. ciclo | Error Δh | Error fracción de vapor |
|---|---|---|---|---|---|
| **Peng-Robinson (PR)** | **13.8 %** | **0.012** | **1.4 K** | **3.9 %** | **0.029** |
| Peng-Robinson 1978 (PR78) | 13.8 % | 0.012 | 1.4 K | 3.9 % | 0.029 |
| PR / Lee-Kesler | 13.8 % | 0.012 | 1.4 K | 5.1 % | 0.029 |
| PR78 Advanced | 12.3 % | 0.042 | 10.4 K | 26.0 % | 0.119 |
| Chao-Seader | 80.4 % | 0.036 | 5.0 K | 9.5 % | 0.129 |
| Grayson-Streed | 89.2 % | 0.041 | 5.3 K | 10.9 % | 0.138 |
| Lee-Kesler-Plöcker | 44.2 % | 0.180 | 10.5 K | 11.3 % | 0.055 |
| Wilson / Raoult / CoolProp | 77–86 % | 0.07 | 7.4–7.7 K | 23–33 % | 0.18 |
| SRK, SRK Adv., PRSV2-M, PRSV2-VL | 23–402 % | 0.10–0.21 | 10.8–17.5 K | 33–36 % | 0.31 |
| NRTL, UNIQUAC | no calculan: sin BIP para Water/Ammonia | | | | |
| UNIFAC (4 variantes), PC-SAFT | no calculan: error interno de DWSIM | | | | |

**PR / PR78** es el mejor con diferencia: es el único con BIP real del par (kij = −0.2533).
Aun así se desvía ~14 % en presiones de saturación y ~4 % (≈25 kJ/kg) en Δh.

## Resultados — ciclo KCS11 caso Elsayed en DWSIM (PR)

Script `scripts/dwsim/kcs11_elsayed_dwsim.py` → `scripts/dwsim/kcs11_elsayed.dwxmz`.
Todos los equipos cuadran (energía del equipo = cambio de entalpía de sus corrientes,
diferencia 0.000 kW); cierre global 0.005 kW; reciclo convergido; pinch del regenerador 4.00 K.

| Fuente | Propiedades | Cierre de intercambiadores | η |
|---|---|---|---|
| Elsayed et al. (2013) | Ibrahim & Klein | pinch 4 K | 11.38 % |
| Motor del proyecto | Tillner-Roth & Friend (IAPWS G4-01) | efectividad calibrada | 11.05 % |
| DWSIM | Peng-Robinson (kij −0.2533) | pinch 4 K | 12.20 % |

Hallazgo numérico: con los ajustes de fábrica DWSIM falla en la válvula, y con
`NL_FastMode=False` da una **falsa convergencia** en la turbina (40 kW de desbalance sin
error). Se resolvió subiendo iteraciones y apretando tolerancias (detalle en el script).

## Conclusión

- **Qué confirma DWSIM**: la η de DWSIM se calculó con equipos, balances y propiedades
  de DWSIM, no con el motor del proyecto; solo la topología y los datos de entrada son
  comunes. Que una implementación independiente llegue a una η cercana (12.20 % vs
  11.05 %) respalda que **las ecuaciones de balance y la topología del modelo matemático
  son coherentes**.
- **Qué no confirma**: las propiedades. DWSIM no tiene Tillner-Roth & Friend y su mejor
  opción (PR) se desvía de IAPWS G4-01 (14 % en p_sat, 4 % en Δh, 0.03 en fracción de
  vapor). Por eso la diferencia de η entre DWSIM y el motor es esperable y no indica un
  error del motor; la verificación de propiedades del motor sigue siendo la de IAPWS G4-01.
- DWSIM es una tercera comparación entre modelos distintos (igual que Elsayed), no una
  verificación del mismo modelo.

## Lo que no sabemos

- Cuánto de la diferencia de η (1.15 puntos) se debe a las propiedades y cuánto al cierre
  (pinch vs efectividad); separar ambos requiere correr el motor con las mismas T de salida
  que DWSIM, o resolver estado por estado.
- Con PR, la entrada de la bomba (287 K, 273.55 kPa) queda con 4.3 % de vapor molar;
  para el motor es líquido saturado. Es efecto del modelo, no del ciclo.

## Qué sigue

1. Opcional: separar el efecto propiedades vs cierre (ver arriba).
2. Decidir si DWSIM entra como tercera fila de la validación externa
   (`PLANTEAMIENTO_MATEMATICO.md` §7) o queda como análisis aparte.
3. Los `_explora*` de esta carpeta son material de descubrimiento de la API (OpenCode 044);
   se pueden conservar como evidencia o archivar.

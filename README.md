# Ciclo Kalina KSC-11 — análisis energético/exergético (app Streamlit)

Aplicación Python para el análisis energético y exergético (exergía física, sin
exergía química) de un ciclo Kalina KSC-11 con mezcla NH3-H2O como fluido de
trabajo, con sensibilidad paramétrica, gráficas matplotlib y exportación a Excel.

## Estado actual

Existen la **capa de propiedades** (patrón adapter), el tipo compartido
`EstadoTermo` y los **8 componentes** del ciclo, cada uno probado de forma
aislada con un `PropertyBackend` mockeado. El resto son stubs con
`# TODO(tarea futura)`:

| Qué | Estado |
|---|---|
| `src/properties/` — interfaz `PropertyBackend` + adapters | ✅ Implementado y probado |
| `src/state.py` — `EstadoTermo` (punto del ciclo) | ✅ Implementado |
| `src/components/` (8 componentes del ciclo) | ✅ Implementado y probado |
| `src/cycle_solver.py`, `src/exergy.py` | ⏳ Stub |
| `src/sensitivity.py`, `src/export_excel.py`, `src/plots.py` | ⏳ Stub |
| `app.py` (UI Streamlit) | ⏳ Stub |
| `tests/` (solver, exergía, sensibilidad, export) | ⏳ Placeholders vacíos |

### Arquitectura de componentes

Cada componente es una **función pura** `resolver(...)` que consume
`EstadoTermo` de entrada, un `PropertyBackend` (solo la interfaz, nunca un
backend concreto) y sus parámetros propios, y devuelve `EstadoTermo`(s) de
salida más las cantidades de energía relevantes en kW. Su topología sigue el
mapa de estados de `CONTEXT.md`:

| Módulo | Estados | Método |
|---|---|---|
| `src/components/hrvg.py` | 1 → 2 | efectividad `ε_HRVG` |
| `src/components/separador.py` | 2 → 3 + 5 | separador ideal (equilibrio L-V, regla de la palanca) |
| `src/components/turbina.py` | 3 → 4 | eficiencia isentrópica `η_t` |
| `src/components/regenerador.py` | 5 → 6 (y 10 pass-through) | efectividad `ε_reg` |
| `src/components/valvula.py` | 6 → 7 | isoentálpica (`h7 = h6`) |
| `src/components/absorbedor.py` | 4 + 7 → 8 | mezcla adiabática (masa/especie/energía) |
| `src/components/condensador.py` | 8 → 9 | efectividad `ε_cond` |
| `src/components/bomba.py` | 9 → 10 | eficiencia isentrópica `η_p` |

## Estructura

```
app.py                      UI Streamlit (futuro)
src/
  properties/               Capa de propiedades (funcional)
    adapter.py              Interfaz abstracta + PropertyRangeError
    _nh3h2o_engine.py       Motor NH3-H2O portado (IAPWS G4-01, iapws)
    _kalina_flash.py        Flash T,P,w -> h,s,fase,q + inversión h/s -> T
    ammonia_water_adapter.py Mezcla NH3-H2O — CAMINO REAL (motor portado)
    pyfluids_adapter.py     Mezcla NH3-H2O vía pyfluids (SOLO referencia)
    iapws_adapter.py        Agua pura vía IAPWS-IF97 (iapws 1.5.5)
  state.py                  EstadoTermo (punto del ciclo, dataclass)
  components/               HRVG, separador, turbina, regenerador, válvula,
                            absorbedor, condensador, bomba (implementados)
  cycle_solver.py, exergy.py, sensitivity.py, export_excel.py, plots.py (futuro)
tests/
  test_properties.py        Tests de la capa de propiedades (mocks + humo)
  test_ammonia_water_adapter.py  Tests del adapter de la mezcla (round-trips)
  test_components.py        Tests unitarios de los 8 componentes (backend fake)
  test_cycle_solver.py, ... Placeholders (futuro)
requirements.txt
```

Convenciones: Python 3.13.x, archivos `.py` ≤ 200 líneas (excepción: el motor
portado `_nh3h2o_engine.py` es copia literal de un código ya validado), unidades
canónicas de la interfaz de propiedades: P [kPa], T [K], h [kJ/kg],
s [kJ/kg·K], x = fracción másica de NH3 [-]. El resto del código solo consume
`PropertyBackend`, nunca los backends concretos.

## Configuración y ejecución (tests)

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m pytest tests/test_properties.py tests/test_ammonia_water_adapter.py tests/test_components.py -v
```

Cobertura (futuro): `.venv\Scripts\python -m pytest --cov=src --cov-report=term-missing`.

## Camino real de la mezcla NH3-H2O

La mezcla NH3-H2O se resuelve con el **motor portado** del proyecto hermano
(`src/properties/_nh3h2o_engine.py` + `_kalina_flash.py`), que envuelve
`iapws.ammonia.H2ONH3` (ecuación de estado de referencia IAPWS G4-01,
Tillner-Roth & Friend, 1998) con dos correcciones documentadas, y que ya fue
validado contra las Tablas 6-8 de la guía IAPWS G4-01. El solver del ciclo solo
consume la interfaz `PropertyBackend` vía `AmmoniaWaterAdapter`.

`PyfluidsAdapter` (pyfluids/CoolProp) se conserva SOLO como referencia: CoolProp
no incluye el par binario amoníaco-agua en sus backends HEOS/BICUBIC — solo
REFPROP (NIST, con licencia) lo cubriría, y ese backend no está disponible en
este entorno (verificado con pyfluids 4.0.0 / CoolProp 8.0.0). Sus tests de humo
real quedan en `skip` automático mientras el backend no cubra la mezcla.

## Documentación técnica

- `Kalina_ksc_11_tercero.md`: especificación base (ciclo, propiedades, arquitectura).
- `CONTEXT.md`: datos de ingeniería confirmados (estados, fórmulas de efectividad,
  valores por defecto, estado muerto).
- `AGENTS.md`: protocolo de trabajo (director técnico + ejecutor).
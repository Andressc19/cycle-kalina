"""Datos de ejemplo construidos a mano para exportación Excel y gráficas.

Reproducen la FORMA exacta de lo que devuelven ``resolver_ciclo`` y
``calcular_exergia`` (mismas claves, mismos tipos), con valores fijos: los
tests de exportación/gráficas no ejecutan ni el backend real ni el solver
(una corrida real tarda ~8 min). Los h/s de los estados son coherentes con el
backend fake lineal de los tests de componentes (h = T + 10·x + 1e-3·P,
s = 0.01·T + x) y las exergías físicas con T0 = 300 K, P0 = 100 kPa.
"""

from __future__ import annotations

from dataclasses import replace

from src.state import EstadoTermo

# (T, P, h, s, x, m, q, fase, etiqueta) — filas e1..e10.
_FILAS_ESTADOS = [
    (350.0, 3000.0, 358.0, 4.00, 0.5, 1.0, 0.0, "líquido", "1"),
    (400.0, 3000.0, 408.0, 4.50, 0.5, 1.0, 1.0, "bifásico", "2"),
    (400.0, 3000.0, 409.0, 4.60, 0.6, 0.5, 1.0, "vapor", "3"),
    (380.0, 400.0, 386.4, 4.40, 0.6, 0.5, 1.0, "vapor", "4"),
    (410.0, 3000.0, 417.0, 4.50, 0.4, 0.5, 0.0, "líquido", "5"),
    (370.0, 3000.0, 377.0, 4.10, 0.4, 0.5, 0.0, "líquido", "6"),
    (365.0, 400.0, 369.4, 4.05, 0.4, 0.5, 0.0, "bifásico", "7"),
    (374.0, 400.0, 379.4, 4.24, 0.5, 1.0, 1.0, "bifásico", "8"),
    (330.0, 400.0, 335.4, 3.80, 0.5, 1.0, 0.0, "líquido", "9"),
    (340.0, 3000.0, 348.0, 3.90, 0.5, 1.0, 0.0, "líquido", "10"),
]

# Exergía física [kJ/kg] con T0 = 300 K, P0 = 100 kPa (misma x de cada
# corriente): ex = (h − h0) − 300·(s − s0).
_EX_FISICA = {"e1": -97.1, "e2": -197.1, "e3": -197.1, "e4": -159.7,
              "e5": -217.1, "e6": -137.1, "e7": -129.7, "e8": -147.7,
              "e9": -59.7, "e10": -77.1}

# Ed [kW] por componente (T0 = 300 K, luego Sgen = Ed/300) — valores exactos
# elegidos para que la suma (Ed_total) cierre en 6.5 kW exactos.
_ED = dict(hrvg=112.5, separador=15.0, turbina=-30.0, regenerador=-30.0,
           valvula=-7.5, absorbedor=4.5, condensador=-88.0, bomba=30.0)
_SGEN = {k: v / 300.0 for k, v in _ED.items()}

# Parámetros de entrada de la corrida (convención {nombre: (valor, unidad)}).
PARAMETROS_EJEMPLO = {
    "P_alta": (3000.0, "kPa"),
    "P_baja": (400.0, "kPa"),
    "x_NH3 (x_b)": (0.50, "-"),
    "T_fuente": (400.0, "K"),
    "T_sumidero": (300.0, "K"),
    "m_b": (1.0, "kg/s"),
    "eta_turbina": (0.85, "-"),
    "eta_bomba": (0.75, "-"),
    "eps_hrvg": (0.85, "-"),
    "eps_reg": (0.75, "-"),
    "eps_cond": (0.80, "-"),
    "T0 (estado muerto)": (300.0, "K"),
    "P0 (estado muerto)": (100.0, "kPa"),
}

BACKEND_EJEMPLO = "AmmoniaWaterAdapter (fake)"

_EX_QI = 12.5        # 50·(1 − 300/400)  kW
_EX_QOUT = 0.0       # 44·(1 − 300/300)  kW


def resultado_ciclo_ejemplo() -> dict:
    """Resultado de ``resolver_ciclo`` construido a mano (10 estados + energías)."""
    estados = {}
    for i, (T, P, h, s, x, m, q, fase, etiqueta) in enumerate(_FILAS_ESTADOS,
                                                               start=1):
        estados[f"e{i}"] = EstadoTermo(T=T, P=P, h=h, s=s, x=x, m=m, q=q,
                                       fase=fase, etiqueta=etiqueta)
    return dict(estados=estados, Qi=50.0, Qout=44.0, Wt=11.3, Wp=12.6,
                Qreg=35.0, Wnet=-1.3, eta=-0.026)


def resultado_exergia_ejemplo() -> dict:
    """Resultado de ``calcular_exergia`` construido a mano (copias con ex_física)."""
    ciclo = resultado_ciclo_ejemplo()
    ed_total = sum(_ED.values())
    residual = _EX_QI - ciclo["Wnet"] - _EX_QOUT - ed_total
    return dict(
        estados={k: replace(e, exergia_fisica=_EX_FISICA[k])
                 for k, e in ciclo["estados"].items()},
        sgen=dict(_SGEN), ed=dict(_ED), ed_total=ed_total,
        ex_qi=_EX_QI, ex_qout=_EX_QOUT, residual=residual,
        residual_rel=abs(residual) / _EX_QI,
    )
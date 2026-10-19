# -*- coding: utf-8 -*-
"""Sens2 etapa B - densidades y caudales volumetricos de un punto ya resuelto (fila de `evaluar_punto(extra=True)`).

No resuelve el ciclo otra vez: parte de las columnas T_e1..T_e10, m_v, m_l y de las presiones del punto.
- Entrada de turbina (estado 3): vapor saturado a P_alta y T_e3 con la composicion del vapor del flash (P_alta, T_e2).
- Salida de turbina (estado 4): a P_baja y T_e4 con esa misma composicion; si es bifasico, el volumen especifico es q/rho_v + (1-q)/rho_l
  con las fases del flash (P_baja, T_e4) y q = titulo masico del vapor que da `fase_de`.
- Bomba (estados 9 y 10): liquido de composicion x_b; caudal = m_b/rho9 y altura = (P_alta - P_baja)/(rho9*g).
Todo con el modelo teqp (el mismo del resto del analisis). Devuelve un diccionario de magnitudes con unidades en el nombre.
"""
import os
import sys

sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))]

G = 9.80665


def _rho_masica(rho_molar, x_molar):
    from src.properties import _teqp_engine as te
    return rho_molar * te.Mm(x_molar) / 1000.0              # mol/m3 * g/mol -> kg/m3


def densidades(f, backend):
    """`f`: fila con P_alta, P_baja, x_b, m_b (=1), m_v, m_l, T_e1..T_e10; `backend`: TeqpAdapter(x=x_b)."""
    from src.properties import _teqp_engine as te
    pa, pb, xb = float(f["P_alta"]), float(f["P_baja"]), float(f["x_b"])
    m_b, m_v = float(f.get("m_b") or 1.0), float(f["m_v"])
    t2, t3, t4, t9 = (float(f["T_e%d" % i]) for i in (2, 3, 4, 9))
    xl, xv = backend.equilibrio_liquido_vapor(pa, t2)               # fracciones masicas de NH3 en liquido y vapor
    out = {"xv_sep": xv, "xl_sep": xl}
    xvm = te.w2m(xv)
    rho3 = _rho_masica(te.rho_vapor(t3, pa * 1000.0, xvm), xvm)
    fase4, q4 = backend.fase_de(pb, t4, xv)
    if fase4 == "bifasico":
        xl4, xv4 = backend.equilibrio_liquido_vapor(pb, t4)
        rv = _rho_masica(te.rho_vapor(t4, pb * 1000.0, te.w2m(xv4)), te.w2m(xv4))
        rl = _rho_masica(te.rho_liquido(t4, pb * 1000.0, te.w2m(xl4)), te.w2m(xl4))
        v4 = q4 / rv + (1.0 - q4) / rl
        rho4 = 1.0 / v4
    else:
        rho4 = _rho_masica(te.rho_vapor(t4, pb * 1000.0, xvm), xvm)
    xbm = te.w2m(xb)
    rho9 = _rho_masica(te.rho_liquido(t9, pb * 1000.0, xbm), xbm)
    out.update(fase4=fase4, q4_dens=q4, rho3=rho3, rho4=rho4, rho9=rho9, V3_m3s=m_v / rho3, V4_m3s=m_v / rho4,
               V9_m3s=m_b / rho9, H_bomba_m=(pa - pb) * 1000.0 / (rho9 * G), RV_turb=rho3 / rho4)
    return out

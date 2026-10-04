"""Sonda de depuración del regenerador (DWSIM): ¿qué modo impone T6 y produce T1?

Compara, sobre la base compartida `_kcs11_dwsim_base`, tres modos del HX con las
especificaciones del pinch de la plantilla (T6 = 303.83 K, MITA = 4 K):
  A) CalcTempHotOut + HotSideOutletTemperature   (el que usa el script de_union)
  B) PinchPoint + MITA                           (el que usa kcs11_elsayed_dwsim.py)
  C) HeatAdded + DeltaQ                          (equivalente a B en potencia)
Para cada uno imprime T1..T10, x3, x5, m5, Wt/Wp/Qi/Qout, eta y el cierre.

Uso:  python -u resultados/2026-10-03_validacion_dwsim/_dbg_regen.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "dwsim"))
import _kcs11_dwsim_base as B          # noqa: E402

P_ALTA, P_BAJA, T_FUENTE, T_SUM, X_B, M_B = 1500.0, 273.5454214157179, 373.0, 283.0, 0.55, 1.0
T6_SP, MITA = 303.83, 4.0
RT = B.runtime()
System = RT["System"]


def modo(R, nombre):
    return System.Enum.Parse(R.CalculationMode.GetType(), nombre)


def _props_hx(d):
    R = d["eq"]["reg"]
    return [p for p in dir(R) if not p.startswith("_") and
            any(k in p for k in ("K", "Temp", "Approach", "Mode", "Duty",
                                 "Delta", "Eff", "Calc"))]


def corre(nombre_modo, fijar, T9=287.0, T5=369.0, x5=0.41, m5=0.75):
    d = B.diagrama(P_ALTA, P_BAJA, X_B, M_B, 0.80, 0.80)
    d["eq"]["hrvg"].CalcMode = System.Enum.Parse(
        d["eq"]["hrvg"].CalcMode.GetType(), "OutletTemperature")
    d["eq"]["hrvg"].OutletTemperature = 369.0
    d["eq"]["hrvg"].DeltaP = 0.0
    d["eq"]["cond"].CalcMode = System.Enum.Parse(
        d["eq"]["cond"].CalcMode.GetType(), "OutletTemperature")
    d["eq"]["cond"].OutletTemperature = T9
    d["eq"]["cond"].DeltaP = 0.0
    d["eq"]["reg"].CalculationMode = modo(d["eq"]["reg"], nombre_modo)
    fijar(d["eq"]["reg"])
    B.fijar(d, "S9", T9, P_BAJA, X_B, M_B)
    B.fijar(d, "S5", T5, P_ALTA, x5, m5)
    errs = B.resolver(d)
    st = [B.props(d, k) for k in ("S1", "S5", "S6", "S9c", "S10")]
    S1, S5, S6, S9c, S10 = st
    m3, h3, h4 = B.props(d, "S3")["m"], B.props(d, "S3")["h"], B.props(d, "S4")["h"]
    Wt, Wp = m3 * (h3 - h4), M_B * (h10_h(S10) - S9c["h"])
    Qi, Qo = M_B * (B.props(d, "S2")["h"] - S1["h"]), M_B * (S9c["h"] * 0 + B.props(d, "S8")["h"] - S9c["h"])
    print("modo %-14s errs=%s" % (nombre_modo, [str(e).splitlines()[0][:60] for e in errs] or "ninguno"))
    print("   T1=%9.3f T5=%9.3f T6=%9.3f T9c=%9.3f T10=%9.3f  x5=%.4f m5=%.4f"
          % (S1["T"], S5["T"], S6["T"], S9c["T"], S10["T"], S5["w"], S5["m"]))
    print("   Wt=%8.3f Wp=%7.4f Qi=%8.3f Qout=%8.3f eta=%.6f (%0.3f %%) cierre=%+.4f"
          % (Wt, Wp, Qi, Qo, (Wt - Wp) / Qi, 100 * (Wt - Wp) / Qi, Qi + Wp - Qo - Wt))
    print("   balance frio m_b*(h1-h10)=%.4f  m5*(h5-h6)=%.4f  (deben ser iguales)"
          % (M_B * (S1["h"] - S10["h"]), S5["m"] * (S5["h"] - S6["h"])))
    return d


def h10_h(S10):
    return S10["h"]


if __name__ == "__main__":
    d = B.diagrama(P_ALTA, P_BAJA, X_B, M_B, 0.8, 0.8)
    print("props HX:", sorted(_props_hx(d)))
    print("TODAS props HX:", sorted(p for p in dir(d["eq"]["reg"])
                                   if not p.startswith("_") and
                                   not p.startswith(("get_", "set_"))))
    R = d["eq"]["reg"]
    print("valores:", [(p, getattr(R, p)) for p in
                       ("MITA", "K", "UA", "TOL1", "ApproachTemp",
                        "ColdSideOutletTemperature", "HotSideOutletTemperature",
                        "ThermalEfficiency", "DeltaP", "DefinedTemperature")
                       if hasattr(R, p)])
    print("modos HX:", [str(x) for x in System.Enum.GetNames(
        d["eq"]["reg"].CalculationMode.GetType())])
    print("modos Heater:", [str(x) for x in System.Enum.GetNames(
        d["eq"]["hrvg"].CalcMode.GetType())])
    print()
    corre("PinchPoint", lambda R: setattr(R, "MITA", MITA))
    print()
    corre("CalcTempHotOut", lambda R: setattr(R, "HotSideOutletTemperature", T6_SP))
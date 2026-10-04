"""Sonda 2: (a) modo `ThermalEfficiency` del HX y (b) duty `HeatAdded`/`HeatRemoved`
del HRVG y del condensador, en kPa/Pa y %, igual que la plantilla.

Compara el eps que DWSIM impone con el del proyecto:
    eps_proyecto = (h5 - h6) / (h5 - h(P_alta, T10, x5))     [src/components/regenerador.py]
    eps_xb       = (h5 - h6) / (h5 - h(P_alta, T10, x_b))    [con x del lado frio]

Uso:  python -u resultados/2026-10-03_validacion_dwsim/_dbg_eps.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "dwsim"))
import _kcs11_dwsim_base as B          # noqa: E402

PA, PB, TF, TS, XB, MB = 1500.0, 273.5454214157179, 373.0, 283.0, 0.55, 1.0
EPS = (0.8882023116022899, 0.9380325550010874, 0.9625029043677631)
RT = B.runtime()
System = RT["System"]


def em(obj, nombre):
    return System.Enum.Parse(obj.CalcMode.GetType(), nombre)


def em_hx(R, nombre):
    return System.Enum.Parse(R.CalculationMode.GetType(), nombre)


def arma(modo_reg, fija_reg, q_hrvg=None, q_cond=None, T9=287.0):
    d = B.diagrama(PA, PB, XB, MB, 0.80, 0.80)
    H, C, R = d["eq"]["hrvg"], d["eq"]["cond"], d["eq"]["reg"]
    if q_hrvg is None:                       # si no, HRVG por temperatura
        H.CalcMode, H.OutletTemperature = em(H, "OutletTemperature"), 369.0
    else:
        H.CalcMode, H.DeltaQ = em(H, "HeatAdded"), q_hrvg
    H.DeltaP = 0.0
    if q_cond is None:
        C.CalcMode, C.OutletTemperature = em(C, "OutletTemperature"), T9
    else:
        C.CalcMode, C.DeltaQ = em(C, "HeatRemoved"), q_cond
    C.DeltaP = 0.0
    R.CalculationMode = em_hx(R, modo_reg)
    fija_reg(R)
    B.fijar(d, "S9", T9, PB, XB, MB)
    B.fijar(d, "S5", 369.0, PA, 0.41, 0.75)
    errs = B.resolver(d)
    return d, errs


def informa(et, d, errs):
    S1, S2, S5 = (B.props(d, k) for k in ("S1", "S2", "S5"))
    S6, S8, S9c, S10 = (B.props(d, k) for k in ("S6", "S8", "S9c", "S10"))
    S3, S4 = B.props(d, "S3"), B.props(d, "S4")
    Wt, Wp = S3["m"] * (S3["h"] - S4["h"]), MB * (S10["h"] - S9c["h"])
    Qi, Qo = MB * (S2["h"] - S1["h"]), MB * (S8["h"] - S9c["h"])
    h6min5 = B.h_PT(d, PA, S10["T"], S5["w"])
    h6minb = B.h_PT(d, PA, S10["T"], XB)
    print("%s  errs=%s" % (et, [str(e).splitlines()[0][:60] for e in errs] or "ninguno"))
    print("   T1=%9.3f T2=%9.3f T5=%9.3f T6=%9.3f T9c=%9.3f T10=%9.3f x5=%.4f m5=%.4f"
          % (S1["T"], S2["T"], S5["T"], S6["T"], S9c["T"], S10["T"], S5["w"], S5["m"]))
    print("   Wt=%8.3f Wp=%7.4f Qi=%8.3f Qout=%8.3f eta=%.6f (%0.3f %%) cierre=%+.4f"
          % (Wt, Wp, Qi, Qo, (Wt - Wp) / Qi, 100 * (Wt - Wp) / Qi, Qi + Wp - Qo - Wt))
    print("   eps_proyecto=%.6f  eps_xb=%.6f  (pedido %.6f)"
          % ((S5["h"] - S6["h"]) / (S5["h"] - h6min5),
             (S5["h"] - S6["h"]) / (S5["h"] - h6minb), EPS[1]))
    print("   eps_hrvg_real=%.6f (pedido %.6f)  eps_cond_real=%.6f (pedido %.6f)"
          % ((S2["h"] - S1["h"]) / (S2["h"] - B.h_PT(d, PA, TF, XB)),
             (S8["h"] - S9c["h"]) / (S8["h"] - B.h_PT(d, PB, TS, XB)), EPS[0], EPS[2]))


if __name__ == "__main__":
    d, e = arma("PinchPoint", lambda R: setattr(R, "MITA", 4.0))
    informa("[A] PinchPoint MITA=4 (control = plantilla)", d, e)
    d, e = arma("ThermalEfficiency",
                lambda R: setattr(R, "ThermalEfficiency", EPS[1]))
    informa("[B] ThermalEfficiency eps_reg (HRVG/cond por T)", d, e)
    d, e = arma("PinchPoint", lambda R: setattr(R, "MITA", 4.0),
                q_hrvg=452.458, q_cond=397.240)
    informa("[C] PinchPoint + HeatAdded/HeatRemoved en kW", d, e)
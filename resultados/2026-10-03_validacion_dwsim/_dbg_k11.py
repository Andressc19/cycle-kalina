"""Diagnostico: que equipo no calcula en la primera vuelta de KALINA-11 (DWSIM-PR)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dwsim"))
import _kcs11_dwsim_base as B
import kcs11_efectividad_dwsim as K
et = sys.argv[1] if len(sys.argv) > 1 else "KALINA-11"
p = [q for q in B.PUNTOS if q[0] == et][0]
_, x_b, Pa, Tf, Pb, Ts, eps = p
a, _ = K._arranque(et)
print("arranque", a)
d = B.diagrama(Pa, Pb, x_b, 1.0, 0.8, 0.8)
sysm = B.runtime()["System"]
for k in ("hrvg", "cond"):
    o = d["eq"][k]; o.CalcMode = sysm.Enum.Parse(o.CalcMode.GetType(), "OutletTemperature")
d["eq"]["hrvg"].OutletTemperature, d["eq"]["cond"].OutletTemperature = a["T2"], a["T9"]
d["eq"]["reg"].MITA = a["T6"] - a["T10"]
B.fijar(d, "S9", a["T9"], Pb, x_b, 1.0); B.fijar(d, "S5", a["T5"], Pa, a["x5"], a["m5"])
print("errores:", B.resolver(d))
for n, o in d["eq"].items():
    print("%-6s calc=%s err=%r" % (n, o.Calculated, (o.ErrorMessage or "")[:160]))
r = d["rec"].GetAsObject(); print("recycle calc=%s conv=%s" % (r.Calculated, r.Converged))
for k in ("S9", "S10", "S1", "S2", "S3", "S4", "S5calc", "S5", "S6", "S7", "S8", "S9c"):
    q = B.props(d, k); print("%-6s T=%8.2f P=%8.1f m=%.4f w=%.4f h=%10.2f vf=%.3f" % (k, q["T"], q["P"], q["m"], q["w"], q["h"], q["vf"]))

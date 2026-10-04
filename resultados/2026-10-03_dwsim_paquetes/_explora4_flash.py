"""Exploracion 4b: FlashCalculationType + IFlashCalculationResult + BIP real."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora4_flash.txt"), "w", encoding="utf-8")


def w(*a):
    s = " ".join(str(v) for v in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


D = r"D:\DWSIM"
os.chdir(D)
from pythonnet import load

load("netfx")
import clr

sys.path.append(D)
os.environ["PATH"] = D + os.pathsep + os.environ["PATH"]
for dll in ("DWSIM.Interfaces", "DWSIM.GlobalSettings", "DWSIM.SharedClasses",
            "DWSIM.Thermodynamics", "DWSIM.UnitOperations", "DWSIM.Automation"):
    clr.AddReference(os.path.join(D, dll + ".dll"))
from DWSIM.Automation import Automation3
from DWSIM.Interfaces.Enums import FlashCalculationType

w("nombres FlashCalculationType:", list(FlashCalculationType.GetNames(FlashCalculationType)))

mgr = Automation3()
M_A, M_W = 17.03052, 18.015268


def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))


def probar(pname, wNH3):
    f2 = mgr.CreateFlowsheet()
    f2.AddCompound("Water")
    f2.AddCompound("Ammonia")
    p2 = f2.CreateAndAddPropertyPackage(pname)
    xm = xmol(wNH3)
    comp = [1 - xm, xm]
    out = {}
    for tag, (ct, v1, v2) in {
        "PT(1500kPa,369K)": (FlashCalculationType.PressureTemperature, 1500e3, 369.0),
        "TVF(T=300,VF=0) burbuja": (FlashCalculationType.TemperatureVaporFraction, 300.0, 0.0),
        "TVF(T=300,VF=1) rocio": (FlashCalculationType.TemperatureVaporFraction, 300.0, 1.0),
        "PVF(P=1500kPa,VF=0) Tbub": (FlashCalculationType.PressureVaporFraction, 1500e3, 0.0),
        "PVF(P=1500kPa,VF=1) Tdew": (FlashCalculationType.PressureVaporFraction, 1500e3, 1.0),
    }.items():
        try:
            r = p2.CalculateEquilibrium(ct, v1, v2, [float(c) for c in comp], [0.0, 0.0], 1.0)
            vals = {}
            for m in ("Temperature", "Pressure", "VaporFraction", "PhaseFractions",
                      "LiquidMolarComposition", "VaporMolarComposition",
                      "OverallMolarComposition", "MassFractions"):
                if hasattr(r, m):
                    v = getattr(r, m)
                    try:
                        vals[m] = [float(z) for z in v] if not isinstance(v, (int, float)) else float(v)
                    except Exception:
                        vals[m] = str(v)
            out[tag] = vals
        except Exception as e:
            out[tag] = f"EXCEPCION {type(e).__name__}: {e}"
    return out, p2


for pname in ("Peng-Robinson (PR)", "NRTL", "Modified UNIFAC (NIST)", "Raoult's Law"):
    res, p2 = probar(pname, 0.55)
    w(f"\n===== {pname} =====")
    for tag, vals in res.items():
        w(f"  {tag}: {vals}")

w("\n===== miembros de IFlashCalculationResult =====")
f2 = mgr.CreateFlowsheet()
f2.AddCompound("Water")
f2.AddCompound("Ammonia")
p2 = f2.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
r = p2.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, 369.0,
                            [1 - xmol(0.55), xmol(0.55)], [0.0, 0.0], 1.0)
w([m for m in dir(r) if not m.startswith("_")])

w("\n===== BIP: tipo concreto y miembros =====")
for pname in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "NRTL",
              "Modified UNIFAC (NIST)", "UNIQUAC", "Raoult's Law", "CoolProp"):
    f3 = mgr.CreateFlowsheet()
    f3.AddCompound("Water")
    f3.AddCompound("Ammonia")
    p3 = f3.CreateAndAddPropertyPackage(pname)
    try:
        tn = p3.GetType().FullName
    except Exception as e:
        tn = f"err {e}"
    ip = [m for m in dir(p3) if any(k in m.lower() for k in
                                     ("interaction", "bip", "kos", "a_ij", "aip"))]
    w(f"\n-- {pname}: tipo={tn}")
    w(f"   miembros BIP: {ip}")
LOG.close()
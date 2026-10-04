"""Exploracion 3: firma de CalculateEquilibrium, composicion global y BIP.

Escribe _explora3_flash.txt junto al script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora3_flash.txt"), "w", encoding="utf-8")


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
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType

mgr = Automation3()
fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.AddCompound("Ammonia")
pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
w("paquete:", pp.Name)
w("ReturnInstance tipo:", type(pp.ReturnInstance))
ri = [m for m in dir(pp.ReturnInstance) if any(
    k in m.lower() for k in ("interaction", "bip", "unifac", "unequac", "nrtl", "uniquac"))]
w("ReturnInstance miembros BIP:", ri)

w("\nCalculateEquilibrium doc:", pp.CalculateEquilibrium.__doc__)
w("CalculateEquilibrium2 doc:", pp.CalculateEquilibrium2.__doc__)

s1 = fs.AddObject(ObjectType.MaterialStream, 100, 100, "S1")
so = s1.GetAsObject()
w("\nSetOverallMassComposition doc:", so.SetOverallMassComposition.__doc__)
w("SetOverallMoleComposition doc:", so.SetOverallMoleComposition.__doc__)
w("SetFlashSpec doc:", so.SetFlashSpec.__doc__)
w("SpecType:", [x for x in dir(type(so).SpecType) if not x.startswith("_")][:40])
w("CalcOverallCompMoleFractions doc:", so.CalcOverallCompMoleFractions.__doc__)

w("\n== fases: nº y tipo ==")
w("GetNumPhases:", so.GetNumPhases())
ph = so.Phases[0]
w("tipo fase:", type(ph))
w("miembros fase:", [m for m in dir(ph) if not m.startswith("_")])
w("\npropiedades fase[0] miembros:", [m for m in dir(ph.Properties) if not m.startswith("_")])

# --- prueba de flash PR con w=0.55 NH3 a 1500 kPa, 369 K ---
w("\n== prueba: composicion global 0.55 masica NH3, P=1500 kPa, T=369 K ==")
M = {"Water": 18.015268, "Ammonia": 17.03052}
w_NH3 = 0.55
w_H2O = 1 - w_NH3
try:
    so.SetOverallMassComposition([w_H2O, w_NH3])
    w("mole fractions leidas:", [float(v) for v in so.CalcOverallCompMoleFractions()])
except Exception as e:
    w("SetOverallMassComposition fallo:", type(e).__name__, e)

so.PropertyPackage = pp
for i, p in enumerate(so.Phases):
    p.Properties.temperature = 369.0
    p.Properties.pressure = 1500e3
    p.Properties.massflow = 1.0

w("\n-- via CalculateEquilibrium --")
xo = [w_H2O, w_NH3]
res = pp.CalculateEquilibrium(1500e3, 369.0, [float(v) for v in xo], 0)
w("resultado:", [float(v) for v in res])

w("\n-- via stream.CalcEquilibrium / Calculate --")
try:
    so.CalcEquilibrium()
    w("AtEquilibrium:", so.AtEquilibrium, "ErrorMessage:", so.ErrorMessage)
    for i, p in enumerate(so.Phases):
        q = p.Properties
        w(f"fase {i}: fase='{q.phase}' T={float(q.temperature):.3f} P={float(q.pressure):.1f} "
          f"w={float(q.massflow):.6g} frac={float(getattr(q,'fraction',0) if hasattr(q,'fraction') else 0):.6g}")
        w("        molarfraction:", [float(v) for v in q.molarfraction])
        w("        massfraction :", [float(v) for v in q.massfraction])
except Exception as e:
    w("CalcEquilibrium fallo:", type(e).__name__, e)
LOG.close()
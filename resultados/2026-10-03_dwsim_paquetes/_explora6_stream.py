"""Exploracion 6: orden correcto AddCompound -> stream -> paquete -> composicion."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora6_stream.txt"), "w", encoding="utf-8")


def w(*a):
    s = " ".join(str(v) for v in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def sec(t):
    w("\n===== " + t + " =====")


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
from DWSIM.Interfaces.Enums import FlashCalculationType
import System

M_A, M_W = 17.03052, 18.015268
mgr = Automation3()


def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))


sec("orden: comp -> stream -> paquete -> composicion")
fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.AddCompound("Ammonia")
so = fs.AddObject(ObjectType.MaterialStream, 100, 100, "S1").GetAsObject()
w("n comps antes de paquete:", so.GetNumCompounds())
pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
w("nombre del paquete:", repr(pp.Name), "| UniqueID:", repr(pp.UniqueID))
w("n comps tras crear paquete (stream aun sin paquete):", so.GetNumCompounds())
so.PropertyPackage = pp
w("n comps tras asignar paquete:", so.GetNumCompounds())
w("ComponentIds:", [str(i) for i in so.ComponentIds])
w("ComponentName:", [str(i) for i in so.ComponentName])

sec("SetOverallMassComposition con System.Double[]")
try:
    arr = System.Array[System.Double]([0.45, 0.55])
    so.SetOverallMassComposition(arr)
    w("OK -> molefrac global:", [float(v) for v in so.CalcOverallCompMoleFractions()])
except Exception as e:
    w("EXCEPCION", type(e).__name__, str(e)[:200])

sec("Phase.Properties.massfraction / molarfraction")
q = so.Phases[0].Properties
w("q:", type(q))
for attr in ("massfraction", "molarfraction", "massflow", "temperature", "pressure"):
    try:
        w(f"  {attr} =", getattr(q, attr))
    except Exception as e:
        w(f"  {attr} -> {type(e).__name__}: {str(e)[:100]}")

sec("rutas de composicion: SetOverallCompoundMolarFlow / SetOverallCompoundMassFlow")
for m in ("SetOverallCompoundMolarFlow", "SetOverallCompoundMassFlow",
          "SetOverallComposition", "SetPhaseComposition", "SetOverallMassComposition",
          "NormalizeOverallMassComposition", "MassFractionsToMoleFractions",
          "MoleFractionsToMassFractions"):
    try:
        w(f"  {m}: {getattr(type(so), m).__doc__}")
    except Exception as e:
        w(f"  {m}: <no doc> {e}")

sec("flujo completo PR: PVF para T_burbuja y T_rocio")
comp = [float(1 - xmol(0.55)), float(xmol(0.55))]
w("composicion molar:", comp)
for tag, ct, v1, v2 in (
        ("PT 1500kPa/369K", FlashCalculationType.PressureTemperature, 1500e3, 369.0),
        ("TVF T=300 VF=0 (burbuja)", FlashCalculationType.TemperatureVaporFraction, 300.0, 0.0),
        ("TVF T=300 VF=1 (rocio)", FlashCalculationType.TemperatureVaporFraction, 300.0, 1.0),
        ("PVF P=1500kPa VF=0 (Tbub)", FlashCalculationType.PressureVaporFraction, 1500e3, 0.0),
        ("PVF P=1500kPa VF=1 (Tdew)", FlashCalculationType.PressureVaporFraction, 1500e3, 1.0)):
    try:
        pp.CurrentMaterialStream = so
        r = pp.CalculateEquilibrium(ct, v1, v2, [c for c in comp], [0.0, 0.0], 1.0)
        w(f"\n  [{tag}] tipo={type(r)}")
        w("    miembros:", [m for m in dir(r) if not m.startswith("_")])
        w("    ToString:", str(r))
        for m in ("Success", "ErrorMessage", "Temperature", "Pressure", "VaporFraction",
                  "PhaseFractions", "LiquidMolarComposition", "VaporMolarComposition",
                  "OverallMolarComposition"):
            if hasattr(r, m):
                v = getattr(r, m)
                try:
                    w(f"      {m} =", [float(z) for z in v] if not isinstance(v, (int, float, str)) else v)
                except Exception:
                    w(f"      {m} = {v}")
    except Exception as e:
        w(f"\n  [{tag}] EXCEPCION {type(e).__name__}: {str(e)[:220]}")
LOG.close()
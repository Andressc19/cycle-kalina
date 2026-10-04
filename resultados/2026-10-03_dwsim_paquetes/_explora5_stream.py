"""Exploracion 5: CurrentMaterialStream + SetFlashSpec + SpecType + BIP."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora5_stream.txt"), "w", encoding="utf-8")


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
from DWSIM.Interfaces.Enums import FlashCalculationType

M_A, M_W = 17.03052, 18.015268
mgr = Automation3()


def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))


fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.AddCompound("Ammonia")
so = fs.AddObject(ObjectType.MaterialStream, 100, 100, "S1").GetAsObject()
w("SetFlashSpec doc:", so.SetFlashSpec.__doc__)
w("SpecType nombre:", so.SpecType)
w("SpecType valores:", [x for x in dir(type(so).SpecType) if not x.startswith("_")])
w("GetFlashSpec doc:", so.GetFlashSpec.__doc__)
w("molarfraction doc:", so.Phases[0].Properties.molarfraction.__doc__)

pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
so.SetOverallMassComposition([1 - 0.55, 0.55])
w("\nmolefrac global tras SetOverallMassComposition:",
  [float(v) for v in so.CalcOverallCompMoleFractions()])
w("masa molar leida:", float(so.GetOverallMolecularWeight()))

so.PropertyPackage = pp
so.Phases[0].Properties.temperature = 369.0
so.Phases[0].Properties.pressure = 1500e3
so.Phases[0].Properties.massflow = 1.0

w("\n-- ruta A: pp.CurrentMaterialStream = so, luego CalculateEquilibrium --")
try:
    pp.CurrentMaterialStream = so
    comp = [1 - xmol(0.55), xmol(0.55)]
    r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, 369.0,
                                [float(c) for c in comp], [0.0, 0.0], 1.0)
    w("  OK. miembros:", [m for m in dir(r) if not m.startswith("_")])
    w("  ToString:", str(r))
    for m in ("Temperature", "Pressure", "VaporFraction", "PhaseFractions",
              "LiquidMolarComposition", "VaporMolarComposition",
              "OverallMolarComposition", "MassFractions", "Success", "ErrorMessage"):
        if hasattr(r, m):
            v = getattr(r, m)
            try:
                w(f"   {m} =", [float(z) for z in v] if not isinstance(v, (int, float, str)) else v)
            except Exception as e:
                w(f"   {m} = {v} (no iterable)")
except Exception as e:
    w("  EXCEPCION", type(e).__name__, str(e)[:300])

w("\n-- ruta B: SetFlashSpec + CalcEquilibrium --")
try:
    so.SetFlashSpec(0, 1500e3, 1, 369.0)
    w("  SpecType tras SetFlashSpec:", so.SpecType, " SpecVar:", so.SpecVar, so.SpecVar2)
except Exception as e:
    w("  SetFlashSpec EXCEPCION", type(e).__name__, str(e)[:300])

try:
    so.CalcEquilibrium()
    w("  AtEquilibrium:", so.AtEquilibrium)
    w("  ErrorMessage:", so.ErrorMessage)
    w("  NumFases:", so.GetNumPhases())
    for i, ph in enumerate(so.Phases):
        q = ph.Properties
        w(f"   fase {i}: T={float(q.temperature):.4f} P={float(q.pressure):.1f} "
          f"w={float(q.massflow):.8g} VF={float(q.phasefraction):.8g}")
        w("     molarfraction:", [float(v) for v in q.molarfraction])
except Exception as e:
    w("  CalcEquilibrium EXCEPCION", type(e).__name__, str(e)[:400])

w("\n-- propiedades de fase: nombres --")
w([m for m in dir(so.Phases[0].Properties) if not m.startswith("_")])

w("\n-- BIP: reflexion del paquete con stream asignado --")
for pname in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "PRSV2-VL",
              "NRTL", "Modified UNIFAC (NIST)", "Modified UNIFAC (Dortmund)",
              "UNIQUAC", "UNIFAC", "UNIFAC-LL", "Raoult's Law", "CoolProp",
              "Chao-Seader", "Grayson-Streed", "Wilson", "Lee-Kesler-Plucker",
              "PC-SAFT (with Association Support) (.NET Code)", "GERG-2008",
              "Steam Tables (IAPWS-IF97)", "Seawater IAPWS-08"):
    f3 = mgr.CreateFlowsheet()
    f3.AddCompound("Water")
    f3.AddCompound("Ammonia")
    s3 = f3.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    s3.SetOverallMassComposition([0.45, 0.55])
    s3.Phases[0].Properties.temperature = 369.0
    s3.Phases[0].Properties.pressure = 1500e3
    s3.Phases[0].Properties.massflow = 1.0
    try:
        p3 = f3.CreateAndAddPropertyPackage(pname)
        p3.CurrentMaterialStream = s3
        s3.PropertyPackage = p3
        tn = p3.GetType().FullName
        ipm = [m for m in dir(p3) if any(k in m.lower() for k in
                                          ("interaction", "bip", "kos", "unifac", "unequac"))]
        w(f"\n-- {pname}\n   tipo={tn}\n   miembros BIP/grupo={ipm}")
        for m in ipm:
            try:
                v = getattr(p3, m)
                if hasattr(v, "GetLength"):
                    w(f"     {m}: rank={v.Rank} long={v.GetLength(0)}x"
                      f"{v.GetLength(1) if v.Rank > 1 else 1}"
                      f"{'x' + str(v.GetLength(2)) if v.Rank > 2 else ''}")
                else:
                    w(f"     {m}: {v}")
            except Exception as e:
                w(f"     {m}: <{type(e).__name__}>")
    except Exception as e:
        w(f"\n-- {pname}: EXCEPCION {type(e).__name__}: {str(e)[:200]}")
LOG.close()
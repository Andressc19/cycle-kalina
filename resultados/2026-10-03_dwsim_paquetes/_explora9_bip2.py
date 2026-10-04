"""Exploracion 9: donde viven los BIP (jerarquia de tipos + XML) y VF casi-extremos."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora9_bip2.txt"), "w", encoding="utf-8")


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
from System.Reflection import BindingFlags

M_A, M_W = 17.03052, 18.015268
mgr = Automation3()
KF = [0.1, 5.0]


def nuevo(pname):
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water")
    fs.AddCompound("Ammonia")
    so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 1.0)
    so.SetOverallCompoundMassFlow("Ammonia", 1.0)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(pname)
    so.PropertyPackage = pp
    pp.CurrentMaterialStream = so
    return fs, so, pp


sec("A) jerarquia de tipos del paquete PR y todos los campos (no publicos incluidos)")
fs, so, pp = nuevo("Peng-Robinson (PR)")
t = pp.GetType()
niv = 0
while t is not None:
    w(f"\n-- nivel {niv}: {t.FullName}")
    for f in t.GetFields(BindingFlags.Instance | BindingFlags.Public |
                         BindingFlags.NonPublic | BindingFlags.Static |
                         BindingFlags.FlattenHierarchy):
        w(f"     campo  {f.Name} : {f.FieldType.Name}")
    for p in t.GetProperties(BindingFlags.Instance | BindingFlags.Public |
                             BindingFlags.NonPublic | BindingFlags.FlattenHierarchy):
        if any(k in p.Name.lower() for k in ("inter", "bip", "kos", "param")):
            w(f"     prop   {p.Name} : {p.PropertyType.Name}")
    t = t.BaseType
    niv += 1

sec("B) ParametersXMLString (contenido truncado) por paquete")
for pname in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "NRTL", "UNIQUAC",
              "Modified UNIFAC (NIST)", "Raoult's Law", "UNIFAC", "Chao-Seader",
              "CoolProp", "Steam Tables (IAPWS-IF97)"):
    try:
        f2, s2, p2 = nuevo(pname)
        v = p2.ParametersXMLString
        txt = str(v)
        w(f"\n-- {pname}: tipo={type(v)} len={len(txt)}")
        w("   " + txt[:1200].replace("\n", "\n   "))
    except Exception as e:
        w(f"\n-- {pname}: EXC {type(e).__name__}: {str(e)[:150]}")

sec("C) VF casi extremos para obtener ambas composiciones (PR, T=300, x_NH3=0.2)")
comp = [0.8, 0.2]
for vf in (0.0, 1e-9, 1e-6, 1.0 - 1e-6, 1.0 - 1e-9, 1.0):
    try:
        r = pp.CalculateEquilibrium(FlashCalculationType.TemperatureVaporFraction, 300.0, vf,
                                    [float(c) for c in comp], list(KF), 1.0)
        w(f"   VF={vf:.9g} -> P={float(r.CalculatedPressure)/1e6:.8f} MPa "
          f"xL={[round(float(z),6) for z in r.GetLiquidPhase1MoleFractions()]} "
          f"xV={[round(float(z),6) for z in r.GetVaporPhaseMoleFractions()]} "
          f"nL={[round(float(z),6) for z in r.LiquidPhase1MoleAmounts]} "
          f"nV={[round(float(z),6) for z in r.VaporPhaseMoleAmounts]} err={r.ResultException}")
    except Exception as e:
        w(f"   VF={vf:.9g} -> EXC {type(e).__name__}: {str(e)[:110]}")

sec("D) PVF (burbuja/rocio en T a P dada) con K iniciales")
for P, vf in ((1500e3, 0.0), (1500e3, 1.0), (273.55e3, 0.0)):
    try:
        r = pp.CalculateEquilibrium(FlashCalculationType.PressureVaporFraction, float(P), vf,
                                    [float(c) for c in comp], list(KF), 1.0)
        w(f"   P={P/1e3} kPa VF={vf} -> T={float(r.CalculatedTemperature):.4f} K "
          f"xL={[round(float(z),6) for z in r.GetLiquidPhase1MoleFractions()]} "
          f"xV={[round(float(z),6) for z in r.GetVaporPhaseMoleFractions()]} err={r.ResultException}")
    except Exception as e:
        w(f"   P={P/1e3} kPa VF={vf} -> EXC {type(e).__name__}: {str(e)[:110]}")

sec("E) entalpia: ruta Calculate del stream")
try:
    s2 = fs.AddObject(ObjectType.MaterialStream, 200, 200, "E1").GetAsObject()
    s2.SetOverallCompoundMassFlow("Water", 0.45)
    s2.SetOverallCompoundMassFlow("Ammonia", 0.55)
    s2.NormalizeOverallMassComposition()
    s2.PropertyPackage = pp
    pp.CurrentMaterialStream = s2
    hs = {}
    for T2 in (369.0, 300.0):
        s2.SetFlashSpec("PT")
        s2.Phases[0].Properties.temperature = T2
        s2.Phases[0].Properties.pressure = 1500e3
        s2.Phases[0].Properties.massflow = 1.0
        s2.CalcEquilibrium("PT", 369.0)   # firma (String, Object)?
        hs[T2] = float(s2.Phases[0].Properties.enthalpy)
    w("   h:", hs, "Delta h:", hs[369.0] - hs[300.0])
except Exception as e:
    w("   EXC", type(e).__name__, str(e)[:300])

sec("F) ruta alternativa: entalpia desde el resultado del flash")
for T2 in (369.0, 300.0):
    r = pp.CurrentMaterialStream
    fs3, s3, p3 = nuevo("Peng-Robinson (PR)")
    rr = p3.CurrentMaterialStream
    res = p3.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, T2,
                                  [0.4361300189230316, 0.5638699810769684], list(KF), 1.0)
    w(f"   T={T2}: CalculatedEnthalpy={float(res.CalculatedEnthalpy):.4f} "
      f"CalculatedEntropy={float(res.CalculatedEntropy):.6f} "
      f"nL={sum(float(z) for z in res.LiquidPhase1MoleAmounts):.6f} "
      f"nV={sum(float(z) for z in res.VaporPhaseMoleAmounts):.6f}")
LOG.close()
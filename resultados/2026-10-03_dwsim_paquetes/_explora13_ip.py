"""Exploracion 13: campo `ip` (BIP) de las EOS cubicas tras un flash, todos los paquetes."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora13_ip.txt"), "w", encoding="utf-8")
def w(*a):
    s = " ".join(str(v) for v in a); print(s); LOG.write(s + "\n"); LOG.flush()
D = r"D:\DWSIM"; os.chdir(D)
from pythonnet import load; load("netfx")
import clr
sys.path.append(D); os.environ["PATH"] = D + os.pathsep + os.environ["PATH"]
for dll in ("DWSIM.Interfaces", "DWSIM.GlobalSettings", "DWSIM.SharedClasses",
            "DWSIM.Thermodynamics", "DWSIM.UnitOperations", "DWSIM.Automation"):
    clr.AddReference(os.path.join(D, dll + ".dll"))
from DWSIM.Automation import Automation3
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Interfaces.Enums import FlashCalculationType
from System.Reflection import BindingFlags
BF = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly
M_A, M_W = 17.03052, 18.015268
mgr = Automation3()
def xmol(w): return (w / M_A) / ((w / M_A) + ((1 - w) / M_W))
def leer_ip(pp):
    t = pp.GetType()
    while t is not None and t.FullName != "System.Object":
        for f in t.GetFields(BF):
            if f.Name == "ip":
                v = f.GetValue(pp)
                if v is not None and hasattr(v, "Rank"):
                    d = [v.GetLength(i) for i in range(v.Rank)]
                    return f"{t.Name}.ip", [[round(float(v[a, b]), 6) for b in range(d[1])] for a in range(d[0])]
        t = t.BaseType
    return None, None
def leer_mip(pp):
    t = pp.GetType()
    while t is not None and t.FullName != "System.Object":
        for f in t.GetFields(BF):
            if f.Name == "m_ip":
                v = f.GetValue(pp)
                return len(v.Columns), [[str(x) for x in r] for r in v.Rows]
        t = t.BaseType
    return None, None
nombres = list(mgr.CreateFlowsheet().GetAvailablePropertyPackages())
x = xmol(0.55)
w("paquetes:", len(nombres))
for n in nombres:
    try:
        fs = mgr.CreateFlowsheet(); fs.AddCompound("Water"); fs.AddCompound("Ammonia")
        so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
        so.SetOverallCompoundMassFlow("Water", 0.45); so.SetOverallCompoundMassFlow("Ammonia", 0.55)
        so.NormalizeOverallMassComposition()
        pp = fs.CreateAndAddPropertyPackage(n); so.PropertyPackage = pp; pp.CurrentMaterialStream = so
    except Exception as e:
        w(f"\n-- {n}: NO CREA {type(e).__name__}: {str(e)[:80]}"); continue
    vf = None
    try:
        r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, 369.0,
                                    [float(1 - x), float(x)], [0.1, 5.0], 1.0)
        vf = sum(float(z) for z in r.VaporPhaseMoleAmounts) / float(r.BaseMoleAmount)
    except Exception as e:
        w(f"\n-- {n}: {pp.GetType().Name} | flash FALLO {type(e).__name__}: {str(e)[:90]}")
    nom, val = leer_ip(pp)
    ncol, filas = leer_mip(pp)
    w(f"\n-- {n}: {pp.GetType().Name} | VF1500kPa369K={vf}")
    w(f"     {nom} = {val}")
    w(f"     m_ip: {ncol} columnas, {len(filas)} filas -> {filas}")
LOG.close()

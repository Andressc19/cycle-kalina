"""Exploracion 12: contenido de MAT_KIJ (BIP de las EOS cubicas) tras un flash."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora12_matkij.txt"), "w", encoding="utf-8")
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
def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))
def nuevo(n):
    fs = mgr.CreateFlowsheet(); fs.AddCompound("Water"); fs.AddCompound("Ammonia")
    so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 0.45); so.SetOverallCompoundMassFlow("Ammonia", 0.55)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(n); so.PropertyPackage = pp; pp.CurrentMaterialStream = so
    return fs, so, pp
def dump_matkij(pp, etiqueta):
    t = pp.GetType()
    while t is not None and t.FullName != "System.Object":
        for f in t.GetFields(BF):
            if f.Name != "MAT_KIJ":
                continue
            v = f.GetValue(pp)
            w(f"   [{etiqueta}] {t.Name}.MAT_KIJ = {v}")
            if v is None:
                continue
            d = [v.GetLength(i) for i in range(v.Rank)]
            w(f"      dims={d}")
            for a in range(d[0]):
                for b in range(d[1]):
                    celda = v[a, b]
                    try:
                        w(f"      [{a}][{b}] tipo={type(celda).__name__} valor={celda}")
                    except Exception as e:
                        w(f"      [{a}][{b}] <{type(e).__name__}>")
        t = t.BaseType
for n in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "Peng-Robinson 1978 (PR78)",
          "Peng-Robinson-Stryjek-Vera 2 (PRSV2-M)"):
    try:
        fs, so, pp = nuevo(n)
    except Exception as e:
        w(f"\n-- {n}: no crea {type(e).__name__}"); continue
    w(f"\n===== {n} =====")
    dump_matkij(pp, "antes del flash")
    x = xmol(0.55)
    try:
        r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, 369.0,
                                    [float(1 - x), float(x)], [0.1, 5.0], 1.0)
        w(f"   flash OK VF={sum(float(z) for z in r.VaporPhaseMoleAmounts)/float(r.BaseMoleAmount):.6f}")
    except Exception as e:
        w(f"   flash fallo {type(e).__name__}: {str(e)[:90]}")
    dump_matkij(pp, "despues del flash")
    # ip
    t = pp.GetType()
    while t is not None and t.FullName != "System.Object":
        for f in t.GetFields(BF):
            if f.Name == "ip":
                v = f.GetValue(pp)
                if v is not None and hasattr(v, "Rank"):
                    d = [v.GetLength(i) for i in range(v.Rank)]
                    w(f"   {t.Name}.ip dims={d} valores={[[float(v[a, b]) for b in range(d[1])] for a in range(d[0])]}")
                else:
                    w(f"   {t.Name}.ip = {v}")
        t = t.BaseType
LOG.close()

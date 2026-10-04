"""Exploracion 11: leer el campo privado `ip` con GetFields (no GetField)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora11_ip.txt"), "w", encoding="utf-8")
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
from System.Reflection import BindingFlags
BF = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly
mgr = Automation3()
def nuevo(n):
    fs = mgr.CreateFlowsheet(); fs.AddCompound("Water"); fs.AddCompound("Ammonia")
    so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 1.0); so.SetOverallCompoundMassFlow("Ammonia", 1.0)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(n); so.PropertyPackage = pp; pp.CurrentMaterialStream = so
    return pp
for n in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "Peng-Robinson 1978 (PR78)",
          "Peng-Robinson-Stryjek-Vera 2 (PRSV2-M)", "Peng-Robinson-Stryjek-Vera 2 (PRSV2-VL)",
          "PR/LK", "Peng-Robinson / Lee-Kesler (PR/LK)", "SRK Advanced",
          "Soave-Redlich-Kwong (SRK) Advanced", "Peng-Robinson 1978 (PR78) Advanced",
          "CoolProp", "PC-SAFT (with Association Support) (.NET Code)"):
    try:
        pp = nuevo(n)
    except Exception as e:
        w(f"\n-- {n}: no crea: {type(e).__name__}: {str(e)[:70]}"); continue
    t = pp.GetType(); w(f"\n-- {n} -> {t.FullName}")
    while t is not None and t.FullName != "System.Object":
        for f in t.GetFields(BF):
            if f.Name in ("ip", "m_ip", "MAT_KIJ", "m_Henry"):
                try:
                    v = f.GetValue(pp)
                    if f.Name == "MAT_KIJ" or f.Name == "m_Henry":
                        w(f"   {t.Name}.{f.Name}: tipo={type(v).__name__} (no inspeccionado)"); continue
                    if hasattr(v, "GetLength") and hasattr(v, "Rank"):
                        d = [v.GetLength(i) for i in range(v.Rank)]
                        w(f"   {t.Name}.{f.Name}: {type(v).__name__} dims={d} valores={[[float(v[a, b]) for b in range(d[1])] for a in range(d[0])]}")
                    else:
                        w(f"   {t.Name}.{f.Name}: {type(v).__name__} Columns={[str(c) for c in v.Columns] if hasattr(v, 'Columns') else '-'} filas={[[str(x) for x in r] for r in v.Rows] if hasattr(v, 'Rows') else '-'}")
                except Exception as e:
                    w(f"   {t.Name}.{f.Name}: <{type(e).__name__}: {str(e)[:60]}>")
        t = t.BaseType
LOG.close()

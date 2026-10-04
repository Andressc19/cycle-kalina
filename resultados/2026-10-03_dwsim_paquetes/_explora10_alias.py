"""Exploracion 10: alias de nombres de paquete y lectura real de BIP."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora10_alias.txt"), "w", encoding="utf-8")


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
from System.Reflection import BindingFlags

mgr = Automation3()
BF = (BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic |
      BindingFlags.DeclaredOnly)


def nuevo(nombre):
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water")
    fs.AddCompound("Ammonia")
    so = fs.AddObject(
        __import__("DWSIM.Interfaces.Enums.GraphicObjects", fromlist=["ObjectType"])
        .ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 1.0)
    so.SetOverallCompoundMassFlow("Ammonia", 1.0)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(nombre)
    so.PropertyPackage = pp
    pp.CurrentMaterialStream = so
    return fs, so, pp


def campo(obj, nombres):
    for nombre in nombres:
        t = obj.GetType()
        while t is not None and t.FullName != "System.Object":
            f = t.GetField(nombre, BF)
            if f is not None:
                try:
                    return nombre, f.GetValue(obj)
                except Exception as e:
                    return nombre, f"<{type(e).__name__}: {str(e)[:60]}>"
            t = t.BaseType
    return None, None


w("== alias: PRSV2-VL y Lee-Kesler-Plucker ==")
for alias in ("Peng-Robinson-Stryjek-Vera 2 (PRSV2-VL)", "PRSV2-VL",
              "Lee-Kesler-Pl\u00fccker", "Lee-Kesler-Plucker", "Lee-Kesler-Pl\u00fccker (LKP)",
              "Lee-Kesler-Plucker (LKP)"):
    try:
        nuevo(alias)
        w(f"   {alias!r}: OK")
    except Exception as e:
        w(f"   {alias!r}: {type(e).__name__}: {str(e)[:80]}")

w("\n== BIP: campo ip (Double[,]) y m_ip (DataTable) por paquete ==")
for nombre in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)",
               "Peng-Robinson 1978 (PR78)", "PRSV2-M", "Peng-Robinson-Stryjek-Vera 2 (PRSV2-M)",
               "NRTL", "UNIQUAC", "Modified UNIFAC (NIST)", "UNIFAC",
               "Raoult's Law", "CoolProp", "Chao-Seader", "Grayson-Streed", "Wilson",
               "PC-SAFT (with Association Support) (.NET Code)"):
    try:
        fs, so, pp = nuevo(nombre)
    except Exception as e:
        w(f"\n-- {nombre}: no se pudo crear: {type(e).__name__}: {str(e)[:80]}")
        continue
    w(f"\n-- {nombre} ({pp.GetType().Name})")
    nom, v = campo(pp, ["ip", "m_ip"])
    if v is None:
        w("   no hay campo ip/m_ip")
        continue
    w(f"   campo '{nom}' tipo={type(v)}")
    try:
        w(f"   dims={[v.GetLength(i) for i in range(v.Rank)]}")
        for i in range(v.GetLength(0)):
            row = []
            for j in range(v.GetLength(1)):
                row.append(float(v[i, j]) if v.Rank == 2 else float(v[i, j, 0]))
            w(f"     fila {i}: {row}")
    except Exception as e:
        w(f"   no es array: {type(e).__name__}: {str(e)[:80]}")
        try:
            w(f"   Columns={[str(c) for c in v.Columns]}")
            w(f"   Rows={[[str(x) for x in row] for row in v.Rows]}")
        except Exception as e2:
            w(f"   tampoco DataTable: {type(e2).__name__}: {str(e2)[:80]}")
LOG.close()
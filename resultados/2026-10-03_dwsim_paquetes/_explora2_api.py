"""Exploracion 2: inventario de paquetes de propiedades + reflexion de BIP.

Escribe _explora2_paquetes.txt y _explora2_api.txt junto al script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora2_paquetes.txt"), "w", encoding="utf-8")


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

mgr = Automation3()

# --- 1. lista de paquetes disponibles: 3 vias de descubrimiento ---
w("== via 1: fs.GetAvailablePropertyPackages() ==")
mgr0 = Automation3()
fs0 = mgr0.CreateFlowsheet()
try:
    pkgs = list(fs0.GetAvailablePropertyPackages())
    w("n =", len(pkgs))
    for p in pkgs:
        w("  -", p)
except Exception as e:
    w("EXCEPCION", type(e).__name__, e)
    pkgs = []

w("\n== via 2: fs.AvailablePropertyPackages (propiedad) ==")
try:
    w([str(p) for p in fs0.AvailablePropertyPackages])
except Exception as e:
    w("EXCEPCION", type(e).__name__, e)

# --- 2. compuestos: reflexion de la clase Compound ---
w("\n== reflexion de un ICompound (Water) ==")
fs1 = mgr.CreateFlowsheet()
wtr = fs1.AddCompound("Water")
nh3 = fs1.AddCompound("Ammonia")
w("tipo Water:", type(wtr))
w([m for m in dir(wtr) if not m.startswith("_")])

w("\n== reflexion de IPropertyPackage (Steam Tables) ==")
pp = fs1.CreateAndAddPropertyPackage("Steam Tables (IAPWS-IF97)")
w("tipo:", type(pp))
w([m for m in dir(pp) if not m.startswith("_")])

w("\n== reflexion de IMaterialStream / MaterialStream ==")
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType

s1 = fs1.AddObject(ObjectType.MaterialStream, 100, 100, "S1")
so = s1.GetAsObject()
w("tipo stream obj:", type(so))
w([m for m in dir(so) if not m.startswith("_")])
LOG.close()
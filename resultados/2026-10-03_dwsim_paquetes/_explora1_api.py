"""Exploracion 1: como descubrir la API de DWSIM (paquetes, compuestos, BIP).

Escribe todo en _explora1_api.txt junto al script. No modifica nada del proyecto.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora1_api.txt"), "w", encoding="utf-8")


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
w("== Automation3 metodos/propiedades publicas ==")
w([m for m in dir(mgr) if not m.startswith("_")])

fs = mgr.CreateFlowsheet()
w("\n== Flowsheet (tipo real) ==", type(fs))
w("== Flowsheet miembros publicos ==")
w([m for m in dir(fs) if not m.startswith("_")])

w("\n== AddCompound: sobrecargas / documentacion ==")
try:
    w("doc:", fs.AddCompound.__doc__)
except Exception as e:
    w("doc: error", e)

for cand in ("Water", "Ammonia"):
    try:
        r = fs.AddCompound(cand)
        w(f"AddCompound({cand!r}) ->", r)
    except Exception as e:
        w(f"AddCompound({cand!r}) -> EXCEPCION {type(e).__name__}: {e}")

w("\n== compuestos ya en el flowsheet ==")
try:
    w([str(c) for c in fs.GetCompounds()])
except Exception as e:
    w("GetCompounds fallo:", type(e).__name__, e)

w("\n== CreateAndAddPropertyPackage doc ==")
try:
    w(fs.CreateAndAddPropertyPackage.__doc__)
except Exception as e:
    w("error", e)

w("\n== candidatos a metodos de listado de paquetes ==")
cands = [m for m in dir(mgr) if any(k in m.lower() for k in
         ("pack", "prop", "avail", "list", "compo"))]
w(cands)
LOG.close()
"""Exploracion puntual 6: como se fija el Q (energy stream con el equipo como
source, como en la plantilla) y comportamiento de CalcTempHotOut con la
topologia exacta de la plantilla. Material de descubrimiento.
"""
import os
import sys

D = r"D:\DWSIM"
os.chdir(D)
from pythonnet import load
load("netfx")
import clr
sys.path.append(D)
for dll in ("DWSIM.Interfaces", "DWSIM.GlobalSettings", "DWSIM.SharedClasses",
            "DWSIM.Thermodynamics", "DWSIM.UnitOperations", "DWSIM.Automation"):
    clr.AddReference(os.path.join(D, dll + ".dll"))
import System
from System import Array, Double
from DWSIM.Automation import Automation3
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType as OT
from DWSIM.Interfaces.Enums import FlashCalculationType as FCT

M_NH3, M_H2O = 17.03052, 18.015268
AJUSTES = {"PHFlash_Maximum_Number_Of_External_Iterations": "1000",
           "PHFlash_Maximum_Number_Of_Internal_Iterations": "1000",
           "PTFlash_Maximum_Number_Of_External_Iterations": "2000",
           "PTFlash_Maximum_Number_Of_Internal_Iterations": "2000",
           "PHFlash_External_Loop_Tolerance": "1e-8",
           "PHFlash_Internal_Loop_Tolerance": "1e-8",
           "PTFlash_External_Loop_Tolerance": "1e-8",
           "PTFlash_Internal_Loop_Tolerance": "1e-8"}
mgr = Automation3()


def xmol(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return Array[Double]([n_w / (n_a + n_w), n_a / (n_a + n_w)])


def nuevo_fs():
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water")
    fs.AddCompound("Ammonia")
    pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
    fset = pp.GetType().GetProperty("FlashSettings").GetValue(pp)
    for k in list(fset.Keys):
        if str(k) in AJUSTES:
            fset[k] = AJUSTES[str(k)]
    return fs, pp


def fijar(so, T, P, w, m):
    so.SetOverallComposition(xmol(w))
    p = so.Phases[0].Properties
    p.temperature, p.pressure, p.massflow = T, P, m


def enum(o, n):
    return System.Enum.Parse(o.CalcMode.GetType(), n)


def ph(s):
    p = s.Phases[0].Properties
    return dict(T=round(float(p.temperature), 4),
                P=round(float(p.pressure), 1), m=round(float(p.massflow), 6),
                h=round(float(p.enthalpy), 4) if p.enthalpy is not None else None)


print("=== EnergyStream: propiedades escribibles ===")
fs, pp = nuevo_fs()
e = fs.AddObject(OT.EnergyStream, 10, 10, "E").GetAsObject()
print(sorted(str(p.Name) for p in e.GetType().GetProperties() if p.CanWrite))
print("metodos:", [str(m.Name) for m in e.GetType().GetMethods()
                   if str(m.Name).startswith("Set")])

print("=== Heater HeatAdded: energy stream equipo->ES, 300 kW ===")
fs, pp = nuevo_fs()
a = fs.AddObject(OT.MaterialStream, 10, 10, "A").GetAsObject()
fijar(a, 340.0, 1500e3, 0.55, 1.0)
h = fs.AddObject(OT.Heater, 100, 10, "H").GetAsObject()
b = fs.AddObject(OT.MaterialStream, 200, 10, "B").GetAsObject()
es = fs.AddObject(OT.EnergyStream, 100, 60, "QE").GetAsObject()
fs.ConnectObjects(a.GraphicObject, h.GraphicObject, -1, -1)
fs.ConnectObjects(h.GraphicObject, b.GraphicObject, -1, -1)
fs.ConnectObjects(h.GraphicObject, es.GraphicObject, -1, -1)
h.CalcMode = enum(h, "HeatAdded")
h.DeltaP = 0
errs = mgr.CalculateFlowsheet2(fs)
print(" errs1=", [str(x).splitlines()[0][:70] for x in errs] if errs else "-")
print(" A=", ph(a), " B=", ph(b), " h.EnergyFlow=", h.EnergyFlow,
      " es.EnergyFlow=", es.EnergyFlow)
for metodo in ("EnergyFlow", "SetEnergyFlow"):
    try:
        if metodo == "SetEnergyFlow":
            es.SetEnergyFlow(300e3)
        else:
            es.EnergyFlow = 300e3
        h.DeCalculate()
        errs = mgr.CalculateFlowsheet2(fs)
        print("  tras %s -> %s: es=%s h.EnergyFlow=%s errs=%s"
              % (metodo, ph(b), es.EnergyFlow, h.EnergyFlow,
                 [str(x).splitlines()[0][:60] for x in errs] if errs else "-"))
    except Exception as exc:
        print("  %s FALLA: %s" % (metodo, str(exc).splitlines()[0][:90]))

print("=== HX con topologia de la plantilla (puerto 0 frio, 1 caliente) ===")
fs, pp = nuevo_fs()
s10 = fs.AddObject(OT.MaterialStream, 10, 10, "S10").GetAsObject()
fijar(s10, 330.0, 1500e3, 0.55, 1.0)
s5 = fs.AddObject(OT.MaterialStream, 10, 100, "S5").GetAsObject()
fijar(s5, 400.0, 1500e3, 0.40, 0.75)
hx = fs.AddObject(OT.HeatExchanger, 100, 50, "REG").GetAsObject()
s1 = fs.AddObject(OT.MaterialStream, 200, 10, "S1").GetAsObject()
s6 = fs.AddObject(OT.MaterialStream, 200, 100, "S6").GetAsObject()
fs.ConnectObjects(s10.GraphicObject, hx.GraphicObject, 0, 0)
fs.ConnectObjects(hx.GraphicObject, s1.GraphicObject, 0, 0)
fs.ConnectObjects(s5.GraphicObject, hx.GraphicObject, 0, 1)
fs.ConnectObjects(hx.GraphicObject, s6.GraphicObject, 1, 0)
hx.CalculationMode = System.Enum.Parse(hx.CalculationMode.GetType(), "CalcTempHotOut")
hx.HotSideOutletTemperature = 360.0
errs = mgr.CalculateFlowsheet2(fs)
print(" errs=", [str(x).splitlines()[0][:90] for x in errs] if errs else "-")
for n, s in (("S10", s10), ("S1", s1), ("S5", s5), ("S6", s6)):
    print("   %-4s %s" % (n, ph(s)))
ef = hx.EnergyFlow
print("  Q hx=%s | 0.75*(h5-h6)=%.4f | 1.0*(h1-h10)=%.4f"
      % (ef, 0.75 * (ph(s5)["h"] - ph(s6)["h"]), ph(s1)["h"] - ph(s10)["h"]))
"""Exploracion puntual 5: diagnostico Heater/Cooler en modo duty y puertos
correctos del HeatExchanger. Material de descubrimiento.
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
    return (float(p.temperature), float(p.pressure), float(p.massflow),
            float(p.enthalpy) if p.enthalpy is not None else float("nan"))


print("=== Heater HeatAdded con energy stream: variantes ===")
for orden in ("valor antes de resolver", "valor tras resolver"):
    fs, pp = nuevo_fs()
    a = fs.AddObject(OT.MaterialStream, 10, 10, "A").GetAsObject()
    fijar(a, 340.0, 1500e3, 0.55, 1.0)
    e = fs.AddObject(OT.EnergyStream, 100, 60, "E").GetAsObject()
    h = fs.AddObject(OT.Heater, 100, 10, "H").GetAsObject()
    b = fs.AddObject(OT.MaterialStream, 200, 10, "B").GetAsObject()
    fs.ConnectObjects(a.GraphicObject, h.GraphicObject, -1, -1)
    fs.ConnectObjects(h.GraphicObject, b.GraphicObject, -1, -1)
    fs.ConnectObjects(e.GraphicObject, h.GraphicObject, -1, -1)
    h.CalcMode = enum(h, "HeatAdded")
    h.DeltaP = 0
    e.EnergyFlow = 300e3
    errs = mgr.CalculateFlowsheet2(fs)
    if orden == "valor tras resolver":
        e.EnergyFlow = 300e3
        h.DeCalculate()
        errs = mgr.CalculateFlowsheet2(fs)
    print("  %-24s errs=%s" % (orden, [str(x).splitlines()[0][:60] for x in errs] if errs else "-"))
    print("     E.EnergyFlow=%s  h.EnergyFlow=%s  ErrorMessage=%s"
          % (e.EnergyFlow, h.EnergyFlow, h.ErrorMessage))
    print("     A(T,P,m,h)=%s" % (ph(a),))
    print("     B(T,P,m,h)=%s" % (ph(b),))

print("=== Heater: comparar duty implicito vs outlets ===")
fs, pp = nuevo_fs()
a = fs.AddObject(OT.MaterialStream, 10, 10, "A").GetAsObject()
fijar(a, 340.0, 1500e3, 0.55, 1.0)
h = fs.AddObject(OT.Heater, 100, 10, "H").GetAsObject()
b = fs.AddObject(OT.MaterialStream, 200, 10, "B").GetAsObject()
fs.ConnectObjects(a.GraphicObject, h.GraphicObject, -1, -1)
fs.ConnectObjects(h.GraphicObject, b.GraphicObject, -1, -1)
h.CalcMode = enum(h, "OutletTemperature")
h.OutletTemperature = 380.0
h.DeltaP = 0
errs = mgr.CalculateFlowsheet2(fs)
print("  errs=", [str(x).splitlines()[0][:60] for x in errs] if errs else "-")
print("  A=", ph(a), " B=", ph(b), " h.EnergyFlow=", h.EnergyFlow)

print("=== HeatExchanger puertos correctos (caliente=1, frio=0) ===")
fs, pp = nuevo_fs()
fr = fs.AddObject(OT.MaterialStream, 10, 10, "FRIO").GetAsObject()
fijar(fr, 320.0, 1500e3, 0.55, 1.0)
hot = fs.AddObject(OT.MaterialStream, 10, 100, "HOT").GetAsObject()
fijar(hot, 400.0, 1500e3, 0.40, 0.75)
hx = fs.AddObject(OT.HeatExchanger, 100, 50, "HX").GetAsObject()
fo = fs.AddObject(OT.MaterialStream, 200, 10, "FOUT").GetAsObject()
ho = fs.AddObject(OT.MaterialStream, 200, 100, "HOUT").GetAsObject()
fs.ConnectObjects(fr.GraphicObject, hx.GraphicObject, -1, 0)
fs.ConnectObjects(hx.GraphicObject, fo.GraphicObject, 0, -1)
fs.ConnectObjects(hot.GraphicObject, hx.GraphicObject, -1, 1)
fs.ConnectObjects(hx.GraphicObject, ho.GraphicObject, 1, -1)
hx.CalculationMode = System.Enum.Parse(hx.CalculationMode.GetType(), "CalcTempHotOut")
hx.HotSideOutletTemperature = 360.0
errs = mgr.CalculateFlowsheet2(fs)
print("  errs=", [str(x).splitlines()[0][:80] for x in errs] if errs else "-")
for n, s in (("FRIO", fr), ("FOUT", fo), ("HOT", hot), ("HOUT", ho)):
    print("   %-5s T=%9.4f h=%12.4f m=%.4f" % (n, ph(s)[0], ph(s)[3], ph(s)[2]))
ef = float(hx.EnergyFlow) if hx.EnergyFlow is not None else float("nan")
print("  Q hx=%.4f kW | caliente 0.75*(h5-h6)=%.4f | frio 1.0*(h10-h1)=%.4f"
      % (ef / 1000.0, 0.75 * (ph(hot)[3] - ph(ho)[3]) / 1000.0,
         1.0 * (ph(fo)[3] - ph(fr)[3]) / 1000.0))
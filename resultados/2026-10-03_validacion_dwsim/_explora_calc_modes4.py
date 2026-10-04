"""Exploracion puntual 4: como se impone el Q de Heater/Cooler (DeltaQ vs
EnergyStream), que atributos tiene IFlashCalculationResult, y el modo
CalcTempHotOut del HeatExchanger. Material de descubrimiento.
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


def enum(obj, nombre):
    return System.Enum.Parse(obj.CalcMode.GetType(), nombre)


def h_flash(pp, so, P, T, w):
    pp.CurrentMaterialStream = so
    xm = xmol(w)
    return float(pp.CalculateEquilibrium(FCT.PressureTemperature, P, T,
                                         [float(xm[0]), float(xm[1])],
                                         [0.0, 0.0], 1.0).CalculatedEnthalpy)


print("=== IFlashCalculationResult: atributos ===")
fs, pp = nuevo_fs()
so = fs.AddObject(OT.MaterialStream, 10, 10, "S").GetAsObject()
so.SetOverallComposition(xmol(0.55))
so.PropertyPackage = pp
pp.CurrentMaterialStream = so
res = pp.CalculateEquilibrium(FCT.PressureTemperature, 1500e3, 369.0,
                              [float(v) for v in xmol(0.55)], [0.0, 0.0], 1.0)
print([a for a in dir(res) if not a.startswith("_")])

print("=== Heater HeatAdded: DeltaQ vs EnergyStream ===")
for modo in ("DeltaQ", "EnergyStream"):
    fs, pp = nuevo_fs()
    a = fs.AddObject(OT.MaterialStream, 10, 10, "A").GetAsObject()
    fijar(a, 340.0, 1500e3, 0.55, 1.0)
    h = fs.AddObject(OT.Heater, 100, 10, "H").GetAsObject()
    b = fs.AddObject(OT.MaterialStream, 200, 10, "B").GetAsObject()
    fs.ConnectObjects(a.GraphicObject, h.GraphicObject, -1, -1)
    fs.ConnectObjects(h.GraphicObject, b.GraphicObject, -1, -1)
    h.CalcMode = enum(h, "HeatAdded")
    h.DeltaP = 0
    if modo == "DeltaQ":
        h.DeltaQ = 300e3            # W
    else:
        e = fs.AddObject(OT.EnergyStream, 100, 60, "E").GetAsObject()
        fs.ConnectObjects(e.GraphicObject, h.GraphicObject, -1, -1)
        e.EnergyFlow = 300e3         # W
    errs = mgr.CalculateFlowsheet2(fs)
    Ta = float(a.Phases[0].Properties.enthalpy)
    Tb = float(b.Phases[0].Properties.enthalpy) if b.Phases[0].Properties.enthalpy is not None else float("nan")
    print("  %-12s errores=%s  hA=%.4f hB=%.4f  m*(hB-hA)=%.3f kW  EnergyFlow=%.3f kW"
          % (modo, [str(x).splitlines()[0][:50] for x in errs] if errs else "-",
             Ta, Tb, (Tb - Ta) / 1000.0, float(h.EnergyFlow or 0) / 1000.0))

print("=== Cooler HeatRemoved ===")
for modo in ("DeltaQ", "EnergyStream"):
    fs, pp = nuevo_fs()
    a = fs.AddObject(OT.MaterialStream, 10, 10, "A").GetAsObject()
    fijar(a, 320.0, 1500e3, 0.55, 1.0)
    c = fs.AddObject(OT.Cooler, 100, 10, "C").GetAsObject()
    b = fs.AddObject(OT.MaterialStream, 200, 10, "B").GetAsObject()
    fs.ConnectObjects(a.GraphicObject, c.GraphicObject, -1, -1)
    fs.ConnectObjects(c.GraphicObject, b.GraphicObject, -1, -1)
    c.CalcMode = enum(c, "HeatRemoved")
    c.DeltaP = 0
    if modo == "DeltaQ":
        c.DeltaQ = 200e3
    else:
        e = fs.AddObject(OT.EnergyStream, 100, 60, "E").GetAsObject()
        fs.ConnectObjects(e.GraphicObject, c.GraphicObject, -1, -1)
        e.EnergyFlow = 200e3
    errs = mgr.CalculateFlowsheet2(fs)
    Ta = float(a.Phases[0].Properties.enthalpy)
    Tb = float(b.Phases[0].Properties.enthalpy) if b.Phases[0].Properties.enthalpy is not None else float("nan")
    print("  %-12s errores=%s  hA=%.4f hB=%.4f  m*(hA-hB)=%.3f kW  EnergyFlow=%.3f kW"
          % (modo, [str(x).splitlines()[0][:50] for x in errs] if errs else "-",
             Ta, Tb, (Ta - Tb) / 1000.0, float(c.EnergyFlow or 0) / 1000.0))

print("=== HeatExchanger CalcTempHotOut ===")
fs, pp = nuevo_fs()
hot = fs.AddObject(OT.MaterialStream, 10, 10, "HOT").GetAsObject()
fijar(hot, 400.0, 1500e3, 0.40, 0.75)
fr = fs.AddObject(OT.MaterialStream, 10, 100, "FRIO").GetAsObject()
fijar(fr, 320.0, 1500e3, 0.55, 1.0)
hx = fs.AddObject(OT.HeatExchanger, 100, 50, "HX").GetAsObject()
ho = fs.AddObject(OT.MaterialStream, 200, 10, "HOUT").GetAsObject()
fo = fs.AddObject(OT.MaterialStream, 200, 100, "FOUT").GetAsObject()
fs.ConnectObjects(hot.GraphicObject, hx.GraphicObject, -1, 0)
fs.ConnectObjects(hx.GraphicObject, ho.GraphicObject, 0, -1)
fs.ConnectObjects(fr.GraphicObject, hx.GraphicObject, -1, 1)
fs.ConnectObjects(hx.GraphicObject, fo.GraphicObject, 1, -1)
hx.CalculationMode = System.Enum.Parse(hx.CalculationMode.GetType(), "CalcTempHotOut")
hx.HotSideOutletTemperature = 360.0
errs = mgr.CalculateFlowsheet2(fs)
print("  errores:", [str(x).splitlines()[0][:80] for x in errs] if errs else "ninguno")
for n, s in (("HOT", hot), ("HOUT", ho), ("FRIO", fr), ("FOUT", fo)):
    p = s.Phases[0].Properties
    print("   %-5s T=%9.4f h=%12.4f m=%.4f" % (n, float(p.temperature),
                                               float(p.enthalpy), float(p.massflow)))
print("  Q hx = %.4f kW | m*(h5-h6)=%.4f | m*(h10-h1)=%.4f"
      % (float(hx.EnergyFlow) / 1000.0,
         0.75 * (float(hot.Phases[0].Properties.enthalpy) - float(ho.Phases[0].Properties.enthalpy)) / 1000.0,
         1.0 * (float(fo.Phases[0].Properties.enthalpy) - float(fr.Phases[0].Properties.enthalpy)) / 1000.0))
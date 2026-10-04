"""Exploracion puntual: nombres de CalcMode de Cooler/Heater/HeatExchanger y
verificacion de la base de entalpia (CalculatedEnhalfpy del flash vs
Phases[0].Properties.enthalpy de una corriente en el mismo estado).
Material de descubrimiento, no forma parte de la entrega.
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


def molar(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return Array[Double]([n_w / (n_a + n_w), n_a / (n_a + n_w)])


mgr = Automation3()
fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.AddCompound("Ammonia")
pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
fset = pp.GetType().GetProperty("FlashSettings").GetValue(pp)
for k in list(fset.Keys):
    if str(k) in AJUSTES:
        fset[k] = AJUSTES[str(k)]

print("--- CalcMode disponibles ---")
for t, nombre in ((OT.Cooler, "COOLER"), (OT.Heater, "HEATER"),
                  (OT.HeatExchanger, "HEATEXCHANGER"), (OT.Pump, "PUMP"),
                  (OT.Expander, "EXPANDER"), (OT.Valve, "VALVE"),
                  (OT.Vessel, "VESSEL")):
    o = fs.AddObject(t, 10, 10, "x" + nombre).GetAsObject()
    try:
        nombres = [str(v) for v in System.Enum.GetNames(o.CalcMode.GetType())]
    except Exception as e:
        nombres = ["<error %s>" % str(e).splitlines()[0][:60]]
    props = [str(p.Name) for p in o.GetType().GetProperties()]
    print(nombre, "->", nombres)
    print("   props:", [q for q in props if any(
        k in q.lower() for k in ("duty", "q", "temperature", "pressure",
                                 "efficien"))])

print("--- base de entalpia ---")
so = fs.AddObject(OT.MaterialStream, 10, 10, "S").GetAsObject()
so.SetOverallComposition(molar(0.55))
so.PropertyPackage = pp
pp.CurrentMaterialStream = so
so.Phases[0].Properties.temperature = 369.0
so.Phases[0].Properties.pressure = 1500e3
so.Phases[0].Properties.massflow = 1.0
errs = mgr.CalculateFlowsheet2(fs)
print("errores:", [str(e).splitlines()[0] for e in errs] if errs else "ninguno")
p = so.Phases[0].Properties
r = pp.CalculateEquilibrium(FCT.PressureTemperature, 1500e3, 369.0,
                            [1 - 0.4779, 0.4779], [0.0, 0.0], 1.0)
print("h Corriente  = %.6f" % float(p.enthalpy))
print("h Flash      = %.6f" % float(r.CalculatedEnthalpy))
print("dif          = %.3e" % (float(p.enthalpy) - float(r.CalculatedEnthalpy)))
r2 = pp.CalculateEquilibrium(FCT.PressureEnthalpy, 273.5454214157179e3,
                             float(p.enthalpy), [1 - 0.4779, 0.4779], [0.0, 0.0], 1.0)
print("T desde (P,h) = %.6f" % float(r2.Temperature))
print("molar x del flash:", [float(v) for v in r.GetLiquidPhase1MoleFractions()])
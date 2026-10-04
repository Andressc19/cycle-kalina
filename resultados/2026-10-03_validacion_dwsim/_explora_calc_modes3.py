"""Exploracion puntual 3: (a) por que falla CalculateEquilibrium tras
CalculateFlowsheet2, (b) como se impone el Q de un Heater/Cooler en modo
HeatAdded/HeatRemoved, (c) modo CalcTempHotOut del HeatExchanger.
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
mgr = Automation3()


def xmol(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return (n_w / (n_a + n_w), n_a / (n_a + n_w))


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


print("=== (a) flash sin CalculateFlowsheet2 ===")
fs, pp = nuevo_fs()
so = fs.AddObject(OT.MaterialStream, 10, 10, "S").GetAsObject()
so.SetOverallCompoundMassFlow("Water", 0.45)
so.SetOverallCompoundMassFlow("Ammonia", 0.55)
so.NormalizeOverallMassComposition()
so.PropertyPackage = pp
pp.CurrentMaterialStream = so
xm = xmol(0.55)
try:
    r = pp.CalculateEquilibrium(FCT.PressureTemperature, 1500e3, 369.0,
                                [xm[0], xm[1]], [0.0, 0.0], 1.0)
    print("  OK h =", float(r.CalculatedEnthalpy), "T =", float(r.Temperature))
except Exception as e:
    print("  FALLA:", str(e).splitlines()[0][:90])

print("=== (a2) flash DESPUES de CalculateFlowsheet2, reasignando CurrentMaterialStream ===")
so.Phases[0].Properties.temperature = 369.0
so.Phases[0].Properties.pressure = 1500e3
so.Phases[0].Properties.massflow = 1.0
errs = mgr.CalculateFlowsheet2(fs)
print("  errores:", [str(e).splitlines()[0] for e in errs] if errs else "ninguno")
print("  h corriente =", float(so.Phases[0].Properties.enthalpy))
pp.CurrentMaterialStream = so
try:
    r = pp.CalculateEquilibrium(FCT.PressureTemperature, 1500e3, 369.0,
                                [xm[0], xm[1]], [0.0, 0.0], 1.0)
    print("  OK h =", float(r.CalculatedEnthalpy))
except Exception as e:
    print("  FALLA:", str(e).splitlines()[0][:90])

print("=== (b) miembros publicos de HEATER (metodos + campos) ===")
fs0, pp0 = nuevo_fs()
h = fs0.AddObject(OT.Heater, 10, 10, "H").GetAsObject()
for m in h.GetType().GetMembers():
    n = str(m.Name)
    if any(k in n.lower() for k in ("duty", "heat", "q", "setcalc", "calc")):
        print("   %-14s %s" % (str(m.MemberType), n))

print("=== (b2) probar DeltaQ / EnergyFlow como Q ===")
print("  DeltaQ inicial =", h.DeltaQ, " EnergyFlow =", h.EnergyFlow)
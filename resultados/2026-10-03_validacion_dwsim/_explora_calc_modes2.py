"""Exploracion puntual 2: TODAS las propiedades de Cooler/Heater/HeatExchanger
y verificacion de la base de entalpia en un flowsheet limpio.
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


def molar(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return Array[Double]([n_w / (n_a + n_w), n_a / (n_a + n_w)])


def xmol(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return (n_w / (n_a + n_w), n_a / (n_a + n_w))


fs0, _ = nuevo_fs()
print("--- todas las propiedades ---")
for t, nombre in ((OT.Cooler, "COOLER"), (OT.Heater, "HEATER"),
                  (OT.HeatExchanger, "HEATEXCHANGER")):
    o = fs0.AddObject(t, 10, 10, "x" + nombre).GetAsObject()
    print(nombre, sorted(str(p.Name) for p in o.GetType().GetProperties()
                         if p.CanWrite))

print("--- base de entalpia (flowsheet limpio) ---")
fs, pp = nuevo_fs()
so = fs.AddObject(OT.MaterialStream, 10, 10, "S").GetAsObject()
so.SetOverallCompoundMassFlow("Water", 0.45)
so.SetOverallCompoundMassFlow("Ammonia", 0.55)
so.NormalizeOverallMassComposition()
so.PropertyPackage = pp
pp.CurrentMaterialStream = so
so.Phases[0].Properties.temperature = 369.0
so.Phases[0].Properties.pressure = 1500e3
so.Phases[0].Properties.massflow = 1.0
errs = mgr.CalculateFlowsheet2(fs)
print("errores:", [str(e).splitlines()[0] for e in errs] if errs else "ninguno")
h_corr = float(so.Phases[0].Properties.enthalpy)
xm = xmol(0.55)
r = pp.CalculateEquilibrium(FCT.PressureTemperature, 1500e3, 369.0,
                            [xm[0], xm[1]], [0.0, 0.0], 1.0)
h_flash = float(r.CalculatedEnthalpy)
print("h Corriente = %.6f   h Flash = %.6f   dif = %.3e"
      % (h_corr, h_flash, h_corr - h_flash))
r2 = pp.CalculateEquilibrium(FCT.PressureEnthalpy, 273.5454214157179e3,
                             h_corr, [xm[0], xm[1]], [0.0, 0.0], 1.0)
print("T desde (P,h) con h de la corriente = %.6f" % float(r2.Temperature))
print("x_liq molares:", [float(v) for v in r.GetLiquidPhase1MoleFractions()])
print("x_vap  molares:", [float(v) for v in r.GetVaporPhaseMoleFractions()])
print("VF molar:", float(sum(r.VaporPhaseMoleAmounts) / float(r.BaseMoleAmount)))
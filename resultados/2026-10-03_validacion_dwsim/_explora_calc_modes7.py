"""Exploracion puntual 7: campos internos de Heater/Cooler (para hallar la
propiedad del Q), fases de una corriente calculada, y lectura de
CalculatedTemperature en el flash P-h. Material de descubrimiento.
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
from System.Reflection import BindingFlags
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


print("=== TODOS los campos (public+privados) de HEATER ===")
fs, pp = nuevo_fs()
h = fs.AddObject(OT.Heater, 10, 10, "H").GetAsObject()
for f in h.GetType().GetFields(BindingFlags.Public | BindingFlags.NonPublic |
                               BindingFlags.Instance):
    print("   %-34s %s" % (str(f.FieldType.Name), str(f.Name)))

print("=== TODOS los campos de COOLER ===")
c = fs.AddObject(OT.Cooler, 10, 60, "C").GetAsObject()
for f in c.GetType().GetFields(BindingFlags.Public | BindingFlags.NonPublic |
                               BindingFlags.Instance):
    print("   %-34s %s" % (str(f.FieldType.Name), str(f.Name)))

print("=== ObjectType: nombres con Spec/Adjust ===")
print([str(v) for v in System.Enum.GetNames(OT.GetType())
       if "Spec" in str(v) or "Adjust" in str(v)])

print("=== fases de una corriente calculada + flash P-h ===")
fs, pp = nuevo_fs()
s10 = fs.AddObject(OT.MaterialStream, 10, 10, "S10").GetAsObject()
s10.SetOverallComposition(xmol(0.55))
p = s10.Phases[0].Properties
p.temperature, p.pressure, p.massflow = 330.0, 1500e3, 1.0
s5 = fs.AddObject(OT.MaterialStream, 10, 100, "S5").GetAsObject()
s5.SetOverallComposition(xmol(0.40))
p = s5.Phases[0].Properties
p.temperature, p.pressure, p.massflow = 400.0, 1500e3, 0.75
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
print(" errs=", [str(x).splitlines()[0][:70] for x in errs] if errs else "-")


def fases(nom, s):
    print("  %s: n_phases=%d" % (nom, len(s.Phases)))
    for i, ph in enumerate(s.Phases):
        pr = ph.Properties
        print("    [%d] id=%s T=%.4f P=%.1f m=%.6f h=%.4f vf=%s"
              % (i, str(ph.PhaseID), float(pr.temperature), float(pr.pressure),
                 float(pr.massflow),
                 float(pr.enthalpy) if pr.enthalpy is not None else float("nan"),
                 str(pr.molarfraction)))


for n, s in (("S10", s10), ("S1", s1), ("S5", s5), ("S6", s6)):
    fases(n, s)

print("=== flash P-h: T con h de una corriente ===")
for nom, s, P, w in (("S10", s10, 273.5454214157179e3, 0.55),
                     ("S1", s1, 1500e3, 0.55)):
    hval = float(s.Phases[0].Properties.enthalpy)
    pp.CurrentMaterialStream = s
    xm = xmol(w)
    r = pp.CalculateEquilibrium(FCT.PressureEnthalpy, P, hval,
                                [float(xm[0]), float(xm[1])], [0.0, 0.0], 1.0)
    print("  %s h=%.4f -> T=%.6f (stream T=%.4f)"
          % (nom, hval, float(r.CalculatedTemperature),
             float(s.Phases[0].Properties.temperature)))
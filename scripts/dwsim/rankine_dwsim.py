"""Ciclo Rankine ideal en DWSIM via pythonnet (runtime netfx). Agua, IAPWS-IF97."""
import sys, os
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
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType

P_BAJA, P_ALTA, T_ALTA, M = 10e3, 8e6, 773.15, 1.0   # Pa, Pa, K, kg/s
ETA_T, ETA_B = 1.0, 1.0                              # ideal

mgr = Automation3()
fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.CreateAndAddPropertyPackage("Steam Tables (IAPWS-IF97)")

def add(t, name, x, y):
    return fs.AddObject(t, x, y, name)

s1, s2, s3, s4, s5 = (add(ObjectType.MaterialStream, f"S{i}", 100 + 150 * i, 100) for i in range(1, 6))
eB, eC, eT, eK = (add(ObjectType.EnergyStream, n, 100, 250) for n in ("W_bomba", "Q_caldera", "W_turbina", "Q_cond"))
bomba = add(ObjectType.Pump, "Bomba", 200, 100)
cald = add(ObjectType.Heater, "Caldera", 350, 100)
turb = add(ObjectType.Expander, "Turbina", 500, 100)
cond = add(ObjectType.Cooler, "Condensador", 650, 100)

c = fs.ConnectObjects
c(s1.GraphicObject, bomba.GraphicObject, -1, -1); c(bomba.GraphicObject, s2.GraphicObject, -1, -1)
c(eB.GraphicObject, bomba.GraphicObject, -1, -1)
c(s2.GraphicObject, cald.GraphicObject, -1, -1); c(cald.GraphicObject, s3.GraphicObject, -1, -1)
c(eC.GraphicObject, cald.GraphicObject, -1, -1)
c(s3.GraphicObject, turb.GraphicObject, -1, -1); c(turb.GraphicObject, s4.GraphicObject, -1, -1)
c(turb.GraphicObject, eT.GraphicObject, -1, -1)
c(s4.GraphicObject, cond.GraphicObject, -1, -1); c(cond.GraphicObject, s5.GraphicObject, -1, -1)
c(cond.GraphicObject, eK.GraphicObject, -1, -1)


def enum_val(obj, prop, name):
    return getattr(type(getattr(obj, prop)), name)

# --- datos de entrada ---
st = s1.GetAsObject()
st.Phases[0].Properties.temperature = 318.9573      # Tsat(10 kPa), liquido saturado
st.Phases[0].Properties.pressure = P_BAJA
st.Phases[0].Properties.massflow = M
st.Phases[0].Properties.molarfraction  # sin efecto; composicion es 100% agua

B = bomba.GetAsObject(); B.CalcMode = enum_val(B, "CalcMode", "OutletPressure"); B.Pout = P_ALTA; B.Eficiencia = ETA_B * 100
H = cald.GetAsObject(); H.CalcMode = enum_val(H, "CalcMode", "OutletTemperature"); H.OutletTemperature = T_ALTA; H.DeltaP = 0
T = turb.GetAsObject(); T.CalcMode = enum_val(T, "CalcMode", "OutletPressure"); T.POut = P_BAJA; T.AdiabaticEfficiency = ETA_T * 100
C = cond.GetAsObject(); C.CalcMode = enum_val(C, "CalcMode", "OutletVaporFraction"); C.OutletVaporFraction = 0.0; C.DeltaP = 0

errs = mgr.CalculateFlowsheet2(fs)
print("errores de solve:", [str(e) for e in errs] if errs else "ninguno")

def p(s): return s.GetAsObject().Phases[0].Properties
for n, s in (("S1", s1), ("S2", s2), ("S3", s3), ("S4", s4), ("S5", s5)):
    q = p(s)
    print(f"{n}: T={q.temperature-273.15:8.2f} C  P={q.pressure/1e3:8.1f} kPa  h={q.enthalpy:9.2f} kJ/kg  s={q.entropy:7.4f} kJ/kgK")
wb = p(s2).enthalpy - p(s1).enthalpy
qc = p(s3).enthalpy - p(s2).enthalpy
wt = p(s3).enthalpy - p(s4).enthalpy
qk = p(s4).enthalpy - p(s5).enthalpy
print(f"w_bomba={wb:.3f}  q_caldera={qc:.2f}  w_turbina={wt:.2f}  q_cond={qk:.2f} kJ/kg")
print(f"eficiencia termica = {(wt-wb)/qc*100:.2f} %")
mgr.SaveFlowsheet(fs, os.path.join(r"D:\Desktop\ciclo_kalina_tercero\scripts\dwsim", "rankine.dwxmz"), True)

"""KCS11, caso Elsayed 2013, en DWSIM via pythonnet (runtime netfx).

Topologia (PLANTEAMIENTO_MATEMATICO.md §1.1):
10 -[REG frio]-> 1 -[HRVG]-> 2 -[SEP]-> {3 -[TURB]-> 4 ; 5 -[REG caliente]-> 6 -[VAL]-> 7}
4 + 7 -[ABS]-> 8 -[COND]-> 9 -[BOMBA]-> 10

Datos (§7): P_alta=1500 kPa, P_baja=273.55 kPa, x_b=0.55 masica, T2=369 K,
T9=287 K, eta_t=eta_p=0.80, regenerador con pinch 4 K (modo PinchPoint, MITA).
Paquete: Peng-Robinson (PR), PROVISIONAL hasta cerrar la sonda de paquetes.
Corte del lazo: S5 (liquido pobre) con bloque Recycle; S9 se alimenta fija y
la salida del condensador (S9c) se compara con ella como cierre del ciclo.
"""
import sys, os
D = r"D:\DWSIM"
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kcs11_elsayed.dwxmz")
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

P_ALTA, P_BAJA = 1500e3, 273.55e3          # Pa
T2, T9, MITA = 369.0, 287.0, 4.0           # K
ETA_T, ETA_P, M_B = 80.0, 80.0, 1.0        # %, %, kg/s
M_NH3, M_H2O = 17.03052, 18.015268


def molar(w):
    n_a, n_w = w / M_NH3, (1 - w) / M_H2O
    return Array[Double]([n_w / (n_a + n_w), n_a / (n_a + n_w)])   # orden: Water, Ammonia


mgr = Automation3()
fs = mgr.CreateFlowsheet()
fs.AddCompound("Water")
fs.AddCompound("Ammonia")
# Ajustes del flash (probados 2026-10-03 en los flash P-H de turbina y valvula):
# - de fabrica (100 iteraciones P-T): la valvula (liquido pobre 1500->273.55 kPa)
#   falla en el flash P-T interno por maximo de iteraciones.
# - NL_FastMode=False la destraba, pero da una FALSA convergencia en la salida de la
#   turbina (h +144 kJ/kg sobre la pedida, sin error): NO usar.
# - subir iteraciones P-H y P-T resuelve ambos con dH = 0.000 kJ/kg.
# - con tolerancias de fabrica (1e-4) el absorbedor queda con dH = -2.34 kJ/kg
#   (2.3 kW de desbalance); con 1e-8 en P-H y P-T queda en 0.0000.
_TOL = "1e-8"
AJUSTES = {"PHFlash_Maximum_Number_Of_External_Iterations": "1000",
           "PHFlash_Maximum_Number_Of_Internal_Iterations": "1000",
           "PTFlash_Maximum_Number_Of_External_Iterations": "2000",
           "PTFlash_Maximum_Number_Of_Internal_Iterations": "2000",
           "PHFlash_External_Loop_Tolerance": _TOL, "PHFlash_Internal_Loop_Tolerance": _TOL,
           "PTFlash_External_Loop_Tolerance": _TOL, "PTFlash_Internal_Loop_Tolerance": _TOL}

def paquete(ajustes, tag):
    pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
    pp.Tag = tag
    fset = pp.GetType().GetProperty("FlashSettings").GetValue(pp)
    for k in list(fset.Keys):
        if str(k) in ajustes:
            fset[k] = ajustes[str(k)]
    return pp

PP = paquete(AJUSTES, "PR_NH3H2O")

def add(t, n, x, y):
    return fs.AddObject(t, x, y, n)

def enum(obj, nombre):
    return System.Enum.Parse(obj.CalcMode.GetType(), nombre)

# --- equipos (posiciones para que el diagrama se lea en la interfaz) ---
bomba = add(OT.Pump, "BOMBA", 100, 400)
reg = add(OT.HeatExchanger, "REGENERADOR", 300, 250)
hrvg = add(OT.Heater, "HRVG", 450, 100)
sep = add(OT.Vessel, "SEPARADOR", 620, 100)
turb = add(OT.Expander, "TURBINA", 820, 60)
val = add(OT.Valve, "VALVULA", 500, 400)
absb = add(OT.Mixer, "ABSORBEDOR", 820, 400)
cond = add(OT.Cooler, "CONDENSADOR", 650, 520)
rec = add(OT.OT_Recycle, "REC_S5", 560, 250)
S = {n: add(OT.MaterialStream, n, x, y) for n, x, y in (
    ("S9", 30, 400), ("S10", 200, 330), ("S1", 380, 170), ("S2", 540, 100),
    ("S3", 740, 40), ("S4", 900, 250), ("S5calc", 620, 200), ("S5", 470, 250),
    ("S6", 400, 400), ("S7", 650, 400), ("S8", 900, 520), ("S9c", 500, 600))}
E = {n: add(OT.EnergyStream, n, x, y) for n, x, y in (
    ("W_bomba", 100, 500), ("Q_hrvg", 450, 20), ("W_turb", 900, 20), ("Q_cond", 650, 620))}

def c(a, b, i=-1, j=-1):
    fs.ConnectObjects(a.GraphicObject, b.GraphicObject, i, j)

c(S["S9"], bomba); c(bomba, S["S10"]); c(E["W_bomba"], bomba)
c(S["S10"], reg, 0, 0); c(reg, S["S1"], 0, 0)           # lado frio: puerto 0
c(S["S5"], reg, 0, 1); c(reg, S["S6"], 1, 0)            # lado caliente: puerto 1
c(S["S1"], hrvg); c(hrvg, S["S2"]); c(E["Q_hrvg"], hrvg)
c(S["S2"], sep, 0, 0); c(sep, S["S3"], 0, 0); c(sep, S["S5calc"], 1, 0)   # 0 vapor, 1 liquido
c(S["S5calc"], rec); c(rec, S["S5"])
c(S["S3"], turb); c(turb, S["S4"]); c(turb, E["W_turb"])
c(S["S6"], val); c(val, S["S7"])
c(S["S4"], absb, 0, 0); c(S["S7"], absb, 0, 1); c(absb, S["S8"])
c(S["S8"], cond); c(cond, S["S9c"]); c(cond, E["Q_cond"])

def fijar(n, T, P, w, m):
    st = S[n].GetAsObject()
    st.SetOverallComposition(molar(w))
    p = st.Phases[0].Properties
    p.temperature, p.pressure, p.massflow = T, P, m

fijar("S9", T9, P_BAJA, 0.55, M_B)                       # entrada fija de la bomba
fijar("S5", T2, P_ALTA, 0.41, 0.75)                     # estimado inicial del corte (motor: x5=0.4096)

B = bomba.GetAsObject(); B.CalcMode = enum(B, "OutletPressure"); B.Pout = P_ALTA; B.Eficiencia = ETA_P
R = reg.GetAsObject(); R.CalcMode = enum(R, "PinchPoint"); R.MITA = MITA
H = hrvg.GetAsObject(); H.CalcMode = enum(H, "OutletTemperature"); H.OutletTemperature = T2; H.DeltaP = 0
T = turb.GetAsObject(); T.CalcMode = enum(T, "OutletPressure"); T.POut = P_BAJA; T.AdiabaticEfficiency = ETA_T
V = val.GetAsObject(); V.CalcMode = enum(V, "OutletPressure"); V.OutletPressure = P_BAJA
C = cond.GetAsObject(); C.CalcMode = enum(C, "OutletTemperature"); C.OutletTemperature = T9; C.DeltaP = 0

RC = rec.GetAsObject(); RC.MaximumIterations = 50
errs = mgr.CalculateFlowsheet2(fs)
print("errores:", [str(e).splitlines()[0] for e in errs] if errs else "ninguno")
print("recycle convergido:", RC.Converged, "| historial:", [round(float(x), 6) for x in list(RC.ConvergenceHistory.TemperatureE)[-5:]] if hasattr(RC.ConvergenceHistory, "TemperatureE") else "")

def props(n):
    st = S[n].GetAsObject(); p = st.Phases[0].Properties
    w = st.Phases[0].Compounds["Ammonia"].MassFraction
    vf = st.Phases[2].Properties.molarfraction
    return tuple(float("nan") if v is None else v for v in
                 (p.temperature, p.pressure / 1e3, p.massflow, w, p.enthalpy, p.entropy, vf))

print(f"{'corr':6}{'T[K]':>9}{'P[kPa]':>9}{'m[kg/s]':>9}{'w_NH3':>8}{'h[kJ/kg]':>10}{'s':>9}{'VFmol':>7}")
for n in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9c", "S9", "S10"):
    T_, P_, m, w, h, s, vf = props(n)
    print(f"{n:6}{T_:9.2f}{P_:9.2f}{m:9.4f}{w:8.4f}{h:10.2f}{s:9.4f}{vf:7.3f}")
m3, h3, h4 = props("S3")[2], props("S3")[4], props("S4")[4]
mb, h9, h10, h1, h2 = M_B, props("S9")[4], props("S10")[4], props("S1")[4], props("S2")[4]
Wt, Wp, Qi = m3 * (h3 - h4), mb * (h10 - h9), mb * (h2 - h1)
Qo = props("S8")[2] * (props("S8")[4] - props("S9c")[4])
print(f"Wt={Wt:.2f} kW  Wp={Wp:.3f} kW  Qi={Qi:.2f} kW  Qout={Qo:.2f} kW")
print(f"eta = {(Wt - Wp) / Qi * 100:.3f} %   cierre Qi+Wp-Qout-Wt = {Qi + Wp - Qo - Wt:.3f} kW")
# Verificacion por equipo: energia que reporta DWSIM vs cambio de entalpia de corrientes
for n, val_eq, val_st in (("TURBINA", E["W_turb"], Wt), ("BOMBA", E["W_bomba"], Wp),
                          ("HRVG", E["Q_hrvg"], Qi), ("CONDENSADOR", E["Q_cond"], Qo)):
    eq = val_eq.GetAsObject().EnergyFlow
    print(f"  {n:12} equipo={eq:9.3f} kW  corrientes={val_st:9.3f} kW  dif={eq - val_st:+.3f}")
m5, h5, h6 = props("S5")[2], props("S5")[4], props("S6")[4]
print(f"  REGENERADOR  caliente={m5 * (h5 - h6):9.3f} kW  frio={mb * (h1 - h10):9.3f} kW")
print(f"  VALVULA      h6={h6:.3f}  h7={props('S7')[4]:.3f} kJ/kg")
print(f"  RECICLO S5   m={m5:.5f} vs S5calc m={props('S5calc')[2]:.5f} kg/s")
mgr.SaveFlowsheet(fs, SALIDA, True)
print("guardado:", SALIDA)

"""Exploracion 8: BIP por reflexion (campos no publicos), firma CalcEquilibrium,
escaneo VF(P) para bisección, TVF con K iniciales mejores."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora8_bip.txt"), "w", encoding="utf-8")


def w(*a):
    s = " ".join(str(v) for v in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def sec(t):
    w("\n===== " + t + " =====")


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
from DWSIM.Interfaces.Enums import FlashCalculationType
import System
from System.Reflection import BindingFlags

M_A, M_W = 17.03052, 18.015268
mgr = Automation3()


def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))


def nuevo(pname):
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water")
    fs.AddCompound("Ammonia")
    so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 1.0)
    so.SetOverallCompoundMassFlow("Ammonia", 1.0)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(pname)
    so.PropertyPackage = pp
    pp.CurrentMaterialStream = so
    return fs, so, pp


def comp_molar(wNH3):
    x = xmol(wNH3)
    return [float(1 - x), float(x)]


def leer_pt(pp, P, T, comp):
    r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, float(P), float(T),
                                [float(c) for c in comp], [0.0, 0.0], 1.0)
    n = float(r.BaseMoleAmount)
    vf = sum(float(v) for v in r.VaporPhaseMoleAmounts) / n
    xl = [float(v) for v in r.GetLiquidPhase1MoleFractions()]
    xv = [float(v) for v in r.GetVaporPhaseMoleFractions()]
    return vf, xl, xv


sec("A) firma de CalcEquilibrium / Calculate en MaterialStream")
fs, so, pp = nuevo("Peng-Robinson (PR)")
for m in ("CalcEquilibrium", "CalcEquilibrium1", "CalcEquilibrium2", "CalcEquilibrium3",
          "Calculate", "Solve", "AtEquilibrium", "SetFlashSpec"):
    try:
        w(f"  {m}: {getattr(type(so), m).__doc__}")
    except Exception as e:
        w(f"  {m}: <{type(e).__name__}>")

sec("B) campos/propiedades no publicos del paquete PR (BIP)")
t = pp.GetType()
w("tipo:", t.FullName)
campos = []
for f in t.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic):
    campos.append((f.Name, str(f.FieldType)))
for p in t.GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic):
    campos.append(("[prop] " + p.Name, str(p.PropertyType)))
inter = [c for c in campos if any(k in c[0].lower() for k in
                                   ("interaction", "bip", "_kos", "unifac", "unequac",
                                    "matrix", "param"))]
for n_, ty in sorted(inter):
    w(f"   {n_} : {ty}")

w("\n-- valores de los campos Interaction* --")
for f in t.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic):
    if "interaction" not in f.Name.lower():
        continue
    try:
        v = f.GetValue(pp)
        if hasattr(v, "GetLength"):
            w(f"   {f.Name}: rank={v.Rank} dims={[v.GetLength(i) for i in range(v.Rank)]}")
            if v.Rank == 3:
                d = [v.GetLength(i) for i in range(3)]
                for i in range(d[0]):
                    for j in range(d[1]):
                        w(f"      [{i}][{j}] = {float(v[i, j, 0]):.6g}, {float(v[i, j, 1]):.6g}")
        else:
            w(f"   {f.Name}: {v}")
    except Exception as e:
        w(f"   {f.Name}: <{type(e).__name__}: {str(e)[:100]}>")

sec("C) escaneo VF(P) con PR a T=300 K, x_NH3=0.2 molar (ref p_bub=0.040710 MPa)")
comp = [0.8, 0.2]
for P in (1e3, 5e3, 1e4, 2e4, 3e4, 4.06e4, 4.5e4, 5e4, 1e5, 2e5):
    try:
        w(f"   P={P/1e3:8.3f} kPa -> VF={leer_pt(pp, P, 300.0, comp)[0]:.8f}")
    except Exception as e:
        w(f"   P={P/1e3:8.3f} kPa -> EXC {type(e).__name__}: {str(e)[:90]}")

sec("D) TVF con vectores K iniciales distintos (T=300, x=0.2, VF=0 y VF=1)")
for kv in ([0.0, 0.0], [0.1, 5.0], [0.001, 10.0], [0.5, 2.0]):
    for vf in (0.0, 1.0):
        try:
            r = pp.CalculateEquilibrium(FlashCalculationType.TemperatureVaporFraction, 300.0, vf,
                                        [float(c) for c in comp], [float(k) for k in kv], 1.0)
            w(f"   kv={kv} VF={vf} -> T={float(r.CalculatedTemperature):.4f} "
              f"P={float(r.CalculatedPressure)/1e6:.6f} MPa  "
              f"xL={[round(float(v),5) for v in r.GetLiquidPhase1MoleFractions()]} "
              f"xV={[round(float(v),5) for v in r.GetVaporPhaseMoleFractions()]} "
              f"err={r.ResultException}")
        except Exception as e:
            w(f"   kv={kv} VF={vf} -> EXC {type(e).__name__}: {str(e)[:110]}")

sec("E) mismo TVF en NRTL")
fs2, so2, pp2 = nuevo("NRTL")
for vf in (0.0, 1.0):
    for kv in ([0.0, 0.0], [0.1, 5.0]):
        try:
            r = pp2.CalculateEquilibrium(FlashCalculationType.TemperatureVaporFraction, 300.0, vf,
                                         [float(c) for c in comp], [float(k) for k in kv], 1.0)
            w(f"   VF={vf} kv={kv} -> T={float(r.CalculatedTemperature):.4f} "
              f"P={float(r.CalculatedPressure)/1e6:.6f} MPa "
              f"xL={[round(float(v),5) for v in r.GetLiquidPhase1MoleFractions()]} "
              f"xV={[round(float(v),5) for v in r.GetVaporPhaseMoleFractions()]} "
              f"err={r.ResultException}")
        except Exception as e:
            w(f"   VF={vf} kv={kv} -> EXC {type(e).__name__}: {str(e)[:110]}")
LOG.close()
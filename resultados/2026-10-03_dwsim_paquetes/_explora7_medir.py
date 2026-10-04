"""Exploracion 7: lectura de resultados, bisection bubble/dew, ruta stream y BIP."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "_explora7_medir.txt"), "w", encoding="utf-8")


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

M_A, M_W = 17.03052, 18.015268
mgr = Automation3()


def xmol(wNH3):
    return (wNH3 / M_A) / ((wNH3 / M_A) + ((1 - wNH3) / M_W))


def nuevo_paquete(pname):
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
    so.Phases[0].Properties.temperature = 369.0
    so.Phases[0].Properties.pressure = 1500e3
    so.Phases[0].Properties.massflow = 1.0
    return fs, so, pp


def comp_molar(wNH3):
    x = xmol(wNH3)
    return [float(1 - x), float(x)]


sec("A) composicion: SetOverallCompoundMassFlow + NormalizeOverallMassComposition")
fs, so, pp = nuevo_paquete("Peng-Robinson (PR)")
w("molefrac global:", so.CalcOverallCompMoleFractions())
w("masa molar global:", float(so.GetOverallMolecularWeight()))
w("molarfraction fase0:", so.Phases[0].Properties.molarfraction)

sec("B) flash PT: como leer VF y composiciones de IFlashCalculationResult")
r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, 1500e3, 369.0,
                            comp_molar(0.55), [0.0, 0.0], 1.0)
w("CalculatedTemperature:", r.CalculatedTemperature)
w("CalculatedPressure:", r.CalculatedPressure)
w("BaseMoleAmount:", r.BaseMoleAmount)
w("LiquidPhase1MoleAmounts:", [float(v) for v in r.LiquidPhase1MoleAmounts])
w("VaporPhaseMoleAmounts:", [float(v) for v in r.VaporPhaseMoleAmounts])
w("GetLiquidPhase1MoleFractions():", [float(v) for v in r.GetLiquidPhase1MoleFractions()])
w("GetVaporPhaseMoleFractions():", [float(v) for v in r.GetVaporPhaseMoleFractions()])
w("GetLiquidPhase1MassFractions():", [float(v) for v in r.GetLiquidPhase1MassFractions()])
w("GetVaporPhaseMassFractions():", [float(v) for v in r.GetVaporPhaseMassFractions()])
w("ResultException:", r.ResultException)
w("IterationsTaken:", r.IterationsTaken, "TimeTaken:", r.TimeTaken)


def leer_pt(pp, P, T, comp):
    r = pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, P, T,
                                [float(c) for c in comp], [0.0, 0.0], 1.0)
    n = r.BaseMoleAmount
    vf = float(sum(float(v) for v in r.VaporPhaseMoleAmounts)) / float(n)
    xl = [float(v) for v in r.GetLiquidPhase1MoleFractions()]
    xv = [float(v) for v in r.GetVaporPhaseMoleFractions()]
    return vf, xl, xv, r


w("\nVF a 1500 kPa/369 K, w=0.55:", leer_pt(pp, 1500e3, 369.0, comp_molar(0.55))[:3])

sec("C) bisection: p_burbuja y p_rocio a T=300 K con x=0.2 molar")
T, x = 300.0, [0.8, 0.2]
lo, hi = 1e3, 2e5
for _ in range(80):
    mid = 0.5 * (lo + hi)
    try:
        vf = leer_pt(pp, mid, T, x)[0]
    except Exception as e:
        vf = None
    if vf is None:
        hi = mid
    elif vf <= 1e-12:
        lo = mid
    else:
        hi = mid
w("p_burbuja brackets:", lo / 1e6, hi / 1e6, "MPa (ref 0.040710)")
lo2, hi2 = 1e3, 2e5
for _ in range(80):
    mid = 0.5 * (lo2 + hi2)
    try:
        vf = leer_pt(pp, mid, T, x)[0]
    except Exception:
        vf = None
    if vf is None:
        lo2 = mid
    elif vf >= 1 - 1e-12:
        lo2 = mid
    else:
        hi2 = mid
w("p_rocio brackets:", lo2 / 1e6, hi2 / 1e6, "MPa (ref 0.00437062)")

sec("D) ruta stream: SetFlashSpec('PT') + CalcEquilibrium + enthalpy")
try:
    so.SetFlashSpec("PT")
    w("SpecType tras SetFlashSpec('PT'):", so.SpecType)
    so.Phases[0].Properties.temperature = 369.0
    so.Phases[0].Properties.pressure = 1500e3
    so.Phases[0].Properties.massflow = 1.0
    so.CalcEquilibrium()
    w("AtEquilibrium:", so.AtEquilibrium, "ErrorMessage:", repr(so.ErrorMessage))
    w("GetNumPhases:", so.GetNumPhases())
    for i, ph in enumerate(so.Phases):
        q = ph.Properties
        w(f"  fase {i}: phase={q.phase} T={float(q.temperature):.4f} P={float(q.pressure):.1f} "
          f"w={float(q.massflow):.8g} h={float(q.enthalpy):.6f} VF={float(q.phasefraction):.8g}")
        w("     molarfraction:", [float(v) for v in q.molarfraction])
        w("     massfraction :", [float(v) for v in q.massfraction])
except Exception as e:
    w("EXCEPCION", type(e).__name__, str(e)[:300])

sec("E) enthalpia en dos estados para Delta h (misma ruta)")
try:
    res = {}
    for T2 in (369.0, 300.0):
        so.SetFlashSpec("PT")
        so.Phases[0].Properties.temperature = T2
        so.Phases[0].Properties.pressure = 1500e3
        so.Phases[0].Properties.massflow = 1.0
        so.CalcEquilibrium()
        res[T2] = float(so.Phases[0].Properties.enthalpy)
    w("h:", res, "Delta h =", res[369.0] - res[300.0])
except Exception as e:
    w("EXCEPCION", type(e).__name__, str(e)[:300])

sec("F) BIP: reflexion por paquete (con stream asignado)")
for pname in ("Peng-Robinson (PR)", "Soave-Redlich-Kwong (SRK)", "PRSV2-VL",
              "NRTL", "Modified UNIFAC (NIST)", "Modified UNIFAC (Dortmund)",
              "UNIQUAC", "UNIFAC", "UNIFAC-LL", "Raoult's Law", "CoolProp",
              "Chao-Seader", "Grayson-Streed", "Wilson", "Lee-Kesler-Plucker",
              "PC-SAFT (with Association Support) (.NET Code)", "GERG-2008",
              "Steam Tables (IAPWS-IF97)", "Seawater IAPWS-08", "Black Oil",
              "Peng-Robinson-Stryjek-Vera 2 (PRSV2-M)", "Peng-Robinson / Lee-Kesler (PR/LK)",
              "Peng-Robinson 1978 (PR78)", "Peng-Robinson 1978 (PR78) Advanced",
              "Soave-Redlich-Kwong (SRK) Advanced", "CAPE-OPEN",
              "CoolProp (Incompressible Fluids)", "CoolProp (Incompressible Mixtures)"):
    try:
        f3, s3, p3 = nuevo_paquete(pname)
        tn = p3.GetType().FullName
        ipm = [m for m in dir(p3) if any(k in m.lower() for k in
                                          ("interaction", "bip", "_kos", "unifac", "unequac"))]
        w(f"\n-- {pname}\n   tipo={tn}\n   miembrosBIP={ipm}")
        for m in ipm:
            try:
                v = getattr(p3, m)
                w(f"     {m} = {v}")
            except Exception as e:
                w(f"     {m}: <{type(e).__name__}: {str(e)[:80]}>")
    except Exception as e:
        w(f"\n-- {pname}: EXCEPCION {type(e).__name__}: {str(e)[:200]}")
LOG.close()
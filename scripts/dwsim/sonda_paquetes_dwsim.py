"""Sonda: error de cada paquete de propiedades de DWSIM para NH3-H2O.

Referencias: IAPWS G4-01 Tablas 7/8 (valores de la guia) y el motor del proyecto
(AmmoniaWaterAdapter) para los puntos del caso Elsayed (referencia_motor.json).
Solo mide con lo que trae DWSIM; los ajustes del flash son los mismos del ciclo
(kcs11_elsayed_dwsim.py: mas iteraciones y tolerancia 1e-8).
Salidas en resultados/2026-10-03_dwsim_paquetes/: comparacion.csv, resumen_paquetes.csv.
"""
import csv, json, math, os, sys, time
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "..", "..", "resultados", "2026-10-03_dwsim_paquetes")
REF = json.load(open(os.path.join(OUT, "referencia_motor.json"), encoding="utf-8"))
D = r"D:\DWSIM"
os.chdir(D)
from pythonnet import load
load("netfx")
import clr
sys.path.append(D)
for dll in ("DWSIM.Interfaces", "DWSIM.GlobalSettings", "DWSIM.SharedClasses",
            "DWSIM.Thermodynamics", "DWSIM.UnitOperations", "DWSIM.Automation"):
    clr.AddReference(os.path.join(D, dll + ".dll"))
from DWSIM.Automation import Automation3
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Interfaces.Enums import FlashCalculationType as FCT

M_A, M_W = 17.03052, 18.015268
AJUSTES = {"PHFlash_Maximum_Number_Of_External_Iterations": "1000",
           "PHFlash_Maximum_Number_Of_Internal_Iterations": "1000",
           "PTFlash_Maximum_Number_Of_External_Iterations": "2000",
           "PTFlash_Maximum_Number_Of_Internal_Iterations": "2000",
           "PHFlash_External_Loop_Tolerance": "1e-8", "PHFlash_Internal_Loop_Tolerance": "1e-8",
           "PTFlash_External_Loop_Tolerance": "1e-8", "PTFlash_Internal_Loop_Tolerance": "1e-8"}
# Excluidos sin medir (motivo): no son modelos de mezcla liquido-vapor NH3-H2O.
EXCLUIDOS = {"Steam Tables (IAPWS-IF97)": "agua pura", "Seawater IAPWS-08": "agua de mar (requiere sal)",
             "Black Oil": "petroleo (pseudocomponentes)", "CAPE-OPEN": "requiere paquete externo",
             "CoolProp (Incompressible Fluids)": "fluidos incompresibles",
             "CoolProp (Incompressible Mixtures)": "mezclas incompresibles",
             "GERG-2008": "gas natural; sin NH3 en el modelo"}
mgr = Automation3()


def x_de_w(w):
    return (w / M_A) / (w / M_A + (1 - w) / M_W)


def w_de_x(x):
    return x * M_A / (x * M_A + (1 - x) * M_W)


def nuevo(nombre):
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water"); fs.AddCompound("Ammonia")
    so = fs.AddObject(ObjectType.MaterialStream, 10, 10, "S").GetAsObject()
    so.SetOverallCompoundMassFlow("Water", 0.45); so.SetOverallCompoundMassFlow("Ammonia", 0.55)
    so.NormalizeOverallMassComposition()
    pp = fs.CreateAndAddPropertyPackage(nombre)
    fset = pp.GetType().GetProperty("FlashSettings").GetValue(pp)
    for k in list(fset.Keys):
        if str(k) in AJUSTES:
            fset[k] = AJUSTES[str(k)]
    so.PropertyPackage = pp; pp.CurrentMaterialStream = so
    return so, pp


def pt(pp, P, T, x):
    """Flash P-T -> (VF molar, x_liq NH3, y_vap NH3) en fraccion molar."""
    r = pp.CalculateEquilibrium(FCT.PressureTemperature, P, T, [1 - x, x], [0.0, 0.0], 1.0)
    vf = sum(float(v) for v in r.VaporPhaseMoleAmounts) / float(r.BaseMoleAmount)
    xl = [float(v) for v in r.GetLiquidPhase1MoleFractions()]
    xv = [float(v) for v in r.GetVaporPhaseMoleFractions()]
    return vf, (xl[1] if len(xl) > 1 else float("nan")), (xv[1] if len(xv) > 1 else float("nan"))


def biseccion(f, lo, hi, n=70, log=False):
    """Frontera donde f pasa de False (lo) a True (hi)."""
    for _ in range(n):
        mid = math.sqrt(lo * hi) if log else 0.5 * (lo + hi)
        if f(mid):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def p_burbuja(pp, T, x):     # por encima de p_bub todo liquido (VF=0)
    return biseccion(lambda P: pt(pp, P, T, x)[0] <= 1e-10, 1e2, 6e7, log=True)


def p_rocio(pp, T, x):       # por encima de p_dew aparece liquido (VF<1)
    return biseccion(lambda P: pt(pp, P, T, x)[0] < 1 - 1e-10, 1e2, 6e7, log=True)


def T_burbuja(pp, P, x):     # por encima de T_bub aparece vapor
    return biseccion(lambda T: pt(pp, P, T, x)[0] > 1e-10, 180.0, 640.0)


def T_rocio(pp, P, x):       # por encima de T_dew todo vapor
    return biseccion(lambda T: pt(pp, P, T, x)[0] >= 1 - 1e-10, 180.0, 640.0)


def h_PT(pp, P, T, x):
    """h [kJ/kg] por flash P-T del paquete (CalculatedEnthalpy)."""
    r = pp.CalculateEquilibrium(FCT.PressureTemperature, P, T, [1 - x, x], [0.0, 0.0], 1.0)
    return float(r.CalculatedEnthalpy)


NAN = float("nan")


def seguro(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        FALLOS.append(f"{fn.__name__}{a[1:]}: {str(e).splitlines()[0][:100]}")
        return NAN


FALLOS = []


def medidas(so, pp):
    """[(magnitud, tipo, valor_dwsim, referencia)] con tipo en p/x/T/h/vf."""
    m = []
    for d in REF["tabla7_re"]:
        pb = seguro(p_burbuja, pp, d["T_K"], d["xL_molar_NH3"])
        m.append((f"T7 p_bub x={d['xL_molar_NH3']} T={d['T_K']:.0f}", "p", pb / 1e6, d["p_bub_MPa"]))
        m.append((f"T7 x_v x={d['xL_molar_NH3']} T={d['T_K']:.0f}", "x",
                  seguro(lambda *a: pt(*a)[2], pp, pb * (1 - 1e-6), d["T_K"], d["xL_molar_NH3"]), d["xv_molar_NH3"]))
    for d in REF["tabla8_re"]:
        pr = seguro(p_rocio, pp, d["T_K"], d["xv_molar_NH3"])
        m.append((f"T8 p_dew y={d['xv_molar_NH3']} T={d['T_K']:.0f}", "p", pr / 1e6, d["p_dew_MPa"]))
        m.append((f"T8 x_L y={d['xv_molar_NH3']} T={d['T_K']:.0f}", "x",
                  seguro(lambda *a: pt(*a)[1], pp, pr * (1 + 1e-6), d["T_K"], d["xv_molar_NH3"]), d["xL_molar_NH3"]))
    xb, c = x_de_w(0.55), REF["puntos_ciclo"]
    m.append(("(a) T_bub 273.55 kPa", "T", seguro(T_burbuja, pp, 273.55e3, xb), c["a_Tburbuja_273p55kPa"]["T_K"]))
    m.append(("(b) T_bub 1500 kPa", "T", seguro(T_burbuja, pp, 1500e3, xb), c["b_Tburbuja_1500kPa"]["T_K"]))
    m.append(("(b) T_dew 1500 kPa", "T", seguro(T_rocio, pp, 1500e3, xb), c["b_Trocio_1500kPa"]["T_K"]))
    r = seguro(pt, pp, 1500e3, 369.0, xb)
    vf, xl, xv = r if isinstance(r, tuple) else (NAN, NAN, NAN)
    cc = c["c_flash_1500kPa_369K"]
    wl, wv = w_de_x(xl), w_de_x(xv)
    m.append(("(c) w_liq 1500 kPa 369 K", "x", wl, cc["xL_masica_NH3"]))
    m.append(("(c) w_vap 1500 kPa 369 K", "x", wv, cc["xV_masica_NH3"]))
    m.append(("(c) fraccion vapor masica", "vf", (0.55 - wl) / (wv - wl), cc["vapor_fraction"]))
    dh = seguro(h_PT, pp, 1500e3, 369.0, xb) - seguro(h_PT, pp, 1500e3, 300.0, xb)
    m.append(("(d) dh 369-300 K a 1500 kPa", "h", dh, c["d_delta_h_1500kPa_369K_menos_300K"]["delta_h_kJ_kg"]))
    return m


def main():
    nombres = [str(n) for n in mgr.CreateFlowsheet().GetAvailablePropertyPackages()]
    filas, resumen = [], []
    for nom in nombres:
        if nom in EXCLUIDOS:
            resumen.append(dict(paquete=nom, estado="excluido: " + EXCLUIDOS[nom])); continue
        t0 = time.time()
        try:
            so, pp = nuevo(nom)
            FALLOS.clear()
            ms = medidas(so, pp)
        except Exception as e:
            msg = str(e).replace("\n", " ")[:160]
            resumen.append(dict(paquete=nom, estado="falla: " + msg)); print(nom, "FALLA", msg); continue
        err = {k: [] for k in ("p", "x", "T", "h", "vf")}
        for mag, tipo, v, r in ms:
            ea, er = v - r, (v - r) / r if r else float("nan")
            filas.append(dict(paquete=nom, magnitud=mag, dwsim=v, referencia=r, err_abs=ea, err_rel=er))
            err[tipo].append(abs(er) if tipo in ("p", "h") else abs(ea))
        nan = sum(1 for f in filas if f["paquete"] == nom and f["dwsim"] != f["dwsim"])
        prom = lambda l: (sum(v for v in l if v == v) / n) if (n := sum(1 for v in l if v == v)) else NAN
        resumen.append(dict(paquete=nom, estado="medido", err_rel_p_sat_pct=100 * prom(err["p"]),
                            err_abs_x=prom(err["x"]), err_T_ciclo_K=prom(err["T"]),
                            err_rel_dh_pct=100 * prom(err["h"]), err_abs_vf=prom(err["vf"]),
                            n_nan=nan, segundos=round(time.time() - t0, 1),
                            fallos=" | ".join(dict.fromkeys(FALLOS))[:400]))
        print(nom, {k: round(v, 4) if isinstance(v, float) else v for k, v in resumen[-1].items()}, flush=True)
    with open(os.path.join(OUT, "comparacion.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    campos = ["paquete", "estado", "err_rel_p_sat_pct", "err_abs_x", "err_T_ciclo_K",
              "err_rel_dh_pct", "err_abs_vf", "n_nan", "segundos", "fallos"]
    with open(os.path.join(OUT, "resumen_paquetes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(resumen)


if __name__ == "__main__":
    main()

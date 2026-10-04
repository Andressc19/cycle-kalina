"""Base compartida de los scripts de KCS-11 en DWSIM (`scripts/dwsim/`).

Carga el runtime de DWSIM por pythonnet (netfx, DLLs en `D:\\DWSIM`) y construye el
diagrama KCS-11 con la MISMA topología, puertos y AJUSTES de flash que la plantilla
`kcs11_elsayed_dwsim.py` (que no se modifica). Este módulo NO decide el cierre de los
intercambiadores. P en kPa, T en K, m en kg/s, h en kJ/kg, x = fracción másica NH3."""
from __future__ import annotations

import os, sys  # noqa: E401

D = r"D:\DWSIM"
M_NH3, M_H2O = 17.03052, 18.015268
_TOL = "1e-8"
# Ajustes de flash probados el 2026-10-03 (plantilla): con los de fabrica la valvula
# falla en el flash P-T y la turbina da una FALSA convergencia.
AJUSTES = {"PHFlash_Maximum_Number_Of_External_Iterations": "1000", "PHFlash_Maximum_Number_Of_Internal_Iterations": "1000",
           "PTFlash_Maximum_Number_Of_External_Iterations": "2000", "PTFlash_Maximum_Number_Of_Internal_Iterations": "2000",
           "PHFlash_External_Loop_Tolerance": _TOL, "PHFlash_Internal_Loop_Tolerance": _TOL,
           "PTFlash_External_Loop_Tolerance": _TOL, "PTFlash_Internal_Loop_Tolerance": _TOL}
DLL = ("DWSIM.Interfaces", "DWSIM.GlobalSettings", "DWSIM.SharedClasses",
       "DWSIM.Thermodynamics", "DWSIM.UnitOperations", "DWSIM.Automation")
RT = None  # runtime de DWSIM, cargado una vez
# 6 puntos de TASK_CONTEXT_validacion_dwsim: (etiqueta, x_b, P_alta kPa, T_fuente K,
# P_baja kPa, T_sumidero K, (eps_hrvg, eps_reg, eps_cond)); PINCH_ELSAYED = arranque.
PUNTOS = [
    ("ELSAYED", 0.55, 1500.0, 373.0, 273.5454214157179, 283.0,
     (0.8882023116022899, 0.9380325550010874, 0.9625029043677631)),
    ("KALINA-11", 0.65, 5000.0, 423.0, 704.644595, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-22", 0.80, 5000.0, 394.0, 952.892781, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-21", 0.80, 4000.0, 394.0, 1101.510788, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-01", 0.60, 3000.0, 394.0, 523.749936, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-16", 0.70, 5000.0, 423.0, 890.811268, 283.0, (0.85, 0.80, 0.85)),
]
PINCH_ELSAYED = dict(T1=343.86, T2=369.0, T5=369.0, T6=303.83, T8=304.59, T9=287.0, T10=299.83, x5=0.3873, m5=0.71918)


def runtime():
    """Carga (una sola vez) el runtime de DWSIM por pythonnet/netfx."""
    global RT
    if RT is None:
        os.chdir(D)
        from pythonnet import load
        load("netfx")
        import clr
        sys.path.append(D)
        for dll in DLL:
            clr.AddReference(os.path.join(D, dll + ".dll"))
        from System import Array, Double
        from DWSIM.Automation import Automation3
        from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType as OT
        from DWSIM.Interfaces.Enums import FlashCalculationType as FCT
        RT = dict(System=__import__("System"), Array=Array, Double=Double,
                  Automation3=Automation3, OT=OT, FCT=FCT, clr=clr)
    return RT


def molar(w):
    """Fracción másica de NH3 -> fracción molar de NH3."""
    n_a, n_w = w / M_NH3, (1.0 - w) / M_H2O
    return n_a / (n_a + n_w)


def w_de_xm(xm):
    """Fracción molar de NH3 -> fracción másica de NH3."""
    return xm * M_NH3 / (xm * M_NH3 + (1.0 - xm) * M_H2O)


def diagrama(P_alta, P_baja, x_b, m_b, eta_t, eta_p):
    """Flowsheet KCS-11 completo (topología de la plantilla). P en kPa."""
    rt = runtime()
    System, OT, Automation3 = rt["System"], rt["OT"], rt["Automation3"]
    mgr = Automation3()
    fs = mgr.CreateFlowsheet()
    fs.AddCompound("Water")
    fs.AddCompound("Ammonia")
    pp = fs.CreateAndAddPropertyPackage("Peng-Robinson (PR)")
    pp.Tag = "PR_NH3H2O"
    fset = pp.GetType().GetProperty("FlashSettings").GetValue(pp)
    for k in list(fset.Keys):
        if str(k) in AJUSTES:
            fset[k] = AJUSTES[str(k)]

    def add(t, n, x, y):
        return fs.AddObject(t, x, y, n)

    def c(a, b, i=-1, j=-1):
        fs.ConnectObjects(a.GraphicObject, b.GraphicObject, i, j)

    bomba = add(OT.Pump, "BOMBA", 100, 400); reg = add(OT.HeatExchanger, "REGENERADOR", 300, 250)
    hrvg = add(OT.Heater, "HRVG", 450, 100); sep = add(OT.Vessel, "SEPARADOR", 620, 100)
    turb = add(OT.Expander, "TURBINA", 820, 60); val = add(OT.Valve, "VALVULA", 500, 400)
    absb = add(OT.Mixer, "ABSORBEDOR", 820, 400); cond = add(OT.Cooler, "CONDENSADOR", 650, 520)
    rec = add(OT.OT_Recycle, "REC_S5", 560, 250)
    S = {n: add(OT.MaterialStream, n, x, y) for n, x, y in (
        ("S9", 30, 400), ("S10", 200, 330), ("S1", 380, 170), ("S2", 540, 100), ("S3", 740, 40),
        ("S4", 900, 250), ("S5calc", 620, 200), ("S5", 470, 250), ("S6", 400, 400), ("S7", 650, 400),
        ("S8", 900, 520), ("S9c", 500, 600))}
    E = {n: add(OT.EnergyStream, n, x, y) for n, x, y in (
        ("W_bomba", 100, 500), ("Q_hrvg", 450, 20), ("W_turb", 900, 20), ("Q_cond", 650, 620))}
    c(S["S9"], bomba); c(bomba, S["S10"]); c(E["W_bomba"], bomba)
    c(S["S10"], reg, 0, 0); c(reg, S["S1"], 0, 0)      # lado frio: puerto 0
    c(S["S5"], reg, 0, 1); c(reg, S["S6"], 1, 0)       # lado caliente: puerto 1
    c(S["S1"], hrvg); c(hrvg, S["S2"]); c(E["Q_hrvg"], hrvg)
    c(S["S2"], sep, 0, 0); c(sep, S["S3"], 0, 0); c(sep, S["S5calc"], 1, 0)
    c(S["S5calc"], rec); c(rec, S["S5"])
    c(S["S3"], turb); c(turb, S["S4"]); c(turb, E["W_turb"])
    c(S["S6"], val); c(val, S["S7"])
    c(S["S4"], absb, 0, 0); c(S["S7"], absb, 0, 1); c(absb, S["S8"])
    c(S["S8"], cond); c(cond, S["S9c"]); c(cond, E["Q_cond"])

    def em(obj, nombre):
        return System.Enum.Parse(obj.CalcMode.GetType(), nombre)

    B = bomba.GetAsObject(); B.CalcMode = em(B, "OutletPressure")
    B.Pout = P_alta * 1e3; B.Eficiencia = 100.0 * eta_p
    T = turb.GetAsObject(); T.CalcMode = em(T, "OutletPressure")
    T.POut = P_baja * 1e3; T.AdiabaticEfficiency = 100.0 * eta_t
    V = val.GetAsObject(); V.CalcMode = em(V, "OutletPressure")
    V.OutletPressure = P_baja * 1e3
    H = hrvg.GetAsObject(); H.CalcMode = em(H, "HeatAdded"); H.DeltaP = 0.0
    C = cond.GetAsObject(); C.CalcMode = em(C, "HeatRemoved"); C.DeltaP = 0.0
    R = reg.GetAsObject()
    # Regenerador en modo PinchPoint (MITA = T6 - T10), igual que la plantilla. Sondas
    # `_dbg_regen.py`/`_dbg_eps.py` (2026-10-03): `CalcTempHotOut` y `ThermalEfficiency`
    # NO calculan el lado frio (dejan T1 = 298.15 K; `OverallCoefficient` = 0).
    R.CalculationMode = System.Enum.Parse(R.CalculationMode.GetType(), "PinchPoint")
    R.MITA = 4.0
    rec.GetAsObject().MaximumIterations = 60
    return dict(mgr=mgr, fs=fs, pp=pp, S=S, E=E, P_alta=P_alta, P_baja=P_baja, x_b=x_b, m_b=m_b,
                _FCT=rt["FCT"], _Array=rt["Array"], _Double=rt["Double"],
                eq=dict(bomba=B, hrvg=H, reg=R, turb=T, val=V, cond=C), rec=rec)


def fijar(d, nombre, T, P_kPa, w, m):
    """Fija T [K], P [kPa], w (NH3 masica) y m de una corriente. OJO: la API usa
    **Pa** en `Properties.pressure`, `Pout` y `OutletPressure`, y **%** en `Eficiencia`."""
    st = d["S"][nombre].GetAsObject()
    xm = molar(w)
    st.SetOverallComposition(d["_Array"][d["_Double"]]([1.0 - xm, xm]))
    p = st.Phases[0].Properties
    p.temperature, p.pressure, p.massflow = float(T), float(P_kPa) * 1e3, float(m)


def props(d, nombre):
    """(T [K], P [kPa], m [kg/s], w NH3 másica, h [kJ/kg], VF molar)."""
    st = d["S"][nombre].GetAsObject()
    p = st.Phases[0].Properties
    w = w_de_xm(molar(st.Phases[0].Compounds["Ammonia"].MassFraction))
    vf = st.Phases[2].Properties.molarfraction
    return dict(T=float(p.temperature), P=float(p.pressure) / 1e3, m=float(p.massflow), w=w,
                h=float(p.enthalpy) if p.enthalpy is not None else float("nan"),
                vf=float("nan") if vf is None else float(vf))


def h_PT(d, P_kPa, T, w):
    """h [kJ/kg] del PR en (P, T, w). Único flash directo fiable (el P-H lanza
    AggregateException); misma base de h que las corrientes (rel. 6e-9 contra S9)."""
    pp = d["pp"]
    pp.CurrentMaterialStream = d["S"]["S1"].GetAsObject()
    xm = molar(w)
    return float(pp.CalculateEquilibrium(d["_FCT"].PressureTemperature, P_kPa * 1e3, float(T),
                                         [1.0 - xm, xm], [0.0, 0.0], 1.0).CalculatedEnthalpy)


def T_de_h(d, P_kPa, h, w, T_lo, T_hi, n=34):
    """Invierte h(T) -> T por bisección sobre flashes P-T (el flash P-H de este PR
    falla en los estados del ciclo, 2026-10-03). h(T) es monótona; n=34 -> 1e-8 K."""
    h_lo, h_hi = h_PT(d, P_kPa, T_lo, w), h_PT(d, P_kPa, T_hi, w)
    if not min(h_lo, h_hi) <= h <= max(h_lo, h_hi):
        raise ValueError("h=%.2f fuera de [%.2f, %.2f] en P=%.0f kPa, w=%.4f" % (h, h_lo, h_hi, P_kPa, w))
    for _ in range(n):
        T_m = 0.5 * (T_lo + T_hi)
        try:
            h_m = h_PT(d, P_kPa, T_m, w)
        except Exception:                      # T suelta donde falla el flash P-T
            T_m += 1e-4; h_m = h_PT(d, P_kPa, T_m, w)  # (2026-10-03)
        if h_m < h:
            T_lo = T_m
        else:
            T_hi = T_m
    return 0.5 * (T_lo + T_hi)


def energia(d, nombre):
    """Caudal de energía [kW] que DWSIM reporta; `nan` si no lo rellenó."""
    v = d["E"][nombre].GetAsObject().EnergyFlow
    return float("nan") if v is None else float(v)


def sin_calcular(d):
    """Equipos que DWSIM dejó sin calcular. `CalculateFlowsheet2` puede devolver cero
    errores con media planta sin calcular (KALINA-11, 2026-10-03): hay que mirarlo."""
    malos = ["%s sin calcular: %s" % (k, (o.ErrorMessage or "").splitlines()[0][:80] if o.ErrorMessage else "")
             for k, o in d["eq"].items() if not o.Calculated]
    return malos + ([] if d["rec"].GetAsObject().Converged else ["reciclo S5 sin converger"])


def resolver(d):
    """Resuelve el flowsheet; devuelve la lista de errores (vacía si ok)."""
    return list(d["mgr"].CalculateFlowsheet2(d["fs"]) or [])
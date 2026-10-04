"""KCS-11 con CIERRE POR EFECTIVIDAD resuelto dentro de DWSIM (Peng-Robinson).

Misma topología que la plantilla `kcs11_elsayed_dwsim.py` (que no se modifica), pero
las tres especificaciones de intercambio se imponen con las MISMAS ecuaciones del
solver del proyecto (`src/components/{hrvg,regenerador,condensador}.py`):
    h2 = h1 + eps_hrvg*(h(P_alta,T_fuente,x_b) - h1)        [HRVG]
    h6 = h5 - eps_reg *(h5 - h(P_alta,T10,x5))              [Regenerador]
    h9 = h8 - eps_cond*(h8 - h(P_baja,T_sumidero,x8))       [Condensador]
Las efectividades se imponen como temperaturas de salida (T2, T9 por inversion h->T;
regenerador en PinchPoint con MITA = T6 - T10); lazo externo de sustitucion sucesiva
sub-relajada (LAMB) sobre el residuo de esas tres specs. S9 se fija a la misma T9. Arranca de un estado fisico conocido (`_arranque`), no de estimados
arbitrarios. Equivalencias medidas por las sondas `_dbg_regen.py`/`_dbg_eps.py`
(2026-10-03): `DeltaQ` va en **kW** (452.458 kW -> T2 = 369.002 K) y el regenerador
solo resuelve el lado frio en modo `PinchPoint` (MITA = T6 - T10); `CalcTempHotOut`
y `ThermalEfficiency` lo dejan en 298.15 K.

Uso:  python -u scripts/dwsim/kcs11_efectividad_dwsim.py [humo|puntos]
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kcs11_dwsim_base as B          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "resultados", "2026-10-03_validacion_dwsim")
MOTOR_CSV = os.path.join(OUT, "motor_puntos.csv")
M_B, TOL_K, MAX_ITER, LAMB, N_REINT = 1.0, 1e-3, 100, 0.7, 10


def _arranque(et):
    """Estado fisico conocido con el que arranca el lazo (T y x; las entalpias las
    recalcula el PR): fila `real` de la Etapa 2, o el pinch de la plantilla."""
    if os.path.exists(MOTOR_CSV):
        with open(MOTOR_CSV, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["etiqueta"] == et and r["motor"] == "real" and r["eta"]:
                    return (dict((k, float(r[k])) for k in
                                 ("T1", "T2", "T5", "T6", "T8", "T9", "T10", "x5", "m5")),
                            "motor_puntos.csv:real")
    if et == "ELSAYED":
        return dict(B.PINCH_ELSAYED), "pinch kcs11_elsayed_dwsim.py"
    raise KeyError("sin estado fisico de partida para %s: falta motor_puntos.csv" % et)


def resolver_dwsim(P_alta, P_baja, T_fuente, T_sumidero, x_b, m_b, eta_t, eta_p,
                   eps_hrvg, eps_reg, eps_cond, arranque=None, fuente_arr=""):
    """Resuelve el ciclo en DWSIM con las tres specs por efectividad.

    Las efectividades se traducen a temperaturas de salida (misma ecuacion, otra
    forma de imponerla): T2 y T9 por inversion h->T (biseccion sobre flash P-T del
    mismo PR) y el regenerador en PinchPoint con MITA = T6 - T10. S9 (corte del
    ciclo) se fija a la misma T9 que el condensador, asi el corte cierra solo.
    Converge cuando el residuo de las tres specs es < TOL_K. Devuelve ``convergio``,
    ``iteraciones``, ``eta``, ``Wt``, ``Wp``, ``Qi``, ``Qout``, ``T1..T10``, ``x3``,
    ``x5``, ``m3``, ``m5``, ``equipo`` (kW), ``cierre`` y las efectividades
    resultantes; si DWSIM devuelve errores, ``convergio=False`` y ``error``.
    (2026-10-03: la version por calor + S9 sustituido oscilaba 60 iteraciones.)
    """
    a = arranque
    d = B.diagrama(P_alta, P_baja, x_b, m_b, eta_t, eta_p)
    sysm = B.runtime()["System"]
    for k in ("hrvg", "cond"):
        o = d["eq"][k]
        o.CalcMode = sysm.Enum.Parse(o.CalcMode.GetType(), "OutletTemperature")
    h2max = B.h_PT(d, P_alta, T_fuente, x_b)          # referencias, mismo PR
    T2, T9, mita = a["T2"], a["T9"], max(a["T6"] - a["T10"], 0.05)
    B.fijar(d, "S5", a["T5"], P_alta, a["x5"], a["m5"])
    hist, errs, fallos = [], [], []
    conv, rein = False, 0
    for it in range(1, MAX_ITER + 1):
        for k in range(N_REINT + 1):       # reintento: el flash P-T de PR falla en T
            dl = 0.05 * k * (-1) ** k      # sueltas de liquido comprimido (2026-10-03)
            T2, T9, mita = T2 + dl, T9 + dl, mita + dl
            d["eq"]["hrvg"].OutletTemperature, d["eq"]["cond"].OutletTemperature = T2, T9
            d["eq"]["reg"].MITA = mita
            B.fijar(d, "S9", T9, P_baja, x_b, m_b)
            errs = [str(e).splitlines()[0][:90] for e in B.resolver(d)] + B.sin_calcular(d)
            if not errs:
                break
            rein += 1
        if errs:
            break
        S1, S5, S8, S10 = (B.props(d, k) for k in ("S1", "S5", "S8", "S10"))
        h9min = B.h_PT(d, P_baja, T_sumidero, S8["w"])   # x8, como el proyecto
        h6min = B.h_PT(d, P_alta, S10["T"], S5["w"])     # x5, como el proyecto
        try:
            T2n = B.T_de_h(d, P_alta, S1["h"] + eps_hrvg * (h2max - S1["h"]), x_b, S1["T"], T_fuente)
            T9n = B.T_de_h(d, P_baja, S8["h"] - eps_cond * (S8["h"] - h9min), S8["w"], T_sumidero, S8["T"])
            T6n = B.T_de_h(d, P_alta, S5["h"] - eps_reg * (S5["h"] - h6min), S5["w"], S10["T"], S5["T"])
        except ValueError as exc:
            fallos.append("it%d %s" % (it, exc))
            errs = ["inversion h->T: %s" % exc]
            break
        mitan = T6n - S10["T"]
        res = max(abs(T2n - T2), abs(T9n - T9), abs(mitan - mita))
        hist.append((it, S1["T"], T2, T9, mita, res))
        if res < TOL_K:
            conv = True
            break
        T2 += LAMB * (T2n - T2); T9 += LAMB * (T9n - T9); mita += LAMB * (mitan - mita)
    if errs:
        return dict(convergio=False, iteraciones=it, relajaciones=rein, hist=hist,
                    error="; ".join(errs), fallos=fallos)
    S1, S2, S3, S4, S5, S6, S7, S8, S9, S9c, S10 = (B.props(d, k) for k in (
        "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S9c", "S10"))
    Wt, Wp = S3["m"] * (S3["h"] - S4["h"]), m_b * (S10["h"] - S9["h"])
    Qi, Qout = m_b * (S2["h"] - S1["h"]), S8["m"] * (S8["h"] - S9c["h"])
    eh = (S2["h"] - S1["h"]) / (h2max - S1["h"])
    er = (S5["h"] - S6["h"]) / (S5["h"] - h6min)
    ec = (S8["h"] - S9c["h"]) / (S8["h"] - h9min)
    eq = dict((k, B.energia(d, e) - v) for k, e, v in
              (("TURBINA", "W_turb", Wt), ("BOMBA", "W_bomba", Wp), ("HRVG", "Q_hrvg", Qi), ("CONDENSADOR", "Q_cond", Qout)))
    return dict(convergio=conv, iteraciones=it, relajaciones=rein, hist=hist,
                eta=(Wt - Wp) / Qi, Wt=Wt, Wp=Wp, Qi=Qi, Qout=Qout, Wnet=Wt - Wp,
                cierre=Qi + Wp - Qout - Wt, T1=S1["T"], T2=S2["T"], T3=S3["T"],
                T4=S4["T"], T5=S5["T"], T6=S6["T"], T7=S7["T"], T8=S8["T"],
                T9=S9c["T"], T10=S10["T"], x3=S3["w"], x5=S5["w"], m3=S3["m"],
                m5=S5["m"], x8=S8["w"], dx9=S9c["w"] - x_b, eps_hrvg_res=eh, eps_reg_res=er, eps_cond_res=ec,
                d_eps_hrvg=eh - eps_hrvg, d_eps_reg=er - eps_reg, d_eps_cond=ec - eps_cond,
                equipo=eq, error="", eps_pedidas=(eps_hrvg, eps_reg, eps_cond),
                fallos=fallos, arranque=fuente_arr, _d=d)   # _d: diagrama, para leer corrientes


def _resumen(et, r):
    """Imprime estados, energías, verificacion por equipo y efectividades."""
    if r.get("error"):
        print("%-10s NO CONVERGE (iter=%s) -> %s" % (et, r["iteraciones"], r["error"]), flush=True)
        return
    print("%-10s convergio=%s iter=%s relajaciones=%s arranque=%s"
          % (et, r["convergio"], r["iteraciones"], r["relajaciones"], r["arranque"]), flush=True)
    print("   T: " + " ".join("T%d=%.3f" % (k, r["T%d" % k]) for k in range(1, 11)))
    print("   x3=%.5f x5=%.5f x8=%.5f dx9=%+.5f m3=%.5f m5=%.5f"
          % (r["x3"], r["x5"], r["x8"], r["dx9"], r["m3"], r["m5"]))
    print("   Wt=%.3f Wp=%.4f Qi=%.3f Qout=%.3f Wnet=%.3f kW  eta=%.6f (%.3f %%)  cierre=%+.4f kW"
          % (r["Wt"], r["Wp"], r["Qi"], r["Qout"], r["Wnet"], r["eta"], r["eta"] * 100.0, r["cierre"]))
    print("   equipo (equipo - corrientes, kW): " + "  ".join("%s=%+.4f" % kv for kv in r["equipo"].items()))
    print("   eps pedida -> resultante: " + "  ".join(
        "%s %.6f -> %.6f (d=%+.1e)" % (k, e, r["eps_%s_res" % k], r["d_eps_%s" % k])
        for k, e in zip(("hrvg", "reg", "cond"), r["eps_pedidas"])))
    for f in r["fallos"][:3]:
        print("   flash P-H fallido: " + f)


def humo():
    """Prueba de humo: caso Elsayed con los eps calibrados."""
    et, x_b, Pa, Tf, Pb, Ts, eps = B.PUNTOS[0]
    d = B.diagrama(Pa, Pb, x_b, M_B, 0.80, 0.80)
    B.fijar(d, "S9", 373.0, Pa, 0.55, M_B)      # base de h PR: corriente S9
    B.resolver(d)
    h_c, h_f = B.props(d, "S9")["h"], B.h_PT(d, Pa, 373.0, 0.55)
    print("Base de entalpia PR en (P_alta, 373 K, x=0.55): h(corriente) - "
          "h(flash PR) = %.3e kJ/kg (rel %.2e)" % (h_c - h_f,
                                                   abs(h_c - h_f) / abs(h_c)))
    if abs(h_c - h_f) / abs(h_c) > 1e-5:
        print("ABORTO: el flash PR y la corriente no comparten base de h")
        return
    arr, fte = _arranque(et)
    t0 = time.perf_counter()
    r = resolver_dwsim(Pa, Pb, Tf, Ts, x_b, M_B, 0.80, 0.80, *eps,
                       arranque=arr, fuente_arr=fte)
    print("=== PRUEBA DE HUMO %s (%.1f s) ===" % (et, time.perf_counter() - t0))
    _resumen(et, r)
    print("   historial (it, T1, T2spec, T9spec, MITA, residuo) [K]:")
    for h in r["hist"]:
        print("     %3d %10.4f %10.4f %10.4f %8.4f %10.2e" % h)


def puntos():
    """Resuelve los 6 puntos y escribe dwsim_puntos.csv."""
    cab = ["etiqueta", "x_b", "P_alta", "T_fuente", "P_baja", "T_sumidero", "eps_hrvg", "eps_reg", "eps_cond",
           "convergio", "iteraciones", "relajaciones", "eta", "Wnet", "Qi", "Wt", "Wp", "Qout", "cierre_kW",
           "x3", "x5", "x8", "dx9", "m3", "m5", "eps_hrvg_res", "eps_reg_res", "eps_cond_res",
           "d_eps_hrvg", "d_eps_reg", "d_eps_cond", "arranque", "error", "flash_fallos", "segundos"] \
        + ["T%d" % k for k in range(1, 11)] + ["dif_" + k for k in ("TURBINA", "BOMBA", "HRVG", "CONDENSADOR")]
    filas = []
    for et, x_b, Pa, Tf, Pb, Ts, eps in B.PUNTOS:
        arr, fte = _arranque(et)
        t0 = time.perf_counter()
        r = resolver_dwsim(Pa, Pb, Tf, Ts, x_b, M_B, 0.80, 0.80, *eps, arranque=arr, fuente_arr=fte)
        f = dict(etiqueta=et, x_b=x_b, P_alta=Pa, T_fuente=Tf, P_baja=Pb, T_sumidero=Ts,
                 eps_hrvg=eps[0], eps_reg=eps[1], eps_cond=eps[2],
                 segundos=round(time.perf_counter() - t0, 1), flash_fallos="; ".join(r["fallos"])[:300])
        f["cierre_kW"] = r.get("cierre", "")
        f.update(dict((k, v) for k, v in r.items() if k not in ("hist", "equipo", "fallos")))
        f.update(dict(("dif_" + k, v) for k, v in r.get("equipo", {}).items()))
        filas.append(f)
        _resumen(et, r)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "dwsim_puntos.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    print("-> %s" % os.path.join(OUT, "dwsim_puntos.csv"))


if __name__ == "__main__":
    humo() if (sys.argv[1] if len(sys.argv) > 1 else "puntos") == "humo" else puntos()
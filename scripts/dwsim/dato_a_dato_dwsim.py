"""Ciclo KALINA (argumento: etiqueta) en DWSIM-PR con el cierre por efectividad del
proyecto (`kcs11_efectividad_dwsim.resolver_dwsim`). Arranca desde los estados del motor
del proyecto para el mismo ciclo (motor_<etiqueta>.json, de `dato_a_dato_motor.py`).
Guarda 10 estados (T, P, h, x, m, VF molar), energías y dos referencias de h con la
misma composición: h0 = h_PR(P0, T0, x) y h0L = h_PR(P_alta, T0, x) (principal).
Python global (pythonnet). Salida: resultados/2026-10-03_dato_a_dato/dwsim_<etiqueta>.json
"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import _kcs11_dwsim_base as B           # noqa: E402
import kcs11_efectividad_dwsim as K     # noqa: E402

OUT = os.path.join(AQUI, "..", "..", "resultados", "2026-10-03_dato_a_dato")
MAPA = {1: "S1", 2: "S2", 3: "S3", 4: "S4", 5: "S5", 6: "S6", 7: "S7", 8: "S8", 9: "S9c", 10: "S10"}
CLAVES = ("P_alta", "P_baja", "T_fuente", "T_sumidero", "x_b", "m_b", "eta_t", "eta_p",
          "eps_hrvg", "eps_reg", "eps_cond")


def correr(et):
    mo = json.load(open(os.path.join(OUT, "motor_%s.json" % et)))
    P, T0, P0, e = mo["punto"], mo["T0"], mo["P0"], mo["estados"]
    arr = dict(("T%d" % k, e[str(k)]["T"]) for k in (1, 2, 5, 6, 8, 9, 10))
    arr.update(x5=e["5"]["x"], m5=e["5"]["m"])
    r = K.resolver_dwsim(*[P[k] for k in CLAVES], arranque=arr, fuente_arr="motor_%s.json" % et)
    if r.get("error"):
        json.dump(dict(etiqueta=et, convergio=False, error=r["error"]),
                  open(os.path.join(OUT, "dwsim_%s.json" % et), "w"), indent=1)
        print(et, "NO CONVERGE:", r["error"]); return
    d = r.pop("_d")
    est = {}
    for k, n in MAPA.items():
        q = B.props(d, n)
        est[str(k)] = dict(T=q["T"], P=q["P"], h=q["h"], x=q["w"], m=q["m"], vf_molar=q["vf"],
                           h0=B.h_PT(d, P0, T0, q["w"]), h0L=B.h_PT(d, P["P_alta"], T0, q["w"]))
    res = dict(etiqueta=et, punto=P, T0=T0, P0=P0, estados=est,
               **{k: r[k] for k in ("convergio", "iteraciones", "relajaciones", "eta", "Wt", "Wp", "Qi",
                                     "Qout", "Wnet", "cierre", "eps_hrvg_res", "eps_reg_res", "eps_cond_res")},
               equipo=r["equipo"])
    json.dump(res, open(os.path.join(OUT, "dwsim_%s.json" % et), "w"), indent=1)
    print(et, "convergio", r["convergio"], "iter", r["iteraciones"], "eta", r["eta"], "cierre",
          round(r["cierre"], 5), "equipo", {k: round(v, 5) for k, v in r["equipo"].items()},
          "deps", [round(r["eps_%s_res" % k] - P["eps_" + k], 6) for k in ("hrvg", "reg", "cond")], flush=True)


if __name__ == "__main__":
    for et in sys.argv[1:]:
        correr(et)

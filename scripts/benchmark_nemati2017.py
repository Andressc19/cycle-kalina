"""Benchmark contra una segunda fuente independiente: Nemati, Nami, Ranjbar & Yari (2017),
"A comparative thermodynamic analysis of ORC and Kalina cycles for waste heat recovery: a
case study for CGAM cogeneration system", Case Studies in Thermal Engineering 9, 1-13,
doi:10.1016/j.csite.2016.11.003 (Univ. de Tabriz; EES). Papers/comparativa kalian y ORC...pdf

Su KCS11 (Fig. 1b, §2.2) tiene la topología de este repo. Datos de su Tabla 5 (corrientes
12-20) y §2.3 (η_t = 0.85, η_p = 0.75, agua de enfriamiento a ambiente 298.15 K). El paper no
da η ni potencia del Kalina para ese caso: se comparan ESTADOS.

1) Pruebas directas de propiedades (independientes del cierre del ciclo):
   - equilibrio L-V a (5000 kPa, 415 K): x_vapor 0.9543, x_liquido 0.5173 (corrientes 13, 14)
   - T de burbuja a (1061 kPa, x=0.90): 303.15 K (corriente 18, salida del condensador)
2) Ciclo: efectividades calibradas EN UN PASO desde sus temperaturas (T2=415, T6=336.1,
   T9=303.15 K) con este motor, igual que la validación Elsayed (§7). Se comparan los estados
   que el cierre NO fija: T1, T4, T8, T10, x3, x5 y el reparto de caudal del separador.
Motor: AmmoniaWaterAdapter (motor real). Salida: resultados/2026-10-03_benchmark_nemati/
"""
import json
import os
import sys
import time

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, REPO)
from src.cycle_solver import resolver_ciclo                          # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402

OUT = os.path.join(REPO, "resultados", "2026-10-03_benchmark_nemati")
M_A, M_W = 17.03052, 18.015268
PA, PB, XB = 5000.0, 1061.0, 0.90
T_FUENTE, T_SUMIDERO = 429.0, 298.15          # gas a la entrada del evaporador (corr. 7); agua (21)
# Tabla 5 de Nemati et al. (2017), en la numeración de este repo
NEMATI = {"1": dict(P=5000, T=314.4, n=5.848, x=0.90), "2": dict(P=5000, T=415.0, n=5.848, x=0.90),
          "3": dict(P=5000, T=415.0, n=5.121, x=0.9543), "4": dict(P=1061, T=341.5, n=5.121, x=0.9543),
          "5": dict(P=5000, T=415.0, n=0.7272, x=0.5173), "6": dict(P=5000, T=336.1, n=0.7272, x=0.5173),
          "8": dict(P=1061, T=340.0, n=5.848, x=0.90), "9": dict(P=1061, T=303.15, n=5.848, x=0.90),
          "10": dict(P=5000, T=304.3, n=5.848, x=0.90)}


def masa_molar(w):
    xm = (w / M_A) / (w / M_A + (1 - w) / M_W)
    return xm * M_A + (1 - xm) * M_W


def main():
    os.makedirs(OUT, exist_ok=True)
    be = AmmoniaWaterAdapter(x=XB)
    res = dict(fuente="Nemati et al. 2017, Tabla 5", nemati=NEMATI)
    # 1) pruebas directas
    wl, wv = be.equilibrio_liquido_vapor(PA, 415.0)
    res["VLE_5000kPa_415K"] = dict(x_liq_motor=wl, x_liq_nemati=0.5173, x_vap_motor=wv, x_vap_nemati=0.9543)
    res["Tbub_1061kPa_x090"] = dict(motor=be.bubble_point(PB, XB), nemati=303.15)
    print(res["VLE_5000kPa_415K"], res["Tbub_1061kPa_x090"], flush=True)
    # reparto del separador en masa según Nemati (caudales molares × masa molar)
    m = {k: v["n"] * masa_molar(v["x"]) for k, v in NEMATI.items()}
    res["fraccion_vapor_masica_nemati"] = m["3"] / m["2"]
    # 2) calibración de un paso: ε desde sus temperaturas, con este motor
    h = lambda P, T, x: be.h(P, T=T, x=x)                                     # noqa: E731
    x5 = NEMATI["5"]["x"]
    eps_hrvg = (h(PA, 415.0, XB) - h(PA, 314.4, XB)) / (h(PA, T_FUENTE, XB) - h(PA, 314.4, XB))
    eps_reg = (h(PA, 415.0, x5) - h(PA, 336.1, x5)) / (h(PA, 415.0, x5) - h(PA, 304.3, x5))
    eps_cond = (h(PB, 340.0, XB) - h(PB, 303.15, XB)) / (h(PB, 340.0, XB) - h(PB, T_SUMIDERO, XB))
    res["eps_calibradas"] = dict(hrvg=eps_hrvg, reg=eps_reg, cond=eps_cond)
    print("eps", res["eps_calibradas"], flush=True)
    t0 = time.perf_counter()
    r = resolver_ciclo(be, P_alta=PA, P_baja=PB, T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, x_b=XB,
                       m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond)
    e = r["estados"]
    res["ciclo_motor"] = {str(k): dict(T=e["e%d" % k].T, P=e["e%d" % k].P, x=e["e%d" % k].x,
                                       m=e["e%d" % k].m, q=e["e%d" % k].q) for k in range(1, 11)}
    res["ciclo_motor"].update(eta=r["eta"], Wnet=r["Wnet"], Qi=r["Qi"], segundos=time.perf_counter() - t0)
    json.dump(res, open(os.path.join(OUT, "benchmark_nemati.json"), "w"), indent=1)
    print("%-3s %9s %9s %8s | %8s %8s" % ("e", "T_nemati", "T_motor", "dT", "x_nem", "x_mot"))
    for k, v in NEMATI.items():
        c = res["ciclo_motor"][k]
        print("%-3s %9.2f %9.2f %+8.2f | %8.4f %8.4f" % (k, v["T"], c["T"], c["T"] - v["T"], v["x"], c["x"]))
    print("fraccion vapor masica: nemati %.4f  motor %.4f" % (res["fraccion_vapor_masica_nemati"],
                                                            res["ciclo_motor"]["3"]["m"]))
    print("eta motor %.4f  Wnet %.3f kW/(kg/s)  Qi %.2f" % (r["eta"], r["Wnet"], r["Qi"]))


if __name__ == "__main__":
    main()

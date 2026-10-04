"""Ciclo KALINA (argumento: etiqueta, p. ej. KALINA-03) con el solver del proyecto (motor real AmmoniaWaterAdapter): 10 estados
(T, P, h, s, x, m, q, fase), energías y h0 = h(P0, T0, x_estado) (estado muerto). Con el
h0L = h(P_alta, T0, x_estado) (referencia líquida). Usar con el .venv.
Salida: resultados/2026-10-03_dato_a_dato/motor_<etiqueta>.json
"""
import json, os, sys, time
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, REPO)
from src.cycle_solver import resolver_ciclo                        # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402

# Ciclos KALINA con P_alta <= 3000 kPa (zona donde DWSIM-PR resuelve), de
# resultados/2026-09-27_teqp_verificado/regresion_22.csv: (x_b, T_fuente, P_baja).
CICLOS = {"KALINA-01": (0.60, 394.0, 523.749936), "KALINA-03": (0.60, 423.0, 752.471907),
          "KALINA-06": (0.65, 394.0, 687.98037), "KALINA-09": (0.65, 423.0, 967.9991),
          "KALINA-12": (0.70, 394.0, 868.092712), "KALINA-17": (0.75, 394.0, 1060.024938)}


def punto(et):
    x_b, Tf, Pb = CICLOS[et]
    return dict(P_alta=3000.0, P_baja=Pb, T_fuente=Tf, T_sumidero=283.0, x_b=x_b, m_b=1.0,
                eta_t=0.80, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85)


PUNTO = punto("KALINA-01")
T0, P0 = 300.032917, 101.325
OUT = os.path.join(REPO, "resultados", "2026-10-03_dato_a_dato")

def correr(et):
    """Resuelve el ciclo `et` y guarda motor_<et>.json con h0 y h0L por estado."""
    P = punto(et)
    be = AmmoniaWaterAdapter(x=P["x_b"])
    t0 = time.perf_counter()
    r = resolver_ciclo(be, **P)
    est = {}
    for k in range(1, 11):
        e = r["estados"]["e%d" % k]
        est[str(k)] = dict(T=e.T, P=e.P, h=e.h, s=e.s, x=e.x, m=e.m, q=e.q, fase=e.fase,
                           h0=be.h(P0, T=T0, x=e.x), h0L=be.h(P["P_alta"], T=T0, x=e.x))
    res = dict(etiqueta=et, punto=P, T0=T0, P0=P0, estados=est, segundos=time.perf_counter() - t0,
               **{k: r[k] for k in ("Qi", "Qout", "Wt", "Wp", "Qreg", "Wnet", "eta")})
    json.dump(res, open(os.path.join(OUT, "motor_%s.json" % et), "w"), indent=1)
    print(et, "eta", r["eta"], "t", res["segundos"], flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    correr(sys.argv[1])

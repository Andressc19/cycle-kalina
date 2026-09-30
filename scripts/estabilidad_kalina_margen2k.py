"""Estabilidad de los 22 puntos KALINA de barrido_margen2k.csv — tarea
2026-09-24-rama-turbina-y-estabilidad, Parte 2.

Para cada punto KALINA (x_b, P_alta, T_fuente con su P_baja=P* de la tarea
margen2k) se resuelve el ciclo con TeqpAdapter en P*−0.5, P* y P*+0.5 kPa y se
registra eta, Wnet, h4, T4, margen O2 y clasificacion.

El punto es ESTABLE si |max(eta)-min(eta)| <= 0.01, |max(h4)-min(h4)| <= 10
kJ/kg y la clasificacion no cambia entre las 3 evaluaciones. Las excepciones
por evaluacion se capturan y reportan (nunca abortan ni se ocultan): una
evaluacion fallida marca el punto inestable.

Margen O2 con la receta exacta de la tarea margen2k: T9_amb = re-solucion del
condensador a max(T_SUMIDERO,T_AMB_DISENO)=283.15 K; T_bur = bubble_point.

No modifica src/ ni archivos existentes; escribe solo en
resultados/2026-09-24_rama_turbina/estabilidad_kalina.csv.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.components import condensador  # noqa: E402
from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

SRC = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
OUT_DIR = REPO / "resultados" / "2026-09-24_rama_turbina"
OUT = OUT_DIR / "estabilidad_kalina.csv"
T_AMB_DISENO, T_AMB_EVAL = 283.15, max(T_SUMIDERO, 283.15)
EPS = (0.85, 0.80, 0.85)
DP = 0.5                                        # perturbacion de P* [kPa]
SOLVE_KW = {"T_sumidero": T_SUMIDERO, "m_b": M_B, "eta_t": ETA_T, "eta_p": ETA_P,
            "eps_hrvg": EPS[0], "eps_reg": EPS[1], "eps_cond": EPS[2]}
EVAL_KW = {"T_sumidero": T_SUMIDERO, "m_b": M_B,
           "eps_hrvg": EPS[0], "eps_reg": EPS[1], "eps_cond": EPS[2]}
EXC = (CicloNoConvergeError, PropertyRangeError, ValueError,
       RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value
COLS = ("x_b", "P_alta", "T_fuente", "P_estrella",
        "eta_m", "eta_0", "eta_p", "Wnet_m", "Wnet_0", "Wnet_p",
        "h4_m", "h4_0", "h4_p", "T4_m", "T4_0", "T4_p",
        "margen_m", "margen_0", "margen_p",
        "clasif_m", "clasif_0", "clasif_p", "err_m", "err_0", "err_p",
        "dEta", "dH4", "clases_distintas", "estable", "detalle")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def evaluar(backend, x_b, P_alta, T_fuente, P):
    """Resuelve el ciclo en P y devuelve (estado dict, resultado_resolved, error)."""
    try:
        res = resolver_ciclo(backend, P_alta=P_alta, P_baja=P, T_fuente=T_fuente,
                             x_b=x_b, **SOLVE_KW)
        e4 = res["estados"]["e4"]
        T9_amb = condensador.resolver(res["estados"]["e8"], backend,
                                      T_sumidero=T_AMB_EVAL, eps=EPS[2],
                                      m=M_B)[0].T
        T_bur = backend.bubble_point(P, x_b)
        val = evaluar_ciclo(backend, res, P_alta=P_alta, P_baja=P, T_fuente=T_fuente,
                            x_b=x_b, T_amb_diseno=T_AMB_DISENO, **EVAL_KW)
    except EXC as exc:
        return None, None, f"{type(exc).__name__}: {exc}"
    return (dict(eta=res["eta"], Wnet=res["Wnet"], h4=e4.h, T4=e4.T,
                 margen=T_bur - T9_amb, clasif=val.clasificacion.value,
                 fallas=",".join(f.codigo for f in val.fallas)), res, "")


def fila_de(backend, x_b, P_alta, T_fuente, P_star):
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente,
                P_estrella=round(P_star, 6), detalle="")
    estados, errores = [], []
    for suf, P in (("m", P_star - DP), ("0", P_star), ("p", P_star + DP)):
        est, _, err = evaluar(backend, x_b, P_alta, T_fuente, P)
        estados.append(est)
        errores.append(err)
        for campo, valor in (("eta", est["eta"] if est else ""),
                             ("Wnet", est["Wnet"] if est else ""),
                             ("h4", est["h4"] if est else ""),
                             ("T4", est["T4"] if est else ""),
                             ("margen", est["margen"] if est else ""),
                             ("clasif", est["clasif"] if est else NOCONV)):
            fila[f"{campo}_{suf}"] = (round(valor, 6) if isinstance(valor, float)
                                      else valor)
        fila[f"err_{suf}"] = err
    ok = [e for e, err in zip(estados, errores) if err == ""]
    if len(ok) < 3:
        fila.update(dEta="", dH4="", clases_distintas="",
                    estable=False, detalle="evaluacion(es) con error: "
                    + "; ".join(f"{e or '?'}" for e in errores))
        return fila
    d_eta = max(e["eta"] for e in ok) - min(e["eta"] for e in ok)
    d_h4 = max(e["h4"] for e in ok) - min(e["h4"] for e in ok)
    clases = set(e["clasif"] for e in ok)
    fila.update(dEta=round(d_eta, 6), dH4=round(d_h4, 6),
                clases_distintas=len(clases),
                estable=d_eta <= 0.01 and d_h4 <= 10.0 and len(clases) == 1,
                detalle="")
    return fila


def cargar_kalina():
    filas = []
    with open(SRC, "r", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("clasificacion") != "KALINA":
                continue
            filas.append((float(r["x_b"]), float(r["P_alta"]), float(r["T_fuente"]),
                          float(r["P_baja"])))
    return filas


def principal():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    puntos = cargar_kalina()
    log(f"Puntos KALINA a evaluar: {len(puntos)}")
    t0 = time.time()
    resultado, fallos = [], 0
    for i, (x_b, P_alta, T_fuente, P_star) in enumerate(puntos, 1):
        fila = fila_de(TeqpAdapter(x=x_b), x_b, P_alta, T_fuente, P_star)
        resultado.append(fila)
        fallos += 0 if fila["estable"] else 1
        log(f"[{time.time() - t0:6.0f}s] {i}/{len(puntos)} x_b={x_b} "
            f"P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} P*={P_star:.6f} "
            f"eta_m0p={fila['eta_m']}/{fila['eta_0']}/{fila['eta_p']} "
            f"clasif={fila['clasif_m']}/{fila['clasif_0']}/{fila['clasif_p']} "
            f"dEta={fila['dEta']} dH4={fila['dH4']} "
            f"estable={fila['estable']} {fila['detalle'][:60]}")
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(resultado)
    n_est = sum(1 for f in resultado if f["estable"])
    log(f"Parte 2 completa en {time.time() - t0:.0f}s; "
        f"{n_est}/{len(resultado)} puntos estables; CSV: {OUT}")


if __name__ == "__main__":
    principal()
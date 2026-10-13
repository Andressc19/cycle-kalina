# -*- coding: utf-8 -*-
"""Paso 1 del diagnostico del punto +1.16 pp (P_alta=2300 kPa, x_b=0.55). SIN motor:
solo lee las curvas del paper y la tabla de validacion y escribe 5 CSV en
resultados/2026-10-13_punto_1p16pp/. No importa ningun backend de propiedades.

Uso: .venv/Scripts/python.exe scripts/punto_1p16_datos.py
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator, CubicSpline

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "resultados" / "2026-10-13_punto_1p16pp"
FIG7 = REPO / "resultados" / "2026-09-24_embaye_vectorial" / "curvas_embaye_fig7.csv"
VAL = REPO / "resultados" / "2026-09-24_validacion_tendencias" / "validacion_tendencias.csv"
CURVA = "KCS11(Con.=0.55)"
TEXTO_15BAR = 11.38          # valor del texto del paper (KCS11 0.55 @ 15 bar), Embaye et al.
P_INTERP = (2100, 2200, 2250, 2300, 2350, 2400)          # kPa
P_DESPL = 1910.0             # inicio de la rama descendente en kPa (> 19.1 bar)


def leer(ruta: Path) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(nombre: str, filas: list[dict], campos: list[str]) -> None:
    with open(OUT / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


def curve_paper() -> tuple[np.ndarray, np.ndarray]:
    """Curva KCS11(Con.=0.55) de la Fig 7: P [kPa] estrictamente creciente y eta [pp]."""
    pts = [(100.0 * float(r["P_evap_bar"]), float(r["eta_pct"]))
           for r in leer(FIG7) if r["curva"] == CURVA]
    pts.sort()
    return (np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))


def comparables() -> list[dict]:
    """23 puntos: teqp, convergen, titulo_salida_turbina >= 0.90, eta_paper disponible."""
    out = []
    for f in leer(VAL):
        if f["motor"] != "teqp" or f["convergio"] != "True":
            continue
        if f["titulo_salida_turbina"] == "" or float(f["titulo_salida_turbina"]) < 0.90:
            continue
        if f["eta_paper_pct"] == "":
            continue
        out.append(f)
    return out


def clave(f: dict) -> str:
    return f"{f['serie']}|{f['P_alta_kPa']}|{f['x_b']}|{f['T_fuente_K']}"


def stats(filas: list[dict]) -> dict:
    d = np.array([float(f["delta_pp"]) for f in filas])
    r = np.array([abs(float(f["delta_rel_pct"])) for f in filas])
    return dict(n=len(filas), delta_medio_pp=round(float(d.mean()), 4),
                absdelta_medio_pp=round(float(np.abs(d).mean()), 4),
                absdelta_max_pp=round(float(np.abs(d).max()), 4),
                mediana_absrel_pct=round(float(np.median(r)), 4))


def paso_h1(xs, ys):
    ops = {"lineal": lambda p: float(np.interp(p, xs, ys)),
           "pchip": PchipInterpolator(xs, ys), "cubic": CubicSpline(xs, ys)}
    i = int(np.searchsorted(xs, 2300.0) - 1)
    seg = lambda k: (ys[k + 1] - ys[k]) / ((xs[k + 1] - xs[k]) / 100.0)
    pend = {}
    if i >= 1:
        pend["dEta_dP_seg_izq_pp_bar"] = round(float(seg(i - 1)), 5)
    pend["dEta_dP_seg_2300_pp_bar"] = round(float(seg(i)), 5)
    if i + 2 <= len(xs) - 1:
        pend["dEta_dP_seg_der_pp_bar"] = round(float(seg(i + 1)), 5)
    filas = []
    for p in P_INTERP:
        fila = dict(P_kPa=p, eta_lineal_pp=round(ops["lineal"](p), 4),
                    eta_pchip_pp=round(float(ops["pchip"](p)), 4),
                    eta_cubic_pp=round(float(ops["cubic"](p)), 4))
        fila.update(pend if p == 2300 else {})
        filas.append(fila)
    campos = ["P_kPa", "eta_lineal_pp", "eta_pchip_pp", "eta_cubic_pp",
              "dEta_dP_seg_izq_pp_bar", "dEta_dP_seg_2300_pp_bar", "dEta_dP_seg_der_pp_bar"]
    escribir("h1_interpolacion.csv", filas, campos)
    return ops["lineal"](2300.0)


def paso_desplazamiento(xs, ys):
    """P_paper en que la rama descendente alcanza cada eta_modelo (P como funcion de eta)."""
    mask = xs > P_DESPL
    xd, yd = xs[mask], ys[mask]
    orden = np.argsort(yd)                       # eta ascendente -> P descendente
    xp, fp = yd[orden], xd[orden]
    filas = []
    for f in sorted((r for r in leer(VAL) if r["serie"] == "Fig7_KCS11_0p55"
                     and r["motor"] == "teqp" and r["convergio"] == "True"),
                    key=lambda r: float(r["P_alta_kPa"])):
        eta = float(f["eta_modelo_pct"])
        pmodelo = float(f["P_alta_kPa"]) / 100.0
        ppapel = float(np.interp(eta, xp, fp)) if xp[0] <= eta <= xp[-1] else ""
        filas.append(dict(P_modelo_kPa=float(f["P_alta_kPa"]), P_modelo_bar=pmodelo,
                          eta_modelo_pp=eta, P_paper_bar=round(ppapel, 4) if ppapel != "" else "",
                          dP_bar=round(pmodelo - ppapel, 4) if ppapel != "" else ""))
    escribir("h1_desplazamiento.csv", filas,
             ["P_modelo_kPa", "P_modelo_bar", "eta_modelo_pp", "P_paper_bar", "dP_bar"])


def paso_duplicados():
    p = {clave(f): float(f["eta_paper_pct"]) for f in leer(VAL) if f["eta_paper_pct"] != ""}
    fig7 = p["Fig7_KCS11_0p55|1500|0.55|373.0"]
    fig3 = p["Fig3_15bar|1500.0|0.55|373.0"]
    filas = [dict(fuente=nm, eta_paper_pct=et,
                  dif_vs_fig7_pp=round(et - fig7, 4), dif_vs_fig3_pp=round(et - fig3, 4),
                  dif_vs_texto_pp=round(et - TEXTO_15BAR, 4))
             for nm, et in (("Fig7", fig7), ("Fig3", fig3), ("texto", TEXTO_15BAR))]
    escribir("h5_duplicados.csv", filas,
             ["fuente", "eta_paper_pct", "dif_vs_fig7_pp", "dif_vs_fig3_pp", "dif_vs_texto_pp"])


def paso_estadistica(cmp23):
    def fila(crit, sub, nota=""):
        s = stats(sub)
        excl = " ; ".join(clave(f) for f in cmp23 if f not in sub)
        return dict(criterio=crit, **s, excluidos=excl, nota=nota)
    p2300 = [f for f in cmp23 if not (f["serie"] == "Fig7_KCS11_0p55"
                                      and f["P_alta_kPa"] == "2300")]
    def filtro(col, umbral):
        return [f for f in cmp23 if float(f[col]) >= umbral]
    filas = [fila("todos", cmp23),
             fila("sin_punto_2300", p2300),
             fila("sin_punto_2300_por_decision", p2300,
                  "exclusion por decision del usuario, causa abierta, NO por criterio objetivo"),
             fila("Wnet>=20kW", filtro("Wnet_kW", 20.0)),
             fila("Wnet>=25kW", filtro("Wnet_kW", 25.0)),
             fila("eps_hrvg>=0.80", filtro("eps_hrvg", 0.80)),
             fila("eps_hrvg>=0.85", filtro("eps_hrvg", 0.85))]
    escribir("estadistica_con_sin.csv", filas,
             ["criterio", "n", "delta_medio_pp", "absdelta_medio_pp", "absdelta_max_pp",
              "mediana_absrel_pct", "excluidos", "nota"])


def paso_diagnostico(cmp23):
    filas = [dict(serie=f["serie"], T_fuente_K=f["T_fuente_K"], P_alta_kPa=f["P_alta_kPa"],
                  x_b=f["x_b"], eps_hrvg=f["eps_hrvg"], Wnet_kW=f["Wnet_kW"],
                  q4=f["titulo_salida_turbina"], delta_pp=f["delta_pp"],
                  delta_rel_pct=f["delta_rel_pct"])
             for f in sorted(cmp23, key=lambda r: float(r["eps_hrvg"]))]
    escribir("diagnostico_23.csv", filas,
             ["serie", "T_fuente_K", "P_alta_kPa", "x_b", "eps_hrvg", "Wnet_kW", "q4",
              "delta_pp", "delta_rel_pct"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    xs, ys = curve_paper()
    cmp23 = comparables()
    eta2300 = paso_h1(xs, ys)
    paso_desplazamiento(xs, ys)
    paso_duplicados()
    paso_estadistica(cmp23)
    paso_diagnostico(cmp23)
    print(f"comparables n={len(cmp23)}")
    print(f"eta_paper(2300 kPa, lineal) = {eta2300:.4f} pp")
    for f in leer(OUT / "h1_interpolacion.csv"):
        print(" interp", f)
    for f in leer(OUT / "estadistica_con_sin.csv"):
        print(" stat  ", {k: f[k] for k in ("criterio", "n", "delta_medio_pp",
                                            "absdelta_medio_pp", "absdelta_max_pp")})
    print("Salidas en", OUT)


if __name__ == "__main__":
    main()

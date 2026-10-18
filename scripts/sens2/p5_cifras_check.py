# -*- coding: utf-8 -*-
"""Sens2 - p5_cifras_check: comprobacion independiente de las cifras de las conclusiones.

Recalcula desde los CSV crudos (no desde p5_hechos.py) los 23 controles de prompts/ref_rev_final.py y
8 controles de texto: cada cifra recalculada, con su formato, debe aparecer como subcadena del campo
indicado de la conclusion. Escribe p5_cifras_check.csv (grupo, control, resultado, detalle) y
p5_cifras_check.md (conteo OK/FALLA y lista de FALLA); imprime una linea OK/FALLA por control y sale
con codigo 1 si hay alguna FALLA. No modifica ningun texto.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
R = os.path.join(RAIZ, "resultados")
D = os.path.join(R, "2026-10-17_sens2_P5")
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

FILAS = []


def chk(grupo, control, cond, detalle):
    FILAS.append({"grupo": grupo, "control": control,
                  "resultado": "OK" if cond else "FALLA", "detalle": detalle})
    print(("OK    " if cond else "FALLA ") + control + " :: " + detalle)


def sub(texto, valor, fmt):
    return (fmt % valor) in str(texto)


def main():
    P = lambda *p: os.path.join(R, *p)                                  # noqa: E731
    concl = pd.read_csv(os.path.join(D, "p5_conclusiones.csv"))

    def ev(cid, campo="evidencia"):
        r = concl[concl["id"] == cid]
        return str(r.iloc[0][campo]) if len(r) else ""

    d = pd.read_csv(P("2026-10-17_sens2_P2", "p2_dataset_dedup.csv"))
    k = d[d.kalina & d.eta_pct.notna()]
    env = pd.read_csv(P("2026-10-17_sens2_P4", "p4_envolventes.csv"))
    e = env[env.centro == "todos"]
    TOP = "10 % de KALINA (total) con mayor eta"

    def g(q, col, conj="KALINA (total)"):
        return float(e[(e.cantidad == q) & (e.conjunto == conj)].iloc[0][col])

    # --- Controles portados de ref_rev_final.py ---
    a, b = g("Qi_mb", "p5"), g("Qi_mb", "p95")
    chk("E", "E6", abs(a - 228.8) < 0.5 and abs(b - 1695.3) < 0.5, "Qi_mb p5=%.1f p95=%.1f (229-1695)" % (a, b))
    w = [g("Wp_Wt", "p5"), g("Wp_Wt", "p95"), g("Wp_Wt", "p50")]
    chk("E", "E7", abs(w[0] - 0.0238) < 5e-4 and abs(w[1] - 0.3014) < 5e-4 and abs(w[2] - 0.060) < 1e-3,
        "Wp/Wt p5=%.4f p95=%.4f p50=%.3f" % tuple(w))
    t = [g("Wp_Wt", "p5", TOP), g("Wp_Wt", "p95", TOP)]
    chk("E", "E7top10", abs(t[0] - 0.0272) < 5e-4 and abs(t[1] - 0.0781) < 5e-4,
        "Wp/Wt top10 p5=%.4f p95=%.4f" % tuple(t))
    qo = g("Qout_mb", "p50")
    chk("E", "E5qout", abs(qo - 721.2) < 0.5, "Qout_mb p50=%.1f (721)" % qo)
    ac = [g("aprox_cond_sal", "p5"), g("aprox_cond_sal", "p95")]
    chk("E", "E5aprox", abs(ac[0] - 2.6) < 0.1 and abs(ac[1] - 23.4) < 0.1,
        "aprox p5=%.1f p95=%.1f (2.6-23.4)" % tuple(ac))
    q4 = g("q4", "p50", TOP)
    chk("E", "E3q4", abs(q4 - 0.9355) < 1e-3, "q4 top10 p50=%.4f (0.9355)" % q4)

    def pt(i):
        return d[d.id_punto == i].iloc[0]

    a = pt("C1-B3-0127")
    chk("M", "M2pt", abs(a.eta_pct - 14.01) < 0.01 and a.P_alta == 5000 and a.P_baja == 600,
        "C1-B3-0127 eta=%.2f P_alta=%.0f P_baja=%.0f" % (a.eta_pct, a.P_alta, a.P_baja))
    a = pt("C1-B5-0228")
    chk("M", "M3", abs(a.eta_pct - 13.95) < 0.01 and a.eta_t == 0.95 and a.eps_reg == 0.95 and a.P_alta == 3300,
        "C1-B5-0228 eta=%.2f eta_t=%.2f eps_reg=%.2f" % (a.eta_pct, a.eta_t, a.eps_reg))
    a = pt("N7B-C4-B1-045")
    chk("M", "M4c4", abs(a.eta_pct - 13.23) < 0.01 and a.T_fuente == 423.15 and a.P_baja == 800,
        "N7B-C4-B1-045 eta=%.2f T_fuente=%.2f P_baja=%.0f" % (a.eta_pct, a.T_fuente, a.P_baja))
    a = pt("C2-LHS-0005")
    chk("M", "M4c2", abs(a.eta_pct - 12.37) < 0.01 and not a.fuera_rango, "C2-LHS-0005 eta=%.2f" % a.eta_pct)
    mx = [k[~k.fuera_rango].eta_pct.max(), k[k.fuera_rango].eta_pct.max()]
    chk("M", "M1max", abs(mx[0] - 14.53) < 0.01 and abs(mx[1] - 14.82) < 0.01,
        "eta max dentro=%.2f fuera=%.2f" % tuple(mx))
    md = [k.eta_pct.median(), k.eta_pct.quantile(0.9)]
    chk("M", "M1medp90", abs(md[0] - 7.73) < 0.01 and abs(md[1] - 11.53) < 0.01,
        "eta mediana=%.2f P90=%.2f" % tuple(md))
    fr = float(k.fuera_rango.mean())
    chk("L", "L4frac", abs(fr - 0.15) < 0.005, "fuera de rango=%.3f" % fr)
    zg = pd.read_csv(P("2026-10-17_sens2_P1", "p1_zonas_grises.csv"))
    o2 = int((zg.dominante == "viol_O2").sum())
    chk("L", "L1", len(zg) == 255 and o2 == 249, "zonas=%d O2=%d" % (len(zg), o2))
    dist = pd.read_csv(P("2026-10-17_sens2_P2", "p2_distancia.csv"))
    chk("L", "L2n", len(dist) == 968, "CORREGIBLE con vecino=%d" % len(dist))
    nv = float((dist.nvars_diff == 1).mean())
    chk("L", "L2nvars", abs(nv - 0.4928) < 0.002, "a una variable=%.3f" % nv)
    for cg, c in (("D4c1", "C1 Husavik"), ("D4c2", "C2 ancla A*"), ("D4c3", "C3 caliente 150 C"), ("D4c4", "C4 frio 110 C")):
        v = float(k[k.centro == c].eps_cond.min())
        ref = {"D4c1": 0.80, "D4c2": 0.65, "D4c3": 0.85, "D4c4": 0.85}[cg]
        chk("D", cg, abs(v - ref) < 1e-9, "%s eps_cond min=%.4f" % (c, v))
    f6c = float(d[d.clasificacion == "CORREGIBLE"].eta_pct.median())
    f6k = float(k.eta_pct.median())
    chk("F", "F6medianas", abs(f6c - 10.20) < 0.01 and abs(f6k - 7.73) < 0.01,
        "medianas cor=%.2f kal=%.2f" % (f6c, f6k))
    chk("GLOBAL", "Gn", len(concl) == len(pd.read_csv(P("2026-10-17_sens2_P5", "p5_evidencia.csv"))) and concl.id.is_unique, "conclusiones=%d" % len(concl))
    txt = " ".join(concl.fillna("").astype(str).values.ravel()).lower()
    malas = [w for w in ("confiable", "no citable", "fuera de rango del motor", "sin respaldo", "indicio", "extrapol") if w in txt]
    chk("GLOBAL", "Gterm", not malas, "terminos prohibidos en conclusiones: %s" % (malas or "ninguno"))

    # --- Controles de texto (dato crudo -> subcadena en la conclusion) ---
    u = pd.read_csv(P("2026-10-17_sens2_U1", "u1_filas.csv"))
    u = u[u.barrido.isin(["U1A", "U1A2"])]
    fu = {c: float((u[u.centro == c].clasificacion == "KALINA").mean()) for c in ("C1", "C2", "C3", "C4")}
    tu = ev("U1")
    chk("U", "U1", all(sub(tu, fu[c], "%.2f") for c in fu),
        "P(KALINA) " + " ".join("%s=%.2f" % (c, fu[c]) for c in fu))

    import x1_cargar as X
    xd = X.cargar_todo()
    xk = xd[(xd.clasificacion == "KALINA") & xd.m_O2.notna()]
    l7 = 100.0 * float((xk.m_O2 < 3).mean())
    chk("L", "L7", sub(ev("L7"), l7, "%.1f"), "m_O2<3 K = %.1f %% en evidencia L7" % l7)

    rp = pd.read_csv(P("2026-10-18_sens2_R1", "r1_puntos.csv"))
    l8 = int(((rp.cerca == True) & (rp.clasificacion == "KALINA")).sum())    # noqa: E712
    chk("L", "L8", sub(ev("L8"), l8, "%d"), "cerca y KALINA = %d en evidencia L8" % l8)

    rv = pd.read_csv(P("2026-10-18_sens2_R1", "r2_vecinos_puntos.csv"))
    l9 = float((rv.pred_kalina == (rv.clasificacion == "KALINA")).mean())
    chk("L", "L9", sub(ev("L9"), l9, "%.3f"), "exactitud = %.3f en evidencia L9" % l9)

    br = xd[xd.estudio.isin([1, 10]) & (xd.variable == "base") & xd.centro.astype(str).str.startswith("C1")].iloc[0]
    m2 = float(br.eta_pct)
    chk("M", "M2", sub(ev("M2"), m2, "%.2f"), "centro C1 eta = %.2f %% en evidencia M2" % m2)

    chk("F", "F6", sub(ev("F6"), f6c, "%.1f") and sub(ev("F6"), f6k, "%.1f"),
        "medianas cor=%.1f kal=%.1f en evidencia F6" % (f6c, f6k))

    x = d[d.estudio.isin([3, 14])]
    c4 = x[x.centro == "C4 frio 110 C"]
    lo = c4[c4.T_fuente <= c4.T_fuente.quantile(0.25)]
    d3 = "%d de %d" % (int((lo.clasificacion == "NO_CONVERGIO").sum()), len(lo))
    chk("D", "D3", d3 in ev("D3"), "C4 cuartil bajo: %s en evidencia D3" % d3)

    dr = pd.read_csv(P("2026-10-17_sens2_P2", "p2_distancia_resumen.csv"))
    l2 = abs(float(dr[(dr.seccion == "eta") & (dr.centro == "todos")].iloc[0].mediana))
    chk("L", "L2", sub(ev("L2"), l2, "%.2f"), "abs(mediana eta) = %.2f en evidencia L2" % l2)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import p5_cifras_check_b as B
    B.extra(chk, ev, sub, P)

    # --- Salidas ---
    n = len(FILAS)
    nf = sum(f["resultado"] == "FALLA" for f in FILAS)
    pd.DataFrame(FILAS, columns=["grupo", "control", "resultado", "detalle"]).to_csv(
        os.path.join(D, "p5_cifras_check.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    with open(os.path.join(D, "p5_cifras_check.md"), "w", encoding="utf-8") as f:
        f.write("# Sens2 P5 - comprobacion independiente de las cifras\n\n")
        f.write("- controles: %d\n- OK: %d\n- FALLA: %d\n\n" % (n, n - nf, nf))
        f.write("## FALLA\n\n| grupo | control | detalle |\n|---|---|---|\n")
        for fila in FILAS:
            if fila["resultado"] == "FALLA":
                f.write("| %s | %s | %s |\n" % (fila["grupo"], fila["control"], fila["detalle"]))
    print("\ncontroles: %d  OK: %d  FALLA: %d" % (n, n - nf, nf))
    return nf


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

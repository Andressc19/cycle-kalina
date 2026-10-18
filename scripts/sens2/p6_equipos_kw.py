# -*- coding: utf-8 -*-
"""Sens2 F1 - A7k, Parte 1: requisitos de equipos por kW neto (sin motor).

Los requisitos del libro estan por kg/s de fluido de trabajo (m_b). Para preseleccionar
equipos hacen falta por kW neto, y se obtienen de columnas que ya existen sin correr el
motor: con `p4_comun.cargar()` se toman los KALINA (total) con `wnet_mb` finito y > 0 y se
calcula, por kW neto, Qi_kW = Qi_mb/wnet_mb, Qout_kW = Qout_mb/wnet_mb,
Qreg_kW = qreg_qi*Qi_mb/wnet_mb, Wt_kW = Wt_mb/wnet_mb, Wp_kW = Wp_mb/wnet_mb,
UA_kW = UA_reg/wnet_mb (1/K) y m_b_kW = 1/wnet_mb (kg/s por kW neto). Control:
Qi_kW = 100/eta_pct con tolerancia relativa del 1 %. Se informan P5, P50 y P95 (cuantiles
0.05, 0.50, 0.95) y n de las 7 magnitudes en los ambitos: todos, los cuatro centros,
solo LHS (estudios 3 y 14) y el 10 % de mayor eta. Salidas: p6_equipos_kw.csv y
p6_equipos_kw.md.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import p4_comun as c  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
MAGS = [("Qi_kW", "kW por kW neto"), ("Qout_kW", "kW por kW neto"),
        ("Qreg_kW", "kW por kW neto"), ("Wt_kW", "kW por kW neto"),
        ("Wp_kW", "kW por kW neto"), ("UA_kW", "K^-1"),
        ("m_b_kW", "kg/s por kW neto")]
UNIDAD_100 = {"Qi_kW": "kW", "Qout_kW": "kW", "Qreg_kW": "kW", "Wt_kW": "kW",
              "Wp_kW": "kW", "UA_kW": "kW/K", "m_b_kW": "kg/s"}
LHS = [3, 14]
AMB_LHS = "solo LHS"
AMB_TOP = "10 % de mayor eta"
AMB_EJ = "ejemplo 100 kW"
ADVERTENCIA = ("son envolventes de un muestreo numerico, por kg/s de fluido; "
               "no son especificaciones de compra")
COLS = ["ambito", "magnitud", "unidad", "n", "p5", "p50", "p95"]


def base_kw(d):
    """KALINA (total) con wnet_mb finito y > 0, con las 7 magnitudes por kW neto."""
    m = c.mask_total(d) & d["wnet_mb"].notna() & (d["wnet_mb"] > 0)
    b = d[m].copy()
    w = b["wnet_mb"].to_numpy(float)
    b["Qi_kW"] = b["Qi_mb"].to_numpy(float) / w
    b["Qout_kW"] = b["Qout_mb"].to_numpy(float) / w
    b["Qreg_kW"] = b["qreg_qi"].to_numpy(float) * b["Qi_mb"].to_numpy(float) / w
    b["Wt_kW"] = b["Wt_mb"].to_numpy(float) / w
    b["Wp_kW"] = b["Wp_mb"].to_numpy(float) / w
    b["UA_kW"] = b["UA_reg"].to_numpy(float) / w
    b["m_b_kW"] = 1.0 / w
    return b


def ambitos(b):
    """Pares (nombre, subconjunto) de los ambitos pedidos, en orden."""
    out = [("todos", b)]
    for ce in c.CENTROS[:4]:
        out.append((ce, b[b["centro"] == ce]))
    out.append((AMB_LHS, b[b["estudio"].isin(LHS)]))
    out.append((AMB_TOP, b[c.mask_top10(b)]))
    return out


def control(b):
    """Fraccion de filas con Qi_kW = 100/eta_pct dentro del 1 % relativo."""
    qi = np.asarray(pd.to_numeric(b["Qi_kW"], errors="coerce"), float)
    ref = 100.0 / np.asarray(pd.to_numeric(b["eta_pct"], errors="coerce"), float)
    ok = np.isfinite(qi) & np.isfinite(ref) & (np.abs(qi - ref) <= 0.01 * np.abs(ref))
    n = int(len(b))
    return (float(ok.mean()) if n else float("nan"), int(ok.sum()), n)


def filas_cuantiles(b, pares):
    """Filas [ambito, magnitud, unidad, n, p5, p50, p95] de cada ambito y magnitud."""
    filas = []
    for nombre, s in pares:
        for mag, uni in MAGS:
            r = c.resumen_serie(s[mag])
            filas.append([nombre, mag, uni, r["n"], r["p5"], r["p50"], r["p95"]])
    return filas


def filas_ejemplo(b):
    """Filas del ejemplo de 100 kW netos: ambito `todos` multiplicado por 100."""
    filas = []
    for mag, _ in MAGS:
        r = c.resumen_serie(b[mag])
        filas.append([AMB_EJ, mag, UNIDAD_100[mag], r["n"],
                      100.0 * r["p5"], 100.0 * r["p50"], 100.0 * r["p95"]])
    return filas


def markdown(filas, ej, frac, ok, n):
    l = ["# Sens2 F1 - A7k: requisitos de equipos por kW neto (sin motor)", "",
         "P5, P50 y P95 (cuantiles 0.05, 0.50, 0.95) de las magnitudes por kW neto sobre",
         "los KALINA (total) con trabajo neto positivo. Ambitos: todos, los cuatro centros,",
         "solo LHS (estudios 3 y 14) y el 10 % de KALINA (total) con mayor eta. Unidades:",
         "las cinco primeras magnitudes en kW por kW neto, UA_kW en K^-1 y m_b_kW en",
         "kg/s por kW neto.", "",
         "## Control Qi_kW = 100/eta_pct (tolerancia relativa 1 %)", "",
         "%d de %d filas dentro del 1 %% (fraccion %.4f)." % (ok, n, frac), "",
         "## Cuantiles por magnitud y ambito", "",
         "| ambito | magnitud | unidad | n | P5 | P50 | P95 |",
         "|---|---|---|---|---|---|---|"]
    for f in filas:
        l.append("| %s | %s | %s | %d | %s | %s | %s |" % (
            f[0], f[1], f[2], f[3], c.fmt(f[4], 4), c.fmt(f[5], 4), c.fmt(f[6], 4)))
    l += ["", "## Ejemplo de dimensionamiento para 100 kW netos", "",
          "Las cinco magnitudes de potencia y m_b_kW del ambito `todos` multiplicadas por 100,",
          "y UA_kW por 100 para dar kW/K. Fila adicional `%s`." % AMB_EJ, "",
          "| ambito | magnitud | unidad | n | P5 | P50 | P95 |",
          "|---|---|---|---|---|---|---|"]
    for f in ej:
        l.append("| %s | %s | %s | %d | %s | %s | %s |" % (
            f[0], f[1], f[2], f[3], c.fmt(f[4], 4), c.fmt(f[5], 4), c.fmt(f[6], 4)))
    l += ["", "Advertencia: %s." % ADVERTENCIA, ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    b = base_kw(d)
    pares = ambitos(b)
    filas = filas_cuantiles(b, pares)
    frac, ok, n = control(b)
    ej = filas_ejemplo(b)
    os.makedirs(SALIDA, exist_ok=True)
    t = pd.DataFrame(filas, columns=COLS)
    t.to_csv(os.path.join(SALIDA, "p6_equipos_kw.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_equipos_kw.md"), "w", encoding="utf-8") as fh:
        fh.write(markdown(filas, ej, frac, ok, n) + "\n")
    print("p6_equipos_kw.csv:", len(t), "filas (sin el ejemplo de 100 kW)")
    print("control Qi_kW = 100/eta_pct: %d de %d (fraccion %.4f)" % (ok, n, frac))
    print("ambito todos:")
    for f in filas:
        if f[0] == "todos":
            print("  %-8s n=%4d  P5=%10s  P50=%10s  P95=%10s  [%s]"
                  % (f[1], f[3], c.fmt(f[4], 4), c.fmt(f[5], 4), c.fmt(f[6], 4), f[2]))
    print("ejemplo 100 kW (todos x100):")
    for f in ej:
        print("  %-8s n=%4d  P5=%10s  P50=%10s  P95=%10s  [%s]"
              % (f[1], f[3], c.fmt(f[4], 4), c.fmt(f[5], 4), c.fmt(f[6], 4), f[2]))


if __name__ == "__main__":
    main()

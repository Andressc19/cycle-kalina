"""Tablas del reporte de `2026-10-02-reejecutar-no-convergio` a partir de los CSV ya
generados (no resuelve ningún ciclo): resultados por barrido de origen, causas de los
que siguen sin converger, cruce con la comprobación O5 y la verificación con el motor
real. Escribe `resultados/2026-10-02_reejecucion/tablas_reejecucion.md` y lo imprime.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "2026-10-02_reejecucion"
O5 = RAIZ / "resultados" / "2026-10-01_comprobacion_o5" / "comprobacion_o5_filas.csv"
CLAVE_O5 = ("P_alta", "x_b", "T_fuente", "T_sumidero", "eps_hrvg")


def _origen(s):
    return str(s).split(";")[0].split("/")[-1].replace(".csv", "")


def tabla_por_origen(r):
    r = r.assign(origen=r.csv_origenes.map(_origen), conv=r.convergio.astype(str) == "True")
    g = r.groupby("origen")
    t = pd.DataFrame({
        "puntos": g.size(),
        "recuperados": g.conv.sum(),
        "KALINA": g.apply(lambda x: ((x.clasificacion == "KALINA") & x.conv).sum()),
        "CORREGIBLE": g.apply(lambda x: ((x.clasificacion == "CORREGIBLE") & x.conv).sum()),
        "INVIABLE": g.apply(lambda x: ((x.clasificacion == "INVIABLE") & x.conv).sum()),
        "NO_CONV_tras_clasificar": g.apply(lambda x: ((x.clasificacion == "NO_CONVERGIO") & x.conv).sum()),
        "siguen_sin_converger": g.apply(lambda x: (~x.conv).sum()),
    }).sort_values("puntos", ascending=False)
    t.loc["TOTAL"] = t.sum()
    t["%_recuperado"] = (100 * t.recuperados / t.puntos).round(1)
    return t


def tabla_causas(r):
    nc = r[r.convergio.astype(str) != "True"]
    return nc.causa.fillna("otro").replace("", "otro").value_counts().rename("filas").to_frame()


def cruce_o5(r):
    if not O5.exists():
        return pd.DataFrame()
    o5 = pd.read_csv(O5)
    m = r.merge(o5[[*CLAVE_O5, "veredicto"]], on=list(CLAVE_O5), how="inner")
    m = m.assign(conv=m.convergio.astype(str) == "True")
    return pd.crosstab(m.veredicto, m.conv.map({True: "converge ahora", False: "sigue sin converger"}),
                       margins=True, margins_name="total")


def tiempos(r):
    t = r.t_s.astype(float)
    conv = r.convergio.astype(str) == "True"
    filas = {"todas": t, "recuperadas": t[conv], "sin converger": t[~conv]}
    d = pd.DataFrame({k: [len(v), v.mean(), v.median(), v.quantile(.9), v.max()] for k, v in filas.items()},
                     index=["n", "media_s", "mediana_s", "p90_s", "max_s"]).T.round(1)
    d.loc["cortadas por presupuesto (300 s)"] = [int((r.causa == "presupuesto agotado").sum()), *[None] * 4]
    return d


def main():
    r = pd.read_csv(OUT / "reejecucion_filas.csv")
    partes = [("Resultado por barrido de origen", tabla_por_origen(r)),
              ("Causa de los que siguen sin converger", tabla_causas(r)),
              ("Cruce con la comprobación O5", cruce_o5(r)),
              ("Tiempos por fila", tiempos(r))]
    vr = OUT / "verificacion_real.csv"
    if vr.exists() and vr.stat().st_size > 0:       # puede existir vacío mientras corre el paso 4
        partes.append(("Verificación con el motor real", pd.read_csv(vr)))
    texto = "\n\n".join(f"## {t}\n\n```\n{df.to_string()}\n```" for t, df in partes)  # sin tabulate
    (OUT / "tablas_reejecucion.md").write_text(texto + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()

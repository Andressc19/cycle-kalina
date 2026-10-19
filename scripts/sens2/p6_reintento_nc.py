# -*- coding: utf-8 -*-
"""Sens2 etapa B - reintento de NO_CONVERGIO con mayor presupuesto (barrido REINT0 del motor).

Grupo 'lento': NO_CONVERGIO originales que agotaron el presupuesto (t_s >= 250 s) y se volvieron a correr con presupuesto 900 s y tope 1100 s.
Grupo 'control': NO_CONVERGIO originales rapidos (t_s < 100 s), mismas condiciones; sirve para comprobar que el motor es determinista (deben seguir sin converger).
Salidas en resultados/2026-10-18_sens2_F1: p6_reintento_nc.csv (una fila por punto) y p6_reintento_nc.md (conteos por grupo y clase nueva).
"""
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENT = os.environ.get("S2B_DIR", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_B"))
SAL = os.environ.get("S2B_OUT", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1"))


def main():
    ruta = os.path.join(ENT, "s2b_filas.csv")
    if not os.path.exists(ruta):
        print("sin s2b_filas.csv: nada que analizar")
        return 0
    d = pd.read_csv(ruta)
    d = d[d["barrido"] == "REINT0"].copy()
    if d.empty:
        print("sin filas REINT0")
        return 0
    d["clasificacion"] = d["clasificacion"].fillna("ERROR_MOTOR")
    d["grupo"] = d["id_punto"].str.extract(r"^RN-(lento|control)-")[0]
    d["id_original"] = d["id_punto"].str.replace(r"^RN-(lento|control)-", "", regex=True)
    d["t_s_original"] = d["val1"]
    d["causa_nueva"] = d["mensaje"].fillna("").str.replace(r"\[NO_CONVERGIO\]\s*", "", regex=True).str.slice(0, 60)
    o = d[["id_original", "grupo", "centro", "t_s_original", "t_s", "clasificacion", "eta", "causa_nueva"]].rename(columns={"t_s": "t_s_nuevo", "clasificacion": "clase_nueva"})
    os.makedirs(SAL, exist_ok=True)
    o.to_csv(os.path.join(SAL, "p6_reintento_nc.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    tab = pd.crosstab(d["grupo"], d["clasificacion"])
    md = ["# Sens2 etapa B - reintento de NO_CONVERGIO con mayor presupuesto", "",
          "Presupuesto 900 s y tope 1100 s (el original era 300 s y 600 s). El motor es determinista: si el grupo de control cambia de clase, el reintento no es comparable.", "",
          "| grupo | puntos | siguen NO_CONVERGIO | ahora KALINA | ahora CORREGIBLE | ahora INVIABLE | error del motor |", "|---|---|---|---|---|---|---|"]
    for g in ("lento", "control"):
        if g in tab.index:
            r = tab.loc[g]
            md.append("| %s | %d | %d | %d | %d | %d | %d |" % (g, r.sum(), r.get("NO_CONVERGIO", 0), r.get("KALINA", 0), r.get("CORREGIBLE", 0), r.get("INVIABLE", 0), r.get("ERROR_MOTOR", 0)))
    md += ["", "## Causas de los que siguen sin converger", "", "| causa (primeros 60 caracteres) | n |", "|---|---|"]
    s = d[d["clasificacion"] == "NO_CONVERGIO"]["causa_nueva"].value_counts()
    md += ["| %s | %d |" % (k, v) for k, v in s.items()]
    with open(os.path.join(SAL, "p6_reintento_nc.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(tab.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

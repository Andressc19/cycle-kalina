# -*- coding: utf-8 -*-
"""Sens2 etapa B - pisos de P_baja con paso de 25 kPa (puntos PISOS del motor frente a la malla B2 de 100-150 kPa).

Por centro y nivel de x_b: piso de la malla (primer nivel KALINA), nivel inferior de la malla, puntos intermedios corridos, y el piso
refinado = menor P_baja desde el cual todos los puntos corridos hasta el piso de la malla son KALINA. Entradas: s2b_filas.csv (barrido
PISOS). Salidas: p6_pisos25.csv y p6_pisos25.md en resultados/2026-10-18_sens2_F1 (variables de entorno S2B_DIR y S2B_OUT para pruebas).
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
ENT = os.environ.get("S2B_DIR", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_B"))
SAL = os.environ.get("S2B_OUT", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1"))
NOMBRE = {"C1": "C1 Husavik", "C2": "C2 ancla A*", "C3": "C3 caliente 150 C", "C4": "C4 frio 110 C"}


def main():
    ruta = os.path.join(ENT, "s2b_filas.csv")
    if not os.path.exists(ruta):
        print("sin s2b_filas.csv: nada que analizar")
        return 0
    d = pd.read_csv(ruta)
    d = d[d["barrido"] == "PISOS"]
    if d.empty:
        print("sin filas PISOS")
        return 0
    import s2_calc as C
    import s2b_puntos as P
    filas = []
    for cod, nombre in NOMBRE.items():
        _, cls, av, bv = C.malla_clases(nombre, "B2")
        av, bv = [float(a) for a in av], [float(b) for b in bv]
        for xb in P.XB_PISOS[nombre]:
            j = min(range(len(bv)), key=lambda i: abs(bv[i] - xb))
            col = [i for i in range(len(av)) if cls[i, j] == "K"]
            if not col:
                continue
            hi = av[min(col)]
            lo = av[min(col) - 1] if min(col) > 0 else float("nan")
            g = d[(d["centro"] == cod) & ((d["x_b"] - xb).abs() < 1e-6)].sort_values("P_baja")
            if g.empty:
                continue
            ref = hi
            for p, c in sorted(zip(g["P_baja"], g["clasificacion"]), reverse=True):
                if c == "KALINA":
                    ref = float(p)
                else:
                    break
            gk = g[g["clasificacion"] == "KALINA"]
            filas.append(dict(centro=cod, x_b=xb, nivel_inferior_malla=lo, piso_malla=hi, minimo_kalina_observado=float(gk["P_baja"].min()) if len(gk) else float("nan"), n_puntos=len(g),
                              n_kalina=int((g["clasificacion"] == "KALINA").sum()), n_corregible=int((g["clasificacion"] == "CORREGIBLE").sum()),
                              n_no_convergio=int((g["clasificacion"] == "NO_CONVERGIO").sum()), piso_refinado=ref, mejora_kpa=hi - ref,
                              clases_por_P_baja=" ".join("%d:%s" % (round(p), c[0]) for p, c in zip(g["P_baja"], g["clasificacion"]))))
    t = pd.DataFrame(filas)
    os.makedirs(SAL, exist_ok=True)
    t.to_csv(os.path.join(SAL, "p6_pisos25.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    md = ["# Sens2 etapa B - pisos de P_baja con paso de 25 kPa", "",
          "Piso refinado = menor P_baja desde el cual todos los puntos corridos (paso 25 kPa) hasta el piso de la malla son KALINA. 'mejora' = piso de la malla menos piso refinado.", "",
          "| centro | x_b | nivel inferior malla | piso malla | puntos | KALINA | CORREGIBLE | NO_CONVERGIO | piso refinado | mejora (kPa) |", "|---|---|---|---|---|---|---|---|---|---|"]
    md += ["| %s | %.2f | %s | %.0f | %d | %d | %d | %d | %.0f | %.0f |" % (r.centro, r.x_b, "-" if pd.isna(r.nivel_inferior_malla) else "%.0f" % r.nivel_inferior_malla,
           r.piso_malla, r.n_puntos, r.n_kalina, r.n_corregible, r.n_no_convergio, r.piso_refinado, r.mejora_kpa) for r in t.itertuples()]
    md += ["", "Los NO_CONVERGIO cuentan como 'no KALINA' al buscar el piso (cortan la secuencia)."]
    with open(os.path.join(SAL, "p6_pisos25.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("pisos: %d filas; mejora mediana %.0f kPa" % (len(t), t["mejora_kpa"].median()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

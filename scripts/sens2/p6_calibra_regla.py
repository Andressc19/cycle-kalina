# -*- coding: utf-8 -*-
"""Sens2 F1 - calibracion de la regla "distinguible" (q < 0.05 en al menos 2 metodos) y BH de familia global.

Entrada: p6_nulo_perm.csv (caja, bloque, respuesta, variable, tipo {real, dummy}, metodo, p_perm, q_bloque, q_respuesta).
La regla declara distinguible una variable si q < 0.05 en al menos 2 metodos dentro de su bloque y respuesta. El archivo
solo trae q_bloque para las variables reales; para poder aplicar la regla a las dummy se recalcula BH por bloque y
respuesta sobre TODAS las pruebas (reales + dummy) -> "q_regla". Sobre las dummy se mide la tasa de falsos positivos.
Familia global: BH a p_perm sobre todas las pruebas juntas, por metodo y con los metodos mezclados; se compara el numero
de reales distinguidas con la regla por bloque (q_bloque del archivo). Salidas: p6_calibra_regla.csv y p6_calibra_regla.md.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p6_comun as K  # noqa: E402

COLS = ["tabla", "k", "grupo", "n_unidades", "marcadas", "fraccion", "ic_lo", "ic_hi", "bloque",
        "respuesta", "reales_bloque", "reales_global_metodo", "reales_global_mezcla"]


def conteo(sub, qcol):
    """Por (bloque, respuesta, variable): en cuantos metodos qcol < Q."""
    return sub.assign(sig=sub[qcol] < K.Q).groupby(["bloque", "respuesta", "variable"])["sig"].sum()


def fila_k(tabla, k, grupo, n, m):
    lo, hi = K.wilson(m, n)
    return {"tabla": tabla, "k": k, "grupo": grupo, "n_unidades": n, "marcadas": m,
            "fraccion": m / n, "ic_lo": lo, "ic_hi": hi}


def main():
    d = pd.read_csv(os.path.join(K.OUT, "p6_nulo_perm.csv"))
    n_si = int((d["caja"] != "no").sum())
    d = d[d["caja"] == "no"].reset_index(drop=True)

    d["q_regla"] = np.nan
    for _, ix in d.groupby(["bloque", "respuesta"]).groups.items():
        d.loc[ix, "q_regla"] = K.bh(d.loc[ix, "p_perm"].values)
    d["q_regla_dummy"] = np.nan
    dum_all = d["tipo"] == "dummy"
    for _, ix in d[dum_all].groupby(["bloque", "respuesta"]).groups.items():
        d.loc[ix, "q_regla_dummy"] = K.bh(d.loc[ix, "p_perm"].values)
    d["q_global_metodo"] = np.nan
    for _, ix in d.groupby("metodo").groups.items():
        d.loc[ix, "q_global_metodo"] = K.bh(d.loc[ix, "p_perm"].values)
    d["q_global_mezcla"] = K.bh(d["p_perm"].values)

    dum, rea = d[dum_all], d[~dum_all]
    c_dum = conteo(dum, "q_regla")
    c_dum_alt = conteo(dum, "q_regla_dummy")
    c_rea = conteo(rea, "q_regla")
    c_rea_blq = conteo(rea, "q_bloque")
    c_rea_gme = conteo(rea, "q_global_metodo")
    c_rea_gmz = conteo(rea, "q_global_mezcla")

    filas = []
    # Tabla B: fraccion marcada segun el umbral k (cada prueba = una normalizacion de la regla de BH).
    for k in (1, 2, 3, 4):
        filas.append(fila_k("B_curva_k", k, "dummy", len(c_dum), int((c_dum >= k).sum())))
        filas.append(fila_k("B_curva_k", k, "real", len(c_rea), int((c_rea >= k).sum())))
        filas.append(fila_k("B_curva_k_alt_dummy_solas", k, "dummy", len(c_dum_alt), int((c_dum_alt >= k).sum())))
    # Tabla A: la regla a k = 2, en total y por respuesta (solo las dummy).
    for rs in sorted(c_dum.index.get_level_values("respuesta").unique()):
        sub = c_dum.xs(rs, level="respuesta")
        filas.append(fila_k("A_por_respuesta", 2, rs, len(sub), int((sub >= 2).sum())))
    filas.append(fila_k("A_por_respuesta", 2, "Total", len(c_dum), int((c_dum >= 2).sum())))
    # Tabla C: reales distinguidas por bloque x respuesta, con la regla por bloque y con la correccion global.
    ag_b = (c_rea_blq >= 2).groupby(level=[0, 1]).sum()
    ag_m = (c_rea_gme >= 2).groupby(level=[0, 1]).sum()
    ag_z = (c_rea_gmz >= 2).groupby(level=[0, 1]).sum()
    for bl, rs in ag_b.index:
        filas.append({"tabla": "C_global", "bloque": bl, "respuesta": rs, "n_unidades": 9,
                      "reales_bloque": int(ag_b.loc[(bl, rs)]), "reales_global_metodo": int(ag_m.loc[(bl, rs)]),
                      "reales_global_mezcla": int(ag_z.loc[(bl, rs)])})
    filas.append({"tabla": "C_global", "bloque": "TOTAL", "respuesta": "todos", "n_unidades": int(len(c_rea)),
                  "reales_bloque": int(ag_b.sum()), "reales_global_metodo": int(ag_m.sum()),
                  "reales_global_mezcla": int(ag_z.sum())})

    t = pd.DataFrame(filas, columns=COLS)
    os.makedirs(K.OUT, exist_ok=True)
    t.to_csv(os.path.join(K.OUT, "p6_calibra_regla.csv"), index=False)

    m2 = int((c_dum >= 2).sum()); lo, hi = K.wilson(m2, len(c_dum))
    alt2 = int((c_dum_alt >= 2).sum())
    md = ["# Sens2 F1 - calibracion de la regla \"distinguible\"", "",
          "Una variable dummy es una columna de numeros aleatorios que se incluye como control: no tiene relacion con la respuesta, "
          "asi que cada vez que la regla la marca cuenta como falso positivo.",
          "Regla: una variable es distinguible si su q (Benjamini-Hochberg por bloque y respuesta sobre todas las pruebas) queda por "
          "debajo de 0.05 en al menos 2 metodos. Aplicada a las 3 dummy en los 4 bloques y las 3 respuestas (36 evaluaciones), la regla "
          "marca %d (%.1f %%, IC 95 %% de Wilson [%.1f %%, %.1f %%])." % (m2, 100.0 * m2 / len(c_dum), 100.0 * lo, 100.0 * hi),
          "Por respuesta: " + ", ".join("%s %d de %d" % (rs, int((c_dum.xs(rs, level="respuesta") >= 2).sum()),
                                                          len(c_dum.xs(rs, level="respuesta")))
                                         for rs in sorted(c_dum.index.get_level_values("respuesta").unique())) + ".",
          "Al bajar el umbral a k = 1 salen %d de %d dummy (%.1f %%); con k = 3 y k = 4, ninguna." % (
              int((c_dum >= 1).sum()), len(c_dum), 100.0 * int((c_dum >= 1).sum()) / len(c_dum)),
          "Si la correccion se hiciera solo con las 3 dummy (sin las reales) ninguna queda marcada a ningun k (%d de %d a k = 2)." % (
              alt2, len(c_dum_alt)),
          "Familia global: al juntar todas las pruebas en una sola familia, las reales distinguidas suman %d con la regla por bloque, "
          "%d con BH por metodo y %d con los metodos mezclados (de %d en total)." % (
              int(ag_b.sum()), int(ag_m.sum()), int(ag_z.sum()), len(c_rea)),
          "Filas con caja distinta de \"no\": %d (la caja comun queda vacia/inviable y no se calcula)." % n_si]
    with open(os.path.join(K.OUT, "p6_calibra_regla.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))
    print("")
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Sens2 R2c - acuerdo agregado de las fronteras contando cada ventana una sola vez (sus dos bordes dan el mismo
n y los mismos aciertos). Entrada: r1_fronteras_contraste.csv y r2_fronteras_eficiencias.csv."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_filtro import SALIDA  # noqa: E402


def agregar(c, nombre):
    ok = c[c["n"] >= 5].copy()
    u = ok[(ok["forma"] == "escalon") | ~ok.duplicated(["centro", "variable", "forma", "n", "aciertos"])]
    fila = {"contraste": nombre}
    for tag, d in (("con_ventanas_dobles", ok), ("ventanas_una_vez", u)):
        fila["predictores_" + tag] = len(d)
        fila["evaluaciones_" + tag] = int(d["n"].sum())
        fila["acuerdo_" + tag] = d["aciertos"].sum() / d["n"].sum()
    if "acuerdo_clase_mayoritaria" in u:
        fila["mayoritaria_ventanas_una_vez"] = (u["acuerdo_clase_mayoritaria"].astype(float) * u["n"]).sum() / u["n"].sum()
    return fila


def main():
    r1 = pd.read_csv(os.path.join(SALIDA, "r1_fronteras_contraste.csv"))
    r2 = pd.read_csv(os.path.join(SALIDA, "r2_fronteras_eficiencias.csv"))
    out = pd.DataFrame([agregar(r1, "R1 otras variables libres"), agregar(r2, "R2 eficiencias a +-0.10 del centro")])
    out.to_csv(os.path.join(SALIDA, "r2_acuerdo_agregado.csv"), index=False)
    print(out.round(3).T.to_string())


if __name__ == "__main__":
    main()

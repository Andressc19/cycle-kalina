# -*- coding: utf-8 -*-
"""Sens2 F1 - p6_mO2: estadisticas del subenfriamiento m_O2 (K) de los puntos KALINA.

Cuantas filas KALINA quedan por debajo de 1, 3 y 5 K de m_O2. Se calcula para `todos` y para
cada centro cuyo nombre empieza por C1, C2, C3 y C4 (filas separadas). Salida:
`resultados/2026-10-18_sens2_F1/p6_mO2_estadisticas.csv` (porcentajes de 0 a 100).
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
import x1_cargar as X  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
CORTES = (1.0, 3.0, 5.0)
CENTROS = ("C1", "C2", "C3", "C4")


def kalina_con_mo2(d):
    """Filas KALINA con m_O2 no nulo."""
    return d[(d["clasificacion"] == "KALINA") & d["m_O2"].notna()]


def _fila(centro, k):
    return {"centro": centro, "n": int(len(k)),
            "p_menor_1K": 100.0 * float((k["m_O2"] < CORTES[0]).mean()),
            "p_menor_3K": 100.0 * float((k["m_O2"] < CORTES[1]).mean()),
            "p_menor_5K": 100.0 * float((k["m_O2"] < CORTES[2]).mean())}


def estadisticas(k):
    """Tabla de todos y de C1, C2, C3 y C4."""
    filas = [_fila("todos", k)]
    for c in CENTROS:
        filas.append(_fila(c, k[k["centro"].astype(str).str.startswith(c)]))
    return pd.DataFrame(filas, columns=["centro", "n", "p_menor_1K", "p_menor_3K", "p_menor_5K"])


def main():
    os.makedirs(SALIDA, exist_ok=True)
    k = kalina_con_mo2(X.cargar_todo())
    est = estadisticas(k)
    ruta = os.path.join(SALIDA, "p6_mO2_estadisticas.csv")
    est.to_csv(ruta, index=False)
    print("m_O2 (K) de los KALINA: porcentaje por debajo de 1, 3 y 5 K")
    print("%-7s %6s %9s %9s %9s" % ("centro", "n", "p<1K", "p<3K", "p<5K"))
    for _, r in est.iterrows():
        print("%-7s %6d %9.1f %9.1f %9.1f"
              % (r["centro"], r["n"], r["p_menor_1K"], r["p_menor_3K"], r["p_menor_5K"]))
    print("escrito:", ruta)


if __name__ == "__main__":
    main()

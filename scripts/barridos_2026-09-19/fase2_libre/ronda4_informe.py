"""Fase 2, ronda 4 (tarea 2026-09-28-fase2-ronda4-campana-3h) — reporte final.

Arma el informe de la campana extendida LEYENDO UNICAMENTE
resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv (el mismo
archivo al que se hizo append; no escribe nada, no crea archivos). Separa las
filas de la ronda 4 de las 184 de las rondas 1-3 usando el conjunto de columnas
de `ronda4_columnas.columnas()`, de modo que las comparaciones no mezclen los
dos regimenes de efectividades (las rondas 1-3 usaban eps_hrvg=0.85,
eps_reg=0.75 y eps_cond hasta 0.95; esta ronda exige [0.75, 0.85] en las tres).

Por columna (columna = todo menos P_baja) calcula, sobre los puntos que
convergieron:
  * `P_baja*` = menor P_baja clasificada KALINA (el "minimo que logra KALINA");
  * el bracket que lo envuelve (ultimo CORREGIBLE por debajo) y el cruce O2=0
    interpolado linealmente, que es la estimacion fina de la frontera;
  * si la columna nunca llega a KALINA dentro del rango explorado, el mayor
    P_baja probado y su margen O2, para poder decir "no alcanzado" con dato.

Uso:  python ronda4_informe.py      (o: ronda4_campana.py informe)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ronda4_columnas import CSV, SIN_PB  # noqa: E402

# Las rondas 1-3 dejaron 184 filas al principio del archivo y esta ronda solo
# hizo APPEND, asi que las filas de la ronda 4 son exactamente las posteriores a
# ese indice. No se puede discriminar por clave de columna: 4 de las columnas de
# la ronda 4 (submalla de efectividades con eps_hrvg=0.85, eps_reg=0.75,
# eta_t=0.85, eta_p=0.75) coinciden con combinaciones ya evaluadas antes.
N_PREVIAS = 184


def _clave_fila(r) -> tuple:
    return tuple(round(float(r[v]), 3) for v in SIN_PB)


def dividir() -> tuple:
    """(campana de la ronda 4, filas previas de las rondas 1-3)."""
    df = pd.read_csv(CSV)
    assert len(df) > N_PREVIAS, "el CSV crecio por debajo de las 184 filas previas"
    previas = df.iloc[:N_PREVIAS].copy()
    assert (previas["eps_hrvg"] == 0.85).all() and (previas["eps_reg"] == 0.75).all(), \
        "las filas previas ya no son las de las rondas 1-3 (se perdio el orden)"
    return df.iloc[N_PREVIAS:].copy(), previas


def frontera(sub: pd.DataFrame) -> dict:
    """{clave de columna: (P_baja*, cruce O2=0, P_baja max, O2 en el max)}."""
    out: dict = {}
    for k, g in sub.groupby(sub.apply(_clave_fila, axis=1)):
        g = g[g["convergio"].astype(bool) & g["O2_margen"].notna()]
        if g.empty:
            continue
        g = g.sort_values("P_baja")
        kal = g[g["clasificacion"] == "KALINA"]
        p_max = float(g["P_baja"].iloc[-1])
        o2_max = float(g["O2_margen"].iloc[-1])
        if kal.empty:
            out[k] = (None, None, p_max, o2_max)
            continue
        p_star = float(kal["P_baja"].iloc[0])
        abajo = g[g["P_baja"] < p_star]
        if abajo.empty:
            out[k] = (p_star, None, p_max, o2_max)     # KALINA ya en el piso
            continue
        p_lo = float(abajo["P_baja"].iloc[-1])
        o2_lo = float(abajo["O2_margen"].iloc[-1])
        o2_hi = float(g[g["P_baja"] == p_star]["O2_margen"].iloc[0])
        cruce = (p_lo + (p_star - p_lo) * (-o2_lo) / (o2_hi - o2_lo)
                 if o2_hi != o2_lo else p_star)
        out[k] = (p_star, cruce, p_max, o2_max)
    return out


def _f(v, fmt="{:7.0f}"):
    return "   --  " if v is None else fmt.format(v)


def _linea(k, f) -> str:
    pa, xb, et, ep, eh, er, ec = k
    return (f"Pa={pa:.0f} x_b={xb:.3f} eta_t={et:.2f} eta_p={ep:.2f} "
            f"eps_hrvg={eh:.2f} eps_reg={er:.2f} eps_cond={ec:.2f}")


def informe() -> None:
    camp, prev = dividir()
    fr = frontera(camp)
    print("=" * 78)
    print("FASE 2 RONDA 4 - CAMPANA EXTENDIDA, efectividades en [0.75, 0.85]")
    print("=" * 78)
    print(f"Ancla: T_fuente=470.0 K, T_sumidero=300.032917 K, "
          f"T_amb_diseno=303.55 K, motor TeqpAdapter.")
    print(f"Puntos de la ronda 4 en el CSV: {len(camp)}   "
          f"(filas previas de las rondas 1-3 conservadas: {len(prev)})")
    print(f"Clasificacion de la ronda 4: "
          f"{camp['clasificacion'].value_counts().to_dict()}")
    print(f"Columnas cubiertas: {len(fr)}   |   de las cuales con KALINA: "
          f"{sum(1 for v in fr.values() if v[0] is not None)}")
    dups = pd.read_csv(CSV).duplicated(subset=list(SIN_PB) + ["P_baja"]).sum()
    print(f"Duplicados de 8-tuplo en TODO el archivo: {int(dups)}")
    print(f"Rangos: eps_hrvg [{camp.eps_hrvg.min():.2f}, {camp.eps_hrvg.max():.2f}] "
          f"| eps_reg [{camp.eps_reg.min():.2f}, {camp.eps_reg.max():.2f}] "
          f"| eps_cond [{camp.eps_cond.min():.2f}, {camp.eps_cond.max():.2f}] "
          f"| x_b [{camp.x_b.min():.3f}, {camp.x_b.max():.3f}] "
          f"| P_baja [{camp.P_baja.min():.0f}, {camp.P_baja.max():.0f}] kPa")

    print("\n--- A) MALLA PRINCIPAL: P_baja* (menor P_baja KALINA) ---")
    print("    base eps_hrvg=eps_reg=0.80, P_alta=3000, eta_t=0.85, eta_p=0.75")
    base = (3000., 0.85, 0.75, 0.80, 0.80)
    print(f"{'x_b':>6s} | " + " | ".join(
        f"ec={ec:.2f}: P* / cruce / P_max"
        for ec in (0.75, 0.80, 0.85)))
    for xb in (0.40, 0.425, 0.45, 0.475, 0.50):
        celdas = []
        for ec in (0.75, 0.80, 0.85):
            v = fr.get((3000., xb, 0.85, 0.75, 0.80, 0.80, ec))
            if v is None:
                celdas.append("   sin datos      ")
            else:
                p_star, cruce, p_max, o2 = v
                celdas.append(f"{_f(p_star, '{:6.0f}')}/"
                              f"{_f(cruce, '{:6.0f}')}/{_f(p_max, '{:6.0f}')}")
        print(f"{xb:6.3f} | " + " | ".join(celdas))
    print("  P* = menor P_baja KALINA [kPa] | cruce = interpolacion lineal de "
          "O2=0 en el bracket | P_max = mayor P_baja probado")

    print("\n--- B) FRONTERA POR COLUMNA (las 59 columnas de la campana) ---")
    sin_kal = []
    for k in sorted(fr, key=lambda k: (k[6], -k[1], k[0])):
        p_star, cruce, p_max, o2 = fr[k]
        if p_star is None:
            sin_kal.append((k, p_max, o2))
        else:
            print(f"  {_linea(k, fr)} -> P_baja*={_f(p_star, '{:6.0f}')} kPa, "
                  f"cruce O2=0 ~ {_f(cruce, '{:6.0f}')} kPa")
    if sin_kal:
        print("\n  Columnas SIN KALINA dentro del rango explorado "
              "(frontera no alcanzada):")
        for k, p_max, o2 in sin_kal:
            print(f"  {_linea(k, fr)} -> P_baja* = -- ; mejor punto probado "
                  f"P_baja={p_max:.0f} kPa con O2_margen={o2:+.2f} K")

    print("\n--- C) COMPARACION vs RONDAS 1-3 (eps_cond mas alto) ---")
    print("    'P_baja* de las rondas 1-3' = menor P_baja KALINA de esas filas")
    print("    (eps_hrvg=0.85, eps_reg=0.75, eps_cond hasta 0.95, x_b hasta 0.35)")
    fprev = frontera(prev)
    print(f"{'x_b':>6s} | {'rondas 1-3':>32s} | {'ronda 4 (eps_cond<=0.85)':>34s}")
    for xb in (0.40, 0.425, 0.45, 0.475, 0.50):
        p3 = [v[0] for k, v in fprev.items() if k[1] == xb and v[0] is not None]
        p4 = [v[0] for k, v in fr.items() if k[1] == xb and v[0] is not None]
        s3 = (f"min {min(p3):.0f} kPa en {len(p3)} col" if p3 else "sin KALINA")
        s4 = (f"min {min(p4):.0f} kPa en {len(p4)} col" if p4 else "sin KALINA")
        print(f"{xb:6.3f} | {s3:>32s} | {s4:>34s}")
    print("\n  Detalle del mejor eps_cond de las rondas 1-3 (el mas alto, 0.95):")
    for xb in (0.40, 0.425, 0.45, 0.475, 0.50):
        v = fprev.get((3000., xb, 0.85, 0.75, 0.85, 0.75, 0.95))
        if v:
            print(f"    x_b={xb:.3f}: eps_cond=0.95 -> P_baja* = "
                  f"{'--' if v[0] is None else f'{v[0]:.0f} kPa'} "
                  f"(rondas 1-3, resto de la base)")
    print("=" * 78)


if __name__ == "__main__":
    informe()

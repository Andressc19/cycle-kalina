"""A3 y A4 del CIERRE del benchmark: la discrepancia de la fila sana y la elección de
la configuración de MB. NO mide nada: solo recalcula cifras DESDE los CSV.

  * A3 — MB_t6_STno frente a M0 en las 30 filas "sanas": qué filas difieren, en qué
    columna, y con qué evidencia (nF, fase del fallo, mensajes, `eta_original`).
  * A4 — tabla de las configuraciones de MB con ST no sobre las 40 filas que M0 no
    resuelve, y elección con el criterio EXACTO del director: la de MENOR tope que
    recupera el MISMO número de filas que "sin tope"; si empatan en filas, la de
    menor tiempo total sobre las 40.

Uso:  python scripts/benchmark_cierre_informe.py [a3|a4|todo]
"""
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                    # noqa: E402
from benchmark_cierre_modos import (CSV_A, CSV_TOPES, OUT, TOPE_DE,     # noqa: E402
                                    cfg_nombre)

LOG = OUT / "progreso_cierre.log"
SIN_TOPE = cfg_nombre(("MB", None, False))
ST_NO = [c for c in TOPE_DE if c.endswith("STno")]      # criterio del director: ST no
TOL_ETA, TOL_T1 = 1e-6, 1e-4


def log(msg):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()


def a3():
    """MB_t6_STno frente a M0 en las 30 filas sanas, fila a fila."""
    s = pd.read_csv(CSV_A).query("etapa == 'A2'")
    m0 = s[s.config == "M0"].set_index(["csv_origen", "fila_csv"]).sort_index()
    mb = s[s.config == "MB_t6_STno"].set_index(["csv_origen", "fila_csv"]).sort_index()
    assert list(m0.index) == list(mb.index), "las 30 sanas no coinciden"
    ambas = m0.convergio.astype(bool) & mb.convergio.astype(bool)
    print(f"A3: {len(m0)} filas sanas · M0 converge {int(m0.convergio.sum())} · "
          f"MB_t6_STno converge {int(mb.convergio.sum())} · ambas "
          f"{int(ambas.sum())}")
    d_eta = (m0.eta - mb.eta).abs()
    d_t1 = (m0.T1_sol - mb.T1_sol).abs()
    d_nf = (m0.nF - mb.nF).abs()
    print(f"    en las {int(ambas.sum())} que ambas resuelven: max|d eta| = "
          f"{d_eta[ambas].max():.3e} (tol {TOL_ETA}), max|d T1_sol| = "
          f"{d_t1[ambas].max():.3e} K (tol {TOL_T1}), filas con nF distinto = "
          f"{int((d_nf[ambas] > 0).sum())}, filas con `reintento_usado` = "
          f"{int(mb.reintento_usado[ambas].sum())}")
    dif = sorted(set(m0.index[~ambas.values]))
    print(f"    filas donde NO coinciden: {len(dif)} -> {dif}")
    cols = ["grupo", "clasificacion_original", "eta_original", "convergio", "causa",
            "clasificacion", "eta", "T1_sol", "nF", "t_s", "reintento_usado",
            "fase_fallo", "punto_cascada", "msg", "msg_intento1", "B_verificado",
            "B_dh4s"]
    for k in dif:
        print("\n    --- evidencia de la fila", k, "---")
        cmp = pd.DataFrame({"M0": m0.loc[k, cols], "MB_t6_STno": mb.loc[k, cols]})
        for c in ("msg", "msg_intento1"):
            cmp.loc[c] = [str(cmp.loc[c, "M0"])[:150], str(cmp.loc[c, "MB_t6_STno"])[:150]]
        print(cmp.to_string())
        d = abs(float(mb.loc[k, "eta"]) - float(mb.loc[k, "eta_original"]))
        print(f"    |eta(MB) - eta_original| = {d:.3e}  "
              f"(clasificacion_original={mb.loc[k, 'clasificacion_original']}, "
              f"clasificacion(MB)={mb.loc[k, 'clasificacion']})")
    log(f"A3: {len(dif)} discrepancia(s) entre M0 y MB_t6_STno en las 30 sanas: {dif}; "
        f"max|d eta| en las comunes = {d_eta[ambas].max():.3e}")
    return dif


def a4():
    """Tabla de las configuraciones de MB con ST no sobre las 40 filas que M0 no
    resuelve, y elección con el criterio exacto del director."""
    a = pd.read_csv(CSV_A).query("etapa == 'A1'")
    t = pd.concat([a, pd.read_csv(CSV_TOPES)], ignore_index=True)
    t = t[t.config.isin(ST_NO)]
    g = (t.groupby("config")
          .agg(filas_medidas=("convergio", "size"),
               filas_recuperadas=("convergio", "sum"),
               t_total_s=("t_s", "sum"), nF_medio=("nF", "mean"),
               t_mediana_s=("t_s", "median"), t_max_s=("t_s", "max"))
          .reindex([c for c in ST_NO if c in set(t.config)]))
    g["tope"] = [TOPE_DE[c] for c in g.index]
    g = g.sort_values("tope")
    g["filas_por_1000s"] = (g.filas_recuperadas / (g.t_total_s / 1000.0)).round(3)
    g = g[["tope", "filas_medidas", "filas_recuperadas", "t_total_s", "t_mediana_s",
           "t_max_s", "nF_medio", "filas_por_1000s"]]
    print("\nA4: MB con ST no sobre las 40 filas que M0 no resuelve "
          "(M0 recupera 0/40)\n")
    print(g.round(2).to_string())
    print("\n  control de sumas: cada configuracion mide 40 filas -> "
          f"{int(g.filas_medidas.sum())} mediciones en la tabla = "
          f"{len(g)} configs x 40")
    assert (g.filas_medidas == 40).all(), "alguna configuracion no midio 40 filas"
    ref = int(g.loc[SIN_TOPE, "filas_recuperadas"])
    cand = g[g.filas_recuperadas == ref].sort_values(["tope", "t_total_s"])
    elegido = cand.index[0]
    print(f"\n  'sin tope' ({SIN_TOPE}) recupera {ref}/40. Candidatas (mismas filas): "
          f"{list(cand.index)}")
    print(f"  ELEGIDA = {elegido} (tope {TOPE_DE[elegido]}, "
          f"t_total = {g.loc[elegido, 't_total_s']:.1f} s, "
          f"nF medio = {g.loc[elegido, 'nF_medio']:.2f}, "
          f"{g.loc[elegido, 'filas_por_1000s']:.2f} filas/1000 s)")
    descartadas = [c for c in g.index if c not in cand.index]
    if descartadas:
        print("  Descartadas por recuperar MENOS filas que 'sin tope': "
              + ", ".join(f"{c} ({int(g.loc[c, 'filas_recuperadas'])}/40)" for c in
                          descartadas))
    log(f"A4: 'sin tope' recupera {ref}/40; candidatas {list(cand.index)}; "
        f"ELEGIDA = {elegido} (tope {TOPE_DE[elegido]}, "
        f"t={g.loc[elegido, 't_total_s']:.1f} s)")
    for c, r in g.iterrows():
        log(f"  A4 tabla: {c:16s} tope={r.tope:>7} filas={int(r.filas_recuperadas):2d}/"
            f"{int(r.filas_medidas)} t={r.t_total_s:8.1f}s nF={r.nF_medio:5.2f} "
            f"filas/1000s={r.filas_por_1000s:.2f}")
    return elegido, g, ref


def main() -> None:
    etapa = sys.argv[1].lower() if len(sys.argv) > 1 else "todo"
    if etapa in ("a3", "todo"):
        a3()
    if etapa in ("a4", "todo"):
        a4()


if __name__ == "__main__":
    main()

"""Sensibilidad 1, Ronda 2 — capa de DATOS del reporte (`ronda2_filas.csv`).

KALINA confiable: clase KALINA, `fuera_rango` falso/vacio y todo `eta_*`/`eps_*` en [0.40, 0.95].
"""
from __future__ import annotations

import csv
from collections import Counter

import numpy as np

BARRIDOS = ("N2", "N5", "N6")
N2_VARS = ("T_fuente", "P_alta", "P_baja", "x_b", "T_sumidero")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
STATS = ("minimo", "p10", "mediana", "p90", "maximo")
LETRA = dict(KALINA="K", CORREGIBLE="c", INVIABLE="i", NO_CONVERGIO="n")


def num(v):
    """float o None (tolera '', 'None')."""
    try:
        return None if v in (None, "", "None") else float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, n=6) -> str:
    x = v if isinstance(v, (int, float)) else num(v)
    return "—" if x is None else f"{x:.{n}g}"


def leer_filas(path) -> list:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clase(f) -> str:
    return f.get("clasificacion") or "NO_CONVERGIO"


def es_kalina(f) -> bool:
    return clase(f) == "KALINA"


def fuera_rango(f) -> bool:
    return str(f.get("fuera_rango") or "").strip().lower() in ("true", "1")


def confiable(f) -> bool:
    """Clase KALINA, sin `fuera_rango` y todos los eta_*/eps_* en [0.40, 0.95]."""
    if not es_kalina(f) or fuera_rango(f):
        return False
    return all(num(f.get(k)) is not None and 0.40 - 1e-9 <= num(f.get(k))
               <= 0.95 + 1e-9 for k in ETAS_EPS)


def percentiles(vals: list) -> dict:
    """min, p10, mediana, p90, max (y n). `None` si no hay datos."""
    if not vals:
        return dict(n=0, minimo=None, p10=None, mediana=None, p90=None,
                    maximo=None)
    q = np.percentile(np.asarray(vals, float), [0, 10, 50, 90, 100])
    return dict(n=len(vals), minimo=float(q[0]), p10=float(q[1]),
                mediana=float(q[2]), p90=float(q[3]), maximo=float(q[4]))


def centros_de(filas: list, barrido: str) -> list:
    return sorted({f.get("centro") for f in filas if f.get("barrido") == barrido})


def grupo(filas: list, barrido: str, centro: str) -> list:
    return [f for f in filas if f.get("barrido") == barrido
            and (centro == "TOTAL" or f.get("centro") == centro)]


def resumen_por(filas: list, barrido: str, centro: str) -> dict:
    """Conteos por clase y eta (min/mediana/max) entre KALINA confiables."""
    rs = grupo(filas, barrido, centro)
    cnt = Counter(clase(f) for f in rs)
    conf = [f for f in rs if confiable(f)]
    q = percentiles([v for v in (num(f.get("eta")) for f in conf)
                     if v is not None])
    row = dict(barrido=barrido, centro=centro, n_puntos=len(rs),
               n_kalina=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
               n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
               n_kalina_confiable=len(conf),
               n_kalina_fuera_rango=sum(1 for f in rs
                                        if es_kalina(f) and fuera_rango(f)))
    for k, s in (("min", "minimo"), ("mediana", "mediana"), ("max", "maximo")):
        row[f"eta_{k}_pct"] = None if q[s] is None else 100 * q[s]
    return row


def n2_ventanas(filas: list) -> dict:
    """N2: percentiles entre KALINA (confiables+no)."""
    n2 = [f for f in filas if f.get("barrido") == "N2"]
    kal = [f for f in n2 if es_kalina(f)]
    row = dict(n_puntos=len(n2), n_kal_total=len(kal))
    for v in N2_VARS:
        vals = [num(f.get(v)) for f in kal if num(f.get(v)) is not None]
        row.update({f"{v}_{s}": x for s, x in percentiles(vals).items()
                    if s in STATS})
    return row


def n2_top5(filas: list) -> list:
    kal = [f for f in filas if f.get("barrido") == "N2" and es_kalina(f)]
    return sorted(kal, key=lambda f: num(f.get("eta")) or -1, reverse=True)[:5]


def n5_frontera(filas: list) -> list:
    n5 = [f for f in filas if f.get("barrido") == "N5"]
    out = []
    for tf in sorted({num(f.get("T_fuente")) for f in n5}):
        for ts in sorted({num(f.get("T_sumidero")) for f in n5}):
            g = [f for f in n5 if num(f.get("T_fuente")) == tf
                 and num(f.get("T_sumidero")) == ts and es_kalina(f)]
            base = dict(T_fuente=tf, T_fuente_C=tf - 273.15,
                        T_sumidero=ts, T_sumidero_C=ts - 273.15)
            if not g:
                out.append(dict(base, P_baja_min=None, eta_max_pct=None,
                                P_baja_eta_max=None, hay_confiable=False))
                continue
            # P_baja minima con KALINA
            pbmin = min(g, key=lambda x: num(x.get("P_baja")) or 1e18)
            # eta maxima entre sus KALINA y P_baja que la logra
            etamax = max(g, key=lambda x: num(x.get("eta")) or -1)
            em = num(etamax.get("eta"))
            out.append(dict(base,
                            P_baja_min=num(pbmin.get("P_baja")),
                            eta_max_pct=None if em is None else 100 * em,
                            P_baja_eta_max=num(etamax.get("P_baja")),
                            hay_confiable=any(confiable(x) for x in g)))
    return out


def celda(f) -> str:
    if f is None:
        return "?"
    c = clase(f)
    letra = LETRA.get(c, "?")
    if c != "NO_CONVERGIO" and fuera_rango(f):
        return letra.lower()
    return letra


def n5_mallas_por_tf(filas: list) -> dict:
    n5 = [f for f in filas if f.get("barrido") == "N5"]
    idx = {(num(f.get("T_fuente")), num(f.get("T_sumidero")),
            num(f.get("P_baja"))): f for f in n5}
    tfs = sorted({num(f.get("T_fuente")) for f in n5})
    tss = sorted({num(f.get("T_sumidero")) for f in n5})
    pbs = sorted({num(f.get("P_baja")) for f in n5})
    res = {}
    for tf in tfs:
        tf_c = tf - 273.15
        cab = ["P_baja \\ T_sum [C]"] + [f"{ts - 273.15:.0f}" for ts in tss]
        lines = []
        for pb in pbs:
            cells = [f"{pb:.0f}"]
            for ts in tss:
                cells.append(celda(idx.get((tf, ts, pb))))
            lines.append(cells)
        res[tf_c] = (cab, lines, tss, pbs)
    return res


def n6_cubos(filas: list) -> dict:
    n6 = [f for f in filas if f.get("barrido") == "N6"]
    out = {}
    for centro in sorted({f.get("centro") for f in n6}):
        g = [f for f in n6 if f.get("centro") == centro]
        out[centro] = sorted(g, key=lambda x: (num(x.get("eta_t")), num(x.get("eps_hrvg")), num(x.get("eps_reg"))))
    return out


def n6_mejor_barato(filas: list) -> dict:
    n6 = [f for f in filas if f.get("barrido") == "N6"]
    best = {}
    for centro in sorted({f.get("centro") for f in n6}):
        conf = [f for f in n6 if f.get("centro") == centro and confiable(f)]
        if not conf:
            best[centro] = None
            continue
        # minimizar suma de efectividades (barato): eta_t + eps_hrvg + eps_reg
        def suma(f):
            return (num(f.get("eta_t")) or 1) + (num(f.get("eps_hrvg")) or 1) + (num(f.get("eps_reg")) or 1)
        best[centro] = min(conf, key=suma)
    return best


def tiempo_agotado(filas: list) -> list:
    por = {}
    for f in filas:
        msg = f.get("mensaje") or ""
        if msg.startswith("tiempo_agotado") or msg == "tiempo_agotado_600s":
            k = (f.get("barrido"), f.get("centro"))
            por[k] = por.get(k, 0) + 1
    return [f"- {b} / {c}: {n} punto(s)" for (b, c), n in sorted(por.items())]

"""M4b — tablas de PRESIONES sobre los 500 puntos (final_M4b §Diseño 4).

(b) `m4b_rangos_presiones.csv`: mín, p5, mediana, p95 y máx de P_alta, P_baja,
dP y rP dentro de KALINA, los mismos estadísticos de los no KALINA genuinos, y
el KS con su valor p entre los dos grupos. (c)/(d)/(e) franjas iguales de
P_alta (6 entre 2000 y 5000 kPa), T_fuente (6 entre 380 y 500 K) y T_sumidero
(4 entre 278.15 y 303.55 K) con los rangos de los KALINA. (g)
`m4b_bloqueo_por_rP.csv`: entre los genuinos no KALINA, el conteo de
`codigos_falla` por zona de rP respecto de los percentiles 5–95 de KALINA.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp

from m4_datos import genu
from m4b_datos import OUT, escribir
from m4b_presiones_fig import hist_dP_rP, plano_presiones

VPRES = ("P_alta", "P_baja", "dP", "rP")
FRANJAS = {"P_alta": (2000.0, 5000.0, 6),
           "T_fuente": (380.0, 500.0, 6),
           "T_sumidero": (278.15, 303.55, 4)}
ARCHIVOS = {"P_alta": "m4b_ventana_por_palta.csv",
            "T_fuente": "m4b_ventana_por_tfuente.csv",
            "T_sumidero": "m4b_ventana_por_tsumidero.csv"}
CRANGOS = ["variable", "grupo", "n", "min", "p05", "mediana", "p95", "max",
           "KS", "p_valor"]
CFRANJA = ["variable", "franja", "lo", "hi", "n", "n_kalina", "pct_kalina",
           "P_baja_min", "P_baja_max", "dP_min", "dP_max", "rP_min", "rP_max"]
CBLOQ = ["zona", "codigos_falla", "n"]
ZONAS = ("rP < p5 KALINA", "rP dentro de [p5, p95]", "rP > p95 KALINA")


def _stats(vals: list) -> dict:
    """n, mín, p5, mediana, p95 y máx de `vals` (vacío → todos `None`)."""
    if not vals:
        return dict(n=0, min=None, p05=None, mediana=None, p95=None, max=None)
    a = np.array(vals, dtype=float)
    p05, med, p95 = np.percentile(a, [5, 50, 95])
    return dict(n=len(vals), min=float(a.min()), p05=float(p05),
                mediana=float(med), p95=float(p95), max=float(a.max()))


def tabla_rangos(filas: list) -> list:
    """(b) una fila por (variable, grupo) con los estadísticos y el KS."""
    out = []
    for v in VPRES:
        kal = [f[v] for f in filas
               if f["clasificacion"] == "KALINA" and f.get(v) is not None]
        nog = [f[v] for f in filas
               if genu(f) and f["clasificacion"] != "KALINA"
               and f.get(v) is not None]
        st = ks_2samp(kal, nog) if kal and nog else None
        ks = float(st[0]) if st is not None else None
        pv = float(st[1]) if st is not None else None
        for grupo, vals in (("KALINA", kal), ("no_KALINA_genuino", nog)):
            out.append(dict(variable=v, grupo=grupo, **_stats(vals),
                            KS=ks, p_valor=pv))
    return out


def tabla_franjas(filas: list, var: str) -> list:
    """(c)/(d)/(e) franjas iguales de `var` con `n`, % y rangos de KALINA."""
    lo, hi, k = FRANJAS[var]
    bor = [lo + (hi - lo) * i / k for i in range(k + 1)]
    out = []
    for i in range(k):
        a, b = bor[i], bor[i + 1]
        sel = [f for f in filas if f.get(var) is not None
               and (a <= f[var] < b if i < k - 1 else a <= f[var] <= b)]
        kal = [f for f in sel if f["clasificacion"] == "KALINA"]
        n = len(sel)
        row = dict(variable=var, franja=i + 1, lo=a, hi=b, n=n,
                   n_kalina=len(kal),
                   pct_kalina=round(100.0 * len(kal) / n, 1) if n else None)
        for v in ("P_baja", "dP", "rP"):
            vals = [f[v] for f in kal if f.get(v) is not None]
            row[f"{v}_min"] = min(vals) if vals else None
            row[f"{v}_max"] = max(vals) if vals else None
        out.append(row)
    return out


def tabla_bloqueo(filas: list, p05: float, p95: float) -> list:
    """(g) genuinos no KALINA: `codigos_falla` contado por zona de rP."""
    cuenta = {}
    for f in filas:
        if not genu(f) or f["clasificacion"] == "KALINA" or f.get("rP") is None:
            continue
        if f["rP"] < p05:
            zona = ZONAS[0]
        elif f["rP"] > p95:
            zona = ZONAS[2]
        else:
            zona = ZONAS[1]
        cod = f["codigos_falla"] or "(sin codigos)"
        cuenta[zona, cod] = cuenta.get((zona, cod), 0) + 1
    o = {z: i for i, z in enumerate(ZONAS)}
    filas_out = [dict(zona=z, codigos_falla=c, n=n)
                 for (z, c), n in sorted(cuenta.items(),
                                         key=lambda kv: (o[kv[0][0]], -kv[1],
                                                         kv[0][1]))]
    return filas_out


def main(filas: list) -> dict:
    """Escribe (b)–(g) y las dos figuras; devuelve las filas del reporte."""
    rangos = tabla_rangos(filas)
    escribir(OUT, "m4b_rangos_presiones.csv", CRANGOS, rangos)
    franjas = {}
    for var in FRANJAS:
        franjas[var] = tabla_franjas(filas, var)
        escribir(OUT, ARCHIVOS[var], CFRANJA, franjas[var])
    kal = [f["rP"] for f in filas
           if f["clasificacion"] == "KALINA" and f.get("rP") is not None]
    p05, p95 = (float(x) for x in np.percentile(np.array(kal), [5, 95]))
    bloqueo = tabla_bloqueo(filas, p05, p95)
    escribir(OUT, "m4b_bloqueo_por_rP.csv", CBLOQ, bloqueo)
    plano_presiones(filas)
    hist_dP_rP(filas)
    return dict(rangos=rangos, franjas=franjas, bloqueo=bloqueo,
                rp_kalina=(p05, p95))

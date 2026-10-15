"""Sensibilidad 1, N7 — puntos de N7A (una variable) y N7B (pares).
Centros de `ronda1_filas.csv`: C3 (150 C), C4 (110 C); eta_p=0.80, m_b=1.0.
N7A OFAT base-incluida; N7B mallas 7x7 (descarte P_alta < 1.3*P_baja).
"""
import csv
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-15_sens1_N7"

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
COMBO = tuple(VARIABLES) + ("m_b",)
M_B = 1.0
CENTROS = (
    ("C3", dict(T_fuente=423.15, T_sumidero=280.5, P_alta=3150.0,
                P_baja=950.0, x_b=0.75, m_b=M_B, eta_t=0.85, eta_p=0.80,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)),
    ("C4", dict(T_fuente=383.15, T_sumidero=282.5, P_alta=3880.0,
                P_baja=910.0, x_b=0.88, m_b=M_B, eta_t=0.85, eta_p=0.80,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)))
CENTROS_D = dict(CENTROS)
NOMBRE_ORIGEN = {"C3": "N1-T150-19", "C4": "N1-T110-06"}

# N7A: rejillas OFAT (T_fuente en C)
_TF_C = [70 + 10 * i for i in range(24)]                 # 70..300 C
_TS = [round(278.15 + 2.5 * i, 2) for i in range(11)]    # 278.15..303.15 K
_PALTA = [1000.0 + 250 * i for i in range(17)]           # 1000..5000 kPa
_PBAJA = [200.0 + 100 * i for i in range(19)]            # 200..2000 kPa
_XB = [round(0.30 + 0.05 * i, 2) for i in range(14)]     # 0.30..0.95
_EF = [round(0.40 + 0.05 * i, 2) for i in range(12)]     # 0.40..0.95
_CON_BASE = ("T_fuente", "T_sumidero", "P_baja")         # spec: "+ base"
_REJ = {"T_sumidero": _TS, "P_baja": _PBAJA, "P_alta": _PALTA, "x_b": _XB}

# N7B: mallas 7x7 (unidades de la spec; T_fuente en C)
PARES = (("B1", "T_fuente", "P_baja"), ("B2", "P_baja", "x_b"),
         ("B3", "P_alta", "P_baja"), ("B4", "eps_cond", "T_sumidero"))
PARES_D = {p: (a, b) for p, a, b in PARES}
GRID = {
    "T_fuente": {"C3": [110, 130, 140, 150, 160, 180, 200],
                 "C4": [80, 90, 100, 110, 120, 135, 150]},
    "P_baja": {"C3": [500, 650, 800, 950, 1100, 1300, 1600],
               "C4": [500, 650, 800, 910, 1050, 1250, 1500]},
    "x_b": {"C3": [0.55, 0.62, 0.68, 0.75, 0.82, 0.88, 0.95],
            "C4": [0.65, 0.72, 0.78, 0.83, 0.88, 0.92, 0.95]},
    "P_alta": {"C3": [2000, 2500, 3150, 3500, 4000, 4500, 5000],
               "C4": [2500, 3000, 3400, 3880, 4300, 4600, 5000]},
    "eps_cond": {"C3": [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                 "C4": [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]},
    "T_sumidero": {"C3": [278.15, 280.5, 283.15, 288.15, 293.15, 298.15,
                          303.15],
                   "C4": [278.15, 282.5, 285.65, 288.15, 293.15, 298.15,
                          303.15]},
}
META = ("id_punto", "barrido", "centro", "variable", "valor", "par",
        "var1", "val1", "var2", "val2")
CM_DIS = list(META) + list(COMBO)
CM_DESC = ["barrido", "centro", "nivel", "n_candidatas", "n_descartados",
           "n_duplicados", "n_final"]


def rejilla_a(var, centro, base_val):
    """Valores del barrido OFAT de `var` (K si T_fuente)."""
    vals = ([round(c + 273.15, 2) for c in _TF_C] if var == "T_fuente"
            else list(_REJ.get(var, _EF)))
    if var in _CON_BASE and not any(abs(v - base_val) <= 1e-9 for v in vals):
        vals.append(round(base_val, 2))
    return sorted(vals)


def valores_brutos(var, centro):
    """Rejilla de N7B en unidades de la spec (C si T_fuente)."""
    return list(GRID[var][centro])

def valores(var, centro):
    """Rejilla de N7B en unidades de diseno (K si T_fuente)."""
    if var == "T_fuente":
        return [round(c + 273.15, 2) for c in GRID[var][centro]]
    return [float(v) for v in GRID[var][centro]]


def clave(combo):
    return tuple(round(float(combo[k]), 6) for k in VARIABLES)


def n7a_puntos():
    """(tareas N7A, descartes). Base primero; dedup por (centro, combinacion)."""
    tareas, desc = [], []
    for centro, base in CENTROS:
        vistos, por_var, cand = set(), {}, [0]

        def add(var, valor, combo):
            cand[0] += 1
            k = clave(combo)
            if k in vistos:
                return
            vistos.add(k)
            por_var[var] = por_var.get(var, 0) + 1
            tareas.append(dict(
                id_punto=f"N7A-{centro}-{var}-{por_var[var]:03d}",
                barrido="N7A", centro=centro, variable=var, valor=valor,
                par="", var1="", val1=None, var2="", val2=None,
                combo=dict(combo)))

        ini = len(tareas)
        add("base", None, base)
        for var in VARIABLES:
            for v in rejilla_a(var, centro, base[var]):
                add(var, float(v), dict(base, **{var: float(v)}))
        n_fin = len(tareas) - ini
        desc.append(dict(barrido="N7A", centro=centro, nivel="todas",
                         n_candidatas=cand[0], n_descartados=0,
                         n_duplicados=cand[0] - n_fin, n_final=n_fin))
    return tareas, desc


def n7b_puntos():
    """(tareas N7B, descartes). Descarta P_alta < 1.3*P_baja; dedup por centro."""
    tareas, desc = [], []
    for centro, base in CENTROS:
        vistos, por_par, cand = set(), {}, [0, 0]

        def add(par, a, va, b, vb, combo):
            cand[0] += 1
            if float(combo["P_alta"]) < 1.3 * float(combo["P_baja"]):
                cand[1] += 1
                return
            k = clave(combo)
            if k in vistos:
                return
            vistos.add(k)
            por_par[par] = por_par.get(par, 0) + 1
            tareas.append(dict(
                id_punto=f"N7B-{centro}-{par}-{por_par[par]:03d}",
                barrido="N7B", centro=centro, variable="", valor=None,
                par=par, var1=a, val1=va, var2=b, val2=vb, combo=dict(combo)))

        ini = len(tareas)
        for par, a, b in PARES:
            ra, da = valores_brutos(a, centro), valores(a, centro)
            rb, db = valores_brutos(b, centro), valores(b, centro)
            for i, va in enumerate(da):
                for j, vb in enumerate(db):
                    add(par, a, float(va), b, float(vb),
                        dict(base, **{a: float(va), b: float(vb)}))
        n_fin = len(tareas) - ini
        desc.append(dict(
            barrido="N7B", centro=centro, nivel="todas",
            n_candidatas=cand[0], n_descartados=cand[1],
            n_duplicados=cand[0] - cand[1] - n_fin, n_final=n_fin))
    return tareas, desc


def tareas(barrido):
    """Tareas del barrido pedido (N7A, N7B o all)."""
    if barrido == "N7A":
        return n7a_puntos()[0]
    if barrido == "N7B":
        return n7b_puntos()[0]
    if barrido == "all":
        return n7a_puntos()[0] + n7b_puntos()[0]
    return []


def diseno_completo():
    """Todas las tareas y descartes por (barrido, centro) + TOTAL."""
    ts, ds = [], []
    for b, fn in (("N7A", n7a_puntos), ("N7B", n7b_puntos)):
        tb, db = fn()
        ts += tb
        ds += db
        tot = {k: sum(r[k] for r in db) for k in
               ("n_candidatas", "n_descartados", "n_duplicados", "n_final")}
        ds.append(dict(barrido=b, centro="TOTAL", nivel="todas", **tot))
    return ts, ds


def _escribir_diseno(dirs):
    dirs.mkdir(parents=True, exist_ok=True)
    todos, desc = diseno_completo()
    with open(dirs / "n7_diseno.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CM_DIS, extrasaction="ignore")
        w.writeheader()
        for t in todos:
            w.writerow({**{k: t[k] for k in META}, **t["combo"]})
    with open(dirs / "n7_descartes.csv", "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CM_DESC)
        w.writeheader()
        w.writerows(desc)
    print(f"diseno escrito: {dirs / 'n7_diseno.csv'} ({len(todos)}) | "
          f"{dirs / 'n7_descartes.csv'} ({len(desc)} filas)", flush=True)
    for b in ("N7A", "N7B"):
        n = sum(1 for t in todos if t["barrido"] == b)
        print(f"  {b}: {n} puntos planeados", flush=True)
    return todos, desc

if __name__ == "__main__":
    _escribir_diseno(OUT)

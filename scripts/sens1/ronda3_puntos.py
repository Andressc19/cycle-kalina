"""Sensibilidad 1, Ronda 3 - puntos del barrido N9 (N10 y N8 van despues).

N9: pares del regenerador y la turbina en C3 y C4. Dos mallas 7x7 por centro
(el resto de variables en el valor del centro; eta_p=0.80 y m_b=1.0 fijos).
El punto base de cada centro se anade PRIMERO con `par="base"`, de modo que el
dedup por (barrido, centro, combinacion) lo deja una sola vez y la celda
central de cada malla queda cubierta por ese base (el reporte la rellena).
Salidas en `resultados/2026-10-16_sens1_ronda3/`: `ronda3_diseno.csv` (conteo
a verificar antes de correr) y `ronda3_descartes.csv`. Deja la estructura
lista para anadir N10 y N8 en tareas posteriores.
Se ejecuta como modulo (lo importa `ronda3_corrida.py`) y como script.
"""
from __future__ import annotations

import csv
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-16_sens1_ronda3"

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
# N9: dos mallas 7x7 por centro; el valor con "b" en la spec es el del centro.
PARES = (("B5", "eps_reg", "eta_t"), ("B6", "eps_hrvg", "T_fuente"))
GRID = {
    "eps_reg": [0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 0.95],
    "eta_t": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
    "eps_hrvg": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
    "T_fuente_C": {"C3": [110, 130, 140, 150, 160, 180, 200],
                   "C4": [80, 90, 100, 110, 120, 135, 150]},
}
DEFINIDOS = ("N9",)                      # despues: ("N9", "N10", "N8")
BARRIDOS_CLI = ("N9", "N10", "N8", "all")
META = ("id_punto", "barrido", "centro", "par", "var1", "val1", "var2", "val2")
CM_DIS = list(META) + list(COMBO)
CM_DESC = ["barrido", "centro", "n_candidatas", "n_descartados",
           "n_duplicados", "n_final"]


def valores(var, centro):
    """Rejilla de N9 en unidades de diseno (K si T_fuente)."""
    if var == "T_fuente":
        return [round(c + 273.15, 2) for c in GRID["T_fuente_C"][centro]]
    return [float(v) for v in GRID[var]]


def clave(combo):
    return tuple(round(float(combo[k]), 6) for k in VARIABLES)


def n9_puntos():
    """(tareas N9, descartes). Base primero; dedup por (barrido, centro, ...)."""
    tareas, desc = [], []
    for centro, base in CENTROS:
        vistos, por_par, cand = set(), {}, [0, 0]

        def add(par, a, va, b, vb, combo):
            cand[0] += 1
            k = clave(combo)
            if k in vistos:
                cand[1] += 1
                return
            vistos.add(k)
            por_par[par] = por_par.get(par, 0) + 1
            tareas.append(dict(
                id_punto=f"N9-{centro}-{par}-{por_par[par]:04d}",
                barrido="N9", centro=centro, par=par, var1=a, val1=va,
                var2=b, val2=vb, combo=dict(combo)))

        ini = len(tareas)
        add("base", "", None, "", None, dict(base))
        for par, a, b in PARES:
            for va in valores(a, centro):
                for vb in valores(b, centro):
                    add(par, a, float(va), b, float(vb),
                        dict(base, **{a: float(va), b: float(vb)}))
        desc.append(dict(barrido="N9", centro=centro, n_candidatas=cand[0],
                         n_descartados=0, n_duplicados=cand[1],
                         n_final=len(tareas) - ini))
    return tareas, desc


_FABRICAS = {"N9": n9_puntos}


def tareas(barrido):
    """Tareas del barrido pedido; [] si todavia no esta definido."""
    if barrido == "all":
        out = []
        for b in DEFINIDOS:
            out += tareas(b)
        return out
    fn = _FABRICAS.get(barrido)
    return [] if fn is None else fn()[0]


def diseno_completo():
    """Tareas y descartes de los barridos definidos + fila TOTAL por barrido."""
    ts, ds = [], []
    for b in DEFINIDOS:
        tb, db = _FABRICAS[b]()
        ts += tb
        ds += db
        tot = {k: sum(r[k] for r in db) for k in
               ("n_candidatas", "n_descartados", "n_duplicados", "n_final")}
        ds.append(dict(barrido=b, centro="TOTAL", **tot))
    return ts, ds


def _escribir_diseno(dirs):
    dirs.mkdir(parents=True, exist_ok=True)
    todos, desc = diseno_completo()
    with open(dirs / "ronda3_diseno.csv", "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CM_DIS, extrasaction="ignore")
        w.writeheader()
        for t in todos:
            w.writerow({**{k: t[k] for k in META}, **t["combo"]})
    with open(dirs / "ronda3_descartes.csv", "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CM_DESC)
        w.writeheader()
        w.writerows(desc)
    print(f"diseno escrito: {dirs / 'ronda3_diseno.csv'} ({len(todos)}) | "
          f"{dirs / 'ronda3_descartes.csv'} ({len(desc)} filas)", flush=True)
    for b in DEFINIDOS:
        for c in sorted({t["centro"] for t in todos if t["barrido"] == b}):
            n = sum(1 for t in todos if t["barrido"] == b and t["centro"] == c)
            print(f"  {b} / {c}: {n} puntos planeados", flush=True)
    return todos, desc


if __name__ == "__main__":
    _escribir_diseno(OUT)

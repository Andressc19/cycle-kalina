"""M2S — efecto de un sumidero frío con P_baja libre y piso de O2 = clima.

Malla: 4 bases (B1 `T_fuente`=403.0, B2 `T_fuente`=420.0, B3 `eps_hrvg`=0.40,
B4 = el profesor exacto) × `T_sumidero` ∈ {278.15, 283.15, 288.15, 293.15,
300.032917} K —siempre con `t_amb_diseno = T_sumidero`, el piso de O2 sigue al
clima— × `P_baja` ∈ `numpy.linspace(150, 1500, 10)`: 4 × 5 × 10 = 200 corridas
con `ProcessPoolExecutor(max_workers=5)`, cada fila con flush en
`resultados/2026-10-06_final_M2S/m2s_malla.csv`. Bisección por (base,
T_sumidero) sobre P_baja (tolerancia 10 kPa, máximo 7 iteraciones, en rondas
paralelas) en cada par de vecinos donde cambia «es KALINA», o donde cambia
`m_O2 >= 0` con ambos genuinos: `m2s_biseccion.csv`. Punto genuino:
`clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`; una fila con `convergio=True`
y `NO_CONVERGIO` es espuria (N2) y cuenta como NO genuina en todo. Con
`M2S_HUMO=1`: 1 base × 2 T_sumidero × 2 P_baja, sin bisección, en `.../humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import numpy as np  # noqa: E402

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402

HUMO = os.environ.get("M2S_HUMO") == "1"
_SUB = "2026-10-06_final_M2S/" + ("humo" if HUMO else "")
OUT = _RAIZ / "resultados" / _SUB
N_WORKERS = 5
BASES = {"B1": {"T_fuente": 403.0}, "B2": {"T_fuente": 420.0},
         "B3": {"eps_hrvg": 0.40}, "B4": {}}
TSUM = (278.15, 283.15, 288.15, 293.15, 300.032917)
P_MALLA = np.linspace(150.0, 1500.0, 10)
TOL_P, MAX_IT = 10.0, 7
GENUINAS = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
CMALLA = ["base", "T_sumidero_val", "P_baja_val"] + list(COLS)
CBISE = ["base", "T_sumidero_val", "P_baja_val", "frontera", "iteracion",
         "nota"] + list(COLS)


def genuina(f: dict) -> bool:
    """Punto genuino: KALINA, CORREGIBLE o INVIABLE (la espuria N2, no)."""
    if f.get("convergio") is True and f.get("clasificacion") == "NO_CONVERGIO":
        return False
    return f.get("clasificacion") in GENUINAS


def es_kalina(f: dict) -> bool:
    return f.get("clasificacion") == "KALINA"


def cumple(f: dict, frontera: str) -> bool:
    """¿La fila cumple el criterio? En O2 un punto NO genuino NO cumple."""
    if frontera == "KALINA":
        return es_kalina(f)
    m = f.get("m_O2")
    return genuina(f) and m is not None and m >= 0.0


def _eval(t: dict) -> dict:
    """Corre UN punto (base + T_sumidero + P_baja; el resto, de la base)."""
    combo = dict(PROFESOR, **BASES[t["base"]], T_sumidero=t["T_sum"],
                 P_baja=t["P_baja"])
    f = evaluar_punto(combo, motor="teqp", t_amb_diseno=t["T_sum"],
                      tag=f'{t["base"]}:{t["T_sum"]:g}')
    f.update(base=t["base"], T_sumidero_val=t["T_sum"],
             P_baja_val=t["P_baja"], frontera=t.get("frontera"),
             iteracion=t.get("iteracion"), nota=t.get("nota"))
    if f.get("frontera") == "O2" and not genuina(f):
        f["nota"] = "punto medio no genuino"
    return f


def _ejecutar(tareas: list, cab: list, fh, esc) -> list:
    """Todo el lote en el pool; escribe cada fila con flush en su CSV."""
    orden = [None] * len(tareas)
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(_eval, t): i for i, t in enumerate(tareas)}
        for n, fu in enumerate(as_completed(futs), 1):
            f = fu.result()
            orden[futs[fu]] = f
            esc.writerow({c: f.get(c) for c in cab})
            fh.flush()
            print(f'[{n}/{len(tareas)}] {f["base"]} T_sum={f["T_sumidero_val"]:g} '
                  f'P_baja={f["P_baja_val"]:g} {f["clasificacion"]} '
                  f'{f["t_s"]:.1f}s', flush=True)
    return orden


def celdas() -> list:
    """200 tareas (en humo: 1 base × 2 T_sumidero × 2 P_baja)."""
    bs = list(BASES)[:1] if HUMO else list(BASES)
    ts = TSUM[:2] if HUMO else TSUM
    ps = P_MALLA[[0, -1]] if HUMO else P_MALLA
    return [dict(base=b, T_sum=float(t), P_baja=float(p))
            for b in bs for t in ts for p in ps]


def detectar(filas: list) -> list:
    """Fronteras de la malla entre vecinos de P_baja, por (base, T_sumidero)."""
    fr, grupos = [], {}
    for f in filas:
        grupos.setdefault((f["base"], f["T_sumidero_val"]), []).append(f)
    for (base, Ts), pts in grupos.items():
        pts = sorted(pts, key=lambda f: f["P_baja_val"])
        for p, q in zip(pts, pts[1:]):
            for nom in ("KALINA", "O2"):
                if nom == "O2" and not (genuina(p) and genuina(q)):
                    continue
                if cumple(p, nom) != cumple(q, nom):
                    fr.append(dict(base=base, T_sum=Ts, frontera=nom,
                                   lo=p["P_baja_val"], hi=q["P_baja_val"],
                                   lo_si=cumple(p, nom), f_lo=p, f_hi=q,
                                   iter=0))
    return fr


def fase_biseccion(todos: list, fh, esc) -> list:
    """Rondas de bisección sobre P_baja de todas las fronteras a la vez."""
    ronda, activos, hechas = 0, todos, []
    while activos:
        ronda += 1
        for f in activos:
            print(f'[ronda {ronda}] {f["base"]} T_sum={f["T_sum"]:g} '
                  f'{f["frontera"]} {f["lo"]:g}..{f["hi"]:g}', flush=True)
        t = [dict(base=f["base"], T_sum=f["T_sum"],
                  P_baja=(f["lo"] + f["hi"]) / 2, frontera=f["frontera"],
                  iteracion=f["iter"], nota=None) for f in activos]
        medias = _ejecutar(t, CBISE, fh, esc)
        hechas += medias
        vivos = []
        for f, m in zip(activos, medias):
            if cumple(m, f["frontera"]) == f["lo_si"]:
                f["lo"], f["f_lo"] = m["P_baja_val"], m
            else:
                f["hi"], f["f_hi"] = m["P_baja_val"], m
            f["iter"] += 1
            if f["hi"] - f["lo"] >= TOL_P and f["iter"] < MAX_IT:
                vivos.append(f)
        activos = vivos
    return hechas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"M2S | humo={HUMO} | {N_WORKERS} workers -> {OUT}", flush=True)
    with open(OUT / "m2s_malla.csv", "w", encoding="utf-8", newline="") as fm, \
            open(OUT / "m2s_biseccion.csv", "w", encoding="utf-8",
                 newline="") as fb:
        em = csv.DictWriter(fm, fieldnames=CMALLA)
        em.writeheader()
        fm.flush()
        eb = csv.DictWriter(fb, fieldnames=CBISE)
        eb.writeheader()
        fb.flush()
        t0 = time.perf_counter()
        tm = time.perf_counter()
        malla = _ejecutar(celdas(), CMALLA, fm, em)
        t_malla = time.perf_counter() - tm
        fr = [] if HUMO else detectar(malla)
        print(f"{len(fr)} fronteras detectadas en la malla", flush=True)
        tm = time.perf_counter()
        bise = fase_biseccion(fr, fb, eb)
        t_bise = time.perf_counter() - tm
    import m2s_reporte as rep  # noqa: E402
    rep.generar(malla, bise, fr, t_malla, t_bise)
    print(f"fin: {len(malla)} malla + {len(bise)} biseccion en "
          f"{time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()

"""M2 nivel 2 — ¿con DOS cambios al enunciado del profesor aparece KALINA?

Ruta A (solo diseño): `eps_hrvg` ∈ {0.75, 0.78, 0.81} conservando toda la fuente
y el sitio del profesor (T_fuente = 623.15 K). Ruta B (sitio + diseño):
`T_fuente` ∈ {380, 390, 403, 420, 434, 466, 497, 529, 560} K con todo lo demás
del profesor (eps_hrvg = 0.85). En ambas la segunda variable es `P_baja` (la
regla del proyecto para cerrar O2) y las otras nueve quedan como él las dio.
Fase A: malla `P_baja ∈ numpy.linspace(400, 2000, 12)` por valor de la variable
1 → 144 corridas con `ProcessPoolExecutor(max_workers=6)`. Fase B: bisección
sobre P_baja entre los vecinos donde cambia KALINA o `m_O2 >= 0` (tolerancia
10 kPa, máximo 8 iteraciones, en rondas paralelas). Salida en
`resultados/2026-10-06_final_M2/`: `m2n2_malla.csv`, `m2n2_biseccion.csv`,
`m2n2_fronteras.csv`, `m2n2_kalina.csv`, `m2n2_resumen.csv` y
`REPORTE_M2_N2.md` (los tres últimos, escritos por `m2_nivel2_reporte.py`).
Con `M2_HUMO=1`: 1 valor por ruta × 2 valores de P_baja, sin bisección, y todo
en `.../humo_n2/`.
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

HUMO = os.environ.get("M2_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-06_final_M2/humo_n2" if HUMO else "2026-10-06_final_M2")
N_WORKERS = 6
RUTAS = {"A": ("eps_hrvg", (0.75, 0.78, 0.81)),
         "B": ("T_fuente", (380.0, 390.0, 403.0, 420.0, 434.0, 466.0, 497.0, 529.0, 560.0))}
P_MALLA = np.linspace(400.0, 2000.0, 12)
TOL_P, MAX_IT = 10.0, 8
GENUINAS = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
CMALLA = ["fase", "ruta", "var1", "val1", "P_baja_val"] + list(COLS)
CBISE = ["fase", "ruta", "var1", "val1", "frontera", "iteracion", "P_baja_val",
         "nota"] + list(COLS)


def genuina(f: dict) -> bool:
    """Punto genuino: KALINA, CORREGIBLE o INVIABLE (N2 espurio = NO)."""
    return f["clasificacion"] in GENUINAS


def es_kalina(f: dict) -> bool:
    return f["clasificacion"] == "KALINA"


def cumple(f: dict, frontera: str) -> bool:
    """¿La fila cumple el criterio? En O2 un punto no genuino NO cumple."""
    if frontera == "KALINA":
        return es_kalina(f)
    m = f.get("m_O2")
    return genuina(f) and m is not None and m >= 0.0


def _eval(t: dict) -> dict:
    """Corre UN punto (ruta + variable 1 + P_baja; el resto, del profesor)."""
    combo = dict(PROFESOR, **{t["var1"]: t["val1"], "P_baja": t["P"]})
    f = evaluar_punto(combo, motor="teqp", tag=f'{t["ruta"]}:{t["var1"]}={t["val1"]:g}')
    f.update({k: t.get(k) for k in ("fase", "ruta", "var1", "val1", "P_baja_val",
                                    "frontera", "iteracion", "nota")})
    if f.get("frontera") == "O2" and not genuina(f):
        f["nota"] = "punto medio no genuino"
    return f


def _ejecutar(tareas: list, cab: list, fh, esc) -> list:
    """Todo el lote en el pool; devuelve las filas en el orden en que se enviaron."""
    orden = [None] * len(tareas)
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(_eval, t): i for i, t in enumerate(tareas)}
        for n, fu in enumerate(as_completed(futs), 1):
            f = fu.result()
            orden[futs[fu]] = f
            esc.writerow({c: f.get(c) for c in cab}); fh.flush()
            print(f'[{n}/{len(tareas)}] {f["ruta"]} {f["var1"]}={f["val1"]:g} '
                  f'P_baja={f["P_baja_val"]:g} {f["clasificacion"]} {f["t_s"]:.1f}s',
                  flush=True)
    return orden


def fase_malla(fh, esc) -> list:
    """Fase A: 144 corridas (en humo: 1 valor por ruta × 2 valores de P_baja)."""
    ps = P_MALLA[[0, -1]] if HUMO else P_MALLA
    t = [dict(fase="malla", ruta=r, var1=v, val1=float(x), P=float(p),
              P_baja_val=float(p))
         for r, (v, xs) in RUTAS.items()
         for x in (list(xs)[:1] if HUMO else xs)
         for p in ps]
    return _ejecutar(t, CMALLA, fh, esc)


def detectar(filas: list) -> list:
    """Fronteras entre vecinos de la malla: KALINA, o m_O2 >= 0 con ambos genuinos."""
    fr, grupos = [], {}
    for f in filas:
        grupos.setdefault((f["ruta"], f["val1"]), []).append(f)
    for (ruta, val1), pts in grupos.items():
        pts = sorted(pts, key=lambda f: f["P_baja_val"])
        var1 = pts[0]["var1"]
        for p, q in zip(pts, pts[1:]):
            for nom in ("KALINA", "O2"):
                if nom == "O2" and not (genuina(p) and genuina(q)):
                    continue
                if cumple(p, nom) != cumple(q, nom):
                    fr.append(dict(ruta=ruta, var1=var1, val1=val1, frontera=nom,
                                   lo=p["P_baja_val"], hi=q["P_baja_val"],
                                   lo_si=cumple(p, nom), f_lo=p, f_hi=q, iter=0))
    return fr


def fase_biseccion(todos: list, fh, esc) -> list:
    """Fase B: rondas de bisección sobre P_baja; muta `todos`."""
    ronda, activos, hechas = 0, todos, []
    while activos:
        ronda += 1
        for f in activos:
            print(f'[ronda {ronda}] {f["ruta"]} {f["var1"]}={f["val1"]:g} '
                  f'{f["frontera"]} {f["lo"]:g}..{f["hi"]:g}', flush=True)
        t = [dict(fase="biseccion", ruta=f["ruta"], var1=f["var1"], val1=f["val1"],
                  frontera=f["frontera"], iteracion=f["iter"],
                  P=(f["lo"] + f["hi"]) / 2, P_baja_val=(f["lo"] + f["hi"]) / 2,
                  nota=None)
             for f in activos]
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
    print(f"M2 nivel 2 | humo={HUMO} | {N_WORKERS} workers -> {OUT}", flush=True)
    with open(OUT / "m2n2_malla.csv", "w", encoding="utf-8", newline="") as fm, \
            open(OUT / "m2n2_biseccion.csv", "w", encoding="utf-8", newline="") as fb:
        em = csv.DictWriter(fm, fieldnames=CMALLA); em.writeheader(); fm.flush()
        eb = csv.DictWriter(fb, fieldnames=CBISE); eb.writeheader(); fb.flush()
        t0 = time.perf_counter()
        tm = time.perf_counter()
        malla = fase_malla(fm, em)
        t_malla = time.perf_counter() - tm
        fr = [] if HUMO else detectar(malla)
        print(f"{len(fr)} fronteras detectadas en la malla", flush=True)
        tm = time.perf_counter()
        bise = fase_biseccion(fr, fb, eb)
        t_bise = time.perf_counter() - tm
    import m2_nivel2_reporte as rep  # noqa: E402
    rep.generar(malla, bise, fr, t_malla, t_bise)
    print(f"fin: {len(malla)} malla + {len(bise)} biseccion en "
          f"{time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()

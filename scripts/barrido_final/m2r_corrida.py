"""M2R — repetición de M2 con η y ε en [0.40, 0.95] (TASK_CONTEXT final_M2R).

Malla: `n1`, eps_hrvg/eps_reg/eps_cond/eta_t/eta_p, cada una con
`numpy.linspace(0.40, 0.95, 12)` y el resto en PROFESOR (60 corridas); `n2a`,
eps_hrvg ∈ {0.40, 0.50, 0.60, 0.70, 0.80} × eps_cond en ese mismo linspace, con
P_baja = 400 del profesor (60); `n2b`, eps_hrvg ∈ {0.40, …, 0.70} × P_baja ∈
`numpy.linspace(400, 2000, 12)` (48); `n3`, T_fuente ∈ {403, 420, 434, 466,
497, 529, 560} × eps_cond ∈ {0.85, 0.90, 0.95} con P_baja = 400 (21), sin
bisección. Bisección de máximo 8 iteraciones (tolerancia 0.005 en ε/η y 10 kPa
en P_baja), en rondas paralelas con `ProcessPoolExecutor(max_workers=5)`: en
`n1` sobre la variable barrida donde cambia «es genuino» o «es KALINA»; en
`n2a`/`n2b` sobre la segunda variable donde cambia «es KALINA», o donde cambia
`m_O2 >= 0` con ambos vecinos genuinos. Un CSV por parte, escrito con flush, y
en consola `[n/N] parte var1=val1 var2=val2 clase t_s`. Salida en
`resultados/2026-10-06_final_M2R/`; con `M2R_HUMO=1`: 1 punto por parte, sin
bisección, todo en `.../humo/`.
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

HUMO = os.environ.get("M2R_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-06_final_M2R/humo" if HUMO else "2026-10-06_final_M2R")
N_WORKERS = 5
GENUINAS = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
EPS = tuple(float(x) for x in np.linspace(0.40, 0.95, 12))
PBAJA = tuple(float(x) for x in np.linspace(400.0, 2000.0, 12))
V5 = ("eps_hrvg", "eps_reg", "eps_cond", "eta_t", "eta_p")
HRVG_A, HRVG_B = (0.40, 0.50, 0.60, 0.70, 0.80), (0.40, 0.50, 0.60, 0.70)
TF3 = (403.0, 420.0, 434.0, 466.0, 497.0, 529.0, 560.0)
EC3 = (0.85, 0.90, 0.95)
TOL_E, TOL_P, MAX_IT = 0.005, 10.0, 8
PARTES_MALLA = ("n1", "n2a", "n2b", "n3")
PARTES_BISE = ("n1", "n2a", "n2b")
CMALLA = ["parte", "var1", "val1", "var2", "val2"] + list(COLS)
CBISE = ["parte", "var1", "val1", "var2", "val2", "frontera", "iteracion"] + list(COLS)

def genuina(f: dict) -> bool:
    """Punto genuino: KALINA, CORREGIBLE o INVIABLE (el espurio N2, no)."""
    return f["clasificacion"] in GENUINAS

def cumple(f: dict, fr: str) -> bool:
    """¿La fila cumple el criterio de esa frontera?"""
    if fr == "genuino":
        return genuina(f)
    if fr == "kalina":
        return f["clasificacion"] == "KALINA"
    m = f.get("m_O2")
    return genuina(f) and m is not None and m >= 0.0

def _fmt(x) -> str:
    return "—" if x is None else f"{x:g}"

def celdas() -> list:
    """Las 189 celdas de la malla (en humo: la primera de cada parte)."""
    t = [dict(parte="n1", var1=v, val1=x, var2="", val2=None, extras={v: x}) for v in V5 for x in EPS]
    t += [dict(parte="n2a", var1="eps_hrvg", val1=h, var2="eps_cond", val2=c, extras={"eps_hrvg": h, "eps_cond": c}) for h in HRVG_A for c in EPS]
    t += [dict(parte="n2b", var1="eps_hrvg", val1=h, var2="P_baja", val2=p, extras={"eps_hrvg": h, "P_baja": p}) for h in HRVG_B for p in PBAJA]
    t += [dict(parte="n3", var1="T_fuente", val1=T, var2="eps_cond", val2=c, extras={"T_fuente": T, "eps_cond": c}) for T in TF3 for c in EC3]
    return [next(c for c in t if c["parte"] == p) for p in PARTES_MALLA] if HUMO else t

def _eval(t: dict) -> dict:
    """Corre UN punto (nunca lanza: `evaluar_punto` captura todo)."""
    f = evaluar_punto(dict(PROFESOR, **t["extras"]), motor="teqp",
                      tag=f'{t["parte"]}:{t["var1"]}={t["val1"]:g}')
    f.update({k: t.get(k) for k in ("parte", "var1", "val1", "var2", "val2",
                                    "frontera", "iteracion", "mid")})
    return f

def _ejecutar(tareas: list, cab: list, mano: dict) -> list:
    """Todo el lote en el pool; escribe cada fila con flush en su CSV de parte."""
    orden = [None] * len(tareas)
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(_eval, t): i for i, t in enumerate(tareas)}
        for n, fu in enumerate(as_completed(futs), 1):
            f = fu.result()
            orden[futs[fu]] = f
            fh, esc = mano[f["parte"]]
            esc.writerow({c: f.get(c) for c in cab})
            fh.flush()
            v2 = f'{f["var2"]}={f["val2"]:g}' if f.get("var2") else "var2=—"
            print(f'[{n}/{len(tareas)}] {f["parte"]} {f["var1"]}={_fmt(f["val1"])} '
                  f'{v2} {f["clasificacion"]} {f["t_s"]:.1f}s', flush=True)
    return orden

def abrir(prefijo: str, partes, cab: list) -> dict:
    """Un CSV por parte con cabecera y flush: {parte: (fh, esc)}."""
    mano = {}
    for p in partes:
        fh = open(OUT / f"m2r_{p}_{prefijo}.csv", "w", encoding="utf-8", newline="")
        esc = csv.DictWriter(fh, fieldnames=cab)
        esc.writeheader()
        fh.flush()
        mano[p] = (fh, esc)
    return mano

def _frontera(fila_lo: dict, fila_hi: dict, parte: str, var1, val1, var2, ref,
              nom: str, lo: float, hi: float, tol: float) -> dict:
    return dict(parte=parte, var1=var1, val1=val1, var2=var2, val2=None, ref=ref,
                frontera=nom, lo=lo, hi=hi, lo_si=cumple(fila_lo, nom),
                f_lo=fila_lo, f_hi=fila_hi, iter=0, tol=tol)

def detectar(filas: list) -> list:
    """Fronteras de la malla: `n1` por variable (genuino o KALINA); `n2a`/`n2b`
    por valor de var1 (KALINA, o `m_O2 >= 0` con ambos vecinos genuinos)."""
    fr = []
    for v in V5:
        pts = sorted((f for f in filas if f["parte"] == "n1" and f["var1"] == v),
                     key=lambda f: f["val1"])
        for p, q in zip(pts, pts[1:]):
            for nom in ("genuino", "kalina"):
                if cumple(p, nom) != cumple(q, nom):
                    fr.append(_frontera(p, q, "n1", v, None, "", v, nom,
                                        p["val1"], q["val1"], TOL_E))
    for parte in ("n2a", "n2b"):
        grupos = {}
        for f in filas:
            if f["parte"] == parte:
                grupos.setdefault(f["val1"], []).append(f)
        for val1, pts in grupos.items():
            pts = sorted(pts, key=lambda f: f["val2"])
            for p, q in zip(pts, pts[1:]):
                for nom in ("kalina", "o2"):
                    if nom == "o2" and not (genuina(p) and genuina(q)):
                        continue
                    if cumple(p, nom) != cumple(q, nom):
                        fr.append(_frontera(p, q, parte, pts[0]["var1"], val1,
                                            pts[0]["var2"], pts[0]["var2"], nom,
                                            p["val2"], q["val2"],
                                            TOL_E if parte == "n2a" else TOL_P))
    return fr

def _tarea_bise(f: dict) -> dict:
    """La tarea de la mitad del intervalo actual de una frontera."""
    x = (f["lo"] + f["hi"]) / 2
    if f["parte"] == "n1":
        extras, val1, val2 = {f["ref"]: x}, x, None
    else:
        extras, val1, val2 = {f["var1"]: f["val1"], f["ref"]: x}, f["val1"], x
    return dict(parte=f["parte"], var1=f["var1"], val1=val1, var2=f["var2"],
                val2=val2, extras=extras, frontera=f["frontera"],
                iteracion=f["iter"], mid=x)

def fase_biseccion(fr: list, mano: dict) -> list:
    """Rondas de bisección sobre todas las fronteras a la vez; muta `fr`."""
    ronda, activos, hechas = 0, fr, []
    while activos:
        ronda += 1
        for f in activos:
            print(f'[ronda {ronda}] {f["parte"]} {f["var1"]}={_fmt(f["val1"])} '
                  f'{f["frontera"]} {f["lo"]:g}..{f["hi"]:g}', flush=True)
        medias = _ejecutar([_tarea_bise(f) for f in activos], CBISE, mano)
        hechas += medias
        vivos = []
        for f, m in zip(activos, medias):
            if cumple(m, f["frontera"]) == f["lo_si"]:
                f["lo"], f["f_lo"] = m["mid"], m
            else:
                f["hi"], f["f_hi"] = m["mid"], m
            f["iter"] += 1
            if f["hi"] - f["lo"] >= f["tol"] and f["iter"] < MAX_IT:
                vivos.append(f)
        activos = vivos
    return hechas

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"M2R | humo={HUMO} | {N_WORKERS} workers -> {OUT}", flush=True)
    t0 = time.perf_counter()
    mano, mano_b = abrir("malla", PARTES_MALLA, CMALLA), abrir("biseccion", PARTES_BISE, CBISE)
    tm = time.perf_counter()
    malla = _ejecutar(celdas(), CMALLA, mano)
    t_malla = time.perf_counter() - tm
    fr = [] if HUMO else detectar(malla)
    print(f"{len(fr)} fronteras detectadas en la malla", flush=True)
    tm = time.perf_counter()
    bise = fase_biseccion(fr, mano_b) if fr else []
    t_bise = time.perf_counter() - tm
    for m in (mano, mano_b):
        for fh, _esc in m.values():
            fh.close()
    import m2r_reporte as rep  # noqa: E402
    rep.generar(malla, bise, fr, t_malla, t_bise)
    print(f"fin: {len(malla)} malla + {len(bise)} biseccion en "
          f"{time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)

if __name__ == "__main__":
    main()

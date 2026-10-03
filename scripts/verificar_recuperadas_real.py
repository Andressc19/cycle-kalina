"""Paso 4 de `2026-10-02-reejecutar-no-convergio`: verifica con el motor real
(`AmmoniaWaterAdapter`) una muestra de filas que el bracket tolerante MA recuperó en
`resultados/2026-10-02_reejecucion/reejecucion_filas.csv` (antes NO_CONVERGIO, ahora
convergen con `TeqpVerificado`).

Selección (determinista): todas las KALINA si son <= 3; la de mayor y la de menor `eta`;
las que tengan una falla N2; y el resto repartido por barrido de origen hasta 10 filas.
Cada fila se resuelve completa con el motor real, `bracket_tolerante=True` y sin
presupuesto de tiempo, y se clasifica con `evaluar_ciclo`. Criterio: `|Δη|/η < 0.5 %` y
misma clasificación que con teqp. 6 workers, CSV incremental y reanudable, una línea
por fila en `progreso_real.log`; una excepción en una fila se registra y no aborta.
No toca `src/` ni ningún CSV existente.
"""
from __future__ import annotations

import csv, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.cycle_solver import resolver_ciclo                             # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter   # noqa: E402
from src.restricciones import evaluar_ciclo                              # noqa: E402

OUT = RAIZ / "resultados" / "2026-10-02_reejecucion"
CSV_IN, CSV_OUT, LOG = OUT / "reejecucion_filas.csv", OUT / "verificacion_real.csv", OUT / "progreso_real.log"
COLS11 = ("P_alta", "P_baja", "T_fuente", "T_sumidero", "x_b", "m_b", "eta_t", "eta_p",
          "eps_hrvg", "eps_reg", "eps_cond")
N_MUESTRA, NW, TOL_REL = 10, 6, 0.005
COLS = ("clave", "csv_origenes", "motivo", "eta_teqp", "clas_teqp", "eta_real", "clas_real",
        "d_eta_rel", "misma_clas", "verificada", "t_s", "msg")


def _log(msg):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def seleccionar(filas):
    """Hasta N_MUESTRA filas recuperadas, con el motivo de selección de cada una."""
    rec = [f for f in filas if f["convergio"] == "True" and f["eta"] not in ("", None)]
    for f in rec:
        f["_eta"] = float(f["eta"])
    elegidas = {}

    def tomar(f, motivo):
        if f["clave"] not in elegidas and len(elegidas) < N_MUESTRA:
            elegidas[f["clave"]] = dict(f, motivo=motivo)

    kal = [f for f in rec if f["clasificacion"] == "KALINA"]
    for f in (kal if len(kal) <= 3 else kal[:3]):
        tomar(f, "KALINA")
    if rec:
        tomar(max(rec, key=lambda f: f["_eta"]), "eta maxima")
        tomar(min(rec, key=lambda f: f["_eta"]), "eta minima")
    for f in rec:
        if "N2" in (f.get("fallas") or "").split(","):
            tomar(f, "falla N2")
    por_origen = {}
    for f in rec:
        por_origen.setdefault(f["csv_origenes"].split(";")[0], []).append(f)
    while len(elegidas) < min(N_MUESTRA, len(rec)):
        avance = False
        for origen, lista in por_origen.items():
            libres = [f for f in lista if f["clave"] not in elegidas]
            if libres:
                tomar(libres[len(libres) // 2], f"reparto: {origen.split('/')[-1]}")
                avance = True
        if not avance:
            break
    return list(elegidas.values())


def verificar(f):
    """Una fila con el motor real. Nunca lanza."""
    kw = {c: float(f[c]) for c in COLS11}
    vk = {**{c: kw[c] for c in COLS11 if c not in ("eta_t", "eta_p")},
          "T_amb_diseno": float(f["T_amb_diseno"])}
    d = dict(clave=f["clave"], csv_origenes=f["csv_origenes"], motivo=f["motivo"],
             eta_teqp=f["eta"], clas_teqp=f["clasificacion"])
    t0 = time.perf_counter()
    try:
        real = AmmoniaWaterAdapter(x=kw["x_b"])
        res = resolver_ciclo(real, bracket_tolerante=True, **kw)
        val = evaluar_ciclo(real, res, **vk)
        eta_t, eta_r = float(f["eta"]), res["eta"]
        rel = abs(eta_r - eta_t) / abs(eta_t) if eta_t else float("nan")
        misma = val.clasificacion.value == f["clasificacion"]
        d.update(eta_real=round(eta_r, 6), clas_real=val.clasificacion.value,
                 d_eta_rel=round(rel, 6), misma_clas=misma,
                 verificada=bool(rel < TOL_REL and misma))
    except Exception as exc:                       # el fallo real queda registrado
        d.update(verificada=False, msg=f"{type(exc).__name__}: {exc}"[:240])
    d["t_s"] = round(time.perf_counter() - t0, 1)
    return d


def seleccionar_corregibles(filas, n):
    """Complemento: `n` recuperadas válidas CORREGIBLE (el 94 % de lo recuperado),
    repartidas por barrido de origen; la muestra principal quedó cargada de soluciones
    espurias (falla N2) por su regla de selección."""
    val = [dict(f, motivo=f"CORREGIBLE: {f['csv_origenes'].split(';')[0].split('/')[-1]}")
           for f in filas if f["convergio"] == "True" and f["clasificacion"] == "CORREGIBLE"]
    por_origen, elegidas = {}, []
    for f in val:
        por_origen.setdefault(f["csv_origenes"].split(";")[0], []).append(f)
    while len(elegidas) < min(n, len(val)):
        for lista in por_origen.values():
            if lista and len(elegidas) < n:
                elegidas.append(lista.pop(len(lista) // 2))
    return elegidas


def main():
    global CSV_OUT
    with CSV_IN.open(encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.DictReader(fh))
    if "--corregibles" in sys.argv:
        CSV_OUT = OUT / "verificacion_real_corregibles.csv"
        muestra = seleccionar_corregibles(filas, int(sys.argv[sys.argv.index("--corregibles") + 1]))
    else:
        muestra = seleccionar(filas)
    hecho = set()
    if CSV_OUT.exists():
        with CSV_OUT.open(encoding="utf-8-sig", newline="") as fh:
            hecho = {r["clave"] for r in csv.DictReader(fh)}
    pend = [f for f in muestra if f["clave"] not in hecho]
    _log(f"=== inicio: muestra={len(muestra)} ya_hechas={len(hecho)} pendientes={len(pend)}")
    nuevo = not CSV_OUT.exists() or CSV_OUT.stat().st_size == 0
    t0 = time.perf_counter()
    with CSV_OUT.open("a", encoding="utf-8-sig" if nuevo else "utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, restval="", extrasaction="ignore")
        if nuevo:
            w.writeheader()
        with ProcessPoolExecutor(max_workers=NW) as pool:
            for n, fut in enumerate(as_completed([pool.submit(verificar, f) for f in pend]), 1):
                d = fut.result()
                w.writerow(d)
                fh.flush()
                _log(f"{n}/{len(pend)} ({time.perf_counter()-t0:.0f}s) {d['motivo']} -> "
                     f"verificada={d['verificada']} d_eta_rel={d.get('d_eta_rel')} "
                     f"clas {d['clas_teqp']}/{d.get('clas_real')} t={d['t_s']}s {d.get('msg', '')[:80]}")
    _log(f"=== fin {time.perf_counter()-t0:.0f} s")


if __name__ == "__main__":
    main()

"""M9 — paso 2: selección hacia adelante y el conjunto máximo (final_M9 §2).

Ronda 1: el mejor de los 6 escenarios del paso 1 es el conjunto S. Rondas
siguientes: S pasa a ser el mejor `S∪g` de la ronda (máx. 3 rondas; en cada una
50 LHS con `seed = 20261108 + índice correlativo`). Se cierra con la primera de:
ningún `S∪g` de la ronda tiene KALINA, S ya tiene 4 grupos, o se pasan 3 h 15 min
desde `m9_tiempos.csv`. Luego, para cada `S∪g` de la última ronda con 0 KALINA
(hasta 2, los de menor D_min) se corre la búsqueda dirigida de `m9_busqueda.py`.
Salidas: `m9_paso2.csv`, `m9_busqueda.csv` y `m9_escalera.csv`. Reanudable por
`(ronda, conjunto, id)`. Con `M9_HUMO=1`: 2 puntos por conjunto y 2 rondas.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, evaluar_punto  # noqa: E402
import m9_datos as m9  # noqa: E402
import m9_busqueda  # noqa: E402

N_WORKERS = 7
N_LHS = 2 if m9.HUMO else 50
RONDAS_MAX = 2 if m9.HUMO else 3
SEED0 = 20261108
T_TOPE = 3 * 3600 + 15 * 60
TODOS = ("TF", "EF", "PA", "PB", "TS", "XB")
CAMP = ["ronda", "escenario", "conservados", "id", "omitido"] + list(COLS)
CEST = ["ronda", "conservados", "n_conservadas", "n_eval", "n_genuinos",
        "n_kalina", "n_kalina_confiable", "D_min", "criterio_mas_roto",
        "elegido", "kalina_por_busqueda"]


def _eval(t: dict) -> dict:
    """UNA corrida de la LHS del paso 2 en un hijo del pool."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["tag"],
                      t_amb_diseno=t["combo"]["T_sumidero"])
    f.update(ronda=t["ronda"], escenario=t["escenario"],
             conservados=t["conservados"], id=t["id"], omitido=False)
    return f


def _correr(codes, ronda, seed, pool, esc, fh, previos) -> list:
    """Corre (o reanuda) la LHS de un conjunto y devuelve todas sus filas."""
    nombre = "+".join(codes)
    res, fut = {}, {}
    for i, p in enumerate(m9.muestra(codes, N_LHS, seed)):
        key = (str(ronda), nombre, str(i))
        if key in previos:
            res[i] = previos[key]
            continue
        c = {v: p[v] for v in (*m9.VARS10, "m_b")}
        t = dict(combo=c, ronda=ronda, escenario=nombre, conservados=nombre,
                 id=i, tag=f"m9:P2:{ronda}:{nombre}")
        if c["P_baja"] >= c["P_alta"] - m9.DP_MIN:
            f = m9.omitido(c, tag=t["tag"])
            f.update(ronda=ronda, escenario=nombre, conservados=nombre, id=i,
                     omitido=True)
            res[i] = f
            esc.writerow({col: f.get(col) for col in CAMP}); fh.flush()
        else:
            fut[i] = pool.submit(_eval, t)
    for i, fu in fut.items():
        res[i] = fu.result()
        esc.writerow({col: res[i].get(col) for col in CAMP}); fh.flush()
    return [res[i] for i in sorted(res)]


def _fila(ronda, codes, rows, elegido, kal=False) -> dict:
    r = m9.resumen(rows)
    ds = [f["D"] for f in rows if m9.genu(f) and f.get("D") is not None]
    cod, n = m9.criterio_mas_roto(rows)
    return dict(ronda=ronda, conservados="+".join(codes),
                n_conservadas=m9.n_conservadas(codes), n_eval=len(rows),
                n_genuinos=r["n_genuinos"], n_kalina=r["n_kalina"],
                n_kalina_confiable=r["n_conf"], D_min=min(ds) if ds else None,
                criterio_mas_roto=f"{cod}:{n}" if cod else "", elegido=elegido,
                kalina_por_busqueda=kal)


def _parte1() -> tuple:
    """Lee `m9_paso1.csv`, devuelve la escalera de la ronda 0 y el ranking."""
    rows = m9.leer(m9.OUT / "m9_paso1.csv")
    por = {}
    for f in rows:
        por.setdefault(f["conservados"], []).append(f)
    rank = sorted(por, key=lambda g: m9.clave_ranking(por[g]))
    escalera = [_fila(0, [g], por[g], g == rank[0]) for g in por]
    print("paso1 ranking:", [(g, m9.resumen(por[g])) for g in rank], flush=True)
    return escalera, rank


def _dmin(rows):
    ds = [f["D"] for f in rows if m9.genu(f) and f.get("D") is not None]
    return min(ds) if ds else None


def _busqueda_dirigida(ultima, pool, fh, esc) -> list:
    """Búsqueda dirigida en los 0-KALINA de la última ronda (máx. 2)."""
    cand = [(_dmin(r), codes, r) for codes, r in ultima
            if not any(m9.es_kalina(f) for f in r)]
    cand.sort(key=lambda t: t[0] if t[0] is not None else 1e18)
    tocados = []
    for _, codes, r in cand[:2]:
        gen = [f for f in r if m9.genu(f) and f.get("D") is not None]
        if not gen:
            continue
        base = min(gen, key=lambda f: f["D"])
        print(f"  busqueda dirigida {'+'.join(codes)}: LHS 0 KALINA, "
              f"base D={base['D']}", flush=True)
        ok = m9_busqueda.buscar(codes, {v: base[v] for v in (*m9.VARS10, "m_b")},
                                pool, fh, esc)
        tocados.append(("+".join(codes), ok))
    return tocados


def main() -> None:
    m9.OUT.mkdir(parents=True, exist_ok=True)
    inicio = m9.leer_inicio() or time.time()
    escalera, rank = _parte1()
    S, ultima, i_corr, ronda = [rank[0]], [], 0, 0
    corte = "S alcanzó 4 grupos"
    fh, esc, _v = m9.reanudar(
        m9.OUT / "m9_paso2.csv", CAMP,
        lambda f: (str(f.get("ronda")), f.get("conservados"), str(f.get("id"))))
    previos = {(str(f.get("ronda")), f.get("conservados"), str(f.get("id"))): f
               for f in m9.leer(m9.OUT / "m9_paso2.csv")}
    tocados = []
    t0 = time.perf_counter()
    try:
        with open(m9.OUT / "m9_busqueda.csv", "w", encoding="utf-8",
                  newline="") as fb:
            escb = csv.DictWriter(fb, fieldnames=m9_busqueda.CBUS)
            escb.writeheader(); fb.flush()
            with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
                while len(S) < 4 and ronda < RONDAS_MAX:
                    if time.time() - inicio > T_TOPE:
                        corte = "se pasaron 3 h 15 min"; break
                    ronda += 1
                    otros = [g for g in TODOS if g not in S]
                    if not otros:
                        corte = "no quedan grupos"; break
                    ultima = []
                    for g in otros:
                        i_corr += 1
                        rows = _correr(S + [g], ronda, SEED0 + i_corr, pool,
                                       esc, fh, previos)
                        ultima.append((S + [g], rows))
                    rank2 = sorted(ultima, key=lambda t: m9.clave_ranking(t[1]))
                    for codes, rows in ultima:
                        escalera.append(_fila(ronda, codes, rows,
                                              codes == rank2[0][0]))
                    gan = rank2[0]
                    print(f"ronda {ronda}: ganador {gan[0]} "
                          f"{m9.resumen(gan[1])}", flush=True)
                    if not any(m9.es_kalina(f) for f in gan[1]):
                        corte = "ningún S∪g de la ronda tiene KALINA"; break
                    S = gan[0]
                tocados = _busqueda_dirigida(ultima, pool, fb, escb)
    finally:
        fh.close()
    for codes, ok in tocados:
        for e in escalera:
            if e["conservados"] == codes:
                e["kalina_por_busqueda"] = ok
    with open(m9.OUT / "m9_escalera.csv", "w", encoding="utf-8",
              newline="") as fh2:
        w = csv.DictWriter(fh2, fieldnames=CEST)
        w.writeheader()
        w.writerows({c: e.get(c) for c in CEST} for e in escalera)
        fh2.flush()
    (m9.OUT / "m9_paso2_corte.txt").write_text(corte, encoding="utf-8")
    print(f"M9 paso 2 fin: S={S}, corte={corte}, búsqueda={tocados}, "
          f"{time.perf_counter() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()

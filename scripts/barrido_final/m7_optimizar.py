"""M7 — búsqueda por patrones: η máximo dentro de la región KALINA.

Objetivo lexicográfico (MATEMATICA §7.2): minimizar `(D, −η)` — primero llegar
a D = 0 (KALINA) y, entre los KALINA, maximizar η. Los 5 arranques corren en
secuencia; cada iteración evalúa en paralelo (pool de 7) los candidatos
`u ± paso·e_i` (recortados a [0, 1]) de las variables libres, acepta el mejor
y, si ninguno mejora, divide el paso entre 2. Se corta con `paso < 0.01` o 120
evaluaciones por arranque. Un candidato con `P_baja ≥ P_alta − 300` se
descarta sin evaluarse; un no genuino o un punto sin D nunca mejora. Piso de
O2 = `T_sumidero`; solo motor teqp. Salidas en
`resultados/2026-10-07_final_M7/`; con `M7_HUMO=1`: A1, 1 iteración, `humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402
from m2s_corrida import BASES  # noqa: E402

HUMO = os.environ.get("M7_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M7/humo" if HUMO
                              else "2026-10-07_final_M7")
N_WORKERS = 7
PASO0, PASO_MIN, MAX_EVAL, DP_MIN = 0.10, 0.01, 120, 300.0
MAX_IT = 1 if HUMO else 10 ** 9          # humo: 1 arranque con 1 iteración
GENUINAS = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
# Caja de búsqueda de TASK_CONTEXT final_M7 (§caja); m_b queda fija en 1.0.
CAJA = {"T_fuente": (380.0, 500.0), "T_sumidero": (278.15, 303.55),
        "P_alta": (2000.0, 5000.0), "P_baja": (300.0, 2500.0),
        "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
        "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
        "eps_cond": (0.40, 0.95)}
FIJAS = {"A1": (), "A2": (), "A3": ("T_fuente", "T_sumidero"),
         "A4": ("P_alta", "P_baja", "T_sumidero"), "A5": ("T_fuente", "x_b")}
CAB = ["arranque", "iteracion", "paso", "aceptado"] + list(COLS)


def _leer(carpeta: str, nombre: str) -> list:
    """Filas (texto) de un CSV de la campaña."""
    with open(_RAIZ / "resultados" / carpeta / nombre, encoding="utf-8",
              newline="") as fh:
        return list(csv.DictReader(fh))


def arranques() -> list:
    """Los 5 arranques (TASK_CONTEXT §arranques): id, variables y fijas."""
    top = _leer("2026-10-07_final_M4b", "m4b_top_kalina.csv")
    r1 = min(top, key=lambda f: int(float(f["puesto"])))       # top 1 de M4b
    m2 = _leer("2026-10-06_final_M2S", "m2s_kalina.csv")
    r2 = max((f for f in m2 if f["base"] == "B2"
              and float(f["T_sumidero_val"]) == 278.15),
             key=lambda f: float(f["eta"]))                    # mejor de B2
    m5 = _leer("2026-10-07_final_M5", "m5_cercano_profesor.csv")
    r3 = next(f for f in m5 if f["escenario"] == "1"
              and f["tipo"] == "mejor_eta")                    # S1
    r5 = next(f for f in m5 if f["escenario"] == "5"
              and f["tipo"] == "mejor_eta")                    # S5
    a2 = dict(PROFESOR, **BASES["B2"], T_sumidero=278.15,
              P_baja=float(r2["P_baja_val"]))
    a4 = dict(PROFESOR, T_fuente=403.0, eps_cond=0.95)         # M2R parte 3
    return [dict(id="A1", combo={v: float(r1[v]) for v in CAJA},
                 fijas=FIJAS["A1"]),
            dict(id="A2", combo=a2, fijas=FIJAS["A2"]),
            dict(id="A3", combo={v: float(r3[v]) for v in CAJA},
                 fijas=FIJAS["A3"]),
            dict(id="A4", combo=a4, fijas=FIJAS["A4"]),
            dict(id="A5", combo={v: float(r5[v]) for v in CAJA},
                 fijas=FIJAS["A5"])]


def _a_u(combo: dict, libres: list) -> list:
    """u = (v − a)/(b − a) de cada variable libre."""
    return [(combo[v] - CAJA[v][0]) / (CAJA[v][1] - CAJA[v][0])
            for v in libres]


def _de_u(u: list, libres: list) -> dict:
    """Las variables libres de vuelta a sus unidades."""
    return {v: CAJA[v][0] + w * (CAJA[v][1] - CAJA[v][0])
            for v, w in zip(libres, u)}


def _candidatos(u: list, paso: float) -> list:
    """Pares (i, u') de `u ± paso·e_i` recortado a [0, 1] con movimiento real."""
    out = []
    for i, ui in enumerate(u):
        for s in (1.0, -1.0):
            w = min(1.0, max(0.0, ui + s * paso))
            if w != ui:                       # el recorte lo dejó donde estaba
                out.append((i, w))
    return out


def _clave(f: dict):
    """`(D, −η)` si el punto es elegible; `None` si no lo es."""
    if f.get("clasificacion") not in GENUINAS or f.get("eta") is None:
        return None
    return None if f.get("D") is None else (f["D"], -f["eta"])


def _evaluar(t: dict):
    """Corre UN candidato en un hijo del pool; devuelve (índice, u, fila)."""
    c = t["combo"]
    f = evaluar_punto(c, motor="teqp", tag=t["tag"],
                      t_amb_diseno=c["T_sumidero"])
    f.update(arranque=t["arr"], iteracion=t["it"], paso=t["paso"],
             aceptado=False)
    return t["idx"], t["u"], f


def _escribir(fh, esc, fila: dict) -> None:
    """Una fila con flush en su CSV."""
    esc.writerow({c: fila.get(c) for c in CAB})
    fh.flush()


def optimizar(arr: dict, pool, fe, esc_e, ft, esc_t) -> None:
    """La búsqueda por patrones de UN arranque (secuencia de iteraciones)."""
    libres = [v for v in CAJA if v not in arr["fijas"]]
    c0 = dict(arr["combo"], m_b=1.0)
    u = _a_u(c0, libres)
    paso, n_eval, it = PASO0, 0, 0
    base = evaluar_punto(c0, motor="teqp", tag=arr["id"],
                         t_amb_diseno=c0["T_sumidero"])
    base.update(arranque=arr["id"], iteracion=0, paso=0.0, aceptado=True)
    _escribir(fe, esc_e, base)
    _escribir(ft, esc_t, base)
    k0, n_eval, actual = _clave(base), 1, base
    print(f'{arr["id"]} inicio: D={base["D"]} eta={base["eta"]} '
          f'libres={len(libres)} ({", ".join(libres)})', flush=True)
    while n_eval < MAX_EVAL and it < MAX_IT and paso >= PASO_MIN:
        it += 1
        tareas = []
        for i, w in _candidatos(u, paso):
            uu = list(u)
            uu[i] = w
            c = dict(c0, **_de_u(uu, libres))
            if c["P_baja"] >= c["P_alta"] - DP_MIN:     # descartado, sin eval
                continue
            tareas.append(dict(idx=len(tareas), u=uu, combo=c, arr=arr["id"],
                               it=it, paso=paso,
                               tag=f'{arr["id"]}:{it}:{len(tareas)}'))
        if not tareas:                                  # nada que probar
            paso /= 2.0
            continue
        if n_eval + len(tareas) > MAX_EVAL:             # no pasar de 120
            break
        futs = [pool.submit(_evaluar, t) for t in tareas]
        res = sorted(f.result() for f in as_completed(futs))  # orden de envío
        n_eval += len(res)
        validos = [(_clave(f), j, uu, f) for j, (_, uu, f) in enumerate(res)
                   if _clave(f) is not None]
        mej = min(validos) if validos else None
        gana = mej is not None and (k0 is None or mej[0] < k0)
        if gana:
            k0, u, actual = mej[0], mej[2], mej[3]
            actual["aceptado"] = True
        else:
            paso /= 2.0
        for _, _, f in res:                             # todas, con flush
            _escribir(fe, esc_e, f)
        if gana:
            _escribir(ft, esc_t, actual)
        print(f'{arr["id"]} it={it} n={n_eval} cands={len(res)} '
              f'{"ACEPTA" if gana else "divide paso"} paso={paso:.5f} '
              f'D={k0[0] if k0 else None} eta={actual["eta"]}', flush=True)
    print(f'{arr["id"]} fin: {n_eval} evaluaciones, {it} iteraciones, '
          f'D={actual["D"]} eta={actual["eta"]}', flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    arrs = arranques()[:1] if HUMO else arranques()
    print(f"M7 | humo={HUMO} | arranques={[a['id'] for a in arrs]} | "
          f"{N_WORKERS} workers -> {OUT}", flush=True)
    t0 = time.perf_counter()
    with open(OUT / "m7_evaluaciones.csv", "w", encoding="utf-8",
              newline="") as fe, \
            open(OUT / "m7_trayectorias.csv", "w", encoding="utf-8",
                 newline="") as ft:
        esc_e = csv.DictWriter(fe, fieldnames=CAB)
        esc_e.writeheader()
        fe.flush()
        esc_t = csv.DictWriter(ft, fieldnames=CAB)
        esc_t.writeheader()
        ft.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
            for a in arrs:
                optimizar(a, pool, fe, esc_e, ft, esc_t)
    print(f"fin: {time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()

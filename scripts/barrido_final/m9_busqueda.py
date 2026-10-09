"""M9 — paso 2.4: búsqueda dirigida por patrones para rescatar un conjunto.

Cuando un `S∪g` del paso 2 da 0 KALINA, el LHS pudo fallar en una franja
angosta. Para cada uno de esos conjuntos (como mucho 2, los de menor D_min) se
parte de su genuino de menor D y se hace una búsqueda por patrones que minimiza
SOLO D sobre las variables libres normalizadas a [0, 1]: paso inicial 0.15, que
se divide a la mitad cuando ningún vecino ±paso mejora; paso mínimo 0.02; máximo
40 evaluaciones; se detiene apenas D = 0 (KALINA). Reutiliza `_candidatos` de
`m7_optimizar.py` (sin modificarlo); `_a_u`/`_de_u` son locales porque la caja
de M9 es distinta de la caja de M7. Salida: `m9_busqueda.csv`.
"""
from __future__ import annotations

import csv, sys  # noqa: E401,E402
from concurrent.futures import as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, evaluar_punto  # noqa: E402
import m9_datos as m9  # noqa: E402
from m7_optimizar import _candidatos  # noqa: E402

PASO0, PASO_MIN, MAX_EVAL = 0.15, 0.02, 40
CBUS = ["conjunto", "conservados", "iteracion", "paso", "aceptado"] + list(COLS)


def _a_u(combo: dict, lib: list) -> list:
    """u = (v − a)/(b − a) de cada variable libre (caja de M9)."""
    return [(combo[v] - m9.CAJA[v][0]) / (m9.CAJA[v][1] - m9.CAJA[v][0])
            for v in lib]


def _de_u(u: list, lib: list, c0: dict) -> dict:
    """Combo con las libres de vuelta a sus unidades (las fijas de `c0`)."""
    c = dict(c0)
    for v, w in zip(lib, u):
        a, b = m9.CAJA[v]
        c[v] = a + w * (b - a)
    return c


def _eval(t: dict) -> dict:
    """UNA evaluación de un vecino en un hijo del pool."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["tag"],
                      t_amb_diseno=t["combo"]["T_sumidero"])
    f.update(conjunto=t["conjunto"], conservados=t["conservados"],
             iteracion=t["it"], paso=t["paso"], aceptado=False)
    return t["idx"], f


def _clave(f: dict):
    """`D` del vecino si es genuino y tiene D; `None` si no."""
    if not m9.genu(f) or f.get("D") is None:
        return None
    return f["D"]


def buscar(codes: list, base: dict, pool, fh, esc) -> bool:
    """Búsqueda por patrones de UN conjunto; `True` si encuentra KALINA."""
    lib = m9.libres(codes)
    nombre = "+".join(codes)
    c0 = dict(base)
    u = _a_u(c0, lib)
    paso, n_eval, it = PASO0, 0, 0
    b0 = evaluar_punto(c0, motor="teqp", tag=f"m9:B:{nombre}",
                       t_amb_diseno=c0["T_sumidero"])
    b0.update(conjunto=nombre, conservados=nombre, iteracion=0, paso=0.0,
              aceptado=True)
    esc.writerow({c: b0.get(c) for c in CBUS})
    fh.flush()
    n_eval += 1
    k0, mejor = _clave(b0), b0
    print(f'  busqueda {nombre}: base D={b0["D"]} eta={b0["eta"]} '
          f'libres={len(lib)}', flush=True)
    encontro = m9.es_kalina(b0)
    while (not encontro and n_eval < MAX_EVAL and paso >= PASO_MIN):
        it += 1
        tareas = []
        for idx, w in _candidatos(u, paso):
            uu = list(u)
            uu[idx] = w
            c = _de_u(uu, lib, c0)
            if c["P_baja"] >= c["P_alta"] - m9.DP_MIN:
                continue
            tareas.append(dict(idx=len(tareas), combo=c, conjunto=nombre,
                               conservados=f"{nombre}@{it}",
                               it=it, paso=paso, u=uu,
                               tag=f"m9:B:{nombre}:{it}:{len(tareas)}"))
        if not tareas:
            paso /= 2.0
            continue
        if n_eval + len(tareas) > MAX_EVAL:
            break
        futs = [pool.submit(_eval, t) for t in tareas]
        res = sorted(fu.result() for fu in as_completed(futs))
        n_eval += len(res)
        validos = [(_clave(f), i, t["u"], f)
                   for (i, f), t in zip(res, tareas) if _clave(f) is not None]
        mej = min(validos) if validos else None
        gana = mej is not None and (k0 is None or mej[0] < k0)
        elegido = mej[3] if gana else None
        if gana:
            k0, u, mejor = mej[0], mej[2], elegido
        for _, f in res:
            f["aceptado"] = gana and f is elegido
            esc.writerow({c: f.get(c) for c in CBUS})
        fh.flush()
        encontro = k0 == 0.0
        print(f'  {nombre} it={it} n={n_eval} cands={len(res)} '
              f'{"ACEPTA" if gana else "divide"} paso={paso:.3f} D={k0} '
              f'eta={mejor["eta"]}', flush=True)
    return encontro

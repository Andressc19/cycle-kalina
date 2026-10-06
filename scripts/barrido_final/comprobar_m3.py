"""Comprobación final de M3 (TASK_CONTEXT final_M3, paso 4).
Verifica (a) filas y columnas de `m3_ofat.csv` más la estructura de la malla,
(b) que E y Δη se recalculan a mano para dos variables, (c) que `m3_resumen.csv`
y `m3_cruces.csv` tienen la forma pedida, (d) que las tres figuras existen y
(e) que `REPORTE_M3.md` trae las 10 secciones. rc=1 si algo falla."""
from __future__ import annotations

import csv, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m3_analisis as an  # noqa: E402
import m3_ofat as ofat  # noqa: E402

OUT = ofat.OUT
GEN = ("KALINA", "CORREGIBLE", "INVIABLE")
FALLOS: list = []


def ck(ok, msg, det="") -> bool:
    print(f"OK   {msg}" if ok else f"FALLO {msg} :: {det}")
    if not ok:
        FALLOS.append(f"{msg} :: {det}")
    return bool(ok)


def n(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def leer(nombre):
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def parte_a(filas):
    """(a) 171 filas, columnas CM3 y la estructura 1 + 10×(15 + 2)."""
    ck(len(filas) == 171, "m3_ofat.csv: 171 filas", f"filas={len(filas)}")
    ck(list(filas[0]) == ofat.CM3, "m3_ofat.csv: columnas == CM3", str(list(filas[0])[:5]))
    tipos = {}
    for f in filas:
        tipos[f["tipo_punto"]] = tipos.get(f["tipo_punto"], 0) + 1
    ck(tipos == {"ancla": 1, "malla": 150, "vecino": 20}, "reparto 1 ancla / 150 malla / 20 vecino",
       str(tipos))
    for nom, a, b in ofat.RANGOS:
        m = sorted([n(f["valor"]) for f in filas
                    if f["variable"] == nom and f["tipo_punto"] == "malla"])
        esp = ofat.malla(a, b)
        ck(len(m) == 15 and all(abs(x - y) < 1e-9 for x, y in zip(m, esp)),
           f"malla de {nom}: 15 valores a + j(b-a)/14", str(m[:3]))
        v = sorted([n(f["valor"]) for f in filas
                    if f["variable"] == nom and f["tipo_punto"] == "vecino"])
        h = 0.01 * (b - a)
        ck(len(v) == 2 and abs(v[0] - (ofat.ANCHOR[nom] - h)) < 1e-9
           and abs(v[1] - (ofat.ANCHOR[nom] + h)) < 1e-9,
           f"vecinos de {nom}: A* ± 0.01(b-a)", str(v))


def _a_mano(filas, nom):
    """E y Δη de `nom`, calculados aquí desde el CSV crudo (sin m3_analisis)."""
    a, b = next((x, y) for k, x, y in ofat.RANGOS if k == nom)
    h = 0.01 * (b - a)
    eta0 = n(next(f for f in filas if f["tipo_punto"] == "ancla")["eta"])
    vec = sorted([f for f in filas if f["variable"] == nom
                  and f["tipo_punto"] == "vecino"], key=lambda f: n(f["valor"]))
    E = (n(vec[1]["eta"]) - n(vec[0]["eta"])) / (2 * h) * ofat.ANCHOR[nom] / eta0
    ets = [n(f["eta"]) for f in filas if f["variable"] == nom
           and f["tipo_punto"] == "malla" and f["clasificacion"] in GEN
           and n(f["eta"]) is not None]
    return E, max(ets) - min(ets), len(ets)


def parte_b(filas, res):
    """(b) E y Δη recalculados a mano para dos variables, contra m3_resumen.csv."""
    for nom in ("T_fuente", "eps_cond"):
        E, dE, cnt = _a_mano(filas, nom)
        fila = next(r for r in res if r["variable"] == nom)
        ck(abs(E - n(fila["E_eta"])) <= 1e-12 * max(1.0, abs(E)),
           f"E de {nom} recalculada a mano", f"{E} vs {fila['E_eta']}")
        ck(abs(dE - n(fila["delta_eta"])) <= 1e-12 * max(1.0, abs(dE)),
           f"Δη de {nom} recalculada a mano ({cnt} genuinos)",
           f"{dE} vs {fila['delta_eta']}")


def parte_c(res, cruces):
    """(c) columnas y número de filas de resumen y cruces."""
    ck(len(res) == 10 and list(res[0]) == an.CRES,
       "m3_resumen.csv: 10 filas con CRES", f'filas={len(res)} cols={list(res[0])[:4]}')
    ck(list(cruces[0]) == an.CCRU, "m3_cruces.csv: columnas CCRU", str(list(cruces[0])))
    ck({c["tipo"] for c in cruces} <= {"margen", "clase"}, "cruces: tipo margen/clase",
       str({c["tipo"] for c in cruces}))
    mal = [c for c in cruces if c["tipo"] == "margen"
           and not (n(c["v_j"]) <= n(c["v_cruce"]) <= n(c["v_j1"])
                    or n(c["v_j1"]) <= n(c["v_cruce"]) <= n(c["v_j"]))]
    ck(not mal, "cruces: v_cruce entre v_j y v_j1", str(mal[:2]))


def parte_f(res):
    """(f) «al bajar / al subir» = primer punto de la malla más allá del borde."""
    import m3_reporte as rep

    _, g = an.agrupar(an.leer())   # an.leer() convierte valor/eta a float
    for r in res:
        m = g[r["variable"]][2]
        for lado, ext, sgn in (("bajar", n(r["kalina_desde"]), -1),
                               ("subir", n(r["kalina_hasta"]), +1)):
            if ext is None:
                esp = "sin zona KALINA"
            else:
                fuera = [f for f in m if (n(f["valor"]) - ext) * sgn > 0]
                if not fuera:
                    esp = "— (llega al extremo del rango)"
                else:
                    f = min(fuera, key=lambda x: abs(n(x["valor"]) - ext))
                    lado_ok = (n(f["valor"]) - ext) * sgn > 0
                    ck(lado_ok, f'{r["variable"]} {lado}: punto {f["valor"]} más allá de {ext}')
                    esp = f'{f["codigos_falla"] or "sin código"} ({f["clasificacion"]})'
            ck(rep._lado(m, ext, sgn) == esp, f'_lado {r["variable"]} ({lado})',
               f'{rep._lado(m, ext, sgn)} vs {esp}')


def parte_d():
    """(d) las tres figuras existen, pesan y traen contenido (no están en blanco)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for nom in ("m3_tornado.png", "m3_elasticidad.png", "m3_curvas.png"):
        p = OUT / nom
        if not ck(p.exists() and p.stat().st_size > 20000, f"{nom} existe y pesa > 20 kB",
                 f"{p.stat().st_size if p.exists() else 'no existe'} bytes"):
            continue
        img = plt.imread(p)
        ck(img.shape[0] >= 600 and img.shape[1] >= 800 and float(img.std()) > 0.02,
           f"{nom}: dimensiones y contenido no nulos",
           f"shape={img.shape} std={float(img.std()):.4f}")


def parte_e():
    """(e) REPORTE_M3.md con las 10 secciones."""
    p = OUT / "REPORTE_M3.md"
    if not ck(p.exists(), "REPORTE_M3.md existe", str(p)):
        return
    txt = p.read_text(encoding="utf-8")
    for i in range(1, 11):
        ck(f"## {i}." in txt, f"reporte: sección {i}", "")
    ck("![Tornado](m3_tornado.png)" in txt and "![Curvas](m3_curvas.png)" in txt,
       "reporte: enlaza las figuras", "")


def info(filas):
    """Dato para el informe (no es un check): puntos genuinos con η ≤ 0."""
    neg = [(f["variable"], n(f["valor"]), n(f["eta"])) for f in filas
           if f["clasificacion"] in GEN and n(f["eta"]) is not None and n(f["eta"]) <= 0]
    print(f"INFO: {len(neg)} puntos genuinos con eta <= 0 -> "
          + "; ".join(f'{v}={val:g} eta={e:.4f}' for v, val, e in neg))


def main() -> int:
    filas, res, cruces = leer("m3_ofat.csv"), leer("m3_resumen.csv"), leer("m3_cruces.csv")
    for parte in (lambda: parte_a(filas), lambda: parte_b(filas, res),
                  lambda: parte_c(res, cruces), lambda: parte_f(res),
                  parte_d, parte_e):
        parte()
    info(filas)
    print(f"\n{len(FALLOS)} fallos" if FALLOS else "\nTODO OK")
    for f in FALLOS:
        print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())

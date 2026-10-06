"""M4 — verificación de la salida (TASK_CONTEXT final_M4, paso 4).

Comprueba, leyendo los CSV de nuevo y sin recalcular el ciclo: (1) que
`m4_muestra.csv` y `m4_lhs.csv` coinciden; (2) la propiedad LHS (un punto por
franja en cada variable); (3) que el KS de dos variables, recalculado a mano,
coincide con `m4_rsa.csv`; (4) que los números de `REPORTE_M4.md` coinciden con
los CSV (conteos, tabla RSA, top-10, ρ de Spearman y tiempo). Imprime
`ok`/`FALLA` por chequeo y devuelve 1 si algo falla.
"""
from __future__ import annotations

import csv, re, sys  # noqa: E401,E402
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m4_datos import CAJA, OUT, VARS10, VARS13, leer  # noqa: E402

fallos = []


def ck(ok, msg, det=""):
    print(("ok    " if ok else "FALLA ") + msg + ("" if ok else f"  [{det}]"),
          flush=True)
    if not ok:
        fallos.append(msg)


def _cerca(a, b, rel=1e-5, abs_=6e-4):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def leer_csv(nombre):
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _f(c):
    c = (c or "").strip().strip("[]")
    try:
        return float(c.split(",")[0])
    except ValueError:
        return None


def _num(x):
    """Celda numérica del CSV: vacío → `None`."""
    return None if x in (None, "") else float(x)


def _par(c):
    """Celda `[a, b]` → `(a, b)`."""
    c = (c or "").strip().strip("[]")
    p = [x.strip() for x in c.split(",")]
    if len(p) != 2:
        return None, None
    try:
        return float(p[0]), float(p[1])
    except ValueError:
        return None, None


def _seccion(txt, desde, hasta):
    return txt.split(desde)[1].split(hasta)[0]


def _filas_tabla(trozo):
    return [l.split("|")[1:-1] for l in trozo.splitlines()
            if l.startswith("| ") and not l.startswith("| variable")
            and not l.startswith("|---") and not l.startswith("| #")]


def ks_a_mano(filas, v):
    """KS a mano: máxima separación entre las dos CDF empíricas."""
    b = [f[v] for f in filas if f["clasificacion"] == "KALINA"]
    bb = [f[v] for f in filas if f["clasificacion"] != "KALINA"]
    if not b or not bb:
        return None
    xs = sorted(set(b + bb))
    fb = sum(1 for x in b if x <= xs[0]) / len(b)
    fbb = sum(1 for x in bb if x <= xs[0]) / len(bb)
    mejor = abs(fb - fbb)
    for x in xs[1:]:
        fb = sum(1 for y in b if y <= x) / len(b)
        fbb = sum(1 for y in bb if y <= x) / len(bb)
        mejor = max(mejor, abs(fb - fbb))
    return mejor


def chk_muestra():
    mue, filas = leer_csv("m4_muestra.csv"), leer()
    ck(len(mue) == len(filas), f"m4_muestra.csv y m4_lhs.csv: mismo nº de filas "
        f"({len(mue)} vs {len(filas)})")
    por_id = {int(f["id_muestra"]): f for f in filas}
    dif, ids_ok = 0.0, True
    for r in mue:
        f = por_id.get(int(r["id_muestra"]))
        if f is None:
            ids_ok = False
            continue
        for v in VARS10:
            dif = max(dif, abs(float(r[v]) - f[v]))
    ck(ids_ok and dif <= 1e-9,
       f"m4_muestra.csv = m4_lhs.csv en las 10 variables (máx dif {dif:.2e})")
    n = len(mue)
    for v in VARS10:
        a, b = CAJA[v]
        u = [(float(r[v]) - a) / (b - a) for r in mue]
        dentro = all(-1e-12 <= x <= 1 + 1e-12 for x in u)
        franjas = sorted(min(n - 1, max(0, int(x * n))) for x in u)
        ck(dentro and franjas == list(range(n)),
           f"LHS: {v} un punto por cada una de las {n} franjas",
           f"dentro={dentro} franjas={franjas[:8]}...")
    for f in filas:
        if abs(f["dP"] - (f["P_alta"] - f["P_baja"])) > 1e-9:
            ck(False, "derivada dP", str(f["id_muestra"]))
            break
    else:
        ck(True, "derivada dP = P_alta − P_baja en todas las filas")


def chk_ks():
    rsa = {(r["separacion"], r["variable"]): r for r in leer_csv("m4_rsa.csv")}
    filas = leer()
    for v in ("P_baja", "T_fuente"):
        a = ks_a_mano(filas, v)
        b = rsa[("KALINA", v)]["KS"]
        b = None if b in (None, "") else float(b)
        ck(a is not None and b is not None and abs(a - b) <= 1e-9,
           f"KS a mano de {v} (separación KALINA) = m4_rsa.csv",
           f"mano={a} csv={b}")


def chk_salidas():
    esperado = {"m4_rsa.csv": 52, "m4_pawn.csv": 20, "m4_prcc.csv": 40,
                "m4_convergencia.csv": 23}
    for nombre, n in esperado.items():
        filas = leer_csv(nombre)
        ck(len(filas) == n, f"{nombre}: {len(filas)} filas (esperado {n})")
    top = leer_csv("m4_top_kalina.csv")
    nk = sum(1 for f in leer() if f["clasificacion"] == "KALINA")
    ck(len(top) == min(10, nk), f"m4_top_kalina.csv: {len(top)} filas "
       f"(esperado {min(10, nk)})")
    ets = [float(f["eta"]) for f in top]
    ck(ets == sorted(ets, reverse=True), "m4_top_kalina.csv: η en orden descendente")
    for nombre in ("m4_cart.txt", "m4_cdf_kalina.png", "m4_prcc_eta.png",
                   "m4_rsa_ks.png", "m4_cart.png"):
        ck((OUT / nombre).exists(), f"existe {nombre}")


def chk_reporte():
    txt = (OUT / "REPORTE_M4.md").read_text(encoding="utf-8")
    filas = leer()
    res = Counter(f["clasificacion"] for f in filas)
    m = re.search(r"De \*\*(\d+)\*\* puntos: \*\*(\d+) KALINA\*\*", txt)
    ck(m and int(m.group(1)) == len(filas) and int(m.group(2)) == res["KALINA"],
       "REPORTE §3: total y nº de KALINA coinciden con m4_lhs.csv",
       m.group(0) if m else "sin la frase")
    m = re.search(r"Conteos por clase: (.*)\.", txt)
    got = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)",
                                            m.group(1))} if m else {}
    ck(got == dict(res), "REPORTE §3: conteos por clase coinciden",
       f"reporte={got} csv={dict(res)}")
    rsa = {(r["separacion"], r["variable"]): r for r in leer_csv("m4_rsa.csv")}
    trozo = _seccion(txt, "Separación **KALINA vs el resto**", "### 4.1")
    filas_t = _filas_tabla(trozo)
    ck(len(filas_t) == 13, f"REPORTE §4: {len(filas_t)} filas de tabla (esperado 13)")
    for c in filas_t:
        v, ks, ic, p, fav, nb, nbbar = [x.strip() for x in c]
        r = rsa[("KALINA", v)]
        lo, hi = _par(ic)
        p05, p95 = _par(fav)
        ok = (_cerca(_f(ks), _num(r["KS"])) and _cerca(lo, _num(r["ic_lo"]))
              and _cerca(hi, _num(r["ic_hi"]))
              and _cerca(_f(p), _num(r["p_valor"]), rel=5e-4)
              and _cerca(p05, _num(r["fav_p05"]), rel=1e-5)
              and _cerca(p95, _num(r["fav_p95"]), rel=1e-5)
              and int(nb) == int(r["n_B"]) and int(nbbar) == int(r["n_Bbar"]))
        ck(ok, f"REPORTE §4: {v} coincide con m4_rsa.csv", str(c))
    top = leer_csv("m4_top_kalina.csv")
    trozo = _seccion(txt, "## 8. Los 10 mejores KALINA", "## 9.")
    ft = _filas_tabla(trozo)
    ck(len(ft) == len(top), f"REPORTE §8: {len(ft)} filas (esperado {len(top)})")
    for c, r in zip(ft, top):
        ck(_cerca(_f(c[2]), _num(r["eta"]), rel=1e-6, abs_=5e-5),
           f"REPORTE §8: η de id {r['id_muestra']} coincide", str(c[:3]))
    conv = {(r["metrica"], r["variable"]): r for r in leer_csv("m4_convergencia.csv")}
    for metrica, etiqueta in (("KS_KALINA", r"KS \(KALINA\) = ([-\d./n]+)"),
                              ("PRCC_eta", r"PRCC\(η\) = ([-\d./n]+)")):
        m = re.search(etiqueta, txt)
        csv_v = _num(conv[(metrica, VARS13[0])]["rho_spearman"])
        if not m:
            ck(False, f"REPORTE §9: falta el ρ de {metrica}")
        elif m.group(1) == "n/d":
            ck(csv_v is None, f"REPORTE §9: ρ {metrica} = n/d coincide con el CSV",
               f"csv={csv_v}")
        else:
            ck(_cerca(float(m.group(1)), csv_v, rel=1e-4, abs_=6e-5),
               f"REPORTE §9: ρ {metrica} coincide con m4_convergencia.csv",
               f"reporte={m.group(1)} csv={csv_v}")
    st = OUT / "stdout.txt"
    if st.exists():
        for enc in ("utf-8", "utf-16", "cp1252", "latin-1"):
            try:
                s = st.read_bytes().decode(enc)
            except (UnicodeDecodeError, ValueError):
                continue
            m = re.search(r"fin: (\d+) corridas en (\d+) s", s)
            if m:
                ck(f"tardó {m.group(2)} s" in txt,
                   "REPORTE §10: el tiempo total coincide con stdout.txt",
                   f"esperado tardó {m.group(2)} s")
                break


def main() -> int:
    chk_muestra()
    chk_ks()
    chk_salidas()
    chk_reporte()
    print(("\nTODO OK" if not fallos else f"\n{len(fallos)} FALLAS: "
           + " | ".join(fallos)), flush=True)
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Comprobación final de M2S (TASK_CONTEXT final_M2S, paso 5) — escrito con `write`.
Verifica (a) conteos/columnas de los cuatro CSV; (b) que no haya duplicados y que el
resumen se recalcula a mano desde malla + bisección; (c) que cada número del
`REPORTE_M2S.md` (§3 a §9) coincide con los CSV; (d) que la figura no está en blanco."""
from __future__ import annotations
import csv, re, sys  # noqa: E401,E402
from pathlib import Path
_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import m2s_corrida as cor  # noqa: E402
import m2s_reporte as rep  # noqa: E402
OUT = cor.OUT
NUM = ("eta", "Wnet", "m_O1", "m_O2", "D", "P_baja_val", "T_sumidero_val",
       "T_amb_diseno", "T_sumidero", "t_s", "B_verificado", "n_genuinos",
       "n_kalina", "n_N2", "P_baja_min_kalina", "eta_min_kalina",
       "B_verificado_min_kalina", "eta_max_kalina", "P_baja_eta_max_kalina")
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
def igual(a, b, tol=1e-9):
    """Dos números (o None) iguales dentro de `tol` relativo."""
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def fuera(f) -> bool:
    return f.get("fuera_rango") in (True, "True", "1", 1)
def leer(nombre):
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for f in filas:
        if "convergio" in f:
            f["convergio"] = f["convergio"] == "True"
        for k in NUM:
            if k in f:
                f[k] = n(f[k])
    return filas
def celdas(res, b, Ts):
    """La pareja (P_baja mínima KALINA, η) de una celda de la tabla §3."""
    r = next(x for x in res if x["base"] == b and x["T_sumidero"] == Ts)
    return ["—", "—"] if r["P_baja_min_kalina"] is None else [f'{r["P_baja_min_kalina"]:g}', f'{r["eta_min_kalina"]:.4f}']


def parte_a(malla, bise, res, kal):
    """(a) conteos, columnas y estructura de los cuatro CSV."""
    ck(len(malla) == 200, "malla: 200 filas", f"filas={len(malla)}")
    ck(list(malla[0]) == cor.CMALLA, "malla: columnas == CMALLA", str(list(malla[0])[:5]))
    claves = [(f["base"], f["T_sumidero_val"], f["P_baja_val"]) for f in malla]
    ck(len(set(claves)) == 200, "malla: sin duplicados (base, T, P_baja)", f"unicos={len(set(claves))}")
    esp = {(b, float(t), float(p)) for b in cor.BASES for t in cor.TSUM for p in cor.P_MALLA}
    ck(set(claves) == esp, "malla: producto cartesiano 4 bases x 5 T x 10 P",
       f"faltan={len(esp - set(claves))} sobran={len(set(claves) - esp)}")
    mal = [f for f in malla if f["T_amb_diseno"] != f["T_sumidero_val"]]
    ck(not mal, "malla: t_amb_diseno == T_sumidero en las 200 filas (el piso sigue al clima)",
       str([(f["T_amb_diseno"], f["T_sumidero_val"]) for f in mal[:3]]))
    ck(all(150.0 <= f["P_baja_val"] <= 1500.0 for f in malla), "malla: P_baja dentro de [150, 1500]", "")
    ck(bool(bise) and list(bise[0]) == cor.CBISE, "biseccion: columnas == CBISE", f"filas={len(bise)}")
    kb = [(f["base"], f["T_sumidero_val"], f["P_baja_val"], f["frontera"], f["iteracion"]) for f in bise]
    ck(len(set(kb)) == len(kb), "biseccion: sin duplicados", f"unicos={len(set(kb))} de {len(kb)}")
    ck(len(res) == 20 and list(res[0]) == rep.CRES, "resumen: 20 filas con CRES",
       f"filas={len(res)} cols={list(res[0])[:4]}")
    ck(len({(r["base"], r["T_sumidero"]) for r in res}) == 20, "resumen: 20 celdas (base, T) únicas", "")
    ck(bool(kal) and list(kal[0]) == rep.CKAL, "kalina: columnas == CKAL", f"filas={len(kal)}")
    kk = [(f["base"], f["T_sumidero_val"], f["P_baja_val"]) for f in kal]
    ck(len(set(kk)) == len(kk), "kalina: sin duplicados (base, T, P_baja)", f"unicos={len(set(kk))} de {len(kk)}")

def parte_b(malla, bise, res, kal):
    """(b) `m2s_resumen.csv` y `m2s_kalina.csv` recalculados desde las fases."""
    todo = malla + bise
    for r in res:
        cel = f'{r["base"]} T={r["T_sumidero"]:g}'
        g = [f for f in todo if f["base"] == r["base"] and f["T_sumidero_val"] == r["T_sumidero"]]
        gen = [f for f in g if cor.genuina(f)]
        ks = sorted([f for f in g if cor.es_kalina(f)], key=lambda f: f["P_baja_val"])
        n2 = sum(1 for f in g if f.get("convergio") is True and f.get("clasificacion") == "NO_CONVERGIO")
        ck(r["n_genuinos"] == len(gen), f"resumen {cel}: n_genuinos", f'{r["n_genuinos"]} vs {len(gen)}')
        ck(r["n_kalina"] == len(ks), f"resumen {cel}: n_kalina", f'{r["n_kalina"]} vs {len(ks)}')
        ck(r["n_N2"] == n2, f"resumen {cel}: n_N2", f'{r["n_N2"]} vs {n2}')
        ce = [f for f in ks if f["eta"] is not None]
        k0, km = (ks[0] if ks else None), (max(ce, key=lambda f: f["eta"]) if ce else None)
        ck(igual(r["P_baja_min_kalina"], k0 and k0["P_baja_val"]), f"resumen {cel}: P_baja_min_kalina",
           str(r["P_baja_min_kalina"]))
        ck(igual(r["eta_min_kalina"], k0 and k0["eta"]), f"resumen {cel}: eta_min_kalina",
           str(r["eta_min_kalina"]))
        ck(str(r["fuera_rango_min_kalina"]) == str(k0["fuera_rango"] if k0 else ""),
           f"resumen {cel}: fuera_rango_min_kalina", str(r["fuera_rango_min_kalina"]))
        ck(igual(r["eta_max_kalina"], km and km["eta"]), f"resumen {cel}: eta_max_kalina",
           str(r["eta_max_kalina"]))
        ck(igual(r["P_baja_eta_max_kalina"], km and km["P_baja_val"]), f"resumen {cel}: P_baja_eta_max",
           str(r["P_baja_eta_max_kalina"]))
    hab = {(f["base"], f["T_sumidero_val"], f["P_baja_val"]) for f in todo if cor.es_kalina(f)}
    ck(len(kal) == len(hab) and sum(r["n_kalina"] for r in res) >= len(hab),
       f"kalina: filas==únicos {len(kal)}; suma n_kalina={sum(r['n_kalina'] for r in res)} (con duplicados) >= {len(hab)}", "")
    ck(all((k["base"], k["T_sumidero_val"], k["P_baja_val"]) in hab for k in kal),
       "kalina: cada fila es KALINA en malla + bisección", "")


def _s8(res, kal):
    """§8, reconstruido aquí desde el resumen (sin usar m2s_reporte)."""
    ok = [b for b in cor.BASES if any(r["n_kalina"] for r in res if r["base"] == b)]
    lin = [f"- **{len(ok)} de {len(cor.BASES)} bases** alcanzan KALINA "
           f"({', '.join(ok) if ok else 'ninguna'}); hay **{len(kal)}** puntos KALINA sin duplicados en total."]
    for b in ok:
        rs = [r for r in res if r["base"] == b and r["eta_min_kalina"] is not None]
        if len(rs) >= 2:
            fr, ca = rs[0], rs[-1]
            lin.append(f"- **{b}**: al bajar el sumidero de {ca['T_sumidero']:g} a {fr['T_sumidero']:g} K, "
                       f"η de {ca['eta_min_kalina']:.4f} a {fr['eta_min_kalina']:.4f} "
                       f"({fr['eta_min_kalina'] - ca['eta_min_kalina']:+.5f}) y la P_baja mínima de "
                       f"{ca['P_baja_min_kalina']:g} a {fr['P_baja_min_kalina']:g} kPa.")
    return lin


def parte_c(res, kal, todo):
    """(c) cada número del REPORTE_M2S.md, recalculado desde los CSV."""
    p = OUT / "REPORTE_M2S.md"
    if not ck(p.exists() and not cor.HUMO, "REPORTE_M2S.md existe fuera de humo/", str(p)):
        return
    txt = p.read_text(encoding="utf-8")
    for i in range(1, 11):
        ck(f"## {i}." in txt, f"reporte: sección {i}", "")
    for Ts in cor.TSUM:
        esp = "| " + f"{Ts:g} | " + " | ".join(sum((celdas(res, b, Ts) for b in cor.BASES), [])) + " |"
        ck(esp in txt, f"reporte §3: fila T_sumidero = {Ts:g}", esp)
    b4 = [r for r in res if r["base"] == "B4"]
    ck(("**Sí.**" in txt) == any(r["n_kalina"] for r in b4), "reporte §4: «Sí/No» según los KALINA de B4",
       f'n_kalina B4 = {sum(r["n_kalina"] for r in b4)}')
    for b in cor.BASES:
        rs = [r for r in res if r["base"] == b]
        ps = []
        for fr, ca in zip(rs, rs[1:]):
            dt = ca["T_sumidero"] - fr["T_sumidero"]
            a, c = fr["eta_min_kalina"], ca["eta_min_kalina"]
            t = f'{ca["T_sumidero"]:g} → {fr["T_sumidero"]:g} K (ΔT = {dt:.3f} K)'
            ps.append(f"{t}: — (sin KALINA en un extremo)" if a is None or c is None else f"{t}: η {a - c:+.5f}")
        ck(f"- **{b}**: " + " · ".join(ps) in txt, f"reporte §5: pasos de {b}", "")
    for lin in _s8(res, kal):
        ck(lin in txt, f"reporte §8: {lin[:46]}…", "")
    fk = [k for k in kal if fuera(k)]
    if fk:
        esp = (f"- {len(fk)} de los {len(kal)} puntos KALINA quedan **fuera del rango confiable** "
               "(IAPWS G4-01): " + "; ".join(f'{k["base"]} {k["T_sumidero_val"]:g} K / {k["P_baja_val"]:g} kPa'
                                              for k in fk) + ".")
        ck(esp in txt, "reporte §9: lista de KALINA fuera de rango", esp[:80])
    g278 = [f for f in todo if f["T_sumidero_val"] == 278.15]
    mal = [f for f in g278 if not cor.genuina(f)]
    ck(f"- En el clima más frío (278.15 K) {len(mal)} de {len(g278)} puntos no son genuinos "
       "(N2 o no convergen): son los que quedan más cerca del límite del motor." in txt,
       "reporte §9: no genuinos en 278.15 K", f"{len(mal)} de {len(g278)}")
    m = re.search(r"Malla: (\d+) s · Bisección: (\d+) s · Total: (\d+) s", txt)
    ck(bool(m) and abs(int(m.group(3)) - int(m.group(1)) - int(m.group(2))) <= 1,
       "reporte §7: total == malla + bisección (±1 s por redondeo)", m.group(0) if m else "sin línea")
    raw = (OUT / "stdout.txt").read_bytes()
    e = re.search(r"fin: (\d+) malla \+ (\d+) biseccion en (\d+) s",
                  raw.decode("utf-16" if raw[:2] == b"\xff\xfe" else "utf-8", errors="replace"))
    ck(bool(m) and bool(e) and int(e.group(1)) == 200 and int(e.group(2)) == len(todo) - 200
       and 0 <= int(e.group(3)) - int(m.group(3)) < 600,
       "stdout: fin con 200 malla + bisección y total cercano al del reporte",
       f'stdout={e.group(0) if e else "?"} reporte={m.group(0) if m else "?"}')


def parte_d():
    """(d) la figura existe, pesa y trae contenido (no está en blanco)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    p = OUT / "m2s_pbaja_eta.png"
    if not ck(p.exists() and p.stat().st_size > 20000, "m2s_pbaja_eta.png existe y pesa > 20 kB",
              f"{p.stat().st_size if p.exists() else 'no existe'} bytes"):
        return
    img = plt.imread(p)
    ck(img.shape[0] >= 500 and img.shape[1] >= 1000 and float(img.std()) > 0.02,
       "m2s_pbaja_eta.png: dimensiones y contenido no nulos", f"shape={img.shape} std={float(img.std()):.4f}")


def main() -> int:
    malla, bise = leer("m2s_malla.csv"), leer("m2s_biseccion.csv")
    res, kal = leer("m2s_resumen.csv"), leer("m2s_kalina.csv")
    for parte in (lambda: parte_a(malla, bise, res, kal), lambda: parte_b(malla, bise, res, kal),
                  lambda: parte_c(res, kal, malla + bise), parte_d):
        parte()
    print(f"\n{len(FALLOS)} fallos" if FALLOS else "\nTODO OK")
    for f in FALLOS:
        print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())

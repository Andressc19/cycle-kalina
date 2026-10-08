"""M7 — verificación de la campaña M7 (TASK_CONTEXT final_M7 §Pasos 4).

Comprueba, SIN recalcular el ciclo: (1) que las trayectorias sean monótonas en
`(D, −η)`; (2) que las variables fijas de cada arranque no cambian y valen lo
del TASK_CONTEXT — transcripción independiente `FIJAS_SPEC` —; (3) que las
variables libres respeten los límites de la caja `CAJA_SPEC` (también
transcrita a mano) en TODAS las evaluaciones, quedando exentas las fijas (la
caja de T_fuente no aplica a A3/A5); y (4) que los números de
`REPORTE_M7.md` coincidan con los CSV, reconstruyendo con `m7_analisis` cada
línea desde los CSV. Además: ≤ 120 evaluaciones por arranque, ninguna fila con
`P_baja ≥ P_alta − 300`, aceptadas de evaluaciones == trayectorias y
`m7_optimos.csv` == último punto aceptado. Sale con 1 si algo falla.
"""
from __future__ import annotations

import contextlib, io, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m7_analisis as an  # noqa: E402

# Transcripción INDEPENDIENTE de TASK_CONTEXT final_M7 (§caja y §arranques).
CAJA_SPEC = {"T_fuente": (380.0, 500.0), "T_sumidero": (278.15, 303.55),
             "P_alta": (2000.0, 5000.0), "P_baja": (300.0, 2500.0),
             "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
             "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
             "eps_cond": (0.40, 0.95)}
FIJAS_SPEC = {"A1": {}, "A2": {},
              "A3": {"T_fuente": 623.15, "T_sumidero": 300.032917},
              "A4": {"P_alta": 3000.0, "P_baja": 400.0,
                     "T_sumidero": 300.032917},
              "A5": {"T_fuente": 623.15, "x_b": 0.50}}
CSV3 = ("m7_evaluaciones.csv", "m7_trayectorias.csv", "m7_optimos.csv")
PNG, REPORTE = "m7_convergencia.png", "REPORTE_M7.md"
DP_MIN, MAX_EVAL, TOL = 300.0, 120, 1e-9
FAL = 0


def chk(ok: bool, msg: str) -> None:
    """Imprime `OK`/`FALLO` y acumula los fallos para el código de salida."""
    global FAL
    FAL += 0 if ok else 1
    print(("OK    " if ok else "FALLO ") + msg, flush=True)


def _k(f: dict):
    """`(D, −η)` de la fila si está definido; `None` si falta alguno."""
    if f.get("D") is None or f.get("eta") is None:
        return None
    return (f["D"], -f["eta"])


def _transcripcion() -> None:
    """La caja y las fijas del verificador == las de `m7_optimizar`."""
    chk(CAJA_SPEC == an.CAJA,
        "la caja del verificador == la caja de m7_optimizar (cruzada)")
    chk({a: set(v) for a, v in FIJAS_SPEC.items()}
        == {a: set(v) for a, v in an.FIJAS.items()},
        "las variables fijas del verificador == las de m7_optimizar")


def _monotonia(tray: list) -> None:
    """Cada trayectoria es estrictamente decreciente en `(D, −η)`."""
    for a, filas in sorted(an.por_arranque(tray).items()):
        ks = list(map(_k, filas))
        hueco = [i for i, k in enumerate(ks) if k is None and i]
        peor = [(x, y) for x, y in zip(ks, ks[1:]) if x and y and not y < x]
        chk(not hueco and not peor,
            f"{a}: {len(filas)} puntos aceptados estrictamente monótonos en "
            f"(D, −η)"
            + (f" -> sube en {peor[0]}" if peor else "")
            + (f" -> sin D/η en fila {hueco}" if hueco else ""))


def _fijas_y_caja(ev: list) -> None:
    """Las fijas intactas en TODAS las filas; las libres, dentro de la caja."""
    mal_f, mal_c = [], []
    for f in ev:
        esp = FIJAS_SPEC.get(f["arranque"])
        if esp is None:
            mal_f.append(f'{f["arranque"]}: arranque fuera de spec')
            continue
        for v, x in esp.items():                     # (2) fijas intactas
            y = f.get(v)
            if y is None or abs(y - x) > TOL:
                mal_f.append(f'{f["arranque"]}:{f["iteracion"]}:{v}={y}')
        for v, (a, b) in CAJA_SPEC.items():          # (3) libres en la caja
            if v in esp:
                continue                             # fija: la caja no aplica
            y = f.get(v)
            if y is None or not a - TOL <= y <= b + TOL:
                mal_c.append(f'{f["arranque"]}:{f["iteracion"]}:{v}={y}')
    chk(not mal_f, f"{len(ev)} filas con las variables fijas intactas "
        f"(valores del TASK_CONTEXT)" + (f" -> {mal_f[:3]}" if mal_f else ""))
    chk(not mal_c, f"{len(ev)} filas con las libres dentro de la caja de M7"
        + (f" -> {mal_c[:3]}" if mal_c else ""))


def _conteos(ev: list, tray: list) -> None:
    """≤ 120 evaluaciones por arranque, sin dP < 300 y aceptadas == trayectoria."""
    mal = [f for f in ev if f.get("P_baja") is not None
           and f["P_baja"] >= f["P_alta"] - DP_MIN - TOL]
    chk(not mal, f"ninguna de las {len(ev)} evaluaciones viola "
        f"P_baja ≥ P_alta − 300" + (f" -> {len(mal)} filas" if mal else ""))
    n = {a: sum(1 for f in ev if f["arranque"] == a) for a in FIJAS_SPEC}
    chk(all(1 <= x <= MAX_EVAL for x in n.values()),
        f"cada arranque tiene 1–{MAX_EVAL} evaluaciones: {n}")
    acep = {(f["arranque"], int(f["iteracion"])) for f in ev
            if f["aceptado"] == "True"}
    ids = {(f["arranque"], int(f["iteracion"])) for f in tray}
    chk(acep == ids, f"las {len(ids)} filas aceptadas de m7_evaluaciones "
        f"== las de m7_trayectorias"
        + (f" -> solo eval {sorted(acep - ids)[:2]} "
           f"solo tray {sorted(ids - acep)[:2]}" if acep != ids else ""))


def _optimos(tray: list, ev: list, opts: list) -> None:
    """`m7_optimos.csv` == el último punto aceptado de cada trayectoria."""
    mal, grp = [], an.por_arranque(tray)
    if set(grp) != {f["arranque"] for f in opts}:
        mal.append(f"arranques {sorted(grp)} != {sorted(f['arranque'] for f in opts)}")
    for a, filas in grp.items():
        o = next((x for x in opts if x["arranque"] == a), None)
        if o is None:
            continue
        u = filas[-1]
        for v in ("eta", "Wnet", "D", "m_O1", "m_O2", "m_O5", *CAJA_SPEC):
            x, y = o.get(v), u.get(v)
            if (x is None) != (y is None) or (x is not None and abs(x - y) > TOL):
                mal.append(f"{a}:{v} {x} != {y}")
        n = sum(1 for f in ev if f["arranque"] == a)
        it = max(int(f["iteracion"]) for f in filas)
        if int(float(o["iteraciones"])) != it or int(o["evaluaciones"]) != n:
            mal.append(f"{a}: it/ev {o['iteraciones']}/{o['evaluaciones']} "
                       f"!= {it}/{n}")
    chk(not mal, "m7_optimos.csv == el último punto aceptado de cada "
        "trayectoria, con sus conteos" + (f" -> {mal[:3]}" if mal else ""))


def _reporte(opts: list, ini: dict, ev: list) -> None:
    """(4) Cada línea que `m7_analisis` recalcula desde los CSV está en el reporte."""
    p = an.OUT / REPORTE
    if not p.exists():
        chk(False, f"existe {REPORTE}")
        return
    txt = p.read_text(encoding="utf-8", errors="replace")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        an.resumen(opts, ini, ev)
    lin = [l for l in buf.getvalue().splitlines() if l.strip()]
    mal = [l for l in lin if l not in txt]
    chk(not mal, f"las {len(lin)} líneas con cifras recalculadas desde los CSV "
        f"están en {REPORTE}" + (f" -> {mal[:2]}" if mal else ""))


def main() -> None:
    print(f"m7_verificar | OUT={an.OUT}", flush=True)
    faltan = [n for n in CSV3 if not (an.OUT / n).exists()]
    chk(not faltan, f"están los 3 CSV de salida (faltan: {faltan})")
    if faltan:
        print(f"FIN: {FAL} fallo(s)", flush=True)
        sys.exit(1)
    chk((an.OUT / PNG).exists(), f"existe {PNG}")
    _transcripcion()
    tray, ev = an.leer("m7_trayectorias.csv"), an.leer("m7_evaluaciones.csv")
    chk(bool(tray) and bool(ev),
        f"hay filas: {len(tray)} aceptadas y {len(ev)} evaluaciones")
    if not tray or not ev:
        print(f"FIN: {FAL} fallo(s)", flush=True)
        sys.exit(1)
    _monotonia(tray)
    _fijas_y_caja(ev)
    _conteos(ev, tray)
    opts = an.leer("m7_optimos.csv")
    chk(bool(opts), f"m7_optimos.csv tiene {len(opts)} filas (1 por arranque)")
    _optimos(tray, ev, opts)
    grp = an.por_arranque(tray)
    _reporte(opts, {a: f[0] for a, f in grp.items()}, ev)
    print(f"FIN: {FAL} fallo(s)", flush=True)
    sys.exit(1 if FAL else 0)


if __name__ == "__main__":
    main()

"""Comprobacion exacta y barata del criterio O5 ("la salida del HRVG cae fuera de la campana
binaria") en las filas NO_CONVERGIO con el mensaje de flash, SIN correr el solver del ciclo y
SIN invertir T con `T_from_Ph`. El HRVG cumple h2 = (1-eps)*h1 + eps*h2max (h1 = h(P_alta,T1,x),
h2max = h(P_alta,T_fuente,x), T1 >= T_sumidero, eps <= 1), luego h2_min = (1-eps_lo)*
h(P_alta,T_sumidero,x) + eps_lo*h2max <= h2 <= h2max; y h_rocio <= h <= h_burbuja es la
condicion de dos fases a (P_alta,x): h2_min >= h_rocio -> SOBRECALENTADA_DEMOSTRADA, h2max <
h_burbuja -> LIQUIDA_DEMOSTRADA, ninguna -> DENTRO_DE_CAMPANA_POSIBLE, motor sin cobertura ->
NO_EVALUABLE. Solo `h`, `bubble_point` y `dew_point` de AmmoniaWaterAdapter. Detalle y cifras
en REPORTE_COMPROBACION_O5.md."""
from __future__ import annotations

import csv
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.properties.adapter import PropertyRangeError                # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402

RES, OUT = ROOT / "resultados", ROOT / "resultados" / "2026-10-01_comprobacion_o5"
CSV_UNIV, CSV_CTRL, LOG = (OUT / "comprobacion_o5_filas.csv", OUT / "comprobacion_o5_control.csv", OUT / "progreso.log")
FRASE, COLS_MSG = "no existe equilibrio bifásico", ("mensaje", "detalle_error", "excepcion_original", "msg", "error")
EPS_SUPUESTA = 0.75  # banda de diseño del proyecto 0.75-0.85 (TASK_CONTEXT)
CAMPOS = ("P_alta", "x_b", "T_fuente", "T_sumidero")
COLS = ("clave", "csv_origen", "P_alta", "x_b", "T_fuente", "T_sumidero", "eps_hrvg",
        "eps_lo", "eps_supuesta", "h1_min", "h2max", "h2_min", "h_rocio", "h_burbuja",
        "T_rocio", "T_burbuja", "margen_sobrecalentada", "veredicto", "error")
# CSV -> script que lo generó: única fuente para los parámetros que el CSV no trae.
SCRIPT_DE = {"barridos_2026-09-19/b0_scan_cementera.csv": "scripts/barridos_2026-09-19/b0_scan_cementera.py",
             "2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv": "scripts/barrido_literatura_kcs11.py",
             "2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv": "scripts/exploracion_tfuente_bajo.py",
             "2026-09-23_pinch6_realista/barrido_pinch6_realista.csv": "scripts/barrido_pinch6_realista.py"}
MALAS = ("SOBRECALENTADA", "LIQUIDA")  # prefijos que NO pueden salir en una fila de control
_A = AmmoniaWaterAdapter()             # bubble_point/dew_point llevan x explícito


def _log(msg: str) -> None:            # una linea de progreso: el unico .log de la corrida
    LOG.open("a", encoding="utf-8").write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def _num(v):    # float finito, o None si la celda está vacía o no es numérica
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return f if f == f and abs(f) != float("inf") else None


def _const_de_script(rel: str, nombre: str, salto: int = 0):
    """Constante de nivel de módulo del script generador del CSV; si el script hace
    `from modulo import CONST` se resuelve un salto más en ese módulo (los generadores
    importan T_SUMIDERO de `calibracion_elsayed_malla`); None si no se reconstruye."""
    if not rel or not (ROOT / rel).exists(): return None
    src = re.sub(r"#[^\n]*", "", (ROOT / rel).read_text(encoding="utf-8"))
    m = re.search(rf"^{nombre}\s*=\s*(-?[\d.]+(?:[eE][-+]?\d+)?)\s*$", src, re.M)
    if m:
        return float(m.group(1))
    if salto < 2:
        for mod, nombres in re.findall(r"^from\s+(\w+)\s+import\s*(\([^)]*\)|[^\n(]*)",
                                       src, re.M | re.S):
            if re.search(rf"\b{nombre}\b", nombres):
                return _const_de_script(f"scripts/{mod}.py", nombre, salto + 1)
    return None


def _param(rel: str, fila: dict, campo: str):
    """Columna del CSV si la trae; si no, la constante homónima del script que lo generó."""
    v = _num(fila.get(campo))
    return v if v is not None else _const_de_script(SCRIPT_DE.get(rel, ""), campo.upper())


def _clave(d: dict) -> str:
    return "|".join(f"{d[c]:.6g}" for c in CAMPOS + ("eps_lo",))

def recolectar(modo: str) -> list:
    """Universo (NO_CONVERGIO con la frase del flash) o control (KALINA/CORREGIBLE), deduplicado."""
    datos: dict = {}
    sueltas: list = []
    for p in sorted(RES.rglob("*.csv")):
        if "_tmp" in p.parts or OUT in p.parents: continue
        rel = p.relative_to(RES).as_posix()
        with p.open(encoding="utf-8-sig", newline="") as fh:
            crudos = list(csv.DictReader(fh))
        if not crudos or "clasificacion" not in crudos[0]: continue
        for n, r in enumerate(crudos, start=2):
            cls = (r.get("clasificacion") or "").strip()
            ok = (cls == "NO_CONVERGIO" and FRASE in " ".join(
                r.get(c) or "" for c in COLS_MSG)) if modo == "universo" else \
                cls in ("KALINA", "CORREGIBLE")
            if not ok: continue
            d = {c: _param(rel, r, c) for c in CAMPOS}
            eps, falta = _num(r.get("eps_hrvg")), [c for c, v in d.items() if v is None]
            if falta or (modo != "universo" and eps is None):
                if modo == "universo":   # se registra y se sigue; no se inventa
                    sueltas.append(dict(clave=f"nopar|{rel}|{n}", csv_origen=rel, eps_lo=eps,
                                        veredicto="PARAMETROS_NO_RECONSTRUIBLES",
                                        error=f"sin {', '.join(falta) or 'eps_hrvg'}", **d))
                continue
            d.update(clave="", csv_origen=rel, eps_hrvg=eps, _cls=cls,
                     eps_supuesta=eps is None, eps_lo=EPS_SUPUESTA if eps is None else eps)
            k = _clave(d)
            if modo == "universo" and k in datos:
                datos[k]["csv_origen"] += f";{rel}"
                continue
            d["clave"] = k if modo == "universo" else f"{k}|{rel}|{n}"
            datos[d["clave"]] = d
    if modo == "universo":
        return sorted(list(datos.values()) + sueltas,
                      key=lambda d: ((d["P_alta"] or 0.0), (d["x_b"] or 0.0)))
    salida = []
    for cls in ("KALINA", "CORREGIBLE"):
        pool = sorted((d for d in datos.values() if d["_cls"] == cls),
                      key=lambda d: (d["csv_origen"], d["P_alta"], d["x_b"]))
        salida += [pool[round(i * (len(pool) - 1) / 24)] for i in range(25)]
        _log(f"[control] pool {cls}={len(pool)} -> 25 filas con paso uniforme")
    return salida


_C: dict = {}          # caches del worker: viven en el proceso hijo

def _h(P, T, x):
    k = ("h", round(P, 6), round(T, 6), round(x, 9))
    if k not in _C:
        _C[k] = _A.h(P, T, x)
    return _C[k]

def _sat(P, x):    # (T_burbuja, T_rocio, h_burbuja, h_rocio), cacheado por (P_alta, x_b)
    k = ("sat", round(P, 6), round(x, 9))
    if k not in _C:
        Tb, Tr = _A.bubble_point(P, x), _A.dew_point(P, x)
        _C[k] = (Tb, Tr, _h(P, Tb, x), _h(P, Tr, x))
    return _C[k]

def evaluar(fila: dict) -> dict:
    """Veredicto O5 de una fila. Nunca lanza: el fallo real del motor va a `error`."""
    d, P, x, e = dict(fila), fila["P_alta"], fila["x_b"], fila["eps_lo"]
    try:
        h2max = _h(P, d["T_fuente"], x)
        Tb, Tr, h_bur, h_rocio = _sat(P, x)
        h1_min = _h(P, d["T_sumidero"], x)
    except (PropertyRangeError, ValueError, RuntimeError, ArithmeticError) as exc:
        d.update(veredicto="NO_EVALUABLE", error=f"{type(exc).__name__}: {exc}")
        return d
    h2_min = (1.0 - e) * h1_min + e * h2max
    d.update(h1_min=h1_min, h2max=h2max, h2_min=h2_min, h_burbuja=h_bur, h_rocio=h_rocio,
             T_burbuja=Tb, T_rocio=Tr, error="", margen_sobrecalentada=h2_min - h_rocio,
             veredicto="SOBRECALENTADA_DEMOSTRADA" if h2_min >= h_rocio else
             "LIQUIDA_DEMOSTRADA" if h2max < h_bur else "DENTRO_DE_CAMPANA_POSIBLE")
    return d

def correr(filas: list, destino: Path, etiqueta: str) -> None:
    """Prueba en 6 workers, una fila por combinación terminada (con flush); reanudable."""
    hecho = set()
    if destino.exists():
        with destino.open(encoding="utf-8-sig", newline="") as fh:
            hecho = {r["clave"] for r in csv.DictReader(fh)}
    pend = [d for d in filas if d["clave"] not in hecho]
    _log(f"[{etiqueta}] {destino.name}: {len(filas)} filas, ya_hechas={len(hecho)}, "
         f"pendientes={len(pend)}")
    if not pend: return
    t0 = time.perf_counter()
    with destino.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, restval="", extrasaction="ignore")
        w.writeheader() if destino.stat().st_size == 0 else None
        with ProcessPoolExecutor(max_workers=6) as pool:
            for i, d in enumerate(pool.map(evaluar, pend, chunksize=1), start=1):
                w.writerow(d)
                fh.flush()
                if i % 10 == 0 or i == len(pend):
                    _log(f"[{etiqueta}] {i}/{len(pend)} t={time.perf_counter()-t0:.0f}s "
                         f"ultimo={d['veredicto']} err={d['error'][:70]}")
    _log(f"[{etiqueta}] terminada en {time.perf_counter()-t0:.0f}s")
def main(argv: list) -> int:
    """--humo: 6 filas dentro de un worker real. Sin argumento: control y luego universo."""
    OUT.mkdir(parents=True, exist_ok=True)
    _log(f"=== inicio {time.strftime('%Y-%m-%d %H:%M:%S')} argv={' '.join(argv)}")
    if "--humo" in argv:
        with ProcessPoolExecutor(max_workers=1) as pool:
            for d in pool.map(evaluar, recolectar("universo")[:6]):
                _log("HUMO " + " ".join(f"{k}={d.get(k)}" for k in COLS if k != "error"))
        return 0
    correr(recolectar("control"), CSV_CTRL, "control")
    with CSV_CTRL.open(encoding="utf-8-sig", newline="") as fh:
        malas = [d for d in csv.DictReader(fh) if d["veredicto"].startswith(MALAS)]
    _log(f"[control] {len(malas)} falsas 'demostradas' entre las filas escritas (criterio: 0)")
    if malas:
        for d in malas[:5]:
            _log(f"[control] FALLA {d['clave']} -> {d['veredicto']}")
        _log("[control] se detiene el resto: logica o parametros mal")
        return 2
    correr(recolectar("universo"), CSV_UNIV, "universo")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
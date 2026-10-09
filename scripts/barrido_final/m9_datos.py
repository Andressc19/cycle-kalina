"""M9 — caja, grupos del profesor y utilidades compartidas (TASK_CONTEXT final_M9).

Caja, grupos, LHS, tipado, "genuino"/"KALINA confiable" y reanudación compartidas.
"""
from __future__ import annotations

import csv, os, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from scipy.stats import qmc  # noqa: E402

from comun import COLS, PROFESOR  # noqa: E402

HUMO = os.environ.get("M9_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-08_final_M9/humo" if HUMO
                              else "2026-10-08_final_M9")
# Caja de las variables libres (TASK_CONTEXT final_M9 §caja).
CAJA = {"T_fuente": (380.0, 520.0), "T_sumidero": (278.15, 303.55),
        "P_alta": (2000.0, 5000.0), "P_baja": (300.0, 2000.0),
        "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
        "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
        "eps_cond": (0.40, 0.95)}
VARS10 = tuple(CAJA)
GRUPOS = {"TF": ("T_fuente",),
          "EF": ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"),
          "PA": ("P_alta",), "PB": ("P_baja",), "TS": ("T_sumidero",),
          "XB": ("x_b",)}
DP_MIN = 300.0                      # P_baja >= P_alta - 300 -> no se evalúa
MOTIVO = "P_baja demasiado cerca de P_alta"
GENU = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
CFLOT = ("eta", "Wnet", "D", "m_O1", "m_O2", "m_O3", "m_O5", "q4", "q2",
         "T9_amb", "T_bub", "T_amb_diseno", "t_s", *VARS10)
CBOOL = ("convergio", "fuera_rango", "B_verificado")


def num(s):
    """Cadena a `float`; vacío o inconvertible -> `None`."""
    if s in (None, ""):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def tipar(rows: list) -> list:
    """Tipa números y booleanos (incl. extras de M9) y añade dP/rP a cada fila."""
    for f in rows:
        for k in CFLOT + ("D_min", "piso_tamb", "P_baja_test", "min", "p05",
                          "mediana", "p95", "max", "ks_estadistico", "ks_p",
                          "eta_teqp", "eta_real", "d_eta_pp"):
            if k in f:
                f[k] = num(f.get(k))
        for k in ("ronda", "n_conservadas", "n_eval", "n_genuinos", "n_kalina",
                  "n_kalina_confiable", "n"):
            if k in f:
                v = num(f.get(k))
                f[k] = None if v is None else int(v)
        for k in CBOOL + ("omitido", "elegido", "kalina_por_busqueda", "coincide_clase"):
            if k in f:
                v = f.get(k)
                f[k] = None if v in (None, "") else v == "True"
        f["clasificacion"] = f.get("clasificacion") or None
        if f.get("P_alta") is not None and f.get("P_baja") is not None:
            f["dP"] = f["P_alta"] - f["P_baja"]
            f["rP"] = f["P_alta"] / f["P_baja"]
    return rows


def leer(path) -> list:
    """Filas tipadas de un CSV del M9."""
    with open(path, encoding="utf-8", newline="") as fh:
        return tipar(list(csv.DictReader(fh)))


def genu(f: dict) -> bool:
    """Punto genuino: KALINA, CORREGIBLE o INVIABLE (N2 no cuenta)."""
    return f.get("clasificacion") in GENU


def es_kalina(f: dict) -> bool:
    return f.get("clasificacion") == "KALINA"


def confiable(f: dict) -> bool:
    """KALINA, fuera_rango == False y B_verificado == True."""
    return (es_kalina(f) and f.get("fuera_rango") is False
            and f.get("B_verificado") is True)


def libres(codes: list) -> list:
    """Variables libres del conjunto `codes` (grupos conservados del profesor)."""
    fijas = {v for c in codes for v in GRUPOS[c]}
    return [v for v in VARS10 if v not in fijas]


def n_conservadas(codes: list) -> int:
    return sum(len(GRUPOS[c]) for c in codes)


def muestra(codes: list, n: int, seed: int) -> list:
    """LHS de `n` puntos: grupos conservados fijos, el resto en la caja."""
    lib = libres(codes)
    lo = [CAJA[v][0] for v in lib]
    hi = [CAJA[v][1] for v in lib]
    X = qmc.scale(qmc.LatinHypercube(d=len(lib), seed=seed).random(n), lo, hi)
    out = []
    for i in range(n):
        p = dict(PROFESOR)
        p.update({v: float(X[i][j]) for j, v in enumerate(lib)})
        out.append(p)
    return out


def omitido(combo: dict, *, tag: str, motivo: str = MOTIVO) -> dict:
    """Fila `omitido=True` sin evaluar (sus variables sí se escriben)."""
    f = dict.fromkeys(COLS)
    f.update(combo)
    f.update(tag=tag, mensaje=motivo, omitido=True)
    return f


def criterio_mas_roto(filas: list):
    """`(código, n)` más frecuente entre los genuinos NO KALINA de `filas`."""
    cuenta: dict = {}
    for f in filas:
        if not genu(f) or es_kalina(f):
            continue
        cods = [c for c in (f.get("codigos_falla") or "").split(",") if c]
        for c in cods or ["(sin codigos)"]:
            cuenta[c] = cuenta.get(c, 0) + 1
    if not cuenta:
        return None, 0
    c = max(cuenta, key=lambda k: (cuenta[k], k))
    return c, cuenta[c]


def resumen(filas: list) -> dict:
    """Conteos de genuinos, KALINA y KALINA confiables de `filas`."""
    return dict(n_genuinos=sum(1 for f in filas if genu(f)),
                n_kalina=sum(1 for f in filas if es_kalina(f)),
                n_conf=sum(1 for f in filas if confiable(f)))


def clave_ranking(filas: list):
    """Clave de ranking del TASK_CONTEXT §Paso 2.1 (menor es mejor)."""
    r = resumen(filas)
    ds = [f["D"] for f in filas if genu(f) and f.get("D") is not None]
    dmin = min(ds) if ds else None
    return (-r["n_conf"], -r["n_kalina"], dmin if dmin is not None else 1e18)


def marca_inicio() -> None:
    """Escribe `m9_tiempos.csv` con la marca de inicio si aún no existe."""
    import time
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "m9_tiempos.csv"
    if p.exists():
        return
    p.write_text("momento,marca\ninicio,%.6f\n" % time.time(), encoding="utf-8")


def n_filas(path) -> int:
    """Filas de datos (sin cabecera) del CSV, o 0 si no existe."""
    if not Path(path).exists():
        return 0
    with open(path, encoding="utf-8", newline="") as fh:
        return max(0, sum(1 for _ in fh) - 1)


def reanudar(path, cols: list, clave):
    """Abre `path` para append (con cabecera si es nuevo) -> `(fh, escritor, vistas)`.

    `vistas` son las claves ya presentes: no hay que volver a correr esas filas.
    """
    p = Path(path)
    existe = p.exists()
    vistas = {clave(f) for f in leer(p)} if existe else set()
    fh = open(p, "a" if existe else "w", encoding="utf-8", newline="")
    esc = csv.DictWriter(fh, fieldnames=cols)
    if not existe:
        esc.writeheader()
        fh.flush()
    return fh, esc, vistas


def leer_inicio():
    """Epoch del inicio del paso 0, o `None` si no existe el archivo."""
    p = OUT / "m9_tiempos.csv"
    if not p.exists():
        return None
    for r in csv.DictReader(open(p, encoding="utf-8", newline="")):
        if r.get("momento") == "inicio":
            return float(r["marca"])
    return None

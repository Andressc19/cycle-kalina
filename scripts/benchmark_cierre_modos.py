"""Modos y carga deitems del CIERRE del benchmark (tarea
`2026-10-01-benchmark-cierre-topes`).

NO modifica `src/`, `tests/`, ni los scripts/CSV existentes: IMPORTA
`scripts/benchmark_modos.py` (M0/MA/MB, instrumentación, verificación B) y
`sonda_arranque_solver.py` (`muestra()`, `_kw_f2/_kw_lt`, `NoBracket`,
`EPS_PARTIDA`, `LIT`) y los usa tal cual. Añade solo:

  * un bracket SIN tope de intentos —copia fiel de `P._bracket_tol`, que es el V2
    de la ablación, más la salida temprana ST opcional—, porque
    `benchmark_modos._bracket_tope` SÍ lleva tope (`max_rep`) y por eso `tope 6`
    NO es V2 (con tope 6 MB rescata 11 de las 40 filas; V2, 28);
  * la lectura de las 40 filas de la Parte A y de los 93 puntos del mini-barrido
    desde los CSV de la corrida anterior, sin recalcular nada.

Los dos parches (`cfg_nombre`, `_bracket_tope`) se aplican DENTRO de `medir`, o
sea en cada proceso worker: con `spawn` (Windows) el hijo importa este módulo
pero no hereda los parches de otro proceso.

El orquestador es `benchmark_cierre_topes.py`.
"""
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                    # noqa: E402
import benchmark_modos as BM                                          # noqa: E402
import sonda_arranque_solver as P                                      # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-01_benchmark_reintento"
CSV_A = OUT / "benchmark_filas.csv"
CSV_TOPES = OUT / "benchmark_filas_topes.csv"
CSV_MINI = OUT / "benchmark_minibarrido.csv"
CSV_MINI_MB = OUT / "benchmark_minibarrido_mb_corregido.csv"
CSV_ABL = _RAIZ / "resultados" / "2026-10-01_ablacion_tiempos" / "ablacion_filas.csv"
#: las 4 configuraciones nuevas de la Parte A2. `None` = sin tope de intentos.
CFGS_NUEVAS = [("MB", 10, False), ("MB", 15, False), ("MB", None, False), ("MB", None, True)]
COLS_CSV = P.COLS_PARAM                      # los 11 parámetros, nombres del CSV
TOPE_DE = {"MB_t2_STno": 2, "MB_t3_STno": 3, "MB_t6_STno": 6, "MB_t10_STno": 10,
           "MB_t15_STno": 15, "MB_sintope_STno": 10**6}
_BRACKET_TOPE = BM._bracket_tope             # referencias ANTES de los parches:
_CFG_NOMBRE_ORIG = BM.cfg_nombre             # `medir` reescribe `BM.cfg_nombre`,
                                             # así que `cfg_nombre` DEBE llamar a la
                                             # original (si llamara a `BM.cfg_nombre`
                                             # se llamaría a sí misma -> RecursionError).


def cfg_nombre(cfg):
    """Nombre de columna; `tope=None` -> 'MB_sintope_STno|STsi'."""
    if isinstance(cfg, tuple) and cfg[1] is None:
        return f"MB_sintope_ST{'si' if cfg[2] else 'no'}"
    return _CFG_NOMBRE_ORIG(cfg)


def _bracket_sin_tope(F, Ts, Tf, paso=BM.PASO, st=False):
    """Copia fiel de `P._bracket_tol` (V2): repliega cada extremo `paso` K al
    interior HASTA agotar el rango físico, y exige cambio de signo. `st` añade la
    MISMA salida temprana de `BM._bracket_tope`: si el primer intento del extremo
    alto y el último del bajo fallan ambos con 'no existe equilibrio bifásico', se
    rinde sin replegar (no amplía la regla de ST de la Parte A).
    `F(T) -> (valor_o_None, PropertyRangeError_o_None)`."""
    lo, hi = Ts + 1.0, Tf - 1.0
    if not lo < hi:
        raise P.NoBracket("rango físico de T1 degenerado")
    f_lo, e_lo = F(lo)
    while f_lo is None and lo + paso < hi:
        lo, f_lo, e_lo = (lo + paso, *F(lo + paso))
    f_hi, e_hi = F(hi)
    if st and f_lo is None and BM._bifasico(e_hi) and BM._bifasico(e_lo):
        raise P.NoBracket("ST: los dos extremos fallan sin equilibrio bifásico "
                          f"(hi@{hi:.1f} K)")
    while f_hi is None and hi - paso > lo:
        hi, f_hi, e_hi = (hi - paso, *F(hi - paso))
    if f_lo is None or f_hi is None:
        raise P.NoBracket(f"sin dos extremos evaluables en {paso} K "
                          f"(f_lo={f_lo}, f_hi={f_hi})")
    if f_lo * f_hi > 0.0:
        raise P.NoBracket(f"extremos [{lo:.1f}, {hi:.1f}] K sin cambio de signo "
                          f"(f_lo={f_lo:.5g}, f_hi={f_hi:.5g})")
    return lo, hi


def _dispatch(F, Ts, Tf, max_rep, paso=BM.PASO, st=False):
    """Sin tope -> `_bracket_sin_tope`; con tope -> el MISMO bracket ya medido en la
    Parte A (t2/t3/t6/t10/t15 salen todos del mismo código)."""
    return (_bracket_sin_tope(F, Ts, Tf, paso, st) if max_rep is None
            else _BRACKET_TOPE(F, Ts, Tf, max_rep, paso, st))


def medir(tarea):
    """`BM.medir` (misma instrumentación y verificación B) con los parches puestos
    en este proceso."""
    BM.cfg_nombre, BM._bracket_tope = cfg_nombre, _dispatch
    return BM.medir(tarea)


def _kw_de_csv(r):
    """`kw` desde las columnas de un CSV del benchmark: los 11 parámetros +
    tolerancias; en el CSV de literatura, `eps` vacíos -> los de partida."""
    eh, er, ec = float(r.eps_hrvg), float(r.eps_reg), float(r.eps_cond)
    if eh != eh:
        eh, er, ec = P.EPS_PARTIDA
    kw = {c: float(r[c]) for c in COLS_CSV}
    kw.update(dict(tol_T10=float(r.tol_T10), max_iter_frio=int(r.max_iter_frio)))
    if str(r.get("csv_origen", "")).startswith("barrido_literatura"):
        kw.update(P.LIT)
    return kw


def control_kw(items, ref, etiqueta, log):
    """Coherencia: el `kw` que se va a medir debe ser IDÉNTICO al de la corrida
    anterior (columnas del CSV), y `x_backend` también. Aborta si no."""
    ref = {(r.csv_origen, int(r.fila_csv)): r for r in ref.itertuples()}
    for i in items:
        k, r = (i["csv_origen"], i["fila_csv"]), ref[(i["csv_origen"], i["fila_csv"])]
        for c in COLS_CSV + ("tol_T10", "max_iter_frio"):
            if abs(float(i["kw"][c]) - float(getattr(r, c))) > 1e-9:
                raise SystemExit(f"[{etiqueta}] kw no coincide en {k} col={c}: "
                                 f"{i['kw'][c]} != {getattr(r, c)}")
        if abs(float(i["x_backend"]) - float(r.x_backend)) > 1e-12:
            raise SystemExit(f"[{etiqueta}] x_backend no coincide en {k}")
    log(f"{etiqueta}: control OK — kw y x_backend identicos al CSV previo en "
        f"{len(items)} filas ({len(COLS_CSV) + 3} columnas cada una)")


def items_a1():
    """Las 40 filas que M0 no resuelve, con el `kw` de `P.muestra()` (misma
    fuente que la corrida anterior)."""
    a = pd.read_csv(CSV_A)
    claves = {(r.csv_origen, int(r.fila_csv)) for r in a[a.etapa == "A1"].itertuples()}
    idx = {(i["csv_origen"], i["fila_csv"]): i for i in P.muestra()}
    faltan = claves - set(idx)
    if faltan:
        raise SystemExit(f"muestra() ya no reconstruye {len(faltan)} filas de la Parte A")
    return [idx[k] for k in sorted(claves)], a


def items_mini():
    """Los 93 puntos del mini-barrido: `kw` de `P.muestra()` para las filas que M0
    no resuelve y reconstruido desde el CSV para las sanas."""
    b = pd.read_csv(CSV_MINI)
    base = b[b.etapa == "M0"].set_index(["csv_origen", "fila_csv"])
    idx = {(i["csv_origen"], i["fila_csv"]): i for i in P.muestra()}
    out = [idx[k] if k in idx else
           dict(csv_origen=k[0], fila_csv=k[1], grupo=r.grupo, kw=_kw_de_csv(r),
                x_backend=float(r.x_backend), clasif=r.clasificacion_original,
                eta_orig=float(r.eta_original), exc_orig="")
           for k, r in base.iterrows()]
    return out, b
"""Sonda de diagnóstico: ¿el arranque del solver produce falsos NO_CONVERGIO?

Tarea `2026-09-30-arranque-solver-falsos-negativos`: no modifica `src/`, `tests/`
ni CSV existentes; escribe solo `resultados/2026-09-30_arranque_solver/`. Por fila
(backend `TeqpVerificado`): **V0** = réplica de `resolver_ciclo` (arranque en frío
`T10_inicial=None` y bracket original); **V1** = V0 con `T10_inicial = T_sumidero +
5 K` sin warm start (conserva `ultimo_T10`); **V2** = V1 con `F_seguro`
(`PropertyRangeError` -> None) y bracket replegado 5 K al interior hasta dos
extremos evaluables con cambio de signo (punto interior no evaluable ->
`PuntoNoEvaluable`: brentq no admite None). `Proxy` graba cada petición antes de
delegar y `PRE`/`COLD` decodifican la que falla sin tocar `src/`.
"""
import sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
from scipy.optimize import brentq                                       # noqa: E402
from src._cycle_loops import CicloNoConvergeError, _bracketear, evaluar  # noqa: E402
from src.properties.adapter import PropertyRangeError                   # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter    # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado               # noqa: E402
from src.restricciones import evaluar_ciclo                             # noqa: E402
from src.verificacion_motor_real import verificar_turbina               # noqa: E402

OUT_DIR = _RAIZ / "resultados" / "2026-09-30_arranque_solver"
CSV_OUT = OUT_DIR / "sonda_filas.csv"
T_AMB, N_WORKERS = 303.55, 6  # piso O2: fase2_libre lo pasa; literatura usa el default
TOL = dict(tol_T10=1e-3, max_iter_frio=300)   # defaults de `resolver_ciclo`
LIT = dict(T_sumidero=283.0, eta_t=0.80, eta_p=0.80, m_b=1.0)  # calibracion_elsayed_malla
EPS_PARTIDA = (0.85, 0.75, 0.80)                                # calibracion_elsayed_malla
COLS_PARAM = ("x_b", "P_alta", "P_baja", "T_fuente", "T_sumidero", "m_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
PRE = ("e1.h", "e1.s", "hrvg.h2max", "hrvg.T2", "hrvg.s2", "sep.ELV", "sep.e3.h", "sep.e3.s", "sep.e5.h", "sep.e5.s", "turb.h4s", "turb.T4", "turb.s4")
COLD = ("reg.h_fria", "reg.s_fria", "reg.h6_min", "reg.T6", "reg.s6", "valv.T7", "valv.s7", "abs.T8", "abs.s8", "cond.h9_min", "cond.T9", "cond.s9", "bom.h10s", "bom.T10", "bom.s10")
_MOTOR_REAL = AmmoniaWaterAdapter(x=0.5)   # con spawn: una instancia por worker

class NoBracket(Exception): ...       # V2: sin dos extremos evaluables
class PuntoNoEvaluable(Exception): ...  # V2: punto interior de brentq no evaluable
def _msg(exc) -> str:
    return f"{type(exc).__name__}: {exc}"[:240]

def decodificar(n: int, tipo: str) -> tuple[str, int]:   # (componente, iteración base 1)
    if n < len(PRE):
        return PRE[n], 0
    r, k = n - len(PRE), len(COLD)
    return ("cierre_T1_nuevo", r // k) if r and not r % k and tipo == "T_from_Ph" else (COLD[r % k], r // k + 1)

class Proxy:
    """Graba el orden de las peticiones de propiedades: etiqueta ANTES de delegar,
    así la llamada que lanza excepción queda en `calls` (índice `len(calls) - 1`).
    `bubble_point`, `dew_point` y `fase_de` (solo de `restricciones`) van por
    `__getattr__` sin registrarse."""
    def __init__(self, real):
        self._real, self.calls = real, []
    def _p(self, etiq, metodo, *a, **kw):
        self.calls.append(etiq)
        return getattr(self._real, metodo)(*a, **kw)
    def h(self, P, T=None, x=None, s=None, quality=None):
        return self._p("h(P,s,x)" if s is not None else "h(P,T,x)", "h", P, T=T, x=x, s=s, quality=quality)
    def s(self, P, T=None, x=None):
        return self._p("s(P,T,x)", "s", P, T=T, x=x)
    def T_from_Ph(self, P, h, x=None):
        return self._p("T_from_Ph", "T_from_Ph", P, h, x=x)
    def T_from_Ps(self, P, s, x=None):
        return self._p("T_from_Ps", "T_from_Ps", P, s, x=x)
    def equilibrio_liquido_vapor(self, P, T):
        return self._p("ELV", "equilibrio_liquido_vapor", P, T)
    def __getattr__(self, name):
        return getattr(self.__dict__["_real"], name)

def _bracket_tol(F, Ts, Tf, paso=5.0):   # V2: repliega cada extremo `paso` K al interior
    lo, hi = Ts + 1.0, Tf - 1.0
    if not lo < hi:
        raise NoBracket("rango físico de T1 degenerado")
    f_lo = F(lo)
    while f_lo is None and lo + paso < hi:
        lo, f_lo = lo + paso, F(lo + paso)
    f_hi = F(hi)
    while f_hi is None and hi - paso > lo:
        hi, f_hi = hi - paso, F(hi - paso)
    if f_lo is None or f_hi is None:
        raise NoBracket(f"sin dos extremos evaluables en {paso} K (f_lo={f_lo}, f_hi={f_hi})")
    if f_lo * f_hi > 0.0:
        raise NoBracket(f"extremos [{lo:.1f}, {hi:.1f}] K sin cambio de signo (f_lo={f_lo:.5g}, f_hi={f_hi:.5g})")
    return lo, hi

def orquestar(px, kw, variante, tr) -> dict:   # `resolver_ciclo` con la variante pedida
    ultimo, nF, Ts, Tf = None, [0], kw["T_sumidero"], kw["T_fuente"]
    def F(T1, fase=None, full=False):
        nonlocal ultimo
        nF[0] += 1
        px.calls.clear()
        T10_ini = ultimo if ultimo is not None or variante == "V0" else Ts + 5.0
        try:
            nuevo, est, ener = evaluar(T1, px, **kw, T10_inicial=T10_ini)
        except PropertyRangeError as exc:
            comp, it = decodificar(len(px.calls) - 1, px.calls[-1] if px.calls else "")
            # `_bracketear` solo amplía hacia fuera: extremo si T1 <= Ts+1 o >= Tf-1
            donde = fase or ("extremo_lo" if T1 <= Ts + 1.0 + 1e-9 else
                             "extremo_hi" if T1 >= Tf - 1.0 - 1e-9 else "interior_brentq")
            tr.append(dict(donde=donde, T1_trial=round(T1, 4), nF=nF[0], comp=comp, iter_frio=it, msg=_msg(exc)))
            raise
        ultimo = est["e10"].T
        return (nuevo - T1, est, ener) if full else nuevo - T1
    def F_seguro(T1):
        try:
            return F(T1)
        except PropertyRangeError:
            return None
    def F_brentq(T1):
        v = F_seguro(T1) if variante == "V2" else F(T1)
        if v is None:
            raise PuntoNoEvaluable(f"punto interior no evaluable (T={T1:.4f} K)")
        return v
    lo, hi = _bracket_tol(F_seguro, Ts, Tf) if variante == "V2" else _bracketear(F, Ts, Tf)
    _, est, ener = F(brentq(F_brentq, lo, hi, xtol=1e-4), "punto_final", True)
    Wnet = ener["Wt"] - ener["Wp"]
    return dict(estados=est, **ener, Wnet=Wnet, eta=Wnet / ener["Qi"])

def sondear(item: dict) -> dict:   # V0/V1/V2 de una fila + verificación B si KALINA
    kw, real = item["kw"], TeqpVerificado(x=item["x_backend"])
    px = Proxy(real)
    fila = dict(csv_origen=item["csv_origen"], fila_csv=item["fila_csv"], grupo=item["grupo"], **kw,
                T_amb_diseno=T_AMB, backend=f"TeqpVerificado(x={item['x_backend']})",
                clasificacion_original=item["clasif"], eta_original=item["eta_orig"], excepcion_original=item["exc_orig"])
    vk = {k: kw[k] for k in COLS_PARAM if k not in ("eta_t", "eta_p")} | dict(T_amb_diseno=T_AMB)
    for v in ("V0", "V1", "V2"):
        tr, t0 = [], time.perf_counter()
        try:
            res = orquestar(px, kw, v, tr)
            val = evaluar_ciclo(real, res, **vk)
            fila.update({f"{v}": "convergio", f"{v}_clas": val.clasificacion.value,
                         f"{v}_eta": round(res["eta"], 6), f"{v}_Wnet": round(res["Wnet"], 4),
                         f"{v}_T1": round(res["estados"]["e1"].T, 4), f"{v}_msg": val.mensaje_reporte()[:200]})
            if item["eta_orig"] is not None:
                fila[f"d_eta_{v}"] = round(res["eta"] - item["eta_orig"], 9)
            if val.clasificacion.value == "KALINA":          # opción B (CONTEXT.md)
                b = verificar_turbina(res, P_baja=kw["P_baja"], motor_real=_MOTOR_REAL, eta_t=kw["eta_t"])
                fila.update({f"{v}_B_verificado": b["verificado"],
                             f"{v}_B_dh4s": None if b["dh4s"] is None else round(b["dh4s"], 4),
                             f"{v}_B_error": b["error"][:150]})
        except (CicloNoConvergeError, NoBracket, PuntoNoEvaluable) as exc:
            fila.update({f"{v}": "no_convergio", f"{v}_msg": _msg(exc)[:200]})
        except PropertyRangeError as exc:
            fila.update({f"{v}": "error_backend", f"{v}_msg": _msg(exc)[:200]})
        fila[f"{v}_t_s"] = round(time.perf_counter() - t0, 1)
        if v == "V0" and tr:
            fila.update(donde_falla=tr[0]["donde"], T1_trial=tr[0]["T1_trial"], iter_lazo_frio=tr[0]["iter_frio"],
                        nF_V0=tr[0]["nF"], punto_cascada=tr[0]["comp"], excepcion_V0=tr[0]["msg"])
    return fila

def _kw_f2(r) -> dict:      # los 11 parámetros salen de las columnas del CSV
    return {c: float(r[c]) for c in COLS_PARAM} | TOL

def _kw_lt(r) -> dict:      # fijos de calibracion_elsayed_malla.py
    eh, er, ec = float(r.eps_hrvg), float(r.eps_reg), float(r.eps_cond)
    if eh != eh:            # eps vacío -> el fallo fue en el paso base r0
        eh, er, ec = EPS_PARTIDA
    return dict(P_alta=float(r.P_alta), P_baja=float(r.P_baja), T_fuente=float(r.T_fuente),
                x_b=float(r.x_b), eps_hrvg=eh, eps_reg=er, eps_cond=ec, **TOL, **LIT)

def muestra() -> list[dict]:
    d2 = pd.read_csv(_RAIZ / "resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv")
    dl = pd.read_csv(_RAIZ / "resultados/2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv")
    nc2, de = d2[d2.clasificacion == "NO_CONVERGIO"], lambda s: s.fillna("").astype(str)
    ctl2 = d2[(d2.clasificacion == "KALINA") & d2.x_b.isin((0.35, 0.40, 0.45, 0.50)) & (d2.T_fuente == 470.0) &
              d2.P_baja.isin((400., 450., 500., 550., 600.)) & d2.eps_cond.isin((0.80, 0.85, 0.90, 0.95)) &
              (d2.eps_hrvg == 0.85) & (d2.eps_reg == 0.75)]
    specs = (("busqueda_libre_v2", nc2[nc2.mensaje.str.contains("T_from_Ph", na=False)], "f2_T_from_Ph", 15, _kw_f2, 0.5),
             ("busqueda_libre_v2", nc2[nc2.mensaje.str.contains(r"h\(P, s, x\)", na=False)], "f2_h_Ps", 5, _kw_f2, 0.5),
             ("barrido_literatura_kcs11", dl[de(dl.detalle_error).str.contains("T_from_Ph")], "lit_T_from_Ph", 0, _kw_lt, "xb"),
             ("barrido_literatura_kcs11", dl[de(dl.detalle_error).str.contains("no existe equilibrio")], "lit_bifasico", 0, _kw_lt, "xb"),
             ("busqueda_libre_v2", ctl2, "ctl_KALINA_f2", 5, _kw_f2, 0.5),
             ("barrido_literatura_kcs11", dl[dl.clasificacion == "CORREGIBLE"], "ctl_literatura", 5, _kw_lt, "xb"))
    out = []
    for origen, sub, grupo, k, mk, xb in specs:
        n, k = int(sub.shape[0]), k or n   # k=0 -> todas las filas del grupo
        idx = list(range(n)) if n <= k else sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
        for i in idx:
            r, kw = sub.iloc[i], mk(sub.iloc[i])
            exc = r.mensaje if origen.startswith("busqueda") else (r.fallas if grupo.startswith("ctl") else r.detalle_error)
            out.append(dict(csv_origen=origen, fila_csv=int(sub.index[i]), grupo=grupo, kw=kw,
                            x_backend=kw["x_b"] if xb == "xb" else xb, clasif=r.clasificacion,
                            eta_orig=float(r.eta), exc_orig=str(exc)[:200]))
    return out

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items, t0, filas = muestra(), time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        for n, fut in enumerate(as_completed([pool.submit(sondear, i) for i in items]), 1):
            filas.append(fut.result())
            print(f"  {n}/{len(items)} ({time.perf_counter() - t0:.0f} s)", flush=True)
    pd.DataFrame(filas).sort_values(["csv_origen", "fila_csv"]).to_csv(CSV_OUT, index=False)
    print(f"{len(items)} filas -> {CSV_OUT} en {time.perf_counter() - t0:.0f} s")

if __name__ == "__main__":
    main()
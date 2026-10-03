"""Núcleo de MODOS del benchmark de tiempos del "reintento tolerante".

Se reimplementan aquí los modos M0/MA/MB sin editar `src/`:
  "M0"        arranque en frío (`T10_inicial=None`) + `_bracketear` original.
  "MA"        V2 desde el primer intento: `T_sumidero + 5 K` + bracket tolerante
              (tope 6 intentos/extremo, paso 5 K, sin ST).
  ("MB",t,st) corre M0; si lanza `PropertyRangeError` o `CicloNoConvergeError`
              DURANTE el bracketeo (en los extremos), repite con V2 (tope `t`,
              ST según `st`). Tiempo MB = intento fallido + reintento; si M0
              converge, MB = M0 exactamente.

Importa `scripts/sonda_arranque_solver.py` sin modificarlo y reutiliza su
`Proxy`, `decodificar`, `_msg`, `NoBracket`, `PuntoNoEvaluable`, `COLS_PARAM`.
"""
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import sonda_arranque_solver as P                                         # noqa: E402
from scipy.optimize import brentq                                         # noqa: E402
from src._cycle_loops import CicloNoConvergeError, _bracketear, evaluar   # noqa: E402
from src.properties.adapter import PropertyRangeError                     # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado                 # noqa: E402
from src.restricciones import evaluar_ciclo                               # noqa: E402
from src.verificacion_motor_real import verificar_turbina                 # noqa: E402

PASO, TOPE_MA = 5.0, 6
CFGS = [("MB", t, s) for t in (2, 3, 6) for s in (True, False)]   # 6 configs de MB


def cfg_nombre(cfg):
    """Nombre de columna: 'M0', 'MA', 'MB_t2_STsi' …"""
    if not isinstance(cfg, tuple):
        return cfg
    return f"MB_t{cfg[1]}_ST{'si' if cfg[2] else 'no'}"


def parse_cfg(nombre):
    """Inversa de `cfg_nombre`: 'MB_t6_STsi' -> ('MB', 6, True)."""
    if not nombre.startswith("MB_t"):
        return nombre
    _, t, s = nombre.split("_")
    return ("MB", int(t[1:]), s == "STsi")


def _bifasico(exc) -> bool:
    """`PropertyRangeError` de `equilibrio_liquido_vapor` con el texto 'no existe
    equilibrio bifásico' — la condición EXACTA de la salida temprana (ST)."""
    t = str(exc)
    return isinstance(exc, PropertyRangeError) and "equilibrio_liquido_vapor" in t \
        and "no existe equilibrio bifásico" in t


def _bracket_tope(F, Ts, Tf, max_rep, paso=PASO, st=False):
    """Bracket tolerante: copia local parametrizada de `P._bracket_tol` (NO se
    edita el original) con TOPE de `max_rep` intentos por extremo — el primero
    incluido — y ST. `F(T) -> (valor_o_None, PropertyRangeError_o_None)`."""
    lo, hi = Ts + 1.0, Tf - 1.0
    if not lo < hi:
        raise P.NoBracket("rango físico de T1 degenerado")
    res, err_previo = {}, None
    for lado in ("lo", "hi"):
        T, f, e = (lo if lado == "lo" else hi), None, None
        for n in range(1, int(max_rep) + 1):
            f, e = F(T)
            if f is not None:
                break
            if st and n == 1 and _bifasico(e) and _bifasico(err_previo):
                raise P.NoBracket(f"ST: los dos extremos fallan sin equilibrio "
                                  f"bifásico ({lado}@{T:.1f} K)")
            Tn = T + paso if lado == "lo" else T - paso
            if not (Tn < hi if lado == "lo" else Tn > lo):
                break
            T = Tn
        res[lado], err_previo = (T, f, e), e
    loT, f_lo, _ = res["lo"]
    hiT, f_hi, _ = res["hi"]
    if f_lo is None or f_hi is None:
        raise P.NoBracket(f"sin dos extremos evaluables en {paso} K "
                          f"(f_lo={f_lo}, f_hi={f_hi})")
    if f_lo * f_hi > 0.0:
        raise P.NoBracket(f"extremos [{loT:.1f}, {hiT:.1f}] K sin cambio de signo "
                          f"(f_lo={f_lo:.5g}, f_hi={f_hi:.5g})")
    return loT, hiT


def _intento(px, kw, warm, tol, tope, st, c):
    """Un intento completo (M0 si `tol=False`; V2 acotado si `tol=True`).
    `c` (contador) acumula nF, fase del fallo y cascada del primer fallo."""
    ultimo, Ts, Tf = None, kw["T_sumidero"], kw["T_fuente"]

    def F(T1, full=False):
        nonlocal ultimo
        c["nF"] += 1
        px.calls.clear()
        T10_ini = ultimo if (ultimo is not None or not warm) else Ts + 5.0
        try:
            nuevo, est, ener = evaluar(T1, px, **kw, T10_inicial=T10_ini)
        except (PropertyRangeError, CicloNoConvergeError):
            if not c["cascada"] and px.calls:
                c["cascada"] = P.decodificar(len(px.calls) - 1, px.calls[-1])[0]
            raise
        ultimo = est["e10"].T
        return (nuevo - T1, est, ener) if full else nuevo - T1

    def F_seguro(T1):
        try:
            return F(T1), None
        except PropertyRangeError as exc:
            return None, exc

    def F_brentq(T1):
        if not tol:
            return F(T1)
        v, _ = F_seguro(T1)
        if v is None:
            raise P.PuntoNoEvaluable(f"punto interior no evaluable (T={T1:.4f} K)")
        return v

    c["fase"] = "bracket"
    lo, hi = (_bracket_tope(F_seguro, Ts, Tf, tope, st=st) if tol
              else _bracketear(F, Ts, Tf))
    c["fase"] = "brentq"
    T1 = brentq(F_brentq, lo, hi, xtol=1e-4)
    c["fase"] = "final"
    _, est, ener = F(T1, full=True)
    Wnet = ener["Wt"] - ener["Wp"]
    return dict(estados=est, **ener, Wnet=Wnet, eta=Wnet / ener["Qi"])


def _correr(px, kw, cfg, c):
    """Devuelve el estado final del intento (o lanza). MB = intento M0 + reintento
    V2 si el M0 falla en el bracketeo; el tiempo se acumula en `c['t1']` + el del
    reintento."""
    if not isinstance(cfg, tuple):
        return _intento(px, kw, cfg == "MA", cfg == "MA", TOPE_MA, False, c)
    t0 = time.perf_counter()
    try:
        return _intento(px, kw, False, False, TOPE_MA, False, c)
    except (PropertyRangeError, CicloNoConvergeError) as exc:
        if c["fase"] != "bracket":          # no falló en los extremos: no reintenta
            raise
        c["reintento"], c["msg1"] = True, P._msg(exc)[:200]
        c["nF1"], c["t1"] = c["nF"], round(time.perf_counter() - t0, 2)
        return _intento(px, kw, True, True, cfg[1], cfg[2], c)


def medir(tarea: dict) -> dict:
    """Una fila x una configuración: cronometra, clasifica y verifica (B) si KALINA."""
    item, cfg = tarea["item"], tarea["cfg"]
    kw, real = item["kw"], TeqpVerificado(x=item["x_backend"])
    px = P.Proxy(real)
    base = dict(etapa=tarea["etapa"], config=cfg_nombre(cfg), csv_origen=item["csv_origen"],
                fila_csv=item["fila_csv"], grupo=item["grupo"], **kw,
                x_backend=item["x_backend"], T_amb_diseno=P.T_AMB,
                backend=f"TeqpVerificado(x={item['x_backend']})",
                clasificacion_original=item["clasif"], eta_original=item["eta_orig"])
    vk = {k: kw[k] for k in P.COLS_PARAM if k not in ("eta_t", "eta_p")} | dict(T_amb_diseno=P.T_AMB)
    c = dict(nF=0, nF1=0, t1=0.0, fase="", cascada="", reintento=False, msg1="")
    t0 = time.perf_counter()
    try:
        res = _correr(px, kw, cfg, c)
        val = evaluar_ciclo(real, res, **vk)
        out = dict(convergio=True, causa="", clasificacion=val.clasificacion.value,
                   eta=round(res["eta"], 6), T1_sol=round(res["estados"]["e1"].T, 4),
                   nF=c["nF"], msg=val.mensaje_reporte()[:200])
        if val.clasificacion.value == "KALINA":
            b = verificar_turbina(res, P_baja=kw["P_baja"], motor_real=P._MOTOR_REAL,
                                  eta_t=kw["eta_t"])
            out.update(B_verificado=b["verificado"],
                       B_dh4s=None if b["dh4s"] is None else round(b["dh4s"], 4))
    except (CicloNoConvergeError, P.NoBracket, P.PuntoNoEvaluable) as exc:
        out = dict(convergio=False, causa=type(exc).__name__, clasificacion="NO_CONVERGIO",
                   eta=None, T1_sol=None, nF=c["nF"], msg=P._msg(exc)[:200])
    except PropertyRangeError as exc:
        out = dict(convergio=False, causa="PropertyRangeError", clasificacion="NO_CONVERGIO",
                   eta=None, T1_sol=None, nF=c["nF"], msg=P._msg(exc)[:200])
    out.update(t_s=round(time.perf_counter() - t0, 2), nF_intento1=c["nF1"],
               t_intento1_s=c["t1"], reintento_usado=c["reintento"],
               punto_cascada=c["cascada"], msg_intento1=c["msg1"],
               st_disparo=out["msg"].startswith("ST:"), fase_fallo=c["fase"])
    return base | out
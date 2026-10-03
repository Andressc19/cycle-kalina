"""Ablación arranque vs bracket y comportamiento de tiempos (sin tocar `src/`).

Tarea `2026-10-01-ablacion-arranque-y-tiempos`: no modifica `src/`, `tests/` ni
CSV existentes; escribe solo `resultados/2026-10-01_ablacion_tiempos/`. Importa
`scripts/sonda_arranque_solver.py` (sin modificarlo) y reutiliza su muestra de
56 filas, su `Proxy`, su `_bracket_tol` y sus parámetros por fila. Corre 5
variantes sobre las MISMAS 56 filas: **V0** original; **V1** arranque tibio;
**V2** V1 + bracket tolerante; **VB** V0 + bracket tolerante (solo bracket);
**V3** V1 + bracket tolerante con repliegue por bisección (<= 6 intentos/extremo).
V0/V1/V2 se vuelven a medir aquí (corrida de referencia) porque el CSV previo solo
trae `nF` e iteraciones del PRIMER fallo de V0, no los totales por variante.
Contadores: `nF` = evaluaciones de F; `iter` = iteraciones del lazo frío sumadas
en todas las evaluaciones, contadas por la traza del `Proxy`
(`NPRE` + 15 por iteración + 1 de cierre); el resto de esa división se cuenta en
`<var>_anom` (debe quedar en 0).
"""
import sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))
import sonda_arranque_solver as P                                           # noqa: E402
from scipy.optimize import brentq                                            # noqa: E402
from src._cycle_loops import CicloNoConvergeError, _bracketear, evaluar      # noqa: E402
from src.properties.adapter import PropertyRangeError                        # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado                    # noqa: E402
from src.restricciones import evaluar_ciclo                                  # noqa: E402
from src.verificacion_motor_real import verificar_turbina                   # noqa: E402

OUT_DIR = _RAIZ / "resultados" / "2026-10-01_ablacion_tiempos"
CSV_OUT = OUT_DIR / "ablacion_filas.csv"
N_WORKERS, MAX_BIS = 6, 6
NPRE, NCOLD = len(P.PRE), len(P.COLD)
VARIANTES = ("V0", "V1", "V2", "VB", "V3")
ARRANQUE = {"V0": False, "V1": True, "V2": True, "VB": False, "V3": True}  # warm start?
BRACKET = {"V0": "orig", "V1": "orig", "V2": "tol", "VB": "tol", "V3": "bis"}


def _iter_frio(ncalls) -> int:      # iteraciones del lazo frío de una traza completa
    k, resto = divmod(max(0, ncalls - NPRE - 1), NCOLD)
    return k if resto == 0 else 0


def _bracket_bis(F, Ts, Tf, max_intentos=MAX_BIS):
    """V3: repliegue por bisección. Si un extremo no evalúa, se prueban hacia el
    interior los puntos `extremo + (distancia_opuesta)/2^k`, k=1..max_intentos
    (6): el punto medio es el primer intento. El extremo opuesto que hace de
    referencia es el último evaluable (el del otro lado, ya refinado si cerró)."""
    lo0, hi0 = Ts + 1.0, Tf - 1.0
    if not lo0 < hi0:
        raise P.NoBracket("rango físico de T1 degenerado")
    lo, f_lo = lo0, F(lo0)
    for k in range(1, max_intentos + 1):
        if f_lo is not None:
            break
        lo = lo0 + (hi0 - lo0) / 2 ** k
        f_lo = F(lo)
    if f_lo is None:
        raise P.NoBracket(f"extremo_lo sin evaluar en {max_intentos} intentos "
                          f"de bisección (T={lo:.4f} K)")
    hi, f_hi = hi0, F(hi0)
    for k in range(1, max_intentos + 1):
        if f_hi is not None:
            break
        hi = hi0 - (hi0 - lo) / 2 ** k
        f_hi = F(hi)
    if f_hi is None:
        raise P.NoBracket(f"extremo_hi sin evaluar en {max_intentos} intentos "
                          f"de bisección (T={hi:.4f} K)")
    if f_lo * f_hi > 0.0:
        raise P.NoBracket(f"extremos [{lo:.1f}, {hi:.1f}] K sin cambio de signo "
                          f"(f_lo={f_lo:.5g}, f_hi={f_hi:.5g})")
    return lo, hi


def orquestar(px, kw, variante, cont):
    """Réplica de `resolver_ciclo` con la variante pedida (V0/V1 idénticas a la
    sonda previa; VB/V2 = bracket tolerante; V3 = bisección). Acumula en `cont`
    nF, iteraciones del lazo frío y la traza del primer fallo."""
    warm, modo = ARRANQUE[variante], BRACKET[variante]
    ultimo, Ts, Tf = None, kw["T_sumidero"], kw["T_fuente"]

    def F(T1, fase=None, full=False):
        nonlocal ultimo
        cont["nF"] += 1
        px.calls.clear()
        T10_ini = ultimo if (ultimo is not None or not warm) else Ts + 5.0
        try:
            nuevo, est, ener = evaluar(T1, px, **kw, T10_inicial=T10_ini)
        except (PropertyRangeError, CicloNoConvergeError) as exc:
            if isinstance(exc, PropertyRangeError):
                comp, it = P.decodificar(len(px.calls) - 1, px.calls[-1] if px.calls else "")
            else:                                    # lazo frío agotado (max_iter_frio)
                comp, it = "lazo_frio.max_iter", kw["max_iter_frio"]
            # `_bracketear` solo amplía hacia fuera: extremo si T1 <= Ts+1 o >= Tf-1
            donde = fase or ("extremo_lo" if T1 <= Ts + 1.0 + 1e-9 else
                             "extremo_hi" if T1 >= Tf - 1.0 - 1e-9 else "interior_brentq")
            cont["iter"] += it
            cont["tr"].append(dict(donde=donde, T1_trial=round(T1, 4), comp=comp,
                                   iter_frio=it, nF=cont["nF"], msg=P._msg(exc)))
            raise
        k, resto = divmod(len(px.calls) - NPRE - 1, NCOLD)
        cont["iter"] += k
        cont["anom"] += int(resto != 0)
        ultimo = est["e10"].T
        return (nuevo - T1, est, ener) if full else nuevo - T1

    def F_seguro(T1):
        try:
            return F(T1)
        except PropertyRangeError:
            return None

    def F_brentq(T1):
        v = F_seguro(T1) if modo != "orig" else F(T1)
        if v is None:
            raise P.PuntoNoEvaluable(f"punto interior no evaluable (T={T1:.4f} K)")
        return v

    br = {"orig": _bracketear, "tol": P._bracket_tol, "bis": _bracket_bis}[modo]
    lo, hi = br(F_seguro if modo != "orig" else F, Ts, Tf)
    _, est, ener = F(brentq(F_brentq, lo, hi, xtol=1e-4), "punto_final", True)
    Wnet = ener["Wt"] - ener["Wp"]
    return dict(estados=est, **ener, Wnet=Wnet, eta=Wnet / ener["Qi"])


def sondear(item: dict) -> dict:
    """Las 5 variantes de una fila + verificación B (CONTEXT.md) si KALINA."""
    kw, real = item["kw"], TeqpVerificado(x=item["x_backend"])
    px = P.Proxy(real)
    fila = dict(csv_origen=item["csv_origen"], fila_csv=item["fila_csv"], grupo=item["grupo"], **kw,
                T_amb_diseno=P.T_AMB, x_backend=item["x_backend"],
                backend=f"TeqpVerificado(x={item['x_backend']})",
                clasificacion_original=item["clasif"], eta_original=item["eta_orig"],
                excepcion_original=item["exc_orig"])
    vk = {k: kw[k] for k in P.COLS_PARAM if k not in ("eta_t", "eta_p")} | dict(T_amb_diseno=P.T_AMB)
    for v in VARIANTES:
        cont, t0 = dict(nF=0, iter=0, anom=0, tr=[]), time.perf_counter()
        try:
            res = orquestar(px, kw, v, cont)
            val = evaluar_ciclo(real, res, **vk)
            fila.update({f"{v}": "convergio", f"{v}_causa": "", f"{v}_clas": val.clasificacion.value,
                         f"{v}_eta": round(res["eta"], 6), f"{v}_Wnet": round(res["Wnet"], 4),
                         f"{v}_T1": round(res["estados"]["e1"].T, 4),
                         f"{v}_msg": val.mensaje_reporte()[:200]})
            if item["eta_orig"] is not None:
                fila[f"d_eta_{v}"] = round(res["eta"] - item["eta_orig"], 9)
            if val.clasificacion.value == "KALINA":          # opción B (CONTEXT.md)
                b = verificar_turbina(res, P_baja=kw["P_baja"], motor_real=P._MOTOR_REAL, eta_t=kw["eta_t"])
                fila.update({f"{v}_B_verificado": b["verificado"],
                             f"{v}_B_dh4s": None if b["dh4s"] is None else round(b["dh4s"], 4)})
        except (CicloNoConvergeError, P.NoBracket, P.PuntoNoEvaluable) as exc:
            fila.update({f"{v}": "no_convergio", f"{v}_causa": type(exc).__name__,
                         f"{v}_msg": P._msg(exc)[:200]})
        except PropertyRangeError as exc:
            fila.update({f"{v}": "error_backend", f"{v}_causa": "PropertyRangeError",
                         f"{v}_msg": P._msg(exc)[:200]})
        t_s = time.perf_counter() - t0
        fila.update({f"{v}_t_s": round(t_s, 1), f"{v}_nF": cont["nF"], f"{v}_iter": cont["iter"],
                     f"{v}_anom": cont["anom"],
                     f"{v}_t_por_F": round(t_s / cont["nF"], 3) if cont["nF"] else None})
        if v == "V0" and cont["tr"]:
            fila.update(donde_falla=cont["tr"][0]["donde"], T1_trial=cont["tr"][0]["T1_trial"],
                        iter_lazo_frio=cont["tr"][0]["iter_frio"],
                        nF_V0_ref=cont["tr"][0]["nF"], punto_cascada=cont["tr"][0]["comp"],
                        excepcion_V0=cont["tr"][0]["msg"])
    return fila


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items, t0, filas = P.muestra(), time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        for n, fut in enumerate(as_completed([pool.submit(sondear, i) for i in items]), 1):
            filas.append(fut.result())
            print(f"  {n}/{len(items)} ({time.perf_counter() - t0:.0f} s)", flush=True)
    df = pd.DataFrame(filas).sort_values(["csv_origen", "fila_csv"])
    df.to_csv(CSV_OUT, index=False)
    print(f"{len(items)} filas x {len(VARIANTES)} variantes -> {CSV_OUT} "
          f"en {time.perf_counter() - t0:.0f} s de reloj de pared; anomalias de traza: {int(df[[f'{v}_anom' for v in VARIANTES]].to_numpy().sum())}")


if __name__ == "__main__":
    main()
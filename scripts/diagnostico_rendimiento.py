"""Diagnóstico de rendimiento del solver del ciclo con el backend NH3-H2O real.

Tarea 2026-09-17-diagnostico-rendimiento-solver. NO toca el código de
producción: instrumenta por monkeypatch en tiempo de ejecución (componentes,
métodos del backend y funciones del motor portado) y mide:

- coste por llamada del motor (`estado`, `estado_de`, `flash_TP`);
- coste por método del adapter (h, s, T_from_Ph, T_from_Ps, equilibrio);
- coste por componente (resolver de cada componente del lazo frío);
- iteraciones del lazo interior (`lazo_frio`) por evaluación del lazo exterior;
- intento completo de `resolver_ciclo` con presupuesto de tiempo (watchdog que
  fuerza os._exit; nunca se espera más de lo pedido).

Uso (con el venv del proyecto, desde la raíz):
    python scripts/diagnostico_rendimiento.py micro
    python scripts/diagnostico_rendimiento.py evaluar [segundos]
    python scripts/diagnostico_rendimiento.py tibio
    python scripts/diagnostico_rendimiento.py final --cold [segundos]
    python scripts/diagnostico_rendimiento.py final --warm [segundos]
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

from scipy.optimize import brentq

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))

import src.components.absorbedor as C_abs
import src.components.bomba as C_bomba
import src.components.condensador as C_cond
import src.components.hrvg as C_hrvg
import src.components.regenerador as C_reg
import src.components.separador as C_sep
import src.components.turbina as C_turb
import src.components.valvula as C_valv
import src.properties._kalina_flash as kf
from src import _cycle_loops as loops
from src import cycle_solver as solver
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter

# -- parámetros del caso base (TASK_CONTEXT 2026-09-17-diagnostico...) ---------
PARAMS = dict(P_alta=3000.0, P_baja=400.0, T_fuente=470.0,
              T_sumidero=300.032917, x_b=0.5, m_b=1.0, eta_t=0.85, eta_p=0.75,
              eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
TOL = dict(tol_T10=1e-4, max_iter_frio=300)


# -- instrumentación -----------------------------------------------------------
class Stats:
    """Contadores y acumuladores de tiempo (segundos) por clave."""

    def __init__(self) -> None:
        self.n = defaultdict(int)
        self.t = defaultdict(float)
        self.iter_por_lazo: list[int] = []

    def resumen(self) -> str:
        lineas = []
        for clave in sorted(set(self.n) | set(self.t)):
            n, t = self.n[clave], self.t[clave]
            medio = f"{t / n * 1e3:8.1f} ms" if n else "   --   "
            lineas.append(f"  {clave:28s} n={n:6d}  total={t:9.3f} s  "
                          f"media={medio}")
        return "\n".join(lineas)


def parchear_func(modulo, nombre, stats, clave):
    """Envuelve una función del módulo con contador+tiempo (monkeypatch)."""
    orig = getattr(modulo, nombre)

    def nueva(*a, **k):
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            dt = time.perf_counter() - t0
            stats.n[clave] += 1
            stats.t[clave] += dt

    setattr(modulo, nombre, nueva)
    return orig


def parchear_metodo(instancia, nombre, stats, clave):
    """Envuelve un método (bound) de una instancia con contador+tiempo."""
    orig = getattr(instancia, nombre)

    def nueva(*a, **k):
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            dt = time.perf_counter() - t0
            stats.n[clave] += 1
            stats.t[clave] += dt

    setattr(instancia, nombre, nueva)
    return orig


def limpiar_caches_motor() -> None:
    """Vacía las cachés del motor portado para medir arranques fríos honestos."""
    kf._flash.clear()
    kf._ultimaT.clear()
    kf._puros.clear()
    kf._env.clear()


def con_presupuesto(segundos: float, fn):
    """Ejecuta fn; un watchdog fuerza os._exit si se supera el presupuesto."""
    def matar():
        print(f"\n[LIMITE] presupuesto de {segundos:.0f} s agotado; mato el "
              f"proceso ahora mismo.", flush=True)
        os._exit(3)

    timer = threading.Timer(segundos, matar)
    timer.daemon = True
    timer.start()
    try:
        return fn()
    finally:
        timer.cancel()


def _adapter_instrumentado(stats):
    backend = AmmoniaWaterAdapter(x=0.5)
    for nombre, clave in (("h", "backend.h"), ("s", "backend.s"),
                          ("T_from_Ph", "backend.T_from_Ph"),
                          ("T_from_Ps", "backend.T_from_Ps"),
                          ("equilibrio_liquido_vapor", "backend.equilibrio")):
        parchear_metodo(backend, nombre, stats, clave)
    return backend


def _patch_motor(stats):
    parchear_func(kf, "estado", stats, "motor.estado")
    parchear_func(kf, "estado_de", stats, "motor.estado_de")
    parchear_func(kf, "flash_TP", stats, "motor.flash_TP")


def _patch_componentes(stats):
    parchear_func(C_hrvg, "resolver", stats, "comp.hrvg")
    parchear_func(C_sep, "resolver", stats, "comp.separador")
    parchear_func(C_turb, "resolver", stats, "comp.turbina")
    parchear_func(C_reg, "resolver", stats, "comp.regenerador")
    parchear_func(C_valv, "resolver", stats, "comp.valvula")
    parchear_func(C_abs, "resolver", stats, "comp.absorbedor")
    parchear_func(C_cond, "resolver", stats, "comp.condensador")
    parchear_func(C_bomba, "resolver", stats, "comp.bomba")


def _patch_lazo(stats, verbose=False):
    orig = loops.lazo_frio

    def nueva(*a, **k):
        prev_bomba = stats.n["comp.bomba"]
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            dt = time.perf_counter() - t0
            stats.n["lazo_frio"] += 1
            stats.t["lazo_frio"] += dt
            stats.iter_por_lazo.append(stats.n["comp.bomba"] - prev_bomba)
            if verbose:
                print(f"  [eval #{stats.n['lazo_frio']}] lazo_frio={dt:6.2f} s "
                      f"| {stats.iter_por_lazo[-1]:3d} iteraciones interiores",
                      flush=True)

    loops.lazo_frio = nueva
    return orig


# -- experimentos --------------------------------------------------------------
def micro():
    """Coste por llamada de cada operación del backend/motor (frío y tibio)."""
    stats = Stats()
    _patch_motor(stats)
    backend = _adapter_instrumentado(stats)
    P, T, x = 3000.0, 330.0, 0.5

    def medir(nombre, fn, veces=3):
        times = []
        for _ in range(veces):
            limpiar_caches_motor()
            t0 = time.perf_counter()
            fn()
            times.append(time.perf_counter() - t0)
        limpiar_caches_motor()
        t0 = time.perf_counter()
        fn()
        tibio = time.perf_counter() - t0
        print(f"{nombre:32s} frio_cada(min)={min(times):8.3f} s  "
              f"tibio={tibio:8.4f} s")
        time.sleep(0.05)

    medir("h(P,T,x)", lambda: backend.h(P, T=T, x=x))
    medir("s(P,T,x)", lambda: backend.s(P, T=T, x=x))
    medir("T_from_Ph(P,h,x)", lambda: backend.T_from_Ph(P, 650.0, x=x))
    medir("T_from_Ps(P,s,x)", lambda: backend.T_from_Ps(P, 2.0, x=x))
    medir("equilibrio(P,T)", lambda: backend.equilibrio_liquido_vapor(P, 370.0))
    medir("h(P,s,x) [bomba]", lambda: backend.h(P, s=1.7, x=x))
    print("\n-- totales del micro-benchmark (motor) --")
    print(stats.resumen())


def evaluar_una(segundos: float):
    """Una evaluación del lazo exterior (evaluar, T1=330) instrumentada."""
    stats = Stats()
    _patch_motor(stats)
    _patch_componentes(stats)
    _patch_lazo(stats)
    backend = _adapter_instrumentado(stats)
    limpiar_caches_motor()

    def correr():
        t0 = time.perf_counter()
        T1_nuevo, estados, energias = loops.evaluar(330.0, backend, **PARAMS,
                                                    **TOL)
        print(f"evaluar(T1=330) -> T1_nuevo = {T1_nuevo:.4f} K en "
              f"{time.perf_counter() - t0:.2f} s", flush=True)
        n_it = stats.iter_por_lazo[-1]
        print(f"iteraciones del lazo interior: {n_it}")
        print(f"e10.T = {estados['e10'].T:.4f} K, "
              f"Qi = {energias['Qi']:.2f} kW")
        print("\n-- tiempo por componente --")
        for cl in sorted(stats.t, key=lambda c: -stats.t[c]):
            if cl.startswith("comp."):
                print(f"  {cl:22s} n={stats.n[cl]:4d} "
                      f"total={stats.t[cl]:7.2f} s "
                      f"media={stats.t[cl] / stats.n[cl] * 1e3:8.1f} ms")
        print("\n-- motor/backend --")
        print(stats.resumen())
        if n_it and stats.t["lazo_frio"]:
            print(f"\nlazo_frio total={stats.t['lazo_frio']:.2f} s en {n_it} "
                  f"iteraciones -> {stats.t['lazo_frio'] / n_it:.2f} "
                  f"s/iteración típica")

    con_presupuesto(segundos, correr)


def tibio():
    """Compara arranque frío (T10=T1) vs tibio (último T10) en 3 evaluaciones."""
    stats = Stats()
    _patch_motor(stats)
    _patch_componentes(stats)
    _patch_lazo(stats)
    backend = _adapter_instrumentado(stats)

    print("Modo FRÍO (T10_inicial = T1_trial, como el código actual):")
    limpiar_caches_motor()
    for T1 in (350.0, 360.0, 370.0):
        t0 = time.perf_counter()
        T1n, estados, _ = loops.evaluar(T1, backend, **PARAMS, **TOL,
                                        T10_inicial=None)
        dt = time.perf_counter() - t0
        print(f"  T1={T1:6.1f} -> T1n={T1n:7.3f} K | {dt:7.2f} s | "
              f"{stats.iter_por_lazo[-1]:3d} iter | e10.T="
              f"{estados['e10'].T:7.3f} K")

    print("Modo TIBIO (T10_inicial = último T10 convergido):")
    limpiar_caches_motor()
    t10_cache = None
    for T1 in (350.0, 360.0, 370.0):
        t0 = time.perf_counter()
        T1n, estados, _ = loops.evaluar(T1, backend, **PARAMS, **TOL,
                                        T10_inicial=t10_cache)
        dt = time.perf_counter() - t0
        t10_cache = estados["e10"].T
        print(f"  T1={T1:6.1f} -> T1n={T1n:7.3f} K | {dt:7.2f} s | "
              f"{stats.iter_por_lazo[-1]:3d} iter | e10.T="
              f"{estados['e10'].T:7.3f} K")


def residuos(segundos: float):
    """Replica del lazo_frio con registro del residuo |T10_{n+1}-T10_n| por
    iteración, para ver si converge a tol_T10=1e-4 o si el ruido numérico del
    motor lo plafonea (candidato a relajar tolerancia). Time-box obligatorio."""
    stats = Stats()
    _patch_motor(stats)
    _patch_componentes(stats)
    backend = _adapter_instrumentado(stats)
    limpiar_caches_motor()

    def correr():
        # cascada cabeza (lo mismo que evaluar antes del lazo_frio)
        h1 = backend.h(PARAMS["P_alta"], T=330.0, x=PARAMS["x_b"])
        s1 = backend.s(PARAMS["P_alta"], T=330.0, x=PARAMS["x_b"])
        from src.state import EstadoTermo
        e1 = EstadoTermo(T=330.0, P=PARAMS["P_alta"], h=h1, s=s1,
                         x=PARAMS["x_b"], m=1.0)
        e2, info = C_hrvg.resolver(e1, backend, T_fuente=PARAMS["T_fuente"],
                                   eps=PARAMS["eps_hrvg"], m_b=1.0)
        e3, e5, _ = C_sep.resolver(e2, backend)
        m_v, m_l = e3.m, e5.m
        e4, _ = C_turb.resolver(e3, backend, P_salida=PARAMS["P_baja"],
                                eta_t=PARAMS["eta_t"])

        T10 = 330.0
        print(f"separador: m_v={m_v:.4f}, m_l={m_l:.4f}, e3.x={e3.x:.4f}, "
              f"e5.x={e5.x:.4f}", flush=True)
        print("iter | T10_guess   | T10_salida | residuo | t_acum(s)")
        t0 = time.perf_counter()
        for it in range(1, 51):
            t_it = time.perf_counter()
            h_fria = backend.h(PARAMS["P_alta"], T=T10, x=PARAMS["x_b"])
            s_fria = backend.s(PARAMS["P_alta"], T=T10, x=PARAMS["x_b"])
            ef = EstadoTermo(T=T10, P=PARAMS["P_alta"], h=h_fria, s=s_fria,
                             x=PARAMS["x_b"])
            e6, _, _ = C_reg.resolver(e5, ef, backend, eps=PARAMS["eps_reg"])
            e7, _ = C_valv.resolver(e6, backend, P_salida=PARAMS["P_baja"])
            e8, _ = C_abs.resolver(e4, e7, backend, m_turbina=m_v,
                                   m_valvula=m_l)
            e9, _ = C_cond.resolver(e8, backend,
                                    T_sumidero=PARAMS["T_sumidero"],
                                    eps=PARAMS["eps_cond"], m=1.0)
            e10, _ = C_bomba.resolver(e9, backend, P_salida=PARAMS["P_alta"],
                                      eta_p=PARAMS["eta_p"], m=1.0)
            resid = abs(e10.T - T10)
            dt_it = time.perf_counter() - t_it
            print(f"{it:4d} | {T10:9.4f} | {e10.T:9.4f} | {resid:9.2e} "
                  f"| {time.perf_counter() - t0:8.1f}", flush=True)
            if resid < 1e-4:
                print(f">>> convergió en iteración {it} (tol 1e-4)")
                break
            T10 = e10.T

    con_presupuesto(segundos, correr)


def _resolver_cold(backend, segundos):
    """Réplica del resolver_ciclo ORIGINAL (arranque frío) para comparar."""
    kw = dict(PARAMS, tol_T10=1e-4, max_iter_frio=300)

    def F(T1):
        T1n, _, _ = loops.evaluar(T1, backend, **kw, T10_inicial=None)
        return T1n - T1

    lo, hi = loops._bracketear(F, PARAMS["T_sumidero"], PARAMS["T_fuente"])
    T1_sol = brentq(F, lo, hi, xtol=1e-4)
    _, estados, energias = loops.evaluar(T1_sol, backend, **kw, T10_inicial=None)
    return T1_sol, estados, energias


def final(arranque: str, segundos: float):
    """Intento completo de resolver_ciclo con presupuesto de tiempo."""
    stats = Stats()
    _patch_motor(stats)
    _patch_componentes(stats)
    _patch_lazo(stats, verbose=True)
    backend = _adapter_instrumentado(stats)
    limpiar_caches_motor()
    t0 = time.perf_counter()

    def correr():
        if arranque == "cold":
            print("resolver_ciclo (ARRANQUE FRÍO, código original), "
                  "T_fuente=470.0 K", flush=True)
            T1_sol, estados, energias = _resolver_cold(backend, segundos)
        else:
            print("resolver_ciclo (ARRANQUE TIBIO) — backend REAL, "
                  "T_fuente=470.0 K", flush=True)
            res = solver.resolver_ciclo(backend, **PARAMS)
            T1_sol = res["estados"]["e1"].T
            estados, energias = res["estados"], res
        dt = time.perf_counter() - t0
        print(f"\n[CONVERGIO] T1_sol = {T1_sol:.4f} K en {dt:.2f} s; "
              f"evaluaciones exteriores = {stats.n['lazo_frio']}", flush=True)
        print("\n-- estados --")
        for i in range(1, 11):
            e = estados[f"e{i}"]
            print(f"  e{i:2d}: T={e.T:8.3f} K  P={e.P:8.1f} kPa  "
                  f"h={e.h:9.3f} kJ/kg  s={e.s:8.4f}  x={e.x:.4f}  m={e.m}")
        print("\n-- energías --")
        for k in ("Qi", "Qout", "Wt", "Wp", "Qreg"):
            print(f"  {k:6s} = {energias[k]:.4f} kW")
        if arranque == "warm":
            print(f"  {'Wnet':6s} = {res['Wnet']:.4f} kW")
            print(f"  {'eta':6s} = {res['eta']:.6f}")
        print("\n-- tiempo por componente --")
        for cl in sorted(stats.t, key=lambda c: -stats.t[c]):
            if cl.startswith("comp."):
                print(f"  {cl:22s} n={stats.n[cl]:4d} "
                      f"total={stats.t[cl]:7.2f} s")
        print("\n-- motor/backend --")
        print(stats.resumen())
        its = stats.iter_por_lazo
        print(f"\niteraciones interiores por evaluación: {its}")

    con_presupuesto(segundos, correr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["micro", "evaluar", "tibio", "residuos",
                                     "final"])
    ap.add_argument("extra", nargs="?", default=None)
    ap.add_argument("--cold", action="store_true")
    ap.add_argument("--warm", action="store_true")
    args = ap.parse_args()

    if args.modo == "micro":
        micro()
    elif args.modo == "evaluar":
        evaluar_una(float(args.extra or "120"))
    elif args.modo == "tibio":
        tibio()
    elif args.modo == "residuos":
        residuos(float(args.extra or "240"))
    elif args.modo == "final":
        seg = float(args.extra or "600")
        if args.warm:
            final("warm", seg)
        elif args.cold:
            final("cold", seg)
        else:
            sys.exit("final requiere --cold o --warm")


if __name__ == "__main__":
    main()
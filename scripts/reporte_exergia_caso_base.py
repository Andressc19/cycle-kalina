"""Reporte de exergía del caso base del ciclo Kalina KSC-11 (backend real).

Tarea 2026-09-17-exergia: ejecuta `resolver_ciclo` con el `AmmoniaWaterAdapter`
real (caso base de CONTEXT.md: T_fuente=470 K, resto de valores por defecto —
~8 min, esperado y ya diagnosticado) y calcula el balance exergético completo
con `src.exergy.calcular_exergia` (T0=300.032917 K, P0=101.325 kPa). Imprime
el reporte numérico que pide el TASK_CONTEXT en RESULTS.

Uso (con el venv del proyecto, desde la raíz):
    python scripts/reporte_exergia_caso_base.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))

from src import exergy
from src.cycle_solver import resolver_ciclo
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter

# Parámetros del caso base (CONTEXT.md "Valores por defecto sugeridos para la
# UI" + nota de la tarea 2026-09-17-diagnostico-rendimiento-solver).
PARAMS = dict(P_alta=3000.0, P_baja=400.0, T_fuente=470.0,
              T_sumidero=300.032917, x_b=0.5, m_b=1.0, eta_t=0.85, eta_p=0.75,
              eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
T0, P0 = exergy.T0_POR_DEFECTO, exergy.P0_POR_DEFECTO


def main() -> None:
    # Consola Windows cp1252: forzar UTF-8 para caracteres no ASCII.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    backend = AmmoniaWaterAdapter(x=0.5)
    t0 = time.perf_counter()
    print("Resolviendo el ciclo con el backend real "
          "(~8 min esperado, T_fuente=470 K)...", flush=True)
    res = resolver_ciclo(backend, **PARAMS)
    t_res = time.perf_counter() - t0
    ex = exergy.calcular_exergia(res, backend, T_fuente=PARAMS["T_fuente"],
                                 T_sumidero=PARAMS["T_sumidero"], T0=T0, P0=P0)

    print(f"\n[CONVERGIO] en {t_res:.1f} s -- eta = {res['eta']:.6f} "
          f"({100 * res['eta']:.2f} %)")
    print(f"T1 = {res['estados']['e1'].T:.4f} K | "
          f"T2 = {res['estados']['e2'].T:.4f} K")
    print("\n-- 1) exergia fisica por estado [kJ/kg] "
          f"(T0={T0:.4f} K, P0={P0:.1f} kPa) --")
    encabezado = "  estado    T[K]      P[kPa]     h[kJ/kg]   s[kJ/kgK]   x     m[kg/s]   ex_fisica"
    print(encabezado)
    for i in range(1, 11):
        e = ex["estados"][f"e{i}"]
        print(f"  e{i:<5d} {e.T:9.3f} {e.P:9.1f} {e.h:10.3f} {e.s:10.4f} "
              f"{e.x:6.4f} {e.m:8.4f} {e.exergia_fisica:10.4f}")

    print("\n-- 2) Sgen [kW/K] y Ed [kW] por componente (Ed = T0*Sgen) --")
    for comp in ("hrvg", "separador", "turbina", "regenerador", "valvula",
                 "absorbedor", "condensador", "bomba"):
        print(f"  {comp:12s} Sgen = {ex['sgen'][comp]:12.6f}   "
              f"Ed = {ex['ed'][comp]:10.4f}")
    print(f"  {'Ed_total':12s} {'':12s} Ed = {ex['ed_total']:10.4f} kW")

    print("\n-- 3) balance global de exergia [kW] --")
    print(f"  Ex_Qi   = {ex['ex_qi']:10.4f}   (Qi = {res['Qi']:.4f} kW, "
          f"T_fuente = 470 K)")
    print(f"  Ex_Qout = {ex['ex_qout']:10.4f}   (Qout = {res['Qout']:.4f} kW, "
          f"T_sumidero = 300.032917 K)")
    print(f"  Wnet    = {res['Wnet']:10.4f}   (Wt = {res['Wt']:.4f}, "
          f"Wp = {res['Wp']:.4f})")
    print(f"  residual = Ex_Qi - Wnet - Ex_Qout - Ed_total = "
          f"{ex['residual']:10.4f} kW")
    print(f"  residual_rel (vs Ex_Qi) = {ex['residual_rel']:.6e}  "
          f"[criterio: < 1e-3]")


if __name__ == "__main__":
    main()
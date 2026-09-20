"""Fase 3 (tarea 2026-09-19-fase3-caso-real): ajuste de P_baja sobre el eje
real de Húsavík para pasar el criterio O2 (cavitación de bomba).

El escaneo (busqueda_base_husavik.py) mostró que T8 (salida absorbedor) se
puede bajar de 302.9 a ~296 K con eta_t/eps_reg/eps_cond, pero el objetivo O2
queda fijo en bubble(P_baja, x_b) = 281.15 K mientras P_baja siga calibrada al
MÍNIMO (T_sumidero + 3 K). El criterio O2 pide un "margen de subenfriamiento
de diseño" contra el piso ambiental 303.55 K (30.4 °C, vault): la forma
honesta de dárselo es subir P_baja por encima del mínimo — sube bubble(P_baja,
x_b) y con ello la temperatura de saturación del condensado.

P_baja del caso real NO está publicada (la literatura da solo P_alta 32-34
bar): este ajuste queda dentro de CAMPOS_CICLO (50-5000 kPa) y se documenta
con honestidad como margen de diseño, no como dato real.

Añade cada punto probado (mismo esquema que `tabla_barrido`) al CSV
busqueda_husavik.csv ya creado por el escaneo. NO modifica código de
producción.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]  # script en scripts/.../fase3_real/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_FUENTE = 394.15
T_SUMIDERO = 278.15
MB = 1.0
ETA_P = 0.80
N_WORKERS = 4
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
       / "busqueda_husavik.csv")
COLUMNAS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "convergio", "clasificacion", "eta", "Wnet", "mensaje")

# (P_alta, P_baja, x_b, eta_t, eps_hrvg, eps_reg, eps_cond)
# Refinamiento final: frontera O2 con eta_t=0.90 (valor citado en la
# literatura del caso) y eps_cond/eps_reg lo mas cerca de los defaults.
PUNTOS = [
    (3300.0, 1150.0, 0.82, 0.90, 0.85, 0.95, 0.98),
    (3300.0, 1200.0, 0.82, 0.90, 0.85, 0.95, 0.98),
    (3300.0, 1250.0, 0.82, 0.90, 0.85, 0.95, 0.98),
    (3300.0, 1200.0, 0.82, 0.90, 0.85, 0.95, 0.95),
    (3300.0, 1250.0, 0.82, 0.90, 0.85, 0.95, 0.95),
    (3300.0, 1300.0, 0.82, 0.90, 0.85, 0.95, 0.95),
    (3300.0, 1200.0, 0.82, 0.90, 0.85, 0.90, 0.98),
]


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.82)


def resolver_punto(pa: float, pb: float, xb: float, eta_t: float, eps_h: float,
                   eps_r: float, eps_c: float) -> dict:
    backend = importar_backend()
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=eta_t,
                 eta_p=ETA_P, eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c)
    fila = dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, P_alta=pa,
                P_baja=pb, x_b=xb, m_b=MB, eta_t=eta_t, eta_p=ETA_P,
                eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, Wnet=None, mensaje=str(exc))
        return fila
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=eps_h, eps_reg=eps_r,
                        eps_cond=eps_c)
    t8 = res["estados"]["e8"].T
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=f"T8={t8:.2f} K || {val.mensaje_reporte()}")
    return fila


def main() -> None:
    print(f"Ajuste de P_baja: {len(PUNTOS)} puntos -> {CSV}", flush=True)
    filas = []
    t0 = time.perf_counter()
    n = 0
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, *p) for p in PUNTOS]
        for fut in as_completed(futuros):
            filas.append(fut.result())
            n += 1
            if n % 2 == 0:
                print(f"  {n}/{len(PUNTOS)} ({time.perf_counter()-t0:.0f} s)",
                      flush=True)
    df_nuevo = pd.DataFrame(filas)[list(COLUMNAS)]
    df_nuevo.to_csv(CSV, mode="a", header=False, index=False,
                    encoding="utf-8")

    print(f"\nResultados ({time.perf_counter()-t0:.0f} s total):", flush=True)
    for f in filas:
        estado = (f"eta={f['eta']:.4f} Wnet={f['Wnet']:.1f} kW"
                  if f["convergio"] else "sin converger")
        print(f"  P_baja={f['P_baja']:.0f} eta_t={f['eta_t']:.2f} "
              f"eps_r={f['eps_reg']:.2f} eps_c={f['eps_cond']:.2f} "
              f"-> {f['clasificacion']} ({estado})", flush=True)
    kalina = [f for f in filas if f["clasificacion"] == "KALINA"]
    if kalina:
        print(f"\nKALINA en {len(kalina)} punto(s):")
        for k in kalina:
            print(f"  P_baja={k['P_baja']:.1f} eta={k['eta']:.5f} "
                  f"Wnet={k['Wnet']:.2f} kW")


if __name__ == "__main__":
    main()
"""Fase 2, ronda 2 (tarea 2026-09-21-fase2-ronda2-pbaja) — rejilla P_baja alta.

Segunda ronda de exploracion de Fase 2: ancla FIJA T_fuente=470.0 K y
T_sumidero=300.032917 K, motor SOLO TeqpAdapter, y como palanca principal
P_baja (cruzada con x_b y eps_cond: las 3 variables que gobiernan el criterio
O2, causa de casi todos los CORREGIBLE de Fase 2 — ver sensibilidad_*.csv /
mapa_2d). T_amb_diseno=303.55 (mismo de toda Fase 2, BASE_LIBRE_v2.md).

La logica: subir P_baja eleva el punto de burbuja T_sat_L(P_baja, x_b), lo que
empuja el margen O2 = T_sat_L - T9_amb hacia positivo (CORREGIBLE -> KALINA)
sin tocar los rangos realistas ya usados (eta_t 0.80-0.90, eta_p 0.70-0.80,
eps_hrvg 0.80-0.95, eps_reg 0.70-0.85, eps_cond 0.80-0.95 — TASK punto 4).

Bloques (resto de variables en la base del repo: P_alta=3000, eta_t=0.85,
eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, m_b=1.0):
  A  x_b=0.50  P_baja {620,650,680,710,740} x eps_cond {0.90,0.93,0.95}
     -> x_b=0.50 quedo 100% CORREGIBLE hasta P_baja=600 (busqueda_libre_v2):
        se sube P_baja para cruzar la frontera O2.
  B  x_b=0.475 (NUNCA probada) P_baja {520,550,580,610,640,670} x eps {0.90,0.93,0.95}
  C  x_b=0.425 (NUNCA probada) P_baja {480,510,540,570}          x eps {0.90,0.93,0.95}
  D  x_b=0.45  afinado de frontera: P_baja {460,470,480,490,510,520}
     x eps_cond {0.91,0.93,0.95}  (v2 solo probo 450/500/550/600 con 0.80/0.85/0.90/0.95)
  E  x_b=0.35  huecos eps_cond {0.86,0.88,0.92} en P_baja {400,450,500}
  F  x_b=0.40  huecos eps_cond {0.87,0.92} en P_baja {550,600}
  G  P_alta {2800,3200} x {(0.50,650),(0.45,500)} con eps_cond=0.95
     (P_alta acompania, NO es la palanca prioritaria -> solo 4 puntos)

Anti-duplicado: lee TODOS los CSV de fase2_libre (incluido
mapa_2d_pbaja_epscond.csv, cuyos 8-tuplos se reconstruyen con el CENTRO
documentado en malla_2d_sensibilidad.py y se verifican por igualdad contra
busqueda_libre_v2.csv) y descarta toda candidata cuyo 8-tuplo (P_alta,
P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond) redondeado a 3
decimales ya exista.

Salida: APPEND a resultados/barridos_2026-09-19/fase2_libre/
busqueda_libre_v2.csv con el MISMO esquema de columnas del archivo real
(se lee la cabecera, no se asume). NO crea CSVs nuevos. NO toca src/.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.restricciones import evaluar_ciclo  # noqa: E402

T_AMB_DISENO = 303.55
BASE = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
            eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75)
CARPETA = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
CSV = CARPETA / "busqueda_libre_v2.csv"
VARS_ENTRADA = ("P_alta", "P_baja", "x_b", "eta_t", "eta_p",
                "eps_hrvg", "eps_reg", "eps_cond")
N_WORKERS = 4


def tupla(m) -> tuple:
    """8-tuplo de diseno, redondeado a 3 decimales (clave anti-duplicado)."""
    return tuple(round(float(m[v]), 3) for v in VARS_ENTRADA)


def leer_probadas() -> set:
    """Conjunto de 8-tuplos ya evaluados en TODOS los CSV de fase2_libre."""
    probadas: set = set()
    for f in sorted(CARPETA.glob("*.csv")):
        df = pd.read_csv(CARPETA / f.name)
        if f.name == "mapa_2d_pbaja_epscond.csv":
            # Ese CSV guarda solo (P_baja, eps_cond); la base es el CENTRO de
            # malla_2d_sensibilidad.py (x_b=0.40, resto BASE). Verificacion de
            # reconstruccion mas abajo: (400, 0.95, 0.40) duplica a v2.
            tuplas = [tupla(dict(BASE, x_b=0.40, P_baja=r.P_baja,
                                 eps_cond=r.eps_cond)) for _, r in df.iterrows()]
        else:
            if any(v not in df.columns for v in VARS_ENTRADA):
                continue  # anclas y demas sin las 11 variables -> no aplican
            tuplas = [tupla(r) for _, r in df.iterrows()]
        probadas.update(tuplas)
    t_ref = tupla(dict(BASE, x_b=0.40, P_baja=400.0, eps_cond=0.95))
    assert t_ref in probadas, "mapa_2d reconstruido no duplica a v2 (400/0.95/0.40)"
    return probadas


def rejilla_nueva() -> list:
    """80 candidatas; el filtro de duplicados descarta las que sobren."""
    def pts(xb: float, pbajas, econds) -> list:
        return [dict(BASE, x_b=xb, P_baja=pb, eps_cond=ec)
                for pb in pbajas for ec in econds]

    rej = (pts(0.50, (620.0, 650.0, 680.0, 710.0, 740.0), (0.90, 0.93, 0.95))
           + pts(0.475, (520.0, 550.0, 580.0, 610.0, 640.0, 670.0),
                 (0.90, 0.93, 0.95))
           + pts(0.425, (480.0, 510.0, 540.0, 570.0), (0.90, 0.93, 0.95))
           + pts(0.45, (460.0, 470.0, 480.0, 490.0, 510.0, 520.0),
                 (0.91, 0.93, 0.95))
           + pts(0.35, (400.0, 450.0, 500.0), (0.86, 0.88, 0.92))
           + pts(0.40, (550.0, 600.0), (0.87, 0.92)))
    for xb, pb, pa in ((0.50, 650.0, 2800.0), (0.50, 650.0, 3200.0),
                       (0.45, 500.0, 2800.0), (0.45, 500.0, 3200.0)):
        rej.append(dict(BASE, x_b=xb, P_baja=pb, P_alta=pa, eps_cond=0.95))
    return rej


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def resolver_punto(combo: dict) -> dict:
    """Resuelve + clasifica con TeqpAdapter y adjunta diagnostico O2 (worker)."""
    from src.components.condensador import resolver as resolver_cond
    backend = importar_backend()
    fila = dict(combo, T_sat_L=None, T9_amb=None, O2_margen=None)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:300])
        return fila
    val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                        P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                        T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                        m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    T_amb_evaluar = max(combo["T_sumidero"], T_AMB_DISENO)
    est9_amb, _ = resolver_cond(res["estados"]["e8"], backend,
                                T_sumidero=T_amb_evaluar,
                                eps=combo["eps_cond"], m=combo["m_b"])
    T_sat_L = backend.bubble_point(combo["P_baja"], combo["x_b"])
    fila.update(T_sat_L=T_sat_L, T9_amb=est9_amb.T, O2_margen=T_sat_L - est9_amb.T)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:300])
    return fila


def main() -> None:
    print("Anti-duplicado: leyendo TODOS los CSV de fase2_libre...", flush=True)
    probadas = leer_probadas()
    candidatas = rejilla_nueva()
    nuevas = [c for c in candidatas if tupla(c) not in probadas]
    n_desc = len(candidatas) - len(nuevas)
    print(f"  candidatas generadas: {len(candidatas)} | "
          f"descartadas por duplicado: {n_desc} | nuevas: {len(nuevas)}",
          flush=True)
    if not nuevas:
        print("Nada nuevo que correr.")
        return
    cabecera = list(pd.read_csv(CSV, nrows=0).columns) if CSV.exists() else [
        "T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
        "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
        "T_sat_L", "T9_amb", "O2_margen", "convergio", "clasificacion",
        "eta", "Wnet", "mensaje"]
    print(f"  Ronda 2: {len(nuevas)} puntos TeqpAdapter, ancla fija, "
          f"T_amb_diseno={T_AMB_DISENO} K, {N_WORKERS} workers; append a "
          f"{CSV.name} (columnas: {len(cabecera)}).", flush=True)
    t0 = time.perf_counter()
    filas: list = []
    primera = not CSV.exists()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, p) for p in nuevas]
        for n, fut in enumerate(as_completed(futuros), 1):
            filas.append(fut.result())
            if n % 10 == 0 or n == len(nuevas):
                tabla = pd.DataFrame(filas).reindex(columns=cabecera)
                tabla.to_csv(CSV, mode="a" if not primera else "w",
                             header=primera, index=False, encoding="utf-8")
                primera = False
                filas = []
                print(f"  {n}/{len(nuevas)} guardados "
                      f"({time.perf_counter() - t0:.0f} s)", flush=True)
    df = pd.read_csv(CSV)
    print(df["clasificacion"].value_counts().to_string(), flush=True)
    nuevas_df = df.tail(len(nuevas))
    kal = nuevas_df[nuevas_df["clasificacion"] == "KALINA"]
    if not kal.empty:
        ks = kal.sort_values("eta", ascending=False)
        print(f"KALINA nuevas: {len(kal)} "
              f"(rango P_baja {kal['P_baja'].min():.0f}-{kal['P_baja'].max():.0f})",
              flush=True)
        for _, r in ks.head(10).iterrows():
            print(f"  P_alta={r['P_alta']:.0f} P_baja={r['P_baja']:.0f} "
                  f"x_b={r['x_b']:.3f} eps_cond={r['eps_cond']:.2f} "
                  f"eta={r['eta']:.5f} O2_margen={r['O2_margen']:+.2f} K",
                  flush=True)
    else:
        print("Sin KALINA nuevas en esta rejilla.", flush=True)
    print(f"CSV completo: {CSV} ({len(df)} filas).", flush=True)


if __name__ == "__main__":
    main()
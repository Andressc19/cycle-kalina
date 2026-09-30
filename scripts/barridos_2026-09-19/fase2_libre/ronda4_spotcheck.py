"""Fase 2, ronda 4 (tarea 2026-09-29-fase2-ronda4-spotcheck-motor-real) —
spot-check con MOTOR REAL de los puntos de MENOR margen O2.

La ronda 4 (613 filas al final de busqueda_libre_v2.csv) corrio solo con
TeqpAdapter. Aqui se toman sus filas `clasificacion=KALINA` con menor
`|O2_margen|` (las mas cerca del filo de la frontera O2) y se re-resuelven con
`AmmoniaWaterAdapter` (IAPWS G4-01), comparando clasificacion y eta contra el
CSV. NO es un barrido nuevo: no se agrega ninguna fila a busqueda_libre_v2.csv
ni a ningun otro CSV. Todo sale a fase2_libre/spotcheck_ronda4_motor_real.json,
con checkpoint por punto (leccion de la sensibilidad final de Fase 2).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

# `comun_sensibilidad.resolver_punto(combo, factory)` ya hace lo pedido:
# `resolver_ciclo` + `evaluar_ciclo` + margenes O1/O2/S5/O5 con el backend que
# se le pase. Se carga por ruta (la carpeta lleva guiones) y se registra en
# sys.modules para que el pool con spawn lo pueda despicklear.
_CARPETA = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "comun_sensibilidad", _CARPETA / "comun_sensibilidad.py")
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)
sys.modules.setdefault("comun_sensibilidad", comun)

FASE2 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
CSV = FASE2 / "busqueda_libre_v2.csv"
JSON_OUT = FASE2 / "spotcheck_ronda4_motor_real.json"
N_PREVIAS = 184            # filas de las rondas 1-3 conservadas al principio
N_SPOT = 10                # tope de puntos con motor real (TASK: 8-10)
N_WORKERS = 4
VARS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
        "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")


def _worker(combo: dict) -> dict:
    """Un punto con el motor REAL (worker de proceso).

    try/except ABIERTO alrededor de TODA la llamada: `resolver_punto` solo
    protege el `resolver_ciclo`; el diagnostico posterior (`evaluar_ciclo`,
    `fase_de`, `bubble_point`, condensador con T_amb) tambien puede lanzar
    `PropertyRangeError` cerca de la frontera, y ahi la excepcion SUBE por el
    pipe y tumba la tanda entera. Todo punto se registra, converja o no.
    """
    try:
        return comun.resolver_punto(combo, comun.importar_real)
    except Exception as exc:                                   # noqa: BLE001
        m = f"{type(exc).__name__}: {exc}"[:300]     # `registro` usa .get()
        return dict(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, margen_O2=None, mensaje=m)


def combo_de(fila) -> dict:
    """Los 11 parametros de entrada, tal cual estan en la fila del CSV."""
    return {v: float(fila[v]) for v in VARS}


def cargar() -> tuple:
    """(df completo, ronda 4 = filas posteriores a las 184 previas)."""
    df = pd.read_csv(CSV)
    assert len(df) > N_PREVIAS, "el CSV crecio por debajo de las 184 previas"
    previas = df.iloc[:N_PREVIAS]
    assert (previas["eps_hrvg"] == 0.85).all() and (previas["eps_reg"] == 0.75).all(), \
        "las filas previas ya no son las de las rondas 1-3 (se perdio el orden)"
    return df, df.iloc[N_PREVIAS:].copy()


def candidatos(camp: pd.DataFrame) -> list:
    """KALINA de la ronda 4 ordenados por |O2_margen| creciente (el filo)."""
    k = camp[(camp["clasificacion"] == "KALINA")
             & camp["O2_margen"].notna()].copy()
    k["_absO2"] = k["O2_margen"].abs()
    return list(k.sort_values("_absO2").head(N_SPOT).iterrows())


def cerca_del_filo(camp: pd.DataFrame, n: int = 5) -> list:
    """CORREGIBLE de la ronda 4 mas cerca del filo (O2_margen mas alto < 0).

    NO se re-resuelven con motor real (el TASK prioriza KALINA y topa el
    presupuesto en 8-10): se documentan tal cual, para que se vea que el filo
    tambien esta apretado por el lado fallido.
    """
    c = camp[(camp["clasificacion"] == "CORREGIBLE")
             & camp["O2_margen"].notna()].copy()
    c = c.sort_values("O2_margen", ascending=False).head(n)
    return [dict(fila_csv=i, combo=combo_de(r),
                 teqp=dict(clasificacion=r["clasificacion"], eta=float(r["eta"]),
                           O2_margen=float(r["O2_margen"])))
            for i, r in c.iterrows()]


def registro(idx, fila, real: dict) -> dict:
    """Punto completo: entradas, Teqp (del CSV), motor real y veredicto."""
    comb = combo_de(fila)
    teqp = dict(clasificacion=str(fila["clasificacion"]),
                eta=float(fila["eta"]), Wnet=float(fila["Wnet"]),
                T_sat_L=float(fila["T_sat_L"]), T9_amb=float(fila["T9_amb"]),
                O2_margen=float(fila["O2_margen"]))
    conv, rc = bool(real.get("convergio")), real.get("clasificacion")
    coincide = conv and rc == teqp["clasificacion"]
    eta_real, o2_real = real.get("eta"), real.get("margen_O2")
    veredicto = ("COINCIDE" if coincide
                 else "DIFIERE" if conv else "NO_CONVERGIO_MOTOR_REAL")
    return dict(
        fila_csv=idx, linea_csv=int(idx) + 2,      # +2: cabecera + base 0
        combo=comb, teqp=teqp,
        real=dict(convergio=conv, clasificacion=rc, eta=eta_real,
                  Wnet=real.get("Wnet"), O2_margen=o2_real,
                  T_sat_L=real.get("T_sat_L"), T9_amb=real.get("T9_amb"),
                  q4=real.get("q4"), margen_O1=real.get("margen_O1"),
                  criterio_ligante=real.get("criterio_ligante"),
                  margen_ligante=real.get("margen_ligante"),
                  mensaje=(real.get("mensaje") or "")[:300]),
        coincide_clasificacion=bool(coincide), veredicto=veredicto,
        delta_O2_margen=(None if o2_real is None
                         else round(o2_real - teqp["O2_margen"], 4)),
        delta_eta=(None if not conv or eta_real is None
                   else round(eta_real - teqp["eta"], 6)))


def _volcar(puntos: list, extra: dict) -> None:
    """Vuelca el JSON completo (idempotente: se puede reentrar)."""
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(extra, puntos=puntos), fh, indent=2, ensure_ascii=False)


def main() -> None:
    df, camp = cargar()
    sel = candidatos(camp)
    filo = cerca_del_filo(camp)
    extra = dict(
        tarea="2026-09-29-fase2-ronda4-spotcheck-motor-real",
        fuente=f"{CSV.name}, filas {N_PREVIAS + 2}-{len(df) + 1} = {len(camp)} "
               f"puntos ronda 4 (las {N_PREVIAS} previas son rondas 1-3)",
        motor_real="AmmoniaWaterAdapter (iapws.ammonia.H2ONH3, IAPWS G4-01)",
        motor_csv="TeqpAdapter", T_amb_diseno=comun.T_AMB_DISENO,
        n_previas=N_PREVIAS, n_ronda4=int(len(camp)),
        n_kalina_ronda4=int((camp["clasificacion"] == "KALINA").sum()),
        seleccion="clasificacion=KALINA por |O2_margen| creciente",
        cerca_del_filo_corregible_no_verificados=filo)
    print(f"Ronda 4: {len(camp)} filas | KALINA: {extra['n_kalina_ronda4']} | "
          f"motor real: {len(sel)} pts | T_amb={comun.T_AMB_DISENO} K", flush=True)
    for i, r in sel:
        print(f"  fila {i} (linea {int(i) + 2}): Pa={r['P_alta']:.0f} "
              f"Pb={r['P_baja']:.3f} x_b={r['x_b']:.3f} eta_t={r['eta_t']:.2f} "
              f"eta_p={r['eta_p']:.2f} eps=({r['eps_hrvg']:.2f},"
              f"{r['eps_reg']:.2f},{r['eps_cond']:.2f}) "
              f"O2_margen={r['O2_margen']:+.4f} K eta={r['eta']:.5f}", flush=True)
    puntos: list = []
    if JSON_OUT.exists():                       # reentrada: no repetir lo hecho
        try:
            puntos = json.loads(JSON_OUT.read_text(encoding="utf-8"))["puntos"]
        except (json.JSONDecodeError, OSError, KeyError):
            puntos = []
    sel = [(i, r) for i, r in sel if i not in {p["fila_csv"] for p in puntos}]
    if not sel:
        print("Los puntos seleccionados ya estaban verificados; no se repite.",
              flush=True)
        _volcar(puntos, extra)
        return
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futs = {pool.submit(_worker, combo_de(r)): i for i, r in sel}
        for n, fut in enumerate(as_completed(futs), 1):
            i = futs[fut]
            reg = registro(i, df.loc[i], fut.result())
            puntos.append(reg)
            puntos.sort(key=lambda p: abs(p["teqp"]["O2_margen"]))
            _volcar(puntos, extra)             # checkpoint por punto
            print(f"  [{n}/{len(sel)}] fila {i}: teqp={reg['teqp']['clasificacion']} "
                  f"-> real={reg['real']['clasificacion']} [{reg['veredicto']}] "
                  f"dO2={reg['delta_O2_margen']} dEta={reg['delta_eta']}", flush=True)
    print(f"  {len(sel)} puntos motor real en {time.perf_counter() - t0:.0f} s de "
          f"pared ({N_WORKERS} workers)", flush=True)
    n = {v: sum(1 for p in puntos if p["veredicto"] == v)
         for v in ("COINCIDE", "DIFIERE", "NO_CONVERGIO_MOTOR_REAL")}
    _volcar(puntos, dict(extra, resumen=dict(
        n=len(puntos), coinciden=n["COINCIDE"], difieren=n["DIFIERE"],
        no_convergio_motor_real=n["NO_CONVERGIO_MOTOR_REAL"],
        quedan_KALINA_solo_teqp=n["DIFIERE"] + n["NO_CONVERGIO_MOTOR_REAL"],
        segundos_pared=round(time.perf_counter() - t0, 1))))
    print(f"COINCIDE {n['COINCIDE']} | DIFIERE {n['DIFIERE']} | "
          f"NO_CONVERGIO real {n['NO_CONVERGIO_MOTOR_REAL']}")
    print(f"Guardado {JSON_OUT}")


if __name__ == "__main__":
    main()

"""Fase 2, ronda 6 (tarea 2026-09-29-fase2-ronda6-tfuente-libre-xb-alto) — spot-
check con MOTOR REAL de los KALINA de la ronda, leccion obligatoria del TASK.

Selecciona de `ronda6_diagnostico.csv` los puntos `clasificacion=KALINA` con MENOR
margen COMBINADO y los re-resuelve con `AmmoniaWaterAdapter` (IAPWS G4-01),
comparando clasificacion/eta contra Teqp. Como O1 va en fraccion de titulo y O2 en
kelvin, el "margen combinado" se normaliza con `comun_sensibilidad.UMBRALES_SPOT`
(O1 0.02, O2/S5 2.0): score = min(margen_X / umbral_X) sobre O1/O2/S5.

DIFERENCIA CRITICA con la ronda 5: `T_fuente` NO es un ancla fija de 470 K — es la
variable de esta ronda y sale de cada fila del companion (que si lo guarda). Solo
`T_sumidero` y `m_b` se reinyectan como anclas del TASK (reglas 1 y 10). Ademas se
conserva el contexto del FILTRO DE CAMPANA (T_bub, T_dew, estado_filtro) para que
el veredicto se pueda auditar contra la fisica de la campana.

NO es un barrido nuevo: no se agrega ninguna fila a busqueda_libre_v2.csv ni al
companion. Todo sale a `spotcheck_ronda6_motor_real.json`, con checkpoint por punto.
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

_CARPETA = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "comun_sensibilidad", _CARPETA / "comun_sensibilidad.py")
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)
sys.modules.setdefault("comun_sensibilidad", comun)

FASE2 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
DIAG = FASE2 / "ronda6_diagnostico.csv"
JSON_OUT = FASE2 / "spotcheck_ronda6_motor_real.json"
N_SPOT = 8                 # TASK: 5-8 puntos KALINA de menor margen O1/O2
N_WORKERS = 4
ETA_OBJETIVO = 0.1242887803299733   # mejor eta historico; referencia deeln TASK
# Anclas fijas del TASK (regla 1 y regla 10); el companion no las guarda.
ANCLAS = dict(T_sumidero=300.032917, m_b=1.0)
VARS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
        "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
NORM = comun.UMBRALES_SPOT


def _worker(combo: dict) -> dict:
    """Un punto con el motor REAL. try/except ABIERTO: todo se registra."""
    try:
        return comun.resolver_punto(combo, comun.importar_real)
    except Exception as exc:                                   # noqa: BLE001
        return dict(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, margen_O2=None, margen_O1=None,
                    mensaje=f"{type(exc).__name__}: {exc}"[:300])


def combo_de(fila) -> dict:
    """Los 11 parametros de entrada, anclas fijas incluidas.

    `T_fuente` viene de la fila (es la variable de la ronda 6, no un ancla).
    """
    return dict({v: float(fila[v]) for v in VARS if v in fila}, **ANCLAS)


def _score(fila) -> float:
    """min(margen_O1/0.02, margen_O2/2, margen_S5/2): menor score, mas al filo."""
    return min(float(fila["margen_O1"]) / NORM["O1"],
               float(fila["margen_O2"]) / NORM["O2"],
               float(fila["margen_S5"]) / NORM["S5"])


def candidatos(d: pd.DataFrame) -> list:
    """KALINA de la ronda 6 por score combinado O1/O2/S5 normalizado ascendente."""
    k = d[(d["clasificacion"] == "KALINA") & d["margen_O2"].notna()].copy()
    k["_score"] = k.apply(_score, axis=1)
    return list(k.sort_values("_score").head(N_SPOT).iterrows())


def registro(idx, fila, real: dict) -> dict:
    """Punto completo: entradas, Teqp (companion), motor real y veredicto."""
    comb = combo_de(fila)
    teqp = dict(clasificacion=str(fila["clasificacion"]),
                eta=float(fila["eta"]), margen_O1=float(fila["margen_O1"]),
                margen_O2=float(fila["margen_O2"]),
                margen_S5=float(fila["margen_S5"]), q4=float(fila["q4"]))
    conv, rc = bool(real.get("convergio")), real.get("clasificacion")
    eta_real, o2_real = real.get("eta"), real.get("margen_O2")
    veredicto = ("COINCIDE" if conv and rc == teqp["clasificacion"]
                 else "DIFIERE" if conv else "NO_CONVERGIO_MOTOR_REAL")
    return dict(
        fila_diag=int(idx), combo=comb, teqp=teqp,
        filtro=dict(T_bub=fila.get("T_bub"), T_dew=fila.get("T_dew"),
                    estado_filtro=fila.get("estado_filtro")),
        real=dict(convergio=conv, clasificacion=rc, eta=eta_real,
                  Wnet=real.get("Wnet"), margen_O1=real.get("margen_O1"),
                  margen_O2=o2_real, q4=real.get("q4"),
                  T_sat_L=real.get("T_sat_L"), T9_amb=real.get("T9_amb"),
                  criterio_ligante=real.get("criterio_ligante"),
                  margen_ligante=real.get("margen_ligante"),
                  mensaje=(real.get("mensaje") or "")[:300]),
        coincide_clasificacion=bool(conv and rc == teqp["clasificacion"]),
        veredicto=veredicto,
        delta_O2_margen=(None if o2_real is None
                         else round(float(o2_real) - teqp["margen_O2"], 4)),
        delta_eta=(None if not conv or eta_real is None
                   else round(float(eta_real) - teqp["eta"], 6)))


def _volcar(puntos: list, extra: dict) -> None:
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(extra, puntos=puntos), fh, indent=2, ensure_ascii=False)


def main() -> None:
    df = pd.read_csv(DIAG)
    sel = candidatos(df)
    n_kalina = int((df["clasificacion"] == "KALINA").sum())
    extra = dict(
        tarea="2026-09-29-fase2-ronda6-tfuente-libre-xb-alto",
        fuente=f"{DIAG.name} (companion ronda 6, {len(df)} puntos)",
        motor_real="AmmoniaWaterAdapter (iapws.ammonia.H2ONH3, IAPWS G4-01)",
        motor_companion="TeqpAdapter", T_amb_diseno=comun.T_AMB_DISENO,
        seleccion="KALINA por min(margen_O1/0.02, margen_O2/2, margen_S5/2)",
        nota_T_fuente="T_fuente LIBRE por ronda (no es el ancla de 470 K de la r5)",
        eta_objetivo_historico=ETA_OBJETIVO, n_kalina_ronda6=n_kalina)
    print(f"Ronda 6: {len(df)} filas | KALINA: {n_kalina} | motor real: "
          f"{len(sel)} pts | T_amb={comun.T_AMB_DISENO} K", flush=True)
    if n_kalina:
        mejor = df[df["clasificacion"] == "KALINA"]["eta"].max()
        print(f"  mejor eta KALINA de la ronda: {float(mejor):.6f} "
              f"(objetivo historico {ETA_OBJETIVO:.6f})", flush=True)
    for i, r in sel:
        print(f"  fila {i}: Tf={r['T_fuente']:.0f} Pa={r['P_alta']:.0f} "
              f"Pb={r['P_baja']:.1f} x_b={r['x_b']:.3f} "
              f"eps_cond={r['eps_cond']:.2f} mO1={r['margen_O1']:+.4f} "
              f"mO2={r['margen_O2']:+.3f} eta={r['eta']:.5f}", flush=True)
    puntos: list = []
    if JSON_OUT.exists():
        try:
            puntos = json.loads(JSON_OUT.read_text(encoding="utf-8"))["puntos"]
        except (json.JSONDecodeError, OSError, KeyError):
            puntos = []
    hechos = {p["fila_diag"] for p in puntos}
    sel = [(i, r) for i, r in sel if i not in hechos]
    if not sel:
        print("Los puntos ya estaban verificados; no se repite.", flush=True)
        _volcar(puntos, extra)
        return
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futs = {pool.submit(_worker, combo_de(r)): i for i, r in sel}
        for n, fut in enumerate(as_completed(futs), 1):
            i = futs[fut]
            reg = registro(i, df.loc[i], fut.result())
            puntos.append(reg)
            puntos.sort(key=lambda p: abs(p["teqp"]["margen_O2"]))
            _volcar(puntos, extra)
            print(f"  [{n}/{len(sel)}] fila {i}: teqp={reg['teqp']['clasificacion']}"
                  f" -> real={reg['real']['clasificacion']} [{reg['veredicto']}] "
                  f"dO2={reg['delta_O2_margen']} dEta={reg['delta_eta']}", flush=True)
    n = {v: sum(1 for p in puntos if p["veredicto"] == v)
         for v in ("COINCIDE", "DIFIERE", "NO_CONVERGIO_MOTOR_REAL")}
    etas = [p["real"]["eta"] for p in puntos
            if p["veredicto"] == "COINCIDE" and p["real"]["eta"] is not None]
    _volcar(puntos, dict(extra, resumen=dict(
        n=len(puntos), coinciden=n["COINCIDE"], difieren=n["DIFIERE"],
        no_convergio_motor_real=n["NO_CONVERGIO_MOTOR_REAL"],
        quedan_KALINA_solo_teqp=n["DIFIERE"] + n["NO_CONVERGIO_MOTOR_REAL"],
        mejor_eta_motor_real=(None if not etas else float(max(etas))),
        segundos_pared=round(time.perf_counter() - t0, 1))))
    print(f"COINCIDE {n['COINCIDE']} | DIFIERE {n['DIFIERE']} | "
          f"NO_CONVERGIO real {n['NO_CONVERGIO_MOTOR_REAL']}")
    print(f"Guardado {JSON_OUT}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
r"""Sens2 etapa B - corredor reanudable de los puntos DENS (`s2b_puntos_dens.py`), con columnas de densidad y caudal volumetrico.

Igual que `s2b_corrida.py`, pero la salida es `s2b_dens_filas.csv` y cada fila convergida lleva las columnas de `s2b_dens.densidades`.
Uso:  ..\..\..\.venv\Scripts\python.exe scripts\sens2\s2b_corrida_dens.py DENS     (relanzar reanuda)
"""
import os
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR), str(_DIR.parents[0] / "sens1")]
import ronda3_corrida as R  # noqa: E402
import s2b_puntos_dens as P  # noqa: E402

OUT = _DIR.parents[1] / "resultados" / "2026-10-18_sens2_B"
DENS_COLS = ["xv_sep", "xl_sep", "fase4", "q4_dens", "rho3", "rho4", "rho9", "V3_m3s", "V4_m3s", "V9_m3s", "H_bomba_m", "RV_turb"]
R.OUT = OUT
R.FILAS = OUT / "s2b_dens_filas.csv"
R.tareas_r3 = P.tareas
R.BARRIDOS_CLI = P.BARRIDOS_CLI
R.N_WORKERS = int(os.environ.get("S2B_WORKERS", "5"))
R.LIMITE_S = float(os.environ.get("S2B_LIMITE", "600"))
R.CM = list(R.CM) + DENS_COLS


def _worker(conn, t):
    """UN punto; calcula ademas las densidades si convergio. Corre en un hijo."""
    import comun
    try:
        f = comun.evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"], t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
        f.update({k: t.get(k) for k in R.META})
        if f.get("clasificacion") in ("KALINA", "CORREGIBLE") and f.get("m_v") not in (None, ""):
            try:
                import s2b_dens
                from src.properties.teqp_adapter import TeqpAdapter
                f.update(s2b_dens.densidades(f, TeqpAdapter(x=float(f["x_b"]))))
            except BaseException as exc:                       # noqa: BLE001
                f["mensaje"] = ("%s | dens: %s: %s" % (f.get("mensaje") or "", type(exc).__name__, exc))[:300]
    except BaseException as exc:                               # noqa: BLE001
        f = R.fila_base(t)
        f["mensaje"] = f"error_worker: {type(exc).__name__}: {exc}"[:300]
        f["error_inesperado"] = f["mensaje"]
    try:
        conn.send(f)
    finally:
        conn.close()


R._worker = _worker

if __name__ == "__main__":
    R.main(sys.argv)

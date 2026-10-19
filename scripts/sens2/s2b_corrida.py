# -*- coding: utf-8 -*-
"""Sens2 etapa B - corredor reanudable (un proceso por punto) de `s2b_puntos.py`.

Reutiliza el corredor de `scripts/sens1/ronda3_corrida.py` (N_WORKERS procesos, escritura incremental, salta los `id_punto` ya
escritos). Presupuesto del resolutor y tope duro por punto desde las variables de entorno S2B_PRESUPUESTO (s, defecto 300) y
S2B_LIMITE (s, defecto 600). Uso:
    ..\\..\\..\\.venv\\Scripts\\python.exe scripts\\sens2\\s2b_corrida.py REINT0|PISOS|all
Relanzar el mismo comando reanuda.
"""
import os
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR), str(_DIR.parents[0] / "sens1")]
import ronda3_corrida as R  # noqa: E402
import s2b_puntos as P  # noqa: E402

OUT = _DIR.parents[1] / "resultados" / "2026-10-18_sens2_B"
R.OUT = OUT
R.FILAS = OUT / "s2b_filas.csv"
R.tareas_r3 = P.tareas
R.BARRIDOS_CLI = P.BARRIDOS_CLI
R.N_WORKERS = int(os.environ.get("S2B_WORKERS", "5"))
R.LIMITE_S = float(os.environ.get("S2B_LIMITE", "600"))


def _worker(conn, t):
    """UN punto con el presupuesto pedido; corre en un hijo (igual que `R._worker`)."""
    import comun
    comun.PRESUPUESTO_S = float(os.environ.get("S2B_PRESUPUESTO", "300"))
    try:
        f = comun.evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"], t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
        f.update({k: t.get(k) for k in R.META})
    except BaseException as exc:                       # noqa: BLE001
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

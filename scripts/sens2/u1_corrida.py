# -*- coding: utf-8 -*-
"""Sens2 U1 - corredor reanudable de la propagacion de incertidumbre (un proceso por punto).

Reutiliza el corredor de `scripts/sens1/ronda3_corrida.py` (5 procesos, tope duro de 600 s, escritura
incremental, salta los `id_punto` ya escritos) con los puntos de `u1_puntos.py`. Uso:
    ..\\..\\..\\.venv\\Scripts\\python.exe scripts\\sens2\\u1_corrida.py U1A|U1B|all
Relanzar el mismo comando reanuda.
"""
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR), str(_DIR.parents[0] / "sens1")]
import ronda3_corrida as R  # noqa: E402
import u1_puntos as U  # noqa: E402

OUT = _DIR.parents[1] / "resultados" / "2026-10-17_sens2_U1"
R.OUT = OUT
R.FILAS = OUT / "u1_filas.csv"
R.tareas_r3 = U.tareas
R.BARRIDOS_CLI = U.BARRIDOS_CLI

if __name__ == "__main__":
    R.main(sys.argv)

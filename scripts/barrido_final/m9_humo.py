"""M9 — humo: corre el flujo completo con `M9_HUMO=1`.

Pone `M9_HUMO=1` en el entorno y delega en `m9_main.py`: 2 puntos por escenario
del paso 1, 2 P_baja de Húsavík, 2 rondas del paso 2 y salida en
`resultados/2026-10-08_final_M9/humo/`. NO toca el Excel final (ver `m9_main.py`).
"""
from __future__ import annotations

import os, sys  # noqa: E401,E402
from pathlib import Path

os.environ["M9_HUMO"] = "1"
_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR)]

import m9_main  # noqa: E402

if __name__ == "__main__":
    m9_main.main()

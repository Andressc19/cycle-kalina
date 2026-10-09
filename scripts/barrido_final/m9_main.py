"""M9 — corrida completa: paso 0/3 → 1 → 2 → 4 → 5 (final_M9 §Pasos).

Lanza cada script como subproceso con el Python que ejecuta este archivo, en
orden, y se detiene si alguno falla. Con `M9_HUMO=1` corre en
`resultados/2026-10-08_final_M9/humo/` y OMITE la cadena de Excel (para no
escribir filas de humo en `datos/Excel_final_kalina.xlsx`). Pensado para
lanzarse EN PRIMER PLANO con `timeout` de la herramienta shell de 14400000 ms.
"""
from __future__ import annotations

import os, subprocess, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
PY = sys.executable
PASOS = ["m9_corrida.py", "m9_paso1.py", "m9_paso2.py", "m9_analisis.py",
         "m9_figuras.py", "m9_verificar.py"]
EXCEL = ["excel_final.py", "excel_m2.py", "excel_m3_m2r.py", "excel_m2s_m4.py",
         "excel_m5.py", "excel_m5c_m7_m8.py", "excel_m6.py", "excel_m9.py",
         "verificar_excel_m9.py"]


def corre(script: str) -> int:
    """Ejecuta un script en primer plano y devuelve su código de salida."""
    print(f"\n===== {script} =====", flush=True)
    return subprocess.run([PY, str(_DIR / script)], cwd=str(_DIR)).returncode


def main() -> None:
    for s in PASOS:
        if corre(s):
            sys.exit(f"FALLÓ {s}")
    if os.environ.get("M9_HUMO") == "1":
        print("\nHUMO: se omite la cadena de Excel y su verificación.", flush=True)
        return
    for s in EXCEL:
        if corre(s):
            sys.exit(f"FALLÓ {s}")


if __name__ == "__main__":
    main()

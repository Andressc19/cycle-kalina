"""Etapa 2: el solver del PROYECTO en los mismos 6 puntos, con los dos motores.

`resolver_ciclo` (src/cycle_solver.py, sin tocar) con:
  - `AmmoniaWaterAdapter` (motor real portado, IAPWS G4-01) ~5 min/punto
  - `TeqpVerificado` (teqp + respaldo del motor en la zona de riesgo) ~30 s/punto

Una fila por (punto, motor) en `motor_puntos.csv`, con `flush` tras cada fila:
si el CSV ya tiene la fila, no se recalcula (corrida reanudable).

Uso (desacoplado):  nohup .venv/Scripts/python -u scripts/dwsim/motor_puntos_validacion.py \
                        > resultados/2026-10-03_validacion_dwsim/motor_consola.txt 2>&1 &
"""
from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.cycle_solver import resolver_ciclo                    # noqa: E402
from src.properties.ammonia_water_adapter import (              # noqa: E402
    AmmoniaWaterAdapter)
from src.properties.teqp_verificado import TeqpVerificado      # noqa: E402

OUT = REPO / "resultados" / "2026-10-03_validacion_dwsim"
CSV = OUT / "motor_puntos.csv"
# (etiqueta, x_b, P_alta kPa, T_fuente K, P_baja kPa, T_sumidero K, eps x3)
PUNTOS = [
    ("ELSAYED", 0.55, 1500.0, 373.0, 273.5454214157179, 283.0,
     (0.8882023116022899, 0.9380325550010874, 0.9625029043677631)),
    ("KALINA-11", 0.65, 5000.0, 423.0, 704.644595, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-22", 0.80, 5000.0, 394.0, 952.892781, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-21", 0.80, 4000.0, 394.0, 1101.510788, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-01", 0.60, 3000.0, 394.0, 523.749936, 283.0, (0.85, 0.80, 0.85)),
    ("KALINA-16", 0.70, 5000.0, 423.0, 890.811268, 283.0, (0.85, 0.80, 0.85)),
]
M_B, ETA_T, ETA_P, T_SUMIDERO = 1.0, 0.80, 0.80, 283.0
MOTORES = [("teqp", TeqpVerificado), ("real", AmmoniaWaterAdapter)]
CAMPOS = ["motor", "etiqueta", "x_b", "P_alta", "T_fuente", "P_baja",
          "T_sumidero", "eps_hrvg", "eps_reg", "eps_cond", "convergio",
          "eta", "Wnet", "Qi", "Wt", "Wp", "Qout", "tiempo_s"]
CAMPOS += ["T%d" % k for k in range(1, 11)] + ["x3", "x5", "m3", "m5", "error"]


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def fila(base, motor, res, dt, error=""):
    f = dict(base, motor=motor, convergio=not error,
             tiempo_s=round(dt, 2), error=error)
    if error:
        f.update({k: "" for k in CAMPOS if k not in f})
        return f
    e = res["estados"]
    f.update(eta=round(res["eta"], 9), Wnet=round(res["Wnet"], 6),
             Qi=round(res["Qi"], 6), Wt=round(res["Wt"], 6),
             Wp=round(res["Wp"], 6), Qout=round(res["Qout"], 6))
    for k in range(1, 11):
        f["T%d" % k] = round(e["e%d" % k].T, 5)
    f.update(x3=round(e["e3"].x, 9), x5=round(e["e5"].x, 9),
             m3=round(e["e3"].m, 8), m5=round(e["e5"].m, 8))
    return f


def ya_hechas():
    if not CSV.exists():
        return set()
    with open(CSV, newline="", encoding="utf-8") as fh:
        return {(r["motor"], r["etiqueta"]) for r in csv.DictReader(fh)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    nuevo = not CSV.exists()
    hechas = ya_hechas()
    fh = open(CSV, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(fh, fieldnames=CAMPOS)
    if nuevo:
        w.writeheader()
        fh.flush()
    log("ETAPA 2: resolver_ciclo con %s" % ", ".join(m for m, _ in MOTORES))
    log("  puntos ya en el CSV: %d" % len(hechas))
    for motor, cls in MOTORES:                    # teqp (rapido) y luego real
        for et, x_b, Pa, Tf, Pb, Ts, eps in PUNTOS:
            if (motor, et) in hechas:
                log("  %-9s ya resuelto -> no se recalcula" % et)
                continue
            base = dict(etiqueta=et, x_b=x_b, P_alta=Pa, T_fuente=Tf,
                        P_baja=Pb, T_sumidero=Ts, eps_hrvg=eps[0],
                        eps_reg=eps[1], eps_cond=eps[2])
            log("  %-6s %-9s x_b=%.2f P=%.1f/%.4f T=%.0f/%.0f ..."
                % (motor, et, x_b, Pa, Pb, Tf, Ts))
            t0 = time.perf_counter()
            try:
                res = resolver_ciclo(
                    cls(x=x_b), P_alta=Pa, P_baja=Pb, T_fuente=Tf,
                    T_sumidero=T_SUMIDERO, x_b=x_b, m_b=M_B, eta_t=ETA_T,
                    eta_p=ETA_P, eps_hrvg=eps[0], eps_reg=eps[1],
                    eps_cond=eps[2])
                f = fila(base, motor, res, time.perf_counter() - t0)
                log("    eta=%.6f (%.3f %%)  Wnet=%.4f kW  %.1f s"
                    % (res["eta"], res["eta"] * 100.0, res["Wnet"],
                       time.perf_counter() - t0))
            except Exception as exc:             # fallo real, documentado
                f = fila(base, motor, None, time.perf_counter() - t0,
                         error=("%s: %s" % (type(exc).__name__, exc))[:180])
                log("    FALLO: %s" % f["error"])
            w.writerow(f)
            fh.flush()                            # reanudable
    fh.close()
    log("LISTO -> %s" % CSV.relative_to(REPO))


if __name__ == "__main__":
    main()
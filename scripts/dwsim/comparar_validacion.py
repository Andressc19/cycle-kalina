"""Etapa 3 de la validación cruzada (TASK_CONTEXT_validacion_dwsim.md).

Une `motor_puntos.csv` (solver del proyecto: motor real y teqp) con `dwsim_puntos.csv`
(DWSIM-PR, mismo cierre por efectividad) y escribe `comparacion.csv`: por punto y
magnitud, los tres valores y las diferencias teqp − real y DWSIM − real (absolutas y
relativas). No compara entalpías absolutas (cada modelo tiene su estado de
referencia): solo trabajos, calores, η, temperaturas, composiciones y caudales.
Solo stdlib: corre con cualquier Python.
"""
import csv
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "resultados", "2026-10-03_validacion_dwsim")
MAGNITUDES = (["eta", "Wnet", "Qi", "Wt", "Wp", "Qout"]
              + ["T%d" % k for k in range(1, 11)] + ["x3", "x5", "m3", "m5"])
ORDEN = ["ELSAYED", "KALINA-11", "KALINA-22", "KALINA-21", "KALINA-01", "KALINA-16"]


def _leer(nombre):
    with open(os.path.join(OUT, nombre), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def main():
    motor = {(r["etiqueta"], r["motor"]): r for r in _leer("motor_puntos.csv")}
    dw = {r["etiqueta"]: r for r in _leer("dwsim_puntos.csv")}
    filas = []
    for et in ORDEN:
        real, teqp, d = motor.get((et, "real")), motor.get((et, "teqp")), dw.get(et)
        if not (real and teqp and d) or d["convergio"] != "True":
            print("omitido %s: DWSIM no convergio (%s)" % (et, (d or {}).get("error", "sin fila")[:90]))
            continue
        for m in MAGNITUDES:
            vr, vt, vd = _f(real[m]), _f(teqp[m]), _f(d[m])
            filas.append(dict(
                etiqueta=et, magnitud=m, real=vr, teqp=vt, dwsim=vd,
                teqp_menos_real=vt - vr, dwsim_menos_real=vd - vr,
                teqp_rel=(vt - vr) / vr if vr else float("nan"),
                dwsim_rel=(vd - vr) / vr if vr else float("nan"),
                dwsim_convergio=d["convergio"]))
    with open(os.path.join(OUT, "comparacion.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print("%-10s %9s %9s %9s %11s %11s" % ("punto", "eta_real", "eta_teqp", "eta_DWSIM",
                                           "teqp-real", "DWSIM-real"))
    for f in filas:
        if f["magnitud"] == "eta":
            print("%-10s %8.4f%% %8.4f%% %8.4f%% %+9.4f pp %+9.3f pp" % (
                f["etiqueta"], 100 * f["real"], 100 * f["teqp"], 100 * f["dwsim"],
                100 * f["teqp_menos_real"], 100 * f["dwsim_menos_real"]))
    print("-> %s" % os.path.join(OUT, "comparacion.csv"))


if __name__ == "__main__":
    main()

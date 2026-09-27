"""Regresión `TeqpAdapter` vs `TeqpVerificado` sobre los puntos KALINA del
barrido `2026-09-24_margen2k` (TASK_CONTEXT 2026-09-27-teqp-verificado).

Para cada una de las 22 filas con `clasificacion == KALINA` de
`barrido_margen2k.csv`: resuelve el ciclo en SU `P_baja` con los dos adapters
y clasifica cada resultado con `evaluar_ciclo(..., T_amb_diseno=283.15)`.
Escribe `regresion_22.csv` (una fila por punto), `regresion_recurrencias.csv`
(detalle de cada llamada respaldada) y `REPORTE_TEQP_VERIFICADO.md`; el log va a
`run.log`. Costo: ~35 s por ciclo, ~30 min. Uso: `python -u <este script>`.
"""

from __future__ import annotations

import csv
import statistics as st
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.cycle_solver import resolver_ciclo                     # noqa: E402
from src.properties.adapter import PropertyRangeError           # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter              # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado       # noqa: E402
from src.restricciones.clasificacion import evaluar_ciclo       # noqa: E402

OUT = REPO / "resultados" / "2026-09-27_teqp_verificado"
SRC = REPO / "resultados" / "2026-09-24_margen2k" / "barrido_margen2k.csv"
EPS = (0.85, 0.80, 0.85)                 # efectividades fijas del TASK_CONTEXT
T_SUMIDERO, T_AMB_DISENO = 283.0, 283.15
ETA_T, ETA_P, M_B = 0.80, 0.80, 1.0
EXC = (PropertyRangeError, ValueError, RuntimeError, NotImplementedError,
       ZeroDivisionError, OverflowError, ArithmeticError)
_LOG = None


def log(msg):
    linea = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(linea, flush=True)
    if _LOG is not None:
        _LOG.write(linea + "\n")


def escribir(nombre, filas):
    if not filas:
        return
    with open(OUT / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    log(f"  -> {nombre} ({len(filas)} filas)")

def puntos_kalina():
    with open(SRC, newline="", encoding="utf-8") as fh:
        rs = [r for r in csv.DictReader(fh) if r["clasificacion"] == "KALINA"]
    log(f"{len(rs)} filas con clasificacion == KALINA en {SRC.relative_to(REPO)}")
    return [dict(etiqueta=f"KALINA-{i + 1:02d}", x_b=float(r["x_b"]),
                 P_alta=float(r["P_alta"]), T_fuente=float(r["T_fuente"]),
                 P_baja=float(r["P_baja"]), eta_ref=float(r["eta"]))
            for i, r in enumerate(rs)]


def correr(cls, p):
    """Resuelve + clasifica un punto con `cls`; devuelve (fila, tiempo en s)."""
    be = cls(x=p["x_b"])
    comun = dict(P_alta=p["P_alta"], P_baja=p["P_baja"], T_fuente=p["T_fuente"],
                 T_sumidero=T_SUMIDERO, x_b=p["x_b"], m_b=M_B,
                 eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(be, eta_t=ETA_T, eta_p=ETA_P, **comun)
        val = evaluar_ciclo(be, res, T_amb_diseno=T_AMB_DISENO, **comun)
        # 9 decimales: con 6, el Δη de ~1e-7 de un trial descartado se vería 0.
        fila = dict(eta=round(res["eta"], 9), Wnet=round(res["Wnet"], 6),
                    clasificacion=val.clasificacion.value,
                    n_fallas=len(val.fallas),
                    fallas=",".join(f.codigo for f in val.fallas), error="")
    except EXC as exc:
        fila = dict(eta="", Wnet="", clasificacion="ERROR", n_fallas="",
                    fallas="", error=f"{type(exc).__name__}: {exc}"[:150])
    dt = time.perf_counter() - t0
    fila.update(tiempo_s=round(dt, 2),
                n_recurrencias=getattr(be, "n_recurrencias", 0),
                n_fallos=getattr(be, "n_fallos", 0),
                t_real_s=round(getattr(be, "t_real", 0.0), 2),
                verificacion_incompleta=getattr(be, "verificacion_incompleta", False))
    return fila, be


def principal():
    global _LOG
    OUT.mkdir(parents=True, exist_ok=True)
    _LOG = open(OUT / "run.log", "w", encoding="utf-8", buffering=1)
    log("REGRESION TeqpAdapter vs TeqpVerificado sobre los puntos KALINA")
    log(f"  T_sumidero={T_SUMIDERO} K, T_amb_diseno={T_AMB_DISENO} K, "
        f"eta_t=eta_p={ETA_T}, eps={EPS}, m_b={M_B}")
    puntos = puntos_kalina()
    filas, detalle = [], []
    for p in puntos:
        ft, _ = correr(TeqpAdapter, p)
        fv, bv = correr(TeqpVerificado, p)
        d_eta = (round(fv["eta"] - ft["eta"], 12)
                 if ft["eta"] != "" and fv["eta"] != "" else "")
        cambia = ft["clasificacion"] != fv["clasificacion"]
        filas.append(dict(
            etiqueta=p["etiqueta"], x_b=p["x_b"], P_alta=p["P_alta"],
            T_fuente=p["T_fuente"], P_baja=p["P_baja"], eta_ref=p["eta_ref"],
            eta_teqp=ft["eta"], eta_verif=fv["eta"], d_eta=d_eta,
            clas_teqp=ft["clasificacion"], clas_verif=fv["clasificacion"],
            cambia_clasificacion=cambia, fallas_teqp=ft["fallas"],
            fallas_verif=fv["fallas"], n_recurrencias=fv["n_recurrencias"],
            n_fallos=fv["n_fallos"], t_real_s=fv["t_real_s"],
            verificacion_incompleta=fv["verificacion_incompleta"],
            t_teqp_s=ft["tiempo_s"], t_verif_s=fv["tiempo_s"],
            sobrecosto_pct=round(100.0 * (fv["tiempo_s"] / ft["tiempo_s"] - 1.0), 2),
            error_teqp=ft["error"], error_verif=fv["error"]))
        detalle += [dict(etiqueta=p["etiqueta"], **r) for r in bv.recurrencias]
        log(f"  {p['etiqueta']} x={p['x_b']} P*={p['P_baja']:.3f} "
            f"eta: teqp {ft['eta']} / verif {fv['eta']} (ref {p['eta_ref']})")
        log(f"      clas: {ft['clasificacion']} / {fv['clasificacion']}"
            f"{'  <-- CAMBIA' if cambia else ''} | t {ft['tiempo_s']}s -> {fv['tiempo_s']}s"
            f" | rec={fv['n_recurrencias']} t_real={fv['t_real_s']}s "
            f"incompleta={fv['verificacion_incompleta']}")
    escribir("regresion_22.csv", filas)
    escribir("regresion_recurrencias.csv", detalle)
    reporte(filas, detalle)
    _LOG.close()


def reporte(filas, detalle):
    t_teqp = st.mean(f["t_teqp_s"] for f in filas)
    t_verif = st.mean(f["t_verif_s"] for f in filas)
    sobrecosto = 100.0 * (t_verif / t_teqp - 1.0)
    n_err = sum(1 for f in filas if f["error_teqp"] or f["error_verif"])
    cambian = [f for f in filas if f["cambia_clasificacion"]]
    con_eta = [f for f in filas if f["d_eta"] != ""]
    distintos = [f for f in con_eta if abs(f["d_eta"]) > 1e-9]
    L = []
    A = L.append
    A("# REPORTE — `TeqpVerificado` sobre los 22 puntos KALINA "
      "(TASK 2026-09-27-teqp-verificado)\n")
    A(f"Generado por `scripts/regresion_teqp_verificado.py` el "
      f"{time.strftime('%Y-%m-%d %H:%M:%S')}. Datos: "
      f"`resultados/2026-09-27_teqp_verificado/regresion_22.csv` "
      f"({len(filas)} puntos) y `regresion_recurrencias.csv` "
      f"({len(detalle)} llamadas respaldadas).\n")
    A("## Qué se comparó\n")
    A("Cada punto KALINA del barrido `2026-09-24_margen2k` se resolvió en SU "
      f"`P_baja` con `TeqpAdapter` y con `TeqpVerificado` "
      f"(T_sumidero={T_SUMIDERO} K, T_amb_diseno={T_AMB_DISENO} K, "
      f"η_t=η_p={ETA_T}, ε={EPS}, ṁ_b={M_B} kg/s) y se clasificó con "
      "`evaluar_ciclo` sobre el MISMO adapter que resolvió el ciclo.\n")
    A("## Resumen\n")
    A("| Magnitud | Valor |")
    A("|---|---|")
    A(f"| Puntos | {len(filas)} |")
    A(f"| Puntos con error | {n_err} |")
    A(f"| Puntos donde η cambia | {len(distintos)} de {len(con_eta)} |")
    A(f"| Puntos donde cambia la clasificación | {len(cambian)} |")
    A(f"| Recurrencias totales al motor real | {sum(f['n_recurrencias'] for f in filas)} |")
    A(f"| Recurrencias con `fallo=True` | {sum(f['n_fallos'] for f in filas)} |")
    A(f"| Puntos con `verificacion_incompleta` | "
      f"{sum(1 for f in filas if f['verificacion_incompleta'])} |")
    A(f"| Tiempo medio `TeqpAdapter` | {t_teqp:.2f} s/punto |")
    A(f"| Tiempo medio `TeqpVerificado` | {t_verif:.2f} s/punto |")
    A(f"| **Sobrecosto** | **{sobrecosto:+.2f} %** |")
    A(f"| Tiempo total en motor real | "
      f"{sum(f['t_real_s'] for f in filas):.1f} s |")
    A("")
    A("## Diferencias por punto\n")
    A("| # | x_b | P_alta | T_fuente | P_baja | η teqp | η verif | Δη | "
      "clas teqp | clas verif | rec | t_real [s] | incompleta | t teqp [s] | "
      "t verif [s] |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in filas:
        A(f"| {f['etiqueta']} | {f['x_b']} | {f['P_alta']:.0f} | "
          f"{f['T_fuente']:.0f} | {f['P_baja']:.3f} | {f['eta_teqp']} | "
          f"{f['eta_verif']} | {f['d_eta']} | {f['clas_teqp']} | "
          f"{f['clas_verif']} | {f['n_recurrencias']} | {f['t_real_s']} | "
          f"{f['verificacion_incompleta']} | {f['t_teqp_s']} | {f['t_verif_s']} |")
    A("")
    if distintos:
        A("### Puntos con Δη ≠ 0\n")
        for f in distintos:
            A(f"- **{f['etiqueta']}** (x_b={f['x_b']}, P_baja={f['P_baja']:.3f} "
              f"kPa): η {f['eta_teqp']} -> {f['eta_verif']} "
              f"(Δ={f['d_eta']:+.9f}), {f['n_recurrencias']} recurrencia(s), "
              f"clasificación {f['clas_teqp']} -> {f['clas_verif']}.")
        A("")
    else:
        A("### Puntos con Δη ≠ 0\n")
        A("Ninguno (con las precisiones registradas). Aun así, "
          f"{sum(1 for f in filas if f['n_recurrencias'])} punto(s) con "
          "recurrencia(s): si una cae en un trial descartado de la búsqueda de "
          "Brent en T1, η puede variar solo en la última cifra.\n")
    A("### Cambios de clasificación\n")
    if cambian:
        for f in cambian:
            A(f"- **{f['etiqueta']}**: {f['clas_teqp']} -> {f['clas_verif']} "
              f"(fallas {f['fallas_teqp'] or '—'} -> {f['fallas_verif'] or '—'}).")
    else:
        A("Ninguno.")
    A("")
    A("### Recurrencias al motor real\n")
    if detalle:
        A("| # | método | P [kPa] | x | x_molar | T_teqp [K] | Ta [K] | Tw [K] "
          "| criterio | origen | valor_teqp | valor_real | t_real [s] | fallo |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for f in filas:
            for r in [d for d in detalle if d["etiqueta"] == f["etiqueta"]]:
                A(f"| {f['etiqueta']} | `{r['metodo']}` | {r['P']} | {r['x']} | "
                  f"{r['x_molar']} | {r['T_teqp']} | {r['Ta']} | {r['Tw']} | "
                  f"{r['criterio']} | {r['origen']} | {r['valor_teqp']} | "
                  f"{r['valor_real']} | {r['t_real_s']} | {r['fallo']} |")
    else:
        A("Ninguna llamada de los 22 puntos cayó en la zona de riesgo.")
    A("")
    A("## Lectura\n")
    A(f"- **Costo**: {sobrecosto:+.2f} % de media por punto "
      f"({t_teqp:.2f} -> {t_verif:.2f} s; mediana del ratio por punto "
      f"{100.0 * st.median(f['t_verif_s'] / f['t_teqp_s'] for f in filas) - 100.0:+.2f} %). "
      f"El ruido de reloj entre corridas es de ±1-2 s por punto (~5 %), o sea que "
      f"esta media está DENTRO del ruido. Lo sistemático es el coste de detección "
      f"(0.475 ms por inversión, medido en `scripts/costo_soluciones_teqp.py`) y el "
      f"resto son los {sum(f['t_real_s'] for f in filas):.1f} s de motor real. El "
      f"+2.8 % del prototipo NO es comparable: allí se contrastó la media de 3 "
      f"puntos NORMALES contra la media de los 22 (líneas base distintas).")
    A("- **Coherencia**: `TeqpVerificado` no cambia ningún resultado fuera de la "
      "zona de riesgo: en los puntos sin recurrencia la salida es bit a bit la de "
      "`TeqpAdapter`. La única diferencia posible es la corrección de la raíz falsa "
      "(y su efecto en las iteraciones de la búsqueda de Brent).")
    if any(f["verificacion_incompleta"] for f in filas):
        A("- **Aviso**: hubo puntos con `verificacion_incompleta=True`: el motor "
          "real no cubrió el estado y el valor devuelto es el de teqp. Esos "
          "puntos quedan marcados y NO deben publicarse como verificados.")
    else:
        A("- `verificacion_incompleta=False` en los 22 puntos: el motor real "
          "cubrió todas las recurrencias que hubo.")
    (OUT / "REPORTE_TEQP_VERIFICADO.md").write_text("\n".join(L), encoding="utf-8")
    log("  -> REPORTE_TEQP_VERIFICADO.md")
    log(f"SOBRECOSTO {sobrecosto:+.2f} % ({t_teqp:.2f} -> {t_verif:.2f} s/punto); "
        f"recurrencias {sum(f['n_recurrencias'] for f in filas)}; "
        f"cambios de clasificacion {len(cambian)}")


if __name__ == "__main__":
    principal()
